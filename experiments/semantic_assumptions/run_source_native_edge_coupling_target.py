#!/usr/bin/env python3
"""Execute the single frozen source-native edge-coupling target test."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

from source_native_edge_coupling_core import ALPHABET, ALPHABET_INDEX, load_panel, passes, score


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "source_native_edge_coupling_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_edge_coupling_capacity_validation.json"
CORE = BASE / "source_native_edge_coupling_core.py"
TEST_SPEC = BASE / "SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md"
PREFLIGHT = RESULTS / "source_native_edge_coupling_preflight.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_edge_coupling_preflight_validation.json"
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_NATIVE_EDGE_COUPLING_TARGET_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_coupling_target.json"
REPORT = RESULTS / "source_native_edge_coupling_target_report.md"

FROZEN = {
    MASKED: "db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c",
    CAPACITY_VALIDATION: "889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5",
    CORE: "c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349",
    TEST_SPEC: "634eff5ddf6e3e823728d3aa40e4fd0465b5743ba003216c69692f21ef3f466c",
    PREFLIGHT: "901eea3a922c866d5c6705ac284cfc3c9406580853c0bb624216bf40e8587d61",
    PREFLIGHT_VALIDATION: "7ec2b481b320ead5fb847f3faf74877c25e59536279b525e071e7f9d3e9c3b2c",
    TARGET_SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    TARGET_SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "551f5cd464d1877dbdae10579db440a0f1ab8abe00aae27a230197f4a9677621",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("edge-coupling target artifact already exists")
    with tempfile.TemporaryDirectory(prefix="source_native_edge_coupling_target_", dir=RESULTS) as directory:
        result_stage = Path(directory) / "result.json"
        report_stage = Path(directory) / "report.md"
        result_stage.write_bytes(result_bytes)
        report_stage.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("edge-coupling target artifact appeared during execution")
        os.link(result_stage, OUT)
        try:
            os.link(report_stage, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def gate_values(summary: dict) -> dict[str, bool]:
    return {
        "exact_14955_rows": summary["eligible_rows"] == 14955,
        "exact_94_folios": summary["physical_folios"] == 94,
        "gain_at_least_0_02": summary["effect_equal_folio"] >= 0.02,
        "at_least_65_positive_folios": summary["positive_folios"] >= 65,
        "sign_p_at_most_0_01": summary["sign_p"] <= 0.01,
        "minimum_deletion_positive": summary["minimum_leave_one_folio_out"] > 0.0,
        "max_contribution_at_most_0_08": summary["max_abs_contribution_fraction"] <= 0.08,
        "currier_A_gain_at_least_0_01": summary["currier"]["A"]["effect_equal_folio"] >= 0.01,
        "currier_A_minimum_deletion_positive": summary["currier"]["A"]["minimum_leave_one_folio_out"] > 0.0,
        "currier_A_at_least_60_percent_positive": summary["currier"]["A"]["positive_folios"] / summary["currier"]["A"]["folios"] >= 0.60,
        "currier_B_gain_at_least_0_01": summary["currier"]["B"]["effect_equal_folio"] >= 0.01,
        "currier_B_minimum_deletion_positive": summary["currier"]["B"]["minimum_leave_one_folio_out"] > 0.0,
        "currier_B_at_least_60_percent_positive": summary["currier"]["B"]["positive_folios"] / summary["currier"]["B"]["folios"] >= 0.60,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing a second source-native edge-coupling target run")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen target input mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_TARGET_MASKED_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity validation is not PASS")
    preflight = json.loads(PREFLIGHT.read_text())
    if preflight["status"] != "PASS_TARGET_FREE_EDGE_COUPLING_PREFLIGHT" or preflight["decision"] != "GO_FREEZE_ONE_EDGE_COUPLING_TARGET" or not all(preflight["gates"].values()):
        raise SystemExit("synthetic preflight does not authorize target")
    preflight_validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if preflight_validation["status"] != "PASS_INDEPENDENT_88_WORLD_PREFLIGHT_RECONSTRUCTION" or not preflight_validation["target_outputs_absent"]:
        raise SystemExit("independent preflight validation does not authorize target")
    if json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("target source validation is not PASS")

    panel = load_panel(MASKED)
    with TARGET_SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    source_by_id = {row["consensus_group_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("duplicate target consensus-group ID")

    outcomes = np.empty(len(panel.rows), dtype=np.int64)
    outcome_counts: Counter[str] = Counter()
    for index, masked in enumerate(panel.rows):
        source = source_by_id.get(masked["consensus_group_id"])
        if source is None or masked["unit_id"] != source["consensus_group_id"]:
            raise ValueError("target join identity mismatch")
        if source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE":
            raise ValueError("target source scope mismatch")
        surface = source["family_surface"]
        if len(surface) < 3 or any(value not in ALPHABET_INDEX for value in surface):
            raise ValueError("invalid target family surface")
        folio_match = re.match(r"f\d+", source["page"])
        if folio_match is None:
            raise ValueError("invalid target physical folio")
        group_index = int(source["consensus_group_index"])
        group_count = int(source["consensus_group_count"])
        locus_position = "SINGLE" if group_count == 1 else ("FIRST" if group_index == 1 else ("LAST" if group_index == group_count else "MIDDLE"))
        length_bin = min(len(surface), 8)
        baseline_cell = "|".join(map(str, (surface[1], surface[-2], length_bin, locus_position, source["currier"])))
        full_cell = baseline_cell + "|" + surface[0]
        exact = {
            "locus": source["locus"], "page": source["page"],
            "physical_folio": folio_match.group(), "section": source["section"],
            "currier": source["currier"], "hand": source["hand"], "kind": source["kind"],
            "locus_position": locus_position, "symbol_count": str(len(surface)),
            "length_bin": str(length_bin), "opening_family": surface[0],
            "core_first_family": surface[1], "core_last_family": surface[-2],
            "baseline_cell": baseline_cell, "full_cell": full_cell,
            "masked_family_surface": surface[:-1] + "#",
        }
        if any(masked[key] != value for key, value in exact.items()):
            raise ValueError("target remasking or metadata mismatch")
        outcome = surface[-1]
        outcomes[index] = ALPHABET_INDEX[outcome]
        outcome_counts[outcome] += 1

    if len(panel.rows) != 19203 or int(panel.eligible.sum()) != 14955 or len(panel.folio_values) != 94:
        raise ValueError("target capacity drift")
    summary = score(panel, outcomes)
    gates = gate_values(summary)
    target_pass = passes(summary)
    if target_pass != all(gates.values()):
        raise ValueError("target gate implementation mismatch")
    if target_pass:
        status = "CONFIRM_TRANSFERABLE_OPENING_CONDITIONED_CLOSING_FAMILY_SELECTION"
        decision = "RETAIN_SOURCE_NATIVE_EDGE_COUPLING_RELATION"
    else:
        status = "NONCONFIRM_SOURCE_NATIVE_EDGE_COUPLING"
        decision = "CLOSE_EXACT_EDGE_COUPLING_TEST_WITHOUT_RETUNING"

    result = {
        "experiment": "SOURCE_NATIVE_EDGE_COUPLING_TARGET",
        "status": status,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "joined_rows": len(panel.rows),
        "eligible_rows": int(panel.eligible.sum()),
        "physical_folios": len(panel.folio_values),
        "outcome_counts": {family: outcome_counts[family] for family in ALPHABET},
        "summary": summary,
        "gates": {**gates, "TARGET_PASS": target_pass},
        "decision": decision,
        "target_rows_accessed": len(panel.rows),
        "target_scores_computed": 1,
        "event_level_outcomes_stored": 0,
        "complete_family_surfaces_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": (
            "A transferable opening-conditioned closing-family selection relation beyond the frozen "
            "second-family, penultimate-family, capped-length, locus-position, Currier, and held-folio "
            "controls. It is compatible with edge agreement, paired affixal selection, or templatic "
            "morphology but proves none of them and supplies no sound, word, meaning, plaintext, or translation."
        ),
    }
    report = f"""# Source-native opening/closing edge-coupling target

Status: **{status}**

The one authorized target join scored **{summary['eligible_rows']:,}** eligible
groups on **{summary['physical_folios']}** physical folios. The equal-folio
proper-score gain is **{summary['effect_equal_folio']:+.6f} nat/group**;
**{summary['positive_folios']}/{summary['physical_folios']}** folios are positive
with exact sign p **{summary['sign_p']:.8g}**. The minimum leave-one-folio-out
gain is **{summary['minimum_leave_one_folio_out']:+.6f}** and the maximum absolute
folio contribution is **{summary['max_abs_contribution_fraction']:.4f}**.

Currier A/B equal-folio gains are
**{summary['currier']['A']['effect_equal_folio']:+.6f}** and
**{summary['currier']['B']['effect_equal_folio']:+.6f}**. `TARGET_PASS` is
**{str(target_pass).lower()}**; the decision is **{decision}**.

No event-level outcomes or complete family surfaces are stored. This test can
establish only source-native structural edge selection. It does not identify an
affix, circumfix, operator, sound, word, language, cipher operation, meaning,
plaintext, or translation.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "gates": result["gates"], "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
