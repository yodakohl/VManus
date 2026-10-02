#!/usr/bin/env python3
"""Protocol and pixel-provenance checks for GDT1142; never judges image meaning."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt1142_f25v_native_contact_followup"
ART = EXP / "artifacts"
OUT = ART / "VALIDATION.json"
VALID = True
CHECKS: list[dict] = []


def add(name: str, ok: bool, detail: str, kind: str = "independently_checkable") -> None:
    global VALID
    CHECKS.append({"check": name, "passed": bool(ok), "evidence_type": kind, "detail": detail})
    VALID = VALID and bool(ok)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def repo_bytes_at(revision: str, relpath: str) -> bytes | None:
    proc = subprocess.run(["git", "show", f"{revision}:{relpath}"], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return proc.stdout if proc.returncode == 0 else None


def repo_paths_at(revision: str, directory: str) -> set[str]:
    proc = subprocess.run(["git", "ls-tree", "-r", "--name-only", revision, directory], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if proc.returncode != 0:
        return set()
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def main() -> int:
    global VALID
    source = read_json(EXP / "src/SOURCE.json")
    method = (EXP / "METHOD.md").read_text(encoding="utf-8")
    prereg = (EXP / "PREREGISTRATION.md").read_text(encoding="utf-8")
    observer_plan_path = ART / "OBSERVER_PLAN.md"
    observer_plan_sha = sha(observer_plan_path)

    registration_commit = "46630bdcaebf7dcc853fb9f8e78afc5fb07819dc"
    frozen_registration_paths = [
        "experiments/yolo/gdt1142_f25v_native_contact_followup/METHOD.md",
        "experiments/yolo/gdt1142_f25v_native_contact_followup/PREREGISTRATION.md",
        "experiments/yolo/gdt1142_f25v_native_contact_followup/src/SOURCE.json",
        "experiments/yolo/gdt1142_f25v_native_contact_followup/artifacts/OBSERVER_PLAN.md",
        "experiments/yolo/gdt1142_f25v_native_contact_followup/artifacts/VALIDATION_PLAN.md",
    ]
    frozen_registration_results = []
    frozen_registration_ok = True
    for rel in frozen_registration_paths:
        committed = repo_bytes_at(registration_commit, rel)
        current = (ROOT / rel).read_bytes()
        same = committed is not None and committed == current
        frozen_registration_ok &= same
        frozen_registration_results.append({"path": rel, "sha256": hashlib.sha256(current).hexdigest(),
                                             "matches_public_registration_commit": same})
    add("registered_contract_files_match_public_commit", frozen_registration_ok,
        "METHOD, PREREGISTRATION, SOURCE, OBSERVER_PLAN, and VALIDATION_PLAN bytes match the pre-acquisition public registration commit.")

    # Exact preregistered dependencies.
    pins_ok = True
    pin_results = []
    for pin in source["input_pins"]:
        p = ROOT / pin["path"]
        actual = sha(p) if p.is_file() else None
        ok = actual == pin["sha256"]
        pins_ok &= ok
        pin_results.append({"path": pin["path"], "expected_sha256": pin["sha256"],
                            "actual_sha256": actual, "passed": ok})
    add("registered_input_pins", pins_ok, "All four SOURCE.json input pins match byte-for-byte." if pins_ok else "At least one registered input pin differs or is absent.")

    receipt_path = ROOT / source["input_pins"][3]["path"]
    meta_receipt = read_json(receipt_path)
    dims = source["expected_dimensions"]
    area = dims[0] * dims[1]
    metadata_ok = (
        meta_receipt.get("status") == 200
        and meta_receipt.get("target_pixels_received") is False
        and meta_receipt.get("final_url") == "https://collections.library.yale.edu/iiif/2/1006123/info.json"
        and meta_receipt.get("metadata", {}).get("@id") == "https://collections.library.yale.edu/iiif/2/1006123"
        and [meta_receipt.get("metadata", {}).get("width"), meta_receipt.get("metadata", {}).get("height")] == dims
        and meta_receipt.get("metadata", {}).get("profile", [None, {}])[1].get("maxArea") == area
        and any(s.get("width") == dims[0] and s.get("height") == dims[1]
                for s in meta_receipt.get("metadata", {}).get("sizes", []))
    )
    add("pinned_canvas_metadata_and_area", metadata_ok,
        f"Canvas {source['canvas']} metadata lists {dims[0]}×{dims[1]}, native size, and maxArea {area}; the cap's cause for GDT1095 is not inferred.")
    old_proportional_area = math.ceil(3000 * dims[1] / dims[0]) * 3000
    cap = meta_receipt.get("metadata", {}).get("profile", [None, {}])[1].get("maxArea")
    add("old_3000_width_cap_is_only_plausible_explanation", old_proportional_area > cap,
        f"A proportional 3000px-wide rendition would be about {old_proportional_area:,} pixels versus cap {cap:,}; this calculation does not establish the earlier server's reason.")

    acq = read_json(ART / "ACQUISITION.json")
    native_path = ART / "native.jpg"
    crop_path = ART / "contact_crop.png"
    native_hash = sha(native_path)
    crop_hash = sha(crop_path)
    with Image.open(native_path) as im:
        im.load()
        native_dims = list(im.size)
        native_mode = im.mode
        native_format = im.format
        native = im.copy()
    with Image.open(crop_path) as im:
        im.load()
        crop_dims = list(im.size)
        crop_mode = im.mode
        crop = im.copy()
    acquisition_ok = (
        acq.get("request_count") == 1
        and acq.get("request_url") == source["url"]
        and acq.get("final_url") == source["url"]
        and acq.get("canvas") == source["canvas"]
        and acq.get("folio") == source["folio"]
        and acq.get("http_status") == 200
        and acq.get("content_type") == "image/jpeg"
        and acq.get("bytes") == native_path.stat().st_size
        and acq.get("sha256") == native_hash
        and acq.get("dimensions") == dims == native_dims
        and acq.get("outcome") == "NATIVE_INPUT_ACQUIRED"
        and acq.get("sealed_opened") is False
        and acq.get("independent_confirmation_capacity") == 0
    )
    add("acquisition_receipt_matches_retained_native_bytes", acquisition_ok,
        "Receipt claims one exact-URL 200 request; URL/status/count and successful server request remain receipt-backed, while byte count, file hash, decoded dimensions and image format are locally checkable.",
        "mixed_local_check_and_receipt")
    add("native_image_format_and_dimensions", native_format == "JPEG" and native_dims == dims,
        f"Retained file decodes as {native_format}, {native_dims}, mode {native_mode}; no visual inspection performed.")

    norm = source["fixed_crop_normalized"]
    expected_bounds = [math.floor(norm[0] * dims[0]), math.floor(norm[1] * dims[1]),
                       math.ceil(norm[2] * dims[0]), math.ceil(norm[3] * dims[1])]
    actual_bounds = acq.get("crop", {}).get("bounds")
    expected_crop_dims = [expected_bounds[2] - expected_bounds[0], expected_bounds[3] - expected_bounds[1]]
    exact_crop = native.crop(tuple(expected_bounds))
    crop_pixel_equal = (exact_crop.mode == crop.mode and exact_crop.size == crop.size
                        and ImageChops.difference(exact_crop, crop).getbbox() is None)
    crop_ok = (
        actual_bounds == expected_bounds
        and acq.get("crop", {}).get("path") == "artifacts/contact_crop.png"
        and acq.get("crop", {}).get("parent_sha256") == native_hash
        and acq.get("crop", {}).get("sha256") == crop_hash
        and acq.get("crop", {}).get("dimensions") == expected_crop_dims == crop_dims
        and acq.get("crop", {}).get("resampled") is False
        and acq.get("crop", {}).get("mode") == crop_mode == "RGB"
        and crop_pixel_equal
    )
    add("crop_bounds_and_decoded_pixel_identity", crop_ok,
        f"Expected fixed integer slice {expected_bounds}, dimensions {expected_crop_dims}; crop decodes RGB and pixel-by-pixel equals that slice of the retained original (no visual interpretation).")

    release = read_json(ART / "VIEW_RELEASE.json")
    root_obs = read_json(ART / "ROOT_OBSERVATION.json")
    observer = read_json(ART / "OBSERVER.json")
    root_freeze = read_json(ART / "ROOT_FREEZE.json")
    comparison = read_json(ART / "COMPARISON_FREEZE.json")
    result = read_json(ART / "RESULT.json")
    add("view_release_binds_acquisition_receipt", release.get("acquisition_receipt_sha256") == sha(ART / "ACQUISITION.json"),
        "The view-release receipt's acquisition receipt hash matches the retained acquisition record; this does not establish the recorded server transaction itself.",
        "byte_check_plus_receipt")
    record_hashes = {
        "ROOT_OBSERVATION.json": sha(ART / "ROOT_OBSERVATION.json"),
        "ROOT_OBSERVATION.md": sha(ART / "ROOT_OBSERVATION.md"),
        "OBSERVER.json": sha(ART / "OBSERVER.json"),
        "OBSERVER.md": sha(ART / "OBSERVER.md"),
    }
    expected_files = {k: record_hashes[k] for k in comparison.get("files", {})}
    exact_comparison_keys = {"ROOT_OBSERVATION.json", "ROOT_OBSERVATION.md", "OBSERVER.json", "OBSERVER.md"}
    exact_root_keys = {"ROOT_OBSERVATION.json", "ROOT_OBSERVATION.md"}
    freeze_hashes_ok = (set(comparison.get("files", {})) == exact_comparison_keys
                        and set(root_freeze.get("files", {})) == exact_root_keys
                        and comparison.get("files") == {k: record_hashes[k] for k in exact_comparison_keys}
                        and root_freeze.get("files") == {k: record_hashes[k] for k in exact_root_keys}
                        and comparison.get("root_freeze_sha256") == sha(ART / "ROOT_FREEZE.json"))
    add("initial_observation_records_match_freeze_receipts", freeze_hashes_ok,
        "The currently retained initial-record bytes match ROOT_FREEZE and COMPARISON_FREEZE hashes; receipts evidence their stated pre-comparison freeze, not truth of their visual claims.",
        "byte_check_plus_freeze_receipts")

    view_items_ok = True
    expected_views = ["artifacts/native.jpg", "artifacts/contact_crop.png"]
    for record in (release, root_obs):
        view_items_ok &= record.get("view_order") == expected_views
        view_items_ok &= record.get("original_sha256") == native_hash
        view_items_ok &= record.get("crop_sha256") == crop_hash
    view_items_ok &= release.get("root_answers_disclosed") is False
    view_items_ok &= release.get("historical_narratives_disclosed") is False
    inv = observer.get("view_inventory", [])
    view_items_ok &= len(inv) == 2 and [v.get("path") for v in inv] == expected_views
    view_items_ok &= all(v.get("view_count") == 1 and v.get("detail") == "original" for v in inv)
    if len(inv) == 2:
        view_items_ok &= inv[0].get("sha256") == native_hash and inv[0].get("dimensions") == dims
        view_items_ok &= inv[1].get("sha256") == crop_hash and inv[1].get("dimensions") == expected_crop_dims
        view_items_ok &= inv[1].get("parent_bounds") == expected_bounds and inv[1].get("resampled") is False
    view_items_ok &= observer.get("release_utc") == release.get("released_utc")
    view_items_ok &= observer.get("view_count") == 2 and observer.get("plan_sha256") == observer_plan_sha
    add("registered_two_view_inventory_and_bindings", view_items_ok,
        "Both initial record files and the release receipt bind the same original then fixed crop hashes; answer/narrative separation and view counts are recorded claims, not independently provable from retained bytes.",
        "mixed_local_check_and_receipt")

    chronology_ok = False
    try:
        chronology_ok = (
            parse_time(release["released_utc"]) < parse_time(root_freeze["frozen_utc"])
            and parse_time(release["released_utc"]) < parse_time(observer["frozen_at_utc"])
            and parse_time(root_freeze["frozen_utc"]) < parse_time(observer["frozen_at_utc"])
            and parse_time(observer["frozen_at_utc"]) < parse_time(comparison["comparison_started_utc"])
            and comparison.get("initial_records_unchanged") is True
            and abs((parse_time(comparison["root_frozen_utc"]) - parse_time(root_freeze["frozen_utc"])).total_seconds()) < 1
            and comparison.get("observer_frozen_utc") == observer.get("frozen_at_utc")
            and root_freeze.get("second_observer_answers_read") is False
        )
    except (KeyError, TypeError, ValueError):
        chronology_ok = False
    add("separate_freezes_precede_comparison", chronology_ok,
        "Recorded timestamps and the comparison receipt place each initial freeze before comparison; they do not independently prove what either observer had seen.",
        "receipt-backed_chronology")

    registration_time_ok = False
    commit_author_time = None
    try:
        commit_time_proc = subprocess.run(
            ["git", "show", "-s", "--format=%aI", registration_commit], cwd=ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        commit_author_time = commit_time_proc.stdout.strip()
        registration_time_ok = (
            acq.get("public_registration_commit") == registration_commit
            and acq.get("public_main_verified_before_request") is True
            and parse_time(commit_author_time) < parse_time(acq["request_started_utc"])
            and parse_time(source["registered_utc"]) < parse_time(acq["request_started_utc"])
            and parse_time(acq["request_started_utc"]) < parse_time(acq["response_completed_utc"])
            and parse_time(acq["response_completed_utc"]) < parse_time(release["released_utc"])
        )
    except (KeyError, TypeError, ValueError, subprocess.CalledProcessError):
        registration_time_ok = False
    add("registration_request_response_release_chronology", registration_time_ok,
        "Commit author time, SOURCE registration, acquisition start/response, and view release follow the required order; public-main verification and transaction times are stated in receipts and not independently verified against remote/server history.",
        "local_commit_time_plus_receipt_chronology")

    required = ["LEAF_CONTINUITY", "SEPARATE_SHAFT", "TETHER", "DISTINCT_BODY", "SECOND_ACTOR"]
    allowed = {"PRESENT", "ABSENT_AT_SUPPLIED_SCALE", "UNRESOLVED"}
    root_observation_array = root_obs.get("observations", [])
    observer_item_array = observer.get("items", [])
    ro = {x["item"]: x for x in root_observation_array}
    ob = {x["item"]: x for x in observer_item_array}
    record_complete = (len(root_observation_array) == len(required) and len(ro) == len(required)
                       and set(ro) == set(required) and len(observer_item_array) == len(required)
                       and len(ob) == len(required) and set(ob) == set(required))
    if record_complete:
        record_complete &= all(ro[k].get("judgment") in allowed and bool(ro[k].get("reason")) for k in required)
        record_complete &= all(ob[k].get("assessment") in allowed and bool(ob[k].get("direct_reason")) for k in required)
        record_complete &= all(set(ro[k].get("view", "").split()) <= {"full", "and", "crop"} for k in required)
        record_complete &= all(set(ob[k].get("supporting_views", [])) <= {1, 2}
                               and len(ob[k].get("supporting_views", [])) > 0 for k in required)
    add("five_fixed_items_complete_with_allowed_categories_and_reasons", record_complete,
        "Checks fixed keys, answer vocabulary, nonempty direct reasons and supplied-view references; does not assess whether descriptions are visually true.",
        "schema_and_manual_review_dependent")

    comparison_items = {x.get("item"): x for x in result.get("items", [])}
    reconciliation_ok = (set(comparison_items) == set(required) and len(result.get("items", [])) == len(required))
    disagreements = []
    if reconciliation_ok:
        for key in required:
            rj = ro[key]["judgment"]
            oj = ob[key]["assessment"]
            row = comparison_items[key]
            same = rj == oj
            retained = rj if same else "UNRESOLVED"
            if not same:
                disagreements.append(key)
            reconciliation_ok &= row.get("root") == rj and row.get("second_observer") == oj
            reconciliation_ok &= row.get("agreement") is same and row.get("retained") == retained
        reconciliation_ok &= result.get("disagreements") == disagreements
    add("reconciliation_preserves_each_record_and_disagreement", reconciliation_ok,
        "Reconciliation values are mechanically compared with both frozen records; disagreements, if present, remain explicitly listed and retained as unresolved. This is a record-consistency check, not an assessment of observation quality.",
        "record_comparison")

    # This scope decision follows the registered rule: leaf contact alone does not
    # distinguish consumption/contact-healing/emblematic roles; no shaft, tether,
    # second actor, or other explicit role-selecting structure is recorded.
    role_neutral = (all(comparison_items[k].get("retained") in allowed for k in required)
                    and all(comparison_items[k].get("retained") != "PRESENT"
                            for k in ["SEPARATE_SHAFT", "TETHER", "SECOND_ACTOR"])
                    and result.get("decision") == "NATIVE_OBSERVATIONS_RETAINED_ROLE_UNSELECTED")
    add("registered_result_category_matches_retained_scope", role_neutral,
        "The recorded result retains leaf contact/body distinction while no predeclared shaft, tether, or second-actor discriminator is recorded; visual truth and semantic role remain outside validation.",
        "mechanical_scope_rule")

    limits_ok = (
        result.get("confirmed_words") == 0
        and result.get("independent_confirmation_capacity") == 0
        and result.get("old_results_revised") is False
        and result.get("extra_pixels_after_registered_views") is False
        and result.get("reserves_opened") is False
        and source.get("sealed") == ["f84", "f84r"]
        and source.get("unadmitted") == ["f116v"]
        and source.get("reserve") == "CLOSED"
        and "not a proved server-error diagnosis" in method
        and "not a proved server-error diagnosis" in prereg
    )
    add("scope_and_claim_limits_retained", limits_ok,
        "The records preserve same-photograph exposure, zero independent confirmation, sealed/unadmitted/reserve limits, unchanged GDT1095, and no meaning claim.",
        "record_and_contract_check")

    # Confirm the earlier GDT1095 result and complete directory are byte-identical
    # to the public pre-acquisition registration commit.
    old_dir = "experiments/yolo/gdt1095_f25v_native_contact_geometry"
    old_paths = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / old_dir).rglob("*")
                       if p.is_file() and "__pycache__" not in p.relative_to(ROOT).parts)
    committed_old_paths = repo_paths_at(registration_commit, old_dir)
    current_old_paths = set(old_paths)
    old_tree_ok = bool(old_paths) and current_old_paths == committed_old_paths
    old_checks = []
    for rel in old_paths:
        committed = repo_bytes_at(acq["public_registration_commit"], rel)
        current = (ROOT / rel).read_bytes()
        ok = committed is not None and committed == current
        old_checks.append({"path": rel, "sha256": hashlib.sha256(current).hexdigest(), "matches_registration_commit": ok})
        old_tree_ok &= ok
    old_result = read_json(ROOT / old_dir / "artifacts/RESULT.json")
    old_tree_ok &= old_result.get("decision") == "MISSING_REGISTERED_HIGHRES_INPUT"
    old_tree_ok &= old_result.get("executed_visual_observations") == 0
    old_tree_ok &= old_result.get("negative_visual_observations") == 0
    add("gdt1095_unchanged_at_public_registration_commit", old_tree_ok,
        "Current GDT1095 file path set equals the committed path set (excluding __pycache__), and every retained file equals its committed bytes; registered missing-input result remains unchanged.")

    result_doc = {
        "experiment": "GDT1142",
        "validation_scope": "Protocol, record consistency, exact source-byte and crop-pixel provenance. No image pixels were displayed or interpreted by this validator.",
        "validator_protocol_status": "PASS" if VALID else "FAIL",
        "visual_truth_status": "NOT_ASSESSED",
        "semantic_selection_status": "NOT_ASSESSED",
        "decision_recorded_by_experiment": result.get("decision"),
        "acquisition": {
            "request_count_claim": acq.get("request_count"),
            "request_url_claim": acq.get("request_url"),
            "http_status_claim": acq.get("http_status"),
            "response_time_claim": acq.get("response_completed_utc"),
            "retained_native_sha256": native_hash,
            "retained_native_bytes": native_path.stat().st_size,
            "retained_native_dimensions": native_dims,
            "crop_sha256": crop_hash,
            "crop_pixel_equal_to_registered_slice": crop_pixel_equal,
            "crop_bounds": expected_bounds,
            "crop_dimensions": crop_dims,
        },
        "registered_pins": pin_results,
        "registered_contract_files": frozen_registration_results,
        "registration_author_time": commit_author_time,
        "registration_chronology_passed": registration_time_ok,
        "observer_freeze_order": {
            "release_utc": release.get("released_utc"),
            "root_freeze_utc": root_freeze.get("frozen_utc"),
            "second_observer_freeze_utc": observer.get("frozen_at_utc"),
            "comparison_utc": comparison.get("comparison_started_utc"),
            "initial_record_hashes_match_freeze_receipts": freeze_hashes_ok,
            "chronology_and_separation_are_receipt_backed": chronology_ok,
            "observer_plan_sha256": observer_plan_sha,
        },
        "retained_observations": [
            {"item": k, "root": ro.get(k, {}).get("judgment"),
             "second_observer": ob.get(k, {}).get("assessment"),
             "retained": comparison_items.get(k, {}).get("retained")}
            for k in required
        ],
        "gdt1095": {"unchanged_against_commit": acq.get("public_registration_commit"),
                    "committed_paths": sorted(committed_old_paths),
                    "current_paths_match_commit": current_old_paths == committed_old_paths,
                    "files_compared": old_checks,
                    "registered_decision": old_result.get("decision")},
        "checks": CHECKS,
        "limits": [
            "HTTP request count, response status, final URL, and view order rely on retained acquisition and observation receipts; this validator cannot establish server-side history or observer conduct.",
            "Completeness and categorical consistency do not prove the visual descriptions true.",
            "Agreement between two records about the same exposed photograph is not independent manuscript confirmation.",
            "The registered metadata-area cap is a plausible explanation for the old 3000px failure, not a proven cause.",
        ],
    }
    OUT.write_text(json.dumps(result_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"GDT1142 protocol validation: {'PASS' if VALID else 'FAIL'} ({sum(c['passed'] for c in CHECKS)}/{len(CHECKS)} checks)")
    return 0 if VALID else 1


if __name__ == "__main__":
    raise SystemExit(main())
