# 04 — Built-in collections

Four built-in containers cover most of what `java.util` gives you. Choosing the right one is a
question you will be asked at interview and in code review alike.

| Type | Ordered | Mutable | Duplicates | Lookup cost | Java analogy |
|---|---|---|---|---|---|
| `list` | yes | yes | yes | `O(n)` by value, `O(1)` by index | `ArrayList` |
| `tuple` | yes | **no** | yes | `O(n)` | immutable array / record |
| `dict` | insertion order | yes | keys unique | `O(1)` | `LinkedHashMap` |
| `set` | no | yes | no | `O(1)` | `HashSet` |

## `list`

A dynamic array, not a linked list. Indexing is cheap, inserting at the front is not.

```python
items = [3, 1, 2]
items.append(4)            # O(1) amortised
items.extend([5, 6])
items.insert(0, 0)         # O(n) - shifts everything
items.remove(3)            # removes the first occurrence, O(n), ValueError if missing
last = items.pop()         # O(1) from the end
first = items.pop(0)       # O(n) from the front - use collections.deque instead
items.sort(key=abs, reverse=True)   # in place, returns None
items.reverse()
items.index(2)             # ValueError if missing
items.count(2)
```

### Slicing

```python
xs = [0, 1, 2, 3, 4, 5]

xs[2:5]       # [2, 3, 4]      from 2 up to (not including) 5
xs[:3]        # [0, 1, 2]
xs[3:]        # [3, 4, 5]
xs[::2]       # [0, 2, 4]      every second element
xs[::-1]      # reversed copy
xs[-2:]       # last two

xs[1:3] = [10, 11, 12]   # slices can be assigned to; the list grows
del xs[::2]              # and deleted
```

Slicing a list always produces a **new list** (a shallow copy). Slicing a string produces a new
string. This is one of the most-used tools in the language — learn the `[start:stop:step]` form.

### Sorting

```python
people = [("Anna", 32), ("Bob", 25), ("Cecil", 41)]

sorted(people, key=lambda p: p[1])                 # by age
sorted(people, key=lambda p: (-p[1], p[0]))        # age desc, then name asc

from operator import itemgetter, attrgetter
sorted(people, key=itemgetter(1))                  # faster and clearer than a lambda
sorted(employees, key=attrgetter("last_name"))
```

Python's sort is **stable** (Timsort), so sorting twice by different keys gives you a
multi-level ordering. There is no `Comparator`-style two-argument comparison function; you
supply a `key` function that maps each element to something comparable. (`functools.cmp_to_key`
exists for the rare case where you really need the old style.)

## `tuple`

An immutable sequence. Two distinct uses:

**1. A fixed-size record** — the elements mean different things:

```python
point = (3, 4)
name, age = ("Anna", 32)          # unpacking
```

**2. Hashable value** — it can be a dict key or a set member, because it is immutable.

```python
cache: dict[tuple[str, int], float] = {}
cache[("EUR", 2024)] = 389.5
```

Syntax details that bite:

```python
single = (42,)         # a one-element tuple - the comma makes it, not the parentheses
not_a_tuple = (42)     # just the integer 42
empty = ()
also_tuple = 1, 2, 3   # parentheses are optional
```

Multiple return values are just a tuple:

```python
def min_max(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)

low, high = min_max([3, 1, 4])
```

### Unpacking

```python
a, b = b, a                       # swap, no temporary variable
first, *rest = [1, 2, 3, 4]       # first=1, rest=[2, 3, 4]
*init, last = [1, 2, 3, 4]        # init=[1, 2, 3], last=4
(a, b), c = (1, 2), 3             # nested
for key, value in mapping.items():
    ...
```

**When should a tuple be a class instead?** As soon as you write `data[2]` and have to remember
what index 2 means, switch to a `NamedTuple` or a `dataclass` (module 02).

## `dict`

The hash map — and the backbone of the language. Objects, modules and namespaces are all
implemented with dicts underneath.

```python
scores = {"anna": 92, "bob": 78}

scores["anna"]                 # 92, KeyError if missing
scores.get("carol")            # None if missing
scores.get("carol", 0)         # 0 if missing
scores["carol"] = 85           # insert or update
scores.setdefault("dave", 0)   # insert only if missing, returns the value
scores.pop("bob")              # remove and return, KeyError if missing
scores.pop("bob", None)        # safe version

"anna" in scores               # membership tests the KEYS, O(1)
len(scores)

scores.keys(), scores.values(), scores.items()   # dynamic views, not copies
merged = defaults | overrides                     # 3.9+ union
defaults.update(overrides)                        # in place
```

Since 3.7 the insertion order is **guaranteed** by the language, so iteration order is
predictable.

### Iteration

```python
for name in scores:                      # iterates over KEYS
    ...
for name, score in scores.items():       # key + value - use this
    ...
for score in scores.values():
    ...
```

### Grouping and counting — the two most common tasks

```python
from collections import defaultdict, Counter

# Grouping
by_city: defaultdict[str, list[str]] = defaultdict(list)
for person in people:
    by_city[person.city].append(person.name)

# Counting
counts = Counter(word.lower() for word in text.split())
counts.most_common(3)          # [('the', 12), ('a', 9), ('of', 7)]
```

`defaultdict(list)` creates an empty list on first access to a missing key, which removes the
`if key not in d:` dance. Note that reading a missing key *creates* it — if that is undesirable,
use `dict.setdefault` or a plain `dict` with `.get`.

## `set`

An unordered collection of unique, hashable elements.

```python
tags = {"python", "backend"}
tags.add("api")
tags.discard("backend")       # no error if missing (remove() raises)
"python" in tags              # O(1)

a, b = {1, 2, 3}, {3, 4}
a | b      # union            {1, 2, 3, 4}
a & b      # intersection     {3}
a - b      # difference       {1, 2}
a ^ b      # symmetric diff   {1, 2, 4}
a <= b     # subset?
```

Note: `{}` is an **empty dict**, not an empty set. Use `set()` for that.

Typical uses:

```python
unique = set(items)                       # deduplicate (order lost)
unique = list(dict.fromkeys(items))       # deduplicate, order preserved

if set(required) - set(provided):         # what is missing?
    raise ValueError("missing fields")
```

Membership testing is the big win: `x in a_list` is `O(n)`, `x in a_set` is `O(1)`. Turning a
list into a set before a loop of membership checks is one of the most common real performance
fixes you will make.

## Costs summary

| Operation | `list` | `dict` / `set` |
|---|---|---|
| `x in c` | `O(n)` | `O(1)` |
| `c[i]` by index | `O(1)` | — |
| `c[k]` by key | — | `O(1)` |
| append / add | `O(1)`* | `O(1)` |
| insert / delete at front | `O(n)` | — |
| iteration | `O(n)` | `O(n)` |

\* amortised; occasionally the backing array is reallocated.

## Beyond the built-ins: `collections`

```python
from collections import deque, Counter, defaultdict, OrderedDict, ChainMap

queue = deque([1, 2, 3])       # O(1) at both ends: queues, sliding windows
queue.appendleft(0)
queue.popleft()
window = deque(maxlen=100)     # ring buffer: pushes the oldest item out
```

`deque` is what you use instead of a list when you need a queue — `list.pop(0)` is `O(n)`.

## Choosing: a decision list

1. Do keys map to values? → `dict`
2. Do I only care about membership and uniqueness? → `set`
3. Is it a fixed-size record with a meaning per position, or does it need to be hashable? → `tuple`
4. Do I add/remove from both ends? → `deque`
5. Otherwise → `list`

## Check yourself

1. Why is `list.pop(0)` slow, and what do you use instead?
2. What makes `sorted(people, key=lambda p: (-p[1], p[0]))` sort the way it does?
3. Why can a tuple be a dict key while a list cannot?
4. What is the difference between `d["k"]`, `d.get("k")` and `d.setdefault("k", 0)`?
5. What does `{}` create, and how do you create an empty set?
6. You are checking membership against 10,000 items inside a loop. What is the fix?
