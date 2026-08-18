#!/usr/bin/env python3
"""Independent reconstruction validator for GDT338 (does not import runner)."""

from __future__ import annotations

import csv
import hashlib
import json
import math
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


EXP = ROOT / "experiments/yolo/gdt338_renderer_invariant_equivalence"
ART = EXP / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
FOLDS336 = ROOT / "gdt336_folds.tsv"
DESIGN = ART / "gdt338_design.json"
CAPACITY = ART / "gdt338_capacity.tsv"
FREEZE = ART / "gdt338_freeze.json"
PREDICTIONS = ART / "gdt338_holdout_predictions.tsv"
MODELS = ART / "gdt338_model_scores.tsv"
FOLIO = ART / "gdt338_folio_scores.tsv"
REGISTER = ART / "gdt338_register_scores.tsv"
LENGTH = ART / "gdt338_length_scores.tsv"
NULL = ART / "gdt338_null.tsv"
CLASSES = ART / "gdt338_equivalence_classes.tsv"
COUNTER = ART / "gdt338_counterexamples.tsv"
RESULT = ART / "gdt338_result.json"
VALIDATION = ART / "gdt338_validation.json"
WRAPPERS = ("NONE", "ch", "che", "d", "q", "s", "sh", "t")
WRAPPER_MODELS = (
    "REGISTER_TWO_RULE",
    "COORDINATE_TWO_RULE",
    "COORDINATE_CONTEXT_TABLE",
    "REGISTER_MARKOV_TWO_RULE",
    "JOINT_NO_RULE",
    "JOINT_TWO_RULE",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def stable_id(prefix: str, value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return prefix + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def place(row: dict[str, str]) -> tuple[str, str, str]:
    index = int(row["group_index"])
    count = int(row["group_count"])
    return row["line_first"], row["within_field_position"], str(min(3, int(4 * (index - 1) / max(1, count))))


def probabilities(counts: Counter[str], row: dict[str, str], beta_s: float, beta_q: float) -> dict[str, float]:
    score = {wrapper: math.log(counts[wrapper] + 0.5) for wrapper in WRAPPERS}
    score["s"] += beta_s * int(row["line_first"])
    score["q"] += beta_q * int(row["prev_dy"])
    offset = max(score.values())
    weight = {wrapper: math.exp(value - offset) for wrapper, value in score.items()}
    total = sum(weight.values())
    return {wrapper: value / total for wrapper, value in weight.items()}


def choose_wrapper(prob: dict[str, float]) -> str:
    return max(WRAPPERS, key=lambda value: (prob[value], -WRAPPERS.index(value)))


def choose_tuple(prob: dict[str, float]) -> str:
    return max(sorted(prob), key=lambda value: (prob[value], value))


def near(a: float, b: float, tolerance: float = 5e-9) -> bool:
    return abs(a - b) <= tolerance


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    capacity = read_tsv(CAPACITY)
    published_predictions = read_tsv(PREDICTIONS)
    model_rows = read_tsv(MODELS)
    null_rows = read_tsv(NULL)
    alpha_rows = read_tsv(FOLDS336)
    alpha_by_fold = {(row["register"], row["held_folio"]): int(row["selected_alpha"]) for row in alpha_rows}
    guard = GuardedTSV(INTER, selector_column="page", forbidden_action="error")
    rows = list(guard)
    check("source_rows", len(rows) == 8448, len(rows))
    check("source_guard_no_f84", guard.stats.skipped_forbidden == 0 and all(not row["page"].startswith("f84") for row in rows))

    grouped: dict[tuple[str, str, str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["register"], row["physical_folio"], row["page"], row["locus"], int(row["field_ordinal"]))
        grouped[key].append(row)
    fields = []
    previous: dict[str, str] = {}
    for key, members in sorted(grouped.items()):
        members.sort(key=lambda row: int(row["group_index"]))
        for index, row in enumerate(members):
            previous[row["event_id_sha256"]] = "<START>" if index == 0 else members[index - 1]["observed_wrapper"]
        normalized = tuple(row["joint_tuple_id"] for row in members)
        rendered = tuple((row["observed_wrapper"], row["joint_tuple_id"]) for row in members)
        fields.append(
            {
                "key": key,
                "field_id": stable_id("FLD", key),
                "class_id": stable_id("NEQ", normalized),
                "register_class_cell_id": stable_id("NRC", (key[0], normalized)),
                "register": key[0],
                "folio": key[1],
                "normalized": normalized,
                "rendered": rendered,
                "members": members,
                "powered": all(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in members),
            }
        )
    field_by_id = {field["field_id"]: field for field in fields}

    reconstructed_capacity = []
    for held in fields:
        if not held["powered"]:
            continue
        training = [
            field
            for field in fields
            if field["register"] == held["register"] and field["folio"] != held["folio"] and field["powered"]
        ]
        if held["rendered"] in {field["rendered"] for field in training}:
            continue
        same = [field for field in training if field["normalized"] == held["normalized"]]
        if len({field["folio"] for field in same}) < 2 or len({field["rendered"] for field in same}) < 2:
            continue
        reconstructed_capacity.append(held["field_id"])
    check("capacity_exact_ids", reconstructed_capacity == [row["field_id"] for row in capacity], len(reconstructed_capacity))
    counts = {
        "fields": len(capacity),
        "group_events": sum(len(field_by_id[row["field_id"]]["members"]) for row in capacity),
        "physical_folios": len({row["physical_folio"] for row in capacity}),
        "normalized_classes": len({row["class_id"] for row in capacity}),
        "register_class_cells": len({row["register_class_cell_id"] for row in capacity}),
        "registers": len({row["register"] for row in capacity}),
        "one_group_fields": sum(int(row["group_count"]) == 1 for row in capacity),
        "two_group_fields": sum(int(row["group_count"]) == 2 for row in capacity),
    }
    check("capacity_counts", counts == freeze["counts"] == result["counts"], counts)
    check("capacity_surfaces_unseen", all(row["held_surface_seen_in_training"] == "NO" for row in capacity))

    beta_s = float(design["fixed_renderer_coefficients"]["s_line_first"])
    beta_q = float(design["fixed_renderer_coefficients"]["q_prev_dy"])
    reconstructed: list[dict[str, object]] = []
    for capacity_row in capacity:
        field = field_by_id[capacity_row["field_id"]]
        register = field["register"]
        folio = field["folio"]
        training = [row for row in rows if row["register"] == register and row["physical_folio"] != folio]
        register_counts: Counter[str] = Counter()
        coordinate_counts: dict[str, Counter[str]] = defaultdict(Counter)
        context_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
        markov_counts: dict[str, Counter[str]] = defaultdict(Counter)
        joint_counts: dict[str, Counter[str]] = defaultdict(Counter)
        base_counts: Counter[tuple[str, str]] = Counter()
        placed_counts: Counter[tuple[str, tuple[str, str, str], str]] = Counter()
        candidates: dict[str, set[str]] = defaultdict(set)
        for row in training:
            wrapper = row["observed_wrapper"]
            coordinate = row["coordinate_id"]
            joint = row["joint_tuple_id"]
            register_counts[wrapper] += 1
            coordinate_counts[coordinate][wrapper] += 1
            context_counts[(coordinate, row["line_first"], row["prev_dy"])][wrapper] += 1
            markov_counts[previous[row["event_id_sha256"]]][wrapper] += 1
            joint_counts[joint][wrapper] += 1
            base_counts[(coordinate, joint)] += 1
            placed_counts[(coordinate, place(row), joint)] += 1
            candidates[coordinate].add(joint)
        alpha = alpha_by_fold[(register, folio)]
        for member in field["members"]:
            coordinate = member["coordinate_id"]
            context = (coordinate, member["line_first"], member["prev_dy"])
            coordinate_counter = coordinate_counts[coordinate] or register_counts
            context_counter = context_counts[context] or coordinate_counter
            markov_counter = markov_counts[previous[member["event_id_sha256"]]] or register_counts
            wp = {
                "REGISTER_TWO_RULE": probabilities(register_counts, member, beta_s, beta_q),
                "COORDINATE_TWO_RULE": probabilities(coordinate_counter, member, beta_s, beta_q),
                "COORDINATE_CONTEXT_TABLE": probabilities(context_counter, member, 0.0, 0.0),
                "REGISTER_MARKOV_TWO_RULE": probabilities(markov_counter, member, beta_s, beta_q),
                "JOINT_NO_RULE": probabilities(joint_counts[member["joint_tuple_id"]], member, 0.0, 0.0),
                "JOINT_TWO_RULE": probabilities(joint_counts[member["joint_tuple_id"]], member, beta_s, beta_q),
            }
            cand = sorted(candidates[coordinate])
            check("held_tuple_in_training", member["joint_tuple_id"] in cand, member["event_id_sha256"])
            base_total = sum(base_counts[(coordinate, value)] for value in cand)
            base = {
                value: (base_counts[(coordinate, value)] + 0.5) / (base_total + 0.5 * len(cand)) for value in cand
            }
            pkey = place(member)
            ptotal = sum(placed_counts[(coordinate, pkey, value)] for value in cand)
            placed = {
                value: (placed_counts[(coordinate, pkey, value)] + alpha * base[value]) / (ptotal + alpha)
                for value in cand
            }
            reconstructed.append(
                {
                    "field_id": field["field_id"],
                    "event_id": member["event_id_sha256"],
                    "wrapper": member["observed_wrapper"],
                    "tuple": member["joint_tuple_id"],
                    "wp": wp,
                    "tp": {"COORDINATE": base, "PLACEMENT": placed},
                }
            )
    check("prediction_row_count", len(reconstructed) == len(published_predictions) == 32, len(reconstructed))
    published_by_event = {row["event_id"]: row for row in published_predictions}
    for prediction in reconstructed:
        published = published_by_event[prediction["event_id"]]
        check("prediction_field_id", published["field_id"] == prediction["field_id"], prediction["event_id"])
        check("wrapper_top1_candidate", published["candidate_wrapper_top1"] == choose_wrapper(prediction["wp"]["JOINT_TWO_RULE"]), prediction["event_id"])
        check("wrapper_probability_candidate", near(float(published["candidate_wrapper_probability"]), prediction["wp"]["JOINT_TWO_RULE"][prediction["wrapper"]]), prediction["event_id"])
        check("tuple_top1_placement", published["placement_top1_tuple_id"] == choose_tuple(prediction["tp"]["PLACEMENT"]), prediction["event_id"])
        check("tuple_probability_placement", near(float(published["placement_probability"]), prediction["tp"]["PLACEMENT"][prediction["tuple"]]), prediction["event_id"])

    model_index = {(row["channel"], row["model"]): row for row in model_rows}
    bits: dict[tuple[str, str], float] = {}
    tops: dict[tuple[str, str], int] = {}
    exact: dict[tuple[str, str], int] = {}
    for channel, models in (("WRAPPER", WRAPPER_MODELS), ("PLACEMENT", ("COORDINATE", "PLACEMENT"))):
        for model in models:
            total = 0.0
            top = 0
            field_flags: dict[str, list[bool]] = defaultdict(list)
            for prediction in reconstructed:
                truth = prediction["wrapper"] if channel == "WRAPPER" else prediction["tuple"]
                prob = prediction["wp"][model] if channel == "WRAPPER" else prediction["tp"][model]
                total -= math.log2(prob[truth])
                chosen = choose_wrapper(prob) if channel == "WRAPPER" else choose_tuple(prob)
                correct = chosen == truth
                top += int(correct)
                field_flags[prediction["field_id"]].append(correct)
            bits[(channel, model)] = total
            tops[(channel, model)] = top
            exact[(channel, model)] = sum(all(flags) for flags in field_flags.values())
            published = model_index[(channel, model)]
            check(f"model_bits:{channel}:{model}", near(total, float(published["held_bits"])), total)
            check(f"model_top1:{channel}:{model}", top == int(published["group_top1"]), top)
            check(f"model_exact:{channel}:{model}", exact[(channel, model)] == int(published["exact_field_top1"]), exact[(channel, model)])

    best_baseline = min(
        (model for model in WRAPPER_MODELS if model != "JOINT_TWO_RULE"),
        key=lambda model: (bits[("WRAPPER", model)], model),
    )
    wrapper_gain = bits[("WRAPPER", best_baseline)] - bits[("WRAPPER", "JOINT_TWO_RULE")]
    placement_gain = bits[("PLACEMENT", "COORDINATE")] - bits[("PLACEMENT", "PLACEMENT")]
    check("best_wrapper_baseline", best_baseline == result["wrapper"]["best_baseline"], best_baseline)
    check("wrapper_gain", near(wrapper_gain, result["wrapper"]["raw_gain_bits"]), wrapper_gain)
    check("placement_gain", near(placement_gain, result["placement"]["raw_gain_bits"]), placement_gain)
    check("selector_charge_wrapper", near(result["wrapper"]["selector_paid_gain_bits"], wrapper_gain - math.log2(6)))
    check("selector_charge_placement", near(result["placement"]["selector_paid_gain_bits"], placement_gain - 1.0))

    check("null_worlds", len(null_rows) == int(design["null"]["worlds"]), len(null_rows))
    wrapper_p = (1 + sum(float(row["max_two_gain_bits"]) >= wrapper_gain - 1e-12 for row in null_rows)) / (len(null_rows) + 1)
    placement_p = (1 + sum(float(row["max_two_gain_bits"]) >= placement_gain - 1e-12 for row in null_rows)) / (len(null_rows) + 1)
    check("wrapper_p", near(wrapper_p, result["wrapper"]["max_two_diagnostic_p"]), wrapper_p)
    check("placement_p", near(placement_p, result["placement"]["max_two_diagnostic_p"]), placement_p)

    register_rows = read_tsv(REGISTER)
    folio_rows = read_tsv(FOLIO)
    check("register_count", len(register_rows) == 3, len(register_rows))
    check("folio_count", len(folio_rows) == 17, len(folio_rows))
    check("length_strata", {row["stratum"] for row in read_tsv(LENGTH)} == {"1", "2"})
    check("class_count", len(read_tsv(CLASSES)) == 9)
    check("counterexamples", len(read_tsv(COUNTER)) == 6)
    check("semantic_unassigned", all(row["semantic_state"] == "UNASSIGNED" for row in capacity + published_predictions))
    check("f84_flag", result["source_access"]["f84_opened_parsed_retained_joined_or_scored"] is False)
    check("no_semantics", result["semantic_assignments"] == 0 and result["translation_assignments"] == 0)

    for mapping_name in ("inputs", "documents", "implementation", "outputs"):
        for relative, digest in result[mapping_name].items():
            check(f"hash:{relative}", sha256_file(ROOT / relative) == digest)
    content = dict(result)
    content_hash = content.pop("content_sha256")
    check("result_content_hash", hashlib.sha256(canonical_json_bytes(content)).hexdigest() == content_hash)
    check("result_status_allowed", result["status"] in design["decision_statuses"], result["status"])

    validation = {
        "schema": "GDT338_VALIDATION_V1",
        "experiment": "GDT338",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "checks": checks,
        "scope": "Independent source-panel, eligibility, score, prediction, decision, hash, and seal reconstruction without importing the producer.",
        "result_sha256": sha256_file(RESULT),
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
    }
    VALIDATION.write_bytes(canonical_json_bytes(validation))
    print(json.dumps({"status": "PASS", "checks": len(checks)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
