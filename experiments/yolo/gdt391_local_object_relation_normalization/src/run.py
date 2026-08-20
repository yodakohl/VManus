#!/usr/bin/env python3
"""Materialize the frozen GDT391 source-aware object normalization census."""
from __future__ import annotations

import csv
import hashlib
import json
import re
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
FRAME = ART / "gdt391_complete_unit_frame.tsv"
FREEZE = ART / "gdt391_pre_normalization_freeze.json"
IMAGE_MANIFEST = ART / "gdt391_image_manifest.tsv"
IMAGE_HASHES = ART / "gdt391_review_image_hashes.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def object_id(page: str, reference: str) -> str:
    return "G391_OBJ_" + hashlib.sha256((page + "|" + reference).encode()).hexdigest()[:12].upper()


# The source description nominates one visibly individuated object/region in
# these cases.  IDs remain opaque; the reference is retained only for audit.
SINGULAR: dict[str, tuple[str, str, str]] = {
    "f58r.1": ("SOURCE_STAR_TAIL_AT_FIRST_PARAGRAPH", "LINEAR_CONTOUR_OR_STROKE", "CONTACT_OR_OVERLAP"),
    "f67r2.48": ("SOURCE_SECTOR_08_30", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f67v2.2": ("SOURCE_NORTHEAST_CIRCLE", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f67v2.22": ("SOURCE_SOUTHEAST_CIRCLE", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f68r1.5": ("SOURCE_TOP_MEDALLION", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f68r1.6": ("SOURCE_TOP_MEDALLION", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f68r1.7": ("SOURCE_TOP_MEDALLION", "BOUNDED_REGION_OR_COMPARTMENT", "INSIDE_BOUNDED_REGION"),
    "f82r.10": ("SOURCE_CROSS_SHAPED_TUBE", "LINEAR_CONTOUR_OR_STROKE", "ON_OR_ATTACHED"),
    "f82v.3": ("SOURCE_NORTH_POOL", "BOUNDED_REGION_OR_COMPARTMENT", "ON_OR_ATTACHED"),
    "f82v.45": ("SOURCE_EAST_POOL_WITH_WATERFALL", "BOUNDED_REGION_OR_COMPARTMENT", "ON_OR_ATTACHED"),
    "f100r.10": ("SOURCE_DRAWING_UNIT_2_6", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
    "f102v2.18": ("SOURCE_DRAWING_UNIT_2_7", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
    "f89r2.33": ("SOURCE_DRAWING_UNIT_4_4", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
    "f99v.20": ("SOURCE_DRAWING_UNIT_1_8", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
    "f99v.32": ("SOURCE_DRAWING_UNIT_4_1", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
    "f99v.35": ("SOURCE_DRAWING_UNIT_4_1", "PLANT_OR_FIGURE_DRAWING_UNIT", "CONTACT_OR_OVERLAP"),
}

# Proximity-only rows with a single non-drawing reference not recoverable from
# the square-bracket source notation.
PROX_SPECIAL: dict[str, tuple[str, str]] = {
    "f67r2.24": ("SOURCE_SECTOR_00_30", "BOUNDED_REGION_OR_COMPARTMENT"),
    "f67r2.44": ("SOURCE_SECTOR_07_30", "BOUNDED_REGION_OR_COMPARTMENT"),
    "f82v.1": ("SOURCE_NORTHWEST_FIGURE", "PLANT_OR_FIGURE_DRAWING_UNIT"),
    "f82v.2": ("SOURCE_NORTH_FIGURE", "PLANT_OR_FIGURE_DRAWING_UNIT"),
    "f82v.42": ("SOURCE_UPPER_CURVED_CHANNEL", "LINEAR_CONTOUR_OR_STROKE"),
    "f82v.43": ("SOURCE_UPPER_CURVED_CHANNEL", "LINEAR_CONTOUR_OR_STROKE"),
    "f82v.46": ("SOURCE_FIGURE_2", "PLANT_OR_FIGURE_DRAWING_UNIT"),
    "f82v.48": ("SOURCE_LOWER_CURVED_CHANNEL", "LINEAR_CONTOUR_OR_STROKE"),
    "f100r.7": ("SOURCE_DRAWING_UNIT_2_2", "PLANT_OR_FIGURE_DRAWING_UNIT"),
}


def add_star_singular(frame: list[dict[str, str]]) -> None:
    for row in frame:
        if row["array_id"] in {"f68r1:S1", "f68r2:S1"}:
            SINGULAR[row["locus"]] = (
                "SOURCE_NAMED_STAR_FOR_" + row["locus"].replace(".", "_"),
                "DISCRETE_POINT_OR_STARLIKE_OBJECT",
                "ON_OR_ATTACHED",
            )


def one_square_reference(detail: str) -> str:
    refs = []
    for match in re.findall(r"<([^<>]+)>\[([^\]]+)\]", detail):
        ref = f"{match[0]}[{match[1]}]"
        if ref not in refs:
            refs.append(ref)
    return refs[0] if len(refs) == 1 else ""


def main() -> int:
    frame = tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    mappings = tsv(IMAGE_MANIFEST)
    image_hashes = tsv(IMAGE_HASHES)
    assert len(frame) == 180 and [row["locus"] for row in frame] == freeze["frame"]["locus_review_order"]
    assert {row["page"] for row in frame} == set(freeze["frame"]["pages_allowlist"])
    assert all(not row["page"].lower().startswith("f84") for row in frame)
    assert len({row["canvas_id"] for row in mappings}) == len(image_hashes) == 20
    assert all("84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mappings)
    add_star_singular(frame)

    page_canvases: dict[str, list[str]] = defaultdict(list)
    for row in mappings:
        page_canvases[row["page"]].append(row["canvas_id"])

    page_rows = []
    for index, page in enumerate(freeze["frame"]["pages_allowlist"], 1):
        page_rows.append(
            {
                "page_review_index": index,
                "page": page,
                "physical_folio": next(row["physical_folio"] for row in frame if row["page"] == page),
                "canvas_ids": ";".join(sorted(set(page_canvases[page]))),
                "complete_page_review_state": "REVIEWED_SOURCE_AWARE",
                "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
                "automated_visual_method": "NONE",
                "formal_identity_access_state": "SEALED",
            }
        )
    write(ART / "gdt391_page_review.tsv", page_rows)

    observations: list[dict[str, object]] = []
    for row in frame:
        locus = row["locus"]
        source_state = row["source_relation_state"]
        strong = source_state != "PROXIMITY_ONLY"
        reference = ""
        topology = "OTHER_OR_UNRESOLVED"
        normalized_relation = "AMBIGUOUS_OR_MULTIPLE"
        localization_state = "MULTIPLE_OR_ALTERNATIVE_OBJECTS"
        basis = "SOURCE_DESCRIPTION_RETAINS_AMBIGUOUS_OWNER_OR_RELATION"
        singular_positive = 0

        if locus in SINGULAR:
            reference, topology, normalized_relation = SINGULAR[locus]
            localization_state = "SINGULAR_OBJECT_LOCALIZED"
            basis = "SOURCE_EXACT_OBJECT_NOMINATION_CONSISTENT_WITH_COMPLETE_PAGE_GEOMETRY"
            singular_positive = 1
        elif not strong:
            if locus in PROX_SPECIAL:
                reference, topology = PROX_SPECIAL[locus]
            else:
                reference = one_square_reference(row["source_visual_detail"])
                if reference:
                    topology = "PLANT_OR_FIGURE_DRAWING_UNIT"
            normalized_relation = "PROXIMITY_ONLY"
            if reference:
                localization_state = "SINGULAR_OBJECT_LOCALIZED"
                basis = "SOURCE_NOMINATED_SINGLE_NEARBY_OBJECT_WITHOUT_OWNERSHIP"
            elif "between" in row["source_visual_detail"].lower() or "aligned" in row["source_visual_detail"].lower():
                localization_state = "MULTIPLE_OR_ALTERNATIVE_OBJECTS"
                basis = "SOURCE_DESCRIPTION_NAMES_MULTIPLE_OR_ALIGNMENT_ONLY"
            else:
                localization_state = "NO_RELATION_BEYOND_PROXIMITY"
                basis = "NO_SINGULAR_SOURCE_OBJECT_REFERENCE"
        elif "REL_ARRAY_OR_GROUP" in source_state:
            localization_state = "OBJECT_REGION_NOT_INDIVIDUATED"
            topology = "ARRAY_OR_GROUP_REGION"
            basis = "HEDGED_SOURCE_GROUP_OR_SEGMENTATION_ASSERTION_WITHOUT_SINGULAR_OWNER"
        elif locus == "f68r1.3":
            localization_state = "OBJECT_REGION_NOT_INDIVIDUATED"
            topology = "OTHER_OR_UNRESOLVED"
            basis = "TEXT_RUNS_INTO_DIAGRAM_REGION_WITHOUT_INDIVIDUATED_OBJECT"

        normalized_id = object_id(row["page"], reference) if reference else ""
        observations.append(
            {
                "review_index": row["review_index"],
                "unit_review_index": row["unit_review_index"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "array_id": row["array_id"],
                "source_relation_state": source_state,
                "source_confidence": row["source_confidence"],
                "object_localization_state": localization_state,
                "normalized_relation_geometry": normalized_relation,
                "neutral_object_topology": topology,
                "normalized_object_id": normalized_id,
                "source_object_reference": reference,
                "singular_positive_relation": singular_positive,
                "matched_same_unit_comparator_available": 0,
                "later_score_eligibility": "INELIGIBLE_PENDING_COMPARATOR_CHECK" if singular_positive else "INELIGIBLE_NOT_SINGULAR_POSITIVE",
                "normalization_basis": basis,
                "canvas_ids": ";".join(sorted(set(page_canvases[row["page"]]))),
                "reviewer_provenance": "SINGLE_AI_SOURCE_AWARE_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
                "formal_identity_access_state": "SEALED",
            }
        )

    by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in observations:
        by_unit[str(row["array_id"])].append(row)
    for row in observations:
        if not row["singular_positive_relation"]:
            continue
        comparators = [
            other
            for other in by_unit[str(row["array_id"])]
            if other["normalized_relation_geometry"] == "PROXIMITY_ONLY"
            and other["object_localization_state"] == "SINGULAR_OBJECT_LOCALIZED"
            and other["neutral_object_topology"] == row["neutral_object_topology"]
        ]
        if comparators:
            row["matched_same_unit_comparator_available"] = 1
            row["later_score_eligibility"] = "ELIGIBLE_LOCAL_RELATION_WITHIN_UNIT_MATCH"
        else:
            row["later_score_eligibility"] = "INELIGIBLE_NO_SAME_UNIT_TOPOLOGY_MATCH"

    write(ART / "gdt391_normalized_object_relations.tsv", observations)
    eligible = [row for row in observations if row["later_score_eligibility"] == "ELIGIBLE_LOCAL_RELATION_WITHIN_UNIT_MATCH"]
    eligible_units = {str(row["array_id"]) for row in eligible}
    eligible_folios = {str(row["physical_folio"]) for row in eligible}
    singular = [row for row in observations if row["singular_positive_relation"]]
    state_counts = Counter(str(row["object_localization_state"]) for row in observations)
    relation_counts = Counter(str(row["normalized_relation_geometry"]) for row in observations)

    gates = [
        ("G01_FORMAL_SEAL", 1, "No Voynich surface, family, PAGE_HOST, tuple, or renderer identity was read or scored."),
        ("G02_COMPLETE_UNIT_FRAME", 1, "All 180 loci in the 44 frozen source units were normalized."),
        ("G03_SINGULAR_POSITIVE_RELATIONS", int(len(singular) >= 50), f"{len(singular)} singular positive relations versus minimum 50."),
        ("G04_POSITIVE_FOLIOS", int(len({row['physical_folio'] for row in singular}) >= 5), f"{len({row['physical_folio'] for row in singular})} singular-positive folios versus minimum five."),
        ("G05_MATCHED_ELIGIBLE_RELATIONS", int(len(eligible) >= 50), f"{len(eligible)} positives retain a same-unit topology-matched singular proximity comparator versus minimum 50."),
        ("G06_MIXED_ELIGIBLE_UNITS", int(len(eligible_units) >= 10), f"{len(eligible_units)} eligible mixed units versus minimum ten."),
        ("G07_ELIGIBLE_FOLIOS", int(len(eligible_folios) >= 5), f"{len(eligible_folios)} eligible folios versus minimum five."),
    ]
    gate_rows = [{"gate_id": gate_id, "current_pass": passed, "evidence": evidence} for gate_id, passed, evidence in gates]
    write(ART / "gdt391_capacity_gates.tsv", gate_rows)
    write(ART / "gdt391_eligible_relation_packet.tsv", eligible, list(observations[0]))

    access = {
        "schema": "GDT391_ACCESS_V1",
        "pages_reviewed": 21,
        "official_yale_canvases_reviewed": 20,
        "frozen_loci_normalized": 180,
        "direct_visual_reviewer_count": 1,
        "direct_visual_reviewer_type": "AI_SOURCE_AWARE_EXPLORATORY_NOT_HUMAN_OR_CONFIRMATORY",
        "prior_page_exposure_disclosed": True,
        "ocr_calls": 0,
        "automated_image_classification_calls": 0,
        "clip_embedding_caption_calls": 0,
        "formal_identity_rows_read": 0,
        "voynich_surface_strings_read": 0,
        "f84_image_transcription_source_group_formal_identity_prediction_or_score_access": False,
    }
    access["content_hash"] = digest(access)
    (ART / "gdt391_access_log.json").write_text(json.dumps(access, indent=2, sort_keys=True) + "\n")

    output_paths = [
        ART / "gdt391_page_review.tsv",
        ART / "gdt391_normalized_object_relations.tsv",
        ART / "gdt391_eligible_relation_packet.tsv",
        ART / "gdt391_capacity_gates.tsv",
        ART / "gdt391_access_log.json",
    ]
    result = {
        "schema": "GDT391_RESULT_V1",
        "status": "NORMALIZATION_SUCCEEDS_BUT_MATCHED_RELATION_CAPACITY_FAILS",
        "counts": {
            "complete_unit_loci": len(observations),
            "source_units": len(by_unit),
            "pages_reviewed": len(page_rows),
            "physical_folios": len({row["physical_folio"] for row in observations}),
            "official_canvases": len(image_hashes),
            "singular_positive_relations": len(singular),
            "singular_positive_folios": len({row["physical_folio"] for row in singular}),
            "eligible_matched_positive_relations": len(eligible),
            "eligible_mixed_units": len(eligible_units),
            "eligible_folios": len(eligible_folios),
            "object_localization_states": dict(sorted(state_counts.items())),
            "normalized_relation_states": dict(sorted(relation_counts.items())),
        },
        "capacity": {
            "minimum_singular_positive_relations": 50,
            "minimum_physical_folios": 5,
            "minimum_mixed_units": 10,
            "all_gates_pass": all(passed for _, passed, _ in gates),
            "later_formal_scoring_authorized": False,
        },
        "interpretation": "The source-aware census can normalize a substantial singular relation layer, dominated by f68 star attachments, but only a small subset retains same-unit topology-matched proximity controls. The separate local text-object route is not identifiable at the frozen matched-comparator capacity.",
        "review": {
            "provenance": "SINGLE_AI_SOURCE_AWARE_EXPLORATORY_WITH_PRIOR_PAGE_EXPOSURE",
            "complete_frame": True,
            "automated_visual_judgments": 0,
        },
        "access": access,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [FRAME, FREEZE, IMAGE_MANIFEST, IMAGE_HASHES]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in output_paths},
        "implementation": {str((BASE / path).relative_to(ROOT)): sha(BASE / path) for path in ["src/prepare_review.py", "src/run.py"]},
        "claim_ceiling": "TEXT_BLIND_LOCAL_TEXT_OBJECT_GEOMETRY_OWNERSHIP_AND_CAPACITY_ONLY",
    }
    result["content_hash"] = digest(result)
    (ART / "gdt391_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
