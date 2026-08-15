#!/usr/bin/env python3
"""Validate the corrected GDT130 localization and bindings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt130_localization.json"
PREDICTION = ROOT / "gdt130_prediction.json"
TSV = ROOT / "gdt130_source_aware_localization.tsv"
OUT = ROOT / "gdt130_localization_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(TSV.open(encoding="utf-8"), delimiter="\t"))
    row = rows[0]
    checks = {}
    checks["schema"] = result["schema"] == "GDT130_QOKAL_SHEDY_LOCALIZATION_V1"
    checks["status"] = result["status"] == "SECURE_LINE23_TO_STAR09_LOCALIZATION"
    checks["one_row"] = len(rows) == 1
    checks["target_binding"] = row["target_id"] == prediction["target"]["target_id"] and row["visual_binding"] == prediction["target"]["visual_binding"]
    checks["star"] = row["selected_star_ordinal"] == "9" and row["star_census"] == "10"
    checks["nearest_center"] = abs(int(row["star_center_y_px"]) - int(row["line_center_y_px"])) == 6 and abs(int(row["adjacent_upper_star_y_px"]) - int(row["line_center_y_px"])) > 150 and abs(int(row["adjacent_lower_star_y_px"]) - int(row["line_center_y_px"])) > 100
    x, y, w, h = map(int, row["crop_xywh"].split(","))
    checks["crop_geometry"] = (x, y, w, h) == (80, 1485, 190, 165) and 0 <= x < int(row["canvas_width"]) and 0 <= y < int(row["canvas_height"]) and x + w <= int(row["canvas_width"]) and y + h <= int(row["canvas_height"])
    checks["hashes"] = row["full_image_sha256"] == "4451503bbcbf9f9ab541c65c630bd37bfb06991c708abf29b2ad184ee09ac20c" and row["crop_sha256"] == "b714dc9c22b6c9941d0bcfecf6d186019b6207c9692c477e64fbebf8fa61bdb4"
    checks["separation"] = row["localizer_context"] == "SOURCE_AWARE_LOCALIZER_NO_PREDICTION_ACCESS" and row["ray_tail_color_judgment"] == "NOT_PERFORMED"
    checks["invalid_not_scored"] = result["invalid_star06_scored"] is False
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["document_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded = content.pop("content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    status = "PASS_CORRECTED_SOURCE_AWARE_LOCALIZATION_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT130_QOKAL_SHEDY_LOCALIZATION_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
