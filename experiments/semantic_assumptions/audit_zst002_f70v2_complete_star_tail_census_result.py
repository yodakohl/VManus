#!/usr/bin/env python3
"""Record and audit the complete native-visual f70v2 star-tail census."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_METHOD.md"
SELECTION = RES / "zst002_f70v2_complete_star_tail_census_selection.json"
SELECTION_VALIDATION = RES / "zst002_f70v2_complete_star_tail_census_selection_validation.json"
PROJECTION = RES / "zst002_f70v2_complete_star_tail_census_projection.tsv"
OUT = RES / "zst002_f70v2_complete_star_tail_census_result.json"
REPORT = RES / "zst002_f70v2_complete_star_tail_census_result_report.md"

FULL_SHA = "062ff6a9f14d0c16eb12dc8f6dc480771b7c19746ebdb20302b998e66181ccea"
REVIEW_REGIONS = {
    "top_2200x2100_at_700_200": "9243d68d4fd82437e9b747e5098c16b0c658fccab64c024db42e3d79f615da4e",
    "right_2100x2200_at_1750_700": "e530510996e2cfd732a1f46506687d87f33acca03aac594e8b67859101c23474",
    "bottom_2200x1900_at_700_1750": "3044f8fe0bf69507122af9c24daf5766c6ed34b7087ba1b4ae07aa8cbed6a392",
    "left_1900x2200_at_450_700": "168d47eb51c15c99d58e366e79d0a5768d191cb8637799cb423c8f5cc52a2b91",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for path in (PROJECTION, OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    selection = json.loads(SELECTION.read_text())
    if selection["status"] != "FROZEN_COMPLETE_29_SLOT_F70V2_PANEL" or len(selection["rows"]) != 29:
        raise SystemExit("selection mismatch")
    rows = []
    for source in selection["rows"]:
        rows.append({
            "source_record_id": source["source_record_id"],
            "page": source["page"],
            "physical_folio": source["physical_folio"],
            "source_unit": source["source_unit"],
            "source_item": source["source_item"],
            "ring": source["ring"],
            "grove_number": source["grove_number"],
            "current_locus": source["current_locus"],
            "strict_eligible": "1" if source["strict_eligible"] else "0",
            "tail_state": "NO_TAIL",
            "grade_confidence": "HIGH",
            "native_image_id": "YALE_1006200_FULL",
            "native_image_sha256": FULL_SHA,
            "visual_basis": "complete ordinary held-star contour visible; no distinct line or tapered extension continues beyond the star away from the holding hand/arm",
        })
    with PROJECTION.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    strict = [row for row in rows if row["strict_eligible"] == "1"]
    strict_by_ring = {
        ring: dict(sorted(Counter(row["tail_state"] for row in strict if row["ring"] == ring).items()))
        for ring in ("OUTER", "INNER")
    }
    mixed = [ring for ring, counts in strict_by_ring.items() if set(counts) == {"TAIL", "NO_TAIL"}]
    selected_mixed = [row for row in strict if row["ring"] in mixed]
    mixed_states = Counter(row["tail_state"] for row in selected_mixed)
    gates = {
        "exact_complete_29_slot_census": len(rows) == 29,
        "all_slots_receive_source_bound_native_visual_grade": all(row["tail_state"] in {"TAIL", "NO_TAIL", "UNCERTAIN"} for row in rows),
        "exact_25_predeclared_strict_slots": len(strict) == 25,
        "at_least_one_mixed_strict_ring": bool(mixed),
        "at_least_two_strict_tail_and_two_strict_no_tail_across_mixed_rings": mixed_states["TAIL"] >= 2 and mixed_states["NO_TAIL"] >= 2,
        "no_formal_feature_or_association_opened": True,
    }
    result = {
        "experiment": "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_RESULT",
        "schema": "ZST002_RESULT_V1",
        "status": "STOP_ZERO_TAIL_IN_COMPLETE_F70V2_PANEL",
        "decision": "KEEP_ZODIAC_STAR_TAIL_FORMAL_MARKER_ROUTE_CLOSED",
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SELECTION.relative_to(ROOT)): sha(SELECTION),
            str(SELECTION_VALIDATION.relative_to(ROOT)): sha(SELECTION_VALIDATION),
            str(PROJECTION.relative_to(ROOT)): sha(PROJECTION),
        },
        "image_binding": {
            "canvas_id": "1006200", "official_dimensions": [3945, 3772],
            "full_image_sha256": FULL_SHA, "review_region_sha256s": REVIEW_REGIONS,
        },
        "counts": {
            "graded_slots": len(rows), "graded_states": dict(sorted(Counter(row["tail_state"] for row in rows).items())),
            "strict_slots": len(strict), "strict_states": dict(sorted(Counter(row["tail_state"] for row in strict).items())),
            "strict_by_ring": strict_by_ring, "mixed_strict_rings": mixed, "mixed_strict_slots": len(selected_mixed),
            "formal_features_constructed": 0, "formal_associations_scored": 0,
        },
        "gates": gates,
        "access": {
            "official_source_native_pixels_used": True,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "label_text_used_in_grade": False,
            "formal_family_member_root_parser_role_or_association_opened": False,
            "preflight_console_incidentally_displayed_machine_readable_source_transcriptions_before_selection_publication": True,
            "incidental_transcriptions_used_in_selection_or_visual_grade": False,
        },
        "claim_ceiling": "The complete f70v2 census supplies no TAIL positive and therefore does not reopen the stopped formal-marker route. It establishes no star-tail word zodiac name sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# ZST002 f70v2 complete star-tail census result\n\n"
        "Status: **STOP_ZERO_TAIL_IN_COMPLETE_F70V2_PANEL**.\n\n"
        "Direct native inspection of all 29 frozen f70v2 slots finds 29 NO_TAIL, zero TAIL, and zero UNCERTAIN grades. "
        "All held stars have ordinary complete contours with no independent line or tapered extension continuing beyond the star away from the holding hand or arm. "
        "The 25 predeclared strict slots likewise contain 25 NO_TAIL: 16 OUTER and nine INNER. Neither ring is mixed, so both target capacity gates fail.\n\n"
        "During preflight, a console diagnostic incidentally displayed the machine-readable source transcriptions for these records before selection publication. "
        "They did not encode a tail state and were not used in selection or visual grading; the exposure is recorded for provenance. No formal identity or association was opened after grading.\n\n"
        "Keep the zodiac star-tail formal-marker route closed. No star-tail word, zodiac name, sound, language, cipher, plaintext, meaning, or translation follows.\n"
    )


if __name__ == "__main__":
    main()
