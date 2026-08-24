#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P490 = ROOT / "experiments/yolo/sidequest_semantic_b3_double_check_transfer_four_hundred_ninetieth"

TARGET = "H1-S001"
MACRO = "PFLANZENAUSZUG ZWEIMAL ABZIEHEN UND DOSIEREN"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    target = [row for row in events if row["statement_id"] == TARGET]
    manual = read(P490 / "FOUR_HUNDRED_NINETIETH_169_ITEM_TWO_MACRO_MANUAL.tsv")
    ledger = read(P490 / "FOUR_HUNDRED_NINETIETH_776_TWO_MACRO_LEDGER.tsv")
    readings = {
        "E001": ("P1_PFLANZENANSATZ", "Kurz Material von der abgebildeten Pflanze abnehmen."),
        "E002": ("P1_PFLANZENANSATZ", "Aus diesem Material einen bereiten Pflanzenansatz setzen."),
        "E003": ("P1_PFLANZENANSATZ", "Aus dem laufenden Pflanzenansatz speisen."),
        "E004": ("P2_ERSTER_AUSZUG", "Den Pflanzenansatz in das Arbeitsfach füllen."),
        "E005": ("P2_ERSTER_AUSZUG", "Das örtlich gelernte Auszugsfach oder den Empfänger wählen."),
        "E006": ("P2_ERSTER_AUSZUG", "Die erste Laufflüssigkeit aus dem Arbeitsfach abziehen."),
        "E007": ("P3_ZWEITER_AUSZUG_UND_DOSIS", "Danach erneut füllen, weiter ausziehen und die zweite Fraktion gewinnen."),
        "E008": ("P3_ZWEITER_AUSZUG_UND_DOSIS", "Die zweite Auszugsfraktion verwenden."),
        "E009": ("P3_ZWEITER_AUSZUG_UND_DOSIS", "Die zweite Fraktion auf Sollmaß setzen."),
        "E010": ("P3_ZWEITER_AUSZUG_UND_DOSIS", "Die dosierte Auszugsfraktion kurz einfüllen oder ansetzen."),
    }
    trace = []
    for row in target:
        phase, revised = readings[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1, "event_id": row["event_id"], "locus": row["locus"],
            "field_id": row["field_id"], "surface": row["surface"], "component_parse": row["component_parse"],
            "macro_phase": phase, "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised, "state_transition": row["state_transition"],
            "owner_code": row["owner_code"], "closes_step": row["closes_step"],
        })
    write("FOUR_HUNDRED_NINETY_FIRST_10_EVENT_EXTRACTION_TRACE.tsv", trace)

    nodes = [
        {"node_id": "N1", "object_de": "Material der abgebildeten Pflanze", "created_at": "IMAGE_OWNER", "role": "SOURCE_MATERIAL"},
        {"node_id": "N2", "object_de": "abgenommene Pflanzenfraktion", "created_at": "E001", "role": "MATERIAL_FRACTION"},
        {"node_id": "N3", "object_de": "bereiter Pflanzenansatz", "created_at": "E002", "role": "EXTRACTION_BATCH"},
        {"node_id": "N4", "object_de": "gefülltes Auszugsfach", "created_at": "E004", "role": "WORK_COMPARTMENT"},
        {"node_id": "N5", "object_de": "erste abgezogene Laufflüssigkeit", "created_at": "E006", "role": "FIRST_EXTRACT"},
        {"node_id": "N6", "object_de": "zweite Auszugsfraktion", "created_at": "E007", "role": "SECOND_EXTRACT"},
        {"node_id": "N7", "object_de": "auf Sollmaß gesetzte Auszugsfraktion", "created_at": "E009", "role": "MEASURED_OUTPUT"},
        {"node_id": "N8", "object_de": "kurz eingesetzte Auszugsfraktion", "created_at": "E010", "role": "READY_FOR_NEXT_STEP"},
    ]
    write("FOUR_HUNDRED_NINETY_FIRST_EIGHT_EXTRACTION_OBJECTS.tsv", nodes)
    edges = [
        ("E001", "N1", "N2", "MATERIAL_ABNEHMEN"), ("E002", "N2", "N3", "ANSATZ_BEREITEN"),
        ("E003", "N3", "N3", "AUS_ANSATZ_SPEISEN"), ("E004", "N3", "N4", "ARBEITSFACH_FUELLEN"),
        ("E005", "N4", "N4", "AUSZUGSFACH_WAEHLEN"), ("E006", "N4", "N5", "ERSTEN_AUSZUG_ABZIEHEN"),
        ("E007", "N5", "N6", "ERNEUT_FUELLEN_UND_ZWEITEN_AUSZUG_ABZIEHEN"),
        ("E008", "N6", "N6", "ZWEITEN_AUSZUG_VERWENDEN"), ("E009", "N6", "N7", "SOLLWERT_SETZEN"),
        ("E010", "N7", "N8", "KURZ_EINSETZEN"),
    ]
    edge_rows = [{"edge_order": index + 1, "event_id": event, "source_object": source, "target_object": target_node, "operation": operation} for index, (event, source, target_node, operation) in enumerate(edges)]
    write("FOUR_HUNDRED_NINETY_FIRST_10_EXTRACTION_EDGES.tsv", edge_rows)

    candidates = [
        {"candidate": "A", "macro_name_de": MACRO, "plant_owner_fit": 5, "fill_draw_repeat_fit": 6, "measure_finish_fit": 5, "invented_content_cost": 1, "total": 15, "decision": "SELECT"},
        {"candidate": "B", "macro_name_de": "PFLANZENSAFT DOSIEREN UND KURZ ANWENDEN", "plant_owner_fit": 5, "fill_draw_repeat_fit": 3, "measure_finish_fit": 4, "invented_content_cost": 3, "total": 9, "decision": "RIVAL"},
        {"candidate": "C", "macro_name_de": "EIGENSCHAFTEN DER ABGEBILDETEN PFLANZE AUFZAEHLEN", "plant_owner_fit": 5, "fill_draw_repeat_fit": 0, "measure_finish_fit": 0, "invented_content_cost": 4, "total": 1, "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_NINETY_FIRST_THREE_HERBAL_MACRO_READINGS.tsv", candidates)

    comparison = [
        {"feature": "pictured_owner", "H1_S001": "WHOLE_PLANT", "B1_S002": "SHARED_POOL", "shared_supertype": "WET_PROCESS"},
        {"feature": "repeat_structure", "H1_S001": "FILL_DRAW_TWICE", "B1_S002": "TAKE_TWO_PORTIONS", "shared_supertype": "TWO_PASS_WET_PROCESS"},
        {"feature": "new_fraction_or_portion", "H1_S001": "EXTRACT_FRACTIONS", "B1_S002": "SIBLING_PORTIONS", "shared_supertype": "MATERIAL_DIVISION"},
        {"feature": "final_control", "H1_S001": "MEASURE_AND_SHORT_SET", "B1_S002": "SHORT_AND_LONG_HOLD", "shared_supertype": "CONTROLLED_OUTPUT"},
        {"feature": "same_exact_macro", "H1_S001": "NO", "B1_S002": "NO", "shared_supertype": "YES_ONLY_AT_TWO_PASS_WET_PROCESS"},
    ]
    write("FOUR_HUNDRED_NINETY_FIRST_H1_B1_TWO_PASS_COMPARISON.tsv", comparison)

    revised_manual = []
    for row in manual:
        new = dict(row)
        if row["item_id"] == "W:H1-S001":
            new["teaching_value_or_rule_de"] = MACRO + ": " + " ".join(item["revised_event_reading_de"] for item in trace)
            new["source_artifact"] = "PASS491_H1_DOUBLE_EXTRACTION"
        revised_manual.append(new)
    write("FOUR_HUNDRED_NINETY_FIRST_169_ITEM_THREE_MACRO_MANUAL.tsv", revised_manual)
    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "LOCAL_NOMENCLATOR_MACRO"
            new["syntax_item"] = "W:H1-S001"
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETY_FIRST_776_THREE_MACRO_LEDGER.tsv", revised_ledger)

    translation = (
        "Nimm kurz Material von der abgebildeten Pflanze und bereite daraus einen Ansatz. "
        "Speise den Ansatz in das örtliche Auszugsfach und ziehe die erste Laufflüssigkeit ab. "
        "Fülle danach erneut, ziehe die zweite Fraktion ab, verwende sie nach Sollmaß und setze sie kurz für den nächsten Schritt ein."
    )
    (HERE / "FOUR_HUNDRED_NINETY_FIRST_COMPLETE_H1_S001_READING.md").write_text(
        f"# {MACRO}\n\n{translation}\n\nDas Bild setzt das Pflanzenmaterial; Auszugsfach und Flüssigkeit stehen nur im Text und sind nicht gezeichnet.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": 3,
        "objects": len(nodes), "edges": len(edge_rows), "draw_cycles": 2, "selected_macro": MACRO,
        "plant_property_clause_rejected": True, "manual_items": len(revised_manual), "ledger_groups": len(revised_ledger),
        "macro_events_total": sum(row["local_macro"] != "NONE" for row in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
