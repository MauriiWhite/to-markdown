"""Lo que habla con el mundo exterior: la red, el proceso y el disco de trabajo.

Separado del dominio y de las etapas porque es la capa que se puede sustituir sin que nada
más se entere, y la que hay que instrumentar cuando algo va lento o falla.

  `net`      transporte HTTP: conexiones vivas, gzip, redirecciones, reintentos
  `monitor`  contadores del proceso en vivo, para medir el rendimiento
  `cleanup`  qué se puede borrar del contenido descargado y cómo se repone
"""

from __future__ import annotations

from .monitor import Monitor, Sample, bump, counters, reset
from .net import BASE, close_connections, get_bytes, load_http, request, save_http

__all__ = [
    "BASE",
    "Monitor",
    "Sample",
    "bump",
    "close_connections",
    "counters",
    "get_bytes",
    "load_http",
    "request",
    "reset",
    "save_http",
]
