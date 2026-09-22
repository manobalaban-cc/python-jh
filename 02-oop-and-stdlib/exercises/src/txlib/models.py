"""Domain model — TODO.

See the specification in ../../README.md, section "1. txlib/models.py".

Requirements recap:
  - Currency: StrEnum with EUR, USD, GBP, JPY, CAD, HUF
  - Money: frozen, slotted dataclass (amount: Decimal, currency: Currency = EUR)
      * __post_init__ rejects negative amounts
      * __str__ -> "1,234.50 EUR"
      * __add__ (same currency only), __mul__ and __rmul__ by int | Decimal
  - Transaction: frozen, slotted dataclass (timestamp, money, recipient)
      * is_large(threshold=Decimal("1000"))
      * sorts chronologically
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Currency(StrEnum):
    """TODO: the supported currencies."""


@dataclass(frozen=True, slots=True)
class Money:
    """TODO: an amount in a single currency."""

    amount: Decimal


@dataclass(frozen=True, slots=True)
class Transaction:
    """TODO: one bank transaction."""

    timestamp: datetime
