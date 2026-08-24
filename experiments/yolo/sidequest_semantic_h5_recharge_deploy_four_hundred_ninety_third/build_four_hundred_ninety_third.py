#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P492 = ROOT / "experiments/yolo/sidequest_semantic_h2_standardize_dispatch_four_hundred_ninety_second"
TARGET = "H5-S001"
MACRO = "PFLANZENZUSATZ DOSIEREN NACHBESCHICKEN UND EINSETZEN"


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
    manual = read(P492 / "FOUR_HUNDRED_NINETY_SECOND_169_ITEM_FOUR_MACRO_MANUAL.tsv")
    ledger = read(P492 / "FOUR_HUNDRED_NINETY_SECOND_776_FOUR_MACRO_LEDGER.tsv")
    readings = {
        "E074": ("P1_ERSTE_DOSIERTE_BESCHICKUNG", "Aus dem Bildbesitzer einen Zusatzansatz abziehen."),
        "E075": ("P1_ERSTE_DOSIERTE_BESCHICKUNG", "Eine erste Pflanzenzutat nehmen."),
        "E076": ("P1_ERSTE_DOSIERTE_BESCHICKUNG", "Diese Zutat an die gelernte Arbeitsstelle bringen."),
        "E077": ("P1_ERSTE_DOSIERTE_BESCHICKUNG", "Die erste Beschickung auf Sollmaß setzen."),
        "E078": ("P2_NACHBESCHICKEN", "Eine weitere Pflanzenzutat nehmen."),
        "E079": ("P2_NACHBESCHICKEN", "Diese weitere Zutat in denselben Arbeitsgang zuführen."),
        "E080": ("P3_FOLGEANSATZ_EINSETZEN", "Danach den Folgeansatz abziehen oder bereitstellen."),
        "E081": ("P3_FOLGEANSATZ_EINSETZEN", "Diesen Folgeansatz einsetzen."),
        "E082": ("P3_FOLGEANSATZ_EINSETZEN", "Den Folgeansatz an die gelernte Zielstelle bringen."),
    }
    trace = []
    for row in target:
        phase, revised = readings[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1,
            "event_id": row["event_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "surface": row["surface"],
            "component_parse": row["component_parse"],
            "macro_phase": phase,
            "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised,
            "state_transition": row["state_transition"],
            "owner_code": row["owner_code"],
        })
    write("FOUR_HUNDRED_NINETY_THIRD_NINE_EVENT_RECHARGE_TRACE.tsv", trace)

    ingredient_allographs = []
    for row in target:
        if row["component_parse"] == "HO":
            ingredient_allographs.append({
                "sequence_order": len(ingredient_allographs) + 1,
                "event_id": row["event_id"],
                "surface": row["surface"],
                "component": "HO",
                "role_de": "Pflanzenzutat in einer eigenen Beschickungsphase",
                "same_exact_card": "YES",
                "same_material_required": "NO__SAME_INGREDIENT_CLASS_ONLY",
            })
    write("FOUR_HUNDRED_NINETY_THIRD_CHO_SHO_INGREDIENT_ALLOGRAPHS.tsv", ingredient_allographs)

    objects = [
        {"node_id": "N1", "object_de": "abgebildete ganze Pflanze", "created_at": "IMAGE_OWNER", "role": "SOURCE_OWNER"},
        {"node_id": "N2", "object_de": "Zusatzansatz", "created_at": "E074", "role": "ADDITION_BATCH"},
        {"node_id": "N3", "object_de": "erste Pflanzenzutat", "created_at": "E075", "role": "FIRST_ADDITION"},
        {"node_id": "N4", "object_de": "dosierte erste Beschickung", "created_at": "E077", "role": "MEASURED_FIRST_CHARGE"},
        {"node_id": "N5", "object_de": "weitere Pflanzenzutat", "created_at": "E078", "role": "SECOND_ADDITION"},
        {"node_id": "N6", "object_de": "nachbeschickter Folgeansatz", "created_at": "E080", "role": "FOLLOWING_BATCH"},
        {"node_id": "N7", "object_de": "am Ziel eingesetzter Folgeansatz", "created_at": "E082", "role": "DEPLOYED_OUTPUT"},
    ]
    write("FOUR_HUNDRED_NINETY_THIRD_SEVEN_RECHARGE_OBJECTS.tsv", objects)

    candidates = [
        {"candidate": "A", "macro_name_de": MACRO, "two_charge_fit": 6, "measure_then_follow_batch_fit": 6, "target_deploy_fit": 5, "invented_content_cost": 1, "total": 16, "decision": "SELECT"},
        {"candidate": "B", "macro_name_de": "ZWEI PFLANZENTEILE SAMMELN UND ANWENDEN", "two_charge_fit": 5, "measure_then_follow_batch_fit": 3, "target_deploy_fit": 4, "invented_content_cost": 3, "total": 9, "decision": "RIVAL"},
        {"candidate": "C", "macro_name_de": "EINEN WEITEREN PFLANZENAUSZUG HERSTELLEN", "two_charge_fit": 1, "measure_then_follow_batch_fit": 2, "target_deploy_fit": 2, "invented_content_cost": 2, "total": 3, "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_NINETY_THIRD_THREE_H5_MACRO_READINGS.tsv", candidates)

    comparison = [
        {"feature": "first_transition", "H1_S001": "MATERIAL_FRACTION", "H2_S001": "READY_PREPARATION", "H5_S001": "ADDITION_BATCH"},
        {"feature": "repeat", "H1_S001": "FILL_DRAW_TWICE", "H2_S001": "MEASURE_CHECK_TWICE", "H5_S001": "INGREDIENT_CHARGE_TWICE"},
        {"feature": "new_object", "H1_S001": "SECOND_EXTRACT", "H2_S001": "NONE", "H5_S001": "FOLLOWING_BATCH"},
        {"feature": "finish", "H1_S001": "MEASURE_SHORT_SET", "H2_S001": "DISPATCH", "H5_S001": "DEPLOY_AT_TARGET"},
        {"feature": "same_macro", "H1_S001": "NO", "H2_S001": "NO", "H5_S001": "NO"},
    ]
    write("FOUR_HUNDRED_NINETY_THIRD_THREE_HERBAL_MACRO_COMPARISON.tsv", comparison)

    revised_manual = []
    for row in manual:
        new = dict(row)
        if row["item_id"] == "W:H5-S001":
            new["teaching_value_or_rule_de"] = MACRO + ": " + " ".join(item["revised_event_reading_de"] for item in trace)
            new["source_artifact"] = "PASS493_H5_RECHARGE_DEPLOY"
        revised_manual.append(new)
    write("FOUR_HUNDRED_NINETY_THIRD_169_ITEM_FIVE_MACRO_MANUAL.tsv", revised_manual)

    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "LOCAL_NOMENCLATOR_MACRO"
            new["syntax_item"] = "W:H5-S001"
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETY_THIRD_776_FIVE_MACRO_LEDGER.tsv", revised_ledger)

    (HERE / "FOUR_HUNDRED_NINETY_THIRD_COMPLETE_H5_S001_READING.md").write_text(
        "# " + MACRO + "\n\n"
        "Ziehe aus der abgebildeten Pflanze einen Zusatzansatz ab. Nimm eine erste Pflanzenzutat, "
        "bringe sie an die gelernte Arbeitsstelle und setze die Beschickung auf Sollmaß. "
        "Nimm eine weitere Pflanzenzutat und führe sie demselben Arbeitsgang zu. "
        "Stelle danach den Folgeansatz bereit, setze ihn ein und bringe ihn an die örtlich gelernte Zielstelle.\n\n"
        "`cho` und `sho` sind dieselbe HO-Karte in zwei aufeinanderfolgenden Beschickungsphasen. "
        "Das Bild bestimmt die ganze Pflanze, aber nicht zwei bestimmte sichtbare Pflanzenteile.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": 3,
        "objects": len(objects), "ingredient_allographs": len(ingredient_allographs),
        "selected_macro": MACRO, "manual_items": len(revised_manual), "ledger_groups": len(revised_ledger),
        "macro_events_total": sum(row["local_macro"] != "NONE" for row in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
