# 04 — Grouping, joining, reshaping

If you know SQL, this chapter is mostly a translation table. If you know SQL well, you already
know 80% of pandas.

| SQL | pandas |
|---|---|
| `SELECT a, b FROM t` | `df[["a", "b"]]` |
| `WHERE x > 10` | `df[df["x"] > 10]` |
| `ORDER BY x DESC` | `df.sort_values("x", ascending=False)` |
| `LIMIT 10` | `df.head(10)` |
| `GROUP BY a` | `df.groupby("a")` |
| `COUNT(*)` | `.size()` |
| `SUM(x)` | `.agg({"x": "sum"})` |
| `HAVING sum(x) > 100` | `.loc[lambda d: d["x"] > 100]` after the aggregation |
| `JOIN` | `df.merge(other, on="key", how="inner")` |
| `UNION ALL` | `pd.concat([a, b])` |
| `DISTINCT` | `.drop_duplicates()` |
| `CASE WHEN` | `np.where(...)` / `np.select(...)` |

## `groupby`

Split, apply, combine:

```python
df = pd.read_csv("data/car_sales.csv", parse_dates=["Date"])

df.groupby("VehicleMake")["SalePrice"].mean()
df.groupby("VehicleMake")["SalePrice"].agg(["count", "mean", "median", "sum"])
df.groupby(["VehicleMake", "SaleType"])["SalePrice"].sum()      # several keys -> MultiIndex

# Named aggregations: the readable form, with the output column names you want
summary = df.groupby("DealershipLocation").agg(
    sales=("SalesID", "count"),
    revenue=("SalePrice", "sum"),
    avg_price=("SalePrice", "mean"),
    max_mileage=("VehicleMileage", "max"),
)

# A custom function per group
df.groupby("VehicleMake")["SalePrice"].agg(lambda s: s.quantile(0.9))
```

Things worth knowing:

```python
df.groupby("VehicleMake", dropna=False)      # include the NaN group (excluded by default!)
df.groupby("VehicleMake", observed=True)     # for category dtype: skip unused categories
df.groupby("VehicleMake", as_index=False)    # keep the key as a column instead of the index
```

The `dropna=False` default is a genuine footgun: rows whose group key is missing silently
disappear from your report.

### `transform` and `filter`

```python
# transform: one value per ROW, broadcast back - "the group mean next to each row"
df["make_avg"] = df.groupby("VehicleMake")["SalePrice"].transform("mean")
df["vs_avg"] = df["SalePrice"] - df["make_avg"]

# filter: keep whole groups matching a condition
big_makes = df.groupby("VehicleMake").filter(lambda g: len(g) > 100)

# rank within a group
df["rank_in_make"] = df.groupby("VehicleMake")["SalePrice"].rank(ascending=False)
```

`transform` is the one people do not discover on their own, and it replaces a merge-back in
nine cases out of ten.

## Joins: `merge`

```python
sales = pd.read_csv("data/car_sales.csv")
targets = pd.DataFrame({"DealershipLocation": ["New York", "San Diego"], "target": [1_000_000, 750_000]})

merged = sales.merge(targets, on="DealershipLocation", how="left")
```

`how=` takes `inner` (default), `left`, `right`, `outer` and `cross` — the same semantics as SQL.

```python
# Different column names on each side
a.merge(b, left_on="customer_id", right_on="id", how="inner")

# Join on the index
a.merge(b, left_index=True, right_index=True)
a.join(b)                                   # shorthand for an index join

# Suffixes when both sides have a column of the same name
a.merge(b, on="key", suffixes=("_left", "_right"))
```

### The check that saves your report

```python
merged = sales.merge(targets, on="DealershipLocation", how="left", validate="many_to_one")
```

`validate` raises if the relationship is not what you assumed (`one_to_one`, `one_to_many`,
`many_to_one`, `many_to_many`). A duplicated key on the "one" side silently multiplies your
rows and inflates every total — this is the most common way a junior produces a confidently
wrong number.

Also useful:

```python
merged = a.merge(b, on="key", how="left", indicator=True)
merged["_merge"].value_counts()      # both / left_only / right_only
```

Always compare `len(df)` before and after a merge.

## Concatenation

```python
pd.concat([jan, feb, mar])                            # stack rows
pd.concat([jan, feb], ignore_index=True)              # renumber the index
pd.concat([left, right], axis=1)                      # side by side, aligned on the index

# The real use case: 12 Excel files, one per industry
from pathlib import Path

frames = []
for path in sorted(Path("data/marketing_xlsx").glob("*.xlsx")):
    frame = pd.read_excel(path)
    frame["industry"] = path.stem.replace("Marketing_Expenditures_", "")
    frames.append(frame)

everything = pd.concat(frames, ignore_index=True)
```

Note the pattern: collect frames in a list, concatenate **once** at the end. Concatenating
inside the loop copies everything on every iteration.

## Wide and long: `pivot`, `melt`, `pivot_table`

**Tidy data** means: one row per observation, one column per variable. Most real exports are
*wide* — `country_indicators.csv` has one column per year — and most analysis wants *long*.

```python
wide = pd.read_csv("data/country_indicators.csv", sep=";", na_values=[".."])

long = wide.melt(
    id_vars=["Series Name", "Country Name", "Country Code"],
    value_vars=[c for c in wide.columns if c.startswith("2")],
    var_name="year",
    value_name="value",
)
long["year"] = long["year"].str[:4].astype(int)
```

Going the other way:

```python
back = long.pivot(index="Country Name", columns="year", values="value")
```

`pivot_table` is `pivot` plus aggregation — the Excel pivot table:

```python
table = df.pivot_table(
    index="VehicleMake",
    columns="SaleType",
    values="SalePrice",
    aggfunc="mean",
    margins=True,          # add the row/column totals
    fill_value=0,
)
```

`crosstab` is the frequency-counting shortcut:

```python
pd.crosstab(df["VehicleMake"], df["SaleType"])
pd.crosstab(df["VehicleMake"], df["SaleType"], normalize="index")     # row percentages
```

## MultiIndex, briefly

Grouping by several keys produces a hierarchical index:

```python
grouped = df.groupby(["VehicleMake", "SaleType"])["SalePrice"].sum()

grouped.loc["Audi"]
grouped.loc[("Audi", "New")]
grouped.unstack()              # move the innermost level into columns
grouped.reset_index()          # flatten back into a normal frame
```

Advice for the first year: **flatten early**. `reset_index()` after a groupby keeps your code
readable; keep the MultiIndex only when you are actively using it.

## Method chaining

```python
report = (
    pd.read_csv("data/car_sales.csv", parse_dates=["Date"])
    .rename(columns=str.lower)
    .query("saleprice > 0")
    .assign(
        year=lambda d: d["date"].dt.year,
        margin=lambda d: d["saleprice"] - d["downpayment"],
    )
    .groupby(["year", "vehiclemake"], as_index=False)
    .agg(sales=("salesid", "count"), revenue=("saleprice", "sum"))
    .sort_values("revenue", ascending=False)
    .head(20)
)
```

Chaining avoids a swarm of `df2`, `df3`, `df_final` variables and makes the pipeline read as a
sequence of steps. `assign` with a lambda is what lets you reference columns created earlier in
the same chain. Keep chains to a screenful; beyond that, extract named functions and use
`.pipe(func)`.

## Performance notes

```python
df.memory_usage(deep=True).sum() / 1e6        # MB
```

- Read only the columns you need (`usecols`), and only the rows you need (`nrows`, or filter early).
- Convert repeated text columns to `category`.
- Save intermediate results as Parquet, not CSV: it keeps dtypes, is compressed, and loads an
  order of magnitude faster.
- If a pandas job no longer fits in memory, the answer is usually chunking (`chunksize=`),
  Parquet + column selection, or moving the aggregation into the database — not a bigger machine.

## Check yourself

1. Which SQL clause does `transform` correspond to, and when do you use it?
2. What does `validate="many_to_one"` protect you from?
3. Why must you check row counts before and after a merge?
4. What is the difference between `pivot` and `pivot_table`?
5. What is wide vs long data, and which one do most analyses want?
6. Why is `pd.concat` inside a loop a bad idea?
