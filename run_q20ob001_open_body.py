#!/usr/bin/env python3
"""Run the frozen Q20OB001 OPEN-to-BODY predictive dependence test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "q20ob001_source_panel.tsv"
PANEL_AUDIT = ROOT / "q20ob001_source_panel_audit.json"
METHOD = ROOT / "Q20OB001_OPEN_BODY_METHOD.md"
OUT_FOLDS = ROOT / "q20ob001_fold_results.tsv"
OUT_RECORDS = ROOT / "q20ob001_record_predictions.tsv"
OUT_NULL = ROOT / "q20ob001_null_results.tsv"
OUT_BASE = ROOT / "q20ob001_baseline_comparison.tsv"
OUT_RESULT = ROOT / "q20ob001_result.json"
OUT_REPORT = ROOT / "Q20OB001_OPEN_BODY_REPORT.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
REPRESENTATIONS = ("MEMBER", "FAMILY", "GROUP")
FOLIOS = ("f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115")
GRID = (0.0, 1 / 128, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2)
ALPHA = 0.5
WORLDS = 4096
ZERO_TOLERANCE = 1e-9
FREEZE_COMMIT = "6c1b319"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def seed_for(*parts: object) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, output: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in output:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)


def load_panel() -> list[dict[str, object]]:
    output = []
    for row in rows(PANEL):
        assert not row["page"].startswith("f84r")
        output.append(
            {
                **row,
                "star_ordinal": int(row["star_ordinal"]),
                "record_line_count": int(row["record_line_count"]),
                "open_group_count": int(row["open_group_count"]),
                "open_member_count": int(row["open_member_count"]),
                "body_line_count": int(row["body_line_count"]),
                "body_group_count": int(row["body_group_count"]),
                "body_member_count": int(row["body_member_count"]),
                "open_members": json.loads(row["open_member_groups_json"]),
                "body_members": json.loads(row["body_member_lines_json"]),
                "open_families": json.loads(row["open_family_groups_json"]),
                "body_families": json.loads(row["body_family_lines_json"]),
            }
        )
    assert len(output) == 510
    for edition in EDITIONS:
        edition_rows = [row for row in output if row["edition"] == edition]
        assert len(edition_rows) == 170 and len({row["unit_id"] for row in edition_rows}) == 170
    return output


def symbol_groups(record: dict[str, object], representation: str, part: str) -> list[list[str]]:
    if representation == "MEMBER":
        value = record["open_members"] if part == "OPEN" else record["body_members"]
    elif representation == "FAMILY":
        value = record["open_families"] if part == "OPEN" else record["body_families"]
    else:
        raise ValueError(representation)
    if part == "OPEN":
        return [list(group) for group in value]  # type: ignore[arg-type]
    return [list(group) for line in value for group in line]  # type: ignore[arg-type]


def exact_groups(record: dict[str, object], part: str) -> list[list[str]]:
    if part == "OPEN":
        return [[" ".join(group) for group in record["open_members"]]]  # type: ignore[index]
    return [[" ".join(group) for group in line] for line in record["body_members"]]  # type: ignore[index]


def body_lines(record: dict[str, object], representation: str) -> list[list[list[str]]]:
    if representation == "MEMBER":
        return record["body_members"]  # type: ignore[return-value]
    if representation == "FAMILY":
        return record["body_families"]  # type: ignore[return-value]
    raise ValueError(representation)


def fit_order2(train: list[dict[str, object]], representation: str, inventory: tuple[str, ...]) -> np.ndarray:
    index = {token: i for i, token in enumerate(inventory)}
    k = len(inventory)
    counts = np.zeros((k + 1, k + 1, k + 1), dtype=np.float64)
    for record in train:
        for group in symbol_groups(record, representation, "BODY"):
            a = b = k
            for token in group:
                c = index[token]
                counts[a, b, c] += 1
                a, b = b, c
            counts[a, b, k] += 1
    return (counts + ALPHA) / (counts.sum(axis=2, keepdims=True) + ALPHA * (k + 1))


def symbol_counts(record: dict[str, object], representation: str, part: str, index: dict[str, int]) -> np.ndarray:
    counts = np.zeros(len(index), dtype=np.float64)
    for group in symbol_groups(record, representation, part):
        for token in group:
            counts[index[token]] += 1
    return counts


def smooth(counts: np.ndarray) -> np.ndarray:
    return (counts + ALPHA) / (float(counts.sum()) + ALPHA * len(counts))


def score_symbol(
    record: dict[str, object], representation: str, index: dict[str, int], p0: np.ndarray,
    local_weight: float, local_q: np.ndarray, open_weight: float = 0.0, open_q: np.ndarray | None = None,
) -> float:
    k = len(index)
    total = 0.0
    for group in symbol_groups(record, representation, "BODY"):
        a = b = k
        for token in group:
            c = index[token]
            probability = (1 - local_weight) * p0[a, b, c] + local_weight * local_q[c]
            if open_weight:
                assert open_q is not None
                probability = (1 - open_weight) * probability + open_weight * open_q[c]
            total -= math.log2(float(probability))
            a, b = b, c
        total -= math.log2(float(p0[a, b, k]))
    return total


def fit_group_model(train: list[dict[str, object]], member_inventory: tuple[str, ...]) -> dict[str, object]:
    group_counts = Counter(group for record in train for line in exact_groups(record, "BODY") for group in line)
    vocabulary = tuple(sorted(group_counts))
    index = {group: i for i, group in enumerate(vocabulary)}
    escape = len(vocabulary)
    eos = escape + 1
    counts = np.zeros(len(vocabulary) + 2, dtype=np.float64)
    for group, count in group_counts.items():
        counts[index[group]] = count
    counts[eos] = sum(len(exact_groups(record, "BODY")) for record in train)
    probabilities = (counts + ALPHA) / (counts.sum() + ALPHA * len(counts))
    member_p0 = fit_order2(train, "MEMBER", member_inventory)
    member_index = {token: i for i, token in enumerate(member_inventory)}
    return {"vocabulary": vocabulary, "index": index, "escape": escape, "eos": eos, "p0": probabilities, "member_p0": member_p0, "member_index": member_index}


def group_category_counts(record: dict[str, object], part: str, model: dict[str, object]) -> np.ndarray:
    index = model["index"]
    assert isinstance(index, dict)
    escape = int(model["escape"])
    counts = np.zeros(escape + 1, dtype=np.float64)
    for line in exact_groups(record, part):
        for group in line:
            counts[index.get(group, escape)] += 1
    return counts


def escaped_group_bits(group: str, model: dict[str, object]) -> float:
    tokens = group.split()
    member_p0 = model["member_p0"]
    member_index = model["member_index"]
    assert isinstance(member_p0, np.ndarray) and isinstance(member_index, dict)
    k = len(member_index)
    a = b = k
    total = 0.0
    for token in tokens:
        c = member_index[token]
        total -= math.log2(float(member_p0[a, b, c]))
        a, b = b, c
    total -= math.log2(float(member_p0[a, b, k]))
    return total


def score_group(
    record: dict[str, object], model: dict[str, object], local_weight: float, local_q: np.ndarray,
    open_weight: float = 0.0, open_q: np.ndarray | None = None,
) -> float:
    index = model["index"]
    assert isinstance(index, dict)
    escape, eos = int(model["escape"]), int(model["eos"])
    p0 = model["p0"]
    assert isinstance(p0, np.ndarray)
    total = 0.0
    for line in exact_groups(record, "BODY"):
        for group in line:
            category = index.get(group, escape)
            probability = (1 - local_weight) * p0[category] + local_weight * local_q[category]
            if open_weight:
                assert open_q is not None
                probability = (1 - open_weight) * probability + open_weight * open_q[category]
            total -= math.log2(float(probability))
            if category == escape:
                total += escaped_group_bits(group, model)
        total -= math.log2(float(p0[eos]))
    return total


def counts_for(record: dict[str, object], representation: str, part: str, model: dict[str, object]) -> np.ndarray:
    if representation == "GROUP":
        return group_category_counts(record, part, model)
    index = model["index"]
    assert isinstance(index, dict)
    return symbol_counts(record, representation, part, index)


def score_record(
    record: dict[str, object], representation: str, model: dict[str, object], local_weight: float,
    local_q: np.ndarray, open_weight: float = 0.0, open_q: np.ndarray | None = None,
) -> float:
    if representation == "GROUP":
        return score_group(record, model, local_weight, local_q, open_weight, open_q)
    return score_symbol(record, representation, model["index"], model["p0"], local_weight, local_q, open_weight, open_q)  # type: ignore[arg-type]


def build_model(train: list[dict[str, object]], all_rows: list[dict[str, object]], representation: str) -> dict[str, object]:
    member_inventory = tuple(sorted({token for record in all_rows for group in symbol_groups(record, "MEMBER", "OPEN") + symbol_groups(record, "MEMBER", "BODY") for token in group}))
    if representation == "GROUP":
        return fit_group_model(train, member_inventory)
    inventory = tuple(sorted({token for record in all_rows for group in symbol_groups(record, representation, "OPEN") + symbol_groups(record, representation, "BODY") for token in group}))
    return {"inventory": inventory, "index": {token: i for i, token in enumerate(inventory)}, "p0": fit_order2(train, representation, inventory)}


def folio_other_body_q(records: list[dict[str, object]], representation: str, model: dict[str, object]) -> dict[str, np.ndarray]:
    total = sum((counts_for(record, representation, "BODY", model) for record in records), start=np.zeros(len(counts_for(records[0], representation, "BODY", model))))
    return {str(record["unit_id"]): smooth(total - counts_for(record, representation, "BODY", model)) for record in records}


def choose_weights(train: list[dict[str, object]], representation: str, model: dict[str, object]) -> tuple[float, float, float, float]:
    by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in train:
        by_folio[str(record["physical_folio"])].append(record)
    local_q = {unit: q for folio_rows in by_folio.values() for unit, q in folio_other_body_q(folio_rows, representation, model).items()}
    local_scores = []
    for weight in GRID:
        bits = sum(score_record(record, representation, model, weight, local_q[str(record["unit_id"])]) for record in train)
        local_scores.append((bits, weight))
    local_bits, local_weight = min(local_scores)
    open_q = {str(record["unit_id"]): smooth(counts_for(record, representation, "OPEN", model)) for record in train}
    open_scores = []
    for weight in GRID:
        bits = sum(
            score_record(record, representation, model, local_weight, local_q[str(record["unit_id"])], weight, open_q[str(record["unit_id"])])
            for record in train
        )
        open_scores.append((bits, weight))
    conditional_bits, open_weight = min(open_scores)
    return local_weight, open_weight, local_bits, conditional_bits


def kt_category_bits(train_values: list[int], held_values: list[int], support: tuple[int, ...]) -> float:
    counts = Counter(train_values)
    denominator = len(train_values) + ALPHA * len(support)
    return sum(-math.log2((counts[value] + ALPHA) / denominator) for value in held_values)


def length_baseline(train: list[dict[str, object]], held: list[dict[str, object]]) -> float:
    line_support = tuple(range(1, 7))
    group_support = tuple(range(1, max(int(record["open_group_count"]) for record in train + held) + 15))
    member_support = tuple(range(1, 30))
    train_lines = [int(record["body_line_count"]) for record in train]
    held_lines = [int(record["body_line_count"]) for record in held]
    train_group_counts = [len(line) for record in train for line in record["body_members"]]  # type: ignore[index]
    held_group_counts = [len(line) for record in held for line in record["body_members"]]  # type: ignore[index]
    train_member_counts = [len(group) for record in train for line in record["body_members"] for group in line]  # type: ignore[index]
    held_member_counts = [len(group) for record in held for line in record["body_members"] for group in line]  # type: ignore[index]
    assert set(train_lines + held_lines) <= set(line_support)
    assert set(train_group_counts + held_group_counts) <= set(group_support)
    assert set(train_member_counts + held_member_counts) <= set(member_support)
    return (
        kt_category_bits(train_lines, held_lines, line_support)
        + kt_category_bits(train_group_counts, held_group_counts, group_support)
        + kt_category_bits(train_member_counts, held_member_counts, member_support)
    )


def assignments_for(records: list[dict[str, object]], edition: str, folio: str, world: int) -> tuple[list[int], int]:
    strata: dict[int, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        strata[int(record["open_member_count"])].append(index)
    assignment = list(range(len(records)))
    swappable = 0
    for length, indices in sorted(strata.items()):
        if len(indices) < 2:
            continue
        swappable += len(indices)
        shuffled = indices.copy()
        random.Random(seed_for("Q20OB001", edition, folio, world, length)).shuffle(shuffled)
        for target, source in zip(indices, shuffled, strict=True):
            assignment[target] = source
    return assignment, swappable


def previous_assignment(records: list[dict[str, object]]) -> list[int]:
    strata: dict[int, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        strata[int(record["open_member_count"])].append(index)
    assignment = list(range(len(records)))
    for indices in strata.values():
        if len(indices) > 1:
            for offset, target in enumerate(indices):
                assignment[target] = indices[offset - 1]
    return assignment


def main() -> None:
    panel = load_panel()
    fold_rows: list[dict[str, object]] = []
    record_rows: list[dict[str, object]] = []
    baseline_rows: list[dict[str, object]] = []
    true_gains: dict[tuple[str, str], float] = Counter()
    true_bits: dict[tuple[str, str], float] = Counter()
    local_bits: dict[tuple[str, str], float] = Counter()
    string_bits: dict[tuple[str, str], float] = Counter()
    body_members: dict[str, int] = Counter()
    previous_gains: dict[tuple[str, str], float] = Counter()
    null_gains = {(edition, representation): np.zeros(WORLDS) for edition in EDITIONS for representation in REPRESENTATIONS}
    selected_weights: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    positive_folds: dict[tuple[str, str], int] = Counter()
    swappable_by_edition: dict[str, int] = Counter()

    for edition in EDITIONS:
        edition_rows = [row for row in panel if row["edition"] == edition]
        edition_rows.sort(key=lambda row: (FOLIOS.index(str(row["physical_folio"])), str(row["page"]), int(row["star_ordinal"])))
        body_members[edition] = sum(int(row["body_member_count"]) for row in edition_rows)
        for held_folio in FOLIOS:
            train = [row for row in edition_rows if row["physical_folio"] != held_folio]
            held = [row for row in edition_rows if row["physical_folio"] == held_folio]
            length_bits = length_baseline(train, held)
            baseline_rows.append({"edition": edition, "held_folio": held_folio, "baseline": "BODY_SHAPE_LENGTH_KT", "held_bits": f"{length_bits:.9f}", "held_records": len(held), "held_body_members": sum(int(row["body_member_count"]) for row in held), "bits_per_record": f"{length_bits / len(held):.9f}"})
            assignments = [assignments_for(held, edition, held_folio, world)[0] for world in range(WORLDS)]
            _, swappable = assignments_for(held, edition, held_folio, 0)
            swappable_by_edition[edition] += swappable
            previous = previous_assignment(held)
            for representation in REPRESENTATIONS:
                model = build_model(train, edition_rows, representation)
                local_weight, open_weight, training_local_bits, training_conditional_bits = choose_weights(train, representation, model)
                selected_weights[(edition, representation)].append((local_weight, open_weight))
                local_q = folio_other_body_q(held, representation, model)
                open_q = [smooth(counts_for(record, representation, "OPEN", model)) for record in held]
                base = np.zeros(len(held))
                local = np.zeros(len(held))
                pair = np.full((len(held), len(held)), np.inf)
                for i, record in enumerate(held):
                    zero_q = local_q[str(record["unit_id"])]
                    base[i] = score_record(record, representation, model, 0.0, zero_q)
                    local[i] = score_record(record, representation, model, local_weight, zero_q)
                    for j, candidate in enumerate(held):
                        if int(candidate["open_member_count"]) == int(record["open_member_count"]):
                            pair[i, j] = score_record(record, representation, model, local_weight, zero_q, open_weight, open_q[j])
                conditional = float(sum(pair[i, i] for i in range(len(held))))
                fold_gain = float(local.sum() - conditional)
                if abs(fold_gain) < ZERO_TOLERANCE:
                    fold_gain = 0.0
                previous_conditional = float(sum(pair[i, previous[i]] for i in range(len(held))))
                previous_gain = float(local.sum() - previous_conditional)
                if abs(previous_gain) < ZERO_TOLERANCE:
                    previous_gain = 0.0
                key = (edition, representation)
                true_gains[key] += fold_gain
                true_bits[key] += conditional
                local_bits[key] += float(local.sum())
                string_bits[key] += float(base.sum())
                previous_gains[key] += previous_gain
                positive_folds[key] += int(fold_gain > ZERO_TOLERANCE)
                for world, assignment in enumerate(assignments):
                    permuted = float(sum(pair[i, assignment[i]] for i in range(len(held))))
                    world_gain = float(local.sum() - permuted)
                    null_gains[key][world] += 0.0 if abs(world_gain) < ZERO_TOLERANCE else world_gain
                fold_rows.append(
                    {
                        "edition": edition,
                        "held_folio": held_folio,
                        "representation": representation,
                        "train_records": len(train),
                        "held_records": len(held),
                        "held_body_members": sum(int(row["body_member_count"]) for row in held),
                        "swappable_records_exact_open_length": swappable,
                        "selected_local_other_body_weight": f"{local_weight:.8f}",
                        "selected_own_open_weight": f"{open_weight:.8f}",
                        "training_local_bits": f"{training_local_bits:.9f}",
                        "training_conditional_bits": f"{training_conditional_bits:.9f}",
                        "held_string_baseline_bits": f"{base.sum():.9f}",
                        "held_local_body_baseline_bits": f"{local.sum():.9f}",
                        "held_true_open_conditional_bits": f"{conditional:.9f}",
                        "own_open_gain_bits": f"{fold_gain:.9f}",
                        "own_open_gain_bits_per_body_member": f"{fold_gain / sum(int(row['body_member_count']) for row in held):.9f}",
                        "previous_compatible_open_gain_bits": f"{previous_gain:.9f}",
                        "positive_gain": int(fold_gain > ZERO_TOLERANCE),
                    }
                )
                for i, record in enumerate(held):
                    record_rows.append(
                        {
                            "edition": edition,
                            "representation": representation,
                            "held_folio": held_folio,
                            "unit_id": record["unit_id"],
                            "page": record["page"],
                            "star_ordinal": record["star_ordinal"],
                            "open_locus": record["open_locus"],
                            "record_line_count": record["record_line_count"],
                            "open_member_count": record["open_member_count"],
                            "body_member_count": record["body_member_count"],
                            "permutation_eligible": int(sum(int(other["open_member_count"]) == int(record["open_member_count"]) for other in held) >= 2),
                            "local_body_baseline_bits": f"{local[i]:.9f}",
                            "true_open_conditional_bits": f"{pair[i, i]:.9f}",
                            "true_open_gain_bits": f"{local[i] - pair[i, i]:.9f}",
                        }
                    )
                baseline_rows.extend(
                    [
                        {"edition": edition, "held_folio": held_folio, "baseline": f"{representation}_TRAINING_STRING", "held_bits": f"{base.sum():.9f}", "held_records": len(held), "held_body_members": sum(int(row["body_member_count"]) for row in held), "bits_per_record": f"{base.sum() / len(held):.9f}"},
                        {"edition": edition, "held_folio": held_folio, "baseline": f"{representation}_PLUS_OTHER_BODY_LOCAL_VOCAB", "held_bits": f"{local.sum():.9f}", "held_records": len(held), "held_body_members": sum(int(row["body_member_count"]) for row in held), "bits_per_record": f"{local.sum() / len(held):.9f}"},
                    ]
                )

    null_rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, object]] = {}
    for edition in EDITIONS:
        normalized_null = {representation: null_gains[(edition, representation)] / body_members[edition] for representation in REPRESENTATIONS}
        max_null = np.max(np.vstack([normalized_null[representation] for representation in REPRESENTATIONS]), axis=0)
        for representation in REPRESENTATIONS:
            key = (edition, representation)
            observed = true_gains[key] / body_members[edition]
            local_p = (1 + int(np.sum(normalized_null[representation] >= observed - 1e-15))) / (WORLDS + 1)
            max_p = (1 + int(np.sum(max_null >= observed - 1e-15))) / (WORLDS + 1)
            summary_key = f"{edition}:{representation}"
            summaries[summary_key] = {
                "true_gain_bits": true_gains[key],
                "true_gain_bits_per_body_member": observed,
                "null_median_gain_bits_per_body_member": float(np.median(normalized_null[representation])),
                "true_minus_null_median_bits_per_body_member": observed - float(np.median(normalized_null[representation])),
                "local_permutation_p": local_p,
                "maxT_three_representation_p": max_p,
                "positive_held_folios": positive_folds[key],
                "selected_local_weights": [weight[0] for weight in selected_weights[key]],
                "selected_open_weights": [weight[1] for weight in selected_weights[key]],
                "nonzero_open_weight_folds": sum(weight[1] > 0 for weight in selected_weights[key]),
                "previous_compatible_open_gain_bits": previous_gains[key],
                "string_baseline_bits": string_bits[key],
                "local_body_baseline_bits": local_bits[key],
                "true_conditional_bits": true_bits[key],
            }
            null_rows.append(
                {
                    "edition": edition,
                    "representation": representation,
                    "worlds": WORLDS,
                    "swappable_records": swappable_by_edition[edition],
                    "true_gain_bits": f"{true_gains[key]:.9f}",
                    "true_gain_bits_per_body_member": f"{observed:.12f}",
                    "null_q05_gain_bits_per_body_member": f"{np.quantile(normalized_null[representation], 0.05):.12f}",
                    "null_median_gain_bits_per_body_member": f"{np.median(normalized_null[representation]):.12f}",
                    "null_q95_gain_bits_per_body_member": f"{np.quantile(normalized_null[representation], 0.95):.12f}",
                    "local_permutation_p": f"{local_p:.12f}",
                    "maxT_three_representation_p": f"{max_p:.12f}",
                    "null_array_sha256": hashlib.sha256(normalized_null[representation].astype("<f8").tobytes()).hexdigest(),
                }
            )

    primary = summaries["ZL3b:MEMBER"]
    alternate_positive = all(float(summaries[f"{edition}:MEMBER"]["true_gain_bits"]) > ZERO_TOLERANCE for edition in ("IT2a", "RF1b"))
    capacity = all(swappable_by_edition[edition] >= 100 for edition in EDITIONS) and len(FOLIOS) >= 7
    supported = (
        float(primary["true_gain_bits"]) > ZERO_TOLERANCE
        and float(primary["maxT_three_representation_p"]) <= 0.05
        and alternate_positive
        and int(primary["positive_held_folios"]) >= 6
        and float(primary["true_gain_bits"]) > float(primary["previous_compatible_open_gain_bits"])
        and int(primary["nonzero_open_weight_folds"]) >= 6
    )
    if not capacity:
        decision = "INSUFFICIENT_OPEN_BODY_CAPACITY"
    elif float(primary["true_gain_bits"]) <= ZERO_TOLERANCE or float(primary["true_minus_null_median_bits_per_body_member"]) <= ZERO_TOLERANCE:
        decision = "OPEN_BODY_DEPENDENCE_NOT_ABOVE_MATCHED_CONTROLS"
    elif supported:
        decision = "TRANSFERABLE_OPEN_BODY_DEPENDENCE_SUPPORTED"
    else:
        decision = "OPEN_BODY_DEPENDENCE_WEAK_OR_FOLIO_LOCAL"

    write_tsv(OUT_FOLDS, fold_rows)
    write_tsv(OUT_RECORDS, record_rows)
    write_tsv(OUT_NULL, null_rows)
    write_tsv(OUT_BASE, baseline_rows)
    result = {
        "schema": "Q20OB001_OPEN_BODY_RESULT_V1",
        "status": decision,
        "exploratory": True,
        "freeze_commit": FREEZE_COMMIT,
        "capacity": {
            "units": 170,
            "alternate_reading_rows": 510,
            "physical_folios": list(FOLIOS),
            "folds": 8,
            "swappable_records_by_reading": dict(swappable_by_edition),
            "body_members_by_reading": dict(body_members),
            "f84r_rows_retained_joined_or_scored": 0,
        },
        "model": {
            "representations": list(REPRESENTATIONS),
            "primary": "MEMBER",
            "weights": list(GRID),
            "alpha": ALPHA,
            "permutation_worlds": WORLDS,
            "numerical_zero_tolerance_bits": ZERO_TOLERANCE,
            "null": "within_physical_folio_exact_open_member_count_complete_OPEN_permutation",
            "local_baseline": "training_string_plus_all_other_BODY_records_on_held_folio",
            "semantic_features": False,
        },
        "summaries": summaries,
        "decision_gates": {
            "capacity": capacity,
            "zl_member_positive_gain": float(primary["true_gain_bits"]) > ZERO_TOLERANCE,
            "zl_member_maxT_p_le_0_05": float(primary["maxT_three_representation_p"]) <= 0.05,
            "it_rf_member_positive_gain": alternate_positive,
            "zl_member_positive_on_6_of_8_folios": int(primary["positive_held_folios"]) >= 6,
            "zl_member_beats_previous_compatible_open": float(primary["true_gain_bits"]) > float(primary["previous_compatible_open_gain_bits"]),
            "zl_member_nonzero_open_weight_6_of_8": int(primary["nonzero_open_weight_folds"]) >= 6,
        },
        "null_digests": {f"{row['edition']}:{row['representation']}": row["null_array_sha256"] for row in null_rows},
        "inputs": {path.name: sha(path) for path in (METHOD, PANEL, PANEL_AUDIT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (OUT_FOLDS, OUT_RECORDS, OUT_NULL, OUT_BASE)},
        "claim_ceiling": "Transferable source-internal first-line to later-line dependence only; no recipe, heading, semantic field, language, word class, plaintext, meaning, or translation.",
        "negative_scope": "The nonconfirmation closes only the registered one-weight direct MEMBER/FAMILY/GROUP OPEN-cache family; it does not exclude every possible nonlinear OPEN-to-BODY relation.",
    }
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    table_lines = []
    for edition in EDITIONS:
        for representation in REPRESENTATIONS:
            summary = summaries[f"{edition}:{representation}"]
            table_lines.append(
                f"| {edition} | {representation} | {float(summary['true_gain_bits']):+.3f} | {float(summary['true_gain_bits_per_body_member']):+.6f} | {float(summary['null_median_gain_bits_per_body_member']):+.6f} | {float(summary['local_permutation_p']):.6f} | {float(summary['maxT_three_representation_p']):.6f} | {int(summary['positive_held_folios'])}/8 |"
            )
    report = f"""# Q20OB001 OPEN-to-BODY predictive dependence report

Status: **{decision}**

The frozen test used 170 clean star-delimited units on eight physical folios.
Each folio was held out once. ZL3b, IT2a, and RF1b were scored as alternate
reading sensitivities, not independent samples. f84r remained excluded.

## Held-folio OPEN increment

Positive gain means the unit's own OPEN improved BODY prediction above a
training-folio string model already augmented by the vocabulary of every other
BODY record on the held folio.

| reading | representation | true gain bits | gain/member | null median/member | local p | maxT p | positive folios |
|---|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table_lines)}

The primary ZL3b MEMBER endpoint has **{float(primary['true_gain_bits']):+.3f}**
bits of gain ({float(primary['true_gain_bits_per_body_member']):+.6f} per BODY
member), versus matched-null median
**{float(primary['null_median_gain_bits_per_body_member']):+.6f}**. Its local
permutation p is **{float(primary['local_permutation_p']):.6f}** and the
three-representation maxT p is
**{float(primary['maxT_three_representation_p']):.6f}**. Exact-length
permutation capacity is ZL/IT/RF
**{swappable_by_edition['ZL3b']}/{swappable_by_edition['IT2a']}/{swappable_by_edition['RF1b']}**
of 170 records.

The own-OPEN weight is nonzero in **{int(primary['nonzero_open_weight_folds'])}/8**
ZL folds, and **{int(primary['positive_held_folios'])}/8** held folios have a
positive primary gain. The deterministic previous-compatible-OPEN gain is
**{float(primary['previous_compatible_open_gain_bits']):+.3f}** bits.

## Baselines and interpretation

Training-only order-2 character/member and family models, an exact whole-group
dictionary with character escape, the other-BODY held-folio vocabulary cache,
and a separate BODY length/shape KT baseline are all published fold by fold.
The aggregate ZL member-string baseline is
**{float(primary['string_baseline_bits']) / body_members['ZL3b']:.6f}**
bits per BODY member. Both the fitted other-BODY cache and own-OPEN cache select
zero weight in all eight primary folds, so neither improves that baseline.
The permutation keeps BODY, folio, exact OPEN member count, total record member
length, and local vocabulary fixed. Singleton length strata contribute no
pairing evidence.

This experiment tests only whether the particular first line carries
transferable formal information about its later lines. `OPEN` and `BODY` are
positional names. The nonconfirmation applies only to the registered direct
MEMBER/FAMILY/GROUP cache family; it does not exclude every nonlinear
OPEN-to-BODY relation. No recipe, header, title, semantic field, language,
word class, plaintext, meaning, or translation follows.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": decision, "primary_gain_bits": primary["true_gain_bits"], "primary_maxT_p": primary["maxT_three_representation_p"], "positive_folios": primary["positive_held_folios"]}, indent=2))


if __name__ == "__main__":
    main()
