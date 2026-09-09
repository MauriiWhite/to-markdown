"""Ejecuta las etapas y entrega su salida línea a línea.

Sin `textual`: quien orqueste el pipeline no tiene por qué depender de la interfaz que lo
muestra. La TUI le pasa un `emit` que escribe en el registro; una prueba le pasa una lista.
"""

from __future__ import annotations

import contextlib
import io
import time

from ..analytics import record_stage
from ..core import Book


class Tee(io.TextIOBase):
    """Recoge lo que las etapas imprimen y lo entrega línea a línea.

    Las etapas usan `print`, que es lo correcto para una herramienta de línea de comandos y
    lo que hace que la CLI y la TUI muestren exactamente lo mismo. Capturarlo, en vez de
    reescribir las etapas para que emitan eventos, evita dos caminos que se desincronicen.
    """

    def __init__(self, emit) -> None:
        self._emit = emit
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._emit(line)
        return len(text)

    def flush(self) -> None:
        if self._buffer:
            self._emit(self._buffer)
            self._buffer = ""


def run_stages(stages: list[str], books: list[Book], emit) -> bool:
    """Corre las etapas en orden, emitiendo cada línea. Devuelve si terminó bien.

    Un `SystemExit` de `guard` o de la verificación del PDF es una parada **deliberada**, no
    un fallo del programa: se atrapa y se muestra. El caso que el proyecto entero está
    construido para detectar no puede terminar en una pantalla en blanco.
    """
    from ..stages import STAGES

    tee = Tee(emit)
    for name in stages:
        emit(f"[b]── {name} ─────────────────────────[/b]")
        started = time.perf_counter()
        try:
            with contextlib.redirect_stdout(tee):
                STAGES[name](books)
            tee.flush()
            record_stage(name, books, time.perf_counter() - started, ok=True)
        except SystemExit as stop:
            tee.flush()
            record_stage(name, books, time.perf_counter() - started, ok=False)
            emit("")
            for line in str(stop).splitlines():
                emit(f"[b]{line}[/b]" if line.strip() else "")
            emit(f"[b]Se detuvo en «{name}». No se escribió nada.[/b]")
            return False
        except Exception as exc:  # noqa: BLE001 — la TUI no puede morirse con la etapa
            tee.flush()
            record_stage(name, books, time.perf_counter() - started, ok=False)
            emit(f"[b]Error en «{name}» — {type(exc).__name__}: {exc}[/b]")
            return False
        emit(f"[dim]{name} terminó en {time.perf_counter() - started:.1f} s[/dim]")
    return True


# Tono de las líneas: plotext trae su propia paleta y es de colores, así que se le pasa
# el tono a mano en cada trazo.
