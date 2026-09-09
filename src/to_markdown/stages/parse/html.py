"""Del HTML de la SP a Markdown, y del Markdown a unidades numeradas.

Todo determinista, sin modelo: jerarquía, numeración, tablas y notación matemática escrita
en HTML (`<sub>`, `<sup>`) se extraen con parser.

Va aparte del ensamblado del documento porque es la parte que hay que ajustar cuando la SP
cambia su maquetación, y no tiene nada que ver con cómo se compone un documento a partir de
sus metadatos.
"""

from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser

TAGS = re.compile(r"<[^>]+>")

# Los dos marcadores con que la SP delimita el cuerpo normativo. Cortar hasta el fin del
# archivo arrastraría el pie de página; `<!--end-box-->` cierra la caja exactamente.
BODY_OPEN = '<div id="cuerpo_documento"'
BOX_END = "<!--end-box-->"

NOTE = re.compile(r"^nota\s+de\s+actualizac\w*\s*:?\s*", re.IGNORECASE)

# Un número normativo abre bloque: "1. ", "2.- ", "3) ". Es la unidad atómica con la que
# la propia norma se cita y se modifica.
UNIT_START = re.compile(r"^(\d{1,3})\s*[.\-)]\s+\S")

BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "table", "blockquote"}
HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####"}



BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "table", "blockquote"}
HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####"}

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", TAGS.sub("", text).replace("\xa0", " "))
    # La fuente escribe `VC <sub>i</sub>`; el espacio es maquetación, no notación.
    return re.sub(r"\s+(?=[_^]\{)", "", text).strip()



class BodyToMarkdown(HTMLParser):
    """Convierte el cuerpo normativo a Markdown.

    Reglas que importan y por qué:
      - `<sub>`/`<sup>` -> `_{}`/`^{}`: en este corpus son notación matemática (`VC_i`,
        `l_x`, `BH_m`), verificado sobre las 837 ocurrencias. No son notas al pie.
      - `<img>` -> `[[FIG:<sha256>]]`: marcador que resuelve la etapa 3. El `<a>` que
        envuelve la imagen se descarta; solo enlaza al archivo.
      - `<h6>` -> cita si es "Nota de actualización" (3.076 en el corpus: dicen qué NCG
        modificó el número anterior, y van pegadas a su número, nunca sueltas). Los demás
        son pies de figura y se dejan como texto.
    """

    def __init__(self, images: dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.images = images
        self.blocks: list[str] = []
        self.notes: list[str] = []
        self.figures: list[str] = []
        self._buf: list[str] = []
        self._tag: str | None = None
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._row_is_header = False
        self._cell: list[str] | None = None
        self._note: list[str] | None = None

    # -- utilidades internas -------------------------------------------------
    def _flush(self) -> None:
        text = clean_text("".join(self._buf))
        self._buf.clear()
        if not text:
            return
        if self._tag in HEADINGS:
            self.blocks.append(f"{HEADINGS[self._tag]} {text}")
        elif self._tag == "h6" and NOTE.match(text):
            self.blocks.append(f"> **Nota de actualización:** {NOTE.sub('', text)}")
        elif self._tag == "h6":
            # Los otros 71 `<h6>` del corpus son pies de figura y fuentes ("Fuente: …"),
            # no historial normativo. Se quedan en el cuerpo, junto a lo que describen.
            self.blocks.append(f"*{text}*")
        elif self._tag == "li":
            self.blocks.append(f"- {text}")
        else:
            self.blocks.append(text)

    def _emit(self, text: str) -> None:
        if self._note is not None:
            self._note.append(text)
        if self._cell is not None:
            self._cell.append(text)
        elif self._row is None:
            self._buf.append(text)
        # Texto suelto entre `</td>` y `<td>` es maquetación: se descarta.

    # -- interfaz de HTMLParser ----------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Toma independiente del contexto: el Manual de Cuentas mete sus notas dentro de
        # celdas de tabla y a mitad del texto de la celda, donde un `^Nota…` nunca calzaría.
        if tag == "h6":
            self._note = []

        attributes = dict(attrs)
        if tag == "img":
            src = attributes.get("src") or ""
            digest = self.images.get(src)
            marker = f"[[FIG:{digest}]]" if digest else f"[[FIG-MISSING:{src}]]"
            if digest:
                self.figures.append(digest)
            self._emit(f"\n\n{marker}\n\n" if self._cell is None else marker)
        elif tag == "br":
            self._emit("\n")
        elif tag == "sub":
            self._emit("_{")
        elif tag == "sup":
            self._emit("^{")
        elif tag == "table":
            self._flush()
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
            self._row_is_header = False
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._row_is_header = self._row_is_header or tag == "th"
        elif tag in BLOCK_TAGS and self._table is None:
            self._flush()
            self._tag = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == "h6" and self._note is not None:
            text = clean_text("".join(self._note))
            self._note = None
            if NOTE.match(text):
                self.notes.append(NOTE.sub("", text))

        if tag in ("sub", "sup"):
            self._emit("}")
        elif tag in ("td", "th") and self._cell is not None:
            self._row.append(clean_text("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self._table.append((self._row_is_header, self._row))
            self._row = None
        elif tag == "table" and self._table is not None:
            self.blocks.append(_markdown_table(self._table))
            self._table = None
            self._tag = None
        elif tag in BLOCK_TAGS and self._table is None:
            self._flush()
            self._tag = None

    def handle_data(self, data: str) -> None:
        self._emit(data)

    def result(self) -> str:
        self._flush()
        return "\n\n".join(block for block in self.blocks if block.strip())


def _markdown_table(raw: list[tuple[bool, list[str]]]) -> str:
    """Renderiza una tabla. Dos decisiones de fidelidad:

    - Las celdas vacías se conservan: en normativa una celda vacía puede ser información
      (un campo que no aplica), no ruido.
    - Solo 4 de las 371 tablas del corpus traen `<th>`. En las otras 367, promover la
      primera fila a encabezado convertiría un dato en un rótulo y un agente leería mal la
      tabla. Sin `<th>` se emite un encabezado vacío y todas las filas quedan como datos.
    """
    rows = [(is_header, row) for is_header, row in raw if any(cell for cell in row)]
    if not rows:
        return ""
    width = max(len(row) for _, row in rows)
    rows = [(is_header, row + [""] * (width - len(row))) for is_header, row in rows]
    if rows[0][0]:
        header, body = rows[0][1], [row for _, row in rows[1:]]
    else:
        header, body = [""] * width, [row for _, row in rows]
    lines = [
        "| " + " | ".join(cell.replace("|", "\\|") for cell in header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    lines += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in body]
    return "\n".join(lines)


def split_units(markdown: str, pvid: str, citation: str) -> list[dict]:
    """Parte el cuerpo en unidades numeradas direccionables.

    Es lo que hace que un changelog sirva: "el N° 4 del Capítulo II cambió" es accionable,
    "este documento de 12 KB cambió" no lo es. El `unit_id` usa el número porque es como la
    norma se cita a sí misma; la renumeración (93 casos documentados en el corpus) se
    detecta después emparejando por `sha256`, no por posición.
    """
    units: list[dict] = []
    current: dict | None = None
    preamble: list[str] = []

    for block in markdown.split("\n\n"):
        match = UNIT_START.match(block)
        if match:
            if current:
                units.append(current)
            current = {"number": match.group(1), "blocks": [block]}
        elif current is not None:
            current["blocks"].append(block)
        else:
            preamble.append(block)
    if current:
        units.append(current)

    if preamble and any(b.strip() for b in preamble):
        units.insert(0, {"number": None, "blocks": preamble})

    out = []
    for unit in units:
        text = "\n\n".join(unit["blocks"]).strip()
        if not text:
            continue
        number = unit["number"]
        out.append({
            "unit_id": f"{pvid}#{number or 'preamble'}",
            "number": number,
            "citation": f"{citation}, N° {number}" if number else citation,
            "text": text,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    return out
