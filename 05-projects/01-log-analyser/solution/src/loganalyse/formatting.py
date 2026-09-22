"""Rendering summaries as text or JSON."""

import json
from datetime import datetime

from loganalyse.stats import (
    EndpointReport,
    ErrorReport,
    Summary,
    duration_stats,
    top_paths,
)


def human_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:,.1f} {unit}"
        size /= 1024
    return f"{size:,.1f} TB"  # pragma: no cover - unreachable, kept for mypy


def _stamp(moment: datetime | None) -> str:
    return moment.strftime("%Y-%m-%d %H:%M:%S") if moment else "-"


def format_summary(summary: Summary, source: str) -> str:
    if summary.requests == 0:
        return (
            f"File:            {source}\n"
            f"Lines:           {summary.total_lines:,} "
            f"({summary.unparsable:,} unparsable)\n"
            "No parsable requests in the selected period.\n"
        )

    lines = [
        f"File:            {source}",
        f"Lines:           {summary.total_lines:,} "
        f"({summary.unparsable:,} unparsable, {summary.unparsable_share:.1%})",
        f"Period:          {_stamp(summary.first_seen)} - {_stamp(summary.last_seen)}",
        f"Requests:        {summary.requests:,}",
        f"Unique clients:  {len(summary.clients):,}",
        f"Total traffic:   {human_bytes(summary.bytes_sent)}",
        "",
        "Status codes:",
    ]

    for status_class in sorted(summary.status_classes):
        count = summary.status_classes[status_class]
        lines.append(f"  {status_class}   {count:>9,}   {count / summary.requests:>6.1%}")

    lines += ["", "Top 5 endpoints:"]
    for endpoint, count in top_paths(summary, 5):
        lines.append(f"  {endpoint:<32} {count:>9,}   {count / summary.requests:>6.1%}")

    stats = duration_stats(summary.durations)
    lines += [
        "",
        "Response time:   "
        f"mean {stats['mean']:.3f}s  median {stats['median']:.3f}s  "
        f"p95 {stats['p95']:.3f}s  p99 {stats['p99']:.3f}s",
    ]
    return "\n".join(lines) + "\n"


def format_slowest(reports: list[EndpointReport]) -> str:
    if not reports:
        return "No endpoint has enough requests to rank.\n"

    lines = [f"{'endpoint':<36}{'requests':>10}{'mean':>10}{'p95':>10}{'errors':>9}"]
    lines.append("-" * 75)
    for report in reports:
        lines.append(
            f"{report.endpoint:<36}{report.requests:>10,}"
            f"{report.mean_duration:>9.3f}s{report.p95_duration:>9.3f}s{report.errors:>9,}"
        )
    return "\n".join(lines) + "\n"


def format_errors(reports: list[ErrorReport]) -> str:
    if not reports:
        return "No errors in the selected period.\n"

    lines = [f"{'status':>6}  {'endpoint':<36}{'count':>8}  first seen           last seen"]
    lines.append("-" * 96)
    for report in reports:
        lines.append(
            f"{report.status:>6}  {report.endpoint:<36}{report.count:>8,}  "
            f"{_stamp(report.first_seen)}  {_stamp(report.last_seen)}"
        )
    return "\n".join(lines) + "\n"


def summary_as_json(summary: Summary, source: str) -> str:
    stats = duration_stats(summary.durations)
    payload = {
        "source": source,
        "lines": summary.total_lines,
        "unparsable": summary.unparsable,
        "requests": summary.requests,
        "unique_clients": len(summary.clients),
        "bytes_sent": summary.bytes_sent,
        "first_seen": summary.first_seen.isoformat() if summary.first_seen else None,
        "last_seen": summary.last_seen.isoformat() if summary.last_seen else None,
        "status_classes": dict(sorted(summary.status_classes.items())),
        "top_endpoints": [
            {"endpoint": endpoint, "requests": count} for endpoint, count in top_paths(summary, 10)
        ],
        "response_time": {key: round(value, 4) for key, value in stats.items()},
    }
    return json.dumps(payload, indent=2)


def slowest_as_json(reports: list[EndpointReport]) -> str:
    return json.dumps(
        [
            {
                "endpoint": report.endpoint,
                "requests": report.requests,
                "mean": round(report.mean_duration, 4),
                "p95": round(report.p95_duration, 4),
                "errors": report.errors,
            }
            for report in reports
        ],
        indent=2,
    )


def errors_as_json(reports: list[ErrorReport]) -> str:
    return json.dumps(
        [
            {
                "status": report.status,
                "endpoint": report.endpoint,
                "count": report.count,
                "first_seen": report.first_seen.isoformat(),
                "last_seen": report.last_seen.isoformat(),
            }
            for report in reports
        ],
        indent=2,
    )
