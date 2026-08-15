#!/usr/bin/env python3
"""Bind the corrected GDT130 source-aware line-to-star localization."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt130_prediction.json"
LOCALIZATION = ROOT / "gdt130_source_aware_localization.tsv"
REPORT = ROOT / "GDT130_QOKAL_SHEDY_LOCALIZATION_REPORT.md"
OUT = ROOT / "gdt130_localization.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()


def main():
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    assert prediction["status"] == "CORRECTED_FROZEN_BEFORE_F116R_LINE_TO_STAR_LOCALIZATION"
    rows = list(csv.DictReader(LOCALIZATION.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 1
    row = rows[0]
    assert row["target_id"] == prediction["target"]["target_id"]
    assert row["visual_binding"] == prediction["target"]["visual_binding"]
    assert row["selected_star_ordinal"] == "9" and row["localization_state"] == "SECURE"
    assert row["ray_tail_color_judgment"] == "NOT_PERFORMED"
    result = {
        "schema": "GDT130_QOKAL_SHEDY_LOCALIZATION_V1",
        "status": "SECURE_LINE23_TO_STAR09_LOCALIZATION",
        "target_id": row["target_id"], "page": row["page"], "formal_locus": row["formal_locus"],
        "visual_binding": row["visual_binding"], "selected_star_ordinal": int(row["selected_star_ordinal"]),
        "geometry": {"line_center_y_px": int(row["line_center_y_px"]), "line_y_uncertainty_px": int(row["line_y_uncertainty_px"]),
                     "star_center": [int(row["star_center_x_px"]), int(row["star_center_y_px"])],
                     "crop_xywh": [int(value) for value in row["crop_xywh"].split(",")],
                     "adjacent_star_y_px": [int(row["adjacent_upper_star_y_px"]), int(row["adjacent_lower_star_y_px"])]},
        "image": {"canvas": [int(row["canvas_width"]), int(row["canvas_height"])], "image_url": row["image_url"],
                  "full_image_sha256": row["full_image_sha256"], "crop_url": row["crop_url"], "crop_sha256": row["crop_sha256"]},
        "provenance": row["observation_provenance"], "localizer_context": row["localizer_context"],
        "feature_judgment": row["ray_tail_color_judgment"],
        "invalid_star06_scored": False,
        "claim_ceiling": "Source-aware geometry binding only; no ray result, number, star meaning, role, word, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted")},
        "inputs": {PREDICTION.name: sha(PREDICTION), "gdt130_prediction_validation.json": sha(ROOT / "gdt130_prediction_validation.json"), LOCALIZATION.name: sha(LOCALIZATION)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {REPORT.name: sha(REPORT)},
    }
    result["content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "star": result["selected_star_ordinal"], "crop": result["geometry"]["crop_xywh"]}, sort_keys=True))


if __name__ == "__main__":
    main()
