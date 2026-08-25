#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_four_gap_recipe_closure_eight_hundred_ninety_fifth"
PREFIX = "EIGHT_HUNDRED_NINETY_SIXTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source_marks = read(SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_437_REVISED_MARK_DECK.tsv")
    source_units = read(SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_118_REVISED_UNIT_EXECUTION.tsv")
    decisions = read(HERE / f"{PREFIX}_5_FINAL_PROSE_WHOLE_WORDS.tsv")
    passage = read(HERE / f"{PREFIX}_19_CARD_B1_S002_MASTER_PASSAGE.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_COMPLETE_WORKSHOP_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_COMPLETE_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_COMPLETE_UNIT_EXECUTION.tsv")
    prose = read(HERE / f"{PREFIX}_112_COMPLETE_PROSE_UNITS.tsv")
    cards = read(HERE / f"{PREFIX}_6_PROSE_COMPLETE_JOB_CARDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    target_ids = {row["identity"] for row in decisions}
    unchanged = [field for field in source_marks[0] if field not in {"concrete_default_de", "apprentice_action", "semantic_revision"}]
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "decisions_5": len(decisions) == 5 and len(target_ids) == 5,
        "passage_19": len(passage) == 19 and [int(row["position"]) for row in passage] == list(range(1, 20)),
        "one_mark_each": all(sum(mark["identity"] == identity for mark in marks) == 1 for identity in target_ids),
        "short_values": all(1 <= len(row["new_whole_word_de"].split()) <= 6 for row in decisions),
        "vocabulary_231": len(vocabulary) == 231,
        "marks_437": len(marks) == 437,
        "mark_order_unchanged": [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks],
        "mark_structure_unchanged": all(all(mark[field] == source[field] for field in unchanged) for mark, source in zip(marks, source_marks)),
        "units_118": len(units) == 118,
        "unit_order_unchanged": [row["master_unit_id"] for row in units] == [row["master_unit_id"] for row in source_units],
        "prose_units_112": len(prose) == 112 and all(row["section"] != "WHEN" for row in prose),
        "all_prose_executable": all(row["execution_status"] == "SHARED_OR_TAUGHT_EXECUTABLE" and row["model_marks"] == "0" for row in prose),
        "no_mixed": not any(row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" for row in units),
        "conditions_6": sum(row["execution_status"] == "MODEL_LEAF_REQUIRED" for row in units) == 6,
        "prose_marks_364": sum(row["master_section"] != "WHEN" for row in marks) == 364,
        "condition_marks_73": sum(row["master_section"] == "WHEN" for row in marks) == 73,
        "no_local_prose_marks": not any(row["master_section"] != "WHEN" and row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in marks),
        "cards_6_complete": len(cards) == 6 and all(row["prose_complete"] == "YES" and row["prose_units"] == row["executable_prose_units"] for row in cards),
        "conditions_untouched": all(row["final_prose_gap_words_de"] == "NONE" for row in units if row["section"] == "WHEN"),
        "sealed": summary["sealed_pages"] == ["f84", "f84r"] and not any(row["page"].startswith("f84") for row in marks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
