#!/usr/bin/env python3
"""Materialize the frozen GDT389 direct-visual connector census."""
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
BASE = ROOT / "experiments/yolo/gdt389_connector_edge_census"
ART = BASE / "artifacts"
FRAME = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_page_frame.tsv"
FREEZE = ART / "gdt389_pre_image_freeze.json"
IMAGE_MANIFEST = ART / "gdt389_image_manifest.tsv"
IMAGE_MAPPING = ART / "gdt389_image_mapping.json"
IMAGE_HASHES = ART / "gdt389_review_image_hashes.tsv"


AMBIGUOUS = {
    "f67v2": "Corner-circle face networks use short connecting strokes; nearby or contained inscriptions do not occupy two singular line endpoints, and no arrow or flow direction is visible.",
    "f68r3": "A curved tail joins a star group to a moon drawing; inscriptions lie near the group and tail, but the line endpoints are graphical objects and no arrowhead supplies direction.",
    "f75r": "A long vertical tube links an upper basin or figure region to a lower pool; surrounding and internal writing does not form two singular endpoint inscriptions.",
    "f75v": "Repeated spout or figure columns and pools share drawn ducts; short inscriptions lie within the columns, but no duct visibly joins one inscription endpoint to another.",
    "f77r": "An upper segmented band or branch apparatus and lower drawings have nearby labels; connector endpoints are vessels or figures and direction is unresolved.",
    "f77v": "An upper conduit joins three figure or basin units; inscriptions are adjacent labels rather than connector endpoints, with no arrowhead or independent direction.",
    "f78r": "A segmented duct joins upper basket-like structures and a pool; nearby inscriptions label components but are not two connector endpoints.",
    "f80r": "A right-margin tube and pool system links figures; upper labels and prose are not visibly attached as two connector endpoints.",
    "f81v": "A large enclosed figure array and a marginal drawn stem or tube provide possible connected geometry, but no singular pair of inscription endpoints can be isolated.",
    "f82r": "Tubes link figures, a cross-piece, and pools; inscriptions are on or near apparatus rather than visibly attached to two connector endpoints.",
    "f82v": "Pools, tubes, and arc-like structures link figures; inscriptions lie near the drawings but not at two singular connector endpoints.",
    "f83r": "Arches and tubes join figures and source or target drawings; nearby inscriptions do not form two line endpoints and direction is unresolved.",
    "f83v": "Paired green forms and flow-like apparatus connect drawings; labels are adjacent, while endpoint ownership and direction remain unresolved.",
    "f85r2": "The two official part canvases show radial or path structures and prose; exact subpanel attribution and inscription endpoints remain unresolved, and no arrowhead is visible.",
}

RADIAL = {
    "f57v", "f67r1", "f67r2", "f67v1", "f68r1", "f68r2", "f68v2",
    "f69r", "f69v", "f70r1", "f70v1", "f70v2", "f71r", "f71v",
    "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v",
}

HERBAL_TEXT_PHARMA = {
    "f3v", "f9r", "f39v", "f40v", "f42r", "f42v", "f58r", "f58v", "f65r",
    "f76r", "f88r", "f88v", "f89r1", "f89r2", "f89v1", "f89v2", "f94r",
    "f99r", "f99v", "f100r", "f100v", "f102r1", "f102r2", "f102v1", "f102v2",
}


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
    order = freeze["page_universe"]["review_order"]
    frame_by_page = {row["page"]: row for row in frame}
    assert len(order) == 61 and set(order) == set(frame_by_page)
    assert len(AMBIGUOUS) + len(RADIAL) + len(HERBAL_TEXT_PHARMA) == 61
    assert not (set(AMBIGUOUS) & RADIAL or set(AMBIGUOUS) & HERBAL_TEXT_PHARMA or RADIAL & HERBAL_TEXT_PHARMA)
    assert set(AMBIGUOUS) | RADIAL | HERBAL_TEXT_PHARMA == set(order)
    assert all(not page.lower().startswith("f84") for page in order)
    assert len({row["canvas_id"] for row in image_hashes}) == 50

    map_by_page: dict[str, list[dict[str, str]]] = {}
    for row in mappings:
        assert not row["page"].lower().startswith("f84")
        assert "84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower()
        map_by_page.setdefault(row["page"], []).append(row)
    assert set(map_by_page) == set(order)

    observations: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []
    for review_index, page in enumerate(order, 1):
        canvas_rows = map_by_page[page]
        canvas_ids = ";".join(sorted({row["canvas_id"] for row in canvas_rows}))
        image_urls = ";".join(sorted({row["review_image_url"] for row in canvas_rows}))
        if page in AMBIGUOUS:
            screen_state = "AMBIGUOUS_CONNECTOR"
            geometry_class = "GRAPHICAL_CONNECTOR_WITH_NONSINGULAR_OR_NONINSCRIPTION_ENDPOINTS"
            note = AMBIGUOUS[page]
            exact_endpoint_count = "UNRESOLVED"
            localization_state = "NOT_ATTEMPTED_SCREEN_DID_NOT_ESTABLISH_TWO_INSCRIPTION_ENDPOINTS"
            candidate_id = f"GDT389_CAND_{len(candidates) + 1:03d}"
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "review_index": review_index,
                    "page": page,
                    "physical_folio": frame_by_page[page]["physical_folio"],
                    "canvas_ids": canvas_ids,
                    "geometry_class": geometry_class,
                    "visible_inscription_endpoint_count": exact_endpoint_count,
                    "source_aware_endpoint_localization": localization_state,
                    "direction_basis": "NONE_OR_UNRESOLVED",
                    "failure_stage": "PAGE_SCREEN_ENDPOINT_OWNERSHIP",
                    "eligibility_status": "INELIGIBLE_AMBIGUOUS_NONINSCRIPTION_ENDPOINTS",
                    "review_note": note,
                    "formal_access_state": "SEALED",
                }
            )
        elif page in RADIAL:
            screen_state = "NO_CONNECTOR_CANDIDATE"
            geometry_class = "RADIAL_CIRCULAR_OR_ARRAY_LAYOUT_ONLY"
            note = "Only radial, circular, array, or object-label geometry is visible; spokes and catalogue or radial adjacency are excluded and no line joins two inscription endpoints."
            exact_endpoint_count = "0"
            localization_state = "NOT_APPLICABLE"
        else:
            screen_state = "NO_CONNECTOR_CANDIDATE"
            geometry_class = "HERBAL_PHARMA_OR_TEXT_LAYOUT_WITHOUT_INSCRIPTION_CONNECTOR"
            note = "Plant stems, roots, containers, drawing outlines, prose layout, or object labels are visible, but no authorial line, duct, path, arrow, or pointer joins two inscriptions."
            exact_endpoint_count = "0"
            localization_state = "NOT_APPLICABLE"
        observations.append(
            {
                "review_index": review_index,
                "page": page,
                "physical_folio": frame_by_page[page]["physical_folio"],
                "canvas_ids": canvas_ids,
                "review_image_urls": image_urls,
                "page_screen_state": screen_state,
                "geometry_class": geometry_class,
                "visible_exact_inscription_endpoint_count": exact_endpoint_count,
                "source_aware_endpoint_localization": localization_state,
                "direction_basis": "NONE_OR_UNRESOLVED",
                "review_note": note,
                "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY",
                "automated_visual_method": "NONE",
                "formal_access_state": "SEALED",
            }
        )

    assert len(observations) == 61 and len(candidates) == 14
    assert Counter(row["page_screen_state"] for row in observations) == {
        "NO_CONNECTOR_CANDIDATE": 47,
        "AMBIGUOUS_CONNECTOR": 14,
    }
    write_tsv(ART / "gdt389_page_observations.tsv", observations)
    write_tsv(ART / "gdt389_ambiguous_candidates.tsv", candidates)

    edge_fields = [
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
        "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
        "source_aware_localizer", "relation_reviewer", "relation_confidence", "ambiguity_state",
        "formal_access_state", "fold_assignment", "eligibility_status",
    ]
    write_tsv(ART / "gdt389_eligible_edge_packet.tsv", [], edge_fields)

    gates = [
        ("G01_FORMAL_SEAL", 1, "No formal identity, surface, family, PAGE_HOST, or tuple row was read or scored."),
        ("G02_COMPLETE_PAGE_FRAME", 1, "All 61 frozen pages on 30 physical folios received a direct visual page-screen outcome."),
        ("G03_EXACT_PIVOT", 0, "No connector candidate established even the required two singular inscription endpoints."),
        ("G04_EXACT_TARGET", 0, "No independent exact target inscription was localized."),
        ("G05_FIXED_DIRECTION", 0, "No candidate supplied an arrowhead, unambiguous authorial flow direction, or frozen external source order."),
        ("G06_SINGULAR_OWNERSHIP", 0, "All 14 connector-rich pages remained ambiguous at inscription-endpoint ownership."),
        ("G07_EDGE_CAPACITY", 0, "Zero eligible directed edges is below the frozen minimum of 50."),
        ("G08_FOLIO_CAPACITY", 0, "Zero eligible edge folios is below the frozen minimum of five."),
        ("G09_MOBILE_NULL", 0, "No eligible target exists for a matched mobile alternative."),
    ]
    gate_rows = [
        {"gate_id": gate_id, "current_pass": passed, "evidence": evidence}
        for gate_id, passed, evidence in gates
    ]
    write_tsv(ART / "gdt389_capacity_gates.tsv", gate_rows)

    access = {
        "schema": "GDT389_ACCESS_V1",
        "official_yale_canvases_opened": 50,
        "frozen_pages_reviewed": 61,
        "direct_visual_reviewer_count": 1,
        "direct_visual_reviewer_type": "AI_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
        "ocr_calls": 0,
        "automated_image_classification_calls": 0,
        "clip_embedding_caption_calls": 0,
        "formal_rows_read": 0,
        "voynich_text_identities_read": 0,
        "f84_image_transcription_source_group_formal_identity_prediction_or_score_access": False,
        "known_prior_metadata_display_breach": "See CORRECTION.md; no further f84 access occurred in image mapping or review.",
    }
    access["content_hash"] = content_hash(access)
    (ART / "gdt389_access_log.json").write_text(json.dumps(access, indent=2, sort_keys=True) + "\n")

    output_paths = [
        ART / "gdt389_page_observations.tsv",
        ART / "gdt389_ambiguous_candidates.tsv",
        ART / "gdt389_eligible_edge_packet.tsv",
        ART / "gdt389_capacity_gates.tsv",
        ART / "gdt389_access_log.json",
    ]
    result = {
        "schema": "GDT389_RESULT_V1",
        "status": "COMPLETE_CENSUS_ZERO_ELIGIBLE_DIRECTED_EDGES",
        "counts": {
            "frozen_pages_reviewed": 61,
            "physical_folios_reviewed": 30,
            "official_canvases_reviewed": 50,
            "no_connector_candidate_pages": 47,
            "ambiguous_connector_pages": 14,
            "connector_with_fewer_than_two_inscriptions_pages": 0,
            "connector_with_two_or_more_inscriptions_pages": 0,
            "exact_endpoint_localizations": 0,
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
        "interpretation": "Visible connectors in the frozen frame join graphical objects or regions, not two singular, directionally ordered inscription endpoints. The current parent-link application remains closed at acquisition capacity.",
        "review": {
            "provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
            "complete_frame": True,
            "all_ambiguities_published": True,
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
        "claim_ceiling": "GEOMETRY_ONLY_COMPLETE_CONNECTOR_CENSUS_AND_CAPACITY",
    }
    result["content_hash"] = content_hash(result)
    (ART / "gdt389_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
