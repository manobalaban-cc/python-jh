# Migration cheat sheet: Java / C# / JavaScript → Python

## Syntax

| Concept | Java / C# | Python |
|---|---|---|
| Block | `{ ... }` | indentation (4 spaces) |
| Statement end | `;` | newline |
| Comment | `//`, `/* */` | `#`, and a docstring for documentation |
| Variable | `int x = 5;` | `x = 5` (or `x: int = 5`) |
| Constant | `final int MAX = 10;` | `MAX = 10` (convention only, not enforced) |
| String | `"a" + b` | `f"a{b}"` |
| Null | `null` | `None` |
| Booleans | `true` / `false` | `True` / `False` |
| Logical ops | `&&`, `\|\|`, `!` | `and`, `or`, `not` |
| Ternary | `c ? a : b` | `a if c else b` |
| Increment | `i++` | `i += 1` (there is no `++`) |
| Equality | `.equals()` vs `==` | `==` (value) vs `is` (identity) |
| Casting | `(int) x` | `int(x)` (a conversion, not a cast) |
| Integer division | `7 / 2 == 3` | `7 // 2 == 3`; `7 / 2 == 3.5` |
| Switch | `switch` | `match` (3.10+), `elif`, or a dict of handlers |
| For loop | `for (int i=0; i<n; i++)` | `for i in range(n)` |
| For-each | `for (var x : xs)` | `for x in xs` |
| While | `while (c) { }` | `while c:` |
| Do-while | `do { } while (c);` | `while True: ... if not c: break` |
| Lambda | `x -> x * 2` | `lambda x: x * 2` |
| Main | `public static void main` | `if __name__ == "__main__":` |

## Types and collections

| Java / C# | Python |
|---|---|
| `int`, `long`, `Integer` | `int` (arbitrary precision) |
| `double`, `float` | `float` (always 64-bit) |
| `BigDecimal` | `decimal.Decimal` |
| `String`, `char` | `str` (no separate character type) |
| `byte[]` | `bytes`, `bytearray` |
| `ArrayList<T>` | `list` |
| `T[]` (fixed) | `tuple` (immutable) or `array`/NumPy for numbers |
| `HashMap<K,V>`, `Dictionary` | `dict` |
| `LinkedHashMap` | `dict` (insertion-ordered by language guarantee) |
| `HashSet<T>` | `set` |
| `Deque`, `Queue` | `collections.deque` |
| `Optional<T>`, `T?` | `T \| None` |
| `enum` | `enum.Enum` / `StrEnum` |
| `record`, POJO | `@dataclass` |
| `Stream` / LINQ | comprehensions, generators, `itertools` |

## Object orientation

| Java / C# | Python |
|---|---|
| `new Foo()` | `Foo()` |
| Constructor | `__init__` (an initialiser; the object already exists) |
| `this` | `self`, explicit as the first parameter |
| `toString()` | `__str__` / `__repr__` |
| `equals()` / `hashCode()` | `__eq__` / `__hash__` |
| `Comparable` | `__lt__` (+ `functools.total_ordering`) |
| `Iterable` | `__iter__` |
| `AutoCloseable` / `using` | `__enter__` / `__exit__`, the `with` statement |
| `private` / `protected` | `_name` (convention), `__name` (name mangling only) |
| getters/setters | plain attributes, then `@property` if logic appears |
| `static` method | `@staticmethod`, or just a module-level function |
| Factory method | `@classmethod` |
| `interface` | `Protocol` (structural) or `ABC` (nominal) |
| `abstract` | `abc.ABC` + `@abstractmethod` |
| `@Override` | nothing — which is why you run `mypy` |
| Method overloading | **not available**; use default values, `*args`, or `functools.singledispatch` |
| Generics `<T>` | `def f[T](x: T) -> T` (3.12+) or `TypeVar` |
| Annotations / attributes | decorators |
| Package | module (file) and package (directory) |

## Exceptions

| Java / C# | Python |
|---|---|
| `try/catch/finally` | `try/except/else/finally` |
| `catch (E e)` | `except E as e:` |
| `throw new E("x")` | `raise E("x")` |
| `throws` declaration | nothing; document it in the docstring |
| Checked exceptions | do not exist |
| `NullPointerException` | `AttributeError` / `TypeError` |
| `IllegalArgumentException` | `ValueError` / `TypeError` |
| `IndexOutOfBoundsException` | `IndexError` |
| `e.printStackTrace()` | `logging.exception("...")` |
| Style | defensive checks (LBYL) | try it and handle the failure (EAFP) |

## Tooling

| Java / C# | Python |
|---|---|
| Maven / Gradle / NuGet | `pip` + `pyproject.toml`, or `uv` |
| `pom.xml` / `.csproj` | `pyproject.toml` |
| `mvn install` | `pip install -e ".[dev]"` |
| Maven Central / NuGet | PyPI |
| JUnit / xUnit | `pytest` |
| Mockito / Moq | `unittest.mock` |
| Checkstyle / SpotBugs / StyleCop | `ruff` |
| `javac` type checking | `mypy` / `pyright` (separate, optional, do it anyway) |
| Javadoc / XML docs | docstrings + Sphinx or MkDocs |
| `.jar` / `.dll` | wheel (`.whl`) |
| JVM / CLR | CPython |
| `-Xmx` | nothing equivalent; memory is not pre-allocated |
| Threads | threads (GIL-limited), processes, or `asyncio` |

## From JavaScript / TypeScript

| JS / TS | Python |
|---|---|
| `const`, `let` | plain assignment; `Final` is a hint only |
| `undefined` and `null` | just `None` |
| `===` | `==` (Python does not coerce) |
| `array.map(f)` | `[f(x) for x in xs]` |
| `array.filter(f)` | `[x for x in xs if f(x)]` |
| `array.reduce(f, init)` | `functools.reduce(f, xs, init)` |
| `Object.keys(o)` | `o.keys()` |
| `{...a, ...b}` | `a \| b` (dicts) |
| `[...a, ...b]` | `[*a, *b]` |
| `async/await` | `async/await` (same idea, different loop) |
| `Promise.all` | `asyncio.gather` |
| `npm install` | `pip install` |
| `package.json` | `pyproject.toml` |
| `node_modules/` | the virtual environment's `site-packages` |
| `jest` | `pytest` |
| Truthiness | similar, but `[]` and `{}` are **falsy** in Python |

## Habits to unlearn

1. **`camelCase`** → `snake_case` for variables and functions.
2. **Getters and setters everywhere** → public attributes, `@property` when needed.
3. **A class for everything** → modules and functions are first-class; `Util` classes are a smell.
4. **Checking before acting** → EAFP: try it, handle the exception.
5. **Index loops** → `for item in items`, `enumerate`, `zip`.
6. **`StringBuilder`** → `"".join(parts)`.
7. **Interfaces for everything** → duck typing, with `Protocol` where the contract matters.
8. **Defensive null checks everywhere** → `X | None` plus a type checker.
9. **Deep inheritance hierarchies** → composition; Python makes it cheap.
10. **Comments explaining what the code does** → readable code plus docstrings explaining *why*.

## Things Python does that will surprise you

- Default argument values are evaluated **once**, at definition time.
- Assignment never copies; everything is a reference.
- `is` and `==` are different questions, and `is` on small integers lies.
- Mutable class attributes are shared between instances.
- A module is executed on first import; a module-level `print` runs then.
- Everything is mutable-by-convention: `_private` is an honour system.
- There is no `final`, no `const`, no compile step to catch your typo — hence `ruff` and `mypy`.
