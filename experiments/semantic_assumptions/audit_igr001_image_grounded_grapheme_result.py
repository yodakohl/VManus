#!/usr/bin/env python3
"""Serialize the frozen IGR001 native-vision observations and capacity result."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "IGR001_IMAGE_GROUNDED_GRAPHEME_METHOD.md"
OBSERVATIONS = BASE / "igr001_image_grounded_grapheme_observations.tsv"
SELECTION = RES / "igr001_image_grounded_grapheme_selection.json"
SELECTION_VALIDATION = RES / "igr001_image_grounded_grapheme_selection_validation.json"
OUT = RES / "igr001_image_grounded_grapheme_result.json"
REPORT = RES / "igr001_image_grounded_grapheme_result_report.md"

LOCALIZATION_STATES = {
    "ONE_CLEAR_VISIBLE_UNIT",
    "LIGATED_OR_COMPOSITE_UNIT",
    "DAMAGED_RETRACED_OR_AMBIGUOUS",
    "LOCALIZATION_UNRESOLVED",
}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
STEMS = {"ZERO", "ONE", "TWO_PLUS"}
LOOPS = {"NONE", "ONE", "TWO_PLUS"}
YN = {"YES", "NO"}
SIGNATURE_FIELDS = (
    "main_vertical_stems",
    "closed_loops",
    "left_extension",
    "right_extension",
    "descender",
    "separated_dot",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_observations() -> list[dict[str, object]]:
    with OBSERVATIONS.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 24:
        raise SystemExit(f"expected 24 observations, got {len(rows)}")
    out: list[dict[str, object]] = []
    for row in rows:
        state = row["localization_state"]
        if state not in LOCALIZATION_STATES or row["confidence"] not in CONFIDENCE:
            raise SystemExit(f"invalid rubric value for {row['opaque_id']}")
        resolved = state in {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"}
        sig = tuple(row[name] for name in SIGNATURE_FIELDS)
        if resolved:
            if sig[0] not in STEMS or sig[1] not in LOOPS or any(x not in YN for x in sig[2:]):
                raise SystemExit(f"invalid complete signature for {row['opaque_id']}")
        elif sig != ("NA",) * 6:
            raise SystemExit(f"non-resolved target has a signature for {row['opaque_id']}")
        width, height = int(row["image_width"]), int(row["image_height"])
        box = [int(row[x]) for x in ("crop_x0", "crop_y0", "crop_x1", "crop_y1")]
        if not (0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height):
            raise SystemExit(f"invalid crop for {row['opaque_id']}")
        out.append({
            "opaque_id": row["opaque_id"],
            "type_index": int(row["type_index"]),
            "page": row["page"],
            "locus": row["locus"],
            "canvas_id": row["canvas_id"],
            "official_full_image_url": row["official_full_image_url"],
            "official_full_image_sha256": row["official_full_image_sha256"],
            "official_dimensions": [width, height],
            "bounded_inspection_box_xyxy": box,
            "localization_state": state,
            "confidence": row["confidence"],
            "shape_signature": dict(zip(SIGNATURE_FIELDS, sig)),
            "visible_note": row["visible_note"],
            "machine_authored_native_visual_judgment": True,
        })
    return out


def render_report(status: str, decision: str, types: list[dict[str, object]], gates: dict[str, object]) -> str:
    lines = [
        "# IGR001 image-grounded recurrent-disagreement result",
        "",
        f"Status: **{status}**.",
        "",
        "The frozen source-only selection supplied 24 positions in eight recurrent manual-code triplets on "
        "19 physical folios. Native visual inspection used the official full-resolution Yale canvases and "
        "the preregistered neutral shape rubric; it used no OCR, CLIP, embedding, or automated image model.",
        "",
        "| type | localized targets | most common complete signature | matching targets | both conditions |",
        "|---:|---:|---|---:|:---:|",
    ]
    for item in types:
        signature = item["modal_complete_signature"]
        sig_text = "NA" if signature is None else "/".join(signature[name] for name in SIGNATURE_FIELDS)
        lines.append(
            f"| {item['type_index']} | {item['localized_target_count']}/3 | `{sig_text}` | "
            f"{item['modal_signature_count']}/3 | {'yes' if item['meets_both_conditions'] else 'no'} |"
        )
    lines.extend([
        "",
        f"Frozen gate reconstruction: {gates['localized_types']} localized types (threshold 6), "
        f"{gates['matching_shape_types']} matching-shape types (threshold 5), and "
        f"{gates['non_dominant_types_meeting_both']} non-dominant types meeting both (threshold 4).",
        "",
        f"Decision: **{decision}**.",
        "",
        "These are machine-authored native-visual judgments, not independent human annotations. The result "
        "establishes at most whether recurrent transcription disagreements have enough visible-shape stability "
        "to justify a later preregistered grapheme atlas. It does not decide the correct transcription, name "
        "a grapheme, establish allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    observations = load_observations()
    selected = selection["targets"]
    if [x["opaque_id"] for x in observations] != [x["opaque_id"] for x in selected]:
        raise SystemExit("observation order does not match frozen selection")
    for observed, frozen in zip(observations, selected):
        expected_url = f"https://collections.library.yale.edu/iiif/2/{frozen['canvas_id']}/full/full/0/default.jpg"
        if any(observed[key] != frozen[key] for key in ("opaque_id", "type_index", "page", "locus", "canvas_id")):
            raise SystemExit(f"selection mismatch for {frozen['opaque_id']}")
        if observed["official_dimensions"] != frozen["official_dimensions"] or observed["official_full_image_url"] != expected_url:
            raise SystemExit(f"image binding mismatch for {frozen['opaque_id']}")
        if len(observed["official_full_image_sha256"]) != 64:
            raise SystemExit(f"invalid image hash for {frozen['opaque_id']}")

    type_summaries: list[dict[str, object]] = []
    for type_index in range(1, 9):
        rows = [x for x in observations if x["type_index"] == type_index]
        if len(rows) != 3:
            raise SystemExit(f"type {type_index} does not have three targets")
        localized_count = sum(x["localization_state"] != "LOCALIZATION_UNRESOLVED" for x in rows)
        signatures = [tuple(x["shape_signature"][name] for name in SIGNATURE_FIELDS)
                      for x in rows if x["localization_state"] in {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"}]
        counts = Counter(signatures)
        modal_tuple, modal_count = (max(counts.items(), key=lambda kv: (kv[1], kv[0])) if counts else (None, 0))
        localized = localized_count == 3
        matching = modal_count >= 2
        first = next(x for x in selected if x["type_index"] == type_index)
        type_summaries.append({
            "type_index": type_index,
            "family": first["family"],
            "manual_code_triplet": [first["zl_code"], first["it_code"], first["rf_code"]],
            "dominant_reference_type": type_index == 1,
            "localized_target_count": localized_count,
            "all_three_targets_localized": localized,
            "complete_signature_target_count": len(signatures),
            "modal_complete_signature": None if modal_tuple is None else dict(zip(SIGNATURE_FIELDS, modal_tuple)),
            "modal_signature_count": modal_count,
            "at_least_two_matching_signatures": matching,
            "meets_both_conditions": localized and matching,
            "target_ids": [x["opaque_id"] for x in rows],
        })
    gates = {
        "localized_types": sum(x["all_three_targets_localized"] for x in type_summaries),
        "localized_types_threshold": selection["gates"]["localized_types"],
        "localized_types_pass": False,
        "matching_shape_types": sum(x["at_least_two_matching_signatures"] for x in type_summaries),
        "matching_shape_types_threshold": selection["gates"]["matching_shape_types"],
        "matching_shape_types_pass": False,
        "non_dominant_types_meeting_both": sum(x["meets_both_conditions"] and not x["dominant_reference_type"] for x in type_summaries),
        "non_dominant_types_meeting_both_threshold": selection["gates"]["non_dominant_types_meeting_both"],
        "non_dominant_types_meeting_both_pass": False,
    }
    gates["localized_types_pass"] = gates["localized_types"] >= gates["localized_types_threshold"]
    gates["matching_shape_types_pass"] = gates["matching_shape_types"] >= gates["matching_shape_types_threshold"]
    gates["non_dominant_types_meeting_both_pass"] = (
        gates["non_dominant_types_meeting_both"] >= gates["non_dominant_types_meeting_both_threshold"]
    )
    passed = all(gates[key] for key in (
        "localized_types_pass", "matching_shape_types_pass", "non_dominant_types_meeting_both_pass"
    ))
    status = ("PASS_VISIBLE_SHAPE_CAPACITY_FOR_LATER_IMAGE_GROUNDED_GRAPHEME_ATLAS" if passed
              else "STOP_VISIBLE_LIGHT_LOCALIZATION_CAPACITY")
    decision = ("AUTHORIZE_LATER_PREREGISTERED_IMAGE_GROUNDED_GRAPHEME_ATLAS" if passed
                else "DO_NOT_BUILD_IMAGE_GROUNDED_GRAPHEME_ATLAS_FROM_THIS_PANEL")
    result = {
        "experiment": "IGR001_IMAGE_GROUNDED_GRAPHEME_RESULT",
        "schema": "IGR001_IMAGE_GROUNDED_GRAPHEME_RESULT_V1",
        "status": status,
        "decision": decision,
        "observations": observations,
        "type_summaries": type_summaries,
        "gates": gates,
        "counts": {
            "targets": len(observations),
            "triplet_types": len(type_summaries),
            "physical_folios": len({x["physical_folio"] for x in selected}),
            "official_canvases": len({x["canvas_id"] for x in observations}),
            "localized_targets": sum(x["localization_state"] != "LOCALIZATION_UNRESOLVED" for x in observations),
            "resolved_shape_signatures": sum(x["localization_state"] in {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"} for x in observations),
        },
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, OBSERVATIONS, SELECTION, SELECTION_VALIDATION)},
        "access": {
            "selection_frozen_before_target_images": True,
            "all_selected_official_full_resolution_images_opened": True,
            "machine_authored_native_visual_judgments": True,
            "independent_human_annotations_claimed": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "manual_code_identity_used_only_to_localize_frozen_positions": True,
            "semantic_or_preferred_reading_judgment_made": False,
        },
        "claim_ceiling": (
            "The result establishes at most visible-shape capacity behind recurrent manual reading disagreements. "
            "It cannot decide the correct transcription, name an authorial grapheme, establish allography, sound, "
            "alphabet, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(render_report(status, decision, type_summaries, gates))


if __name__ == "__main__":
    main()
