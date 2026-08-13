#!/usr/bin/env python3
"""Independent validator for CDA001 cached-data route exhaustion."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
METHOD = BASE / "CDA001_CACHED_DATA_ROUTE_EXHAUSTION_METHOD.md"
BUILDER = BASE / "build_cda001_cached_data_route_exhaustion.py"
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
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
RESULT = RES / "cda001_cached_data_route_exhaustion.json"
REPORT = RES / "cda001_cached_data_route_exhaustion_report.md"
OUT = RES / "cda001_cached_data_route_exhaustion_validation.json"
OUT_REPORT = RES / "cda001_cached_data_route_exhaustion_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pf(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def ck(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {name}")
    checks.append(name)


def main() -> None:
    for path in (OUT, OUT_REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path.name}")
    checks: list[str] = []
    result = json.loads(RESULT.read_text())
    igr1 = json.loads(IGR1.read_text())["targets"]
    igr2 = json.loads(IGR2.read_text())["targets"]
    tgc_panel = list(csv.DictReader(TGC_PANEL.open(newline=""), delimiter="\t"))
    used_loci = {row["locus"] for row in (*igr1, *igr2, *tgc_panel)}
    used_folios = {row["physical_folio"] for row in (*igr1, *igr2, *tgc_panel)}
    stable = []
    with SOURCE.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if (
                row["strict_zero_alternative"] == "1"
                and row["grammar_scope"] == "CONFIRMED_PROSE"
                and 1 <= int(row["symbol_count"]) <= 8
                and row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"]
            ):
                stable.append(row)
    locus_fresh = [row for row in stable if row["locus"] not in used_loci]
    folio_fresh = [row for row in stable if pf(row["page"]) not in used_folios]
    counts = result["counts"]
    ck((len(stable), sum(int(row["symbol_count"]) for row in stable), len({pf(row["page"]) for row in stable})) == (18844, 74994, 94), "stable_reservoir_18844_74994_94", checks)
    ck((len(locus_fresh), sum(int(row["symbol_count"]) for row in locus_fresh)) == (18271, 72737), "unused_locus_reservoir_18271_72737", checks)
    ck((len(folio_fresh), sum(int(row["symbol_count"]) for row in folio_fresh), len({pf(row["page"]) for row in folio_fresh})) == (4878, 18068, 46), "unused_folio_reservoir_4878_18068_46", checks)
    anchors = json.loads(ANCHORS.read_text())
    ck(anchors["counts"]["candidate_families"] == 11 and anchors["counts"]["admissible_families"] == 0 and anchors["counts"]["maximum_gate_count"] == 4, "anchor_registry_11_0_max4", checks)
    ck(json.loads(TGC_STOP.read_text())["counts"]["whole_folio_fresh_rows"] == 0, "tgc_zero_whole_folio_fresh", checks)
    statuses = {
        "RTA001": json.loads(RTA.read_text())["decision"],
        "LTG001": json.loads(LTG.read_text())["status"],
        "IGR002": json.loads(IGR2_RESULT.read_text())["status"],
        "TGC001": json.loads(TGC_STOP.read_text())["status"],
        "NVA001": json.loads(NVA1.read_text())["status"],
        "NVA002": json.loads(NVA2.read_text())["status"],
    }
    expected_statuses = {
        "RTA001": "NO_TRANSFER_AT_REGISTERED_RESOLUTION",
        "LTG001": "FINAL_NONCONFIRMATION",
        "IGR002": "FINAL_MAPPING_INVARIANT_VISIBLE_SHAPE_TRANSFER_FAILURE_PROVENANCE_QUALIFIED",
        "TGC001": "STOP_FRESH_PANEL_IMPOSSIBLE_2_ROWS_ZERO_WHOLE_FOLIO_FRESH",
        "NVA001": "STOP_NO_GENUINELY_NEW_CAPACITY_QUALIFIED_NATIVE_VISUAL_ROUTE",
        "NVA002": "STOP_NO_NEW_PUBLIC_IMAGE_LAYER_OR_UNCOVERED_MSI_FOLIO",
    }
    ck(statuses == expected_statuses, "literal_negative_stop_statuses_exact", checks)
    ck(statuses == result["bound_route_statuses"], "bound_statuses_exact", checks)
    ck(counts == {
        "admissible_translation_anchor_families": 0,
        "all_reading_stable_groups": 18844,
        "all_reading_stable_physical_folios": 94,
        "all_reading_stable_symbol_positions": 74994,
        "maximum_translation_anchor_gates_of_six": 4,
        "tgc_whole_folio_fresh_rows": 0,
        "translation_anchor_families": 11,
        "unused_folio_stable_groups": 4878,
        "unused_folio_stable_symbol_positions": 18068,
        "unused_locus_stable_groups": 18271,
        "unused_locus_stable_symbol_positions": 72737,
        "unused_stable_physical_folios": 46,
    }, "result_counts_exact", checks)
    expected_inputs = {str(path.relative_to(BASE.parents[1])): sha(path) for path in (SOURCE, RES / "source_sta_family_consensus_validation.json", IGR1, IGR2, TGC_PANEL, TGC_STOP, ANCHORS, NVA1, NVA2, RTA, LTG, IGR2_RESULT, METHOD, BUILDER)}
    ck(result["inputs"] == expected_inputs, "input_hashes_exact", checks)
    ck(result["status"] == "STOP_NO_ADMISSIBLE_CACHED_DATA_ROUTE", "stop_status", checks)
    ck(result["decision"] == "WAIT_FOR_NEW_TRANSLATION_BEARING_EVIDENCE", "wait_decision", checks)
    ck(result["access"] == {"external_claim_validated": False, "manuscript_image_bodies_opened": False, "ocr_clip_embedding_or_automated_vision_used": False, "semantic_or_translation_target_scored": False}, "access_closed", checks)
    ck(result["minimum_new_evidence"]["independent_physical_folios"] == 5 and len(result["minimum_new_evidence"]["requirements"]) == 5, "minimum_new_evidence_exact", checks)
    ck(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n" == RESULT.read_text(), "result_canonical", checks)
    report = REPORT.read_text()
    ck("No admissible cached-data route remains" in report and "not proof that the manuscript is untranslatable" in report, "report_ceiling", checks)

    payload = {
        "checks": checks,
        "checks_passed": len(checks),
        "decision": result["decision"],
        "inputs": {str(path.relative_to(BASE.parents[1])): sha(path) for path in (METHOD, BUILDER, RESULT, REPORT)},
        "status": "PASS_INDEPENDENT_CACHED_ROUTE_EXHAUSTION_RECONSTRUCTION",
    }
    OUT.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    OUT_REPORT.write_text(
        "# CDA001 cached-data route exhaustion validation\n\n"
        f"Status: **{payload['status']}**.\n\n"
        f"Independent source-only reconstruction passes {len(checks)} checks. It reproduces the stable-group reservoirs, zero-of-eleven anchor capacity, six bound route decisions, zero TGC whole-folio-fresh rows, closed access, and the new-evidence requirement.\n\n"
        "This route audit supplies no word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    print(json.dumps({"status": payload["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
