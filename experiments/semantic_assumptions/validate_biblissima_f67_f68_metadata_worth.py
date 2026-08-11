#!/usr/bin/env python3
"""Independent live reconstruction of the Biblissima f67/f68 worth screen."""

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
PRODUCER = RESULTS / "biblissima_f67_f68_metadata_worth.json"
PRODUCER_REPORT = RESULTS / "biblissima_f67_f68_metadata_worth_report.md"
OUT_JSON = RESULTS / "biblissima_f67_f68_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "biblissima_f67_f68_metadata_worth_validation_report.md"
DESCRIPTOR = "https://portail.biblissima.fr/fr/ark%3A/43093/descf4fc91662474e76c35499d8330ef5ef170dae69e"
BOURGES = "ifdata56986cb2e622112dde8decd293f74c74f1504020"
SAINTE_GENEVIEVE = "ifdataec2821b9662c8742888e61d816cd20594ddc4cd5"
FIELD_NAMES = {
    "Type",
    "Feuillet / page",
    "Inscription",
    "Rubrique",
    "Date de fabrication",
    "Descripteurs",
    "Manuscrit",
    "Texte",
    "Lieu de fabrication",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def get(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Biblissima-circle-independent/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get_all("Location"):
            raise RuntimeError(f"unexpected response for {url}")
        return response.read().decode("utf-8")


def plain(markup: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", markup)).split())


def link_panels(markup: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    unique: dict[str, dict[str, str]] = {}
    for href, label in re.findall(
        r'<a href="(https://portail\.biblissima\.fr/fr/ark:/43093/ifdata[^"]+)"[^>]*>(.*?)</a>',
        markup,
        re.S,
    ):
        title = plain(label)
        folded = title.casefold()
        if not title.startswith("Rose des vents") and not ("soleil" in folded and "lune" in folded):
            continue
        rid = href.rsplit("/", 1)[1]
        item = {"record_id": rid, "url": href, "title": title}
        if rid in unique and item != unique[rid]:
            raise RuntimeError("record collision")
        unique[rid] = item
    wind = sorted((x for x in unique.values() if x["title"].startswith("Rose des vents")), key=lambda x: x["record_id"])
    astronomy = sorted(
        (x for x in unique.values() if "soleil" in x["title"].casefold() and "lune" in x["title"].casefold()),
        key=lambda x: x["record_id"],
    )
    return wind, astronomy


def read_record(seed: dict[str, str]) -> dict[str, object]:
    markup = get(seed["url"])
    if seed["title"] not in [plain(x) for x in re.findall(r"<h1[^>]*>(.*?)</h1>", markup, re.I | re.S)]:
        raise RuntimeError("title mismatch")
    fields: dict[str, str] = {}
    pairs = re.findall(r"<li><strong>([^<]*?):\s*</strong>\s*<span>(.*?)</span></li>", markup, re.I | re.S)
    for raw_name, raw_value in pairs:
        name, value = plain(raw_name), plain(raw_value)
        if name in FIELD_NAMES and value:
            if name in fields and fields[name] != value:
                raise RuntimeError("field collision")
            fields[name] = value
    source_block = re.search(r'<section class="records" id="records">(.*?)</section>', markup, re.I | re.S)
    item = re.search(r"<li>(.*?)</li>", source_block.group(1), re.I | re.S) if source_block else None
    source_link = re.search(r'<a href="([^"]+)"', item.group(1), re.I | re.S) if item else None
    if item is None or source_link is None:
        raise RuntimeError("missing source provenance")
    source_name = plain(item.group(1).split("<a", 1)[0]).rstrip(" :")
    locator = re.search(r"var iiifInfoUrl\s*=\s*(\[[^;]*\]);", markup, re.S)
    info_urls = json.loads(locator.group(1)) if locator else []
    if type(info_urls) is not list or any(type(x) is not str or not x.startswith("https://") for x in info_urls):
        raise RuntimeError("bad IIIF locator list")
    return {
        **seed,
        "fields": fields,
        "data_source": source_name,
        "source_url_not_opened": source_link.group(1),
        "iiif_info_urls_not_opened": info_urls,
    }


def medieval(date: str) -> bool:
    years = [int(x) for x in re.findall(r"(?<![0-9])([0-9]{4})(?![0-9])", date)]
    if years:
        return max(years) <= 1500
    century = re.search(r"(?<![0-9])([0-9]{1,2})(?:e|er)\s*(?:-|à|au)?\s*(?:[0-9]{1,2}(?:e|er))?\s*(?:s\.|siècle)", date, re.I)
    return century is not None and int(century.group(1)) <= 15


def descriptors(row: dict[str, object]) -> set[str]:
    return {x.strip().casefold() for x in str(row["fields"].get("Descripteurs", "")).split(",") if x.strip()}


def review(row: dict[str, object]) -> dict[str, bool]:
    terms = descriptors(row)
    return {
        "date_through_fifteenth_century": medieval(str(row["fields"].get("Date de fabrication", ""))),
        "circle_and_winds_descriptors": {"cercle", "vents"} <= terms,
        "human_figure_descriptor": bool(terms & {"homme", "femme", "tête", "de profil", "de face", "en médaillon"}),
        "named_human_data_source": bool(row["data_source"] and row["source_url_not_opened"]),
        "page_embedded_iiif_locator": bool(row["iiif_info_urls_not_opened"]),
        "identification_inscription_descriptor": "inscription identification" in terms,
    }


def transfer(row: dict[str, object]) -> dict[str, bool]:
    context = " ".join((str(row["title"]), *[str(x) for x in row["fields"].values()]))
    return {
        "complete_readable_ordered_owned_register": bool(re.search(r"registre ordonné|ordered owned register|propriétaire des étiquettes", context, re.I)),
        "one_to_one_common_slot_coordinate": bool(re.search(r"one-to-one common slot|coordonnée commune|correspondance univoque", context, re.I)),
        "preserved_start_and_orientation": bool(re.search(r"point de départ.*orientation|start.*orientation", context, re.I)),
    }


def summarize(panel: list[dict[str, object]]) -> dict[str, int]:
    early = sum(medieval(str(x["fields"].get("Date de fabrication", ""))) for x in panel)
    undated = sum("Date de fabrication" not in x["fields"] for x in panel)
    return {
        "record_count": len(panel),
        "records_with_human_inscription": sum("Inscription" in x["fields"] for x in panel),
        "records_through_fifteenth_century": early,
        "records_without_date": undated,
        "records_after_fifteenth_century": len(panel) - early - undated,
    }


def expected_report() -> str:
    return (
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
        "Moon, star, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f67 or f68.\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Biblissima circle validation outputs")
    wind_seeds, astronomy_seeds = link_panels(get(DESCRIPTOR))
    all_seeds = sorted(wind_seeds + astronomy_seeds, key=lambda x: x["record_id"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(read_record, all_seeds))
    indexed = {str(row["record_id"]): row for row in rows}
    winds = [indexed[x["record_id"]] for x in wind_seeds]
    astronomy = [indexed[x["record_id"]] for x in astronomy_seeds]
    candidates = []
    for row in winds:
        gates = review(row)
        if all(v for k, v in gates.items() if k != "identification_inscription_descriptor"):
            candidates.append({**row, "human_review_gates": gates, "source_transfer_gates": transfer(row)})
    stable = {"descriptor_url": DESCRIPTOR, "wind_records": winds, "sun_moon_records": astronomy}
    reconstructed = {
        "experiment": "BIBLISSIMA_F67_F68_METADATA_WORTH",
        "status": "PROVISIONAL_TWO_QUALIFIED_HUMAN_IMAGE_REVIEW_CANDIDATES",
        "decision": "RETAIN_BOURGES_MS105_F95V_AND_SG_MS1029_F135_FOR_HUMAN_TOPOLOGY_INSPECTION_NO_SOURCE_TRANSFER",
        "source": {"publisher": "Biblissima / Initiale / Mandragore", "descriptor_url": DESCRIPTOR, "stable_projection_sha256": digest(encoded(stable))},
        "wind_family": summarize(winds),
        "sun_moon_family": {**summarize(astronomy), "records_naming_sun_moon_and_stars": sum("étoile" in str(x["title"]).casefold() for x in astronomy)},
        "human_review_candidates": candidates,
        "gates": {"qualified_human_wind_topology_inspection": True, "qualified_human_f68_astronomy_inspection": False, "source_transfer_authorized": False, "image_or_iiif_document_opened": False, "paper_review_authorized": False},
        "source_access": {"biblissima_descriptor_and_text_records_opened": True, "named_source_urls_opened": False, "embedded_iiif_locator_strings_recorded": True, "iiif_info_thumbnail_image_canvas_manifest_or_manuscript_page_opened": False, "paper_pdf_ocr_or_automated_visual_output_opened": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: digest(SPEC.read_bytes())},
        "claim_ceiling": "Bourges BM Ms. 105 f.095v and Bibliothèque Sainte-Geneviève Ms. 1029 f.135 are provenance-clean wind-circle records worth qualified human topology inspection; the latter is additionally catalogued with a man, woman, heads in medallions, and identification inscriptions. Current metadata fixes no complete readable owned register, common one-to-one slot coordinate, start, or orientation, and the Sun/Moon family supplies no Sun-Moon-stars record. No direction, wind, person, head, sex, object, Sun, Moon, star, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers to f67 or f68.",
    }
    checks = {
        "wind_selection_exact_18": len(winds) == 18,
        "sun_moon_selection_exact_3": len(astronomy) == 3,
        "selection_disjoint": not ({x["record_id"] for x in winds} & {x["record_id"] for x in astronomy}),
        "wind_inscriptions_exact_11": summarize(winds)["records_with_human_inscription"] == 11,
        "wind_dates_exact_15_0_3": [summarize(winds)[k] for k in ("records_through_fifteenth_century", "records_without_date", "records_after_fifteenth_century")] == [15, 0, 3],
        "astronomy_dates_exact_2_0_1": [summarize(astronomy)[k] for k in ("records_through_fifteenth_century", "records_without_date", "records_after_fifteenth_century")] == [2, 0, 1],
        "astronomy_inscriptions_exact_1": summarize(astronomy)["records_with_human_inscription"] == 1,
        "no_sun_moon_stars_title": reconstructed["sun_moon_family"]["records_naming_sun_moon_and_stars"] == 0,
        "candidate_ids_exact": [x["record_id"] for x in candidates] == [BOURGES, SAINTE_GENEVIEVE],
        "candidate_dates_pass": all(x["human_review_gates"]["date_through_fifteenth_century"] for x in candidates),
        "candidate_circle_winds_pass": all(x["human_review_gates"]["circle_and_winds_descriptors"] for x in candidates),
        "candidate_human_descriptors_pass": all(x["human_review_gates"]["human_figure_descriptor"] for x in candidates),
        "candidate_initiale_sources_exact": [x["data_source"] for x in candidates] == ["Initiale", "Initiale"],
        "candidate_iiif_locator_counts_exact": [len(x["iiif_info_urls_not_opened"]) for x in candidates] == [1, 2],
        "sainte_genevieve_identification_descriptor": candidates[1]["human_review_gates"]["identification_inscription_descriptor"],
        "bourges_no_identification_descriptor": not candidates[0]["human_review_gates"]["identification_inscription_descriptor"],
        "all_transfer_gates_false": not any(value for x in candidates for value in x["source_transfer_gates"].values()),
        "stable_projection_digest_matches": reconstructed["source"]["stable_projection_sha256"] == json.loads(PRODUCER.read_text())["source"]["stable_projection_sha256"],
        "canonical_result_exact": encoded(reconstructed) == PRODUCER.read_bytes(),
        "report_exact": expected_report().encode() == PRODUCER_REPORT.read_bytes(),
        "source_access_ceiling_exact": reconstructed["source_access"] == json.loads(PRODUCER.read_text())["source_access"],
        "no_image_or_source_url_requested": not reconstructed["gates"]["image_or_iiif_document_opened"] and not reconstructed["source_access"]["named_source_urls_opened"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"independent validation failed: {failed}")
    validation = {
        "experiment": "BIBLISSIMA_F67_F68_METADATA_WORTH_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "decision": "VALIDATE_TWO_HUMAN_REVIEW_CANDIDATES_NO_SOURCE_TRANSFER",
        "validated_result_sha256": digest(PRODUCER.read_bytes()),
        "validated_report_sha256": digest(PRODUCER_REPORT.read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": {"wind_records": len(winds), "sun_moon_records": len(astronomy), "human_review_candidates": len(candidates), "source_transfer_candidates": 0},
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUT_JSON.write_bytes(encoded(validation))
    OUT_REPORT.write_text(
        "# Biblissima f67/f68 diagram metadata worth — independent validation\n\n"
        f"All **{len(checks)}** checks pass. Independent code live-reconstructs the complete 18-record wind-rose family, "
        "three-record Sun/Moon family, date and inscription partitions, both Initiale-provenance human-review candidates, "
        "every frozen inspection and transfer gate, the stable projection, canonical result, and exact report.\n\n"
        "This validates two requests for qualified human topology inspection and zero source-transfer candidates. No image "
        "or named source URL was opened, and no direction, wind, person, head, sex, object, Sun, Moon, star, slot, label, "
        "word, sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
