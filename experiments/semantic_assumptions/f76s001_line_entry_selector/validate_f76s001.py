#!/usr/bin/env python3
"""Nonimporting reconstruction of the frozen F76S001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
SOURCE_ALIGNMENT_AUDIT = ROOT / "experiments/semantic_assumptions/results/f76r_keylike_sequence_source_audit.md"
SOURCE_CROSSWALK = ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv"
PREREG = ROOT / "experiments/semantic_assumptions/hypotheses/F76S001_LINE_ENTRY_SELECTOR_PREREGISTRATION.md"
AMENDMENT = ROOT / "experiments/semantic_assumptions/hypotheses/F76S001_PRESCORE_EXECUTION_AMENDMENT.md"
RUNNER = HERE / "run_f76s001.py"
VALIDATOR = Path(__file__).resolve()
CONTROL_RESULT = HERE / "CONTROL_RESULT.json"
TARGET_JSON = HERE / "TARGET_RESULT.json"
OUTPUT_JSON = HERE / "INDEPENDENT_VALIDATION.json"
OUTPUT_REPORT = ROOT / "experiments/semantic_assumptions/results/f76s001_line_entry_selector_independent_validation_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
CHANNELS = ("carrier", "q_state", "role_path")
LOCI = ("f76r.5", "f76r.8", "f76r.11", "f76r.15", "f76r.19", "f76r.23", "f76r.28", "f76r.32", "f76r.38")
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
EPS = 1e-12
INPUT_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
SOURCE_ALIGNMENT_AUDIT_SHA256 = "27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744"
SOURCE_CROSSWALK_SHA256 = "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc"
CLAIM_CEILING = (
    "root-free repeated-s line-entry association under the fixed human-editorial "
    "aligned-line pairing only; no authorial ownership, selector function, paragraph "
    "segmentation, reuse outside this panel, glyph meaning, sound, lexeme, plaintext, "
    "language, or translation"
)
EXPECTED_CONTROL_ASSERTIONS = {
    "combo_count_84",
    "planted_passes",
    "planted_unique_tail",
    "negative_fails",
    "channel_only_fails_deletion",
    "pair_leverage_fails_pair_gate",
    "reading_disagreement_fails",
    "conservative_four_way_top_tie",
    "degenerate_rejected",
    "deterministic_repeat",
    "row_contract_accepts_exact_27",
    "row_contract_rejects_duplicate",
    "row_contract_rejects_missing",
    "row_contract_rejects_scope_drift",
    "row_contract_rejects_page_drift",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def control_bindings() -> dict[str, str]:
    return {
        "input_sha256": digest(INPUT),
        "source_alignment_audit_sha256": digest(SOURCE_ALIGNMENT_AUDIT),
        "source_crosswalk_sha256": digest(SOURCE_CROSSWALK),
        "preregistration_sha256": digest(PREREG),
        "prescore_amendment_sha256": digest(AMENDMENT),
        "runner_sha256": digest(RUNNER),
        "validator_sha256": digest(VALIDATOR),
    }


def expected_pairing() -> list[dict[str, Any]]:
    return [
        {"position": position, "mark_locus": mark_locus, "prose_locus": prose_locus, "mark": mark}
        for position, mark_locus, prose_locus, mark in PAIRING
    ]


def equivalent(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=EPS)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equivalent(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(equivalent(a, b) for a, b in zip(left, right))
    return left == right


def edit_distance(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + (a[i - 1] != b[j - 1]),
            )
    return table[-1][-1]


def load() -> dict[str, list[dict[str, Any]]]:
    wanted = {(reading, locus) for reading in READINGS for locus in LOCI}
    found: dict[tuple[str, str], list[dict[str, str]]] = {key: [] for key in wanted}
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["edition"], row["locus"])
            if key in wanted:
                found[key].append(row)
    for key, matches in found.items():
        if len(matches) != 1:
            raise RuntimeError(f"expected exactly one input row for {key}, found {len(matches)}")
        if matches[0]["page"] != "f76r" or matches[0]["grammar_scope"] != "CONFIRMED_PROSE":
            raise RuntimeError(f"target row scope drift: {key}")
    output: dict[str, list[dict[str, Any]]] = {}
    for reading in READINGS:
        items = []
        for locus in LOCI:
            row = found[(reading, locus)][0]
            surfaces = row["surface"].split()
            role_words = row["role_sequence"].split()
            if not surfaces or not role_words:
                raise RuntimeError(f"empty opening: {reading} {locus}")
            roles = tuple(role_words[0].split("+"))
            base_roles = tuple(value.removeprefix("Q_") for value in roles)
            if not base_roles:
                raise RuntimeError(f"empty role path: {reading} {locus}")
            items.append({
                "carrier": row["line_carrier"],
                "q_state": roles[0].startswith("Q_"),
                "role_path": base_roles,
                "surface": surfaces[0],
            })
        output[reading] = items
    return output


def similarity(a: dict[str, Any], b: dict[str, Any], channels: tuple[str, ...]) -> float:
    values = {
        "carrier": float(a["carrier"] == b["carrier"]),
        "q_state": float(a["q_state"] == b["q_state"]),
        "role_path": 1.0 - edit_distance(a["role_path"], b["role_path"]) / max(len(a["role_path"]), len(b["role_path"])),
    }
    return statistics.fmean(values[name] for name in channels)


def reconstruct(panel: dict[str, list[dict[str, Any]]], channels: tuple[str, ...]) -> dict[str, Any]:
    all_scores: dict[str, list[float]] = {}
    all_z: dict[str, list[float]] = {}
    for reading in READINGS:
        scores = []
        for combo in COMBOS:
            scores.append(statistics.fmean(
                similarity(panel[reading][i], panel[reading][j], channels)
                for i, j in itertools.combinations(combo, 2)
            ))
        mean = statistics.fmean(scores)
        sd = statistics.pstdev(scores)
        if sd <= EPS:
            raise RuntimeError(f"{reading}: degenerate orbit")
        all_scores[reading] = scores
        all_z[reading] = [(value - mean) / sd for value in scores]
    offset = COMBOS.index(TARGET)
    sync = [min(all_z[r][i] for r in READINGS) for i in range(84)]
    observed = sync[offset]
    exact_tail = sum(value >= observed - EPS for value in sync)
    strictly_greater = sum(value > observed + EPS for value in sync)
    tied_at_target = sum(abs(value - observed) <= EPS for value in sync)
    ranks = {
        r: 1 + sum(value > all_scores[r][offset] + EPS for value in all_scores[r])
        for r in READINGS
    }
    effects = {
        r: all_scores[r][offset] - statistics.median(all_scores[r])
        for r in READINGS
    }
    pair_gate = {}
    pair_details = {}
    for r in READINGS:
        all_pairs = [similarity(panel[r][i], panel[r][j], channels) for i, j in itertools.combinations(range(9), 2)]
        target_pairs = [similarity(panel[r][i], panel[r][j], channels) for i, j in itertools.combinations(TARGET, 2)]
        median_pair = statistics.median(all_pairs)
        pair_gate[r] = all(value > median_pair + EPS for value in target_pairs)
        pair_details[r] = {"all_pair_median": median_pair, "target_pair_scores": target_pairs}
    orbit_digest = hashlib.sha256(json.dumps(
        {r: [format(value, ".17g") for value in all_scores[r]] for r in READINGS},
        sort_keys=True,
    ).encode()).hexdigest()
    return {
        "channels": list(channels),
        "combo_count": len(COMBOS),
        "target_positions_one_based": [index + 1 for index in TARGET],
        "exact_tail_count": exact_tail,
        "strictly_greater_count": strictly_greater,
        "tied_at_target_count": tied_at_target,
        "exact_p": exact_tail / 84,
        "target_synchronous_z": observed,
        "reading_ranks": ranks,
        "reading_effects": effects,
        "minimum_effect": min(effects.values()),
        "pair_gate": pair_gate,
        "pair_details": pair_details,
        "surface_duplicate_veto": {
            r: len({panel[r][i]["surface"] for i in TARGET}) == 3
            for r in READINGS
        },
        "orbit_digest": orbit_digest,
    }


def main() -> None:
    stored = json.loads(TARGET_JSON.read_text(encoding="utf-8"))
    controls = json.loads(CONTROL_RESULT.read_text(encoding="utf-8"))
    current_control_bindings = control_bindings()
    current_target_bindings = {
        **current_control_bindings,
        "control_result_sha256": digest(CONTROL_RESULT),
    }
    panel = load()
    primary = reconstruct(panel, CHANNELS)
    expected = stored["result"]["primary"]
    checks = {
        "frozen_source_hashes": (
            current_control_bindings["input_sha256"] == INPUT_SHA256
            and current_control_bindings["source_alignment_audit_sha256"] == SOURCE_ALIGNMENT_AUDIT_SHA256
            and current_control_bindings["source_crosswalk_sha256"] == SOURCE_CROSSWALK_SHA256
        ),
        "control_identity": controls.get("experiment") == "F76S001" and controls.get("mode") == "CONTROLS",
        "control_status": controls.get("status") == "PASS_CONTROLS_TARGET_STILL_FORBIDDEN",
        "control_assertions": (
            controls.get("all_controls_pass") is True
            and set(controls.get("assertions", {})) == EXPECTED_CONTROL_ASSERTIONS
            and all(controls.get("assertions", {}).values())
        ),
        "control_bindings": controls.get("bindings") == current_control_bindings,
        "target_identity": stored.get("experiment") == "F76S001" and stored.get("mode") == "TARGET",
        "target_bindings": stored.get("bindings") == current_target_bindings,
        "target_pairing": stored.get("pairing") == expected_pairing(),
        "target_claim_ceiling": stored.get("claim_ceiling") == CLAIM_CEILING,
        "row_cardinality_and_scope": all(len(panel[r]) == 9 for r in READINGS),
        "combo_count": expected["combo_count"] == 84,
        "primary_complete": equivalent(primary, expected),
        "exact_tail": primary["exact_tail_count"] == expected["exact_tail_count"],
        "exact_p": math.isclose(primary["exact_p"], expected["exact_p"], abs_tol=1e-12),
        "synchronous_z": math.isclose(primary["target_synchronous_z"], expected["target_synchronous_z"], abs_tol=1e-12),
        "ranks": primary["reading_ranks"] == expected["reading_ranks"],
        "effects": all(math.isclose(primary["reading_effects"][r], expected["reading_effects"][r], abs_tol=1e-12) for r in READINGS),
        "minimum_effect": math.isclose(primary["minimum_effect"], expected["minimum_effect"], abs_tol=1e-12),
        "pair_gate": primary["pair_gate"] == expected["pair_gate"],
        "orbit_digest": primary["orbit_digest"] == expected["orbit_digest"],
        "surface_veto": all(primary["surface_duplicate_veto"].values()),
    }
    loo = {}
    for omitted in CHANNELS:
        retained = tuple(channel for channel in CHANNELS if channel != omitted)
        rebuilt = reconstruct(panel, retained)
        saved = stored["result"]["leave_one_channel_out"][omitted]
        rebuilt_saved_shape = {
            "retained_channels": list(retained),
            "exact_tail_count": rebuilt["exact_tail_count"],
            "exact_p": rebuilt["exact_p"],
            "target_synchronous_z": rebuilt["target_synchronous_z"],
        }
        valid = equivalent(rebuilt_saved_shape, saved)
        checks[f"loo_{omitted}"] = valid
        loo[omitted] = rebuilt
    gates = {
        "complete_support": all(len(panel[r]) == 9 for r in READINGS),
        "surface_duplicate_veto": checks["surface_veto"],
        "primary_exact_p": primary["exact_p"] <= 4 / 84 + EPS,
        "all_reading_rank": all(value <= 3 for value in primary["reading_ranks"].values()),
        "minimum_effect": primary["minimum_effect"] >= 0.10 - EPS,
        "all_target_pairs_above_median": all(primary["pair_gate"].values()),
        "all_channel_deletions": all(value["exact_p"] <= 4 / 84 + EPS for value in loo.values()),
    }
    checks["gates"] = gates == stored["result"]["gates"]
    checks["decision"] = all(gates.values()) == stored["result"]["pass"]
    expected_status = "EXPLORATORY_SELECTOR_CANDIDATE" if all(gates.values()) else "FINAL_NONCONFIRMATION"
    checks["target_status"] = stored.get("status") == expected_status
    payload = {
        "experiment": "F76S001",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION" if all(checks.values()) else "FAIL_INDEPENDENT_RECONSTRUCTION",
        "checks": checks,
        "check_count": len(checks),
        "all_checks_pass": all(checks.values()),
        "target_result_sha256": digest(TARGET_JSON),
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(
        "# F76S001 independent validation\n\n"
        f"Status: **{payload['status']}**\n\n"
        f"A nonimporting implementation passes {len(checks)} checks over the input, all 84 synchronous scores, channel deletions, gates, and decision.\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
