#!/usr/bin/env python3
"""Text-only worth check for Morgan M.721 f13r as an f57v homologue."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "MORGAN_M721_F57V_WIND_PAGE_METADATA_WORTH_CHECK_SPEC.md"
REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
URL = "https://ica.themorgan.org/manuscript/page/9/128486"
OUT_JSON = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth.json"
OUT_REPORT = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth_report.md"

EVIDENCE = (
    "La sfera",
    "Italy, probably Florence, second half of 15th century",
    "MS M.721 fol. 13r",
    "Diagram showing sun (personified) labeled SOLE",
    "Diagram of four winds personified as faces labeled PLAGA ORIE(N)TALE, PLAGA SETTANTRONALE, PLAGA MERIDIONALE, and PLAGA OCCIDE(N)TALE",
    "Wheel diagram with names of winds, in lower right margin",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get() -> str:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-Morgan-M721-worth-check/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected Morgan response")
        raw = response.read()
    return re.sub(r"\s+", " ", raw.decode("utf-8")).strip()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Morgan worth-check outputs")
    text = get()
    phrase_checks = {phrase: phrase in text for phrase in EVIDENCE}
    if not all(phrase_checks.values()):
        raise ValueError("Morgan evidence projection drift")
    registry = REGISTRY.read_text(encoding="utf-8")
    requested = "A complete readable homologue with the same four-person and two-label-register topology"
    if requested not in registry:
        raise ValueError("f57 acquisition bar drift")
    projection = "\n".join(EVIDENCE).encode("utf-8") + b"\n"
    gates = {
        "single_physical_page": True,
        "four_personified_wind_faces": True,
        "four_readable_face_direction_labels": True,
        "wind_name_wheel_on_same_page": True,
        "same_integrated_diagram": False,
        "author_visible_mapping_between_face_labels_and_wheel_names": False,
        "same_four_person_two_register_topology_as_f57v": False,
        "preserved_start_orientation_mapping_to_f57v": False,
    }
    result = {
        "experiment": "MORGAN_M721_F57V_WIND_PAGE_METADATA_WORTH_CHECK",
        "status": "PASS_OFFICIAL_HUMAN_METADATA_NEAR_MATCH_IDENTIFIED",
        "decision": "STOP_BEFORE_IMAGE_CODEX_PAPER_OR_ROSTER_REVIEW_SEPARATE_DIAGRAMS_NO_SLOT_MAPPING",
        "source": {
            "url": URL,
            "title": "La sfera",
            "manuscript_folio": "MS M.721 fol. 13r",
            "place_date": "Italy, probably Florence, second half of 15th century",
            "evidence_projection_sha256": sha(projection),
        },
        "phrase_checks": phrase_checks,
        "gates": gates,
        "label_values": ["PLAGA ORIE(N)TALE", "PLAGA SETTANTRONALE", "PLAGA MERIDIONALE", "PLAGA OCCIDE(N)TALE"],
        "source_access": {
            "official_html_opened": True,
            "images_or_thumbnails_opened": False,
            "papers_pdfs_or_codex_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claim_or_wind_roster_opened": False,
        },
        "inputs": {
            str(SPEC.relative_to(BASE)): sha(SPEC.read_bytes()),
            str(REGISTRY.relative_to(BASE)): sha(REGISTRY.read_bytes()),
        },
        "claim_ceiling": "Morgan M.721 f13r is a close same-page four-wind comparandum, but its separately catalogued face-label and wind-wheel diagrams supply no f57v slot mapping, wind, direction, quality, element, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Morgan M.721 f13r / f57v metadata worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_CODEX_PAPER_OR_ROSTER_REVIEW_SEPARATE_DIAGRAMS_NO_SLOT_MAPPING**.\n\n"
        "The Morgan Library's human-curated entry identifies a genuine close same-page comparandum: four winds "
        "personified as faces and labelled with four cardinal `PLAGA ...` phrases, plus a wind-name wheel lower on "
        "the same folio. This is stronger than a generic four-quality wheel because the four face labels are explicit.\n\n"
        "It still does not meet the acquisition bar. The catalogue describes the faces and wheel as separate diagrams "
        "and publishes no connector, one-to-one face-to-wheel mapping, shared start/orientation, or integrated two-register "
        "topology corresponding to f57v. Opening the image or selecting a wind roster cannot repair that missing public relation.\n\n"
        "No image, thumbnail, codex, paper, PDF, OCR, automated visual output, decoder claim, or wind roster entered this "
        "result. M.721 remains a close four-wind comparandum only and supplies no f57v wind, direction, quality, element, "
        "label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
