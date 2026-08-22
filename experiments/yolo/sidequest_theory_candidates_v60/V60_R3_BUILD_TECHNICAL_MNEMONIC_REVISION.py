#!/usr/bin/env python3
"""Build the V60 R3 exact-card technical mnemonic pressure test."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V59 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v59"
SOURCE_CARDS = V59 / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv"
SOURCE_EVENTS = V59 / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"

OUT_DECISIONS = HERE / "V60_R3_11_CARD_TECHNICAL_DECISIONS.tsv"
OUT_AUDIT = HERE / "V60_R3_85_OCCURRENCE_AUDIT.tsv"
OUT_CARDS = HERE / "V60_R3_REVISED_STRICT_173_CARD_DICTIONARY.tsv"
OUT_EVENTS = HERE / "V60_R3_REVISED_STRICT_381_EVENT_INTERLINEAR.tsv"


DECISIONS = [
    {
        "card": "AIIN",
        "exact_id": "2f1c5e56e8f0ff459065",
        "previous": "MASS?",
        "winner": "SOLLWERT?",
        "rival_1": "MASS?",
        "rival_2": "DAUER?",
        "source_class": "PARAMETER_REFERENCE_CARD",
        "process_state_effect": "active_slot.value := prescribed_reference",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "Generic prescribed reference survives all positions and both registers; exact numeric kind remains a local filler.",
        "contradiction": "No visible scale or unit exists, and five field-final occurrences leave the governed slot implicit.",
        "confidence": "0.74",
        "decision": "REVISE_MASS_TO_BROADER_TECHNICAL_PARAMETER",
    },
    {
        "card": "OKY",
        "exact_id": "276a7c2d74d1143446f4",
        "previous": "VERWENDEN?",
        "winner": "AUSFÜHREN?",
        "rival_1": "VERWENDEN?",
        "rival_2": "BUCHEN?",
        "source_class": "ACTION_EXECUTION_CARD",
        "process_state_effect": "execute(active_item); advance active_work_state",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "A generic execute instruction covers use, application and facility-cycle continuation without naming the object.",
        "contradiction": "One occurrence is a complete one-card field, so both action and object must be inherited; no external action referent exists.",
        "confidence": "0.58",
        "decision": "REVISE_USE_TO_GENERIC_EXECUTION",
    },
    {
        "card": "CTHY",
        "exact_id": "e0b630cb1b5df5e7105b",
        "previous": "BEREIT?",
        "winner": "FREIGABE?",
        "rival_1": "BEREIT?",
        "rival_2": "HALTEN?",
        "source_class": "STATE_GATE_CARD",
        "process_state_effect": "active_item.ready := true; permit next operation",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "Seven nonterminal occurrences act naturally as a gate between preparation and the following local operation.",
        "contradiction": "Six of seven are medial and could be an ordinary connector or inherited stencil prompt rather than a stored readiness state.",
        "confidence": "0.61",
        "decision": "REVISE_READY_TO_EXECUTABLE_RELEASE_GATE",
    },
    {
        "card": "OR",
        "exact_id": "7a4bb8136330ee4e6e56",
        "previous": "BEREITUNG?",
        "winner": "ANSATZ?",
        "rival_1": "BEREITUNG?",
        "rival_2": "CHARGE?",
        "source_class": "ACTIVE_BATCH_CARD",
        "process_state_effect": "active_batch := prepared_working_lot",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "A prepared working lot fits five Herbal and two Bio entries and supports record-level batch bookkeeping.",
        "contradiction": "The exact card occurs twice consecutively in one field; identical adjacent loads may be copying cadence rather than two batches.",
        "confidence": "0.60",
        "decision": "REVISE_PREPARATION_TO_TECHNICAL_BATCH",
    },
    {
        "card": "AL",
        "exact_id": "dd0ecaf5e27d81befffc",
        "previous": "AN?",
        "winner": "ZIEL?",
        "rival_1": "AN?",
        "rival_2": "STATION?",
        "source_class": "TARGET_RELATION_CARD",
        "process_state_effect": "route.target := pictured_or_local_destination",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "The target-slot reading tolerates first, medial, last and inherited one-card use across Herbal and Bio.",
        "contradiction": "The only one-card field and several field-initial cases contain no overt route operand; the target is supplied entirely by picture or stencil.",
        "confidence": "0.50",
        "decision": "REVISE_PREPOSITION_TO_TARGET_SLOT",
    },
    {
        "card": "EY",
        "exact_id": "b5df9126607030b95175",
        "previous": "KLAR?",
        "winner": "KLARLAUF?",
        "rival_1": "KLAR?",
        "rival_2": "FILTERN?",
        "source_class": "STATE_THRESHOLD_CARD",
        "process_state_effect": "flow_state.clarity := threshold_reached",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "Four open occurrences can mark a clear-flow threshold without importing the filtering apparatus or medium.",
        "contradiction": "The occurrences split across first, medial and last positions; clarity may be a local action expansion rather than a stable state value.",
        "confidence": "0.49",
        "decision": "REVISE_GENERIC_CLEAR_TO_FLOW_THRESHOLD",
    },
    {
        "card": "OLOR",
        "exact_id": "dec401773c1f0347793d",
        "previous": "ZUVOR?",
        "winner": "VORLAUF?",
        "rival_1": "ZUVOR?",
        "rival_2": "RÜCKLAUF?",
        "source_class": "PRIOR_BATCH_RELATION_CARD",
        "process_state_effect": "link.source := previous_batch_or_run",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "Both occurrences supply a plausible previous-run operand in one Herbal and one Bio record.",
        "contradiction": "There are only two occurrences and both touch an exact LINK card, so the prior relation cannot be isolated from the larger construction.",
        "confidence": "0.48",
        "decision": "REVISE_ANAPHOR_TO_PRIOR_RUN_REFERENCE",
    },
    {
        "card": "OTCHEY",
        "exact_id": "faf321940aed922846a9",
        "previous": "TEIL?",
        "winner": "POSTEN?",
        "rival_1": "TEIL?",
        "rival_2": "ABSCHNITT?",
        "source_class": "MARKED_ITEM_SELECTOR_CARD",
        "process_state_effect": "active_item := marked_lot_or_section",
        "scope": "CROSS_REGISTER_EXPLORATORY_EXACT_CARD",
        "assessment": "Both line-initial occurrences open a selected subitem before its local specification.",
        "contradiction": "Only two occurrences exist and their plant-part versus apparatus-run owners differ; the formal marked frame may explain all apparent content.",
        "confidence": "0.40",
        "decision": "REVISE_PART_TO_MARKED_WORK_ITEM",
    },
    {
        "card": "OKEEY",
        "exact_id": "0275fbf14e07935b0a45",
        "previous": "WARM?",
        "winner": "TEMPERIEREN?",
        "rival_1": "WARMHALTEN?",
        "rival_2": "NACHFÜLLEN?",
        "source_class": "TEMPERATURE_CONTROL_CARD",
        "process_state_effect": "temperature_state := working_band",
        "scope": "BIO_LOCAL_EXPLORATORY_EXACT_CARD",
        "assessment": "Seven Bio occurrences precede or follow filtering, flushing, use and transfer as a reusable temperature-control step.",
        "contradiction": "No scale or independent heat referent is visible, and all evidence comes from one register-local expansion deck.",
        "confidence": "0.69",
        "decision": "REVISE_WARM_TO_EXECUTABLE_TEMPERING",
    },
    {
        "card": "OKE",
        "exact_id": "7db18b2f0fb7ed0fcfd3",
        "previous": "SPÜLEN?",
        "winner": "SPÜLEN?",
        "rival_1": "REINIGEN?",
        "rival_2": "UMWÄLZEN?",
        "source_class": "FLUSH_ACTION_CARD_CLOSE_CONFOUNDED",
        "process_state_effect": "working_state := flushed; FORMAL_CLOSE commits field",
        "scope": "BIO_LOCAL_EXPLORATORY_CLOSE_CONFOUNDED_EXACT_CARD",
        "assessment": "All eight Bio occurrences can end a flush/cleaning cell, including three inherited one-card work cells.",
        "contradiction": "All eight are terminal; the exact card may be an opaque committed categorical value with no independently recoverable flush action.",
        "confidence": "0.46",
        "decision": "KEEP_ACTION_BUT_EXPOSE_CLOSE_CONFOUNDING",
    },
    {
        "card": "LCHE",
        "exact_id": "de7321bface5628e35d6",
        "previous": "ABLASSEN?",
        "winner": "ABFÜHREN?",
        "rival_1": "ABLASSEN?",
        "rival_2": "AUSGEBEN?",
        "source_class": "OUTFLOW_ACTION_CARD_CLOSE_CONFOUNDED",
        "process_state_effect": "route active charge to outlet_or_sink; FORMAL_CLOSE commits field",
        "scope": "BIO_LOCAL_EXPLORATORY_CLOSE_CONFOUNDED_EXACT_CARD",
        "assessment": "Eight Bio terminals, five of them one-card cells, accept a generic outflow/dispatch action better than a specified lower drain.",
        "contradiction": "Every occurrence is terminal and five are one-card fields; semantic outflow is inseparable from an inherited categorical answer plus commit.",
        "confidence": "0.51",
        "decision": "REVISE_DRAIN_TO_GENERIC_OUTFLOW_WITH_CLOSE_CAVEAT",
    },
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def position_records(events: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)
    enriched: dict[str, dict[str, str]] = {}
    for members in by_field.values():
        for index, event in enumerate(members):
            if len(members) == 1:
                position = "ONLY"
            elif index == 0:
                position = "FIRST"
            elif index == len(members) - 1:
                position = "LAST"
            else:
                position = "MIDDLE"
            copy = dict(event)
            copy["field_position"] = position
            copy["field_length"] = str(len(members))
            copy["previous_exact_id"] = members[index - 1]["joint_tuple_id"] if index else "FIELD_START"
            copy["next_exact_id"] = members[index + 1]["joint_tuple_id"] if index + 1 < len(members) else "FIELD_END"
            enriched[event["event_serial"]] = copy
    return enriched


def occurrence_fit(decision: dict[str, str], event: dict[str, str]) -> str:
    card = decision["card"]
    serial = int(event["event_serial"])
    if card in {"OKE", "LCHE"}:
        return "CLOSE_CONFOUNDED_NOT_DISPROVED"
    if card == "OLOR":
        return "LINK_NEIGHBOR_CONFOUNDED"
    if card == "OTCHEY":
        return "FORMAL_FRAME_CONFOUNDED"
    if card == "OR" and serial in {33, 34}:
        return "ADJACENT_IDENTICAL_CARD_PRESSURE"
    if card == "AL" and serial == 166:
        return "ONE_CARD_INHERITED_TARGET_PRESSURE"
    if card == "OKY" and serial == 247:
        return "ONE_CARD_INHERITED_ACTION_PRESSURE"
    if card == "EY":
        return "STATE_VERSUS_ACTION_UNRESOLVED"
    return "COMPATIBLE_WITH_TECHNICAL_DEFAULT_AND_LOCAL_FILLER"


def main() -> None:
    require(SOURCE_CARDS.is_file() and SOURCE_EVENTS.is_file(), "canonical V59 R1 sources missing")
    source_cards = read_tsv(SOURCE_CARDS)
    source_events = read_tsv(SOURCE_EVENTS)
    require(len(source_cards) == 173 and len(source_events) == 381, "canonical V59 R1 counts changed")
    decision_by_id = {row["exact_id"]: row for row in DECISIONS}
    require(len(decision_by_id) == 11, "decision IDs must be unique")
    card_by_id = {row["joint_tuple_id"]: row for row in source_cards}
    require(set(decision_by_id) <= set(card_by_id), "target ID absent from canonical dictionary")
    for exact_id, decision in decision_by_id.items():
        require(card_by_id[exact_id]["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == decision["previous"], f"V59 mnemonic changed for {decision['card']}")

    enriched = position_records(source_events)
    target_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        if event["joint_tuple_id"] in decision_by_id:
            target_events[event["joint_tuple_id"]].append(enriched[event["event_serial"]])
    require(sum(map(len, target_events.values())) == 85, "target occurrence count must be 85")

    decision_rows: list[dict[str, str]] = []
    for decision in DECISIONS:
        exact_id = decision["exact_id"]
        occurrences = target_events[exact_id]
        positions = Counter(event["field_position"] for event in occurrences)
        registers = Counter("HERBAL" if event["record_unit_id"].startswith("H") else "BIO" for event in occurrences)
        position_summary = ";".join(f"{name}={positions.get(name, 0)}" for name in ("FIRST", "MIDDLE", "LAST", "ONLY"))
        register_summary = ";".join(f"{name}={registers.get(name, 0)}" for name in ("HERBAL", "BIO"))
        decision_rows.append(
            {
                "card": decision["card"],
                "exact_joint_tuple_id": exact_id,
                "surface_examples_display_only": card_by_id[exact_id]["surface_examples"],
                "V59_R1_previous_mnemonic": decision["previous"],
                "V60_R3_selected_technical_default": decision["winner"],
                "rival_1": decision["rival_1"],
                "rival_2": decision["rival_2"],
                "source_class": decision["source_class"],
                "process_state_effect": decision["process_state_effect"],
                "occurrences_checked": str(len(occurrences)),
                "event_serials_checked": ",".join(f"E{event['event_serial']}" for event in occurrences),
                "pages": "|".join(sorted({event["page"] for event in occurrences})),
                "record_units": "|".join(sorted({event["record_unit_id"] for event in occurrences})),
                "register_counts": register_summary,
                "field_position_counts": position_summary,
                "physical_line_initial_count": str(sum(event["event_index_in_locus"] == "1" for event in occurrences)),
                "terminal_count": str(sum(event["terminal_status"] == "TERMINAL" for event in occurrences)),
                "strict_control_prompt_count": str(sum(event["strict_control_prompt"] != "NONE" for event in occurrences)),
                "all_occurrence_assessment": decision["assessment"],
                "strongest_contradiction": decision["contradiction"],
                "confidence": decision["confidence"],
                "decision": decision["decision"],
                "binding_basis": "EXACT_JOINT_TUPLE_ID_ONLY",
            }
        )

    final_mnemonic = {exact_id: decision["winner"] for exact_id, decision in decision_by_id.items()}
    audit_rows: list[dict[str, str]] = []
    audit_serial = 0
    for decision in DECISIONS:
        for event in target_events[decision["exact_id"]]:
            audit_serial += 1
            prev_id = event["previous_exact_id"]
            next_id = event["next_exact_id"]
            audit_rows.append(
                {
                    "audit_serial": str(audit_serial),
                    "card": decision["card"],
                    "exact_joint_tuple_id": decision["exact_id"],
                    "V60_R3_selected_technical_default": decision["winner"],
                    "event_serial": event["event_serial"],
                    "page": event["page"],
                    "locus": event["locus"],
                    "record_unit_id": event["record_unit_id"],
                    "field_id": event["field_id"],
                    "field_position": event["field_position"],
                    "field_length": event["field_length"],
                    "physical_line_initial": "YES" if event["event_index_in_locus"] == "1" else "NO",
                    "terminal_status": event["terminal_status"],
                    "strict_control_prompt": event["strict_control_prompt"],
                    "surface_display_only": event["surface"],
                    "previous_exact_id": prev_id,
                    "previous_final_mnemonic": final_mnemonic.get(prev_id, "UNKNOWN_EXEMPLAR") if prev_id != "FIELD_START" else "FIELD_START",
                    "next_exact_id": next_id,
                    "next_final_mnemonic": final_mnemonic.get(next_id, "UNKNOWN_EXEMPLAR") if next_id != "FIELD_END" else "FIELD_END",
                    "LOCAL_IATROMEDICAL_EXPANSION": event["LOCAL_IATROMEDICAL_EXPANSION"],
                    "NONMEDICAL_RIVAL": event["NONMEDICAL_RIVAL"],
                    "source_class": decision["source_class"],
                    "process_state_effect": decision["process_state_effect"],
                    "occurrence_fit": occurrence_fit(decision, event),
                    "strongest_card_contradiction": decision["contradiction"],
                    "confidence": decision["confidence"],
                    "binding_basis": "EXACT_JOINT_TUPLE_ID_ONLY",
                }
            )

    revised_cards: list[dict[str, str]] = []
    for source in source_cards:
        exact_id = source["joint_tuple_id"]
        decision = decision_by_id.get(exact_id)
        row = dict(source)
        row["V59_R1_PREVIOUS_MNEMONIC"] = source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        if decision:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = decision["winner"]
            row["mnemonic_scope"] = decision["scope"]
            row["V60_R3_SOURCE_CLASS"] = decision["source_class"]
            row["V60_R3_PROCESS_STATE_EFFECT"] = decision["process_state_effect"]
            row["V60_R3_RIVAL_1"] = decision["rival_1"]
            row["V60_R3_RIVAL_2"] = decision["rival_2"]
            row["V60_R3_STRONGEST_CONTRADICTION"] = decision["contradiction"]
            row["V60_R3_CONFIDENCE"] = decision["confidence"]
            row["V60_R3_DECISION"] = decision["decision"]
            row["UNKNOWN_EXEMPLAR_STATUS"] = source["UNKNOWN_EXEMPLAR_STATUS"] + ";V60_R3_EXACT_CARD_TECHNICAL_DEFAULT_EXPLORATORY"
        else:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = "UNKNOWN_EXEMPLAR"
            row["mnemonic_scope"] = "UNKNOWN_EXEMPLAR"
            row["V60_R3_SOURCE_CLASS"] = "UNKNOWN_EXEMPLAR"
            row["V60_R3_PROCESS_STATE_EFFECT"] = "COPY_LOCAL_EXEMPLAR_NO_SEMANTIC_TRANSITION"
            row["V60_R3_RIVAL_1"] = "NONE"
            row["V60_R3_RIVAL_2"] = "NONE"
            row["V60_R3_STRONGEST_CONTRADICTION"] = "NOT_IN_V60_ELEVEN_CARD_TARGET_SET"
            row["V60_R3_CONFIDENCE"] = "0.00"
            row["V60_R3_DECISION"] = "UNKNOWN_EXEMPLAR"
        row["V60_R3_BINDING_BASIS"] = "EXACT_JOINT_TUPLE_ID_ONLY"
        row["V60_R3_COMPONENT_INHERITANCE"] = "FORBIDDEN"
        row["source_lineage"] = source["source_lineage"] + ">V60_R3"
        revised_cards.append(row)

    revised_events: list[dict[str, str]] = []
    for source in source_events:
        exact_id = source["joint_tuple_id"]
        decision = decision_by_id.get(exact_id)
        positional = enriched[source["event_serial"]]
        row = dict(source)
        row["V59_R1_PREVIOUS_MNEMONIC"] = source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        row["V60_R3_FIELD_POSITION"] = positional["field_position"]
        if decision:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = decision["winner"]
            row["mnemonic_scope"] = decision["scope"]
            row["V60_R3_SOURCE_CLASS"] = decision["source_class"]
            row["V60_R3_PROCESS_STATE_EFFECT"] = decision["process_state_effect"]
            row["V60_R3_OCCURRENCE_FIT"] = occurrence_fit(decision, positional)
            row["V60_R3_CONFIDENCE"] = decision["confidence"]
            row["UNKNOWN_EXEMPLAR_STATUS"] = source["UNKNOWN_EXEMPLAR_STATUS"] + ";V60_R3_EXACT_CARD_TECHNICAL_DEFAULT_EXPLORATORY"
        else:
            row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] = "UNKNOWN_EXEMPLAR"
            row["mnemonic_scope"] = "UNKNOWN_EXEMPLAR"
            row["V60_R3_SOURCE_CLASS"] = "UNKNOWN_EXEMPLAR"
            row["V60_R3_PROCESS_STATE_EFFECT"] = "COPY_LOCAL_EXEMPLAR_NO_SEMANTIC_TRANSITION"
            row["V60_R3_OCCURRENCE_FIT"] = "NOT_IN_V60_ELEVEN_CARD_TARGET_SET"
            row["V60_R3_CONFIDENCE"] = "0.00"
        row["V60_R3_BINDING_BASIS"] = "EXACT_JOINT_TUPLE_ID_ONLY"
        row["V60_R3_COMPONENT_INHERITANCE"] = "FORBIDDEN"
        row["V60_R3_LINE_STATEMENT_STATUS"] = "PHYSICAL_LINE_NOT_SENTENCE"
        row["source_lineage"] = source["source_lineage"] + ">V60_R3"
        revised_events.append(row)

    decision_fields = list(decision_rows[0])
    audit_fields = list(audit_rows[0])
    card_fields = list(revised_cards[0])
    event_fields = list(revised_events[0])
    write_tsv(OUT_DECISIONS, decision_rows, decision_fields)
    write_tsv(OUT_AUDIT, audit_rows, audit_fields)
    write_tsv(OUT_CARDS, revised_cards, card_fields)
    write_tsv(OUT_EVENTS, revised_events, event_fields)
    print("PASS build")
    print(f"decisions={len(decision_rows)} audited_occurrences={len(audit_rows)} cards={len(revised_cards)} events={len(revised_events)}")


if __name__ == "__main__":
    main()
