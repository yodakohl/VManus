#!/usr/bin/env python3
"""One-shot omitted-vowel sensitivity of the latent-space homophonic model."""

from __future__ import annotations

import ctypes
import hashlib
import heapq
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from gdt001_core import LETTERS, ROOT, TARGET_ALPHABET, canonical, categorical_bits, fixed_costs, load_lattice, sha256_file, universal_uint_bits
from gdt001_language_models import PACK_NAMES
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_group_code_high_order import dense_costs, lm


ORDER = 2
VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"  # y is consonantal in this frozen sensitivity.
EPSILON = tuple(TARGET_ALPHABET.index(char) for char in VOWELS + " ")
BOS = 27


def source_arrays(paths):
    tokens, offsets, counts = [], [0], np.zeros(len(LETTERS), dtype=np.int64)
    for path in paths:
        line = [LETTERS.index(char) for word in path.words for char in word]
        tokens.extend(line); offsets.append(len(tokens))
        for token in line: counts[token] += 1
    return np.asarray(tokens, dtype=np.int32), np.asarray(offsets, dtype=np.int64), counts


def closure(costs, start, initial=False):
    """Positive-cost shortest epsilon paths from one order-2 history."""
    distance = np.full(28 * 28, np.inf); origin = start[0] * 28 + start[1]
    distance[origin] = 0.0; queue = [(0.0, origin)]
    while queue:
        value, node = heapq.heappop(queue)
        if value != distance[node]: continue
        left, right = divmod(node, 28)
        for emitted in EPSILON:
            if emitted == 26 and (right == 26 or (initial and node == origin)): continue
            target = right * 28 + emitted; candidate = value + float(costs[left, right, emitted])
            if candidate < distance[target] - 1e-12:
                distance[target] = candidate; heapq.heappush(queue, (candidate, target))
    return distance


def transition_tables(costs):
    target_ids = [TARGET_ALPHABET.index(char) for char in CONSONANTS]
    starts = np.full((21, 28), np.inf)
    first = closure(costs, (BOS, BOS), True)
    for d_index, required in enumerate(target_ids):
        for node, value in enumerate(first):
            left, right = divmod(node, 28)
            starts[d_index, right] = min(starts[d_index, right], value + float(costs[left, right, required]))
    transitions = np.full((21, 21, 28, 28), np.inf)
    terminals = np.full((21, 28), np.inf)
    for c_index, current in enumerate(target_ids):
        for previous in range(28):
            distances = closure(costs, (previous, current))
            terminals[c_index, previous] = min(value for node, value in enumerate(distances) if node % 28 != 26)
            for d_index, required in enumerate(target_ids):
                row = transitions[c_index, d_index, previous]
                for node, value in enumerate(distances):
                    left, right = divmod(node, 28)
                    row[right] = min(row[right], value + float(costs[left, right, required]))
    return np.ascontiguousarray(starts), np.ascontiguousarray(transitions), np.ascontiguousarray(terminals)


def scorer():
    source = ROOT / "gdt001_skeleton_score.cpp"; library = ROOT / ".gdt001/gdt001_skeleton_score.so"
    library.parent.mkdir(exist_ok=True)
    if not library.exists() or library.stat().st_mtime_ns < source.stat().st_mtime_ns:
        subprocess.run(["g++", "-O3", "-std=c++17", "-shared", "-fPIC", str(source), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).gdt001_skeleton_score
    function.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int64), ctypes.c_int64,
                         ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
    function.restype = ctypes.c_double
    return function


def project_mapping(language):
    """Project the frozen direct homophonic key to the next alphabetic consonant."""
    screen = json.loads((ROOT / "gdt001_latent_space_homophonic_results.json").read_text())["screen"]
    direct = next(row["mapping"] for row in screen if row["language"] == language and row["order"] == ORDER)
    target = []
    for value in direct:
        letter = chr(97 + int(value)); position = ord(letter) - 97
        while chr(97 + position % 26) not in CONSONANTS: position += 1
        target.append(CONSONANTS.index(chr(97 + position % 26)))
    return np.asarray(target, dtype=np.int32)


def reverse_bits(mapping, counts):
    groups = defaultdict(list)
    for source, target in enumerate(mapping): groups[int(target)].append(int(counts[source]))
    return sum(categorical_bits(group) for group in groups.values())


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines); tokens, offsets, counts = source_arrays(paths)
    fixed = sum(fixed_costs(paths).values()); leader = float(json.loads((ROOT / "gdt001_current_summary.json").read_text())["leaderboard"][0]["total_bits"])
    call = scorer(); rows = []
    for language in PACK_NAMES:
        costs = dense_costs(lm(language, ORDER), ORDER); starts, transitions, terminals = transition_tables(costs); mapping = project_mapping(language)
        language_bits = call(tokens.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)), offsets.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)), len(offsets) - 1,
                             mapping.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)), starts.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), transitions.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), terminals.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
        reverse = reverse_bits(mapping, counts)
        key = 3.0 + math.log2(len(PACK_NAMES)) + universal_uint_bits(ORDER) + len(LETTERS) * math.log2(len(CONSONANTS))
        total = fixed + key + language_bits + reverse
        mapping_rows = [{"source": LETTERS[i], "required_consonant": CONSONANTS[int(value)], "occurrences": int(counts[i])} for i, value in enumerate(mapping)]
        rows.append({"language": language, "order": ORDER, "total_bits": total, "bits_per_symbol": total / len(tokens),
                     "gap_vs_current_source_leader_bits": total - leader, "key_bits": key, "language_bits": language_bits,
                     "reverse_bits": reverse, "fixed_bits": fixed, "mapping_hash": hashlib.sha256(canonical(mapping_rows)).hexdigest(),
                     "mapping": mapping_rows, "cpu_exact": True})
    best = min(rows, key=lambda row: row["total_bits"]); decision = "STOP_PROJECTED_KEY_DIAGNOSTIC_LOSES_NO_FAMILY_INFERENCE" if best["total_bits"] >= leader else "CONTINUE_CONSONANTAL_SKELETON_KEY_SEARCH"
    result = {"schema": "GDT001_CONSONANTAL_SKELETON_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "decision": decision,
              "scope": "one deterministic projected-key diagnostic; order 2; six frozen packs; unbounded positive-cost latent aeiou/space insertions; no wider key search",
              "constraint": "delete a,e,i,o,u,SPACE from each latent plaintext line equals its mapped 21-consonant source sequence; y is consonantal; leading, trailing, and consecutive spaces are forbidden",
              "current_source_leader_bits": leader, "rows": rows, "best": best,
              "projected_key_source": {"artifact": "gdt001_latent_space_homophonic_results.json", "sha256": sha256_file(ROOT / "gdt001_latent_space_homophonic_results.json"), "selection": "same language, order 2 screen mapping"},
              "inputs": {name: sha256_file(ROOT / name) for name in ("gdt001_corpus_lattice.json", "gdt001_language_pack_manifest.json", "gdt001_latent_space_homophonic_results.json")},
              "implementation": {name: sha256_file(ROOT / name) for name in ("run_gdt001_consonantal_skeleton.py", "gdt001_skeleton_score.cpp")},
              "claim_ceiling": "One inherited projected-key diagnostic only; no inference about unsearched consonantal keys and no consonant value, vowel, space, language, plaintext, meaning, or translation is established."}
    (ROOT / "gdt001_consonantal_skeleton_results.json").write_bytes(canonical(result))
    print(json.dumps({"decision": decision, "best_language": best["language"], "best_total_bits": best["total_bits"], "gap_bits": best["gap_vs_current_source_leader_bits"]}))


if __name__ == "__main__": main()
