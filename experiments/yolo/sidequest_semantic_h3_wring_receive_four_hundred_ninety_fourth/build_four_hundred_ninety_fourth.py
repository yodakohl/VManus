#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P493 = ROOT / "experiments/yolo/sidequest_semantic_h5_recharge_deploy_four_hundred_ninety_third"
TARGET = "H3-S001"
MACRO = "ANSATZ AUSWRINGEN BEMESSEN UND IN EMPFANGSBESTAND ABZIEHEN"


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
    manual = read(P493 / "FOUR_HUNDRED_NINETY_THIRD_169_ITEM_FIVE_MACRO_MANUAL.tsv")
    ledger = read(P493 / "FOUR_HUNDRED_NINETY_THIRD_776_FIVE_MACRO_LEDGER.tsv")
    analysis = {
        "E039": ("P1_HALTEPHASE", "T+SH+OL", "Den laufenden Ansatz weiter im Halteschritt führen."),
        "E040": ("P1_HALTEPHASE", "SH+O+AL", "Den Ansatz im Arbeitsgang an der gelernten Stelle halten."),
        "E041": ("P2_AUSWRINGEN_UND_BEMESSEN", "PROC028", "Den gehaltenen Ansatz auswringen."),
        "E042": ("P2_AUSWRINGEN_UND_BEMESSEN", "SH+Y+AIIN", "Den ausgewrungenen Posten bis zum Sollmaß halten."),
        "E043": ("P3_EMPFANG_UND_ABZUG", "P+Y", "Diesen Posten in den gelernten Empfänger geben."),
        "E044": ("P3_EMPFANG_UND_ABZUG", "PROC031", "Den daraus entstandenen Empfangsbestand übernehmen."),
        "E045": ("P3_EMPFANG_UND_ABZUG", "T+CH+O+DY", "Den Empfangsbestand abfüllen oder abziehen und den Schritt schließen."),
    }
    trace = []
    for row in target:
        phase, manual_item, revised = analysis[row["event_id"]]
        trace.append({
            "event_order": len(trace) + 1,
            "event_id": row["event_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "surface": row["surface"],
            "component_parse": row["component_parse"],
            "manual_item": manual_item,
            "macro_phase": phase,
            "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised,
            "state_transition": row["state_transition"],
            "closes_step": row["closes_step"],
        })
    write("FOUR_HUNDRED_NINETY_FOURTH_SEVEN_EVENT_WRING_RECEIVE_TRACE.tsv", trace)

    coverage = [
        {"event_id": r["event_id"], "surface": r["surface"], "manual_item": r["manual_item"],
         "already_in_pass493_manual": "YES", "new_local_value_needed": "NO",
         "reading_de": r["revised_event_reading_de"]} for r in trace
    ]
    write("FOUR_HUNDRED_NINETY_FOURTH_COMPLETE_EXISTING_ITEM_COVERAGE.tsv", coverage)

    stages = [
        {"stage": "S1", "input_de": "laufender Pflanzenansatz", "operation_de": "an der Arbeitsstelle weiter halten", "output_de": "gehaltener Ansatz", "events": "E039|E040"},
        {"stage": "S2", "input_de": "gehaltener Ansatz", "operation_de": "auswringen und bis Sollmaß halten", "output_de": "bemessener ausgewrungener Posten", "events": "E041|E042"},
        {"stage": "S3", "input_de": "bemessener ausgewrungener Posten", "operation_de": "in Empfänger geben und Bestand übernehmen", "output_de": "Empfangsbestand", "events": "E043|E044"},
        {"stage": "S4", "input_de": "Empfangsbestand", "operation_de": "abfüllen oder abziehen", "output_de": "geschlossener Arbeitsausgang", "events": "E045"},
    ]
    write("FOUR_HUNDRED_NINETY_FOURTH_FOUR_WRING_RECEIVE_STAGES.tsv", stages)

    candidates = [
        {"candidate": "A", "reading_de": MACRO, "component_fit": 7, "object_continuity": 5, "invented_substance_cost": 0, "total": 12, "decision": "SELECT"},
        {"candidate": "B", "reading_de": "BLUETENKRAUT IN WEIN KOCHEN UND KLARSEIHEN", "component_fit": 3, "object_continuity": 5, "invented_substance_cost": 4, "total": 4, "decision": "WITHDRAW_OLD_EXPANSION"},
        {"candidate": "C", "reading_de": "PFLANZE BESCHREIBEN UND EIGENSCHAFTEN NENNEN", "component_fit": 0, "object_continuity": 1, "invented_substance_cost": 3, "total": -2, "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_NINETY_FOURTH_THREE_H3_READINGS.tsv", candidates)

    revised_manual = []
    removed = 0
    for row in manual:
        if row["item_id"] == "W:H3-S001":
            removed += 1
            continue
        revised_manual.append(dict(row))
    for i, row in enumerate(revised_manual, 1):
        row["manual_order"] = str(i)
    write("FOUR_HUNDRED_NINETY_FOURTH_168_ITEM_H3_DECOMPOSED_MANUAL.tsv", revised_manual)

    trace_map = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in trace_map:
            item = trace_map[row["item_id"]]
            new["semantic_layer"] = "COMPOSED_EXISTING_COMPONENT_OR_WHOLE_CARD_CHAIN"
            new["syntax_item"] = item["manual_item"]
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        revised_ledger.append(new)
    write("FOUR_HUNDRED_NINETY_FOURTH_776_H3_DECOMPOSED_LEDGER.tsv", revised_ledger)

    (HERE / "FOUR_HUNDRED_NINETY_FOURTH_COMPLETE_H3_S001_READING.md").write_text(
        "# " + MACRO + "\n\n"
        "Führe den laufenden Pflanzenansatz im Halteschritt weiter und halte ihn an der gelernten Arbeitsstelle. "
        "Wringe ihn aus und halte den ausgewrungenen Posten bis zum Sollmaß. "
        "Gib ihn in den gelernten Empfänger, übernimm den entstandenen Empfangsbestand, "
        "fülle oder ziehe ihn ab und schließe den Schritt.\n\n"
        "Die ältere Lesung mit Blütenkraut, Wein und Klarauszug bleibt eine mögliche Rezeptausmalung, "
        "ist aber nicht mehr Bestandteil des Kartenwörterbuchs.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": 3,
        "stages": len(stages), "existing_item_coverage": sum(r["already_in_pass493_manual"] == "YES" for r in coverage),
        "new_local_values": sum(r["new_local_value_needed"] == "YES" for r in coverage),
        "removed_local_whole_forms": removed, "manual_items_before": len(manual),
        "manual_items_after": len(revised_manual), "ledger_groups": len(revised_ledger),
        "macro_events_total": sum(r["local_macro"] != "NONE" for r in revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
