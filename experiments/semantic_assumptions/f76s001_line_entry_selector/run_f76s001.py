#!/usr/bin/env python3
"""Run frozen controls or the single F76S001 line-entry selector target."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import statistics
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
SOURCE_AUDIT = ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv"
PREREG = ROOT / "experiments/semantic_assumptions/hypotheses/F76S001_LINE_ENTRY_SELECTOR_PREREGISTRATION.md"
VALIDATOR = HERE / "validate_f76s001.py"
CONTROL_RESULT = HERE / "CONTROL_RESULT.json"
TARGET_RESULT = HERE / "TARGET_RESULT.json"
CONTROL_REPORT = ROOT / "experiments/semantic_assumptions/results/f76s001_line_entry_selector_control_report.md"
TARGET_REPORT = ROOT / "experiments/semantic_assumptions/results/f76s001_line_entry_selector_report.md"

READINGS = ("ZL3b", "IT2a", "RF1b")
CHANNELS = ("carrier", "q_state", "role_path")
INPUT_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
SOURCE_SHA256 = "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc"
PAIRING = (
    (1, "f76r.4", "f76r.5", "s"),
    (2, "f76r.7", "f76r.8", "d"),
    (3, "f76r.10", "f76r.11", "q"),
    (4, "f76r.14", "f76r.15", "s"),
    (5, "f76r.18", "f76r.19", "o"),
    (6, "f76r.22", "f76r.23", "l"),
    (7, "f76r.27", "f76r.28", "k"),
    (8, "f76r.31", "f76r.32", "r"),
    (9, "f76r.37", "f76r.38", "s"),
)
TARGET = (0, 3, 8)
COMBOS = tuple(itertools.combinations(range(9), 3))
PRIMARY_P_LIMIT = 4 / 84
EPS = 1e-12


class DegenerateOrbit(RuntimeError):
    pass


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def levenshtein(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def feature(carrier: str, q_state: bool, role_path: tuple[str, ...], surface: str = "") -> dict[str, Any]:
    return {
        "carrier": carrier,
        "q_state": bool(q_state),
        "role_path": tuple(role_path),
        "surface": surface,
    }


def channel_similarities(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    path_left = left["role_path"]
    path_right = right["role_path"]
    denominator = max(len(path_left), len(path_right))
    if denominator == 0:
        raise ValueError("empty role path")
    return {
        "carrier": float(left["carrier"] == right["carrier"]),
        "q_state": float(left["q_state"] == right["q_state"]),
        "role_path": 1.0 - levenshtein(path_left, path_right) / denominator,
    }


def pair_score(left: dict[str, Any], right: dict[str, Any], channels: tuple[str, ...]) -> float:
    values = channel_similarities(left, right)
    return sum(values[channel] for channel in channels) / len(channels)


def triplet_score(features: list[dict[str, Any]], combo: tuple[int, int, int], channels: tuple[str, ...]) -> float:
    pairs = itertools.combinations(combo, 2)
    return statistics.fmean(pair_score(features[a], features[b], channels) for a, b in pairs)


def score_panel(panel: dict[str, list[dict[str, Any]]], channels: tuple[str, ...] = CHANNELS) -> dict[str, Any]:
    if tuple(panel) != READINGS:
        raise ValueError("reading order drift")
    reading_scores: dict[str, list[float]] = {}
    reading_z: dict[str, list[float]] = {}
    for reading in READINGS:
        features = panel[reading]
        if len(features) != 9:
            raise ValueError(f"{reading}: expected nine features")
        scores = [triplet_score(features, combo, channels) for combo in COMBOS]
        deviation = statistics.pstdev(scores)
        if deviation <= EPS:
            raise DegenerateOrbit(f"{reading}: degenerate orbit")
        mean = statistics.fmean(scores)
        reading_scores[reading] = scores
        reading_z[reading] = [(value - mean) / deviation for value in scores]

    target_offset = COMBOS.index(TARGET)
    synchronous = [min(reading_z[reading][offset] for reading in READINGS) for offset in range(len(COMBOS))]
    target_sync = synchronous[target_offset]
    exact_tail = sum(value >= target_sync - EPS for value in synchronous)
    exact_p = exact_tail / len(COMBOS)

    ranks: dict[str, int] = {}
    effects: dict[str, float] = {}
    pair_gate: dict[str, bool] = {}
    pair_details: dict[str, Any] = {}
    for reading in READINGS:
        scores = reading_scores[reading]
        observed = scores[target_offset]
        ranks[reading] = 1 + sum(value > observed + EPS for value in scores)
        effects[reading] = observed - statistics.median(scores)
        all_pairs = [
            pair_score(panel[reading][a], panel[reading][b], channels)
            for a, b in itertools.combinations(range(9), 2)
        ]
        median_pair = statistics.median(all_pairs)
        target_pairs = [
            pair_score(panel[reading][a], panel[reading][b], channels)
            for a, b in itertools.combinations(TARGET, 2)
        ]
        pair_gate[reading] = all(value > median_pair + EPS for value in target_pairs)
        pair_details[reading] = {
            "all_pair_median": median_pair,
            "target_pair_scores": target_pairs,
        }

    surface_veto = {
        reading: len({panel[reading][index]["surface"] for index in TARGET}) == 3
        for reading in READINGS
    }
    return {
        "channels": list(channels),
        "combo_count": len(COMBOS),
        "target_positions_one_based": [index + 1 for index in TARGET],
        "target_synchronous_z": target_sync,
        "exact_tail_count": exact_tail,
        "exact_p": exact_p,
        "reading_ranks": ranks,
        "reading_effects": effects,
        "minimum_effect": min(effects.values()),
        "pair_gate": pair_gate,
        "pair_details": pair_details,
        "surface_duplicate_veto": surface_veto,
        "orbit_digest": hashlib.sha256(
            json.dumps(
                {
                    reading: [format(value, ".17g") for value in reading_scores[reading]]
                    for reading in READINGS
                },
                sort_keys=True,
            ).encode()
        ).hexdigest(),
    }


def evaluate(panel: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    primary = score_panel(panel)
    leave_one_out: dict[str, Any] = {}
    for omitted in CHANNELS:
        retained = tuple(channel for channel in CHANNELS if channel != omitted)
        reduced = score_panel(panel, retained)
        leave_one_out[omitted] = {
            "retained_channels": list(retained),
            "exact_tail_count": reduced["exact_tail_count"],
            "exact_p": reduced["exact_p"],
            "target_synchronous_z": reduced["target_synchronous_z"],
        }
    gates = {
        "complete_support": all(len(panel[reading]) == 9 for reading in READINGS),
        "surface_duplicate_veto": all(primary["surface_duplicate_veto"].values()),
        "primary_exact_p": primary["exact_p"] <= PRIMARY_P_LIMIT + EPS,
        "all_reading_rank": all(rank <= 3 for rank in primary["reading_ranks"].values()),
        "minimum_effect": primary["minimum_effect"] >= 0.10 - EPS,
        "all_target_pairs_above_median": all(primary["pair_gate"].values()),
        "all_channel_deletions": all(item["exact_p"] <= PRIMARY_P_LIMIT + EPS for item in leave_one_out.values()),
    }
    return {
        "primary": primary,
        "leave_one_channel_out": leave_one_out,
        "gates": gates,
        "pass": all(gates.values()),
    }


def synthetic_panel(kind: str) -> dict[str, list[dict[str, Any]]]:
    planted = [
        feature("A", False, ("BARE",), f"surface-{i}") if i in TARGET else
        feature(chr(66 + i), bool(i % 2), (f"ROLE_{i}",), f"surface-{i}")
        for i in range(9)
    ]
    negative = [
        feature("A", False, ("R0",), "n0"),
        feature("Z", True, ("SAME",), "n1"),
        feature("Z", True, ("SAME",), "n2"),
        feature("B", True, ("R3", "X"), "n3"),
        feature("Z", True, ("SAME",), "n4"),
        feature("C", False, ("R5",), "n5"),
        feature("D", True, ("R6",), "n6"),
        feature("E", False, ("R7",), "n7"),
        feature("F", True, ("R8", "Y"), "n8"),
    ]
    channel_only = [
        feature("A" if i in TARGET else chr(66 + i), bool(i % 2), (f"ROLE_{i}",), f"c-{i}")
        for i in range(9)
    ]
    pair_leverage = [
        feature("A", False, ("SAME",), "p0"),
        feature("B", True, ("R1",), "p1"),
        feature("C", False, ("R2",), "p2"),
        feature("A", False, ("SAME",), "p3"),
        feature("D", True, ("R4",), "p4"),
        feature("E", False, ("R5",), "p5"),
        feature("F", True, ("R6",), "p6"),
        feature("G", False, ("R7",), "p7"),
        feature("H", True, ("DIFFERENT", "LONG"), "p8"),
    ]
    if kind == "planted":
        return {reading: [dict(item) for item in planted] for reading in READINGS}
    if kind == "negative":
        return {reading: [dict(item) for item in negative] for reading in READINGS}
    if kind == "channel_only":
        return {reading: [dict(item) for item in channel_only] for reading in READINGS}
    if kind == "pair_leverage":
        return {reading: [dict(item) for item in pair_leverage] for reading in READINGS}
    if kind == "reading_disagreement":
        return {
            "ZL3b": [dict(item) for item in planted],
            "IT2a": [dict(item) for item in planted],
            "RF1b": [dict(item) for item in negative],
        }
    if kind == "degenerate":
        row = [feature("A", False, ("SAME",), f"d-{i}") for i in range(9)]
        return {reading: [dict(item) for item in row] for reading in READINGS}
    raise ValueError(kind)


def run_controls() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for kind in ("planted", "negative", "channel_only", "pair_leverage", "reading_disagreement"):
        results[kind] = evaluate(synthetic_panel(kind))
    degenerate_rejected = False
    try:
        evaluate(synthetic_panel("degenerate"))
    except DegenerateOrbit:
        degenerate_rejected = True
    deterministic = evaluate(synthetic_panel("planted")) == results["planted"]
    assertions = {
        "combo_count_84": results["planted"]["primary"]["combo_count"] == 84,
        "planted_passes": results["planted"]["pass"],
        "planted_unique_tail": results["planted"]["primary"]["exact_tail_count"] == 1,
        "negative_fails": not results["negative"]["pass"],
        "channel_only_fails_deletion": not results["channel_only"]["gates"]["all_channel_deletions"],
        "pair_leverage_fails_pair_gate": not results["pair_leverage"]["gates"]["all_target_pairs_above_median"],
        "reading_disagreement_fails": not results["reading_disagreement"]["pass"],
        "degenerate_rejected": degenerate_rejected,
        "deterministic_repeat": deterministic,
    }
    payload = {
        "experiment": "F76S001",
        "mode": "CONTROLS",
        "status": "PASS_CONTROLS_TARGET_STILL_FORBIDDEN" if all(assertions.values()) else "FAIL_CONTROLS",
        "assertions": assertions,
        "results": results,
        "bindings": {
            "input_sha256": sha256(INPUT),
            "source_audit_sha256": sha256(SOURCE_AUDIT),
            "preregistration_sha256": sha256(PREREG),
            "runner_sha256": sha256(Path(__file__)),
            "validator_sha256": sha256(VALIDATOR),
        },
    }
    payload["all_controls_pass"] = all(assertions.values()) and payload["bindings"]["input_sha256"] == INPUT_SHA256 and payload["bindings"]["source_audit_sha256"] == SOURCE_SHA256
    if not payload["all_controls_pass"]:
        payload["status"] = "FAIL_CONTROLS"
    write_json(CONTROL_RESULT, payload)
    CONTROL_REPORT.write_text(
        "# F76S001 anonymous control report\n\n"
        f"Status: **{payload['status']}**\n\n"
        f"All {len(assertions)} frozen assertions pass: `{payload['all_controls_pass']}`. "
        "The target was not loaded or scored. The control artifact binds the input, "
        "source audit, preregistration, production runner, and independent validator.\n",
        encoding="utf-8",
    )
    return payload


def load_target_panel() -> dict[str, list[dict[str, Any]]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["edition"] in READINGS and row["page"] == "f76r":
                rows[(row["edition"], row["locus"])] = row
    panel: dict[str, list[dict[str, Any]]] = {reading: [] for reading in READINGS}
    for reading in READINGS:
        for position, _mark_locus, prose_locus, _mark in PAIRING:
            row = rows.get((reading, prose_locus))
            if row is None or row["grammar_scope"] != "CONFIRMED_PROSE":
                raise RuntimeError(f"missing prose row: {reading} {prose_locus}")
            words = row["surface"].split()
            role_words = row["role_sequence"].split()
            if not words or not role_words:
                raise RuntimeError(f"empty opening: {reading} {prose_locus}")
            roles = tuple(role_words[0].split("+"))
            q_state = roles[0].startswith("Q_")
            base_roles = tuple(role[2:] if role.startswith("Q_") else role for role in roles)
            if not base_roles:
                raise RuntimeError(f"empty role path: {reading} {prose_locus}")
            panel[reading].append(feature(row["line_carrier"], q_state, base_roles, words[0]))
            if position != len(panel[reading]):
                raise RuntimeError("position drift")
    return panel


def verify_bindings() -> dict[str, str]:
    if not CONTROL_RESULT.is_file():
        raise RuntimeError("control result absent")
    controls = json.loads(CONTROL_RESULT.read_text(encoding="utf-8"))
    if not controls.get("all_controls_pass"):
        raise RuntimeError("control gate not passed")
    current = {
        "input_sha256": sha256(INPUT),
        "source_audit_sha256": sha256(SOURCE_AUDIT),
        "preregistration_sha256": sha256(PREREG),
        "runner_sha256": sha256(Path(__file__)),
        "validator_sha256": sha256(VALIDATOR),
    }
    if current != controls["bindings"]:
        raise RuntimeError("control binding drift")
    return current


def run_target() -> dict[str, Any]:
    bindings = verify_bindings()
    panel = load_target_panel()
    result = evaluate(panel)
    payload = {
        "experiment": "F76S001",
        "mode": "TARGET",
        "status": "EXPLORATORY_SELECTOR_CANDIDATE" if result["pass"] else "FINAL_NONCONFIRMATION",
        "pairing": [
            {"position": position, "mark_locus": mark_locus, "prose_locus": prose_locus, "mark": mark}
            for position, mark_locus, prose_locus, mark in PAIRING
        ],
        "result": result,
        "bindings": bindings,
        "claim_ceiling": "root-free repeated-s line-entry association only; no ownership, glyph meaning, lexeme, plaintext, or translation",
    }
    write_json(TARGET_RESULT, payload)
    primary = result["primary"]
    TARGET_REPORT.write_text(
        "# F76S001 repeated-margin line-entry selector\n\n"
        f"Status: **{payload['status']}**\n\n"
        f"The repeated-s triplet has exact synchronous p `{primary['exact_p']:.9f}`, "
        f"minimum effect `{primary['minimum_effect']:+.6f}`, and reading ranks "
        f"`{primary['reading_ranks']}`. The full frozen decision is `{result['pass']}`.\n\n"
        "This fixed exploratory test uses only root-free line-entry features. It cannot "
        "establish mark ownership, glyph meaning, a word class, lexeme, plaintext, or translation.\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--controls", action="store_true")
    modes.add_argument("--target", action="store_true")
    args = parser.parse_args()
    payload = run_controls() if args.controls else run_target()
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
