# Datasets

Every dataset used by the exercises and projects. They come from the earlier version of this
course; several of them are genuinely messy, which is why they were kept.

| File | Rows | Format notes |
|---|---|---|
| `transactions.csv` | 1,000 | `Timestamp,Amount,Currency,Recipient`. 9 rows have a missing field. Currencies: EUR, USD, GBP, JPY, CAD. Timestamps are ISO with microseconds. |
| `car_sales.csv` | 5,000 | 20 columns: vehicle, customer, price, financing, dealership, salesperson. `Date` is ISO. Synthetic but internally consistent. |
| `tips.csv` | 244 | The classic restaurant-tips dataset. Quoted strings, numeric bill and tip. |
| `dogs_database.csv` | 500 | **Has a UTF-8 BOM** — open with `encoding="utf-8-sig"`. Columns include `Height (cm)` and `Weight (kg)`. |
| `dogs_database.xlsx` | 500 | The same data as Excel. |
| `traffic.csv` | 3 | Tiny; page views per day. Good for a first pivot/melt. |
| `student_data.csv` | 6 | Tiny; long format (Student, Subject, Grade). Good for a first `pivot`. |
| `country_indicators.csv` | 10,855 | World Bank export. **Semicolon-separated**, wide (one column per year, named `2000 [YR2000]`), `..` means missing. |
| `GDP_eu.csv` | 299 | Quarterly euro-area GDP, one column per country, many empty early years. |
| `inflation_eu.csv` | 347 | HICP per country. **Terrible column names** with embedded quotes and series codes — a renaming exercise. |
| `inflation_HU.csv` | ~60 | Hungarian statistical office (KSH) export: **cp1250 encoding**, semicolon-separated, **decimal comma**, a title row above the header, Hungarian column names. The single best encoding-and-locale exercise in the folder. |
| `EUR_HUF_history.csv` | 129 | `Date` looks like `5/31/2024 Friday` — split before parsing. |
| `marketing_xlsx/*.xlsx` | 12 files × ~69 rows | One file per industry. Columns: `Company`, then one column per year 2014–2023. The industry is only in the file name. |
| `generate_transactions.py`, `generate_car_sales.py` | — | The generators for the two synthetic datasets, if you want more rows or a different seed. |

## Suggested first commands

```python
import pandas as pd

pd.read_csv("data/transactions.csv", parse_dates=["Timestamp"])
pd.read_csv("data/car_sales.csv", parse_dates=["Date"])
pd.read_csv("data/dogs_database.csv", encoding="utf-8-sig")
pd.read_csv("data/country_indicators.csv", sep=";", na_values=[".."])
pd.read_excel("data/marketing_xlsx/Marketing_Expenditures_Retail.xlsx")
```

## A note on provenance

`transactions.csv`, `car_sales.csv`, `dogs_database.csv` and the marketing workbooks are
generated, not real customer data — but they were generated to look like the real thing,
missing values and all. The World Bank, Eurostat and ECB extracts are genuine public data as
exported by those services, which is exactly why their formats are so awkward.
