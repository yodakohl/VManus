#!/usr/bin/env python3
"""Validate GDT430's prospective nineteen-core paradigm deck."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt430_4938_candidate_density.tsv",
        OUT / "gdt430_5_neighbor_support_bands.tsv",
        OUT / "gdt430_293_absent_multi_neighbor_predictions.tsv",
        OUT / "gdt430_861_page_private_recipe_replay.tsv",
        OUT / "gdt430_24_page_leaveout_summary.tsv",
        OUT / "FOUR_HIGHEST_PREDICTION_CARD.md",
        OUT / "gdt430_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after = {path: path.read_bytes() for path in tracked}
    candidates = read_tsv("gdt430_4938_candidate_density.tsv")
    bands = read_tsv("gdt430_5_neighbor_support_bands.tsv")
    predictions = read_tsv("gdt430_293_absent_multi_neighbor_predictions.tsv")
    leaveout = read_tsv("gdt430_861_page_private_recipe_replay.tsv")
    page_summary = read_tsv("gdt430_24_page_leaveout_summary.tsv")
    result = json.loads((OUT / "gdt430_result.json").read_text(encoding="utf-8"))

    band_map = {int(row["source_neighbor_count"]): row for row in bands}
    prediction_counts = Counter(row["prediction_rank"] for row in predictions)
    leaveout_counts = Counter(row["replay_status"] for row in leaveout)
    strongest = {row["candidate_recipe"] for row in predictions if row["prediction_rank"] == "AMBER_HIGH_PRIORITY"}
    checks = {
        "candidate_rows_4938": len(candidates) == 4938,
        "candidate_ids_unique": len({row["candidate_recipe"] for row in candidates}) == 4938,
        "generated_observed_372": sum(row["current_status"] == "OBSERVED" for row in candidates) == 372,
        "generated_absent_4566": sum(row["current_status"] == "ABSENT" for row in candidates) == 4566,
        "support_bands_5": len(bands) == 5 and set(band_map) == {1, 2, 3, 4, 5},
        "band1_exact": band_map[1]["observed_recipe_count"] == "185" and band_map[1]["absent_recipe_count"] == "4273",
        "band2_exact": band_map[2]["observed_recipe_count"] == "88" and band_map[2]["absent_recipe_count"] == "246",
        "band3_exact": band_map[3]["observed_recipe_count"] == "64" and band_map[3]["absent_recipe_count"] == "43",
        "band4_exact": band_map[4]["observed_recipe_count"] == "30" and band_map[4]["absent_recipe_count"] == "4",
        "band5_exact": band_map[5]["observed_recipe_count"] == "5" and band_map[5]["absent_recipe_count"] == "0",
        "predictions_293": len(predictions) == 293,
        "prediction_bands_exact": prediction_counts == Counter({"AMBER_NARROW": 246, "AMBER_STRONG": 43, "AMBER_HIGH_PRIORITY": 4}),
        "strongest_four_exact": strongest == {"AL+AIN", "AR+OR", "CH+AR", "SH+AIN"},
        "all_predictions_absent": all(next(row for row in candidates if row["candidate_recipe"] == prediction["candidate_recipe"])["current_status"] == "ABSENT" for prediction in predictions),
        "no_surface_prediction": all(row["surface_rule"].startswith("DO_NOT_INVENT_SURFACE") for row in predictions),
        "leaveout_rows_861": len(leaveout) == 861,
        "leaveout_pages_24": len(page_summary) == 24 and len({row["held_page"] for row in leaveout}) == 24,
        "leaveout_any_neighbor_149": len(leaveout) - leaveout_counts["NOT_RECOVERED_BY_ONE_CORE_REPLACEMENT"] == 149,
        "leaveout_multi_neighbor_55": sum(leaveout_counts[key] for key in ("RECOVERED_HIGH_PRIORITY", "RECOVERED_STRONG", "RECOVERED_NARROW")) == 55,
        "leaveout_strong_or_high_16": leaveout_counts["RECOVERED_HIGH_PRIORITY"] + leaveout_counts["RECOVERED_STRONG"] == 16,
        "result_status": result["status"] == "FOUR_HIGH_AND_FORTY_THREE_STRONG_COMPONENT_PREDICTIONS_FIXED",
        "result_recipe_count": result["observed_recipe_type_count"] == 1268,
        "surface_predictions_zero": result["surface_predictions"] == 0,
        "no_meaning_revision": result["meaning_revisions"] == 0,
        "no_new_roots": result["new_roots"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt430_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
