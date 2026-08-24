#!/usr/bin/env python3
"""Validate the compact pass-678 historical operational model."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_seventy_eighth.py")], check=True)
    ranking = read("SIX_HUNDRED_SEVENTY_EIGHTH_7_MODEL_RANKING.tsv")
    matrix = read("SIX_HUNDRED_SEVENTY_EIGHTH_70_PROPERTY_MATRIX.tsv")
    layers = read("SIX_HUNDRED_SEVENTY_EIGHTH_5_LAYER_HYBRID.tsv")
    crosswalk = read("SIX_HUNDRED_SEVENTY_EIGHTH_10_RULE_CROSSWALK.tsv")
    sources = read("SIX_HUNDRED_SEVENTY_EIGHTH_12_HISTORICAL_SOURCES.tsv")
    checks = {
        "seven_models": len(ranking) == 7,
        "seventy_property_rows": len(matrix) == 70,
        "ten_properties_each": all(sum(row["model_id"] == model["model_id"] for row in matrix) == 10 for model in ranking),
        "scores_in_range": all(0 <= int(row["creative_fit_0_to_3"]) <= 3 for row in matrix),
        "ranking_totals_match": all(int(model["creative_fit_total_of_30"]) == sum(int(row["creative_fit_0_to_3"]) for row in matrix if row["model_id"] == model["model_id"]) for model in ranking),
        "bdhd_best_single": ranking[0]["model_id"] == "M3_BDHD_ALCHEMICAL_CODE_ALPHABET",
        "five_hybrid_layers": len(layers) == 5,
        "layer_order_complete": [int(row["layer_order"]) for row in layers] == [1, 2, 3, 4, 5],
        "ten_crosswalk_rows": len(crosswalk) == 10,
        "twelve_sources": len(sources) == 12,
        "urls_present": all(row["url"].startswith("https://") for row in sources),
        "no_extra_page_tokens": not any(
            token
            in "\n".join(
                path.read_text(encoding="utf-8")
                for path in HERE.iterdir()
                if path.is_file() and path.suffix not in {".py", ".json"}
            )
            for token in ["f84r", "f84v"]
        ),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
    }
    (HERE / "SIX_HUNDRED_SEVENTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
