# Thirty non-Pythonic patterns and their fixes

These are the code-review comments a developer coming from another language collects in their
first month. Each entry: what gets written, what it should be, and why it matters.

## Iteration

**1. Index loops**

```python
for i in range(len(names)):        # no
    print(names[i])

for name in names:                 # yes
    print(name)
```

**2. Needing the index anyway**

```python
i = 0                              # no
for name in names:
    print(i, name)
    i += 1

for i, name in enumerate(names, start=1):    # yes
    print(i, name)
```

**3. Two lists in parallel**

```python
for i in range(len(names)):                  # no
    print(names[i], scores[i])

for name, score in zip(names, scores, strict=True):   # yes
    print(name, score)
```

**4. Iterating a dict by keys to get values**

```python
for key in mapping:                # no
    value = mapping[key]

for key, value in mapping.items(): # yes
    ...
```

**5. Building a list with append**

```python
result = []                        # no, when it is a simple map/filter
for x in values:
    if x > 0:
        result.append(x * 2)

result = [x * 2 for x in values if x > 0]     # yes
```

**6. A comprehension used for side effects**

```python
[print(x) for x in items]          # no - builds a list of None
for x in items:                    # yes
    print(x)
```

## Conditions

**7. Comparing to True/False**

```python
if is_valid == True:               # no
if is_valid:                       # yes
if is_valid is True:               # only when you really mean "the object True"
```

**8. Checking emptiness by length**

```python
if len(items) > 0:                 # no
if items:                          # yes
```

**9. `== None`**

```python
if value == None:                  # no
if value is None:                  # yes
```

**10. Chained range checks**

```python
if 0 <= i and i < len(xs):         # no
if 0 <= i < len(xs):               # yes
```

**11. Long `or` chains for membership**

```python
if c == "EUR" or c == "USD" or c == "GBP":    # no
if c in {"EUR", "USD", "GBP"}:                # yes - a set, O(1)
```

**12. if/elif ladder that is really a lookup**

```python
if kind == "csv":                  # no
    handler = read_csv
elif kind == "json":
    handler = read_json

HANDLERS = {"csv": read_csv, "json": read_json}       # yes
handler = HANDLERS[kind]
```

## Data access

**13. Checking a key before reading it**

```python
if "name" in data:                 # no
    name = data["name"]
else:
    name = "unknown"

name = data.get("name", "unknown") # yes
```

**14. Building a grouping dict by hand**

```python
groups = {}                        # no
for item in items:
    if item.city not in groups:
        groups[item.city] = []
    groups[item.city].append(item)

groups = defaultdict(list)         # yes
for item in items:
    groups[item.city].append(item)
```

**15. Counting by hand**

```python
counts = {}                        # no
for word in words:
    counts[word] = counts.get(word, 0) + 1

counts = Counter(words)            # yes
```

**16. Index-based tuple access**

```python
print(row[0], row[2])              # no - what is index 2?
name, _, city = row                # yes
# or better: a NamedTuple or dataclass
```

## Strings

**17. Concatenating in a loop**

```python
s = ""                             # no - O(n^2)
for line in lines:
    s += line

s = "".join(lines)                 # yes
```

**18. Old-style formatting in new code**

```python
"Hello, %s" % name                 # no
"Hello, {}".format(name)           # no
f"Hello, {name}"                   # yes
```

**19. f-strings in logging**

```python
logger.info(f"loaded {n} rows")    # no - formats even when the level is off
logger.info("loaded %s rows", n)   # yes
```

**20. Manual `strip` chains for whitespace**

```python
" ".join(text.split())             # yes - collapses any run of whitespace
```

## Files and resources

**21. Opening without closing**

```python
f = open("data.csv")               # no
data = f.read()

with open("data.csv", encoding="utf-8") as f:    # yes
    data = f.read()
```

**22. Leaving the encoding to the platform**

```python
open("data.csv")                   # no - cp1252 on Windows
open("data.csv", encoding="utf-8") # yes
```

**23. Building paths with string concatenation**

```python
path = folder + "/" + name         # no
path = Path(folder) / name         # yes
```

**24. Reading a whole file to count lines**

```python
lines = f.readlines()              # no - the whole file in memory
count = len(lines)

count = sum(1 for _ in f)          # yes
```

## Functions

**25. A mutable default argument**

```python
def add(item, target=[]):          # no - shared between calls
def add(item, target=None):        # yes
    if target is None:
        target = []
```

**26. Assigning a lambda to a name**

```python
double = lambda x: x * 2           # no
def double(x: int) -> int:         # yes
    return x * 2
```

**27. `map`/`filter` with a lambda**

```python
list(map(lambda x: x * 2, xs))     # no
[x * 2 for x in xs]                # yes
list(map(str.upper, names))        # acceptable: an existing named function
```

**28. Returning different types from different branches**

```python
def find(key):                     # no - callers cannot handle this
    if ...: return []
    if ...: return None
    return "error"

def find(key) -> list[Item]:       # yes - one type, raise for the error case
```

## Errors

**29. Bare or over-broad `except`**

```python
try:                               # no
    ...
except:
    pass

try:                               # yes
    value = int(text)
except ValueError:
    logger.warning("not a number: %r", text)
    return None
```

**30. Losing the original exception**

```python
except ValueError:                             # no
    raise RuntimeError("processing failed")

except ValueError as exc:                      # yes
    raise RuntimeError("processing failed") from exc
```

## Bonus: things that mark an experienced Python developer

```python
# Swap without a temporary
a, b = b, a

# Unpacking with a rest
first, *rest = items

# The walrus, where it removes a double computation
if (n := len(items)) > 10:
    print(f"too many: {n}")

# for...else instead of a found-flag
for item in items:
    if item.matches(query):
        break
else:
    raise LookupError("no match")

# Sorting by several keys, mixed directions
sorted(people, key=lambda p: (-p.score, p.name))

# Deduplicate, order preserved
list(dict.fromkeys(items))

# Transpose
rows = list(zip(*columns, strict=True))

# A context manager for a temporary state change
with suppress(FileNotFoundError):
    path.unlink()

# Generator pipeline: constant memory
total = sum(row.amount for row in parse(read_lines(path)))
```
