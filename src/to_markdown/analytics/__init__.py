"""Métricas del pipeline y los gráficos de texto con que se muestran.

Va aparte de la TUI a propósito: son funciones puras sobre lo que ya está en disco, así que
se pueden probar sin levantar una interfaz y se pueden reusar desde un informe. La TUI solo
las dibuja.

Este módulo es la fachada. Dentro:

  `format`        primitivas de dibujo — barras, líneas de tendencia, números
  `sources`       las series con fecha: duración de etapas y actividad normativa
  `metrics`       lo que hay en disco, leído sin recalcular nada
  `charts_state`  gráficos del estado actual (una foto)
  `charts_trend`  gráficos de tendencia (cómo cambia en el tiempo)
  `charts`        el informe: qué secciones y en qué orden
"""

from __future__ import annotations

from .charts import CHARTS, SECTIONS, metrics_report, report
from .charts_state import coverage_chart, download_chart, processing_chart
from .charts_trend import amendment_chart, run_history_chart, timing_chart
from .format import (
    BRAILLE,
    DENSITY,
    EIGHTHS,
    bar,
    es,
    human_bytes,
    rows_chart,
    sparkline,
    timeline,
)
from .metrics import (
    coverage_metrics,
    download_metrics,
    history,
    processing_metrics,
    snapshot,
)
from .sources import (
    AMENDMENT_DATE,
    NCG_NUMBER,
    TIMINGS,
    YEAR_RANGE,
    amendment_activity,
    record_stage,
    stage_timings,
)

# `history_chart` era el nombre anterior de la serie de corridas; se conserva porque el
# informe y las pruebas lo nombran así.
history_chart = run_history_chart

__all__ = [
    "AMENDMENT_DATE",
    "BRAILLE",
    "CHARTS",
    "DENSITY",
    "EIGHTHS",
    "NCG_NUMBER",
    "SECTIONS",
    "TIMINGS",
    "YEAR_RANGE",
    "amendment_activity",
    "amendment_chart",
    "bar",
    "coverage_chart",
    "coverage_metrics",
    "download_chart",
    "download_metrics",
    "es",
    "history",
    "history_chart",
    "human_bytes",
    "metrics_report",
    "processing_chart",
    "processing_metrics",
    "record_stage",
    "report",
    "rows_chart",
    "run_history_chart",
    "snapshot",
    "sparkline",
    "stage_timings",
    "timeline",
    "timing_chart",
]
