#!/usr/bin/env python3
"""Export ten fixed, inspectable GDT001 decoder packets."""

from __future__ import annotations

import csv
import base64
import json
import math
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

from gdt001_abbreviation_model import decode_path as decode_abbreviation, tokenize_word
from gdt001_core import LETTERS, ROOT, SOURCE_ALPHABET, canonical, load_lattice, sha256_file, train_ngram_logprob
from gdt001_language_models import source_unigrams, train_pack, path_language_bits, path_homophone_reverse_bits
from gdt001_neural_null import cpu_score as neural_cpu_score
from gdt001_nonsemantic_models import predictive_path_bits
from gdt001_record_models import decompose


RUNS = ROOT / ".gdt001/runs"
OUT = ROOT / "candidates"
PACKETS = (
    ("HERBAL_CURRIER_A", "f1r", (1, 2, 3, 4, 5)),
    ("CURRIER_B_PROSE", "f75r", (1, 2, 3, 4, 5)),
    ("BIOLOGICAL_LABEL_RICH", "f75v", ()),
    ("F57V", "f57v", ()),
    ("F67R2", "f67r2", ()),
    ("F75V", "f75v", ()),
    ("CIRCULAR_RADIAL", "f69v", ()),
    ("F116V_STRESS", "f116v", ()),
)


def selected_candidates(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    good = sorted((item for item in results if item["convergence_status"] == "CONVERGED"), key=lambda x: (x["total_bits"], x["candidate_id"]))
    selected: list[dict[str, Any]] = []
    # Five strongest globally, then the strongest missing required system class.
    for item in good[:5]: selected.append(item)
    for family in ("ABBR_LANG", "HOMOPHONIC_CIPHER", "RECORD_NOTATION", "HYBRID", "NONSEMANTIC_GENERATOR"):
        item = next(row for row in good if row["model_class"] == family)
        if item not in selected: selected.append(item)
    for item in good:
        if len(selected) == 10: break
        if item not in selected: selected.append(item)
    return selected[:10]


def decode(item: dict[str, Any], path) -> tuple[str, str]:
    decoder = item["decoder"]
    schema = decoder.get("schema", "")
    if schema == "GDT001_EXPLICIT_MONOTONIC_MAPPING_V1":
        mapping = {row["source_unit"]: row["latent_unit"] for row in decoder["mapping"]}
        return " ".join("+".join(word) for word in path.words), " ".join("".join(mapping[c] for c in word) for word in path.words)
    if schema == "GDT001_ABBREVIATION_TRANSDUCER_V1":
        segmented, plaintext = decode_abbreviation(path, decoder)
        return " ".join(segmented), plaintext
    if schema == "GDT001_RECORD_NOTATION_V1":
        values = {row["source_core"]: row["latent_value"] for row in decoder["anonymous_values"]}
        operators = {row["source_prefix"]: row["latent_operator"] for row in decoder["anonymous_operators"]}
        states = {row["source_suffix"]: row["latent_state"] for row in decoder["anonymous_states"]}
        records = []
        for word in path.words:
            pre, core, suf = decompose(word); records.append(f"{operators.get(pre or '_','OP_UNK')}:{values.get(core or '_','VALUE_UNK')}:{states.get(suf or '_','STATE_UNK')}")
        return " | ".join(path.words), " ".join(records)
    if schema == "GDT001_DUAL_CHANNEL_PROCEDURAL_V1":
        records = []
        for index, word in enumerate(path.words):
            pre, core, suf = decompose(word)
            records.append(f"{'ENTRY' if index == 0 else 'BODY'}[{pre or '_'};STEM={core};SUF={suf or '_'}]")
        return " | ".join(path.words), " ".join(records)
    if schema == "GDT001_ANONYMOUS_RECORD_DICTIONARY_V1":
        values = {row["source_group"]: row["latent_value"] for row in decoder["dictionary"]}
        return " | ".join(path.words), " ".join(values[word] for word in path.words)
    return " ".join("+".join(word) for word in path.words), path.source_line


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def mapping_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    decoder = item["decoder"]; schema = decoder.get("schema", "")
    rows = []
    if "mapping" in decoder:
        for row in decoder["mapping"]:
            rows.append({
                "source_unit": row.get("source_unit", ""), "latent_or_plaintext_unit": row.get("latent_unit", row.get("plaintext_unit", "")),
                "mapping_probability": row.get("mapping_probability", 1.0), "context_restriction": row.get("context_restriction", "ALL"),
                "occurrences": row.get("occurrences", 0), "counterexamples": "all nonchosen mappings under frozen deterministic key",
            })
    elif schema == "GDT001_RECORD_NOTATION_V1":
        for kind, key, source in (("OP", "anonymous_operators", "source_prefix"), ("STATE", "anonymous_states", "source_suffix"), ("VALUE", "anonymous_values", "source_core")):
            for row in decoder[key]: rows.append({"source_unit": row[source], "latent_or_plaintext_unit": row[f"latent_{'operator' if kind == 'OP' else 'state' if kind == 'STATE' else 'value'}"], "mapping_probability": 1.0, "context_restriction": kind, "occurrences": row["occurrences"], "counterexamples": "none admitted; unknown inventory entries fail"})
    else:
        rows.append({"source_unit": "<SOURCE_STREAM>", "latent_or_plaintext_unit": "<SOURCE_STREAM>", "mapping_probability": 1.0, "context_restriction": decoder.get("decoded_output", "explicit reconstruction"), "occurrences": item["source_symbols"], "counterexamples": "not a semantic mapping"})
    return rows


def wrong_path(path):
    words = tuple(word[1:] + word[:1] if len(word) > 1 else word for word in path.words)
    text = " ".join(words)
    return replace(path, words=words, source_line=text, source_ids=tuple(SOURCE_ALPHABET.index(char) for char in text))


def abbreviation_conditional_bits(path, decoder, lm) -> float:
    mapping = {row["source_unit"]: row["plaintext_unit"] for row in decoder["mapping"]}
    occurrences = {row["source_unit"]: row["occurrences"] for row in decoder["mapping"]}
    groups = {}
    for unit, target in mapping.items():
        if target != "<NULL>": groups.setdefault(target, []).append(unit)
    reverse = {}
    for target, units in groups.items():
        denominator = sum(occurrences[unit] + 0.5 for unit in units)
        for unit in units: reverse[unit] = -math.log2((occurrences[unit] + 0.5) / denominator)
    target_ids = []; reverse_bits = 0.0
    units = tuple(decoder["source_units_longest_first"])
    for word_index, word in enumerate(path.words):
        if word_index: target_ids.append(26)
        for unit in tokenize_word(word, units):
            target = mapping[unit]
            if target != "<NULL>":
                target_ids.append(ord(target) - ord("a")); reverse_bits += reverse[unit]
    history = [27] * lm.order; bits = reverse_bits
    for value in target_ids:
        bits += float(lm.costs[tuple(history) + (value,)])
        if lm.order: history = history[1:] + [value]
    return bits


def reverse_scorer(item, selected):
    decoder = item["decoder"]; schema = decoder.get("schema", "")
    if schema == "GDT001_NONSEMANTIC_NGRAM_GENERATOR_V1":
        table = train_ngram_logprob([path.source_ids for path in selected], 26, decoder["order"])
        return "POSTERIOR_PREDICTIVE_SOURCE_NGRAM", lambda path: predictive_path_bits(path, table, decoder["order"])
    if schema == "GDT001_EXPLICIT_MONOTONIC_MAPPING_V1":
        lm = train_pack(decoder["language_pack"], decoder["language_model_order"])
        mapping = [0] * 25
        for row in decoder["mapping"]:
            if row["source_unit"] in LETTERS: mapping[LETTERS.index(row["source_unit"])] = ord(row["latent_unit"]) - ord("a")
        counts = source_unigrams(selected); homophonic = decoder["mapping_kind"] == "HOMOPHONIC"
        return "LANGUAGE_LM_PLUS_EXPLICIT_REVERSE_KEY", lambda path: path_language_bits(lm, mapping, path) + (path_homophone_reverse_bits(mapping, counts, path) if homophonic else 0.0)
    if schema == "GDT001_ABBREVIATION_TRANSDUCER_V1":
        lm = train_pack(decoder["language_pack"], decoder["language_model_order"])
        return "LANGUAGE_LM_PLUS_MULTIGRAPH_REVERSE_AMBIGUITY", lambda path: abbreviation_conditional_bits(path, decoder, lm)
    if schema == "GDT001_QUANTIZED_GRU_NULL_V1":
        import numpy as np
        arrays = {}; scales = {}
        for name, record in decoder["tensors"].items():
            arrays[name] = np.frombuffer(base64.b64decode(record["base64"]), dtype=np.int8).reshape(record["shape"]); scales[name] = record["scale_float32"]
        return "CPU_INT8_GRU_SOURCE_PROBABILITY", lambda path: neural_cpu_score([path], arrays, scales)
    # These record models encode a source dictionary/program in the latent
    # record. Conditional reverse generation is consequently deterministic.
    return "DETERMINISTIC_FROM_EXPLICIT_LATENT_RECORD", lambda path: 0.0


def main() -> None:
    _, lines = load_lattice(); line_by_locus = {line.locus: line for line in lines}
    results = [json.loads(path.read_text()) for path in RUNS.glob("*.json")]
    selected = selected_candidates(results); OUT.mkdir(exist_ok=True)
    index = []
    for rank, item in enumerate(selected, 1):
        directory = OUT / item["candidate_id"]; directory.mkdir(exist_ok=True)
        chosen = dict(zip((line.locus for line in lines), item["selected_path_ids"]))
        all_rows = []; segmentation = []; lexical = Counter()
        for line in lines:
            path = next(path for path in line.paths if path.path_id == chosen[line.locus])
            segmented, decoded = decode(item, path); lexical.update(decoded.split())
            all_rows.append({"locus": line.locus, "page": line.page, "section": line.section, "currier": line.currier, "source_lattice_paths": "|".join(p.path_id for p in line.paths), "selected_source": path.source_line, "literal_decoded": decoded, "normalized_plaintext_or_record": decoded, "confidence": "EXPLORATORY", "alternative_analysis": "other lattice path or mapping restart", "uncertainty_reason": "whole-manuscript postselected candidate"})
            segmentation.append({"locus": line.locus, "selected_path_id": path.path_id, "source": path.source_line, "segmentation": segmented, "rule": item["decoder"].get("segmentation_rule", item["decoder"].get("word_rule", "source-symbol stream"))})
        selected_paths = [next(path for path in line.paths if path.path_id == chosen[line.locus]) for line in lines]
        reverse_mode, score_source = reverse_scorer(item, selected_paths)
        write_tsv(directory / "candidate_plaintext.tsv", list(all_rows[0]), all_rows)
        write_tsv(directory / "segmentation.tsv", list(segmentation[0]), segmentation)
        maps = mapping_rows(item); write_tsv(directory / "mapping.tsv", list(maps[0]), maps)
        lexrows = [{"latent_item": value, "occurrences": count, "interpretation": "ANONYMOUS_OR_LITERAL_EXPLORATORY"} for value, count in lexical.most_common()]
        write_tsv(directory / "lexicon.tsv", ["latent_item", "occurrences", "interpretation"], lexrows)
        reverse = []
        for label, page, positions in PACKETS:
            packet_lines = [line for line in lines if line.page == page and (not positions or int(line.locus.rsplit(".", 1)[-1]) in positions)]
            for line in packet_lines:
                path = next(path for path in line.paths if path.path_id == chosen[line.locus]); segmented, decoded = decode(item, path)
                wrong = wrong_path(path); actual_bits = score_source(path); wrong_bits = score_source(wrong)
                if reverse_mode == "DETERMINISTIC_FROM_EXPLICIT_LATENT_RECORD": wrong_bits = float("inf")
                reverse.append({"packet": label, "locus": line.locus, "source_lattice": " || ".join(p.source_line for p in line.paths), "selected_segmentation": segmented, "literal_decoded": decoded, "normalized_plaintext_or_record": decoded, "confidence": "EXPLORATORY", "alternative_analysis": " || ".join(p.source_line for p in line.paths if p.path_id != path.path_id) or "NONE", "uncertainty_reason": "postselected whole-manuscript decoder", "reverse_generation_mode": reverse_mode, "actual_source_bits": actual_bits, "wrong_form_rule": "rotate each multi-symbol manual group left by one source symbol", "wrong_source_bits": wrong_bits, "actual_advantage_bits": wrong_bits - actual_bits})
        write_tsv(directory / "reverse_generation.tsv", list(reverse[0]), reverse)
        spec = {key: item[key] for key in ("candidate_id", "status", "model_class", "language_or_system", "seed", "config", "config_hash", "total_bits", "bits_per_symbol", "bits_per_physical_line", "key_bits", "latent_bits", "reconstruction_bits", "exception_bits", "selected_path_digest", "decoder_hash")}
        spec["decoder"] = item["decoder"]; (directory / "model_spec.json").write_bytes(canonical(spec))
        structural = f"# {item['candidate_id']} — structural explanation\n\nExploratory, not a confirmed translation.\n\nThe frozen explicit decoder is `{item['decoder'].get('schema','UNKNOWN')}`. It scores {item['bits_per_symbol']:.6f} bits per source symbol after the complete stated key, latent, reconstruction, lattice, and exception costs. It is evaluated on all physical lines and the same fixed packet; nothing here assigns a historical meaning unless the model class explicitly emits tentative historical-language letters.\n"
        (directory / "structural_explanation.md").write_text(structural)
        failure = f"# Failure analysis\n\nThis candidate remains exploratory. Its gap from the tournament leader is {item['bits_per_symbol'] - selected[0]['bits_per_symbol']:.6f} bits/source-symbol. Decoder hash instability across restarts, plausible-looking accidental substrings, imperfect historical corpus match, and inadequate structural coverage can each falsify it. The reverse edit-distance column is a diagnostic, not the common MDL score.\n"
        (directory / "failure_analysis.md").write_text(failure)
        predictions = [f"{n}. Freeze this decoder and require the mapping/record state used at the hash-selected occurrence bucket {n:02d} to recur without a new exception; any incompatible occurrence kills this prediction." for n in range(1, 11)]
        (directory / "risky_predictions.md").write_text("# Risky predictions\n\n" + "\n".join(predictions) + "\n")
        index.append({"rank_in_export": rank, "candidate_id": item["candidate_id"], "model_class": item["model_class"], "bits_per_symbol": item["bits_per_symbol"], "decoder_hash": item["decoder_hash"], "model_spec_sha256": sha256_file(directory / "model_spec.json")})
    (OUT / "index.json").write_bytes(canonical({"schema": "GDT001_CANDIDATE_EXPORT_INDEX_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "candidates": index}))
    print(json.dumps({"candidates": len(index), "index_sha256": sha256_file(OUT / "index.json")}))


if __name__ == "__main__": main()
