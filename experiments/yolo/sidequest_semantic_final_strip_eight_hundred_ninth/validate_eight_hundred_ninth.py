#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_ninth.py")], check=True)
    cards = read("EIGHT_HUNDRED_NINTH_24_FINAL_STRIP_CARDS.tsv")
    events = read("EIGHT_HUNDRED_NINTH_30_FINAL_STRIP_EVENTS.tsv")
    decisions = read("EIGHT_HUNDRED_NINTH_3_ROOT_DECISIONS.tsv")
    grades = read("EIGHT_HUNDRED_NINTH_5_T_GRADE_ROWS.tsv")
    roles = read("EIGHT_HUNDRED_NINTH_7_CKH_ARGUMENT_ROLES.tsv")
    readings = read("EIGHT_HUNDRED_NINTH_7_READABLE_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_root = {row["component"]: row for row in decisions}
    checks = {
        "twenty_four_cards_thirty_events": len(cards) == 24 and len(events) == 30,
        "component_counts_t10_ckh14_r6": (by_root["T"]["events"], by_root["CKH"]["events"], by_root["R"]["events"]) == ("10", "14", "6"),
        "all_promoted_meaning_invariant": all(row["meaning_invariant"] == "YES" and row["decision"] == "PROMOTE_TO_PARADIGM_CORE31" for row in decisions),
        "t_grade_five_rows_one_missing": len(grades) == 5 and sum(row["events"] == "0" for row in grades) == 1,
        "two_t_prediction_surfaces_no_collision": summary["t_prediction_surfaces"] == 2 and summary["t_prediction_collisions"] == 0,
        "seven_ckh_roles_fourteen_events": len(roles) == 7 and sum(int(row["events"]) for row in roles) == 14,
        "seven_readable_statements": len(readings) == 7,
        "core31_strip0": summary["new_core_size"] == 31 and summary["remaining_recurrent_strip_values"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
