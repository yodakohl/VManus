#!/usr/bin/env python3
"""Text-only Initiale follow-up for the f67v2 wind-circle lead."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "INITIALE_F67V2_CARDINAL_WIND_OWNERSHIP_SPEC.md"
TARGET_PRIOR = RESULTS / "bnf_lat18499_f67v2_wind_rose_metadata_worth.json"
OUT_JSON = RESULTS / "initiale_f67v2_cardinal_wind_ownership.json"
OUT_REPORT = RESULTS / "initiale_f67v2_cardinal_wind_ownership_report.md"
URLS = {
    "Bourges_Ms105_f095v": "https://initiale.irht.cnrs.fr/decor/14834",
    "Sainte_Genevieve_Ms1029_f135": "https://initiale.irht.cnrs.fr/decor/69596",
}
NOTE = 'Les quatre vents cardinaux, couronnés, sont nommés dans le cercle central : "oriente", "occidente", "miechiorn", "aquilo".'
NAMES = ["oriente", "occidente", "miechiorn", "aquilo"]
FIELDS = (
    "Référence",
    "Folio/page",
    "Sujet",
    "Contexte",
    "Mot clé",
    "Conservation",
    "Notes",
    "Signature",
    "Auteur",
    "Titre",
    "Origine",
    "Datation",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def clean(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", value)).split())


def fetch(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-Initiale-cardinal-wind/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get_all("Location"):
            raise ValueError(f"unexpected Initiale response: {url}")
        return response.read().decode("utf-8")


def parse_notice(key: str, url: str) -> dict[str, object]:
    page = fetch(url)
    values: dict[str, str] = {}
    for raw_name, raw_value in re.findall(
        r"<label>(.*?)</label>\s*<p class=\"txt_res\"[^>]*>(.*?)</p>",
        page,
        flags=re.I | re.S,
    ):
        name, value = clean(raw_name), clean(raw_value)
        if name in FIELDS and value:
            if name in values and values[name] != value:
                raise ValueError(f"duplicate Initiale field: {key} {name}")
            values[name] = value
    image_match = re.search(r'<span id="nbImages">([0-9]+)</span>', page)
    locator_urls = sorted(set(re.findall(r'data-infojson="(https://iiif\.irht\.cnrs\.fr/iiif/[^\"]+/info\.json)"', page)))
    if image_match is None or int(image_match.group(1)) < 1 or not locator_urls:
        raise ValueError(f"Initiale locator drift: {key}")
    return {
        "record": key,
        "url": url,
        "fields": values,
        "declared_image_count_not_opened": int(image_match.group(1)),
        "iiif_info_urls_not_opened": locator_urls,
    }


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Initiale ownership outputs")
    notices = [parse_notice(key, url) for key, url in URLS.items()]
    bourges, sg = notices
    bourges_terms = {item.strip() for item in str(bourges["fields"].get("Mot clé", "")).split(",")}
    required_bourges = {"vents (les)", "points cardinaux (les)", "tête", "cercle", "souffle"}
    if bourges["fields"].get("Sujet") != "Rose des vents" or not required_bourges <= bourges_terms or "Notes" in bourges["fields"]:
        raise ValueError("Bourges control notice drift")
    if sg["fields"].get("Notes") != NOTE:
        raise ValueError("Sainte-Geneviève cardinal-wind note drift")
    projected_names = re.findall(r'"([^"]+)"', str(sg["fields"]["Notes"]))
    if projected_names != NAMES:
        raise ValueError("Sainte-Geneviève name projection drift")
    target = json.loads(TARGET_PRIOR.read_text())
    target_projection = {
        "f67v2_four_corner_face_groups": target["gates"]["f67v2_has_four_corner_face_groups"],
        "f67v2_each_group_exactly_three_faces": target["gates"]["f67v2_each_group_has_exactly_three_faces"],
        "f67v2_text_loci": target["counts"]["f67v2_text_loci"],
        "f67v2_radial_loci": target["counts"]["f67v2_radial_loci"],
        "f67v2_label_loci": target["counts"]["f67v2_label_loci"],
        "f67v2_owned_twelve_slot_register": target["gates"]["f67v2_has_owned_twelve_slot_text_register"],
        "common_start_direction_and_slot_correspondence": target["gates"]["common_start_direction_and_slot_correspondence"],
    }
    if target_projection != {
        "f67v2_four_corner_face_groups": True,
        "f67v2_each_group_exactly_three_faces": False,
        "f67v2_text_loci": 22,
        "f67v2_radial_loci": 8,
        "f67v2_label_loci": 6,
        "f67v2_owned_twelve_slot_register": False,
        "common_start_direction_and_slot_correspondence": False,
    }:
        raise ValueError("validated f67v2 target projection drift")
    source_gates = {
        "exactly_four_cardinal_winds_stated": "quatre vents cardinaux" in NOTE,
        "crowned_personification_stated": "couronnés" in NOTE,
        "central_circle_collective_name_ownership_stated": "nommés dans le cercle central" in NOTE,
        "exactly_four_name_strings_published": len(projected_names) == 4 and len(set(projected_names)) == 4,
        "individual_name_to_figure_position_map_stated": False,
        "visual_start_or_orientation_stated": False,
    }
    transfer_gates = {
        "exact_source_target_unit_cardinality_and_topology": False,
        "one_owned_target_text_locus_per_figure_group": False,
        "one_to_one_source_name_target_locus_map": False,
        "common_start_and_orientation": False,
    }
    if not all(source_gates[key] for key in tuple(source_gates)[:4]) or any(source_gates[key] for key in tuple(source_gates)[4:]) or any(transfer_gates.values()):
        raise ValueError("ownership/transfer gate drift")
    evidence = {"notices": notices, "projected_cardinal_names": projected_names, "target_projection": target_projection}
    result = {
        "experiment": "INITIALE_F67V2_CARDINAL_WIND_OWNERSHIP",
        "status": "PASS_EXPLICIT_SOURCE_INTERNAL_FOUR_CARDINAL_WIND_REGISTER_NO_F67V2_TRANSFER",
        "decision": "RETAIN_SG1029_F135_AS_STRONG_FOUR_CARDINAL_WIND_COMPARATOR_STOP_BEFORE_IMAGE",
        "source": {"publisher": "Initiale / IRHT-CNRS", "record_urls": URLS, "evidence_projection_sha256": sha(canonical(evidence))},
        "notices": notices,
        "projected_cardinal_names_in_catalogue_order_not_visual_order": projected_names,
        "source_gates": source_gates,
        "target_projection": target_projection,
        "transfer_gates": transfer_gates,
        "gates": {"source_internal_four_cardinal_register": True, "qualified_human_image_inspection_still_worthwhile": True, "f67v2_source_transfer_authorized": False, "image_or_iiif_document_opened": False},
        "source_access": {"initiale_html_notices_opened": True, "initiale_or_arca_images_opened": False, "iiif_information_documents_opened": False, "papers_pdfs_ocr_or_automated_visual_output_opened": False, "decoder_claims_opened": False},
        "inputs": {SPEC.name: sha(SPEC.read_bytes()), f"results/{TARGET_PRIOR.name}": sha(TARGET_PRIOR.read_bytes())},
        "claim_ceiling": "Initiale 69596 establishes a source-internal collective register of four crowned cardinal winds named oriente, occidente, miechiorn, and aquilo in a central circle. It does not map each name to an individual figure position, and f67v2 has nonmatching 3/4-face groups, several competing text registers, and no common start/orientation. No Initiale direction or wind name, crown, sex, person, face, slot, label, word, sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
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
        "sound, language, cipher operation, plaintext, meaning, or translation transfers to f67v2.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
