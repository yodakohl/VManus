#!/usr/bin/env python3
"""Validate the four-role workshop floor plan."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_second.py")], check=True)
    roles = read("SIX_HUNDRED_NINETY_SECOND_4_SCRIBE_ROLES.tsv")
    assignments = read("SIX_HUNDRED_NINETY_SECOND_26_ROOT_ASSIGNMENTS.tsv")
    routes = read("SIX_HUNDRED_NINETY_SECOND_11_RECORD_ROUTES.tsv")
    handoffs = read("SIX_HUNDRED_NINETY_SECOND_6_HANDOFF_RULES.tsv")
    role_load = {row["scribe_role"]: int(row["specialist_token_uses"]) for row in roles}
    checks = {
        "four_roles": len(roles) == 4,
        "twenty_six_roots_once": len(assignments) == 26 and len({row["component"] for row in assignments}) == 26,
        "role_root_sum": sum(int(row["specialist_root_cards"]) for row in roles) == 26,
        "role_loads": role_load == {"S01_MASTER_CORRECTOR": 6, "S02_PREPARATION_WET": 61, "S03_TRANSFER": 101, "S04_STATE_CONTROL": 74},
        "eleven_routes": len(routes) == 11,
        "nine_prep_wet": sum(int(row["prep_wet_token_uses"]) > 0 for row in routes) == 9,
        "all_transfer": all(int(row["transfer_token_uses"]) > 0 for row in routes),
        "all_state": all(int(row["state_token_uses"]) > 0 for row in routes),
        "six_local_command_records": sum(int(row["local_command_uses"]) > 0 for row in routes) == 6,
        "fifty_three_visits": sum(int(row["desk_visits"]) for row in routes) == 53,
        "forty_two_handoffs": sum(int(row["handoffs"]) for row in routes) == 42,
        "six_handoff_rules": len(handoffs) == 6,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
