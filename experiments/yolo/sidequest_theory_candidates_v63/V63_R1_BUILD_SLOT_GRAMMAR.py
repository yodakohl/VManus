#!/usr/bin/env python3
"""Build the blinded R1 V63 slot-grammar artifacts from selected V60--V62 ledgers."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

EVENT_PATH = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
STATEMENT_PATH = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
TRANSITION_PATH = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
INVENTORY_PATH = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_REGISTER_INVENTORY.tsv"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
TEMPLATE_ORDER = [
    "PARAMETER_ASSIGNMENT",
    "TARGET_ASSIGNMENT",
    "RELATION_LINK",
    "STATE_CHECK_GATE",
    "ACTION",
    "TERMINAL_ACTION",
    "SELECTION_REFERENCE",
]

EXACT_TO_TEMPLATE = {
    "MASS?": "PARAMETER_ASSIGNMENT",
    "ANWENDEN?": "ACTION",
    "BEREIT?": "STATE_CHECK_GATE",
    "ANSATZ?": "SELECTION_REFERENCE",
    "ZIEL?": "TARGET_ASSIGNMENT",
    "KLAR?": "STATE_CHECK_GATE",
    "VORIGES?": "SELECTION_REFERENCE",
    "ANTEIL?": "SELECTION_REFERENCE",
    "TEMPERIEREN?": "ACTION",
    "SPÜLEN?": "TERMINAL_ACTION",
    "ABLASSEN?": "TERMINAL_ACTION",
}

FORMAL_TO_TEMPLATE = {
    "SET(<ARG_AIIN>)": ("SET(ARG_AIIN)", "PARAMETER_ASSIGNMENT"),
    "SET(<ARG_AL>)": ("SET(ARG_AL)", "TARGET_ASSIGNMENT"),
    "FRAME_O(LINK)": ("FRAME_O(LINK)", "RELATION_LINK"),
    "MARK(<ARG_AIIN>)": ("MARK(ARG_AIIN)", "SELECTION_REFERENCE"),
    "MARK(<ARG_AL>)": ("MARK(ARG_AL)", "SELECTION_REFERENCE"),
    "MARK(<ARG_AR>)": ("MARK(ARG_AR)", "SELECTION_REFERENCE"),
}

STATE_KEYS = {
    "OWNER": "OWNER",
    "ACTIVE_ITEM/PREPARATION": "ACTIVE",
    "TARGET/STATION": "TARGET",
    "PREVIOUS_ITEM": "PREVIOUS",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def split_pipe(value: str) -> list[str]:
    if not value or value == "NONE":
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def parse_state(value: str) -> dict[str, str]:
    state: dict[str, str] = {}
    for item in value.split(";"):
        key, val = item.split("=", 1)
        state[STATE_KEYS[key]] = val
    assert set(state) == {"OWNER", "ACTIVE", "TARGET", "PREVIOUS"}
    return state


def render_state(state: dict[str, str]) -> str:
    return ";".join(f"{key}={state[key]}" for key in ("OWNER", "ACTIVE", "TARGET", "PREVIOUS"))


def anchor_for_event(event: dict[str, str]) -> dict[str, str] | None:
    mnemonic = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
    formula = event["formal_formula_opaque"]
    exact = mnemonic in EXACT_TO_TEMPLATE
    formal = formula in FORMAL_TO_TEMPLATE
    assert not (exact and formal), f"overlapping licenses at event {event['event_serial']}"
    if exact:
        return {
            "kind": "EXACT",
            "trigger": mnemonic,
            "template": EXACT_TO_TEMPLATE[mnemonic],
        }
    if formal:
        trigger, template = FORMAL_TO_TEMPLATE[formula]
        return {"kind": "FORMAL", "trigger": trigger, "template": template}
    return None


def choose_register(
    pre: dict[str, str],
    post: dict[str, str],
    key: str,
    *,
    prefer_post: bool = False,
) -> tuple[str, str, list[str]]:
    first, first_name = (post, "POST") if prefer_post else (pre, "PRE")
    second, second_name = (pre, "PRE") if prefer_post else (post, "POST_FALLBACK")
    if first[key] != "UNSET":
        return first[key], first_name, []
    if second[key] != "UNSET":
        flag = "POST_FALLBACK_ORDER_UNRESOLVED" if second_name == "POST_FALLBACK" else "PREVIOUS_VALUE_REUSED"
        return second[key], second_name, [flag]
    return "UNRESOLVED", "UNSET", [f"REQUIRED_{key}_UNSET"]


def owner_context(pre: dict[str, str], post: dict[str, str]) -> tuple[str, list[str]]:
    value, source, flags = choose_register(pre, post, "OWNER")
    return f"OWNER={value}[{source}]", flags


def bind_anchor(
    event: dict[str, str],
    anchor: dict[str, str],
    transition: dict[str, str],
) -> tuple[str, list[str]]:
    pre = parse_state(transition["pre_state"])
    post = parse_state(transition["post_state"])
    template = anchor["template"]
    trigger = anchor["trigger"]
    pieces: list[str] = []
    flags: list[str] = []
    owner, owner_flags = owner_context(pre, post)
    pieces.append(owner)
    flags.extend(owner_flags)

    if template == "PARAMETER_ASSIGNMENT":
        active, source, local_flags = choose_register(pre, post, "ACTIVE")
        pieces.extend((f"ACTIVE={active}[{source}]", f"PARAMETER_PROMPT={trigger}"))
        flags.extend(local_flags)
    elif template == "TARGET_ASSIGNMENT":
        active, active_source, active_flags = choose_register(pre, post, "ACTIVE")
        target, target_source, target_flags = choose_register(pre, post, "TARGET", prefer_post=True)
        pieces.extend(
            (
                f"ACTIVE={active}[{active_source}]",
                f"TARGET={target}[{target_source}]",
                f"TARGET_PROMPT={trigger}",
            )
        )
        flags.extend(active_flags + target_flags)
        if pre["TARGET"] != "UNSET" and post["TARGET"] != pre["TARGET"]:
            flags.append("TARGET_OVERWRITE_HISTORY_REQUIRED")
        flags.append("TARGET_REFERENT_REMAINS_ANONYMOUS")
    elif template == "RELATION_LINK":
        active, active_source, active_flags = choose_register(pre, post, "ACTIVE")
        pieces.append(f"ACTIVE={active}[{active_source}]")
        flags.extend(active_flags)
        if pre["PREVIOUS"] != "UNSET":
            other, other_source = pre["PREVIOUS"], "PREVIOUS@PRE"
        elif pre["TARGET"] != "UNSET":
            other, other_source = pre["TARGET"], "TARGET@PRE"
        else:
            other, other_source = "UNRESOLVED", "NO_PRE_ENDPOINT"
            flags.append("REQUIRED_RELATION_ENDPOINT_UNSET")
        pieces.extend((f"OTHER={other}[{other_source}]", f"LINK_PROMPT={trigger}"))
        if post["PREVIOUS"] != pre["PREVIOUS"] or post["TARGET"] != pre["TARGET"]:
            flags.append("WITHIN_STATEMENT_LINK_ORDER_UNRESOLVED")
    elif template == "STATE_CHECK_GATE":
        active, source, local_flags = choose_register(pre, post, "ACTIVE")
        pieces.extend((f"ACTIVE={active}[{source}]", f"STATE_PROMPT={trigger}", "RESULT=UNRESOLVED"))
        flags.extend(local_flags)
    elif template in {"ACTION", "TERMINAL_ACTION"}:
        active, source, local_flags = choose_register(pre, post, "ACTIVE")
        target = pre["TARGET"] if pre["TARGET"] != "UNSET" else post["TARGET"]
        target_source = "PRE" if pre["TARGET"] != "UNSET" else ("POST_FALLBACK" if target != "UNSET" else "OPTIONAL_UNSET")
        pieces.extend(
            (
                f"ACTIVE={active}[{source}]",
                f"TARGET={target}[{target_source}]",
                f"ACTION_PROMPT={trigger}",
            )
        )
        flags.extend(local_flags)
        if target_source == "POST_FALLBACK":
            flags.append("POST_FALLBACK_ORDER_UNRESOLVED")
        if template == "TERMINAL_ACTION":
            flags.append("TERMINAL_MNEMONIC_CLOSURE_CONFOUND")
    elif template == "SELECTION_REFERENCE":
        if anchor["kind"] == "FORMAL":
            argument = re.search(r"\((ARG_[A-Z]+)\)", trigger)
            assert argument
            pieces.extend((f"REFERENCE={argument.group(1)}[OPAQUE_FORMAL_ARGUMENT]", f"MARK_PROMPT={trigger}"))
            flags.append("FORMAL_ARGUMENT_NOT_MAPPED_TO_REGISTER")
        elif trigger == "VORIGES?":
            previous, source, local_flags = choose_register(pre, post, "PREVIOUS")
            pieces.extend((f"PREVIOUS={previous}[{source}]", f"REFERENCE_PROMPT={trigger}"))
            flags.extend(local_flags)
            flags.append("ANTECEDENT_REMAINS_ANONYMOUS")
        else:
            active, source, local_flags = choose_register(pre, post, "ACTIVE", prefer_post=True)
            pieces.extend((f"ACTIVE={active}[{source}]", f"SELECTION_PROMPT={trigger}"))
            flags.extend(local_flags)
            flags.append("SELECTED_REFERENT_REMAINS_ANONYMOUS")
    else:
        raise AssertionError(template)

    return ";".join(pieces), sorted(set(flags))


def template_inventory_rows() -> list[dict[str, str]]:
    return [
        {
            "template_id": "PARAMETER_ASSIGNMENT",
            "licensed_exact_anchors": "MASS?",
            "licensed_formal_anchors": "SET(ARG_AIIN)",
            "required_register_slots": "ACTIVE",
            "optional_register_slots": "OWNER",
            "ephemeral_slots": "PARAMETER_PROMPT;VALUE_UNRESOLVED",
            "executable_operator": "SET PARAMETER_PROMPT FOR ACTIVE; retain value as unresolved",
            "register_update_rule": "no persistent parameter register; use the selected V62 statement transition unchanged",
            "failure_rule": "without exact/formal anchor: EXEMPLAR_ONLY; without ACTIVE: unresolved slot, never invent an object",
            "strongest_contradiction": "MASS? supplies no number or unit; SET(ARG_AIIN) may be a purely graphic standard slot",
            "apprentice_rule": "copy the prompt, leave its value blank, and never turn a local dose into the card meaning",
        },
        {
            "template_id": "TARGET_ASSIGNMENT",
            "licensed_exact_anchors": "ZIEL?",
            "licensed_formal_anchors": "SET(ARG_AL)",
            "required_register_slots": "ACTIVE;TARGET",
            "optional_register_slots": "OWNER",
            "ephemeral_slots": "TARGET_PROMPT",
            "executable_operator": "BIND TARGET slot for ACTIVE to anonymous TARGET",
            "register_update_rule": "take TARGET from the V62 transition result; preserve overwrite history",
            "failure_rule": "if TARGET remains UNSET, keep the assignment unresolved rather than naming a destination",
            "strongest_contradiction": "two licensed assignments end with TARGET still UNSET; target identity is exemplar-derived",
            "apprentice_rule": "write only the target-slot mark and its anonymous ID; the pictured destination stays outside the card",
        },
        {
            "template_id": "RELATION_LINK",
            "licensed_exact_anchors": "NONE",
            "licensed_formal_anchors": "FRAME_O(LINK)",
            "required_register_slots": "ACTIVE;PREVIOUS_OR_TARGET",
            "optional_register_slots": "OWNER",
            "ephemeral_slots": "LINK_PROMPT",
            "executable_operator": "LINK ACTIVE to PREVIOUS, otherwise to TARGET",
            "register_update_rule": "do not alter registers; use only a pre-state endpoint unless event order is independently known",
            "failure_rule": "if no pre-state endpoint exists, emit UNRESOLVED rather than borrowing one from local prose",
            "strongest_contradiction": "ten of nineteen anchors lack a pre-state PREVIOUS and TARGET endpoint",
            "apprentice_rule": "draw the link only after writing both anonymous endpoints in the margin",
        },
        {
            "template_id": "STATE_CHECK_GATE",
            "licensed_exact_anchors": "BEREIT?;KLAR?",
            "licensed_formal_anchors": "NONE",
            "required_register_slots": "ACTIVE",
            "optional_register_slots": "OWNER;TARGET",
            "ephemeral_slots": "STATE_PROMPT;RESULT_UNRESOLVED",
            "executable_operator": "CHECK STATE_PROMPT on ACTIVE; HOLD if result is not supplied",
            "register_update_rule": "state check itself changes no persistent register",
            "failure_rule": "a local result or threshold remains exemplar-only",
            "strongest_contradiction": "the cards do not show whether the gate passed, nor which observable threshold was used",
            "apprentice_rule": "ask the one-word state question; never copy the explanatory condition into the card",
        },
        {
            "template_id": "ACTION",
            "licensed_exact_anchors": "ANWENDEN?;TEMPERIEREN?",
            "licensed_formal_anchors": "NONE",
            "required_register_slots": "ACTIVE",
            "optional_register_slots": "OWNER;TARGET",
            "ephemeral_slots": "ACTION_PROMPT",
            "executable_operator": "DO ACTION_PROMPT on ACTIVE, optionally at TARGET",
            "register_update_rule": "retain the selected V62 transition; the action prompt alone creates no object or target",
            "failure_rule": "missing target is optional; missing ACTIVE remains unresolved",
            "strongest_contradiction": "ANWENDEN? and TEMPERIEREN? can still be generic process labels or copy cues",
            "apprentice_rule": "name the operation prompt, point only to anonymous registers, and keep tools/materials in the exemplar",
        },
        {
            "template_id": "TERMINAL_ACTION",
            "licensed_exact_anchors": "SPÜLEN?;ABLASSEN?",
            "licensed_formal_anchors": "NONE",
            "required_register_slots": "ACTIVE",
            "optional_register_slots": "OWNER;TARGET",
            "ephemeral_slots": "ACTION_PROMPT",
            "executable_operator": "DO terminal ACTION_PROMPT on ACTIVE; do not pronounce layout closure",
            "register_update_rule": "retain the V62 transition; terminal class does not itself close a clause",
            "failure_rule": "without the exact mnemonic there is no terminal action, even at a closed field",
            "strongest_contradiction": "all sixteen occurrences are confounded with two formal closure families; anonymous END_A/END_B remains viable",
            "apprentice_rule": "separate the one-word action card from the silent field-ending operation",
        },
        {
            "template_id": "SELECTION_REFERENCE",
            "licensed_exact_anchors": "ANSATZ?;VORIGES?;ANTEIL?",
            "licensed_formal_anchors": "MARK(ARG_AIIN);MARK(ARG_AL);MARK(ARG_AR)",
            "required_register_slots": "ACTIVE_OR_PREVIOUS_OR_OPAQUE_FORMAL_ARGUMENT",
            "optional_register_slots": "OWNER;TARGET",
            "ephemeral_slots": "SELECTION_OR_REFERENCE_PROMPT",
            "executable_operator": "SELECT ACTIVE/ANTEIL, REFER TO PREVIOUS, or MARK opaque formal argument",
            "register_update_rule": "use V62 ACTIVE/PREVIOUS transitions; MARK does not choose a register by itself",
            "failure_rule": "if antecedent or selected item is unresolved, retain the prompt and flag the missing reference",
            "strongest_contradiction": "MARK has three opaque arguments and VORIGES? has only two occurrences; one reference class is not established",
            "apprentice_rule": "write the anonymous pointer before reading the local exemplar noun",
        },
    ]


def strongest_unit_contradiction(
    anchors: list[tuple[dict[str, str], dict[str, str], str, list[str]]],
    residue_count: int,
    transition: dict[str, str],
) -> str:
    if not anchors:
        return "NO_LICENSED_EXACT_OR_FORMAL_ANCHOR"
    flags = {flag for _, _, _, local_flags in anchors for flag in local_flags}
    if "REQUIRED_RELATION_ENDPOINT_UNSET" in flags or any(flag.startswith("REQUIRED_") for flag in flags):
        return "REQUIRED_ANONYMOUS_SLOT_UNRESOLVED"
    if "TERMINAL_MNEMONIC_CLOSURE_CONFOUND" in flags:
        return "TERMINAL_ACTION_VS_FORMAL_CLOSURE_CONFOUND"
    if "FORMAL_ARGUMENT_NOT_MAPPED_TO_REGISTER" in flags:
        return "MARK_ARGUMENT_TO_REGISTER_MAPPING_UNRESOLVED"
    if residue_count:
        return "UNLICENSED_EVENT_RESIDUE_REQUIRES_EXEMPLAR"
    if transition["irreducible_ambiguity_codes"] != "NONE":
        return f"V62_REGISTER_WARNING:{transition['irreducible_ambiguity_codes']}"
    return "TEMPLATE_CLASS_ONLY;NO_SOURCE_WORD_ORDER_OR_REFERENT"


def execute_text(template: str, binding: str) -> str:
    values = {}
    for item in binding.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            values[key] = value
    active = values.get("ACTIVE", "UNRESOLVED")
    target = values.get("TARGET", "OPTIONAL_UNSET")
    if template == "PARAMETER_ASSIGNMENT":
        return f"SET PARAMETER_PROMPT={values['PARAMETER_PROMPT']} FOR {active}; VALUE=UNRESOLVED"
    if template == "TARGET_ASSIGNMENT":
        return f"BIND TARGET_SLOT OF {active} TO {target}; REFERENT=ANONYMOUS"
    if template == "RELATION_LINK":
        return f"LINK {active} TO {values['OTHER']}"
    if template == "STATE_CHECK_GATE":
        return f"CHECK {values['STATE_PROMPT']} ON {active}; IF RESULT UNKNOWN THEN HOLD"
    if template == "ACTION":
        return f"DO {values['ACTION_PROMPT']} ON {active}; TARGET={target}"
    if template == "TERMINAL_ACTION":
        return f"DO {values['ACTION_PROMPT']} ON {active}; TARGET={target}; KEEP CLOSURE SILENT"
    if template == "SELECTION_REFERENCE":
        if "REFERENCE" in values:
            return f"MARK {values['REFERENCE']}; REGISTER_BINDING=UNRESOLVED"
        if "PREVIOUS" in values:
            return f"REFER TO {values['PREVIOUS']}"
        return f"SELECT {values['ACTIVE']} BY {values['SELECTION_PROMPT']}"
    raise AssertionError(template)


def main() -> None:
    events = read_tsv(EVENT_PATH)
    statements = read_tsv(STATEMENT_PATH)
    transitions = read_tsv(TRANSITION_PATH)
    inventories = read_tsv(INVENTORY_PATH)

    assert len(events) == 381
    assert len(statements) == 116
    assert len(transitions) == 116
    assert len(inventories) == 4
    assert {row["page"] for row in events} == ALLOWED_PAGES
    assert {row["page"] for row in statements} == ALLOWED_PAGES

    event_by_serial = {int(row["event_serial"]): row for row in events}
    assert set(event_by_serial) == set(range(1, 382))
    transition_by_statement = {row["statement_id"]: row for row in transitions}
    assert len(transition_by_statement) == 116

    statement_by_event: dict[int, dict[str, str]] = {}
    field_to_statement: dict[str, dict[str, str]] = {}
    for statement in statements:
        for serial_text in split_pipe(statement["event_serials"]):
            serial = int(serial_text)
            assert serial not in statement_by_event
            statement_by_event[serial] = statement
        for field in split_pipe(statement["constituent_fields"]):
            assert field not in field_to_statement
            field_to_statement[field] = statement
    assert set(statement_by_event) == set(event_by_serial)
    assert len(field_to_statement) == 135

    anchors_by_statement: dict[str, list[tuple[dict[str, str], dict[str, str], str, list[str]]]] = defaultdict(list)
    anchors_by_field: dict[str, list[tuple[dict[str, str], dict[str, str], str, list[str]]]] = defaultdict(list)
    licensed_serials: set[int] = set()
    for event in events:
        anchor = anchor_for_event(event)
        if not anchor:
            continue
        serial = int(event["event_serial"])
        statement = statement_by_event[serial]
        transition = transition_by_statement[statement["statement_id"]]
        binding, flags = bind_anchor(event, anchor, transition)
        item = (event, anchor, binding, flags)
        anchors_by_statement[statement["statement_id"]].append(item)
        anchors_by_field[event["field_id"]].append(item)
        licensed_serials.add(serial)

    assert len(licensed_serials) == 126

    statement_rows: list[dict[str, object]] = []
    for statement in statements:
        statement_id = statement["statement_id"]
        transition = transition_by_statement[statement_id]
        serials = [int(value) for value in split_pipe(statement["event_serials"])]
        anchors = sorted(anchors_by_statement.get(statement_id, []), key=lambda item: int(item[0]["event_serial"]))
        anchor_serials = {int(item[0]["event_serial"]) for item in anchors}
        residue = [serial for serial in serials if serial not in anchor_serials]
        templates = [item[1]["template"] for item in anchors]
        flags = sorted({flag for item in anchors for flag in item[3]})
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "constituent_loci": statement["constituent_loci"],
                "constituent_fields": statement["constituent_fields"],
                "event_count": len(serials),
                "licensed_anchor_event_count": len(anchors),
                "unlicensed_exemplar_event_count": len(residue),
                "anchor_event_serials": "|".join(str(item[0]["event_serial"]) for item in anchors) or "NONE",
                "anchor_channel_sequence": " | ".join(
                    f"E{item[0]['event_serial']}:{item[1]['kind']}:{item[1]['trigger']}" for item in anchors
                ) or "NONE",
                "template_sequence": " | ".join(
                    f"E{item[0]['event_serial']}:{item[1]['template']}" for item in anchors
                ) or "EXEMPLAR_ONLY",
                "template_set": "|".join(template for template in TEMPLATE_ORDER if template in templates) or "EXEMPLAR_ONLY",
                "mapping_status": "TEMPLATE_ANCHORED_NO_TOTAL_PARSE" if anchors else "EXEMPLAR_ONLY",
                "all_events_channel_anchored": "YES_BUT_NOT_A_TOTAL_PARSE" if anchors and not residue else "NO",
                "pre_register_state": render_state(parse_state(transition["pre_state"])),
                "post_register_state": render_state(parse_state(transition["post_state"])),
                "slot_binding_sequence": " || ".join(
                    f"E{item[0]['event_serial']}:{item[2]}" for item in anchors
                ) or "NONE",
                "slot_or_order_warnings": "|".join(flags) or "NONE",
                "v62_transition_warning": transition["irreducible_ambiguity_codes"],
                "unlicensed_exemplar_event_serials": "|".join(map(str, residue)) or "NONE",
                "selected_short_card_skeleton": statement["selected_short_card_skeleton"],
                "local_clause_status": "V61_EXEMPLAR_ONLY;NOT_USED_TO_LICENSE_TEMPLATE_OR_FILL_CARD_VALUE",
                "strongest_contradiction": strongest_unit_contradiction(anchors, len(residue), transition),
                "source_lineage": "V60_SELECTED_381>V61_SELECTED_116>V62_SELECTED_TRANSITIONS>V63_R1",
            }
        )

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)
    field_rows: list[dict[str, object]] = []
    for field_id in sorted(events_by_field, key=lambda value: int(value[1:])):
        field_events = sorted(events_by_field[field_id], key=lambda row: int(row["event_serial"]))
        statement = field_to_statement[field_id]
        transition = transition_by_statement[statement["statement_id"]]
        anchors = sorted(anchors_by_field.get(field_id, []), key=lambda item: int(item[0]["event_serial"]))
        anchor_serials = {int(item[0]["event_serial"]) for item in anchors}
        residue = [int(event["event_serial"]) for event in field_events if int(event["event_serial"]) not in anchor_serials]
        templates = [item[1]["template"] for item in anchors]
        flags = sorted({flag for item in anchors for flag in item[3]})
        loci = []
        for event in field_events:
            if event["locus"] not in loci:
                loci.append(event["locus"])
        field_rows.append(
            {
                "field_id": field_id,
                "statement_id": statement["statement_id"],
                "record_unit_id": field_events[0]["record_unit_id"],
                "page": field_events[0]["page"],
                "locus": "|".join(loci),
                "event_count": len(field_events),
                "licensed_anchor_event_count": len(anchors),
                "unlicensed_exemplar_event_count": len(residue),
                "anchor_event_serials": "|".join(str(item[0]["event_serial"]) for item in anchors) or "NONE",
                "anchor_channel_sequence": " | ".join(
                    f"E{item[0]['event_serial']}:{item[1]['kind']}:{item[1]['trigger']}" for item in anchors
                ) or "NONE",
                "template_sequence": " | ".join(
                    f"E{item[0]['event_serial']}:{item[1]['template']}" for item in anchors
                ) or "EXEMPLAR_ONLY",
                "template_set": "|".join(template for template in TEMPLATE_ORDER if template in templates) or "EXEMPLAR_ONLY",
                "mapping_status": "TEMPLATE_ANCHORED_NO_TOTAL_PARSE" if anchors else "EXEMPLAR_ONLY",
                "all_events_channel_anchored": "YES_BUT_NOT_A_TOTAL_PARSE" if anchors and not residue else "NO",
                "register_scope": "V62_STATEMENT_PRE_TO_POST_ONLY;NO_WITHIN_STATEMENT_EVENT_ORDER",
                "pre_register_state": render_state(parse_state(transition["pre_state"])),
                "post_register_state": render_state(parse_state(transition["post_state"])),
                "slot_binding_sequence": " || ".join(
                    f"E{item[0]['event_serial']}:{item[2]}" for item in anchors
                ) or "NONE",
                "slot_or_order_warnings": "|".join(flags) or "NONE",
                "unlicensed_exemplar_event_serials": "|".join(map(str, residue)) or "NONE",
                "local_field_status": "EXEMPLAR_ONLY_BEYOND_LISTED_ANCHORS",
                "strongest_contradiction": strongest_unit_contradiction(anchors, len(residue), transition),
                "source_lineage": "V60_SELECTED_381>V61_SELECTED_116>V62_SELECTED_TRANSITIONS>V63_R1",
            }
        )

    inventory_rows = template_inventory_rows()

    channel_rows: list[dict[str, object]] = []
    for mnemonic, template in EXACT_TO_TEMPLATE.items():
        matching = [event for event in events if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == mnemonic]
        statement_ids = {statement_by_event[int(event["event_serial"])]["statement_id"] for event in matching}
        channel_rows.append(
            {
                "channel_id": f"EXACT:{mnemonic}",
                "channel_kind": "EXACT_CARD_MNEMONIC",
                "frozen_trigger": mnemonic,
                "template_id": template,
                "event_occurrence_count": len(matching),
                "statement_scope_count": len(statement_ids),
                "field_scope_count": len({event["field_id"] for event in matching}),
                "anchor_permission": "YES",
                "slot_permission": "PROMPT_ONLY;NO_VISIBLE_FORM_OR_COMPONENT_INHERITANCE",
                "strongest_limit": "working mnemonic, not a proven lexeme or phrase",
            }
        )
    formal_groups = [
        ("SET(ARG_AIIN)", {"SET(<ARG_AIIN>)"}, "PARAMETER_ASSIGNMENT"),
        ("SET(ARG_AL)", {"SET(<ARG_AL>)"}, "TARGET_ASSIGNMENT"),
        ("FRAME_O(LINK)", {"FRAME_O(LINK)"}, "RELATION_LINK"),
        ("MARK", {"MARK(<ARG_AIIN>)", "MARK(<ARG_AL>)", "MARK(<ARG_AR>)"}, "SELECTION_REFERENCE"),
    ]
    for label, formulas, template in formal_groups:
        matching = [event for event in events if event["formal_formula_opaque"] in formulas]
        statement_ids = {statement_by_event[int(event["event_serial"])]["statement_id"] for event in matching}
        channel_rows.append(
            {
                "channel_id": f"FORMAL:{label}",
                "channel_kind": "FORMAL_OPERATION",
                "frozen_trigger": label,
                "template_id": template,
                "event_occurrence_count": len(matching),
                "statement_scope_count": len(statement_ids),
                "field_scope_count": len({event["field_id"] for event in matching}),
                "anchor_permission": "YES",
                "slot_permission": "FORMAL_OPERATOR_ONLY;ARGUMENT_REMAINS_OPAQUE",
                "strongest_limit": "formal placement/control is not a source-language word",
            }
        )
    inventory_lookup = {row["register"]: row for row in inventories}
    register_rows = [
        ("OWNER", "OWNER", "all templates as record context"),
        ("ACTIVE", "ACTIVE_ITEM/PREPARATION", "parameter;relation;state;action;terminal;selection"),
        ("TARGET", "TARGET/STATION", "target;relation;action;terminal"),
        ("PREVIOUS", "PREVIOUS_ITEM", "relation;selection"),
    ]
    for short, source, uses in register_rows:
        row = inventory_lookup[source]
        channel_rows.append(
            {
                "channel_id": f"REGISTER:{short}",
                "channel_kind": "ANONYMOUS_REGISTER",
                "frozen_trigger": short,
                "template_id": "SLOT_FILLER_ONLY",
                "event_occurrence_count": 0,
                "statement_scope_count": 116,
                "field_scope_count": 135,
                "anchor_permission": "NO",
                "slot_permission": uses,
                "strongest_limit": f"{row['semantic_status']}; operations {row['operation_counts']}",
            }
        )

    example_specs = [
        ("EX01", 22, "exact MASS?"),
        ("EX02", 247, "exact ANWENDEN?"),
        ("EX03", 16, "exact BEREIT?"),
        ("EX04", 17, "exact ANSATZ?"),
        ("EX05", 214, "exact ZIEL?"),
        ("EX06", 203, "exact KLAR?"),
        ("EX07", 113, "exact VORIGES?"),
        ("EX08", 98, "exact ANTEIL?"),
        ("EX09", 205, "exact TEMPERIEREN?"),
        ("EX10", 101, "exact SPÜLEN?"),
        ("EX11", 235, "exact ABLASSEN?"),
        ("EX12", 56, "formal SET(ARG_AIIN)"),
        ("EX13", 172, "formal SET(ARG_AL)"),
        ("EX14", 124, "formal FRAME_O(LINK)"),
        ("EX15", 230, "formal MARK"),
    ]
    example_rows: list[dict[str, object]] = []
    for example_id, serial, purpose in example_specs:
        event = event_by_serial[serial]
        statement = statement_by_event[serial]
        transition = transition_by_statement[statement["statement_id"]]
        anchor = anchor_for_event(event)
        assert anchor
        binding, flags = bind_anchor(event, anchor, transition)
        example_rows.append(
            {
                "example_id": example_id,
                "purpose": purpose,
                "template_id": anchor["template"],
                "statement_id": statement["statement_id"],
                "field_id": event["field_id"],
                "page": event["page"],
                "locus": event["locus"],
                "anchor_event_serial": serial,
                "anchor_channel": f"{anchor['kind']}:{anchor['trigger']}",
                "pre_register_state": render_state(parse_state(transition["pre_state"])),
                "step_1_bind_slots": binding,
                "step_2_execute_template": execute_text(anchor["template"], binding),
                "step_3_apply_register_transition": (
                    f"OWNER:{transition['owner_operation']};ACTIVE:{transition['active_item_preparation_operation']};"
                    f"TARGET:{transition['target_station_operation']};PREVIOUS:{transition['previous_item_operation']}"
                ),
                "post_register_state": render_state(parse_state(transition["post_state"])),
                "local_exemplar_expansion": statement["concrete_workshop_reading"],
                "separation_rule": "steps 1-3 are anonymous/template-level; local expansion is an exemplar and cannot refill the card",
                "warnings": "|".join(flags) or "NONE",
                "strongest_contradiction": strongest_unit_contradiction(
                    [(event, anchor, binding, flags)],
                    int(statement["event_count"]) - 1,
                    transition,
                ),
            }
        )

    template_counts = Counter(item[1]["template"] for items in anchors_by_statement.values() for item in items)
    template_statement_counts = {
        template: sum(template in {item[1]["template"] for item in anchors_by_statement.get(row["statement_id"], [])} for row in statements)
        for template in TEMPLATE_ORDER
    }
    template_field_counts = {
        template: sum(template in {item[1]["template"] for item in anchors_by_field.get(field, [])} for field in events_by_field)
        for template in TEMPLATE_ORDER
    }
    covered_statements = sum(row["mapping_status"] != "EXEMPLAR_ONLY" for row in statement_rows)
    covered_fields = sum(row["mapping_status"] != "EXEMPLAR_ONLY" for row in field_rows)
    all_statement_events_anchored = sum(row["all_events_channel_anchored"] != "NO" for row in statement_rows)
    all_field_events_anchored = sum(row["all_events_channel_anchored"] != "NO" for row in field_rows)
    exact_anchor_count = sum(anchor_for_event(event) is not None and anchor_for_event(event)["kind"] == "EXACT" for event in events)
    formal_anchor_count = sum(anchor_for_event(event) is not None and anchor_for_event(event)["kind"] == "FORMAL" for event in events)

    record_rows = []
    record_order = sorted({row["record_unit_id"] for row in events}, key=lambda value: (value[0], int(value[1:])))
    for record in record_order:
        record_statement_rows = [row for row in statement_rows if row["record_unit_id"] == record]
        record_field_rows = [row for row in field_rows if row["record_unit_id"] == record]
        record_rows.append(
            (
                record,
                f"{sum(row['mapping_status'] != 'EXEMPLAR_ONLY' for row in record_statement_rows)}/{len(record_statement_rows)}",
                f"{sum(row['mapping_status'] != 'EXEMPLAR_ONLY' for row in record_field_rows)}/{len(record_field_rows)}",
            )
        )

    template_table = "\n".join(
        f"| `{template}` | {template_counts[template]} | {template_statement_counts[template]} | {template_field_counts[template]} |"
        for template in TEMPLATE_ORDER
    )
    record_table = "\n".join(f"| {record} | {statement_count} | {field_count} |" for record, statement_count, field_count in record_rows)

    report = f"""# V63 R1 — lehrbare Slotgrammatik ohne Totalparse

Status: kreative Werkstattedition; keine wissenschaftliche Entzifferung, kein Lexemnachweis.

## Entscheidung

Eine kleine Grammatik ist **als Anker- und Registerverfahren lehrbar**, aber nicht als vollständige Sprache. Sie besteht aus genau sieben Templates. Ein Template darf nur durch ein ausgewähltes exaktes Merkwort oder einen ausdrücklich freigegebenen Formaloperator beginnen. OWNER, ACTIVE, TARGET und PREVIOUS füllen danach ausschließlich anonyme Slots; ein Registerzustand darf niemals selbst ein Template erzeugen.

Von 381 Ereignissen tragen 126 einen V63-Anker: {exact_anchor_count} exakte Merkwortvorkommen und {formal_anchor_count} Formaloperatoren. Damit werden {covered_statements}/116 Aussagen und {covered_fields}/135 Felder wenigstens einmal verankert; 52 Aussagen und 61 Felder bleiben vollständig `EXEMPLAR_ONLY`. 255 Ereignisse bleiben unlizenzierter Exemplarrest. Selbst die {all_statement_events_anchored} Aussagen und {all_field_events_anchored} Felder, deren sämtliche Ereignisse Anker sind, gelten ausdrücklich **nicht** als Totalparse: Referenten, Werte, Wortfolge und lokale Prosa bleiben außerhalb der Grammatik.

## Gefrorenes Inventar

| Template | Instanzen | Aussagen | Felder |
|---|---:|---:|---:|
{template_table}

Die vollständigen Operator-, Slot-, Fehler- und Lehrregeln stehen in `V63_R1_TEMPLATE_INVENTORY.tsv`. Die Zuordnung ist absichtlich eng:

- `MASS?` und `SET(ARG_AIIN)` → Parameterzuweisung.
- `ZIEL?` und `SET(ARG_AL)` → Zielzuweisung.
- `FRAME_O(LINK)` → Relationsverknüpfung.
- `BEREIT?`, `KLAR?` → Zustandsprüfung/Sperre.
- `ANWENDEN?`, `TEMPERIEREN?` → Handlung.
- `SPÜLEN?`, `ABLASSEN?` → terminale Handlung.
- `ANSATZ?`, `VORIGES?`, `ANTEIL?` und `MARK` → Auswahl/Verweis.

Andere SET-, LINK-, FRAME- oder Schlussformen, der bloße sichtbare Kartenkörper und der strikte Prompt `VORGABEPARAMETER?` sind in V63 keine selbständigen Anker. Insbesondere wird die Oberfläche `daiin` nicht wie die exakte Karte `MASS?` behandelt. `MARK` bleibt formales Markieren eines opaken Arguments; seine Einordnung unter Auswahl/Verweis benennt weder Referent noch Wortart.

## Ausführbare Schreib- und Leseregel

1. V61-`statement_id` statt physischer Zeile aufschlagen; eine Zeile beendet keine Aussage automatisch.
2. Ereignisse in veröffentlichter Reihenfolge lesen und ausschließlich in der exakten V60-Spalte oder in der engen Formal-Allowlist nach einem Anker suchen.
3. Ohne Anker `EXEMPLAR_ONLY` schreiben und stoppen. Register dürfen diesen Stopp nicht umgehen.
4. Bei einem Anker das zugehörige der sieben Templates öffnen. Mehrere Anker bleiben als geordnete Folge erhalten; sie werden nicht zu einem neuen Satzwert verschmolzen.
5. OWNER/ACTIVE/TARGET/PREVIOUS aus dem V62-Vorzustand einsetzen. Ein Nachzustand darf nur als markierter `POST_FALLBACK` dienen, weil V62 keine Ereignisordnung innerhalb einer Aussage beweist.
6. Fehlende Pflichtrolle als `UNRESOLVED` notieren. Ein Pflanzen-, Stoff-, Körper-, Gefäß- oder Stationswort darf nur aus dem lokalen Exemplar kommen und bleibt dort.
7. Den V62-Übergang unverändert ausführen und ins Verlaufsbuch schreiben. Kein Kartenanker erhält dadurch eine stille Objektbedeutung.
8. Formale Feldschließung lautlos ausführen. Sie ist weder Satzzeichen noch Bedeutung von `SPÜLEN?`/`ABLASSEN?`.

## Drei vollständige Rücklesetests

### H2-S001 / F003

Die Ankerfolge enthält `BEREIT? → ANSATZ? → MASS?`. Aus dem anfangs leeren Recordzustand liefert der veröffentlichte V62-Übergang OWNER=H2:O01 und ACTIVE=H2:I001. Der Lehrling schreibt daher abstrakt: `CHECK BEREIT? ON H2:I001; SELECT H2:I001 BY ANSATZ?; SET MASS? FOR H2:I001; VALUE=UNRESOLVED`. Erst danach darf er die V61-Werkstattklausel als lokale Exemplarlesung danebenstellen. Widerspruch: Die Ereignisreihenfolge der Registereinführung innerhalb der Aussage ist nicht beobachtet; ACTIVE ist hier ausdrücklich ein `POST_FALLBACK`.

### B1-S004 / F026

Vor der Aussage stehen ACTIVE=B1:I002 und PREVIOUS=B1:I001. Der formale Anker `FRAME_O(LINK)` erlaubt genau `LINK B1:I002 TO B1:I001`; er erlaubt weder die Benennung beider Posten noch eine konkrete räumliche oder medizinische Relation. Der V62-Zustand bleibt unverändert. Widerspruch: PREVIOUS hat mehrere plausible lokale Referentenklassen; die anonyme Kante ist ausführbar, die Sachrelation nicht bestimmt.

### B3-S003 / F073

Vor dem Feld stehen OWNER=B3:O01, ACTIVE=B3:I001 und TARGET=B3:T001. Der exakte Anker `ABLASSEN?` erlaubt `DO ABLASSEN? ON B3:I001; TARGET=B3:T001`; die formale Schließung wird getrennt und lautlos ausgeführt. Widerspruch: Alle acht `ABLASSEN?`- und alle acht `SPÜLEN?`-Vorkommen fallen mit zwei Schlussfamilien zusammen. `END_A/END_B` bleibt daher ein gleichwertiger technischer Rivale.

`V63_R1_EXECUTABLE_EXAMPLES.tsv` führt für alle elf exakten und alle vier formalen Ankerklassen je ein vollständiges Bindungs-, Ausführungs- und Updatebeispiel mit strikt abgetrennter lokaler Exemplarlesung.

## Abdeckung nach Record

| Record | verankerte Aussagen | verankerte Felder |
|---|---:|---:|
{record_table}

Die 116- und 135-Zeilen-Karten veröffentlichen jeden Nullfall als `EXEMPLAR_ONLY`; es gibt keine erzwungene Restkategorie und keine semantische Ableitung aus sichtbaren Komponenten.

## Stärkste Widersprüche

1. **Abdeckung:** Mehr als die Hälfte der Ereignisse und 52/116 Aussagen besitzen keinen lizenzierten Anker. Die Grammatik ist ein Skelett, keine vollständige Quellsyntax.
2. **Registerzirkularität:** Viele V62-IDs wurden in der kreativen Edition mithilfe lokaler Exemplare eingeführt. Darum dürfen sie Slots füllen, aber nie ein Template oder einen Kartenwert begründen.
3. **Relationslücke:** Zehn von 19 `FRAME_O(LINK)`-Ankern haben im Aussage-Vorzustand weder PREVIOUS noch TARGET als zweiten Endpunkt. Ein späterer Nachzustand beweist die Ereignisordnung nicht.
4. **Ziellücke:** Zwei von 16 Zielzuweisungsankern enden mit TARGET=UNSET; alle anderen Ziele bleiben anonyme, teils überschriebene IDs.
5. **Terminalkonfundierung:** Die 16 terminalen Merkwörter sind vollständig mit Schlussformen konfundiert. Eine reine Renderer-/Formularlesung bleibt stark.
6. **Quelltextlücke:** Kein Template liefert Zahl, Einheit, Instrument, Material, Körperteil, Station oder Ergebnis. Diese Angaben stammen weiterhin nur aus den gekennzeichneten lokalen Exemplaren.

## Typische Lehrlingsfehler und Reparaturen

- **Fehler:** gleich aussehende Oberflächen oder Teilformen übernehmen den Merkwert. **Reparatur:** nur die exakte Joint-Tuple-Zeile im ausgewählten Ledger nachschlagen.
- **Fehler:** ein getragenes ACTIVE erzeugt automatisch eine Handlung. **Reparatur:** ohne exakten/formalen Anker `EXEMPLAR_ONLY`.
- **Fehler:** H2:I001 als Pflanze, Flüssigkeit oder Person aussprechen. **Reparatur:** ID anonym zurücklesen; Sachwort nur in der getrennten Exemplarspalte.
- **Fehler:** `MASS?` mit einer lokal geratenen Menge füllen. **Reparatur:** `VALUE=UNRESOLVED` belassen.
- **Fehler:** `MARK` als Zustand oder bestimmtes Pronomen lesen. **Reparatur:** nur das opake Formalargument markieren.
- **Fehler:** `SPÜLEN?` oder `ABLASSEN?` aus jedem Feldschluss ableiten. **Reparatur:** terminales Template nur bei der exakten Karte; Schlussoperation separat.
- **Fehler:** den restlichen deutschen Satz aus einem Anker generieren. **Reparatur:** unlizenzierte Ereignisse und lokale Ergänzungen sichtbar als Exemplarrest führen.

## Schluss

V63 verbessert V62 als **unterrichtbares Kontrollskelett**: sieben Templates, ein enger Triggercheck, vier anonyme Merkregister und ein verpflichtender `UNRESOLVED`-Ausgang. Es verbessert V59 nicht zu einer Übersetzung. Der stärkste Gesamtrivale bleibt ein illustriertes Formular-/Musterbuch, in dem SET/LINK/MARK und die beiden Schlussfamilien Produktionszeichen sind und die deutschen Prozesssätze nur moderne Exemplare.

Validierung: siehe `V63_R1_VALIDATION.json`; die reproduzierbare Erzeugung steht in `V63_R1_BUILD_SLOT_GRAMMAR.py`, der unabhängige Prüfer in `V63_R1_VALIDATE_SLOT_GRAMMAR.py`.
"""

    write_tsv(
        OUT / "V63_R1_TEMPLATE_INVENTORY.tsv",
        inventory_rows,
        list(inventory_rows[0]),
    )
    write_tsv(
        OUT / "V63_R1_LICENSED_CHANNELS.tsv",
        channel_rows,
        list(channel_rows[0]),
    )
    write_tsv(
        OUT / "V63_R1_116_STATEMENT_TEMPLATE_MAP.tsv",
        statement_rows,
        list(statement_rows[0]),
    )
    write_tsv(
        OUT / "V63_R1_135_FIELD_TEMPLATE_MAP.tsv",
        field_rows,
        list(field_rows[0]),
    )
    write_tsv(
        OUT / "V63_R1_EXECUTABLE_EXAMPLES.tsv",
        example_rows,
        list(example_rows[0]),
    )
    (OUT / "V63_R1_SLOT_GRAMMAR_REPORT.md").write_text(report, encoding="utf-8")

    build_summary = {
        "status": "BUILT_PENDING_INDEPENDENT_VALIDATION",
        "templates": len(inventory_rows),
        "licensed_channels": len(channel_rows),
        "events": len(events),
        "licensed_anchor_events": len(licensed_serials),
        "unlicensed_exemplar_events": len(events) - len(licensed_serials),
        "statements": len(statement_rows),
        "template_anchored_statements": covered_statements,
        "exemplar_only_statements": len(statement_rows) - covered_statements,
        "fields": len(field_rows),
        "template_anchored_fields": covered_fields,
        "exemplar_only_fields": len(field_rows) - covered_fields,
        "examples": len(example_rows),
        "template_instance_counts": dict(template_counts),
    }
    (OUT / "V63_R1_BUILD_SUMMARY.json").write_text(
        json.dumps(build_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
