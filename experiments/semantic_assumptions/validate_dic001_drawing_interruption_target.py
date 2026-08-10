#!/usr/bin/env python3
"""Production-free reconstruction of the frozen DIC001 target result."""

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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RES = HERE / "results"
SOURCE = RES / "source_native_structural_interlinear_v1.tsv"
PANEL = RES / "dic001_drawing_interruption_capacity.tsv"
FREEZE = HERE / "DIC001_DRAWING_INTERRUPTION_TARGET_FREEZE.json"
TARGET = RES / "dic001_drawing_interruption_target.json"
TARGET_REPORT = RES / "dic001_drawing_interruption_target_report.md"
OUT = RES / "dic001_drawing_interruption_target_validation.json"
OUT_REPORT = RES / "dic001_drawing_interruption_target_validation_report.md"
SPACE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"
N_WORLD = 65536


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page):
    found = re.match(r"f\d+", page)
    if not found: raise AssertionError(page)
    return found.group(0)


def numeric_locus(locus): return int(locus.rsplit(".", 1)[1])


def verify_seal():
    seal = json.loads(FREEZE.read_text())
    if seal["status"] != "SEALED_SINGLE_TARGET_AUTHORIZED": raise SystemExit("bad seal")
    if set(seal["frozen_files"]) != set(seal["frozen_file_allowlist"]): raise SystemExit("seal allowlist mismatch")
    for relative, expected in seal["frozen_files"].items():
        path = REPO / relative
        if digest(path) != expected: raise SystemExit("seal drift: " + relative)
    return seal


def edge_tuple(left, right):
    x, y = left["family_surface"], right["family_surface"]
    x2 = x[-2:] if len(x) > 1 else "#" + x
    y2 = y[:2] if len(y) > 1 else y + "#"
    return x[-1], y[0], x[-1] + "|" + y[0], x2, y2, x2 + "|" + y2


def classifier(training):
    frequency = [[Counter() for _ in range(6)] for _ in range(2)]
    denominator = [[0] * 6 for _ in range(2)]
    levels = [set() for _ in range(6)]
    for _, _, label, left, right in training:
        for column, value in enumerate(edge_tuple(left, right)):
            frequency[label][column][value] += 1
            denominator[label][column] += 1
            levels[column].add(value)
    def evaluate(left, right):
        result = 0.0
        for column, value in enumerate(edge_tuple(left, right)):
            size = len(levels[column]) + 1
            result += math.log((frequency[1][column][value] + 1) / (denominator[1][column] + size))
            result -= math.log((frequency[0][column][value] + 1) / (denominator[0][column] + size))
        return result
    return evaluate


def make_reference(rows, excluded_pages):
    loci = defaultdict(list)
    for row in rows:
        if row["page"] not in excluded_pages and row["grammar_scope"] == "CONFIRMED_PROSE":
            loci[row["locus"]].append(row)
    for groups in loci.values(): groups.sort(key=lambda x: int(x["group_index"]))
    events = []
    for groups in loci.values():
        for left, right in zip(groups, groups[1:]):
            if left["right_boundary_profile"] == SPACE:
                events.append((left["page"], physical_folio(left["page"]), 0, left, right))
    page_lines = defaultdict(list)
    for groups in loci.values(): page_lines[groups[0]["page"]].append(groups)
    for page, lines in page_lines.items():
        lines.sort(key=lambda groups: numeric_locus(groups[0]["locus"]))
        for prior, latter in zip(lines, lines[1:]):
            if numeric_locus(latter[0]["locus"]) == numeric_locus(prior[0]["locus"]) + 1 and latter[0]["code"].startswith("+P"):
                events.append((page, physical_folio(page), 1, prior[-1], latter[0]))
    return events


def build_basis(panel, neighbors):
    n = len(panel); columns = [np.ones(n)]
    pages = sorted({x["page"] for x in panel})
    columns += [np.array([x["page"] == page for x in panel], dtype=float) for page in pages[1:]]
    position = np.array([float(x["normalized_boundary_position"]) for x in panel])
    columns += [position, position * position, position * position * position]
    decile = np.minimum((10 * position).astype(np.int64), 9)
    columns += [(decile == value).astype(float) for value in range(1, 10)]
    group_count = np.minimum(np.array([int(x["group_count"]) for x in panel]), 20)
    columns += [(group_count == value).astype(float) for value in sorted(set(group_count))[1:]]
    left_length = np.array([min(8, len(left["family_surface"])) for left, _ in neighbors])
    right_length = np.array([min(8, len(right["family_surface"])) for _, right in neighbors])
    cells = sorted(set(zip(left_length.tolist(), right_length.tolist())))
    columns += [((left_length == a) & (right_length == b)).astype(float) for a, b in cells[1:]]
    return np.column_stack(columns), cells


def panel_topology(panel):
    pages = defaultdict(list)
    for index, row in enumerate(panel): pages[row["page"]].append(index)
    folios = sorted({row["physical_folio"] for row in panel})
    folio_page_count = Counter(panel[indices[0]]["physical_folio"] for indices in pages.values())
    overall = np.zeros(len(panel)); metadata = []
    for page, indices_list in pages.items():
        indices = np.array(indices_list)
        high = np.array([i for i in indices if panel[i]["boundary_class"] == "DRAWING_INTERRUPTION"])
        low = np.array([i for i in indices if panel[i]["boundary_class"] == "DEFINITE_SPACE"])
        row = panel[indices[0]]
        multiplier = 1 / (len(folios) * folio_page_count[row["physical_folio"]])
        overall[high] = multiplier / len(high); overall[low] = -multiplier / len(low)
        metadata.append((page, indices, len(high), multiplier, row["physical_folio"], row["currier"], row["section"]))
    return overall, metadata, folios


def describe(vector, panel, overall, metadata, folios):
    per_page = {}
    for page, indices, _, _, _, _, _ in metadata:
        high = np.array([panel[i]["boundary_class"] == "DRAWING_INTERRUPTION" for i in indices])
        per_page[page] = float(vector[indices][high].mean() - vector[indices][~high].mean())
    per_folio = {folio: float(np.mean([per_page[page] for page, _, _, _, f, _, _ in metadata if f == folio])) for folio in folios}
    def subgroup(predicate):
        groups = defaultdict(list)
        for page, _, _, _, folio, currier, section in metadata:
            if predicate(currier, section): groups[folio].append(per_page[page])
        return float(np.mean([np.mean(values) for values in groups.values()]))
    norm = sum(abs(value) for value in per_folio.values())
    return {
        "effect": float(overall @ vector),
        "positive_folios": sum(value > 0 for value in per_folio.values()),
        "currier_A": subgroup(lambda c, s: c == "A"), "currier_B": subgroup(lambda c, s: c == "B"),
        "section_H": subgroup(lambda c, s: s == "H"), "section_non_H": subgroup(lambda c, s: s != "H"),
        "minimum_deletion_effect": min(float(np.mean([value for f, value in per_folio.items() if f != removed])) for removed in folios),
        "maximum_absolute_folio_concentration": max(abs(value) for value in per_folio.values()) / norm,
        "folio_effects": per_folio,
    }


def shuffled_statistics(metadata, vectors):
    def one(meta):
        page, indices, k, scale, _, _, _ = meta
        seed = int.from_bytes(hashlib.sha256(f"76001004|{page}".encode()).digest()[:8], "little")
        priority = np.random.default_rng(seed).random((N_WORLD, len(indices)))
        chosen = np.argpartition(priority, k - 1, axis=1)[:, :k]
        selected = np.take(vectors[indices], chosen, axis=0).sum(axis=1)
        total = vectors[indices].sum(axis=0)
        return scale * (selected / k - (total - selected) / (len(indices) - k))
    result = np.zeros((N_WORLD, 2))
    with ThreadPoolExecutor(max_workers=16) as executor:
        for value in executor.map(one, metadata): result += value
    return result


def reconstruct():
    with SOURCE.open(newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    with PANEL.open(newline="") as handle: panel = list(csv.DictReader(handle, delimiter="\t"))
    assert len(panel) == 4571
    classes = Counter(x["boundary_class"] for x in panel)
    assert classes == {"DEFINITE_SPACE": 4143, "DRAWING_INTERRUPTION": 428}
    target_pages = {x["page"] for x in panel if x["boundary_class"] == "DRAWING_INTERRUPTION"}
    source_index = {(x["locus"], int(x["group_index"])): x for x in source}
    neighbors = [(source_index[(x["locus"], int(x["left_group_index"]))], source_index[(x["locus"], int(x["right_group_index"]))]) for x in panel]
    reference = make_reference(source, target_pages)
    folios = sorted({x["physical_folio"] for x in panel})
    scores = np.empty(len(panel)); scale_records = {}
    for held in folios:
        training = [x for x in reference if x[1] != held]
        model = classifier(training)
        ordinary = np.array([model(x[3], x[4]) for x in training if x[2] == 0])
        mean = float(np.mean(ordinary)); sd = float(np.std(ordinary, ddof=0))
        indices = [i for i, x in enumerate(panel) if x["physical_folio"] == held]
        scores[indices] = [(model(*neighbors[i]) - mean) / sd for i in indices]
        scale_records[held] = {"training_events": len(training), "training_spaces": int(sum(x[2] == 0 for x in training)), "space_mean": mean, "space_sd": sd}
    basis, cells = build_basis(panel, neighbors)
    residual = scores - basis @ np.linalg.lstsq(basis, scores, rcond=None)[0]
    overall, metadata, folios = panel_topology(panel)
    null = shuffled_statistics(metadata, np.column_stack((scores, residual)))
    raw = describe(scores, panel, overall, metadata, folios)
    res = describe(residual, panel, overall, metadata, folios)
    p_raw = (1 + int(np.sum(null[:, 0] >= raw["effect"]))) / 65537
    p_res = (1 + int(np.sum(null[:, 1] >= res["effect"]))) / 65537
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
             if passed else "The fixed drawing-interruption reset-likeness contrast is not confirmed; this does not prove grammatical continuity and supplies no ownership, word boundary, word, sound, POS, meaning, plaintext, language, cipher, or translation.")
    result = {
        "experiment": "DIC001_DRAWING_INTERRUPTION_TARGET",
        "status": "CONFIRMED_DISTRIBUTED_RESET_LIKENESS" if passed else "FINAL_NONCONFIRMATION",
        "inputs": {"freeze_sha256": digest(FREEZE), "source_sha256": digest(SOURCE), "panel_sha256": digest(PANEL)},
        "counts": {"panel_rows": len(panel), "targets": 428, "controls": 4143, "pages": len(metadata), "folios": len(folios),
                   "reference_events": len(reference), "reference_spaces": sum(x[2] == 0 for x in reference), "reference_resets": sum(x[2] == 1 for x in reference), "permutation_worlds": N_WORLD},
        "transform": {"nuisance_columns": basis.shape[1], "nuisance_rank": int(np.linalg.matrix_rank(basis)), "observed_length_cells": len(cells),
                      "raw_score_sha256": hashlib.sha256(np.asarray(scores, dtype="<f8").tobytes()).hexdigest(),
                      "residual_score_sha256": hashlib.sha256(np.asarray(residual, dtype="<f8").tobytes()).hexdigest(), "fold_scales": scale_records},
        "raw": raw, "residual": res, "p_raw": p_raw, "p_residual": p_res,
        "null": {"raw_min": float(null[:, 0].min()), "raw_max": float(null[:, 0].max()), "residual_min": float(null[:, 1].min()), "residual_max": float(null[:, 1].max()),
                 "matrix_sha256": hashlib.sha256(np.asarray(null, dtype="<f8").tobytes()).hexdigest()},
        "gates": gates, "decision": "RETAIN_RESET_BOUNDARY_SEGMENTATION" if passed else "DO_NOT_ASSERT_RESET_OR_CONTINUITY",
        "target_rows_accessed": 428, "ocr_or_image_features_accessed": False, "english_glosses": 0, "claim_ceiling": claim,
    }
    report = (
        "# DIC001 drawing-interruption target\n\n" f"Status: **{result['status']}**.\n\n"
        f"Across **{len(folios)}** equally weighted physical folios, raw reset-likeness is **{raw['effect']:.6f}** (p **{p_raw:.6f}**) and nuisance-residual reset-likeness is **{res['effect']:.6f}** (p **{p_res:.6f}**); **{res['positive_folios']}/{len(folios)}** residual folios are positive. Currier A/B residual effects are **{res['currier_A']:.6f}/{res['currier_B']:.6f}**, and Herbal/non-Herbal effects are **{res['section_H']:.6f}/{res['section_non_H']:.6f}**.\n\n" + claim + "\n")
    return result, report


def compare(x, y, path="root"):
    checks, errors, maximum = 1, [], 0.0
    if type(x) is not type(y): return checks, [path + ": type"], maximum
    if isinstance(x, dict):
        if set(x) != set(y): errors.append(path + ": keys")
        for key in sorted(set(x) & set(y)):
            c, e, m = compare(x[key], y[key], path + "." + key); checks += c; errors += e; maximum = max(maximum, m)
    elif isinstance(x, list):
        if len(x) != len(y): errors.append(path + ": length")
        for index, pair in enumerate(zip(x, y)):
            c, e, m = compare(pair[0], pair[1], f"{path}[{index}]"); checks += c; errors += e; maximum = max(maximum, m)
    elif isinstance(x, float):
        maximum = abs(x - y)
        if maximum > 2e-14: errors.append(f"{path}: delta {maximum:.3g}")
    elif x != y: errors.append(path + ": value")
    return checks, errors, maximum


def main():
    seal = verify_seal()
    if not TARGET.exists() or not TARGET_REPORT.exists(): raise SystemExit("target result absent")
    expected, expected_report = reconstruct()
    checks, errors, maximum = compare(expected, json.loads(TARGET.read_text()))
    checks += 1
    if TARGET_REPORT.read_text() != expected_report: errors.append("target report mismatch")
    checks += len(seal["frozen_files"])
    validation = {
        "experiment": "DIC001_DRAWING_INTERRUPTION_TARGET_VALIDATION",
        "status": "PASS" if not errors else "FAIL", "assertions": checks, "discrepancies": errors,
        "maximum_numeric_abs_difference": maximum, "target_result_sha256": digest(TARGET), "target_report_sha256": digest(TARGET_REPORT),
        "freeze_sha256": digest(FREEZE), "reconstructed_decision": expected["decision"], "reconstructed_gates": expected["gates"],
        "ocr_or_image_features_accessed": False, "english_glosses": 0,
        "claim_ceiling": expected["claim_ceiling"],
    }
    with OUT.open("x") as handle: json.dump(validation, handle, indent=2, sort_keys=True); handle.write("\n")
    OUT_REPORT.write_text(
        "# DIC001 target validation\n\n"
        f"Status: **{validation['status']}** with **{checks:,}** checks and **{len(errors)}** discrepancies. Maximum numeric difference is **{maximum:.3g}**.\n\n"
        f"The independently reconstructed decision is **{expected['decision']}**.\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
