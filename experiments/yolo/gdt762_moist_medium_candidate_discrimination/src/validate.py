#!/usr/bin/env python3
"""Validate GDT762 artifacts and a byte-identical builder replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt762_moist_medium_candidate_discrimination")
EXP = ROOT / BASE_REL
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("gdt762_builder_for_validation", RUN)


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    tables = {
        name: read_tsv(name)
        for name in builder.OUTPUT_NAMES
        if name.endswith(".tsv")
    }
    expected_rows = {
        "CANDIDATE_OCCURRENCE_ATLAS.tsv": 404,
        "STATE_PAIR_EXPOSURE.tsv": 22,
        "DIRECT_STATE_CONTACT_ATLAS.tsv": 98,
        "RADIUS2_STATE_RELAY_ATLAS.tsv": 66,
        "CANDIDATE_PAIR_CONTACT_MATRIX.tsv": 33,
        "CANDIDATE_POLARITY_SUMMARY.tsv": 3,
        "PCHEEY_EXACT_CONTEXT_ATLAS.tsv": 3,
        "CANDIDATE_DIRECT_NEIGHBOR_DECK.tsv": 306,
        "REPEATED_CANDIDATE_CONSTRUCTION_ATLAS.tsv": 5,
        "OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv": 16,
        "DIRECTED_PATTERN_NULL_CENSUS.tsv": 1571,
        "BODY_FAMILY_CONTEXT_CONTROL.tsv": 12,
        "H1_POST_MOIST_SPECIFICITY_AUDIT.tsv": 89,
        "BOUNDARY_SHELL_RIVAL_AUDIT.tsv": 16,
        "CONFOUNDER_AND_FORM_OVERLAP_AUDIT.tsv": 7,
        "SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv": 94,
        "HISTORICAL_ROLE_RIVAL_AUDIT.tsv": 27,
        "ROLE_HYPOTHESIS_SCORECARD.tsv": 14,
        "THREE_PCHEEY_WORKING_SPANS.tsv": 3,
        "THREE_CANDIDATE_WORKING_REVISION.tsv": 3,
    }
    require(result["schema"] == "GDT762_RESULT_V1", "result schema")
    require(result["status"] == builder.STATUS, "result status")
    require(set(tables) == set(expected_rows), "fixed artifact table set")
    for name, count in expected_rows.items():
        require(len(tables[name]) == count, f"row count {name}")

    occurrences = tables["CANDIDATE_OCCURRENCE_ATLAS.tsv"]
    exposure = tables["STATE_PAIR_EXPOSURE.tsv"]
    direct = tables["DIRECT_STATE_CONTACT_ATLAS.tsv"]
    radius2 = tables["RADIUS2_STATE_RELAY_ATLAS.tsv"]
    pair_matrix = tables["CANDIDATE_PAIR_CONTACT_MATRIX.tsv"]
    summaries = tables["CANDIDATE_POLARITY_SUMMARY.tsv"]
    pcheey_contexts = tables["PCHEEY_EXACT_CONTEXT_ATLAS.tsv"]
    repeated = tables["REPEATED_CANDIDATE_CONSTRUCTION_ATLAS.tsv"]
    ol_amount = tables["OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv"]
    nulls = tables["DIRECTED_PATTERN_NULL_CENSUS.tsv"]
    bodies = tables["BODY_FAMILY_CONTEXT_CONTROL.tsv"]
    h1 = tables["H1_POST_MOIST_SPECIFICITY_AUDIT.tsv"]
    boundary = tables["BOUNDARY_SHELL_RIVAL_AUDIT.tsv"]
    confounders = tables["CONFOUNDER_AND_FORM_OVERLAP_AUDIT.tsv"]
    repairs = tables["SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv"]
    historical = tables["HISTORICAL_ROLE_RIVAL_AUDIT.tsv"]
    scorecard = tables["ROLE_HYPOTHESIS_SCORECARD.tsv"]
    revisions = tables["THREE_CANDIDATE_WORKING_REVISION.tsv"]

    require(len({row["candidate_occurrence_id"] for row in occurrences}) == 404, "unique candidate ids")
    require(Counter(row["candidate_surface"] for row in occurrences) == Counter({
        "ckhy": 25, "pcheey": 3, "ol": 376,
    }), "fixed candidate recurrence")
    require(len({row["locus"] for row in occurrences}) == 366, "366 candidate loci")
    require(len({row["page"] for row in occurrences}) == 110, "110 candidate pages")
    require(len({row["physical_folio"] for row in occurrences}) == 67, "67 physical folios")
    require(Counter(
        row["candidate_line_position"] for row in occurrences
        if row["candidate_surface"] == "pcheey"
    ) == Counter({"MIDDLE": 3}), "pcheey always medial")
    require(all(row["paragraph_start_line"] == "1" for row in occurrences if row["candidate_surface"] == "pcheey"), "pcheey lines start paragraphs")

    direct_status = Counter(
        row[f"{side}_status"] for row in occurrences for side in ("l1", "r1")
    )
    radius_status = Counter(
        row[f"{side}_status"] for row in occurrences for side in ("l2", "r2")
    )
    require(direct_status == Counter({
        "ELIGIBLE": 473, "STATE": 98, "CANDIDATE": 14,
        "SUSPECT": 17, "NONEXACT": 141, "EDGE": 65,
    }), "direct slot status census")
    require(radius_status == Counter({
        "ELIGIBLE": 408, "STATE": 66, "CANDIDATE": 16,
        "SUSPECT": 11, "NONEXACT": 131, "EDGE": 176,
    }), "radius-two slot status census")
    target_contacts = [
        (row["candidate_surface"], row[f"{side}_surface"])
        for row in occurrences for side in ("l2", "l1", "r1", "r2")
        if row[f"{side}_status"] == "CANDIDATE"
    ]
    require(set(target_contacts) == {("ol", "ol")}, "all target-target contacts are ol-to-ol")

    expected_exposure = {
        "cho": 45, "sho": 93, "chy": 114, "shy": 67, "chey": 282,
        "shey": 179, "cheey": 137, "sheey": 105, "chdy": 89, "shdy": 25,
        "chedy": 296, "shedy": 219, "cheedy": 39, "sheedy": 41,
        "chol": 303, "shol": 146, "cheol": 118, "sheol": 71,
        "cheor": 56, "sheor": 31, "cheo": 36, "sheo": 28,
    }
    require({row["surface"]: int(row["reader_exact_occurrences"]) for row in exposure} == expected_exposure, "fixed 11-pair exposure")
    require(sum(int(row["reader_exact_occurrences"]) for row in exposure if row["polarity"] == "DRY") == 1515, "dry-side exposure")
    require(sum(int(row["reader_exact_occurrences"]) for row in exposure if row["polarity"] == "MOIST") == 1005, "moist-side exposure")
    require(all(row["pair_side_epistemic_status"] == "WORKING_PAIR_SIDE_NOT_CONFIRMED_LEXEME" for row in exposure), "pair sides stay working labels")
    sho = next(row for row in exposure if row["surface"] == "sho")
    require(sho["pair_asymmetry_caveat"] == "SHO_LINE_INITIAL_BIASED_27_OF_93_VS_CHO_1_OF_45", "sho position caveat")

    require(len({row["contact_id"] for row in direct}) == 98, "unique direct contact ids")
    require(len({row["contact_id"] for row in radius2}) == 66, "unique radius-two ids")
    summary = {row["candidate_surface"]: row for row in summaries}
    expected_profiles = {
        "ckhy": (25, 1, 2, 1, 3),
        "pcheey": (3, 0, 3, 0, 0),
        "ol": (376, 58, 34, 37, 25),
    }
    for surface, expected in expected_profiles.items():
        row = summary[surface]
        actual = tuple(int(row[field]) for field in (
            "reader_exact_occurrences", "direct_dry_edges", "direct_moist_edges",
            "radius2_dry_relays", "radius2_moist_relays",
        ))
        require(actual == expected, f"candidate profile {surface}")
        require(row["specific_water_selected"] == "0", f"no water {surface}")
        require(row["specific_wine_selected"] == "0", f"no wine {surface}")
        require(row["specific_oil_selected"] == "0", f"no oil {surface}")
        require(row["component_export_credit"] == "0", f"no component {surface}")
    require(summary["ol"]["moist_to_dry_normalized_rate_ratio"] == "0.883685", "ol nearly neutral polarity")
    require(summary["pcheey"]["decision"] == "SELECT_POST_MOIST_FORM_II_RECORD_FIELD__C1_SOURCE_RIVAL", "pcheey decision")
    require(len(pair_matrix) == 3 * 11, "complete candidate-by-pair matrix")

    require({row["locus"] for row in pcheey_contexts} == {"f8r.9", "f10v.1", "f105r.24"}, "three pcheey loci")
    require(Counter(row["l1_surface"] for row in pcheey_contexts) == Counter({"sheo": 2, "sho": 1}), "three post-moist predecessors")
    require(all(row["multiple_h1_record_forms_on_line"] == "1" for row in pcheey_contexts), "all pcheey lines contain multiple H1 forms")
    require(Counter(int(row["exact_h1_record_form_count_on_line"]) for row in pcheey_contexts) == Counter({2: 2, 3: 1}), "pcheey H1 line counts")
    require(all(row["working_phrase_relation"] == "POST_MOIST_FORM_II_RECORD_FIELD" for row in pcheey_contexts), "pcheey structural renderer")
    require(all(row["conditional_working_phrase_license"] == "1" for row in pcheey_contexts), "three local pcheey licenses")
    require(all(row["confirmed_plaintext"] == "0" for row in pcheey_contexts), "pcheey is not plaintext")

    pcheey_null = next(row for row in nulls if row["surface"] == "pcheey")
    require(pcheey_null["all_occurrences_after_sho_or_sheo"] == "1", "pcheey full predecessor coverage")
    require([row["surface"] for row in nulls if row["all_occurrences_after_sho_or_sheo"] == "1"] == ["pcheey"], "pcheey unique in recurrent universe")
    require(sum(int(row["exact_n3_cohort"]) for row in nulls) == 235, "N3 null cohort")
    require(sum(int(row["n3_pages3_all_middle_selection_matched"]) for row in nulls) == 91, "selection-matched null cohort")
    require(sum(int(row["n2_to_n4_cohort"]) for row in nulls) == 929, "N2-N4 null cohort")

    body_map = {row["whole_surface"]: row for row in bodies}
    require((body_map["pchey"]["reader_exact_occurrences"], body_map["pchy"]["reader_exact_occurrences"]) == ("6", "1"), "dry-body controls 6 plus 1")
    require(body_map["pchey"]["left_sho_or_sheo_contacts"] == "0" and body_map["pchy"]["left_sho_or_sheo_contacts"] == "0", "dry-body controls have no post-moist contacts")
    require(sum(int(row["reader_exact_occurrences"]) for row in h1) == 199, "199 H1 occurrences")
    require(sum(int(row["left_sho_or_sheo_contacts"]) for row in h1) == 3, "three exact H1 post-moist contacts")
    require(sum(int(row["left_sho_or_sheo_contacts"]) for row in h1 if row["surface"] != "pcheey") == 0, "all other H1 forms zero")
    require(all(row["eva_p_letter_or_semantic_credit"] == "0" for row in h1), "EVA p has no semantic credit")

    repeated_map = {row["written_pattern_eva"]: row for row in repeated}
    require(repeated_map["daiin ckhy"]["reader_exact_occurrences"] == "3", "daiin ckhy repeats three times")
    require(repeated_map["sheo pcheey"]["reader_exact_occurrences"] == "2", "sheo pcheey repeats twice")
    require(repeated_map["sho pcheey"]["reader_exact_occurrences"] == "1", "sho pcheey outer replication")
    require(repeated_map["ol s aiin"]["reader_exact_occurrences"] == "4", "ol s aiin repeats four times")
    require(repeated_map["sheo pcheey X daiin"]["reader_exact_occurrences"] == "2", "gapped pcheey-value frame repeats")

    require(sum(int(row["ol_directed_edges"]) for row in ol_amount) == 17, "17 ol amount edges")
    require(len({row["page"] for row in ol_amount}) == 13, "13 ol amount pages")
    require(Counter(row["decision"] for row in ol_amount) == Counter({
        "EXACT_AMOUNT_CONTENT_PHRASE_LICENSE": 8,
        "BILATERAL_AMBIGUOUS_CONTACT": 1,
        "CONTACT_SUPPORT_ONLY_NONPREFERRED_SIDE": 7,
    }), "ol amount dispatch")
    require(sum(int(row["conditional_phrase_license"]) for row in ol_amount) == 8, "eight ol amount licenses")
    f94 = next(row for row in ol_amount if row["locus"] == "f94v.9")
    require(f94["extended_working_phrase_de"] == "Ansatzstoff: drei Drachmen; abseihen", "f94v local working phrase")
    bilateral = next(row for row in ol_amount if row["decision"] == "BILATERAL_AMBIGUOUS_CONTACT")
    require("ol s aiin ol" in bilateral["written_line_eva"], "bilateral ol amount remains explicit")
    require(all(row["specific_medium_selected"] == "0" for row in ol_amount), "ol amount does not name a medium")

    boundary_map = {row["surface_or_span"]: row for row in boundary}
    require((boundary_map["sheo pcheey"]["reader_exact_occurrences"], boundary_map["sho pcheey"]["reader_exact_occurrences"]) == ("2", "1"), "spaced moist construction counts")
    require(boundary_map["cho pcheey"]["reader_exact_occurrences"] == "0" and boundary_map["cheo pcheey"]["reader_exact_occurrences"] == "0", "dry spaced controls absent")
    require(all(boundary_map[surface]["reader_exact_occurrences"] == "0" for surface in ("shopcheey", "sheopcheey", "chopcheey", "cheopcheey")), "exact-body fused forms absent")
    require((boundary_map["opcheey"]["reader_exact_occurrences"], boundary_map["qopcheey"]["reader_exact_occurrences"]) == ("4", "4"), "O/QO shell rivals")

    confound = {row["surface"]: row for row in confounders}
    require((confound["shor"]["direct_dry_edges_all11"], confound["shor"]["direct_moist_edges_all11"]) == ("0", "12"), "shor moist pseudopositive")
    require(confound["shor"]["naive_moist_selectivity_pseudopositive"] == "1", "shor confound flag")
    require((confound["chor"]["direct_dry_edges_all11"], confound["chor"]["direct_moist_edges_all11"]) == ("29", "7"), "chor dry pseudopositive")
    require((confound["daiin"]["direct_dry_edges_all11"], confound["daiin"]["direct_moist_edges_all11"]) == ("90", "42"), "amount control broad contacts")

    require(len(repairs) == 94, "94 structural precedence repairs")
    require(sum(int(row["old_literal_head_noun_detected"]) for row in repairs) == 94, "all repaired rows carried retired head nouns")
    repair_map = {row["surface"]: row for row in repairs}
    require(repair_map["pchey"]["inherited_gdt734_candidate_de"] == "Pulver, trocken gebunden, Form I", "pchey old leak recorded")
    require(repair_map["pchey"]["repaired_structural_candidate_de"] == "H1-Ganzform im Feld „trockene Form I“; genaue Bedeutung offen", "pchey repaired")
    require(repair_map["paiin"]["inherited_gdt734_candidate_de"] == "Pulver, Charge III", "paiin old leak recorded")
    require(repair_map["paiin"]["repaired_structural_candidate_de"] == "H1-Ganzform im Feld „Ordinalstufe III“; genaue Bedeutung offen", "paiin repaired")
    for row in occurrences:
        require(not row["page"].startswith("f84"), f"sealed page absent {row['candidate_occurrence_id']}")
        for side in ("l2", "l1", "r1", "r2"):
            if row[f"{side}_semantic_source"] == "GDT736_FORMAL_ROLE_REPAIR_NO_HEAD_NOUN":
                semantic = row[f"{side}_semantic_candidate_de"].lower()
                require(not any(term in semantic for term in ("pulver", "samen", "saat", "wurzel", "holz")), f"retired noun absent {row['candidate_occurrence_id']} {side}")

    require(Counter(row["surface"] for row in historical) == Counter({"ckhy": 9, "pcheey": 9, "ol": 9}), "historical deck 9 per target")
    require(all(row["eva_spelling_match_credit"] == "0" for row in historical), "no EVA-Latin spelling match")
    require(all(row["target_assignment_credit"] == "0" for row in historical), "historical categories name no target")
    require(all(row["confirmed_lexeme"] == "0" for row in historical), "historical audit confirms no lexeme")
    ol_media = [row for row in historical if row["surface"] == "ol" and row["historical_candidate_id"] in {"E028", "E029", "E030"}]
    require(all(row["decision"] == "LIVE_SPECIFIC_MEDIUM_RIVAL__LIQUID_AXIS_MISSING" for row in ol_media), "ol media rivals remain unselected")

    score = {(row["surface"], row["hypothesis_role"]): row for row in scorecard}
    require(score[("pcheey", "RECORD_FORM_FIELD")]["rank_within_candidate"] == "1", "pcheey record field first")
    require(score[("pcheey", "DRY_SOURCE_OR_COMPLEMENT")]["rank_within_candidate"] == "2", "pcheey dry source second")
    require(score[("ol", "GENERAL_PREPARATION_OR_CARRIER")]["rank_within_candidate"] == "1", "ol carrier first")
    require(all(row["specific_medium_identity_selected"] == "0" for row in scorecard), "scorecard selects no medium")
    revision = {row["surface"]: row for row in revisions}
    require(revision["pcheey"]["new_role"] == "POST_MOIST_FORM_II_RECORD_FIELD__C1_DRY_SOURCE_RIVAL", "pcheey revised role")
    require(revision["ol"]["new_role"] == "QUANTITY_BEARING_PREPARATION_OR_CONTENT_CARRIER", "ol revised role")
    require(all(row["global_component_export_allowed"] == "0" for row in revisions), "no global component export")

    forbidden_filler = ("Arbeitsgut", "Arbeitschritt", "Arbeitsmaterial")
    for rows in tables.values():
        for row in rows:
            text = " ".join(row.values())
            require(not any(term in text for term in forbidden_filler), "no generic work filler")

    require(result["scope"]["candidate_occurrences"] == 404, "result candidate count")
    require(result["scope"]["state_reader_exact_occurrences"] == 2520, "result state count")
    require(result["scope"]["semantic_precedence_repairs"] == 94, "result repair count")
    require(result["neighbor_slot_status"]["direct_clean_exact_including_candidate_targets"] == 585, "result direct clean slots")
    require(result["neighbor_slot_status"]["direct_score_eligible_excluding_candidate_targets"] == 571, "result direct scoring slots")
    require(result["neighbor_slot_status"]["radius2_clean_exact_including_candidate_targets"] == 490, "result radius clean slots")
    require(result["neighbor_slot_status"]["radius2_score_eligible_excluding_candidate_targets"] == 474, "result radius scoring slots")
    require(result["pcheey_result"]["selected_construction_role"] == "POST_MOIST_FORM_II_RECORD_FIELD", "result pcheey role")
    require(result["pcheey_result"]["all_three_lines_have_multiple_h1_record_forms"] is True, "result pcheey line ecology")
    require(result["ol_result"]["exact_amount_content_phrase_licenses"] == 8, "result ol licenses")
    require(result["medium_result"]["specific_medium_selected"] == 0, "result no medium")
    require(result["semantic_quarantine"] == {
        "active_suspect_surface_union": 237,
        "gdt736_training_form_neutral_repairs": 94,
        "gdt737_retired_head_surfaces": 80,
        "gdt738_retired_salt_surfaces": 2,
        "gdt754_source_composed_surfaces": 172,
        "later_repaired_surface_exemptions": 147,
    }, "semantic quarantine and repair summary")
    require(result["guard"]["inherited_token_query"] == {
        "selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150,
    }, "inherited guarded query")
    require(result["claim_boundary"] == {
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "confirmed_solvents": 0, "confirmed_material_identities": 0,
        "component_values": 0, "new_pages": 0, "new_images": 0,
        "f84_accessed": False, "f84r_accessed": False,
    }, "claim boundary")

    with tempfile.TemporaryDirectory(prefix="gdt762_replay_") as temp:
        replay_dir = Path(temp)
        replay_result = builder.build(replay_dir)
        require(replay_result == result, "replayed result object")
        for name in builder.OUTPUT_NAMES:
            require((replay_dir / name).is_file(), f"replay output exists {name}")
            require(digest(replay_dir / name) == digest(ART / name), f"byte replay {name}")

    validation = {
        "schema": "GDT762_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "byte_identical_replay": True,
        "scope": result["scope"],
        "pcheey_result": result["pcheey_result"],
        "ckhy_result": result["ckhy_result"],
        "ol_result": result["ol_result"],
        "medium_result": result["medium_result"],
        "claim_ceiling": (
            "GDT762 selects a reproducible pcheey post-moist Form-II record-field "
            "construction, retains a C1 dry-source reading on the three exact spans, "
            "and promotes ol only to a quantity-bearing preparation/content carrier. "
            "It identifies no water, wine, oil, lexeme, component value, or plaintext clause."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
