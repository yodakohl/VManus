#!/usr/bin/env python3
"""Clarify Haruna's manuscript K and the scope of its f45v comparison."""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SPEC = HERE / "HARUNA_2011_K45V_SOURCE_CLARIFICATION_SPEC.md"
PRIOR = RESULTS / "haruna_2011_f67v2_twelve_wind_busts.json"
OUT = RESULTS / "haruna_2011_k45v_source_clarification.json"
REPORT = RESULTS / "haruna_2011_k45v_source_clarification_report.md"

PAPER_URL = "https://www.societearcheologiquedumidi.fr/_samf/memoires/t_71/83-125_Haruna.pdf"
OCCITANICA_URL = "https://www.occitanica.eu/items/show/12177"
BL_URL = "https://www.bl.uk/files/v5dwkion/production/f66693975b985b9dbc61bf8385ecf40f3da1cd08.pdf/digitised-manuscripts.pdf?dl="


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def fetch(url: str, kind: str) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-K45v-source-clarification/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get_all("Location"):
            raise ValueError(f"unexpected {kind} response")
        body = response.read()
    if kind == "html" and b"Harley 4940" not in body:
        raise ValueError("Occitanica body incomplete")
    if kind == "pdf" and (not body.startswith(b"%PDF-") or len(body) < 100_000):
        raise ValueError(f"{kind} body incomplete")
    return body


def pdf_text(body: bytes) -> str:
    run = subprocess.run(["pdftotext", "-layout", "-", "-"], input=body, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if run.stderr:
        raise ValueError("unexpected pdftotext diagnostic")
    return run.stdout.decode("utf-8")


def flat_text(value: str) -> str:
    return " ".join(value.split())


def html_text(body: bytes) -> str:
    decoded = body.decode("utf-8")
    without_tags = re.sub(r"<[^>]+>", " ", decoded)
    return flat_text(html.unescape(without_tags))


def report_text() -> str:
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
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite K45v clarification outputs")
    paper = fetch(PAPER_URL, "pdf")
    occitanica = fetch(OCCITANICA_URL, "html")
    bl = fetch(BL_URL, "pdf")
    paper_text = pdf_text(paper)
    paper_flat = flat_text(paper_text)
    occitanica_flat = html_text(occitanica)
    bl_flat = flat_text(pdf_text(bl))
    displayed_figures = sorted({int(value) for value in re.findall(r"\bF[iI]G\.\s*(\d+)", paper_text)})
    source_checks = {
        "occitanica_K_is_Harley_4940": "K – Londres, British Museum, Harley 4940." in occitanica_flat,
        "occitanica_K_complete_fourteenth_century": "Languedoc. XIV e siècle. Le texte complet." in occitanica_flat,
        "bl_Harley_4940_title": "Harley MS 4940 Matfre Ermengaud, Breviari d'amor" in bl_flat,
        "bl_mid_fourteenth_century": "Harley MS 4940 Matfre Ermengaud, Breviari d'amor Mid 14th French; century" in bl_flat,
        "bl_languages_french_old_occitan": "French; century Occitan, Old" in bl_flat,
        "paper_K_identity": "Le manuscrit K (Londres, British Library, ms. Harley 4940)" in paper_flat,
        "paper_internal_item_29_after_verse_6112": "29. (après le v. 6112) La rose des vents" in paper_flat,
        "paper_K_f45v_locator": "dans K, f. 45v (illustration n° 29, la rose des vents)" in paper_flat,
        "paper_inscription_details_differ": "les détails expliqués par les inscriptions dans les diagrammes diffèrent selon les auteurs des deux ouvrages" in paper_flat,
        "paper_similar_pictorial_ideas": "des idées picturales similaires sont utilisées dans les deux manuscrits" in paper_flat,
        "paper_displayed_figures_stop_at_22": displayed_figures and max(displayed_figures) == 22,
    }
    if not all(source_checks.values()):
        raise ValueError(f"source clarification drift: {source_checks}")
    prior = json.loads(PRIOR.read_text())
    if prior["paper_projection"]["related_manuscript_locator"] != "K, f. 45v":
        raise ValueError("prior K locator drift")
    transfer_gates = {
        "shared_inscription_set_stated": False,
        "individual_bust_to_name_ownership_stated": False,
        "four_sectors_of_three_busts_stated": False,
        "common_visual_start_or_orientation_stated": False,
        "common_owned_f67v2_slot_coordinate": False,
    }
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
        "paper_max_displayed_figure_number": max(displayed_figures),
        "comparison_scope": "similar pictorial ideas; inscription-explained details differ by author",
    }
    result = {
        "experiment": "HARUNA_2011_K45V_SOURCE_CLARIFICATION",
        "status": "PASS_K_IDENTIFIED_INTERNAL_ILLUSTRATION_NUMBER_CLARIFIED",
        "decision": "STOP_K45V_ART_HOMOLOGUE_NO_SHARED_INSCRIPTION_OR_SLOT_MAP",
        "source_checks": source_checks,
        "source_projection": projection,
        "transfer_gates": transfer_gates,
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
            "paper": {"url": PAPER_URL, "sha256": sha(paper)},
            "occitanica": {"url": OCCITANICA_URL, "sha256": sha(occitanica)},
            "british_library_list": {"url": BL_URL, "sha256": sha(bl)},
            "projection_sha256": sha(canonical({"source_checks": source_checks, "source_projection": projection})),
        },
        "inputs": {SPEC.name: sha(SPEC.read_bytes()), f"results/{PRIOR.name}": sha(PRIOR.read_bytes())},
        "claim_ceiling": "Haruna's K is British Library Harley MS 4940 f45v, and illustration 29 is the Breviari's internal wind-rose inventory item rather than a displayed paper figure. The paper compares pictorial ideas while stating that inscription-explained details differ by author. This supplies no shared inscription set, bust/name ownership, four-by-three placement, start, orientation, f67v2 slot map, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(report_text(), encoding="utf-8")


if __name__ == "__main__":
    main()
