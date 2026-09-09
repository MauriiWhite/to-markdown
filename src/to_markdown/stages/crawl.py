"""Etapa 1: recorre el árbol de cada Libro y deja su HTML y sus imágenes en su carpeta.

El árbol se recorre en anchura desde la raíz de cada Libro, y cada Libro escribe en
`data/web/<slug>/`. Cada página trae sus hijos en el bloque `SP_pa_menuSubvalores_compendio`;
una página sin hijos y con `cuerpo_documento` es una hoja, es decir, texto normativo.

El recorrido por Libro no cuesta nada frente al recorrido único: son las mismas 1.476
peticiones repartidas en cinco tandas, y `max_workers` sigue mandando. Lo que se gana es
que el caché queda particionado en origen, no reordenado después.

El transporte —conexiones vivas, gzip, reintentos— vive en `net`: aquí solo está el
recorrido.

Uso:  uv run python -m to_markdown crawl
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from ..core import BOOKS, Book
from ..infra.monitor import bump
from ..infra.net import BASE, WORKERS, get_bytes, load_http, request, save_http

SUBVALUES = re.compile(r'id="i__SP_pa_menuSubvalores_compendio_1">(.*?)</div>', re.DOTALL)
ANCHOR = re.compile(r'href="w3-propertyvalue-(\d+)\.html"[^>]*>(.*?)</a>', re.DOTALL)
BODY = re.compile(r'<div id="cuerpo_documento"[^>]*>(.*)', re.DOTALL)
IMG_SRC = re.compile(r'<img [^>]*src="([^"]+)"')
TAGS = re.compile(r"<[^>]+>")
PAGE_TITLE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
SITE_SUFFIX = re.compile(r"\s*-\s*SP\.\s*Compendio de Pensiones\s*$")


# Metadatos HTTP por página (ETag / Last-Modified). Son la señal de cambio más barata y
# más autoritativa que hay: el servidor la publica y honra peticiones condicionales.
# Van por Libro, como todo lo demás: el índice de un Libro no dice nada de los otros.

def fetch(book: Book, pvid: str, revalidate: bool = False) -> str:
    """HTML de un nodo, cacheado en la carpeta de su Libro. Con `revalidate` revalida
    contra el servidor en vez de confiar en el caché: manda `If-None-Match` /
    `If-Modified-Since` y un 304 confirma que no cambió sin transferir el cuerpo.

    Medido sobre el corpus: 938 de 1.472 páginas no se tocan desde 2020 y solo ~158
    cambiaron en 2026. Una revalidación completa descarga un puñado de páginas y recibe el
    resto como 304 de cero bytes.
    """
    path = book.cache / f"{pvid}.html"
    url = f"{BASE}w3-propertyvalue-{pvid}.html"
    http = load_http(book)
    meta = http.get(pvid, {})

    if path.exists() and not revalidate:
        return path.read_text(encoding="utf-8")

    headers: dict[str, str] = {}
    if path.exists() and revalidate:
        if meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        elif meta.get("last_modified"):
            headers["If-Modified-Since"] = meta["last_modified"]

    status, response_headers, body = request(url, headers)
    if status == 304 or body is None:
        return path.read_text(encoding="utf-8")

    html = body.decode("utf-8", "replace")
    path.write_text(html, encoding="utf-8")
    http[pvid] = {
        "etag": response_headers.get("etag", ""),
        "last_modified": response_headers.get("last-modified", ""),
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    return html


def children(html: str) -> list[tuple[str, str]]:
    """Hijos de un nodo del árbol, como (pvid, título)."""
    block = SUBVALUES.search(html)
    if not block:
        return []
    return [
        (m.group(1), TAGS.sub("", m.group(2)).strip())
        for m in ANCHOR.finditer(block.group(1))
    ]


def page_title(html: str) -> str:
    """Título de la página según el propio sitio, sin el sufijo del portal.

    Es de dónde sale el nombre vigente del Libro: la raíz no tiene padre del cual heredar
    un título, y su breadcrumb no se nombra a sí mismo. Además está siempre al día — los
    breadcrumbs de 39 documentos todavía traen el nombre anterior de los Libros I y V.
    """
    match = PAGE_TITLE.search(html)
    return SITE_SUFFIX.sub("", TAGS.sub("", match.group(1))).strip() if match else ""


def body_html(html: str) -> str | None:
    """Cuerpo normativo de una hoja, o None si la página es un índice."""
    match = BODY.search(html)
    return match.group(1) if match else None


def tree_order(nodes: dict[str, dict]) -> list[str]:
    """Los nodos en profundidad, con los hijos en el orden en que el CMS los lista.

    Es el orden en que el Compendio se lee y en que la SP lo imprime en su PDF. Ordenar por
    pvid daría otra cosa: los pvid se asignan por fecha de creación, así que un capítulo
    agregado después queda al final aunque normativamente vaya al medio.
    """
    children: dict[str | None, list[str]] = {}
    for pvid, node in nodes.items():
        children.setdefault(node["parent"], []).append(pvid)
    order: list[str] = []
    stack = list(reversed(children.get(None, [])))
    while stack:
        pvid = stack.pop()
        order.append(pvid)
        stack += reversed(children.get(pvid, []))
    return order


def crawl(book: Book, pool: ThreadPoolExecutor, revalidate: bool = False) -> dict:
    """Recorre el árbol de un Libro. Devuelve su manifiesto y lo escribe a disco.

    El pool se recibe en vez de crearse aquí: un `ThreadPoolExecutor` por nivel del árbol
    levantaba hilos nuevos en cada nivel, y con ellos conexiones nuevas, que es justo lo
    que el keep-alive existe para evitar. Con un pool para toda la corrida, los tres hilos
    conservan sus tres conexiones desde la primera página hasta la última.
    """
    nodes: dict[str, dict] = {}
    frontier = [(book.pvid, "", None)]
    depth = 0

    while frontier:
        depth += 1
        pages = list(pool.map(lambda node: fetch(book, node[0], revalidate), frontier))

        next_frontier: list[tuple[str, str, str | None]] = []
        for (pvid, title, parent), html in zip(frontier, pages, strict=True):
            kids = children(html)
            nodes[pvid] = {
                "pvid": pvid,
                "title": title or page_title(html),
                "parent": parent,
                "depth": depth,
                "is_leaf": not kids,
                # "Tiene texto normativo" y "no tiene hijos" NO son lo mismo, y tratarlos
                # como sinónimos costaba 190.502 caracteres: 24 nodos del corpus tienen
                # hijos Y cuerpo propio (un Título que además imparte instrucciones, un
                # Capítulo con su preámbulo antes de los números). El PDF los imprime; el
                # pipeline los descartaba en silencio por no ser hojas.
                "has_body": body_html(html) is not None,
                "url": f"{BASE}w3-propertyvalue-{pvid}.html",
                "last_modified": load_http(book).get(pvid, {}).get("last_modified", ""),
            }
            next_frontier += [(kid, kid_title, pvid) for kid, kid_title in kids]

        print(f"  level {depth}: {len(frontier)} nodes -> {len(next_frontier)} children", flush=True)
        frontier = next_frontier

    order = tree_order(nodes)
    manifest = {
        # El Libro se identifica en su propio manifiesto: una carpeta suelta tiene que
        # poder decir de qué Libro es sin volver a config.toml.
        "book": {"slug": book.slug, "pvid": book.pvid, "title": nodes[book.pvid]["title"]},
        "order": order,
        # La lista autoritativa de páginas con texto normativo, ya en orden de lectura.
        # Que la calcule el crawl y no cada etapa es lo que impide que vuelvan a discrepar.
        "documents": [p for p in order if nodes[p]["has_body"]],
        "nodes": nodes,
        "leaves": sorted(p for p, n in nodes.items() if n["is_leaf"]),
    }
    book.file("manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def download_images(book: Book, manifest: dict, pool: ThreadPoolExecutor) -> dict[str, str]:
    """Descarga las imágenes de los cuerpos normativos del Libro, nombradas por SHA-256.

    El hash deduplica (la misma figura aparece en varias normas) y hace que el caché de
    las etapas 4 y 5 sea idempotente: re-ejecutar no vuelve a llamar al modelo.

    Deduplicar dentro del Libro y no entre Libros no cuesta nada: se verificó que ninguna
    de las 1.743 figuras del corpus aparece en dos Libros distintos.
    """
    index_path = book.file("images.json")
    index: dict[str, str] = (
        json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    )

    sources: list[str] = []
    for pvid in manifest["documents"]:
        body = body_html(fetch(book, pvid))
        if body:
            sources += [src for src in IMG_SRC.findall(body) if src not in index]
    sources = sorted(set(sources))
    print(f"  images to download: {len(sources)} (already cached: {len(index)})")

    def grab(src: str) -> tuple[str, str] | None:
        try:
            blob = get_bytes(urllib.parse.urljoin(BASE, src))
        except RuntimeError as exc:
            print(f"    failed: {src} ({exc})")
            return None
        digest = hashlib.sha256(blob).hexdigest()
        bump("images")
        suffix = Path(urllib.parse.urlparse(src).path).suffix.lower() or ".bin"
        (book.images / f"{digest}{suffix}").write_bytes(blob)
        return src, digest

    for result in pool.map(grab, sources):
        if result:
            index[result[0]] = result[1]

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index


def main(books: list[Book] | None = None, revalidate: bool = False) -> None:
    # Un solo pool para los cinco Libros: los hilos —y sus conexiones— sobreviven al cambio
    # de Libro igual que al cambio de nivel.
    with ThreadPoolExecutor(WORKERS) as pool:
        for book in books or BOOKS:
            _crawl_book(book, pool, revalidate)
    # Al salir del `with`, el pool hace `shutdown` y los hilos mueren: sus conexiones
    # —que viven en el almacenamiento local de cada hilo— se cierran con ellos.


def _crawl_book(book: Book, pool: ThreadPoolExecutor, revalidate: bool) -> None:
    print(f"\n--- {book.name} ({book.slug}) ---", flush=True)
    book.mkdirs()
    manifest = crawl(book, pool, revalidate)
    save_http(book)
    print(
        f"  nodes: {len(manifest['nodes'])} | leaves: {len(manifest['leaves'])} "
        f"| with normative text: {len(manifest['documents'])}"
    )
    index = download_images(book, manifest, pool)
    save_http(book)
    print(
        f"  images: {len(index)} references -> "
        f"{len(set(index.values()))} unique files"
    )
    dated = [n["last_modified"] for n in manifest["nodes"].values() if n["last_modified"]]
    if dated:
        print(f"  with known modification date: {len(dated)}/{len(manifest['nodes'])}")


if __name__ == "__main__":
    main()
