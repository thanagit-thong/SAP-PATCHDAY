from __future__ import annotations

from datetime import date
from calendar import month_name
import re

import requests


BASE_URL = (
    "https://support.sap.com/en/my-support/knowledge-base/"
    "security-notes-news"
)


def bulletin_url(year: int, month: int) -> str:
    slug = f"{month_name[month].lower()}-{year}"
    return f"{BASE_URL}/{slug}.html"


def fetch_bulletin(year: int, month: int) -> tuple[str, str]:
    url = bulletin_url(year, month)
    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "SAP-PATCHDAY/1.0 (+automated security research)"
        },
    )
    response.raise_for_status()
    return url, response.text


def patch_day_for_month(year: int, month: int) -> date:
    """Return the second Tuesday of the requested month."""
    d = date(year, month, 1)
    days_until_tuesday = (1 - d.weekday()) % 7
    first_tuesday = d.replace(day=1 + days_until_tuesday)
    return first_tuesday.replace(day=first_tuesday.day + 7)
