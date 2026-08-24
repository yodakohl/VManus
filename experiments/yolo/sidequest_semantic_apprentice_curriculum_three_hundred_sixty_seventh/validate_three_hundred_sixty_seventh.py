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
    course = read("THREE_HUNDRED_SIXTY_SEVENTH_SIX_DAY_CURRICULUM.tsv")
    order = read("THREE_HUNDRED_SIXTY_SEVENTH_FRESH_TEN_CARD_ORDER.tsv")
    checks = {
        "six_days": len(course) == 6 and [int(r["day"]) for r in course] == list(range(1, 7)),
        "ten_cards": len(order) == 10 and [int(r["position"]) for r in order] == list(range(1, 11)),
        "two_cycles": {r["microcycle"] for r in order} == {"C1", "C2"},
        "surfaces_registered": all(r["selected_surface"] in r["registered_surface_palette"].split("|") for r in order),
        "identities_unique": len({r["selected_joint_tuple_id"] for r in order}) == 10,
        "all_backread_exact": all(r["backread_exact"] == "YES" for r in order),
        "no_running_exemplar": all(r["selection_route"] != "RUNNING_PAGE_EXEMPLAR" for r in order),
        "six_slots_represented": len({r["backread_slot_code"] for r in order}) == 6,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
