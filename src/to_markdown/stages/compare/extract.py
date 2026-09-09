"""Lo que se saca del PDF oficial: su texto y sus figuras.

Las dos cosas van juntas porque son la misma responsabilidad —lanzar `poppler` y quedarse
con lo que devuelve— y son la única parte de la comparativa que toca el sistema de archivos.
El resto de la etapa son funciones sobre cadenas.

Incluye la forma canónica con que se cotejan los dos lados: es lo primero que se le hace al
texto recién extraído, así que vive con la extracción.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unicodedata

from PIL import Image

from ...core import Book

PAGE_NUMBER = re.compile(r"^\s*\d{1,4}\s*$")
# Línea de índice: texto, puntos de relleno y el número de página. El índice del PDF no
# existe en la web —es navegación, no norma— y sin descartarlo los primeros capítulos
# anclarían dentro de él.
TOC_LINE = re.compile(r"\.{5,}\s*\d+\s*$")
FIGURE_MARKER = re.compile(r"\[\[FIG(?:-MISSING)?:[^\]]*\]\]")

def canonical(text: str) -> str:
    """Uniforma comillas, guiones y espacios **sin tocar las mayúsculas**.

    La caja se baja aparte y solo para comparar. El texto que se escribe a los `.md` sale
    de aquí: un compendio normativo en minúsculas no es una transcripción fiel, es un
    subproducto de la herramienta de comparación filtrándose al entregable.
    """
    text = unicodedata.normalize("NFC", text).replace("\xa0", " ")
    text = re.sub(r"[’‘´`]", "'", re.sub(r"[“”]", '"', text))
    text = re.sub(r"[‐‑‒–—]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str) -> str:
    """Forma canónica para comparar. `lower` y no `casefold` a propósito: casefold no
    conserva la longitud (ß -> ss) y aquí los desplazamientos del texto en caja original y
    del texto en minúsculas tienen que coincidir carácter a carácter."""
    return canonical(text).lower()


def extract_text(book: Book, force: bool = False) -> str:
    """Texto del PDF oficial, cacheado. Usa `pdftotext` de poppler, que ya está en el
    sistema: para leer un PDF con capa de texto no hace falta una dependencia más."""
    out = book.pdf / "text.txt"
    if out.exists() and not force and out.stat().st_mtime >= book.pdf_source.stat().st_mtime:
        return out.read_text(encoding="utf-8")
    if not shutil.which("pdftotext"):
        raise SystemExit(
            "missing `pdftotext` (poppler-utils package). It is the only thing this stage needs\n"
            "outside Python:  sudo pacman -S poppler   |   apt install poppler-utils"
        )
    if not book.pdf_source.exists():
        raise SystemExit(f"missing official PDF: {book.pdf_source}")
    book.pdf.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(book.pdf_source), str(out)],
        check=True, capture_output=True,
    )
    return out.read_text(encoding="utf-8")



def clean_pages(raw: str, book: Book) -> tuple[str, list[tuple[int, int]], int]:
    """Quita la utilería de página y devuelve (texto en caja original, offset->página,
    líneas de índice descartadas).

    Se van tres cosas que el PDF tiene por ser un documento impreso y la web no tiene por
    no serlo: el encabezado corrido, el número de página y el índice. Ninguna es norma, y
    contarlas como "contenido de más" sería ruido que tapa los hallazgos reales.
    """
    header = normalize(f"Compendio de Normas del Sistema de Pensiones - {book.roman}")
    chunks: list[str] = []
    starts: list[int] = []
    skipped = 0
    total = 0
    for number, page in enumerate(raw.split("\f"), start=1):
        lines = [line for line in page.split("\n") if line.strip()]
        while lines and (normalize(lines[0]) == header or PAGE_NUMBER.match(lines[0])):
            lines.pop(0)
        keep = [line for line in lines if not TOC_LINE.search(line)]
        skipped += len(lines) - len(keep)
        piece = canonical(" ".join(keep))
        if not piece:
            continue
        chunks.append(piece)
        starts.append(total)
        total += len(piece) + 1
    text = " ".join(chunks)
    # offset de inicio -> número de página, para poder citar "página N del PDF".
    return text, list(zip(starts, range(1, len(starts) + 1), strict=True)), skipped


def tree_order(manifest: dict) -> list[str]:
    """Los nodos en profundidad, con los hijos en el orden en que el CMS los lista.

    Es el orden en que el Compendio se lee y se imprime. `manifest["leaves"]` está ordenado
    por pvid, que no es lo mismo: los pvid se asignan por fecha de creación, así que un
    capítulo agregado después queda al final aunque vaya al medio.
    """
    children: dict[str | None, list[str]] = {}
    for pvid, node in manifest["nodes"].items():
        children.setdefault(node["parent"], []).append(pvid)
    order: list[str] = []
    stack = list(reversed(children.get(None, [])))
    while stack:
        pvid = stack.pop()
        order.append(pvid)
        stack += reversed(children.get(pvid, []))
    return order




def extract_images(book: Book, force: bool = False) -> dict[str, str]:
    """Extrae las figuras embebidas en el PDF, nombradas por SHA-256 como en el lado web.

    Se usa `pdfimages` de poppler, que ya viene con `pdftotext`. Medido sobre el Libro I:
    devuelve 72 imágenes, exactamente las 72 que tiene el portal, sin duplicados ni
    utilería de página — el PDF lo genera Apache FOP desde el mismo CMS, así que embebe
    las figuras y nada más.

    El índice va por página (`p0007-000`) y no por orden de aparición: es lo que permite
    devolverle cada figura a la sección que la contiene, ya que de la sección conocemos su
    rango de páginas.
    """
    index_path = book.file_pdf("images.json")
    if index_path.exists() and not force:
        return json.loads(index_path.read_text(encoding="utf-8"))
    if not shutil.which("pdfimages"):
        raise SystemExit("missing `pdfimages` (poppler-utils package, same one that ships pdftotext)")

    book.pdf_images.mkdir(parents=True, exist_ok=True)
    for stale in book.pdf_images.glob("*.png"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["pdfimages", "-png", "-p", str(book.pdf_source), f"{tmp}/i"],
            check=True, capture_output=True,
        )
        index: dict[str, str] = {}
        for path in sorted(pathlib.Path(tmp).glob("i-*.png")):
            # `i-<página>-<n>.png`, que es lo que produce `pdfimages -p`.
            _, page, number = path.stem.split("-")
            blob = path.read_bytes()
            digest = hashlib.sha256(blob).hexdigest()
            (book.pdf_images / f"{digest}.png").write_bytes(blob)
            index[f"p{page}-{number}"] = digest

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index



def visual_key(path: pathlib.Path) -> bytes | None:
    """Huella visual de una figura: 16x16 en gris.

    Contar archivos no sirve para responder "¿el PDF trae más figuras?". El PDF embebe la
    misma figura varias veces con compresión distinta —son bytes distintos y SHA-256
    distintos— y el portal la sirve en JPG mientras que `pdfimages` la devuelve en PNG. Sin
    normalizar, el PDF parecía traer 122 figuras de más; comparadas por píxeles, 1.714 de
    1.744 son la misma.
    """
    try:
        with Image.open(path) as im:
            return im.convert("L").resize((16, 16), Image.LANCZOS).tobytes()
    except Exception:  # noqa: BLE001 — una figura ilegible no puede tumbar el informe
        return None


def _keys(paths: list[pathlib.Path], cache: dict[str, str]) -> set[bytes]:
    """Huellas visuales de un conjunto de figuras, memoizadas por nombre de archivo.

    El nombre ES el SHA-256 del contenido, así que la huella de un archivo dado no puede
    cambiar nunca: memoizarla es exacto, no una aproximación. MEDIDO sobre el Libro III,
    que tiene 1.683 figuras entre los dos lados: decodificarlas con Pillow en cada corrida
    costaba 11,9 s de los 37,5 s de la etapa. Con caché, la segunda corrida no abre ninguna.
    """
    out: set[bytes] = set()
    for path in paths:
        hit = cache.get(path.name)
        if hit is None:
            key = visual_key(path)
            # Se guarda también el fallo (`""`), o una figura ilegible se reintentaría en
            # cada corrida para volver a fallar igual.
            cache[path.name] = hit = key.hex() if key else ""
        if hit:
            out.add(bytes.fromhex(hit))
    return out


def compare_figures(book: Book) -> dict:
    """Las figuras del PDF contra las del portal, por contenido y no por archivo."""
    cache_path = book.file_pdf("visual_keys.json")
    cache: dict[str, str] = (
        json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    )
    before = len(cache)
    web = _keys(sorted(book.images.iterdir()), cache)
    pdf = _keys(sorted(book.pdf_images.iterdir()), cache)
    if len(cache) != before:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return {
        "web_files": len(list(book.images.iterdir())),
        "pdf_files": len(list(book.pdf_images.iterdir())),
        "web_distinct": len(web),
        "pdf_distinct": len(pdf),
        "shared": len(web & pdf),
        "only_in_web": len(web - pdf),
        "only_in_pdf": len(pdf - web),
    }


def images_by_page(index: dict[str, str]) -> dict[int, list[str]]:
    pages: dict[int, list[str]] = {}
    for key, digest in index.items():
        pages.setdefault(int(key[1:].split("-")[0]), []).append(digest)
    return pages


