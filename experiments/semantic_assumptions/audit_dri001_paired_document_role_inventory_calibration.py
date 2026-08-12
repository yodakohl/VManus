#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY_METHOD.md"
SELECTION = RES / "dri001_paired_document_role_inventory_selection.json"
SELECTION_VALIDATION = RES / "dri001_paired_document_role_inventory_selection_validation.json"
OUT = RES / "dri001_paired_document_role_inventory_calibration.json"
REPORT = RES / "dri001_paired_document_role_inventory_calibration_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# SHA-256 of the exact Yale IIIF 1600-pixel review witnesses. Two logical
# f102r parts deliberately share one official foldout image.
IMAGE_SHA = {
    "1006106": "3c2b2c224c797a33f3f0d00fdeaa4c3643eedcf0015a983b8d7bb2d30bf44241",
    "1006183": "3d2a930da0504af0393ee3c19e279291efd3382512656e64371b18fe29210432",
    "1006197": "cb95e2e015566be12188a32a27f917471ad259aaf77c302c0041ffeac062db3a",
    "1006204": "a92adc853dc9c481ae96ee9a0429476c8662398edda84fd8ee55544fbbc3438a",
    "1006207": "6ddf7fef398c1a0ad6d8137781eb4ef9d712026c6fb4580d45b60d1b2c47f076",
    "1006219": "db5a89702d143efecbe3a632e0a9a0cbf7344938a2ba6adac617913a7f183eac",
    "1006225": "cf7bb572d4709773c9f1a82a41eb59d96edf314a6a0338405118999628cd4dbb",
    "1006226": "fe8f16fa61ce137db6296e02994edcdd34c2f25897e39c25d677c1adbe9f558b",
    "1006230": "3c943a512d9ad93ee610967a9101518b91acac2a5b4869a9475297338a0a2f91",
    "1006235": "e9eeebabc6242c931f25dc3f2e8bdfa6b1ba7e965a9da73f794c7a989cc8e776",
    "1006248": "9efbbe3305c9f963516665d95e62dd44b6a7c191d611a420ef0dabcb9b07ff7f",
    "1006250": "755dd2adce5242788b6112db6deb97f0a6f0778878a4bda78130c09e4499734b",
    "1006251": "65c113a9874d192c891a36b6d9e9eab1125920c6664c59bc172e499ed23aa823",
    "1006262": "184a036f6fb161742fedbf3746c09a4e14ba209d001ddcab6de3059a43cd246e",
}


# Evidence vector order: continuous prose, dominant illustration, repeated
# object/cell template, singular ownership devices, diagram-defined slots.
JUDGMENTS = {
    "f68v2": (
        "DIAGRAM_PARAMETER_ARRAY", (True, True, True, False, True),
        "The selected foldout part has a compact prose block plus a circular construction whose repeated radial and annular inscription positions are fixed by the drawing; no singular caption ownership is used.",
    ),
    "f84r": (
        "REPEATED_OWNED_RECORDS", (True, False, True, True, False),
        "Repeated drawn human-form units occupy separated canopy bays and local stacks. At least three inscription stacks are visibly reserved over distinct units by bay divisions and horizontal separation, alongside prose blocks.",
    ),
    "f80v": (
        "PROSE_DOMINANT", (True, False, True, False, False),
        "A continuous multi-paragraph writing field dominates the page. Repeated marginal drawn units interrupt or frame it but have no repeated singular inscription slots.",
    ),
    "f83v": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "Large linked painted forms and several smaller drawn units share the page with two continuous prose blocks; nearby short inscriptions are not assigned by repeated singular ownership devices.",
    ),
    "f55v": (
        "OBJECT_WITH_PROSE", (True, True, False, False, False),
        "One large branching painted illustration dominates the page while continuous prose blocks occupy the remaining spaces; no singular caption connector or repeated owner cells are visible.",
    ),
    "f17r": (
        "OBJECT_WITH_PROSE", (True, True, False, False, False),
        "One large branching painted illustration dominates most of the page and continuous prose wraps above and beside it without a singular caption assignment device.",
    ),
    "f101v": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "A field of separated painted object fragments and containers occupies most of the page above a continuous prose block. Short nearby inscriptions rely on proximity rather than leaders, cells, or consistently reserved owner stacks.",
    ),
    "f100r": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "Two broad fields of separated painted fragments and containers alternate with continuous prose. The inscriptions are nearby but do not form at least three securely assigned owner slots.",
    ),
    "f89v2": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected foldout part alternates compact prose blocks with multiple painted fragments and containers. Their open spacing supplies proximity, not a repeated leader, enclosure, divider, or secure owner stack.",
    ),
    "f102r1": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected middle foldout part alternates prose blocks with several painted fragment and container fields. The open layout does not give at least three inscriptions secure singular ownership.",
    ),
    "f102r2": (
        "OBJECT_WITH_PROSE", (True, True, True, False, False),
        "The selected right foldout part alternates prose blocks with several painted fragment and container fields. Nearby writing lacks repeated author-visible singular assignment devices.",
    ),
    "f107r": (
        "PROSE_DOMINANT", (True, False, True, False, False),
        "Continuous lines fill nearly the whole page in a sequence of compact entries marked by repeated small margin signs; there is no dominant illustration or diagram-defined slot array.",
    ),
    "f86v5": (
        "PROSE_DOMINANT", (True, False, False, False, False),
        "The selected left foldout part is an uninterrupted dense multi-line prose field; the drawings belong to the neighboring logical part rather than this selected region.",
    ),
    "f72v3": (
        "DIAGRAM_PARAMETER_ARRAY", (False, True, True, False, True),
        "The selected zodiac foldout part is organized by concentric circular bands with repeated drawn units and inscriptions occupying annular positions fixed by the diagram, not a prose block or singular captions.",
    ),
    "f73v": (
        "DIAGRAM_PARAMETER_ARRAY", (False, True, True, False, True),
        "Concentric bands organize repeated drawn units and inscriptions around a center. The cyclic diagram supplies the visible slot system and there is no continuous prose block.",
    ),
}


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    rows = [row for row in selection["rows"] if row["phase"] == "CALIBRATION"]
    if [row["page"] for row in rows] != list(JUDGMENTS):
        raise SystemExit("calibration row order changed")
    observations = []
    for row in rows:
        role, flags, basis = JUDGMENTS[row["page"]]
        observations.append({
            "cell_id": row["cell_id"],
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "canvas_id": row["canvas_id"],
            "review_image_url": row["review_image_url"],
            "review_image_sha256": IMAGE_SHA[row["canvas_id"]],
            "role": role,
            "evidence": {
                "continuous_prose_block": flags[0],
                "dominant_illustration": flags[1],
                "repeated_object_or_cell_template": flags[2],
                "singular_ownership_devices": flags[3],
                "diagram_defined_slots": flags[4],
            },
            "visible_basis": basis,
            "uncertainty": "LOW",
            "machine_authored_native_visual_judgment": True,
        })
    roles = Counter(row["role"] for row in observations)
    unresolved = roles["MIXED_OR_UNRESOLVED"]
    gate = unresolved <= selection["calibration_gate"]["maximum_unresolved"]
    result = {
        "experiment": "DRI001_PAIRED_DOCUMENT_ROLE_INVENTORY_CALIBRATION",
        "schema": "DRI001_CALIBRATION_V1",
        "status": "PASS_CALIBRATION_ZERO_UNRESOLVED_NO_RUBRIC_AMENDMENT",
        "decision": "AUTHORIZE_SEALED_DIAGNOSTIC_IMAGE_ACCESS",
        "observations": observations,
        "counts": {
            "pages": len(observations),
            "physical_folios": len({row["physical_folio"] for row in observations}),
            "unique_canvases": len({row["canvas_id"] for row in observations}),
            "unresolved": unresolved,
            "distinct_nonunresolved_roles": len([role for role in roles if role != "MIXED_OR_UNRESOLVED"]),
            "role_counts": {role: roles.get(role, 0) for role in selection["rubric_roles"]},
        },
        "calibration_gate": {
            "maximum_unresolved": selection["calibration_gate"]["maximum_unresolved"],
            "observed_unresolved": unresolved,
            "rubric_amendment_required": False,
            "passes": gate,
        },
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION)},
        "access": {
            "calibration_images_opened_after_selection_publication": True,
            "diagnostic_images_opened_during_calibration": False,
            "official_source_native_pixels_used": True,
            "machine_authored_native_visual_judgments": True,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "transcription_identity_or_formal_fillers_used": False,
            "rubric_amended_after_image_access": False,
        },
        "claim_ceiling": "The unchanged five-role rubric resolves all fifteen calibration pages and authorizes the sealed diagnostic half. This is a machine-authored native-visual calibration, not literal human annotation. It establishes no manuscript-wide document class heading caption field name word POS sound language cipher plaintext meaning or translation.",
    }
    if not gate:
        raise SystemExit("calibration gate failed")
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# DRI001 paired document-role calibration\n\n"
        "Status: **PASS_CALIBRATION_ZERO_UNRESOLVED_NO_RUBRIC_AMENDMENT**.\n\n"
        "All fifteen calibration pages were inspected once on their frozen official Yale witnesses. The unchanged rubric yields three `PROSE_DOMINANT`, eight `OBJECT_WITH_PROSE`, one `REPEATED_OWNED_RECORDS`, three `DIAGRAM_PARAMETER_ARRAY`, and zero `MIXED_OR_UNRESOLVED` judgments. Four non-unresolved roles are represented, and the frozen maximum of three unresolved pages is met with zero. The sealed diagnostic half is therefore authorized.\n\n"
        "The judgments are machine-authored direct native visual observations under the user's prospective authorization, not literal human annotation. No OCR, CLIP, embeddings, batch recognition, transcription identity, or formal filler entered. This calibration supplies no document-wide class, heading, caption, field name, word, POS, sound, language, cipher, plaintext, meaning, or translation.\n"
    )


if __name__ == "__main__":
    main()
