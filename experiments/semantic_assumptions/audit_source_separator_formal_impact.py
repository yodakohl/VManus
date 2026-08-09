#!/usr/bin/env python3
"""Audit legacy formal/residual claims against source-group boundaries."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SPEC = HERE / "SOURCE_SEPARATOR_FORMAL_IMPACT_SPEC.md"
SOURCE_ATLAS = RESULTS / "source_separator_transcription.tsv"
SOURCE_RESULT = RESULTS / "source_separator_transcription.json"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
CANDIDATES = RESULTS / "unparsed_surface_candidate_lattice.tsv"
SEGMENTATION = RESULTS / "unparsed_surface_segmentation.json"
USR002 = RESULTS / "usr002_exact_y_capacity.tsv"
OUTPUT_TSV = RESULTS / "source_separator_formal_impact_groups.tsv"
OUTPUT_JSON = RESULTS / "source_separator_formal_impact.json"
OUTPUT_REPORT = RESULTS / "source_separator_formal_impact_report.md"

EXPECTED = {
    SOURCE_ATLAS: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    SOURCE_RESULT: "c047bef98ad0f83c65e0dbdad8e6904b6ed4ea6e3d945407191c39fd482e36f4",
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    CANDIDATES: "2b39b60c3bc4348490bd54a2a1965201e9d9eb625c98c3b5c9736b7f96ab12f1",
    SEGMENTATION: "fb003077191a98ef4a8c16b996552ed4fd635f93e1bb26109716f554cf46ea97",
    USR002: "280bd2d89c39a0d1466b6a79ae62a9cbfe3d92f2c63cd670f9abd842496d0407",
}

READINGS = ("ZL3b", "IT2a", "RF1b")
GROUP_FIELDS = [
    "source_group_id", "edition", "locus", "page", "grammar_scope", "kind",
    "source_group_index", "source_group_count", "left_separator", "right_separator",
    "ivtff_group_raw", "clean_ascii_fragments", "clean_ascii_fragment_count",
    "legacy_surface_positions_1based", "retained_fragment_positions_1based",
    "omitted_fragment_positions_1based", "retained_fragments", "omitted_fragments",
    "legacy_mapping_status", "formal_impact_class",
]
STATUS = "PASS_SOURCE_SEPARATOR_FORMAL_IMPACT_CORRECTION"
CLAIM = (
    "This audit distinguishes source groups from cleaner fragments and corrects affected "
    "structural counts only. It does not expand special glyphs, choose authorial spacing, "
    "repair the formal parser, assign an unparsed role, identify a sound or language, or "
    "provide plaintext or translation."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def formal_surfaces(row: dict[str, str]) -> list[str]:
    if not row["formal_interlinear"]:
        return []
    return [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]


def unique_mask(tokens: tuple[str, ...], target: str) -> tuple[bool, ...]:
    @lru_cache(maxsize=None)
    def solve(index: int, offset: int) -> tuple[int, tuple[bool, ...]]:
        if index == len(tokens):
            return (1, ()) if offset == len(target) else (0, ())
        count, suffix = solve(index + 1, offset)
        selected = (False,) + suffix if count else ()
        token = tokens[index]
        if target.startswith(token, offset):
            keep_count, keep_suffix = solve(index + 1, offset + len(token))
            if keep_count:
                if count == 0:
                    selected = (True,) + keep_suffix
                count = min(2, count + keep_count)
        return count, selected

    count, selected = solve(0, 0)
    if count != 1:
        raise RuntimeError(f"legacy/formal alignment has {count} solutions")
    return selected


def nested(counter: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = defaultdict(dict)
    for (left, right), count in sorted(counter.items()):
        output[left][right] = count
    return dict(output)


def main() -> None:
    observed = {str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): value for path, value in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("formal-impact input drift")

    atlas = load_tsv(SOURCE_ATLAS)
    interlinear_rows = load_tsv(INTERLINEAR)
    interlinear = {(row["edition"], row["locus"]): row for row in interlinear_rows}
    if len(interlinear) != len(interlinear_rows):
        raise RuntimeError("duplicate interlinear key")
    source_rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for group in atlas:
        source_rows[(group["edition"], group["locus"])].append(group)
    if len(atlas) != 115_470 or len(source_rows) != 15_985:
        raise RuntimeError("source atlas size drift")

    position_group: dict[tuple[str, str, int], dict[str, str]] = {}
    masks: dict[tuple[str, str], tuple[bool, ...]] = {}
    retained_positions: dict[tuple[str, str], list[int]] = {}
    affected_rows = Counter()
    affected_groups = Counter()
    first_last = Counter()
    source_scope_rows = Counter()
    legacy_scope_rows = Counter()
    omitted_events: dict[tuple[str, str, int], str] = {}
    impacted_group_rows: list[dict[str, str | int]] = []
    source_loci = defaultdict(set)
    source_pages = defaultdict(set)

    for key, groups in source_rows.items():
        groups.sort(key=lambda item: int(item["source_group_index"]))
        edition, locus = key
        if [int(group["source_group_index"]) for group in groups] != list(range(1, len(groups) + 1)):
            raise RuntimeError("noncontiguous source group indices")
        scope = groups[0]["grammar_scope"]
        source_scope_rows[(edition, scope)] += 1
        fragments: list[str] = []
        for group in groups:
            values = group["clean_ascii_fragments"].split()
            positions = [int(value) for value in group["legacy_surface_positions_1based"].split(",") if value]
            if len(values) != len(positions):
                raise RuntimeError("source fragment position mismatch")
            for position in positions:
                position_group[(edition, locus, position)] = group
            fragments.extend(values)

        if key in interlinear:
            row = interlinear[key]
            legacy_scope_rows[(edition, row["grammar_scope"])] += 1
            tokens = tuple(row["surface"].split())
            if list(tokens) != fragments:
                raise RuntimeError("atlas/interlinear surface drift")
            mask = unique_mask(tokens, "".join(formal_surfaces(row)))
            masks[key] = mask
            retained = [position for position, keep in enumerate(mask, 1) if keep]
            retained_positions[key] = retained
            for position, (token, keep) in enumerate(zip(tokens, mask), 1):
                if not keep:
                    omitted_events[(edition, locus, position)] = token
        else:
            if fragments:
                raise RuntimeError("nonempty source row absent from interlinear")
            masks[key] = ()
            retained_positions[key] = []

        bad_groups = [group for group in groups if group["legacy_mapping_status"] != "ONE_ASCII_FRAGMENT"]
        if bad_groups:
            affected_rows[(edition, scope)] += 1
            source_loci[edition].add(locus)
            source_pages[edition].add(groups[0]["page"])
        for boundary_name, group in (("FIRST", groups[0]), ("LAST", groups[-1])):
            if group["legacy_mapping_status"] != "ONE_ASCII_FRAGMENT":
                first_last[(edition, scope, boundary_name, group["legacy_mapping_status"])] += 1
        mask = masks[key]
        tokens = interlinear[key]["surface"].split() if key in interlinear else []
        for group in bad_groups:
            positions = [int(value) for value in group["legacy_surface_positions_1based"].split(",") if value]
            retained = [position for position in positions if mask and mask[position - 1]]
            omitted = [position for position in positions if not mask or not mask[position - 1]]
            if group["legacy_mapping_status"] == "ZERO_ASCII_FRAGMENT":
                impact = "SOURCE_GROUP_ABSENT_FROM_LEGACY_ASCII"
            elif retained and omitted:
                impact = "MULTI_FRAGMENT_MIXED_RETAINED_OMITTED"
            elif retained:
                impact = "MULTI_FRAGMENT_ALL_RETAINED"
            else:
                impact = "MULTI_FRAGMENT_ALL_OMITTED"
            affected_groups[(edition, scope, group["legacy_mapping_status"])] += 1
            impacted_group_rows.append({
                "source_group_id": group["source_group_id"],
                "edition": edition,
                "locus": locus,
                "page": group["page"],
                "grammar_scope": scope,
                "kind": group["kind"],
                "source_group_index": group["source_group_index"],
                "source_group_count": group["source_group_count"],
                "left_separator": group["left_separator"],
                "right_separator": group["right_separator"],
                "ivtff_group_raw": group["ivtff_group_raw"],
                "clean_ascii_fragments": group["clean_ascii_fragments"],
                "clean_ascii_fragment_count": group["clean_ascii_fragment_count"],
                "legacy_surface_positions_1based": group["legacy_surface_positions_1based"],
                "retained_fragment_positions_1based": ",".join(map(str, retained)),
                "omitted_fragment_positions_1based": ",".join(map(str, omitted)),
                "retained_fragments": " ".join(tokens[position - 1] for position in retained),
                "omitted_fragments": " ".join(tokens[position - 1] for position in omitted),
                "legacy_mapping_status": group["legacy_mapping_status"],
                "formal_impact_class": impact,
            })

    # Reconstruct and bind the published residual atlas event by event.
    stored_residual_events: dict[tuple[str, str, int], str] = {}
    for row in load_tsv(RESIDUAL):
        for item in row["position_token_pairs"].split(";"):
            position, token = item.split(":", 1)
            key = (row["edition"], row["locus"], int(position))
            if key in stored_residual_events:
                raise RuntimeError("duplicate residual event")
            stored_residual_events[key] = token
    if stored_residual_events != omitted_events:
        raise RuntimeError("residual event reconstruction drift")

    residual_source_class = Counter()
    residual_type_class = Counter()
    y_detail = Counter()
    for event, token in omitted_events.items():
        group = position_group[event]
        source_class = (
            "COMPLETE_SOURCE_GROUP"
            if int(group["clean_ascii_fragment_count"]) == 1
            else "INTRA_SOURCE_FRAGMENT"
        )
        residual_source_class[source_class] += 1
        residual_type_class[(source_class, token)] += 1
        if token == "y":
            y_detail[(event[0], source_class)] += 1
            if source_class == "COMPLETE_SOURCE_GROUP" and group["ivtff_group_raw"] == "y":
                y_detail[(event[0], "EXACT_RAW_Y_GROUP")] += 1

    # Consecutive retained formal nodes and registered positive role edges.
    formal_edges = Counter()
    formal_separators = Counter()
    confirmed_edges = Counter()
    confirmed_types = Counter()
    confirmed_type_topology = Counter()
    confirmed_separator_types = Counter()
    skipped_confirmed_examples: list[dict[str, object]] = []
    for key, row in interlinear.items():
        edition, locus = key
        retained = retained_positions[key]
        groups = source_rows[key]
        position_to_group_index = {
            position: int(position_group[(edition, locus, position)]["source_group_index"])
            for position in range(1, len(row["surface"].split()) + 1)
        }

        def topology(left_position: int, right_position: int) -> tuple[str, str]:
            left_group = position_to_group_index[left_position]
            right_group = position_to_group_index[right_position]
            if left_group == right_group:
                return "INTRA_SOURCE_GROUP", "NONMANUAL_CLEANER_BOUNDARY"
            if right_group == left_group + 1:
                return "ADJACENT_SOURCE_GROUPS", groups[left_group - 1]["right_separator"]
            return "SKIPS_SOURCE_GROUPS", "INTERVENING_SOURCE_GROUP"

        for left, right in zip(retained, retained[1:]):
            edge_class, separator = topology(left, right)
            formal_edges[(edition, edge_class)] += 1
            formal_separators[(edition, separator)] += 1
        for item in filter(None, row["confirmed_edges"].split(";")):
            coordinates, edge_type = item.split(":", 1)
            node_index = int(coordinates.split(">", 1)[0][1:])
            left, right = retained[node_index - 1], retained[node_index]
            edge_class, separator = topology(left, right)
            confirmed_edges[(edition, edge_class)] += 1
            confirmed_types[edge_type] += 1
            confirmed_type_topology[(edge_type, edge_class)] += 1
            confirmed_separator_types[(edge_type, separator)] += 1
            if edge_class == "SKIPS_SOURCE_GROUPS":
                left_group = position_to_group_index[left]
                right_group = position_to_group_index[right]
                skipped_confirmed_examples.append({
                    "edition": edition,
                    "locus": locus,
                    "registered_edge": item,
                    "left_legacy_position": left,
                    "right_legacy_position": right,
                    "intervening_source_groups": [
                        group["source_group_id"] for group in groups[left_group:right_group - 1]
                    ],
                })

    # Candidate-lattice totals, now split by source-group validity.
    candidate_counts = Counter()
    candidate_y_counts = Counter()
    candidate_rows = load_tsv(CANDIDATES)
    candidate_event_ids: set[str] = set()
    for row in candidate_rows:
        event = (row["edition"], row["locus"], int(row["surface_position_1based"]))
        if row["event_id"] in candidate_event_ids or omitted_events.get(event) != row["residual_token"]:
            raise RuntimeError("candidate event binding drift")
        candidate_event_ids.add(row["event_id"])
        source_class = (
            "COMPLETE_SOURCE_GROUP"
            if int(position_group[event]["clean_ascii_fragment_count"]) == 1
            else "INTRA_SOURCE_FRAGMENT"
        )
        candidate_counts[(source_class, row["coverage_class"])] += 1
        if row["residual_token"] == "y":
            candidate_y_counts[(source_class, row["coverage_class"])] += 1
    if len(candidate_event_ids) != 3_838:
        raise RuntimeError("candidate event count drift")

    # Direct cross-reading events; only one-fragment groups on both sides are safe.
    segmentation = json.loads(SEGMENTATION.read_text(encoding="utf-8"))
    summaries = segmentation["cross_reading_space_only"]["directed_residual_fusion_summary"]
    direct_counts = Counter()
    direct_type_counts = Counter()
    direct_loci = defaultdict(set)
    unsafe_direct: list[dict[str, object]] = []
    for token, summary in summaries.items():
        for event in summary["events_detail"]:
            source_key = (event["source_edition"], event["locus"], int(event["source_position_1based"]))
            fused_key = (event["other_edition"], event["locus"], int(event["fused_position_1based"]))
            source_group = position_group[source_key]
            fused_group = position_group[fused_key]
            safe = (
                int(source_group["clean_ascii_fragment_count"]) == 1
                and int(fused_group["clean_ascii_fragment_count"]) == 1
            )
            state = "SOURCE_SAFE" if safe else "CLEANER_AFFECTED"
            direct_counts[state] += 1
            direct_type_counts[(token, state)] += 1
            if safe:
                direct_loci[token].add(event["locus"])
            else:
                unsafe_direct.append({
                    "token": token,
                    "source_edition": event["source_edition"],
                    "other_edition": event["other_edition"],
                    "locus": event["locus"],
                    "source_group": source_group["source_group_id"],
                    "source_raw": source_group["ivtff_group_raw"],
                    "fused_group": fused_group["source_group_id"],
                })
            if token == "y" and event["sole_boundary_change"] and event["neighbor_mapping_preserved"]:
                direct_counts["Y_SOLE_MAPPING_PRESERVED_TOTAL"] += 1
                direct_counts["Y_SOLE_MAPPING_PRESERVED_SOURCE_SAFE"] += int(safe)
    if sum(direct_counts[state] for state in ("SOURCE_SAFE", "CLEANER_AFFECTED")) != 312:
        raise RuntimeError("direct event count drift")

    # The already-stopped USR002 panel remains source-safe if every target group is simple/raw.
    usr_rows = load_tsv(USR002)
    usr_safe = 0
    for candidate in usr_rows:
        offset = int(candidate["character_offset_1based"]) - 1
        for edition in READINGS:
            row = interlinear[(edition, candidate["locus"])]
            start = 0
            hit: tuple[int, str, int] | None = None
            for position, token in enumerate(row["surface"].split(), 1):
                if start <= offset < start + len(token):
                    hit = (position, token, offset - start)
                    break
                start += len(token)
            if hit is None or hit[1][hit[2]] != "y":
                raise RuntimeError("USR002 character-offset drift")
            group = position_group[(edition, candidate["locus"], hit[0])]
            safe = int(group["clean_ascii_fragment_count"]) == 1 and group["ivtff_group_raw"] == hit[1]
            if not safe:
                raise RuntimeError("USR002 source-group safety failure")
            usr_safe += 1
    if len(usr_rows) != 30 or usr_safe != 90:
        raise RuntimeError("USR002 panel size drift")

    # Keep a stable edition/page/locus/group order.
    impacted_group_rows.sort(key=lambda item: (READINGS.index(str(item["edition"])), str(item["page"]), str(item["locus"]), int(item["source_group_index"])))
    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GROUP_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(impacted_group_rows)

    corrected_direct_edges = {
        edge_type: confirmed_type_topology[(edge_type, "ADJACENT_SOURCE_GROUPS")]
        for edge_type in sorted(confirmed_types)
    }
    payload = {
        "status": STATUS,
        "inputs": observed,
        "implementation": {
            "spec_sha256": sha256(SPEC),
            "producer_sha256": sha256(Path(__file__)),
            "extended_entities_expanded": False,
            "formal_parser_rerun": False,
            "english_lexical_glosses": 0,
        },
        "source_exposure": {
            "source_scope_rows": nested(source_scope_rows),
            "legacy_scope_rows": nested(legacy_scope_rows),
            "affected_rows_by_edition_scope": nested(affected_rows),
            "affected_source_groups_by_edition_scope_status": {
                "|".join(key): value for key, value in sorted(affected_groups.items())
            },
            "affected_loci_by_edition": {edition: len(source_loci[edition]) for edition in READINGS},
            "affected_pages_by_edition": {edition: len(source_pages[edition]) for edition in READINGS},
            "first_last_affected": {"|".join(key): value for key, value in sorted(first_last.items())},
            "affected_group_rows": len(impacted_group_rows),
            "affected_group_atlas_sha256": sha256(OUTPUT_TSV),
        },
        "residual_correction": {
            "legacy_residual_events": len(omitted_events),
            "source_class_counts": dict(sorted(residual_source_class.items())),
            "complete_source_group_type_counts": {
                token: count for (source_class, token), count in sorted(residual_type_class.items())
                if source_class == "COMPLETE_SOURCE_GROUP"
            },
            "intra_source_fragment_type_counts": {
                token: count for (source_class, token), count in sorted(residual_type_class.items())
                if source_class == "INTRA_SOURCE_FRAGMENT"
            },
            "y_by_edition_source_class": {"|".join(key): value for key, value in sorted(y_detail.items())},
        },
        "formal_adjacency_correction": {
            "all_formal_adjacencies_by_edition_topology": nested(formal_edges),
            "all_formal_adjacencies_by_edition_separator": nested(formal_separators),
            "registered_hard_edges_by_edition_topology": nested(confirmed_edges),
            "registered_hard_edge_original_counts": dict(sorted(confirmed_types.items())),
            "registered_hard_edge_direct_source_counts": corrected_direct_edges,
            "registered_hard_edge_by_type_topology": {
                "|".join(key): value for key, value in sorted(confirmed_type_topology.items())
            },
            "registered_hard_edge_by_type_separator": {
                "|".join(key): value for key, value in sorted(confirmed_separator_types.items())
            },
            "skipped_registered_edge_examples": skipped_confirmed_examples,
        },
        "candidate_lattice_correction": {
            "events": len(candidate_event_ids),
            "by_source_class_and_coverage": {"|".join(key): value for key, value in sorted(candidate_counts.items())},
            "y_by_source_class_and_coverage": {"|".join(key): value for key, value in sorted(candidate_y_counts.items())},
        },
        "direct_spacing_evidence": {
            "events": sum(direct_counts[state] for state in ("SOURCE_SAFE", "CLEANER_AFFECTED")),
            "source_safe_events": direct_counts["SOURCE_SAFE"],
            "cleaner_affected_events": direct_counts["CLEANER_AFFECTED"],
            "by_token_and_state": {"|".join(key): value for key, value in sorted(direct_type_counts.items())},
            "source_safe_physical_loci_by_token": {token: len(loci) for token, loci in sorted(direct_loci.items())},
            "y_sole_boundary_mapping_preserved_total": direct_counts["Y_SOLE_MAPPING_PRESERVED_TOTAL"],
            "y_sole_boundary_mapping_preserved_source_safe": direct_counts["Y_SOLE_MAPPING_PRESERVED_SOURCE_SAFE"],
            "cleaner_affected_examples": unsafe_direct,
        },
        "usr002_invariance": {
            "candidate_spans": len(usr_rows),
            "reading_specific_target_groups": usr_safe,
            "all_are_exact_raw_one_fragment_groups": usr_safe == 90,
            "prior_unscored_stop_unchanged": True,
        },
        "gates": {
            "source_atlas_complete": len(atlas) == 115_470 and len(source_rows) == 15_985,
            "all_residual_events_reconstructed": len(omitted_events) == 3_838,
            "all_affected_groups_emitted": len(impacted_group_rows) == 2_861,
            "all_formal_adjacencies_classified": sum(formal_edges.values()) == 98_274,
            "all_registered_hard_edges_classified": sum(confirmed_edges.values()) == 4_737,
            "zero_registered_hard_edges_inside_source_group": sum(
                count for (edition, topology), count in confirmed_edges.items()
                if topology == "INTRA_SOURCE_GROUP"
            ) == 0,
            "candidate_lattice_event_set_complete": len(candidate_event_ids) == 3_838,
            "direct_spacing_event_set_complete": sum(direct_counts[state] for state in ("SOURCE_SAFE", "CLEANER_AFFECTED")) == 312,
            "usr002_source_safe_stop_invariant": usr_safe == 90,
            "no_semantic_assignment": True,
        },
        "decision": {
            "broad_residual_and_candidate_counts_require_correction": True,
            "direct_cross_reading_spacing_evidence_retained_qualified": True,
            "registered_hard_dependency_system_retained_with_six_exclusions": True,
            "rf1b_token_boundary_features_require_source_aware_rebuild": True,
            "usr002_unscored_stop_reopened": False,
        },
        "claim_ceiling": CLAIM,
    }
    if not all(payload["gates"].values()):
        raise RuntimeError("formal-impact gate failure")
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    residual = payload["residual_correction"]
    formal = payload["formal_adjacency_correction"]
    direct = payload["direct_spacing_evidence"]
    candidate = payload["candidate_lattice_correction"]
    report = f"""# Source-separator impact on the legacy formal layer

Status: **{STATUS}**

The impact is large but localized. Of the **{residual['legacy_residual_events']:,}**
legacy residual events, only
**{residual['source_class_counts']['COMPLETE_SOURCE_GROUP']:,}** are complete
source groups; **{residual['source_class_counts']['INTRA_SOURCE_FRAGMENT']:,}**
are fragments created inside a source group by the ASCII cleaner.

The old `y` residual total was 2,463. Only 731 are complete one-fragment source
groups, and only **625** have the exact raw group spelling `y`; 1,732 are
intra-group cleaner fragments. Consequently the broad one-sided candidate
lattice is corrected from 2,178 mapping-preserving events to **576 complete
source groups**. For `y`, the corresponding correction is 2,117 to **525**.

The direct natural experiments mostly survive. **{direct['source_safe_events']:,}/312**
directed split/fused events are source-safe, including **186/188** `y` events.
The conservative mapping-preserving `y` subset becomes
**{direct['y_sole_boundary_mapping_preserved_source_safe']}/{direct['y_sole_boundary_mapping_preserved_total']}**.
Both excluded events are the same ZL f89r2.9 cleaner split of raw `otold[:y]`.
All 90 reading-specific groups behind the already-unscored USR002 capacity panel
are exact raw one-fragment groups, so that transcription-confidence stop is
unchanged.

The core registered dependency inventory is much less affected. There are 917
retained formal adjacencies inside one source group, but **zero** is one of the
4,737 registered hard edges. **4,731/4,737** registered edges directly join
adjacent source groups; six skip an intervening source group. Among the direct
edges, 4,699 cross a confident apparent space, 26 an uncertain small space, and
six a drawing interruption. The safe description is therefore a required
source separator, usually confident—not a universal “mandatory space.”

RF1b carries 901/917 intra-source formal adjacencies and 1,793/1,801 residual
fragments, so RF token-boundary and word-count features require a source-aware
rebuild. ZL3b and IT2a are much less exposed. This does not license a meaning,
word, sound, language, plaintext, or translation.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
