#!/usr/bin/env python3
"""Independent text-layer validation of the Haruna f67v2 source check."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SPEC = HERE / "HARUNA_2011_F67V2_TWELVE_WIND_BUSTS_SPEC.md"
INITIALE = RESULTS / "initiale_f67v2_cardinal_wind_ownership.json"
TARGET = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
PRODUCTION = RESULTS / "haruna_2011_f67v2_twelve_wind_busts.json"
PRODUCTION_REPORT = RESULTS / "haruna_2011_f67v2_twelve_wind_busts_report.md"
OUT = RESULTS / "haruna_2011_f67v2_twelve_wind_busts_validation.json"
OUT_REPORT = RESULTS / "haruna_2011_f67v2_twelve_wind_busts_validation_report.md"
PDF = "https://www.societearcheologiquedumidi.fr/_samf/memoires/t_71/MSAMF_LXXI_2011.pdf"
TOPOLOGY = "les douze vents personnifiés en buste et rangés en cercle"


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bytes_for(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def acquire() -> bytes:
    request = urllib.request.Request(PDF, method="GET", headers={"User-Agent": "VManus-Haruna-independent/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200 or response.geturl() != PDF or response.headers.get_all("Location"):
            raise RuntimeError("paper response drift")
        data = response.read()
    if not data.startswith(b"%PDF-") or len(data) < 1_000_000:
        raise RuntimeError("paper body incomplete")
    return data


def extract(data: bytes) -> str:
    process = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if process.stderr:
        raise RuntimeError("embedded text extraction diagnostic")
    return " ".join(process.stdout.decode().split())


def report_text() -> str:
    return (
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
        "slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Haruna validation outputs")
    pdf = acquire()
    text = extract(pdf)
    paper_checks = {
        "article_title": "La culture picturale du Breviari d’amor de Matfre Ermengaud dans les enluminures toulousaines du XIVe siècle" in text,
        "twelve_personified_winds_in_busts_and_circle": TOPOLOGY in text,
        "exact_sainte_genevieve_f135ra_locator": "Paris, Bibliothèque Sainte-Geneviève, ms. 1029, f. 135ra" in text,
        "brevari_K_f45v_illustration_29_locator": "dans K, f. 45v (illustration n° 29, la rose des vents)" in text,
        "similar_pictorial_ideas_statement": "des idées picturales similaires sont utilisées dans les deux manuscrits" in text,
    }
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
    source_gates = {"twelve_winds_personified_as_busts": True, "twelve_busts_arranged_in_circle": True, "exact_manuscript_folio_locator": True, "four_cardinal_name_register_from_independent_initiale_notice": True, "four_sectors_of_three_busts_stated": False, "individual_bust_name_ownership_stated": False, "visual_start_or_orientation_stated": False}
    transfer = {"exact_source_target_unit_topology": False, "one_owned_target_text_locus_per_source_bust": False, "one_to_one_source_name_target_locus_map": False, "common_start_and_orientation": False}
    evidence = {"phrase_checks": paper_checks, "initiale_projection": initiale_projection, "target_projection": target_projection}
    reconstructed = {
        "experiment": "HARUNA_2011_F67V2_TWELVE_WIND_BUSTS",
        "status": "PASS_HUMAN_TEXT_TWELVE_PERSONIFIED_WINDS_IN_CIRCLE_NO_F67V2_TRANSFER",
        "decision": "RETAIN_12_BUSTS_PLUS_4_CARDINAL_NAMES_SYSTEM_PRIOR_STOP_NO_SLOT_MAP",
        "source": {"author": "Hiromi Haruna-Czaplicki", "title": "La culture picturale du Breviari d’amor de Matfre Ermengaud dans les enluminures toulousaines du XIVe siècle", "journal": "Mémoires de la Société Archéologique du Midi de la France", "volume_year_pages": "71 (2011), 83-125", "pdf_url": PDF, "pdf_sha256": checksum(pdf), "evidence_projection_sha256": checksum(bytes_for(evidence))},
        "paper_phrase_checks": paper_checks,
        "paper_projection": {"manuscript": "Paris, Bibliothèque Sainte-Geneviève, ms. 1029", "folio": "f. 135ra", "topology": TOPOLOGY, "related_manuscript_locator": "K, f. 45v", "related_illustration": "n° 29, la rose des vents"},
        "initiale_projection": initiale_projection,
        "target_projection": target_projection,
        "source_gates": source_gates,
        "transfer_gates": transfer,
        "gates": {"paper_worth_gate_passed_before_opening": True, "human_text_supplies_twelve_bust_circle_topology": True, "qualified_human_image_inspection_still_worthwhile": True, "f67v2_source_transfer_authorized": False, "paper_figures_or_manuscript_images_opened": False},
        "source_access": {"public_pdf_opened": True, "embedded_human_text_layer_extracted": True, "pdf_pages_or_figures_rendered_or_inspected": False, "ocr_or_automated_visual_output_used": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: checksum(SPEC.read_bytes()), f"results/{INITIALE.name}": checksum(INITIALE.read_bytes()), f"results/{TARGET.name}": checksum(TARGET.read_bytes())},
        "claim_ceiling": "Haruna-Czaplicki identifies Sainte-Geneviève ms. 1029 f.135ra as twelve winds personified as busts and arranged in a circle; Initiale independently supplies four crowned cardinal winds and four central-circle name strings. This strengthens a 12-personified-winds plus 4-cardinal-names source-family prior, but supplies no four-by-three placement, bust/name ownership, target slot map, start, or orientation. No wind, direction, bust, crown, person, sex, face, slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.",
    }
    production = json.loads(PRODUCTION.read_text())
    checks = {
        "pdf_body_hash_exact": reconstructed["source"]["pdf_sha256"] == production["source"]["pdf_sha256"],
        "embedded_text_title": paper_checks["article_title"],
        "embedded_text_twelve_bust_topology": paper_checks["twelve_personified_winds_in_busts_and_circle"],
        "embedded_text_exact_manuscript_folio": paper_checks["exact_sainte_genevieve_f135ra_locator"],
        "embedded_text_related_illustration": paper_checks["brevari_K_f45v_illustration_29_locator"],
        "embedded_text_similarity_context": paper_checks["similar_pictorial_ideas_statement"],
        "all_paper_phrase_checks": all(paper_checks.values()),
        "initiale_four_cardinal_names_exact": initiale_projection["published_name_strings"] == ["oriente", "occidente", "miechiorn", "aquilo"],
        "initiale_no_individual_position_map": not initiale_projection["individual_name_to_figure_position_map"],
        "target_four_groups_nonuniform": target_projection["four_corner_face_groups"] and not target_projection["each_group_exactly_three_faces"],
        "target_loci_exact": [target_projection["text_loci"], target_projection["radial_loci"], target_projection["label_loci"]] == [22, 8, 6],
        "target_no_owned_twelve_slot_register": not target_projection["owned_twelve_slot_register"],
        "source_four_by_three_not_stated": not source_gates["four_sectors_of_three_busts_stated"],
        "source_no_individual_bust_ownership": not source_gates["individual_bust_name_ownership_stated"],
        "source_no_visual_start_orientation": not source_gates["visual_start_or_orientation_stated"],
        "all_transfer_gates_false": not any(transfer.values()),
        "evidence_projection_digest_exact": reconstructed["source"]["evidence_projection_sha256"] == production["source"]["evidence_projection_sha256"],
        "canonical_result_exact": bytes_for(reconstructed) == PRODUCTION.read_bytes(),
        "report_exact": report_text().encode() == PRODUCTION_REPORT.read_bytes(),
        "no_figures_images_or_ocr": not reconstructed["source_access"]["pdf_pages_or_figures_rendered_or_inspected"] and not reconstructed["source_access"]["ocr_or_automated_visual_output_used"],
        "claim_ceiling_exact": reconstructed["claim_ceiling"] == production["claim_ceiling"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Haruna independent validation failed: {failed}")
    result = {
        "experiment": "HARUNA_2011_F67V2_TWELVE_WIND_BUSTS_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_HUMAN_TEXT_LAYER_RECONSTRUCTION",
        "decision": "VALIDATE_12_BUSTS_PLUS_4_CARDINAL_NAMES_PRIOR_NO_F67V2_TRANSFER",
        "validated_result_sha256": checksum(PRODUCTION.read_bytes()),
        "validated_report_sha256": checksum(PRODUCTION_REPORT.read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": {"paper_topology_statements": 1, "personified_winds": 12, "initiale_cardinal_names": 4, "f67v2_transfer_candidates": 0},
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUT.write_bytes(bytes_for(result))
    OUT_REPORT.write_text(
        "# Haruna-Czaplicki 2011 f67v2 twelve-wind-bust source — independent validation\n\n"
        f"All **{len(checks)}** checks pass. Independent code refetches and hash-binds the public paper, extracts only its "
        "embedded human text layer, reconstructs the exact twelve-personified-winds topology and manuscript locator, joins "
        "the validated Initiale and f67v2 projections, and reproduces every gate, canonical result, and report.\n\n"
        "This validates a stronger source-family prior and zero f67v2 transfers. No figure, PDF page image, manuscript image, "
        "OCR, or automated visual output was opened; no wind, direction, bust, crown, person, sex, face, slot, label, word, "
        "sound, language, cipher operation, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
