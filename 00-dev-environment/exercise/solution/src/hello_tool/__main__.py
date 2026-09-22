"""Command-line entry point.

Runs on ``python -m hello_tool`` and via the ``hello-tool`` script registered in
``[project.scripts]``.
"""

import sys

from hello_tool.core import greet


def main() -> int:
    """Entry point. Returns the process exit code."""
    args = sys.argv[1:]
    if not args:
        print("usage: hello-tool NAME [--shout]", file=sys.stderr)
        return 2

    shout = "--shout" in args
    names = [a for a in args if not a.startswith("--")]

    try:
        print(greet(names[0], shout=shout))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
