"""Etapa de cambios: qué cambió respecto de la corrida anterior, y de qué tipo.

Responde tres preguntas distintas que un solo hash no puede separar:

  ¿el servidor tocó la página?     -> `Last-Modified` / `ETag` (lo resuelve HTTP, no nosotros)
  ¿cambió el contenido, o solo lo tocaron?  -> `source_sha256` del cuerpo HTML
  ¿es un cambio normativo declarado?        -> apareció una "Nota de actualización" nueva

Cruzarlas da una clasificación, que es mucho más útil que un booleano: un retoque del CMS,
una corrección de tipeo y una modificación por Norma de Carácter General no son lo mismo y
no se accionan igual.

El diff es por unidad numerada, no por documento: "el N° 4 del Capítulo II cambió" es
accionable; "este documento de 12 KB cambió" no lo es.

Uso:  uv run python -m to_markdown.changes
"""

from __future__ import annotations

import difflib
import json
from datetime import UTC, datetime

from ..core import BOOKS, Book
from ..core.guard import previous_state, save_state
from .parse import SCHEMA_VERSION

# Orden de severidad para el informe: lo normativo primero.
CATEGORIES = ("new", "normative", "editorial", "removed", "pipeline", "cosmetic")
# La prosa del informe va en español, como el resto de la documentación; las claves y los
# identificadores de esquema van en inglés.
EXPLAIN = {
    "new": "normas que no existían en la corrida anterior",
    "normative": "el contenido cambió y la propia norma lo declara con una Nota de actualización",
    "editorial": "el contenido cambió sin nota que lo declare (tipeo, formato, corrección)",
    "removed": "normas que ya no están en el árbol",
    "pipeline": "cambió nuestra salida, no la norma: es una modificación del parser",
    "cosmetic": "el CMS tocó la página pero el contenido es idéntico",
}


def classify(before: dict, after: dict) -> str | None:
    """Clase de cambio de un documento, o None si no cambió en nada observable."""
    source_changed = before.get("source_sha256") != after.get("source_sha256")
    content_changed = before.get("content_sha256") != after.get("content_sha256")

    if not source_changed and not content_changed:
        return None
    if not source_changed and content_changed:
        # La fuente es idéntica pero nuestra salida no: cambió el parser, no la norma.
        # Distinguirlo es la razón de llevar dos hashes en vez de uno.
        return "pipeline"
    if source_changed and not content_changed:
        return "cosmetic"
    new_notes = set(after.get("amendment_notes", [])) - set(before.get("amendment_notes", []))
    return "normative" if new_notes else "editorial"


def diff_units(before: list[dict], after: list[dict]) -> list[dict]:
    """Diff a nivel de número normativo, con detección de renumeración.

    La renumeración es real y frecuente: 93 notas del corpus dicen cosas como "pasando los
    actuales números 3 al 12 a ser 5 al 14". Emparejar solo por número reportaría decenas de
    cambios falsos, así que primero se empareja por hash de contenido: misma unidad con otro
    número es una renumeración, no una modificación.
    """
    by_sha = {}
    for unit in before:
        by_sha.setdefault(unit["sha256"], []).append(unit)
    by_num = {u["number"]: u for u in before if u["number"]}

    events: list[dict] = []
    consumed: set[str] = set()

    for unit in after:
        same = next(
            (u for u in by_sha.get(unit["sha256"], []) if u["unit_id"] not in consumed), None
        )
        if same:
            consumed.add(same["unit_id"])
            if same["number"] != unit["number"]:
                events.append({
                    "type": "renumbered",
                    "from": same["number"],
                    "to": unit["number"],
                    "unit_id": unit["unit_id"],
                })
            continue

        old = by_num.get(unit["number"]) if unit["number"] else None
        if old and old["unit_id"] not in consumed:
            consumed.add(old["unit_id"])
            # Hash distinto con texto idéntico no es un cambio: reportarlo produciría un
            # diff vacío, que en un changelog se lee como un fallo de la herramienta.
            if old["text"] == unit["text"]:
                continue
            events.append({
                "type": "modified",
                "number": unit["number"],
                "unit_id": unit["unit_id"],
                "diff": _text_diff(old["text"], unit["text"]),
            })
        else:
            events.append({
                "type": "added",
                "number": unit["number"],
                "unit_id": unit["unit_id"],
                "text": unit["text"][:400],
            })

    for unit in before:
        if unit["unit_id"] not in consumed and not any(
            e.get("unit_id", "").endswith(f"#{unit['number']}") for e in events
        ):
            events.append({
                "type": "removed",
                "number": unit["number"],
                "unit_id": unit["unit_id"],
                "text": unit["text"][:400],
            })
    return events


def _text_diff(before: str, after: str, max_lines: int = 24) -> str:
    lines = list(
        difflib.unified_diff(
            before.splitlines(), after.splitlines(), lineterm="", n=1, fromfile="", tofile=""
        )
    )[2:]
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"… ({len(lines) - max_lines} líneas más)"]
    return "\n".join(lines)


def build_report(book: Book, before: list[dict], after: list[dict]) -> dict:
    prev = {d["pvid"]: d for d in before}
    curr = {d["pvid"]: d for d in after}
    changes: list[dict] = []

    for pvid, document in curr.items():
        if pvid not in prev:
            changes.append({"category": "new", "document": _summary(document), "units": []})
            continue
        category = classify(prev[pvid], document)
        if not category:
            continue
        before_notes = set(prev[pvid].get("amendment_notes", []))
        changes.append({
            "category": category,
            "document": _summary(document),
            "new_notes": sorted(set(document.get("amendment_notes", [])) - before_notes),
            "units": diff_units(prev[pvid].get("units", []), document.get("units", []))
            if category in ("normative", "editorial", "pipeline")
            else [],
        })

    for pvid, document in prev.items():
        if pvid not in curr:
            changes.append({"category": "removed", "document": _summary(document), "units": []})

    changes.sort(key=lambda c: CATEGORIES.index(c["category"]))
    return {
        "book": {"slug": book.slug, "name": book.name},
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "schema_version": SCHEMA_VERSION,
        "documents_before": len(before),
        "documents_after": len(after),
        "summary": {c: sum(1 for x in changes if x["category"] == c) for c in CATEGORIES},
        "changes": changes,
    }


def _summary(document: dict) -> dict:
    return {
        "pvid": document["pvid"],
        "citation": document.get("citation", document.get("path", "")),
        "url": document["url"],
    }


def render(report: dict) -> str:
    lines = [
        f"# Cambios — {report['book']['name']} — {report['generated_at']}",
        "",
        f"Documentos: {report['documents_before']:,} → {report['documents_after']:,}",
        "",
        "| Clase | Documentos | Qué significa |",
        "| --- | ---: | --- |",
    ]
    for category in CATEGORIES:
        lines.append(f"| {category} | {report['summary'][category]} | {EXPLAIN[category]} |")

    if not report["changes"]:
        lines += ["", "Sin cambios respecto de la corrida anterior."]
        return "\n".join(lines) + "\n"

    for category in CATEGORIES:
        group = [c for c in report["changes"] if c["category"] == category]
        if not group:
            continue
        lines += ["", f"## {category} ({len(group)})", ""]
        for change in group:
            doc = change["document"]
            lines += [f"### {doc['citation']}", "", doc["url"], ""]
            for note in change.get("new_notes", []):
                lines.append(f"- **Nota de actualización nueva:** {note}")
            for event in change["units"]:
                if event["type"] == "renumbered":
                    lines.append(f"- N° {event['from']} → N° {event['to']} (renumerado, texto idéntico)")
                elif event["type"] == "modified":
                    lines += [f"- **N° {event['number']} modificado**", ""]
                    if event["diff"]:
                        lines += ["```diff", event["diff"], "```", ""]
                elif event["type"] == "added":
                    lines += [f"- **N° {event['number']} agregado**", "", f"  > {event['text'][:300]}", ""]
                else:
                    lines += [f"- **N° {event['number']} eliminado**", "", f"  > {event['text'][:300]}", ""]
            lines.append("")
    return "\n".join(lines) + "\n"


def changes_for(book: Book) -> dict | None:
    """Informe de cambios de un Libro, o None si es su primera corrida."""
    book.mkdirs()
    current = json.loads(book.file("documents.json").read_text(encoding="utf-8"))
    before = previous_state(book)

    if before is None:
        print(f"{book.slug:10} first run: nothing to compare against, saving baseline state")
        save_state(book, current)
        return None

    report = build_report(book, before, current)
    # La clave del informe es `generated_at`; escribirla mal aquí reventaba con KeyError en
    # la segunda corrida de cualquier Libro, que es justo cuando el changelog empieza a valer.
    stamp = report["generated_at"].replace(":", "").replace("-", "")
    (book.changelog / f"{stamp}.md").write_text(render(report), encoding="utf-8")
    book.file("changes.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary_line = " · ".join(
        f"{c} {report['summary'][c]}" for c in CATEGORIES if report["summary"][c]
    )
    print(f"{book.slug:10} changes: {len(report['changes']):4} | {summary_line or 'no changes'}")
    print(f"{'':10} changelog -> {book.changelog / f'{stamp}.md'}")
    # El estado avanza aquí, no en `parse`: si avanzara antes, el diff se compararía
    # contra sí mismo y siempre daría "sin cambios".
    save_state(book, current)
    return report


def main(books: list[Book] | None = None) -> None:
    for book in books or BOOKS:
        changes_for(book)


if __name__ == "__main__":
    main()
