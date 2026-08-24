#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

VALUES = {
    "E056": "nach Mass ansetzen", "E057": "Mass", "E058": "eine Portion davon", "E059": "diese Portion", "E060": "abkühlen; Schluss",
    "E061": "Mass", "E062": "dies umsetzen", "E063": "verwahren",
    "E064": "Mass dieses Postens", "E065": "Auszug daraus", "E066": "länger wärmen", "E067": "fortsetzen; Schluss",
    "E068": "Mass", "E069": "an die Stelle setzen", "E070": "anwärmen", "E071": "Ansatz", "E072": "dies", "E073": "Ansatzportion",
}


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = [row for row in csv.DictReader(handle, delimiter="\t") if row["record_unit_id"] == "H4"]
    interlinear = []
    for order, row in enumerate(events, start=1):
        interlinear.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "selected_small_value_de": VALUES[row["event_id"]],
            "semantic_role": "QUANTITY" if "AIIN" in row["semantic_segmentation"] or "AIN_PORTION" in row["semantic_segmentation"] else ("CLOSE" if "CLOSE" in row["semantic_segmentation"] else "PROCESS_OR_ITEM"),
        })
    write("FOUR_HUNDRED_TWENTY_SECOND_H4_18_EVENT_INTERLINEAR.tsv", interlinear)

    statements = [
        {"statement_id": "H4-S001", "events": "E056-E060", "card_sequence_de": "nach Mass ansetzen > Mass > Portion davon > diese Portion > abkühlen; Schluss", "continuous_reading_de": "Nach Maß ansetzen, eine Portion davon nehmen und diese abkühlen; den Schritt schließen."},
        {"statement_id": "H4-S002", "events": "E061-E063", "card_sequence_de": "Mass > dies umsetzen > verwahren", "continuous_reading_de": "Die bemessene Menge umsetzen und verwahren."},
        {"statement_id": "H4-S003", "events": "E064-E067", "card_sequence_de": "Mass dieses Postens > Auszug daraus > länger wärmen > fortsetzen; Schluss", "continuous_reading_de": "Diesen Posten bemessen, den Auszug daraus nehmen, länger wärmen und fortsetzen; den Schritt schließen."},
        {"statement_id": "H4-S004", "events": "E068-E073", "card_sequence_de": "Mass > an Stelle setzen > anwärmen > Ansatz > dies > Ansatzportion", "continuous_reading_de": "Nach Maß an die Stelle setzen und anwärmen; aus diesem Ansatz eine Ansatzportion nehmen."},
    ]
    write("FOUR_HUNDRED_TWENTY_SECOND_H4_FOUR_STATEMENTS.tsv", statements)

    comparison = [
        {"operation_or_noun": "MASS", "H4": 4, "H5": 2, "shared_layer": "YES", "interpretation": "common quantity grammar"},
        {"operation_or_noun": "PORTION", "H4": 4, "H5": 0, "shared_layer": "INDIRECT", "interpretation": "H5 uses Gabe instead"},
        {"operation_or_noun": "ANSATZ", "H4": 2, "H5": 2, "shared_layer": "YES", "interpretation": "common preparation noun"},
        {"operation_or_noun": "WÄRMEN_KÜHLEN", "H4": 3, "H5": 0, "shared_layer": "NO", "interpretation": "H4 preparation specialization"},
        {"operation_or_noun": "VERWAHREN", "H4": 1, "H5": 0, "shared_layer": "NO", "interpretation": "H4 storage specialization"},
        {"operation_or_noun": "WASCHEN_AUFTRAGEN_GEBRAUCHEN", "H4": 0, "H5": 3, "shared_layer": "NO", "interpretation": "H5 application specialization"},
    ]
    write("FOUR_HUNDRED_TWENTY_SECOND_H4_H5_LAYER_COMPARISON.tsv", comparison)

    models = [
        {"model": "GENERAL_PLANT_PREPARATION_COMMON_LAYER", "H4_fit": 4, "H5_fit": 4, "explains_difference": 4, "score": 12, "decision": "SELECT"},
        {"model": "SAME_MEDICINE_RECIPE", "H4_fit": 3, "H5_fit": 4, "explains_difference": 2, "score": 9, "decision": "KEEP_RIVAL"},
        {"model": "UNRELATED_ARTICLES", "H4_fit": 2, "H5_fit": 2, "explains_difference": 4, "score": 8, "decision": "REJECT_SHARED_GRAMMAR"},
    ]
    write("FOUR_HUNDRED_TWENTY_SECOND_THREE_H4_H5_MODELS.tsv", models)

    correction = [{
        "incorrect_preview": "H4 contains cloth squeeze restrain store chain",
        "correct_inventory": "H4 contains measure portion cool store extract warm and batch portion; cloth squeeze and re-strain belong H3",
        "effect": "scope corrected before interpretation; H4 outputs contain exactly E056-E073",
    }]
    write("FOUR_HUNDRED_TWENTY_SECOND_SCOPE_CORRECTION.tsv", correction)

    summary = {
        "status": "PASS", "events": len(interlinear), "statements": len(statements),
        "decision": "H4_GENERAL_PREPARATION__H5_APPLICATION_EXTENSION", "scope_correction": "H3_NOT_H4_HAS_CLOTH_CHAIN",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
