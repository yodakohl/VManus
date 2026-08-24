#!/usr/bin/env python3
"""Validate the action-specific grade doctrine."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    doctrine = read("SIX_HUNDRED_ELEVENTH_SEVENTEEN_ACTION_GRADE_DOCTRINE.tsv")
    scope = read("SIX_HUNDRED_ELEVENTH_GRADE_SCOPE_ASSIGNMENTS.tsv")
    cards = read("SIX_HUNDRED_ELEVENTH_173_GRADE_AWARE_DICTIONARY.tsv")
    checks = {
        "actions17": len(doctrine) == 17 and len({row["action_component"] for row in doctrine}) == 17,
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "every_grade_token_scoped": all(row["scope_kind"] in {"ACTION_SCOPE", "NONACTION_SCOPE"} for row in scope),
        "every_action_scope_known": all(row["scoped_action_component"] != "NONE" for row in scope if row["scope_kind"] == "ACTION_SCOPE"),
        "only_three_grades": {row["grade_component"] for row in scope} == {"E", "EE", "EEE"},
        "observed_grades_permitted": all(set(row["observed_grades"].split("|")) <= set(row["permitted_grades"].split("|")) for row in doctrine if row["observed_grades"] != "NONE"),
        "ok_has_all_grades": next(row for row in doctrine if row["action_component"] == "OK")["observed_grades"] == "KURZ|LANG|VOLL",
        "sh_and_chk_no_full": all("VOLL" not in next(row for row in doctrine if row["action_component"] == action)["permitted_grades"] for action in ["SH", "CHK"]),
        "point_actions_no_grade": all(next(row for row in doctrine if row["action_component"] == action)["observed_grades"] == "NONE" for action in ["CFH", "CHD", "LD", "P", "R", "S", "SHED", "TALAM"]),
        "all_card_scope_summaries_present": all(row["grade_scope_assignments"] for row in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_ELEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
