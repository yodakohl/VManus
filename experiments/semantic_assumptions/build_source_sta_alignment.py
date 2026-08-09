#!/usr/bin/env python3
"""Build the official STA1/source-group alignment without semantic parsing."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SPEC = HERE / "SOURCE_STA_ALIGNMENT_SPEC.md"
SOURCE_ATLAS = RESULTS / "source_separator_transcription.tsv"
OUTPUT_TSV = RESULTS / "source_sta_group_alignment.tsv"
OUTPUT_JSON = RESULTS / "source_sta_group_alignment.json"
OUTPUT_REPORT = RESULTS / "source_sta_group_alignment_report.md"

NATIVE = {
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA = {
    edition: ROOT / "transcription" / "sources" / "sta" / f"{edition}.txt"
    for edition in NATIVE
}
RULE_EXACT = {
    "IT2a": ROOT / "transcription" / "sources" / "sta" / "STA-EvaT_def.bit",
    "ZL3b": ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit",
    "RF1b": ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit",
}
RULE_BASIC = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_Bint.bit"

EXPECTED_HASHES = {
    "spec": "5b2334f67e5ee24bbf8fdef7cefdc9579ab18e3a293817c05f4f0b84725d799d",
    "source_atlas": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "native_IT2a": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "native_ZL3b": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "native_RF1b": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "sta_IT2a": "215f2d05690828c00bd4ae00d6201df31050adcd81601343b142ae91b9dfeee4",
    "sta_ZL3b": "8438ba1c45f47fe1d06b5262cbcdf60ce69158a0edbd4dd802612896f3217e2a",
    "sta_RF1b": "81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17",
    "rule_exact_Eva": "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    "rule_exact_EvaT": "c8ff6e19b0273ceaa2f5a8a82584dc3bc9eec08f004864836988969601f9c96c",
    "rule_basic": "3c39164a76781ab781b5fbce2bcf75cee3183013a8d994d0463b2aa8f113a289",
}

OFFICIAL_URLS = {
    "native_IT2a": "https://www.voynich.nu/data/IT2a-n.txt",
    "native_ZL3b": "https://www.voynich.nu/data/ZL3b-n.txt",
    "native_RF1b": "https://www.voynich.nu/data/RF1b-e.txt",
    "sta_IT2a": "https://www.voynich.nu/data/sta/IT2a.txt",
    "sta_ZL3b": "https://www.voynich.nu/data/sta/ZL3b.txt",
    "sta_RF1b": "https://www.voynich.nu/data/sta/RF1b.txt",
    "rule_exact_Eva": "https://www.voynich.nu/software/bitrans/STA-Eva_def.bit",
    "rule_exact_EvaT": "https://www.voynich.nu/software/bitrans/STA-EvaT_def.bit",
    "rule_basic": "https://www.voynich.nu/software/bitrans/STA-Eva_Bint.bit",
}

LOCUS_RE = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$")
RULE_RE = re.compile(r"^([A-Z][0-9a-z])\s+(\S+)$")
CODE_RE = re.compile(r"[A-Z][0-9a-z]")
INLINE_COMMENT_RE = re.compile(r"<![^>]*>")

SEPARATOR_NAMES = {
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION",
    "<~>": "DRAWING_INTERRUPTION_UNALIGNED",
}

FIELDS = [
    "source_group_id",
    "edition",
    "locus",
    "source_group_index",
    "source_group_count",
    "left_separator",
    "right_separator",
    "sta_group_raw",
    "primary_sta_codes",
    "primary_sta_families",
    "primary_sta_symbol_count",
    "alternative_site_count",
    "nearest_basic_eva_primary",
]

STATUS = "PASS_LOSSLESS_SOURCE_SEPARATOR_PRESERVING_STA_ALIGNMENT"
CLAIM_CEILING = (
    "This pass establishes a lossless common STA1 representation aligned to the source "
    "separator groups, plus an explicitly lossy nearest-basic-EVA convenience view. STA "
    "codes are transcription symbols, not proven physical letters, sounds, morphemes, "
    "words, meanings, plaintext, language, or translation."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_paths() -> dict[str, Path]:
    return {
        "spec": SPEC,
        "source_atlas": SOURCE_ATLAS,
        "native_IT2a": NATIVE["IT2a"],
        "native_ZL3b": NATIVE["ZL3b"],
        "native_RF1b": NATIVE["RF1b"],
        "sta_IT2a": STA["IT2a"],
        "sta_ZL3b": STA["ZL3b"],
        "sta_RF1b": STA["RF1b"],
        "rule_exact_Eva": RULE_EXACT["ZL3b"],
        "rule_exact_EvaT": RULE_EXACT["IT2a"],
        "rule_basic": RULE_BASIC,
    }


def load_rules(path: Path) -> dict[str, str]:
    output: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = RULE_RE.match(line)
        if not match:
            continue
        code, value = match.groups()
        if code in output:
            raise RuntimeError(f"duplicate rule {code} in {path.name}")
        output[code] = value
    if not output:
        raise RuntimeError(f"empty rule file {path.name}")
    return output


def split_source_groups(text: str) -> tuple[list[str], list[str]]:
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
        if text.startswith("<->", index) or text.startswith("<~>", index):
            separator(text[index:index + 3])
            index += 3
            continue
        character = text[index]
        if character == "<":
            end = text.find(">", index + 1)
            if end < 0:
                raise RuntimeError("unterminated angle annotation")
            tag = text[index:end + 1]
            if tag not in {"<%>", "<$>"}:
                current.append(tag)
            index = end + 1
            continue
        if character in "[{":
            close = "]" if character == "[" else "}"
            end = text.find(close, index + 1)
            if end < 0:
                raise RuntimeError("unterminated bracket form")
            current.append(text[index:end + 1])
            index = end + 1
            continue
        if character in ".,":
            separator(character)
            index += 1
            continue
        current.append(character)
        index += 1

    group = "".join(current).strip()
    if group:
        if groups:
            if len(pending) != 1:
                raise RuntimeError("empty source group or compound separator")
            boundaries.append(pending[0])
        groups.append(group)
        pending = []
    if pending or not groups or len(boundaries) != len(groups) - 1:
        raise RuntimeError("invalid source group topology")
    return groups, boundaries


def parse_ivtff(path: Path) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        match = LOCUS_RE.match(line)
        if not match:
            continue
        locus, code, _comment, text = match.groups()
        if locus in rows:
            raise RuntimeError(f"duplicate locus {locus} in {path.name}")
        rows[locus] = (code, text)
    return rows


def parse_sta_sequence(sequence: str) -> list[str]:
    if not sequence:
        return []
    if len(sequence) % 2:
        raise RuntimeError(f"invalid STA sequence {sequence!r}")
    codes = [sequence[index:index + 2] for index in range(0, len(sequence), 2)]
    if any(CODE_RE.fullmatch(code) is None for code in codes):
        raise RuntimeError(f"invalid STA sequence {sequence!r}")
    return codes


def primary_sta_codes(group: str) -> tuple[list[str], int, list[list[str]]]:
    primary: list[str] = []
    alternatives: list[list[str]] = []
    index = 0
    sites = 0
    while index < len(group):
        if group[index] == "<":
            end = group.find(">", index + 1)
            if end < 0:
                raise RuntimeError("unterminated STA angle annotation")
            index = end + 1
            continue
        if group[index] == "[":
            end = group.find("]", index + 1)
            if end < 0:
                raise RuntimeError("unterminated STA alternative")
            options = group[index + 1:end].split(":")
            if len(options) < 2:
                raise RuntimeError("invalid STA alternative")
            parsed = [parse_sta_sequence(option) for option in options]
            primary.extend(parsed[0])
            alternatives.extend(parsed)
            sites += 1
            index = end + 1
            continue
        if group[index] in "]:":
            raise RuntimeError("stray STA markup")
        code = group[index:index + 2]
        if CODE_RE.fullmatch(code) is None:
            raise RuntimeError(f"invalid STA code at {group!r}")
        primary.append(code)
        alternatives.append([code])
        index += 2
    return primary, sites, alternatives


def convert_sta_markup(group: str, rules: dict[str, str]) -> str:
    output: list[str] = []
    index = 0
    while index < len(group):
        character = group[index]
        if character == "<":
            end = group.find(">", index + 1)
            if end < 0:
                raise RuntimeError("unterminated STA angle annotation")
            output.append(group[index:end + 1])
            index = end + 1
            continue
        if character in "[]:":
            output.append(character)
            index += 1
            continue
        code = group[index:index + 2]
        if CODE_RE.fullmatch(code) is None or code not in rules:
            raise RuntimeError(f"unmapped STA code {code!r}")
        output.append(rules[code])
        index += 2
    return "".join(output)


def load_crosswalk() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    with SOURCE_ATLAS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["source_group_id"]
        if key in by_id:
            raise RuntimeError(f"duplicate source-group ID {key}")
        by_id[key] = row
    return rows, by_id


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> None:
    observed_hashes = {name: sha256(path) for name, path in input_paths().items()}
    if observed_hashes != EXPECTED_HASHES:
        raise RuntimeError("source-STA input drift")

    exact_rules = {
        edition: load_rules(path)
        for edition, path in RULE_EXACT.items()
    }
    basic_rules = load_rules(RULE_BASIC)
    crosswalk_rows, crosswalk_by_id = load_crosswalk()

    output_by_id: dict[str, dict[str, str | int]] = {}
    by_edition: dict[str, Counter] = {edition: Counter() for edition in NATIVE}
    observed_codes: set[str] = set()
    observed_families: set[str] = set()
    separator_counts = Counter()

    for edition in NATIVE:
        native_rows = parse_ivtff(NATIVE[edition])
        sta_rows = parse_ivtff(STA[edition])
        if native_rows.keys() != sta_rows.keys():
            raise RuntimeError(f"native/STA locus-key mismatch for {edition}")
        for locus in native_rows:
            native_code, native_text = native_rows[locus]
            sta_code, sta_text = sta_rows[locus]
            if native_code != sta_code:
                raise RuntimeError(f"native/STA locus-code mismatch at {edition}|{locus}")
            native_groups, native_boundaries = split_source_groups(native_text)
            sta_groups, sta_boundaries = split_source_groups(sta_text)
            if native_boundaries != sta_boundaries or len(native_groups) != len(sta_groups):
                raise RuntimeError(f"native/STA topology mismatch at {edition}|{locus}")
            reverse_row_parts: list[str] = []
            for index, sta_group in enumerate(sta_groups):
                if index:
                    reverse_row_parts.append(sta_boundaries[index - 1])
                reverse_row_parts.append(convert_sta_markup(sta_group, exact_rules[edition]))
            reverse_row = "".join(reverse_row_parts)
            native_no_comments = INLINE_COMMENT_RE.sub("", native_text).replace("<%>", "").replace("<$>", "")
            if reverse_row != native_no_comments:
                raise RuntimeError(f"native/STA row reverse mismatch at {edition}|{locus}")

            by_edition[edition]["loci"] += 1
            by_edition[edition]["groups"] += len(sta_groups)
            by_edition[edition]["boundaries"] += len(sta_boundaries)
            for boundary in sta_boundaries:
                separator_counts[SEPARATOR_NAMES[boundary]] += 1

            for group_index, (native_group, sta_group) in enumerate(zip(native_groups, sta_groups), 1):
                group_id = f"{edition}|{locus}|G{group_index:03d}"
                if group_id not in crosswalk_by_id:
                    raise RuntimeError(f"missing source-group crosswalk {group_id}")
                source = crosswalk_by_id[group_id]
                if (
                    source["edition"] != edition
                    or source["locus"] != locus
                    or int(source["source_group_index"]) != group_index
                    or int(source["source_group_count"]) != len(sta_groups)
                    or source["ivtff_group_raw"] != native_group
                ):
                    raise RuntimeError(f"source-group crosswalk mismatch {group_id}")
                left = "LINE_START" if group_index == 1 else SEPARATOR_NAMES[sta_boundaries[group_index - 2]]
                right = "LINE_END" if group_index == len(sta_groups) else SEPARATOR_NAMES[sta_boundaries[group_index - 1]]
                if source["left_separator"] != left or source["right_separator"] != right:
                    raise RuntimeError(f"separator crosswalk mismatch {group_id}")
                native_no_comment = INLINE_COMMENT_RE.sub("", native_group)
                if convert_sta_markup(sta_group, exact_rules[edition]) != native_no_comment:
                    raise RuntimeError(f"native/STA group reverse mismatch {group_id}")

                primary, alternative_sites, every_path = primary_sta_codes(sta_group)
                all_codes = {code for path in every_path for code in path}
                missing_exact = all_codes - exact_rules[edition].keys()
                missing_basic = all_codes - basic_rules.keys()
                if missing_exact or missing_basic:
                    raise RuntimeError(f"STA rule coverage failure {group_id}: {missing_exact} {missing_basic}")
                observed_codes.update(all_codes)
                observed_families.update(code[0] for code in all_codes)
                nearest = "".join(basic_rules[code] for code in primary)
                output_by_id[group_id] = {
                    "source_group_id": group_id,
                    "edition": edition,
                    "locus": locus,
                    "source_group_index": group_index,
                    "source_group_count": len(sta_groups),
                    "left_separator": left,
                    "right_separator": right,
                    "sta_group_raw": sta_group,
                    "primary_sta_codes": " ".join(primary),
                    "primary_sta_families": "".join(code[0] for code in primary),
                    "primary_sta_symbol_count": len(primary),
                    "alternative_site_count": alternative_sites,
                    "nearest_basic_eva_primary": nearest,
                }
                by_edition[edition]["primary_symbols"] += len(primary)
                by_edition[edition]["alternative_sites"] += alternative_sites
                by_edition[edition]["groups_with_alternatives"] += int(alternative_sites > 0)

    if len(output_by_id) != len(crosswalk_rows) or set(output_by_id) != set(crosswalk_by_id):
        raise RuntimeError("source-group output/crosswalk coverage mismatch")
    ordered = [output_by_id[row["source_group_id"]] for row in crosswalk_rows]

    temporary_tsv = OUTPUT_TSV.with_suffix(".tsv.tmp")
    with temporary_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)
    temporary_tsv.replace(OUTPUT_TSV)

    summary = {
        "status": STATUS,
        "claim_ceiling": CLAIM_CEILING,
        "official_sources": OFFICIAL_URLS,
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": observed_hashes[name]}
            for name, path in input_paths().items()
        },
        "counts": {
            "editions": len(NATIVE),
            "reading_rows": sum(counter["loci"] for counter in by_edition.values()),
            "source_groups": len(ordered),
            "source_boundaries": sum(counter["boundaries"] for counter in by_edition.values()),
            "primary_sta_symbols": sum(counter["primary_symbols"] for counter in by_edition.values()),
            "observed_sta_codes_all_paths": len(observed_codes),
            "observed_sta_families_all_paths": len(observed_families),
            "alternative_sites": sum(counter["alternative_sites"] for counter in by_edition.values()),
            "groups_with_alternatives": sum(counter["groups_with_alternatives"] for counter in by_edition.values()),
            "native_sta_locus_key_mismatches": 0,
            "native_sta_locus_code_mismatches": 0,
            "native_sta_topology_mismatches": 0,
            "native_sta_reverse_row_mismatches": 0,
            "native_sta_reverse_group_mismatches": 0,
            "unmapped_observed_sta_codes": 0,
            "source_group_crosswalk_mismatches": 0,
        },
        "by_edition": {
            edition: dict(sorted(counter.items()))
            for edition, counter in by_edition.items()
        },
        "separator_counts": dict(sorted(separator_counts.items())),
        "observed_sta_codes_all_paths": sorted(observed_codes),
        "observed_sta_families_all_paths": sorted(observed_families),
        "output": {
            "path": str(OUTPUT_TSV.relative_to(ROOT)),
            "rows": len(ordered),
            "sha256": sha256(OUTPUT_TSV),
        },
        "gates": {
            "exact_input_hashes": True,
            "exact_locus_keys_and_codes": True,
            "exact_group_separator_topology": True,
            "exact_reverse_native_rows_and_groups": True,
            "all_sta_codes_fixed_width_and_rule_covered": True,
            "exact_source_group_crosswalk": True,
            "raw_sta_retained_as_authoritative_surface": True,
            "nearest_basic_eva_marked_lossy": True,
            "zero_formal_or_semantic_assignments": True,
        },
    }
    atomic_text(OUTPUT_JSON, json.dumps(summary, indent=2, sort_keys=True) + "\n")

    report = f"""# Source-preserving STA alignment

Status: **{STATUS}**

The official STA1 level-0 files align exactly to all **{summary['counts']['reading_rows']:,}**
native reading rows, **{summary['counts']['source_groups']:,}** source groups, and
**{summary['counts']['source_boundaries']:,}** source separators. Applying the official
edition-specific bidirectional rules reconstructs every native row and group exactly
after removing only the inline comments that the STA release declares omitted.

The aligned primary paths contain **{summary['counts']['primary_sta_symbols']:,}** STA
symbols. Across every supplied alternative, **{summary['counts']['observed_sta_codes_all_paths']}**
codes in **{summary['counts']['observed_sta_families_all_paths']}** families occur; all are
covered by both the exact reverse rules and the explicitly lossy nearest-basic-EVA
rules. ZL3b contains **{summary['counts']['alternative_sites']}** marked alternative
sites across **{summary['counts']['groups_with_alternatives']}** groups; the raw markup
retains every option.

This repairs the common character layer without inventing rare-glyph expansions or
boundaries. STA codes remain transcription symbols, not proven letters, sounds,
morphemes, words, meanings, plaintext, language, or translation.
"""
    atomic_text(OUTPUT_REPORT, report)


if __name__ == "__main__":
    main()
