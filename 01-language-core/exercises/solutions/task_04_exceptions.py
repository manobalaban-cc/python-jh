"""Reference solution — chapter 07."""

from collections.abc import Callable, Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ImportFailure(Exception):
    """Base class for every error raised by this module.

    Giving a package one base exception lets callers write a single
    `except ImportFailure` and still catch everything we throw.
    """


class ValidationError(ImportFailure):
    """One field of one record failed validation."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason


class SourceUnavailable(ImportFailure):
    """The input could not be read at all."""


def parse_amount(text: str) -> Decimal:
    try:
        amount = Decimal(text.strip())
    except (InvalidOperation, AttributeError) as exc:
        # `from exc` keeps the original error in the traceback instead of hiding it.
        raise ValidationError("amount", f"not a number: {text!r}") from exc

    if amount < 0:
        raise ValidationError("amount", f"must not be negative: {amount}")
    return amount


def dig(data: dict[str, object], *keys: str) -> object | None:
    current: object = data
    try:
        for key in keys:
            current = current[key]  # type: ignore[index]
    except (KeyError, TypeError):
        # KeyError: the key is missing. TypeError: we hit a non-subscriptable value.
        return None
    return current


def retry(operation: Callable[[], str], attempts: int = 3) -> str:
    last_error: OSError | None = None

    for _ in range(attempts):
        try:
            return operation()
        except OSError as exc:  # only transport-level errors are retriable
            last_error = exc

    raise SourceUnavailable(f"failed after {attempts} attempts") from last_error


def process_records(
    records: Iterable[dict[str, str]],
) -> tuple[list[Decimal], list[str]]:
    amounts: list[Decimal] = []
    errors: list[str] = []

    for row, record in enumerate(records, start=1):
        try:
            amounts.append(parse_amount(record["amount"]))
        except KeyError:
            errors.append(f"row {row}: missing field 'amount'")
        except ValidationError as exc:
            errors.append(f"row {row}: {exc}")

    return amounts, errors


def load_settings(path: str, defaults: dict[str, str]) -> dict[str, str]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        # Only this one is expected. A PermissionError is a real problem and
        # must not be swallowed, so we do not catch OSError here.
        return dict(defaults)

    settings = dict(defaults)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        settings[key.strip()] = value.strip()
    return settings
