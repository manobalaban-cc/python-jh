from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal

import pytest

from txlib.models import Currency, Money, Transaction


def test_currency_is_a_string() -> None:
    assert Currency.EUR == "EUR"
    assert f"{Currency.GBP}" == "GBP"
    assert Currency("HUF") is Currency.HUF


def test_money_str() -> None:
    assert str(Money(Decimal("815.85"), Currency.GBP)) == "815.85 GBP"
    assert str(Money(Decimal("1234.5"), Currency.EUR)) == "1,234.50 EUR"


def test_money_defaults_to_eur() -> None:
    assert Money(Decimal("1")).currency is Currency.EUR


def test_money_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="negative"):
        Money(Decimal("-1"), Currency.EUR)


def test_money_is_immutable() -> None:
    money = Money(Decimal("10"), Currency.EUR)
    with pytest.raises(FrozenInstanceError):
        money.amount = Decimal("20")  # type: ignore[misc]


def test_money_is_hashable_and_comparable_by_value() -> None:
    a = Money(Decimal("10"), Currency.EUR)
    b = Money(Decimal("10"), Currency.EUR)
    assert a == b
    assert a is not b
    assert {a, b} == {a}, "equal values must hash the same"


def test_money_addition() -> None:
    total = Money(Decimal("10"), Currency.EUR) + Money(Decimal("5.50"), Currency.EUR)
    assert total == Money(Decimal("15.50"), Currency.EUR)


def test_money_addition_rejects_mixed_currencies() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("10"), Currency.EUR) + Money(Decimal("10"), Currency.GBP)


def test_money_multiplication_works_both_ways() -> None:
    money = Money(Decimal("10"), Currency.EUR)
    assert money * 3 == Money(Decimal("30"), Currency.EUR)
    assert 3 * money == Money(Decimal("30"), Currency.EUR)


def test_transaction_is_large(sample_transaction: Transaction) -> None:
    assert sample_transaction.is_large(Decimal("800")) is True
    assert sample_transaction.is_large() is False  # default threshold is 1000


def test_transactions_sort_chronologically() -> None:
    older = Transaction(datetime(2024, 1, 1), Money(Decimal("1")), "A")
    newer = Transaction(datetime(2024, 6, 1), Money(Decimal("1")), "B")
    assert sorted([newer, older]) == [older, newer]
    assert min(newer, older) is older


def test_transaction_repr_is_informative(sample_transaction: Transaction) -> None:
    text = repr(sample_transaction)
    assert "Transaction(" in text
    assert "Amazon" in text
