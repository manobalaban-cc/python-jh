# 02 — pandas fundamentals

## Series and DataFrame

```python
import pandas as pd

s = pd.Series([100, 250, 75], index=["a", "b", "c"], name="amount")
```

A **Series** is a one-dimensional labelled array: a NumPy array plus an **index**.

```python
df = pd.DataFrame(
    {
        "recipient": ["Amazon", "Spotify", "Amazon"],
        "amount": [100.0, 250.0, 75.0],
        "currency": ["EUR", "EUR", "GBP"],
    }
)
```

A **DataFrame** is a table: an ordered collection of Series sharing one index. Each column has
its own dtype — that is the difference from a NumPy 2-D array.

Mental model for someone who knows SQL: a DataFrame is a result set you can keep querying, and
the index is a row label that survives filtering and joins.

## Loading data

```python
df = pd.read_csv("data/transactions.csv")

# The arguments you will actually need
df = pd.read_csv(
    "data/country_indicators.csv",
    sep=";",                       # a European "CSV"
    encoding="utf-8",              # or "utf-8-sig" when Excel added a BOM
    na_values=["..", "N/A", ""],   # extra strings that mean "missing"
    decimal=",",                   # 1234,56 style numbers
    thousands=" ",
    parse_dates=["Date"],
    dtype={"SalesID": "int32", "VehicleMake": "category"},
    usecols=["Date", "SalePrice", "VehicleMake"],   # read only what you need
    nrows=1000,                    # peek at a huge file
)

pd.read_excel("data/marketing_xlsx/Marketing_Expenditures_Retail.xlsx", sheet_name=0)
pd.read_json(...), pd.read_parquet(...), pd.read_sql(query, connection)
```

Writing:

```python
df.to_csv("out.csv", index=False)       # index=False unless the index is meaningful!
df.to_parquet("out.parquet")            # keeps dtypes, compressed, much faster to reload
df.to_excel("out.xlsx", sheet_name="summary", index=False)
```

## First look at a dataset

Always run these before anything else:

```python
df.shape            # (rows, columns)
df.head(10)
df.tail()
df.sample(5)        # random rows - better for spotting patterns than the first five
df.info()           # dtypes, non-null counts, memory usage  <- the most useful one
df.describe()       # numeric summary
df.describe(include="object")     # counts, unique, top for text columns
df.columns.tolist()
df.dtypes
df.isna().sum()     # missing values per column
df["currency"].value_counts(dropna=False)
df["amount"].nunique()
```

`df.info()` answers three questions at once: how big is it, what types did pandas infer, and
where is data missing. Make it a reflex.

## Selecting columns

```python
df["amount"]                    # a Series
df[["amount", "currency"]]      # a DataFrame (note the double brackets)
df.amount                       # works, but breaks on spaces and shadows methods - avoid
```

## Selecting rows: `loc` and `iloc`

This is the part everyone gets wrong at first.

| | Meaning | Slice end |
|---|---|---|
| `df.loc[...]` | by **label** (index value, column name) | **inclusive** |
| `df.iloc[...]` | by **position** (0-based integer) | exclusive |

```python
df.loc[0]                         # the row LABELLED 0
df.loc[0:5]                       # labels 0 through 5 - SIX rows, the end is included
df.loc[0, "amount"]
df.loc[0:5, ["amount", "currency"]]
df.loc[:, "amount"]

df.iloc[0]                        # the FIRST row, whatever its label
df.iloc[0:5]                      # five rows
df.iloc[-1]                       # the last row
df.iloc[0, 1]                     # first row, second column
```

After filtering or sorting, labels and positions no longer coincide — that is when mixing them
up produces silently wrong results.

## Filtering with boolean masks

```python
df[df["amount"] > 1000]
df[(df["amount"] > 1000) & (df["currency"] == "EUR")]       # & | ~ with parentheses
df[df["currency"].isin(["EUR", "GBP"])]
df[df["recipient"].str.startswith("A")]
df[df["amount"].between(100, 500)]
df[df["recipient"].isna()]
df[~df["recipient"].isna()]                                  # ~ is "not"

# Same thing, more readable in a chain
df.query("amount > 1000 and currency == 'EUR'")
```

Remember: `and`/`or` raise `ValueError: The truth value of a Series is ambiguous`. Use `&`/`|`,
and parenthesise every comparison.

## Adding and modifying columns

```python
df["amount_with_vat"] = df["amount"] * 1.27                 # vectorised
df["is_large"] = df["amount"] > 1000
df["recipient"] = df["recipient"].str.strip().str.title()

# Conditional column
import numpy as np
df["size"] = np.where(df["amount"] > 1000, "large", "small")

# Several conditions
df["band"] = pd.cut(df["amount"], bins=[0, 100, 1000, np.inf], labels=["S", "M", "L"])

# In a chain, without mutating the original
df = df.assign(
    amount_with_vat=lambda d: d["amount"] * 1.27,
    is_large=lambda d: d["amount"] > 1000,
)
```

### Chained assignment, copy-on-write, and `SettingWithCopyWarning`

```python
df[df["amount"] > 100]["flag"] = True     # never do this
```

This is *chained assignment*: the filter produces a new object, and you set a column on that
temporary, which is then thrown away.

- **pandas 2.x** raised the famously unhelpful `SettingWithCopyWarning` — and whether the
  original was modified depended on internal details.
- **pandas 3.x** made copy-on-write the default. The assignment now raises
  `ChainedAssignmentError` and reliably does **nothing** to `df`.

Either way the fix is the same — be explicit about what you are modifying:

```python
df.loc[df["amount"] > 100, "flag"] = True     # modify the original

subset = df[df["amount"] > 100].copy()        # or work on a deliberate copy
subset["flag"] = True
```

Under copy-on-write every operation behaves as if it returned a copy, so a derived frame never
mutates its parent by accident. It is a big improvement, but you will still meet pandas 2 in
existing projects — know both.

## Do not loop over rows

```python
# WRONG - slow and verbose
for i in range(len(df)):
    df.loc[i, "total"] = df.loc[i, "price"] * df.loc[i, "quantity"]

# Also wrong, just less obviously
for index, row in df.iterrows():
    ...

# RIGHT
df["total"] = df["price"] * df["quantity"]
```

`iterrows()` is roughly a thousand times slower than the vectorised form on a large frame, and
it gives you each row as a Series with the dtypes flattened. Rules of thumb:

1. Vectorised operation if at all possible.
2. `df["col"].map(func)` or `df.apply(func, axis=1)` when the logic really is per row.
   `apply` is a loop in disguise — convenient, not fast.
3. `itertuples()` if you genuinely need to iterate (faster than `iterrows`, and named).

## Sorting and the index

```python
df.sort_values("amount", ascending=False)
df.sort_values(["currency", "amount"], ascending=[True, False])
df.nlargest(10, "amount")           # faster and clearer than sort + head
df.nsmallest(5, "amount")

df.sort_index()
df.reset_index(drop=True)           # renumber 0..n-1 after filtering; drop=True discards the old one
df.set_index("SalesID")             # make a column the index
```

Why care about the index? Because pandas **aligns on it**. Adding two Series matches labels, not
positions:

```python
a = pd.Series([1, 2, 3], index=["x", "y", "z"])
b = pd.Series([10, 20, 30], index=["z", "y", "x"])
a + b        # x: 31, y: 22, z: 13   - aligned by label, not order
```

This is a feature (it prevents silently comparing misaligned data) and a trap (it produces
`NaN` when labels do not match).

## A first complete example

```python
import pandas as pd

df = pd.read_csv("data/transactions.csv", parse_dates=["Timestamp"])

print(df.info())
print(df.isna().sum())

large_eur = (
    df[(df["Amount"] > 500) & (df["Currency"] == "EUR")]
    .sort_values("Amount", ascending=False)
    .head(10)
)
print(large_eur[["Timestamp", "Recipient", "Amount"]])

print(f"total: {df['Amount'].sum():,.2f}")
print(f"mean:  {df['Amount'].mean():,.2f}")
print(df["Recipient"].value_counts().head())
```

## Check yourself

1. What is the difference between a Series and a DataFrame?
2. What is the difference between `loc` and `iloc`, including slice behaviour?
3. Why does `df[df.a > 1 and df.b < 2]` raise, and what is the fix?
4. What does `SettingWithCopyWarning` mean and how do you avoid it?
5. Why is `iterrows()` almost always the wrong answer?
6. What does "pandas aligns on the index" mean, and when does it bite?
