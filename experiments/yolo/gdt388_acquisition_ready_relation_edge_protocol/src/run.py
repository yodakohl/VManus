#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol"
ART = BASE / "artifacts"
P360 = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"
P337 = ROOT / "experiments/yolo/gdt337_external_homologue_census/artifacts/gdt337_result.json"
P372 = ROOT / "experiments/yolo/gdt372_external_prespecification_capacity/artifacts/gdt372_result.json"
P386 = ROOT / "experiments/yolo/gdt386_independent_relation_edge_capacity/artifacts/gdt386_result.json"
P387 = ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_result.json"

RELATION_CHANNELS = {
    "HUMAN_REL_ATTACHMENT",
    "HUMAN_REL_CONTACT",
    "HUMAN_REL_ENCLOSURE",
    "HUMAN_REL_ARRAY_GROUP",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def content_hash(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    annotation_rows = read_tsv(P360)
    assert all(not row["page"].startswith("f84") for row in annotation_rows)
    relation_rows = [row for row in annotation_rows if row["channel"] in RELATION_CHANNELS]
    positive_rows = [row for row in relation_rows if row["visual_state"] != "PROXIMITY_ONLY"]
    assert len(relation_rows) == 1059 and len({row["locus"] for row in relation_rows}) == 335
    assert len(positive_rows) == 95 and len({row["locus"] for row in positive_rows}) == 94

    page_frame_rows = []
    for page in sorted({row["page"] for row in annotation_rows}):
        page_rows = [row for row in annotation_rows if row["page"] == page]
        page_relation = [row for row in page_rows if row["channel"] in RELATION_CHANNELS]
        page_positive = [row for row in page_relation if row["visual_state"] != "PROXIMITY_ONLY"]
        folios = {row["physical_folio"] for row in page_rows}
        assert len(folios) == 1
        page_frame_rows.append(
            {
                "page": page,
                "physical_folio": next(iter(folios)),
                "annotation_rows": len(page_rows),
                "relation_rows": len(page_relation),
                "positive_relation_rows": len(page_positive),
                "channels": ";".join(sorted({row["channel"] for row in page_rows})),
                "review_scope": "COMPLETE_PAGE_CONNECTOR_CENSUS",
                "formal_access_state": "SEALED",
            }
        )
    assert len(page_frame_rows) == 61 and len({row["physical_folio"] for row in page_frame_rows}) == 30
    write_tsv(ART / "gdt388_page_frame.tsv", page_frame_rows)

    capacity_rows = []
    names = {
        "HUMAN_REL_ATTACHMENT": "LOCAL_LABEL_OBJECT_ATTACHMENT",
        "HUMAN_REL_CONTACT": "LOCAL_TEXT_DRAWING_CONTACT",
        "HUMAN_REL_ENCLOSURE": "LOCAL_TEXT_DRAWING_ENCLOSURE",
        "HUMAN_REL_ARRAY_GROUP": "LOCAL_ARRAY_OR_GROUP_MEMBERSHIP",
    }
    for channel in sorted(RELATION_CHANNELS):
        eligible = [row for row in relation_rows if row["channel"] == channel]
        positive = [row for row in eligible if row["visual_state"] != "PROXIMITY_ONLY"]
        unhedged = [row for row in positive if row["confidence"] == "UNHEDGED"]
        capacity_rows.append(
            {
                "endpoint_family": names[channel],
                "source_channel": channel,
                "catalogue_rows": len(eligible),
                "positive_relation_rows": len(positive),
                "positive_unique_loci": len({row["locus"] for row in positive}),
                "positive_folios": len({row["physical_folio"] for row in positive}),
                "unhedged_positive_rows": len(unhedged),
                "unhedged_positive_folios": len({row["physical_folio"] for row in unhedged}),
                "normalized_visual_target_ids": 0,
                "exact_target_loci": 0,
                "ordered_inscription_edges": 0,
                "relation_instrument_eligible": 0,
                "status": "LOCAL_GEOMETRY_ONLY",
                "reason": "The source records a local text-to-drawing state but no independent target inscription or ordered relation edge.",
            }
        )
    write_tsv(ART / "gdt388_relation_type_capacity.tsv", capacity_rows)

    g337 = json.loads(P337.read_text())
    g372 = json.loads(P372.read_text())
    g386 = json.loads(P386.read_text())
    g387 = json.loads(P387.read_text())
    assert g337["counts"]["special_circle_arrays"] == 45
    assert g337["counts"]["special_circle_folios"] == 7
    assert g386["viable_endpoints"] == 0
    assert g387["status"] == "CROSS_DOMAIN_PARENT_LINK_SIGNATURE_SUPPORTED"

    batch_rows = [
        {
            "priority": 1,
            "batch_id": "B01_AUTHORIAL_CONNECTOR_BETWEEN_LABELED_ENDPOINTS",
            "selection_frame": f"All {len(page_frame_rows)} f84-free pages on {len({row['physical_folio'] for row in page_frame_rows})} folios in gdt388_page_frame.tsv; select from visible connector geometry only.",
            "current_observations": 0,
            "current_folios": 0,
            "required_observations": 50,
            "required_folios": 5,
            "acquisition_action": "Locate every explicit arrow, line, duct, path, or pointer with separately localizable inscriptions at both ends; retain ambiguous direction as unresolved.",
            "fatal_exclusion": "Either endpoint lacks an exact locus; direction comes only from text order; target is reconstructible from layout; connector is merely proximity.",
            "status": "PRIMARY_NEW_ACQUISITION_REQUIRED",
        },
        {
            "priority": 2,
            "batch_id": "B02_LOCAL_TEXT_OBJECT_RELATION_NORMALIZATION",
            "selection_frame": "Complete existing attachment/contact/enclosure/array source units, not positive rows alone.",
            "current_observations": len(positive_rows),
            "current_folios": len({row["physical_folio"] for row in positive_rows}),
            "required_observations": 50,
            "required_folios": 5,
            "acquisition_action": "Normalize visual object IDs and explicit ownership/direction without opening formal identity; preserve hedged and proximity-only rows.",
            "fatal_exclusion": "Do not treat a visual object ID as a manuscript target locus or import this batch into the parent-link score.",
            "status": "USEFUL_SEPARATE_ENDPOINT_NOT_PARENT_LINK",
        },
        {
            "priority": 3,
            "batch_id": "B03_CROSS_PAGE_REFERENT_DIRECTION_UPGRADE",
            "selection_frame": "All 40 frozen human-nominated cross-page referent pairs.",
            "current_observations": g386["counts"]["cross_page_referent_pairs"],
            "current_folios": 40,
            "required_observations": 50,
            "required_folios": 5,
            "acquisition_action": "Seek a source-authored or externally fixed direction and singular endpoint locus for both members; same/similar drawing alone is insufficient.",
            "fatal_exclusion": "Researcher chooses direction from Voynich text, recurrence, or desired prediction.",
            "status": "BLOCKED_ZERO_ORDERED_EDGES",
        },
        {
            "priority": 4,
            "batch_id": "B04_SPECIAL_CIRCLE_POINTER_CENSUS",
            "selection_frame": f"All {g337['counts']['special_circle_arrays']} frozen text-blind arrays on {g337['counts']['special_circle_folios']} physical folios.",
            "current_observations": g337["counts"]["special_circle_arrays"],
            "current_folios": g337["counts"]["special_circle_folios"],
            "required_observations": 50,
            "required_folios": 5,
            "acquisition_action": "Record only author-visible pointer/start/direction relations to separately owned labels; do not infer cyclic order from catalogue order.",
            "fatal_exclusion": "Radial adjacency, center-spoke geometry, rotation, or array ordinal uniquely determines the nominated target.",
            "status": "BLOCKED_ZERO_AUTHORIAL_START_DIRECTION",
        },
        {
            "priority": 5,
            "batch_id": "B05_Q20_INTER_RECORD_POINTER_CENSUS",
            "selection_frame": "All 170 star-defined records on eight f84-free physical folios.",
            "current_observations": g386["counts"]["q20_records"],
            "current_folios": g386["counts"]["q20_physical_folios"],
            "required_observations": 50,
            "required_folios": 5,
            "acquisition_action": "Record an edge only if an author-visible device independently points from one complete record/star to another.",
            "fatal_exclusion": "OPEN/BODY membership, physical order, shared star rendering, or tuple recurrence supplies the target.",
            "status": "BLOCKED_ZERO_INTER_RECORD_POINTERS",
        },
    ]
    write_tsv(ART / "gdt388_acquisition_batches.tsv", batch_rows)

    gates = [
        ("G01_FORMAL_SEAL", "No Voynich surface/family/tuple identity is opened during acquisition.", 1, "Only f84-free annotation and compact result artifacts were read."),
        ("G02_EXACT_PIVOT", "Every retained edge has one exact pivot manuscript locus.", 0, "No new edge rows have been acquired."),
        ("G03_EXACT_TARGET", "Every retained edge has one exact target manuscript locus independent of the pivot.", 0, "Current local geometry has zero exact target loci."),
        ("G04_FIXED_DIRECTION", "Direction follows an authorial pointer, external order, or source-authored ownership rule.", 0, "Current cross-page and local relations are unordered for this purpose."),
        ("G05_SINGULAR_OWNERSHIP", "Both endpoint ownership mappings are singular; proximity is not ownership.", 0, "No normalized endpoint pair currently satisfies this."),
        ("G06_GRAMMAR_INDEPENDENCE", "Target identity cannot be reconstructed from tuple recurrence, placement, boundaries, or predictor features.", 0, "No current edge survives the previous gates."),
        ("G07_EDGE_CAPACITY", "At least 50 eligible directed edges exist.", 0, "Current eligible count is zero."),
        ("G08_FOLIO_CAPACITY", "Eligible edges span at least five physical folios with a preassigned held-folio split.", 0, "Current eligible folio count is zero."),
        ("G09_MOBILE_NULL", "At least one matched alternative target remains mobile for every scored pivot.", 0, "Cannot be evaluated before acquisition."),
    ]
    gate_rows = [
        {"gate_id": gate_id, "acceptance_rule": rule, "current_pass": passed, "current_evidence": evidence}
        for gate_id, rule, passed, evidence in gates
    ]
    write_tsv(ART / "gdt388_acquisition_gates.tsv", gate_rows)

    schema_fields = [
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
        "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
        "source_aware_localizer", "relation_reviewer", "relation_confidence", "ambiguity_state",
        "formal_access_state", "fold_assignment", "eligibility_status",
    ]
    write_tsv(ART / "gdt388_edge_packet_template.tsv", [], schema_fields)

    outputs = [
        ART / "gdt388_page_frame.tsv",
        ART / "gdt388_relation_type_capacity.tsv",
        ART / "gdt388_acquisition_batches.tsv",
        ART / "gdt388_acquisition_gates.tsv",
        ART / "gdt388_edge_packet_template.tsv",
    ]
    result = {
        "schema": "GDT388_RESULT_V1",
        "status": "ACQUISITION_PROTOCOL_FROZEN_ZERO_ELIGIBLE_CURRENT_EDGES",
        "current_capacity": {
            "local_relation_catalogue_rows": len(relation_rows),
            "local_relation_unique_loci": len({row["locus"] for row in relation_rows}),
            "local_relation_folios": len({row["physical_folio"] for row in relation_rows}),
            "positive_local_relation_rows": len(positive_rows),
            "positive_local_relation_unique_loci": len({row["locus"] for row in positive_rows}),
            "positive_local_relation_folios": len({row["physical_folio"] for row in positive_rows}),
            "unhedged_positive_rows": sum(row["confidence"] == "UNHEDGED" for row in positive_rows),
            "independent_ordered_target_edges": 0,
            "independent_ordered_target_folios": 0,
        },
        "positive_state_counts": dict(sorted(Counter(row["visual_state"] for row in positive_rows).items())),
        "acquisition": {
            "primary_batch": "B01_AUTHORIAL_CONNECTOR_BETWEEN_LABELED_ENDPOINTS",
            "minimum_edges": 50,
            "minimum_physical_folios": 5,
            "max_externally_frozen_comparisons": 3,
            "frozen_page_frame_pages": len(page_frame_rows),
            "frozen_page_frame_folios": len({row["physical_folio"] for row in page_frame_rows}),
            "power_note": "GDT372 favors approximately one to three externally frozen comparisons and still requires a matched null; the larger 12-discovery plus 4-held design is a planning target, not a claim that 50 edges alone confirms anything.",
            "scoring_authorized": False,
        },
        "source_access": {
            "voynich_images_opened": False,
            "voynich_formal_rows_read": 0,
            "voynich_text_identities_read": 0,
            "new_visual_observations": 0,
            "f84_opened_parsed_retained_or_scored": False,
        },
        "gdt372_gate": g372["gate"],
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [P360, P337, P372, P386, P387]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs},
        "implementation": {
            str((BASE / rel).relative_to(ROOT)): sha(BASE / rel)
            for rel in ["src/run.py", "src/validate.py"]
        },
        "claim_ceiling": "TEXT_BLIND_ACQUISITION_PROTOCOL_AND_CAPACITY_ONLY",
    }
    result["content_hash"] = content_hash(result)
    (ART / "gdt388_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "current_capacity": result["current_capacity"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
