"""Core logic of the example tool.

Everything the application does lives here, free of I/O concerns, so that it can be
tested without a terminal. The command-line plumbing lives in ``__main__``.
"""


def greet(name: str, shout: bool = False) -> str:
    """Return a greeting for ``name``.

    >>> greet("Anna")
    'Hello, Anna!'
    >>> greet("Anna", shout=True)
    'HELLO, ANNA!'
    >>> greet("   ")
    Traceback (most recent call last):
        ...
    ValueError: name must not be empty
    """
    name = name.strip()
    if not name:
        raise ValueError("name must not be empty")

    message = f"Hello, {name}!"
    return message.upper() if shout else message
