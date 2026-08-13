#!/usr/bin/env python3
"""Frequent complete groups emitting one or two plaintext letters."""

import csv, hashlib, json, math
from collections import Counter

import numpy as np

from gdt001_core import ROOT, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES, train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_expanding_abbreviation import CODE_COUNT, decode
from run_gdt001_group_character_code import encoded


KS = (16, 32, 64, 128)


def sufficient(seqs, k):
    counts = np.zeros(k); events = Counter()
    for seq in seqs:
        history = [k, k]
        for token in seq:
            events[tuple(history) + (token,)] += 1; counts[token] += 1; history = [history[1], token]
    return np.asarray(list(events), dtype=np.int64), np.asarray(list(events.values()), dtype=np.float64), counts


def cpu_scores(lm, keys, freq, counts, maps):
    output = []
    for mapping in maps:
        value = 0.0
        for (a, b, c), n in zip(keys, freq):
            def emit(x): return (27,) if x == len(mapping) else decode(int(mapping[x]))
            ea, eb, ec = emit(a), emit(b), emit(c); history = (ea + eb)[-2:]
            value += n * lm.costs[history[0], history[1], ec[0]]
            if len(ec) == 2: value += n * lm.costs[history[1], ec[0], ec[1]]
        groups = {}
        for source, code in enumerate(mapping): groups.setdefault(int(code), []).append(source)
        value += sum(categorical_bits([int(counts[source]) for source in sources]) for sources in groups.values())
        n2 = sum(counts[source] for source, code in enumerate(mapping) if code >= 26); n1 = counts.sum() - n2
        value += categorical_bits([int(n1), int(n2)]); output.append(value)
    return np.asarray(output)


def gpu_scores(lm, keys_np, freq_np, counts_np, maps):
    import torch
    keys = torch.as_tensor(keys_np, device="cuda"); freq = torch.as_tensor(freq_np, device="cuda", dtype=torch.float64)
    costs = torch.as_tensor(lm.costs, device="cuda", dtype=torch.float64); counts = torch.as_tensor(counts_np, device="cuda", dtype=torch.float64); output = []
    k = maps.shape[1]
    for start in range(0, len(maps), 512):
        mapping = torch.as_tensor(maps[start:start + 512], device="cuda"); n = len(mapping)
        extended = torch.cat([mapping, torch.full((n, 1), -2, device="cuda")], 1)
        codes = [extended[:, keys[:, i]] for i in range(3)]
        def parts(code):
            bos = code == -2; two = code >= 26
            first = torch.where(bos, 27, torch.where(two, (code - 26) // 26, code))
            second = torch.where(two, (code - 26) % 26, first)
            return first, second, two
        af, a2, at = parts(codes[0]); bf, b2, bt = parts(codes[1]); cf, c2, ct = parts(codes[2])
        h1 = torch.where(bt, b2, bf); h0 = torch.where(bt, bf, torch.where(at, a2, af))
        values = (costs[h0, h1, cf] * freq).sum(1) + (costs[h1, cf, c2] * freq * ct).sum(1)
        multiplicity = torch.zeros((n, CODE_COUNT), device="cuda", dtype=torch.float64); totals = torch.zeros_like(multiplicity); members = torch.zeros_like(multiplicity)
        multiplicity.scatter_add_(1, mapping, torch.ones_like(mapping, dtype=torch.float64)); totals.scatter_add_(1, mapping, counts.expand(n, -1))
        constants = torch.lgamma(counts + .5) - torch.lgamma(torch.tensor(.5, device="cuda", dtype=torch.float64)); members.scatter_add_(1, mapping, constants.expand(n, -1))
        logp = torch.lgamma(.5 * multiplicity) - torch.lgamma(totals + .5 * multiplicity) + members
        values += torch.where(multiplicity > 0, -logp / math.log(2), 0).sum(1)
        n2 = ((mapping >= 26) * counts).sum(1); n1 = counts.sum() - n2
        values += (-torch.lgamma(torch.tensor(1., device="cuda")) + torch.lgamma(n1 + n2 + 1.) - torch.lgamma(n1 + .5) - torch.lgamma(n2 + .5) + 2 * torch.lgamma(torch.tensor(.5, device="cuda"))) / math.log(2)
        output.append(values.cpu().numpy())
    return np.concatenate(output)


def search(lm, keys, freq, counts, seed, population=4096, generations=12):
    rng = np.random.default_rng(seed); k = len(counts)
    pop = rng.integers(0, CODE_COUNT, size=(population, k), dtype=np.int64)
    for _ in range(generations):
        scores = gpu_scores(lm, keys, freq, counts, pop); elite = pop[np.argsort(scores)[:128]].copy()
        children = elite[rng.integers(0, 128, len(pop) - 128)].copy(); rows = np.arange(len(children))
        positions = rng.integers(0, k, len(children)); children[rows, positions] = rng.integers(0, CODE_COUNT, len(children))
        pop = np.vstack([elite, children])
    scores = gpu_scores(lm, keys, freq, counts, pop); index = int(np.argmin(scores))
    exact = float(cpu_scores(lm, keys, freq, counts, pop[index:index + 1])[0]); assert abs(exact - scores[index]) < 2e-6
    return exact, pop[index]


def line_structure(paths):
    counts = Counter(len(path.words) for path in paths); maximum = max(counts)
    return universal_uint_bits(maximum) + categorical_bits([counts[i] for i in range(maximum + 1)])


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values())
    symbols = sum(len(w) for p in paths for w in p.words); line_bits = line_structure(paths)
    leader = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]
    rows = []; mappings = []; screen = []
    for k in KS:
        seqs, _, _, vocab, _, common = encoded(paths, k); common += line_bits
        keys, freq, counts = sufficient(seqs, k); matched_payload = kt_ngram_bits(seqs, k, 2)
        null_key = 3.0 + math.log2(len(KS)) + universal_uint_bits(2) + common
        null_total = fixed + null_key + matched_payload
        rows.append({"model": "MATCHED_GROUP_NULL", "k": k, "language": "_", "seed": 0,
                     "total_bits": null_total, "bits_per_symbol": null_total / symbols,
                     "gap_vs_matched_null_bits": 0.0, "gap_vs_context_axis_bits": null_total - leader["total_bits"],
                     "key_bits": null_key, "payload_bits": matched_payload, "fixed_bits": fixed,
                     "decoder_hash": hashlib.sha256(canonical({"vocab": vocab, "order": 2})).hexdigest(), "cpu_exact": True})
        for language in PACK_NAMES:
            bits, mapping = search(train_pack(language, 2), keys, freq, counts, 31101)
            key = 3.0 + math.log2(len(KS)) + math.log2(len(PACK_NAMES)) + universal_uint_bits(2) + common + k * math.log2(CODE_COUNT)
            total = fixed + key + bits
            mapping_rows = [{"source_group": vocab[i], "plaintext": "".join(chr(97 + x) for x in decode(int(code))),
                             "occurrences": int(counts[i])} for i, code in enumerate(mapping)]
            digest = hashlib.sha256(canonical(mapping_rows)).hexdigest()
            item = {"model": "GROUP_EXPANSION_LANGUAGE", "k": k, "language": language, "seed": 31101,
                    "total_bits": total, "bits_per_symbol": total / symbols,
                    "gap_vs_matched_null_bits": total - null_total, "gap_vs_context_axis_bits": total - leader["total_bits"],
                    "key_bits": key, "payload_bits": bits, "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
            rows.append(item); screen.append(item); mappings.append(item | {"mapping": mapping_rows})
    winner = min(screen, key=lambda r: r["total_bits"]); seqs, _, _, vocab, _, common = encoded(paths, winner["k"]); common += line_bits
    keys, freq, counts = sufficient(seqs, winner["k"]); lm = train_pack(winner["language"], 2)
    null_total = next(r["total_bits"] for r in rows if r["model"] == "MATCHED_GROUP_NULL" and r["k"] == winner["k"])
    for seed in (31102, 31103):
        bits, mapping = search(lm, keys, freq, counts, seed); key = 3.0 + math.log2(len(KS)) + math.log2(len(PACK_NAMES)) + universal_uint_bits(2) + common + winner["k"] * math.log2(CODE_COUNT); total = fixed + key + bits
        mapping_rows = [{"source_group": vocab[i], "plaintext": "".join(chr(97 + x) for x in decode(int(code))), "occurrences": int(counts[i])} for i, code in enumerate(mapping)]
        digest = hashlib.sha256(canonical(mapping_rows)).hexdigest(); item = {"model": "GROUP_EXPANSION_LANGUAGE", "k": winner["k"], "language": winner["language"], "seed": seed,
                "total_bits": total, "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total, "gap_vs_context_axis_bits": total - leader["total_bits"],
                "key_bits": key, "payload_bits": bits, "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
        rows.append(item); mappings.append(item | {"mapping": mapping_rows})
    best = min((r for r in rows if r["model"] == "GROUP_EXPANSION_LANGUAGE"), key=lambda r: r["total_bits"])
    same = [r for r in rows if r["model"] == "GROUP_EXPANSION_LANGUAGE" and r["k"] == winner["k"] and r["language"] == winner["language"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_GROUP_EXPANSION_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_GROUP_EXPANSION_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory complete-group one/two-letter expansion only; no group, letter, language, plaintext, or translation is established."}
    (ROOT / "gdt001_group_expansion_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_group_expansion_mappings.json").write_bytes(canonical({"schema": "GDT001_GROUP_EXPANSION_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_group_expansion_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__":
    main()
