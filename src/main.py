from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import validate

from src.collectors.patchday import fetch_bulletin, patch_day_for_month
from src.parsers.patchday_parser import parse_bulletin


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "patchday.schema.json"
OUTPUT_DIR = ROOT / "doc" / "patchday"


def build_document(year: int, month: int) -> dict:
    url, html = fetch_bulletin(year, month)
    notes, summary = parse_bulletin(html)

    patch_day = patch_day_for_month(year, month)

    notes.sort(key=lambda x: (x["note_number"], x["status"]))

    document = {
        "schema_version": "1.0",
        "source": {
            "provider": "SAP",
            "type": "SAP Security Patch Day",
            "url": url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        },
        "patch_day": {
            "year": year,
            "month": month,
            "month_name": patch_day.strftime("%B"),
            "scheduled_date": patch_day.isoformat(),
        },
        "summary": {
            "announced_new_notes": summary["announced_new_notes"],
            "announced_updates": summary["announced_updates"],
            "parsed_records": len(notes),
            "parsed_new_notes": sum(n["status"] == "new" for n in notes),
            "parsed_updates": sum(n["status"] == "updated" for n in notes),
        },
        "security_notes": notes,
    }

    with SCHEMA.open(encoding="utf-8") as f:
        schema = json.load(f)
    validate(instance=document, schema=schema)

    return document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    args = parser.parse_args()

    now = datetime.now()
    year = args.year or now.year
    month = args.month or now.month

    document = build_document(year, month)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{year:04d}-{month:02d}.json"

    output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {output}")
    print(f"Parsed {document['summary']['parsed_records']} records")


if __name__ == "__main__":
    main()
