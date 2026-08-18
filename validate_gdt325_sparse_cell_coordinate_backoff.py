#!/usr/bin/env python3
"""Independently rebuild GDT325 predictions, null, arithmetic, and hashes."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
RESULT = R / "gdt325_result.json"
OUT = R / "gdt325_validation.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(name):
    with (R / name).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def close(a, b, tolerance=3e-9): return abs(float(a) - float(b)) <= tolerance
def event_bin(n): return "5_6" if n <= 6 else "7_9"


def prob(counts, alpha, line, prev, classes, bs=0.0, bq=0.0):
    scores = np.log(np.array(counts, float) + alpha); scores[classes.index("s")] += bs * line; scores[classes.index("q")] += bq * prev; scores -= scores.max(); value = np.exp(scores); return value / value.sum()


def main():
    checks = []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    result = json.loads(RESULT.read_text()); stored = result.pop("content_sha256"); check("result_content", stored == canonical_hash(result))
    design = json.loads((R / "gdt325_design.json").read_text()); design_stored = design.pop("content_sha256"); check("design_content", design_stored == canonical_hash(design))
    source = [row for row in read("gdt278_native_event_inventory.tsv") if row["control_id"] == "VOYNICH_REFERENCE"]; check("source_f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source))
    classes = design["classes"]; ci = {value: i for i, value in enumerate(classes)}; keys = tuple(design["cell_fields"]); cells = defaultdict(list); source_by_id = {}
    for row in source:
        cells[tuple(row[key] for key in keys)].append(row); source_by_id[hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]] = row
    powered = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    global_counts = np.zeros(len(classes), int); coord_counts = defaultdict(lambda: np.zeros(len(classes), int))
    for key, members in powered.items():
        for row in members: global_counts[ci[row["wrapper"]]] += 1; coord_counts[key[1:]][ci[row["wrapper"]]] += 1
    coord_by_id = {hashlib.sha256(("COORD|" + "|".join(key)).encode()).hexdigest()[:20]: value for key, value in coord_counts.items()}
    panel = read("gdt325_frozen_panel.tsv"); check("panel", len(panel) == 609 and len({row["cell_id"] for row in panel}) == 94 and len({row["physical_folio"] for row in panel}) == 85)
    truth = np.array([ci[source_by_id[row["event_id_sha256"]]["wrapper"]] for row in panel], int); models = design["models"]; probabilities = {model: np.zeros((len(panel), len(classes))) for model in models}; bs = design["fixed_coefficients"]["s_X_line_first"]; bq = design["fixed_coefficients"]["q_X_prev_dy"]
    for i, row in enumerate(panel):
        line, prev, coord = int(row["line_first"]), int(row["prev_dy"]), coord_by_id[row["coordinate_id"]]
        probabilities["GLOBAL"][i] = prob(global_counts, design["alpha"], line, prev, classes); probabilities["GLOBAL_TWO_RULE"][i] = prob(global_counts, design["alpha"], line, prev, classes, bs, bq); probabilities["COORDINATE"][i] = prob(coord, design["alpha"], line, prev, classes); probabilities["COORDINATE_TWO_RULE"][i] = prob(coord, design["alpha"], line, prev, classes, bs, bq)
    bits = {model: -np.log2(np.clip(probabilities[model][np.arange(len(panel)), truth], 1e-15, 1)) for model in models}; by_cell = defaultdict(list)
    for i, row in enumerate(panel): by_cell[row["cell_id"]].append(i)
    cell_rows = {row["cell_id"]: row for row in read("gdt325_cell_scores.tsv")}; observed = {}
    for cell_id, indices in by_cell.items():
        for model in models: check(f"cell_{cell_id}_{model}", close(np.mean(bits[model][indices]), cell_rows[cell_id][f"{model}_bits_per_event"]))
    model_rows = {row["model"]: row for row in read("gdt325_model_scores.tsv")}
    for model in models:
        values = np.array([np.mean(bits[model][indices]) for indices in by_cell.values()]); global_values = np.array([np.mean(bits["GLOBAL"][indices]) for indices in by_cell.values()]); observed[model] = float(np.sum(global_values - values)); check(f"model_cell_{model}", close(values.mean(), model_rows[model]["cell_balanced_bits_per_event"]) and close(observed[model], model_rows[model]["cell_equivalent_gain_bits"])); check(f"model_event_{model}", close(bits[model].mean(), model_rows[model]["event_weighted_bits_per_event"]) and close(np.sum(bits["GLOBAL"] - bits[model]), model_rows[model]["event_weighted_gain_bits"]))
    null_rows = read("gdt325_null.tsv"); check("null_shape", len(null_rows) == 8192 and null_rows[0]["world_index"] == "0" and null_rows[-1]["world_index"] == "8191"); strata = defaultdict(list)
    for i, row in enumerate(panel): strata[(row["register"], row["line_first"], row["prev_dy"], event_bin(int(row["cell_event_count"])))].append(i)
    maxima = []
    for world, stored_row in enumerate(null_rows):
        permuted = truth.copy()
        for stratum, indices in sorted(strata.items()):
            values = truth[indices].copy(); digest = hashlib.sha256(f"{design['null']['seed']}|{world}|{'|'.join(stratum)}".encode()).hexdigest(); rng = np.random.default_rng(int(digest[:16], 16)); rng.shuffle(values); permuted[indices] = values
        world_bits = {model: -np.log2(np.clip(probabilities[model][np.arange(len(panel)), permuted], 1e-15, 1)) for model in models}; gains = {}
        for model in models:
            gains[model] = sum(float(np.mean(world_bits["GLOBAL"][indices]) - np.mean(world_bits[model][indices])) for indices in by_cell.values()); check(f"null_{world}_{model}", close(gains[model], stored_row[model]))
        maxima.append(max(gains.values())); check(f"null_max_{world}", close(maxima[-1], stored_row["max_four_cell_equivalent_gain_bits"]))
    for model in models: check(f"p_{model}", close((1 + sum(value >= observed[model] - 1e-15 for value in maxima)) / 8193, model_rows[model]["max_four_diagnostic_p"]))
    check("decision", result["status"] == "SPARSE_CELL_COORDINATE_BACKOFF_NOT_SUPPORTED" and result["summary"]["best_coordinate_model"] == "COORDINATE")
    check("input_hashes", all(result["inputs"][name] == sha(R / name) for name in result["inputs"])); check("document_hashes", all(result["documents"][name] == sha(R / name) for name in result["documents"])); check("implementation_hashes", all(result["implementation"][name] == sha(R / name) for name in result["implementation"])); check("output_hashes", all(result["outputs"][name] == sha(R / name) for name in result["outputs"])); check("result_f84", result["f84"]["input_rows"] == 0 and not any(value for key, value in result["f84"].items() if key != "input_rows"))
    validation = {"schema": "GDT325_VALIDATION_V1", "status": "PASS", "scope": "INDEPENDENT_SOURCE_REBUILD_ALL_CELL_SCORES_ALL_NULL_WORLDS_ARITHMETIC_DECISION_AND_HASHES", "checks_passed": len(checks), "result_sha256": sha(RESULT), "f84_rows": 0}; validation["content_sha256"] = canonical_hash(validation); OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n"); print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__": main()
