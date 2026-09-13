from __future__ import annotations

from calendar import month_name
from datetime import date
import re

import requests
from bs4 import BeautifulSoup


BASE_URL = (
    "https://support.sap.com/en/my-support/knowledge-base/"
    "security-notes-news"
)

USER_AGENT = "SAP-PATCHDAY/1.1 (+automated security research)"


def monthly_bulletin_url(year: int, month: int) -> str:
    slug = f"{month_name[month].lower()}-{year}"
    return f"{BASE_URL}/{slug}.html"


def yearly_archive_url(year: int) -> str:
    return f"{BASE_URL}/bulletin-{year}.html"


def fetch_url(url: str) -> str:
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def extract_month_section(html: str, year: int, month: int) -> str:
    """
    Extract only the requested month's section from SAP's yearly archive page.
    SAP historical bulletin pages contain all months of a year on one page.
    """

    soup = BeautifulSoup(html, "html.parser")
    target_month = month_name[month]

    # SAP headings may use either "-" or "–".
    heading_pattern = re.compile(
        rf"SAP\s+Security\s+Patch\s+Day\s*[-–—]\s*"
        rf"{re.escape(target_month)}\s+{year}",
        re.IGNORECASE,
    )

    headings = soup.find_all(
        ["h1", "h2", "h3", "h4"],
        string=lambda text: bool(
            text and heading_pattern.search(" ".join(text.split()))
        ),
    )

    if not headings:
        raise ValueError(
            f"Could not find {target_month} {year} section "
            f"in SAP yearly archive."
        )

    target = headings[0]

    parts = [str(target)]

    # Collect everything until the next SAP Patch Day heading.
    for element in target.find_all_next():
        if element.name in {"h1", "h2", "h3", "h4"}:
            heading_text = " ".join(element.stripped_strings)

            if re.search(
                r"SAP\s+Security\s+Patch\s+Day\s*[-–—]",
                heading_text,
                re.IGNORECASE,
            ):
                break

        parts.append(str(element))

    return "\n".join(parts)


def fetch_bulletin(year: int, month: int) -> tuple[str, str]:
    """
    Fetch the correct SAP bulletin format.

    2026+:
        SAP publishes one bulletin page per month.

    <= 2025:
        SAP publishes one yearly archive page containing all months.
        We extract only the requested month's section.
    """

    if year >= 2026:
        url = monthly_bulletin_url(year, month)
        html = fetch_url(url)
        return url, html

    url = yearly_archive_url(year)
    html = fetch_url(url)

    month_html = extract_month_section(
        html,
        year,
        month,
    )

    return url, month_html


def patch_day_for_month(year: int, month: int) -> date:
    """Return the second Tuesday of the requested month."""

    d = date(year, month, 1)

    days_until_tuesday = (1 - d.weekday()) % 7
    first_tuesday = d.replace(
        day=1 + days_until_tuesday
    )

    return first_tuesday.replace(
        day=first_tuesday.day + 7
    )
