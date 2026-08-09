#!/usr/bin/env python3
"""Source-only capacity audit for explicit opposing label placements.

The interlinear is consulted only for locus/edition coverage. Voynich strings,
roots, tokens, and grammar features are never read or scored.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/"
    "existing_human_exact_locus_annotations.tsv"
)
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
DEFAULT_JSON = Path(
    "experiments/semantic_assumptions/results/"
    "directional_label_placement_capacity.json"
)
DEFAULT_PANEL = Path(
    "experiments/semantic_assumptions/directional_label_placement_capacity/"
    "HORIZONTAL_SOURCE_PANEL.tsv"
)

READINGS = {"ZL3b", "IT2a", "RF1b"}
OBJECT = (
    r"(?:plant|root(?:s)?|leaf|leaves|stem|nymph(?:s)?|pond|channel|"
    r"funnel|man|container|moon|sun|star(?:s)?|road|rosette|canopy|"
    r"triangle|spikes?)"
)
PATTERNS = {
    "horizontal": {
        "positive": re.compile(rf"\beast of (?:the )?{OBJECT}\b", re.I),
        "negative": re.compile(rf"\bwest of (?:the )?{OBJECT}\b", re.I),
        "positive_any": re.compile(r"\beast(?:ward|wards)?\b", re.I),
        "negative_any": re.compile(r"\bwest(?:ward|wards)?\b", re.I),
        "labels": ("EAST", "WEST"),
    },
    "vertical": {
        "positive": re.compile(rf"\babove (?:the )?{OBJECT}\b", re.I),
        "negative": re.compile(rf"\b(?:below|under) (?:the )?{OBJECT}\b", re.I),
        "positive_any": re.compile(r"\babove\b", re.I),
        "negative_any": re.compile(r"\b(?:below|under)\b", re.I),
        "labels": ("ABOVE", "BELOW"),
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise ValueError(f"page has no physical-folio prefix: {page!r}")
    return match.group(1)


def classify(axis: str, comment: str) -> str | None:
    rules = PATTERNS[axis]
    positive = bool(rules["positive"].search(comment))
    negative = bool(rules["negative"].search(comment))
    mixed = bool(rules["positive_any"].search(comment)) and bool(
        rules["negative_any"].search(comment)
    )
    if mixed or positive == negative:
        return None
    return rules["labels"][0 if positive else 1]


def natural_key(value: str) -> tuple[object, ...]:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def audit_axis(
    axis: str,
    eligible: list[dict[str, str]],
    coverage: dict[str, set[str]],
) -> tuple[dict[str, object], list[dict[str, str]]]:
    classified = []
    for row in eligible:
        direction = classify(axis, row["local_comment"])
        if direction is not None:
            classified.append((row, direction))

    covered = [
        (row, direction)
        for row, direction in classified
        if coverage[row["source_locus"]] == READINGS
    ]
    groups: dict[tuple[str, str, str], list[tuple[dict[str, str], str]]] = defaultdict(list)
    for row, direction in covered:
        groups[(row["page"], row["normalized_code"], row["object_tags"])].append(
            (row, direction)
        )
    matched = {
        key: rows
        for key, rows in groups.items()
        if len({direction for _, direction in rows}) == 2
    }

    panel = []
    for (page, code, tags), rows in matched.items():
        stratum = "|".join((page, code, tags))
        for row, direction in rows:
            panel.append(
                {
                    "physical_folio": physical_folio(page),
                    "page": page,
                    "stratum_id": stratum,
                    "class": direction,
                    "source_locus": row["source_locus"],
                    "normalized_code": code,
                    "object_tags": tags,
                    "readings": ";".join(sorted(READINGS)),
                }
            )
    panel.sort(key=lambda row: natural_key(row["source_locus"]))

    folio_counts = Counter(row["physical_folio"] for row in panel)
    class_counts = Counter(row["class"] for row in panel)
    context_families = {
        (row["normalized_code"], row["object_tags"]) for row in panel
    }
    folios = len(folio_counts)
    max_share = max(folio_counts.values(), default=0) / max(len(panel), 1)
    gates = {
        "at_least_six_physical_folios": folios >= 6,
        "leave_one_folio_retains_five": max(folios - 1, 0) >= 5,
        "at_least_three_code_object_contexts": len(context_families) >= 3,
        "maximum_folio_share_at_most_0_45": max_share <= 0.45,
        "all_rows_have_exactly_three_manual_readings": all(
            coverage[row["source_locus"]] == READINGS for row in panel
        ),
        "all_strata_same_page_code_object_and_both_classes": all(
            len({direction for _, direction in rows}) == 2 for rows in matched.values()
        ),
    }
    summary = {
        "eligible_source_rows": len(eligible),
        "explicit_exclusive_classified_rows": len(classified),
        "fully_covered_classified_rows": len(covered),
        "classified_rows_without_full_three_reading_coverage": sorted(
            row["source_locus"]
            for row, _ in classified
            if coverage[row["source_locus"]] != READINGS
        ),
        "matched_strata": len(matched),
        "matched_rows": len(panel),
        "physical_folios": folios,
        "context_families": len(context_families),
        "class_counts": dict(sorted(class_counts.items())),
        "folio_counts": dict(sorted(folio_counts.items(), key=lambda item: natural_key(item[0]))),
        "maximum_folio_share": max_share,
        "matched_stratum_counts": {
            "|".join(key): dict(sorted(Counter(direction for _, direction in rows).items()))
            for key, rows in sorted(matched.items(), key=lambda item: natural_key(item[0][0]))
        },
        "gates": gates,
        "admitted": all(gates.values()),
    }
    return summary, panel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-panel", type=Path, default=DEFAULT_PANEL)
    args = parser.parse_args()

    annotation_path = ROOT / ANNOTATIONS
    interlinear_path = ROOT / INTERLINEAR
    with annotation_path.open(newline="", encoding="utf-8") as handle:
        annotations = list(csv.DictReader(handle, delimiter="\t"))
    coverage: dict[str, set[str]] = defaultdict(set)
    with interlinear_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            # Deliberately read no text-bearing column.
            coverage[row["locus"]].add(row["edition"])

    eligible = [
        row
        for row in annotations
        if row["certainty"] == "UNHEDGED"
        and row["relation_scope"] == "EXACT_LOCAL_COMMENT"
    ]
    horizontal, horizontal_panel = audit_axis("horizontal", eligible, coverage)
    vertical, _ = audit_axis("vertical", eligible, coverage)

    assert len(annotations) == 1192
    assert len(eligible) == 398
    assert horizontal["explicit_exclusive_classified_rows"] == 108
    assert horizontal["fully_covered_classified_rows"] == 104
    assert horizontal["matched_strata"] == 8
    assert horizontal["matched_rows"] == 57
    assert horizontal["physical_folios"] == 6
    assert horizontal["class_counts"] == {"EAST": 39, "WEST": 18}
    assert horizontal["admitted"] is True
    assert vertical["explicit_exclusive_classified_rows"] == 60
    assert vertical["fully_covered_classified_rows"] == 58
    assert vertical["matched_strata"] == 5
    assert vertical["matched_rows"] == 18
    assert vertical["physical_folios"] == 4
    assert vertical["admitted"] is False

    result = {
        "status": "PASS_HORIZONTAL_CAPACITY_STOP_VERTICAL_CAPACITY",
        "source_only": True,
        "voynich_string_features_opened": False,
        "inputs": {
            str(ANNOTATIONS): sha256(annotation_path),
            str(INTERLINEAR): sha256(interlinear_path),
        },
        "selection_contract": {
            "certainty": "UNHEDGED",
            "relation_scope": "EXACT_LOCAL_COMMENT",
            "classification_field": "local_comment",
            "mixed_direction_rows_excluded": True,
            "coverage": sorted(READINGS),
            "stratum": ["exact page/panel", "exact normalized_code", "exact object_tags"],
            "independence_cluster": "physical folio",
        },
        "horizontal": horizontal,
        "vertical": vertical,
        "decision": {
            "admitted_axis": "horizontal",
            "stopped_axis": "vertical",
            "authorization": "target-blind prescore design only",
            "claim_ceiling": (
                "capacity for a formal placement-association test; no ownership, "
                "direction word, lexeme, plaintext, language, or translation"
            ),
        },
    }

    output_json = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    output_panel = args.output_panel if args.output_panel.is_absolute() else ROOT / args.output_panel
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_panel.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = [
        "physical_folio", "page", "stratum_id", "class", "source_locus",
        "normalized_code", "object_tags", "readings",
    ]
    with output_panel.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(horizontal_panel)


if __name__ == "__main__":
    main()
