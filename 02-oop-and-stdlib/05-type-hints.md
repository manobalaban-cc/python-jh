# 05 — Type hints and `mypy`

## What annotations are and are not

```python
def total(prices: list[float], vat: float = 0.27) -> float:
    return sum(prices) * (1 + vat)
```

- They are **not enforced at runtime**. `total("not a list")` will happily fail somewhere else.
- They are read by **static checkers** (`mypy`, `pyright`), by your **IDE** for completion, and
  by **humans**.
- Some libraries do read them at runtime and act on them — Pydantic validates against them,
  FastAPI builds request parsing and OpenAPI docs from them, `dataclasses` builds fields from
  them. That is the exception, not the rule.

Python calls this **gradual typing**: annotate what you want, leave the rest. Unannotated code
keeps working — which is exactly how a large codebase gets typed over time.

## The basics

```python
name: str = "Anna"
count: int = 0
ratio: float = 0.5            # int is accepted where float is expected
active: bool = True
data: bytes = b""

items: list[str]
pairs: tuple[str, int]              # exactly two elements, fixed types
row: tuple[str, ...]                # any number, all str
mapping: dict[str, int]
unique: set[str]

maybe: str | None = None            # 3.10+; older: Optional[str]
number: int | float                 # union; older: Union[int, float]
```

Since 3.9 the built-in types are generic, so `List`, `Dict`, `Tuple` from `typing` are obsolete.
`ruff`'s `UP` rules rewrite the old forms automatically.

## Functions

```python
from collections.abc import Callable, Iterable, Iterator, Sequence


def process(
    rows: Iterable[str],                    # accept the most general type you can
    transform: Callable[[str], str],        # a function taking str, returning str
    *,
    limit: int | None = None,
) -> list[str]:                             # return the most specific type
    ...


def lines() -> Iterator[str]:               # a generator function
    yield "one"


def log(message: str) -> None:              # returns nothing
    print(message)


def fail(reason: str) -> NoReturn:          # never returns (always raises or exits)
    raise RuntimeError(reason)
```

The asymmetry is the rule worth memorising: **be liberal in what you accept, specific in what
you return.** A function annotated `def f(items: list[str])` cannot be called with a tuple or a
generator; `Iterable[str]` can.

## Classes

```python
from typing import Self


class Account:
    interest_rate: float = 0.02          # class attribute

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner: str = owner
        self.balance = balance           # inferred from the parameter, no annotation needed
        self._log: list[str] = []        # empty containers DO need one

    def with_bonus(self, amount: float) -> Self:      # 3.11+: "the same class"
        return type(self)(self.owner, self.balance + amount)
```

`Self` is what you want for fluent APIs and alternative constructors — it keeps working in
subclasses, unlike hard-coding `-> "Account"`.

## Generics

```python
def first[T](items: Sequence[T]) -> T | None:        # 3.12+ syntax
    return items[0] if items else None


class Repository[T]:
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, key: str, item: T) -> None:
        self._items[key] = item

    def get(self, key: str) -> T | None:
        return self._items.get(key)


repo: Repository[Account] = Repository()
account = repo.get("anna")       # mypy knows this is Account | None
```

Before 3.12 the same thing required `TypeVar`:

```python
from typing import TypeVar, Generic

T = TypeVar("T")

def first(items: Sequence[T]) -> T | None: ...
class Repository(Generic[T]): ...
```

You will see both; write the new form in new code.

## Narrowing

`mypy` follows control flow, which is why `X | None` is workable in practice:

```python
def describe(value: str | None) -> str:
    if value is None:
        return "missing"
    return value.upper()          # mypy knows value is str here


def handle(event: dict[str, object]) -> None:
    kind = event.get("type")
    if isinstance(kind, str):     # isinstance narrows too
        print(kind.upper())
```

When you know something the checker cannot prove:

```python
from typing import cast

config = cast(dict[str, str], load_json(path))     # "trust me" - no runtime check

assert value is not None        # also narrows, and does check at runtime
```

Use `cast` sparingly; every cast is a place where your types can lie.

## `Any` and when not to use it

```python
from typing import Any

def parse(raw: Any) -> Any:      # switches type checking OFF for this value
    ...
```

`Any` is contagious: anything derived from it is unchecked too. Prefer `object` when you truly
accept anything (it forces the caller to narrow before using it), and reserve `Any` for
genuinely dynamic boundaries.

## `TypedDict` and `Literal`

```python
from typing import Literal, TypedDict


class UserRecord(TypedDict):
    id: int
    name: str
    email: str | None


def render(user: UserRecord) -> str:
    return f"{user['name']} <{user['email']}>"     # mypy checks the keys


Mode = Literal["r", "w", "a"]

def open_file(path: str, mode: Mode = "r") -> None: ...

open_file("x.txt", "z")     # mypy error: invalid literal
```

`TypedDict` is how you type JSON-shaped data without converting it into objects.

## Running `mypy`

```bash
mypy src/
mypy --strict src/
```

`strict` turns on a bundle of options, the most important being: every function must be
annotated, `Any` may not silently leak, and unused ignores are errors.

In an existing codebase, enable it per module:

```toml
[tool.mypy]
python_version = "3.12"
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "myapp.core.*"
strict = true

[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true
```

Silencing a specific line (always with the error code, never bare):

```python
result = legacy_api()  # type: ignore[no-any-return]
```

Third-party libraries without annotations need stub packages:

```bash
python -m pip install types-requests pandas-stubs
```

## What good annotations buy you

1. The IDE completes attribute names and catches typos as you type.
2. Refactoring becomes safe: rename a field and the checker finds every call site.
3. The signature documents the contract, so fewer docstrings go stale.
4. Reviews focus on logic instead of "what does this function return?".

## Check yourself

1. What do annotations do at runtime, and which libraries are the exception?
2. Why annotate a parameter as `Iterable[str]` rather than `list[str]`?
3. When do you need an annotation on an assignment, and when is inference enough?
4. What is the difference between `Any` and `object`?
5. How does `mypy` know that `value` is a `str` after `if value is None: return`?
6. How do you introduce `mypy` into a large untyped codebase?
