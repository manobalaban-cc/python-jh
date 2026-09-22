"""The use case: read a CSV file into a repository."""

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

from txlib.errors import SourceError, ValidationError
from txlib.instrumentation import timed
from txlib.parsing import REQUIRED_COLUMNS, parse_row
from txlib.repository import Repository

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ImportResult:
    """What one import run did."""

    imported: int = 0
    skipped: int = 0
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.imported + self.skipped

    def __str__(self) -> str:
        return f"{self.imported} imported, {self.skipped} skipped"


@timed
def load_file(path: Path, repository: Repository) -> ImportResult:
    """Load every transaction from ``path`` into ``repository``.

    A row that fails validation is counted and recorded, never fatal: one bad line
    in a 10,000 line export must not lose the other 9,999.

    Raises:
        SourceError: If the file is missing, unreadable, or not a transaction file.
    """
    result = ImportResult()

    try:
        # newline="" is required by the csv module; encoding is never left to the platform.
        with open(path, encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)

            missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames or ())
            if missing:
                raise SourceError(f"missing columns: {', '.join(sorted(missing))}")

            # Streaming: one row in memory at a time, however large the file.
            for row_number, row in enumerate(reader, start=1):
                try:
                    repository.add(parse_row(row, row_number))
                except ValidationError as exc:
                    logger.warning("skipping row %d: %s", row_number, exc.reason)
                    result.skipped += 1
                    result.errors.append(exc)
                else:
                    result.imported += 1

    except FileNotFoundError as exc:
        raise SourceError(f"no such file: {path}") from exc
    except OSError as exc:
        raise SourceError(f"cannot read {path}: {exc}") from exc

    return result
