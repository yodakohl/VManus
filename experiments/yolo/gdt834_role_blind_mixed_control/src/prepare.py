#!/usr/bin/env python3
"""Independent fresh historical source and typed/opaque matched controls.

No fitting or Voynich data access. Source gates run before any key generation.
Every public observation omits plaintext; opaque observations also omit roles.
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
SOURCE_FILE = "la_udante-ud-dev.conllu"
SOURCE_SHA256 = "11d96611add7862a886ca77bebc4bb32c8d314a2f6eec6f1a6a2d116abaae7e4"
HELPER_RELATIVE = "experiments/yolo/gdt833_reference_orthography_intervention/src/prepare.py"
HELPER_SHA256 = "6360504e06bdf13a67177b3071db1ca1421184105e702d8ef0017dda5d8c5494"
REFERENCE_BASE = "experiments/yolo/gdt833_reference_orthography_intervention/prepared"
REFERENCE_BINDINGS = {
    "reference.jsonl": ("reference_native.jsonl", "dc9c57b32779b4be64911c042d8ad468f090ebbebcd9686d71a7ba422263b3e1"),
    "reference_ids.json": ("reference_ids.json", "b759b59a92bde4e56efc83db8b702eb37a835abecf57f18a37a92ca097010526"),
    "candidates.json": ("candidates.json", "66d920e39056d6136a92c8a4509bb0d24c0d9ca9c1e01fdb9794d2f3ce663e86"),
    "families.json": ("families.json", "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def _helper():
    path = ROOT / HELPER_RELATIVE
    if sha(path) != HELPER_SHA256:
        raise RuntimeError("Frozen GDT833 helper changed")
    module = types.ModuleType("_gdt834_frozen_gdt833_helper")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


HELPER = _helper()
SOURCE_HELPER = HELPER.HELPER


def make_maps(seed, spec):
    """Pure source-independent typed key plus independent 38-way aliasing."""
    typed_key = HELPER.make_key(seed, spec)
    typed_ids = sorted(typed_key)
    opaque_ids = [f"X{i:02d}" for i in range(len(typed_ids))]
    random.Random(seed + spec["opaque_shuffle_seed_offset"]).shuffle(opaque_ids)
    opaque_to_typed = dict(zip(opaque_ids, typed_ids))
    opaque_key = {opaque: {"role": typed[0], "output": typed_key[typed]} for opaque, typed in opaque_to_typed.items()}
    return typed_key, opaque_to_typed, opaque_key


def build_world(seed, paragraphs, spec):
    typed_key, opaque_to_typed, opaque_key = make_maps(seed, spec)
    typed_to_opaque = {typed: opaque for opaque, typed in opaque_to_typed.items()}
    payloads = {}
    for split in ("discovery", "held"):
        typed_rows, opaque_rows = [], []
        for paragraph in paragraphs:
            if paragraph["split"] != split:
                continue
            typed_words = [HELPER.encode_word(word, typed_key, spec) for word in paragraph["words"]]
            opaque_words = [[typed_to_opaque[atom] for atom in word] for word in typed_words]
            if ["".join(opaque_key[atom]["output"] for atom in word) for word in opaque_words] != paragraph["words"]:
                raise AssertionError("Original-spelling opaque roundtrip failed")
            if [[opaque_to_typed[atom] for atom in word] for word in opaque_words] != typed_words:
                raise AssertionError("Typed and opaque words differ beyond ID aliasing")
            typed_rows.append({"paragraph_id": paragraph["paragraph_id"], "words": typed_words})
            opaque_rows.append({"paragraph_id": paragraph["paragraph_id"], "words": opaque_words})
        payloads["typed_" + split] = {"schema": "GDT834_TYPED_CIPHERTEXT_V1", "world_id": seed, "split": split, "paragraphs": typed_rows}
        payloads[split] = {"schema": "GDT834_OPAQUE_CIPHERTEXT_V1", "world_id": seed, "split": split, "paragraphs": opaque_rows}
    truth = {"schema": "GDT834_WORLD_TRUTH_V1", "world_id": seed, "typed_decode_map": typed_key,
        "opaque_to_typed": opaque_to_typed, "decode_map": opaque_key, "paragraphs": copy.deepcopy(paragraphs)}
    return payloads, truth


def verify_source(source_dir):
    head = subprocess.check_output(["git", "-C", str(source_dir), "rev-parse", "HEAD"], text=True).strip()
    if head != UDANTE_COMMIT or sha(source_dir / SOURCE_FILE) != SOURCE_SHA256:
        raise RuntimeError("Pinned Epistolae source changed")
    for name in [SOURCE_FILE, "README.md", "LICENSE.txt"]:
        expected = subprocess.check_output(["git", "-C", str(source_dir), "show", f"{UDANTE_COMMIT}:{name}"])
        if (source_dir / name).read_bytes() != expected:
            raise RuntimeError("Pinned source file differs from committed data")


def source_phase(source_dir, output, spec):
    verify_source(source_dir)
    prepared = output / "prepared"
    prepared.mkdir(parents=True, exist_ok=True)
    bindings = {}
    for destination, (source_name, expected) in REFERENCE_BINDINGS.items():
        path = ROOT / REFERENCE_BASE / source_name
        if sha(path) != expected:
            raise RuntimeError("Frozen native reference or candidate file changed")
        (prepared / destination).write_bytes(path.read_bytes())
        bindings[destination] = {"source": REFERENCE_BASE + "/" + source_name, "sha256": expected}
    reference = [json.loads(line) for line in (prepared / "reference.jsonl").read_text().splitlines()]
    candidates = json.loads((prepared / "candidates.json").read_text())
    rows, excluded, reuse_events = [], [], []
    citations = Counter()
    last = None
    total_sentences = 0
    for comments, tokens in SOURCE_HELPER.sentences(source_dir / SOURCE_FILE):
        if not comments.get("sent_id", "").startswith(spec["source_work"] + "-"):
            raise RuntimeError("Unexpected work in fixed Epistolae source")
        total_sentences += 1
        citation = comments.get("citation_hierarchy", "")
        parts = citation.split(",")
        if len(parts) != 2 or not parts[1].startswith("Paragraphus_"):
            raise RuntimeError("Unexpected Epistolae citation structure")
        letter = parts[0]
        if letter in spec["discovery_letters"]:
            split = "discovery"
        elif letter in spec["held_letters"]:
            split = "held"
        else:
            raise RuntimeError("Letter outside the fixed discovery/held allocation")
        if citation != last:
            citations[citation] += 1
            occurrence = citations[citation]
            paragraph_id = "Epi:" + ":".join(parts)
            if occurrence > 1:
                paragraph_id += f":occurrence_{occurrence}"
                reuse_events.append({"citation_hierarchy": citation, "occurrence": occurrence, "paragraph_id": paragraph_id, "first_sentence_id": comments["sent_id"]})
            rows.append({"paragraph_id": paragraph_id, "letter": letter, "citation_hierarchy": citation, "citation_occurrence": occurrence,
                "split": split, "words": [], "lemma_sets": [], "annotation_status": [], "source_sentence_ids": [], "sentence_word_spans": [], "unsupported": False})
            last = citation
        row = rows[-1]
        words, bad, analyses, statuses = SOURCE_HELPER.annotation_join(comments, tokens)
        start = len(row["words"])
        row["words"].extend(words)
        row["lemma_sets"].extend(analyses)
        row["annotation_status"].extend(statuses)
        row["source_sentence_ids"].append(comments["sent_id"])
        row["sentence_word_spans"].append([start, start + len(words)])
        row["unsupported"] |= bad
    paragraphs = []
    for row in rows:
        if row.pop("unsupported"):
            excluded.append({"paragraph_id": row["paragraph_id"], "split": row["split"], "reason": "UNREPRESENTABLE_ALPHABETIC_WORD", "words": len(row["words"])})
        else:
            paragraphs.append(row)
    discovery_forms = {word for row in paragraphs if row["split"] == "discovery" for word in row["words"]}
    discovery_lemmas = {key for row in paragraphs if row["split"] == "discovery" for analysis in row["lemma_sets"] if analysis is not None for key in analysis}
    supports = {split: Counter() for split in ("discovery", "held")}
    partitions = {}
    for split in supports:
        selected = [row for row in paragraphs if row["split"] == split]
        for row in selected:
            row["novel_form"] = [word not in discovery_forms for word in row["words"]]
            row["novel_lemma"] = [None if analysis is None or len(analysis) != 1 else analysis[0] not in discovery_lemmas for analysis in row["lemma_sets"]]
            row["composed"] = [word not in spec["wholeword_values"] for word in row["words"]]
            for word in row["words"]:
                supports[split].update(SOURCE_HELPER.logical_encode_word(word, spec))
        partitions[split] = {"paragraphs": len(selected), "sentences": sum(len(row["source_sentence_ids"]) for row in selected),
            "words": sum(len(row["words"]) for row in selected), "types": len({word for row in selected for word in row["words"]}),
            "novel_composed_form_occurrences": sum(new and composed for row in selected for new, composed in zip(row["novel_form"], row["composed"])),
            "known_novel_lemma_occurrences": sum(flag is True for row in selected for flag in row["novel_lemma"]),
            "novel_composed_lemma_occurrences": sum(flag is True and composed for row in selected for flag, composed in zip(row["novel_lemma"], row["composed"])),
            "unknown_lemma_occurrences": sum(flag is None for row in selected for flag in row["novel_lemma"]),
            "annotation_status_counts": dict(Counter(status for row in selected for status in row["annotation_status"]))}
    active = set(supports["discovery"]) | set(supports["held"])
    support_meta = {}
    for kind, total in [("L", 26), ("S", 4), ("W", 8)]:
        active_kind = {atom for atom in active if atom[0] == kind}
        held_kind = {atom for atom in supports["held"] if atom[0] == kind}
        support_meta[kind] = {"nominal_rules": total, "active_rules": len(active_kind), "inactive_unscored_rules": total - len(active_kind),
            "minimum_discovery_occurrences_active_rules": min((supports["discovery"][atom] for atom in active_kind), default=0),
            "minimum_discovery_occurrences_held_active_rules": min((supports["discovery"][atom] for atom in held_kind), default=0),
            "held_only_rules": sum(supports["discovery"][atom] == 0 for atom in held_kind)}
    control_ngrams = {gram for row in paragraphs for gram in SOURCE_HELPER.windows(row["words"], spec["deduplication_audit_words"])}
    reference_overlap = sum(any(gram in control_ngrams for gram in SOURCE_HELPER.windows(sentence, spec["deduplication_audit_words"])) for sentence in reference)
    missing_wholes = set(spec["wholeword_values"]) - set(candidates["wholeword_pool"])
    gates = {
        "discovery_citation_runs": partitions["discovery"]["paragraphs"] >= spec["minimum_discovery_paragraphs"],
        "held_citation_runs": partitions["held"]["paragraphs"] >= spec["minimum_held_paragraphs"],
        "active_suffix_discovery_coverage": support_meta["S"]["minimum_discovery_occurrences_active_rules"] >= spec["minimum_discovery_occurrences_active_suffix_or_wholeword"],
        "active_wholeword_discovery_coverage": support_meta["W"]["minimum_discovery_occurrences_active_rules"] >= spec["minimum_discovery_occurrences_active_suffix_or_wholeword"],
        "held_active_literal_discovery_coverage": support_meta["L"]["minimum_discovery_occurrences_held_active_rules"] >= spec["minimum_discovery_occurrences_held_active_literal"],
        "held_novel_composed_forms": partitions["held"]["novel_composed_form_occurrences"] >= spec["minimum_held_novel_composed_form_occurrences"],
        "held_unambiguous_novel_composed_lemmas": partitions["held"]["novel_composed_lemma_occurrences"] >= spec["minimum_held_unambiguous_novel_composed_lemma_occurrences"],
        "wholeword_truth_in_frozen_candidate_pool": not missing_wholes,
    }
    save_json(output / "sealed/source_truth.json", {"schema": "GDT834_SOURCE_TRUTH_V1", "paragraphs": paragraphs,
        "missing_wholeword_candidates": sorted(missing_wholes),
        "logical_rule_support": {split: [{"role": kind, "output": value, "occurrences": n} for (kind, value), n in sorted(counter.items())] for split, counter in supports.items()}})
    save_json(prepared / "inventory.json", {"schema": "GDT834_OPAQUE_INVENTORY_V1", "primitive_ids": [f"X{i:02d}" for i in range(spec["opaque_inventory_size"])]})
    source_manifest = {"schema": "GDT834_SOURCE_MANIFEST_V1", "repository": UDANTE_URL, "commit": UDANTE_COMMIT, "license": "CC BY-NC-SA 3.0",
        "source_file": SOURCE_FILE, "files": {name: {"sha256": sha(source_dir / name), "bytes": (source_dir / name).stat().st_size} for name in [SOURCE_FILE, "README.md", "LICENSE.txt"]},
        "reference_bindings": bindings, "source_helper": {"path": HELPER_RELATIVE, "sha256": HELPER_SHA256},
        "transitive_GDT832_helper": {"path": HELPER.HELPER_RELATIVE, "sha256": HELPER.HELPER_SHA256}}
    save_json(output / "sources/MANIFEST.json", source_manifest)
    for name in ("README.md", "LICENSE.txt"):
        (output / "sources" / name).write_bytes((source_dir / name).read_bytes())
    notes = ["# GDT834 source and observation notes", "", "The natural whole-letter partition Epistolae I–VI versus VII–XIII was selected before new support counts. All maximal contiguous citation runs and representable words retain original order. No letter, paragraph or rare word was selected to improve decoder performance. Source dates, disputed authorship and genre descriptions remain in the copied primary README.", "", f"Noncontiguous citation reuse events: {len(reuse_events)}; distinct reused labels: {len({row['citation_hierarchy'] for row in reuse_events})}. Original citation labels and sentence spans remain in evaluator truth. Any unrepresentable alphabetic word rejects its whole run; exclusions are recorded in CAPACITY.json.", "", "Reference, reference IDs, candidate pools and empty family factors are byte-identical copies of the frozen GDT833 NATIVE inputs. There is no v/u collapse. Exact twenty-word overlap against fresh controls is an audit count, not an invitation to edit the frozen reference or choose a different source split.", "", "One fixed value key is generated per world. A separate random stream permutes the entire 38-symbol inventory into X00–X37. Opaque packets expose exact word/paragraph boundaries and no role-prefixed or role-sorted IDs. The matched typed baseline is produced from the same words and value key. Baseline and blind jobs must be isolated procedurally: typed observations and their solutions cannot be supplied to the blind fit.", "", "The public opaque inventory contains only 38 nominal IDs. Active class counts in the source audit are not fitter inputs. Roles, values, typed/opaque aliases, plaintext and novelty tags remain sealed until all designated fits are locked. Recovery counts can only concern observed rules; unused cards supply no evidence.", ""]
    (output / "sources/SOURCE_NOTES.md").write_text("\n".join(notes), encoding="utf-8")
    capacity = {"schema": "GDT834_SOURCE_CAPACITY_V1", "status": "SOURCE_CAPACITY_PASS" if all(gates.values()) else "SOURCE_CAPACITY_STOP",
        "gates": gates, "failed_gates": sorted(k for k, v in gates.items() if not v), "key_generated": False,
        "encoder_spec_sha256": sha(SPEC_PATH), "source_truth_sha256": sha(output / "sealed/source_truth.json"),
        "sources_manifest_sha256": sha(output / "sources/MANIFEST.json"),
        "prepared_input_sha256": {name: sha(prepared / name) for name in [*REFERENCE_BINDINGS, "inventory.json"]},
        "control_sentences_before_exclusion": total_sentences, "excluded_control_paragraphs": excluded,
        "control_noncontiguous_citation_reuse_events": len(reuse_events), "control_distinct_reused_citation_labels": len({row["citation_hierarchy"] for row in reuse_events}),
        "partitions": partitions, "rule_support": support_meta, "active_counts_not_fitter_inputs": True,
        "reference_sentences": len(reference), "reference_words": sum(map(len, reference)), "reference_sentences_with_exact20word_control_overlap": reference_overlap,
        "missing_wholeword_candidate_count": len(missing_wholes), "reference_and_candidates_byte_identical_to_GDT833_NATIVE": True}
    save_json(prepared / "CAPACITY.json", capacity)
    return capacity


def generation_phase(output, spec):
    capacity = json.loads((output / "prepared/CAPACITY.json").read_text())
    if capacity["status"] != "SOURCE_CAPACITY_PASS" or capacity["encoder_spec_sha256"] != sha(SPEC_PATH):
        raise RuntimeError("Fixed source capacity must pass before generating any key")
    for name, expected in capacity["prepared_input_sha256"].items():
        if sha(output / "prepared" / name) != expected:
            raise RuntimeError("Frozen prepared input changed")
    source_truth = output / "sealed/source_truth.json"
    if sha(source_truth) != capacity["source_truth_sha256"]:
        raise RuntimeError("Original plaintext or evaluation annotation changed")
    paragraphs = json.loads(source_truth.read_text())["paragraphs"]
    worlds = []
    for seed in spec["world_seeds"]:
        payloads, truth = build_world(seed, paragraphs, spec)
        hashes = {}
        for packet, payload in payloads.items():
            path = output / f"prepared/world_{seed}_{packet}.json"
            save_json(path, payload)
            hashes[packet] = sha(path)
        truth.update({"source_truth_sha256": sha(source_truth), "encoder_spec_sha256": sha(SPEC_PATH), "ciphertext_sha256": hashes})
        truth_path = output / f"sealed/world_{seed}_truth.json"
        save_json(truth_path, truth)
        worlds.append({"world_id": seed, "ciphertext_sha256": hashes, "sealed_truth_sha256": sha(truth_path),
            "typed_opaque_original_spelling_roundtrip_pass": True, "opaque_nominal_ids": 38})
    result = {"schema": "GDT834_GENERATION_V1", "status": "MATCHED_TYPED_AND_ROLE_BLIND_CONTROLS_GENERATED",
        "capacity_sha256": sha(output / "prepared/CAPACITY.json"), "encoder_spec_sha256": sha(SPEC_PATH), "worlds": worlds,
        "source_content_and_value_key_shared_between_observations": True, "roles_values_aliases_plaintext_in_console": False,
        "requires_isolated_typed_and_blind_fit_jobs": True}
    save_json(output / "prepared/GENERATION.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=EXPERIMENT / "runtime/udante_source")
    parser.add_argument("--output", type=Path, default=EXPERIMENT)
    parser.add_argument("--phase", choices=["sources", "generate", "all"], default="sources")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text())
    if args.phase in ("sources", "all"):
        capacity = source_phase(args.source_dir, args.output, spec)
        print(json.dumps(capacity, sort_keys=True))
        if capacity["status"] != "SOURCE_CAPACITY_PASS":
            return
    if args.phase in ("generate", "all"):
        print(json.dumps(generation_phase(args.output, spec), sort_keys=True))


if __name__ == "__main__":
    main()
