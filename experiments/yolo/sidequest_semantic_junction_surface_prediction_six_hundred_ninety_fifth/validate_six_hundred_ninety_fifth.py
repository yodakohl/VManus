#!/usr/bin/env python3
"""Validate junction surface-family reconstruction."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_fifth.py")], check=True)
    predictions = read("SIX_HUNDRED_NINETY_FIFTH_20_SURFACE_FAMILY_PREDICTIONS.tsv")
    fragments = read("SIX_HUNDRED_NINETY_FIFTH_24_DIAGNOSTIC_FRAGMENTS.tsv")
    residues = read("SIX_HUNDRED_NINETY_FIFTH_RENDERER_RESIDUES.tsv")
    classes = Counter(row["prediction_class"] for row in predictions)
    checks = {
        "twenty_cards": len(predictions) == 20 and len({row["card_no"] for row in predictions}) == 20,
        "twenty_four_components": len(fragments) == 24,
        "all_ordered_matches": all(row["ordered_fragment_match"] == "YES" for row in predictions),
        "nine_exact_concats": classes["EXACT_COMPONENT_CONCATENATION"] == 9,
        "eleven_bound_renderers": classes["ORDERED_COMPONENTS_PLUS_BOUND_RENDERER"] == 11,
        "zero_whole_only": classes["WHOLE_CARD_ONLY"] == 0,
        "residue_rows_cover_cards": sum(int(row["exact_cards"]) for row in residues) == 20,
        "nine_no_residue": next(int(row["exact_cards"]) for row in residues if row["renderer_residue"] == "NONE") == 9,
        "required_examples": {row["card_no"]: row["canonical_direct_concat"] for row in predictions}["PROC006"] == "chair" and {row["card_no"]: row["canonical_direct_concat"] for row in predictions}["PROC057"] == "cheeckhody",
        "no_empty_requests": all(row["semantic_request_de"] and row["predicted_fragment_family"] for row in predictions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
