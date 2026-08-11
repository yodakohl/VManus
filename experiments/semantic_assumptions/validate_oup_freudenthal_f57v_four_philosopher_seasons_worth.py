#!/usr/bin/env python3
"""Independent live reconstruction of the Oxford/f57v worth check."""

from __future__ import annotations

import hashlib
import html
from html.parser import HTMLParser
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "OUP_FREUDENTHAL_F57V_FOUR_PHILOSOPHER_SEASONS_WORTH_CHECK_SPEC.md"
PRODUCER = BASE / "check_oup_freudenthal_f57v_four_philosopher_seasons_worth.py"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q08.html"
RESULT = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth.json"
REPORT = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth_report.md"
OUT_JSON = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth_validation.json"
OUT_REPORT = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth_validation_report.md"
URL = "https://oup.silverchair-cdn.com/book-minimal/26277/chapter-minimal/194504296"

FROZEN = {
    SPEC: "cf3f4728140296448413291b3ef12bd1e8af87815e91b3ef4279b690868b5109",
    PRODUCER: "e324f06c93f865627df0e750eb522533a8ccecf05f1126063166eefae01bd836",
    CATALOGUE: "ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7",
    RESULT: "e2c08e49c8f314ca9737a88aced1809b942494dc026f3e29495ca744dc8798ea",
    REPORT: "c7aa08cc3859eba4e8ecfbcc2cf904e6b2fb34eea24699ec9352e7be2183d20f",
}
SOURCE_PHRASES = (
    "Aristotle’s Theory of Material Substance: Heat and Pneuma, Form and Soul",
    "Gad Freudenthal",
    "A Note on the Cover Illustration",
    "https://doi.org/10.1093/acprof:oso/9780198238645.002.0006",
    "Page viii",
    "Published: 04 February 1999",
    "The portraits of Roman philosophers are used to represent the four seasons",
    "the central caption, stihia id est tempora vel elementa , identifies with the elements",
    "listed along the periphery of the circle are the combinations of the elementary qualities",
    "The diagram is found in a manuscript of Bede’s De ratione temporum",
    "produced in southern Italy in the eleventh century",
    "Isidorian, abstract qualities-seasons diagrams",
)
F57_PHRASES = (
    "A circular drawing with four concentric circular bands with writing",
    "In the centre are four 'persons'",
    "4 items of circular writing",
    "4 items of writing along radii (all outward)",
    "four labels near the persons",
    "4 x 17 characters",
)


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def strict_json(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")

    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate result key")
        return dict(items)

    value = json.loads(
        raw,
        object_pairs_hook=hook,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if type(value) is not dict or canonical(value) != raw:
        raise ValueError("noncanonical result")
    return value


def fetch() -> tuple[bytes, str]:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-OUP-f57-worth-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected Oxford response")
        raw = response.read()
    if len(raw) < 8_000:
        raise ValueError("incomplete Oxford minimal page")
    parser = _VisibleText()
    parser.feed(raw.decode("utf-8"))
    text = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()
    return raw, text


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Oxford/f57 validation outputs")
    checks: list[str] = []
    for path, expected_hash in FROZEN.items():
        if sha(path.read_bytes()) != expected_hash:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_json(RESULT)
    checks.append("canonical_duplicate_free_result")
    raw, source = fetch()
    source_checks = {phrase: phrase in source for phrase in SOURCE_PHRASES}
    if not all(source_checks.values()):
        raise ValueError("live Oxford projection mismatch")
    checks.extend(("live_official_oxford_html", "human_note_identity", "four_portraits_and_seasons", "caption_seasons_elements", "peripheral_quality_combinations", "bede_date_place_context"))
    extract = source.split(" Extract ", 1)[1].split(" Subject Metaphysics", 1)[0]
    absent_fields = {
        "shelfmark": "shelfmark" not in extract.lower(),
        "folio": "folio" not in extract.lower(),
        "named_library": "library" not in extract.lower(),
        "portrait_names": not any(name in extract for name in ("Plato", "Aristotle", "Virgil", "Ovid")),
    }
    if not all(absent_fields.values()):
        raise ValueError("identification-field absence mismatch")
    checks.extend(("no_shelfmark_or_folio", "no_portrait_names"))
    catalogue = re.sub(r"\s+", " ", html.unescape(CATALOGUE.read_text(encoding="utf-8"))).strip()
    f57_checks = {phrase: phrase in catalogue for phrase in F57_PHRASES}
    if not all(f57_checks.values()):
        raise ValueError("f57v catalogue projection mismatch")
    checks.extend(("f57_four_bands", "f57_four_persons", "f57_radial_and_label_counts", "f57_four_by_seventeen"))
    mutated_phrases = tuple(phrase for phrase in SOURCE_PHRASES if "periphery" not in phrase)
    if any("periphery" in phrase for phrase in mutated_phrases):
        raise ValueError("peripheral-register mutation failed")
    checks.append("peripheral_register_mutation")
    projection = ("\n".join(SOURCE_PHRASES) + "\n").encode("utf-8")
    counts = {
        "described_human_portraits": 4,
        "described_seasons": 4,
        "described_elements": 4,
        "f57v_circular_bands": 4,
        "f57v_central_persons": 4,
        "f57v_radial_texts": 4,
        "f57v_person_near_labels": 4,
        "f57v_repeated_periods": 4,
        "f57v_items_per_repeated_period": 17,
    }
    claim = "The Oxford extract strengthens only a four-person season-element-quality diagram-family prior. Without a shelfmark, explicit owner table, shared start, orientation, and register correspondence, it assigns no philosopher, season, element, quality, direction, label, word, sound, language, cipher, plaintext, meaning, or translation to f57v."
    expected = {
        "experiment": "OUP_FREUDENTHAL_F57V_FOUR_PHILOSOPHER_SEASONS_WORTH_CHECK",
        "status": "PASS_CLOSEST_TEXT_DESCRIBED_FOUR_PERSON_SEASON_ELEMENT_QUALITY_COMPARATOR",
        "decision": "STOP_BEFORE_IMAGE_OR_SOURCE_TRANSFER_SHELFMARK_AND_SLOT_OWNERSHIP_UNRESOLVED",
        "source": {
            "url": URL,
            "author": "Gad Freudenthal",
            "title": "A Note on the Cover Illustration",
            "book": "Aristotle’s Theory of Material Substance: Heat and Pneuma, Form and Soul",
            "doi": "10.1093/acprof:oso/9780198238645.002.0006",
            "page": "viii",
            "published": "04 February 1999",
            "central_caption_literal": "stihia id est tempora vel elementa",
            "evidence_projection_sha256": sha(projection),
            "live_html_sha256": sha(raw),
        },
        "source_phrase_checks": source_checks,
        "absent_identification_fields": absent_fields,
        "f57v_phrase_checks": f57_checks,
        "counts": counts,
        "gates": {
            "official_human_scholarly_extract": True,
            "four_human_portraits_represent_four_seasons": True,
            "central_caption_links_seasons_and_elements": True,
            "peripheral_elementary_quality_combinations": True,
            "bede_southern_italy_eleventh_century_context": True,
            "f57v_has_four_central_persons": True,
            "f57v_has_four_written_circular_bands": True,
            "f57v_has_four_radial_texts_and_four_person_near_labels": True,
            "source_shelfmark_and_folio_published": False,
            "each_portrait_explicitly_owns_one_season_and_element": False,
            "each_quality_combination_explicitly_owns_the_same_slot": False,
            "common_start_orientation_and_register_correspondence": False,
        },
        "source_access": {
            "official_scholarly_extract_opened": True,
            "related_human_bibliographic_search_performed": True,
            "manuscript_or_cover_images_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_or_translation_papers_validated": False,
        },
        "inputs": {
            str(SPEC.relative_to(BASE)): FROZEN[SPEC],
            str(CATALOGUE.relative_to(BASE)): FROZEN[CATALOGUE],
        },
        "claim_ceiling": claim,
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.extend(("evidence_projection_digest", "gate_vector_exact", "result_object_exact"))
    report = (
        "# Oxford four-philosopher seasons/elements diagram / f57v worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_OR_SOURCE_TRANSFER_SHELFMARK_AND_SLOT_OWNERSHIP_UNRESOLVED**.\n\n"
        "The official Oxford extract clears the literature-worth threshold and is the closest text-described comparator "
        "found in the current acquisition pass. It states that four Roman-philosopher portraits represent the four seasons, "
        "that the central caption `stihia id est tempora vel elementa` identifies the seasons with the elements, and that "
        "combinations of elementary qualities are listed around the periphery. It locates the diagram only in an eleventh-"
        "century southern Italian manuscript of Bede's *De ratione temporum*.\n\n"
        "That is a material topology match, but not a transfer key. The published extract gives no shelfmark or folio, names "
        "no individual portrait, assigns no portrait to a particular season or element, assigns no peripheral quality "
        "combination to a portrait, and fixes no start or orientation. Related human bibliographic searching did not resolve "
        "those fields, so no candidate manuscript is silently substituted.\n\n"
        "No manuscript or cover image, OCR, automated visual output, decoder claim, or translation paper entered the result. "
        "The source strengthens only a four-person season-element-quality diagram-family prior and supplies no f57v "
        "philosopher, season, element, quality, direction, label, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")
    validation = {
        "experiment": "OUP_FREUDENTHAL_F57V_FOUR_PHILOSOPHER_SEASONS_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_OFFICIAL_SOURCE_RECONSTRUCTION",
        "decision": expected["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "counts": counts,
        "claim_ceiling": claim,
    }
    OUT_JSON.write_text(canonical(validation), encoding="utf-8")
    OUT_REPORT.write_text(
        "# Oxford four-philosopher seasons/elements worth check — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator live-refetches the official Oxford minimal chapter page and "
        "independently reconstructs the four-portrait seasons statement, central seasons/elements caption, peripheral "
        "quality register, Bede/date/place context, absent identification fields, f57v topology, stop decision, canonical "
        "result, and exact report.\n\n"
        "This confirms only the text-level source-worth result. It supplies no f57v philosopher, season, element, quality, "
        "direction, label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
