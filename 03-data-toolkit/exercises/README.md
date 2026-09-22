# Exercises — the data toolkit

Two parts: a set of `pytest`-verified pandas functions, and an open-ended analysis you present
to the group.

```bash
cd 03-data-toolkit/exercises
python -m pip install pandas numpy matplotlib seaborn pytest openpyxl
python -m pytest -v
```

## Part 1 — `tasks/task_pandas.py`

Eleven functions, from loading and cleaning through grouping, joining and reshaping. The tests
run against the **real files** in [`../../data/`](../../data/), so the expected numbers are real:
`transactions.csv` really does have 9 unusable rows out of 1000, and Chicago really is the
top dealership by revenue.

Reference solution: `solutions/task_pandas.py`.

Rules:

- no `iterrows`, no `apply(axis=1)` — if you reach for a row loop, you are missing a vectorised tool;
- never mutate the DataFrame you were handed;
- the functions must be pure: same input, same output, no printing.

## Part 2 — a small analysis you present

Pick **one** dataset and answer three questions with it. Deliverable: one `.py` script that
produces a short printed summary and saves two charts as PNG files.

| Dataset | Suggested questions |
|---|---|
| `car_sales.csv` | Do used cars really sell for less, and by how much per make? Which dealership has the best average margin? Does mileage predict price? |
| `tips.csv` | Does tipping percentage depend on the day, the party size or the time of day? |
| `dogs_database.csv` | Which breeds are heaviest for their height? How does age relate to size? |
| `EUR_HUF_history.csv` | What was the trend and the volatility? Show a 7-day moving average. |
| `country_indicators.csv` | Which countries grew fastest between 2000 and 2015? Reshape to long first. |
| `marketing_xlsx/` | Which industry spends most? Concatenate the twelve Excel files first. |

Requirements:

1. A `main()` function and a `if __name__ == "__main__":` guard — a script, not a notebook.
2. Loading and cleaning in a separate function from the analysis.
3. Every question answered with a number *and* a sentence of interpretation.
4. Two charts, saved to disk, with titles, axis labels and units.
5. State explicitly how many rows you dropped while cleaning, and why.

Assessment focuses on: correct handling of missing data, no row loops, readable chained
transformations, and whether the charts answer the question asked.

## Part 3 (stretch) — from an API

Fetch something live and analyse it: the exchange-rate API of the Hungarian National Bank, the
European Central Bank, the World Bank, or any public JSON API you like. Requirements: a timeout,
`raise_for_status()`, no key in the source, and `pd.json_normalize` from JSON to DataFrame.
