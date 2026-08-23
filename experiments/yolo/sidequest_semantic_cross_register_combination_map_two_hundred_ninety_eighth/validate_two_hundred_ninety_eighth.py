#!/usr/bin/env python3
"""Validate Pass 298 combination map."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    pairs = read("TWO_HUNDRED_NINETY_EIGHTH_406_FAMILY_PAIR_MAP.tsv")
    triples = read("TWO_HUNDRED_NINETY_EIGHTH_ASTRO_TRIPLE_COMPOSITIONS.tsv")
    leads = read("TWO_HUNDRED_NINETY_EIGHTH_12_CROSS_REGISTER_SPELLING_LEADS.tsv")
    statuses = Counter(row["register_status"] for row in pairs)
    checks = {
        "pairs_406": len(pairs) == 406,
        "four_statuses": set(statuses) == {"BOTH_REGISTERS", "PROSE_ONLY", "ASTRO_ONLY_VISIBLE_COMBINATION", "UNSEEN_PAIR"},
        "status_sum": sum(statuses.values()) == 406,
        "triples_nonempty": len(triples) >= 1,
        "twelve_leads": len(leads) == 12,
        "all_leads_visible": all(row["visible_in_astro"] == "YES" for row in leads),
        "all_leads_concrete": all(row["proposed_prose_workshop_value_de"] for row in leads),
        "required_surfaces": {"okaiiin", "olar", "alaiin", "chedaiin", "eckhear", "qotair", "saral", "salsain"} <= {row["visible_astro_surface"] for row in leads},
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_EIGHTH_406_FAMILY_PAIR_MAP.tsv", HERE / "TWO_HUNDRED_NINETY_EIGHTH_COMBINATION_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_EIGHTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
