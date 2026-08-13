#!/usr/bin/env python3
"""Independent artifact/arithmetic audit of the token-level hidden-state code."""

import hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

from gdt001_core import (LETTERS, canonical, categorical_bits, fixed_costs,
                         kt_ngram_bits, load_lattice, universal_uint_bits)
from gdt001_scaffold_payload import common_selected_paths

ROOT = Path(__file__).resolve().parent


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    result = json.load(open(ROOT / "gdt001_symbol_state_markov_results.json")); artifacts = json.load(open(ROOT / "gdt001_symbol_state_markov_paths.json"))
    need(result["schema"] == "GDT001_SYMBOL_STATE_MARKOV_V1", "schema"); need(result["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status"); need(result["decision"] == "STOP_SYMBOL_STATE_MARKOV_UNSTABLE", "decision")
    need(len(result["rows"]) == 9 and len(artifacts["paths"]) == 9, "nine_runs")
    _, lattice_lines = load_lattice()
    selected = common_selected_paths(lattice_lines)
    active = [character for character in LETTERS if character not in "juz"]
    symbol_index = {character: index for index, character in enumerate(active)}
    space = len(active)
    sequences = []
    null_flags = []
    null_values = []
    for path in selected:
        sequence = []
        for word_index, word in enumerate(path.words):
            if word_index:
                sequence.append(space)
            for character in word:
                if character in "juz":
                    null_flags.append(1)
                    null_values.append(character)
                else:
                    null_flags.append(0)
                    sequence.append(symbol_index[character])
        sequences.append(sequence)
    side_bits = categorical_bits([null_flags.count(0), null_flags.count(1)])
    side_bits += categorical_bits([null_values.count(character) for character in "juz"])
    fixed_bits = sum(fixed_costs(selected).values())
    mixer_total = json.load(open(ROOT / "gdt001_online_context_mixer_results.json"))["best"]["total_bits"]
    independently_counted_events = sum(
        sum(character not in "juz" for word in path.words for character in word)
        + max(0, len(path.words) - 1)
        for path in selected
    )
    need(result["physical_lines"] == len(selected) == 5386, "physical_lines")
    need(result["modeled_events"] == independently_counted_events == 227021, "modeled_events")
    need(result["source_symbols"] == sum(len(word) for path in selected for word in path.words) == 194324, "source_symbols")
    by = {(row["requested_k"], row["seed"]): row for row in artifacts["paths"]}
    for row in result["rows"]:
        need(row["cpu_exact"] is True, f"cpu_{row['requested_k']}_{row['seed']}")
        total = row["key_bits"] + row["state_transition_bits"] + row["emission_bits"] + row["side_channel_bits"] + row["fixed_bits"]
        need(abs(total - row["total_bits"]) < 1e-6, f"sum_{row['requested_k']}_{row['seed']}")
        item = by[(row["requested_k"], row["seed"])]; need(hashlib.sha256(canonical(item["states"])).hexdigest() == row["state_path_hash"], f"path_hash_{row['requested_k']}_{row['seed']}")
        need(sum(len(line) for line in item["states"]) == independently_counted_events, f"event_count_{row['requested_k']}_{row['seed']}")
        k = row["requested_k"]
        need(row["used_k"] == len({state for line in item["states"] for state in line}), f"used_k_{k}_{row['seed']}")
        transition_bits = kt_ngram_bits(item["states"], k, 1)
        emissions = defaultdict(Counter)
        for sequence, states in zip(sequences, item["states"]):
            history = [space + 1, space + 1]
            for token, state in zip(sequence, states):
                emissions[(state, tuple(history))][token] += 1
                history = [history[-1], token]
        emission_bits = sum(categorical_bits([counts.get(token, 0) for token in range(space + 1)]) for counts in emissions.values())
        expected_key = (3.0 + math.log2(2) + math.log2(3) + math.log2(3)
                        + universal_uint_bits(3) + math.log2(math.comb(len(LETTERS), 3))
                        + universal_uint_bits(k))
        need(abs(row["state_transition_bits"] - transition_bits) < 1e-7, f"transition_{k}_{row['seed']}")
        need(abs(row["emission_bits"] - emission_bits) < 1e-7, f"emission_{k}_{row['seed']}")
        need(abs(row["side_channel_bits"] - side_bits) < 1e-9, f"side_{k}_{row['seed']}")
        need(abs(row["fixed_bits"] - fixed_bits) < 1e-9, f"fixed_{k}_{row['seed']}")
        need(abs(row["key_bits"] - expected_key) < 1e-9, f"key_{k}_{row['seed']}")
        need(abs(row["bits_per_symbol"] - row["total_bits"] / result["source_symbols"]) < 1e-12, f"bps_{k}_{row['seed']}")
        need(abs(row["gap_vs_context_mixer_bits"] - (row["total_bits"] - mixer_total)) < 1e-7, f"gap_{k}_{row['seed']}")
    best = min(result["rows"], key=lambda row: row["total_bits"]); need(best == result["best"], "best_exact"); need(best["gap_vs_context_mixer_bits"] > 84000, "loses_mixer")
    for k in (2, 3, 4): need(len({row["state_path_hash"] for row in result["rows"] if row["requested_k"] == k}) == 3, f"unstable_k{k}")
    output = {"schema": "GDT001_SYMBOL_STATE_MARKOV_VALIDATION_V1", "status": "PASS_EXACT_ARTIFACT_ARITHMETIC_STOP",
              "check_count": len(checks), "checks": checks, "best_total_bits": best["total_bits"],
              "claim_ceiling": "Artifact/arithmetic validation only; no state, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_symbol_state_markov_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "best_total_bits": best["total_bits"]}))


if __name__ == "__main__": main()
