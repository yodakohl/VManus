#!/usr/bin/env python3
"""Independent arithmetic and official-image binding validation for IGR001."""
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
PRODUCER = BASE / "audit_igr001_image_grounded_grapheme_result.py"
METHOD = BASE / "IGR001_IMAGE_GROUNDED_GRAPHEME_METHOD.md"
OBSERVATIONS = BASE / "igr001_image_grounded_grapheme_observations.tsv"
SELECTION = RES / "igr001_image_grounded_grapheme_selection.json"
SELECTION_VALIDATION = RES / "igr001_image_grounded_grapheme_selection_validation.json"
RESULT = RES / "igr001_image_grounded_grapheme_result.json"
REPORT = RES / "igr001_image_grounded_grapheme_result_report.md"
OUT = RES / "igr001_image_grounded_grapheme_result_validation.json"
OUT_REPORT = RES / "igr001_image_grounded_grapheme_result_validation.md"
SIGNATURE_FIELDS = ("main_vertical_stems", "closed_loops", "left_extension", "right_extension", "descender", "separated_dot")
LOCALIZATION_STATES = {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT", "DAMAGED_RETRACED_OR_AMBIGUOUS", "LOCALIZATION_UNRESOLVED"}
RESOLVED_STATES = {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not JPEG")
    i = 2
    while i + 9 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in {0xD8, 0xD9}:
            continue
        length = int.from_bytes(data[i:i + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            return int.from_bytes(data[i + 5:i + 7], "big"), int.from_bytes(data[i + 3:i + 5], "big")
        i += length
    raise ValueError("JPEG size marker not found")


def fetch_image(item: tuple[str, str, list[int]]) -> tuple[str, str, list[int]]:
    url, expected_hash, expected_dimensions = item
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-IGR001-validator/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    return url, hashlib.sha256(data).hexdigest(), list(jpeg_dimensions(data))


def render_report(result: dict[str, object]) -> str:
    gates = result["gates"]
    lines = [
        "# IGR001 image-grounded recurrent-disagreement result", "",
        f"Status: **{result['status']}**.", "",
        "The frozen source-only selection supplied 24 positions in eight recurrent manual-code triplets on "
        "19 physical folios. Native visual inspection used the official full-resolution Yale canvases and "
        "the preregistered neutral shape rubric; it used no OCR, CLIP, embedding, or automated image model.", "",
        "| type | localized targets | most common complete signature | matching targets | both conditions |",
        "|---:|---:|---|---:|:---:|",
    ]
    for item in result["type_summaries"]:
        signature = item["modal_complete_signature"]
        sig_text = "NA" if signature is None else "/".join(signature[name] for name in SIGNATURE_FIELDS)
        lines.append(f"| {item['type_index']} | {item['localized_target_count']}/3 | `{sig_text}` | {item['modal_signature_count']}/3 | {'yes' if item['meets_both_conditions'] else 'no'} |")
    lines.extend([
        "",
        f"Frozen gate reconstruction: {gates['localized_types']} localized types (threshold 6), "
        f"{gates['matching_shape_types']} matching-shape types (threshold 5), and "
        f"{gates['non_dominant_types_meeting_both']} non-dominant types meeting both (threshold 4).", "",
        f"Decision: **{result['decision']}**.", "",
        "These are machine-authored native-visual judgments, not independent human annotations. The result "
        "establishes at most whether recurrent transcription disagreements have enough visible-shape stability "
        "to justify a later preregistered grapheme atlas. It does not decide the correct transcription, name "
        "a grapheme, establish allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation.", "",
    ])
    return "\n".join(lines)


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    selection = json.loads(SELECTION.read_text())
    with OBSERVATIONS.open(newline="") as handle:
        raw = list(csv.DictReader(handle, delimiter="\t"))
    observations = result["observations"]
    checks: dict[str, bool] = {}
    checks["canonical_result_bytes"] = RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    checks["exact_24_frozen_ids_and_order"] = [x["opaque_id"] for x in observations] == [x["opaque_id"] for x in selection["targets"]] == [x["opaque_id"] for x in raw]
    checks["exact_eight_types_three_targets_each"] = Counter(x["type_index"] for x in observations) == Counter({i: 3 for i in range(1, 9)})
    checks["exact_19_folios"] = len({x["physical_folio"] for x in selection["targets"]}) == 19
    checks["all_judgments_explicitly_machine_authored"] = all(x["machine_authored_native_visual_judgment"] is True for x in observations) and result["access"]["independent_human_annotations_claimed"] is False
    checks["prohibited_automated_vision_absent"] = result["access"]["ocr_clip_embedding_or_automated_vision_used"] is False
    checks["all_crop_boxes_in_bounds"] = all(0 <= x["bounded_inspection_box_xyxy"][0] < x["bounded_inspection_box_xyxy"][2] <= x["official_dimensions"][0] and 0 <= x["bounded_inspection_box_xyxy"][1] < x["bounded_inspection_box_xyxy"][3] <= x["official_dimensions"][1] for x in observations)
    reconstructed_observations = []
    for row in raw:
        reconstructed_observations.append({
            "opaque_id": row["opaque_id"],
            "type_index": int(row["type_index"]),
            "page": row["page"],
            "locus": row["locus"],
            "canvas_id": row["canvas_id"],
            "official_full_image_url": row["official_full_image_url"],
            "official_full_image_sha256": row["official_full_image_sha256"],
            "official_dimensions": [int(row["image_width"]), int(row["image_height"])],
            "bounded_inspection_box_xyxy": [int(row[name]) for name in ("crop_x0", "crop_y0", "crop_x1", "crop_y1")],
            "localization_state": row["localization_state"],
            "confidence": row["confidence"],
            "shape_signature": {name: row[name] for name in SIGNATURE_FIELDS},
            "visible_note": row["visible_note"],
            "machine_authored_native_visual_judgment": True,
        })
    checks["complete_observation_payload_reconstructed_from_tsv"] = reconstructed_observations == observations
    checks["rubric_enums_and_signature_eligibility"] = all(
        x["localization_state"] in LOCALIZATION_STATES
        and x["confidence"] in {"HIGH", "MEDIUM", "LOW"}
        and (
            (x["localization_state"] in RESOLVED_STATES
             and x["shape_signature"]["main_vertical_stems"] in {"ZERO", "ONE", "TWO_PLUS"}
             and x["shape_signature"]["closed_loops"] in {"NONE", "ONE", "TWO_PLUS"}
             and all(x["shape_signature"][name] in {"YES", "NO"} for name in SIGNATURE_FIELDS[2:]))
            or (x["localization_state"] not in RESOLVED_STATES
                and all(x["shape_signature"][name] == "NA" for name in SIGNATURE_FIELDS))
        )
        for x in observations
    )
    checks["complete_frozen_target_provenance"] = all(
        observed["opaque_id"] == frozen["opaque_id"]
        and observed["type_index"] == frozen["type_index"]
        and observed["page"] == frozen["page"]
        and observed["locus"] == frozen["locus"]
        and observed["canvas_id"] == frozen["canvas_id"]
        and observed["official_dimensions"] == frozen["official_dimensions"]
        and observed["official_full_image_url"] == f"https://collections.library.yale.edu/iiif/2/{frozen['canvas_id']}/full/full/0/default.jpg"
        for observed, frozen in zip(observations, selection["targets"])
    )
    reconstructed_counts = {
        "targets": len(observations),
        "triplet_types": len({x["type_index"] for x in observations}),
        "physical_folios": len({x["physical_folio"] for x in selection["targets"]}),
        "official_canvases": len({x["canvas_id"] for x in observations}),
        "localized_targets": sum(x["localization_state"] != "LOCALIZATION_UNRESOLVED" for x in observations),
        "resolved_shape_signatures": sum(x["localization_state"] in RESOLVED_STATES for x in observations),
    }
    checks["complete_result_counts_reconstructed"] = result["counts"] == reconstructed_counts
    expected_inputs = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in (METHOD, OBSERVATIONS, SELECTION, SELECTION_VALIDATION)
    }
    checks["all_result_input_hashes_reconstructed"] = result["inputs"] == expected_inputs

    reconstructed_types = []
    for type_index in range(1, 9):
        rows = [x for x in observations if x["type_index"] == type_index]
        localized_count = sum(x["localization_state"] != "LOCALIZATION_UNRESOLVED" for x in rows)
        signatures = [tuple(x["shape_signature"][name] for name in SIGNATURE_FIELDS) for x in rows if x["localization_state"] in {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"}]
        counts = Counter(signatures)
        modal_tuple, modal_count = (max(counts.items(), key=lambda kv: (kv[1], kv[0])) if counts else (None, 0))
        stored = result["type_summaries"][type_index - 1]
        reconstructed_types.append({"localized": localized_count == 3, "matching": modal_count >= 2, "both": localized_count == 3 and modal_count >= 2, "non_dominant": type_index != 1})
        checks[f"type_{type_index}_summary_reconstructed"] = (
            stored["localized_target_count"] == localized_count and
            stored["all_three_targets_localized"] == (localized_count == 3) and
            stored["complete_signature_target_count"] == len(signatures) and
            stored["modal_signature_count"] == modal_count and
            stored["modal_complete_signature"] == (None if modal_tuple is None else dict(zip(SIGNATURE_FIELDS, modal_tuple))) and
            stored["at_least_two_matching_signatures"] == (modal_count >= 2) and
            stored["meets_both_conditions"] == (localized_count == 3 and modal_count >= 2)
        )
    reconstructed_gates = {
        "localized_types": sum(x["localized"] for x in reconstructed_types),
        "matching_shape_types": sum(x["matching"] for x in reconstructed_types),
        "non_dominant_types_meeting_both": sum(x["both"] and x["non_dominant"] for x in reconstructed_types),
    }
    checks["gate_counts_reconstructed"] = all(result["gates"][key] == value for key, value in reconstructed_gates.items())
    checks["gate_thresholds_frozen"] = all(
        result["gates"][f"{key}_threshold"] == selection["gates"][key]
        for key in ("localized_types", "matching_shape_types", "non_dominant_types_meeting_both")
    )
    reconstructed_passes = {
        f"{key}_pass": reconstructed_gates[key] >= selection["gates"][key]
        for key in reconstructed_gates
    }
    checks["gate_pass_booleans_reconstructed"] = all(result["gates"][key] == value for key, value in reconstructed_passes.items())
    passed = all(reconstructed_passes.values())
    expected_status = "PASS_VISIBLE_SHAPE_CAPACITY_FOR_LATER_IMAGE_GROUNDED_GRAPHEME_ATLAS" if passed else "STOP_VISIBLE_LIGHT_LOCALIZATION_CAPACITY"
    checks["status_follows_frozen_gates"] = result["status"] == expected_status
    expected_decision = "AUTHORIZE_LATER_PREREGISTERED_IMAGE_GROUNDED_GRAPHEME_ATLAS" if passed else "DO_NOT_BUILD_IMAGE_GROUNDED_GRAPHEME_ATLAS_FROM_THIS_PANEL"
    checks["decision_follows_frozen_gates"] = result["decision"] == expected_decision
    checks["report_exactly_reconstructed"] = REPORT.read_text() == render_report(result)

    unique = {}
    for x in observations:
        unique[x["official_full_image_url"]] = (x["official_full_image_url"], x["official_full_image_sha256"], x["official_dimensions"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        fetched = list(pool.map(fetch_image, unique.values()))
    fetched_map = {url: (digest, dims) for url, digest, dims in fetched}
    checks["all_official_full_image_bytes_hash_match"] = all(fetched_map[url] == (expected_hash, expected_dims) for url, expected_hash, expected_dims in unique.values())
    checks["exact_official_canvas_count"] = len(unique) == result["counts"]["official_canvases"] == 20
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    validation = {
        "experiment": "IGR001_IMAGE_GROUNDED_GRAPHEME_RESULT_VALIDATION",
        "schema": "IGR001_IMAGE_GROUNDED_GRAPHEME_RESULT_VALIDATION_V1",
        "status": f"PASS_{len(checks)}_CHECK_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "producer_sha256": sha256(PRODUCER),
        "validated_result_sha256": sha256(RESULT),
        "validated_report_sha256": sha256(REPORT),
        "official_image_bytes_live_reacquired": True,
        "official_canvas_count": len(unique),
        "visual_judgments_independently_reperformed": False,
        "reconstructed_gates": reconstructed_gates,
        "claim_ceiling": "Validation reconstructs source bindings and recorded-judgment arithmetic; it supplies no independent visual judgment, grapheme name, text meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n")
    OUT_REPORT.write_text(
        "# IGR001 result validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"Independently reconstructed all result arithmetic and live-reacquired/hash-matched {len(unique)} official Yale full-resolution canvases. "
        "The validator does not claim a second visual inspection.\n"
    )


if __name__ == "__main__":
    main()
