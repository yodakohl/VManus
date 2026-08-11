#!/usr/bin/env python3
"""Text-only worth check for BnF Latin 18499 f26r and f67v2."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "BNF_LAT18499_F67V2_WIND_ROSE_METADATA_WORTH_CHECK_SPEC.md"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q09.html"
URL = "https://mandragore.bnf.fr/ark:/12148/cgfbt74042j"
OUT_JSON = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
OUT_REPORT = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth_report.md"

INSCRIPTION = (
    "oriens - meridies - occidens - septentrio / subsolanus calidus siccus - eurus - nothus - "
    "auster calidus humidus - affricus - zephirus // favonius frigidus humidus - cirtius - chorus - "
    "boreas frigius siccus - aquilo - vulturnus"
)
GROUPS = (
    ("oriens", ("subsolanus", "eurus", "nothus"), "calidus siccus"),
    ("meridies", ("auster", "affricus", "zephirus"), "calidus humidus"),
    ("occidens", ("favonius", "cirtius", "chorus"), "frigidus humidus"),
    ("septentrio", ("boreas", "aquilo", "vulturnus"), "frigius siccus"),
)
BNF_PHRASES = (
    "Latin 18499",
    "Italie - XIIIe siècle",
    "f. 26r",
    "Rose des vents",
    "Maurus Salernitanus, Glosulae isagoges johannitii",
    INSCRIPTION,
)
F67_PHRASES = (
    "4 smaller circles in the four (NE, SE, SW and NW) corners",
    "contain between three and four human faces, joined by lines",
    "This page has 22 text items (loci)",
    "8 lines of text in 'floating' paragraphs",
    "8 items of writing along radii (4 inwards, 4 outwards)",
    "6 'astronomical' labels",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch() -> str:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-BnF-Lat18499-worth-check/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected BnF response")
        raw = response.read()
    return re.sub(r"\s+", " ", html.unescape(raw.decode("utf-8"))).strip()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite BnF worth-check outputs")
    source = fetch()
    bnf_checks = {phrase: phrase in source for phrase in BNF_PHRASES}
    if not all(bnf_checks.values()):
        raise ValueError("BnF evidence projection drift")
    catalogue = re.sub(r"\s+", " ", html.unescape(CATALOGUE.read_text(encoding="utf-8"))).strip()
    f67_checks = {phrase: phrase in catalogue for phrase in F67_PHRASES}
    if not all(f67_checks.values()):
        raise ValueError("f67v2 description drift")
    group_rows = [
        {"group_order": index, "direction": direction, "wind_names": list(names), "catalogue_quality_spelling": quality}
        for index, (direction, names, quality) in enumerate(GROUPS, 1)
    ]
    if len({name for _, names, _ in GROUPS for name in names}) != 12:
        raise ValueError("wind-name projection mismatch")
    gates = {
        "readable_four_direction_headings": True,
        "readable_twelve_wind_names": True,
        "readable_four_quality_pairs": True,
        "sequence_projects_to_four_groups_of_three": True,
        "f67v2_has_four_corner_face_groups": True,
        "f67v2_each_group_has_exactly_three_faces": False,
        "f67v2_has_owned_twelve_slot_text_register": False,
        "common_start_direction_and_slot_correspondence": False,
    }
    projection = ("\n".join(BNF_PHRASES) + "\n").encode("utf-8")
    result = {
        "experiment": "BNF_LAT18499_F67V2_WIND_ROSE_METADATA_WORTH_CHECK",
        "status": "PASS_NEW_COMPLETE_READABLE_4X3_WIND_ROSE_COMPARATOR",
        "decision": "STOP_BEFORE_IMAGE_OR_ROSTER_REVIEW_NO_F67V2_TWELVE_SLOT_TEXT_REGISTER",
        "source": {
            "url": URL,
            "manuscript": "Latin 18499",
            "folio": "f. 26r",
            "date_place": "Italie - XIIIe siècle",
            "subject": "Rose des vents",
            "text": "Maurus Salernitanus, Glosulae isagoges johannitii",
            "evidence_projection_sha256": sha(projection),
        },
        "bnf_phrase_checks": bnf_checks,
        "f67v2_phrase_checks": f67_checks,
        "projected_groups": group_rows,
        "counts": {"direction_headings": 4, "wind_names": 12, "quality_pairs": 4, "f67v2_text_loci": 22, "f67v2_radial_loci": 8, "f67v2_label_loci": 6},
        "gates": gates,
        "source_access": {
            "official_html_opened": True,
            "manuscript_images_or_thumbnails_opened": False,
            "papers_pdfs_or_rosters_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_opened": False,
        },
        "inputs": {str(SPEC.relative_to(BASE)): sha(SPEC.read_bytes()), str(CATALOGUE.relative_to(BASE)): sha(CATALOGUE.read_bytes())},
        "claim_ceiling": "BnF Latin 18499 f26r strengthens the readable 4x3 wind-directional source-family prior, but f67v2 exposes no owned twelve-slot text register or common slot coordinate; no direction, wind, quality, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# BnF Latin 18499 f26r / f67v2 wind-rose metadata worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_OR_ROSTER_REVIEW_NO_F67V2_TWELVE_SLOT_TEXT_REGISTER**.\n\n"
        "The official Mandragore record supplies a genuinely useful new source comparandum. Its published inscription "
        "contains four cardinal headings, twelve distinct wind names in a repeating four-by-three sequence, and four "
        "hot/cold/dry/moist pairs. The literal catalogue spelling `frigius siccus` is preserved rather than corrected.\n\n"
        "This strengthens the provisional wind/directional-cosmography family for f67v2, whose four corner circles contain "
        "three or four connected faces. It does not supply a label transfer: f67v2 has 22 text loci—eight floating, eight "
        "radial, and six labels—not an owned twelve-slot register, and the BnF metadata supplies no common start, direction, "
        "or cross-manuscript slot correspondence.\n\n"
        "No image, thumbnail, canvas, paper, PDF, OCR, automated visual output, decoder claim, or spelling roster entered "
        "this result. The BnF source remains a strong readable 4×3 wind comparandum only and supplies no f67v2 direction, "
        "wind, quality, label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
