"""Qué se puede borrar del contenido descargado, cuánto pesa y qué cuesta reponerlo.

Va aparte de la TUI para poder probarlo sin levantar una interfaz: es la única operación de
la herramienta que destruye trabajo, y una operación destructiva que solo se puede ejercitar
a mano es una que nadie ejercita.

Cada objetivo declara **cómo se repone**. Es lo que convierte "borrar 371 MB" en una
decisión informada: el entregable se rehace en un segundo, el caché del portal cuesta tres
minutos de red, y el estado no se repone de ninguna manera.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from ..core import ASSETS, BOOKS, DATA, OUTPUT, PDF


@dataclass(frozen=True)
class Target:
    """Un conjunto de rutas que se borran juntas porque se reponen juntas."""

    key: str
    label: str
    paths: list[Path] = field(default_factory=list)
    rebuild: str = ""
    # `True` cuando lo que se borra no se puede volver a obtener de ninguna fuente. Es la
    # diferencia entre perder tiempo y perder información, y la interfaz tiene que decirla.
    irreversible: bool = False

    def size(self) -> int:
        return sum(
            f.stat().st_size
            for path in self.paths
            if path.exists()
            for f in ([path] if path.is_file() else path.rglob("*"))
            if f.is_file()
        )

    def files(self) -> int:
        return sum(
            1
            for path in self.paths
            if path.exists()
            for f in ([path] if path.is_file() else path.rglob("*"))
            if f.is_file()
        )

    def exists(self) -> bool:
        return any(path.exists() for path in self.paths)


def targets() -> list[Target]:
    """Lo que se puede borrar, de lo más barato de reponer a lo más caro.

    El orden es la advertencia: quien recorre la lista de arriba abajo se encuentra primero
    con lo que se rehace solo y al final con lo que no se rehace nunca.
    """
    return [
        Target(
            "output", "Entregable (output/)", [OUTPUT],
            rebuild="uv run python -m to_markdown bundle · ~1 s, sin red",
        ),
        Target(
            "pdf-work", "Comparativa del PDF (data/pdf/)", [PDF],
            rebuild="uv run python -m to_markdown compare · ~24 s, sin red",
        ),
        Target(
            "pdf-source", "PDF oficiales (assets/books/)",
            [b.pdf_source for b in BOOKS] + [BOOKS[0].pdf_source.parent / "http.json"],
            rebuild="uv run python -m to_markdown pdf · ~18 s, 130 MB de red",
        ),
        Target(
            "images", "Figuras descargadas (data/web/*/images/)",
            [b.images for b in BOOKS],
            rebuild="uv run python -m to_markdown crawl · descarga las 1.747 figuras",
        ),
        Target(
            "cache", "Caché del portal (data/web/*/cache/)",
            [b.cache for b in BOOKS],
            rebuild="uv run python -m to_markdown crawl · ~3 min, 1.476 páginas",
        ),
        Target(
            "state", "Historial y línea base (data/web/*/state/, changelog/)",
            [b.state for b in BOOKS] + [b.changelog for b in BOOKS],
            rebuild="NO SE REPONE · se pierde el historial de corridas y la línea base "
                    "contra la que `changes` compara",
            irreversible=True,
        ),
        Target(
            "everything", "TODO el contenido descargado (data/, output/, assets/)",
            # `ASSETS` y no `WEB.parent.parent / "assets"`: esa aritmética acertaba solo
            # mientras `data/` y `assets/` colgaran del mismo sitio en `config.toml`.
            [DATA, OUTPUT, ASSETS],
            rebuild="uv run python -m to_markdown · ~4 min y vuelve a bajar todo, "
                    "menos el historial de corridas, que se pierde",
            irreversible=True,
        ),
    ]


def by_key(key: str) -> Target:
    for target in targets():
        if target.key == key:
            return target
    raise KeyError(key)


def purge(target: Target) -> tuple[int, int]:
    """Borra el objetivo. Devuelve (archivos, bytes) de lo que había.

    Se mide antes de borrar: después no hay nada que medir, y el número es lo que se le
    informa a quien acaba de aprobarlo.
    """
    files, size = target.files(), target.size()
    for path in target.paths:
        if not path.exists():
            continue
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
    return files, size
