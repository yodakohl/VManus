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
    sheet = read("SEVEN_HUNDRED_SEVENTY_THIRD_7_CARD_MASTER_SHEET.tsv")
    exercises = read("SEVEN_HUNDRED_SEVENTY_THIRD_7_MASTER_SHEET_EXERCISES.tsv")
    trace = read("SEVEN_HUNDRED_SEVENTY_THIRD_8_MODEL_OCCURRENCE_TRACE.tsv")
    lessons = read("SEVEN_HUNDRED_SEVENTY_THIRD_16_REVISED_LESSONS.tsv")
    roles = read("SEVEN_HUNDRED_SEVENTY_THIRD_4_REVISED_ROLE_LOADS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    role = {row["role"]: row for row in roles}
    checks = {
        "counts_7_7_8_16_4": (len(sheet), len(exercises), len(trace), len(lessons), len(roles)) == (7, 7, 8, 16, 4),
        "seven_unique_cards": len({row["exact_card_id"] for row in sheet}) == 7,
        "six_model_components": {component for row in sheet for component in row["model_only_components"].split(",")} == {"LSH", "CFH", "DA", "LD", "OS", "TALAM"},
        "every_exercise_stops_without_model": all(row["without_model_response"] == "STOP_AND_REQUEST_MODEL__DO_NOT_INVENT_COMPONENT_RULE" for row in exercises),
        "covered_recall_exact": all(row["with_model_response"] == row["expected_surfaces"] == row["covered_model_recall"] and row["result"] == "PASS_EXACT" for row in exercises),
        "eight_occurrences_exact_no_invention": all(row["recalled_exactly"] == "YES" and row["new_component_rule_invented"] == "NO" for row in trace),
        "hours_110_69_80_24": (int(role["MASTER_CORRECTOR"]["curriculum_hours"]), int(role["HERBAL_SCRIBE"]["curriculum_hours"]), int(role["BIO_STATION_SCRIBE"]["curriculum_hours"]), int(role["ASTRO_TABLE_SCRIBE"]["curriculum_hours"])) == (110, 69, 80, 24),
        "prose_roles_have_12_21_6": all((row["fast_components"], row["wall_components"], row["model_components"]) == (("0", "0", "0") if row["role"] == "ASTRO_TABLE_SCRIBE" else ("12", "21", "6")) for row in roles),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (sheet, exercises, trace, lessons, roles) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["invented_rules"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
