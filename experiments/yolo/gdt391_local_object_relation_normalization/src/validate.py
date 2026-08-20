#!/usr/bin/env python3
"""Independent artifact/accounting validator for GDT391.

The validator does not independently reproduce source-aware visual ownership
judgments.  It reconstructs frame coverage, normalized IDs, matched-comparator
eligibility, capacity, access assertions, and hashes.
"""
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
FRAME = ART / "gdt391_complete_unit_frame.tsv"
FREEZE = ART / "gdt391_pre_normalization_freeze.json"
MAPPING = ART / "gdt391_image_manifest.tsv"
IMAGE_HASHES = ART / "gdt391_review_image_hashes.tsv"
PAGES = ART / "gdt391_page_review.tsv"
OBS = ART / "gdt391_normalized_object_relations.tsv"
ELIGIBLE = ART / "gdt391_eligible_relation_packet.tsv"
GATES = ART / "gdt391_capacity_gates.tsv"
ACCESS = ART / "gdt391_access_log.json"
RESULT = ART / "gdt391_result.json"
OUT = ART / "gdt391_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    frame = tsv(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    mapping = tsv(MAPPING)
    image_hashes = tsv(IMAGE_HASHES)
    pages = tsv(PAGES)
    observations = tsv(OBS)
    eligible = tsv(ELIGIBLE)
    gates = tsv(GATES)
    access = json.loads(ACCESS.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    frame_loci = {row["locus"] for row in frame}
    check("frame_180_unique", len(frame) == len(frame_loci) == 180, len(frame))
    check("frame_44_units", len({row["array_id"] for row in frame}) == 44, "44")
    check("frame_21_pages_12_folios", len({row["page"] for row in frame}) == 21 and len({row["physical_folio"] for row in frame}) == 12, "21/12")
    check("frame_frozen_order", [row["locus"] for row in frame] == freeze["frame"]["locus_review_order"], frame[:2])
    check("all_inputs_no_forbidden_selector", all(not row["page"].lower().startswith("f84") for row in frame + mapping + pages + observations + eligible), "zero f84")
    check("mapping_exact_pages", {row["page"] for row in mapping} == {row["page"] for row in frame}, len(mapping))
    check("mapping_20_canvases", len({row["canvas_id"] for row in mapping}) == len(image_hashes) == 20, "20")
    check("mapping_safe_labels", all("84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mapping), "safe")
    check("image_hash_shapes", all(len(row["sha256"]) == 64 and int(row["pixel_width"]) > 0 and int(row["pixel_height"]) > 0 for row in image_hashes), "valid")
    check("page_review_complete", len(pages) == 21 and {row["page"] for row in pages} == {row["page"] for row in frame}, len(pages))
    check("page_review_states", {row["complete_page_review_state"] for row in pages} == {"REVIEWED_SOURCE_AWARE"}, "reviewed")
    check("page_no_automated_vision", {row["automated_visual_method"] for row in pages} == {"NONE"}, "NONE")

    check("observations_complete_unique", len(observations) == len({row["locus"] for row in observations}) == 180 and {row["locus"] for row in observations} == frame_loci, len(observations))
    check("observations_frozen_order", [row["locus"] for row in observations] == freeze["frame"]["locus_review_order"], observations[:2])
    frame_by_locus = {row["locus"]: row for row in frame}
    check("observation_source_metadata_exact", all(tuple(row[key] for key in ["page", "physical_folio", "array_id", "source_relation_state", "source_confidence"]) == tuple(frame_by_locus[row["locus"]][key] for key in ["page", "physical_folio", "array_id", "source_relation_state", "source_confidence"]) for row in observations), "exact")
    check(
        "observation_id_integrity",
        all(
            (
                row["normalized_object_id"]
                == "G391_OBJ_"
                + hashlib.sha256((row["page"] + "|" + row["source_object_reference"]).encode()).hexdigest()[:12].upper()
            )
            if row["source_object_reference"]
            else not row["normalized_object_id"]
            for row in observations
        ),
        "exact",
    )
    check("observation_formal_seal", {row["formal_identity_access_state"] for row in observations} == {"SEALED"}, "SEALED")
    check("proximity_not_positive", all(row["singular_positive_relation"] == "0" for row in observations if row["normalized_relation_geometry"] == "PROXIMITY_ONLY"), "zero")
    check("positive_implies_singular_id", all(row["object_localization_state"] == "SINGULAR_OBJECT_LOCALIZED" and row["normalized_object_id"] for row in observations if row["singular_positive_relation"] == "1"), "exact")

    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in observations:
        by_unit[row["array_id"]].append(row)
    reconstructed = []
    for row in observations:
        if row["singular_positive_relation"] != "1":
            continue
        comparators = [other for other in by_unit[row["array_id"]] if other["normalized_relation_geometry"] == "PROXIMITY_ONLY" and other["object_localization_state"] == "SINGULAR_OBJECT_LOCALIZED" and other["neutral_object_topology"] == row["neutral_object_topology"]]
        expected = bool(comparators)
        check("matched_flag_" + row["locus"], (row["matched_same_unit_comparator_available"] == "1") == expected, len(comparators))
        if expected:
            reconstructed.append(row)
    check("eligible_packet_exact", [row["locus"] for row in eligible] == [row["locus"] for row in reconstructed], len(eligible))
    check("eligible_status_exact", all(row["later_score_eligibility"] == "ELIGIBLE_LOCAL_RELATION_WITHIN_UNIT_MATCH" for row in eligible), "exact")

    singular = [row for row in observations if row["singular_positive_relation"] == "1"]
    eligible_units = {row["array_id"] for row in eligible}
    eligible_folios = {row["physical_folio"] for row in eligible}
    gate_map = {row["gate_id"]: int(row["current_pass"]) for row in gates}
    check("seven_gates", len(gate_map) == 7, len(gate_map))
    expected_pass = {
        "G01_FORMAL_SEAL": 1,
        "G02_COMPLETE_UNIT_FRAME": 1,
        "G03_SINGULAR_POSITIVE_RELATIONS": int(len(singular) >= 50),
        "G04_POSITIVE_FOLIOS": int(len({row['physical_folio'] for row in singular}) >= 5),
        "G05_MATCHED_ELIGIBLE_RELATIONS": int(len(eligible) >= 50),
        "G06_MIXED_ELIGIBLE_UNITS": int(len(eligible_units) >= 10),
        "G07_ELIGIBLE_FOLIOS": int(len(eligible_folios) >= 5),
    }
    check("gate_decisions_reconstruct", gate_map == expected_pass, gate_map)

    check("access_content_hash", access["content_hash"] == digest(access), access["content_hash"])
    check("access_counts", access["pages_reviewed"] == 21 and access["official_yale_canvases_reviewed"] == 20 and access["frozen_loci_normalized"] == 180, access)
    check("access_no_automated_or_formal", access["ocr_calls"] == access["automated_image_classification_calls"] == access["clip_embedding_caption_calls"] == access["formal_identity_rows_read"] == access["voynich_surface_strings_read"] == 0, "zero")
    check("access_no_new_forbidden", access["f84_image_transcription_source_group_formal_identity_prediction_or_score_access"] is False, False)

    check("result_content_hash", result["content_hash"] == digest(result), result["content_hash"])
    check("result_status", result["status"] == "NORMALIZATION_SUCCEEDS_BUT_MATCHED_RELATION_CAPACITY_FAILS", result["status"])
    counts = result["counts"]
    check("result_counts", counts["complete_unit_loci"] == 180 and counts["source_units"] == 44 and counts["pages_reviewed"] == 21 and counts["physical_folios"] == 12 and counts["official_canvases"] == 20 and counts["singular_positive_relations"] == len(singular) and counts["eligible_matched_positive_relations"] == len(eligible) and counts["eligible_mixed_units"] == len(eligible_units) and counts["eligible_folios"] == len(eligible_folios), counts)
    check("result_state_counts", counts["object_localization_states"] == dict(sorted(Counter(row["object_localization_state"] for row in observations).items())) and counts["normalized_relation_states"] == dict(sorted(Counter(row["normalized_relation_geometry"] for row in observations).items())), "exact")
    check("capacity_stopped", result["capacity"]["all_gates_pass"] is False and result["capacity"]["later_formal_scoring_authorized"] is False, result["capacity"])
    for path, expected_hash in result["inputs"].items():
        check("input_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)
    for path, expected_hash in result["outputs"].items():
        check("output_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)
    for path, expected_hash in result["implementation"].items():
        check("implementation_hash_" + Path(path).name, sha(ROOT / path) == expected_hash, expected_hash)

    payload = {
        "schema": "GDT391_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_ARTIFACT_FRAME_ID_ELIGIBILITY_CAPACITY_ACCESS_AND_HASH_VALIDATION; SOURCE_AWARE_VISUAL_JUDGMENTS_NOT_INDEPENDENTLY_REVIEWED",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "result_content_hash": result["content_hash"],
        "checks": checks,
    }
    payload["content_hash"] = digest(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
