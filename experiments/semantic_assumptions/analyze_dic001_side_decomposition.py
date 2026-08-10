#!/usr/bin/env python3
"""Decompose confirmed DIC001 reset likeness into left/right/cross blocks."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

import run_dic001_drawing_interruption_target as base


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
SPEC = HERE / "DIC001_SIDE_DECOMPOSITION_SPEC.md"; SCRIPT = Path(__file__).resolve()
TARGET = RES / "dic001_drawing_interruption_target.json"
OUT = RES / "dic001_side_decomposition.json"; REPORT = RES / "dic001_side_decomposition_report.md"
NAMES = ("LEFT_TERMINAL", "RIGHT_INITIAL", "CROSS_PAIR")


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def component_fields(left, right):
    a, b = left["family_surface"], right["family_surface"]
    a2 = a[-2:] if len(a) > 1 else "#" + a; b2 = b[:2] if len(b) > 1 else b + "#"
    return ((a[-1], a2), (b[0], b2), (a[-1] + "|" + b[0], a2 + "|" + b2))


def component_model(events):
    counts = [[[Counter() for _ in range(2)] for _ in range(3)] for _ in range(2)]
    totals = [[[0] * 2 for _ in range(3)] for _ in range(2)]
    levels = [[set() for _ in range(2)] for _ in range(3)]
    for event in events:
        for block, values in enumerate(component_fields(event[3], event[4])):
            for slot, value in enumerate(values):
                counts[event[2]][block][slot][value] += 1; totals[event[2]][block][slot] += 1; levels[block][slot].add(value)
    def score(left, right):
        answer = np.zeros(3)
        for block, values in enumerate(component_fields(left, right)):
            for slot, value in enumerate(values):
                k = len(levels[block][slot]) + 1
                answer[block] += math.log((counts[1][block][slot][value] + 1) / (totals[1][block][slot] + k))
                answer[block] -= math.log((counts[0][block][slot][value] + 1) / (totals[0][block][slot] + k))
        return answer
    return score


def main():
    target = json.loads(TARGET.read_text())
    if target["status"] != "CONFIRMED_DISTRIBUTED_RESET_LIKENESS": raise SystemExit("confirmed target absent")
    with base.SOURCE.open(newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    with base.PANEL.open(newline="") as handle: panel = list(csv.DictReader(handle, delimiter="\t"))
    target_pages = {row["page"] for row in panel if row["boundary_class"] == "DRAWING_INTERRUPTION"}
    lookup = {(row["locus"], int(row["group_index"])): row for row in source}
    joined = [(lookup[(row["locus"], int(row["left_group_index"]))], lookup[(row["locus"], int(row["right_group_index"]))]) for row in panel]
    reference = base.reference_events(source, target_pages); folios = sorted({row["physical_folio"] for row in panel})
    raw = np.empty((len(panel), 3)); frozen_order_raw = np.empty(len(panel))
    for held in folios:
        train = [event for event in reference if event[1] != held]; model = component_model(train); full_model = base.fit(train)
        space = np.vstack([model(event[3], event[4]) for event in train if event[2] == 0])
        full_space = np.array([full_model(event[3], event[4]) for event in train if event[2] == 0])
        means = space.mean(axis=0); full_mean = full_space.mean(); full_sd = full_space.std(ddof=0)
        indices = [i for i, row in enumerate(panel) if row["physical_folio"] == held]
        raw[indices] = np.vstack([(model(*joined[i]) - means) / full_sd for i in indices])
        frozen_order_raw[indices] = [(full_model(*joined[i]) - full_mean) / full_sd for i in indices]
    unreconciled_raw = raw.sum(axis=1); raw_additivity = float(np.max(np.abs(unreconciled_raw - frozen_order_raw)))
    if hashlib.sha256(np.asarray(frozen_order_raw, dtype="<f8").tobytes()).hexdigest() != target["transform"]["raw_score_sha256"]:
        raise SystemExit("separate full score does not reproduce frozen raw score")
    if raw_additivity > 1e-12: raise SystemExit(f"component raw additivity exceeds tolerance: {raw_additivity:.17g}")
    raw[:, 2] += frozen_order_raw - raw.sum(axis=1)
    design, _ = base.nuisance_matrix(panel, joined)
    residual = raw - design @ np.linalg.lstsq(design, raw, rcond=None)[0]
    full_residual = frozen_order_raw - design @ np.linalg.lstsq(design, frozen_order_raw, rcond=None)[0]
    if hashlib.sha256(np.asarray(full_residual, dtype="<f8").tobytes()).hexdigest() != target["transform"]["residual_score_sha256"]:
        raise SystemExit("full residual does not reproduce frozen target")
    residual_additivity = float(np.max(np.abs(residual.sum(axis=1) - full_residual)))
    if residual_additivity > 1e-12: raise SystemExit("component residual additivity exceeds tolerance")
    residual[:, 2] += full_residual - residual.sum(axis=1)
    weight, meta, folios = base.topology(panel)
    vectors = np.column_stack((raw, residual)); null = base.permutation_null(panel, meta, vectors)
    blocks = {}
    for j, name in enumerate(NAMES):
        raw_summary = base.diagnostics(raw[:, j], panel, weight, meta, folios)
        residual_summary = base.diagnostics(residual[:, j], panel, weight, meta, folios)
        blocks[name] = {
            "raw": raw_summary, "residual": residual_summary,
            "p_raw": (1 + int(np.sum(null[:, j] >= raw_summary["effect"]))) / 65537,
            "p_residual": (1 + int(np.sum(null[:, 3 + j] >= residual_summary["effect"]))) / 65537,
        }
    result = {
        "experiment": "DIC001_SIDE_DECOMPOSITION", "status": "PASS_POST_CONFIRMATION_DESCRIPTIVE_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (base.SOURCE, base.PANEL, TARGET, SPEC, SCRIPT)},
        "counts": {"panel_rows": len(panel), "targets": 428, "controls": 4143, "folios": len(folios), "permutation_worlds": 65536},
        "blocks": blocks,
        "additivity": {"raw_max_abs": raw_additivity,
                       "residual_max_abs": residual_additivity,
                       "post_reconciliation_raw_max_abs": float(np.max(np.abs(raw.sum(axis=1) - frozen_order_raw))),
                       "post_reconciliation_residual_max_abs": float(np.max(np.abs(residual.sum(axis=1) - full_residual))),
                       "frozen_raw_sha256": target["transform"]["raw_score_sha256"], "frozen_residual_sha256": target["transform"]["residual_score_sha256"]},
        "new_confirmation_claim": False, "decision": "DESCRIBE_SIDE_LOCALIZATION_ONLY",
        "claim_ceiling": "Post-confirmation localization of the confirmed DIC001 structural score only; no picture ownership, word, POS, meaning, plaintext, language, cipher, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# DIC001 side decomposition\n\nStatus: **PASS_POST_CONFIRMATION_DESCRIPTIVE_DECOMPOSITION**.\n\n"
        + "\n".join(f"- {name}: raw **{blocks[name]['raw']['effect']:.6f}** (p **{blocks[name]['p_raw']:.6f}**); residual **{blocks[name]['residual']['effect']:.6f}** (p **{blocks[name]['p_residual']:.6f}**)." for name in NAMES)
        + "\n\nThis is a post-confirmation localization of the already-confirmed structural score, not a new independent result or a semantic reading.\n")
    print(json.dumps({name: {"raw": blocks[name]["raw"]["effect"], "residual": blocks[name]["residual"]["effect"], "p_residual": blocks[name]["p_residual"]} for name in NAMES}, indent=2))


if __name__ == "__main__": main()
