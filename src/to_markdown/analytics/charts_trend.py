"""Gráficos de tendencia: cómo cambian las cosas en el tiempo.

Una foto dice cuánto hay; una tendencia dice hacia dónde va. Aquí están las tres series con
fecha del proyecto —la actividad normativa del Compendio, la duración de las etapas y el
historial de corridas— y por eso van antes que las estructurales en el informe.
"""

from __future__ import annotations

from collections import Counter

from ..core import BOOKS
from .format import bar, es, sparkline, timeline


def amendment_chart(snap: dict, width: int) -> list[str]:
    """Cuánto cambió la norma cada año. Es LA tendencia del corpus.

    No mide nuestro trabajo sino el del organismo: cada barra es cuántos números normativos
    declararon una modificación ese año, según las propias notas que la SP pega al número
    que cambia.
    """
    activity = snap["amendments"]
    years = activity["years"]
    if not years:
        return ["[b]Actividad normativa[/b]", "", "  sin notas fechadas todavía"]

    lines = ["[b]Actividad normativa por año[/b] · modificaciones que declara la norma", ""]
    lines += timeline(dict(years), width)

    total = sum(years.values())
    span = max(years) - min(years) + 1
    recent = sum(v for k, v in years.items() if k >= max(years) - 4)
    peak = max(years.items(), key=lambda kv: kv[1])
    lines += [
        "",
        (f"[b]{es(total)}[/b] modificaciones fechadas en [b]{span}[/b] años "
         f"({min(years)}–{max(years)})"),
        (f"promedio [b]{es(total / span, 0)}[/b] al año · máximo en [b]{peak[0]}[/b] "
         f"con {peak[1]}"),
        f"últimos 5 años: [b]{es(recent)}[/b] ({recent / total:.0%} del total)",
    ]
    if activity["undated"]:
        lines.append(
            f"[dim]{activity['undated']} notas sin fecha legible, no entran en la serie[/dim]"
        )

    lines += ["", "[dim]Por Libro, mismos años[/dim]"]
    for slug, counts in activity["by_book"].items():
        if not counts:
            continue
        run = [float(counts.get(y, 0)) for y in range(min(years), max(years) + 1)]
        lines.append(
            f"{slug:<9} {sparkline(run, max(8, width - 22))} {es(sum(counts.values())):>6}"
        )
    lines.append(f"[dim]{es(len(activity['ncg']))} Normas de Carácter General distintas "
                 f"citadas en el corpus[/dim]")
    return lines


def timing_chart(snap: dict, width: int) -> list[str]:
    """Cuánto tarda cada etapa, y si eso está empeorando.

    La mediana responde "cuánto cuesta"; la serie responde "¿está tardando más que antes?",
    que es la pregunta que una sola corrida no puede contestar.
    """
    timings = snap["timings"]
    if not timings:
        return [
            "[b]Duración de las etapas[/b]", "",
            "  todavía no hay corridas registradas",
            ("[dim]Se anota sola en cada corrida, desde el panel o desde la "
             "línea de comandos.[/dim]"),
        ]

    # Solo se comparan corridas del MISMO alcance. Una etapa sobre un Libro y la misma
    # sobre los cinco tardan cosas distintas por definición, y mezclarlas daba tendencias
    # de +800% que solo decían "esta vez corrí más Libros".
    #
    # Se toma el alcance MÁS FRECUENTE y no el de la última corrida: una prueba o una
    # reejecución suelta sobre un Libro no puede redefinir contra qué se compara todo.
    # A igual frecuencia gana el alcance más grande, que es el que la gente corre.
    frequency = Counter(len(r.get("books", [])) for r in timings)
    scope = max(frequency, key=lambda n: (frequency[n], n))
    comparable = [r for r in timings if len(r.get("books", [])) == scope]
    by_stage: dict[str, list[float]] = {}
    for row in comparable:
        by_stage.setdefault(row["stage"], []).append(float(row.get("seconds", 0)))
    if not by_stage:
        return ["[b]Duración de las etapas[/b]", "", "  sin corridas comparables todavía"]

    scope_label = "los 5 Libros" if scope == len(BOOKS) else f"{scope} Libro(s)"
    lines = [f"[b]Duración de las etapas[/b] · mediana sobre {scope_label}", ""]
    medians = {k: sorted(v)[len(v) // 2] for k, v in by_stage.items()}
    tail = max(len(f"{v:.1f} s") for v in medians.values())
    space = max(4, width - 9 - tail - 3)
    top = max(medians.values())
    for stage, value in sorted(medians.items(), key=lambda kv: -kv[1]):
        lines.append(
            f"{stage:<9} {bar(value, top, space):<{space}} {f'{value:.1f} s':>{tail}}"
        )

    lines += ["", "[dim]Tendencia por etapa (corridas en orden)[/dim]"]
    for stage, values in sorted(by_stage.items(), key=lambda kv: -medians[kv[0]]):
        if len(values) < 2:
            lines.append(f"{stage:<9} [dim](una sola corrida: {values[0]:.1f} s)[/dim]")
            continue
        change = (values[-1] - values[0]) / values[0] if values[0] else 0.0
        mark, close = (("[b]", "[/b]") if abs(change) >= 0.25 else ("[dim]", "[/dim]"))
        lines.append(
            f"{stage:<9} {sparkline(values, max(8, width - 26))} "
            f"{mark}{change:+.0%}{close} [dim]×{len(values)}[/dim]"
        )

    total = sum(medians.values())
    aborted = sum(1 for row in timings if not row.get("ok", True))
    off_scope = len(timings) - len(comparable)
    lines += [
        "",
        f"una corrida completa: [b]{total:.0f} s[/b] sumando las medianas",
        (f"[b]{len(comparable)}[/b] ejecuciones comparables registradas"
         + (f" · [b]{aborted}[/b] se detuvieron" if aborted else "")
         + (f" [dim]· {off_scope} de otro alcance, fuera de la serie[/dim]"
            if off_scope else "")),
    ]
    return lines


def run_history_chart(snap: dict, width: int) -> list[str]:
    """La deriva entre corridas, que ninguna invariante puede ver.

    Cada invariante compara una corrida contra la anterior, así que un descenso lento nunca
    la dispara. La serie sí lo muestra.
    """
    lines = ["[b]Historial de corridas[/b] · texto extraído, corrida a corrida", ""]
    series = {s: v for s, v in snap["history"].items() if v}
    if not series:
        return [*lines, "  todavía no hay corridas registradas"]

    suffixes = {
        slug: (f"{(v[-1] - v[0]) / v[0] if v[0] else 0.0:+.1%}",
               f"×{len(v)}" if width < 60 else f"({len(v)} corridas)")
        for slug, v in series.items()
    }
    suffix_width = max(len(a) + 1 + len(b) for a, b in suffixes.values())
    space = max(6, width - 10 - suffix_width - 1)
    for slug, values in snap["history"].items():
        if not values:
            lines.append(f"{slug:<9} [dim](sin corridas registradas)[/dim]")
            continue
        drift, count = suffixes[slug]
        value = float(drift.rstrip("%"))
        mark, close = (("[dim]", "[/dim]") if abs(value) < 1
                       else ("[b]", "[/b]") if abs(value) >= 25 else ("", ""))
        tail = f"{drift} {count}".rjust(suffix_width)
        lines.append(f"{slug:<9} {sparkline(values, space)} {mark}{tail}{close}")

    stamps = [v for v in snap["history_at"].values() if v]
    if stamps:
        first_seen = sorted(f[0] for f in stamps if f)
        last_seen = sorted(f[-1] for f in stamps if f)
        lines += ["", f"[dim]de {first_seen[0][:10]} a {last_seen[-1][:10]}[/dim]"]
    lines.append(
        "[dim]Una línea plana significa que el pipeline es reproducible; "
        "una deriva sostenida, que algo cambió.[/dim]"
    )
    return lines



