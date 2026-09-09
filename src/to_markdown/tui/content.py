"""Todo lo que el panel muestra en palabras y en números.

Una sola responsabilidad: **el contenido**, separado de cómo se dibuja. Aquí están las
descripciones de las etapas, el texto de los paneles informativos y la ayuda; en `app` está
el armado, y en `theme` los tonos.

Sin `textual`: son constantes y funciones puras de datos a líneas, así que se puede
comprobar cada ancho —o leer qué hace una etapa— sin levantar una interfaz. Es lo que hace
verificable que los paneles sean responsive.
"""

from __future__ import annotations

from ..analytics import es, human_bytes, processing_metrics
from ..core import BOOKS

STAGE_HELP = {
    "crawl": "Descarga las páginas del sitio de la Superintendencia",
    "refresh": "Vuelve a preguntar si algo cambió (en vez de descargar todo otra vez)",
    "parse": "Convierte esas páginas a texto ordenado y numerado",
    "changes": "Compara con la corrida anterior y dice qué cambió",
    "export": "Arma un archivo Markdown por cada Título del Compendio",
    "pdf": "Descarga los 5 PDF oficiales y comprueba que cada uno sea el que dice",
    "compare": "Contrasta el PDF oficial contra lo extraído del sitio",
    "bundle": "Deja todo listo en output/, que es lo que se entrega",
}
STAGE_WRITES = {
    "crawl": "data/web/<libro>/cache/ · images/",
    "refresh": "lo mismo que crawl, pero sin volver a bajar lo que no cambió",
    "parse": "data/web/<libro>/documents.json",
    "changes": "data/web/<libro>/changelog/",
    "export": "data/web/<libro>/markdown/ · documents.jsonl",
    "pdf": "assets/books/Book<N>.pdf",
    "compare": "data/pdf/<libro>/coverage.md",
    "bundle": "output/",
}
NEEDS_NETWORK = {"crawl", "refresh", "pdf"}
DEFAULT_STAGES = ("crawl", "parse", "changes", "export", "pdf", "compare", "bundle")
REFRESH_STAGES = ("refresh", "parse", "changes", "export", "pdf", "compare", "bundle")

# Los paneles por los que rota `tab`, en el orden en que se usan.
PANELS = ("#stages", "#books", "#log")
# Los apartados se intercalan antes del registro cuando están abiertos: ver `_panels()`.
ANALYTICS = "#analytics"
METRICS = "#metrics-box"
PERFORMANCE = "#performance"
DRAWERS = (METRICS, ANALYTICS, PERFORMANCE)
# Cada cuánto se muestrea el proceso mientras corre. Medio segundo da una curva legible
# sin que el muestreo se note en lo que mide.
SAMPLE_SECONDS = 0.5

# Tono de las líneas de los gráficos en vivo. Plotext trae su propia paleta, ajena a la del
# panel, así que se le pasa el tono a mano en cada trazo.
#
# Es el `blue` de Catppuccin Mocha (#89b4fa), el mismo acento que marca el foco: las dos
# curvas son «el programa ahora mismo», que es lo que se está mirando. Va como literal y no
# importado de `theme` porque este módulo no puede depender de textual — una prueba
# comprueba que los dos no se separen.
TONE_LINE = (137, 180, 250)



def state_lines(rows: list[dict], width: int) -> list[str]:
    """El panel de estado del corpus, escrito para el ancho disponible.

    El texto era de ancho fijo —unas 45 columnas— contra una barra que baja hasta 26, así
    que las filas se partían y la tabla dejaba de leerse. Se decide cuántas columnas caben
    ANTES de escribirlas: es la única forma de que una tabla de ancho fijo sea responsive.

    Va como función de módulo y no como método para poder probar cada ancho sin levantar
    la interfaz.
    """
    total = {k: sum(r[k] for r in rows) for k in ("documents", "units", "delivered")}
    if not total["documents"]:
        # Aquí manda el ancho igual que abajo. El mensaje medía 31 columnas fijas contra
        # una barra que baja hasta 26, así que se partía en dos justo cuando es lo ÚNICO
        # que hay en el panel — el primer día de quien estrena la herramienta.
        if width >= 31:
            message = "Todavía no hay nada descargado."
        elif width >= 24:
            message = "Nada descargado todavía."
        else:
            message = "Nada descargado."
        start = "Pulsa [b]a[/b] para empezar." if width >= 21 else "Pulsa [b]a[/b]."
        return [message, "", start]

    lines = []
    for row in rows:
        if width >= 44:
            lines.append(f"{row['slug']:<9} {row['documents']:>4} normas  "
                         f"{row['sections']:>2} títulos  {row['delivered']:>2} md")
        elif width >= 34:
            lines.append(f"{row['slug']:<9} {row['documents']:>4} nor  "
                         f"{row['sections']:>2} tít  {row['delivered']:>2} md")
        elif width >= 22:
            lines.append(f"{row['slug']:<9} {row['documents']:>4} {row['sections']:>3}")
        else:
            lines.append(f"{row['slug'][5:]:<4}{row['documents']:>5}")
    lines.append("")
    if width >= 28:
        lines += [
            f"[b]{es(total['documents'])}[/b] normas extraídas",
            f"[b]{es(total['units'])}[/b] números normativos",
            f"[b]{total['delivered']}[/b] archivos en output/",
        ]
    else:
        lines += [
            f"[b]{es(total['documents'])}[/b] normas",
            f"[b]{es(total['units'])}[/b] números",
            f"[b]{total['delivered']}[/b] md",
        ]
    return lines


def corpus_state() -> dict:
    """Lo que hay hoy en disco, por Libro. Barato: lee JSON ya escrito, no recalcula nada."""
    return {"books": [processing_metrics(book) for book in BOOKS]}



def performance_lines(summary: dict, running: bool) -> list[str]:
    """El encabezado numérico del apartado de rendimiento.

    Una curva sin escala no dice si el pico fueron 3 peticiones por segundo o 300, así que
    los gráficos van siempre acompañados de los números que los sitúan.
    """
    if not summary:
        return [
            "[b]Rendimiento del programa[/b]",
            "Todavía no hay muestras. Empieza una corrida y aparecen solas.",
        ]
    state = "corriendo" if running else "en reposo"
    return [
        f"[b]Rendimiento del programa[/b] · {state} · {summary['elapsed']:.0f} s",
        (f"peticiones {es(summary['requests'])} · "
         f"{summary['requests_per_second']:.1f}/s (pico {summary['peak_requests_per_second']:.1f}) · "
         f"red {human_bytes(summary['bytes'])}"),
        (f"memoria {summary['rss_mb']:.0f} MB (pico {summary['peak_rss_mb']:.0f}) · "
         f"CPU {summary['cpu_percent']:.0f}% · "
         f"normas {es(summary['documents'])} · figuras {es(summary['images'])}"),
    ]




HELP = """[b]Qué es esto[/b]

Una herramienta que descarga el Compendio de Normas del Sistema de Pensiones desde el
sitio de la Superintendencia de Pensiones de Chile y lo convierte a Markdown, un formato
de texto que se puede leer, buscar y versionar.

El resultado queda en la carpeta [b]output/[/b]. Eso es lo único que se entrega.


[b]Cómo se usa, paso a paso[/b]

  1. Si es la primera vez, pulsa [b]a[/b]. Hace todo el proceso de principio a fin y
     tarda unos cuatro minutos (descarga unas 1.476 páginas y 130 MB de PDF).
  2. Mira la salida en el panel de la derecha. Cada etapa dice qué encontró.
  3. Cuando termine, pulsa [b]g[/b]. Se abre un apartado con los gráficos, sin tapar
     nada; [b]g[/b] otra vez lo cierra.
  4. Los archivos quedan en [b]output/[/b], una carpeta por Libro.

Para actualizar más adelante, pulsa [b]r[/b]: en vez de descargar todo otra vez, le
pregunta al sitio qué cambió. Es mucho más rápido.


[b]Los gráficos[/b]

Todos son de tendencia: muestran cómo cambian las cosas, no una foto suelta.

  [b]Actividad normativa[/b]  Cuánto cambió la norma cada año, según las fechas que la
                       propia Superintendencia escribe en sus notas de actualización.
  [b]Duración[/b]             Cuánto tarda cada etapa y si está tardando más que antes.
  [b]Historial[/b]            Cuánto texto se extrajo en cada corrida. Una línea plana
                       significa que el proceso es reproducible.
  [b]Cobertura[/b]            El PDF oficial contra el sitio, capítulo por capítulo.
  [b]Procesamiento[/b]        Qué salió: normas, números, figuras, notas.
  [b]Descarga[/b]             Qué hay en caché y cuánto pesa.

Van uno debajo de otro en un solo desplazamiento: no hay pestañas que recorrer.


[b]Los paneles[/b]

  [b]1 · Etapas[/b]   Los pasos del proceso, en el orden en que corren.
  [b]2 · Libros[/b]   Los cinco Libros del Compendio. Puedes procesar solo algunos.
  [b]3 · Salida[/b]   Lo que las etapas van informando mientras corren.

Hay además tres apartados que se abren y se cierran con la misma tecla, uno a la vez:
[b]m[/b] las métricas del corpus, [b]g[/b] los gráficos de tendencia y [b]p[/b] el rendimiento del
programa en vivo. El que esté abierto entra en la rotación de Tab.

[b]Tab[/b] pasa de un panel al siguiente, [b]Mayús+Tab[/b] al anterior. El panel activo se
distingue por el borde más claro.


[b]Teclas[/b]

  [b]Tab[/b] / [b]Mayús+Tab[/b]  Cambiar de panel
  [b]↑[/b] [b]↓[/b]              Moverse dentro del panel
  [b]espacio[/b]           Marcar o desmarcar lo resaltado
  [b]Intro[/b]             Correr lo que esté marcado
  [b]a[/b]                 Correr todo el proceso
  [b]r[/b]                 Actualizar (pregunta qué cambió, no baja todo)
  [b]d[/b]                 Volver a la selección inicial
  [b]m[/b]                 Abrir o cerrar las métricas (la misma tecla)
  [b]g[/b]                 Abrir o cerrar los gráficos (la misma tecla)
  [b]p[/b]                 Abrir o cerrar el rendimiento en vivo (la misma tecla)
  [b]D[/b]                 Borrar contenido descargado (pide confirmar dos veces)
  [b]x[/b]                 Parar la corrida en curso
  [b]c[/b]                 Limpiar el panel de salida
  [b]?[/b]                 Esta ayuda
  [b]q[/b]                 Salir


[b]Las etapas, en palabras[/b]

  [b]crawl[/b]     Descarga las páginas del sitio. Necesita internet. Es la más lenta.
  [b]refresh[/b]   Igual que crawl, pero solo baja lo que cambió. Reemplaza a crawl.
  [b]parse[/b]     Convierte el HTML descargado a texto ordenado y numerado.
  [b]changes[/b]   Compara con la corrida anterior y escribe qué cambió.
  [b]export[/b]    Arma un archivo Markdown por cada Título del Compendio.
  [b]pdf[/b]       Descarga los 5 PDF oficiales y comprueba que cada uno sea el que dice.
  [b]compare[/b]   Contrasta el PDF oficial contra lo que se extrajo del sitio.
  [b]bundle[/b]    Deja todo listo en output/.


[b]Si algo se detiene[/b]

La herramienta está hecha para pararse antes de escribir algo malo, no para seguir de
largo. Si ves un mensaje que empieza con «DEGRADED CORPUS» o «WRONG PDF», significa que
detectó un problema y [b]no escribió nada[/b]: lo que había sigue intacto.

El mensaje dice qué invariante falló. La guía en docs/OPERATIONS.md explica cada caso.


[b]Nada de esto cuesta dinero[/b]

No hay claves de API ni servicios de pago. Solo descarga páginas públicas del sitio de la
Superintendencia, con tres conexiones a la vez para no sobrecargarlo.


[dim]Esc o q para cerrar esta ayuda.[/dim]"""


