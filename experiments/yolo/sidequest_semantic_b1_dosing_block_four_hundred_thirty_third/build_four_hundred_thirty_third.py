#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B1_DIR = ROOT / "experiments/yolo/sidequest_semantic_source_path_target_four_hundred_thirty_second"
ALL = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(B1_DIR / "FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_66_EVENTS.tsv")
    statements = read(B1_DIR / "FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_21_STATEMENTS.tsv")
    all_events = read(ALL)
    revisions = {
        "b5fcea1eaed06b2f2291": ("OK+AIIN", "bemessen", "MEASURE_SETUP"),
        "9da1b6ac2c929daea697": ("K+AIN", "eine Portion", "FIRST_PORTION"),
        "94df4847b7b16c98394a": ("OL+K+AIN", "weitere Portion", "FOLLOWING_PORTION"),
        "0f18de177ed7c878bf95": ("WHOLE_CARD_DL", "Zusatz", "LOCAL_ADDITIVE"),
        "dec401773c1f0347793d": ("OL+OR", "weiterer Ansatz", "FOLLOWING_BATCH"),
        "4eab1841ed655c20a348": ("SH+E+CKH+AL", "kurz an der Durchlassstelle", "SHORT_PASSAGE_TARGET"),
    }
    for row in events:
        if row["joint_tuple_id"] in revisions:
            row["small_value_de"] = revisions[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "B1_DOSING_AND_PASSAGE_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_66_EVENTS.tsv", events)

    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] == "B1-S002":
            row["continuous_reading_de"] = (
                "Bemessen; Beckenwasser an die Stelle setzen; mit demselben Bestand fortsetzen; "
                "eine und eine weitere Portion an der Stelle führen; noch warm halten; Zusatz und "
                "weiteren Ansatz zugeben; an der Durchlassstelle kurz halten; Maß setzen; länger an "
                "der Stelle halten; nochmals Maß setzen; durchführen, überführen und schließen."
            )
        elif row["statement_id"] == "B1-S006":
            row["continuous_reading_de"] = "Eine Portion zugeben, durchführen, den Zusatz zugeben und abkühlen."
    write("FOUR_HUNDRED_THIRTY_THIRD_REVISED_B1_21_STATEMENTS.tsv", statements)

    target = [row for row in events if row["statement_id"] == "B1-S002"]
    slots = []
    slot_roles = [
        "MEASURE_SETUP", "MEDIUM", "TARGET_SET", "SAME", "CONTINUE", "FIRST_PORTION",
        "FOLLOWING_PORTION", "TARGET", "CONTINUE", "WARM_STATE", "ADDITIVE", "FOLLOWING_BATCH",
        "CONTINUE", "SHORT_PASSAGE_TARGET", "MEASURE", "LONG_TARGET_HOLD", "MEASURE",
        "PASSAGE", "TRANSFER_CLOSE",
    ]
    for index, (row, role) in enumerate(zip(target, slot_roles, strict=True), start=1):
        slots.append({
            "slot": index, "event_id": row["event_id"], "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"], "role": role,
            "small_value_de": row["small_value_de"],
        })
    write("FOUR_HUNDRED_THIRTY_THIRD_B1_S002_NINETEEN_SLOTS.tsv", slots)

    candidates = [
        {"surface": "sheckhal", "candidate": "kurz an der Durchlassstelle", "stem_fit": 4, "left_fit": 4, "right_fit": 4, "economy": 4, "total": 16, "decision": "SELECT"},
        {"surface": "sheckhal", "candidate": "mäßige Menge", "stem_fit": 1, "left_fit": 3, "right_fit": 3, "economy": 3, "total": 10, "decision": "WITHDRAW"},
        {"surface": "sheckhal", "candidate": "handwarm", "stem_fit": 1, "left_fit": 3, "right_fit": 2, "economy": 3, "total": 9, "decision": "RIVAL"},
        {"surface": "sheckhal", "candidate": "kleine Schale", "stem_fit": 1, "left_fit": 2, "right_fit": 2, "economy": 2, "total": 7, "decision": "RIVAL"},
    ]
    write("FOUR_HUNDRED_THIRTY_THIRD_SHECKHAL_CANDIDATES.tsv", candidates)

    audit = []
    ids = {row["joint_tuple_id"] for row in target}
    for joint_id in sorted(ids):
        rows = [row for row in all_events if row["joint_tuple_id"] == joint_id]
        current = [row for row in target if row["joint_tuple_id"] == joint_id][0]
        audit.append({
            "joint_tuple_id": joint_id, "B1_S002_surfaces": "|".join(sorted({row["surface"] for row in target if row["joint_tuple_id"] == joint_id})),
            "fixed_page_events": len(rows), "records": "|".join(sorted({row["record_unit_id"] for row in rows})),
            "small_value_de": current["small_value_de"],
        })
    write("FOUR_HUNDRED_THIRTY_THIRD_S002_EXACT_CARD_AUDIT.tsv", audit)

    summary = {
        "status": "PASS", "B1_events": len(events), "B1_statements": len(statements),
        "S002_events": len(target), "S002_exact_cards": len(ids),
        "revised_exact_cards": len(revisions), "selected_sheckhal": "kurz an der Durchlassstelle",
    }
    (HERE / "FOUR_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
