#!/usr/bin/env python3
"""Build conservative attested formal alternatives for omitted surface groups.

No new root or role is invented.  A residual group receives a candidate only
when joining it to an immediately adjacent retained group creates an exact
surface type whose root/role mapping is already attested elsewhere in the
frozen formal snapshot.  Alternatives remain a lattice; they are not resolved
into a single parse.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
SEGMENTATION = RESULTS / "unparsed_surface_segmentation.json"
OUTPUT_TSV = RESULTS / "unparsed_surface_candidate_lattice.tsv"
OUTPUT_JSON = RESULTS / "unparsed_surface_candidate_lattice.json"
OUTPUT_REPORT = RESULTS / "unparsed_surface_candidate_lattice_report.md"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    SEGMENTATION: "fb003077191a98ef4a8c16b996552ed4fd635f93e1bb26109716f554cf46ea97",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def formal_inventory(
    rows: list[dict[str, str]], residual_at: dict[tuple[str, str], set[int]]
) -> tuple[
    dict[str, set[tuple[str, str]]],
    dict[tuple[str, str], list[tuple[str, str] | None]],
    dict[tuple[str, tuple[str, str]], set[tuple[str, str, int]]],
]:
    inventory: dict[str, set[tuple[str, str]]] = defaultdict(set)
    positions: dict[tuple[str, str], list[tuple[str, str] | None]] = {}
    witnesses: dict[tuple[str, tuple[str, str]], set[tuple[str, str, int]]] = defaultdict(set)
    for row in rows:
        key = (row["edition"], row["locus"])
        surface = row["surface"].split()
        roots = row["root_sequence"].split()
        roles = row["role_sequence"].split()
        formal_surfaces = (
            [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]
            if row["formal_interlinear"] else []
        )
        if not (len(formal_surfaces) == len(roots) == len(roles)):
            raise RuntimeError(f"formal tuple drift at {key}")
        values: list[tuple[str, str] | None] = []
        formal_index = 0
        omitted = residual_at.get(key, set())
        for position, token in enumerate(surface, start=1):
            if position in omitted:
                values.append(None)
                continue
            if formal_index >= len(formal_surfaces) or token != formal_surfaces[formal_index]:
                raise RuntimeError(f"formal surface alignment drift at {key}")
            mapping = (roots[formal_index], roles[formal_index])
            values.append(mapping)
            inventory[token].add(mapping)
            witnesses[(token, mapping)].add((row["edition"], row["locus"], position))
            formal_index += 1
        if formal_index != len(formal_surfaces):
            raise RuntimeError(f"formal exhaustion drift at {key}")
        positions[key] = values
    return inventory, positions, witnesses


def encode_mapping(mapping: tuple[str, str]) -> str:
    return f"{mapping[0]}[{mapping[1]}]"


def main() -> None:
    observed = {path: digest(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError("candidate-lattice input drift")
    rows = load(INTERLINEAR)
    residual_rows = load(RESIDUAL)
    row_index = {(row["edition"], row["locus"]): row for row in rows}
    if len(row_index) != len(rows) or len(rows) != 15_960:
        raise RuntimeError("interlinear identity drift")

    residual_at: dict[tuple[str, str], set[int]] = {}
    residual_token_at: dict[tuple[str, str, int], str] = {}
    for row in residual_rows:
        key = (row["edition"], row["locus"])
        positions = [int(value) for value in row["omitted_positions_1based"].split(";")]
        tokens = row["omitted_tokens"].split()
        if not (len(positions) == len(tokens) == int(row["omitted_token_count"])):
            raise RuntimeError(f"residual count drift at {key}")
        residual_at[key] = set(positions)
        for position, token in zip(positions, tokens):
            residual_token_at[(key[0], key[1], position)] = token

    inventory, position_mappings, mapping_witnesses = formal_inventory(rows, residual_at)
    segmentation = json.loads(SEGMENTATION.read_text(encoding="utf-8"))
    direct_witnesses: dict[tuple[str, str, int, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for summary in segmentation["cross_reading_space_only"]["directed_residual_fusion_summary"].values():
        for event in summary["events_detail"]:
            direct_witnesses[(
                str(event["source_edition"]),
                str(event["locus"]),
                int(event["source_position_1based"]),
                str(event["token"]),
                str(event["direction"]),
                str(event["fused"]),
            )].append(event)
    lattice_rows = []
    type_summary: dict[str, Counter[str]] = defaultdict(Counter)
    type_loci: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for edition, locus, position in sorted(residual_token_at):
        row = row_index[(edition, locus)]
        surface = row["surface"].split()
        token = residual_token_at[(edition, locus, position)]
        mappings = position_mappings[(edition, locus)]
        alternatives = []
        for direction, neighbor_index, fused_surface in (
            (
                "LEFT",
                position - 2,
                surface[position - 2] + token if position > 1 else "",
            ),
            (
                "RIGHT",
                position,
                token + surface[position] if position < len(surface) else "",
            ),
        ):
            if not fused_surface or neighbor_index < 0 or neighbor_index >= len(surface):
                continue
            neighbor_mapping = mappings[neighbor_index]
            if neighbor_mapping is None:
                continue
            for candidate_mapping in sorted(inventory.get(fused_surface, set())):
                witnesses = mapping_witnesses[(fused_surface, candidate_mapping)]
                direct = direct_witnesses.get(
                    (edition, locus, position, token, direction, fused_surface), []
                )
                alternatives.append({
                    "direction": direction,
                    "fused_surface": fused_surface,
                    "root": candidate_mapping[0],
                    "role": candidate_mapping[1],
                    "mapping_relation": (
                        "NEUTRAL_SAME_AS_NEIGHBOR"
                        if candidate_mapping == neighbor_mapping
                        else "REPLACEMENT_ATTESTED"
                    ),
                    "neighbor_surface": surface[neighbor_index],
                    "neighbor_mapping": encode_mapping(neighbor_mapping),
                    "has_other_physical_locus_witness": any(
                        witness_locus != locus for _, witness_locus, _ in witnesses
                    ),
                    "has_same_edition_witness": any(
                        witness_edition == edition for witness_edition, _, _ in witnesses
                    ),
                    "direct_same_locus_alternate_reading_witness": bool(direct),
                    "direct_sole_boundary_mapping_preserving_witness": any(
                        event["sole_boundary_change"]
                        and event["neighbor_mapping_preserved"]
                        for event in direct
                    ),
                })
        deduped = []
        seen = set()
        for alternative in alternatives:
            key = tuple(sorted(alternative.items()))
            if key not in seen:
                deduped.append(alternative)
                seen.add(key)
        neutral_directions = sorted({
            str(item["direction"]) for item in deduped
            if item["mapping_relation"] == "NEUTRAL_SAME_AS_NEIGHBOR"
        })
        replacement_directions = sorted({
            str(item["direction"]) for item in deduped
            if item["mapping_relation"] == "REPLACEMENT_ATTESTED"
        })
        preserving_alternatives = [
            item for item in deduped
            if item["mapping_relation"] == "NEUTRAL_SAME_AS_NEIGHBOR"
        ]
        coverage = (
            "PARSER_MAPPING_PRESERVING_ATTESTED" if neutral_directions
            else "PARSER_MAPPING_CHANGING_ATTESTED" if replacement_directions
            else "NO_ADJACENT_ATTESTED_FUSION"
        )
        type_summary[token].update({
            "events": 1,
            f"coverage:{coverage}": 1,
            "left_neutral": int("LEFT" in neutral_directions),
            "right_neutral": int("RIGHT" in neutral_directions),
            "both_neutral": int(set(neutral_directions) == {"LEFT", "RIGHT"}),
            "left_replacement": int("LEFT" in replacement_directions),
            "right_replacement": int("RIGHT" in replacement_directions),
            f"edition:{edition}": 1,
            f"preserving_edition:{edition}": int(
                coverage == "PARSER_MAPPING_PRESERVING_ATTESTED"
            ),
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
        lattice_rows.append({
            "event_id": f"{edition}|{locus}|{position}",
            "edition": edition,
            "locus": locus,
            "page": row["page"],
            "surface_position_1based": str(position),
            "residual_token": token,
            "coverage_class": coverage,
            "neutral_directions": ";".join(neutral_directions),
            "replacement_directions": ";".join(replacement_directions),
            "candidate_count": str(len(deduped)),
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
            "candidate_json": json.dumps(deduped, separators=(",", ":"), sort_keys=True),
        })

    fieldnames = list(lattice_rows[0])
    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(lattice_rows)

    coverage_counts = Counter(row["coverage_class"] for row in lattice_rows)
    summaries = {}
    for token in sorted(type_summary, key=lambda item: (-type_summary[item]["events"], item)):
        counts = type_summary[token]
        summaries[token] = {
            "events": counts["events"],
            "parser_mapping_preserving_attested": counts["coverage:PARSER_MAPPING_PRESERVING_ATTESTED"],
            "parser_mapping_changing_attested": counts["coverage:PARSER_MAPPING_CHANGING_ATTESTED"],
            "unresolved": counts["coverage:NO_ADJACENT_ATTESTED_FUSION"],
            "left_neutral": counts["left_neutral"],
            "right_neutral": counts["right_neutral"],
            "both_neutral": counts["both_neutral"],
            "left_replacement": counts["left_replacement"],
            "right_replacement": counts["right_replacement"],
            "by_edition": {
                edition: counts[f"edition:{edition}"] for edition in ("ZL3b", "IT2a", "RF1b")
            },
            "mapping_preserving_by_edition": {
                edition: counts[f"preserving_edition:{edition}"]
                for edition in ("ZL3b", "IT2a", "RF1b")
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
                for name in (
                    "PARSER_MAPPING_PRESERVING_ATTESTED",
                    "PARSER_MAPPING_CHANGING_ATTESTED",
                    "NO_ADJACENT_ATTESTED_FUSION",
                )
            },
        }

    expected_event_ids = {
        f"{edition}|{locus}|{position}" for edition, locus, position in residual_token_at
    }
    output_event_ids = [row["event_id"] for row in lattice_rows]
    every_candidate_attested = all(
        (str(item["root"]), str(item["role"]))
        in inventory[str(item["fused_surface"])]
        for row in lattice_rows
        for item in json.loads(row["candidate_json"])
    )
    preserving_count = coverage_counts["PARSER_MAPPING_PRESERVING_ATTESTED"]
    changing_count = coverage_counts["PARSER_MAPPING_CHANGING_ATTESTED"]
    preserving_other_locus = sum(
        row["mapping_preserving_has_other_locus_witness"] == "1" for row in lattice_rows
    )
    preserving_same_edition = sum(
        row["mapping_preserving_has_same_edition_witness"] == "1" for row in lattice_rows
    )
    payload = {
        "status": "PASS_FROZEN_PARTIAL_PARSER_ONE_SIDED_COMPATIBILITY_INVENTORY",
        "decision": "DESCRIPTIVE_PARSER_INTERNAL_COMPATIBILITY_ONLY",
        "input_sha256": {
            str(path.relative_to(HERE.parents[1])): value for path, value in observed.items()
        },
        "candidate_tsv_sha256": digest(OUTPUT_TSV),
        "totals": {
            "events": len(lattice_rows),
            "physical_loci": len({row["locus"] for row in lattice_rows}),
            "parser_mapping_preserving_attested": preserving_count,
            "parser_mapping_changing_attested": changing_count,
            "unresolved": coverage_counts["NO_ADJACENT_ATTESTED_FUSION"],
            "mapping_preserving_has_other_locus_witness": preserving_other_locus,
            "mapping_preserving_lacks_other_locus_witness": preserving_count - preserving_other_locus,
            "mapping_preserving_has_same_edition_witness": preserving_same_edition,
        },
        "type_summary": summaries,
        "gates": {
            "exact_residual_event_key_set_represented_once": (
                len(output_event_ids) == len(set(output_event_ids)) == 3_838
                and set(output_event_ids) == expected_event_ids
            ),
            "every_candidate_mapping_is_exactly_attested": every_candidate_attested,
            "candidate_schema_contains_no_selected_parse": all(
                "selected" not in row and "chosen" not in row for row in lattice_rows
            ),
        },
        "claim_ceiling": (
            "This conservative one-event, one-neighbor inventory records only exact adjacent fused "
            "surfaces and root/role mappings already attested in the same unavailable frozen partial "
            "parser. Mapping-preserving cases are parser-internal compatibility, not neutral evidence "
            "between manuscript parses. Adjacent residual runs and simultaneous two-sided or multi-group "
            "fusions are not modeled. No candidate is selected as authorial, and no operator, suffix, "
            "morphology, sound, word, plaintext, or meaning is established."
        ),
        "english_lexical_glosses": 0,
    }
    if not all(payload["gates"].values()) or payload["english_lexical_glosses"] != 0:
        raise RuntimeError(f"candidate-inventory gate failure: {payload['gates']}")
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    y = summaries["y"]
    dy = summaries["dy"]
    ky = summaries["ky"]
    report = f"""# UNPARSED_SURFACE one-sided compatibility inventory

Decision: **DESCRIPTIVE FROZEN-PARSER COMPATIBILITY ONLY**.

All {len(lattice_rows):,} omitted surface events are retained.  Exact adjacent
fusion types already attested in the frozen formal snapshot supply at least one
parser-mapping-preserving candidate for {preserving_count:,} events and
mapping-changing candidates only for {changing_count:,};
{coverage_counts['NO_ADJACENT_ATTESTED_FUSION']:,} remain unresolved.

Literal `y` has a mapping-preserving candidate at
{y['parser_mapping_preserving_attested']:,}/{y['events']:,} events: left at
{y['left_neutral']:,}, right at {y['right_neutral']:,}, and both at
{y['both_neutral']:,}.  “Both” means two separate one-sided alternatives, not
one simultaneous two-sided parse.  By contrast, `dy` has
{dy['parser_mapping_changing_attested']:,} mapping-changing-only and
{dy['parser_mapping_preserving_attested']:,} preserving events; `ky` has
{ky['parser_mapping_changing_attested']:,} and
{ky['parser_mapping_preserving_attested']:,}.

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
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "events": len(lattice_rows),
        "mapping_preserving": preserving_count,
        "mapping_changing_only": changing_count,
        "unresolved": coverage_counts["NO_ADJACENT_ATTESTED_FUSION"],
        "y_mapping_preserving": y["parser_mapping_preserving_attested"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
