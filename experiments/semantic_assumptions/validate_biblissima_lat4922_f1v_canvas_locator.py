#!/usr/bin/env python3
"""Independent live validation of the Latin 4922 f1v locator stop."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "BIBLISSIMA_LAT4922_F1V_CANVAS_LOCATOR_SPEC.md"
PRODUCER = BASE / "check_biblissima_lat4922_f1v_canvas_locator.py"
WORTH = RESULTS / "biblissima_f57_fourfold_metadata_worth.json"
RESULT = RESULTS / "biblissima_lat4922_f1v_canvas_locator.json"
REPORT = RESULTS / "biblissima_lat4922_f1v_canvas_locator_report.md"
OUT = RESULTS / "biblissima_lat4922_f1v_canvas_locator_validation.json"
OUT_MD = RESULTS / "biblissima_lat4922_f1v_canvas_locator_validation_report.md"
MANIFEST = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/manifest.json"
PAGINATION = "https://gallica.bnf.fr/services/Pagination?ark=btv1b9066969x"
WITNESS = "https://gallica.bnf.fr/ark:/12148/btv1b9066969x"
FROZEN = {
    SPEC: "58d859b10e7ddefdfd9fef51405f8d2613395b03e1a1cfa8be1178797c2b8be9",
    PRODUCER: "9370730580f417bc125fce4a7209a6a209bdb6234a63f01ef5876254042283d2",
    WORTH: "3d581c40330763ddef573e115e7cd3f5d8090c2516141cb8dd65cf01d6a48126",
    RESULT: "f1fc48f0803ad77115d9a2fe79849dbd229e915747fe03d3b250fedc1f0fbc17",
    REPORT: "abe2bc0f2a45b06ec77d395bff0360f4bb8c31895ec3659e57ed61e7b320a085",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def read_result() -> dict[str, object]:
    raw = RESULT.read_bytes()

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        if len(pairs) != len({key for key, _ in pairs}):
            raise ValueError("duplicate JSON key")
        return dict(pairs)

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=hook, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value, dict) or canonical(value) != raw:
        raise ValueError("result canonicality drift")
    return value


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Lat4922-locator-validator/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location") is not None:
            raise ValueError("unexpected repository response")
        return response.read()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing to overwrite locator validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen hash drift: {path.name}")
        checks.append(f"sha256:{path.name}")
    source_result = read_result()
    checks.append("canonical_duplicate_free_result")
    manifest = json.loads(fetch(MANIFEST).decode("utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    sequences = manifest.get("sequences")
    if not isinstance(sequences, list) or len(sequences) != 1 or not isinstance(sequences[0], dict):
        raise ValueError("sequence schema drift")
    canvases = sequences[0].get("canvases")
    if not isinstance(canvases, list):
        raise ValueError("canvas schema drift")
    expected_ids = [f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/canvas/f{index}" for index in range(1, 200)]
    if [row.get("@id") for row in canvases] != expected_ids or [row.get("label") for row in canvases] != ["NP"] * 199:
        raise ValueError("canvas orbit drift")
    if manifest.get("structures", []) != []:
        raise ValueError("unexpected logical structures")
    checks.extend(("manifest_identity", "one_sequence", "199_sequential_canvases", "all_canvas_labels_np", "zero_logical_ranges"))
    root = ET.fromstring(fetch(PAGINATION))
    pages = root.findall(".//page")
    numbers = [row.findtext("numero") for row in pages]
    orders = [row.findtext("ordre") for row in pages]
    types = [row.findtext("pagination_type") for row in pages]
    legends = [row.findtext("legend") for row in pages]
    if numbers != ["NP"] * 199 or orders != list(map(str, range(1, 200))) or types != ["N"] * 199 or any(value not in (None, "") for value in legends):
        raise ValueError("pagination orbit drift")
    checks.extend(("199_pagination_entries", "all_numero_np", "orders_1_through_199", "all_type_n", "zero_legends"))
    expected = {
        "experiment": "BIBLISSIMA_LAT4922_F1V_CANVAS_LOCATOR",
        "status": "STOP_NO_REPOSITORY_LOGICAL_FOLIATION",
        "decision": "QUALIFIED_HUMAN_MUST_NAVIGATE_TO_PHYSICAL_F1V_NO_SCAN_OFFSET_GUESS",
        "source": {"manifest_url": MANIFEST, "pagination_url": PAGINATION, "official_witness_url": WITNESS},
        "manifest": {"id": manifest.get("@id"), "label": manifest.get("label"), "canvas_count": 199, "unique_canvas_label": "NP", "logical_structure_count": 0, "sequential_canvas_ids_f1_through_f199": True},
        "pagination": {"page_count": 199, "unique_numero": "NP", "orders_are_1_through_199": True, "unique_pagination_type": "N", "legend_count": 0},
        "gates": {"physical_f1v_named_by_biblissima_and_mandragore": True, "repository_canvas_label_or_range_maps_f1v": False, "exact_page_specific_canvas_locator_available": False, "manual_navigation_required": True, "scan_offset_inferred": False},
        "source_access": {"iiif_manifest_metadata_opened": True, "pagination_xml_opened": True, "canvas_thumbnail_image_info_ocr_pdf_or_pixels_opened": False, "automated_visual_output_used": False},
        "inputs": {SPEC.name: FROZEN[SPEC], str(WORTH.relative_to(BASE)): FROZEN[WORTH]},
        "claim_ceiling": "Gallica supplies a complete 199-canvas witness but no repository-authored logical mapping from physical f.1v to a canvas; a qualified human must navigate the official viewer and no scan offset, visual topology, Voynich label, word, sound, language, cipher, plaintext, meaning, or translation may be inferred.",
    }
    if source_result != expected:
        raise ValueError("exact result reconstruction drift")
    checks.extend(("exact_gate_vector", "no_scan_offset_inference", "exact_result_object"))
    expected_report = (
        "# Biblissima Latin 4922 f1v canvas locator\n\n"
        "Decision: **QUALIFIED_HUMAN_MUST_NAVIGATE_TO_PHYSICAL_F1V_NO_SCAN_OFFSET_GUESS**.\n\n"
        "The official Gallica IIIF manifest contains 199 sequential canvases, all labelled `NP`, and no logical ranges. The independent Gallica Pagination service likewise contains 199 sequential entries, all numbered `NP`, all type `N`, with no legends. These services therefore do not map physical f.1v to one scan.\n\n"
        "The official whole-manuscript witness remains the correct human-review entry point. A qualified reviewer must navigate to physical f.1v in the viewer; covers and flyleaves make a guessed numeric offset inadmissible. No canvas image, thumbnail, image-service metadata, OCR, PDF, or manuscript pixels entered this locator.\n\n"
        "This operational stop supplies no visual topology, Voynich label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise ValueError("report reconstruction drift")
    checks.append("exact_report_bytes")
    validation = {
        "experiment": "BIBLISSIMA_LAT4922_F1V_CANVAS_LOCATOR_VALIDATION",
        "status": "PASS_INDEPENDENT_REPOSITORY_METADATA_STOP_RECONSTRUCTION",
        "decision": source_result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "counts": {"manifest_canvases": 199, "pagination_entries": 199, "logical_folio_labels": 0, "legends": 0, "exact_locators": 0},
        "claim_ceiling": source_result["claim_ceiling"],
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Biblissima Latin 4922 f1v canvas locator — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator independently rebuilds both 199-entry repository orbits, "
        "confirms every label is `NP`, confirms zero ranges and legends, and reconstructs the no-offset result and report.\n\n"
        "A qualified human must navigate the official witness to physical f.1v. No visual topology, Voynich label, word, "
        "sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
