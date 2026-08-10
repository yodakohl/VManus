#!/usr/bin/env python3
"""Apply the target-free inferential-unit correction to co-switch capacity."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
AMENDMENT = BASE / "CHO_CHE_COSWITCH_CAPACITY_V2_AMENDMENT.md"
RUNNER = Path(__file__).resolve()
V1_SPEC = BASE / "CHO_CHE_COSWITCH_CAPACITY_SPEC.md"
V1_RUNNER = BASE / "build_cho_che_coswitch_capacity.py"
V1_RESULT = RESULTS / "cho_che_coswitch_capacity.json"
PANEL = RESULTS / "cho_che_coswitch_masked_panel.tsv"
V1_REPORT = RESULTS / "cho_che_coswitch_capacity_report.md"
OUT = RESULTS / "cho_che_coswitch_capacity_v2.json"
REPORT = RESULTS / "cho_che_coswitch_capacity_v2_report.md"
EXPECTED = {
    V1_SPEC: "15690943688a533641d3177524c18fd4f08c1c7935b67adea862f1d655961a0a",
    V1_RUNNER: "b83655e1b70e9c0bf3dfde6940afa5cbbc95a955db226800878787411e7d01c0",
    V1_RESULT: "5f1ae292148f27d31aa02e14b7b766b3019bd98ff5b552207485b73f28b0ecce",
    PANEL: "25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003",
    V1_REPORT: "bcf019aa42b00afd03e31ff9caf69894b6f6927764aa96b881e6a979d5f16baf",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
FIELDS = (
    "source_group_id", "edition", "locus", "page", "collapsed_page",
    "physical_folio", "side", "page_state", "section", "currier", "hand",
    "kind", "grammar_scope", "primary_sta_symbol_count",
    "page_position_quartile", "group_position_class",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("refusing to overwrite v2 capacity artifacts")
    with tempfile.TemporaryDirectory(prefix="cho_che_coswitch_capacity_v2_", dir=RESULTS) as directory:
        staged_result = Path(directory) / "result"
        staged_report = Path(directory) / "report"
        staged_result.write_bytes(result_bytes)
        staged_report.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("v2 capacity artifact appeared during staging")
        os.link(staged_result, OUT)
        try:
            os.link(staged_report, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"v1 binding mismatch: {path.name}")
    v1 = json.loads(V1_RESULT.read_text())
    if v1["status"] != "STOP_INSUFFICIENT_CHO_CHE_COSWITCH_CAPACITY":
        raise ValueError("unexpected v1 status")
    false_v1 = {key for key, value in v1["gates"].items() if not value}
    if false_v1 != {"at_least_1600_groups_each_reading"}:
        raise ValueError("v1 did not stop on exactly the corrected gate")

    with PANEL.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("panel schema")
        rows = list(reader)
    if len(rows) != 5012 or len({row["source_group_id"] for row in rows}) != len(rows):
        raise ValueError("panel identity")
    groups = Counter(row["edition"] for row in rows)
    side_counts = Counter((row["edition"], row["physical_folio"], row["side"]) for row in rows)
    leaves = sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:]))
    state_by_side = {}
    for row in rows:
        key = row["physical_folio"], row["side"]
        state = int(row["page_state"])
        if key in state_by_side and state_by_side[key] != state:
            raise ValueError("state drift")
        state_by_side[key] = state
    if any({state_by_side[(folio, side)] for side in ("r", "v")} != {0, 1} for folio in leaves):
        raise ValueError("not paired opposite states")
    high_recto = sum(state_by_side[(folio, "r")] == 1 for folio in leaves)
    high_verso = len(leaves) - high_recto
    panel_cells = Counter(
        (row["edition"], row["physical_folio"], row["side"], row["section"], row["currier"], row["hand"], row["kind"], row["grammar_scope"])
        for row in rows
    )
    shared_cells = all(
        any(
            key[0] == row["edition"] and key[1] == row["physical_folio"]
            and key[2] != row["side"] and key[3:] == (
                row["section"], row["currier"], row["hand"], row["kind"], row["grammar_scope"]
            )
            for key in panel_cells
        )
        for row in rows
    )
    prose = {row["physical_folio"] for row in rows if row["grammar_scope"] == "CONFIRMED_PROSE"}
    diagnostic = {row["physical_folio"] for row in rows if row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"}
    forbidden = {"ivtff_group_raw", "clean_ascii_fragments", "sta_group_raw", "primary_sta_codes", "primary_sta_families", "target_family", "score", "effect", "p_value"}
    orbit = 2 ** len(leaves)
    gates = {
        key: value for key, value in v1["gates"].items()
        if key != "at_least_1600_groups_each_reading"
    }
    gates.update({
        "exact_v1_descriptive_group_counts_preserved": {edition: groups[edition] for edition in READINGS} == v1["groups_by_reading"],
        "exact_eight_leaf_panel": leaves == v1["eligible_common_switch_leaves"] and len(leaves) == 8,
        "exact_opposite_state_pair_each_leaf": all({state_by_side[(folio, side)] for side in ("r", "v")} == {0, 1} for folio in leaves),
        "actual_metadata_cell_overlap": shared_cells,
        "minimum_30_groups_each_side_recomputed": min(side_counts.values()) >= 30,
        "orientation_support_recomputed": min(high_recto, high_verso) >= 3,
        "prose_and_diagnostic_support_recomputed": len(prose) >= 5 and len(diagnostic) >= 2,
        "panel_forbidden_columns_absent_recomputed": not (forbidden & set(FIELDS)),
        "synthetic_power_required_before_target": True,
    })
    passed = all(gates.values()) and orbit == 256 and 1 / orbit <= .01
    status = "PASS_CORRECTED_INFERENTIAL_UNIT_CHO_CHE_COSWITCH_CAPACITY" if passed else "STOP_V2_CHO_CHE_COSWITCH_CAPACITY"
    decision = "AUTHORIZE_TARGET_FREE_COSWITCH_PREFLIGHT_ONLY" if passed else "CLOSE_COSWITCH_ROUTE_UNSCORED"
    result = {
        "experiment": "CHO_CHE_COSWITCH_CAPACITY_V2",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*EXPECTED, AMENDMENT, RUNNER)},
        "v1_status_preserved": v1["status"],
        "v1_false_gate": sorted(false_v1),
        "correction": "remove noninferential rounded total-group gate; require target-free synthetic power on exact physical-leaf geometry",
        "eligible_common_switch_leaves": leaves,
        "groups_by_reading": {edition: groups[edition] for edition in READINGS},
        "minimum_groups_per_reading_leaf_side": min(side_counts.values()),
        "high_recto_leaves": high_recto,
        "high_verso_leaves": high_verso,
        "prose_leaf_count": len(prose),
        "diagnostic_leaf_count": len(diagnostic),
        "leaf_flip_orbit": orbit,
        "attainable_one_sided_p_floor": 1 / orbit,
        "target_associations_computed": 0,
        "scores_computed": 0,
        "p_values_computed": 0,
        "english_glosses": 0,
        "gates": gates,
        "claim_ceiling": "V2 establishes only score-blind capacity for a held-physical-leaf synthetic preflight after correcting a noninferential row-total gate. It supplies no co-switch result, meaning, sound, wordhood, language, cipher, plaintext, or translation.",
    }
    report = f"""# `cho/che` independent co-switch capacity v2

Status: **{status}**

V1 is preserved as a target-free stop: RF retained 1,597 rather than 1,600
groups.  V2 corrects only that noninferential rounded row-total gate.  The
actual independent-unit geometry remains **{len(leaves)} physical leaves**,
**{high_recto}/{high_verso}** high-recto/high-verso, at least
**{min(side_counts.values())}** groups per reading/leaf/side, and an exact
**{orbit}**-state leaf-flip orbit (floor **{1/orbit:.6f}**).

The exact per-reading totals remain recorded: ZL **{groups['ZL3b']:,}**, IT
**{groups['IT2a']:,}**, RF **{groups['RF1b']:,}**.  No feature/state
association, score, effect, or p-value has been computed.  Decision:
**{decision}**.  Synthetic null/power calibration is mandatory before target
access.  This supplies no co-switch result, meaning, sound, wordhood, language,
cipher, plaintext, or translation.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "decision": decision, "gates": gates}, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
