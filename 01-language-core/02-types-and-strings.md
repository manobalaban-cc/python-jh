# 02 — Built-in types, strings, conversions

## Numbers

### `int` — arbitrary precision

```python
big = 2 ** 1000
print(big)                # prints all 302 digits
print(big.bit_length())   # 1001
```

There is no `int` / `long` distinction, no overflow, no `Integer.MAX_VALUE`. A Python integer
grows as large as memory allows. The price is speed — which NumPy later solves with
fixed-width types.

Division is an easy place to slip:

```python
7 / 2        # 3.5   true division, ALWAYS returns a float (Java would give 3!)
7 // 2       # 3     floor division
-7 // 2      # -4    rounds towards minus infinity, not towards zero (Java: -3)
7 % 2        # 1
-7 % 2       # 1     the result takes the divisor's sign (Java: -1)
divmod(7, 2) # (3, 1)
```

`//` and `%` behave **differently from Java and C** for negative operands. If you write modulo
arithmetic over possibly negative input, write a test for it.

### `float` — IEEE 754 double

The usual traps apply:

```python
0.1 + 0.2 == 0.3          # False
0.1 + 0.2                 # 0.30000000000000004

import math
math.isclose(0.1 + 0.2, 0.3)      # True  <- compare floats like this
```

**Never use `float` for money.** Use this instead:

```python
from decimal import Decimal

price = Decimal("19.99")       # from a string! Decimal(19.99) already carries the error
vat = Decimal("0.27")
print(price * (1 + vat))       # 25.3873
```

The `decimal` module gives decimal-based arithmetic with configurable precision (Java's
`BigDecimal`). For exact ratios there is `fractions.Fraction`.

### `bool`

`bool` is **a subclass of `int`**, so:

```python
True + True               # 2
isinstance(True, int)     # True
sum([True, False, True])  # 2   <- frequently used for counting
```

## `None`

Python's `null`, with one important difference: `None` is an **object**, the single instance of
`NoneType`. There is no null pointer and no primitive/object split.

```python
result = None
if result is None:      # always is / is not, never ==
    ...
```

A function that returns nothing actually returns `None`:

```python
def f():
    pass

print(f())      # None
```

Which produces a classic bug:

```python
items = [3, 1, 2]
ordered = items.sort()      # BUG: sort() sorts in place and returns None
print(ordered)              # None

ordered = sorted(items)     # correct: returns a new list
```

**A convention worth memorising:** things that mutate in place return `None`
(`list.sort`, `list.append`, `dict.update`); things that build something new return it
(`sorted`, `str.upper`, `list.copy`).

## Strings

`str` is **immutable** and holds a sequence of Unicode code points.

```python
s = "Grüße"
len(s)            # 5  <- characters, not bytes!
s[0]              # 'G'
s[-1]             # 'e'
s[1:4]            # 'rüß'
s[::-1]           # reversed
"üß" in s         # True
```

There is no separate character type: `s[0]` is a string of length one.

### `str` vs `bytes`

```python
text = "Grüße"
data = text.encode("utf-8")      # b'Gr\xc3\xbc\xc3\x9fe'  <- bytes
back = data.decode("utf-8")      # 'Grüße'                 <- str
len(text)   # 5 characters
len(data)   # 7 bytes
```

The distinction is critical for file and network I/O. When opening files, **always pass an
encoding**, because the default is platform-dependent:

```python
open("data.csv", encoding="utf-8")       # do this
open("data.csv")                          # not this - Windows may use cp1252
```

### Formatting: f-strings

```python
name = "Anna"
amount = 1234.5678

f"Hello, {name}!"                # 'Hello, Anna!'
f"{amount:.2f}"                  # '1234.57'          two decimals
f"{amount:10.2f}"                # '   1234.57'       width 10, right-aligned
f"{amount:<10.2f}|"              # '1234.57   |'      left-aligned
f"{amount:,.2f}"                 # '1,234.57'         thousands separator
f"{0.8734:.1%}"                  # '87.3%'
f"{255:#x}"                      # '0xff'
f"{name!r}"                      # "'Anna'"           repr() form
f"{amount=}"                     # 'amount=1234.5678' for debugging
```

Any expression can go inside, not just a name:

```python
f"{len(name)} letters, {'large' if amount > 1000 else 'small'} amount"
```

Older code still uses `"{}".format(...)` and `"%s" % ...`. Write f-strings in new code — with
one exception: **not in logging calls**.

```python
logging.info("Processed %s rows", n)     # good: formats only if the record is emitted
logging.info(f"Processed {n} rows")      # bad: formats always, even when the level is off
```

### The string methods you will actually use

```python
s = "  Anna Nagy;12;Budapest  "

s.strip()                      # trims whitespace on both ends
s.strip().split(";")           # ['Anna Nagy', '12', 'Budapest']
";".join(["a", "b", "c"])      # 'a;b;c'
s.replace(";", ",")
s.lower(), s.upper(), s.title()
s.startswith("  Anna"), s.endswith("  ")
"12".isdigit(), "abc".isalpha()
s.find("Anna")                 # index or -1
s.index("Anna")                # index or ValueError
"a-b-c".split("-", maxsplit=1) # ['a', 'b-c']
"line1\nline2".splitlines()    # ['line1', 'line2']
s.removeprefix("  Anna ")      # 3.9+
```

### Building strings in a loop

```python
# BAD - a new string object on every iteration, O(n^2)
result = ""
for line in lines:
    result += line + "\n"

# GOOD - O(n)
result = "\n".join(lines)

# When the logic is more involved:
parts: list[str] = []
for line in lines:
    parts.append(transform(line))
result = "".join(parts)
```

### Multi-line and raw strings

```python
text = """First line
Second line"""

path = r"C:\Users\Anna\data.csv"     # raw: \U is not an escape sequence here
pattern = r"\d{4}-\d{2}-\d{2}"       # ALWAYS use r-strings for regular expressions
```

## Conversions

```python
int("42")           # 42
int("42.5")         # ValueError! go through float first
int(float("42.5"))  # 42  (truncates, does not round)
int("ff", 16)       # 255
float("3.14")
str(42)
list("abc")         # ['a', 'b', 'c']
tuple([1, 2])
set([1, 1, 2])      # {1, 2}
dict([("a", 1)])    # {'a': 1}
bool("")            # False
```

Conversion with error handling, the Python way:

```python
def safe_int(text: str, default: int = 0) -> int:
    try:
        return int(text)
    except ValueError:
        return default
```

## Truthiness — what counts as false

Any object can be evaluated in a boolean context. The **falsy** values are:

```python
False, None, 0, 0.0, 0j, Decimal(0), "", [], (), {}, set(), range(0)
```

Everything else is truthy — including the string `"False"` and the list `[0]`.

```python
if items:              # idiomatic: "if not empty"
if len(items) > 0:     # works, but noisy

if text:               # "if non-empty string"
if text is not None:   # this means something DIFFERENT: an empty string passes
```

**Common bug:** when `0` is a valid value, truthiness is the wrong test.

```python
def configure(value: int | None = None) -> int:
    if not value:        # WRONG: overrides a legitimate 0 as well
        return 10
    return value

def configure(value: int | None = None) -> int:
    if value is None:    # correct
        return 10
    return value
```

## Check yourself

1. What is `-7 // 2` and why is it not `-3`?
2. Why do we not use `float` for financial calculations, and what replaces it?
3. What is the difference between `list.sort()` and `sorted()`?
4. How do `str` and `bytes` relate? When do you need which?
5. Why should you not use an f-string in a `logging` call?
6. Why is `if not value:` wrong when `0` is a legitimate input?
