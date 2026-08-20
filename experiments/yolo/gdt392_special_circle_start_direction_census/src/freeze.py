#!/usr/bin/env python3
"""Freeze the complete f84-free special-circle start/direction census."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt392_special_circle_start_direction_census"
ART = BASE / "artifacts"
INVENTORY = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
PROTOCOL = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
SOURCE_MAPPING = ROOT / "experiments/yolo/gdt389_connector_edge_census/artifacts/gdt389_image_manifest.tsv"
SOURCE_HASHES = ROOT / "experiments/yolo/gdt389_connector_edge_census/artifacts/gdt389_review_image_hashes.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_tsv(path: Path, selector: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n\r").split("\t")
        index = header.index(selector)
        for raw in handle:
            values = raw.rstrip("\n\r").split("\t")
            value = values[index].strip().lower()
            if value.startswith("f84"):
                raise RuntimeError(f"forbidden selector in {path.name}: {value}")
            rows.append(dict(zip(header, values)))
    return rows


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    slots = guarded_tsv(INVENTORY, "page")
    mapping = guarded_tsv(SOURCE_MAPPING, "page")
    hashes = list(csv.DictReader(SOURCE_HASHES.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(slots) == 504
    arrays: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        arrays[row["array_id"]].append(row)
    assert len(arrays) == 45
    pages = sorted({row["page"] for row in slots})
    folios = sorted({row["physical_folio"] for row in slots})
    assert len(pages) == 23 and len(folios) == 7
    page_mapping = defaultdict(list)
    for row in mapping:
        if row["page"] in pages:
            page_mapping[row["page"]].append(row)
    assert set(page_mapping) == set(pages)
    selected_canvas_ids = {row["canvas_id"] for rows in page_mapping.values() for row in rows}
    hash_by_canvas = {row["canvas_id"]: row for row in hashes}
    assert selected_canvas_ids <= set(hash_by_canvas)

    frame: list[dict[str, object]] = []
    for array_id, rows in arrays.items():
        first = rows[0]
        slot_count = int(first["slot_count"])
        indexes = sorted(int(row["slot_index"]) for row in rows)
        assert len(rows) == slot_count and indexes == list(range(1, slot_count + 1))
        assert len({row["page"] for row in rows}) == len({row["physical_folio"] for row in rows}) == len({row["unit"] for row in rows}) == 1
        occupancy = Counter(row["occupancy_state"] for row in rows)
        canvas_ids = sorted({row["canvas_id"] for row in page_mapping[first["page"]]})
        frame.append(
            {
                "array_index": int(first["array_index"]),
                "array_id": array_id,
                "physical_folio": first["physical_folio"],
                "page": first["page"],
                "unit": first["unit"],
                "slot_count": slot_count,
                "transcribed_slots": occupancy.get("TRANSCRIBED", 0),
                "absent_slots": occupancy.get("ABSENT", 0),
                "unreadable_or_other_slots": slot_count - occupancy.get("TRANSCRIBED", 0) - occupancy.get("ABSENT", 0),
                "neutral_unit_description": first["unit_description"],
                "canvas_ids": ";".join(canvas_ids),
                "formal_access_state": "SEALED",
            }
        )
    frame.sort(key=lambda row: int(row["array_index"]))
    assert [int(row["array_index"]) for row in frame] == list(range(1, 46))
    write(ART / "gdt392_array_frame.tsv", frame)

    selected_mapping = [row for row in mapping if row["page"] in pages]
    write(ART / "gdt392_image_manifest.tsv", selected_mapping)
    selected_hashes = [hash_by_canvas[canvas_id] for canvas_id in sorted(selected_canvas_ids)]
    write(ART / "gdt392_review_image_hashes.tsv", selected_hashes)

    freeze = {
        "schema": "GDT392_PRE_IMAGE_FREEZE_V1",
        "status": "FROZEN_BEFORE_FOCUSED_ARRAY_REVIEW",
        "question": "Do any of the 45 complete special-circle arrays contain an author-visible start and direction tied to separately owned label slots?",
        "frame": {
            "arrays": 45,
            "slots": 504,
            "pages": 23,
            "physical_folios": 7,
            "official_canvases": len(selected_canvas_ids),
            "array_review_order": [str(row["array_id"]) for row in frame],
            "pages_allowlist": pages,
        },
        "outcome_states": [
            "NO_AUTHORIAL_START_OR_DIRECTION",
            "DISTINCT_START_MARKER_NO_DIRECTION",
            "DIRECTION_MARKER_NO_SINGULAR_START",
            "START_AND_DIRECTION_WITHOUT_ORDERED_OWNED_LABELS",
            "ELIGIBLE_AUTHORIAL_START_DIRECTION",
            "AMBIGUOUS_OR_UNRESOLVED",
        ],
        "eligibility": [
            "start marker is author-visible and array-local",
            "direction is author-visible and is not inferred from catalogue/text/radial order",
            "ordered slots have separately owned exact manuscript loci",
            "the resulting directed edges are external to Voynich formal identity",
            "at least 50 directed edges span at least five physical folios",
            "targets remain mobile under a topology-preserving matched null",
        ],
        "forbidden_substitutes": [
            "catalogue slot order",
            "clock-face annotation convention",
            "ordinary clockwise reading convention",
            "radial adjacency or center-spoke geometry",
            "decorated sector without independent direction",
            "Voynich text order, recurrence, surface, family, PAGE_HOST, tuple, or renderer identity",
        ],
        "access": {
            "source_inventory_rows_read": len(slots),
            "source_visual_descriptions_available": True,
            "focused_array_review_performed": False,
            "voynich_surface_or_formal_rows_read": 0,
            "f84_opened_parsed_retained_or_scored": False,
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [INVENTORY, PROTOCOL, SOURCE_MAPPING, SOURCE_HASHES]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in [ART / "gdt392_array_frame.tsv", ART / "gdt392_image_manifest.tsv", ART / "gdt392_review_image_hashes.tsv"]},
        "implementation": {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())},
        "claim_ceiling": "TEXT_BLIND_SPECIAL_CIRCLE_START_DIRECTION_ACQUISITION_ONLY",
    }
    freeze["content_hash"] = digest(freeze)
    (ART / "gdt392_pre_image_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], "frame": freeze["frame"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
