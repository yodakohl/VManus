#!/usr/bin/env python3
"""Materialize the frozen GDT390 Q20 inter-record-pointer census."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
FRAME = ART / "gdt390_record_frame.tsv"
FREEZE = ART / "gdt390_pre_image_freeze.json"
IMAGE_MANIFEST = ART / "gdt390_image_manifest.tsv"
IMAGE_MAPPING = ART / "gdt390_image_mapping.json"
IMAGE_HASHES = ART / "gdt390_review_image_hashes.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_hash(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    frame = read_tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    mappings = read_tsv(IMAGE_MANIFEST)
    image_hashes = read_tsv(IMAGE_HASHES)
    page_order = freeze["frame"]["page_review_order"]
    record_order = freeze["frame"]["record_review_order"]
    by_page = {row["page"]: row for row in mappings}
    frame_by_unit = {row["unit_id"]: row for row in frame}

    assert len(frame) == len(frame_by_unit) == 170
    assert len(page_order) == 13 and set(page_order) == set(by_page)
    assert len(record_order) == 170 and set(record_order) == set(frame_by_unit)
    assert len(image_hashes) == 13 and {row["page"] for row in image_hashes} == set(page_order)
    assert all(not row["page"].lower().startswith("f84") for row in frame)
    assert all("84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mappings)

    page_note = (
        "Complete-page review shows star-like marginal record markers beside text blocks, "
        "but no visible arrow, line, bracket, tail, path, or other authorial device connects "
        "one star-defined record or marker to a different record or marker."
    )
    page_observations: list[dict[str, object]] = []
    for review_index, page in enumerate(page_order, 1):
        mapping = by_page[page]
        records = [row for row in frame if row["page"] == page]
        page_observations.append(
            {
                "review_index": review_index,
                "page": page,
                "physical_folio": records[0]["physical_folio"],
                "canvas_id": mapping["canvas_id"],
                "review_image_url": mapping["review_image_url"],
                "frozen_record_count": len(records),
                "page_screen_state": "NO_INTER_RECORD_POINTER",
                "candidate_cross_record_devices": 0,
                "direction_basis": "NONE_OR_UNRESOLVED",
                "review_note": page_note,
                "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY",
                "automated_visual_method": "NONE",
                "formal_access_state": "SEALED",
            }
        )
    write_tsv(ART / "gdt390_page_observations.tsv", page_observations)

    record_observations: list[dict[str, object]] = []
    for review_index, unit_id in enumerate(record_order, 1):
        row = frame_by_unit[unit_id]
        record_observations.append(
            {
                "record_review_index": review_index,
                "unit_id": unit_id,
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "star_ordinal": row["star_ordinal"],
                "record_line_count": row["record_line_count"],
                "record_region_review_state": "REVIEWED_WITH_COMPLETE_PAGE",
                "outgoing_pointer_candidate_count": 0,
                "incoming_pointer_candidate_count": 0,
                "record_pointer_state": "NO_VISIBLE_INTER_RECORD_POINTER",
                "review_basis": "COMPLETE_PAGE_DIRECT_VISUAL_SCREEN",
                "formal_access_state": "SEALED",
            }
        )
    write_tsv(ART / "gdt390_record_observations.tsv", record_observations)

    candidate_fields = [
        "candidate_id", "page", "physical_folio", "source_unit_id", "target_unit_id",
        "visible_device", "direction_basis", "singular_source_ownership",
        "singular_target_ownership", "eligibility_status", "formal_access_state",
    ]
    write_tsv(ART / "gdt390_pointer_candidates.tsv", [], candidate_fields)
    edge_fields = [
        "edge_id", "page", "physical_folio", "source_unit_id", "target_unit_id",
        "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
        "source_manifest_id", "page_crop_sha256", "source_crop_sha256", "target_crop_sha256",
        "reviewer_provenance", "ambiguity_state", "formal_access_state", "fold_assignment",
        "eligibility_status",
    ]
    write_tsv(ART / "gdt390_eligible_edge_packet.tsv", [], edge_fields)

    gates = [
        ("G01_FORMAL_SEAL", 1, "No group surface, family, PAGE_HOST, tuple, record-template, or formal row was read or scored."),
        ("G02_COMPLETE_PAGE_FRAME", 1, "All 13 frozen pages on eight physical folios received a direct visual screen."),
        ("G03_COMPLETE_RECORD_FRAME", 1, "All 170 frozen star-defined record regions were covered by their complete-page screens."),
        ("G04_POINTER_CANDIDATE", 0, "No visible inter-record connector or pointer candidate was found."),
        ("G05_EXACT_SOURCE", 0, "No pointer candidate supplied an exact singular source record."),
        ("G06_EXACT_TARGET", 0, "No pointer candidate supplied an exact singular target record."),
        ("G07_FIXED_DIRECTION", 0, "No arrowhead or other authorial direction device was found."),
        ("G08_EDGE_CAPACITY", 0, "Zero eligible directed edges is below the frozen minimum of 50."),
        ("G09_FOLIO_CAPACITY", 0, "Zero eligible edge folios is below the frozen minimum of five."),
        ("G10_MOBILE_NULL", 0, "No eligible target exists for a matched mobile alternative."),
    ]
    gate_rows = [{"gate_id": gate_id, "current_pass": passed, "evidence": evidence} for gate_id, passed, evidence in gates]
    write_tsv(ART / "gdt390_capacity_gates.tsv", gate_rows)

    access = {
        "schema": "GDT390_ACCESS_V1",
        "official_yale_canvases_opened": 13,
        "frozen_pages_reviewed": 13,
        "frozen_records_reviewed": 170,
        "direct_visual_reviewer_count": 1,
        "direct_visual_reviewer_type": "AI_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
        "ocr_calls": 0,
        "automated_image_classification_calls": 0,
        "clip_embedding_caption_calls": 0,
        "formal_rows_read": 0,
        "voynich_text_identities_read": 0,
        "f84_image_transcription_source_group_formal_identity_prediction_or_score_access": False,
        "known_prior_metadata_display_breach": "See VOYNICH_CURRENT_ROUTE.md; no further f84 access occurred in GDT390 mapping or review.",
    }
    access["content_hash"] = content_hash(access)
    (ART / "gdt390_access_log.json").write_text(json.dumps(access, indent=2, sort_keys=True) + "\n")

    output_paths = [
        ART / "gdt390_page_observations.tsv",
        ART / "gdt390_record_observations.tsv",
        ART / "gdt390_pointer_candidates.tsv",
        ART / "gdt390_eligible_edge_packet.tsv",
        ART / "gdt390_capacity_gates.tsv",
        ART / "gdt390_access_log.json",
    ]
    page_counts = Counter(row["page_screen_state"] for row in page_observations)
    result = {
        "schema": "GDT390_RESULT_V1",
        "status": "COMPLETE_Q20_CENSUS_ZERO_INTER_RECORD_POINTERS",
        "counts": {
            "frozen_pages_reviewed": len(page_observations),
            "physical_folios_reviewed": len({row["physical_folio"] for row in page_observations}),
            "frozen_records_reviewed": len(record_observations),
            "official_canvases_reviewed": len(image_hashes),
            "no_inter_record_pointer_pages": page_counts["NO_INTER_RECORD_POINTER"],
            "ambiguous_cross_record_geometry_pages": 0,
            "pointer_candidates": 0,
            "exact_source_target_localizations": 0,
            "eligible_directed_edges": 0,
            "eligible_directed_edge_folios": 0,
        },
        "capacity": {
            "minimum_edges": 50,
            "minimum_physical_folios": 5,
            "edge_gate_pass": False,
            "folio_gate_pass": False,
            "later_formal_scoring_authorized": False,
        },
        "interpretation": "Across the complete 170-record Q20 frame, star-like marginal record markers are present but no author-visible device connects one record to another. The inter-record parent/reference-pointer route closes at acquisition capacity.",
        "review": {
            "provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
            "complete_page_frame": True,
            "complete_record_frame": True,
            "automated_visual_judgments": 0,
        },
        "access": access,
        "inputs": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [FRAME, FREEZE, IMAGE_MANIFEST, IMAGE_MAPPING, IMAGE_HASHES]
        },
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in output_paths},
        "implementation": {
            str((BASE / path).relative_to(ROOT)): sha(BASE / path)
            for path in ["src/map_images.py", "src/prepare_review.py", "src/run.py"]
        },
        "claim_ceiling": "Q20_INTER_RECORD_POINTER_GEOMETRY_AND_CAPACITY_ONLY",
    }
    result["content_hash"] = content_hash(result)
    (ART / "gdt390_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
