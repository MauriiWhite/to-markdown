"""Invariantes estructurales del corpus, evaluadas por Libro. La red que impide
degradarse en silencio.

El peor fallo de un scraper no es caerse: es seguir corriendo y devolver menos. Si mañana
la Superintendencia cambia su CMS y `#cuerpo_documento` deja de existir, el pipeline
extraería documentos vacíos y los escribiría encima de los buenos sin decir nada.

Por eso las salidas se validan antes de escribirse y, ante una regresión, se aborta
conservando el corpus anterior. Fallar cerrado, no abierto.

Se evalúa **por Libro** y no sobre el total por dos razones. Una: un total holgado esconde
un Libro roto — perder los 124 documentos del Libro I deja 1.074, todavía sobre cualquier
cota global razonable. Dos: cada Libro tiene su propia carpeta y su propio estado, así que
un Libro degradado aborta solo el suyo y los otros cuatro conservan su salida buena.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from .books import Book

# Cotas por Libro medidas sobre el corpus real (agosto 2026): están en `config.toml`,
# junto al Libro al que pertenecen. Aquí quedan solo las que son proporciones y no dependen
# del tamaño del Libro.
MIN_WITH_PATH = 0.95
# "Con contenido" es texto **o** figura: 73 anexos del corpus son legítimamente una sola
# imagen (formularios), y contarlos como degradados haría que la invariante llore lobo.
MIN_WITH_CONTENT = 0.98
# Vacíos de verdad: 6 capítulos que la SP publica sin cuerpo (4321-4324, 4327, 4328), los
# seis en el Libro III. Verificado contra la fuente, no es un fallo del parser. Que este
# número crezca —en cualquier Libro— sí lo sería.
MAX_EMPTY = 10
# Tolerancia de variación de volumen entre corridas. El Compendio cambia ~160 páginas al
# año: una corrida que mueva más del 25% del texto de un Libro no es una actualización
# normativa.
MAX_TEXT_DRIFT = 0.25

OVERRIDE = "TO_MARKDOWN_FORCE"


def previous_state(book: Book) -> list[dict] | None:
    path = book.state / "documents.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save_state(book: Book, documents: list[dict]) -> None:
    book.state.mkdir(parents=True, exist_ok=True)
    (book.state / "documents.json").write_text(
        json.dumps(documents, ensure_ascii=False), encoding="utf-8"
    )


def metrics(documents: list[dict]) -> dict:
    """Salud del corpus en una línea. Se acumula por corrida para que la deriva sea
    visible: un descenso lento de figuras o unidades no dispara ninguna invariante, pero
    en la serie se ve."""
    return {
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "documents": len(documents),
        "chars": sum(len(d.get("markdown", "")) for d in documents),
        "units": sum(len(d.get("units", [])) for d in documents),
        "figures": len({f for d in documents for f in d.get("figures", [])}),
        "notes": sum(len(d.get("amendment_notes", [])) for d in documents),
        "empty": sum(
            1 for d in documents if not d.get("markdown", "").strip() and not d.get("figures")
        ),
    }


def record(book: Book, documents: list[dict]) -> None:
    book.state.mkdir(parents=True, exist_ok=True)
    with (book.state / "runs.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"book": book.slug, **metrics(documents)}, ensure_ascii=False) + "\n")


def check(book: Book, documents: list[dict], manifest: dict | None = None) -> list[str]:
    """Invariantes violadas por este Libro. Lista vacía significa Libro sano."""
    problems: list[str] = []
    total = len(documents)

    if total < book.min_documents:
        problems.append(f"only {total} documents, expected >={book.min_documents}")
    if not total:
        return problems

    if manifest:
        # El manifiesto de un Libro tiene exactamente una raíz, y es la suya. Si trae otra,
        # el crawl se salió de su subárbol y la carpeta ya no contiene lo que dice.
        roots = [p for p, n in manifest["nodes"].items() if n["parent"] is None]
        if roots != [book.pvid]:
            problems.append(f"unexpected roots in manifest: {roots}, expected [{book.pvid}]")

    with_path = sum(1 for d in documents if d.get("path")) / total
    if with_path < MIN_WITH_PATH:
        problems.append(f"only {with_path:.0%} have hierarchy, expected >={MIN_WITH_PATH:.0%}")

    with_content = sum(
        1 for d in documents if len(d.get("markdown", "")) > 100 or d.get("figures")
    ) / total
    if with_content < MIN_WITH_CONTENT:
        problems.append(
            f"only {with_content:.1%} have content, expected >={MIN_WITH_CONTENT:.0%}"
        )

    empty = sum(1 for d in documents if not d.get("markdown", "").strip() and not d.get("figures"))
    if empty > MAX_EMPTY:
        problems.append(f"{empty} empty documents, at most {MAX_EMPTY} tolerated")

    units = sum(len(d.get("units", [])) for d in documents)
    if units < book.min_units:
        problems.append(f"only {units} numbered units, expected >={book.min_units}")

    previous = previous_state(book)
    if previous:
        before = sum(len(d.get("markdown", "")) for d in previous)
        now = sum(len(d.get("markdown", "")) for d in documents)
        if before and abs(now - before) / before > MAX_TEXT_DRIFT:
            problems.append(
                f"text volume changed {(now - before) / before:+.0%} "
                f"({before:,} -> {now:,} chars), over the {MAX_TEXT_DRIFT:.0%} tolerated"
            )
    return problems


def enforce(book: Book, documents: list[dict], manifest: dict | None = None) -> None:
    """Aborta si el Libro está degradado, sin tocar su salida anterior."""
    problems = check(book, documents, manifest)
    if not problems:
        return
    detail = "\n".join(f"  - {p}" for p in problems)
    if os.environ.get(OVERRIDE):
        print(f"WARNING: invariants violated in {book.slug}, continuing because {OVERRIDE}=1:\n{detail}")
        return
    raise SystemExit(
        f"\nDEGRADED CORPUS in {book.name} ({book.slug}) — nothing was written:\n{detail}\n\n"
        f"The site may have changed structure. Check the selectors in parse.py against a\n"
        f"real page before continuing. If the change is legitimate: {OVERRIDE}=1 uv run ...\n"
    )
