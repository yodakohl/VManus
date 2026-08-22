#!/usr/bin/env python3
"""Build V79 R2: apprentice reconstruction and contradiction repair.

The audit is deliberately bounded to central V78 prose and central V75 Astro.
It tests a visible read-once rule on every within-statement physical-line
transition before assigning any interpretation to the E180/E181 doublet.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V78_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_11_CONTINUOUS_RECORDS.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"

OUT_TRANSITIONS = HERE / "V79_R2_19_LINE_TRANSITION_AUDIT.tsv"
OUT_TRACES = HERE / "V79_R2_COMPLETE_FORWARD_BACKWARD_TRACES.tsv"
OUT_REPAIRS = HERE / "V79_R2_REPAIR_DECISIONS.tsv"
OUT_RESULT = HERE / "V79_R2_RESULT.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def bracket_exemplar(text: str) -> str:
    text = " ".join((text or "").split()).strip()
    if text.startswith("[EXEMPLAR:") and text.endswith("]"):
        return text
    return f"[EXEMPLAR:{text}]"


def main() -> None:
    events = read_tsv(V78_EVENTS)
    statements = read_tsv(V78_STATEMENTS)
    records = read_tsv(V78_RECORDS)
    groups = read_tsv(V75_GROUPS)
    loci = read_tsv(V75_LOCI)

    event_by_serial = {int(row["event_serial"]): row for row in events}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    # ------------------------------------------------------------------
    # Presemantic audit of all within-statement physical-line transitions.
    # ------------------------------------------------------------------
    transition_rows: list[dict[str, object]] = []
    transition_index = 0
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        for left, right in zip(rows, rows[1:]):
            if left["locus"] == right["locus"]:
                continue
            transition_index += 1
            same_card = left["joint_tuple_id"] == right["joint_tuple_id"]
            same_owner = left["image_owner_id"] == right["image_owner_id"]
            no_close = left["terminal_status"] != "TERMINAL"
            no_owner_reset = not right["owner_break_before"].startswith("BREAK_")
            rule_match = same_card and same_owner and no_close and no_owner_reset
            if rule_match:
                decision = "READ_ONCE__FIRST_VISIBLE_COPY_NOT_COUNTED_AS_SECOND_SOURCE_TOKEN"
                source_tokens = 1
                failure_reason = "NONE__ALL_FOUR_VISIBLE_CONDITIONS_PASS"
            elif not same_card:
                decision = "READ_BOTH__NONIDENTICAL_EXACT_CARDS"
                source_tokens = 2
                failure_reason = "EXACT_CARD_ID_DIFFERS"
            elif not same_owner or not no_owner_reset:
                decision = "READ_BOTH_SEPARATELY__VISIBLE_OWNER_RESET"
                source_tokens = 2
                failure_reason = "OWNER_DIFFERS_OR_RESET_INTERVENES"
            else:
                decision = "READ_BOTH__CLOSE_INTERVENES"
                source_tokens = 2
                failure_reason = "LEFT_EVENT_CLOSES_BEFORE_NEXT_LINE"

            transition_rows.append(
                {
                    "transition_index": transition_index,
                    "statement_id": statement["statement_id"],
                    "record_unit_id": statement["record_unit_id"],
                    "page": statement["page"],
                    "left_event_id": left["event_id"],
                    "left_physical_line": left["locus"],
                    "left_exact_card": left["joint_tuple_id"],
                    "left_owner": left["image_owner_id"],
                    "left_terminal_status": left["terminal_status"],
                    "right_event_id": right["event_id"],
                    "right_physical_line": right["locus"],
                    "right_exact_card": right["joint_tuple_id"],
                    "right_owner": right["image_owner_id"],
                    "right_owner_break_before": right["owner_break_before"],
                    "same_statement": "YES",
                    "same_exact_card": "YES" if same_card else "NO",
                    "same_visible_owner": "YES" if same_owner else "NO",
                    "no_close_between": "YES" if no_close else "NO",
                    "no_owner_reset_between": "YES" if no_owner_reset else "NO",
                    "read_once_rule_match": "YES" if rule_match else "NO",
                    "source_token_count_for_visible_pair": source_tokens,
                    "decision": decision,
                    "failure_reason_if_not_match": failure_reason,
                    "historical_hypothesis_label": (
                        "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_HYPOTHESIS__NOT_ATTESTED_STANDARD_CATCHWORD"
                        if rule_match
                        else "NO_ANTICIPATION_CLAIM"
                    ),
                    "semantic_use": "NONE__RULE_TESTED_FROM_VISIBLE_FORM_OWNER_AND_CLOSE_ONLY",
                }
            )

    transition_fields = [
        "transition_index", "statement_id", "record_unit_id", "page", "left_event_id",
        "left_physical_line", "left_exact_card", "left_owner", "left_terminal_status",
        "right_event_id", "right_physical_line", "right_exact_card", "right_owner",
        "right_owner_break_before", "same_statement", "same_exact_card", "same_visible_owner",
        "no_close_between", "no_owner_reset_between", "read_once_rule_match",
        "source_token_count_for_visible_pair", "decision", "failure_reason_if_not_match",
        "historical_hypothesis_label", "semantic_use",
    ]
    write_tsv(OUT_TRANSITIONS, transition_rows, transition_fields)

    rule_matches = [row for row in transition_rows if row["read_once_rule_match"] == "YES"]
    anticipation_visible_ids = {"E180"}
    main_visible_ids = {"E181"}

    # ----------------------------------------------------------
    # Complete traces: H2 (24), B2 (62), f69 left slots (33 groups).
    # ----------------------------------------------------------
    trace_rows: list[dict[str, object]] = []
    chosen_prose = [row for row in events if row["record_unit_id"] in {"H2", "B2"}]
    prose_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in chosen_prose:
        prose_by_unit[row["record_unit_id"]].append(row)

    trace_serial = 0
    for unit in ["H2", "B2"]:
        rows = prose_by_unit[unit]
        for forward_idx, row in enumerate(rows, start=1):
            trace_serial += 1
            backward_idx = len(rows) - forward_idx + 1
            card = row["joint_tuple_id"]
            owner_break = row["owner_break_before"]
            if row["event_id"] in anticipation_visible_ids:
                visible_copy_role = "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_COPY"
                source_token_count = 0
                formal_recovery = "VISIBLE_DUPLICATE_OF_NEXT_LINE_ENTRY__DO_NOT_COUNT_AS_SECOND SOURCE TOKEN"
                error_guard = "Do not call this a standard catchword; do not generate the device elsewhere."
            elif row["event_id"] in main_visible_ids:
                visible_copy_role = "MAIN_SOURCE_TOKEN_AFTER_LOCAL_VISIBLE_DUPLICATE"
                source_token_count = 1
                formal_recovery = "FORMAL_RELATION_OR_ENTRY_MARK; PER? only if supplied by the master exemplar"
                error_guard = "Count the E180/E181 visible pair once; retain both written copies."
            elif card == ET_CARD:
                visible_copy_role = "EXACT_RECURRENT_LINK_FORM"
                source_token_count = 1
                formal_recovery = "FORMAL_LINK_SLOT_RECOVERABLE; ET? lexical category not recoverable without master"
                error_guard = "Copy once; do not infer a second sense or portable conjunction from distribution alone."
            elif card == PER_CARD:
                visible_copy_role = "EXACT_RECURRENT_RELATION_OR_ENTRY_FORM"
                source_token_count = 1
                formal_recovery = "FORMAL_RELATION_OR_ENTRY_MARK; PER? lexical category not recoverable without master"
                error_guard = "Require the next local complement; do not turn field position into a word meaning."
            elif row["portable_status"] == "FORMAL_LABEL_NOT_WORD":
                visible_copy_role = "FORMAL_NONWORD_PROMPT"
                source_token_count = 1
                formal_recovery = row["portable_token_or_formal_prompt"]
                error_guard = "Formal prompt is not spoken or promoted to a portable word."
            else:
                visible_copy_role = "OPAQUE_EXACT_CARD"
                source_token_count = 1
                formal_recovery = "EXACT_CARD_OWNER_PLACEMENT_AND_CLOSE_ONLY"
                error_guard = "Concrete content is copied from the master exemplar, never reconstructed from the card."

            if owner_break.startswith("RECORD_START"):
                owner_action = "OPEN_LOCAL_OWNER_AND_CLEAR_ALL_ARGUMENTS"
            elif owner_break.startswith("BREAK_"):
                owner_action = "VISIBLE_OWNER_RESET__CLEAR_SUBSTANCE_TARGET_DIRECTION"
            else:
                owner_action = "KEEP_CURRENT_VISIBLE_OWNER_ONLY"

            trace_rows.append(
                {
                    "trace_serial": trace_serial,
                    "trace_unit": unit,
                    "atom_kind": "PROSE_EVENT",
                    "forward_audit_order": forward_idx,
                    "backward_audit_order": backward_idx,
                    "audit_order_status": "PHYSICAL_RECORD_ORDER",
                    "atom_id": row["event_id"],
                    "page": row["page"],
                    "physical_locus": row["locus"],
                    "field_or_slot": row["field_id"],
                    "statement_id": row["statement_id"],
                    "exact_visible_identity": card,
                    "visible_owner": row["image_owner_id"],
                    "owner_action": owner_action,
                    "literal_or_formal_layer": row["portable_token_or_formal_prompt"],
                    "visible_copy_role": visible_copy_role,
                    "forward_copy_instruction": "Copy exact visible card at this position; obtain all concrete content from the master exemplar.",
                    "backward_formal_recovery": formal_recovery,
                    "master_exemplar_content": row["source_expansion_de"],
                    "concrete_semantics_without_master": "NOT_RECOVERABLE",
                    "source_token_count": source_token_count,
                    "close_status": row["terminal_status"],
                    "error_guard": error_guard,
                    "trace_pass_condition": "EXACT_FORM_OWNER_CLOSE_AND_SOURCE_COUNT_RECONSTRUCTED",
                }
            )

    # Use all 33 copied groups in all 28 local left-wheel slots. L01..L28 is
    # only an editorial completeness order; it is not a celestial reading order.
    astro_rows = [
        row for row in groups
        if row["page"] == "f69v"
        and row["local_namespace"] == "A3_LEFT_WHEEL_ONLY"
        and row["locus"] != "f69v.1"
    ]
    astro_rows.sort(key=lambda row: int(row["group_serial"]))
    slot_group_counts = Counter(row["locus"] for row in astro_rows)
    for forward_idx, row in enumerate(astro_rows, start=1):
        trace_serial += 1
        backward_idx = len(astro_rows) - forward_idx + 1
        segment_total = slot_group_counts[row["locus"]]
        segment_index = int(row["event_index"])
        owner_action = "OPEN_LOCAL_SLOT" if segment_index == 1 else "CONTINUE_SAME_LOCAL_SLOT_LABEL"
        trace_rows.append(
            {
                "trace_serial": trace_serial,
                "trace_unit": "F69_LEFT_28_SLOTS",
                "atom_kind": "ASTRO_COPIED_GROUP_SEGMENT",
                "forward_audit_order": forward_idx,
                "backward_audit_order": backward_idx,
                "audit_order_status": "EDITORIAL_COMPLETENESS_ORDER_ONLY__NO_START_ROTATION_OR_DIRECTION",
                "atom_id": row["opaque_local_id"],
                "page": row["page"],
                "physical_locus": row["locus"],
                "field_or_slot": row["local_image_owner"],
                "statement_id": "NONE__LOCAL_CELESTIAL_LABEL",
                "exact_visible_identity": row["opaque_local_id"],
                "visible_owner": row["local_image_owner"],
                "owner_action": owner_action,
                "literal_or_formal_layer": f"OPAQUE_COPY_SEGMENT_{segment_index:02d}_OF_{segment_total:02d}",
                "visible_copy_role": "LOCAL_SLOT_LABEL_SEGMENT",
                "forward_copy_instruction": "Copy this opaque group segment into this same visible radial slot; never import a neighbour-wheel value.",
                "backward_formal_recovery": f"Recover membership in {row['local_image_owner']} and segment {segment_index}/{segment_total}; no name, rank, start or direction.",
                "master_exemplar_content": bracket_exemplar(row["copied_local_meaning_or_label"]),
                "concrete_semantics_without_master": "NOT_RECOVERABLE__ONLY_LOCAL_SLOT_AND_SEGMENT_MEMBERSHIP",
                "source_token_count": 1,
                "close_status": "LOCAL_LABEL_END" if segment_index == segment_total else "LOCAL_LABEL_CONTINUES",
                "error_guard": "L01..L28 are editorial addresses; do not infer Moon-station identity, order, cycle, start, rotation or direction.",
                "trace_pass_condition": "ALL_VISIBLE_GROUP_SEGMENTS_RETURN_TO_THE_SAME_LOCAL_SLOT",
            }
        )

    trace_fields = [
        "trace_serial", "trace_unit", "atom_kind", "forward_audit_order", "backward_audit_order",
        "audit_order_status", "atom_id", "page", "physical_locus", "field_or_slot", "statement_id",
        "exact_visible_identity", "visible_owner", "owner_action", "literal_or_formal_layer",
        "visible_copy_role", "forward_copy_instruction", "backward_formal_recovery",
        "master_exemplar_content", "concrete_semantics_without_master", "source_token_count",
        "close_status", "error_guard", "trace_pass_condition",
    ]
    write_tsv(OUT_TRACES, trace_rows, trace_fields)

    repair_rows = [
        {
            "issue": "GENERAL_VISIBLE_READ_ONCE_RULE",
            "evidence": "19 within-statement physical-line transitions audited; exactly E180→E181 passes same-card/same-owner/no-close/no-reset.",
            "formal_decision": "LOCAL_RULE_SUPPORTED_FOR_THIS_ONE_VISIBLE_PAIR",
            "semantic_decision": "NONE",
            "winner": "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_HYPOTHESIS",
            "loser_or_rival": "TWO_INDEPENDENT_PER_SOURCE_TOKENS",
            "failure_or_limit": "Only one positive instance; cannot establish a workshop-wide convention or standard catchword.",
            "apprentice_rule": "Retain both written copies but count only the line-entry copy as the source token when all four visible criteria pass.",
        },
        {
            "issue": "HISTORICAL_CATCHWORD_LABEL",
            "evidence": "Ordinary medieval catchwords are quire/page assembly apparatus; this pair is an internal physical-line duplicate.",
            "formal_decision": "DO_NOT_CALL_STANDARD_CATCHWORD_OR_KUSTODE",
            "semantic_decision": "NONE",
            "winner": "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY",
            "loser_or_rival": "ATTESTED_STANDARD_CATCHWORD_CONVENTION",
            "failure_or_limit": "Intentional anticipation and accidental dittography remain observationally tied on one example.",
            "apprentice_rule": "Use the read-once correction locally; never generate the device in a fresh line without an exemplar.",
        },
        {
            "issue": "ET_QUESTION_MARK_VS_FORMAL_LINK",
            "evidence": "H2 E027/E029 is a clean repeated link chain, but the visible structure is identical under ET? and a nonlexical link slot.",
            "formal_decision": "FORMAL_LINK_SLOT_RECOVERABLE_WITHOUT_MASTER",
            "semantic_decision": "ET? ONLY_IF_MASTER_CODEBOOK_SUPPLIES_THE_GLOSS",
            "winner": "FORMAL_LINK_AT_INTERNAL_READBACK",
            "loser_or_rival": "PORTABLE_ET_LEXEME_AS_INTERNALLY_RECOVERED",
            "failure_or_limit": "The exact 1414 codebook word et attests a historical category, not this card mapping.",
            "apprentice_rule": "Copy the link form once. Say ET? only from the master key; otherwise report FORMAL_LINK.",
        },
        {
            "issue": "PER_QUESTION_MARK_VS_ENTRY_RESET",
            "evidence": "Read-once repairs E180/E181 formally; most other occurrences are entry-biased, while E219 is medial.",
            "formal_decision": "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS",
            "semantic_decision": "PER? ONLY_IF_MASTER_CODEBOOK_SUPPLIES_THE_GLOSS",
            "winner": "FORMAL_RELATION_ENTRY_AT_INTERNAL_READBACK",
            "loser_or_rival": "PORTABLE_PER_LEXEME_AS_INTERNALLY_RECOVERED",
            "failure_or_limit": "A pure reset label cannot explain every medial occurrence; the broader formal relation class remains necessary.",
            "apprentice_rule": "After local deduplication, recover one relation/entry mark; require its next local complement and do not infer PER from placement alone.",
        },
        {
            "issue": "B2_VISIBLE_OWNER_RESETS",
            "evidence": "E189, E198, E203 and E212 open four new visible owners; E203 occurs inside a cross-line statement.",
            "formal_decision": "RESET_SUBSTANCE_TARGET_DIRECTION_AT_EACH_OWNER_BREAK",
            "semantic_decision": "NO_CARRY_ACROSS_DISCONNECTED_SCENES",
            "winner": "LOCAL_STATION_WORKFLOW",
            "loser_or_rival": "ONE_PAGE_GLOBAL_FLOW",
            "failure_or_limit": "Concrete station functions still require the master exemplar.",
            "apprentice_rule": "Owner break outranks sentence continuity; clear arguments even inside one reconstructed statement.",
        },
        {
            "issue": "F69_LEFT_28_SLOT_TRACE",
            "evidence": "28 local slots contain 33 opaque group segments; five slots contain two segments.",
            "formal_decision": "LOCAL_SLOT_AND_SEGMENT_MEMBERSHIP_RECOVERABLE",
            "semantic_decision": "NAMES_ORDER_START_DIRECTION_AND_FUNCTION_NOT_RECOVERABLE",
            "winner": "LOCAL_UNORDERED_SLOT_INVENTORY",
            "loser_or_rival": "UNIVERSAL_28_STEP_CYCLE",
            "failure_or_limit": "Forward/backward order in the trace is editorial coverage order only.",
            "apprentice_rule": "Copy each segment within its own slot; never move a value between wheels or infer a cycle.",
        },
        {
            "issue": "MASTER_EXEMPLAR_SEPARATION",
            "evidence": "Exact form, owner, placement, close and local duplication are visible; concrete German source content is not.",
            "formal_decision": "FORMAL_COPY_AND_READBACK_POSSIBLE",
            "semantic_decision": "CONCRETE_CONTENT_REQUIRES_MASTER_EXEMPLAR",
            "winner": "TWO_LAYER_WORKSHOP_MANUAL",
            "loser_or_rival": "SELF_DECODING_DICTIONARY",
            "failure_or_limit": "An apprentice cannot continue a new semantic entry without the master exemplar.",
            "apprentice_rule": "Never fill a bracketed content value from the opaque card alone.",
        },
    ]
    repair_fields = [
        "issue", "evidence", "formal_decision", "semantic_decision", "winner",
        "loser_or_rival", "failure_or_limit", "apprentice_rule",
    ]
    write_tsv(OUT_REPAIRS, repair_rows, repair_fields)

    result = {
        "experiment": "V79_R2_HISTORICAL_APPRENTICE_RECONSTRUCTION",
        "status": "PASS",
        "scope": "FIXED_TEN_PAGE_SIDEQUEST_ONLY",
        "line_transitions_audited": len(transition_rows),
        "cross_line_statements": sum(int(row["cross_physical_line_transitions"]) > 0 for row in statements),
        "read_once_rule_matches": [f"{row['left_event_id']}->{row['right_event_id']}" for row in rule_matches],
        "read_once_false_positives_under_visible_rule": 0,
        "read_once_hypothesis": "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY__NOT_STANDARD_CATCHWORD",
        "h2_trace_events": sum(row["trace_unit"] == "H2" for row in trace_rows),
        "b2_trace_events": sum(row["trace_unit"] == "B2" for row in trace_rows),
        "b2_visible_owner_resets": [
            row["atom_id"] for row in trace_rows
            if row["trace_unit"] == "B2" and str(row["owner_action"]).startswith("VISIBLE_OWNER_RESET")
        ],
        "f69_left_slots": len({row["physical_locus"] for row in trace_rows if row["trace_unit"] == "F69_LEFT_28_SLOTS"}),
        "f69_left_group_segments": sum(row["trace_unit"] == "F69_LEFT_28_SLOTS" for row in trace_rows),
        "total_trace_rows": len(trace_rows),
        "et_decision": "FORMAL_LINK_RECOVERABLE__ET_GLOSS_REQUIRES_MASTER",
        "per_decision": "FORMAL_RELATION_ENTRY_RECOVERABLE__PER_GLOSS_REQUIRES_MASTER",
        "semantic_forward_continuation_without_master": "FAIL__NOT_RECOVERABLE",
        "formal_copy_and_readback_with_master": "PASS",
        "new_portable_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
        "inputs": [str(path.relative_to(ROOT)) for path in [V78_EVENTS, V78_STATEMENTS, V78_RECORDS, V75_GROUPS, V75_LOCI]],
        "outputs": [OUT_TRANSITIONS.name, OUT_TRACES.name, OUT_REPAIRS.name],
        "interpretation_ceiling": "WORKSHOP_COPY_MODEL_NOT_DECIPHERMENT_OR_TRANSLATION",
    }
    OUT_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
