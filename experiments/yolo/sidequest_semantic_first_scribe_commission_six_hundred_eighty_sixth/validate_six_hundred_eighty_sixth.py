#!/usr/bin/env python3
"""Validate the two supervised first-scribe commissions."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_sixth.py")], check=True)
    logs = read("SIX_HUNDRED_EIGHTY_SIXTH_83_COMMISSION_LOOKUP_LOG.tsv")
    statements = read("SIX_HUNDRED_EIGHTY_SIXTH_25_COMMISSION_STATEMENTS.tsv")
    commissions = read("SIX_HUNDRED_EIGHTY_SIXTH_2_COMPLETE_COMMISSIONS.tsv")
    corrections = read("SIX_HUNDRED_EIGHTY_SIXTH_CORRECTION_LOAD.tsv")
    checks = {
        "eighty_three_events": len(logs) == 83 and len({row["event_id"] for row in logs}) == 83,
        "twenty_five_statements": len(statements) == 25 and sum(int(row["events"]) for row in statements) == 83,
        "two_commissions": len(commissions) == 2 and {row["record"] for row in commissions} == {"H3", "B1"},
        "commission_event_sum": sum(int(row["events"]) for row in commissions) == 83,
        "exact_card_selected": all(row["selected_card_no"] in row["allowed_card_nos"].split("|") for row in logs),
        "surface_allowed": all(any(row["copied_surface"] in group.split("|") for group in row["allowed_surfaces"].split("; ")) for row in logs),
        "readback_exact": all(row["master_dictation_de"] == row["readback_de"] for row in logs),
        "owner_set_twice": sum(row["owner_action"] == "SET_VISIBLE_OWNER" for row in logs) == 2,
        "corrections_present": len(corrections) >= 5,
        "fixed_pages": {row["page"] for row in logs} == {"f11r", "f81v"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
