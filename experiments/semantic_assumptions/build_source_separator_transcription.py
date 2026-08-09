#!/usr/bin/env python3
"""Build a source-bound, separator-aware IVTFF transcription atlas."""

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
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
OUTPUT_TSV = RESULTS / "source_separator_transcription.tsv"
OUTPUT_JSON = RESULTS / "source_separator_transcription.json"
OUTPUT_REPORT = RESULTS / "source_separator_transcription_report.md"

SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
EXPECTED_INPUTS = {
    "ZL3b": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "IT2a": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "RF1b": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "pre_grounding_interlinear": "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legacy_clean(text: str) -> list[str]:
    text = SQUARE_RE.sub(lambda match: match.group(1), text)
    text = BRACE_RE.sub("", text)
    text = ANGLE_RE.sub(" ", text)
    text = text.replace("?", "").replace("!", "").replace("*", "").replace("'", "")
    return [
        cleaned
        for part in SPLIT_RE.split(text)
        if (cleaned := re.sub(r"[^A-Za-z]", "", part).lower())
    ]


def split_source_groups(text: str) -> tuple[list[str], list[str]]:
    """Return verbatim groups (minus row-control tags) and between-group markers."""
    groups: list[str] = []
    boundaries: list[str] = []
    pending: list[str] = []
    current: list[str] = []
    index = 0

    def separator(marker: str) -> None:
        nonlocal current, pending
        group = "".join(current).strip()
        current = []
        if group:
            if groups:
                if len(pending) != 1:
                    raise RuntimeError("empty source group or compound separator")
                boundaries.append(pending[0])
            groups.append(group)
            pending = []
        pending.append(marker)

    while index < len(text):
        if text.startswith("<->", index):
            separator("<->")
            index += 3
            continue
        if text.startswith("<~>", index):
            separator("<~>")
            index += 3
            continue
        char = text[index]
        if char == "<":
            end = text.find(">", index + 1)
            if end < 0:
                raise RuntimeError("unterminated angle annotation")
            tag = text[index:end + 1]
            if tag not in {"<%>", "<$>"}:
                current.append(tag)
            index = end + 1
            continue
        if char in "[{":
            close = "]" if char == "[" else "}"
            end = text.find(close, index + 1)
            if end < 0:
                raise RuntimeError("unterminated alternative or brace form")
            current.append(text[index:end + 1])
            index = end + 1
            continue
        if char in ".,":
            separator(char)
            index += 1
            continue
        current.append(char)
        index += 1

    group = "".join(current).strip()
    if group:
        if groups:
            if len(pending) != 1:
                raise RuntimeError("empty source group or compound separator")
            boundaries.append(pending[0])
        groups.append(group)
        pending = []
    if pending:
        raise RuntimeError("trailing source separator without group")
    if not groups or len(boundaries) != len(groups) - 1:
        raise RuntimeError("invalid source group topology")
    return groups, boundaries


def read_interlinear() -> dict[tuple[str, str], list[str]]:
    with INTERLINEAR.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    output: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        key = (row["edition"], row["locus"])
        if key in output:
            raise RuntimeError(f"duplicate interlinear key {key}")
        output[key] = row["surface"].split()
    return output


def main() -> None:
    observed = {edition: sha256(path) for edition, path in SOURCES.items()}
    observed["pre_grounding_interlinear"] = sha256(INTERLINEAR)
    if observed != EXPECTED_INPUTS:
        raise RuntimeError("source-separator input drift")

    interlinear = read_interlinear()
    atlas: list[dict[str, str | int]] = []
    seen_source: set[tuple[str, str]] = set()
    by_edition: dict[str, Counter] = {edition: Counter() for edition in SOURCES}
    separators = Counter()
    zero_row_keys: set[tuple[str, str]] = set()

    for edition, path in SOURCES.items():
        page = ""
        metadata: dict[str, str] = {}
        source_row_index = 0
        for raw_line in path.read_text(encoding="utf-8", errors="strict").splitlines():
            page_match = PAGE_RE.match(raw_line)
            if page_match:
                page = page_match.group(1).lower()
                metadata = dict(META_RE.findall(page_match.group(2)))
                continue
            match = LOCUS_RE.match(raw_line)
            if not match:
                continue
            locus, code, _comment, text = match.groups()
            key = (edition, locus)
            if key in seen_source:
                raise RuntimeError(f"duplicate source key {key}")
            seen_source.add(key)
            source_row_index += 1
            groups, boundaries = split_source_groups(text)
            fragments_by_group = [legacy_clean(group) for group in groups]
            flat = [fragment for fragments in fragments_by_group for fragment in fragments]
            if flat:
                if key not in interlinear:
                    raise RuntimeError(f"nonempty source row missing in interlinear {key}")
                if flat != interlinear[key]:
                    raise RuntimeError(f"legacy surface mismatch at {key}")
            else:
                if key in interlinear:
                    raise RuntimeError(f"zero-token source row present in interlinear {key}")
                zero_row_keys.add(key)

            source_positions = 0
            scope = (
                "CONFIRMED_PROSE"
                if len(code) > 1 and code[1] == "P" and metadata.get("L", "") in {"A", "B"}
                else "DIAGNOSTIC_NONPROSE"
            )
            for group_index, (group, fragments) in enumerate(zip(groups, fragments_by_group), 1):
                count = len(fragments)
                positions = list(range(source_positions + 1, source_positions + count + 1))
                source_positions += count
                mapping_status = (
                    "ZERO_ASCII_FRAGMENT"
                    if count == 0
                    else "ONE_ASCII_FRAGMENT"
                    if count == 1
                    else "MULTI_ASCII_FRAGMENT"
                )
                left = "LINE_START" if group_index == 1 else SEPARATOR_NAMES[boundaries[group_index - 2]]
                right = (
                    "LINE_END"
                    if group_index == len(groups)
                    else SEPARATOR_NAMES[boundaries[group_index - 1]]
                )
                if any(character in group for character in "\t\r\n"):
                    raise RuntimeError("TSV-unsafe source group")
                atlas.append({
                    "source_group_id": f"{edition}|{locus}|G{group_index:03d}",
                    "edition": edition,
                    "locus": locus,
                    "page": page,
                    "section": metadata.get("I", ""),
                    "currier": metadata.get("L", ""),
                    "hand": metadata.get("H", ""),
                    "code": code,
                    "kind": code[1] if len(code) > 1 else "",
                    "grammar_scope": scope,
                    "source_row_index": source_row_index,
                    "source_group_index": group_index,
                    "source_group_count": len(groups),
                    "paragraph_start": int("<%>" in text),
                    "paragraph_end": int("<$>" in text),
                    "left_separator": left,
                    "right_separator": right,
                    "ivtff_group_raw": group,
                    "clean_ascii_fragments": " ".join(fragments),
                    "clean_ascii_fragment_count": count,
                    "legacy_surface_positions_1based": ",".join(map(str, positions)),
                    "legacy_interlinear_row_present": int(bool(flat)),
                    "legacy_mapping_status": mapping_status,
                })
                by_edition[edition]["source_groups"] += 1
                by_edition[edition][mapping_status] += 1
                by_edition[edition]["clean_ascii_fragments"] += count
                by_edition[edition]["cleaner_created_boundaries"] += max(0, count - 1)
            for marker in boundaries:
                separators[SEPARATOR_NAMES[marker]] += 1
                by_edition[edition][f"separator:{SEPARATOR_NAMES[marker]}"] += 1
            by_edition[edition]["source_rows"] += 1
            by_edition[edition]["manual_boundaries"] += len(boundaries)
            by_edition[edition]["zero_token_rows"] += int(not flat)

    if set(interlinear) != seen_source - zero_row_keys:
        raise RuntimeError("source/interlinear key partition mismatch")

    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(atlas)

    totals = Counter()
    for counts in by_edition.values():
        totals.update(counts)
    payload = {
        "status": STATUS,
        "inputs": observed,
        "implementation": {
            "spec_sha256": sha256(SPEC),
            "producer_sha256": sha256(Path(__file__)),
            "source_separator_states": list(SEPARATOR_NAMES.values()),
            "extended_entities_expanded": False,
            "formal_parser_used": False,
            "semantic_fields_used": False,
        },
        "counts": {
            "source_rows": totals["source_rows"],
            "legacy_interlinear_rows": len(interlinear),
            "source_rows_absent_from_legacy_interlinear": totals["zero_token_rows"],
            "source_groups": totals["source_groups"],
            "manual_boundaries": totals["manual_boundaries"],
            "clean_ascii_fragments": totals["clean_ascii_fragments"],
            "zero_ascii_fragment_groups": totals["ZERO_ASCII_FRAGMENT"],
            "one_ascii_fragment_groups": totals["ONE_ASCII_FRAGMENT"],
            "multi_ascii_fragment_groups": totals["MULTI_ASCII_FRAGMENT"],
            "cleaner_created_nonmanual_boundaries": totals["cleaner_created_boundaries"],
            "manual_separator_states": dict(sorted(separators.items())),
        },
        "by_edition": {edition: dict(sorted(counts.items())) for edition, counts in by_edition.items()},
        "output": {
            "atlas": str(OUTPUT_TSV.relative_to(ROOT)),
            "atlas_rows": len(atlas),
            "atlas_sha256": sha256(OUTPUT_TSV),
        },
        "gates": {
            "all_source_rows_accounted": totals["source_rows"] == 15_985,
            "legacy_row_partition_exact": len(interlinear) == 15_960 and totals["zero_token_rows"] == 25,
            "all_legacy_surface_tokens_reconstructed": totals["clean_ascii_fragments"] == 118_011,
            "all_source_groups_emitted_once": len(atlas) == totals["source_groups"] == 115_470,
            "manual_boundary_topology_exact": totals["manual_boundaries"] == totals["source_groups"] - totals["source_rows"],
            "separator_vocabulary_exact": set(separators) == set(SEPARATOR_NAMES.values()),
            "no_extended_entity_expansion": True,
            "no_formal_or_semantic_assignment": True,
        },
        "claim_ceiling": CLAIM_CEILING,
    }
    if not all(payload["gates"].values()):
        raise RuntimeError("source-separator gate failure")
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    c = payload["counts"]
    report = f"""# Source-separator transcription correction

Status: **{STATUS}**

The three frozen human IVTFF sources contain **{c['source_rows']:,}** reading
rows, **{c['source_groups']:,}** source-separated groups, and
**{c['manual_boundaries']:,}** explicit source boundaries.  The old
pre-grounding `surface` exactly reconstructs its own **{c['clean_ascii_fragments']:,}**
ASCII fragments, but it is not a complete representation of those sources.

- **{c['zero_ascii_fragment_groups']:,}** source groups produce no ASCII token;
  **{c['source_rows_absent_from_legacy_interlinear']:,}** whole reading rows
  disappear for this reason.
- **{c['multi_ascii_fragment_groups']:,}** single source groups produce multiple
  ASCII fragments, creating **{c['cleaner_created_nonmanual_boundaries']:,}**
  boundaries that no transcriber marked.
- Only **{c['one_ascii_fragment_groups']:,}** source groups map one-to-one to an
  old ASCII token.

The new atlas stores every source group, its exact left/right separator state,
and its complete mapping to the legacy fragments.  Extended `@number;` entities
and uncertain/alternative forms remain verbatim; none is guessed or expanded.

The source separators comprise {c['manual_separator_states']['DEFINITE_SPACE']:,}
confident apparent spaces, {c['manual_separator_states']['UNCERTAIN_SMALL_SPACE']:,}
uncertain small spaces, {c['manual_separator_states']['DRAWING_INTERRUPTION']:,}
drawing interruptions, and
{c['manual_separator_states']['DRAWING_INTERRUPTION_UNALIGNED']:,} unaligned
drawing interruptions.

This corrects the representation boundary.  It does not decide which spaces
are authorial and supplies no sound, word, role, lexeme, plaintext, language,
or translation.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
