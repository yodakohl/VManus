#!/usr/bin/env python3
"""Nonimporting integrity/accounting validator for the GDT339 comparator freeze."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt339_comparator_first_semantic_incidence"
ART = EXP / "artifacts"
DESIGN = ART / "gdt339_comparator_design.json"
COREMA = ROOT / "gdt176_external_role_units.tsv"
NUREMBERG = ROOT / "gdt155_unblinded_record_truth.tsv"
SUMMARY = ART / "gdt339_comparator_units_summary.tsv"
FOLDS = ART / "gdt339_comparator_folds.tsv"
MODELS = ART / "gdt339_comparator_models.tsv"
NULL = ART / "gdt339_comparator_null.tsv"
VARIANTS = ART / "gdt339_tried_variants.tsv"
FREEZE = ART / "gdt339_invariant_freeze.json"
RESULT = ART / "gdt339_comparator_result.json"
VALIDATION = ART / "gdt339_comparator_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256_file(path: Path) -> str:
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


def token_count(text: str) -> int:
    return len(re.findall(r"[^\W_]+", unicodedata.normalize("NFC", text.lower()), flags=re.UNICODE))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    corema = read_tsv(COREMA)
    nuremberg_records = [row for row in read_tsv(NUREMBERG) if row["corpus"] == "NUREMBERG"]
    nuremberg_units = 0
    nuremberg_classes = Counter()
    for row in nuremberg_records:
        addressee = token_count(row["regularized_addressee"])
        content = token_count(row["regularized_content"])
        other = 0
        if row["regularized_other_sections"] != "NONE":
            for part in row["regularized_other_sections"].split(" || "):
                other += token_count(part.split("=", 1)[1] if "=" in part else part)
        nuremberg_units += addressee + content + other
        nuremberg_classes.update({"ADDRESSEE": addressee, "CONTENT": content, "OTHER": other})
    check("corema_units", len(corema) == 22394, len(corema))
    check("corema_collections", sorted({row["collection_id"] for row in corema}) == ["b4", "b6", "br1", "bs1", "gr1", "w1"])
    check("corema_roles", {row["oracle_role"] for row in corema} == {"OPENER", "OPERATION", "INGREDIENT", "TOOL", "CLOSER"})
    check("nuremberg_records", len(nuremberg_records) == 3176, len(nuremberg_records))
    check("nuremberg_units", nuremberg_units == 421720, nuremberg_units)
    check("nuremberg_classes_nonempty", set(nuremberg_classes) == {"ADDRESSEE", "CONTENT", "OTHER"}, nuremberg_classes)
    check("nuremberg_books", sorted({row["book_or_ms"] for row in nuremberg_records}) == ["Band2", "Band3", "Band4", "Band5"])

    summary = read_tsv(SUMMARY)
    check("summary_rows", len(summary) == 10, len(summary))
    check("summary_collections", {(row["dataset"], row["collection"]) for row in summary} == {(d["dataset"], c) for d in design["comparators"] for c in d["held_collections"]})
    check("summary_raw_hidden", all(row["raw_forms_exported"] == "NO" for row in summary))
    check("summary_full_units", sum(int(row["full_units"]) for row in summary if row["dataset"] == "COREMA") == 22394 and sum(int(row["full_units"]) for row in summary if row["dataset"] == "NUREMBERG") == 421720)

    folds = read_tsv(FOLDS)
    models = read_tsv(MODELS)
    variants = read_tsv(VARIANTS)
    null = read_tsv(NULL)
    check("fold_rows", len(folds) == 50, len(folds))
    check("model_rows", len(models) == 10, len(models))
    check("variant_rows", len(variants) == 4, len(variants))
    check("null_worlds", len(null) == int(design["null"]["worlds"]), len(null))
    eligible = [row for row in models if row["selection_eligible"] == "YES"]
    candidates = list(design["candidate_models"])
    check("candidate_rows", {(row["dataset"], row["model"]) for row in eligible} == {(d, m) for d in ("COREMA", "NUREMBERG") for m in candidates})
    by_key = {(row["dataset"], row["model"]): row for row in models}
    selected = min(candidates, key=lambda model: (sum(float(by_key[(dataset, model)]["balanced_bits_per_unit"]) for dataset in ("COREMA", "NUREMBERG")), model))
    check("selected_model", selected == freeze["selected"]["selected_model"] == result["selected_model"], selected)
    observed = sum(float(by_key[(dataset, selected)]["gain_vs_uniform_bits"]) for dataset in ("COREMA", "NUREMBERG"))
    check("aggregate_gain", math.isclose(observed, freeze["comparator_evidence"]["aggregate_gain_vs_uniform_bits"], abs_tol=1e-8), observed)
    positive_folds = sum(float(row["gain_vs_uniform_bits"]) > 0 for row in folds if row["model"] == selected)
    check("positive_folds", positive_folds == freeze["comparator_evidence"]["positive_folds"], positive_folds)
    task_positive = {dataset: float(by_key[(dataset, selected)]["gain_vs_uniform_bits"]) > 0 for dataset in ("COREMA", "NUREMBERG")}
    check("task_positive", task_positive == freeze["comparator_evidence"]["task_positive"], task_positive)
    frequency_gains = {dataset: float(by_key[(dataset, selected)]["gain_vs_uniform_bits"]) - float(by_key[(dataset, "FREQUENCY_DEGREE")]["gain_vs_uniform_bits"]) for dataset in ("COREMA", "NUREMBERG")}
    check("frequency_gains", all(math.isclose(frequency_gains[key], freeze["comparator_evidence"]["gain_over_frequency_by_task"][key], abs_tol=1e-8) for key in frequency_gains), frequency_gains)
    exceed = sum(float(row["max_three_gain_bits"]) >= observed - 1e-12 for row in null)
    p_value = (exceed + 1) / (len(null) + 1)
    check("null_p", math.isclose(p_value, freeze["comparator_evidence"]["max_three_diagnostic_p"], abs_tol=1e-15), p_value)
    selector_paid = observed - float(design["selection_charge_bits"])
    check("selector_paid", math.isclose(selector_paid, freeze["comparator_evidence"]["selector_paid_gain_bits"], abs_tol=1e-8), selector_paid)
    supported = all(task_positive.values()) and (selected == "FREQUENCY_DEGREE" or all(value > 0 for value in frequency_gains.values())) and positive_folds >= int(design["selection_gates"]["positive_folds_min"]) and selector_paid > 0 and p_value <= float(design["selection_gates"]["max3_p_max"])
    expected_status = "COMPARATOR_INVARIANT_SUPPORTED_AND_FROZEN" if supported else "NO_TRANSFERABLE_COMPARATOR_INVARIANT"
    check("decision", freeze["status"] == result["status"] == expected_status, expected_status)
    check("voynich_unread", freeze["voynich_outcomes_read_or_scored"] is False and result["voynich_outcomes_read_or_scored"] is False)
    check("opaque_only", result["opaque_ids_only"] is True and result["raw_position_shape_language_and_local_sequence_used"] is False)
    check("f84_all_false", all(value is False for value in freeze["f84"].values()))
    check("coefficient_dimensions", len(freeze["selected"]["anonymous_class_order"]) == 5 and all(len(row) == 5 for row in freeze["selected"]["beta"]))
    check("all_candidate_models_frozen", set(freeze["selected"]["frozen_candidate_models"]) == set(candidates))
    for path, digest in {**freeze["inputs"], **freeze["outputs"], **freeze["implementation"]}.items():
        check(f"freeze_hash:{path}", sha256_file(ROOT / path) == digest)
    for path, digest in {**result["inputs"], **result["outputs"], **result["implementation"]}.items():
        check(f"result_hash:{path}", sha256_file(ROOT / path) == digest)
    check("freeze_content_hash", content_hash(freeze) == freeze["content_sha256"])
    check("result_content_hash", content_hash(result) == result["content_sha256"])
    validation = {
        "schema": "GDT339_COMPARATOR_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "result_sha256": sha256_file(RESULT),
        "freeze_sha256": sha256_file(FREEZE),
        "source_reconstruction": {"corema_units": len(corema), "nuremberg_records": len(nuremberg_records), "nuremberg_units": nuremberg_units},
        "decision_reconstruction": {"selected": selected, "positive_folds": positive_folds, "max_three_p": p_value, "status": expected_status},
        "scope": "Independent source census, exported-score accounting, gates, hashes, and freeze dimensions; classifier optimization is not independently refit.",
        "checks": checks,
    }
    validation["content_sha256"] = hashlib.sha256(canonical(validation)).hexdigest()
    VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {expected_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
