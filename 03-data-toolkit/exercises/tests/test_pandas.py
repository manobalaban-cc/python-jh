"""Tests for the module 03 exercises.

They run against the real datasets in ../../../data, so the numbers are real too.
"""

from pathlib import Path

import pandas as pd
import pytest

from tasks.task_pandas import (
    add_amount_band,
    attach_targets,
    busiest_weekday,
    indicators_to_long,
    load_car_sales,
    load_transactions,
    monthly_totals,
    price_vs_make_average,
    revenue_by_location,
    top_recipients,
    total_by_currency,
)

DATA = Path(__file__).resolve().parents[3] / "data"


@pytest.fixture(scope="session")
def transactions() -> pd.DataFrame:
    return load_transactions(DATA / "transactions.csv")


@pytest.fixture(scope="session")
def car_sales() -> pd.DataFrame:
    return load_car_sales(DATA / "car_sales.csv")


# --- loading and cleaning ----------------------------------------------------


def test_load_transactions_drops_incomplete_rows(transactions: pd.DataFrame) -> None:
    assert len(transactions) == 991, "1000 rows in the file, 9 of them incomplete"
    assert transactions.isna().sum().sum() == 0


def test_load_transactions_uses_snake_case_columns(transactions: pd.DataFrame) -> None:
    assert list(transactions.columns) == ["timestamp", "amount", "currency", "recipient"]


def test_load_transactions_sets_dtypes(transactions: pd.DataFrame) -> None:
    assert pd.api.types.is_datetime64_any_dtype(transactions["timestamp"])
    assert pd.api.types.is_numeric_dtype(transactions["amount"])
    assert isinstance(transactions["currency"].dtype, pd.CategoricalDtype)


def test_load_transactions_normalises_text(transactions: pd.DataFrame) -> None:
    assert set(transactions["currency"].unique()) <= {"EUR", "USD", "GBP", "JPY", "CAD"}
    assert (transactions["recipient"] == transactions["recipient"].str.strip()).all()


def test_index_is_reset(transactions: pd.DataFrame) -> None:
    assert transactions.index.tolist() == list(range(len(transactions)))


# --- aggregation -------------------------------------------------------------


def test_total_by_currency(transactions: pd.DataFrame) -> None:
    totals = total_by_currency(transactions)
    assert totals.index[0] == "CAD", "CAD has the largest total"
    assert totals.is_monotonic_decreasing
    assert round(float(totals.sum()), 2) == round(float(transactions["amount"].sum()), 2)


def test_top_recipients(transactions: pd.DataFrame) -> None:
    top = top_recipients(transactions, 3)
    assert list(top.columns) == ["recipient", "transactions", "total"]
    assert len(top) == 3
    assert top.loc[0, "recipient"] == "Amazon"
    assert top.loc[0, "transactions"] == 226


def test_monthly_totals(transactions: pd.DataFrame) -> None:
    monthly = monthly_totals(transactions)
    assert isinstance(monthly.index, pd.DatetimeIndex)
    assert monthly.index.is_monotonic_increasing
    assert round(float(monthly.sum()), 2) == round(float(transactions["amount"].sum()), 2)


def test_add_amount_band(transactions: pd.DataFrame) -> None:
    banded = add_amount_band(transactions)
    assert "band" not in transactions.columns, "the input must not be modified"

    counts = banded["band"].value_counts()
    assert counts["small"] == 93
    assert counts["medium"] == 408
    assert counts["large"] == 490

    assert banded.loc[banded["amount"] < 100, "band"].eq("small").all()
    assert banded.loc[banded["amount"] >= 500, "band"].eq("large").all()


def test_busiest_weekday(transactions: pd.DataFrame) -> None:
    assert busiest_weekday(transactions) == "Monday"


# --- car sales ---------------------------------------------------------------


def test_load_car_sales(car_sales: pd.DataFrame) -> None:
    assert len(car_sales) == 5000
    assert pd.api.types.is_datetime64_any_dtype(car_sales["Date"])
    assert isinstance(car_sales["VehicleMake"].dtype, pd.CategoricalDtype)


def test_revenue_by_location(car_sales: pd.DataFrame) -> None:
    summary = revenue_by_location(car_sales)
    assert list(summary.columns) == ["DealershipLocation", "sales", "revenue", "avg_price"]
    assert summary["revenue"].is_monotonic_decreasing
    assert summary["sales"].sum() == 5000
    assert summary.loc[0, "DealershipLocation"] == "Chicago"


def test_price_vs_make_average(car_sales: pd.DataFrame) -> None:
    enriched = price_vs_make_average(car_sales)
    assert len(enriched) == len(car_sales), "transform must not change the row count"
    assert {"make_avg_price", "price_delta"} <= set(enriched.columns)

    # The deltas within one make must cancel out.
    per_make = enriched.groupby("VehicleMake", observed=True)["price_delta"].sum()
    assert per_make.abs().max() < 1e-6


def test_attach_targets_rejects_duplicate_keys(car_sales: pd.DataFrame) -> None:
    locations = list(car_sales["DealershipLocation"].unique())
    targets = pd.DataFrame({"DealershipLocation": locations, "target": range(len(locations))})

    merged = attach_targets(car_sales, targets)
    assert len(merged) == len(car_sales)
    assert merged["target"].notna().all()

    duplicated = pd.concat([targets, targets.head(1)], ignore_index=True)
    with pytest.raises(pd.errors.MergeError):
        attach_targets(car_sales, duplicated)


# --- reshaping ---------------------------------------------------------------


def test_indicators_to_long() -> None:
    long = indicators_to_long(DATA / "country_indicators.csv")

    assert list(long.columns) == ["country", "country_code", "series", "year", "value"]
    assert long["year"].between(2000, 2015).all()
    assert pd.api.types.is_integer_dtype(long["year"])
    assert pd.api.types.is_float_dtype(long["value"])
    assert long["value"].notna().all(), "rows without a value must be dropped"
    assert len(long) == 36132
