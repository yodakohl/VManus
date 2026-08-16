#!/usr/bin/env python3
"""GDT164: parser-independent held-base substitution context transfer."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import random
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
CONTROL_SOURCE = ROOT / "gdt159_diplomatic_corpora.json.gz"
CONTROL_MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
DESIGN = ROOT / "gdt164_design.json"
METHOD = ROOT / "GDT164_PARSER_INDEPENDENT_SUBSTITUTION_METHOD.md"
REPORT = ROOT / "GDT164_PARSER_INDEPENDENT_SUBSTITUTION_REPORT.md"
INVENTORY = ROOT / "gdt164_substitution_inventory.tsv"
PREDICTIONS = ROOT / "gdt164_external_context_predictions.tsv"
OP_SCORES = ROOT / "gdt164_operation_scores.tsv"
COMPARATORS = ROOT / "gdt164_comparator_scores.tsv"
NULLS = ROOT / "gdt164_null_results.tsv"
COUNTER = ROOT / "gdt164_counterexamples.tsv"
VARIANTS = ROOT / "gdt164_variant_log.tsv"
RESULT = ROOT / "gdt164_result.json"

LENGTHS = (2, 3)
WORLDS = 1024
MIN_COUNT = 2
MIN_CASES = 4
MIN_TRAIN_CASES = 3
MIN_TRAIN_BASES = 2
MAX_WEIGHT = 20.0
BLOCKS = ("prev_hash", "next_hash", "prev_len", "next_len", "prev_freq", "next_freq",
          "from_start", "to_end", "unit_quartile", "unit_span")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


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
        writer.writeheader()
        writer.writerows(rows)


def compact(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hash_bucket(value: str) -> str:
    return f"H{int(hashlib.sha256(value.encode()).hexdigest()[:8], 16) % 32:02d}"


def len_class(value: str | None) -> str:
    if value is None:
        return "MISSING"
    n = len(value)
    return "L1" if n == 1 else "L2" if n == 2 else "L3" if n == 3 else "L4P"


def freq_class(n: int | None) -> str:
    if n is None:
        return "MISSING"
    return "R1" if n == 1 else "R2_4" if n <= 4 else "R5_15" if n <= 15 else "R16P"


def distance_class(n: int) -> str:
    return str(n) if n < 3 else "3P"


def span_class(n: int) -> str:
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def read_voynich() -> tuple[list[dict[str, str]], int, int]:
    minimal = []
    rejected = 0
    total = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for source_row in csv.DictReader(handle, delimiter="\t"):
            total += 1
            if source_row["page"].startswith("f84") or source_row["locus"].startswith("f84"):
                rejected += 1
                continue
            minimal.append({"identity": source_row["page_host"], "unit": source_row["locus"],
                            "index": source_row["group_index"], "stratum1": source_row["section"],
                            "stratum2": source_row["hand"], "corpus_id": "VOYNICH_PAGE_HOST"})
    assert total == 15592 and rejected == 228 and len(minimal) == 15364
    assert not any(r["unit"].startswith("f84") for r in minimal)
    return minimal, rejected, total


def read_controls() -> dict[str, list[dict[str, str]]]:
    with gzip.open(CONTROL_SOURCE, "rt", encoding="utf-8") as handle:
        raw = json.load(handle)["records"]
    out = defaultdict(list)
    for row in raw:
        corpus = str(row["corpus_id"])
        out[corpus].append({"identity": unicodedata.normalize("NFC", str(row["form"])),
                            "unit": str(row["unit_id"]), "index": str(row["occurrence_index"]),
                            "stratum1": str(row["fold_id"]), "stratum2": "ALL", "corpus_id": corpus})
    return dict(out)


def external_occurrences(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    frequency = Counter(r["identity"] for r in rows)
    units = defaultdict(dict)
    for row in rows:
        units[row["unit"]][int(row["index"])] = row
    out = []
    for unit, index in units.items():
        lo, hi = min(index), max(index)
        span = hi - lo + 1
        for pos, row in index.items():
            if len(row["identity"]) not in LENGTHS:
                continue
            previous = index.get(pos - 1)
            following = index.get(pos + 1)
            pident = previous["identity"] if previous else None
            nident = following["identity"] if following else None
            quartile = min(3, int(4 * (pos - lo) / max(1, hi - lo)))
            out.append({**row,
                        "prev_hash": hash_bucket(pident) if pident else "MISSING",
                        "next_hash": hash_bucket(nident) if nident else "MISSING",
                        "prev_len": len_class(pident), "next_len": len_class(nident),
                        "prev_freq": freq_class(frequency[pident]) if pident else "MISSING",
                        "next_freq": freq_class(frequency[nident]) if nident else "MISSING",
                        "from_start": distance_class(pos - lo), "to_end": distance_class(hi - pos),
                        "unit_quartile": f"Q{quartile}", "unit_span": span_class(span)})
    return out


def vectorize(occurrences: list[dict[str, str]]):
    values = {block: sorted({r[block] for r in occurrences}) for block in BLOCKS}
    dimensions = [(block, value) for block in BLOCKS for value in values[block]]
    sizes = {block: len(values[block]) for block in BLOCKS}
    totals = Counter()
    cells = Counter()
    for row in occurrences:
        key = (row["identity"], row["stratum1"], row["stratum2"])
        totals[key] += 1
        for block in BLOCKS:
            cells[key, block, row[block]] += 1
    vectors = {key: np.array([(cells[key, block, value] + .5) / (n + .5 * sizes[block])
                              for block, value in dimensions], dtype=float)
               for key, n in totals.items()}
    return vectors, totals, [f"{block}={value}" for block, value in dimensions]


def edge_list(mapping: dict[str, str]) -> list[dict[str, object]]:
    buckets = defaultdict(list)
    for identity, word in mapping.items():
        if len(word) not in LENGTHS:
            continue
        for pos in range(len(word)):
            buckets[len(word), pos, word[:pos] + "*" + word[pos + 1:]].append(identity)
    out = []
    for (length, pos, base), identities in buckets.items():
        for i, left in enumerate(identities):
            for right in identities[i + 1:]:
                a, b = mapping[left], mapping[right]
                if a == b or sum(x != y for x, y in zip(a, b)) != 1:
                    continue
                if a[pos] < b[pos]:
                    source, target, sg, tg = left, right, a[pos], b[pos]
                else:
                    source, target, sg, tg = right, left, b[pos], a[pos]
                out.append({"source": source, "target": target, "length": length, "position": pos + 1,
                            "source_glyph": sg, "target_glyph": tg,
                            "operation": f"L{length}:P{pos + 1}:{sg}>{tg}",
                            "base_family": f"L{length}:P{pos + 1}:{base}"})
    return sorted(out, key=lambda r: (r["operation"], r["base_family"], r["source"], r["target"]))


def cases_for(mapping, vectors, totals):
    strata = defaultdict(set)
    for key in vectors:
        strata[key[0]].add((key[1], key[2]))
    out = []
    for edge in edge_list(mapping):
        for s1, s2 in sorted(strata[edge["source"]] & strata[edge["target"]]):
            source = (edge["source"], s1, s2)
            target = (edge["target"], s1, s2)
            ns, nt = totals[source], totals[target]
            if ns < MIN_COUNT or nt < MIN_COUNT:
                continue
            out.append({**edge, "stratum1": s1, "stratum2": s2, "source_count": ns,
                        "target_count": nt, "weight": min(MAX_WEIGHT, float(min(ns, nt))),
                        "delta": vectors[target] - vectors[source]})
    return out


def weighted_mean(rows):
    return np.average(np.stack([r["delta"] for r in rows]), axis=0,
                      weights=np.array([r["weight"] for r in rows]))


def make_prediction(test, predicted, model, mode):
    actual = test["delta"]
    dot = float(actual @ predicted)
    norm = float(np.linalg.norm(actual) * np.linalg.norm(predicted))
    return {"mode": mode, "model": model, "operation": test["operation"],
            "base_family": test["base_family"], "source_host": test["source"],
            "target_host": test["target"], "stratum1": test["stratum1"],
            "stratum2": test["stratum2"], "source_count": test["source_count"],
            "target_count": test["target_count"], "weight": test["weight"],
            "zero_sse": float(actual @ actual),
            "pred_sse": float((actual - predicted) @ (actual - predicted)),
            "dot": dot, "cosine": dot / norm if norm else 0.0,
            "actual_norm": float(np.linalg.norm(actual)), "predicted_norm": float(np.linalg.norm(predicted)),
            "actual": actual, "predicted": predicted,
            "claim_state": "EXTERNAL_CONTEXT_DELTA_NO_MORPHOLOGY_OR_MEANING"}


def predictions(cases, mode: str, include_exact: bool):
    by_op = defaultdict(list)
    by_position = defaultdict(list)
    by_exact = defaultdict(list)
    for row in cases:
        by_op[row["operation"]].append(row)
        by_position[row["length"], row["position"]].append(row)
        by_exact[row["source"], row["target"]].append(row)
    out = []
    for test in cases:
        def allowed(row):
            if mode in ("HELD_BASE_AND_SECTION", "HELD_BASE_AND_FOLD") and row["stratum1"] == test["stratum1"]:
                return False
            if mode == "HELD_BASE_AND_HAND" and row["stratum2"] == test["stratum2"]:
                return False
            return True
        train = [r for r in by_op[test["operation"]]
                 if r["base_family"] != test["base_family"] and allowed(r)]
        if len(train) >= MIN_TRAIN_CASES and len({r["base_family"] for r in train}) >= MIN_TRAIN_BASES:
            out.append(make_prediction(test, weighted_mean(train), "OP_SUBSTITUTION", mode))
        position = [r for r in by_position[test["length"], test["position"]]
                    if r["operation"] != test["operation"] and r["base_family"] != test["base_family"] and allowed(r)]
        if len(position) >= MIN_TRAIN_CASES and len({r["base_family"] for r in position}) >= MIN_TRAIN_BASES:
            out.append(make_prediction(test, weighted_mean(position), "POSITION_ONLY", mode))
        if include_exact:
            exact = [r for r in by_exact[test["source"], test["target"]] if r is not test and allowed(r)]
            if exact:
                out.append(make_prediction(test, weighted_mean(exact), "EXACT_PAIR_OTHER_STRATA", mode))
    return out


def stats(rows):
    if not rows:
        return {"predictions": 0, "weight": 0.0, "fractional_mse_gain": 0.0,
                "mean_cosine": 0.0, "positive_dot_rate": 0.0}
    weight = sum(float(r["weight"]) for r in rows)
    zero = sum(float(r["weight"]) * float(r["zero_sse"]) for r in rows)
    error = sum(float(r["weight"]) * float(r["pred_sse"]) for r in rows)
    return {"predictions": len(rows), "weight": weight,
            "fractional_mse_gain": 1 - error / zero if zero else 0.0,
            "mean_cosine": sum(float(r["weight"]) * float(r["cosine"]) for r in rows) / weight,
            "positive_dot_rate": sum(float(r["weight"]) * (float(r["dot"]) > 0) for r in rows) / weight}


def primary(cases):
    rows = [r for r in predictions(cases, "HELD_BASE", False) if r["model"] == "OP_SUBSTITUTION"]
    per_op = defaultdict(list)
    for row in rows:
        per_op[row["operation"]].append(row)
    return stats(rows), {key: stats(value) for key, value in per_op.items()}


def random_mapping(labels: dict[str, str], rng: random.Random) -> dict[str, str]:
    out = {identity: [""] * len(word) for identity, word in labels.items()}
    for length in LENGTHS:
        identities = sorted(i for i, word in labels.items() if len(word) == length)
        for pos in range(length):
            glyphs = [labels[i][pos] for i in identities]
            rng.shuffle(glyphs)
            for identity, glyph in zip(identities, glyphs):
                out[identity][pos] = glyph
    return {identity: "".join(chars) for identity, chars in out.items()}


def null_worlds(corpus, labels, vectors, totals, observed_gain, observed_top):
    rng = random.Random(seed("GDT164_NULL_" + corpus))
    rows = []
    gains = []
    tops = []
    for world in range(WORLDS):
        mapping = random_mapping(labels, rng)
        cases = cases_for(mapping, vectors, totals)
        score, per_op = primary(cases)
        top = max((x["fractional_mse_gain"] for x in per_op.values()), default=0.0)
        rows.append({"corpus_id": corpus, "world": world, "eligible_cases": len(cases),
                     "op_predictions": int(score["predictions"]),
                     "op_fractional_mse_gain": score["fractional_mse_gain"],
                     "top_operation_fractional_mse_gain": top,
                     "collisions": len(mapping) - len(set(mapping.values()))})
        gains.append(float(score["fractional_mse_gain"]))
        tops.append(float(top))
    return rows, {"aggregate_local_p": (1 + sum(x >= observed_gain - 1e-12 for x in gains)) / (WORLDS + 1),
                  "top_operation_maxT_p": (1 + sum(x >= observed_top - 1e-12 for x in tops)) / (WORLDS + 1),
                  "null_aggregate_mean": sum(gains) / WORLDS, "null_top_mean": sum(tops) / WORLDS}


def printable_prediction(row, corpus):
    return {key: value for key, value in {**row, "corpus_id": corpus}.items()
            if key not in ("actual", "predicted")}


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert design["status"] == "FROZEN_BEFORE_SCORING" and design["null_worlds"] == WORLDS
    vrows, rejected, source_total = read_voynich()
    payloads = {"VOYNICH_PAGE_HOST": vrows, **read_controls()}
    objects = {}
    all_predictions = []
    comparator_rows = []
    inventory_rows = []
    voy_modes = ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND")
    summaries = {}
    voy_dims = []
    voy_cases = []

    for corpus, minimal in sorted(payloads.items()):
        occurrences = external_occurrences(minimal)
        vectors, totals, dimensions = vectorize(occurrences)
        labels = {r["identity"]: r["identity"] for r in occurrences}
        cases = cases_for(labels, vectors, totals)
        base_predictions = predictions(cases, "HELD_BASE", True)
        transfer_mode = "HELD_BASE_AND_SECTION" if corpus == "VOYNICH_PAGE_HOST" else "HELD_BASE_AND_FOLD"
        transfer_predictions = predictions(cases, transfer_mode, True)
        hand_predictions = predictions(cases, "HELD_BASE_AND_HAND", True) if corpus == "VOYNICH_PAGE_HOST" else []
        combined = base_predictions + transfer_predictions + hand_predictions
        all_predictions += [printable_prediction(row, corpus) for row in combined]
        score, per_op = primary(cases)
        top = max((x["fractional_mse_gain"] for x in per_op.values()), default=0.0)
        row = {"corpus_id": corpus, "occurrences": len(occurrences), "types": len(labels),
               "hamming1_edges": len(edge_list(labels)), "eligible_cells": len(cases),
               "retained_operations": sum(len([r for r in cases if r["operation"] == op]) >= MIN_CASES for op in {r["operation"] for r in cases})}
        for mode, predrows in (("HELD_BASE", base_predictions), (transfer_mode, transfer_predictions)):
            for model in ("OP_SUBSTITUTION", "POSITION_ONLY", "EXACT_PAIR_OTHER_STRATA"):
                summary = stats([r for r in predrows if r["model"] == model])
                for key, value in summary.items():
                    row[f"{mode.lower()}_{model.lower()}_{key}"] = value
        row["best_operation_gain"] = top
        row["capacity_state"] = "POWERED" if int(row["held_base_op_substitution_predictions"]) >= 100 else "LOW_CAPACITY"
        comparator_rows.append(row)
        objects[corpus] = (labels, vectors, totals, cases, score, per_op, top)
        if corpus == "VOYNICH_PAGE_HOST":
            voy_dims = dimensions
            voy_cases = cases
            for mode, predrows in (("HELD_BASE", base_predictions),
                                   ("HELD_BASE_AND_SECTION", transfer_predictions),
                                   ("HELD_BASE_AND_HAND", hand_predictions)):
                for model in ("OP_SUBSTITUTION", "POSITION_ONLY", "EXACT_PAIR_OTHER_STRATA"):
                    summaries[mode, model] = stats([r for r in predrows if r["model"] == model])

    # Voynich operation inventory and post-ranked operation atlas.
    op_cases = defaultdict(list)
    for case in voy_cases:
        op_cases[case["operation"]].append(case)
    for op, group in sorted(op_cases.items()):
        first = group[0]
        inventory_rows.append({"operation": op, "length": first["length"], "position": first["position"],
                               "source_glyph": first["source_glyph"], "target_glyph": first["target_glyph"],
                               "eligible_cells": len(group), "base_families": len({r["base_family"] for r in group}),
                               "sections": "|".join(sorted({str(r["stratum1"]) for r in group})),
                               "hands": "|".join(sorted({str(r["stratum2"]) for r in group})),
                               "retained_for_transfer": int(len(group) >= MIN_CASES),
                               "claim_state": "DIRECTED_FORMAL_RELATION_NO_MORPHOLOGY_OR_MEANING"})

    vpred_objects = []
    for mode in voy_modes:
        vpred_objects += predictions(voy_cases, mode, False)
    op_scores = []
    for op in sorted(objects["VOYNICH_PAGE_HOST"][5]):
        row = {"operation": op, "eligible_cells": len(op_cases[op]),
               "base_families": len({r["base_family"] for r in op_cases[op]}),
               "sections": len({r["stratum1"] for r in op_cases[op]}),
               "hands": len({r["stratum2"] for r in op_cases[op]})}
        for mode in voy_modes:
            subset = [r for r in vpred_objects if r["mode"] == mode and r["model"] == "OP_SUBSTITUTION" and r["operation"] == op]
            summary = stats(subset)
            for key, value in summary.items():
                row[f"{mode.lower()}_{key}"] = value
        subset = [r for r in vpred_objects if r["mode"] == "HELD_BASE" and r["model"] == "OP_SUBSTITUTION" and r["operation"] == op]
        if subset:
            weights = np.array([r["weight"] for r in subset])
            actual = np.average(np.stack([r["actual"] for r in subset]), axis=0, weights=weights)
            predicted = np.average(np.stack([r["predicted"] for r in subset]), axis=0, weights=weights)
            strongest = sorted(range(len(actual)), key=lambda i: (-abs(float(actual[i])), voy_dims[i]))[:5]
            row["dominant_external_dimensions"] = "|".join(f"{voy_dims[i]}:{actual[i]:+.4f}/{predicted[i]:+.4f}" for i in strongest)
        else:
            row["dominant_external_dimensions"] = ""
        op_scores.append(row)

    # One identical position-preserving null per corpus.
    all_nulls = []
    null_summaries = {}
    for corpus in sorted(objects):
        labels, vectors, totals, cases, score, per_op, top = objects[corpus]
        null_rows, null_summary = null_worlds(corpus, labels, vectors, totals,
                                              float(score["fractional_mse_gain"]), float(top))
        all_nulls += null_rows
        null_summaries[corpus] = null_summary
        row = next(r for r in comparator_rows if r["corpus_id"] == corpus)
        row.update({"null_local_p": null_summary["aggregate_local_p"],
                    "best_operation_maxT_p": null_summary["top_operation_maxT_p"],
                    "null_mean_gain": null_summary["null_aggregate_mean"]})

    vnull = null_summaries["VOYNICH_PAGE_HOST"]
    hnull_rows = [r for r in all_nulls if r["corpus_id"] == "VOYNICH_PAGE_HOST"]
    for row in op_scores:
        gain = float(row["held_base_fractional_mse_gain"])
        row["maxT_p"] = (1 + sum(float(x["top_operation_fractional_mse_gain"]) >= gain - 1e-12 for x in hnull_rows)) / (WORLDS + 1)
        cross = float(row["held_base_and_section_fractional_mse_gain"]) > 0 and float(row["held_base_and_hand_fractional_mse_gain"]) > 0
        positive = gain > 0 and float(row["held_base_mean_cosine"]) > 0 and float(row["held_base_positive_dot_rate"]) > .5
        row["label"] = "INTERESTING_EXPLORATORY" if positive and cross and float(row["maxT_p"]) <= .05 else "WEAK" if positive else "UNSTABLE" if gain > 0 else "NO_SIGNAL"
        row["claim_state"] = "PARSER_INDEPENDENT_EXTERNAL_CONTEXT_RELATION_NO_MORPHOLOGY_OR_MEANING"
    op_scores.sort(key=lambda r: (float(r["maxT_p"]), -float(r["held_base_fractional_mse_gain"]), r["operation"]))

    vrow = next(r for r in comparator_rows if r["corpus_id"] == "VOYNICH_PAGE_HOST")
    powered = [r for r in comparator_rows if r["corpus_id"] != "VOYNICH_PAGE_HOST" and r["capacity_state"] == "POWERED"]
    base_gain = float(summaries["HELD_BASE", "OP_SUBSTITUTION"]["fractional_mse_gain"])
    section_gain = float(summaries["HELD_BASE_AND_SECTION", "OP_SUBSTITUTION"]["fractional_mse_gain"])
    hand_gain = float(summaries["HELD_BASE_AND_HAND", "OP_SUBSTITUTION"]["fractional_mse_gain"])
    all_positive = base_gain > 0 and section_gain > 0 and hand_gain > 0
    null_pass = float(vnull["aggregate_local_p"]) <= .05
    maxt_pass = any(float(r["maxT_p"]) <= .05 and r["label"] == "INTERESTING_EXPLORATORY" for r in op_scores)
    above_controls = bool(powered) and base_gain > max(float(r["held_base_op_substitution_fractional_mse_gain"]) for r in powered)
    if all_positive and null_pass and maxt_pass and above_controls:
        status = "PARSER_INDEPENDENT_SUBSTITUTION_TRANSFER_SUPPORTED"
    elif all_positive:
        status = "PARSER_INDEPENDENT_TRANSFER_PROVISIONAL"
    elif base_gain > 0:
        status = "PARSER_INDEPENDENT_TRANSFER_LOCAL_ONLY"
    else:
        status = "PARSER_INDEPENDENT_SUBSTITUTION_NOT_SUPPORTED"

    counters = []
    for row in sorted(op_scores, key=lambda r: float(r["held_base_fractional_mse_gain"]))[:15]:
        counters.append({"counterexample_type": "LOW_OR_NEGATIVE_EXTERNAL_TRANSFER", "item": row["operation"],
                         "evidence": f"base {float(row['held_base_fractional_mse_gain']):+.6f}; section {float(row['held_base_and_section_fractional_mse_gain']):+.6f}; hand {float(row['held_base_and_hand_fractional_mse_gain']):+.6f}",
                         "impact": "Repeated one-character relation does not guarantee an external-context operator."})
    counters += [
        {"counterexample_type": "EXACT_IDENTITY_BASELINE", "item": "EXACT_PAIR_OTHER_STRATA",
         "evidence": f"held-base gain {float(summaries['HELD_BASE','EXACT_PAIR_OTHER_STRATA']['fractional_mse_gain']):+.6f}",
         "impact": "Exact pair identity is separate and may remain more predictive than substitution class."},
        {"counterexample_type": "HASHED_NEIGHBOR_IDENTITY", "item": "SHA256_BUCKET32",
         "evidence": "External neighbor identities are compressed to fixed 32-way hashes.",
         "impact": "This controls target dimension but can hide or create collision-level detail."},
        {"counterexample_type": "GDT003_STRING_CEILING", "item": "GDT003",
         "evidence": "Nested paradigm prediction did not beat strong character/string baselines.",
         "impact": "External context transfer alone is not established linguistic morphology."}
    ]
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "External neighboring identity/class plus unit-position delta; held masked base."},
        {"variant_id": "V01", "status": "RUN_TRANSFER", "description": "Also exclude target Voynich section."},
        {"variant_id": "V02", "status": "RUN_TRANSFER", "description": "Also exclude target Voynich hand."},
        {"variant_id": "V03", "status": "RUN_TRANSFER", "description": "Historical held-fold transfer."},
        {"variant_id": "V04", "status": "RUN_BASELINE", "description": "Position-only different glyph pair."},
        {"variant_id": "V05", "status": "RUN_BASELINE", "description": "Exact host pair in other strata."},
        {"variant_id": "V06", "status": "RUN_NULL", "description": "1024 position-preserving identity-label worlds per corpus."},
        {"variant_id": "V07", "status": "FORBIDDEN", "description": "No focal raw token, wrapper, inner-D, frame, right family, DY, B3, semantic field, alternative parser, or f84 row."}
    ]

    def formatted(rows):
        return [{k: (f"{v:.12f}" if isinstance(v, float) else v) for k, v in row.items()} for row in rows]
    write(INVENTORY, formatted(inventory_rows))
    write(PREDICTIONS, formatted(all_predictions))
    write(OP_SCORES, formatted(op_scores))
    write(COMPARATORS, formatted(comparator_rows))
    write(NULLS, formatted(all_nulls))
    write(COUNTER, counters)
    write(VARIANTS, variants)

    top = op_scores[:12]
    report = f"""# GDT164 — parser-independent substitution report

Decision: **{status}**.

## Voynich external-context transfer

The firewall-retained source has {len(vrows):,} rows and {len(voy_cases):,}
eligible section×hand cells.  The target has {len(voy_dims)} dimensions built
only from neighboring source-group identities/classes and mechanical unit
coordinates.

| split | model | predictions | fractional MSE gain | cosine | positive-dot |
| --- | --- | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{mode}` | `{model}` | {int(summaries[mode,model]['predictions'])} | {float(summaries[mode,model]['fractional_mse_gain']):+.6f} | {float(summaries[mode,model]['mean_cosine']):+.6f} | {float(summaries[mode,model]['positive_dot_rate']):.3f} |\n" for mode in voy_modes for model in ("OP_SUBSTITUTION","POSITION_ONLY","EXACT_PAIR_OTHER_STRATA")) + f"""

Aggregate position-preserving p is {float(vnull['aggregate_local_p']):.6f};
best-operation maxT p is {float(vnull['top_operation_maxT_p']):.6f}.

## Strongest directed relations

| operation | cells/bases | sections/hands | base gain | held-section | held-hand | maxT p | dominant external deltas | label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
""" + "".join(f"| `{r['operation']}` | {r['eligible_cells']}/{r['base_families']} | {r['sections']}/{r['hands']} | {float(r['held_base_fractional_mse_gain']):+.4f} | {float(r['held_base_and_section_fractional_mse_gain']):+.4f} | {float(r['held_base_and_hand_fractional_mse_gain']):+.4f} | {float(r['maxT_p']):.4f} | `{r['dominant_external_dimensions']}` | `{r['label']}` |\n" for r in top) + f"""

These are post-ranked exploratory relations.  Character names are frozen HPR2
display characters, not manuscript graphemes or sounds.

## Identical historical endpoint

| corpus | capacity | cells/base predictions | held-base gain | position | exact pair | held-stratum gain | null p | top maxT p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['corpus_id']}` | `{r['capacity_state']}` | {r['eligible_cells']}/{int(r['held_base_op_substitution_predictions'])} | {float(r['held_base_op_substitution_fractional_mse_gain']):+.5f} | {float(r['held_base_position_only_fractional_mse_gain']):+.5f} | {float(r['held_base_exact_pair_other_strata_fractional_mse_gain']):+.5f} | {float(r[('held_base_and_section' if r['corpus_id']=='VOYNICH_PAGE_HOST' else 'held_base_and_fold')+'_op_substitution_fractional_mse_gain']):+.5f} | {float(r['null_local_p']):.4f} | {float(r['best_operation_maxT_p']):.4f} |\n" for r in comparator_rows) + f"""

The endpoint and null are identical across corpora.  Historical held strata are
source folds; they are provenance partitions, not independent manuscripts.

## Interpretation

This is the direct parser-coupling test.  The target excludes every focal
same-group HPR2 field and contains only external neighbor and unit-position
information.  The exact identity baseline remains separate.  A positive result
would establish only a transferable surface association; it would not establish
linguistic morphology or meaning.  See `gdt164_counterexamples.tsv` for failed
relations and limitations.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {"schema": "GDT164_PARSER_INDEPENDENT_SUBSTITUTION_RESULT_V1", "status": status,
              "source_total_rows": source_total, "source_retained_rows": len(vrows), "rejected_f84_rows": rejected,
              "external_context_dimensions": voy_dims, "short_host_occurrences": sum(len(r["identity"]) in LENGTHS for r in vrows),
              "short_host_types": len(objects["VOYNICH_PAGE_HOST"][0]), "hamming1_edges": len(edge_list(objects["VOYNICH_PAGE_HOST"][0])),
              "eligible_cells": len(voy_cases), "substitution_classes": len(inventory_rows),
              "retained_substitution_classes": sum(int(r["retained_for_transfer"]) for r in inventory_rows),
              "voynich_summaries": {f"{mode}|{model}": summaries[mode, model] for mode in voy_modes for model in ("OP_SUBSTITUTION","POSITION_ONLY","EXACT_PAIR_OTHER_STRATA")},
              "voynich_null": vnull, "top_operations": top, "comparators": comparator_rows,
              "decision_inputs": {"all_voynich_modes_positive": all_positive, "aggregate_null_pass": null_pass,
                                  "at_least_one_maxT_operation": maxt_pass, "above_all_powered_historical_controls": above_controls},
              "interpretation": "Parser-independent external-context prediction by held-base one-character substitution classes; exact identity remains separate and no linguistic or semantic function is assigned.",
              "claim_ceiling": "No grapheme, phoneme, morpheme, word, POS, language, semantic role, meaning, plaintext, or translation.",
              "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
              "inputs": {SOURCE.name: sha(SOURCE), CONTROL_SOURCE.name: sha(CONTROL_SOURCE), CONTROL_MANIFEST.name: sha(CONTROL_MANIFEST), DESIGN.name: sha(DESIGN), "gdt163_result.json": sha(ROOT / "gdt163_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {p.name: sha(p) for p in (INVENTORY,PREDICTIONS,OP_SCORES,COMPARATORS,NULLS,COUNTER,VARIANTS)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(compact({"status": status, "eligible_cells": len(voy_cases), "base_gain": base_gain,
                   "section_gain": section_gain, "hand_gain": hand_gain,
                   "null_p": vnull["aggregate_local_p"], "maxT_p": vnull["top_operation_maxT_p"]}))


if __name__ == "__main__":
    main()
