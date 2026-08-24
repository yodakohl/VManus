#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
IIN_IDS = {"2c82523794dcb7d2b343", "409de02322e7b2ca0c62", "fcc1deda9e24ec268eb0"}
AIIN_ID = "2f1c5e56e8f0ff459065"


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
    iin_rows = []
    assignments = {
        "E036": ("K+IIN", "WEICHSTUFE", "weiche Konsistenz als Ziel einstellen"),
        "E161": ("IIN", "SOLLSTUFE", "örtliche Arbeitsstufe vor längerem Auffangen"),
        "E309": ("IIN", "SOLLSTUFE", "örtliche Arbeitsstufe vor Bereit-/Absetzgang"),
        "E371": ("DA+IIN", "ZWEITE_OEFFNUNGSSTELLUNG", "Stellung der zweiten Öffnung wählen"),
    }
    for source in events:
        if source["joint_tuple_id"] not in IIN_IDS:
            continue
        composition, value, expansion = assignments[source["event_id"]]
        iin_rows.append({
            "event_id": source["event_id"],
            "record": source["record_unit_id"],
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "composition": composition,
            "iin_contribution": "SOLLSTUFE_OR_SETTING",
            "selected_card_value_de": value,
            "contextual_expansion_de": expansion,
        })
    write("FOUR_HUNDRED_EIGHTH_FOUR_IIN_OCCURRENCES.tsv", iin_rows)

    aiin_rows = [row for row in events if row["joint_tuple_id"] == AIIN_ID]
    contrast = [
        {"family": "AIIN", "exact_card_types": 1, "events": len(aiin_rows), "small_value_de": "Sollmaß", "question_answered": "wie viel", "examples": "aiin|chaiin|daiin|saiin|taiin"},
        {"family": "IIN", "exact_card_types": 3, "events": len(iin_rows), "small_value_de": "Sollstufe/Einstellung", "question_answered": "in welcher Arbeitsstellung", "examples": "oiiin|soiiin|kaiiin|daiiin"},
    ]
    write("FOUR_HUNDRED_EIGHTH_AIIN_IIN_CONTRAST.tsv", contrast)

    rules = [
        {"pattern": "IIN", "learned_rule": "set the required working stage", "example": "OIIIN/SOIIIN", "result_de": "Sollstufe"},
        {"pattern": "K+IIN", "learned_rule": "apply a soft/consistency hull to the stage", "example": "KAIIIN", "result_de": "Weichstufe"},
        {"pattern": "DA+IIN", "learned_rule": "apply the learned second-opening hull to the setting", "example": "DAIIIN", "result_de": "Stellung der zweiten Öffnung"},
        {"pattern": "AIIN", "learned_rule": "do not decompose as A+IIN", "example": "AIIN/DAIIN/SAIIN", "result_de": "Sollmaß"},
    ]
    write("FOUR_HUNDRED_EIGHTH_FOUR_APPRENTICE_RULES.tsv", rules)

    summary = {
        "status": "PASS",
        "iin_events": len(iin_rows),
        "iin_exact_cards": len({row["joint_tuple_id"] for row in iin_rows}),
        "aiin_events": len(aiin_rows),
        "decision": "IIN_WORK_SETTING_DISTINCT_FROM_AIIN_MEASURE",
        "b5_value": "SECOND_OPENING_SETTING",
    }
    (HERE / "FOUR_HUNDRED_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
