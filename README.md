# SAP-PATCHDAY

Automated SAP Security Patch Day collector.
JSON file is available at doc/patchday

- Please note that this project is under development.If you only need the monthly Security Note JSON files (Phase 1), you can readily consume and integrate them into your application.
- Feel free to fork and use this repository at your own risk.
- Please be aware that the code was created using a combination of AI-generated tools and minor manual adjustments.


## Project plan
Phase 1  ✅  Public SAP Patch Day ingestion
Phase 2  🔜  SAP Note deep collector
Phase 3  🔜  System exposure matching
Phase 4  🔜  SAP Security Intelligence / RAG


## Phase 1

This repository:
1. Checks the SAP Security Patch Day bulletin.
2. Determines the current Patch Day month.
3. Downloads the public SAP bulletin.
4. Parses Security Notes and updates.
5. Validates the generated JSON.
6. Writes `doc/patchday/YYYY-MM.json`.
7. Can be run locally or by GitHub Actions.

Phase 2 will add authenticated SAP for Me / deep SAP Note collection.
Phase 3 will add SAP system exposure matching.
Phase 4 will provide SAP Security intelligence for RAG/LLM.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main --year 2026 --month 9
```

The parser is deliberately tolerant of changes to the SAP bulletin HTML and keeps the raw source URL in the output.

## Output

```text
doc/patchday/2026-09.json
```

## Important

Do not put SAP S-ID passwords or other credentials in this repository. Authentication is intentionally out of scope for Phase 1.

## Historical backfill

The repository supports rebuilding monthly Patch Day JSON files for a date range.

Example:

```bash
python -m src.backfill --from 2025-01 --to 2026-09
```

By default, existing JSON files are preserved. To intentionally rebuild them:

```bash
python -m src.backfill --from 2025-01 --to 2026-09 --overwrite
```

GitHub Actions also provides a manual **SAP Security Patch Day Backfill** workflow.
The default range is January 2025 through the current September 2026 Patch Day.

The collector fetches each month's public SAP bulletin directly. It does not invent
or synthesize historical records. A failed month causes the backfill job to fail so
missing historical data is visible rather than silently committed.
