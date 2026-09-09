"""De dónde salen las series temporales: la duración de las etapas y la actividad
normativa que declaran las propias notas del Compendio.

Van juntas porque son las dos únicas fuentes con fecha del proyecto, y aparte de las
métricas porque una métrica se lee de un JSON y esto hay que extraerlo.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime

from ..core import BOOKS, DATA, Book

MONTHS = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|"
    "octubre|noviembre|diciembre"
)
# Las notas de actualización fechan la modificación: "…por la Norma de Carácter General
# Nº 31, de fecha 29 de diciembre de 2011". Es la ÚNICA serie temporal real del corpus:
# el `Last-Modified` del servidor no sirve —el CMS reguardó las 1.476 páginas el mismo día
# y todas dicen 2026—, pero la norma sí declara cuándo la cambiaron.
AMENDMENT_DATE = re.compile(
    rf"de fecha\s+(\d{{1,2}})\s+de\s+({MONTHS})\s+de\s+(\d{{4}})", re.IGNORECASE
)
NCG_NUMBER = re.compile(r"Norma de Car[áa]cter General\s+N[°ºo]?\s*(\d+)", re.IGNORECASE)
# El corpus trae erratas de tipeo en los años ("1012" por "2012", 2 casos). Fuera de este
# rango no es actividad normativa, es un dedo que se resbaló.
YEAR_RANGE = (1980, 2100)

# Duración de cada etapa, por corrida. Se escribe fuera de `data/web/<libro>/` porque una
# etapa puede abarcar varios Libros y el tiempo es de la corrida, no del Libro.
TIMINGS = DATA / "timings.jsonl"

# Octavos de bloque. Permiten una resolución de 1/8 de columna, que en una barra de 20
# columnas es la diferencia entre ver cinco escalones y ver una proporción real.

def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default



def record_stage(name: str, books: list[Book], seconds: float, ok: bool) -> None:
    """Anota cuánto tardó una etapa. Lo llaman la CLI y la TUI, para que la serie sea la
    misma se haya corrido por donde se haya corrido."""
    TIMINGS.parent.mkdir(parents=True, exist_ok=True)
    with TIMINGS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "stage": name,
            "books": [b.slug for b in books],
            "seconds": round(seconds, 2),
            "ok": ok,
        }, ensure_ascii=False) + "\n")


def stage_timings(limit: int = 400) -> list[dict]:
    """Las últimas corridas de cada etapa, en orden cronológico."""
    if not TIMINGS.exists():
        return []
    out: list[dict] = []
    for line in TIMINGS.read_text(encoding="utf-8").splitlines()[-limit:]:
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def amendment_activity(books: list[Book] | None = None) -> dict[str, Counter]:
    """Cuántas modificaciones normativas declara el corpus por año, y por qué NCG.

    Es la tendencia que el Compendio tiene de verdad: no cuánto extrajimos nosotros, sino
    cuánto cambió la norma y cuándo. Sale de las propias notas de actualización, que la SP
    escribe pegadas al número que modifican.
    """
    years: Counter[int] = Counter()
    ncg: Counter[int] = Counter()
    by_book: dict[str, Counter] = {}
    undated = 0
    for book in books or BOOKS:
        notes = [
            note
            for document in read_json(book.file("documents.json"), [])
            for note in document.get("amendment_notes", [])
        ]
        local: Counter[int] = Counter()
        for note in notes:
            found = AMENDMENT_DATE.search(note)
            year = int(found.group(3)) if found else None
            if year and YEAR_RANGE[0] <= year <= YEAR_RANGE[1]:
                years[year] += 1
                local[year] += 1
            else:
                undated += 1
            for match in NCG_NUMBER.finditer(note):
                ncg[int(match.group(1))] += 1
        by_book[book.slug] = local
    return {"years": years, "ncg": ncg, "by_book": by_book, "undated": undated}


