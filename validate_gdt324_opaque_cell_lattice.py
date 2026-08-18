#!/usr/bin/env python3
"""Independently rebuild and validate GDT324 without importing its runner."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
RESULT = R / "gdt324_result.json"
OUT = R / "gdt324_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(name):
    with (R / name).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=2e-9):
    return abs(float(a) - float(b)) <= tolerance


def ids(key):
    return (hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20], hashlib.sha256(("HOST|" + key[0]).encode()).hexdigest()[:20], hashlib.sha256(("COORD|" + "|".join(key[1:])).encode()).hexdigest()[:20])


def probability(counts, alpha):
    value = np.array(counts, float) + alpha
    return value / value.sum()


def ce(counts, p):
    counts = np.array(counts, float)
    return float(-np.sum(counts * np.log2(np.clip(p, 1e-15, 1))) / counts.sum())


def event_bin(n):
    return "10_19" if n < 20 else "20_49" if n < 50 else "50_PLUS"


def folio_bin(n):
    return "3_4" if n < 5 else "5_9" if n < 10 else "10_PLUS"


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    result = json.loads(RESULT.read_text())
    stored = result.pop("content_sha256")
    check("result_content", stored == canonical_hash(result))
    design = json.loads((R / "gdt324_design.json").read_text())
    design_stored = design.pop("content_sha256")
    check("design_content", design_stored == canonical_hash(design))
    source = [row for row in read("gdt278_native_event_inventory.tsv") if row["control_id"] == "VOYNICH_REFERENCE"]
    check("source_f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source))
    keys = tuple(design["cell_fields"])
    classes = design["classes"]
    class_index = {value: i for i, value in enumerate(classes)}
    cells = defaultdict(list)
    for row in source:
        cells[tuple(row[key] for key in keys)].append(row)
    eligible = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    key_by_cell = {ids(key)[0]: key for key in eligible}
    panel = read("gdt324_frozen_cells.tsv")
    check("capacity", len(eligible) == 136 and len(panel) == 60 and sum(int(row["event_count"]) for row in panel) == 3135 and len({row["host_id"] for row in panel}) == 20)
    counts = {}
    for cell_id, key in key_by_cell.items():
        value = np.zeros(len(classes), int)
        for row in eligible[key]:
            value[class_index[row["wrapper"]]] += 1
        counts[cell_id] = value
    total = sum(counts.values(), np.zeros(len(classes), int))
    score_rows = {row["cell_id"]: row for row in read("gdt324_cell_scores.tsv")}
    probabilities = {}
    vectors = []
    rebuilt = []
    for panel_row in panel:
        cell_id = panel_row["cell_id"]
        key = key_by_cell[cell_id]
        target = counts[cell_id]
        vectors.append(target)
        _, host_id, coordinate_id = ids(key)
        global_counts = total - target
        host_counts = sum((counts[other] for other, other_key in key_by_cell.items() if other != cell_id and ids(other_key)[1] == host_id), np.zeros(len(classes), int))
        coord_counts = sum((counts[other] for other, other_key in key_by_cell.items() if other != cell_id and ids(other_key)[2] == coordinate_id), np.zeros(len(classes), int))
        pg = probability(global_counts, design["alpha"])
        ph = probability(host_counts, design["alpha"])
        pc = probability(coord_counts, design["alpha"]) if coord_counts.sum() else pg.copy()
        logpa = np.log(ph) + np.log(pc) - np.log(pg)
        pa = np.exp(logpa - logpa.max())
        pa /= pa.sum()
        p = {"GLOBAL": pg, "COORDINATE": pc, "HOST_SIBLING": ph, "HOST_COORD_ADDITIVE": pa}
        probabilities[cell_id] = p
        values = {model: ce(target, p[model]) for model in design["models"]}
        rebuilt.append((target, values))
        stored_row = score_rows[cell_id]
        check(f"cell_identity_{cell_id}", stored_row["host_id"] == host_id and stored_row["coordinate_id"] == coordinate_id and int(stored_row["events"]) == int(target.sum()))
        for model in design["models"]:
            check(f"cell_bits_{cell_id}_{model}", close(values[model], stored_row[f"{model}_bits_per_event"]))
    model_rows = {row["model"]: row for row in read("gdt324_model_scores.tsv")}
    global_values = np.array([values["GLOBAL"] for _, values in rebuilt])
    weights = np.array([target.sum() for target, _ in rebuilt])
    observed = {}
    for model in design["models"]:
        values = np.array([entry[model] for _, entry in rebuilt])
        observed[model] = float(np.sum(global_values - values))
        check(f"model_cell_bits_{model}", close(values.mean(), model_rows[model]["cell_balanced_bits_per_event"]))
        check(f"model_cell_gain_{model}", close(observed[model], model_rows[model]["cell_equivalent_gain_bits"]))
        check(f"model_event_bits_{model}", close(np.average(values, weights=weights), model_rows[model]["event_weighted_bits_per_event"]))
    null_rows = read("gdt324_null.tsv")
    check("null_shape", len(null_rows) == 8192 and null_rows[0]["world_index"] == "0" and null_rows[-1]["world_index"] == "8191")
    strata = defaultdict(list)
    for i, row in enumerate(panel):
        strata[(event_bin(int(row["event_count"])), folio_bin(int(row["folio_count"])))].append(i)
    maxima = []
    for world, stored_row in enumerate(null_rows):
        assignment = list(range(len(panel)))
        for stratum, indices in sorted(strata.items()):
            shuffled = indices.copy()
            digest = hashlib.sha256(f"{design['null']['seed']}|{world}|{stratum[0]}|{stratum[1]}".encode()).hexdigest()
            rng = np.random.default_rng(int(digest[:16], 16))
            rng.shuffle(shuffled)
            for target_index, vector_index in zip(indices, shuffled):
                assignment[target_index] = vector_index
        values = {}
        for model in design["models"][1:]:
            gain = 0.0
            for i, panel_row in enumerate(panel):
                vector = vectors[assignment[i]]
                p = probabilities[panel_row["cell_id"]]
                gain += ce(vector, p["GLOBAL"]) - ce(vector, p[model])
            values[model] = gain
            check(f"null_{world}_{model}", close(gain, stored_row[model]))
        maxima.append(max(values.values()))
        check(f"null_max_{world}", close(maxima[-1], stored_row["max_three_cell_equivalent_gain_bits"]))
    for model in design["models"][1:]:
        p = (1 + sum(value >= observed[model] - 1e-15 for value in maxima)) / 8193
        check(f"p_{model}", close(p, model_rows[model]["max_three_diagnostic_p"]))
    check("decision", result["status"] == "OPAQUE_COORDINATE_ECOLOGY_ONLY" and result["summary"]["best_model"] == "COORDINATE")
    check("input_hashes", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]))
    check("document_hashes", all(result["documents"][name] == sha(R / name) for name in result["documents"]))
    check("implementation_hashes", all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("output_hashes", all(result["outputs"][name] == sha(R / name) for name in result["outputs"]))
    check("result_f84", result["f84"]["input_rows"] == 0 and not any(value for key, value in result["f84"].items() if key != "input_rows"))
    validation = {"schema": "GDT324_VALIDATION_V1", "status": "PASS", "scope": "INDEPENDENT_SOURCE_REBUILD_ALL_CELL_SCORES_ALL_NULL_WORLDS_ARITHMETIC_DECISION_AND_HASHES", "checks_passed": len(checks), "result_sha256": sha(RESULT), "f84_rows": 0}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
