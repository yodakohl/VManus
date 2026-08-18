#!/usr/bin/env python3
"""Independently reconstruct GDT321 two-rule and full-anchor scoring."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PANEL = R / "gdt318_frozen_panel.tsv"
DESIGN = R / "gdt321_design.json"
MODELS = R / "gdt321_model_scores.tsv"
FOLDS = R / "gdt321_folio_scores.tsv"
SECTIONS = R / "gdt321_section_scores.tsv"
COEFFICIENTS = R / "gdt321_coefficient_summary.tsv"
NULL = R / "gdt321_null.tsv"
RESULT = R / "gdt321_result.json"
OUT = R / "gdt321_validation.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def close(a, b): return abs(float(a) - float(b)) < 5e-12
def softmax(scores):
    shifted = scores - scores.max(axis=1, keepdims=True); values = np.exp(shifted); return values / values.sum(axis=1, keepdims=True)
def offsets(train, test, truth, class_count, alpha):
    cells = sorted({row["cell_id"] for row in train}); ci = {cell: index for index, cell in enumerate(cells)}; counts = np.full((len(cells), class_count), alpha)
    for row, value in zip(train, truth): counts[ci[row["cell_id"]], value] += 1
    logged = np.log(counts); return np.array([logged[ci[row["cell_id"]]] for row in train]), np.array([logged[ci[row["cell_id"]]] for row in test])
def fit_two(train_offsets, train, truth, test_offsets, test, si, qi, ridge):
    beta = np.zeros(2); line = np.array([float(row["line_first"]) for row in train]); prev = np.array([float(row["prev_dy"]) for row in train])
    for _ in range(60):
        scores = train_offsets.copy(); scores[:, si] += beta[0] * line; scores[:, qi] += beta[1] * prev; p = softmax(scores); ys = (truth == si); yq = (truth == qi)
        gradient = np.array([np.sum((p[:, si] - ys) * line) + ridge * beta[0], np.sum((p[:, qi] - yq) * prev) + ridge * beta[1]])
        hessian = np.array([[np.sum(p[:, si] * (1 - p[:, si]) * line * line) + ridge, np.sum(-p[:, si] * p[:, qi] * line * prev)], [np.sum(-p[:, si] * p[:, qi] * line * prev), np.sum(p[:, qi] * (1 - p[:, qi]) * prev * prev) + ridge]])
        step = np.linalg.pinv(hessian) @ gradient; beta -= step
        if abs(step).max() < 1e-9: break
    scores = test_offsets.copy(); scores[:, si] += beta[0] * np.array([float(row["line_first"]) for row in test]); scores[:, qi] += beta[1] * np.array([float(row["prev_dy"]) for row in test]); return softmax(scores), beta
def fit_full(train_offsets, train, truth, test_offsets, test, class_count, ridge):
    x = np.array([[float(row["line_first"]), float(row["prev_dy"])] for row in train]); z = np.array([[float(row["line_first"]), float(row["prev_dy"])] for row in test]); beta = np.zeros((class_count, 2)); eye = np.eye(beta.size) * ridge
    for _ in range(60):
        p = softmax(train_offsets + x @ beta.T); target = np.zeros_like(p); target[np.arange(len(truth)), truth] = 1; gradient = (p - target).T @ x + ridge * beta; hessian = eye.copy()
        for a in range(2):
            for b in range(2):
                weights = x[:, a] * x[:, b]; block = np.diag(np.sum(weights[:, None] * p, axis=0)) - np.einsum("i,ik,il->kl", weights, p, p)
                for k in range(class_count):
                    for l in range(class_count): hessian[k * 2 + a, l * 2 + b] += block[k, l]
        step = np.linalg.pinv(hessian) @ gradient.reshape(-1); beta -= step.reshape(beta.shape)
        if abs(step).max() < 1e-9: break
    return softmax(test_offsets + z @ beta.T)
def bits(probability, truth): return -np.log2(np.clip(probability[np.arange(len(truth)), truth], 1e-12, 1))
def permute(truth, rows, seed, world):
    out = truth.copy(); strata = defaultdict(list)
    for index, row in enumerate(rows): strata[(row["cell_id"], row["register"])].append(index)
    for key, indices in sorted(strata.items()):
        values = truth[indices].copy(); digest = hashlib.sha256(f"{seed}|{world}|{key[0]}|{key[1]}".encode()).hexdigest(); rng = np.random.default_rng(int(digest[:16], 16)); rng.shuffle(values); out[indices] = values
    return out
def main():
    checks = []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    design = json.loads(DESIGN.read_text()); rows = read(PANEL); classes = design["classes"]; ci = {value: index for index, value in enumerate(classes)}
    truth_map = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: ci[row["wrapper"]] for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"}; check("source_join", all(row["event_id_sha256"] in truth_map for row in rows)); truth = np.array([truth_map[row["event_id_sha256"]] for row in rows])
    probabilities = {model: np.zeros((len(rows), len(classes))) for model in ("CELL", "ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR")}; coefficients = []; exported_folds = {(row["physical_folio"], row["model"]): row for row in read(FOLDS)}; folios = sorted({row["physical_folio"] for row in rows})
    for folio in folios:
        tri = [i for i, row in enumerate(rows) if row["physical_folio"] != folio]; tei = [i for i, row in enumerate(rows) if row["physical_folio"] == folio]; train = [rows[i] for i in tri]; test = [rows[i] for i in tei]; train_truth = truth[tri]; to, zo = offsets(train, test, train_truth, len(classes), design["alpha"]); probabilities["CELL"][tei] = softmax(zo); probabilities["ROBUST_TWO_RULE"][tei], beta = fit_two(to, train, train_truth, zo, test, ci["s"], ci["q"], design["ridge"]); probabilities["FULL_GDT318_ANCHOR"][tei] = fit_full(to, train, train_truth, zo, test, len(classes), design["ridge"]); coefficients.append(beta)
        base = bits(probabilities["CELL"][tei], truth[tei])
        for model in ("CELL", "ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR"):
            gain = 0 if model == "CELL" else float(np.sum(base - bits(probabilities[model][tei], truth[tei]))); check("fold", close(exported_folds[(folio, model)]["gain_bits"], gain))
    baseline = bits(probabilities["CELL"], truth); gains = {model: baseline - bits(probabilities[model], truth) for model in ("ROBUST_TWO_RULE", "FULL_GDT318_ANCHOR")}; observed = {model: float(value.mean()) for model, value in gains.items()}; exported_models = {row["model"]: row for row in read(MODELS)}
    for model, value in observed.items(): check("model", close(exported_models[model]["gain_bits_per_event"], value))
    exported_sections = {(row["section"], row["model"]): row for row in read(SECTIONS)}
    for key, row in exported_sections.items():
        indices = [i for i, value in enumerate(rows) if value["section"] == key[0]]; check("section", close(row["gain_bits"], gains[key[1]][indices].sum()))
    exported_coefficients = {row["parameter"]: row for row in read(COEFFICIENTS)}; check("s_coef", close(exported_coefficients["s_X_line_first"]["mean_coefficient"], np.mean([value[0] for value in coefficients])) and int(exported_coefficients["s_X_line_first"]["positive_folds"]) == sum(value[0] > 0 for value in coefficients)); check("q_coef", close(exported_coefficients["q_X_prev_dy"]["mean_coefficient"], np.mean([value[1] for value in coefficients])) and int(exported_coefficients["q_X_prev_dy"]["positive_folds"]) == sum(value[1] > 0 for value in coefficients))
    exported_null = read(NULL); check("null_rows", len(exported_null) == design["null"]["worlds"]); maxima = []
    for world in range(design["null"]["worlds"]):
        shuffled = permute(truth, rows, design["null"]["seed"], world); base = bits(probabilities["CELL"], shuffled); values = {model: float(np.mean(base - bits(probabilities[model], shuffled))) for model in gains}
        for model, value in values.items(): check("null", close(exported_null[world][model], value))
        maxima.append(max(values.values())); check("null_max", close(exported_null[world]["max_two_gain_bits_per_event"], maxima[-1]))
    for model in gains:
        p = (1 + sum(value >= observed[model] - 1e-15 for value in maxima)) / (1 + len(maxima)); check("p", close(exported_models[model]["max_two_diagnostic_p"], p))
    robust = exported_models["ROBUST_TWO_RULE"]; fraction = observed["ROBUST_TWO_RULE"] / observed["FULL_GDT318_ANCHOR"]; positive_sections = sum(float(row["gain_bits"]) > 0 for (section, model), row in exported_sections.items() if model == "ROBUST_TWO_RULE" and section in ("B", "H", "S")); passed = float(robust["charged_gain_bits"]) > 0 and fraction >= design["decision"]["fraction_full_gain_min"] and positive_sections >= design["decision"]["positive_powered_sections_min"] and all(int(row["positive_folds"]) >= design["decision"]["positive_coefficients_min_each"] for row in exported_coefficients.values()) and float(robust["max_two_diagnostic_p"]) <= design["decision"]["max_two_p_le"]; status = "TWO_RULE_RENDERER_SUFFICIENT" if passed else "TWO_RULE_RENDERER_INSUFFICIENT"
    result = json.loads(RESULT.read_text()); stored = result.pop("content_sha256"); check("content", stored == canonical_hash(result)); check("status", result["status"] == status); check("summary", close(result["summary"]["fraction_full_gain"], fraction) and close(result["summary"]["robust_gain_bits_per_event"], observed["ROBUST_TWO_RULE"])); check("bindings", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]) and all(result["outputs"][name] == sha(R / name) for name in result["outputs"]) and all(result["documents"][name] == sha(R / name) for name in result["documents"]) and all(result["implementation"][name] == sha(R / name) for name in result["implementation"])); check("f84", not any(result["f84"].values()) and not any(row["page"].startswith("f84") for row in rows))
    validation = {"schema": "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "f84_rows": 0, "scope": "INDEPENDENT_RESTRICTED_AND_FULL_CROSSFIT_NULL_MDL_DECISION_RECONSTRUCTION"}; validation["content_sha256"] = canonical_hash(validation); OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n"); print(json.dumps({"status": "PASS", "checks": len(checks), "reconstructed_status": status}, sort_keys=True))
if __name__ == "__main__": main()
