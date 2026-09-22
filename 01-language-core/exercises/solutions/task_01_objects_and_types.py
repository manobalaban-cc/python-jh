"""Reference solution — chapters 01-02."""

import copy
from decimal import Decimal


def append_without_mutating(items: list[int], value: int) -> list[int]:
    # A new list, built from the old one. `items + [value]` works too; the point is
    # that neither expression touches the caller's list.
    return [*items, value]


def deep_update(matrix: list[list[int]], row: int, col: int, value: int) -> list[list[int]]:
    # A shallow copy would share the inner lists, so mutating result[row] would be
    # visible through the original matrix as well.
    result = copy.deepcopy(matrix)
    result[row][col] = value
    return result


def are_same_object(a: object, b: object) -> bool:
    return a is b


def safe_divide(a: int, b: int) -> float | None:
    try:
        return a / b
    except ZeroDivisionError:
        return None


def floor_and_remainder(a: int, b: int) -> tuple[int, int]:
    # divmod returns exactly this pair. Python floors towards minus infinity and the
    # remainder takes the divisor's sign, which is why -7 // 2 == -4 and -7 % 2 == 1.
    quotient, remainder = divmod(a, b)
    return quotient, remainder


def total_with_vat(prices: list[str], vat_rate: str) -> Decimal:
    # Decimal built from strings: Decimal(19.99) would already carry the binary
    # floating-point error, which is exactly what we are avoiding here.
    net = sum((Decimal(price) for price in prices), start=Decimal("0"))
    return net * (Decimal("1") + Decimal(vat_rate))


def normalise_name(raw: str) -> str:
    # str.split() with no argument splits on any run of whitespace and drops empties,
    # so strip + collapse is a single call.
    return " ".join(part.capitalize() for part in raw.split())


def initials(full_name: str) -> str:
    return "".join(f"{part[0].upper()}." for part in full_name.split())


def format_report_line(name: str, amount: float, share: float) -> str:
    return f"{name:<20}{amount:>12,.2f}{share:>8.1%}"


def join_lines(lines: list[str]) -> str:
    # `result += line` in a loop is O(n^2): strings are immutable, so every step
    # allocates a new string and copies everything seen so far. join is O(n).
    return "\n".join(lines)


def byte_length(text: str, encoding: str = "utf-8") -> int:
    return len(text.encode(encoding))
