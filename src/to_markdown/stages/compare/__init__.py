"""Etapa 6: alinea el compendio oficial en PDF contra lo extraído del portal.

La SP publica lo mismo dos veces: capítulo por capítulo en su portal (`data/web/`) y como
un documento único en PDF (`assets/books/`). Esta etapa responde qué trae uno que el otro
no, que es la única forma de saber si la extracción quedó completa.

Para que la comparación signifique algo, el PDF se lleva **al mismo orden y a la misma
segmentación que la web**: se recorre el árbol del Libro en profundidad —el orden en que
el propio CMS lista sus capítulos, que es el orden en que los imprime— y cada documento se
ancla en el texto del PDF avanzando siempre hacia adelante.

Comparar sin alinear daría un diff de 9 MB contra 10 MB, ilegible e inaccionable. Alineado,
la pregunta se contesta por capítulo: "el N° 3 del Capítulo II está en el PDF y no en la
web".

Este módulo es la fachada: la alineación —que es lo propio de la etapa— más lo que se
expone hacia fuera. La medición vive en `coverage`, la extracción en `text` y `figures`, y
lo que se escribe en `render`.

Uso:  uv run python -m to_markdown compare
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime

from ...core import BOOKS, Book
from .coverage import (
    BODY_ANCHOR,
    FIGURE_MARKER,
    HEADING_GAP,
    SHINGLE,
    WORD,
    compare_document,
    lexical_coverage,
    occurrences,
    runs,
    shingles,
    verdict,
)
from .extract import (
    canonical,
    clean_pages,
    compare_figures,
    extract_images,
    extract_text,
    images_by_page,
    normalize,
    tree_order,
    visual_key,
)
from .render import render, to_markdown, write_markdown

__all__ = [
    "BODY_ANCHOR",
    "FIGURE_MARKER",
    "HEADING_GAP",
    "SHINGLE",
    "WORD",
    "align",
    "canonical",
    "clean_pages",
    "compare_document",
    "compare_figures",
    "extract_images",
    "extract_text",
    "images_by_page",
    "lexical_coverage",
    "main",
    "normalize",
    "occurrences",
    "render",
    "runs",
    "shingles",
    "to_markdown",
    "tree_order",
    "verdict",
    "visual_key",
    "write_markdown",
]

def align(book: Book) -> dict:
    """Lleva el PDF al orden y la segmentación de la web, y compara capítulo por capítulo."""
    book.mkdirs()
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    web = {d["pvid"]: d for d in json.loads(book.file("documents.json").read_text(encoding="utf-8"))}
    order = [pvid for pvid in tree_order(manifest) if pvid in web]

    text, pages, toc_lines = clean_pages(extract_text(book), book)
    figures = images_by_page(extract_images(book))
    # Mismo texto en minúsculas: se busca sobre éste y se corta sobre aquél, así el `.md`
    # conserva la caja original. `lower` preserva la longitud, así que los offsets valen
    # para los dos; si algún día no fuera cierto, mejor saberlo aquí que en el entregable.
    lowered = text.lower()
    if len(lowered) != len(text):
        raise SystemExit("`lower()` changed the text length: offsets are no longer valid")

    def page_of(offset: int) -> int:
        page = 1
        for start, number in pages:
            if start > offset:
                break
            page = number
        return page

    # 1) Recolectar todos los encabezados del PDF y ordenarlos por posición. Las fronteras
    #    salen del propio documento, no del orden en que preguntamos.
    events: list[tuple[int, int, str, str]] = []
    missing: list[str] = []
    for pvid in order:
        hits = occurrences(lowered, web[pvid])
        if not hits:
            missing.append(pvid)
            continue
        events += [(head, body_start, how, pvid) for head, body_start, how in hits]
    events.sort()

    # Un encabezado dentro del anterior es el encabezado corrido de la misma sección
    # repetido, no una sección nueva.
    boundaries: list[tuple[int, int, str, str]] = []
    for event in events:
        if boundaries and event[0] < boundaries[-1][1]:
            continue
        boundaries.append(event)

    # 2) Referencias a nivel de Libro: todo el texto de un lado, para preguntar
    #    "¿este pasaje existe en algún lugar del otro?" sin depender del corte.
    #    Se incluyen `path` y `title` porque en el PDF son texto del cuerpo (los encabezados
    #    se imprimen) y en la web son metadatos: sin ellos, cada encabezado del PDF saldría
    #    como contenido inexistente en el portal.
    web_reference = {
        shingle
        for document in web.values()
        for shingle, _ in shingles(
            normalize(
                f"{document['path']} {document['title']} "
                f"{FIGURE_MARKER.sub(' ', document['markdown'])}"
            )
        )
    }
    # Los niveles intermedios del árbol (Libro, Título, Letra) no son documentos —no tienen
    # cuerpo— pero el PDF sí les imprime una portadilla con su nombre. Sin incluirlos, cada
    # una de esas portadillas se reportaría como texto que el portal no tiene, cuando el
    # portal lo tiene como nodo de navegación.
    web_reference |= {
        shingle
        for node in manifest["nodes"].values()
        if node["title"]
        for shingle, _ in shingles(normalize(node["title"]))
    }
    pdf_reference = {shingle for shingle, _ in shingles(lowered)}
    web_bag: Counter[str] = Counter()
    for document in web.values():
        web_bag.update(
            m.group()
            for m in WORD.finditer(
                normalize(
                    f"{document['path']} {document['title']} "
                    f"{FIGURE_MARKER.sub(' ', document['markdown'])}"
                )
            )
        )
    pdf_bag = Counter(m.group() for m in WORD.finditer(lowered))

    # 3) Cortar: cada sección llega hasta el encabezado siguiente, venga de donde venga.
    #    Un capítulo puede aparecer más de una vez (el PDF repite algunos anexos): sus
    #    trozos se concatenan bajo el mismo pvid en vez de que gane el último.
    pieces: dict[str, list[str]] = {}
    where: dict[str, tuple[int, str]] = {}
    for index, (head, body_start, how, pvid) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        # Se corta sobre el texto en caja original.
        pieces.setdefault(pvid, []).append(text[body_start:end].strip())
        where.setdefault(pvid, (head, how))

    # Rango de páginas de cada sección, para devolverle sus figuras. Una figura se asigna
    # a la primera sección que la reclama: en la página donde termina una y empieza otra,
    # atribuirla a las dos la duplicaría en el entregable.
    spans: dict[str, tuple[int, int]] = {}
    for index, (head, _, _, pvid) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        first, last = page_of(head), page_of(end)
        seen = spans.get(pvid)
        spans[pvid] = (min(seen[0], first), max(seen[1], last)) if seen else (first, last)

    claimed: set[str] = set()
    documents: list[dict] = []
    comparisons: list[dict] = []
    for index, pvid in enumerate(p for p in order if p in pieces):
        head, how = where[pvid]
        first, last = spans[pvid]
        mine: list[str] = []
        for page in range(first, last + 1):
            for digest in figures.get(page, []):
                if digest not in claimed:
                    claimed.add(digest)
                    mine.append(digest)
        pdf_body = "\n\n".join(piece for piece in pieces[pvid] if piece)
        document = web[pvid]
        documents.append({
            "pvid": pvid,
            "order": index,
            "path": document["path"],
            "title": document["title"],
            "anchored_by": how,
            "occurrences": len(pieces[pvid]),
            "pdf_page": first,
            "pdf_page_end": last,
            "figures": mine,
            "text": pdf_body,
        })
        web_body = normalize(FIGURE_MARKER.sub(" ", document["markdown"]))
        comparisons.append({
            "pvid": pvid,
            "citation": document.get("citation", document["path"]),
            "pdf_page": page_of(head),
            "anchored_by": how,
            **compare_document(
                pdf_body.lower(), web_body, web_reference, pdf_reference, web_bag, pdf_bag
            ),
        })

    # 4) Lo que quedó fuera de todo capítulo: el PDF trae índice y portada que la web no
    #    tiene por no ser un documento impreso. Se cuenta aparte, nunca se calla.
    covered = sum(len(d["text"]) for d in documents)
    preamble = boundaries[0][0] if boundaries else len(text)

    book.file_pdf("documents.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    section_files = write_markdown(book, documents, comparisons, manifest)
    verdicts = Counter(c["verdict"] for c in comparisons)
    report = {
        "book": {"slug": book.slug, "name": book.name, "pdf": book.pdf_file},
        "verdicts": dict(verdicts),
        "extra_words_in_pdf": sum(
            c["only_in_pdf"] for c in comparisons if c["verdict"] == "extra_in_pdf"
        ),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "pdf_pages": len(pages),
        "pdf_chars": len(text),
        "toc_lines_skipped": toc_lines,
        "front_matter_chars": preamble,
        "aligned": len(documents),
        "section_files": section_files,
        "web_documents": len(order),
        "anchored_by_heading": sum(1 for d in documents if d["anchored_by"] == "heading"),
        "anchored_by_body": sum(1 for d in documents if d["anchored_by"] == "body"),
        # "No lo pude anclar" y "no está" son cosas distintas, y confundirlas afirma de
        # más: de los 5 que no anclan, los 5 tienen entre 88% y 100% de su vocabulario en
        # el PDF y dos traen frases literales. Lo que falla es el encabezado —el PDF lo
        # imprime distinto del `path` del portal—, no el contenido. Se mide y se dice.
        "unanchored": [
            {
                "pvid": p,
                "citation": web[p].get("citation", ""),
                "title": web[p]["title"],
                "web_chars": len(web[p]["markdown"]),
                "lexical_in_pdf": round(
                    lexical_coverage(
                        normalize(FIGURE_MARKER.sub(" ", web[p]["markdown"])), pdf_bag
                    ), 4,
                ),
            }
            for p in missing
        ],
        "uncovered_chars": len(text) - covered - preamble,
        "figures": compare_figures(book),
        "documents": comparisons,
    }
    book.file_pdf("coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    book.file_pdf("coverage.md").write_text(render(report), encoding="utf-8")
    return report


# `pdftotext` entrega un chorro plano: sin párrafos, sin listas, sin notas. Estas dos
# marcas son las únicas que el propio texto normativo hace explícitas, así que son las
# únicas que se reponen. Inferir más —qué era tabla, qué era encabezado— sería inventar
# estructura que el PDF no dejó en su capa de texto, y un Markdown que inventa jerarquía
# miente peor que uno plano.

def main(books: list[Book] | None = None) -> None:
    for book in books or BOOKS:
        report = align(book)
        v = report["verdicts"]
        words = sum(d["pdf_words"] for d in report["documents"]) or 1
        extra = report["extra_words_in_pdf"]
        print(
            f"{book.slug:10} aligned {report['aligned']:4}/{report['web_documents']:4} "
            f"| unanchored {len(report['unanchored']):2} "
            f"| .md {report['section_files']:4} "
            f"| match {v.get('match', 0):4} reformat. {v.get('reformatted', 0):3} "
            f"unaligned {v.get('unaligned', 0):3} extra {v.get('extra_in_pdf', 0):3} "
            f"| text only in PDF {extra:6,} ({extra / words:.2%})"
        )
        f = report["figures"]
        print(
            f"{'':10} figures: {f['shared']} in both · {f['only_in_web']} web only "
            f"· {f['only_in_pdf']} PDF only"
        )
        print(f"{'':10} -> {book.file_pdf('coverage.md')}")


if __name__ == "__main__":
    main()
