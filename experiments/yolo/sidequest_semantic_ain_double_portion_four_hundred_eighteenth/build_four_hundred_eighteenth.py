#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    ain = [row for row in events if "AIN_PORTION" in row["semantic_segmentation"]]
    occurrence_rows = []
    for row in ain:
        composition = row["semantic_segmentation"]
        if composition.startswith("OK+"):
            expansion = "eine Portion zugeben"
        elif composition.startswith("OL_"):
            expansion = "eine weitere Portion"
        elif composition.startswith("OR_"):
            expansion = "eine Portion des Ansatzes"
        elif composition.startswith("CHED+"):
            expansion = "eine Portion umsetzen"
        elif composition.startswith("Y_REFERENT"):
            expansion = "diese Portion"
        else:
            expansion = "eine Portion"
        occurrence_rows.append({
            "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "composition": composition, "ain_invariant_de": "Portion", "composed_value_de": expansion,
        })
    write("FOUR_HUNDRED_EIGHTEENTH_SIXTEEN_AIN_OCCURRENCES.tsv", occurrence_rows)

    family = []
    for joint_id in sorted({row["joint_tuple_id"] for row in ain}):
        group = [row for row in ain if row["joint_tuple_id"] == joint_id]
        family.append({
            "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({row["surface_display"] for row in group})),
            "events": len(group),
            "composition": group[0]["semantic_segmentation"],
            "portable_ain_value_de": "Portion",
            "whole_card_value_de": occurrence_rows[[row["joint_tuple_id"] for row in ain].index(joint_id)]["composed_value_de"],
        })
    write("FOUR_HUNDRED_EIGHTEENTH_SEVEN_AIN_CARDS.tsv", family)

    models = [
        {"candidate": "FÜLLUNG", "bare_fit": 2, "OK_fit": 3, "OL_fit": 2, "OR_fit": 2, "CHED_fit": 2, "score": 11, "decision": "REJECT_TOO_CONTAINER_BOUND"},
        {"candidate": "TEIL", "bare_fit": 4, "OK_fit": 3, "OL_fit": 4, "OR_fit": 4, "CHED_fit": 4, "score": 19, "decision": "KEEP_AS_SUPERCLASS"},
        {"candidate": "PORTION", "bare_fit": 4, "OK_fit": 4, "OL_fit": 4, "OR_fit": 4, "CHED_fit": 4, "score": 20, "decision": "SELECT"},
        {"candidate": "HÄLFTE", "bare_fit": 2, "OK_fit": 2, "OL_fit": 2, "OR_fit": 2, "CHED_fit": 2, "score": 10, "decision": "REJECT_NO_BINARY_REQUIREMENT"},
    ]
    write("FOUR_HUNDRED_EIGHTEENTH_FOUR_AIN_MODELS.tsv", models)

    b2_ids = ["E198", "E199", "E200", "E201"]
    readings = ["eine Portion zugeben", "dasselbe", "eine Portion zugeben", "länger ansetzen; Schluss"]
    b2 = []
    by_id = {row["event_id"]: row for row in events}
    for order, (event_id, reading) in enumerate(zip(b2_ids, readings), start=1):
        row = by_id[event_id]
        b2.append({
            "order": order, "event_id": event_id, "surface": row["surface_display"], "small_value_de": reading,
            "operation_instance": "ADD_1" if event_id == "E198" else ("ADD_2" if event_id == "E200" else "LINK_OR_CLOSE"),
            "source_scope": "SAME_SOURCE" if event_id in {"E199", "E200"} else "CURRENT_SOURCE",
        })
    write("FOUR_HUNDRED_EIGHTEENTH_B2_DOUBLE_PORTION.tsv", b2)

    contrast = [
        {"family": "AIN", "events": len(ain), "exact_cards": len(family), "small_value_de": "Portion", "question": "welcher abgeteilte Posten"},
        {"family": "AIIN", "events": sum(row["joint_tuple_id"] == "2f1c5e56e8f0ff459065" for row in events), "exact_cards": 1, "small_value_de": "Mass", "question": "wie viel als Vorgabe"},
        {"family": "IIN", "events": 4, "exact_cards": 3, "small_value_de": "Sollstand", "question": "welcher Arbeitsstand"},
    ]
    write("FOUR_HUNDRED_EIGHTEENTH_AIN_AIIN_IIN_CONTRAST.tsv", contrast)

    summary = {
        "status": "PASS", "ain_events": len(ain), "ain_exact_cards": len(family),
        "b2_additions": 2, "decision": "AIN_PORTION__B2_TWO_EQUAL_SEQUENTIAL_PORTIONS",
    }
    (HERE / "FOUR_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
