#!/usr/bin/env python3
"""Validate the pocket grammar's completeness and size."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = rows("FIFTY_FIFTH_24_DESK_RULES.tsv")
    examples = rows("FIFTY_FIFTH_12_POCKET_EXAMPLES.tsv")
    phases = Counter(row["desk_phase"] for row in rules)
    pocket = (OUT / "FIFTY_FIFTH_ONE_PAGE_POCKET_GRAMMAR.md").read_text(encoding="utf-8")
    checks = {
        "twenty_four_rules": len(rules) == 24 and len({row["rule_id"] for row in rules}) == 24,
        "all_five_phases": set(phases) == {"VORBEREITEN", "LESEN", "SATZ", "SCHREIBEN", "ASTRO"},
        "twelve_examples": len(examples) == 12,
        "four_branches_represented": set(row["lesson_branch"] for row in examples) == {"OBSERVED_FUSED", "ANALYTIC_OBSERVED", "ANALYTIC_MASTER", "CONTROLLED_PARAPHRASE"},
        "one_page_scale": len(pocket.splitlines()) <= 60 and len(pocket.split()) <= 500,
        "master_stop_present": "Meister fragen" in pocket,
        "line_rule_present": "Zeile ist nur Platz" in pocket,
        "astro_no_join_present": "f68 und f69 nicht koppeln" in pocket,
        "fixed_pages_sealed": "f84" not in pocket.lower() and all("f84" not in "\t".join(row.values()).lower() for row in rules + examples),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "phase_counts": dict(phases)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
