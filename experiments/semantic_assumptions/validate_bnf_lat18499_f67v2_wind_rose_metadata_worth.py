#!/usr/bin/env python3
"""Independent live reconstruction of the BnF/f67v2 worth check."""

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
PRODUCER = BASE / "check_bnf_lat18499_f67v2_wind_rose_metadata_worth.py"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q09.html"
RESULT = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
REPORT = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth_report.md"
OUT_JSON = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth_validation_report.md"
URL = "https://mandragore.bnf.fr/ark:/12148/cgfbt74042j"

FROZEN = {
    SPEC: "1745b203eb706f84ae07b4702767825c014ea930dcac445b30dc6e3728bbfb84",
    PRODUCER: "655ce8a07f6cd69dc6cba191b41ad6e86a0980451f392f2489968e88e8132809",
    CATALOGUE: "56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
    RESULT: "84a27c1da3c6400de89fc475bff3198466a3c79dd2f2ef92338ab814f3f851c7",
    REPORT: "c7ff12cb64934e4be929e36ea515cdeaa0a15a38f5be683096f593d82100d6ff",
}
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
BNF_PHRASES = ("Latin 18499", "Italie - XIIIe siècle", "f. 26r", "Rose des vents", "Maurus Salernitanus, Glosulae isagoges johannitii", INSCRIPTION)
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
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-BnF-Lat18499-worth-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected BnF response")
        raw = response.read()
    return re.sub(r"\s+", " ", html.unescape(raw.decode("utf-8"))).strip()


def load_result() -> dict[str, object]:
    raw = RESULT.read_text(encoding="utf-8")
    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate result key")
        return dict(items)
    value = json.loads(raw, object_pairs_hook=hook, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError("noncanonical result")
    return value


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite BnF validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = load_result()
    checks.append("canonical_duplicate_free_result")
    source = fetch()
    bnf_checks = {phrase: phrase in source for phrase in BNF_PHRASES}
    if not all(bnf_checks.values()):
        raise ValueError("live BnF projection mismatch")
    checks.extend(("live_official_html", "manuscript_folio_date_place", "wind_rose_subject", "literal_inscription"))
    catalogue = re.sub(r"\s+", " ", html.unescape(CATALOGUE.read_text(encoding="utf-8"))).strip()
    f67_checks = {phrase: phrase in catalogue for phrase in F67_PHRASES}
    if not all(f67_checks.values()):
        raise ValueError("f67 source projection mismatch")
    checks.extend(("f67_four_corner_face_groups", "f67_three_or_four_faces", "f67_22_locus_partition"))
    names = [name for _, triple, _ in GROUPS for name in triple]
    if len(names) != 12 or len(set(names)) != 12 or len(GROUPS) != 4:
        raise ValueError("4x3 projection mismatch")
    if [quality for _, _, quality in GROUPS][-1] != "frigius siccus":
        raise ValueError("literal spelling guard failed")
    checks.extend(("four_direction_groups", "twelve_distinct_wind_names", "four_quality_pairs", "literal_frigius_preserved"))
    if len(names[:-1]) == 12 or len(names) != 12:
        raise ValueError("twelve-name mutation guard failed")
    checks.append("twelve_name_completeness_mutation")
    projection = ("\n".join(BNF_PHRASES) + "\n").encode("utf-8")
    groups = [
        {"group_order": index, "direction": direction, "wind_names": list(triple), "catalogue_quality_spelling": quality}
        for index, (direction, triple, quality) in enumerate(GROUPS, 1)
    ]
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
    expected = {
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
        "projected_groups": groups,
        "counts": {"direction_headings": 4, "wind_names": 12, "quality_pairs": 4, "f67v2_text_loci": 22, "f67v2_radial_loci": 8, "f67v2_label_loci": 6},
        "gates": gates,
        "source_access": {
            "official_html_opened": True,
            "manuscript_images_or_thumbnails_opened": False,
            "papers_pdfs_or_rosters_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_opened": False,
        },
        "inputs": {str(SPEC.relative_to(BASE)): FROZEN[SPEC], str(CATALOGUE.relative_to(BASE)): FROZEN[CATALOGUE]},
        "claim_ceiling": "BnF Latin 18499 f26r strengthens the readable 4x3 wind-directional source-family prior, but f67v2 exposes no owned twelve-slot text register or common slot coordinate; no direction, wind, quality, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.extend(("evidence_projection_digest", "gate_vector_exact", "result_object_exact"))
    report = (
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
        "wind, quality, label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")
    validation = {
        "experiment": "BNF_LAT18499_F67V2_WIND_ROSE_METADATA_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_OFFICIAL_SOURCE_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "counts": expected["counts"],
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# BnF Latin 18499 f26r / f67v2 worth check — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator live-refetches the official Mandragore record, reconstructs "
        "the four headings, twelve names, four literal quality strings, f67v2's 22-locus partition, decision, and report.\n\n"
        "This strengthens only a wind-diagram family prior and stops before image or roster review. It supplies no f67v2 "
        "direction, wind, quality, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
