"""Las etapas del pipeline y el orden en que corren.

El registro vive aquí y no en el CLI porque no es una decisión de la línea de comandos:
cuáles son las etapas y en qué orden van es del pipeline. El CLI y la TUI son dos formas de
invocarlo, y las dos leen esto.

    crawl → parse → changes → export → pdf → compare → bundle

`refresh` queda fuera de la corrida por defecto a propósito: es la **alternativa** a
`crawl`, no su continuación. Encadenar ambas revalidaría contra el servidor las 1.476
páginas recién descargadas, para nada.
"""

from __future__ import annotations

from ..core import Book
from . import bundle, changes, compare, crawl, export, parse, pdf

STAGES = {
    "crawl": crawl.main,
    # Revalida contra el servidor en vez de confiar en el caché: es el modo para detectar
    # cambios, y cuesta casi nada porque casi todo responde 304.
    "refresh": lambda books: crawl.main(books, revalidate=True),
    "parse": parse.main,
    "changes": changes.main,
    "export": export.main,
    # Baja los cinco PDF oficiales de la SP y verifica que cada uno sea el Libro que dice
    # ser. Va antes de `compare` porque es su entrada, y después de `parse` porque la
    # verificación cruza el PDF contra el árbol que extrajo el crawler.
    "pdf": pdf.main,
    # Contrasta el PDF oficial contra lo extraído del portal.
    "compare": compare.main,
    # Empaqueta `output/`: los Markdown y sus índices, listos para entregar.
    "bundle": bundle.main,
}

DEFAULT = ("crawl", "parse", "changes", "export", "pdf", "compare", "bundle")

__all__ = ["DEFAULT", "STAGES", "Book"]
