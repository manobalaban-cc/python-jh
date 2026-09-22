# 06 — Functions

## Definition and annotations

```python
def transfer(amount: float, sender: str, recipient: str, note: str = "") -> bool:
    """Transfer money between accounts.

    Args:
        amount: The amount to transfer, must be positive.
        sender: Source account identifier.
        recipient: Target account identifier.
        note: Optional message shown on the statement.

    Returns:
        True if the transfer was accepted.

    Raises:
        ValueError: If amount is not positive.
    """
```

Annotations are **not enforced at runtime** — they exist for `mypy`, your IDE and the reader.
Write them on everything public; they are the closest thing Python has to a compiler.

The docstring is the first statement in the body, and it is what `help(transfer)` shows.
Google style (above) and NumPy style are both common; pick one per project.

## Arguments: positional and keyword

```python
def connect(host: str, port: int = 5432, *, timeout: float = 5.0, retries: int = 3) -> None:
    ...

connect("localhost")                        # defaults
connect("localhost", 5433)                  # positional
connect("localhost", port=5433)             # keyword
connect("localhost", timeout=1.0)           # keyword-only
connect("localhost", 5433, 1.0)             # TypeError! timeout is keyword-only
```

The bare `*` marks the start of **keyword-only** parameters. Use it for optional flags —
it makes call sites self-documenting and lets you reorder parameters later without breaking
callers. `/` does the opposite, marking positional-only parameters (rare in application code).

**A strong convention:** if an argument is a bare `True`/`False` at the call site, make it
keyword-only. `save(data, True)` tells the reader nothing; `save(data, overwrite=True) `does.

## `*args` and `**kwargs`

```python
def log_all(*args: object, sep: str = " ", **kwargs: str) -> None:
    print(sep.join(str(a) for a in args), kwargs)

log_all("a", "b", level="INFO")     # args=("a", "b"), kwargs={"level": "INFO"}
```

The same syntax unpacks at the call site:

```python
values = [1, 2, 3]
print(*values)                       # print(1, 2, 3)

config = {"host": "localhost", "port": 5432}
connect(**config)                    # connect(host="localhost", port=5432)
```

Most useful when writing wrappers and decorators that must forward whatever they receive.

## The mutable default trap

The single most famous Python gotcha:

```python
def add_item(item: str, target: list[str] = []) -> list[str]:   # BROKEN
    target.append(item)
    return target

add_item("a")     # ['a']
add_item("b")     # ['a', 'b']   <- the same list!
```

**Why:** default values are evaluated **once**, when the `def` statement executes — not on each
call. The list is created once and shared by every call that does not pass its own.

The fix:

```python
def add_item(item: str, target: list[str] | None = None) -> list[str]:
    if target is None:
        target = []
    target.append(item)
    return target
```

The same applies to `{}`, `set()`, `datetime.now()` and any other mutable or
evaluated-at-definition-time expression. `ruff`'s `B006` rule catches this.

## Functions are objects

```python
def double(x: int) -> int:
    return x * 2

f = double                 # not a call - a reference
f(21)                      # 42

operations = {"double": double, "negate": lambda x: -x}
operations["double"](21)

def apply_twice(fn, value):        # a function taking a function
    return fn(fn(value))
```

### `lambda`

An anonymous, **single-expression** function. No statements, no multiple lines.

```python
sorted(people, key=lambda p: p.age)
```

Use it only as a throwaway argument. Assigning one to a name (`f = lambda x: x * 2`) is worse
than `def` in every way — worse tracebacks, no docstring — and `ruff` flags it (`E731`).

## Scope: LEGB

Name resolution goes **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in.

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        print(x)        # 'enclosing' - found one level up

    inner()
```

The important rule: **assigning to a name anywhere in a function makes it local for the whole
function**, which produces this classic:

```python
counter = 0

def increment():
    counter += 1        # UnboundLocalError: counter is local because we assign to it

def increment():
    global counter      # works, but a global counter is usually a design smell
    counter += 1
```

In nested functions, `nonlocal` targets the enclosing function's variable:

```python
def make_counter():
    count = 0
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
c(); c()      # 1, 2
```

Prefer returning values over mutating outer state; `global` in application code is nearly
always a sign that something should be a class or an explicit parameter.

## Closures

An inner function captures the *variables* of its enclosing scope, not their values at
definition time:

```python
def multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor      # factor comes from the closure
    return multiply

double = multiplier(2)
triple = multiplier(3)
double(10)      # 20
```

The late-binding trap, which everyone hits in a loop:

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]        # [2, 2, 2] - not [0, 1, 2]!

funcs = [lambda i=i: i for i in range(3)]    # bind now, via a default argument
[f() for f in funcs]        # [0, 1, 2]
```

## Return values

```python
def divide(a: float, b: float) -> tuple[float, float]:
    return a // b, a % b        # a tuple

quotient, remainder = divide(7, 2)
```

A function with no `return` returns `None`. A bare `return` does the same.

**Do not return different types depending on the path** — `list | None | str` return types make
callers miserable. Return a consistent type, or raise.

## `functools` essentials

```python
from functools import lru_cache, cache, partial, reduce, wraps

@cache                      # memoisation, unbounded (3.9+)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@lru_cache(maxsize=1000)    # bounded variant
def geocode(address: str) -> tuple[float, float]:
    ...

to_int = partial(int, base=16)     # pre-bind arguments
to_int("ff")                        # 255
```

`@cache` requires hashable arguments and is a memory leak waiting to happen on unbounded input
— fine for pure functions with a small key space.

## Pure functions and side effects

The testable shape, which you already know but which matters even more here because the
type system will not save you:

```python
# HARD to test: reads a file, prints, mutates global state
def process():
    data = open("input.csv").read()
    global total
    total = compute(data)
    print(total)

# EASY to test: input in, value out
def parse(text: str) -> list[Record]: ...
def summarize(records: list[Record]) -> Summary: ...

def main() -> None:                         # I/O confined to one place
    text = Path("input.csv").read_text(encoding="utf-8")
    print(summarize(parse(text)))
```

## Check yourself

1. When are default argument values evaluated, and what does that break?
2. What does the bare `*` do in a parameter list, and why is it good practice?
3. Why does `counter += 1` raise `UnboundLocalError` inside a function?
4. What is the difference between `global` and `nonlocal`?
5. Why does `[lambda: i for i in range(3)]` return three functions that all give 2?
6. When is `@cache` a good idea, and when is it a memory leak?
