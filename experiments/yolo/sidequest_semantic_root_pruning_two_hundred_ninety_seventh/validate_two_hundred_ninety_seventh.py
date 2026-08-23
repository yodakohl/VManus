#!/usr/bin/env python3
"""Validate Pass 297 root pruning."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    audit = read("TWO_HUNDRED_NINETY_SEVENTH_36_ROOT_AUDIT.tsv")
    productive = read("TWO_HUNDRED_NINETY_SEVENTH_29_PRODUCTIVE_FAMILIES.tsv")
    demoted = read("TWO_HUNDRED_NINETY_SEVENTH_7_DEMOTED_MICROSIGNS.tsv")
    inventory = read("TWO_HUNDRED_NINETY_SEVENTH_REVISED_105_ENTRY_INVENTORY.tsv")
    checks = {
        "audit_36": len(audit) == 36,
        "productive_29": len(productive) == 29,
        "core_19": sum(row["new_tier"] == "CORE_PRODUCTIVE_FAMILY" for row in productive) == 19,
        "specialist_10": sum(row["new_tier"] == "SPECIALIST_PRODUCTIVE_FAMILY" for row in productive) == 10,
        "demoted_7": len(demoted) == 7,
        "demoted_exact": {row["family_id_old"] for row in demoted} == {"AN", "OS_RECEIVER", "CH_POUR", "TCH_PREPARATION", "OYK_VESSEL", "SHFY_DURATION", "D_PREVIOUS"},
        "inventory_105": sum(int(row["entry_count"]) for row in inventory) == 105,
        "no_meaning_lost": all(row["retained_concrete_value_de"] for row in demoted),
        "all_families_accounted": {row["family_id"] for row in productive} | {row["family_id_old"] for row in demoted} == {row["family_id"] for row in audit},
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_SEVENTH_36_ROOT_AUDIT.tsv", HERE / "TWO_HUNDRED_NINETY_SEVENTH_REVISED_ROOT_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_SEVENTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
