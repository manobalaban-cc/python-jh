"""Reference solution — module 03 pandas exercises."""

from pathlib import Path

import numpy as np
import pandas as pd

CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CAD"]


def load_transactions(path: Path) -> pd.DataFrame:
    """Load and clean data/transactions.csv."""
    df = pd.read_csv(path)

    # Normalise the header once, immediately: everything downstream gets easier.
    df.columns = df.columns.str.strip().str.lower()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["currency"] = df["currency"].str.strip().str.upper()
    df["recipient"] = df["recipient"].str.strip().str.title()

    # A row missing any of these cannot be used, so it goes - deliberately, and countably.
    df = df.dropna(subset=["timestamp", "amount", "currency", "recipient"])
    df = df.drop_duplicates()

    df["currency"] = df["currency"].astype("category")
    return df.reset_index(drop=True)


def total_by_currency(df: pd.DataFrame) -> pd.Series:
    """Total amount per currency, largest first."""
    return df.groupby("currency", observed=True)["amount"].sum().sort_values(ascending=False)


def top_recipients(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """The n recipients with the highest transaction count."""
    return (
        df.groupby("recipient", as_index=False)
        .agg(transactions=("amount", "count"), total=("amount", "sum"))
        .sort_values(["transactions", "recipient"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )


def monthly_totals(df: pd.DataFrame) -> pd.Series:
    """Total amount per calendar month, indexed by month end."""
    return df.set_index("timestamp").sort_index()["amount"].resample("ME").sum()


def add_amount_band(df: pd.DataFrame) -> pd.DataFrame:
    """Add a `band` column: small (<100), medium (<500), large (>=500)."""
    result = df.copy()
    result["band"] = pd.cut(
        result["amount"],
        bins=[-np.inf, 100, 500, np.inf],
        labels=["small", "medium", "large"],
        right=False,  # [0,100) [100,500) [500,inf)
    )
    return result


def busiest_weekday(df: pd.DataFrame) -> str:
    """Name of the weekday with the most transactions."""
    counts = df["timestamp"].dt.day_name().value_counts()
    return str(counts.idxmax())


def load_car_sales(path: Path) -> pd.DataFrame:
    """Load data/car_sales.csv with the right dtypes."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df.columns = df.columns.str.strip()
    for column in ["VehicleMake", "VehicleType", "SaleType", "DealershipLocation"]:
        df[column] = df[column].astype("category")
    return df


def revenue_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """Sales count, total revenue and average price per dealership, best first."""
    return (
        df.groupby("DealershipLocation", as_index=False, observed=True)
        .agg(
            sales=("SalesID", "count"),
            revenue=("SalePrice", "sum"),
            avg_price=("SalePrice", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )


def price_vs_make_average(df: pd.DataFrame) -> pd.DataFrame:
    """Add `make_avg_price` and `price_delta` (price minus the make average)."""
    result = df.copy()
    # transform broadcasts the group value back onto every row of that group.
    result["make_avg_price"] = result.groupby("VehicleMake", observed=True)["SalePrice"].transform(
        "mean"
    )
    result["price_delta"] = result["SalePrice"] - result["make_avg_price"]
    return result


def attach_targets(sales: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    """Left-join one target row per dealership onto the sales rows.

    `validate` makes pandas raise if the relationship is not many-to-one - a
    duplicated target row would otherwise silently multiply the sales rows.
    """
    return sales.merge(
        targets,
        on="DealershipLocation",
        how="left",
        validate="many_to_one",
    )


def indicators_to_long(path: Path) -> pd.DataFrame:
    """Reshape the wide World Bank export into tidy long format.

    Columns: country, country_code, series, year (int), value (float).
    Rows with no value are dropped.
    """
    wide = pd.read_csv(path, sep=";", na_values=[".."])
    year_columns = [c for c in wide.columns if c[:4].isdigit()]

    long = wide.melt(
        id_vars=["Series Name", "Series Code", "Country Name", "Country Code"],
        value_vars=year_columns,
        var_name="year",
        value_name="value",
    )

    long["year"] = long["year"].str[:4].astype(int)
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long = long.dropna(subset=["value"])

    return (
        long.rename(
            columns={
                "Country Name": "country",
                "Country Code": "country_code",
                "Series Name": "series",
            }
        )[["country", "country_code", "series", "year", "value"]]
        .sort_values(["country", "series", "year"])
        .reset_index(drop=True)
    )
