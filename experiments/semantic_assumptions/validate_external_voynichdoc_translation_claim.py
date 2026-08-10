#!/usr/bin/env python3
"""Independent live-source validator for the Voynichdoc claim audit.

The producer is neither imported nor executed.  Five public pages are fetched
anew and parsed from rendered HTML text nodes.  This validator establishes
only what those pages publish or omit; it cannot test an unpublished method.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import ssl
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
AUDIT_JSON = RESULTS / "external_voynichdoc_translation_claim_audit.json"
AUDIT_REPORT = RESULTS / "external_voynichdoc_translation_claim_audit.md"
OUTPUT_JSON = RESULTS / "external_voynichdoc_translation_claim_audit_validation.json"
OUTPUT_REPORT = RESULTS / "external_voynichdoc_translation_claim_audit_validation.md"

EXPECTED_AUDIT_JSON_SHA = "75ad25c953d24ddc965ccfa7ed4d963631892e2983be795ea89e449f841dcbce"
EXPECTED_AUDIT_REPORT_SHA = "ad64797865ffb55f121f43180496c651d212615c18c0dfb569b40eb3eeac682a"

SOURCES = {
    "author": {
        "url": "https://www.voynichdoc.com/autor",
        "bytes": 349705,
        "sha256": "bff8b374b3d84a9be7a370dfc0274d584ba8484b437fc8cf9876b4bdf3dee607",
    },
    "f10r": {
        "url": "https://www.voynichdoc.com/seccion-botanica/orquidea-macho-orchis-mascula-f10r/78",
        "bytes": 364795,
        "sha256": "245ab6e5934f27fe178f959fdc1b2579e308de91e43062b8828f815329ba3057",
    },
    "f70r_outer": {
        "url": "https://www.voynichdoc.com/seccion-astronomica-astrologica/zodiaco-piscis-f70r-circulo-imagenext/61",
        "bytes": 368780,
        "sha256": "f27b0e49a3cdb174d9eae333c7510f96e96a069640284a91039313000659947d",
    },
    "home": {
        "url": "https://www.voynichdoc.com/home",
        "bytes": 360469,
        "sha256": "7f9008084c10bc30dd64dfe2342676d7eefac7f144e722f5b68545323dda7a6d",
    },
    "timeline": {
        "url": "https://www.voynichdoc.com/timeline",
        "bytes": 407408,
        "sha256": "641c40f0c25740d2ea6b371c752908ed34d83efff2bbbc6b5ac5ae5d4c76f665",
    },
}

CLAIM_CEILING = (
    "This holds the currently published modernized narratives outside the active "
    "evidence base until a source-aligned method is published. It does not prove "
    "the author's unpublished method or interpretations false."
)

F10_NARRATIVE_SHA = "d3b2c9dd6bb1e30f8f002959172f29857f1e18c3bd0058bc52ba9e29e382b9e6"
F70_NARRATIVE_SHA = "3f2b6185220b8867169add8af34315b0f0b4c44467237959abad0bd377c22030"
F10_VISIBLE_SHA = "5d431fe7122cc9709cc7358a4f8e8f3b3e2df3ed1bd8551c75430b09635f4ad8"
F70_VISIBLE_SHA = "5e91501cfc3b57efb306a4032a17128df030ae704b4360a223eb98e693925726"


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized(text: str) -> str:
    return " ".join(html.unescape(text).split())


def text_sha(text: str) -> str:
    return sha256_bytes((text + "\n").encode("utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


class VisibleHTML(HTMLParser):
    """Collect rendered text-bearing nodes, paragraphs, titles, and links."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}
    BREAK_TAGS = {"article", "br", "div", "h1", "h2", "h3", "h4", "li", "p"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.all_parts: list[str] = []
        self.paragraphs: list[str] = []
        self.titles: list[str] = []
        self.links: list[tuple[str, str, str]] = []
        self._paragraph: list[str] | None = None
        self._title: list[str] | None = None
        self.visible_tables = 0
        self.visible_pre = 0
        self.visible_code = 0

    def _append(self, value: str) -> None:
        self.all_parts.append(value)
        if self._paragraph is not None:
            self._paragraph.append(value)
        if self._title is not None:
            self._title.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        attr = {key: value or "" for key, value in attrs}
        if "href" in attr:
            self.links.append((tag, attr.get("rel", ""), attr["href"]))
        if tag == "p":
            require(self._paragraph is None, "nested paragraph in public HTML")
            self._paragraph = []
        if tag == "h1":
            require(self._title is None, "nested h1 in public HTML")
            self._title = []
        if tag == "table":
            self.visible_tables += 1
        elif tag == "pre":
            self.visible_pre += 1
        elif tag == "code":
            self.visible_code += 1
        if tag in self.BREAK_TAGS:
            self._append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS:
            if self.skip_depth:
                self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "p" and self._paragraph is not None:
            self.paragraphs.append(normalized("".join(self._paragraph)))
            self._paragraph = None
        if tag == "h1" and self._title is not None:
            self.titles.append(normalized("".join(self._title)))
            self._title = None
        if tag in self.BREAK_TAGS:
            self._append(" ")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self._append(data)

    @property
    def visible_text(self) -> str:
        return normalized("".join(self.all_parts))


def fetch(url: str) -> bytes:
    parsed = urlparse(url)
    require(parsed.scheme == "https" and parsed.hostname == "www.voynichdoc.com", "unexpected source host")
    request = Request(url, headers={"User-Agent": "VManus-independent-source-audit/1.0"})
    context = ssl.create_default_context()
    with urlopen(request, timeout=45, context=context) as response:
        require(response.status == 200, f"HTTP status {response.status} for {url}")
        require(response.geturl() == url, f"unexpected redirect for {url}")
        content_type = response.headers.get_content_type()
        require(content_type == "text/html", f"unexpected content type for {url}")
        return response.read()


def parse_page(raw: bytes) -> VisibleHTML:
    require(b"\x00" not in raw, "NUL in HTML source")
    page = VisibleHTML()
    page.feed(raw.decode("utf-8", errors="strict"))
    page.close()
    require(page.skip_depth == 0, "unclosed skipped HTML element")
    require(page.visible_text != "", "empty visible page")
    return page


def contains(text: str, phrase: str) -> bool:
    return phrase.casefold() in text.casefold()


def exact_phrase_once(text: str, phrase: str, label: str) -> None:
    require(text.casefold().count(phrase.casefold()) == 1, f"{label}: expected phrase not unique")


def machine_method_links(pages: dict[str, VisibleHTML]) -> tuple[list[str], int]:
    forbidden: list[str] = []
    pwa_manifest_count = 0
    file_re = re.compile(r"(?i)(?:\.(?:csv|tsv|json|py|ipynb|zip|tar|gz|7z)(?:[?#]|$))")
    for name, page in pages.items():
        for tag, rel, href in page.links:
            path = urlparse(href).path
            if tag == "link" and "manifest" in rel.casefold().split() and path == "/manifest.json":
                pwa_manifest_count += 1
                continue
            if file_re.search(href):
                forbidden.append(f"{name}:{href}")
    return forbidden, pwa_manifest_count


def assert_translation_page_absences(name: str, page: VisibleHTML) -> None:
    text = page.visible_text
    patterns = {
        "EVA token": r"(?i)(?<![A-Za-z])EVA(?![A-Za-z])",
        "source transcription": r"(?i)\b(?:transcription|transliteration)\b",
        "line/token alignment": r"(?i)\b(?:alignment|aligned|line-by-line|token-by-token)\b",
        "cryptographic key or mapping": r"(?i)\b(?:cryptographic keys?|key table|mapping table)\b",
        "machine method": r"(?i)\b(?:algorithm|decoder|methodology|source code|notebook)\b",
        "named-language claim": r"(?i)\blanguage\b",
    }
    for label, pattern in patterns.items():
        require(re.search(pattern, text) is None, f"{name}: visible {label} found")
    require(page.visible_tables == 0, f"{name}: visible table found")
    require(page.visible_pre == 0 and page.visible_code == 0, f"{name}: visible pre/code block found")


def build_expected_result(raw: dict[str, bytes], pages: dict[str, VisibleHTML]) -> tuple[dict[str, Any], dict[str, Any]]:
    home = pages["home"].visible_text
    timeline = pages["timeline"].visible_text
    author = pages["author"].visible_text
    f10 = pages["f10r"]
    f70 = pages["f70r_outer"]

    disclosure_phrases = {
        "not_literal_translation": "The translations should not be understood as literal translations.",
        "does_not_reflect_source_syntax_or_structure": "they do not purport to reflect the language, style, syntax, or structure of the original",
        "discourse_reorganized": "The modernization process involves reorganizing the discourse",
        "vocabulary_homogenized": "homogenizing the vocabulary",
        "faithful_interpretation_deferred": "A plausible interpretation, more faithful to the source text, will be made available for specialized analysis at a later stage.",
        "english_site_text_ai_translated": "translated into English using AI tools (ChatGPT, 2026)",
    }
    for label, phrase in disclosure_phrases.items():
        exact_phrase_once(home, phrase, label)
    methodology_phrase = "In the coming months, we will publish all the different paragraphs and finally the methodology used."
    exact_phrase_once(timeline, methodology_phrase, "methodology_deferred")

    exact_phrase_once(author, "identifying the cryptographic keys and the primary language in which it is written", "claimed_keys_primary_language")
    exact_phrase_once(author, "Six months later, he deciphered the second language.", "claimed_second_language")

    require(f10.titles == ["Early purple orchid (Orchis mascula)(f10r)"], "f10r title mismatch")
    require(f70.titles == ["Pisces (f70r) Images of the Outer Ring."], "f70r title mismatch")
    f10_narratives = [p for p in f10.paragraphs if "[Complete translate]" in p]
    f70_narratives = [p for p in f70.paragraphs if "[Complete translation]" in p]
    require(len(f10_narratives) == 1 and len(f70_narratives) == 1, "complete narrative marker mismatch")
    f10_narrative = f10_narratives[0]
    f70_narrative = f70_narratives[0]
    require(len(f10_narrative.split()) == 236 and text_sha(f10_narrative) == F10_NARRATIVE_SHA, "f10r complete narrative mismatch")
    require(len(f70_narrative.split()) == 397 and text_sha(f70_narrative) == F70_NARRATIVE_SHA, "f70r complete narrative mismatch")
    require(text_sha(f10.visible_text) == F10_VISIBLE_SHA, "f10r visible-page digest mismatch")
    require(text_sha(f70.visible_text) == F70_VISIBLE_SHA, "f70r visible-page digest mismatch")
    exact_phrase_once(home, "26/07/2026", "f10r publication date")
    exact_phrase_once(home, "The complete translation of Early purple orchid (Orchis mascula) from the Voynich Manuscript is published.", "f10r publication claim")

    date_phrases = [
        "the twentieth day of April",
        "the tenth of May",
        "the ninth of June",
        "the third of November",
        "the seventh of September",
    ]
    for phrase in date_phrases:
        exact_phrase_once(f70_narrative, phrase, f"f70r date {phrase}")
    day_month_mentions = re.findall(
        r"(?i)\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
        r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|"
        r"eighteenth|nineteenth|twentieth)(?: day)? of (?:January|February|March|"
        r"April|May|June|July|August|September|October|November|December)\b",
        f70_narrative,
    )
    require(len(day_month_mentions) == 5, "f70r contains an unexpected day-month count")

    assert_translation_page_absences("f10r", f10)
    assert_translation_page_absences("f70r_outer", f70)
    forbidden_links, pwa_count = machine_method_links(pages)
    require(forbidden_links == [], "machine-readable method-like link found")
    require(pwa_count == 5, "root PWA manifest link is not present exactly once on each page")

    source_rows = {
        name: {"bytes": len(raw[name]), "sha256": sha256_bytes(raw[name]), "url": SOURCES[name]["url"]}
        for name in sorted(SOURCES)
    }
    result = {
        "admission_gates": {
            "claimed_languages_named_on_examined_translation_pages": False,
            "cryptographic_keys_or_mapping_published": False,
            "held_page_prediction_or_falsifier_published": False,
            "independent_reproduction_available": False,
            "literal_source_faithful_translation_available": False,
            "source_transliteration_to_plaintext_alignment_available": False,
        },
        "claim_ceiling": CLAIM_CEILING,
        "claim_checks": {
            "claims_two_languages_and_keys": True,
            "f10r_complete_translation_present": True,
            "f70r_complete_translation_present": True,
            "f70r_contains_precise_dates": True,
        },
        "decision": "DO_NOT_IMPORT_PLAINTEXT_PLANT_NAMES_DATES_OR_LANGUAGE_CLAIMS",
        "disclosed_limits": {
            "discourse_reorganized": True,
            "does_not_reflect_source_syntax_or_structure": True,
            "english_site_text_ai_translated": True,
            "faithful_interpretation_deferred": True,
            "methodology_deferred": True,
            "not_literal_translation": True,
            "vocabulary_homogenized": True,
        },
        "experiment": "EXTERNAL_VOYNICHDOC_TRANSLATION_CLAIM_AUDIT",
        "reproduction_checks": {
            "eva_source_shown": False,
            "key_or_mapping_table_shown": False,
            "line_or_token_alignment_shown": False,
            "machine_readable_method_linked": False,
            "named_primary_or_second_language_on_translation_pages": False,
            "source_transliteration_shown": False,
        },
        "sources": source_rows,
        "status": "HOLD_AS_TRANSLATION_EVIDENCE_METHOD_AND_ALIGNMENT_NOT_PUBLISHED",
    }
    detail = {
        "f10r": {
            "complete_narrative_sha256": F10_NARRATIVE_SHA,
            "complete_narrative_words": 236,
            "publication_date": "26/07/2026",
            "visible_text_sha256": F10_VISIBLE_SHA,
        },
        "f70r_outer": {
            "complete_narrative_sha256": F70_NARRATIVE_SHA,
            "complete_narrative_words": 397,
            "date_phrases": date_phrases,
            "visible_text_sha256": F70_VISIBLE_SHA,
        },
        "pwa_manifest_links_excluded_as_infrastructure": pwa_count,
    }
    return result, detail


def build_audit_report() -> bytes:
    text = (
        "# External Voynichdoc translation-claim audit\n\n"
        "Status: **HOLD_AS_TRANSLATION_EVIDENCE_METHOD_AND_ALIGNMENT_NOT_PUBLISHED**.\n\n"
        "The site publishes polished narratives for pages including f10r and f70r, and claims that cryptographic keys plus two languages have been identified. It does not currently name those languages on the examined translation pages, publish the keys, show an EVA/source transcription, align source groups to plaintext, provide a literal translation, expose a held-page falsifier, or provide machine-readable code/data.\n\n"
        "The site itself says the public text reorganizes discourse, homogenizes vocabulary, does not reflect source language/style/syntax/structure, and must not be understood as literal translation. It says a more faithful version and the methodology will appear later. The English website wording was produced with ChatGPT; the Spanish research is identified as official.\n\n"
        "Therefore none of the published plant names, remedies, political narrative, dates, language claims, or plaintext enters the active translation. Reopen only when the claimed method and source-aligned literal output are public and can predict held material. This hold does not prove the unpublished method false.\n"
    )
    return text.encode("utf-8")


def write_outputs(validation: dict[str, Any]) -> None:
    require(not OUTPUT_JSON.exists() and not OUTPUT_REPORT.exists(), "validation output already exists")
    report = (
        "# External Voynichdoc claim-audit validation\n\n"
        "Status: **PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION**.\n\n"
        "Five public pages were fetched again and matched the frozen byte hashes. Independent visible-HTML parsing reproduces every claim, disclosure, absence, admission gate, decision, and the canonical audit JSON/report. The root `/manifest.json` links are ordinary PWA manifest declarations, not translation methodology.\n\n"
        "The result remains a provenance and reproducibility hold. It does not establish that the author's unpublished method or interpretations are false.\n"
        "The negative publication checks are page-scoped to the five bound sources; they are not proof that no relevant artifact exists elsewhere.\n"
    ).encode("utf-8")
    json_bytes = canonical_json_bytes(validation)
    tmp_json = OUTPUT_JSON.with_name(OUTPUT_JSON.name + f".tmp.{os.getpid()}")
    tmp_report = OUTPUT_REPORT.with_name(OUTPUT_REPORT.name + f".tmp.{os.getpid()}")
    try:
        tmp_json.write_bytes(json_bytes)
        tmp_report.write_bytes(report)
        os.link(tmp_json, OUTPUT_JSON)
        os.link(tmp_report, OUTPUT_REPORT)
    finally:
        tmp_json.unlink(missing_ok=True)
        tmp_report.unlink(missing_ok=True)


def main() -> None:
    require(sha256_file(AUDIT_JSON) == EXPECTED_AUDIT_JSON_SHA, "audit JSON hash mismatch")
    require(sha256_file(AUDIT_REPORT) == EXPECTED_AUDIT_REPORT_SHA, "audit report hash mismatch")

    raw: dict[str, bytes] = {}
    pages: dict[str, VisibleHTML] = {}
    for name in sorted(SOURCES):
        body = fetch(SOURCES[name]["url"])
        require(len(body) == SOURCES[name]["bytes"], f"{name}: byte count changed")
        require(sha256_bytes(body) == SOURCES[name]["sha256"], f"{name}: live page hash changed")
        raw[name] = body
        pages[name] = parse_page(body)

    reconstructed, detail = build_expected_result(raw, pages)
    audit_bytes = AUDIT_JSON.read_bytes()
    published = json.loads(audit_bytes.decode("utf-8"))
    require(audit_bytes == canonical_json_bytes(published), "audit JSON is not canonical")
    require(canonical_json_bytes(reconstructed) == audit_bytes, "audit JSON differs from independent reconstruction")
    require(AUDIT_REPORT.read_bytes() == build_audit_report(), "audit report differs from independent reconstruction")
    require(reconstructed["claim_ceiling"] == CLAIM_CEILING, "claim ceiling was overstated")

    validator_sha = sha256_file(Path(__file__).resolve())
    validation = {
        "checks": {
            "admission_gates_exact": True,
            "canonical_audit_json_exact": True,
            "canonical_audit_report_exact": True,
            "claim_ceiling_no_false_method_rejection": True,
            "complete_f10r_narrative_bound": True,
            "complete_f70r_narrative_and_dates_bound": True,
            "disclosed_limits_exact": True,
            "five_live_page_hashes_exact": True,
            "generic_manifest_is_pwa_infrastructure": True,
            "translation_page_reproduction_absences_exact": True,
        },
        "decision": reconstructed["decision"],
        "experiment": "EXTERNAL_VOYNICHDOC_TRANSLATION_CLAIM_AUDIT_VALIDATION",
        "hashes": {
            "audit_json_sha256": EXPECTED_AUDIT_JSON_SHA,
            "audit_report_sha256": EXPECTED_AUDIT_REPORT_SHA,
            "validator_sha256": validator_sha,
        },
        "page_details": detail,
        "overstatement_guard": {
            "absence_claims_proven_on_five_examined_pages": True,
            "absence_claims_proven_site_wide": False,
            "unpublished_method_or_interpretations_proven_false": False,
        },
        "scope": {
            "examined_pages_only": True,
            "producer_imported_or_executed": False,
            "unpublished_method_claimed_false": False,
        },
        "sources": reconstructed["sources"],
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
    }
    write_outputs(validation)
    print(json.dumps({
        "status": validation["status"],
        "validator_sha256": validator_sha,
        "validation_json_sha256": sha256_file(OUTPUT_JSON),
        "validation_report_sha256": sha256_file(OUTPUT_REPORT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
