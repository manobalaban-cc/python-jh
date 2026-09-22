"""Exception hierarchy for the library.

One base class per package means a caller can write a single `except TxError` and
still catch everything we raise, without catching unrelated bugs.
"""


class TxError(Exception):
    """Base class for every error raised by txlib."""


class SourceError(TxError):
    """The input could not be read, or is not a transaction file at all."""


class ValidationError(TxError):
    """A single field of a single row failed validation."""

    def __init__(self, field: str, reason: str, row_number: int) -> None:
        super().__init__(f"row {row_number}, field {field!r}: {reason}")
        self.field = field
        self.reason = reason
        self.row_number = row_number
