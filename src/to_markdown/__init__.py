"""to-markdown · convierte fuentes documentales a Markdown verificable.

La primera fuente —y la que define el diseño— es el **Compendio de Normas del Sistema de
Pensiones** de la Superintendencia de Pensiones de Chile.

Este módulo es la fachada del paquete: reexporta el modelo y las rutas para que el resto
del código escriba `from .. import Book` sin tener que saber si el modelo vive en
`core/books.py` o en otro lado.
"""

from __future__ import annotations

from .core.books import BOOKS, BY_SLUG, Book
from .core.config import ASSETS, CONFIG, DATA, OUTPUT, PDF, ROOT, WEB

__all__ = [
    "ASSETS",
    "BOOKS",
    "BY_SLUG",
    "CONFIG",
    "DATA",
    "OUTPUT",
    "PDF",
    "ROOT",
    "WEB",
    "Book",
]
