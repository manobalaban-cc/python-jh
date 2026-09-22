# 02 — Dunder methods and the data model

The "data model" is Python's answer to interfaces. Instead of implementing `Comparable` or
`Iterable`, you implement a **special method** — a name with double underscores on both sides,
hence *dunder* — and the language wires the syntax to it.

| You write | Python calls |
|---|---|
| `len(obj)` | `obj.__len__()` |
| `obj[key]` | `obj.__getitem__(key)` |
| `obj + other` | `obj.__add__(other)` |
| `obj == other` | `obj.__eq__(other)` |
| `for x in obj` | `obj.__iter__()` |
| `x in obj` | `obj.__contains__(x)` |
| `str(obj)`, `print(obj)` | `obj.__str__()` |
| `repr(obj)`, the REPL | `obj.__repr__()` |
| `with obj:` | `obj.__enter__()` / `obj.__exit__()` |
| `obj()` | `obj.__call__()` |
| `bool(obj)`, `if obj:` | `obj.__bool__()`, falling back to `__len__` |

This is what "everything is duck typing" means in practice: `len()` works on anything with a
`__len__`, including your own classes.

## `__repr__` and `__str__`

Implement `__repr__` on **every** class you write. It is what you see in the debugger, in logs
and in test failure output; a default `<Account object at 0x000001EF3...>` wastes your time
every single time.

```python
class Account:
    def __init__(self, owner: str, balance: float) -> None:
        self.owner = owner
        self.balance = balance

    def __repr__(self) -> str:
        # For the developer: unambiguous, ideally valid Python.
        return f"Account(owner={self.owner!r}, balance={self.balance!r})"

    def __str__(self) -> str:
        # For the end user: readable. Optional; falls back to __repr__.
        return f"{self.owner}: {self.balance:,.2f} EUR"
```

The `!r` conversion inside an f-string calls `repr()` on the value, which is what keeps strings
quoted — `owner='Anna'` rather than `owner=Anna`.

## Equality and hashing

By default, two objects are equal only if they are the *same* object. For value objects you
want value equality:

```python
class Money:
    def __init__(self, amount: Decimal, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented          # let Python try the reflected operation
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))
```

Three rules that are exactly the same as in Java, and equally often violated:

1. If `a == b` then `hash(a) == hash(b)` must hold.
2. Hash only on **immutable** state. If you hash on a field you later change, the object gets
   lost inside its own dict.
3. **Defining `__eq__` sets `__hash__` to None**, making instances unhashable. If you want them
   in a set or as dict keys, define `__hash__` too.

Return `NotImplemented` (not `False`, and not `NotImplementedError`) for unsupported types:
that tells Python to try the other operand's reflected method before giving up.

## Ordering

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.major, self.minor = major, minor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor) < (other.major, other.minor)
```

`@total_ordering` derives `<=`, `>`, `>=` from `__eq__` and `__lt__`. Comparing tuples is the
standard trick for multi-field ordering — tuples compare element by element, left to right.

With `__lt__` defined, `sorted()`, `min()` and `max()` work on your type for free.

## Container behaviour

```python
class Portfolio:
    def __init__(self) -> None:
        self._positions: dict[str, int] = {}

    def __len__(self) -> int:
        return len(self._positions)

    def __getitem__(self, ticker: str) -> int:
        return self._positions[ticker]

    def __setitem__(self, ticker: str, quantity: int) -> None:
        self._positions[ticker] = quantity

    def __contains__(self, ticker: str) -> bool:
        return ticker in self._positions

    def __iter__(self) -> Iterator[str]:
        return iter(self._positions)


portfolio = Portfolio()
portfolio["AAPL"] = 10
len(portfolio)            # 1
"AAPL" in portfolio       # True
for ticker in portfolio:  # iterates
    ...
```

Note what you did *not* have to do: no interface declarations, no registration. Implement the
method and the syntax works.

## Operator overloading

```python
class Money:
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int | Decimal) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: int | Decimal) -> "Money":
        return self * factor          # so that 3 * money works too

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)
```

Overload operators **only** when the meaning is obvious and mathematical. `invoice + customer`
is clever and unreadable; write a method with a name.

## Truthiness

```python
class Result:
    def __init__(self, rows: list[str]) -> None:
        self.rows = rows

    def __bool__(self) -> bool:
        return bool(self.rows)
```

Without `__bool__`, Python falls back to `__len__`, and without both, every instance is truthy.
That last case is a classic bug: `if result:` on an "empty" object silently takes the wrong branch.

## Callable objects

```python
class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute

    def __call__(self, request: str) -> bool:
        ...

limiter = RateLimiter(60)
limiter("GET /api")        # the instance is callable
```

Useful when you need a function with configuration and state — a middleware, a validator, a
key function.

## The full reference

The complete list lives in the [Python Data Model](https://docs.python.org/3/reference/datamodel.html)
chapter of the language reference. You do not need to memorise it; you need to know it exists
and to recognise `__something__` as "this is the language hooking into my class".

## Check yourself

1. Why should you write `__repr__` on every class?
2. What is the difference between `__str__` and `__repr__`?
3. What happens to `__hash__` when you define `__eq__`, and why does it matter?
4. Why return `NotImplemented` rather than `False` from `__eq__`?
5. Which dunder methods make `for x in obj` and `x in obj` work?
6. When is operator overloading a bad idea?
