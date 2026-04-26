#!/usr/bin/env python3
"""Validate the structure and consistency of generated export files."""

import csv
import json
import sys
from pathlib import Path

FORMATS = ["movies.json", "movies.min.json", "movies.csv", "movies.ndjson"]
SECTIONS = ["full", "ids"]

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"  FAIL: {msg}")


def check(label: str, fn):
    print(f"  {label} ...", end=" ")
    try:
        fn()
        print("ok")
    except AssertionError as e:
        fail(str(e))


def validate_section(section_dir: Path) -> int:
    """Validate one section (full/ or ids/). Returns the expected row count."""
    label = section_dir.name

    print(f"\n[{label}]")

    # All top-level format files exist
    for filename in FORMATS:
        check(f"{filename} exists", lambda f=filename: assert_exists(section_dir / f))

    # Load canonical list from movies.json
    json_path = section_dir / "movies.json"
    if not json_path.exists():
        fail("movies.json missing — cannot continue section validation")
        return 0

    with json_path.open(encoding="utf-8") as f:
        records = json.load(f)

    check(
        "movies.json is a non-empty array",
        lambda: assert_(
            isinstance(records, list) and len(records) > 0,
            "expected non-empty JSON array",
        ),
    )

    row_count = len(records)

    # min.json is a single line
    check(
        "movies.min.json is single line",
        lambda: assert_(
            (section_dir / "movies.min.json").read_text(encoding="utf-8").count("\n")
            == 0,
            "movies.min.json has multiple lines",
        ),
    )

    # min.json parses to same count
    check(
        "movies.min.json matches row count",
        lambda: assert_(
            len(
                json.loads(
                    (section_dir / "movies.min.json").read_text(encoding="utf-8")
                )
            )
            == row_count,
            "min.json row count mismatch",
        ),
    )

    # ndjson: one valid JSON object per line, no trailing newline, correct count
    def check_ndjson():
        text = (section_dir / "movies.ndjson").read_text(encoding="utf-8")
        assert not text.endswith("\n"), "ndjson has trailing newline"
        lines = text.split("\n")
        assert (
            len(lines) == row_count
        ), f"ndjson has {len(lines)} lines, expected {row_count}"
        for line in lines:
            json.loads(line)  # raises on invalid JSON

    check("movies.ndjson line count and validity", check_ndjson)

    # CSV row count matches
    def check_csv():
        with (section_dir / "movies.csv").open(newline="", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))
        assert (
            len(csv_rows) == row_count
        ), f"CSV has {len(csv_rows)} rows, expected {row_count}"

    check("movies.csv row count", check_csv)

    # by_id validation
    by_id_dir = section_dir / "by_id"
    if not by_id_dir.exists():
        fail("by_id/ directory missing")
        return row_count

    by_id_files = sorted(by_id_dir.glob("movies.*.json"))
    # Only check the non-minified files
    canonical_by_id = [f for f in by_id_files if not f.name.endswith(".min.json")]

    for by_id_path in canonical_by_id:
        field = by_id_path.stem.split(".", 1)[1]  # e.g. "movies.imdb_id" -> "imdb_id"

        def check_by_id(path=by_id_path, f=field):
            mapping = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(mapping, dict), "expected a JSON object"
            for key, record in mapping.items():
                assert key, f"empty key in {path.name}"
                assert (
                    record.get(f) == key
                ), f"key {key!r} doesn't match field value {record.get(f)!r}"
            # id field must contain all rows
            if f == "id":
                assert (
                    len(mapping) == row_count
                ), f"movies.id.json has {len(mapping)} entries, expected {row_count}"

        check(f"by_id/{by_id_path.name}", check_by_id)

        min_path = by_id_dir / (by_id_path.stem + ".min.json")
        check(f"by_id/{min_path.name} exists", lambda p=min_path: assert_exists(p))

    return row_count


def assert_exists(path: Path) -> None:
    assert path.exists(), f"{path} does not exist"


def assert_(condition: bool, msg: str) -> None:
    assert condition, msg


def main() -> None:
    parser_desc = "Validate crosswalk export files"
    import argparse

    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument(
        "exports_dir",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parent.parent / "exports" / "movies",
        help="Path to exports/movies/ (default: auto-detected)",
    )
    args = parser.parse_args()

    exports_dir = args.exports_dir.resolve()
    print(f"Validating exports at: {exports_dir}")

    if not exports_dir.exists():
        sys.exit(f"Exports directory not found: {exports_dir}")

    section_counts = {}
    for section in SECTIONS:
        section_dir = exports_dir / section
        if not section_dir.exists():
            fail(f"{section}/ directory missing")
            continue
        section_counts[section] = validate_section(section_dir)

    # Row counts must match across sections
    if len(section_counts) == len(SECTIONS):
        print("\n[cross-section]")
        check(
            "full and ids row counts match",
            lambda: assert_(
                len(set(section_counts.values())) == 1,
                f"row count mismatch: {section_counts}",
            ),
        )

    print()
    if errors:
        print(f"{len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
