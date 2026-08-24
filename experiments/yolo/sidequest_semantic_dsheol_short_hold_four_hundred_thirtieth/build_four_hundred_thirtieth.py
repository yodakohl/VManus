#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b1_pool_article_four_hundred_twenty_ninth"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_TWENTY_NINTH_B1_66_EVENT_INTERLINEAR.tsv")
    target = [row for row in events if row["joint_tuple_id"] == "74c76d589d44120f647b"]
    assert len(target) == 1 and target[0]["event_id"] == "E160"
    for row in events:
        if row["event_id"] == "E160":
            row["small_value_de"] = "kurz halten"
            row["lexicon_source"] = "B1_COMPOSED_SH_HOLD+E_SHORT+OL_CONTINUE"
    write("FOUR_HUNDRED_THIRTIETH_REVISED_B1_66_EVENT_INTERLINEAR.tsv", events)

    statements = read("FOUR_HUNDRED_TWENTY_NINTH_B1_21_STATEMENTS.tsv")
    for row in statements:
        if row["statement_id"] == "B1-S018":
            row["card_sequence_de"] = row["card_sequence_de"].replace("einreiben", "kurz halten")
            row["continuous_reading_de"] = "Das Empfangsgefäß bereitstellen, den Posten kurz halten, auf Sollstand bringen, länger auffangen und schließen."
    write("FOUR_HUNDRED_THIRTIETH_REVISED_B1_21_STATEMENTS.tsv", statements)

    candidates = [
        {"candidate": "KURZ_HALTEN", "value_de": "kurz halten", "component_fit": 4, "left_fit": 4, "right_fit": 4, "owner_fit": 4, "specificity": 4, "total": 20, "decision": "SELECT"},
        {"candidate": "VORBEREITEN", "value_de": "vorbereiten", "component_fit": 1, "left_fit": 4, "right_fit": 3, "owner_fit": 4, "specificity": 2, "total": 14, "decision": "RIVAL"},
        {"candidate": "BESCHICHTEN", "value_de": "beschichten", "component_fit": 1, "left_fit": 2, "right_fit": 2, "owner_fit": 3, "specificity": 3, "total": 11, "decision": "RIVAL"},
        {"candidate": "AUSSTREICHEN", "value_de": "ausstreichen", "component_fit": 1, "left_fit": 2, "right_fit": 2, "owner_fit": 2, "specificity": 3, "total": 10, "decision": "RIVAL"},
        {"candidate": "EINREIBEN", "value_de": "einreiben", "component_fit": 1, "left_fit": 1, "right_fit": 1, "owner_fit": 1, "specificity": 3, "total": 7, "decision": "WITHDRAW"},
    ]
    write("FOUR_HUNDRED_THIRTIETH_DSHEOL_CANDIDATES.tsv", candidates)

    pocket = [{
        "surface": "dsheol", "joint_tuple_id": "74c76d589d44120f647b", "events": 1,
        "composition": "SH_HOLD + E_SHORT + OL_CONTINUE", "small_value_de": "kurz halten",
        "source_context": "EMPFANGSGEFAESS > DSHEOL > SOLLSTAND > LAENGER_AUFFANGEN_CLOSE",
        "instruction_de": "Halte den aufgenommenen Posten kurz, bevor du ihn auf Sollstand bringst.",
    }]
    write("FOUR_HUNDRED_THIRTIETH_POCKET_RULE.tsv", pocket)

    summary = {
        "status": "PASS", "target_events": 1, "B1_events": len(events), "B1_statements": len(statements),
        "old_value": "einreiben", "new_value": "kurz halten", "selected_composition": "SH+E+OL",
    }
    (HERE / "FOUR_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
