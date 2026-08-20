#!/usr/bin/env python3
"""Independent accounting and integrity validator for GDT390.

The validator does not independently reproduce the direct visual judgments.
It reconstructs the frozen frame, mapping/review coverage, candidate and edge
accounting, access assertions, hashes, and capacity decision.
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
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
FRAME = ART / "gdt390_record_frame.tsv"
FREEZE = ART / "gdt390_pre_image_freeze.json"
MAPPING_TSV = ART / "gdt390_image_manifest.tsv"
MAPPING_JSON = ART / "gdt390_image_mapping.json"
IMAGE_HASHES = ART / "gdt390_review_image_hashes.tsv"
PAGES = ART / "gdt390_page_observations.tsv"
RECORDS = ART / "gdt390_record_observations.tsv"
CANDIDATES = ART / "gdt390_pointer_candidates.tsv"
EDGES = ART / "gdt390_eligible_edge_packet.tsv"
GATES = ART / "gdt390_capacity_gates.tsv"
ACCESS = ART / "gdt390_access_log.json"
RESULT = ART / "gdt390_result.json"
OUT = ART / "gdt390_validation.json"


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
    pages = rows(PAGES)
    records = rows(RECORDS)
    candidates = rows(CANDIDATES)
    edges = rows(EDGES)
    gates = rows(GATES)
    access = json.loads(ACCESS.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    frame_units = {row["unit_id"] for row in frame}
    frame_pages = {row["page"] for row in frame}
    frame_folios = {row["physical_folio"] for row in frame}
    page_order = freeze["frame"]["page_review_order"]
    record_order = freeze["frame"]["record_review_order"]
    check("frame_170_unique_records", len(frame) == len(frame_units) == 170, len(frame))
    check("frame_13_pages", len(frame_pages) == 13, len(frame_pages))
    check("frame_8_folios", len(frame_folios) == 8, len(frame_folios))
    check("frame_no_forbidden_page", all(not row["page"].lower().startswith("f84") for row in frame), "zero f84")
    check("freeze_page_order_exact", len(page_order) == 13 and set(page_order) == frame_pages, len(page_order))
    check("freeze_page_hash_order", page_order == sorted(page_order, key=lambda page: hashlib.sha256(("GDT390_PAGE_ORDER_V1|" + page).encode()).hexdigest()), page_order[:3])
    check("freeze_record_order_exact", len(record_order) == 170 and set(record_order) == frame_units, len(record_order))
    check("freeze_record_hash_order", record_order == sorted(record_order, key=lambda unit: hashlib.sha256(("GDT390_RECORD_ORDER_V1|" + unit).encode()).hexdigest()), record_order[:3])
    check("frame_page_counts", Counter(row["page"] for row in frame) == Counter(freeze["frame"]["page_record_counts"]), dict(Counter(row["page"] for row in frame)))

    check("mapping_13_rows_canvases", len(mapping) == len({row["canvas_id"] for row in mapping}) == 13, len(mapping))
    check("mapping_exact_pages", {row["page"] for row in mapping} == frame_pages, len(mapping))
    check("mapping_no_forbidden_page_or_label", all(not row["page"].lower().startswith("f84") and "84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in mapping), "safe")
    check("mapping_formal_seal", {row["formal_access_state"] for row in mapping} == {"SEALED"}, "SEALED")
    check("mapping_metadata_counts", mapping_meta["allowed_pages"] == mapping_meta["mapped_pages"] == mapping_meta["mapping_rows"] == mapping_meta["unique_canvases"] == 13, mapping_meta)
    check("mapping_metadata_zero_forbidden", mapping_meta["mixed_f84_canvas_fields_retained"] == mapping_meta["rejected_canvas_nonlabel_fields_parsed_or_retained"] == mapping_meta["formal_rows_read"] == 0, "zero")
    check("mapping_manifest_hash", mapping_meta["image_manifest_sha256"] == sha(MAPPING_TSV), sha(MAPPING_TSV))
    check("image_hash_13_rows", len(image_hashes) == len({row["canvas_id"] for row in image_hashes}) == 13, len(image_hashes))
    check("image_hash_exact_pages", {row["page"] for row in image_hashes} == frame_pages, len(image_hashes))
    check("image_hash_shapes", all(len(row["sha256"]) == 64 and int(row["pixel_width"]) > 0 and int(row["pixel_height"]) > 0 for row in image_hashes), "valid")

    page_names = [row["page"] for row in pages]
    check("page_observations_complete_unique", len(pages) == len(set(page_names)) == 13 and set(page_names) == frame_pages, len(pages))
    check("page_observations_frozen_order", page_names == page_order and [int(row["review_index"]) for row in pages] == list(range(1, 14)), page_names[:3])
    check("page_record_counts_reconstruct", all(int(row["frozen_record_count"]) == sum(item["page"] == row["page"] for item in frame) for row in pages), "exact")
    check("page_states_all_negative", {row["page_screen_state"] for row in pages} == {"NO_INTER_RECORD_POINTER"}, "all negative")
    check("page_candidate_counts_zero", all(int(row["candidate_cross_record_devices"]) == 0 for row in pages), "zero")
    check("page_canvas_resolution", all(row["canvas_id"] == next(item["canvas_id"] for item in mapping if item["page"] == row["page"]) for row in pages), "exact")
    check("page_reviewer_provenance", {row["reviewer_provenance"] for row in pages} == {"SINGLE_AI_DIRECT_VISUAL_EXPLORATORY"}, "single AI")
    check("page_no_automated_vision", {row["automated_visual_method"] for row in pages} == {"NONE"}, "NONE")
    check("page_formal_seal", {row["formal_access_state"] for row in pages} == {"SEALED"}, "SEALED")

    record_units = [row["unit_id"] for row in records]
    check("record_observations_complete_unique", len(records) == len(set(record_units)) == 170 and set(record_units) == frame_units, len(records))
    check("record_observations_frozen_order", record_units == record_order and [int(row["record_review_index"]) for row in records] == list(range(1, 171)), record_units[:3])
    frame_by_unit = {row["unit_id"]: row for row in frame}
    check("record_metadata_exact", all(tuple(row[key] for key in ["page", "physical_folio", "star_ordinal", "record_line_count"]) == tuple(frame_by_unit[row["unit_id"]][key] for key in ["page", "physical_folio", "star_ordinal", "record_line_count"]) for row in records), "exact")
    check("record_states_all_negative", {row["record_pointer_state"] for row in records} == {"NO_VISIBLE_INTER_RECORD_POINTER"}, "all negative")
    check("record_candidate_counts_zero", all(int(row["outgoing_pointer_candidate_count"]) == int(row["incoming_pointer_candidate_count"]) == 0 for row in records), "zero")
    check("record_formal_seal", {row["formal_access_state"] for row in records} == {"SEALED"}, "SEALED")

    check("candidate_packet_empty", len(candidates) == 0, len(candidates))
    check("eligible_edge_packet_empty", len(edges) == 0, len(edges))
    gate_map = {row["gate_id"]: int(row["current_pass"]) for row in gates}
    check("ten_gates", len(gate_map) == 10, len(gate_map))
    check("only_seal_and_complete_frame_gates_pass", {key for key, value in gate_map.items() if value} == {"G01_FORMAL_SEAL", "G02_COMPLETE_PAGE_FRAME", "G03_COMPLETE_RECORD_FRAME"}, gate_map)

    check("access_content_hash", access["content_hash"] == digest(access), access["content_hash"])
    check("access_counts", access["official_yale_canvases_opened"] == access["frozen_pages_reviewed"] == 13 and access["frozen_records_reviewed"] == 170, access)
    check("access_no_automated_or_formal", access["ocr_calls"] == access["automated_image_classification_calls"] == access["clip_embedding_caption_calls"] == access["formal_rows_read"] == access["voynich_text_identities_read"] == 0, "zero")
    check("access_no_new_forbidden_content", access["f84_image_transcription_source_group_formal_identity_prediction_or_score_access"] is False, False)

    check("result_content_hash", result["content_hash"] == digest(result), result["content_hash"])
    check("result_status", result["status"] == "COMPLETE_Q20_CENSUS_ZERO_INTER_RECORD_POINTERS", result["status"])
    counts = result["counts"]
    check("result_frame_counts", counts["frozen_pages_reviewed"] == len(pages) and counts["physical_folios_reviewed"] == len(frame_folios) and counts["frozen_records_reviewed"] == len(records) and counts["official_canvases_reviewed"] == len(image_hashes), counts)
    check("result_negative_counts", counts["no_inter_record_pointer_pages"] == 13 and counts["ambiguous_cross_record_geometry_pages"] == counts["pointer_candidates"] == counts["exact_source_target_localizations"] == counts["eligible_directed_edges"] == counts["eligible_directed_edge_folios"] == 0, counts)
    check("capacity_stopped", result["capacity"]["edge_gate_pass"] is False and result["capacity"]["folio_gate_pass"] is False and result["capacity"]["later_formal_scoring_authorized"] is False, result["capacity"])
    for path, expected in result["inputs"].items():
        check("input_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)
    for path, expected in result["outputs"].items():
        check("output_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)
    for path, expected in result["implementation"].items():
        check("implementation_hash_" + Path(path).name, sha(ROOT / path) == expected, expected)

    payload = {
        "schema": "GDT390_VALIDATION_V1",
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
