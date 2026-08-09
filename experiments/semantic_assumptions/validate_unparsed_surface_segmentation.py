#!/usr/bin/env python3
"""Clean-room validation of the frozen UNPARSED_SURFACE segmentation audit.

This module deliberately does not import the production audit.  It rebuilds
surface boundaries, residual positions, retained-node occurrence mappings,
and directed split/fused events from the two frozen TSV inputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
PRODUCER = HERE / "audit_unparsed_surface_segmentation.py"
RESULT = RESULTS / "unparsed_surface_segmentation.json"
REPORT = RESULTS / "unparsed_surface_segmentation_report.md"
OUTPUT = RESULTS / "unparsed_surface_segmentation_validation.json"
OUTPUT_REPORT = RESULTS / "unparsed_surface_segmentation_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
CORE_TYPES = ("y", "dy", "ky", "sy")

EXPECTED_SHA256 = {
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv":
        "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv":
        "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    "experiments/semantic_assumptions/audit_unparsed_surface_segmentation.py":
        "fce6d791367fd088545f8888ba7cbdcac3f82aadfb1471f2ce5e172ddbb8225e",
    "experiments/semantic_assumptions/results/unparsed_surface_segmentation.json":
        "fb003077191a98ef4a8c16b996552ed4fd635f93e1bb26109716f554cf46ea97",
    "experiments/semantic_assumptions/results/unparsed_surface_segmentation_report.md":
        "59b9d28079d6ed705ac46749f57e9738dd07e4c04f4b34c7bdf46722ef64dfa5",
}

EXPECTED_OMITTED = {
    "ddy": 6, "dg": 3, "dky": 3, "dm": 4, "dpy": 3, "dsy": 2,
    "dy": 774, "dym": 3, "f": 30, "fydy": 3, "g": 41, "gm": 2,
    "ky": 83, "m": 53, "mdy": 1, "p": 31, "py": 8, "sy": 114,
    "ty": 51, "y": 2463, "ydy": 25, "yf": 1, "yky": 51, "yp": 2,
    "ypdy": 2, "yty": 73, "ytym": 1, "yy": 5,
}

EXPECTED_CORE = {
    "y": {
        "events": 188,
        "physical_loci": 128,
        "direction": {"BOTH": 7, "LEFT": 63, "RIGHT": 118},
        "source_to_other_reading": {
            "IT2a->RF1b": 19, "IT2a->ZL3b": 8,
            "RF1b->IT2a": 15, "RF1b->ZL3b": 4,
            "ZL3b->IT2a": 89, "ZL3b->RF1b": 53,
        },
        "direction_loci": {
            "IT2a->RF1b": 19, "IT2a->ZL3b": 8,
            "RF1b->IT2a": 15, "RF1b->ZL3b": 4,
            "ZL3b->IT2a": 87, "ZL3b->RF1b": 52,
        },
        "fused_outcome_is_parsed_events": 178,
        "neighbor_mapping_preserved_events": 163,
        "sole_boundary_change_events": 139,
        "sole_boundary_eligible_neighbor_mapping_events": 130,
        "sole_boundary_neighbor_mapping_preserved_events": 130,
    },
    "dy": {
        "events": 68,
        "physical_loci": 40,
        "direction": {"BOTH": 3, "LEFT": 57, "RIGHT": 8},
        "source_to_other_reading": {
            "IT2a->RF1b": 13, "IT2a->ZL3b": 13,
            "RF1b->IT2a": 2, "RF1b->ZL3b": 5,
            "ZL3b->IT2a": 15, "ZL3b->RF1b": 20,
        },
        "direction_loci": {
            "IT2a->RF1b": 12, "IT2a->ZL3b": 13,
            "RF1b->IT2a": 2, "RF1b->ZL3b": 5,
            "ZL3b->IT2a": 13, "ZL3b->RF1b": 18,
        },
        "fused_outcome_is_parsed_events": 66,
        "neighbor_mapping_preserved_events": 0,
        "sole_boundary_change_events": 43,
        "sole_boundary_eligible_neighbor_mapping_events": 40,
        "sole_boundary_neighbor_mapping_preserved_events": 0,
    },
    "ky": {
        "events": 22,
        "physical_loci": 14,
        "direction": {"BOTH": 1, "LEFT": 19, "RIGHT": 2},
        "source_to_other_reading": {
            "IT2a->RF1b": 2, "IT2a->ZL3b": 3,
            "RF1b->IT2a": 2,
            "ZL3b->IT2a": 8, "ZL3b->RF1b": 7,
        },
        "direction_loci": {
            "IT2a->RF1b": 2, "IT2a->ZL3b": 3,
            "RF1b->IT2a": 2,
            "ZL3b->IT2a": 8, "ZL3b->RF1b": 7,
        },
        "fused_outcome_is_parsed_events": 21,
        "neighbor_mapping_preserved_events": 0,
        "sole_boundary_change_events": 14,
        "sole_boundary_eligible_neighbor_mapping_events": 12,
        "sole_boundary_neighbor_mapping_preserved_events": 0,
    },
    "sy": {
        "events": 2,
        "physical_loci": 1,
        "direction": {"BOTH": 0, "LEFT": 2, "RIGHT": 0},
        "source_to_other_reading": {
            "IT2a->ZL3b": 1, "RF1b->ZL3b": 1,
        },
        "direction_loci": {
            "IT2a->ZL3b": 1, "RF1b->ZL3b": 1,
        },
        "fused_outcome_is_parsed_events": 2,
        "neighbor_mapping_preserved_events": 0,
        "sole_boundary_change_events": 1,
        "sole_boundary_eligible_neighbor_mapping_events": 1,
        "sole_boundary_neighbor_mapping_preserved_events": 0,
    },
}

EXPECTED_STATUS = "PASS_UNPARSED_SURFACE_SEGMENTATION_INVENTORY"
EXPECTED_DECISION = (
    "BOUNDARY_MOBILE_Y_AND_LEFT_FUSING_DY_KY_ARE_STRUCTURAL_LEADS_NOT_CONFIRMED"
)
EXPECTED_CLAIM = (
    "The frozen parser's omission is exact-token deterministic, and direct alternate-reading "
    "space-only variants show that some omitted groups participate in boundary-mobile alternate "
    "segmentations. Frozen mapping preservation is a repair clue, not an independently reproducible "
    "parser result. This establishes neither authorial spacing nor a suffix, morpheme, sound, "
    "separator, word, number, or meaning."
)
EXPECTED_NEXT_TEST = (
    "Run only a parser-free capacity and power preflight for exact-y cross-reading spacing natural "
    "experiments. Treat alternate readings as repeated observations of the same locus, not independent "
    "samples; do not use the unavailable parser's omissions as held labels."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class RowView:
    """Independent character-offset and retained-position view of one row."""

    def __init__(self, row: dict[str, str], omitted: dict[int, str]) -> None:
        self.row = row
        self.tokens = row["surface"].split()
        self.starts: list[int] = []
        self.ends: list[int] = []
        offset = 0
        for token in self.tokens:
            self.starts.append(offset)
            offset += len(token)
            self.ends.append(offset)
        self.compact = "".join(self.tokens)
        self.boundaries = set(self.ends[:-1])
        self.omitted = omitted

        retained_positions = [
            position for position in range(1, len(self.tokens) + 1)
            if position not in omitted
        ]
        roots = row["root_sequence"].split()
        roles = row["role_sequence"].split()
        if len(retained_positions) != len(roots) or len(roots) != len(roles):
            raise AssertionError("retained occurrence mapping cardinality mismatch")
        if len(roots) != int(row["word_count"]):
            raise AssertionError("word_count does not bind retained mappings")
        self.mapping = {
            position: (roots[index], roles[index])
            for index, position in enumerate(retained_positions)
        }

    def containing_position(self, start: int, end: int) -> int | None:
        matches = [
            position
            for position, (left, right) in enumerate(zip(self.starts, self.ends), 1)
            if left <= start and right >= end
        ]
        return matches[0] if len(matches) == 1 else None


def main() -> None:
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        if not condition:
            raise AssertionError(message)
        checks += 1

    paths = {relative: REPO / relative for relative in EXPECTED_SHA256}
    observed_hashes = {relative: sha256(path) for relative, path in paths.items()}
    check(observed_hashes == EXPECTED_SHA256, "frozen artifact hash mismatch")

    rows = read_tsv(INTERLINEAR)
    residual_rows = read_tsv(RESIDUAL)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    by_key = {(row["edition"], row["locus"]): row for row in rows}
    check(len(rows) == len(by_key) == 15_960, "interlinear key/cardinality mismatch")
    check(len(residual_rows) == 2_833, "residual atlas row cardinality mismatch")

    omissions: dict[tuple[str, str], dict[int, str]] = {}
    for residual in residual_rows:
        key = (residual["edition"], residual["locus"])
        check(key in by_key and key not in omissions, "residual key mismatch")
        positions = [int(value) for value in residual["omitted_positions_1based"].split(";")]
        tokens = residual["omitted_tokens"].split()
        check(
            len(positions) == len(tokens) == int(residual["omitted_token_count"]),
            "residual event cardinality mismatch",
        )
        surface = by_key[key]["surface"].split()
        check(
            all(1 <= position <= len(surface) for position in positions),
            "residual position outside surface",
        )
        check(
            all(surface[position - 1] == token for position, token in zip(positions, tokens)),
            "residual token does not match full surface",
        )
        check(
            residual["position_token_pairs"]
            == ";".join(f"{position}:{token}" for position, token in zip(positions, tokens)),
            "position-token serialization mismatch",
        )
        omissions[key] = dict(zip(positions, tokens))

    views = {
        key: RowView(row, omissions.get(key, {}))
        for key, row in by_key.items()
    }

    surface_counts: Counter[str] = Counter()
    omitted_counts: Counter[str] = Counter()
    for key, view in views.items():
        surface_counts.update(view.tokens)
        omitted_counts.update(view.omitted.values())
        check(
            all(view.tokens[position - 1] == token for position, token in view.omitted.items()),
            "view omission mismatch",
        )

    partially_omitted = sorted(
        token for token, count in omitted_counts.items()
        if count != surface_counts[token]
    )
    always_omitted = {
        token: surface_counts[token]
        for token in surface_counts
        if omitted_counts[token] == surface_counts[token]
    }
    never_omitted = {
        token for token in surface_counts if omitted_counts[token] == 0
    }
    check(sum(surface_counts.values()) == 118_011, "surface group total")
    check(dict(sorted(always_omitted.items())) == EXPECTED_OMITTED, "exact omitted type inventory")
    check(not partially_omitted, "partially omitted token type found")
    check(len(surface_counts) == 10_909 and len(never_omitted) == 10_881, "surface vocabulary partition")

    expected_type_determinism = {
        "surface_groups": sum(surface_counts.values()),
        "surface_types": len(surface_counts),
        "always_omitted_types": len(always_omitted),
        "always_omitted_occurrences": sum(always_omitted.values()),
        "partially_omitted_types": len(partially_omitted),
        "never_omitted_types": len(never_omitted),
        "always_omitted_type_inventory": [
            {"token": token, "occurrences": count}
            for token, count in sorted(always_omitted.items(), key=lambda item: (-item[1], item[0]))
        ],
    }
    check(result["type_determinism"] == expected_type_determinism, "type determinism artifact mismatch")

    by_locus: dict[str, dict[str, RowView]] = defaultdict(dict)
    for (edition, locus), view in views.items():
        by_locus[locus][edition] = view

    pair_counts: Counter[str] = Counter()
    pair_loci: dict[str, set[str]] = defaultdict(set)
    for locus, edition_views in by_locus.items():
        for left_edition, right_edition in combinations(EDITIONS, 2):
            if left_edition not in edition_views or right_edition not in edition_views:
                continue
            left = edition_views[left_edition]
            right = edition_views[right_edition]
            if left.compact != right.compact:
                continue
            if left.tokens == right.tokens:
                pair_counts["exact_same_tokenization_pairs"] += 1
                pair_loci["exact_same_tokenization_loci"].add(locus)
                continue
            pair_counts["space_only_variant_pairs"] += 1
            pair_loci["space_only_variant_loci"].add(locus)
            if len(left.boundaries ^ right.boundaries) == 1:
                pair_counts["single_boundary_variant_pairs"] += 1
                pair_loci["single_boundary_variant_loci"].add(locus)
            else:
                pair_counts["multi_boundary_variant_pairs"] += 1
                pair_loci["multi_boundary_variant_loci"].add(locus)

    check(pair_counts["space_only_variant_pairs"] == 1_440, "space-only pair total")
    check(len(pair_loci["space_only_variant_loci"]) == 941, "space-only physical-locus total")
    check(pair_counts["single_boundary_variant_pairs"] == 1_188, "single-boundary pair total")
    check(pair_counts["multi_boundary_variant_pairs"] == 252, "multi-boundary pair total")
    artifact_cross = result["cross_reading_space_only"]
    check(artifact_cross["pair_counts"]["space_only_variant_pairs"] == 1_440, "artifact space-only pair total")
    check(artifact_cross["physical_locus_counts"]["space_only_variant_loci"] == 941, "artifact space-only locus total")
    check(artifact_cross["pair_counts"]["single_boundary_variant_pairs"] == 1_188, "artifact single-boundary total")

    reconstructed_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    direction_loci: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for (source_edition, locus), source in views.items():
        for source_position, token in source.omitted.items():
            if token not in CORE_TYPES:
                continue
            start = source.starts[source_position - 1]
            end = source.ends[source_position - 1]
            for other_edition in EDITIONS:
                if other_edition == source_edition or other_edition not in by_locus[locus]:
                    continue
                other = by_locus[locus][other_edition]
                if source.compact != other.compact:
                    continue
                fused_position = other.containing_position(start, end)
                if fused_position is None:
                    continue
                fused_start = other.starts[fused_position - 1]
                fused_end = other.ends[fused_position - 1]
                if fused_start == start and fused_end == end:
                    continue
                if fused_start < start and fused_end > end:
                    direction = "BOTH"
                elif fused_start < start:
                    direction = "LEFT"
                elif fused_end > end:
                    direction = "RIGHT"
                else:
                    raise AssertionError("strict containment has no fusion direction")

                removed_boundaries: set[int] = set()
                if fused_start < start and start > 0:
                    removed_boundaries.add(start)
                if fused_end > end and end < len(source.compact):
                    removed_boundaries.add(end)
                sole_boundary = (source.boundaries ^ other.boundaries) == removed_boundaries
                fused_mapping = other.mapping.get(fused_position)
                if direction == "LEFT":
                    neighbor_mapping = source.mapping.get(source_position - 1)
                elif direction == "RIGHT":
                    neighbor_mapping = source.mapping.get(source_position + 1)
                else:
                    neighbor_mapping = None
                preserved = (
                    fused_mapping is not None
                    and neighbor_mapping is not None
                    and fused_mapping == neighbor_mapping
                )
                direction_key = f"{source_edition}->{other_edition}"
                direction_loci[token][direction_key].add(locus)
                reconstructed_events[token].append({
                    "token": token,
                    "locus": locus,
                    "source_edition": source_edition,
                    "other_edition": other_edition,
                    "source_position_1based": source_position,
                    "fused_position_1based": fused_position,
                    "direction": direction,
                    "fused": other.tokens[fused_position - 1],
                    "fused_mapping": list(fused_mapping) if fused_mapping is not None else None,
                    "neighbor_mapping": list(neighbor_mapping) if neighbor_mapping is not None else None,
                    "neighbor_mapping_preserved": preserved,
                    "sole_boundary_change": sole_boundary,
                })

    reconstructed_summary: dict[str, dict[str, Any]] = {}
    for token in CORE_TYPES:
        events = reconstructed_events[token]
        directions = Counter(event["direction"] for event in events)
        source_to_other = Counter(
            f"{event['source_edition']}->{event['other_edition']}" for event in events
        )
        sole = [event for event in events if event["sole_boundary_change"]]
        eligible = [
            event for event in sole
            if event["fused_mapping"] is not None and event["neighbor_mapping"] is not None
        ]
        reconstructed_summary[token] = {
            "events": len(events),
            "physical_loci": len({event["locus"] for event in events}),
            "direction": {name: directions[name] for name in ("BOTH", "LEFT", "RIGHT")},
            "source_to_other_reading": dict(sorted(source_to_other.items())),
            "fused_outcome_is_parsed_events": sum(event["fused_mapping"] is not None for event in events),
            "neighbor_mapping_preserved_events": sum(event["neighbor_mapping_preserved"] for event in events),
            "sole_boundary_change_events": len(sole),
            "sole_boundary_eligible_neighbor_mapping_events": len(eligible),
            "sole_boundary_neighbor_mapping_preserved_events": sum(
                event["neighbor_mapping_preserved"] for event in eligible
            ),
        }

        constants_without_loci = {
            key: value for key, value in EXPECTED_CORE[token].items()
            if key != "direction_loci"
        }
        check(reconstructed_summary[token] == constants_without_loci, f"{token} core constants")
        reconstructed_direction_loci = {
            direction: len(loci)
            for direction, loci in sorted(direction_loci[token].items())
        }
        check(
            reconstructed_direction_loci == EXPECTED_CORE[token]["direction_loci"],
            f"{token} direction-specific locus constants",
        )

        artifact_summary = artifact_cross["directed_residual_fusion_summary"][token]
        artifact_without_details = {
            key: value for key, value in artifact_summary.items()
            if key != "events_detail"
        }
        check(
            artifact_without_details == reconstructed_summary[token],
            f"{token} artifact summary mismatch",
        )
        expected_events = sorted(canonical(event) for event in events)
        artifact_events = sorted(canonical(event) for event in artifact_summary["events_detail"])
        check(artifact_events == expected_events, f"{token} event identity mismatch")

    core_events = sum(reconstructed_summary[token]["events"] for token in CORE_TYPES)
    core_loci = {
        event["locus"]
        for token in CORE_TYPES for event in reconstructed_events[token]
    }
    check(core_events == artifact_cross["core_y_dy_ky_sy_fusion_events"] == 280, "core event total")
    check(len(core_loci) == artifact_cross["core_y_dy_ky_sy_fusion_physical_loci"] == 177, "core locus total")

    expected_gates = {
        "at_least_one_space_only_single_boundary_variant": pair_counts["single_boundary_variant_pairs"] > 0,
        "core_fusion_events_reconstruct_expected_280": core_events == 280,
        "exact_token_identity_determines_frozen_parser_omission": (
            len(always_omitted) == 28 and not partially_omitted
        ),
        "sole_boundary_y_preserves_neighbor_mapping_130_of_130": (
            reconstructed_summary["y"]["sole_boundary_eligible_neighbor_mapping_events"] == 130
            and reconstructed_summary["y"]["sole_boundary_neighbor_mapping_preserved_events"] == 130
        ),
        "y_is_boundary_mobile_not_suffix_only": (
            reconstructed_summary["y"]["direction"]["LEFT"] > 0
            and reconstructed_summary["y"]["direction"]["RIGHT"] > 0
        ),
    }
    check(all(expected_gates.values()), "reconstructed decision gate failure")
    check(result["gates"] == expected_gates, "artifact decision gates")
    check(result["status"] == EXPECTED_STATUS, "status mismatch")
    check(result["decision"] == EXPECTED_DECISION, "decision mismatch")
    check(result["claim_ceiling"] == EXPECTED_CLAIM, "claim ceiling mismatch")
    check(result["next_test"] == EXPECTED_NEXT_TEST, "next-test mismatch")
    check(result["english_lexical_glosses"] == 0, "lexical gloss ceiling")
    check(
        result["input_sha256"] == {
            "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv":
                EXPECTED_SHA256["experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"],
            "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv":
                EXPECTED_SHA256["experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv"],
        },
        "result input hashes",
    )

    validation = {
        "status": "PASS_INDEPENDENT_UNPARSED_SURFACE_SEGMENTATION_RECONSTRUCTION",
        "checks": checks,
        "artifact_sha256": observed_hashes,
        "type_determinism": {
            "surface_groups": 118_011,
            "surface_types": 10_909,
            "always_omitted_types": 28,
            "always_omitted_occurrences": 3_838,
            "partially_omitted_types": 0,
            "never_omitted_types": 10_881,
        },
        "cross_reading_space_only": {
            "variant_pairs": pair_counts["space_only_variant_pairs"],
            "physical_loci": len(pair_loci["space_only_variant_loci"]),
            "single_boundary_pairs": pair_counts["single_boundary_variant_pairs"],
            "multi_boundary_pairs": pair_counts["multi_boundary_variant_pairs"],
        },
        "core_directed_fusions": {
            "events": core_events,
            "physical_loci": len(core_loci),
            "by_token": {
                token: {
                    **reconstructed_summary[token],
                    "direction_loci": EXPECTED_CORE[token]["direction_loci"],
                }
                for token in CORE_TYPES
            },
        },
        "gates": expected_gates,
        "decision": EXPECTED_DECISION,
        "claim_ceiling": EXPECTED_CLAIM,
        "english_lexical_glosses": 0,
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_text = f"""# UNPARSED_SURFACE segmentation independent validation

Status: **{validation['status']}**.

A clean-room implementation that does not import the producer reconstructed
all {validation['type_determinism']['surface_groups']:,} surface groups,
{validation['type_determinism']['surface_types']:,} exact types, the exact
28-type / 3,838-occurrence deterministic omission inventory, and zero partly
omitted types.

It independently recovered {pair_counts['space_only_variant_pairs']:,}
space-only reading pairs on {len(pair_loci['space_only_variant_loci']):,}
physical loci, including {pair_counts['single_boundary_variant_pairs']:,}
single-boundary pairs. Character-offset containment reconstructed all 280 core
directed events and all event identities: `y` 188 / 128 loci, `dy` 68 / 40,
`ky` 22 / 14, and `sy` 2 / 1, together with every edition direction and its
physical-locus cardinality.

For sole-boundary events with parsed fused and neighboring occurrences, the
independent retained-position mapping gives 130/130 preservation for `y`,
versus 0/40 for `dy`, 0/12 for `ky`, and 0/1 for `sy`. The producer result,
decision gates, claim ceiling, input hashes, and exact report hash all match
the frozen contract.

This validates inventory arithmetic and binding only. Alternate readings are
not independent samples; no preferred spacing, authorial boundary, suffix,
morpheme, separator, sound, number, word, plaintext, or meaning follows.
"""
    OUTPUT_REPORT.write_text(report_text, encoding="utf-8")
    print(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
