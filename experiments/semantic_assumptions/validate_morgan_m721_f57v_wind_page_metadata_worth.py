#!/usr/bin/env python3
"""Independent live reconstruction of the Morgan M.721 f57v worth check."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "MORGAN_M721_F57V_WIND_PAGE_METADATA_WORTH_CHECK_SPEC.md"
PRODUCER = BASE / "check_morgan_m721_f57v_wind_page_metadata_worth.py"
REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
RESULT = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth.json"
REPORT = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth_report.md"
OUT_JSON = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "morgan_m721_f57v_wind_page_metadata_worth_validation_report.md"
URL = "https://ica.themorgan.org/manuscript/page/9/128486"

FROZEN = {
    SPEC: "e0e8d4d4bcc518778c28f77973efdeb097b0de4379f82f9a01ea820d72edd016",
    PRODUCER: "c2e5468b7eee7f4849a9b8e4ad6210366c19a02c4c890d64639e2887af3f47b9",
    REGISTRY: "0261d2e7856ddf26b18fe46915f66446734dcc687cc516dac4aa23c4704b7a1c",
    RESULT: "cf5eff5ee093a2fbb14352f8703e1efbf9c2bcd4a3ca97886996c8de260b9a39",
    REPORT: "3d18673eaf5d7d9a4baf15d11dc3cf167aa7fd1eb7553281d3983e312df711fb",
}
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


def live_text() -> str:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-Morgan-M721-worth-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected Morgan response")
        raw = response.read()
    return re.sub(r"\s+", " ", raw.decode("utf-8")).strip()


def strict_json() -> dict[str, object]:
    raw = RESULT.read_text(encoding="utf-8")
    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate result key")
        return dict(items)
    value = json.loads(raw, object_pairs_hook=hook, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError("noncanonical result JSON")
    return value


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Morgan validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_json()
    checks.append("canonical_duplicate_free_result")
    text = live_text()
    phrase_checks = {phrase: phrase in text for phrase in EVIDENCE}
    if not all(phrase_checks.values()):
        raise ValueError("live evidence projection mismatch")
    checks.extend(("live_official_html", "manuscript_folio_identity", "place_date_identity", "sun_moon_diagram", "four_wind_faces", "four_face_labels", "separate_wind_wheel"))
    projection = "\n".join(EVIDENCE).encode("utf-8") + b"\n"
    if sha(projection) != result["source"]["evidence_projection_sha256"]:
        raise ValueError("evidence projection digest mismatch")
    checks.append("stable_evidence_projection")
    if "A complete readable homologue with the same four-person and two-label-register topology" not in REGISTRY.read_text(encoding="utf-8"):
        raise ValueError("acquisition bar mismatch")
    checks.append("f57_acquisition_bar")
    if all(phrase in text.replace("Wheel diagram with names of winds, in lower right margin", "") for phrase in EVIDENCE):
        raise ValueError("separate-wheel mutation failed")
    checks.append("separate_wheel_required_mutation")

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
    expected = {
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
        "inputs": {str(SPEC.relative_to(BASE)): FROZEN[SPEC], str(REGISTRY.relative_to(BASE)): FROZEN[REGISTRY]},
        "claim_ceiling": "Morgan M.721 f13r is a close same-page four-wind comparandum, but its separately catalogued face-label and wind-wheel diagrams supply no f57v slot mapping, wind, direction, quality, element, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.append("result_object_exact")
    report = (
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
        "label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")
    validation = {
        "experiment": "MORGAN_M721_F57V_WIND_PAGE_METADATA_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_OFFICIAL_SOURCE_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "gates": gates,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Morgan M.721 f13r / f57v metadata worth check — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator live-refetches the official Morgan page and reconstructs the "
        "four readable face labels, separately catalogued wind wheel, acquisition-bar failure, result, and report.\n\n"
        "This stops before images, codex or paper review, and roster selection. It supplies no f57v wind, direction, "
        "quality, element, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
