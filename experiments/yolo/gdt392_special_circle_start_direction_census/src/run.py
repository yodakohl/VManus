#!/usr/bin/env python3
"""Materialize the frozen GDT392 focused special-circle census."""
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
BASE = ROOT / "experiments/yolo/gdt392_special_circle_start_direction_census"
ART = BASE / "artifacts"
FRAME = ART / "gdt392_array_frame.tsv"
FREEZE = ART / "gdt392_pre_image_freeze.json"
MAPPING = ART / "gdt392_image_manifest.tsv"
IMAGE_HASHES = ART / "gdt392_review_image_hashes.tsv"

START_ONLY = {
    "SCARR001|f67r1|D1": "A decorated square in the adjacent text ring fixes a conspicuous sector boundary; no arrowhead or other author-visible direction is present.",
    "SCARR002|f67r2|M1": "A dotted radial line from the central figure fixes a conspicuous boundary used by the source census; clockwise order is editorial, not visibly directed.",
    "SCARR003|f67r2|M2": "A dotted radial line fixes a conspicuous boundary used by the source census; no author-visible direction distinguishes the two cyclic orientations.",
    "SCARR004|f67r2|M3": "A dotted radial tail fixes a conspicuous boundary used by the source census; no arrowhead or visible direction is present.",
    "SCARR007|f67v1|X1": "A double ray and wide-gap boundary visibly distinguish a sector break; no visible direction selects clockwise versus counterclockwise order.",
    "SCARR013|f69r|E1": "A decorated wedge visibly distinguishes one radial boundary; no arrowhead or other visible direction is present.",
}


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    frame = tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    mapping = tsv(MAPPING)
    image_hashes = tsv(IMAGE_HASHES)
    assert [row["array_id"] for row in frame] == freeze["frame"]["array_review_order"]
    assert len(frame) == 45 and sum(int(row["slot_count"]) for row in frame) == 504
    assert all(not row["page"].lower().startswith("f84") for row in frame + mapping)

    observations: list[dict[str, object]] = []
    for row in frame:
        array_id = row["array_id"]
        if array_id in START_ONLY:
            state = "DISTINCT_START_MARKER_NO_DIRECTION"
            start = 1
            note = START_ONLY[array_id]
        else:
            state = "NO_AUTHORIAL_START_OR_DIRECTION"
            start = 0
            note = "Focused review found ordinary radial/cyclic layout, figures, stars, sectors, or color variation but no singular author-visible start and no arrowhead or other independent direction marker."
        observations.append(
            {
                **row,
                "review_state": state,
                "author_visible_start_candidate": start,
                "author_visible_direction": 0,
                "ordered_label_ownership_state": "NOT_ASSESSED_DIRECTION_ABSENT",
                "eligible_authorial_start_direction": 0,
                "directed_edges_licensed": 0,
                "review_note": note,
                "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
                "automated_visual_method": "NONE",
            }
        )
    write(ART / "gdt392_array_observations.tsv", observations)
    candidates = [row for row in observations if row["author_visible_start_candidate"]]
    write(ART / "gdt392_start_only_candidates.tsv", candidates)

    gates = [
        ("G01_COMPLETE_FRAME", 1, "All 45 frozen arrays/504 slots received one focused array outcome."),
        ("G02_FORMAL_SEAL", 1, "No Voynich surface, family, PAGE_HOST, tuple, or renderer identity was read or scored."),
        ("G03_AUTHOR_VISIBLE_START", int(bool(candidates)), f"{len(candidates)} arrays retain a start-only candidate."),
        ("G04_AUTHOR_VISIBLE_DIRECTION", 0, "Zero arrays have an independent visible direction marker."),
        ("G05_ORDERED_OWNED_LABELS", 0, "Ownership was not promoted because every array already fails visible direction."),
        ("G06_MINIMUM_DIRECTED_EDGES", 0, "Zero directed edges versus minimum 50."),
        ("G07_MINIMUM_PHYSICAL_FOLIOS", 0, "Zero eligible folios versus minimum five."),
        ("G08_MOBILE_MATCHED_NULL", 0, "No eligible directed relation exists to enter a matched null."),
    ]
    write(ART / "gdt392_capacity_gates.tsv", [{"gate_id": a, "current_pass": b, "evidence": c} for a, b, c in gates])

    access = {
        "schema": "GDT392_ACCESS_V1",
        "arrays_reviewed": 45,
        "slots_covered": 504,
        "pages_reviewed": 23,
        "official_yale_canvases_reviewed": len(image_hashes),
        "direct_visual_reviewer_count": 1,
        "direct_visual_reviewer_type": "AI_DIRECT_VISUAL_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
        "prior_page_exposure_disclosed": True,
        "ocr_calls": 0,
        "automated_image_classification_calls": 0,
        "clip_embedding_caption_calls": 0,
        "voynich_surface_or_formal_rows_read": 0,
        "f84_image_transcription_source_group_formal_identity_prediction_or_score_access": False,
    }
    access["content_hash"] = digest(access)
    (ART / "gdt392_access_log.json").write_text(json.dumps(access, indent=2, sort_keys=True) + "\n")

    state_counts = Counter(str(row["review_state"]) for row in observations)
    output_paths = [
        ART / "gdt392_array_observations.tsv",
        ART / "gdt392_start_only_candidates.tsv",
        ART / "gdt392_capacity_gates.tsv",
        ART / "gdt392_access_log.json",
    ]
    result = {
        "schema": "GDT392_RESULT_V1",
        "status": "COMPLETE_CENSUS_ZERO_ELIGIBLE_START_DIRECTION_ARRAYS",
        "counts": {
            "arrays": len(observations),
            "slots": sum(int(row["slot_count"]) for row in observations),
            "pages": len({row["page"] for row in observations}),
            "physical_folios": len({row["physical_folio"] for row in observations}),
            "official_canvases": len(image_hashes),
            "start_only_candidates": len(candidates),
            "start_only_folios": len({row["physical_folio"] for row in candidates}),
            "direction_markers": 0,
            "eligible_arrays": 0,
            "eligible_directed_edges": 0,
            "eligible_physical_folios": 0,
            "review_states": dict(sorted(state_counts.items())),
        },
        "capacity": {
            "minimum_directed_edges": 50,
            "minimum_physical_folios": 5,
            "all_gates_pass": False,
            "formal_scoring_authorized": False,
        },
        "start_only_array_ids": [row["array_id"] for row in candidates],
        "interpretation": "The complete special-circle inventory contains several visibly distinguished start boundaries, but no independent author-visible direction. Clockwise catalogue/transcription order cannot convert them into ordered target relations.",
        "review": {
            "provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
            "complete_frame": True,
            "automated_visual_judgments": 0,
        },
        "access": access,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [FRAME, FREEZE, MAPPING, IMAGE_HASHES]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in output_paths},
        "implementation": {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())},
        "claim_ceiling": "TEXT_BLIND_SPECIAL_CIRCLE_START_DIRECTION_CENSUS_AND_CAPACITY_ONLY",
    }
    result["content_hash"] = digest(result)
    (ART / "gdt392_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
