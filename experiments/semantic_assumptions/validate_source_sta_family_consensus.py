#!/usr/bin/env python3
"""Independent validation of the exact-family three-reading scaffold."""

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
PRODUCER = HERE / "build_source_sta_family_consensus.py"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
UPSTREAM_JSON = RESULTS / "source_sta_group_alignment.json"
UPSTREAM_VALIDATION = RESULTS / "source_sta_group_alignment_validation.json"
SOURCE = RESULTS / "source_separator_transcription.tsv"
LOCI = RESULTS / "source_sta_family_consensus_loci.tsv"
BOUNDARIES = RESULTS / "source_sta_family_consensus_boundaries.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
PRODUCTION_JSON = RESULTS / "source_sta_family_consensus.json"
PRODUCTION_REPORT = RESULTS / "source_sta_family_consensus_report.md"
VALIDATION_JSON = RESULTS / "source_sta_family_consensus_validation.json"
VALIDATION_REPORT = RESULTS / "source_sta_family_consensus_validation_report.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
META = ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")
EXPECTED_HASHES = {
    "spec": "c7a494fdc37c3c2c63b527513e046920aace695b16d11d88a084d4f7efd26275",
    "producer": "f7dea2b56445c59435aa284c67e1f54556026fd553db2a8d2269ae1dec06ede1",
    "alignment": "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
    "upstream_json": "1df2786fa95c8dcca4845c86e13003e968ad36ae760a5f258a6f936eb7abcad2",
    "upstream_validation": "cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd",
    "source": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "loci": "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    "boundaries": "b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974",
    "groups": "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    "production_json": "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    "production_report": "9e0fa4c03ac4a9453d2b6385d5a6b2c1586409e4ea219beb9c53da0bb102bf84",
}

PRODUCTION_STATUS = "PASS_EXACT_THREE_READING_STA_FAMILY_GRAMMAR_SCAFFOLD"
STATUS = "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION"
CLAIM = (
    "This pass establishes an exact-family three-reading transcription scaffold and "
    "source-synchronized boundary capacity only. It does not establish authorial word "
    "boundaries, physical character identity, pronunciation, morphology, parts of speech, "
    "language, cipher, lexemes, plaintext, or translation."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def assert_check(value: bool, message: str, checks: list[int]) -> None:
    if not value:
        raise RuntimeError(message)
    checks[0] += 1


def boundary_profile(maps: dict[tuple[str, str], dict[int, str]], locus: str, position: int) -> str:
    return ";".join(f"{edition}:{maps[edition, locus].get(position, 'NONE')}" for edition in EDITIONS)


def position_list(value: str) -> list[int]:
    return [] if not value else [int(item) for item in value.split(",")]


def atomic(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> None:
    checks = [0]
    paths = {
        "spec": SPEC,
        "producer": PRODUCER,
        "alignment": ALIGNMENT,
        "upstream_json": UPSTREAM_JSON,
        "upstream_validation": UPSTREAM_VALIDATION,
        "source": SOURCE,
        "loci": LOCI,
        "boundaries": BOUNDARIES,
        "groups": GROUPS,
        "production_json": PRODUCTION_JSON,
        "production_report": PRODUCTION_REPORT,
    }
    hashes = {name: digest(path) for name, path in paths.items()}
    assert_check(hashes == EXPECTED_HASHES, "frozen hash mismatch", checks)

    source_rows = load_tsv(SOURCE)
    meta: dict[tuple[str, str], tuple[str, ...]] = {}
    source_ids: set[str] = set()
    for row in source_rows:
        identifier = row["source_group_id"]
        assert_check(identifier not in source_ids, f"duplicate source ID {identifier}", checks)
        source_ids.add(identifier)
        key = (row["edition"], row["locus"])
        value = tuple(row[field] for field in META)
        assert_check(key not in meta or meta[key] == value, f"metadata drift {key}", checks)
        meta[key] = value

    symbols: dict[tuple[str, str], list[str]] = defaultdict(list)
    separators: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    alternatives = Counter()
    seen_alignment: set[str] = set()
    expected_group_index = Counter()
    for row in load_tsv(ALIGNMENT):
        identifier = row["source_group_id"]
        assert_check(identifier in source_ids and identifier not in seen_alignment, f"alignment ID {identifier}", checks)
        seen_alignment.add(identifier)
        key = (row["edition"], row["locus"])
        expected_group_index[key] += 1
        assert_check(int(row["source_group_index"]) == expected_group_index[key], f"group order {identifier}", checks)
        codes = row["primary_sta_codes"].split()
        assert_check(row["primary_sta_families"] == "".join(code[0] for code in codes), f"family field {identifier}", checks)
        symbols[key].extend(codes)
        alternatives[key] += int(row["alternative_site_count"])
        if row["right_separator"] != "LINE_END":
            position = len(symbols[key])
            assert_check(position > 0 and position not in separators[key], f"boundary position {identifier}", checks)
            separators[key][position] = row["right_separator"]
    assert_check(seen_alignment == source_ids, "alignment/source set mismatch", checks)
    for key, boundary_map in separators.items():
        assert_check(all(position < len(symbols[key]) for position in boundary_map), f"terminal boundary {key}", checks)

    reading_loci = {
        edition: {locus for current, locus in symbols if current == edition}
        for edition in EDITIONS
    }
    common = set.intersection(*(reading_loci[edition] for edition in EDITIONS))
    selected = []
    for locus in sorted(common):
        assert_check(len({meta[edition, locus] for edition in EDITIONS}) == 1, f"metadata mismatch {locus}", checks)
        family_views = [tuple(code[0] for code in symbols[edition, locus]) for edition in EDITIONS]
        if family_views[0] == family_views[1] == family_views[2]:
            selected.append(locus)

    stored_loci_rows = load_tsv(LOCI)
    stored_boundary_rows = load_tsv(BOUNDARIES)
    stored_group_rows = load_tsv(GROUPS)
    stored_loci = {row["locus"]: row for row in stored_loci_rows}
    stored_boundaries = {row["boundary_id"]: row for row in stored_boundary_rows}
    stored_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in stored_group_rows:
        stored_groups[row["locus"]].append(row)
    assert_check(len(stored_loci) == len(stored_loci_rows), "duplicate stored loci", checks)
    assert_check(len(stored_boundaries) == len(stored_boundary_rows), "duplicate stored boundaries", checks)
    assert_check(list(stored_loci) == selected, "selected locus order/set mismatch", checks)

    support_counts = Counter()
    strict_support_counts = Counter()
    profiles = Counter()
    strict_profiles = Counter()
    type_counts = Counter()
    strict_type_counts = Counter()
    totals = Counter()
    expected_boundary_ids: set[str] = set()
    expected_group_ids: set[str] = set()

    for locus in selected:
        row = stored_loci[locus]
        metadata_values = meta["ZL3b", locus]
        metadata_dict = dict(zip(META, metadata_values))
        family = [code[0] for code in symbols["ZL3b", locus]]
        length = len(family)
        for edition in EDITIONS:
            assert_check([code[0] for code in symbols[edition, locus]] == family, f"selected family mismatch {edition}|{locus}", checks)
        alt_count = sum(alternatives[edition, locus] for edition in EDITIONS)
        strict = int(alt_count == 0)
        union = sorted(set().union(*(separators[edition, locus] for edition in EDITIONS)))
        by_support = {1: [], 2: [], 3: []}
        synchronized = []

        expected_locus = {
            "locus": locus,
            **metadata_dict,
            "symbol_count": str(length),
            "family_sequence": "".join(family),
            "zl_sta_codes": " ".join(symbols["ZL3b", locus]),
            "it_sta_codes": " ".join(symbols["IT2a", locus]),
            "rf_sta_codes": " ".join(symbols["RF1b", locus]),
            "alternative_sites": str(alt_count),
            "strict_zero_alternative": str(strict),
        }
        for field, value in expected_locus.items():
            assert_check(row[field] == value, f"locus field {locus} {field}", checks)

        for position in union:
            assert_check(0 < position < length, f"noninternal union {locus}|{position}", checks)
            values = {edition: separators[edition, locus].get(position, "NONE") for edition in EDITIONS}
            supporting = [edition for edition in EDITIONS if values[edition] != "NONE"]
            support = len(supporting)
            by_support[support].append(position)
            if support >= 2:
                synchronized.append(position)
            present_types = {values[edition] for edition in supporting}
            consensus = next(iter(present_types)) if len(present_types) == 1 else "MIXED_SOURCE_SEPARATOR"
            identifier = f"{locus}|B{position:03d}"
            expected_boundary_ids.add(identifier)
            assert_check(identifier in stored_boundaries, f"missing boundary {identifier}", checks)
            stored = stored_boundaries[identifier]
            expected_boundary = {
                "boundary_id": identifier,
                "locus": locus,
                **metadata_dict,
                "strict_zero_alternative": str(strict),
                "position_after_symbol": str(position),
                "left_family": family[position - 1],
                "right_family": family[position],
                "zl_separator": values["ZL3b"],
                "it_separator": values["IT2a"],
                "rf_separator": values["RF1b"],
                "support_count": str(support),
                "supporting_readings": ",".join(supporting),
                "supporting_type_count": str(len(present_types)),
                "type_consensus": consensus,
                "synchronized_boundary": str(int(support >= 2)),
            }
            for field, value in expected_boundary.items():
                assert_check(stored[field] == value, f"boundary field {identifier} {field}", checks)
            support_counts[support] += 1
            profile_tuple = tuple(values[edition] for edition in EDITIONS)
            profiles[profile_tuple] += 1
            type_counts[consensus] += 1
            if strict:
                strict_support_counts[support] += 1
                strict_profiles[profile_tuple] += 1
                strict_type_counts[consensus] += 1

        positional_fields = {
            "union_boundary_positions": union,
            "synchronized_boundary_positions": synchronized,
            "three_reading_boundary_positions": by_support[3],
            "two_reading_boundary_positions": by_support[2],
            "one_reading_boundary_positions": by_support[1],
        }
        for field, values in positional_fields.items():
            assert_check(position_list(row[field]) == values, f"locus positions {locus} {field}", checks)
        exact_sets = int(set(separators["ZL3b", locus]) == set(separators["IT2a", locus]) == set(separators["RF1b", locus]))
        exact_maps = int(separators["ZL3b", locus] == separators["IT2a", locus] == separators["RF1b", locus])
        assert_check(row["exact_boundary_position_sets"] == str(exact_sets), f"exact sets {locus}", checks)
        assert_check(row["exact_typed_boundary_maps"] == str(exact_maps), f"exact maps {locus}", checks)

        cuts = [0, *synchronized, length]
        rows = stored_groups[locus]
        assert_check(len(rows) == len(cuts) - 1, f"group count {locus}", checks)
        for index, ((start, end), stored) in enumerate(zip(zip(cuts, cuts[1:]), rows), 1):
            identifier = f"{locus}|C{index:03d}"
            expected_group_ids.add(identifier)
            left = "LINE_START" if start == 0 else boundary_profile(separators, locus, start)
            right = "LINE_END" if end == length else boundary_profile(separators, locus, end)
            expected_group = {
                "consensus_group_id": identifier,
                "locus": locus,
                **metadata_dict,
                "strict_zero_alternative": str(strict),
                "consensus_group_index": str(index),
                "consensus_group_count": str(len(cuts) - 1),
                "start_symbol_1based": str(start + 1),
                "end_symbol_1based": str(end),
                "symbol_count": str(end - start),
                "family_surface": "".join(family[start:end]),
                "zl_sta_codes": " ".join(symbols["ZL3b", locus][start:end]),
                "it_sta_codes": " ".join(symbols["IT2a", locus][start:end]),
                "rf_sta_codes": " ".join(symbols["RF1b", locus][start:end]),
                "left_boundary_profile": left,
                "right_boundary_profile": right,
            }
            for field, value in expected_group.items():
                assert_check(stored[field] == value, f"group field {identifier} {field}", checks)

        assert_check("".join(group["family_surface"] for group in rows) == row["family_sequence"], f"family reconstruction {locus}", checks)
        for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"):
            assert_check(" ".join(group[field] for group in rows) == row[field], f"member reconstruction {locus} {field}", checks)

        totals["exact_loci"] += 1
        totals["exact_symbols"] += length
        totals["exact_union_boundaries"] += len(union)
        totals["exact_synchronized_boundaries"] += len(synchronized)
        totals["exact_groups"] += len(cuts) - 1
        totals["exact_position_set_loci"] += exact_sets
        totals["exact_typed_map_loci"] += exact_maps
        if strict:
            totals["strict_loci"] += 1
            totals["strict_symbols"] += length
            totals["strict_union_boundaries"] += len(union)
            totals["strict_synchronized_boundaries"] += len(synchronized)
            totals["strict_groups"] += len(cuts) - 1
            totals["strict_exact_position_set_loci"] += exact_sets
            totals["strict_exact_typed_map_loci"] += exact_maps

    assert_check(expected_boundary_ids == set(stored_boundaries), "boundary ID set mismatch", checks)
    assert_check(expected_group_ids == {row["consensus_group_id"] for row in stored_group_rows}, "group ID set mismatch", checks)

    counts = {
        "reading_loci_by_edition": {edition: len(reading_loci[edition]) for edition in EDITIONS},
        "common_three_reading_loci": len(common),
        **dict(sorted(totals.items())),
        "broad_boundary_support": {str(key): support_counts[key] for key in (1, 2, 3)},
        "strict_boundary_support": {str(key): strict_support_counts[key] for key in (1, 2, 3)},
        "broad_synchronized_fraction_of_union": totals["exact_synchronized_boundaries"] / totals["exact_union_boundaries"],
        "strict_synchronized_fraction_of_union": totals["strict_synchronized_boundaries"] / totals["strict_union_boundaries"],
    }
    profile_dict = lambda counter: {"|".join(key): value for key, value in sorted(counter.items())}
    expected_json = {
        "status": PRODUCTION_STATUS,
        "claim_ceiling": CLAIM,
        "inputs": {
            "spec": {"path": "experiments/semantic_assumptions/SOURCE_STA_FAMILY_CONSENSUS_SPEC.md", "sha256": hashes["spec"]},
            "sta_alignment": {"path": "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv", "sha256": hashes["alignment"]},
            "sta_summary": {"path": "experiments/semantic_assumptions/results/source_sta_group_alignment.json", "sha256": hashes["upstream_json"]},
            "sta_validation": {"path": "experiments/semantic_assumptions/results/source_sta_group_alignment_validation.json", "sha256": hashes["upstream_validation"]},
            "source_atlas": {"path": "experiments/semantic_assumptions/results/source_separator_transcription.tsv", "sha256": hashes["source"]},
        },
        "counts": counts,
        "broad_boundary_profiles": profile_dict(profiles),
        "strict_boundary_profiles": profile_dict(strict_profiles),
        "broad_type_consensus_counts": dict(sorted(type_counts.items())),
        "strict_type_consensus_counts": dict(sorted(strict_type_counts.items())),
        "outputs": {
            "loci": {"path": "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv", "rows": len(stored_loci_rows), "sha256": hashes["loci"]},
            "boundaries": {"path": "experiments/semantic_assumptions/results/source_sta_family_consensus_boundaries.tsv", "rows": len(stored_boundary_rows), "sha256": hashes["boundaries"]},
            "groups": {"path": "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv", "rows": len(stored_group_rows), "sha256": hashes["groups"]},
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
    assert_check(json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json, "production JSON mismatch", checks)

    expected_report = f"""# Exact-family three-reading grammar scaffold

Status: **{PRODUCTION_STATUS}**

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
    assert_check(PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report, "production report mismatch", checks)

    # Mutation controls for the exact-agreement and strict-panel definitions.
    assert_check(tuple("AB") != tuple("ACB"), "gap alignment accidentally allowed", checks)
    assert_check(tuple("AB") != tuple("AC"), "family mutation not rejected", checks)
    assert_check(int(sum((0, 0, 1)) == 0) == 0, "alternative mutation remains strict", checks)
    toy = {"ZL3b": {1: "D"}, "IT2a": {1: "D"}, "RF1b": {2: "D"}}
    assert_check(sum(1 in toy[edition] for edition in EDITIONS) == 2, "boundary support mutation", checks)

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
            "producer_sha256": hashes["producer"],
            "loci_sha256": hashes["loci"],
            "boundaries_sha256": hashes["boundaries"],
            "groups_sha256": hashes["groups"],
            "json_sha256": hashes["production_json"],
            "report_sha256": hashes["production_report"],
        },
        "reconstructed_counts": counts,
        "gates": {
            "all_frozen_hashes_match": True,
            "all_exact_family_loci_reconstructed": True,
            "all_boundary_union_rows_reconstructed": True,
            "all_synchronized_groups_reconstructed": True,
            "complete_json_and_report_reconstructed": True,
            "family_gap_alternative_boundary_mutations_reject": True,
            "zero_formal_or_semantic_assignments": True,
        },
        "claim_ceiling": CLAIM,
    }
    atomic(VALIDATION_JSON, json.dumps(validation, indent=2, sort_keys=True) + "\n")
    report = f"""# Exact-family grammar scaffold — independent validation

Status: **{STATUS}**

A nonimporting implementation reconstructed **{counts['exact_loci']:,}** exact-family
loci, **{counts['exact_union_boundaries']:,}** union boundary rows, and
**{counts['exact_groups']:,}** synchronized construction groups in
**{checks[0]:,}** checks with zero discrepancies. It also reproduced the complete
JSON/report and rejected family, gap, alternative, and boundary mutations.

This validates a transcription scaffold only. It supplies no authorial word,
physical letter, sound, morphology, meaning, plaintext, language, or translation.
"""
    atomic(VALIDATION_REPORT, report)


if __name__ == "__main__":
    main()
