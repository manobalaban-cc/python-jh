"""Module 03 exercises — pandas on the real datasets in ../../../data.

Implement every function so that tests/test_pandas.py passes. The tests use the
actual files, so the expected numbers are real; if a count is off by a few rows,
your cleaning rules differ from the ones described here.

Rules:
  - no loops over rows (no iterrows, no apply(axis=1) unless a task says otherwise)
  - never modify the DataFrame you were given; return a new one
"""

from pathlib import Path

import pandas as pd

CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CAD"]


def load_transactions(path: Path) -> pd.DataFrame:
    """Load and clean data/transactions.csv.

    Steps:
      1. read the CSV
      2. lower-case and strip the column names (timestamp, amount, currency, recipient)
      3. timestamp -> datetime, amount -> numeric (unparseable values become NaN)
      4. currency -> stripped, upper-cased, then category dtype
      5. recipient -> stripped, title-cased
      6. drop rows missing any of the four fields, then drop exact duplicates
      7. reset the index

    The file has 1000 rows; 9 of them are incomplete.
    """
    raise NotImplementedError


def total_by_currency(df: pd.DataFrame) -> pd.Series:
    """Total amount per currency, largest first."""
    raise NotImplementedError


def top_recipients(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """The n recipients with the most transactions.

    Columns: recipient, transactions (count), total (sum). Ties broken by name.
    The index must be 0..n-1.
    """
    raise NotImplementedError


def monthly_totals(df: pd.DataFrame) -> pd.Series:
    """Total amount per calendar month, indexed by month end, chronological.

    Hint: this is what resample() is for.
    """
    raise NotImplementedError


def add_amount_band(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a `band` column: small < 100 <= medium < 500 <= large.

    Hint: pd.cut with explicit bin edges.
    """
    raise NotImplementedError


def busiest_weekday(df: pd.DataFrame) -> str:
    """Name of the weekday with the most transactions, e.g. "Monday"."""
    raise NotImplementedError


def load_car_sales(path: Path) -> pd.DataFrame:
    """Load data/car_sales.csv.

    Parse Date as a datetime, and make VehicleMake, VehicleType, SaleType and
    DealershipLocation category dtype.
    """
    raise NotImplementedError


def revenue_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """Per dealership: sales (count), revenue (sum), avg_price (mean).

    Highest revenue first, index reset. Use named aggregation.
    """
    raise NotImplementedError


def price_vs_make_average(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with `make_avg_price` and `price_delta` columns.

    `make_avg_price` is the average SalePrice of that row's VehicleMake, and
    `price_delta` is SalePrice minus that average. The row count must not change.

    Hint: groupby(...).transform(...)
    """
    raise NotImplementedError


def attach_targets(sales: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    """Left-join the per-dealership targets onto the sales rows.

    The join must RAISE if the targets table has more than one row per
    dealership - a silent row multiplication would corrupt every total
    downstream. Hint: the `validate` parameter of merge.
    """
    raise NotImplementedError


def indicators_to_long(path: Path) -> pd.DataFrame:
    """Reshape the wide World Bank export (data/country_indicators.csv) to long form.

    The file is semicolon-separated and uses ".." for missing values. The year
    columns are named "2000 [YR2000]" and so on.

    Output columns: country, country_code, series, year (int), value (float).
    Drop rows that have no value. Sort by country, series, year and reset the index.
    """
    raise NotImplementedError
