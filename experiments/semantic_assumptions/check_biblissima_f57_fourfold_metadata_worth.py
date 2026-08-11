#!/usr/bin/env python3
"""Metadata-only Biblissima/Mandragore worth screen for the f57v gap."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "BIBLISSIMA_F57_FOURFOLD_METADATA_WORTH_SPEC.md"
DESCRIPTOR_URL = "https://portail.biblissima.fr/fr/ark%3A/43093/descf4fc91662474e76c35499d8330ef5ef170dae69e"
BIBLISSIMA_BASE = "https://portail.biblissima.fr/fr/ark:/43093/"
LAT4922_RECORD_ID = "ifdataa421994eb0ca3aa5859ed3e48cc58069932100fb"
LAT4922_MANUSCRIPT_URL = BIBLISSIMA_BASE + "mdata6048b6d2f5407f5b2d271313354894063fba2f8c"
MANDRAGORE_URL = "https://mandragore.bnf.fr/ark:/12148/cgfbt65147k"
GALlica_MANIFEST = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/manifest.json"
GALlica_WITNESS = "https://gallica.bnf.fr/ark:/12148/btv1b9066969x"
OUT_JSON = RESULTS / "biblissima_f57_fourfold_metadata_worth.json"
OUT_REPORT = RESULTS / "biblissima_f57_fourfold_metadata_worth_report.md"
SUBJECTS = (
    "Âges, humeurs, saisons, éléments",
    "Éléments et humeurs",
    "Éléments et leurs qualités",
    "Éléments, saisons, humeurs",
    "Quatre éléments (Les)",
    "Saisons et humeurs",
    "Zodiaque, éléments et qualités",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fetch(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Biblissima-metadata-worth/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location"):
            raise ValueError(f"unexpected response: {url}")
        return response.read().decode("utf-8")


def text(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", value)).split())


def selected_links(page: str) -> list[dict[str, str]]:
    rows = []
    for url, title_markup in re.findall(
        r'<a href="(https://portail\.biblissima\.fr/fr/ark:/43093/ifdata[^"]+)"[^>]*>(.*?)</a>',
        page,
        flags=re.DOTALL,
    ):
        title = text(title_markup)
        if any(subject.casefold() in title.casefold() for subject in SUBJECTS):
            rows.append({"url": url, "record_id": url.rsplit("/", 1)[-1], "title": title})
    rows.sort(key=lambda row: row["record_id"])
    if len(rows) != 24 or len({row["record_id"] for row in rows}) != 24:
        raise ValueError("selected Biblissima family drift")
    return rows


def record(row: dict[str, str]) -> dict[str, object]:
    page = fetch(row["url"])
    headings = [text(value) for value in re.findall(r"<h1[^>]*>(.*?)</h1>", page, flags=re.I | re.S)]
    block = re.search(r'<ul class="description">(.*?)</ul>\s*</div>', page, flags=re.I | re.S)
    if block is None or row["title"] not in headings:
        raise ValueError(f"record identity drift: {row['record_id']}")
    fields: dict[str, str] = {}
    for name, value in re.findall(r"<li><strong>(.*?):</strong>\s*<span>(.*?)</span></li>", block.group(1), flags=re.I | re.S):
        key = text(name)
        clean = text(value)
        if clean:
            fields[key] = clean
    allowed = ("Type", "Feuillet / page", "Inscription", "Date de fabrication", "Descripteurs", "Manuscrit", "Texte", "Lieu de fabrication")
    projection = {key: fields[key] for key in allowed if key in fields}
    source_match = re.search(r"Source des données.*?<li>\s*([^<]+).*?<a href=\"([^\"]+)\"", page, flags=re.I | re.S)
    if source_match is None:
        raise ValueError("missing human data source")
    return {**row, "fields": projection, "data_source": text(source_match.group(1)), "source_url": source_match.group(2)}


def century_in_range(value: str) -> bool:
    match = re.search(r"([0-9]+)(?:e|er) siècle", value)
    return match is not None and int(match.group(1)) <= 15


def person_terms(value: str) -> bool:
    return bool(re.search(r"\b(quatre|four)\s+(personnages?|personnes?|portraits?|philosophes?|figures?|têtes?|visages?|people|persons?|heads?|faces?)\b", value, re.I))


def mandragore_projection() -> dict[str, object]:
    page = fetch(MANDRAGORE_URL)
    facts = {
        "ark": "ark:/12148/cgfbt65147k" in page,
        "shelfmark": "Latin 4922" in page,
        "folio": "f. 1v" in page,
        "subject": "Âges, humeurs, saisons, éléments" in page,
        "inscription": "noms des âges, humeurs, saisons et éléments / quatuor sunt etates (humores/partes anni/elementa) / melius (pejus) se habet / frigidus et humidus..." in page,
        "keywords_exactly_four": "4&nbsp;Mots-clés" in page,
        "no_mandragore_image": "Pas d&#39;image" in page,
    }
    if not all(facts.values()):
        raise ValueError("Mandragore candidate drift")
    return {"url": MANDRAGORE_URL, "facts": facts}


def manuscript_projection() -> dict[str, object]:
    page = fetch(LAT4922_MANUSCRIPT_URL)
    manifests = sorted(set(re.findall(r'data-manifest="([^"]+)"', page)))
    if manifests != [GALlica_MANIFEST] or GALlica_WITNESS not in page:
        raise ValueError("Latin 4922 digital witness drift")
    return {"url": LAT4922_MANUSCRIPT_URL, "iiif_manifest_url_not_opened": GALlica_MANIFEST, "gallica_witness_url_not_opened": GALlica_WITNESS}


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Biblissima worth outputs")
    links = selected_links(fetch(DESCRIPTOR_URL))
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(record, links))
    records.sort(key=lambda row: str(row["record_id"]))
    inscription_count = sum("Inscription" in row["fields"] for row in records)
    in_range_count = sum(century_in_range(str(row["fields"].get("Date de fabrication", ""))) for row in records)
    undated_count = sum("Date de fabrication" not in row["fields"] for row in records)
    out_of_range_count = len(records) - in_range_count - undated_count
    if inscription_count != 13 or in_range_count != 22 or undated_count != 1 or out_of_range_count != 1:
        raise ValueError("family summary drift")
    candidate = next(row for row in records if row["record_id"] == LAT4922_RECORD_ID)
    candidate_text = " ".join([candidate["title"], *candidate["fields"].values()])
    inscription = str(candidate["fields"].get("Inscription", ""))
    inspection_gates = {
        "date_through_fifteenth_century": century_in_range(str(candidate["fields"].get("Date de fabrication", ""))),
        "ages_humours_seasons_elements_named": all(value in inscription.casefold() for value in ("âges", "humeurs", "saisons", "éléments")),
        "literal_inscription_values_or_fragments": "quatuor sunt etates" in inscription and "frigidus et humidus" in inscription,
        "official_digital_witness_url": True,
    }
    transfer_gates = {
        "four_people_portraits_or_figures_stated": person_terms(candidate_text),
        "two_four_item_registers_with_explicit_slot_ownership": bool(re.search(r"owned|one-to-one|slot|register|appartient|relié|connecté", candidate_text, re.I)),
        "start_and_orientation_preserved": bool(re.search(r"\bstart\b|\borientation\b|\bpoint de départ\b|\bsens de lecture\b", candidate_text, re.I)),
    }
    if not all(inspection_gates.values()) or any(transfer_gates.values()):
        raise ValueError("candidate gate drift")
    mandragore = mandragore_projection()
    manuscript = manuscript_projection()
    stable_projection = {"descriptor_url": DESCRIPTOR_URL, "selected_records": records, "mandragore": mandragore, "manuscript": manuscript}
    result = {
        "experiment": "BIBLISSIMA_F57_FOURFOLD_METADATA_WORTH",
        "status": "PROVISIONAL_WORTH_QUALIFIED_HUMAN_IMAGE_REVIEW",
        "decision": "RETAIN_LATIN_4922_F1V_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER",
        "source": {"publisher": "Biblissima / Mandragore (BnF)", "descriptor_url": DESCRIPTOR_URL, "stable_projection_sha256": sha(canonical(stable_projection))},
        "family": {"selected_record_count": len(records), "records_with_human_inscription": inscription_count, "records_through_fifteenth_century": in_range_count, "records_without_date": undated_count, "records_after_fifteenth_century": out_of_range_count, "selection_subjects": list(SUBJECTS)},
        "candidate": {"record_id": LAT4922_RECORD_ID, "title": candidate["title"], "fields": candidate["fields"], "biblissima_url": candidate["url"], "mandragore_url": MANDRAGORE_URL, "manuscript_metadata_url": LAT4922_MANUSCRIPT_URL, "gallica_witness_url_not_opened": GALlica_WITNESS, "iiif_manifest_url_not_opened": GALlica_MANIFEST, "inspection_gates": inspection_gates, "transfer_gates": transfer_gates},
        "gates": {"worth_qualified_human_image_inspection": True, "source_transfer_authorized": False, "image_or_manifest_opened": False, "paper_review_authorized": False},
        "source_access": {"biblissima_descriptor_and_text_records_opened": True, "mandragore_text_record_opened": True, "biblissima_manuscript_metadata_opened": True, "thumbnail_image_canvas_iiif_manifest_or_gallica_witness_opened": False, "manuscript_paper_pdf_ocr_or_automated_visual_output_opened": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: sha(SPEC.read_bytes())},
        "claim_ceiling": "BnF Latin 4922 f.1v is a provenance-clean fourfold age-humour-season-element inscription and a precise candidate for qualified human topology inspection, but current human metadata states no four persons, no owned two-register slot map, and no start/orientation; no age, humour, season, element, person, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f57v.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
        "# Biblissima f57 fourfold-register metadata worth screen\n\n"
        "Decision: **RETAIN_LATIN_4922_F1V_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER**.\n\n"
        "A fixed human-thesaurus selection yields 24 Biblissima records: 13 publish inscriptions, 22 are explicitly "
        "dated through the fifteenth century, one lacks a date, and one is from 1583. The strongest record is BnF "
        "Latin 4922 f.1v, a late-fourteenth-century Norwich "
        "*Polychronicon* diagram catalogued as `Âges, humeurs, saisons, éléments`. Mandragore publishes the inscription "
        "class and fragments `quatuor sunt etates (humores/partes anni/elementa)` and `frigidus et humidus...`. "
        "Biblissima links the digitized manuscript and IIIF manifest.\n\n"
        "This is worth qualified human inspection of the diagram topology. It is not yet a Voynich source key: the "
        "human metadata names no four people, portraits, philosophers, figures, heads, or faces; states no one-to-one "
        "ownership of two four-item registers; and fixes no start or orientation. Mandragore itself has no image for "
        "the record, while the whole manuscript witness is available through Gallica.\n\n"
        "No thumbnail, image, canvas, IIIF manifest body, Gallica witness, manuscript page, paper, PDF, OCR, automated "
        "visual output, or decoder claim entered this screen. No age, humour, season, element, person, slot, label, word, "
        "sound, language, cipher, plaintext, meaning, or translation transfers to f57v.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
