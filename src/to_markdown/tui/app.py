"""El panel de control: los tres paneles fijos, los tres apartados y las teclas.

Todo lo que no es "cómo se ve" vive fuera: los textos de las etapas en `constants`, el
contenido de los paneles en `panels`, la ejecución de las etapas en `runner`, los tonos en
`theme` y los modales en `screens`. Aquí queda el armado y el comportamiento.
"""

from __future__ import annotations

import time
from typing import ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Header, RichLog, SelectionList, Static
from textual.widgets.selection_list import Selection
from textual_plotext import PlotextPlot

from ..analytics import human_bytes
from ..core import BOOKS, Book
from ..infra.cleanup import by_key, purge, targets
from ..infra.monitor import Monitor
from ..infra.monitor import reset as reset_counters
from .content import (
    ANALYTICS,
    DEFAULT_STAGES,
    DRAWERS,
    METRICS,
    NEEDS_NETWORK,
    PANELS,
    PERFORMANCE,
    REFRESH_STAGES,
    SAMPLE_SECONDS,
    STAGE_HELP,
    STAGE_WRITES,
    corpus_state,
    state_lines,
)
from .drawers import DrawerMixin
from .runner import run_stages
from .screens import CleanScreen, Confirm, HelpScreen
from .theme import CSS as DASHBOARD_CSS
from .theme import MOCHA


class Panel(SelectionList[str]):
    """Los dos paneles marcables.

    `OptionList` —de quien `SelectionList` hereda— liga Intro a «seleccionar». Con el foco
    en un panel, que es donde arranca y donde se pasa el tiempo, Intro desmarcaba en
    silencio la fila resaltada en vez de correr lo marcado, que es lo que anuncian la ayuda
    y el pie. Aquí Intro vuelve a ser de la app; para marcar está la barra espaciadora.
    """

    BINDINGS: ClassVar = [Binding("enter", "app.run", "correr lo marcado", show=False)]


class Dashboard(DrawerMixin, App):
    """Panel de control del pipeline."""

    # La hoja de estilos vive en `theme`, junto a los tonos que reparte.
    CSS = DASHBOARD_CSS

    HORIZONTAL_BREAKPOINTS: ClassVar = [(0, "-narrow"), (92, "-normal")]

    BINDINGS: ClassVar = [
        # `priority` es necesario: sin él, el Tab interno de textual (mover el foco al
        # siguiente widget) gana y el panel nunca rota. Con él, en cambio, Tab llega aquí
        # incluso con un modal encima — por eso las acciones se lo devuelven al modal.
        Binding("tab", "next_panel", "cambiar de panel", priority=True),
        Binding("shift+tab", "previous_panel", "panel anterior", priority=True),
        Binding("space", "toggle", "marcar"),
        Binding("enter", "run", "correr lo marcado"),
        Binding("a", "run_all", "correr todo"),
        Binding("r", "run_refresh", "actualizar"),
        Binding("d", "reset", "restablecer"),
        Binding("m", "metrics", "métricas"),
        Binding("g", "charts", "gráficos"),
        Binding("p", "performance", "rendimiento"),
        Binding("D", "purge", "borrar datos"),
        Binding("x", "stop", "parar"),
        Binding("c", "clear_log", "limpiar registro"),
        Binding("question_mark", "help", "ayuda"),
        Binding("q", "quit", "salir"),
    ]

    def __init__(self, preselect: list[str] | None = None) -> None:
        super().__init__()
        self.preselect = preselect or [b.slug for b in BOOKS]
        self.running = False
        self.status_text = ""
        self.panel = 0
        self.monitor = Monitor()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="side"):
            yield Panel(
                *[Selection(f"{n:8} {STAGE_HELP[n]}", n, n in DEFAULT_STAGES)
                  for n in STAGE_HELP],
                id="stages",
            )
            yield Panel(
                *[Selection(f"{b.slug:9} {b.name}", b.slug, b.slug in self.preselect)
                  for b in BOOKS],
                id="books",
            )
            yield Static(id="state")
        with Vertical(id="main"):
            # El apartado de gráficos vive aquí y no en una pantalla aparte: se abre y
            # se cierra con la misma tecla sin tapar el registro ni perder el sitio, y
            # no hay pestañas que recorrer — el informe entero va en un solo
            # desplazamiento, de lo temporal a lo estructural.
            # Tres apartados distintos, no tres pestañas del mismo: responden
            # preguntas distintas y se abren por separado.
            #   `m` métricas    — los números del corpus
            #   `g` gráficos    — cómo cambia el corpus en el tiempo
            #   `p` rendimiento — cómo va el PROGRAMA ahora mismo
            yield VerticalScroll(Static(id="metrics"), id="metrics-box")
            yield VerticalScroll(Static(id="charts"), id="analytics")
            # `VerticalScroll` y no `Vertical`: es enfocable —hace falta para que
            # entre en la rotación de Tab— y en una terminal baja las dos gráficas se
            # pueden recorrer en vez de quedar aplastadas.
            with VerticalScroll(id="performance"):
                yield Static(id="perf-summary")
                yield PlotextPlot(id="perf-rate")
                yield PlotextPlot(id="perf-memory")
            # `wrap=False` a propósito: la salida de las etapas es tabular, y con
            # ajuste de línea las columnas dejan de alinearse. Se desplaza en
            # horizontal con las flechas, como en lazygit.
            yield RichLog(id="log", markup=True, wrap=False, highlight=False,
                          auto_scroll=True, max_lines=20000)
        yield Static(id="hint")
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.register_theme(MOCHA)
        self.theme = MOCHA.name
        self.title = "to-markdown"
        self.sub_title = "Compendio de Normas del Sistema de Pensiones · SP Chile"
        self.query_one("#stages", SelectionList).border_title = (
            "1 · Etapas — espacio marca o desmarca"
        )
        self.query_one("#books", SelectionList).border_title = "2 · Libros"
        self.query_one("#state", Static).border_title = "Estado del corpus"
        self.query_one("#log", RichLog).border_title = "3 · Salida"
        self.query_one(ANALYTICS).border_title = "Gráficos — «g» abre y cierra"
        self.query_one(METRICS).border_title = "Métricas — «m» abre y cierra"
        self.query_one(PERFORMANCE).border_title = (
            "Rendimiento del programa — «p» abre y cierra"
        )
        # El muestreo corre siempre, no solo con el apartado abierto: si empezara al
        # abrirlo, la curva arrancaría a mitad de la corrida.
        self.set_interval(SAMPLE_SECONDS, self._sample)
        self.query_one("#stages", SelectionList).focus()
        self.refresh_state()
        self.update_hint()
        self.write("[b]Bienvenido.[/b]")
        self.write("")
        self.write("Este panel descarga el Compendio de Normas del sitio de la")
        self.write("Superintendencia de Pensiones y lo convierte a Markdown.")
        self.write("")
        self.write("  · [b]a[/b] hace todo el proceso de principio a fin.")
        self.write("  · [b]Tab[/b] cambia de panel, [b]espacio[/b] marca, "
                   "[b]Intro[/b] corre lo marcado.")
        self.write("  · [b]g[/b] abre y cierra los gráficos de tendencia.")
        self.write("  · [b]?[/b] abre la ayuda completa.")
        self.write("")

    # -- estado ---------------------------------------------------------
    def refresh_state(self) -> None:
        """El estado del corpus, adaptado al ancho que tenga el panel."""
        panel = self.query_one("#state", Static)
        panel.update("\n".join(state_lines(corpus_state()["books"], panel.size.width or 30)))

    def selected(self, widget: str) -> list[str]:
        return list(self.query_one(f"#{widget}", SelectionList).selected)

    def update_hint(self) -> None:
        """La línea que explica, en palabras, qué hace lo que está resaltado.

        Va encolada, no inmediata: `Widget.focus()` no mueve el foco en el acto, lo encola
        con `call_later`. Leer `self.focused` en la misma vuelta devolvía el panel ANTERIOR,
        así que la pista describía el panel que acababas de dejar —y al arrancar, con el
        foco todavía en nadie, describía el registro. `call_later` entra detrás del cambio
        de foco en la misma cola, así que lee el panel que corresponde.
        """
        self.call_later(self._draw_hint)

    def _draw_hint(self) -> None:
        focused = self.focused
        if isinstance(focused, SelectionList) and focused.id == "stages":
            try:
                name = focused.get_option_at_index(focused.highlighted or 0).value
            except Exception:  # noqa: BLE001 - lista vacía o sin resaltado
                return
            network = " · necesita conexión a internet" if name in NEEDS_NETWORK else ""
            self.query_one("#hint", Static).update(
                f"[b]{name}[/b]: {STAGE_HELP[name]}{network}\nEscribe en: {STAGE_WRITES[name]}"
            )
        elif isinstance(focused, SelectionList) and focused.id == "books":
            self.query_one("#hint", Static).update(
                "Los cinco Libros del Compendio. Marca solo los que quieras procesar.\n"
                "Desmarcar uno lo deja intacto: no se borra nada."
            )
        elif focused is not None and focused.id == "analytics":
            self.query_one("#hint", Static).update(
                "Gráficos de tendencia del Compendio: cómo cambia la norma en el "
                "tiempo.\nFlechas o rueda para recorrerlos · «g» los cierra."
            )
        elif focused is not None and focused.id == "metrics-box":
            self.query_one("#hint", Static).update(
                "Los números del corpus, sin gráficos.\n«m» los cierra."
            )
        elif focused is not None and focused.id == "performance":
            self.query_one("#hint", Static).update(
                "Rendimiento del PROGRAMA, en vivo: a qué ritmo va y cuánta memoria "
                "usa.\nSe actualiza solo mientras corre · «p» lo cierra."
            )
        else:
            self.query_one("#hint", Static).update(
                "Salida de las etapas. Flechas para desplazarte, «c» para limpiarla.\n"
                "Tab vuelve al primer panel."
            )

    def update_status(self, message: str = "") -> None:
        if message:
            self.status_text = message
            self.query_one("#status", Static).update(message)
            return
        stages = [s for s in STAGE_HELP if s in self.selected("stages")]
        books = self.selected("books")
        if not stages or not books:
            self.status_text = "nada marcado"
            self.query_one("#status", Static).update(
                "Nada marcado — usa espacio para marcar al menos una etapa y un Libro"
            )
            return
        flags = "" if len(books) == len(BOOKS) else "".join(f" -b {b}" for b in books)
        self.status_text = f"listo · python -m to_markdown {' '.join(stages)}{flags}"
        self.query_one("#status", Static).update(
            f"Intro corre esto → python -m to_markdown {' '.join(stages)}{flags}"
        )

    def write(self, line: str) -> None:
        self.query_one("#log", RichLog).write(line)

    # -- navegación entre paneles ---------------------------------------
    def _delegate(self, action: str) -> bool:
        """Le devuelve la tecla al modal que esté encima, si sabe qué hacer con ella.

        Los bindings con `priority` de la app se disparan antes que los de la pantalla
        activa. Para Tab eso es justo lo que se quiere en el panel principal y justo lo
        que no se quiere dentro de los gráficos, donde Tab cambia de gráfico.
        """
        screen = self.screen
        if screen is not self.screen_stack[0] and hasattr(screen, action):
            getattr(screen, action)()
            return True
        return False

    def _panels(self) -> tuple[str, ...]:
        """Los paneles por los que rota Tab. El de gráficos solo cuenta si está
        abierto: rotar hacia un panel invisible deja el foco en ninguna parte."""
        open_drawers = [d for d in DRAWERS if self.query_one(d).has_class("-open")]
        return (*PANELS[:2], *open_drawers, PANELS[2])

    def _focus_panel(self, index: int) -> None:
        panels = self._panels()
        self.panel = index % len(panels)
        self.query_one(panels[self.panel]).focus()
        self.update_hint()

    def action_next_panel(self) -> None:
        if not self._delegate("action_next"):
            self._focus_panel(self.panel + 1)

    def action_previous_panel(self) -> None:
        if not self._delegate("action_previous"):
            self._focus_panel(self.panel - 1)

    # -- acciones -------------------------------------------------------
    def on_selection_list_selected_changed(self, _) -> None:
        self.update_status()

    def on_selection_list_selection_highlighted(self, _) -> None:
        self.update_hint()

    def action_toggle(self) -> None:
        focused = self.focused
        if isinstance(focused, SelectionList):
            focused.toggle_highlighted_selection()

    def action_reset(self) -> None:
        stages = self.query_one("#stages", SelectionList)
        stages.deselect_all()
        for name in DEFAULT_STAGES:
            stages.select(name)
        # La selección inicial de Libros es la que se pidió al abrir (`tui -b book-iii`),
        # no siempre los cinco: `d` restablece, no amplía.
        books = self.query_one("#books", SelectionList)
        books.deselect_all()
        for slug in self.preselect:
            books.select(slug)
        self.update_status()

    def action_run(self) -> None:
        self.launch([s for s in STAGE_HELP if s in self.selected("stages")])

    def action_run_all(self) -> None:
        self.launch(list(DEFAULT_STAGES))

    def action_run_refresh(self) -> None:
        self.launch(list(REFRESH_STAGES))

    def action_clear_log(self) -> None:
        self.query_one("#log", RichLog).clear()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_purge(self) -> None:
        if self.running:
            self.write("Hay una corrida en curso. Pulsa «x» para pararla antes de borrar.")
            return
        # `CleanScreen` esconde los objetivos que no existen, así que sin nada descargado
        # se abría un modal que decía «elige qué borrar» con la lista vacía y sin nada que
        # elegir. Se responde en el registro y no se abre nada.
        if not any(target.exists() for target in targets()):
            self.write("No hay nada descargado que borrar.")
            return
        self.push_screen(CleanScreen(), self._chose_target)

    def _chose_target(self, key: str | None) -> None:
        if not key:
            return
        target = by_key(key)
        # La palabra es distinta según el riesgo: lo que no se repone exige escribir
        # algo que nadie teclea por inercia.
        word = "no se repone" if target.irreversible else "borrar"
        self.push_screen(
            Confirm(target, word),
            lambda ok, t=target: self._purge(t) if ok else self.write(
                f"No se borró nada ({t.label})."
            ),
        )

    def _purge(self, target) -> None:
        files, size = purge(target)
        self.write(f"[b]Borrado:[/b] {target.label} — {files} archivos, "
                   f"{human_bytes(size)}.")
        self.write(f"Para reponerlo: {target.rebuild}")
        self.refresh_state()
        self.update_status()

    # -- corrida --------------------------------------------------------
    def launch(self, stages: list[str]) -> None:
        if self.running:
            self.write("Ya hay una corrida en curso. Pulsa «x» para pararla.")
            return
        slugs = self.selected("books")
        if not stages or not slugs:
            self.write("Marca al menos una etapa y un Libro (con la barra espaciadora).")
            return
        books = [b for b in BOOKS if b.slug in slugs]
        # Los contadores se ponen a cero por corrida: un ritmo acumulado desde que se
        # abrió el panel mezcla la corrida de hace media hora con la de ahora.
        reset_counters()
        self.monitor.clear()
        self.running = True
        network = " · descargando de internet" if set(stages) & NEEDS_NETWORK else ""
        self.update_status(f"Corriendo: {' '.join(stages)}{network}…")
        self.run_pipeline(stages, books)

    @work(thread=True, exclusive=True)
    def run_pipeline(self, stages: list[str], books: list[Book]) -> None:
        """Las etapas bloquean; van a un hilo para que la TUI siga respondiendo."""
        started = time.perf_counter()

        def emit(line: str) -> None:
            self.call_from_thread(self.write, line)

        ok = run_stages(stages, books, emit)
        self.call_from_thread(self.finished, ok, time.perf_counter() - started)

    def finished(self, ok: bool, elapsed: float) -> None:
        self.running = False
        self.write(
            f"[b]Listo en {elapsed:.1f} s.[/b]" if ok
            else "[b]Se detuvo. Nada quedó a medias en el disco.[/b]"
        )
        self.write("")
        self.refresh_state()
        self.redraw_drawers()
        self.update_status(
            f"{'Terminado' if ok else 'DETENIDO'} en {elapsed:.1f} s · "
            f"«g» ver gráficos · «?» ayuda · «q» salir"
        )
