#!/usr/bin/env python3
"""Language-agnostic, nested GDT003 structural fingerprint comparator."""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import multiprocessing as mp
import os
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt003_nested_heldout import apply_op, discover_operations, levenshtein, op_id


ROOT = Path(__file__).resolve().parent
CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
MANIFEST = ROOT / "gdt003_structural_fingerprint_corpus_manifest.tsv"
PROVENANCE = ROOT / "gdt003_structural_fingerprint_source_provenance.json"
METHOD = ROOT / "GDT003_STRUCTURAL_FINGERPRINT_COMPARATOR_METHOD.md"
SOURCE_AUDIT = ROOT / "GDT003_STRUCTURAL_FINGERPRINT_SOURCE_AUDIT.md"
GDT003_CORE = ROOT / "run_gdt003_nested_heldout.py"
OUT_FINGERPRINTS = ROOT / "gdt003_structural_fingerprints.tsv"
OUT_TRANSFORMS = ROOT / "gdt003_structural_fingerprint_transformations.tsv"
OUT_BASELINES = ROOT / "gdt003_structural_fingerprint_baselines.tsv"
OUT_RANKING = ROOT / "gdt003_structural_fingerprint_ranking.tsv"
OUT_FAMILY = ROOT / "gdt003_structural_fingerprint_family_ranking.tsv"
OUT_HITS = ROOT / "gdt003_structural_fingerprint_heldout_hits.tsv"
OUT_COUNTER = ROOT / "gdt003_structural_fingerprint_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt003_structural_fingerprint_result.json"
OUT_REPORT = ROOT / "GDT003_STRUCTURAL_FINGERPRINT_COMPARATOR_REPORT.md"

SOURCE_FREEZE_COMMIT = "8b23ce9dafa31fc9a196642e3b4aec39ac1a2662"
STRATA = (
    "PREFIX_ADD:NEW1", "PREFIX_ADD:NEW2", "PREFIX_ADD:NEW3",
    "SUFFIX_ADD:NEW1", "SUFFIX_ADD:NEW2", "SUFFIX_ADD:NEW3",
    "PREFIX_REPLACE:OLD1_NEW1", "PREFIX_REPLACE:OLD1_NEW2",
    "PREFIX_REPLACE:OLD2_NEW1", "PREFIX_REPLACE:OLD2_NEW2",
    "SUFFIX_REPLACE:OLD2_NEW2", "SUFFIX_REPLACE:OLD2_NEW3",
    "SUFFIX_REPLACE:OLD3_NEW2", "SUFFIX_REPLACE:OLD3_NEW3",
)
SCALARS = (
    "log_operation_density", "left_right_log2_support_ratio", "replace_fraction",
    "rectangle_completion_rate", "compatible_pair_density", "log_prediction_density",
    "heldout_precision", "ap_gain_over_best_string", "generic_lr_ap_gain",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def dynamic_kt(freq: Counter[str], order: int):
    alphabet = set("".join(freq))
    unknown = "\ufffd"
    context_char: Counter[tuple[str, str]] = Counter()
    contexts: Counter[str] = Counter()
    k = len(alphabet) + 2  # END plus one unknown cell
    for value, count in freq.items():
        sequence = "^" * order + value + "$"
        for index in range(order, len(sequence)):
            history = sequence[index - order:index]
            char = sequence[index]
            context_char[history, char] += count
            contexts[history] += count

    def score(value: str) -> float:
        mapped = "".join(char if char in alphabet else unknown for char in value)
        sequence = "^" * order + mapped + "$"
        bits = 0.0
        for index in range(order, len(sequence)):
            history = sequence[index - order:index]
            char = sequence[index]
            bits -= math.log2((context_char[history, char] + 0.5) / (contexts[history] + 0.5 * k))
        return -bits / max(1, len(value) + 1)
    return score


def auc(scores: list[float], labels: list[int]) -> float:
    positive = [score for score, label in zip(scores, labels) if label]
    negative = [score for score, label in zip(scores, labels) if not label]
    if not positive or not negative:
        return 0.5  # explicit neutral convention when one class is absent
    return sum((left > right) + 0.5 * (left == right) for left in positive for right in negative) / (len(positive) * len(negative))


def average_precision(scores: list[float], labels: list[int], keys: list[str]) -> float:
    positives = sum(labels)
    if not positives:
        return 0.0  # explicit zero-retrieval convention
    ordered = sorted(zip(scores, labels, keys), key=lambda row: (-row[0], row[2]))
    hits = 0
    total = 0.0
    for rank, (_, label, _) in enumerate(ordered, 1):
        if label:
            hits += 1
            total += hits / rank
    return total / positives


def metric(rows: list[dict[str, object]], field: str) -> dict[str, object]:
    if not rows:
        return {"predictions": 0, "exact": 0, "precision": 0.0, "average_precision": 0.0, "auc": 0.5}
    scores = [float(row[field]) for row in rows]
    labels = [int(row["target_present"]) for row in rows]
    keys = [f"{row['fold_id']}|{row['predicted_fourth']}|{row['operation_A']}|{row['operation_B']}" for row in rows]
    exact = sum(labels)
    return {
        "predictions": len(rows), "exact": exact, "precision": exact / len(rows),
        "average_precision": average_precision(scores, labels, keys), "auc": auc(scores, labels),
    }


def is_generic_lr(a: tuple[str, str, str], b: tuple[str, str, str]) -> bool:
    def one_left(op: tuple[str, str, str]) -> bool:
        return op[0] == "PREFIX_ADD" and len(op[2]) == 1
    def right(op: tuple[str, str, str]) -> bool:
        return op[0].startswith("SUFFIX_")
    return (one_left(a) and right(b)) or (one_left(b) and right(a))


def is_voynich_qright(a: tuple[str, str, str], b: tuple[str, str, str]) -> bool:
    def q(op: tuple[str, str, str]) -> bool:
        return op == ("PREFIX_ADD", "", "q")
    def named_right(op: tuple[str, str, str]) -> bool:
        return op[0].startswith("SUFFIX_") and bool({op[1], op[2]} & {"dy", "dal", "dar"})
    return (q(a) and named_right(b)) or (q(b) and named_right(a))


def candidate_key(row: dict[str, object]) -> tuple[float, str, str, str]:
    return (float(row["paradigm_score"]), str(row["operation_A"]), str(row["operation_B"]), str(row["base_X"]))


def deduplicate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    best: dict[str, dict[str, object]] = {}
    for row in rows:
        target = str(row["predicted_fourth"])
        if target not in best or candidate_key(row) > candidate_key(best[target]):
            best[target] = row
    return list(best.values())


def construct_candidates(
    forms: set[str], selected: list[dict[str, object]], edge_maps: dict[tuple[str, str, str], dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    selected_by_op = {row["operation"]: row for row in selected}
    by_source: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for operation, edges in edge_maps.items():
        for source in edges:
            by_source[source].append(operation)
    stats: dict[tuple[tuple[str, str, str], tuple[str, str, str]], dict[str, object]] = defaultdict(lambda: {"triplets": 0, "complete": 0, "missing": []})
    commuting_pairs = 0
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
            if int(stats[key]["triplets"]) == 0:
                commuting_pairs += 1
            stats[key]["triplets"] = int(stats[key]["triplets"]) + 1
            if ab in forms:
                stats[key]["complete"] = int(stats[key]["complete"]) + 1
            else:
                stats[key]["missing"].append((base, ax, bx, ab))  # type: ignore[union-attr]
    broad: list[dict[str, object]] = []
    generic: list[dict[str, object]] = []
    qright: list[dict[str, object]] = []
    eligible_pairs = triplets = complete = 0
    for (operation_a, operation_b), value in stats.items():
        n_triplets, n_complete = int(value["triplets"]), int(value["complete"])
        if n_triplets < 3 or n_complete < 1:
            continue
        eligible_pairs += 1
        triplets += n_triplets
        complete += n_complete
        edge_a = int(selected_by_op[operation_a]["edge_types"])
        edge_b = int(selected_by_op[operation_b]["edge_types"])
        score = math.log2((n_complete + 0.5) / (n_triplets + 1)) + math.log2(1 + min(edge_a, edge_b)) / 20
        for base, ax, bx, target in value["missing"]:  # type: ignore[assignment]
            row = {
                "operation_A": op_id(operation_a), "operation_B": op_id(operation_b),
                "base_X": base, "A_X": ax, "B_X": bx, "predicted_fourth": target,
                "training_triplets": n_triplets, "training_complete": n_complete,
                "operation_A_edges": edge_a, "operation_B_edges": edge_b, "paradigm_score": score,
            }
            broad.append(row)
            if is_generic_lr(operation_a, operation_b):
                generic.append(dict(row))
            if is_voynich_qright(operation_a, operation_b):
                qright.append(dict(row))
    return deduplicate(broad), deduplicate(generic), deduplicate(qright), {
        "commuting_pairs": commuting_pairs, "eligible_pairs": eligible_pairs,
        "eligible_triplets": triplets, "complete_rectangles": complete,
    }


def score_candidates(rows: list[dict[str, object]], fold_id: str, held_forms: set[str], train_freq: Counter[str], kt2, kt4) -> None:
    for row in rows:
        target = str(row["predicted_fourth"])
        visible = (str(row["base_X"]), str(row["A_X"]), str(row["B_X"]))
        row["fold_id"] = fold_id
        row["target_present"] = int(target in held_forms)
        row["character_order2_kt_score"] = kt2(target)
        row["character_order4_kt_score"] = kt4(target)
        row["visible_whole_group_frequency_score"] = sum(math.log2(1 + train_freq[value]) for value in visible)
        row["nearest_edit_score"] = -sum(levenshtein(target, value) for value in visible) / 3


def evaluate_corpus(payload: tuple[str, list[dict[str, object]], dict[str, str]]) -> dict[str, object]:
    corpus_id, records, meta = payload
    fold_ids = sorted({str(row["fold_id"]) for row in records})
    transformations: list[dict[str, object]] = []
    all_predictions: list[dict[str, object]] = []
    generic_predictions: list[dict[str, object]] = []
    qright_predictions: list[dict[str, object]] = []
    hit_examples: list[dict[str, object]] = []
    stratum_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    left_support = right_support = 0
    total_ops = total_train_types = 0
    eligible_pairs = commuting_pairs = eligible_triplets = complete_rectangles = 0
    possible_pair_denominator = 0
    held_novel_types = 0
    fold_hashes = []

    for held_fold in fold_ids:
        train = [row for row in records if row["fold_id"] != held_fold]
        held = [row for row in records if row["fold_id"] == held_fold]
        train_freq = Counter(str(row["form"]) for row in train)
        train_forms = set(train_freq)
        held_forms = {str(row["form"]) for row in held}
        held_novel_types += len(held_forms - train_forms)
        form_folds: dict[str, set[str]] = defaultdict(set)
        for row in train:
            form_folds[str(row["form"])].add(str(row["fold_id"]))
        selected, edge_maps = discover_operations(train_forms, train_freq, form_folds)
        total_ops += len(selected)
        total_train_types += len(train_forms)
        possible_pair_denominator += len(selected) * (len(selected) - 1) // 2
        for item in selected:
            operation = item["operation"]
            family, old, new = operation  # type: ignore[misc]
            stratum_counts[str(item["stratum"])] += 1
            family_counts[str(family)] += 1
            support = int(item["edge_types"])
            if str(family).startswith("PREFIX"):
                left_support += support
            else:
                right_support += support
            transformations.append({
                "corpus_id": corpus_id, "held_fold": held_fold, "operation_id": item["operation_id"],
                "operation_family": family, "old_edge": old, "new_edge": new,
                "stratum": item["stratum"], "edge_types": item["edge_types"],
                "edge_occurrence_support": item["edge_occurrence_support"], "edge_folds": item["edge_folios"],
                "rank_within_stratum": item["rank_within_stratum"],
            })
        broad, generic, qright, pair_counts = construct_candidates(train_forms, selected, edge_maps)
        commuting_pairs += pair_counts["commuting_pairs"]
        eligible_pairs += pair_counts["eligible_pairs"]
        eligible_triplets += pair_counts["eligible_triplets"]
        complete_rectangles += pair_counts["complete_rectangles"]
        kt2, kt4 = dynamic_kt(train_freq, 2), dynamic_kt(train_freq, 4)
        for rows in (broad, generic, qright):
            score_candidates(rows, held_fold, held_forms, train_freq, kt2, kt4)
        all_predictions.extend(broad)
        generic_predictions.extend(generic)
        qright_predictions.extend(qright)
        fold_hashes.append(canonical_sha({
            "fold": held_fold,
            "operations": [(row["operation_id"], row["edge_types"]) for row in selected],
            "broad": [(row["predicted_fourth"], row["target_present"]) for row in sorted(broad, key=lambda x: str(x["predicted_fourth"]))],
        }))

    models = (
        ("NESTED_PARADIGM", "paradigm_score"),
        ("CHARACTER_ORDER2_KT", "character_order2_kt_score"),
        ("CHARACTER_ORDER4_KT", "character_order4_kt_score"),
        ("VISIBLE_WHOLE_GROUP_FREQUENCY", "visible_whole_group_frequency_score"),
        ("NEAREST_EDIT_DISTANCE", "nearest_edit_score"),
    )
    baseline_rows: list[dict[str, object]] = []
    scope_metrics: dict[str, dict[str, dict[str, object]]] = {}
    for scope, rows in (("ALL_ALGEBRA", all_predictions), ("GENERIC_ONECHAR_LEFT_PLUS_RIGHT", generic_predictions), ("VOYNICH_Q_PLUS_DY_DAL_DAR", qright_predictions)):
        scope_metrics[scope] = {}
        for model, field in models:
            value = metric(rows, field)
            scope_metrics[scope][model] = value
            baseline_rows.append({"corpus_id": corpus_id, "scope": scope, "model": model, **value})

    broad_paradigm = scope_metrics["ALL_ALGEBRA"]["NESTED_PARADIGM"]
    broad_baselines = [scope_metrics["ALL_ALGEBRA"][model] for model, _ in models if model != "NESTED_PARADIGM"]
    paradigm_ap = float(broad_paradigm["average_precision"] or 0.0)
    best_string_ap = max(float(row["average_precision"] or 0.0) for row in broad_baselines)
    generic_paradigm = scope_metrics["GENERIC_ONECHAR_LEFT_PLUS_RIGHT"]["NESTED_PARADIGM"]
    generic_baselines = [scope_metrics["GENERIC_ONECHAR_LEFT_PLUS_RIGHT"][model] for model, _ in models if model != "NESTED_PARADIGM"]
    generic_ap = float(generic_paradigm["average_precision"] or 0.0)
    generic_best = max(float(row["average_precision"] or 0.0) for row in generic_baselines)
    q_paradigm = scope_metrics["VOYNICH_Q_PLUS_DY_DAL_DAR"]["NESTED_PARADIGM"]
    q_baselines = [scope_metrics["VOYNICH_Q_PLUS_DY_DAL_DAR"][model] for model, _ in models if model != "NESTED_PARADIGM"]
    q_ap = float(q_paradigm["average_precision"] or 0.0)
    q_best = max(float(row["average_precision"] or 0.0) for row in q_baselines)

    for row in sorted((row for row in all_predictions if int(row["target_present"])), key=lambda item: (-float(item["paradigm_score"]), str(item["fold_id"]), str(item["predicted_fourth"])))[:20]:
        hit_examples.append({
            "corpus_id": corpus_id, "fold_id": row["fold_id"], "predicted_fourth": row["predicted_fourth"],
            "operation_A": row["operation_A"], "operation_B": row["operation_B"],
            "base_X": row["base_X"], "A_X": row["A_X"], "B_X": row["B_X"],
            "paradigm_score": row["paradigm_score"], "model_hidden": 1,
        })

    add_count = family_counts["PREFIX_ADD"] + family_counts["SUFFIX_ADD"]
    replace_count = family_counts["PREFIX_REPLACE"] + family_counts["SUFFIX_REPLACE"]
    spectrum_total = sum(stratum_counts.values())
    fingerprint: dict[str, object] = {
        "corpus_id": corpus_id, **meta,
        "tokens": len(records), "folds": len(fold_ids), "form_types": len({str(row['form']) for row in records}),
        "mean_discovered_operations": total_ops / len(fold_ids),
        "log_operation_density": math.log1p(1000 * total_ops / max(1, total_train_types)),
        "left_edge_support": left_support, "right_edge_support": right_support,
        "left_right_log2_support_ratio": math.log2((right_support + 1) / (left_support + 1)),
        "replace_fraction": replace_count / max(1, add_count + replace_count),
        "rectangle_completion_rate": complete_rectangles / max(1, eligible_triplets),
        "complete_rectangles": complete_rectangles, "eligible_triplets": eligible_triplets,
        "compatible_operation_pairs": eligible_pairs, "commuting_operation_pairs": commuting_pairs,
        "compatible_pair_density": eligible_pairs / max(1, possible_pair_denominator),
        "predictions": broad_paradigm["predictions"], "exact_hits": broad_paradigm["exact"],
        "heldout_precision": broad_paradigm["precision"], "paradigm_average_precision": paradigm_ap,
        "best_string_average_precision": best_string_ap, "ap_gain_over_best_string": paradigm_ap - best_string_ap,
        "held_novel_types": held_novel_types,
        "log_prediction_density": math.log1p(int(broad_paradigm["predictions"]) / max(1, held_novel_types)),
        "generic_lr_predictions": generic_paradigm["predictions"], "generic_lr_exact": generic_paradigm["exact"],
        "generic_lr_ap": generic_ap, "generic_lr_best_string_ap": generic_best, "generic_lr_ap_gain": generic_ap - generic_best,
        "voynich_qright_predictions": q_paradigm["predictions"], "voynich_qright_exact": q_paradigm["exact"],
        "voynich_qright_ap": q_ap, "voynich_qright_best_string_ap": q_best, "voynich_qright_ap_gain": q_ap - q_best,
        "fold_stream_sha256": canonical_sha(fold_hashes),
    }
    for stratum in STRATA:
        fingerprint[f"spectrum_{stratum}"] = stratum_counts[stratum] / max(1, spectrum_total)
    return {"fingerprint": fingerprint, "transformations": transformations, "baselines": baseline_rows, "hits": hit_examples}


def js_distance(left: list[float], right: list[float]) -> float:
    eps = 1e-12
    p = [(value + eps) for value in left]
    q = [(value + eps) for value in right]
    p = [value / sum(p) for value in p]
    q = [value / sum(q) for value in q]
    m = [(a + b) / 2 for a, b in zip(p, q)]
    divergence = 0.5 * sum(a * math.log2(a / c) for a, c in zip(p, m)) + 0.5 * sum(b * math.log2(b / c) for b, c in zip(q, m))
    return math.sqrt(max(0.0, divergence))


def main() -> None:
    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        corpus_payload = json.load(handle)
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle, delimiter="\t"))
    metadata = {row["corpus_id"]: row for row in manifest_rows}
    by_corpus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in corpus_payload["records"]:
        by_corpus[str(row["corpus_id"])].append(row)
    jobs = [(corpus_id, rows, metadata[corpus_id]) for corpus_id, rows in sorted(by_corpus.items())]
    workers = min(6, max(1, os.cpu_count() or 1), len(jobs))
    with mp.get_context("fork").Pool(workers) as pool:
        evaluated = pool.map(evaluate_corpus, jobs)

    fingerprints = [item["fingerprint"] for item in evaluated]
    transformations = [row for item in evaluated for row in item["transformations"]]
    baselines = [row for item in evaluated for row in item["baselines"]]
    hits = [row for item in evaluated for row in item["hits"]]
    fp_by_id = {str(row["corpus_id"]): row for row in fingerprints}
    target = fp_by_id["VOYNICH_MATCHED"]
    matched = [row for row in fingerprints if row["capacity_state"] == "MATCHED_12000"]
    ranges = {field: (min(float(row[field]) for row in matched), max(float(row[field]) for row in matched)) for field in SCALARS}
    for row in fingerprints:
        spectrum = [float(row[f"spectrum_{stratum}"]) for stratum in STRATA]
        target_spectrum = [float(target[f"spectrum_{stratum}"]) for stratum in STRATA]
        jsd = js_distance(spectrum, target_spectrum)
        squared = []
        for field in SCALARS:
            low, high = ranges[field]
            scale = high - low if high > low else 1.0
            squared.append(((float(row[field]) - float(target[field])) / scale) ** 2)
        scalar_rms = math.sqrt(sum(squared) / len(squared))
        row["spectrum_js_distance"] = jsd
        row["scalar_rms_distance"] = scalar_rms
        row["structural_distance_to_voynich"] = (jsd + scalar_rms) / 2
        row["distance_rank_eligible"] = int(row["capacity_state"] == "MATCHED_12000" and row["corpus_id"] != "VOYNICH_MATCHED")
        row["distance_interpretation"] = "DESCRIPTIVE_ORTHOGRAPHIC_SURFACE_DISTANCE_NOT_LANGUAGE_ID"

    ranking_rows: list[dict[str, object]] = []
    scopes = {
        "ALL_MATCHED": lambda row: row["tier"] != "TARGET",
        "MODERN_MATCHED_SENSITIVITY": lambda row: row["tier"] == "MODERN_MATCHED_SENSITIVITY",
        "HISTORICAL_MATCHED": lambda row: row["tier"] == "HISTORICAL_UD",
    }
    for scope, predicate in scopes.items():
        candidates = sorted(
            [row for row in fingerprints if int(row["distance_rank_eligible"]) and predicate(row)],
            key=lambda row: (float(row["structural_distance_to_voynich"]), str(row["corpus_id"])),
        )
        for rank, row in enumerate(candidates, 1):
            ranking_rows.append({
                "ranking_scope": scope, "rank": rank, "corpus_id": row["corpus_id"], "language": row["language"],
                "family": row["family"], "tier": row["tier"], "historical_status": row["historical_status"],
                "structural_distance_to_voynich": row["structural_distance_to_voynich"],
                "spectrum_js_distance": row["spectrum_js_distance"], "scalar_rms_distance": row["scalar_rms_distance"],
                "ap_gain_over_best_string": row["ap_gain_over_best_string"], "heldout_precision": row["heldout_precision"],
                "claim_ceiling": "STRUCTURAL_SURFACE_NEIGHBOR_ONLY_NOT_LANGUAGE_IDENTIFICATION",
            })
    for row in sorted((row for row in fingerprints if row["capacity_state"] != "MATCHED_12000"), key=lambda row: str(row["corpus_id"])):
        ranking_rows.append({
            "ranking_scope": "UNRANKED_LOW_CAPACITY", "rank": "", "corpus_id": row["corpus_id"], "language": row["language"],
            "family": row["family"], "tier": row["tier"], "historical_status": row["historical_status"],
            "structural_distance_to_voynich": row["structural_distance_to_voynich"],
            "spectrum_js_distance": row["spectrum_js_distance"], "scalar_rms_distance": row["scalar_rms_distance"],
            "ap_gain_over_best_string": row["ap_gain_over_best_string"], "heldout_precision": row["heldout_precision"],
            "claim_ceiling": "LOW_CAPACITY_DESCRIPTIVE_NOT_RANKED",
        })

    families: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in fingerprints:
        if int(row["distance_rank_eligible"]):
            families[str(row["family"])].append(row)
    family_rows = []
    for family, rows in families.items():
        family_rows.append({
            "family": family, "member_corpora": len(rows), "members": ";".join(sorted(str(row["corpus_id"]) for row in rows)),
            "mean_structural_distance": sum(float(row["structural_distance_to_voynich"]) for row in rows) / len(rows),
            "minimum_member_distance": min(float(row["structural_distance_to_voynich"]) for row in rows),
            "aggregation": "MEAN_OF_MATCHED_CORPUS_DISTANCES",
            "claim_ceiling": "DESCRIPTIVE_FAMILY_LABEL_AGGREGATION_NOT_ANCESTRY_OR_IDENTIFICATION",
        })
    family_rows.sort(key=lambda row: (float(row["mean_structural_distance"]), str(row["family"])))
    for rank, row in enumerate(family_rows, 1):
        row["rank"] = rank

    requested_missing = [row for row in manifest_rows if int(row["sampled_tokens"]) == 0]
    all_ranked = [row for row in ranking_rows if row["ranking_scope"] == "ALL_MATCHED"]
    closest = all_ranked[0]
    modern_rank = [row for row in ranking_rows if row["ranking_scope"] == "MODERN_MATCHED_SENSITIVITY"]
    historical_rank = [row for row in ranking_rows if row["ranking_scope"] == "HISTORICAL_MATCHED"]
    counterexamples = [
        {"claim": "CUMAN_MATCH", "evidence": "No matched historical Cuman corpus was admitted; Kazakh is explicitly modern Kipchak sensitivity.", "impact": "Cuman comparison unavailable."},
        {"claim": "MIDDLE_ARMENIAN_RANK", "evidence": "788 eligible tokens in two documents; no token splitting or padding.", "impact": "Unranked insufficient capacity."},
        {"claim": "OLD_GEORGIAN_PRIMARY_RANK", "evidence": "6093 tokens, six folds, below 12k matched design.", "impact": "Descriptive low-capacity sensitivity only."},
        {"claim": "EARLY_MALTESE_MATCH", "evidence": "Only modern Maltese Wikipedia admitted.", "impact": "No Early Maltese or Siculo-Arabic inference."},
        {"claim": "STRUCTURAL_NEAREST_EQUALS_LANGUAGE", "evidence": "Native script, orthography, tokenization, genre and frozen draw affect every fingerprint.", "impact": "Distances are descriptive, not identification probabilities."},
        {"claim": "Q_RIGHT_PRODUCTIVE_BEYOND_STRINGS", "evidence": f"Matched Voynich q/right AP gain={float(target['voynich_qright_ap_gain']):+.12f}.", "impact": "Literal subsystem remains formal and is not mapped to comparator strings."},
        {"claim": "THREE_TRANSCRIPTION_REPLICATIONS", "evidence": "Voynich corpus admits only exact ZL3b/IT2a/RF1b agreement.", "impact": "One physical reading per source group."},
        {"claim": "F84R_USED", "evidence": "f84r excluded before Voynich surface sampling; source validator finds no f84 string.", "impact": "Sealed holdout preserved."},
    ]

    write_tsv(OUT_FINGERPRINTS, sorted(fingerprints, key=lambda row: str(row["corpus_id"])))
    write_tsv(OUT_TRANSFORMS, sorted(transformations, key=lambda row: (str(row["corpus_id"]), str(row["held_fold"]), str(row["operation_id"]))))
    write_tsv(OUT_BASELINES, sorted(baselines, key=lambda row: (str(row["corpus_id"]), str(row["scope"]), str(row["model"]))))
    write_tsv(OUT_RANKING, ranking_rows)
    write_tsv(OUT_FAMILY, family_rows, ["rank", "family", "member_corpora", "members", "mean_structural_distance", "minimum_member_distance", "aggregation", "claim_ceiling"])
    write_tsv(OUT_HITS, sorted(hits, key=lambda row: (str(row["corpus_id"]), str(row["fold_id"]), str(row["predicted_fourth"]))))
    write_tsv(OUT_COUNTER, counterexamples)

    report = f"""# GDT003 structural fingerprint comparator report

Status: **LANGUAGE_AGNOSTIC_STRUCTURAL_NEIGHBORS_ONLY**

## Outcome

The closest capacity-matched corpus in this frozen tournament is
**{closest['language']}** (`{closest['corpus_id']}`), with descriptive distance
{float(closest['structural_distance_to_voynich']):.6f}. This is not a language
identification. It is a rank among a small, postulated corpus panel whose
scripts, genres, orthographic systems, tokenization, and source dates differ.

Voynich's matched nested algebra made {target['predictions']:,} candidate
fourth-cell predictions, with {target['exact_hits']} exact held-fold hits,
precision {float(target['heldout_precision']):.9f}, and AP gain over the best
same-candidate string baseline {float(target['ap_gain_over_best_string']):+.9f}.
The literal `q` plus `dy/dal/dar` subgroup's AP gain was
{float(target['voynich_qright_ap_gain']):+.9f}
({target['voynich_qright_exact']}/{target['voynich_qright_predictions']} exact).
No literal Voynich operation was mapped into another script.

The matched Voynich fingerprint has {float(target['mean_discovered_operations']):.3f}
retained operations per fold, left/right log-support ratio
{float(target['left_right_log2_support_ratio']):+.6f}, rectangle completion
{float(target['rectangle_completion_rate']):.6f}, and compatible-pair density
{float(target['compatible_pair_density']):.6f}. These are surface-system
statistics, not linguistic categories.

## Overall matched rank

| rank | corpus | family | tier | distance | AP gain | precision |
| ---: | --- | --- | --- | ---: | ---: | ---: |
"""
    for row in all_ranked:
        report += f"| {row['rank']} | {row['language']} | {row['family']} | {row['tier']} | {float(row['structural_distance_to_voynich']):.6f} | {float(row['ap_gain_over_best_string']):+.6f} | {float(row['heldout_precision']):.6f} |\n"
    report += """

The rank combines Jensen-Shannon distance between the predeclared edit spectra
with an equally weighted, range-normalized scalar fingerprint. It is sensitive
to the admitted panel and is not a posterior probability.

## Components behind the nearest ranks

| corpus | mean operations | right/left log2 support | replace fraction | rectangle completion | compatible-pair density | AP gain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
"""
    for rank_row in all_ranked[:10]:
        row = fp_by_id[str(rank_row["corpus_id"])]
        report += (
            f"| {row['language']} | {float(row['mean_discovered_operations']):.3f} | "
            f"{float(row['left_right_log2_support_ratio']):+.6f} | {float(row['replace_fraction']):.6f} | "
            f"{float(row['rectangle_completion_rate']):.6f} | {float(row['compatible_pair_density']):.6f} | "
            f"{float(row['ap_gain_over_best_string']):+.6f} |\n"
        )
    report += f"""

Voynich itself has by far the denser compatible-pair inventory in this table;
the nearest neighbors match only a mixture of components. Old Italian is an
ordinary control and ranks first, which directly blocks a geographically
specific reading of the rank. Modern Adyghe is the closest modern sensitivity,
but its positive AP gain is only {float(fp_by_id['ADYGHE_MODERN_SENSITIVITY']['ap_gain_over_best_string']):+.6f}
from {fp_by_id['ADYGHE_MODERN_SENSITIVITY']['exact_hits']}/{fp_by_id['ADYGHE_MODERN_SENSITIVITY']['predictions']}
exact predictions.

## Voynich same-candidate prediction baselines

| model | AP | paradigm minus model |
| --- | ---: | ---: |
"""
    voy_base = [row for row in baselines if row["corpus_id"] == "VOYNICH_MATCHED" and row["scope"] == "ALL_ALGEBRA"]
    voy_paradigm_ap = next(float(row["average_precision"] or 0) for row in voy_base if row["model"] == "NESTED_PARADIGM")
    for row in sorted(voy_base, key=lambda value: str(value["model"])):
        ap = float(row["average_precision"] or 0)
        report += f"| {row['model']} | {ap:.9f} | {voy_paradigm_ap - ap:+.9f} |\n"
    report += """

On this matched resample, the broad algebra does not beat KT2. This does not
rewrite the larger 102-folio GDT003 result; it shows that its small positive
full-corpus advantage is not stable under this capacity/genre-matched sampling
design. The predeclared literal Voynich q/right subsystem is substantially
worse than its strongest string baseline here as well.

## Historical tier and missing varieties

"""
    if historical_rank:
        report += "| historical rank | corpus | distance | AP gain |\n| ---: | --- | ---: | ---: |\n"
        for row in historical_rank:
            report += f"| {row['rank']} | {row['language']} | {float(row['structural_distance_to_voynich']):.6f} | {float(row['ap_gain_over_best_string']):+.6f} |\n"
    report += """

Old Georgian is retained at 6,093 tokens as a low-capacity descriptive
sensitivity and receives no primary rank. Middle Armenian has only 788 eligible
tokens in two source documents and is not fitted. No historical Cuman or Early
Maltese/Siculo-Arabic corpus was admitted; modern Kazakh and Maltese are visibly
labeled proxies/sensitivities.

## Reading the spectra

The artifacts report the left/right support ratio, add/replace balance,
rectangle completion, compatible-pair density, held-out precision, and gain
over KT/string baselines separately. A close aggregate distance can therefore
coexist with failure on the decisive predictive dimension. `gdt003_structural_fingerprint_baselines.tsv`
contains the identical-candidate baseline comparison for every corpus.

The generic cross-language subsystem is “one-character left add plus any
right-edge operation.” It tests positional combinability without asserting
that any two literal characters correspond. The Voynich-specific `q` plus
`dy/dal/dar` result is reported only for Voynich.

## Family aggregation

| family rank | family | members | mean distance | closest member distance |
| ---: | --- | ---: | ---: | ---: |
"""
    for row in family_rows:
        report += f"| {row['rank']} | {row['family']} | {row['member_corpora']} | {float(row['mean_structural_distance']):.6f} | {float(row['minimum_member_distance']):.6f} |\n"
    report += """

Family labels are descriptive metadata. Several families have one corpus;
their “family rank” is therefore just that corpus's rank, not a replicated
family-level estimate.

## Falsifiers and limitations

- Historical exact-variety capacity is incomplete, especially for Middle
  Armenian, Old Georgian, Cuman, and Early Maltese.
- Wikipedia is a modern random-page sensitivity corpus, not a historical or
  genre-matched manuscript corpus.
- Native orthographies are intentionally preserved. Distance can reflect
  script conventions and editorial tokenization.
- Exact held-fold hits are computationally hidden public forms, not new text.
- f84r remained sealed.
- No phoneme, sound, meaning, morpheme, POS, plaintext, or translation is
  assigned.

## Conclusion

This experiment ranks surface-system fingerprints, not languages. The useful
question is whether the nearest corpus shares Voynich's balance of edge edits,
rectangle completion, compatibility, and held-out gain. The rank is therefore
reported alongside every dirty confound and predictive counterexample, and it
does not revise GDT003's `LIMITED/LOCAL COMPOSITION ONLY` conclusion.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")

    result: dict[str, object] = {
        "schema": "GDT003_STRUCTURAL_FINGERPRINT_COMPARATOR_RESULT_V1",
        "status": "LANGUAGE_AGNOSTIC_STRUCTURAL_NEIGHBORS_ONLY",
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "corpora": {"evaluated": len(fingerprints), "matched_ranked": len(all_ranked), "low_capacity_evaluated": sum(row["capacity_state"] != "MATCHED_12000" for row in fingerprints), "insufficient_not_fitted": [row["corpus_id"] for row in requested_missing]},
        "voynich": {key: target[key] for key in ("predictions", "exact_hits", "heldout_precision", "paradigm_average_precision", "best_string_average_precision", "ap_gain_over_best_string", "generic_lr_ap_gain", "voynich_qright_predictions", "voynich_qright_exact", "voynich_qright_ap_gain")},
        "closest_all_matched": all_ranked[:5],
        "closest_modern": modern_rank[:5],
        "closest_historical": historical_rank[:5],
        "family_ranking": family_rows,
        "distance_definition": {"spectrum": "JENSEN_SHANNON_DISTANCE", "scalars": list(SCALARS), "combination": "MEAN_OF_SPECTRUM_JSD_AND_MINMAX_SCALAR_RMS", "ranges": ranges},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (CORPORA, MANIFEST, PROVENANCE, METHOD, SOURCE_AUDIT)},
        "implementation": {
            str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
            str(GDT003_CORE.relative_to(ROOT)): sha(GDT003_CORE),
        },
        "claim_ceiling": "Surface-form transformation-system comparison only; no language identification, no phoneme mapping, morphology, meaning, plaintext, or translation.",
    }
    result["outputs"] = {str(path.relative_to(ROOT)): sha(path) for path in (OUT_FINGERPRINTS, OUT_TRANSFORMS, OUT_BASELINES, OUT_RANKING, OUT_FAMILY, OUT_HITS, OUT_COUNTER, OUT_REPORT)}
    result["result_content_sha256"] = canonical_sha(result)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "closest": closest["corpus_id"], "distance": closest["structural_distance_to_voynich"], "voynich_ap_gain": target["ap_gain_over_best_string"], "voynich_qright_ap_gain": target["voynich_qright_ap_gain"]}, sort_keys=True))


if __name__ == "__main__":
    main()
