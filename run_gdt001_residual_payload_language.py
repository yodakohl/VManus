#!/usr/bin/env python3
"""Language test on outcomes at source-selected exceptional contexts."""

import csv, hashlib, json, math
from collections import Counter, defaultdict

import numpy as np

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, load_lattice
from gdt001_language_models import PACK_NAMES, train_pack
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_contextual_language import search_encoded
from run_gdt001_source_selected_nulls import encoded


FIELD = {"CURRIER": "currier", "SECTION": "section", "HAND": "hand",
         "KIND": "kind", "GRAMMAR_SCOPE": "grammar_scope"}


def c_bits(counter, alphabet):
    return categorical_bits([counter.get(i, 0) for i in range(alphabet)])


def payload_stream(lines, paths, selected):
    seqs, _, _, active, space, _ = encoded(paths, frozenset("juz")); alphabet = len(active) + 1; bos = alphabet
    selected_by_context = {tuple(item["context"]): item["predictor"] for item in selected}
    streams = []; counts = np.zeros(len(active)); matched = defaultdict(Counter); events = Counter()
    for line, seq in zip(lines, seqs):
        history = [bos, bos, bos]; output = []
        for token in seq:
            context = tuple(history[-2:]); predictor = selected_by_context.get(context)
            if predictor is not None:
                if predictor == "HISTORY3": value = history[-3]
                else: value = getattr(line, FIELD[predictor]) or "_"
                matched[(context, predictor, str(value))][token] += 1; events[predictor] += 1
                output.append(token)
                if token < len(active): counts[token] += 1
            history = history[1:] + [token]
        streams.append(output)
    matched_bits = sum(c_bits(counter, alphabet) for counter in matched.values())
    return streams, counts, np.zeros(len(active), dtype=np.int64), active, space, matched_bits, events


def main():
    _, lines = load_lattice(); paths = common_selected_paths(lines)
    baseline = json.loads((ROOT / "gdt001_variable_context_source_results.json").read_text())["best"]
    decoder = json.loads((ROOT / "gdt001_variable_context_source_decoder.json").read_text())
    args = payload_stream(lines, paths, decoder["selected_contexts"]); streams, counts, cats, active, space, matched_bits, events = args
    other_bits = baseline["payload_bits"] - matched_bits; symbols = sum(len(w) for p in paths for w in p.words)
    rows = []; mappings = []
    for language in PACK_NAMES:
        bits, mapping, digest = search_encoded(streams, counts, cats, active, space, train_pack(language, 2),
                                                33101, population=8192, generations=18)
        key = math.log2(len(PACK_NAMES)) + len(active) * math.log2(27)
        total = baseline["fixed_bits"] + baseline["side_channel_bits"] + baseline["key_bits"] + other_bits + key + bits
        item = {"language": language, "seed": 33101, "selected_events": int(sum(events.values())),
                "total_bits": total, "bits_per_symbol": total / symbols,
                "gap_vs_matched_variable_context_bits": total - baseline["total_bits"],
                "base_key_bits": baseline["key_bits"], "payload_key_bits": key,
                "other_source_bits": other_bits, "language_and_reverse_bits": bits,
                "selected_matched_null_bits": matched_bits, "fixed_bits": baseline["fixed_bits"],
                "rare_side_bits": baseline["side_channel_bits"], "decoder_hash": digest, "cpu_exact": True}
        rows.append(item); mappings.append(item | {"mapping": mapping})
    winner = min(rows, key=lambda r: r["total_bits"]); lm = train_pack(winner["language"], 2)
    for seed in (33102, 33103):
        bits, mapping, digest = search_encoded(streams, counts, cats, active, space, lm, seed,
                                                population=8192, generations=18)
        key = math.log2(len(PACK_NAMES)) + len(active) * math.log2(27)
        total = baseline["fixed_bits"] + baseline["side_channel_bits"] + baseline["key_bits"] + other_bits + key + bits
        item = {"language": winner["language"], "seed": seed, "selected_events": int(sum(events.values())),
                "total_bits": total, "bits_per_symbol": total / symbols,
                "gap_vs_matched_variable_context_bits": total - baseline["total_bits"],
                "base_key_bits": baseline["key_bits"], "payload_key_bits": key,
                "other_source_bits": other_bits, "language_and_reverse_bits": bits,
                "selected_matched_null_bits": matched_bits, "fixed_bits": baseline["fixed_bits"],
                "rare_side_bits": baseline["side_channel_bits"], "decoder_hash": digest, "cpu_exact": True}
        rows.append(item); mappings.append(item | {"mapping": mapping})
    best = min(rows, key=lambda r: r["total_bits"]); same = [r for r in rows if r["language"] == winner["language"]]
    stable = len({r["decoder_hash"] for r in same}) == 1
    decision = ("CONTINUE" if best["gap_vs_matched_variable_context_bits"] < 0 else "STOP") + "_RESIDUAL_PAYLOAD_LANGUAGE_" + ("STABLE" if stable else "UNSTABLE")
    result = {"schema": "GDT001_RESIDUAL_PAYLOAD_LANGUAGE_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
              "decision": decision, "event_counts_by_predictor": dict(sorted(events.items())),
              "best": best, "rows": rows,
              "claim_ceiling": "Exploratory language test on exceptional source-context outcomes only; no context, symbol, language, plaintext, meaning, or translation is established."}
    (ROOT / "gdt001_residual_payload_language_results.json").write_bytes(canonical(result))
    (ROOT / "gdt001_residual_payload_language_mappings.json").write_bytes(canonical({"schema": "GDT001_RESIDUAL_PAYLOAD_LANGUAGE_MAPPINGS_V1", "mappings": mappings}))
    with (ROOT / "gdt001_residual_payload_language_results.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"decision": decision, "events": int(sum(events.values())), "matched_bits": matched_bits, "best": best}))


if __name__ == "__main__":
    main()
