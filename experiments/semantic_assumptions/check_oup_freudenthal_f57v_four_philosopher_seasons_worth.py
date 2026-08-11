#!/usr/bin/env python3
"""Text-only worth check for the Oxford four-philosopher diagram and f57v."""

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
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q08.html"
URL = "https://oup.silverchair-cdn.com/book-minimal/26277/chapter-minimal/194504296"
OUT_JSON = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth.json"
OUT_REPORT = RESULTS / "oup_freudenthal_f57v_four_philosopher_seasons_worth_report.md"

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


def visible_text(raw: bytes) -> str:
    parser = _VisibleText()
    parser.feed(raw.decode("utf-8"))
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()


def fetch() -> tuple[bytes, str]:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-OUP-f57-worth-check/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected Oxford response")
        raw = response.read()
    if len(raw) < 8_000:
        raise ValueError("incomplete Oxford minimal page")
    return raw, visible_text(raw)


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Oxford/f57 worth-check outputs")
    raw, source = fetch()
    source_checks = {phrase: phrase in source for phrase in SOURCE_PHRASES}
    if not all(source_checks.values()):
        raise ValueError("Oxford evidence projection drift")
    extract = source.split(" Extract ", 1)[1].split(" Subject Metaphysics", 1)[0]
    absent_fields = {
        "shelfmark": "shelfmark" not in extract.lower(),
        "folio": "folio" not in extract.lower(),
        "named_library": "library" not in extract.lower(),
        "portrait_names": not any(name in extract for name in ("Plato", "Aristotle", "Virgil", "Ovid")),
    }
    if not all(absent_fields.values()):
        raise ValueError("Oxford extract now supplies a previously absent identification field")
    catalogue = re.sub(r"\s+", " ", html.unescape(CATALOGUE.read_text(encoding="utf-8"))).strip()
    f57_checks = {phrase: phrase in catalogue for phrase in F57_PHRASES}
    if not all(f57_checks.values()):
        raise ValueError("f57v catalogue projection drift")
    gates = {
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
    }
    projection = ("\n".join(SOURCE_PHRASES) + "\n").encode("utf-8")
    result = {
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
        "counts": {
            "described_human_portraits": 4,
            "described_seasons": 4,
            "described_elements": 4,
            "f57v_circular_bands": 4,
            "f57v_central_persons": 4,
            "f57v_radial_texts": 4,
            "f57v_person_near_labels": 4,
            "f57v_repeated_periods": 4,
            "f57v_items_per_repeated_period": 17,
        },
        "gates": gates,
        "source_access": {
            "official_scholarly_extract_opened": True,
            "related_human_bibliographic_search_performed": True,
            "manuscript_or_cover_images_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_or_translation_papers_validated": False,
        },
        "inputs": {
            str(SPEC.relative_to(BASE)): sha(SPEC.read_bytes()),
            str(CATALOGUE.relative_to(BASE)): sha(CATALOGUE.read_bytes()),
        },
        "claim_ceiling": "The Oxford extract strengthens only a four-person season-element-quality diagram-family prior. Without a shelfmark, explicit owner table, shared start, orientation, and register correspondence, it assigns no philosopher, season, element, quality, direction, label, word, sound, language, cipher, plaintext, meaning, or translation to f57v.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
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
        "philosopher, season, element, quality, direction, label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
