#!/usr/bin/env python3
"""Execute the frozen DIC001 drawing-interruption target exactly once."""

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
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = HERE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
PANEL = RESULTS / "dic001_drawing_interruption_capacity.tsv"
FREEZE = HERE / "DIC001_DRAWING_INTERRUPTION_TARGET_FREEZE.json"
OUTPUT = RESULTS / "dic001_drawing_interruption_target.json"
REPORT = RESULTS / "dic001_drawing_interruption_target_report.md"
VALIDATION_OUTPUT = RESULTS / "dic001_drawing_interruption_target_validation.json"
VALIDATION_REPORT = RESULTS / "dic001_drawing_interruption_target_validation_report.md"
SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
WORLDS = 65536


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page):
    match = re.match(r"f\d+", page)
    if not match: raise AssertionError(page)
    return match.group(0)


def line_number(locus):
    return int(locus.rsplit(".", 1)[1])


def verify_freeze():
    freeze = json.loads(FREEZE.read_text())
    if freeze.get("status") != "SEALED_SINGLE_TARGET_AUTHORIZED": raise SystemExit("invalid DIC001 freeze status")
    required_outputs = {str(path.relative_to(REPO)) for path in (OUTPUT, REPORT, VALIDATION_OUTPUT, VALIDATION_REPORT)}
    if set(freeze.get("target_outputs", {})) != required_outputs: raise SystemExit("invalid frozen output set")
    if set(freeze.get("frozen_files", {})) != set(freeze.get("frozen_file_allowlist", [])): raise SystemExit("invalid frozen file allowlist")
    for relative, expected in freeze["frozen_files"].items():
        path = REPO / relative
        if not path.is_file() or sha(path) != expected: raise SystemExit("frozen file drift: " + relative)
    for relative, absent in freeze["target_outputs"].items():
        if absent is not True or (REPO / relative).exists(): raise SystemExit("target output not absent: " + relative)
    return freeze


def fields(left, right):
    a, b = left["family_surface"], right["family_surface"]
    a2 = a[-2:] if len(a) > 1 else "#" + a
    b2 = b[:2] if len(b) > 1 else b + "#"
    return (a[-1], b[0], a[-1] + "|" + b[0], a2, b2, a2 + "|" + b2)


def fit(events):
    counts = [[Counter() for _ in range(6)] for _ in range(2)]
    totals = [[0] * 6 for _ in range(2)]
    vocabulary = [set() for _ in range(6)]
    for event in events:
        for j, value in enumerate(fields(event[3], event[4])):
            counts[event[2]][j][value] += 1; totals[event[2]][j] += 1; vocabulary[j].add(value)
    def score(left, right):
        answer = 0.0
        for j, value in enumerate(fields(left, right)):
            k = len(vocabulary[j]) + 1
            answer += math.log((counts[1][j][value] + 1) / (totals[1][j] + k))
            answer -= math.log((counts[0][j][value] + 1) / (totals[0][j] + k))
        return answer
    return score


def reference_events(source_rows, target_pages):
    lines = defaultdict(list)
    for row in source_rows:
        if row["page"] not in target_pages and row["grammar_scope"] == "CONFIRMED_PROSE":
            lines[row["locus"]].append(row)
    for groups in lines.values(): groups.sort(key=lambda row: int(row["group_index"]))
    events = []
    for groups in lines.values():
        for left, right in zip(groups, groups[1:]):
            if left["right_boundary_profile"] == SPACE:
                events.append((left["page"], folio(left["page"]), 0, left, right))
    pages = defaultdict(list)
    for groups in lines.values(): pages[groups[0]["page"]].append(groups)
    for page, page_lines in pages.items():
        page_lines.sort(key=lambda groups: line_number(groups[0]["locus"]))
        for first, second in zip(page_lines, page_lines[1:]):
            if line_number(second[0]["locus"]) == line_number(first[0]["locus"]) + 1 and second[0]["code"].startswith("+P"):
                events.append((page, folio(page), 1, first[-1], second[0]))
    return events


def nuisance_matrix(panel_rows, joined):
    n = len(panel_rows); columns = [np.ones(n)]
    pages = sorted({row["page"] for row in panel_rows})
    for page in pages[1:]: columns.append(np.array([row["page"] == page for row in panel_rows], dtype=float))
    position = np.array([float(row["normalized_boundary_position"]) for row in panel_rows])
    columns += [position, position ** 2, position ** 3]
    bins = np.minimum((position * 10).astype(np.int64), 9)
    columns += [(bins == value).astype(float) for value in range(1, 10)]
    counts = np.minimum(np.array([int(row["group_count"]) for row in panel_rows]), 20)
    columns += [(counts == value).astype(float) for value in sorted(set(counts))[1:]]
    left = np.array([min(len(pair[0]["family_surface"]), 8) for pair in joined])
    right = np.array([min(len(pair[1]["family_surface"]), 8) for pair in joined])
    cells = sorted(set(zip(left.tolist(), right.tolist())))
    columns += [((left == a) & (right == b)).astype(float) for a, b in cells[1:]]
    return np.column_stack(columns), cells


def topology(panel_rows):
    by_page = defaultdict(list)
    for i, row in enumerate(panel_rows): by_page[row["page"]].append(i)
    folios = sorted({row["physical_folio"] for row in panel_rows})
    pages_per_folio = Counter(panel_rows[idx[0]]["physical_folio"] for idx in by_page.values())
    weight = np.zeros(len(panel_rows)); meta = []
    for page, index_list in by_page.items():
        indices = np.array(index_list)
        targets = np.array([i for i in indices if panel_rows[i]["boundary_class"] == "DRAWING_INTERRUPTION"])
        controls = np.array([i for i in indices if panel_rows[i]["boundary_class"] == "DEFINITE_SPACE"])
        first = panel_rows[indices[0]]; scale = 1 / (len(folios) * pages_per_folio[first["physical_folio"]])
        weight[targets] = scale / len(targets); weight[controls] = -scale / len(controls)
        meta.append({"page": page, "indices": indices, "k": len(targets), "scale": scale,
                     "folio": first["physical_folio"], "currier": first["currier"], "section": first["section"]})
    return weight, meta, folios


def diagnostics(vector, panel_rows, weight, meta, folios):
    page = {}
    for item in meta:
        idx = item["indices"]
        selected = np.array([panel_rows[i]["boundary_class"] == "DRAWING_INTERRUPTION" for i in idx])
        page[item["page"]] = float(vector[idx][selected].mean() - vector[idx][~selected].mean())
    folio_effects = {f: float(np.mean([page[x["page"]] for x in meta if x["folio"] == f])) for f in folios}
    def subset(predicate):
        grouped = defaultdict(list)
        for item in meta:
            if predicate(item): grouped[item["folio"]].append(page[item["page"]])
        return float(np.mean([np.mean(values) for values in grouped.values()]))
    total_absolute = sum(abs(value) for value in folio_effects.values())
    return {
        "effect": float(weight @ vector), "positive_folios": sum(value > 0 for value in folio_effects.values()),
        "currier_A": subset(lambda x: x["currier"] == "A"), "currier_B": subset(lambda x: x["currier"] == "B"),
        "section_H": subset(lambda x: x["section"] == "H"), "section_non_H": subset(lambda x: x["section"] != "H"),
        "minimum_deletion_effect": min(float(np.mean([v for f, v in folio_effects.items() if f != deleted])) for deleted in folios),
        "maximum_absolute_folio_concentration": max(abs(value) for value in folio_effects.values()) / total_absolute,
        "folio_effects": folio_effects,
    }


def permutation_null(panel_rows, meta, vectors):
    def page_null(item):
        seed = int.from_bytes(hashlib.sha256(f"76001004|{item['page']}".encode()).digest()[:8], "little")
        rng = np.random.default_rng(seed)
        priorities = rng.random((WORLDS, len(item["indices"])))
        chosen = np.argpartition(priorities, item["k"] - 1, axis=1)[:, :item["k"]]
        selected_sum = np.take(vectors[item["indices"]], chosen, axis=0).sum(axis=1)
        total = vectors[item["indices"]].sum(axis=0)
        contrast = selected_sum / item["k"] - (total - selected_sum) / (len(item["indices"]) - item["k"])
        return contrast * item["scale"]
    null = np.zeros((WORLDS, vectors.shape[1]))
    with ThreadPoolExecutor(max_workers=16) as pool:
        for contribution in pool.map(page_null, meta): null += contribution
    return null


def atomic_pair(json_text, report_text):
    if OUTPUT.exists() or REPORT.exists(): raise SystemExit("target outputs appeared before installation")
    temporaries = []
    try:
        for text, suffix in ((json_text, ".json.tmp"), (report_text, ".md.tmp")):
            handle = tempfile.NamedTemporaryFile("w", dir=RESULTS, suffix=suffix, delete=False)
            with handle: handle.write(text); handle.flush(); os.fsync(handle.fileno())
            temporaries.append(Path(handle.name))
        os.link(temporaries[0], OUTPUT)
        try: os.link(temporaries[1], REPORT)
        except Exception:
            OUTPUT.unlink(missing_ok=True); raise
    finally:
        for path in temporaries: path.unlink(missing_ok=True)


def main():
    freeze = verify_freeze()
    with SOURCE.open(newline="") as handle: source_rows = list(csv.DictReader(handle, delimiter="\t"))
    with PANEL.open(newline="") as handle: panel_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(panel_rows) != 4571 or Counter(row["boundary_class"] for row in panel_rows) != {"DEFINITE_SPACE": 4143, "DRAWING_INTERRUPTION": 428}: raise SystemExit("target panel contract failed")
    target_pages = {row["page"] for row in panel_rows if row["boundary_class"] == "DRAWING_INTERRUPTION"}
    lookup = {(row["locus"], int(row["group_index"])): row for row in source_rows}
    joined = [(lookup[(row["locus"], int(row["left_group_index"]))], lookup[(row["locus"], int(row["right_group_index"]))]) for row in panel_rows]
    reference = reference_events(source_rows, target_pages)
    target_folios = sorted({row["physical_folio"] for row in panel_rows})
    standardized = np.empty(len(panel_rows)); fold_scales = {}
    for held in target_folios:
        train = [event for event in reference if event[1] != held]
        scorer = fit(train)
        space_scores = np.array([scorer(event[3], event[4]) for event in train if event[2] == 0])
        mean, sd = float(space_scores.mean()), float(space_scores.std(ddof=0))
        if not np.isfinite(sd) or sd <= 0: raise SystemExit("invalid fold scale")
        indices = [i for i, row in enumerate(panel_rows) if row["physical_folio"] == held]
        standardized[indices] = [(scorer(*joined[i]) - mean) / sd for i in indices]
        fold_scales[held] = {"training_events": len(train), "training_spaces": int(sum(event[2] == 0 for event in train)), "space_mean": mean, "space_sd": sd}
    design, length_cells = nuisance_matrix(panel_rows, joined)
    residual = standardized - design @ np.linalg.lstsq(design, standardized, rcond=None)[0]
    if not np.isfinite(standardized).all() or not np.isfinite(residual).all(): raise SystemExit("nonfinite target transform")
    weight, meta, folios = topology(panel_rows)
    vectors = np.column_stack((standardized, residual))
    null = permutation_null(panel_rows, meta, vectors)
    raw = diagnostics(standardized, panel_rows, weight, meta, folios)
    res = diagnostics(residual, panel_rows, weight, meta, folios)
    p_raw = (1 + int(np.sum(null[:, 0] >= raw["effect"]))) / (WORLDS + 1)
    p_res = (1 + int(np.sum(null[:, 1] >= res["effect"]))) / (WORLDS + 1)
    gates = {
        "raw_effect_at_least_010": raw["effect"] >= .10, "residual_effect_at_least_010": res["effect"] >= .10,
        "raw_p_at_most_001": p_raw <= .01, "residual_p_at_most_001": p_res <= .01,
        "positive_residual_folios_at_least_39": res["positive_folios"] >= 39,
        "currier_A_B_residual_at_least_010": min(res["currier_A"], res["currier_B"]) >= .10,
        "H_and_non_H_residual_at_least_010": min(res["section_H"], res["section_non_H"]) >= .10,
        "all_residual_deletions_positive": res["minimum_deletion_effect"] > 0,
        "residual_folio_concentration_at_most_015": res["maximum_absolute_folio_concentration"] <= .15,
    }
    passed = all(gates.values())
    claim = ("Drawing interruptions have a distributed local family-edge shape more like known continuation-line restarts than same-page ordinary spaces, beyond frozen position, group-count, page, and length nuisance fields; no ownership, word boundary, word, sound, POS, meaning, plaintext, language, cipher, or translation follows."
             if passed else
             "The fixed drawing-interruption reset-likeness contrast is not confirmed; this does not prove grammatical continuity and supplies no ownership, word boundary, word, sound, POS, meaning, plaintext, language, cipher, or translation.")
    result = {
        "experiment": "DIC001_DRAWING_INTERRUPTION_TARGET",
        "status": "CONFIRMED_DISTRIBUTED_RESET_LIKENESS" if passed else "FINAL_NONCONFIRMATION",
        "inputs": {"freeze_sha256": sha(FREEZE), "source_sha256": sha(SOURCE), "panel_sha256": sha(PANEL)},
        "counts": {"panel_rows": len(panel_rows), "targets": 428, "controls": 4143, "pages": len(meta), "folios": len(folios), "reference_events": len(reference), "reference_spaces": sum(event[2] == 0 for event in reference), "reference_resets": sum(event[2] == 1 for event in reference), "permutation_worlds": WORLDS},
        "transform": {"nuisance_columns": design.shape[1], "nuisance_rank": int(np.linalg.matrix_rank(design)), "observed_length_cells": len(length_cells), "raw_score_sha256": hashlib.sha256(np.asarray(standardized, dtype="<f8").tobytes()).hexdigest(), "residual_score_sha256": hashlib.sha256(np.asarray(residual, dtype="<f8").tobytes()).hexdigest(), "fold_scales": fold_scales},
        "raw": raw, "residual": res, "p_raw": p_raw, "p_residual": p_res,
        "null": {"raw_min": float(null[:, 0].min()), "raw_max": float(null[:, 0].max()), "residual_min": float(null[:, 1].min()), "residual_max": float(null[:, 1].max()), "matrix_sha256": hashlib.sha256(np.asarray(null, dtype="<f8").tobytes()).hexdigest()},
        "gates": gates, "decision": "RETAIN_RESET_BOUNDARY_SEGMENTATION" if passed else "DO_NOT_ASSERT_RESET_OR_CONTINUITY",
        "target_rows_accessed": 428, "ocr_or_image_features_accessed": False, "english_glosses": 0,
        "claim_ceiling": claim,
    }
    report = (
        "# DIC001 drawing-interruption target\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"Across **{len(folios)}** equally weighted physical folios, raw reset-likeness is **{raw['effect']:.6f}** (p **{p_raw:.6f}**) and nuisance-residual reset-likeness is **{res['effect']:.6f}** (p **{p_res:.6f}**); **{res['positive_folios']}/{len(folios)}** residual folios are positive. Currier A/B residual effects are **{res['currier_A']:.6f}/{res['currier_B']:.6f}**, and Herbal/non-Herbal effects are **{res['section_H']:.6f}/{res['section_non_H']:.6f}**.\n\n"
        + claim + "\n"
    )
    for relative in freeze["target_outputs"]:
        if (REPO / relative).exists(): raise SystemExit("target output appeared during execution")
    atomic_pair(json.dumps(result, indent=2, sort_keys=True) + "\n", report)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
