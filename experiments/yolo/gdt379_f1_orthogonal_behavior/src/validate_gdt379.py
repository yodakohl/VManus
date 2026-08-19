#!/usr/bin/env python3
"""Independent retained-data validation for GDT379; never imports the scorer."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
F1 = "2f1c5e56e8f0ff459065"
D_GROUP = "c502a1edfafbe3e54262"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def opaque(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]
def valid_content(obj):
    expected = obj["content_hash"]; clone = dict(obj); clone.pop("content_hash")
    return expected == hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def bucket(n): return "1_8" if n <= 8 else "9_16" if n <= 16 else "17_32" if n <= 32 else "33_PLUS"
def freq_bucket(n): return "0_3" if n <= 3 else "4_7" if n <= 7 else "8_15" if n <= 15 else "16_31" if n <= 31 else "32_PLUS"
def line_position(row):
    i, n = int(row["group_index"]), int(row["group_count"])
    return "SINGLE" if n == 1 else "START" if i == 1 else "END" if i == n else "MIDDLE"
def closure(row):
    if row["dy_closure"] == "1": return "DY"
    if row["b3"] == "1": return "B3"
    return "LINE_END" if int(row["group_index"]) == int(row["group_count"]) else "OTHER"

def main():
    checks = []
    def check(name, value):
        checks.append({"check": name, "pass": bool(value)})
        if not value: raise AssertionError(name)

    with SOURCE.open(newline="") as h: rows = list(csv.DictReader(h, delimiter="\t"))
    check("source_8448", len(rows) == 8448)
    check("source_f84_free", all(not any(r[k].startswith("f84") for k in ["page", "physical_folio", "locus"]) for r in rows))
    check("source_91_folios", len({r["physical_folio"] for r in rows}) == 91)
    check("source_5_registers", len({r["register"] for r in rows}) == 5)
    check("F1_435", sum(r["joint_tuple_id"] == F1 for r in rows) == 435)
    source_groups = [opaque(["SOURCE_GROUP", r["joint_tuple_id"], r["observed_wrapper"]]) for r in rows]
    check("d_rendered_249", sum(x == D_GROUP for x in source_groups) == 249)
    check("d_group_exact_relation", all(rows[i]["joint_tuple_id"] == F1 and rows[i]["observed_wrapper"] == "d" for i, x in enumerate(source_groups) if x == D_GROUP))
    records = defaultdict(list); fields = defaultdict(list)
    for i, r in enumerate(rows):
        records[(r["page"], r["record_ordinal"])].append(i)
        fields[(r["page"], r["record_ordinal"], r["locus"], r["field_ordinal"])].append(i)
    check("records_288", len(records) == 288)
    check("fields_2400", len(fields) == 2400)

    result = json.loads((ART / "gdt379_result.json").read_text())
    check("result_content_hash", valid_content(result))
    check("result_status", result["status"] == "NO_STABLE_JOINTLY_ADJUSTED_ORTHOGONAL_CONSEQUENCE")
    check("no_promotion", result["F1"]["promoted"] is False and result["families"]["promoted"] == 0)
    check("semantic_zero", result["semantic_assignments"] == 0 and result["forbidden_claims_made"] == 0)
    check("f84_flags_false", all(v is False for v in result["f84"].values()))
    check("input_hashes", all(sha(ROOT / p) == digest for p, digest in result["inputs"].items()))
    check("output_hashes", all(sha(ROOT / p) == digest for p, digest in result["outputs"].items()))
    check("document_hashes", all(sha(ROOT / p) == digest for p, digest in result["documents"].items()))
    check("implementation_hashes", all(sha(ROOT / p) == digest for p, digest in result["implementation"].items()))
    check("correction_hashes", all(sha(ROOT / p) == digest for p, digest in result["corrections"].items()))
    for p in result["corrections"]:
        check("correction_content_" + Path(p).stem, valid_content(json.loads((ROOT / p).read_text())))

    with (ART / "gdt379_submetric_results.tsv").open(newline="") as h: sub = list(csv.DictReader(h, delimiter="\t"))
    with (ART / "gdt379_family_results.tsv").open(newline="") as h: fam = list(csv.DictReader(h, delimiter="\t"))
    check("submetrics_36", len(sub) == 36 and len({r["submetric_id"] for r in sub}) == 36)
    check("families_11", len(fam) == 11 and len({r["family_id"] for r in fam}) == 11)
    check("classifications_exact", Counter(r["classification"] for r in fam) == Counter({"NO_SIGNAL": 8, "WEAK": 2, "UNSTABLE": 1}))
    check("all_unassigned", all(r["semantic_state"] == "UNASSIGNED" for r in sub + fam))

    with gzip.open(ART / "gdt379_null_submetrics.tsv.gz", "rt", newline="") as h: null_rows = list(csv.DictReader(h, delimiter="\t"))
    check("null_worlds_4096", len(null_rows) == 4096)
    metric_names = [r["submetric_id"] for r in sub]
    check("null_metric_columns_exact", set(null_rows[0]) == {"world", *metric_names})
    matrix = np.asarray([[float(r[name]) for name in metric_names] for r in null_rows])
    means = matrix.mean(axis=0); sds = matrix.std(axis=0, ddof=1); safe = sds.copy(); safe[safe == 0] = np.inf
    obs = np.asarray([float(r["observed"]) for r in sub])
    zs = (obs - means) / safe
    world_z = (matrix - means) / safe
    max_abs = np.max(np.abs(world_z), axis=1)
    with gzip.open(ART / "gdt379_null.tsv.gz", "rt", newline="") as h: maxima = list(csv.DictReader(h, delimiter="\t"))
    check("global_null_4096", len(maxima) == 4096)
    check("global_maxima_exact", np.max(np.abs(max_abs - np.asarray([float(r["global_max_abs_z"]) for r in maxima]))) < 2e-9)
    for j, row in enumerate(sub):
        local = (1 + np.sum(np.abs(matrix[:, j] - means[j]) >= abs(obs[j] - means[j]) - 1e-15)) / 4097
        joint = (1 + np.sum(max_abs >= abs(zs[j]) - 1e-15)) / 4097
        check("metric_math_" + row["submetric_id"], abs(float(row["null_mean"]) - means[j]) < 2e-10 and abs(float(row["null_sd"]) - sds[j]) < 2e-10 and abs(float(row["z"]) - zs[j]) < 2e-9 and abs(float(row["local_p"]) - local) < 2e-10 and abs(float(row["joint_maxT_p"]) - joint) < 2e-10)

    # Independent exact H2 recurrence and matched stability reconstruction.
    out = np.full(len(rows), np.nan); rlen = np.zeros(len(rows), int)
    for seq in records.values():
        for p, i in enumerate(seq):
            rlen[i] = len(seq)
            if p + 2 < len(seq): out[i] = float(rows[i]["joint_tuple_id"] == rows[seq[p + 2]]["joint_tuple_id"])
    y = np.asarray([r["joint_tuple_id"] == F1 for r in rows])
    check("H2_394_opportunities", int(np.sum(y & np.isfinite(out))) == 394)
    check("H2_29_returns", int(np.nansum(out[y])) == 29)
    h2 = next(r for r in sub if r["submetric_id"] == "F1_D05_RETURN_H2")
    check("H2_rate", abs(float(h2["observed"]) - 29 / 394) < 2e-12)
    totals = Counter(r["joint_tuple_id"] for r in rows); by_folio = Counter((r["physical_folio"], r["joint_tuple_id"]) for r in rows)
    keys = []
    for i, r in enumerate(rows):
        tf = totals[r["joint_tuple_id"]] - by_folio[(r["physical_folio"], r["joint_tuple_id"])]
        keys.append((r["physical_folio"], r["section"], r["register"], r["currier"], r["hand"], bucket(int(rlen[i])), line_position(r), r["within_field_position"], closure(r), freq_bucket(tf)))
    groups = defaultdict(list)
    for i, key in enumerate(keys): groups[key].append(i)
    mobile = [np.asarray(v, int) for v in groups.values() if 0 < int(y[v].sum()) < len(v)]
    residual = np.full(len(rows), np.nan); mobile_mask = np.zeros(len(rows), bool)
    for group in mobile:
        mobile_mask[group] = True
        valid = group[np.isfinite(out[group])]
        if len(valid): residual[valid] = out[valid] - out[valid].mean()
    folio_signs = []
    for folio in sorted({r["physical_folio"] for r in rows}):
        local = np.asarray([r["physical_folio"] == folio for r in rows]) & y & mobile_mask & np.isfinite(residual)
        if local.sum() >= 2: folio_signs.append(residual[local].mean() > 0)
    reg_signs = []
    for reg in sorted({r["register"] for r in rows}):
        local = np.asarray([r["register"] == reg for r in rows]) & y & mobile_mask & np.isfinite(residual)
        if local.sum() >= 3: reg_signs.append(residual[local].mean() > 0)
    check("H2_stability_67", len(folio_signs) == 67)
    check("H2_stability_26", sum(folio_signs) == 26)
    check("H2_registers_5", len(reg_signs) == 5 and sum(reg_signs) == 5)
    check("H2_class_unstable", next(r for r in fam if r["family_id"] == "F1_D05_SCOPE_HORIZON")["classification"] == "UNSTABLE")

    with (ART / "gdt379_f1_chains.tsv").open(newline="") as h: chains = list(csv.DictReader(h, delimiter="\t"))
    check("chain_rows_22", len(chains) == 22)
    check("chain_max_arity_4", max(int(r["operand_arity"]) for r in chains) == 4)
    with (ART / "gdt379_f2_held_folds.tsv").open(newline="") as h: f2 = list(csv.DictReader(h, delimiter="\t"))
    check("F2_84_folds", len(f2) == 84)
    check("F2_not_F1", all(r["selected_F2_opaque_id"] != F1 for r in f2))
    f2_score = sum(float(r["standardized_held_contribution"]) for r in f2) / np.sqrt(len(f2))
    f2_row = next(r for r in sub if r["submetric_id"] == "F1_D06_NESTED_F2_HELD_Z")
    check("F2_score_reconstructed", abs(f2_score - float(f2_row["observed"])) < 2e-9)

    validation = {
        "schema": "GDT379_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks_total": len(checks), "checks": checks,
        "result_sha256": sha(ART / "gdt379_result.json"), "validator_sha256": sha(BASE / "src/validate_gdt379.py"),
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    validation["content_hash"] = hashlib.sha256(json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt379_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")

if __name__ == "__main__": main()
