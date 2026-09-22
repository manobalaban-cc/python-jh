"""Aggregation: a stream of lines in, summary objects out."""

import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime

from loganalyse.models import LogEntry, PathStats
from loganalyse.parsing import parse_line


@dataclass(slots=True)
class EndpointReport:
    endpoint: str
    requests: int
    mean_duration: float
    p95_duration: float
    errors: int


@dataclass(slots=True)
class ErrorReport:
    status: int
    endpoint: str
    count: int
    first_seen: datetime
    last_seen: datetime


@dataclass(slots=True)
class Summary:
    """Everything the report needs, in constant memory per request."""

    total_lines: int = 0
    unparsable: int = 0
    requests: int = 0
    bytes_sent: int = 0
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    clients: set[str] = field(default_factory=set)
    status_classes: Counter[str] = field(default_factory=Counter)
    endpoints: dict[str, PathStats] = field(default_factory=lambda: defaultdict(PathStats))
    errors: dict[tuple[int, str], ErrorReport] = field(default_factory=dict)
    durations: list[float] = field(default_factory=list)

    @property
    def unparsable_share(self) -> float:
        return self.unparsable / self.total_lines if self.total_lines else 0.0


def aggregate(
    lines: Iterable[str],
    *,
    since: datetime | None = None,
    until: datetime | None = None,
) -> Summary:
    """Consume the log line by line and build the summary.

    Nothing per request is retained except the aggregates, the set of client
    addresses and the durations, so memory is bounded by the number of distinct
    clients and endpoints rather than by the number of requests.
    """
    summary = Summary()

    for line in lines:
        if not line.strip():
            continue

        summary.total_lines += 1
        entry = parse_line(line)
        if entry is None:
            summary.unparsable += 1
            continue

        if not _in_window(entry, since, until):
            continue

        _accumulate(summary, entry)

    return summary


def _in_window(entry: LogEntry, since: datetime | None, until: datetime | None) -> bool:
    # The log carries an offset; the filters usually do not. Compare naively in
    # that case rather than raising on every single line.
    stamp = (
        entry.timestamp if since is None or since.tzinfo else entry.timestamp.replace(tzinfo=None)
    )
    if since is not None and stamp < since:
        return False
    stamp = (
        entry.timestamp if until is None or until.tzinfo else entry.timestamp.replace(tzinfo=None)
    )
    return not (until is not None and stamp >= until)


def _accumulate(summary: Summary, entry: LogEntry) -> None:
    summary.requests += 1
    summary.bytes_sent += entry.size
    summary.clients.add(entry.ip)
    summary.status_classes[entry.status_class] += 1

    if summary.first_seen is None or entry.timestamp < summary.first_seen:
        summary.first_seen = entry.timestamp
    if summary.last_seen is None or entry.timestamp > summary.last_seen:
        summary.last_seen = entry.timestamp

    stats = summary.endpoints[entry.endpoint]
    stats.requests += 1
    stats.bytes_sent += entry.size
    if entry.is_error:
        stats.errors += 1
    if entry.duration is not None:
        stats.durations.append(entry.duration)
        summary.durations.append(entry.duration)

    if entry.is_error:
        key = (entry.status, entry.endpoint)
        report = summary.errors.get(key)
        if report is None:
            summary.errors[key] = ErrorReport(
                status=entry.status,
                endpoint=entry.endpoint,
                count=1,
                first_seen=entry.timestamp,
                last_seen=entry.timestamp,
            )
        else:
            report.count += 1
            report.first_seen = min(report.first_seen, entry.timestamp)
            report.last_seen = max(report.last_seen, entry.timestamp)


def percentile(values: list[float], fraction: float) -> float:
    """Simple nearest-rank percentile; enough for a report, and dependency-free."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(fraction * len(ordered)), len(ordered) - 1)
    return ordered[index]


def duration_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "p95": 0.0, "p99": 0.0}
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
    }


def top_paths(summary: Summary, limit: int = 5) -> list[tuple[str, int]]:
    counts = [(endpoint, stats.requests) for endpoint, stats in summary.endpoints.items()]
    counts.sort(key=lambda item: (-item[1], item[0]))
    return counts[:limit]


def slowest_endpoints(
    summary: Summary, limit: int = 10, min_requests: int = 10
) -> list[EndpointReport]:
    """Endpoints ranked by mean duration, ignoring rarely used ones."""
    reports = [
        EndpointReport(
            endpoint=endpoint,
            requests=stats.requests,
            mean_duration=statistics.fmean(stats.durations),
            p95_duration=percentile(stats.durations, 0.95),
            errors=stats.errors,
        )
        for endpoint, stats in summary.endpoints.items()
        if stats.requests >= min_requests and stats.durations
    ]
    reports.sort(key=lambda report: report.mean_duration, reverse=True)
    return reports[:limit]


def error_reports(summary: Summary, status_class: str | None = None) -> list[ErrorReport]:
    reports = list(summary.errors.values())
    if status_class:
        wanted = int(status_class[0])
        reports = [report for report in reports if report.status // 100 == wanted]
    reports.sort(key=lambda report: (-report.count, report.status, report.endpoint))
    return reports


def iter_entries(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Convenience generator for callers that want the entries themselves."""
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry
