#!/usr/bin/env python3
"""Nested physical-folio replication of GDT003 formal composition."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
S = ROOT / "experiments/semantic_assumptions/results"
METHOD = ROOT / "GDT003_NESTED_HELDOUT_METHOD.md"
SEPARATOR = S / "source_separator_transcription.tsv"
ALIGNMENT = S / "source_sta_group_alignment.tsv"
OLD_RESULT = ROOT / "gdt003_results.json"
OUT_TRANS = ROOT / "gdt003_nested_transformations.tsv"
OUT_FOLDS = ROOT / "gdt003_nested_fold_summary.tsv"
OUT_CORRECT = ROOT / "gdt003_nested_correct_predictions.tsv"
OUT_TOP = ROOT / "gdt003_nested_top_predictions.tsv"
OUT_BASE = ROOT / "gdt003_nested_baseline_comparison.tsv"
OUT_COUNTER = ROOT / "gdt003_nested_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt003_nested_result.json"
OUT_REPORT = ROOT / "GDT003_NESTED_HELDOUT_REPORT.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
ALPHABET = tuple("abcdefghijklmnopqrstuvwxyz?$")
MIN_EDGES = 5
MIN_FOLIOS = 3
PER_STRATUM = 32
MIN_PAIR_TRIPLETS = 3
MIN_PAIR_COMPLETE = 1
PERMUTATION_WORLDS = 4096
PERMUTATION_SEED = 3003002
FREEZE_COMMIT = "f750ca2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def guarded_rows(path: Path) -> list[dict[str, str]]:
    """Skip f84r by routing field before retaining any other formal fields."""
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        fields = handle.readline().rstrip("\r\n").split("\t")
        locus_index = fields.index("locus")
        for raw in handle:
            values = raw.rstrip("\r\n").split("\t")
            if values[locus_index].startswith("f84r"):
                continue
            rows.append(dict(zip(fields, values, strict=True)))
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def physical_folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    return match.group(1) if match else page


def load_records() -> tuple[list[dict[str, str]], int]:
    metadata = {row["source_group_id"]: row for row in guarded_rows(SEPARATOR)}
    groups: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in guarded_rows(ALIGNMENT):
        source_id = row["source_group_id"]
        if source_id not in metadata:
            raise RuntimeError(f"alignment row missing separator record: {source_id}")
        meta = metadata[source_id]
        groups[(row["locus"], int(row["source_group_index"]))][row["edition"]] = {
            "surface": row["nearest_basic_eva_primary"].lower(),
            "source_group_count": row["source_group_count"],
            "locus": row["locus"],
            "page": meta["page"],
            "folio": physical_folio(meta["page"]),
            "section": meta["section"],
            "kind": meta["kind"],
        }
    records = []
    rejected = 0
    for key, edition_map in groups.items():
        if (
            set(edition_map) == set(EDITIONS)
            and len({row["surface"] for row in edition_map.values()}) == 1
            and len({row["source_group_count"] for row in edition_map.values()}) == 1
        ):
            row = edition_map["ZL3b"]
            if not re.fullmatch(r"[a-z?]+", row["surface"]):
                raise RuntimeError(f"unexpected display surface: {row['surface']}")
            records.append({"key": f"{key[0]}|G{key[1]:03d}", **row})
        else:
            rejected += 1
    return records, rejected


def op_id(op: tuple[str, str, str]) -> str:
    family, old, new = op
    if family.endswith("ADD"):
        return f"{family}:{new}"
    return f"{family}:{old}>{new}"


def op_stratum(op: tuple[str, str, str]) -> str:
    family, old, new = op
    if family.endswith("ADD"):
        return f"{family}:NEW{len(new)}"
    return f"{family}:OLD{len(old)}_NEW{len(new)}"


def apply_op(op: tuple[str, str, str], value: str) -> str | None:
    family, old, new = op
    if family == "PREFIX_ADD":
        return new + value
    if family == "SUFFIX_ADD":
        return value + new
    if family == "PREFIX_REPLACE":
        return new + value[len(old) :] if value.startswith(old) and len(value) > len(old) else None
    if family == "SUFFIX_REPLACE":
        return value[: -len(old)] + new if value.endswith(old) and len(value) > len(old) else None
    raise ValueError(family)


def discover_operations(
    forms: set[str], freq: Counter[str], form_folios: dict[str, set[str]]
) -> tuple[list[dict[str, object]], dict[tuple[str, str, str], dict[str, str]]]:
    edge_sets: dict[tuple[str, str, str], set[tuple[str, str]]] = defaultdict(set)
    for target in forms:
        for width in range(1, min(3, len(target) - 1) + 1):
            source = target[width:]
            if source in forms:
                edge_sets[("PREFIX_ADD", "", target[:width])].add((source, target))
            source = target[:-width]
            if source in forms:
                edge_sets[("SUFFIX_ADD", "", target[-width:])].add((source, target))

    prefix_index: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for value in forms:
        for width in (1, 2):
            if len(value) > width:
                prefix_index[value[width:]].append((value[:width], value))
    for values in prefix_index.values():
        for left, right in itertools.combinations(values, 2):
            if left[0] == right[0]:
                continue
            source, target = sorted((left, right), key=lambda item: item[0])
            edge_sets[("PREFIX_REPLACE", source[0], target[0])].add((source[1], target[1]))

    suffix_index: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for value in forms:
        for width in (2, 3):
            if len(value) > width:
                suffix_index[value[:-width]].append((value[-width:], value))
    for values in suffix_index.values():
        for left, right in itertools.combinations(values, 2):
            if left[0] == right[0]:
                continue
            source, target = sorted((left, right), key=lambda item: item[0])
            edge_sets[("SUFFIX_REPLACE", source[0], target[0])].add((source[1], target[1]))

    eligible: list[dict[str, object]] = []
    for operation, edges in edge_sets.items():
        folios = set().union(*(form_folios[source] | form_folios[target] for source, target in edges))
        if len(edges) < MIN_EDGES or len(folios) < MIN_FOLIOS:
            continue
        occurrence_support = sum(freq[source] + freq[target] for source, target in edges)
        eligible.append(
            {
                "operation": operation,
                "operation_id": op_id(operation),
                "stratum": op_stratum(operation),
                "edge_types": len(edges),
                "edge_occurrence_support": occurrence_support,
                "edge_folios": len(folios),
                "edges": edges,
            }
        )
    by_stratum: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in eligible:
        by_stratum[str(row["stratum"])].append(row)
    retained: list[dict[str, object]] = []
    for stratum, rows in sorted(by_stratum.items()):
        rows.sort(key=lambda row: (-int(row["edge_types"]), -int(row["edge_occurrence_support"]), str(row["operation_id"])))
        for rank, row in enumerate(rows[:PER_STRATUM], 1):
            row["rank_within_stratum"] = rank
            retained.append(row)
    retained.sort(key=lambda row: str(row["operation_id"]))
    edge_maps = {
        row["operation"]: {source: target for source, target in row["edges"]}  # type: ignore[index]
        for row in retained
    }
    return retained, edge_maps


def levenshtein(left: str, right: str) -> int:
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        new = [i]
        for j, b in enumerate(right, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = new
    return row[-1]


def kt_model(freq: Counter[str], order: int):
    context_char = Counter()
    context = Counter()
    k = len(ALPHABET)
    for value, count in freq.items():
        sequence = "^" * order + value + "$"
        for index in range(order, len(sequence)):
            history = sequence[index - order : index]
            char = sequence[index]
            context_char[history, char] += count
            context[history] += count

    def score(value: str) -> float:
        sequence = "^" * order + value + "$"
        bits = 0.0
        for index in range(order, len(sequence)):
            history = sequence[index - order : index]
            char = sequence[index]
            bits -= math.log2((context_char[history, char] + 0.5) / (context[history] + 0.5 * k))
        return -bits / max(1, len(value) + 1)

    return score


def is_q_right_pair(left: tuple[str, str, str], right: tuple[str, str, str]) -> bool:
    def is_q(op: tuple[str, str, str]) -> bool:
        return op == ("PREFIX_ADD", "", "q")

    def is_right(op: tuple[str, str, str]) -> bool:
        family, old, new = op
        return family.startswith("SUFFIX_") and bool({old, new} & {"dy", "dal", "dar"})

    return (is_q(left) and is_right(right)) or (is_q(right) and is_right(left))


def fold_candidates(
    forms: set[str], selected: list[dict[str, object]], edge_maps: dict[tuple[str, str, str], dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    selected_by_op = {row["operation"]: row for row in selected}
    by_source: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for operation, edges in edge_maps.items():
        for source in edges:
            by_source[source].append(operation)
    pair_stats: dict[tuple[tuple[str, str, str], tuple[str, str, str]], dict[str, object]] = defaultdict(
        lambda: {"triplets": 0, "complete": 0, "missing": []}
    )
    for base, operations in by_source.items():
        operations.sort(key=op_id)
        for operation_a, operation_b in itertools.combinations(operations, 2):
            ax = edge_maps[operation_a][base]
            bx = edge_maps[operation_b][base]
            ab = apply_op(operation_a, bx)
            ba = apply_op(operation_b, ax)
            if ab is None or ab != ba:
                continue
            key = (operation_a, operation_b)
            pair_stats[key]["triplets"] = int(pair_stats[key]["triplets"]) + 1
            if ab in forms:
                pair_stats[key]["complete"] = int(pair_stats[key]["complete"]) + 1
            else:
                pair_stats[key]["missing"].append((base, ax, bx, ab))  # type: ignore[union-attr]

    candidates: list[dict[str, object]] = []
    eligible_pairs = 0
    for (operation_a, operation_b), stats in pair_stats.items():
        triplets = int(stats["triplets"])
        complete = int(stats["complete"])
        if triplets < MIN_PAIR_TRIPLETS or complete < MIN_PAIR_COMPLETE:
            continue
        eligible_pairs += 1
        edge_a = int(selected_by_op[operation_a]["edge_types"])
        edge_b = int(selected_by_op[operation_b]["edge_types"])
        rate = (complete + 0.5) / (triplets + 1)
        paradigm_score = math.log2(rate) + math.log2(1 + min(edge_a, edge_b)) / 20
        for base, ax, bx, target in stats["missing"]:  # type: ignore[assignment]
            candidates.append(
                {
                    "operation_A": op_id(operation_a),
                    "operation_B": op_id(operation_b),
                    "operation_A_tuple": operation_a,
                    "operation_B_tuple": operation_b,
                    "base_X": base,
                    "A_X": ax,
                    "B_X": bx,
                    "predicted_fourth": target,
                    "training_triplets": triplets,
                    "training_complete": complete,
                    "operation_A_edges": edge_a,
                    "operation_B_edges": edge_b,
                    "paradigm_score": paradigm_score,
                    "q_right_named_subgroup": int(is_q_right_pair(operation_a, operation_b)),
                }
            )
    def deduplicate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        best: dict[str, dict[str, object]] = {}
        for row in rows:
            target = str(row["predicted_fourth"])
            key = (float(row["paradigm_score"]), str(row["operation_A"]), str(row["operation_B"]), str(row["base_X"]))
            if target not in best:
                best[target] = dict(row)
            else:
                previous = best[target]
                old_key = (float(previous["paradigm_score"]), str(previous["operation_A"]), str(previous["operation_B"]), str(previous["base_X"]))
                if key > old_key:
                    best[target] = dict(row)
        return list(best.values())

    # The named q/right subsystem is deduplicated independently.  Otherwise a
    # stronger unrelated derivation of the same target silently removes a
    # legitimate q/right prediction from the subgroup evaluation.
    return deduplicate(candidates), deduplicate([row for row in candidates if int(row["q_right_named_subgroup"])]), eligible_pairs


def auc(scores: list[float], labels: list[int]) -> float | None:
    positive = [score for score, label in zip(scores, labels) if label]
    negative = [score for score, label in zip(scores, labels) if not label]
    if not positive or not negative:
        return None
    return sum((left > right) + 0.5 * (left == right) for left in positive for right in negative) / (len(positive) * len(negative))


def average_precision(scores: list[float], labels: list[int], keys: list[str]) -> float | None:
    positives = sum(labels)
    if not positives:
        return None
    ordered = sorted(zip(scores, labels, keys), key=lambda row: (-row[0], row[2]))
    hits = 0
    total = 0.0
    for rank, (_, label, _) in enumerate(ordered, 1):
        if label:
            hits += 1
            total += hits / rank
    return total / positives


def metrics(rows: list[dict[str, object]], score_field: str, novel_denominator: int) -> dict[str, object]:
    scores = [float(row[score_field]) for row in rows]
    labels = [int(row["target_present"]) for row in rows]
    keys = [f"{row['fold_id']}|{row['predicted_fourth']}|{row['operation_A']}|{row['operation_B']}" for row in rows]
    positives = sum(labels)
    unique_correct = len({(row["fold_id"], row["predicted_fourth"]) for row in rows if int(row["target_present"])})
    return {
        "predictions": len(rows),
        "exact_correct": positives,
        "precision": positives / len(rows) if rows else 0.0,
        "coverage_of_held_novel_types": unique_correct / novel_denominator if novel_denominator else 0.0,
        "novel_type_denominator": novel_denominator,
        "average_precision": average_precision(scores, labels, keys),
        "auc": auc(scores, labels),
        "mean_positive_score": sum(score for score, label in zip(scores, labels) if label) / positives if positives else None,
        "mean_negative_score": sum(score for score, label in zip(scores, labels) if not label) / (len(rows) - positives) if len(rows) > positives else None,
    }


def rank_rows(rows: list[dict[str, object]], fields: list[str]) -> None:
    for field in fields:
        rank_field = field.replace("_score", "_rank_in_fold")
        for rank, row in enumerate(sorted(rows, key=lambda item: (-float(item[field]), str(item["predicted_fourth"]))), 1):
            row[rank_field] = rank


def score_fold_candidates(
    candidates: list[dict[str, object]], held_folio: str, folio_count: int,
    train_forms: set[str], held_forms: set[str], train_freq: Counter[str],
    held_loci: dict[str, set[str]], kt2, kt4,
) -> None:
    for row in candidates:
        target = str(row["predicted_fourth"])
        visible = (str(row["base_X"]), str(row["A_X"]), str(row["B_X"]))
        row["fold_id"] = held_folio
        row["training_folios"] = folio_count - 1
        row["training_form_types"] = len(train_forms)
        row["target_hidden_from_training"] = 1
        row["target_present"] = int(target in held_forms)
        row["target_loci"] = ";".join(sorted(held_loci[target]))
        row["character_order2_kt_score"] = kt2(target)
        row["character_order4_kt_score"] = kt4(target)
        row["visible_whole_group_frequency_score"] = sum(math.log2(1 + train_freq[value]) for value in visible)
        row["nearest_edit_score"] = -sum(levenshtein(target, value) for value in visible) / 3
        row["model_exposure"] = "ENTIRE_PHYSICAL_FOLIO_EXCLUDED_BEFORE_OPERATION_DISCOVERY"
        row["claim_state"] = "COMPUTATIONAL_HOLDOUT_NOT_NEW_EVIDENCE"
        row.pop("operation_A_tuple", None)
        row.pop("operation_B_tuple", None)
    rank_rows(
        candidates,
        [
            "paradigm_score", "character_order2_kt_score", "character_order4_kt_score",
            "visible_whole_group_frequency_score", "nearest_edit_score",
        ],
    )


def permutation_test(rows: list[dict[str, object]], score_fields: list[str]) -> dict[str, object]:
    labels = np.array([int(row["target_present"]) for row in rows], dtype=np.int8)
    positives = int(labels.sum())
    orders = {
        field: np.array(sorted(range(len(rows)), key=lambda index: (-float(rows[index][field]), str(rows[index]["fold_id"]), str(rows[index]["predicted_fourth"]))), dtype=np.int64)
        for field in score_fields
    }
    folds: dict[str, np.ndarray] = {}
    for fold in sorted({str(row["fold_id"]) for row in rows}):
        folds[fold] = np.array([index for index, row in enumerate(rows) if row["fold_id"] == fold], dtype=np.int64)

    def ap_fast(y: np.ndarray, order: np.ndarray) -> float:
        if positives == 0:
            return 0.0
        ordered = y[order]
        cumulative = np.cumsum(ordered)
        ranks = np.arange(1, len(order) + 1)
        return float(np.sum((cumulative / ranks) * ordered) / positives)

    observed = {field: ap_fast(labels, order) for field, order in orders.items()}
    observed_delta = observed["paradigm_score"] - max(observed[field] for field in score_fields if field != "paradigm_score")
    rng = np.random.default_rng(PERMUTATION_SEED)
    exceed = 0
    for _ in range(PERMUTATION_WORLDS):
        permuted = labels.copy()
        for indices in folds.values():
            permuted[indices] = rng.permutation(permuted[indices])
        aps = {field: ap_fast(permuted, order) for field, order in orders.items()}
        delta = aps["paradigm_score"] - max(aps[field] for field in score_fields if field != "paradigm_score")
        exceed += int(delta >= observed_delta - 1e-15)
    return {
        "worlds": PERMUTATION_WORLDS,
        "seed": PERMUTATION_SEED,
        "observed_average_precision": observed,
        "observed_advantage_over_best_string": observed_delta,
        "exceedances": exceed,
        "inclusive_plus_one_p": (exceed + 1) / (PERMUTATION_WORLDS + 1),
    }


def main() -> None:
    records, rejected = load_records()
    folios = sorted({row["folio"] for row in records})
    if any(row["page"].startswith("f84r") for row in records):
        raise RuntimeError("f84r entered nested corpus")

    transformation_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    q_predictions: list[dict[str, object]] = []
    novel_denominator = 0
    named_operation_fold_counts = Counter()

    for fold_index, held_folio in enumerate(folios, 1):
        train = [row for row in records if row["folio"] != held_folio]
        held = [row for row in records if row["folio"] == held_folio]
        train_freq = Counter(row["surface"] for row in train)
        train_forms = set(train_freq)
        held_forms = {row["surface"] for row in held}
        held_novel = held_forms - train_forms
        novel_denominator += len(held_novel)
        form_folios: dict[str, set[str]] = defaultdict(set)
        for row in train:
            form_folios[row["surface"]].add(row["folio"])
        selected, edge_maps = discover_operations(train_forms, train_freq, form_folios)
        operation_set_hash = canonical_sha(
            [
                {
                    "operation_id": row["operation_id"],
                    "edge_types": row["edge_types"],
                    "edge_occurrence_support": row["edge_occurrence_support"],
                    "edge_folios": row["edge_folios"],
                    "rank": row["rank_within_stratum"],
                }
                for row in selected
            ]
        )
        for row in selected:
            operation = row["operation"]
            family, old, new = operation
            transformation_rows.append(
                {
                    "fold_id": held_folio,
                    "operation_id": row["operation_id"],
                    "operation_family": family,
                    "old_edge": old,
                    "new_edge": new,
                    "stratum": row["stratum"],
                    "rank_within_stratum": row["rank_within_stratum"],
                    "training_edge_types": row["edge_types"],
                    "training_edge_occurrence_support": row["edge_occurrence_support"],
                    "training_edge_folios": row["edge_folios"],
                    "operation_set_sha256": operation_set_hash,
                    "held_folio_excluded_before_discovery": 1,
                    "claim_state": "TRAINING_DISCOVERED_FORMAL_RULE_NO_LINGUISTIC_STATUS",
                }
            )
            if str(row["operation_id"]) in {
                "PREFIX_ADD:q", "SUFFIX_ADD:dy", "SUFFIX_ADD:dal", "SUFFIX_ADD:dar",
                "PREFIX_REPLACE:d>s", "PREFIX_REPLACE:o>ot", "SUFFIX_REPLACE:dal>dar",
                "SUFFIX_REPLACE:dal>dy", "SUFFIX_REPLACE:dar>dy",
            }:
                named_operation_fold_counts[str(row["operation_id"])] += 1

        candidates, q_candidates, eligible_pairs = fold_candidates(train_forms, selected, edge_maps)
        kt2 = kt_model(train_freq, 2)
        kt4 = kt_model(train_freq, 4)
        held_loci: dict[str, set[str]] = defaultdict(set)
        for row in held:
            held_loci[row["surface"]].add(row["locus"])
        score_fold_candidates(candidates, held_folio, len(folios), train_forms, held_forms, train_freq, held_loci, kt2, kt4)
        score_fold_candidates(q_candidates, held_folio, len(folios), train_forms, held_forms, train_freq, held_loci, kt2, kt4)
        predictions.extend(candidates)
        q_predictions.extend(q_candidates)
        positives = sum(int(row["target_present"]) for row in candidates)
        q_positives = sum(int(row["target_present"]) for row in q_candidates)
        digest_fields = (
            "predicted_fourth", "operation_A", "operation_B", "base_X", "A_X", "B_X",
            "training_triplets", "training_complete", "paradigm_score", "character_order2_kt_score",
            "character_order4_kt_score", "visible_whole_group_frequency_score", "nearest_edit_score", "target_present",
        )
        candidate_stream_hash = canonical_sha(
            [{field: row[field] for field in digest_fields} for row in sorted(candidates, key=lambda item: str(item["predicted_fourth"]))]
        )
        q_candidate_stream_hash = canonical_sha(
            [{field: row[field] for field in digest_fields} for row in sorted(q_candidates, key=lambda item: str(item["predicted_fourth"]))]
        )
        fold_rows.append(
            {
                "fold_index": fold_index,
                "fold_id": held_folio,
                "held_physical_groups": len(held),
                "held_form_types": len(held_forms),
                "held_novel_form_types": len(held_novel),
                "training_physical_groups": len(train),
                "training_form_types": len(train_forms),
                "discovered_eligible_operations": len(selected),
                "eligible_operation_pairs": eligible_pairs,
                "predicted_novel_types": len(candidates),
                "exact_correct": positives,
                "q_right_predictions": len(q_candidates),
                "q_right_correct": q_positives,
                "operation_set_sha256": operation_set_hash,
                "candidate_stream_sha256": candidate_stream_hash,
                "q_right_candidate_stream_sha256": q_candidate_stream_hash,
            }
        )

    score_models = [
        ("NESTED_PARADIGM", "paradigm_score"),
        ("CHARACTER_ORDER2_KT", "character_order2_kt_score"),
        ("CHARACTER_ORDER4_KT", "character_order4_kt_score"),
        ("VISIBLE_WHOLE_GROUP_FREQUENCY", "visible_whole_group_frequency_score"),
        ("NEAREST_EDIT_DISTANCE", "nearest_edit_score"),
    ]
    baseline_rows: list[dict[str, object]] = []
    all_metrics = {}
    q_rows = q_predictions
    for scope, rows, denominator in (("ALL_DISCOVERED_ALGEBRA", predictions, novel_denominator), ("PREDECLARED_Q_RIGHT_SUBGROUP", q_rows, novel_denominator)):
        for model, field in score_models:
            value = metrics(rows, field, denominator)
            all_metrics[scope, model] = value
            rank_field = field.replace("_score", "_rank_in_fold")
            baseline_rows.append(
                {
                    "scope": scope,
                    "model": model,
                    **value,
                    "top1_hits": sum(int(row[rank_field]) == 1 and int(row["target_present"]) for row in rows),
                    "top5_hits": sum(int(row[rank_field]) <= 5 and int(row["target_present"]) for row in rows),
                    "comparison_scope": "Identical training-discovered exact fourth-form candidates",
                }
            )
    baseline_rows.append(
        {
            "scope": "ISOLATED_MISSING_GROUP",
            "model": "GDT001_CONTEXT_MIXER",
            "predictions": 0,
            "exact_correct": 0,
            "precision": "",
            "coverage_of_held_novel_types": "",
            "novel_type_denominator": novel_denominator,
            "average_precision": "",
            "auc": "",
            "mean_positive_score": "",
            "mean_negative_score": "",
            "top1_hits": "",
            "top5_hits": "",
            "comparison_scope": "NOT_DIRECTLY_COMPARABLE: full serialized context required",
        }
    )

    score_fields = [field for _, field in score_models]
    permutation = permutation_test(predictions, score_fields)
    paradigm = all_metrics["ALL_DISCOVERED_ALGEBRA", "NESTED_PARADIGM"]
    string_models = [all_metrics["ALL_DISCOVERED_ALGEBRA", model] for model, _ in score_models if model != "NESTED_PARADIGM"]
    best_string_ap = max(float(row["average_precision"]) for row in string_models if row["average_precision"] is not None)
    paradigm_advantage = float(paradigm["average_precision"]) - best_string_ap
    q_paradigm = all_metrics["PREDECLARED_Q_RIGHT_SUBGROUP", "NESTED_PARADIGM"]
    q_string = [all_metrics["PREDECLARED_Q_RIGHT_SUBGROUP", model] for model, _ in score_models if model != "NESTED_PARADIGM"]
    q_best_string_ap = max(float(row["average_precision"]) for row in q_string if row["average_precision"] is not None) if q_rows and int(q_paradigm["exact_correct"]) else 0.0
    q_advantage = (float(q_paradigm["average_precision"]) - q_best_string_ap) if q_paradigm["average_precision"] is not None else 0.0
    exact_correct = int(paradigm["exact_correct"])
    if exact_correct >= 5 and paradigm_advantage >= 0.02 and permutation["inclusive_plus_one_p"] <= 0.05 and q_advantage > 0:
        decision = "PRODUCTIVE COMPOSITION SUPPORTED"
    elif exact_correct > 0 and paradigm_advantage > 0:
        decision = "LIMITED/LOCAL COMPOSITION ONLY"
    elif exact_correct > 0:
        decision = "NOT DISTINGUISHABLE FROM STRING STATISTICS"
    else:
        decision = "PRODUCTIVE COMPOSITION FALSIFIED"

    counterexamples = [
        {
            "candidate": "NESTED_TRANSFORMATION_ALGEBRA",
            "counterexample": "Every transformation and operation pair must be reselected without the held folio.",
            "evidence": f"{len(folios)} physical-folio folds; operation-set hashes are fold-specific",
            "impact": "Global GDT003 transformation-template leakage is removed.",
        },
        {
            "candidate": "ALGEBRA_BEATS_STRING_STATISTICS",
            "counterexample": "Compare nested paradigm AP with the best score on the identical candidate targets.",
            "evidence": f"paradigm advantage={paradigm_advantage:.12f}; permutation p={permutation['inclusive_plus_one_p']:.12f}",
            "impact": decision,
        },
        {
            "candidate": "Q_PLUS_RIGHT_EDGE",
            "counterexample": "The named subgroup receives no forced operation inclusion and must survive fold-local discovery.",
            "evidence": f"predictions={len(q_rows)};correct={q_paradigm['exact_correct']};AP advantage={q_advantage:.12f}",
            "impact": "Formal compatibility only; no q/dy/dal/dar meaning or morphology.",
        },
        {
            "candidate": "INDEPENDENT_REPLICATION",
            "counterexample": "All manuscript readings and the earlier successes were public before masking.",
            "evidence": "Nested computational holdout, not newly acquired manuscript evidence",
            "impact": "Correct predictions are model-hidden but not external evidence.",
        },
        {
            "candidate": "THREE_READING_REPLICATION",
            "counterexample": "ZL3b, IT2a, and RF1b are alternate readings of one object.",
            "evidence": f"{rejected} ambiguous/topology-disagreement keys excluded",
            "impact": "No N-times-three inflation.",
        },
        {
            "candidate": "F84R_HOLDOUT_USE",
            "counterexample": "The f84r routing key is discarded before formal retention.",
            "evidence": "zero f84r records, transformations, candidates, or scores",
            "impact": "f84r remains sealed.",
        },
    ]

    correct = sorted(
        [row for row in predictions if int(row["target_present"])],
        key=lambda row: (str(row["fold_id"]), str(row["predicted_fourth"])),
    )
    q_correct = sorted(
        [row for row in q_rows if int(row["target_present"])],
        key=lambda row: (str(row["fold_id"]), str(row["predicted_fourth"])),
    )
    correct_export = [{"evaluation_scope": "ALL_DISCOVERED_ALGEBRA", **row} for row in correct]
    correct_export.extend({"evaluation_scope": "PREDECLARED_Q_RIGHT_SUBGROUP", **row} for row in q_correct)
    top_export: list[dict[str, object]] = []
    for scope, rows in (("ALL_DISCOVERED_ALGEBRA", predictions), ("PREDECLARED_Q_RIGHT_SUBGROUP", q_rows)):
        for model, field in score_models:
            rank_field = field.replace("_score", "_rank_in_fold")
            for row in rows:
                if int(row[rank_field]) <= 5:
                    top_export.append(
                        {
                            "evaluation_scope": scope,
                            "model": model,
                            "fold_id": row["fold_id"],
                            "rank_in_fold": row[rank_field],
                            "score": row[field],
                            "target_present": row["target_present"],
                            "predicted_fourth": row["predicted_fourth"],
                            "operation_A": row["operation_A"],
                            "operation_B": row["operation_B"],
                            "base_X": row["base_X"],
                            "A_X": row["A_X"],
                            "B_X": row["B_X"],
                            "target_loci": row["target_loci"] or "NONE",
                        }
                    )

    write_tsv(OUT_TRANS, transformation_rows)
    write_tsv(OUT_FOLDS, fold_rows)
    write_tsv(OUT_CORRECT, correct_export)
    write_tsv(OUT_TOP, top_export)
    write_tsv(OUT_BASE, baseline_rows)
    write_tsv(OUT_COUNTER, counterexamples)

    old_successes = {
        (row["fold_id"], row["predicted_fourth"])
        for row in json.loads(OLD_RESULT.read_text(encoding="utf-8"))["highest_value_model_hidden_predictions"]
    }
    result: dict[str, object] = {
        "schema": "GDT003_NESTED_HELDOUT_RESULT_V1",
        "experiment": "GDT003_NESTED_HELDOUT_REPLICATION",
        "status": decision,
        "freeze_commit": FREEZE_COMMIT,
        "corpus": {
            "strict_physical_groups": len(records),
            "physical_folios": len(folios),
            "ambiguous_or_topology_disagreement_keys_excluded": rejected,
            "alternate_readings_not_replications": True,
        },
        "holdout": {
            "unit": "COMPLETE_PHYSICAL_FOLIO",
            "f84r_formal_payload_retained_joined_or_scored": False,
            "held_folio_excluded_before_transformation_discovery": True,
        },
        "selector": {
            "operation_grammar": "TARGET_BLIND_EDGE_EDIT_V1",
            "minimum_edge_types": MIN_EDGES,
            "minimum_training_folios": MIN_FOLIOS,
            "top_per_edit_length_stratum": PER_STRATUM,
            "minimum_pair_triplets": MIN_PAIR_TRIPLETS,
            "minimum_pair_complete": MIN_PAIR_COMPLETE,
        },
        "prediction": {
            "all": paradigm,
            "best_string_average_precision": best_string_ap,
            "paradigm_AP_advantage_over_best_string": paradigm_advantage,
            "q_right_subgroup": q_paradigm,
            "q_right_best_string_average_precision": q_best_string_ap,
            "q_right_AP_advantage_over_best_string": q_advantage,
            "correct_prediction_examples": [
                {
                    "fold_id": row["fold_id"],
                    "predicted_fourth": row["predicted_fourth"],
                    "operation_A": row["operation_A"],
                    "operation_B": row["operation_B"],
                    "base_X": row["base_X"],
                    "A_X": row["A_X"],
                    "B_X": row["B_X"],
                    "target_loci": row["target_loci"],
                    "q_right_named_subgroup": row["q_right_named_subgroup"],
                    "also_in_original_gdt003_nine": int((row["fold_id"], row["predicted_fourth"]) in old_successes),
                }
                for row in correct[:50]
            ],
            "complete_correct_prediction_artifact": str(OUT_CORRECT.relative_to(ROOT)),
        },
        "permutation": permutation,
        "named_operation_discovery_folds": dict(sorted(named_operation_fold_counts.items())),
        "counts": {
            "folds": len(fold_rows),
            "transformation_rows": len(transformation_rows),
            "prediction_rows": len(predictions),
            "q_right_prediction_rows": len(q_rows),
            "exact_correct": exact_correct,
            "q_right_exact_correct": int(q_paradigm["exact_correct"]),
            "correct_prediction_artifact_rows": len(correct_export),
            "top_prediction_artifact_rows": len(top_export),
            "old_gdt003_nine_recovered": sum((row["fold_id"], row["predicted_fourth"]) in old_successes for row in correct),
        },
        "inputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (METHOD, SEPARATOR, ALIGNMENT, OLD_RESULT)
        },
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
        "claim_ceiling": "Formal source-group composition only; no morpheme, grammatical category, language, sound, meaning, plaintext, or translation.",
    }

    report = f"""# GDT003 nested held-folio replication report

Status: **{decision}**

## Result

This replication removes the main selection weakness in the first GDT003 run.
Each of {len(folios)} outer folds excluded a complete physical folio, discovered
its added/replaced edge strings from training types only, selected operations
within the frozen edit-length strata, froze compatible operation pairs, and
then predicted exact types on the unseen folio.

The nested algebra made {len(predictions):,} distinct fold-target predictions
and recovered {exact_correct} exact unseen-folio types. Precision was only
{float(paradigm['precision']):.12f}. Its average precision
was {float(paradigm['average_precision']):.12f}; the strongest string baseline
was {best_string_ap:.12f}. The difference was {paradigm_advantage:+.12f}.
The 4,096-world within-folio label-permutation comparison gave
`p={permutation['inclusive_plus_one_p']:.12f}` for algebra minus the best string
baseline.

## Same-candidate baseline comparison

| model | predictions | exact | AP | AUC | top-1 | top-5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
"""
    for row in baseline_rows:
        if row["scope"] != "ALL_DISCOVERED_ALGEBRA" or row["model"] == "GDT001_CONTEXT_MIXER":
            continue
        ap_value = float(row["average_precision"])
        auc_value = float(row["auc"])
        report += f"| {row['model']} | {row['predictions']} | {row['exact_correct']} | {ap_value:.12f} | {auc_value:.12f} | {row['top1_hits']} | {row['top5_hits']} |\n"

    report += f"""

The GDT001 context mixer remains a stronger complete-source model, but it is
not assigned an invented isolated-target score because its probabilities
depend on canonical serialized context.

## Training-discovered q plus right-edge subgroup

The named subgroup was not forced into any fold. The rules had to survive the
same training-only support and stratum selector as every other edge edit.
It generated {len(q_rows):,} candidates and {int(q_paradigm['exact_correct'])}
correct held-folio completions. Paradigm AP was
{float(q_paradigm['average_precision']) if q_paradigm['average_precision'] is not None else 0.0:.12f};
the subgroup's strongest string AP was {q_best_string_ap:.12f}, a difference of
{q_advantage:+.12f}.

Fold survival counts for the previously discussed operations are recorded in
`gdt003_nested_result.json`; survival means only that the rule was rediscovered
from that fold's training corpus. It does not assign operator or suffix status.

## Exact model-hidden completions

"""
    if correct:
        report += "| held folio | visible cells | predicted fourth | learned operations | held locus | q/right | prior-nine |\n| --- | --- | --- | --- | --- | ---: | ---: |\n"
        for row in correct[:25]:
            prior = int((row["fold_id"], row["predicted_fourth"]) in old_successes)
            report += (
                f"| {row['fold_id']} | `{row['base_X']}`, `{row['A_X']}`, `{row['B_X']}` | `{row['predicted_fourth']}` | "
                f"`{row['operation_A']}` + `{row['operation_B']}` | {row['target_loci']} | {row['q_right_named_subgroup']} | {prior} |\n"
            )
        report += f"\nFirst 25 of {len(correct)} broad-algebra hits are shown. All exact hits, including the independently deduplicated q/right hits, are in `{OUT_CORRECT.name}`.\n"
    else:
        report += "No exact held-folio completion survived nested discovery.\n"

    report += f"""

These are computationally hidden predictions of already-public readings, not
new manuscript evidence. The editions are alternate observations, not three
replications.

## Falsification assessment

- The actual transformation strings were learned independently in every fold;
  global GDT003's nine templates were not supplied.
- Every candidate target was absent from its training corpus.
- The comparison uses identical candidates for paradigm, KT2, KT4,
  visible-cell frequency, and nearest-edit scores.
- The broad selector emits over a million candidates and therefore has very
  low absolute precision. The decisive quantity is the same-candidate AP
  advantage `{paradigm_advantage:+.12f}`, not attractive exact forms alone.
- f84r remained sealed: no retained record, operation, candidate, or score uses
  its formal payload.
- No `q`, `dy`, `dal`, or `dar` meaning, morpheme, POS, language, or translation
  follows.

## Conclusion

The nested test asks a stricter question than the original GDT003 result: can
the algebra itself be rediscovered without the target folio and then outperform
ordinary string statistics? The answer is encoded by the same-candidate AP
comparison and the preregistered decision above.

{decision}
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    result["outputs"] = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in (OUT_TRANS, OUT_FOLDS, OUT_CORRECT, OUT_TOP, OUT_BASE, OUT_COUNTER, OUT_REPORT)
    }
    normalized = json.loads(json.dumps(result, sort_keys=True, ensure_ascii=True))
    result["result_content_sha256"] = canonical_sha(normalized)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(decision)
    print(json.dumps(result["counts"], sort_keys=True))
    print(f"AP advantage {paradigm_advantage:+.12f}; permutation p={permutation['inclusive_plus_one_p']:.12f}")


if __name__ == "__main__":
    main()
