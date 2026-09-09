"""Gráficos del estado actual: qué se descargó, qué se procesó y cuánto cubre el PDF.

Son una foto. Responden "cuánto hay" con forma de barra, que es más rápido de comparar
entre Libros que una tabla de números.
"""

from __future__ import annotations

from .format import DENSITY, es, human_bytes, rows_chart


def download_chart(snap: dict, width: int) -> list[str]:
    """Qué se descargó y qué costó traerlo."""
    lines = ["[b]Descarga[/b] · lo que hay en caché", ""]
    rows = [(d["slug"], d["pages"], f"{d['pages']} pág") for d in snap["download"]]
    lines += rows_chart(rows, width)
    lines += ["", "[dim]HTML en caché[/dim]"]
    lines += rows_chart(
        [(d["slug"], d["cache_bytes"], human_bytes(d["cache_bytes"])) for d in snap["download"]],
        width,
    )
    lines += ["", "[dim]Figuras descargadas[/dim]"]
    lines += rows_chart(
        [(d["slug"], d["images"], f"{d['images']} · {human_bytes(d['image_bytes'])}")
         for d in snap["download"]],
        width,
    )
    lines += ["", "[dim]PDF oficial[/dim]"]
    lines += rows_chart(
        [(d["slug"], d["pdf_bytes"], human_bytes(d["pdf_bytes"]) if d["pdf_bytes"] else "—")
         for d in snap["download"]],
        width,
    )

    total_pages = sum(d["pages"] for d in snap["download"])
    tracked = sum(d["tracked"] for d in snap["download"])
    revalidable = sum(d["revalidable"] for d in snap["download"])
    weight = sum(d["cache_bytes"] + d["image_bytes"] + d["pdf_bytes"] for d in snap["download"])
    fetches = [d["last_fetch"] for d in snap["download"] if d["last_fetch"]]
    lines += [
        "",
        f"[b]{es(total_pages)}[/b] páginas · [b]{human_bytes(weight)}[/b] en disco",
        (f"[b]{revalidable}/{tracked}[/b] revalidables con ETag"
         if tracked else "sin índice HTTP todavía"),
    ]
    if fetches:
        lines.append(f"última extracción del portal: {max(fetches)}")
    return lines


def processing_chart(snap: dict, width: int) -> list[str]:
    """Qué salió del procesamiento, y con cuánto margen sobre las cotas."""
    lines = ["[b]Procesamiento[/b] · normas extraídas", ""]
    lines += rows_chart(
        [(p["slug"], p["documents"], str(p["documents"])) for p in snap["processing"]], width
    )
    lines += ["", "[dim]Números normativos direccionables[/dim]"]
    lines += rows_chart(
        [(p["slug"], p["units"], es(p["units"])) for p in snap["processing"]], width
    )
    lines += ["", "[dim]Texto extraído[/dim]"]
    lines += rows_chart(
        [(p["slug"], p["chars"], f"{p['chars'] / 1e6:.2f} MB") for p in snap["processing"]], width
    )
    lines += ["", "[dim]Figuras · notas de actualización[/dim]"]
    lines += rows_chart(
        [(p["slug"], p["figures"], f"{p['figures']} fig · {p['notes']} notas")
         for p in snap["processing"]],
        width,
    )

    lines += ["", "[dim]Margen sobre la cota mínima de cada Libro[/dim]"]
    margins = []
    for p in snap["processing"]:
        if not p["min_documents"]:
            continue
        share = p["documents"] / p["min_documents"] - 1
        margins.append((p["slug"], max(share, 0), f"+{share:.0%}"))
    lines += rows_chart(margins, width)

    total = {k: sum(p[k] for p in snap["processing"])
             for k in ("documents", "units", "figures", "notes", "sections", "delivered")}
    lines += [
        "",
        f"[b]{es(total['documents'])}[/b] normas · [b]{es(total['units'])}[/b] números",
        f"[b]{es(total['figures'])}[/b] figuras · [b]{es(total['notes'])}[/b] notas",
        f"[b]{total['sections']}[/b] Títulos · [b]{total['delivered']}[/b] archivos entregados",
    ]
    return lines


def coverage_chart(snap: dict, width: int) -> list[str]:
    """El PDF oficial contra el portal: la medida de si la extracción quedó completa."""
    ready = [c for c in snap["coverage"] if c.get("ready")]
    if not ready:
        return ["[b]Cobertura[/b]", "", "  sin comparativa todavía: corre la etapa `compare`"]

    lines = ["[b]Cobertura[/b] · PDF oficial contra el portal", ""]
    lines += ["[dim]Capítulos alineados[/dim]"]
    lines += rows_chart(
        [(c["slug"], c["aligned"], f"{c['aligned']}/{c['documents']}") for c in ready], width
    )

    lines += ["", "[dim]Veredicto por capítulo[/dim]"]
    label, tail = 9, 4
    space = max(8, width - label - tail - 3)
    for c in ready:
        total = max(c["match"] + c["reformatted"] + c["unaligned"] + c["extra_in_pdf"], 1)
        cells = [(DENSITY[k], c[k]) for k in
                 ("match", "reformatted", "unaligned", "extra_in_pdf")]
        drawn = 0
        parts = []
        for index, (glyph, count) in enumerate(cells):
            size = (space - drawn) if index == len(cells) - 1 else round(count / total * space)
            drawn += size
            if size > 0:
                parts.append(glyph * size)
        lines.append(f"{c['slug']:<{label}} {''.join(parts)} {c['match'] / total:>3.0%}")
    # La leyenda se parte cuando no cabe: en una terminal angosta, una sola línea de 59
    # columnas se cortaría justo donde están los nombres de las clases.
    legend = [
        f"{DENSITY['match']} igual", f"{DENSITY['reformatted']} reformateado",
        f"{DENSITY['unaligned']} sin alinear", f"{DENSITY['extra_in_pdf']} solo en el PDF",
    ]
    lines.append("")
    if sum(len(x) + 3 for x in legend) <= width:
        lines.append("   ".join(legend))
    else:
        lines += [f"  {x}" for x in legend]
    lines.append("[dim]Cuanto más lleno el bloque, mejor calzan PDF y portal.[/dim]")

    lines += ["", "[dim]Texto que solo está en el PDF[/dim]"]
    lines += rows_chart(
        [(c["slug"], c["extra_share"], f"{c['extra_share']:.3%}") for c in ready], width
    )

    lines += ["", "[dim]Figuras compartidas · solo web · solo PDF[/dim]"]
    lines += rows_chart(
        [(c["slug"], c["figures_shared"],
          f"{c['figures_shared']} · {c['figures_only_web']} · {c['figures_only_pdf']}")
         for c in ready],
        width,
    )

    aligned = sum(c["aligned"] for c in ready)
    documents = sum(c["documents"] for c in ready) or 1
    extra = sum(c["extra_words"] for c in ready)
    pages = sum(c["pdf_pages"] for c in ready)
    lines += [
        "",
        (f"[b]{aligned}/{documents}[/b] alineados ({aligned / documents:.1%}) "
         f"sobre {es(pages)} páginas de PDF"),
        f"[b]{es(extra)}[/b] palabras existen solo en el PDF",
    ]
    return lines
