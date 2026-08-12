#!/usr/bin/env python3
"""Build the source-bound inline prose/figure-cardinality worth screen."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
OBS = BASE / "inline_prose_figure_cardinality_worth_screen_observations.tsv"
RESULT = BASE / "results/inline_prose_figure_cardinality_worth_screen.json"
REPORT = BASE / "results/inline_prose_figure_cardinality_worth_screen_report.md"

NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def number(value: str) -> int:
    return int(value) if value.isdigit() else NUMBERS[value.lower()]


def select_candidates() -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    token = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    word_re = re.compile(rf"\b({token})\s+words?\b", re.I)
    figure_re = re.compile(rf"\b({token})\s+(?:nymphs?|figures?)\b", re.I)
    range_re = re.compile(rf"\b(?:between\s+)?({token})\s+(?:and|[-–])\s+({token})\s+words?\b", re.I)
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            comment = row["local_comment"]
            if "REL_ARRAY_OR_GROUP" not in row["local_relation_tags"]:
                continue
            words = word_re.findall(comment)
            figures = figure_re.findall(comment)
            if len(words) != 1 or len(figures) != 1 or range_re.search(comment):
                continue
            if number(words[0]) != number(figures[0]):
                continue
            selected.append({
                "locus": row["locus"],
                "certainty": row["certainty"],
                "count": str(number(words[0])),
                "comment": comment,
            })
    return selected


def build() -> tuple[dict[str, object], str]:
    selected = select_candidates()
    if [(r["locus"], r["certainty"], r["count"]) for r in selected] != [
        ("f81r.1", "UNHEDGED", "7"),
        ("f84r.27", "HEDGED", "10"),
    ]:
        raise SystemExit("mechanical candidate panel changed")
    with OBS.open(newline="", encoding="utf-8") as handle:
        observations = list(csv.DictReader(handle, delimiter="\t"))
    if [r["locus"] for r in observations] != ["f81r.1", "f84r.27"]:
        raise SystemExit("observation order changed")
    for row, source in zip(observations, selected, strict=True):
        if row["human_certainty"] != source["certainty"]:
            raise SystemExit("certainty mismatch")
        if row["group_count"] != source["count"] or row["figure_count"] != source["count"]:
            raise SystemExit("count mismatch")
        if any(row[key] != "NO" for key in (
            "explicit_cells_or_enclosures", "explicit_leaders_or_connectors",
            "explicit_dividers", "complete_nonoverlapping_one_to_one_layout",
            "singular_ordered_ownership",
        )):
            raise SystemExit("ownership gate changed")
        if row["continuous_multiline_prose"] != "YES" or len(row["official_sha256"]) != 64:
            raise SystemExit("source-bound observation malformed")

    counts = {
        "mechanically_selected_lines": 2,
        "physical_folios": 2,
        "exact_cardinality_matches": 2,
        "unhedged_human_comments": 1,
        "hedged_human_comments": 1,
        "continuous_multiline_prose_lines": 2,
        "lines_with_explicit_cells_leaders_or_dividers": 0,
        "singularly_owned_ordered_arrays": 0,
        "filler_associations_opened": 0,
        "translation_anchors": 0,
    }
    result: dict[str, object] = {
        "experiment": "INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN",
        "schema": "INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN_V1",
        "status": "STOP_TWO_CARDINALITY_MATCHES_NO_SINGULAR_ORDERED_OWNERSHIP",
        "decision": "CLOSE_INLINE_PROSE_AS_INDIVIDUAL_FIGURE_LABEL_ARRAY",
        "counts": counts,
        "candidates": [
            {
                "locus": row["locus"],
                "count": int(row["group_count"]),
                "human_certainty": row["human_certainty"],
                "official_canvas_id": row["official_canvas_id"],
                "official_sha256": row["official_sha256"],
                "singular_ordered_ownership": False,
                "observation": row["observation"],
            }
            for row in observations
        ],
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(ANNOTATIONS.relative_to(ROOT)): sha(ANNOTATIONS),
            str(OBS.relative_to(ROOT)): sha(OBS),
        },
        "claim_ceiling": (
            "Two physical folios have human-reported equality between a prose-line group count and an adjacent figure "
            "count, but neither supplies an author-visible one-to-one ownership device. The equality does not establish "
            "that any group is a figure label, name, ordinal, role, word, sound, language, cipher, plaintext, meaning, "
            "or translation."
        ),
    }
    report = (
        "# Inline prose / figure-cardinality worth screen\n\n"
        "Status: **STOP — TWO COUNT MATCHES, ZERO SINGULARLY OWNED ARRAYS**.\n\n"
        "The existing human annotation layer mechanically selects two exact count correspondences: seven groups under "
        "seven figures at f81r.1 and ten groups under ten figures at f84r.27. Source-bound inspection of the exact official "
        "canvases confirms the aggregate layouts but not an individual mapping. Both candidate lines continue into "
        "multiline prose, and neither has cells, leaders, dividers, or non-overlapping one-group/one-figure compartments.\n\n"
        "No filler association or text-feature score was opened. The count correspondences may reflect deliberate page "
        "composition, but they do not establish labels, names, ordinals, roles, words, sounds, language, cipher, plaintext, "
        "meaning, or translation.\n"
    )
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        RESULT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
