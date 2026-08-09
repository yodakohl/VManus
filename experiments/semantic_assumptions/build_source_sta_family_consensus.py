#!/usr/bin/env python3
"""Build an exact-family, three-reading source grammar scaffold."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SPEC = HERE / "SOURCE_STA_FAMILY_CONSENSUS_SPEC.md"
STA_ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
STA_SUMMARY = RESULTS / "source_sta_group_alignment.json"
STA_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
SOURCE_ATLAS = RESULTS / "source_separator_transcription.tsv"

OUTPUT_LOCI = RESULTS / "source_sta_family_consensus_loci.tsv"
OUTPUT_BOUNDARIES = RESULTS / "source_sta_family_consensus_boundaries.tsv"
OUTPUT_GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
OUTPUT_JSON = RESULTS / "source_sta_family_consensus.json"
OUTPUT_REPORT = RESULTS / "source_sta_family_consensus_report.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
EXPECTED_HASHES = {
    "spec": "c7a494fdc37c3c2c63b527513e046920aace695b16d11d88a084d4f7efd26275",
    "sta_alignment": "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    "sta_summary": "1df2786fa95c8dcca4845c86e13003e968ad36ae760a5f258a6f936eb7abcad2",
    "sta_validation": "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    "source_atlas": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
}

META_FIELDS = ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")
LOCUS_FIELDS = [
    "locus", *META_FIELDS, "symbol_count", "family_sequence",
    "zl_sta_codes", "it_sta_codes", "rf_sta_codes", "alternative_sites",
    "strict_zero_alternative", "union_boundary_positions",
    "synchronized_boundary_positions", "three_reading_boundary_positions",
    "two_reading_boundary_positions", "one_reading_boundary_positions",
    "exact_boundary_position_sets", "exact_typed_boundary_maps",
]
BOUNDARY_FIELDS = [
    "boundary_id", "locus", *META_FIELDS, "strict_zero_alternative",
    "position_after_symbol", "left_family", "right_family", "zl_separator",
    "it_separator", "rf_separator", "support_count", "supporting_readings",
    "supporting_type_count", "type_consensus", "synchronized_boundary",
]
GROUP_FIELDS = [
    "consensus_group_id", "locus", *META_FIELDS, "strict_zero_alternative",
    "consensus_group_index", "consensus_group_count", "start_symbol_1based",
    "end_symbol_1based", "symbol_count", "family_surface", "zl_sta_codes",
    "it_sta_codes", "rf_sta_codes", "left_boundary_profile",
    "right_boundary_profile",
]

STATUS = "PASS_EXACT_THREE_READING_STA_FAMILY_GRAMMAR_SCAFFOLD"
CLAIM = (
    "This pass establishes an exact-family three-reading transcription scaffold and "
    "source-synchronized boundary capacity only. It does not establish authorial word "
    "boundaries, physical character identity, pronunciation, morphology, parts of speech, "
    "language, cipher, lexemes, plaintext, or translation."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_paths() -> dict[str, Path]:
    return {
        "spec": SPEC,
        "sta_alignment": STA_ALIGNMENT,
        "sta_summary": STA_SUMMARY,
        "sta_validation": STA_VALIDATION,
        "source_atlas": SOURCE_ATLAS,
    }


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str | int]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def profile(boundary_maps: dict[str, dict[int, str]], locus: str, position: int) -> str:
    return ";".join(
        f"{edition}:{boundary_maps[edition, locus].get(position, 'NONE')}"
        for edition in EDITIONS
    )


def main() -> None:
    observed_hashes = {name: sha256(path) for name, path in input_paths().items()}
    if observed_hashes != EXPECTED_HASHES:
        raise RuntimeError("STA-family scaffold input drift")
    sta_summary = json.loads(STA_SUMMARY.read_text(encoding="utf-8"))
    sta_validation = json.loads(STA_VALIDATION.read_text(encoding="utf-8"))
    if sta_summary["status"] != "PASS_LOSSLESS_SOURCE_SEPARATOR_PRESERVING_STA_ALIGNMENT":
        raise RuntimeError("upstream STA alignment not passed")
    if sta_validation["status"] != "PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION":
        raise RuntimeError("upstream independent STA validation not passed")

    source_rows = csv_rows(SOURCE_ATLAS)
    metadata: dict[tuple[str, str], tuple[str, ...]] = {}
    source_ids: set[str] = set()
    for row in source_rows:
        identifier = row["source_group_id"]
        if identifier in source_ids:
            raise RuntimeError(f"duplicate source-group ID {identifier}")
        source_ids.add(identifier)
        key = (row["edition"], row["locus"])
        value = tuple(row[field] for field in META_FIELDS)
        if key in metadata and metadata[key] != value:
            raise RuntimeError(f"within-locus metadata drift {key}")
        metadata[key] = value

    codes: dict[tuple[str, str], list[str]] = defaultdict(list)
    boundary_maps: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    alternative_sites = Counter()
    group_indices: dict[tuple[str, str], list[int]] = defaultdict(list)
    sta_ids: set[str] = set()
    for row in csv_rows(STA_ALIGNMENT):
        identifier = row["source_group_id"]
        if identifier in sta_ids or identifier not in source_ids:
            raise RuntimeError(f"STA/source ID mismatch {identifier}")
        sta_ids.add(identifier)
        key = (row["edition"], row["locus"])
        group_index = int(row["source_group_index"])
        group_count = int(row["source_group_count"])
        group_indices[key].append(group_index)
        if group_index > group_count:
            raise RuntimeError(f"invalid group index {identifier}")
        member_codes = row["primary_sta_codes"].split()
        if any(len(code) != 2 or code[0] not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for code in member_codes):
            raise RuntimeError(f"invalid STA member code {identifier}")
        if row["primary_sta_families"] != "".join(code[0] for code in member_codes):
            raise RuntimeError(f"stored family mismatch {identifier}")
        codes[key].extend(member_codes)
        alternative_sites[key] += int(row["alternative_site_count"])
        if row["right_separator"] != "LINE_END":
            position = len(codes[key])
            if position <= 0 or position in boundary_maps[key]:
                raise RuntimeError(f"invalid boundary offset {identifier}")
            boundary_maps[key][position] = row["right_separator"]
    if sta_ids != source_ids:
        raise RuntimeError("STA/source group coverage mismatch")
    for key, indices in group_indices.items():
        if indices != list(range(1, len(indices) + 1)):
            raise RuntimeError(f"noncontiguous group indices {key}")
        length = len(codes[key])
        if not length or any(position >= length for position in boundary_maps[key]):
            raise RuntimeError(f"noninternal boundary {key}")

    locus_sets = {
        edition: {locus for current_edition, locus in codes if current_edition == edition}
        for edition in EDITIONS
    }
    common_loci = set.intersection(*(locus_sets[edition] for edition in EDITIONS))
    exact_loci: list[str] = []
    for locus in sorted(common_loci):
        meta = {metadata[edition, locus] for edition in EDITIONS}
        if len(meta) != 1:
            raise RuntimeError(f"cross-reading metadata mismatch {locus}")
        families = [tuple(code[0] for code in codes[edition, locus]) for edition in EDITIONS]
        if families[0] == families[1] == families[2]:
            exact_loci.append(locus)

    locus_rows: list[dict[str, str | int]] = []
    boundary_rows: list[dict[str, str | int]] = []
    group_rows: list[dict[str, str | int]] = []
    boundary_support = Counter()
    strict_boundary_support = Counter()
    boundary_profiles = Counter()
    strict_boundary_profiles = Counter()
    type_consensus_counts = Counter()
    strict_type_consensus_counts = Counter()
    panel_counts = Counter()

    for locus in exact_loci:
        meta_values = metadata["ZL3b", locus]
        meta = dict(zip(META_FIELDS, meta_values))
        edition_codes = {edition: codes[edition, locus] for edition in EDITIONS}
        families = [code[0] for code in edition_codes["ZL3b"]]
        length = len(families)
        if any(len(edition_codes[edition]) != length for edition in EDITIONS):
            raise RuntimeError(f"member sequence length mismatch {locus}")
        if any(
            [code[0] for code in edition_codes[edition]] != families
            for edition in EDITIONS
        ):
            raise RuntimeError(f"family mismatch after selection {locus}")
        alternatives = sum(alternative_sites[edition, locus] for edition in EDITIONS)
        strict = int(alternatives == 0)
        union_positions = sorted(set().union(*(boundary_maps[edition, locus] for edition in EDITIONS)))
        if any(position <= 0 or position >= length for position in union_positions):
            raise RuntimeError(f"noninternal union boundary {locus}")
        positions_by_support: dict[int, list[int]] = {1: [], 2: [], 3: []}
        synchronized: list[int] = []

        for position in union_positions:
            values = {
                edition: boundary_maps[edition, locus].get(position, "NONE")
                for edition in EDITIONS
            }
            supporting = [edition for edition in EDITIONS if values[edition] != "NONE"]
            support = len(supporting)
            if support not in {1, 2, 3}:
                raise RuntimeError(f"invalid support {locus}|{position}")
            positions_by_support[support].append(position)
            if support >= 2:
                synchronized.append(position)
            supporting_types = {values[edition] for edition in supporting}
            type_consensus = next(iter(supporting_types)) if len(supporting_types) == 1 else "MIXED_SOURCE_SEPARATOR"
            profile_value = tuple(values[edition] for edition in EDITIONS)
            boundary_support[support] += 1
            boundary_profiles[profile_value] += 1
            type_consensus_counts[type_consensus] += 1
            if strict:
                strict_boundary_support[support] += 1
                strict_boundary_profiles[profile_value] += 1
                strict_type_consensus_counts[type_consensus] += 1
            boundary_rows.append({
                "boundary_id": f"{locus}|B{position:03d}",
                "locus": locus,
                **meta,
                "strict_zero_alternative": strict,
                "position_after_symbol": position,
                "left_family": families[position - 1],
                "right_family": families[position],
                "zl_separator": values["ZL3b"],
                "it_separator": values["IT2a"],
                "rf_separator": values["RF1b"],
                "support_count": support,
                "supporting_readings": ",".join(supporting),
                "supporting_type_count": len(supporting_types),
                "type_consensus": type_consensus,
                "synchronized_boundary": int(support >= 2),
            })

        exact_position_sets = int(
            set(boundary_maps["ZL3b", locus])
            == set(boundary_maps["IT2a", locus])
            == set(boundary_maps["RF1b", locus])
        )
        exact_typed_maps = int(
            boundary_maps["ZL3b", locus]
            == boundary_maps["IT2a", locus]
            == boundary_maps["RF1b", locus]
        )
        locus_rows.append({
            "locus": locus,
            **meta,
            "symbol_count": length,
            "family_sequence": "".join(families),
            "zl_sta_codes": " ".join(edition_codes["ZL3b"]),
            "it_sta_codes": " ".join(edition_codes["IT2a"]),
            "rf_sta_codes": " ".join(edition_codes["RF1b"]),
            "alternative_sites": alternatives,
            "strict_zero_alternative": strict,
            "union_boundary_positions": ",".join(map(str, union_positions)),
            "synchronized_boundary_positions": ",".join(map(str, synchronized)),
            "three_reading_boundary_positions": ",".join(map(str, positions_by_support[3])),
            "two_reading_boundary_positions": ",".join(map(str, positions_by_support[2])),
            "one_reading_boundary_positions": ",".join(map(str, positions_by_support[1])),
            "exact_boundary_position_sets": exact_position_sets,
            "exact_typed_boundary_maps": exact_typed_maps,
        })

        cuts = [0, *synchronized, length]
        for index, (start, end) in enumerate(zip(cuts, cuts[1:]), 1):
            if end <= start:
                raise RuntimeError(f"empty synchronized group {locus}")
            left_profile = "LINE_START" if start == 0 else profile(boundary_maps, locus, start)
            right_profile = "LINE_END" if end == length else profile(boundary_maps, locus, end)
            group_rows.append({
                "consensus_group_id": f"{locus}|C{index:03d}",
                "locus": locus,
                **meta,
                "strict_zero_alternative": strict,
                "consensus_group_index": index,
                "consensus_group_count": len(cuts) - 1,
                "start_symbol_1based": start + 1,
                "end_symbol_1based": end,
                "symbol_count": end - start,
                "family_surface": "".join(families[start:end]),
                "zl_sta_codes": " ".join(edition_codes["ZL3b"][start:end]),
                "it_sta_codes": " ".join(edition_codes["IT2a"][start:end]),
                "rf_sta_codes": " ".join(edition_codes["RF1b"][start:end]),
                "left_boundary_profile": left_profile,
                "right_boundary_profile": right_profile,
            })

        panel_counts["exact_loci"] += 1
        panel_counts["exact_symbols"] += length
        panel_counts["exact_union_boundaries"] += len(union_positions)
        panel_counts["exact_synchronized_boundaries"] += len(synchronized)
        panel_counts["exact_groups"] += len(cuts) - 1
        panel_counts["exact_position_set_loci"] += exact_position_sets
        panel_counts["exact_typed_map_loci"] += exact_typed_maps
        if strict:
            panel_counts["strict_loci"] += 1
            panel_counts["strict_symbols"] += length
            panel_counts["strict_union_boundaries"] += len(union_positions)
            panel_counts["strict_synchronized_boundaries"] += len(synchronized)
            panel_counts["strict_groups"] += len(cuts) - 1
            panel_counts["strict_exact_position_set_loci"] += exact_position_sets
            panel_counts["strict_exact_typed_map_loci"] += exact_typed_maps

    if len(boundary_rows) != panel_counts["exact_union_boundaries"]:
        raise RuntimeError("boundary output count mismatch")
    if len(group_rows) != panel_counts["exact_groups"]:
        raise RuntimeError("group output count mismatch")

    # Reconstruction from synchronized groups must be exact for all three views.
    groups_by_locus: dict[str, list[dict[str, str | int]]] = defaultdict(list)
    for row in group_rows:
        groups_by_locus[str(row["locus"])].append(row)
    locus_index = {str(row["locus"]): row for row in locus_rows}
    for locus, rows in groups_by_locus.items():
        original = locus_index[locus]
        if "".join(str(row["family_surface"]) for row in rows) != original["family_sequence"]:
            raise RuntimeError(f"family group reconstruction failure {locus}")
        for edition, field in (("ZL3b", "zl_sta_codes"), ("IT2a", "it_sta_codes"), ("RF1b", "rf_sta_codes")):
            joined = " ".join(str(row[field]) for row in rows)
            if joined != original[field]:
                raise RuntimeError(f"member group reconstruction failure {edition}|{locus}")

    write_tsv(OUTPUT_LOCI, LOCUS_FIELDS, locus_rows)
    write_tsv(OUTPUT_BOUNDARIES, BOUNDARY_FIELDS, boundary_rows)
    write_tsv(OUTPUT_GROUPS, GROUP_FIELDS, group_rows)

    def string_profile(counter: Counter) -> dict[str, int]:
        return {
            "|".join(profile_values): count
            for profile_values, count in sorted(counter.items())
        }

    counts = {
        "reading_loci_by_edition": {edition: len(locus_sets[edition]) for edition in EDITIONS},
        "common_three_reading_loci": len(common_loci),
        **dict(sorted(panel_counts.items())),
        "broad_boundary_support": {str(key): boundary_support[key] for key in (1, 2, 3)},
        "strict_boundary_support": {str(key): strict_boundary_support[key] for key in (1, 2, 3)},
        "broad_synchronized_fraction_of_union": panel_counts["exact_synchronized_boundaries"] / panel_counts["exact_union_boundaries"],
        "strict_synchronized_fraction_of_union": panel_counts["strict_synchronized_boundaries"] / panel_counts["strict_union_boundaries"],
    }
    summary = {
        "status": STATUS,
        "claim_ceiling": CLAIM,
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": observed_hashes[name]}
            for name, path in input_paths().items()
        },
        "counts": counts,
        "broad_boundary_profiles": string_profile(boundary_profiles),
        "strict_boundary_profiles": string_profile(strict_boundary_profiles),
        "broad_type_consensus_counts": dict(sorted(type_consensus_counts.items())),
        "strict_type_consensus_counts": dict(sorted(strict_type_consensus_counts.items())),
        "outputs": {
            "loci": {"path": str(OUTPUT_LOCI.relative_to(ROOT)), "rows": len(locus_rows), "sha256": sha256(OUTPUT_LOCI)},
            "boundaries": {"path": str(OUTPUT_BOUNDARIES.relative_to(ROOT)), "rows": len(boundary_rows), "sha256": sha256(OUTPUT_BOUNDARIES)},
            "groups": {"path": str(OUTPUT_GROUPS.relative_to(ROOT)), "rows": len(group_rows), "sha256": sha256(OUTPUT_GROUPS)},
        },
        "gates": {
            "exact_input_hashes": True,
            "exact_three_reading_metadata": True,
            "no_dynamic_alignment_or_preferred_reading": True,
            "exact_family_sequence_selection": True,
            "all_boundary_offsets_internal": True,
            "all_member_families_equal": True,
            "all_synchronized_groups_reconstruct": True,
            "broad_and_strict_panels_separate": True,
            "zero_legacy_formal_or_semantic_fields": True,
        },
    }
    atomic_text(OUTPUT_JSON, json.dumps(summary, indent=2, sort_keys=True) + "\n")

    report = f"""# Exact-family three-reading grammar scaffold

Status: **{STATUS}**

Of **{counts['common_three_reading_loci']:,}** physical loci shared by ZL3b,
IT2a, and RF1b, **{counts['exact_loci']:,}** have an exactly identical complete
STA family sequence without any edit alignment. The primary strict panel removes
every bracketed alternative and retains **{counts['strict_loci']:,}** loci with
**{counts['strict_symbols']:,}** aligned family symbols.

In the broad panel, **{counts['exact_synchronized_boundaries']:,}** of
**{counts['exact_union_boundaries']:,}** union boundary positions
({counts['broad_synchronized_fraction_of_union']:.2%}) are supported by at least
two readings. In the strict panel, the corresponding count is
**{counts['strict_synchronized_boundaries']:,}** of
**{counts['strict_union_boundaries']:,}**
({counts['strict_synchronized_fraction_of_union']:.2%}). Exactly
**{counts['strict_boundary_support']['3']:,}** strict-panel positions occur in all
three readings, **{counts['strict_boundary_support']['2']:,}** in two, and
**{counts['strict_boundary_support']['1']:,}** in only one.

Splitting only at synchronized positions produces **{counts['strict_groups']:,}**
strict source-aware construction groups. They reconstruct every family and member
sequence exactly. This is the clean input for a new grammar reconstruction; it is
not evidence for authorial wordhood, sound, morphology, meaning, plaintext,
language, or translation.
"""
    atomic_text(OUTPUT_REPORT, report)


if __name__ == "__main__":
    main()
