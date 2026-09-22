"""Cross-cutting concerns: timing as a decorator and as a context manager."""

import functools
import logging
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any, Literal

logger = logging.getLogger(__name__)


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Log how long each call to ``func`` takes.

    The 3.12 type-parameter syntax (``[**P, R]``) keeps the wrapped signature
    visible to mypy, so callers of a decorated function still get argument
    checking and completion. Before 3.12 this needed ParamSpec and TypeVar
    objects declared at module level.
    """

    @functools.wraps(func)  # without this, the wrapper would masquerade as `wrapper`
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            # `finally`, so a failing call is timed as well.
            logger.info("%s took %.3f s", func.__name__, time.perf_counter() - start)

    return wrapper


class Timer:
    """Context manager measuring the wall-clock time of a block.

    >>> with Timer("import") as timer:
    ...     pass
    >>> timer.elapsed >= 0
    True
    """

    def __init__(self, label: str) -> None:
        self.label = label
        self.elapsed: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        # The return type says "never swallows an exception". Annotating it as
        # plain `bool` makes mypy warn, because a bool return means the context
        # manager *might* suppress errors - a real source of hidden bugs.
        self.elapsed = time.perf_counter() - self._start
        logger.info("%s took %.3f s", self.label, self.elapsed)
        return False


@contextmanager
def measured(label: str) -> Iterator[dict[str, Any]]:
    """The same thing written with contextlib, for comparison."""
    result: dict[str, Any] = {}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start
        logger.info("%s took %.3f s", label, result["elapsed"])
