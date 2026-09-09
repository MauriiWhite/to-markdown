"""Lo que la comparativa deja escrito: el Markdown del lado PDF y el informe legible.

Separado de la medición a propósito: cambiar cómo se presenta un hallazgo no puede obligar
a tocar el criterio con que se decidió que era un hallazgo.
"""

from __future__ import annotations

import json
import re

from ...core import Book
from ..export import sections

ITEM = re.compile(r"(?<=[.;:)])\s+(?=\d{1,3}[.)]\s+[A-ZÁÉÍÓÚÑ¿(])")
AMENDMENT = re.compile(r"\s*Nota de actualizaci[óo]n:\s*", re.IGNORECASE)


def to_markdown(text: str, title: str = "") -> str:
    """Repone los saltos de párrafo que el PDF perdió al aplanarse.

    Las notas de actualización van en cita, como en el lado web: dicen qué Norma de
    Carácter General modificó el número anterior, y perdidas dentro del párrafo dejan de
    leerse como el metadato de vigencia que son.
    """
    # El PDF imprime el título como encabezado del cuerpo; el `.md` ya lo trae arriba.
    if title and text[: len(title)].lower() == title.lower():
        text = text[len(title):].lstrip(" .-")
    text = ITEM.sub("\n\n", text)
    text = AMENDMENT.sub("\n\n> **Nota de actualización:** ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def write_markdown(book: Book, documents: list[dict], comparisons: list[dict], manifest: dict) -> int:
    """Un `.md` por Capítulo, en espejo exacto de `data/web/<libro>/markdown/`.

    Mismo criterio de agrupación y mismo nombre de archivo que el lado web, para que
    `diff data/web/book-i/markdown/002-*.md data/pdf/book-i/markdown/002-*.md` sea una
    comparación directa, sin herramienta de por medio.

    El front matter lleva de dónde salió cada sección —página del PDF, cómo se ancló, qué
    cobertura tiene— porque un `.md` suelto tiene que poder declarar cuánto vale su
    alineación sin volver al informe.
    """
    for path in book.pdf_markdown.glob("*.md"):
        path.unlink()
    stats = {c["pvid"]: c for c in comparisons}
    grouped = sections(manifest, documents)
    for section in grouped:
        members = section["documents"]
        pages = [d["pdf_page"] for d in members]
        lines = [
            "---",
            f"book: {book.slug}",
            f"section_pvid: {section['pvid']}",
            f"order: {section['index']}",
            f"title: {json.dumps(section['title'], ensure_ascii=False)}",
            f"path: {json.dumps(section['path'], ensure_ascii=False)}",
            f"documents: {json.dumps([d['pvid'] for d in members], ensure_ascii=False)}",
            "source: pdf",
            f"pdf_file: {book.pdf_file}",
            f"pdf_pages: {min(pages)}-{max(pages)}",
            f"coverage_pdf: {min(stats[d['pvid']]['coverage_pdf'] for d in members):.4f}",
            "---",
            "",
            f"# {section['title']}",
            "",
        ]
        emitted = {section["pvid"]}
        for document in members:
            info = stats[document["pvid"]]
            # Misma jerarquía anidada que el lado web: los niveles intermedios del árbol
            # se emiten como encabezados a la profundidad que les toca.
            chain: list[str] = []
            node = document["pvid"]
            while node and node != section["pvid"]:
                chain.append(node)
                node = manifest["nodes"][node]["parent"]
            chain.reverse()
            for depth, pvid in enumerate(chain, start=2):
                if pvid in emitted:
                    continue
                emitted.add(pvid)
                lines += [f"{'#' * min(6, depth)} {manifest['nodes'][pvid]['title']}", ""]

            if info["verdict"] == "unaligned":
                lines += [
                    "> ⚠️ El corte de esta sección absorbió texto vecino: el PDF agrupa sus",
                    "> Anexos distinto que el árbol del portal. El texto es del Libro, pero no",
                    "> necesariamente todo de esta sección.",
                    "",
                ]
            lines += [to_markdown(document["text"], document["title"]), ""]
            for digest in document["figures"]:
                lines += [
                    f"![Figura {digest[:12]}](../images/{digest}.png)",
                    "",
                ]
            lines += [
                (f"<!-- pvid {document['pvid']} · {book.pdf_file} "
                 f"pág. {document['pdf_page']} · ancla {document['anchored_by']} "
                 f"· cobertura {info['coverage_pdf']:.0%} -->"),
                "",
            ]
        (book.pdf_markdown / section["filename"]).write_text(
            "\n".join(lines).rstrip() + "\n", encoding="utf-8"
        )
    return len(grouped)



def render(report: dict) -> str:
    """El informe legible. Lo que se revisa de verdad es un archivo, no un JSON."""
    total_pdf = sum(d["only_in_pdf"] for d in report["documents"])
    total_web = sum(d["only_in_web"] for d in report["documents"])
    words_pdf = sum(d["pdf_words"] for d in report["documents"])
    words_web = sum(d["web_words"] for d in report["documents"])

    lines = [
        f"# {report['book']['name']} — PDF oficial contra portal",
        "",
        (f"`{report['book']['pdf']}` · {report['pdf_pages']:,} páginas · "
         f"generado {report['generated_at']}"),
        "",
        "## Alineación",
        "",
        "| | |",
        "| --- | ---: |",
        f"| Documentos en el portal | {report['web_documents']:,} |",
        f"| Alineados en el PDF | {report['aligned']:,} |",
        f"| — por encabezado | {report['anchored_by_heading']:,} |",
        f"| — por cuerpo (encabezado distinto en el PDF) | {report['anchored_by_body']:,} |",
        f"| Sin anclar (el texto puede estar igual) | {len(report['unanchored']):,} |",
        "",
        "## Volumen",
        "",
        "| | |",
        "| --- | ---: |",
        f"| Texto del PDF (sin utilería de página) | {report['pdf_chars']:,} chars |",
        f"| Índice y portada, previos al primer capítulo | {report['front_matter_chars']:,} chars |",
        f"| Líneas de índice descartadas | {report['toc_lines_skipped']:,} |",
        f"| Palabras comparadas — PDF | {words_pdf:,} |",
        f"| Palabras comparadas — portal | {words_web:,} |",
        f"| Solo en el PDF | {total_pdf:,} ({total_pdf / words_pdf:.1%}) |" if words_pdf else "",
        f"| Solo en el portal | {total_web:,} ({total_web / words_web:.1%}) |" if words_web else "",
        "",

        "## Figuras",
        "",
        "Comparadas por contenido visual y no por archivo: el PDF embebe la misma figura",
        "varias veces con compresión distinta, y el portal la sirve en JPG donde",
        "`pdfimages` devuelve PNG.",
        "",
        "| | |",
        "| --- | ---: |",
        (f"| Archivos — portal / PDF | {report['figures']['web_files']:,} / "
         f"{report['figures']['pdf_files']:,} |"),
        (f"| Figuras distintas — portal / PDF | {report['figures']['web_distinct']:,} / "
         f"{report['figures']['pdf_distinct']:,} |"),
        f"| Presentes en ambos | {report['figures']['shared']:,} |",
        f"| Solo en el portal | {report['figures']['only_in_web']:,} |",
        f"| Solo en el PDF | {report['figures']['only_in_pdf']:,} |",
        "",
    ]

    if report["unanchored"]:
        lines += [
            "## Sin anclar",
            "",
            "El encabezado que el PDF imprime para estas secciones no coincide con el `path`",
            "del portal, así que no se pudo cortar su tramo. `Léxico en el PDF` dice cuánto de",
            "su vocabulario sí aparece en el documento: cerca de 100% significa que el texto",
            "está y lo que falla es la alineación, no el contenido.",
            "",
            "| Cita | Título | Chars | Léxico en el PDF |",
            "| --- | --- | ---: | ---: |",
        ]
        for item in report["unanchored"]:
            lines.append(
                f"| {item['citation'][:60]} | {item['title'][:44]} "
                f"| {item['web_chars']:,} | {item['lexical_in_pdf']:.0%} |"
            )
        lines.append("")

    extra = sorted(report["documents"], key=lambda d: -d["only_in_pdf"])
    extra = [d for d in extra if d["only_in_pdf"]][:25]
    if extra:
        lines += ["## Capítulos con más contenido en el PDF que en el portal", "",
                  "| Cita | pág. | Solo en PDF | Cobertura PDF |", "| --- | ---: | ---: | ---: |"]
        for d in extra:
            lines.append(
                f"| {d['citation'][:64]} | {d['pdf_page']} | {d['only_in_pdf']:,} "
                f"| {d['coverage_pdf']:.1%} |"
            )
        lines += ["", "### Pasajes presentes solo en el PDF", ""]
        for d in extra[:10]:
            if not d["extra_in_pdf"]:
                continue
            lines += [f"**{d['citation'][:90]}** (pág. {d['pdf_page']})", ""]
            for passage in d["extra_in_pdf"][:2]:
                lines += ["> " + passage[:400].replace("\n", " "), ""]
    return "\n".join(line for line in lines if line != "") + "\n"


