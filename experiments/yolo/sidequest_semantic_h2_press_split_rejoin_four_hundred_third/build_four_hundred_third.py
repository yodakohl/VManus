#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

CRITICAL = {
    "E018": ("CRUSH", "PLANT_MASS", "CRUSHED_PLANT_MASS", "Kraut zerstoßen"),
    "E019": ("PRESS_SPLIT", "CRUSHED_PLANT_MASS", "PRESS_PAIR", "in Flüssigkeit und Pressmasse trennen"),
    "E020": ("OPEN_REFERENT_1", "PRESS_PAIR", "PRESSED_LIQUID", "ausgepresste Flüssigkeit als Posten 1"),
    "E021": ("OPEN_REFERENT_2", "PRESS_PAIR", "PRESSED_PLANT_MASS", "feuchte Pressmasse als Posten 2"),
    "E022": ("BIND_PAIR_MEASURE", "PRESSED_LIQUID|PRESSED_PLANT_MASS", "MEASURED_PRESS_PAIR", "Sollverhältnis der zwei Pressposten setzen"),
    "E023": ("KEEP_PAIR_ACTIVE", "MEASURED_PRESS_PAIR", "ACTIVE_PRESS_PAIR", "das abgemessene Paar weiterführen"),
    "E028": ("RECALL_PREVIOUS_BRANCH", "FOLLOW_ON_BATCH", "TWO_ACTIVE_PREPARATIONS", "vorigen Zweig wieder hinzunehmen"),
    "E033": ("RECALL_PREPARATION_1", "TWO_ACTIVE_PREPARATIONS", "FOLLOW_ON_PREPARATION", "Folgezubereitung in das Gefäß setzen"),
    "E034": ("RECALL_PREPARATION_2", "TWO_ACTIVE_PREPARATIONS", "PRIMARY_PREPARATION", "vorige Presszubereitung in das Gefäß setzen"),
    "E035": ("COLLAPSE_TO_CURRENT", "FOLLOW_ON_PREPARATION|PRIMARY_PREPARATION", "COMBINED_VESSEL_ITEM", "beide als einen Gefäßposten weiterführen"),
}


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
    critical_rows = []
    for event_id, (operation, before, after, reading) in CRITICAL.items():
        source = by_id[event_id]
        critical_rows.append({
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "operation": operation,
            "register_before": before,
            "register_after": after,
            "working_reading_de": reading,
        })
    write("FOUR_HUNDRED_THIRD_TEN_CRITICAL_EVENTS.tsv", critical_rows)

    pair_rows = [
        {"pair": "Y_Y", "events": "E020|E021", "position": "IMMEDIATELY_AFTER_PRESS", "single_value": "dieser Posten", "pair_value": "zwei Pressposten", "candidate_instances": "ausgepresste Flüssigkeit|feuchte Pressmasse", "following_collapse": "E023 Y keeps pair active"},
        {"pair": "OR_OR", "events": "E033|E034", "position": "AFTER_VESSEL_CARD", "single_value": "Ansatz", "pair_value": "zwei Ansätze", "candidate_instances": "Folgezubereitung|vorige Presszubereitung", "following_collapse": "E035 Y resumes combined vessel item"},
    ]
    write("FOUR_HUNDRED_THIRD_TWO_PARALLEL_PAIRS.tsv", pair_rows)

    candidates = [
        ("C1_PRESS_LIQUID_AND_CAKE", "Pressflüssigkeit", "feuchte Pressmasse", "two derived preparations", "SELECTED", "pressing naturally makes two work objects and final soft application can recombine them"),
        ("C2_TWO_PORTIONS_OF_LIQUID", "erste Flüssigkeitsportion", "zweite Flüssigkeitsportion", "two portions", "LIVE_RIVAL", "fits duplication but underuses the press residue"),
        ("C3_ACTIVE_AND_RESERVE", "aktiver Pressauszug", "zurückgelegter Pressauszug", "active and reserve", "LIVE_RIVAL", "fits later previous/current registers but lacks H3-style reserve cards"),
        ("C4_ONE_ITEM_REASSERTED", "derselbe Pressauszug", "derselbe Pressauszug", "one reiterated item", "WEAKEST", "does not explain paired open-slot grammar"),
    ]
    write("FOUR_HUNDRED_THIRD_FOUR_SPLIT_MODELS.tsv", [
        {"model": model, "y_slot_1": one, "y_slot_2": two, "later_or_pair": later, "decision": decision, "reason": reason}
        for model, one, two, later, decision, reason in candidates
    ])

    graph = [
        ("PICTURED_PLANT", "CRUSHED_PLANT_MASS", "CRUSH"),
        ("CRUSHED_PLANT_MASS", "PRESSED_LIQUID", "PRESS_OUTPUT_1"),
        ("CRUSHED_PLANT_MASS", "PRESSED_PLANT_MASS", "PRESS_OUTPUT_2"),
        ("PRESSED_LIQUID", "FOLLOW_ON_PREPARATION", "PROCESS_CURRENT_BRANCH"),
        ("PRESSED_PLANT_MASS", "PRIMARY_PREPARATION", "PROCESS_PREVIOUS_BRANCH"),
        ("FOLLOW_ON_PREPARATION", "COMBINED_VESSEL_ITEM", "OR_SLOT_1"),
        ("PRIMARY_PREPARATION", "COMBINED_VESSEL_ITEM", "OR_SLOT_2"),
        ("COMBINED_VESSEL_ITEM", "SOFT_EXTERNAL_APPLICATION", "SOFTEN_AND_APPLY"),
    ]
    write("FOUR_HUNDRED_THIRD_EIGHT_FLOW_EDGES.tsv", [
        {"from_node": source, "to_node": target, "relation": relation}
        for source, target, relation in graph
    ])

    summary = {
        "status": "PASS",
        "critical_events": len(critical_rows),
        "parallel_pairs": len(pair_rows),
        "models": len(candidates),
        "flow_edges": len(graph),
        "decision": "PRESS_SPLIT_TWO_REFERENTS_THEN_OR_PAIR_REJOIN",
    }
    (HERE / "FOUR_HUNDRED_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
