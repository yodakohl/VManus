#!/usr/bin/env python3
"""Independent exact reconstruction of the literal line-initial screen."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from functools import lru_cache

from gdt001_core import (LETTERS, ROOT, SOURCE_ALPHABET, canonical,
                         categorical_bits, fixed_costs, kt_ngram_bits,
                         load_lattice, sha256_file, universal_uint_bits)
from gdt001_language_models import PACK_NAMES, train_pack
from run_gdt001_source_selected_nulls import encoded


ORDER = 2
SHARE = 1 / 64
SEEDS = (64101, 64102, 64103)
RARE = frozenset("juz")
PREDICTORS = (("HISTORY3", None), ("CURRIER", "currier"),
              ("SECTION", "section"), ("HAND", "hand"),
              ("KIND", "kind"), ("GRAMMAR_SCOPE", "grammar_scope"))


def probability(counter, token, alphabet):
    return (counter[token] + .5) / (sum(counter.values()) + .5 * alphabet)


def line_initials(lines, paths):
    rows = []
    for line, path in zip(lines, paths):
        if line.grammar_scope != "CONFIRMED_PROSE":
            continue
        prefix, suffix = line.locus.rsplit(".", 1)
        if not suffix.isdigit() or prefix.casefold() != line.page.casefold():
            raise AssertionError(f"non-numeric locus {line.locus}")
        if not path.source_line:
            continue
        if path.source_line[0] == " ":
            raise AssertionError(f"space initial {line.locus}")
        rows.append((line.page, int(suffix), line.locus,
                     LETTERS.index(path.source_line[0])))
    rows.sort()
    by_page = defaultdict(list)
    for page, _, _, token in rows:
        by_page[page].append(token)
    return rows, [by_page[page] for page in sorted(by_page)]


def selected_paths(lines):
    with (ROOT / "candidates/nonsemantic_ngram_o2/segmentation.tsv").open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(lines):
        raise AssertionError("segmentation length")
    output = []
    for line, row in zip(lines, rows):
        if row["locus"] != line.locus:
            raise AssertionError(f"segmentation locus {line.locus}")
        output.append(next(path for path in line.paths if path.path_id == row["selected_path_id"]))
    return output


def body_bits(lines, paths):
    sequences, _, _, active, _, side = encoded(paths, RARE)
    alphabet = len(active) + 1
    bos = alphabet
    shared = defaultdict(Counter)
    longer = defaultdict(Counter)
    metadata = {name: defaultdict(Counter) for name, _ in PREDICTORS[1:]}
    weights = {}
    total = 0.0
    for line, path, sequence in zip(lines, paths, sequences):
        history = [bos, bos, bos]
        for position, token in enumerate(sequence):
            context = tuple(history[-2:])
            counters = [shared[context], longer[(context, history[-3])]]
            for name, field in PREDICTORS[1:]:
                counters.append(metadata[name][(context, getattr(line, field) or "_")])
            probs = [probability(counter, token, alphabet) for counter in counters]
            current = weights.setdefault(context, [1 / len(counters)] * len(counters))
            mixture = sum(weight * value for weight, value in zip(current, probs))
            if not (position == 0 and line.grammar_scope == "CONFIRMED_PROSE" and path.source_line):
                total -= math.log2(mixture)
            posterior = [weight * value / mixture for weight, value in zip(current, probs)]
            weights[context] = [(1 - SHARE) * value + SHARE / len(counters)
                                for value in posterior]
            for counter in counters:
                counter[token] += 1
            history = history[1:] + [token]
    return total, side


def sufficient(sequences):
    events = Counter()
    counts = [0] * len(LETTERS)
    for sequence in sequences:
        history = [len(LETTERS), len(LETTERS)]
        for token in sequence:
            events[tuple(history) + (token,)] += 1
            counts[token] += 1
            history = history[1:] + [token]
    return sorted(events.items()), counts


@lru_cache(maxsize=None)
def language_model(language):
    return train_pack(language, ORDER)


def mapped_bits(language, events, counts, mapping):
    lm = language_model(language)
    extended = [*mapping, 27]
    total = 0.0
    for (left, right, token), frequency in events:
        total += float(lm.costs[extended[left], extended[right], extended[token]]) * frequency
    reverse = defaultdict(list)
    for source, target in enumerate(mapping):
        reverse[target].append(counts[source])
    return total + sum(categorical_bits(group) for group in reverse.values())


def main():
    result = json.loads((ROOT / "gdt001_line_initial_channel_results.json").read_text())
    checks = []

    def need(value, name):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    need(result["schema"] == "GDT001_LINE_INITIAL_CHANNEL_V1", "schema")
    need(result["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status")
    need(result["decision"] == "STOP_LINE_INITIAL_LANGUAGE_CHANNEL", "decision")
    expected_inputs = {name: sha256_file(ROOT / name) for name in
                       ("gdt001_corpus_lattice.json", "gdt001_language_pack_manifest.json",
                        "candidates/nonsemantic_ngram_o2/segmentation.tsv",
                        "gdt001_online_context_mixer_results.json")}
    need(result["inputs"] == expected_inputs, "input_hashes")
    need(result["implementation"] == sha256_file(ROOT / "run_gdt001_line_initial_channel.py"),
         "implementation_hash")
    _, lines = load_lattice()
    paths = selected_paths(lines)
    ordered, sequences = line_initials(lines, paths)
    need(result["counts"] == {"lattice_physical_lines": len(lines),
                              "confirmed_prose_initials": len(ordered),
                              "excluded_other_or_empty_lines": len(lines) - len(ordered),
                              "pages": len(sequences),
                              "initial_events": sum(map(len, sequences)),
                              "supported_initial_signs": len({token for sequence in sequences
                                                               for token in sequence})}, "counts")
    fixed = sum(fixed_costs(paths).values())
    need(result["selected_path_digest"] == hashlib.sha256(
        canonical([path.path_id for path in paths])).hexdigest(), "selected_path_digest")
    expected_stream = [{"locus": line.locus, "source_initial": path.source_line[0]}
                       for _, _, line, path in sorted(
                           [(line.page, int(line.locus.rsplit(".", 1)[1]), line, path)
                            for line, path in zip(lines, paths)
                            if line.grammar_scope == "CONFIRMED_PROSE" and path.source_line],
                           key=lambda row: (row[0], row[1], row[2].locus))]
    need(result["initial_stream_sha256"] == hashlib.sha256(canonical(expected_stream)).hexdigest(),
         "initial_stream_hash")
    body, side = body_bits(lines, paths)
    rare_key = universal_uint_bits(len(RARE)) + math.log2(math.comb(len(LETTERS), len(RARE)))
    body_key = 3 + rare_key + math.log2(2) + math.log2(6)
    need(abs(result["body"]["bits"] - body) < 1e-8, "body_bits")
    need(abs(result["body"]["key_bits"] - body_key) < 1e-12, "body_key")
    anonymous_initial = kt_ngram_bits(sequences, len(LETTERS), ORDER)
    anonymous_key = 1 + universal_uint_bits(ORDER) + math.log2(7)
    anonymous_total = fixed + side + body_key + body + anonymous_key + anonymous_initial
    for field, value in (("initial_bits", anonymous_initial), ("key_bits", anonymous_key),
                         ("total_bits", anonymous_total)):
        need(abs(result["matched_anonymous"][field] - value) < 1e-8,
             f"anonymous:{field}")
    events, counts = sufficient(sequences)
    raw_leader = json.loads((ROOT / "gdt001_online_context_mixer_results.json").read_text())["best"]["total_bits"]
    need(abs(result["raw_global_leader_bits"] - raw_leader) < 1e-9 and
         abs(result["selector_adjusted_global_leader_bits"] - (raw_leader + 1)) < 1e-9,
         "global_leader")
    need([(row["language"], row["seed"]) for row in result["rows"]] ==
         [(language, seed) for language in PACK_NAMES for seed in SEEDS], "row_order")
    key = body_key + 1 + universal_uint_bits(ORDER) + math.log2(7) + \
          math.log2(len(SEEDS)) + len(LETTERS) * math.log2(27)
    totals = []
    for row in result["rows"]:
        mapping_rows = row["mapping"]
        need([item["source"] for item in mapping_rows] == list(LETTERS),
             f"{row['language']}:{row['seed']}:sources")
        need([item["occurrences"] for item in mapping_rows] == counts,
             f"{row['language']}:{row['seed']}:counts")
        targets = [26 if item["target"] == " " else ord(item["target"]) - 97
                   for item in mapping_rows]
        need(all(0 <= value < 27 for value in targets),
             f"{row['language']}:{row['seed']}:targets")
        need(row["mapping_hash"] == hashlib.sha256(canonical(mapping_rows)).hexdigest(),
             f"{row['language']}:{row['seed']}:mapping_hash")
        expected_decoder = {"schema": "GDT001_LINE_INITIAL_LANGUAGE_DECODER_V1",
                            "language_pack": row["language"], "language_model_order": ORDER,
                            "mapping": mapping_rows,
                            "scope": "first modeled sign of each nonempty CONFIRMED_PROSE physical line",
                            "serialization": "numeric physical-line suffix within page; page reset",
                            "body_channel": "juz-rare causal seven-expert source mixer; decoded initial updates experts before remaining line events"}
        need(row["decoder"] == expected_decoder and
             row["decoder_hash"] == hashlib.sha256(canonical(expected_decoder)).hexdigest(),
             f"{row['language']}:{row['seed']}:decoder")
        payload = mapped_bits(row["language"], events, counts, targets)
        total = fixed + side + body + key + payload
        for field, value in (("fixed_bits", fixed), ("body_bits", body),
                             ("key_bits", key),
                             ("rare_side_bits", side),
                             ("initial_payload_and_reverse_bits", payload),
                             ("total_bits", total),
                             ("gap_vs_matched_anonymous_bits", total - anonymous_total),
                             ("gap_vs_global_leader_bits", total - result["selector_adjusted_global_leader_bits"])):
            need(abs(float(row[field]) - value) < 1e-7,
                 f"{row['language']}:{row['seed']}:{field}")
        # Independently prove that the retained key is a one-coordinate local optimum.
        for source in range(len(LETTERS)):
            for target in range(27):
                trial = targets.copy()
                trial[source] = target
                need(mapped_bits(row["language"], events, counts, trial) >= payload - 1e-9,
                     f"{row['language']}:{row['seed']}:local:{source}:{target}")
        totals.append(total)
    best_index = min(range(len(totals)), key=lambda i: (totals[i], result["rows"][i]["language"],
                                                        result["rows"][i]["seed"]))
    need(result["best"] == result["rows"][best_index], "best")
    best_language = result["best"]["language"]
    same = [row for row in result["rows"] if row["language"] == best_language]
    supported_indices = [i for i, item in enumerate(same[0]["mapping"]) if item["occurrences"]]
    for row in same:
        supported = [item for item in row["mapping"] if item["occurrences"]]
        need(row["supported_mapping_hash"] == hashlib.sha256(canonical(supported)).hexdigest(),
             f"supported_mapping_hash:{row['seed']}")
    stable = len({row["supported_mapping_hash"] for row in same}) == 1
    need(result["stable_best_language_mapping"] == stable and not stable, "instability")
    agreements = []
    for left in range(len(same)):
        for right in range(left + 1, len(same)):
            agreements.append(sum(same[left]["mapping"][i]["target"] ==
                                  same[right]["mapping"][i]["target"]
                                  for i in supported_indices) / len(supported_indices))
    need(result["best_language_pairwise_supported_mapping_agreement"] == agreements,
         "mapping_agreement")
    need(result["best"]["total_bits"] > anonymous_total > result["selector_adjusted_global_leader_bits"],
         "stop_arithmetic")
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    registered = [row for row in ledger if row["run_id"].startswith("lineinitial_")]
    need(len(registered) == len(result["rows"]), "ledger_count")
    for row in result["rows"]:
        stored = next(item for item in registered if item["run_id"] ==
                      f"lineinitial_{row['language']}_o{row['order']}_s{row['seed']}")
        need(abs(float(stored["total_bits"]) - row["total_bits"]) < 1e-5,
             f"ledger_total:{row['language']}:{row['seed']}")
        need(stored["decoder_hash"] == row["decoder_hash"],
             f"ledger_hash:{row['language']}:{row['seed']}")
    output = {"schema": "GDT001_LINE_INITIAL_CHANNEL_VALIDATION_V1",
              "status": "PASS_INDEPENDENT_CPU_EXACT_STOP",
              "check_count": len(checks), "checks": checks,
              "result_sha256": sha256_file(ROOT / "gdt001_line_initial_channel_results.json"),
              "best_total_bits": result["best"]["total_bits"],
              "claim_ceiling": "Independent corpus ordering, score, local-optimum, matched-null, and stability validation only; no acrostic, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_line_initial_channel_validation.json").write_bytes(canonical(output))
    print(json.dumps({"status": output["status"], "checks": len(checks),
                      "best_total_bits": output["best_total_bits"]}))


if __name__ == "__main__":
    main()
