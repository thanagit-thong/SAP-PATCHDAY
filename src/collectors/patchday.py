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
    """
    Build the monthly SAP Security Patch Day URL.

    Example:
        2026-09
        -> https://support.sap.com/en/my-support/knowledge-base/
           security-notes-news/september-2026.html
    """
    slug = f"{month_name[month].lower()}-{year}"
    return f"{BASE_URL}/{slug}.html"


def yearly_archive_url(year: int) -> str:
    """
    Build the SAP yearly Security Patch Day archive URL.

    Example:
        2025
        -> https://support.sap.com/en/my-support/knowledge-base/
           security-notes-news/bulletin-2025.html
    """
    return f"{BASE_URL}/bulletin-{year}.html"


def bulletin_url(year: int, month: int) -> str:
    """
    Backward-compatible helper.

    For Current year : return the monthly bulletin URL.
    For Previous year: return the yearly archive URL.
    """
    current_year = date.today().year

    if year == current_year:
        return monthly_bulletin_url(year, month)

    return yearly_archive_url(year)


def fetch_url(url: str) -> str:
    """
    Download an SAP bulletin page.
    """
    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": USER_AGENT
        },
    )

    response.raise_for_status()

    return response.text


def extract_month_section(
    html: str,
    year: int,
    month: int,
) -> str:
    """
    Extract only the requested month's section from SAP's
    yearly archive page.

    Historical SAP bulletin pages contain all months of a year
    on a single page.

    Example:

        bulletin-2025.html

        January 2025
        ----------------
        notes...

        February 2025
        ----------------
        notes...

    When requesting January 2025, only the January section
    is returned.
    """

    soup = BeautifulSoup(html, "html.parser")

    target_month = month_name[month]

    # SAP has used both hyphen and en-dash in headings.
    heading_pattern = re.compile(
        rf"SAP\s+Security\s+Patch\s+Day\s*[-–—]\s*"
        rf"{re.escape(target_month)}\s+{year}",
        re.IGNORECASE,
    )

    target_heading = None

    # Do not rely on BeautifulSoup's `string=` matching.
    # SAP page markup may contain nested elements inside headings.
    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4"]
    ):
        heading_text = " ".join(
            heading.stripped_strings
        )

        if heading_pattern.search(heading_text):
            target_heading = heading
            break

    if target_heading is None:
        raise ValueError(
            f"Could not find SAP Security Patch Day section "
            f"for {target_month} {year} "
            f"in the yearly archive page."
        )

    parts = [str(target_heading)]

    # Collect everything after the target heading until
    # the next SAP Security Patch Day heading.
    for element in target_heading.find_all_next():

        if element.name in {
            "h1",
            "h2",
            "h3",
            "h4",
        }:
            heading_text = " ".join(
                element.stripped_strings
            )

            if re.search(
                r"SAP\s+Security\s+Patch\s+Day\s*[-–—]",
                heading_text,
                re.IGNORECASE,
            ):
                break

        parts.append(str(element))

    result = "\n".join(parts)

    if not result.strip():
        raise ValueError(
            f"Extracted empty section for "
            f"{target_month} {year}."
        )

    return result


def fetch_bulletin(
    year: int,
    month: int,
) -> tuple[str, str]:
    """
    Fetch the correct SAP Security Patch Day bulletin.

    SAP publishing model:

    Current year: One page per month.
    Example: september-2026.html

    Previous year: One archive page per year.
    Example: bulletin-2025.html

    The requested month is extracted from that page.
    """

    # ---------------------------------------------------------
    # 2026 and newer
    # ---------------------------------------------------------
    if year == date.today().year:

        url = monthly_bulletin_url(
            year,
            month,
        )

        html = fetch_url(url)

        return url, html

    # ---------------------------------------------------------
    # 2025 and older
    # ---------------------------------------------------------
    url = yearly_archive_url(year)

    html = fetch_url(url)

    month_html = extract_month_section(
        html,
        year,
        month,
    )

    return url, month_html


def patch_day_for_month(
    year: int,
    month: int,
) -> date:
    """
    Return the second Tuesday of the requested month.
    """

    d = date(
        year,
        month,
        1,
    )

    days_until_tuesday = (
        1 - d.weekday()
    ) % 7

    first_tuesday = d.replace(
        day=1 + days_until_tuesday
    )

    second_tuesday = first_tuesday.replace(
        day=first_tuesday.day + 7
    )

    return second_tuesday
