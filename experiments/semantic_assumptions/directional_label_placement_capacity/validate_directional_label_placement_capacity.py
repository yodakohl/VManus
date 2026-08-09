#!/usr/bin/env python3
"""Independent, nonimporting validator for the direction source-capacity audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "experiments/semantic_assumptions/results/directional_label_placement_capacity.json"
PANEL = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
ANNOTATIONS = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
INTERLINEAR = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
OUTPUT = ROOT / "experiments/semantic_assumptions/results/directional_label_placement_capacity_validation.json"
READINGS = {"IT2a", "RF1b", "ZL3b"}
OBJECT = r"(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|triangle|spikes?)"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(axis: str, text: str) -> str | None:
    text = text.lower()
    if axis == "horizontal":
        pos = bool(re.search(rf"\beast of (?:the )?{OBJECT}\b", text))
        neg = bool(re.search(rf"\bwest of (?:the )?{OBJECT}\b", text))
        mixed = bool(re.search(r"\beast(?:ward|wards)?\b", text)) and bool(re.search(r"\bwest(?:ward|wards)?\b", text))
        names = ("EAST", "WEST")
    else:
        pos = bool(re.search(rf"\babove (?:the )?{OBJECT}\b", text))
        neg = bool(re.search(rf"\b(?:below|under) (?:the )?{OBJECT}\b", text))
        mixed = bool(re.search(r"\babove\b", text)) and bool(re.search(r"\b(?:below|under)\b", text))
        names = ("ABOVE", "BELOW")
    if mixed or pos == neg:
        return None
    return names[0] if pos else names[1]


def rebuild(axis: str, eligible: list[dict[str, str]], coverage: dict[str, set[str]]):
    classified = [(row, label(axis, row["local_comment"])) for row in eligible]
    classified = [(row, direction) for row, direction in classified if direction]
    covered = [(row, direction) for row, direction in classified if coverage[row["source_locus"]] == READINGS]
    groups = defaultdict(list)
    for row, direction in covered:
        groups[(row["page"], row["normalized_code"], row["object_tags"])].append((row, direction))
    groups = {key: rows for key, rows in groups.items() if len({direction for _, direction in rows}) == 2}
    panel = []
    for key, rows in groups.items():
        page, code, tags = key
        folio = re.match(r"^(f\d+)", page).group(1)
        for row, direction in rows:
            panel.append((folio, page, "|".join(key), direction, row["source_locus"], code, tags, ";".join(sorted(READINGS))))
    panel.sort(key=lambda row: tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", row[4])))
    return classified, covered, groups, panel


def main() -> None:
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    annotations = list(csv.DictReader(ANNOTATIONS.open(newline="", encoding="utf-8"), delimiter="\t"))
    coverage = defaultdict(set)
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            coverage[row["locus"]].add(row["edition"])
    eligible = [row for row in annotations if row["certainty"] == "UNHEDGED" and row["relation_scope"] == "EXACT_LOCAL_COMMENT"]
    h_class, h_cov, h_groups, h_panel = rebuild("horizontal", eligible, coverage)
    v_class, v_cov, v_groups, v_panel = rebuild("vertical", eligible, coverage)
    disk_panel = list(csv.reader(PANEL.open(newline="", encoding="utf-8"), delimiter="\t"))
    expected_header = ["physical_folio", "page", "stratum_id", "class", "source_locus", "normalized_code", "object_tags", "readings"]

    checks = {
        "input_hashes": stored["inputs"] == {
            "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": digest(ANNOTATIONS),
            "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv": digest(INTERLINEAR),
        },
        "annotation_total_1192": len(annotations) == 1192,
        "eligible_total_398": len(eligible) == 398,
        "horizontal_classified_108": len(h_class) == 108,
        "horizontal_covered_104": len(h_cov) == 104,
        "horizontal_strata_8": len(h_groups) == 8,
        "horizontal_rows_57": len(h_panel) == 57,
        "horizontal_folios_6": len({row[0] for row in h_panel}) == 6,
        "horizontal_classes_39_18": Counter(row[3] for row in h_panel) == {"EAST": 39, "WEST": 18},
        "horizontal_folio_counts": Counter(row[0] for row in h_panel) == {"f68": 3, "f88": 3, "f89": 6, "f99": 23, "f100": 4, "f102": 18},
        "panel_exact": disk_panel == [expected_header] + [list(row) for row in h_panel],
        "horizontal_all_gates": all(stored["horizontal"]["gates"].values()) and stored["horizontal"]["admitted"] is True,
        "vertical_classified_60": len(v_class) == 60,
        "vertical_covered_58": len(v_cov) == 58,
        "vertical_strata_rows_folios": (len(v_groups), len(v_panel), len({row[0] for row in v_panel})) == (5, 18, 4),
        "vertical_stopped": stored["vertical"]["admitted"] is False and stored["decision"]["stopped_axis"] == "vertical",
        "claim_ceiling": stored["decision"]["authorization"] == "target-blind prescore design only" and "no ownership" in stored["decision"]["claim_ceiling"],
        "final_status": stored["status"] == "PASS_HORIZONTAL_CAPACITY_STOP_VERTICAL_CAPACITY" and stored["voynich_string_features_opened"] is False,
    }
    payload = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": digest(RESULT),
        "panel_sha256": digest(PANEL),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
