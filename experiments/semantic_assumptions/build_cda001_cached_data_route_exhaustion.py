#!/usr/bin/env python3
"""Build the source-only CDA001 cached-data route exhaustion result."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
METHOD = BASE / "CDA001_CACHED_DATA_ROUTE_EXHAUSTION_METHOD.md"
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RES / "source_sta_family_consensus_validation.json"
IGR1 = RES / "igr001_image_grounded_grapheme_selection.json"
IGR2 = RES / "igr002_image_grounded_grapheme_atlas_selection.json"
TGC_PANEL = RES / "tgc001_whole_group_trace_capacity_panel.tsv"
TGC_STOP = RES / "tgc001_fresh_panel_feasibility_correction.json"
ANCHORS = RES / "translation_anchor_acquisition_registry_v1.json"
NVA1 = RES / "nva001_native_visual_next_route_worth.json"
NVA2 = RES / "nva002_public_physical_layer_update_prescreen.json"
RTA = RES / "rta001_result.json"
LTG = RES / "ltg001_latent_channel_result.json"
IGR2_RESULT = RES / "igr002_image_grounded_grapheme_atlas_result.json"
OUT = RES / "cda001_cached_data_route_exhaustion.json"
REPORT = RES / "cda001_cached_data_route_exhaustion_report.md"

EXPECTED = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    IGR1: "6837ed894969452dc138f433fd52e3399d468de48bb654e805ebab6b8ded96aa",
    IGR2: "caa5bd8dd40e37a550b48fc26f89c2696bd5fb2c57e47b006a478e09bee93be2",
    TGC_PANEL: "1b5393da5c246acfc7a61a9d555241dcd37ed8f593286776696544d2c0a17d97",
    TGC_STOP: "f3276a37e0248b4e497ee62f1daa03f325c1cfaac68fc26d4695e63bdc2b5b47",
    ANCHORS: "0a285cccbe9507987978157d4511ce099e2a3ff54e22f416297337c89089ad14",
    NVA1: "1138bba6cb609cf5fb8c86a65d369591bb8dc69c66a296f1a48f4c29fdf00ffa",
    NVA2: "73518dbf8e6549a4ed42ffb4481f2e00768174b02ca77bb04c60d1b6f72face6",
    RTA: "9987037c2d60189d337cccf3aeb2b817a9a8ac9b47b719cf663f40c87e892f97",
    LTG: "e5ca5c6ebe60b391c0cf0d7826a4acb8c1f1879677f0ff96033ceae7ae652fd3",
    IGR2_RESULT: "c5b553ab6f04ed01fe30a8a8bb5d0114f9ac84a0bb4c9e866d984dd47e30b3e1",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path.name}")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input drift: {path.name}")
    if not json.loads(SOURCE_VALIDATION.read_text())["status"].startswith("PASS_"):
        raise SystemExit("source validation is not PASS")

    igr1 = json.loads(IGR1.read_text())["targets"]
    igr2 = json.loads(IGR2.read_text())["targets"]
    tgc = list(csv.DictReader(TGC_PANEL.open(newline=""), delimiter="\t"))
    used_loci = {row["locus"] for row in (*igr1, *igr2, *tgc)}
    used_folios = {row["physical_folio"] for row in (*igr1, *igr2, *tgc)}
    source = list(csv.DictReader(SOURCE.open(newline=""), delimiter="\t"))
    stable = [
        row for row in source
        if row["strict_zero_alternative"] == "1"
        and row["grammar_scope"] == "CONFIRMED_PROSE"
        and 1 <= int(row["symbol_count"]) <= 8
        and row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"]
    ]
    locus_fresh = [row for row in stable if row["locus"] not in used_loci]
    folio_fresh = [row for row in stable if folio(row["page"]) not in used_folios]
    if (len(stable), sum(int(row["symbol_count"]) for row in stable), len({folio(row["page"]) for row in stable})) != (18844, 74994, 94):
        raise SystemExit("stable reservoir drift")
    if (len(locus_fresh), sum(int(row["symbol_count"]) for row in locus_fresh)) != (18271, 72737):
        raise SystemExit("locus-fresh reservoir drift")
    if (len(folio_fresh), sum(int(row["symbol_count"]) for row in folio_fresh), len({folio(row["page"]) for row in folio_fresh})) != (4878, 18068, 46):
        raise SystemExit("folio-fresh reservoir drift")

    anchors = json.loads(ANCHORS.read_text())
    nva1 = json.loads(NVA1.read_text())
    nva2 = json.loads(NVA2.read_text())
    tgc_stop = json.loads(TGC_STOP.read_text())
    rta = json.loads(RTA.read_text())
    ltg = json.loads(LTG.read_text())
    igr2_result = json.loads(IGR2_RESULT.read_text())
    bound_statuses = {
        "RTA001": rta["decision"],
        "LTG001": ltg["status"],
        "IGR002": igr2_result["status"],
        "TGC001": tgc_stop["status"],
        "NVA001": nva1["status"],
        "NVA002": nva2["status"],
    }
    expected_statuses = {
        "RTA001": "NO_TRANSFER_AT_REGISTERED_RESOLUTION",
        "LTG001": "FINAL_NONCONFIRMATION",
        "IGR002": "FINAL_MAPPING_INVARIANT_VISIBLE_SHAPE_TRANSFER_FAILURE_PROVENANCE_QUALIFIED",
        "TGC001": "STOP_FRESH_PANEL_IMPOSSIBLE_2_ROWS_ZERO_WHOLE_FOLIO_FRESH",
        "NVA001": "STOP_NO_GENUINELY_NEW_CAPACITY_QUALIFIED_NATIVE_VISUAL_ROUTE",
        "NVA002": "STOP_NO_NEW_PUBLIC_IMAGE_LAYER_OR_UNCOVERED_MSI_FOLIO",
    }
    if bound_statuses != expected_statuses:
        raise SystemExit("route status drift")
    if anchors["counts"] != {
        "admissible_families": 0,
        "candidate_families": 11,
        "maximum_gate_count": 4,
        "selected_ledger_rows": 11,
        "special_circle_families": 4,
    }:
        raise SystemExit("anchor registry drift")
    if tgc_stop["counts"]["whole_folio_fresh_rows"] != 0:
        raise SystemExit("TGC fresh capacity drift")

    result = {
        "access": {
            "external_claim_validated": False,
            "manuscript_image_bodies_opened": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "semantic_or_translation_target_scored": False,
        },
        "bound_route_statuses": bound_statuses,
        "claim_ceiling": "The present cache contains no admissible next experiment under the active rules. This does not show that the manuscript is untranslatable and supplies no word, sound, language, cipher, plaintext, meaning, or translation.",
        "counts": {
            "translation_anchor_families": anchors["counts"]["candidate_families"],
            "admissible_translation_anchor_families": anchors["counts"]["admissible_families"],
            "maximum_translation_anchor_gates_of_six": anchors["counts"]["maximum_gate_count"],
            "all_reading_stable_groups": len(stable),
            "all_reading_stable_symbol_positions": sum(int(row["symbol_count"]) for row in stable),
            "all_reading_stable_physical_folios": len({folio(row["page"]) for row in stable}),
            "unused_locus_stable_groups": len(locus_fresh),
            "unused_locus_stable_symbol_positions": sum(int(row["symbol_count"]) for row in locus_fresh),
            "unused_folio_stable_groups": len(folio_fresh),
            "unused_folio_stable_symbol_positions": sum(int(row["symbol_count"]) for row in folio_fresh),
            "unused_stable_physical_folios": len({folio(row["page"]) for row in folio_fresh}),
            "tgc_whole_folio_fresh_rows": tgc_stop["counts"]["whole_folio_fresh_rows"],
        },
        "decision": "WAIT_FOR_NEW_TRANSLATION_BEARING_EVIDENCE",
        "excluded_reservoir_interpretation": {
            "manual_identity_target": "EXACT_LABEL_DECODER_DUPLICATE_OR_FORBIDDEN",
            "symbol_count_or_boundary_target": "BROAD_VISUAL_SEGMENTATION_WITHOUT_INDEPENDENT_PHYSICAL_GOLD",
            "alternate_reading_choice": "CLOSED_TRANSCRIPTION_ADJUDICATION_OR_ALLOGRAPHY_ROUTE",
        },
        "experiment": "CDA001_CACHED_DATA_ROUTE_EXHAUSTION",
        "inputs": {str(path.relative_to(BASE.parents[1])): sha(path) for path in (*EXPECTED, METHOD, Path(__file__).resolve())},
        "minimum_new_evidence": {
            "independent_physical_folios": 5,
            "requirements": [
                "provenance-clean human diplomatic annotation",
                "singular author-visible Voynich-text to independently readable-value binding",
                "repeated contrasting readable values",
                "unique current-locus mappings with uncertainty",
                "at least one whole physical folio reserved untouched for confirmation",
            ],
        },
        "status": "STOP_NO_ADMISSIBLE_CACHED_DATA_ROUTE",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# CDA001 cached-data route exhaustion audit\n\n"
        f"Status: **{result['status']}**.\n\n"
        "The translation-anchor registry remains at zero admissible families out of eleven, with a maximum of four of six gates. RTA001, LTG001, IGR002, TGC001, NVA001, and NVA002 retain their registered negative or stop decisions.\n\n"
        f"The unused transcription cache is numerically large: {len(locus_fresh):,} all-reading-stable groups remain outside IGR001, IGR002, and TGC001 selected loci, and {len(folio_fresh):,} lie on {len({folio(row['page']) for row in folio_fresh})} physical folios outside those three panels. This is not a claim of no exposure in other experiments. Those rows do not create a new experiment. Their manual identities would be an excluded exact-label decoder; their counts or boundaries would be a broad visual segmentation target without independent physical-boundary truth.\n\n"
        "No admissible cached-data route remains. The minimum translation-bearing addition is a provenance-clean, singularly owned, independently readable contrast family on at least five physical folios with one whole folio untouched. Another model or GPU search cannot resolve the semantic permutation without such evidence. This is not proof that the manuscript is untranslatable and supplies no word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
