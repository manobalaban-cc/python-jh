"""Domain model: immutable value objects."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self


class Currency(StrEnum):
    """The currencies this library understands.

    StrEnum (3.11+) members behave as strings, so they serialise to JSON and
    format into f-strings without any conversion.
    """

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    HUF = "HUF"


@dataclass(frozen=True, slots=True, order=False)
class Money:
    """An amount in a single currency.

    Frozen, so it is hashable and safe to share; slotted, because a large import
    creates a lot of these.
    """

    amount: Decimal
    currency: Currency = Currency.EUR

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"amount must not be negative: {self.amount}")

    def __str__(self) -> str:
        return f"{self.amount:,.2f} {self.currency}"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError(f"cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        if not isinstance(factor, int | Decimal):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    # Makes `2 * money` work as well as `money * 2`.
    __rmul__ = __mul__

    @classmethod
    def zero(cls, currency: Currency) -> Self:
        return cls(Decimal("0"), currency)


@dataclass(frozen=True, slots=True)
class Transaction:
    """One bank transaction."""

    timestamp: datetime
    money: Money
    recipient: str

    def __lt__(self, other: "Transaction") -> bool:
        # `order=True` would compare every field in order, and Money defines no
        # ordering - so we define the one comparison that actually makes sense.
        # This is enough for sorted(), min() and max().
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.timestamp < other.timestamp

    def is_large(self, threshold: Decimal = Decimal("1000")) -> bool:
        """Is this transaction at or above ``threshold``?"""
        return self.money.amount >= threshold
