#!/usr/bin/env python3
"""GDT163: held-base one-character substitution context transfer."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import random
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
CONTROL_SOURCE = ROOT / "gdt159_diplomatic_corpora.json.gz"
CONTROL_MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
DESIGN = ROOT / "gdt163_design.json"
METHOD = ROOT / "GDT163_SUBSTITUTION_CONTEXT_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT163_SUBSTITUTION_CONTEXT_TRANSFER_REPORT.md"
INVENTORY = ROOT / "gdt163_substitution_inventory.tsv"
HPR_PRED = ROOT / "gdt163_hpr2_predictions.tsv"
GENERIC_PRED = ROOT / "gdt163_generic_predictions.tsv"
OP_SCORES = ROOT / "gdt163_operation_scores.tsv"
COMPARATORS = ROOT / "gdt163_comparator_scores.tsv"
NULLS = ROOT / "gdt163_null_results.tsv"
COUNTER = ROOT / "gdt163_counterexamples.tsv"
VARIANTS = ROOT / "gdt163_variant_log.tsv"
RESULT = ROOT / "gdt163_result.json"

LENGTHS = (2, 3)
COMPONENTS = ("wrapper", "inner_d", "local_frame", "right_family", "dy_closure", "b3")
WORLDS = 1024
MIN_COUNT = 2
MIN_CASES = 4
MIN_TRAIN_CASES = 3
MIN_TRAIN_BASES = 2
MAX_WEIGHT = 20.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def write(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def read_source() -> tuple[list[dict[str, str]], int]:
    rows = []; rejected = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84") or row["locus"].startswith("f84"):
                rejected += 1; continue
            assert not row["page"].startswith("f84r") and not row["locus"].startswith("f84r")
            rows.append(row)
    assert len(rows) == 15364 and rejected == 228
    return rows, rejected


def length_bin(value: str | None) -> str:
    if value is None: return "MISSING"
    n = len(value)
    return "L1" if n == 1 else "L2" if n == 2 else "L3" if n == 3 else "L4P"


def edge_list(mapping: dict[str, str]) -> list[dict[str, object]]:
    buckets: dict[tuple[int, int, str], list[str]] = defaultdict(list)
    for ident, word in mapping.items():
        if len(word) not in LENGTHS: continue
        for pos in range(len(word)):
            buckets[len(word), pos, word[:pos] + "*" + word[pos + 1 :]].append(ident)
    seen = set(); out = []
    for (length, pos, base), ids in buckets.items():
        for i, left in enumerate(ids):
            for right in ids[i + 1 :]:
                a, b = mapping[left], mapping[right]
                if a == b or sum(x != y for x, y in zip(a, b)) != 1: continue
                key = tuple(sorted((left, right)))
                if key in seen: continue
                seen.add(key)
                if a[pos] < b[pos]: source, target, sg, tg = left, right, a[pos], b[pos]
                else: source, target, sg, tg = right, left, b[pos], a[pos]
                out.append({"source": source, "target": target, "length": length, "position": pos + 1,
                            "source_glyph": sg, "target_glyph": tg,
                            "operation": f"L{length}:P{pos + 1}:{sg}>{tg}", "base_family": f"L{length}:P{pos + 1}:{base}"})
    return sorted(out, key=lambda x: (str(x["operation"]), str(x["base_family"]), str(x["source"]), str(x["target"])))


def random_position_mapping(labels: dict[str, str], rng: random.Random) -> dict[str, str]:
    out = {ident: [""] * len(word) for ident, word in labels.items()}
    for length in LENGTHS:
        ids = sorted(ident for ident, word in labels.items() if len(word) == length)
        for pos in range(length):
            chars = [labels[ident][pos] for ident in ids]; rng.shuffle(chars)
            for ident, ch in zip(ids, chars): out[ident][pos] = ch
    return {ident: "".join(chars) for ident, chars in out.items()}


def vector_layout(block_values: dict[str, list[str]]) -> tuple[list[tuple[str, str]], dict[str, int]]:
    dims = [(block, value) for block in block_values for value in block_values[block]]
    return dims, {block: len(values) for block, values in block_values.items()}


def smoothed_vectors(occurrences: list[dict[str, str]], identity_key: str, cell_keys: tuple[str, ...], blocks: tuple[str, ...], block_values: dict[str, list[str]]) -> tuple[dict[tuple[str, ...], np.ndarray], Counter[tuple[str, ...]], list[str]]:
    dims, sizes = vector_layout(block_values); counts = Counter(); cells = Counter()
    for row in occurrences:
        key = (row[identity_key],) + tuple(row[k] for k in cell_keys)
        cells[key] += 1
        for block in blocks: counts[key, block, row[block]] += 1
    vectors = {}
    for key, n in cells.items():
        vectors[key] = np.array([(counts[key, block, value] + 0.5) / (n + 0.5 * sizes[block]) for block, value in dims], dtype=float)
    return vectors, cells, [f"{a}={b}" for a, b in dims]


def hpr_cases(mapping: dict[str, str], vectors: dict[tuple[str, ...], np.ndarray], cell_counts: Counter[tuple[str, ...]]) -> list[dict[str, object]]:
    by_identity = defaultdict(set)
    for key in vectors: by_identity[key[0]].add((key[1], key[2]))
    cases = []
    for edge in edge_list(mapping):
        source, target = str(edge["source"]), str(edge["target"])
        for section, hand in sorted(by_identity[source] & by_identity[target]):
            ks = (source, section, hand); kt = (target, section, hand)
            ns, nt = cell_counts[ks], cell_counts[kt]
            if ns < MIN_COUNT or nt < MIN_COUNT: continue
            cases.append({**edge, "section": section, "hand": hand, "source_count": ns, "target_count": nt,
                          "weight": min(MAX_WEIGHT, float(min(ns, nt))), "delta": vectors[kt] - vectors[ks]})
    return cases


def generic_cases(mapping: dict[str, str], vectors: dict[tuple[str, ...], np.ndarray], cell_counts: Counter[tuple[str, ...]]) -> list[dict[str, object]]:
    cases = []
    for edge in edge_list(mapping):
        source, target = str(edge["source"]), str(edge["target"]); ks, kt = (source,), (target,)
        ns, nt = cell_counts[ks], cell_counts[kt]
        if ns < MIN_COUNT or nt < MIN_COUNT: continue
        cases.append({**edge, "section": "ALL", "hand": "ALL", "source_count": ns, "target_count": nt,
                      "weight": min(MAX_WEIGHT, float(min(ns, nt))), "delta": vectors[kt] - vectors[ks]})
    return cases


def weighted_mean(cases: list[dict[str, object]]) -> np.ndarray:
    weights = np.array([float(c["weight"]) for c in cases]); matrix = np.stack([c["delta"] for c in cases])
    return np.average(matrix, axis=0, weights=weights)


def prediction_stats(rows: list[dict[str, object]]) -> dict[str, float]:
    if not rows: return {"predictions": 0, "weight": 0.0, "fractional_mse_gain": 0.0, "mean_cosine": 0.0, "positive_dot_rate": 0.0}
    total_w = sum(float(r["weight"]) for r in rows); zero = sum(float(r["weight"]) * float(r["zero_sse"]) for r in rows); err = sum(float(r["weight"]) * float(r["pred_sse"]) for r in rows)
    return {"predictions": len(rows), "weight": total_w, "fractional_mse_gain": 1 - err / zero if zero else 0.0,
            "mean_cosine": sum(float(r["weight"]) * float(r["cosine"]) for r in rows) / total_w,
            "positive_dot_rate": sum(float(r["weight"]) * (float(r["dot"]) > 0) for r in rows) / total_w}


def make_prediction(test: dict[str, object], pred: np.ndarray, model: str, mode: str) -> dict[str, object]:
    actual = test["delta"]; assert isinstance(actual, np.ndarray)
    na = float(np.linalg.norm(actual)); npred = float(np.linalg.norm(pred)); dot = float(actual @ pred)
    return {"mode": mode, "model": model, "operation": test["operation"], "base_family": test["base_family"], "source_host": test["source"], "target_host": test["target"],
            "section": test["section"], "hand": test["hand"], "source_count": test["source_count"], "target_count": test["target_count"], "weight": test["weight"],
            "zero_sse": float(actual @ actual), "pred_sse": float((actual - pred) @ (actual - pred)), "dot": dot,
            "cosine": dot / (na * npred) if na and npred else 0.0, "actual_norm": na, "predicted_norm": npred,
            "claim_state": "HELD_FORMAL_DELTA_NO_MORPHOLOGY_OR_MEANING"}


def predict_cases(cases: list[dict[str, object]], mode: str, include_exact: bool) -> list[dict[str, object]]:
    by_op = defaultdict(list); by_pos = defaultdict(list); by_base = defaultdict(list)
    for case in cases:
        by_op[case["operation"]].append(case); by_pos[case["length"], case["position"]].append(case); by_base[case["base_family"]].append(case)
    out = []
    for test in cases:
        def allowed(row: dict[str, object]) -> bool:
            if mode == "HELD_BASE_AND_SECTION" and row["section"] == test["section"]: return False
            if mode == "HELD_BASE_AND_HAND" and row["hand"] == test["hand"]: return False
            return True
        train = [r for r in by_op[test["operation"]] if r["base_family"] != test["base_family"] and allowed(r)]
        if len(train) >= MIN_TRAIN_CASES and len({r["base_family"] for r in train}) >= MIN_TRAIN_BASES:
            out.append(make_prediction(test, weighted_mean(train), "OP_SUBSTITUTION", mode))
        position = [r for r in by_pos[test["length"], test["position"]] if r["operation"] != test["operation"] and r["base_family"] != test["base_family"] and allowed(r)]
        if len(position) >= MIN_TRAIN_CASES and len({r["base_family"] for r in position}) >= MIN_TRAIN_BASES:
            out.append(make_prediction(test, weighted_mean(position), "POSITION_ONLY", mode))
        if include_exact:
            exact = [r for r in by_base[test["base_family"]] if r is not test and allowed(r)]
            if exact: out.append(make_prediction(test, weighted_mean(exact), "EXACT_PAIR_OTHER_STRATA", mode))
    return out


def fast_primary(cases: list[dict[str, object]]) -> tuple[dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    """Primary held-base op and position scores, used for every null world."""
    by_op = defaultdict(list); by_pos = defaultdict(list)
    for case in cases: by_op[case["operation"]].append(case); by_pos[case["length"], case["position"]].append(case)
    op_rows = []; position_rows = []; per_op = {}
    for operation, group in by_op.items():
        if len(group) < MIN_CASES: continue
        local = []
        for test in group:
            train = [r for r in group if r["base_family"] != test["base_family"]]
            if len(train) >= MIN_TRAIN_CASES and len({r["base_family"] for r in train}) >= MIN_TRAIN_BASES:
                row = make_prediction(test, weighted_mean(train), "OP_SUBSTITUTION", "HELD_BASE"); op_rows.append(row); local.append(row)
        if local: per_op[operation] = prediction_stats(local)
    for test in cases:
        train = [r for r in by_pos[test["length"], test["position"]] if r["operation"] != test["operation"] and r["base_family"] != test["base_family"]]
        if len(train) >= MIN_TRAIN_CASES and len({r["base_family"] for r in train}) >= MIN_TRAIN_BASES:
            position_rows.append(make_prediction(test, weighted_mean(train), "POSITION_ONLY", "HELD_BASE"))
    return prediction_stats(op_rows), prediction_stats(position_rows), per_op


def generic_occurrences_voynich(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_unit = defaultdict(dict)
    for row in rows: by_unit[row["locus"]][int(row["group_index"])] = row
    out = []
    for unit, index in by_unit.items():
        lo, hi = min(index), max(index)
        for pos, row in index.items():
            if len(row["page_host"]) not in LENGTHS: continue
            quartile = int(4 * (pos - lo) / max(1, hi - lo)); quartile = min(3, quartile)
            out.append({"identity": row["page_host"], "prev_len": length_bin(index[pos - 1]["page_host"] if pos - 1 in index else None),
                        "next_len": length_bin(index[pos + 1]["page_host"] if pos + 1 in index else None), "unit_quartile": f"Q{quartile}"})
    return out


def generic_occurrences_control(records: list[dict[str, object]]) -> list[dict[str, str]]:
    by_unit = defaultdict(dict)
    for row in records: by_unit[str(row["unit_id"])][int(row["occurrence_index"])] = unicodedata.normalize("NFC", str(row["form"]))
    out = []
    for unit, index in by_unit.items():
        lo, hi = min(index), max(index)
        for pos, form in index.items():
            if len(form) not in LENGTHS: continue
            quartile = int(4 * (pos - lo) / max(1, hi - lo)); quartile = min(3, quartile)
            out.append({"identity": form, "prev_len": length_bin(index.get(pos - 1)), "next_len": length_bin(index.get(pos + 1)), "unit_quartile": f"Q{quartile}"})
    return out


def null_worlds(corpus_id: str, labels: dict[str, str], case_builder, vectors, counts, observed_gain: float, observed_top: float) -> tuple[list[dict[str, object]], dict[str, float]]:
    rng = random.Random(seed("GDT163_NULL_" + corpus_id)); rows = []; agg = []; tops = []
    for world in range(WORLDS):
        mapping = random_position_mapping(labels, rng); cases = case_builder(mapping, vectors, counts); score, position, per_op = fast_primary(cases)
        top = max((x["fractional_mse_gain"] for x in per_op.values()), default=0.0)
        row = {"corpus_id": corpus_id, "world": world, "eligible_cases": len(cases), "op_predictions": int(score["predictions"]),
               "op_fractional_mse_gain": score["fractional_mse_gain"], "position_fractional_mse_gain": position["fractional_mse_gain"],
               "top_operation_fractional_mse_gain": top, "collisions": len(mapping) - len(set(mapping.values()))}
        rows.append(row); agg.append(float(score["fractional_mse_gain"])); tops.append(float(top))
    return rows, {"aggregate_local_p": (1 + sum(x >= observed_gain - 1e-12 for x in agg)) / (WORLDS + 1),
                  "top_operation_maxT_p": (1 + sum(x >= observed_top - 1e-12 for x in tops)) / (WORLDS + 1),
                  "null_aggregate_mean": sum(agg) / WORLDS, "null_top_mean": sum(tops) / WORLDS}


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8")); assert design["status"] == "FROZEN_BEFORE_SCORING" and design["null_worlds"] == WORLDS
    source, rejected = read_source(); candidate = [r for r in source if len(r["page_host"]) in LENGTHS]
    hpr_values = {component: sorted({r[component] for r in candidate}) for component in COMPONENTS}
    hpr_vectors, hpr_counts, hpr_dims = smoothed_vectors(candidate, "page_host", ("section", "hand"), COMPONENTS, hpr_values)
    host_labels = {r["page_host"]: r["page_host"] for r in candidate}
    hcases = hpr_cases(host_labels, hpr_vectors, hpr_counts)
    assert len(host_labels) == 241 and len(edge_list(host_labels)) == 933 and len(hcases) == 660

    # Full HPR2 predictions and summaries.
    hpred = []
    for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND"): hpred += predict_cases(hcases, mode, True)
    hsummary = {}
    for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND"):
        for model in ("OP_SUBSTITUTION", "POSITION_ONLY", "EXACT_PAIR_OTHER_STRATA"):
            hsummary[mode, model] = prediction_stats([r for r in hpred if r["mode"] == mode and r["model"] == model])
    primary, primary_position, per_op = fast_primary(hcases)

    # Operation inventory and cross-mode operation scores.
    op_cases = defaultdict(list)
    for case in hcases: op_cases[case["operation"]].append(case)
    inventory = []
    for op, cases in sorted(op_cases.items()):
        first = cases[0]
        inventory.append({"operation": op, "length": first["length"], "position": first["position"], "source_glyph": first["source_glyph"], "target_glyph": first["target_glyph"],
                          "eligible_cells": len(cases), "base_families": len({c["base_family"] for c in cases}), "sections": "|".join(sorted({str(c["section"]) for c in cases})),
                          "hands": "|".join(sorted({str(c["hand"]) for c in cases})), "retained_for_transfer": int(len(cases) >= MIN_CASES),
                          "claim_state": "DIRECTED_ONE_CHARACTER_FORMAL_RELATION_NO_MORPHOLOGY_OR_MEANING"})
    op_scores = []
    for op in sorted(per_op):
        row = {"operation": op, "eligible_cells": len(op_cases[op]), "base_families": len({c["base_family"] for c in op_cases[op]}),
               "sections": len({str(c["section"]) for c in op_cases[op]}), "hands": len({str(c["hand"]) for c in op_cases[op]})}
        for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND"):
            stats = prediction_stats([r for r in hpred if r["model"] == "OP_SUBSTITUTION" and r["mode"] == mode and r["operation"] == op])
            for key, value in stats.items(): row[f"{mode.lower()}_{key}"] = value
        op_scores.append(row)

    # Generic local-sequence channel applied identically to VMS and controls.
    generic_values = {"prev_len": ["MISSING", "L1", "L2", "L3", "L4P"], "next_len": ["MISSING", "L1", "L2", "L3", "L4P"], "unit_quartile": ["Q0", "Q1", "Q2", "Q3"]}
    generic_blocks = ("prev_len", "next_len", "unit_quartile")
    generic_payloads = {"VOYNICH_PAGE_HOST": generic_occurrences_voynich(source)}
    with gzip.open(CONTROL_SOURCE, "rt", encoding="utf-8") as handle: external = json.load(handle)["records"]
    by_corpus = defaultdict(list)
    for row in external: by_corpus[str(row["corpus_id"])].append(row)
    for corpus_id, records in by_corpus.items(): generic_payloads[corpus_id] = generic_occurrences_control(records)

    comparator_rows = []; generic_predictions = []; all_nulls = []
    generic_objects = {}
    for corpus_id, occurrences in sorted(generic_payloads.items()):
        vectors, counts, dims = smoothed_vectors(occurrences, "identity", (), generic_blocks, generic_values)
        labels = {r["identity"]: r["identity"] for r in occurrences if len(r["identity"]) in LENGTHS}
        cases = generic_cases(labels, vectors, counts); score, position, pop = fast_primary(cases)
        predictions = predict_cases(cases, "HELD_BASE", False)
        for row in predictions: row["corpus_id"] = corpus_id
        generic_predictions += predictions
        top = max((x["fractional_mse_gain"] for x in pop.values()), default=0.0)
        null_rows, null_summary = null_worlds(corpus_id, labels, generic_cases, vectors, counts, float(score["fractional_mse_gain"]), float(top))
        all_nulls += null_rows
        comparator_rows.append({"corpus_id": corpus_id, "occurrences": len(occurrences), "types": len(labels), "hamming1_edges": len(edge_list(labels)), "eligible_cases": len(cases),
                                "op_predictions": int(score["predictions"]), "op_fractional_mse_gain": score["fractional_mse_gain"], "op_mean_cosine": score["mean_cosine"],
                                "op_positive_dot_rate": score["positive_dot_rate"], "position_fractional_mse_gain": position["fractional_mse_gain"],
                                "increment_over_position": float(score["fractional_mse_gain"]) - float(position["fractional_mse_gain"]), "best_operation_gain": top,
                                "null_local_p": null_summary["aggregate_local_p"], "best_operation_maxT_p": null_summary["top_operation_maxT_p"],
                                "null_mean_gain": null_summary["null_aggregate_mean"], "capacity_state": "POWERED" if int(score["predictions"]) >= 100 else "LOW_CAPACITY"})
        generic_objects[corpus_id] = (labels, cases, score, position, pop, null_summary)

    # HPR2 null after generic worlds so every family remains independently seeded.
    htop = max((x["fractional_mse_gain"] for x in per_op.values()), default=0.0)
    hnull_rows, hnull_summary = null_worlds("VOYNICH_HPR2_OUTER", host_labels, hpr_cases, hpr_vectors, hpr_counts, float(primary["fractional_mse_gain"]), float(htop))
    all_nulls += hnull_rows
    for row in op_scores:
        row["maxT_p"] = hnull_summary["top_operation_maxT_p"] if abs(float(row["held_base_fractional_mse_gain"]) - htop) <= 1e-12 else (1 + sum(float(x["top_operation_fractional_mse_gain"]) >= float(row["held_base_fractional_mse_gain"]) - 1e-12 for x in hnull_rows)) / (WORLDS + 1)
        strong = float(row["held_base_fractional_mse_gain"]) > 0 and float(row["held_base_mean_cosine"]) > 0 and float(row["held_base_positive_dot_rate"]) > 0.5
        cross = float(row["held_base_and_section_fractional_mse_gain"]) > 0 and float(row["held_base_and_hand_fractional_mse_gain"]) > 0
        row["label"] = "INTERESTING_EXPLORATORY" if strong and cross and float(row["maxT_p"]) <= 0.05 else "WEAK" if strong else "UNSTABLE" if float(row["held_base_fractional_mse_gain"]) > 0 else "NO_SIGNAL"
        row["claim_state"] = "HELD_BASE_SUBSTITUTION_VECTOR_NO_MORPHOLOGY_OR_MEANING"
    op_scores.sort(key=lambda r: (float(r["maxT_p"]), -float(r["held_base_fractional_mse_gain"]), str(r["operation"])))

    # Decision and counterexamples.
    powered = [r for r in comparator_rows if r["corpus_id"] != "VOYNICH_PAGE_HOST" and r["capacity_state"] == "POWERED"]
    vgeneric = next(r for r in comparator_rows if r["corpus_id"] == "VOYNICH_PAGE_HOST")
    all_modes_positive = all(float(hsummary[mode, "OP_SUBSTITUTION"]["fractional_mse_gain"]) > 0 for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND"))
    has_maxt = any(float(r["maxT_p"]) <= 0.05 and r["label"] == "INTERESTING_EXPLORATORY" for r in op_scores)
    above_controls = bool(powered) and float(vgeneric["op_fractional_mse_gain"]) > max(float(r["op_fractional_mse_gain"]) for r in powered)
    primary_positive = float(primary["fractional_mse_gain"]) > 0 and float(primary["mean_cosine"]) > 0 and float(primary["positive_dot_rate"]) > 0.5
    if primary_positive and all_modes_positive and has_maxt and above_controls: status = "PRODUCTIVE_INTERNAL_SUBSTITUTION_TRANSFER_INTERESTING"
    elif primary_positive and not above_controls: status = "SUBSTITUTION_TRANSFER_NOT_ABOVE_HISTORICAL_CONTROLS"
    elif primary_positive: status = "LOCAL_OR_REGISTER_CONDITIONED_SUBSTITUTION_ONLY"
    else: status = "NO_PRODUCTIVE_SUBSTITUTION_SIGNAL"

    counters = []
    for row in sorted(op_scores, key=lambda r: float(r["held_base_fractional_mse_gain"]))[:12]:
        counters.append({"counterexample_type": "LOW_OR_NEGATIVE_HELD_BASE_TRANSFER", "item": row["operation"], "evidence": f"gain {float(row['held_base_fractional_mse_gain']):+.6f}; cosine {float(row['held_base_mean_cosine']):+.6f}", "impact": "Repeated spelling change does not imply a uniform context operator."})
    for row in op_scores:
        if float(row["held_base_fractional_mse_gain"]) > 0 and (float(row["held_base_and_section_fractional_mse_gain"]) <= 0 or float(row["held_base_and_hand_fractional_mse_gain"]) <= 0):
            counters.append({"counterexample_type": "REGISTER_OR_HAND_REVERSAL", "item": row["operation"], "evidence": f"base {float(row['held_base_fractional_mse_gain']):+.6f}; section {float(row['held_base_and_section_fractional_mse_gain']):+.6f}; hand {float(row['held_base_and_hand_fractional_mse_gain']):+.6f}", "impact": "The relation is not manuscript-wide under the strict transfer split."})
    counters += [
        {"counterexample_type": "EXACT_IDENTITY_BASELINE", "item": "EXACT_PAIR_OTHER_STRATA", "evidence": f"held-base exact-pair gain {float(hsummary['HELD_BASE','EXACT_PAIR_OTHER_STRATA']['fractional_mse_gain']):+.6f}", "impact": "Exact host-pair recurrence remains separate and may explain more than the substitution class."},
        {"counterexample_type": "GDT003_STRING_CEILING", "item": "GDT003", "evidence": "Nested paradigm prediction did not beat character/string baselines.", "impact": "A context-vector relation is not established linguistic morphology."},
        {"counterexample_type": "HISTORICAL_CONTEXT_LIMIT", "item": "GDT159", "evidence": "Historical controls lack Voynich HPR2 fields and are compared only on the identical generic local-sequence endpoint.", "impact": "Cross-corpus ranking calibrates ordinary neighborhood structure, not identical manuscript annotation."},
    ]

    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "HPR2 outer-context delta, min2 endpoint occurrences, leave base family out."},
        {"variant_id": "V01", "status": "RUN_TRANSFER", "description": "Also exclude target section."},
        {"variant_id": "V02", "status": "RUN_TRANSFER", "description": "Also exclude target hand."},
        {"variant_id": "V03", "status": "RUN_BASELINE", "description": "Position-only different-glyph-pair delta."},
        {"variant_id": "V04", "status": "RUN_BASELINE", "description": "Exact host pair from other section/hand strata, kept separate."},
        {"variant_id": "V05", "status": "RUN_CONTROL", "description": "Identical generic contiguous-neighbor length and unit-position context on Voynich plus five GDT159 corpora."},
        {"variant_id": "V06", "status": "RUN_NULL", "description": "1024 position-preserving identity-label worlds per corpus."},
        {"variant_id": "V07", "status": "NOT_RUN", "description": "No semantic labels, language model, phoneme map, translation, alternative HPR2 parser, or f84 row."},
    ]

    def fmt(rows):
        return [{k: (f"{v:.12f}" if isinstance(v, float) else v) for k, v in row.items()} for row in rows]
    write(INVENTORY, fmt(inventory)); write(HPR_PRED, fmt(hpred)); write(GENERIC_PRED, fmt(generic_predictions)); write(OP_SCORES, fmt(op_scores)); write(COMPARATORS, fmt(comparator_rows)); write(NULLS, fmt(all_nulls)); write(COUNTER, counters); write(VARIANTS, variants)

    top = op_scores[:12]
    report = f"""# GDT163 — substitution context-transfer report

Decision: **{status}**.

## HPR2 outer-context transfer

The frozen short-host inventory yields {len(hcases):,} section×hand cells from
{len(inventory)} directed substitution classes; {sum(int(r['retained_for_transfer']) for r in inventory)} classes meet the four-cell transfer threshold.

| split | model | predictions | fractional MSE gain | mean cosine | positive-dot rate |
| --- | --- | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{mode}` | `{model}` | {int(hsummary[mode,model]['predictions'])} | {float(hsummary[mode,model]['fractional_mse_gain']):+.6f} | {float(hsummary[mode,model]['mean_cosine']):+.6f} | {float(hsummary[mode,model]['positive_dot_rate']):.3f} |\n" for mode in ("HELD_BASE","HELD_BASE_AND_SECTION","HELD_BASE_AND_HAND") for model in ("OP_SUBSTITUTION","POSITION_ONLY","EXACT_PAIR_OTHER_STRATA")) + f"""

The primary operation learner's position-preserving aggregate p is
{hnull_summary['aggregate_local_p']:.6f}; its best-operation maxT p is
{hnull_summary['top_operation_maxT_p']:.6f}.  Exact-pair transfer is shown only
as a separate baseline and never enters the learned substitution vector.

## Strongest specific substitutions

| operation | cells/bases | sections/hands | held-base gain | held-section | held-hand | cosine | maxT p | label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
""" + "".join(f"| `{r['operation']}` | {r['eligible_cells']}/{r['base_families']} | {r['sections']}/{r['hands']} | {float(r['held_base_fractional_mse_gain']):+.4f} | {float(r['held_base_and_section_fractional_mse_gain']):+.4f} | {float(r['held_base_and_hand_fractional_mse_gain']):+.4f} | {float(r['held_base_mean_cosine']):+.4f} | {float(r['maxT_p']):.4f} | `{r['label']}` |\n" for r in top) + f"""

These rows are selected after scoring and receive maxT rather than local-only
labels.  Character names are frozen HPR2 display characters, not inferred
manuscript graphemes or sounds.

## Identical generic local-sequence control

| corpus | capacity | cases/predictions | op gain | position gain | increment | cosine | positive-dot | null p | top maxT p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['corpus_id']}` | `{r['capacity_state']}` | {r['eligible_cases']}/{r['op_predictions']} | {float(r['op_fractional_mse_gain']):+.5f} | {float(r['position_fractional_mse_gain']):+.5f} | {float(r['increment_over_position']):+.5f} | {float(r['op_mean_cosine']):+.4f} | {float(r['op_positive_dot_rate']):.3f} | {float(r['null_local_p']):.4f} | {float(r['best_operation_maxT_p']):.4f} |\n" for r in comparator_rows) + f"""

This endpoint is deliberately modest: previous/next contiguous form length and
within-unit position.  It is the only context representation applied
identically to Voynich and the historical corpora.  GDT159 sampled gaps remain
`MISSING`; they are not reinterpreted as record boundaries.

## Interpretation

The result tests whether a repeated surface substitution carries a portable
formal-context delta beyond exact host identity and position.  Even a positive
result is not a linguistic morphology finding: GDT003's string ceiling and
GDT162's exact-identity advantage remain in force.  No substitution receives a
function, morpheme, phoneme, language, semantic role, meaning, plaintext, or
translation.

All f84 rows were rejected before retention.  The actual source has zero f84r
rows; f84r was not opened, queried, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {"schema": "GDT163_SUBSTITUTION_CONTEXT_TRANSFER_RESULT_V1", "status": status,
              "source_rows": len(source), "rejected_f84_rows": rejected, "short_host_occurrences": len(candidate), "short_host_types": len(host_labels),
              "hpr2_dimensions": hpr_dims, "hpr2_cells": len(hcases), "substitution_classes": len(inventory), "retained_substitution_classes": sum(int(r["retained_for_transfer"]) for r in inventory),
              "hpr2_summaries": {f"{mode}|{model}": hsummary[mode, model] for mode in ("HELD_BASE","HELD_BASE_AND_SECTION","HELD_BASE_AND_HAND") for model in ("OP_SUBSTITUTION","POSITION_ONLY","EXACT_PAIR_OTHER_STRATA")},
              "hpr2_null": hnull_summary, "top_operations": top, "generic_comparators": comparator_rows,
              "decision_inputs": {"primary_positive": primary_positive, "all_modes_positive": all_modes_positive, "at_least_one_maxT_operation": has_maxt, "generic_voynich_above_all_powered_controls": above_controls},
              "interpretation": "Held-base prediction of formal context deltas by exact one-character substitution classes, with exact identity separate and historical surface controls.",
              "claim_ceiling": "No grapheme, phoneme, morpheme, word, POS, language, semantic role, meaning, plaintext, or translation.",
              "f84r": {"present_in_actual_input": False, "opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
              "inputs": {SOURCE.name: sha(SOURCE), CONTROL_SOURCE.name: sha(CONTROL_SOURCE), CONTROL_MANIFEST.name: sha(CONTROL_MANIFEST), DESIGN.name: sha(DESIGN), "gdt162_result.json": sha(ROOT / "gdt162_result.json"), "gdt159_result.json": sha(ROOT / "gdt159_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {p.name: sha(p) for p in (INVENTORY,HPR_PRED,GENERIC_PRED,OP_SCORES,COMPARATORS,NULLS,COUNTER,VARIANTS)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "hpr_cells": len(hcases), "primary_gain": primary["fractional_mse_gain"], "section_gain": hsummary["HELD_BASE_AND_SECTION","OP_SUBSTITUTION"]["fractional_mse_gain"], "hand_gain": hsummary["HELD_BASE_AND_HAND","OP_SUBSTITUTION"]["fractional_mse_gain"], "top": top[0]["operation"] if top else "NONE"}, sort_keys=True))


if __name__ == "__main__": main()
