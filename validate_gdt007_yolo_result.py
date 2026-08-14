#!/usr/bin/env python3
"""Independent public-artifact validator for GDT007."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORE = {"INK_TOUCH_OR_CROSSING": 0, "NARROW_VISIBLE_GAP": 1, "ORDINARY_VISIBLE_GAP": 2, "WIDE_VISIBLE_GAP": 3}


def read(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def signflip(diffs):
    diffs = [d for d in diffs if d]
    observed = abs(sum(diffs))
    return sum(abs(sum(d if mask & (1 << i) else -d for i, d in enumerate(diffs))) >= observed - 1e-12 for mask in range(1 << len(diffs))) / (1 << len(diffs)) if diffs else 1.0


def main():
    checks = []
    def check(name, value):
        checks.append({"name": name, "pass": bool(value)})
        if not value: raise AssertionError(name)

    rec = read("gdt007_localization_reconciliation.tsv")
    work = read("gdt007_blind_worklist.tsv")
    ra = read("gdt007_blind_reviews_a.tsv"); rb = read("gdt007_blind_reviews_b.tsv")
    obs = read("gdt007_blind_observations.tsv"); comp = read("gdt007_baseline_comparison.tsv")
    counter = read("gdt007_counterexamples.tsv")
    result = json.loads((ROOT / "gdt007_yolo_result.json").read_text())
    ids = {r["blind_id"] for r in work}
    check("counts", len(rec) == 34 and len(work) == len(ra) == len(rb) == len(obs) == 45 and len(comp) == 9)
    check("blind_id_sets", ids == {r["blind_id"] for r in ra} == {r["blind_id"] for r in rb} == {r["blind_id"] for r in obs})
    check("image_hash_bindings", all(next(x for x in work if x["blind_id"] == r["blind_id"])["image_sha256"] == r["delivered_image_sha256"] for r in obs))
    check("localizer_reconciliation", sum(r["reconciliation_state"] == "AGREE_WITHIN_50PX" for r in rec) == 23 and sum(r["review_variant_count"] == "2" for r in rec) == 11 and sum(int(r["review_variant_count"]) for r in rec) == 45)
    check("replacement_count", sum(r["original_offset_state"] == "INSIDE_ONE_STA_SIGN_REPLACED" for r in rec) == 5)
    check("review_labels", all(r["review_state"] in set(SCORE) | {"UNRESOLVED"} for r in ra + rb))
    ja = {r["blind_id"]: r for r in ra}; jb = {r["blind_id"]: r for r in rb}
    agreement = sum(ja[x]["review_state"] == jb[x]["review_state"] for x in ids)
    check("reviewer_agreement", agreement == 25 and result["reviewer_exact_state_agreement"]["equal"] == 25)
    probes = {}
    for row in obs:
        probes.setdefault((row["pair_id"], row["arm"], row["cut_ordinal"]), {})[row["localizer_variant"]] = row
    check("probe_count", len(probes) == 34 and all("A" in v for v in probes.values()))

    expected = {}
    surfaces = {
        "LOCALIZER_A": [v["A"] for v in probes.values()],
        "LOCALIZER_B_SENSITIVITY": [v.get("B", v["A"]) for v in probes.values()],
        "AGREEMENT_ONLY": [v["A"] for v in probes.values() if v["A"]["agreement_within_50px"] == "1"],
    }
    for surface, values in surfaces.items():
        for reviewer in ("A", "B", "MEAN_OF_A_B"):
            scored = {}
            for row in values:
                if reviewer == "MEAN_OF_A_B":
                    a, b = row["reviewer_A_state"], row["reviewer_B_state"]
                    if a not in SCORE or b not in SCORE: continue
                    value = (SCORE[a] + SCORE[b]) / 2
                else:
                    state = row[f"reviewer_{reviewer}_state"]
                    if state not in SCORE: continue
                    value = SCORE[state]
                scored[(row["pair_id"], row["cut_ordinal"], row["arm"])] = value
            t = [v for k, v in scored.items() if k[2] == "TARGET"]; c = [v for k, v in scored.items() if k[2] == "CONTROL"]
            diffs = []
            for pair, ordinal in {(k[0], k[1]) for k in scored}:
                if (pair, ordinal, "TARGET") in scored and (pair, ordinal, "CONTROL") in scored:
                    diffs.append(scored[(pair, ordinal, "TARGET")] - scored[(pair, ordinal, "CONTROL")])
            expected[(surface, reviewer)] = (sum(t)/len(t)-sum(c)/len(c), sum(diffs)/len(diffs), signflip(diffs))
    for row in comp:
        values = expected[(row["localizer_surface"], row["reviewer"])]
        check("comparison_" + row["localizer_surface"] + "_" + row["reviewer"], all(abs(float(row[field]) - value) < 5e-9 for field, value in zip(("target_minus_control", "paired_mean_difference", "paired_signflip_p_two_sided"), values)))
    lead = expected[("AGREEMENT_ONLY", "MEAN_OF_A_B")]
    check("strongest_lead", all(abs(float(result["strongest_lead"][field]) - value) < 5e-9 for field, value in zip(("reviewer_mean_target_minus_control", "paired_mean_difference", "paired_signflip_p_two_sided"), lead)))
    check("counterexamples", len(counter) == 6 and {r["classification"] for r in counter} >= {"COUNTEREXAMPLE", "UNSTABLE", "LIKELY_LOCALIZATION_CONFOUND"})
    check("status", result["status"] == "WEAK_UNSTABLE_TARGET_GAP_LEAD" and not result["effect_same_direction_all_six_surfaces"])
    check("no_f84", all(not r["locus"].startswith("f84") for r in rec + obs) and not result["holdout"]["f84r_opened"] and result["holdout"]["f84r_rows_retained_joined_or_scored"] == 0)
    for name, digest in result["inputs"].items(): check("hash_" + name, sha(name) == digest)
    check("ceiling", "no confirmed spacing effect" in result["claim_ceiling"] and "translation" in result["claim_ceiling"])
    payload = {"status": "PASS_PUBLIC_ARTIFACT_RECONSTRUCTION", "checks_passed": len(checks), "checks": checks, "result_sha256": sha("gdt007_yolo_result.json"), "report_sha256": sha("GDT007_YOLO_APPROXIMATE_CUT_REPORT.md"), "validator_sha256": sha("validate_gdt007_yolo_result.py"), "branch_ledger_sha256": sha("GDT002_YOLO_LEDGER.tsv"), "scope": "Independently reconstructs public blind-ID joins, reviewer/localizer sensitivity effects, exact sign-flip diagnostics, hashes, holdout exclusion, and claim ceiling; it does not repeat visual judgments or recreate omitted crop pixels."}
    (ROOT / "gdt007_yolo_validation.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__": main()
