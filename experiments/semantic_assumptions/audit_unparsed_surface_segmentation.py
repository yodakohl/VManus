#!/usr/bin/env python3
"""Audit whether omitted surface groups behave like alternate space decisions.

This is descriptive and root/role meanings are explicitly out of scope.  It
uses exact manual transcription strings only: alternate readings are compared
at the same physical locus when their concatenated characters are identical.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
OUTPUT_JSON = RESULTS / "unparsed_surface_segmentation.json"
OUTPUT_REPORT = RESULTS / "unparsed_surface_segmentation_report.md"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
}
READING_ORDER = {"ZL3b": 0, "IT2a": 1, "RF1b": 2}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def boundaries(tokens: list[str]) -> set[int]:
    out: set[int] = set()
    offset = 0
    for token in tokens[:-1]:
        offset += len(token)
        out.add(offset)
    return out


def token_left_of(tokens: list[str], boundary: int) -> tuple[int, str]:
    offset = 0
    for index, token in enumerate(tokens):
        offset += len(token)
        if offset == boundary:
            return index, token
    raise ValueError("boundary is not present")


def spans(tokens: list[str]) -> list[tuple[int, int]]:
    out = []
    start = 0
    for token in tokens:
        end = start + len(token)
        out.append((start, end))
        start = end
    return out


def formal_type_mappings(rows: list[dict[str, str]]) -> dict[str, set[tuple[str, str]]]:
    mappings: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in rows:
        if not row["formal_interlinear"]:
            continue
        surfaces = [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]
        roots = row["root_sequence"].split()
        roles = row["role_sequence"].split()
        if not (len(surfaces) == len(roots) == len(roles)):
            raise RuntimeError(f"formal tuple drift at {(row['edition'], row['locus'])}")
        for surface, root, role in zip(surfaces, roots, roles):
            mappings[surface].add((root, role))
    return mappings


def formal_position_mappings(
    rows: list[dict[str, str]], residual_at: dict[tuple[str, str], set[int]]
) -> dict[tuple[str, str], list[tuple[str, str] | None]]:
    out: dict[tuple[str, str], list[tuple[str, str] | None]] = {}
    for row in rows:
        key = (row["edition"], row["locus"])
        surface = row["surface"].split()
        omitted = residual_at.get(key, set())
        roots = row["root_sequence"].split()
        roles = row["role_sequence"].split()
        formal_surfaces = (
            [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]
            if row["formal_interlinear"] else []
        )
        if not (len(formal_surfaces) == len(roots) == len(roles)):
            raise RuntimeError(f"formal position tuple drift at {key}")
        values: list[tuple[str, str] | None] = []
        formal_index = 0
        for position, token in enumerate(surface, start=1):
            if position in omitted:
                values.append(None)
                continue
            if formal_index >= len(formal_surfaces) or formal_surfaces[formal_index] != token:
                raise RuntimeError(f"formal surface position drift at {key}")
            values.append((roots[formal_index], roles[formal_index]))
            formal_index += 1
        if formal_index != len(formal_surfaces):
            raise RuntimeError(f"formal position exhaustion drift at {key}")
        out[key] = values
    return out


def main() -> None:
    observed = {path: sha256(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError("frozen segmentation-audit input drift")
    rows = load(INTERLINEAR)
    residual_rows = load(RESIDUAL)
    if len(rows) != 15_960:
        raise RuntimeError("interlinear row count drift")

    omitted_occurrences: Counter[str] = Counter()
    residual_at: dict[tuple[str, str], set[int]] = {}
    for row in residual_rows:
        positions = {int(value) for value in row["omitted_positions_1based"].split(";")}
        tokens = row["omitted_tokens"].split()
        if len(positions) != len(tokens) or len(tokens) != int(row["omitted_token_count"]):
            raise RuntimeError("residual count drift")
        residual_at[(row["edition"], row["locus"])] = positions
        omitted_occurrences.update(tokens)

    surface_occurrences: Counter[str] = Counter()
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        surface_occurrences.update(row["surface"].split())
        by_locus[row["locus"]].append(row)

    omitted_types = set(omitted_occurrences)
    partial_types = sorted(
        token for token, count in omitted_occurrences.items()
        if count != surface_occurrences[token]
    )
    if partial_types:
        raise RuntimeError(f"partially omitted exact types: {partial_types}")

    mappings = formal_type_mappings(rows)
    position_mappings = formal_position_mappings(rows, residual_at)
    pair_counts: Counter[str] = Counter()
    locus_sets: dict[str, set[str]] = defaultdict(set)
    residual_right: Counter[str] = Counter()
    residual_left: Counter[str] = Counter()
    direct_events: list[dict[str, object]] = []
    directed_fusions: list[dict[str, object]] = []

    for locus, locus_rows in sorted(by_locus.items()):
        locus_rows.sort(key=lambda row: READING_ORDER[row["edition"]])
        for row_a, row_b in itertools.combinations(locus_rows, 2):
            tokens_a = row_a["surface"].split()
            tokens_b = row_b["surface"].split()
            if "".join(tokens_a) != "".join(tokens_b):
                continue
            if tokens_a == tokens_b:
                pair_counts["exact_same_tokenization_pairs"] += 1
                locus_sets["exact_same_tokenization_loci"].add(locus)
                continue
            pair_counts["space_only_variant_pairs"] += 1
            locus_sets["space_only_variant_loci"].add(locus)
            ba = boundaries(tokens_a)
            bb = boundaries(tokens_b)
            for source_row, source_tokens, other_row, other_tokens, other_internal in (
                (row_a, tokens_a, row_b, tokens_b, bb),
                (row_b, tokens_b, row_a, tokens_a, ba),
            ):
                source_residuals = residual_at.get((source_row["edition"], locus), set())
                other_all_boundaries = {0, len("".join(other_tokens))} | other_internal
                source_spans = spans(source_tokens)
                other_spans = spans(other_tokens)
                source_position_map = position_mappings[(source_row["edition"], locus)]
                other_position_map = position_mappings[(other_row["edition"], locus)]
                for source_position in sorted(source_residuals):
                    token = source_tokens[source_position - 1]
                    start, end = source_spans[source_position - 1]
                    if any(start < value < end for value in other_all_boundaries):
                        pair_counts["residual_internally_split_in_other_reading"] += 1
                        continue
                    missing_left = start not in other_all_boundaries
                    missing_right = end not in other_all_boundaries
                    if not (missing_left or missing_right):
                        continue
                    direction = (
                        "BOTH" if missing_left and missing_right
                        else "LEFT" if missing_left else "RIGHT"
                    )
                    fused_index = next(
                        index for index, (other_start, other_end) in enumerate(other_spans)
                        if other_start <= start and end <= other_end
                    )
                    neighbor_index = (
                        source_position - 2 if direction == "LEFT"
                        else source_position if direction == "RIGHT"
                        else None
                    )
                    neighbor_mapping = (
                        source_position_map[neighbor_index]
                        if neighbor_index is not None else None
                    )
                    fused_mapping = other_position_map[fused_index]
                    removed_boundaries = (
                        ({start} if missing_left else set())
                        | ({end} if missing_right else set())
                    )
                    directed_fusions.append({
                        "locus": locus,
                        "source_edition": source_row["edition"],
                        "other_edition": other_row["edition"],
                        "source_position_1based": source_position,
                        "token": token,
                        "direction": direction,
                        "fused": other_tokens[fused_index],
                        "fused_position_1based": fused_index + 1,
                        "neighbor_mapping": neighbor_mapping,
                        "fused_mapping": fused_mapping,
                        "neighbor_mapping_preserved": (
                            neighbor_mapping is not None and neighbor_mapping == fused_mapping
                        ),
                        "sole_boundary_change": (ba ^ bb) == removed_boundaries,
                    })
            diff = ba ^ bb
            if len(diff) != 1:
                pair_counts["multi_boundary_variant_pairs"] += 1
                locus_sets["multi_boundary_variant_loci"].add(locus)
                continue
            pair_counts["single_boundary_variant_pairs"] += 1
            locus_sets["single_boundary_variant_loci"].add(locus)
            boundary = next(iter(diff))
            if boundary in ba:
                split_row, split_tokens, fused_row, fused_tokens = row_a, tokens_a, row_b, tokens_b
            else:
                split_row, split_tokens, fused_row, fused_tokens = row_b, tokens_b, row_a, tokens_a
            left_index, left = token_left_of(split_tokens, boundary)
            right = split_tokens[left_index + 1]
            fused_index = -1
            offset = 0
            fused = ""
            for candidate_index, candidate in enumerate(fused_tokens):
                next_offset = offset + len(candidate)
                if offset < boundary < next_offset:
                    fused = candidate
                    fused_index = candidate_index
                    break
                offset = next_offset
            if fused != left + right or fused_index < 0:
                raise RuntimeError("single-boundary fusion identity failure")
            split_residuals = residual_at.get((split_row["edition"], locus), set())
            right_is_residual = left_index + 2 in split_residuals
            left_is_residual = left_index + 1 in split_residuals
            if right_is_residual:
                residual_right[right] += 1
                pair_counts["right_residual_split_pairs"] += 1
                locus_sets["right_residual_split_loci"].add(locus)
            if left_is_residual:
                residual_left[left] += 1
                pair_counts["left_residual_split_pairs"] += 1
                locus_sets["left_residual_split_loci"].add(locus)
            left_map = sorted(mappings.get(left, set()))
            right_map = sorted(mappings.get(right, set()))
            fused_map = sorted(mappings.get(fused, set()))
            split_position_map = position_mappings[(split_row["edition"], locus)]
            fused_position_map = position_mappings[(fused_row["edition"], locus)]
            left_occurrence_mapping = split_position_map[left_index]
            right_occurrence_mapping = split_position_map[left_index + 1]
            fused_occurrence_mapping = fused_position_map[fused_index]
            direct_events.append({
                "locus": locus,
                "split_edition": split_row["edition"],
                "fused_edition": fused_row["edition"],
                "boundary_character_offset": boundary,
                "split_position_1based": left_index + 2,
                "left": left,
                "right": right,
                "fused": fused,
                "left_is_unparsed_surface": left_is_residual,
                "right_is_unparsed_surface": right_is_residual,
                "left_mapping": left_map,
                "right_mapping": right_map,
                "fused_mapping": fused_map,
                "left_and_fused_mapping_identical": bool(left_map) and left_map == fused_map,
                "right_and_fused_mapping_identical": bool(right_map) and right_map == fused_map,
                "left_occurrence_mapping": left_occurrence_mapping,
                "right_occurrence_mapping": right_occurrence_mapping,
                "fused_occurrence_mapping": fused_occurrence_mapping,
                "left_and_fused_occurrence_mapping_identical": (
                    left_occurrence_mapping is not None
                    and left_occurrence_mapping == fused_occurrence_mapping
                ),
                "fused_token_index_1based": fused_index + 1,
            })

    right_type_summary = {}
    for token, count in sorted(residual_right.items(), key=lambda item: (-item[1], item[0])):
        selected = [event for event in direct_events if event["right_is_unparsed_surface"] and event["right"] == token]
        right_type_summary[token] = {
            "reading_pair_events": count,
            "physical_loci": len({str(event["locus"]) for event in selected}),
            "left_and_fused_mapping_identical_events": sum(
                bool(event["left_and_fused_mapping_identical"]) for event in selected
            ),
            "left_and_fused_occurrence_mapping_identical_events": sum(
                bool(event["left_and_fused_occurrence_mapping_identical"]) for event in selected
            ),
            "examples": selected[:8],
        }

    directed_summary = {}
    for token in sorted({str(event["token"]) for event in directed_fusions}):
        selected = [event for event in directed_fusions if event["token"] == token]
        direction_counts = Counter(str(event["direction"]) for event in selected)
        source_pairs = Counter(
            f"{event['source_edition']}->{event['other_edition']}" for event in selected
        )
        sole_eligible = [
            event for event in selected
            if event["sole_boundary_change"]
            and event["direction"] != "BOTH"
            and event["neighbor_mapping"] is not None
            and event["fused_mapping"] is not None
        ]
        directed_summary[token] = {
            "events": len(selected),
            "physical_loci": len({str(event["locus"]) for event in selected}),
            "direction": {
                name: direction_counts[name] for name in ("LEFT", "RIGHT", "BOTH")
            },
            "source_to_other_reading": dict(sorted(source_pairs.items())),
            "sole_boundary_change_events": sum(
                bool(event["sole_boundary_change"]) for event in selected
            ),
            "fused_outcome_is_parsed_events": sum(
                event["fused_mapping"] is not None for event in selected
            ),
            "neighbor_mapping_preserved_events": sum(
                bool(event["neighbor_mapping_preserved"]) for event in selected
            ),
            "sole_boundary_eligible_neighbor_mapping_events": len(sole_eligible),
            "sole_boundary_neighbor_mapping_preserved_events": sum(
                bool(event["neighbor_mapping_preserved"]) for event in sole_eligible
            ),
            "events_detail": selected,
        }

    core_types = {"y", "dy", "ky", "sy"}
    core_directed_fusions = [
        event for event in directed_fusions if event["token"] in core_types
    ]

    type_determinism = {
        "surface_groups": sum(surface_occurrences.values()),
        "surface_types": len(surface_occurrences),
        "always_omitted_types": len(omitted_types),
        "always_omitted_occurrences": sum(omitted_occurrences.values()),
        "never_omitted_types": len(surface_occurrences) - len(omitted_types),
        "partially_omitted_types": len(partial_types),
        "always_omitted_type_inventory": [
            {"token": token, "occurrences": omitted_occurrences[token]}
            for token in sorted(omitted_types, key=lambda item: (-omitted_occurrences[item], item))
        ],
    }
    payload = {
        "status": "PASS_UNPARSED_SURFACE_SEGMENTATION_INVENTORY",
        "decision": "BOUNDARY_MOBILE_Y_AND_LEFT_FUSING_DY_KY_ARE_STRUCTURAL_LEADS_NOT_CONFIRMED",
        "input_sha256": {
            str(path.relative_to(HERE.parents[1])): value for path, value in observed.items()
        },
        "type_determinism": type_determinism,
        "cross_reading_space_only": {
            "pair_counts": dict(sorted(pair_counts.items())),
            "physical_locus_counts": {
                name: len(values) for name, values in sorted(locus_sets.items())
            },
            "right_residual_type_counts": dict(residual_right.most_common()),
            "left_residual_type_counts": dict(residual_left.most_common()),
            "right_residual_type_summary": right_type_summary,
            "all_single_boundary_events": direct_events,
            "directed_residual_fusion_summary": directed_summary,
            "directed_residual_fusion_events": len(directed_fusions),
            "directed_residual_fusion_physical_loci": len(
                {str(event["locus"]) for event in directed_fusions}
            ),
            "core_y_dy_ky_sy_fusion_events": len(core_directed_fusions),
            "core_y_dy_ky_sy_fusion_physical_loci": len(
                {str(event["locus"]) for event in core_directed_fusions}
            ),
        },
        "gates": {
            "exact_token_identity_determines_frozen_parser_omission": len(partial_types) == 0,
            "at_least_one_space_only_single_boundary_variant": bool(direct_events),
            "core_fusion_events_reconstruct_expected_280": len(core_directed_fusions) == 280,
            "y_is_boundary_mobile_not_suffix_only": (
                directed_summary["y"]["direction"] == {"LEFT": 63, "RIGHT": 118, "BOTH": 7}
            ),
            "sole_boundary_y_preserves_neighbor_mapping_130_of_130": (
                directed_summary["y"]["sole_boundary_eligible_neighbor_mapping_events"] == 130
                and directed_summary["y"]["sole_boundary_neighbor_mapping_preserved_events"] == 130
            ),
        },
        "next_test": (
            "Run only a parser-free capacity and power preflight for exact-y cross-reading spacing natural "
            "experiments. Treat alternate readings as repeated observations of the same locus, not "
            "independent samples; do not use the unavailable parser's omissions as held labels."
        ),
        "claim_ceiling": (
            "The frozen parser's omission is exact-token deterministic, and direct alternate-reading "
            "space-only variants show that some omitted groups participate in boundary-mobile alternate "
            "segmentations. Frozen mapping preservation is a repair clue, not an independently reproducible "
            "parser result. This establishes neither authorial spacing nor a suffix, morpheme, sound, "
            "separator, word, number, or meaning."
        ),
        "english_lexical_glosses": 0,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    y = directed_summary["y"]
    dy = directed_summary["dy"]
    ky = directed_summary["ky"]
    sy = directed_summary["sy"]
    report = f"""# UNPARSED_SURFACE segmentation inventory

Decision: **BOUNDARY-MOBILE `y` AND LEFT-FUSING `dy`/`ky` ARE STRUCTURAL
LEADS, NOT CONFIRMED FUNCTIONS**.

The complete manual surface has {type_determinism['surface_groups']:,} groups
of {type_determinism['surface_types']:,} exact types.  Exactly
{type_determinism['always_omitted_types']} types account for all
{type_determinism['always_omitted_occurrences']:,} omitted occurrences;
{type_determinism['never_omitted_types']:,} types are never omitted and zero
types are partly omitted.  The frozen formal parser therefore has a
deterministic lexical coverage hole, not random row loss.

Among alternate readings of the same physical locus, exact concatenated
characters with different spaces occur in
{pair_counts['space_only_variant_pairs']:,} reading pairs on
{len(locus_sets['space_only_variant_loci']):,} loci.  Of these,
{pair_counts['single_boundary_variant_pairs']:,} pairs differ at exactly one
space.  The four leading residual types `y/dy/ky/sy` participate in
{len(core_directed_fusions):,} directed fusion events on
{len({str(event['locus']) for event in core_directed_fusions}):,} physical
loci.

| type | events | loci | LEFT | RIGHT | BOTH |
|---|---:|---:|---:|---:|---:|
| `y` | {y['events']} | {y['physical_loci']} | {y['direction']['LEFT']} | {y['direction']['RIGHT']} | {y['direction']['BOTH']} |
| `dy` | {dy['events']} | {dy['physical_loci']} | {dy['direction']['LEFT']} | {dy['direction']['RIGHT']} | {dy['direction']['BOTH']} |
| `ky` | {ky['events']} | {ky['physical_loci']} | {ky['direction']['LEFT']} | {ky['direction']['RIGHT']} | {ky['direction']['BOTH']} |
| `sy` | {sy['events']} | {sy['physical_loci']} | {sy['direction']['LEFT']} | {sy['direction']['RIGHT']} | {sy['direction']['BOTH']} |

`LEFT` and `RIGHT` name the boundary missing in the other transcription.
Literal `y` is therefore boundary-mobile, not suffix-only.  `dy` and `ky`
instead fuse predominantly to the left.  In the conservative cases where the
entire reading pair differs only at that one boundary, the incomplete frozen
parser preserves the adjacent root/role mapping in 130/130 eligible `y`
events, versus 0/40 for `dy`, 0/12 for `ky`, and 0/1 for `sy`.  This is a useful
formal-repair clue, but it is not an independent parser validation because the
parser source is unavailable.

Alternate readings are repeated descriptions of the same manuscript, not
independent samples, and different transcribed spaces do not by themselves
prove authorial spacing.  The next step is only a parser-free capacity and
power preflight for exact-y split/fused natural experiments at physical-locus
level.  No suffix, morpheme, separator, sound, number, plaintext, or English
meaning is assigned.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "space_only_pairs": pair_counts["space_only_variant_pairs"],
        "single_boundary_pairs": pair_counts["single_boundary_variant_pairs"],
        "right_residual_pairs": pair_counts["right_residual_split_pairs"],
        "y_fusion_events": y["events"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
