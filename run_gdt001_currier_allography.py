#!/usr/bin/env python3
"""Search a reversible Currier-B-to-shared-latent alphabet permutation."""

import csv, hashlib, json, math, random
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


BASE = BCOUNTS = LOOKUP = None
ALPHABET = ACTIVE = 0


def tensor_cost(counts):
    totals = counts.sum(axis=2)
    return float((LOOKUP["total"][totals].sum() - LOOKUP["cell"][counts].sum()) / math.log(2.0))


def score_perm(perm):
    context_map = np.arange(ALPHABET + 1); token_map = np.arange(ALPHABET)
    context_map[:ACTIVE] = perm; token_map[:ACTIVE] = perm
    transformed = np.zeros_like(BCOUNTS)
    transformed[np.ix_(context_map, context_map, token_map)] = BCOUNTS
    return tensor_cost(BASE + transformed)


def search(seed):
    rng = random.Random(seed); perm = list(range(ACTIVE)); rng.shuffle(perm)
    score = score_perm(perm); best_score = score; best = tuple(perm); accepted = 0
    for step in range(6000):
        i, j = rng.sample(range(ACTIVE), 2); perm[i], perm[j] = perm[j], perm[i]
        proposal = score_perm(perm); temperature = max(0.02, 3.0 * (1.0 - step / 6000.0))
        if proposal <= score or rng.random() < math.exp((score - proposal) / temperature):
            score = proposal; accepted += 1
            if score < best_score: best_score = score; best = tuple(perm)
        else: perm[i], perm[j] = perm[j], perm[i]
    return {"seed": seed, "payload_bits": best_score, "permutation": list(best), "accepted_moves": accepted}


def main():
    global BASE, BCOUNTS, LOOKUP, ALPHABET, ACTIVE
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words)
    source = json.loads((ROOT / "gdt001_source_selected_null_results.json").read_text())["selected_source_null"]
    context = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    nulls = frozenset(source["null_symbols"]); seqs, _, _, active, _, side = encoded(paths, nulls)
    ACTIVE = len(active); ALPHABET = ACTIVE + 1; bos = ALPHABET
    BASE = np.zeros((ALPHABET + 1, ALPHABET + 1, ALPHABET), dtype=np.int64); BCOUNTS = np.zeros_like(BASE)
    for line, seq in zip(lines, seqs):
        target = BCOUNTS if line.currier == "B" else BASE; history = [bos, bos]
        for token in seq:
            target[history[0], history[1], token] += 1; history = [history[1], token]
    maximum = int((BASE + BCOUNTS).sum())
    cell = np.array([math.lgamma(i + .5) - math.lgamma(.5) for i in range(maximum + 1)])
    total = np.array([math.lgamma(i + ALPHABET * .5) - math.lgamma(ALPHABET * .5) for i in range(maximum + 1)])
    LOOKUP = {"cell": cell, "total": total}
    seeds = list(range(27101, 27117))
    with ProcessPoolExecutor(max_workers=16) as pool: searches = list(pool.map(search, seeds))
    rare_key = universal_uint_bits(len(nulls)) + math.log2(math.comb(len(LETTERS), len(nulls)))
    permutation_key = math.lgamma(ACTIVE + 1) / math.log(2.0)
    key = 3.0 + math.log2(2) + rare_key + permutation_key + universal_uint_bits(2)
    rows = []; mappings = []
    for item in searches:
        total_bits = fixed + side + key + item["payload_bits"]
        mapping = [{"currier_b_source": active[i], "shared_latent": active[item["permutation"][i]]} for i in range(ACTIVE)]
        decoder = {"schema": "GDT001_CURRIER_ALLOGRAPHY_DECODER_V1", "currier_a_and_unknown": "IDENTITY",
                   "currier_b_permutation": mapping, "rare_symbols": source["null_symbols"], "order": 2,
                   "reconstruction": "apply the inverse frozen Currier-B permutation and then restore the ordered rare-event channel"}
        digest = hashlib.sha256(canonical(decoder)).hexdigest()
        row = {"seed": item["seed"], "total_bits": total_bits, "bits_per_symbol": total_bits / symbols,
               "gap_vs_source_winner_bits": total_bits - source["total_bits"],
               "gap_vs_context_axis_bits": total_bits - context["total_bits"], "key_bits": key,
               "side_channel_bits": side, "payload_bits": item["payload_bits"], "fixed_bits": fixed,
               "accepted_moves": item["accepted_moves"], "decoder_hash": digest, "cpu_exact": True}
        rows.append(row); mappings.append({"seed": item["seed"], "decoder_hash": digest, "mapping": mapping})
    winner = min(rows, key=lambda x: x["total_bits"]); stability = len({r["decoder_hash"] for r in rows})
    decision = ("CONTINUE" if winner["gap_vs_context_axis_bits"] < 0 else "STOP") + "_CURRIER_ALLOGRAPHY_" + ("STABLE" if stability == 1 else "UNSTABLE")
    result = {"schema": "GDT001_CURRIER_ALLOGRAPHY_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": winner, "unique_decoder_hashes": stability, "rows": rows,
              "claim_ceiling": "Exploratory reversible source-to-source alphabet normalization only; no allograph, sound, language, meaning, or plaintext is established."}
    (ROOT / "gdt001_currier_allography_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_currier_allography_mappings.json").write_bytes(canonical({"schema": "GDT001_CURRIER_ALLOGRAPHY_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_currier_allography_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": winner, "unique_decoders": stability}))


if __name__ == "__main__":
    main()
