#!/usr/bin/env python3
"""Independent source/accounting validator for final GDT339 application."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt339_comparator_first_semantic_incidence"
ART = EXP / "artifacts"
DESIGN = ART / "gdt339_comparator_design.json"
FREEZE = ART / "gdt339_invariant_freeze.json"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
PREDICTIONS = ART / "gdt339_voynich_tuple_folds.tsv"
FOLDS = ART / "gdt339_voynich_folio_scores.tsv"
REGISTERS = ART / "gdt339_voynich_register_scores.tsv"
MODELS = ART / "gdt339_voynich_model_scores.tsv"
NULL = ART / "gdt339_voynich_null.tsv"
COUNTER = ART / "gdt339_counterexamples.tsv"
RESULT = ART / "gdt339_result.json"
VALIDATION = ART / "gdt339_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def binomial_bits(hits: int, trials: int, probability: float) -> float:
    p = min(max(probability, 1e-12), 1 - 1e-12)
    return -hits * math.log2(p) - (trials - hits) * math.log2(1 - p)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    guard = GuardedTSV(SOURCE, selector_column="page", forbidden_action="error")
    source = list(guard)
    check("source_rows", len(source) == 8448, len(source))
    check("source_f84_zero", guard.stats.skipped_forbidden == 0 and not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source), guard.stats)
    check("source_fields", all(row["joint_tuple_id"] and row["physical_folio"] and row["record_ordinal"] for row in source))

    by_record: dict[str, set[str]] = defaultdict(set)
    record_folio: dict[str, str] = {}
    counts = Counter()
    records: dict[tuple[str, str], set[str]] = defaultdict(set)
    registers: dict[tuple[str, str], str] = {}
    for row in source:
        record = f"{row['page']}|{row['record_ordinal']}"
        ident = row["joint_tuple_id"]
        folio = row["physical_folio"]
        by_record[record].add(ident)
        record_folio[record] = folio
        counts[(ident, folio)] += 1
        records[(ident, folio)].add(record)
        registers[(ident, folio)] = row["register"]
    partners: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record, identities in by_record.items():
        folio = record_folio[record]
        for ident in identities:
            partners[(ident, folio)].update(identities - {ident})
    folios_by_tuple: dict[str, set[str]] = defaultdict(set)
    for ident, folio in counts:
        folios_by_tuple[ident].add(folio)
    all_folios = sorted({folio for _, folio in counts})
    check("physical_folios_nonempty", len(all_folios) > 20, len(all_folios))

    predictions = read_tsv(PREDICTIONS)
    expected: set[tuple[str, str]] = set()
    for held in all_folios:
        for ident, folios in folios_by_tuple.items():
            if held in folios and len(folios - {held}) >= 2 and len(records[(ident, held)]) >= 2 and partners[(ident, held)]:
                expected.add((held, ident))
    actual = {(row["held_folio"], row["joint_tuple_id"]) for row in predictions}
    check("eligible_tuple_fold_set", actual == expected, f"actual={len(actual)} expected={len(expected)}")
    check("prediction_unique", len(actual) == len(predictions), len(predictions))
    for row in predictions:
        held = row["held_folio"]
        ident = row["joint_tuple_id"]
        training_folios = folios_by_tuple[ident] - {held}
        training_partners = set().union(*(partners[(ident, folio)] for folio in training_folios))
        held_partners = partners[(ident, held)]
        check(f"register:{held}:{ident}", row["register"] == registers[(ident, held)])
        check(f"training_occurrences:{held}:{ident}", int(row["training_occurrences"]) == sum(counts[(ident, folio)] for folio in training_folios))
        check(f"training_folios:{held}:{ident}", int(row["training_folios"]) == len(training_folios))
        check(f"held_records:{held}:{ident}", int(row["held_records"]) == len(records[(ident, held)]))
        check(f"partner_outcome:{held}:{ident}", int(row["hits"]) == len(held_partners & training_partners) and int(row["trials"]) == len(held_partners))
        check(f"anonymous_class:{held}:{ident}", row["anonymous_class"] in {"C0", "C1", "C2", "C3", "C4"})
        check(f"probability_bounds:{held}:{ident}", all(0 < float(row[name]) < 1 for name in ("p_register_frequency", "p_comparator_class", "p_exact_tuple")))
        check(f"unassigned:{held}:{ident}", row["semantic_state"] == "UNASSIGNED" and row["translation_state"] == "UNASSIGNED")

    names = ("register_frequency", "comparator_class", "exact_tuple")
    bits = {name: sum(binomial_bits(int(row["hits"]), int(row["trials"]), float(row[f"p_{name}"])) for row in predictions) for name in names}
    models = read_tsv(MODELS)
    check("model_rows", {row["model"] for row in models} == set(names), len(models))
    for row in models:
        name = row["model"]
        check(f"model_bits:{name}", math.isclose(float(row["held_bits"]), bits[name], abs_tol=2e-8), bits[name])
        check(f"model_gain:{name}", math.isclose(float(row["gain_vs_register_frequency_bits"]), bits["register_frequency"] - bits[name], abs_tol=2e-8))

    def verify_grouped(path: Path, key: str) -> list[dict[str, str]]:
        exported = read_tsv(path)
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in predictions:
            grouped[row[key]].append(row)
        check(f"{key}_strata", {row["stratum"] for row in exported} == set(grouped))
        for row in exported:
            members = grouped[row["stratum"]]
            base = sum(binomial_bits(int(item["hits"]), int(item["trials"]), float(item["p_register_frequency"])) for item in members)
            candidate = sum(binomial_bits(int(item["hits"]), int(item["trials"]), float(item["p_comparator_class"])) for item in members)
            exact = sum(binomial_bits(int(item["hits"]), int(item["trials"]), float(item["p_exact_tuple"])) for item in members)
            check(f"{key}_score:{row['stratum']}", math.isclose(float(row["class_gain_bits"]), base - candidate, abs_tol=2e-8) and math.isclose(float(row["exact_tuple_gain_bits"]), base - exact, abs_tol=2e-8))
        return exported

    folio_rows = verify_grouped(FOLDS, "held_folio")
    register_rows = verify_grouped(REGISTERS, "register")
    observed = bits["register_frequency"] - bits["comparator_class"]
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(predictions):
        groups[(row["register"], row["training_frequency_bin"])].append(index)
    null = read_tsv(NULL)
    check("null_worlds", len(null) == int(design["voynich_scoring"]["null_worlds"]), len(null))
    exceed = 0
    for world, exported in enumerate(null):
        check(f"null_world_id:{world}", int(exported["world"]) == world)
        rng = random.Random(int(design["voynich_scoring"]["null_seed"]) * 1_000_003 + world)
        permuted = [float(row["p_comparator_class"]) for row in predictions]
        for indices in groups.values():
            values = [permuted[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                permuted[index] = value
        null_bits = sum(binomial_bits(int(row["hits"]), int(row["trials"]), permuted[index]) for index, row in enumerate(predictions))
        gain = bits["register_frequency"] - null_bits
        check(f"null_gain:{world}", math.isclose(float(exported["permuted_class_gain_bits"]), gain, abs_tol=2e-8))
        exceed += gain >= observed - 1e-12
    p_value = (exceed + 1) / (len(null) + 1)
    positive_folios = sum(float(row["class_gain_bits"]) > 0 for row in folio_rows)
    summary = {"tuple_fold_tests": len(predictions), "partner_trials": sum(int(row["trials"]) for row in predictions), "physical_folios": len(folio_rows), "registers": len(register_rows), "exact_tuples": len({row["joint_tuple_id"] for row in predictions})}
    check("result_counts", result["counts"] == summary, summary)
    check("result_gain", math.isclose(result["voynich"]["raw_gain_bits"], observed, abs_tol=2e-8))
    check("result_paid_gain", math.isclose(result["voynich"]["selector_paid_gain_bits"], observed - float(design["voynich_scoring"]["model_selector_bits"]), abs_tol=2e-8))
    check("result_p", math.isclose(result["voynich"]["permutation_p"], p_value, abs_tol=1e-15), p_value)
    check("result_positive_folios", result["voynich"]["positive_folios"] == positive_folios, positive_folios)
    gates = design["voynich_capacity_gates"]
    capacity = summary["tuple_fold_tests"] >= int(gates["tuple_fold_tests_min"]) and summary["physical_folios"] >= int(gates["physical_folios_min"]) and summary["registers"] >= int(gates["registers_min"])
    candidate = capacity and observed - float(design["voynich_scoring"]["model_selector_bits"]) > 0 and positive_folios / summary["physical_folios"] >= float(gates["positive_folio_fraction_min"]) and p_value <= float(gates["max_family_p_max"])
    comparator = freeze["status"] == "COMPARATOR_INVARIANT_SUPPORTED_AND_FROZEN"
    expected_status = "NO_TRANSFERABLE_COMPARATOR_INVARIANT" if not comparator else ("ANONYMOUS_INCIDENCE_CLASS_STABILITY_PROVISIONAL" if candidate else "COMPARATOR_INVARIANT_VOYNICH_STABILITY_NOT_SUPPORTED")
    check("status", result["status"] == expected_status, expected_status)
    check("gate_vector", result["gates"] == {"comparator": comparator, "capacity": capacity, "voynich": candidate})
    check("no_assignments", result["semantic_assignments"] == result["translation_assignments"] == result["tuple_merges"] == 0)
    check("f84_false", result["source_access"]["f84_opened_parsed_retained_joined_or_scored"] is False)
    check("counterexamples", len(read_tsv(COUNTER)) >= 6)
    for path, digest in {**result["inputs"], **result["documents"], **result["implementation"], **result["outputs"]}.items():
        check(f"hash:{path}", sha256_file(ROOT / path) == digest)
    copy = dict(result)
    claimed = copy.pop("content_sha256")
    check("result_content_hash", hashlib.sha256(canonical_json_bytes(copy)).hexdigest() == claimed)
    check("prediction_f84_absent", all(not row["held_folio"].startswith("f84") for row in predictions))
    check("folio_score_f84_absent", all(row["stratum_type"] != "held_folio" or not row["stratum"].startswith("f84") for row in folio_rows))
    validation = {
        "schema": "GDT339_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "result_sha256": sha256_file(RESULT),
        "source_reconstruction": summary,
        "score_reconstruction": {"class_gain_bits": observed, "positive_folios": positive_folios, "permutation_p": p_value, "status": expected_status},
        "scope": "Nonimporting exact source eligibility, partner outcomes, codelength, strata, fixed-prediction null, gates and hashes. Frozen comparator class coefficients and corpus-calibrated probability cells are not independently refit.",
        "checks": checks,
    }
    validation["content_sha256"] = hashlib.sha256(canonical_json_bytes(validation)).hexdigest()
    VALIDATION.write_bytes(canonical_json_bytes(validation))
    print(f"PASS {len(checks)}/{len(checks)} {expected_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
