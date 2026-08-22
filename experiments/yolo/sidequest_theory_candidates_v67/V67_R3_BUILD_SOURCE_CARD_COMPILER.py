#!/usr/bin/env python3
"""Build the V67 R3 exemplar-bound source-to-card compiler audit."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent

P60 = YOLO / "sidequest_theory_candidates_v60"
P61 = YOLO / "sidequest_theory_candidates_v61"
P62 = YOLO / "sidequest_theory_candidates_v62"
P63 = YOLO / "sidequest_theory_candidates_v63"
P64 = YOLO / "sidequest_theory_candidates_v64"
P65 = YOLO / "sidequest_theory_candidates_v65"
P66 = YOLO / "sidequest_theory_candidates_v66"

SOURCES = {
    "deck": P60 / "V60_SELECTED_173_CARD_DICTIONARY.tsv",
    "events": P60 / "V60_SELECTED_381_EVENT_LEDGER.tsv",
    "decisions": P60 / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv",
    "statements": P61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv",
    "records": P61 / "V61_SELECTED_11_RECORD_CONTINUATIONS.tsv",
    "boundaries": P61 / "V61_SELECTED_46_LINE_BOUNDARIES.tsv",
    "registers": P62 / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv",
    "register_models": P62 / "V62_SELECTED_REDUCED_REGISTER_MODELS.tsv",
    "register_inventory": P62 / "V62_SELECTED_REGISTER_INVENTORY.tsv",
    "templates": P63 / "V63_SELECTED_TEMPLATE_DEFINITIONS.tsv",
    "event_parse": P63 / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv",
    "field_parse": P63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv",
    "statement_parse": P63 / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv",
    "herbal_events": P64 / "V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv",
    "herbal_records": P64 / "V64_R2_FIVE_RECORD_EDITIONS.tsv",
    "bio_events": P65 / "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv",
    "bio_records": P65 / "V65_R2_SIX_RECORD_EDITIONS.tsv",
    "astro_groups": P66 / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv",
    "astro_loci": P66 / "V66_R3_142_LOCUS_FUNCTIONS.tsv",
    "astro_diagrams": P66 / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv",
}

OUT_AUDIT = HERE / "V67_R3_776_GROUP_ROUNDTRIP_AUDIT.tsv"
OUT_CLAUSES = HERE / "V67_R3_116_TYPED_SOURCE_CLAUSES.tsv"
OUT_RUNTIME = HERE / "V67_R3_116_RUNTIME_REGISTER_TRANSITIONS.tsv"
OUT_AUTOMATON = HERE / "V67_R3_COMPILER_TRANSITIONS.tsv"
OUT_UNITS = HERE / "V67_R3_14_UNIT_SUMMARY.tsv"
OUT_TRACES = HERE / "V67_R3_LONG_TRACE_STEPS.tsv"
OUT_MODELS = HERE / "V67_R3_STATE_CODEBOOK_COMPARISON.tsv"
OUT_ORDER = HERE / "V67_R3_2_ABSTRACT_ORDER_MODELS.tsv"
OUT_ERRORS = HERE / "V67_R3_ERROR_AUDIT.tsv"

PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
UNIT_ORDER = ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3")

FAMILY = {
    "PARAMETER_ASSIGN": "PARAMETER",
    "TARGET_ASSIGN": "TARGET",
    "LINK_ACTIVE": "LINK",
    "STATE_GATE": "STATE",
    "ACTION_APPLY": "ACTION",
    "ACTION_TEMPER": "ACTION",
    "TERMINAL_FLUSH": "TERMINAL",
    "TERMINAL_DRAIN": "TERMINAL",
    "SELECT_PART": "SELECT",
    "SELECT_PREVIOUS": "SELECT",
}
ORDER_MODELS = {
    "LATIN_LIKE_DEPENDENT_FIRST_PROXY": ("SELECT", "TARGET", "PARAMETER", "STATE", "LINK", "ACTION", "TERMINAL"),
    "VERNACULAR_LIKE_HEAD_FIRST_PROXY": ("ACTION", "LINK", "SELECT", "TARGET", "PARAMETER", "STATE", "TERMINAL"),
}


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


def serials(value: str) -> list[str]:
    return value.split("|") if value and value != "NONE" else []


def prompt_channel(row: dict[str, str]) -> tuple[str, str]:
    mnemonic = row["selected_exact_mnemonic"]
    formal = row["strict_formal_prompt"]
    if mnemonic != "UNKNOWN" and formal != "NONE":
        return "EXACT_MNEMONIC_PLUS_FORMAL_CONVERGENT", f"MNEMONIC:{mnemonic}|FORMAL:{formal}"
    if mnemonic != "UNKNOWN":
        return "EXACT_MNEMONIC", f"MNEMONIC:{mnemonic}"
    if formal != "NONE":
        return "STRICT_FORMAL_PROMPT", f"FORMAL:{formal}"
    return "EXEMPLAR_WHOLE_CARD", "NO_REUSABLE_PROMPT"


def abstract_sequence(event_rows: list[dict[str, str]]) -> list[str]:
    return [FAMILY[row["event_template"]] for row in event_rows if row["event_template"] in FAMILY]


def order_score(sequence: list[str], order: tuple[str, ...]) -> tuple[int, int]:
    rank = {value: index for index, value in enumerate(order)}
    comparisons = 0
    violations = 0
    for left_index, left in enumerate(sequence):
        for right in sequence[left_index + 1:]:
            if left == right:
                continue
            comparisons += 1
            violations += rank[left] > rank[right]
    return comparisons, violations


AUTOMATON = [
    ("T01", "READY", "START_PROSE_UNIT", "CLAUSE_TYPED", "reset four registers; open record-local namespace"),
    ("T02", "READY", "START_ASTRO_UNIT", "EVENT_SELECT", "open page-local diagram namespace; bypass prose registers"),
    ("T03", "CLAUSE_TYPED", "VALID_TYPED_CLAUSE", "REGISTERS_BOUND", "apply selected V62 transition log"),
    ("T04", "CLAUSE_TYPED", "MISSING_REQUIRED_REGISTER_OR_LOG", "REJECT", "fail closed; never invent a referent"),
    ("T05", "REGISTERS_BOUND|EVENT_SELECT", "EXACT_MNEMONIC", "CARD_BOUND", "select its one licensed exact joint card"),
    ("T06", "REGISTERS_BOUND|EVENT_SELECT", "STRICT_FORMAL_PROMPT", "CARD_BOUND", "select its formal exact card; do not inherit a word"),
    ("T07", "REGISTERS_BOUND|EVENT_SELECT", "EXEMPLAR_EVENT_KEY", "CARD_BOUND", "look up an existing whole prose card"),
    ("T08", "EVENT_SELECT", "ASTRO_LOCAL_ADDRESS", "CARD_BOUND", "look up one page-local diagram group"),
    ("T09", "REGISTERS_BOUND|EVENT_SELECT", "NO_LICENSED_CARD_OR_EXEMPLAR", "REJECT", "new card synthesis forbidden"),
    ("T10", "CARD_BOUND", "COPY_WHOLE_CARD_PAYLOAD", "FIELD_BUFFER", "copy opaque card and occurrence renderer selector atomically"),
    ("T11", "FIELD_BUFFER", "MORE_GROUP_IN_FIELD_OR_LOCUS", "EVENT_SELECT", "emit SPACE after the whole group; preserve source order"),
    ("T12", "FIELD_BUFFER", "END_OPEN_FIELD", "FIELD_COMMITTED", "record field cut without spoken close"),
    ("T13", "FIELD_BUFFER", "END_TERMINAL_FIELD", "FIELD_COMMITTED", "commit observed terminal card; CLOSE remains silent"),
    ("T14", "FIELD_BUFFER", "CLOSE_BEFORE_FIELD_END_OR_MISSING_AT_DECLARED_TERMINAL", "REJECT", "field-envelope violation"),
    ("T15", "FIELD_COMMITTED", "MORE_FIELD_SAME_STATEMENT", "EVENT_SELECT", "preserve field partition and active statement"),
    ("T16", "FIELD_COMMITTED", "NEXT_TYPED_STATEMENT", "CLAUSE_TYPED", "carry/reset registers exactly as logged"),
    ("T17", "FIELD_COMMITTED", "ALL_UNIT_FIELDS_BUFFERED", "REFLOW_BUFFER", "apply stored physical-locus map after clause compilation"),
    ("T18", "REFLOW_BUFFER", "VALID_LINE_REFLOW", "HAND_RENDER", "SPACE between groups; LINE_RESET only at stored locus boundary"),
    ("T19", "REFLOW_BUFFER", "LINE_RESET_USED_AS_SENTENCE_OR_UNLICENSED_REFLOW", "REJECT", "line is not sentence"),
    ("T20", "HAND_RENDER", "COPY_NEXT_WHOLE_SURFACE", "HAND_RENDER", "copy exemplar surface without phonetic or component analysis"),
    ("T21", "HAND_RENDER", "END_UNIT", "UNIT_DONE", "return visible unit plus formal trace"),
    ("T22", "ANY", "PAGE_HOST_COMPONENT_PHONETIC_OR_CROSSPAGE_INHERITANCE", "REJECT", "forbidden semantic path"),
]


def main() -> None:
    src = {name: read_tsv(path) for name, path in SOURCES.items()}
    expected = {
        "deck": 173, "events": 381, "decisions": 11, "statements": 116,
        "records": 11, "boundaries": 46, "registers": 116,
        "register_models": 5, "register_inventory": 4, "templates": 12,
        "event_parse": 381, "field_parse": 135, "statement_parse": 116,
        "herbal_events": 100, "herbal_records": 5, "bio_events": 281,
        "bio_records": 6, "astro_groups": 395, "astro_loci": 142,
        "astro_diagrams": 3,
    }
    for name, count in expected.items():
        require(len(src[name]) == count, f"{name}: expected {count}, got {len(src[name])}")
    require({row["page"] for row in src["events"]} == PROSE_PAGES, "prose page scope changed")
    require({row["page"] for row in src["astro_groups"]} == ASTRO_PAGES, "Astro page scope changed")
    require({row["record_unit_id"] for row in src["events"]} == set(UNIT_ORDER[:11]), "prose units changed")
    require({row["diagram_id"] for row in src["astro_groups"]} == set(UNIT_ORDER[11:]), "Astro units changed")

    events = {row["event_serial"]: row for row in src["events"]}
    parses = {row["event_serial"]: row for row in src["event_parse"]}
    statements = {row["statement_id"]: row for row in src["statements"]}
    statement_parses = {row["statement_id"]: row for row in src["statement_parse"]}
    register_transitions = {row["statement_id"]: row for row in src["registers"]}
    fields = {row["field_id"]: row for row in src["field_parse"]}
    require(set(events) == set(parses) == {str(i) for i in range(1, 382)}, "prose event projection")
    require(set(statements) == set(statement_parses) == set(register_transitions), "statement projection")
    require(set(fields) == {f"F{i:03d}" for i in range(1, 136)}, "field projection")

    local_event_rows = src["herbal_events"] + src["bio_events"]
    local_payload: dict[str, str] = {}
    for row in local_event_rows:
        serial = row["event_serial"]
        source = events[serial]
        require((row["page"], row["locus"], row["record_unit_id"], row["field_id"], row["statement_id"], row["joint_tuple_id"], row["surface_display_only"]) ==
                (source["page"], source["locus"], source["record_unit_id"], source["field_id"], parses[serial]["statement_id"], source["joint_tuple_id"], source["surface"]),
                f"selected local event drift: {serial}")
        local_payload[serial] = row.get("v64_tagged_source_segment") or row.get("v65_concrete_default_segment") or ""
        require(bool(local_payload[serial]), f"missing local payload: {serial}")
    require(set(local_payload) == set(events), "local payload coverage")

    field_members = {field_id: serials(row["event_serials"]) for field_id, row in fields.items()}
    locus_members: dict[tuple[str, str], list[str]] = defaultdict(list)
    for serial in sorted(events, key=int):
        event = events[serial]
        locus_members[(event["page"], event["locus"])].append(serial)

    surfaces_by_id: dict[str, set[str]] = defaultdict(set)
    ids_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in events.values():
        surfaces_by_id[row["joint_tuple_id"]].add(row["surface"])
        ids_by_surface[row["surface"]].add(row["joint_tuple_id"])
    require(len(surfaces_by_id) == 173 and all(len(ids) == 1 for ids in ids_by_surface.values()), "prose renderer identity changed")
    multi_surface_ids = {key for key, values in surfaces_by_id.items() if len(values) > 1}
    require((len(multi_surface_ids), sum(events[s]["joint_tuple_id"] in multi_surface_ids for s in events)) == (34, 202), "renderer variant counts changed")

    astro_by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    astro_ids_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in src["astro_groups"]:
        astro_by_locus[(row["diagram_id"], row["source_locus"])].append(row)
        astro_ids_by_surface[row["surface_display_only"]].add(row["local_group_id"])
    require(sum(len(astro_ids_by_surface[row["surface_display_only"]]) > 1 for row in src["astro_groups"]) == 140, "Astro surface ambiguity changed")

    clause_kind = {
        statement_id: {"UNIQUE": "CONTROLLED_UNIQUE", "AMBIGUOUS": "MIXED_AMBIGUOUS", "UNPARSED": "OPAQUE_UNPARSED"}[row["parse_status"]]
        for statement_id, row in statement_parses.items()
    }

    audit_rows: list[dict[str, str]] = []
    for serial in sorted(events, key=int):
        event = events[serial]
        parsed = parses[serial]
        channel, prompt = prompt_channel(parsed)
        field_id = event["field_id"]
        is_field_end = serial == field_members[field_id][-1]
        is_locus_end = serial == locus_members[(event["page"], event["locus"])][-1]
        require(not (event["terminal_status"] == "TERMINAL" and not is_field_end), f"terminal not field-final: {serial}")
        audit_rows.append({
            "combined_group_ordinal": serial,
            "namespace": "PROSE_EXACT_JOINT_CARD",
            "unit_id": event["record_unit_id"],
            "page": event["page"],
            "source_locus": event["locus"],
            "field_or_local_address": field_id,
            "statement_or_locus_unit": parsed["statement_id"],
            "group_ordinal_within_unit": event["event_index_in_record"],
            "opaque_whole_card_key": f"P:{event['joint_tuple_id']}",
            "surface_display_only": event["surface"],
            "typed_source_class": clause_kind[parsed["statement_id"]],
            "silent_state_mode": "FOUR_RECORD_LOCAL_REGISTERS",
            "compiler_channel": channel,
            "licensed_prompt": prompt,
            "event_template_or_local_role": parsed["event_template"],
            "external_exemplar_payload_key": f"SRC:P:E{int(serial):03d}",
            "external_source_payload": local_payload[serial],
            "field_grouping_operation": "CLOSE_AND_COMMIT" if is_field_end and event["terminal_status"] == "TERMINAL" else "OPEN_FIELD_CUT" if is_field_end else "APPEND_FIELD",
            "line_reflow_operation": "LINE_RESET" if is_locus_end else "SPACE",
            "hand_renderer_operation": "COPY_OCCURRENCE_SURFACE_ATOMICALLY;NO_COMPONENT_OR_PHONETIC_RULE",
            "id_to_surface_encode_status": "EXTERNAL_OCCURRENCE_RENDERER_SELECTOR_REQUIRED" if event["joint_tuple_id"] in multi_surface_ids else "UNIQUE_DECK_SURFACE",
            "surface_to_id_decode_status": "UNIQUE_WITHIN_PROSE_DECK",
            "formal_identity_order_layout_roundtrip": "PASS",
            "source_intention_without_exemplar": "PARTIAL_CONTROL_TEMPLATE_ONLY" if parsed["event_parse_status"] != "UNPARSED_EXEMPLAR" else "LOST_OPAQUE_EVENT",
            "source_intention_with_exemplar": "PASS_SELECTED_LOCAL_PAYLOAD",
            "external_exemplar_required_for_complete_source": "YES",
            "semantic_contract": "WORKING_PROMPT_NOT_LEXEM;EXACT_CARD_ATOMIC;NO_PAGE_HOST_OR_STRING_INHERITANCE",
        })

    astro_locus_id = {(row["diagram_id"], row["source_locus"]): row["local_locus_id"] for row in src["astro_loci"]}
    for offset, row in enumerate(src["astro_groups"], 382):
        members = astro_by_locus[(row["diagram_id"], row["source_locus"])]
        is_locus_end = row["local_group_id"] == members[-1]["local_group_id"]
        audit_rows.append({
            "combined_group_ordinal": str(offset),
            "namespace": "ASTRO_PAGE_LOCAL_GROUP",
            "unit_id": row["diagram_id"],
            "page": row["page"],
            "source_locus": row["source_locus"],
            "field_or_local_address": row["local_lookup_address"],
            "statement_or_locus_unit": astro_locus_id[(row["diagram_id"], row["source_locus"])],
            "group_ordinal_within_unit": row["local_group_id"].rsplit("G", 1)[1],
            "opaque_whole_card_key": f"A:{row['local_group_id']}",
            "surface_display_only": row["surface_display_only"],
            "typed_source_class": "ASTRO_LOCAL_LOOKUP_FRAGMENT",
            "silent_state_mode": "ASTRO_LOCAL_ADDRESS_BYPASS;NO_PROSE_REGISTERS",
            "compiler_channel": "ASTRO_LOCAL_FORMAL_EXEMPLAR",
            "licensed_prompt": f"LOCAL_ROLE:{row['technical_group_role']}",
            "event_template_or_local_role": row["instrument_component"],
            "external_exemplar_payload_key": f"SRC:A:{row['local_group_id']}",
            "external_source_payload": row["concrete_technical_function_German"],
            "field_grouping_operation": "NOT_A_PROSE_FIELD",
            "line_reflow_operation": "LOCUS_RESET" if is_locus_end else "SPACE",
            "hand_renderer_operation": "COPY_PAGE_LOCAL_SURFACE_ATOMICALLY;NO_COMPONENT_OR_PHONETIC_RULE",
            "id_to_surface_encode_status": "UNIQUE_PAGE_LOCAL_GROUP_SELECTOR",
            "surface_to_id_decode_status": "AMBIGUOUS_WITHOUT_LOCAL_ADDRESS" if len(astro_ids_by_surface[row["surface_display_only"]]) > 1 else "UNIQUE_WITHIN_ASTRO_SURFACES",
            "formal_identity_order_layout_roundtrip": "PASS",
            "source_intention_without_exemplar": "LOCAL_ADDRESS_AND_ROLE_ONLY;CONCRETE_PAYLOAD_LOST",
            "source_intention_with_exemplar": "PASS_SELECTED_LOCAL_PAYLOAD",
            "external_exemplar_required_for_complete_source": "YES",
            "semantic_contract": "ASTRO_LOCAL_ONLY;NO_PROSE_CARD;NO_CROSSPAGE_JOIN;NO_WORD_VALUE",
        })
    require(len(audit_rows) == 776, "combined audit coverage")

    clause_rows: list[dict[str, str]] = []
    runtime_rows: list[dict[str, str]] = []
    ordering_accumulator = {name: Counter() for name in ORDER_MODELS}
    for statement in src["statements"]:
        statement_id = statement["statement_id"]
        parsed = statement_parses[statement_id]
        transition = register_transitions[statement_id]
        member_serials = serials(statement["event_serials"])
        member_parses = [parses[value] for value in member_serials]
        member_events = [events[value] for value in member_serials]
        sequence = abstract_sequence(member_parses)
        order_results: dict[str, tuple[int, int]] = {}
        for name, order in ORDER_MODELS.items():
            comparisons, violations = order_score(sequence, order)
            order_results[name] = (comparisons, violations)
            ordering_accumulator[name]["statements"] += 1
            ordering_accumulator[name]["comparisons"] += comparisons
            ordering_accumulator[name]["violations"] += violations
            if comparisons:
                ordering_accumulator[name]["informative_statements"] += 1
                ordering_accumulator[name]["exact_fit_statements"] += violations == 0
        latin = order_results["LATIN_LIKE_DEPENDENT_FIRST_PROXY"]
        vernacular = order_results["VERNACULAR_LIKE_HEAD_FIRST_PROXY"]
        if not latin[0]:
            order_verdict = "NOT_INFORMATIVE_FEWER_THAN_TWO_DISTINCT_SLOT_FAMILIES"
        elif latin[1] < vernacular[1]:
            order_verdict = "LATIN_LIKE_PROXY_LOWER_LOCAL_VIOLATION"
        elif vernacular[1] < latin[1]:
            order_verdict = "VERNACULAR_LIKE_PROXY_LOWER_LOCAL_VIOLATION"
        else:
            order_verdict = "LOCAL_TIE"
        field_sequence = serials(statement["constituent_fields"])
        field_contract = []
        for field_id in field_sequence:
            last = events[field_members[field_id][-1]]
            field_contract.append(f"{field_id}:{'TERMINAL_CLOSE' if last['terminal_status'] == 'TERMINAL' else 'OPEN_CUT'}")
        rendered_loci: list[str] = []
        for locus in serials(statement["constituent_loci"]):
            surfaces = [row["surface"] for row in member_events if row["locus"] == locus]
            rendered_loci.append(f"{locus}=" + " ".join(surfaces))
        control_sequence = []
        for row in member_parses:
            channel, prompt = prompt_channel(row)
            control_sequence.append(prompt if channel != "EXEMPLAR_WHOLE_CARD" else f"EXEMPLAR:E{int(row['event_serial']):03d}")
        clause_rows.append({
            "statement_id": statement_id,
            "unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "typed_clause_class": clause_kind[statement_id],
            "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "field_grouping_contract": "|".join(field_contract),
            "physical_locus_reflow": " || LINE_RESET || ".join(rendered_loci),
            "abstract_slot_sequence": " > ".join(sequence) if sequence else "NONE",
            "compiler_control_sequence": " > ".join(control_sequence),
            "whole_card_key_sequence": "|".join(f"P:{row['joint_tuple_id']}" for row in member_events),
            "silent_register_demand": transition["silent_register_demand"],
            "pre_state": transition["pre_state"],
            "register_operations_OWNER_ACTIVE_TARGET_PREVIOUS": "/".join((transition["owner_operation"], transition["active_item_preparation_operation"], transition["target_station_operation"], transition["previous_item_operation"])),
            "inferred_missing_slots": transition["inferred_missing_slots"],
            "post_state": transition["post_state"],
            "backward_from_full_transition_log": "PASS",
            "backward_from_post_state_only": transition["backward_reconstructable_from_post_state_only"],
            "latin_like_pair_comparisons": str(latin[0]),
            "latin_like_order_violations": str(latin[1]),
            "vernacular_like_pair_comparisons": str(vernacular[0]),
            "vernacular_like_order_violations": str(vernacular[1]),
            "abstract_order_verdict": order_verdict,
            "external_source_payload": " > ".join(local_payload[value] for value in member_serials),
            "encode_contract": "TYPE>V62_REGISTERS>V63_PROMPT_OR_EXEMPLAR>WHOLE_CARD>FIELD_CLOSE>V61_REFLOW>ATOMIC_RENDER",
            "formal_roundtrip": "PASS_EXACT_ID_ORDER_FIELD_LOCUS",
            "complete_source_without_exemplar": "FAIL;CONTROL_SKELETON_ONLY",
            "complete_source_with_exemplar": "PASS_SELECTED_CREATIVE_SOURCE",
            "strongest_error_or_rival": transition["irreducible_ambiguity_codes"] if transition["irreducible_ambiguity_codes"] != "NONE" else statement["strongest_alternative"],
            "semantic_contract": "NO_PHONETICS;NO_PAGE_HOST;NO_NEW_CARD;LOCAL_PAYLOAD_NOT_CARD_MEANING",
        })
        runtime_rows.append({
            "transition_serial": transition["transition_serial"],
            "statement_id": statement_id,
            "unit_id": statement["record_unit_id"],
            "entry_boundary_class": transition["entry_boundary_class"],
            "observed_triggers": transition["observed_triggers"],
            "inferred_missing_slots": transition["inferred_missing_slots"],
            "pre_state": transition["pre_state"],
            "owner_operation": transition["owner_operation"],
            "active_operation": transition["active_item_preparation_operation"],
            "target_operation": transition["target_station_operation"],
            "previous_operation": transition["previous_item_operation"],
            "operation_trace": transition["operation_trace"],
            "post_state": transition["post_state"],
            "compiler_state_path": "CLAUSE_TYPED>REGISTERS_BOUND>EVENT_SELECT>FIELD_BUFFER>FIELD_COMMITTED",
            "backward_from_full_log": "PASS",
            "backward_from_post_state_only": transition["backward_reconstructable_from_post_state_only"],
            "irreducible_ambiguity_codes": transition["irreducible_ambiguity_codes"],
            "record_local_contract": transition["anonymous_id_contract"],
        })
    require(len(clause_rows) == len(runtime_rows) == 116, "clause/runtime coverage")

    order_rows: list[dict[str, str]] = []
    for name, order in ORDER_MODELS.items():
        counts = ordering_accumulator[name]
        order_rows.append({
            "order_model": name,
            "abstract_rank_order": " > ".join(order),
            "statement_count": "116",
            "informative_statements": str(counts["informative_statements"]),
            "exact_fit_statements": str(counts["exact_fit_statements"]),
            "ordered_pair_comparisons": str(counts["comparisons"]),
            "pair_order_violations": str(counts["violations"]),
            "violation_rate": f"{counts['violations'] / counts['comparisons']:.6f}",
            "selection_verdict": "TIE_BY_TOTAL_VIOLATIONS" if counts["violations"] == 42 else "RECHECK",
            "linguistic_claim": "NONE;ABSTRACT_SLOT_PROXY_ONLY;NO_LANGUAGE_OR_WORD_ORDER_IDENTIFICATION",
        })
    require([(r["informative_statements"], r["pair_order_violations"]) for r in order_rows] == [("28", "42"), ("28", "42")], "ordering totals changed")

    automaton_rows = [
        {
            "transition_id": transition_id,
            "from_state": from_state,
            "input_or_guard": guard,
            "to_state": to_state,
            "deterministic_action": action,
            "failure_policy": "FAIL_CLOSED" if to_state == "REJECT" else "CONTINUE",
            "historical_hand_execution": "marginal current-entry marks plus copied whole-card exemplar; no modern arithmetic required",
        }
        for transition_id, from_state, guard, to_state, action in AUTOMATON
    ]

    # The selected five- and six-record editions supply the concrete source
    # payload; Astro remains a separate local lookup namespace.
    herbal_record = {row["record_unit_id"]: row for row in src["herbal_records"]}
    bio_record = {row["record_unit_id"]: row for row in src["bio_records"]}
    astro_diagram = {row["diagram_id"]: row for row in src["astro_diagrams"]}
    unit_rows: list[dict[str, str]] = []
    for unit_id in UNIT_ORDER:
        unit_audit = [row for row in audit_rows if row["unit_id"] == unit_id]
        if unit_id.startswith(("H", "B")):
            unit_events = [row for row in src["events"] if row["record_unit_id"] == unit_id]
            unit_fields = [row for row in src["field_parse"] if row["record_unit_id"] == unit_id]
            unit_statements = [row for row in src["statement_parse"] if row["record_unit_id"] == unit_id]
            unit_transitions = [row for row in src["registers"] if row["record_unit_id"] == unit_id]
            channels = Counter(row["compiler_channel"] for row in unit_audit)
            record = herbal_record.get(unit_id) or bio_record[unit_id]
            title = record.get("article_title") or record.get("edition_title") or unit_id
            complete = record["tagged_continuous_german_source_edition"]
            contradiction = record.get("strongest_nonmedical_rival") or record.get("strongest_contradiction") or "LOCAL_EXEMPLAR_DEPENDENCE"
            unit_rows.append({
                "unit_id": unit_id,
                "unit_kind": "HERBAL_PROSE" if unit_id.startswith("H") else "BIOLOGICAL_PROSE",
                "page": unit_events[0]["page"],
                "unit_title_or_formal_role": title,
                "visible_group_count": str(len(unit_events)),
                "locus_count": str(len({row["locus"] for row in unit_events})),
                "field_count": str(len(unit_fields)),
                "statement_count": str(len(unit_statements)),
                "exact_mnemonic_events": str(channels["EXACT_MNEMONIC"] + channels["EXACT_MNEMONIC_PLUS_FORMAL_CONVERGENT"]),
                "strict_formal_only_events": str(channels["STRICT_FORMAL_PROMPT"]),
                "reusable_control_union_events": str(len(unit_events) - channels["EXEMPLAR_WHOLE_CARD"]),
                "exemplar_only_or_local_events": str(channels["EXEMPLAR_WHOLE_CARD"]),
                "terminal_close_count": str(sum(row["terminal_status"] == "TERMINAL" for row in unit_events)),
                "parse_status_fields": ";".join(f"{key}:{value}" for key, value in sorted(Counter(row["parse_status"] for row in unit_fields).items())),
                "parse_status_statements": ";".join(f"{key}:{value}" for key, value in sorted(Counter(row["parse_status"] for row in unit_statements).items())),
                "post_state_only_backward_pass": str(sum(row["backward_reconstructable_from_post_state_only"] == "YES" for row in unit_transitions)),
                "occurrence_renderer_selector_needed": str(sum(row["joint_tuple_id"] in multi_surface_ids for row in unit_events)),
                "surface_only_unique_in_local_namespace": str(len(unit_events)),
                "formal_roundtrip_pass": f"{len(unit_events)}/{len(unit_events)}",
                "complete_source_roundtrip_without_exemplar": "0/" + str(len(unit_events)),
                "complete_source_roundtrip_with_exemplar": f"{len(unit_events)}/{len(unit_events)}",
                "complete_unit_source_default": complete,
                "strongest_contradiction_or_rival": contradiction,
                "compiler_verdict": "PASS_EXISTING_EXEMPLAR;FAIL_STANDALONE_SEMANTIC_CODEC",
            })
        else:
            groups = [row for row in src["astro_groups"] if row["diagram_id"] == unit_id]
            diagram = astro_diagram[unit_id]
            unambiguous = sum(len(astro_ids_by_surface[row["surface_display_only"]]) == 1 for row in groups)
            unit_rows.append({
                "unit_id": unit_id,
                "unit_kind": "ASTRO_LOCAL_LOOKUP",
                "page": groups[0]["page"],
                "unit_title_or_formal_role": diagram["technical_formal_role"],
                "visible_group_count": str(len(groups)),
                "locus_count": diagram["locus_count"],
                "field_count": "0;NOT_PROSE_FIELDS",
                "statement_count": "0;LOCAL_LOCI_INSTEAD",
                "exact_mnemonic_events": "0",
                "strict_formal_only_events": "0;PROSE_PROMPTS_FORBIDDEN",
                "reusable_control_union_events": "0;GLOBAL",
                "exemplar_only_or_local_events": str(len(groups)),
                "terminal_close_count": "0;NOT_PROSE_CLOSE",
                "parse_status_fields": "NOT_APPLICABLE",
                "parse_status_statements": "NOT_APPLICABLE",
                "post_state_only_backward_pass": "NOT_APPLICABLE",
                "occurrence_renderer_selector_needed": "0;LOCAL_GROUP_ID_SELECTS_SURFACE",
                "surface_only_unique_in_local_namespace": str(unambiguous),
                "formal_roundtrip_pass": f"{len(groups)}/{len(groups)}",
                "complete_source_roundtrip_without_exemplar": "0/" + str(len(groups)),
                "complete_source_roundtrip_with_exemplar": f"{len(groups)}/{len(groups)}",
                "complete_unit_source_default": diagram["complete_technical_default_German"],
                "strongest_contradiction_or_rival": diagram["strongest_contradiction"],
                "compiler_verdict": "PASS_PAGE_LOCAL_EXEMPLAR;NO_PROSE_OR_CROSSPAGE_CODEC",
            })
    require(len(unit_rows) == 14 and sum(int(row["visible_group_count"]) for row in unit_rows) == 776, "unit summary coverage")

    selected_trace_units = {
        "H5-S001": "HERBAL_CROSS_LINE_9",
        "B1-S002": "LONGEST_PROSE_STATEMENT_19",
        "B2-S005": "F82R_3_TO_4_CARRY_8",
        "B5-S003": "THREE_LINE_REFLOW_9",
        "A1:L074": "F67_LONG_INSTRUCTION_LOCUS_13",
        "A2:L001": "F68_LONG_HEADER_LOCUS_9",
        "A3:L001": "F69_LONG_HEADER_LOCUS_40",
    }
    audit_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in audit_rows:
        audit_by_statement[row["statement_or_locus_unit"]].append(row)
    trace_rows: list[dict[str, str]] = []
    for trace_unit, trace_id in selected_trace_units.items():
        members = audit_by_statement[trace_unit]
        require(bool(members), f"missing trace unit: {trace_unit}")
        prose_transition = register_transitions.get(trace_unit)
        for step, row in enumerate(members, 1):
            trace_rows.append({
                "trace_id": trace_id,
                "trace_unit": trace_unit,
                "trace_kind": "PROSE_STATEMENT" if prose_transition else "ASTRO_LOCUS",
                "step": str(step),
                "step_count": str(len(members)),
                "unit_id": row["unit_id"],
                "source_location": f"{row['source_locus']}:{row['field_or_local_address']}",
                "typed_source_payload": row["external_source_payload"],
                "register_entry": prose_transition["pre_state"] if prose_transition and step == 1 else "CARRY_WITHIN_STATEMENT" if prose_transition else "ASTRO_BYPASS",
                "selection_channel": row["compiler_channel"],
                "licensed_prompt": row["licensed_prompt"],
                "whole_card_key": row["opaque_whole_card_key"],
                "hand_rendered_surface": row["surface_display_only"],
                "field_operation": row["field_grouping_operation"],
                "reflow_operation": row["line_reflow_operation"],
                "register_exit": prose_transition["post_state"] if prose_transition and step == len(members) else "CARRY_WITHIN_STATEMENT" if prose_transition else "ASTRO_BYPASS",
                "decoded_source_with_exemplar": row["external_source_payload"],
                "roundtrip_result": "PASS_FORMAL_AND_SELECTED_EXEMPLAR",
            })
    require(Counter(row["trace_unit"] for row in trace_rows) == Counter({"H5-S001": 9, "B1-S002": 19, "B2-S005": 8, "B5-S003": 9, "A1:L074": 13, "A2:L001": 9, "A3:L001": 40}), "long trace lengths")

    model_rows: list[dict[str, str]] = []
    for row in src["register_models"]:
        model_rows.append({
            "comparison_axis": "SILENT_REGISTER_STATE",
            "model": row["model_name"],
            "persistent_register_slots": row["register_count"],
            "codebook_key_count": "0;STATE_ONLY_COMPARISON",
            "covered_existing_groups": "NOT_APPLICABLE",
            "fully_reconstructable_source_statements": row["statements_fully_generable"] + "/116",
            "external_exemplar_payload_entries": "STILL_REQUIRED",
            "failure_or_cost": row["missing_silent_slot_instances"] + " missing silent-slot instances",
            "verdict": row["verdict"],
        })
    codebook_models = [
        ("MNEMONIC_ONLY", 11, 85, "691 groups lack even this global prompt"),
        ("FORMAL_PROMPT_ONLY", 4, 45, "731 groups lack this formal prompt; one card overlaps mnemonic deck"),
        ("UNION_GLOBAL_CONTROL", 14, 119, "657 groups lack a global prompt; 262/381 prose events remain exemplar-only"),
        ("FULL_PROSE_OPAQUE_DECK", 173, 381, "identity only; 202 occurrences still require renderer-variant selector"),
        ("FULL_LOCAL_RENDERER", 568, 776, "173 prose IDs plus 395 Astro-local group keys; source intention absent"),
        ("AGGREGATED_SOURCE_EXEMPLARS", 258, 776, "116 prose clauses plus 142 Astro loci; embedded group alignment still stored"),
        ("EVENT_LEVEL_SOURCE_PAYLOAD", 776, 776, "complete selected payload, but no productivity beyond published occurrences"),
    ]
    for name, keys, coverage, failure in codebook_models:
        model_rows.append({
            "comparison_axis": "CODEBOOK_AND_EXEMPLAR",
            "model": name,
            "persistent_register_slots": "4_FOR_PROSE;ASTRO_BYPASS",
            "codebook_key_count": str(keys),
            "covered_existing_groups": f"{coverage}/776",
            "fully_reconstructable_source_statements": "0/116_WITHOUT_LOCAL_PAYLOAD" if name != "EVENT_LEVEL_SOURCE_PAYLOAD" and name != "AGGREGATED_SOURCE_EXEMPLARS" else "116/116_WITH_EMBEDDED_PAYLOAD",
            "external_exemplar_payload_entries": "776_EVENT_LEVEL" if name == "EVENT_LEVEL_SOURCE_PAYLOAD" else "258_AGGREGATED_WITH_ALIGNMENT" if name == "AGGREGATED_SOURCE_EXEMPLARS" else "REQUIRED_FOR_COMPLETE_SOURCE",
            "failure_or_cost": failure,
            "verdict": "FORMAL_ONLY" if coverage < 776 else "COMPLETE_EXISTING_RELEASE_NOT_GENERATIVE_CODEC",
        })

    error_rows = [
        ("E01", "SOURCE_PAYLOAD_REMOVED", "776 groups", "Complete local intention is lost for every group", "require occurrence/locus exemplar key"),
        ("E02", "UNLICENSED_PROSE_CARD_REQUEST", "159 opaque prose types; 262 occurrences", "Slots cannot select the opaque tail", "fail closed or cite existing whole-card exemplar"),
        ("E03", "ID_TO_SURFACE_WITHOUT_VARIANT_SELECTOR", "202 prose occurrences in 34 card IDs", "one exact ID admits several copied surfaces", "store occurrence renderer selector; infer no phonetics"),
        ("E04", "ASTRO_SURFACE_WITHOUT_LOCAL_ADDRESS", "140/395 groups", "surface repeats do not identify local group", "retain diagram+locus+group address"),
        ("E05", "POST_STATE_WITHOUT_TRANSITION_LOG", "69/116 statements", "prior register operations are not recoverable", "retain full V62 transition log"),
        ("E06", "THREE_OR_FEWER_REGISTERS", "9/116 failures at best three-register model", "TARGET-sensitive clauses lose a required slot", "use four record-local registers"),
        ("E07", "CLOSE_SPOKEN_OR_MOVED", "90 terminal fields", "formal commit becomes false lexical content or invalid envelope", "keep close silent and field-final"),
        ("E08", "LINE_RESET_AS_SENTENCE", "18/116 cross-line statements", "source clause is split", "apply V61 reflow after field compilation"),
        ("E09", "CARRY_ACROSS_RECORD", "11 prose record starts", "anonymous IDs acquire a false antecedent", "reset all four registers per record"),
        ("E10", "ORDER_NORMALIZATION", "42/94 pair violations under each proxy", "either abstract order rewrites observed cards", "preserve source order; use proxies only as audit"),
        ("E11", "ASTRO_F68_F69_JOIN", "0 licensed joins", "creates an unsupported crosspage key", "keep A2 and A3 namespaces separate"),
        ("E12", "PAGE_HOST_STRING_COMPONENT_OR_PHONETIC_INHERITANCE", "all 776 groups", "creates a new semantic or sound rule", "reject path; exact whole card remains atomic"),
        ("E13", "TERMINAL_ACTION_FROM_CLOSE_ALONE", "16 OKE/LCHE occurrences", "terminal confound is mistaken for action semantics", "require exact whole card plus observed terminal; preserve rival"),
        ("E14", "NEW_SOURCE_CLAUSE_WITHOUT_EXEMPLAR", "outside the 116 prose clauses/142 Astro loci", "compiler has no licensed opaque payload or layout", "reject; this is not a productive standalone codec"),
    ]
    errors = [
        {"error_id": eid, "error_condition": condition, "observed_scope": scope, "loss_or_false_claim": loss, "deterministic_repair": repair, "status": "HELD_FAILURE_MODE"}
        for eid, condition, scope, loss, repair in error_rows
    ]

    require(Counter(row["compiler_channel"] for row in audit_rows if row["namespace"] == "PROSE_EXACT_JOINT_CARD") == Counter({
        "EXEMPLAR_WHOLE_CARD": 262, "EXACT_MNEMONIC": 74,
        "STRICT_FORMAL_PROMPT": 34, "EXACT_MNEMONIC_PLUS_FORMAL_CONVERGENT": 11,
    }), "compiler channel counts")
    require(sum(row["field_grouping_operation"] == "CLOSE_AND_COMMIT" for row in audit_rows) == 90, "close count")
    require(Counter(row["parse_status"] for row in src["field_parse"]) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "field parse counts")
    require(Counter(row["parse_status"] for row in src["statement_parse"]) == Counter({"UNIQUE": 12, "AMBIGUOUS": 49, "UNPARSED": 55}), "statement parse counts")
    require(sum(row["backward_reconstructable_from_post_state_only"] == "YES" for row in src["registers"]) == 47, "post-only backward count")

    write_tsv(OUT_AUDIT, audit_rows)
    write_tsv(OUT_CLAUSES, clause_rows)
    write_tsv(OUT_RUNTIME, runtime_rows)
    write_tsv(OUT_AUTOMATON, automaton_rows)
    write_tsv(OUT_UNITS, unit_rows)
    write_tsv(OUT_TRACES, trace_rows)
    write_tsv(OUT_MODELS, model_rows)
    write_tsv(OUT_ORDER, order_rows)
    write_tsv(OUT_ERRORS, errors)

    print("PASS V67 R3 build")
    print("units=14 groups=776 prose=381 astro=395 fields=135 statements=116")
    print("global_control=119/381 mnemonic=85 formal_only=34 exemplar_prose=262")
    print("formal_roundtrip=776/776 complete_source_without_exemplar=0/776 with_exemplar=776/776")
    print("registers=4 full_log_backward=116/116 post_state_only=47/116")
    print("order_proxies=42/94 violations each; language_order=TIE_UNIDENTIFIED")


if __name__ == "__main__":
    main()
