#!/usr/bin/env python3
"""Independent non-importing validator for the f77r transition bridge."""

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
RESULT = Path(
    "experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json"
)
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/"
    "existing_human_exact_locus_annotations.tsv"
)
SEGMENTS = Path(
    "experiments/semantic_assumptions/f77r_quality_transition_bridge/"
    "F77R_SEGMENTS.tsv"
)
BOUNDARIES = Path(
    "experiments/semantic_assumptions/f77r_quality_transition_bridge/"
    "F77R_BOUNDARIES.tsv"
)
EDITIONS = ("ZL3b", "IT2a", "RF1b")
NAMES = {"10": "HOT", "01": "MOIST", "00": "COLD", "11": "DRY"}
VALID = {
    frozenset(("COLD", "DRY")),
    frozenset(("DRY", "HOT")),
    frozenset(("HOT", "MOIST")),
    frozenset(("MOIST", "COLD")),
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(surface: str) -> str:
    text = "".join(surface.split())
    code = ("1" if text[:2] == "ot" else "0") + (
        "1" if text[-1:] == "y" else "0"
    )
    return NAMES[code]


def passes(sequence: tuple[str, ...], mask: tuple[bool, ...]) -> bool:
    emitted_pairs = []
    for position in range(5):
        changes = sequence[position] != sequence[position + 1]
        if changes != mask[position]:
            return False
        if mask[position]:
            emitted_pairs.append(
                frozenset((sequence[position], sequence[position + 1]))
            )
    return len(emitted_pairs) == 4 and set(emitted_pairs) == VALID


def generic_passes(sequence: tuple[str, ...], mask: tuple[bool, ...]) -> bool:
    emitted_pairs = []
    for position in range(5):
        changes = sequence[position] != sequence[position + 1]
        if changes != mask[position]:
            return False
        if mask[position]:
            emitted_pairs.append(
                frozenset((sequence[position], sequence[position + 1]))
            )
    return (
        len(emitted_pairs) == len(set(emitted_pairs)) == 4
        and len(set(sequence)) == 4
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result_path = ROOT / RESULT
    result = json.loads(result_path.read_text(encoding="utf-8"))
    checks: list[tuple[str, bool]] = []

    for relative, expected in result["inputs"].items():
        checks.append((f"input_hash:{relative}", digest(ROOT / relative) == expected))

    interlinear = rows(ROOT / INTERLINEAR)
    annotations = rows(ROOT / ANNOTATIONS)
    segment_rows = sorted(rows(ROOT / SEGMENTS), key=lambda row: int(row["position"]))
    boundary_rows = sorted(
        rows(ROOT / BOUNDARIES), key=lambda row: int(row["boundary_position"])
    )
    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interlinear:
        by_locus[row["locus"]][row["edition"]] = row

    checks.append(("six_segments", len(segment_rows) == 6))
    checks.append(("five_boundaries", len(boundary_rows) == 5))
    checks.append(
        (
            "segment_positions",
            [int(row["position"]) for row in segment_rows] == list(range(1, 7)),
        )
    )
    checks.append(
        (
            "boundary_positions",
            [int(row["boundary_position"]) for row in boundary_rows]
            == list(range(1, 6)),
        )
    )
    mask = tuple(row["emits"] == "1" for row in boundary_rows)
    checks.append(("emission_mask", mask == (True, True, False, True, True)))

    states_by_edition = {}
    for edition in EDITIONS:
        sequence = tuple(
            classify(by_locus[row["locus"]][edition]["surface"])
            for row in segment_rows
        )
        states_by_edition[edition] = sequence
        checks.append(
            (f"stored_states:{edition}", list(sequence) == result["states_by_edition"][edition])
        )
    observed = states_by_edition["ZL3b"]
    checks.append(("reading_identity", len(set(states_by_edition.values())) == 1))
    checks.append(
        (
            "observed_sequence",
            observed == ("COLD", "DRY", "HOT", "HOT", "MOIST", "COLD"),
        )
    )
    checks.append(("complete_gate", passes(observed, mask)))

    universe = list(itertools.product(tuple(NAMES.values()), repeat=6))
    conditional = sorted(set(itertools.permutations(observed)))
    checks.append(("universe_size", len(universe) == 4096))
    checks.append(("universe_passes", sum(passes(x, mask) for x in universe) == 8))
    checks.append(
        ("universe_generic_passes", sum(generic_passes(x, mask) for x in universe) == 72)
    )
    checks.append(("conditional_size", len(conditional) == 180))
    checks.append(
        ("conditional_passes", sum(passes(x, mask) for x in conditional) == 4)
    )
    checks.append(
        (
            "conditional_generic_passes",
            sum(generic_passes(x, mask) for x in conditional) == 12,
        )
    )

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
    window_count = 0
    window_passes = []
    generic_window_passes = []
    for key, values in sorted(groups.items()):
        ordered = sorted(set(values))
        for offset in range(len(ordered) - 5):
            window = ordered[offset : offset + 6]
            numbers = [item[0] for item in window]
            if numbers != list(range(numbers[0], numbers[0] + 6)):
                continue
            loci = [item[1] for item in window]
            readings = {
                tuple(classify(by_locus[locus][edition]["surface"]) for locus in loci)
                for edition in EDITIONS
            }
            if len(readings) != 1:
                continue
            window_count += 1
            sequence = next(iter(readings))
            if passes(sequence, mask):
                window_passes.append((*key, numbers[0]))
            if generic_passes(sequence, mask):
                generic_window_passes.append((*key, numbers[0]))
    checks.append(("window_count", window_count == 184))
    checks.append(
        (
            "window_passes",
            set(window_passes) == {("f77r", "V1", 2)},
        )
    )
    checks.append(
        (
            "generic_window_passes",
            set(generic_window_passes)
            == {("f68r1", "S1", 15), ("f77r", "V1", 2)},
        )
    )
    checks.append(
        (
            "appearance_mismatch_stored",
            result["appearance_crosscheck"]["same_position_matches"] == 0,
        )
    )
    checks.append(
        (
            "decision_ceiling",
            "no quality label element label" in result["decision"]["forbid"],
        )
    )

    failed = [name for name, passed in checks if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "nonimporting": True,
        "check_count": len(checks),
        "failed_checks": failed,
        "result_sha256": digest(result_path),
        "observed_sequence": list(observed),
        "unconditional": {"passes": 8, "total": 4096},
        "fixed_multiset": {"passes": 4, "total": 180},
        "stable_windows": {
            "classical_pair_passes": len(window_passes),
            "generic_four_edge_passes": len(generic_window_passes),
            "total": window_count,
        },
    }
    if failed:
        raise SystemExit(json.dumps(validation, indent=2))
    payload = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
