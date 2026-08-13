#!/usr/bin/env python3
"""Homophonic historical-language decoder with exact latent plaintext spaces."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import (
    ROOT, LETTERS, TARGET_ALPHABET, canonical, categorical_bits, fixed_costs,
    load_lattice, universal_uint_bits,
)
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm


ORDERS = (2, 4)
SEEDS = (53101, 53102, 53103)
INITIAL_SEEDS = (101, 202, 303)
SPACE = 26
BOS = 27


def source_sequences(paths):
    """Return source-letter IDs only; manual boundaries stay in the fixed channel."""
    sequences = []
    counts = np.zeros(len(LETTERS), dtype=np.int64)
    for path in paths:
        sequence = [LETTERS.index(char) for word in path.words for char in word]
        sequences.append(sequence)
        for token in sequence:
            counts[token] += 1
    return sequences, counts


def reverse_bits(mapping, counts):
    groups = defaultdict(list)
    for source, target in enumerate(mapping):
        groups[int(target)].append(int(counts[source]))
    return sum(categorical_bits(group) for group in groups.values())


def initial_mapping(language):
    candidates = []
    for seed in INITIAL_SEEDS:
        pattern = ROOT / f".gdt001/runs/homophonic_cipher_{language}_s{seed:04d}.json"
        if not pattern.exists():
            continue
        item = json.loads(pattern.read_text())
        mapping = item["decoder"]["mapping"][:-1]
        values = np.asarray([ord(row["latent_unit"]) - 97 for row in mapping], dtype=np.int64)
        candidates.append((float(item["total_bits"]), values))
    if not candidates:
        raise ValueError(f"no retained homophonic seed for {language}")
    return min(candidates, key=lambda item: item[0])[1]


def viterbi_line(sequence, mapping, costs, order, with_path=False):
    """Minimum-cost path with an optional target space before each letter."""
    mapped = tuple(int(mapping[source]) for source in sequence)
    if not mapped: return (0.0, ()) if with_path else 0.0
    # State is exactly the last `order` emitted target symbols. For each source
    # letter, emit LETTER or (except initially) SPACE,LETTER.
    states = {(BOS,) * order: (0.0, () if with_path else None)}
    for index, letter in enumerate(mapped):
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
                candidate = (value + added, path + (before,) if with_path else None)
                if (next_history not in updated or candidate[0] < updated[next_history][0] - 1e-12 or
                        (with_path and abs(candidate[0] - updated[next_history][0]) <= 1e-12 and candidate[1] < updated[next_history][1])):
                    updated[next_history] = candidate
        states = updated
    value, tail = min(states.values(), key=lambda item: (item[0], item[1] or ()))
    return (value, tail) if with_path else value


def cpu_score(sequences, mapping, counts, costs, order, with_paths=False):
    language_bits = 0.0; paths = []; spaces = 0
    for sequence in sequences:
        if with_paths:
            bits, path = viterbi_line(sequence, mapping, costs, order, True)
            language_bits += bits; paths.append(path); spaces += sum(path)
        else:
            language_bits += viterbi_line(sequence, mapping, costs, order)
    reverse = reverse_bits(mapping, counts)
    if with_paths:
        return language_bits + reverse, language_bits, reverse, paths, spaces
    return language_bits + reverse


def search(sequences, counts, costs, order, language, seed):
    rng = np.random.default_rng(seed); initial = initial_mapping(language)
    # Each declared seed supplies exactly one distinct one-coordinate proposal
    # after the 12-way initial screen.  The retained choice is rescored exactly.
    proposal = initial.copy(); position = int(rng.integers(0, len(LETTERS)))
    target = int(rng.integers(0, 25))
    if target >= int(initial[position]): target += 1
    proposal[position] = target
    initial_bits = cpu_score(sequences, initial, counts, costs, order)
    proposal_bits = cpu_score(sequences, proposal, counts, costs, order)
    evidence = {"proposal_source": position, "proposal_old_target": int(initial[position]),
                "proposal_new_target": target, "proposal_payload_bits": proposal_bits,
                "proposal_delta_bits": proposal_bits - initial_bits,
                "proposal_mapping_hash": hashlib.sha256(canonical(list(map(int, proposal)))).hexdigest(),
                "proposal_accepted": proposal_bits < initial_bits - 1e-9}
    if evidence["proposal_accepted"]:
        return proposal, proposal_bits, 1, 2, evidence
    return initial, initial_bits, 0, 2, evidence


def mapping_rows(mapping, counts):
    multiplicity = Counter(map(int, mapping))
    return [{"source": LETTERS[i], "target": chr(97 + int(target)),
             "occurrences": int(counts[i]), "reverse_ambiguity": multiplicity[int(target)]}
            for i, target in enumerate(mapping)]


def plaintext_lines(sequences, mapping, paths):
    output = []
    for sequence, flags in zip(sequences, paths):
        chars = []
        for source, before in zip(sequence, flags):
            if before: chars.append(" ")
            chars.append(chr(97 + int(mapping[source])))
        output.append("".join(chars))
    return output


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); sequences, counts = source_sequences(paths)
    fixed = sum(fixed_costs(paths).values()); symbols = int(counts.sum())
    leader = json.loads((ROOT / "gdt001_current_summary.json").read_text())["leaderboard"][0]
    screen = []
    for order in ORDERS:
        for language in PACK_NAMES:
            costs = dense_costs(lm(language, order), order); mapping = initial_mapping(language)
            payload = cpu_score(sequences, mapping, counts, costs, order)
            reverse = reverse_bits(mapping, counts)
            key = (3.0 + math.log2(len(PACK_NAMES)) + math.log2(len(ORDERS))
                   + math.log2(len(SEEDS)) + universal_uint_bits(order) + len(LETTERS) * math.log2(26))
            screen.append({"language": language, "order": order, "seed": 0,
                           "total_bits": fixed + key + payload, "payload_bits": payload,
                           "language_bits": payload - reverse, "reverse_bits": reverse,
                           "key_bits": key, "fixed_bits": fixed, "mapping": list(map(int, mapping)),
                           "mapping_hash": hashlib.sha256(canonical(list(map(int, mapping)))).hexdigest(),
                           "decoder_hash": hashlib.sha256(canonical({"language": language, "order": order, "mapping": list(map(int, mapping)), "space_rule": "exact line-reset Viterbi"})).hexdigest(),
                           "cpu_exact": True})
    winner = min(screen, key=lambda item: item["total_bits"])
    language = winner["language"]; order = winner["order"]
    costs = dense_costs(lm(language, order), order); rows = []; decoders = []
    for seed in SEEDS:
        mapping, _, accepted, evaluated, proposal = search(sequences, counts, costs, order, language, seed)
        payload, language_bits, reverse, space_paths, space_count = cpu_score(sequences, mapping, counts, costs, order, True)
        rows_map = mapping_rows(mapping, counts); plaintext = plaintext_lines(sequences, mapping, space_paths)
        mapping_hash = hashlib.sha256(canonical(rows_map)).hexdigest(); path_hash = hashlib.sha256(canonical(space_paths)).hexdigest()
        plaintext_hash = hashlib.sha256(canonical(plaintext)).hexdigest()
        key = (3.0 + math.log2(len(PACK_NAMES)) + math.log2(len(ORDERS))
               + math.log2(len(SEEDS)) + universal_uint_bits(order) + len(LETTERS) * math.log2(26))
        total = fixed + key + payload
        row = {"language": language, "order": order, "seed": seed, "total_bits": total,
               "bits_per_symbol": total / symbols, "gap_vs_current_source_leader_bits": total - float(leader["total_bits"]),
               "key_bits": key, "language_bits": language_bits, "reverse_bits": reverse, "fixed_bits": fixed,
               "inserted_spaces": space_count, "accepted_coordinate_moves": accepted, "evaluated_keys": evaluated,
               "mapping_hash": mapping_hash, "space_path_hash": path_hash, "plaintext_hash": plaintext_hash,
               "cpu_exact": True} | proposal
        decoder = {"schema": "GDT001_LATENT_SPACE_HOMOPHONIC_DECODER_V1", "language": language,
                   "order": order, "seed": seed, "mapping": rows_map,
                   "space_rule": "before each noninitial plaintext letter choose SPACE+LETTER or LETTER by exact line-reset Viterbi; no leading, trailing, or consecutive spaces",
                   "source_boundary_rule": "manual source boundaries are absent from latent plaintext and restored by the fixed lattice channel",
                   "space_paths": ["".join(map(str, flags)) for flags in space_paths], "plaintext_lines": plaintext,
                   "mapping_hash": mapping_hash, "space_path_hash": path_hash, "plaintext_hash": plaintext_hash,
                   "reconstruction": "decode latent plaintext from the frozen historical LM; the paid reverse-homophone channel recovers every source letter; the common lattice channel restores source separators and raw readings"}
        decoders.append(row | {"decoder": decoder, "decoder_hash": hashlib.sha256(canonical(decoder)).hexdigest()}); rows.append(row)
    best = min(decoders, key=lambda item: item["total_bits"])
    decision = "CONTINUE_LATENT_SPACE_HOMOPHONIC_SCREEN" if best["total_bits"] < float(leader["total_bits"]) else "STOP_LATENT_SPACE_HOMOPHONIC_SCREEN_LOSES"
    output = {"schema": "GDT001_LATENT_SPACE_HOMOPHONIC_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "current_source_leader_bits": float(leader["total_bits"]),
              "search_scope": "exact initial score for six packs x two orders; exactly one one-coordinate proposal for each of three seeds on the winning configuration",
              "screen": screen, "best": {key: value for key, value in best.items() if key != "decoder"}, "rows": rows,
              "claim_ceiling": "Exploratory latent-plaintext-space homophonic decoder only; no language, word boundary, sound, plaintext, meaning, or translation is established."}
    (ROOT / "gdt001_latent_space_homophonic_results.json").write_bytes(canonical(output))
    (ROOT / "gdt001_latent_space_homophonic_decoders.json").write_bytes(canonical({"schema": "GDT001_LATENT_SPACE_HOMOPHONIC_DECODERS_V1", "decoders": decoders}))
    with (ROOT / "gdt001_latent_space_homophonic_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "best": output["best"]}))


if __name__ == "__main__":
    main()
