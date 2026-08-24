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
    panels = read("THREE_HUNDRED_SIXTY_SIXTH_14_PAIR_DECISION_BOOK.tsv")
    events = read("THREE_HUNDRED_SIXTY_SIXTH_72_PAIR_OCCURRENCES.tsv")
    drills = read("THREE_HUNDRED_SIXTY_SIXTH_14_WRONG_CARD_DRILLS.tsv")
    checks = {
        "14_panels": len(panels) == 14 and len({r["pair_id"] for r in panels}) == 14,
        "72_events": len(events) == 72 and len({r["event_id"] for r in events}) == 72,
        "all_events_resolved": all(r["candidate_count_after_owner_and_right"] == "1" and r["exact_selection"] == "YES" for r in events),
        "two_routes": {r["selection_route"] for r in events} == {"OWNER", "OWNER_PLUS_RIGHT_NEIGHBOR"},
        "panel_counts_sum": sum(int(r["events"]) for r in panels) == 72,
        "14_drills": len(drills) == 14 and len({r["pair_id"] for r in drills}) == 14,
        "all_drills_wrong_then_right": all(r["deliberately_wrong_joint_tuple_id"] != r["correct_joint_tuple_id"] and r["repaired_exactly"] == "YES" for r in drills),
        "no_master_exemplar": all(r["master_exemplar_opened"] == "NO" for r in drills),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
