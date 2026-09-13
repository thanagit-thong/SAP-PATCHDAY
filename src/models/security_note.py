from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SecurityNote:
    note_number: str
    title: str
    priority: str | None
    cvss: float | None
    cve: list[str] = field(default_factory=list)
    affected_versions_raw: list[str] = field(default_factory=list)
    status: str = "new"
    source_text: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
