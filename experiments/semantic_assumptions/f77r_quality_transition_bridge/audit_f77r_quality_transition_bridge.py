#!/usr/bin/env python3
"""Reconstruct the post-hoc f57-state / f77r-boundary bridge."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/f77r_quality_transition_bridge")
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
EXACT_ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/"
    "existing_human_exact_locus_annotations.tsv"
)
PAGE_ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
)
DESIGN = BASE / "DESIGN.md"
SEGMENTS = BASE / "F77R_SEGMENTS.tsv"
BOUNDARIES = BASE / "F77R_BOUNDARIES.tsv"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
STATE_BY_BITS = {"10": "HOT", "01": "MOIST", "00": "COLD", "11": "DRY"}
ELEMENT_BY_PAIR = {
    frozenset(("COLD", "DRY")): "EARTH",
    frozenset(("DRY", "HOT")): "FIRE",
    frozenset(("HOT", "MOIST")): "AIR",
    frozenset(("MOIST", "COLD")): "WATER",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def bits(surface: str) -> str:
    compact = "".join(surface.split())
    return f"{int(compact.startswith('ot'))}{int(compact.endswith('y'))}"


def complete_gate(states: tuple[str, ...], emission_mask: tuple[bool, ...]) -> bool:
    if len(states) != 6 or len(emission_mask) != 5:
        return False
    pairs = []
    for index, emits in enumerate(emission_mask):
        changed = states[index] != states[index + 1]
        if emits != changed:
            return False
        if emits:
            pairs.append(frozenset((states[index], states[index + 1])))
    return len(pairs) == 4 and set(pairs) == set(ELEMENT_BY_PAIR)


def generic_four_edge_gate(
    states: tuple[str, ...], emission_mask: tuple[bool, ...]
) -> bool:
    if len(states) != 6 or len(emission_mask) != 5:
        return False
    pairs = []
    for index, emits in enumerate(emission_mask):
        changed = states[index] != states[index + 1]
        if emits != changed:
            return False
        if emits:
            pairs.append(frozenset((states[index], states[index + 1])))
    return len(pairs) == len(set(pairs)) == 4 and len(set(states)) == 4


def stable_window_control(
    annotations: list[dict[str, str]],
    by_locus: dict[str, dict[str, dict[str, str]]],
    emission_mask: tuple[bool, ...],
) -> dict[str, object]:
    groups: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    for annotation in annotations:
        match = re.search(r"\.(\d+)$", annotation["source_locus"])
        locus = annotation["locus"]
        if not match or locus not in by_locus:
            continue
        if set(by_locus[locus]) != set(EDITIONS):
            continue
        if by_locus[locus]["ZL3b"]["kind"] != "L":
            continue
        groups[(annotation["page"], annotation["unit"])].append(
            (int(match.group(1)), locus)
        )

    stable_windows = []
    for (page, unit), values in sorted(groups.items()):
        ordered = sorted(set(values))
        for start in range(len(ordered) - 5):
            window = ordered[start : start + 6]
            indices = [item[0] for item in window]
            if indices != list(range(indices[0], indices[0] + 6)):
                continue
            loci = [item[1] for item in window]
            states_by_edition = {
                edition: tuple(
                    STATE_BY_BITS[bits(by_locus[locus][edition]["surface"])]
                    for locus in loci
                )
                for edition in EDITIONS
            }
            if len(set(states_by_edition.values())) != 1:
                continue
            state_sequence = states_by_edition["ZL3b"]
            stable_windows.append(
                {
                    "page": page,
                    "unit": unit,
                    "start_index": indices[0],
                    "loci": loci,
                    "state_sequence": list(state_sequence),
                    "classical_pair_gate": complete_gate(
                        state_sequence, emission_mask
                    ),
                    "generic_four_edge_gate": generic_four_edge_gate(
                        state_sequence, emission_mask
                    ),
                }
            )
    classical_passes = [
        row for row in stable_windows if row["classical_pair_gate"]
    ]
    generic_passes = [
        row for row in stable_windows if row["generic_four_edge_gate"]
    ]
    return {
        "stable_consecutive_six_label_windows": len(stable_windows),
        "classical_pair_gate_pass_count": len(classical_passes),
        "classical_pair_gate_passes": classical_passes,
        "generic_four_edge_gate_pass_count": len(generic_passes),
        "generic_four_edge_gate_passes": generic_passes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = {
        INTERLINEAR: ROOT / INTERLINEAR,
        EXACT_ANNOTATIONS: ROOT / EXACT_ANNOTATIONS,
        PAGE_ANNOTATIONS: ROOT / PAGE_ANNOTATIONS,
        DESIGN: ROOT / DESIGN,
        SEGMENTS: ROOT / SEGMENTS,
        BOUNDARIES: ROOT / BOUNDARIES,
    }
    interlinear = read_tsv(paths[INTERLINEAR])
    annotations = read_tsv(paths[EXACT_ANNOTATIONS])
    page_annotations = read_tsv(paths[PAGE_ANNOTATIONS])
    segments = read_tsv(paths[SEGMENTS])
    boundaries = read_tsv(paths[BOUNDARIES])

    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interlinear:
        by_locus[row["locus"]][row["edition"]] = row

    segments.sort(key=lambda row: int(row["position"]))
    boundaries.sort(key=lambda row: int(row["boundary_position"]))
    emission_mask = tuple(row["emits"] == "1" for row in boundaries)

    target_rows = []
    states_by_edition = {}
    for edition in EDITIONS:
        states = []
        for segment in segments:
            locus = segment["locus"]
            row = by_locus[locus][edition]
            bit_code = bits(row["surface"])
            state = STATE_BY_BITS[bit_code]
            states.append(state)
            target_rows.append(
                {
                    "edition": edition,
                    "position": int(segment["position"]),
                    "locus": locus,
                    "surface": row["surface"],
                    "root_sequence": row["root_sequence"],
                    "bits": bit_code,
                    "f57_page_role_state": state,
                }
            )
        states_by_edition[edition] = tuple(states)

    stable_states = states_by_edition["ZL3b"]
    boundary_results = []
    predicted_elements = []
    for boundary, emits in zip(boundaries, emission_mask, strict=True):
        left_index = int(boundary["left_segment_position"]) - 1
        right_index = int(boundary["right_segment_position"]) - 1
        left_state = stable_states[left_index]
        right_state = stable_states[right_index]
        pair = frozenset((left_state, right_state))
        element = ELEMENT_BY_PAIR.get(pair) if emits else None
        if emits:
            predicted_elements.append(element)
        boundary_results.append(
            {
                "boundary_position": int(boundary["boundary_position"]),
                "opening": boundary["opening"],
                "emits": emits,
                "left_state": left_state,
                "right_state": right_state,
                "state_changes": left_state != right_state,
                "classical_pair_element": element,
            }
        )

    all_sequences = list(itertools.product(STATE_BY_BITS.values(), repeat=6))
    fixed_multiset_sequences = sorted(set(itertools.permutations(stable_states)))
    all_pass = sum(complete_gate(sequence, emission_mask) for sequence in all_sequences)
    fixed_pass = sum(
        complete_gate(sequence, emission_mask) for sequence in fixed_multiset_sequences
    )
    all_generic_pass = sum(
        generic_four_edge_gate(sequence, emission_mask) for sequence in all_sequences
    )
    fixed_generic_pass = sum(
        generic_four_edge_gate(sequence, emission_mask)
        for sequence in fixed_multiset_sequences
    )

    window_control = stable_window_control(annotations, by_locus, emission_mask)

    f77_page_rows = [row for row in page_annotations if row["page"] == "f77r"]
    assert len(f77_page_rows) == 1
    page_row = f77_page_rows[0]
    appearance_phrase = "left to right) air, water, fire, earth"
    assert appearance_phrase in page_row["tentative_identifications"].lower()
    appearance_proposal = ["AIR", "WATER", "FIRE", "EARTH"]
    appearance_matches = sum(
        predicted == proposed
        for predicted, proposed in zip(
            predicted_elements, appearance_proposal, strict=True
        )
    )

    result = {
        "status": "PROVISIONAL_POSTHOC_FOUR_STATE_TRANSITION_CONSTRUCTION",
        "exposure": "POSTHOC_NO_CONFIRMATORY_P_VALUE",
        "inputs": {str(path): sha256(real_path) for path, real_path in paths.items()},
        "official_witness_qc": {
            "manifest_url": "https://collections.library.yale.edu/manifests/2002046",
            "manifest_sha256": (
                "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
            ),
            "f77r_canvas_id": 1006212,
            "scope": "author-visible emission topology only; no semantic labels",
        },
        "state_mapping": STATE_BY_BITS,
        "target_rows": target_rows,
        "states_by_edition": {
            edition: list(states) for edition, states in states_by_edition.items()
        },
        "emission_mask": list(emission_mask),
        "boundary_results": boundary_results,
        "gates": {
            "alternate_reading_state_identity": len(set(states_by_edition.values())) == 1,
            "emission_iff_state_change": all(
                row["emits"] == row["state_changes"] for row in boundary_results
            ),
            "four_classical_pairs_exactly_once": (
                predicted_elements == ["EARTH", "FIRE", "AIR", "WATER"]
            ),
            "nonemitting_boundary_identical": (
                not boundary_results[2]["emits"]
                and not boundary_results[2]["state_changes"]
            ),
        },
        "exact_descriptive_nulls": {
            "all_four_state_sequences": len(all_sequences),
            "all_four_state_passes": all_pass,
            "all_four_state_generic_four_edge_passes": all_generic_pass,
            "fixed_observed_multiset_sequences": len(fixed_multiset_sequences),
            "fixed_observed_multiset_passes": fixed_pass,
            "fixed_observed_multiset_generic_four_edge_passes": fixed_generic_pass,
        },
        "consecutive_window_control": window_control,
        "appearance_crosscheck": {
            "cached_human_proposal": appearance_proposal,
            "transition_pair_prediction": predicted_elements,
            "same_position_matches": appearance_matches,
            "role_evidence_flag": page_row[
                "tentative_identifications_are_role_evidence"
            ],
            "interpretation": (
                "zero-position agreement is counterevidence to a direct element gloss"
            ),
        },
        "decision": {
            "retain": (
                "a provisional cross-page four-state transition construction: "
                "f57-derived states predict f77r emission versus non-emission and "
                "cover the four classical adjacent-quality pairs"
            ),
            "forbid": (
                "no quality label element label ot/y meaning lexeme plaintext or "
                "translation"
            ),
            "confirm_only_if": (
                "a second independently annotated segmented system is frozen before "
                "its Voynich strings and reproduces the transition rule with owned outputs"
            ),
        },
    }

    assert stable_states == ("COLD", "DRY", "HOT", "HOT", "MOIST", "COLD")
    assert emission_mask == (True, True, False, True, True)
    assert all(result["gates"].values())
    assert (all_pass, len(all_sequences)) == (8, 4096)
    assert (fixed_pass, len(fixed_multiset_sequences)) == (4, 180)
    assert all_generic_pass == 72
    assert fixed_generic_pass == 12
    assert window_control["stable_consecutive_six_label_windows"] == 184
    assert window_control["classical_pair_gate_pass_count"] == 1
    assert {
        (row["page"], row["unit"], row["start_index"])
        for row in window_control["classical_pair_gate_passes"]
    } == {("f77r", "V1", 2)}
    assert window_control["generic_four_edge_gate_pass_count"] == 2
    assert {
        (row["page"], row["unit"], row["start_index"])
        for row in window_control["generic_four_edge_gate_passes"]
    } == {("f68r1", "S1", 15), ("f77r", "V1", 2)}
    assert appearance_matches == 0
    assert page_row["tentative_identifications_are_role_evidence"] == "0"

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
