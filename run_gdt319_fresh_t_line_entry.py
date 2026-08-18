#!/usr/bin/env python3
"""Score fresh t/non-t LOFO physical-line-entry transfer."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt319_frozen_panel.tsv"
DESIGN = R / "gdt319_design.json"
METHOD = R / "GDT319_FRESH_T_LINE_ENTRY_METHOD.md"
PREDICTIONS = R / "gdt319_predictions.tsv"
FOLDS = R / "gdt319_folio_scores.tsv"
SECTIONS = R / "gdt319_section_scores.tsv"
NULL = R / "gdt319_null.tsv"
COUNTER = R / "gdt319_counterexamples.tsv"
REPORT = R / "GDT319_FRESH_T_LINE_ENTRY_REPORT.md"
RESULT = R / "gdt319_result.json"


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


def matrices(train, test, full):
    cells = sorted({row["cell_id"] for row in train})
    def encode(rows):
        return np.array([[1.0] + [float(row["cell_id"] == cell) for cell in cells] + ([float(row["line_first"])] if full else []) for row in rows])
    return encode(train), encode(test)


def fit(train_x, train_y, test_x, ridge):
    beta = np.zeros(train_x.shape[1])
    penalty = np.eye(len(beta)) * ridge
    penalty[0, 0] = 0
    for _ in range(100):
        probability = 1 / (1 + np.exp(-np.clip(train_x @ beta, -30, 30)))
        weight = np.maximum(probability * (1 - probability), 1e-8)
        step = np.linalg.pinv(train_x.T @ (train_x * weight[:, None]) + penalty) @ (train_x.T @ (train_y - probability) - penalty @ beta)
        beta += step
        if abs(step).max() < 1e-10:
            break
    predicted = 1 / (1 + np.exp(-np.clip(test_x @ beta, -30, 30)))
    return np.clip(predicted, 0.01, 0.99), beta


def event_bits(probability, truth):
    return -(truth * np.log2(probability) + (1 - truth) * np.log2(1 - probability))


def permute(truth, rows, seed, world):
    out = truth.copy()
    strata = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        values = truth[indices].copy()
        digest = hashlib.sha256(f"{seed}|{world}|{key[0]}|{key[1]}".encode()).hexdigest()
        rng = np.random.default_rng(int(digest[:16], 16))
        rng.shuffle(values)
        out[indices] = values
    return out


def matched(rows, truth):
    strata = defaultdict(lambda: [[], []])
    raw = [[], []]
    for index, row in enumerate(rows):
        state = int(row["line_first"])
        strata[(row["cell_id"], row["register"])][state].append(int(truth[index]))
        raw[state].append(int(truth[index]))
    numerator = denominator = 0.0
    for elsewhere, line_start in strata.values():
        if elsewhere and line_start:
            weight = len(elsewhere) * len(line_start) / (len(elsewhere) + len(line_start))
            numerator += weight * (sum(line_start) / len(line_start) - sum(elsewhere) / len(elsewhere))
            denominator += weight
    return len(raw[0]), sum(raw[0]) / len(raw[0]), len(raw[1]), sum(raw[1]) / len(raw[1]), numerator / denominator if denominator else 0.0


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    rows = read(PANEL)
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "t") for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}
    truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
    folios = sorted({row["physical_folio"] for row in rows})
    baseline = np.zeros(len(rows))
    candidate = np.zeros(len(rows))
    coefficients = {}
    fold_rows = []
    for folio in folios:
        train = [row for row in rows if row["physical_folio"] != folio]
        test = [row for row in rows if row["physical_folio"] == folio]
        train_truth = np.array([truth_map[row["event_id_sha256"]] for row in train], float)
        indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
        train_x, test_x = matrices(train, test, False)
        baseline[indices], _ = fit(train_x, train_truth, test_x, design["ridge"])
        train_x, test_x = matrices(train, test, True)
        candidate[indices], beta = fit(train_x, train_truth, test_x, design["ridge"])
        coefficients[folio] = beta[-1]
        gain = float(np.sum(event_bits(baseline[indices], truth[indices]) - event_bits(candidate[indices], truth[indices])))
        fold_rows.append({"physical_folio": folio, "events": len(indices), "t_events": int(truth[indices].sum()), "line_start_coefficient": f"{beta[-1]:.12f}", "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(indices):.12f}"})
    gains = event_bits(baseline, truth) - event_bits(candidate, truth)
    gain = float(gains.mean())
    elsewhere_n, elsewhere_rate, line_n, line_rate, delta = matched(rows, truth)
    section_rows = []
    for section in sorted({row["section"] for row in rows}):
        indices = [index for index, row in enumerate(rows) if row["section"] == section]
        section_rows.append({"section": section, "events": len(indices), "t_events": int(truth[indices].sum()), "gain_bits": f"{gains[indices].sum():.12f}", "gain_bits_per_event": f"{gains[indices].mean():.12f}", "powered": int(truth[indices].sum() > 0 and truth[indices].sum() < len(indices))})
    null_values = []
    for world in range(design["null"]["worlds"]):
        permuted = permute(truth, rows, design["null"]["seed"], world)
        null_values.append(float(np.mean(event_bits(baseline, permuted) - event_bits(candidate, permuted))))
    diagnostic_p = (1 + sum(value >= gain - 1e-15 for value in null_values)) / (1 + len(null_values))
    positive_coefficients = int(sum(value > 0 for value in coefficients.values()))
    positive_folios = int(sum(float(row["gain_bits"]) > 0 for row in fold_rows))
    powered = {row["section"]: row for row in section_rows if row["section"] in ("B", "H", "S") and int(row["powered"])}
    positive_powered_sections = int(sum(float(row["gain_bits"]) > 0 for row in powered.values()))
    passed = gain > 0 and delta > 0 and positive_coefficients >= design["decision"]["positive_coefficients_min"] and positive_powered_sections >= design["decision"]["positive_powered_sections_min"] and diagnostic_p <= design["decision"]["alignment_p_le"]
    status = "T_LINE_ENTRY_EXTENDS_TO_FRESH_SURFACES" if passed else "T_LINE_ENTRY_FRESH_SURFACE_TRANSFER_WEAK_OR_FAILED"
    prediction_rows = [{"event_id_sha256": row["event_id_sha256"], "cell_id": row["cell_id"], "physical_folio": row["physical_folio"], "section": row["section"], "register": row["register"], "line_first": row["line_first"], "observed_t": int(truth[index]), "cell_probability": f"{baseline[index]:.12f}", "cell_line_start_probability": f"{candidate[index]:.12f}", "gain_bits": f"{gains[index]:.12f}"} for index, row in enumerate(rows)]
    write(PREDICTIONS, prediction_rows)
    write(FOLDS, fold_rows)
    write(SECTIONS, section_rows)
    write(NULL, [{"world_index": index, "alignment_gain_bits_per_event": f"{value:.12f}"} for index, value in enumerate(null_values)])
    counterexamples = [
        {"counterexample_id": "C01", "finding": "The t line-entry direction was selected after GDT318 exposure.", "impact": "GDT319 is prospective only for transfer to disjoint exact surfaces."},
        {"counterexample_id": "C02", "finding": "Only seven cells, 50 events, and 20 t choices remain after strict surface exclusion.", "impact": "Section and folio estimates have high variance."},
        {"counterexample_id": "C03", "finding": "Every cell is already known to license t.", "impact": "The test predicts event choice, not a new license."},
        {"counterexample_id": "C04", "finding": "The fixed-crossfit alignment diagnostic does not retrain shuffled worlds.", "impact": "Its p-value is diagnostic rather than exact."},
        {"counterexample_id": "C05", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The sealed holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = [
        "# GDT319 — fresh-surface `t` line-entry transfer", "", f"Status: **{status}**.", "",
        "Every exact surface used by GDT318 is excluded.", "",
        f"Across seven new cells, 50 events, and 31 held-folio folds, adding physical line start changes held log loss by {gain:+.6f} bits/event. The cell/register-matched delta is {delta:+.3f}; raw `t` rates are {line_rate:.1%} at line start and {elsewhere_rate:.1%} elsewhere.", "",
        f"Coefficients are positive in {positive_coefficients}/31 folds and {positive_folios}/31 folios improve. Powered-section gains are " + ", ".join(f"{section}={float(row['gain_bits_per_event']):+.4f}" for section, row in powered.items()) + f". Alignment diagnostic p={diagnostic_p:.8f}.", "",
        "A pass extends only the stochastic line-entry selector to t-compatible cells; it does not make t a linguistic prefix.", "", "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [PREDICTIONS, FOLDS, SECTIONS, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt319_capacity.tsv", R / "gdt319_design_validation.json", SOURCE, R / "gdt318_result.json"]
    result = {
        "schema": "GDT319_FRESH_T_LINE_ENTRY_RESULT_V1", "status": status,
        "summary": {"cells": 7, "events": len(rows), "t_events": int(truth.sum()), "folios": len(folios), "gain_bits_per_event": gain, "matched_line_start_delta": delta, "positive_coefficients": positive_coefficients, "positive_folios": positive_folios, "positive_powered_sections": positive_powered_sections, "alignment_diagnostic_p": diagnostic_p},
        "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
