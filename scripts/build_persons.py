#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

INTEGER_FIELDS = {"birth_year", "birth_month", "birth_day"}


def load_schema(schema_path: Path) -> tuple[list[str], list[str]]:
    """Return (full_fields, id_fields) from a single-file persons schema."""
    if not schema_path.exists():
        sys.exit(f"Schema not found: {schema_path}")

    try:
        with schema_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        core_fields = list(data["fields"].keys())
        sources = data.get("sources", [])
        active_id_fields = [s["id_field"] for s in sources if s.get("active", True)]
    except (yaml.YAMLError, KeyError, TypeError) as e:
        sys.exit(f"Failed to parse schema: {e}")

    full_fields = core_fields + active_id_fields
    id_fields = ["id"] + active_id_fields
    return full_fields, id_fields


def read_csv(csv_path: Path) -> list[dict]:
    """Read persons CSV, cast integer fields, omit empty optional fields."""
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        for field in INTEGER_FIELDS:
            if row.get(field):
                row[field] = int(row[field])
        result.append({k: v for k, v in row.items() if v != ""})
    return result


def write_outputs(
    records: list[dict],
    out_dir: Path,
    id_fields: list[str],
    stem: str,
    csv_fieldnames: list[str],
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

    # Use full field list for CSV so columns are consistent even when optional
    # fields are absent from some rows.
    with (out_dir / f"{stem}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=csv_fieldnames, extrasaction="ignore", restval=""
        )
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
        description="Build crosswalk export artifacts for persons"
    )
    parser.add_argument("csv", type=Path, help="Path to persons.csv")
    parser.add_argument(
        "--schema", required=True, type=Path, help="Path to persons.yaml"
    )
    args = parser.parse_args()

    csv_path = args.csv.resolve()
    stem = csv_path.stem  # "persons"
    repo_root = Path(__file__).resolve().parent.parent

    full_fields, id_fields = load_schema(args.schema.resolve())
    rows = read_csv(csv_path)
    if not rows:
        sys.exit(f"CSV is empty: {csv_path}")

    print(f"Read {len(rows)} rows")
    print(f"  full fields: {full_fields}")
    print(f"  id fields:   {id_fields}")

    full_records = [{k: row[k] for k in full_fields if k in row} for row in rows]
    ids_records = [{k: row[k] for k in id_fields if k in row} for row in rows]

    exports = repo_root / "exports" / stem
    write_outputs(full_records, exports / "full", id_fields, stem, full_fields)
    write_outputs(ids_records, exports / "ids", id_fields, stem, id_fields)

    print(f"Wrote exports to {exports}")


if __name__ == "__main__":
    main()
