#!/usr/bin/env python3
"""Independently reconstruct GDT317 panel scores, ranks, and bindings."""
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
SCORES = R / "gdt317_panel_scores.tsv"
FOLDS = R / "gdt317_folio_scores.tsv"
NULL = R / "gdt317_null.tsv"
RESULT = R / "gdt317_result.json"
OUT = R / "gdt317_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b):
    return abs(float(a) - float(b)) < 5e-12


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


def matched_delta(rows, truth):
    strata = defaultdict(lambda: [[], []])
    for index, row in enumerate(rows):
        strata[(row["cell_id"], row["register"])][int(row["prev_dy"])].append(int(truth[index]))
    numerator = denominator = 0.0
    for absent, present in strata.values():
        if absent and present:
            weight = len(absent) * len(present) / (len(absent) + len(present))
            numerator += weight * (sum(present) / len(present) - sum(absent) / len(absent))
            denominator += weight
    return numerator / denominator if denominator else 0.0


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    design = json.loads(DESIGN.read_text())
    panel_rows = read(PANEL)
    source_truth = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "q") for row in read(SOURCE)}
    check("source_join", all(row["event_id_sha256"] in source_truth for row in panel_rows))
    exported_scores = {row["panel"]: row for row in read(SCORES)}
    exported_folds = {(row["panel"], row["physical_folio"]): row for row in read(FOLDS)}
    exported_null = defaultdict(list)
    for row in read(NULL):
        exported_null[row["panel"]].append(row)
    calculated = []
    for panel in design["powered_panels"]:
        rows = [row for row in panel_rows if row["panel"] == panel]
        truth = np.array([source_truth[row["event_id_sha256"]] for row in rows], float)
        baseline = np.zeros(len(rows))
        candidate = np.zeros(len(rows))
        coefficients = []
        for folio in sorted({row["physical_folio"] for row in rows}):
            train = [row for row in rows if row["physical_folio"] != folio]
            test = [row for row in rows if row["physical_folio"] == folio]
            train_truth = np.array([source_truth[row["event_id_sha256"]] for row in train], float)
            indices = [index for index, row in enumerate(rows) if row["physical_folio"] == folio]
            train_x, test_x = matrices(train, test, False)
            baseline[indices], _ = fit(train_x, train_truth, test_x, design["instrument"]["ridge"])
            train_x, test_x = matrices(train, test, True)
            candidate[indices], beta = fit(train_x, train_truth, test_x, design["instrument"]["ridge"])
            coefficients.append(beta[-1])
            fold_gain = float(np.sum(event_bits(baseline[indices], truth[indices]) - event_bits(candidate[indices], truth[indices])))
            exported_fold = exported_folds[(panel, folio)]
            check("fold", close(exported_fold["prev_dy_coefficient"], beta[-1]) and close(exported_fold["gain_bits"], fold_gain))
        gain = float(np.mean(event_bits(baseline, truth) - event_bits(candidate, truth)))
        delta = matched_delta(rows, truth)
        null_values = []
        for world in range(design["instrument"]["null_worlds"]):
            permuted = permute(truth, rows, design["instrument"]["null_seed"], world, panel)
            null_values.append(float(np.mean(event_bits(baseline, permuted) - event_bits(candidate, permuted))))
        check("null_rows", len(exported_null[panel]) == len(null_values))
        check("null_values", all(close(row["alignment_gain_bits_per_event"], value) for row, value in zip(exported_null[panel], null_values)))
        diagnostic_p = (1 + sum(value >= gain - 1e-15 for value in null_values)) / (1 + len(null_values))
        row = exported_scores[panel]
        check("panel_score", close(row["gain_bits_per_event"], gain) and close(row["matched_post_dy_delta"], delta) and int(row["positive_coefficients"]) == sum(value > 0 for value in coefficients) and close(row["alignment_diagnostic_p"], diagnostic_p))
        calculated.append((panel, gain, delta))

    gain_order = sorted(calculated, key=lambda item: (-item[1], item[0]))
    delta_order = sorted(calculated, key=lambda item: (-item[2], item[0]))
    check("ranks", all(int(exported_scores[item[0]]["gain_rank"]) == rank for rank, item in enumerate(gain_order, 1)) and all(int(exported_scores[item[0]]["delta_rank"]) == rank for rank, item in enumerate(delta_order, 1)))
    voynich = exported_scores["VOYNICH_REFERENCE"]
    controls_ge = sum(float(row["gain_bits_per_event"]) >= float(voynich["gain_bits_per_event"]) - 1e-15 for panel, row in exported_scores.items() if panel != "VOYNICH_REFERENCE")
    if int(voynich["gain_rank"]) == 1 and int(voynich["delta_rank"]) == 1:
        status = "Q_POST_DY_VOYNICH_ENRICHED"
    elif controls_ge >= 2:
        status = "Q_POST_DY_NOT_VOYNICH_SPECIFIC"
    else:
        status = "Q_POST_DY_CONTROL_MIXED"
    result = json.loads(RESULT.read_text())
    stored_content = result.pop("content_sha256")
    check("content", stored_content == canonical_hash(result))
    check("status", result["status"] == status and result["summary"]["controls_gain_ge_voynich"] == controls_ge)
    check("bindings", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]) and all(result["outputs"][name] == sha(R / name) for name in result["outputs"]) and all(result["documents"][name] == sha(R / name) for name in result["documents"]) and all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("f84", not any(result["f84"].values()) and not any(row["page"].startswith("f84") for row in panel_rows))
    validation = {
        "schema": "GDT317_Q_POST_DY_CONTROL_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks": checks,
        "result_sha256": sha(RESULT), "f84_rows": 0,
        "scope": "INDEPENDENT_PANEL_CROSSFIT_NULL_RANK_DECISION_AND_BINDING_RECONSTRUCTION",
    }
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
