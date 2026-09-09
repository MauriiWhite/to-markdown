"""El dominio: qué es un Libro, dónde vive y qué tiene que cumplir el corpus.

No depende de nada del proyecto hacia fuera —ni de la red, ni del disco de trabajo, ni de
la interfaz—. Es la capa sobre la que se apoyan todas las demás.
"""

from __future__ import annotations

from .books import BOOKS, BY_SLUG, Book
from .config import ASSETS, CONFIG, DATA, OUTPUT, PDF, ROOT, WEB
from .guard import check, enforce, metrics, previous_state, record, save_state

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
    "check",
    "enforce",
    "metrics",
    "previous_state",
    "record",
    "save_state",
]
