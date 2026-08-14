#!/usr/bin/env python3
"""Independent record/claim validator for GDT004 (no producer import)."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_tsv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def guarded_locus_rows(name, wanted_loci):
    with (ROOT / name).open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        locus_i = header.index("locus")
        out = []
        for line in f:
            probe = line.split("\t", locus_i + 1)
            if len(probe) <= locus_i or probe[locus_i] not in wanted_loci:
                continue
            out.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return out


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    checks = []
    def check(name, value):
        checks.append({"name": name, "pass": bool(value)})
        if not value:
            raise AssertionError(name)

    sel = read_tsv("gdt004_module_shape_selection.tsv")
    obs = read_tsv("gdt004_module_shape_observations.tsv")
    atlas = read_tsv("gdt004_module_shape_atlas.tsv")
    hyp = read_tsv("gdt004_module_shape_hypotheses.tsv")
    result = json.loads((ROOT / "gdt004_module_shape_result.json").read_text())
    check("nine_unique_targets", len(sel) == len(obs) == len(atlas) == 9 and len({r["target_id"] for r in atlas}) == 9)
    check("nine_physical_folios", len({r["physical_folio"] for r in atlas}) == 9)
    check("no_f84_in_outputs", all("f84" not in json.dumps(x) for x in [sel, obs, atlas, hyp]))
    check("direct_visual_provenance", all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in atlas))
    check("single_source_groups", all(r["physical_group_state"] == "VISIBLE_SINGLE_SOURCE_GROUP" for r in atlas))
    check("no_distinct_internal_separator", not any(r["left_cut_state"] == "DISTINCT_PHYSICAL_SEPARATOR" or r["right_cut_state"] == "DISTINCT_PHYSICAL_SEPARATOR" for r in atlas))
    check("eight_q_targets", sum(r["operation_A"] == "PREPEND_Q" for r in atlas) == 8)
    check("eight_dy_targets", sum(r["target_surface"].endswith("dy") for r in atlas) == 8)
    check("edition_basic_agreement", all(r["alternate_basic_surface_agreement"] == "3_OF_3" for r in atlas))
    check("prediction_correct", all(r["folio_holdout_exact_correct"] == "1" for r in atlas))

    wanted_loci = {r["locus"] for r in sel}
    src = guarded_locus_rows("experiments/semantic_assumptions/results/source_separator_transcription.tsv", wanted_loci)
    sta = guarded_locus_rows("experiments/semantic_assumptions/results/source_sta_group_alignment.tsv", wanted_loci)
    for s in sel:
        rr = [r for r in src if r["locus"] == s["locus"] and r["source_group_index"] == s["group_index"]]
        ss = [r for r in sta if r["locus"] == s["locus"] and r["source_group_index"] == s["group_index"]]
        check(f"source_join_{s['target_id']}", {r["edition"] for r in rr} == {"ZL3b", "IT2a", "RF1b"} and {r["nearest_basic_eva_primary"] for r in ss} == {s["target_surface"]})
        x,y,w,h = map(int, s["target_xywh"].split(",")); cw=int(s["canvas_width"]); ch=int(s["canvas_height"])
        check(f"target_bounds_{s['target_id']}", x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= cw and y+h <= ch)
    check("hypothesis_ratings", [r["rating"] for r in hyp] == ["PROVISIONAL","PROVISIONAL","WEAK","FAILED","WEAK"])
    check("historical_result_preserved", result["gdt003_constraint"] == "NOT DISTINGUISHABLE FROM STRING STATISTICS remains unchanged")
    check("holdout_sealed", result["holdout"] == {"f84r_formal_payload_opened": False, "f84r_rows_retained_joined_or_scored": 0})
    for name, digest in result["inputs"].items():
        check(f"input_hash_{name}", sha(name) == digest)
    for name, digest in result["outputs"].items():
        check(f"output_hash_{name}", sha(name) == digest)
    check("claim_ceiling", "no morpheme" in result["claim_ceiling"] and "translation" in result["claim_ceiling"])

    payload = {
        "status": "PASS_RECORD_AND_CLAIM_INTEGRITY",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha("gdt004_module_shape_result.json"),
        "report_sha256": sha("GDT004_EXPLORATORY_MODULE_SHAPE_REPORT.md"),
        "validator_sha256": sha("validate_gdt004_module_shape_atlas.py"),
        "branch_ledger_sha256": sha("GDT002_YOLO_LEDGER.tsv"),
        "validator_scope": "Reconstructs source joins, bounds, counts, hashes, holdout exclusion, and claim literals; does not independently repeat human visual inspection or download images.",
    }
    (ROOT / "gdt004_module_shape_validation.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
