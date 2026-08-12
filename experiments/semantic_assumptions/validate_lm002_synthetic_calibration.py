#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
PANEL = BASE / "lm002_leaf_margin_cho_che_capacity_panel.tsv"
SPEC = ROOT / "experiments/semantic_assumptions/LM002_SYNTHETIC_CALIBRATION_SPEC.md"
RESULT = BASE / "lm002_synthetic_calibration.json"
REPORT = BASE / "lm002_synthetic_calibration_report.md"
OUT = BASE / "lm002_synthetic_calibration_validation.json"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("phase_quartile_side_cell", "phase_quire_cell")
FAMILIES = ("NULL", "DISTRIBUTED_FULL", "DISTRIBUTED_REDUCED", "ONE_CELL", "ONE_CURRIER", "ONE_PHASE", "PAGE_SIDE_ONLY", "QUIRE_ONLY", "TEXT_VOLUME_ONLY", "READING_DISAGREEMENT", "ONE_PHASE_REVERSED")
COUNTS = {"NULL": 64, **{name: 8 for name in FAMILIES if name != "NULL"}}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bit(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") & 1


def geometry(rows: list[dict]) -> dict:
    result = {}
    for view in VIEWS:
        groups = defaultdict(list)
        for row in rows: groups[row[view]].append(row)
        cells = []
        for key, values in sorted(groups.items()):
            if len({row["visual"] for row in values}) == 2:
                cells.append((key, sorted(values, key=lambda row: row["opaque_id"])))
        cell_options = []
        for _, values in cells:
            ids = [row["index"] for row in values]
            count = sum(row["visual"] for row in values)
            cell_options.append([(ids, frozenset(choice)) for choice in itertools.combinations(ids, count)])
        assignments = []
        for product in itertools.product(*cell_options):
            assignment = {row["index"]: row["visual"] for row in rows}
            for ids, selected in product:
                for row_id in ids: assignment[row_id] = int(row_id in selected)
            assignments.append(assignment)
        result[view] = (cells, assignments)
    return result


def contrasts(values: dict[int, int], assignment: dict[int, int], cells: list[tuple[str, list[dict]]]) -> list[Fraction]:
    output = []
    for _, members in cells:
        positive = [values[row["index"]] for row in members if assignment[row["index"]]]
        negative = [values[row["index"]] for row in members if not assignment[row["index"]]]
        output.append(Fraction(sum(positive), len(positive)) - Fraction(sum(negative), len(negative)))
    return output


def score(channels: dict[str, dict[int, int]], rows: list[dict], geom: dict, view: str) -> dict:
    cells, orbit = geom[view]
    observed = {row["index"]: row["visual"] for row in rows}
    cell_values = {reading: contrasts(channels[reading], observed, cells) for reading in READINGS}
    effects = {reading: sum(cell_values[reading], Fraction()) / len(cells) for reading in READINGS}
    direction = 1 if all(effects[r] > 0 for r in READINGS) else -1 if all(effects[r] < 0 for r in READINGS) else 0
    statistic = min(abs(effects[r]) for r in READINGS) if direction else Fraction(-1)
    tail = 0
    for assignment in orbit:
        current = {}
        for reading in READINGS:
            parts = contrasts(channels[reading], assignment, cells)
            current[reading] = sum(parts, Fraction()) / len(parts)
        if all(current[r] > 0 for r in READINGS) or all(current[r] < 0 for r in READINGS):
            candidate = min(abs(current[r]) for r in READINGS)
        else:
            candidate = Fraction(-1)
        tail += candidate >= statistic
    signs = {reading: sum(value * direction > 0 for value in cell_values[reading]) if direction else 0 for reading in READINGS}
    concentration = {}
    for reading in READINGS:
        total = sum(abs(value) for value in cell_values[reading])
        concentration[reading] = max(abs(value) for value in cell_values[reading]) / total if total else Fraction(1)
    return {"effects": effects, "direction": direction, "T": statistic, "tail": tail, "orbit": len(orbit), "p": Fraction(tail, len(orbit)), "signs": signs, "concentration": concentration}


def blocks(channels: dict[str, dict[int, int]], rows: list[dict], fields: tuple[str, ...], direction: int, allowed: set[int] | None = None) -> dict[str, list[Fraction]]:
    groups = defaultdict(list)
    for row in rows:
        if allowed is None or row["index"] in allowed:
            groups[tuple(row[field] for field in fields)].append(row)
    output = {reading: [] for reading in READINGS}
    for _, members in sorted(groups.items()):
        if len({row["visual"] for row in members}) != 2: continue
        for reading in READINGS:
            positive = [channels[reading][row["index"]] for row in members if row["visual"]]
            negative = [channels[reading][row["index"]] for row in members if not row["visual"]]
            output[reading].append(direction * (Fraction(sum(positive), len(positive)) - Fraction(sum(negative), len(negative))))
    return output


def evaluate(em: dict, threshold: dict, volume: dict, rows: list[dict], geom: dict) -> dict:
    em_scores = {view: score(em, rows, geom, view) for view in VIEWS}
    threshold_scores = {view: score(threshold, rows, geom, view) for view in VIEWS}
    volume_channels = {reading: volume for reading in READINGS}
    volume_scores = {view: score(volume_channels, rows, geom, view) for view in VIEWS}
    direction = em_scores[VIEWS[0]]["direction"]
    mobile = {row["index"] for _, members in geom[VIEWS[0]][0] for row in members}
    currier = blocks(em, rows, ("currier",), direction, mobile)
    phase_currier = blocks(em, rows, ("source_phase", "currier"), direction)
    gates = {
        "em_p_both": all(em_scores[view]["p"] <= Fraction(1, 100) for view in VIEWS),
        "em_effect_both": all(em_scores[view]["T"] >= Fraction(1, 4) for view in VIEWS),
        "same_nonzero_direction": direction != 0 and all(em_scores[view]["direction"] == direction for view in VIEWS),
        "four_of_five_cells_each_reading": all(em_scores[view]["signs"][reading] >= 4 for view in VIEWS for reading in READINGS),
        "both_curriers_same_direction": all(len(currier[reading]) == 2 and all(value > 0 for value in currier[reading]) for reading in READINGS),
        "three_of_four_phase_currier_none_below_minus_point10": all(len(phase_currier[reading]) == 4 and sum(value > 0 for value in phase_currier[reading]) >= 3 and all(value >= Fraction(-1, 10) for value in phase_currier[reading]) for reading in READINGS),
        "cell_concentration_at_most_point40": all(em_scores[view]["concentration"][reading] <= Fraction(2, 5) for view in VIEWS for reading in READINGS),
        "threshold_robustness": all(threshold_scores[view]["direction"] == direction and threshold_scores[view]["T"] >= Fraction(1, 5) and threshold_scores[view]["p"] <= Fraction(1, 50) for view in VIEWS),
        "volume_not_aligned_at_point05": all(volume_scores[view]["p"] > Fraction(1, 20) for view in VIEWS),
    }
    return {"pass": all(gates.values()), "gates": gates, "em": em_scores, "threshold": threshold_scores, "volume": volume_scores}


def create(family: str, world: int, rows: list[dict], geom: dict) -> tuple[dict, dict, dict]:
    world_id = f"{family}_{world:03d}"
    visual = {row["index"]: row["visual"] for row in rows}
    em = {reading: dict(visual) for reading in READINGS}
    if family == "NULL":
        em = {reading: {row["index"]: bit(f"LM002|{world_id}|EM|{reading}|{row['opaque_id']}") for row in rows} for reading in READINGS}
        threshold = {reading: {row["index"]: bit(f"LM002|{world_id}|THRESHOLD|{reading}|{row['opaque_id']}") for row in rows} for reading in READINGS}
    else:
        if family == "DISTRIBUTED_REDUCED":
            mobile = {row["index"] for _, members in geom[VIEWS[0]][0] for row in members}
            candidates = sorted((hashlib.sha256(f"LM002_REDUCED|{row['opaque_id']}|{reading}".encode()).hexdigest(), row["index"], reading) for row in rows if row["index"] in mobile and row["visual"] for reading in READINGS)
            _, row_id, reading = candidates[world]
            em[reading][row_id] = 0
        elif family == "ONE_CELL":
            selected = geom[VIEWS[0]][0][world % 5][0]
            em = {reading: {row["index"]: row["visual"] if row[VIEWS[0]] == selected else 0 for row in rows} for reading in READINGS}
        elif family == "ONE_CURRIER":
            selected = "A" if world % 2 == 0 else "B"
            em = {reading: {row["index"]: row["visual"] if row["currier"] == selected else 1 - row["visual"] for row in rows} for reading in READINGS}
        elif family == "ONE_PHASE":
            selected = ("LM001X", "LM001Y", "LM001_HELD")[world % 3]
            em = {reading: {row["index"]: row["visual"] if row["source_phase"] == selected else 0 for row in rows} for reading in READINGS}
        elif family == "PAGE_SIDE_ONLY":
            em = {reading: {row["index"]: int(row["page_side"] == "r") for row in rows} for reading in READINGS}
        elif family == "QUIRE_ONLY":
            em = {reading: {row["index"]: bit(f"LM002_QUIRE|{world_id}|{row['quire']}") for row in rows} for reading in READINGS}
        elif family == "READING_DISAGREEMENT":
            reverse = READINGS[(world + 1) % 3]
            em[reverse] = {key: 1 - value for key, value in visual.items()}
        elif family == "ONE_PHASE_REVERSED":
            selected = ("LM001X", "LM001Y", "LM001_HELD")[world % 3]
            em = {reading: {row["index"]: 1 - row["visual"] if row["source_phase"] == selected else row["visual"] for row in rows} for reading in READINGS}
        threshold = {reading: dict(em[reading]) for reading in READINGS}
    volume = dict(visual) if family == "TEXT_VOLUME_ONLY" else {row["index"]: 0 for row in rows}
    return em, threshold, volume


def public(family: str, world: int, result: dict) -> dict:
    def compact(values: dict) -> dict:
        return {view: {"direction": values[view]["direction"], "T": float(values[view]["T"]), "tail": values[view]["tail"], "orbit": values[view]["orbit"], "p": float(values[view]["p"])} for view in VIEWS}
    return {"world_id": f"{family}_{world:03d}", "family": family, "full_pass": result["pass"], "gates": result["gates"], "em": compact(result["em"]), "threshold": compact(result["threshold"]), "volume": compact(result["volume"])}


def reconstruct(row_order: list[dict]) -> tuple[list[dict], dict]:
    rows = [dict(row) for row in row_order]
    for index, row in enumerate(rows): row["index"] = index; row["visual"] = int(row["leaf_margin_state"] == "TOOTHED")
    geom = geometry(rows)
    worlds = []
    for family in FAMILIES:
        for world in range(COUNTS[family]):
            worlds.append(public(family, world, evaluate(*create(family, world, rows, geom), rows, geom)))
    passes = {family: sum(item["full_pass"] for item in worlds if item["family"] == family) for family in FAMILIES}
    return worlds, passes


def main() -> None:
    checks = []
    panel_rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    worlds, passes = reconstruct(panel_rows)
    assert len(worlds) == 144 and len({row["world_id"] for row in worlds}) == 144
    checks.append("exact_144_world_registry")
    assert passes == {"NULL": 0, "DISTRIBUTED_FULL": 8, "DISTRIBUTED_REDUCED": 7, "ONE_CELL": 0, "ONE_CURRIER": 0, "ONE_PHASE": 0, "PAGE_SIDE_ONLY": 0, "QUIRE_ONLY": 0, "TEXT_VOLUME_ONLY": 0, "READING_DISAGREEMENT": 0, "ONE_PHASE_REVERSED": 0}
    checks.append("independent_family_pass_counts")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["worlds"] == worlds and stored["family_passes"] == passes
    checks.append("all_world_gates_and_diagnostics")
    assert stored["status"] == "STOP_SYNTHETIC_INSTRUMENT_FAILED" and stored["decision"] == "FORBID_FORMAL_TARGET_ACCESS"
    assert stored["gates"]["eight_of_eight_reduced"] is False and sum(stored["gates"].values()) == 6
    checks.append("frozen_reduced_power_stop")
    reversed_worlds, reversed_passes = reconstruct(list(reversed(panel_rows)))
    assert reversed_worlds == worlds and reversed_passes == passes
    checks.append("row_order_invariance")
    # A global outcome complement is an exact direction-symmetry check.
    rows = [dict(row) for row in panel_rows]
    for index, row in enumerate(rows): row["index"] = index; row["visual"] = int(row["leaf_margin_state"] == "TOOTHED")
    geom = geometry(rows)
    full = create("DISTRIBUTED_FULL", 0, rows, geom)
    complemented = ({reading: {key: 1 - value for key, value in full[0][reading].items()} for reading in READINGS}, {reading: {key: 1 - value for key, value in full[1][reading].items()} for reading in READINGS}, full[2])
    assert evaluate(*full, rows, geom)["pass"] is True and evaluate(*complemented, rows, geom)["pass"] is True
    checks.append("global_state_complement_invariance")
    assert stored["access"] == {"formal_target_rows_accessed": False, "formal_target_table_opened": False, "real_state_scores_computed": False}
    checks.append("formal_target_access_seal")
    expected_report = "# LM002 synthetic calibration\n\nStatus: **STOP_SYNTHETIC_INSTRUMENT_FAILED**.\n\nFamily full-pass counts: " + ", ".join(f"`{key}` {passes[key]}/{COUNTS[key]}" for key in FAMILIES) + ".\n\nThe formal target table was not opened or parsed. The instrument failed its frozen calibration and formal-target access remains forbidden. No association, leaf word, plant identity, plaintext, meaning, or translation follows.\n"
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("exact_report_reconstruction")
    assert stored["inputs"] == {str(PANEL.relative_to(ROOT)): digest(PANEL), str(SPEC.relative_to(ROOT)): digest(SPEC)}
    checks.append("input_bindings")
    out = {"experiment": "LM002_SYNTHETIC_CALIBRATION_VALIDATION", "status": "PASS_9_CHECK_INDEPENDENT_STOP_RECONSTRUCTION", "check_count": len(checks), "checks": checks, "validated_result_sha256": digest(RESULT), "validated_report_sha256": digest(REPORT), "formal_target_table_opened_by_validator": False, "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
