"""Turning raw CSV rows into domain objects."""

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal, InvalidOperation

from txlib.errors import ValidationError
from txlib.models import Currency, Money, Transaction

REQUIRED_COLUMNS = ("Timestamp", "Amount", "Currency", "Recipient")


def _required(row: Mapping[str, str], field: str, row_number: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValidationError(field, "missing or empty", row_number)
    return value


def parse_row(row: Mapping[str, str], row_number: int) -> Transaction:
    """Convert one CSV row into a :class:`Transaction`.

    Args:
        row: The raw row, as produced by ``csv.DictReader``.
        rows_number: 1-based row number, used in error messages.

    Raises:
        ValidationError: If any field is missing or cannot be parsed.
    """
    raw_timestamp = _required(row, "Timestamp", row_number)
    raw_amount = _required(row, "Amount", row_number)
    raw_currency = _required(row, "Currency", row_number)
    recipient = _required(row, "Recipient", row_number)

    try:
        timestamp = datetime.fromisoformat(raw_timestamp)
    except ValueError as exc:
        # `from exc` keeps the original parse error visible in the traceback.
        raise ValidationError(
            "Timestamp", f"not a datetime: {raw_timestamp!r}", row_number
        ) from exc

    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as exc:
        raise ValidationError("Amount", f"not a number: {raw_amount!r}", row_number) from exc

    try:
        currency = Currency(raw_currency.upper())
    except ValueError as exc:
        accepted = ", ".join(c.value for c in Currency)
        raise ValidationError(
            "Currency",
            f"unknown currency {raw_currency!r}, expected one of: {accepted}",
            row_number,
        ) from exc

    try:
        money = Money(amount, currency)
    except ValueError as exc:
        raise ValidationError("Amount", str(exc), row_number) from exc

    return Transaction(timestamp=timestamp, money=money, recipient=recipient)
