"""El informe: qué secciones lo componen y en qué orden.

Las secciones temporales van primero porque son lo que una foto no puede contar. El
informe entero se recorre en un solo desplazamiento: no hay pestañas.
"""

from __future__ import annotations

from .charts_state import coverage_chart, download_chart, processing_chart
from .charts_trend import amendment_chart, run_history_chart, timing_chart
from .format import es, human_bytes


def metrics_report(snap: dict, width: int) -> list[str]:
    """Los NÚMEROS, sin gráficos. Es el apartado que responde "cuánto hay" de un vistazo,
    sin tener que leer una barra contra una escala."""
    lines: list[str] = ["[b]Métricas del corpus[/b]", ""]
    cols = ("Libro", "Normas", "Números", "Figuras", "Notas", "Títulos", "md", "Texto")
    widths = (9, 7, 8, 8, 6, 8, 4, 9)
    lines.append(" ".join(c.rjust(w) if i else c.ljust(w)
                          for i, (c, w) in enumerate(zip(cols, widths, strict=True))))
    lines.append("[dim]" + "─" * min(width, sum(widths) + len(widths) - 1) + "[/dim]")
    totals = dict.fromkeys(("documents", "units", "figures", "notes", "sections",
                            "delivered", "chars"), 0)
    for row in snap["processing"]:
        for key in totals:
            totals[key] += row[key]
        lines.append(
            f"{row['slug']:<9} {row['documents']:>7} {es(row['units']):>8} "
            f"{es(row['figures']):>8} {es(row['notes']):>6} {row['sections']:>8} "
            f"{row['delivered']:>4} {row['chars'] / 1e6:>7.2f} MB"
        )
    lines.append("[dim]" + "─" * min(width, sum(widths) + len(widths) - 1) + "[/dim]")
    lines.append(
        f"{'TOTAL':<9} {totals['documents']:>7} {es(totals['units']):>8} "
        f"{es(totals['figures']):>8} {es(totals['notes']):>6} {totals['sections']:>8} "
        f"{totals['delivered']:>4} {totals['chars'] / 1e6:>7.2f} MB"
    )

    ready = [c for c in snap["coverage"] if c.get("ready")]
    if ready:
        aligned = sum(c["aligned"] for c in ready)
        documents = sum(c["documents"] for c in ready) or 1
        extra = sum(c["extra_words"] for c in ready)
        pages = sum(c["pdf_pages"] for c in ready)
        shared = sum(c["figures_shared"] for c in ready)
        lines += [
            "", "[b]Contraste contra el PDF oficial[/b]", "",
            f"  capítulos alineados      {aligned}/{documents}  ({aligned / documents:.1%})",
            f"  páginas de PDF leídas    {es(pages)}",
            f"  texto solo en el PDF     {es(extra)} palabras",
            f"  figuras en ambos lados   {es(shared)}",
        ]

    download = snap["download"]
    weight = sum(d["cache_bytes"] + d["image_bytes"] + d["pdf_bytes"] for d in download)
    tracked = sum(d["tracked"] for d in download)
    revalidable = sum(d["revalidable"] for d in download)
    lines += [
        "", "[b]En disco[/b]", "",
        f"  páginas en caché         {es(sum(d['pages'] for d in download))}",
        f"  figuras descargadas      {es(sum(d['images'] for d in download))}",
        f"  peso total               {human_bytes(weight)}",
        (f"  revalidables con ETag    {revalidable}/{tracked}" if tracked
         else "  revalidables con ETag    (sin índice HTTP todavía)"),
    ]
    activity = snap["amendments"]
    if activity["years"]:
        lines += [
            "", "[b]Actividad normativa[/b]", "",
            f"  modificaciones fechadas  {es(sum(activity['years'].values()))}",
            f"  período                  {min(activity['years'])}–{max(activity['years'])}",
            f"  NCG distintas citadas    {es(len(activity['ncg']))}",
        ]
    return lines


# El informe completo, apilado en un solo desplazamiento. Va primero lo que cambia en el
# tiempo —que es lo que una foto no puede contar— y después el estado actual.
SECTIONS = (
    amendment_chart,
    timing_chart,
    run_history_chart,
    coverage_chart,
    processing_chart,
    download_chart,
)


def report(snap: dict, width: int) -> list[str]:
    """Todas las secciones, una debajo de otra, separadas por una regla."""
    out: list[str] = []
    for index, section in enumerate(SECTIONS):
        if index:
            out += ["", "[dim]" + "─" * max(8, width) + "[/dim]", ""]
        out += section(snap, width)
    return out


CHARTS = {
    "actividad": amendment_chart,
    "duración": timing_chart,
    "historial": run_history_chart,
    "cobertura": coverage_chart,
    "procesamiento": processing_chart,
    "descarga": download_chart,
}
