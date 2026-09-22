# 03 — The data toolkit

Almost every Python job touches data: an import job, a report, an analysis, a monitoring
dashboard. This module covers the stack that does it — plus the HTTP client you need to fetch
the data in the first place.

| Chapter | Topic |
|---|---|
| [01](01-numpy.md) | NumPy: arrays, dtypes, vectorisation, broadcasting — and why it is fast |
| [02](02-pandas-fundamentals.md) | Series, DataFrame, the index, selection, filtering |
| [03](03-cleaning-and-types.md) | Missing data, dtypes, dates, strings, duplicates — real, messy files |
| [04](04-groupby-join-reshape.md) | `groupby`/`agg`, `merge`, `pivot`/`melt`, tidy data, method chaining |
| [05](05-visualisation.md) | matplotlib and seaborn: the figure/axes model, choosing a chart |
| [06](06-http-and-apis.md) | `requests`, REST, JSON, errors, retries, pagination, secrets |
| [exercises/](exercises/) | Exercises on the real datasets in `data/` |

## Why these libraries

- **NumPy** is the foundation: a contiguous, typed array plus operations implemented in C.
  Everything else in the numeric stack is built on it.
- **pandas** is the tabular layer: labelled columns, mixed dtypes, joins, grouping, I/O for
  CSV/Excel/SQL/Parquet. It is the SQL of in-memory data.
- **matplotlib** is the plotting engine; **seaborn** is a thin, opinionated layer on top that
  makes statistical charts one-liners.
- **requests** is the HTTP client everyone uses. (`httpx` is the modern alternative with the
  same API plus async support.)

```bash
python -m pip install pandas numpy matplotlib seaborn requests openpyxl pyarrow
```

## The datasets

Everything in this module works on the files in [`../data/`](../data/), which come from the
earlier version of this course. They are real, and several of them are genuinely messy — which
is the point.

| File | Rows | What makes it interesting |
|---|---|---|
| `transactions.csv` | 1,000 | missing values, several currencies, timestamps |
| `car_sales.csv` | 5,000 | wide, mixed types, good for grouping and joins |
| `tips.csv` | 244 | the classic teaching dataset for visualisation |
| `dogs_database.csv` | 500 | categorical data, a BOM in the header |
| `country_indicators.csv` | 10,855 | semicolon-separated, wide year columns, `..` for missing |
| `EUR_HUF_history.csv` | 129 | dates like `5/31/2024 Friday` — a parsing exercise |
| `inflation_eu.csv` | 347 | horrifying column names, one column per country |
| `GDP_eu.csv` | 299 | quarterly time series, mostly empty early years |
| `marketing_xlsx/` | 12 files | Excel, one file per industry — concatenation practice |

## By the end of this module

- You know when a loop over a DataFrame is the wrong answer (almost always) and what replaces it.
- You can load a messy CSV, fix the dtypes, handle missing values and explain what you did.
- You can answer business questions with `groupby`, `merge` and `pivot_table`.
- You can produce a readable chart, and you can say why you chose that chart.
- You can consume a paginated REST API with error handling, retries and no secrets in the code.
