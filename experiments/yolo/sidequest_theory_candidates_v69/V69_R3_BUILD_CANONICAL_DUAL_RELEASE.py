#!/usr/bin/env python3
"""Build the deterministic V69 R3 canonical dual release."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"


def p(version: int, name: str) -> Path:
    return YOLO / f"sidequest_theory_candidates_v{version}" / name


SOURCE_SPECS = [
    (p(60, "V60_FOUR_ROLE_SELECTION.md"), "V60", "SELECTION", "47af2d38753816a78ff8f243e64e1eb084fccfc239ef44bc6e0cf548186ca1ae"),
    (p(61, "V61_FOUR_ROLE_SELECTION.md"), "V61", "SELECTION", "b73b0f2146f123118fbb4a3618c63778c0c3593e90df37a4e540528aba2587ba"),
    (p(62, "V62_FOUR_ROLE_SELECTION.md"), "V62", "SELECTION", "681e91fe9564767efa2cd76bb4e2d54257956b004b094bb38a52e7ded843df38"),
    (p(63, "V63_FOUR_ROLE_SELECTION.md"), "V63", "SELECTION", "1ef3d544edd73a8ed1a2c1d2b0ee158b525f1034e50accadf7affeef080a8c11"),
    (p(64, "V64_FOUR_ROLE_SELECTION.md"), "V64", "SELECTION", "def880d426029ff058d845bfb5e72fb38d530731fe60c8294df2dcc6af4438b4"),
    (p(65, "V65_FOUR_ROLE_SELECTION.md"), "V65", "SELECTION", "f0ac186514ab7edd906a23a690c3d24e71e99faa96e5483181ed2f0f78c8beac"),
    (p(66, "V66_FOUR_ROLE_SELECTION.md"), "V66", "SELECTION", "d760c21449409b155aa174613266f278f5a82327341c9f91e3b39b04acc7eb2e"),
    (p(67, "V67_FOUR_ROLE_SELECTION.md"), "V67", "SELECTION", "3c7f96b35452a8f6aac02023015ff437d422b3180040b295145cd4deac28106a"),
    (p(68, "V68_FOUR_ROLE_SELECTION.md"), "V68", "SELECTION", "d252d2bf190f8fd6d10ded2e0e931411d0144ee780f1d5afbedaa0ef32798a91"),
    (p(60, "V60_SELECTED_173_CARD_DICTIONARY.tsv"), "V60", "CARD_DECK", "f5fe8d951db08a43ab7aa1e488b5c5efd7866c7389e418cfd74cb99e3f53fd6d"),
    (p(60, "V60_SELECTED_381_EVENT_LEDGER.tsv"), "V60", "PROSE_EVENTS", "51d69e33c7a02111c79322fb8c1537e34a61fb91c3f885ea48373c20be890f45"),
    (p(61, "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"), "V61", "STATEMENTS", "6083ba9ec5bd2122f953bbcbb4d733fc3cee2c24f7fff75543a73e764c813fc3"),
    (p(61, "V61_SELECTED_46_LINE_BOUNDARIES.tsv"), "V61", "REFLOW", "8f0c0ebd1ae05c24ab1c5d8918a708f1923c2937f2acce86ac09aac951b7c885"),
    (p(62, "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"), "V62", "REGISTERS", "2ee7d0ef2a5abe49388ba0dc2bc650c1677f3747537059ccd486cac335ca7139"),
    (p(63, "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"), "V63", "EVENT_PARSER", "f009982934532f1ad02d427feba65017edd93cee1b0819b870c537034278e2c4"),
    (p(63, "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"), "V63", "FIELDS", "c6b724d450f999eec873159dc48656e5994f37ffca41d1bcbb4f3f386c8e9680"),
    (p(63, "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"), "V63", "STATEMENT_PARSER", "09789240ec65a32e36f12d0839335a8f6c5c3a5b8637dfdbe91e88adadd5ab65"),
    (p(66, "V66_R3_395_GROUP_LOOKUP_EDITION.tsv"), "V66", "ASTRO_GROUPS", "eb2ce0bee4566bc78ac12930854fd6de27969bd534d1ac7a71c4a43878f57b8a"),
    (p(66, "V66_R3_F68_29_ADDRESS_CATALOGUE.tsv"), "V66", "F68_ADDRESSES", "1f6cbef2ced3c7f7a4508f53a1a2d1b637b76f6627c89615cf9542d6fa5a77af"),
    (p(66, "V66_R3_F69_28_TECHNICAL_RULES.tsv"), "V66", "F69_RULES", "239f9d5100108d41c17de7a0fb92c0153eb2df34a4ca0f65f98f6ca06021dcf4"),
    (p(67, "V67_R3_COMPILER_TRANSITIONS.tsv"), "V67", "COMPILER", "7fb556ee36ff440d9303dea3a7a0046658ed9fe4f553c8a13f17de14ccf5e24c"),
    (p(68, "V68_R3_776_GROUP_ADVERSARIAL_LEDGER.tsv"), "V68", "DUAL_GROUPS", "6655391622c40a253d47bb4701ed2b70eafd0f42c358a9e3c8c3ce2be9e218ea"),
    (p(68, "V68_R3_14_UNIT_TECHNICAL_EDITION.tsv"), "V68", "DUAL_UNITS", "401aa8186bb41dcd54f699d1581c3a8bf5a1885845851656cf8be5947ca94b4f"),
    (p(68, "V68_R3_14_PROCESS_GRAPHS.tsv"), "V68", "PROCESSES", "550a37f20d9d30ec102d98f47fe947a2e8241b7cbbabbd8774dc1e95e92f6159"),
    (p(68, "V68_R3_28_MODEL_COSTS.tsv"), "V68", "COSTS", "e3ab98d39e23a898ea9f17257a321b93aa7190e2dcbfefacf448e82885d0640d"),
    (p(68, "V68_R3_14_CONTRADICTIONS.tsv"), "V68", "CONTRADICTIONS", "0c6449a5e75a954f3641fa418637ca9432dd7e7739a14e569409aca0f1b58c11"),
    (p(68, "V68_R3_4_SECTION_COMPARISON.tsv"), "V68", "COMPARISON", "0d6201888e1adbe7b0bde21ed929e96909a7edf5aeeb61555af473f54795d53f"),
]

OUT_CARDS = HERE / "V69_R3_173_CARD_DICTIONARY.tsv"
OUT_EVENTS = HERE / "V69_R3_381_PROSE_EVENT_LEDGER.tsv"
OUT_FIELDS = HERE / "V69_R3_135_FIELD_LEDGER.tsv"
OUT_STATEMENTS = HERE / "V69_R3_116_STATEMENT_LEDGER.tsv"
OUT_ASTRO = HERE / "V69_R3_395_ASTRO_GROUP_LEDGER.tsv"
OUT_UNIFIED = HERE / "V69_R3_776_UNIFIED_DUAL_LEDGER.tsv"
OUT_UNITS = HERE / "V69_R3_14_UNIT_DUAL_EDITION.tsv"
OUT_COMPILER = HERE / "V69_R3_22_COMPILER_TRANSITIONS.tsv"
OUT_INVARIANTS = HERE / "V69_R3_INVARIANT_AUDIT.tsv"
OUT_SOURCES = HERE / "V69_R3_SOURCE_MANIFEST.tsv"
OUT_RELEASE = HERE / "V69_R3_RELEASE_MANIFEST.tsv"

UNIT_ORDER = ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3")
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
UNSET_STATE = "OWNER=UNSET;ACTIVE_ITEM/PREPARATION=UNSET;TARGET/STATION=UNSET;PREVIOUS_ITEM=UNSET"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_rows_and_manifest() -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    manifest: list[dict[str, str]] = []
    for path, iteration, role, expected_hash in SOURCE_SPECS:
        actual = digest(path)
        require(actual == expected_hash, f"source hash changed: {rel(path)}")
        row_count = "NOT_TABULAR"
        if path.suffix == ".tsv":
            rows = read_tsv(path)
            tables[role] = rows
            row_count = str(len(rows))
        manifest.append({
            "source_path": rel(path),
            "iteration": iteration,
            "lineage_role": role,
            "row_count": row_count,
            "byte_count": str(path.stat().st_size),
            "sha256": actual,
            "selection_status": "FROZEN_SELECTED_OR_SELECTED_DERIVATIVE",
            "scope_contract": "TEN_ALLOWED_PAGES_ONLY;NO_NEW_SOURCE",
        })
    return tables, manifest


def main() -> None:
    t, source_manifest = source_rows_and_manifest()
    cards0 = t["CARD_DECK"]
    events0 = t["PROSE_EVENTS"]
    statements0 = t["STATEMENTS"]
    boundaries0 = t["REFLOW"]
    registers0 = t["REGISTERS"]
    event_parse0 = t["EVENT_PARSER"]
    fields0 = t["FIELDS"]
    statement_parse0 = t["STATEMENT_PARSER"]
    astro0 = t["ASTRO_GROUPS"]
    dual0 = t["DUAL_GROUPS"]
    units0 = t["DUAL_UNITS"]
    processes0 = t["PROCESSES"]
    costs0 = t["COSTS"]
    contradictions0 = t["CONTRADICTIONS"]
    compiler0 = t["COMPILER"]
    require((len(cards0), len(events0), len(fields0), len(statements0), len(astro0), len(dual0), len(units0)) == (173, 381, 135, 116, 395, 776, 14), "primary source counts")

    # Canonical card deck: exact identity and formal prompt are retained, while
    # both content worlds are explicitly forbidden at card-type level.
    card_rows: list[dict[str, str]] = []
    for row in cards0:
        mnemonic = row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        card_rows.append({
            "exact_joint_card_id": row["joint_tuple_id"],
            "surface_examples_display_only": row["surface_examples"],
            "occurrences": row["occurrences"],
            "pages": row["pages"],
            "formal_formula_opaque": row["formal_formula_opaque"],
            "formal_value": row["FORMAL_VALUE"],
            "strict_formal_prompt": row["strict_control_prompt"],
            "working_exact_mnemonic_or_UNKNOWN_EXEMPLAR": mnemonic if mnemonic != "UNKNOWN" else "UNKNOWN_EXEMPLAR",
            "mnemonic_scope": row["mnemonic_scope"],
            "semantic_tail_status": "CREATIVE_SHORT_PROMPT_NOT_TRANSLATION" if mnemonic != "UNKNOWN" else "UNKNOWN_EXEMPLAR;NO_GLOBAL_SEMANTIC_VALUE",
            "iatromedical_card_value": "NONE;LOCAL_EVENT_EXEMPLAR_ONLY",
            "practical_card_value": "NONE;LOCAL_EVENT_EXEMPLAR_ONLY",
            "component_inheritance": "FORBIDDEN;EXACT_JOINT_CARD_ATOMIC",
            "page_host_semantics": "FORBIDDEN",
            "confirmed_lexeme": "NO",
            "source_lineage": row["source_lineage"] + ">V60_SELECTED>V69_R3_CANONICAL_NO_DOMAIN_VALUE",
        })
    require(len({row["exact_joint_card_id"] for row in card_rows}) == 173, "card IDs not unique")

    dual_by_ordinal = {row["combined_group_ordinal"]: row for row in dual0}
    parse_by_serial = {row["event_serial"]: row for row in event_parse0}
    register_by_statement = {row["statement_id"]: row for row in registers0}
    statement_parse_by_id = {row["statement_id"]: row for row in statement_parse0}
    statement_source_by_id = {row["statement_id"]: row for row in statements0}

    event_rows: list[dict[str, str]] = []
    for source in events0:
        serial = source["event_serial"]
        parsed = parse_by_serial[serial]
        dual = dual_by_ordinal[serial]
        mnemonic = source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        require((source["record_unit_id"], source["page"], source["locus"], source["field_id"], source["joint_tuple_id"], source["surface"]) ==
                (dual["unit_id"], dual["page"], dual["source_locus"], dual["field_or_local_address"], dual["opaque_whole_card_or_local_group_key"].removeprefix("P:"), dual["surface_display_only"]), f"dual event drift: {serial}")
        require((source["joint_tuple_id"], source["surface"], source["field_id"]) == (parsed["joint_tuple_id"], parsed["surface_display_only"], parsed["field_id"]), f"parser event drift: {serial}")
        event_rows.append({
            "event_serial": serial,
            "page": source["page"],
            "locus": source["locus"],
            "record_unit_id": source["record_unit_id"],
            "field_id": source["field_id"],
            "statement_id": parsed["statement_id"],
            "event_index_in_locus": source["event_index_in_locus"],
            "event_index_in_record": source["event_index_in_record"],
            "surface_display_only": source["surface"],
            "exact_joint_card_id": source["joint_tuple_id"],
            "formal_formula_opaque": source["formal_formula_opaque"],
            "formal_value": source["FORMAL_VALUE"],
            "terminal_status": source["terminal_status"],
            "strict_formal_prompt": source["strict_control_prompt"],
            "working_exact_mnemonic_or_UNKNOWN_EXEMPLAR": mnemonic if mnemonic != "UNKNOWN" else "UNKNOWN_EXEMPLAR",
            "semantic_tail_status": "CREATIVE_SHORT_PROMPT_NOT_TRANSLATION" if mnemonic != "UNKNOWN" else "UNKNOWN_EXEMPLAR;LOCAL_PAYLOAD_REQUIRED",
            "compiler_channel": dual["compiler_channel_inherited"],
            "bounded_template": parsed["event_template"],
            "template_trigger_origin": parsed["trigger_origin"],
            "template_parse_status": parsed["event_parse_status"],
            "required_registers": parsed["required_registers"],
            "symbolic_register_effect": parsed["symbolic_register_effect"],
            "field_and_line_operation": dual["field_and_reflow_contract"],
            "iatromedical_local_exemplar": dual["selected_iatromedical_comparator"],
            "practical_local_exemplar": dual["complete_local_technical_default"],
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "formal_roundtrip": dual["formal_roundtrip"],
            "semantic_contract": "NO_CONFIRMED_LEXEME;NO_PAGE_HOST_OR_COMPONENT_MEANING;LOCAL_DUAL_TEXT_NOT_CARD_VALUE",
            "source_lineage": source["source_lineage"] + ">V63_SELECTED_PARSE>V68_DUAL>V69_R3",
        })
    require([int(row["event_serial"]) for row in event_rows] == list(range(1, 382)), "event order")
    event_by_serial = {row["event_serial"]: row for row in event_rows}

    field_rows: list[dict[str, str]] = []
    for field in fields0:
        members = [event_by_serial[value] for value in field["event_serials"].split("|")]
        last = members[-1]
        terminal = "TERMINAL_CLOSE" if last["terminal_status"] == "TERMINAL" else "OPEN_CUT"
        field_rows.append({
            "field_id": field["field_id"],
            "record_unit_id": field["record_unit_id"],
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": field["statement_id"],
            "field_position_in_statement": field["field_position_in_statement"],
            "event_count": field["event_count"],
            "event_serials": field["event_serials"],
            "exact_card_sequence": "|".join(row["exact_joint_card_id"] for row in members),
            "surface_sequence_display_only": " ".join(row["surface_display_only"] for row in members),
            "formal_prompt_sequence": " > ".join(row["strict_formal_prompt"] for row in members),
            "mnemonic_or_UNKNOWN_sequence": " > ".join(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] for row in members),
            "terminal_envelope": terminal,
            "line_reflow_after_field": last["field_and_line_operation"].rsplit(">", 1)[-1],
            "primary_template": field["primary_template"],
            "ordered_event_template_sequence": field["ordered_event_template_sequence"],
            "parse_status": field["parse_status"],
            "recognized_event_count": field["recognized_event_count"],
            "exemplar_only_event_count": field["exemplar_only_event_count"],
            "semantic_UNKNOWN_EXEMPLAR_event_count": str(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR" for row in members)),
            "register_pre_state": field["register_pre_state_statement_envelope"],
            "register_update_trace": field["register_update_trace"],
            "register_post_state": field["register_post_state_statement_envelope"],
            "iatromedical_field_exemplar": " ; ".join(row["iatromedical_local_exemplar"] for row in members),
            "practical_field_exemplar": " ; ".join(row["practical_local_exemplar"] for row in members),
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "opaque_roundtrip_status": field["roundtrip_status"],
            "semantic_contract": "FIELD_NOT_SENTENCE;CLOSE_SILENT;LOCAL_DUAL_EXEMPLARS",
        })
    require(len(field_rows) == 135, "field count")

    statement_rows: list[dict[str, str]] = []
    first_statement_by_unit: dict[str, str] = {}
    for source in statements0:
        first_statement_by_unit.setdefault(source["record_unit_id"], source["statement_id"])
    for source in statements0:
        statement_id = source["statement_id"]
        parsed = statement_parse_by_id[statement_id]
        transition = register_by_statement[statement_id]
        members = [event_by_serial[value] for value in source["event_serials"].split("|")]
        is_first = first_statement_by_unit[source["record_unit_id"]] == statement_id
        if is_first:
            require(transition["pre_state"] == UNSET_STATE and transition["owner_operation"] == "INTRODUCE", f"record reset failed: {statement_id}")
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "statement_ordinal_in_record": source["statement_ordinal_in_record"],
            "constituent_fields": source["constituent_fields"],
            "constituent_loci": source["constituent_loci"],
            "physical_line_count": source["physical_line_count"],
            "internal_cross_line_boundaries": source["internal_cross_line_boundaries"],
            "event_count": source["event_count"],
            "event_serials": source["event_serials"],
            "exact_card_sequence": "|".join(row["exact_joint_card_id"] for row in members),
            "closure_sequence": source["closure_sequence"],
            "entry_boundary_class": source["entry_boundary_class"],
            "exit_boundary_class": source["exit_boundary_class"],
            "ordered_template_sequence": parsed["ordered_event_template_sequence"],
            "parse_status": parsed["parse_status"],
            "recognized_event_count": parsed["recognized_event_count"],
            "exemplar_only_event_count": parsed["exemplar_only_event_count"],
            "record_reset_status": "PASS_RESET_AT_RECORD_START" if is_first else "WITHIN_RECORD_TRANSITION",
            "pre_state": transition["pre_state"],
            "owner_active_target_previous_operations": "/".join((transition["owner_operation"], transition["active_item_preparation_operation"], transition["target_station_operation"], transition["previous_item_operation"])),
            "inferred_missing_slots": transition["inferred_missing_slots"],
            "operation_trace": transition["operation_trace"],
            "post_state": transition["post_state"],
            "backward_from_full_transition_log": "YES",
            "backward_from_post_state_only": transition["backward_reconstructable_from_post_state_only"],
            "iatromedical_statement_exemplar": " ; ".join(row["iatromedical_local_exemplar"] for row in members),
            "practical_statement_exemplar": " ; ".join(row["practical_local_exemplar"] for row in members),
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "formal_roundtrip": parsed["roundtrip_status"],
            "strongest_segmentation_rival": source["strongest_alternative"],
            "semantic_contract": "REGISTER_IDS_RECORD_LOCAL;LINE_RESET_NOT_SENTENCE;DUAL_LOCAL_EXEMPLAR_ONLY",
        })
    require(len(first_statement_by_unit) == 11 and len(statement_rows) == 116, "statement/reset counts")

    astro_source_by_id = {"A:" + row["local_group_id"]: row for row in astro0}
    astro_rows: list[dict[str, str]] = []
    for dual in dual0[381:]:
        source = astro_source_by_id[dual["opaque_whole_card_or_local_group_key"]]
        require((dual["unit_id"], dual["page"], dual["source_locus"], dual["surface_display_only"]) ==
                (source["diagram_id"], source["page"], source["source_locus"], source["surface_display_only"]), "Astro dual drift")
        astro_rows.append({
            "astro_group_serial": str(len(astro_rows) + 1),
            "unified_group_ordinal": dual["combined_group_ordinal"],
            "diagram_id": source["diagram_id"],
            "page": source["page"],
            "source_locus": source["source_locus"],
            "local_locus_id": dual["statement_or_locus_unit"],
            "local_group_id": source["local_group_id"],
            "local_lookup_address": source["local_lookup_address"],
            "group_index_within_locus": source["group_index_within_locus"],
            "surface_display_only": source["surface_display_only"],
            "instrument_component": source["instrument_component"],
            "formal_local_role": source["technical_group_role"],
            "working_mnemonic_or_UNKNOWN_EXEMPLAR": "UNKNOWN_EXEMPLAR_LOCAL",
            "iatromedical_local_exemplar": dual["selected_iatromedical_comparator"],
            "practical_local_exemplar": dual["complete_local_technical_default"],
            "orientation_contract": source["orientation_contract"],
            "crosspage_contract": source["crosspage_contract"],
            "line_reflow_operation": dual["field_and_reflow_contract"],
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "formal_roundtrip": dual["formal_roundtrip"],
            "semantic_contract": "NO_PROSE_ID_OR_PROMPT;PAGE_LOCAL_EXEMPLAR_NOT_WORD;NO_F68_F69_JOIN",
            "source_lineage": source["source_lineage"] + ">V68_DUAL>V69_R3",
        })
    require(len(astro_rows) == 395, "Astro count")

    unified_rows: list[dict[str, str]] = []
    for event in event_rows:
        unified_rows.append({
            "unified_group_id": f"U{int(event['event_serial']):04d}",
            "unified_group_ordinal": event["event_serial"],
            "namespace": "PROSE_EXACT_JOINT_CARD",
            "unit_id": event["record_unit_id"],
            "page": event["page"],
            "source_locus": event["locus"],
            "field_or_local_address": event["field_id"],
            "statement_or_local_locus": event["statement_id"],
            "opaque_exact_or_local_id": "P:" + event["exact_joint_card_id"],
            "surface_display_only": event["surface_display_only"],
            "formal_layer": event["formal_value"] + "|" + event["strict_formal_prompt"],
            "working_mnemonic_or_UNKNOWN_EXEMPLAR": event["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"],
            "parser_or_layout_role": event["bounded_template"],
            "iatromedical_local_exemplar": event["iatromedical_local_exemplar"],
            "practical_local_exemplar": event["practical_local_exemplar"],
            "terminal_field_line_layer": event["terminal_status"] + "|" + event["field_and_line_operation"],
            "state_contract": "FOUR_RECORD_LOCAL_REGISTERS",
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "formal_roundtrip": event["formal_roundtrip"],
            "semantic_contract": event["semantic_contract"],
        })
    for astro in astro_rows:
        ordinal = int(astro["unified_group_ordinal"])
        unified_rows.append({
            "unified_group_id": f"U{ordinal:04d}",
            "unified_group_ordinal": str(ordinal),
            "namespace": "ASTRO_PAGE_LOCAL_GROUP",
            "unit_id": astro["diagram_id"],
            "page": astro["page"],
            "source_locus": astro["source_locus"],
            "field_or_local_address": astro["local_lookup_address"],
            "statement_or_local_locus": astro["local_locus_id"],
            "opaque_exact_or_local_id": "A:" + astro["local_group_id"],
            "surface_display_only": astro["surface_display_only"],
            "formal_layer": astro["formal_local_role"],
            "working_mnemonic_or_UNKNOWN_EXEMPLAR": "UNKNOWN_EXEMPLAR_LOCAL",
            "parser_or_layout_role": astro["instrument_component"],
            "iatromedical_local_exemplar": astro["iatromedical_local_exemplar"],
            "practical_local_exemplar": astro["practical_local_exemplar"],
            "terminal_field_line_layer": "NOT_PROSE_CLOSE|" + astro["line_reflow_operation"],
            "state_contract": "ASTRO_PAGE_LOCAL_ADDRESS;NO_PROSE_REGISTERS",
            "domain_selection": "NONE;DUAL_UNRESOLVED",
            "complete_source_recovery_without_exemplar": "NO",
            "formal_roundtrip": astro["formal_roundtrip"],
            "semantic_contract": astro["semantic_contract"],
        })
    require([int(row["unified_group_ordinal"]) for row in unified_rows] == list(range(1, 777)), "unified order")

    process_by_unit = {row["unit_id"]: row for row in processes0}
    contradiction_by_unit = {row["unit_id"]: row for row in contradictions0}
    costs_by_unit_role = {(row["unit_id"], row["model_role"]): row for row in costs0}
    unit_rows: list[dict[str, str]] = []
    for source in units0:
        unit_id = source["unit_id"]
        members = [row for row in unified_rows if row["unit_id"] == unit_id]
        process = process_by_unit[unit_id]
        contradiction = contradiction_by_unit[unit_id]
        practical_cost = costs_by_unit_role[(unit_id, "TECHNICAL_RIVAL")]
        medical_cost = costs_by_unit_role[(unit_id, "IATROMEDICAL_COMPARATOR")]
        content_hash_basis = "|".join(row["opaque_exact_or_local_id"] for row in members) + "\n" + source["selected_iatromedical_comparator_complete_German"] + "\n" + source["technical_default_complete_German"]
        unit_rows.append({
            "unit_id": unit_id,
            "section_axis": source["section_axis"],
            "page": source["page"],
            "group_count": source["group_count"],
            "locus_count": source["locus_count"],
            "field_count": source["field_count"],
            "statement_count": source["statement_count"],
            "iatromedical_complete_reading": source["selected_iatromedical_comparator_complete_German"],
            "practical_complete_reading": source["technical_default_complete_German"],
            "domain_selection": "NONE;COEQUAL_DUAL_EDITION",
            "iatromedical_weighted_cost_section_local": medical_cost["weighted_cost"],
            "practical_weighted_cost_section_local": practical_cost["weighted_cost"],
            "cost_comparability": practical_cost["comparability_contract"],
            "deterministic_process_graph": process["deterministic_process_graph"],
            "execution_rule": process["execution_rule"],
            "strongest_practical_contradiction": contradiction["strongest_technical_contradiction"],
            "strongest_iatromedical_contradiction": contradiction["strongest_iatromedical_contradiction_or_nonmedical_rival"],
            "record_or_namespace_reset": "RESET_FOUR_REGISTERS_AT_RECORD_START" if unit_id.startswith(("H", "B")) else "RESET_TO_PAGE_LOCAL_DIAGRAM_NAMESPACE",
            "line_reflow_contract": "PHYSICAL_LINE_NOT_SENTENCE" if unit_id.startswith(("H", "B")) else "DRAWN_LOCUS_PRIMARY;NO_IMPLICIT_ORIENTATION",
            "complete_source_recovery_without_exemplar": f"0/{len(members)}",
            "complete_source_recovery_with_exemplar": f"{len(members)}/{len(members)}",
            "unit_content_sha256": text_digest(content_hash_basis),
            "semantic_contract": "NO_WINNER;NO_CONFIRMED_LEXEME;BOTH_READINGS_LOCAL_EXEMPLARS",
        })
    require([row["unit_id"] for row in unit_rows] == list(UNIT_ORDER), "unit order")

    compiler_rows = []
    for row in compiler0:
        compiler_rows.append({
            **row,
            "canonical_input_layer": "TYPED_SOURCE+FOUR_REGISTERS+EXACT_OR_LOCAL_EXEMPLAR_KEY",
            "canonical_output_layer": "OPAQUE_ID+FIELD_OR_LOCUS+REFLOW+WHOLE_SURFACE",
            "decode_without_exemplar": "FORMAL_ONLY;COMPLETE_SOURCE_RECOVERY_NONE",
            "domain_policy": "IATROMEDICAL_AND_PRACTICAL_COEQUAL;NO_SELECTION",
            "semantic_prohibition": "NO_PAGE_HOST_COMPONENT_PHONETIC_OR_NEW_CARD_MEANING",
        })
    require(len(compiler_rows) == 22, "compiler transition count")

    f68 = [row for row in t["F68_ADDRESSES"] if row["catalogue_entry_type"] == "SPATIAL_STATION"]
    f69 = t["F69_RULES"]
    require(len(f68) == len(f69) == 28, "28er inventories")
    f68_forms = [row["surface_display_only"] for row in f68]
    f69_forms = [row["surface_entry_display_only"] for row in f69]
    same_index = sum(left == right for left, right in zip(f68_forms, f69_forms, strict=True))
    all_pair = sum(left == right for left in f68_forms for right in f69_forms)

    boundary_counts = Counter(row["classification"] for row in boundaries0)
    field_status = Counter(row["parse_status"] for row in field_rows)
    statement_status = Counter(row["parse_status"] for row in statement_rows)
    mnemonic_cards = [row for row in card_rows if row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR"]
    formal_cards = [row for row in card_rows if row["strict_formal_prompt"] != "NONE"]
    control_card_ids = {row["exact_joint_card_id"] for row in mnemonic_cards + formal_cards}
    no_control_cards = [row for row in card_rows if row["exact_joint_card_id"] not in control_card_ids]
    mnemonic_events = [row for row in event_rows if row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR"]
    formal_events = [row for row in event_rows if row["strict_formal_prompt"] != "NONE"]
    control_events = [row for row in event_rows if row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR" or row["strict_formal_prompt"] != "NONE"]
    invariant_rows: list[dict[str, str]] = []

    def inv(name: str, observed: object, expected: object, contract: str) -> None:
        status = "PASS" if str(observed) == str(expected) else "FAIL"
        invariant_rows.append({"invariant": name, "observed": str(observed), "expected": str(expected), "status": status, "contract": contract})
        require(status == "PASS", f"invariant failed: {name}: {observed} != {expected}")

    inv("CARD_TYPE_COUNT", len(card_rows), 173, "exact joint IDs")
    inv("CARD_OCCURRENCE_SUM", sum(int(row["occurrences"]) for row in card_rows), 381, "full prose deck")
    inv("MNEMONIC_CARD_TYPES", len(mnemonic_cards), 11, "V60 exact working deck")
    inv("MNEMONIC_EVENT_OCCURRENCES", len(mnemonic_events), 85, "exact mnemonic only")
    inv("FORMAL_PROMPT_CARD_TYPES", len(formal_cards), 4, "strict formal prompts")
    inv("FORMAL_PROMPT_EVENT_OCCURRENCES", len(formal_events), 45, "formal channel")
    inv("CONTROL_UNION_CARD_TYPES", len(control_card_ids), 14, "one mnemonic/formal overlap")
    inv("CONTROL_UNION_EVENT_OCCURRENCES", len(control_events), 119, "V63 recognized events")
    inv("UNKNOWN_MNEMONIC_CARD_TYPES", sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR" for row in card_rows), 162, "all tails explicit")
    inv("UNKNOWN_MNEMONIC_EVENT_OCCURRENCES", sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR" for row in event_rows), 296, "all tails explicit")
    inv("NO_CONTROL_CARD_TYPES", len(no_control_cards), 159, "neither mnemonic nor formal prompt")
    inv("NO_CONTROL_EVENT_OCCURRENCES", sum(row["compiler_channel"] == "EXEMPLAR_WHOLE_CARD" for row in event_rows), 262, "V63 EXEMPLAR_ONLY")
    inv("PROSE_EVENT_COUNT", len(event_rows), 381, "complete prose")
    inv("FIELD_COUNT", len(field_rows), 135, "complete fields")
    inv("TERMINAL_FIELD_COUNT", sum(row["terminal_envelope"] == "TERMINAL_CLOSE" for row in field_rows), 90, "close field-final and silent")
    inv("OPEN_FIELD_COUNT", sum(row["terminal_envelope"] == "OPEN_CUT" for row in field_rows), 45, "open fields")
    inv("FIELD_PARSE_PROFILE", f"U{field_status['UNIQUE']}:A{field_status['AMBIGUOUS']}:X{field_status['UNPARSED']}", "U14:A56:X65", "bounded parser")
    inv("STATEMENT_COUNT", len(statement_rows), 116, "complete statements")
    inv("STATEMENT_PARSE_PROFILE", f"U{statement_status['UNIQUE']}:A{statement_status['AMBIGUOUS']}:X{statement_status['UNPARSED']}", "U12:A49:X55", "bounded parser")
    inv("RECORD_LOCAL_RESET_COUNT", sum(row["record_reset_status"] == "PASS_RESET_AT_RECORD_START" for row in statement_rows), 11, "four registers reset at every prose record")
    inv("PHYSICAL_LINE_BOUNDARY_COUNT", len(boundaries0), 46, "V61 reflow")
    inv("BOUNDARY_CLASS_PROFILE", f"C{boundary_counts['CONTINUE_SAME_CLAUSE']}:R{boundary_counts['RESUME_ACTIVE_ITEM']}:P{boundary_counts['NEXT_PARALLEL_CELL']}:S{boundary_counts['START_NEW_CLAUSE']}:U{boundary_counts['UNRESOLVED']}", "C19:R8:P10:S8:U1", "line not sentence")
    inv("CROSS_LINE_STATEMENT_COUNT", sum(int(row["physical_line_count"]) > 1 for row in statement_rows), 18, "17 two-locus plus one three-locus")
    inv("BACKWARD_WITH_FULL_TRANSITION_LOG", sum(row["backward_from_full_transition_log"] == "YES" for row in statement_rows), 116, "full V62 log")
    inv("BACKWARD_FROM_POST_STATE_ONLY", sum(row["backward_from_post_state_only"] == "YES" for row in statement_rows), 47, "post-state insufficiency")
    inv("ASTRO_GROUP_COUNT", len(astro_rows), 395, "complete local Astro")
    inv("ASTRO_LOCUS_COUNT", len({(row["page"], row["source_locus"]) for row in astro_rows}), 142, "74+37+31")
    inv("F68_F69_SAME_INDEX_FULL_FORM_MATCH", same_index, 0, "no direct join")
    inv("F68_F69_ALL_PAIR_FULL_FORM_MATCH", all_pair, 0, "no direct join")
    inv("F68_F69_DIRECT_JOIN_COUNT", sum("NO_F68_F69_JOIN" not in row["semantic_contract"] for row in astro_rows if row["page"] in {"f68r1", "f69v"}), 0, "namespaces separate")
    inv("UNIFIED_GROUP_COUNT", len(unified_rows), 776, "381+395")
    inv("UNIT_COUNT", len(unit_rows), 14, "11 prose+3 Astro")
    inv("COMPLETE_SOURCE_RECOVERY_WITHOUT_EXEMPLAR", sum(row["complete_source_recovery_without_exemplar"] != "NO" for row in unified_rows), 0, "no standalone semantic codec")
    inv("DOMAIN_WINNER_SELECTED", sum(row["domain_selection"] not in {"NONE;DUAL_UNRESOLVED"} for row in unified_rows), 0, "coequal content fork")
    inv("CONFIRMED_LEXEME_COUNT", sum(row["confirmed_lexeme"] != "NO" for row in card_rows), 0, "scientific ceiling")
    inv("ALLOWED_PAGE_COUNT", len({row["page"] for row in unified_rows}), 10, "fixed ten-page scope")
    inv("COMPILER_TRANSITION_COUNT", len(compiler_rows), 22, "V67 deterministic transducer")

    write_tsv(OUT_CARDS, card_rows)
    write_tsv(OUT_EVENTS, event_rows)
    write_tsv(OUT_FIELDS, field_rows)
    write_tsv(OUT_STATEMENTS, statement_rows)
    write_tsv(OUT_ASTRO, astro_rows)
    write_tsv(OUT_UNIFIED, unified_rows)
    write_tsv(OUT_UNITS, unit_rows)
    write_tsv(OUT_COMPILER, compiler_rows)
    write_tsv(OUT_INVARIANTS, invariant_rows)
    write_tsv(OUT_SOURCES, source_manifest)

    release_specs = [
        (OUT_CARDS, 173, "exact_joint_card_id"),
        (OUT_EVENTS, 381, "event_serial"),
        (OUT_FIELDS, 135, "field_id"),
        (OUT_STATEMENTS, 116, "statement_id"),
        (OUT_ASTRO, 395, "astro_group_serial"),
        (OUT_UNIFIED, 776, "unified_group_id"),
        (OUT_UNITS, 14, "unit_id"),
        (OUT_COMPILER, 22, "transition_id"),
        (OUT_INVARIANTS, len(invariant_rows), "invariant"),
        (OUT_SOURCES, len(source_manifest), "source_path"),
    ]
    release_rows = []
    for path, count, primary_key in release_specs:
        release_rows.append({
            "release_path": rel(path),
            "row_count": str(count),
            "primary_key": primary_key,
            "sha256": digest(path),
            "canonical_status": "V69_R3_DETERMINISTIC_DUAL_RELEASE",
            "semantic_policy": "NO_WINNER;LOCAL_EXEMPLARS;FORMAL_LAYERS_SEPARATE",
        })
    write_tsv(OUT_RELEASE, release_rows)

    print("PASS V69 R3 build")
    print("cards=173 prose_events=381 fields=135 statements=116 astro_groups=395 unified=776 units=14")
    print("mnemonics=11/85 formal=4/45 control_union=14/119 unknown_mnemonic=162/296 exemplar_only=159/262")
    print("resets=11 boundaries=46 crossline_statements=18 f68_f69_matches=0/0 direct_join=0")
    print("source_without_exemplar=0/776 domain_winner=NONE confirmed_lexemes=0")
    print(f"source_manifest={len(source_manifest)} release_manifest={len(release_rows)} invariants={len(invariant_rows)}")


if __name__ == "__main__":
    main()
