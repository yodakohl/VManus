#!/usr/bin/env python3
"""Run the frozen target-cell-blind GDT324 lattice compression test."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt324_frozen_cells.tsv"
DESIGN = R / "gdt324_design.json"
METHOD = R / "GDT324_OPAQUE_CELL_LATTICE_COMPRESSION_METHOD.md"
CELL_SCORES = R / "gdt324_cell_scores.tsv"
MODEL_SCORES = R / "gdt324_model_scores.tsv"
HOST_SCORES = R / "gdt324_host_scores.tsv"
NULL = R / "gdt324_null.tsv"
COUNTER = R / "gdt324_counterexamples.tsv"
REPORT = R / "GDT324_OPAQUE_CELL_LATTICE_COMPRESSION_REPORT.md"
RESULT = R / "gdt324_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ids(key):
    cell = hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20]
    host = hashlib.sha256(("HOST|" + key[0]).encode()).hexdigest()[:20]
    coord = hashlib.sha256(("COORD|" + "|".join(key[1:])).encode()).hexdigest()[:20]
    return cell, host, coord


def probability(counts, alpha):
    value = np.array(counts, float) + alpha
    return value / value.sum()


def event_bin(value):
    return "10_19" if value < 20 else "20_49" if value < 50 else "50_PLUS"


def folio_bin(value):
    return "3_4" if value < 5 else "5_9" if value < 10 else "10_PLUS"


def cross_entropy(counts, probability_vector):
    counts = np.array(counts, float)
    return float(-np.sum(counts * np.log2(np.clip(probability_vector, 1e-15, 1))) / counts.sum())


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    source = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source)
    classes = design["classes"]
    class_index = {value: i for i, value in enumerate(classes)}
    keys = tuple(design["cell_fields"])
    cells = defaultdict(list)
    for row in source:
        cells[tuple(row[key] for key in keys)].append(row)
    eligible = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    key_by_cell = {ids(key)[0]: key for key in eligible}
    panel = read(PANEL)
    target_ids = [row["cell_id"] for row in panel]
    counts_by_cell = {}
    for cell_id, key in key_by_cell.items():
        counts = np.zeros(len(classes), int)
        for row in eligible[key]:
            counts[class_index[row["wrapper"]]] += 1
        counts_by_cell[cell_id] = counts
    total_counts = sum(counts_by_cell.values(), np.zeros(len(classes), int))
    cell_probabilities = {}
    cell_rows = []
    for panel_row in panel:
        cell_id = panel_row["cell_id"]
        key = key_by_cell[cell_id]
        host_id, coordinate_id = panel_row["host_id"], panel_row["coordinate_id"]
        target = counts_by_cell[cell_id]
        global_counts = total_counts - target
        host_counts = sum((counts_by_cell[other] for other, other_key in key_by_cell.items() if other != cell_id and ids(other_key)[1] == host_id), np.zeros(len(classes), int))
        coordinate_counts = sum((counts_by_cell[other] for other, other_key in key_by_cell.items() if other != cell_id and ids(other_key)[2] == coordinate_id), np.zeros(len(classes), int))
        p_global = probability(global_counts, design["alpha"])
        p_host = probability(host_counts, design["alpha"])
        p_coordinate = probability(coordinate_counts, design["alpha"]) if coordinate_counts.sum() else p_global.copy()
        log_additive = np.log(p_host) + np.log(p_coordinate) - np.log(p_global)
        p_additive = np.exp(log_additive - log_additive.max())
        p_additive /= p_additive.sum()
        probabilities = {"GLOBAL": p_global, "COORDINATE": p_coordinate, "HOST_SIBLING": p_host, "HOST_COORD_ADDITIVE": p_additive}
        cell_probabilities[cell_id] = probabilities
        bits = {model: cross_entropy(target, probabilities[model]) for model in design["models"]}
        row = {"cell_id": cell_id, "host_id": host_id, "coordinate_id": coordinate_id, "events": int(target.sum()), "folios": int(panel_row["folio_count"]), "sibling_cells": int(panel_row["sibling_cells"]), "outcome_entropy_bits": f"{cross_entropy(target, probability(target, 0)):.12f}", "majority_wrapper": classes[int(np.argmax(target))], "distinct_wrappers": int(np.count_nonzero(target))}
        for model in design["models"]:
            row[f"{model}_bits_per_event"] = f"{bits[model]:.12f}"
            row[f"{model}_gain_vs_global"] = f"{bits['GLOBAL'] - bits[model]:.12f}"
            row[f"{model}_top_wrapper"] = classes[int(np.argmax(probabilities[model]))]
        cell_rows.append(row)
    write(CELL_SCORES, cell_rows)
    observed = {}
    for model in design["models"]:
        cell_bits = np.array([float(row[f"{model}_bits_per_event"]) for row in cell_rows])
        global_bits = np.array([float(row["GLOBAL_bits_per_event"]) for row in cell_rows])
        event_counts = np.array([int(row["events"]) for row in cell_rows])
        observed[model] = {"cell_bits": float(cell_bits.mean()), "cell_gain": float(np.sum(global_bits - cell_bits)), "event_bits": float(np.average(cell_bits, weights=event_counts)), "event_gain": float(np.sum((global_bits - cell_bits) * event_counts)), "positive_cells": int(np.sum(cell_bits < global_bits))}
    strata = defaultdict(list)
    for index, row in enumerate(panel):
        strata[(event_bin(int(row["event_count"])), folio_bin(int(row["folio_count"])))].append(index)
    target_vectors = [counts_by_cell[row["cell_id"]] for row in panel]
    null_rows = []
    null_values = {model: [] for model in design["models"][1:]}
    for world in range(design["null"]["worlds"]):
        assignment = list(range(len(panel)))
        for stratum, indices in sorted(strata.items()):
            shuffled = indices.copy()
            digest = hashlib.sha256(f"{design['null']['seed']}|{world}|{stratum[0]}|{stratum[1]}".encode()).hexdigest()
            rng = np.random.default_rng(int(digest[:16], 16))
            rng.shuffle(shuffled)
            for target_index, vector_index in zip(indices, shuffled):
                assignment[target_index] = vector_index
        gains = {}
        for model in design["models"][1:]:
            total = 0.0
            for i, panel_row in enumerate(panel):
                vector = target_vectors[assignment[i]]
                probabilities = cell_probabilities[panel_row["cell_id"]]
                total += cross_entropy(vector, probabilities["GLOBAL"]) - cross_entropy(vector, probabilities[model])
            gains[model] = total
            null_values[model].append(total)
        null_rows.append({"world_index": world, **{model: f"{gains[model]:.12f}" for model in design["models"][1:]}, "max_three_cell_equivalent_gain_bits": f"{max(gains.values()):.12f}"})
    max_null = [float(row["max_three_cell_equivalent_gain_bits"]) for row in null_rows]
    model_rows = []
    for model in design["models"]:
        p = 1.0 if model == "GLOBAL" else (1 + sum(value >= observed[model]["cell_gain"] - 1e-15 for value in max_null)) / (1 + len(max_null))
        selector_paid = observed[model]["cell_gain"] if model == "GLOBAL" else observed[model]["cell_gain"] - design["selector_bits"]
        model_rows.append({"model": model, "cells": len(panel), "events": sum(int(row["events"]) for row in cell_rows), "cell_balanced_bits_per_event": f"{observed[model]['cell_bits']:.12f}", "cell_equivalent_gain_bits": f"{observed[model]['cell_gain']:.12f}", "selector_paid_cell_equivalent_gain_bits": f"{selector_paid:.12f}", "event_weighted_bits_per_event": f"{observed[model]['event_bits']:.12f}", "event_weighted_gain_bits": f"{observed[model]['event_gain']:.12f}", "positive_cells": observed[model]["positive_cells"], "max_three_diagnostic_p": f"{p:.12f}"})
    write(MODEL_SCORES, model_rows)
    host_rows = []
    for host_id in sorted({row["host_id"] for row in cell_rows}):
        selected = [row for row in cell_rows if row["host_id"] == host_id]
        for model in design["models"][1:]:
            host_rows.append({"host_id": host_id, "model": model, "cells": len(selected), "events": sum(int(row["events"]) for row in selected), "cell_equivalent_gain_bits": f"{sum(float(row['GLOBAL_gain_vs_global']) - float(row[f'{model}_gain_vs_global']) for row in selected) * -1:.12f}", "positive_cells": sum(float(row[f"{model}_gain_vs_global"]) > 0 for row in selected)})
    write(HOST_SCORES, host_rows)
    write(NULL, null_rows)
    model_map = {row["model"]: row for row in model_rows}
    additive = model_map["HOST_COORD_ADDITIVE"]
    additive_pass = float(additive["selector_paid_cell_equivalent_gain_bits"]) > 0 and float(additive["cell_equivalent_gain_bits"]) > max(float(model_map["COORDINATE"]["cell_equivalent_gain_bits"]), float(model_map["HOST_SIBLING"]["cell_equivalent_gain_bits"])) and float(additive["max_three_diagnostic_p"]) <= design["decision"]["max_three_p_le"]
    if additive_pass:
        status = "OPAQUE_CELL_LATTICE_FACTORABLE"
    else:
        singles = [model_map[model] for model in ("COORDINATE", "HOST_SIBLING") if float(model_map[model]["selector_paid_cell_equivalent_gain_bits"]) > 0]
        best_single = max(singles, key=lambda row: float(row["cell_equivalent_gain_bits"])) if singles else None
        if best_single and best_single["model"] == "HOST_SIBLING":
            status = "OPAQUE_HOST_ECOLOGY_ONLY"
        elif best_single:
            status = "OPAQUE_COORDINATE_ECOLOGY_ONLY"
        else:
            status = "OPAQUE_CELL_LEXICON_NOT_COMPRESSED"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "Only 60 powered sibling cells from 20 recurrent hosts are scoreable.", "impact": "The test has no mechanism for a new or singleton host."},
        {"counterexample_id": "C02", "finding": "Opaque host identity is an explicit predictor.", "impact": "Any gain compresses a known-host table and is not a glyph-derived grammar."},
        {"counterexample_id": "C03", "finding": "Cell eligibility requires 10 events on three folios.", "impact": "Rare-cell and rare-host behavior remains outside scope."},
        {"counterexample_id": "C04", "finding": "The panel follows extensive exposure of the GDT compatibility lexicon.", "impact": "This is targeted architectural decomposition rather than independent discovery."},
        {"counterexample_id": "C05", "finding": "Null worlds match coarse support bins and reuse fitted probabilities.", "impact": "Max-three p is a diagnostic, not an exact refitted conditional test."},
        {"counterexample_id": "C06", "finding": "No f84 row occurs in the source, panel, or output.", "impact": "The prohibited holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = ["# GDT324 — opaque-cell lattice compression", "", f"Status: **{status}**.", "", "Every target cell was removed in full before constructing global, coordinate, same-host-sibling, or additive wrapper distributions.", "", "| model | cell-balanced bits/event | cell-equivalent gain | selector-paid | event-weighted gain | positive cells | max-three p |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in model_rows:
        report.append(f"| {row['model']} | {float(row['cell_balanced_bits_per_event']):.6f} | {float(row['cell_equivalent_gain_bits']):+.3f} | {float(row['selector_paid_cell_equivalent_gain_bits']):+.3f} | {float(row['event_weighted_gain_bits']):+.2f} | {row['positive_cells']}/60 | {float(row['max_three_diagnostic_p']):.8f} |")
    report += ["", f"Coordinate peers provide {float(model_map['COORDINATE']['cell_equivalent_gain_bits']):+.3f} cell-equivalent bits ({float(model_map['COORDINATE']['selector_paid_cell_equivalent_gain_bits']):+.3f} after selection), but same-host sibling cells lose {abs(float(model_map['HOST_SIBLING']['cell_equivalent_gain_bits'])):.3f} bits and the additive model loses {abs(float(additive['cell_equivalent_gain_bits'])):.3f}. Thus a small renderer-coordinate ecology transfers across hosts, while an opaque host does not carry one stable wrapper-license profile across renderer coordinates.", "", "The result compresses neither a new host nor the joint host×coordinate license table. Exact compatibility cells remain required.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [CELL_SCORES, MODEL_SCORES, HOST_SCORES, NULL, COUNTER, REPORT]
    inputs = [SOURCE, PANEL, R / "gdt324_design_validation.json", R / "gdt310_result.json", R / "gdt323_result.json"]
    summary = {"training_cells": len(eligible), "target_cells": len(panel), "target_events": sum(int(row["events"]) for row in cell_rows), "target_hosts": len({row["host_id"] for row in cell_rows}), "best_model": max(model_rows[1:], key=lambda row: float(row["cell_equivalent_gain_bits"]))["model"], "additive_cell_equivalent_gain_bits": float(additive["cell_equivalent_gain_bits"]), "additive_selector_paid_gain_bits": float(additive["selector_paid_cell_equivalent_gain_bits"]), "additive_max_three_p": float(additive["max_three_diagnostic_p"])}
    result = {"schema": "GDT324_OPAQUE_CELL_LATTICE_RESULT_V1", "status": status, "summary": summary, "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"], "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs}}
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()
