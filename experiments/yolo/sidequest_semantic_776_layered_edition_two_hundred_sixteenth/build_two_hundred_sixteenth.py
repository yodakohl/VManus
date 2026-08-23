#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
SCOPED = ROOT / "experiments/yolo/sidequest_semantic_scoped_apprentice_grammar_two_hundred_fifteenth"
EVENTS = BASE / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv"
ASTRO = BASE / "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv"
CARDS = SCOPED / "TWO_HUNDRED_FIFTEENTH_173_CARD_SCOPED_DICTIONARY.tsv"
BRIDGES = BASE / "TWO_HUNDRED_THIRTEENTH_13_ASTRO_BRIDGE_CARD_SUMMARY.tsv"

LAYER_DESCRIPTIONS = {
    "COMMON_PORTABLE_CARD": "exakte Karte mit demselben Kernwert in Herbal, Bio und Astro",
    "LOCAL_CARD_WITH_COMMON_AXIS": "lokale Prosakarte, die mindestens eine gemeinsame Achse enthält",
    "PROSE_COMPONENT_CARD": "komponierte Herbal/Bio-Karte ohne derzeit portablen Astro-Ganzwert",
    "LOCAL_WHOLE_CARD": "gelernte lokale Prosa-Ganzkarte",
    "LOCAL_PRODUCTIVE_CARD_CORE": "produktive lokale Karte außerhalb der 28 Lehrachsen",
    "COMMON_PORTABLE_SURFACE": "Astrogruppe, deren ganze Oberfläche eine gemeinsame Kernkarte ist",
    "ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH": "lokales Astroetikett mit gleicher Oberfläche wie eine andere Prosakarte",
    "ASTRO_LOCAL_EXEMPLAR": "lokales Astroetikett ohne exakte Prosakarte",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    astro = read(ASTRO)
    scoped = {row["master_card_id"]: row for row in read(CARDS)}
    bridge_ids = {row["master_card_id"] for row in read(BRIDGES)}
    unified: list[dict[str, object]] = []
    serial = 0

    for event in events:
        serial += 1
        card_id = event["master_card_id"]
        if card_id in bridge_ids:
            layer = "COMMON_PORTABLE_CARD"
        elif scoped[card_id]["semantic_scope"] == "HAS_COMMON_CORE_AXIS":
            layer = "LOCAL_CARD_WITH_COMMON_AXIS"
        else:
            layer = scoped[card_id]["semantic_scope"]
        local_expansion = "Sollmaß" if card_id == "MC039" else "Klarlauf" if card_id == "MC119" else event["portable_value_de"]
        unified.append({
            "unified_serial": serial,
            "source_kind": "PROSE_EVENT",
            "section": "HERBAL" if event["record_unit_id"].startswith("H") else "BIOLOGICAL",
            "unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus_or_field": event["field_id"],
            "source_id": event["event_id"],
            "visible_owner": event["visible_owner"],
            "visible_surface": event["visible_surface"],
            "normalized_id": card_id,
            "primary_layer": layer,
            "portable_core_value_de": event["portable_value_de"] if layer == "COMMON_PORTABLE_CARD" else "NONE",
            "local_expansion_de": local_expansion,
            "component_axes": "+".join(value for value in (scoped[card_id]["common_axes"], scoped[card_id]["prose_only_axes"]) if value != "NONE") or "NONE",
            "layer_rule_de": LAYER_DESCRIPTIONS[layer],
        })

    page_unit = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}
    for group in astro:
        serial += 1
        if group["is_herbal_bio_bridge_card"] == "YES":
            layer = "COMMON_PORTABLE_SURFACE"
            portable = group["exact_prose_value_de"]
        elif group["exact_prose_card_id"] != "NONE":
            layer = "ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH"
            portable = "NONE"
        else:
            layer = "ASTRO_LOCAL_EXEMPLAR"
            portable = "NONE"
        unified.append({
            "unified_serial": serial,
            "source_kind": "ASTRO_GROUP",
            "section": "ASTRO",
            "unit_id": page_unit[group["page"]],
            "page": group["page"],
            "locus_or_field": group["locus"],
            "source_id": f"A{int(group['group_serial']):03d}",
            "visible_owner": group["visible_owner"],
            "visible_surface": group["visible_surface"],
            "normalized_id": group["exact_prose_card_id"] if group["exact_prose_card_id"] != "NONE" else f"ASTRO_LOCAL_{int(group['group_serial']):03d}",
            "primary_layer": layer,
            "portable_core_value_de": portable,
            "local_expansion_de": group["astro_local_reading_de"],
            "component_axes": "LOCAL_ASTRO_PARSE",
            "layer_rule_de": LAYER_DESCRIPTIONS[layer],
        })
    write(OUT / "TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv", unified)

    units: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in unified:
        units[str(row["unit_id"])].append(row)
    unit_rows: list[dict[str, object]] = []
    for unit_id, rows in units.items():
        counts = Counter(str(row["primary_layer"]) for row in rows)
        unit_rows.append({
            "unit_id": unit_id,
            "section": rows[0]["section"],
            "page": rows[0]["page"],
            "visible_groups": len(rows),
            "common_portable": counts["COMMON_PORTABLE_CARD"] + counts["COMMON_PORTABLE_SURFACE"],
            "local_with_common_axis": counts["LOCAL_CARD_WITH_COMMON_AXIS"],
            "prose_extension": counts["PROSE_COMPONENT_CARD"],
            "local_prose_whole_or_core": counts["LOCAL_WHOLE_CARD"] + counts["LOCAL_PRODUCTIVE_CARD_CORE"],
            "astro_homograph": counts["ASTRO_LOCAL_LABEL_WITH_PROSE_HOMOGRAPH"],
            "astro_local_exemplar": counts["ASTRO_LOCAL_EXEMPLAR"],
            "layer_profile": "|".join(f"{key}:{value}" for key, value in sorted(counts.items())),
        })
    write(OUT / "TWO_HUNDRED_SIXTEENTH_14_UNIT_LAYER_SUMMARY.tsv", unit_rows)

    layer_rows = [
        {"primary_layer": layer, "description_de": description, "group_count": sum(row["primary_layer"] == layer for row in unified)}
        for layer, description in LAYER_DESCRIPTIONS.items()
    ]
    write(OUT / "TWO_HUNDRED_SIXTEENTH_LAYER_DICTIONARY.tsv", layer_rows)
    layer_counts = Counter(str(row["primary_layer"]) for row in unified)
    summary = {
        "prose_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "astro_source_sha256": hashlib.sha256(ASTRO.read_bytes()).hexdigest(),
        "card_scope_source_sha256": hashlib.sha256(CARDS.read_bytes()).hexdigest(),
        "groups": len(unified),
        "prose_events": sum(row["source_kind"] == "PROSE_EVENT" for row in unified),
        "astro_groups": sum(row["source_kind"] == "ASTRO_GROUP" for row in unified),
        "units": len(unit_rows),
        "layer_counts": dict(layer_counts),
        "common_portable_total": layer_counts["COMMON_PORTABLE_CARD"] + layer_counts["COMMON_PORTABLE_SURFACE"],
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
