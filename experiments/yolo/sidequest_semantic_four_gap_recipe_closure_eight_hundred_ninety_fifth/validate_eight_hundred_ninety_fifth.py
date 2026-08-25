#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_three_gap_phrase_closure_eight_hundred_ninety_fourth"
PREFIX = "EIGHT_HUNDRED_NINETY_FIFTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source_marks = read(SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_437_REVISED_MARK_DECK.tsv")
    source_units = read(SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_118_REVISED_UNIT_EXECUTION.tsv")
    decisions = read(HERE / f"{PREFIX}_12_FOUR_GAP_WHOLE_WORDS.tsv")
    recipes = read(HERE / f"{PREFIX}_3_MEMORIZED_FOUR_STEP_RECIPES.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_REVISED_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv")
    cards = read(HERE / f"{PREFIX}_6_REVISED_JOB_CARDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    target_ids = {row["identity"] for row in decisions}
    unchanged = [field for field in source_marks[0] if field not in {"concrete_default_de", "apprentice_action", "semantic_revision"}]
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "decisions_12": len(decisions) == 12 and len(target_ids) == 12,
        "recipes_3": len(recipes) == 3 and all(len(row["identity_recipe"].split()) == 4 for row in recipes),
        "one_mark_each": all(sum(mark["identity"] == identity for mark in marks) == 1 for identity in target_ids),
        "short_values": all(1 <= len(row["new_whole_word_de"].split()) <= 7 for row in decisions),
        "vocabulary_231": len(vocabulary) == 231,
        "marks_437": len(marks) == 437,
        "mark_order_unchanged": [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks],
        "mark_structure_unchanged": all(all(mark[field] == source[field] for field in unchanged) for mark, source in zip(marks, source_marks)),
        "units_118": len(units) == 118,
        "unit_order_unchanged": [row["master_unit_id"] for row in units] == [row["master_unit_id"] for row in source_units],
        "closed_flags_3": sum(row["four_gap_unit_closed"] == "YES" for row in units) == 3,
        "executable_111": sum(row["execution_status"] == "SHARED_OR_TAUGHT_EXECUTABLE" for row in units) == 111,
        "mixed_1": sum(row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" for row in units) == 1,
        "conditions_6": sum(row["execution_status"] == "MODEL_LEAF_REQUIRED" for row in units) == 6,
        "cards_6": len(cards) == 6,
        "conditions_untouched": all(row["four_step_recipe_id"] == "NONE" for row in units if row["section"] == "WHEN"),
        "sealed": summary["sealed_pages"] == ["f84", "f84r"] and not any(row["page"].startswith("f84") for row in marks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
