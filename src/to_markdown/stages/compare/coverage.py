"""La medición: n-gramas, cobertura léxica y el veredicto de cada capítulo.

Son funciones puras sobre texto ya normalizado. Que no toquen disco ni red es lo que
permite probar el criterio con dos cadenas inventadas en vez de con un corpus entero.
"""

from __future__ import annotations

import re
import sys
from collections import Counter

from ...core import CONFIG
from .extract import normalize

SHINGLE = CONFIG["compare"]["shingle"]
HEADING_GAP = CONFIG["compare"]["heading_gap"]
# Caracteres del cuerpo que sirven de ancla de respaldo cuando el encabezado no calza.
BODY_ANCHOR = CONFIG["compare"]["body_anchor"]

FIGURE_MARKER = re.compile(r"\[\[FIG(?:-MISSING)?:[^\]]*\]\]")
WORD = re.compile(r"\w+", re.UNICODE)

def occurrences(text: str, document: dict) -> list[tuple[int, int, str]]:
    # `text` viene en minúsculas: aquí solo se buscan posiciones, nunca se devuelve texto.
    """Todos los encabezados de este documento en el PDF, como (inicio, fin de título, cómo).

    Se buscan TODAS las apariciones y no la siguiente hacia adelante. Buscar de a una,
    avanzando, parecía razonable —y valida que el orden coincida— pero deja sangrando el
    corte: el PDF agrupa los Anexos de otra forma que el árbol del portal, así que un
    capítulo se ancla más allá de donde de verdad empieza y el anterior se queda con su
    texto. Con todas las apariciones a la vista, cada sección termina en el encabezado que
    de verdad la sigue, sea de quien sea.
    """
    path, title = normalize(document["path"]), normalize(document["title"])
    found: list[tuple[int, int, str]] = []
    if title:
        at_path = text.find(path)
        while at_path >= 0:
            at_title = text.find(title, at_path)
            if at_title >= 0 and at_title - (at_path + len(path)) <= HEADING_GAP:
                found.append((at_path, at_title + len(title), "heading"))
            at_path = text.find(path, at_path + 1)
    if found:
        return found

    # Respaldo: el propio cuerpo. Cubre los capítulos cuyo encabezado en el PDF no coincide
    # con el `path` de la web —el PDF imprime un encabezado corrido que a veces difiere—,
    # donde el texto sí está y saldría como un falso "ausente".
    body = normalize(FIGURE_MARKER.sub(" ", document["markdown"]))[:BODY_ANCHOR]
    if len(body) >= 40:
        at_body = text.find(body)
        if at_body >= 0:
            return [(at_body, at_body, "body")]
    return []



def shingles(text: str, size: int = SHINGLE) -> list[tuple[tuple[str, ...], int]]:
    """N-gramas de palabras con su posición. Comparar por n-gramas y no por párrafos es lo
    que hace que un salto de línea distinto no cuente como contenido distinto.

    El n-grama es una **tupla de palabras**, no la cadena unida. Es exactamente la misma
    identidad —dos tuplas son iguales si y solo si sus palabras lo son— pero sin construir
    2 millones de cadenas de las que nadie lee nunca el contenido: aquí el n-grama solo se
    usa como miembro de un conjunto, y `runs()` agrupa por la posición, no por el texto.

    Las palabras se internan porque el corpus repite muchísimo ("de", "la", "pensión"):
    con `sys.intern` todas las apariciones comparten un objeto, y con él su hash ya
    calculado, que es lo que hace barato hashear la tupla.

    MEDIDO sobre los 3 MB del Libro III: 1,93 s con cadenas unidas, 0,87 s así. La etapa
    completa baja de 29,2 s a 20,6 s y **los 1.214 veredictos salen idénticos**.
    """
    words: list[str] = []
    positions: list[int] = []
    for match in WORD.finditer(text):
        words.append(sys.intern(match.group()))
        positions.append(match.start())
    if len(words) < size:
        return [(tuple(words), 0)] if words else []
    return [
        (tuple(words[i : i + size]), positions[i]) for i in range(len(words) - size + 1)
    ]


def runs(missing: list[tuple[tuple[str, ...], int]], text: str, size: int = SHINGLE) -> list[str]:
    """Agrupa n-gramas sueltos en pasajes contiguos legibles.

    Un listado de 3.000 n-gramas no dice nada; "este párrafo de 400 caracteres está en el
    PDF y no en la web" sí. La agrupación es lo que convierte una métrica en un hallazgo.
    """
    out: list[str] = []
    start = end = None
    for _, position in missing:
        if start is None:
            start = end = position
        elif position - end <= len(text[end:position]) and position - end < 200:
            end = position
        else:
            out.append(text[start:end + 200].strip())
            start = end = position
    if start is not None:
        out.append(text[start:end + 200].strip())
    return out


def lexical_coverage(text: str, bag: Counter[str]) -> float:
    """Cuánto del texto existe en el otro lado **sin importar el orden**.

    Es la métrica que distingue las dos cosas que un n-grama confunde. El Manual de Cuentas
    del Libro IV lo muestra: la web lo publica como tabla HTML y sale `| nivel | cuenta de
    mayor. |`; el PDF imprime esas mismas celdas seguidas y en otro orden de columnas. Los
    n-gramas no calzan y parece contenido nuevo, pero las 21 palabras distintivas del
    pasaje están las 21 en la web.

    Con las dos juntas la lectura es inequívoca: n-gramas bajos y léxico alto es
    reformateo; los dos bajos es contenido que de verdad solo está de un lado.
    """
    tokens = Counter(m.group() for m in WORD.finditer(text))
    total = sum(tokens.values())
    if not total:
        return 1.0
    return sum(min(count, bag[token]) for token, count in tokens.items()) / total


def verdict(ngram: float, lexical: float, suspect: bool) -> str:
    """Cómo se lee un capítulo. Las claves van en inglés, como todo identificador de
    esquema; la prosa del informe, en español.

    `unaligned` existe para no mentir: cuando el corte absorbió texto vecino, el capítulo
    trae párrafos que pertenecen a otro y la pregunta "¿esto sobra?" no tiene respuesta a
    ese nivel. Meterlo en `extra_in_pdf` inflaba el hallazgo con texto que sí está en la
    web, dos capítulos más allá — que fue exactamente lo que pasó al medirlo sin esta clase.
    """
    if ngram >= 0.95:
        return "match"
    if suspect:
        return "unaligned"
    if lexical >= 0.95:
        return "reformatted"
    return "extra_in_pdf"


def compare_document(
    pdf_text: str,
    web_text: str,
    web_reference: set[str],
    pdf_reference: set[str],
    web_bag: Counter[str],
    pdf_bag: Counter[str],
) -> dict:
    """Qué trae cada lado que el otro no, para un mismo capítulo.

    La pertenencia se resuelve contra el **Libro entero**, no contra el capítulo alineado
    enfrente. Es deliberado y corrige un artefacto que hacía inservible el número: el PDF
    agrupa los Anexos de otra forma que el árbol del portal, así que un capítulo puede
    quedar alineado unos párrafos más allá de donde de verdad empieza, y su vecino absorbe
    el sobrante. Comparado contra el capítulo de enfrente, ese sobrante se reportaría como
    "contenido que solo está en el PDF" cuando está en la web, dos capítulos más allá.

    La alineación sigue sirviendo, pero para **ubicar** el hallazgo —en qué capítulo y en
    qué página del PDF está— no para decidir si es un hallazgo.
    """
    pdf_shingles = shingles(pdf_text)
    web_shingles = shingles(web_text)

    only_pdf = [(s, p) for s, p in pdf_shingles if s not in web_reference]
    only_web = [(s, p) for s, p in web_shingles if s not in pdf_reference]
    coverage_pdf = 1 - len(only_pdf) / len(pdf_shingles) if pdf_shingles else 1.0
    lexical_pdf = lexical_coverage(pdf_text, web_bag)
    return {
        "pdf_words": len(pdf_shingles),
        "web_words": len(web_shingles),
        "only_in_pdf": len(only_pdf),
        "only_in_web": len(only_web),
        "coverage_pdf": coverage_pdf,
        "coverage_web": 1 - len(only_web) / len(web_shingles) if web_shingles else 1.0,
        "lexical_pdf": lexical_pdf,
        "lexical_web": lexical_coverage(web_text, pdf_bag),
        "verdict": verdict(
            coverage_pdf, lexical_pdf, len(pdf_shingles) > 3 * len(web_shingles) + 250
        ),
        # Una sección que quedó mucho más grande que su equivalente en la web absorbió a
        # sus vecinas: el corte no es de fiar aunque el conteo sí lo sea.
        "alignment_suspect": len(pdf_shingles) > 3 * len(web_shingles) + 250,
        "extra_in_pdf": runs(only_pdf, pdf_text)[:5],
        "extra_in_web": runs(only_web, web_text)[:5],
    }


