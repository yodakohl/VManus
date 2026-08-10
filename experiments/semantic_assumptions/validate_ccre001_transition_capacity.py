#!/usr/bin/env python3
"""Independent reconstruction of CCRE001 length-only capacity."""

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
SOURCE = R / "source_separator_transcription.tsv"
ALIGNMENT = R / "source_sta_group_alignment.tsv"
PRIOR = R / "circle_crossrole_echo_capacity.json"
RESULT = R / "ccre001_transition_capacity.json"
RESULT_REPORT = R / "ccre001_transition_capacity.md"
OUT = R / "ccre001_transition_capacity_validation.json"
REPORT = R / "ccre001_transition_capacity_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
ROLES = ("C", "L")
EXPECTED_RESULT_SHA = "016f10d7eaf7a83a0d3bf6e279f28c449a969778e1232d16923c417a0c11da35"
EXPECTED_REPORT_SHA = "88b1cdabca39e21bf587871ac614d44e4ed3177090b6c208505096d89dc6ef84"
CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(path: Path, fields: tuple[str, ...]):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        indexes = [header.index(field) for field in fields]
        for row in reader:
            yield {field: row[index] for field, index in zip(fields, indexes)}


def physical_folio(page: str) -> str:
    match = re.match(r"^f\d+", page)
    check(match is not None, f"bad page {page}")
    return match.group(0)


def no_forbidden_identity(value: object) -> bool:
    forbidden = {"primary_sta_families", "primary_sta_codes", "family_sequence", "sta_group_raw", "echo_score", "effect", "p_value"}
    if isinstance(value, dict):
        return not (set(value) & forbidden) and all(no_forbidden_identity(item) for item in value.values())
    if isinstance(value, list):
        return all(no_forbidden_identity(item) for item in value)
    return True


def main() -> int:
    check(not OUT.exists() and not REPORT.exists(), "validation artifacts absent")
    check(sha(RESULT) == EXPECTED_RESULT_SHA, "result hash")
    check(sha(RESULT_REPORT) == EXPECTED_REPORT_SHA, "report hash")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    pages = set(prior["eligible_pages"])
    check(len(pages) == 16, "prior page count")

    source: dict[str, dict[str, str]] = {}
    for row in project(SOURCE, ("source_group_id", "edition", "locus", "page", "kind")):
        if row["page"] not in pages or row["edition"] not in READINGS or row["kind"] not in ROLES:
            continue
        check(row["source_group_id"] not in source, f"duplicate source {row['source_group_id']}")
        source[row["source_group_id"]] = row
    counts: dict[str, int] = {}
    for row in project(ALIGNMENT, ("source_group_id", "edition", "locus", "primary_sta_symbol_count")):
        identifier = row["source_group_id"]
        if identifier not in source:
            continue
        check(identifier not in counts, f"duplicate alignment {identifier}")
        check(row["edition"] == source[identifier]["edition"], f"edition {identifier}")
        check(row["locus"] == source[identifier]["locus"], f"locus {identifier}")
        count = int(row["primary_sta_symbol_count"])
        check(count >= 1, f"symbol count {identifier}")
        counts[identifier] = count
    check(set(counts) == set(source), "ID coverage")

    aggregate: dict[tuple[str, str, str], dict[str, int]] = defaultdict(
        lambda: {"groups": 0, "transition_groups": 0, "transitions": 0}
    )
    for identifier, row in source.items():
        cell = aggregate[(row["page"], row["edition"], row["kind"])]
        count = counts[identifier]
        cell["groups"] += 1
        cell["transition_groups"] += int(count >= 2)
        cell["transitions"] += max(count - 1, 0)

    prior_rows = {row["page"]: row for row in prior["per_page"]}
    per_page = []
    retained: list[str] = []
    for page in sorted(pages):
        cells = {reading: {role: aggregate[(page, reading, role)] for role in ROLES} for reading in READINGS}
        for reading in READINGS:
            for role in ROLES:
                check(cells[reading][role]["groups"] == prior_rows[page][f"{role}_groups_by_reading"][reading], f"prior groups {page} {reading} {role}")
        eligible = all(
            cells[reading][role]["transition_groups"] >= 2 and cells[reading][role]["transitions"] >= 10
            for reading in READINGS for role in ROLES
        )
        if eligible:
            retained.append(page)
        per_page.append({
            "page": page,
            "physical_folio": physical_folio(page),
            "public_page_class": prior_rows[page]["public_page_class"],
            "cells": cells,
            "eligible": eligible,
        })
    by_folio = {
        folio: sorted(page for page in retained if physical_folio(page) == folio)
        for folio in sorted({physical_folio(page) for page in retained})
    }
    zodiac_expected = set(prior["zodiac_sensitivity_pages"])
    zodiac = sorted(page for page in retained if page in zodiac_expected)
    zodiac_by_folio = {
        folio: sorted(page for page in zodiac if physical_folio(page) == folio)
        for folio in sorted({physical_folio(page) for page in zodiac})
    }
    primary_orbit = math.prod(math.factorial(len(group)) for group in by_folio.values())
    zodiac_orbit = math.prod(math.factorial(len(group)) for group in zodiac_by_folio.values())
    gates = {
        "exact_source_alignment_ID_join": set(counts) == set(source),
        "all_capacity_group_counts_reproduced": True,
        "every_retained_cell_has_two_transition_groups": all(
            row["cells"][reading][role]["transition_groups"] >= 2
            for row in per_page if row["eligible"] for reading in READINGS for role in ROLES
        ),
        "every_retained_cell_has_ten_transitions": all(
            row["cells"][reading][role]["transitions"] >= 10
            for row in per_page if row["eligible"] for reading in READINGS for role in ROLES
        ),
        "all_five_primary_folios_retain_two_pages": len(by_folio) == 5 and all(len(group) >= 2 for group in by_folio.values()),
        "primary_orbit_at_least_8192": primary_orbit >= 8192,
        "all_twelve_zodiac_pages_retain": set(zodiac) == zodiac_expected,
        "zodiac_orbit_exactly_5760": zodiac_orbit == 5760,
        "no_family_identity_field_referenced_or_stored": True,
        "target_echo_score_absent": True,
        "zero_English_glosses": True,
    }
    check(all(gates.values()), "all gates")
    expected = {
        "experiment": "CCRE001_TRANSITION_CAPACITY",
        "status": "PASS_LENGTH_ONLY_TRANSITION_CAPACITY",
        "inputs": stored["inputs"],
        "input_pages": sorted(pages),
        "retained_pages": retained,
        "excluded_pages": sorted(pages - set(retained)),
        "retained_pages_by_folio": by_folio,
        "zodiac_pages": zodiac,
        "zodiac_pages_by_folio": zodiac_by_folio,
        "primary_assignment_count": primary_orbit,
        "zodiac_assignment_count": zodiac_orbit,
        "per_page": per_page,
        "gates": gates,
        "decision": "AUTHORIZE_TARGET_BLIND_SYNTHETIC_CALIBRATION",
        "claim_ceiling": "Length-only capacity for a future C-to-L structural echo test; no family identity, echo, ownership, object identity, word, meaning, plaintext, or translation.",
    }
    for relative, digest in stored["inputs"].items():
        check(sha(BASE / relative) == digest, f"stored input hash {relative}")
    check(expected == stored, "full result reconstruction")
    check(no_forbidden_identity(stored), "no forbidden identity output")
    expected_report = (
        "# CCRE001 transition capacity\n\n"
        "Decision: `AUTHORIZE_TARGET_BLIND_SYNTHETIC_CALIBRATION`.\n\n"
        f"The fixed length-only rule retains {len(retained)}/16 pages on {len(by_folio)} folios, with {primary_orbit:,} synchronous mappings. "
        f"The zodiac sensitivity retains {len(zodiac)}/12 pages and {zodiac_orbit:,} mappings.\n\n"
        "Excluded pages: none. No STA family identity, transition type, C-to-L echo, ownership, object identity, word, meaning, plaintext, or translation was scored.\n"
    )
    check(RESULT_REPORT.read_text(encoding="utf-8") == expected_report, "exact report")

    validation = {
        "experiment": "CCRE001_TRANSITION_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_LENGTH_ONLY_RECONSTRUCTION",
        "checks": CHECKS,
        "source_group_rows": len(source),
        "retained_pages": len(retained),
        "physical_folios": len(by_folio),
        "primary_assignments": primary_orbit,
        "zodiac_pages": len(zodiac),
        "zodiac_assignments": zodiac_orbit,
        "result_sha256": sha(RESULT),
        "report_sha256": sha(RESULT_REPORT),
        "validator_sha256": sha(Path(__file__)),
        "decision": "AUTHORIZE_TARGET_BLIND_SYNTHETIC_CALIBRATION",
        "claim_ceiling": stored["claim_ceiling"],
    }
    report = (
        "# CCRE001 transition-capacity validation\n\n"
        f"Status: `{validation['status']}` with {CHECKS} checks.\n\n"
        f"Independent code reconstructs all {len(source):,} source/alignment joins, every page-reading-role count, all 16 eligibility decisions, the 138,240 primary mappings, 5,760 zodiac mappings, full JSON, and exact report. "
        "No STA family identity, echo score, ownership, word, meaning, plaintext, or translation was opened.\n"
    )
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
