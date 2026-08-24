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
    rows = read("THREE_HUNDRED_SEVENTY_FOURTH_46_TRANSITION_REAUDIT.tsv")
    corrections = read("THREE_HUNDRED_SEVENTY_FOURTH_CORRECTIONS.tsv")
    conflicts = [r for r in rows if r["strict_rule_matches_selected"] == "NO"]
    checks = {
        "46_transitions": len(rows) == 46 and len({r["transition_no"] for r in rows}) == 46,
        "one_conflict": len(conflicts) == 1,
        "conflict_is_e180_e181": conflicts[0]["left_event_id"] == "E180" and conflicts[0]["right_event_id"] == "E181",
        "conflict_has_slot_drop": conflicts[0]["predecessor_to_left_slot_drop"] == "YES",
        "selected_stays_read_once": conflicts[0]["final_pass374_decision"] == "READ_ONCE_CARRY",
        "two_corrections": len(corrections) == 2,
        "pass373_withdrawn": corrections[0]["new_status"] == "WITHDRAWN",
        "all_final_decisions_preserved": all(r["final_pass374_decision"] == r["selected_pass358_decision"] for r in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SEVENTY_FOURTH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
