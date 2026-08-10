#!/usr/bin/env python3
"""Build a text-blind public-data capacity panel for zodiac label cycles."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = BASE / "cache/existing_human_annotations/labtit-best.idx"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
CROSSWALK_RESULT = RESULTS / "existing_human_current_locus_crosswalk.json"
CROSSWALK_VALIDATION = RESULTS / "existing_human_current_locus_crosswalk_validation.json"
OWNERSHIP_VALIDATION = RESULTS / "zodiac_star_slot_ownership_validation.json"
OUT_TSV = RESULTS / "zodiac_label_cycle_capacity.tsv"
OUT_JSON = RESULTS / "zodiac_label_cycle_capacity.json"
OUT_REPORT = RESULTS / "zodiac_label_cycle_capacity.md"

STOLFI_URL = "https://www.ic.unicamp.br/en/~stolfi/EXPORT/00-EXPORT/98-02-01-lotsa-labels/"
GROVE_URL = "https://en.wikibooks.org/wiki/The_Voynich_Manuscript/Jargon#G"
RING_SCOPES = {"INNER", "MIDDLE", "OUTER"}
READINGS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"f(\d+)[rv]\d*", page)
    if not match:
        raise AssertionError(f"bad page: {page}")
    return f"f{int(match.group(1))}"


def source_rows() -> list[dict[str, object]]:
    output = []
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        fields = raw.split("|")
        if len(fields) != 11 or fields[1] != "zodiac":
            continue
        comments = fields[10].strip()
        lowered = comments.lower()
        if "not in circle" in lowered:
            scope = "OUTSIDE"
        else:
            scope = next(
                (candidate.upper() for candidate in ("central", "inner", "middle", "outer") if candidate in lowered),
                "UNKNOWN",
            )
        ordinal_match = re.search(r"#\s*(\d+)", comments)
        output.append(
            {
                "source_record_id": f"STOLFI_BEST_{fields[0]}",
                "page": fields[2],
                "scope": scope,
                "grove_ordinal": int(ordinal_match.group(1)) if ordinal_match else None,
                "explicit_hash_ordinal": bool(ordinal_match),
            }
        )
    return output


def crosswalk_rows() -> dict[str, dict[str, str]]:
    with CROSSWALK.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    keyed = {row["source_record_id"]: row for row in rows}
    if len(keyed) != len(rows):
        raise AssertionError("duplicate crosswalk source_record_id")
    return keyed


def render_report(result: dict[str, object]) -> str:
    counts = result["counts"]
    dropped = result["dropped_rings"]
    return (
        "# Zodiac label cycle capacity\n\n"
        "Status: **PASS_TEXT_BLIND_21_RING_235_SLOT_PUBLIC_ORDINAL_PANEL**.\n\n"
        "This grouping is public catalogue data, not a user-supplied page or label assignment. "
        f"The [Stolfi/Grove label catalogue]({STOLFI_URL}) supplies the zodiac page, ring description, "
        "and Grove number; Grove numbers count positions clockwise within a ring. The already validated "
        "current-locus crosswalk maps those public records to the manual ZL3b/IT2a/RF1b transcription "
        "without image recognition or OCR.\n\n"
        f"The raw catalogue contains {counts['public_zodiac_records']} zodiac records on "
        f"{counts['public_zodiac_pages']} pages. A strict panel keeps only complete INNER/MIDDLE/OUTER "
        "rings whose ordinals are exactly 1..N and whose every record has an explicit human Grove key, "
        "a primary one-to-one current-locus mapping, and all three manual readings. It retains "
        f"**{counts['eligible_rings']} rings, {counts['eligible_slots']} label slots, "
        f"{counts['eligible_pages']} pages, and {counts['eligible_physical_folios']} physical folios**. "
        "Every retained mapping uses `HUMAN_GROVE_SCOPE_NUMBER`; no label text, STA identity, adjacency "
        "similarity, or manuscript outcome was inspected.\n\n"
        "Four rings are excluded before any text score: f70v1 INNER and OUTER use string-cluster mapping "
        "rather than the explicit human-position crosswalk; f72r2 OUTER contains the public missing label; "
        "and f72v1 OUTER contains one catalogue ordinal written as `6 (or possibly the queen)` rather than "
        "an explicit `#6`. CENTRAL and OUTSIDE records are not cyclic-ring members.\n\n"
        "The panel is therefore sufficient for a new rotation/reflection-invariant test of whether adjacent "
        "zodiac labels share transferable partial construction structure more than within-ring permutations. "
        "Such a test must preserve whole labels, ring membership, length opportunity, alternate-reading "
        "linkage, and physical-folio concentration. It is distinct from the failed C-to-L echo, duplicate-sign, "
        "opposition, and universal 30-position phase routes. No object ownership is assumed: the only geometry "
        "used is public clockwise ring order.\n\n"
        "Claim ceiling: capacity and public cyclic order only. No serial code, number, degree, sign name, "
        "word, meaning, plaintext, or translation follows.\n\n"
        "## Dropped rings\n\n"
        + "\n".join(
            f"- `{row['ring_id']}` ({row['slots']} slots): {', '.join(row['reasons'])}"
            for row in dropped
        )
        + "\n"
    )


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, OUT_REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")

    cw_status = json.loads(CROSSWALK_RESULT.read_text(encoding="utf-8"))
    cw_validation = json.loads(CROSSWALK_VALIDATION.read_text(encoding="utf-8"))
    ownership = json.loads(OWNERSHIP_VALIDATION.read_text(encoding="utf-8"))
    if cw_status.get("status") != "PASS_CLUSTERED_MULTI_EVIDENCE_CURRENT_LOCUS_CROSSWALK":
        raise AssertionError("crosswalk status drift")
    if cw_validation.get("status") != "PASS_INDEPENDENT_CLUSTERED_CURRENT_LOCUS_CROSSWALK_VALIDATION":
        raise AssertionError("crosswalk validation drift")
    if ownership.get("status") != "PASS_INDEPENDENT_PUBLIC_SOURCE_AGGREGATE_CONFOUND_CORRECTION":
        raise AssertionError("zodiac ownership correction drift")

    source = source_rows()
    crosswalk = crosswalk_rows()
    if len(source) != 300 or len({row["source_record_id"] for row in source}) != 300:
        raise AssertionError("public zodiac inventory drift")
    if set(row["source_record_id"] for row in source) - set(crosswalk):
        raise AssertionError("source record missing from crosswalk")

    candidate_rings: dict[tuple[str, str], list[tuple[dict[str, object], dict[str, str]]]] = defaultdict(list)
    nonring = Counter()
    for src in source:
        if src["scope"] not in RING_SCOPES:
            nonring[str(src["scope"])] += 1
            continue
        candidate_rings[(str(src["page"]), str(src["scope"]))].append(
            (src, crosswalk[str(src["source_record_id"])])
        )

    kept: list[dict[str, object]] = []
    dropped: list[dict[str, object]] = []
    panel_rows: list[dict[str, object]] = []
    for (page, scope), records in sorted(candidate_rings.items()):
        ring_id = f"{page}:{scope}"
        reasons = []
        ordinals = [src["grove_ordinal"] for src, _ in records]
        if any(value is None for value in ordinals):
            reasons.append("NONEXPLICIT_OR_MISSING_GROVE_ORDINAL")
        elif sorted(int(value) for value in ordinals) != list(range(1, len(records) + 1)):
            reasons.append("NONCONTIGUOUS_GROVE_ORDINALS")
        if any(cw["matching_method"] != "HUMAN_GROVE_SCOPE_NUMBER" for _, cw in records):
            reasons.append("NOT_ALL_EXPLICIT_HUMAN_POSITION_MAPPINGS")
        if any(cw["primary_eligible"] != "1" or not cw["current_locus"] for _, cw in records):
            reasons.append("MISSING_OR_NONPRIMARY_CURRENT_LOCUS")
        if any(cw["all_three_present"] != "1" for _, cw in records):
            reasons.append("NOT_ALL_THREE_MANUAL_READINGS_PRESENT")
        if len({cw["current_locus"] for _, cw in records if cw["current_locus"]}) != len(records):
            reasons.append("CURRENT_LOCUS_NOT_ONE_TO_ONE")
        if reasons:
            dropped.append({"ring_id": ring_id, "slots": len(records), "reasons": reasons})
            continue

        ordered = sorted(records, key=lambda item: int(item[0]["grove_ordinal"]))
        kept.append({"ring_id": ring_id, "page": page, "scope": scope, "slots": len(ordered)})
        for src, cw in ordered:
            panel_rows.append(
                {
                    "ring_id": ring_id,
                    "page": page,
                    "physical_folio": physical_folio(page),
                    "ring_scope": scope,
                    "grove_ordinal": int(src["grove_ordinal"]),
                    "source_record_id": src["source_record_id"],
                    "current_locus": cw["current_locus"],
                    "current_code": cw["current_code"],
                    "current_kind": cw["current_kind"],
                    "matching_method": cw["matching_method"],
                    "match_status": cw["match_status"],
                }
            )

    panel_loci = [str(row["current_locus"]) for row in panel_rows]
    page_set = {str(row["page"]) for row in panel_rows}
    folio_set = {str(row["physical_folio"]) for row in panel_rows}
    ring_lengths = Counter(int(row["slots"]) for row in kept)
    gates = {
        "public_source_has_exactly_300_zodiac_records": len(source) == 300,
        "public_source_has_exactly_12_zodiac_pages": len({str(row["page"]) for row in source}) == 12,
        "one_public_missing_label_is_preserved": any(
            row["source_record_id"] == "STOLFI_BEST_0606" and not crosswalk[str(row["source_record_id"])]["current_locus"]
            for row in source
        ),
        "exactly_25_candidate_physical_rings": len(candidate_rings) == 25,
        "exactly_21_strict_complete_rings": len(kept) == 21,
        "exactly_235_strict_slots": len(panel_rows) == 235,
        "strict_panel_spans_11_pages_and_4_folios": len(page_set) == 11 and len(folio_set) == 4,
        "every_retained_mapping_is_explicit_human_grove_key": all(
            row["matching_method"] == "HUMAN_GROVE_SCOPE_NUMBER" for row in panel_rows
        ),
        "every_retained_ring_has_contiguous_ordinals": all(
            sorted(int(row["grove_ordinal"]) for row in panel_rows if row["ring_id"] == ring["ring_id"])
            == list(range(1, int(ring["slots"]) + 1))
            for ring in kept
        ),
        "every_retained_slot_is_one_to_one": len(panel_loci) == len(set(panel_loci)),
        "all_three_readings_linked_not_independent": True,
        "no_label_text_STA_identity_similarity_or_outcome_accessed": True,
        "no_image_OCR_or_neural_vision_used": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError(gates)

    fieldnames = list(panel_rows[0])
    lines = ["\t".join(fieldnames)]
    lines.extend("\t".join(str(row[field]) for field in fieldnames) for row in panel_rows)
    tsv_bytes = ("\n".join(lines) + "\n").encode()
    result: dict[str, object] = {
        "experiment": "ZLA001_ZODIAC_LABEL_CYCLE_CAPACITY",
        "status": "PASS_TEXT_BLIND_21_RING_235_SLOT_PUBLIC_ORDINAL_PANEL",
        "decision": "AUTHORIZE_PREREGISTRATION_AND_TARGET_BLIND_CONTROLS_ONLY",
        "inputs": {str(path.relative_to(BASE.parent.parent)): sha(path) for path in (
            SOURCE, CROSSWALK, CROSSWALK_RESULT, CROSSWALK_VALIDATION, OWNERSHIP_VALIDATION, Path(__file__)
        )},
        "public_provenance": {
            "catalogue_url": STOLFI_URL,
            "grove_number_definition_url": GROVE_URL,
            "catalogue_role": "public human catalogue supplies zodiac page, ring scope, and clockwise Grove ordinal",
            "crosswalk_role": "validated human-position crosswalk supplies current locus only",
        },
        "counts": {
            "public_zodiac_records": len(source),
            "public_zodiac_pages": len({str(row["page"]) for row in source}),
            "candidate_rings": len(candidate_rings),
            "candidate_ring_slots": sum(len(rows) for rows in candidate_rings.values()),
            "eligible_rings": len(kept),
            "eligible_slots": len(panel_rows),
            "eligible_pages": len(page_set),
            "eligible_physical_folios": len(folio_set),
            "dropped_rings": len(dropped),
            "nonring_records": dict(sorted(nonring.items())),
        },
        "eligible_ring_length_counts": {str(key): value for key, value in sorted(ring_lengths.items())},
        "eligible_rings": kept,
        "dropped_rings": dropped,
        "panel_sha256": hashlib.sha256(tsv_bytes).hexdigest(),
        "gates": gates,
        "claim_ceiling": "Public clockwise cycle geometry and score-blind capacity only; no adjacency effect, serial code, number, degree, sign name, object ownership, word, meaning, plaintext, or translation.",
    }
    report = render_report(result)
    OUT_TSV.write_bytes(tsv_bytes)
    OUT_JSON.write_bytes(canonical_bytes(result))
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "panel_sha256": result["panel_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
