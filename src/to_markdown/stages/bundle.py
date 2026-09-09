"""Etapa 7: arma `output/`, la carpeta lista para entregar.

No transforma nada: toma los Markdown que ya produjo `export` y los empaqueta con los
índices que un lector —persona o modelo— necesita para orientarse. Va aparte de `export`
porque son dos cosas distintas: `data/` es el área de trabajo del pipeline, con su caché,
su estado y sus artefactos intermedios; `output/` es lo único que se le manda a alguien.

La estructura es una carpeta por Libro, y cada una con su `index.md`. El índice importa
más de lo que parece cuando el destinatario es un modelo: sin él, encontrar "el Capítulo
XXIV del Título III" obliga a leer los 12 archivos del Libro; con él, es una consulta al
índice y después un solo archivo.

Uso:  uv run python -m to_markdown bundle
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime

from ..core import BOOKS, CONFIG, OUTPUT, Book

BASE = CONFIG["crawl"]["base_url"]
WORD = re.compile(r"\w+", re.UNICODE)
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def es(number: int) -> str:
    """Número con separador de miles español. El índice es prosa en español y lo lee tanto
    una persona como un modelo; `1,582` ahí se lee como mil coma quinientos ochenta y dos."""
    return f"{number:,}".replace(",", ".")


def words(text: str) -> int:
    return len(WORD.findall(FRONT_MATTER.sub("", text)))


def crawled_at(book: Book) -> str:
    """Cuándo se descargó realmente este Libro, según las cabeceras del propio crawl.

    Se usa la fecha del crawl y no la de hoy: el bundle puede rearmarse mil veces sobre un
    corpus de la semana pasada, y fechar el paquete en vez del contenido haría creer que la
    norma está más al día de lo que está.
    """
    path = book.file("http.json")
    if not path.exists():
        return ""
    stamps = [
        meta.get("fetched_at", "")
        for meta in json.loads(path.read_text(encoding="utf-8")).values()
    ]
    return max((s for s in stamps if s), default="")


def outline(section: dict, documents: dict[str, dict], nodes: dict[str, dict]) -> list[str]:
    """Las Letras y Capítulos de un Título, como lista anidada.

    Es la tabla de consulta que convierte "¿dónde está el Capítulo XXIV?" en una sola
    lectura de archivo. Se corta en el Capítulo: los números que cuelgan de él se citan
    como `Capítulo XXIV, N° 3` y no necesitan entrada propia.
    """
    lines: list[str] = []
    seen = {section["pvid"]}
    for pvid in section["documents"]:
        chain: list[str] = []
        node: str | None = pvid
        while node and node != section["pvid"]:
            chain.append(node)
            node = nodes[node]["parent"]
        chain.reverse()
        for depth, ancestor in enumerate(chain[:2]):
            if ancestor in seen:
                continue
            seen.add(ancestor)
            title = nodes[ancestor]["title"] or documents.get(ancestor, {}).get("title", "")
            if title:
                lines.append(f"{'  ' * depth}- {title}")
        if not chain and pvid not in seen:
            seen.add(pvid)
            lines.append(f"- {documents[pvid]['title']}")
    return lines


def topics_index(sections: list[dict], documents: dict[str, dict]) -> dict[str, list[int]]:
    """Materia -> en qué Títulos aparece. Son las etiquetas que pone la propia SP, así que
    valen más que cualquier clasificación que inventáramos nosotros."""
    out: dict[str, set[int]] = {}
    for section in sections:
        for pvid in section["documents"]:
            for topic in documents.get(pvid, {}).get("topics", []):
                out.setdefault(topic, set()).add(section["index"])
    return {topic: sorted(where) for topic, where in sorted(out.items())}


def book_index(book: Book, sections: list[dict], documents: dict[str, dict],
               nodes: dict[str, dict], sizes: dict[str, int]) -> str:
    total_docs = sum(len(s["documents"]) for s in sections)
    total_units = sum(len(d["units"]) for d in documents.values())
    total_notes = sum(len(d["amendment_notes"]) for d in documents.values())
    stamp = crawled_at(book)

    lines = [
        f"# {book.name} — Índice",
        "",
        "Compendio de Normas del Sistema de Pensiones · Superintendencia de Pensiones de Chile.",
        "",
        f"- Fuente: {BASE}w3-propertyvalue-{book.pvid}.html",
        f"- Extraído del portal: {stamp or 'sin fecha registrada'}",
        (f"- Contenido: **{len(sections)} Títulos**, {total_docs} normas, "
         f"{es(total_units)} números normativos, {es(total_notes)} notas de actualización"),
        "",
        "Cada Título es un archivo. Para citar una norma se usa su Capítulo y su número:",
        '"Título III, Capítulo XXIV, N° 3".',
        "",
        "## Títulos",
        "",
        "| # | Archivo | Título | Normas | Palabras |",
        "| ---: | --- | --- | ---: | ---: |",
    ]
    for section in sections:
        lines.append(
            (f"| {section['index']} | `{section['filename']}` | {section['title']} "
             f"| {len(section['documents'])} | {es(sizes.get(section['filename'], 0))} |"),
        )

    lines += ["", "## Qué contiene cada Título", ""]
    for section in sections:
        lines += [
            f"### {section['index']}. {section['title']}",
            "",
            f"Archivo: `{section['filename']}` · {len(section['documents'])} normas",
            "",
        ]
        body = outline(section, documents, nodes)
        lines += body or ["- (sin subdivisiones)"]
        lines.append("")

    topics = topics_index(sections, documents)
    if topics:
        lines += [
            "## Materias",
            "",
            ("Las materias que la propia Superintendencia asocia a cada norma, y en qué "
             "Títulos aparecen."),
            "",
            "| Materia | Títulos |",
            "| --- | --- |",
        ]
        for topic, where in topics.items():
            lines.append(f"| {topic} | {', '.join(str(w) for w in where)} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def readme(summary: list[dict]) -> str:
    total = {k: sum(b[k] for b in summary) for k in ("sections", "documents", "units", "notes")}
    lines = [
        "# Compendio de Normas del Sistema de Pensiones",
        "",
        "Superintendencia de Pensiones de Chile, extraído de su portal y convertido a Markdown.",
        "",
        (f"**{total['sections']} archivos** en 5 Libros · {es(total['documents'])} normas · "
         f"{es(total['units'])} números normativos · {es(total['notes'])} notas de "
         f"actualización."),
        "",
        "## Los cinco Libros",
        "",
        "| Carpeta | Libro | Títulos | Normas | Extraído |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for book in summary:
        lines.append(
            (f"| `{book['slug']}/` | {book['name']} | {book['sections']} "
             f"| {book['documents']} | {book['crawled_at'][:10] or '—'} |"),
        )
    lines += [
        "",
        "## Cómo está organizado",
        "",
        ("Una carpeta por Libro. Dentro, un archivo Markdown por **Título** —la unidad con la "
         "que la norma se cita y se modifica entera— y un `index.md` que lista sus Títulos, "
         "los Capítulos que contiene cada uno y las materias que cubre."),
        "",
        "```",
        "book-i/",
        "├── index.md                      ← empezar aquí",
        "├── 1-titulo-i-afiliacion-....md",
        "└── ...",
        "```",
        "",
        ("Para ubicar una norma: leer el `index.md` del Libro, encontrar el Título que la "
         "contiene, y abrir ese archivo. Dentro, la jerarquía va como encabezados "
         "(`##` Letra, `###` Capítulo) y cada norma conserva su `pvid` y su URL de origen en "
         "un comentario."),
        "",
        "## Sobre el contenido",
        "",
        "- El texto normativo está **íntegro y sin resumir**, tal como lo publica la SP.",
        ("- Las tablas se convirtieron desde el HTML original, así que conservan sus filas y "
         "columnas."),
        ("- Las **figuras se enlazan a la imagen original en `spensiones.cl`**: no hay copias "
         "locales que puedan diferir de la fuente. Requieren conexión para verse."),
        ("- Las **notas de actualización** están marcadas como citas (`>`) e indican qué Norma "
         "de Carácter General modificó cada número."),
        "",
        "## Procedencia",
        "",
        f"Portal de origen: {BASE}",
        "",
        ("Cada archivo lleva en su front matter el `pvid` de las páginas que lo componen, y "
         "cada norma un comentario con su URL. Cualquier afirmación de este corpus se puede "
         "contrastar contra la página del organismo."),
        "",
        f"Paquete generado el {datetime.now(UTC).strftime('%Y-%m-%d')}.",
    ]
    return "\n".join(lines) + "\n"


def bundle_book(book: Book) -> dict:
    sections = json.loads(book.file("sections.json").read_text(encoding="utf-8"))
    documents = {
        d["pvid"]: d
        for d in json.loads(book.file("documents.json").read_text(encoding="utf-8"))
    }
    nodes = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))["nodes"]

    target = OUTPUT / book.slug
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    sizes: dict[str, int] = {}
    for section in sections:
        source = book.markdown / section["filename"]
        text = source.read_text(encoding="utf-8")
        sizes[section["filename"]] = words(text)
        shutil.copyfile(source, target / section["filename"])

    (target / "index.md").write_text(
        book_index(book, sections, documents, nodes, sizes), encoding="utf-8"
    )
    return {
        "slug": book.slug,
        "name": book.name,
        "sections": len(sections),
        "documents": sum(len(s["documents"]) for s in sections),
        "units": sum(len(d["units"]) for d in documents.values()),
        "notes": sum(len(d["amendment_notes"]) for d in documents.values()),
        "words": sum(sizes.values()),
        "crawled_at": crawled_at(book),
    }


def main(books: list[Book] | None = None) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for book in books or BOOKS:
        stats = bundle_book(book)
        summary.append(stats)
        print(
            (f"{book.slug:9} {stats['sections']:3} .md + index | "
             f"{stats['documents']:4} normas | {stats['words']:8,} palabras"),
        )
    if len(summary) == len(BOOKS):
        (OUTPUT / "README.md").write_text(readme(summary), encoding="utf-8")
    print(
        (f"{'TOTAL':9} {sum(s['sections'] for s in summary):3} .md + "
         f"{len(summary)} índices -> {OUTPUT}"),
    )


if __name__ == "__main__":
    main()
