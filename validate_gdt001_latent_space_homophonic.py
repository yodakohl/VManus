#!/usr/bin/env python3
"""Independent CPU checks for the latent-plaintext-space decoder screen."""

import hashlib
import json
import math
from collections import defaultdict

from gdt001_core import LETTERS, ROOT, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm


SPACE = 26
BOS = 27


def reference_viterbi(letters, costs, order):
    """Exact DP over emitted target histories, independent of producer flags."""
    if not letters:
        return 0.0, ()
    states = {(BOS,) * order: (0.0, ())}
    for index, letter in enumerate(letters):
        updated = {}
        for history, (value, path) in states.items():
            for before in ((0,) if index == 0 else (0, 1)):
                next_history = history
                added = 0.0
                if before:
                    added += float(costs[next_history + (SPACE,)])
                    next_history = next_history[1:] + (SPACE,)
                added += float(costs[next_history + (letter,)])
                next_history = next_history[1:] + (letter,)
                candidate = (value + added, path + (before,))
                if next_history not in updated or candidate < updated[next_history]:
                    updated[next_history] = candidate
        states = updated
    return min(states.values())


def reference_reverse(mapping, counts):
    groups = defaultdict(list)
    for source, target in enumerate(mapping):
        groups[target].append(counts[source])
    return sum(categorical_bits(group) for group in groups.values())


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    result = json.load(open(ROOT / "gdt001_latent_space_homophonic_results.json"))
    decoders = json.load(open(ROOT / "gdt001_latent_space_homophonic_decoders.json"))["decoders"]
    need(result["schema"] == "GDT001_LATENT_SPACE_HOMOPHONIC_V1", "schema")
    need(result["decision"] == "STOP_LATENT_SPACE_HOMOPHONIC_SCREEN_LOSES", "decision")
    need(len(result["screen"]) == 12, "six_languages_x_two_orders_screened")
    need({row["language"] for row in result["screen"]} == set(PACK_NAMES), "language_pack_scope")
    need({row["order"] for row in result["screen"]} == {2, 4}, "order_scope")
    need(len(result["rows"]) == len(decoders) == 3, "three_retained_restarts")
    need({row["seed"] for row in result["rows"]} == {53101, 53102, 53103}, "restart_seeds")
    _, lines = load_lattice()
    selected = common_selected_paths(lines)
    sequences = [[LETTERS.index(char) for word in path.words for char in word] for path in selected]
    counts = [0] * len(LETTERS)
    for sequence in sequences:
        for source in sequence:
            counts[source] += 1
    fixed = sum(fixed_costs(selected).values())
    for screen in result["screen"]:
        mapping = list(map(int, screen["mapping"]))
        need(hashlib.sha256(canonical(mapping)).hexdigest() == screen["mapping_hash"], f"screen_mapping:{screen['language']}:{screen['order']}")
        costs = dense_costs(lm(screen["language"], screen["order"]), screen["order"])
        language_bits = sum(reference_viterbi(tuple(mapping[source] for source in sequence), costs, screen["order"])[0] for sequence in sequences)
        reverse_bits = reference_reverse(mapping, counts)
        expected_key = 3.0 + math.log2(6) + math.log2(2) + math.log2(3) + universal_uint_bits(screen["order"]) + len(LETTERS) * math.log2(26)
        need(math.isclose(screen["language_bits"], language_bits, abs_tol=1e-7), f"screen_language:{screen['language']}:{screen['order']}")
        need(math.isclose(screen["reverse_bits"], reverse_bits, abs_tol=1e-7), f"screen_reverse:{screen['language']}:{screen['order']}")
        need(math.isclose(screen["key_bits"], expected_key, abs_tol=1e-12), f"screen_key:{screen['language']}:{screen['order']}")
        need(math.isclose(screen["total_bits"], fixed + expected_key + language_bits + reverse_bits, abs_tol=1e-7), f"screen_total:{screen['language']}:{screen['order']}")
    screen_best = min(result["screen"], key=lambda item: (item["total_bits"], item["language"], item["order"]))
    need((screen_best["language"], screen_best["order"]) == ("middle_high_german", 2), "screen_argmin")
    for row, item in zip(result["rows"], decoders):
        need(row == {key: value for key, value in item.items() if key not in {"decoder", "decoder_hash"}}, f"row:{row['seed']}")
        need(abs(row["total_bits"] - (row["key_bits"] + row["language_bits"] + row["reverse_bits"] + row["fixed_bits"])) < 1e-7, f"sum:{row['seed']}")
        decoder = item["decoder"]
        need(hashlib.sha256(canonical(decoder)).hexdigest() == item["decoder_hash"], f"decoder:{row['seed']}")
        need(hashlib.sha256(canonical(decoder["mapping"])).hexdigest() == row["mapping_hash"], f"mapping:{row['seed']}")
        paths = [tuple(map(int, flags)) for flags in decoder["space_paths"]]
        need(hashlib.sha256(canonical(paths)).hexdigest() == row["space_path_hash"], f"paths:{row['seed']}")
        need(hashlib.sha256(canonical(decoder["plaintext_lines"])).hexdigest() == row["plaintext_hash"], f"plaintext:{row['seed']}")
        mapping = [ord(entry["target"]) - 97 for entry in decoder["mapping"]]
        costs = dense_costs(lm(row["language"], row["order"]), row["order"])
        language_bits = 0.0
        for sequence, flags, plaintext in zip(sequences, paths, decoder["plaintext_lines"]):
            letters = tuple(mapping[source] for source in sequence)
            bits, expected_flags = reference_viterbi(letters, costs, row["order"])
            assert expected_flags == flags
            rebuilt = "".join((" " if before else "") + chr(97 + letter) for letter, before in zip(letters, flags))
            assert rebuilt == plaintext
            language_bits += bits
        need(math.isclose(language_bits, row["language_bits"], abs_tol=1e-7), f"independent_language_bits:{row['seed']}")
        need(math.isclose(reference_reverse(mapping, counts), row["reverse_bits"], abs_tol=1e-7), f"independent_reverse_bits:{row['seed']}")
        expected_key = 3.0 + math.log2(6) + math.log2(2) + math.log2(3) + universal_uint_bits(row["order"]) + len(LETTERS) * math.log2(26)
        need(math.isclose(row["key_bits"], expected_key, abs_tol=1e-12), f"key_cost:{row['seed']}")
        need(math.isclose(row["fixed_bits"], fixed, abs_tol=1e-7), f"fixed_bits:{row['seed']}")
        proposal = mapping.copy()
        need(proposal[row["proposal_source"]] == row["proposal_old_target"], f"proposal_old:{row['seed']}")
        proposal[row["proposal_source"]] = row["proposal_new_target"]
        need(hashlib.sha256(canonical(proposal)).hexdigest() == row["proposal_mapping_hash"], f"proposal_hash:{row['seed']}")
        proposal_language = sum(reference_viterbi(tuple(proposal[source] for source in sequence), costs, row["order"])[0] for sequence in sequences)
        proposal_payload = proposal_language + reference_reverse(proposal, counts)
        need(math.isclose(proposal_payload, row["proposal_payload_bits"], abs_tol=1e-7), f"proposal_score:{row['seed']}")
        need(math.isclose(proposal_payload - (row["language_bits"] + row["reverse_bits"]), row["proposal_delta_bits"], abs_tol=1e-7), f"proposal_delta:{row['seed']}")
        need(row["proposal_accepted"] is False and row["accepted_coordinate_moves"] == 0 and row["evaluated_keys"] == 2, f"proposal_rejected:{row['seed']}")
        need(sum(map(sum, paths)) == row["inserted_spaces"], f"space_count:{row['seed']}")
        need(row["gap_vs_current_source_leader_bits"] > 376000, f"decisive_loss:{row['seed']}")
    expected_best = {key: value for key, value in min(decoders, key=lambda item: item["total_bits"]).items() if key != "decoder"}
    need(result["best"] == expected_best, "best_exact")
    need(result["best"]["gap_vs_current_source_leader_bits"] > 376000, "best_loses")
    output = {"schema": "GDT001_LATENT_SPACE_HOMOPHONIC_VALIDATION_V1", "status": "PASS_EXACT_ARTIFACT_ARITHMETIC_DECISIVE_SCREEN_STOP",
              "check_count": len(checks), "checks": checks, "best_total_bits": result["best"]["total_bits"],
              "claim_ceiling": "Screen artifact/arithmetic validation only; no language, word boundary, plaintext, meaning, or translation."}
    (ROOT / "gdt001_latent_space_homophonic_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "best_total_bits": output["best_total_bits"]}))


if __name__ == "__main__":
    main()
