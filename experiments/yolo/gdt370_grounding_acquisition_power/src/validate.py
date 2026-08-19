#!/usr/bin/env python3
"""Integrity and aggregate validator for GDT370 (does not import the producer)."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt370_grounding_acquisition_power"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(ok), "detail": detail})
        if not ok:
            raise AssertionError(f"{name}: {detail}")

    result_path = ART / "gdt370_result.json"
    result = json.loads(result_path.read_text())
    grid = read_tsv(ART / "gdt370_power_grid.tsv")
    designs = read_tsv(ART / "gdt370_design_thresholds.tsv")

    check("schema", result["schema"] == "GDT370_RESULT_V1")
    check("grid_rows", len(grid) == 140, str(len(grid)))
    check("design_rows", len(designs) == 20, str(len(designs)))
    check("library", result["simulation"]["candidate_library"] == 81)
    check("selector_cost", abs(result["simulation"]["selector_cost_bits"] - math.log2(81)) < 1e-12)
    check("trials", all(int(r["trials"]) == 256 for r in grid))
    check("held_folios", all(int(r["held_folios"]) == 2 for r in grid))
    check("rate_bounds", all(0 <= float(r[k]) <= 1 for r in grid for k in ("selected_true_rate", "any_pass_rate", "successful_detection_rate", "wrong_predicate_pass_rate", "both_held_positive_rate")))
    check("pass_partition", all(abs(float(r["any_pass_rate"]) - float(r["successful_detection_rate"]) - float(r["wrong_predicate_pass_rate"])) < 1e-12 for r in grid))

    by = {(int(r["folios"]), int(r["arrays_per_folio"]), int(r["cells_per_array"]), r["effect"], r["direction_mode"]): r for r in grid}
    recomputed = []
    for d in designs:
        key = (int(d["folios"]), int(d["arrays_per_folio"]), int(d["cells_per_array"]))
        stable = by[key + ("MEDIUM", "STABLE")]
        null = by[key + ("NULL", "STABLE")]
        reverse = by[key + ("MEDIUM", "REVERSING")]
        ok = float(stable["successful_detection_rate"]) >= .80 and float(null["any_pass_rate"]) <= .05 and float(reverse["any_pass_rate"]) <= .10
        check(f"design_gate_{key}", (d["adequate"] == "True") == ok)
        if ok:
            recomputed.append((int(d["total_cells"]),) + key)
    recomputed.sort()
    check("adequate_count", result["adequate_design_count"] == len(recomputed))
    if recomputed:
        _, folios, arrays, cells = recomputed[0]
        rec = result["recommended_design"]
        check("recommendation", (rec["folios"], rec["arrays_per_folio"], rec["cells_per_array"]) == (folios, arrays, cells))
    else:
        check("recommendation_none", result["recommended_design"] is None)

    for rel, digest in result["inputs"].items():
        check(f"input_hash_{rel}", sha(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items():
        check(f"output_hash_{rel}", sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        check(f"implementation_hash_{rel}", sha(ROOT / rel) == digest)
    payload = dict(result)
    stored = payload.pop("content_hash")
    check("content_hash", hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored)
    check("no_new_voynich", result["new_voynich_rows_loaded"] == 0)
    check("no_new_images", result["new_images_accessed"] == 0)
    check("f84_sealed", result["f84_accessed"] is False)

    validation = {
        "schema": "GDT370_VALIDATION_V1",
        "status": "PASS",
        "scope": "INTEGRITY_AND_INDEPENDENT_AGGREGATE_GATE_RECONSTRUCTION; STOCHASTIC_KERNEL_NOT_INDEPENDENTLY_REIMPLEMENTED",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(result_path),
        "validator_sha256": sha(BASE / "src/validate.py"),
        "f84_accessed": False,
    }
    (ART / "gdt370_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
