"""Shared fixtures.

pytest imports this file automatically for every test in this directory and below,
so nothing here needs to be imported by hand.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from txlib.models import Currency, Money, Transaction

VALID_CSV = (
    "Timestamp,Amount,Currency,Recipient\n"
    "2024-04-27 13:59:08,815.85,GBP,Amazon\n"
    "2024-01-13 13:59:08,373.09,JPY,Starbucks\n"
    "2024-02-01 09:00:00,120.00,GBP,Amazon\n"
)


@pytest.fixture
def valid_csv(tmp_path: Path) -> Path:
    """A small, well-formed transaction file."""
    path = tmp_path / "transactions.csv"
    path.write_text(VALID_CSV, encoding="utf-8")
    return path


@pytest.fixture
def messy_csv(tmp_path: Path) -> Path:
    """A file where three of the five rows are broken, each in a different way."""
    path = tmp_path / "messy.csv"
    path.write_text(
        "Timestamp,Amount,Currency,Recipient\n"
        "2024-04-27 13:59:08,815.85,GBP,Amazon\n"  # ok
        "not-a-date,10.00,EUR,Spotify\n"  # bad timestamp
        "2024-04-28 10:00:00,abc,EUR,Spotify\n"  # bad amount
        "2024-04-29 10:00:00,10.00,XXX,Spotify\n"  # unknown currency
        "2024-04-30 10:00:00,25.00,EUR,Netflix\n",  # ok
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_transaction() -> Transaction:
    return Transaction(
        timestamp=datetime(2024, 4, 27, 13, 59, 8),
        money=Money(Decimal("815.85"), Currency.GBP),
        recipient="Amazon",
    )
