#!/usr/bin/env python3
"""Validate component ecology counts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ecology = rows("HUNDRED_FOURTH_44_COMPONENT_ECOLOGY.tsv")
    portable = rows("HUNDRED_FOURTH_PORTABLE_CORE.tsv")
    specialists = rows("HUNDRED_FOURTH_SPECIALIST_COMPONENTS.tsv")
    occurrences = rows("HUNDRED_FOURTH_ATOM_OCCURRENCES.tsv")
    checks = {
        "components_44": len(ecology) == 44,
        "atoms_unique": len({row["atom"] for row in ecology}) == 44,
        "partition_complete": len(portable) + len(specialists) == 44,
        "occurrence_totals_match": sum(int(row["total_atom_occurrences"]) for row in ecology) == len(occurrences),
        "domain_totals_match": all(int(row["herbal_occurrences"]) + int(row["biological_occurrences"]) == int(row["total_atom_occurrences"]) for row in ecology),
        "portable_powered_both": all(len(row["herbal_records"].split(",")) >= 2 and len(row["biological_records"].split(",")) >= 2 for row in portable),
        "all_occurrences_mapped": all(row["atom"] in {item["atom"] for item in ecology} for row in occurrences),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
