#!/usr/bin/env python3
"""Within-line hidden-state source decoder with an explicitly coded state path."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, kt_ngram_bits, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded


KS = (2, 3, 4)
SEEDS = (39101, 39102, 39103)


def histories(sequences, alphabet):
    output = []
    for sequence in sequences:
        history = [alphabet, alphabet]; line = []
        for token in sequence:
            line.append((tuple(history), token)); history = [history[-1], token]
        output.append(line)
    return output


def tables(events, states, k, alphabet):
    transition = defaultdict(Counter); emission = defaultdict(Counter)
    for line, assignment in zip(events, states):
        previous = k
        for (history, token), state in zip(line, assignment):
            transition[previous][state] += 1; emission[(state, history)][token] += 1; previous = state
    trans_cost = np.empty((k + 1, k));
    for previous in range(k + 1):
        counter = transition[previous]; denominator = sum(counter.values()) + .5 * k
        trans_cost[previous] = [-math.log2((counter[state] + .5) / denominator) for state in range(k)]
    emit_cost = {}
    for key, counter in emission.items():
        denominator = sum(counter.values()) + .5 * alphabet
        emit_cost[key] = np.asarray([-math.log2((counter[token] + .5) / denominator) for token in range(alphabet)])
    fallback = np.full(alphabet, math.log2(alphabet))
    return trans_cost, emit_cost, fallback


def viterbi(line, k, trans, emission, fallback):
    if not line: return []
    history, token = line[0]; score = trans[k] + np.asarray([emission.get((state, history), fallback)[token] for state in range(k)]); back = []
    for history, token in line[1:]:
        candidate = score[:, None] + trans[:k]; predecessor = np.argmin(candidate, axis=0); score = candidate[predecessor, np.arange(k)]
        score += np.asarray([emission.get((state, history), fallback)[token] for state in range(k)]); back.append(predecessor)
    state = int(np.argmin(score)); output = [state]
    for predecessor in reversed(back): state = int(predecessor[state]); output.append(state)
    output.reverse(); return output


def canonicalize(states, k):
    mapping = {}; next_id = 0; output = []
    for line in states:
        row = []
        for state in line:
            if state not in mapping: mapping[state] = next_id; next_id += 1
            row.append(mapping[state])
        output.append(row)
    return output, next_id


def exact(events, states, k, alphabet):
    transition_bits = kt_ngram_bits(states, k, 1); emission = defaultdict(Counter)
    for line, assignment in zip(events, states):
        for (history, token), state in zip(line, assignment): emission[(state, history)][token] += 1
    emission_bits = sum(categorical_bits([counter.get(token, 0) for token in range(alphabet)]) for counter in emission.values())
    return transition_bits, emission_bits


def fit(sequences, k, seed, alphabet):
    events = histories(sequences, alphabet); rng = np.random.default_rng(seed); states = [rng.integers(0, k, len(line)).tolist() for line in events]
    trajectory = []
    for _ in range(30):
        trans, emission, fallback = tables(events, states, k, alphabet); updated = [viterbi(line, k, trans, emission, fallback) for line in events]
        updated, used = canonicalize(updated, k); transition_bits, emission_bits = exact(events, updated, k, alphabet); value = transition_bits + emission_bits
        trajectory.append(value)
        if updated == states: states = updated; break
        states = updated
    states, used = canonicalize(states, k); transition_bits, emission_bits = exact(events, states, k, alphabet)
    digest = hashlib.sha256(canonical(states)).hexdigest()
    return states, used, transition_bits, emission_bits, trajectory, digest


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); nulls = frozenset("juz"); sequences, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1
    fixed = sum(fixed_costs(paths).values()); symbols = sum(len(word) for path in paths for word in path.words); rare_key = universal_uint_bits(3) + math.log2(math.comb(len(LETTERS), 3)); leader = json.loads((ROOT / "gdt001_online_context_mixer_results.json").read_text())["best"]
    rows = []; state_artifacts = []
    for k in KS:
        for seed in SEEDS:
            states, used, transitions, emissions, trajectory, digest = fit(sequences, k, seed, alphabet)
            key = 3.0 + math.log2(2) + math.log2(len(KS)) + math.log2(len(SEEDS)) + rare_key + universal_uint_bits(k)
            total = fixed + side + key + transitions + emissions
            row = {"requested_k": k, "used_k": used, "seed": seed, "total_bits": total, "bits_per_symbol": total / symbols,
                   "gap_vs_context_mixer_bits": total - leader["total_bits"], "key_bits": key, "state_transition_bits": transitions,
                   "emission_bits": emissions, "side_channel_bits": side, "fixed_bits": fixed, "iterations": len(trajectory),
                   "state_path_hash": digest, "cpu_exact": True}; rows.append(row); state_artifacts.append(row | {"states": states})
    best = min(rows, key=lambda row: row["total_bits"]); peers = [row for row in rows if row["requested_k"] == best["requested_k"]]
    stable = len({row["state_path_hash"] for row in peers}) == 1
    decision = ("CONTINUE" if best["gap_vs_context_mixer_bits"] < 0 else "STOP") + "_SYMBOL_STATE_MARKOV_" + ("STABLE" if stable else "UNSTABLE")
    output = {"schema": "GDT001_SYMBOL_STATE_MARKOV_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
              "physical_lines": len(sequences), "modeled_events": sum(map(len, sequences)), "source_symbols": symbols,
              "best": best, "rows": rows,
              "claim_ceiling": "Explicit within-line latent source-state code only; no state is a language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_symbol_state_markov_results.json").write_bytes(canonical(output)); (ROOT / "gdt001_symbol_state_markov_paths.json").write_bytes(canonical({"schema": "GDT001_SYMBOL_STATE_MARKOV_PATHS_V1", "paths": state_artifacts}))
    with (ROOT / "gdt001_symbol_state_markov_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": best}))


if __name__ == "__main__": main()
