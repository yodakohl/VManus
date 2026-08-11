#!/usr/bin/env python3
"""Independent live validation of the Haruna manuscript-K clarification."""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RES = BASE / "results"
SPEC = BASE / "HARUNA_2011_K45V_SOURCE_CLARIFICATION_SPEC.md"
PRIOR = RES / "haruna_2011_f67v2_twelve_wind_busts.json"
PRODUCTION = RES / "haruna_2011_k45v_source_clarification.json"
PRODUCTION_REPORT = RES / "haruna_2011_k45v_source_clarification_report.md"
OUT = RES / "haruna_2011_k45v_source_clarification_validation.json"
OUT_REPORT = RES / "haruna_2011_k45v_source_clarification_validation_report.md"
PAPER = "https://www.societearcheologiquedumidi.fr/_samf/memoires/t_71/83-125_Haruna.pdf"
OCCITANICA = "https://www.occitanica.eu/items/show/12177"
BL = "https://www.bl.uk/files/v5dwkion/production/f66693975b985b9dbc61bf8385ecf40f3da1cd08.pdf/digitised-manuscripts.pdf?dl="


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def get(url: str, expected: bytes) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-K45v-independent/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get_all("Location"):
            raise RuntimeError("source response drift")
        data = response.read()
    if expected not in data:
        raise RuntimeError("source body signature absent")
    return data


def extract_pdf(data: bytes) -> str:
    run = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if run.stderr:
        raise RuntimeError("text-layer extraction diagnostic")
    return run.stdout.decode("utf-8")


def compact(value: str) -> str:
    return " ".join(value.split())


def visible_html(data: bytes) -> str:
    markup = data.decode("utf-8")
    return compact(html.unescape(re.sub(r"<[^>]*>", " ", markup)))


def expected_report() -> str:
    return (
        "# Haruna 2011 manuscript-K f45v source clarification\n\n"
        "Decision: **STOP_K45V_ART_HOMOLOGUE_NO_SHARED_INSCRIPTION_OR_SLOT_MAP**.\n\n"
        "The source prescreen resolves `K` as British Library Harley MS 4940, a complete fourteenth-century "
        "*Breviari d'amor* witness. The British Library independently describes it as Matfre Ermengaud's work, "
        "mid-fourteenth century, in French and Old Occitan.\n\n"
        "`Illustration n° 29` is the Breviari illustration inventory item after verse 6112, `La rose des vents`; "
        "it is not a displayed figure 29 in Haruna's paper, whose figure captions stop at 22. Footnote 138 locates "
        "that inventory item at K f45v.\n\n"
        "The comparison is explicitly art-historical rather than inscription-identical: the paper says that details "
        "explained by inscriptions differ between the two authors, while similar pictorial ideas are used. Therefore "
        "Sainte-Geneviève's four central cardinal names cannot be copied onto K, and neither source supplies a shared "
        "individual bust/name map, four-by-three placement, start, orientation, or f67v2 slot coordinate.\n\n"
        "Only public human catalogue prose and embedded PDF text layers were read. No figure or manuscript image was "
        "rendered or inspected; no OCR, automated vision, or decoder claim was used. No wind, direction, inscription, "
        "bust, face, slot, label, word, sound, language, cipher, plaintext, meaning, or translation transfers.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite K45v validation outputs")
    paper_body = get(PAPER, b"%PDF-")
    occitanica_body = get(OCCITANICA, b"Harley 4940")
    bl_body = get(BL, b"%PDF-")
    paper_raw = extract_pdf(paper_body)
    paper_text = compact(paper_raw)
    occitanica_text = visible_html(occitanica_body)
    bl_text = compact(extract_pdf(bl_body))
    caption_numbers = sorted({int(item) for item in re.findall(r"\bF[iI]G\.\s*(\d+)", paper_raw)})
    checks_source = {
        "occitanica_K_is_Harley_4940": "K – Londres, British Museum, Harley 4940." in occitanica_text,
        "occitanica_K_complete_fourteenth_century": "Languedoc. XIV e siècle. Le texte complet." in occitanica_text,
        "bl_Harley_4940_title": "Harley MS 4940 Matfre Ermengaud, Breviari d'amor" in bl_text,
        "bl_mid_fourteenth_century": "Harley MS 4940 Matfre Ermengaud, Breviari d'amor Mid 14th French; century" in bl_text,
        "bl_languages_french_old_occitan": "French; century Occitan, Old" in bl_text,
        "paper_K_identity": "Le manuscrit K (Londres, British Library, ms. Harley 4940)" in paper_text,
        "paper_internal_item_29_after_verse_6112": "29. (après le v. 6112) La rose des vents" in paper_text,
        "paper_K_f45v_locator": "dans K, f. 45v (illustration n° 29, la rose des vents)" in paper_text,
        "paper_inscription_details_differ": "les détails expliqués par les inscriptions dans les diagrammes diffèrent selon les auteurs des deux ouvrages" in paper_text,
        "paper_similar_pictorial_ideas": "des idées picturales similaires sont utilisées dans les deux manuscrits" in paper_text,
        "paper_displayed_figures_stop_at_22": caption_numbers and max(caption_numbers) == 22,
    }
    prior = json.loads(PRIOR.read_text())
    projection = {
        "manuscript_siglum": "K",
        "shelfmark": "Harley MS 4940",
        "folio": "f. 45v",
        "work": "Matfre Ermengaud, Breviari d'amor",
        "date": "mid-14th century",
        "languages": ["French", "Occitan, Old"],
        "internal_illustration_number": 29,
        "internal_illustration_title": "La rose des vents",
        "inventory_position": "after verse 6112",
        "paper_max_displayed_figure_number": max(caption_numbers),
        "comparison_scope": "similar pictorial ideas; inscription-explained details differ by author",
    }
    transfer = {
        "shared_inscription_set_stated": False,
        "individual_bust_to_name_ownership_stated": False,
        "four_sectors_of_three_busts_stated": False,
        "common_visual_start_or_orientation_stated": False,
        "common_owned_f67v2_slot_coordinate": False,
    }
    reconstructed = {
        "experiment": "HARUNA_2011_K45V_SOURCE_CLARIFICATION",
        "status": "PASS_K_IDENTIFIED_INTERNAL_ILLUSTRATION_NUMBER_CLARIFIED",
        "decision": "STOP_K45V_ART_HOMOLOGUE_NO_SHARED_INSCRIPTION_OR_SLOT_MAP",
        "source_checks": checks_source,
        "source_projection": projection,
        "transfer_gates": transfer,
        "gates": {
            "paper_worth_screen_passed_before_initial_open": prior["gates"]["paper_worth_gate_passed_before_opening"],
            "source_clarification_material": True,
            "additional_paper_or_image_review_worthwhile": False,
            "f67v2_source_transfer_authorized": False,
        },
        "source_access": {
            "human_catalogue_text_opened": True,
            "embedded_human_pdf_text_opened": True,
            "paper_figure_or_manuscript_image_rendered_or_inspected": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claim_opened": False,
        },
        "sources": {
            "paper": {"url": PAPER, "sha256": digest(paper_body)},
            "occitanica": {"url": OCCITANICA, "sha256": digest(occitanica_body)},
            "british_library_list": {"url": BL, "sha256": digest(bl_body)},
            "projection_sha256": digest(encoded({"source_checks": checks_source, "source_projection": projection})),
        },
        "inputs": {SPEC.name: digest(SPEC.read_bytes()), f"results/{PRIOR.name}": digest(PRIOR.read_bytes())},
        "claim_ceiling": "Haruna's K is British Library Harley MS 4940 f45v, and illustration 29 is the Breviari's internal wind-rose inventory item rather than a displayed paper figure. The paper compares pictorial ideas while stating that inscription-explained details differ by author. This supplies no shared inscription set, bust/name ownership, four-by-three placement, start, orientation, f67v2 slot map, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    production = json.loads(PRODUCTION.read_text())
    checks = {
        "all_live_source_checks": all(checks_source.values()),
        "paper_body_hash_exact": reconstructed["sources"]["paper"]["sha256"] == production["sources"]["paper"]["sha256"],
        "occitanica_body_hash_exact": reconstructed["sources"]["occitanica"]["sha256"] == production["sources"]["occitanica"]["sha256"],
        "bl_body_hash_exact": reconstructed["sources"]["british_library_list"]["sha256"] == production["sources"]["british_library_list"]["sha256"],
        "K_identity_exact": projection["shelfmark"] == "Harley MS 4940" and projection["folio"] == "f. 45v",
        "internal_illustration_number_exact": projection["internal_illustration_number"] == 29,
        "paper_caption_max_exact": projection["paper_max_displayed_figure_number"] == 22,
        "inscription_difference_explicit": checks_source["paper_inscription_details_differ"],
        "pictorial_similarity_explicit": checks_source["paper_similar_pictorial_ideas"],
        "all_transfer_gates_false": not any(transfer.values()),
        "no_image_ocr_or_decoder_claim": not any([reconstructed["source_access"]["paper_figure_or_manuscript_image_rendered_or_inspected"], reconstructed["source_access"]["ocr_or_automated_visual_output_used"], reconstructed["source_access"]["decoder_claim_opened"]]),
        "projection_digest_exact": reconstructed["sources"]["projection_sha256"] == production["sources"]["projection_sha256"],
        "canonical_result_exact": encoded(reconstructed) == PRODUCTION.read_bytes(),
        "report_exact": expected_report().encode() == PRODUCTION_REPORT.read_bytes(),
        "claim_ceiling_exact": reconstructed["claim_ceiling"] == production["claim_ceiling"],
    }
    failed = [key for key, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"independent K45v validation failed: {failed}")
    result = {
        "experiment": "HARUNA_2011_K45V_SOURCE_CLARIFICATION_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_TEXT_RECONSTRUCTION",
        "decision": "VALIDATE_K45V_ART_HOMOLOGUE_STOP_NO_SHARED_INSCRIPTION_OR_SLOT_MAP",
        "validated_result_sha256": digest(PRODUCTION.read_bytes()),
        "validated_report_sha256": digest(PRODUCTION_REPORT.read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": {"logical_sources": 3, "source_checks": len(checks_source), "displayed_paper_figures": max(caption_numbers), "transfer_gates_passing": sum(transfer.values())},
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUT.write_bytes(encoded(result))
    OUT_REPORT.write_text(
        "# Haruna 2011 manuscript-K f45v clarification — independent validation\n\n"
        f"All **{len(checks)}** checks pass. Independent code refetches the article-only human text layer, Occitanica "
        "catalogue, and British Library list; it reconstructs K's identity, the internal illustration-29 distinction, "
        "the explicit inscription-difference statement, every gate, canonical result, and report.\n\n"
        "The result stops at an art-historical homologue with no shared inscription or target slot map. No figure or "
        "manuscript image, OCR, automated vision, decoder claim, word, plaintext, meaning, or translation is admitted.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
