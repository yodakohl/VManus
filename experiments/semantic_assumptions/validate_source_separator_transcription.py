#!/usr/bin/env python3
"""Clean-room validation of the source-separator transcription atlas.

This module imports no producer or legacy parser code.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SPEC = HERE / "SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md"
PRODUCER = HERE / "build_source_separator_transcription.py"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
ATLAS = RESULTS / "source_separator_transcription.tsv"
RESULT = RESULTS / "source_separator_transcription.json"
REPORT = RESULTS / "source_separator_transcription_report.md"
VALIDATION = RESULTS / "source_separator_transcription_validation.json"
VALIDATION_REPORT = RESULTS / "source_separator_transcription_validation_report.md"

SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
EXPECTED_HASHES = {
    "ZL3b": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "IT2a": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "RF1b": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "interlinear": "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "spec": "fdcfb65a67438ae154979b1499ce63dc359e0e65ae5eaf93e73637e7dec3ec46",
    "producer": "dd93f78547a4917334b3bbf3d10e6af075b2ef2d2870e25bcfcdab5cd41aee51",
    "atlas": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "result": "c047bef98ad0f83c65e0dbdad8e6904b6ed4ea6e3d945407191c39fd482e36f4",
    "report": "f2ddd3c91304f175220e3693af04bfc535e60c3f0111b96b60631c6de4d1ea17",
}

PAGE_RE = re.compile(r"^<([^>.]+)>\s+<!(.*)>")
LOCUS_RE = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
META_RE = re.compile(r"\$([A-Z])=([^\s>]+)")
SQUARE_RE = re.compile(r"\[([^:\]]+)(?::[^\]]*)?\]")
BRACE_RE = re.compile(r"\{[^}]*\}")
ANGLE_RE = re.compile(r"<[^>]*>")
SPLIT_RE = re.compile(r"[\s.,;:=/\\|+\-]+")

SEPARATOR_NAMES = {
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION",
    "<~>": "DRAWING_INTERRUPTION_UNALIGNED",
}
FIELDS = [
    "source_group_id", "edition", "locus", "page", "section", "currier",
    "hand", "code", "kind", "grammar_scope", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
    "clean_ascii_fragments", "clean_ascii_fragment_count",
    "legacy_surface_positions_1based", "legacy_interlinear_row_present",
    "legacy_mapping_status",
]
STATUS = "PASS_SOURCE_SEPARATOR_TRANSCRIPTION_LOSS_ACCOUNTED"
CLAIM_CEILING = (
    "This atlas establishes source-row, source-group, separator, and legacy-cleaner "
    "loss/split provenance only. It does not establish authorial word boundaries, "
    "pronunciation, language, cipher, grammatical roles, lexemes, plaintext, or translation."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(text: str) -> list[str]:
    selected = SQUARE_RE.sub(lambda match: match.group(1), text)
    selected = BRACE_RE.sub("", selected)
    selected = ANGLE_RE.sub(" ", selected)
    selected = selected.replace("?", "").replace("!", "").replace("*", "").replace("'", "")
    output: list[str] = []
    for part in SPLIT_RE.split(selected):
        letters = re.sub(r"[^A-Za-z]", "", part).lower()
        if letters:
            output.append(letters)
    return output


def groups(text: str) -> tuple[list[str], list[str]]:
    output: list[str] = []
    boundaries: list[str] = []
    pending: list[str] = []
    buffer: list[str] = []
    cursor = 0

    def cut(marker: str) -> None:
        nonlocal buffer, pending
        value = "".join(buffer).strip()
        buffer = []
        if value:
            if output:
                if len(pending) != 1:
                    raise ValueError("non-single separator between source groups")
                boundaries.append(pending[0])
            output.append(value)
            pending = []
        pending.append(marker)

    while cursor < len(text):
        marker = next((value for value in ("<->", "<~>") if text.startswith(value, cursor)), None)
        if marker:
            cut(marker)
            cursor += len(marker)
            continue
        value = text[cursor]
        if value == "<":
            end = text.find(">", cursor + 1)
            if end == -1:
                raise ValueError("unterminated angle field")
            tag = text[cursor:end + 1]
            if tag not in {"<%>", "<$>"}:
                buffer.append(tag)
            cursor = end + 1
            continue
        if value == "[" or value == "{":
            closing = "]" if value == "[" else "}"
            end = text.find(closing, cursor + 1)
            if end == -1:
                raise ValueError("unterminated literal alternative")
            buffer.append(text[cursor:end + 1])
            cursor = end + 1
            continue
        if value == "." or value == ",":
            cut(value)
            cursor += 1
            continue
        buffer.append(value)
        cursor += 1

    value = "".join(buffer).strip()
    if value:
        if output:
            if len(pending) != 1:
                raise ValueError("non-single separator before final group")
            boundaries.append(pending[0])
        output.append(value)
        pending = []
    if pending or not output or len(boundaries) + 1 != len(output):
        raise ValueError("invalid source topology")
    return output, boundaries


def interlinear_rows() -> dict[tuple[str, str], list[str]]:
    output: dict[tuple[str, str], list[str]] = {}
    with INTERLINEAR.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["edition"], row["locus"])
            if key in output:
                raise ValueError("duplicate interlinear key")
            output[key] = row["surface"].split()
    return output


def expected_rows():
    legacy = interlinear_rows()
    seen: set[tuple[str, str]] = set()
    zero_rows: set[tuple[str, str]] = set()
    totals = Counter()
    editions = {edition: Counter() for edition in SOURCES}
    separator_counts = Counter()

    for edition, source in SOURCES.items():
        page = ""
        meta: dict[str, str] = {}
        row_index = 0
        for line in source.read_text(encoding="utf-8", errors="strict").splitlines():
            page_match = PAGE_RE.match(line)
            if page_match:
                page = page_match.group(1).lower()
                meta = dict(META_RE.findall(page_match.group(2)))
                continue
            match = LOCUS_RE.match(line)
            if not match:
                continue
            locus, code, _comment, text = match.groups()
            key = (edition, locus)
            if key in seen:
                raise ValueError("duplicate source key")
            seen.add(key)
            row_index += 1
            source_groups, source_boundaries = groups(text)
            fragments = [clean(group) for group in source_groups]
            flat = [item for group_fragments in fragments for item in group_fragments]
            if flat:
                if key not in legacy or legacy[key] != flat:
                    raise ValueError("legacy surface reconstruction mismatch")
            else:
                if key in legacy:
                    raise ValueError("zero-token row found in legacy table")
                zero_rows.add(key)
            scope = (
                "CONFIRMED_PROSE"
                if len(code) > 1 and code[1] == "P" and meta.get("L", "") in {"A", "B"}
                else "DIAGNOSTIC_NONPROSE"
            )
            position = 0
            for group_index, (raw_group, emitted) in enumerate(zip(source_groups, fragments), 1):
                count = len(emitted)
                mapped_positions = list(range(position + 1, position + count + 1))
                position += count
                state = "ZERO_ASCII_FRAGMENT" if count == 0 else "ONE_ASCII_FRAGMENT" if count == 1 else "MULTI_ASCII_FRAGMENT"
                left = "LINE_START" if group_index == 1 else SEPARATOR_NAMES[source_boundaries[group_index - 2]]
                right = "LINE_END" if group_index == len(source_groups) else SEPARATOR_NAMES[source_boundaries[group_index - 1]]
                row = {
                    "source_group_id": f"{edition}|{locus}|G{group_index:03d}",
                    "edition": edition,
                    "locus": locus,
                    "page": page,
                    "section": meta.get("I", ""),
                    "currier": meta.get("L", ""),
                    "hand": meta.get("H", ""),
                    "code": code,
                    "kind": code[1] if len(code) > 1 else "",
                    "grammar_scope": scope,
                    "source_row_index": str(row_index),
                    "source_group_index": str(group_index),
                    "source_group_count": str(len(source_groups)),
                    "paragraph_start": str(int("<%>" in text)),
                    "paragraph_end": str(int("<$>" in text)),
                    "left_separator": left,
                    "right_separator": right,
                    "ivtff_group_raw": raw_group,
                    "clean_ascii_fragments": " ".join(emitted),
                    "clean_ascii_fragment_count": str(count),
                    "legacy_surface_positions_1based": ",".join(map(str, mapped_positions)),
                    "legacy_interlinear_row_present": str(int(bool(flat))),
                    "legacy_mapping_status": state,
                }
                totals["source_groups"] += 1
                totals[state] += 1
                totals["clean_ascii_fragments"] += count
                totals["cleaner_created_boundaries"] += max(count - 1, 0)
                editions[edition]["source_groups"] += 1
                editions[edition][state] += 1
                editions[edition]["clean_ascii_fragments"] += count
                editions[edition]["cleaner_created_boundaries"] += max(count - 1, 0)
                yield row, totals, editions, separator_counts, legacy, seen, zero_rows
            for boundary in source_boundaries:
                name = SEPARATOR_NAMES[boundary]
                separator_counts[name] += 1
                totals["manual_boundaries"] += 1
                editions[edition]["manual_boundaries"] += 1
                editions[edition][f"separator:{name}"] += 1
            totals["source_rows"] += 1
            editions[edition]["source_rows"] += 1
            editions[edition]["zero_token_rows"] += int(not flat)


def main() -> None:
    observed = {
        "ZL3b": digest(SOURCES["ZL3b"]),
        "IT2a": digest(SOURCES["IT2a"]),
        "RF1b": digest(SOURCES["RF1b"]),
        "interlinear": digest(INTERLINEAR),
        "spec": digest(SPEC),
        "producer": digest(PRODUCER),
        "atlas": digest(ATLAS),
        "result": digest(RESULT),
        "report": digest(REPORT),
    }
    if observed != EXPECTED_HASHES:
        raise RuntimeError("frozen artifact hash drift")

    checks = 0
    ids: set[str] = set()
    last_state = None
    with ATLAS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != FIELDS:
            raise RuntimeError("atlas field order mismatch")
        checks += 1
        generator = expected_rows()
        for stored, generated in zip(reader, generator, strict=True):
            expected, totals, editions, separator_counts, legacy, seen, zero_rows = generated
            if stored != expected:
                mismatch = next(field for field in FIELDS if stored.get(field) != expected.get(field))
                raise RuntimeError(f"atlas mismatch at {expected['source_group_id']} field {mismatch}")
            if stored["source_group_id"] in ids:
                raise RuntimeError("duplicate atlas group id")
            ids.add(stored["source_group_id"])
            checks += len(FIELDS) + 1
            last_state = (totals, editions, separator_counts, legacy, seen, zero_rows)
    if last_state is None:
        raise RuntimeError("empty atlas")
    totals, editions, separator_counts, legacy, seen, zero_rows = last_state
    if seen - zero_rows != set(legacy):
        raise RuntimeError("final source/legacy key partition mismatch")
    checks += 1

    # Controls cover all separator states and both cleaner failure modes.
    synthetic_groups, synthetic_boundaries = groups("a.b,c<->d<~>e")
    if synthetic_groups != ["a", "b", "c", "d", "e"] or synthetic_boundaries != [".", ",", "<->", "<~>"]:
        raise RuntimeError("separator-state mutation control failed")
    if clean("q@221;r") != ["q", "r"] or clean("@140;") or clean("[ch:sh]ol") != ["chol"] or clean("{cto}"):
        raise RuntimeError("legacy-cleaner mutation control failed")
    for malformed in ("a..b", "a."):
        try:
            groups(malformed)
        except ValueError:
            pass
        else:
            raise RuntimeError("malformed topology mutation was accepted")
    checks += 6

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_inputs = {
        "ZL3b": EXPECTED_HASHES["ZL3b"],
        "IT2a": EXPECTED_HASHES["IT2a"],
        "RF1b": EXPECTED_HASHES["RF1b"],
        "pre_grounding_interlinear": EXPECTED_HASHES["interlinear"],
    }
    expected_counts = {
        "source_rows": totals["source_rows"],
        "legacy_interlinear_rows": len(legacy),
        "source_rows_absent_from_legacy_interlinear": len(zero_rows),
        "source_groups": totals["source_groups"],
        "manual_boundaries": totals["manual_boundaries"],
        "clean_ascii_fragments": totals["clean_ascii_fragments"],
        "zero_ascii_fragment_groups": totals["ZERO_ASCII_FRAGMENT"],
        "one_ascii_fragment_groups": totals["ONE_ASCII_FRAGMENT"],
        "multi_ascii_fragment_groups": totals["MULTI_ASCII_FRAGMENT"],
        "cleaner_created_nonmanual_boundaries": totals["cleaner_created_boundaries"],
        "manual_separator_states": dict(sorted(separator_counts.items())),
    }
    expected_gates = {
        "all_source_rows_accounted": totals["source_rows"] == 15_985,
        "legacy_row_partition_exact": len(legacy) == 15_960 and len(zero_rows) == 25,
        "all_legacy_surface_tokens_reconstructed": totals["clean_ascii_fragments"] == 118_011,
        "all_source_groups_emitted_once": len(ids) == totals["source_groups"] == 115_470,
        "manual_boundary_topology_exact": totals["manual_boundaries"] == totals["source_groups"] - totals["source_rows"],
        "separator_vocabulary_exact": set(separator_counts) == set(SEPARATOR_NAMES.values()),
        "no_extended_entity_expansion": True,
        "no_formal_or_semantic_assignment": True,
    }
    comparisons = {
        "status": result.get("status") == STATUS,
        "inputs": result.get("inputs") == expected_inputs,
        "implementation_spec": result["implementation"]["spec_sha256"] == EXPECTED_HASHES["spec"],
        "implementation_producer": result["implementation"]["producer_sha256"] == EXPECTED_HASHES["producer"],
        "implementation_flags": result["implementation"]["extended_entities_expanded"] is False
        and result["implementation"]["formal_parser_used"] is False
        and result["implementation"]["semantic_fields_used"] is False,
        "separator_state_order": result["implementation"]["source_separator_states"] == list(SEPARATOR_NAMES.values()),
        "counts": result.get("counts") == expected_counts,
        "by_edition": result.get("by_edition") == {edition: dict(sorted(counts.items())) for edition, counts in editions.items()},
        "output": result.get("output") == {
            "atlas": "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
            "atlas_rows": len(ids),
            "atlas_sha256": EXPECTED_HASHES["atlas"],
        },
        "gates": result.get("gates") == expected_gates and all(expected_gates.values()),
        "claim_ceiling": result.get("claim_ceiling") == CLAIM_CEILING,
    }
    failed = [name for name, passed in comparisons.items() if not passed]
    if failed:
        raise RuntimeError("result reconstruction failed: " + ", ".join(failed))
    checks += len(comparisons)

    validation = {
        "status": "PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "inputs": observed,
        "reconstructed_counts": expected_counts,
        "reconstructed_by_edition": {edition: dict(sorted(counts.items())) for edition, counts in editions.items()},
        "mutation_controls": {
            "four_separator_states": "PASS",
            "cleaner_zero_and_split": "PASS",
            "empty_and_trailing_group_rejection": "PASS",
        },
        "isolation": {
            "producer_imported": False,
            "legacy_parser_imported": False,
            "extended_entities_expanded": False,
            "formal_or_semantic_fields_used": False,
        },
        "claim_ceiling": CLAIM_CEILING,
        "validator_sha256": digest(Path(__file__)),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# Independent source-separator transcription validation

Status: **PASS_INDEPENDENT_SOURCE_SEPARATOR_RECONSTRUCTION**

The clean-room validator made **{checks:,}** successful checks without importing
the producer or legacy parser.  It reconstructed all **{expected_counts['source_rows']:,}**
source rows, **{expected_counts['source_groups']:,}** source groups,
**{expected_counts['manual_boundaries']:,}** explicit separators, and their exact
**{expected_counts['clean_ascii_fragments']:,}**-fragment legacy mapping.

It independently confirms **{expected_counts['zero_ascii_fragment_groups']:,}**
zero-fragment groups, **{expected_counts['multi_ascii_fragment_groups']:,}**
multi-fragment groups, and **{expected_counts['cleaner_created_nonmanual_boundaries']:,}**
cleaner-created nonmanual boundaries.  Exact atlas rows, source/interlinear key
partition, hashes, counts, gates, and claim ceiling all match.  Synthetic
controls reject empty/trailing source groups and exercise all four separator
states plus both cleaner failure modes.

This validates transcription provenance and loss accounting only.  It assigns
no authorial word boundary, sound, grammatical role, lexeme, plaintext,
language, or translation.
"""
    VALIDATION_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
