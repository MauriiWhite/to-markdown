"""Las métricas del corpus, leídas de lo que ya está escrito en disco.

Nada se recalcula: abrir el panel no puede costar lo que cuesta `parse`. Cada función
responde por una etapa del pipeline —qué se descargó, qué se procesó, qué cubre el PDF— y
`snapshot` las junta en una sola lectura.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from ..core import BOOKS, OUTPUT, Book
from .sources import amendment_activity, read_json, stage_timings


def download_metrics(book: Book) -> dict:
    """Lo que costó traer este Libro: páginas, imágenes, PDF y cuándo se trajo."""
    http = read_json(book.file("http.json"), {})
    images = read_json(book.file("images.json"), {})
    stamps = sorted(m.get("fetched_at", "") for m in http.values() if m.get("fetched_at"))
    cache = list(book.cache.glob("*.html")) if book.cache.exists() else []
    local_images = list(book.images.iterdir()) if book.images.exists() else []
    return {
        "slug": book.slug,
        "pages": len(cache),
        "cache_bytes": sum(p.stat().st_size for p in cache),
        "images": len(local_images),
        "image_bytes": sum(p.stat().st_size for p in local_images),
        "image_refs": len(images),
        # Sin ETag ni Last-Modified, `refresh` no puede revalidar esa página y la baja
        # entera. Es la métrica que dice cuánto cuesta la próxima actualización.
        "revalidable": sum(1 for m in http.values() if m.get("etag") or m.get("last_modified")),
        "tracked": len(http),
        "pdf_bytes": book.pdf_source.stat().st_size if book.pdf_source.exists() else 0,
        "first_fetch": stamps[0][:10] if stamps else "",
        "last_fetch": stamps[-1][:10] if stamps else "",
    }


def processing_metrics(book: Book) -> dict:
    """Lo que salió del procesamiento: normas, números, figuras y el entregable."""
    documents = read_json(book.file("documents.json"), [])
    sections = read_json(book.file("sections.json"), [])
    folder = OUTPUT / book.slug
    delivered = list(folder.glob("*.md")) if folder.exists() else []
    return {
        "slug": book.slug,
        "documents": len(documents),
        "chars": sum(len(d.get("markdown", "")) for d in documents),
        "units": sum(len(d.get("units", [])) for d in documents),
        "figures": len({f for d in documents for f in d.get("figures", [])}),
        "notes": sum(len(d.get("amendment_notes", [])) for d in documents),
        "topics": len({t for d in documents for t in d.get("topics", [])}),
        "sections": len(sections),
        "delivered": len(delivered),
        "delivered_bytes": sum(p.stat().st_size for p in delivered),
        "min_documents": book.min_documents,
        "min_units": book.min_units,
    }


def coverage_metrics(book: Book) -> dict:
    """La comparativa contra el PDF oficial, que es la medida de si la extracción quedó
    completa. Sin ella el resto de los números dicen cuánto se extrajo, no cuánto falta."""
    report = read_json(book.file_pdf("coverage.json"), {})
    if not report:
        return {"slug": book.slug, "ready": False}
    verdicts = report.get("verdicts", {})
    figures = report.get("figures", {})
    words = sum(d["pdf_words"] for d in report.get("documents", [])) or 1
    return {
        "slug": book.slug,
        "ready": True,
        "aligned": report.get("aligned", 0),
        "documents": report.get("web_documents", 0),
        "unanchored": len(report.get("unanchored", [])),
        "match": verdicts.get("match", 0),
        "reformatted": verdicts.get("reformatted", 0),
        "unaligned": verdicts.get("unaligned", 0),
        "extra_in_pdf": verdicts.get("extra_in_pdf", 0),
        "extra_words": report.get("extra_words_in_pdf", 0),
        "extra_share": report.get("extra_words_in_pdf", 0) / words,
        "pdf_pages": report.get("pdf_pages", 0),
        "figures_shared": figures.get("shared", 0),
        "figures_only_web": figures.get("only_in_web", 0),
        "figures_only_pdf": figures.get("only_in_pdf", 0),
    }


def history(book: Book, field: str = "chars") -> list[float]:
    """La serie de una métrica a lo largo de las corridas.

    Es lo que hace visible la deriva lenta: un descenso gradual de figuras o de unidades no
    dispara ninguna invariante —cada corrida está dentro de la tolerancia de la anterior—
    pero en la serie se ve de inmediato.
    """
    path = book.state / "runs.jsonl"
    if not path.exists():
        return []
    out: list = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                value = json.loads(line).get(field, 0)
            except json.JSONDecodeError:
                continue
            # `at` es una marca de tiempo y se devuelve tal cual; el resto son números.
            out.append(value if field == "at" else float(value or 0))
    return out


def snapshot(books: list[Book] | None = None) -> dict:
    """Todo lo anterior, para los Libros pedidos, en una sola lectura de disco."""
    books = books or BOOKS
    return {
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "download": [download_metrics(b) for b in books],
        "processing": [processing_metrics(b) for b in books],
        "coverage": [coverage_metrics(b) for b in books],
        "history": {b.slug: history(b) for b in books},
        "history_at": {b.slug: history(b, "at") for b in books},
        "amendments": amendment_activity(books),
        "timings": stage_timings(),
    }


# -- gráficos ---------------------------------------------------------------------------
#
# Todos reciben `width` y se dibujan para ese ancho. La TUI le pasa el ancho real del panel
# en cada redibujo, así que los gráficos siguen al tamaño de la terminal sin nada especial.

