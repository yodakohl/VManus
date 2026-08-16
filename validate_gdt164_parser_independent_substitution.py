#!/usr/bin/env python3
"""Independent validation of GDT164 source firewall, scores, nulls, and seal."""
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
RESULT = ROOT / "gdt164_result.json"
VALIDATION = ROOT / "gdt164_validation.json"
LENGTHS = (2, 3)
BLOCKS = ("prev_hash", "next_hash", "prev_len", "next_len", "prev_freq", "next_freq",
          "from_start", "to_end", "unit_quartile", "unit_span")
WORLDS = 1024
MIN_COUNT = 2
MIN_CASES = 4
MIN_TRAIN = 3
MIN_BASES = 2


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def close(a: float, b: float, tol: float = 3e-9) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hbucket(value: str) -> str:
    return f"H{int(hashlib.sha256(value.encode()).hexdigest()[:8], 16) % 32:02d}"


def lclass(value: str | None) -> str:
    if value is None:
        return "MISSING"
    n = len(value)
    return "L1" if n == 1 else "L2" if n == 2 else "L3" if n == 3 else "L4P"


def fclass(n: int | None) -> str:
    if n is None:
        return "MISSING"
    return "R1" if n == 1 else "R2_4" if n <= 4 else "R5_15" if n <= 15 else "R16P"


def dclass(n: int) -> str:
    return str(n) if n < 3 else "3P"


def sclass(n: int) -> str:
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def external(rows):
    counts = Counter(r["identity"] for r in rows)
    units = defaultdict(dict)
    for row in rows:
        units[row["unit"]][int(row["index"])] = row
    out = []
    for index in units.values():
        lo, hi = min(index), max(index)
        for pos, row in index.items():
            if len(row["identity"]) not in LENGTHS:
                continue
            before = index.get(pos - 1)
            after = index.get(pos + 1)
            p = before["identity"] if before else None
            n = after["identity"] if after else None
            q = min(3, int(4 * (pos - lo) / max(1, hi - lo)))
            out.append({**row, "prev_hash": hbucket(p) if p else "MISSING",
                        "next_hash": hbucket(n) if n else "MISSING",
                        "prev_len": lclass(p), "next_len": lclass(n),
                        "prev_freq": fclass(counts[p]) if p else "MISSING",
                        "next_freq": fclass(counts[n]) if n else "MISSING",
                        "from_start": dclass(pos - lo), "to_end": dclass(hi - pos),
                        "unit_quartile": f"Q{q}", "unit_span": sclass(hi - lo + 1)})
    return out


def vectors(rows):
    values = {block: sorted({r[block] for r in rows}) for block in BLOCKS}
    dims = [(block, value) for block in BLOCKS for value in values[block]]
    sizes = {block: len(values[block]) for block in BLOCKS}
    totals = Counter()
    cats = Counter()
    for row in rows:
        key = row["identity"], row["stratum1"], row["stratum2"]
        totals[key] += 1
        for block in BLOCKS:
            cats[key, block, row[block]] += 1
    vec = {key: np.array([(cats[key, block, value] + .5) / (n + .5 * sizes[block])
                          for block, value in dims]) for key, n in totals.items()}
    return vec, totals, [f"{a}={b}" for a, b in dims]


def edge_list(mapping):
    buckets = defaultdict(list)
    for identity, form in mapping.items():
        if len(form) not in LENGTHS:
            continue
        for pos in range(len(form)):
            buckets[len(form), pos, form[:pos] + "*" + form[pos + 1:]].append(identity)
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
                            "base": f"L{length}:P{pos + 1}:{base}"})
    return out


def cases(mapping, vec, totals):
    strata = defaultdict(set)
    for identity, s1, s2 in vec:
        strata[identity].add((s1, s2))
    out = []
    for edge in edge_list(mapping):
        for s1, s2 in strata[edge["source"]] & strata[edge["target"]]:
            a = edge["source"], s1, s2
            b = edge["target"], s1, s2
            if totals[a] < MIN_COUNT or totals[b] < MIN_COUNT:
                continue
            out.append({**edge, "s1": s1, "s2": s2, "weight": float(min(20, totals[a], totals[b])),
                        "delta": vec[b] - vec[a]})
    return out


def mean(rows):
    return np.average(np.stack([r["delta"] for r in rows]), axis=0,
                      weights=np.array([r["weight"] for r in rows]))


def result_row(test, prediction):
    actual = test["delta"]
    dot = float(actual @ prediction)
    denom = float(np.linalg.norm(actual) * np.linalg.norm(prediction))
    return {"operation": test["operation"], "weight": test["weight"],
            "zero": float(actual @ actual), "error": float((actual - prediction) @ (actual - prediction)),
            "cosine": dot / denom if denom else 0.0, "positive": dot > 0}


def predict(all_cases, mode, model):
    group = defaultdict(list)
    for row in all_cases:
        key = row["operation"] if model == "OP_SUBSTITUTION" else (row["source"], row["target"])
        group[key].append(row)
    out = []
    for test in all_cases:
        key = test["operation"] if model == "OP_SUBSTITUTION" else (test["source"], test["target"])
        train = []
        for row in group[key]:
            if row is test:
                continue
            if model == "OP_SUBSTITUTION" and row["base"] == test["base"]:
                continue
            if mode in ("HELD_BASE_AND_SECTION", "HELD_BASE_AND_FOLD") and row["s1"] == test["s1"]:
                continue
            if mode == "HELD_BASE_AND_HAND" and row["s2"] == test["s2"]:
                continue
            train.append(row)
        if model == "OP_SUBSTITUTION" and (len(train) < MIN_TRAIN or len({r["base"] for r in train}) < MIN_BASES):
            continue
        if model != "OP_SUBSTITUTION" and not train:
            continue
        out.append(result_row(test, mean(train)))
    return out


def summary(rows):
    if not rows:
        return {"predictions": 0, "weight": 0.0, "fractional_mse_gain": 0.0,
                "mean_cosine": 0.0, "positive_dot_rate": 0.0}
    weight = sum(r["weight"] for r in rows)
    zero = sum(r["weight"] * r["zero"] for r in rows)
    error = sum(r["weight"] * r["error"] for r in rows)
    return {"predictions": len(rows), "weight": weight, "fractional_mse_gain": 1 - error / zero,
            "mean_cosine": sum(r["weight"] * r["cosine"] for r in rows) / weight,
            "positive_dot_rate": sum(r["weight"] * r["positive"] for r in rows) / weight}


def primary(all_cases):
    rows = predict(all_cases, "HELD_BASE", "OP_SUBSTITUTION")
    by = defaultdict(list)
    for row in rows:
        by[row["operation"]].append(row)
    return summary(rows), {op: summary(group) for op, group in by.items()}


def random_map(labels, rng):
    out = {identity: [""] * len(form) for identity, form in labels.items()}
    for length in LENGTHS:
        identities = sorted(x for x in labels if len(labels[x]) == length)
        for pos in range(length):
            glyphs = [labels[x][pos] for x in identities]
            rng.shuffle(glyphs)
            for identity, glyph in zip(identities, glyphs):
                out[identity][pos] = glyph
    return {identity: "".join(chars) for identity, chars in out.items()}


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
    for group_name in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group_name].items():
            check("hash:" + name, sha(ROOT / name) == digest)

    raw = read_tsv(SOURCE)
    check("source_zero_f84r", not any(r["page"].startswith("f84r") or r["locus"].startswith("f84r") for r in raw))
    kept_raw = [r for r in raw if not r["page"].startswith("f84") and not r["locus"].startswith("f84")]
    check("f84_guard_counts", len(raw) == 15592 and len(kept_raw) == 15364 and len(raw) - len(kept_raw) == 228)
    minimal = [{"identity": r["page_host"], "unit": r["locus"], "index": r["group_index"],
                "stratum1": r["section"], "stratum2": r["hand"], "corpus_id": "VOYNICH_PAGE_HOST"}
               for r in kept_raw]
    payloads = {"VOYNICH_PAGE_HOST": minimal}
    with gzip.open(CONTROL, "rt", encoding="utf-8") as handle:
        controls = json.load(handle)["records"]
    by = defaultdict(list)
    for row in controls:
        corpus = str(row["corpus_id"])
        by[corpus].append({"identity": unicodedata.normalize("NFC", str(row["form"])),
                           "unit": str(row["unit_id"]), "index": str(row["occurrence_index"]),
                           "stratum1": str(row["fold_id"]), "stratum2": "ALL", "corpus_id": corpus})
    payloads.update(by)

    exported = {r["corpus_id"]: r for r in read_tsv(ROOT / "gdt164_comparator_scores.tsv")}
    null_export = defaultdict(dict)
    for row in read_tsv(ROOT / "gdt164_null_results.tsv"):
        null_export[row["corpus_id"]][int(row["world"])] = row
    built = {}
    for corpus, base_rows in payloads.items():
        occurrences = external(base_rows)
        vec, totals, dims = vectors(occurrences)
        labels = {r["identity"]: r["identity"] for r in occurrences}
        cs = cases(labels, vec, totals)
        built[corpus] = labels, vec, totals, cs
        row = exported[corpus]
        check("occurrences:" + corpus, len(occurrences) == int(row["occurrences"]))
        check("types:" + corpus, len(labels) == int(row["types"]))
        check("edges:" + corpus, len(edge_list(labels)) == int(row["hamming1_edges"]))
        check("cells:" + corpus, len(cs) == int(row["eligible_cells"]))
        modes = ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND") if corpus == "VOYNICH_PAGE_HOST" else ("HELD_BASE", "HELD_BASE_AND_FOLD")
        for mode in modes:
            for model in ("OP_SUBSTITUTION", "EXACT_PAIR_OTHER_STRATA"):
                got = summary(predict(cs, mode, model))
                prefix = mode.lower() + "_" + model.lower() + "_"
                for metric in ("predictions", "weight", "fractional_mse_gain", "mean_cosine", "positive_dot_rate"):
                    expected = (result["voynich_summaries"][mode + "|" + model][metric]
                                if corpus == "VOYNICH_PAGE_HOST" else row[prefix + metric])
                    check(f"score:{corpus}:{mode}:{model}:{metric}", close(float(got[metric]), float(expected)))
        if corpus == "VOYNICH_PAGE_HOST":
            check("external_dimensions", dims == result["external_context_dimensions"] and len(dims) == 104)

    # Complete independent recreation of all six 1,024-world null families.
    for corpus, (labels, vec, totals, _) in built.items():
        rng = random.Random(int(hashlib.sha256(("GDT164_NULL_" + corpus).encode()).hexdigest()[:16], 16))
        gains = []
        tops = []
        for world in range(WORLDS):
            score, per_op = primary(cases(random_map(labels, rng), vec, totals))
            top = max((r["fractional_mse_gain"] for r in per_op.values()), default=0.0)
            gains.append(score["fractional_mse_gain"])
            tops.append(top)
            saved = null_export[corpus][world]
            check(f"null_gain:{corpus}:{world}", close(float(saved["op_fractional_mse_gain"]), score["fractional_mse_gain"]))
            check(f"null_top:{corpus}:{world}", close(float(saved["top_operation_fractional_mse_gain"]), top))
        observed = exported[corpus]
        gain = float(observed["held_base_op_substitution_fractional_mse_gain"])
        top = float(observed["best_operation_gain"])
        p = (1 + sum(x >= gain - 1e-12 for x in gains)) / (WORLDS + 1)
        mp = (1 + sum(x >= top - 1e-12 for x in tops)) / (WORLDS + 1)
        check("null_p:" + corpus, close(p, float(observed["null_local_p"])))
        check("null_maxT:" + corpus, close(mp, float(observed["best_operation_maxT_p"])))
        check("null_mean:" + corpus, close(sum(gains) / WORLDS, float(observed["null_mean_gain"])))

    predictions_header = set(read_tsv(ROOT / "gdt164_external_context_predictions.tsv")[0])
    forbidden = {"token", "wrapper", "inner_d", "local_frame", "right_family", "dy_closure", "b3"}
    check("prediction_firewall", not (predictions_header & forbidden))
    check("null_row_count", sum(len(x) for x in null_export.values()) == 6 * WORLDS)
    check("result_decision", result["status"] == "PARSER_INDEPENDENT_SUBSTITUTION_NOT_SUPPORTED")
    check("negative_three_modes", all(float(result["voynich_summaries"][mode + "|OP_SUBSTITUTION"]["fractional_mse_gain"]) < 0 for mode in ("HELD_BASE", "HELD_BASE_AND_SECTION", "HELD_BASE_AND_HAND")))
    ops = {r["operation"]: r for r in read_tsv(ROOT / "gdt164_operation_scores.tsv")}
    check("gdt163_top_collapse", float(ops["L3:P3:a>y"]["held_base_fractional_mse_gain"]) < 0 and float(ops["L3:P3:a>y"]["held_base_and_section_fractional_mse_gain"]) < 0 and float(ops["L3:P3:a>y"]["held_base_and_hand_fractional_mse_gain"]) < 0)
    check("claim_and_seal", "translation" in result["claim_ceiling"] and not any(result["f84r"].values()))

    validation = {"schema": "GDT164_PARSER_INDEPENDENT_SUBSTITUTION_VALIDATION_V1",
                  "status": "PASS_INDEPENDENT_SOURCE_FIREWALL_SCORE_NULL_AND_SEAL_RECONSTRUCTION",
                  "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
                  "result_sha256": sha(RESULT), "result_content_sha256": result["result_content_sha256"],
                  "validator_sha256": sha(Path(__file__))}
    validation["validation_content_sha256"] = csha(validation)
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": len(checks),
                      "base_gain": result["voynich_summaries"]["HELD_BASE|OP_SUBSTITUTION"]["fractional_mse_gain"],
                      "null_p": result["voynich_null"]["aggregate_local_p"]}, sort_keys=True))


if __name__ == "__main__":
    main()
