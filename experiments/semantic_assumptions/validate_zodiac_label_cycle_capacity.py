#!/usr/bin/env python3
"""Clean-room reconstruction of the ZLA001 public ordinal capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
SOURCE = BASE / "cache/existing_human_annotations/labtit-best.idx"
CROSSWALK = R / "existing_human_current_locus_crosswalk.tsv"
PRODUCTION = R / "zodiac_label_cycle_capacity.json"
PANEL = R / "zodiac_label_cycle_capacity.tsv"
REPORT = R / "zodiac_label_cycle_capacity.md"
OUT = R / "zodiac_label_cycle_capacity_validation.json"
OUT_MD = R / "zodiac_label_cycle_capacity_validation.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"f(\d+)[rv]\d*", page)
    if match is None:
        raise AssertionError(page)
    return f"f{int(match.group(1))}"


def load_source() -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        fields = line.split("|")
        if len(fields) != 11 or fields[1] != "zodiac":
            continue
        comments = fields[10].lower()
        scope = "OUTSIDE" if "not in circle" in comments else next(
            (name.upper() for name in ("central", "inner", "middle", "outer") if name in comments),
            "UNKNOWN",
        )
        match = re.search(r"#\s*(\d+)", fields[10])
        record_id = f"STOLFI_BEST_{fields[0]}"
        if record_id in output:
            raise AssertionError("duplicate source ID")
        output[record_id] = {
            "page": fields[2],
            "scope": scope,
            "ordinal": int(match.group(1)) if match else None,
        }
    return output


def load_crosswalk() -> dict[str, dict[str, str]]:
    with CROSSWALK.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    output = {row["source_record_id"]: row for row in rows}
    if len(output) != len(rows):
        raise AssertionError("duplicate crosswalk ID")
    return output


def rejection_reasons(records: list[tuple[dict[str, object], dict[str, str]]]) -> list[str]:
    reasons = []
    ordinals = [source["ordinal"] for source, _ in records]
    if any(value is None for value in ordinals):
        reasons.append("NONEXPLICIT_OR_MISSING_GROVE_ORDINAL")
    elif sorted(int(value) for value in ordinals) != list(range(1, len(records) + 1)):
        reasons.append("NONCONTIGUOUS_GROVE_ORDINALS")
    if any(row["matching_method"] != "HUMAN_GROVE_SCOPE_NUMBER" for _, row in records):
        reasons.append("NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS")
    if any(row["primary_eligible"] != "1" or not row["current_locus"] for _, row in records):
        reasons.append("MISSING_OR_NONPRIMARY_CURRENT_LOCUS")
    if any(row["all_three_present"] != "1" for _, row in records):
        reasons.append("NOT_ALL_THREE_MANUAL_READINGS_PRESENT")
    if len({row["current_locus"] for _, row in records if row["current_locus"]}) != len(records):
        reasons.append("CURRENT_LOCUS_NOT_ONE_TO_ONE")
    return reasons


def main() -> None:
    for path in (OUT, OUT_MD):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    stored = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    source = load_source()
    crosswalk = load_crosswalk()
    checks = 0

    def check(value: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(label)

    check(len(source) == 300, "source count")
    check(len({row["page"] for row in source.values()}) == 12, "page count")
    check(set(source) <= set(crosswalk), "crosswalk coverage")
    check(source["STOLFI_BEST_0606"] == {"page": "f72r2", "scope": "OUTER", "ordinal": 14}, "missing-label source")
    check(not crosswalk["STOLFI_BEST_0606"]["current_locus"], "missing-label crosswalk")

    grouped: dict[tuple[str, str], list[tuple[dict[str, object], dict[str, str]]]] = defaultdict(list)
    nonring = Counter()
    for record_id, src in source.items():
        if src["scope"] not in {"INNER", "MIDDLE", "OUTER"}:
            nonring[str(src["scope"])] += 1
            continue
        grouped[(str(src["page"]), str(src["scope"]))].append((src, crosswalk[record_id]))
    check(len(grouped) == 25, "ring count")
    check(sum(len(rows) for rows in grouped.values()) == 286, "ring slot count")
    check(nonring == Counter({"OUTSIDE": 13, "CENTRAL": 1}), "nonring counts")

    expected_rows = []
    expected_kept = []
    expected_dropped = []
    for (page, scope), records in sorted(grouped.items()):
        ring_id = f"{page}:{scope}"
        reasons = rejection_reasons(records)
        if reasons:
            expected_dropped.append({"ring_id": ring_id, "slots": len(records), "reasons": reasons})
            continue
        ordered = sorted(records, key=lambda item: int(item[0]["ordinal"]))
        expected_kept.append({"ring_id": ring_id, "page": page, "scope": scope, "slots": len(records)})
        for src, row in ordered:
            expected_rows.append({
                "ring_id": ring_id,
                "page": page,
                "physical_folio": physical_folio(page),
                "ring_scope": scope,
                "grove_ordinal": str(src["ordinal"]),
                "source_record_id": row["source_record_id"],
                "current_locus": row["current_locus"],
                "current_code": row["current_code"],
                "current_kind": row["current_kind"],
                "matching_method": row["matching_method"],
                "match_status": row["match_status"],
            })

    with PANEL.open(encoding="utf-8", newline="") as handle:
        actual_rows = list(csv.DictReader(handle, delimiter="\t"))
    check(actual_rows == expected_rows, "exact panel rows")
    checks += len(expected_rows)
    check(len(expected_kept) == 21, "kept rings")
    check(len(expected_rows) == 235, "kept slots")
    check(len({row["page"] for row in expected_rows}) == 11, "kept pages")
    check(len({row["physical_folio"] for row in expected_rows}) == 4, "kept folios")
    check(len({row["current_locus"] for row in expected_rows}) == 235, "unique loci")
    check(all(row["matching_method"] == "HUMAN_GROVE_SCOPE_NUMBER" for row in expected_rows), "human positions")
    check(expected_dropped == stored["dropped_rings"], "dropped rings")
    check(expected_kept == stored["eligible_rings"], "kept ring manifest")
    check(sha(PANEL) == stored["panel_sha256"], "panel hash")

    expected_counts = {
        "public_zodiac_records": 300,
        "public_zodiac_pages": 12,
        "candidate_rings": 25,
        "candidate_ring_slots": 286,
        "eligible_rings": 21,
        "eligible_slots": 235,
        "eligible_pages": 11,
        "eligible_physical_folios": 4,
        "dropped_rings": 4,
        "nonring_records": {"CENTRAL": 1, "OUTSIDE": 13},
    }
    check(stored["counts"] == expected_counts, "stored counts")
    check(stored["status"] == "PASS_TEXT_BLIND_21_RING_235_SLOT_PUBLIC_ORDINAL_PANEL", "status")
    check(stored["decision"] == "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CONTROLS_ONLY", "decision")
    check(all(stored["gates"].values()), "gates")
    check("no adjacency effect" in stored["claim_ceiling"], "claim ceiling")
    check(sha(REPORT) == hashlib.sha256(REPORT.read_bytes()).hexdigest(), "report readable/hashable")

    # Adversarial eligibility controls, applied without touching text identities.
    good = list(grouped[("f73r", "INNER")])
    bad = [(dict(src), dict(row)) for src, row in good]
    bad[1][0]["ordinal"] = bad[0][0]["ordinal"]
    check("NONCONTIGUOUS_GROVE_ORDINALS" in rejection_reasons(bad), "duplicate ordinal rejected")
    bad = [(dict(src), dict(row)) for src, row in good]
    bad[0][1]["current_locus"] = ""
    check("MISSING_OR_NONPRIMARY_CURRENT_LOCUS" in rejection_reasons(bad), "missing locus rejected")
    bad = [(dict(src), dict(row)) for src, row in good]
    bad[0][1]["matching_method"] = "PAGE_LOCAL_PHYSICAL_CLUSTER_STRING"
    check("NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS" in rejection_reasons(bad), "string mapping rejected")
    bad = [(dict(src), dict(row)) for src, row in good]
    bad[0][1]["all_three_present"] = "0"
    check("NOT_ALL_THREE_MANUAL_READINGS_PRESENT" in rejection_reasons(bad), "reading omission rejected")

    validation = {
        "experiment": "ZLA001_ZODIAC_LABEL_CYCLE_CAPACITY_VALIDATION",
        "status": "PASS",
        "checks": checks,
        "inputs": {path.name: sha(path) for path in (SOURCE, CROSSWALK, PRODUCTION, PANEL, REPORT, Path(__file__))},
        "reconstructed": expected_counts,
        "mutations": {
            "duplicate_ordinal_rejected": True,
            "missing_locus_rejected": True,
            "nonhuman_mapping_rejected": True,
            "missing_reading_rejected": True,
        },
        "claim_ceiling": "Independent reconstruction validates public clockwise-ring capacity only; it supplies no adjacency result, serial code, number, degree, sign name, ownership, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Zodiac label cycle capacity validation\n\n"
        f"Status: **PASS** ({checks} checks). A nonimporting reconstruction recovered all 300 public zodiac "
        "records, 25 candidate rings, the exact four exclusions, and every one of the 235 rows in the strict "
        "21-ring panel. Duplicate ordinals, missing loci, non-human-position mappings, and missing alternate "
        "readings are rejected. No label text or adjacency score was evaluated.\n\n"
        "This validates capacity and provenance only, not a cyclic construction effect or any translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": checks, "panel_sha256": sha(PANEL)}, sort_keys=True))


if __name__ == "__main__":
    main()
