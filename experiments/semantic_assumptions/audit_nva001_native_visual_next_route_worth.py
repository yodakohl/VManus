#!/usr/bin/env python3
"""Source-only worth audit for the next native-visual Voynich route."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "NVA001_NATIVE_VISUAL_NEXT_ROUTE_WORTH_METHOD.md"
LEDGER = BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"
ANNOTATIONS = RES / "existing_human_exact_locus_annotations.tsv"
ROLES = RES / "existing_human_locus_roles.tsv"
PUBLIC_PAGES = RES / "public_voynich_nu_page_annotations_v2.tsv"
DRI_SELECTION = RES / "dri001_paired_document_role_inventory_selection.json"
DRI_RESULT = RES / "dri001_paired_document_role_inventory_result.json"
DRI2_RESULT = RES / "dri002_discordant_cell_role_capacity_result.json"
REGISTRY = RES / "translation_anchor_acquisition_registry_v1.tsv"
OUT = RES / "nva001_native_visual_next_route_worth.json"
REPORT = RES / "nva001_native_visual_next_route_worth_report.md"

STRONG = ("REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def physical_folio(page: str) -> str:
    match = re.match(r"f(\d+)", page)
    return "f" + match.group(1) if match else page


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")

    ledger_rows = {row["experiment"]: row for row in read_tsv(LEDGER)}
    expected_statuses = {
        "attached_label_v2_final": "FINAL_VALIDATED_NARROW_NONCONFIRMATION",
        "LM001Y_final_residual_leaf_margin_census_result": "PASS_COMBINED_VISUAL_CAPACITY_ALL_ORIGINAL_GATES",
        "LM002_synthetic_calibration": "STOP_SYNTHETIC_INSTRUMENT_FAILED",
        "SME003_independent_full_calibration_validation": "PASS_402_CASE_TARGET_FREE_RECONSTRUCTION_FAIL_CLOSE_CONFIRMED",
        "f66r_border_permitted_evidence_audit": "PASS_PHYSICAL_HIERARCHY_FUNCTION_UNKNOWN",
        "RFH001_f73v_retracer_hook": "PASS_ONE_VISIBLE_HOOK_BEARING_UNDERSTROKE_AND_HOOKLESS_RETRACING",
        "RBR002_complete_outer_ring_underlayer_capacity": "STOP_INSUFFICIENT_COMPLETE_UNDERLAYER_RECOVERY_CAPACITY",
        "DRI002_discordant_cell_role_capacity_result": "STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY",
    }
    observed_statuses = {key: ledger_rows[key]["status"] for key in expected_statuses}
    if observed_statuses != expected_statuses:
        raise SystemExit(observed_statuses)

    annotations = read_tsv(ANNOTATIONS)
    strong_rows: dict[str, list[dict[str, str]]] = {}
    unit_states: dict[tuple[str, str], set[str]] = defaultdict(set)
    for relation in STRONG:
        selected = [
            row for row in annotations
            if row["certainty"] == "UNHEDGED"
            and row["relation_scope"] == "EXACT_LOCAL_COMMENT"
            and relation in row["local_relation_tags"].split(";")
        ]
        strong_rows[relation] = selected
        for row in selected:
            unit_states[(row["page"], row["unit"])].add(relation)
    strong_counts = {
        relation: {
            "loci": len(rows),
            "units": len({(row["page"], row["unit"]) for row in rows}),
            "pages": sorted({row["page"] for row in rows}),
        }
        for relation, rows in strong_rows.items()
    }
    if {key: (value["loci"], value["units"]) for key, value in strong_counts.items()} != {
        "REL_EXPLICIT_ATTACHMENT": (51, 6),
        "REL_ENCLOSURE": (48, 10),
        "REL_OVERLAP_OR_CONTACT": (8, 6),
    }:
        raise SystemExit(strong_counts)
    mixed_strong_units = sorted(
        f"{page}|{unit}" for (page, unit), states in unit_states.items() if len(states) >= 2
    )
    if mixed_strong_units:
        raise SystemExit(mixed_strong_units)

    retracing = [row for row in annotations if re.search(r"\bretrac", row["local_comment"], re.I)]
    feature_difference = [
        row for row in retracing
        if re.search(r"original hook.*retracer did not", row["local_comment"], re.I)
    ]
    if len(retracing) != 9 or [(row["page"], row["locus"]) for row in feature_difference] != [("f73v", "f73v.15")]:
        raise SystemExit("retracing census changed")

    page_rows: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in read_tsv(ROLES):
        page_rows.setdefault(row["page"], []).append(row)
    cells: dict[tuple[str, str], list[str]] = defaultdict(list)
    for page, rows in page_rows.items():
        kind_run = "".join(kind for kind, _ in itertools.groupby(row["kind"] for row in rows))
        cells[(rows[0]["section"], kind_run)].append(page)
    text_cell_pages = cells[("T", "P")]
    if text_cell_pages != ["f1r", "f85r1", "f86v6", "f86v5"]:
        raise SystemExit(text_cell_pages)

    selection = json.loads(DRI_SELECTION.read_text(encoding="utf-8"))
    result = json.loads(DRI_RESULT.read_text(encoding="utf-8"))
    selected_text_pages = [
        row["page"] for row in selection["rows"]
        if row["section"] == "T" and row["kind_run_template"] == "P"
    ]
    text_cell_result = next(row for row in result["cells"] if row["cell_id"] == "DRC13")
    if selected_text_pages != ["f86v5", "f85r1"] or {
        text_cell_result["calibration_role"], text_cell_result["diagnostic_role"]
    } != {"PROSE_DOMINANT"}:
        raise SystemExit("DRC13 changed")
    public = {row["page"]: row for row in read_tsv(PUBLIC_PAGES)}
    f1r_text = " ".join((public["f1r"]["general_description"], public["f1r"]["text_description"])).lower()
    f1r_prose_fixed = "text-only page" in f1r_text and "four paragraphs" in f1r_text and "fill the entire page" in f1r_text
    if not f1r_prose_fixed:
        raise SystemExit("f1r prose evidence changed")
    maximum_nonprose_folios_in_text_cell = 1

    dri2 = json.loads(DRI2_RESULT.read_text(encoding="utf-8"))
    if dri2["status"] != "STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY":
        raise SystemExit("DRI002 status changed")

    registry = read_tsv(REGISTRY)
    admissible = [row for row in registry if row["admissible"] == "1"]
    if len(registry) != 11 or admissible:
        raise SystemExit("translation-anchor registry changed")

    candidate_checks = {
        "held_star_point_count": {
            "decision": "DUPLICATE_FINAL_52_LOCUS_17_TEST_NONCONFIRMATION",
            "new_image_access_authorized": False,
        },
        "herbal_leaf_margin": {
            "decision": "CONSUMED_VISUAL_CAPACITY_FORMAL_SUCCESSOR_STOPPED_SYNTHETIC",
            "new_image_access_authorized": False,
        },
        "strong_exact_local_relations": {
            "counts": strong_counts,
            "mixed_strong_units": mixed_strong_units,
            "decision": "STOP_ZERO_WITHIN_UNIT_RELATION_MOBILITY",
            "new_image_access_authorized": False,
        },
        "retracing_feature_recurrence": {
            "retracing_comments": len(retracing),
            "strict_feature_difference_loci": [row["locus"] for row in feature_difference],
            "decision": "STOP_ONE_FEATURE_DIFFERENCE_LOCUS",
            "new_image_access_authorized": False,
        },
        "f66r_marginal_columns": {
            "decision": "DUPLICATE_PRIOR_PHYSICAL_HIERARCHY_FUNCTION_UNKNOWN",
            "new_image_access_authorized": False,
        },
        "compact_text_only_role_cell": {
            "pages": text_cell_pages,
            "published_prose_dominant_pages": ["f85r1", "f86v5"],
            "human_fixed_prose_dominant_page": "f1r",
            "remaining_unjudged_page": "f86v6",
            "maximum_nonprose_folios": maximum_nonprose_folios_in_text_cell,
            "decision": "STOP_SECOND_ROLE_CANNOT_REACH_TWO_FOLIOS",
            "new_image_access_authorized": False,
        },
        "translation_anchor_registry": {
            "families": len(registry),
            "admissible": len(admissible),
            "decision": "STOP_ZERO_ADMISSIBLE_READABLE_ANCHORS",
            "new_image_access_authorized": False,
        },
    }
    gates = {
        "all_candidate_checks_source_only": True,
        "zero_manuscript_image_bodies_opened": True,
        "zero_transcription_fillers_or_formal_features_opened": True,
        "zero_ocr_clip_embedding_or_automated_vision": True,
        "zero_new_capacity_qualified_visual_routes": not any(
            item["new_image_access_authorized"] for item in candidate_checks.values()
        ),
        "zero_current_admissible_translation_anchors": len(admissible) == 0,
    }
    if not all(gates.values()):
        raise SystemExit(gates)

    payload = {
        "experiment": "NVA001_NATIVE_VISUAL_NEXT_ROUTE_WORTH_AUDIT",
        "schema": "NVA001_RESULT_V1",
        "status": "STOP_NO_GENUINELY_NEW_CAPACITY_QUALIFIED_NATIVE_VISUAL_ROUTE",
        "decision": "REQUIRE_NEW_READABLE_OR_PHYSICAL_LAYER_EVIDENCE",
        "candidate_checks": candidate_checks,
        "gates": gates,
        "prerequisite_route_statuses": observed_statuses,
        "inputs": {
            str(path.relative_to(ROOT)): sha(path)
            for path in (METHOD, ANNOTATIONS, ROLES, PUBLIC_PAGES, DRI_SELECTION, DRI_RESULT, DRI2_RESULT, REGISTRY)
        },
        "access": {
            "manuscript_image_bodies_opened": False,
            "transcription_surface_family_member_root_or_parser_role_opened": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "semantic_association_scored": False,
        },
        "next_action": (
            "Acquire a provenance-clean readable one-to-one authorial contrast or new physical-layer evidence. "
            "Use the validated structural edition only to prepare matching against that future anchor."
        ),
        "claim_ceiling": (
            "Current ordinary-image and existing human-annotation data supply no genuinely new capacity-qualified "
            "native-visual route among the frozen candidates. This is a route audit, not evidence that the manuscript "
            "is untranslatable. It establishes no word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical_bytes(payload))
    REPORT.write_text(
        "# NVA001 native-visual next-route worth audit\n\n"
        "Status: **STOP_NO_GENUINELY_NEW_CAPACITY_QUALIFIED_NATIVE_VISUAL_ROUTE**.\n\n"
        "Seven tempting continuations were checked before opening any new image body or Voynich filler. "
        "Held-star point count, leaf-margin state, and f66r marginal columns duplicate completed work. "
        "The strong exact-local relation atlas has 51 attachment loci in six units, 48 enclosure loci in ten units, "
        "and eight contact loci in six units, but zero units contain two strong relation types. The nine retracing "
        "comments contain only one strict original-feature/retracer-omission statement, f73v.15. The compact text-only "
        "`T × P` cell has four folios, but f85r1, f86v5, and human-described f1r are prose-dominant, leaving only f86v6 "
        "able to differ; a second role cannot reach two folios. Finally, zero of eleven translation-anchor registry "
        "families is currently admissible.\n\n"
        "The next translation-relevant action is evidence acquisition: a readable one-to-one authorial contrast, a "
        "new independent folio satisfying a named reopen condition, or new physical-layer/multispectral evidence. "
        "The validated structural edition can prepare matching against such evidence, but it cannot manufacture an "
        "English gloss. No word, sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "candidate_checks": len(candidate_checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
