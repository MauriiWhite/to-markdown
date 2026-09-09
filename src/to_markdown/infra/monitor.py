"""Contadores del proceso en vivo: qué está haciendo el pipeline mientras corre.

Esto NO mide el Compendio, mide el programa. Es la diferencia entre "cuántas normas hay"
—que se responde leyendo `data/`— y "a qué ritmo las está trayendo ahora mismo", que solo
se puede responder muestreando mientras corre.

Los contadores son de módulo y se incrementan desde las etapas. Es deliberado que sean
globales y no un objeto que haya que pasar: instrumentar el pipeline no puede obligar a
cambiar la firma de cada función, o la instrumentación termina donde termina la paciencia.

Todo es de la biblioteca estándar. Un medidor de rendimiento que necesita instalar algo es
un medidor que no se usa.
"""

from __future__ import annotations

import os
import resource
import threading
import time
from dataclasses import dataclass, field

# Los contadores viven en un solo diccionario y se tocan bajo lock: las etapas de red
# corren en varios hilos y un `+=` sobre un entero no es atómico en todos los casos.
_LOCK = threading.Lock()
_COUNTERS: dict[str, float] = {}
_STARTED = time.perf_counter()
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096


def bump(name: str, amount: float = 1) -> None:
    """Suma al contador. Es lo único que las etapas necesitan saber de este módulo."""
    with _LOCK:
        _COUNTERS[name] = _COUNTERS.get(name, 0) + amount


def counters() -> dict[str, float]:
    with _LOCK:
        return dict(_COUNTERS)


def reset() -> None:
    """Pone los contadores a cero. Se llama al empezar una corrida, no al importar: el
    módulo puede haberse cargado mucho antes de que alguien pulse una tecla."""
    global _STARTED
    with _LOCK:
        _COUNTERS.clear()
    _STARTED = time.perf_counter()


def rss_bytes() -> int:
    """Memoria residente del proceso.

    `/proc/self/statm` es exacto y cuesta una lectura; `getrusage` es el respaldo portable,
    pero devuelve el MÁXIMO histórico y no el actual, así que solo sirve para no quedarse
    sin dato en un sistema donde no haya `/proc`.
    """
    try:
        with open("/proc/self/statm", encoding="ascii") as fh:
            return int(fh.read().split()[1]) * PAGE_SIZE
    except (OSError, IndexError, ValueError):
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def cpu_seconds() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


@dataclass
class Sample:
    """Una foto del proceso. Los ritmos se calculan contra la foto anterior, no se guardan:
    guardarlos obligaría a que quien muestrea lo hiciera a un intervalo fijo."""

    at: float
    elapsed: float
    rss: int
    cpu: float
    counters: dict[str, float] = field(default_factory=dict)


@dataclass
class Monitor:
    """Serie de muestras con los ritmos ya derivados.

    Guarda una ventana acotada: un gráfico de línea en una terminal no puede mostrar más
    puntos que columnas tiene, y una corrida larga llenaría la memoria con datos que nadie
    va a ver.
    """

    window: int = 600
    samples: list[Sample] = field(default_factory=list)

    def take(self) -> Sample:
        sample = Sample(
            at=time.time(),
            elapsed=time.perf_counter() - _STARTED,
            rss=rss_bytes(),
            cpu=cpu_seconds(),
            counters=counters(),
        )
        self.samples.append(sample)
        del self.samples[: max(0, len(self.samples) - self.window)]
        return sample

    def clear(self) -> None:
        self.samples.clear()

    def series(self, name: str) -> list[float]:
        """El valor acumulado de un contador, muestra a muestra."""
        return [s.counters.get(name, 0.0) for s in self.samples]

    def rate(self, name: str) -> list[float]:
        """El ritmo por segundo entre muestras consecutivas.

        Es lo que responde "¿a qué velocidad va ahora?", que el acumulado no puede: una
        curva acumulada siempre sube, y sube igual de bonito cuando el ritmo se derrumbó.
        """
        out: list[float] = []
        for previous, current in zip(self.samples, self.samples[1:], strict=False):
            span = current.elapsed - previous.elapsed
            delta = current.counters.get(name, 0.0) - previous.counters.get(name, 0.0)
            out.append(delta / span if span > 0 else 0.0)
        return out

    def cpu_percent(self) -> list[float]:
        out: list[float] = []
        for previous, current in zip(self.samples, self.samples[1:], strict=False):
            span = current.elapsed - previous.elapsed
            out.append((current.cpu - previous.cpu) / span * 100 if span > 0 else 0.0)
        return out

    def memory_mb(self) -> list[float]:
        return [s.rss / 1e6 for s in self.samples]

    def timeline(self) -> list[float]:
        return [s.elapsed for s in self.samples]

    def summary(self) -> dict:
        """Los números que acompañan a los gráficos. Sin ellos, una curva sin escala no
        dice si el pico fueron 3 peticiones por segundo o 300."""
        if not self.samples:
            return {}
        last = self.samples[-1]
        rates = self.rate("requests")
        return {
            "elapsed": last.elapsed,
            "rss_mb": last.rss / 1e6,
            "peak_rss_mb": max(s.rss for s in self.samples) / 1e6,
            "cpu_percent": self.cpu_percent()[-1] if len(self.samples) > 1 else 0.0,
            "requests": last.counters.get("requests", 0),
            "bytes": last.counters.get("bytes", 0),
            "documents": last.counters.get("documents", 0),
            "images": last.counters.get("images", 0),
            "requests_per_second": rates[-1] if rates else 0.0,
            "peak_requests_per_second": max(rates) if rates else 0.0,
            "samples": len(self.samples),
        }
