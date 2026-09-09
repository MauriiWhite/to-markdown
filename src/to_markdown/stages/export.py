"""Etapa 4: resuelve las figuras dentro del texto y escribe el entregable.

Cada marcador `[[FIG:…]]` se reemplaza por su contenido convertido, **siempre acompañado de
la URL de la imagen original**. Esa es la garantía de que la transformación es aditiva: si
una conversión salió mal, la fuente sigue a un clic de distancia.

Las fórmulas sin verificar se marcan de forma visible, no en un comentario oculto: un agente
que lea el documento debe poder advertir "esto no está verificado" en vez de afirmarlo.

Uso:  uv run python -m to_markdown.export
"""

from __future__ import annotations

import json
import re
import unicodedata
from urllib.parse import urljoin

from ..core import BOOKS, CONFIG, Book

BASE = CONFIG["crawl"]["base_url"]
GROUP_BY = CONFIG["export"]["group_by"]
MARKER = re.compile(r"\[\[FIG:([0-9a-f]{64})\]\]")
MISSING = re.compile(r"\[\[FIG-MISSING:([^\]]+)\]\]")


def figure_url(src: str) -> str:
    """URL absoluta de la imagen en el sitio de la Superintendencia."""
    return urljoin(BASE, src) if src else ""


def render_figure(figure: dict | None, digest: str, sources: dict[str, str]) -> str:
    """Bloque Markdown para una figura: la imagen **servida desde el sitio de la SP**.

    El Markdown apunta a la URL original y no a una copia local a propósito. Lo que este
    corpus garantiza sobre una figura es su procedencia: quien lea el documento tiene que
    poder abrir la imagen tal como la publica la Superintendencia, sin intermediarios y sin
    depender de que alguien haya copiado bien el archivo.

    La copia local sigue existiendo bajo `images/<sha256>` y su hash va en el comentario de
    traza. Es el respaldo por si la SP cambia o retira el archivo, no la fuente de verdad.
    """
    src = (figure or {}).get("src") or sources.get(digest, "")
    url = figure_url(src)
    if not url:
        return f"<!-- figura {digest[:12]} · sin URL de origen conocida -->"
    # La URL ya va visible en el enlace; el comentario solo agrega el hash, que es lo que
    # permite encontrar la copia local y detectar si la SP cambió el archivo.
    return f"![Figura]({url})\n\n<!-- figura {digest} -->"
def resolve(markdown: str, figures: dict[str, dict], sources: dict[str, str] | None = None) -> str:
    sources = sources or {}
    text = MARKER.sub(
        lambda m: render_figure(figures.get(m.group(1)), m.group(1), sources), markdown
    )
    # Una imagen que no se pudo descargar igual tiene URL, y la URL es lo que importa:
    # el enlace al sitio de la SP puede funcionar perfectamente aunque nuestro `urlopen`
    # haya fallado ese día. Dejarla como comentario mudo perdía la referencia.
    return MISSING.sub(lambda m: f"![Figura]({figure_url(m.group(1))})", text)


# Los niveles del Compendio, del más grueso al más fino. Un Libro se divide en Títulos, un
# Título en Letras y una Letra en Capítulos.
LEVELS = {
    "title": re.compile(r"^T[íi]tulo\b", re.IGNORECASE),
    "letter": re.compile(r"^(Letra\s+)?[A-Z](\.\d+)?[.\s]"),
    "chapter": re.compile(r"^Cap[íi]tulo\b", re.IGNORECASE),
}
HEADING = re.compile(r"^(#{1,5})\s", re.MULTILINE)


def group_of(pvid: str, nodes: dict[str, dict], level: str) -> str:
    """El nodo que define la unidad de archivo de este documento.

    Se sube por el árbol desde el propio documento y gana el ancestro más cercano del nivel
    pedido; si esa rama no lo tiene —hay normas que cuelgan directo de una Letra, o de un
    Título sin Letra de por medio— se cae al nivel siguiente hacia abajo.

    Se resuelve por el árbol y no por prefijos del `path` porque los nombres se repiten:
    "Capítulo I. Introducción" aparece 11 veces solo en el Libro III, bajo Letras distintas,
    y agrupar por texto los fundiría en un archivo.
    """
    chain: list[str] = []
    node: str | None = pvid
    while node:
        chain.append(node)
        node = nodes[node]["parent"]
    order = list(LEVELS)
    for name in order[order.index(level):]:
        for candidate in chain:
            if LEVELS[name].match(nodes[candidate]["title"]):
                return candidate
    return chain[-1]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")[:70]


def sections(manifest: dict, documents: list[dict], level: str = GROUP_BY) -> list[dict]:
    """Los documentos agrupados en archivos, en orden de lectura del Compendio.

    Por defecto un archivo por **Título**: es la unidad con la que la norma se cita y se
    modifica entera ("el Título III del Libro I"), y con la que la SP encabeza cada página
    de su PDF. Las Letras y Capítulos que cuelgan de él no se leen sueltos, así que van
    dentro del mismo archivo como jerarquía de encabezados.

    Los grupos y su numeración salen del **manifiesto completo**, no de los documentos que
    se pasan. Es lo que hace que el nombre de archivo sea estable: el lado PDF recibe solo
    los capítulos que logró alinear, y si el número ordinal se calculara sobre ese
    subconjunto, cada capítulo sin alinear correría todos los siguientes y los dos árboles
    dejarían de poder compararse con un `diff`.
    """
    nodes = manifest["nodes"]
    by_pvid = {d["pvid"]: d for d in documents}
    groups: dict[str, list[str]] = {}
    for pvid in manifest["documents"]:
        groups.setdefault(group_of(pvid, nodes, level), []).append(pvid)

    out = []
    for index, (pvid, member_ids) in enumerate(groups.items(), start=1):
        members = [by_pvid[m] for m in member_ids if m in by_pvid]
        if not members:
            continue
        title = nodes[pvid]["title"] or members[0]["title"]
        out.append({
            "pvid": pvid,
            "title": title,
            "path": members[0]["path"],
            "level": level,
            "index": index,
            "filename": f"{index}-{slugify(title)}.md",
            "documents": members,
        })
    return out


def demote(markdown: str, levels: int = 2) -> str:
    """Baja los encabezados del cuerpo para que quepan bajo los de la sección.

    El cuerpo trae `#`…`#####` heredados del HTML de la SP. Si se pegaran tal cual bajo el
    `#` del Título, un `#` interno competiría con el título del archivo y el índice del
    Markdown saldría plano. Bajarlos conserva la jerarquía en vez de aplanarla.
    """
    return HEADING.sub(lambda m: "#" * min(6, len(m.group(1)) + levels) + " ", markdown)


def section_markdown(
    book: Book, section: dict, resolved: dict[str, str], nodes: dict[str, dict]
) -> str:
    """Una sección entera como un solo Markdown, con su jerarquía interna intacta.

    Los niveles intermedios del árbol —las Letras y los Capítulos que cuelgan del Título—
    se emiten como encabezados anidados, cada uno a la profundidad que le toca. Sin eso,
    un Título con 12 Capítulos sería una pared de texto: el archivo tendría el contenido
    correcto y ninguna forma de navegarlo.
    """
    members = section["documents"]
    lines = [
        "---",
        f"book: {book.slug}",
        f"section_pvid: {section['pvid']}",
        f"level: {section['level']}",
        f"order: {section['index']}",
        f"title: {json.dumps(section['title'], ensure_ascii=False)}",
        f"path: {json.dumps(section['path'], ensure_ascii=False)}",
        f"documents: {json.dumps([d['pvid'] for d in members], ensure_ascii=False)}",
        "source: web",
        "---",
        "",
        f"# {section['title']}",
        "",
    ]
    emitted = {section["pvid"]}
    for document in members:
        # Cadena desde la raíz de la sección (exclusive) hasta el propio documento.
        chain: list[str] = []
        node: str | None = document["pvid"]
        while node and node != section["pvid"]:
            chain.append(node)
            node = nodes[node]["parent"]
        chain.reverse()

        for depth, pvid in enumerate(chain, start=2):
            if pvid in emitted:
                continue
            emitted.add(pvid)
            lines += [f"{'#' * min(6, depth)} {nodes[pvid]['title']}", ""]

        level = min(6, len(chain) + 1)
        if document["topics"]:
            lines += [f"*Materias: {', '.join(document['topics'])}*", ""]
        lines += [
            demote(resolved[document["pvid"]], level).strip(),
            "",
            f"<!-- pvid {document['pvid']} · {document['url']} -->",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def front_matter(document: dict) -> str:
    # `title` es el título propio de la página; el nivel Título de la jerarquía va anidado
    # bajo `hierarchy`, porque en plano ambos reclamarían la misma clave.
    lines = [
        "---",
        f"pvid: {document['pvid']}",
        f"url: {document['url']}",
        f"title: {json.dumps(document['title'], ensure_ascii=False)}",
        f"path: {json.dumps(document['path'], ensure_ascii=False)}",
    ]
    hierarchy = document.get("hierarchy") or {}
    if hierarchy:
        lines.append("hierarchy:")
        for level in ("book", "title", "letter", "chapter"):
            if hierarchy.get(level):
                lines.append(f"  {level}: {json.dumps(hierarchy[level], ensure_ascii=False)}")
    if document["topics"]:
        lines.append(f"topics: {json.dumps(document['topics'], ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def export_book(book: Book) -> tuple[list[dict], list[dict], list[dict]]:
    """Escribe el entregable del Libro: JSONL, un Markdown por Título y el índice de figuras."""
    book.mkdirs()
    documents = json.loads(book.file("documents.json").read_text(encoding="utf-8"))
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    index = json.loads(book.file("images.json").read_text(encoding="utf-8"))
    sources = {digest: src for src, digest in index.items()}

    resolved: dict[str, str] = {}
    with book.file("documents.jsonl").open("w", encoding="utf-8") as out:
        for document in documents:
            markdown = resolve(document["markdown"], {}, sources)
            resolved[document["pvid"]] = markdown
            out.write(json.dumps({**document, "markdown": markdown}, ensure_ascii=False) + "\n")

    # Un archivo por Título, no por página del CMS. Un Título es lo que alguien pide entero
    # y con lo que la norma se cita; sus Letras, Capítulos y anexos no se leen sueltos, y
    # repartidos en 40 archivos hay que recomponerlos a mano para leer una sola norma.
    for path in book.markdown.glob("*.md"):
        path.unlink()
    grouped = sections(manifest, documents)
    for section in grouped:
        (book.markdown / section["filename"]).write_text(
            section_markdown(book, section, resolved, manifest["nodes"]), encoding="utf-8"
        )
    book.file("sections.json").write_text(
        json.dumps(
            [{k: v for k, v in c.items() if k != "documents"}
             | {"documents": [d["pvid"] for d in c["documents"]]} for c in grouped],
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    figures = figure_index(book, documents, sources)
    with book.file("figures.jsonl").open("w", encoding="utf-8") as out:
        for figure in figures:
            out.write(json.dumps(figure, ensure_ascii=False) + "\n")

    return documents, figures, grouped


def figure_index(book: Book, documents: list[dict], sources: dict[str, str]) -> list[dict]:
    """Una entrada por figura: su URL en el sitio de la SP y qué normas la citan.

    `url` es lo que hace verificable el corpus; `file` es el respaldo local por si la SP
    cambia el archivo. Los `documents` que la referencian van también porque una figura
    reutilizada en cinco normas es un dato, no una repetición.
    """
    users: dict[str, list[str]] = {}
    for document in documents:
        for digest in document["figures"]:
            users.setdefault(digest, []).append(document["pvid"])

    out = []
    for digest, pvids in users.items():
        local = sorted(book.images.glob(f"{digest}.*"))
        src = sources.get(digest, "")
        out.append({
            "sha256": digest,
            "src": src,
            "url": figure_url(src),
            "file": local[0].name if local else "",
            "documents": pvids,
        })
    return sorted(out, key=lambda f: f["sha256"])


def report(documents: list[dict], figures: list[dict]) -> None:
    chars = sum(len(d["markdown"]) for d in documents)
    notes = sum(len(d["amendment_notes"]) for d in documents)
    units = sum(len(d["units"]) for d in documents)
    referenced = {f for d in documents for f in d["figures"]}
    without_url = sum(1 for f in figures if not f["url"])
    print(f"documents: {len(documents)} | {chars:,} chars | units: {units:,} | notes: {notes}")
    print(f"figures: {len(referenced)} referenced | {len(figures)} with a source URL")
    if without_url:
        # La procedencia es lo único que este corpus promete sobre una figura. Perderla en
        # silencio sería exactamente el fallo que el resto del pipeline evita.
        print(f"WARNING: {without_url} figures without a source URL")


def main(books: list[Book] | None = None) -> None:
    books = books or BOOKS
    all_documents: list[dict] = []
    all_figures: list[dict] = []
    for book in books:
        documents, figures, grouped = export_book(book)
        print(f"\n--- {book.name} ({book.slug}) ---")
        print(f"sections: {len(grouped)} .md files ({GROUP_BY}) for {len(documents)} documents")
        report(documents, figures)
        all_documents += documents
        # Ninguna figura se repite entre Libros (verificado sobre las 1.743 del corpus),
        # así que el total es la suma y no hay que desduplicar.
        all_figures += figures

    if len(books) > 1:
        print(f"\n--- TOTAL ({len(books)} books) ---")
        report(all_documents, all_figures)


if __name__ == "__main__":
    main()
