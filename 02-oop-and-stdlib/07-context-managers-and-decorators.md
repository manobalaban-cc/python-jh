# 07 — Context managers and decorators

Two features you will meet on day one of reading real Python code, and that make library code
look like magic until you know how they work.

## Context managers: the `with` statement

`with` is Python's try-with-resources. It guarantees cleanup, including when an exception is
raised.

```python
with open("data.csv", encoding="utf-8") as f:
    process(f)
# the file is closed here, exception or not
```

Several at once:

```python
with open("in.csv") as src, open("out.csv", "w") as dst:
    dst.write(src.read())
```

Where you meet them: files, `sqlite3` connections, `threading.Lock`, `requests.Session`,
`tempfile.TemporaryDirectory`, `pytest.raises`, database transactions.

### Writing one with a class

```python
from types import TracebackType


class Timer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self                      # this is what `as` binds

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.elapsed = time.perf_counter() - self.start
        logger.info("%s took %.3f s", self.label, self.elapsed)
        return False                     # False: do not suppress the exception


with Timer("import"):
    run_import()
```

`__exit__` receives the exception if one happened. Returning `True` **swallows** it — almost
always wrong, and the reason some libraries hide errors mysteriously.

### Writing one with a decorator

Usually shorter:

```python
from contextlib import contextmanager
from collections.abc import Iterator


@contextmanager
def transaction(connection) -> Iterator[Connection]:
    tx = connection.begin()
    try:
        yield connection          # everything before yield = __enter__, after = __exit__
    except Exception:
        tx.rollback()
        raise
    else:
        tx.commit()


with transaction(conn) as c:
    c.execute(...)
```

The single `yield` is the boundary. The `try/finally` around it is what guarantees cleanup.

### `contextlib` helpers

```python
from contextlib import suppress, closing, nullcontext, ExitStack

with suppress(FileNotFoundError):        # instead of try/except/pass
    Path("cache.tmp").unlink()

with closing(urlopen(url)) as response:  # for objects with close() but no __enter__
    ...

ctx = open(path) if path else nullcontext()   # conditional context manager

with ExitStack() as stack:                    # a dynamic number of them
    files = [stack.enter_context(open(p)) for p in paths]
```

## Decorators

A decorator is a function that takes a function and returns a replacement. The `@` syntax is
just sugar:

```python
@timed
def process(): ...

# is exactly
def process(): ...
process = timed(process)
```

### Writing one

```python
import functools
import time
from collections.abc import Callable
from typing import Any


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)                       # keeps __name__, __doc__, signature
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info("%s took %.3f s", func.__name__, time.perf_counter() - start)

    return wrapper


@timed
def import_transactions(path: Path) -> int:
    ...
```

`functools.wraps` is not optional: without it the wrapped function reports itself as `wrapper`,
which breaks tracebacks, `help()`, and any tool that introspects your code.

`*args, **kwargs` in the wrapper is what makes the decorator work on any signature.

### Decorators with arguments

One more level of nesting, because `@retry(times=3)` must first *call* `retry` and then apply
the result:

```python
def retry(times: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last: Exception | None = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except OSError as exc:
                    last = exc
                    logger.warning("attempt %d/%d failed: %s", attempt + 1, times, exc)
                    time.sleep(delay)
            raise RuntimeError(f"failed after {times} attempts") from last

        return wrapper

    return decorator


@retry(times=5, delay=0.5)
def fetch(url: str) -> bytes:
    ...
```

### The decorators you will use without writing any

```python
@property               # attribute-style access          (chapter 01)
@staticmethod
@classmethod
@dataclass              # code generation                  (chapter 03)
@functools.cache        # memoisation                      (01-language-core/06)
@functools.wraps
@abstractmethod         # abstract base classes            (chapter 04)
@contextmanager
@pytest.fixture         # test fixtures                    (chapter 09)
@pytest.mark.parametrize
@app.get("/items")      # routing in FastAPI               (module 04)
```

### Decorating a class method

The decorator sees `self` as the first positional argument, so a generic `*args` wrapper works
unchanged. Order matters when stacking:

```python
class Api:
    @property
    @functools.cache          # applied first, closest to the function
    def config(self) -> dict[str, str]: ...
```

Read a decorator stack bottom-up: the one nearest the `def` wraps first.

> Caching on instance methods with `functools.cache` keeps the instance alive forever (the
> cache holds `self`). Use `functools.cached_property` for per-instance caching instead.

## When not to write a decorator

Decorators hide behaviour at the call site. A decorator earns its place when the concern is
genuinely **cross-cutting** — timing, retries, logging, authorisation, caching, registration —
and applies to many functions. For one-off behaviour, a plain function call is clearer.

## Check yourself

1. What does `with` guarantee, and what does `__exit__` returning `True` mean?
2. What are the two ways to write a context manager, and when do you use the class version?
3. What does `@` actually do to the decorated function?
4. Why is `functools.wraps` necessary?
5. Why does a decorator with arguments need three levels of nesting?
6. In what order do stacked decorators apply?
