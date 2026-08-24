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
    profiles = read("FOUR_HUNDRED_EIGHTY_SEVENTH_TWENTY_PROFILE_PREFERENCES.tsv")
    positional = read("FOUR_HUNDRED_EIGHTY_SEVENTH_FORTY_ONE_POSITIONAL_PREFERENCES.tsv")
    audit = read("FOUR_HUNDRED_EIGHTY_SEVENTH_102_OBSERVED_CHOICE_AUDIT.tsv")
    copies = read("FOUR_HUNDRED_EIGHTY_SEVENTH_452_FOUR_PROFILE_TEACHING_COPIES.tsv")
    checks = {
        "profile_rows_20": len(profiles) == 20,
        "positional_rows_41": len(positional) == 41,
        "choice_audit_102": len(audit) == 102,
        "global_exact_41": sum(row["global_exact"] == "YES" for row in audit) == 41,
        "profile_exact_58": sum(row["profile_exact"] == "YES" for row in audit) == 58,
        "positional_exact_67": sum(row["positional_exact"] == "YES" for row in audit) == 67,
        "copies_452": len(copies) == 452,
        "four_profiles_each": all(sum(row["source_item_id"] == item for row in copies) == 4 for item in {row["source_item_id"] for row in copies}),
        "formal_cards_unchanged": all(row["same_formal_card"] == "YES" for row in copies),
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in audit),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
