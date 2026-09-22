# 03 — Control flow

## Blocks are defined by indentation

There are no braces and no semicolons. Indentation **is** the syntax:

```python
if x > 0:
    print("positive")
    print("still inside the if")
print("outside")
```

- 4 spaces per level (PEP 8), never tabs; mixing them raises `TabError`.
- The colon at the end of the header line is mandatory.
- An empty block is not allowed — use `pass` (or `...`) as a placeholder.

This is not cosmetic: a misplaced indentation changes program semantics without any error
message. Let the formatter handle it, and configure your editor to show whitespace.

## `if` / `elif` / `else`

```python
if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
else:
    grade = "C"
```

There is no `switch`; `elif` chains or `match` (below) replace it.

### Conditional expression (the ternary)

```python
label = "large" if amount > 1000 else "small"
```

Note the word order: *value* `if` *condition* `else` *other value*. It reads like English and
trips up everyone used to `cond ? a : b` for about a week.

### Chained comparisons

```python
if 0 <= index < len(items):       # this actually works, and means what it looks like
    ...

if a == b == c:                   # all three equal
    ...
```

This is genuinely nicer than `0 <= index && index < len(items)`, and it evaluates `index` once.

### Boolean operators

`and`, `or`, `not` — words, not symbols. They **short-circuit** and, importantly, they
**return one of the operands**, not a boolean:

```python
name = user_input or "anonymous"      # a common idiom for defaults
value = cache and cache.get("key")    # None/False-safe chaining
```

Careful: `or` treats every falsy value the same, so `0 or 10` is `10`. When `0` is legitimate,
use an explicit `is None` check (see the previous chapter).

The walrus operator assigns inside an expression:

```python
if (n := len(items)) > 10:
    print(f"too many: {n}")

while (line := f.readline()):
    process(line)
```

Use it sparingly — mostly to avoid computing something twice.

## `for` — there is no C-style loop

Python's `for` is a **for-each** over an iterable. There is no `for (int i = 0; i < n; i++)`.

```python
for item in items:
    print(item)

for i in range(5):            # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):     # 2, 4, 6, 8
    print(i)
```

`range` is not a list: it is a lazy sequence that generates values on demand, so
`range(10_000_000)` costs almost no memory.

### Iterating the way Python wants you to

```python
# INDEX-BASED - carried over from other languages, avoid
for i in range(len(names)):
    print(names[i])

# IDIOMATIC
for name in names:
    print(name)

# When you genuinely need the index
for i, name in enumerate(names, start=1):
    print(f"{i}. {name}")

# Two sequences in parallel
for name, score in zip(names, scores, strict=True):
    print(name, score)

# Dictionary
for key, value in mapping.items():
    print(key, value)

# Reversed / sorted
for name in reversed(names): ...
for name in sorted(names, key=len): ...
```

`zip(..., strict=True)` (3.10+) raises if the sequences have different lengths — without it,
`zip` silently stops at the shortest, which hides bugs.

### `for ... else` and `while ... else`

A Python oddity worth knowing, because it shows up in real code:

```python
for item in items:
    if item.is_valid():
        chosen = item
        break
else:
    # runs only if the loop finished WITHOUT break
    raise ValueError("no valid item found")
```

Read `else` here as "no break". It replaces the `found = False` flag pattern.

## `while`

```python
while queue:
    item = queue.pop()
    process(item)
```

No `do...while`; emulate it with `while True:` plus a `break` at the bottom.

`break` and `continue` work as expected. There is no labelled break for nested loops — extract
the loops into a function and `return` instead.

## `match` — structural pattern matching (3.10+)

This is **not** a `switch`. It matches against the *structure* of a value, the way Scala's or
Rust's pattern matching does.

```python
match command.split():
    case ["quit"]:
        return None
    case ["load", filename]:                 # binds filename
        return load(filename)
    case ["save", filename, *options]:       # binds the rest as a list
        return save(filename, options)
    case [action, *_] if action.startswith("_"):   # guard
        raise ValueError("private action")
    case _:                                  # default
        raise ValueError(f"unknown command: {command}")
```

It matches dicts and objects too:

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        handle_click(x, y)
    case {"type": "key", "code": code}:
        handle_key(code)

match shape:
    case Circle(radius=r):
        return 3.14159 * r * r
    case Rectangle(width=w, height=h):
        return w * h
```

**Trap:** a bare name in a `case` is a *capture pattern*, not a comparison. `case ERROR:`
matches everything and binds it to `ERROR`. To compare against a constant, qualify it:
`case Status.ERROR:` or `case "error":`.

When a simple value dispatch is all you need, an `elif` chain or a dict lookup is often clearer:

```python
handlers = {"click": handle_click, "key": handle_key}
handler = handlers.get(event_type, handle_unknown)
handler(event)
```

## The loop that does not exist: `do`, `goto`, labelled break

| Pattern from elsewhere | Python equivalent |
|---|---|
| `for (int i = 0; ...)` | `for i in range(n)` |
| `foreach (x in xs)` | `for x in xs` |
| `do { } while (c)` | `while True: ... if not c: break` |
| `switch` | `match`, `elif` chain, or a dict of handlers |
| labelled `break` | extract to a function and `return` |
| `i++` | `i += 1` (there is no `++`) |

## Check yourself

1. Why is indentation a correctness issue and not a style issue in Python?
2. What does `name = user_input or "anonymous"` do, and when is it wrong?
3. What does `enumerate(items, start=1)` return?
4. When does the `else` branch of a `for` loop execute?
5. Why is `zip(a, b, strict=True)` safer than plain `zip`?
6. Why does `case ERROR:` in a `match` statement match everything?
