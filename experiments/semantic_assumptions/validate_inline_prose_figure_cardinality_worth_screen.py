#!/usr/bin/env python3
"""Independent reconstruction of the inline prose/figure-cardinality stop."""

from __future__ import annotations

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
OUT_JSON = BASE / "results/inline_prose_figure_cardinality_worth_screen_validation.json"
OUT_MD = BASE / "results/inline_prose_figure_cardinality_worth_screen_validation_report.md"

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def as_number(text: str) -> int:
    return int(text) if text.isdigit() else WORDS[text.lower()]


def main() -> None:
    checks: list[str] = []
    token = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    wr = re.compile(rf"\b({token})\s+words?\b", re.I)
    fr = re.compile(rf"\b({token})\s+(?:nymphs?|figures?)\b", re.I)
    rr = re.compile(rf"\b(?:between\s+)?({token})\s+(?:and|[-–])\s+({token})\s+words?\b", re.I)
    selected: list[tuple[str, str, int]] = []
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            comment = row["local_comment"]
            w, f = wr.findall(comment), fr.findall(comment)
            if ("REL_ARRAY_OR_GROUP" in row["local_relation_tags"] and len(w) == 1 and len(f) == 1
                    and not rr.search(comment) and as_number(w[0]) == as_number(f[0])):
                selected.append((row["locus"], row["certainty"], as_number(w[0])))
    assert selected == [("f81r.1", "UNHEDGED", 7), ("f84r.27", "HEDGED", 10)]
    checks.append("mechanical_candidate_selection")

    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [(r["locus"], int(r["group_count"]), int(r["figure_count"])) for r in rows] == [
        ("f81r.1", 7, 7), ("f84r.27", 10, 10)]
    checks.append("exact_two_folio_count_panel")
    assert [r["official_canvas_id"] for r in rows] == ["1006220", "1006226"]
    assert [r["official_sha256"] for r in rows] == [
        "e5e83f606eb9c3089051035f53ea694bcb1dadb5a93ee0064019c903ec6802fe",
        "7e8fa7c29b6c6ab462ad5359bdabfcd60505622700f6e5cb18478d20cbd79fbe",
    ]
    checks.append("exact_official_image_bindings")
    assert all(r["continuous_multiline_prose"] == "YES" for r in rows)
    assert all(r[k] == "NO" for r in rows for k in (
        "explicit_cells_or_enclosures", "explicit_leaders_or_connectors", "explicit_dividers",
        "complete_nonoverlapping_one_to_one_layout", "singular_ordered_ownership"))
    checks.append("registered_ownership_gate")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "continuous_multiline_prose_lines": 2,
        "exact_cardinality_matches": 2,
        "filler_associations_opened": 0,
        "hedged_human_comments": 1,
        "lines_with_explicit_cells_leaders_or_dividers": 0,
        "mechanically_selected_lines": 2,
        "physical_folios": 2,
        "singularly_owned_ordered_arrays": 0,
        "translation_anchors": 0,
        "unhedged_human_comments": 1,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/inline_prose_figure_cardinality_worth_screen_observations.tsv": sha(OBS),
        "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": sha(ANNOTATIONS),
    }
    checks.append("input_bindings_reconstructed")
    assert result["status"] == "STOP_TWO_CARDINALITY_MATCHES_NO_SINGULAR_ORDERED_OWNERSHIP"
    assert result["decision"] == "CLOSE_INLINE_PROSE_AS_INDIVIDUAL_FIGURE_LABEL_ARRAY"
    assert "does not establish" in result["claim_ceiling"]
    checks.append("status_decision_ceiling")
    expected_report = (
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
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")

    assert len(checks) == 8
    validation = {
        "experiment": "INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN_VALIDATION",
        "schema": "INLINE_PROSE_FIGURE_CARDINALITY_WORTH_SCREEN_VALIDATION_V1",
        "status": "PASS_8_CHECK_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the source-bound ownership stop and supplies no translation.",
    }
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Inline prose / figure-cardinality validation\n\n"
        "Status: **PASS — 8 independent reconstruction checks**.\n\n"
        "Independent code reconstructs the two mechanically selected human count correspondences, exact official image "
        "bindings, frozen ownership judgments, aggregate counts, input hashes, stop decision, and report bytes. It does "
        "not reinterpret the machine visual judgments and supplies no figure label, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
