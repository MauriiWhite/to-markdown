"""El tema Catppuccin Mocha y la hoja de estilos del panel.

Se registra como TEMA y no como variables de CSS porque los colores que los widgets de
textual eligen solos —las teclas del pie, los avisos, el cursor de los campos— salen de
`accent`, `success`, `warning` y `error`, que se leen del tema y no del CSS de la app.
Parchear el CSS no los alcanza.

Cómo está aplicada la paleta, que es lo que hay que respetar al tocar algo:

  **Elevación.** Catppuccin ordena sus fondos de más hondo a más alto: `crust` → `mantle` →
  `base` → `surface0…2`. Aquí `base` es la pantalla, `mantle` el interior de los paneles
  (hundidos respecto de la pantalla) y `surface0` las barras que flotan encima —encabezado,
  estado y pie—. Un panel nunca es más claro que la barra que lo corona.

  **Texto.** Una sola escala, de más a menos importante: `text` para el contenido,
  `subtext0` para lo explicativo, `overlay1` para lo apagado. No se usa un acento como color
  de párrafo: los acentos significan algo y gastarlos en prosa los vacía.

  **Un acento interactivo, y uno solo.** `blue` marca lo que tiene el foco, y nada más.
  Si el borde azul apareciera en dos sitios a la vez dejaría de responder «dónde estoy».
  Los modales se distinguen con `lavender` porque son otra capa, no otro foco.

  **Los acentos semánticos no decoran.** `green` es lo que sí entra en la corrida, `yellow`
  avisa, `red` es un error, `peach` marca lo que sale a internet. Ningún acento se usa
  «porque queda bien»: el tema monocromático anterior los aplanó todos a un mismo gris
  justamente para que nadie los leyera como decoración, y esa disciplina se conserva.

  **El color nunca es el único canal.** Las categorías de los gráficos se siguen
  distinguiendo por DENSIDAD DE TRAMA (`█▓▒░`, ver `analytics.format`), no por matiz. El
  color queda como refuerzo redundante, que es lo que hace que el panel siga leyéndose en
  una terminal sin color y para quien no distingue un matiz de otro.
"""

from __future__ import annotations

from textual.theme import Theme

# La paleta oficial de Catppuccin Mocha, literal y con sus nombres. Va entera aunque no se
# use cada tono: es la referencia contra la que se comprueba que no se coló un color de
# fuera, y nombrarlos como los nombra Catppuccin hace auditable el mapeo de arriba.
CRUST = "#11111b"
MANTLE = "#181825"
BASE = "#1e1e2e"
SURFACE0 = "#313244"
SURFACE1 = "#45475a"
SURFACE2 = "#585b70"
OVERLAY0 = "#6c7086"
OVERLAY1 = "#7f849c"
OVERLAY2 = "#9399b2"
SUBTEXT0 = "#a6adc8"
SUBTEXT1 = "#bac2de"
TEXT = "#cdd6f4"
LAVENDER = "#b4befe"
BLUE = "#89b4fa"
SAPPHIRE = "#74c7ec"
SKY = "#89dceb"
TEAL = "#94e2d5"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
PEACH = "#fab387"
MAROON = "#eba0ac"
RED = "#f38ba8"
MAUVE = "#cba6f7"
PINK = "#f5c2e7"
FLAMINGO = "#f2cdcd"
ROSEWATER = "#f5e0dc"

PALETTE = {
    "crust": CRUST, "mantle": MANTLE, "base": BASE,
    "surface0": SURFACE0, "surface1": SURFACE1, "surface2": SURFACE2,
    "overlay0": OVERLAY0, "overlay1": OVERLAY1, "overlay2": OVERLAY2,
    "subtext0": SUBTEXT0, "subtext1": SUBTEXT1, "text": TEXT,
    "lavender": LAVENDER, "blue": BLUE, "sapphire": SAPPHIRE, "sky": SKY,
    "teal": TEAL, "green": GREEN, "yellow": YELLOW, "peach": PEACH,
    "maroon": MAROON, "red": RED, "mauve": MAUVE, "pink": PINK,
    "flamingo": FLAMINGO, "rosewater": ROSEWATER,
}

MOCHA = Theme(
    name="catppuccin-mocha",
    dark=True,
    background=BASE,
    surface=MANTLE,
    panel=SURFACE0,
    boost=SURFACE0,
    foreground=TEXT,
    primary=BLUE,
    secondary=MAUVE,
    accent=LAVENDER,
    # Las tres semánticas vuelven a tener matiz. En el tema monocromático anterior estaban
    # aplanadas al mismo gris a propósito; aquí cada una dice lo suyo y ninguna se usa para
    # otra cosa.
    success=GREEN,
    warning=YELLOW,
    error=RED,
    variables={
        # `text` es la variable que usa el CSS interno de casi todos los widgets. Textual la
        # define como `auto 87%` —un blanco de contraste rebajado— y ese `auto` gana sobre
        # cualquier `$text:` declarado en la hoja de la app, así que el registro, las listas
        # y el encabezado salían en un gris casi blanco ajeno a la paleta en vez de en el
        # `text` de Catppuccin. Fijarla aquí es lo único que los alcanza.
        "text": TEXT,
        "text-muted-alpha": "1.0",
        # El cursor de bloque invierte: fondo del acento, texto del fondo más hondo. Es la
        # única inversión del panel, y por eso se lee como «esto es lo resaltado».
        "block-cursor-foreground": CRUST,
        "block-cursor-background": LAVENDER,
        "block-cursor-text-style": "none",
        "block-hover-background": SURFACE0,
        # El foco es azul; lo que no lo tiene se queda en el gris de superficie. El
        # contraste entre los dos ES la señal, así que `border-blurred` no puede ser un azul
        # apagado: tiene que ser otro color.
        "border": BLUE,
        "border-blurred": SURFACE1,
        "scrollbar": SURFACE1,
        "scrollbar-hover": SURFACE2,
        "scrollbar-active": LAVENDER,
        "scrollbar-background": MANTLE,
        "scrollbar-background-hover": MANTLE,
        "scrollbar-background-active": MANTLE,
        # El pie es una referencia permanente: la tecla en azul y su descripción en el gris
        # de texto secundario. Sin recuadros invertidos — quince teclas invertidas compiten
        # entre sí y con el panel.
        "footer-key-foreground": BLUE,
        "footer-key-background": SURFACE0,
        "footer-description-foreground": SUBTEXT0,
        "footer-description-background": SURFACE0,
        "footer-item-background": SURFACE0,
        "footer-foreground": SUBTEXT0,
        "footer-background": SURFACE0,
        "input-cursor-background": LAVENDER,
        "input-cursor-foreground": CRUST,
        "input-selection-background": SURFACE1,
        "button-color-foreground": CRUST,
        "link-color": BLUE,
        "link-color-hover": LAVENDER,
        "link-background-hover": SURFACE0,
        "text-primary": TEXT,
        "text-secondary": SUBTEXT0,
        "text-accent": LAVENDER,
        "text-success": GREEN,
        # `text-warning`, no `text-aviso`: el nombre en español no existe en textual, así
        # que la variable se definía y nadie la leía nunca.
        "text-warning": YELLOW,
        "text-error": RED,
        "text-muted": OVERLAY1,
        "text-disabled": OVERLAY0,
    },
)


# La hoja de estilos del panel. Va con el tema porque es la otra mitad de la misma
# decisión: el tema fija los tonos y esto los reparte.
CSS = """
/* Los tonos de Catppuccin Mocha con su nombre propio. Se repiten aquí porque el CSS de
   textual no puede leer las constantes del módulo, y con el nombre original para que
   cualquier regla de abajo se pueda contrastar contra la paleta sin traducir nada. */
$crust: #11111b;
$mantle: #181825;
$base: #1e1e2e;
$surface0: #313244;
$surface1: #45475a;
$surface2: #585b70;
$overlay0: #6c7086;
$overlay1: #7f849c;
$subtext0: #a6adc8;
$text: #cdd6f4;
$lavender: #b4befe;
$blue: #89b4fa;
$green: #a6e3a1;
$yellow: #f9e2af;
$peach: #fab387;
$red: #f38ba8;

$surface: $mantle; $panel: $surface0; $primary: $blue; $accent: $lavender;
$boost: $surface0;

Screen { layout: horizontal; background: $crust; color: $text; }

#side { width: 34%; max-width: 52; min-width: 26; height: 100%; }
#main { width: 1fr; height: 100%; }

#analytics, #metrics-box, #performance { height: 3fr; display: none; }
#analytics.-open, #metrics-box.-open, #performance.-open { display: block; }
#charts, #metrics { width: auto; }
#perf-summary { height: 4; padding: 0 1; }
#perf-rate, #perf-memory { height: 1fr; min-height: 8; }

#stages  { height: 2fr; min-height: 8; }
#books   { height: 1fr; min-height: 5; }
#state   { height: 1fr; min-height: 5; padding: 0 1; overflow-y: auto; }
#log     { height: 1fr; }

/* La elevación, como la usa Catppuccin: `mantle` es la barra lateral y `base` el área de
   trabajo. Aquí eso se traduce a que los controles —etapas, Libros, estado— van hundidos y
   la salida y los apartados, que es lo que se está mirando, van un escalón más arriba. Las
   barras de `surface0` flotan sobre los dos.

   El borde apagado es gris de superficie y no un azul tenue, para que la diferencia con el
   panel enfocado se vea sin tener que comparar. */
#stages, #books, #state, #log, #analytics, #metrics-box, #performance {
    border: round $surface1; color: $text;
}
#stages, #books, #state {
    background: $mantle; scrollbar-background: $mantle; scrollbar-color: $surface1;
}
#log, #analytics, #metrics-box, #performance {
    background: $base; scrollbar-background: $base; scrollbar-color: $surface1;
}
#stages:focus-within, #books:focus-within, #log:focus-within,
#analytics:focus-within, #metrics-box:focus-within,
#performance:focus-within { border: round $blue; }
/* Verde porque significa «esto entra en la corrida», no porque destaque. */
SelectionList > .selection-list--button-selected-highlighted,
SelectionList > .selection-list--button-selected { color: $green; }
OptionList { background: $mantle; color: $text; }
OptionList > .option-list--option-highlighted { background: $surface0; color: $text; }

/* La pista explica; va en el gris de texto secundario, legible pero por debajo del
   contenido. La barra de estado dice qué se va a correr —es la línea más accionable del
   panel— y por eso es la única que va a texto pleno sobre una superficie elevada. */
#hint   { dock: bottom; height: 2; background: $mantle; color: $subtext0; padding: 0 1; }
#status { dock: bottom; height: 1; background: $surface0; color: $text; padding: 0 1; }

Header { background: $surface0; color: $text; }
Header > .header--sub-title { color: $subtext0; }
Footer { background: $surface0; color: $subtext0; }
Footer > .footer-key--key { color: $blue; background: $surface0; }

/* Los modales se centran solos. `Screen` de arriba les impone `layout: horizontal`
   —el selector de tipo alcanza a las subclases—, y sin `align` el cuadro queda
   pegado arriba a la izquierda en vez de al medio.

   El velo sobre `crust` es lo que los hace leer como una capa encima y no como otra
   pantalla: sin él, el fondo opaco borraba el panel y se perdía el sitio donde se estaba. */
ModalScreen { layout: vertical; align: center middle; background: $crust 60%; }

/* Lavanda y no azul: el azul ya significa «aquí está el foco» dentro del panel, y un modal
   no es un panel enfocado — es otra capa. Dos acentos, dos cosas distintas. */
#dialog {
    width: 84%; max-width: 96; height: auto; max-height: 88%;
    border: round $lavender; background: $mantle; color: $text; padding: 1 2;
}
#dialog-text { height: auto; }
#confirm-input {
    border: round $surface2; background: $base; color: $text; margin-top: 1;
}
#confirm-input:focus { border: round $blue; }

/* Pantalla angosta: los paneles dejan de ir al costado y se apilan. Debajo de
   unas 92 columnas, una barra lateral y un registro no caben sin que los dos
   queden ilegibles.

   La barra se acota al 45% del alto y los paneles principales llevan `min-height`.
   MEDIDO: sin la cota, a 85x28 la barra apilada se comía todo y el registro
   quedaba con CERO filas — visible en el layout, inútil en la práctica. */
Screen.-narrow { layout: vertical; }
Screen.-narrow #side {
    width: 100%; max-width: 100%; height: auto; max-height: 45%;
}
Screen.-narrow #main { width: 100%; height: 1fr; min-height: 8; }
Screen.-narrow #stages { height: 7; min-height: 4; }
Screen.-narrow #books  { height: 5; min-height: 3; }
Screen.-narrow #state  { display: none; }
Screen.-narrow #log    { min-height: 4; }
Screen.-narrow #analytics,
Screen.-narrow #metrics-box,
Screen.-narrow #performance { height: 2fr; min-height: 6; }
/* Con un apartado abierto en pantalla angosta, la barra se aparta del todo: quien
   abrió los gráficos está mirando los gráficos, no las casillas. */
Screen.-narrow.-drawer #side { display: none; }
"""
