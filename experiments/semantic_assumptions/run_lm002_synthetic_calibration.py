#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
PANEL = BASE / "lm002_leaf_margin_cho_che_capacity_panel.tsv"
SPEC = ROOT / "experiments/semantic_assumptions/LM002_SYNTHETIC_CALIBRATION_SPEC.md"
OUT = BASE / "lm002_synthetic_calibration.json"
REPORT = BASE / "lm002_synthetic_calibration_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("phase_quartile_side_cell", "phase_quire_cell")
FAMILIES = ("NULL", "DISTRIBUTED_FULL", "DISTRIBUTED_REDUCED", "ONE_CELL", "ONE_CURRIER", "ONE_PHASE", "PAGE_SIDE_ONLY", "QUIRE_ONLY", "TEXT_VOLUME_ONLY", "READING_DISAGREEMENT", "ONE_PHASE_REVERSED")
COUNTS = {"NULL": 64, **{name: 8 for name in FAMILIES if name != "NULL"}}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bit(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") & 1


def prepare(rows: list[dict]) -> dict:
    prepared = {}
    for view in VIEWS:
        grouped = defaultdict(list)
        for row in rows: grouped[row[view]].append(row)
        cells = []
        for key, values in sorted(grouped.items()):
            if len({row["visual"] for row in values}) == 2:
                values = sorted(values, key=lambda row: row["opaque_id"])
                cells.append((key, values))
        choices = []
        for _, values in cells:
            ids = [row["index"] for row in values]
            k = sum(row["visual"] for row in values)
            choices.append([(ids, frozenset(combo)) for combo in itertools.combinations(ids, k)])
        assignments = []
        for product in itertools.product(*choices):
            assigned = {row["index"]: row["visual"] for row in rows}
            for ids, toothed in product:
                for index in ids: assigned[index] = int(index in toothed)
            assignments.append(assigned)
        prepared[view] = {"cells": cells, "assignments": assignments}
    assert len(prepared[VIEWS[0]]["assignments"]) == 108
    assert len(prepared[VIEWS[1]]["assignments"]) == 324
    return prepared


def cell_scores(outcome: dict[int, int], assignment: dict[int, int], cells: list[tuple[str, list[dict]]]) -> list[Fraction]:
    scores = []
    for _, values in cells:
        toothed = [outcome[row["index"]] for row in values if assignment[row["index"]]]
        smooth = [outcome[row["index"]] for row in values if not assignment[row["index"]]]
        scores.append(Fraction(sum(toothed), len(toothed)) - Fraction(sum(smooth), len(smooth)))
    return scores


def channel_stats(outcomes: dict[str, dict[int, int]], rows: list[dict], prepared: dict, view: str) -> dict:
    cells = prepared[view]["cells"]
    observed = {row["index"]: row["visual"] for row in rows}
    effects, per_cells = {}, {}
    for reading in READINGS:
        values = cell_scores(outcomes[reading], observed, cells)
        per_cells[reading] = values
        effects[reading] = sum(values, Fraction()) / len(values)
    if all(effects[r] > 0 for r in READINGS): direction = 1
    elif all(effects[r] < 0 for r in READINGS): direction = -1
    else: direction = 0
    observed_t = min(abs(effects[r]) for r in READINGS) if direction else Fraction(-1)
    tail = 0
    for assignment in prepared[view]["assignments"]:
        assignment_effects = {}
        for reading in READINGS:
            vals = cell_scores(outcomes[reading], assignment, cells)
            assignment_effects[reading] = sum(vals, Fraction()) / len(vals)
        if all(assignment_effects[r] > 0 for r in READINGS) or all(assignment_effects[r] < 0 for r in READINGS):
            value = min(abs(assignment_effects[r]) for r in READINGS)
        else: value = Fraction(-1)
        tail += value >= observed_t
    orbit = len(prepared[view]["assignments"])
    signs = {reading: sum(value * direction > 0 for value in per_cells[reading]) if direction else 0 for reading in READINGS}
    concentration = {}
    for reading in READINGS:
        denominator = sum(abs(value) for value in per_cells[reading])
        concentration[reading] = max(abs(value) for value in per_cells[reading]) / denominator if denominator else Fraction(1)
    return {"effects": effects, "direction": direction, "T": observed_t, "tail": tail, "orbit": orbit, "p": Fraction(tail, orbit), "signs": signs, "concentration": concentration, "cells": per_cells}


def pooled_block_contrasts(outcomes: dict[str, dict[int, int]], rows: list[dict], keys: tuple[str, ...], direction: int, allowed: set[int] | None = None) -> dict[str, list[Fraction]]:
    grouped = defaultdict(list)
    for row in rows:
        if allowed is None or row["index"] in allowed:
            grouped[tuple(row[key] for key in keys)].append(row)
    result = {reading: [] for reading in READINGS}
    for _, values in sorted(grouped.items()):
        if len({row["visual"] for row in values}) != 2: continue
        for reading in READINGS:
            toothed = [outcomes[reading][row["index"]] for row in values if row["visual"]]
            smooth = [outcomes[reading][row["index"]] for row in values if not row["visual"]]
            result[reading].append(direction * (Fraction(sum(toothed), len(toothed)) - Fraction(sum(smooth), len(smooth))))
    return result


def evaluate(em: dict[str, dict[int, int]], threshold: dict[str, dict[int, int]], volume: dict[int, int], rows: list[dict], prepared: dict) -> dict:
    ems = {view: channel_stats(em, rows, prepared, view) for view in VIEWS}
    ths = {view: channel_stats(threshold, rows, prepared, view) for view in VIEWS}
    volume3 = {reading: volume for reading in READINGS}
    vols = {view: channel_stats(volume3, rows, prepared, view) for view in VIEWS}
    direction = ems[VIEWS[0]]["direction"]
    mobile_primary = {row["index"] for _, values in prepared[VIEWS[0]]["cells"] for row in values}
    currier = pooled_block_contrasts(em, rows, ("currier",), direction, mobile_primary)
    phase_currier = pooled_block_contrasts(em, rows, ("source_phase", "currier"), direction)
    gates = {
        "em_p_both": all(ems[view]["p"] <= Fraction(1, 100) for view in VIEWS),
        "em_effect_both": all(ems[view]["T"] >= Fraction(1, 4) for view in VIEWS),
        "same_nonzero_direction": direction != 0 and all(ems[view]["direction"] == direction for view in VIEWS),
        "four_of_five_cells_each_reading": all(ems[view]["signs"][reading] >= 4 for view in VIEWS for reading in READINGS),
        "both_curriers_same_direction": all(len(currier[reading]) == 2 and all(value > 0 for value in currier[reading]) for reading in READINGS),
        "three_of_four_phase_currier_none_below_minus_point10": all(len(phase_currier[reading]) == 4 and sum(value > 0 for value in phase_currier[reading]) >= 3 and all(value >= Fraction(-1, 10) for value in phase_currier[reading]) for reading in READINGS),
        "cell_concentration_at_most_point40": all(ems[view]["concentration"][reading] <= Fraction(2, 5) for view in VIEWS for reading in READINGS),
        "threshold_robustness": all(ths[view]["direction"] == direction and ths[view]["T"] >= Fraction(1, 5) and ths[view]["p"] <= Fraction(1, 50) for view in VIEWS),
        "volume_not_aligned_at_point05": all(vols[view]["p"] > Fraction(1, 20) for view in VIEWS),
    }
    return {"pass": all(gates.values()), "gates": gates, "em": ems, "threshold": ths, "volume": vols, "currier": currier, "phase_currier": phase_currier}


def make_world(family: str, index: int, rows: list[dict], prepared: dict) -> tuple[dict, dict, dict]:
    world_id = f"{family}_{index:03d}"
    visual = {row["index"]: row["visual"] for row in rows}
    em = {reading: {} for reading in READINGS}
    if family == "NULL":
        for reading in READINGS:
            for row in rows: em[reading][row["index"]] = bit(f"LM002|{world_id}|EM|{reading}|{row['opaque_id']}")
        threshold = {reading: {row["index"]: bit(f"LM002|{world_id}|THRESHOLD|{reading}|{row['opaque_id']}") for row in rows} for reading in READINGS}
    else:
        for reading in READINGS: em[reading] = dict(visual)
        if family == "DISTRIBUTED_REDUCED":
            mobile = {row["index"] for _, values in prepared[VIEWS[0]]["cells"] for row in values}
            pairs = [(hashlib.sha256(f"LM002_REDUCED|{row['opaque_id']}|{reading}".encode()).hexdigest(), row["index"], reading) for row in rows if row["index"] in mobile and row["visual"] for reading in READINGS]
            _, selected, reading = sorted(pairs)[index]
            em[reading][selected] = 0
        elif family == "ONE_CELL":
            selected = prepared[VIEWS[0]]["cells"][index % 5][0]
            for reading in READINGS:
                em[reading] = {row["index"]: row["visual"] if row[VIEWS[0]] == selected else 0 for row in rows}
        elif family == "ONE_CURRIER":
            selected = "A" if index % 2 == 0 else "B"
            for reading in READINGS: em[reading] = {row["index"]: row["visual"] if row["currier"] == selected else 1 - row["visual"] for row in rows}
        elif family == "ONE_PHASE":
            selected = ("LM001X", "LM001Y", "LM001_HELD")[index % 3]
            for reading in READINGS: em[reading] = {row["index"]: row["visual"] if row["source_phase"] == selected else 0 for row in rows}
        elif family == "PAGE_SIDE_ONLY":
            for reading in READINGS: em[reading] = {row["index"]: int(row["page_side"] == "r") for row in rows}
        elif family == "QUIRE_ONLY":
            for reading in READINGS: em[reading] = {row["index"]: bit(f"LM002_QUIRE|{world_id}|{row['quire']}") for row in rows}
        elif family == "READING_DISAGREEMENT":
            reversed_reading = READINGS[(index + 1) % 3]
            em[reversed_reading] = {key: 1 - value for key, value in visual.items()}
        elif family == "ONE_PHASE_REVERSED":
            selected = ("LM001X", "LM001Y", "LM001_HELD")[index % 3]
            for reading in READINGS: em[reading] = {row["index"]: (1 - row["visual"] if row["source_phase"] == selected else row["visual"]) for row in rows}
        threshold = {reading: dict(em[reading]) for reading in READINGS}
    volume = dict(visual) if family == "TEXT_VOLUME_ONLY" else {row["index"]: 0 for row in rows}
    return em, threshold, volume


def public_world(family: str, index: int, evaluated: dict) -> dict:
    def small(stats: dict) -> dict:
        return {view: {"direction": stats[view]["direction"], "T": float(stats[view]["T"]), "tail": stats[view]["tail"], "orbit": stats[view]["orbit"], "p": float(stats[view]["p"])} for view in VIEWS}
    return {"world_id": f"{family}_{index:03d}", "family": family, "full_pass": evaluated["pass"], "gates": evaluated["gates"], "em": small(evaluated["em"]), "threshold": small(evaluated["threshold"]), "volume": small(evaluated["volume"])}


def main() -> None:
    rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    for index, row in enumerate(rows): row["index"] = index; row["visual"] = int(row["leaf_margin_state"] == "TOOTHED")
    prepared = prepare(rows)
    worlds = []
    for family in FAMILIES:
        for index in range(COUNTS[family]):
            worlds.append(public_world(family, index, evaluate(*make_world(family, index, rows, prepared), rows, prepared)))
    family_passes = {family: sum(world["full_pass"] for world in worlds if world["family"] == family) for family in FAMILIES}
    gates = {
        "zero_of_64_null": family_passes["NULL"] == 0,
        "eight_of_eight_full": family_passes["DISTRIBUTED_FULL"] == 8,
        "eight_of_eight_reduced": family_passes["DISTRIBUTED_REDUCED"] == 8,
        "zero_all_adversaries": all(family_passes[family] == 0 for family in FAMILIES[3:]),
        "exact_world_registry": len(worlds) == 144 and len({world["world_id"] for world in worlds}) == 144,
        "exact_orbits": len(prepared[VIEWS[0]]["assignments"]) == 108 and len(prepared[VIEWS[1]]["assignments"]) == 324,
        "formal_target_unopened": True,
    }
    status = "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION" if all(gates.values()) else "STOP_SYNTHETIC_INSTRUMENT_FAILED"
    decision = "AUTHORIZE_SEPARATE_TARGET_FREEZE" if all(gates.values()) else "FORBID_FORMAL_TARGET_ACCESS"
    result = {"experiment": "LM002_SYNTHETIC_CALIBRATION", "schema": "LM002_CALIBRATION_V1", "status": status, "decision": decision, "world_count": len(worlds), "family_passes": family_passes, "gates": gates, "worlds": worlds, "inputs": {str(PANEL.relative_to(ROOT)): sha(PANEL), str(SPEC.relative_to(ROOT)): sha(SPEC)}, "access": {"formal_target_table_opened": False, "formal_target_rows_accessed": False, "real_state_scores_computed": False}, "claim_ceiling": "This target-free calibration assesses only whether the frozen exact statistic can distinguish artificial distributed binary states from null and confounded worlds. It supplies no manuscript association, leaf word, plant identity, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    REPORT.write_text(f"# LM002 synthetic calibration\n\nStatus: **{status}**.\n\nFamily full-pass counts: " + ", ".join(f"`{key}` {value}/{COUNTS[key]}" for key, value in family_passes.items()) + ".\n\nThe formal target table was not opened or parsed. " + ("A separate target freeze is authorized; no target has been run." if all(gates.values()) else "The instrument failed its frozen calibration and formal-target access remains forbidden.") + " No association, leaf word, plant identity, plaintext, meaning, or translation follows.\n", encoding="utf-8")


if __name__ == "__main__": main()
