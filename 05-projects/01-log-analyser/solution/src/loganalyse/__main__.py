"""Command-line interface for the log analyser."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from loganalyse import formatting, stats
from loganalyse.parsing import open_log

logger = logging.getLogger(__name__)

TIMESTAMP_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d")


def parse_moment(raw: str) -> datetime:
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD or 'YYYY-MM-DD HH:MM', got {raw!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loganalyse", description="Analyse nginx access logs.")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v info, -vv debug")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("path", help="log file, or - for stdin")
    common.add_argument("--since", type=parse_moment, help="only entries at or after this moment")
    common.add_argument("--until", type=parse_moment, help="only entries before this moment")
    common.add_argument("--format", choices=["text", "json"], default="text")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("summary", parents=[common], help="overall statistics")

    slowest = subparsers.add_parser("slowest", parents=[common], help="slowest endpoints")
    slowest.add_argument("--top", type=int, default=10)
    slowest.add_argument("--min-requests", type=int, default=10)

    errors = subparsers.add_parser("errors", parents=[common], help="4xx and 5xx responses")
    errors.add_argument("--status", choices=["4xx", "5xx"], help="restrict to one class")

    return parser


def configure_logging(verbosity: int) -> None:
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    logging.basicConfig(level=level, format="%(levelname)-8s %(message)s", stream=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)

    if args.path != "-" and not Path(args.path).is_file():
        logger.error("no such file: %s", args.path)
        return 1

    try:
        with open_log(args.path) as handle:
            summary = stats.aggregate(handle, since=args.since, until=args.until)
    except OSError as exc:
        logger.error("cannot read %s: %s", args.path, exc)
        return 1

    logger.info("parsed %d lines, %d unparsable", summary.total_lines, summary.unparsable)

    if args.command == "summary":
        output = (
            formatting.summary_as_json(summary, args.path)
            if args.format == "json"
            else formatting.format_summary(summary, args.path)
        )
    elif args.command == "slowest":
        # Each branch keeps its own name: reusing one variable for two different
        # report types is exactly what mypy is there to stop.
        slowest = stats.slowest_endpoints(summary, limit=args.top, min_requests=args.min_requests)
        output = (
            formatting.slowest_as_json(slowest)
            if args.format == "json"
            else formatting.format_slowest(slowest)
        )
    else:
        errors = stats.error_reports(summary, status_class=args.status)
        output = (
            formatting.errors_as_json(errors)
            if args.format == "json"
            else formatting.format_errors(errors)
        )

    print(output, end="" if output.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
