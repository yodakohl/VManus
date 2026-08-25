#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DECK = ROOT / "sidequest_semantic_apprentice_job_deck_eight_hundred_eighty_ninth"
PREFIX = "EIGHT_HUNDRED_NINETIETH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source_marks = read(DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_437_MARK_FRONT_BACK_BINDING.tsv")
    source_units = read(DECK / "EIGHT_HUNDRED_EIGHTY_NINTH_118_UNIT_EXECUTION.tsv")
    decisions = read(HERE / f"{PREFIX}_12_TAUGHT_WHOLE_WORDS.tsv")
    occurrences = read(HERE / f"{PREFIX}_20_WHOLE_WORD_OCCURRENCES.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_REVISED_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv")
    cards = read(HERE / f"{PREFIX}_6_REVISED_JOB_CARDS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    promoted = {row["identity"] for row in decisions}
    unchanged_mark_fields = [field for field in source_marks[0] if field not in {"concrete_default_de", "apprentice_action"}]
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "decisions_12": len(decisions) == 12 and len(promoted) == 12,
        "occurrences_20": len(occurrences) == 20,
        "eight_recurrent": Counter(row["selection_class"] for row in decisions)["RECURRENT_LOCAL_CARD"] == 8,
        "four_h3": Counter(row["selection_class"] for row in decisions)["H3_CHAIN_COMPLETION"] == 4,
        "short_values": all(1 <= len(row["new_whole_word_de"].split()) <= 5 for row in decisions),
        "all_promoted_marks_bound": Counter(row["identity"] for row in occurrences) == Counter(row["identity"] for row in marks if row["identity"] in promoted),
        "vocabulary_231": len(vocabulary) == 231,
        "marks_437": len(marks) == 437,
        "mark_order_unchanged": [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks],
        "mark_structure_unchanged": all(all(mark[field] == source[field] for field in unchanged_mark_fields) for mark, source in zip(marks, source_marks)),
        "only_promoted_meanings_change": all((mark["concrete_default_de"] != source["concrete_default_de"]) == (mark["identity"] in promoted) for mark, source in zip(marks, source_marks)),
        "units_118": len(units) == 118,
        "unit_order_unchanged": [row["master_unit_id"] for row in units] == [row["master_unit_id"] for row in source_units],
        "newly_freed_6": sum(row["newly_freed_from_local_leaf"] == "YES" for row in units) == 6,
        "executable_59": sum(row["execution_status"] == "SHARED_OR_TAUGHT_EXECUTABLE" for row in units) == 59,
        "condition_units_unchanged": all(row["execution_status"] == "MODEL_LEAF_REQUIRED" and row["taught_whole_words_de"] == "NONE" for row in units if row["section"] == "WHEN"),
        "cards_6": len(cards) == 6,
        "no_component_change": summary["component_changes"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"] and not any(row["page"].startswith("f84") for row in marks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
