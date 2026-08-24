#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    with (HERE / "THREE_HUNDRED_SIXTY_NINTH_EIGHT_CARD_PAIRED_ORDER.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks = {
        "eight_cards": len(rows) == 8 and [int(r["position"]) for r in rows] == list(range(1, 9)),
        "two_cycles": {r["microcycle"] for r in rows} == {"C1", "C2"},
        "three_pair_cards": sum(r["pair_id"] != "NONE" for r in rows) == 3,
        "two_owner_one_neighbor": sum(r["decision_route"] == "PAIR_OWNER" for r in rows) == 2 and sum(r["decision_route"] == "PAIR_OWNER_PLUS_RIGHT" for r in rows) == 1,
        "all_surfaces_registered": all(r["surface_registered"] == "YES" for r in rows),
        "all_values_backread": all(r["backread_exact"] == "YES" for r in rows),
        "one_owner": {r["visible_owner"] for r in rows} == {"B3_MAIN_ARCH_LINKED_PAIR"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
