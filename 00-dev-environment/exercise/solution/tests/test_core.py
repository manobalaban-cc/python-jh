import pytest

from hello_tool.core import greet


def test_greet_returns_polite_message() -> None:
    assert greet("Anna") == "Hello, Anna!"


def test_greet_shouts_when_asked() -> None:
    assert greet("Anna", shout=True) == "HELLO, ANNA!"


@pytest.mark.parametrize("raw,expected", [("  Anna  ", "Hello, Anna!"), ("Bob", "Hello, Bob!")])
def test_greet_strips_whitespace(raw: str, expected: str) -> None:
    assert greet(raw) == expected


def test_greet_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        greet("   ")
