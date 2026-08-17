#!/usr/bin/env python3
"""Compose GDT179 and the retained f77 transition bridge into a page reading."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GDT179 = ROOT / "gdt179_result.json"
BRIDGE = ROOT / "experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json"
SEGMENTS = ROOT / "experiments/semantic_assumptions/f77r_quality_transition_bridge/F77R_SEGMENTS.tsv"
BOUNDARIES = ROOT / "experiments/semantic_assumptions/f77r_quality_transition_bridge/F77R_BOUNDARIES.tsv"
METHOD = ROOT / "GDT180_F77_PROCESS_TRANSLATION_METHOD.md"

STEPS = ROOT / "gdt180_f77_process_steps.tsv"
TRANSITIONS = ROOT / "gdt180_f77_transition_translation.tsv"
PREDICTIONS = ROOT / "gdt180_predictions.tsv"
COUNTER = ROOT / "gdt180_counterexamples.tsv"
RESULT = ROOT / "gdt180_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    gdt179 = json.loads(GDT179.read_text())
    bridge = json.loads(BRIDGE.read_text())
    assert gdt179["status"] == "PROVISIONAL_COMPLETE_F57_ROLE_SCAFFOLD_LOCAL_TWO_BIT_QUALITY_DECODER"
    assert bridge["status"] == "PROVISIONAL_POSTHOC_FOUR_STATE_TRANSITION_CONSTRUCTION"
    assert not gdt179["f84r_accessed"]

    segment_rows = read_tsv(SEGMENTS)
    boundary_rows = read_tsv(BOUNDARIES)
    assert len(segment_rows) == 6 and len(boundary_rows) == 5

    per_locus: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    for row in bridge["target_rows"]:
        per_locus[row["locus"]][row["edition"]] = (row["surface"], row["bits"])
    state_sequence = bridge["states_by_edition"]["ZL3b"]
    assert all(bridge["states_by_edition"][edition] == state_sequence for edition in ("IT2a", "RF1b"))
    assert state_sequence == ["COLD", "DRY", "HOT", "HOT", "MOIST", "COLD"]

    step_rows: list[dict[str, object]] = []
    for source, state in zip(segment_rows, state_sequence):
        locus = source["locus"]
        values = per_locus[locus]
        assert set(values) == {"ZL3b", "IT2a", "RF1b"}
        bits = {value[1] for value in values.values()}
        assert len(bits) == 1
        step_rows.append(
            {
                "step": int(source["position"]),
                "locus": locus,
                "left_opening": source["left_opening"],
                "right_opening": source["right_opening"],
                "ZL3b_surface": values["ZL3b"][0],
                "IT2a_surface": values["IT2a"][0],
                "RF1b_surface": values["RF1b"][0],
                "local_state_bits": next(iter(bits)),
                "provisional_quality_state": state,
                "translation_class": "QUALITY_STATE_LIKE",
                "confidence": "PROVISIONAL_POSTHOC",
            }
        )
    write_tsv(STEPS, list(step_rows[0]), step_rows)

    transition_rows: list[dict[str, object]] = []
    for frozen, source in zip(bridge["boundary_results"], boundary_rows):
        assert int(frozen["boundary_position"]) == int(source["boundary_position"])
        assert int(bool(frozen["emits"])) == int(source["emits"])
        element = frozen["classical_pair_element"] or "NONE_HOT_HOLD"
        transition_rows.append(
            {
                "boundary": int(source["boundary_position"]),
                "opening": source["opening"],
                "left_state": frozen["left_state"],
                "right_state": frozen["right_state"],
                "state_changes": int(bool(frozen["state_changes"])),
                "visible_emission": int(source["emits"]),
                "provisional_transition_class": element,
                "process_reading": "ELEMENT_QUALITY_TRANSITION_OUTPUT" if source["emits"] == "1" else "HOT_STATE_HOLD_NO_OUTPUT",
                "exact_relation_match": int(int(bool(frozen["state_changes"])) == int(source["emits"])),
            }
        )
    assert sum(int(row["exact_relation_match"]) for row in transition_rows) == 5
    assert [row["provisional_transition_class"] for row in transition_rows] == ["EARTH", "FIRE", "NONE_HOT_HOLD", "AIR", "WATER"]
    write_tsv(TRANSITIONS, list(transition_rows[0]), transition_rows)

    prediction_rows = [
        {"prediction_id": "P1", "prediction": "A new independently owned six-segment analogue using the same state code will emit only where adjacent states differ.", "status": "UNTESTED", "failure": "Any securely owned same-system unchanged boundary emits, or a changed boundary does not."},
        {"prediction_id": "P2", "prediction": "A readable legend for the four emitting openings will follow EARTH-FIRE-AIR-WATER in physical order, with no element at the central HOT-HOT boundary.", "status": "UNTESTED", "failure": "A source-owned readable legend fixes another order."},
        {"prediction_id": "P3", "prediction": "The duplicated HOT state represents a hold/repetition step rather than two independent content values.", "status": "UNTESTED", "failure": "Independent text or topology distinguishes two different owned values at steps 3 and 4."},
        {"prediction_id": "P4", "prediction": "The process returns to the same coarse COLD state at its two ends despite different surface groups.", "status": "PARTIALLY_OBSERVED_FORMALLY", "failure": "A new independent state endpoint differentiates the two ends under the same four-state system."},
    ]
    write_tsv(PREDICTIONS, list(prediction_rows[0]), prediction_rows)

    counter_rows = [
        {"id": "C1", "finding": "The bridge was discovered after f77 topology and labels were exposed.", "impact": "The exact fit is theory generation, not replication."},
        {"id": "C2", "finding": "A cached visual puff-order proposal gives AIR-WATER-FIRE-EARTH, zero of four agreeing with this order.", "impact": "Outputs cannot be glossed as named elements."},
        {"id": "C3", "finding": "Residual f57-to-f77 surface identity ranks poorly under complete-form assignment.", "impact": "The states are compiler-bit classes, not repeated quality words."},
        {"id": "C4", "finding": "The f67v1 universal graphical-output transfer failed.", "impact": "Emission-if-change is not manuscript-wide."},
        {"id": "C5", "finding": "No operation, material, bodily process, or recipe is independently identified on f77r.", "impact": "PROCESS remains an abstract diagram function."},
        {"id": "C6", "finding": "f84r remains sealed and unused.", "impact": "No final surprise evidence is consumed."},
    ]
    write_tsv(COUNTER, list(counter_rows[0]), counter_rows)

    outputs = [STEPS, TRANSITIONS, PREDICTIONS, COUNTER]
    result = {
        "experiment": "GDT180_F77_PROCESS_TRANSLATION_SYNTHESIS",
        "status": "PROVISIONAL_F77_QUALITY_STATE_PROCESS_READING",
        "state_sequence": state_sequence,
        "transition_sequence": [row["provisional_transition_class"] for row in transition_rows],
        "emission_mask": [int(row["visible_emission"]) for row in transition_rows],
        "counts": {"segments": 6, "boundaries": 5, "relation_matches": 5, "emitting_transitions": 4, "nonemitting_holds": 1},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [GDT179, BRIDGE, SEGMENTS, BOUNDARIES, METHOD]},
        "outputs": {path.name: sha(path) for path in outputs},
        "implementation": sha(Path(__file__).resolve()),
        "f84r_accessed": False,
        "claim_ceiling": (
            "A provisional page-level quality-state process: COLD to DRY to HOT, HOT hold, "
            "MOIST to COLD, with emissions at the four changing classical element pairs. "
            "No source group is a confirmed word and no operation, material, language, plaintext, "
            "or manuscript-wide translation is established."
        ),
    }
    RESULT.write_bytes(canonical(result))
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
