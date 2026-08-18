#!/usr/bin/env python3
"""Independent accounting/integrity validator for GDT340 Stage A."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema"
ART = EXP / "artifacts"
DESIGN = ART / "gdt340_comparator_design.json"
INVENTORY = ROOT / "gdt176_corema_recipe_inventory.tsv"
RECORDS = ART / "gdt340_comparator_record_schemas.tsv"
FOLDS = ART / "gdt340_comparator_folds.tsv"
MODELS = ART / "gdt340_comparator_models.tsv"
NULL = ART / "gdt340_comparator_null.tsv"
FREEZE = ART / "gdt340_schema_instrument_freeze.json"
RESULT = ART / "gdt340_comparator_result.json"
VALIDATION = ART / "gdt340_comparator_validation.json"


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
    result = json.loads(RESULT.read_text())
    inventory = read_tsv(INVENTORY)
    records = read_tsv(RECORDS)
    folds = read_tsv(FOLDS)
    models = read_tsv(MODELS)
    null = read_tsv(NULL)
    check("inventory_1136", len(inventory) == 1136, len(inventory))
    check("records_1136", len(records) == 1136, len(records))
    check("record_keys", {(r["collection_id"], r["recipe_id"]) for r in inventory} == {(r["collection"], r["record"]) for r in records})
    check("six_collections", sorted({r["collection"] for r in records}) == design["collections"])
    check("forms_hidden", all(r["source_forms_exported"] == "NO" and r["unit_order_exported"] == "NO" for r in records))
    axes = design["primary_axes"]
    expected_counts = {
        "MATERIAL": sum(int(r["ingredient_count"]) + int(r["dish_count"]) > 0 for r in inventory),
        "OPERATION": sum(int(r["instruction_count"]) > 0 for r in inventory),
        "INTERMEDIATE_STATE": sum(int(r["time_count"]) > 0 for r in inventory),
        "APPLICATION": sum(int(r["servingTip_count"]) + int(r["householdTip_count"]) > 0 for r in inventory),
        "RESULT_CONDITION": sum(int(r["closer_count"]) + int(r["dietetics_count"]) > 0 for r in inventory),
    }
    observed_counts = {axis: sum(int(r[axis.lower()]) for r in records) for axis in axes}
    check("axis_counts", observed_counts == expected_counts, observed_counts)
    check("fold_rows", len(folds) == 6 * 5 * 2, len(folds))
    check("model_rows", len(models) == 5 * 2, len(models))
    check("null_worlds", len(null) == int(design["null"]["worlds"]), len(null))
    by_key = {(r["axis"], r["model"]): r for r in models}
    for axis in axes:
        for model in design["models"]:
            selected = [r for r in folds if r["axis"] == axis and r["model"] == model]
            gain = sum(float(r["gain_vs_prior_bits"]) for r in selected)
            check(f"gain:{axis}:{model}", math.isclose(gain, float(by_key[(axis, model)]["gain_vs_prior_bits"]), abs_tol=1e-7), gain)
            check(f"fold_signs:{axis}:{model}", sum(float(r["gain_vs_prior_bits"]) > 0 for r in selected) == int(by_key[(axis, model)]["positive_folds"]))
    recoverable = sorted(r["axis"] for r in models if r["recoverable"] == "YES")
    check("recoverable_axes", recoverable == sorted(freeze["recoverable_axes"]) == sorted(result["recoverable_axes"]), recoverable)
    optional = any(axis in recoverable for axis in ("INTERMEDIATE_STATE", "APPLICATION", "RESULT_CONDITION"))
    status = "COMPARATOR_RECORD_SCHEMA_RECOVERABLE" if optional else "NO_OPTIONAL_RECORD_SCHEMA_RECOVERABLE"
    check("status", status == freeze["status"] == result["status"], status)
    check("five_models", set(freeze["fitted_axes"]) == set(axes))
    check("feature_width", all(len(v["beta"]) == 12 and len(v["mean"]) == 11 and len(v["scale"]) == 11 for v in freeze["fitted_axes"].values()))
    check("no_voynich_scoring", freeze["voynich_tuple_values_retained_or_scored"] is False and result["voynich_tuple_values_retained_or_scored"] is False)
    check("f84_false", all(value is False for value in freeze["f84"].values()) and all(value is False for value in result["f84"].values()))
    for path, digest in {**freeze["inputs"], **freeze["outputs"], **freeze["implementation"]}.items():
        check(f"freeze_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items():
        check(f"result_hash:{path}", sha(ROOT / path) == digest)
    check("freeze_content_hash", content_hash(freeze) == freeze["content_sha256"])
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT340_COMPARATOR_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks_failed": 0,
        "result_sha256": sha(RESULT), "freeze_sha256": sha(FREEZE),
        "source_reconstruction": {"records": len(records), "axis_counts": observed_counts},
        "decision_reconstruction": {"recoverable_axes": recoverable, "status": status},
        "scope": "Independent source/target-count reconstruction, exported arithmetic, gates, hashes and frozen dimensions; optimizer is not independently refit.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation)
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
