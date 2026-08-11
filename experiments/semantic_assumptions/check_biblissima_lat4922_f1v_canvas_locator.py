#!/usr/bin/env python3
"""Metadata-only attempt to locate Latin 4922 f1v in Gallica."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "BIBLISSIMA_LAT4922_F1V_CANVAS_LOCATOR_SPEC.md"
WORTH = RESULTS / "biblissima_f57_fourfold_metadata_worth.json"
MANIFEST_URL = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/manifest.json"
PAGINATION_URL = "https://gallica.bnf.fr/services/Pagination?ark=btv1b9066969x"
WITNESS_URL = "https://gallica.bnf.fr/ark:/12148/btv1b9066969x"
OUT = RESULTS / "biblissima_lat4922_f1v_canvas_locator.json"
OUT_MD = RESULTS / "biblissima_lat4922_f1v_canvas_locator_report.md"
WORTH_SHA = "3d581c40330763ddef573e115e7cd3f5d8090c2516141cb8dd65cf01d6a48126"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Lat4922-human-review-locator/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location"):
            raise ValueError(f"unexpected response: {url}")
        return response.read()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing to overwrite Latin 4922 locator outputs")
    if sha(WORTH.read_bytes()) != WORTH_SHA:
        raise ValueError("worth-result binding drift")
    manifest = json.loads(fetch(MANIFEST_URL).decode("utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    sequences = manifest.get("sequences", [])
    if not isinstance(sequences, list) or len(sequences) != 1:
        raise ValueError("manifest sequence drift")
    canvases = sequences[0].get("canvases", [])
    expected_ids = [f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/canvas/f{index}" for index in range(1, 200)]
    canvas_ids = [canvas.get("@id") for canvas in canvases]
    canvas_labels = [canvas.get("label") for canvas in canvases]
    if canvas_ids != expected_ids or canvas_labels != ["NP"] * 199 or manifest.get("structures", []) != []:
        raise ValueError("manifest canvas-orbit drift")
    root = ET.fromstring(fetch(PAGINATION_URL))
    pages = root.findall(".//page")
    numbers = [page.findtext("numero") for page in pages]
    orders = [page.findtext("ordre") for page in pages]
    types = [page.findtext("pagination_type") for page in pages]
    legends = [page.findtext("legend") for page in pages]
    if numbers != ["NP"] * 199 or orders != [str(index) for index in range(1, 200)] or types != ["N"] * 199 or any(legend not in (None, "") for legend in legends):
        raise ValueError("pagination orbit drift")
    result = {
        "experiment": "BIBLISSIMA_LAT4922_F1V_CANVAS_LOCATOR",
        "status": "STOP_NO_REPOSITORY_LOGICAL_FOLIATION",
        "decision": "QUALIFIED_HUMAN_MUST_NAVIGATE_TO_PHYSICAL_F1V_NO_SCAN_OFFSET_GUESS",
        "source": {"manifest_url": MANIFEST_URL, "pagination_url": PAGINATION_URL, "official_witness_url": WITNESS_URL},
        "manifest": {"id": manifest.get("@id"), "label": manifest.get("label"), "canvas_count": len(canvases), "unique_canvas_label": "NP", "logical_structure_count": len(manifest.get("structures", [])), "sequential_canvas_ids_f1_through_f199": True},
        "pagination": {"page_count": len(pages), "unique_numero": "NP", "orders_are_1_through_199": True, "unique_pagination_type": "N", "legend_count": sum(legend not in (None, "") for legend in legends)},
        "gates": {"physical_f1v_named_by_biblissima_and_mandragore": True, "repository_canvas_label_or_range_maps_f1v": False, "exact_page_specific_canvas_locator_available": False, "manual_navigation_required": True, "scan_offset_inferred": False},
        "source_access": {"iiif_manifest_metadata_opened": True, "pagination_xml_opened": True, "canvas_thumbnail_image_info_ocr_pdf_or_pixels_opened": False, "automated_visual_output_used": False},
        "inputs": {SPEC.name: sha(SPEC.read_bytes()), str(WORTH.relative_to(BASE)): WORTH_SHA},
        "claim_ceiling": "Gallica supplies a complete 199-canvas witness but no repository-authored logical mapping from physical f.1v to a canvas; a qualified human must navigate the official viewer and no scan offset, visual topology, Voynich label, word, sound, language, cipher, plaintext, meaning, or translation may be inferred.",
    }
    OUT.write_bytes(canonical(result))
    OUT_MD.write_text(
        "# Biblissima Latin 4922 f1v canvas locator\n\n"
        "Decision: **QUALIFIED_HUMAN_MUST_NAVIGATE_TO_PHYSICAL_F1V_NO_SCAN_OFFSET_GUESS**.\n\n"
        "The official Gallica IIIF manifest contains 199 sequential canvases, all labelled `NP`, and no logical ranges. "
        "The independent Gallica Pagination service likewise contains 199 sequential entries, all numbered `NP`, all "
        "type `N`, with no legends. These services therefore do not map physical f.1v to one scan.\n\n"
        "The official whole-manuscript witness remains the correct human-review entry point. A qualified reviewer must "
        "navigate to physical f.1v in the viewer; covers and flyleaves make a guessed numeric offset inadmissible. No "
        "canvas image, thumbnail, image-service metadata, OCR, PDF, or manuscript pixels entered this locator.\n\n"
        "This operational stop supplies no visual topology, Voynich label, word, sound, language, cipher, plaintext, "
        "meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
