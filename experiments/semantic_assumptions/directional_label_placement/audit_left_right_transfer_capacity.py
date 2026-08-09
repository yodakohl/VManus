#!/usr/bin/env python3
"""Source-only independent LEFT/RIGHT transfer-capacity audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ANNOTATIONS = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
INTERLINEAR = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
OLD_PANEL = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
OUTPUT = ROOT / "experiments/semantic_assumptions/results/directional_label_left_right_capacity.json"
READINGS = {"IT2a", "RF1b", "ZL3b"}
OBJECT = r"(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|triangle|spikes?|figure|drawing|pool|pipe|band|circle)"
LEFT = re.compile(rf"\bleft of (?:the )?{OBJECT}\b", re.I)
RIGHT = re.compile(rf"\bright of (?:the )?{OBJECT}\b", re.I)
LEFT_ANY = re.compile(r"\bleft\b", re.I)
RIGHT_ANY = re.compile(r"\bright\b", re.I)
FOREIGN = (
    re.compile(r"\bis entry\s*<", re.I),
    re.compile(r"^\s*label\s*<[^>]+>.*\b(?:left|right) of\b", re.I),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def classify(comment: str) -> str | None:
    left = bool(LEFT.search(comment))
    right = bool(RIGHT.search(comment))
    mixed = bool(LEFT_ANY.search(comment)) and bool(RIGHT_ANY.search(comment))
    if mixed or left == right:
        return None
    return "LEFT" if left else "RIGHT"


def main() -> None:
    annotations = rows(ANNOTATIONS)
    prior = {row["source_locus"] for row in rows(OLD_PANEL)}
    coverage = defaultdict(set)
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            coverage[row["locus"]].add(row["edition"])
    classified = []
    for row in annotations:
        if (
            row["certainty"] != "UNHEDGED"
            or row["relation_scope"] != "EXACT_LOCAL_COMMENT"
            or row["source_locus"] in prior
            or coverage[row["source_locus"]] != READINGS
        ):
            continue
        label = classify(row["local_comment"])
        if label:
            classified.append((row, label))
    foreign = [
        (row, label) for row, label in classified
        if any(pattern.search(row["local_comment"]) for pattern in FOREIGN)
    ]
    direct = [item for item in classified if item not in foreign]
    groups = defaultdict(list)
    for row, label in direct:
        groups[(row["page"], row["normalized_code"], row["object_tags"])].append((row, label))
    matched = {
        key: values for key, values in groups.items()
        if len({label for _, label in values}) == 2
    }
    assert len(annotations) == 1192
    assert len(prior) == 57
    assert len(classified) == 9
    assert Counter(label for _, label in classified) == {"LEFT": 8, "RIGHT": 1}
    assert len(foreign) == 8
    assert [(row["source_locus"], label) for row, label in direct] == [("f84r.1", "LEFT")]
    assert not matched
    payload = {
        "status": "STOP_NO_INDEPENDENT_LEFT_RIGHT_CONTRAST",
        "source_only": True,
        "voynich_strings_read": False,
        "inputs": {
            "annotations": sha(ANNOTATIONS),
            "interlinear": sha(INTERLINEAR),
            "excluded_prior_panel": sha(OLD_PANEL),
        },
        "prior_loci_excluded": len(prior),
        "covered_exclusive_rows_before_subject_guard": len(classified),
        "before_subject_guard_classes": dict(sorted(Counter(label for _, label in classified).items())),
        "foreign_locus_reference_rows": [row["source_locus"] for row, _ in foreign],
        "direct_rows": [
            {
                "source_locus": row["source_locus"], "class": label,
                "page": row["page"], "normalized_code": row["normalized_code"],
                "object_tags": row["object_tags"],
            }
            for row, label in direct
        ],
        "matched_exact_strata": len(matched),
        "decision": {
            "admitted": False,
            "reason": "one direct LEFT label and zero direct RIGHT labels after foreign-locus references are removed",
            "bound_e_transfer_test_authorized": False,
            "claim_ceiling": "source-capacity stop only; no placement marker or semantic gloss",
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
