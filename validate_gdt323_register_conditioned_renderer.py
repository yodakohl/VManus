#!/usr/bin/env python3
"""Independently validate GDT323 inventories, arithmetic, hashes, and decision."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt323_result.json"
OUT = R / "gdt323_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(name):
    with (R / name).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=2e-8):
    return abs(float(a) - float(b)) <= tolerance


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    result = json.loads(RESULT.read_text())
    stored = result.pop("content_sha256")
    check("result_content", stored == canonical_hash(result))
    design = json.loads((R / "gdt323_design.json").read_text())
    design_content = design.pop("content_sha256")
    check("design_content", design_content == canonical_hash(design))
    panel = read("gdt318_frozen_panel.tsv")
    check("panel_counts", len(panel) == 5607 and len({r["cell_id"] for r in panel}) == 126 and len({r["physical_folio"] for r in panel}) == 91)
    check("panel_registers", Counter(r["register"] for r in panel) == Counter({"HERBAL_A": 1617, "HERBAL_B": 494, "OTHER_A": 265, "OTHER_B": 1709, "STARS_RECIPE_B": 1522}))
    check("panel_f84", not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in panel))
    models = read("gdt323_model_scores.tsv")
    folds = read("gdt323_folio_scores.tsv")
    registers = read("gdt323_register_scores.tsv")
    sections = read("gdt323_section_scores.tsv")
    coefficients = read("gdt323_coefficient_summary.tsv")
    null = read("gdt323_null.tsv")
    check("model_names", [r["model"] for r in models] == design["models"])
    check("model_counts", [int(r["parameters"]) for r in models] == [0, 2, 4, 10])
    check("fold_shape", len(folds) == 91 * 4 and Counter(r["model"] for r in folds) == Counter({m: 91 for m in design["models"]}))
    check("register_shape", len(registers) == 5 * 3 and Counter(r["model"] for r in registers) == Counter({m: 5 for m in design["models"][1:]}))
    check("section_shape", len(sections) == 6 * 3)
    check("coefficient_shape", len(coefficients) == 2 * (1 + 2 + 5))
    check("null_shape", len(null) == 8192 and [int(null[0]["world_index"]), int(null[-1]["world_index"])] == [0, 8191])
    by_model = {r["model"]: r for r in models}
    for model in design["models"][1:]:
        fold_gain = sum(float(r["gain_bits"]) for r in folds if r["model"] == model)
        register_gain = sum(float(r["gain_bits"]) for r in registers if r["model"] == model)
        section_gain = sum(float(r["gain_bits"]) for r in sections if r["model"] == model)
        check(f"gain_additivity_{model}", close(fold_gain, by_model[model]["raw_gain_bits"], 2e-7) and close(register_gain, fold_gain, 2e-7) and close(section_gain, fold_gain, 2e-7))
        expected_charge = design["parameter_charges_bits"][model] + design["model_selector_bits"]
        check(f"charge_{model}", close(by_model[model]["charge_bits"], expected_charge) and close(by_model[model]["charged_gain_bits"], float(by_model[model]["raw_gain_bits"]) - expected_charge))
        p = (1 + sum(float(r["max_three_gain_bits_per_event"]) >= float(by_model[model]["gain_bits_per_event"]) - 1e-15 for r in null)) / 8193
        check(f"null_p_{model}", close(p, by_model[model]["max_three_diagnostic_p"]))
    for row in coefficients:
        check(f"coef_counts_{row['model']}_{row['group']}_{row['effect']}", int(row["folds"]) == 91 and int(row["positive_folds"]) + int(row["negative_folds"]) == 91)
    eligible = []
    for row in models:
        model = row["model"]
        direction = True if model in ("CELL", "GLOBAL_TWO_RULE") else all(float(c["mean_coefficient"]) > 0 for c in coefficients if c["model"] == model)
        if direction:
            eligible.append(row)
    selected = min(eligible, key=lambda row: float(row["charged_total_bits"]))["model"]
    status = {"REGISTER_TWO_RULE": "REGISTER_CONDITIONED_TWO_RULE_PREFERRED", "CURRIER_TWO_RULE": "CURRIER_CONDITIONED_TWO_RULE_PREFERRED", "GLOBAL_TWO_RULE": "GLOBAL_TWO_RULE_REMAINS_PREFERRED", "CELL": "REGISTER_CONDITIONING_MIXED"}[selected]
    check("decision", selected == result["summary"]["selected_model"] and status == result["status"])
    check("input_hashes", all(result["inputs"][name] == sha(R / name) for name in result["inputs"]))
    check("document_hashes", all(result["documents"][name] == sha(R / name) for name in result["documents"]))
    check("implementation_hashes", all(result["implementation"][name] == sha(R / name) for name in result["implementation"]))
    check("output_hashes", all(result["outputs"][name] == sha(R / name) for name in result["outputs"]))
    check("result_f84", result["f84"]["input_rows"] == 0 and not any(value for key, value in result["f84"].items() if key != "input_rows"))
    validation = {"schema": "GDT323_VALIDATION_V1", "status": "PASS", "scope": "INDEPENDENT_INVENTORY_ARITHMETIC_DECISION_AND_HASH_VALIDATION_NOT_MODEL_REFIT", "checks_passed": len(checks), "checks": checks, "result_sha256": sha(RESULT), "selected_model": selected, "f84_rows": 0}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "selected": selected}, sort_keys=True))


if __name__ == "__main__":
    main()
