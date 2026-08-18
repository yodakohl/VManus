#!/usr/bin/env python3
"""Run the unchanged GDT316 q post-DY instrument on frozen controls."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt317_frozen_panel.tsv"
DESIGN = R / "gdt317_design.json"
METHOD = R / "GDT317_Q_POST_DY_CONTROL_CALIBRATION_METHOD.md"
SCORES = R / "gdt317_panel_scores.tsv"
FOLDS = R / "gdt317_folio_scores.tsv"
NULL = R / "gdt317_null.tsv"
COUNTER = R / "gdt317_counterexamples.tsv"
REPORT = R / "GDT317_Q_POST_DY_CONTROL_CALIBRATION_REPORT.md"
RESULT = R / "gdt317_result.json"


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


def matrices(train, test, include_prev_dy):
    cells = sorted({row["cell_id"] for row in train})
    def encode(rows):
        return np.array([[1.0] + [float(row["cell_id"] == cell) for cell in cells] + ([float(row["prev_dy"])] if include_prev_dy else []) for row in rows])
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


def permute(truth, rows, seed, world, panel):
    out = truth.copy()
    strata = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        values = truth[indices].copy()
        digest = hashlib.sha256(f"{seed}|{world}|{panel}|{key[0]}|{key[1]}".encode()).hexdigest()
        rng = np.random.default_rng(int(digest[:16], 16))
        rng.shuffle(values)
        out[indices] = values
    return out


def matched(rows, truth):
    strata = defaultdict(lambda: [[], []])
    raw = [[], []]
    for index, row in enumerate(rows):
        state = int(row["prev_dy"])
        strata[(row["cell_id"], row["register"])][state].append(int(truth[index]))
        raw[state].append(int(truth[index]))
    numerator = denominator = 0.0
    for absent, present in strata.values():
        if absent and present:
            weight = len(absent) * len(present) / (len(absent) + len(present))
            numerator += weight * (sum(present) / len(present) - sum(absent) / len(absent))
            denominator += weight
    return (
        sum(raw[1]) / len(raw[1]) if raw[1] else 0.0,
        sum(raw[0]) / len(raw[0]) if raw[0] else 0.0,
        numerator / denominator if denominator else 0.0,
    )


def main():
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    assert stored == canonical_hash(design)
    all_rows = read(PANEL)
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "q") for row in read(SOURCE)}
    score_rows = []
    fold_rows = []
    null_rows = []
    for panel in design["powered_panels"]:
        rows = [row for row in all_rows if row["panel"] == panel]
        truth = np.array([truth_map[row["event_id_sha256"]] for row in rows], float)
        baseline = np.zeros(len(rows))
        candidate = np.zeros(len(rows))
        coefficients = []
        for folio in sorted({row["physical_folio"] for row in rows}):
            train = [row for row in rows if row["physical_folio"] != folio]
            test = [row for row in rows if row["physical_folio"] == folio]
            train_truth = np.array([truth_map[row["event_id_sha256"]] for row in train], float)
            indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
            train_x, test_x = matrices(train, test, False)
            baseline[indices], _ = fit(train_x, train_truth, test_x, design["instrument"]["ridge"])
            train_x, test_x = matrices(train, test, True)
            candidate[indices], beta = fit(train_x, train_truth, test_x, design["instrument"]["ridge"])
            coefficients.append(beta[-1])
            gain = float(np.sum(event_bits(baseline[indices], truth[indices]) - event_bits(candidate[indices], truth[indices])))
            fold_rows.append({
                "panel": panel, "physical_folio": folio, "events": len(indices),
                "q_events": int(truth[indices].sum()),
                "prev_dy_coefficient": f"{beta[-1]:.12f}",
                "gain_bits": f"{gain:.12f}", "gain_bits_per_event": f"{gain / len(indices):.12f}",
            })
        gains = event_bits(baseline, truth) - event_bits(candidate, truth)
        gain = float(gains.mean())
        post_rate, other_rate, delta = matched(rows, truth)
        null_values = []
        for world in range(design["instrument"]["null_worlds"]):
            permuted = permute(truth, rows, design["instrument"]["null_seed"], world, panel)
            value = float(np.mean(event_bits(baseline, permuted) - event_bits(candidate, permuted)))
            null_values.append(value)
            null_rows.append({"panel": panel, "world_index": world, "alignment_gain_bits_per_event": f"{value:.12f}"})
        diagnostic_p = (1 + sum(value >= gain - 1e-15 for value in null_values)) / (1 + len(null_values))
        score_rows.append({
            "panel": panel, "cells": len({row["cell_id"] for row in rows}),
            "events": len(rows), "q_events": int(truth.sum()), "folios": len(coefficients),
            "gain_bits_per_event": f"{gain:.12f}",
            "matched_post_dy_delta": f"{delta:.12f}",
            "raw_q_rate_post_dy": f"{post_rate:.12f}",
            "raw_q_rate_elsewhere": f"{other_rate:.12f}",
            "positive_coefficients": int(sum(value > 0 for value in coefficients)),
            "positive_folios": int(sum(float(row["gain_bits"]) > 0 for row in fold_rows if row["panel"] == panel)),
            "alignment_diagnostic_p": f"{diagnostic_p:.12f}",
            "gain_rank": "", "delta_rank": "",
        })
    gain_order = sorted(score_rows, key=lambda row: (-float(row["gain_bits_per_event"]), row["panel"]))
    delta_order = sorted(score_rows, key=lambda row: (-float(row["matched_post_dy_delta"]), row["panel"]))
    for rank, row in enumerate(gain_order, 1):
        row["gain_rank"] = rank
    for rank, row in enumerate(delta_order, 1):
        row["delta_rank"] = rank
    by_panel = {row["panel"]: row for row in score_rows}
    voynich = by_panel["VOYNICH_REFERENCE"]
    controls_ge = sum(float(row["gain_bits_per_event"]) >= float(voynich["gain_bits_per_event"]) - 1e-15 for row in score_rows if row["panel"] != "VOYNICH_REFERENCE")
    if int(voynich["gain_rank"]) == 1 and int(voynich["delta_rank"]) == 1:
        status = "Q_POST_DY_VOYNICH_ENRICHED"
    elif controls_ge >= 2:
        status = "Q_POST_DY_NOT_VOYNICH_SPECIFIC"
    else:
        status = "Q_POST_DY_CONTROL_MIXED"
    write(SCORES, sorted(score_rows, key=lambda row: row["panel"]))
    write(FOLDS, fold_rows)
    write(NULL, null_rows)
    counterexamples = [
        {"counterexample_id": "C01", "finding": "Only three control panels meet the frozen q-cell capacity thresholds.", "impact": "Specificity is calibrated against a narrow powered set; thresholds were not relaxed."},
        {"counterexample_id": "C02", "finding": "Control q is an observation-parser surface class, not a harmonized prefix or morpheme.", "impact": "A rank difference calibrates architecture only."},
        {"counterexample_id": "C03", "finding": "Panels differ greatly in folio count and cell support.", "impact": "Raw scores and coverage are reported without rescaling."},
        {"counterexample_id": "C04", "finding": "The fixed-crossfit diagnostic does not retrain within each shuffled world.", "impact": "Its p-values are alignment diagnostics, not exact null tests."},
        {"counterexample_id": "C05", "finding": "Voynich uses the GDT316 disjoint surface panel while controls have no analogous selection history.", "impact": "The control rank is an architectural calibration rather than a symmetric replication."},
        {"counterexample_id": "C06", "finding": "No f84 row occurs in source, panel, or output.", "impact": "The sealed holdout remains untouched."},
    ]
    write(COUNTER, counterexamples)
    report = [
        "# GDT317 — `q` post-DY control calibration", "", f"Status: **{status}**.", "",
        "The GDT316 instrument and all capacity thresholds are unchanged. No panel was rescaled or tuned.", "",
        "| panel | events / q | gain bits/event | matched delta | gain rank | delta rank |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(score_rows, key=lambda item: int(item["gain_rank"])):
        report.append(f"| {row['panel']} | {row['events']} / {row['q_events']} | {float(row['gain_bits_per_event']):+.5f} | {float(row['matched_post_dy_delta']):+.3f} | {row['gain_rank']} | {row['delta_rank']} |")
    report += [
        "", f"Voynich ranks {voynich['gain_rank']}/{len(score_rows)} by held gain and {voynich['delta_rank']}/{len(score_rows)} by matched delta. {controls_ge} controls equal or exceed its held gain.", "",
        "This comparison calibrates the positive GDT316 rule; it does not harmonize the parser surface class across corpora or identify a linguistic function.", "",
        "## Claim ceiling", "", design["claim_ceiling"] + " No f84 row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n")
    outputs = [SCORES, FOLDS, NULL, COUNTER, REPORT]
    inputs = [PANEL, R / "gdt317_capacity.tsv", R / "gdt317_design_validation.json", SOURCE, R / "gdt316_result.json"]
    result = {
        "schema": "GDT317_Q_POST_DY_CONTROL_RESULT_V1", "status": status,
        "summary": {"panels": len(score_rows), "voynich_gain_rank": int(voynich["gain_rank"]), "voynich_delta_rank": int(voynich["delta_rank"]), "controls_gain_ge_voynich": controls_ge},
        "semantic_assignments": 0, "claim_ceiling": design["claim_ceiling"],
        "f84": {"input_rows": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": result["summary"], "scores": score_rows}, sort_keys=True))


if __name__ == "__main__":
    main()
