#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MASTER = ROOT / "sidequest_semantic_six_master_order_cards_eight_hundred_eighty_eighth"
PREFIX = "EIGHT_HUNDRED_EIGHTY_NINTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source_marks = read(MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_437_MARK_MASTER_BINDING.tsv")
    source_units = read(MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_118_READABLE_UNITS.tsv")
    marks = read(HERE / f"{PREFIX}_437_MARK_FRONT_BACK_BINDING.tsv")
    units = read(HERE / f"{PREFIX}_118_UNIT_EXECUTION.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_CARD_WORKSHOP_VOCABULARY.tsv")
    slots = read(HERE / f"{PREFIX}_42_FILLED_CHECKLIST_SLOTS.tsv")
    cards = read(HERE / f"{PREFIX}_6_APPRENTICE_JOB_CARDS.tsv")
    calibrations = read(HERE / f"{PREFIX}_6_HOUSE_CALIBRATIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    edition = (HERE / f"{PREFIX}_APPRENTICE_FRONT_BACK_DECK.md").read_text(encoding="utf-8")
    mark_projection = [{key: row[key] for key in source_marks[0]} for row in marks]
    unit_projection = [{key: row[key] for key in source_units[0]} for row in units]
    statuses = Counter(row["execution_status"] for row in units)
    allowed = {"SHARED_CORE_EXECUTABLE", "CORE_PLUS_LOCAL_MODEL", "LOCAL_MODEL_ONLY", "MODEL_LEAF_REQUIRED"}
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "cards_6": len(cards) == 6,
        "slots_42": len(slots) == 42,
        "seven_slots_each": Counter(row["order_id"] for row in slots) == {f"WH{i:02d}": 7 for i in range(1, 7)},
        "required_slot_names": all({row["slot"] for row in slots if row["order_id"] == f"WH{i:02d}"} == {"MATERIAL", "MEASURE", "SOURCE", "TARGET", "OPERATION", "RESULT", "CONDITION"} for i in range(1, 7)),
        "slots_filled": all(row["filled"] == "YES" and row["value_de"] for row in slots),
        "marks_437": len(marks) == 437,
        "marks_exact_projection": mark_projection == source_marks,
        "units_118": len(units) == 118,
        "units_exact_projection": unit_projection == source_units,
        "vocabulary_complete": len(vocabulary) == len({row["identity"] for row in marks}),
        "mark_actions_complete": all(row["apprentice_action"] in {"READ_SHARED_CORE", "COPY_LOCAL_MODEL"} for row in marks),
        "unit_status_complete": set(statuses) <= allowed and sum(statuses.values()) == 118,
        "unit_counts_reconcile": all(int(row["core_marks"]) + int(row["model_marks"]) == int(row["marks"]) for row in units),
        "condition_units_model": all(row["execution_status"] == "MODEL_LEAF_REQUIRED" for row in units if row["section"] == "WHEN"),
        "phrases_exactly_named": all(row["recurrent_phrase_ids"] == "NONE" or all(item.startswith("CPH") for item in row["recurrent_phrase_ids"].split(",")) for row in units),
        "calibrations_6": len(calibrations) == 6,
        "every_card_in_edition": all(f"## {row['order_id']}:" in edition for row in cards),
        "every_unit_on_back": all(f"`{row['master_unit_id']}`" in edition for row in units),
        "sealed": summary["sealed_pages"] == ["f84", "f84r"] and not any(row["page"].startswith("f84") for row in marks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
