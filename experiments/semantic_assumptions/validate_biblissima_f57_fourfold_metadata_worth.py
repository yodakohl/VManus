#!/usr/bin/env python3
"""Independent validation of the Biblissima f57 metadata worth lead."""

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
PRODUCER = BASE / "check_biblissima_f57_fourfold_metadata_worth.py"
RESULT = RESULTS / "biblissima_f57_fourfold_metadata_worth.json"
REPORT = RESULTS / "biblissima_f57_fourfold_metadata_worth_report.md"
OUT = RESULTS / "biblissima_f57_fourfold_metadata_worth_validation.json"
OUT_MD = RESULTS / "biblissima_f57_fourfold_metadata_worth_validation_report.md"
DESC = "https://portail.biblissima.fr/fr/ark%3A/43093/descf4fc91662474e76c35499d8330ef5ef170dae69e"
RECORD_ID = "ifdataa421994eb0ca3aa5859ed3e48cc58069932100fb"
RECORD_URL = "https://portail.biblissima.fr/fr/ark:/43093/" + RECORD_ID
MANUSCRIPT_URL = "https://portail.biblissima.fr/fr/ark:/43093/mdata6048b6d2f5407f5b2d271313354894063fba2f8c"
MANDRAGORE = "https://mandragore.bnf.fr/ark:/12148/cgfbt65147k"
MANIFEST = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b9066969x/manifest.json"
WITNESS = "https://gallica.bnf.fr/ark:/12148/btv1b9066969x"
FROZEN = {
    SPEC: "41ec5918edcd26616dd6b77deafc034d27983d9cecb8799feb055d4cd95025b4",
    PRODUCER: "a8c76828269314f3bb6dd0608141d824a25f1a711e0603100f369663e8015a7d",
    RESULT: "3d581c40330763ddef573e115e7cd3f5d8090c2516141cb8dd65cf01d6a48126",
    REPORT: "7914a72f30a4afb7de4c2bc692bae42c56b116f4115cccd3db65005dd978b8f7",
}
FAMILIES = (
    "Âges, humeurs, saisons, éléments",
    "Éléments et humeurs",
    "Éléments et leurs qualités",
    "Éléments, saisons, humeurs",
    "Quatre éléments (Les)",
    "Saisons et humeurs",
    "Zodiaque, éléments et qualités",
)
FIELD_ORDER = ("Type", "Feuillet / page", "Inscription", "Date de fabrication", "Descripteurs", "Manuscrit", "Texte", "Lieu de fabrication")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def strict_json() -> dict[str, object]:
    raw = RESULT.read_bytes()

    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        if len(pairs) != len({key for key, _ in pairs}):
            raise ValueError("duplicate JSON key")
        return dict(pairs)

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=hook, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value, dict) or canonical(value) != raw:
        raise ValueError("result is not canonical")
    return value


def live(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Biblissima-independent-validator/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location") is not None:
            raise ValueError(f"unexpected response: {url}")
        return response.read().decode("utf-8")


def plain(markup: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", markup)).split())


def family_links() -> list[dict[str, str]]:
    page = live(DESC)
    rows = []
    for url, title_markup in re.findall(r'<a href="(https://portail\.biblissima\.fr/fr/ark:/43093/ifdata[^"]+)"[^>]*>(.*?)</a>', page, flags=re.S):
        title = plain(title_markup)
        if any(family.casefold() in title.casefold() for family in FAMILIES):
            rows.append({"url": url, "record_id": url.rsplit("/", 1)[-1], "title": title})
    rows = sorted(rows, key=lambda row: row["record_id"])
    if len(rows) != 24 or len({row["record_id"] for row in rows}) != 24:
        raise ValueError("family orbit drift")
    return rows


def rebuild(row: dict[str, str]) -> dict[str, object]:
    page = live(row["url"])
    headings = {plain(value) for value in re.findall(r"<h1[^>]*>(.*?)</h1>", page, flags=re.I | re.S)}
    if row["title"] not in headings:
        raise ValueError("record heading drift")
    block = re.search(r'<ul class="description">(.*?)</ul>\s*</div>', page, flags=re.I | re.S)
    if block is None:
        raise ValueError("description block absent")
    observed: dict[str, str] = {}
    for label, value in re.findall(r"<li><strong>(.*?):</strong>\s*<span>(.*?)</span></li>", block.group(1), flags=re.I | re.S):
        key, content = plain(label), plain(value)
        if content:
            observed[key] = content
    source = re.search(r"Source des données.*?<li>\s*([^<]+).*?<a href=\"([^\"]+)\"", page, flags=re.I | re.S)
    if source is None:
        raise ValueError("record data source absent")
    return {**row, "fields": {field: observed[field] for field in FIELD_ORDER if field in observed}, "data_source": plain(source.group(1)), "source_url": source.group(2)}


def medieval(date: str) -> bool:
    match = re.search(r"([0-9]+)(?:e|er) siècle", date)
    return match is not None and int(match.group(1)) <= 15


def source_details() -> tuple[dict[str, object], dict[str, object]]:
    mandragore_page = live(MANDRAGORE)
    facts = {
        "ark": "ark:/12148/cgfbt65147k" in mandragore_page,
        "shelfmark": "Latin 4922" in mandragore_page,
        "folio": "f. 1v" in mandragore_page,
        "subject": "Âges, humeurs, saisons, éléments" in mandragore_page,
        "inscription": "noms des âges, humeurs, saisons et éléments / quatuor sunt etates (humores/partes anni/elementa) / melius (pejus) se habet / frigidus et humidus..." in mandragore_page,
        "keywords_exactly_four": "4&nbsp;Mots-clés" in mandragore_page,
        "no_mandragore_image": "Pas d&#39;image" in mandragore_page,
    }
    if not all(facts.values()):
        raise ValueError("Mandragore source drift")
    manuscript_page = live(MANUSCRIPT_URL)
    manifests = sorted(set(re.findall(r'data-manifest="([^"]+)"', manuscript_page)))
    if manifests != [MANIFEST] or WITNESS not in manuscript_page:
        raise ValueError("digital witness drift")
    return ({"url": MANDRAGORE, "facts": facts}, {"url": MANUSCRIPT_URL, "iiif_manifest_url_not_opened": MANIFEST, "gallica_witness_url_not_opened": WITNESS})


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing to overwrite Biblissima validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen hash mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_json()
    checks.append("canonical_duplicate_free_result")
    links = family_links()
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(rebuild, links))
    records.sort(key=lambda row: str(row["record_id"]))
    inscriptions = sum("Inscription" in row["fields"] for row in records)
    in_range = sum(medieval(str(row["fields"].get("Date de fabrication", ""))) for row in records)
    undated = sum("Date de fabrication" not in row["fields"] for row in records)
    later = len(records) - in_range - undated
    if (inscriptions, in_range, undated, later) != (13, 22, 1, 1):
        raise ValueError("family counts drift")
    checks.extend(("twenty_four_unique_family_records", "thirteen_human_inscriptions", "date_partition_22_1_1", "human_fields_only"))
    candidate = next(row for row in records if row["record_id"] == RECORD_ID)
    inscription = str(candidate["fields"].get("Inscription", ""))
    candidate_text = " ".join([str(candidate["title"]), *map(str, candidate["fields"].values())])
    inspection = {
        "date_through_fifteenth_century": medieval(str(candidate["fields"].get("Date de fabrication", ""))),
        "ages_humours_seasons_elements_named": all(item in inscription.casefold() for item in ("âges", "humeurs", "saisons", "éléments")),
        "literal_inscription_values_or_fragments": "quatuor sunt etates" in inscription and "frigidus et humidus" in inscription,
        "official_digital_witness_url": True,
    }
    transfer = {
        "four_people_portraits_or_figures_stated": bool(re.search(r"\b(quatre|four)\s+(personnages?|personnes?|portraits?|philosophes?|figures?|têtes?|visages?|people|persons?|heads?|faces?)\b", candidate_text, re.I)),
        "two_four_item_registers_with_explicit_slot_ownership": bool(re.search(r"\bowned\b|\bone-to-one\b|\bslot\b|\bregister\b|\bappartient\b|\brelié\b|\bconnecté\b", candidate_text, re.I)),
        "start_and_orientation_preserved": bool(re.search(r"\bstart\b|\borientation\b|\bpoint de départ\b|\bsens de lecture\b", candidate_text, re.I)),
    }
    if not all(inspection.values()) or any(transfer.values()):
        raise ValueError("candidate gate drift")
    checks.extend(("candidate_identity_and_literal_inscription", "inspection_gate_all_true", "transfer_gate_all_false"))
    mandragore, manuscript = source_details()
    checks.extend(("mandragore_independent_source_agreement", "mandragore_no_image", "official_gallica_witness_link", "iiif_manifest_not_opened"))
    projection = {"descriptor_url": DESC, "selected_records": records, "mandragore": mandragore, "manuscript": manuscript}
    expected = {
        "experiment": "BIBLISSIMA_F57_FOURFOLD_METADATA_WORTH",
        "status": "PROVISIONAL_WORTH_QUALIFIED_HUMAN_IMAGE_REVIEW",
        "decision": "RETAIN_LATIN_4922_F1V_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER",
        "source": {"publisher": "Biblissima / Mandragore (BnF)", "descriptor_url": DESC, "stable_projection_sha256": sha(canonical(projection))},
        "family": {"selected_record_count": 24, "records_with_human_inscription": inscriptions, "records_through_fifteenth_century": in_range, "records_without_date": undated, "records_after_fifteenth_century": later, "selection_subjects": list(FAMILIES)},
        "candidate": {"record_id": RECORD_ID, "title": candidate["title"], "fields": candidate["fields"], "biblissima_url": candidate["url"], "mandragore_url": MANDRAGORE, "manuscript_metadata_url": MANUSCRIPT_URL, "gallica_witness_url_not_opened": WITNESS, "iiif_manifest_url_not_opened": MANIFEST, "inspection_gates": inspection, "transfer_gates": transfer},
        "gates": {"worth_qualified_human_image_inspection": True, "source_transfer_authorized": False, "image_or_manifest_opened": False, "paper_review_authorized": False},
        "source_access": {"biblissima_descriptor_and_text_records_opened": True, "mandragore_text_record_opened": True, "biblissima_manuscript_metadata_opened": True, "thumbnail_image_canvas_iiif_manifest_or_gallica_witness_opened": False, "manuscript_paper_pdf_ocr_or_automated_visual_output_opened": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: FROZEN[SPEC]},
        "claim_ceiling": "BnF Latin 4922 f.1v is a provenance-clean fourfold age-humour-season-element inscription and a precise candidate for qualified human topology inspection, but current human metadata states no four persons, no owned two-register slot map, and no start/orientation; no age, humour, season, element, person, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f57v.",
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.extend(("stable_projection_digest", "exact_result_object", "exact_gate_vector"))
    report = (
        "# Biblissima f57 fourfold-register metadata worth screen\n\n"
        "Decision: **RETAIN_LATIN_4922_F1V_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER**.\n\n"
        "A fixed human-thesaurus selection yields 24 Biblissima records: 13 publish inscriptions, 22 are explicitly dated through the fifteenth century, one lacks a date, and one is from 1583. The strongest record is BnF Latin 4922 f.1v, a late-fourteenth-century Norwich *Polychronicon* diagram catalogued as `Âges, humeurs, saisons, éléments`. Mandragore publishes the inscription class and fragments `quatuor sunt etates (humores/partes anni/elementa)` and `frigidus et humidus...`. Biblissima links the digitized manuscript and IIIF manifest.\n\n"
        "This is worth qualified human inspection of the diagram topology. It is not yet a Voynich source key: the human metadata names no four people, portraits, philosophers, figures, heads, or faces; states no one-to-one ownership of two four-item registers; and fixes no start or orientation. Mandragore itself has no image for the record, while the whole manuscript witness is available through Gallica.\n\n"
        "No thumbnail, image, canvas, IIIF manifest body, Gallica witness, manuscript page, paper, PDF, OCR, automated visual output, or decoder claim entered this screen. No age, humour, season, element, person, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f57v.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("exact_report_bytes")
    validation = {
        "experiment": "BIBLISSIMA_F57_FOURFOLD_METADATA_WORTH_VALIDATION",
        "status": "PASS_INDEPENDENT_24_RECORD_LIVE_SOURCE_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "counts": {"selected_records": 24, "human_inscriptions": 13, "medieval_records": 22, "human_review_candidates": 1, "source_transfer_candidates": 0},
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Biblissima f57 fourfold-register metadata worth — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator independently reconstructs the 24-record human-thesaurus "
        "family, 13 inscriptions, exact date partition, Latin 4922 f.1v source fields, Mandragore agreement, Gallica "
        "witness link, candidate gates, canonical result, and report.\n\n"
        "This validates a qualified-human topology-inspection lead only. It authorizes no source transfer and supplies "
        "no age, humour, season, element, person, slot, label, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
