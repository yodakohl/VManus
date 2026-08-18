#!/usr/bin/env python3
"""Nonimporting source/accounting validator for GDT340 Stage B."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema"
ART = EXP / "artifacts"
DESIGN = ART / "gdt340_comparator_design.json"
FREEZE = ART / "gdt340_schema_instrument_freeze.json"
COMPARATOR = ART / "gdt340_comparator_result.json"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
INVENTORY = ART / "gdt340_voynich_record_inventory.tsv"
FOLDS = ART / "gdt340_voynich_schema_folds.tsv"
MODELS = ART / "gdt340_voynich_schema_models.tsv"
NULL = ART / "gdt340_voynich_schema_null.tsv"
COUNTER = ART / "gdt340_counterexamples.tsv"
RESULT = ART / "gdt340_result.json"
VALIDATION = ART / "gdt340_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def main() -> int:
    checks = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text())
    freeze = json.loads(FREEZE.read_text())
    comparator = json.loads(COMPARATOR.read_text())
    result = json.loads(RESULT.read_text())
    guard = GuardedTSV(SOURCE, selector_column="page", forbidden_action="error")
    rows = list(guard)
    check("source_rows", len(rows) == 8448, len(rows))
    check("guard_no_forbidden", guard.stats.skipped_forbidden == 0, guard.stats)
    check("source_no_f84", all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in rows))
    expected = {}
    for name, spec in design["target_panels"].items():
        selected = [r for r in rows if r["section"] == spec["section"] and r["register"] == spec["register"]]
        records = {(r["page"], r["physical_folio"], r["record_ordinal"]) for r in selected}
        expected[name] = {"events": len(selected), "records": len(records), "folios": len({key[1] for key in records})}
    check("recipe_census", expected["RECIPE_STARS_S"] == {"events": 2430, "records": 82, "folios": 12}, expected["RECIPE_STARS_S"])
    check("pharma_census", expected["PHARMA_P"] == {"events": 264, "records": 12, "folios": 5}, expected["PHARMA_P"])
    inventory = read_tsv(INVENTORY)
    folds = read_tsv(FOLDS)
    models = read_tsv(MODELS)
    null = read_tsv(NULL)
    counter = read_tsv(COUNTER)
    check("inventory_rows", len(inventory) == 94, len(inventory))
    check("inventory_panels", Counter(r["panel"] for r in inventory) == Counter({"RECIPE_STARS_S": 82, "PHARMA_P": 12}))
    check("inventory_no_ids_forms", all(r["tuple_ids_exported"] == "NO" and r["surface_forms_exported"] == "NO" for r in inventory))
    check("only_recoverable_axis", {r["axis"] for r in inventory} == set(freeze["recoverable_axes"]) == {"INTERMEDIATE_STATE"})
    check("fold_rows", len(folds) == 17, len(folds))
    check("model_rows", len(models) == 2, len(models))
    check("null_worlds", len(null) == int(design["target_model"]["worlds"]), len(null))
    check("counterexamples", len(counter) == 6, len(counter))
    by_panel = {r["panel"]: r for r in models}
    for panel, model in by_panel.items():
        selected = [r for r in folds if r["panel"] == panel]
        gain = sum(float(r["gain_bits"]) for r in selected)
        check(f"gain:{panel}", math.isclose(gain, float(model["gain_bits"]), abs_tol=1e-7), gain)
        check(f"records:{panel}", sum(int(r["records"]) for r in selected) == int(model["records"]))
        check(f"coverage:{panel}", sum(int(r["covered_records"]) for r in selected) == int(model["covered_records"]))
        check(f"positive_folios:{panel}", sum(float(r["gain_bits"]) > 0 for r in selected) == int(model["positive_folios"]))
    check("headline_recipe_gain", math.isclose(float(by_panel["RECIPE_STARS_S"]["gain_bits"]), -6.609964574, abs_tol=1e-9))
    check("headline_pharma_gain", math.isclose(float(by_panel["PHARMA_P"]["gain_bits"]), 1.304685165, abs_tol=1e-9))
    check("exact_null_capacity", int(by_panel["RECIPE_STARS_S"]["mobile_exact_null_records"]) == 2 and int(by_panel["PHARMA_P"]["mobile_exact_null_records"]) == 0)
    check("p_values_one", all(float(r["local_p"]) == 1.0 and float(r["max_family_p"]) == 1.0 for r in models))
    powered = [r for r in models if int(r["records"]) >= 20 and int(r["covered_records"]) >= 10 and int(r["mobile_exact_null_records"]) >= 10]
    status = "INSUFFICIENT_COMPARATOR_OR_TARGET_CAPACITY" if not powered else "NO_BLIND_SECTION_SPECIFIC_SCHEMA_RECOVERY"
    check("status", result["status"] == status, status)
    check("stage_a", result["stage_a_status"] == comparator["status"] == "COMPARATOR_RECORD_SCHEMA_RECOVERABLE")
    check("public_freeze_commit", result["access"]["voynich_tuple_scoring_after_public_comparator_freeze_commit"] == "b019e33")
    check("f84_false", all(value is False for key, value in result["access"].items() if key.startswith("f84_")))
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items():
        check(f"hash:{path}", sha(ROOT / path) == digest)
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT340_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks_failed": 0,
        "result_sha256": sha(RESULT), "comparator_freeze_sha256": sha(FREEZE),
        "source_reconstruction": expected,
        "decision_reconstruction": {"powered_endpoints": len(powered), "status": status},
        "scope": "Independent guarded source census, panel/record joins, score arithmetic, exact-null capacity, status and hash validation; comparator and target optimizers are not independently refit.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation)
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
