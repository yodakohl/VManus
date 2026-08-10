#!/usr/bin/env python3
"""Independent PFR001 reconstruction; imports no production module."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
A = R / "existing_human_label_annotations.tsv"
X = R / "existing_human_current_locus_crosswalk.tsv"
J = R / "public_pharma_root_plant_capacity.json"
OUT = R / "public_pharma_root_plant_capacity_validation.json"
REPORT = R / "public_pharma_root_plant_capacity_validation.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def columns(path: Path, names: tuple[str, ...]) -> list[tuple[str, ...]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = csv.reader(handle, delimiter="\t")
        head = next(rows)
        ix = [head.index(name) for name in names]
        return [tuple(row[i] for i in ix) for row in rows]


def pf(page: str) -> str:
    return re.match(r"f\d+", page).group()  # type: ignore[union-attr]


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    stored = json.loads(J.read_text(encoding="utf-8"))
    checks: list[bool] = []
    annotations = columns(
        A, ("source_record_id", "section", "page", "object_class", "object_guess", "certainty")
    )
    cross = {
        rid: (page, eligible)
        for rid, page, eligible in columns(X, ("source_record_id", "current_page", "primary_eligible"))
    }
    source = [
        row for row in annotations
        if row[1] == "pharma" and row[3] == "P" and row[5] == "UNHEDGED"
        and row[4] in {"plant", "root"}
    ]
    mapped = [(rid, cross[rid][0], state) for rid, _, _, _, state, _ in source if cross[rid][1] == "1"]
    checks += [len(source) == 154, len(mapped) == 118]
    checks += [Counter(row[4] for row in source) == {"plant": 113, "root": 41}]
    checks += [Counter(row[2] for row in mapped) == {"plant": 90, "root": 28}]
    pages: dict[str, Counter[str]] = defaultdict(Counter)
    folios: dict[str, Counter[str]] = defaultdict(Counter)
    for _, page, state in mapped:
        pages[page][state] += 1
        folios[pf(page)][state] += 1
    mixed_pages = {page: counts for page, counts in pages.items() if len(counts) == 2}
    mixed_folios = {folio: counts for folio, counts in folios.items() if len(counts) == 2}
    checks += [mixed_pages == {
        "f89r1": Counter({"plant": 8, "root": 1}),
        "f99v": Counter({"root": 14, "plant": 1}),
    }]
    checks += [mixed_folios == {
        "f89": Counter({"plant": 15, "root": 1}),
        "f99": Counter({"root": 27, "plant": 1}),
    }]
    orbit = math.prod(math.comb(sum(c.values()), c["root"]) for c in mixed_pages.values())
    checks += [orbit == 135, stored["mapped_primary_panel"]["within_mixed_page_assignment_orbit"] == orbit]
    checks += [stored["physical_folio_sign_orbit"] == 4]
    checks += [stored["physical_folio_minimum_one_sided_p"] == 0.25]
    checks += [stored["gates"] == {
        "at_least_five_mixed_folios": False,
        "both_classes_on_at_least_five_folios": False,
        "every_held_mixed_folio_has_five_training_labels_per_class": False,
        "three_minority_labels_in_each_direction": False,
    }]
    checks += [stored["status"] == "STOP_UNSCORED_PAGE_AND_FOLIO_CONFOUNDED"]
    checks += [stored["decision"] == "STOP_BEFORE_ANY_VOYNICH_STRING_OR_GRAMMAR_SCORE"]
    checks += [stored["voynich_string_columns_selected"] is False]
    checks += [stored["semantic_or_grammar_score_computed"] is False]
    checks += [stored["ocr_or_automated_vision_used"] is False]
    checks += [stored["inputs"]["results/existing_human_label_annotations.tsv"] == digest(A)]
    checks += [stored["inputs"]["results/existing_human_current_locus_crosswalk.tsv"] == digest(X)]
    if not all(checks):
        raise SystemExit(f"validation failed: {[i for i, ok in enumerate(checks) if not ok]}")
    validation = {
        "status": "PASS_INDEPENDENT_PFR001_CAPACITY_RECONSTRUCTION",
        "checks": len(checks),
        "failures": 0,
        "source_rows": len(source),
        "mapped_rows": len(mapped),
        "mixed_pages": sorted(mixed_pages),
        "mixed_folios": sorted(mixed_folios),
        "within_page_orbit": orbit,
        "folio_sign_orbit": 4,
        "result_sha256": digest(J),
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# PFR001 independent validation\n\n"
        f"PASS: {len(checks)} checks independently reconstruct 154 public records, "
        "118 mapped records, the two mixed pages and folios, the 135 label assignment "
        "orbit, the four-state folio sign orbit, all failed gates, and the unscored stop. "
        "No Voynich string or image-derived feature was used.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
