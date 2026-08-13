#!/usr/bin/env python3
"""Higher-order historical-language models for complete-group character codes."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import ROOT, TARGET_ALPHABET, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_character_code import encoded


LANGUAGES = ("latin", "old_italian_tuscan", "medieval_czech", "old_hungarian", "latin_scholastic")
KS = (128,)
ORDERS = (3, 4)


def lm(language, order, alpha=.5):
    size = len(TARGET_ALPHABET); counts = defaultdict(Counter); bos = size
    for raw in (ROOT / ".gdt001/language_packs" / f"{language}.txt").read_text().splitlines():
        history = [bos] * order
        for char in raw:
            token = TARGET_ALPHABET.index(char); counts[tuple(history)][token] += 1
            history = history[1:] + [token]
    table = {}
    for history, counter in counts.items():
        denominator = sum(counter.values()) + alpha * size
        table[history] = np.asarray([-math.log2((counter[i] + alpha) / denominator) for i in range(size)])
    return table


def sufficient(seqs, order, k):
    events = Counter()
    for seq in seqs:
        history = [k] * order
        for token in seq:
            events[tuple(history) + (token,)] += 1; history = history[1:] + [token]
    return np.asarray(list(events), dtype=np.int64), np.asarray(list(events.values()), dtype=np.float64)


def dense_costs(table, order):
    # Only histories observed in the source are ever requested after mapping;
    # a dict lookup CPU scorer is exact, while GPU batches gather flattened
    # target history IDs from a dense 28^order table.
    size = 28; shape = (size,) * order + (27,); output = np.full(shape, math.log2(27), dtype=np.float64)
    for history, costs in table.items(): output[history] = costs
    return output


def cpu(costs, keys, freq, counts, maps, order):
    result = []
    for mapping in maps:
        extended = np.concatenate([mapping, [27]]); target = extended[keys]
        value = float(np.sum(costs[tuple(target[:, i] for i in range(order + 1))] * freq))
        groups = defaultdict(list)
        for source, target_id in enumerate(mapping): groups[int(target_id)].append(source)
        value += sum(categorical_bits([int(counts[source]) for source in sources]) for sources in groups.values()); result.append(value)
    return np.asarray(result)


def gpu(costs_np, keys_np, freq_np, counts_np, maps, order):
    import torch
    keys = torch.as_tensor(keys_np, device="cuda"); freq = torch.as_tensor(freq_np, device="cuda", dtype=torch.float64)
    costs = torch.as_tensor(costs_np, device="cuda", dtype=torch.float64); counts = torch.as_tensor(counts_np, device="cuda", dtype=torch.float64); output = []
    k = maps.shape[1]
    for start in range(0, len(maps), 256):
        mapping = torch.as_tensor(maps[start:start + 256], device="cuda"); n = len(mapping)
        extended = torch.cat([mapping, torch.full((n, 1), 27, device="cuda")], 1); target = extended[:, keys]
        value = (costs[tuple(target[:, :, i] for i in range(order + 1))] * freq).sum(1)
        multiplicity = torch.zeros((n, 27), device="cuda", dtype=torch.float64); totals = torch.zeros_like(multiplicity); members = torch.zeros_like(multiplicity)
        multiplicity.scatter_add_(1, mapping, torch.ones_like(mapping, dtype=torch.float64)); totals.scatter_add_(1, mapping, counts.expand(n, -1))
        constants = torch.lgamma(counts + .5) - torch.lgamma(torch.tensor(.5, device="cuda", dtype=torch.float64)); members.scatter_add_(1, mapping, constants.expand(n, -1))
        logp = torch.lgamma(.5 * multiplicity) - torch.lgamma(totals + .5 * multiplicity) + members
        value += torch.where(multiplicity > 0, -logp / math.log(2), 0).sum(1); output.append(value.cpu().numpy())
    return np.concatenate(output)


def search(costs, seqs, counts, k, order, seed, population=4096, generations=14):
    keys, freq = sufficient(seqs, order, k); rng = np.random.default_rng(seed)
    pop = rng.integers(0, 27, size=(population, k), dtype=np.int64)
    for _ in range(generations):
        scores = gpu(costs, keys, freq, counts, pop, order); elite = pop[np.argsort(scores)[:128]].copy()
        children = elite[rng.integers(0, 128, len(pop) - 128)].copy(); rows = np.arange(len(children)); positions = rng.integers(0, k, len(children))
        children[rows, positions] = rng.integers(0, 27, len(children)); pop = np.vstack([elite, children])
    scores = gpu(costs, keys, freq, counts, pop, order); index = int(np.argmin(scores)); exact = float(cpu(costs, keys, freq, counts, pop[index:index + 1], order)[0]); assert abs(exact - scores[index]) < 2e-6
    return exact, pop[index]


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); fixed = sum(fixed_costs(paths).values()); symbols = sum(len(w) for p in paths for w in p.words)
    leader = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]; rows = []; mappings = []; screen = []
    lm_cache = {(language, order): dense_costs(lm(language, order), order) for language in LANGUAGES for order in ORDERS}
    for k in KS:
        seqs, counts, _, vocab, _, common = encoded(paths, k)
        for order in ORDERS:
            null_payload = kt_ngram_bits(seqs, k, order); null_key = 3.0 + math.log2(len(KS)) + math.log2(len(ORDERS)) + universal_uint_bits(order) + common; null_total = fixed + null_key + null_payload
            rows.append({"model": "MATCHED_GROUP_NULL", "k": k, "order": order, "language": "_", "seed": 0,
                         "total_bits": null_total, "bits_per_symbol": null_total / symbols, "gap_vs_matched_null_bits": 0.0,
                         "gap_vs_variable_context_bits": null_total - leader["total_bits"], "key_bits": null_key,
                         "payload_bits": null_payload, "fixed_bits": fixed, "decoder_hash": hashlib.sha256(canonical({"vocab": vocab, "order": order})).hexdigest(), "cpu_exact": True})
            for language in LANGUAGES:
                bits, mapping = search(lm_cache[(language, order)], seqs, counts, k, order, 34101)
                key = 3.0 + math.log2(len(KS)) + math.log2(len(ORDERS)) + math.log2(len(LANGUAGES)) + universal_uint_bits(order) + common + k * math.log2(27); total = fixed + key + bits
                mapping_rows = [{"source_group": vocab[i], "target": " " if mapping[i] == 26 else chr(97 + int(mapping[i])), "occurrences": int(counts[i])} for i in range(k)]
                digest = hashlib.sha256(canonical(mapping_rows)).hexdigest(); item = {"model": "GROUP_CHARACTER_LANGUAGE", "k": k, "order": order, "language": language, "seed": 34101,
                        "total_bits": total, "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total,
                        "gap_vs_variable_context_bits": total - leader["total_bits"], "key_bits": key, "payload_bits": bits,
                        "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
                rows.append(item); screen.append(item); mappings.append(item | {"mapping": mapping_rows})
    winner = min(screen, key=lambda r: r["total_bits"]); seqs, counts, _, vocab, _, common = encoded(paths, winner["k"]); null_total = next(r["total_bits"] for r in rows if r["model"] == "MATCHED_GROUP_NULL" and r["k"] == winner["k"] and r["order"] == winner["order"])
    for seed in (34102, 34103):
        bits, mapping = search(lm_cache[(winner["language"], winner["order"])], seqs, counts, winner["k"], winner["order"], seed)
        key = 3.0 + math.log2(len(KS)) + math.log2(len(ORDERS)) + math.log2(len(LANGUAGES)) + universal_uint_bits(winner["order"]) + common + winner["k"] * math.log2(27); total = fixed + key + bits
        mapping_rows = [{"source_group": vocab[i], "target": " " if mapping[i] == 26 else chr(97 + int(mapping[i])), "occurrences": int(counts[i])} for i in range(winner["k"])]
        digest = hashlib.sha256(canonical(mapping_rows)).hexdigest(); item = {"model": "GROUP_CHARACTER_LANGUAGE", "k": winner["k"], "order": winner["order"], "language": winner["language"], "seed": seed,
                "total_bits": total, "bits_per_symbol": total / symbols, "gap_vs_matched_null_bits": total - null_total,
                "gap_vs_variable_context_bits": total - leader["total_bits"], "key_bits": key, "payload_bits": bits,
                "fixed_bits": fixed, "decoder_hash": digest, "cpu_exact": True}
        rows.append(item); mappings.append(item | {"mapping": mapping_rows})
    best = min((r for r in rows if r["model"] == "GROUP_CHARACTER_LANGUAGE"), key=lambda r: r["total_bits"]); same = [r for r in rows if r["model"] == "GROUP_CHARACTER_LANGUAGE" and r["k"] == winner["k"] and r["order"] == winner["order"] and r["language"] == winner["language"]]; stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_null_bits"] < 0 else "STOP") + "_GROUP_CODE_HIGH_ORDER_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_GROUP_CODE_HIGH_ORDER_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision, "best": best, "rows": rows,
              "claim_ceiling": "Exploratory higher-order complete-group character code; no group has an established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_high_order_results.json").write_bytes(canonical(result)); (ROOT / "gdt001_group_code_high_order_mappings.json").write_bytes(canonical({"schema": "GDT001_GROUP_CODE_HIGH_ORDER_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_group_code_high_order_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__": main()
