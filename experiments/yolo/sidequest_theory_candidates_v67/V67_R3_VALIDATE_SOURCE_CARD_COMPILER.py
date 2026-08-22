#!/usr/bin/env python3
"""Validate the V67 R3 source-to-card compiler release."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
BUILDER = HERE / "V67_R3_BUILD_SOURCE_CARD_COMPILER.py"

SOURCE_EVENTS = YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_STATEMENTS = YOLO / "sidequest_theory_candidates_v61" / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_REGISTERS = YOLO / "sidequest_theory_candidates_v62" / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
SOURCE_FIELDS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
SOURCE_ASTRO = YOLO / "sidequest_theory_candidates_v66" / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv"

FILES = {
    "audit": (HERE / "V67_R3_776_GROUP_ROUNDTRIP_AUDIT.tsv", 776),
    "clauses": (HERE / "V67_R3_116_TYPED_SOURCE_CLAUSES.tsv", 116),
    "runtime": (HERE / "V67_R3_116_RUNTIME_REGISTER_TRANSITIONS.tsv", 116),
    "automaton": (HERE / "V67_R3_COMPILER_TRANSITIONS.tsv", 22),
    "units": (HERE / "V67_R3_14_UNIT_SUMMARY.tsv", 14),
    "traces": (HERE / "V67_R3_LONG_TRACE_STEPS.tsv", 107),
    "models": (HERE / "V67_R3_STATE_CODEBOOK_COMPARISON.tsv", 12),
    "order": (HERE / "V67_R3_2_ABSTRACT_ORDER_MODELS.tsv", 2),
    "errors": (HERE / "V67_R3_ERROR_AUDIT.tsv", 14),
}

PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    data = {name: read_tsv(path) for name, (path, _) in FILES.items()}
    for name, (_, expected) in FILES.items():
        require(len(data[name]) == expected, f"{name}: expected {expected}, got {len(data[name])}")

    source_events = read_tsv(SOURCE_EVENTS)
    source_statements = read_tsv(SOURCE_STATEMENTS)
    source_registers = read_tsv(SOURCE_REGISTERS)
    source_fields = read_tsv(SOURCE_FIELDS)
    source_astro = read_tsv(SOURCE_ASTRO)
    require((len(source_events), len(source_statements), len(source_registers), len(source_fields), len(source_astro)) == (381, 116, 116, 135, 395), "source count drift")
    require({row["page"] for row in source_events} == PROSE_PAGES, "prose page scope")
    require({row["page"] for row in source_astro} == ASTRO_PAGES, "Astro page scope")

    audit = data["audit"]
    require([int(row["combined_group_ordinal"]) for row in audit] == list(range(1, 777)), "combined ordinal sequence")
    require(Counter(row["namespace"] for row in audit) == Counter({"PROSE_EXACT_JOINT_CARD": 381, "ASTRO_PAGE_LOCAL_GROUP": 395}), "namespace counts")
    require({row["page"] for row in audit} == PROSE_PAGES | ASTRO_PAGES, "new page in output")
    require(all(row["formal_identity_order_layout_roundtrip"] == "PASS" for row in audit), "formal roundtrip failure")
    require(all(row["source_intention_with_exemplar"] == "PASS_SELECTED_LOCAL_PAYLOAD" for row in audit), "exemplar roundtrip failure")
    require(all(row["external_exemplar_required_for_complete_source"] == "YES" for row in audit), "hidden standalone source recovery")
    require(all(row["external_source_payload"] for row in audit), "missing local payload")

    prose_audit = audit[:381]
    astro_audit = audit[381:]
    require(Counter(row["compiler_channel"] for row in prose_audit) == Counter({
        "EXEMPLAR_WHOLE_CARD": 262,
        "EXACT_MNEMONIC": 74,
        "STRICT_FORMAL_PROMPT": 34,
        "EXACT_MNEMONIC_PLUS_FORMAL_CONVERGENT": 11,
    }), "prose channel counts")
    require(all(row["compiler_channel"] == "ASTRO_LOCAL_FORMAL_EXEMPLAR" for row in astro_audit), "Astro imported prose prompt")
    require(sum(row["field_grouping_operation"] == "CLOSE_AND_COMMIT" for row in prose_audit) == 90, "terminal close count")
    require(sum(row["field_grouping_operation"] == "OPEN_FIELD_CUT" for row in prose_audit) == 45, "open field count")
    require(sum(row["line_reflow_operation"] == "LINE_RESET" for row in prose_audit) == 57, "prose locus reset count")
    require(sum(row["line_reflow_operation"] == "LOCUS_RESET" for row in astro_audit) == 142, "Astro locus reset count")
    require(sum(row["id_to_surface_encode_status"] == "EXTERNAL_OCCURRENCE_RENDERER_SELECTOR_REQUIRED" for row in prose_audit) == 202, "renderer selector count")
    require(sum(row["surface_to_id_decode_status"] == "AMBIGUOUS_WITHOUT_LOCAL_ADDRESS" for row in astro_audit) == 140, "Astro surface ambiguity count")

    event_by_serial = {row["event_serial"]: row for row in source_events}
    require(set(event_by_serial) == {str(i) for i in range(1, 382)}, "source event serials")
    for row in prose_audit:
        source = event_by_serial[row["combined_group_ordinal"]]
        require(row["unit_id"] == source["record_unit_id"], "prose unit projection")
        require(row["page"] == source["page"] and row["source_locus"] == source["locus"], "prose layout projection")
        require(row["field_or_local_address"] == source["field_id"], "field projection")
        require(row["opaque_whole_card_key"] == "P:" + source["joint_tuple_id"], "prose exact ID projection")
        require(row["surface_display_only"] == source["surface"], "prose surface projection")
    astro_by_id = {row["local_group_id"]: row for row in source_astro}
    require(len(astro_by_id) == 395, "Astro IDs not unique")
    for row in astro_audit:
        source = astro_by_id[row["opaque_whole_card_key"].removeprefix("A:")]
        require((row["unit_id"], row["page"], row["source_locus"], row["surface_display_only"]) ==
                (source["diagram_id"], source["page"], source["source_locus"], source["surface_display_only"]), "Astro projection")
        require("NO_CROSSPAGE_JOIN" in row["semantic_contract"], "Astro crosspage contract")

    clauses = data["clauses"]
    require(Counter(row["typed_clause_class"] for row in clauses) == Counter({"CONTROLLED_UNIQUE": 12, "MIXED_AMBIGUOUS": 49, "OPAQUE_UNPARSED": 55}), "typed clause classes")
    require({row["statement_id"] for row in clauses} == {row["statement_id"] for row in source_statements}, "statement coverage")
    require(sum(int(row["event_count"]) for row in clauses) == 381, "statement event partition")
    require(all(row["formal_roundtrip"] == "PASS_EXACT_ID_ORDER_FIELD_LOCUS" for row in clauses), "statement formal roundtrip")
    require(all(row["complete_source_without_exemplar"] == "FAIL;CONTROL_SKELETON_ONLY" for row in clauses), "standalone semantic overclaim")
    require(all(row["complete_source_with_exemplar"] == "PASS_SELECTED_CREATIVE_SOURCE" for row in clauses), "statement exemplar roundtrip")
    require(sum("LINE_RESET" in row["physical_locus_reflow"] for row in clauses) == 18, "cross-line statement count")
    decoded_serials = [serial for row in clauses for serial in row["event_serials"].split("|")]
    require(Counter(decoded_serials) == Counter(str(i) for i in range(1, 382)), "statement event partition exactness")

    runtime = data["runtime"]
    source_register_by_id = {row["statement_id"]: row for row in source_registers}
    require({row["statement_id"] for row in runtime} == set(source_register_by_id), "runtime transition coverage")
    require(sum(row["backward_from_post_state_only"] == "YES" for row in runtime) == 47, "post-only backward count")
    require(all(row["backward_from_full_log"] == "PASS" for row in runtime), "full-log backward failure")
    for row in runtime:
        source = source_register_by_id[row["statement_id"]]
        require(row["pre_state"] == source["pre_state"] and row["post_state"] == source["post_state"], "register state projection")
        require(row["operation_trace"] == source["operation_trace"], "transition log projection")

    automaton = data["automaton"]
    require([row["transition_id"] for row in automaton] == [f"T{i:02d}" for i in range(1, 23)], "automaton transition IDs")
    require(Counter(row["to_state"] for row in automaton)["REJECT"] == 5, "fail-closed transition count")
    require(all(row["failure_policy"] == ("FAIL_CLOSED" if row["to_state"] == "REJECT" else "CONTINUE") for row in automaton), "automaton failure policy")
    require(any("phonetic" in row["deterministic_action"] for row in automaton), "phonetic rejection absent")

    units = data["units"]
    require([row["unit_id"] for row in units] == ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"], "unit order")
    require(sum(int(row["visible_group_count"]) for row in units) == 776, "unit group total")
    require(sum(int(row["locus_count"]) for row in units) == 199, "combined locus total")
    require(sum(int(row["field_count"].split(";", 1)[0]) for row in units) == 135, "field total")
    require(sum(int(row["statement_count"].split(";", 1)[0]) for row in units) == 116, "statement total")
    require(sum(int(row["reusable_control_union_events"].split(";", 1)[0]) for row in units) == 119, "global control total")
    require(all(row["complete_source_roundtrip_without_exemplar"].startswith("0/") for row in units), "unit source overclaim")

    traces = data["traces"]
    require(Counter(row["trace_unit"] for row in traces) == Counter({
        "H5-S001": 9, "B1-S002": 19, "B2-S005": 8, "B5-S003": 9,
        "A1:L074": 13, "A2:L001": 9, "A3:L001": 40,
    }), "long trace coverage")
    require(all(row["roundtrip_result"] == "PASS_FORMAL_AND_SELECTED_EXEMPLAR" for row in traces), "trace failure")
    for trace_unit, members in defaultdict(list, {key: [row for row in traces if row["trace_unit"] == key] for key in {row["trace_unit"] for row in traces}}).items():
        require([int(row["step"]) for row in members] == list(range(1, len(members) + 1)), f"trace step order: {trace_unit}")
        require(all(int(row["step_count"]) == len(members) for row in members), f"trace length label: {trace_unit}")

    models = data["models"]
    state_models = [row for row in models if row["comparison_axis"] == "SILENT_REGISTER_STATE"]
    codebooks = [row for row in models if row["comparison_axis"] == "CODEBOOK_AND_EXEMPLAR"]
    require([row["fully_reconstructable_source_statements"] for row in state_models] == ["9/116", "27/116", "88/116", "107/116", "116/116"], "minimal register sequence")
    require({row["model"] for row in codebooks} == {"MNEMONIC_ONLY", "FORMAL_PROMPT_ONLY", "UNION_GLOBAL_CONTROL", "FULL_PROSE_OPAQUE_DECK", "FULL_LOCAL_RENDERER", "AGGREGATED_SOURCE_EXEMPLARS", "EVENT_LEVEL_SOURCE_PAYLOAD"}, "codebook model set")
    union = next(row for row in codebooks if row["model"] == "UNION_GLOBAL_CONTROL")
    require((union["codebook_key_count"], union["covered_existing_groups"]) == ("14", "119/776"), "control codebook size/coverage")

    order = data["order"]
    require({row["order_model"] for row in order} == {"LATIN_LIKE_DEPENDENT_FIRST_PROXY", "VERNACULAR_LIKE_HEAD_FIRST_PROXY"}, "order models")
    require(all((row["informative_statements"], row["ordered_pair_comparisons"], row["pair_order_violations"], row["selection_verdict"]) == ("28", "94", "42", "TIE_BY_TOTAL_VIOLATIONS") for row in order), "order tie")
    require(all(row["linguistic_claim"].startswith("NONE") for row in order), "language claim introduced")
    require([row["error_id"] for row in data["errors"]] == [f"E{i:02d}" for i in range(1, 15)], "error audit IDs")

    before = {name: digest(path) for name, (path, _) in FILES.items()}
    subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(path) for name, (path, _) in FILES.items()}
    require(before == after, "builder not byte-deterministic")

    print("PASS V67 R3 validator")
    print("units=14 groups=776 prose=381 astro=395 fields=135 statements=116 loci=199")
    print("formal_roundtrip=776/776; selected_source_with_exemplar=776/776; without_exemplar=0/776")
    print("control_union=119/381 prose events with 14 exact cards; opaque prose=262/381")
    print("registers=4:116/116; post_state_only=47/116; order_proxy_tie=42/94 each")
    print("deterministic_rebuild=PASS")


if __name__ == "__main__":
    validate()
