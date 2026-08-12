#!/usr/bin/env python3
"""Freeze the complete strictly mapped-capacity f70v2 star/figure ring panel."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_METHOD.md"
CROSSWALK = RES / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"
ZST001 = RES / "zst001_zodiac_star_tail_native_visual_capacity.json"
OUT = RES / "zst002_f70v2_complete_star_tail_census_selection.json"
REPORT = RES / "zst002_f70v2_complete_star_tail_census_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def strict(row: dict[str, str], groups: dict[str, list[dict[str, str]]]) -> tuple[bool, str]:
    ring = "OUTER" if row["source_unit"] == "s1" else "INNER"
    if row["primary_eligible"] != "1" or not row["current_locus"] or not re.fullmatch(ring + r":GROVE_[1-9][0-9]*", row["position_key"]):
        return False, "CROSSWALK_NOT_STRICT"
    values = sorted(groups.get(row["current_locus"], []), key=lambda x: int(x["consensus_group_index"]))
    if not values:
        return False, "NO_CONSENSUS"
    if any(x["page"] != "f70v2" or x["kind"] != "L" or x["grammar_scope"] != "DIAGNOSTIC_NONPROSE" or x["strict_zero_alternative"] != "1" or not x["family_surface"] for x in values):
        return False, "NONSTRICT_CONSENSUS"
    if [int(x["consensus_group_index"]) for x in values] != list(range(1, len(values) + 1)) or {int(x["consensus_group_count"]) for x in values} != {len(values)}:
        return False, "NONCONTIGUOUS_CONSENSUS"
    return True, "NONE"


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    crosswalk = read_tsv(CROSSWALK)
    group_rows = read_tsv(GROUPS)
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in group_rows:
        lookup[row["locus"]].append(row)
    selected = [r for r in crosswalk if r["source_page"] == "f70v2" and r["source_unit"] in {"s1", "s2"}]
    expected = [("s1", str(i)) for i in range(1, 20)] + [("s2", str(i)) for i in range(1, 11)]
    if [(r["source_unit"], r["source_item"]) for r in selected] != expected:
        raise SystemExit("incomplete or reordered f70v2 panel")
    rows = []
    exclusions = {}
    for source in selected:
        ring = "OUTER" if source["source_unit"] == "s1" else "INNER"
        grove_number = source["position_key"].rsplit("_", 1)[-1]
        ok, reason = strict(source, lookup)
        if not ok:
            exclusions[source["source_record_id"]] = reason
        rows.append({
            "source_record_id": source["source_record_id"],
            "page": "f70v2",
            "physical_folio": "f70",
            "source_unit": source["source_unit"],
            "source_item": source["source_item"],
            "ring": ring,
            "grove_number": grove_number,
            "position_key": source["position_key"],
            "current_locus": source["current_locus"],
            "strict_eligible": ok,
            "strict_exclusion": reason,
        })
    strict_by_ring = {ring: sum(r["strict_eligible"] for r in rows if r["ring"] == ring) for ring in ("OUTER", "INNER")}
    result = {
        "experiment": "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_SELECTION",
        "schema": "ZST002_SELECTION_V1",
        "status": "FROZEN_COMPLETE_29_SLOT_F70V2_PANEL",
        "decision": "AUTHORIZE_COMPLETE_TEXT_BLIND_NATIVE_VISUAL_CENSUS",
        "canvas": {
            "manifest_id": "2002046", "canvas_id": "1006200", "official_dimensions": [3945, 3772],
            "review_image_url": "https://collections.library.yale.edu/iiif/2/1006200/full/2400,/0/default.jpg",
        },
        "counts": {"selected_slots": 29, "outer_slots": 19, "inner_slots": 10, "strict_slots": sum(r["strict_eligible"] for r in rows), "strict_by_ring": strict_by_ring, "strict_exclusions": exclusions},
        "rows": rows,
        "rubric": ["TAIL", "NO_TAIL", "UNCERTAIN"],
        "capacity_gate": "AT_LEAST_ONE_MIXED_STRICT_RING_AND_AT_LEAST_TWO_STRICT_TAIL_AND_TWO_STRICT_NO_TAIL_ACROSS_MIXED_F70V2_RINGS",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (METHOD, CROSSWALK, GROUPS, ZST001)},
        "access": {
            "prior_full_canvas_exposure_disclosed": True,
            "selected_image_body_opened_by_builder": False,
            "surface_family_member_root_parser_role_or_formal_association_serialized": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
        },
        "claim_ceiling": "This freezes a complete f70v2 drawing-state census and strict-capacity mask. It establishes no star-tail word zodiac name sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# ZST002 f70v2 complete star-tail census selection\n\n"
        "Status: **FROZEN_COMPLETE_29_SLOT_F70V2_PANEL**.\n\n"
        f"All 29 f70v2 ring slots are frozen: 19 OUTER and 10 INNER. {result['counts']['strict_slots']} are strict-capacity eligible before visual grading "
        f"({strict_by_ring['OUTER']} OUTER, {strict_by_ring['INNER']} INNER). No surface or formal association was opened or scored.\n\n"
        "A visual pass requires at least one mixed strict ring and at least two strict examples of each state across mixed rings. No translation follows.\n"
    )


if __name__ == "__main__":
    main()
