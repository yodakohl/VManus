#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    families = read("SEVEN_HUNDRED_EIGHTY_EIGHTH_8_REPEATED_LADDERS.tsv")
    rungs = read("SEVEN_HUNDRED_EIGHTY_EIGHTH_17_ATTESTED_RUNGS.tsv")
    missing = read("SEVEN_HUNDRED_EIGHTY_EIGHTH_7_MISSING_RUNGS.tsv")
    matrix = read("SEVEN_HUNDRED_EIGHTY_EIGHTH_75_CORE_ENDPOINT_MATRIX.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    family = {row["ladder_signature"]: row for row in families}
    predictions = [row for row in missing if row["predicted_surfaces"] != "NO_SAFE_SURFACE"]
    predicted_surfaces = [surface for row in predictions for surface in row["predicted_surfaces"].split(",")]
    checks = {
        "counts_8_17_7_75": (len(families), len(rungs), len(missing), len(matrix)) == (8, 17, 7, 75),
        "one_complete_ladder": [row["ladder_signature"] for row in families if row["ladder_status"] == "COMPLETE_THREE_RUNG"] == ["OK+DY"],
        "ok_dy_counts_8_10_1": [int(row["events"]) for row in rungs if row["ladder_signature"] == "OK+DY"] == [8, 10, 1],
        "six_predictable_one_withheld": len(predictions) == 6 and sum(row["predicted_surfaces"] == "NO_SAFE_SURFACE" for row in missing) == 1,
        "seven_unique_predicted_surfaces": len(predicted_surfaces) == len(set(predicted_surfaces)) == 7,
        "predictions_unseen": all(row["fixed_page_collision"] == "NONE" for row in predictions),
        "t_y_surface_withheld": family["T+Y"]["ladder_status"] == "SEMANTIC_RUNG_ONLY_SURFACE_UNSTABLE" and next(row for row in missing if row["ladder_signature"] == "T+Y")["use_status"] == "SEMANTIC_RUNG_EXPECTED__SURFACE_WITHHELD",
        "matrix_shape": {row["core"] for row in matrix} == {"OK", "OT", "SH", "CHK", "SOLK"} and {row["endpoint"] for row in matrix} == {"Y", "DY", "AL", "OL", "AIIN"} and {row["grade"] for row in matrix} == {"E", "EE", "EEE"},
        "matrix_22_attested_6_formable": sum(row["status"] == "ATTESTED" for row in matrix) == 22 and sum(row["status"] == "FORMABLE_BY_REPEATED_LADDER" for row in matrix) == 6,
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (families, rungs, missing, matrix) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "ONE_COMPLETE_AND_SIX_SURFACE_PREDICTABLE_GRADE_LADDERS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
