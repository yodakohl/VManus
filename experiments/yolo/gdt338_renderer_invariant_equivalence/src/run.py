#!/usr/bin/env python3
"""Run the frozen GDT338 held-folio renderer-equivalence test."""

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


EXP = ROOT / "experiments/yolo/gdt338_renderer_invariant_equivalence"
ART = EXP / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
FOLDS336 = ROOT / "gdt336_folds.tsv"
DESIGN = ART / "gdt338_design.json"
CAPACITY = ART / "gdt338_capacity.tsv"
FREEZE = ART / "gdt338_freeze.json"
METHOD = EXP / "METHOD.md"
REPORT = EXP / "REPORT.md"
CLASSES = ART / "gdt338_equivalence_classes.tsv"
PREDICTIONS = ART / "gdt338_holdout_predictions.tsv"
MODELS = ART / "gdt338_model_scores.tsv"
FOLIO_SCORES = ART / "gdt338_folio_scores.tsv"
REGISTER_SCORES = ART / "gdt338_register_scores.tsv"
LENGTH_SCORES = ART / "gdt338_length_scores.tsv"
NULL = ART / "gdt338_null.tsv"
COUNTER = ART / "gdt338_counterexamples.tsv"
RESULT = ART / "gdt338_result.json"
WRAPPERS = ("NONE", "ch", "che", "d", "q", "s", "sh", "t")
WRAPPER_MODELS = (
    "REGISTER_TWO_RULE",
    "COORDINATE_TWO_RULE",
    "COORDINATE_CONTEXT_TABLE",
    "REGISTER_MARKOV_TWO_RULE",
    "JOINT_NO_RULE",
    "JOINT_TWO_RULE",
)
PLACEMENT_MODELS = ("COORDINATE", "PLACEMENT")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError(f"fieldnames required for empty table {path}")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_id(prefix: str, value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return prefix + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def place(row: dict[str, str]) -> tuple[str, str, str]:
    group_index = int(row["group_index"])
    group_count = int(row["group_count"])
    quartile = str(min(3, int(4 * (group_index - 1) / max(1, group_count))))
    return row["line_first"], row["within_field_position"], quartile


def softmax_counts(
    counts: Counter[str], line_first: str, prev_dy: str, beta_s: float, beta_q: float
) -> dict[str, float]:
    scores = [math.log(counts[wrapper] + 0.5) for wrapper in WRAPPERS]
    scores[WRAPPERS.index("s")] += beta_s * int(line_first)
    scores[WRAPPERS.index("q")] += beta_q * int(prev_dy)
    offset = max(scores)
    weights = [math.exp(score - offset) for score in scores]
    total = sum(weights)
    return {wrapper: weight / total for wrapper, weight in zip(WRAPPERS, weights)}


def argmax_key(probabilities: dict[str, float]) -> str:
    return max(WRAPPERS, key=lambda wrapper: (probabilities[wrapper], -WRAPPERS.index(wrapper)))


def tuple_argmax(probabilities: dict[str, float]) -> str:
    return max(sorted(probabilities), key=lambda value: (probabilities[value], value))


def grouped_fields(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, str]]:
    grouped: dict[tuple[str, str, str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["register"],
            row["physical_folio"],
            row["page"],
            row["locus"],
            int(row["field_ordinal"]),
        )
        grouped[key].append(row)
    fields: list[dict[str, object]] = []
    previous_wrapper: dict[str, str] = {}
    for key, members in sorted(grouped.items()):
        members.sort(key=lambda row: int(row["group_index"]))
        for index, row in enumerate(members):
            previous_wrapper[row["event_id_sha256"]] = "<START>" if index == 0 else members[index - 1]["observed_wrapper"]
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
                "page": key[2],
                "locus": key[3],
                "field_ordinal": key[4],
                "rows": members,
                "normalized": normalized,
                "rendered": rendered,
                "group_count": len(members),
                "powered": all(row["renderer_state"] == "EXECUTABLE_POWERED_CELL" for row in members),
            }
        )
    return fields, previous_wrapper


def build_fold(
    register: str,
    held_folio: str,
    rows: list[dict[str, str]],
    fields: list[dict[str, object]],
    previous_wrapper: dict[str, str],
) -> dict[str, object]:
    training = [row for row in rows if row["register"] == register and row["physical_folio"] != held_folio]
    register_counts: Counter[str] = Counter()
    coordinate_counts: dict[str, Counter[str]] = defaultdict(Counter)
    context_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    markov_counts: dict[str, Counter[str]] = defaultdict(Counter)
    joint_counts: dict[str, Counter[str]] = defaultdict(Counter)
    base_counts: Counter[tuple[str, str]] = Counter()
    placement_counts: Counter[tuple[str, tuple[str, str, str], str]] = Counter()
    candidates: dict[str, set[str]] = defaultdict(set)
    for row in training:
        wrapper = row["observed_wrapper"]
        coordinate = row["coordinate_id"]
        joint = row["joint_tuple_id"]
        register_counts[wrapper] += 1
        coordinate_counts[coordinate][wrapper] += 1
        context_counts[(coordinate, row["line_first"], row["prev_dy"])][wrapper] += 1
        markov_counts[previous_wrapper[row["event_id_sha256"]]][wrapper] += 1
        joint_counts[joint][wrapper] += 1
        base_counts[(coordinate, joint)] += 1
        placement_counts[(coordinate, place(row), joint)] += 1
        candidates[coordinate].add(joint)
    training_fields = [
        field
        for field in fields
        if field["register"] == register and field["folio"] != held_folio and field["powered"]
    ]
    return {
        "register_counts": register_counts,
        "coordinate_counts": coordinate_counts,
        "context_counts": context_counts,
        "markov_counts": markov_counts,
        "joint_counts": joint_counts,
        "base_counts": base_counts,
        "placement_counts": placement_counts,
        "candidates": candidates,
        "training_fields": training_fields,
    }


def wrapper_probabilities(
    row: dict[str, str], previous: str, fold: dict[str, object], beta_s: float, beta_q: float
) -> dict[str, dict[str, float]]:
    register_counts = fold["register_counts"]
    coordinate_counts = fold["coordinate_counts"]
    context_counts = fold["context_counts"]
    markov_counts = fold["markov_counts"]
    joint_counts = fold["joint_counts"]
    coordinate = row["coordinate_id"]
    context = (coordinate, row["line_first"], row["prev_dy"])
    coordinate_counter = coordinate_counts[coordinate] or register_counts
    context_counter = context_counts[context] or coordinate_counter
    markov_counter = markov_counts[previous] or register_counts
    joint_counter = joint_counts[row["joint_tuple_id"]]
    if not joint_counter:
        raise AssertionError("held normalized class did not supply training joint counts")
    return {
        "REGISTER_TWO_RULE": softmax_counts(register_counts, row["line_first"], row["prev_dy"], beta_s, beta_q),
        "COORDINATE_TWO_RULE": softmax_counts(coordinate_counter, row["line_first"], row["prev_dy"], beta_s, beta_q),
        "COORDINATE_CONTEXT_TABLE": softmax_counts(context_counter, "0", "0", 0.0, 0.0),
        "REGISTER_MARKOV_TWO_RULE": softmax_counts(markov_counter, row["line_first"], row["prev_dy"], beta_s, beta_q),
        "JOINT_NO_RULE": softmax_counts(joint_counter, "0", "0", 0.0, 0.0),
        "JOINT_TWO_RULE": softmax_counts(joint_counter, row["line_first"], row["prev_dy"], beta_s, beta_q),
    }


def placement_probabilities(
    row: dict[str, str], fold: dict[str, object], alpha: int
) -> dict[str, dict[str, float]]:
    coordinate = row["coordinate_id"]
    candidates = sorted(fold["candidates"][coordinate])
    if row["joint_tuple_id"] not in candidates:
        raise AssertionError("held normalized tuple missing from training candidates")
    base_counts = fold["base_counts"]
    placement_counts = fold["placement_counts"]
    base_total = sum(base_counts[(coordinate, candidate)] for candidate in candidates)
    base = {
        candidate: (base_counts[(coordinate, candidate)] + 0.5) / (base_total + 0.5 * len(candidates))
        for candidate in candidates
    }
    position = place(row)
    placement_total = sum(placement_counts[(coordinate, position, candidate)] for candidate in candidates)
    placed = {
        candidate: (placement_counts[(coordinate, position, candidate)] + alpha * base[candidate])
        / (placement_total + alpha)
        for candidate in candidates
    }
    return {"COORDINATE": base, "PLACEMENT": placed}


def summarize_channel(
    predictions: list[dict[str, object]], channel: str, models: tuple[str, ...]
) -> tuple[list[dict[str, object]], dict[str, dict[str, float]]]:
    rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, float]] = {}
    truth_key = "wrapper_truth" if channel == "WRAPPER" else "tuple_truth"
    for model in models:
        bits = 0.0
        top1 = 0
        field_correct: dict[str, bool] = defaultdict(lambda: True)
        for prediction in predictions:
            probabilities = prediction[f"{channel.lower()}_probabilities"][model]
            truth = prediction[truth_key]
            bits -= math.log2(max(probabilities[truth], 1e-300))
            chosen = argmax_key(probabilities) if channel == "WRAPPER" else tuple_argmax(probabilities)
            correct = chosen == truth
            top1 += int(correct)
            field_correct[prediction["field_id"]] &= correct
        exact_fields = sum(field_correct.values())
        summaries[model] = {"bits": bits, "top1": top1, "exact_fields": exact_fields}
        rows.append(
            {
                "channel": channel,
                "model": model,
                "group_events": len(predictions),
                "fields": len(field_correct),
                "held_bits": f"{bits:.12f}",
                "bits_per_group": f"{bits / len(predictions):.12f}",
                "group_top1": top1,
                "exact_field_top1": exact_fields,
                "semantic_state": "UNASSIGNED",
            }
        )
    return rows, summaries


def gain_by_stratum(
    predictions: list[dict[str, object]], key: str, wrapper_baseline: str
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for prediction in predictions:
        grouped[str(prediction[key])].append(prediction)
    output: list[dict[str, object]] = []
    for value, members in sorted(grouped.items()):
        wrapper_base_bits = wrapper_candidate_bits = placement_base_bits = placement_bits = 0.0
        wrapper_base_top = wrapper_candidate_top = placement_base_top = placement_top = 0
        wrapper_fields: dict[str, list[bool]] = defaultdict(list)
        placement_fields: dict[str, list[bool]] = defaultdict(list)
        for prediction in members:
            wrapper_truth = prediction["wrapper_truth"]
            wp = prediction["wrapper_probabilities"]
            wrapper_base_bits -= math.log2(wp[wrapper_baseline][wrapper_truth])
            wrapper_candidate_bits -= math.log2(wp["JOINT_TWO_RULE"][wrapper_truth])
            wb = argmax_key(wp[wrapper_baseline]) == wrapper_truth
            wc = argmax_key(wp["JOINT_TWO_RULE"]) == wrapper_truth
            wrapper_base_top += int(wb)
            wrapper_candidate_top += int(wc)
            wrapper_fields[prediction["field_id"]].append(wb)
            wrapper_fields[prediction["field_id"]].append(wc)
            tuple_truth = prediction["tuple_truth"]
            tp = prediction["placement_probabilities"]
            placement_base_bits -= math.log2(tp["COORDINATE"][tuple_truth])
            placement_bits -= math.log2(tp["PLACEMENT"][tuple_truth])
            pb = tuple_argmax(tp["COORDINATE"]) == tuple_truth
            pc = tuple_argmax(tp["PLACEMENT"]) == tuple_truth
            placement_base_top += int(pb)
            placement_top += int(pc)
            placement_fields[prediction["field_id"]].append(pb)
            placement_fields[prediction["field_id"]].append(pc)
        wrapper_base_exact = sum(all(flags[::2]) for flags in wrapper_fields.values())
        wrapper_candidate_exact = sum(all(flags[1::2]) for flags in wrapper_fields.values())
        placement_base_exact = sum(all(flags[::2]) for flags in placement_fields.values())
        placement_exact = sum(all(flags[1::2]) for flags in placement_fields.values())
        output.append(
            {
                "stratum_type": key,
                "stratum": value,
                "fields": len(wrapper_fields),
                "group_events": len(members),
                "wrapper_baseline": wrapper_baseline,
                "wrapper_baseline_bits": f"{wrapper_base_bits:.12f}",
                "wrapper_candidate_bits": f"{wrapper_candidate_bits:.12f}",
                "wrapper_gain_bits": f"{wrapper_base_bits - wrapper_candidate_bits:.12f}",
                "wrapper_baseline_group_top1": wrapper_base_top,
                "wrapper_candidate_group_top1": wrapper_candidate_top,
                "wrapper_baseline_exact_fields": wrapper_base_exact,
                "wrapper_candidate_exact_fields": wrapper_candidate_exact,
                "coordinate_bits": f"{placement_base_bits:.12f}",
                "placement_bits": f"{placement_bits:.12f}",
                "placement_gain_bits": f"{placement_base_bits - placement_bits:.12f}",
                "coordinate_group_top1": placement_base_top,
                "placement_group_top1": placement_top,
                "coordinate_exact_fields": placement_base_exact,
                "placement_exact_fields": placement_exact,
            }
        )
    return output


def permutation_groups(predictions: list[dict[str, object]], fields: tuple[str, ...]) -> list[list[int]]:
    grouped: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, prediction in enumerate(predictions):
        grouped[tuple(str(prediction[field]) for field in fields)].append(index)
    return [indices for _, indices in sorted(grouped.items())]


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    capacity = read_tsv(CAPACITY)
    guard = GuardedTSV(INTER, selector_column="page", forbidden_action="error")
    rows = list(guard)
    if len(rows) != 8448 or guard.stats.skipped_forbidden:
        raise AssertionError((len(rows), guard.stats))
    fields, previous_wrapper = grouped_fields(rows)
    field_by_id = {field["field_id"]: field for field in fields}
    if set(field_by_id) < {row["field_id"] for row in capacity}:
        raise AssertionError("frozen capacity field missing")
    alpha_rows = read_tsv(FOLDS336)
    alpha_by_fold = {(row["register"], row["held_folio"]): int(row["selected_alpha"]) for row in alpha_rows}
    beta_s = float(design["fixed_renderer_coefficients"]["s_line_first"])
    beta_q = float(design["fixed_renderer_coefficients"]["q_prev_dy"])

    fold_cache: dict[tuple[str, str], dict[str, object]] = {}
    predictions: list[dict[str, object]] = []
    field_rows: dict[str, list[dict[str, str]]] = {}
    for capacity_row in capacity:
        field = field_by_id[capacity_row["field_id"]]
        register = str(field["register"])
        folio = str(field["folio"])
        fold_key = (register, folio)
        if fold_key not in alpha_by_fold:
            raise AssertionError(f"missing frozen GDT336 alpha for {fold_key}")
        if fold_key not in fold_cache:
            fold_cache[fold_key] = build_fold(register, folio, rows, fields, previous_wrapper)
        fold = fold_cache[fold_key]
        training_fields = fold["training_fields"]
        same = [candidate for candidate in training_fields if candidate["normalized"] == field["normalized"]]
        if len({candidate["folio"] for candidate in same}) < 2 or len({candidate["rendered"] for candidate in same}) < 2:
            raise AssertionError("frozen class eligibility failed")
        if field["rendered"] in {candidate["rendered"] for candidate in training_fields}:
            raise AssertionError("held rendered surface leaked into training")
        members = list(field["rows"])
        field_rows[field["field_id"]] = members
        for member in members:
            previous = previous_wrapper[member["event_id_sha256"]]
            wp = wrapper_probabilities(member, previous, fold, beta_s, beta_q)
            pp = placement_probabilities(member, fold, alpha_by_fold[fold_key])
            predictions.append(
                {
                    "field_id": field["field_id"],
                    "class_id": field["class_id"],
                    "register": register,
                    "held_folio": folio,
                    "page": field["page"],
                    "locus": field["locus"],
                    "field_group_count": field["group_count"],
                    "event_id": member["event_id_sha256"],
                    "coordinate_id": member["coordinate_id"],
                    "line_first": member["line_first"],
                    "prev_dy": member["prev_dy"],
                    "previous_wrapper": previous,
                    "wrapper_truth": member["observed_wrapper"],
                    "tuple_truth": member["joint_tuple_id"],
                    "selected_alpha": alpha_by_fold[fold_key],
                    "wrapper_probabilities": wp,
                    "placement_probabilities": pp,
                }
            )

    wrapper_model_rows, wrapper_summary = summarize_channel(predictions, "WRAPPER", WRAPPER_MODELS)
    placement_model_rows, placement_summary = summarize_channel(predictions, "PLACEMENT", PLACEMENT_MODELS)
    model_rows = wrapper_model_rows + placement_model_rows
    write_tsv(MODELS, model_rows)
    best_wrapper_baseline = min(
        (model for model in WRAPPER_MODELS if model != "JOINT_TWO_RULE"),
        key=lambda model: (wrapper_summary[model]["bits"], model),
    )

    folio_rows = gain_by_stratum(predictions, "held_folio", best_wrapper_baseline)
    register_rows = gain_by_stratum(predictions, "register", best_wrapper_baseline)
    length_rows = gain_by_stratum(predictions, "field_group_count", best_wrapper_baseline)
    write_tsv(FOLIO_SCORES, folio_rows)
    write_tsv(REGISTER_SCORES, register_rows)
    write_tsv(LENGTH_SCORES, length_rows)

    class_grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in capacity:
        class_grouped[row["class_id"]].append(row)
    class_rows: list[dict[str, object]] = []
    for class_id, members in sorted(class_grouped.items()):
        class_rows.append(
            {
                "class_id": class_id,
                "registers": "|".join(sorted({row["register"] for row in members})),
                "register_class_cells": len({row["register_class_cell_id"] for row in members}),
                "group_count": members[0]["group_count"],
                "held_fields": len(members),
                "held_folios": len({row["physical_folio"] for row in members}),
                "minimum_training_folios": min(int(row["training_physical_folios"]) for row in members),
                "minimum_training_surface_variants": min(int(row["training_distinct_surfaces"]) for row in members),
                "held_surfaces_all_unseen": "YES",
                "normalization": "EXACT_ORDERED_JOINT_TUPLE_SEQUENCE",
                "semantic_state": "UNASSIGNED",
                "translation_state": "UNASSIGNED",
            }
        )
    write_tsv(CLASSES, class_rows)

    prediction_rows: list[dict[str, object]] = []
    for prediction in predictions:
        wp = prediction["wrapper_probabilities"]
        pp = prediction["placement_probabilities"]
        prediction_rows.append(
            {
                "field_id": prediction["field_id"],
                "class_id": prediction["class_id"],
                "register": prediction["register"],
                "held_folio": prediction["held_folio"],
                "page": prediction["page"],
                "locus": prediction["locus"],
                "field_group_count": prediction["field_group_count"],
                "event_id": prediction["event_id"],
                "coordinate_id": prediction["coordinate_id"],
                "line_first": prediction["line_first"],
                "prev_dy": prediction["prev_dy"],
                "selected_alpha": prediction["selected_alpha"],
                "observed_wrapper": prediction["wrapper_truth"],
                "best_wrapper_baseline": best_wrapper_baseline,
                "baseline_wrapper_top1": argmax_key(wp[best_wrapper_baseline]),
                "candidate_wrapper_top1": argmax_key(wp["JOINT_TWO_RULE"]),
                "baseline_wrapper_probability": f"{wp[best_wrapper_baseline][prediction['wrapper_truth']]:.12f}",
                "candidate_wrapper_probability": f"{wp['JOINT_TWO_RULE'][prediction['wrapper_truth']]:.12f}",
                "observed_joint_tuple_id": prediction["tuple_truth"],
                "coordinate_top1_tuple_id": tuple_argmax(pp["COORDINATE"]),
                "placement_top1_tuple_id": tuple_argmax(pp["PLACEMENT"]),
                "coordinate_probability": f"{pp['COORDINATE'][prediction['tuple_truth']]:.12f}",
                "placement_probability": f"{pp['PLACEMENT'][prediction['tuple_truth']]:.12f}",
                "semantic_state": "UNASSIGNED",
                "translation_state": "UNASSIGNED",
            }
        )
    write_tsv(PREDICTIONS, prediction_rows)

    wrapper_groups = permutation_groups(
        predictions, ("held_folio", "register", "coordinate_id", "line_first", "prev_dy")
    )
    tuple_groups = permutation_groups(predictions, ("held_folio", "register", "coordinate_id"))
    wrapper_mobile = sum(len(group) for group in wrapper_groups if len(group) > 1)
    tuple_mobile = sum(len(group) for group in tuple_groups if len(group) > 1)
    wrapper_truth = [prediction["wrapper_truth"] for prediction in predictions]
    tuple_truth = [prediction["tuple_truth"] for prediction in predictions]
    null_rows: list[dict[str, object]] = []
    observed_wrapper_gain = wrapper_summary[best_wrapper_baseline]["bits"] - wrapper_summary["JOINT_TWO_RULE"]["bits"]
    observed_placement_gain = placement_summary["COORDINATE"]["bits"] - placement_summary["PLACEMENT"]["bits"]
    exceed_wrapper = exceed_placement = 0
    for world in range(int(design["null"]["worlds"])):
        rng = random.Random(int(design["null"]["seed"]) * 1_000_003 + world)
        shuffled_wrappers = wrapper_truth.copy()
        shuffled_tuples = tuple_truth.copy()
        for group in wrapper_groups:
            values = [wrapper_truth[index] for index in group]
            rng.shuffle(values)
            for index, value in zip(group, values):
                shuffled_wrappers[index] = value
        for group in tuple_groups:
            values = [tuple_truth[index] for index in group]
            rng.shuffle(values)
            for index, value in zip(group, values):
                shuffled_tuples[index] = value
        wrapper_bits = {model: 0.0 for model in WRAPPER_MODELS}
        coordinate_bits = placement_bits = 0.0
        for index, prediction in enumerate(predictions):
            for model in WRAPPER_MODELS:
                wrapper_bits[model] -= math.log2(prediction["wrapper_probabilities"][model][shuffled_wrappers[index]])
            coordinate_bits -= math.log2(prediction["placement_probabilities"]["COORDINATE"][shuffled_tuples[index]])
            placement_bits -= math.log2(prediction["placement_probabilities"]["PLACEMENT"][shuffled_tuples[index]])
        best_null_baseline = min(
            (model for model in WRAPPER_MODELS if model != "JOINT_TWO_RULE"),
            key=lambda model: (wrapper_bits[model], model),
        )
        wrapper_gain = wrapper_bits[best_null_baseline] - wrapper_bits["JOINT_TWO_RULE"]
        placement_gain = coordinate_bits - placement_bits
        max_two = max(wrapper_gain, placement_gain)
        exceed_wrapper += int(max_two >= observed_wrapper_gain - 1e-12)
        exceed_placement += int(max_two >= observed_placement_gain - 1e-12)
        null_rows.append(
            {
                "world": world,
                "wrapper_best_baseline": best_null_baseline,
                "wrapper_gain_bits": f"{wrapper_gain:.12f}",
                "placement_gain_bits": f"{placement_gain:.12f}",
                "max_two_gain_bits": f"{max_two:.12f}",
            }
        )
    write_tsv(NULL, null_rows)
    worlds = int(design["null"]["worlds"])
    wrapper_p = (exceed_wrapper + 1) / (worlds + 1)
    placement_p = (exceed_placement + 1) / (worlds + 1)

    wrapper_paid = observed_wrapper_gain - math.log2(len(WRAPPER_MODELS))
    placement_paid = observed_placement_gain - 1.0
    wrapper_positive_registers = sum(float(row["wrapper_gain_bits"]) > 0 for row in register_rows)
    placement_positive_registers = sum(float(row["placement_gain_bits"]) > 0 for row in register_rows)
    wrapper_positive_folios = sum(float(row["wrapper_gain_bits"]) > 0 for row in folio_rows)
    placement_positive_folios = sum(float(row["placement_gain_bits"]) > 0 for row in folio_rows)
    capacity_counts = freeze["counts"]
    capacity_pass = (
        capacity_counts["fields"] >= design["capacity_gates"]["fields_min"]
        and capacity_counts["physical_folios"] >= design["capacity_gates"]["folios_min"]
        and capacity_counts["normalized_classes"] >= design["capacity_gates"]["normalized_objects_min"]
        and capacity_counts["register_class_cells"] >= design["capacity_gates"]["register_object_cells_min"]
        and capacity_counts["registers"] >= design["capacity_gates"]["registers_min"]
    )
    wrapper_pass = (
        wrapper_paid > 0
        and wrapper_positive_registers >= 2
        and wrapper_positive_folios >= 10
        and wrapper_p <= 0.05
    )
    placement_pass = (
        placement_paid > 0
        and placement_positive_registers >= 2
        and placement_positive_folios >= 10
        and placement_summary["PLACEMENT"]["exact_fields"] >= placement_summary["COORDINATE"]["exact_fields"]
        and placement_p <= 0.05
    )
    if capacity_pass and wrapper_pass and placement_pass:
        status = "RENDERER_INVARIANT_FORMAL_EQUIVALENCE_SUPPORTED"
    elif capacity_pass and wrapper_pass:
        status = "EXACT_JOINT_RENDERER_NORMALIZATION_ONLY"
    else:
        status = "NO_STABLE_RENDERER_INVARIANT_EQUIVALENCE"

    counter_rows = [
        {
            "counterexample_id": "C01_SMALL_PANEL",
            "finding": "The prospective panel contains only 25 fields and 32 groups.",
            "impact": "Any positive result must transfer across folds and cannot be generalized beyond the ten frozen classes.",
        },
        {
            "counterexample_id": "C02_SEQUENCE_CAPACITY",
            "finding": "Only seven held fields contain two groups; eighteen are one-group tuple cases.",
            "impact": "Multi-group sequence evidence is reported separately and cannot be inferred from one-group success.",
        },
        {
            "counterexample_id": "C03_NO_BROADER_MERGE",
            "finding": "GDT325 and GDT326 forbid coordinate deletion and PAGE_HOST-coordinate factorization.",
            "impact": "Different exact joint-tuple sequences remain distinct even if their placement or wrappers resemble one another.",
        },
        {
            "counterexample_id": "C04_EXPOSED_REPRESENTATION",
            "finding": "The GDT327 tuple representation and GDT322 renderer cells were defined on the existing corpus before GDT338.",
            "impact": "The outer folds test new surface/folio transfer, not a pristine held representation discovery.",
        },
        {
            "counterexample_id": "C05_NULL_CAPACITY",
            "finding": f"Only {wrapper_mobile}/{len(predictions)} wrapper events and {tuple_mobile}/{len(predictions)} tuple events are mobile in the fixed-prediction diagnostics.",
            "impact": "Diagnostic p-values are not exact retrained or high-capacity conditional tests.",
        },
        {
            "counterexample_id": "C06_SEMANTICS_SEALED",
            "finding": "No glyph, separate PAGE_HOST feature, substring, annotation, external source, or f84 row enters the model; PAGE_HOST remains opaque inside the exact joint ID.",
            "impact": "No outcome can establish a linguistic or semantic equivalence.",
        },
    ]
    write_tsv(COUNTER, counter_rows)

    multi = next(row for row in length_rows if row["stratum"] == "2")
    report = f"""# GDT338 renderer-invariant formal equivalence report

Status: **{status}**.

## Prospective panel

The frozen outer panel contains {capacity_counts['fields']} fields / {capacity_counts['group_events']} groups on {capacity_counts['physical_folios']} held physical folios, representing {capacity_counts['normalized_classes']} exact normalized classes in {capacity_counts['registers']} registers. Every held rendered surface was absent from training; every normalized class had at least two training surfaces on at least two training folios. No raw glyph, separate PAGE_HOST feature, substring, semantic annotation, or external source was used; PAGE_HOST remains opaque inside the exact joint ID.

## Unseen-surface wrapper transfer

The best noncandidate wrapper baseline is **{best_wrapper_baseline}**. `JOINT_TWO_RULE` changes held codelength by {observed_wrapper_gain:+.3f} bits relative to that baseline ({wrapper_paid:+.3f} after the fixed log2(6) selector), with {wrapper_positive_folios}/{capacity_counts['physical_folios']} positive folio folds and {wrapper_positive_registers}/{capacity_counts['registers']} positive registers. Its fixed-prediction max-two diagnostic p is {wrapper_p:.6f}.

Exact wrapper-sequence top-1 is {int(wrapper_summary['JOINT_TWO_RULE']['exact_fields'])}/{capacity_counts['fields']} for the candidate versus {int(wrapper_summary[best_wrapper_baseline]['exact_fields'])}/{capacity_counts['fields']} for the best baseline. Exact rendered-surface lookup has 0/{capacity_counts['fields']} coverage by construction.

## Normalized-object recovery from placement

The frozen GDT336 placement correction changes held tuple codelength by {observed_placement_gain:+.3f} bits ({placement_paid:+.3f} after the one-bit selector), with {placement_positive_folios}/{capacity_counts['physical_folios']} positive folio folds and {placement_positive_registers}/{capacity_counts['registers']} positive registers. Exact normalized-field top-1 is {int(placement_summary['PLACEMENT']['exact_fields'])}/{capacity_counts['fields']} versus {int(placement_summary['COORDINATE']['exact_fields'])}/{capacity_counts['fields']}; max-two diagnostic p is {placement_p:.6f}.

The genuinely multi-group sensitivity contains seven two-group fields. Its wrapper gain is {float(multi['wrapper_gain_bits']):+.3f} bits and its placement gain is {float(multi['placement_gain_bits']):+.3f} bits. This small subset is reported as a sensitivity, not upgraded into sequence-level evidence.

## Interpretation

The decision gates are mechanical. A failure means that the executable grammar does not justify a new equivalence relation beyond exact opaque joint-tuple identity under the tested renderer/placement marginalization. A pass would still establish only formal predictive exchangeability, never semantic or linguistic identity.

## Claim ceiling

Opaque exact-joint renderer normalization only. No different tuple sequence, word, morpheme, PAGE_HOST function, semantic role, meaning, sound, language, plaintext, translation, diagram phase, or external correspondence is inferred. f84 was not opened, parsed, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    scientific_inputs = [
        INTER,
        FOLDS336,
        DESIGN,
        CAPACITY,
        FREEZE,
        METHOD,
        ROOT / "gdt322_result.json",
        ROOT / "gdt327_result.json",
        ROOT / "gdt335_result.json",
        ROOT / "gdt336_result.json",
    ]
    outputs = [CLASSES, PREDICTIONS, MODELS, FOLIO_SCORES, REGISTER_SCORES, LENGTH_SCORES, NULL, COUNTER]
    result = {
        "schema": "GDT338_RENDERER_INVARIANT_EQUIVALENCE_RESULT_V1",
        "status": status,
        "counts": capacity_counts,
        "wrapper": {
            "best_baseline": best_wrapper_baseline,
            "raw_gain_bits": observed_wrapper_gain,
            "selector_paid_gain_bits": wrapper_paid,
            "positive_folios": wrapper_positive_folios,
            "positive_registers": wrapper_positive_registers,
            "candidate_group_top1": int(wrapper_summary["JOINT_TWO_RULE"]["top1"]),
            "baseline_group_top1": int(wrapper_summary[best_wrapper_baseline]["top1"]),
            "candidate_exact_fields": int(wrapper_summary["JOINT_TWO_RULE"]["exact_fields"]),
            "baseline_exact_fields": int(wrapper_summary[best_wrapper_baseline]["exact_fields"]),
            "max_two_diagnostic_p": wrapper_p,
            "mobile_events": wrapper_mobile,
        },
        "placement": {
            "raw_gain_bits": observed_placement_gain,
            "selector_paid_gain_bits": placement_paid,
            "positive_folios": placement_positive_folios,
            "positive_registers": placement_positive_registers,
            "placement_group_top1": int(placement_summary["PLACEMENT"]["top1"]),
            "coordinate_group_top1": int(placement_summary["COORDINATE"]["top1"]),
            "placement_exact_fields": int(placement_summary["PLACEMENT"]["exact_fields"]),
            "coordinate_exact_fields": int(placement_summary["COORDINATE"]["exact_fields"]),
            "max_two_diagnostic_p": placement_p,
            "mobile_events": tuple_mobile,
        },
        "gates": {
            "capacity": capacity_pass,
            "wrapper_transfer": wrapper_pass,
            "placement_recovery": placement_pass,
        },
        "source_access": {
            "f84_opened_parsed_retained_joined_or_scored": False,
            "raw_surface_glyphs_used": False,
            "page_host_identity_used_separately_from_joint_tuple": False,
            "semantic_or_external_annotations_used": False,
        },
        "semantic_assignments": 0,
        "translation_assignments": 0,
        "claim_ceiling": "Renderer-invariant predictive exchangeability of exact opaque joint-tuple field sequences only; no broader tuple merge, semantics, language, plaintext, or translation.",
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in scientific_inputs},
        "documents": {str(REPORT.relative_to(ROOT)): sha256_file(REPORT)},
        "implementation": {
            str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve())
        },
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in outputs},
    }
    result["content_sha256"] = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    RESULT.write_bytes(canonical_json_bytes(result))
    print(json.dumps({"status": status, "wrapper": result["wrapper"], "placement": result["placement"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
