"""La configuración y las rutas del proyecto.

Un solo archivo lee `config.toml` y decide dónde vive cada cosa. Todo lo demás importa de
aquí: si mañana la configuración viniera de otro lado, este es el único archivo que cambia.
"""

from __future__ import annotations

import tomllib
from pathlib import Path


def _find_root(start: Path) -> Path:
    """La raíz del proyecto: el primer directorio hacia arriba con `config.toml`.

    Se busca en vez de contar niveles porque contar los ata a la profundidad del archivo:
    este módulo ya se movió una vez y `parents[2]` dejó de apuntar a la raíz sin que nada
    lo dijera hasta que el pipeline no arrancó.
    """
    for folder in (start, *start.parents):
        if (folder / "config.toml").exists():
            return folder
    raise SystemExit(f"no se encontró `config.toml` subiendo desde {start}")


ROOT = _find_root(Path(__file__).resolve().parent)

with (ROOT / "config.toml").open("rb") as fh:
    CONFIG = tomllib.load(fh)

DATA = ROOT / CONFIG["paths"]["data"]
ASSETS = ROOT / CONFIG["paths"]["assets"]

# `data/` se parte primero por FUENTE y después por Libro. Son dos cosas distintas y no
# comparables campo a campo: `web/` es lo que la SP publica en su portal, capítulo por
# capítulo, y es lo que el pipeline extrae; `pdf/` es el compendio que la propia SP exporta
# como documento único. Mezclarlos en una carpeta haría imposible responder la pregunta que
# motiva tenerlos juntos: qué trae uno que el otro no.
WEB = DATA / "web"
PDF = DATA / "pdf"

# `output/` es lo único que se entrega: los Markdown ya listos más sus índices.
# Va fuera de `data/` a propósito — `data/` es el área de trabajo del pipeline,
# con caché, estado y artefactos intermedios que nadie externo necesita ver.
OUTPUT = ROOT / CONFIG["paths"]["output"]
