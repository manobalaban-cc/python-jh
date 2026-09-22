# 05 — Visualisation with matplotlib and seaborn

A chart is read by a person. Most of this chapter is mechanics, but start with the part that
decides whether the chart is any good: **choosing the form**.

## Choose the form before you write any code

Ask what job the numbers have to do:

| The data's job | Use |
|---|---|
| Compare magnitudes across categories | horizontal bar chart (sorted!) |
| Show change over time | line chart |
| Show a distribution | histogram, KDE, box or violin plot |
| Show a relationship between two numbers | scatter plot (add a trend line if it means something) |
| Show composition | stacked bar — and only if the parts sum to a meaningful whole |
| Show one number that matters | **no chart** — print the number, large |
| Show a table of numbers people will look up | **no chart** — a table |

Rules that hold regardless of library:

- **Never use two y-axes.** Two measures at different scales belong in two charts, or indexed
  to a common base. A dual-axis chart lets you "prove" any correlation by rescaling.
- **Sort bars by value**, not alphabetically, unless the category order is meaningful (months).
- **Start bar charts at zero.** Truncating the axis exaggerates differences.
- **Avoid pie charts** beyond two or three slices; people cannot compare angles.
- **Colour encodes identity or magnitude, never rank.** If a filter changes which series are
  shown, the surviving series must keep their colours.
- **One hue, light to dark, for magnitude**; two hues with a neutral middle for
  positive/negative; a fixed categorical order for identity. Never a rainbow ramp.
- Label directly where you can; a legend is required as soon as there are two or more series,
  so identity is never carried by colour alone.

## matplotlib: figure and axes

Everything else in Python plotting is built on matplotlib, so learn its object model rather
than the `plt.plot()` global interface.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))     # Figure = the canvas, Axes = one plot on it

ax.plot(df["date"], df["rate"], linewidth=2, label="EUR/HUF")
ax.set_title("EUR/HUF exchange rate, 2024")
ax.set_xlabel("date")
ax.set_ylabel("rate")
ax.legend()
ax.grid(True, alpha=0.3)                    # recessive grid, never dominant

fig.tight_layout()
fig.savefig("eur_huf.png", dpi=150, bbox_inches="tight")
plt.close(fig)                              # free the memory in a script or a loop
```

- `Figure` is the whole image; `Axes` is one coordinate system inside it. One figure can hold
  many axes.
- `plt.something()` acts on "the current axes" — fine in an interactive session, a source of
  confusion in a script. Use the `fig, ax` form.
- In a script, **save** rather than `plt.show()`; `show()` blocks.

Several panels:

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
axes[0, 0].hist(df["SalePrice"], bins=30)
axes[0, 1].scatter(df["VehicleMileage"], df["SalePrice"], s=8, alpha=0.4)
```

Small multiples — the same chart repeated per category, with shared axes — are almost always
better than one crowded chart with eight series.

## seaborn: statistical charts in one line

seaborn sits on matplotlib, understands DataFrames, and does the aggregation for you.

```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid", palette="colorblind")     # colorblind-safe by default
```

```python
tips = pd.read_csv("data/tips.csv")

# Distribution
sns.histplot(data=tips, x="total_bill", bins=30, kde=True)

# Category comparison - note the horizontal orientation for long labels
sns.barplot(data=tips, y="day", x="total_bill", estimator="mean", errorbar=None)

# Distribution per category
sns.boxplot(data=tips, x="day", y="total_bill")
sns.violinplot(data=tips, x="day", y="total_bill", inner="quartile")

# Relationship
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time", size="size", alpha=0.7)
sns.regplot(data=tips, x="total_bill", y="tip")            # with a fitted line

# Counts
sns.countplot(data=tips, y="day", order=tips["day"].value_counts().index)

# Correlation heat map - diverging palette centred on zero
corr = tips[["total_bill", "tip", "size"]].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, vmin=-1, vmax=1)
```

Figure-level functions create their own figure and can facet:

```python
sns.relplot(data=tips, x="total_bill", y="tip", col="time", row="smoker", kind="scatter")
sns.catplot(data=tips, x="day", y="total_bill", kind="box", col="time")
sns.lmplot(data=tips, x="total_bill", y="tip", hue="smoker")
```

Axes-level functions (`histplot`, `boxplot`, …) draw into an existing `ax`, which is what you
want when composing a multi-panel figure:

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=tips, x="day", y="total_bill", ax=ax)
ax.set_title("Bill distribution by day")
```

## pandas' own `.plot()`

For a quick look during exploration, a DataFrame plots itself (through matplotlib):

```python
df.groupby("VehicleMake")["SalePrice"].mean().sort_values().plot.barh(figsize=(8, 6))
df.set_index("Date")["SalePrice"].resample("ME").sum().plot(title="Monthly revenue")
df["SalePrice"].plot.hist(bins=40)
```

This is for *you*, while exploring. Anything another human will see deserves explicit titles,
axis labels and units.

## Making a chart presentable

```python
fig, ax = plt.subplots(figsize=(10, 6))

data = (
    df.groupby("VehicleMake", as_index=False)["SalePrice"]
    .mean()
    .sort_values("SalePrice")
)

ax.barh(data["VehicleMake"], data["SalePrice"], color="#4C78A8")
ax.set_title("Average sale price by make", fontsize=14, pad=12)
ax.set_xlabel("average price (USD)")
ax.set_ylabel("")                                  # the categories label themselves
ax.xaxis.set_major_formatter(lambda x, _: f"{x:,.0f}")
ax.spines[["top", "right"]].set_visible(False)     # remove chart junk
ax.grid(axis="x", alpha=0.3)
ax.set_axisbelow(True)                             # grid behind the bars

for y, value in enumerate(data["SalePrice"]):      # direct labels beat a busy axis
    ax.text(value + 200, y, f"{value:,.0f}", va="center", fontsize=9)

fig.tight_layout()
fig.savefig("avg_price_by_make.png", dpi=150)
```

The checklist before you hand a chart over:

- [ ] Title says the **finding**, not the mechanism ("Used cars sell for 32% less", not "Price by type")
- [ ] Axes labelled, with units
- [ ] Numbers formatted for humans (`1,234` not `1234.0`; percentages as percentages)
- [ ] Bars sorted, axis starting at zero
- [ ] No unexplained colours; a legend as soon as there are two series
- [ ] Readable at the size it will actually be viewed
- [ ] You looked at the rendered image, not just the code

## Where to go beyond

| Library | Use it for |
|---|---|
| matplotlib | full control, publication output, anything embedded |
| seaborn | statistical charts, fast exploration |
| plotly | interactive charts (hover, zoom) for notebooks and web pages |
| altair | declarative, grammar-of-graphics style |
| Great Tables / `df.style` | formatted tables, which are often the right answer |

## Check yourself

1. What is the difference between a Figure and an Axes?
2. Why avoid the `plt.`-global interface in a script?
3. Why is a dual-axis chart a bad idea?
4. When is the right chart no chart at all?
5. What is the difference between a figure-level and an axes-level seaborn function?
6. Name three things that make a chart presentable that have nothing to do with the data.
