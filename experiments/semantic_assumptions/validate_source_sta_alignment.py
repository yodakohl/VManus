#!/usr/bin/env python3
"""Clean-room validation of the source-preserving STA1 alignment."""

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

SPEC = HERE / "SOURCE_STA_ALIGNMENT_SPEC.md"
PRODUCER = HERE / "build_source_sta_alignment.py"
CROSSWALK = RESULTS / "source_separator_transcription.tsv"
PRODUCTION_TSV = RESULTS / "source_sta_group_alignment.tsv"
PRODUCTION_JSON = RESULTS / "source_sta_group_alignment.json"
PRODUCTION_REPORT = RESULTS / "source_sta_group_alignment_report.md"
VALIDATION_JSON = RESULTS / "source_sta_group_alignment_validation.json"
VALIDATION_REPORT = RESULTS / "source_sta_group_alignment_validation_report.md"

NATIVE = {
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA = {
    key: ROOT / "transcription" / "sources" / "sta" / f"{key}.txt"
    for key in NATIVE
}
EXACT_RULE_PATH = {
    "IT2a": ROOT / "transcription" / "sources" / "sta" / "STA-EvaT_def.bit",
    "ZL3b": ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit",
    "RF1b": ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit",
}
BASIC_RULE_PATH = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_Bint.bit"

EXPECTED_HASHES = {
    "spec": "5b2334f67e5ee24bbf8fdef7cefdc9579ab18e3a293817c05f4f0b84725d799d",
    "producer": "8b609848e877a8b7e1671a2097ae12a012288ae30e2b0f9f5c3b0e61c1dd32da",
    "crosswalk": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "native_IT2a": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "native_ZL3b": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "native_RF1b": "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    "sta_IT2a": "215f2d05690828c00bd4ae00d6201df31050adcd81601343b142ae91b9dfeee4",
    "sta_ZL3b": "8438ba1c45f47fe1d06b5262cbcdf60ce69158a0edbd4dd802612896f3217e2a",
    "sta_RF1b": "81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17",
    "rule_exact_Eva": "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    "rule_exact_EvaT": "c8ff6e19b0273ceaa2f5a8a82584dc3bc9eec08f004864836988969601f9c96c",
    "rule_basic": "3c39164a76781ab781b5fbce2bcf75cee3183013a8d994d0463b2aa8f113a289",
    "production_tsv": "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    "production_json": "1df2786fa95c8dcca4845c86e13003e968ad36ae760a5f258a6f936eb7abcad2",
    "production_report": "60a5429398de75deda76cf6c2ea1ed53fb300ac952bf432baec2e83801f1cfd7",
}

STATUS = "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION"
PRODUCTION_STATUS = "PASS_LOSSLESS_SOURCE_SEPARATOR_PRESERVING_STA_ALIGNMENT"
CLAIM = (
    "This pass establishes a lossless common STA1 representation aligned to the source "
    "separator groups, plus an explicitly lossy nearest-basic-EVA convenience view. STA "
    "codes are transcription symbols, not proven physical letters, sounds, morphemes, "
    "words, meanings, plaintext, language, or translation."
)

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

FIELDS = [
    "source_group_id", "edition", "locus", "source_group_index",
    "source_group_count", "left_separator", "right_separator",
    "sta_group_raw", "primary_sta_codes", "primary_sta_families",
    "primary_sta_symbol_count", "alternative_site_count",
    "nearest_basic_eva_primary",
]

BOUNDARY_NAME = {
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "<->": "DRAWING_INTERRUPTION",
    "<~>": "DRAWING_INTERRUPTION_UNALIGNED",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, counter: list[int]) -> None:
    if not condition:
        raise RuntimeError(message)
    counter[0] += 1


def read_rules(path: Path) -> dict[str, str]:
    rules: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        pieces = raw.split()
        if len(pieces) != 2 or re.fullmatch(r"[A-Z][0-9a-z]", pieces[0]) is None:
            continue
        if pieces[0] in rules:
            raise RuntimeError(f"duplicate rule {pieces[0]}")
        rules[pieces[0]] = pieces[1]
    if not rules:
        raise RuntimeError("empty rules")
    return rules


def read_loci(path: Path) -> dict[str, tuple[str, str]]:
    output: dict[str, tuple[str, str]] = {}
    pattern = re.compile(r"^<([^,]+),([^>]*)>\s*(?:<![^>]*>)?\s*(.*)$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(raw)
        if not match:
            continue
        locus, code, body = match.groups()
        if locus in output:
            raise RuntimeError(f"duplicate locus {locus}")
        output[locus] = (code, body)
    return output


def groups_and_boundaries(body: str) -> tuple[list[str], list[str]]:
    """Independent character scanner for IVTFF source separators."""
    groups: list[str] = []
    boundaries: list[str] = []
    buffer: list[str] = []
    pending: str | None = None
    cursor = 0

    def finish(marker: str | None) -> None:
        nonlocal buffer, pending
        value = "".join(buffer).strip()
        buffer = []
        if value:
            if groups:
                if pending is None:
                    raise RuntimeError("missing separator")
                boundaries.append(pending)
            groups.append(value)
            pending = None
        if marker is not None:
            if pending is not None:
                raise RuntimeError("compound separator")
            pending = marker

    while cursor < len(body):
        marker = None
        if body.startswith("<->", cursor) or body.startswith("<~>", cursor):
            marker = body[cursor:cursor + 3]
        if marker is not None:
            finish(marker)
            cursor += 3
            continue
        char = body[cursor]
        if char == "<":
            end = body.find(">", cursor + 1)
            if end < 0:
                raise RuntimeError("unclosed angle tag")
            tag = body[cursor:end + 1]
            if tag not in ("<%>", "<$>"):
                buffer.append(tag)
            cursor = end + 1
            continue
        if char in "[{":
            end = body.find("]" if char == "[" else "}", cursor + 1)
            if end < 0:
                raise RuntimeError("unclosed bracket")
            buffer.append(body[cursor:end + 1])
            cursor = end + 1
            continue
        if char in ".,":
            finish(char)
            cursor += 1
            continue
        buffer.append(char)
        cursor += 1
    finish(None)
    if pending is not None or not groups or len(boundaries) + 1 != len(groups):
        raise RuntimeError("invalid group topology")
    return groups, boundaries


def code_sequence(value: str) -> list[str]:
    if not value:
        return []
    if len(value) % 2:
        raise RuntimeError("odd STA sequence")
    result = [value[index:index + 2] for index in range(0, len(value), 2)]
    if any(re.fullmatch(r"[A-Z][0-9a-z]", code) is None for code in result):
        raise RuntimeError("invalid STA symbol")
    return result


def decode_group(raw: str) -> tuple[list[str], int, set[str]]:
    primary: list[str] = []
    all_codes: set[str] = set()
    sites = 0
    cursor = 0
    while cursor < len(raw):
        if raw[cursor] == "<":
            end = raw.find(">", cursor + 1)
            if end < 0:
                raise RuntimeError("unclosed group tag")
            cursor = end + 1
            continue
        if raw[cursor] == "[":
            end = raw.find("]", cursor + 1)
            if end < 0:
                raise RuntimeError("unclosed alternative")
            options = raw[cursor + 1:end].split(":")
            if len(options) < 2:
                raise RuntimeError("single-path alternative")
            parsed = [code_sequence(option) for option in options]
            primary.extend(parsed[0])
            all_codes.update(code for option in parsed for code in option)
            sites += 1
            cursor = end + 1
            continue
        if raw[cursor] in "]:":
            raise RuntimeError("stray markup")
        code = raw[cursor:cursor + 2]
        if re.fullmatch(r"[A-Z][0-9a-z]", code) is None:
            raise RuntimeError("invalid STA code")
        primary.append(code)
        all_codes.add(code)
        cursor += 2
    return primary, sites, all_codes


def reverse_group(raw: str, rules: dict[str, str]) -> str:
    result: list[str] = []
    cursor = 0
    while cursor < len(raw):
        if raw[cursor] == "<":
            end = raw.find(">", cursor + 1)
            if end < 0:
                raise RuntimeError("unclosed tag")
            result.append(raw[cursor:end + 1])
            cursor = end + 1
            continue
        if raw[cursor] in "[]:":
            result.append(raw[cursor])
            cursor += 1
            continue
        code = raw[cursor:cursor + 2]
        if code not in rules:
            raise RuntimeError(f"unmapped code {code}")
        result.append(rules[code])
        cursor += 2
    return "".join(result)


def write_atomic(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> None:
    checks = [0]
    paths = {
        "spec": SPEC,
        "producer": PRODUCER,
        "crosswalk": CROSSWALK,
        "native_IT2a": NATIVE["IT2a"],
        "native_ZL3b": NATIVE["ZL3b"],
        "native_RF1b": NATIVE["RF1b"],
        "sta_IT2a": STA["IT2a"],
        "sta_ZL3b": STA["ZL3b"],
        "sta_RF1b": STA["RF1b"],
        "rule_exact_Eva": EXACT_RULE_PATH["ZL3b"],
        "rule_exact_EvaT": EXACT_RULE_PATH["IT2a"],
        "rule_basic": BASIC_RULE_PATH,
        "production_tsv": PRODUCTION_TSV,
        "production_json": PRODUCTION_JSON,
        "production_report": PRODUCTION_REPORT,
    }
    actual_hashes = {name: digest(path) for name, path in paths.items()}
    require(actual_hashes == EXPECTED_HASHES, "frozen hash mismatch", checks)

    exact = {edition: read_rules(path) for edition, path in EXACT_RULE_PATH.items()}
    basic = read_rules(BASIC_RULE_PATH)
    with CROSSWALK.open(encoding="utf-8", newline="") as handle:
        crosswalk_rows = list(csv.DictReader(handle, delimiter="\t"))
    crosswalk = {row["source_group_id"]: row for row in crosswalk_rows}
    require(len(crosswalk) == len(crosswalk_rows), "duplicate crosswalk IDs", checks)

    reconstructed: dict[str, dict[str, str]] = {}
    edition_counts = {edition: Counter() for edition in NATIVE}
    separators = Counter()
    all_codes: set[str] = set()
    all_families: set[str] = set()

    for edition in NATIVE:
        native = read_loci(NATIVE[edition])
        sta = read_loci(STA[edition])
        require(list(native) == list(sta), f"locus order mismatch {edition}", checks)
        for locus in native:
            native_code, native_body = native[locus]
            sta_code, sta_body = sta[locus]
            require(native_code == sta_code, f"locus code mismatch {edition}|{locus}", checks)
            ngroups, nboundaries = groups_and_boundaries(native_body)
            sgroups, sboundaries = groups_and_boundaries(sta_body)
            require(nboundaries == sboundaries, f"separator mismatch {edition}|{locus}", checks)
            require(len(ngroups) == len(sgroups), f"group count mismatch {edition}|{locus}", checks)
            rebuilt = "".join(
                ((sboundaries[index - 1] if index else "") + reverse_group(group, exact[edition]))
                for index, group in enumerate(sgroups)
            )
            native_clean = re.sub(r"<![^>]*>", "", native_body).replace("<%>", "").replace("<$>", "")
            require(rebuilt == native_clean, f"row reverse mismatch {edition}|{locus}", checks)
            edition_counts[edition]["loci"] += 1
            edition_counts[edition]["groups"] += len(sgroups)
            edition_counts[edition]["boundaries"] += len(sboundaries)
            for boundary in sboundaries:
                separators[BOUNDARY_NAME[boundary]] += 1

            for number, (native_group, sta_group) in enumerate(zip(ngroups, sgroups), 1):
                identifier = f"{edition}|{locus}|G{number:03d}"
                require(identifier in crosswalk, f"missing crosswalk {identifier}", checks)
                source = crosswalk[identifier]
                left = "LINE_START" if number == 1 else BOUNDARY_NAME[sboundaries[number - 2]]
                right = "LINE_END" if number == len(sgroups) else BOUNDARY_NAME[sboundaries[number - 1]]
                require(source["edition"] == edition, f"edition mismatch {identifier}", checks)
                require(source["locus"] == locus, f"locus mismatch {identifier}", checks)
                require(int(source["source_group_index"]) == number, f"index mismatch {identifier}", checks)
                require(int(source["source_group_count"]) == len(sgroups), f"count mismatch {identifier}", checks)
                require(source["left_separator"] == left, f"left mismatch {identifier}", checks)
                require(source["right_separator"] == right, f"right mismatch {identifier}", checks)
                require(source["ivtff_group_raw"] == native_group, f"native group mismatch {identifier}", checks)
                native_clean_group = re.sub(r"<![^>]*>", "", native_group)
                require(reverse_group(sta_group, exact[edition]) == native_clean_group, f"group reverse mismatch {identifier}", checks)
                primary, sites, group_codes = decode_group(sta_group)
                require(group_codes <= exact[edition].keys(), f"exact rule gap {identifier}", checks)
                require(group_codes <= basic.keys(), f"basic rule gap {identifier}", checks)
                all_codes.update(group_codes)
                all_families.update(code[0] for code in group_codes)
                edition_counts[edition]["primary_symbols"] += len(primary)
                edition_counts[edition]["alternative_sites"] += sites
                edition_counts[edition]["groups_with_alternatives"] += int(sites > 0)
                reconstructed[identifier] = {
                    "source_group_id": identifier,
                    "edition": edition,
                    "locus": locus,
                    "source_group_index": str(number),
                    "source_group_count": str(len(sgroups)),
                    "left_separator": left,
                    "right_separator": right,
                    "sta_group_raw": sta_group,
                    "primary_sta_codes": " ".join(primary),
                    "primary_sta_families": "".join(code[0] for code in primary),
                    "primary_sta_symbol_count": str(len(primary)),
                    "alternative_site_count": str(sites),
                    "nearest_basic_eva_primary": "".join(basic[code] for code in primary),
                }

    require(set(reconstructed) == set(crosswalk), "crosswalk set mismatch", checks)
    with PRODUCTION_TSV.open(encoding="utf-8", newline="") as handle:
        stored_rows = list(csv.DictReader(handle, delimiter="\t"))
        require(handle.seek(0) == 0, "seek failure", checks)
    require(list(stored_rows[0]) == FIELDS, "TSV field order mismatch", checks)
    require(len(stored_rows) == len(crosswalk_rows), "TSV row count mismatch", checks)
    for index, (source, stored) in enumerate(zip(crosswalk_rows, stored_rows)):
        expected = reconstructed[source["source_group_id"]]
        require(stored["source_group_id"] == source["source_group_id"], f"TSV order mismatch {index}", checks)
        for field in FIELDS:
            require(stored[field] == expected[field], f"TSV mismatch {expected['source_group_id']} {field}", checks)

    observed_input_hashes = {
        "spec": actual_hashes["spec"],
        "source_atlas": actual_hashes["crosswalk"],
        "native_IT2a": actual_hashes["native_IT2a"],
        "native_ZL3b": actual_hashes["native_ZL3b"],
        "native_RF1b": actual_hashes["native_RF1b"],
        "sta_IT2a": actual_hashes["sta_IT2a"],
        "sta_ZL3b": actual_hashes["sta_ZL3b"],
        "sta_RF1b": actual_hashes["sta_RF1b"],
        "rule_exact_Eva": actual_hashes["rule_exact_Eva"],
        "rule_exact_EvaT": actual_hashes["rule_exact_EvaT"],
        "rule_basic": actual_hashes["rule_basic"],
    }
    input_path_names = {
        "spec": "experiments/semantic_assumptions/SOURCE_STA_ALIGNMENT_SPEC.md",
        "source_atlas": "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
        "native_IT2a": "transcription/sources/IT2a-n.txt",
        "native_ZL3b": "transcription/sources/ZL3b-n.txt",
        "native_RF1b": "transcription/sources/RF1b-e.txt",
        "sta_IT2a": "transcription/sources/sta/IT2a.txt",
        "sta_ZL3b": "transcription/sources/sta/ZL3b.txt",
        "sta_RF1b": "transcription/sources/sta/RF1b.txt",
        "rule_exact_Eva": "transcription/sources/sta/STA-Eva_def.bit",
        "rule_exact_EvaT": "transcription/sources/sta/STA-EvaT_def.bit",
        "rule_basic": "transcription/sources/sta/STA-Eva_Bint.bit",
    }
    expected_summary = {
        "status": PRODUCTION_STATUS,
        "claim_ceiling": CLAIM,
        "official_sources": OFFICIAL_URLS,
        "inputs": {
            name: {"path": input_path_names[name], "sha256": value}
            for name, value in observed_input_hashes.items()
        },
        "counts": {
            "editions": 3,
            "reading_rows": sum(count["loci"] for count in edition_counts.values()),
            "source_groups": len(reconstructed),
            "source_boundaries": sum(count["boundaries"] for count in edition_counts.values()),
            "primary_sta_symbols": sum(count["primary_symbols"] for count in edition_counts.values()),
            "observed_sta_codes_all_paths": len(all_codes),
            "observed_sta_families_all_paths": len(all_families),
            "alternative_sites": sum(count["alternative_sites"] for count in edition_counts.values()),
            "groups_with_alternatives": sum(count["groups_with_alternatives"] for count in edition_counts.values()),
            "native_sta_locus_key_mismatches": 0,
            "native_sta_locus_code_mismatches": 0,
            "native_sta_topology_mismatches": 0,
            "native_sta_reverse_row_mismatches": 0,
            "native_sta_reverse_group_mismatches": 0,
            "unmapped_observed_sta_codes": 0,
            "source_group_crosswalk_mismatches": 0,
        },
        "by_edition": {
            edition: dict(sorted(count.items()))
            for edition, count in edition_counts.items()
        },
        "separator_counts": dict(sorted(separators.items())),
        "observed_sta_codes_all_paths": sorted(all_codes),
        "observed_sta_families_all_paths": sorted(all_families),
        "output": {
            "path": "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
            "rows": len(reconstructed),
            "sha256": actual_hashes["production_tsv"],
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
    stored_summary = json.loads(PRODUCTION_JSON.read_text(encoding="utf-8"))
    require(stored_summary == expected_summary, "production JSON mismatch", checks)

    c = expected_summary["counts"]
    expected_report = f"""# Source-preserving STA alignment

Status: **{PRODUCTION_STATUS}**

The official STA1 level-0 files align exactly to all **{c['reading_rows']:,}**
native reading rows, **{c['source_groups']:,}** source groups, and
**{c['source_boundaries']:,}** source separators. Applying the official
edition-specific bidirectional rules reconstructs every native row and group exactly
after removing only the inline comments that the STA release declares omitted.

The aligned primary paths contain **{c['primary_sta_symbols']:,}** STA
symbols. Across every supplied alternative, **{c['observed_sta_codes_all_paths']}**
codes in **{c['observed_sta_families_all_paths']}** families occur; all are
covered by both the exact reverse rules and the explicitly lossy nearest-basic-EVA
rules. ZL3b contains **{c['alternative_sites']}** marked alternative
sites across **{c['groups_with_alternatives']}** groups; the raw markup
retains every option.

This repairs the common character layer without inventing rare-glyph expansions or
boundaries. STA codes remain transcription symbols, not proven letters, sounds,
morphemes, words, meanings, plaintext, language, or translation.
"""
    require(PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report, "production report mismatch", checks)

    # Independent parser mutation/edge controls.
    require(code_sequence("") == [], "empty alternative control", checks)
    require(decode_group("A1[:A2]B1")[0] == ["A1", "B1"], "empty-first alternative control", checks)
    require(reverse_group("AaB1", exact["RF1b"]) == "@221;d", "extended-entity continuity control", checks)
    for malformed in ("A", "a1", "A1["):
        rejected = False
        try:
            decode_group(malformed)
        except RuntimeError:
            rejected = True
        require(rejected, f"malformed control accepted {malformed}", checks)

    validation = {
        "status": STATUS,
        "checks": checks[0],
        "discrepancies": 0,
        "validator": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": digest(Path(__file__).resolve()),
            "imports_production_module": False,
        },
        "validated_production": {
            "producer_sha256": actual_hashes["producer"],
            "tsv_sha256": actual_hashes["production_tsv"],
            "json_sha256": actual_hashes["production_json"],
            "report_sha256": actual_hashes["production_report"],
        },
        "reconstructed_counts": expected_summary["counts"],
        "gates": {
            "all_frozen_hashes_match": True,
            "all_native_sta_locus_codes_and_topologies_match": True,
            "all_native_rows_and_groups_reverse_exactly": True,
            "all_115470_tsv_rows_reconstructed_exactly": True,
            "complete_json_and_report_reconstructed_exactly": True,
            "empty_alternative_and_extended_entity_controls_pass": True,
            "malformed_sta_controls_reject": True,
            "zero_semantic_assignments": True,
        },
        "claim_ceiling": CLAIM,
    }
    write_atomic(VALIDATION_JSON, json.dumps(validation, indent=2, sort_keys=True) + "\n")
    report = f"""# Source-preserving STA alignment — independent validation

Status: **{STATUS}**

A nonimporting implementation reconstructed all **{c['source_groups']:,}** group
rows, **{c['reading_rows']:,}** native/STA row reversals, the complete production
JSON, and the exact report in **{checks[0]:,}** checks with zero discrepancies.
Empty alternatives, extended entities, and malformed-code controls also behaved as
required.

This validates transcription normalization only. It supplies no physical-letter,
sound, morpheme, word, meaning, plaintext, language, or translation claim.
"""
    write_atomic(VALIDATION_REPORT, report)


if __name__ == "__main__":
    main()
