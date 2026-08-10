#!/usr/bin/env python3
"""Score-blind capacity for page-specific L-to-C construction echoes."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
ATLAS = R / "public_circle_block_role_atlas.tsv"
ATLAS_JSON = R / "public_circle_block_role_atlas.json"
ATLAS_VALIDATION = R / "public_circle_block_role_atlas_validation.json"
OUT = R / "circle_crossrole_echo_capacity.json"
REPORT = R / "circle_crossrole_echo_capacity.md"
READINGS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    atlas_status = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    atlas_validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    if atlas_status["status"] != "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS":
        raise AssertionError("role atlas status drift")
    if atlas_validation["status"] != "PASS":
        raise AssertionError("role atlas validation drift")

    table = rows(ATLAS)
    keyed = {(row["page"], row["reading"], row["ivtff_role"]): row for row in table}
    if len(keyed) != len(table):
        raise AssertionError("duplicate role-atlas row")
    pages = sorted({row["page"] for row in table})
    page_meta = {
        page: {
            "physical_folio": next(row["physical_folio"] for row in table if row["page"] == page),
            "public_page_class": next(row["public_page_class"] for row in table if row["page"] == page),
        }
        for page in pages
    }
    both = []
    for page in pages:
        if all(
            int(keyed[(page, reading, "C")]["locus_count"]) > 0
            and int(keyed[(page, reading, "L")]["locus_count"]) > 0
            for reading in READINGS
        ):
            both.append(page)
    by_folio: dict[str, list[str]] = defaultdict(list)
    for page in both:
        by_folio[page_meta[page]["physical_folio"]].append(page)
    excluded_singletons = sorted(page for folio, values in by_folio.items() if len(values) == 1 for page in values)
    eligible = sorted(page for folio, values in by_folio.items() if len(values) >= 2 for page in values)
    eligible_by_folio = {
        folio: sorted(page for page in eligible if page_meta[page]["physical_folio"] == folio)
        for folio in sorted({page_meta[page]["physical_folio"] for page in eligible})
    }
    zodiac = sorted(page for page in eligible if page_meta[page]["public_page_class"] == "ZODIAC")
    zodiac_by_folio = {
        folio: sorted(page for page in zodiac if page_meta[page]["physical_folio"] == folio)
        for folio in sorted({page_meta[page]["physical_folio"] for page in zodiac})
    }
    complete_orbit = math.prod(math.factorial(len(values)) for values in eligible_by_folio.values())
    zodiac_orbit = math.prod(math.factorial(len(values)) for values in zodiac_by_folio.values())

    def role_totals(selected: list[str], role: str) -> dict[str, int]:
        return {
            reading: sum(int(keyed[(page, reading, role)]["source_group_count"]) for page in selected)
            for reading in READINGS
        }

    per_page = []
    for page in eligible:
        per_page.append({
            "page": page,
            **page_meta[page],
            "C_loci_by_reading": {
                reading: int(keyed[(page, reading, "C")]["locus_count"]) for reading in READINGS
            },
            "L_loci_by_reading": {
                reading: int(keyed[(page, reading, "L")]["locus_count"]) for reading in READINGS
            },
            "C_groups_by_reading": {
                reading: int(keyed[(page, reading, "C")]["source_group_count"]) for reading in READINGS
            },
            "L_groups_by_reading": {
                reading: int(keyed[(page, reading, "L")]["source_group_count"]) for reading in READINGS
            },
            "same_folio_alternative_C_pages": len(eligible_by_folio[page_meta[page]["physical_folio"]]) - 1,
        })
    gates = {
        "all_26_public_circle_pages_accounted": len(pages) == 26,
        "exact_17_pages_have_C_and_L_in_all_readings": len(both) == 17,
        "singleton_f69r_excluded_before_text_access": excluded_singletons == ["f69r"],
        "exact_16_primary_pages": len(eligible) == 16,
        "primary_spans_5_physical_folios": len(eligible_by_folio) == 5,
        "every_primary_page_has_a_same_folio_alternative_C_page": all(
            row["same_folio_alternative_C_pages"] >= 1 for row in per_page
        ),
        "exact_primary_orbit_138240": complete_orbit == 138_240,
        "exact_12_page_4_folio_zodiac_sensitivity": len(zodiac) == 12 and len(zodiac_by_folio) == 4,
        "exact_zodiac_orbit_5760": zodiac_orbit == 5_760,
        "all_three_readings_have_positive_C_and_L_group_capacity": all(
            value > 0 for role in ("C", "L") for value in role_totals(eligible, role).values()
        ),
        "no_STA_identity_or_echo_score_opened": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)
    result = {
        "experiment": "CIRCLE_CROSSROLE_ECHO_CAPACITY",
        "status": "PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL",
        "inputs": {path.name: sha(path) for path in (ATLAS, ATLAS_JSON, ATLAS_VALIDATION, Path(__file__))},
        "all_C_and_L_pages": both,
        "excluded_same_folio_singletons": excluded_singletons,
        "eligible_pages": eligible,
        "eligible_pages_by_folio": eligible_by_folio,
        "zodiac_sensitivity_pages": zodiac,
        "zodiac_pages_by_folio": zodiac_by_folio,
        "primary_synchronous_assignment_count": complete_orbit,
        "zodiac_synchronous_assignment_count": zodiac_orbit,
        "primary_role_group_totals": {
            role: role_totals(eligible, role) for role in ("C", "L")
        },
        "per_page": per_page,
        "gates": gates,
        "decision": "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CONTROLS_ONLY",
        "claim_ceiling": (
            "There is capacity for a within-folio page-specific test of whether L-role label groups "
            "reuse short source-native constructions present in C-role circular text. Capacity does "
            "not establish ownership, label meaning, object identity, wordhood, plaintext, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle C-to-L cross-role echo capacity\n\n"
        "Status: **PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL**\n\n"
        "Seventeen public f67--f73 panels contain both IVTFF circular (`C`) and label (`L`) "
        "material in every manual reading. The sole same-folio singleton, f69r, is excluded "
        "before any source-native text feature is opened. The primary panel therefore has 16 "
        "pages across five physical folios; every page has at least one different same-folio C "
        "bag available as a control. Synchronous within-folio reassignment gives exactly 138,240 "
        "complete mappings. The mandatory zodiac-only sensitivity retains 12 pages on four folios "
        "and 5,760 mappings.\n\n"
        "This is a new same-page cross-role construction question, not the closed duplicate-sign "
        "cross-page profile test. No STA identity or overlap was inspected here. Capacity supplies "
        "no ownership, object, label meaning, wordhood, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "pages": len(eligible), "orbit": complete_orbit}, sort_keys=True))


if __name__ == "__main__":
    main()
