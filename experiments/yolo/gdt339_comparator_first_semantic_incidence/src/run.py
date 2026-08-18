#!/usr/bin/env python3
"""Apply the frozen GDT339 incidence instrument to opaque GDT327 tuples."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


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
METHOD = EXP / "METHOD.md"
DESIGN = ART / "gdt339_comparator_design.json"
FREEZE = ART / "gdt339_invariant_freeze.json"
COMPARATOR_RESULT = ART / "gdt339_comparator_result.json"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SOURCE_RESULT = ROOT / "gdt327_result.json"
PREDICTIONS = ART / "gdt339_voynich_tuple_folds.tsv"
FOLDS = ART / "gdt339_voynich_folio_scores.tsv"
REGISTERS = ART / "gdt339_voynich_register_scores.tsv"
MODELS = ART / "gdt339_voynich_model_scores.tsv"
NULL = ART / "gdt339_voynich_null.tsv"
COUNTER = ART / "gdt339_counterexamples.tsv"
RESULT = ART / "gdt339_result.json"
REPORT = EXP / "REPORT.md"


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def graph_features(reference: list[dict[str, str]], identities: list[str], bins: int) -> np.ndarray:
    records: dict[str, list[str]] = defaultdict(list)
    id_collections: dict[str, set[str]] = defaultdict(set)
    for unit in reference:
        records[unit["record"]].append(unit["identity"])
        id_collections[unit["identity"]].add(unit["collection"])
    counts = Counter(unit["identity"] for unit in reference)
    docs: dict[str, set[str]] = defaultdict(set)
    repeated_docs = Counter()
    degree_sum = Counter()
    degree_sq_sum = Counter()
    bin_counts: dict[str, Counter[int]] = defaultdict(Counter)
    record_counters = {record: Counter(values) for record, values in records.items()}
    for record, counter in record_counters.items():
        values = sorted(counter)
        degree = len(values)
        partner_bins = {
            ident: int(hashlib.sha256(("GDT339_PARTNER_BIN_V1\0" + ident).encode()).hexdigest()[:8], 16) % bins
            for ident in values
        }
        for ident in values:
            docs[ident].add(record)
            repeated_docs[ident] += int(counter[ident] > 1)
            degree_sum[ident] += degree
            degree_sq_sum[ident] += degree * degree
            for partner in values:
                if partner != ident:
                    bin_counts[ident][partner_bins[partner]] += 1
    record_partner_df_sum = {
        record: sum(len(docs[partner]) for partner in counter)
        for record, counter in record_counters.items()
    }
    total = max(1, len(reference))
    n_records = max(1, len(records))
    n_collections = max(1, len({unit["collection"] for unit in reference}))
    max_degree = max((len(counter) for counter in record_counters.values()), default=1)
    output = []
    for ident in identities:
        count = counts[ident]
        df = len(docs.get(ident, ()))
        mean_mult = count / max(1, df)
        mean_degree = degree_sum[ident] / max(1, df)
        variance = max(0.0, degree_sq_sum[ident] / max(1, df) - mean_degree * mean_degree)
        bc = bin_counts[ident]
        partner_total = sum(bc.values())
        entropy = 0.0
        for value in bc.values():
            p = value / max(1, partner_total)
            entropy -= p * math.log2(p) if p else 0.0
        partner_df_weight = sum(record_partner_df_sum[record] - df for record in docs.get(ident, ()))
        partner_weight = sum(max(0, len(record_counters[record]) - 1) for record in docs.get(ident, ()))
        output.append(
            [
                math.log1p(count) / math.log1p(total),
                df / n_records,
                math.log1p(mean_mult),
                math.log1p(mean_degree) / math.log1p(max_degree),
                repeated_docs[ident] / max(1, df),
                math.sqrt(variance) / max(1.0, mean_degree),
                len(bc) / bins,
                entropy / math.log2(bins),
                (max(bc.values()) / partner_total) if partner_total else 0.0,
                (partner_df_weight / max(1, partner_weight)) / n_records,
                len(id_collections.get(ident, ())) / n_collections,
            ]
        )
    return np.asarray(output, dtype=float)


def probabilities(X: np.ndarray, model: dict[str, object]) -> np.ndarray:
    indices = tuple(int(value) for value in model["feature_indices"])
    selected = X[:, indices]
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    Z = np.column_stack([np.ones(len(selected)), np.clip((selected - mean) / scale, -6, 6)])
    logits = Z @ beta
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=1, keepdims=True)


def frequency_bin(count: int) -> str:
    if count < 4:
        return "2_3"
    if count < 8:
        return "4_7"
    if count < 16:
        return "8_15"
    return "16_PLUS"


def binomial_bits(hits: int, trials: int, probability: float) -> float:
    p = min(max(probability, 1e-12), 1 - 1e-12)
    return -hits * math.log2(p) - (trials - hits) * math.log2(1 - p)


def aggregate_score(rows: list[dict[str, object]], model: str) -> float:
    return sum(binomial_bits(int(row["hits"]), int(row["trials"]), float(row[f"p_{model}"])) for row in rows)


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    comparator = json.loads(COMPARATOR_RESULT.read_text(encoding="utf-8"))
    guard = GuardedTSV(SOURCE, selector_column="page", forbidden_action="error")
    source_rows = list(guard)
    if len(source_rows) != 8448 or guard.stats.skipped_forbidden:
        raise AssertionError((len(source_rows), guard.stats))
    if any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source_rows):
        raise AssertionError("f84 entered GDT339")
    units = [
        {
            "collection": row["physical_folio"],
            "folio": row["physical_folio"],
            "register": row["register"],
            "record": f"{row['page']}|{row['record_ordinal']}",
            "identity": row["joint_tuple_id"],
            "field": f"{row['locus']}|{row['field_ordinal']}",
        }
        for row in source_rows
    ]
    by_record: dict[str, set[str]] = defaultdict(set)
    record_folio: dict[str, str] = {}
    counts_by_tuple_folio = Counter()
    records_by_tuple_folio: dict[tuple[str, str], set[str]] = defaultdict(set)
    register_by_tuple_folio: dict[tuple[str, str], str] = {}
    for unit in units:
        by_record[unit["record"]].add(unit["identity"])
        record_folio[unit["record"]] = unit["folio"]
        key = (unit["identity"], unit["folio"])
        counts_by_tuple_folio[key] += 1
        records_by_tuple_folio[key].add(unit["record"])
        register_by_tuple_folio[key] = unit["register"]
    partners_by_tuple_folio: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record, identities in by_record.items():
        folio = record_folio[record]
        for ident in identities:
            partners_by_tuple_folio[(ident, folio)].update(identities - {ident})
    folios_by_tuple: dict[str, set[str]] = defaultdict(set)
    for ident, folio in counts_by_tuple_folio:
        folios_by_tuple[ident].add(folio)
    all_folios = sorted({unit["folio"] for unit in units})
    frozen_models = freeze["selected"]["frozen_candidate_models"]
    selected_model = freeze["selected"]["selected_model"]
    bins = int(design["partner_hash_bins"])
    shrink = float(design["voynich_scoring"]["class_shrinkage_trials"])
    alpha = float(design["voynich_scoring"]["jeffreys_alpha"])
    predictions: list[dict[str, object]] = []
    fold_training_examples: dict[str, list[dict[str, object]]] = {}
    fold_class_maps: dict[str, dict[str, str]] = {}
    for held in all_folios:
        training = [unit for unit in units if unit["folio"] != held]
        training_counts = Counter(unit["identity"] for unit in training)
        eligible = sorted(
            ident
            for ident in folios_by_tuple
            if held in folios_by_tuple[ident]
            and len(folios_by_tuple[ident] - {held}) >= 2
            and len(records_by_tuple_folio[(ident, held)]) >= 2
            and partners_by_tuple_folio[(ident, held)]
        )
        if not eligible:
            continue
        features = graph_features(training, eligible, bins)
        model_probs = {
            model: probabilities(features, frozen_models[model]) for model in frozen_models
        }
        class_map = {
            ident: f"C{int(np.argmax(model_probs[selected_model][index]))}"
            for index, ident in enumerate(eligible)
        }
        # Classes for every sufficiently recurrent training tuple calibrate the
        # class-conditioned incidence table; held outcomes never enter.
        recurrent_training = sorted(
            ident for ident, fs in folios_by_tuple.items() if len(fs - {held}) >= 2
        )
        train_features = graph_features(training, recurrent_training, bins)
        train_selected = probabilities(train_features, frozen_models[selected_model])
        train_class = {
            ident: f"C{int(np.argmax(train_selected[index]))}"
            for index, ident in enumerate(recurrent_training)
        }
        training_examples = []
        for pseudo in all_folios:
            if pseudo == held:
                continue
            for ident in recurrent_training:
                partners = partners_by_tuple_folio.get((ident, pseudo), set())
                if not partners:
                    continue
                rest_folios = (folios_by_tuple[ident] - {held, pseudo})
                if not rest_folios:
                    continue
                reference_partners = set().union(
                    *(partners_by_tuple_folio[(ident, folio)] for folio in rest_folios)
                )
                ref_count = sum(counts_by_tuple_folio[(ident, folio)] for folio in rest_folios)
                training_examples.append(
                    {
                        "register": register_by_tuple_folio[(ident, pseudo)],
                        "bin": frequency_bin(ref_count),
                        "class": train_class[ident],
                        "identity": ident,
                        "hits": len(partners & reference_partners),
                        "trials": len(partners),
                    }
                )
        fold_training_examples[held] = training_examples
        fold_class_maps[held] = class_map
        base_counts = Counter()
        class_counts = Counter()
        exact_counts = Counter()
        global_counts = Counter()
        for example in training_examples:
            base_key = (example["register"], example["bin"])
            class_key = (*base_key, example["class"])
            exact_key = (*base_key, example["identity"])
            base_counts[(*base_key, "hits")] += int(example["hits"])
            base_counts[(*base_key, "trials")] += int(example["trials"])
            class_counts[(*class_key, "hits")] += int(example["hits"])
            class_counts[(*class_key, "trials")] += int(example["trials"])
            exact_counts[(*exact_key, "hits")] += int(example["hits"])
            exact_counts[(*exact_key, "trials")] += int(example["trials"])
            global_counts[(example["register"], "hits")] += int(example["hits"])
            global_counts[(example["register"], "trials")] += int(example["trials"])
        for index, ident in enumerate(eligible):
            register = register_by_tuple_folio[(ident, held)]
            fbin = frequency_bin(training_counts[ident])
            base_key = (register, fbin)
            gh = global_counts[(register, "hits")]
            gt = global_counts[(register, "trials")]
            global_p = (gh + alpha) / (gt + 2 * alpha)
            bh = base_counts[(*base_key, "hits")]
            bt = base_counts[(*base_key, "trials")]
            base_p = (bh + 4 * global_p) / (bt + 4)
            ckey = (*base_key, class_map[ident])
            ch = class_counts[(*ckey, "hits")]
            ct = class_counts[(*ckey, "trials")]
            class_p = (ch + shrink * base_p) / (ct + shrink)
            ekey = (*base_key, ident)
            eh = exact_counts[(*ekey, "hits")]
            et = exact_counts[(*ekey, "trials")]
            exact_p = (eh + shrink * base_p) / (et + shrink)
            held_partners = partners_by_tuple_folio[(ident, held)]
            training_partners = set().union(
                *(partners_by_tuple_folio[(ident, folio)] for folio in folios_by_tuple[ident] - {held})
            )
            predictions.append(
                {
                    "held_folio": held,
                    "register": register,
                    "joint_tuple_id": ident,
                    "training_occurrences": training_counts[ident],
                    "training_frequency_bin": fbin,
                    "training_folios": len(folios_by_tuple[ident] - {held}),
                    "held_records": len(records_by_tuple_folio[(ident, held)]),
                    "anonymous_class": class_map[ident],
                    "anonymous_class_probability": f"{max(model_probs[selected_model][index]):.12f}",
                    "hits": len(held_partners & training_partners),
                    "trials": len(held_partners),
                    "p_register_frequency": f"{base_p:.12f}",
                    "p_comparator_class": f"{class_p:.12f}",
                    "p_exact_tuple": f"{exact_p:.12f}",
                    "semantic_state": "UNASSIGNED",
                    "translation_state": "UNASSIGNED",
                }
            )
    if not predictions:
        raise AssertionError("no GDT339 held-folio capacity")
    write_tsv(PREDICTIONS, predictions)

    model_names = ("register_frequency", "comparator_class", "exact_tuple")
    model_bits = {model: aggregate_score(predictions, model) for model in model_names}
    model_rows = [
        {
            "model": model,
            "tuple_fold_tests": len(predictions),
            "partner_trials": sum(int(row["trials"]) for row in predictions),
            "held_bits": f"{model_bits[model]:.12f}",
            "gain_vs_register_frequency_bits": f"{model_bits['register_frequency'] - model_bits[model]:.12f}",
            "selection_eligible": "YES" if model == "comparator_class" else "NO",
        }
        for model in model_names
    ]
    write_tsv(MODELS, model_rows)

    def grouped_scores(key: str) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in predictions:
            grouped[str(row[key])].append(row)
        output = []
        for value, members in sorted(grouped.items()):
            base = aggregate_score(members, "register_frequency")
            candidate = aggregate_score(members, "comparator_class")
            exact = aggregate_score(members, "exact_tuple")
            output.append(
                {
                    "stratum_type": key,
                    "stratum": value,
                    "tuple_fold_tests": len(members),
                    "partner_trials": sum(int(row["trials"]) for row in members),
                    "register_frequency_bits": f"{base:.12f}",
                    "comparator_class_bits": f"{candidate:.12f}",
                    "class_gain_bits": f"{base - candidate:.12f}",
                    "exact_tuple_bits": f"{exact:.12f}",
                    "exact_tuple_gain_bits": f"{base - exact:.12f}",
                }
            )
        return output

    folio_rows = grouped_scores("held_folio")
    register_rows = grouped_scores("register")
    write_tsv(FOLDS, folio_rows)
    write_tsv(REGISTERS, register_rows)
    observed_gain = model_bits["register_frequency"] - model_bits["comparator_class"]
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(predictions):
        groups[(str(row["register"]), str(row["training_frequency_bin"]))].append(index)
    null_rows = []
    exceed = 0
    for world in range(int(design["voynich_scoring"]["null_worlds"])):
        rng = random.Random(int(design["voynich_scoring"]["null_seed"]) * 1_000_003 + world)
        probabilities_perm = [float(row["p_comparator_class"]) for row in predictions]
        for indices in groups.values():
            values = [probabilities_perm[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                probabilities_perm[index] = value
        null_bits = sum(
            binomial_bits(int(row["hits"]), int(row["trials"]), probabilities_perm[index])
            for index, row in enumerate(predictions)
        )
        gain = model_bits["register_frequency"] - null_bits
        exceed += int(gain >= observed_gain - 1e-12)
        null_rows.append({"world": world, "permuted_class_gain_bits": f"{gain:.12f}"})
    write_tsv(NULL, null_rows)
    p_value = (exceed + 1) / (len(null_rows) + 1)
    positive_folios = sum(float(row["class_gain_bits"]) > 0 for row in folio_rows)
    counts = {
        "tuple_fold_tests": len(predictions),
        "partner_trials": sum(int(row["trials"]) for row in predictions),
        "physical_folios": len(folio_rows),
        "registers": len(register_rows),
        "exact_tuples": len({row["joint_tuple_id"] for row in predictions}),
    }
    gates = design["voynich_capacity_gates"]
    capacity_pass = (
        counts["tuple_fold_tests"] >= int(gates["tuple_fold_tests_min"])
        and counts["physical_folios"] >= int(gates["physical_folios_min"])
        and counts["registers"] >= int(gates["registers_min"])
    )
    voynich_pass = (
        capacity_pass
        and observed_gain - float(design["voynich_scoring"]["model_selector_bits"]) > 0
        and positive_folios / counts["physical_folios"] >= float(gates["positive_folio_fraction_min"])
        and p_value <= float(gates["max_family_p_max"])
    )
    comparator_pass = freeze["status"] == "COMPARATOR_INVARIANT_SUPPORTED_AND_FROZEN"
    if not comparator_pass:
        status = "NO_TRANSFERABLE_COMPARATOR_INVARIANT"
    elif voynich_pass:
        status = "ANONYMOUS_INCIDENCE_CLASS_STABILITY_PROVISIONAL"
    else:
        status = "COMPARATOR_INVARIANT_VOYNICH_STABILITY_NOT_SUPPORTED"
    counter_rows = [
        {"id": "C01_COMPARATOR_FAILURE", "finding": f"Comparator status is {freeze['status']}; only 3/10 held collections/books were positive.", "impact": "No Voynich class can inherit semantic force regardless of its structural diagnostic."},
        {"id": "C02_OPAQUE_ID_CEILING", "finding": "Exact opaque-ID lookup was strong in CoReMA but failed badly across Nuremberg books.", "impact": "Semantic identity reuse is corpus-specific and not a universal incidence invariant."},
        {"id": "C03_CLASS_CALIBRATION", "finding": "Voynich class-cell rates are calibrated on non-held Voynich folds after the comparator mapping is frozen.", "impact": "Only the class mapping transfers cross-corpus; incidence rate magnitude is corpus-calibrated."},
        {"id": "C04_NO_TUPLE_MERGE", "finding": "Class labels C0..C4 annotate but never merge exact joint_tuple_id values.", "impact": "A shared anonymous class is not an equivalence, word, role or meaning."},
        {"id": "C05_NO_LOCAL_ORDER", "finding": "All partner sets are unordered within record hyperedges.", "impact": "The test cannot recover syntax or sequential dependence."},
        {"id": "C06_F84_SEALED", "finding": "Guarded input contained zero retained or skipped f84 rows.", "impact": "No f84 payload entered selection, fitting, scoring or output."},
    ]
    write_tsv(COUNTER, counter_rows)
    report = f"""# GDT339 comparator-first semantic incidence report

Status: **{status}**.

## Comparator freeze

The readable-control stage selected `{selected_model}` but failed its transfer gates: it was positive in only {freeze['comparator_evidence']['positive_folds']}/10 held collections/books, positive on CoReMA but negative on Nuremberg, with task-relative gains over frequency of {freeze['comparator_evidence']['gain_over_frequency_by_task']['COREMA']:+.3f} and {freeze['comparator_evidence']['gain_over_frequency_by_task']['NUREMBERG']:+.3f} bits. The invariant was frozen and published before this Voynich application, but its status is `NO_TRANSFERABLE_COMPARATOR_INVARIANT`.

## Held-folio Voynich diagnostic

The unchanged anonymous class mapping covers {counts['tuple_fold_tests']} tuple-fold tests / {counts['partner_trials']} held partner trials on {counts['physical_folios']} physical folios, {counts['exact_tuples']} exact tuples and {counts['registers']} registers. It changes held partner-incidence codelength by {observed_gain:+.3f} bits relative to register×frequency ({observed_gain - float(design['voynich_scoring']['model_selector_bits']):+.3f} after the fixed one-bit selector), is positive on {positive_folios}/{counts['physical_folios']} folio folds, and has frequency-matched permutation p={p_value:.6f}. Exact-tuple lookup changes codelength by {model_bits['register_frequency'] - model_bits['exact_tuple']:+.3f} bits and is a namespace-specific strong control.

The Voynich numbers are anonymous structural diagnostics only. Because the comparator invariant failed before Voynich scoring, no positive diagnostic could license a semantic class.

## Decision

Retain exact GDT327 tuples and stop this comparator-incidence route. No tuple is merged or assigned a semantic role, gloss, word, sound, language, plaintext or translation.

f84 was not opened, parsed, retained, joined or scored.
"""
    REPORT.write_text(report, encoding="utf-8")
    scientific_inputs = (METHOD, DESIGN, FREEZE, COMPARATOR_RESULT, SOURCE, SOURCE_RESULT)
    outputs = (PREDICTIONS, FOLDS, REGISTERS, MODELS, NULL, COUNTER)
    result = {
        "schema": "GDT339_RESULT_V1",
        "status": status,
        "comparator_status": freeze["status"],
        "selected_invariant": selected_model,
        "counts": counts,
        "voynich": {
            "raw_gain_bits": observed_gain,
            "selector_paid_gain_bits": observed_gain - float(design["voynich_scoring"]["model_selector_bits"]),
            "positive_folios": positive_folios,
            "permutation_p": p_value,
            "exact_tuple_gain_bits": model_bits["register_frequency"] - model_bits["exact_tuple"],
        },
        "gates": {"comparator": comparator_pass, "capacity": capacity_pass, "voynich": voynich_pass},
        "semantic_assignments": 0,
        "translation_assignments": 0,
        "tuple_merges": 0,
        "source_access": {"f84_opened_parsed_retained_joined_or_scored": False, "page_host_used": False, "local_sequence_used": False, "visual_or_external_semantics_joined_to_voynich": False},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in scientific_inputs},
        "documents": {str(REPORT.relative_to(ROOT)): sha256_file(REPORT)},
        "implementation": {str(Path(__file__).resolve().relative_to(ROOT)): sha256_file(Path(__file__).resolve())},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in outputs},
        "claim_ceiling": "Anonymous held-folio incidence stability of exact opaque tuples only; no merge, role, meaning, language, plaintext or translation.",
    }
    result["content_sha256"] = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    RESULT.write_bytes(canonical_json_bytes(result))
    print(json.dumps({"status": status, "counts": counts, "voynich": result["voynich"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
