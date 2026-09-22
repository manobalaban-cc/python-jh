# 01 — The object model: names, references, mutability

This is the most important chapter of the course. Understand it, and 80% of Python's later
"weirdness" explains itself.

## Everything is an object

In Python **every value is an object**: `42`, `"hi"`, `None`, functions, classes, even modules.
There are no primitive types, no `int` / `Integer` split as in Java.

```python
print((42).__class__)        # <class 'int'>
print("hi".upper)            # <built-in method upper of str object>
print(len.__class__)         # <class 'builtin_function_or_method'>

def f(): ...
f.author = "Anna"            # you can even attach attributes to a function
print(f.author)              # Anna
```

It also means **functions are values**: they can be passed around, returned, stored in a list.
This is what "first-class functions" means, and Python style leans on it heavily.

## Names are labels, not boxes

This is the key mental shift coming from Java, C# or C.

**Not how it works:** "the variable `x` is a box holding 42."
**How it works:** "the object `42` exists in memory, and the name `x` points at it."

```python
a = [1, 2, 3]
b = a            # NOT a copy! b points at the same list
b.append(4)
print(a)         # [1, 2, 3, 4]   <- "a" changed too
```

This is exactly what Java does with reference types — the difference is that in Python there
are **no exceptions to the rule**: no primitives, so *every* assignment binds a reference.

`id()` reveals object identity (in CPython, the memory address):

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(id(a) == id(b))    # True  - the same object
print(id(a) == id(c))    # False - two distinct objects
print(a == c)            # True  - but equal in value
print(a is c)            # False
```

### `is` versus `==`

| Operator | Question it asks |
|---|---|
| `==` | are the **values** equal (calls `__eq__`) |
| `is` | is it the **same object** (identity, `id()` comparison) |

**Rule:** use `is` only for `None`, `True`, `False` and sentinel objects:

```python
if result is None:      # correct
if result == None:      # works, but not idiomatic, and a custom __eq__ can lie
```

### Small integers and the `is` trap

```python
a = 256
b = 256
print(a is b)      # True

a = 257
b = 257
print(a is b)      # False (when run as a script)
```

Not a bug: CPython pre-creates and shares the integers from `-5` to `256` (*interning*). Short,
identifier-like strings get the same treatment. This is an **implementation detail** you must
never rely on — which is precisely why we do not use `is` to compare values.

## Mutable and immutable

| Immutable | Mutable |
|---|---|
| `int`, `float`, `complex`, `bool` | `list` |
| `str`, `bytes` | `dict` |
| `tuple` | `set` |
| `frozenset` | `bytearray` |
| `None` | your own classes (by default) |

An immutable object **cannot be changed**; what happens instead is that a new object is created:

```python
s = "hi"
print(id(s))
s += " there"      # does NOT modify the string: builds a new one and rebinds s
print(id(s))       # different value
```

That is why concatenating strings in a loop is slow (a new object plus a copy on every step),
and why we use `"".join(parts)` instead.

### Why this matters in practice

**1. Function calls.** Python passes arguments "by object reference": the function receives the
reference.

```python
def add_item(items: list[int]) -> None:
    items.append(99)          # mutates the CALLER's list!

def rebind(items: list[int]) -> None:
    items = [0, 0, 0]         # only rebinds the local name; the caller is untouched

numbers = [1, 2]
add_item(numbers)
print(numbers)                # [1, 2, 99]
rebind(numbers)
print(numbers)                # [1, 2, 99]  - unchanged
```

**2. Copying.** When you really need a copy:

```python
import copy

original = [[1, 2], [3, 4]]

shallow = original.copy()        # or list(original), or original[:]
deep = copy.deepcopy(original)

shallow[0].append(99)
print(original)                  # [[1, 2, 99], [3, 4]]  <- the inner list is shared!

deep[1].append(99)
print(original)                  # unchanged
```

A **shallow copy** creates a new container pointing at the same elements. A **deep copy**
recursively copies everything — expensive, so only when you must.

**3. Dictionary keys and set members.** Only **hashable** objects can be keys, and mutable
types are not hashable by default:

```python
d = {}
d[(1, 2)] = "ok"         # tuple: fine
d[[1, 2]] = "boom"       # TypeError: unhashable type: 'list'
```

The reason: a hash value must stay constant for the object's lifetime, or the dict would lose
track of the entry. Immutable types guarantee that.

## Garbage collection

CPython uses **reference counting**: every object knows how many references point at it, and it
is freed the moment that count hits zero. On top of that a **cycle detector** runs, because
reference counting cannot reclaim reference cycles.

Practical consequences:

- Cleanup is **more deterministic** than on the JVM: when the last reference to a file object
  disappears, the file is closed. Do **not** rely on it though (PyPy behaves differently) —
  that is what the `with` statement is for.
- A reference cycle (`a.b = b; b.a = a`) does not leak, it just frees later.
- `del x` does **not** delete an object, it removes a name. The object goes away when nothing
  refers to it any more.

## Dynamically but strongly typed

Two axes that are often conflated:

|  | Static | Dynamic |
|---|---|---|
| **Strong** | Java, C#, Rust | **Python**, Ruby |
| **Weak** | C | JavaScript, PHP |

- **Dynamic**: the *name* carries no type, the *object* does. The same name can be an `int`
  today and a `str` tomorrow (though good code does not do that).
- **Strong**: types do not convert silently. `1 + "2"` is a `TypeError` in Python, while
  JavaScript happily gives `"12"`.

```python
x = 42
x = "now a string"     # allowed (dynamic)
1 + "2"                # TypeError (strong)
```

Type annotations (`x: int`) change **nothing** at runtime — they exist for static checkers. See
[02-oop-and-stdlib/05-type-hints.md](../02-oop-and-stdlib/05-type-hints.md).

## Check yourself

1. What happens in memory on `b = a` when `a` is a list?
2. When do you use `is` and when `==`? Why?
3. Why is a list rejected as a dict key?
4. What is the difference between a shallow and a deep copy? When do you need which?
5. Why does `x = 5` inside a function not affect the caller, while `x.append(5)` does?
6. Is Python strongly or weakly typed? Give the example that settles it.
