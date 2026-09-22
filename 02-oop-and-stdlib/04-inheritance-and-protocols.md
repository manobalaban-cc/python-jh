# 04 — Inheritance, duck typing, protocols, composition

## Inheritance works as you expect — with one twist

```python
class Repository:
    def __init__(self, connection: str) -> None:
        self.connection = connection

    def save(self, record: dict[str, object]) -> None:
        raise NotImplementedError


class CsvRepository(Repository):
    def __init__(self, connection: str, delimiter: str = ";") -> None:
        super().__init__(connection)          # not optional: nothing is called for you
        self.delimiter = delimiter

    def save(self, record: dict[str, object]) -> None:
        ...
```

`super().__init__()` is **never implicit**. Forget it and the parent's attributes simply do not
exist, producing an `AttributeError` far from the real cause.

There is no `@Override` annotation and no compiler check that you actually overrode something —
a typo in a method name creates a new method instead of overriding. This is one of the reasons
to enable `mypy`.

## Multiple inheritance and the MRO

Python allows multiple inheritance and resolves it with the **Method Resolution Order** (C3
linearisation):

```python
class A:
    def greet(self) -> str: return "A"

class B(A):
    def greet(self) -> str: return "B"

class C(A):
    def greet(self) -> str: return "C"

class D(B, C):
    pass

D().greet()          # 'B'
D.__mro__            # (D, B, C, A, object)
```

`super()` does not mean "my parent"; it means "the next class in the MRO", which in a diamond
depends on the *instance's* class, not the one you are writing. This is what makes cooperative
multiple inheritance (mixins) work — and what makes it confusing.

**Practical guidance:** use multiple inheritance only for small, stateless mixins
(`LoggingMixin`, `ComparableMixin`). For anything else, compose.

## Duck typing

"If it walks like a duck and quacks like a duck…" — Python does not check types at call sites,
only whether the operation is supported.

```python
def render(rows: Iterable[str], out) -> None:
    for row in rows:
        out.write(row + "\n")
```

`out` can be a file, a `StringIO`, a socket wrapper or your own class — anything with a
`write` method. No interface declaration, no adapter, no registration. This is why Python tests
so easily: passing a fake object requires nothing but implementing the methods you use.

The cost is that the contract lives in the documentation rather than the type system. Which is
what `Protocol` fixes.

## `Protocol` — structural typing

```python
from typing import Protocol


class SupportsWrite(Protocol):
    def write(self, data: str) -> int: ...


def render(rows: Iterable[str], out: SupportsWrite) -> None:
    for row in rows:
        out.write(row + "\n")
```

Now `mypy` checks that whatever you pass has a compatible `write` method — **without the class
having to inherit from or know about `SupportsWrite`**. That is structural ("static duck")
typing, the same idea as TypeScript interfaces or Go interfaces.

This is the modern, preferred way to express "any object that can do X" in Python.

```python
class Repository(Protocol):
    def save(self, record: dict[str, object]) -> None: ...
    def find(self, key: str) -> dict[str, object] | None: ...


def import_all(records: list[dict[str, object]], repo: Repository) -> int:
    for record in records:
        repo.save(record)
    return len(records)
```

Any class with those two methods satisfies it — including the fake you write in a test.

## Abstract base classes

When you *do* want inheritance and enforcement at instantiation time:

```python
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def export(self, rows: list[dict[str, object]]) -> bytes:
        """Serialise the rows."""

    def export_to_file(self, rows: list[dict[str, object]], path: Path) -> None:
        # a concrete method shared by every subclass - this is why ABC beats Protocol here
        path.write_bytes(self.export(rows))


class JsonExporter(Exporter):
    def export(self, rows: list[dict[str, object]]) -> bytes:
        return json.dumps(rows).encode("utf-8")


Exporter()          # TypeError: Can't instantiate abstract class
```

| Use | When |
|---|---|
| `Protocol` | you only need "anything shaped like this"; you do not own the implementations |
| `ABC` | you own the hierarchy and want to share concrete code, and instantiating a half-built subclass should fail loudly |

## `isinstance` and when to use it

```python
isinstance(value, str)                    # fine
isinstance(value, (int, float))           # fine
type(value) == str                         # avoid: breaks for subclasses
```

Prefer duck typing and polymorphism; use `isinstance` for genuine branching on input type
(a parser that accepts `str | Path | IO`), and for narrowing types so `mypy` follows you.

The abstract base classes in `collections.abc` are what you should check against, not concrete
types:

```python
from collections.abc import Iterable, Sequence, Mapping

isinstance(value, Iterable)      # True for list, tuple, set, dict, generator, str...
isinstance(value, Sequence)      # list, tuple, str - indexable and sized
isinstance(value, Mapping)       # dict and friends
```

Use those names in annotations too: accept the most general thing you can (`Iterable[str]`)
and return the most specific (`list[str]`).

## Composition over inheritance

The Java advice holds, and Python makes composition cheaper because there is no interface
ceremony:

```python
# Inheritance - the subclass is welded to the parent's internals
class CachingRepository(SqlRepository):
    ...

# Composition - each part is testable and replaceable on its own
class CachingRepository:
    def __init__(self, inner: Repository, cache: dict[str, object] | None = None) -> None:
        self._inner = inner
        self._cache = cache if cache is not None else {}

    def find(self, key: str) -> dict[str, object] | None:
        if key not in self._cache:
            self._cache[key] = self._inner.find(key)
        return self._cache[key]
```

Both satisfy the `Repository` protocol; the second one can wrap *any* implementation.

## Check yourself

1. What happens if you forget `super().__init__()` in a subclass?
2. What does `super()` actually refer to in a multiple-inheritance hierarchy?
3. What is duck typing, and what does it cost you?
4. What problem does `Protocol` solve, and how does it differ from an ABC?
5. When is `isinstance` appropriate, and what should you check against?
6. Why does the "prefer composition" advice apply even more strongly in Python?
