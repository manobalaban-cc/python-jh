# 03 — Dataclasses, named tuples, enums

Most classes in an application carry data. Writing `__init__`, `__repr__` and `__eq__` by hand
for each of them is noise — Python generates them for you.

## `@dataclass`

```python
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date


@dataclass
class Transaction:
    timestamp: date
    amount: Decimal
    currency: str
    recipient: str
    tags: list[str] = field(default_factory=list)      # mutable default, done right
    note: str = ""

    def is_large(self, threshold: Decimal = Decimal("1000")) -> bool:
        return self.amount >= threshold


tx = Transaction(date(2024, 5, 1), Decimal("250.00"), "EUR", "Amazon")
print(tx)          # Transaction(timestamp=datetime.date(2024, 5, 1), amount=Decimal('250.00'), ...)
tx == Transaction(date(2024, 5, 1), Decimal("250.00"), "EUR", "Amazon")   # True
```

What the decorator generates: `__init__`, `__repr__` and `__eq__`. The annotations are not
optional here — they are what the decorator reads to build the fields.

`field(default_factory=list)` is how you give a mutable default safely: the factory is called
once per instance, which sidesteps the shared-mutable-default trap. Writing `tags: list[str] = []`
raises an error at class creation time; the language actively stops you.

### The options that matter

```python
@dataclass(frozen=True)       # immutable: assignment raises, and __hash__ is generated
@dataclass(order=True)        # generates __lt__, __le__, __gt__, __ge__ by field order
@dataclass(slots=True)        # uses __slots__: less memory, faster attribute access (3.10+)
@dataclass(kw_only=True)      # every field must be passed by keyword (3.10+)
```

`frozen=True` is the default you should reach for on value objects — an immutable object can be
a dict key, is safe to share between threads, and cannot be corrupted by a caller.

```python
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must not be negative")
```

`__post_init__` runs after the generated `__init__` — this is where validation goes.

### Useful helpers

```python
from dataclasses import asdict, astuple, replace, fields

asdict(tx)                     # nested dict, recursive - handy for JSON
astuple(tx)
replace(tx, amount=Decimal("300"))   # a copy with one field changed (works on frozen too)
[f.name for f in fields(tx)]
```

`replace()` is how you "modify" a frozen instance: you do not, you build a new one.

## `NamedTuple`

A tuple with named fields: immutable, hashable, unpackable, and it compares and iterates like a
tuple.

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

p = Point(1.0, 2.0)
p.x                 # 1.0
x, y = p            # unpacks
p[0]                # 1.0 - it really is a tuple
p._replace(x=5.0)   # a modified copy
```

Use it when the value is genuinely tuple-like and you want tuple behaviour (unpacking, use as a
dict key, a cheap return value). For anything with more than two or three fields, or with any
behaviour, a frozen dataclass reads better.

## `dataclass` vs `NamedTuple` vs `dict` vs `TypedDict` vs Pydantic

| Tool | When |
|---|---|
| `dict` | genuinely dynamic keys (a parsed JSON blob you pass straight through) |
| `TypedDict` | a dict with a known key shape, usually at an API boundary; no runtime cost |
| `NamedTuple` | small, immutable, tuple-like value; needs unpacking or hashing |
| `@dataclass` | the default choice for structured data inside your application |
| `@dataclass(frozen=True)` | value objects, configuration, anything shared |
| Pydantic `BaseModel` | data crossing a trust boundary that must be **validated and parsed** |

The last row matters: dataclasses **do not validate anything**. `Transaction(amount="not a
number")` is perfectly happy at runtime. When the data comes from a request body, a config file
or an external API, use Pydantic (module 04); inside your own code, a dataclass is enough.

## `Enum`

```python
from enum import Enum, StrEnum, IntEnum, auto


class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


Status.PENDING              # <Status.PENDING: 'pending'>
Status.PENDING.name         # 'PENDING'
Status.PENDING.value        # 'pending'
Status("approved")          # lookup by value -> Status.APPROVED
list(Status)                # every member, in definition order
Status.PENDING is Status.PENDING    # True - members are singletons
```

Why bother instead of string constants? Because `status == "aproved"` is a typo that silently
evaluates to `False`, whereas `Status("aproved")` raises `ValueError` immediately. Enum members
are also self-documenting in IDEs and exhaustively checkable by `mypy`.

```python
class Priority(IntEnum):        # comparable and usable as an int
    LOW = 1
    HIGH = 3

Priority.HIGH > Priority.LOW    # True


class Currency(StrEnum):        # 3.11+ - behaves as a str, so JSON just works
    EUR = "EUR"
    HUF = "HUF"

f"{Currency.EUR}"               # 'EUR'
```

`auto()` fills in values when they carry no meaning:

```python
class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
```

Enums pair well with `match`:

```python
match status:
    case Status.PENDING:
        ...
    case Status.APPROVED:
        ...
```

Note the qualified name: a bare `case PENDING:` would be a capture pattern that matches anything.

## Putting it together

```python
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Currency(StrEnum):
    EUR = "EUR"
    HUF = "HUF"
    USD = "USD"


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency = Currency.EUR

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"negative amount: {self.amount}")

    def __str__(self) -> str:
        return f"{self.amount:,.2f} {self.currency}"


@dataclass(slots=True)
class Transaction:
    timestamp: datetime
    money: Money
    recipient: str
    tags: list[str] = field(default_factory=list)
```

This is what idiomatic modern Python domain code looks like: annotated, mostly immutable, no
boilerplate, no getters.

## Check yourself

1. What does `@dataclass` generate for you?
2. Why is `tags: list[str] = []` an error in a dataclass, and what do you write instead?
3. What does `frozen=True` buy you?
4. How do you "change" a field on a frozen instance?
5. When do you need Pydantic instead of a dataclass?
6. Why is an `Enum` better than a set of string constants?
