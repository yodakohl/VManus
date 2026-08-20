#!/usr/bin/env python3
"""Independent artifact/accounting validator for GDT392."""
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


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    frame = tsv(ART / "gdt392_array_frame.tsv")
    obs = tsv(ART / "gdt392_array_observations.tsv")
    candidates = tsv(ART / "gdt392_start_only_candidates.tsv")
    gates = tsv(ART / "gdt392_capacity_gates.tsv")
    mapping = tsv(ART / "gdt392_image_manifest.tsv")
    hashes = tsv(ART / "gdt392_review_image_hashes.tsv")
    access = json.loads((ART / "gdt392_access_log.json").read_text(encoding="utf-8"))
    correction = json.loads((ART / "gdt392_access_correction.json").read_text(encoding="utf-8"))
    result = json.loads((ART / "gdt392_result.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    check("frame_45_arrays_504_slots", len(frame) == 45 and sum(int(r["slot_count"]) for r in frame) == 504, f"{len(frame)}/{sum(int(r['slot_count']) for r in frame)}")
    check("frame_23_pages_7_folios", len({r["page"] for r in frame}) == 23 and len({r["physical_folio"] for r in frame}) == 7, f"{len({r['page'] for r in frame})}/{len({r['physical_folio'] for r in frame})}")
    check("observations_complete_unique", len(obs) == 45 and len({r["array_id"] for r in obs}) == 45, len(obs))
    check("observations_frozen_order", [r["array_id"] for r in obs] == [r["array_id"] for r in frame], obs[:2])
    check("all_outputs_no_f84", all(not r["page"].lower().startswith("f84") for r in frame + obs + mapping), "zero selectors")
    check("mapping_23_pages", {r["page"] for r in mapping} == {r["page"] for r in frame}, len({r["page"] for r in mapping}))
    check("mapping_14_canvases", len({r["canvas_id"] for r in mapping}) == len(hashes) == 14, len(hashes))
    check("formal_sealed", all(r["formal_access_state"] == "SEALED" for r in obs), "all")
    check("no_automated_visual_method", all(r["automated_visual_method"] == "NONE" for r in obs), "all")
    state_counts = Counter(r["review_state"] for r in obs)
    check("state_counts", state_counts == {"NO_AUTHORIAL_START_OR_DIRECTION": 39, "DISTINCT_START_MARKER_NO_DIRECTION": 6}, dict(state_counts))
    check("start_candidates_exact_six", len(candidates) == 6 and {r["array_id"] for r in candidates} == {r["array_id"] for r in obs if r["author_visible_start_candidate"] == "1"}, [r["array_id"] for r in candidates])
    check("start_candidates_two_folios", {r["physical_folio"] for r in candidates} == {"f67", "f69"}, sorted({r["physical_folio"] for r in candidates}))
    check("direction_zero", all(r["author_visible_direction"] == "0" for r in obs), "zero")
    check("eligible_zero", all(r["eligible_authorial_start_direction"] == "0" and r["directed_edges_licensed"] == "0" for r in obs), "zero")
    check("ownership_not_promoted", all(r["ordered_label_ownership_state"] == "NOT_ASSESSED_DIRECTION_ABSENT" for r in obs), "all")
    gate_map = {r["gate_id"]: r for r in gates}
    check("gate_count", len(gates) == 8, len(gates))
    check("gate_start_only_pass", gate_map["G03_AUTHOR_VISIBLE_START"]["current_pass"] == "1", gate_map["G03_AUTHOR_VISIBLE_START"])
    check("gate_direction_fail", gate_map["G04_AUTHOR_VISIBLE_DIRECTION"]["current_pass"] == "0", gate_map["G04_AUTHOR_VISIBLE_DIRECTION"])
    check("gate_capacity_fail", gate_map["G06_MINIMUM_DIRECTED_EDGES"]["current_pass"] == "0" and gate_map["G07_MINIMUM_PHYSICAL_FOLIOS"]["current_pass"] == "0", "both")
    check("access_counts", access["arrays_reviewed"] == 45 and access["slots_covered"] == 504 and access["official_yale_canvases_reviewed"] == 14, access)
    check("access_no_ocr_or_automation", access["ocr_calls"] == access["automated_image_classification_calls"] == access["clip_embedding_caption_calls"] == 0, access)
    check("access_source_materialization_disclosed", access["source_inventory_full_rows_materialized"] == 504 and access["post_visual_review_catalogue_rows_with_diplomatic_notation_displayed"] is True, access)
    check("access_formal_zero", access["formal_family_page_host_joint_tuple_or_renderer_rows_read"] == 0 and access["formal_scoring_run"] is False, access)
    check("access_f84_false", access["f84_opened_parsed_retained_displayed_or_scored"] is False, access)
    body = dict(access); claimed = body.pop("content_hash")
    check("access_content_hash", digest(body) == claimed, claimed)
    check("result_status", result["status"] == "COMPLETE_CENSUS_ZERO_ELIGIBLE_START_DIRECTION_ARRAYS", result["status"])
    check("result_counts", result["counts"]["arrays"] == 45 and result["counts"]["start_only_candidates"] == 6 and result["counts"]["direction_markers"] == result["counts"]["eligible_arrays"] == result["counts"]["eligible_directed_edges"] == 0, result["counts"])
    check("result_scoring_locked", result["capacity"]["formal_scoring_authorized"] is False, result["capacity"])
    check("result_candidate_ids", result["start_only_array_ids"] == [r["array_id"] for r in candidates], result["start_only_array_ids"])
    check("result_access_bound", result["access"] == access, "exact")
    correction_body = dict(correction); correction_claimed = correction_body.pop("content_hash")
    check("correction_content_hash", digest(correction_body) == correction_claimed, correction_claimed)
    check("correction_scientific_effect_none", correction["scientific_effect"] == "NONE_COUNTS_STATES_GATES_AND_DECISION_UNCHANGED", correction["scientific_effect"])
    check("correction_f84_false", correction["corrected_access"]["f84_opened_parsed_retained_displayed_or_scored"] is False, correction["corrected_access"])
    for path, expected in result["inputs"].items():
        check(f"input_hash:{path}", sha(ROOT / path) == expected, expected)
    for path, expected in result["outputs"].items():
        check(f"output_hash:{path}", sha(ROOT / path) == expected, expected)
    for path, expected in result["implementation"].items():
        check(f"implementation_hash:{path}", sha(ROOT / path) == expected, expected)
    body = dict(result); claimed = body.pop("content_hash")
    check("result_content_hash", digest(body) == claimed, claimed)
    failed = sum(not row["pass"] for row in checks)
    validation = {
        "schema": "GDT392_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "scope": "Independent reconstruction of complete-frame accounting, candidate/state counts, gate logic, access assertions, hashes, and result integrity. It does not independently reproduce the single-AI direct visual start/direction judgments.",
        "result_sha256": sha(ART / "gdt392_result.json"),
    }
    validation["content_hash"] = digest(validation)
    (ART / "gdt392_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"{validation['status']} {validation['checks_passed']}/{len(checks)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
