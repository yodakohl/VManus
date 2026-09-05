#!/usr/bin/env python3
"""Prepare reference and independent historical controls without truth output.

The source phase emits only aggregate control metadata. Generation is a
separate command requiring the exact confirmed encoder-spec hash. No Voynich
source is read. Control plaintext and encoding maps are written only to sealed/.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import random
import subprocess
import unicodedata
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
SPEC_PATH = Path(__file__).with_name("ENCODER_SPEC.json")
ITTB_COMMIT = "b19bcbd3ab66914570b5bb0616a9066d56d5e7ea"
UDANTE_COMMIT = "e02420457780c6fbb503ba39a7d8798ab6a8645c"
SOURCE_REPOS = {
    "ittb": (ITTB_COMMIT, "https://github.com/UniversalDependencies/UD_Latin-ITTB.git", "la_ittb-ud-train.conllu"),
    "udante": (UDANTE_COMMIT, "https://github.com/UniversalDependencies/UD_Latin-UDante.git", "la_udante-ud-train.conllu"),
}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    return digest_bytes(path.read_bytes())


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def normalized_words(text):
    """Return every alphabetic run and an explicit unsupported-script flag."""
    text = text.casefold().replace("æ", "ae").replace("œ", "oe")
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    words, current = [], []
    for c in text:
        if c.isalpha():
            current.append(c)
        elif current:
            words.append("".join(current))
            current = []
    if current:
        words.append("".join(current))
    unsupported = any(any(c not in "abcdefghijklmnopqrstuvwxyz" for c in word) for word in words)
    return words, unsupported


def lemma_key(lemma, pos):
    if lemma == "_" or pos in {"PUNCT", "SYM", "X", "_"}:
        return None
    lemma = lemma.casefold().replace("æ", "ae").replace("œ", "oe")
    lemma = "".join(c for c in unicodedata.normalize("NFKD", lemma) if not unicodedata.combining(c))
    if "|" in lemma:
        raise ValueError("Unexpected lemma delimiter")
    return lemma + "|" + pos


def sentences(path):
    comments, rows = {}, []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.rstrip("\n")
            if not line:
                if comments or rows:
                    yield comments, rows
                comments, rows = {}, []
            elif line.startswith("# "):
                if " = " in line:
                    key, value = line[2:].split(" = ", 1)
                    comments[key] = value
            elif not line.startswith("#"):
                fields = line.split("\t")
                if len(fields) != 10:
                    raise ValueError("Invalid CoNLL-U field count")
                rows.append(fields)
    if comments or rows:
        yield comments, rows


def annotation_join(comments, rows):
    """Exact written-word join; MWTs or mismatches never fabricate a lemma."""
    words, unsupported = normalized_words(comments["text"])
    surface_words, analyses, statuses = [], [], []
    covered = set()
    for fields in rows:
        token_id = fields[0]
        if "-" in token_id:
            lo, hi = map(int, token_id.split("-"))
            covered.update(range(lo, hi + 1))
            forms, bad = normalized_words(fields[1])
            surface_words.extend(forms)
            analyses.extend([None] * len(forms))
            statuses.extend(["UNKNOWN_MULTIWORD_TOKEN"] * len(forms))
            continue
        if not token_id.isdigit() or int(token_id) in covered:
            continue
        forms, bad = normalized_words(fields[1])
        key = lemma_key(fields[2], fields[3])
        surface_words.extend(forms)
        if len(forms) == 1 and key is not None and not bad:
            analyses.append([key])
            statuses.append("EXACT_SINGLE_TOKEN_JOIN")
        else:
            analyses.extend([None] * len(forms))
            statuses.extend(["UNKNOWN_NONUNIQUE_OR_MISSING_ANNOTATION"] * len(forms))
    if surface_words != words:
        analyses = [None] * len(words)
        statuses = ["UNKNOWN_SENTENCE_SURFACE_ALIGNMENT"] * len(words)
    assert len(words) == len(analyses) == len(statuses)
    return words, unsupported, analyses, statuses


def windows(words, width):
    return (tuple(words[i:i + width]) for i in range(max(0, len(words) - width + 1)))


def ensure_source(kind, path, fetch):
    commit, url, filename = SOURCE_REPOS[kind]
    if not path.exists():
        if not fetch:
            raise RuntimeError(f"Missing {kind} source; pass its directory or --fetch-sources")
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", url, str(path)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(path), "checkout", "--detach", commit], check=True, capture_output=True)
    actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if actual != commit:
        raise RuntimeError(f"Pinned {kind} commit mismatch")
    for name in [filename, "README.md", "LICENSE.txt"]:
        committed = subprocess.check_output(["git", "-C", str(path), "show", f"{commit}:{name}"])
        if (path / name).read_bytes() != committed:
            raise RuntimeError(f"Modified {kind} bound source {name}")
    return path / filename


def logical_encode_word(word, spec):
    if word in spec["wholeword_values"]:
        return [("W", word)]
    for suffix in spec["suffix_values"]:
        if word.endswith(suffix) and len(word) - len(suffix) >= spec["suffix_minimum_stem_characters"]:
            return [("L", c) for c in word[:-len(suffix)]] + [("S", suffix)]
    return [("L", c) for c in word]


def source_phase(args, spec):
    out = args.output
    reference_path = ensure_source("ittb", args.reference_dir, args.fetch_sources)
    control_path = ensure_source("udante", args.control_dir, args.fetch_sources)
    grouped, order = {}, []
    citation_runs = Counter()
    repeated_citations = []
    current_citation = None
    current_paragraph_id = None
    selected_sentences = 0
    for comments, rows in sentences(control_path):
        source_id = comments.get("sent_id", "")
        if not source_id.startswith("Mon-"):
            current_citation = None
            continue
        selected_sentences += 1
        citation = comments.get("citation_hierarchy", "")
        pieces = citation.split(",")
        if len(pieces) != 3 or not pieces[2].startswith("Paragraphus_"):
            raise RuntimeError("Monarchia citation structure differs from the registered grouping")
        book, chapter, paragraph = pieces
        if book == spec["discovery_book"]:
            split = "discovery"
        elif book in spec["held_books"]:
            split = "held"
        else:
            raise RuntimeError("Unexpected Monarchia book")
        if citation != current_citation:
            citation_runs[citation] += 1
            occurrence = citation_runs[citation]
            paragraph_id = "Mon:" + ":".join(pieces)
            if occurrence > 1:
                paragraph_id += f":occurrence_{occurrence}"
                repeated_citations.append({"citation_hierarchy": citation, "occurrence": occurrence,
                    "paragraph_id": paragraph_id, "first_sentence_id": source_id})
            order.append(paragraph_id)
            grouped[paragraph_id] = {"paragraph_id": paragraph_id, "book": book, "chapter": chapter,
                "citation_hierarchy": citation, "citation_occurrence": occurrence,
                "split": split, "words": [], "lemma_sets": [],
                "annotation_status": [], "source_sentence_ids": [], "sentence_word_spans": [], "unsupported": False}
            current_citation, current_paragraph_id = citation, paragraph_id
        else:
            paragraph_id = current_paragraph_id
        paragraph_row = grouped[paragraph_id]
        words, bad, analyses, statuses = annotation_join(comments, rows)
        start = len(paragraph_row["words"])
        paragraph_row["words"].extend(words)
        paragraph_row["lemma_sets"].extend(analyses)
        paragraph_row["annotation_status"].extend(statuses)
        paragraph_row["source_sentence_ids"].append(source_id)
        paragraph_row["sentence_word_spans"].append([start, start + len(words)])
        paragraph_row["unsupported"] |= bad
    paragraphs, excluded = [], []
    for key in order:
        row = grouped[key]
        if row["unsupported"]:
            excluded.append({"paragraph_id": key, "reason": "UNREPRESENTABLE_ALPHABETIC_WORD", "word_count": len(row["words"]), "split": row["split"]})
        else:
            row.pop("unsupported")
            paragraphs.append(row)
    if not paragraphs or set(p["split"] for p in paragraphs) != {"discovery", "held"}:
        raise RuntimeError("Missing complete control partition")

    width = spec["deduplication_ngram_words"]
    control_ngrams = {g for row in paragraphs for g in windows(row["words"], width)}
    reference, reference_ids, removed_ids, reference_bad = [], [], [], []
    families = defaultdict(set)
    reference_status = Counter()
    for comments, rows in sentences(reference_path):
        words, bad, analyses, statuses = annotation_join(comments, rows)
        source_id = comments.get("reference", comments["sent_id"])
        if bad:
            reference_bad.append(source_id)
            continue
        if any(g in control_ngrams for g in windows(words, width)):
            removed_ids.append(source_id)
            continue
        reference.append(words)
        reference_ids.append(source_id)
        reference_status.update(statuses)
        for word, analysis in zip(words, analyses):
            if analysis is not None:
                families[word].update(analysis)
    frequencies = Counter(word for row in reference for word in row)
    candidates = sorted((word for word in frequencies if spec["wholeword_candidate_minimum_characters"] <= len(word) <= spec["wholeword_candidate_maximum_characters"]), key=lambda w: (-frequencies[w], w))[:spec["wholeword_candidate_pool_size"]]
    missing_wholes = sorted(set(spec["wholeword_values"]) - set(candidates))
    missing_suffixes = sorted(set(spec["suffix_values"]) - set(spec["suffix_candidate_pool"]))

    discovery_forms = {word for row in paragraphs if row["split"] == "discovery" for word in row["words"]}
    discovery_lemmas = {key for row in paragraphs if row["split"] == "discovery" for analysis in row["lemma_sets"] if analysis is not None for key in analysis}
    support = {split: Counter() for split in ("discovery", "held")}
    split_meta = {}
    for split in ("discovery", "held"):
        selected = [row for row in paragraphs if row["split"] == split]
        status_counts = Counter()
        for row in selected:
            row["novel_form"] = [w not in discovery_forms for w in row["words"]]
            row["novel_lemma"] = [None if a is None or len(a) != 1 else a[0] not in discovery_lemmas for a in row["lemma_sets"]]
            row["composed"] = [w not in spec["wholeword_values"] for w in row["words"]]
            status_counts.update(row["annotation_status"])
            for word in row["words"]:
                support[split].update(logical_encode_word(word, spec))
        split_meta[split] = {"paragraphs": len(selected), "sentences": sum(len(r["source_sentence_ids"]) for r in selected),
            "words": sum(len(r["words"]) for r in selected), "types": len({w for r in selected for w in r["words"]}),
            "annotation_status_counts": dict(status_counts),
            "novel_form_tokens": sum(sum(r["novel_form"]) for r in selected),
            "novel_form_types": len({w for r in selected for w, flag in zip(r["words"], r["novel_form"]) if flag}),
            "known_novel_lemma_tokens": sum(sum(flag is True for flag in r["novel_lemma"]) for r in selected),
            "novel_composed_form_tokens": sum(sum(new and composed for new, composed in zip(r["novel_form"], r["composed"])) for r in selected),
            "unknown_lemma_tokens": sum(sum(flag is None for flag in r["novel_lemma"]) for r in selected)}
    held_only = set(support["held"]) - set(support["discovery"])
    support_metadata = {}
    for kind in ("L", "S", "W"):
        active_discovery = [n for (k, value), n in support["discovery"].items() if k == kind]
        held_rules = {key for key in support["held"] if key[0] == kind}
        values = {"L": list(spec["letter_alphabet"]), "S": spec["suffix_values"], "W": spec["wholeword_values"]}[kind]
        support_metadata[kind] = {"discovery_active_rules": len(active_discovery),
            "held_active_rules": len(held_rules), "held_only_rules": sum(key[0] == kind for key in held_only),
            "minimum_active_discovery_count": min(active_discovery, default=0),
            "minimum_discovery_count_all_declared_rules": min(support["discovery"][(kind, value)] for value in values),
            "minimum_discovery_count_among_held_active": min((support["discovery"][key] for key in held_rules), default=0)}
    by_prefix = defaultdict(set)
    for word in discovery_forms:
        atoms = logical_encode_word(word, spec)
        if len(atoms) - 1 >= spec["source_family_minimum_prefix_primitives"]:
            by_prefix[tuple(atoms[:-1])].add(word)
    source_family_edges = 0
    reference_supported_family_edges = 0
    for forms in by_prefix.values():
        for left, right in itertools.combinations(sorted(forms), 2):
            source_family_edges += 1
            reference_supported_family_edges += bool(families.get(left, set()) & families.get(right, set()))
    gates = {
        "minimum_discovery_paragraphs": split_meta["discovery"]["paragraphs"] >= spec["minimum_discovery_paragraphs"],
        "minimum_held_paragraphs": split_meta["held"]["paragraphs"] >= spec["minimum_held_paragraphs"],
        "wholeword_truth_in_reference_pool": not missing_wholes,
        "suffix_truth_in_frozen_pool": not missing_suffixes,
        "suffix_discovery_coverage": support_metadata["S"]["minimum_discovery_count_all_declared_rules"] >= spec["minimum_discovery_occurrences_each_suffix_or_wholeword"],
        "wholeword_discovery_coverage": support_metadata["W"]["minimum_discovery_count_all_declared_rules"] >= spec["minimum_discovery_occurrences_each_suffix_or_wholeword"],
        "held_active_letter_discovery_coverage": support_metadata["L"]["minimum_discovery_count_among_held_active"] >= spec["minimum_discovery_occurrences_each_held_active_letter"],
        "minimum_observed_source_family_edges": source_family_edges >= spec["minimum_source_family_edges"],
        "minimum_held_novel_composed_form_occurrences": split_meta["held"]["novel_composed_form_tokens"] >= spec["minimum_held_novel_composed_form_occurrences"],
        "minimum_held_known_novel_lemma_occurrences": split_meta["held"]["known_novel_lemma_tokens"] >= spec["minimum_held_known_novel_lemma_occurrences"],
        "minimum_reference_lemma_supported_source_family_edges": reference_supported_family_edges >= spec["minimum_reference_lemma_supported_source_family_edges"],
    }
    capacity_pass = all(gates.values())
    capacity = {"schema": "GDT832_SOURCE_CAPACITY_V1", "status": "SOURCE_CAPACITY_PASS" if capacity_pass else "SOURCE_CAPACITY_STOP",
        "encoder_spec_sha256": digest_file(SPEC_PATH), "key_generated": False,
        "monarchia_sentences_before_exclusion": selected_sentences, "paragraphs_before_exclusion": len(order),
        "noncontiguous_reused_citation_labels": len(repeated_citations),
        "paragraph_unit": spec["paragraph_unit"],
        "excluded_control_paragraphs": excluded, "partitions": split_meta,
        "reference_sentences": len(reference), "reference_words": sum(map(len, reference)),
        "reference_types": len(frequencies), "reference_family_forms": len(families),
        "reference_annotation_status_counts": dict(reference_status),
        "reference_sentences_removed_for_20word_overlap": len(removed_ids),
        "reference_sentences_removed_for_unsupported_script": len(reference_bad),
        "wholeword_candidates": len(candidates), "missing_truth_wholewords_from_pool_count": len(missing_wholes),
        "missing_truth_suffixes_from_pool_count": len(missing_suffixes), "rule_support": support_metadata,
        "observed_discovery_source_family_edges": source_family_edges,
        "reference_lemma_supported_source_family_edges": reference_supported_family_edges,
        "gates": gates, "failed_gates": sorted(key for key, passed in gates.items() if not passed),
        "limits": ["Reference families contain attested forms, not exhaustive paradigms.", "Unknown token/lemma joins remain unknown.", "Public metadata contains no control plaintext or encoding map."]}
    (out / "prepared").mkdir(parents=True, exist_ok=True)
    (out / "prepared/reference.jsonl").write_bytes(b"".join(canonical(words) for words in reference))
    save_json(out / "prepared/reference_ids.json", reference_ids)
    save_json(out / "prepared/families.json", {word: sorted(values) for word, values in families.items()})
    save_json(out / "prepared/candidates.json", {"suffix_pool": spec["suffix_candidate_pool"], "wholeword_pool": candidates})
    save_json(out / "prepared/CAPACITY.json", capacity)
    save_json(out / "sealed/source_truth.json", {"schema": "GDT832_SOURCE_TRUTH_V1", "paragraphs": paragraphs,
        "missing_wholeword_candidates": missing_wholes, "missing_suffix_candidates": missing_suffixes,
        "reference_dedup_removed_ids": removed_ids, "reference_unsupported_removed_ids": reference_bad,
        "logical_rule_support": {split: [{"kind": k, "value": value, "count": n} for (k, value), n in sorted(counts.items())] for split, counts in support.items()}})
    manifest = {"schema": "GDT832_SOURCE_MANIFEST_V1", "license": "CC BY-NC-SA 3.0", "sources": {}}
    for kind, path in [("ittb", args.reference_dir), ("udante", args.control_dir)]:
        commit, url, filename = SOURCE_REPOS[kind]
        destination = out / "sources" / kind
        destination.mkdir(parents=True, exist_ok=True)
        for name in ["README.md", "LICENSE.txt"]:
            (destination / name).write_bytes((path / name).read_bytes())
        manifest["sources"][kind] = {"url": url, "commit": commit, "input_file": filename,
            "sha256": digest_file(path / filename), "bytes": (path / filename).stat().st_size,
            "README_sha256": digest_file(path / "README.md"), "LICENSE_sha256": digest_file(path / "LICENSE.txt")}
    save_json(out / "sources/MANIFEST.json", manifest)
    notes = ["# GDT832 source grouping notes", "", "The pinned UDante source repeats eight citation labels noncontiguously in Monarchia Book II. The source phase first stopped before writing outputs or generating a key. Before any fit, the coordinator clarified the unit as a maximal contiguous run of one exact citation. Repeated labels are disambiguated by occurrence; the original citation and source sentence IDs are retained. No chapter label is silently changed and no nonadjacent text is merged. The Book I versus Books II/III split and every other selection rule are unchanged.", "", "| Original citation | Occurrence | Run ID | First source sentence |", "|---|---:|---|---|"]
    for row in repeated_citations:
        notes.append(f"| {row['citation_hierarchy']} | {row['occurrence']} | {row['paragraph_id']} | {row['first_sentence_id']} |")
    notes.extend(["", "Normalization preserves every ordered alphabetic word after the specified casefold/ligature/NFKD transformation. A control run containing any still unrepresentable alphabetic word is excluded as a whole and recorded in CAPACITY.json. Punctuation and spacing are not scored. No word is individually deleted to make a control fit.", "", "Reference uses only pinned ITTB TRAIN. Reference sentences sharing an exact twenty-word sequence with a retained control run are removed before both language-model and family preparation. CoNLL-U multiword tokens are reconstructed as written forms; their multiple syntactic analyses are not collapsed to one invented lemma. Exact single-token joins support the family dictionary, and any unresolved join stays unknown.", "", "The historical resources carry CC BY-NC-SA 3.0; copied source READMEs and license text retain attribution and provenance. Attested lemma/form memberships are not an exhaustive historical paradigm generator. No Voynich data are inputs.", ""])
    (out / "sources/SOURCE_NOTES.md").write_text("\n".join(notes), encoding="utf-8")
    return capacity


def generation_phase(args, spec):
    spec_hash = digest_file(SPEC_PATH)
    if args.confirm_spec_sha256 != spec_hash:
        raise RuntimeError("Generation requires exact confirmed encoder-spec SHA256")
    capacity_path = args.output / ("prepared/ACTIVE_RULE_CAPACITY.json" if args.active_rule_control else "prepared/CAPACITY.json")
    capacity = json.loads(capacity_path.read_text())
    expected_status = "ACTIVE_RULE_SOURCE_CAPACITY_PASS" if args.active_rule_control else "SOURCE_CAPACITY_PASS"
    if capacity["status"] != expected_status or capacity["encoder_spec_sha256"] != spec_hash:
        raise RuntimeError("Source capacity has not passed under this encoder specification")
    if args.active_rule_control:
        checks = [("initial_capacity_sha256", args.output / "prepared/CAPACITY.json"),
            ("source_truth_sha256", args.output / "sealed/source_truth.json"),
            ("sources_manifest_sha256", args.output / "sources/MANIFEST.json")]
        for field, path in checks:
            if digest_file(path) != capacity[field]:
                raise RuntimeError("Active-rule source binding changed")
        for relative, expected in capacity["prepared_input_sha256"].items():
            if digest_file(args.output / "prepared" / relative) != expected:
                raise RuntimeError("Active-rule prepared input changed")
    truth = json.loads((args.output / "sealed/source_truth.json").read_text())
    world_summaries = []
    for world_index, seed in enumerate(spec["world_seeds"]):
        rng = random.Random(seed)
        encode, decode = {}, {}
        for kind, values in [("L", list(spec["letter_alphabet"])), ("S", spec["suffix_values"]), ("W", spec["wholeword_values"])]:
            ids = [f"{kind}{i:02d}" for i in range(len(values))]
            rng.shuffle(ids)
            for value, card in zip(values, ids):
                encode[(kind, value)] = card
                decode[card] = value
        ciphertext_hashes = {}
        pseudo_paragraphs = []
        for split in ("discovery", "held"):
            pseudo_seed = spec["pseudo_discovery_seed_base" if split == "discovery" else "pseudo_held_seed_base"] + world_index
            pseudo_rng = random.Random(pseudo_seed)
            for paragraph in truth["paragraphs"]:
                if paragraph["split"] != split:
                    continue
                shuffled = copy.deepcopy(paragraph)
                indices = list(range(len(paragraph["words"])))
                pseudo_rng.shuffle(indices)
                for field in ("words", "lemma_sets", "annotation_status", "novel_form", "novel_lemma", "composed"):
                    shuffled[field] = [paragraph[field][i] for i in indices]
                shuffled["source_order_indices"] = indices
                shuffled["sentence_word_spans"] = None
                pseudo_paragraphs.append(shuffled)
        for condition, paragraph_source in [("real", truth["paragraphs"]), ("pseudo", pseudo_paragraphs)]:
            for split in ("discovery", "held"):
                rows = []
                for paragraph in paragraph_source:
                    if paragraph["split"] != split:
                        continue
                    coded = [[encode[atom] for atom in logical_encode_word(word, spec)] for word in paragraph["words"]]
                    recovered = ["".join(decode[card] for card in word) for word in coded]
                    if recovered != paragraph["words"]:
                        raise AssertionError("Generator roundtrip failed")
                    rows.append({"paragraph_id": paragraph["paragraph_id"], "words": coded})
                payload = {"schema": "GDT832_CIPHERTEXT_V1", "world_id": seed, "condition": condition, "split": split, "paragraphs": rows}
                suffix = "" if condition == "real" else "_pseudo"
                destination = args.output / f"prepared/world_{seed}{suffix}_{split}.json"
                save_json(destination, payload)
                ciphertext_hashes[condition + "_" + split] = digest_file(destination)
        save_json(args.output / f"sealed/world_{seed}_truth.json", {"schema": "GDT832_WORLD_TRUTH_V1", "world_id": seed,
            "decode_map": decode, "source_truth_sha256": digest_file(args.output / "sealed/source_truth.json"),
            "encoder_spec_sha256": spec_hash, "ciphertext_sha256": ciphertext_hashes,
            "paragraphs": truth["paragraphs"], "pseudo_paragraphs": pseudo_paragraphs})
        active_atoms = {atom for paragraph in truth["paragraphs"] for word in paragraph["words"] for atom in logical_encode_word(word, spec)}
        active_ids = sorted(encode[atom] for atom in active_atoms)
        inactive_ids = sorted(set(decode) - set(active_ids))
        world_summaries.append({"world_id": seed, "ciphertext_sha256": ciphertext_hashes, "roundtrip_pass": True,
            "observed_primitive_ids": active_ids, "unobserved_unscored_primitive_ids": inactive_ids})
    summary = {"schema": "GDT832_GENERATION_V1", "status": "BLINDED_CONTROL_GENERATED", "worlds": world_summaries,
        "encoder_spec_sha256": spec_hash, "plaintext_or_key_in_console": False,
        "capacity_file": capacity_path.name, "capacity_sha256": digest_file(capacity_path),
        "blinding": "Procedural; seed-defined keys are reconstructible but not exposed to the decoder operator."}
    save_json(args.output / "prepared/GENERATION.json", summary)
    return summary


def active_rule_capacity_phase(args, spec):
    """Separate pre-fit design correction; never rewrite the initial stop."""
    initial_path = args.output / "prepared/CAPACITY.json"
    initial_bytes = initial_path.read_bytes()
    initial = json.loads(initial_bytes)
    spec_hash = digest_file(SPEC_PATH)
    if initial["encoder_spec_sha256"] != spec_hash or initial["key_generated"]:
        raise RuntimeError("Initial source/spec binding or pre-key condition changed")
    if (args.output / "prepared/GENERATION.json").exists():
        raise RuntimeError("Active-rule correction must be committed before key generation")
    truth_path = args.output / "sealed/source_truth.json"
    truth = json.loads(truth_path.read_text())
    support = {split: Counter() for split in ("discovery", "held")}
    for paragraph in truth["paragraphs"]:
        for word in paragraph["words"]:
            support[paragraph["split"]].update(logical_encode_word(word, spec))
    active_suffixes = {atom for split in support.values() for atom in split if atom[0] == "S"}
    minimum = min((support["discovery"][atom] for atom in active_suffixes), default=0)
    gates = dict(initial["gates"])
    gates["suffix_discovery_coverage"] = bool(active_suffixes) and minimum >= spec["minimum_discovery_occurrences_each_suffix_or_wholeword"]
    result = {"schema": "GDT832_ACTIVE_RULE_SOURCE_CAPACITY_V1",
        "status": "ACTIVE_RULE_SOURCE_CAPACITY_PASS" if all(gates.values()) else "ACTIVE_RULE_SOURCE_CAPACITY_STOP",
        "encoder_spec_sha256": spec_hash, "initial_capacity_sha256": digest_bytes(initial_bytes),
        "source_truth_sha256": digest_file(truth_path), "sources_manifest_sha256": digest_file(args.output / "sources/MANIFEST.json"),
        "prepared_input_sha256": {name: digest_file(args.output / "prepared" / name) for name in ("reference.jsonl", "reference_ids.json", "families.json", "candidates.json")},
        "initial_status": initial["status"], "initial_failed_gates": initial["failed_gates"],
        "changed_gate": "suffix_discovery_coverage",
        "active_suffix_rule_count": len(active_suffixes), "inactive_suffix_rule_count": len(spec["suffix_values"]) - len(active_suffixes),
        "minimum_discovery_count_active_suffix_rules": minimum,
        "gates": gates, "failed_gates": sorted(key for key, value in gates.items() if not value), "key_generated": False,
        "correction": "Explicit pre-fit source-design correction: require at least eight discovery occurrences for every suffix rule active in discovery or held. Suffix rules absent from both partitions are unidentifiable and excluded from key accuracy, analogously to unused letters. The nominal four-suffix deck, text, split, encoder and randomization stay unchanged. The initial protocol remains a recorded stop."}
    save_json(args.output / "prepared/ACTIVE_RULE_CAPACITY.json", result)
    notes_path = args.output / "sources/SOURCE_NOTES.md"
    notes = notes_path.read_text(encoding="utf-8")
    heading = "## Pre-fit active-rule design correction"
    if heading not in notes:
        notes += f"\n{heading}\n\nThe original source-capacity protocol stopped solely because one nominal suffix rule occurs in neither discovery nor held. Its CAPACITY.json bytes remain unchanged (SHA256 `{digest_bytes(initial_bytes)}`). Before any encoding key or fitted score existed, the coordinator explicitly changed only the new control's suffix coverage requirement to rules active in either partition. Each such rule still requires at least eight discovery occurrences. The inactive rule remains in the four-card deck but is unidentifiable and receives no key-recovery credit, as already specified for unused letters. No word, paragraph, book split, suffix/wholeword value, candidate pool, random seed or encoder operation was changed. ACTIVE_RULE_CAPACITY.json is a separate decision with source/spec/input bindings; the historical initial stop is not relabeled as a pass. Three active suffix values, not four, can be assessed in this control.\n"
        notes_path.write_text(notes, encoding="utf-8")
    if initial_path.read_bytes() != initial_bytes:
        raise AssertionError("Initial capacity record mutated")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["sources", "generate"], default="sources")
    parser.add_argument("--reference-dir", type=Path, default=ROOT / ".gdt001/repos/latin_ittb")
    parser.add_argument("--control-dir", type=Path, default=ROOT / ".gdt832/repos/latin_udante")
    parser.add_argument("--output", type=Path, default=EXPERIMENT)
    parser.add_argument("--fetch-sources", action="store_true")
    parser.add_argument("--confirm-spec-sha256", default="")
    parser.add_argument("--active-rule-control", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text())
    if args.phase == "generate":
        result = generation_phase(args, spec)
    elif args.active_rule_control:
        result = active_rule_capacity_phase(args, spec)
    else:
        result = source_phase(args, spec)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
