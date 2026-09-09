"""Los tres apartados —métricas, gráficos y rendimiento— y su dibujado.

Va como mixin y no dentro del panel porque es una responsabilidad entera y separable: abrir
y cerrar cajones, decidir cuál está visible, y redibujar su contenido para el ancho que
tengan ahora. El panel se ocupa de lo demás.

Los tres se excluyen entre sí: tres abiertos a la vez dejan a cada uno con un tercio del
alto, que es menos de lo que cualquiera necesita.
"""

from __future__ import annotations

from textual.widgets import Static
from textual_plotext import PlotextPlot

from ..analytics import metrics_report, report, snapshot
from .content import ANALYTICS, DRAWERS, METRICS, PERFORMANCE, TONE_LINE, performance_lines


class DrawerMixin:
    """Abrir, cerrar y redibujar los apartados. Lo mezcla `Dashboard`."""

    def _toggle_drawer(self, selector: str) -> bool:
        """Abre o cierra un apartado. La misma tecla en los dos sentidos: es lo que lo
        hace rápido de consultar y de sacar del medio.

        Abrir uno cierra los otros dos. Tres apartados abiertos a la vez dejan a cada
        uno con un tercio del alto, que es menos de lo que cualquiera necesita.
        """
        box = self.query_one(selector)
        opening = not box.has_class("-open")
        for other in DRAWERS:
            self.query_one(other).set_class(other == selector and opening, "-open")
        self.screen.set_class(opening, "-drawer")
        if opening:
            self.redraw_drawers()
            box.focus()
            self.panel = self._panels().index(selector)
        else:
            self._focus_panel(0)
        self.update_hint()
        return opening

    def action_charts(self) -> None:
        self._toggle_drawer(ANALYTICS)

    def action_metrics(self) -> None:
        self._toggle_drawer(METRICS)

    def action_performance(self) -> None:
        self._toggle_drawer(PERFORMANCE)

    def redraw_drawers(self) -> None:
        """Redibuja el apartado que esté abierto, para el ancho que haya ahora."""
        if self.query_one(ANALYTICS).has_class("-open"):
            width = max(28, self.query_one(ANALYTICS).size.width - 4)
            self.query_one("#charts", Static).update(
                "\n".join(report(snapshot(), width))
            )
        if self.query_one(METRICS).has_class("-open"):
            width = max(28, self.query_one(METRICS).size.width - 4)
            self.query_one("#metrics", Static).update(
                "\n".join(metrics_report(snapshot(), width))
            )
        if self.query_one(PERFORMANCE).has_class("-open"):
            self.draw_performance()

    # -- rendimiento en vivo --------------------------------------------
    def draw_performance(self) -> None:
        """Dibuja las dos líneas del apartado de rendimiento.

        Son líneas y no barras porque la pregunta es "¿cómo viene evolucionando?", y
        una serie temporal con decenas de puntos en barras no se lee. Los colores se
        fijan a mano desde la paleta: plotext trae los suyos y son de colores.
        """
        if not self.query_one(PERFORMANCE).has_class("-open"):
            return
        summary = self.monitor.summary()
        self.query_one("#perf-summary", Static).update(
            "\n".join(performance_lines(summary, self.running))
        )
        timeline = self.monitor.timeline()
        for widget_id, series, title, label in (
            ("#perf-rate", self.monitor.rate("requests"),
             "Peticiones por segundo", "pet/s"),
            ("#perf-memory", self.monitor.memory_mb(), "Memoria del proceso", "MB"),
        ):
            widget = self.query_one(widget_id, PlotextPlot)
            plt = widget.plt
            plt.clear_data()
            plt.theme("clear")
            plt.title(title)
            plt.xlabel("segundos")
            plt.ylabel(label)
            if len(series) >= 2:
                axis = timeline[-len(series):]
                plt.plot(axis, series, color=TONE_LINE, marker="braille")
            widget.refresh()

    def _sample(self) -> None:
        """Toma una muestra del proceso. Corre siempre, no solo con el apartado
        abierto: si solo muestreara mientras se mira, la curva empezaría en el momento
        de abrirlo y no en el de arrancar la corrida."""
        self.monitor.take()
        self.draw_performance()

    def on_resize(self) -> None:
        # Todo lo que se dibuja para un ancho se vuelve a dibujar al cambiarlo: los
        # gráficos, y la tabla de estado, que elige sus columnas según lo que quepa.
        self.redraw_drawers()
        self.refresh_state()

    def action_stop(self) -> None:
        if self.running:
            self.workers.cancel_all()
            self.running = False
            self.write("[b]Cancelado.[/b] La etapa en curso termina sola; "
                       "ninguna deja el disco a medias.")
            self.update_status()

    # -- borrado, con dos validaciones ----------------------------------
