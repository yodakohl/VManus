#!/usr/bin/env python3
"""Export ten fixed, inspectable GDT001 decoder packets."""

from __future__ import annotations

import csv
import base64
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

from gdt001_abbreviation_model import decode_path as decode_abbreviation, tokenize_word
from gdt001_core import LETTERS, ROOT, SOURCE_ALPHABET, canonical, load_lattice, sha256_file, train_ngram_logprob
from gdt001_language_models import source_unigrams, train_pack, path_language_bits, path_homophone_reverse_bits
from gdt001_neural_null import cpu_score as neural_cpu_score
from gdt001_nonsemantic_models import predictive_path_bits
from gdt001_record_models import decompose
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_online_context_mixer import PREDICTORS, probability
from run_gdt001_source_selected_nulls import encoded


RUNS = ROOT / ".gdt001/runs"
OUT = ROOT / "candidates"
PACKETS = (
    ("HERBAL_CURRIER_A", "f1r", (1, 2, 3, 4, 5)),
    ("CURRIER_B_PROSE", "f75r", (1, 2, 3, 4, 5)),
    ("BIOLOGICAL_LABEL_RICH_AND_F75V", "f75v", ()),
    ("F57V", "f57v", ()),
    ("F67R2", "f67r2", ()),
    ("CIRCULAR_RADIAL", "f69v", ()),
    ("F116V_STRESS", "f116v", ()),
)


def selected_candidates(results: list[dict[str, Any]], lines) -> list[dict[str, Any]]:
    """Current diverse ten, rather than ten near-duplicate score-grid rows."""
    by_id = {item["candidate_id"]: item for item in results}
    paths = common_selected_paths(lines); path_ids = [path.path_id for path in paths]
    selected = [by_id[name] for name in (
        "nonsemantic_ngram_o2", "nonsemantic_neural_gru_h48_s0072",
        "record_notation_fields", "hybrid_dual_channel_entry_body",
    )]
    with (ROOT / "GDT001_YOLO_LEDGER.tsv").open() as handle:
        ledger = {row["run_id"]: row for row in csv.DictReader(handle, delimiter="\t")}

    def make(run_id, decoder, config):
        row = ledger[run_id]
        return {
            "candidate_id": run_id, "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
            "model_class": row["model_class"], "language_or_system": row["language_or_system"],
            "seed": int(row["seed"]), "config": config, "config_hash": row["config_hash"],
            "total_bits": float(row["total_bits"]), "bits_per_symbol": float(row["bits_per_symbol"]),
            "bits_per_physical_line": float(row["total_bits"]) / len(lines),
            "key_bits": float(row["key_bits"]), "latent_bits": float(row["latent_bits"]),
            "reconstruction_bits": float(row["reconstruction_bits"]),
            "exception_bits": float(row["exception_bits"]), "selected_path_ids": path_ids,
            "selected_path_digest": hashlib.sha256(canonical(path_ids)).hexdigest(),
            "source_symbols": 194324, "decoder_hash": row["decoder_hash"], "decoder": decoder,
        }

    mixer = json.loads((ROOT / "gdt001_online_context_mixer_results.json").read_text())["best"]
    selected.insert(0, make("contextmixer_s0_015625", mixer["decoder"], {"share": 1 / 64, "experts": mixer["decoder"]["experts"]}))
    latent_result = json.loads((ROOT / "gdt001_latent_line_state_results.json").read_text())["best"]
    latent = next(item for item in json.loads((ROOT / "gdt001_latent_line_state_assignments.json").read_text())["runs"] if item["requested_k"] == latent_result["requested_k"] and item["seed"] == latent_result["seed"])
    line_states = [{"locus": line.locus, "state": state} for line, state in zip(lines, latent["assignments"])]
    latent_decoder = {"schema": "GDT001_LATENT_LINE_STATE_DECODER_V1", "order": 2, "rare_symbols": "juz", "line_states": line_states, "state_count": latent["effective_k"], "line_order": "canonical corpus lattice"}
    latent_item = make("latentline_k2_s28104", latent_decoder, {"k": 2, "order": 2})
    latent_item["_line_state_by_locus"] = {row["locus"]: row["state"] for row in line_states}
    selected.append(latent_item)
    sparse_result = json.loads((ROOT / "gdt001_sparse_payload_results.json").read_text())["best_language"]
    sparse = next(item for item in json.loads((ROOT / "gdt001_sparse_payload_mappings.json").read_text())["mappings"] if item["selector"] == sparse_result["selector"] and item["seed"] == sparse_result["seed"])
    sparse_decoder = {"schema": "GDT001_SPARSE_PAYLOAD_LANGUAGE_DECODER_V1", "selector": sparse_result["selector"], "language_pack": "middle_high_german", "language_model_order": 2, "mapping": sparse["mapping"], "other_channel": "literal source reconstruction"}
    selected.append(make("sparse_payload_che_prefix_mhg_s2301", sparse_decoder, {"selector": "CHE_PREFIX", "language": "middle_high_german", "order": 2}))
    scale = min(json.loads((ROOT / "gdt001_group_code_scale_stability.json").read_text())["rows"], key=lambda item: item["total_bits"])
    scale_decoder = {"schema": "GDT001_COMPLETE_GROUP_CHARACTER_DECODER_V1", "language_pack": scale["language"], "language_model_order": scale["order"], "mapping": scale["mapping"], "residual_rule": "unmapped complete groups retained literally"}
    selected.append(make(f"groupcodescale_k512_medieval_czech_s{scale['seed']}", scale_decoder, {"k": 512, "order": 4, "language": "medieval_czech"}))
    group_best = json.loads((ROOT / "gdt001_group_character_code_results.json").read_text())["best"]
    group_map = next(item for item in json.loads((ROOT / "gdt001_group_character_code_mappings.json").read_text())["mappings"] if item["seed"] == group_best["seed"] and item["k"] == group_best["k"] and item["language"] == group_best["language"])
    group_decoder = {"schema": "GDT001_COMPLETE_GROUP_CHARACTER_DECODER_V1", "language_pack": group_best["language"], "language_model_order": 2, "mapping": [{"source_group": item["source_state"], "target": item["target"], "occurrences": item["occurrences"]} for item in group_map["mapping"]], "residual_rule": "unmapped complete groups retained literally"}
    selected.append(make("groupchar_group_character_language_k128_medieval_czech_s19103", group_decoder, {"k": 128, "order": 2, "language": "medieval_czech"}))
    word_best = json.loads((ROOT / "gdt001_word_nomenclator_results.json").read_text())["best"]
    word_map = next(item for item in json.loads((ROOT / "gdt001_word_nomenclator_decoders.json").read_text())["decoders"] if item["seed"] == word_best["seed"] and item["k"] == word_best["k"] and item["language"] == word_best["language"])
    word_decoder = {"schema": "GDT001_WORD_NOMENCLATOR_DECODER_V1", "language_pack": word_best["language"], "mapping": word_map["mapping"], "residual_rule": "unmapped complete groups retained literally"}
    selected.append(make("wordnom_word_nomenclator_k032_o1_middle_high_german_s13101", word_decoder, {"k": 32, "order": 1, "language": "middle_high_german"}))
    assert len(selected) == 10 and len({item["candidate_id"] for item in selected}) == 10
    return selected


def decode(item: dict[str, Any], path, locus="") -> tuple[str, str]:
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
    if schema == "GDT001_COMPLETE_GROUP_CHARACTER_DECODER_V1":
        mapping = {row["source_group"]: row["target"] for row in decoder["mapping"]}
        values = [mapping.get(word, f"<{word}>") for word in path.words]
        return " | ".join(path.words), "".join(values)
    if schema == "GDT001_WORD_NOMENCLATOR_DECODER_V1":
        mapping = {row["source_group"]: row["target_word"] for row in decoder["mapping"]}
        return " | ".join(path.words), " ".join(mapping.get(word, f"<{word}>") for word in path.words)
    if schema == "GDT001_SPARSE_PAYLOAD_LANGUAGE_DECODER_V1":
        mapping = {row["source_unit"]: row["latent_unit"] for row in decoder["mapping"]}
        values = []
        for word in path.words:
            if word.startswith("che") and len(word) > 3:
                _, core, _ = decompose(word); values.append("CHE_PAYLOAD:" + "".join(mapping[character] for character in core))
            else:
                values.append(f"<SOURCE:{word}>")
        return " | ".join(path.words), " ".join(values)
    if schema == "GDT001_LATENT_LINE_STATE_DECODER_V1":
        state = item["_line_state_by_locus"][locus]
        return " | ".join(path.words), f"STATE_{state} :: {path.source_line}"
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
    if schema == "GDT001_COMPLETE_GROUP_CHARACTER_DECODER_V1":
        for row in decoder["mapping"]:
            rows.append({"source_unit": row["source_group"], "latent_or_plaintext_unit": row["target"], "mapping_probability": "EXPLORATORY_DETERMINISTIC_KEY_NOT_POSTERIOR", "context_restriction": "COMPLETE_GROUP", "occurrences": row["occurrences"], "counterexamples": "unmapped groups use the explicit residual channel; restart mapping is unstable"})
    elif schema == "GDT001_WORD_NOMENCLATOR_DECODER_V1":
        for row in decoder["mapping"]:
            rows.append({"source_unit": row["source_group"], "latent_or_plaintext_unit": row["target_word"], "mapping_probability": "EXPLORATORY_DETERMINISTIC_KEY_NOT_POSTERIOR", "context_restriction": "COMPLETE_GROUP", "occurrences": "GLOBAL", "counterexamples": "unmapped groups use the explicit residual channel; restart mapping is unstable"})
    elif schema == "GDT001_SPARSE_PAYLOAD_LANGUAGE_DECODER_V1":
        for row in decoder["mapping"]:
            rows.append({"source_unit": row["source_unit"], "latent_or_plaintext_unit": row["latent_unit"], "mapping_probability": "EXPLORATORY_DETERMINISTIC_KEY_NOT_POSTERIOR", "context_restriction": "CORE_OF_CHE_PREFIX_GROUP_ONLY", "occurrences": row["occurrences"], "counterexamples": "all nonselected groups stay in a literal source channel; restart mapping is unstable"})
    elif "mapping" in decoder:
        for row in decoder["mapping"]:
            rows.append({
                "source_unit": row.get("source_unit", ""), "latent_or_plaintext_unit": row.get("latent_unit", row.get("plaintext_unit", "")),
                "mapping_probability": row.get("mapping_probability", 1.0), "context_restriction": row.get("context_restriction", "ALL"),
                "occurrences": row.get("occurrences", 0), "counterexamples": "all nonchosen mappings under frozen deterministic key",
            })
    elif schema == "GDT001_RECORD_NOTATION_V1":
        for kind, key, source in (("OP", "anonymous_operators", "source_prefix"), ("STATE", "anonymous_states", "source_suffix"), ("VALUE", "anonymous_values", "source_core")):
            for row in decoder[key]: rows.append({"source_unit": row[source], "latent_or_plaintext_unit": row[f"latent_{'operator' if kind == 'OP' else 'state' if kind == 'STATE' else 'value'}"], "mapping_probability": 1.0, "context_restriction": kind, "occurrences": row["occurrences"], "counterexamples": "none admitted; unknown inventory entries fail"})
    elif schema == "GDT001_LATENT_LINE_STATE_DECODER_V1":
        counts = Counter(row["state"] for row in decoder["line_states"])
        for state, count in sorted(counts.items()):
            rows.append({"source_unit": "PHYSICAL_LINE", "latent_or_plaintext_unit": f"STATE_{state}", "mapping_probability": "EXPLORATORY_LATENT_ASSIGNMENT_NOT_POSTERIOR", "context_restriction": "ONE_STATE_PER_CANONICAL_LOCUS", "occurrences": count, "counterexamples": "restart assignments differ"})
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
    if schema == "GDT001_ONLINE_CONTEXT_MIXER_DECODER_V1":
        # This scorer is stateful in the canonical serialization. A separate
        # packet pass below records actual and wrong-form prequential costs.
        return "CAUSAL_CONTEXT_MIXER_CANONICAL_PREFIX", None
    return "REVERSE_GENERATION_NOT_IMPLEMENTED_CANDIDATE_FAILS_REQUIREMENT", None


def mixer_packet_costs(lines, paths, share, packet_loci):
    sequences, _, _, active, _, _ = encoded(paths, frozenset("juz")); alphabet = len(active) + 1; bos = alphabet
    shared = defaultdict(Counter); longer = defaultdict(Counter)
    metadata = {name: defaultdict(Counter) for name, _ in PREDICTORS[1:]}; weights = {}; actual_output = {}; wrong_output = {}

    def branch_cost(line, sequence):
        local_shared = defaultdict(Counter); local_longer = defaultdict(Counter)
        local_metadata = {name: defaultdict(Counter) for name, _ in PREDICTORS[1:]}; local_weights = {}; bits = 0.0; history = [bos, bos, bos]
        for token in sequence:
            context = tuple(history[-2:]); keys = [(context, history[-3]), *[(context, getattr(line, field) or "_") for _, field in PREDICTORS[1:]]]
            base_counters = [shared[context], longer[keys[0]], *[metadata[name][key] for (name, _), key in zip(PREDICTORS[1:], keys[1:])]]
            delta_counters = [local_shared[context], local_longer[keys[0]], *[local_metadata[name][key] for (name, _), key in zip(PREDICTORS[1:], keys[1:])]]
            probs = [((base[token] + delta[token] + .5) / (sum(base.values()) + sum(delta.values()) + .5 * alphabet)) for base, delta in zip(base_counters, delta_counters)]
            current = local_weights.get(context, weights.get(context, [1 / len(probs)] * len(probs))); mixture = sum(weight * prob for weight, prob in zip(current, probs))
            bits -= math.log2(mixture); posterior = [weight * prob / mixture for weight, prob in zip(current, probs)]
            local_weights[context] = [(1 - share) * value + share / len(probs) for value in posterior]
            for counter in delta_counters: counter[token] += 1
            history = history[1:] + [token]
        return bits

    for line, sequence in zip(lines, sequences):
        if line.locus in packet_loci:
            transformed = []
            for word in paths[len(actual_output)].words:
                changed = word[1:] + word[:1] if len(word) > 1 else word
                transformed.extend(active.index(character) for character in changed if character not in "juz")
                transformed.append(len(active))
            wrong_output[line.locus] = branch_cost(line, transformed[:-1])
        history = [bos, bos, bos]; bits = 0.0
        for token in sequence:
            context = tuple(history[-2:]); counters = [shared[context], longer[(context, history[-3])]]
            counters += [metadata[name][(context, getattr(line, field) or "_")] for name, field in PREDICTORS[1:]]
            probs = [probability(counter, token, alphabet) for counter in counters]
            current = weights.setdefault(context, [1 / len(counters)] * len(counters)); mixture = sum(weight * prob for weight, prob in zip(current, probs))
            bits -= math.log2(mixture); posterior = [weight * prob / mixture for weight, prob in zip(current, probs)]
            weights[context] = [(1 - share) * value + share / len(counters) for value in posterior]
            for counter in counters: counter[token] += 1
            history = history[1:] + [token]
        actual_output[line.locus] = bits
    return actual_output, wrong_output


def main() -> None:
    _, lines = load_lattice(); line_by_locus = {line.locus: line for line in lines}
    results = [json.loads(path.read_text()) for path in RUNS.glob("*.json")]
    selected = selected_candidates(results, lines); OUT.mkdir(exist_ok=True)
    retained = {item["candidate_id"] for item in selected}
    for directory in OUT.iterdir():
        if directory.is_dir() and directory.name not in retained:
            for child in directory.iterdir(): child.unlink()
            directory.rmdir()
    index = []
    for rank, item in enumerate(selected, 1):
        directory = OUT / item["candidate_id"]; directory.mkdir(exist_ok=True)
        chosen = dict(zip((line.locus for line in lines), item["selected_path_ids"]))
        all_rows = []; segmentation = []; lexical = Counter()
        for line in lines:
            path = next(path for path in line.paths if path.path_id == chosen[line.locus])
            segmented, decoded = decode(item, path, line.locus); lexical.update(decoded.split())
            all_rows.append({"locus": line.locus, "page": line.page, "section": line.section, "currier": line.currier, "source_lattice_paths": "|".join(p.path_id for p in line.paths), "selected_source": path.source_line, "literal_decoded": decoded, "normalized_plaintext_or_record": decoded, "confidence": "EXPLORATORY", "alternative_analysis": "other lattice path or mapping restart", "uncertainty_reason": "whole-manuscript postselected candidate"})
            segmentation.append({"locus": line.locus, "selected_path_id": path.path_id, "source": path.source_line, "segmentation": segmented, "rule": item["decoder"].get("segmentation_rule", item["decoder"].get("word_rule", "source-symbol stream"))})
        selected_paths = [next(path for path in line.paths if path.path_id == chosen[line.locus]) for line in lines]
        reverse_mode, score_source = reverse_scorer(item, selected_paths)
        mixer_actual = mixer_wrong = None
        if reverse_mode == "CAUSAL_CONTEXT_MIXER_CANONICAL_PREFIX":
            packet_loci = {line.locus for _, page, positions in PACKETS for line in lines if line.page == page and (not positions or int(line.locus.rsplit(".", 1)[-1]) in positions)}
            mixer_actual, mixer_wrong = mixer_packet_costs(lines, selected_paths, item["decoder"]["share"], packet_loci)
        write_tsv(directory / "candidate_plaintext.tsv", list(all_rows[0]), all_rows)
        write_tsv(directory / "segmentation.tsv", list(segmentation[0]), segmentation)
        maps = mapping_rows(item); write_tsv(directory / "mapping.tsv", list(maps[0]), maps)
        lexrows = [{"latent_item": value, "occurrences": count, "interpretation": "ANONYMOUS_OR_LITERAL_EXPLORATORY"} for value, count in lexical.most_common()]
        write_tsv(directory / "lexicon.tsv", ["latent_item", "occurrences", "interpretation"], lexrows)
        reverse = []
        for label, page, positions in PACKETS:
            packet_lines = [line for line in lines if line.page == page and (not positions or int(line.locus.rsplit(".", 1)[-1]) in positions)]
            for line in packet_lines:
                path = next(path for path in line.paths if path.path_id == chosen[line.locus]); segmented, decoded = decode(item, path, line.locus)
                wrong = wrong_path(path)
                if reverse_mode == "CAUSAL_CONTEXT_MIXER_CANONICAL_PREFIX":
                    actual_bits, wrong_bits = mixer_actual[line.locus], mixer_wrong[line.locus]
                elif score_source is not None:
                    actual_bits = score_source(path); wrong_bits = score_source(wrong)
                else:
                    actual_bits = wrong_bits = "NOT_COMPUTED"
                advantage = wrong_bits - actual_bits if actual_bits != "NOT_COMPUTED" else "NOT_COMPUTED"
                reverse.append({"packet": label, "locus": line.locus, "source_lattice": " || ".join(p.source_line for p in line.paths), "selected_segmentation": segmented, "literal_decoded": decoded, "normalized_plaintext_or_record": decoded, "confidence": "EXPLORATORY", "alternative_analysis": " || ".join(p.source_line for p in line.paths if p.path_id != path.path_id) or "NONE", "uncertainty_reason": "postselected whole-manuscript decoder", "reverse_generation_mode": reverse_mode, "actual_source_bits": actual_bits, "wrong_form_rule": "rotate each multi-symbol manual group left by one source symbol", "wrong_source_bits": wrong_bits, "actual_advantage_bits": advantage})
        write_tsv(directory / "reverse_generation.tsv", list(reverse[0]), reverse)
        spec = {key: item[key] for key in ("candidate_id", "status", "model_class", "language_or_system", "seed", "config", "config_hash", "total_bits", "bits_per_symbol", "bits_per_physical_line", "key_bits", "latent_bits", "reconstruction_bits", "exception_bits", "selected_path_digest")}
        spec["origin_run_decoder_hash"] = item["decoder_hash"]
        spec["decoder"] = item["decoder"]
        spec["decoder_hash"] = hashlib.sha256(canonical(spec["decoder"])).hexdigest()
        (directory / "model_spec.json").write_bytes(canonical(spec))
        structural = f"# {item['candidate_id']} — structural explanation\n\nExploratory, not a confirmed translation.\n\nThe frozen explicit decoder is `{item['decoder'].get('schema','UNKNOWN')}`. It scores {item['bits_per_symbol']:.6f} bits per source symbol after the complete stated key, latent, reconstruction, lattice, and exception costs. It is evaluated on all physical lines and the same fixed packet; nothing here assigns a historical meaning unless the model class explicitly emits tentative historical-language letters.\n"
        (directory / "structural_explanation.md").write_text(structural)
        gap = item['bits_per_symbol'] - selected[0]['bits_per_symbol']
        failure = f"# Failure analysis\n\nThis candidate remains exploratory and is **not a translation**. Its paid gap from the current branch leader is {gap:.6f} bits/source-symbol ({item['total_bits'] - selected[0]['total_bits']:.1f} bits). Its literal output is a model state, source reconstruction, or postselected historical-corpus assignment, never a verified reading. It fails if its retained decoder/hash changes across prescribed restarts, if the real-manuscript advantage is equalled by a frozen control, or if its reverse probability fails on the named fixed packet. No output may be silently repaired.\n"
        (directory / "failure_analysis.md").write_text(failure)
        loci = [row["locus"] for row in reverse[:10]]
        if all(row["wrong_source_bits"] != "NOT_COMPUTED" and math.isfinite(float(row["wrong_source_bits"])) for row in reverse):
            predictions = [f"{n}. At frozen locus `{locus}`, require finite `wrong_source_bits > actual_source_bits` under the exact wrong-form rule in `reverse_generation.tsv`; a non-finite score, equality, or reversal kills this prediction." for n, locus in enumerate(loci, 1)]
        else:
            predictions = [f"{n}. At frozen locus `{locus}`, require a future independent conditional reverse scorer for this exact exported decoder to return finite actual and wrong-form costs with `wrong_source_bits > actual_source_bits`; absence, equality, or reversal kills this prediction and the candidate." for n, locus in enumerate(loci, 1)]
        (directory / "risky_predictions.md").write_text("# Risky predictions\n\n" + "\n".join(predictions) + "\n")
        artifact_hashes = {name: sha256_file(directory / name) for name in ("model_spec.json", "mapping.tsv", "segmentation.tsv", "candidate_plaintext.tsv", "lexicon.tsv", "reverse_generation.tsv", "structural_explanation.md", "failure_analysis.md", "risky_predictions.md")}
        index.append({"rank_in_export": rank, "candidate_id": item["candidate_id"], "model_class": item["model_class"], "bits_per_symbol": item["bits_per_symbol"], "decoder_hash": spec["decoder_hash"], "origin_run_decoder_hash": item["decoder_hash"], "artifact_sha256": artifact_hashes})
    (OUT / "index.json").write_bytes(canonical({"schema": "GDT001_CANDIDATE_EXPORT_INDEX_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "candidates": index}))
    print(json.dumps({"candidates": len(index), "index_sha256": sha256_file(OUT / "index.json")}))


if __name__ == "__main__": main()
