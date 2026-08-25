#!/usr/bin/env python3
"""Validate Pass 1000 outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    full = read_tsv("PASS1000_25_GAP_RECLASSIFICATION.tsv")
    adjacent = read_tsv("PASS1000_12_EMBEDDED_ADJACENCIES.tsv")
    absent = read_tsv("PASS1000_7_REAL_ABSENCES_AND_PREDICTIONS.tsv")
    collisions = read_tsv("PASS1000_3_COLLISION_REPAIRS.tsv")
    summary = json.loads((OUT / "PASS1000_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "twenty_five_source_gaps": len(full) == 25,
        "twelve_adjacent_pairs": len(adjacent) == 12,
        "six_ordered_only_pairs": sum(row["revised_status"] == "IN_LAENGERER_KARTE_GETRENNT_BELEGT" for row in full) == 6,
        "seven_genuine_absences": len(absent) == 7,
        "three_collision_repairs": len(collisions) == 3,
        "all_collision_pairs_have_adjacent_evidence": all(int(row["embedded_adjacent_events"]) > 0 for row in collisions),
        "all_adjacent_rows_positive": all(int(row["adjacent_events"]) > 0 for row in adjacent),
        "all_absences_zero_ordered": all(next(int(row["ordered_total_events"]) for row in full if row["left_root"] == a["left_root"] and row["right_root"] == a["right_root"]) == 0 for a in absent),
        "strongest_prediction_chain": absent[0]["candidate_surface"] == "chain" and absent[0]["prediction_priority"] == "HOCH",
        "summary_counts_match": summary["embedded_adjacent_pairs"] == 12 and summary["embedded_ordered_only_pairs"] == 6 and summary["genuine_absent_pairs"] == 7,
        "no_blank_workshop_rules": all(row["workshop_rule_de"].strip() for row in full),
        "no_sealed_pages": not any("f84" in "\t".join(row.values()).lower() for rows in (full, adjacent, absent, collisions) for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (OUT / "PASS1000_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], result["passed"], result["total"])
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
