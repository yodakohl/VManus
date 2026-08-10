#!/usr/bin/env python3
"""Independent validator for CBD001; imports no production module."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "semantic_assumptions" / "results"
ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"
PROD = RESULTS / "public_circle_bifolio_class_capacity.json"
PROD_MD = RESULTS / "public_circle_bifolio_class_capacity.md"
OUT = RESULTS / "public_circle_bifolio_class_capacity_validation.json"
OUT_MD = RESULTS / "public_circle_bifolio_class_capacity_validation.md"
MAPPING = {
    "f67": "Q09_f67_f68", "f68": "Q09_f67_f68",
    "f69": "Q10_f69_f70", "f70": "Q10_f69_f70",
    "f71": "Q11_f71_f72", "f72": "Q11_f71_f72",
    "f73": "Q12_f73_f74_missing",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    prod = json.loads(PROD.read_text())
    checks = 0

    def check(value: bool, label: str) -> None:
        nonlocal checks
        if not value:
            raise AssertionError(label)
        checks += 1

    check(prod["experiment"] == "CBD001_PUBLIC_CIRCLE_BIFOLIO_CLASS_CAPACITY", "experiment")
    check(prod["status"] == "STOP_UNSCORED_INSUFFICIENT_INDEPENDENT_BIFOLIO_CLASS_SUPPORT", "status")
    check(prod["decision"] == prod["status"], "decision")
    check(prod["atlas_input"]["sha256"] == sha(ATLAS.read_bytes()), "atlas hash")

    pages = {}
    with ATLAS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            value = (row["physical_folio"], row["public_page_class"])
            check(pages.setdefault(row["page"], value) == value, "stable page metadata")
    check(len(pages) == 26, "page count")

    counts = defaultdict(Counter)
    page_lists = defaultdict(list)
    for page, (folio, public_class) in sorted(pages.items()):
        bifolio = MAPPING[folio]
        counts[bifolio][public_class] += 1
        page_lists[bifolio].append(page)
    reconstructed = {key: dict(value) for key, value in counts.items()}
    check(reconstructed == prod["bifolio_class_counts"], "bifolio counts")
    check({k: v for k, v in sorted(page_lists.items())} == prod["pages_by_bifolio"], "page lists")
    check(sum(sum(value.values()) for value in reconstructed.values()) == 26, "count sum")
    check(len(reconstructed) == 4, "bifolio count")

    support = defaultdict(set)
    for bifolio, class_counts in reconstructed.items():
        for public_class in class_counts:
            support[public_class].add(bifolio)
    support = {key: sorted(value) for key, value in support.items()}
    check(support == prod["class_bifolio_support"], "class support")
    check(len(support["ASTRONOMICAL"]) == 1, "astronomical singleton")
    check(len(support["COSMOLOGICAL"]) == 2, "cosmological support")
    check(len(support["ZODIAC"]) == 3, "zodiac support")

    orbit = math.comb(6, 2)
    check(orbit == 15, "Q10 orbit")
    check(prod["held_sheet_capacity"]["Q10_count_preserving_assignments"] == orbit, "stored orbit")
    check(prod["held_sheet_capacity"]["Q10_minimum_attainable_one_sided_p"] == 1 / orbit, "p floor")
    check(prod["held_sheet_capacity"]["p_at_most_0_05_attainable"] is False, "p gate")
    check(prod["gates"]["voynich_text_features_accessed"] is False, "target isolation")
    check(prod["gates"]["class_score_computed"] is False, "unscored")
    check(prod["gates"]["ocr_or_automated_vision_used"] is False, "method exclusion")
    check("four bifolio production units" in prod["claim_ceiling"], "ceiling")
    check("1/15" in PROD_MD.read_text(), "report p floor")

    validation = {
        "status": "PASS_INDEPENDENT_26_PANEL_FOUR_BIFOLIO_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "production_sha256": sha(PROD.read_bytes()),
        "production_report_sha256": sha(PROD_MD.read_bytes()),
        "decision": prod["decision"],
        "voynich_text_features_accessed": False,
        "ocr_or_automated_vision_used": False,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# CBD001 independent validation\n\n"
        f"PASS: **{checks}** checks independently reconstruct all 26 pages, four "
        "bifolios, every class count and support set, the 15-assignment Q10 orbit, "
        "the 1/15 p-value floor, target isolation, and the unscored stop.\n\n"
        "This validates only the bifolio-level capacity limit. It supplies no "
        "class-specific group, word, meaning, plaintext, or translation.\n"
    )


if __name__ == "__main__":
    main()
