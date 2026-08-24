#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P494 = ROOT / "experiments/yolo/sidequest_semantic_h3_wring_receive_four_hundred_ninety_fourth"
TARGET = "B3-S026"
MACRO = "QUELLPOSTEN BEMESSEN UND BEREITSTELLEN FOLGESTATION LANG AUFFANGEN"


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
    manual = read(P494 / "FOUR_HUNDRED_NINETY_FOURTH_168_ITEM_H3_DECOMPOSED_MANUAL.tsv")
    ledger = read(P494 / "FOUR_HUNDRED_NINETY_FOURTH_776_H3_DECOMPOSED_LEDGER.tsv")
    analysis = {
        "E285": ("A1_QUELLE_UND_MASS", "EE+AR", "STATION_A", "Länger aus der örtlichen Quelle führen."),
        "E286": ("A1_QUELLE_UND_MASS", "L+AIIN", "STATION_A", "Das Abführ-Sollmaß setzen."),
        "E287": ("A2_PORTION_BEREITSTELLEN", "CHD+Y", "STATION_A", "Den laufenden Stationsposten umsetzen."),
        "E288": ("A2_PORTION_BEREITSTELLEN", "OK+AIN", "STATION_A", "Eine Portion in den Arbeitsgang setzen."),
        "E289": ("A2_PORTION_BEREITSTELLEN", "CTH+Y", "STATION_A", "Den Stationsposten als bereit feststellen."),
        "E290": ("A2_PORTION_BEREITSTELLEN", "AL+R+OR", "STATION_A", "Den Ansatz an der örtlichen Zielstelle abkühlen."),
        "E291": ("B1_SEPARAT_AUFFANGEN", "SOLK+EE+DY", "STATION_B", "An der neuen sichtbaren Station länger auffangen und schließen."),
    }
    trace = []
    for row in target:
        phase, manual_item, station, revised = analysis[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1,
            "event_id": row["event_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "surface": row["surface"],
            "component_parse": row["component_parse"],
            "manual_item": manual_item,
            "macro_phase": phase,
            "station": station,
            "owner_code": row["owner_code"],
            "revised_event_reading_de": revised,
            "closes_step": row["closes_step"],
        })
    write("FOUR_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv", trace)

    boundary = [
        {"from_event": "E285", "to_event": "E286", "boundary": "SAME_LOCUS", "owner_action": "KEEP_STATION_A", "material_action": "KEEP", "syntax_action": "CONTINUE"},
        {"from_event": "E286", "to_event": "E287", "boundary": "SAME_LOCUS", "owner_action": "KEEP_STATION_A", "material_action": "KEEP", "syntax_action": "CONTINUE"},
        {"from_event": "E287", "to_event": "E288", "boundary": "SAME_LOCUS", "owner_action": "KEEP_STATION_A", "material_action": "KEEP", "syntax_action": "CONTINUE"},
        {"from_event": "E288", "to_event": "E289", "boundary": "SAME_LOCUS", "owner_action": "KEEP_STATION_A", "material_action": "KEEP", "syntax_action": "CONTINUE"},
        {"from_event": "E289", "to_event": "E290", "boundary": "SAME_LOCUS", "owner_action": "KEEP_STATION_A", "material_action": "KEEP", "syntax_action": "CONTINUE"},
        {"from_event": "E290", "to_event": "E291", "boundary": "VISIBLE_GAP_AND_LINE_JUMP", "owner_action": "RESET_TO_STATION_B", "material_action": "DO_NOT_CARRY", "syntax_action": "CONTINUE_WORKFLOW_ONLY"},
    ]
    write("FOUR_HUNDRED_NINETY_FIFTH_SIX_BOUNDARY_DECISIONS.tsv", boundary)

    objects = [
        {"object_id": "A0", "station": "STATION_A", "object_de": "örtliche Quelle", "created_at": "OWNER_A", "crosses_owner_gap": "NO"},
        {"object_id": "A1", "station": "STATION_A", "object_de": "bemessener Quellposten", "created_at": "E286", "crosses_owner_gap": "NO"},
        {"object_id": "A2", "station": "STATION_A", "object_de": "zugesetzter bereiter Ansatz", "created_at": "E289", "crosses_owner_gap": "NO"},
        {"object_id": "B0", "station": "STATION_B", "object_de": "örtlicher Auffangbestand unbekannter Herkunft", "created_at": "OWNER_RESET_E291", "crosses_owner_gap": "NO"},
        {"object_id": "B1", "station": "STATION_B", "object_de": "länger aufgefangener geschlossener Bestand", "created_at": "E291", "crosses_owner_gap": "NO"},
    ]
    write("FOUR_HUNDRED_NINETY_FIFTH_FIVE_LOCAL_OBJECTS.tsv", objects)

    candidates = [
        {"candidate": "A", "reading_de": MACRO, "component_fit": 7, "owner_reset_fit": 5, "invented_connection_cost": 0, "total": 12, "decision": "SELECT"},
        {"candidate": "B", "reading_de": "BEREITEN ANSATZ IN DAS UNTERE BECKEN ABLEITEN", "component_fit": 6, "owner_reset_fit": 1, "invented_connection_cost": 4, "total": 3, "decision": "REJECT_GLOBAL_FLOW"},
        {"candidate": "C", "reading_de": "DOSIERTE MEDIZIN BEREITEN UND IM BECKEN SAMMELN", "component_fit": 5, "owner_reset_fit": 2, "invented_connection_cost": 3, "total": 4, "decision": "LOCAL_MEDICAL_RIVAL"},
    ]
    write("FOUR_HUNDRED_NINETY_FIFTH_THREE_TWO_STATION_READINGS.tsv", candidates)

    revised_manual = []
    removed = 0
    for row in manual:
        if row["item_id"] == "W:B3-S026":
            removed += 1
            continue
        revised_manual.append(dict(row))
    for i, row in enumerate(revised_manual, 1):
        row["manual_order"] = str(i)
    write("FOUR_HUNDRED_NINETY_FIFTH_167_ITEM_TWO_STATION_MANUAL.tsv", revised_manual)

    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "COMPOSED_EXISTING_COMPONENT_CHAIN_WITH_OWNER_RESET"
            new["syntax_item"] = item["manual_item"]
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETY_FIFTH_776_TWO_STATION_LEDGER.tsv", revised_ledger)

    (HERE / "FOUR_HUNDRED_NINETY_FIFTH_COMPLETE_B3_S026_READING.md").write_text(
        "# " + MACRO + "\n\n"
        "Führe an der Randstation länger aus der örtlichen Quelle und setze das Abführ-Sollmaß. "
        "Setze den laufenden Stationsposten um, gib eine Portion hinzu, stelle Bereitschaft fest "
        "und kühle den Ansatz an der dortigen Zielstelle. Nach der großen sichtbaren Lücke beginnt "
        "eine neue Station: Fange dort länger auf und schließe.\n\n"
        "Nur die Arbeitsreihenfolge überquert die Lücke. Besitzer und Stoffbestand werden nicht übertragen.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "stations": 2,
        "owner_resets": sum(r["owner_action"].startswith("RESET") for r in boundary),
        "material_carries_across_reset": sum(r["material_action"] == "KEEP" and r["owner_action"].startswith("RESET") for r in boundary),
        "removed_local_whole_forms": removed, "manual_items_before": len(manual),
        "manual_items_after": len(revised_manual), "ledger_groups": len(revised_ledger),
        "macro_events_total": sum(r["local_macro"] != "NONE" for r in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
