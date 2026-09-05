#!/usr/bin/env python3
"""Independent source preparation and shared-world orthography control.

Only the reference changes between NATIVE and COLLAPSED. No Voynich inputs,
fitted output or recovery score are read. Truth is written only to sealed/.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import types


EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
SPEC_PATH = Path(__file__).with_name("ENCODER_SPEC.json")
UDANTE_COMMIT = "e02420457780c6fbb503ba39a7d8798ab6a8645c"
UDANTE_URL = "https://github.com/UniversalDependencies/UD_Latin-UDante.git"
HELPER_RELATIVE = "experiments/yolo/gdt832_joint_family_context_control/src/prepare.py"
HELPER_SHA256 = "a8ca27308ab3f1fbeda1eef756c71081b602020b8b59350ba8661efd79536b77"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def _bound_helper():
    path = ROOT / HELPER_RELATIVE
    if sha(path) != HELPER_SHA256:
        raise RuntimeError("Frozen GDT832 source helper changed")
    module = types.ModuleType("_gdt833_bound_gdt832_source_helper")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


HELPER = _bound_helper()
normalize_words = HELPER.normalized_words


def pair_reference(native_sentences):
    """Pure paired intervention, preserving its input and all word positions."""
    native = [list(sentence) for sentence in native_sentences]
    collapsed = [[word.replace("v", "u") for word in sentence] for sentence in native_sentences]
    assert len(native) == len(collapsed)
    assert all(len(a) == len(b) for a, b in zip(native, collapsed))
    assert all(b == a.replace("v", "u") for x, y in zip(native, collapsed) for a, b in zip(x, y))
    return native, collapsed


def make_key(seed, spec):
    """The source-independent randomization is identical to GDT832."""
    rng = random.Random(seed)
    result = {}
    for kind, values in [("L", list(spec["letter_alphabet"])), ("S", spec["suffix_values"]), ("W", spec["wholeword_values"])]:
        ids = [f"{kind}{i:02d}" for i in range(len(values))]
        rng.shuffle(ids)
        result.update({card: value for value, card in zip(values, ids)})
    return result


def encode_word(word, decode_map, spec):
    inverse = {(card[0], value): card for card, value in decode_map.items()}
    return [inverse[atom] for atom in HELPER.logical_encode_word(word, spec)]


def build_world(seed, paragraphs, spec):
    """No reference argument: both reference conditions share these outputs."""
    key = make_key(seed, spec)
    payloads = {}
    for split in ("discovery", "held"):
        rows = []
        for paragraph in paragraphs:
            if paragraph["split"] != split:
                continue
            coded = [encode_word(word, key, spec) for word in paragraph["words"]]
            if ["".join(key[a] for a in atoms) for atoms in coded] != paragraph["words"]:
                raise AssertionError("Original-spelling roundtrip failed")
            rows.append({"paragraph_id": paragraph["paragraph_id"], "words": coded})
        payloads[split] = {"schema": "GDT833_CIPHERTEXT_V1", "world_id": seed, "split": split, "paragraphs": rows}
    truth = {"schema": "GDT833_WORLD_TRUTH_V1", "world_id": seed, "decode_map": key, "paragraphs": copy.deepcopy(paragraphs)}
    return payloads, truth


def verify_source(path, fetch):
    if not path.exists():
        if not fetch:
            raise RuntimeError("Missing pinned UDante source; pass --source-dir or --fetch-source")
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", UDANTE_URL, str(path)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(path), "checkout", "--detach", UDANTE_COMMIT], check=True, capture_output=True)
    commit = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if commit != UDANTE_COMMIT:
        raise RuntimeError("UDante commit mismatch")
    names = ["la_udante-ud-train.conllu", "la_udante-ud-test.conllu", "README.md", "LICENSE.txt"]
    for name in names:
        committed = subprocess.check_output(["git", "-C", str(path), "show", f"{UDANTE_COMMIT}:{name}"])
        if (path / name).read_bytes() != committed:
            raise RuntimeError("Pinned UDante source file modified")


def source_phase(source_dir, output, spec, fetch=False):
    verify_source(source_dir, fetch)
    paragraphs, excluded, repeated = [], [], []
    occurrences = Counter()
    last_citation = None
    selected_sentences = 0
    for comments, rows in HELPER.sentences(source_dir / "la_udante-ud-test.conllu"):
        if not comments.get("sent_id", "").startswith(spec["control_work"] + "-"):
            raise RuntimeError("Unexpected work in the fixed DVE control source")
        selected_sentences += 1
        citation = comments.get("citation_hierarchy", "")
        pieces = citation.split(",")
        if len(pieces) != 3 or not pieces[2].startswith("Paragraphus_"):
            raise RuntimeError("Unexpected fixed control citation structure")
        book, chapter, paragraph = pieces
        if book == spec["discovery_book"]:
            split = "discovery"
        elif book in spec["held_books"]:
            split = "held"
        else:
            raise RuntimeError("Unexpected fixed control book")
        if citation != last_citation:
            occurrences[citation] += 1
            occurrence = occurrences[citation]
            paragraph_id = spec["control_work"] + ":" + ":".join(pieces)
            if occurrence > 1:
                paragraph_id += f":occurrence_{occurrence}"
                repeated.append({"citation_hierarchy": citation, "occurrence": occurrence,
                    "paragraph_id": paragraph_id, "first_sentence_id": comments["sent_id"]})
            paragraphs.append({"paragraph_id": paragraph_id, "book": book, "chapter": chapter,
                "citation_hierarchy": citation, "citation_occurrence": occurrence, "split": split,
                "words": [], "lemma_sets": [], "annotation_status": [], "source_sentence_ids": [],
                "sentence_word_spans": [], "unsupported": False})
            last_citation = citation
        row = paragraphs[-1]
        words, bad, analyses, statuses = HELPER.annotation_join(comments, rows)
        start = len(row["words"])
        row["words"].extend(words)
        row["lemma_sets"].extend(analyses)
        row["annotation_status"].extend(statuses)
        row["source_sentence_ids"].append(comments["sent_id"])
        row["sentence_word_spans"].append([start, start + len(words)])
        row["unsupported"] |= bad
    kept = []
    for row in paragraphs:
        if row.pop("unsupported"):
            excluded.append({"paragraph_id": row["paragraph_id"], "split": row["split"], "reason": "UNREPRESENTABLE_ALPHABETIC_WORD", "word_count": len(row["words"])})
        else:
            kept.append(row)
    paragraphs = kept
    width = spec["deduplication_ngram_words"]
    control_ngrams = {gram for row in paragraphs for gram in HELPER.windows(row["words"], width)}
    reference, reference_ids, removed_ids, unsupported_ids = [], [], [], []
    for comments, rows in HELPER.sentences(source_dir / "la_udante-ud-train.conllu"):
        if not comments.get("sent_id", "").startswith(spec["reference_work"] + "-"):
            continue
        words, bad = normalize_words(comments["text"])
        if bad:
            unsupported_ids.append(comments["sent_id"])
            continue
        if any(gram in control_ngrams for gram in HELPER.windows(words, width)):
            removed_ids.append(comments["sent_id"])
            continue
        reference.append(words)
        reference_ids.append(comments["sent_id"])
    native, collapsed = pair_reference(reference)
    if native != reference:
        raise AssertionError("Native reference changed")
    counts = Counter(word for sentence in native for word in sentence)
    pool = sorted((word for word in counts if spec["wholeword_candidate_minimum_characters"] <= len(word) <= spec["wholeword_candidate_maximum_characters"]), key=lambda word: (-counts[word], word))[:spec["wholeword_candidate_pool_size"]]
    missing_wholes = set(spec["wholeword_values"]) - set(pool)
    missing_suffixes = set(spec["suffix_values"]) - set(spec["suffix_candidate_pool"])
    discovery_forms = {word for row in paragraphs if row["split"] == "discovery" for word in row["words"]}
    discovery_lemmas = {key for row in paragraphs if row["split"] == "discovery" for analysis in row["lemma_sets"] if analysis is not None for key in analysis}
    support = {split: Counter() for split in ("discovery", "held")}
    partitions = {}
    for split in support:
        selected = [row for row in paragraphs if row["split"] == split]
        for row in selected:
            row["novel_form"] = [word not in discovery_forms for word in row["words"]]
            row["novel_lemma"] = [None if analysis is None or len(analysis) != 1 else analysis[0] not in discovery_lemmas for analysis in row["lemma_sets"]]
            row["composed"] = [word not in spec["wholeword_values"] for word in row["words"]]
            row["contains_v"] = ["v" in word for word in row["words"]]
            for word in row["words"]:
                support[split].update(HELPER.logical_encode_word(word, spec))
        partitions[split] = {"paragraphs": len(selected), "sentences": sum(len(row["source_sentence_ids"]) for row in selected),
            "words": sum(len(row["words"]) for row in selected), "types": len({word for row in selected for word in row["words"]}),
            "v_containing_words": sum(sum(row["contains_v"]) for row in selected),
            "literal_v_occurrences": sum(word.count("v") for row in selected for word in row["words"]),
            "novel_composed_form_occurrences": sum(new and composed for row in selected for new, composed in zip(row["novel_form"], row["composed"])),
            "known_novel_lemma_occurrences": sum(flag is True for row in selected for flag in row["novel_lemma"]),
            "unknown_lemma_occurrences": sum(flag is None for row in selected for flag in row["novel_lemma"]),
            "annotation_status_counts": dict(Counter(status for row in selected for status in row["annotation_status"]))}
    active = set(support["discovery"]) | set(support["held"])
    support_meta = {}
    for kind, nominal in [("L", len(spec["letter_alphabet"])), ("S", len(spec["suffix_values"])), ("W", len(spec["wholeword_values"]))]:
        active_kind = {atom for atom in active if atom[0] == kind}
        held_kind = {atom for atom in support["held"] if atom[0] == kind}
        support_meta[kind] = {"nominal_rules": nominal, "active_rules": len(active_kind), "unobserved_unscored_rules": nominal - len(active_kind),
            "minimum_discovery_occurrences_active_rules": min((support["discovery"][atom] for atom in active_kind), default=0),
            "minimum_discovery_occurrences_held_active_rules": min((support["discovery"][atom] for atom in held_kind), default=0),
            "held_only_rules": sum(support["discovery"][atom] == 0 for atom in held_kind)}
    reference_v = sum(word.count("v") for sentence in native for word in sentence)
    gates = {
        "discovery_paragraphs": partitions["discovery"]["paragraphs"] >= spec["minimum_discovery_paragraphs"],
        "held_paragraphs": partitions["held"]["paragraphs"] >= spec["minimum_held_paragraphs"],
        "active_suffix_discovery_coverage": support_meta["S"]["minimum_discovery_occurrences_active_rules"] >= spec["minimum_discovery_occurrences_active_suffix_or_wholeword"],
        "active_wholeword_discovery_coverage": support_meta["W"]["minimum_discovery_occurrences_active_rules"] >= spec["minimum_discovery_occurrences_active_suffix_or_wholeword"],
        "held_active_letter_discovery_coverage": support_meta["L"]["minimum_discovery_occurrences_held_active_rules"] >= spec["minimum_discovery_occurrences_held_active_letter"],
        "wholeword_truth_in_native_candidate_pool": not missing_wholes,
        "suffix_truth_in_frozen_candidate_pool": not missing_suffixes,
        "discovery_v_containing_words": partitions["discovery"]["v_containing_words"] >= spec["minimum_discovery_v_containing_words"],
        "held_v_containing_words": partitions["held"]["v_containing_words"] >= spec["minimum_held_v_containing_words"],
        "reference_literal_v": reference_v >= spec["minimum_reference_literal_v"],
        "held_novel_composed_forms": partitions["held"]["novel_composed_form_occurrences"] >= spec["minimum_held_novel_composed_form_occurrences"],
        "held_known_novel_lemmas": partitions["held"]["known_novel_lemma_occurrences"] >= spec["minimum_held_unambiguous_novel_lemma_occurrences"],
        "exact_paired_reference_intervention": all(b == a.replace("v", "u") for ns, cs in zip(native, collapsed) for a, b in zip(ns, cs)) and len(native) == len(collapsed) and all(len(a) == len(b) for a, b in zip(native, collapsed)),
    }
    prepared = output / "prepared"
    prepared.mkdir(parents=True, exist_ok=True)
    for name, sentences in [("reference_native.jsonl", native), ("reference_collapsed.jsonl", collapsed)]:
        (prepared / name).write_bytes(b"".join(canonical(row) for row in sentences))
    save_json(prepared / "reference_ids.json", reference_ids)
    save_json(prepared / "families.json", {})
    save_json(prepared / "candidates.json", {"suffix_pool": spec["suffix_candidate_pool"], "wholeword_pool": pool})
    truth = {"schema": "GDT833_SOURCE_TRUTH_V1", "paragraphs": paragraphs, "reference_removed_overlap_sentence_ids": removed_ids,
        "reference_unsupported_sentence_ids": unsupported_ids, "missing_wholeword_candidates": sorted(missing_wholes),
        "logical_rule_support": {split: [{"kind": kind, "value": value, "count": n} for (kind, value), n in sorted(counter.items())] for split, counter in support.items()}}
    save_json(output / "sealed/source_truth.json", truth)
    source_files = ["la_udante-ud-train.conllu", "la_udante-ud-test.conllu", "README.md", "LICENSE.txt"]
    manifest = {"schema": "GDT833_SOURCE_MANIFEST_V1", "repository": UDANTE_URL, "commit": UDANTE_COMMIT,
        "license": "CC BY-NC-SA 3.0", "reference_source": "la_udante-ud-train.conllu:Mon", "control_source": "la_udante-ud-test.conllu:DVE",
        "files": {name: {"sha256": sha(source_dir / name), "bytes": (source_dir / name).stat().st_size} for name in source_files},
        "frozen_helper": {"path": HELPER_RELATIVE, "sha256": HELPER_SHA256}}
    save_json(output / "sources/MANIFEST.json", manifest)
    for name in ("README.md", "LICENSE.txt"):
        (output / "sources" / name).write_bytes((source_dir / name).read_bytes())
    notes = ["# GDT833 source notes", "", "The fixed source is the pinned UDante repository. All Monarchia sentences form the reference; fresh De vulgari eloquentia Book I is discovery and Book II is held. Whole works and their original sentence/word order are preserved. DVE includes quoted vernacular material; these words are not removed. This is a historical-text control, not a claim that every quoted word is Latin.", "", "Control paragraph units are maximal contiguous citation runs. Five reuse events involve four distinct citation labels; original labels and sentence IDs are retained and occurrence suffixes disambiguate runs. No chapter correction is inferred.", "", "| Original citation | Occurrence | Run ID | First source sentence |", "|---|---:|---|---|"]
    for row in repeated:
        notes.append(f"| {row['citation_hierarchy']} | {row['occurrence']} | {row['paragraph_id']} | {row['first_sentence_id']} |")
    notes.extend(["", "The NATIVE and COLLAPSED reference files contain identical sentence and word positions. The only difference is exact v-to-u replacement in each reference word. Candidate suffixes and the native-frequency wholeword pool are shared. families.json is empty in both arms. The original control plaintext, ciphertext and recovery spelling are never collapsed.", "", "Any unrepresentable alphabetic word excludes its complete control citation run; no individual word is dropped. Exact twenty-word overlaps remove reference sentences only. All exclusions/counts are recorded before key generation. The GDT832 normalizer and annotation join are used through a fixed SHA256 import; no predecessor file is changed.", "", "Source annotation ambiguity is retained as unknown when a written word has multiple syntactic components or an uncertain alignment. Novel-lemma comparisons use all supported discovery analyses, and held novelty requires one unambiguous join. These annotations are evaluator truth only, not decoder inputs.", ""])
    (output / "sources/SOURCE_NOTES.md").write_text("\n".join(notes), encoding="utf-8")
    capacity = {"schema": "GDT833_SOURCE_CAPACITY_V1", "status": "SOURCE_CAPACITY_PASS" if all(gates.values()) else "SOURCE_CAPACITY_STOP",
        "gates": gates, "failed_gates": sorted(k for k, v in gates.items() if not v), "key_generated": False,
        "encoder_spec_sha256": sha(SPEC_PATH), "sources_manifest_sha256": sha(output / "sources/MANIFEST.json"),
        "source_truth_sha256": sha(output / "sealed/source_truth.json"),
        "prepared_input_sha256": {name: sha(prepared / name) for name in ("reference_native.jsonl", "reference_collapsed.jsonl", "reference_ids.json", "families.json", "candidates.json")},
        "reference_sentences": len(native), "reference_words": sum(map(len, native)), "reference_native_v_occurrences": reference_v,
        "reference_collapsed_v_occurrences": sum(word.count("v") for sentence in collapsed for word in sentence),
        "reference_overlap_removed_sentences": len(removed_ids), "reference_unsupported_removed_sentences": len(unsupported_ids),
        "control_sentences_before_exclusion": selected_sentences, "excluded_control_paragraphs": excluded,
        "control_noncontiguous_citation_reuse_events": len(repeated), "control_distinct_reused_citation_labels": len({row["citation_hierarchy"] for row in repeated}),
        "paragraph_unit": spec["paragraph_unit"], "partitions": partitions, "rule_support": support_meta,
        "candidate_pool_size": len(pool), "missing_wholeword_candidate_count": len(missing_wholes),
        "reference_pair_preserves_sentence_and_word_positions": True,
        "no_control_or_gold_orthography_change": True, "family_factors_empty_in_both_conditions": True}
    save_json(prepared / "CAPACITY.json", capacity)
    return capacity


def generation_phase(output, spec):
    capacity = json.loads((output / "prepared/CAPACITY.json").read_text())
    if capacity["status"] != "SOURCE_CAPACITY_PASS" or capacity["encoder_spec_sha256"] != sha(SPEC_PATH):
        raise RuntimeError("Source capacity must pass under this fixed encoder")
    for name, expected in capacity["prepared_input_sha256"].items():
        if sha(output / "prepared" / name) != expected:
            raise RuntimeError("Bound prepared input changed")
    source_truth_path = output / "sealed/source_truth.json"
    if sha(source_truth_path) != capacity["source_truth_sha256"]:
        raise RuntimeError("Bound original source truth changed")
    paragraphs = json.loads(source_truth_path.read_text())["paragraphs"]
    worlds = []
    for seed in spec["world_seeds"]:
        payloads, truth = build_world(seed, paragraphs, spec)
        hashes = {}
        observed = set()
        for split, payload in payloads.items():
            path = output / f"prepared/world_{seed}_{split}.json"
            save_json(path, payload)
            hashes[split] = sha(path)
            observed.update(a for row in payload["paragraphs"] for word in row["words"] for a in word)
        truth.update({"source_truth_sha256": sha(source_truth_path), "encoder_spec_sha256": sha(SPEC_PATH), "ciphertext_sha256": hashes})
        save_json(output / f"sealed/world_{seed}_truth.json", truth)
        worlds.append({"world_id": seed, "ciphertext_sha256": hashes, "observed_primitive_ids": sorted(observed),
            "unobserved_unscored_primitive_ids": sorted(set(truth["decode_map"]) - observed), "original_spelling_roundtrip_pass": True})
    summary = {"schema": "GDT833_GENERATION_V1", "status": "SHARED_BLINDED_CONTROL_GENERATED", "worlds": worlds,
        "capacity_sha256": sha(output / "prepared/CAPACITY.json"), "encoder_spec_sha256": sha(SPEC_PATH),
        "ciphertext_key_and_original_gold_shared_between_reference_conditions": True,
        "control_or_gold_v_to_u_applied": False, "plaintext_or_key_values_in_console": False}
    save_json(output / "prepared/GENERATION.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=ROOT / ".gdt833/repos/latin_udante")
    parser.add_argument("--fetch-source", action="store_true")
    parser.add_argument("--output", type=Path, default=EXPERIMENT)
    parser.add_argument("--phase", choices=["sources", "generate", "all"], default="all")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text())
    if args.phase in ("sources", "all"):
        capacity = source_phase(args.source_dir, args.output, spec, args.fetch_source)
        print(json.dumps(capacity, sort_keys=True))
        if capacity["status"] != "SOURCE_CAPACITY_PASS":
            return
    if args.phase in ("generate", "all"):
        print(json.dumps(generation_phase(args.output, spec), sort_keys=True))


if __name__ == "__main__":
    main()
