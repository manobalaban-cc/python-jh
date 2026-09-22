"""CLI entry point: python -m txlib data/transactions.csv"""

import logging
import sys
from pathlib import Path

from txlib.errors import SourceError
from txlib.loading import load_file
from txlib.repository import InMemoryRepository


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m txlib CSV_PATH", file=sys.stderr)
        return 2

    # Logging is configured here, in the entry point - never inside a library module.
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(name)s: %(message)s")

    repository = InMemoryRepository()
    try:
        result = load_file(Path(args[0]), repository)
    except SourceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"\n{result}")
    print("\nTop 10 recipients:")
    totals = repository.totals_by_recipient()
    for (recipient, _), money in sorted(totals.items(), key=lambda kv: kv[1].amount, reverse=True)[
        :10
    ]:
        print(f"  {recipient:<20} {money}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
