"""Storage abstraction.

``Repository`` is a Protocol, not a base class: an implementation satisfies it by
having the right methods, not by inheriting. That keeps test doubles trivial.
"""

from collections.abc import Iterator
from typing import Protocol

from txlib.models import Currency, Money, Transaction


class Repository(Protocol):
    """Anything that can store transactions and summarise them."""

    def add(self, transaction: Transaction) -> None: ...

    def all(self) -> list[Transaction]: ...

    def totals_by_recipient(self) -> dict[tuple[str, Currency], Money]: ...


class InMemoryRepository:
    """A repository backed by a list. Note: it does NOT inherit from Repository."""

    def __init__(self) -> None:
        self._transactions: list[Transaction] = []

    def __len__(self) -> int:
        return len(self._transactions)

    def __iter__(self) -> Iterator[Transaction]:
        return iter(self._transactions)

    def __repr__(self) -> str:
        return f"InMemoryRepository({len(self._transactions)} transactions)"

    def add(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)

    def all(self) -> list[Transaction]:
        # A copy, so callers cannot mutate our internal list.
        return list(self._transactions)

    def totals_by_recipient(self) -> dict[tuple[str, Currency], Money]:
        """Sum per (recipient, currency).

        The key is a tuple because summing across currencies is meaningless - and
        because tuples are hashable, they can be dict keys directly.
        """
        totals: dict[tuple[str, Currency], Money] = {}
        for transaction in self._transactions:
            key = (transaction.recipient, transaction.money.currency)
            current = totals.get(key)
            totals[key] = transaction.money if current is None else current + transaction.money
        return totals
