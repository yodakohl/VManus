#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SEVEN_HUNDRED_EIGHTY_FIRST_12_TWO_SIDED_SAMPLE_CARDS.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTY_FIRST_6_MARGIN_RULES.tsv")
    events = read("SEVEN_HUNDRED_EIGHTY_FIRST_89_APPRENTICE_EVENT_TRACE.tsv")
    statements = read("SEVEN_HUNDRED_EIGHTY_FIRST_28_APPRENTICE_STATEMENTS.tsv")
    exams = read("SEVEN_HUNDRED_EIGHTY_FIRST_2_FULL_PAGE_EXAMS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    exam = {row["page"]: row for row in exams}
    checks = {
        "counts_12_6_89_28_2": (len(cards), len(rules), len(events), len(statements), len(exams)) == (12, 6, 89, 28, 2),
        "unique_card_slots": len({row["card_slot"] for row in cards}) == 12,
        "f56_counts": tuple(int(exam["f56r"][key]) for key in ("events", "statements", "common_card_turns", "local_model_copies", "surface_changes")) == (27, 6, 6, 21, 2),
        "f82_counts": tuple(int(exam["f82r"][key]) for key in ("events", "statements", "common_card_turns", "local_model_copies", "surface_changes")) == (62, 22, 10, 52, 7),
        "all_event_readbacks_exact": all(row["readback"] == "EXACT_CARD_RECIPE_AND_PROMPT" for row in events),
        "all_statement_results_pass": all(row["result"] == "PASS" for row in statements),
        "all_exam_errors_zero": all(row["wrong_card_ids"] == row["wrong_component_recipes"] == row["wrong_spoken_prompts"] == "0" for row in exams),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (cards, rules, events, statements, exams) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["exam_events"] == 89,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
