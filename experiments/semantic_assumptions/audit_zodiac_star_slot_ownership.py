#!/usr/bin/env python3
"""Audit why public zodiac aggregate counts cannot select a label owner."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
ROLE_ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"
ROLE_ATLAS_JSON = RESULTS / "public_circle_block_role_atlas.json"
ROLE_ATLAS_VALIDATION = RESULTS / "public_circle_block_role_atlas_validation.json"
STOLFI = BASE / "cache" / "existing_human_annotations" / "labtit-best.idx"
OUT_TSV = RESULTS / "zodiac_star_slot_ownership.tsv"
OUT_JSON = RESULTS / "zodiac_star_slot_ownership.json"
REPORT = RESULTS / "zodiac_star_slot_ownership_report.md"

PAGES = (
    "f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2",
    "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v",
)
READINGS = ("ZL3b", "IT2a", "RF1b")
SIGN_RE = re.compile(
    r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b",
    re.I,
)
FIGURE_RE = re.compile(r"\bThere are (\d+)(?: figures)? in total\b", re.I)
LABEL_RE = re.compile(r"\b(\d+) zodiac labels\b", re.I)
NEAR_FIGURE_RE = re.compile(r"\b(\d+) of the zodiac labels are near the small human figures\b", re.I)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def star_holding_figure_count(illustrations: str, figures: int) -> int:
    low = illustrations.lower()
    if "with one exception" in low and "all holding a star" in low:
        return figures - 1
    if "each one is holding a star" in low or "they are all holding a star" in low:
        return figures
    raise AssertionError("unparsed star-bearing figure statement")


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")

    atlas_json = json.loads(ROLE_ATLAS_JSON.read_text(encoding="utf-8"))
    atlas_validation = json.loads(ROLE_ATLAS_VALIDATION.read_text(encoding="utf-8"))
    assert atlas_json["status"] == "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS"
    assert atlas_validation["status"] == "PASS"

    public = {row["page"]: row for row in rows(PUBLIC)}
    assert all(page in public for page in PAGES)
    role_rows = rows(ROLE_ATLAS)
    l_counts = {
        (row["page"], row["reading"]): int(row["locus_count"])
        for row in role_rows
        if row["page"] in PAGES and row["ivtff_role"] == "L"
    }
    assert set(l_counts) == {(page, reading) for page in PAGES for reading in READINGS}

    stolfi_rows = []
    for line in STOLFI.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("|")
        assert len(fields) == 11
        stolfi_rows.append(fields)
    zodiac_unlabelled = [
        fields for fields in stolfi_rows
        if fields[1] == "zodiac" and "not labeled" in fields[10].lower()
    ]
    assert zodiac_unlabelled == [[
        "0606", "zodiac", "f72r2", "S", "23", "V", "-", "-", "Z", "day?",
        "gemini, outer, #14, dressed, male? Not labeled",
    ]]

    output = []
    for page in PAGES:
        source = public[page]
        sign_match = SIGN_RE.search(source["illustrations"])
        figure_match = FIGURE_RE.search(source["illustrations"])
        label_match = LABEL_RE.search(source["text_description"])
        assert sign_match and figure_match and label_match
        figures = int(figure_match.group(1))
        star_figures = star_holding_figure_count(source["illustrations"], figures)
        labels = int(label_match.group(1))
        explicit_nonfigure_star_labels = 0
        if "The 30th is near one of the central stars" in source["text_description"]:
            explicit_nonfigure_star_labels = 1
        near_match = NEAR_FIGURE_RE.search(source["text_description"])
        explicit_near_figure_labels = int(near_match.group(1)) if near_match else ""
        assert {l_counts[(page, reading)] for reading in READINGS} == {labels}
        distinct_f72_exceptions = int(
            page == "f72r2"
            and "in one case (outer ring, bottom right) the star is missing" in source["other_information"].lower()
            and "in another case (outer ring, left) only the label is missing" in source["other_information"].lower()
        )
        output.append({
            "page": page,
            "physical_folio": re.match(r"f\d+", page).group(0),
            "public_sign": sign_match.group(1).upper(),
            "public_figure_count": figures,
            "public_star_holding_figure_count": star_figures,
            "public_label_count": labels,
            "explicit_near_figure_label_count": explicit_near_figure_labels,
            "explicit_nonfigure_star_label_count": explicit_nonfigure_star_labels,
            "figure_count_residual_labels_minus_figures": labels - figures,
            "aggregate_star_count_residual_labels_minus_star_holding_figures_and_nonfigure_label": labels - star_figures - explicit_nonfigure_star_labels,
            "all_reading_ivtff_L_count": labels,
            "f72r2_distinct_star_missing_and_label_missing_slots": distinct_f72_exceptions,
            "f72r2_implied_labelled_nonstar_figure": distinct_f72_exceptions,
            "f72r2_implied_unlabelled_star_holding_figure": distinct_f72_exceptions,
        })

    figure_matches = sum(row["figure_count_residual_labels_minus_figures"] == 0 for row in output)
    aggregate_star_matches = sum(row["aggregate_star_count_residual_labels_minus_star_holding_figures_and_nonfigure_label"] == 0 for row in output)
    exception_rows = [row for row in output if row["figure_count_residual_labels_minus_figures"] != 0]
    assert figure_matches == 10
    assert aggregate_star_matches == 12
    assert [(row["page"], row["figure_count_residual_labels_minus_figures"]) for row in exception_rows] == [
        ("f70v2", 1), ("f72r2", -1),
    ]
    assert len({row["physical_folio"] for row in exception_rows}) == 2
    assert sum(row["f72r2_distinct_star_missing_and_label_missing_slots"] for row in output) == 1
    assert sum(row["f72r2_implied_labelled_nonstar_figure"] for row in output) == 1
    assert sum(row["f72r2_implied_unlabelled_star_holding_figure"] for row in output) == 1
    assert sum(row["explicit_nonfigure_star_label_count"] for row in output) == 1

    fieldnames = list(output[0])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    gates = {
        "all_12_public_zodiac_pages_present": len(output) == 12,
        "all_36_ivtff_L_counts_equal_public_label_counts": all(
            l_counts[(row["page"], reading)] == row["public_label_count"]
            for row in output for reading in READINGS
        ),
        "figure_count_model_has_two_opposite_exceptions": figure_matches == 10 and [
            row["figure_count_residual_labels_minus_figures"] for row in exception_rows
        ] == [1, -1],
        "aggregate_star_count_identity_holds_but_is_not_an_ownership_test": aggregate_star_matches == 12,
        "f70v2_has_explicit_label_near_nonfigure_central_star": next(
            row for row in output if row["page"] == "f70v2"
        )["explicit_nonfigure_star_label_count"] == 1,
        "f72r2_public_source_says_star_and_label_are_missing_at_different_slots": next(
            row for row in output if row["page"] == "f72r2"
        )["f72r2_distinct_star_missing_and_label_missing_slots"] == 1,
        "f72r2_contains_a_labelled_nonstar_figure": next(
            row for row in output if row["page"] == "f72r2"
        )["f72r2_implied_labelled_nonstar_figure"] == 1,
        "f72r2_contains_an_unlabelled_star_holding_figure": next(
            row for row in output if row["page"] == "f72r2"
        )["f72r2_implied_unlabelled_star_holding_figure"] == 1,
        "two_exception_pages_are_different_physical_folios": len({row["physical_folio"] for row in exception_rows}) == 2,
        "zero_lexical_glosses": True,
    }
    assert all(gates.values())
    result = {
        "experiment": "ZODIAC_STAR_SLOT_OWNERSHIP_AUDIT",
        "status": "CORRECTED_INVALIDATED_AGGREGATE_COUNT_OWNERSHIP_CONFOUND",
        "inputs": {path.name: sha(path) for path in (PUBLIC, ROLE_ATLAS, ROLE_ATLAS_JSON, ROLE_ATLAS_VALIDATION, STOLFI)},
        "counts": {
            "pages": len(output),
            "physical_folios": len({row["physical_folio"] for row in output}),
            "reading_specific_L_count_cells": 36,
            "figure_model_matching_pages": figure_matches,
            "aggregate_star_count_matching_pages": aggregate_star_matches,
            "opposite_exception_pages": 2,
            "f72r2_distinct_exception_slots": 2,
        },
        "opposite_exceptions": exception_rows,
        "gates": gates,
        "output_tsv_sha256": sha(OUT_TSV),
        "decision": "RETAIN_COMPOSITE_30_SLOT_INVENTORY_NO_EXCLUSIVE_STAR_OR_FIGURE_OWNER",
        "claim_ceiling": "The public zodiac L inventory belongs to a repeated nymph-star-label slot system, but aggregate counts cannot select stars or figures as the exclusive owner. f72r2 has a labelled figure without a star and a different star-bearing figure without a label. No Voynich word, meaning, plaintext, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public zodiac aggregate-ownership correction\n\n"
        "Status: **CORRECTED_INVALIDATED_AGGREGATE_COUNT_OWNERSHIP_CONFOUND**\n\n"
        "Across all twelve public zodiac panels, the manual IVTFF `L` count equals the public catalogue's label count in all 36 page-reading cells. A simple figure-count model matches 10/12 pages. f70v2 has 29 figures but 30 labels, with the 30th explicitly beside a central star; f72r2 has 30 figures, 29 stars, and 29 labels.\n\n"
        "The stronger public f72r2 note invalidates the initial ownership inference: the star is missing at one figure, while only the label is missing at a different figure. Therefore f72r2 contains both a labelled figure without a star and a star-holding figure without a label. The numerical 29=29 identity is an aggregate coincidence, not one-to-one star ownership. Retain only a repeated composite nymph-star-label slot inventory, with one missing label among the expected 300. STAR, FIGURE, DAY, DEGREE, PERSON, and every lexical translation remain unestablished.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "figure_matches": figure_matches, "aggregate_star_count_matches": aggregate_star_matches}, sort_keys=True))


if __name__ == "__main__":
    main()
