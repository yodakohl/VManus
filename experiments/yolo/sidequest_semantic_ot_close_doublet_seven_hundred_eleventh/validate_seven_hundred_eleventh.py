#!/usr/bin/env python3
"""Validate Pass 711 OT-close doublet resolution."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    targets = read("SEVEN_HUNDRED_ELEVENTH_3_DOUBLE_OCCURRENCES.tsv")
    controls = read("SEVEN_HUNDRED_ELEVENTH_13_CHD_CLOSE_CONTROLS.tsv")
    models = read("SEVEN_HUNDRED_ELEVENTH_5_MODEL_COMPARISON.tsv")
    rules = read("SEVEN_HUNDRED_ELEVENTH_3_SELECTION_RULES.tsv")
    resolution = read("SEVEN_HUNDRED_ELEVENTH_DOCKET_RESOLUTION.tsv")
    checks = {
        "targets_3": len(targets) == 3,
        "target_cards_two": {row["card_no"] for row in targets} == {"PROC145", "PROC166"},
        "same_recipe": {row["component_recipe"] for row in targets} == {"OT+CHD+DY"},
        "same_reading": {row["merged_reading_de"] for row in targets} == {"DANACH · UMSETZEN · SCHLUSS"},
        "b3_e_two": sum(row["record"] == "B3" and row["has_chd_joint_e"] == "YES" for row in targets) == 2,
        "b5_compact_one": sum(row["record"] == "B5" and row["has_chd_joint_e"] == "NO" for row in targets) == 1,
        "controls_13": len(controls) == 13,
        "controls_mixed_e": {row["has_chd_joint_e"] for row in controls} == {"YES", "NO"},
        "models_5": len(models) == 5,
        "local_model_selected": next(row for row in models if row["model"] == "M4_LOCAL_RECORD_RENDERER")["fits_target_3"] == "YES",
        "rules_3": len(rules) == 3,
        "one_resolution": len(resolution) == 1 and resolution[0]["semantic_ambiguity_after_merge"] == "NO",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_ELEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
