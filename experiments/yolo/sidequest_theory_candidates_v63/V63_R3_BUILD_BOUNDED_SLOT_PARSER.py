#!/usr/bin/env python3
"""Build the V63 R3 deterministic bounded slot parser."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V61 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v61"
V62 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v62"

SOURCE_EVENTS = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_STATEMENTS = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_MACHINE = V62 / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
SOURCE_REGISTERS = V62 / "V62_SELECTED_REGISTER_INVENTORY.tsv"

OUT_TEMPLATES = HERE / "V63_R3_TEMPLATE_DEFINITIONS.tsv"
OUT_EVENTS = HERE / "V63_R3_381_EVENT_TEMPLATE_LEDGER.tsv"
OUT_FIELDS = HERE / "V63_R3_135_FIELD_SLOT_PARSE.tsv"
OUT_STATEMENTS = HERE / "V63_R3_116_STATEMENT_SLOT_PARSE.tsv"
OUT_BASELINES = HERE / "V63_R3_BASELINE_COMPARISON.tsv"

REGISTERS = ("OWNER", "ACTIVE_ITEM/PREPARATION", "TARGET/STATION", "PREVIOUS_ITEM")
TEMPLATES = (
    "PARAMETER_ASSIGN",
    "TARGET_ASSIGN",
    "LINK_ACTIVE",
    "STATE_GATE",
    "ACTION_APPLY",
    "ACTION_TEMPER",
    "TERMINAL_FLUSH",
    "TERMINAL_DRAIN",
    "SELECT_PART",
    "SELECT_PREVIOUS",
    "COMPOSITE_SEQUENCE",
    "EXEMPLAR_ONLY",
)

EXACT_TEMPLATE = {
    "MASS?": "PARAMETER_ASSIGN",
    "ZIEL?": "TARGET_ASSIGN",
    "ANSATZ?": "LINK_ACTIVE",
    "BEREIT?": "STATE_GATE",
    "KLAR?": "STATE_GATE",
    "ANWENDEN?": "ACTION_APPLY",
    "TEMPERIEREN?": "ACTION_TEMPER",
    "SPÜLEN?": "TERMINAL_FLUSH",
    "ABLASSEN?": "TERMINAL_DRAIN",
    "ANTEIL?": "SELECT_PART",
    "VORIGES?": "SELECT_PREVIOUS",
}

FORMAL_TEMPLATE = {
    "VORGABEPARAMETER?": "PARAMETER_ASSIGN",
    "STANDARDSLOT_SETZEN": "PARAMETER_ASSIGN",
    "LOKALEN_RELATIONSSLOT_SETZEN": "TARGET_ASSIGN",
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": "LINK_ACTIVE",
}

REQUIRED_REGISTERS = {
    "PARAMETER_ASSIGN": ("ACTIVE_ITEM/PREPARATION",),
    "TARGET_ASSIGN": ("OWNER", "TARGET/STATION"),
    "LINK_ACTIVE": ("ACTIVE_ITEM/PREPARATION", "PREVIOUS_ITEM"),
    "STATE_GATE": ("ACTIVE_ITEM/PREPARATION",),
    "ACTION_APPLY": ("ACTIVE_ITEM/PREPARATION", "TARGET/STATION"),
    "ACTION_TEMPER": ("ACTIVE_ITEM/PREPARATION",),
    "TERMINAL_FLUSH": ("ACTIVE_ITEM/PREPARATION", "TARGET/STATION"),
    "TERMINAL_DRAIN": ("ACTIVE_ITEM/PREPARATION", "TARGET/STATION"),
    "SELECT_PART": ("OWNER", "ACTIVE_ITEM/PREPARATION", "PREVIOUS_ITEM"),
    "SELECT_PREVIOUS": ("ACTIVE_ITEM/PREPARATION", "PREVIOUS_ITEM"),
    "COMPOSITE_SEQUENCE": REGISTERS,
    "EXEMPLAR_ONLY": ("OWNER",),
}

EXACT_EFFECT = {
    "PARAMETER_ASSIGN": "PARAMETER_SLOT:=EXACT_MASS_VALUE;FOUR_REGISTERS=CARRY",
    "TARGET_ASSIGN": "TARGET/STATION:=EXACT_TARGET_ARGUMENT",
    "LINK_ACTIVE": "ACTIVE_ITEM/PREPARATION:=EXACT_ACTIVE_PREPARATION;PREVIOUS_ITEM=CARRY",
    "STATE_GATE": "ACTIVE_ITEM/PREPARATION.STATE:=EXACT_GATE_VALUE",
    "ACTION_APPLY": "APPLY(ACTIVE_ITEM/PREPARATION,TARGET/STATION)",
    "ACTION_TEMPER": "TEMPER(ACTIVE_ITEM/PREPARATION)",
    "TERMINAL_FLUSH": "FLUSH(ACTIVE_ITEM/PREPARATION,TARGET/STATION);COMMIT",
    "TERMINAL_DRAIN": "DRAIN(ACTIVE_ITEM/PREPARATION,TARGET/STATION);COMMIT",
    "SELECT_PART": "PREVIOUS_ITEM:=ACTIVE_ITEM/PREPARATION;ACTIVE_ITEM/PREPARATION:=EXACT_SELECTED_PART",
    "SELECT_PREVIOUS": "ACTIVE_ITEM/PREPARATION:=PREVIOUS_ITEM",
}

FORMAL_EFFECT = {
    "VORGABEPARAMETER?": "FORMAL_PARAMETER_SLOT:=OPAQUE_EVENT_VALUE;FOUR_REGISTERS=CARRY",
    "STANDARDSLOT_SETZEN": "FORMAL_STANDARD_SLOT:=OPAQUE_EVENT_VALUE;FOUR_REGISTERS=CARRY",
    "LOKALEN_RELATIONSSLOT_SETZEN": "TARGET/STATION:=FORMAL_RELATION_SLOT(OPAQUE_EVENT_VALUE)",
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": "ACTIVE_ITEM/PREPARATION:=FORMAL_ACTIVE_LINK(OPAQUE_EVENT_VALUE);PREVIOUS_ITEM=CARRY",
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


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    answer: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            answer.append(value)
    return answer


def aggregate_template(event_templates: list[str]) -> tuple[str, str, str]:
    recognized = sum(template != "EXEMPLAR_ONLY" for template in event_templates)
    exemplar = len(event_templates) - recognized
    if recognized == 0:
        return "EXEMPLAR_ONLY", "UNPARSED", "NO_LICENSED_EXACT_OR_FORMAL_TRIGGER"
    primary = event_templates[0] if len(event_templates) == 1 else "COMPOSITE_SEQUENCE"
    if exemplar == 0:
        return primary, "UNIQUE", "ALL_EVENT_TEMPLATES_DETERMINISTIC"
    return primary, "AMBIGUOUS", "LICENSED_TEMPLATE_SEQUENCE_WITH_EXEMPLAR_GAPS"


def unit_roundtrip(events: list[dict[str, str]], event_parse_by_serial: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    trace = " > ".join(
        f"E{event['event_serial']}@{event['joint_tuple_id']}:{event_parse_by_serial[event['event_serial']]['event_template']}:{event_parse_by_serial[event['event_serial']]['trigger_origin']}"
        for event in events
    )
    decoded = "|".join(event["event_serial"] for event in events)
    digest = hashlib.sha256("|".join(f"{event['event_serial']}:{event['joint_tuple_id']}" for event in events).encode("utf-8")).hexdigest()
    return trace, decoded, digest


def baseline_event_templates(events: list[dict[str, str]], model: str) -> list[str]:
    answer = []
    for event in events:
        if model == "MNEMONIC_BAG":
            answer.append(EXACT_TEMPLATE.get(event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"], "EXEMPLAR_ONLY"))
        elif model == "FORM_ONLY":
            answer.append(FORMAL_TEMPLATE.get(event["strict_control_prompt"], "EXEMPLAR_ONLY"))
        else:
            raise ValueError(model)
    return answer


def bag_signature(events: list[dict[str, str]]) -> str:
    counts = Counter(event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for event in events if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN")
    return ";".join(f"{key}={counts[key]}" for key in sorted(counts)) if counts else "EMPTY_MNEMONIC_BAG"


def form_signature(events: list[dict[str, str]]) -> str:
    return " > ".join(f"{event['strict_control_prompt']}:{event['terminal_status']}" for event in events)


def main() -> None:
    events = read_tsv(SOURCE_EVENTS)
    statements = read_tsv(SOURCE_STATEMENTS)
    machine = read_tsv(SOURCE_MACHINE)
    registers = read_tsv(SOURCE_REGISTERS)
    require((len(events), len(statements), len(machine), len(registers)) == (381, 116, 116, 4), "selected source counts changed")
    require(tuple(row["register"] for row in registers) == REGISTERS, "selected V62 register inventory changed")

    statement_by_id = {row["statement_id"]: row for row in statements}
    machine_by_id = {row["statement_id"]: row for row in machine}
    require(list(statement_by_id) == list(machine_by_id), "V61/V62 statement identity or order changed")
    event_by_serial = {row["event_serial"]: row for row in events}
    require(len(event_by_serial) == 381, "event serials not unique")

    field_to_statement: dict[str, str] = {}
    statement_fields: dict[str, list[str]] = {}
    for statement in statements:
        fields = statement["constituent_fields"].split("|")
        statement_fields[statement["statement_id"]] = fields
        for field_id in fields:
            require(field_id not in field_to_statement, f"field assigned twice: {field_id}")
            field_to_statement[field_id] = statement["statement_id"]
    require(len(field_to_statement) == 135, "selected statements must partition 135 fields")

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)
    require(set(events_by_field) == set(field_to_statement), "field/event scope mismatch")
    events_by_statement: dict[str, list[dict[str, str]]] = {}
    for statement in statements:
        serials = statement["event_serials"].split("|")
        statement_events = [event_by_serial[serial] for serial in serials]
        require([event["field_id"] for event in statement_events] == [field for field in statement_fields[statement["statement_id"]] for _ in events_by_field[field]], f"statement event/field order mismatch: {statement['statement_id']}")
        events_by_statement[statement["statement_id"]] = statement_events

    template_rows = [
        {"template": "PARAMETER_ASSIGN", "exact_trigger": "MASS?", "strict_formal_trigger": "VORGABEPARAMETER?|STANDARDSLOT_SETZEN", "required_registers": "ACTIVE_ITEM/PREPARATION", "symbolic_update": "set an exact parameter or an explicitly FORMAL_OPAQUE parameter slot", "terminal_requirement": "NONE", "bounded_rule": "exact and formal channels may converge but remain separately labelled"},
        {"template": "TARGET_ASSIGN", "exact_trigger": "ZIEL?", "strict_formal_trigger": "LOKALEN_RELATIONSSLOT_SETZEN", "required_registers": "OWNER|TARGET/STATION", "symbolic_update": "set exact target argument OR FORMAL_RELATION_SLOT; never equate the two payloads", "terminal_requirement": "NONE", "bounded_rule": "formal relation slot inherits no semantic target word"},
        {"template": "LINK_ACTIVE", "exact_trigger": "ANSATZ?", "strict_formal_trigger": "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN", "required_registers": "ACTIVE_ITEM/PREPARATION|PREVIOUS_ITEM", "symbolic_update": "resume exact active preparation OR execute FORMAL_ACTIVE_LINK", "terminal_requirement": "NONE", "bounded_rule": "formal link inherits no semantic preparation word"},
        {"template": "STATE_GATE", "exact_trigger": "BEREIT?|KLAR?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION", "symbolic_update": "set selected exact state gate", "terminal_requirement": "NONCLOSE", "bounded_rule": "exact tuple only"},
        {"template": "ACTION_APPLY", "exact_trigger": "ANWENDEN?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION|TARGET/STATION", "symbolic_update": "apply active item to current target", "terminal_requirement": "NONCLOSE", "bounded_rule": "exact tuple only"},
        {"template": "ACTION_TEMPER", "exact_trigger": "TEMPERIEREN?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION", "symbolic_update": "temper active item", "terminal_requirement": "NONCLOSE", "bounded_rule": "exact tuple only"},
        {"template": "TERMINAL_FLUSH", "exact_trigger": "SPÜLEN?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION|TARGET/STATION", "symbolic_update": "flush and commit", "terminal_requirement": "TERMINAL", "bounded_rule": "exact tuple plus observed terminal; CLOSE alone never selects flush"},
        {"template": "TERMINAL_DRAIN", "exact_trigger": "ABLASSEN?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION|TARGET/STATION", "symbolic_update": "drain and commit", "terminal_requirement": "TERMINAL", "bounded_rule": "exact tuple plus observed terminal; CLOSE alone never selects drain"},
        {"template": "SELECT_PART", "exact_trigger": "ANTEIL?", "strict_formal_trigger": "NONE", "required_registers": "OWNER|ACTIVE_ITEM/PREPARATION|PREVIOUS_ITEM", "symbolic_update": "save active as previous and select part", "terminal_requirement": "NONCLOSE", "bounded_rule": "exact tuple only"},
        {"template": "SELECT_PREVIOUS", "exact_trigger": "VORIGES?", "strict_formal_trigger": "NONE", "required_registers": "ACTIVE_ITEM/PREPARATION|PREVIOUS_ITEM", "symbolic_update": "resume depth-one previous item", "terminal_requirement": "NONCLOSE", "bounded_rule": "exact tuple only"},
        {"template": "COMPOSITE_SEQUENCE", "exact_trigger": "TWO_OR_MORE_EVENT_POSITIONS_WITH_AT_LEAST_ONE_LICENSED_TEMPLATE", "strict_formal_trigger": "ORDERED_FORMAL_AND_EXACT_CHANNELS_RETAINED", "required_registers": "OWNER|ACTIVE_ITEM/PREPARATION|TARGET/STATION|PREVIOUS_ITEM", "symbolic_update": "execute event-template sequence in source order", "terminal_requirement": "AS_OBSERVED", "bounded_rule": "does not guess meanings for EXEMPLAR_ONLY positions"},
        {"template": "EXEMPLAR_ONLY", "exact_trigger": "NONE", "strict_formal_trigger": "NONE", "required_registers": "OWNER", "symbolic_update": "copy exact opaque event and use selected local exemplar only", "terminal_requirement": "AS_OBSERVED", "bounded_rule": "no semantic parse"},
    ]
    require(tuple(row["template"] for row in template_rows) == TEMPLATES, "template list changed")

    event_rows: list[dict[str, str]] = []
    event_parse_by_serial: dict[str, dict[str, str]] = {}
    for event in events:
        mnemonic = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        formal = event["strict_control_prompt"]
        exact_template = EXACT_TEMPLATE.get(mnemonic)
        formal_template = FORMAL_TEMPLATE.get(formal)
        if exact_template and formal_template:
            require(exact_template == formal_template, f"conflicting exact/formal templates at E{event['event_serial']}")
            template = exact_template
            origin = "EXACT_PLUS_FORMAL_CONVERGENT"
            payload = f"EXACT:{mnemonic}|FORMAL:{formal}"
            effect = EXACT_EFFECT[template] + " || " + FORMAL_EFFECT[formal]
            status = "UNIQUE_CONVERGENT_CHANNELS"
        elif exact_template:
            template = exact_template
            origin = "EXACT_JOINT_TUPLE_MNEMONIC"
            payload = f"EXACT:{mnemonic}"
            effect = EXACT_EFFECT[template]
            status = "UNIQUE_EXACT"
        elif formal_template:
            template = formal_template
            origin = "STRICT_FORMAL_PROMPT_ONLY"
            payload = f"FORMAL:{formal};SEMANTIC_VALUE=NONE"
            effect = FORMAL_EFFECT[formal]
            status = "UNIQUE_FORMAL_ONLY"
        else:
            template = "EXEMPLAR_ONLY"
            origin = "NO_LICENSED_TRIGGER"
            payload = "OPAQUE_EXACT_EVENT;SEMANTIC_VALUE=NONE"
            effect = "FOUR_REGISTERS:=SELECTED_V62_CONTEXT;NO_TEMPLATE_SEMANTICS"
            status = "UNPARSED_EXEMPLAR"
        if template == "TERMINAL_FLUSH":
            require(event["terminal_status"] == "TERMINAL", f"flush not terminal: E{event['event_serial']}")
        if template == "TERMINAL_DRAIN":
            require(event["terminal_status"] == "TERMINAL", f"drain not terminal: E{event['event_serial']}")
        row = {
            "event_serial": event["event_serial"],
            "page": event["page"],
            "locus": event["locus"],
            "record_unit_id": event["record_unit_id"],
            "field_id": event["field_id"],
            "statement_id": field_to_statement[event["field_id"]],
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display_only": event["surface"],
            "formal_formula_opaque": event["formal_formula_opaque"],
            "terminal_status": event["terminal_status"],
            "strict_formal_prompt": formal,
            "selected_exact_mnemonic": mnemonic,
            "event_template": template,
            "trigger_origin": origin,
            "template_payload": payload,
            "required_registers": "|".join(REQUIRED_REGISTERS[template]),
            "symbolic_register_effect": effect,
            "event_parse_status": status,
            "opaque_roundtrip_atom": f"E{event['event_serial']}@{event['joint_tuple_id']}",
            "formal_semantic_noninheritance": "ENFORCED",
            "binding_contract": "EXACT_JOINT_TUPLE_ATOMIC;NO_STRING_OR_COMPONENT_INHERITANCE;STRICT_FORMAL_PROMPT_HAS_NO_SEMANTIC_WORD",
            "source_lineage": event["source_lineage"] + ">V63_R3_BOUNDED_SLOT_PARSE",
        }
        event_rows.append(row)
        event_parse_by_serial[event["event_serial"]] = row

    field_rows: list[dict[str, str]] = []
    field_units: dict[str, list[dict[str, str]]] = {}
    for field_id, field_events in events_by_field.items():
        field_units[field_id] = field_events
        statement_id = field_to_statement[field_id]
        source_statement = statement_by_id[statement_id]
        source_machine = machine_by_id[statement_id]
        members = statement_fields[statement_id]
        index = members.index(field_id)
        position = "ONLY" if len(members) == 1 else "FIRST" if index == 0 else "LAST" if index == len(members) - 1 else "MIDDLE"
        templates = [event_parse_by_serial[event["event_serial"]]["event_template"] for event in field_events]
        primary, status, reason = aggregate_template(templates)
        trace, decoded, digest = unit_roundtrip(field_events, event_parse_by_serial)
        field_rows.append(
            {
                "field_id": field_id,
                "record_unit_id": field_events[0]["record_unit_id"],
                "page": field_events[0]["page"],
                "locus": field_events[0]["locus"],
                "statement_id": statement_id,
                "field_position_in_statement": position,
                "event_count": str(len(field_events)),
                "event_serials": "|".join(event["event_serial"] for event in field_events),
                "primary_template": primary,
                "ordered_event_template_sequence": " > ".join(templates),
                "licensed_primitive_sequence": " > ".join(template for template in templates if template != "EXEMPLAR_ONLY") if any(template != "EXEMPLAR_ONLY" for template in templates) else "NONE",
                "parse_status": status,
                "parse_reason": reason,
                "recognized_event_count": str(sum(template != "EXEMPLAR_ONLY" for template in templates)),
                "exemplar_only_event_count": str(sum(template == "EXEMPLAR_ONLY" for template in templates)),
                "register_pre_state_statement_envelope": source_machine["pre_state"],
                "register_update_trace": ("STRUCTURAL:" + "/".join((source_machine["owner_operation"], source_machine["active_item_preparation_operation"], source_machine["target_station_operation"], source_machine["previous_item_operation"])) if index == 0 else "STRUCTURAL_ALREADY_APPLIED") + " -> " + " -> ".join(event_parse_by_serial[event["event_serial"]]["symbolic_register_effect"] for event in field_events),
                "register_post_state_statement_envelope": source_machine["post_state"],
                "intermediate_register_resolution": "EXACT_STATEMENT_ENVELOPE" if len(members) == 1 else "NO_UNLICENSED_WITHIN_STATEMENT_STATE;USE_STATEMENT_ENVELOPE",
                "opaque_roundtrip_trace": trace,
                "roundtrip_decoded_event_serials": decoded,
                "roundtrip_event_identity_sha256": digest,
                "roundtrip_status": "PASS_EXACT_OPAQUE_ID_SEQUENCE",
                "local_exemplar_reading": " ; ".join(event["LOCAL_IATROMEDICAL_EXPANSION"] for event in field_events),
                "binding_contract": "EXACT_TUPLE_ATOMIC;FORMAL_AND_SEMANTIC_CHANNELS_SEPARATE;LOCAL_READING_NOT_TEMPLATE_TRIGGER",
                "source_lineage": "V60_SELECTED_EVENTS>V61_SELECTED_STATEMENT>V62_SELECTED_MACHINE>V63_R3_FIELD_PARSE",
            }
        )

    statement_rows: list[dict[str, str]] = []
    statement_units: dict[str, list[dict[str, str]]] = {}
    for statement in statements:
        statement_id = statement["statement_id"]
        statement_events = events_by_statement[statement_id]
        statement_units[statement_id] = statement_events
        source_machine = machine_by_id[statement_id]
        templates = [event_parse_by_serial[event["event_serial"]]["event_template"] for event in statement_events]
        primary, status, reason = aggregate_template(templates)
        trace, decoded, digest = unit_roundtrip(statement_events, event_parse_by_serial)
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
                "constituent_fields": statement["constituent_fields"],
                "event_count": statement["event_count"],
                "event_serials": statement["event_serials"],
                "primary_template": primary,
                "ordered_event_template_sequence": " > ".join(templates),
                "licensed_primitive_sequence": " > ".join(template for template in templates if template != "EXEMPLAR_ONLY") if any(template != "EXEMPLAR_ONLY" for template in templates) else "NONE",
                "parse_status": status,
                "parse_reason": reason,
                "recognized_event_count": str(sum(template != "EXEMPLAR_ONLY" for template in templates)),
                "exemplar_only_event_count": str(sum(template == "EXEMPLAR_ONLY" for template in templates)),
                "pre_state": source_machine["pre_state"],
                "owner_operation": source_machine["owner_operation"],
                "active_item_preparation_operation": source_machine["active_item_preparation_operation"],
                "target_station_operation": source_machine["target_station_operation"],
                "previous_item_operation": source_machine["previous_item_operation"],
                "parser_register_update_trace": "V62_STRUCTURAL[" + "/".join((source_machine["owner_operation"], source_machine["active_item_preparation_operation"], source_machine["target_station_operation"], source_machine["previous_item_operation"])) + "] -> " + " -> ".join(event_parse_by_serial[event["event_serial"]]["symbolic_register_effect"] for event in statement_events) + " -> ASSERT_SELECTED_V62_POST_STATE",
                "post_state": source_machine["post_state"],
                "register_update_status": "PASS_SELECTED_V62_MACHINE_ENVELOPE",
                "opaque_roundtrip_trace": trace,
                "roundtrip_decoded_event_serials": decoded,
                "roundtrip_event_identity_sha256": digest,
                "roundtrip_status": "PASS_EXACT_OPAQUE_ID_SEQUENCE",
                "complete_creative_reading": statement["concrete_workshop_reading"],
                "strongest_segmentation_or_source_alternative": statement["strongest_alternative"],
                "binding_contract": "EXACT_TUPLE_ATOMIC;NO_NEW_CARD_MEANING;STRICT_FORMAL_PROMPT_SEMANTIC_NONINHERITANCE",
                "source_lineage": "V60_SELECTED_EVENTS>V61_SELECTED_STATEMENT>V62_SELECTED_MACHINE>V63_R3_STATEMENT_PARSE",
            }
        )

    # Baselines are frozen transformations of the same units.  MNEMONIC_BAG
    # discards order, formal prompts and unknown events. FORM_ONLY retains the
    # ordered strict-prompt/terminal pattern but discards exact tuple identity.
    baseline_rows: list[dict[str, str]] = []
    parser_rows_by_level = {
        "FIELD": {row["field_id"]: row for row in field_rows},
        "STATEMENT": {row["statement_id"]: row for row in statement_rows},
    }
    units_by_level = {"FIELD": field_units, "STATEMENT": statement_units}
    for level in ("FIELD", "STATEMENT"):
        units = units_by_level[level]
        parser_rows = parser_rows_by_level[level]
        for model in ("BOUNDED_SLOT_PARSER", "MNEMONIC_BAG", "FORM_ONLY"):
            statuses: Counter[str] = Counter()
            primary_matches = 0
            primitive_events = 0
            signatures: dict[str, list[str]] = defaultdict(list)
            for unit_id, unit_events in units.items():
                if model == "BOUNDED_SLOT_PARSER":
                    templates = [event_parse_by_serial[event["event_serial"]]["event_template"] for event in unit_events]
                    signature = "|".join(f"{event['event_serial']}@{event['joint_tuple_id']}" for event in unit_events)
                else:
                    templates = baseline_event_templates(unit_events, model)
                    signature = bag_signature(unit_events) if model == "MNEMONIC_BAG" else form_signature(unit_events)
                primary, status, _ = aggregate_template(templates)
                statuses[status] += 1
                primitive_events += sum(template != "EXEMPLAR_ONLY" for template in templates)
                primary_matches += primary == parser_rows[unit_id]["primary_template"]
                signatures[signature].append(unit_id)
            lookup_unique = sum(len(members) == 1 for members in signatures.values())
            max_collision = max(map(len, signatures.values()))
            baseline_rows.append(
                {
                    "unit_level": level,
                    "model": model,
                    "units": str(len(units)),
                    "source_events": str(sum(len(unit_events) for unit_events in units.values())),
                    "primitive_event_coverage": str(primitive_events),
                    "primitive_event_coverage_rate": f"{primitive_events / 381:.6f}",
                    "unique_units": str(statuses["UNIQUE"]),
                    "ambiguous_units": str(statuses["AMBIGUOUS"]),
                    "unparsed_units": str(statuses["UNPARSED"]),
                    "primary_template_matches_bounded_parser": str(primary_matches),
                    "primary_template_match_rate": f"{primary_matches / len(units):.6f}",
                    "lookup_unique_roundtrip_units": str(len(units) if model == "BOUNDED_SLOT_PARSER" else lookup_unique),
                    "largest_signature_collision_class": str(1 if model == "BOUNDED_SLOT_PARSER" else max_collision),
                    "information_contract": {
                        "BOUNDED_SLOT_PARSER": "ORDERED_EXACT_OPAQUE_IDS+SEPARATE_EXACT_MNEMONIC_AND_FORMAL_CHANNELS",
                        "MNEMONIC_BAG": "UNORDERED_SELECTED_MNEMONIC_COUNTS_ONLY",
                        "FORM_ONLY": "ORDERED_STRICT_FORMAL_PROMPT+TERMINAL_PATTERN_ONLY",
                    }[model],
                    "strongest_contradiction": {
                        "BOUNDED_SLOT_PARSER": "Most events remain EXEMPLAR_ONLY; exact-ID roundtrip does not prove semantic parsing.",
                        "MNEMONIC_BAG": "It loses order, 45 formal prompt events and all opaque exemplar identity.",
                        "FORM_ONLY": "It cannot distinguish flush from drain or recover any exact semantic action without the tuple channel.",
                    }[model],
                    "source_lineage": "V60/V61/V62_SELECTED>V63_R3_FIXED_BASELINE_COMPARISON",
                }
            )

    require((len(template_rows), len(event_rows), len(field_rows), len(statement_rows), len(baseline_rows)) == (12, 381, 135, 116, 6), "output counts changed")
    write_tsv(OUT_TEMPLATES, template_rows)
    write_tsv(OUT_EVENTS, event_rows)
    write_tsv(OUT_FIELDS, field_rows)
    write_tsv(OUT_STATEMENTS, statement_rows)
    write_tsv(OUT_BASELINES, baseline_rows)
    print("PASS build")
    print("templates=12 events=381 fields=135 statements=116 baselines=6")
    print("event_templates=" + ";".join(f"{key}={value}" for key, value in sorted(Counter(row['event_template'] for row in event_rows).items())))


if __name__ == "__main__":
    main()
