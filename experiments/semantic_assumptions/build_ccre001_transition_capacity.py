#!/usr/bin/env python3
"""Length-only capacity for the C-to-L cross-role echo test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
SPEC = BASE / "CCRE001_TRANSITION_CAPACITY_SPEC.md"
CAPACITY = R / "circle_crossrole_echo_capacity.json"
CAPACITY_VALIDATION = R / "circle_crossrole_echo_capacity_validation.json"
SOURCE = R / "source_separator_transcription.tsv"
ALIGNMENT = R / "source_sta_group_alignment.tsv"
OUT = R / "ccre001_transition_capacity.json"
REPORT = R / "ccre001_transition_capacity.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
ROLES = ("C", "L")
EXPECTED = {
    CAPACITY: "26b13101979a8423bea02e6e976b24cc662820a1ecf971b13812cf281bbed5fa",
    CAPACITY_VALIDATION: "3b03f957ed8dcb92508ad73ff35e978816c4d304d0e949cf037686d2551bcacf",
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    ALIGNMENT: "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projected_rows(path: Path, fields: tuple[str, ...]):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        indexes = [header.index(field) for field in fields]
        for values in reader:
            yield {field: values[index] for field, index in zip(fields, indexes)}


def folio(page: str) -> str:
    match = re.match(r"^f\d+", page)
    if not match:
        raise RuntimeError(f"bad page {page}")
    return match.group(0)


def main() -> int:
    if OUT.exists() or REPORT.exists():
        raise RuntimeError("capacity artifact already exists")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise RuntimeError(f"input hash mismatch: {path.name}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL":
        raise RuntimeError("capacity status drift")
    if validation["status"] != "PASS_INDEPENDENT_16_PAGE_5_FOLIO_CAPACITY_RECONSTRUCTION":
        raise RuntimeError("capacity validation drift")
    pages = set(capacity["eligible_pages"])

    source: dict[str, dict[str, str]] = {}
    fields = ("source_group_id", "edition", "locus", "page", "kind")
    for row in projected_rows(SOURCE, fields):
        if row["page"] not in pages or row["edition"] not in READINGS or row["kind"] not in ROLES:
            continue
        identifier = row["source_group_id"]
        if identifier in source:
            raise RuntimeError(f"duplicate source group {identifier}")
        source[identifier] = row

    symbol_counts: dict[str, int] = {}
    alignment_fields = ("source_group_id", "edition", "locus", "primary_sta_symbol_count")
    for row in projected_rows(ALIGNMENT, alignment_fields):
        identifier = row["source_group_id"]
        if identifier not in source:
            continue
        if identifier in symbol_counts:
            raise RuntimeError(f"duplicate alignment group {identifier}")
        if row["edition"] != source[identifier]["edition"] or row["locus"] != source[identifier]["locus"]:
            raise RuntimeError(f"source/alignment mismatch {identifier}")
        count = int(row["primary_sta_symbol_count"])
        if count < 1:
            raise RuntimeError(f"invalid symbol count {identifier}")
        symbol_counts[identifier] = count
    if set(symbol_counts) != set(source):
        raise RuntimeError("source/alignment ID mismatch")

    aggregates: dict[tuple[str, str, str], dict[str, int]] = defaultdict(
        lambda: {"groups": 0, "transition_groups": 0, "transitions": 0}
    )
    for identifier, row in source.items():
        key = (row["page"], row["edition"], row["kind"])
        count = symbol_counts[identifier]
        aggregates[key]["groups"] += 1
        aggregates[key]["transition_groups"] += int(count >= 2)
        aggregates[key]["transitions"] += max(count - 1, 0)

    capacity_rows = {row["page"]: row for row in capacity["per_page"]}
    per_page = []
    retained = []
    for page in sorted(pages):
        cells = {
            reading: {role: aggregates[(page, reading, role)] for role in ROLES}
            for reading in READINGS
        }
        for reading in READINGS:
            for role in ROLES:
                if cells[reading][role]["groups"] != capacity_rows[page][f"{role}_groups_by_reading"][reading]:
                    raise RuntimeError(f"capacity group-count drift {page} {reading} {role}")
        eligible = all(
            cells[reading][role]["transition_groups"] >= 2
            and cells[reading][role]["transitions"] >= 10
            for reading in READINGS
            for role in ROLES
        )
        if eligible:
            retained.append(page)
        per_page.append(
            {
                "page": page,
                "physical_folio": folio(page),
                "public_page_class": capacity_rows[page]["public_page_class"],
                "cells": cells,
                "eligible": eligible,
            }
        )

    retained_by_folio = {
        physical: sorted(page for page in retained if folio(page) == physical)
        for physical in sorted({folio(page) for page in retained})
    }
    zodiac_expected = set(capacity["zodiac_sensitivity_pages"])
    zodiac = sorted(page for page in retained if page in zodiac_expected)
    zodiac_by_folio = {
        physical: sorted(page for page in zodiac if folio(page) == physical)
        for physical in sorted({folio(page) for page in zodiac})
    }
    primary_orbit = math.prod(math.factorial(len(group)) for group in retained_by_folio.values())
    zodiac_orbit = math.prod(math.factorial(len(group)) for group in zodiac_by_folio.values())
    gates = {
        "exact_source_alignment_ID_join": set(symbol_counts) == set(source),
        "all_capacity_group_counts_reproduced": True,
        "every_retained_cell_has_two_transition_groups": all(
            row["cells"][reading][role]["transition_groups"] >= 2
            for row in per_page if row["eligible"] for reading in READINGS for role in ROLES
        ),
        "every_retained_cell_has_ten_transitions": all(
            row["cells"][reading][role]["transitions"] >= 10
            for row in per_page if row["eligible"] for reading in READINGS for role in ROLES
        ),
        "all_five_primary_folios_retain_two_pages": len(retained_by_folio) == 5 and all(len(group) >= 2 for group in retained_by_folio.values()),
        "primary_orbit_at_least_8192": primary_orbit >= 8192,
        "all_twelve_zodiac_pages_retain": set(zodiac) == zodiac_expected,
        "zodiac_orbit_exactly_5760": zodiac_orbit == 5760,
        "no_family_identity_field_referenced_or_stored": True,
        "target_echo_score_absent": True,
        "zero_English_glosses": True,
    }
    passed = all(gates.values())
    decision = "AUTHORIZE_TARGET_BLIND_SYNTHETIC_CALIBRATION" if passed else "STOP_UNSCORED_TRANSITION_CAPACITY"
    result = {
        "experiment": "CCRE001_TRANSITION_CAPACITY",
        "status": "PASS_LENGTH_ONLY_TRANSITION_CAPACITY" if passed else "STOP_LENGTH_ONLY_TRANSITION_CAPACITY",
        "inputs": {str(path.relative_to(BASE)): sha(path) for path in EXPECTED} | {
            SPEC.name: sha(SPEC),
            Path(__file__).name: sha(Path(__file__)),
        },
        "input_pages": sorted(pages),
        "retained_pages": retained,
        "excluded_pages": sorted(pages - set(retained)),
        "retained_pages_by_folio": retained_by_folio,
        "zodiac_pages": zodiac,
        "zodiac_pages_by_folio": zodiac_by_folio,
        "primary_assignment_count": primary_orbit,
        "zodiac_assignment_count": zodiac_orbit,
        "per_page": per_page,
        "gates": gates,
        "decision": decision,
        "claim_ceiling": "Length-only capacity for a future C-to-L structural echo test; no family identity, echo, ownership, object identity, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# CCRE001 transition capacity\n\n"
        f"Decision: `{decision}`.\n\n"
        f"The fixed length-only rule retains {len(retained)}/16 pages on {len(retained_by_folio)} folios, with {primary_orbit:,} synchronous mappings. "
        f"The zodiac sensitivity retains {len(zodiac)}/12 pages and {zodiac_orbit:,} mappings.\n\n"
        f"Excluded pages: {', '.join(sorted(pages - set(retained))) if pages - set(retained) else 'none'}. "
        "No STA family identity, transition type, C-to-L echo, ownership, object identity, word, meaning, plaintext, or translation was scored.\n",
        encoding="utf-8",
    )
    print(json.dumps({"decision": decision, "retained_pages": len(retained), "primary_orbit": primary_orbit, "zodiac_orbit": zodiac_orbit}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
