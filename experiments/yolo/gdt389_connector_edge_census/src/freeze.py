#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
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
R388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    with FRAME.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    pages = sorted(row["page"] for row in rows)
    folios = sorted({row["physical_folio"] for row in rows})
    assert len(pages) == len(set(pages)) == 61 and len(folios) == 30
    assert all(not page.lower().startswith("f84") for page in pages)
    order = sorted(pages, key=lambda page: hashlib.sha256(("GDT389_PAGE_ORDER_V1|" + page).encode()).hexdigest())
    freeze = {
        "schema": "GDT389_PRE_IMAGE_FREEZE_V1",
        "status": "FROZEN_BEFORE_IMAGE_ACCESS",
        "page_universe": {
            "pages": pages,
            "physical_folios": folios,
            "page_count": len(pages),
            "folio_count": len(folios),
            "review_order": order,
            "order_rule": "ascending SHA256('GDT389_PAGE_ORDER_V1|' + exact_page)",
        },
        "allowed_page_screen_states": [
            "NO_CONNECTOR_CANDIDATE",
            "AMBIGUOUS_CONNECTOR",
            "CONNECTOR_WITH_FEWER_THAN_TWO_INSCRIPTIONS",
            "CONNECTOR_WITH_TWO_OR_MORE_INSCRIPTIONS",
            "UNMAPPED_OR_UNREVIEWABLE",
        ],
        "allowed_direction_bases": [
            "VISIBLE_ARROWHEAD",
            "UNAMBIGUOUS_AUTHORIAL_FLOW_DEVICE",
            "FROZEN_EXTERNAL_SOURCE_ORDER",
            "NONE_OR_UNRESOLVED",
        ],
        "forbidden_direction_bases": [
            "TEXT_READING_ORDER",
            "CATALOGUE_ORDER",
            "RADIAL_OR_ARRAY_ADJACENCY",
            "VOYNICH_IDENTITY_OR_RECURRENCE",
            "PROXIMITY_ONLY",
        ],
        "eligibility": {
            "exact_distinct_pivot_and_target_loci": True,
            "singular_endpoint_ownership": True,
            "independent_visible_or_external_direction": True,
            "target_not_determined_by_layout_or_grammar": True,
            "mobile_matched_alternative_target": True,
            "minimum_edges": 50,
            "minimum_physical_folios": 5,
        },
        "access": {
            "allowed_image_authority": "Yale University Library official IIIF only",
            "raw_canvas_label_allowlist_before_retention": True,
            "reject_mixed_canvas_with_any_f84_label": True,
            "formal_identity_access": False,
            "ocr_or_automated_vision": False,
            "f84_access": False,
        },
        "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
        "scoring_authorized": False,
        "inputs": {str(FRAME.relative_to(ROOT)): sha(FRAME), str(R388.relative_to(ROOT)): sha(R388)},
        "implementation": {
            str((BASE / path).relative_to(ROOT)): sha(BASE / path)
            for path in ["src/freeze.py", "src/validate_freeze.py"]
        },
        "claim_ceiling": "GEOMETRY_ONLY_CONNECTOR_EDGE_ACQUISITION",
    }
    freeze["content_hash"] = content(freeze)
    (ART / "gdt389_pre_image_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(f"FROZEN {len(pages)} pages / {len(folios)} folios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
