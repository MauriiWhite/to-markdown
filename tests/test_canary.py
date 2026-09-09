"""Canario contra el sitio en vivo: ¿siguen vigentes los selectores?

Las invariantes de `guard.py` avisan cuando ya corriste el pipeline. Este canario avisa el
día en que la Superintendencia cambia su CMS, que es cuando todavía se puede arreglar sin
prisa. Una sola página, una sola petición.

No corre por defecto (toca la red):  uv run pytest -m network
"""

from __future__ import annotations

import re

import pytest

from to_markdown import BOOKS
from to_markdown.infra.net import BASE, request
from to_markdown.stages.parse import (
    BODY_OPEN,
    BOX_END,
    breadcrumb,
    parse_document,
)

pytestmark = pytest.mark.network

# Página estable desde 2020, con jerarquía completa, materias y notas de actualización.
CANARY = "4074"


@pytest.fixture(scope="module")
def live() -> str:
    status, headers, body = request(f"{BASE}w3-propertyvalue-{CANARY}.html")
    assert status == 200, f"el sitio respondió {status}"
    assert body is not None
    pytest.headers = headers
    return body.decode("utf-8", "replace")


def test_structure_markers_still_exist(live):
    """Los tres anclajes de los que depende toda la extracción."""
    assert BODY_OPEN in live, "cambió el contenedor del cuerpo (#cuerpo_documento)"
    assert BOX_END in live[live.index(BODY_OPEN):], "cambió el cierre de caja del CMS"
    assert "SP_pa_breadcrum_ruta" in live, "cambió el bloque de breadcrumb"


def test_the_hierarchy_is_still_in_the_attributes(live):
    """La jerarquía se lee de `pv-pid-<padre> pvid-<propio>`. Si el CMS deja de emitirlos,
    hay que reconstruir el árbol de otra forma y conviene saberlo antes."""
    assert re.search(r'class="[^"]*pv-pid-\d+ pvid-\d+', live), "desaparecieron los pvid"
    crumbs = breadcrumb(live)
    assert len(crumbs) >= 3, f"breadcrumb degradado: {crumbs}"


def test_the_canary_document_parses_as_always(live):
    """Extracción de punta a punta sobre la página en vivo."""
    document = parse_document(CANARY, live, {})
    assert document is not None
    assert document["hierarchy"]["book"].startswith("Libro I ")
    assert document["hierarchy"]["chapter"] == "Capítulo II. Normas generales de Afiliación"
    assert document["topics"] == ["Afiliación a una A.F.P.", "Afiliado"]
    assert len(document["units"]) >= 15, "se perdieron unidades numeradas"
    assert any("Norma de Carácter General Nº 31" in n for n in document["amendment_notes"])


def test_the_server_still_honors_conditional_requests():
    """Toda la estrategia de actualización depende de esto. Si el servidor deja de mandar
    ETag o de responder 304, hay que volver a comparar por hash y descargar todo."""
    _, headers, _ = request(f"{BASE}w3-propertyvalue-{CANARY}.html")
    etag = headers.get("etag")
    assert etag, f"el servidor dejó de mandar ETag (cabeceras: {sorted(headers)})"
    status, _, body = request(
        f"{BASE}w3-propertyvalue-{CANARY}.html", {"If-None-Match": etag}
    )
    assert status == 304, f"ya no responde 304 a If-None-Match, respondió {status}"
    assert not body


def test_the_site_still_publishes_the_five_books():
    """La partición de `data/` es una foto del índice del Compendio: cinco Libros, cinco
    carpetas. Si la SP agrega un Libro VI, el crawl lo ignoraría en silencio —nunca está
    en `config.toml`, así que nadie lo recorre— y el corpus quedaría incompleto sin que
    ninguna invariante se queje, porque los cinco Libros conocidos seguirían sanos.

    Este canario es lo único que puede avisarlo, y por eso compara contra el índice del
    sitio y no contra el árbol ya descargado.
    """
    status, _, body = request(f"{BASE}w3-channel.html")
    assert status == 200, f"el índice del Compendio respondió {status}"
    html = body.decode("utf-8", "replace")

    published = set(
        re.findall(r'w3-propertyvalue-(\d+)\.html"[^>]*>\s*Libro [IVX]+', html)
    )
    configured = {book.pvid for book in BOOKS}
    assert published == configured, (
        f"cambió la lista de Libros: sobran {sorted(published - configured)}, "
        f"faltan {sorted(configured - published)}. Ajusta [[books]] en config.toml."
    )


def test_every_book_still_links_its_full_pdf():
    """La etapa `pdf` deriva el enlace del pvid (`fo-propertyvalue-<pvid>.pdf`) en vez de
    leerlo del HTML, porque el pvid es la única clave estable del árbol. El costo de esa
    decisión es que si la SP cambia el esquema de la URL, nada lo notaría hasta que la
    descarga fallara. Este canario es lo que lo avisa.

    Se comprueba contra la raíz del Libro, que es donde el portal publica el enlace como
    `AccesoPDF`, y no contra el archivo: basta una petición por Libro.
    """
    from to_markdown.stages.pdf import source_url

    for book in BOOKS:
        status, _, body = request(f"{BASE}w3-propertyvalue-{book.pvid}.html")
        assert status == 200, f"{book.slug}: la raíz respondió {status}"
        html = body.decode("utf-8", "replace")
        expected = source_url(book).rsplit("/", 1)[-1]
        assert expected in html, (
            f"{book.slug}: la raíz ya no enlaza {expected}. La SP cambió el esquema de la "
            f"URL del PDF; revisa `source_url` en pdf.py."
        )


def test_every_books_pdf_is_still_served():
    """Que el enlace esté en el HTML no garantiza que el archivo responda. Se pide con HEAD
    para no bajar 130 MB en una prueba."""
    from to_markdown.stages.pdf import source_url

    for book in BOOKS:
        status, headers, _ = request(source_url(book), method="HEAD")
        assert status == 200, f"{book.slug}: el PDF respondió {status}"
        assert "pdf" in headers.get("content-type", ""), (
            f"{book.slug}: el servidor devuelve {headers.get('content-type')!r}, no un PDF"
        )
        assert headers.get("etag") or headers.get("last-modified"), (
            f"{book.slug}: sin ETag ni Last-Modified, la etapa `pdf` re-descargaría el "
            f"archivo entero en cada corrida"
        )


def test_the_server_still_compresses():
    """El gzip es 4,7x menos transferencia sobre este corpus, y además menos trabajo para
    el sitio del organismo. Si dejara de comprimir, el crawl seguiría siendo correcto pero
    movería cinco veces más bytes sin que nada lo notara."""
    _, headers, body = request(f"{BASE}w3-propertyvalue-{CANARY}.html")
    assert headers.get("content-encoding") == "gzip", (
        f"el servidor dejó de comprimir (content-encoding: "
        f"{headers.get('content-encoding')!r})"
    )
    assert body and b"cuerpo_documento" in body, "el cuerpo no se descomprimió bien"


def test_the_etag_still_matches_with_gzip_on():
    """La trampa de `mod_deflate`: Apache le agrega `-gzip` al ETag al servir comprimido, y
    ese ETag no vuelve a calzar. `_headers` lo normaliza, y esta prueba es lo que avisaría
    si el servidor cambiara de criterio y la normalización pasara a estorbar.

    Es distinta de `test_el_servidor_sigue_honrando_peticiones_condicionales`: aquella
    comprueba que el 304 existe, ésta que sigue existiendo **pidiendo gzip**, que es como
    el crawl pide todo desde que el transporte lo activa.
    """
    _, headers, _ = request(f"{BASE}w3-propertyvalue-{CANARY}.html")
    etag = headers.get("etag", "")
    assert etag and not etag.rstrip('"').endswith("-gzip"), (
        f"el ETag llegó sin normalizar: {etag!r}"
    )
    status, _, body = request(
        f"{BASE}w3-propertyvalue-{CANARY}.html", {"If-None-Match": etag}
    )
    assert status == 304, (
        f"el ETag normalizado ya no calza (respondió {status}). Sin esto, `refresh` "
        f"re-descargaría las 1.476 páginas en cada corrida."
    )
    assert body is None


def test_a_missing_page_is_not_confused_with_an_empty_one():
    """El sitio responde 302 a cualquier pvid que no existe, y el destino es un 404. Sin
    seguir la redirección se cachearía el stub de 267 bytes del 302 como si fuera la
    norma: HTML válido, sin cuerpo, que el parser habría dado por página vacía."""
    with pytest.raises(RuntimeError, match="404"):
        request(f"{BASE}w3-propertyvalue-99999999.html")
