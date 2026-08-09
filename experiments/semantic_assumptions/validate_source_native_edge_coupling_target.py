#!/usr/bin/env python3
"""Production-free reconstruction of the edge-coupling target result."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "source_native_edge_coupling_masked.tsv"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PRODUCTION = RESULTS / "source_native_edge_coupling_target.json"
PRODUCTION_REPORT = RESULTS / "source_native_edge_coupling_target_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_coupling_target_validation.json"
REPORT = RESULTS / "source_native_edge_coupling_target_validation_report.md"
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}
FIELDS = (
    "unit_id", "consensus_group_id", "locus", "page", "physical_folio",
    "section", "currier", "hand", "kind", "locus_position", "symbol_count",
    "length_bin", "opening_family", "core_first_family", "core_last_family",
    "baseline_cell", "full_cell", "masked_family_surface",
    "outside_folio_baseline_support", "outside_folio_full_support", "target_eligible",
)
FROZEN = {
    MASKED: "db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c",
    RESULTS / "source_native_edge_coupling_capacity_validation.json": "889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5",
    BASE / "source_native_edge_coupling_core.py": "c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349",
    BASE / "SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md": "634eff5ddf6e3e823728d3aa40e4fd0465b5743ba003216c69692f21ef3f466c",
    RESULTS / "source_native_edge_coupling_preflight.json": "901eea3a922c866d5c6705ac284cfc3c9406580853c0bb624216bf40e8587d61",
    RESULTS / "source_native_edge_coupling_preflight_validation.json": "7ec2b481b320ead5fb847f3faf74877c25e59536279b525e071e7f9d3e9c3b2c",
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    RESULTS / "source_sta_family_consensus_validation.json": "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    BASE / "SOURCE_NATIVE_EDGE_COUPLING_TARGET_SPEC.md": "551f5cd464d1877dbdae10579db440a0f1ab8abe00aae27a230197f4a9677621",
    BASE / "run_source_native_edge_coupling_target.py": "f230c48bff12b9e7bdf0d92aa57042bcbefc6d44be439721cee15a6794a9a2c3",
    PRODUCTION: "3d7b21401e963fa6a3a4304b4543eaa09d202ad04682e9db2034b9615bdbd27e",
    PRODUCTION_REPORT: "c1f1cc935c198a2b849ac62eb44f060ae8fe9908f35712109b12714df1007e9e",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, checks: list[int]) -> None:
    checks[0] += 1
    if not condition:
        raise AssertionError(message)


def sign_p(positive: int, total: int) -> float:
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2 ** total)


def compare(actual, expected, path: str, checks: list[int]) -> None:
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), f"keys {path}", checks)
        for key in expected:
            compare(actual[key], expected[key], f"{path}.{key}", checks)
    elif isinstance(expected, float):
        require(isinstance(actual, (int, float)) and math.isclose(float(actual), expected, rel_tol=0, abs_tol=1e-14), f"float {path}", checks)
    else:
        require(actual == expected, f"value {path}", checks)


def compute(rows: list[dict], outcomes: np.ndarray) -> dict:
    base_keys = tuple(sorted({row["baseline_cell"] for row in rows}))
    full_keys = tuple(sorted({row["full_cell"] for row in rows}))
    base_map = {key: index for index, key in enumerate(base_keys)}
    full_map = {key: index for index, key in enumerate(full_keys)}
    base_index = np.asarray([base_map[row["baseline_cell"]] for row in rows], dtype=np.int64)
    full_index = np.asarray([full_map[row["full_cell"]] for row in rows], dtype=np.int64)
    eligible_mask = np.asarray([row["target_eligible"] == "1" for row in rows], dtype=bool)
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    base_counts = np.zeros((len(base_keys), len(ALPHABET)), dtype=np.int64)
    full_counts = np.zeros((len(full_keys), len(ALPHABET)), dtype=np.int64)
    np.add.at(base_counts, (base_index, outcomes), 1)
    np.add.at(full_counts, (full_index, outcomes), 1)
    gains = np.full(len(rows), np.nan, dtype=np.float64)
    folio_effects = []
    currier_folios: dict[str, list[float]] = defaultdict(list)
    for folio in folios:
        indices = np.asarray([i for i, row in enumerate(rows) if row["physical_folio"] == folio], dtype=np.int64)
        held_base = np.zeros_like(base_counts)
        held_full = np.zeros_like(full_counts)
        np.add.at(held_base, (base_index[indices], outcomes[indices]), 1)
        np.add.at(held_full, (full_index[indices], outcomes[indices]), 1)
        train_base = base_counts - held_base
        train_full = full_counts - held_full
        eligible = indices[eligible_mask[indices]]
        local = []
        by_currier: dict[str, list[float]] = defaultdict(list)
        for index in eligible:
            outcome = outcomes[index]
            b = base_index[index]
            f = full_index[index]
            base_total = int(train_base[b].sum())
            full_total = int(train_full[f].sum())
            if base_total < 20 or full_total < 5:
                raise AssertionError("support drift")
            p_base = (train_base[b, outcome] + .5) / (base_total + .5 * len(ALPHABET))
            p_full = (train_full[f, outcome] + .5) / (full_total + .5 * len(ALPHABET))
            value = math.log(p_full / p_base)
            gains[index] = value
            local.append(value)
            by_currier[rows[index]["currier"]].append(value)
        folio_effects.append(float(np.mean(local)))
        for key, values in by_currier.items():
            currier_folios[key].append(float(np.mean(values)))
    effects = np.asarray(folio_effects)
    deletion = (effects.sum() - effects) / (len(effects) - 1)
    currier = {}
    for key in ("A", "B"):
        values = np.asarray(currier_folios[key])
        currier[key] = {
            "effect_equal_folio": float(values.mean()),
            "positive_folios": int((values > 0).sum()),
            "folios": len(values),
            "sign_p": sign_p(int((values > 0).sum()), len(values)),
            "minimum_leave_one_folio_out": float(((values.sum() - values) / (len(values) - 1)).min()),
        }
    return {
        "eligible_rows": int(np.isfinite(gains).sum()),
        "physical_folios": len(effects),
        "effect_equal_folio": float(effects.mean()),
        "effect_equal_row": float(np.nanmean(gains)),
        "positive_folios": int((effects > 0).sum()),
        "sign_p": sign_p(int((effects > 0).sum()), len(effects)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(effects).max() / np.abs(effects).sum()),
        "currier": currier,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite edge-coupling target validation")
    checks = [0]
    for path, expected in FROZEN.items():
        require(sha(path) == expected, f"hash {path.name}", checks)
    production = json.loads(PRODUCTION.read_text())
    with MASKED.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        require(tuple(reader.fieldnames or ()) == FIELDS, "masked schema", checks)
        rows = list(reader)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    source = {row["consensus_group_id"]: row for row in source_rows}
    require(len(rows) == 19203 and len({row["unit_id"] for row in rows}) == 19203, "masked rows", checks)
    require(len(source) == len(source_rows), "source IDs", checks)
    outcomes = np.empty(len(rows), dtype=np.int64)
    counts: Counter[str] = Counter()
    for index, masked in enumerate(rows):
        item = source.get(masked["consensus_group_id"])
        require(item is not None and masked["unit_id"] == item["consensus_group_id"], f"join {index}", checks)
        surface = item["family_surface"]
        match = re.match(r"f\d+", item["page"])
        require(item["strict_zero_alternative"] == "1" and item["grammar_scope"] == "CONFIRMED_PROSE", f"scope {index}", checks)
        require(len(surface) >= 3 and match is not None and all(value in INDEX for value in surface), f"surface {index}", checks)
        group_index, group_count = int(item["consensus_group_index"]), int(item["consensus_group_count"])
        position = "SINGLE" if group_count == 1 else ("FIRST" if group_index == 1 else ("LAST" if group_index == group_count else "MIDDLE"))
        length_bin = min(len(surface), 8)
        baseline = "|".join(map(str, (surface[1], surface[-2], length_bin, position, item["currier"])))
        expected = {
            "locus": item["locus"], "page": item["page"], "physical_folio": match.group(),
            "section": item["section"], "currier": item["currier"], "hand": item["hand"],
            "kind": item["kind"], "locus_position": position, "symbol_count": str(len(surface)),
            "length_bin": str(length_bin), "opening_family": surface[0],
            "core_first_family": surface[1], "core_last_family": surface[-2],
            "baseline_cell": baseline, "full_cell": baseline + "|" + surface[0],
            "masked_family_surface": surface[:-1] + "#",
        }
        require(all(masked[key] == value for key, value in expected.items()), f"remask {index}", checks)
        outcomes[index] = INDEX[surface[-1]]
        counts[surface[-1]] += 1
    summary = compute(rows, outcomes)
    compare(production["summary"], summary, "summary", checks)
    require(production["outcome_counts"] == {value: counts[value] for value in ALPHABET}, "outcome counts", checks)
    require(production["joined_rows"] == 19203 and production["eligible_rows"] == 14955 and production["physical_folios"] == 94, "capacities", checks)
    expected_inputs = {path.name: sha(path) for path in FROZEN if path not in {PRODUCTION, PRODUCTION_REPORT}}
    require(production["inputs"] == expected_inputs, "input bindings", checks)
    expected_gates = {
        "exact_14955_rows": summary["eligible_rows"] == 14955,
        "exact_94_folios": summary["physical_folios"] == 94,
        "gain_at_least_0_02": summary["effect_equal_folio"] >= .02,
        "at_least_65_positive_folios": summary["positive_folios"] >= 65,
        "sign_p_at_most_0_01": summary["sign_p"] <= .01,
        "minimum_deletion_positive": summary["minimum_leave_one_folio_out"] > 0,
        "max_contribution_at_most_0_08": summary["max_abs_contribution_fraction"] <= .08,
        "currier_A_gain_at_least_0_01": summary["currier"]["A"]["effect_equal_folio"] >= .01,
        "currier_A_minimum_deletion_positive": summary["currier"]["A"]["minimum_leave_one_folio_out"] > 0,
        "currier_A_at_least_60_percent_positive": summary["currier"]["A"]["positive_folios"] / summary["currier"]["A"]["folios"] >= .60,
        "currier_B_gain_at_least_0_01": summary["currier"]["B"]["effect_equal_folio"] >= .01,
        "currier_B_minimum_deletion_positive": summary["currier"]["B"]["minimum_leave_one_folio_out"] > 0,
        "currier_B_at_least_60_percent_positive": summary["currier"]["B"]["positive_folios"] / summary["currier"]["B"]["folios"] >= .60,
    }
    expected_gates["TARGET_PASS"] = all(expected_gates.values())
    require(production["gates"] == expected_gates, "gates", checks)
    require(production["status"] == "NONCONFIRM_SOURCE_NATIVE_EDGE_COUPLING" and production["decision"] == "CLOSE_EXACT_EDGE_COUPLING_TEST_WITHOUT_RETUNING", "decision", checks)
    require(production["target_rows_accessed"] == 19203 and production["target_scores_computed"] == 1, "access counters", checks)
    require(production["event_level_outcomes_stored"] == production["complete_family_surfaces_stored"] == production["english_glosses"] == 0, "claim counters", checks)
    require("translation" in production["claim_ceiling"] and "compatible" in production["claim_ceiling"], "claim ceiling", checks)
    require(sum(counts.values()) == 19203, "outcome total", checks)
    require(not expected_gates["TARGET_PASS"], "nonconfirmation", checks)

    validation = {
        "experiment": "SOURCE_NATIVE_EDGE_COUPLING_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_TARGET_NONCONFIRM_RECONSTRUCTION",
        "checks": checks[0], "failures": [],
        "production_sha256": sha(PRODUCTION), "production_report_sha256": sha(PRODUCTION_REPORT),
        "validator_sha256": sha(VALIDATOR), "joined_rows": len(rows),
        "eligible_rows": summary["eligible_rows"], "physical_folios": summary["physical_folios"],
        "effect_equal_folio": summary["effect_equal_folio"], "positive_folios": summary["positive_folios"],
        "target_pass": False, "decision": production["decision"],
        "event_level_outcomes_stored": 0, "english_glosses": 0,
        "claim_ceiling": "Independent reconstruction of the frozen structural nonconfirmation only; no affix, word, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native edge-coupling target validation

Status: **{validation['status']}**

A production-free implementation reconstructed all **{len(rows):,}** joins,
**{summary['eligible_rows']:,}** held-row scores, 94 folio summaries, both
Currier summaries, every gate, and the frozen nonconfirmation in
**{checks[0]:,} checks**.

The equal-folio gain is **{summary['effect_equal_folio']:+.6f}** with only
**{summary['positive_folios']}/94** positive folios. The exact test is closed
without retuning. Validation supplies no affix, word, meaning, plaintext, or
translation.
""")
    print(json.dumps({"status": validation["status"], "checks": checks[0], "effect": summary["effect_equal_folio"]}, sort_keys=True))


if __name__ == "__main__":
    main()
