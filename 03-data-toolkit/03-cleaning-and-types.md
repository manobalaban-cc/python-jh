# 03 — Cleaning real data: types, missing values, dates, strings

Textbook examples use clean data. Real files have a byte-order mark in the header, `..` for
missing, `5/31/2024 Friday` as a date and numbers stored as text. This chapter uses the actual
files in [`../data/`](../data/).

## The dtypes you will see

| dtype | Meaning |
|---|---|
| `int64`, `float64` | numbers (NumPy) |
| `Int64`, `Float64` | *nullable* numbers (pandas) — can hold `<NA>` without becoming float |
| `str` | text. In pandas 3 this is the default; pandas 2 used `object` |
| `object` | "anything" — mixed types, or Python objects. Slow; usually a symptom |
| `bool`, `boolean` | booleans; the capitalised one is nullable |
| `datetime64[us]` / `[ns]` | timestamps |
| `timedelta64` | durations |
| `category` | repeated labels stored as codes — big memory saving |

```python
df.dtypes
df.info(memory_usage="deep")
```

An `object` column where you expected numbers is the single most common cause of "why is my
sum a concatenated string".

### Converting

```python
df["amount"] = df["amount"].astype("float64")
df["sales_id"] = df["sales_id"].astype("int32")
df["make"] = df["make"].astype("category")        # for repeated labels

# Safe numeric conversion: unparseable values become NaN instead of raising
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["when"] = pd.to_datetime(df["when"], errors="coerce")
```

`errors="coerce"` is the workhorse: convert what you can, mark the rest as missing, then decide
what to do about it — rather than crashing on row 7,412 of 10,000.

Converting a high-cardinality text column to `category` is one of the easiest wins available:

```python
df["VehicleMake"].memory_usage(deep=True)                      # before
df["VehicleMake"].astype("category").memory_usage(deep=True)   # often 10-20x smaller
```

## Missing data

`NaN` (float), `None`, `NaT` (missing timestamp) and `pd.NA` all mean "missing". Test with the
functions, never with `==`:

```python
df.isna().sum()                       # per column
df.isna().sum().sum()                 # total
df.isna().mean().sort_values()        # proportion missing per column
df[df["Currency"].isna()]             # the offending rows
```

### Deciding what to do

There is no default answer; the choice depends on why the value is missing.

```python
# 1. Drop rows where a critical field is missing
df = df.dropna(subset=["Amount", "Currency"])

# 2. Drop columns that are mostly empty
df = df.dropna(axis=1, thresh=int(0.5 * len(df)))

# 3. Fill with a constant
df["note"] = df["note"].fillna("")
df["quantity"] = df["quantity"].fillna(0)

# 4. Fill from the data itself
df["price"] = df["price"].fillna(df["price"].median())

# 5. Time series: carry the last observation forward
df["rate"] = df["rate"].ffill()          # or .bfill(), or .interpolate()
```

Two rules worth stating explicitly, because juniors get burned by both:

- **Filling numeric gaps with `0` changes your averages.** If a missing price means "unknown",
  filling it with zero invents cheap products. `NaN` is excluded from `mean()`; `0` is not.
- **Say what you did.** Any report that dropped 8% of rows must say so. Count before and after.

```python
before = len(df)
df = df.dropna(subset=["Amount"])
logger.info("dropped %d rows with no amount (%.1f%%)", before - len(df), 100 * (before - len(df)) / before)
```

## Duplicates

```python
df.duplicated().sum()                          # fully identical rows
df.duplicated(subset=["SalesID"]).sum()        # by key
df[df.duplicated(subset=["SalesID"], keep=False)]     # show every copy, not just the extras

df = df.drop_duplicates()
df = df.drop_duplicates(subset=["SalesID"], keep="last")
```

Always look at the duplicates before deleting them. A duplicated key sometimes means a broken
join upstream, not a duplicated record.

## Dates

```python
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# The real file EUR_HUF_history.csv has dates like "5/31/2024 Friday"
rates = pd.read_csv("data/EUR_HUF_history.csv")
rates["Date"] = pd.to_datetime(rates["Date"].str.split().str[0], format="%m/%d/%Y")
```

Always pass `format=` when you know it: it is an order of magnitude faster and it fails loudly
on unexpected input instead of guessing. `dayfirst=True` exists for European `31/05/2024`.

Once a column is a real datetime, the `.dt` accessor opens up:

```python
df["year"] = df["Timestamp"].dt.year
df["month"] = df["Timestamp"].dt.month
df["weekday"] = df["Timestamp"].dt.day_name()
df["date"] = df["Timestamp"].dt.date
df["week"] = df["Timestamp"].dt.isocalendar().week
df["quarter"] = df["Timestamp"].dt.to_period("Q")

df[df["Timestamp"].dt.year == 2024]
df[df["Timestamp"].between("2024-01-01", "2024-06-30")]
```

With a DatetimeIndex you get time-series superpowers:

```python
ts = df.set_index("Timestamp").sort_index()

ts.loc["2024-05"]                       # every row in May 2024
ts.loc["2024-05-01":"2024-05-31"]
ts["Amount"].resample("ME").sum()       # monthly totals ("W", "D", "QE", "YE" also work)
ts["Amount"].rolling(7).mean()          # 7-period moving average
ts["Amount"].pct_change()               # period-over-period change
```

`resample` is the time-series equivalent of `groupby` — the single most useful function for
reporting.

## Strings

The `.str` accessor applies a string operation to a whole column, vectorised:

```python
df["Recipient"] = df["Recipient"].str.strip()
df["Recipient"] = df["Recipient"].str.title()
df["domain"] = df["CustomerEmail"].str.split("@").str[1]
df["has_digit"] = df["VehicleModel"].str.contains(r"\d", regex=True)
df["code"] = df["VehicleEngine"].str.extract(r"([\d.]+)L")     # capture group -> new column
df["clean"] = df["raw"].str.replace(r"\s+", " ", regex=True)
df["padded"] = df["id"].astype(str).str.zfill(6)
```

Numbers stored as European-formatted text:

```python
df["price"] = (
    df["price"]
    .str.replace(".", "", regex=False)     # thousands separator
    .str.replace(",", ".", regex=False)    # decimal comma
    .pipe(pd.to_numeric, errors="coerce")
)
```

A BOM in the header (`dogs_database.csv` has one) shows up as a first column named `ï»¿Name`:

```python
df = pd.read_csv("data/dogs_database.csv", encoding="utf-8-sig")
```

## Renaming and reshaping the header

```python
df = df.rename(columns={"Height (cm)": "height_cm", "Weight (kg)": "weight_kg"})

# Normalise every column name at once - do this immediately after loading
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(r"[^\w]+", "_", regex=True)
    .str.strip("_")
)
```

Consistent `snake_case` column names make everything downstream easier, including `df.query()`
and attribute access.

## Outliers and sanity checks

```python
df["Amount"].describe()
df["Amount"].quantile([0.01, 0.5, 0.99])

q1, q3 = df["Amount"].quantile([0.25, 0.75])
iqr = q3 - q1
outliers = df[(df["Amount"] < q1 - 1.5 * iqr) | (df["Amount"] > q3 + 1.5 * iqr)]

# Assertions that fail loudly instead of producing a wrong report
assert df["Amount"].ge(0).all(), "negative amounts found"
assert df["SalesID"].is_unique, "duplicate sales id"
assert df["Currency"].isin(["EUR", "USD", "GBP", "JPY", "CAD"]).all()
```

Put these checks in the pipeline, not in your head. A silent wrong number is worse than a crash.

## A complete cleaning pipeline

```python
import pandas as pd


def load_transactions(path: str) -> pd.DataFrame:
    """Load and clean the transaction export."""
    df = pd.read_csv(path)

    df.columns = df.columns.str.strip().str.lower()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["currency"] = df["currency"].str.strip().str.upper().astype("category")
    df["recipient"] = df["recipient"].str.strip().str.title()

    before = len(df)
    df = df.dropna(subset=["timestamp", "amount", "currency", "recipient"])
    dropped = before - len(df)
    if dropped:
        print(f"dropped {dropped} incomplete rows out of {before}")

    df = df.drop_duplicates()
    return df.reset_index(drop=True)


df = load_transactions("data/transactions.csv")
print(df.info())
```

Notice the shape: a function that takes a path and returns a clean DataFrame, with no global
state and nothing printed except a deliberate summary. That is what makes it testable.

## Check yourself

1. What does `errors="coerce"` do and why is it useful?
2. When is filling missing numbers with `0` wrong?
3. Why pass `format=` to `pd.to_datetime`?
4. What does the `.dt` accessor need before it works?
5. What is `resample` and how does it relate to `groupby`?
6. How do you fix a CSV whose first column name starts with `ï»¿`?
