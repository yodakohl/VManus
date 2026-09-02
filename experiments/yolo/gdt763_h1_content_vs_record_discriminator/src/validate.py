#!/usr/bin/env python3
"""Validate GDT763 artifacts and a byte-identical builder replay."""

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
BASE_REL = Path("experiments/yolo/gdt763_h1_content_vs_record_discriminator")
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


builder = load_module("gdt763_builder_for_validation", RUN)


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
    tables = {name: read_tsv(name) for name in builder.OUTPUT_NAMES if name.endswith(".tsv")}
    expected_rows = {
        "H1_199_OCCURRENCE_SEQUENCE_ATLAS.tsv": 199,
        "H1_PARAGRAPH_MEDIAL_R1_R3_PROFILE.tsv": 4,
        "H1_CLASS_STATE_PREDECESSOR_PROFILE.tsv": 4,
        "PCHEEY_3_FIELD_FRAME.tsv": 3,
        "GAPPED_DAIIN_FRAME_COHORT.tsv": 3,
        "GAPPED_DAIIN_FRAME_HITS.tsv": 6,
        "STRICT_N3_PARAGRAPH_MEDIAL_CONTROL.tsv": 11,
        "PCHEEY_HYPOTHESIS_SCORECARD.tsv": 4,
        "OL_16_SLOT_FUNCTION_ATLAS.tsv": 16,
        "OL_18_MATCHED_CONTENT_COMPARATORS.tsv": 18,
        "OL_CONTENT_CLASS_PLACEMENT_COMPARISON.tsv": 3,
        "OL_AMOUNT_FORMULA_RECURRENCE.tsv": 5,
        "HISTORICAL_FIELD_FUNCTION_COMPARISON.tsv": 8,
        "TWO_WHOLE_RENDERER_REVISION.tsv": 2,
    }
    require(result["schema"] == "GDT763_RESULT_V1", "result schema")
    require(result["status"] == builder.STATUS, "result status")
    require(set(tables) == set(expected_rows), "fixed artifact table set")
    for name, count in expected_rows.items():
        require(len(tables[name]) == count, f"row count {name}")

    h1 = tables["H1_199_OCCURRENCE_SEQUENCE_ATLAS.tsv"]
    profile = tables["H1_PARAGRAPH_MEDIAL_R1_R3_PROFILE.tsv"]
    state = tables["H1_CLASS_STATE_PREDECESSOR_PROFILE.tsv"]
    frames = tables["PCHEEY_3_FIELD_FRAME.tsv"]
    gapped = tables["GAPPED_DAIIN_FRAME_COHORT.tsv"]
    hits = tables["GAPPED_DAIIN_FRAME_HITS.tsv"]
    controls = tables["STRICT_N3_PARAGRAPH_MEDIAL_CONTROL.tsv"]
    scorecard = tables["PCHEEY_HYPOTHESIS_SCORECARD.tsv"]
    ol = tables["OL_16_SLOT_FUNCTION_ATLAS.tsv"]
    comparators = tables["OL_18_MATCHED_CONTENT_COMPARATORS.tsv"]
    placement = tables["OL_CONTENT_CLASS_PLACEMENT_COMPARISON.tsv"]
    formulas = tables["OL_AMOUNT_FORMULA_RECURRENCE.tsv"]
    history = tables["HISTORICAL_FIELD_FUNCTION_COMPARISON.tsv"]
    revisions = tables["TWO_WHOLE_RENDERER_REVISION.tsv"]

    require(len({row["h1_occurrence_id"] for row in h1}) == 199, "unique H1 ids")
    require(len({row["surface"] for row in h1}) == 68, "68 observed H1 surfaces")
    require(len({row["page"] for row in h1}) == 82, "82 H1 pages")
    require(len({row["locus"] for row in h1}) == 183, "183 H1 loci")
    require(Counter(row["registry_source"] for row in h1) == Counter({"GDT736_TRAINING": 95, "GDT737_HELD": 104}), "training/held occurrence split")
    require(Counter(row["line_position"] for row in h1) == Counter({"FIRST": 125, "MIDDLE": 71, "LAST": 3}), "H1 line positions")
    require(sum(row["paragraph_start_line"] == "1" for row in h1) == 157, "H1 paragraph-start count")
    expected_slot_status = {
        "r1": Counter({"CLEAN": 149, "NONEXACT": 40, "QUARANTINED": 7, "EDGE": 3}),
        "r2": Counter({"CLEAN": 143, "NONEXACT": 36, "QUARANTINED": 7, "EDGE": 13}),
        "r3": Counter({"CLEAN": 137, "NONEXACT": 30, "QUARANTINED": 5, "EDGE": 27}),
    }
    for slot, expected in expected_slot_status.items():
        require(Counter(row[slot + "_status"] for row in h1) == expected, f"{slot} status census")
    for row in h1:
        require(row["component_export_credit"] == "0", f"no component export {row['h1_occurrence_id']}")
        require(not row["page"].startswith("f84"), f"sealed page absent {row['h1_occurrence_id']}")
        for slot in ("l3", "l2", "l1", "r1", "r2", "r3", "r4", "r5"):
            semantic = row[slot + "_semantic_candidate_de"].lower()
            require(not any(term in semantic for term in ("pulver", "samen", "saat", "wurzel", "holz")), f"retired literal display guard {row['h1_occurrence_id']} {slot}")
            if row[slot + "_status"] == "NONEXACT":
                require(row[slot + "_semantic_candidate_de"] == "NONEXACT_UNSCORED", f"nonexact semantic blocked {row['h1_occurrence_id']} {slot}")

    target = [row for row in h1 if row["surface"] == "pcheey"]
    require(len(target) == 3, "three pcheey occurrences")
    require({row["locus"] for row in target} == {"f8r.9", "f10v.1", "f105r.24"}, "pcheey loci")
    require(Counter(row["l1_surface"] for row in target) == Counter({"sheo": 2, "sho": 1}), "pcheey predecessors")
    require(all(row["line_position"] == "MIDDLE" and row["paragraph_start_line"] == "1" for row in target), "pcheey matched geometry")
    require(all(int(row["h1_count_on_line"]) >= 2 for row in target), "pcheey multi-H1 lines")
    require(sum(int(row["right3_any_content"]) for row in target) == 3, "pcheey right content fields")
    require(sum(int(row["right3_any_quality"]) for row in target) == 2, "pcheey right quality fields")
    require(sum(int(row["right3_any_scalar"]) for row in target) == 2, "pcheey right scalar fields")
    require(sum(int(row["gapped_x_daiin"]) for row in target) == 2, "two pcheey X daiin")
    require(sum(int(row["plusminus3_any_process_pass_close"]) for row in target) == 0, "no target result signature")
    require(sum(row["line_position"] == "LAST" for row in target) == 0, "no target line-final")
    require(sum(row["paragraph_end_line"] == "1" for row in target) == 0, "no target paragraph-end")
    require(Counter(row["remaining_tokens_right"] for row in target) == Counter({"5": 2, "3": 1}), "target remaining tokens")

    profile_map = {row["cohort_id"]: row for row in profile}
    require(profile_map["PCHEEY_TARGET"]["occurrences"] == "3", "target profile count")
    require(profile_map["OTHER_H1_POSITION_MATCHED"]["occurrences"] == "49", "49 matched controls")
    require(profile_map["ALL_H1_POSITION_MATCHED"]["occurrences"] == "52", "52 matched total")
    require(profile_map["OTHER_H1_POSITION_MATCHED"]["multi_h1_line_occurrences"] == "15", "matched control multi-H1")
    require(profile_map["PCHEEY_TARGET"]["multi_h1_line_occurrences"] == "3", "target multi-H1")

    state_map = {row["opaque_head_id"]: row for row in state}
    expected_state = {"H1": (6, 12, "2.939086"), "H2": (19, 7, "0.541411"), "H3": (18, 3, "0.244924"), "H4": (61, 20, "0.481817")}
    for head, expected in expected_state.items():
        row = state_map[head]
        require((int(row["immediately_after_dry_state"]), int(row["immediately_after_moist_state"]), row["normalized_moist_to_dry_rate_ratio"]) == expected, f"state profile {head}")
        require(row["dry_state_right_opportunities"] == "1158" and row["moist_state_right_opportunities"] == "788", f"state opportunities {head}")
        require(row["component_export_credit"] == "0", f"state no component {head}")

    require({row["frame_id"] for row in frames} == {"G763-P01", "G763-P02", "G763-P03"}, "frame ids")
    require(Counter(row["gapped_pcheey_x_daiin"] for row in frames) == Counter({"1": 2, "0": 1}), "frame X daiin")
    require(all(row["result_renderer_de"].startswith("NOT_LICENSED") for row in frames), "result renderer blocked")
    require(all(row["confirmed_plaintext"] == "0" and row["component_export_credit"] == "0" for row in frames), "frame claim ceiling")

    gapped_map = {row["cohort"]: row for row in gapped}
    require((gapped_map["PCHEEY"]["x_daiin_hits"], gapped_map["PCHEEY"]["occurrences"]) == ("2", "3"), "pcheey gapped cohort")
    require((gapped_map["OTHER_H1"]["x_daiin_hits"], gapped_map["OTHER_H1"]["occurrences"]) == ("3", "196"), "other H1 gapped cohort")
    require((gapped_map["STRICT_NON_H1_CONTROL"]["surfaces_with_any_hit"], gapped_map["STRICT_NON_H1_CONTROL"]["candidate_surfaces"], gapped_map["STRICT_NON_H1_CONTROL"]["occurrences"]) == ("1", "11", "33"), "strict control gapped cohort")
    expected_hits = {
        ("pcheey", "f10v.1", "qoty"), ("pcheey", "f105r.24", "dal"),
        ("pchaiin", "f22r.4", "ofchy"), ("pcheody", "f99r.15", "oteody"),
        ("pchedal", "f105v.5", "qopchdy"), ("chopy", "f102r1.8", "chofol"),
    }
    require({(row["surface"], row["locus"], row["intervening_surface"]) for row in hits} == expected_hits, "complete X daiin hits")
    require({row["surface"] for row in controls} == {"chefchy", "chopy", "cphar", "ofchey", "opchal", "opcheedy", "orair", "qop", "ypar", "ypchol", "ypchy"}, "strict control surfaces")
    require(sum(int(row["has_any_x_daiin"]) for row in controls) == 1, "one control surface hit")

    decisions = {row["hypothesis_role"]: row["decision"] for row in scorecard}
    require(decisions["PARALLEL_RECORD_FIELD"] == "SELECT_PORTABLE_STRUCTURAL_CORE", "record role selected")
    require(decisions["FIELD_BEARING_DRY_PREPARATION_HEAD"] == "SELECT_COMPOSITE_WITH_RECORD_ROLE", "content head selected")
    require(decisions["DRY_SOURCE_OR_COMPLEMENT"] == "RETAIN_C1_EXACT_SPAN_RIVAL", "source rival retained")
    require(decisions["POST_MOIST_RESULT"] == "DOWNGRADE_WEAKEST_RIVAL", "result downgraded")
    require(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in scorecard), "scorecard claim ceiling")

    require(len({row["ol_slot_id"] for row in ol}) == 16, "unique ol slot ids")
    require(Counter(row["selected_slot_function"] for row in ol) == Counter({"HEAD": 9, "OBJECT_PATIENT": 1, "CONTEXT_SECOND_FIELD": 5, "BILATERAL_AMBIGUOUS": 1}), "ol dispatch counts")
    expected_dispatch = {
        "HEAD": {"G762-A01", "G762-A02", "G762-A03", "G762-A04", "G762-A06", "G762-A10", "G762-A11", "G762-A13", "G762-A15"},
        "OBJECT_PATIENT": {"G762-A16"}, "CONTEXT_SECOND_FIELD": {"G762-A05", "G762-A07", "G762-A08", "G762-A09", "G762-A14"},
        "BILATERAL_AMBIGUOUS": {"G762-A12"},
    }
    for role, identifiers in expected_dispatch.items():
        require({row["source_contact_id"] for row in ol if row["selected_slot_function"] == role} == identifiers, f"ol identity set {role}")
    a16 = next(row for row in ol if row["source_contact_id"] == "G762-A16")
    require((a16["outside_span_surface"], a16["outside_span_reader_exact"], a16["outside_span_axis_class"]) == ("oly", "1", "PROCESS_CLOSE"), "A16 exact process follower")
    require(a16["working_phrase_de"] == "drei Drachmen Ansatz/Zubereitung; abseihen", "A16 concrete renderer")
    a06 = next(row for row in ol if row["source_contact_id"] == "G762-A06")
    require((a06["outside_span_surface"], a06["outside_span_reader_exact"]) == ("shee", "0"), "A06 nonexact process lookalike blocked")
    require(all(row["source_relation_marker"] == "NONE" for row in ol), "zero source markers")
    require(all(row["specific_oil_identity"] == "0" and row["confirmed_plaintext"] == "0" and row["component_export_credit"] == "0" for row in ol), "ol claim ceiling")
    require(all(not row["page"].startswith("f84") for row in ol), "ol sealed page absent")

    require(Counter((row["expression_line_position"], row["content_side"], row["content_role_label_de"]) for row in comparators) == Counter({("MIDDLE", "R", "Zubereitung"): 9, ("FIRST", "R", "Stoff"): 5, ("FIRST", "R", "Zubereitung"): 4}), "18 matched content comparators")
    require(all(row["position_condition_agreement"] == "0" for row in comparators if row["expression_line_position"] == "MIDDLE"), "nine nonpreferred preparation controls")
    placement_map = {row["comparison_class"]: row for row in placement}
    require((placement_map["Stoff"]["expected_side_contacts"], placement_map["Stoff"]["nonexpected_side_contacts"]) == ("16", "1"), "material placement")
    require((placement_map["Zubereitung"]["expected_side_contacts"], placement_map["Zubereitung"]["nonexpected_side_contacts"]) == ("14", "10"), "preparation placement")
    require((placement_map["Stoff/Zubereitung"]["expected_side_contacts"], placement_map["Stoff/Zubereitung"]["nonexpected_side_contacts"]) == ("4", "0"), "mixed placement")
    require(placement_map["Stoff"]["ol_vs_class_odds_ratio"] == "0.071429" and placement_map["Stoff"]["ol_vs_class_fisher_two_sided"] == "0.013323", "ol vs material diagnostic")
    require(placement_map["Zubereitung"]["ol_vs_class_odds_ratio"] == "0.816327" and placement_map["Zubereitung"]["ol_vs_class_fisher_two_sided"] == "1.000000", "ol vs preparation diagnostic")
    require([(row["pattern_eva"], row["reader_exact_amount_contact_positions"]) for row in formulas] == [("ol s aiin", "4"), ("sain ol", "4"), ("saiin ol", "2"), ("or aiin ol", "2"), ("ols + aiin|aiiin", "3")], "formula recurrence")
    require(formulas[-1]["counterevidence"].startswith("ols hat 12 exakte Vorkommen"), "ols whole control")

    require({row["historical_item_id"] for row in history} == {"HEO005", "HEO006", "HEO011", "E020", "E022", "E028", "E036", "E043"}, "historical comparator set")
    require(all(row["target_assignment_credit"] == "0" and row["eva_spelling_credit"] == "0" and row["confirmed_lexeme"] == "0" for row in history), "historical analogy only")
    revision_map = {row["surface"]: row for row in revisions}
    require(set(revision_map) == {"pcheey", "ol"}, "two renderer revisions")
    require(revision_map["pcheey"]["role"] == "FIELD_BEARING_RECORD_CONTENT_HEAD", "pcheey revised role")
    require(revision_map["ol"]["role"] == "QUANTIFIABLE_PREPARATION_CONTENT_HEAD_WITH_CONTEXT_USES", "ol revised role")
    require(all(row["global_identity_selected"] == "0" and row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in revisions), "revision claim ceiling")

    require(result["scope"]["h1_reader_exact_occurrences"] == 199, "result H1 count")
    require(result["scope"]["paragraph_start_medial_h1_occurrences"] == 52, "result matched H1 count")
    require(result["pcheey_result"]["selected_role"] == "FIELD_BEARING_FORM_II_RECORD_CONTENT_HEAD", "result pcheey role")
    require(result["pcheey_result"]["result_relation"] == "DOWNGRADED_WEAKEST_RIVAL", "result target result rival")
    require(result["ol_result"]["slot_dispatch"] == {"BILATERAL_AMBIGUOUS": 1, "CONTEXT_SECOND_FIELD": 5, "HEAD": 9, "OBJECT_PATIENT": 1}, "result ol dispatch")
    require(result["ol_result"]["source_markers"] == 0, "result zero source marker")
    require(result["claim_boundary"] == {"component_values": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_substances": 0, "confirmed_syntax_relations": 0, "confirmed_units": 0, "f84_accessed": False, "f84r_accessed": False, "new_images": 0, "new_pages": 0}, "result claim boundary")
    require(result["guard"]["inherited_token_query"]["skipped_forbidden"] == 98, "guard retained forbidden-row rejection")

    with tempfile.TemporaryDirectory(prefix="gdt763-replay-") as temp_name:
        replay = Path(temp_name)
        replay_result = builder.build(replay)
        require(replay_result == result, "builder replay result equality")
        for name in builder.OUTPUT_NAMES:
            require(digest(replay / name) == digest(ART / name), f"byte replay {name}")

    validation = {
        "schema": "GDT763_VALIDATION_V1", "status": "PASS", "checks": checks,
        "artifact_tables": len(expected_rows), "byte_identical_outputs": len(builder.OUTPUT_NAMES),
        "relation_packet_status": "NOT_APPLICABLE_NO_NEW_SCORE_READY_EDGE_PACKET",
        "sealed_f84": "FORBIDDEN_NOT_ACCESSED", "sealed_f84r": "FORBIDDEN_NOT_ACCESSED",
        "new_pages": 0, "confirmed_lexemes": 0, "component_exports": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
