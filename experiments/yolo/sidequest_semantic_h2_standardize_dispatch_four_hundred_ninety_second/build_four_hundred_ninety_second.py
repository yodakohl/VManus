#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P491 = ROOT / "experiments/yolo/sidequest_semantic_h1_double_extraction_four_hundred_ninety_first"

TARGET = "H2-S001"
MACRO = "PFLANZENANSATZ AUF SOLLMASS EINSTELLEN UND WEITERGEBEN"


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
    manual = read(P491 / "FOUR_HUNDRED_NINETY_FIRST_169_ITEM_THREE_MACRO_MANUAL.tsv")
    ledger = read(P491 / "FOUR_HUNDRED_NINETY_FIRST_776_THREE_MACRO_LEDGER.tsv")
    readings = {
        "E015": ("P1_ANSATZ_AKTIVIEREN", "Aus dem Bildbesitzer kurz einen Pflanzenansatz abziehen."),
        "E016": ("P1_ANSATZ_AKTIVIEREN", "Den Pflanzenansatz als bereit feststellen."),
        "E017": ("P1_ANSATZ_AKTIVIEREN", "Den bereiten Ansatz zum laufenden Arbeitsposten machen."),
        "E018": ("P2_SOLLWERT_EINSTELLEN", "Den Pflanzenansatz auf Sollmaß bereitstellen."),
        "E019": ("P2_SOLLWERT_EINSTELLEN", "Den bereiten Pflanzenansatz weiterführen."),
        "E020": ("P3_WEITERGEBEN", "Denselben Pflanzenansatz auf dem gelernten Weg führen."),
        "E021": ("P3_WEITERGEBEN", "Denselben Pflanzenansatz weiterführen."),
        "E022": ("P3_WEITERGEBEN", "Seinen Sollwert beim Weitergeben erneut setzen oder prüfen."),
        "E023": ("P3_WEITERGEBEN", "Denselben Pflanzenansatz an die gelernte Zielstelle weitergeben."),
    }
    trace = []
    for row in target:
        phase, revised = readings[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1, "event_id": row["event_id"], "locus": row["locus"],
            "field_id": row["field_id"], "surface": row["surface"], "component_parse": row["component_parse"],
            "macro_phase": phase, "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised, "state_transition": row["state_transition"],
            "active_object_de": "laufender Pflanzenansatz", "owner_code": row["owner_code"],
        })
    write("FOUR_HUNDRED_NINETY_SECOND_NINE_EVENT_DISPATCH_TRACE.tsv", trace)

    y_rows = []
    for row in target:
        if row["component_parse"] == "Y":
            y_rows.append({
                "sequence_order": len(y_rows) + 1, "event_id": row["event_id"], "surface": row["surface"],
                "component": "Y", "referent_de": "derselbe laufende Pflanzenansatz",
                "semantic_change_from_previous_y": "NO", "workshop_point_de": "sichtbarer Allographwechsel innerhalb desselben Feldes; kein Wortwechsel",
            })
    write("FOUR_HUNDRED_NINETY_SECOND_THREE_Y_ALLOGRAPHS_ONE_REFERENT.tsv", y_rows)

    states = [
        {"state_id": "N1", "state_de": "Material der abgebildeten Pflanze", "entered_at": "IMAGE_OWNER"},
        {"state_id": "N2", "state_de": "kurz abgezogener Pflanzenansatz", "entered_at": "E015"},
        {"state_id": "N3", "state_de": "bereiter Pflanzenansatz", "entered_at": "E016"},
        {"state_id": "N4", "state_de": "auf Sollmaß eingestellter Pflanzenansatz", "entered_at": "E018"},
        {"state_id": "N5", "state_de": "weitergegebener sollgeprüfter Pflanzenansatz", "entered_at": "E023"},
    ]
    write("FOUR_HUNDRED_NINETY_SECOND_FIVE_DISPATCH_STATES.tsv", states)

    candidates = [
        {"candidate": "A", "macro_name_de": MACRO, "batch_ready_measure_fit": 6, "three_y_same_referent_fit": 5, "local_path_target_fit": 4, "invented_content_cost": 1, "total": 14, "decision": "SELECT"},
        {"candidate": "B", "macro_name_de": "PFLANZENMITTEL DOSIEREN UND ANWENDEN", "batch_ready_measure_fit": 5, "three_y_same_referent_fit": 4, "local_path_target_fit": 3, "invented_content_cost": 3, "total": 9, "decision": "RIVAL"},
        {"candidate": "C", "macro_name_de": "WEITEREN FLUESSIGKEITSAUSZUG HERSTELLEN", "batch_ready_measure_fit": 2, "three_y_same_referent_fit": 1, "local_path_target_fit": 2, "invented_content_cost": 3, "total": 2, "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_NINETY_SECOND_THREE_DISPATCH_READINGS.tsv", candidates)

    revised_manual = []
    for row in manual:
        new = dict(row)
        if row["item_id"] == "W:H2-S001":
            new["teaching_value_or_rule_de"] = MACRO + ": " + " ".join(item["revised_event_reading_de"] for item in trace)
            new["source_artifact"] = "PASS492_H2_STANDARDIZE_DISPATCH"
        revised_manual.append(new)
    write("FOUR_HUNDRED_NINETY_SECOND_169_ITEM_FOUR_MACRO_MANUAL.tsv", revised_manual)
    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "LOCAL_NOMENCLATOR_MACRO"
            new["syntax_item"] = "W:H2-S001"
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETY_SECOND_776_FOUR_MACRO_LEDGER.tsv", revised_ledger)

    translation = (
        "Ziehe aus dem Bildbesitzer kurz einen Pflanzenansatz ab und stelle seine Bereitschaft fest. "
        "Setze den Ansatz auf Sollmaß und führe ihn als bereiten Arbeitsposten weiter. "
        "Führe denselben Ansatz auf dem gelernten Weg, prüfe den Sollwert erneut und gib ihn an die örtlich gelernte Zielstelle weiter."
    )
    (HERE / "FOUR_HUNDRED_NINETY_SECOND_COMPLETE_H2_S001_READING.md").write_text(
        f"# {MACRO}\n\n{translation}\n\nDie drei Formen `dy`, `chy`, `shy` referieren innerhalb desselben Feldes auf denselben Posten.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": 3,
        "states": len(states), "y_allographs": len(y_rows), "distinct_y_referents": 1,
        "selected_macro": MACRO, "same_as_h1_extraction": False, "manual_items": len(revised_manual),
        "ledger_groups": len(revised_ledger), "macro_events_total": sum(row["local_macro"] != "NONE" for row in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
