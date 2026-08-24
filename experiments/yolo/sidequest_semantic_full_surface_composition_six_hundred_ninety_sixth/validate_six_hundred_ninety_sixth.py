#!/usr/bin/env python3
"""Validate the complete 173-card surface grammar."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_sixth.py")], check=True)
    cards = read("SIX_HUNDRED_NINETY_SIXTH_173_CARD_SURFACE_GRAMMAR.tsv")
    surfaces = read("SIX_HUNDRED_NINETY_SIXTH_230_SURFACE_FORM_TRACES.tsv")
    fragments = read("SIX_HUNDRED_NINETY_SIXTH_39_COMPONENT_FRAGMENT_RULES.tsv")
    residues = read("SIX_HUNDRED_NINETY_SIXTH_30_RENDERER_RESIDUES.tsv")
    card_classes = Counter(row["card_prediction_class"] for row in cards)
    surface_classes = Counter(row["surface_class"] for row in surfaces)
    lengths = Counter(int(row["renderer_residue_length"]) for row in surfaces)
    checks = {
        "one_seventy_three_cards": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "two_thirty_surfaces": len(surfaces) == 230,
        "thirty_nine_components": len(fragments) == 39,
        "card_class_counts": card_classes == Counter({"COMPOSED_WITH_BOUND_RENDERER": 116, "COMPOSED_DIRECT_ALL_FORMS": 54, "MEMORIZED_WHOLE_COMMAND": 3}),
        "surface_class_counts": surface_classes == Counter({"ORDERED_COMPONENTS_PLUS_RENDERER": 152, "DIRECT_COMPONENT_STRING": 78}),
        "no_unexplained": not any(row["surface_class"] == "UNEXPLAINED" for row in surfaces),
        "residue_length_distribution": lengths == Counter({0: 78, 1: 85, 2: 49, 3: 15, 4: 3}),
        "thirty_residues": len(residues) == 30,
        "max_residue_four": max(int(row["renderer_residue_length"]) for row in surfaces) == 4,
        "three_whole_commands": {row["card_no"] for row in cards if row["card_prediction_class"] == "MEMORIZED_WHOLE_COMMAND"} == {"PROC005", "PROC034", "PROC043"},
        "form_sum_per_card": sum(int(row["surface_forms"]) for row in cards) == 230,
        "no_empty_semantics": all(row["semantic_recipe_de"] for row in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
