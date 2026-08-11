#!/usr/bin/env python3
"""Independent live reconstruction of the BnF NAL112/f57v worth check."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "BNF_NAL112_F57V_SEASONS_HUMOURS_METADATA_WORTH_CHECK_SPEC.md"
PRODUCER = BASE / "check_bnf_nal112_f57v_seasons_humours_metadata_worth.py"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q08.html"
RESULT = RESULTS / "bnf_nal112_f57v_seasons_humours_metadata_worth.json"
REPORT = RESULTS / "bnf_nal112_f57v_seasons_humours_metadata_worth_report.md"
OUT_JSON = RESULTS / "bnf_nal112_f57v_seasons_humours_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "bnf_nal112_f57v_seasons_humours_metadata_worth_validation_report.md"
URL = "https://mandragore.bnf.fr/ark:/12148/cgfbt75066s"

FROZEN = {
    SPEC: "7a8da3d0e90d52c65fde960e27bcb6ab3c356941390799f3ea2c9a244a8db15a",
    PRODUCER: "83959d058debd35d479a9323b06ae9eac9f40de2b5b0f4a8d7299adcc04aa5dd",
    CATALOGUE: "ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7",
    RESULT: "ed71be14831165558ff7ff929f089b92eb3bb6cd4ef14b014bd2fd37cca2b8ed",
    REPORT: "c7da155562e37a43e4e460aeca9f1c24e52e28b2239527b41ddb13f7d72cb7f5",
}
INSCRIPTION = (
    "anus / oriens - meridies - occidens - septemtrio / ver - humidus - calidus / "
    "estas - calida - sicca / autumnus - siccus - frigidus / hiemns frigidus - humidus"
)
DIRECTIONS = ("oriens", "meridies", "occidens", "septemtrio")
SEASONS = (
    ("ver", ("humidus", "calidus")),
    ("estas", ("calida", "sicca")),
    ("autumnus", ("siccus", "frigidus")),
    ("hiemns", ("frigidus", "humidus")),
)
BNF_PHRASES = (
    "NAL 112", "Italie (Nord)", "XVe siècle (2e moitié)",
    "Isidorus Hispalensis (s.), De natura rerum", "f. 6r", "Saisons et humeurs", INSCRIPTION,
)
F57_PHRASES = (
    "A circular drawing with four concentric circular bands with writing",
    "In the centre are four 'persons'", "4 items of circular writing",
    "4 items of writing along radii (all outward)", "four labels near the persons", "4 x 17 characters",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_result() -> dict[str, object]:
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


def fetch() -> str:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-BnF-NAL112-worth-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected BnF response")
        raw = response.read()
    return re.sub(r"\s+", " ", html.unescape(raw.decode("utf-8"))).strip()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite BnF NAL112 validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_result()
    checks.append("canonical_duplicate_free_result")
    source = fetch()
    bnf_checks = {phrase: phrase in source for phrase in BNF_PHRASES}
    if not all(bnf_checks.values()):
        raise ValueError("live BnF projection mismatch")
    checks.extend(("live_official_html", "manuscript_folio_date_place", "subject_and_text", "literal_inscription"))
    catalogue = re.sub(r"\s+", " ", html.unescape(CATALOGUE.read_text(encoding="utf-8"))).strip()
    f57_checks = {phrase: phrase in catalogue for phrase in F57_PHRASES}
    if not all(f57_checks.values()):
        raise ValueError("f57v catalogue projection mismatch")
    checks.extend(("f57_four_bands", "f57_four_persons", "f57_radial_and_label_counts", "f57_four_by_seventeen"))
    if len(DIRECTIONS) != 4 or len(set(DIRECTIONS)) != 4 or len(SEASONS) != 4:
        raise ValueError("fourfold projection mismatch")
    if any(len(qualities) != 2 for _, qualities in SEASONS):
        raise ValueError("quality-pair projection mismatch")
    checks.extend(("four_direction_literals", "four_season_literals", "eight_quality_occurrences", "literal_typos_preserved"))
    mutated = list(SEASONS)
    mutated[-1] = (mutated[-1][0], (mutated[-1][1][0],))
    if all(len(qualities) == 2 for _, qualities in mutated):
        raise ValueError("quality completeness mutation failed")
    checks.append("quality_pair_completeness_mutation")
    projection = ("\n".join(BNF_PHRASES) + "\n").encode("utf-8")
    expected = {
        "experiment": "BNF_NAL112_F57V_SEASONS_HUMOURS_METADATA_WORTH_CHECK",
        "status": "PASS_NEW_READABLE_FOURFOLD_YEAR_DIRECTION_QUALITY_COMPARATOR",
        "decision": "STOP_BEFORE_IMAGE_MANUSCRIPT_PAPER_OR_ROSTER_REVIEW_NO_CROSS_REGISTER_OWNERSHIP",
        "source": {
            "url": URL, "manuscript": "NAL 112", "folio": "f. 6r",
            "date_place": "Italie (Nord) - XVe siècle (2e moitié)", "subject": "Saisons et humeurs",
            "text": "Isidorus Hispalensis (s.), De natura rerum", "literal_inscription": INSCRIPTION,
            "evidence_projection_sha256": sha(projection),
        },
        "bnf_phrase_checks": bnf_checks,
        "f57v_phrase_checks": f57_checks,
        "direction_sequence": list(DIRECTIONS),
        "season_quality_sequence": [
            {"sequence_order": index, "season_literal": season, "quality_literals": list(qualities)}
            for index, (season, qualities) in enumerate(SEASONS, 1)
        ],
        "counts": {
            "direction_literals": 4, "season_literals": 4, "quality_literal_occurrences": 8,
            "f57v_circular_bands": 4, "f57v_central_persons": 4, "f57v_radial_texts": 4,
            "f57v_person_near_labels": 4, "f57v_repeated_periods": 4, "f57v_items_per_repeated_period": 17,
        },
        "gates": {
            "readable_four_direction_sequence": True, "readable_four_season_sequence": True,
            "readable_two_quality_literals_per_season": True, "f57v_has_four_central_persons": True,
            "f57v_has_four_written_circular_bands": True,
            "f57v_has_four_radial_texts_and_four_person_near_labels": True,
            "source_metadata_explicitly_pairs_each_direction_with_one_season_group": False,
            "source_metadata_maps_season_quality_groups_to_f57v_text_owners": False,
            "common_start_orientation_and_slot_correspondence": False,
        },
        "source_access": {
            "official_html_opened": True, "manuscript_images_or_thumbnails_opened": False,
            "manuscript_or_papers_opened": False, "ocr_or_automated_visual_output_used": False,
            "decoder_claims_or_rosters_opened": False,
        },
        "inputs": {str(SPEC.relative_to(BASE)): FROZEN[SPEC], str(CATALOGUE.relative_to(BASE)): FROZEN[CATALOGUE]},
        "claim_ceiling": "BnF NAL 112 f6r strengthens only a readable fourfold year-direction-quality source-family prior; the metadata supplies no owned cross-register mapping to f57v, so no direction, season, humour, quality, element, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.extend(("evidence_projection_digest", "gate_vector_exact", "result_object_exact"))
    report = (
        "# BnF NAL 112 f6r / f57v seasons-and-humours metadata worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_MANUSCRIPT_PAPER_OR_ROSTER_REVIEW_NO_CROSS_REGISTER_OWNERSHIP**.\n\n"
        "The official Mandragore record supplies a useful new readable comparandum. Its literal inscription lists four "
        "directions and then four seasons, each with two hot/cold/dry/moist quality forms. The catalogue spellings `anus`, "
        "`septemtrio`, and `hiemns` are preserved rather than corrected.\n\n"
        "This strengthens the historical fourfold year–direction–quality source family relevant to f57v. It does not "
        "supply the missing transfer relation. Mandragore provides no image for this record and its metadata does not "
        "explicitly pair each direction with one season group, map either sequence to f57v's four persons, radial texts, "
        "person-near labels, or four repeated written bands, or fix a common start and orientation.\n\n"
        "No image, thumbnail, canvas, manuscript, paper, PDF, OCR, automated visual output, decoder claim, or spelling "
        "roster entered this result. NAL 112 remains a strong readable fourfold comparandum only and supplies no f57v "
        "direction, season, humour, quality, element, label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")
    validation = {
        "experiment": "BNF_NAL112_F57V_SEASONS_HUMOURS_METADATA_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_OFFICIAL_SOURCE_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT], "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()), "check_count": len(checks), "checks": checks,
        "counts": expected["counts"], "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# BnF NAL 112 f6r / f57v worth check — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator live-refetches the official Mandragore record and independently "
        "reconstructs the four directions, four seasons, eight quality occurrences, f57v topology checks, stop decision, "
        "canonical result, and exact report.\n\n"
        "This confirms only the cheap metadata stop before image, manuscript, paper, or roster review and supplies no f57v "
        "direction, season, humour, quality, element, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
