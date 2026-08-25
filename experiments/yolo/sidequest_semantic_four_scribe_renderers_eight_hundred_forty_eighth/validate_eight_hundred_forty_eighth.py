#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_EIGHTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_eighth.py")], check=True)
    profiles = read("4_SCRIBE_PROFILES.tsv")
    matrix = read("12_CARD_VARIANT_MATRIX.tsv")
    assignments = read("48_SCRIBE_ASSIGNMENTS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(profiles) == 4 and len(matrix) == 12 and len(assignments) == 48,
        "profile_ids": {row["scribe"] for row in profiles} == {"S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"},
        "four_per_card": all(sum(row["exact_card_id"] == card["exact_card_id"] for row in assignments) == 4 for card in matrix),
        "registered_surfaces": all(row["surface_registered"] == "YES" for row in assignments),
        "semantic_agreement": all(row["semantic_agreement"] == "YES" and row["component_recipe"] == row["decoded_recipe"] and row["meaning_de"] == row["decoded_meaning_de"] for row in assignments),
        "variant_count": sum(int(row["distinct_chosen_surfaces"]) for row in matrix) == 34 and summary["reused_assignments"] == 14,
        "high_variant_cards": all(int(row["distinct_chosen_surfaces"]) == 4 for row in matrix if int(row["registered_variants"]) >= 4),
        "whole_card_included": sum(row["component_recipe"] == "RESUME_CARD" for row in matrix) == 1,
        "no_hand_attribution": summary["actual_hand_claims"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
