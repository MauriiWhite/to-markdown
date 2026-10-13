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
from .export import MAX_WORDS

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
                lines.append(f"{'  ' * depth}- {title}{detail(documents.get(ancestor))}")
        if not chain and pvid not in seen:
            seen.add(pvid)
            lines.append(f"- {documents[pvid]['title']}{detail(documents[pvid])}")
    return lines


def detail(document: dict | None) -> str:
    """Lo que dice de un Capítulo su línea en el índice: cuántos números trae y sus
    primeras materias. Solo si el nodo es una norma con texto; una Letra no lleva."""
    if not document:
        return ""
    bits = []
    if document["units"]:
        count = len(document["units"])
        bits.append(f"{count} número{'s' if count > 1 else ''}")
    if document["topics"]:
        bits.append(", ".join(document["topics"][:3]))
    return f" — {' · '.join(bits)}" if bits else ""


def topics_index(sections: list[dict], documents: dict[str, dict]) -> dict[str, list[int]]:
    """Materia -> en qué Títulos aparece. Son las etiquetas que pone la propia SP, así que
    valen más que cualquier clasificación que inventáramos nosotros."""
    out: dict[str, set[int]] = {}
    for section in sections:
        for pvid in section["documents"]:
            for topic in documents.get(pvid, {}).get("topics", []):
                out.setdefault(topic, set()).add(section["index"])
    return {topic: sorted(where) for topic, where in sorted(out.items())}


MONTHS = {name: number for number, names in enumerate(
    ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre|setiembre", "octubre", "noviembre", "diciembre"), start=1)
    for name in names.split("|")}
AMENDMENT = re.compile(
    r"(?:Norma de Car[áa]cter General|NCG)\s*N[º°o]?\.?\s*(\d+)\D{0,60}?(\d{1,2})°?\s+de\s*"
    rf"({'|'.join(MONTHS)})\w*\s+(?:del?\s+)?(\d{{4}})",
    re.IGNORECASE,
)


def amendments(document: dict) -> list[tuple[str, int]]:
    """Las NCG que modificaron esta norma, como `(fecha ISO, número)`.

    Sale de las notas de actualización que la propia SP intercala en el texto ("Este número
    fue modificado por la Norma de Carácter General N° 31, de fecha 29 de diciembre de
    2011"). Una nota sin fecha legible no se cuenta acá, pero sigue íntegra en el archivo:
    esto es un dato del índice, no una transformación del texto.
    """
    out = []
    for note in document.get("amendment_notes", []):
        if match := AMENDMENT.search(note):
            number, day, month, year = match.groups()
            out.append((f"{year}-{MONTHS[month.lower()]:02d}-{int(day):02d}", int(number)))
    return out


def es_date(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{day}-{month}-{year}"


SKIPPED_LINE = re.compile(r"^\s*(\||#|>|!\[|<|-{3,}|\*\*[^*]+\*\*\s*$)")
SENTENCE = re.compile(r"(.+?(?<![A-ZÁÉÍÓÚ])[.;:])(?:\s+(?=[A-ZÁÉÍÓÚ¿(])|\s*$)")


def excerpt(markdown: str, limit: int = 60) -> str:
    """La primera oración del texto, **tal como la escribe la SP**, hasta `limit` palabras.

    No es un resumen: es una cita textual del inicio, que en casi todos los Títulos es el
    párrafo donde la propia SP dice qué regula ("El presente Título contiene instrucciones
    respecto de…"). Resumir pediría un modelo, y el pipeline no interpreta: extrae.
    """
    text = re.sub(r"\[\[FIG[^\]]*\]\]", "", markdown)
    lines = [
        line.strip() for line in text.splitlines()
        if line.strip() and not SKIPPED_LINE.match(line)
        # Un rótulo suelto ("I. Introducción") no es prosa y se pegaría a la oración.
        and (len(line.split()) >= 6 or line.rstrip().endswith((".", ";", ":")))
    ]
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", " ".join(lines))
    text = re.sub(r"\*\*|__|`", "", text)
    text = re.sub(r"^(\d+[.)]|[a-z]\))\s+", "", text)
    sentence = next(
        (m.group(1) for m in SENTENCE.finditer(text) if len(m.group(1).split()) >= 12), text
    ) if len(text.split()) > 12 else text
    tokens = sentence.split()
    return " ".join(tokens[:limit]) + ("…" if len(tokens) > limit else "")


def title_roman(title: str, index: int) -> str:
    match = re.match(r"T[íi]tulo\s+([IVXLC]+)\b", title)
    return match.group(1) if match else str(index)


def by_title(sections: list[dict]) -> list[list[dict]]:
    """Las secciones agrupadas por Título, en orden: un Título partido son varias."""
    groups: dict[str, list[dict]] = {}
    for section in sections:
        groups.setdefault(section["pvid"], []).append(section)
    return list(groups.values())


def title_profile(parts: list[dict], documents: dict[str, dict],
                  sizes: dict[str, int]) -> dict:
    """Todo lo que el índice dice de un Título, calculado una vez para los dos índices."""
    members = [documents[p] for part in parts for p in part["documents"] if p in documents]
    topics: dict[str, int] = {}
    for document in members:
        for topic in document["topics"]:
            topics[topic] = topics.get(topic, 0) + 1
    changes = sorted({c for d in members for c in amendments(d)})
    opening = next((d for d in members if excerpt(d["markdown"])), None)
    first = parts[0]
    return {
        "index": first["index"],
        "roman": title_roman(first["title"], first["index"]),
        "title": first["title"],
        "files": [p["filename"] for p in parts],
        "documents": len(members),
        "units": sum(len(d["units"]) for d in members),
        "notes": sum(len(d["amendment_notes"]) for d in members),
        "figures": len({f for d in members for f in d["figures"]}),
        "words": sum(sizes.get(p["filename"], 0) for p in parts),
        # Por cuántas normas del Título aparece cada materia: la más repetida va primero.
        "topics": sorted(topics, key=lambda t: (-topics[t], t)),
        "changes": changes,
        "ncgs": len({number for _, number in changes}),
        "excerpt": excerpt(opening["markdown"]) if opening else "",
        "excerpt_from": opening["citation"] if opening else "",
    }


def latest_ncgs(entries: list[tuple[str, int, str, int]]) -> list[tuple[str, int, list[str]]]:
    """`(fecha, NCG, dónde, orden)` -> una fila por NCG, con su fecha más reciente.

    Se agrupa por número y no por par fecha-número porque la SP a veces fecha distinto la
    misma NCG en dos notas (la 366 aparece el 27 y el 30 de junio de 2026), y dos filas
    para una sola norma harían creer que hubo dos modificaciones.
    """
    rows: dict[int, tuple[str, dict[str, int]]] = {}
    for date, number, where, order in entries:
        known, places = rows.get(number, ("", {}))
        places.setdefault(where, order)
        rows[number] = (max(known, date), places)
    out = [(date, number, sorted(places, key=places.get))
           for number, (date, places) in rows.items()]
    return sorted(out, key=lambda r: (r[0], r[1]), reverse=True)


def plural(count: int, word: str) -> str:
    return f"{es(count)} {word}{'' if count == 1 else 's'}"


def changes_line(profile: dict) -> str:
    if not profile["changes"]:
        return "sin notas de actualización con fecha"
    date, number = max(profile["changes"])
    first = min(profile["changes"])[0]
    return (f"{profile['ncgs']} NCG entre {first[:4]} y {date[:4]}; la más reciente, "
            f"NCG N° {number} del {es_date(date)}")


def book_index(book: Book, sections: list[dict], documents: dict[str, dict],
               nodes: dict[str, dict], sizes: dict[str, int],
               profiles: list[dict]) -> str:
    total_docs = sum(len(s["documents"]) for s in sections)
    total_units = sum(len(d["units"]) for d in documents.values())
    total_notes = sum(len(d["amendment_notes"]) for d in documents.values())
    total_figures = len({f for d in documents.values() for f in d["figures"]})
    stamp = crawled_at(book)
    full_name = nodes.get(book.pvid, {}).get("title") or book.name

    lines = [
        f"# {book.name} — Índice",
        "",
        f"**{full_name}**",
        "",
        ("Compendio de Normas del Sistema de Pensiones · Superintendencia de Pensiones de "
         "Chile. Este índice dice qué regula cada Título del Libro, en qué archivo está cada "
         "Capítulo y qué tan reciente es su última modificación."),
        "",
        f"- Fuente: {BASE}w3-propertyvalue-{book.pvid}.html",
        f"- Extraído del portal: {stamp or 'sin fecha registrada'}",
        (f"- Contenido: **{len(profiles)} Títulos** en {len(sections)} archivos · "
         f"{es(total_docs)} normas · {es(total_units)} números normativos · "
         f"{es(total_notes)} notas de actualización · {es(total_figures)} figuras · "
         f"{es(sum(sizes.values()))} palabras"),
        "",
        (f"Cada Título es un archivo, o varias partes si supera {es(MAX_WORDS)} palabras: "
         "se corta entre Capítulos, nunca dentro de uno, así que un Capítulo que solo ya "
         "supera ese tope queda entero en su parte. Para citar una norma se usa su "
         'Capítulo y su número: "Título III, Capítulo XXIV, N° 3".'),
        "",
        "## Títulos de un vistazo",
        "",
        "| Título | Nombre | Archivos | Normas | Palabras | Última modificación |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for profile in profiles:
        last = (f"NCG N° {max(profile['changes'])[1]} ({es_date(max(profile['changes'])[0])})"
                if profile["changes"] else "—")
        name = re.sub(r"^T[íi]tulo\s+[IVXLC]+\.?\s*", "", profile["title"])
        lines.append(
            (f"| {profile['roman']} | {name} | {len(profile['files'])} "
             f"| {profile['documents']} | {es(profile['words'])} | {last} |"),
        )

    lines += [
        "",
        "## Archivos",
        "",
        "| Archivo | Título | Parte | Normas | Palabras |",
        "| --- | --- | :---: | ---: | ---: |",
    ]
    for section in sections:
        part = f"{section['part']}/{section['parts']}" if section["parts"] > 1 else "—"
        lines.append(
            (f"| `{section['filename']}` | {section['title']} | {part} "
             f"| {len(section['documents'])} | {es(sizes.get(section['filename'], 0))} |"),
        )

    lines += ["", "## Qué contiene cada Título", ""]
    for profile, parts in zip(profiles, by_title(sections), strict=True):
        lines += [
            f"### {profile['index']}. {profile['title']}",
            "",
            (f"- **Tamaño:** {plural(profile['documents'], 'norma')} · "
             f"{plural(profile['units'], 'número')} normativos · {es(profile['words'])} "
             f"palabras · {plural(profile['figures'], 'figura')} · "
             f"{plural(len(profile['files']), 'archivo')}"),
            f"- **Modificaciones:** {changes_line(profile)}",
        ]
        if profile["topics"]:
            lines.append(f"- **Materias:** {', '.join(profile['topics'])}")
        if profile["excerpt"]:
            lines += [
                "",
                f"Cómo empieza (texto de la SP, {profile['excerpt_from']}):",
                "",
                f"> {profile['excerpt']}",
            ]
        lines.append("")
        for section in parts:
            label = (f"Parte {section['part']} de {section['parts']} · "
                     if section["parts"] > 1 else "")
            lines += [
                (f"{label}Archivo: `{section['filename']}` · {len(section['documents'])} "
                 f"normas · {es(sizes.get(section['filename'], 0))} palabras"),
                "",
            ]
            body = outline(section, documents, nodes)
            lines += body or ["- (sin subdivisiones)"]
            lines.append("")

    recent = latest_ncgs([(date, number, profile["roman"], profile["index"])
                          for profile in profiles for date, number in profile["changes"]])
    if recent:
        lines += [
            "## Modificaciones más recientes",
            "",
            ("Las últimas Normas de Carácter General que modificaron este Libro, según las "
             "notas de actualización del propio texto, y qué Títulos tocaron."),
            "",
            "| Fecha | NCG | Títulos |",
            "| --- | ---: | --- |",
        ]
        for date, number, romans in recent[:12]:
            lines.append(f"| {es_date(date)} | N° {number} | {', '.join(romans)} |")
        lines.append("")

    topics = topics_index(sections, documents)
    if topics:
        roman = {p["index"]: p["roman"] for p in profiles}
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
            lines.append(f"| {topic} | {', '.join(roman[w] for w in where)} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def root_index(summary: list[dict]) -> str:
    total = {k: sum(b[k] for b in summary)
             for k in ("sections", "titles", "documents", "units", "notes", "figures", "words")}
    lines = [
        "# Compendio de Normas del Sistema de Pensiones",
        "",
        "Superintendencia de Pensiones de Chile, extraído de su portal y convertido a Markdown.",
        "",
        ("El Compendio reúne en un solo cuerpo las instrucciones que la Superintendencia "
         "imparte a las Administradoras de Fondos de Pensiones y demás entidades del sistema. "
         "Se organiza en cinco Libros; cada Libro en Títulos, y cada Título en Letras, "
         "Capítulos y números normativos."),
        "",
        (f"**{total['titles']} Títulos en {total['sections']} archivos** en 5 Libros · "
         f"{es(total['documents'])} normas · "
         f"{es(total['units'])} números normativos · {es(total['notes'])} notas de "
         f"actualización · {es(total['figures'])} figuras · {es(total['words'])} palabras."),
        "",
        "## Los cinco Libros",
        "",
        "| Carpeta | Libro | Títulos | Archivos | Normas | Palabras | Última modificación | Extraído |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for book in summary:
        last = (f"NCG N° {book['last_change'][1]} ({es_date(book['last_change'][0])})"
                if book["last_change"] else "—")
        lines.append(
            (f"| `{book['folder']}/` | {book['name']} | {book['titles']} | {book['sections']} "
             f"| {book['documents']} | {es(book['words'])} | {last} "
             f"| {book['crawled_at'][:10] or '—'} |"),
        )

    lines += ["", "## Qué trata cada Libro", ""]
    for book in summary:
        lines += [
            f"### {book['name']}",
            "",
            f"**{book['full_name']}** · índice: `{book['folder']}/index.md`",
            "",
        ]
        for profile in book["profiles"]:
            files = profile["files"]
            where = (f"`{files[0]}`" if len(files) == 1
                     else f"{len(files)} partes, `{files[0]}` a `{files[-1]}`")
            topics = (f" · materias: {', '.join(profile['topics'][:4])}"
                      if profile["topics"] else "")
            lines.append(
                (f"- **{profile['title']}** — {plural(profile['documents'], 'norma')}, "
                 f"{es(profile['words'])} palabras · {where}{topics}"),
            )
        lines.append("")

    topics: dict[str, dict[str, list[str]]] = {}
    for book in summary:
        for profile in book["profiles"]:
            for topic in profile["topics"]:
                topics.setdefault(topic, {}).setdefault(book["roman"], []).append(
                    profile["roman"]
                )
    if topics:
        lines += [
            "## Materias en todo el Compendio",
            "",
            ("Las materias que la propia Superintendencia asocia a cada norma, y en qué Libro "
             "y Título aparecen. Es el atajo para saber a qué Libro ir antes de abrir su "
             "índice."),
            "",
            "| Materia | Dónde |",
            "| --- | --- |",
        ]
        for topic in sorted(topics):
            where = "; ".join(f"{book} (T. {', '.join(titles)})"
                              for book, titles in topics[topic].items())
            lines.append(f"| {topic} | {where} |")
        lines.append("")

    recent = latest_ncgs([
        (date, number, f"{book['roman']} T. {profile['roman']}", order * 100 + profile["index"])
        for order, book in enumerate(summary) for profile in book["profiles"]
        for date, number in profile["changes"]
    ])
    if recent:
        lines += [
            "## Modificaciones más recientes",
            "",
            ("Las últimas Normas de Carácter General que modificaron el Compendio, según las "
             "notas de actualización del propio texto."),
            "",
            "| Fecha | NCG | Dónde |",
            "| --- | ---: | --- |",
        ]
        for date, number, where in recent[:15]:
            lines.append(f"| {es_date(date)} | N° {number} | {', '.join(where)} |")
        lines.append("")

    lines += [
        "## Cómo está organizado",
        "",
        ("Una carpeta por Libro. Dentro, un archivo Markdown por **Título** —la unidad con la "
         "que la norma se cita y se modifica entera— y un `index.md` que dice qué regula cada "
         "Título, en qué archivo está cada Capítulo, sus materias y sus modificaciones."),
        "",
        (f"Un Título de más de {es(MAX_WORDS)} palabras se parte en varios archivos "
         "(`…-parte-1.md`, `…-parte-2.md`), para que cada uno quepa holgado en el contexto "
         "de un modelo. El corte va siempre entre Capítulos; cada parte declara en su "
         "encabezado cuál es y enlaza la anterior y la siguiente, y el `index.md` del Libro "
         "dice qué Capítulos trae cada una."),
        "",
        "```",
        "libro-i/",
        "├── index.md                      ← empezar aquí",
        "├── 01-01-titulo-i-afiliacion-....md",
        "└── ...",
        "```",
        "",
        ("Para ubicar una norma: leer el `index.md` del Libro, encontrar el Título —y la "
         "parte— que la contiene, y abrir ese archivo. Dentro, la jerarquía va como encabezados "
         "(`##` Letra, `###` Capítulo). Cada norma abre con una línea **Cita** —Libro, "
         "Título, Letra y Capítulo— y cierra con una línea **Fuente oficial** con su URL en el "
         "portal, así que cualquier fragmento suelto sigue diciendo de dónde es."),
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
         "cada norma su URL a la vista. Cualquier afirmación de este corpus se puede "
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

    target = book.output
    if target.exists():
        shutil.rmtree(target)
    # La carpeta se llamaba como el `slug` (`book-iii`); una vieja quedaría como duplicado.
    shutil.rmtree(OUTPUT / book.slug, ignore_errors=True)
    target.mkdir(parents=True)

    sizes: dict[str, int] = {}
    for section in sections:
        source = book.markdown / section["filename"]
        text = source.read_text(encoding="utf-8")
        sizes[section["filename"]] = words(text)
        shutil.copyfile(source, target / section["filename"])

    profiles = [title_profile(parts, documents, sizes) for parts in by_title(sections)]
    (target / "index.md").write_text(
        book_index(book, sections, documents, nodes, sizes, profiles), encoding="utf-8"
    )
    changes = [c for p in profiles for c in p["changes"]]
    return {
        "slug": book.slug,
        "folder": book.output.name,
        "name": book.name,
        "sections": len(sections),
        "titles": len({s["pvid"] for s in sections}),
        "documents": sum(len(s["documents"]) for s in sections),
        "units": sum(len(d["units"]) for d in documents.values()),
        "notes": sum(len(d["amendment_notes"]) for d in documents.values()),
        "figures": len({f for d in documents.values() for f in d["figures"]}),
        "words": sum(sizes.values()),
        "crawled_at": crawled_at(book),
        "roman": book.roman,
        "full_name": nodes.get(book.pvid, {}).get("title") or book.name,
        "profiles": profiles,
        "last_change": max(changes) if changes else None,
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
        (OUTPUT / "index.md").write_text(root_index(summary), encoding="utf-8")
        # El índice raíz se llamaba README.md; uno viejo quedaría como segundo índice.
        (OUTPUT / "README.md").unlink(missing_ok=True)
    print(
        (f"{'TOTAL':9} {sum(s['sections'] for s in summary):3} .md + "
         f"{len(summary)} índices -> {OUTPUT}"),
    )


if __name__ == "__main__":
    main()
