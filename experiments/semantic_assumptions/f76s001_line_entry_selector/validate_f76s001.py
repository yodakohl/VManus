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
TARGET_JSON = HERE / "TARGET_RESULT.json"
OUTPUT_JSON = HERE / "INDEPENDENT_VALIDATION.json"
OUTPUT_REPORT = ROOT / "experiments/semantic_assumptions/results/f76s001_line_entry_selector_independent_validation_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
CHANNELS = ("carrier", "q_state", "role_path")
LOCI = ("f76r.5", "f76r.8", "f76r.11", "f76r.15", "f76r.19", "f76r.23", "f76r.28", "f76r.32", "f76r.38")
TARGET = (0, 3, 8)
COMBOS = tuple(itertools.combinations(range(9), 3))
EPS = 1e-12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    found: dict[tuple[str, str], dict[str, str]] = {}
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["edition"], row["locus"])
            if key in wanted:
                found[key] = row
    output: dict[str, list[dict[str, Any]]] = {}
    for reading in READINGS:
        items = []
        for locus in LOCI:
            row = found[(reading, locus)]
            surfaces = row["surface"].split()
            roles = tuple(row["role_sequence"].split()[0].split("+"))
            items.append({
                "carrier": row["line_carrier"],
                "q_state": roles[0].startswith("Q_"),
                "role_path": tuple(value.removeprefix("Q_") for value in roles),
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
        all_scores[reading] = scores
        all_z[reading] = [(value - mean) / sd for value in scores]
    offset = COMBOS.index(TARGET)
    sync = [min(all_z[r][i] for r in READINGS) for i in range(84)]
    observed = sync[offset]
    exact_tail = sum(value >= observed - EPS for value in sync)
    ranks = {
        r: 1 + sum(value > all_scores[r][offset] + EPS for value in all_scores[r])
        for r in READINGS
    }
    effects = {
        r: all_scores[r][offset] - statistics.median(all_scores[r])
        for r in READINGS
    }
    pair_gate = {}
    for r in READINGS:
        all_pairs = [similarity(panel[r][i], panel[r][j], channels) for i, j in itertools.combinations(range(9), 2)]
        target_pairs = [similarity(panel[r][i], panel[r][j], channels) for i, j in itertools.combinations(TARGET, 2)]
        pair_gate[r] = all(value > statistics.median(all_pairs) + EPS for value in target_pairs)
    orbit_digest = hashlib.sha256(json.dumps(
        {r: [format(value, ".17g") for value in all_scores[r]] for r in READINGS},
        sort_keys=True,
    ).encode()).hexdigest()
    return {
        "exact_tail_count": exact_tail,
        "exact_p": exact_tail / 84,
        "target_synchronous_z": observed,
        "reading_ranks": ranks,
        "reading_effects": effects,
        "minimum_effect": min(effects.values()),
        "pair_gate": pair_gate,
        "orbit_digest": orbit_digest,
    }


def main() -> None:
    stored = json.loads(TARGET_JSON.read_text(encoding="utf-8"))
    panel = load()
    primary = reconstruct(panel, CHANNELS)
    expected = stored["result"]["primary"]
    checks = {
        "input_hash": digest(INPUT) == stored["bindings"]["input_sha256"],
        "combo_count": expected["combo_count"] == 84,
        "exact_tail": primary["exact_tail_count"] == expected["exact_tail_count"],
        "exact_p": math.isclose(primary["exact_p"], expected["exact_p"], abs_tol=1e-12),
        "synchronous_z": math.isclose(primary["target_synchronous_z"], expected["target_synchronous_z"], abs_tol=1e-12),
        "ranks": primary["reading_ranks"] == expected["reading_ranks"],
        "effects": all(math.isclose(primary["reading_effects"][r], expected["reading_effects"][r], abs_tol=1e-12) for r in READINGS),
        "minimum_effect": math.isclose(primary["minimum_effect"], expected["minimum_effect"], abs_tol=1e-12),
        "pair_gate": primary["pair_gate"] == expected["pair_gate"],
        "orbit_digest": primary["orbit_digest"] == expected["orbit_digest"],
        "surface_veto": all(len({panel[r][i]["surface"] for i in TARGET}) == 3 for r in READINGS),
    }
    loo = {}
    for omitted in CHANNELS:
        retained = tuple(channel for channel in CHANNELS if channel != omitted)
        rebuilt = reconstruct(panel, retained)
        saved = stored["result"]["leave_one_channel_out"][omitted]
        valid = rebuilt["exact_tail_count"] == saved["exact_tail_count"] and math.isclose(rebuilt["exact_p"], saved["exact_p"], abs_tol=1e-12)
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
