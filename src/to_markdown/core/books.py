"""El modelo del dominio: un Libro del Compendio y dónde vive cada cosa suya.

Es el único sitio que sabe traducir "el Libro III" a rutas concretas. Que sea un objeto y
no un puñado de `os.path.join` repartidos es lo que hace que agregar un Libro sea agregar
una tabla a `config.toml`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ASSETS, CONFIG, PDF, WEB


@dataclass(frozen=True)
class Book:
    """Un Libro del Compendio, con su carpeta propia y sus cotas de sanidad.

    Cada Libro es un corpus independiente de punta a punta: su caché HTML, sus imágenes,
    su manifiesto, su estado y su entregable viven bajo `data/<slug>/`. La separación es
    exacta, no una convención: se verificó que los 1.478 nodos del árbol cuelgan de un
    único Libro y que ninguna de las 1.743 figuras se comparte entre dos, así que nada se
    duplica ni se pierde al partir.

    Que sean independientes es lo que permite que una regresión en un Libro no arrastre a
    los otros cuatro: las invariantes se evalúan por Libro y abortan solo el suyo.
    """

    slug: str
    pvid: str
    name: str
    pdf_file: str
    min_documents: int
    min_units: int

    @property
    def roman(self) -> str:
        """"Libro III". Es como el PDF se encabeza a sí mismo en cada página."""
        return f"Libro {self.slug.split('-')[1].upper()}"

    @property
    def web(self) -> Path:
        """Carpeta de lo extraído del portal de la SP. Es la casa del pipeline."""
        return WEB / self.slug

    @property
    def pdf(self) -> Path:
        """Carpeta del compendio oficial en PDF: su texto extraído y la comparativa."""
        return PDF / self.slug

    @property
    def pdf_source(self) -> Path:
        """El PDF original tal como lo publica la SP.

        Vive en `assets/` y no en `data/` porque es una **entrada** del pipeline: `compare`
        lo lee y ninguna etapa lo deriva de otra cosa. La etapa `pdf` lo escribe, pero solo
        para traerlo del portal — no lo transforma, y por eso sigue siendo una entrada.

        El nombre es `Book<N>.pdf` (`pdf_file` de `config.toml`) y no el del servidor
        (`fo-propertyvalue-2536.pdf`), que no dice de qué Libro es.
        """
        return ASSETS / "books" / self.pdf_file

    @property
    def cache(self) -> Path:
        return self.web / "cache"

    @property
    def images(self) -> Path:
        return self.web / "images"

    @property
    def markdown(self) -> Path:
        return self.web / "markdown"

    @property
    def changelog(self) -> Path:
        return self.web / "changelog"

    @property
    def state(self) -> Path:
        return self.web / "state"

    def file(self, name: str) -> Path:
        """Un archivo del lado web. Es el lado por defecto porque es el que se recorre."""
        return self.web / name

    @property
    def pdf_images(self) -> Path:
        """Las figuras embebidas en el PDF oficial, extraídas y nombradas por SHA-256."""
        return self.pdf / "images"

    @property
    def pdf_markdown(self) -> Path:
        """Un `.md` por sección del PDF, en espejo de `web/<libro>/markdown/`."""
        return self.pdf / "markdown"

    def file_pdf(self, name: str) -> Path:
        """Un archivo del lado PDF: el texto extraído y la comparativa contra la web."""
        return self.pdf / name

    def mkdirs(self) -> None:
        """Crea los directorios de trabajo del Libro. Idempotente."""
        for path in (self.cache, self.images, self.markdown, self.changelog, self.state,
                     self.pdf, self.pdf_markdown, self.pdf_images):
            path.mkdir(parents=True, exist_ok=True)


BOOKS: list[Book] = [Book(**entry) for entry in CONFIG["books"]]
BY_SLUG: dict[str, Book] = {book.slug: book for book in BOOKS}
