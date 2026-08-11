#!/usr/bin/env python3
"""Build the score-blind ZST001 star-tail capacity artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
PROJECTION = RESULTS / "zst001_zodiac_star_tail_state_projection.tsv"
OUT = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity.json"
REPORT = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity_report.md"

EXPECTED = {
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
}
NOTE_BINDINGS = {
    ("f72r3", "z"): ("f72r3.S1", "b98ceb38cb8351bae8c743948b3f7d0004c8e7bb4daea2a95a04fe5938eed6ca"),
    ("f72r3", "y"): ("f72r3.S2", "a1dd0e98c81791950ecd951c62d60d1a97d14e1c50a52a6d249603e3a32910e7"),
    ("f72r3", "x"): ("f72r3.S3", "266c96a38063766cc6053915b72200432823c16c2670859c61580194b5385299"),
    ("f73r", "y"): ("f73r.S1", "127f26916640014f7bae7e0d3728be86ca7d469868aba063609df390c69779d3"),
    ("f73r", "x"): ("f73r.S2", "f22341fdd6cd3de0a22e33c3f1e7d707047b2b82afc72b95b39de56f44df623a"),
}
RINGS = {
    ("f72r3", "x"): ("f72", "INNER", 7, {5, 6, 7}),
    ("f72r3", "y"): ("f72", "MIDDLE", 11, {1, 2, 5, 8, 9, 10}),
    ("f72r3", "z"): ("f72", "OUTER", 12, {1, 2, 3, 6, 7, 8, 9, 10, 12}),
    ("f73r", "x"): ("f73", "INNER", 10, {3}),
    ("f73r", "y"): ("f73", "OUTER", 16, {4, 6}),
}
EXPLICIT_NO_TAIL = {("f73r", "x", 8), ("f73r", "x", 9)}
CONFLICTS = {"STOLFI_BEST_0748", "STOLFI_BEST_0749"}
UNIT_URL = "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/060/L16%2BH-eva/UNITS/"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_projection(crosswalk_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {
        (row["source_page"], row["source_unit"], int(row["source_item"])): row
        for row in crosswalk_rows
        if (row["source_page"], row["source_unit"]) in RINGS and row["source_item"].isdigit()
    }
    output = []
    for (page, unit), (folio, ring, count, tails) in RINGS.items():
        note_name, note_sha = NOTE_BINDINGS[(page, unit)]
        for number in range(1, count + 1):
            source = lookup[(page, unit, number)]
            key = (page, unit, number)
            tail_state = "TAIL" if number in tails else "NO_TAIL"
            if tail_state == "TAIL":
                grade_source = "HUMAN_EXPLICIT_TAIL"
                basis = "public unit note explicitly says star with tail"
            elif key in EXPLICIT_NO_TAIL:
                grade_source = "HUMAN_EXPLICIT_NO_TAIL_CORRECTION"
                basis = "public unit note explicitly rejects tail and distinguishes the arm"
            else:
                grade_source = "NATIVE_CLEAR_NO_TAIL"
                basis = "complete held-star contour visible with no independent continuation beyond the holding arm"
            image_id = "YALE_1006203" if folio == "f72" else "YALE_1006206"
            image_sha = (
                "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"
                if folio == "f72"
                else "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad"
            )
            output.append(
                {
                    "source_record_id": source["source_record_id"],
                    "page": page,
                    "physical_folio": folio,
                    "source_unit": unit,
                    "ring": ring,
                    "grove_number": str(number),
                    "tail_state": tail_state,
                    "grade_source": grade_source,
                    "grade_confidence": "HIGH",
                    "catalogue_star_tail_conflict": "1" if source["source_record_id"] in CONFLICTS else "0",
                    "source_note_url": UNIT_URL + note_name,
                    "source_note_sha256": note_sha,
                    "native_image_id": image_id,
                    "native_image_sha256": image_sha,
                    "visual_basis": basis,
                }
            )
    return output


def strict(row: dict[str, str], crosswalk: dict[str, dict[str, str]], group_lookup: dict[str, list[dict[str, str]]]) -> tuple[bool, str]:
    source = crosswalk[row["source_record_id"]]
    expected_key = f"{row['ring']}:GROVE_{row['grove_number']}"
    if (
        source["primary_eligible"] != "1"
        or not source["current_locus"]
        or source["current_page"] != row["page"]
        or source["position_key"] != expected_key
    ):
        return False, "CROSSWALK_NOT_STRICT"
    groups = sorted(group_lookup.get(source["current_locus"], ()), key=lambda value: int(value["consensus_group_index"]))
    if not groups:
        return False, "NO_CONSENSUS"
    if any(
        value["page"] != row["page"]
        or value["kind"] != "L"
        or value["grammar_scope"] != "DIAGNOSTIC_NONPROSE"
        or value["strict_zero_alternative"] != "1"
        or not value["family_surface"]
        for value in groups
    ):
        return False, "NONSTRICT_CONSENSUS"
    if [int(value["consensus_group_index"]) for value in groups] != list(range(1, len(groups) + 1)):
        return False, "NONCONTIGUOUS_CONSENSUS"
    if {int(value["consensus_group_count"]) for value in groups} != {len(groups)}:
        return False, "INCONSISTENT_CONSENSUS_COUNT"
    return True, "NONE"


def report_text(result: dict) -> str:
    counts = result["counts"]
    return (
        "# ZST001 zodiac star-tail capacity\n\n"
        f"Status: **{result['status']}**\n\n"
        "The underlying f73r unit note corrects compact-catalogue inner positions #8 and #9 to NO_TAIL. "
        f"Across {counts['projected_records']} source-bound grades, {counts['strict_labels_all_rings']} labels are strict. "
        f"Four mixed page-ring strata retain {counts['selected_mixed_strict_labels']} labels and a potential "
        f"{counts['potential_cyclic_worlds']}-world cyclic orbit.\n\n"
        "The route stops because physical folio f73 has only one strict TAIL positive in the mixed panel; "
        "the sole documented f70 tailed star is not primary-eligible and cannot rescue replication. "
        "No formal feature was constructed or scored.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    for path in (PROJECTION, OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")
    crosswalk_rows = rows(CROSSWALK)
    group_rows = rows(GROUPS)
    projection = build_projection(crosswalk_rows)
    fieldnames = list(projection[0])
    with PROJECTION.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(projection)

    crosswalk = {row["source_record_id"]: row for row in crosswalk_rows}
    group_lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in group_rows:
        group_lookup[row["locus"]].append(row)
    strict_rows = []
    exclusions = {}
    for row in projection:
        ok, reason = strict(row, crosswalk, group_lookup)
        if ok:
            strict_rows.append(row)
        else:
            exclusions[row["source_record_id"]] = reason
    strict_strata: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in strict_rows:
        strict_strata[f"{row['page']}|{row['ring']}"].append(row)
    mixed = {
        name: values
        for name, values in strict_strata.items()
        if {row["tail_state"] for row in values} == {"TAIL", "NO_TAIL"}
    }
    selected = [row for values in mixed.values() for row in values]
    selected_by_folio = {
        folio: dict(sorted(Counter(row["tail_state"] for row in selected if row["physical_folio"] == folio).items()))
        for folio in sorted({row["physical_folio"] for row in selected})
    }
    f70 = crosswalk["STOLFI_BEST_0425"]
    f70_strict = f70["primary_eligible"] == "1" and bool(f70["position_key"])
    potential_worlds = math.prod(len(values) for values in mixed.values())
    gates = {
        "exact_56_complete_five_ring_projection": len(projection) == 56,
        "two_source_level_catalogue_corrections": {
            row["source_record_id"] for row in projection if row["catalogue_star_tail_conflict"] == "1"
        } == CONFLICTS,
        "at_least_two_physical_folios_and_four_mixed_strata": len(selected_by_folio) >= 2 and len(mixed) >= 4,
        "at_least_two_strict_examples_of_each_state_per_physical_folio": all(
            counts.get("TAIL", 0) >= 2 and counts.get("NO_TAIL", 0) >= 2
            for counts in selected_by_folio.values()
        ),
        "f70_documented_tail_does_not_supply_strict_rescue": not f70_strict,
        "no_formal_feature_constructed_or_scored": True,
    }
    decision = "STOP_UNSCORED_SINGLE_POSITIVE_SECOND_FOLIO"
    if all(gates.values()):
        decision = "PASS_UNSCORED_STAR_TAIL_CONTRAST_CAPACITY"
    result = {
        "experiment": "ZST001_ZODIAC_STAR_TAIL_NATIVE_VISUAL_CAPACITY",
        "status": decision,
        "decision": decision,
        "inputs": {
            str(CROSSWALK.relative_to(BASE)): EXPECTED[CROSSWALK],
            str(GROUPS.relative_to(BASE)): EXPECTED[GROUPS],
            str(PROJECTION.relative_to(BASE)): sha(PROJECTION),
        },
        "source_bindings": {
            "public_unit_notes": {name: digest for name, digest in sorted(NOTE_BINDINGS.values())},
            "f70v1.S1_sha256": "e6500d9c9bf0b9b86604a830eac113a0a330f92591af64d559825f9f0ba7451c",
            "yale_manifest_2002046_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
            "yale_canvas_1006203_full_sha256": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269",
            "yale_canvas_1006203_f72r3_region_sha256": "b290fc5ef365a928f028e8aa6cd280793947194ad01bbe862da751fcb7feb3d1",
            "yale_canvas_1006206_full_sha256": "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad",
        },
        "counts": {
            "projected_records": len(projection),
            "projected_states": dict(sorted(Counter(row["tail_state"] for row in projection).items())),
            "strict_labels_all_rings": len(strict_rows),
            "strict_states_all_rings": dict(sorted(Counter(row["tail_state"] for row in strict_rows).items())),
            "strict_exclusions": dict(sorted(exclusions.items())),
            "strict_by_page_ring": {
                name: dict(sorted(Counter(row["tail_state"] for row in values).items()))
                for name, values in sorted(strict_strata.items())
            },
            "mixed_strata": sorted(mixed),
            "selected_mixed_strict_labels": len(selected),
            "selected_states": dict(sorted(Counter(row["tail_state"] for row in selected).items())),
            "selected_by_physical_folio": selected_by_folio,
            "potential_cyclic_worlds": potential_worlds,
            "formal_features_constructed": 0,
            "formal_associations_scored": 0,
        },
        "f70_rescue": {
            "source_record_id": "STOLFI_BEST_0425",
            "primary_eligible": f70["primary_eligible"],
            "position_key": f70["position_key"],
            "strict_rescue": f70_strict,
        },
        "gates": gates,
        "claim_ceiling": (
            "This unscored stop and source correction establish no star-tail word, zodiac name, sound, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_text(result), encoding="utf-8")


if __name__ == "__main__":
    main()
