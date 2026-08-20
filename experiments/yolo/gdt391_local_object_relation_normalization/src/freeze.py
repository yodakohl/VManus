#!/usr/bin/env python3
"""Freeze the complete-unit GDT391 text-object normalization frame."""
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
BASE = ROOT / "experiments/yolo/gdt391_local_object_relation_normalization"
ART = BASE / "artifacts"
SOURCE = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"
PRIOR = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"
FRAME = ART / "gdt391_complete_unit_frame.tsv"
FREEZE = ART / "gdt391_pre_normalization_freeze.json"

RELATION_CHANNELS = {
    "HUMAN_REL_ATTACHMENT": "REL_EXPLICIT_ATTACHMENT",
    "HUMAN_REL_CONTACT": "REL_OVERLAP_OR_CONTACT",
    "HUMAN_REL_ENCLOSURE": "REL_ENCLOSURE",
    "HUMAN_REL_ARRAY_GROUP": "REL_ARRAY_OR_GROUP",
}
STRONG = set(RELATION_CHANNELS.values())
PREFIX_FIELDS = [
    "case_id", "channel", "visual_state", "page", "physical_folio", "locus",
    "array_id", "provenance", "source_id", "confidence", "evidence_family",
    "evidence_lineage", "evidence_cluster", "visual_detail",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_relation_prefix() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader([handle.readline()], delimiter="\t"))
        assert header[: len(PREFIX_FIELDS)] == PREFIX_FIELDS
        channel_index = header.index("channel")
        page_index = header.index("page")
        for raw in handle:
            cells = raw.rstrip("\n").split("\t")
            channel = cells[channel_index]
            if channel not in RELATION_CHANNELS:
                continue
            page = cells[page_index]
            if page.lower().startswith("f84"):
                raise RuntimeError("forbidden selector reached retained relation frame")
            # Later formal-coverage fields are never assigned, parsed, retained, or displayed.
            rows.append(dict(zip(PREFIX_FIELDS, cells[: len(PREFIX_FIELDS)], strict=True)))
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    rows = read_relation_prefix()
    by_locus: dict[str, dict[str, object]] = {}
    for row in rows:
        locus = row["locus"]
        entry = by_locus.setdefault(
            locus,
            {
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "array_id": row["array_id"],
                "provenance": row["provenance"],
                "source_id": row["source_id"],
                "confidence": row["confidence"],
                "evidence_lineage": row["evidence_lineage"],
                "visual_detail": row["visual_detail"],
                "states": set(),
                "channels": set(),
            },
        )
        for key in ["page", "physical_folio", "array_id", "provenance", "source_id", "confidence", "evidence_lineage", "visual_detail"]:
            assert entry[key] == row[key]
        entry["states"].add(row["visual_state"])
        entry["channels"].add(row["channel"])

    strong_loci = {locus for locus, row in by_locus.items() if row["states"] & STRONG}
    positive_units = {str(by_locus[locus]["array_id"]) for locus in strong_loci}
    complete = {locus: row for locus, row in by_locus.items() if row["array_id"] in positive_units}
    unit_order = sorted(positive_units, key=lambda value: hashlib.sha256(("GDT391_UNIT_ORDER_V1|" + value).encode()).hexdigest())
    locus_order = sorted(complete, key=lambda value: hashlib.sha256(("GDT391_LOCUS_ORDER_V1|" + value).encode()).hexdigest())
    unit_index = {unit: index + 1 for index, unit in enumerate(unit_order)}

    output: list[dict[str, object]] = []
    for review_index, locus in enumerate(locus_order, 1):
        row = complete[locus]
        strong_states = sorted(row["states"] & STRONG)
        state = ";".join(strong_states) if strong_states else "PROXIMITY_ONLY"
        output.append(
            {
                "review_index": review_index,
                "unit_review_index": unit_index[str(row["array_id"])],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "array_id": row["array_id"],
                "source_relation_state": state,
                "source_confidence": row["confidence"],
                "source_visual_detail": row["visual_detail"],
                "source_provenance": row["provenance"],
                "source_id": row["source_id"],
                "evidence_lineage": row["evidence_lineage"],
                "formal_identity_access_state": "SEALED",
            }
        )

    with FRAME.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    unit_counts = Counter(str(row["array_id"]) for row in complete.values())
    unit_positive_counts = Counter(str(complete[locus]["array_id"]) for locus in strong_loci)
    mixed_units = [unit for unit in positive_units if 0 < unit_positive_counts[unit] < unit_counts[unit]]
    pages = sorted({str(row["page"]) for row in complete.values()})
    folios = sorted({str(row["physical_folio"]) for row in complete.values()})
    frame = {
        "schema": "GDT391_PRE_NORMALIZATION_FREEZE_V1",
        "status": "FROZEN_BEFORE_OBJECT_NORMALIZATION",
        "selection": {
            "rule": "ALL_LOCUS_ROWS_IN_EVERY_SOURCE_ARRAY_ID_CONTAINING_AT_LEAST_ONE_STRONG_HUMAN_RELATION",
            "strong_states": sorted(STRONG),
            "proximity_rows_retained": True,
            "hedged_rows_retained": True,
            "formal_coverage_suffix_fields_parsed_retained_or_displayed": False,
        },
        "frame": {
            "source_relation_rows": len(rows),
            "unique_source_loci": len(by_locus),
            "positive_unique_loci": len(strong_loci),
            "positive_source_units": len(positive_units),
            "complete_unit_loci": len(complete),
            "pages": len(pages),
            "physical_folios": len(folios),
            "mixed_relation_units": len(mixed_units),
            "mixed_relation_folios": len({str(row["physical_folio"]) for row in complete.values() if row["array_id"] in mixed_units}),
            "pages_allowlist": pages,
            "folios_allowlist": folios,
            "unit_review_order": unit_order,
            "locus_review_order": locus_order,
        },
        "normalization_states": [
            "SINGULAR_OBJECT_LOCALIZED",
            "MULTIPLE_OR_ALTERNATIVE_OBJECTS",
            "OBJECT_REGION_NOT_INDIVIDUATED",
            "NO_RELATION_BEYOND_PROXIMITY",
            "UNRESOLVED_OR_UNREVIEWABLE",
        ],
        "relation_geometry_states": [
            "ON_OR_ATTACHED",
            "CONTACT_OR_OVERLAP",
            "INSIDE_BOUNDED_REGION",
            "ARRAY_OR_GROUP_MEMBER",
            "PROXIMITY_ONLY",
            "AMBIGUOUS_OR_MULTIPLE",
        ],
        "neutral_object_topologies": [
            "DISCRETE_POINT_OR_STARLIKE_OBJECT",
            "BOUNDED_REGION_OR_COMPARTMENT",
            "LINEAR_CONTOUR_OR_STROKE",
            "PLANT_OR_FIGURE_DRAWING_UNIT",
            "ARRAY_OR_GROUP_REGION",
            "OTHER_OR_UNRESOLVED",
        ],
        "eligibility": {
            "singular_neutral_object_id": True,
            "relation_visible_or_explicitly_source_owned": True,
            "positive_relation_not_proximity_only": True,
            "same_unit_matched_comparator_mobile": True,
            "minimum_singular_positive_relations": 50,
            "minimum_physical_folios": 5,
            "minimum_mixed_units": 10,
        },
        "scoring_authorized": False,
        "reviewer_provenance": "SOURCE_AWARE_SINGLE_AI_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
        "access": {
            "voynich_surface_or_formal_identity_access": False,
            "image_access_after_this_freeze": False,
            "prior_repository_page_exposure_disclosed": True,
            "f84_access": False,
        },
        "inputs": {
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
            str(PRIOR.relative_to(ROOT)): sha(PRIOR),
        },
        "outputs": {str(FRAME.relative_to(ROOT)): sha(FRAME)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "claim_ceiling": "TEXT_BLIND_LOCAL_TEXT_OBJECT_GEOMETRY_OWNERSHIP_AND_CAPACITY_ONLY",
    }
    frame["content_hash"] = digest(frame)
    FREEZE.write_text(json.dumps(frame, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": frame["status"], "frame": {key: value for key, value in frame["frame"].items() if not key.endswith("allowlist") and not key.endswith("order")}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
