"""Domain model for the log analyser."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LogEntry:
    """One successfully parsed request line.

    Frozen and slotted: a 2 GB log produces millions of these, one at a time, and
    __slots__ keeps each one small. Nothing here holds the raw line - that would
    double the memory for no benefit.
    """

    ip: str
    timestamp: datetime
    method: str
    path: str
    endpoint: str
    status: int
    size: int
    referrer: str | None
    user_agent: str
    duration: float | None

    @property
    def status_class(self) -> str:
        """`200` -> `2xx`, `503` -> `5xx`."""
        return f"{self.status // 100}xx"

    @property
    def is_error(self) -> bool:
        return self.status >= 400


@dataclass(slots=True)
class PathStats:
    """Running statistics for one endpoint.

    Counts and sums are O(1) in memory. Durations are kept per endpoint so the
    percentiles are exact; the number of endpoints is bounded by normalisation,
    which is the whole reason we normalise. See README for the trade-off.
    """

    requests: int = 0
    bytes_sent: int = 0
    errors: int = 0
    durations: list[float] = field(default_factory=list)
