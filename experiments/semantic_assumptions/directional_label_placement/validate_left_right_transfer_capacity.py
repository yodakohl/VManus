#!/usr/bin/env python3
"""Independent validation of the LEFT/RIGHT source-capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
I = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
P = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
R = ROOT / "experiments/semantic_assumptions/results/directional_label_left_right_capacity.json"
O = ROOT / "experiments/semantic_assumptions/results/directional_label_left_right_capacity_validation.json"
READINGS = {"IT2a", "RF1b", "ZL3b"}
OBJECT = r"(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|triangle|spikes?|figure|drawing|pool|pipe|band|circle)"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return list(csv.DictReader(path.open(newline="", encoding="utf-8"), delimiter="\t"))


def main() -> None:
    stored = json.loads(R.read_text())
    annotations = load(A)
    old = {row["source_locus"] for row in load(P)}
    coverage = defaultdict(set)
    for row in load(I): coverage[row["locus"]].add(row["edition"])
    selected = []
    for row in annotations:
        if row["certainty"] != "UNHEDGED" or row["relation_scope"] != "EXACT_LOCAL_COMMENT" or row["source_locus"] in old or coverage[row["source_locus"]] != READINGS: continue
        text = row["local_comment"].lower()
        left = bool(re.search(rf"\bleft of (?:the )?{OBJECT}\b", text))
        right = bool(re.search(rf"\bright of (?:the )?{OBJECT}\b", text))
        mixed = bool(re.search(r"\bleft\b", text)) and bool(re.search(r"\bright\b", text))
        if not mixed and left != right: selected.append((row, "LEFT" if left else "RIGHT"))
    foreign = [(row, label) for row, label in selected if re.search(r"\bis entry\s*<", row["local_comment"], re.I) or re.search(r"^\s*label\s*<[^>]+>.*\b(?:left|right) of\b", row["local_comment"], re.I)]
    direct = [item for item in selected if item not in foreign]
    checks = {
        "input_hashes": stored["inputs"] == {"annotations": sha(A), "interlinear": sha(I), "excluded_prior_panel": sha(P)},
        "annotation_total": len(annotations) == 1192,
        "prior_57_excluded": len(old) == stored["prior_loci_excluded"] == 57,
        "nine_before_guard": len(selected) == stored["covered_exclusive_rows_before_subject_guard"] == 9,
        "class_counts": Counter(label for _, label in selected) == {"LEFT": 8, "RIGHT": 1},
        "eight_foreign_references": len(foreign) == len(stored["foreign_locus_reference_rows"]) == 8,
        "one_direct_left": [(row["source_locus"], label) for row, label in direct] == [("f84r.1", "LEFT")],
        "zero_matched_strata": stored["matched_exact_strata"] == 0,
        "transfer_unauthorized": stored["decision"]["admitted"] is False and stored["decision"]["bound_e_transfer_test_authorized"] is False,
        "source_only_stop": stored["source_only"] is True and stored["voynich_strings_read"] is False and stored["status"] == "STOP_NO_INDEPENDENT_LEFT_RIGHT_CONTRAST",
    }
    payload = {"status": "PASS" if all(checks.values()) else "FAIL", "checks_passed": sum(checks.values()), "checks_total": len(checks), "checks": checks, "result_sha256": sha(R)}
    O.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if not all(checks.values()): raise SystemExit(1)


if __name__ == "__main__": main()
