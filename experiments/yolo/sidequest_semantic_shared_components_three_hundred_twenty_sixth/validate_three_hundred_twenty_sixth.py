#!/usr/bin/env python3
"""Validate the 13-component, 17-card workshop deck."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("THREE_HUNDRED_TWENTY_SIXTH_13_COMPONENT_LEXICON.tsv")
    cards = read("THREE_HUNDRED_TWENTY_SIXTH_17_CARD_ANALYSES.tsv")
    surfaces = read("THREE_HUNDRED_TWENTY_SIXTH_51_SURFACE_RENDERINGS.tsv")
    support = read("THREE_HUNDRED_TWENTY_SIXTH_TEN_OUTSIDE_PREDICTIONS.tsv")
    surface_counts = Counter(x["handoff_word_id"] for x in surfaces)
    checks = {
        "thirteen_components": len(components) == 13,
        "seventeen_cards": len(cards) == 17,
        "fifteen_productive": sum(x["analysis_status"].startswith("PRODUCTIVE") for x in cards) == 15,
        "two_whole_cards": sum(x["analysis_status"] == "MEMORIZED_WHOLE_CARD" for x in cards) == 2,
        "fifty_one_surfaces": len(surfaces) == 51,
        "surface_counts_reconcile": all(surface_counts[x["handoff_word_id"]] == int(x["surface_count"]) for x in cards),
        "all_wrappers_semantically_empty": all(x["surface_wrapper_value"] == "NONE" for x in surfaces),
        "ten_outside_supports": len(support) == 10 and all(x["composition_prediction_supported"] == "YES" for x in support),
        "source_reduced_to_ar": next(x for x in cards if x["handoff_word_id"] == "HW11")["semantic_formula"] == "AR",
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [components, cards, surfaces, support] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
