"""Etapa 2: HTML → documentos jerarquizados en Markdown. Todo determinista, sin modelo.

Lo que sale de aquí no puede depender de una IA: jerarquía, numeración, tablas y notación
matemática se extraen con parser. El modelo se reserva para lo que está encerrado en
píxeles, y ese trabajo no está en esta fase.

La conversión del cuerpo vive en `html_markdown`; aquí queda el documento: sus metadatos,
su jerarquía, sus hashes y el ensamblado del Libro.

Uso:  uv run python -m to_markdown parse
"""

from __future__ import annotations

import hashlib
import json
import re

from ...core import BOOKS, CONFIG, Book
from ...core.guard import enforce, record
from .html import (
    BODY_OPEN,
    BOX_END,
    NOTE,
    BodyToMarkdown,
    clean_text,
    split_units,
)

# Reexportados: son marcadores del HTML de origen y viven en `html_markdown`, pero quien
# lee la etapa los busca aquí.
__all__ = ["BODY_OPEN", "BOX_END", "NOTE", "main", "parse_book", "parse_document"]
from ...infra.monitor import bump

BASE = CONFIG["crawl"]["base_url"]
# Se versiona la salida: un consumidor aguas abajo tiene que poder notar que el formato
# cambió, en vez de descubrirlo por un campo que dejó de existir.
SCHEMA_VERSION = 2


CRUMB_BLOCK = re.compile(r"SP_pa_breadcrum_ruta.*?<p>(.*?)</p>", re.DOTALL)
CRUMB_LINK = re.compile(r"<a ([^>]*)>(.*?)</a>", re.DOTALL)
PVID = re.compile(r"pvid-(\d+)")
CANONICAL = re.compile(r'<p class="margen-abajo-xs small aid-\d+ cid-\d+">(.*?)</p>', re.DOTALL)
TITLE = re.compile(r'<h2 class="titulo[^"]*">(.*?)</h2>', re.DOTALL)
TOPICS = re.compile(r'<p class="voces">Materias asociadas:(.*?)</p>', re.DOTALL)
LINK_TEXT = re.compile(r"<a [^>]*>(.*?)</a>", re.DOTALL)
TAGS = re.compile(r"<[^>]+>")
# La fuente escribe el encabezado de cuatro formas distintas, una de ellas con errata
# ("actualizacón"). Un regex estricto perdería notas reales, así que se tolera la variación.

def body_fragment(html: str) -> str | None:
    """Cuerpo normativo delimitado por su caja. Cortar hasta el fin del archivo arrastraría
    el pie de página; `<!--end-box-->` cierra la caja exactamente."""
    start = html.find(BODY_OPEN)
    if start < 0:
        return None
    end = html.find(BOX_END, start)
    return html[start : end if end > 0 else len(html)]


def breadcrumb(html: str) -> list[dict[str, str]]:
    block = CRUMB_BLOCK.search(html)
    if not block:
        return []
    crumbs = []
    for attributes, title in CRUMB_LINK.findall(block.group(1)):
        text = clean_text(title)
        if not text:
            continue
        pvid = PVID.search(attributes)
        crumbs.append({"pvid": pvid.group(1) if pvid else "", "title": text})
    return crumbs


def _level(crumbs: list[dict[str, str]], title: str) -> dict[str, str]:
    """Asigna Libro / Título / Letra / Capítulo por prefijo, no por posición: no todas las
    normas tienen los cuatro niveles (las hay colgando directo de un Título).

    Va anidado bajo `hierarchy` en la salida porque el nivel Título y el título propio de
    la página son cosas distintas y en plano colisionarían con la misma clave.
    """
    levels: dict[str, str] = {}
    for entry in [*crumbs, {"title": title}]:
        name = entry["title"]
        if name.startswith("Libro "):
            levels.setdefault("book", name)
        elif name.startswith(("Título ", "Titulo ")):
            levels.setdefault("title", name)
        elif name.startswith(("Capítulo ", "Capitulo ")):
            levels.setdefault("chapter", name)
        elif re.match(r"^(Letra )?[A-Z](\.\d+)?[.\s]", name):
            levels.setdefault("letter", name)
    return levels


def parse_document(pvid: str, html: str, images: dict[str, str]) -> dict | None:
    body = body_fragment(html)
    if body is None:
        return None

    title_match = TITLE.search(html)
    title = clean_text(title_match.group(1)) if title_match else ""
    canonical = CANONICAL.search(html)
    topics_block = TOPICS.search(html)
    crumbs = breadcrumb(html)

    converter = BodyToMarkdown(images)
    converter.feed(TOPICS.sub("", body))
    markdown = converter.result()

    path = clean_text(canonical.group(1)) if canonical else " > ".join(c["title"] for c in crumbs)
    citation = f"{path}, {title}" if title and title not in path else path

    return {
        "pvid": pvid,
        "url": f"{BASE}w3-propertyvalue-{pvid}.html",
        "title": title,
        "path": path,
        "citation": citation,
        "breadcrumb": crumbs,
        "hierarchy": _level(crumbs, title),
        "topics": [clean_text(m) for m in LINK_TEXT.findall(topics_block.group(1))] if topics_block else [],
        "amendment_notes": converter.notes,
        "figures": list(dict.fromkeys(converter.figures)),
        "markdown": markdown,
        "units": split_units(markdown, pvid, citation),
        # Dos hashes distintos a propósito. `source` es del HTML de origen y responde
        # "¿cambió la norma?"; `content` es de nuestro Markdown y responde "¿cambió nuestra
        # salida?". Con uno solo, cada mejora al parser se vería como si 1.198 normas
        # hubieran cambiado, y el changelog dejaría de valer.
        "source_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "content_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        "schema_version": SCHEMA_VERSION,
    }


def parse_book(book: Book) -> list[dict]:
    """Parsea un Libro completo y escribe su entregable. Aborta solo este Libro si sale
    degradado: los otros cuatro conservan la salida de la corrida anterior."""
    book.mkdirs()
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    images_path = book.file("images.json")
    images = json.loads(images_path.read_text(encoding="utf-8")) if images_path.exists() else {}

    documents = []
    # En orden de lectura y por "tiene cuerpo", no por "es hoja": ver `crawl.tree_order` y
    # `has_body`. El orden importa porque es el del Compendio impreso.
    for pvid in manifest["documents"]:
        html = (book.cache / f"{pvid}.html").read_text(encoding="utf-8")
        document = parse_document(pvid, html, images)
        if document:
            documents.append(document)
            bump("documents")
            bump("units", len(document["units"]))

    # Se valida ANTES de escribir: si el Libro salió degradado, el anterior sobrevive.
    enforce(book, documents, manifest)

    book.file("documents.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    record(book, documents)
    return documents


def main(books: list[Book] | None = None) -> None:
    totals = {"documents": 0, "chars": 0, "units": 0, "figures": 0, "notes": 0}
    for book in books or BOOKS:
        documents = parse_book(book)
        figures = {f for d in documents for f in d["figures"]}
        chars = sum(len(d["markdown"]) for d in documents)
        units = sum(len(d["units"]) for d in documents)
        notes = sum(len(d["amendment_notes"]) for d in documents)
        print(
            f"{book.slug:10} documents: {len(documents):4} | {chars:9,} chars | "
            f"units: {units:5,} | figures: {len(figures):4} | notes: {notes:4}"
        )
        missing = sum(d["markdown"].count("[[FIG-MISSING:") for d in documents)
        if missing:
            print(f"{'':10} WARNING: {missing} images not downloaded (marked FIG-MISSING, not lost)")
        totals["documents"] += len(documents)
        totals["chars"] += chars
        totals["units"] += units
        totals["figures"] += len(figures)
        totals["notes"] += notes

    if len(books or BOOKS) > 1:
        print(
            f"{'TOTAL':10} documents: {totals['documents']:4} | {totals['chars']:9,} chars | "
            f"units: {totals['units']:5,} | figures: {totals['figures']:4} | "
            f"notes: {totals['notes']:4}"
        )


if __name__ == "__main__":
    main()
