#!/usr/bin/env python3
"""Audit the currently public voy nichdoc.com translation claim."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_JSON = RESULTS / "external_voynichdoc_translation_claim_audit.json"
OUT_REPORT = RESULTS / "external_voynichdoc_translation_claim_audit.md"

SOURCES = {
    "home": (
        "https://www.voynichdoc.com/home",
        "7f9008084c10bc30dd64dfe2342676d7eefac7f144e722f5b68545323dda7a6d",
    ),
    "timeline": (
        "https://www.voynichdoc.com/timeline",
        "641c40f0c25740d2ea6b371c752908ed34d83efff2bbbc6b5ac5ae5d4c76f665",
    ),
    "author": (
        "https://www.voynichdoc.com/autor",
        "bff8b374b3d84a9be7a370dfc0274d584ba8484b437fc8cf9876b4bdf3dee607",
    ),
    "f10r": (
        "https://www.voynichdoc.com/seccion-botanica/"
        "orquidea-macho-orchis-mascula-f10r/78",
        "245ab6e5934f27fe178f959fdc1b2579e308de91e43062b8828f815329ba3057",
    ),
    "f70r_outer": (
        "https://www.voynichdoc.com/seccion-astronomica-astrologica/"
        "zodiaco-piscis-f70r-circulo-imagenext/61",
        "f27b0e49a3cdb174d9eae333c7510f96e96a069640284a91039313000659947d",
    ),
}


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-audit/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def plain(data: bytes) -> str:
    value = data.decode("utf-8")
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def build() -> dict[str, object]:
    bodies = {name: download(url) for name, (url, _) in SOURCES.items()}
    hashes = {name: sha(body) for name, body in bodies.items()}
    if any(hashes[name] != expected for name, (_, expected) in SOURCES.items()):
        raise ValueError("public source drift; version rather than silently update")
    texts = {name: plain(body) for name, body in bodies.items()}

    disclosed_limits = {
        "not_literal_translation": (
            "should not be understood as literal translations" in texts["home"]
        ),
        "discourse_reorganized": "reorganizing the discourse" in texts["home"],
        "vocabulary_homogenized": "homogenizing the vocabulary" in texts["home"],
        "does_not_reflect_source_syntax_or_structure": (
            "do not purport to reflect the language, style, syntax, or structure"
            in texts["home"]
        ),
        "faithful_interpretation_deferred": (
            "will be made available for specialized analysis at a later stage"
            in texts["home"]
        ),
        "methodology_deferred": (
            "finally the methodology used" in texts["timeline"]
        ),
        "english_site_text_ai_translated": (
            "translated into English using AI tools (ChatGPT, 2026)" in texts["home"]
        ),
    }
    if not all(disclosed_limits.values()):
        raise ValueError("translation-scope disclosure drift")

    claim_checks = {
        "claims_two_languages_and_keys": (
            "identifying the cryptographic keys and the primary language" in texts["author"]
            and "deciphered the second language" in texts["author"]
        ),
        "f10r_complete_translation_present": (
            bool(re.search(r"Early purple orchid \(\s*Orchis mascula\s*\)\(f10r\)",
                           texts["f10r"]))
            and "[Complete translate]" in texts["f10r"]
        ),
        "f70r_complete_translation_present": (
            "Pisces (f70r) Images of the Outer Ring" in texts["f70r_outer"]
            and "[Complete translation]" in texts["f70r_outer"]
        ),
        "f70r_contains_precise_dates": all(
            phrase in texts["f70r_outer"]
            for phrase in ("twentieth day of April", "tenth of May", "ninth of June",
                           "third of November", "seventh of September")
        ),
    }
    if not all(claim_checks.values()):
        raise ValueError("published translation page drift")

    translation_pages = texts["f10r"] + " " + texts["f70r_outer"]
    raw_translation_html = bodies["f10r"].decode("utf-8") + bodies["f70r_outer"].decode("utf-8")
    machine_links = re.findall(
        r'href=["\']([^"\']+\.(?:csv|tsv|json|py|ipynb|zip)(?:[?#][^"\']*)?)["\']',
        raw_translation_html, flags=re.I,
    )
    method_links = [
        link for link in machine_links
        if link.split("?", 1)[0] != "/manifest.json"
    ]
    reproduction_checks = {
        "source_transliteration_shown": "transliteration" in translation_pages.lower(),
        "eva_source_shown": bool(re.search(r"\bEVA\b", translation_pages)),
        "line_or_token_alignment_shown": any(
            phrase in translation_pages.lower()
            for phrase in ("line-by-line", "token-by-token", "source token", "source line")
        ),
        "key_or_mapping_table_shown": any(
            phrase in translation_pages.lower()
            for phrase in ("mapping table", "key table", "substitution table")
        ),
        "machine_readable_method_linked": bool(method_links),
        "named_primary_or_second_language_on_translation_pages": bool(re.search(
            r"\b(?:Latin|German|Italian|Spanish|Arabic|Hebrew|Syriac|Greek|Romance)\b",
            translation_pages,
        )),
    }
    if any(reproduction_checks.values()):
        raise ValueError("a reproduction field appeared; manual audit required")

    admission_gates = {
        "literal_source_faithful_translation_available": False,
        "source_transliteration_to_plaintext_alignment_available": False,
        "cryptographic_keys_or_mapping_published": False,
        "claimed_languages_named_on_examined_translation_pages": False,
        "held_page_prediction_or_falsifier_published": False,
        "independent_reproduction_available": False,
    }
    return {
        "experiment": "EXTERNAL_VOYNICHDOC_TRANSLATION_CLAIM_AUDIT",
        "status": "HOLD_AS_TRANSLATION_EVIDENCE_METHOD_AND_ALIGNMENT_NOT_PUBLISHED",
        "decision": "DO_NOT_IMPORT_PLAINTEXT_PLANT_NAMES_DATES_OR_LANGUAGE_CLAIMS",
        "sources": {
            name: {"url": url, "sha256": hashes[name], "bytes": len(bodies[name])}
            for name, (url, _) in SOURCES.items()
        },
        "disclosed_limits": disclosed_limits,
        "claim_checks": claim_checks,
        "reproduction_checks": reproduction_checks,
        "admission_gates": admission_gates,
        "claim_ceiling": (
            "This holds the currently published modernized narratives outside the active "
            "evidence base until a source-aligned method is published. It does not prove "
            "the author's unpublished method or interpretations false."
        ),
    }


def report(result: dict[str, object]) -> str:
    return (
        "# External Voynichdoc translation-claim audit\n\n"
        f"Status: **{result['status']}**.\n\n"
        "The site publishes polished narratives for pages including f10r and f70r, "
        "and claims that cryptographic keys plus two languages have been identified. "
        "It does not currently name those languages on the examined translation pages, "
        "publish the keys, show an EVA/source transcription, align source groups to "
        "plaintext, provide a literal translation, expose a held-page falsifier, or "
        "provide machine-readable code/data.\n\n"
        "The site itself says the public text reorganizes discourse, homogenizes "
        "vocabulary, does not reflect source language/style/syntax/structure, and must "
        "not be understood as literal translation. It says a more faithful version and "
        "the methodology will appear later. The English website wording was produced "
        "with ChatGPT; the Spanish research is identified as official.\n\n"
        "Therefore none of the published plant names, remedies, political narrative, "
        "dates, language claims, or plaintext enters the active translation. Reopen "
        "only when the claimed method and source-aligned literal output are public and "
        "can predict held material. This hold does not prove the unpublished method "
        "false.\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite external translation-audit outputs")
    result = build()
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
