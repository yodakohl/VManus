#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LAYERED = ROOT / "experiments/yolo/sidequest_semantic_776_layered_edition_two_hundred_sixteenth"
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
LEDGER = LAYERED / "TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv"
EVENTS = BASE / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv"
STATEMENTS = BASE / "TWO_HUNDRED_THIRTEENTH_116_STATEMENT_CROSS_REGISTER_PROSE.tsv"

PROSE_LABEL = {
    "COMMON_PORTABLE_CARD": "KERN",
    "LOCAL_CARD_WITH_COMMON_AXIS": "ACHSE",
    "PROSE_COMPONENT_CARD": "PROSA",
    "LOCAL_WHOLE_CARD": "GANZKARTE",
    "LOCAL_PRODUCTIVE_CARD_CORE": "LOKAL",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prose_annotation(layer: dict[str, str]) -> str:
    kind = PROSE_LABEL[layer["primary_layer"]]
    if kind == "KERN":
        return f"[KERN:{layer['portable_core_value_de']}]"
    if kind == "ACHSE":
        return f"[ACHSE:{layer['component_axes']}→{layer['local_expansion_de']}]"
    return f"[{kind}:{layer['local_expansion_de']}]"


def astro_annotation(layer: dict[str, str]) -> str:
    if layer["primary_layer"] == "COMMON_PORTABLE_SURFACE":
        return f"[KERN:{layer['portable_core_value_de']}/{layer['visible_surface']}]"
    if layer["primary_layer"] == "ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH":
        return f"[ASTRO-HOMOGRAPH:{layer['visible_surface']}]"
    return f"[EXEMPLAR:{layer['visible_surface']}]"


def main() -> None:
    ledger = read(LEDGER)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    layer_by_event = {row["source_id"]: row for row in ledger if row["source_kind"] == "PROSE_EVENT"}
    astro_layers = [row for row in ledger if row["source_kind"] == "ASTRO_GROUP"]
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    statement_rows: list[dict[str, object]] = []
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        layers = [layer_by_event[row["event_id"]] for row in rows]
        counts = Counter(layer["primary_layer"] for layer in layers)
        statement_rows.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "visible_owner": statement["visible_owner"],
            "visible_sequence": statement["visible_sequence"],
            "layered_card_reading": " ".join(prose_annotation(layer) for layer in layers),
            "fluent_owner_expansion_de": statement["revised_fluent_translation_de"],
            "event_count": len(rows),
            "common_portable_count": counts["COMMON_PORTABLE_CARD"],
            "local_common_axis_count": counts["LOCAL_CARD_WITH_COMMON_AXIS"],
            "prose_extension_count": counts["PROSE_COMPONENT_CARD"],
            "whole_or_local_count": counts["LOCAL_WHOLE_CARD"] + counts["LOCAL_PRODUCTIVE_CARD_CORE"],
        })
    write(OUT / "TWO_HUNDRED_SEVENTEENTH_116_LAYERED_STATEMENTS.tsv", statement_rows)

    astro_group_rows: list[dict[str, object]] = []
    for layer in astro_layers:
        astro_group_rows.append({
            "source_id": layer["source_id"],
            "unit_id": layer["unit_id"],
            "page": layer["page"],
            "locus": layer["locus_or_field"],
            "visible_owner": layer["visible_owner"],
            "visible_surface": layer["visible_surface"],
            "primary_layer": layer["primary_layer"],
            "layered_group_reading": astro_annotation(layer),
            "local_owner_expansion_de": layer["local_expansion_de"],
        })
    write(OUT / "TWO_HUNDRED_SEVENTEENTH_395_LAYERED_ASTRO_GROUPS.tsv", astro_group_rows)

    by_locus: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in astro_group_rows:
        by_locus[(str(row["unit_id"]), str(row["page"]), str(row["locus"]))].append(row)
    locus_rows: list[dict[str, object]] = []
    for (unit_id, page, locus), rows in by_locus.items():
        counts = Counter(str(row["primary_layer"]) for row in rows)
        locus_rows.append({
            "unit_id": unit_id,
            "page": page,
            "locus": locus,
            "visible_owner": rows[0]["visible_owner"],
            "surface_text": " ".join(str(row["visible_surface"]) for row in rows),
            "layered_group_reading": " ".join(str(row["layered_group_reading"]) for row in rows),
            "local_owner_expansion_de": " || ".join(str(row["local_owner_expansion_de"]) for row in rows),
            "group_count": len(rows),
            "common_count": counts["COMMON_PORTABLE_SURFACE"],
            "homograph_count": counts["ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH"],
            "exemplar_count": counts["ASTRO_LOCAL_EXEMPLAR"],
        })
    write(OUT / "TWO_HUNDRED_SEVENTEENTH_142_LAYERED_ASTRO_LOCI.tsv", locus_rows)

    lines = [
        "# Lesbare geschichtete Zehn-Seiten-Ausgabe",
        "",
        "Legende: `[KERN]` ist eine ganze portable Karte; `[ACHSE]` eine lokale Prosakarte mit gemeinsamem Bauteil; `[PROSA]` eine Prosaachse; `[GANZKARTE]` ein gelerntes lokales Wort; `[ASTRO-HOMOGRAPH]` nur gleiche Oberfläche; `[EXEMPLAR]` lokales Diagrammetikett.",
        "",
    ]
    record_order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    for record in record_order:
        rows = [row for row in statement_rows if row["record_unit_id"] == record]
        lines.extend([f"## {record} — {rows[0]['visible_owner']}", ""])
        for row in rows:
            lines.extend([
                f"- **{row['statement_id']}** `{row['visible_sequence']}`",
                f"  - Karten: {row['layered_card_reading']}",
                f"  - Besitzerlesung: {row['fluent_owner_expansion_de']}",
            ])
        lines.append("")
    for unit, title in (("A1", "f67r2 — zwei lokale Räder"), ("A2", "f68r1 — Mehrpaneel-Sternatlas"), ("A3", "f69v — drei getrennte Räder")):
        rows = [row for row in locus_rows if row["unit_id"] == unit]
        lines.extend([f"## {unit}: {title}", ""])
        for row in rows:
            lines.extend([
                f"- **{row['locus']} — {row['visible_owner']}** `{row['surface_text']}`",
                f"  - Gruppen: {row['layered_group_reading']}",
                f"  - Lokale Lesung: {row['local_owner_expansion_de']}",
            ])
        lines.append("")
    (OUT / "TWO_HUNDRED_SEVENTEENTH_READABLE_TEN_PAGES.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "layered_source_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "statements": len(statement_rows),
        "prose_events": sum(int(row["event_count"]) for row in statement_rows),
        "astro_groups": len(astro_group_rows),
        "astro_loci": len(locus_rows),
        "records": len({row["record_unit_id"] for row in statement_rows}),
        "astro_units": len({row["unit_id"] for row in locus_rows}),
        "readable_lines": len(lines),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
