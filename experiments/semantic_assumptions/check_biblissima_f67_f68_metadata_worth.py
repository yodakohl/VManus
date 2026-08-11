#!/usr/bin/env python3
"""Metadata-only Biblissima worth screen for the f67/f68 circle gaps."""

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
SPEC = BASE / "BIBLISSIMA_F67_F68_METADATA_WORTH_SPEC.md"
DESCRIPTOR_URL = "https://portail.biblissima.fr/fr/ark%3A/43093/descf4fc91662474e76c35499d8330ef5ef170dae69e"
OUT_JSON = RESULTS / "biblissima_f67_f68_metadata_worth.json"
OUT_REPORT = RESULTS / "biblissima_f67_f68_metadata_worth_report.md"
BOURGES_ID = "ifdata56986cb2e622112dde8decd293f74c74f1504020"
SAINTE_GENEVIEVE_ID = "ifdataec2821b9662c8742888e61d816cd20594ddc4cd5"
EXPECTED_CANDIDATES = (BOURGES_ID, SAINTE_GENEVIEVE_ID)
ALLOWED_FIELDS = (
    "Type",
    "Feuillet / page",
    "Inscription",
    "Rubrique",
    "Date de fabrication",
    "Descripteurs",
    "Manuscrit",
    "Texte",
    "Lieu de fabrication",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fetch(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Biblissima-circle-worth/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location"):
            raise ValueError(f"unexpected response: {url}")
        return response.read().decode("utf-8")


def clean_text(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", value)).split())


def select_links(page: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    by_id: dict[str, dict[str, str]] = {}
    for url, title_markup in re.findall(
        r'<a href="(https://portail\.biblissima\.fr/fr/ark:/43093/ifdata[^"]+)"[^>]*>(.*?)</a>',
        page,
        flags=re.DOTALL,
    ):
        title = clean_text(title_markup)
        is_wind = title.startswith("Rose des vents")
        folded = title.casefold()
        is_sun_moon = "soleil" in folded and "lune" in folded
        if not (is_wind or is_sun_moon):
            continue
        record_id = url.rsplit("/", 1)[-1]
        row = {"record_id": record_id, "url": url, "title": title}
        if record_id in by_id and by_id[record_id] != row:
            raise ValueError("duplicate record identity drift")
        by_id[record_id] = row
    winds = sorted((row for row in by_id.values() if row["title"].startswith("Rose des vents")), key=lambda row: row["record_id"])
    sun_moon = sorted(
        (row for row in by_id.values() if "soleil" in row["title"].casefold() and "lune" in row["title"].casefold()),
        key=lambda row: row["record_id"],
    )
    if len(winds) != 18 or len(sun_moon) != 3 or {row["record_id"] for row in winds} & {row["record_id"] for row in sun_moon}:
        raise ValueError("Biblissima circle-family selection drift")
    return winds, sun_moon


def record(row: dict[str, str]) -> dict[str, object]:
    page = fetch(row["url"])
    headings = [clean_text(value) for value in re.findall(r"<h1[^>]*>(.*?)</h1>", page, flags=re.I | re.S)]
    if row["title"] not in headings:
        raise ValueError(f"record title drift: {row['record_id']}")
    fields: dict[str, str] = {}
    for name, value in re.findall(
        r"<li><strong>([^<]*?):\s*</strong>\s*<span>(.*?)</span></li>",
        page,
        flags=re.I | re.S,
    ):
        key = clean_text(name)
        clean = clean_text(value)
        if key in ALLOWED_FIELDS and clean:
            if key in fields and fields[key] != clean:
                raise ValueError(f"duplicate field drift: {row['record_id']} {key}")
            fields[key] = clean
    source_section = re.search(r'<section class="records" id="records">(.*?)</section>', page, flags=re.I | re.S)
    if source_section is None:
        raise ValueError(f"missing human source section: {row['record_id']}")
    source_item = re.search(r"<li>(.*?)</li>", source_section.group(1), flags=re.I | re.S)
    if source_item is None:
        raise ValueError(f"missing human source item: {row['record_id']}")
    source_url_match = re.search(r'<a href="([^"]+)"', source_item.group(1), flags=re.I | re.S)
    if source_url_match is None:
        raise ValueError(f"missing human source URL: {row['record_id']}")
    source_name = clean_text(source_item.group(1).split("<a", 1)[0]).rstrip(" :")
    info_match = re.search(r"var iiifInfoUrl\s*=\s*(\[[^;]*\]);", page, flags=re.S)
    info_urls = json.loads(info_match.group(1)) if info_match is not None else []
    if not isinstance(info_urls, list) or any(not isinstance(value, str) or not value.startswith("https://") for value in info_urls):
        raise ValueError(f"invalid IIIF locator declaration: {row['record_id']}")
    return {
        **row,
        "fields": fields,
        "data_source": source_name,
        "source_url_not_opened": source_url_match.group(1),
        "iiif_info_urls_not_opened": info_urls,
    }


def date_through_fifteenth_century(value: str) -> bool:
    years = [int(item) for item in re.findall(r"(?<![0-9])([0-9]{4})(?![0-9])", value)]
    if years:
        return max(years) <= 1500
    centuries = [int(item) for item in re.findall(r"(?<![0-9])([0-9]{1,2})(?:e|er)\s*(?:-|à|au)?\s*(?:[0-9]{1,2}(?:e|er))?\s*(?:s\.|siècle)", value, flags=re.I)]
    return bool(centuries) and max(centuries) <= 15


def descriptor_set(row: dict[str, object]) -> set[str]:
    value = str(row["fields"].get("Descripteurs", ""))
    return {item.strip().casefold() for item in value.split(",") if item.strip()}


def human_review_gates(row: dict[str, object]) -> dict[str, bool]:
    descriptors = descriptor_set(row)
    human_terms = {"homme", "femme", "tête", "de profil", "de face", "en médaillon"}
    return {
        "date_through_fifteenth_century": date_through_fifteenth_century(str(row["fields"].get("Date de fabrication", ""))),
        "circle_and_winds_descriptors": {"cercle", "vents"}.issubset(descriptors),
        "human_figure_descriptor": bool(descriptors & human_terms),
        "named_human_data_source": bool(row["data_source"] and row["source_url_not_opened"]),
        "page_embedded_iiif_locator": bool(row["iiif_info_urls_not_opened"]),
        "identification_inscription_descriptor": "inscription identification" in descriptors,
    }


def source_transfer_gates(row: dict[str, object]) -> dict[str, bool]:
    haystack = " ".join([str(row["title"]), *map(str, row["fields"].values())])
    return {
        "complete_readable_ordered_owned_register": bool(re.search(r"registre ordonné|ordered owned register|propriétaire des étiquettes", haystack, re.I)),
        "one_to_one_common_slot_coordinate": bool(re.search(r"one-to-one common slot|coordonnée commune|correspondance univoque", haystack, re.I)),
        "preserved_start_and_orientation": bool(re.search(r"point de départ.*orientation|start.*orientation", haystack, re.I)),
    }


def partition(records: list[dict[str, object]]) -> dict[str, int]:
    in_range = sum(date_through_fifteenth_century(str(row["fields"].get("Date de fabrication", ""))) for row in records)
    undated = sum("Date de fabrication" not in row["fields"] for row in records)
    return {
        "record_count": len(records),
        "records_with_human_inscription": sum("Inscription" in row["fields"] for row in records),
        "records_through_fifteenth_century": in_range,
        "records_without_date": undated,
        "records_after_fifteenth_century": len(records) - in_range - undated,
    }


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Biblissima circle-worth outputs")
    wind_links, sun_moon_links = select_links(fetch(DESCRIPTOR_URL))
    all_links = sorted(wind_links + sun_moon_links, key=lambda row: row["record_id"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(record, all_links))
    by_id = {str(row["record_id"]): row for row in records}
    wind_records = [by_id[row["record_id"]] for row in wind_links]
    sun_moon_records = [by_id[row["record_id"]] for row in sun_moon_links]
    wind_summary = partition(wind_records)
    astronomy_summary = partition(sun_moon_records)
    expected_wind_summary = {
        "record_count": 18,
        "records_with_human_inscription": 11,
        "records_through_fifteenth_century": 15,
        "records_without_date": 0,
        "records_after_fifteenth_century": 3,
    }
    expected_astronomy_summary = {
        "record_count": 3,
        "records_with_human_inscription": 1,
        "records_through_fifteenth_century": 2,
        "records_without_date": 0,
        "records_after_fifteenth_century": 1,
    }
    if wind_summary != expected_wind_summary or astronomy_summary != expected_astronomy_summary:
        raise ValueError("circle-family summary drift")
    candidates = []
    for row in wind_records:
        gates = human_review_gates(row)
        required = [value for key, value in gates.items() if key != "identification_inscription_descriptor"]
        if all(required):
            transfer = source_transfer_gates(row)
            if any(transfer.values()):
                raise ValueError("unexpected source-transfer metadata")
            candidates.append({**row, "human_review_gates": gates, "source_transfer_gates": transfer})
    if tuple(row["record_id"] for row in candidates) != EXPECTED_CANDIDATES:
        raise ValueError("human-review candidate drift")
    if not candidates[1]["human_review_gates"]["identification_inscription_descriptor"]:
        raise ValueError("Sainte-Geneviève identification-inscription drift")
    astronomy_star_candidates = [row for row in sun_moon_records if "étoile" in str(row["title"]).casefold()]
    if astronomy_star_candidates:
        raise ValueError("unexpected f68 metadata candidate")
    stable_projection = {
        "descriptor_url": DESCRIPTOR_URL,
        "wind_records": wind_records,
        "sun_moon_records": sun_moon_records,
    }
    result = {
        "experiment": "BIBLISSIMA_F67_F68_METADATA_WORTH",
        "status": "PROVISIONAL_TWO_QUALIFIED_HUMAN_IMAGE_REVIEW_CANDIDATES",
        "decision": "RETAIN_BOURGES_MS105_F95V_AND_SG_MS1029_F135_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER",
        "source": {
            "publisher": "Biblissima / Initiale / Mandragore",
            "descriptor_url": DESCRIPTOR_URL,
            "stable_projection_sha256": sha(canonical(stable_projection)),
        },
        "wind_family": wind_summary,
        "sun_moon_family": {**astronomy_summary, "records_naming_sun_moon_and_stars": 0},
        "human_review_candidates": candidates,
        "gates": {
            "qualified_human_wind_topology_inspection": True,
            "qualified_human_f68_astronomy_inspection": False,
            "source_transfer_authorized": False,
            "image_or_iiif_document_opened": False,
            "paper_review_authorized": False,
        },
        "source_access": {
            "biblissima_descriptor_and_text_records_opened": True,
            "named_source_urls_opened": False,
            "embedded_iiif_locator_strings_recorded": True,
            "iiif_info_thumbnail_image_canvas_manifest_or_manuscript_page_opened": False,
            "paper_pdf_ocr_or_automated_visual_output_opened": False,
            "decoder_claims_opened": False,
        },
        "inputs": {SPEC.name: sha(SPEC.read_bytes())},
        "claim_ceiling": "Bourges BM Ms. 105 f.095v and Bibliothèque Sainte-Geneviève Ms. 1029 f.135 are provenance-clean wind-circle records worth qualified human topology inspection; the latter is additionally catalogued with a man, woman, heads in medallions, and identification inscriptions. Current metadata fixes no complete readable owned register, common one-to-one slot coordinate, start, or orientation, and the Sun/Moon family supplies no Sun-Moon-stars record. No direction, wind, person, head, sex, object, Sun, Moon, star, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f67 or f68.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
        "# Biblissima f67/f68 diagram metadata worth screen\n\n"
        "Decision: **RETAIN_BOURGES_MS105_F95V_AND_SG_MS1029_F135_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER**.\n\n"
        "The complete Biblissima `Rose des vents` title family has 18 records: 11 publish human inscriptions, 15 are "
        "dated through the fifteenth century, and three are later. Two records pass the frozen human-review gate. "
        "Bourges BM Ms. 105 f.095v is dated 1090–1110 and catalogued with profile and frontal heads, a circle, cardinal "
        "points, winds, and blowing. Bibliothèque Sainte-Geneviève Ms. 1029 f.135 is dated 1345–1355 and catalogued "
        "with a man, woman, heads in medallions, identification inscriptions, a circle, and winds. Both records have "
        "Initiale provenance links and page-embedded IIIF locators.\n\n"
        "This clears only a qualified-human inspection threshold. Neither record publishes an inscription transcription, "
        "an exact cardinality, a complete owned ordered register, a one-to-one common slot coordinate, or a start and "
        "orientation. BnF Latin 18499 f.26 remains the already-consumed readable twelve-wind comparator, not a newly "
        "selected source.\n\n"
        "The complete three-record Sun/Moon title family contains two medieval eclipse diagrams and one eighteenth-century "
        "diagram, but zero records name the Sun, Moon, and stars together. It supplies no f68 review candidate.\n\n"
        "No named source URL, IIIF information document, thumbnail, image, canvas, manifest, manuscript page, paper, PDF, "
        "OCR, automated visual output, or decoder claim was opened. No direction, wind, person, head, sex, object, Sun, "
        "Moon, star, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f67 or f68.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
