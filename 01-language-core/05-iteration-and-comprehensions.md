# 05 — Iteration, comprehensions, generators

Iteration is the single most Python-specific piece of the language. Streams in Java and LINQ in
C# cover similar ground, but here it is built into the core rather than bolted on as a library.

## The iterator protocol

Two protocols, easy to confuse:

- **iterable**: an object that can produce an iterator. It implements `__iter__`.
- **iterator**: the object that actually walks the sequence. It implements `__next__`
  (and `__iter__` returning itself).

```python
items = [1, 2, 3]          # iterable
it = iter(items)           # iterator
next(it)                   # 1
next(it)                   # 2
next(it)                   # 3
next(it)                   # StopIteration
```

A `for` loop is exactly this, with the `StopIteration` handled for you:

```python
for x in items: ...

# is roughly
it = iter(items)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    ...
```

Consequences that matter:

- **An iterator is consumed.** Once exhausted, it yields nothing. This is why looping twice over
  a `zip`, a `map` or a generator silently produces nothing the second time.
- **A list is not an iterator**, it is an iterable — you can loop over it many times.
- Anything implementing `__iter__` works with `for`, `in`, unpacking, `sum`, `sorted`, `list()`
  and the rest. That is duck typing in action.

## Comprehensions

A comprehension builds a collection from an iterable. It is not merely a shorter loop: it is
an expression, so it can be passed, returned or nested.

```python
# list
squares = [x * x for x in range(10)]
evens = [x for x in numbers if x % 2 == 0]
names = [user.name.upper() for user in users if user.is_active]

# dict
by_id = {user.id: user for user in users}
inverted = {value: key for key, value in mapping.items()}

# set
domains = {email.split("@")[1] for email in emails}

# nested loops: read left to right, exactly as the equivalent for statements nest
pairs = [(x, y) for x in range(3) for y in range(3) if x != y]

# nested data
flat = [item for row in matrix for item in row]
```

The general shape:

```
[ expression  for item in iterable  if condition ]
```

A conditional *expression* goes before the `for`, which is a different thing:

```python
labels = ["even" if x % 2 == 0 else "odd" for x in numbers]
```

### When NOT to use a comprehension

```python
# Unreadable - three levels and a side effect. Write a loop.
result = [transform(x) for sub in data for x in sub if check(x) and x.value > threshold]

# A comprehension for its side effect only - wrong tool, it builds a list of Nones
[print(x) for x in items]      # use a plain for loop
```

The rule of thumb: if it does not fit on one line comfortably, or it does more than
map/filter, write the loop.

## Generator expressions

Swap the brackets for parentheses and nothing is materialised in memory:

```python
total = sum(x * x for x in range(1_000_000))     # constant memory
any(line.startswith("ERROR") for line in log)     # stops at the first match
max((p.price for p in products), default=0)
```

The difference:

```python
[x * x for x in range(10_000_000)]     # ~400 MB list, built immediately
(x * x for x in range(10_000_000))     # a generator object, a few hundred bytes
```

Use a generator expression when you consume the values once — feeding an aggregate, a `for`
loop, or another pipeline stage. Use a list comprehension when you need the result more than
once, need its length, or need indexing.

## Generator functions

Any function containing `yield` becomes a generator function: calling it does not run the body,
it returns a generator. The body runs up to the first `yield` on the first `next()` call, and
**suspends there**, keeping its local state.

```python
def read_records(path: str):
    """Yields one record per line - never holds the whole file in memory."""
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            yield line_no, line.split(";")


for line_no, fields in read_records("data.csv"):
    ...
```

This is the standard shape of Python data processing: **a chain of generators**, each doing one
transformation, with nothing but one record in memory at a time.

```python
def parse(rows):
    for row in rows:
        yield {"name": row[0], "amount": float(row[1])}

def only_large(records, threshold=1000):
    for record in records:
        if record["amount"] >= threshold:
            yield record

rows = read_records("transactions.csv")
records = parse(r for _, r in rows)
big = only_large(records)

for record in big:        # nothing has been read from disk until this line
    print(record)
```

Note that last point — generators are **lazy**. No work happens until something consumes them.
This is also the number one source of confusion: an exception inside a generator surfaces where
it is *consumed*, not where it was created.

### `yield from`

Delegating to another iterable:

```python
def walk(node):
    yield node.value
    for child in node.children:
        yield from walk(child)        # instead of: for v in walk(child): yield v
```

## `itertools` — the standard library of iteration

```python
from itertools import chain, islice, groupby, count, cycle, repeat, product, combinations

chain([1, 2], [3, 4])                 # 1, 2, 3, 4 - concatenate lazily
islice(generator, 10)                 # first 10 elements, "slicing" for iterators
islice(generator, 100, 200)
count(1)                              # 1, 2, 3, ... infinite
product("AB", repeat=2)               # AA, AB, BA, BB
combinations([1, 2, 3], 2)            # (1,2), (1,3), (2,3)
pairwise([1, 2, 3])                   # (1,2), (2,3)   (3.10+)

# groupby needs the input SORTED by the same key - a classic trap
from operator import attrgetter
for city, group in groupby(sorted(people, key=attrgetter("city")), key=attrgetter("city")):
    print(city, len(list(group)))
```

For the grouping job, `collections.defaultdict` is usually clearer than `itertools.groupby`.

## The built-ins that consume iterables

```python
sum(xs), min(xs), max(xs), len(xs)
any(x > 0 for x in xs)        # short-circuits
all(x > 0 for x in xs)
sorted(xs, key=..., reverse=...)
reversed(xs)
enumerate(xs, start=0)
zip(xs, ys, strict=True)
list(xs), tuple(xs), set(xs), dict(pairs)
```

`map` and `filter` exist, but a comprehension is usually more readable:

```python
list(map(str.upper, names))              # acceptable with an existing function
[name.upper() for name in names]         # preferred
list(filter(lambda x: x > 0, numbers))   # avoid
[x for x in numbers if x > 0]            # preferred
```

## Check yourself

1. What is the difference between an iterable and an iterator?
2. Why does looping a second time over the result of `zip()` produce nothing?
3. When do you use a generator expression instead of a list comprehension?
4. What happens when you *call* a function containing `yield`?
5. Why does `itertools.groupby` need sorted input?
6. Rewrite `list(filter(lambda x: x.active, users))` as a comprehension.
