#!/usr/bin/env python3
"""Assign all 39 working entries to the pass-678 historical workshop layers."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P672 = ROOT / "experiments/yolo/sidequest_semantic_integrated_dictionary_six_hundred_seventy_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LAYER = {
    "OK": "OPERATION_SIGN", "CHD": "OPERATION_SIGN", "SH": "OPERATION_SIGN",
    "SHED": "OPERATION_SIGN", "CHK": "OPERATION_SIGN", "SOLK": "OPERATION_SIGN",
    "P": "OPERATION_SIGN", "LSH": "OPERATION_SIGN", "CFH": "OPERATION_SIGN",
    "CH": "OPERATION_SIGN", "T": "OPERATION_SIGN", "K": "OPERATION_SIGN",
    "S": "OPERATION_SIGN", "L": "OPERATION_SIGN", "R": "OPERATION_SIGN",
    "LD": "OPERATION_SIGN",
    "CTH": "STATE_OBJECT_SIGN", "AIR": "STATE_OBJECT_SIGN", "OR": "STATE_OBJECT_SIGN",
    "HO": "STATE_OBJECT_SIGN", "CKH": "STATE_OBJECT_SIGN", "O": "STATE_OBJECT_SIGN",
    "OL": "RELATION_ADDRESS_SIGN", "OT": "RELATION_ADDRESS_SIGN",
    "AL": "RELATION_ADDRESS_SIGN", "AR": "RELATION_ADDRESS_SIGN",
    "AIN": "MEASURE_STAGE_SIGN", "AIIN": "MEASURE_STAGE_SIGN",
    "IIN": "MEASURE_STAGE_SIGN", "AN": "MEASURE_STAGE_SIGN", "DA": "MEASURE_STAGE_SIGN",
    "E": "BOUND_GRADE", "EE": "BOUND_GRADE", "EEE": "BOUND_GRADE",
    "DY": "BOUND_ENDPOINT", "Y": "DEICTIC_REFERENCE",
    "OS": "WHOLE_NOMENCLATOR", "RESUME_CARD": "WHOLE_NOMENCLATOR",
    "TALAM": "WHOLE_NOMENCLATOR",
}

SHORT = {
    "OK": "ANSETZEN", "CHD": "UMSETZEN", "SH": "HALTEN", "SHED": "ABSETZEN",
    "CHK": "WAERMEN", "CTH": "BEREIT", "SOLK": "AUFFANGEN", "P": "EINFUELLEN",
    "LSH": "WASCHEN", "CFH": "AUSWRINGEN", "CH": "ABNEHMEN", "T": "EINTRAGEN",
    "K": "ZUDOSIEREN", "S": "TEILEN", "L": "WEITERLEITEN", "OL": "FORTSETZEN",
    "OT": "DANACH", "AL": "ZIEL", "AR": "QUELLE", "AIR": "LAUF", "OR": "ANSATZ",
    "HO": "ZUTAT", "CKH": "DURCHLASS", "O": "GANG", "Y": "DIES",
    "AIN": "PORTION", "AIIN": "MASS", "IIN": "STUFE", "E": "KURZ", "EE": "LANG",
    "EEE": "VOLL", "R": "KUEHLEN", "AN": "NACHGABE", "DA": "ZWEIT",
    "LD": "BEFESTIGEN", "DY": "SCHLUSS", "OS": "FACH",
    "RESUME_CARD": "WIEDERAUFNEHMEN", "TALAM": "VERWAHREN",
}

ANALOGUE = {
    "OPERATION_SIGN": "alchemistische und pseudo-lullische Operationszeichen",
    "STATE_OBJECT_SIGN": "medizinisch-alchemistische Fach- und Stoffzeichen",
    "RELATION_ADDRESS_SIGN": "tabellarische Adressen und kurze Kanzleioperatoren",
    "MEASURE_STAGE_SIGN": "Apotheker- Abakus- und Tabellenparameter",
    "BOUND_GRADE": "mensuraler gebundener Wertmodifier",
    "BOUND_ENDPOINT": "gelernte Endform einer Notationsfamilie",
    "DEICTIC_REFERENCE": "bildgestuetzte formularische Ellipse",
    "WHOLE_NOMENCLATOR": "diplomatischer Nomenklator und gelernte Brevigrafe",
}

RULE = {
    "OPERATION_SIGN": "als kurzes Verb im Bedeutungsrezept lernen",
    "STATE_OBJECT_SIGN": "als knappen Zustand oder Arbeitsgegenstand lernen; Besitzer konkretisiert",
    "RELATION_ADDRESS_SIGN": "Quelle Ziel oder Reihenfolge relativ zum aktiven Posten lesen",
    "MEASURE_STAGE_SIGN": "als unteilbaren Parameterwert lesen",
    "BOUND_GRADE": "nur an einer lizenzierten Basis als Grad lesen",
    "BOUND_ENDPOINT": "nur in einer lizenzierten exakten Endkarte als Schluss lesen",
    "DEICTIC_REFERENCE": "auf den aktuell gemeinten vom Bild oder Record gelieferten Posten zeigen",
    "WHOLE_NOMENCLATOR": "als ganze Karte lernen; innere Zeichen nicht zerlegen",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    roots = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_39_ROOT_TABLET.tsv")
    cards = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv")
    events = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_381_EVENT_INTERLINEAR.tsv")

    root_rows: list[dict[str, object]] = []
    for row in roots:
        component = row["component"]
        layer = LAYER[component]
        root_rows.append({
            "root_no": row["root_no"],
            "component": component,
            "old_value_de": row["short_value_de"],
            "compact_table_value_de": SHORT[component],
            "changed_for_teaching": "YES" if row["short_value_de"] != SHORT[component] else "NO",
            "historical_layer": layer,
            "closest_workshop_analogue": ANALOGUE[layer],
            "apprentice_rule": RULE[layer],
            "card_types": row["card_types"],
            "events_with_component": row["events_with_component"],
        })

    counts = Counter(row["historical_layer"] for row in root_rows)
    tray_order = [
        "OPERATION_SIGN", "STATE_OBJECT_SIGN", "RELATION_ADDRESS_SIGN", "MEASURE_STAGE_SIGN",
        "BOUND_GRADE", "BOUND_ENDPOINT", "DEICTIC_REFERENCE", "WHOLE_NOMENCLATOR",
    ]
    tray_rows = []
    for tray_no, layer in enumerate(tray_order, start=1):
        members = [row for row in root_rows if row["historical_layer"] == layer]
        tray_rows.append({
            "tray_no": tray_no,
            "historical_layer": layer,
            "entries": len(members),
            "components": " ".join(str(row["component"]) for row in members),
            "spoken_values_de": " | ".join(str(row["compact_table_value_de"]) for row in members),
            "teaching_rule": RULE[layer],
            "historical_analogue": ANALOGUE[layer],
        })

    card_rows = []
    for card in cards:
        components = card["component_recipe"].split("+")
        values = [SHORT[component] for component in components]
        layers = []
        for component in components:
            layer = LAYER[component]
            if layer not in layers:
                layers.append(layer)
        card_rows.append({
            "card_no": card["card_no"],
            "surfaces": card["surfaces"],
            "component_recipe": card["component_recipe"],
            "compact_atomic_reading_de": " · ".join(values),
            "historical_layers": "+".join(layers),
            "composition_mode": card["composition_mode"],
            "events": card["events"],
            "pages": card["pages"],
        })

    cards_by_no = {row["card_no"]: row for row in card_rows}
    event_rows = []
    for event in events:
        compact = cards_by_no[event["card_no"]]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "component_recipe": event["component_recipe"],
            "compact_atomic_reading_de": compact["compact_atomic_reading_de"],
            "historical_layers": compact["historical_layers"],
        })

    write("SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv", root_rows)
    write("SIX_HUNDRED_SEVENTY_NINTH_8_APPRENTICE_TRAYS.tsv", tray_rows)
    write("SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv", card_rows)
    write("SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv", event_rows)

    summary = {
        "status": "PASS",
        "root_entries": len(root_rows),
        "historical_layers": len(counts),
        "layer_counts": dict(sorted(counts.items())),
        "teaching_values_simplified": sum(row["changed_for_teaching"] == "YES" for row in root_rows),
        "card_types": len(card_rows),
        "events": len(event_rows),
        "selected_name": "BILDADRESSIERTER_FACHNOMENKLATOR",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
