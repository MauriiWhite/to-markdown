"""Corre el pipeline en orden. Idempotente: cada etapa reusa su caché.

    uv run python -m to_markdown tui                    panel de control (recomendado)
    uv run python -m to_markdown                        todas las etapas, los cinco Libros
    uv run python -m to_markdown parse export           solo esas etapas
    uv run python -m to_markdown --book book-iii       solo ese Libro
    uv run python -m to_markdown export -b book-iii -b book-iv
"""

from __future__ import annotations

import argparse
import time

from . import analytics
from .core import BOOKS, BY_SLUG, Book
from .stages import DEFAULT, STAGES

TUI = "tui"


def parse_args(argv: list[str] | None = None) -> tuple[list[str], list[Book]]:
    parser = argparse.ArgumentParser(prog="to-markdown", description=__doc__.splitlines()[0])
    parser.add_argument(
        "stages", nargs="*", metavar="ETAPA",
        help=f"stages to run, in order. Default: {', '.join(DEFAULT)}. "
             f"Also available: {', '.join(k for k in STAGES if k not in DEFAULT)}. "
             f"Use `tui` to open the dashboard instead.",
    )
    parser.add_argument(
        "--book", "-b", action="append", metavar="SLUG", dest="books",
        help="run only this book; repeatable. Defaults to all five.",
    )
    args = parser.parse_args(argv)

    for name in args.stages:
        if name == TUI:
            if len(args.stages) > 1:
                parser.error(f"`{TUI}` opens the dashboard; it cannot be combined with stages")
            continue
        if name not in STAGES:
            parser.error(f"unknown stage: {name}. Options: {', '.join(STAGES)}")
    for slug in args.books or []:
        if slug not in BY_SLUG:
            parser.error(f"unknown book: {slug}. Options: {', '.join(BY_SLUG)}")

    # Se devuelven en el orden de `config.toml`, no en el que los escribió quien invoca:
    # el orden del Compendio es I…V y así salen los informes.
    books = [b for b in BOOKS if not args.books or b.slug in args.books]
    return args.stages or list(DEFAULT), books


def main(argv: list[str] | None = None) -> None:
    stages, books = parse_args(argv)
    # La TUI no es una etapa: es la otra forma de invocar las mismas etapas. Se despacha
    # aquí y no en `STAGES` para que no aparezca como algo encadenable a `parse export`.
    if stages == [TUI]:
        from . import tui
        tui.main(books)
        return
    if len(books) < len(BOOKS):
        print(f"only: {', '.join(b.slug for b in books)}")
    for name in stages:
        print(f"\n=== {name} ===", flush=True)
        started = time.perf_counter()
        ok = False
        try:
            STAGES[name](books)
            ok = True
        finally:
            # Se anota también cuando la etapa aborta: una corrida que se detuvo es un
            # dato de la serie, no un hueco. `finally` para que un `SystemExit` de `guard`
            # no se lleve la medición consigo.
            analytics.record_stage(name, books, time.perf_counter() - started, ok)


if __name__ == "__main__":
    main()
