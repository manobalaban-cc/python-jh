"""Turning raw log lines into LogEntry objects."""

import gzip
import logging
import re
from collections.abc import Iterable, Iterator
from datetime import datetime
from pathlib import Path
from typing import IO

from loganalyse.models import LogEntry

logger = logging.getLogger(__name__)

# One compiled regex, used for every line. re.VERBOSE lets us comment it.
LINE_PATTERN = re.compile(
    r"""
    ^(?P<ip>\S+)\s+                       # client address
    (?P<ident>\S+)\s+(?P<user>\S+)\s+     # identd and auth user, almost always "-"
    \[(?P<timestamp>[^\]]+)\]\s+          # [27/Apr/2024:13:59:08 +0200]
    "(?P<method>[A-Z]+)\s+                # "GET
    (?P<path>\S+)\s+                      #  /api/x?page=2
    (?P<protocol>HTTP/[\d.]+)"\s+         #  HTTP/1.1"
    (?P<status>\d{3})\s+                  # 200
    (?P<size>\d+|-)                       # 4523 (or "-" for no body)
    (?:\s+"(?P<referrer>[^"]*)")?         # optional referrer
    (?:\s+"(?P<user_agent>[^"]*)")?       # optional user agent
    (?:\s+(?P<duration>[\d.]+))?          # optional nginx $request_time
    \s*$
    """,
    re.VERBOSE,
)

# Months are matched explicitly: strptime's %b depends on the locale, so on a
# machine with a non-English locale the naive version fails on every line.
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

TIMESTAMP_PATTERN = re.compile(
    r"^(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})\s*([+-]\d{4})?$"
)

NUMERIC_SEGMENT = re.compile(r"^\d+$")
UUID_SEGMENT = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-", re.ASCII)


def parse_timestamp(raw: str) -> datetime:
    """Parse `27/Apr/2024:13:59:08 +0200` without depending on the locale."""
    match = TIMESTAMP_PATTERN.match(raw.strip())
    if match is None:
        raise ValueError(f"bad timestamp: {raw!r}")

    day, month_name, year, hour, minute, second, offset = match.groups()
    if month_name not in MONTHS:
        raise ValueError(f"bad month: {month_name!r}")

    stamp = f"{year}-{MONTHS[month_name]:02d}-{day}T{hour}:{minute}:{second}"
    if offset:
        stamp += f"{offset[:3]}:{offset[3:]}"
    return datetime.fromisoformat(stamp)


def normalise_path(path: str) -> str:
    """Collapse a request path into an endpoint.

    /api/transactions?page=2      -> /api/transactions
    /api/users/1234/orders        -> /api/users/{id}/orders
    /api/items/3fa85f64-5717-...  -> /api/items/{id}
    """
    path = path.split("?", 1)[0].split("#", 1)[0]
    if len(path) > 1:
        path = path.rstrip("/")

    segments = [
        "{id}" if NUMERIC_SEGMENT.match(s) or UUID_SEGMENT.match(s) else s for s in path.split("/")
    ]
    return "/".join(segments) or "/"


def parse_line(line: str) -> LogEntry | None:
    """Parse one line, or return None if it is not a valid request line."""
    match = LINE_PATTERN.match(line.strip())
    if match is None:
        return None

    fields = match.groupdict()
    try:
        timestamp = parse_timestamp(fields["timestamp"])
    except ValueError:
        return None

    raw_size = fields["size"]
    raw_referrer = fields.get("referrer")
    raw_duration = fields.get("duration")

    path = fields["path"]
    return LogEntry(
        ip=fields["ip"],
        timestamp=timestamp,
        method=fields["method"],
        path=path,
        endpoint=normalise_path(path),
        status=int(fields["status"]),
        size=0 if raw_size == "-" else int(raw_size),
        referrer=None if raw_referrer in (None, "", "-") else raw_referrer,
        user_agent=fields.get("user_agent") or "",
        duration=float(raw_duration) if raw_duration else None,
    )


def open_log(path: Path | str) -> IO[str]:
    """Open a log file, transparently handling gzip and stdin ("-")."""
    if str(path) == "-":
        import sys

        return sys.stdin

    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, encoding="utf-8", errors="replace")


def parse_lines(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Stream entries from raw lines, logging (and dropping) unparsable ones.

    A generator, so the caller never holds more than one line plus one entry in
    memory - which is what keeps a 2 GB file workable.
    """
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        entry = parse_line(line)
        if entry is None:
            logger.debug("line %d is unparsable: %.120s", line_number, line.rstrip())
            continue

        yield entry
