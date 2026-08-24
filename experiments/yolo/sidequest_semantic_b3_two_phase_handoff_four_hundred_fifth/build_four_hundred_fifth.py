#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

TRACE = [
    ("E270", "PHASE_A", "SET_MEASURE", "erste Portion auf Sollmaß bringen"),
    ("E271", "PHASE_A", "CHECK_READY", "Bereitschaft der ersten Portion prüfen"),
    ("E272", "PHASE_A", "ASSIGN_TARGET", "erste Zielstelle wählen"),
    ("E273", "PHASE_A", "HAND_OFF_ITEM", "diesen Posten an Phase B übergeben"),
    ("E274", "PHASE_B", "SET_MEASURE", "übernommene Portion erneut bemessen"),
    ("E275", "PHASE_B", "SETTLE_AT_SITE", "an der Absetzstelle halten"),
    ("E276", "PHASE_B", "TEMPER", "auf temperierten Zustand bringen"),
    ("E277", "PHASE_B", "RESUME_ITEM", "diesen temperierten Posten aufnehmen"),
    ("E278", "PHASE_B", "ASSIGN_TARGET", "zweite Zielstelle wählen"),
    ("E279", "PHASE_B", "CHECK_READY", "Bereitschaft am Ziel prüfen"),
    ("E280", "PHASE_B", "LOCAL_TRANSFER_CLOSE", "örtlich umsetzen und den Gang schließen"),
]


def read() -> list[dict[str, str]]:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    by_id = {row["event_id"]: row for row in read()}
    rows = []
    for order, (event_id, phase, operation, reading) in enumerate(TRACE, 1):
        source = by_id[event_id]
        rows.append({
            "order": order,
            "event_id": event_id,
            "locus": source["locus"],
            "phase": phase,
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "operation": operation,
            "card_value_de": source["concrete_word_reading_de"],
            "working_reading_de": reading,
            "visible_owner": "UNRESOLVED_GAP_BETWEEN_MARGIN_AND_MAIN_PAIR",
        })
    write("FOUR_HUNDRED_FIFTH_11_EVENT_HANDOFF.tsv", rows)

    expansions = [
        {
            "model": "BATH_HANDOFF",
            "phase_a": "erste Badeportion abmessen, Bereitschaft prüfen, zum ersten Platz bringen",
            "handoff": "Badeportion an den Absetz-/Temperierplatz übergeben",
            "phase_b": "neu bemessen, abstehen und temperieren, zur Körper-/Badestelle bringen, freigeben",
            "score": 8,
            "reason": "nude figures and local vessels make bathing the best concrete fill",
        },
        {
            "model": "WORKSHOP_VESSEL_HANDOFF",
            "phase_a": "Charge im Vorratsgefäß abmessen und freigeben",
            "handoff": "Charge in ein Absetzgefäß überführen",
            "phase_b": "neu bemessen, temperieren, in den Empfänger umsetzen und schließen",
            "score": 7,
            "reason": "same grammar fits apparatus operation but owner at the text gap is not visibly connected",
        },
        {
            "model": "ONE_STATION_TWO_PHASES",
            "phase_a": "Sollmenge und Startzustand einstellen",
            "handoff": "same item continues across the line",
            "phase_b": "Absetzen, temperieren and locally release at the same station",
            "score": 6,
            "reason": "needs no second station and remains the strongest layout rival",
        },
    ]
    write("FOUR_HUNDRED_FIFTH_THREE_CONCRETE_EXPANSIONS.tsv", expansions)

    mirror = [
        {"role": "MEASURE", "phase_a_event": "E270", "phase_b_event": "E274", "phase_a_surface": "qokaiin", "phase_b_surface": "saiin", "small_value": "Sollmaß"},
        {"role": "READY", "phase_a_event": "E271", "phase_b_event": "E279", "phase_a_surface": "shcthy", "phase_b_surface": "shcthy", "small_value": "bereit"},
        {"role": "TARGET", "phase_a_event": "E272", "phase_b_event": "E278", "phase_a_surface": "dal", "phase_b_surface": "tal", "small_value": "Zielstelle"},
        {"role": "CURRENT_ITEM", "phase_a_event": "E273", "phase_b_event": "E277", "phase_a_surface": "sy", "phase_b_surface": "chey", "small_value": "dieser Posten"},
    ]
    write("FOUR_HUNDRED_FIFTH_FOUR_MIRRORED_ROLES.tsv", mirror)

    summary = {
        "status": "PASS",
        "events": len(rows),
        "phase_a_events": sum(row["phase"] == "PHASE_A" for row in rows),
        "phase_b_events": sum(row["phase"] == "PHASE_B" for row in rows),
        "mirrored_roles": len(mirror),
        "selected_model": "BATH_HANDOFF",
        "visible_owner": "UNRESOLVED",
    }
    (HERE / "FOUR_HUNDRED_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
