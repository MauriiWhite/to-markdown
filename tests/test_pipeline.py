"""Pruebas de las etapas deterministas contra páginas reales ya inspeccionadas.

Todo el pipeline es determinista, así que todo se prueba: no hay una mitad que dependa de
un servicio externo y quede fuera del alcance de la suite.
"""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import pytest

from to_markdown import BOOKS, BY_SLUG, Book
from to_markdown.stages.export import resolve
from to_markdown.stages.parse import NOTE, body_fragment, parse_document

TAGS = re.compile(r"<[^>]+>")


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def images_index() -> dict[str, str]:
    """Índice `src -> sha256` de los cinco Libros, unido.

    Unir no pisa nada: se verificó que ninguna de las 1.743 figuras del corpus aparece en
    dos Libros distintos, y por eso cada Libro puede deduplicar dentro de su carpeta sin
    coordinarse con los otros.
    """
    index: dict[str, str] = {}
    for book in BOOKS:
        path = book.file("images.json")
        if path.exists():
            index.update(json.loads(path.read_text(encoding="utf-8")))
    return index


@pytest.fixture(scope="module")
def documents(images_index) -> dict[str, dict]:
    """Documentos parseados desde HTML congelado en el repo.

    A propósito NO se leen de `data/`, que está en .gitignore: unas pruebas que dependen de
    datos no versionados se saltan en silencio en un clon limpio, y una prueba que se salta
    sola no protege de nada. Estas páginas son reales y cubren los casos que ya fallaron.
    """
    out = {}
    for path in sorted(FIXTURES.glob("*.html")):
        pvid = path.stem
        document = parse_document(pvid, path.read_text(encoding="utf-8"), images_index)
        if document:
            out[pvid] = document
    return out


@pytest.fixture(scope="module", params=[book.slug for book in BOOKS])
def book_corpus(request) -> tuple[Book, list[dict]]:
    """El corpus de un Libro, uno por parámetro. Se salta si no está construido.

    Va por Libro y no sobre el total porque las invariantes también: un total holgado
    esconde un Libro roto.
    """
    book = BY_SLUG[request.param]
    path = book.file("documents.json")
    if not path.exists():
        pytest.skip(f"{book.slug} no construido: `uv run python -m to_markdown crawl parse`")
    return book, json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def corpus_by_book() -> dict[str, list[dict]]:
    """Los cinco corpus a la vez, para lo que solo se puede comprobar comparándolos."""
    out = {}
    for book in BOOKS:
        path = book.file("documents.json")
        if path.exists():
            out[book.slug] = json.loads(path.read_text(encoding="utf-8"))
    if len(out) < len(BOOKS):
        pytest.skip("corpus incompleto: `uv run python -m to_markdown crawl parse`")
    return out


def test_full_hierarchy(documents):
    """La jerarquía se lee del breadcrumb, no se infiere."""
    doc = documents["4074"]
    hierarchy = doc["hierarchy"]
    assert hierarchy["book"].startswith("Libro I ")
    assert hierarchy["title"].startswith("Título I ")
    assert hierarchy["letter"].startswith("A. ")
    assert hierarchy["chapter"] == "Capítulo II. Normas generales de Afiliación"
    assert doc["topics"] == ["Afiliación a una A.F.P.", "Afiliado"]
    assert doc["path"].startswith("Libro I, Título I, Letra A")


def test_amendment_notes(documents):
    """Dicen qué NCG modificó cada número: es el metadato de vigencia."""
    notes_seen = documents["4074"]["amendment_notes"]
    assert any("Norma de Carácter General Nº 31" in n for n in notes_seen)
    assert all(not NOTE.match(n) for n in notes_seen), "el encabezado debe venir ya recortado"


def test_no_note_is_lost(documents):
    """Invariante del corpus: toda `<h6>` que sea nota de actualización queda registrada.

    Vale la pena como prueba porque ya falló una vez: el Manual de Cuentas mete sus notas
    dentro de celdas de tabla, donde el parser las estaba tragando en silencio.
    """
    expected_set = extracted = 0
    for pvid, doc in documents.items():
        body = body_fragment((FIXTURES / f"{pvid}.html").read_text(encoding="utf-8"))
        raw = [
            TAGS.sub("", t).replace("\xa0", " ").strip()
            for t in re.findall(r"<h6[^>]*>(.*?)</h6>", body, re.DOTALL)
        ]
        expected_set += sum(1 for t in raw if NOTE.match(t))
        extracted += len(doc["amendment_notes"])
    assert extracted >= expected_set, f"se perdieron notas: {expected_set} en HTML, {extracted} extraídas"


def test_subscripts_become_math_notation(documents):
    """`<sub>`/`<sup>` son notación matemática en este corpus, no notas al pie."""
    markdown = documents["4305"]["markdown"]
    assert "VC_{i}" in markdown and "VC_{j}" in markdown
    assert "UF_{i}" in markdown
    assert "<sub>" not in markdown and "<sup>" not in markdown


def test_a_table_without_th_promotes_no_data(documents):
    """367 de 371 tablas no traen `<th>`: promover la primera fila convertiría un dato
    en un rótulo."""
    markdown = documents["10683"]["markdown"]
    assert "|  |  |\n| --- | --- |\n| 1 | Sano |" in markdown
    for value in ("1,2353", "1,4706", "1,8235", "2,3774"):
        assert f"| {value} |" in markdown


def test_every_referenced_figure_exists(documents, images_index):
    """Ningún marcador huérfano: si una imagen no se pudo descargar queda FIG-MISSING,
    que es visible, nunca un hueco silencioso."""
    known = set(images_index.values())
    for doc in documents.values():
        for digest in re.findall(r"\[\[FIG:([0-9a-f]{64})\]\]", doc["markdown"]):
            assert digest in known, f"{doc['pvid']} referencia una figura desconocida"


def test_the_figure_points_at_the_sp_site():
    """Lo único que este corpus promete sobre una figura es su procedencia: el Markdown
    tiene que servir la imagen desde el sitio de la Superintendencia, no desde una copia.

    Una ruta local obligaría a confiar en que alguien copió bien el archivo; la URL se
    puede abrir y contrastar contra la fuente en un clic.
    """
    digest = "a" * 64
    painted = resolve(f"[[FIG:{digest}]]", {}, {digest: "articles-1_recurso_1.jpg"})
    assert "![Figura](https://www.spensiones.cl/portal/compendio/596/articles-1_recurso_1.jpg)" in painted
    assert digest in painted, "el hash de la copia local queda en la traza"
    assert "[[FIG:" not in painted






def test_an_undownloaded_image_keeps_its_link():
    """Vale como prueba porque ya falló: la imagen que no se pudo bajar salía como un
    comentario mudo y ahí se perdía la referencia. El enlace al sitio de la SP puede
    funcionar perfectamente aunque nuestro `urlopen` fallara ese día.
    """
    painted = resolve("[[FIG-MISSING:articles-7457_recurso_1.jpg]]", {})
    assert "![Figura](https://www.spensiones.cl/portal/compendio/596/articles-7457_recurso_1.jpg)" in painted
    assert "[[FIG-MISSING:" not in painted


def test_no_corpus_figure_loses_its_origin(documents, images_index):
    """Sobre el corpus real: todo marcador resuelto queda como una imagen enlazada al
    sitio de la SP, nunca como un hueco."""
    sources = {digest: src for src, digest in images_index.items()}
    for doc in documents.values():
        if not doc["figures"]:
            continue
        painted = resolve(doc["markdown"], {}, sources)
        assert "[[FIG:" not in painted, f"{doc['pvid']} dejó un marcador sin resolver"
        for digest in doc["figures"]:
            expected = f"![Figura](https://www.spensiones.cl/portal/compendio/596/{sources[digest]})"
            assert expected in painted, f"{doc['pvid']} perdió el origen de {digest[:12]}"


# --- unidades direccionables -------------------------------------------------

def test_numbered_units_are_addressable(documents):
    """El diff y la cita necesitan granularidad de número, no de documento."""
    unit_ids = documents["4074"]["units"]
    numbers = [u["number"] for u in unit_ids if u["number"]]
    assert numbers == sorted(numbers, key=int), "las unidades deben salir en orden"
    four = next(u for u in unit_ids if u["number"] == "4")
    assert four["unit_id"] == "4074#4"
    assert four["citation"].endswith("N° 4")
    assert "trabajadores independientes" in four["text"]
    assert len(four["sha256"]) == 64


def test_two_hashes_separate_norm_from_parser(documents):
    """Con un solo hash, cada mejora al parser se vería como si la norma hubiera cambiado."""
    doc = documents["4074"]
    assert doc["source_sha256"] != doc["content_sha256"]
    assert doc["schema_version"] >= 1


# --- detección de cambios ----------------------------------------------------

def _doc(pvid="4074", source="s1", content="c1", notes=(), units=()):
    return {
        "pvid": pvid, "url": f"http://x/{pvid}", "citation": "Libro I, N",
        "source_sha256": source, "content_sha256": content,
        "amendment_notes": list(notes), "units": list(units),
    }


def _unit(number, text, unit_id=None):
    import hashlib
    return {
        "unit_id": unit_id or f"4074#{number}", "number": number, "citation": f"c N° {number}",
        "text": text, "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }


def test_change_classification():
    from to_markdown.stages.changes import classify

    assert classify(_doc(), _doc()) is None
    # La fuente cambió pero nuestra salida no: el CMS tocó la página.
    assert classify(_doc(), _doc(source="s2")) == "cosmetic"
    # Nuestra salida cambió pero la fuente no: cambió el parser, no la norma.
    assert classify(_doc(), _doc(content="c2")) == "pipeline"
    # Ambas cambiaron sin nota que lo declare.
    assert classify(_doc(), _doc(source="s2", content="c2")) == "editorial"
    # Ambas cambiaron y la norma lo declara.
    assert classify(_doc(), _doc(source="s2", content="c2", notes=["NCG 370 …"])) == "normative"


def test_renumbering_is_not_reported_as_modification():
    """93 notas del corpus documentan renumeraciones. Emparejar solo por número
    reportaría decenas de cambios falsos en cada una."""
    from to_markdown.stages.changes import diff_units

    before = [_unit("3", "texto tres"), _unit("4", "texto cuatro")]
    after = [_unit("5", "texto tres", "4074#5"), _unit("6", "texto cuatro", "4074#6")]
    events = diff_units(before, after)
    assert {e["type"] for e in events} == {"renumbered"}
    assert {(e["from"], e["to"]) for e in events} == {("3", "5"), ("4", "6")}


def test_a_real_modification_carries_its_diff():
    from to_markdown.stages.changes import diff_units

    events = diff_units([_unit("1", "el plazo es de 10 días")],
                         [_unit("1", "el plazo es de 15 días")])
    assert len(events) == 1 and events[0]["type"] == "modified"
    assert "-el plazo es de 10 días" in events[0]["diff"]
    assert "+el plazo es de 15 días" in events[0]["diff"]


def test_a_different_hash_with_equal_text_is_no_change():
    """Un diff vacío en un changelog se lee como un fallo de la herramienta."""
    from to_markdown.stages.changes import diff_units

    a = _unit("1", "mismo texto")
    b = {**_unit("1", "mismo texto"), "sha256": "z" * 64}
    assert diff_units([a], [b]) == []


# --- invariantes -------------------------------------------------------------

def test_invariants_accept_the_real_corpus(book_corpus):
    from to_markdown.core.guard import check

    book, documents = book_corpus
    assert check(book, documents) == []


def test_invariants_catch_a_degraded_scraper(book_corpus):
    """El peor fallo de un scraper no es caerse: es devolver menos, en silencio."""
    from to_markdown.core.guard import check

    book, documents = book_corpus
    empty_targets = [{**d, "markdown": "", "figures": [], "units": []} for d in documents]
    issues = check(book, empty_targets)
    assert any("have content" in p for p in issues)
    assert any("empty documents" in p for p in issues)
    assert check(book, documents[:5]), "un corpus truncado debe ser rechazado"


def test_a_degraded_book_does_not_drag_the_others(corpus_by_book):
    """La razón de evaluar por Libro: perder entero el Libro I deja 1.074 documentos,
    todavía por encima de cualquier cota global razonable. Sobre el total, ese fallo pasa
    inadvertido; sobre su propio Libro, aborta."""
    from to_markdown.core.guard import check

    book_i = BY_SLUG["book-i"]
    assert check(book_i, []), "un Libro vacío debe ser rechazado por su propia cota"
    for slug, documents in corpus_by_book.items():
        if slug != book_i.slug:
            assert check(BY_SLUG[slug], documents) == [], f"{slug} no debería verse afectado"


# --- separación por Libro ----------------------------------------------------

def test_every_document_lives_in_its_own_book_folder(book_corpus):
    """La partición es exacta, no aproximada: cada norma cuelga de la raíz del Libro en
    cuya carpeta está guardada. El primer nivel del breadcrumb es esa raíz."""
    book, documents = book_corpus
    for document in documents:
        assert document["breadcrumb"], f"{document['pvid']} sin breadcrumb"
        assert document["breadcrumb"][0]["pvid"] == book.pvid, (
            f"{document['pvid']} está en {book.slug} pero cuelga de "
            f"{document['breadcrumb'][0]['pvid']}"
        )


def test_a_books_manifest_holds_only_its_own_root(book_corpus):
    """Si el crawl se saliera de su subárbol, la carpeta dejaría de contener lo que dice."""
    book, _ = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    assert manifest["book"]["pvid"] == book.pvid
    roots = [p for p, n in manifest["nodes"].items() if n["parent"] is None]
    assert roots == [book.pvid]


def test_a_books_cache_is_exactly_its_tree(book_corpus):
    """Ni un HTML de más ni uno de menos: el caché particionado tiene que corresponder
    nodo a nodo con el manifiesto de su Libro."""
    book, _ = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    on_disk = {path.stem for path in book.cache.glob("*.html")}
    assert on_disk == set(manifest["nodes"]), (
        f"{book.slug}: sobran {sorted(on_disk - set(manifest['nodes']))[:5]}, "
        f"faltan {sorted(set(manifest['nodes']) - on_disk)[:5]}"
    )


def test_no_figure_is_shared_between_books(corpus_by_book):
    """Es la premisa que permite que cada Libro deduplique por su cuenta. Si un día una
    figura apareciera en dos Libros, se guardaría dos veces —correcto, pero deja de ser
    cierto que el total de figuras sea la suma de las partes, y el informe mentiría."""
    owners: dict[str, set[str]] = {}
    for slug, documents in corpus_by_book.items():
        for document in documents:
            for digest in document["figures"]:
                owners.setdefault(digest, set()).add(slug)
    shared = {d: b for d, b in owners.items() if len(b) > 1}
    assert not shared, f"{len(shared)} figuras en más de un Libro: {list(shared)[:3]}"


# --- CLI ---------------------------------------------------------------------

def test_book_flag_selects_a_subset_in_compendium_order():
    """`--book` es lo que hace barata una reprocesada: acota el trabajo al Libro que hay que
    reprocesar, y arreglar el Libro III no debería obligar a repasar los otros cuatro.

    El orden de salida es el del Compendio (I…V), no el que escribió quien invoca: los
    informes se leen en ese orden.
    """
    from to_markdown.__main__ import parse_args

    stages, books = parse_args(["parse", "--book", "book-v", "-b", "book-i"])
    assert stages == ["parse"]
    assert [b.slug for b in books] == ["book-i", "book-v"]

    stages, books = parse_args([])
    assert stages[0] == "crawl" and len(books) == len(BOOKS)
    # `refresh` es la alternativa a `crawl`, no su continuación: correr ambos revalidaba
    # contra el servidor 1.478 páginas recién bajadas, para nada.
    assert "refresh" not in stages


def test_unknown_book_runs_nothing():
    """Un slug mal escrito tiene que fallar antes de tocar disco, no a media corrida."""
    from to_markdown.__main__ import parse_args

    with pytest.raises(SystemExit):
        parse_args(["parse", "--book", "book-vi"])
    with pytest.raises(SystemExit):
        parse_args(["parsear"])


# --- nodos con hijos Y cuerpo -------------------------------------------------

def test_a_node_with_children_can_have_a_body(book_corpus):
    """Vale como prueba porque ya falló, y en silencio: el pipeline usaba `is_leaf` como
    sinónimo de "tiene texto normativo" y descartaba 24 nodos que tienen ambas cosas —un
    Título que además imparte instrucciones, un Capítulo con preámbulo antes de sus
    números—. Eran 190.502 caracteres que el PDF de la SP sí imprime.
    """
    book, documents = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    nodes = manifest["nodes"]
    assert set(manifest["documents"]) == {d["pvid"] for d in documents}
    assert all(nodes[pvid]["has_body"] for pvid in manifest["documents"])
    # Y ninguna página con cuerpo puede quedar fuera, tenga hijos o no.
    assert {p for p, n in nodes.items() if n["has_body"]} == set(manifest["documents"])


def test_the_order_is_reading_order_not_pvid_order(book_corpus):
    """El Compendio se lee y se imprime en orden de árbol. Ordenar por pvid pondría al
    final cualquier capítulo agregado después, aunque normativamente vaya al medio."""
    book, documents = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    assert [d["pvid"] for d in documents] == manifest["documents"]
    assert manifest["order"][0] == book.pvid, "el árbol arranca en la raíz del Libro"


# --- agrupación por capítulo --------------------------------------------------

def test_every_document_falls_in_exactly_one_chapter(book_corpus):
    """La agrupación tiene que ser una partición: un documento repetido se leería dos
    veces y uno perdido no se leería nunca."""
    from to_markdown.stages.export import sections

    book, documents = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    grouped = sections(manifest, documents)
    observed = [d["pvid"] for c in grouped for d in c["documents"]]
    assert sorted(observed) == sorted(d["pvid"] for d in documents)
    assert len(observed) == len(set(observed))
    assert len({c["filename"] for c in grouped}) == len(grouped), "nombres de archivo únicos"


def test_homonymous_chapters_do_not_merge(book_corpus):
    """"Capítulo I. Introducción" aparece 11 veces solo en el Libro III, bajo Letras
    distintas. Agrupar por el texto del título las fundiría en un archivo; se agrupa por
    el nodo del árbol justamente para que no pase."""
    from to_markdown.stages.export import sections

    book, documents = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    grouped = sections(manifest, documents)
    titles = collections.Counter(c["title"] for c in grouped)
    repeated = [t for t, n in titles.items() if n > 1]
    for title in repeated:
        same = [c for c in grouped if c["title"] == title]
        assert len({c["pvid"] for c in same}) == len(same), f"{title} se fundió"
        assert len({c["filename"] for c in same}) == len(same), f"{title} pisa su archivo"


def test_the_chapter_ordinal_does_not_depend_on_how_many_are_passed(book_corpus):
    """El nombre de archivo tiene que ser el mismo aunque falten capítulos, o el lado PDF
    —que solo trae los que alineó— nombraría distinto y el `diff` dejaría de servir."""
    from to_markdown.stages.export import sections

    book, documents = book_corpus
    manifest = json.loads(book.file("manifest.json").read_text(encoding="utf-8"))
    complete = {c["pvid"]: c["filename"] for c in sections(manifest, documents)}
    partial = {c["pvid"]: c["filename"] for c in sections(manifest, documents[::2])}
    assert all(complete[pvid] == name for pvid, name in partial.items())


def test_body_headings_sink_below_the_chapter_heading():
    """Un `#` del cuerpo competiría con el título del archivo y aplanaría el índice."""
    from to_markdown.stages.export import demote

    assert demote("# uno\n\n## dos\n\ntexto") == "### uno\n\n#### dos\n\ntexto"
    assert demote("###### ya al fondo") == "###### ya al fondo", "no puede pasar de h6"
    assert demote("no es #encabezado") == "no es #encabezado"


# --- lado PDF ----------------------------------------------------------------

def test_the_pdf_text_keeps_its_capitals():
    """La caja se baja solo para comparar. Un compendio normativo en minúsculas no es una
    transcripción fiel, es la herramienta de comparación filtrándose al entregable."""
    from to_markdown.stages.compare import canonical, normalize

    assert canonical("  Norma  de\nCarácter   General ") == "Norma de Carácter General"
    assert normalize("Norma De Carácter") == "norma de carácter"
    # Los offsets del texto en caja original y en minúsculas tienen que coincidir.
    joined = canonical("Título III. Depósitos Convenidos ÑÁÉÍÓÚ")
    assert len(joined.lower()) == len(joined)


def test_the_pdf_markdown_restores_paragraphs_and_notes():
    """`pdftotext` entrega un chorro plano; sin esto, un capítulo entero es un solo
    párrafo y la nota de vigencia queda enterrada dentro de él."""
    from to_markdown.stages.compare import to_markdown

    flat = (
        "Capítulo II. Normas 1. Primer número del texto. 2. Segundo número aquí. "
        "Nota de actualización: Este número fue modificado por la NCG Nº 31."
    )
    painted = to_markdown(flat, "Capítulo II. Normas")
    assert painted.startswith("1. Primer número"), "el título ya va en el encabezado"
    assert "\n\n2. Segundo número" in painted
    assert "> **Nota de actualización:** Este número fue modificado" in painted
    # Un decimal no puede partirse como si fuera un número normativo.
    assert "\n\n" not in to_markdown("el monto es de $1.500 pesos en total.")


def test_pdf_and_web_produce_the_same_file_names(book_corpus):
    """Los dos árboles se comparan con `diff`, así que el nombre tiene que calzar."""
    book, _ = book_corpus
    if not any(book.pdf_markdown.glob("*.md")):
        pytest.skip("comparativa no construida: `uv run python -m to_markdown compare`")
    web = {p.name for p in book.markdown.glob("*.md")}
    pdf = {p.name for p in book.pdf_markdown.glob("*.md")}
    assert pdf <= web, f"el PDF produjo capítulos que la web no tiene: {sorted(pdf - web)[:3]}"


def test_the_comparison_finds_no_foreign_content(book_corpus):
    """El hallazgo que importa: el PDF oficial no trae normativa que el portal no tenga.

    Se fija en 1% y no en 0 porque la capa de texto del PDF aplana las tablas y el orden de
    las celdas cambia; eso se clasifica aparte como `reformatted`. Lo que este umbral vigila
    es que no aparezca contenido ajeno de verdad.
    """
    book, _ = book_corpus
    path = book.file_pdf("coverage.json")
    if not path.exists():
        pytest.skip("comparativa no construida: `uv run python -m to_markdown compare`")
    report = json.loads(path.read_text(encoding="utf-8"))
    words = sum(d["pdf_words"] for d in report["documents"]) or 1
    assert report["extra_words_in_pdf"] / words < 0.01
    assert report["aligned"] / report["web_documents"] > 0.95


def test_what_does_not_anchor_is_not_declared_missing(book_corpus):
    """"No lo pude anclar" y "no está en el PDF" son cosas distintas.

    Vale como prueba porque ya me hizo afirmar de más: los 5 documentos que no anclan
    tienen entre 88% y 100% de su vocabulario en el PDF. Lo que falla es el encabezado, no
    el contenido, y el informe tiene que decir eso y no lo otro.
    """
    book, _ = book_corpus
    path = book.file_pdf("coverage.json")
    if not path.exists():
        pytest.skip("comparativa no construida: `uv run python -m to_markdown compare`")
    report = json.loads(path.read_text(encoding="utf-8"))
    assert "missing_in_pdf" not in report, "esa clave afirmaba ausencia sin medirla"
    for item in report["unanchored"]:
        assert "lexical_in_pdf" in item, f"{item['pvid']} sin medir si su texto está"


# --- User-Agent ---------------------------------------------------------------

def test_the_user_agent_rotates_per_request():
    """Uno por petición, de escritorio, y sin salir a la red para conseguirlo: el catálogo
    viene empaquetado, así que no agrega un punto de fallo al crawl."""
    from to_markdown.infra.net import user_agent

    samples = {user_agent() for _ in range(40)}
    assert len(samples) > 1, "no está rotando"
    assert all("Mozilla/" in agent for agent in samples)


def test_figures_are_compared_by_content_not_by_file(book_corpus):
    """Contar archivos daba 122 figuras "de más" en el PDF que no existían.

    El PDF embebe la misma figura varias veces con compresión distinta —bytes distintos,
    SHA-256 distinto— y el portal la sirve en JPG donde `pdfimages` devuelve PNG. Por
    archivo no se pueden comparar; por píxeles, 1.714 de 1.744 son la misma.
    """
    book, _ = book_corpus
    path = book.file_pdf("coverage.json")
    if not path.exists():
        pytest.skip("comparativa no construida: `uv run python -m to_markdown compare`")
    figures = json.loads(path.read_text(encoding="utf-8"))["figures"]
    assert figures["shared"] / max(1, figures["web_distinct"]) > 0.95
    assert figures["pdf_distinct"] <= figures["pdf_files"], "el archivo nunca sub-cuenta"


def test_every_figure_reference_resolves(book_corpus):
    """Las figuras van por referencia y no embebidas en base64 (decisión medida: embeber
    lleva el árbol de 9,7 MB a 386 MB y deja archivos de 19 MB, ilegibles para chunking).

    El precio de referenciar es que la ruta relativa tiene que resolver: un `![](...)` roto
    no falla, simplemente no muestra nada, que es la clase de pérdida silenciosa que este
    proyecto no acepta en ningún otro lado.
    """
    book, _ = book_corpus
    if not any(book.pdf_markdown.glob("*.md")):
        pytest.skip("comparativa no construida: `uv run python -m to_markdown compare`")
    reference_text = re.compile(r"!\[[^\]]*\]\((\.\./images/[^)]+)\)")
    for path in book.pdf_markdown.glob("*.md"):
        for reference in reference_text.findall(path.read_text(encoding="utf-8")):
            assert (path.parent / reference).resolve().exists(), f"{path.name} -> {reference}"



















# --- bundle -------------------------------------------------------------------

def test_the_bundle_has_one_index_per_book(book_corpus):
    """`output/` es lo único que se entrega, y el índice es lo que lo hace navegable.

    Sin él, ubicar "el Capítulo XXIV del Título III" obliga a leer los 12 archivos del
    Libro; con él, es una consulta al índice y después un solo archivo. Para un modelo esa
    diferencia es entre buscar y encontrar.
    """
    from to_markdown import OUTPUT

    book, _ = book_corpus
    folder = OUTPUT / book.slug
    if not folder.exists():
        pytest.skip("bundle no construido: `uv run python -m to_markdown bundle`")
    index_text = folder / "index.md"
    assert index_text.is_file(), f"{book.slug} sin index.md"

    section_records = json.loads(book.file("sections.json").read_text(encoding="utf-8"))
    delivered = {p.name for p in folder.glob("*.md")} - {"index.md"}
    assert delivered == {s["filename"] for s in section_records}, "el bundle no calza con export"

    joined = index_text.read_text(encoding="utf-8")
    for section in section_records:
        assert section["filename"] in joined, f"{section['filename']} no está en el índice"
        assert section["title"] in joined


def test_the_index_promises_no_missing_files(book_corpus):
    """Un índice que apunta a un archivo ausente es peor que no tener índice: manda al
    lector —o al modelo— a buscar algo que no existe."""
    from to_markdown import OUTPUT

    book, _ = book_corpus
    folder = OUTPUT / book.slug
    if not folder.exists():
        pytest.skip("bundle no construido: `uv run python -m to_markdown bundle`")
    cited = set(re.findall(r"`([^`]+\.md)`", (folder / "index.md").read_text(encoding="utf-8")))
    for name in cited:
        assert (folder / name).is_file(), f"el índice cita {name}, que no está"


def test_the_bundle_drags_nothing_from_the_work_area():
    """`output/` se entrega a terceros: no puede llevar caché, estado ni intermedios."""
    from to_markdown import BOOKS, OUTPUT

    if not OUTPUT.exists():
        pytest.skip("bundle no construido: `uv run python -m to_markdown bundle`")
    allowed = {"README.md"} | {b.slug for b in BOOKS}
    assert {p.name for p in OUTPUT.iterdir()} <= allowed
    for book in BOOKS:
        folder = OUTPUT / book.slug
        if folder.exists():
            assert all(p.suffix == ".md" for p in folder.iterdir()), "solo Markdown"
            assert not any(p.is_dir() for p in folder.iterdir())


# --- descarga del PDF oficial -------------------------------------------------------


def test_the_pdf_url_comes_from_the_pvid():
    """El enlace del Libro completo se deriva del pvid, que es la única clave estable del
    árbol. Si saliera de una lista aparte, habría dos fuentes de verdad que mantener."""
    from to_markdown.stages.pdf import source_url

    for book in BOOKS:
        assert source_url(book).endswith(f"fo-propertyvalue-{book.pvid}.pdf")


def test_the_pdf_breadcrumb_is_normalized_before_crossing():
    """El PDF escribe "Libro III,Título V" sin el espacio tras la coma en algunas páginas.
    Sin uniformar, esas secciones saldrían huérfanas contra el árbol del crawler."""
    from to_markdown.stages.pdf import _spaced

    assert _spaced("Libro III,Título V, Letra P") == "Libro III, Título V, Letra P"
    assert _spaced("Libro  III,  Título  V") == "Libro III, Título V"


def test_every_pdf_verifies_only_against_its_own_book():
    """La razón de ser de la etapa: renombrar a `Book<N>.pdf` sin comprobar de qué Libro es
    dejaría que un PDF equivocado se comparara contra el árbol de otro, y la cobertura
    saldría llena de "contenido solo en el PDF" sin que nada avisara.

    Se prueban los 25 emparejamientos: los 5 correctos pasan, los 20 restantes se rechazan.
    """
    from to_markdown.stages.pdf import verify

    available = [b for b in BOOKS if b.pdf_source.exists()]
    if len(available) < 2:
        pytest.skip("sin PDF oficiales: `uv run python -m to_markdown pdf`")

    for file in available:
        for candidate in available:
            problems, matched = verify(file.pdf_source, candidate)
            if file.slug == candidate.slug:
                assert not problems, f"{file.pdf_file} rechazado como propio: {problems}"
                assert matched, f"{file.pdf_file} no cruzó ninguna sección con el crawl"
            else:
                assert problems, (
                    f"{file.pdf_file} pasó como {candidate.pdf_file}: "
                    f"un Libro equivocado se compararía contra el árbol de otro"
                )


def test_the_running_head_does_not_confuse_body_with_cover():
    """El cuerpo normativo también nombra al Compendio ("…del Libro I del Compendio de
    Normas del Sistema de Pensiones. Información"). Tomar cualquier línea que lo mencione
    daba un falso positivo que rechazaba un PDF correcto."""
    from to_markdown.stages.pdf import RUNNING_HEAD

    assert RUNNING_HEAD.findall(
        "Compendio de Normas del Sistema de Pensiones - Libro IV\n"
    ) == ["Libro IV"]
    assert not RUNNING_HEAD.findall("Compendio de Normas del Sistema de Pensiones.\n")
    assert not RUNNING_HEAD.findall(
        "Título IV del Libro I del Compendio de Normas del Sistema de Pensiones. Información\n"
    )


def test_the_downloaded_pdf_covers_the_tree_the_crawler_walked(book_corpus):
    """No basta con que el PDF diga "Libro III": tiene que ser el mismo Libro III que
    extrajo el crawler. Las secciones muestreadas del PDF se cruzan contra los `path` de
    `documents.json`, que es el árbol que el pipeline recorrió de verdad."""
    from to_markdown.stages.pdf import verify

    book, _ = book_corpus
    if not book.pdf_source.exists():
        pytest.skip(f"falta {book.pdf_file}: `uv run python -m to_markdown pdf -b {book.slug}`")
    problems, matched = verify(book.pdf_source, book)
    assert not problems, problems
    assert matched >= 2, f"solo {matched} secciones cruzadas con el árbol de {book.slug}"


# --- transporte HTTP: keep-alive, gzip y sus trampas -----------------------------------


def test_the_etag_gzip_suffix_is_normalized():
    """La trampa más cara del gzip, y silenciosa: Apache le agrega `-gzip` al ETag cuando
    sirve comprimido, y ese ETag **nunca vuelve a calzar** — devolverlo en `If-None-Match`
    responde 200, no 304.

    Sin normalizarlo, pedir gzip habría hecho que `refresh` re-descargara las 1.476 páginas
    en cada corrida en vez de recibirlas como 304 de cero bytes, y nada lo habría avisado:
    el corpus seguía saliendo correcto, solo que tardando veinte veces más.
    """
    from to_markdown.infra.net import GZIP_ETAG

    assert GZIP_ETAG.sub(r"\1", '"17444-65ae6d357f9c0-gzip"') == '"17444-65ae6d357f9c0"'
    assert GZIP_ETAG.sub(r"\1", "W/-gzip") == "W/"
    # Un ETag que ya viene limpio no se toca.
    assert GZIP_ETAG.sub(r"\1", '"17444-65ae6d357f9c0"') == '"17444-65ae6d357f9c0"'
    # Ni uno cuyo contenido simplemente termine en algo parecido.
    assert GZIP_ETAG.sub(r"\1", '"abc-gzipped"') == '"abc-gzipped"'


def test_the_path_is_extracted_with_its_query():
    """`http.client` pide la ruta, no la URL entera. Las imágenes traen `?ts=...` y perder
    el query devolvería una versión distinta del archivo."""
    from to_markdown.infra.net import url_path

    assert url_path("https://x.cl/a/b.html") == "/a/b.html"
    assert url_path("https://x.cl/a/img.jpg?ts=1787241414") == "/a/img.jpg?ts=1787241414"


def test_a_dead_connection_reopens_itself():
    """El servidor cierra las conexiones ociosas: la primera petición después de eso falla
    con `RemoteDisconnected`. Reusar esa conexión arrastraría el fallo a toda la tanda."""
    import http.client

    from to_markdown.infra.net import connection

    first = connection(reset=True)
    first.close()
    second = connection(reset=True)
    assert second is not first
    assert isinstance(second, http.client.HTTPSConnection)


def test_the_connection_pool_is_per_thread():
    """Una conexión HTTP/1.1 sirve una petición a la vez. Si dos hilos compartieran la
    misma, sus respuestas se mezclarían."""
    import threading
    from concurrent.futures import ThreadPoolExecutor

    from to_markdown.infra.net import connection

    # La barrera obliga a que los tres hilos estén dentro a la vez: sin ella `pool.map`
    # puede despachar las tres tareas al mismo hilo y la prueba pasaría sin probar nada.
    gate = threading.Barrier(3, timeout=10)

    def grab_connection(_: int) -> int:
        conn = connection(reset=True)
        gate.wait()
        return id(conn)

    with ThreadPoolExecutor(3) as pool:
        connections = list(pool.map(grab_connection, range(3)))
    assert len(set(connections)) == 3, "dos hilos compartieron conexión"


def test_the_memoized_visual_key_equals_the_computed_one(book_corpus):
    """La memoización de `compare_figures` es exacta y no una aproximación: el nombre del
    archivo ES el SHA-256 de su contenido, así que su huella no puede cambiar.

    Se comprueba contra la huella recalculada, que es lo que rompería si alguien cambiara
    el tamaño o el modo de la miniatura sin invalidar el caché.
    """
    import json

    from to_markdown.stages.compare import visual_key

    book, _ = book_corpus
    cache_path = book.file_pdf("visual_keys.json")
    if not cache_path.exists():
        pytest.skip(f"{book.slug} sin comparativa: `uv run python -m to_markdown compare`")

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    reviewed = 0
    for folder in (book.images, book.pdf_images):
        for path in sorted(folder.iterdir())[:5]:
            if path.name not in cache:
                continue
            expected = visual_key(path)
            assert cache[path.name] == (expected.hex() if expected else "")
            reviewed += 1
    assert reviewed, "el caché no cubrió ninguna figura del Libro"


def test_the_ngram_is_exact_identity_not_a_hash():
    """`shingles` devuelve tuplas de palabras en vez de la cadena unida, por velocidad. El
    cambio solo es legítimo si la identidad es **exactamente** la misma: dos n-gramas son
    iguales si y solo si sus palabras lo son, sin colisiones ni aproximación.

    Un hash rodante habría sido más rápido todavía, y habría podido inflar la cobertura al
    dar por presente un pasaje que no está — que es justo lo que la etapa mide.
    """
    from to_markdown.stages.compare import shingles

    a = {s for s, _ in shingles("el afiliado debe presentar la solicitud ante la A F P", 4)}
    b = {s for s, _ in shingles("la solicitud ante la A F P se presenta", 4)}
    assert ("la", "solicitud", "ante", "la") in a & b
    # Mismas palabras en otro orden NO son el mismo n-grama.
    assert ("ante", "solicitud", "la", "la") not in a
    # La posición acompaña al n-grama y es la de su primera palabra.
    joined = "uno dos tres cuatro cinco"
    assert [joined[p:].split()[0] for _, p in shingles(joined, 2)] == [
        "uno", "dos", "tres", "cuatro"
    ]


def test_text_shorter_than_the_ngram_matches_none():
    """El caso borde del corpus: anexos de una línea. Devuelven un n-grama con todas sus
    palabras, que por ser más corto no puede igualar a uno de tamaño completo."""
    from to_markdown.stages.compare import shingles

    short = shingles("solo tres palabras", 8)
    assert short == [(("solo", "tres", "palabras"), 0)]
    assert not shingles("", 8)
    long = {s for s, _ in shingles("solo tres palabras y algunas mas para llegar a ocho", 8)}
    assert short[0][0] not in long


# --- TUI ------------------------------------------------------------------------------


def test_the_tui_captures_what_the_stages_print():
    """Las etapas usan `print`, que es lo correcto para una CLI. La TUI las captura en vez
    de reescribirlas para que emitan eventos: un `print` no puede quedar desincronizado de
    lo que la CLI enseña, y un sistema de eventos paralelo sí."""
    from to_markdown.tui import _Tee

    collected: list[str] = []
    tee = _Tee(collected.append)
    tee.write("una linea\ny me")
    assert collected == ["una linea"], "no debe emitir una línea a medio escribir"
    tee.write("dia\n")
    assert collected == ["una linea", "y media"]
    tee.write("sin salto final")
    tee.flush()
    assert collected[-1] == "sin salto final"


def test_an_aborting_stage_does_not_take_down_the_tui(monkeypatch):
    """`guard` y la verificación del PDF paran con `SystemExit`, que es una parada
    deliberada y no un fallo del programa. Si la TUI no la atrapara, un corpus degradado
    —el caso que el proyecto entero está construido para detectar— cerraría el panel en vez
    de mostrar por qué se detuvo."""
    from to_markdown import stages as stage_registry
    from to_markdown.tui import run_stages

    def abort(_books):
        print("trabajando")
        raise SystemExit("DEGRADED CORPUS in Libro I — nothing was written")

    monkeypatch.setitem(stage_registry.STAGES, "parse", abort)
    collected: list[str] = []
    ok = run_stages(["parse"], list(BOOKS[:1]), collected.append)

    assert ok is False
    joined = "\n".join(collected)
    assert "trabajando" in joined, "lo impreso antes del aborto no se pierde"
    assert "DEGRADED CORPUS" in joined, "el motivo del aborto se muestra"
    assert "No se escribió nada" in joined


def test_the_tui_offers_exactly_the_stages_that_exist():
    """El panel enumera las etapas por su cuenta para poder describirlas. Si alguien agrega
    una etapa a la CLI y no aquí, la TUI dejaría de ser la forma principal de operar."""
    from to_markdown.stages import DEFAULT, STAGES
    from to_markdown.tui import DEFAULT_STAGES, STAGE_HELP

    assert set(STAGE_HELP) == set(STAGES), "la TUI y la CLI ofrecen etapas distintas"
    assert DEFAULT_STAGES == DEFAULT, "la corrida por defecto difiere entre TUI y CLI"


def test_corpus_state_is_read_without_recomputing_anything():
    """El panel muestra el estado al abrir y después de cada corrida. Tiene que salir de
    JSON ya escrito: recalcularlo haría que abrir la TUI costara lo que cuesta `parse`."""
    from to_markdown.tui import corpus_state

    state = corpus_state()
    assert [b["slug"] for b in state["books"]] == [b.slug for b in BOOKS]
    for row in state["books"]:
        assert row["documents"] >= 0 and row["sections"] >= 0


def test_the_tui_starts_runs_a_stage_and_reflects_the_result():
    """Prueba de extremo a extremo del panel, sin terminal: se marca una etapa y un Libro,
    se corre, y se comprueba que la salida de la etapa llegó al registro y que el estado
    volvió a `terminado`. Es lo que impide que la TUI se rompa en silencio al cambiar una
    etapa: el resto de la suite prueba el pipeline, no la interfaz que lo invoca."""
    import asyncio

    from to_markdown.tui import build_app

    book = BOOKS[0]
    if not book.file("sections.json").exists():
        pytest.skip(f"{book.slug} sin exportar: `uv run python -m to_markdown export`")

    async def run_app() -> tuple[bool, str, str]:
        app = build_app()()
        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one("#stages").deselect_all()
            app.query_one("#stages").select("bundle")
            app.query_one("#books").deselect_all()
            app.query_one("#books").select(book.slug)
            await pilot.pause()
            # El comando equivalente se muestra antes de correr: es lo que hace que el
            # panel enseñe la CLI en vez de esconderla.
            assert app.status_text.endswith(f"to_markdown bundle -b {book.slug}")
            app.action_run()
            for _ in range(300):
                await pilot.pause(0.1)
                if not app.running:
                    break
            log_text = "\n".join(str(line) for line in app.query_one("#log").lines)
            return app.running, app.status_text, log_text

    still_running, state, log_text = asyncio.run(run_app())
    assert still_running is False, "la corrida no terminó"
    assert state.lower().startswith("terminado"), state
    assert "bundle" in log_text
    assert book.slug in log_text, "la salida de la etapa no llegó al registro"



def test_purge_opens_the_modal_and_modals_are_centered(tmp_path, monkeypatch):
    """Dos cosas que se rompieron juntas y se prueban juntas.

    `D` → elegir qué borrar → confirmar es el único camino que borra disco, y estaba
    cortado: el import de `by_key` apuntaba a un paquete que no existe, así que elegir
    cualquier objetivo tiraba la TUI entera con `ModuleNotFoundError` en vez de pedir la
    segunda confirmación. Un fallo del que no protege ninguna prueba del pipeline, porque
    no pasa por el pipeline.

    Y el cuadro va al medio: `Screen` les impone `layout: horizontal` a los modales —el
    selector de tipo alcanza a las subclases— y sin `align` quedaban pegados arriba a la
    izquierda.
    """
    import asyncio

    # Objetivos de mentira sobre `tmp_path`: la prueba no puede depender de que quien la
    # corra tenga el Compendio descargado. Con `data/` vacío —un checkout limpio, o justo
    # después de borrar— `D` responde en el registro y no abre nada, que es lo correcto,
    # y esta prueba no llegaba ni a mirar el modal.
    import to_markdown.infra.cleanup as cleanup_module
    import to_markdown.tui.app as tui_app
    import to_markdown.tui.screens as screens_module
    from to_markdown.tui import build_app
    from to_markdown.tui.screens import CleanScreen, Confirm, HelpScreen

    fake = tmp_path / "algo.txt"
    fake.write_text("x", encoding="utf-8")
    fake_targets = [
        cleanup_module.Target(t.key, t.label, [fake], t.rebuild, t.irreversible)
        for t in cleanup_module.targets()
    ]
    # Los tres enlaces: `app` los mira para decidir si hay algo que borrar y para resolver
    # la clave elegida, y `screens` para dibujar la lista.
    monkeypatch.setattr(tui_app, "targets", lambda: fake_targets)
    monkeypatch.setattr(screens_module, "targets", lambda: fake_targets)
    monkeypatch.setattr(tui_app, "by_key", lambda k: next(t for t in fake_targets if t.key == k))

    def assert_centered(app) -> None:
        box, screen_size = app.screen.query_one("#dialog").region, app.screen.size
        assert abs(box.x - (screen_size.width - box.width) // 2) <= 1, box
        assert abs(box.y - (screen_size.height - box.height) // 2) <= 1, box

    async def run_app() -> None:
        app = build_app()()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("D")
            assert isinstance(app.screen, CleanScreen), app.screen
            assert_centered(app)

            # Lo que reventaba: la respuesta del primer modal, con la opción más cara.
            # Se elige con el teclado y no llamando al callback a mano, porque el fallo
            # estaba justo en la cadena dismiss → callback.
            option_list = app.screen.query_one("#targets")
            option_list.highlighted = next(
                i for i, o in enumerate(option_list._options) if o.id == "everything"
            )
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, Confirm), "no se pidió la segunda confirmación"
            assert_centered(app)

            # Esc no borra nada: la salida es tan importante como la confirmación.
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, (Confirm, CleanScreen))

            await pilot.press("question_mark")
            assert isinstance(app.screen, HelpScreen)
            assert_centered(app)

    asyncio.run(run_app())


def test_enter_runs_the_selection_wherever_focus_is():
    """La ayuda y el pie prometen «Intro corre lo marcado». Tenía que ser verdad en los
    tres paneles, y era mentira en dos.

    `SelectionList` hereda de `OptionList` un `enter` → «seleccionar». Con el foco en
    Etapas o Libros —donde el panel arranca y donde se pasa el tiempo— el widget se comía
    la tecla: no corría nada y encima desmarcaba en silencio la fila resaltada. Solo
    funcionaba con el foco en el registro, que es el único de los tres que no liga Intro.
    """
    import asyncio

    from to_markdown.tui import build_app

    async def run_app() -> list[tuple[str, bool, bool]]:
        app = build_app()()
        launched: list[list[str]] = []
        seen = []
        async with app.run_test(size=(120, 40)) as pilot:
            # Se intercepta el hilo de la corrida: interesa QUÉ se lanza, no correrlo.
            app.run_pipeline = lambda stage_names, book_slugs: launched.append(list(stage_names))
            await pilot.pause()
            for tui_app in ("stages", "books", "log"):
                app.query_one(f"#{tui_app}").focus()
                await pilot.pause()
                selected = set(app.selected("stages"))
                launched.clear()
                await pilot.press("enter")
                await pilot.pause()
                seen.append((tui_app, bool(launched), selected != set(app.selected("stages"))))
                app.running = False
        return seen

    for tui_app, did_run, toggled_selection in asyncio.run(run_app()):
        assert did_run, f"Intro no corrió nada con el foco en #{tui_app}"
        assert not toggled_selection, f"Intro alteró la selección con el foco en #{tui_app}"


def test_the_hint_describes_the_panel_you_are_on():
    """`#hint` es la línea que explica en palabras qué hace lo resaltado, y describía el
    panel ANTERIOR.

    `Widget.focus()` no mueve el foco en el acto: lo encola con `call_later`. Leer
    `self.focused` en la misma vuelta devuelve quien tenía el foco antes, así que la pista
    iba siempre un Tab atrasada — y al arrancar, con el foco todavía en nadie, describía el
    registro en vez de la etapa resaltada.
    """
    import asyncio

    from to_markdown.tui import build_app

    async def run_app() -> list[tuple[str, str]]:
        app = build_app()()
        seen = []
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            seen.append((app.focused.id, str(app.query_one("#hint").content)))
            for _ in range(2):
                await pilot.press("tab")
                await pilot.pause()
                seen.append((app.focused.id, str(app.query_one("#hint").content)))
        return seen

    expected = {
        "stages": "Escribe en:",          # qué hace la etapa y dónde escribe
        "books": "Libros",
        "log": "Salida de las etapas",
    }
    seen = asyncio.run(run_app())
    assert [p for p, _ in seen] == ["stages", "books", "log"], seen
    for tui_app, hint in seen:
        assert expected[tui_app] in hint, f"con el foco en #{tui_app} la pista decía: {hint}"


def test_reset_returns_to_the_selection_it_opened_with():
    """`d` se anuncia como «volver a la selección inicial». Con `tui -b book-iii` marcaba
    los cinco Libros, que no es restablecer sino ampliar: quien abrió el panel para un solo
    Libro y pulsó `d` se encontraba a punto de procesar el Compendio entero."""
    import asyncio

    from to_markdown.tui import build_app
    from to_markdown.tui.content import DEFAULT_STAGES

    async def run_app() -> tuple[list[str], set[str]]:
        app = build_app()(["book-iii"])
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.query_one("#books").select_all()
            app.query_one("#stages").deselect_all()
            await pilot.pause()
            await pilot.press("d")
            await pilot.pause()
            return sorted(app.selected("books")), set(app.selected("stages"))

    book_slugs, stage_names = asyncio.run(run_app())
    assert book_slugs == ["book-iii"], book_slugs
    assert stage_names == set(DEFAULT_STAGES), stage_names


def test_the_help_documents_every_key_that_exists():
    """La ayuda es la única referencia que ve quien usa el panel. Dos apartados enteros
    —métricas y rendimiento— existían sin figurar en la lista de teclas."""
    from to_markdown.tui import HELP, build_app

    # Se mira SOLO la lista de teclas: las mismas letras aparecen sueltas en la prosa de
    # más arriba, y buscarlas en la ayuda entera daba por documentada una tecla que no
    # figuraba en la lista.
    documented_keys = HELP[HELP.index("[b]Teclas[/b]"):HELP.index("[b]Las etapas")]
    names = {"enter": "Intro", "space": "espacio", "question_mark": "?",
               "tab": "Tab", "shift+tab": "Tab"}
    for binding in build_app().BINDINGS:
        label = names.get(binding.key, binding.key)
        assert f"[b]{label}[/b]" in documented_keys, f"la lista de teclas no nombra «{binding.key}»"

# --- analítica ------------------------------------------------------------------------


def test_charts_are_drawn_for_the_width_they_receive():
    """Es lo que hace que el panel sirva igual en 80 columnas y en 200: ninguna medida del
    módulo de analítica es fija. Si un gráfico se pasara del ancho, en la TUI aparecería
    recortado o con las barras desalineadas."""
    import re

    from to_markdown.analytics import CHARTS, snapshot

    snap = snapshot()
    # Se exige el ancho en las filas con barras y tramas: son las que no pueden ajustarse
    # sin perder la alineación que las hace comparables. La prosa vive en un `Static`, que
    # ajusta solo.
    glyphs = set("█▓▒░▏▎▍▌▋▊▉⠀⣀⣄⣤⣦⣶⣷⣿⠤")
    for name, draw in CHARTS.items():
        for width in (40, 76, 120, 200):
            for rendered_line in draw(snap, width):
                visible = re.sub(r"\[/?[a-z ]*\]", "", rendered_line)
                if not (glyphs & set(visible)):
                    continue
                assert len(visible) <= width, (
                    f"{name} a {width} columnas se pasó: {len(visible)} — {visible[:60]!r}"
                )


def test_the_bar_respects_the_scale_and_the_edges():
    """Las barras de un gráfico solo se pueden comparar entre sí si comparten escala."""
    from to_markdown.analytics import bar

    assert bar(0, 100, 10) == ""
    assert bar(100, 100, 10) == "█" * 10
    assert len(bar(50, 100, 10)) == 5
    # Un valor por encima del máximo no desborda la barra ni rompe la fila.
    assert bar(999, 100, 10) == "█" * 10
    assert bar(10, 0, 10) == "" and bar(10, 100, 0) == ""


def test_a_flat_series_is_not_drawn_as_a_jump():
    """El pipeline es reproducible, así que la serie histórica es plana. Dividir por un
    rango cero habría que resolverlo, y resolverlo mal —a cero o a tope— haría leer una
    corrida idéntica como un desplome o como un pico."""
    from to_markdown.analytics import sparkline

    assert set(sparkline([100.0] * 8, 8)) == {"⠤"}
    assert not sparkline([], 8)
    upload = sparkline([1.0, 2.0, 3.0, 4.0], 4)
    assert upload[0] < upload[-1], "una serie creciente tiene que dibujarse creciente"
    # Más puntos que ancho: se promedian en cubos en vez de recortarse.
    assert len(sparkline(list(range(100)), 10)) == 10


def test_categories_are_told_apart_without_color():
    """La paleta es monocromática, así que las cuatro clases de veredicto se separan por
    densidad de trama. Que sean cuatro glifos distintos es lo que lo hace legible en una
    terminal sin color y para quien no distingue un color de otro."""
    from to_markdown.analytics import DENSITY

    assert len(set(DENSITY.values())) == 4
    from to_markdown.stages.compare import verdict

    assert set(DENSITY) == {verdict(1.0, 1.0, False), verdict(0.0, 1.0, False),
                            verdict(0.0, 0.0, True), verdict(0.0, 0.0, False)}


def test_analytics_does_not_recompute_the_corpus(book_corpus):
    """El panel muestra las métricas al abrir y después de cada corrida. Tienen que salir de
    JSON ya escrito: recalcularlas haría que abrir la TUI costara lo que cuesta `parse`."""
    from to_markdown.analytics import coverage_metrics, download_metrics, processing_metrics

    book, document_list = book_corpus
    processing = processing_metrics(book)
    assert processing["documents"] == len(document_list)
    assert processing["units"] == sum(len(d["units"]) for d in document_list)
    download = download_metrics(book)
    assert download["pages"] >= processing["documents"]
    coverage = coverage_metrics(book)
    if coverage["ready"]:
        assert coverage["aligned"] <= coverage["documents"]


# --- borrado --------------------------------------------------------------------------


def test_every_purge_target_says_how_to_rebuild_itself():
    """Es lo que convierte «borrar 371 MB» en una decisión informada. Un objetivo sin esa
    frase deja a quien lo lee sin saber si pierde tiempo o pierde información."""
    from to_markdown.infra.cleanup import targets

    purge_targets = targets()
    assert purge_targets, "no hay nada que ofrecer para borrar"
    for target in purge_targets:
        assert target.rebuild, f"{target.key} no dice cómo reponerse"
        assert target.paths
    # Lo irreversible tiene que decirlo con esas palabras, no insinuarlo.
    for target in purge_targets:
        if target.irreversible:
            assert "NO SE REPONE" in target.rebuild or "se pierde" in target.rebuild


def test_purge_measures_before_deleting(tmp_path):
    """Después de borrar no hay nada que medir, y el número es justo lo que se le informa a
    quien acaba de aprobarlo."""
    from to_markdown.infra.cleanup import Target, purge

    folder = tmp_path / "cosas"
    folder.mkdir()
    (folder / "a.txt").write_text("hola", encoding="utf-8")
    (folder / "b.txt").write_text("mundo!", encoding="utf-8")
    target = Target("prueba", "Prueba", [folder], rebuild="volver a crearla")

    assert target.files() == 2
    assert target.size() == 10
    files, bytes_ = purge(target)
    assert (files, bytes_) == (2, 10)
    assert not folder.exists()
    # Borrar algo que ya no está no puede reventar: la TUI ofrece objetivos que pueden
    # haber desaparecido entre que se dibujó la lista y se confirmó.
    assert purge(target) == (0, 0)


def test_purge_targets_go_from_cheap_to_expensive():
    """El orden ES la advertencia: quien recorre la lista de arriba abajo se encuentra
    primero con lo que se rehace solo y al final con lo que no se rehace nunca."""
    from to_markdown.infra.cleanup import targets

    keys = [t.key for t in targets()]
    assert keys[0] == "output", "lo más barato de reponer tiene que ir primero"
    assert keys[-1] == "everything", "borrar todo tiene que ir último"
    irreversible_at = [i for i, t in enumerate(targets()) if t.irreversible]
    assert min(irreversible_at) > keys.index("cache"), (
        "lo irreversible no puede aparecer antes que lo que solo cuesta tiempo"
    )



def test_no_chart_exceeds_the_width_it_is_given():
    """Amplía la cota inferior de la prueba de anchos hasta las 28 columnas, que es el
    suelo REAL: los apartados llaman con `max(28, ancho - 4)`.

    La prueba que había empezaba en 40 y no veía el tramo que la TUI sí alcanza. Ahí
    `rows_chart` tenía un suelo fijo de 4 columnas para la barra —en un módulo cuya premisa
    es no tener ninguna medida fija— y el gráfico de procesamiento salía de 35 columnas
    dentro de un apartado de 28: la fila se parte en dos y desalinea todas las barras.
    """
    import re

    from to_markdown.analytics import CHARTS, snapshot

    snap = snapshot()
    glyphs = set("█▓▒░▏▎▍▌▋▊▉⠀⣀⣄⣤⣦⣶⣷⣿⠤")
    for name, draw in CHARTS.items():
        for width in (28, 32, 36, 40):
            for rendered_line in draw(snap, width):
                visible = re.sub(r"\[/?[a-z ]*\]", "", rendered_line)
                if not (glyphs & set(visible)):
                    continue
                assert len(visible) <= width, (
                    f"{name} a {width} columnas se pasó: {len(visible)} — {visible[:60]!r}"
                )


def test_purge_targets_the_configured_path_not_a_derived_one():
    """`everything` deducía `assets/` con aritmética sobre `WEB` en vez de leer la ruta
    configurada. Acertaba solo mientras `data/` y `assets/` colgaran del mismo sitio: con
    `data = "var/data"` y `assets = "assets"` apuntaba a `var/assets`, así que la operación
    más destructiva de la herramienta dejaba intacto justo lo que decía borrar."""
    from to_markdown.core import ASSETS, DATA, OUTPUT
    from to_markdown.infra.cleanup import by_key

    assert set(by_key("everything").paths) == {DATA, OUTPUT, ASSETS}


def test_purge_with_nothing_downloaded_opens_no_empty_menu(tmp_path, monkeypatch):
    """`CleanScreen` esconde los objetivos que no existen. Sin nada descargado quedaba un
    modal que decía «elige qué borrar y pulsa Intro» con la lista vacía: una pregunta sin
    respuestas posibles, de la que solo se sale con Esc."""
    import asyncio

    from to_markdown.tui import build_app

    async def run_app() -> tuple[bool, str]:
        from to_markdown.tui.screens import CleanScreen

        app = build_app()()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await pilot.press("D")
            await pilot.pause()
            log_text = "\n".join(str(line) for line in app.query_one("#log").lines)
            return isinstance(app.screen, CleanScreen), log_text

    # Ningún objetivo existe: se apuntan todos a rutas bajo `tmp_path`, que está vacío.
    import to_markdown.infra.cleanup as cleanup_module

    empty_targets = [
        cleanup_module.Target(t.key, t.label, [tmp_path / f"no-existe-{t.key}"], t.rebuild,
                        t.irreversible)
        for t in cleanup_module.targets()
    ]
    # Se parchea el enlace de `app`, no el de `cleanup`: `app` hace `from ... import
    # targets`, así que ya tiene su propia referencia y parchear el módulo de origen solo
    # funciona si nadie importó `app` todavía. Eso depende de qué pruebas corrieron antes.
    build_app()  # fuerza el import perezoso de `to_markdown.tui.app`
    monkeypatch.setattr("to_markdown.tui.app.targets", lambda: empty_targets)

    did_open, log_text = asyncio.run(run_app())
    assert not did_open, "abrió el menú de borrado sin nada que borrar"
    assert "No hay nada descargado que borrar" in log_text

# --- tendencias -----------------------------------------------------------------------


def test_amendment_activity_comes_from_the_dates_the_norm_declares(book_corpus):
    """Es la única serie temporal real del corpus. El `Last-Modified` del servidor no
    sirve: el CMS reguardó las 1.476 páginas el mismo día y todas dicen el mismo año. Las
    notas de actualización, en cambio, fechan cada modificación."""
    from to_markdown.analytics import amendment_activity

    book, _ = book_corpus
    activity = amendment_activity([book])
    years = activity["years"]
    assert years, f"{book.slug} no aportó ninguna fecha"
    assert 1980 <= min(years) and max(years) <= 2100, "años fuera de rango entraron a la serie"
    # El corpus trae erratas de tipeo ("1012" por "2012"): tienen que quedar fuera.
    assert 1012 not in years
    assert activity["ncg"], "no se reconoció ninguna Norma de Carácter General"


def test_each_stage_records_its_own_duration(tmp_path, monkeypatch):
    """La serie de duración es lo que responde «¿está tardando más que antes?», que una
    sola corrida no puede contestar. Se anota desde la CLI y desde la TUI por el mismo
    camino, o las dos mitades de la serie no serían comparables."""
    import json

    from to_markdown.analytics import record_stage, sources

    # Se parchea el módulo que escribe, no la fachada: la fachada reexporta la función,
    # pero la ruta la lee `sources`.
    destination = tmp_path / "timings.jsonl"
    monkeypatch.setattr(sources, "TIMINGS", destination)
    record_stage("parse", list(BOOKS[:2]), 1.25, ok=True)
    record_stage("compare", list(BOOKS), 30.0, ok=False)

    table_rows = [json.loads(x) for x in destination.read_text(encoding="utf-8").splitlines()]
    assert [f["stage"] for f in table_rows] == ["parse", "compare"]
    assert table_rows[0]["seconds"] == 1.25 and table_rows[0]["books"] == ["book-i", "book-ii"]
    # Una etapa que abortó igual deja su medición: una corrida detenida es un dato, no un
    # hueco en la serie.
    assert table_rows[1]["ok"] is False


def test_the_duration_trend_does_not_mix_scopes():
    """Una etapa sobre un Libro y la misma sobre los cinco tardan cosas distintas por
    definición. Mezclarlas daba tendencias de +800% que solo decían «esta vez corrí más
    Libros»."""
    from to_markdown.analytics import timing_chart

    timings = (
        [{"stage": "parse", "books": ["book-i"], "seconds": 0.3, "ok": True}] * 2
        + [{"stage": "parse", "books": [b.slug for b in BOOKS], "seconds": 3.0, "ok": True}] * 6
    )
    joined = "\n".join(timing_chart({"timings": timings}, 76))
    assert "los 5 Libros" in joined, "eligió el alcance equivocado"
    assert "3.0 s" in joined and "0.3 s" not in joined
    assert "2 de otro alcance" in joined, "no avisó qué dejó fuera"


def test_the_report_stacks_every_section_without_tabs():
    """El apartado se abre y se cierra con una tecla y se recorre de una sola pasada: no
    hay pestañas que cambiar. Si una sección dejara de emitirse, desaparecería del informe
    sin que nada lo notara."""
    from to_markdown.analytics import SECTIONS, report, snapshot

    rendered = report(snapshot(), 76)
    joined = "\n".join(rendered)
    for section in SECTIONS:
        title = section({"download": [], "processing": [], "coverage": [], "history": {},
                          "history_at": {}, "amendments": {"years": {}, "ncg": {},
                          "by_book": {}, "undated": 0}, "timings": []}, 76)[0]
        mark = title.split("[/b]")[0].replace("[b]", "")
        assert mark in joined, f"falta la sección «{mark}» en el informe"
    # Las secciones temporales van primero: son lo que una foto no puede contar.
    assert joined.index("Actividad normativa") < joined.index("Descarga")


def test_the_charts_drawer_opens_and_closes_with_the_same_key():
    """La misma tecla en los dos sentidos es lo que lo hace rápido de consultar y de sacar
    del medio. Y mientras está abierto tiene que entrar en la rotación de Tab: rotar hacia
    un panel invisible dejaría el foco en ninguna parte."""
    import asyncio

    from to_markdown.tui import ANALYTICS, PANELS, build_app

    async def run_app() -> list:
        app = build_app()()
        async with app.run_test(size=(150, 46)) as pilot:
            await pilot.pause()
            steps = [(app.query_one("#analytics").has_class("-open"), app._panels())]
            await pilot.press("g")
            await pilot.pause()
            steps.append((app.query_one("#analytics").has_class("-open"), app._panels()))
            await pilot.press("g")
            await pilot.pause()
            steps.append((app.query_one("#analytics").has_class("-open"), app._panels()))
            return steps

    closed, opened, toggled_back = asyncio.run(run_app())
    assert closed == (False, PANELS)
    assert opened[0] is True and ANALYTICS in opened[1]
    assert toggled_back == (False, PANELS), "la segunda pulsación tiene que cerrarlo"


def _chroma(hex_color: str) -> int:
    """Distancia entre el canal más alto y el más bajo. Es lo que separa un tono de un gris."""
    channels = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return max(channels) - min(channels)


def _contrast(one: str, other: str) -> float:
    """Razón de contraste de la WCAG entre dos colores."""
    def luminance(hex_color: str) -> float:
        channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                   for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    a, b = luminance(one), luminance(other)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def test_the_theme_is_catppuccin_mocha_and_nothing_else():
    """Ningún color del tema puede estar fuera de la paleta.

    Es la puerta por la que se cuela el color de fuera: basta escribir un hex «parecido» en
    una variable para que la interfaz deje de ser Catppuccin y nadie lo note, porque en una
    captura de pantalla un azul se parece mucho a otro azul.
    """
    from to_markdown.tui.theme import MOCHA, PALETTE

    official = {v.lower() for v in PALETTE.values()}
    # La paleta escrita en el módulo tiene que ser la de Catppuccin, no una de memoria.
    assert PALETTE["base"] == "#1e1e2e"
    assert PALETTE["text"] == "#cdd6f4"
    assert PALETTE["mauve"] == "#cba6f7"
    assert len(official) == 26, "Mocha tiene 26 tonos y ninguno repetido"

    role_colors = [MOCHA.background, MOCHA.surface, MOCHA.panel, MOCHA.foreground,
             MOCHA.primary, MOCHA.secondary, MOCHA.accent,
             MOCHA.success, MOCHA.warning, MOCHA.error]
    for color in role_colors:
        assert color.lower() in official, f"{color} no es un tono de Mocha"
    for name, value in MOCHA.variables.items():
        if isinstance(value, str) and value.startswith("#"):
            assert value.lower() in official, f"la variable «{name}» usa {value}"


def test_the_theme_uses_each_accent_for_one_thing_only():
    """El color es un canal de significado, no un adorno. Dos roles distintos con el mismo
    acento hacen que el acento no responda ninguna pregunta: si el azul marcara a la vez el
    foco y los avisos, ver azul dejaría de decir dónde estás."""
    from to_markdown.tui.theme import MOCHA

    semantic = {
        "primary (foco)": MOCHA.primary,
        "secondary": MOCHA.secondary,
        "accent (capa modal, cursores)": MOCHA.accent,
        "success": MOCHA.success,
        "warning": MOCHA.warning,
        "error": MOCHA.error,
    }
    repeated = [c for c in semantic.values() if list(semantic.values()).count(c) > 1]
    assert not repeated, f"un mismo acento cumple dos papeles: {repeated}"
    # El foco es el borde encendido; lo que no lo tiene, un gris de superficie. Si los dos
    # fueran del mismo color el panel activo dejaría de distinguirse.
    assert MOCHA.variables["border"] != MOCHA.variables["border-blurred"]
    assert _contrast(MOCHA.variables["border"], MOCHA.variables["border-blurred"]) >= 3.0


def test_everything_readable_meets_AA_contrast():
    """Cada par de texto y fondo que el panel dibuja, contra el umbral de la WCAG: 4,5:1
    para texto y 3:1 para los componentes de interfaz (bordes).

    Catppuccin es una paleta bonita, no una paleta accesible por decreto: `overlay0` sobre
    `mantle` no llega a 4,5:1, así que la elección de qué tono va en qué papel es lo que
    hace legible el panel, y eso es exactamente lo que puede romperse al retocar un color.
    """
    from to_markdown.tui import theme as t

    joined = [
        ("contenido del panel", t.TEXT, t.MANTLE),
        ("contenido en pantalla", t.TEXT, t.BASE),
        ("pista explicativa", t.SUBTEXT0, t.MANTLE),
        ("barra de estado", t.TEXT, t.SURFACE0),
        ("descripción del pie", t.SUBTEXT0, t.SURFACE0),
        ("tecla del pie", t.BLUE, t.SURFACE0),
        ("etapa marcada", t.GREEN, t.MANTLE),
        ("aviso", t.YELLOW, t.MANTLE),
        ("error", t.RED, t.MANTLE),
        ("cursor invertido", t.CRUST, t.LAVENDER),
        ("línea de los gráficos", t.BLUE, t.CRUST),
    ]
    for name, foreground, background in joined:
        ratio = _contrast(foreground, background)
        assert ratio >= 4.5, f"{name}: {foreground} sobre {background} da {ratio:.2f}:1"

    components = [
        ("borde con foco", t.BLUE, t.MANTLE),
        ("borde del modal", t.LAVENDER, t.MANTLE),
        ("texto apagado", t.OVERLAY1, t.MANTLE),
    ]
    for name, foreground, background in components:
        ratio = _contrast(foreground, background)
        assert ratio >= 3.0, f"{name}: {foreground} sobre {background} da {ratio:.2f}:1"


def test_the_interface_emits_no_grey_outside_the_palette():
    """El reverso de la prueba anterior, y sobre los códigos ANSI que salen de verdad por la
    terminal: no basta con que el tema esté bien escrito si un widget pinta por su cuenta.

    Mocha no tiene un solo gris neutro — hasta el más apagado, `crust`, va tintado de azul
    (croma 10). Un color acromático en pantalla es, por definición, de fuera: `$text` de
    textual es `auto 87%`, un blanco de contraste que gana sobre cualquier `$text:` de la
    hoja de la app, y con él el registro y las listas salían en gris de croma 2.

    Esta prueba sustituye a la que exigía que la interfaz NO emitiera color: el contrato se
    invirtió a propósito cuando el tema pasó a ser Catppuccin Mocha.
    """
    import asyncio
    import io
    import re

    from rich.console import Console

    from to_markdown.tui import build_app
    from to_markdown.tui.theme import BASE, BLUE, MANTLE, PALETTE, SURFACE0, TEXT

    async def paint(key: str | None) -> str:
        app = build_app()()
        async with app.run_test(size=(132, 38)) as pilot:
            await pilot.pause()
            if key:
                await pilot.press(key)
                await pilot.pause()
            # `file=StringIO`: sin eso, `Console.print` escribe en la salida real y la
            # suite queda llena de códigos ANSI.
            console = Console(record=True, width=132, height=38, force_terminal=True,
                              color_system="truecolor", file=io.StringIO())
            console.print(app.screen._compositor)
            return console.export_text(styles=True)

    def emitted(painted: str) -> set[str]:
        return {
            "#{:02x}{:02x}{:02x}".format(*(int(x) for x in m.groups()))
            for m in re.finditer(r"(?:38|48);2;(\d+);(\d+);(\d+)", painted)
        }

    observed: set[str] = set()
    for key in (None, "g", "m", "p"):
        observed |= emitted(asyncio.run(paint(key)))
    assert observed, "no se emitió ningún color: la prueba no está mirando nada"

    # El suelo es el croma de `crust`, el tono menos saturado de Mocha. Las mezclas que
    # textual hace por su cuenta —bordes redondeados, `[dim]`, barras de desplazamiento—
    # caen entre dos tonos de la paleta y quedan por encima; un gris de textual, debajo.
    floor = min(_chroma(v) for v in PALETTE.values())
    assert floor == 10, "cambió la paleta: revisa el suelo de croma"
    greys = sorted(c for c in observed if _chroma(c) < floor - 1)
    assert not greys, f"la interfaz pintó gris ajeno a Mocha: {greys}"

    # Y que la paleta esté de verdad en pantalla, no solo escrita en el módulo.
    for name, color in (("base", BASE), ("mantle", MANTLE), ("surface0", SURFACE0),
                          ("text", TEXT), ("blue", BLUE)):
        assert color in observed, f"«{name}» ({color}) no aparece en pantalla"


def test_the_chart_tone_does_not_drift_from_the_theme():
    """`content` no puede importar `theme` —tiene que cargarse sin textual— así que el tono
    de las curvas en vivo va como literal RGB. Duplicado sin guardia, se separa."""
    from to_markdown.tui.content import TONE_LINE
    from to_markdown.tui.theme import BLUE

    assert TONE_LINE == tuple(int(BLUE[i:i + 2], 16) for i in (1, 3, 5))


# --- rendimiento en vivo y responsive -------------------------------------------------


def test_the_state_panel_fits_any_width():
    """La tabla era de ancho fijo —unas 45 columnas— contra una barra lateral que baja
    hasta 26, así que las filas se partían y dejaba de leerse. Se decide cuántas columnas
    caben antes de escribirlas."""
    import re

    from to_markdown.tui import corpus_state, state_lines

    table_rows = corpus_state()["books"]
    for width in range(16, 60):
        rendered = [re.sub(r"\[/?[a-z ]*\]", "", x) for x in state_lines(table_rows, width)]
        worst = max(len(x) for x in rendered)
        assert worst <= width, f"a {width} columnas la fila más larga mide {worst}"


def test_the_state_panel_warns_when_there_is_nothing():
    """Un panel vacío con ceros no dice qué hacer; el mensaje sí."""
    from to_markdown.tui import state_lines

    empty_rows = [{"slug": b.slug, "documents": 0, "units": 0, "sections": 0, "delivered": 0}
             for b in BOOKS]
    joined = "\n".join(state_lines(empty_rows, 40))
    assert "Todavía no hay nada descargado" in joined
    assert "a[/b] para empezar" in joined


def test_the_process_counters_measure_the_link_and_the_output():
    """`wire_bytes` es lo que viajó comprimido y `bytes` lo que se entrega descomprimido.
    Los dos juntos dicen cuánto ahorra el gzip; uno solo no puede."""
    from to_markdown.infra import monitor

    monitor.reset()
    assert monitor.counters() == {}
    monitor.bump("requests")
    monitor.bump("wire_bytes", 1000)
    monitor.bump("bytes", 4500)
    counters = monitor.counters()
    assert counters["requests"] == 1
    assert counters["wire_bytes"] < counters["bytes"], "el gzip tiene que ahorrar"


def test_the_rate_derives_between_samples_not_from_the_total():
    """Una curva acumulada siempre sube, y sube igual de bonito cuando el ritmo se
    derrumbó. El ritmo por segundo es lo que responde «¿a qué velocidad va ahora?»."""
    from to_markdown.infra.monitor import Monitor, Sample

    monitor = Monitor()
    monitor.samples = [
        Sample(at=0, elapsed=0.0, rss=100, cpu=0.0, counters={"requests": 0}),
        Sample(at=1, elapsed=1.0, rss=100, cpu=0.5, counters={"requests": 10}),
        Sample(at=2, elapsed=2.0, rss=100, cpu=1.0, counters={"requests": 12}),
    ]
    assert monitor.series("requests") == [0, 10, 12]
    assert monitor.rate("requests") == [10.0, 2.0], "el ritmo cayó y tiene que verse"
    assert monitor.cpu_percent() == [50.0, 50.0]
    summary = monitor.summary()
    assert summary["requests"] == 12 and summary["peak_requests_per_second"] == 10.0


def test_the_sampling_window_does_not_grow_without_bound():
    """Un gráfico de línea no puede mostrar más puntos que columnas tiene la terminal, y
    una corrida larga llenaría la memoria con datos que nadie va a ver."""
    from to_markdown.infra.monitor import Monitor

    monitor = Monitor(window=10)
    for _ in range(40):
        monitor.take()
    assert len(monitor.samples) == 10
    # Y de paso: leer memoria y CPU depende del sistema operativo, y el respaldo de Windows
    # devuelve 0 si la estructura de psapi quedó mal declarada.
    assert monitor.samples[-1].rss > 0 and monitor.samples[-1].cpu > 0


def test_the_three_drawers_are_mutually_exclusive():
    """Tres apartados abiertos a la vez dejan a cada uno con un tercio del alto, que es
    menos de lo que cualquiera necesita. Y cada uno entra en la rotación de Tab solo
    mientras está abierto."""
    import asyncio

    from to_markdown.tui import ANALYTICS, DRAWERS, METRICS, PERFORMANCE, build_app

    async def run_app() -> list:
        app = build_app()()
        async with app.run_test(size=(150, 46)) as pilot:
            await pilot.pause()
            steps = []
            for key, expected in (("m", "metrics-box"), ("g", "analytics"),
                                    ("p", "performance"), ("p", "stages")):
                await pilot.press(key)
                # Se espera a que el foco llegue, en vez de a un `pause` suelto: el
                # muestreo del monitor corre cada medio segundo y compite con el reloj de
                # la prueba, que es de dónde salía una falla intermitente.
                for _ in range(50):
                    await pilot.pause()
                    if app.focused is not None and app.focused.id == expected:
                        break
                open_drawers = [d for d in DRAWERS if app.query_one(d).has_class("-open")]
                steps.append((open_drawers, app.focused.id, app._panels()))
            return steps

    (m, g, p, closed) = asyncio.run(run_app())
    assert m[0] == [METRICS] and m[1] == "metrics-box"
    assert g[0] == [ANALYTICS] and g[1] == "analytics", "abrir uno cierra el anterior"
    assert p[0] == [PERFORMANCE] and p[1] == "performance"
    assert PERFORMANCE in p[2], "el apartado abierto entra en la rotación de Tab"
    assert closed[0] == [], "la misma tecla tiene que cerrarlo"
    assert PERFORMANCE not in closed[2], "cerrado, sale de la rotación"


def test_no_panel_is_left_without_height_on_a_small_terminal():
    """MEDIDO: sin cotas, a 85x28 la barra apilada se comía todo y el registro quedaba con
    cero filas — presente en el layout, inútil en la práctica."""
    import asyncio

    from to_markdown.tui import build_app

    async def measure() -> list:
        app = build_app()()
        async with app.run_test(size=(200, 60)) as pilot:
            await pilot.pause()
            out = []
            for width, height in ((200, 60), (120, 40), (92, 30), (85, 28), (70, 24), (60, 20)):
                await pilot.resize_terminal(width, height)
                await pilot.pause()
                if not app.query_one("#analytics").has_class("-open"):
                    await pilot.press("g")
                    await pilot.pause()
                out.append((width, height,
                            app.query_one("#log").size.height,
                            app.query_one("#analytics").size.height))
            return out

    for width, height, log, charts in asyncio.run(measure()):
        assert log >= 2, f"a {width}x{height} el registro quedó con {log} filas"
        assert charts >= 4, f"a {width}x{height} los gráficos quedaron con {charts} filas"
