# 01 — NumPy

## Why it exists

A Python list of a million numbers is a million pointers to a million boxed `int` objects,
scattered across the heap. Every `+` goes through the interpreter, checks types and allocates a
result object.

A NumPy array is **one contiguous block of raw machine numbers**, and an operation on it runs in
a compiled C loop, with no interpreter and no per-element type checks.

```python
import numpy as np
import time

values = list(range(1_000_000))
array = np.arange(1_000_000)

start = time.perf_counter()
total = sum(x * 2 for x in values)
print(f"python: {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
total = (array * 2).sum()
print(f"numpy:  {time.perf_counter() - start:.3f}s")
```

Expect a 20–100× difference. This is the whole reason the scientific Python stack exists, and
why "Python is slow" is only half true: the language is slow, the arrays are not.

## Creating arrays

```python
import numpy as np

np.array([1, 2, 3])                  # from a list
np.array([[1, 2], [3, 4]])           # 2-dimensional
np.zeros(5)                          # [0. 0. 0. 0. 0.]
np.ones((2, 3))
np.full(3, 7)
np.arange(0, 10, 2)                  # [0 2 4 6 8]   like range(), but an array
np.linspace(0, 1, 5)                 # [0. 0.25 0.5 0.75 1. ]  n evenly spaced points
np.random.default_rng(42).normal(size=1000)      # the modern random API
```

## `dtype` and shape

Unlike a list, an array has **one** element type, fixed at creation:

```python
a = np.array([1, 2, 3])
a.dtype        # dtype('int64')
a.shape        # (3,)
a.ndim         # 1
a.size         # 3
a.nbytes       # 24

np.array([1, 2, 3], dtype=np.float32)
a.astype(np.float64)                  # conversion produces a new array
```

Common dtypes: `int8/16/32/64`, `uint8`, `float32/64`, `bool`, `datetime64[ns]`, and `object`
(a pointer per element — you have lost the performance benefit; avoid).

**Watch out for overflow:** unlike Python's `int`, a NumPy integer has a fixed width and wraps
around silently.

```python
np.array([2**62], dtype=np.int64) * 4      # negative result, no warning
```

## Vectorisation — do not write loops

```python
prices = np.array([100.0, 250.0, 75.0])
vat = 0.27

# NOT this
with_vat = np.array([p * (1 + vat) for p in prices])

# This
with_vat = prices * (1 + vat)

prices + prices        # element-wise
prices * prices
prices > 100           # array([False, True, False])  - a boolean array
np.sqrt(prices)
np.round(prices, 2)
```

Any time you find yourself writing a `for` loop over an array, stop and look for the vectorised
operation. Aside from speed, the vectorised version is usually shorter and clearer.

## Indexing, slicing, masking

```python
a = np.arange(10)

a[0], a[-1]
a[2:5]
a[::2]

m = np.array([[1, 2, 3], [4, 5, 6]])
m[0, 1]          # 2      - row, column in one bracket
m[:, 1]          # array([2, 5])  - the whole second column
m[1, :]          # array([4, 5, 6])
m.T              # transpose
m.reshape(3, 2)
```

Boolean masking is the idiom you will use constantly — and it is exactly how pandas filtering
works underneath:

```python
values = np.array([12, 45, 7, 88, 23])

mask = values > 20             # array([False, True, False, True, True])
values[mask]                   # array([45, 88, 23])
values[values > 20]            # the same, in one line
values[(values > 20) & (values < 50)]     # & and |, NOT and/or, and mind the parentheses
values[values > 20] = 0        # assignment through a mask
```

`and`/`or` do not work on arrays — they need a single truth value. Use `&`, `|`, `~`, and
parenthesise each comparison because `&` binds tighter than `>`.

**A slice is a view, not a copy:**

```python
a = np.arange(5)
b = a[1:3]
b[0] = 99
print(a)          # [ 0 99  2  3  4]  - the original changed
c = a[1:3].copy() # explicit copy when you need one
```

This is the opposite of list slicing, and it is deliberate: views make working with large
arrays cheap.

## Aggregation and axes

```python
m = np.array([[1, 2, 3], [4, 5, 6]])

m.sum()           # 21     everything
m.sum(axis=0)     # array([5, 7, 9])    down the rows -> one value per column
m.sum(axis=1)     # array([6, 15])      across the columns -> one value per row

m.mean(), m.std(), m.min(), m.max()
m.argmax()        # index of the maximum
np.median(m), np.percentile(m, 95)
```

`axis=0` means "collapse the rows", `axis=1` means "collapse the columns". Everyone gets this
backwards at first; the rule that helps is *"axis is the dimension that disappears"*.

## Broadcasting

Operations between differently shaped arrays work when the shapes are compatible: NumPy
virtually stretches the smaller one.

```python
prices = np.array([[100.0, 200.0],
                   [300.0, 400.0]])

prices * 1.27                     # scalar broadcast to every element

rates = np.array([1.0, 0.9])
prices * rates                    # (2,2) * (2,)  -> applied per column

column = np.array([[2.0], [3.0]])
prices * column                   # (2,2) * (2,1) -> applied per row
```

The rule: compare shapes from the right; dimensions must be equal, or one of them must be 1.
Broadcasting avoids building intermediate copies, which is why it matters for big data.

## Missing values

`np.nan` is a float, and it is **not equal to itself**:

```python
np.nan == np.nan          # False
np.isnan(values)          # the correct test

values = np.array([1.0, np.nan, 3.0])
values.sum()              # nan   - contamination spreads
np.nansum(values)         # 4.0   - nan-aware variants: nansum, nanmean, nanmax...
```

Note that `np.nan` only exists in float arrays; an integer array has no way to represent a
missing value. That constraint is why pandas historically upcast integer columns with missing
values to float.

## Where NumPy shows up in your life as a junior

You will mostly use pandas, which is built on NumPy — but these leak through constantly:

- `df["col"].values` gives you a NumPy array.
- The dtypes you see in pandas (`int64`, `float64`, `datetime64[ns]`) are NumPy's.
- `np.where(condition, a, b)` is the standard vectorised if/else in pandas code.
- Boolean masking is identical in both.

```python
import pandas as pd

df["category"] = np.where(df["amount"] > 1000, "large", "small")
df["score"] = np.select(
    [df["amount"] > 1000, df["amount"] > 100],
    ["large", "medium"],
    default="small",
)
```

## Check yourself

1. Why is a NumPy array faster than a list of numbers?
2. What happens if you put a string into an `int64` array?
3. Why do you write `&` instead of `and` when masking?
4. What does `axis=0` mean for `sum()`, and why is it confusing?
5. What is broadcasting, and when does it apply?
6. Why is `values == np.nan` always False?
