#!/usr/bin/env python3
"""Source-only capacity screen for labels on upper versus lower container parts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PHARMA_CONTAINER_ZONE_CAPACITY_METHOD.md"
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
RESULT = BASE / "results/pharma_container_zone_capacity.json"
REPORT = BASE / "results/pharma_container_zone_capacity_report.md"
ALLOWED_FIELDS = {
    "page", "locus", "unit", "normalized_code", "local_comment", "certainty"
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise RuntimeError(("nonnumeric page", page))
    return match.group(0)


TOP_STEMS = (
    "On top lid.",
    "On container, top (bigger) part.",
)
BOTTOM_PATTERNS = (
    re.compile(r"^On body of container, bottom \(wider\) section\."),
    re.compile(r"^On container, bottom half\."),
    re.compile(r"^On container, bottom \((?:wider|widest|smaller)\) (?:section|part)(?:, line [123])?\."),
    re.compile(r"^Label on container, bottom \(wider\) part\."),
    re.compile(r"^On container, bottom bulge\."),
)


def classify(comment: str) -> str | None:
    if comment.startswith(TOP_STEMS):
        return "TOP_PHYSICAL_PART"
    if any(pattern.match(comment) for pattern in BOTTOM_PATTERNS):
        return "BOTTOM_PHYSICAL_PART"
    return None


def build() -> tuple[dict[str, object], str]:
    rows: list[dict[str, str]] = []
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not ALLOWED_FIELDS.issubset(reader.fieldnames or []):
            raise RuntimeError("annotation schema")
        for source_row in reader:
            if source_row["certainty"] != "UNHEDGED":
                continue
            if not source_row["normalized_code"].endswith("Lc"):
                continue
            label_class = classify(source_row["local_comment"])
            if label_class is None:
                continue
            rows.append({
                "page": source_row["page"],
                "folio": folio(source_row["page"]),
                "locus": source_row["locus"],
                "unit": source_row["unit"],
                "class": label_class,
            })

    unit_states = sorted({(row["page"], row["folio"], row["unit"], row["class"]) for row in rows})
    classes_by_page: dict[str, Counter[str]] = defaultdict(Counter)
    classes_by_unit: dict[tuple[str, str], set[str]] = defaultdict(set)
    folios_by_class: dict[str, set[str]] = defaultdict(set)
    for page, physical_folio, unit, label_class in unit_states:
        classes_by_page[page][label_class] += 1
        classes_by_unit[(page, unit)].add(label_class)
        folios_by_class[label_class].add(physical_folio)

    mixed_pages = sorted(page for page, counts in classes_by_page.items() if set(counts) == {
        "TOP_PHYSICAL_PART", "BOTTOM_PHYSICAL_PART"
    })
    mixed_folios = sorted({folio(page) for page in mixed_pages})
    mixed_units = sorted(f"{page}|{unit}" for (page, unit), states in classes_by_unit.items() if len(states) == 2)
    balanced = sum(min(classes_by_page[page].values()) for page in mixed_pages)
    minimum_sign_p = 1 / (2 ** len(mixed_folios))

    gates = {
        "both_states_on_at_least_5_physical_folios": min(len(folios_by_class["TOP_PHYSICAL_PART"]), len(folios_by_class["BOTTOM_PHYSICAL_PART"])) >= 5,
        "at_least_5_mixed_pages": len(mixed_pages) >= 5,
        "at_least_3_mixed_individual_container_units": len(mixed_units) >= 3,
        "at_least_20_balanced_page_opportunities": balanced >= 20,
    }
    status = "PASS_SOURCE_CAPACITY" if all(gates.values()) else "STOP_TWO_FOLIOS_TWO_MIXED_PAGES_ONE_MIXED_CONTAINER"
    result: dict[str, object] = {
        "experiment": "PHARMA_CONTAINER_ZONE_CAPACITY",
        "schema": "PHARMA_CONTAINER_ZONE_CAPACITY_V1",
        "status": status,
        "decision": "DO_NOT_OPEN_TOP_VERSUS_BOTTOM_CONTAINER_LABEL_IDENTITIES",
        "source_access": {
            "allowed_fields": sorted(ALLOWED_FIELDS),
            "voynich_transcription_accessed": False,
            "family_surface_accessed": False,
            "member_code_accessed": False,
            "root_or_role_accessed": False,
            "alternate_readings_treated_as_replicates": False,
        },
        "counts": {
            "selected_source_rows": len(rows),
            "top_source_rows": sum(row["class"] == "TOP_PHYSICAL_PART" for row in rows),
            "bottom_source_rows": sum(row["class"] == "BOTTOM_PHYSICAL_PART" for row in rows),
            "physical_unit_state_observations": len(unit_states),
            "top_unit_state_observations": sum(item[3] == "TOP_PHYSICAL_PART" for item in unit_states),
            "bottom_unit_state_observations": sum(item[3] == "BOTTOM_PHYSICAL_PART" for item in unit_states),
            "top_physical_folios": len(folios_by_class["TOP_PHYSICAL_PART"]),
            "bottom_physical_folios": len(folios_by_class["BOTTOM_PHYSICAL_PART"]),
            "mixed_pages": len(mixed_pages),
            "mixed_physical_folios": len(mixed_folios),
            "mixed_individual_container_units": len(mixed_units),
            "balanced_page_opportunities": balanced,
            "minimum_one_sided_mixed_folio_sign_p": minimum_sign_p,
        },
        "folios_by_class": {key: sorted(values) for key, values in sorted(folios_by_class.items())},
        "mixed_pages": mixed_pages,
        "mixed_folios": mixed_folios,
        "mixed_individual_container_units": mixed_units,
        "gates": gates,
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
        },
        "claim_ceiling": (
            "The current human annotation layer has too little independent upper-part support for a transferable "
            "container-zone marker test. No top, bottom, lid, container, part, word, sound, language, cipher, "
            "plaintext, meaning, or translation follows."
        ),
    }
    report = (
        "# Pharmaceutical container-zone capacity\n\n"
        "Status: **STOP — TWO FOLIOS, TWO MIXED PAGES, ONE MIXED CONTAINER**.\n\n"
        "The conservative source-only rule finds 15 directly annotated label rows: two on an upper physical "
        "container part and 13 on a lower part. Collapsing the three numbered lines on one lower container part "
        "leaves 13 physical unit-state observations (2 TOP, 11 BOTTOM). TOP occurs only on f99 and f102. Only "
        "f99r and f102v2 contain both states, and only f102v2.C1 places separate TOP and BOTTOM inscriptions on "
        "the same individual container. There are two balanced page opportunities, and the best two-folio "
        "one-sided sign orbit has minimum p=1/4=.25.\n\n"
        "All four worth gates fail. No Voynich transcription, family, member, root, role, or formal feature was "
        "opened. This does not establish a lid/top/bottom/container word, plaintext, meaning, or translation.\n"
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
