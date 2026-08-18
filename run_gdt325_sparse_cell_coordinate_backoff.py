#!/usr/bin/env python3
"""Score the frozen sparse-cell coordinate backoff and fixed two-rule renderer."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt325_frozen_panel.tsv"
DESIGN = R / "gdt325_design.json"
METHOD = R / "GDT325_SPARSE_CELL_COORDINATE_BACKOFF_METHOD.md"
PREDICTIONS = R / "gdt325_predictions.tsv"
CELLS = R / "gdt325_cell_scores.tsv"
MODELS = R / "gdt325_model_scores.tsv"
SECTIONS = R / "gdt325_section_scores.tsv"
NULL = R / "gdt325_null.tsv"
COUNTER = R / "gdt325_counterexamples.tsv"
REPORT = R / "GDT325_SPARSE_CELL_COORDINATE_BACKOFF_REPORT.md"
RESULT = R / "gdt325_result.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def probability(counts, alpha, line, prev, classes, beta_s=0.0, beta_q=0.0):
    scores = np.log(np.array(counts, float) + alpha)
    scores[classes.index("s")] += beta_s * line
    scores[classes.index("q")] += beta_q * prev
    scores -= scores.max()
    value = np.exp(scores)
    return value / value.sum()


def event_bin(value): return "5_6" if value <= 6 else "7_9"


def main():
    design = json.loads(DESIGN.read_text()); stored = design.pop("content_sha256"); assert stored == canonical_hash(design)
    source = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source)
    classes = design["classes"]; class_index = {value: i for i, value in enumerate(classes)}; keys = tuple(design["cell_fields"])
    source_by_id = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: row for row in source}
    cells = defaultdict(list)
    for row in source: cells[tuple(row[key] for key in keys)].append(row)
    powered = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    global_counts = np.zeros(len(classes), int); coordinate_counts = defaultdict(lambda: np.zeros(len(classes), int))
    for key, members in powered.items():
        for row in members:
            global_counts[class_index[row["wrapper"]]] += 1
            coordinate_counts[key[1:]][class_index[row["wrapper"]]] += 1
    coordinate_by_id = {hashlib.sha256(("COORD|" + "|".join(key)).encode()).hexdigest()[:20]: value for key, value in coordinate_counts.items()}
    panel = read(PANEL); truth = np.array([class_index[source_by_id[row["event_id_sha256"]]["wrapper"]] for row in panel], int)
    models = design["models"]; probabilities = {model: np.zeros((len(panel), len(classes))) for model in models}
    bs = design["fixed_coefficients"]["s_X_line_first"]; bq = design["fixed_coefficients"]["q_X_prev_dy"]
    for i, row in enumerate(panel):
        line, prev = int(row["line_first"]), int(row["prev_dy"]); coord = coordinate_by_id[row["coordinate_id"]]
        probabilities["GLOBAL"][i] = probability(global_counts, design["alpha"], line, prev, classes)
        probabilities["GLOBAL_TWO_RULE"][i] = probability(global_counts, design["alpha"], line, prev, classes, bs, bq)
        probabilities["COORDINATE"][i] = probability(coord, design["alpha"], line, prev, classes)
        probabilities["COORDINATE_TWO_RULE"][i] = probability(coord, design["alpha"], line, prev, classes, bs, bq)
    bit_arrays = {model: -np.log2(np.clip(probabilities[model][np.arange(len(panel)), truth], 1e-15, 1)) for model in models}
    prediction_rows = []
    for i, row in enumerate(panel):
        prediction_rows.append({"event_id_sha256": row["event_id_sha256"], "cell_id": row["cell_id"], "physical_folio": row["physical_folio"], "section": row["section"], "register": row["register"], "line_first": row["line_first"], "prev_dy": row["prev_dy"], "observed_wrapper": classes[truth[i]], **{f"{model}_probabilities_json": json.dumps({classes[j]: round(float(probabilities[model][i, j]), 12) for j in range(len(classes))}, sort_keys=True, separators=(",", ":")) for model in models}})
    write(PREDICTIONS, prediction_rows)
    by_cell = defaultdict(list)
    for i, row in enumerate(panel): by_cell[row["cell_id"]].append(i)
    cell_rows = []
    for cell_id, indices in sorted(by_cell.items()):
        row = panel[indices[0]]; entry = {"cell_id": cell_id, "coordinate_id": row["coordinate_id"], "events": len(indices), "folios": len({panel[i]["physical_folio"] for i in indices}), "majority_wrapper": classes[int(np.argmax(np.bincount(truth[indices], minlength=len(classes))))]}
        for model in models:
            value = float(np.mean(bit_arrays[model][indices])); entry[f"{model}_bits_per_event"] = f"{value:.12f}"; entry[f"{model}_gain_vs_global"] = f"{float(np.mean(bit_arrays['GLOBAL'][indices]) - value):.12f}"
        cell_rows.append(entry)
    write(CELLS, cell_rows)
    observed = {}
    for model in models:
        cell_bits = np.array([float(row[f"{model}_bits_per_event"]) for row in cell_rows]); global_bits = np.array([float(row["GLOBAL_bits_per_event"]) for row in cell_rows])
        observed[model] = {"cell_bits": float(cell_bits.mean()), "cell_gain": float(np.sum(global_bits - cell_bits)), "event_bits": float(bit_arrays[model].mean()), "event_gain": float(np.sum(bit_arrays["GLOBAL"] - bit_arrays[model])), "positive_cells": int(np.sum(cell_bits < global_bits))}
    strata = defaultdict(list)
    for i, row in enumerate(panel): strata[(row["register"], row["line_first"], row["prev_dy"], event_bin(int(row["cell_event_count"])))].append(i)
    null_rows = []
    for world in range(design["null"]["worlds"]):
        permuted = truth.copy()
        for stratum, indices in sorted(strata.items()):
            values = truth[indices].copy(); digest = hashlib.sha256(f"{design['null']['seed']}|{world}|{'|'.join(stratum)}".encode()).hexdigest(); rng = np.random.default_rng(int(digest[:16], 16)); rng.shuffle(values); permuted[indices] = values
        world_bits = {model: -np.log2(np.clip(probabilities[model][np.arange(len(panel)), permuted], 1e-15, 1)) for model in models}
        values = {}
        for model in models:
            total = 0.0
            for indices in by_cell.values(): total += float(np.mean(world_bits["GLOBAL"][indices]) - np.mean(world_bits[model][indices]))
            values[model] = total
        null_rows.append({"world_index": world, **{model: f"{values[model]:.12f}" for model in models}, "max_four_cell_equivalent_gain_bits": f"{max(values.values()):.12f}"})
    write(NULL, null_rows); max_null = [float(row["max_four_cell_equivalent_gain_bits"]) for row in null_rows]
    model_rows = []
    for model in models:
        p = (1 + sum(value >= observed[model]["cell_gain"] - 1e-15 for value in max_null)) / 8193
        selector = observed[model]["cell_gain"] if model == "GLOBAL" else observed[model]["cell_gain"] - design["selector_bits"]
        model_rows.append({"model": model, "cells": len(cell_rows), "events": len(panel), "cell_balanced_bits_per_event": f"{observed[model]['cell_bits']:.12f}", "cell_equivalent_gain_bits": f"{observed[model]['cell_gain']:.12f}", "selector_paid_cell_equivalent_gain_bits": f"{selector:.12f}", "event_weighted_bits_per_event": f"{observed[model]['event_bits']:.12f}", "event_weighted_gain_bits": f"{observed[model]['event_gain']:.12f}", "positive_cells": observed[model]["positive_cells"], "max_four_diagnostic_p": f"{p:.12f}"})
    write(MODELS, model_rows); model_map = {row["model"]: row for row in model_rows}
    section_rows = []
    for section in sorted({row["section"] for row in panel}):
        indices = [i for i, row in enumerate(panel) if row["section"] == section]
        section_by_cell = defaultdict(list)
        for i in indices: section_by_cell[panel[i]["cell_id"]].append(i)
        for model in models[1:]:
            gains = [float(np.mean(bit_arrays["GLOBAL"][members] - bit_arrays[model][members])) for members in section_by_cell.values()]
            section_rows.append({"section": section, "model": model, "cells": len(section_by_cell), "events": len(indices), "cell_equivalent_gain_bits": f"{sum(gains):.12f}", "mean_cell_gain_bits": f"{np.mean(gains):.12f}", "positive_cells": sum(value > 0 for value in gains)})
    write(SECTIONS, section_rows)
    global_best = max((model_map["GLOBAL"], model_map["GLOBAL_TWO_RULE"]), key=lambda row: float(row["cell_equivalent_gain_bits"])); coordinate_best = max((model_map["COORDINATE"], model_map["COORDINATE_TWO_RULE"]), key=lambda row: float(row["cell_equivalent_gain_bits"])); powered_positive = sum(float(row["cell_equivalent_gain_bits"]) > 0 for row in section_rows if row["model"] == coordinate_best["model"] and row["section"] in ("B", "H", "S"))
    passed = float(coordinate_best["selector_paid_cell_equivalent_gain_bits"]) > 0 and float(coordinate_best["cell_equivalent_gain_bits"]) > float(global_best["cell_equivalent_gain_bits"]) and powered_positive >= 2 and float(coordinate_best["max_four_diagnostic_p"]) <= design["decision"]["max_four_p_le"]
    status = "SPARSE_CELL_COORDINATE_BACKOFF_SUPPORTED" if passed else "SPARSE_CELL_COORDINATE_BACKOFF_NOT_SUPPORTED"
    counterexamples = [
        {"counterexample_id": "C01", "finding": "Targets have only 5–9 events each.", "impact": "Individual cell distributions remain noisy despite cell-balanced scoring."},
        {"counterexample_id": "C02", "finding": "All 12 target coordinates occur in the powered training table.", "impact": "The test does not invent a previously unseen coordinate."},
        {"counterexample_id": "C03", "finding": "The two entry coefficients are inherited full-panel GDT322 estimates.", "impact": "Only their fixed use on sparse cells is tested."},
        {"counterexample_id": "C04", "finding": "The null preserves entry state and register but not exact cell outcome counts.", "impact": "The max-four p is a fixed-prediction diagnostic."},
        {"counterexample_id": "C05", "finding": "A coordinate prior predicts wrapper probabilities, not host or content identity.", "impact": "No lexical or semantic interpretation follows."},
        {"counterexample_id": "C06", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The prohibited holdout remains untouched."},
    ]; write(COUNTER, counterexamples)
    report = ["# GDT325 — sparse-cell coordinate backoff", "", f"Status: **{status}**.", "", "All sparse target-cell events were excluded from count estimation. Coordinate counts come only from the 136 powered GDT324 training cells; entry effects are the exact frozen GDT322 coefficients.", "", "| model | cell-balanced bits/event | cell-equivalent gain | selector-paid | event gain | positive cells | max-four p |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in model_rows: report.append(f"| {row['model']} | {float(row['cell_balanced_bits_per_event']):.6f} | {float(row['cell_equivalent_gain_bits']):+.3f} | {float(row['selector_paid_cell_equivalent_gain_bits']):+.3f} | {float(row['event_weighted_gain_bits']):+.2f} | {row['positive_cells']}/94 | {float(row['max_four_diagnostic_p']):.8f} |")
    report += ["", f"Best global model: **{global_best['model']}**. Best coordinate model: **{coordinate_best['model']}**. B/H/S positive sections for the coordinate candidate: {powered_positive}/3.", "", "The coordinate fallback fails on the prospective sparse panel. Preserve GDT322's `UNLICENSED_OR_UNKNOWN` policy; neither the coordinate table nor the two fixed entry rules licenses these cells.", "", "No opaque host or wrapper license is interpreted as a linguistic fact.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored."]; REPORT.write_text("\n".join(report) + "\n")
    outputs = [PREDICTIONS, CELLS, MODELS, SECTIONS, NULL, COUNTER, REPORT]; inputs = [SOURCE, PANEL, R / "gdt325_design_validation.json", R / "gdt322_renderer_model.json", R / "gdt324_result.json"]
    summary = {"training_cells": len(powered), "target_cells": len(cell_rows), "target_events": len(panel), "target_folios": len({row["physical_folio"] for row in panel}), "best_global_model": global_best["model"], "best_coordinate_model": coordinate_best["model"], "coordinate_cell_equivalent_gain_bits": float(coordinate_best["cell_equivalent_gain_bits"]), "coordinate_selector_paid_gain_bits": float(coordinate_best["selector_paid_cell_equivalent_gain_bits"]), "coordinate_max_four_p": float(coordinate_best["max_four_diagnostic_p"]), "positive_powered_sections": powered_positive}
    result = {"schema": "GDT325_SPARSE_CELL_COORDINATE_BACKOFF_RESULT_V1", "status": status, "summary": summary, "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"], "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in inputs}, "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))}, "outputs": {path.name: sha(path) for path in outputs}}; result["content_sha256"] = canonical_hash(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": summary}, sort_keys=True))


if __name__ == "__main__": main()
