#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path

import yaml


def load_schema(
    core_schema_path: Path, source_schema_path: Path
) -> tuple[list[str], list[str]]:
    """Return (full_fields, id_fields) derived from crosswalk-data schema files."""
    for p in (core_schema_path, source_schema_path):
        if not p.exists():
            sys.exit(f"Schema not found: {p}")

    try:
        with core_schema_path.open(encoding="utf-8") as f:
            core_fields = list(yaml.safe_load(f)["fields"].keys())

        with source_schema_path.open(encoding="utf-8") as f:
            sources = yaml.safe_load(f)["fields"]
        active_id_fields = [s["id_field"] for s in sources if s.get("active", True)]
    except (yaml.YAMLError, KeyError, TypeError) as e:
        sys.exit(f"Failed to parse schema: {e}")

    full_fields = core_fields + active_id_fields
    id_fields = ["id"] + active_id_fields
    return full_fields, id_fields


def read_csv(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["year"] = int(row["year"])
    return rows


def write_outputs(
    records: list[dict], out_dir: Path, id_fields: list[str], stem: str
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    by_id_dir = out_dir / "by_id"
    by_id_dir.mkdir(exist_ok=True)

    (out_dir / f"{stem}.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / f"{stem}.min.json").write_text(
        json.dumps(records, separators=(",", ":"), ensure_ascii=False), encoding="utf-8"
    )

    fieldnames = list(records[0].keys()) if records else []
    with (out_dir / f"{stem}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    ndjson_lines = "\n".join(
        json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in records
    )
    (out_dir / f"{stem}.ndjson").write_text(ndjson_lines, encoding="utf-8")

    for field in id_fields:
        keyed = {r[field]: r for r in records if r.get(field)}
        (by_id_dir / f"{stem}.{field}.json").write_text(
            json.dumps(keyed, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (by_id_dir / f"{stem}.{field}.min.json").write_text(
            json.dumps(keyed, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build crosswalk export artifacts for works"
    )
    parser.add_argument("csv", type=Path, help="Path to works CSV (e.g. movies.csv)")
    parser.add_argument(
        "--core-schema", required=True, type=Path, help="Path to works.yaml"
    )
    parser.add_argument(
        "--source-schema", required=True, type=Path, help="Path to works/movies.yaml"
    )
    args = parser.parse_args()

    csv_path = args.csv.resolve()
    stem = csv_path.stem  # e.g. "movies" from movies.csv
    repo_root = Path(__file__).resolve().parent.parent

    full_fields, id_fields = load_schema(
        args.core_schema.resolve(), args.source_schema.resolve()
    )
    rows = read_csv(csv_path)
    if not rows:
        sys.exit(f"CSV is empty: {csv_path}")

    csv_fields = set(rows[0].keys())
    missing = [f for f in full_fields if f not in csv_fields]
    if missing:
        sys.exit(f"Schema fields missing from CSV: {missing}")

    print(f"Read {len(rows)} rows")
    print(f"  full fields: {full_fields}")
    print(f"  id fields:   {id_fields}")

    full_records = [{k: row[k] for k in full_fields} for row in rows]
    ids_records = [{k: row[k] for k in id_fields} for row in rows]

    exports = repo_root / "exports" / stem
    write_outputs(full_records, exports / "full", id_fields, stem)
    write_outputs(ids_records, exports / "ids", id_fields, stem)

    print(f"Wrote exports to {exports}")


if __name__ == "__main__":
    main()
