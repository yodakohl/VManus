#!/usr/bin/env python3
"""Validate Pass 708 corrector exercise."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    errors = read("SEVEN_HUNDRED_EIGHTH_3_ERROR_CORRECTIONS.tsv")
    trace = read("SEVEN_HUNDRED_EIGHTH_14_EVENT_ERROR_TRACE.tsv")
    copies = read("SEVEN_HUNDRED_EIGHTH_MASTER_ERROR_CORRECTED_COPIES.tsv")
    states = {row["copy_state"]: row for row in copies}
    checks = {
        "errors_3": len(errors) == 3,
        "three_error_types": {row["error_type"] for row in errors} == {"GRADE_TOO_SHORT", "SOURCE_FOR_TARGET", "PREMATURE_CLOSE"},
        "trace_14": len(trace) == 14,
        "three_trace_errors": sum(row["is_error"] == "YES" for row in trace) == 3,
        "all_wrong_surfaces_decode": all(row["decoded_card"] != "AMBIGUOUS" for row in trace),
        "all_repairs_restore": all(row["repair_restores_expected_card"] == "YES" for row in trace),
        "copies_3": len(copies) == 3,
        "error_copy_differs": states["APPRENTICE_ERROR_COPY"]["complete_surface_sequence"] != states["CORRECT_MASTER_COPY"]["complete_surface_sequence"],
        "corrected_equals_master": states["CORRECTED_COPY"]["complete_surface_sequence"] == states["CORRECT_MASTER_COPY"]["complete_surface_sequence"],
        "no_new_surfaces": all(row["new_surface_used"] == "NO" for row in errors),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
