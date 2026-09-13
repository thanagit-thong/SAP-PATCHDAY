from __future__ import annotations

import re
from bs4 import BeautifulSoup


NOTE_RE = re.compile(r"(?<!\d)(\d{7})(?!\d)")
CVE_RE = re.compile(r"CVE-\d{4}-\d{4,}")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_note_text(text: str) -> dict:
    text = clean(text)

    note_match = NOTE_RE.search(text)
    note_number = note_match.group(1) if note_match else None

    cves = sorted(set(CVE_RE.findall(text)))

    priority = None
    for candidate in ("Critical", "High", "Medium", "Low"):
        if re.search(rf"\b{candidate}\b", text, re.I):
            priority = candidate
            break

    cvss = None
    # CVSS is normally the final numeric field in the SAP bulletin row.
    numbers = re.findall(r"(?<![\w.])(?:10(?:\.0)?|[0-9]\.[0-9])(?![\w.])", text)
    if numbers:
        try:
            cvss = float(numbers[-1])
        except ValueError:
            pass

    title = text
    if note_number:
        title = re.sub(rf"^\s*{note_number}\s*", "", title)
    if priority:
        title = re.sub(rf"\s*{priority}\s*$", "", title, flags=re.I)
    if cvss is not None:
        title = re.sub(rf"\s*{re.escape(str(cvss))}\s*$", "", title)

    versions = []
    version_match = re.search(r"Version(?:\(s\)|s)?\s*[:\-]\s*(.+?)(?=\s+(?:Critical|High|Medium|Low)\b|$)", text, re.I)
    if version_match:
        raw_versions = version_match.group(1)
        versions = [
            clean(x.strip(" -,:;"))
            for x in re.split(r",\s*|\s{2,}", raw_versions)
            if clean(x.strip(" -,:;"))
        ]

    return {
        "note_number": note_number,
        "cve": cves,
        "title": title,
        "priority": priority,
        "cvss": cvss,
        "affected_versions_raw": versions,
        "status": "updated" if re.search(r"\bUpdate to Security Note\b", text, re.I) else "new",
        "source_text": text,
    }


def _row_text(row) -> str:
    return clean(" ".join(row.stripped_strings))


def parse_bulletin(html: str) -> tuple[list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")

    notes = []
    seen = set()

    # SAP has used table-based bulletins. Parse rows first, then fall back
    # to text blocks if the markup changes.
    for row in soup.find_all("tr"):
        text = _row_text(row)
        if not NOTE_RE.search(text):
            continue
        parsed = parse_note_text(text)
        if not parsed["note_number"]:
            continue
        key = (parsed["note_number"], parsed["status"])
        if key not in seen:
            notes.append(parsed)
            seen.add(key)

    if not notes:
        for element in soup.find_all(["p", "li", "div"]):
            text = _row_text(element)
            if not NOTE_RE.search(text):
                continue
            parsed = parse_note_text(text)
            if parsed["note_number"]:
                key = (parsed["note_number"], parsed["status"])
                if key not in seen:
                    notes.append(parsed)
                    seen.add(key)

    page_text = clean(soup.get_text(" ", strip=True))

    new_match = re.search(r"release of\s+(\d+)\s+new security notes", page_text, re.I)
    update_match = re.search(r"(?:There (?:is|are)|and)\s+(\d+)\s+updates? to previously released", page_text, re.I)

    summary = {
        "announced_new_notes": int(new_match.group(1)) if new_match else None,
        "announced_updates": int(update_match.group(1)) if update_match else None,
    }

    return notes, summary
