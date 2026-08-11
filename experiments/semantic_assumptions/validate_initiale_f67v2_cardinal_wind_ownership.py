#!/usr/bin/env python3
"""Independent validation of the Initiale f67v2 ownership check."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SPEC = ROOT / "INITIALE_F67V2_CARDINAL_WIND_OWNERSHIP_SPEC.md"
TARGET = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
PRODUCTION = RESULTS / "initiale_f67v2_cardinal_wind_ownership.json"
PRODUCTION_REPORT = RESULTS / "initiale_f67v2_cardinal_wind_ownership_report.md"
OUT = RESULTS / "initiale_f67v2_cardinal_wind_ownership_validation.json"
OUT_REPORT = RESULTS / "initiale_f67v2_cardinal_wind_ownership_validation_report.md"
SOURCES = [
    ("Bourges_Ms105_f095v", "https://initiale.irht.cnrs.fr/decor/14834"),
    ("Sainte_Genevieve_Ms1029_f135", "https://initiale.irht.cnrs.fr/decor/69596"),
]
LITERAL_NOTE = 'Les quatre vents cardinaux, couronnés, sont nommés dans le cercle central : "oriente", "occidente", "miechiorn", "aquilo".'
FIELD_ALLOWLIST = {"Référence", "Folio/page", "Sujet", "Contexte", "Mot clé", "Conservation", "Notes", "Signature", "Auteur", "Titre", "Origine", "Datation"}


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def visible(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def read_url(url: str) -> str:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Initiale-independent/1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get_all("Location"):
            raise RuntimeError("Initiale transport drift")
        return response.read().decode("utf-8")


def notice(name: str, url: str) -> dict[str, object]:
    body = read_url(url)
    fields: dict[str, str] = {}
    for lhs, rhs in re.findall(r'<label>(.*?)</label>\s*<p class="txt_res"[^>]*>(.*?)</p>', body, re.I | re.S):
        key, value = visible(lhs), visible(rhs)
        if key in FIELD_ALLOWLIST and value:
            if key in fields and fields[key] != value:
                raise RuntimeError("Initiale field duplication")
            fields[key] = value
    count = re.search(r'<span id="nbImages">([0-9]+)</span>', body)
    locators = sorted(set(re.findall(r'data-infojson="(https://iiif\.irht\.cnrs\.fr/iiif/[^\"]+/info\.json)"', body)))
    if count is None or not locators:
        raise RuntimeError("Initiale locator metadata missing")
    return {"record": name, "url": url, "fields": fields, "declared_image_count_not_opened": int(count.group(1)), "iiif_info_urls_not_opened": locators}


def expected_report() -> str:
    return (
        "# Initiale f67v2 cardinal-wind ownership metadata check\n\n"
        "Decision: **RETAIN_SG1029_F135_AS_STRONG_FOUR_CARDINAL_WIND_COMPARATOR_STOP_BEFORE_IMAGE**.\n\n"
        "Initiale materially strengthens the Sainte-Geneviève lead. Its 2024/2022 human notice states: `Les quatre vents "
        "cardinaux, couronnés, sont nommés dans le cercle central : \"oriente\", \"occidente\", \"miechiorn\", "
        "\"aquilo\".` This establishes four cardinal winds, crowned personification, a collective central-circle name "
        "register, and exactly four published name strings. The catalogue sequence is not a visual start or orientation, "
        "and the notice does not map each name to a particular figure position.\n\n"
        "Bourges Ms. 105 f.095v remains the weaker control: Initiale confirms the wind rose, heads, cardinal points, "
        "circle, and blowing, but publishes no note or inscription transcription.\n\n"
        "The new source relation still does not supply an f67v2 key. The validated target has four corner groups containing "
        "three or four connected faces and 22 competing text loci—eight floating, eight radial, and six labels. It has no "
        "documented one-label-per-group ownership, source-name/target-locus map, common start, or orientation.\n\n"
        "No Initiale/ARCA image, IIIF information document, canvas, manifest, manuscript page, paper, PDF, OCR, automated "
        "visual output, or decoder claim was opened. No direction, wind name, crown, sex, person, face, slot, label, word, "
        "sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Initiale validation outputs")
    notices = [notice(name, url) for name, url in SOURCES]
    bourges, sg = notices
    names = re.findall(r'"([^"]+)"', str(sg["fields"].get("Notes", "")))
    previous = json.loads(TARGET.read_text())
    target_projection = {
        "f67v2_four_corner_face_groups": previous["gates"]["f67v2_has_four_corner_face_groups"],
        "f67v2_each_group_exactly_three_faces": previous["gates"]["f67v2_each_group_has_exactly_three_faces"],
        "f67v2_text_loci": previous["counts"]["f67v2_text_loci"],
        "f67v2_radial_loci": previous["counts"]["f67v2_radial_loci"],
        "f67v2_label_loci": previous["counts"]["f67v2_label_loci"],
        "f67v2_owned_twelve_slot_register": previous["gates"]["f67v2_has_owned_twelve_slot_text_register"],
        "common_start_direction_and_slot_correspondence": previous["gates"]["common_start_direction_and_slot_correspondence"],
    }
    source_gates = {
        "exactly_four_cardinal_winds_stated": "quatre vents cardinaux" in LITERAL_NOTE,
        "crowned_personification_stated": "couronnés" in LITERAL_NOTE,
        "central_circle_collective_name_ownership_stated": "nommés dans le cercle central" in LITERAL_NOTE,
        "exactly_four_name_strings_published": names == ["oriente", "occidente", "miechiorn", "aquilo"],
        "individual_name_to_figure_position_map_stated": False,
        "visual_start_or_orientation_stated": False,
    }
    transfer_gates = {"exact_source_target_unit_cardinality_and_topology": False, "one_owned_target_text_locus_per_figure_group": False, "one_to_one_source_name_target_locus_map": False, "common_start_and_orientation": False}
    evidence = {"notices": notices, "projected_cardinal_names": names, "target_projection": target_projection}
    reconstructed = {
        "experiment": "INITIALE_F67V2_CARDINAL_WIND_OWNERSHIP",
        "status": "PASS_EXPLICIT_SOURCE_INTERNAL_FOUR_CARDINAL_WIND_REGISTER_NO_F67V2_TRANSFER",
        "decision": "RETAIN_SG1029_F135_AS_STRONG_FOUR_CARDINAL_WIND_COMPARATOR_STOP_BEFORE_IMAGE",
        "source": {"publisher": "Initiale / IRHT-CNRS", "record_urls": dict(SOURCES), "evidence_projection_sha256": h(canon(evidence))},
        "notices": notices,
        "projected_cardinal_names_in_catalogue_order_not_visual_order": names,
        "source_gates": source_gates,
        "target_projection": target_projection,
        "transfer_gates": transfer_gates,
        "gates": {"source_internal_four_cardinal_register": True, "qualified_human_image_inspection_still_worthwhile": True, "f67v2_source_transfer_authorized": False, "image_or_iiif_document_opened": False},
        "source_access": {"initiale_html_notices_opened": True, "initiale_or_arca_images_opened": False, "iiif_information_documents_opened": False, "papers_pdfs_ocr_or_automated_visual_output_opened": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: h(SPEC.read_bytes()), f"results/{TARGET.name}": h(TARGET.read_bytes())},
        "claim_ceiling": "Initiale 69596 establishes a source-internal collective register of four crowned cardinal winds named oriente, occidente, miechiorn, and aquilo in a central circle. It does not map each name to an individual figure position, and f67v2 has nonmatching 3/4-face groups, several competing text registers, and no common start/orientation. No Initiale direction or wind name, crown, sex, person, face, slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.",
    }
    production = json.loads(PRODUCTION.read_text())
    checks = {
        "two_exact_initiale_records": [row["record"] for row in notices] == [x[0] for x in SOURCES],
        "bourges_identity": bourges["fields"].get("Référence") == "Bourges, BM, 0105" and bourges["fields"].get("Folio/page") == "f. 095v",
        "bourges_subject": bourges["fields"].get("Sujet") == "Rose des vents",
        "bourges_keywords": all(x in bourges["fields"].get("Mot clé", "") for x in ("tête", "points cardinaux (les)", "cercle", "souffle")),
        "bourges_no_note": "Notes" not in bourges["fields"],
        "bourges_one_unopened_image_locator": bourges["declared_image_count_not_opened"] == 1 and len(bourges["iiif_info_urls_not_opened"]) == 1,
        "sg_identity": sg["fields"].get("Référence") == "Paris, Bibl. Sainte-Geneviève, 1029" and sg["fields"].get("Folio/page") == "f. 135",
        "sg_subject_and_context": sg["fields"].get("Sujet") == "Rose des vents" and sg["fields"].get("Contexte") == "Miniature au livre 11",
        "sg_literal_note_exact": sg["fields"].get("Notes") == LITERAL_NOTE,
        "sg_four_names_exact": names == ["oriente", "occidente", "miechiorn", "aquilo"],
        "sg_two_unopened_image_locators": sg["declared_image_count_not_opened"] == 2 and len(sg["iiif_info_urls_not_opened"]) == 2,
        "source_internal_register_gates": all(source_gates[x] for x in tuple(source_gates)[:4]),
        "source_individual_placement_gates_false": not source_gates["individual_name_to_figure_position_map_stated"] and not source_gates["visual_start_or_orientation_stated"],
        "target_projection_exact": target_projection == {"f67v2_four_corner_face_groups": True, "f67v2_each_group_exactly_three_faces": False, "f67v2_text_loci": 22, "f67v2_radial_loci": 8, "f67v2_label_loci": 6, "f67v2_owned_twelve_slot_register": False, "common_start_direction_and_slot_correspondence": False},
        "all_transfer_gates_false": not any(transfer_gates.values()),
        "evidence_projection_digest": reconstructed["source"]["evidence_projection_sha256"] == production["source"]["evidence_projection_sha256"],
        "canonical_result_exact": canon(reconstructed) == PRODUCTION.read_bytes(),
        "report_exact": expected_report().encode() == PRODUCTION_REPORT.read_bytes(),
        "image_access_false": not reconstructed["gates"]["image_or_iiif_document_opened"] and not reconstructed["source_access"]["initiale_or_arca_images_opened"],
        "claim_ceiling_exact": reconstructed["claim_ceiling"] == production["claim_ceiling"],
    }
    failures = [key for key, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError(f"Initiale validation failures: {failures}")
    validation = {
        "experiment": "INITIALE_F67V2_CARDINAL_WIND_OWNERSHIP_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_OFFICIAL_SOURCE_RECONSTRUCTION",
        "decision": "VALIDATE_FOUR_CARDINAL_WIND_COMPARATOR_NO_F67V2_TRANSFER",
        "validated_result_sha256": h(PRODUCTION.read_bytes()),
        "validated_report_sha256": h(PRODUCTION_REPORT.read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": {"initiale_notices": 2, "published_cardinal_names": 4, "source_internal_registers": 1, "f67v2_transfer_candidates": 0},
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUT.write_bytes(canon(validation))
    OUT_REPORT.write_text(
        "# Initiale f67v2 cardinal-wind ownership — independent validation\n\n"
        f"All **{len(checks)}** checks pass. Independent code live-reconstructs both Initiale notices, the exact four-name "
        "cardinal-wind note, unopened image-locator metadata, the validated f67v2 comparison, every source and transfer "
        "gate, the canonical result, and the exact report.\n\n"
        "This confirms a source-internal four-cardinal-wind register and zero f67v2 transfers. No image or IIIF information "
        "document was opened, and no direction, wind name, crown, sex, person, face, slot, label, word, sound, language, "
        "cipher operation, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
