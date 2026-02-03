from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ParserResult:
    url: str
    base_url: str
    pages_parsed: int
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        if not self.started_at or not self.finished_at:
            return None
        return (self.finished_at - self.started_at).total_seconds()
