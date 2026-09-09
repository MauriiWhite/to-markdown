"""Cómo se dibuja un número: separadores, tamaños y las primitivas de los gráficos.

Todas reciben el ancho disponible y dibujan para ese ancho. Es lo que hace que el panel
sirva igual en 80 columnas y en 200: no hay ninguna medida fija en este módulo.
"""

from __future__ import annotations

EIGHTHS = " ▏▎▍▌▋▊▉█"
BRAILLE = "⠀⣀⣄⣤⣦⣶⣷⣿"

# La paleta es monocromática, así que las categorías se distinguen por DENSIDAD DE TRAMA y
# no por color. Además de ser el pedido, es más robusto: se sigue leyendo en una terminal
# sin color, en blanco y negro, y para quien no distingue rojo de verde.
#
# El orden va de más lleno a más vacío, y ese orden ES la escala: "igual" (lleno) está mejor
# que "solo en el PDF" (casi vacío), y se ve sin consultar la leyenda.
DENSITY = {
    "match": "█",        # igual de los dos lados
    "reformatted": "▓",  # mismo contenido, otra maquetación
    "unaligned": "▒",    # el corte absorbió texto vecino, no se puede juzgar
    "extra_in_pdf": "░", # contenido que de verdad solo está en el PDF
}



def es(number: float, decimals: int = 0) -> str:
    """Número con separador de miles español, que es el idioma en que se lee el panel."""
    return f"{number:,.{decimals}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def human_bytes(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit in ("B", "KB") else f"{size:.1f} {unit}"
        size /= 1024
    return ""


def bar(value: float, top: float, width: int) -> str:
    """Barra horizontal de `width` columnas, con resolución de un octavo.

    `top` es el máximo de la serie, no del valor: las barras de un gráfico solo se pueden
    comparar entre sí si comparten escala.
    """
    if width <= 0 or top <= 0:
        return ""
    eighths = round(max(0.0, min(value / top, 1.0)) * width * 8)
    return "█" * (eighths // 8) + (EIGHTHS[eighths % 8] if eighths % 8 else "")


def sparkline(values: list[float], width: int) -> str:
    """Serie histórica en una línea. Si hay más puntos que ancho, se promedian en cubos."""
    if not values or width <= 0:
        return ""
    if len(values) > width:
        size = len(values) / width
        values = [
            sum(values[int(i * size):max(int((i + 1) * size), int(i * size) + 1)])
            / max(len(values[int(i * size):max(int((i + 1) * size), int(i * size) + 1)]), 1)
            for i in range(width)
        ]
    low, high = min(values), max(values)
    if high == low:
        # Una serie plana es información: significa que el pipeline es reproducible. Se
        # dibuja a media altura en vez de saltar a cero o a tope por una división por cero.
        return "⠤" * len(values)
    return "".join(
        BRAILLE[min(int((v - low) / (high - low) * (len(BRAILLE) - 1)), len(BRAILLE) - 1)]
        for v in values
    )



def _fit(text: str, width: int) -> str:
    """Recorta a `width` columnas. Un valor cortado se ve cortado; uno que se pasa parte la
    fila en dos y desalinea todas las barras, que es lo único que las hace comparables."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    return text[: width - 1] + "…" if width > 1 else "…"


def _room(width: int, label: int, tail: int) -> tuple[int, int]:
    """Reparte el ancho entre la barra y el valor. Devuelve `(barra, valor)`.

    El ancho pedido manda, siempre. El `max(4, …)` que había antes era un suelo FIJO en un
    módulo cuya premisa es no tener ninguno: a 28 columnas el gráfico de procesamiento
    salía de 35 y en la TUI se partía en dos. Cede primero la barra —es la comparación, y
    sin ella los números siguen ahí— y solo después el valor.
    """
    room = max(0, width - label - 3)
    tail = min(tail, room)
    return room - tail, tail


def rows_chart(rows: list[tuple[str, float, str]], width: int, label: int = 9) -> list[str]:
    """Filas `etiqueta | barra | valor`, con la barra ocupando lo que sobra."""
    if not rows:
        return ["  (sin datos)"]
    top = max((v for _, v, _ in rows), default=0)
    space, tail = _room(width, label, max((len(t) for _, _, t in rows), default=0))
    return [
        f"{name:<{label}.{label}} {bar(value, top, space):<{space}} "
        f"{_fit(text, tail):>{tail}}"
        for name, value, text in rows
    ]



def timeline(counts: dict, width: int, label: int = 6) -> list[str]:
    """Serie por período, de más viejo a más nuevo. Es la forma de un gráfico de tendencia:
    una fila por período y la escala compartida, así que la altura de la barra se lee como
    la altura de la anterior."""
    if not counts:
        return ["  (sin datos)"]
    top = max(counts.values())
    space, tail = _room(width, label, max(len(str(v)) for v in counts.values()))
    return [
        f"{_fit(str(key), label):<{label}} {bar(value, top, space):<{space}} "
        f"{_fit(str(value), tail):>{tail}}"
        for key, value in sorted(counts.items())
    ]


