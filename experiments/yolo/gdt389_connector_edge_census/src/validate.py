#!/usr/bin/env python3
"""Independent integrity and accounting validator for GDT389.

The validator does not claim to reproduce the direct visual judgments.  It
independently reconstructs the frozen frame, image/page coverage, candidate
accounting, access assertions, hashes, and capacity decision from artifacts.
"""
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
MAPPING_TSV = ART / "gdt389_image_manifest.tsv"
MAPPING_JSON = ART / "gdt389_image_mapping.json"
IMAGE_HASHES = ART / "gdt389_review_image_hashes.tsv"
OBS = ART / "gdt389_page_observations.tsv"
CANDS = ART / "gdt389_ambiguous_candidates.tsv"
EDGES = ART / "gdt389_eligible_edge_packet.tsv"
GATES = ART / "gdt389_capacity_gates.tsv"
ACCESS = ART / "gdt389_access_log.json"
RESULT = ART / "gdt389_result.json"
OUT = ART / "gdt389_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    frame = rows(FRAME)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    mapping = rows(MAPPING_TSV)
    mapping_meta = json.loads(MAPPING_JSON.read_text(encoding="utf-8"))
    image_hashes = rows(IMAGE_HASHES)
    observations = rows(OBS)
    candidates = rows(CANDS)
    edges = rows(EDGES)
    gates = rows(GATES)
    access = json.loads(ACCESS.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    frame_pages = {row["page"] for row in frame}
    frame_folios = {row["physical_folio"] for row in frame}
    order = freeze["page_universe"]["review_order"]
    check("frame_61_pages", len(frame) == len(frame_pages) == 61, len(frame_pages))
    check("frame_30_folios", len(frame_folios) == 30, len(frame_folios))
    check("freeze_order_exact_frame", len(order) == 61 and set(order) == frame_pages, len(order))
    check("freeze_order_hash_rule", order == sorted(order, key=lambda page: hashlib.sha256(("GDT389_PAGE_ORDER_V1|" + page).encode()).hexdigest()), order[:3])
    check("frame_has_no_forbidden_page", all(not page.lower().startswith("f84") for page in frame_pages), "zero f84 pages")

    mapped_pages = {row["page"] for row in mapping}
    mapped_canvases = {row["canvas_id"] for row in mapping}
    check("mapping_covers_frame", mapped_pages == frame_pages, len(mapped_pages))
    check("mapping_71_rows", len(mapping) == 71, len(mapping))
    check("mapping_50_canvases", len(mapped_canvases) == 50 and "" not in mapped_canvases, len(mapped_canvases))
    check("mapping_no_forbidden_page_or_label", all(not row["page"].lower().startswith("f84") and "84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mapping), "safe")
    check("mapping_formal_seal", {row["formal_access_state"] for row in mapping} == {"SEALED"}, "SEALED")
    check("mapping_meta_counts", mapping_meta["allowed_pages"] == mapping_meta["mapped_pages"] == 61 and mapping_meta["mapping_rows"] == 71, mapping_meta)
    check("mapping_meta_zero_forbidden_retention", mapping_meta["mixed_f84_canvas_fields_retained"] == 0 and mapping_meta["formal_rows_read"] == 0, "zero")
    check("mapping_tsv_hash", mapping_meta["image_manifest_sha256"] == sha(MAPPING_TSV), sha(MAPPING_TSV))

    check("image_hash_rows", len(image_hashes) == 50 and len({row["canvas_id"] for row in image_hashes}) == 50, len(image_hashes))
    check("image_hash_canvas_set", {row["canvas_id"] for row in image_hashes} == mapped_canvases, len(mapped_canvases))
    check("image_hash_shape", all(len(row["sha256"]) == 64 and int(row["pixel_width"]) > 0 and int(row["pixel_height"]) > 0 for row in image_hashes), "valid")
    check("image_hash_labels_safe", all("84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in image_hashes), "safe")

    obs_pages = [row["page"] for row in observations]
    check("observations_complete_unique", len(observations) == len(set(obs_pages)) == 61 and set(obs_pages) == frame_pages, len(observations))
    check("observations_frozen_order", obs_pages == order and [int(row["review_index"]) for row in observations] == list(range(1, 62)), obs_pages[:3])
    obs_counts = Counter(row["page_screen_state"] for row in observations)
    check("screen_counts", obs_counts == {"NO_CONNECTOR_CANDIDATE": 47, "AMBIGUOUS_CONNECTOR": 14}, dict(obs_counts))
    check("observation_canvas_resolution", all(set(row["canvas_ids"].split(";")) == {item["canvas_id"] for item in mapping if item["page"] == row["page"]} for row in observations), "exact")
    check("observation_provenance", {row["reviewer_provenance"] for row in observations} == {"SINGLE_AI_DIRECT_VISUAL_EXPLORATORY"}, "single AI")
    check("observation_no_automated_vision", {row["automated_visual_method"] for row in observations} == {"NONE"}, "NONE")
    check("observation_formal_seal", {row["formal_access_state"] for row in observations} == {"SEALED"}, "SEALED")
    check("no_successful_endpoint_screen", all(row["page_screen_state"] not in {"CONNECTOR_WITH_FEWER_THAN_TWO_INSCRIPTIONS", "CONNECTOR_WITH_TWO_OR_MORE_INSCRIPTIONS"} for row in observations), "zero")

    ambiguous_pages = {row["page"] for row in observations if row["page_screen_state"] == "AMBIGUOUS_CONNECTOR"}
    check("candidate_rows_match_ambiguities", len(candidates) == 14 and {row["page"] for row in candidates} == ambiguous_pages, len(candidates))
    check("candidate_ids_unique", len({row["candidate_id"] for row in candidates}) == 14, "unique")
    check("candidate_failure_exact", {row["failure_stage"] for row in candidates} == {"PAGE_SCREEN_ENDPOINT_OWNERSHIP"} and {row["source_aware_endpoint_localization"] for row in candidates} == {"NOT_ATTEMPTED_SCREEN_DID_NOT_ESTABLISH_TWO_INSCRIPTION_ENDPOINTS"}, "screen ownership")
    check("candidate_direction_unresolved", {row["direction_basis"] for row in candidates} == {"NONE_OR_UNRESOLVED"}, "unresolved")
    check("candidate_formal_seal", {row["formal_access_state"] for row in candidates} == {"SEALED"}, "SEALED")

    check("eligible_edge_packet_empty", len(edges) == 0, len(edges))
    gate_map = {row["gate_id"]: int(row["current_pass"]) for row in gates}
    check("nine_gates", len(gate_map) == 9, len(gate_map))
    check("only_seal_and_completeness_pass", {key for key, value in gate_map.items() if value} == {"G01_FORMAL_SEAL", "G02_COMPLETE_PAGE_FRAME"}, gate_map)

    check("access_content_hash", access["content_hash"] == digest(access), access["content_hash"])
    check("access_counts", access["official_yale_canvases_opened"] == 50 and access["frozen_pages_reviewed"] == 61, access)
    check("access_no_automated_or_formal", access["ocr_calls"] == access["automated_image_classification_calls"] == access["clip_embedding_caption_calls"] == access["formal_rows_read"] == access["voynich_text_identities_read"] == 0, "zero")
    check("access_no_new_forbidden_content", access["f84_image_transcription_source_group_formal_identity_prediction_or_score_access"] is False, False)

    check("result_content_hash", result["content_hash"] == digest(result), result["content_hash"])
    check("result_status", result["status"] == "COMPLETE_CENSUS_ZERO_ELIGIBLE_DIRECTED_EDGES", result["status"])
    counts = result["counts"]
    check("result_counts_reconstruct", counts["frozen_pages_reviewed"] == len(observations) and counts["physical_folios_reviewed"] == len({row["physical_folio"] for row in observations}) and counts["official_canvases_reviewed"] == len(mapped_canvases) and counts["no_connector_candidate_pages"] == obs_counts["NO_CONNECTOR_CANDIDATE"] and counts["ambiguous_connector_pages"] == obs_counts["AMBIGUOUS_CONNECTOR"], counts)
    check("result_zero_edges", counts["exact_endpoint_localizations"] == counts["eligible_directed_edges"] == counts["eligible_directed_edge_folios"] == 0, counts)
    check("capacity_stopped", result["capacity"]["edge_gate_pass"] is False and result["capacity"]["folio_gate_pass"] is False and result["capacity"]["later_formal_scoring_authorized"] is False, result["capacity"])
    for path, expected in result["inputs"].items():
        check("input_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)
    for path, expected in result["outputs"].items():
        check("output_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)
    for path, expected in result["implementation"].items():
        check("implementation_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)

    payload = {
        "schema": "GDT389_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_ARTIFACT_FRAME_MAPPING_ACCOUNTING_HASH_AND_DECISION_VALIDATION; DIRECT_VISUAL_JUDGMENTS_NOT_INDEPENDENTLY_REVIEWED",
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
