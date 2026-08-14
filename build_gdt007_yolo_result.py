#!/usr/bin/env python3
"""Join frozen GDT007 blind reviews and build compact exploratory comparisons."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORE = {"INK_TOUCH_OR_CROSSING": 0, "NARROW_VISIBLE_GAP": 1, "ORDINARY_VISIBLE_GAP": 2, "WIDE_VISIBLE_GAP": 3}


def read(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write(path, rows, fields=None):
    fields = fields or list(rows[0])
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", lineterminator="\n", fieldnames=fields); w.writeheader(); w.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mean(values):
    return sum(values) / len(values) if values else None


def signflip_p(diffs):
    diffs = [x for x in diffs if x != 0]
    if not diffs:
        return 1.0
    observed = abs(sum(diffs))
    extreme = 0
    total = 1 << len(diffs)
    for mask in range(total):
        value = sum(x if mask & (1 << i) else -x for i, x in enumerate(diffs))
        extreme += abs(value) >= observed - 1e-12
    return extreme / total


def summary(rows, reviewer, localizer_surface, scope):
    states = {"TARGET": [], "CONTROL": []}
    scored = {}
    for row in rows:
        state = row[f"reviewer_{reviewer}_state"]
        if state in SCORE:
            value = SCORE[state]
            states[row["arm"]].append(value)
            scored[(row["pair_id"], row["cut_ordinal"], row["arm"])] = value
    diffs = []
    for pair, ordinal in sorted({(k[0], k[1]) for k in scored}):
        t = scored.get((pair, ordinal, "TARGET")); c = scored.get((pair, ordinal, "CONTROL"))
        if t is not None and c is not None:
            diffs.append(t - c)
    tm, cm = mean(states["TARGET"]), mean(states["CONTROL"])
    return {
        "reviewer": reviewer,
        "localizer_surface": localizer_surface,
        "scope": scope,
        "target_resolved": str(len(states["TARGET"])),
        "control_resolved": str(len(states["CONTROL"])),
        "target_mean_gap_score": "" if tm is None else f"{tm:.9f}",
        "control_mean_gap_score": "" if cm is None else f"{cm:.9f}",
        "target_minus_control": "" if tm is None or cm is None else f"{tm-cm:.9f}",
        "paired_resolved": str(len(diffs)),
        "paired_mean_difference": "" if not diffs else f"{mean(diffs):.9f}",
        "paired_signflip_p_two_sided": f"{signflip_p(diffs):.9f}",
        "target_state_counts": json.dumps(Counter(r[f"reviewer_{reviewer}_state"] for r in rows if r["arm"] == "TARGET"), sort_keys=True),
        "control_state_counts": json.dumps(Counter(r[f"reviewer_{reviewer}_state"] for r in rows if r["arm"] == "CONTROL"), sort_keys=True),
    }


def summary_reviewer_mean(rows, localizer_surface, scope):
    states = {"TARGET": [], "CONTROL": []}
    scored = {}
    for row in rows:
        a, b = row["reviewer_A_state"], row["reviewer_B_state"]
        if a in SCORE and b in SCORE:
            value = (SCORE[a] + SCORE[b]) / 2
            states[row["arm"]].append(value)
            scored[(row["pair_id"], row["cut_ordinal"], row["arm"])] = value
    diffs = []
    for pair, ordinal in sorted({(k[0], k[1]) for k in scored}):
        t = scored.get((pair, ordinal, "TARGET")); c = scored.get((pair, ordinal, "CONTROL"))
        if t is not None and c is not None:
            diffs.append(t - c)
    tm, cm = mean(states["TARGET"]), mean(states["CONTROL"])
    return {
        "reviewer": "MEAN_OF_A_B",
        "localizer_surface": localizer_surface,
        "scope": scope,
        "target_resolved": str(len(states["TARGET"])), "control_resolved": str(len(states["CONTROL"])),
        "target_mean_gap_score": "" if tm is None else f"{tm:.9f}", "control_mean_gap_score": "" if cm is None else f"{cm:.9f}",
        "target_minus_control": "" if tm is None or cm is None else f"{tm-cm:.9f}",
        "paired_resolved": str(len(diffs)), "paired_mean_difference": "" if not diffs else f"{mean(diffs):.9f}",
        "paired_signflip_p_two_sided": f"{signflip_p(diffs):.9f}",
        "target_state_counts": "AVERAGED_NUMERIC_REVIEWER_SCORES", "control_state_counts": "AVERAGED_NUMERIC_REVIEWER_SCORES",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("private_join")
    p.add_argument("worklist")
    p.add_argument("review_a")
    p.add_argument("review_b")
    args = p.parse_args()
    join = read(args.private_join); work = read(args.worklist)
    ra = read(args.review_a); rb = read(args.review_b)
    assert len(join) == len(work) == len(ra) == len(rb) == 45
    ids = {r["blind_id"] for r in join}
    assert ids == {r["blind_id"] for r in work} == {r["blind_id"] for r in ra} == {r["blind_id"] for r in rb}
    for rows in (ra, rb):
        assert all(r["review_state"] in set(SCORE) | {"UNRESOLVED"} for r in rows)

    ra = sorted(ra, key=lambda r: r["blind_id"]); rb = sorted(rb, key=lambda r: r["blind_id"])
    write(ROOT / "gdt007_blind_reviews_a.tsv", ra)
    write(ROOT / "gdt007_blind_reviews_b.tsv", rb)
    write(ROOT / "gdt007_blind_worklist.tsv", sorted(work, key=lambda r: r["blind_id"]))
    ja = {r["blind_id"]: r for r in ra}; jb = {r["blind_id"]: r for r in rb}
    joined = []
    for row in sorted(join, key=lambda r: r["blind_id"]):
        out = {k: row[k] for k in ("blind_id", "pair_id", "arm", "cut_ordinal", "locus", "surface", "localizer_variant", "localizer_delta_px", "localizer_a_confidence", "localizer_b_confidence", "agreement_within_50px", "delivered_image_sha256")}
        for reviewer, values in (("A", ja[row["blind_id"]]), ("B", jb[row["blind_id"]])):
            out[f"reviewer_{reviewer}_state"] = values["review_state"]
            out[f"reviewer_{reviewer}_confidence"] = values["confidence"]
            out[f"reviewer_{reviewer}_neutral_note"] = values["neutral_note"]
        joined.append(out)
    write(ROOT / "gdt007_blind_observations.tsv", joined)

    probes = {}
    for row in joined:
        probes.setdefault((row["pair_id"], row["arm"], row["cut_ordinal"]), {})[row["localizer_variant"]] = row
    assert len(probes) == 34
    surfaces = {"LOCALIZER_A": [], "LOCALIZER_B_SENSITIVITY": [], "AGREEMENT_ONLY": []}
    for variants in probes.values():
        a = variants["A"]
        surfaces["LOCALIZER_A"].append(a)
        surfaces["LOCALIZER_B_SENSITIVITY"].append(variants.get("B", a))
        if a["agreement_within_50px"] == "1":
            surfaces["AGREEMENT_ONLY"].append(a)
    comparisons = []
    for surface, values in surfaces.items():
        for reviewer in ("A", "B"):
            comparisons.append(summary(values, reviewer, surface, "ALL_AVAILABLE" if surface != "AGREEMENT_ONLY" else "23_LOCALIZER_AGREEMENT_PROBES"))
        comparisons.append(summary_reviewer_mean(values, surface, "ALL_AVAILABLE" if surface != "AGREEMENT_ONLY" else "23_LOCALIZER_AGREEMENT_PROBES"))
    write(ROOT / "gdt007_baseline_comparison.tsv", comparisons)

    review_agreement = sum(ja[x]["review_state"] == jb[x]["review_state"] for x in ids)
    variant_rows = [r for r in joined if r["localizer_variant"] == "B"]
    variant_agreement = {}
    for reviewer in ("A", "B"):
        agree = 0
        for b in variant_rows:
            a = next(r for r in joined if r["pair_id"] == b["pair_id"] and r["arm"] == b["arm"] and r["cut_ordinal"] == b["cut_ordinal"] and r["localizer_variant"] == "A")
            agree += a[f"reviewer_{reviewer}_state"] == b[f"reviewer_{reviewer}_state"]
        variant_agreement[reviewer] = {"equal_calls": agree, "variants": len(variant_rows)}
    effects = [float(r["target_minus_control"]) for r in comparisons if r["target_minus_control"] and r["reviewer"] in {"A", "B"}]
    same_direction = bool(effects) and (all(x >= 0 for x in effects) or all(x <= 0 for x in effects))
    agreement_mean = next(r for r in comparisons if r["reviewer"] == "MEAN_OF_A_B" and r["localizer_surface"] == "AGREEMENT_ONLY")
    result = {
        "experiment": "GDT007_YOLO_APPROXIMATE_PHYSICAL_CUT_DISCOVERY",
        "status": "WEAK_UNSTABLE_TARGET_GAP_LEAD",
        "exploratory": True,
        "registered_probes": 34,
        "review_crops": 45,
        "localizer_agreement_within_50px": 23,
        "localizer_disagreements_retaining_both": 11,
        "reviewer_exact_state_agreement": {"equal": review_agreement, "total": 45, "fraction": review_agreement / 45},
        "localization_variant_call_agreement": variant_agreement,
        "effect_same_direction_all_six_surfaces": same_direction,
        "strongest_lead": {
            "scope": "23 localizer-agreement probes",
            "reviewer_mean_target_minus_control": agreement_mean["target_minus_control"],
            "paired_mean_difference": agreement_mean["paired_mean_difference"],
            "paired_signflip_p_two_sided": agreement_mean["paired_signflip_p_two_sided"],
            "classification": "INTERESTING_EXPLORATORY_BUT_UNSTABLE",
            "confounds": "postselected targets; 31/34 low-confidence localization in localizer A; reviewer exact-state agreement 25/45; no human review; GDT003 string-null nonconfirmation",
        },
        "comparisons": comparisons,
        "gdt003_constraint": "NOT DISTINGUISHABLE FROM STRING STATISTICS remains controlling",
        "holdout": {"f84r_opened": False, "f84r_rows_retained_joined_or_scored": 0},
        "claim_ceiling": "Postselected AI-direct approximate-localization discovery only; no confirmed spacing effect, grapheme boundary, morpheme, linguistic slot, language, meaning, semantic role, plaintext, or translation.",
        "inputs": {
            "GDT007_YOLO_APPROXIMATE_CUT_METHOD.md": sha(ROOT / "GDT007_YOLO_APPROXIMATE_CUT_METHOD.md"),
            "prepare_gdt007_yolo_packet.py": sha(ROOT / "prepare_gdt007_yolo_packet.py"),
            "build_gdt007_yolo_result.py": sha(ROOT / "build_gdt007_yolo_result.py"),
            "gdt007_localization_reconciliation.tsv": sha(ROOT / "gdt007_localization_reconciliation.tsv"),
            "gdt007_blind_worklist.tsv": sha(ROOT / "gdt007_blind_worklist.tsv"),
            "gdt007_blind_reviews_a.tsv": sha(ROOT / "gdt007_blind_reviews_a.tsv"),
            "gdt007_blind_reviews_b.tsv": sha(ROOT / "gdt007_blind_reviews_b.tsv"),
            "gdt007_blind_observations.tsv": sha(ROOT / "gdt007_blind_observations.tsv"),
            "gdt007_baseline_comparison.tsv": sha(ROOT / "gdt007_baseline_comparison.tsv"),
        },
        "private_packet_bindings": {"private_join_sha256": sha(args.private_join), "source_worklist_sha256": sha(args.worklist)},
    }
    (ROOT / "gdt007_yolo_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"reviewer_agreement": result["reviewer_exact_state_agreement"], "variant_agreement": variant_agreement, "effects": effects, "same_direction": same_direction}, sort_keys=True))


if __name__ == "__main__":
    main()
