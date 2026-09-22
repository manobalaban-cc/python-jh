# Project 2 — Sales report pipeline

**pandas, matplotlib/seaborn.** A repeatable pipeline that turns raw exports into a report a
manager could actually read.

## The story

Marketing sends you a folder of Excel files, one per industry, every quarter. Sales sends a CSV
export from the dealership system. Today someone spends a day in Excel building the same report
each time, and the numbers never quite match between quarters. Your job: one command, same
report, every time.

## The inputs

All in [`../../data/`](../../data/):

| File | What it is |
|---|---|
| `car_sales.csv` | 5,000 vehicle sales: date, customer, vehicle, price, financing, dealership |
| `marketing_xlsx/*.xlsx` | 12 Excel files, one per industry, marketing spend over 10 years |
| `country_indicators.csv` | World Bank indicators, wide format, `..` for missing (optional context) |

## What to build

```bash
salesreport build --sales data/car_sales.csv --marketing data/marketing_xlsx --out reports/2024-Q2
```

Produces, in the output folder:

```
reports/2024-Q2/
├── summary.md          the written report
├── summary.json        the same numbers, machine-readable
├── by_make.csv         the aggregated table
├── revenue_by_month.png
├── price_by_type.png
└── top_dealerships.png
```

## Required analysis

### Sales

1. Total revenue, transaction count, average and median sale price, for the whole period.
2. Revenue by month (a time series) with the month-over-month change.
3. Per make: count, revenue, average price, average mileage. Sorted by revenue.
4. New vs used: how much cheaper is a used car, per make and overall? Express it as a percentage.
5. Per dealership: revenue, count, average price, and the share of sales with financing approved.
6. Does mileage predict price? Report the correlation and say honestly what it does and does not
   mean.
7. The top 10 salespeople by revenue, with their number of sales.

### Marketing

8. Load and concatenate the twelve Excel files; the industry comes from the file name.
9. Total spend per industry and per year.
10. Year-over-year growth per industry; which industries grew or shrank most?

### Quality gates in the pipeline itself

11. Report how many rows were loaded, how many were dropped, and why.
12. Assert that revenue is non-negative, that ids are unique, and that dates fall in the expected
    range. A failed assertion must produce a clear message, not a traceback in the middle of a chart.

## Charts

Three charts, saved as PNG, each one answering a question stated in its title:

- revenue by month (line),
- sale price distribution by vehicle type (box plot),
- top 10 dealerships by revenue (horizontal bar, sorted).

Every chart: title stating the finding, labelled axes with units, readable numbers, no
chart junk. Re-read [03-data-toolkit/05](../../03-data-toolkit/05-visualisation.md) before you
start — form first, colour last.

## Requirements

1. **A script, not a notebook.** `src/salesreport/`, entry point, `argparse`.
2. **Separate the stages**: `load.py` (I/O and cleaning), `analysis.py` (pure functions on
   DataFrames), `render.py` (charts and text), `__main__.py` (wiring).
3. **No row loops.** No `iterrows`, no `apply(axis=1)` unless you can justify it in the README.
4. **Every analysis function is pure**: DataFrame in, DataFrame or scalar out, no printing, no
   file writing. That is what makes them testable.
5. **Tests**: at least six, using small hand-built DataFrames, covering the aggregations and the
   edge cases (empty input, a make with one sale, missing prices).
6. **Reproducible**: running it twice on the same input produces byte-identical CSV and JSON.
7. `mypy` (with `ignore_missing_imports` for pandas if you skip `pandas-stubs`) and `ruff` clean.

## Suggested structure

```
sales-report/
├── pyproject.toml
├── README.md
├── src/salesreport/
│   ├── __main__.py
│   ├── load.py          read_sales(), read_marketing(), validate()
│   ├── analysis.py      revenue_by_month(), by_make(), new_vs_used(), ...
│   ├── render.py        charts and the markdown report
│   └── models.py        a frozen dataclass for the report's numbers
└── tests/
    ├── test_load.py
    └── test_analysis.py
```

## Hints

- Build a small DataFrame **in the test file** rather than reading the real CSV: three rows you
  fully control beat 5,000 rows you do not.
- `pd.testing.assert_frame_equal` compares frames with tolerances and a readable diff.
- Concatenating the Excel files: collect into a list, `pd.concat` once. `Path.stem` gives you the
  industry name.
- `transform("mean")` gives you the per-group average alongside each row — useful for
  "compared to the average for this make".
- A markdown report is a list of strings joined at the end, or an f-string template. Keep the
  formatting out of the analysis functions.
- For the new-vs-used comparison, watch out for makes that only have one of the two.

## Acceptance criteria

- [ ] One command produces the whole output folder from a clean checkout
- [ ] `summary.md` is readable by a non-technical person and states every number with its unit
- [ ] `summary.json` parses and contains the same numbers as the markdown
- [ ] Running it twice produces identical CSV/JSON output
- [ ] Charts have titles that state a finding, labelled axes, and sorted categories
- [ ] Tests pass, no row loops anywhere, `ruff` and `mypy` clean
- [ ] The README states every cleaning decision you made and how many rows each one dropped

## Stretch

1. `--compare reports/2024-Q1` — add a column of change versus the previous report.
2. `--format html` using `df.to_html()` or Jinja2, with the charts embedded.
3. Cache the parsed input as Parquet and measure the speed difference against re-reading Excel.
4. Add the World Bank data and check whether marketing spend correlates with GDP growth — then
   write one honest paragraph about why a correlation there would not prove anything.
