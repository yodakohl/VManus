#!/usr/bin/env python3
"""Independent validation of GDT163 source joins, scores, nulls, and seals."""
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
CONTROL = ROOT / "gdt159_diplomatic_corpora.json.gz"
RESULT = ROOT / "gdt163_result.json"
VALIDATION = ROOT / "gdt163_validation.json"
LENGTHS = (2, 3)
COMPONENTS = ("wrapper", "inner_d", "local_frame", "right_family", "dy_closure", "b3")
WORLDS = 1024
MIN_COUNT = 2
MIN_CASES = 4
MIN_TRAIN_CASES = 3
MIN_TRAIN_BASES = 2


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def close(a: float, b: float, tol: float = 3e-9) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rng_seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def length_bin(value: str | None) -> str:
    if value is None:
        return "MISSING"
    n = len(value)
    return "L1" if n == 1 else "L2" if n == 2 else "L3" if n == 3 else "L4P"


def edges(mapping: dict[str, str]) -> list[dict[str, object]]:
    buckets = defaultdict(list)
    for ident, word in mapping.items():
        if len(word) not in LENGTHS:
            continue
        for pos in range(len(word)):
            buckets[len(word), pos, word[:pos] + "*" + word[pos + 1:]].append(ident)
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
                            "operation": f"L{length}:P{pos + 1}:{sg}>{tg}",
                            "base_family": f"L{length}:P{pos + 1}:{base}"})
    return sorted(out, key=lambda r: (r["operation"], r["base_family"], r["source"], r["target"]))


def permuted(labels: dict[str, str], rng: random.Random) -> dict[str, str]:
    out = {ident: [""] * len(word) for ident, word in labels.items()}
    for length in LENGTHS:
        identities = sorted(i for i, word in labels.items() if len(word) == length)
        for pos in range(length):
            glyphs = [labels[i][pos] for i in identities]
            rng.shuffle(glyphs)
            for ident, glyph in zip(identities, glyphs):
                out[ident][pos] = glyph
    return {ident: "".join(chars) for ident, chars in out.items()}


def vectorize(rows: list[dict[str, str]], identity: str, cells: tuple[str, ...], blocks: tuple[str, ...], values: dict[str, list[str]]):
    dimensions = [(block, value) for block in values for value in values[block]]
    sizes = {block: len(values[block]) for block in values}
    totals = Counter()
    observed = Counter()
    for row in rows:
        key = (row[identity],) + tuple(row[x] for x in cells)
        totals[key] += 1
        for block in blocks:
            observed[key, block, row[block]] += 1
    vectors = {key: np.array([(observed[key, block, value] + .5) / (n + .5 * sizes[block])
                              for block, value in dimensions], dtype=float)
               for key, n in totals.items()}
    return vectors, totals


def make_hpr_cases(mapping, vectors, totals):
    strata = defaultdict(set)
    for key in vectors:
        strata[key[0]].add((key[1], key[2]))
    out = []
    for edge in edges(mapping):
        for section, hand in sorted(strata[edge["source"]] & strata[edge["target"]]):
            a = (edge["source"], section, hand)
            b = (edge["target"], section, hand)
            if totals[a] < MIN_COUNT or totals[b] < MIN_COUNT:
                continue
            out.append({**edge, "section": section, "hand": hand,
                        "weight": float(min(20, totals[a], totals[b])), "delta": vectors[b] - vectors[a]})
    return out


def make_generic_cases(mapping, vectors, totals):
    out = []
    for edge in edges(mapping):
        a, b = (edge["source"],), (edge["target"],)
        if totals[a] < MIN_COUNT or totals[b] < MIN_COUNT:
            continue
        out.append({**edge, "section": "ALL", "hand": "ALL",
                    "weight": float(min(20, totals[a], totals[b])), "delta": vectors[b] - vectors[a]})
    return out


def mean(group):
    return np.average(np.stack([r["delta"] for r in group]), axis=0,
                      weights=np.array([r["weight"] for r in group]))


def summarize(actual_predictions):
    if not actual_predictions:
        return {"predictions": 0, "weight": 0.0, "fractional_mse_gain": 0.0,
                "mean_cosine": 0.0, "positive_dot_rate": 0.0}
    weight = sum(r["weight"] for r in actual_predictions)
    zero = sum(r["weight"] * float(r["actual"] @ r["actual"]) for r in actual_predictions)
    error = sum(r["weight"] * float((r["actual"] - r["pred"]) @ (r["actual"] - r["pred"])) for r in actual_predictions)
    cos = 0.0
    positive = 0.0
    for row in actual_predictions:
        dot = float(row["actual"] @ row["pred"])
        denom = float(np.linalg.norm(row["actual"]) * np.linalg.norm(row["pred"]))
        cos += row["weight"] * (dot / denom if denom else 0.0)
        positive += row["weight"] * (dot > 0)
    return {"predictions": len(actual_predictions), "weight": weight,
            "fractional_mse_gain": 1 - error / zero if zero else 0.0,
            "mean_cosine": cos / weight, "positive_dot_rate": positive / weight}


def predictions(cases, mode: str, model: str):
    grouped = defaultdict(list)
    key_name = "operation" if model == "OP_SUBSTITUTION" else "source_target"
    for row in cases:
        key = row["operation"] if model == "OP_SUBSTITUTION" else (row["source"], row["target"])
        grouped[key].append(row)
    out = []
    for test in cases:
        key = test["operation"] if key_name == "operation" else (test["source"], test["target"])
        train = []
        for row in grouped[key]:
            if row is test:
                continue
            if model == "OP_SUBSTITUTION" and row["base_family"] == test["base_family"]:
                continue
            if mode == "HELD_BASE_AND_SECTION" and row["section"] == test["section"]:
                continue
            if mode == "HELD_BASE_AND_HAND" and row["hand"] == test["hand"]:
                continue
            train.append(row)
        if model == "OP_SUBSTITUTION":
            if len(train) < MIN_TRAIN_CASES or len({r["base_family"] for r in train}) < MIN_TRAIN_BASES:
                continue
        elif not train:
            continue
        out.append({"actual": test["delta"], "pred": mean(train), "weight": test["weight"], "operation": test["operation"]})
    return out


def primary(cases):
    rows = predictions(cases, "HELD_BASE", "OP_SUBSTITUTION")
    by_op = defaultdict(list)
    for row in rows:
        by_op[row["operation"]].append(row)
    return summarize(rows), {op: summarize(group) for op, group in by_op.items()}


def generic_voynich(rows):
    units = defaultdict(dict)
    for row in rows:
        units[row["locus"]][int(row["group_index"])] = row["page_host"]
    out = []
    for index in units.values():
        lo, hi = min(index), max(index)
        for pos, form in index.items():
            if len(form) not in LENGTHS:
                continue
            q = min(3, int(4 * (pos - lo) / max(1, hi - lo)))
            out.append({"identity": form, "prev_len": length_bin(index.get(pos - 1)),
                        "next_len": length_bin(index.get(pos + 1)), "unit_quartile": f"Q{q}"})
    return out


def generic_control(rows):
    units = defaultdict(dict)
    for row in rows:
        units[str(row["unit_id"])][int(row["occurrence_index"])] = unicodedata.normalize("NFC", str(row["form"]))
    out = []
    for index in units.values():
        lo, hi = min(index), max(index)
        for pos, form in index.items():
            if len(form) not in LENGTHS:
                continue
            q = min(3, int(4 * (pos - lo) / max(1, hi - lo)))
            out.append({"identity": form, "prev_len": length_bin(index.get(pos - 1)),
                        "next_len": length_bin(index.get(pos + 1)), "unit_quartile": f"Q{q}"})
    return out


def main() -> None:
    checks = []
    def check(name, condition):
        checks.append({"check": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    content = dict(result)
    recorded = content.pop("result_content_sha256")
    check("result_content_hash", csha(content) == recorded)
    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            check("hash:" + name, sha(ROOT / name) == digest)

    raw = tsv(SOURCE)
    check("actual_input_zero_f84r", not any(r["page"].startswith("f84r") or r["locus"].startswith("f84r") for r in raw))
    retained = [r for r in raw if not r["page"].startswith("f84") and not r["locus"].startswith("f84")]
    check("f84_guard", len(raw) - len(retained) == 228 and len(retained) == 15364)
    check("retained_zero_f84", not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in retained))
    candidate = [r for r in retained if len(r["page_host"]) in LENGTHS]
    labels = {r["page_host"]: r["page_host"] for r in candidate}
    check("short_host_capacity", len(candidate) == 5848 and len(labels) == 241)
    check("hamming_edges", len(edges(labels)) == 933)

    values = {block: sorted({r[block] for r in candidate}) for block in COMPONENTS}
    hvec, htot = vectorize(candidate, "page_host", ("section", "hand"), COMPONENTS, values)
    hcases = make_hpr_cases(labels, hvec, htot)
    check("hpr_case_capacity", len(hcases) == 660)
    check("operation_inventory", len({r["operation"] for r in hcases}) == 153 and sum(len(v) >= 4 for v in defaultdict(list, {k: [r for r in hcases if r["operation"] == k] for k in {r["operation"] for r in hcases}}).values()) == 65)

    # Refit operation and exact-pair predictions independently in every held mode.
    for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND"):
        for model in ("OP_SUBSTITUTION", "EXACT_PAIR_OTHER_STRATA"):
            got = summarize(predictions(hcases, mode, model))
            expected = result["hpr2_summaries"][mode + "|" + model]
            for metric in ("predictions", "weight", "fractional_mse_gain", "mean_cosine", "positive_dot_rate"):
                check(f"hpr:{mode}:{model}:{metric}", close(float(got[metric]), float(expected[metric])))

    hscore, hop = primary(hcases)
    check("primary_gain", close(hscore["fractional_mse_gain"], result["hpr2_summaries"]["HELD_BASE|OP_SUBSTITUTION"]["fractional_mse_gain"]))
    check("top_operation", max(hop, key=lambda x: hop[x]["fractional_mse_gain"]) == "L3:P3:a>y")

    # Rebuild every generic observed comparison from the common representation.
    generic_values = {"prev_len": ["MISSING", "L1", "L2", "L3", "L4P"],
                      "next_len": ["MISSING", "L1", "L2", "L3", "L4P"],
                      "unit_quartile": ["Q0", "Q1", "Q2", "Q3"]}
    payloads = {"VOYNICH_PAGE_HOST": generic_voynich(retained)}
    with gzip.open(CONTROL, "rt", encoding="utf-8") as handle:
        control_rows = json.load(handle)["records"]
    by_corpus = defaultdict(list)
    for row in control_rows:
        by_corpus[str(row["corpus_id"])].append(row)
    for corpus, rows in by_corpus.items():
        payloads[corpus] = generic_control(rows)
    comparator = {r["corpus_id"]: r for r in tsv(ROOT / "gdt163_comparator_scores.tsv")}
    objects = {}
    for corpus, occurrences in payloads.items():
        vec, tot = vectorize(occurrences, "identity", (), ("prev_len", "next_len", "unit_quartile"), generic_values)
        cmap = {r["identity"]: r["identity"] for r in occurrences}
        cases = make_generic_cases(cmap, vec, tot)
        score, per_op = primary(cases)
        row = comparator[corpus]
        check("generic_occurrences:" + corpus, int(row["occurrences"]) == len(occurrences))
        check("generic_edges:" + corpus, int(row["hamming1_edges"]) == len(edges(cmap)))
        check("generic_cases:" + corpus, int(row["eligible_cases"]) == len(cases))
        check("generic_predictions:" + corpus, int(row["op_predictions"]) == score["predictions"])
        check("generic_gain:" + corpus, close(float(row["op_fractional_mse_gain"]), score["fractional_mse_gain"]))
        check("generic_cosine:" + corpus, close(float(row["op_mean_cosine"]), score["mean_cosine"]))
        check("generic_top:" + corpus, close(float(row["best_operation_gain"]), max((x["fractional_mse_gain"] for x in per_op.values()), default=0.0)))
        objects[corpus] = (cmap, vec, tot)

    # Reconstruct all 1,024 HPR null worlds independently.
    exported_null = defaultdict(dict)
    for row in tsv(ROOT / "gdt163_null_results.tsv"):
        exported_null[row["corpus_id"]][int(row["world"])] = row
    rng = random.Random(rng_seed("GDT163_NULL_VOYNICH_HPR2_OUTER"))
    hgains, htops = [], []
    for world in range(WORLDS):
        mapping = permuted(labels, rng)
        score, pops = primary(make_hpr_cases(mapping, hvec, htot))
        top = max((x["fractional_mse_gain"] for x in pops.values()), default=0.0)
        hgains.append(score["fractional_mse_gain"]); htops.append(top)
        exported = exported_null["VOYNICH_HPR2_OUTER"][world]
        check(f"hpr_null_gain:{world}", close(float(exported["op_fractional_mse_gain"]), score["fractional_mse_gain"]))
        check(f"hpr_null_top:{world}", close(float(exported["top_operation_fractional_mse_gain"]), top))
    hp = (1 + sum(x >= hscore["fractional_mse_gain"] - 1e-12 for x in hgains)) / (WORLDS + 1)
    htop_obs = max(x["fractional_mse_gain"] for x in hop.values())
    hmp = (1 + sum(x >= htop_obs - 1e-12 for x in htops)) / (WORLDS + 1)
    check("hpr_null_local_p", close(hp, result["hpr2_null"]["aggregate_local_p"]))
    check("hpr_null_maxT_p", close(hmp, result["hpr2_null"]["top_operation_maxT_p"]))
    check("hpr_null_mean", close(sum(hgains) / WORLDS, result["hpr2_null"]["null_aggregate_mean"]))

    # Independently replay selected historical worlds and verify every exported p arithmetic.
    selected = {0, 511, 1023}
    for corpus, (cmap, vec, tot) in objects.items():
        if corpus == "VOYNICH_PAGE_HOST":
            pass
        rng = random.Random(rng_seed("GDT163_NULL_" + corpus))
        for world in range(WORLDS):
            mapping = permuted(cmap, rng)
            if world not in selected:
                continue
            score, pops = primary(make_generic_cases(mapping, vec, tot))
            top = max((x["fractional_mse_gain"] for x in pops.values()), default=0.0)
            exported = exported_null[corpus][world]
            check(f"generic_null_gain:{corpus}:{world}", close(float(exported["op_fractional_mse_gain"]), score["fractional_mse_gain"]))
            check(f"generic_null_top:{corpus}:{world}", close(float(exported["top_operation_fractional_mse_gain"]), top))
        null_rows = list(exported_null[corpus].values())
        observed = comparator[corpus]
        gain = float(observed["op_fractional_mse_gain"]); top = float(observed["best_operation_gain"])
        local = (1 + sum(float(r["op_fractional_mse_gain"]) >= gain - 1e-12 for r in null_rows)) / (WORLDS + 1)
        maxt = (1 + sum(float(r["top_operation_fractional_mse_gain"]) >= top - 1e-12 for r in null_rows)) / (WORLDS + 1)
        check("generic_null_p:" + corpus, close(local, float(observed["null_local_p"])))
        check("generic_maxT_p:" + corpus, close(maxt, float(observed["best_operation_maxT_p"])))

    check("null_row_count", sum(len(x) for x in exported_null.values()) == 7 * WORLDS)
    check("prediction_row_counts", len(tsv(ROOT / "gdt163_hpr2_predictions.tsv")) == 4284 and len(tsv(ROOT / "gdt163_generic_predictions.tsv")) == 6793)
    check("decision", result["status"] == "PRODUCTIVE_INTERNAL_SUBSTITUTION_TRANSFER_INTERESTING")
    check("identity_stronger_than_operation", float(result["hpr2_summaries"]["HELD_BASE|EXACT_PAIR_OTHER_STRATA"]["fractional_mse_gain"]) > hscore["fractional_mse_gain"])
    check("generic_absolute_negative", float(comparator["VOYNICH_PAGE_HOST"]["op_fractional_mse_gain"]) < 0)
    check("claim_ceiling", "translation" in result["claim_ceiling"] and not result["f84r"]["opened"] and not result["f84r"]["scored"])

    validation = {
        "schema": "GDT163_SUBSTITUTION_CONTEXT_TRANSFER_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_SOURCE_SCORE_HPR_NULL_AND_HISTORICAL_SAMPLE_RECONSTRUCTION",
        "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
        "result_sha256": sha(RESULT), "result_content_sha256": result["result_content_sha256"],
        "validator_sha256": sha(Path(__file__)),
        "scope_note": "All observed HPR2 and historical scores and the complete 1024-world HPR2 null were independently rebuilt. Three deterministic worlds per generic corpus plus all exported generic p-value arithmetic were independently checked."
    }
    validation["validation_content_sha256"] = csha(validation)
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": len(checks),
                      "hpr_gain": hscore["fractional_mse_gain"], "hpr_p": hp, "hpr_maxT_p": hmp}, sort_keys=True))


if __name__ == "__main__":
    main()
