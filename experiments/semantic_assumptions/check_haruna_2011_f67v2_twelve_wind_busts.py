#!/usr/bin/env python3
"""Text-layer-only source check for the Sainte-Geneviève wind diagram."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SPEC = ROOT / "HARUNA_2011_F67V2_TWELVE_WIND_BUSTS_SPEC.md"
INITIALE = RESULTS / "initiale_f67v2_cardinal_wind_ownership.json"
TARGET = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
PDF_URL = "https://www.societearcheologiquedumidi.fr/_samf/memoires/t_71/MSAMF_LXXI_2011.pdf"
OUT_JSON = RESULTS / "haruna_2011_f67v2_twelve_wind_busts.json"
OUT_REPORT = RESULTS / "haruna_2011_f67v2_twelve_wind_busts_report.md"
TWELVE_PHRASE = "les douze vents personnifiés en buste et rangés en cercle"
LOCATOR_PHRASE = "Paris, Bibliothèque Sainte-Geneviève, ms. 1029, f. 135ra ; dans K, f. 45v (illustration n° 29, la rose des vents)."


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def fetch_pdf() -> bytes:
    request = urllib.request.Request(PDF_URL, method="GET", headers={"User-Agent": "VManus-Haruna-source-check/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200 or response.geturl() != PDF_URL or response.headers.get_all("Location"):
            raise ValueError("unexpected Haruna PDF response")
        body = response.read()
    if not body.startswith(b"%PDF-") or len(body) < 1_000_000:
        raise ValueError("incomplete Haruna PDF")
    return body


def text_layer(pdf: bytes) -> str:
    run = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if run.stderr:
        raise ValueError("unexpected pdftotext diagnostic")
    return run.stdout.decode("utf-8")


def normalized(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Haruna source-check outputs")
    pdf = fetch_pdf()
    text = text_layer(pdf)
    flat = normalized(text)
    phrase_checks = {
        "article_title": "La culture picturale du Breviari d’amor de Matfre Ermengaud dans les enluminures toulousaines du XIVe siècle" in flat,
        "twelve_personified_winds_in_busts_and_circle": TWELVE_PHRASE in flat,
        "exact_sainte_genevieve_f135ra_locator": "Paris, Bibliothèque Sainte-Geneviève, ms. 1029, f. 135ra" in flat,
        "brevari_K_f45v_illustration_29_locator": "dans K, f. 45v (illustration n° 29, la rose des vents)" in flat,
        "similar_pictorial_ideas_statement": "des idées picturales similaires sont utilisées dans les deux manuscrits" in flat,
    }
    if not all(phrase_checks.values()):
        raise ValueError(f"Haruna text-layer drift: {phrase_checks}")
    initiale = json.loads(INITIALE.read_text())
    target = json.loads(TARGET.read_text())
    initiale_projection = {
        "four_cardinal_winds": initiale["source_gates"]["exactly_four_cardinal_winds_stated"],
        "crowned_personification": initiale["source_gates"]["crowned_personification_stated"],
        "central_circle_collective_names": initiale["source_gates"]["central_circle_collective_name_ownership_stated"],
        "published_name_strings": initiale["projected_cardinal_names_in_catalogue_order_not_visual_order"],
        "individual_name_to_figure_position_map": initiale["source_gates"]["individual_name_to_figure_position_map_stated"],
    }
    target_projection = {
        "four_corner_face_groups": target["gates"]["f67v2_has_four_corner_face_groups"],
        "each_group_exactly_three_faces": target["gates"]["f67v2_each_group_has_exactly_three_faces"],
        "text_loci": target["counts"]["f67v2_text_loci"],
        "radial_loci": target["counts"]["f67v2_radial_loci"],
        "label_loci": target["counts"]["f67v2_label_loci"],
        "owned_twelve_slot_register": target["gates"]["f67v2_has_owned_twelve_slot_text_register"],
    }
    if initiale_projection != {"four_cardinal_winds": True, "crowned_personification": True, "central_circle_collective_names": True, "published_name_strings": ["oriente", "occidente", "miechiorn", "aquilo"], "individual_name_to_figure_position_map": False}:
        raise ValueError("Initiale projection drift")
    if target_projection != {"four_corner_face_groups": True, "each_group_exactly_three_faces": False, "text_loci": 22, "radial_loci": 8, "label_loci": 6, "owned_twelve_slot_register": False}:
        raise ValueError("f67v2 projection drift")
    source_gates = {
        "twelve_winds_personified_as_busts": True,
        "twelve_busts_arranged_in_circle": True,
        "exact_manuscript_folio_locator": True,
        "four_cardinal_name_register_from_independent_initiale_notice": True,
        "four_sectors_of_three_busts_stated": False,
        "individual_bust_name_ownership_stated": False,
        "visual_start_or_orientation_stated": False,
    }
    transfer_gates = {
        "exact_source_target_unit_topology": False,
        "one_owned_target_text_locus_per_source_bust": False,
        "one_to_one_source_name_target_locus_map": False,
        "common_start_and_orientation": False,
    }
    evidence = {"phrase_checks": phrase_checks, "initiale_projection": initiale_projection, "target_projection": target_projection}
    result = {
        "experiment": "HARUNA_2011_F67V2_TWELVE_WIND_BUSTS",
        "status": "PASS_HUMAN_TEXT_TWELVE_PERSONIFIED_WINDS_IN_CIRCLE_NO_F67V2_TRANSFER",
        "decision": "RETAIN_12_BUSTS_PLUS_4_CARDINAL_NAMES_SYSTEM_PRIOR_STOP_NO_SLOT_MAP",
        "source": {"author": "Hiromi Haruna-Czaplicki", "title": "La culture picturale du Breviari d’amor de Matfre Ermengaud dans les enluminures toulousaines du XIVe siècle", "journal": "Mémoires de la Société Archéologique du Midi de la France", "volume_year_pages": "71 (2011), 83-125", "pdf_url": PDF_URL, "pdf_sha256": sha(pdf), "evidence_projection_sha256": sha(canonical(evidence))},
        "paper_phrase_checks": phrase_checks,
        "paper_projection": {"manuscript": "Paris, Bibliothèque Sainte-Geneviève, ms. 1029", "folio": "f. 135ra", "topology": TWELVE_PHRASE, "related_manuscript_locator": "K, f. 45v", "related_illustration": "n° 29, la rose des vents"},
        "initiale_projection": initiale_projection,
        "target_projection": target_projection,
        "source_gates": source_gates,
        "transfer_gates": transfer_gates,
        "gates": {"paper_worth_gate_passed_before_opening": True, "human_text_supplies_twelve_bust_circle_topology": True, "qualified_human_image_inspection_still_worthwhile": True, "f67v2_source_transfer_authorized": False, "paper_figures_or_manuscript_images_opened": False},
        "source_access": {"public_pdf_opened": True, "embedded_human_text_layer_extracted": True, "pdf_pages_or_figures_rendered_or_inspected": False, "ocr_or_automated_visual_output_used": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: sha(SPEC.read_bytes()), f"results/{INITIALE.name}": sha(INITIALE.read_bytes()), f"results/{TARGET.name}": sha(TARGET.read_bytes())},
        "claim_ceiling": "Haruna-Czaplicki identifies Sainte-Geneviève ms. 1029 f.135ra as twelve winds personified as busts and arranged in a circle; Initiale independently supplies four crowned cardinal winds and four central-circle name strings. This strengthens a 12-personified-winds plus 4-cardinal-names source-family prior, but supplies no four-by-three placement, bust/name ownership, target slot map, start, or orientation. No wind, direction, bust, crown, person, sex, face, slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
        "# Haruna-Czaplicki 2011 f67v2 twelve-wind-bust source check\n\n"
        "Decision: **RETAIN_12_BUSTS_PLUS_4_CARDINAL_NAMES_SYSTEM_PRIOR_STOP_NO_SLOT_MAP**.\n\n"
        "A prescreen admitted this paper because its index names the exact retained page, Sainte-Geneviève ms. 1029 "
        "f.135ra, as illustration 29. The embedded human text then supplies the material topology statement: `les douze "
        "vents personnifiés en buste et rangés en cercle`. Footnote 138 locates the page and compares it with manuscript "
        "K f.45v, `illustration n° 29, la rose des vents`.\n\n"
        "Combined with Initiale's independent note, the historical source now has a defensible `12 personified winds in a "
        "circle + 4 crowned cardinal names in the central circle` description. The paper does not state four sectors of "
        "three busts, individual bust/name ownership, a visual start, or orientation.\n\n"
        "This remains non-transferable to f67v2. The target has four corner groups with a nonuniform three-/four-face "
        "inventory and 22 competing text loci—eight floating, eight radial, and six labels—with no owned twelve-slot "
        "register. Shared number twelve, wind personification, or four cardinal names cannot choose a Voynich locus.\n\n"
        "Only the embedded human PDF text layer was read. No paper figure, PDF page image, manuscript image, screenshot, "
        "OCR, automated visual output, or decoder claim was opened. No wind, direction, bust, crown, person, sex, face, "
        "slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
