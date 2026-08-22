#!/usr/bin/env python3
"""Build R4's conservative deterministic V63 slot parser."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V59 = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"
V60 = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"
V61 = ROOT / "experiments/yolo/sidequest_theory_candidates_v61"
V62 = ROOT / "experiments/yolo/sidequest_theory_candidates_v62"
EVENTS_IN = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
FIELDS_IN = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
STATEMENTS_IN = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
REGISTERS_IN = V62 / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"

MNEMONIC_TEMPLATE = {
    "MASS?": ("PARAMETER_VALUE", "ACTIVE", "parameter_slot := EXEMPLAR_VALUE"),
    "ANWENDEN?": ("APPLY_ACTIVE", "ACTIVE|TARGET", "apply(ACTIVE,TARGET?)"),
    "BEREIT?": ("TEST_READY_STATE", "ACTIVE", "test(ACTIVE,READY?)"),
    "ANSATZ?": ("BIND_WORKING_BATCH", "ACTIVE", "assert_or_bind(ACTIVE)"),
    "ZIEL?": ("TARGET_VALUE", "TARGET", "TARGET := EXEMPLAR_TARGET"),
    "KLAR?": ("TEST_CLEAR_STATE", "ACTIVE", "test(ACTIVE,CLEAR?)"),
    "VORIGES?": ("SELECT_PREVIOUS", "PREVIOUS", "ACTIVE := PREVIOUS"),
    "ANTEIL?": ("SELECT_PART", "ACTIVE", "ACTIVE := part_of(ACTIVE)"),
    "TEMPERIEREN?": ("TEMPER_ACTIVE", "ACTIVE", "temper(ACTIVE)"),
    "SPÜLEN?": ("FLUSH_AND_COMMIT", "ACTIVE|TARGET", "flush(ACTIVE,TARGET?); commit"),
    "ABLASSEN?": ("DRAIN_AND_COMMIT", "ACTIVE|TARGET", "drain(ACTIVE,TARGET?); commit"),
}

STRICT_TEMPLATE = {
    "VORGABEPARAMETER?": ("REQUEST_STANDARD_PARAMETER", "ACTIVE", "request(parameter_slot)"),
    "STANDARDSLOT_SETZEN": ("FORMAL_SET_STANDARD_SLOT", "ACTIVE", "set(standard_slot)"),
    "LOKALEN_RELATIONSSLOT_SETZEN": ("FORMAL_SET_RELATION_SLOT", "TARGET", "set(local_relation_slot)"),
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": ("FORMAL_LINK_ACTIVE_STATE", "ACTIVE", "link(active_work_state)"),
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    events = read(EVENTS_IN)
    fields = read(FIELDS_IN)
    statements = read(STATEMENTS_IN)
    registers = read(REGISTERS_IN)
    register_by_statement = {row["statement_id"]: row for row in registers}
    events_by_field = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)

    template_rows = []
    for marker, (template, requires, effect) in MNEMONIC_TEMPLATE.items():
        template_rows.append({
            "trigger_layer": "EXACT_CARD_MNEMONIC",
            "trigger": marker,
            "template_id": template,
            "required_anonymous_registers": requires,
            "formal_effect": effect,
            "semantic_ceiling": "WORKING_MNEMONIC_ONLY",
        })
    for marker, (template, requires, effect) in STRICT_TEMPLATE.items():
        template_rows.append({
            "trigger_layer": "STRICT_FORMAL_PROMPT",
            "trigger": marker,
            "template_id": template,
            "required_anonymous_registers": requires,
            "formal_effect": effect,
            "semantic_ceiling": "FORMAL_CONTROL_NOT_SOURCE_WORD",
        })

    field_rows = []
    event_anchor_count = 0
    for field in fields:
        signals = []
        templates = []
        effects = []
        requirements = []
        anchor_events = set()
        for event in events_by_field[field["field_id"]]:
            mnemonic = event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            strict = event["strict_control_prompt"]
            if strict in STRICT_TEMPLATE:
                template, req, effect = STRICT_TEMPLATE[strict]
                signals.append(f"E{event['event_serial']}:FORMAL={strict}")
                templates.append(template)
                effects.append(effect)
                requirements.extend(req.split("|"))
                anchor_events.add(event["event_serial"])
            if mnemonic in MNEMONIC_TEMPLATE:
                template, req, effect = MNEMONIC_TEMPLATE[mnemonic]
                signals.append(f"E{event['event_serial']}:MNEMONIC={mnemonic}")
                templates.append(template)
                effects.append(effect)
                requirements.extend(req.split("|"))
                anchor_events.add(event["event_serial"])
        event_anchor_count += len(anchor_events)
        if not templates:
            parse_class = "EXEMPLAR_ONLY"
            template_sequence = "EXEMPLAR_ONLY"
            formal_effects = "NONE"
            required = "OWNER|ACTIVE"
        elif len(templates) == 1:
            parse_class = "SINGLE_TEMPLATE"
            template_sequence = templates[0]
            formal_effects = effects[0]
            required = "|".join(dict.fromkeys(requirements))
        else:
            parse_class = "COMPOSITE_SEQUENCE"
            template_sequence = " > ".join(templates)
            formal_effects = " ; ".join(effects)
            required = "|".join(dict.fromkeys(requirements))
        field_rows.append({
            "field_id": field["field_id"],
            "page": field["page"],
            "record_unit_id": field["record_unit_id"],
            "locus": field["locus"],
            "surface_sequence": field["surface_sequence"],
            "closure_status": field["closure_status"],
            "anchor_event_count": len(anchor_events),
            "observed_trigger_sequence": " | ".join(signals) if signals else "NONE",
            "parse_class": parse_class,
            "template_sequence": template_sequence,
            "required_anonymous_registers": required,
            "formal_effect_sequence": formal_effects,
            "creative_local_expansion": field["LOCAL_IATROMEDICAL_EXPANSION"],
            "strongest_rival": "MNEMONIC_BAG_WITHOUT_ORDER" if templates else "WHOLE_FIELD_EXEMPLAR",
        })

    field_by_id = {row["field_id"]: row for row in field_rows}
    statement_rows = []
    for statement in statements:
        field_ids = statement["constituent_fields"].split("|")
        selected_fields = [field_by_id[field_id] for field_id in field_ids]
        parsed = [row for row in selected_fields if row["parse_class"] != "EXEMPLAR_ONLY"]
        template_sequence = " || ".join(row["template_sequence"] for row in parsed) if parsed else "EXEMPLAR_ONLY"
        parse_class = "EXEMPLAR_ONLY" if not parsed else ("FULLY_ANCHORED" if len(parsed) == len(selected_fields) else "PARTIALLY_ANCHORED")
        register = register_by_statement[statement["statement_id"]]
        statement_rows.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "field_ids": "|".join(field_ids),
            "field_count": len(field_ids),
            "anchored_field_count": len(parsed),
            "parse_class": parse_class,
            "template_sequence": template_sequence,
            "pre_state": register.get("pre_state", register.get("input_state", "SEE_REGISTER_LEDGER")),
            "post_state": register.get("post_state", register.get("output_state", "SEE_REGISTER_LEDGER")),
            "creative_source_clause": statement["concrete_workshop_reading"],
            "backward_rule": "templates + anonymous register transition + exemplar tail",
            "strongest_rival": "UNORDERED_SELECTED_MNEMONIC_BAG",
            "status": "SLOT_PARSE_NOT_LANGUAGE_GRAMMAR",
        })

    outputs = {
        "templates": HERE / "V63_R4_TEMPLATE_INVENTORY.tsv",
        "fields": HERE / "V63_R4_135_FIELD_SLOT_PARSES.tsv",
        "statements": HERE / "V63_R4_116_STATEMENT_SLOT_PARSES.tsv",
    }
    write(outputs["templates"], template_rows)
    write(outputs["fields"], field_rows)
    write(outputs["statements"], statement_rows)
    field_classes = Counter(row["parse_class"] for row in field_rows)
    statement_classes = Counter(row["parse_class"] for row in statement_rows)
    checks = {
        "templates_15": len(template_rows) == 15,
        "fields_135": len(field_rows) == 135,
        "statements_116": len(statement_rows) == 116,
        "events_union_119": event_anchor_count == 119,
        "all_fields_once": len({row["field_id"] for row in field_rows}) == 135,
        "no_unknown_trigger": all(row["parse_class"] == "EXEMPLAR_ONLY" or row["observed_trigger_sequence"] != "NONE" for row in field_rows),
        "no_f84": all(not row["page"].startswith("f84") for row in statement_rows),
    }
    validation = {
        "schema": "SIDEQUEST_V63_R4_CONSERVATIVE_SLOT_PARSER_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "field_classes": dict(field_classes),
            "statement_classes": dict(statement_classes),
            "anchored_event_union": event_anchor_count,
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (EVENTS_IN, FIELDS_IN, STATEMENTS_IN, REGISTERS_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V63_R4_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("V63 R4 validation failed")


if __name__ == "__main__":
    main()
