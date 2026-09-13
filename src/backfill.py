from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
import time

from src.main import build_document, OUTPUT_DIR


def month_range(start: str, end: str):
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))

    current = date(sy, sm, 1)
    finish = date(ey, em, 1)

    while current <= finish:
        yield current.year, current.month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Backfill SAP Security Patch Day JSON files."
    )
    parser.add_argument("--from", dest="start", required=True, help="YYYY-MM")
    parser.add_argument("--to", dest="end", required=True, help="YYYY-MM")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing monthly JSON files.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between SAP requests in seconds.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    completed = []
    skipped = []
    failed = []

    for year, month in month_range(args.start, args.end):
        output = OUTPUT_DIR / f"{year:04d}-{month:02d}.json"

        if output.exists() and not args.overwrite:
            print(f"{year:04d}-{month:02d}  SKIP  already exists")
            skipped.append(str(output))
            continue

        try:
            document = build_document(year, month)
            output.write_text(
                json.dumps(document, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            s = document["summary"]
            print(
                f"{year:04d}-{month:02d}  OK    "
                f"{s['parsed_new_notes']} new / "
                f"{s['parsed_updates']} updates"
            )
            completed.append(str(output))

        except Exception as exc:
            print(f"{year:04d}-{month:02d}  FAIL  {exc}")
            failed.append({"month": f"{year:04d}-{month:02d}", "error": str(exc)})

        time.sleep(args.delay)

    print("\nBACKFILL SUMMARY")
    print(f"Completed: {len(completed)}")
    print(f"Skipped:   {len(skipped)}")
    print(f"Failed:    {len(failed)}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
