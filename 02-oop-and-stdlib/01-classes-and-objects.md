# 01 — Classes and objects

## The shape of a class

```python
class Account:
    """A bank account."""

    interest_rate = 0.02              # class attribute - shared by every instance

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner            # instance attribute
        self.balance = balance
        self._transactions: list[float] = []

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self._transactions.append(amount)

    def __repr__(self) -> str:
        return f"Account(owner={self.owner!r}, balance={self.balance!r})"


account = Account("Anna", 100.0)     # no `new` keyword
account.deposit(50)
```

Differences from Java/C# worth noting immediately:

- **`self` is explicit.** It is the first parameter of every instance method, and you pass
  nothing for it at the call site — `account.deposit(50)` becomes `Account.deposit(account, 50)`.
  It is a convention, not a keyword, but never call it anything else.
- **`__init__` is not a constructor**, it is an *initialiser*. The object already exists when it
  runs (`__new__` created it). You will rarely touch `__new__`.
- **No field declarations.** Attributes spring into existence when first assigned. Declare them
  all in `__init__` anyway, so readers and type checkers can see the shape of the object.
- **No `new`**, no `public`/`private`, no method overloading.

## Attributes are dynamic

```python
account.nickname = "savings"     # works: a new attribute on this instance only
del account.nickname
```

This flexibility is occasionally useful and mostly a source of typos silently creating new
attributes. `__slots__` switches it off and saves memory:

```python
class Point:
    __slots__ = ("x", "y")        # only these attributes may exist

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

Use `__slots__` for small objects created in large numbers; otherwise it is premature optimisation.

## Class attributes vs instance attributes

```python
class Account:
    interest_rate = 0.02          # one value, shared
    all_accounts: list["Account"] = []     # DANGER, see below

    def __init__(self, owner: str) -> None:
        self.owner = owner        # one value per instance
```

Reading looks up the instance first, then the class. Writing **always** creates an instance
attribute:

```python
a, b = Account("Anna"), Account("Bob")
Account.interest_rate = 0.03     # affects both
a.interest_rate = 0.05           # creates an instance attribute on `a` only
print(b.interest_rate)           # 0.03
```

The trap is the same one as mutable default arguments: a **mutable** class attribute is shared
by every instance.

```python
class Cart:
    items: list[str] = []         # BROKEN: one list for all carts

    def add(self, item: str) -> None:
        self.items.append(item)   # mutates the shared list

class Cart:
    def __init__(self) -> None:
        self.items: list[str] = []    # correct: one list per instance
```

## "Private" attributes

Python has no access modifiers. It has conventions:

| Name | Meaning |
|---|---|
| `value` | public API |
| `_value` | internal; "do not touch, no compatibility promise" |
| `__value` | name mangling: becomes `_ClassName__value` |

```python
class Base:
    def __init__(self) -> None:
        self.public = 1
        self._internal = 2
        self.__mangled = 3

obj = Base()
obj._internal          # works - nothing stops you
obj.__mangled          # AttributeError
obj._Base__mangled     # 3 - this is all the mangling does
```

Double underscore is **not** a security feature; it exists to avoid accidental name collisions
in subclasses. In practice, use a single underscore and trust your colleagues.

## Properties instead of getters and setters

Do not write `get_balance()` / `set_balance()`. Start with a plain attribute, and if you later
need logic, turn it into a property — **the call sites do not change**.

```python
class Account:
    def __init__(self, balance: float) -> None:
        self._balance = balance

    @property
    def balance(self) -> float:
        """Current balance in EUR."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value


account = Account(100)
account.balance          # calls the getter
account.balance = 50     # calls the setter
account.balance = -1     # ValueError
```

A computed, read-only property is even more common:

```python
    @property
    def is_overdrawn(self) -> bool:
        return self._balance < 0
```

This is why Python code has so few getters: you add them only when you need them, without
breaking the API. Keep properties cheap — a caller writing `obj.total` does not expect a
database query.

## Instance, class and static methods

```python
class Transaction:
    def __init__(self, amount: float, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def converted(self, rate: float) -> float:        # instance method
        return self.amount * rate

    @classmethod
    def from_csv_row(cls, row: str) -> "Transaction":  # alternative constructor
        amount, currency = row.split(";")
        return cls(float(amount), currency)

    @staticmethod
    def is_supported(currency: str) -> bool:           # no instance or class needed
        return currency in {"EUR", "HUF", "USD"}
```

- `@classmethod` receives the class as `cls`. Its main use is **alternative constructors**
  (`from_csv_row`, `from_dict`, `parse`). Because it receives `cls`, it works correctly in
  subclasses too.
- `@staticmethod` receives nothing. It is a function that lives in the class namespace for
  organisational reasons. If you write many of them, a module-level function may be the better
  home.

## When should it be a class at all?

Coming from Java, everything looks like a class. In Python, module-level functions are fine —
a class earns its place when there is **state** tied to **behaviour**.

| Need | Use |
|---|---|
| A few related functions | a module |
| Data only, no behaviour | `dataclass`, `NamedTuple`, or a dict |
| State plus behaviour that changes it | a class |
| A single instance holding configuration | a module-level constant or a `dataclass` |
| A "Manager"/"Helper"/"Util" class with only static methods | a module of functions |

## Check yourself

1. Why is `self` explicit, and what does `account.deposit(50)` actually call?
2. What happens when you assign to a class attribute through an instance?
3. Why is `items: list[str] = []` at class level a bug?
4. What does `__value` actually do — and what does it not do?
5. When do you convert an attribute into a property?
6. What is the difference between `@classmethod` and `@staticmethod`, and when is each right?
