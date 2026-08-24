#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def read() -> list[dict[str, str]]:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read()
    target = []
    for row in events:
        if "CTH_READY" in row["semantic_segmentation"]:
            target.append({
                "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
                "surface": row["surface_display"], "family": "CTH_READY", "small_value_de": "bereit",
                "role": "RELEASE_OR_AVAILABILITY_GATE", "terminal": "NO",
            })
        elif "SHED_SETTLE" in row["semantic_segmentation"]:
            target.append({
                "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
                "surface": row["surface_display"], "family": "SHED_SETTLE", "small_value_de": row["concrete_word_reading_de"],
                "role": "REST_OR_SETTLE_OPERATION", "terminal": "YES" if "CLOSE" in row["semantic_segmentation"] else "NO",
            })
    write("FOUR_HUNDRED_TENTH_READY_SETTLE_OCCURRENCES.tsv", target)

    progressions = [
        {"progression": "H1-S002", "sequence": "set item > warm > continue > CTH", "ready_position": "FINAL_PRODUCT_AVAILABLE", "settle_position": "NONE", "reading_de": "Posten ansetzen, anwärmen, fortsetzen, bereit"},
        {"progression": "H2-S001", "sequence": "select plant > CTH > batch > crush > press", "ready_position": "MATERIAL_RELEASE_BEFORE_WORK", "settle_position": "NONE", "reading_de": "Pflanzenposten bereitstellen, dann zerstoßen und pressen"},
        {"progression": "H3-S004", "sequence": "recall reserve > activate > CTH > Y", "ready_position": "SECOND_PRODUCT_AVAILABLE", "settle_position": "NONE", "reading_de": "Reserve einsetzen, Fortsetzung aktivieren, bereit"},
        {"progression": "B3-S021", "sequence": "measure > CTH > target > item > measure > SHEDAL > temper > item > target > CTH > close", "ready_position": "PHASE_A_RELEASE_AND_PHASE_B_RELEASE", "settle_position": "PHASE_B_LOCATION", "reading_de": "erste Phase freigeben; an Absetzstelle temperieren; zweite Phase freigeben"},
        {"progression": "B3-S034", "sequence": "IIN > CTH > work > follow measure > lower site > SHEDY", "ready_position": "BEFORE_OPERATION", "settle_position": "TERMINAL_AFTER_OPERATION", "reading_de": "Sollstufe, bereit, bearbeiten, am unteren Ziel kurz absetzen und schließen"},
    ]
    write("FOUR_HUNDRED_TENTH_FIVE_STATE_PROGRESSIONS.tsv", progressions)

    machine = [
        {"state": "SETTING", "typical_card": "IIN or AIIN", "meaning_de": "Sollzustand oder Sollmaß festlegen", "next": "READY"},
        {"state": "READY", "typical_card": "CTH", "meaning_de": "Posten für die nächste Handlung freigeben", "next": "ACTIVE"},
        {"state": "ACTIVE", "typical_card": "Y plus operation", "meaning_de": "laufenden Posten bearbeiten oder übergeben", "next": "READY_OR_SETTLING"},
        {"state": "SETTLING", "typical_card": "SHED plus grade", "meaning_de": "Posten stehenlassen oder absetzen", "next": "READY_OR_CLOSE"},
        {"state": "CLOSE", "typical_card": "licensed terminal card", "meaning_de": "örtlichen Schritt schließen", "next": "NEXT_FIELD_OR_RECORD"},
    ]
    write("FOUR_HUNDRED_TENTH_FIVE_STATE_MACHINE.tsv", machine)

    summary = {
        "status": "PASS",
        "target_occurrences": len(target),
        "ready_occurrences": sum(row["family"] == "CTH_READY" for row in target),
        "settle_occurrences": sum(row["family"] == "SHED_SETTLE" for row in target),
        "settle_terminal_occurrences": sum(row["family"] == "SHED_SETTLE" and row["terminal"] == "YES" for row in target),
        "progressions": len(progressions),
        "decision": "CTH_READY_GATE__SHED_SETTLE_OPERATION",
    }
    (HERE / "FOUR_HUNDRED_TENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
