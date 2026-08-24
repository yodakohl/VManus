#!/usr/bin/env python3
"""Build Pass 711: resolve qotchedy/otchedy versus otchdy doublet."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TARGET_CARDS = {"PROC145", "PROC166"}
CONTROL_CARDS = {"PROC076", "PROC094", "PROC082", "PROC091", "PROC145", "PROC166"}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    statements = read(P700 / "SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")
    statement_by_id = {row["statement_id"]: row for row in statements}

    target_rows = []
    control_rows = []
    for event in events:
        if event["card_no"] not in CONTROL_CARDS:
            continue
        statement = statement_by_id[event["statement_id"]]
        has_joint_e = "YES" if "CHD_JOINT" in event["renderer_rules"] else "NO"
        row = {
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "statement_id": event["statement_id"], "locus": event["locus"],
            "owner_de": event["owner_de"], "card_no": event["card_no"],
            "component_recipe": event["component_recipe"], "surface": event["observed_surface"],
            "entry_frame": event["entry_frame"], "has_chd_joint_e": has_joint_e,
            "renderer_rules": event["renderer_rules"], "surface_selection_layer": event["surface_selection_layer"],
            "statement_events": statement["events"], "statement_reading_de": statement["working_reading_de"],
        }
        control_rows.append(row)
        if event["card_no"] in TARGET_CARDS:
            target_rows.append({
                **row,
                "merged_semantic_family": "OT_CHD_DY_CLOSE",
                "merged_reading_de": "DANACH · UMSETZEN · SCHLUSS",
                "local_renderer_subfamily": "B3_E_JOINT" if event["record"] == "B3" else "B5_COMPACT",
            })

    model_rows = [
        {"model": "M1_SEMANTIC_SPLIT", "fits_target_3": "NO", "fits_controls_13": "NO", "cost": 2, "assessment_de": "Keine Inhaltsdifferenz in Docket, Komponenten oder Ruecklesung; verworfen."},
        {"model": "M2_ENTRY_FRAME_ONLY", "fits_target_3": "NO", "fits_controls_13": "NO", "cost": 1, "assessment_de": "PROC145 hat q und bare mit e; PROC166 bare ohne e. Bare allein entscheidet nicht."},
        {"model": "M3_GLOBAL_CHD_E_RULE", "fits_target_3": "NO", "fits_controls_13": "NO", "cost": 1, "assessment_de": "Verwandte CHD- und OK+CHD-Schlussfamilien mischen e und kein e sogar innerhalb B1/B3."},
        {"model": "M4_LOCAL_RECORD_RENDERER", "fits_target_3": "YES", "fits_controls_13": "LOCAL_ONLY", "cost": 1, "assessment_de": "B3-Hauptrecord nimmt fuer OT+CHD+DY die e-Fuge; B5-Nachtrag die kompakte Form."},
        {"model": "M5_TWO_MEMORIZED_SEMANTIC_CARDS", "fits_target_3": "YES", "fits_controls_13": "YES", "cost": 2, "assessment_de": "Technisch moeglich, aber doppelt dieselbe Bedeutung und Docketadresse."},
    ]

    rule_rows = [
        {"rule_id": "OTCLOSE-1", "condition": "recipe=OT+CHD+DY AND record=B3", "semantic_family": "OT_CHD_DY_CLOSE", "renderer_choice": "E_JOINT", "surface_options": "qotchedy|otchedy", "apprentice_action_de": "B3-Schublade oeffnen; e-Fuge kopieren; q nur nach lokalem Eintrittsrahmen."},
        {"rule_id": "OTCLOSE-2", "condition": "recipe=OT+CHD+DY AND record=B5", "semantic_family": "OT_CHD_DY_CLOSE", "renderer_choice": "COMPACT_NO_E", "surface_options": "otchdy", "apprentice_action_de": "B5-Nachtragsschublade oeffnen; kompakte Ganzform kopieren."},
        {"rule_id": "OTCLOSE-3", "condition": "recipe=OT+CHD+DY AND other/unseen owner", "semantic_family": "OT_CHD_DY_CLOSE", "renderer_choice": "MASTER_EXEMPLAR_REQUIRED", "surface_options": "NONE_AUTOMATIC", "apprentice_action_de": "Keine globale e-Regel erfinden; Meisterexemplar fragen."},
    ]

    resolution_rows = [
        {"docket_signature": "- || - || CHD || - || OT || DY", "old_exact_card_families": "PROC145|PROC166", "new_semantic_family": "OT_CHD_DY_CLOSE", "semantic_ambiguity_after_merge": "NO", "remaining_copy_choice": "B3_E_JOINT_OR_B5_COMPACT", "remaining_choice_source": "record/owner drawer"},
    ]

    write("SEVEN_HUNDRED_ELEVENTH_3_DOUBLE_OCCURRENCES.tsv", target_rows)
    write("SEVEN_HUNDRED_ELEVENTH_13_CHD_CLOSE_CONTROLS.tsv", control_rows)
    write("SEVEN_HUNDRED_ELEVENTH_5_MODEL_COMPARISON.tsv", model_rows)
    write("SEVEN_HUNDRED_ELEVENTH_3_SELECTION_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_ELEVENTH_DOCKET_RESOLUTION.tsv", resolution_rows)

    summary = {
        "status": "PASS", "target_occurrences": len(target_rows), "control_occurrences": len(control_rows),
        "target_b3_e_joint": sum(row["record"] == "B3" and row["has_chd_joint_e"] == "YES" for row in target_rows),
        "target_b5_compact": sum(row["record"] == "B5" and row["has_chd_joint_e"] == "NO" for row in target_rows),
        "control_e_joint": sum(row["has_chd_joint_e"] == "YES" for row in control_rows),
        "control_compact": sum(row["has_chd_joint_e"] == "NO" for row in control_rows),
        "semantic_families_before": 2, "semantic_families_after": 1,
        "exact_card_ids_preserved_for_copying": 2,
        "decision": "ONE_OT_CHD_DY_SEMANTIC_RECIPE_WITH_B3_E_JOINT_AND_B5_COMPACT_LOCAL_RENDERERS",
    }
    (HERE / "SEVEN_HUNDRED_ELEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
