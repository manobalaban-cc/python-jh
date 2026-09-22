# 02 — OOP, the data model, the standard library

You know object orientation. This module is about what Python does differently: there is no
`private`, no interfaces, no method overloading — and instead there is a **data model** of
special methods that lets your own types behave exactly like built-in ones.

| Chapter | Topic |
|---|---|
| [01](01-classes-and-objects.md) | Classes, `self`, attributes, properties, class vs instance state |
| [02](02-dunder-and-data-model.md) | `__repr__`, `__eq__`, `__hash__`, `__len__`, operator overloading |
| [03](03-dataclasses-and-enums.md) | `dataclass`, `NamedTuple`, `Enum`, immutable value objects |
| [04](04-inheritance-and-protocols.md) | Inheritance, MRO, `super()`, duck typing, ABC, `Protocol`, composition |
| [05](05-type-hints.md) | Type annotations, generics, `mypy`, gradual typing |
| [06](06-modules-and-stdlib-tour.md) | The standard library you must know: `pathlib`, `datetime`, `re`, `logging`, `collections`, … |
| [07](07-context-managers-and-decorators.md) | `with`, `contextlib`, writing decorators, `functools.wraps` |
| [08](08-files-and-serialization.md) | Files, encodings, CSV, JSON, dates, Excel, Parquet |
| [09](09-testing-with-pytest.md) | `pytest`, fixtures, parametrization, mocking, coverage |
| [exercises/](exercises/) | A small library built the way a real one is built |

## By the end of this module

- You write classes that behave like built-in types (`repr`, equality, iteration, `with`).
- You know when a `dataclass` is the right answer and when a plain function is.
- You use composition and `Protocol` instead of deep inheritance trees.
- You write type-annotated code that passes `mypy --strict`.
- You can find the right standard-library module instead of reaching for a dependency.
- You write tests with fixtures, parametrization and mocks, and you know what not to mock.

## The module project

`exercises/` holds a single coherent task: a **CSV import library** with validation, custom
exceptions, a context manager, a decorator and a full test suite. It is deliberately the shape
of a real internal library, and it is the warm-up for the module 05 projects.
