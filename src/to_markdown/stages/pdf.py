"""Etapa 5: baja los cinco PDF oficiales que la SP publica, uno por Libro.

El portal enlaza el Libro completo desde su propia raíz (`fo-propertyvalue-<pvid>.pdf`), así
que la URL sale del **pvid**, que es la única clave estable del árbol — la misma con la que
`crawl` particiona el corpus. No hay una lista de URLs que mantener al día.

El archivo se guarda como `assets/books/Book<N>.pdf` (`pdf_file` de `config.toml`), no con el
nombre del servidor: `fo-propertyvalue-2536.pdf` no dice de qué Libro es, y el nombre es lo
único que ve `compare` cuando abre el archivo.

Renombrar sin verificar sería lo peor de los dos mundos: un `Book3.pdf` que en realidad es el
Libro IV se compararía contra el árbol equivocado y el informe de cobertura saldría lleno de
"contenido solo en el PDF" sin que nada avise. Por eso el PDF se descarga a un temporal, se
verifica contra lo que extrajo el crawler, y **solo entonces** se mueve a su nombre final.

Uso:  uv run python -m to_markdown pdf
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..core import ASSETS, BOOKS, CONFIG, Book
from ..infra.monitor import bump
from ..infra.net import close_connections, request

BASE = CONFIG["crawl"]["base_url"]

# El encabezado corrido que el PDF imprime en TODAS sus páginas. Es la forma en que el
# documento se identifica a sí mismo, y por eso es la verificación autoritativa de que el
# archivo que bajamos es el Libro que dice el nombre con que lo guardamos.
# Se ancla a la línea COMPLETA y no a la subcadena: el cuerpo normativo también se refiere
# al Compendio ("…del Libro I del Compendio de Normas del Sistema de Pensiones. Información"),
# y tomar cualquier línea que lo mencione daba un falso positivo en el Libro I.
RUNNING_HEAD = re.compile(
    r"^Compendio de Normas del Sistema de Pensiones\s*-\s*(Libro [IVXLC]+)\s*$", re.MULTILINE
)
# Los guiones del PDF no siempre son el ASCII: se normalizan antes de comparar.
DASHES = re.compile(r"[‐‑‒–—]")
# Las páginas del PDF repiten el `path` de la norma tal como lo publica el portal
# ("Libro III, Título I Pensiones, Letra B Pensión de Vejez"). Es literalmente el mismo
# string que `parse` guarda en `path`, y eso es lo que permite cruzarlos sin heurística.
BREADCRUMB = re.compile(r"^(Libro\s+[IVXLC]+\s*,.+)$", re.MULTILINE)
# El PDF escribe el mismo breadcrumb con espaciado propio: unas páginas ponen
# "Libro III,Título V" sin el espacio tras la coma. Se uniforma antes de cruzar.
SPACING = re.compile(r"\s+")

# Cómo se muestrea el PDF para verificarlo: cuatro bloques de páginas CONTIGUAS repartidos
# por el documento, no páginas sueltas equiespaciadas.
#
# MEDIDO, y la diferencia no es menor: el encabezado corrido está en todas las páginas, pero
# el breadcrumb solo aparece donde arranca una sección, y esos arranques van agrupados. Con
# 32 páginas sueltas el Libro IV devolvía 10 breadcrumbs en 34 s; con 4 bloques de 16 —las
# mismas 64 páginas, pero en 4 llamadas a `pdftotext` en vez de 32— devuelve 23 en 4,7 s.
# Un bloque contiguo cae dentro de una sección entera, y leer un rango cuesta una sola
# apertura del archivo en lugar de una por página.
BLOCKS = 4
BLOCK_PAGES = 16
# Se muestrea el cuerpo, no los extremos: las primeras páginas son el índice y la última
# puede quedar en blanco. Ni una ni otra traen breadcrumb.
SAMPLE_RANGE = (0.08, 0.92)
# Cuántas de las páginas muestreadas deben traer un breadcrumb reconocible para dar la
# correspondencia por comprobada. Con menos, se avisa en vez de afirmar.
MIN_CRUMBS = 2

# El índice HTTP de los PDF. Va junto a los archivos y no bajo `data/`, porque describe a
# `assets/books/` y tiene que viajar con él: sin ETag, cada corrida re-descargaría 130 MB.
HTTP = ASSETS / "books" / "http.json"


def source_url(book: Book) -> str:
    """El PDF del Libro en el portal. La raíz del Libro lo enlaza como `AccesoPDF`."""
    return f"{BASE}fo-propertyvalue-{book.pvid}.pdf"


def load_http() -> dict[str, dict]:
    return json.loads(HTTP.read_text(encoding="utf-8")) if HTTP.exists() else {}


def save_http(index: dict[str, dict]) -> None:
    HTTP.parent.mkdir(parents=True, exist_ok=True)
    HTTP.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def page_count(path: Path) -> int:
    """Páginas del PDF según `pdfinfo`. 0 si el archivo no es un PDF legible."""
    if not shutil.which("pdfinfo"):
        raise SystemExit(
            "missing `pdfinfo` (poppler-utils package, the same one that ships pdftotext)"
        )
    done = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=False)
    if done.returncode:
        return 0
    match = re.search(r"^Pages:\s+(\d+)", done.stdout, re.MULTILINE)
    return int(match.group(1)) if match else 0


def sample_text(path: Path, pages: int) -> str:
    """Texto de los bloques de muestreo, concatenado.

    `pdftotext -f N -l M` extrae el rango en una sola pasada, así que un bloque de 16
    páginas cuesta lo mismo que una suelta: la apertura del archivo domina, no las páginas.
    """
    span = min(BLOCK_PAGES, max(1, pages // BLOCKS))
    low, high = SAMPLE_RANGE
    out: list[str] = []
    for i in range(BLOCKS):
        offset = low + (high - low) * i / max(1, BLOCKS - 1)
        first = min(max(1, int(pages * offset) - span // 2), max(1, pages - span + 1))
        done = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-f", str(first), "-l", str(min(pages, first + span - 1)),
             str(path), "-"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if done.returncode == 0:
            out.append(done.stdout)
    return DASHES.sub("-", "\n".join(out))


def _spaced(text: str) -> str:
    """Forma mismo de un breadcrumb: coma siempre seguida de un espacio."""
    return SPACING.sub(" ", text.replace(",", ", ")).strip()


def crawled_paths(book: Book) -> set[str] | None:
    """Los `path` que el crawler extrajo para este Libro, o None si todavía no corrió."""
    source = book.file("documents.json")
    if not source.exists():
        return None
    documents = json.loads(source.read_text(encoding="utf-8"))
    return {_spaced(d["path"]) for d in documents if d.get("path")}


def verify(path: Path, book: Book) -> tuple[list[str], int]:
    """Revisa que este PDF sea el de `book`.

    Devuelve `(problemas, secciones_cruzadas)`. Lista de problemas vacía significa correcto;
    el segundo valor es cuántas secciones del PDF se reconocieron en el árbol del crawler,
    que es lo que hace informativo el resumen en vez de un "ok" mudo.

    Dos comprobaciones, y la segunda es la que el nombre del archivo no puede dar:

    1. **El PDF se declara a sí mismo.** Cada página lleva "Compendio de Normas del Sistema
       de Pensiones - Libro III" como encabezado corrido. Si alguna página muestreada nombra
       otro Libro, el archivo no es el que creemos.
    2. **Corresponde a lo que extrajo el crawler.** Las páginas repiten el `path` de la norma
       con el mismo texto que `parse` guardó en `documents.json`. Cruzarlos comprueba que
       este PDF y el subárbol que recorrió el crawler son el mismo Libro, no solo que ambos
       dicen "Libro III".
    """
    problems: list[str] = []
    pages = page_count(path)
    if not pages:
        return [f"not a readable PDF ({path.stat().st_size:,} bytes)"], 0

    expected = book.roman  # "Libro III", como el PDF se encabeza a sí mismo
    text = sample_text(path, pages)
    heads = set(RUNNING_HEAD.findall(text))
    crumbs = BREADCRUMB.findall(text)

    if not heads:
        problems.append(
            f"no running header in {BLOCKS * BLOCK_PAGES} sampled pages of {pages}"
        )
    elif heads != {expected}:
        problems.append(
            f"header says {sorted(heads)} but {book.pdf_file} must be {expected}"
        )

    matched = 0
    known = crawled_paths(book)
    if known is None:
        print(f"{book.slug:10} note: no crawl to cross-check against; run `parse` first")
    elif len(crumbs) < MIN_CRUMBS:
        print(f"{book.slug:10} note: only {len(crumbs)} sections sampled, cross-check inconclusive")
    else:
        # Se cruza por prefijo y no por igualdad: el PDF corta los breadcrumbs largos con
        # el salto de línea ("…Estadísticas de afiliados pensionados y de Bonos de"), así
        # que exigir el string entero declararía huérfanas dos de cada tres secciones
        # legítimas. `path` empieza por el Libro, así que un breadcrumb del Libro
        # equivocado no puede calzar con este conjunto ni por casualidad.
        unknown = [
            c for c in (_spaced(x) for x in crumbs)
            if not any(k.startswith(c) or c.startswith(k) for k in known)
        ]
        matched = len(crumbs) - len(unknown)
        if len(unknown) > len(crumbs) // 2:
            problems.append(
                f"{len(unknown)}/{len(crumbs)} sampled sections are not in the crawled "
                f"{book.slug} tree, e.g. {unknown[0][:70]!r}"
            )
    return problems, matched


def fetch(book: Book, index: dict[str, dict]) -> str:
    """Deja el PDF del Libro en `assets/books/<pdf_file>`. Devuelve qué pasó.

    Idempotente por ETag: el servidor los publica y honra `If-None-Match`, así que una
    corrida sobre un PDF vigente cuesta una petición condicional y cero bytes. Sin eso,
    cada corrida por defecto re-descargaría los 130 MB de los cinco Libros.
    """
    target = book.pdf_source
    target.parent.mkdir(parents=True, exist_ok=True)
    url = source_url(book)
    meta = index.get(book.slug, {})

    if target.exists():
        headers = {}
        if meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        elif meta.get("last_modified"):
            headers["If-Modified-Since"] = meta["last_modified"]
        status, response, _ = request(url, headers, method="HEAD")
        server_etag = response.get("etag", "")
        length = int(response.get("content-length") or 0)
        # Sin ETag guardado —la primera corrida después de bajarlos a mano— el tamaño
        # decide. Re-descargar 130 MB para descubrir que el archivo ya estaba sería el
        # comportamiento que esta etapa existe para evitar.
        fresh = status == 304 or (server_etag and server_etag == meta.get("etag"))
        if not fresh and not meta and length and length == target.stat().st_size:
            fresh = True
        if fresh:
            index[book.slug] = {
                "url": url, "etag": server_etag or meta.get("etag", ""),
                "last_modified": response.get("last-modified", meta.get("last_modified", "")),
                "bytes": target.stat().st_size,
                # Se anota QUÉ archivo se verificó, no solo que se verificó: si el PDF
                # cambia en disco, el tamaño deja de calzar y la comprobación se rehace.
                "verified": meta.get("verified") if meta.get("bytes") == target.stat().st_size
                            else None,
            }
            return "cached"

    status, response, body = request(url)
    if body is None:
        raise SystemExit(f"empty response for {url}")

    # Se verifica en un temporal y recién después se mueve. Un PDF que no corresponde no
    # puede pisar al que ya estaba: es el mismo "fallar cerrado" con que `guard` protege
    # el corpus. Si la SP publica el Libro IV bajo el enlace del III, aquí se detiene.
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / target.name
        staged.write_bytes(body)
        problems, _ = verify(staged, book)
        if problems:
            detail = "\n".join(f"  - {p}" for p in problems)
            raise SystemExit(
                f"\nWRONG PDF for {book.name} ({book.slug}) — nothing was written:\n{detail}\n\n"
                f"  downloaded: {url}\n"
                f"  would be:   {target}\n\n"
                f"The SP may have moved the Book behind another pvid. Check the `AccesoPDF`\n"
                f"link on {BASE}w3-propertyvalue-{book.pvid}.html before continuing.\n"
            )
        shutil.move(str(staged), str(target))
        bump("pdf_bytes", len(body))

    index[book.slug] = {
        "url": url,
        "etag": response.get("etag", ""),
        "last_modified": response.get("last-modified", ""),
        "bytes": len(body),
    }
    return "downloaded"


def main(books: list[Book] | None = None) -> None:
    index = load_http()
    for book in books or BOOKS:
        state = fetch(book, index)
        target = book.pdf_source
        meta = index[book.slug]
        size = target.stat().st_size

        # Verificar cuesta ~1,8 s por Libro (4 llamadas a `pdftotext` sobre un PDF de hasta
        # 66 MB), y la etapa está en la corrida por defecto. Si el archivo en disco es
        # exactamente el que ya se verificó —mismo tamaño— no hay nada nuevo que comprobar.
        # Cualquier cambio de tamaño, incluido un archivo puesto a mano, la vuelve a exigir.
        remembered = meta.get("verified") if meta.get("bytes") == size else None
        if state == "cached" and isinstance(remembered, int):
            problems, crossed, how = [], remembered, "verified earlier"
        else:
            problems, crossed = verify(target, book)
            how = "downloaded" if state == "downloaded" else "re-verified"

        if problems:
            detail = "\n".join(f"  - {p}" for p in problems)
            raise SystemExit(
                f"\nWRONG PDF on disk for {book.name} ({book.slug}):\n{detail}\n\n"
                f"  file: {target}\n\n"
                f"Delete it and re-run `uv run python -m to_markdown pdf` to fetch it again.\n"
            )
        index[book.slug] = {**meta, "bytes": size, "verified": crossed}
        print(
            f"{book.slug:10} {target.name:10} {size / 1e6:6.1f} MB "
            f"| {page_count(target):5} pages | {how:15} | {book.roman}, "
            f"{crossed} sections match the crawl"
        )
    save_http(index)
    # La etapa corre en el hilo principal, así que su conexión no muere con un pool.
    close_connections()
    print(f"{'':10} -> {ASSETS / 'books'}")


if __name__ == "__main__":
    main()
