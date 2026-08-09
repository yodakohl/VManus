#!/usr/bin/env python3
"""Source-only clock-half and fRos alias transfer-capacity audit."""

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
X = ROOT / "transcription/voynich_stolfi25e1_lines.tsv"
O = ROOT / "experiments/semantic_assumptions/results/post_direction_transfer_capacity.json"
READINGS = {"IT2a", "RF1b", "ZL3b"}
OBJECT = r"(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|triangle|spikes?)"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return list(csv.DictReader(path.open(newline="", encoding="utf-8"), delimiter="\t"))


def horizontal(comment: str) -> str | None:
    text = comment.lower()
    east = bool(re.search(rf"\beast of (?:the )?{OBJECT}\b", text))
    west = bool(re.search(rf"\bwest of (?:the )?{OBJECT}\b", text))
    mixed = bool(re.search(r"\beast(?:ward|wards)?\b", text)) and bool(re.search(r"\bwest(?:ward|wards)?\b", text))
    return "EAST" if east and not west and not mixed else "WEST" if west and not east and not mixed else None


def main() -> None:
    annotations = load(A)
    old_panel = {row["source_locus"] for row in load(P)}
    coverage = defaultdict(set)
    for row in load(I): coverage[row["locus"]].add(row["edition"])
    clock = re.compile(r"\b(?:at|sector at|moon at|star at)\s*(\d{1,2}):(\d{2})\b", re.I)
    circular = re.compile(r"circle|band|diagram|sector|star|moon|rosette|radial|nymph|label", re.I)
    clock_rows = []
    for row in annotations:
        if row["certainty"] != "UNHEDGED" or row["relation_scope"] != "EXACT_LOCAL_COMMENT" or row["source_locus"] in old_panel or coverage[row["source_locus"]] != READINGS: continue
        if not circular.search(row["unit_description"] + " " + row["local_comment"]): continue
        positions = {(int(hour) % 12) * 60 + int(minute) for hour, minute in clock.findall(row["local_comment"])}
        if len(positions) != 1: continue
        minute = next(iter(positions))
        if minute in (0, 360): continue
        clock_rows.append((row, "EAST_HALF" if minute < 360 else "WEST_HALF", minute))
    groups = defaultdict(list)
    for row, label, minute in clock_rows:
        groups[(row["page"], row["unit"], row["normalized_code"], row["object_tags"])].append((row, label, minute))
    matched = {key: values for key, values in groups.items() if len({label for _, label, _ in values}) == 2}
    matched_folios = {re.match(r"^f\d+", key[0]).group() for key in matched}

    crosswalk = defaultdict(list)
    for row in load(X): crosswalk[row["source_locus"]].append(row)
    rosette = [row for row in annotations if row["page"] == "f85v2"]
    mapped = [crosswalk[row["source_locus"]] for row in rosette]
    strict_rosette = [(row, horizontal(row["local_comment"])) for row in rosette if row["certainty"] == "UNHEDGED" and row["relation_scope"] == "EXACT_LOCAL_COMMENT" and horizontal(row["local_comment"])]

    assert len(clock_rows) == 58
    assert Counter(label for _, label, _ in clock_rows) == {"EAST_HALF": 25, "WEST_HALF": 33}
    assert len(matched) == 6 and sum(len(values) for values in matched.values()) == 49
    assert matched_folios == {"f67", "f68"}
    assert len(rosette) == 158 and all(len(value) == 1 for value in mapped)
    assert all(value[0]["page"] == "fRos" for value in mapped)
    assert all(row["normalized_code"] == value[0]["code"] for row, value in zip(rosette, mapped))
    assert Counter(tuple(sorted(coverage[value[0]["locus"]])) for value in mapped) == {("RF1b", "ZL3b"): 158}
    assert [(row["source_locus"], label) for row, label in strict_rosette] == [("f85v2.56", "WEST"), ("f85v2.138", "WEST")]

    result = {
        "status": "STOP_CLOCK_TWO_FOLIOS_ROSETTE_ZERO_STRICT_CONTRAST",
        "source_only": True,
        "voynich_feature_scored": False,
        "inputs": {"annotations": sha(A), "interlinear": sha(I), "prior_panel": sha(P), "manual_line_crosswalk": sha(X)},
        "clock_half": {
            "prior_loci_excluded": len(old_panel),
            "classified_rows": len(clock_rows),
            "class_counts": dict(sorted(Counter(label for _, label, _ in clock_rows).items())),
            "matched_exact_units": len(matched),
            "matched_rows": sum(len(values) for values in matched.values()),
            "matched_physical_folios": sorted(matched_folios),
            "admitted": False,
            "reason": "only two independent physical folios",
        },
        "rosette_alias": {
            "annotation_rows": len(rosette),
            "unique_exact_mappings": sum(len(value) == 1 for value in mapped),
            "current_page": "fRos",
            "code_exact_mappings": sum(row["normalized_code"] == value[0]["code"] for row, value in zip(rosette, mapped)),
            "coverage": {"RF1b_ZL3b_only": 158, "IT2a": 0},
            "strict_direction_rows": [{"source_locus": row["source_locus"], "current_locus": crosswalk[row["source_locus"]][0]["locus"], "class": label} for row, label in strict_rosette],
            "matched_strata": 0,
            "admitted": False,
        },
        "decision": {"bound_e_transfer_authorized": False, "claim_ceiling": "source-capacity and alias correction only; no placement marker or gloss"},
    }
    O.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__": main()
