"""Panel de control del pipeline.

Es la forma principal de operar la herramienta. La CLI hace exactamente lo mismo y sigue
disponible para scripts, pero obliga a recordar los nombres de las etapas, en qué orden van
y qué escribe cada una. Aquí se ven.

Este módulo es la **fachada**: expone lo que se usa desde fuera y esconde en qué archivo
está cada cosa. Sirve además para algo concreto — importar `to_markdown.tui` no puede
exigir `textual`, porque el pipeline entero tiene que poder correr en un `cron` sin
terminal. Por eso lo que necesita la biblioteca de interfaz se importa dentro de
`build_app()` y no aquí arriba.

Uso:  uv run python -m to_markdown tui
"""

from __future__ import annotations

from ..core import Book
from .content import (
    ANALYTICS,
    DEFAULT_STAGES,
    DRAWERS,
    HELP,
    METRICS,
    NEEDS_NETWORK,
    PANELS,
    PERFORMANCE,
    REFRESH_STAGES,
    SAMPLE_SECONDS,
    STAGE_HELP,
    STAGE_WRITES,
    TONE_LINE,
    corpus_state,
    performance_lines,
    state_lines,
)
from .runner import Tee, run_stages

MISSING = (
    "the TUI needs `textual`. It ships with the project:  uv sync\n"
    "The pipeline itself runs without it:  uv run python -m to_markdown"
)

# Alias histórico: las pruebas y el código anterior lo nombran así.
_Tee = Tee

__all__ = [
    "ANALYTICS",
    "DEFAULT_STAGES",
    "DRAWERS",
    "HELP",
    "METRICS",
    "MISSING",
    "NEEDS_NETWORK",
    "PANELS",
    "PERFORMANCE",
    "REFRESH_STAGES",
    "SAMPLE_SECONDS",
    "STAGE_HELP",
    "STAGE_WRITES",
    "TONE_LINE",
    "Tee",
    "build_app",
    "corpus_state",
    "main",
    "performance_lines",
    "run_stages",
    "state_lines",
]


def build_app():
    """La clase del panel. Importa `textual` aquí dentro, no al cargar el módulo.

    Es lo que permite que `to_markdown.tui` se importe —para leer `STAGE_HELP`, o para
    probar `state_lines`— en un entorno sin la biblioteca de interfaz instalada.
    """
    try:
        import textual  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(MISSING) from exc
    # El import del panel va FUERA del `try`: atrapar cualquier `ImportError` aquí
    # enmascaraba errores reales del propio panel como "falta textual", que es un
    # diagnóstico falso y caro de perseguir.
    from .app import Dashboard

    return Dashboard


def main(books: list[Book] | None = None) -> None:
    """Abre la TUI. Con `-b`, arranca con solo esos Libros marcados."""
    build_app()([b.slug for b in books] if books else None).run()


if __name__ == "__main__":
    main()
