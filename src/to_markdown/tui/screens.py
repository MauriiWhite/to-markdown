"""Las pantallas modales: confirmar un borrado, elegir qué borrar, y la ayuda.

Van juntas porque son la misma clase de cosa —algo que se abre encima, se contesta y se
cierra— y aparte del panel porque el panel ya tenía mil líneas.
"""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

from ..analytics import human_bytes
from ..infra.cleanup import targets
from .content import HELP


class Confirm(ModalScreen[bool]):
    """Segunda validación: hay que escribir la palabra exacta.

    La primera pregunta se contesta con una tecla, y una tecla se aprieta por reflejo.
    Escribir la palabra obliga a leer qué se está por borrar, que es el punto de tener
    dos pasos y no uno.
    """

    BINDINGS: ClassVar = [Binding("escape", "cancel", "cancelar")]

    def __init__(self, target, word: str) -> None:
        super().__init__()
        self.target = target
        self.word = word

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(
                f"[b]Confirmación final[/b]\n\n"
                f"Se van a borrar [b]{self.target.files()} archivos[/b] "
                f"([b]{human_bytes(self.target.size())}[/b]) de:\n"
                f"  {self.target.label}\n\n"
                f"Cómo se repone:\n  {self.target.rebuild}\n\n"
                + ("[b]Esto no se puede deshacer ni volver a descargar.[/b]\n\n"
                   if self.target.irreversible else "")
                + f"Para confirmar, escribe [b]{self.word}[/b] y pulsa Intro.\n"
                f"Para cancelar, pulsa Esc.",
                id="dialog-text",
            )
            yield Input(placeholder=f"escribe: {self.word}", id="confirm-input")

    def on_mount(self) -> None:
        self.query_one("#confirm-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip().lower() == self.word)

    def action_cancel(self) -> None:
        self.dismiss(False)

class CleanScreen(ModalScreen[str | None]):
    """Primera validación: elegir qué borrar, viendo cuánto pesa y qué cuesta reponerlo."""

    BINDINGS: ClassVar = [
        Binding("escape", "cancel", "volver"),
        Binding("q", "cancel", "volver"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(
                "[b]Borrar contenido descargado[/b]\n\n"
                "Elige qué borrar y pulsa Intro. Después habrá que confirmar una\n"
                "segunda vez escribiendo una palabra. Esc para volver sin borrar.\n\n"
                "La lista va de lo más barato de reponer a lo más caro.",
                id="dialog-text",
            )
            options = []
            for target in targets():
                if not target.exists():
                    continue
                warning = "  ·  NO SE REPONE" if target.irreversible else ""
                options.append(Option(
                    f"{target.label}\n"
                    f"    {human_bytes(target.size())} · {target.files()} archivos{warning}\n"
                    f"    [dim]{target.rebuild}[/dim]",
                    id=target.key,
                ))
            yield OptionList(*options, id="targets")

    def on_mount(self) -> None:
        self.query_one("#targets", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)

    def action_cancel(self) -> None:
        self.dismiss(None)

class HelpScreen(ModalScreen[None]):
    """Ayuda que no da nada por sabido."""

    BINDINGS: ClassVar = [
        Binding("escape", "close", "cerrar"),
        Binding("q", "close", "cerrar"),
        Binding("question_mark", "close", "cerrar"),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog"):
            yield Static(HELP, id="dialog-text")

    def action_close(self) -> None:
        self.dismiss(None)

