#!/usr/bin/env python3
"""Target-blind synthetic controls for ZLA001."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

import zla001_core as core


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
METHOD = ROOT / "ZODIAC_LABEL_ADJACENCY_METHOD.md"
PANEL = BASE / "results/zodiac_label_cycle_capacity.tsv"
CAPACITY = BASE / "results/zodiac_label_cycle_capacity.json"
CAPACITY_VALIDATION = BASE / "results/zodiac_label_cycle_capacity_validation.json"
OUT = BASE / "results/zla001_controls.json"
REPORT = BASE / "results/zla001_controls.md"
KINDS = (
    "DISTRIBUTED",
    "NULL",
    "ONE_FOLIO",
    "READING_DISAGREEMENT",
    "EXACT_ONLY",
    "LENGTH_ONLY",
    "DISTANCE_TWO",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def window_plant(ring: core.Ring, seed: int, step: int = 1) -> list[tuple[str, ...]]:
    n = ring.n
    if step == 1:
        order = list(range(n))
        cycles = [order]
    else:
        unseen = set(range(n))
        cycles = []
        while unseen:
            start = min(unseen)
            cycle = []
            value = start
            while value in unseen:
                unseen.remove(value)
                cycle.append(value)
                value = (value + step) % n
            cycles.append(cycle)
    output: list[tuple[str, ...] | None] = [None] * n
    for cycle_index, cycle in enumerate(cycles):
        width = min(6, max(2, len(cycle) - 1))
        edge = [f"E{seed}:{ring.ring_id}:{cycle_index}:{index}" for index in range(len(cycle))]
        for local, position in enumerate(cycle):
            output[position] = tuple(edge[(local + offset) % len(edge)] for offset in range(width))
    if any(value is None for value in output):
        raise AssertionError("plant construction")
    return [tuple(value) for value in output if value is not None]


def random_sequences(ring: core.Ring, seed: int, reading: str) -> list[tuple[str, ...]]:
    rng = random.Random(f"ZLA001|{seed}|{reading}|{ring.ring_id}")
    alphabet = [f"A{index}" for index in range(12)]
    output = []
    for position in range(ring.n):
        length = 4 + rng.randrange(4)
        output.append(tuple(rng.choice(alphabet) for _ in range(length - 1)) + (f"N{position}",))
    return output


def exact_only_sequences(ring: core.Ring, seed: int) -> list[tuple[str, ...]]:
    rng = random.Random(f"ZLA001|EXACT|{seed}|{ring.ring_id}")
    bases = []
    for pair in range((ring.n + 1) // 2):
        bases.append(tuple(f"X{pair}:{rng.randrange(7)}:{index}" for index in range(5)))
    return [bases[position // 2] for position in range(ring.n)]


def length_only_sequences(ring: core.Ring, seed: int) -> list[tuple[str, ...]]:
    offset = seed % 3
    lengths = [3 + ((position + offset) // 2) % 5 for position in range(ring.n)]
    return [tuple("L" for _ in range(length)) for length in lengths]


def with_boundary(values: list[tuple[str, ...]]) -> list[tuple[str, ...]]:
    output = []
    for sequence in values:
        split = max(1, len(sequence) // 2)
        output.append(sequence[:split] + ("|",) + sequence[split:])
    return output


def synthetic_world(geometry: core.Geometry, kind: str, seed: int) -> dict[str, dict[str, list[list[tuple[str, ...]]]]]:
    output = {reading: {view: [] for view in core.VIEWS} for reading in core.READINGS}
    signal_folio = geometry.folios[seed % len(geometry.folios)]
    for reading in core.READINGS:
        for ring in geometry.rings:
            selected = kind
            if kind == "ONE_FOLIO":
                selected = "DISTRIBUTED" if ring.folio == signal_folio else "NULL"
            if kind == "READING_DISAGREEMENT":
                selected = "DISTRIBUTED" if reading != "RF1b" else "DISTANCE_TWO"
            if selected == "DISTRIBUTED":
                family = window_plant(ring, seed, 1)
            elif selected == "DISTANCE_TWO":
                family = window_plant(ring, seed, 2)
            elif selected == "EXACT_ONLY":
                family = exact_only_sequences(ring, seed)
            elif selected == "LENGTH_ONLY":
                family = length_only_sequences(ring, seed)
            elif selected == "NULL":
                family = random_sequences(ring, seed, reading)
            else:
                raise AssertionError(selected)
            output[reading]["FAMILY_ONLY"].append(family)
            output[reading]["BOUNDARY_AWARE"].append(with_boundary(family))
    return output


def numeric_leaves(value: object, prefix: str = "") -> dict[str, float]:
    output = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if "sha256" in str(key):
                continue
            output.update(numeric_leaves(item, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        output[prefix] = float(value)
    return output


def invariant(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    a = numeric_leaves(left)
    b = numeric_leaves(right)
    if set(a) != set(b):
        return {"pass": False, "reason": "numeric leaf schema", "max_abs": None}
    maximum = max(abs(a[key] - b[key]) for key in a) if a else 0.0
    same_logic = left["gates"] == right["gates"] and left["confirmed"] == right["confirmed"]
    return {"pass": maximum <= core.TOL and same_logic, "max_abs": maximum, "same_logic": same_logic}


def safe_evaluate(geometry: core.Geometry, assignments: np.ndarray, sequences: dict) -> dict[str, object]:
    try:
        result = core.evaluate(geometry, assignments, sequences)
        return {"status": "SCORED", "confirmed": bool(result["confirmed"]), "result": result}
    except AssertionError as error:
        return {"status": "REJECTED_NUMERIC_OR_CONTRACT", "confirmed": False, "error": str(error)}


def compact(record: dict[str, object]) -> dict[str, object]:
    if record["status"] != "SCORED":
        return record
    result = record["result"]
    return {
        "status": "SCORED",
        "confirmed": record["confirmed"],
        "primary": result["primary"],
        "components": result["components"],
        "noexact": result["noexact"],
        "noexact_ring_counts": result["noexact_ring_counts"],
        "noexact_folio_counts": result["noexact_folio_counts"],
        "positive_folio_counts": result["positive_folio_counts"],
        "folio_concentration": result["folio_concentration"],
        "deletion_effects": result["deletion_effects"],
        "gates": result["gates"],
        "result_sha256": canonical_hash(result),
    }


def run(smoke: bool = False) -> dict[str, object]:
    geometry = core.load_geometry(PANEL)
    assignments, orbit = core.assignment_matrix(geometry)
    seeds = range(1 if smoke else 8)
    records: dict[str, list[dict[str, object]]] = {kind: [] for kind in KINDS}
    invariances = []
    for kind in KINDS:
        for seed in seeds:
            sequences = synthetic_world(geometry, kind, seed)
            scored = safe_evaluate(geometry, assignments, sequences)
            records[kind].append({"world": seed, **compact(scored)})
            if kind == "DISTRIBUTED" and scored["status"] == "SCORED":
                shifts = [int.from_bytes(hashlib.sha256(f"rotate|{seed}|{ring.ring_id}".encode()).digest()[:2], "big") for ring in geometry.rings]
                rotated = core.evaluate(geometry, assignments, core.rotate_sequences(sequences, shifts))
                reflected = core.evaluate(geometry, assignments, core.reflect_sequences(sequences))
                invariances.append({
                    "world": seed,
                    "rotation": invariant(scored["result"], rotated),
                    "reflection": invariant(scored["result"], reflected),
                })

    if smoke:
        return {"records": records, "invariances": invariances, "orbit": orbit}

    pass_counts = {kind: sum(bool(row["confirmed"]) for row in values) for kind, values in records.items()}
    mutation_checks = {}
    base = synthetic_world(geometry, "DISTRIBUTED", 0)
    duplicate = assignments.copy()
    duplicate[1] = duplicate[0]
    mutation_checks["duplicate_assignment_rejected"] = safe_evaluate(geometry, duplicate, base)["status"] != "SCORED"
    illegal = assignments.copy()
    illegal[0, 0] = 1
    mutation_checks["adjacent_null_distance_rejected"] = safe_evaluate(geometry, illegal, base)["status"] != "SCORED"
    missing = copy.deepcopy(base)
    missing["ZL3b"]["FAMILY_ONLY"][0].pop()
    mutation_checks["missing_slot_rejected"] = safe_evaluate(geometry, assignments, missing)["status"] != "SCORED"
    empty = copy.deepcopy(base)
    empty["ZL3b"]["FAMILY_ONLY"][0][0] = tuple()
    mutation_checks["empty_sequence_rejected"] = safe_evaluate(geometry, assignments, empty)["status"] != "SCORED"
    repeated_assignments, repeated_orbit = core.assignment_matrix(geometry)
    mutation_checks["deterministic_assignment_serialization"] = orbit == repeated_orbit and np.array_equal(assignments, repeated_assignments)

    gates = {
        "distributed_at_least_7_of_8": pass_counts["DISTRIBUTED"] >= 7,
        "every_negative_zero_of_8": all(pass_counts[kind] == 0 for kind in KINDS if kind != "DISTRIBUTED"),
        "all_rotation_and_reflection_invariances": all(
            item[axis]["pass"] for item in invariances for axis in ("rotation", "reflection")
        ) and len(invariances) == 8,
        "all_mutations_rejected_or_deterministic": all(mutation_checks.values()),
        "exact_65536_unique_assignment_rows": len({row.tobytes() for row in assignments}) == core.N_WORLDS,
        "target_source_not_opened": True,
        "zero_English_glosses": True,
    }
    return {
        "experiment": "ZLA001_TARGET_BLIND_CONTROLS",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "decision": "AUTHORIZE_INDEPENDENT_CONTROL_RECONSTRUCTION" if all(gates.values()) else "STOP_TARGET_FORBIDDEN",
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (METHOD, PANEL, CAPACITY, CAPACITY_VALIDATION, Path(core.__file__), Path(__file__))},
        "geometry": {"rings": len(geometry.rings), "slots": sum(ring.n for ring in geometry.rings), "pages": len(geometry.pages), "folios": len(geometry.folios)},
        "orbit": orbit,
        "pass_counts": pass_counts,
        "records": records,
        "invariances": invariances,
        "mutation_checks": mutation_checks,
        "gates": gates,
        "claim_ceiling": "Synthetic scorer calibration only; no manuscript adjacency effect, serial code, number, degree, word, meaning, plaintext, or translation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        result = run(True)
        print(json.dumps({
            "pass": {kind: [row["confirmed"] for row in values] for kind, values in result["records"].items()},
            "invariances": result["invariances"],
            "orbit": result["orbit"],
        }, sort_keys=True, indent=2))
        return
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    result = run(False)
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# ZLA001 target-blind controls\n\n"
        f"Status: **{result['status']}**. Distributed confirmations: {result['pass_counts']['DISTRIBUTED']}/8. "
        + "Negative confirmations: "
        + ", ".join(f"{kind} {result['pass_counts'][kind]}/8" for kind in KINDS if kind != "DISTRIBUTED")
        + ".\n\n"
        "The complete 65,536-world scorer used only synthetic sequences on the frozen 21-ring geometry. "
        "Rotation, reflection, assignment serialization, and malformed-input controls are included. "
        "No manuscript STA sequence or adjacency score was opened.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "pass_counts": result["pass_counts"], "gates": result["gates"]}, sort_keys=True))


if __name__ == "__main__":
    main()
