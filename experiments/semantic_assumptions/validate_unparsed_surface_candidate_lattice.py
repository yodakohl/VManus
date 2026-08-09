#!/usr/bin/env python3
"""Clean-room validation of the UNPARSED_SURFACE candidate inventory.

This validator deliberately does not import the producer.  It independently
reparses the frozen interlinear and residual atlas, rebuilds the retained-node
surface-to-root/role inventory, aggregates direct alternate-reading witnesses,
and reconstructs every serialized candidate and summary.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
SEGMENTATION = RESULTS / "unparsed_surface_segmentation.json"
PRODUCER = HERE / "build_unparsed_surface_candidate_lattice.py"
LATTICE = RESULTS / "unparsed_surface_candidate_lattice.tsv"
RESULT = RESULTS / "unparsed_surface_candidate_lattice.json"
REPORT = RESULTS / "unparsed_surface_candidate_lattice_report.md"
OUTPUT = RESULTS / "unparsed_surface_candidate_lattice_validation.json"
OUTPUT_REPORT = RESULTS / "unparsed_surface_candidate_lattice_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
PRESERVING = "PARSER_MAPPING_PRESERVING_ATTESTED"
CHANGING = "PARSER_MAPPING_CHANGING_ATTESTED"
UNRESOLVED = "NO_ADJACENT_ATTESTED_FUSION"
SAME = "NEUTRAL_SAME_AS_NEIGHBOR"
REPLACEMENT = "REPLACEMENT_ATTESTED"

EXPECTED_SHA256 = {
    "experiments/semantic_assumptions/build_unparsed_surface_candidate_lattice.py":
        "3f121152343e65a5d418e5159e413d30a04b75199d77a141e8b064e1f8ad0b59",
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv":
        "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv":
        "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    "experiments/semantic_assumptions/results/unparsed_surface_segmentation.json":
        "fb003077191a98ef4a8c16b996552ed4fd635f93e1bb26109716f554cf46ea97",
    "experiments/semantic_assumptions/results/unparsed_surface_candidate_lattice.tsv":
        "2b39b60c3bc4348490bd54a2a1965201e9d9eb625c98c3b5c9736b7f96ab12f1",
    "experiments/semantic_assumptions/results/unparsed_surface_candidate_lattice.json":
        "62fe18a37d058c6100dc811aef0294770c5d22d056cb4fac6d6abd47953a0ef6",
    "experiments/semantic_assumptions/results/unparsed_surface_candidate_lattice_report.md":
        "9c7e3b1c0893005bea48bb99e95817243461b6621ac2a82178353bae8c57c51a",
}

INTERLINEAR_FIELDS = [
    "edition", "locus", "page", "section", "currier", "hand", "code", "kind",
    "grammar_scope", "paragraph_state", "line_carrier", "word_count", "surface",
    "root_sequence", "role_sequence", "formal_interlinear", "confirmed_edges",
    "core34_covered_words", "hybrid95_covered_words",
]
RESIDUAL_FIELDS = [
    "edition", "locus", "page", "grammar_scope", "kind", "surface_token_count",
    "parsed_node_count", "omitted_token_count", "omitted_positions_1based",
    "omitted_tokens", "position_token_pairs",
]
LATTICE_FIELDS = [
    "event_id", "edition", "locus", "page", "surface_position_1based",
    "residual_token", "coverage_class", "neutral_directions",
    "replacement_directions", "candidate_count",
    "mapping_preserving_has_other_locus_witness",
    "mapping_preserving_has_same_edition_witness",
    "direct_same_locus_witness_directions",
    "direct_sole_boundary_mapping_preserving_directions", "candidate_json",
]
CANDIDATE_FIELDS = {
    "direction", "fused_surface", "root", "role", "mapping_relation",
    "neighbor_surface", "neighbor_mapping", "has_other_physical_locus_witness",
    "has_same_edition_witness", "direct_same_locus_alternate_reading_witness",
    "direct_sole_boundary_mapping_preserving_witness",
}
RESULT_FIELDS = {
    "candidate_tsv_sha256", "claim_ceiling", "decision", "english_lexical_glosses",
    "gates", "input_sha256", "status", "totals", "type_summary",
}
TOTAL_FIELDS = {
    "events", "physical_loci", "parser_mapping_preserving_attested",
    "parser_mapping_changing_attested", "unresolved",
    "mapping_preserving_has_other_locus_witness",
    "mapping_preserving_lacks_other_locus_witness",
    "mapping_preserving_has_same_edition_witness",
}
GATE_FIELDS = {
    "exact_residual_event_key_set_represented_once",
    "every_candidate_mapping_is_exactly_attested",
    "candidate_schema_contains_no_selected_parse",
}
TYPE_SUMMARY_FIELDS = {
    "events", "parser_mapping_preserving_attested",
    "parser_mapping_changing_attested", "unresolved", "left_neutral",
    "right_neutral", "both_neutral", "left_replacement", "right_replacement",
    "by_edition", "mapping_preserving_by_edition",
    "mapping_preserving_has_other_locus_witness",
    "mapping_preserving_has_same_edition_witness",
    "mapping_preserving_has_direct_same_locus_witness",
    "physical_loci_by_coverage",
}

EXPECTED_STATUS = "PASS_FROZEN_PARTIAL_PARSER_ONE_SIDED_COMPATIBILITY_INVENTORY"
EXPECTED_DECISION = "DESCRIPTIVE_PARSER_INTERNAL_COMPATIBILITY_ONLY"
EXPECTED_CLAIM = (
    "This conservative one-event, one-neighbor inventory records only exact adjacent fused "
    "surfaces and root/role mappings already attested in the same unavailable frozen partial "
    "parser. Mapping-preserving cases are parser-internal compatibility, not neutral evidence "
    "between manuscript parses. Adjacent residual runs and simultaneous two-sided or multi-group "
    "fusions are not modeled. No candidate is selected as authorial, and no operator, suffix, "
    "morphology, sound, word, plaintext, or meaning is established."
)

EXPECTED_TOTALS = {
    "events": 3_838,
    "physical_loci": 1_808,
    "parser_mapping_preserving_attested": 2_178,
    "parser_mapping_changing_attested": 414,
    "unresolved": 1_246,
    "mapping_preserving_has_other_locus_witness": 2_100,
    "mapping_preserving_lacks_other_locus_witness": 78,
    "mapping_preserving_has_same_edition_witness": 2_050,
}
EXPECTED_Y = {
    "events": 2_463,
    "parser_mapping_preserving_attested": 2_117,
    "parser_mapping_changing_attested": 0,
    "unresolved": 346,
    "left_neutral": 1_865,
    "right_neutral": 824,
    "both_neutral": 572,
    "mapping_preserving_by_edition": {"ZL3b": 269, "IT2a": 100, "RF1b": 1_748},
    "mapping_preserving_has_other_locus_witness": 2_058,
    "mapping_preserving_has_same_edition_witness": 2_022,
    "mapping_preserving_has_direct_same_locus_witness": 134,
}


class ContractError(AssertionError):
    """Raised for a clean-room input or artifact contract violation."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_tsv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != fields:
            raise ContractError(f"TSV schema mismatch at {path.name}")
        return list(reader)


def encode_mapping(mapping: tuple[str, str]) -> str:
    return f"{mapping[0]}[{mapping[1]}]"


def parse_residual_contract(
    residual_rows: list[dict[str, str]],
    row_index: dict[tuple[str, str], dict[str, str]],
    *,
    exact_size: bool = True,
) -> tuple[
    dict[tuple[str, str], set[int]],
    dict[tuple[str, str, int], str],
]:
    residual_at: dict[tuple[str, str], set[int]] = {}
    events: dict[tuple[str, str, int], str] = {}
    for row in residual_rows:
        key = (row["edition"], row["locus"])
        if key not in row_index:
            raise ContractError("residual key absent from interlinear")
        if key in residual_at:
            raise ContractError("duplicate residual row key")
        source = row_index[key]
        if (
            row["page"] != source["page"]
            or row["grammar_scope"] != source["grammar_scope"]
            or row["kind"] != source["kind"]
        ):
            raise ContractError("residual metadata mismatch")
        try:
            positions = [int(value) for value in row["omitted_positions_1based"].split(";")]
            omitted_count = int(row["omitted_token_count"])
            surface_count = int(row["surface_token_count"])
            parsed_count = int(row["parsed_node_count"])
        except ValueError as exc:
            raise ContractError("noninteger residual count/position") from exc
        tokens = row["omitted_tokens"].split()
        surface = source["surface"].split()
        if len(positions) != len(tokens) or len(tokens) != omitted_count:
            raise ContractError("residual event cardinality mismatch")
        if len(set(positions)) != len(positions):
            raise ContractError("duplicate residual event position")
        if surface_count != len(surface) or parsed_count + omitted_count != len(surface):
            raise ContractError("residual surface partition mismatch")
        expected_pairs = ";".join(
            f"{position}:{token}" for position, token in zip(positions, tokens)
        )
        if row["position_token_pairs"] != expected_pairs:
            raise ContractError("position-token serialization mismatch")
        for position, token in zip(positions, tokens):
            if not 1 <= position <= len(surface):
                raise ContractError("residual position outside surface")
            if surface[position - 1] != token:
                raise ContractError("residual token does not occupy declared position")
            event_key = (key[0], key[1], position)
            if event_key in events:
                raise ContractError("duplicate residual event key")
            events[event_key] = token
        residual_at[key] = set(positions)
    if exact_size and (len(residual_rows) != 2_833 or len(events) != 3_838):
        raise ContractError("residual atlas exact cardinality mismatch")
    return residual_at, events


def build_formal_inventory(
    rows: list[dict[str, str]],
    residual_at: dict[tuple[str, str], set[int]],
) -> tuple[
    dict[str, set[tuple[str, str]]],
    dict[tuple[str, str], list[tuple[str, str] | None]],
    dict[tuple[str, tuple[str, str]], set[tuple[str, str, int]]],
]:
    inventory: dict[str, set[tuple[str, str]]] = defaultdict(set)
    position_mappings: dict[tuple[str, str], list[tuple[str, str] | None]] = {}
    witnesses: dict[
        tuple[str, tuple[str, str]], set[tuple[str, str, int]]
    ] = defaultdict(set)
    for row in rows:
        key = (row["edition"], row["locus"])
        surface = row["surface"].split()
        roots = row["root_sequence"].split()
        roles = row["role_sequence"].split()
        formal_surfaces = (
            [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]
            if row["formal_interlinear"] else []
        )
        if not len(formal_surfaces) == len(roots) == len(roles) == int(row["word_count"]):
            raise ContractError("formal tuple cardinality mismatch")
        values: list[tuple[str, str] | None] = []
        formal_index = 0
        for position, token in enumerate(surface, 1):
            if position in residual_at.get(key, set()):
                values.append(None)
                continue
            if formal_index >= len(formal_surfaces) or token != formal_surfaces[formal_index]:
                raise ContractError("formal surface alignment mismatch")
            mapping = (roots[formal_index], roles[formal_index])
            inventory[token].add(mapping)
            witnesses[(token, mapping)].add((row["edition"], row["locus"], position))
            values.append(mapping)
            formal_index += 1
        if formal_index != len(formal_surfaces):
            raise ContractError("formal sequence exhaustion mismatch")
        position_mappings[key] = values
    return inventory, position_mappings, witnesses


def build_direct_witnesses(
    segmentation: dict[str, Any],
) -> tuple[
    dict[tuple[str, str, int, str, str, str], list[dict[str, Any]]],
    int,
    int,
    int,
]:
    try:
        summaries = segmentation["cross_reading_space_only"][
            "directed_residual_fusion_summary"
        ]
    except (KeyError, TypeError) as exc:
        raise ContractError("segmentation direct-witness schema mismatch") from exc
    if not isinstance(summaries, dict):
        raise ContractError("segmentation directed summary is not an object")
    grouped: dict[
        tuple[str, str, int, str, str, str], list[dict[str, Any]]
    ] = defaultdict(list)
    base_groups: dict[
        tuple[str, str, int, str, str], list[dict[str, Any]]
    ] = defaultdict(list)
    event_count = 0
    required = {
        "source_edition", "locus", "source_position_1based", "token", "direction",
        "fused", "sole_boundary_change", "neighbor_mapping_preserved",
    }
    for token, summary in summaries.items():
        if not isinstance(summary, dict) or not isinstance(summary.get("events_detail"), list):
            raise ContractError("segmentation token summary schema mismatch")
        for event in summary["events_detail"]:
            if not isinstance(event, dict) or not required <= set(event):
                raise ContractError("segmentation direct event schema mismatch")
            if event["token"] != token or event["direction"] not in {"LEFT", "RIGHT", "BOTH"}:
                raise ContractError("segmentation direct event identity mismatch")
            if type(event["sole_boundary_change"]) is not bool:
                raise ContractError("segmentation sole-boundary flag is not boolean")
            if type(event["neighbor_mapping_preserved"]) is not bool:
                raise ContractError("segmentation mapping-preserved flag is not boolean")
            key = (
                str(event["source_edition"]), str(event["locus"]),
                int(event["source_position_1based"]), str(event["token"]),
                str(event["direction"]), str(event["fused"]),
            )
            grouped[key].append(event)
            base_groups[key[:-1]].append(event)
            event_count += 1
    return (
        grouped,
        event_count,
        len(base_groups),
        sum(len(events) > 1 for events in base_groups.values()),
    )


def enumerate_candidates(
    *,
    edition: str,
    locus: str,
    position: int,
    token: str,
    surface: list[str],
    mappings: list[tuple[str, str] | None],
    inventory: dict[str, set[tuple[str, str]]],
    witnesses: dict[tuple[str, tuple[str, str]], set[tuple[str, str, int]]],
    direct_witnesses: dict[
        tuple[str, str, int, str, str, str], list[dict[str, Any]]
    ],
) -> list[dict[str, Any]]:
    alternatives: list[dict[str, Any]] = []
    specifications = (
        ("LEFT", position - 2, surface[position - 2] + token if position > 1 else ""),
        ("RIGHT", position, token + surface[position] if position < len(surface) else ""),
    )
    for direction, neighbor_index, fused_surface in specifications:
        if not fused_surface or neighbor_index < 0 or neighbor_index >= len(surface):
            continue
        neighbor_mapping = mappings[neighbor_index]
        if neighbor_mapping is None:
            continue
        for candidate_mapping in sorted(inventory.get(fused_surface, set())):
            mapping_witnesses = witnesses[(fused_surface, candidate_mapping)]
            direct = direct_witnesses.get(
                (edition, locus, position, token, direction, fused_surface), []
            )
            if direct and any(str(item["fused"]) != fused_surface for item in direct):
                raise ContractError("direct witness fused surface mismatch")
            alternatives.append({
                "direction": direction,
                "fused_surface": fused_surface,
                "root": candidate_mapping[0],
                "role": candidate_mapping[1],
                "mapping_relation": SAME if candidate_mapping == neighbor_mapping else REPLACEMENT,
                "neighbor_surface": surface[neighbor_index],
                "neighbor_mapping": encode_mapping(neighbor_mapping),
                "has_other_physical_locus_witness": any(
                    witness_locus != locus for _, witness_locus, _ in mapping_witnesses
                ),
                "has_same_edition_witness": any(
                    witness_edition == edition for witness_edition, _, _ in mapping_witnesses
                ),
                "direct_same_locus_alternate_reading_witness": bool(direct),
                "direct_sole_boundary_mapping_preserving_witness": any(
                    bool(item["sole_boundary_change"])
                    and bool(item["neighbor_mapping_preserved"])
                    for item in direct
                ),
            })
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for alternative in alternatives:
        encoded = json.dumps(alternative, sort_keys=True, separators=(",", ":"))
        if encoded not in seen:
            seen.add(encoded)
            deduped.append(alternative)
    return deduped


def expect_rejection(action: Callable[[], object], label: str) -> str:
    try:
        action()
    except ContractError as exc:
        return f"PASS:{label}:{exc}"
    raise ContractError(f"mutation was not rejected: {label}")


def main() -> None:
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        if not condition:
            raise ContractError(message)
        checks += 1

    path_index = {relative: REPO / relative for relative in EXPECTED_SHA256}
    observed_hashes = {relative: sha256(path) for relative, path in path_index.items()}
    check(observed_hashes == EXPECTED_SHA256, "frozen source/artifact hash mismatch")

    rows = read_tsv(INTERLINEAR, INTERLINEAR_FIELDS)
    residual_rows = read_tsv(RESIDUAL, RESIDUAL_FIELDS)
    lattice_rows = read_tsv(LATTICE, LATTICE_FIELDS)
    check(len(rows) == 15_960, "interlinear row count mismatch")
    row_index = {(row["edition"], row["locus"]): row for row in rows}
    check(len(row_index) == len(rows), "interlinear identity duplication")

    residual_at, residual_events = parse_residual_contract(residual_rows, row_index)
    check(len(residual_at) == 2_833, "residual row identity count mismatch")
    check(len(residual_events) == 3_838, "residual event identity count mismatch")

    inventory, position_mappings, mapping_witnesses = build_formal_inventory(
        rows, residual_at
    )
    segmentation = json.loads(SEGMENTATION.read_text(encoding="utf-8"))
    (
        direct_witnesses,
        direct_event_count,
        direct_base_key_count,
        direct_base_duplicate_count,
    ) = build_direct_witnesses(segmentation)
    check(direct_event_count == 312, "direct witness event count mismatch")
    check(direct_base_key_count == 253, "direct witness base-key count mismatch")
    check(direct_base_duplicate_count == 59, "direct witness duplicate base-key count mismatch")
    check(len(direct_witnesses) == 256, "exact-surface direct witness key count mismatch")
    check(
        sum(len(events) > 1 for events in direct_witnesses.values()) == 56,
        "exact-surface direct witness duplicate-key group count mismatch",
    )

    reconstructed_rows: list[dict[str, str]] = []
    type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    type_loci: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    every_mapping_attested = True
    for edition, locus, position in sorted(residual_events):
        source = row_index[(edition, locus)]
        token = residual_events[(edition, locus, position)]
        surface = source["surface"].split()
        alternatives = enumerate_candidates(
            edition=edition,
            locus=locus,
            position=position,
            token=token,
            surface=surface,
            mappings=position_mappings[(edition, locus)],
            inventory=inventory,
            witnesses=mapping_witnesses,
            direct_witnesses=direct_witnesses,
        )
        for item in alternatives:
            check(set(item) == CANDIDATE_FIELDS, "candidate schema mismatch")
            check(item["direction"] in {"LEFT", "RIGHT"}, "candidate direction mismatch")
            check(item["mapping_relation"] in {SAME, REPLACEMENT}, "mapping relation mismatch")
            for flag in (
                "has_other_physical_locus_witness", "has_same_edition_witness",
                "direct_same_locus_alternate_reading_witness",
                "direct_sole_boundary_mapping_preserving_witness",
            ):
                check(type(item[flag]) is bool, f"candidate {flag} is not boolean")
            every_mapping_attested &= (
                (str(item["root"]), str(item["role"]))
                in inventory[str(item["fused_surface"])]
            )
        neutral_directions = sorted({
            str(item["direction"]) for item in alternatives
            if item["mapping_relation"] == SAME
        })
        replacement_directions = sorted({
            str(item["direction"]) for item in alternatives
            if item["mapping_relation"] == REPLACEMENT
        })
        preserving_alternatives = [
            item for item in alternatives if item["mapping_relation"] == SAME
        ]
        coverage = (
            PRESERVING if neutral_directions else
            CHANGING if replacement_directions else UNRESOLVED
        )
        counts = type_counts[token]
        counts.update({
            "events": 1,
            f"coverage:{coverage}": 1,
            "left_neutral": int("LEFT" in neutral_directions),
            "right_neutral": int("RIGHT" in neutral_directions),
            "both_neutral": int(set(neutral_directions) == {"LEFT", "RIGHT"}),
            "left_replacement": int("LEFT" in replacement_directions),
            "right_replacement": int("RIGHT" in replacement_directions),
            f"edition:{edition}": 1,
            f"preserving_edition:{edition}": int(coverage == PRESERVING),
            "preserving_has_other_locus_witness": int(any(
                bool(item["has_other_physical_locus_witness"])
                for item in preserving_alternatives
            )),
            "preserving_has_same_edition_witness": int(any(
                bool(item["has_same_edition_witness"])
                for item in preserving_alternatives
            )),
            "preserving_has_direct_same_locus_witness": int(any(
                bool(item["direct_same_locus_alternate_reading_witness"])
                for item in preserving_alternatives
            )),
        })
        type_loci[token][coverage].add(locus)
        reconstructed_rows.append({
            "event_id": f"{edition}|{locus}|{position}",
            "edition": edition,
            "locus": locus,
            "page": source["page"],
            "surface_position_1based": str(position),
            "residual_token": token,
            "coverage_class": coverage,
            "neutral_directions": ";".join(neutral_directions),
            "replacement_directions": ";".join(replacement_directions),
            "candidate_count": str(len(alternatives)),
            "mapping_preserving_has_other_locus_witness": str(int(any(
                bool(item["has_other_physical_locus_witness"])
                for item in preserving_alternatives
            ))),
            "mapping_preserving_has_same_edition_witness": str(int(any(
                bool(item["has_same_edition_witness"])
                for item in preserving_alternatives
            ))),
            "direct_same_locus_witness_directions": ";".join(sorted({
                str(item["direction"]) for item in preserving_alternatives
                if item["direct_same_locus_alternate_reading_witness"]
            })),
            "direct_sole_boundary_mapping_preserving_directions": ";".join(sorted({
                str(item["direction"]) for item in preserving_alternatives
                if item["direct_sole_boundary_mapping_preserving_witness"]
            })),
            "candidate_json": json.dumps(
                alternatives, sort_keys=True, separators=(",", ":")
            ),
        })

    check(len(lattice_rows) == 3_838, "candidate TSV row count mismatch")
    actual_event_ids = [row["event_id"] for row in lattice_rows]
    expected_event_ids = {
        f"{edition}|{locus}|{position}" for edition, locus, position in residual_events
    }
    check(len(actual_event_ids) == len(set(actual_event_ids)), "duplicate output event ID")
    check(set(actual_event_ids) == expected_event_ids, "output event-key set mismatch")
    check(lattice_rows == reconstructed_rows, "candidate TSV reconstruction mismatch")
    check(every_mapping_attested, "candidate uses unattested root/role mapping")

    coverage_counts = Counter(row["coverage_class"] for row in reconstructed_rows)
    summaries: dict[str, Any] = {}
    for token in sorted(type_counts, key=lambda item: (-type_counts[item]["events"], item)):
        counts = type_counts[token]
        summary = {
            "events": counts["events"],
            "parser_mapping_preserving_attested": counts[f"coverage:{PRESERVING}"],
            "parser_mapping_changing_attested": counts[f"coverage:{CHANGING}"],
            "unresolved": counts[f"coverage:{UNRESOLVED}"],
            "left_neutral": counts["left_neutral"],
            "right_neutral": counts["right_neutral"],
            "both_neutral": counts["both_neutral"],
            "left_replacement": counts["left_replacement"],
            "right_replacement": counts["right_replacement"],
            "by_edition": {
                edition: counts[f"edition:{edition}"] for edition in EDITIONS
            },
            "mapping_preserving_by_edition": {
                edition: counts[f"preserving_edition:{edition}"] for edition in EDITIONS
            },
            "mapping_preserving_has_other_locus_witness": counts[
                "preserving_has_other_locus_witness"
            ],
            "mapping_preserving_has_same_edition_witness": counts[
                "preserving_has_same_edition_witness"
            ],
            "mapping_preserving_has_direct_same_locus_witness": counts[
                "preserving_has_direct_same_locus_witness"
            ],
            "physical_loci_by_coverage": {
                name: len(type_loci[token][name])
                for name in (PRESERVING, CHANGING, UNRESOLVED)
            },
        }
        check(set(summary) == TYPE_SUMMARY_FIELDS, "type-summary schema mismatch")
        check(set(summary["by_edition"]) == set(EDITIONS), "edition schema mismatch")
        check(
            set(summary["mapping_preserving_by_edition"]) == set(EDITIONS),
            "preserving edition schema mismatch",
        )
        check(
            set(summary["physical_loci_by_coverage"]) == {PRESERVING, CHANGING, UNRESOLVED},
            "physical-locus coverage schema mismatch",
        )
        summaries[token] = summary

    preserving_count = coverage_counts[PRESERVING]
    changing_count = coverage_counts[CHANGING]
    preserving_other_locus = sum(
        row["mapping_preserving_has_other_locus_witness"] == "1"
        for row in reconstructed_rows
    )
    preserving_same_edition = sum(
        row["mapping_preserving_has_same_edition_witness"] == "1"
        for row in reconstructed_rows
    )
    reconstructed_totals = {
        "events": len(reconstructed_rows),
        "physical_loci": len({row["locus"] for row in reconstructed_rows}),
        "parser_mapping_preserving_attested": preserving_count,
        "parser_mapping_changing_attested": changing_count,
        "unresolved": coverage_counts[UNRESOLVED],
        "mapping_preserving_has_other_locus_witness": preserving_other_locus,
        "mapping_preserving_lacks_other_locus_witness": (
            preserving_count - preserving_other_locus
        ),
        "mapping_preserving_has_same_edition_witness": preserving_same_edition,
    }
    check(reconstructed_totals == EXPECTED_TOTALS, "registered total mismatch")
    y = summaries["y"]
    for key, expected in EXPECTED_Y.items():
        check(y[key] == expected, f"registered y metric mismatch: {key}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(set(result) == RESULT_FIELDS, "result top-level schema mismatch")
    check(set(result["totals"]) == TOTAL_FIELDS, "result totals schema mismatch")
    check(set(result["gates"]) == GATE_FIELDS, "result gates schema mismatch")
    check(set(result["type_summary"]) == set(summaries), "result type inventory mismatch")
    check(result["status"] == EXPECTED_STATUS, "result status mismatch")
    check(result["decision"] == EXPECTED_DECISION, "result decision mismatch")
    check(result["claim_ceiling"] == EXPECTED_CLAIM, "result claim ceiling mismatch")
    check(result["english_lexical_glosses"] == 0, "nonzero English lexical gloss count")

    expected_input_hashes = {
        relative: EXPECTED_SHA256[relative]
        for relative in (
            "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv",
            "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv",
            "experiments/semantic_assumptions/results/unparsed_surface_segmentation.json",
        )
    }
    reconstructed_result = {
        "status": EXPECTED_STATUS,
        "decision": EXPECTED_DECISION,
        "input_sha256": expected_input_hashes,
        "candidate_tsv_sha256": EXPECTED_SHA256[
            "experiments/semantic_assumptions/results/unparsed_surface_candidate_lattice.tsv"
        ],
        "totals": reconstructed_totals,
        "type_summary": summaries,
        "gates": {
            "exact_residual_event_key_set_represented_once": True,
            "every_candidate_mapping_is_exactly_attested": True,
            "candidate_schema_contains_no_selected_parse": True,
        },
        "claim_ceiling": EXPECTED_CLAIM,
        "english_lexical_glosses": 0,
    }
    check(result == reconstructed_result, "result JSON reconstruction mismatch")
    check(
        RESULT.read_text(encoding="utf-8")
        == json.dumps(reconstructed_result, indent=2, sort_keys=True) + "\n",
        "result JSON serialization mismatch",
    )

    expected_report = f"""# UNPARSED_SURFACE one-sided compatibility inventory

Decision: **DESCRIPTIVE FROZEN-PARSER COMPATIBILITY ONLY**.

All {len(reconstructed_rows):,} omitted surface events are retained.  Exact adjacent
fusion types already attested in the frozen formal snapshot supply at least one
parser-mapping-preserving candidate for {preserving_count:,} events and
mapping-changing candidates only for {changing_count:,};
{coverage_counts[UNRESOLVED]:,} remain unresolved.

Literal `y` has a mapping-preserving candidate at
{y['parser_mapping_preserving_attested']:,}/{y['events']:,} events: left at
{y['left_neutral']:,}, right at {y['right_neutral']:,}, and both at
{y['both_neutral']:,}.  “Both” means two separate one-sided alternatives, not
one simultaneous two-sided parse.  By contrast, `dy` has
{summaries['dy']['parser_mapping_changing_attested']:,} mapping-changing-only and
{summaries['dy']['parser_mapping_preserving_attested']:,} preserving events; `ky` has
{summaries['ky']['parser_mapping_changing_attested']:,} and
{summaries['ky']['parser_mapping_preserving_attested']:,}.

Of the {preserving_count:,} mapping-preserving events, {preserving_other_locus:,}
have a witness on another physical locus and {preserving_same_edition:,} have a
same-edition witness.  The aggregate is RF-heavy: `y` contributes
{y['mapping_preserving_by_edition']['RF1b']:,} RF,
{y['mapping_preserving_by_edition']['ZL3b']:,} ZL, and
{y['mapping_preserving_by_edition']['IT2a']:,} IT events.

This is not a complete segmentation lattice or a repaired parser.  It handles
one residual plus one retained neighbor, retains every unresolved group, and
assigns no English gloss.  Both omission and mapping labels come from the same
unavailable parser, so mapping preservation is circular and cannot adjudicate
the manuscript's grammar or authorial spacing.
"""
    check(REPORT.read_text(encoding="utf-8") == expected_report, "report reconstruction mismatch")
    check(
        "Adjacent residual runs and simultaneous two-sided or multi-group fusions are not modeled."
        in EXPECTED_CLAIM,
        "claim does not state adjacent/two-sided exclusions",
    )
    check(
        "not a complete segmentation lattice" in expected_report
        and "one residual plus one retained neighbor" in expected_report
        and "two separate one-sided alternatives" in expected_report,
        "report does not state one-sided/adjacent exclusions",
    )

    duplicate_rows = copy.deepcopy(residual_rows)
    duplicate = copy.deepcopy(duplicate_rows[0])
    duplicate_positions = duplicate["omitted_positions_1based"].split(";")
    duplicate_tokens = duplicate["omitted_tokens"].split()
    duplicate_positions.append(duplicate_positions[0])
    duplicate_tokens.append(duplicate_tokens[0])
    duplicate["omitted_positions_1based"] = ";".join(duplicate_positions)
    duplicate["omitted_tokens"] = " ".join(duplicate_tokens)
    duplicate["omitted_token_count"] = str(int(duplicate["omitted_token_count"]) + 1)
    duplicate["parsed_node_count"] = str(int(duplicate["parsed_node_count"]) - 1)
    duplicate["position_token_pairs"] = ";".join(
        f"{position}:{token}"
        for position, token in zip(duplicate_positions, duplicate_tokens)
    )
    duplicate_rows[0] = duplicate

    missing_rows = copy.deepcopy(residual_rows[:-1])

    wrong_position_rows = copy.deepcopy(residual_rows)
    wrong = copy.deepcopy(wrong_position_rows[0])
    wrong_positions = [int(value) for value in wrong["omitted_positions_1based"].split(";")]
    wrong_tokens = wrong["omitted_tokens"].split()
    wrong_surface = row_index[(wrong["edition"], wrong["locus"])]["surface"].split()
    replacement_position = next(
        position for position, surface_token in enumerate(wrong_surface, 1)
        if position not in wrong_positions and surface_token != wrong_tokens[0]
    )
    wrong_positions[0] = replacement_position
    wrong["omitted_positions_1based"] = ";".join(map(str, wrong_positions))
    wrong["position_token_pairs"] = ";".join(
        f"{position}:{token}" for position, token in zip(wrong_positions, wrong_tokens)
    )
    wrong_position_rows[0] = wrong

    mutation_guards = {
        "duplicate_event_rejected": expect_rejection(
            lambda: parse_residual_contract(duplicate_rows, row_index), "duplicate_event"
        ),
        "missing_event_rejected": expect_rejection(
            lambda: parse_residual_contract(missing_rows, row_index), "missing_event"
        ),
        "wrong_position_rejected": expect_rejection(
            lambda: parse_residual_contract(wrong_position_rows, row_index), "wrong_position"
        ),
    }

    synthetic_inventory = {
        "ay": {("A", "ROLE_A")},
        "dyb": {("B", "ROLE_B")},
        "yb": {("B", "ROLE_B")},
        "ayb": {("AB", "ROLE_AB")},
    }
    synthetic_witnesses = defaultdict(set, {
        (surface, mapping): {("ZL3b", "other.1", 1)}
        for surface, mappings in synthetic_inventory.items()
        for mapping in mappings
    })
    adjacent_left = enumerate_candidates(
        edition="ZL3b", locus="synthetic.1", position=2, token="y",
        surface=["a", "y", "dy", "b"],
        mappings=[("A", "ROLE_A"), None, None, ("B", "ROLE_B")],
        inventory=synthetic_inventory, witnesses=synthetic_witnesses,
        direct_witnesses={},
    )
    adjacent_right = enumerate_candidates(
        edition="ZL3b", locus="synthetic.1", position=3, token="dy",
        surface=["a", "y", "dy", "b"],
        mappings=[("A", "ROLE_A"), None, None, ("B", "ROLE_B")],
        inventory=synthetic_inventory, witnesses=synthetic_witnesses,
        direct_witnesses={},
    )
    check(
        {item["fused_surface"] for item in adjacent_left} == {"ay"}
        and {item["fused_surface"] for item in adjacent_right} == {"dyb"},
        "adjacent residual exclusion guard failed",
    )
    two_sided = enumerate_candidates(
        edition="ZL3b", locus="synthetic.2", position=2, token="y",
        surface=["a", "y", "b"],
        mappings=[("A", "ROLE_A"), None, ("B", "ROLE_B")],
        inventory=synthetic_inventory, witnesses=synthetic_witnesses,
        direct_witnesses={},
    )
    check(
        {item["fused_surface"] for item in two_sided} == {"ay", "yb"}
        and "ayb" not in {item["fused_surface"] for item in two_sided},
        "simultaneous two-sided exclusion guard failed",
    )

    validator_hash = sha256(Path(__file__))
    validation = {
        "status": "PASS_INDEPENDENT_UNPARSED_SURFACE_CANDIDATE_RECONSTRUCTION",
        "checks": checks,
        "artifact_sha256": observed_hashes,
        "validator_sha256": validator_hash,
        "production_claim_sha256": text_sha256(EXPECTED_CLAIM),
        "production_report_sha256": observed_hashes[
            "experiments/semantic_assumptions/results/unparsed_surface_candidate_lattice_report.md"
        ],
        "reconstruction": {
            "events": reconstructed_totals["events"],
            "physical_loci": reconstructed_totals["physical_loci"],
            "parser_mapping_preserving_attested": preserving_count,
            "parser_mapping_changing_attested": changing_count,
            "unresolved": coverage_counts[UNRESOLVED],
            "candidate_alternatives": sum(
                int(row["candidate_count"]) for row in reconstructed_rows
            ),
            "mapping_preserving_has_other_locus_witness": preserving_other_locus,
            "mapping_preserving_has_same_edition_witness": preserving_same_edition,
            "y": {key: y[key] for key in EXPECTED_Y},
        },
        "direct_witness_contract": {
            "source_events": direct_event_count,
            "source_event_direction_keys_before_exact_surface": direct_base_key_count,
            "source_event_direction_keys_with_multiple_counterpart_readings": (
                direct_base_duplicate_count
            ),
            "exact_surface_source_event_direction_keys": len(direct_witnesses),
            "exact_surface_keys_with_multiple_counterpart_readings": sum(
                len(events) > 1 for events in direct_witnesses.values()
            ),
            "aggregation": "EXACT_FUSED_SURFACE_THEN_EXISTENTIAL_ANY_COUNTERPART_READING",
            "four_previously_overwritten_y_right_witnesses_present": all(
                row["direct_sole_boundary_mapping_preserving_directions"] == "RIGHT"
                for row in reconstructed_rows
                if row["event_id"] in {
                    "ZL3b|f115v.28|1", "ZL3b|f16r.5|4",
                    "ZL3b|f79r.30|1", "ZL3b|f84v.24|1",
                }
            ),
        },
        "mutation_guards": mutation_guards,
        "scope_guards": {
            "adjacent_residual_neighbor_is_excluded": True,
            "simultaneous_two_sided_fusion_is_excluded": True,
            "exclusions_are_explicit_in_claim_and_report": True,
            "no_selected_parse_field": True,
        },
        "claim_ceiling": (
            "Validation confirms only the arithmetic, serialization, witness provenance, and "
            "one-sided frozen-partial-parser compatibility inventory. It does not repair or "
            "validate the unavailable parser and establishes no authorial boundary, grammar, "
            "morphology, sound, word, plaintext, or meaning."
        ),
        "english_lexical_glosses": 0,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_json_hash = sha256(OUTPUT)
    validation_report = f"""# UNPARSED_SURFACE candidate inventory independent validation

Status: **PASS INDEPENDENT CLEAN-ROOM RECONSTRUCTION**.

A nonimporting implementation reconstructed the exact {reconstructed_totals['events']:,}
reading-specific residual-event keys on {reconstructed_totals['physical_loci']:,} physical loci,
all serialized candidate alternatives, their attested root/role mappings, all witness flags,
the strict result schema, and the production report byte for byte.

The three classes reproduce exactly: {preserving_count:,} frozen-parser mapping-preserving,
{changing_count:,} mapping-changing only, and {coverage_counts[UNRESOLVED]:,} unresolved.
Literal `y` contributes {y['parser_mapping_preserving_attested']:,}/{y['events']:,}, with
left {y['left_neutral']:,}, right {y['right_neutral']:,}, and {y['both_neutral']:,} cases where two
separate one-sided alternatives exist. Its preserving edition counts are RF
{y['mapping_preserving_by_edition']['RF1b']:,}, ZL
{y['mapping_preserving_by_edition']['ZL3b']:,}, and IT
{y['mapping_preserving_by_edition']['IT2a']:,}.

The validator retained all {direct_event_count:,} direct alternate-reading witness records as
{len(direct_witnesses):,} exact-surface source-event/direction keys, using existential aggregation
across counterpart readings. All {sum(len(events) > 1 for events in direct_witnesses.values()):,}
multi-counterpart keys and the four corrected `y`-RIGHT witnesses agree with the artifact.

Duplicate-event, missing-event, and wrong-position mutations are rejected. Synthetic guards
confirm that an adjacent residual is not treated as a retained neighbor and that separate left
and right candidates never become a simultaneous two-sided fusion. Those exclusions and the
parser-circular claim ceiling are explicit in both production artifacts.

Validation JSON SHA-256: `{validation_json_hash}`.

This validates inventory arithmetic and provenance only. It does not reconstruct or validate
the missing parser and establishes no authorial spacing, grammar, morphology, sound, word,
plaintext, or meaning.
"""
    OUTPUT_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "checks": checks,
        "events": reconstructed_totals["events"],
        "candidate_alternatives": validation["reconstruction"]["candidate_alternatives"],
        "validation_json_sha256": validation_json_hash,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
