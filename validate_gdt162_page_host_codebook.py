#!/usr/bin/env python3
"""Independent validation of retained GDT162 data, scores, nulls, and seals."""
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

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
CONTROL_SOURCE = ROOT / "gdt159_diplomatic_corpora.json.gz"
RESULT = ROOT / "gdt162_result.json"
VALIDATION = ROOT / "gdt162_validation.json"
LENGTHS = (2, 3)
COMPONENTS = ("wrapper", "inner_d", "local_frame", "right_family", "dy_closure", "b3")
SMOOTH = 8.0
WORLDS = 1024


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a: float, b: float, tol: float = 2e-8) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def entropy(counts) -> float:
    vals = [int(x) for x in counts if x]; n = sum(vals)
    return -sum((x / n) * math.log2(x / n) for x in vals) if n else 0.0


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b)) if len(a) == len(b) else 99


def pairs(words: dict[str, str]) -> set[tuple[str, str]]:
    buckets = defaultdict(list)
    for ident, word in words.items():
        for pos in range(len(word)): buckets[len(word), pos, word[:pos] + "?" + word[pos + 1 :]].append(ident)
    out = set()
    for ids in buckets.values():
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                if words[a] != words[b] and hamming(words[a], words[b]) == 1: out.add(tuple(sorted((a, b))))
    return out


def cosine(a: list[float], b: list[float]) -> float:
    n = sum(x * y for x, y in zip(a, b)); d = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return n / d if d else 0.0


def vectors(rows: list[dict[str, str]]) -> dict[str, list[float]]:
    dims = [(c, y) for c in COMPONENTS for y in sorted({r[c] for r in rows})]
    n = Counter(r["page_host"] for r in rows); cell = Counter((r["page_host"], c, r[c]) for r in rows for c in COMPONENTS)
    return {h: [(cell[h, c, y] + 0.5) / (n[h] + 0.5 * sum(cc == c for cc, _ in dims)) for c, y in dims] for h in n}


def geometry(mapping: dict[str, str], vec: dict[str, list[float]]) -> dict[str, float]:
    edges = pairs(mapping); poss = sum(n * (n - 1) // 2 for n in [sum(len(s) == L for s in mapping.values()) for L in LENGTHS])
    classes = Counter(); sims = []; delta = defaultdict(list)
    for a, b in edges:
        wa, wb = mapping[a], mapping[b]; pos = next(i for i, (x, y) in enumerate(zip(wa, wb)) if x != y)
        lo, hi = sorted((wa[pos], wb[pos])); key = (len(wa), pos, lo, hi); classes[key] += 1
        sims.append(cosine(vec[a], vec[b])); va, vb = vec[a], vec[b]
        delta[key].append([y - x for x, y in zip(va, vb)] if wa[pos] == lo else [x - y for x, y in zip(va, vb)])
    cohs = []
    for ds in delta.values():
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)): cohs.append(cosine(ds[i], ds[j]))
    tcs = []
    for L in LENGTHS:
        forms = Counter(mapping[h] for h in mapping if len(mapping[h]) == L); pos = [Counter() for _ in range(L)]
        for h, s in mapping.items():
            if len(s) != L: continue
            for i, ch in enumerate(s): pos[i][ch] += 1
        tcs.append(sum(entropy(c.values()) for c in pos) - entropy(forms.values()))
    return {
        "slot_total_correlation_mean": sum(tcs) / 2,
        "neighbor_density": len(edges) / poss,
        "top20_substitution_share": sum(x for _, x in classes.most_common(20)) / len(edges),
        "neighbor_context_cosine": sum(sims) / len(sims),
        "substitution_delta_coherence": sum(cohs) / len(cohs),
        "collisions": float(len(mapping) - len(set(mapping.values()))),
    }


def random_map(labels: dict[str, str], mode: str, rng: random.Random) -> dict[str, str]:
    ids = sorted(labels); out = {h: [""] * len(labels[h]) for h in ids}
    if mode == "LENGTH_UNIGRAM":
        slots = [(h, p) for h in ids for p in range(len(labels[h]))]; glyphs = [labels[h][p] for h, p in slots]; rng.shuffle(glyphs)
        for (h, p), ch in zip(slots, glyphs): out[h][p] = ch
    else:
        for L in LENGTHS:
            group = [h for h in ids if len(labels[h]) == L]
            for p in range(L):
                glyphs = [labels[h][p] for h in group]; rng.shuffle(glyphs)
                for h, ch in zip(group, glyphs): out[h][p] = ch
    return {h: "".join(x) for h, x in out.items()}


def nuisance(row: dict[str, str]) -> tuple[str, ...]:
    return row["section"], row["currier"], row["hand"], str(len(row["page_host"])), row["position_quartile"]


def held_score(rows: list[dict[str, str]], fold_key: str) -> dict[str, float]:
    hostset = sorted({r["page_host"] for r in rows})
    neighbors = {h: {g for g in hostset if len(h) == len(g) and hamming(h, g) == 1} for h in hostset}
    totals = Counter()
    for held in sorted({r[fold_key] for r in rows}):
        train = [r for r in rows if r[fold_key] != held]; test = [r for r in rows if r[fold_key] == held]
        for c in COMPONENTS:
            ys = sorted({r[c] for r in rows}); global_c = Counter(r[c] for r in train)
            nc = Counter((nuisance(r), r[c]) for r in train); nn = Counter(nuisance(r) for r in train)
            hc = Counter((r["page_host"], r[c]) for r in train); hn = Counter(r["page_host"] for r in train)
            for row in test:
                y = row[c]; nk = nuisance(row); h = row["page_host"]
                pg = (global_c[y] + 0.5) / (len(train) + 0.5 * len(ys))
                pn = (nc[nk, y] + SMOOTH * pg) / (nn[nk] + SMOOTH)
                pe = (hc[h, y] + SMOOTH * pn) / (hn[h] + SMOOTH)
                z = neighbors[h]; nbn = sum(hn[q] for q in z); nby = sum(hc[q, y] for q in z)
                pnb = (nby + SMOOTH * pn) / (nbn + SMOOTH)
                totals["nuisance_bits"] -= math.log2(pn); totals["exact_host_bits"] -= math.log2(pe); totals["neighbor_bits"] -= math.log2(pnb)
    totals["exact_gain_vs_nuisance"] = totals["nuisance_bits"] - totals["exact_host_bits"]
    totals["neighbor_gain_vs_nuisance"] = totals["nuisance_bits"] - totals["neighbor_bits"]
    totals["exact_gain_vs_neighbor"] = totals["neighbor_bits"] - totals["exact_host_bits"]
    return dict(totals)


def main() -> None:
    checks = []
    def check(name: str, condition: bool) -> None:
        checks.append({"check": name, "pass": bool(condition)})
        if not condition: raise AssertionError(name)

    result = json.loads(RESULT.read_text(encoding="utf-8")); content = dict(result); got = content.pop("result_content_sha256")
    check("result_content_hash", csha(content) == got)
    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items(): check(f"hash:{name}", sha(ROOT / name) == digest)

    raw = read_tsv(SOURCE)
    check("actual_input_has_zero_f84r", sum(r["page"].startswith("f84r") or r["locus"].startswith("f84r") for r in raw) == 0)
    rows = [r for r in raw if not r["page"].startswith("f84") and not r["locus"].startswith("f84")]
    check("f84_guard_counts", len(raw) - len(rows) == 228 and len(rows) == 15364)
    check("retained_zero_f84", not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in rows))
    candidate = [r for r in rows if len(r["page_host"]) in LENGTHS and r["page_host"] != "EMPTY"]
    counts = Counter(r["page_host"] for r in candidate)
    check("short_capacity", len(candidate) == 5848 and len(counts) == 241)
    check("folio_capacity", len({r["physical_folio"] for r in rows}) == 93)

    # Inventory and length outputs.
    inv = read_tsv(ROOT / "gdt162_host_inventory.tsv")
    check("inventory_types", len(inv) == len(counts) and {r["page_host"]: int(r["occurrences"]) for r in inv} == counts)
    length = {r["representation"]: r for r in read_tsv(ROOT / "gdt162_length_recurrence.tsv")}
    all_hosts = [r["page_host"] for r in rows]; full_counts = Counter(all_hosts)
    check("page_host_short_mass", close(float(length["VOYNICH_PAGE_HOST"]["length_2_3_token_mass"]), len(candidate) / len(rows)))
    recurrent = sum(n for h, n in counts.items() if n >= 2)
    check("page_host_recurrent_coverage", close(float(length["VOYNICH_PAGE_HOST"]["short_recurrent_token_coverage"]), recurrent / len(candidate)))
    crossfolio = defaultdict(set)
    for r in candidate: crossfolio[r["page_host"]].add(r["physical_folio"])
    cf = sum(counts[h] for h in counts if len(crossfolio[h]) >= 2) / len(candidate)
    check("page_host_crossfolio_coverage", close(float(length["VOYNICH_PAGE_HOST"]["short_cross_fold_token_coverage"]), cf))

    # Historical control counts are rebuilt from the frozen gzip.
    with gzip.open(CONTROL_SOURCE, "rt", encoding="utf-8") as handle: controls = json.load(handle)["records"]
    by = defaultdict(list)
    for r in controls: by[r["corpus_id"]].append(unicodedata.normalize("NFC", r["form"]))
    for corpus, forms in by.items():
        row = length[corpus]; short = sum(len(f) in LENGTHS for f in forms)
        check(f"control_capacity:{corpus}", int(row["tokens"]) == len(forms))
        check(f"control_short_mass:{corpus}", close(float(row["length_2_3_token_mass"]), short / len(forms)))

    # Exact neighbor graph and reported atlas.
    labels = {h: h for h in counts}; edges = pairs(labels)
    atlas = read_tsv(ROOT / "gdt162_neighbor_substitutions.tsv")
    check("neighbor_edges", len(edges) == 933 and len(atlas) == 933)
    check("neighbor_pairs_exact", {tuple(sorted((r["host_a"], r["host_b"]))) for r in atlas} == edges)
    vec = vectors(candidate); obs = geometry(labels, vec)
    for key, value in result["observed_geometry"].items(): check("observed_geometry:" + key, close(float(value), obs[key]))

    # Independent held-fold refits.
    hf = held_score(candidate, "physical_folio"); hs = held_score(candidate, "section")
    for key in ("nuisance_bits", "exact_host_bits", "neighbor_bits", "exact_gain_vs_nuisance", "neighbor_gain_vs_nuisance", "exact_gain_vs_neighbor"):
        check("held_folio:" + key, close(float(result["held_folio_context"][key]), hf[key]))
        check("held_section:" + key, close(float(result["held_section_context"][key]), hs[key]))

    # Reconstruct the two geometry nulls independently, including key p-values.
    null_rows = {(r["null"], r["metric"]): r for r in read_tsv(ROOT / "gdt162_null_summary.tsv")}
    for mode in ("LENGTH_UNIGRAM", "POSITION_PRESERVING"):
        rng = random.Random(int(hashlib.sha256(("GDT162_" + mode).encode()).hexdigest()[:16], 16)); values = defaultdict(list)
        for _ in range(WORLDS):
            z = geometry(random_map(labels, mode, rng), vec)
            for key, value in z.items(): values[key].append(value)
        for metric in ("neighbor_density", "neighbor_context_cosine", "substitution_delta_coherence", "slot_total_correlation_mean", "collisions"):
            row = null_rows[mode, metric]
            check(f"null_mean:{mode}:{metric}", close(float(row["null_mean"]), sum(values[metric]) / WORLDS))
        for metric in ("neighbor_context_cosine", "substitution_delta_coherence"):
            p = (1 + sum(x >= obs[metric] - 1e-12 for x in values[metric])) / (WORLDS + 1)
            check(f"null_local_p:{mode}:{metric}", close(float(null_rows[mode, metric]["local_p"]), p))

    # Output and decision integrity.
    check("context_row_count", len(read_tsv(ROOT / "gdt162_context_transfer.tsv")) == 588)
    check("control_row_count", len(read_tsv(ROOT / "gdt162_historical_controls.tsv")) == 7)
    check("null_summary_row_count", len(null_rows) == 18)
    check("decision", result["status"] == "SHORT_HOST_INTERNAL_PRODUCTIVITY_INTERESTING" and result["decision_inputs"]["productive_rule"] and not result["decision_inputs"]["codebook_rule"])
    check("claim_ceiling", "translation" in result["claim_ceiling"] and not result["f84r"]["opened"] and not result["f84r"]["scored"])

    validation = {
        "schema": "GDT162_PAGE_HOST_CODEBOOK_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_SOURCE_SCORE_NULL_AND_SEAL_RECONSTRUCTION",
        "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
        "result_sha256": sha(RESULT), "result_content_sha256": result["result_content_sha256"],
        "validator_sha256": sha(Path(__file__)),
    }
    validation["validation_content_sha256"] = csha(validation)
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": len(checks), "neighbor_edges": len(edges), "exact_gain": hf["exact_gain_vs_nuisance"], "neighbor_gain": hf["neighbor_gain_vs_nuisance"]}, sort_keys=True))


if __name__ == "__main__":
    main()
