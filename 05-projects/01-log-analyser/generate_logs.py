"""Generate a realistic nginx access log for project 1.

    python generate_logs.py --lines 200000 --out access.log --malformed 0.001

Standard library only, so it runs anywhere the project runs.
"""

from __future__ import annotations

import argparse
import gzip
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

PATHS: list[tuple[str, float]] = [
    ("/api/transactions", 0.30),
    ("/api/health", 0.18),
    ("/api/transactions/{id}", 0.12),
    ("/api/reports/monthly", 0.08),
    ("/api/users/{id}/orders", 0.07),
    ("/static/app.js", 0.07),
    ("/static/style.css", 0.06),
    ("/api/login", 0.05),
    ("/api/export", 0.04),
    ("/admin/dashboard", 0.03),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/125.0",
    "curl/8.4.0",
    "python-requests/2.32.3",
    "Prometheus/2.51.0",
]

REFERRERS = ["https://app.example.com/", "https://app.example.com/reports", "-", "-", "-"]

MALFORMED_LINES = [
    "",
    "this is not a log line at all",
    '192.168.1.10 - - [27/Apr/2024:13:59:08 +0200] "GET /api/transactions',
    '- - - [invalid timestamp] "GET / HTTP/1.1" 200 100 "-" "-"',
    '10.0.0.1 - - [27/Apr/2024:13:59:08 +0200] "" 200 0 "-" "-"',
]


def weighted_path(rng: random.Random) -> str:
    """Pick a path, then turn the {id} placeholders into real ids."""
    paths, weights = zip(*PATHS, strict=True)
    path = rng.choices(paths, weights=weights, k=1)[0]

    if "{id}" in path:
        path = path.replace("{id}", str(rng.randint(1, 5000)))
    if path == "/api/transactions" and rng.random() < 0.4:
        path += f"?page={rng.randint(1, 50)}"
    return path


def status_for(path: str, rng: random.Random) -> int:
    """Endpoints fail in different ways, which makes the report interesting."""
    roll = rng.random()
    if path.startswith("/admin"):
        return 200 if roll < 0.70 else (403 if roll < 0.95 else 500)
    if path.startswith("/api/login"):
        return 200 if roll < 0.80 else 401
    if path.startswith("/api/export"):
        return 200 if roll < 0.85 else (504 if roll < 0.95 else 500)
    if roll < 0.955:
        return 200
    if roll < 0.972:
        return 304
    if roll < 0.993:
        return 404
    return 500


def duration_for(path: str, rng: random.Random) -> float:
    """Log-normal-ish durations, with export and reports deliberately slow."""
    base = {
        "/api/export": 2.5,
        "/api/reports/monthly": 0.9,
        "/api/health": 0.004,
        "/static/app.js": 0.008,
        "/static/style.css": 0.006,
    }
    mean = next((value for prefix, value in base.items() if path.startswith(prefix)), 0.12)
    return round(max(0.001, rng.lognormvariate(0, 0.6) * mean), 3)


def client_pool(rng: random.Random, size: int = 400) -> list[str]:
    """A fixed set of client addresses, so "unique clients" means something.

    A few of them are heavy users - that is what real traffic looks like, and it
    gives the analyser something to find.
    """
    pool = [
        f"{rng.choice([10, 192, 172])}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        for _ in range(size)
    ]
    return pool + pool[:20] * 15  # the first 20 addresses appear far more often


def build_line(moment: datetime, rng: random.Random, clients: list[str]) -> str:
    path = weighted_path(rng)
    status = status_for(path, rng)
    method = "POST" if path in {"/api/login", "/api/transactions"} and rng.random() < 0.2 else "GET"
    size = 0 if status in {304, 204} else rng.randint(180, 25_000)
    ip = rng.choice(clients)
    stamp = moment.strftime("%d/%b/%Y:%H:%M:%S %z")

    line = (
        f'{ip} - - [{stamp}] "{method} {path} HTTP/1.1" {status} {size} '
        f'"{rng.choice(REFERRERS)}" "{rng.choice(USER_AGENTS)}"'
    )
    # A small share of lines predate the duration extension being enabled.
    if rng.random() > 0.02:
        line += f" {duration_for(path, rng)}"
    return line


def generate(lines: int, out: Path, malformed: float, seed: int) -> None:
    rng = random.Random(seed)
    start = datetime(2024, 4, 27, tzinfo=timezone(timedelta(hours=2)))
    clients = client_pool(rng)
    opener = gzip.open if out.suffix == ".gz" else open

    with opener(out, "wt", encoding="utf-8", newline="\n") as handle:  # type: ignore[operator]
        moment = start
        for _ in range(lines):
            # Traffic is heavier during the working day: the gap shrinks between 8:00 and 18:00.
            busy = 8 <= moment.hour < 18
            moment += timedelta(seconds=rng.expovariate(1 / (0.35 if busy else 2.0)))

            if rng.random() < malformed:
                handle.write(rng.choice(MALFORMED_LINES) + "\n")
            else:
                handle.write(build_line(moment, rng, clients) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lines", type=int, default=200_000)
    parser.add_argument("--out", type=Path, default=Path("access.log"))
    parser.add_argument("--malformed", type=float, default=0.001, help="share of broken lines")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate(args.lines, args.out, args.malformed, args.seed)
    size_mb = args.out.stat().st_size / 1e6
    print(f"wrote {args.lines:,} lines to {args.out} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
