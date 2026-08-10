#!/usr/bin/env python3
"""Independent reconstruction of circle C-to-L echo capacity."""

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
ATLAS = R / "public_circle_block_role_atlas.tsv"
SOURCE = R / "source_separator_transcription.tsv"
PRODUCTION = R / "circle_crossrole_echo_capacity.json"
PRODUCTION_REPORT = R / "circle_crossrole_echo_capacity.md"
OUT = R / "circle_crossrole_echo_capacity_validation.json"
REPORT = R / "circle_crossrole_echo_capacity_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
SCOPE = re.compile(r"^f(?:67|68|69|70|71|72|73)")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = 0

    def check(value: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(name)

    atlas_rows = rows(ATLAS)
    page_class = {row["page"]: row["public_page_class"] for row in atlas_rows}
    atlas_pages = sorted(page_class)
    check(len(atlas_pages) == 26, "public page count")
    raw_counts: Counter[tuple[str, str, str]] = Counter()
    raw_groups: Counter[tuple[str, str, str]] = Counter()
    seen_loci: set[tuple[str, str]] = set()
    for row in rows(SOURCE):
        if not SCOPE.match(row["page"]) or row["kind"] not in {"P", "L", "C", "R"}:
            continue
        key = (row["page"], row["edition"], row["kind"])
        raw_groups[key] += 1
        locus_key = (row["edition"], row["locus"])
        if locus_key not in seen_loci:
            raw_counts[key] += 1
            seen_loci.add(locus_key)
    for row in atlas_rows:
        key = (row["page"], row["reading"], row["ivtff_role"])
        check(raw_counts[key] == int(row["locus_count"]), f"locus count {key}")
        check(raw_groups[key] == int(row["source_group_count"]), f"group count {key}")

    both = sorted(page for page in atlas_pages if all(
        raw_counts[(page, reading, "C")] > 0 and raw_counts[(page, reading, "L")] > 0
        for reading in READINGS
    ))
    by_folio: dict[str, list[str]] = defaultdict(list)
    for page in both:
        by_folio[re.match(r"^f\d+", page).group(0)].append(page)
    excluded = sorted(page for values in by_folio.values() if len(values) == 1 for page in values)
    eligible = sorted(page for values in by_folio.values() if len(values) >= 2 for page in values)
    eligible_by_folio = {
        folio: sorted(page for page in eligible if re.match(r"^f\d+", page).group(0) == folio)
        for folio in sorted({re.match(r"^f\d+", page).group(0) for page in eligible})
    }
    zodiac = sorted(page for page in eligible if page_class[page] == "ZODIAC")
    zodiac_by_folio = {
        folio: sorted(page for page in zodiac if re.match(r"^f\d+", page).group(0) == folio)
        for folio in sorted({re.match(r"^f\d+", page).group(0) for page in zodiac})
    }
    orbit = math.prod(math.factorial(len(values)) for values in eligible_by_folio.values())
    zodiac_orbit = math.prod(math.factorial(len(values)) for values in zodiac_by_folio.values())
    stored = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    check(stored["status"] == "PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL", "status")
    check(stored["all_C_and_L_pages"] == both, "all both-role pages")
    check(stored["excluded_same_folio_singletons"] == excluded == ["f69r"], "singleton")
    check(stored["eligible_pages"] == eligible and len(eligible) == 16, "eligible pages")
    check(stored["eligible_pages_by_folio"] == eligible_by_folio and len(eligible_by_folio) == 5, "primary folios")
    check(stored["zodiac_sensitivity_pages"] == zodiac and len(zodiac) == 12, "zodiac pages")
    check(stored["zodiac_pages_by_folio"] == zodiac_by_folio and len(zodiac_by_folio) == 4, "zodiac folios")
    check(stored["primary_synchronous_assignment_count"] == orbit == 138_240, "primary orbit")
    check(stored["zodiac_synchronous_assignment_count"] == zodiac_orbit == 5_760, "zodiac orbit")
    totals = {
        role: {
            reading: sum(raw_groups[(page, reading, role)] for page in eligible)
            for reading in READINGS
        }
        for role in ("C", "L")
    }
    check(stored["primary_role_group_totals"] == totals, "group totals")
    for row in stored["per_page"]:
        page = row["page"]
        folio = re.match(r"^f\d+", page).group(0)
        check(row["physical_folio"] == folio, f"folio {page}")
        check(row["public_page_class"] == page_class[page], f"class {page}")
        for role in ("C", "L"):
            check(row[f"{role}_loci_by_reading"] == {
                reading: raw_counts[(page, reading, role)] for reading in READINGS
            }, f"{role} loci {page}")
            check(row[f"{role}_groups_by_reading"] == {
                reading: raw_groups[(page, reading, role)] for reading in READINGS
            }, f"{role} groups {page}")
        check(row["same_folio_alternative_C_pages"] == len(eligible_by_folio[folio]) - 1, f"alternatives {page}")
    check(all(stored["gates"].values()), "production gates")
    check(stored["decision"] == "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CONTROLS_ONLY", "decision")
    check(stored["inputs"]["public_circle_block_role_atlas.tsv"] == sha(ATLAS), "atlas hash")
    check(stored["inputs"]["audit_circle_crossrole_echo_capacity.py"] == sha(BASE / "audit_circle_crossrole_echo_capacity.py"), "producer hash")

    validation = {
        "experiment": "CIRCLE_CROSSROLE_ECHO_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_16_PAGE_5_FOLIO_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "bindings": {
            "source_separator_transcription_sha256": sha(SOURCE),
            "role_atlas_sha256": sha(ATLAS),
            "producer_result_sha256": sha(PRODUCTION),
            "producer_report_sha256": sha(PRODUCTION_REPORT),
            "validator_sha256": sha(Path(__file__)),
        },
        "reconstructed": {
            "public_pages": len(atlas_pages),
            "both_role_pages": len(both),
            "eligible_pages": len(eligible),
            "primary_folios": len(eligible_by_folio),
            "primary_assignments": orbit,
            "zodiac_pages": len(zodiac),
            "zodiac_folios": len(zodiac_by_folio),
            "zodiac_assignments": zodiac_orbit,
        },
        "decision": "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CONTROLS_ONLY",
        "claim_ceiling": stored["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle C-to-L cross-role echo capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_16_PAGE_5_FOLIO_CAPACITY_RECONSTRUCTION**\n\n"
        f"Independent raw source-group counting passed {checks} checks and reconstructed the exact "
        "16-page/five-folio primary panel, f69r singleton exclusion, 138,240 synchronous "
        "within-folio mappings, and 12-page/four-folio 5,760-mapping zodiac sensitivity. "
        "No STA identity or cross-role echo score was opened. This authorizes preregistration and "
        "target-blind controls only; it supplies no ownership, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
