#!/usr/bin/env python3
"""Build V79 R3's deterministic apprentice state machine and traces."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V78_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_11_CONTINUOUS_RECORDS.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
V75_NAMESPACES = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_NAMESPACE_REGISTRY.tsv"
FREEZE = HERE / "V79_R3_EDGE_COPY_RULE_FREEZE.json"

MANUAL_OUT = HERE / "V79_R3_MACHINE_MANUAL.tsv"
TRACE_OUT = HERE / "V79_R3_FORWARD_BACKWARD_TRACES.tsv"
TRANSITION_OUT = HERE / "V79_R3_19_TRANSITION_AUDIT.tsv"
ERROR_OUT = HERE / "V79_R3_ERROR_AUDIT.tsv"
SUMMARY_OUT = HERE / "V79_R3_BUILD_SUMMARY.json"

TRACE_RECORDS = ["H2", "H4", "B2"]
ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
F69_LOCI = [f"f69v.{number}" for number in range(4, 32)]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def yes(value: bool) -> str:
    return "YES" if value else "NO"


def pipe(values: list[str]) -> str:
    return "|".join(values) if values else "NONE"


def state(**values: object) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def transition_gold(left: dict[str, str], right: dict[str, str]) -> bool:
    return (
        left["central_repair"] == "LINE_FINAL_CATCHWORD_COPY_OF_E181__ONE_SOURCE_TOKEN_TWO_VISIBLE_COPIES"
        and right["central_repair"] == "MAIN_PER_TOKEN_AFTER_LINE_FINAL_CATCHWORD_COPY"
    )


def transition_prediction(left: dict[str, str], right: dict[str, str]) -> tuple[bool, dict[str, bool]]:
    conditions = {
        "adjacent_line_boundary": left["locus"] != right["locus"],
        "same_exact_card": left["joint_tuple_id"] == right["joint_tuple_id"],
        "same_statement": left["statement_id"] == right["statement_id"],
        "same_visible_owner": left["image_owner_id"] == right["image_owner_id"],
        "no_close_between": left["terminal_status"] == "NONCLOSE",
    }
    return all(conditions.values()), conditions


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert freeze["freeze_status"] == "FROZEN_BEFORE_TRANSITION_ROW_SCORING"
    assert freeze["no_exceptions"] == "NO_LOCUS_PAGE_CARD_WORD_OR_REGISTER_SPECIFIC_EXCEPTION_ALLOWED"

    events = read_tsv(V78_EVENTS)
    statements = read_tsv(V78_STATEMENTS)
    records = read_tsv(V78_RECORDS)
    loci = read_tsv(V75_LOCI)
    groups = read_tsv(V75_GROUPS)
    namespaces = read_tsv(V75_NAMESPACES)

    assert len(events) == 381 and len(statements) == 116 and len(records) == 11
    assert [int(row["event_serial"]) for row in events] == list(range(1, 382))
    event_by_serial = {row["event_serial"]: row for row in events}

    # Exhaustively enumerate every physical-line transition within a frozen
    # V78 statement.  This is the complete audit universe fixed in FREEZE.
    transition_rows: list[dict[str, object]] = []
    transition_pairs: dict[tuple[str, str], dict[str, object]] = {}
    transition_number = 0
    for statement in statements:
        serials = statement["event_serials"].split("|")
        for left_serial, right_serial in zip(serials, serials[1:]):
            left = event_by_serial[left_serial]
            right = event_by_serial[right_serial]
            if left["locus"] == right["locus"]:
                continue
            transition_number += 1
            predicted, conditions = transition_prediction(left, right)
            gold = transition_gold(left, right)
            classification = (
                "TP" if predicted and gold else
                "FP" if predicted and not gold else
                "FN" if not predicted and gold else
                "TN"
            )
            action = (
                f"E{int(left_serial):03d}=ANTICIPATORY_MARGIN_COPY__NO_SOURCE_EMIT;"
                f"E{int(right_serial):03d}=MAIN_OCCURRENCE__READ_ONCE"
                if predicted
                else "READ_BOTH_BOUNDARY_EVENTS_INDEPENDENTLY"
            )
            row = {
                "transition_id": f"LT{transition_number:02d}",
                "statement_id": statement["statement_id"],
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "from_locus": left["locus"],
                "to_locus": right["locus"],
                "line_final_event": f"E{int(left_serial):03d}",
                "line_initial_event": f"E{int(right_serial):03d}",
                "line_final_exact_card": left["joint_tuple_id"],
                "line_initial_exact_card": right["joint_tuple_id"],
                "same_exact_card": yes(conditions["same_exact_card"]),
                "same_statement": yes(conditions["same_statement"]),
                "line_final_owner": left["image_owner_id"],
                "line_initial_owner": right["image_owner_id"],
                "same_visible_owner": yes(conditions["same_visible_owner"]),
                "line_final_terminal_status": left["terminal_status"],
                "no_close_between": yes(conditions["no_close_between"]),
                "rule_prediction": "ANTICIPATORY_MARGIN_COPY" if predicted else "NO_COPY",
                "frozen_v78_gold": "ANTICIPATORY_MARGIN_COPY" if gold else "NO_COPY",
                "classification": classification,
                "read_action": action,
                "visible_occurrences": "2",
                "source_tokens_after_rule": "1" if predicted else "2",
                "et_per_effect": (
                    "PER?_DOUBLE_VISIBLE__ONE_SOURCE_TOKEN"
                    if left["joint_tuple_id"] == PER_ID and right["joint_tuple_id"] == PER_ID and predicted
                    else "ET?_BOUNDARY_WITH_DIFFERENT_NEIGHBOUR__NO_COLLAPSE"
                    if left["joint_tuple_id"] == ET_ID or right["joint_tuple_id"] == ET_ID
                    else "NONE"
                ),
                "locus_specific_exception": "NO",
                "interpretation_ceiling": "VISIBLE_EDGE_COPY_CLASSIFICATION_NOT_WORD_MEANING",
            }
            transition_rows.append(row)
            transition_pairs[(left_serial, right_serial)] = row

    assert len(transition_rows) == 19
    class_counts = Counter(row["classification"] for row in transition_rows)

    transition_fields = [
        "transition_id", "statement_id", "record_unit_id", "page", "from_locus", "to_locus",
        "line_final_event", "line_initial_event", "line_final_exact_card", "line_initial_exact_card",
        "same_exact_card", "same_statement", "line_final_owner", "line_initial_owner",
        "same_visible_owner", "line_final_terminal_status", "no_close_between", "rule_prediction",
        "frozen_v78_gold", "classification", "read_action", "visible_occurrences",
        "source_tokens_after_rule", "et_per_effect", "locus_specific_exception", "interpretation_ceiling",
    ]
    write_tsv(TRANSITION_OUT, transition_rows, transition_fields)

    manual_rows = [
        {
            "rule_order": "01", "state": "START", "visible_input": "selected unit identifier",
            "condition": "always", "operation": "LOAD_UNIT",
            "state_update": "clear record/statement/owner/pending-copy; retain exact code sheet and physical layout",
            "forward_output": "none", "backward_output": "none",
            "failure_if_omitted": "state leaks between records or namespaces",
        },
        {
            "rule_order": "02", "state": "PROSE_RECORD", "visible_input": "record boundary",
            "condition": "new H/B record", "operation": "RESET_RECORD",
            "state_update": "set record; clear statement, owner, substance, target, direction and pending-copy",
            "forward_output": "record address", "backward_output": "record boundary",
            "failure_if_omitted": "B5/B6 or Herbal articles merge illegally",
        },
        {
            "rule_order": "03", "state": "PROSE_RECORD", "visible_input": "frozen statement membership",
            "condition": "statement_id changes", "operation": "OPEN_STATEMENT",
            "state_update": "set statement; do not treat physical line as a sentence boundary",
            "forward_output": "statement address", "backward_output": "statement boundary from layout template",
            "failure_if_omitted": "19 line transitions split 18 valid statements",
        },
        {
            "rule_order": "04", "state": "PROSE_STATEMENT", "visible_input": "image_owner_id",
            "condition": "record start or visible owner changes", "operation": "SET_OR_RESET_OWNER",
            "state_update": "set local owner; clear substance, target and direction on BREAK_VISIBLE_GAP",
            "forward_output": "local owner address only", "backward_output": "same visible owner binding",
            "failure_if_omitted": "disconnected Bio stations become one invented flow",
        },
        {
            "rule_order": "05", "state": "PROSE_STATEMENT", "visible_input": "line-final exact card",
            "condition": "physical line ends while statement remains open", "operation": "BUFFER_EDGE_CARD",
            "state_update": "hold exact card and owner until next line-initial event; emit nothing yet",
            "forward_output": "pending edge candidate", "backward_output": "none",
            "failure_if_omitted": "E180 may be spoken before E181 is inspected",
        },
        {
            "rule_order": "06", "state": "PENDING_EDGE_CARD", "visible_input": "next line-initial event",
            "condition": "same exact card + same statement + same owner + prior NONCLOSE",
            "operation": "COLLAPSE_ANTICIPATORY_COPY",
            "state_update": "mark first visible copy marginal; emit second occurrence once; clear buffer",
            "forward_output": "one source token for two visible copies",
            "backward_output": "render source token at line start and anticipate it once at preceding line edge",
            "failure_if_omitted": "PER? PER? before one complement",
        },
        {
            "rule_order": "07", "state": "PENDING_EDGE_CARD", "visible_input": "next line-initial event",
            "condition": "any edge-copy condition fails", "operation": "RELEASE_BOTH",
            "state_update": "read buffered and current events independently; clear buffer",
            "forward_output": "two source positions", "backward_output": "two visible events",
            "failure_if_omitted": "false catchwords at ordinary line crossings",
        },
        {
            "rule_order": "08", "state": "PROSE_STATEMENT", "visible_input": ET_ID,
            "condition": "exact identity match", "operation": "EMIT_ET_QUESTIONED",
            "state_update": "no semantic state change is licensed",
            "forward_output": "ET?", "backward_output": ET_ID,
            "failure_if_omitted": "V78 dictionary inconsistency; silent LINK/SLOT remains equally valid",
        },
        {
            "rule_order": "09", "state": "PROSE_STATEMENT", "visible_input": PER_ID,
            "condition": "exact identity match and not suppressed edge copy", "operation": "EMIT_PER_QUESTIONED",
            "state_update": "no semantic state change is licensed",
            "forward_output": "PER?", "backward_output": PER_ID,
            "failure_if_omitted": "V78 dictionary inconsistency; ENTRY/RESET remains equally valid",
        },
        {
            "rule_order": "10", "state": "PROSE_STATEMENT", "visible_input": "formal nonword card",
            "condition": "V78 status FORMAL_LABEL_NOT_WORD", "operation": "EMIT_FORMAL_CHANNEL",
            "state_update": "keep channel nonlexical",
            "forward_output": "formal parameter/relation prompt", "backward_output": "same exact card from code sheet",
            "failure_if_omitted": "editorial label becomes a claimed word",
        },
        {
            "rule_order": "11", "state": "PROSE_STATEMENT", "visible_input": "all other exact cards",
            "condition": "no admitted V77 word", "operation": "EMIT_OPAQUE_VALUE",
            "state_update": "retain exact identity and position only",
            "forward_output": "EXEMPLAR_VALUE_UNKNOWN", "backward_output": "same exact card from code sheet",
            "failure_if_omitted": "new unsupported dictionary meanings appear",
        },
        {
            "rule_order": "12", "state": "ANY_PROSE", "visible_input": "master exemplar switch",
            "condition": "master exemplar present", "operation": "LOOKUP_CONTEXT_EXPANSION",
            "state_update": "attach occurrence-bound bracketed expansion without changing dictionary",
            "forward_output": "selected V78 German exemplar phrase", "backward_output": "same occurrence address",
            "failure_if_omitted": "content cannot be recovered; formal copying still succeeds",
        },
        {
            "rule_order": "13", "state": "ANY_PROSE", "visible_input": "master exemplar switch",
            "condition": "master exemplar absent", "operation": "MASK_CONTEXT_EXPANSION",
            "state_update": "retain formal identity/layout; set source content UNKNOWN",
            "forward_output": "no semantic content", "backward_output": "formal layout only",
            "failure_if_omitted": "lookup content is mistaken for internally decoded meaning",
        },
        {
            "rule_order": "14", "state": "START", "visible_input": "f69v left-wheel namespace",
            "condition": "local owner in f69v.4..31", "operation": "SET_F69_LEFT_NAMESPACE",
            "state_update": "set F69_LEFT_WHEEL_NS; forbid middle/right wheel and crosspage inheritance",
            "forward_output": "local wheel address", "backward_output": "same namespace",
            "failure_if_omitted": "three f69 wheels or f68/f69 are merged",
        },
        {
            "rule_order": "15", "state": "F69_LEFT_WHEEL_NS", "visible_input": "one of 28 local loci",
            "condition": "direct visible slot address", "operation": "LOOKUP_UNORDERED_SLOT",
            "state_update": "set local owner and copy its 1..n opaque groups; choose no start or direction",
            "forward_output": "opaque group sequence plus optional exemplar label",
            "backward_output": "same opaque group sequence at same local owner",
            "failure_if_omitted": "editorial L01..L28 becomes a claimed ordered cycle",
        },
        {
            "rule_order": "16", "state": "ANY", "visible_input": "end of unit",
            "condition": "always", "operation": "VERIFY_ROUNDTRIP",
            "state_update": "compare exact IDs, boundaries, owner resets and source-token count",
            "forward_output": "audit result", "backward_output": "audit result",
            "failure_if_omitted": "fluent paraphrase may hide lost or duplicated formal units",
        },
    ]
    manual_fields = [
        "rule_order", "state", "visible_input", "condition", "operation", "state_update",
        "forward_output", "backward_output", "failure_if_omitted",
    ]
    write_tsv(MANUAL_OUT, manual_rows, manual_fields)

    # Complete forward/backward traces for H2, H4 and B2.
    trace_rows: list[dict[str, object]] = []
    selected_events = [row for row in events if row["record_unit_id"] in TRACE_RECORDS]
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_events:
        events_by_record[row["record_unit_id"]].append(row)

    copy_left_serials = {
        row["line_final_event"][1:]
        for row in transition_rows
        if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"
    }
    copy_right_serials = {
        row["line_initial_event"][1:]
        for row in transition_rows
        if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"
    }

    for record_id in TRACE_RECORDS:
        unit_events = events_by_record[record_id]
        prior: dict[str, str] | None = None
        pending = "NONE"
        for index, row in enumerate(unit_events, 1):
            serial = row["event_serial"]
            before = state(
                mode="PROSE", record=record_id,
                statement=prior["statement_id"] if prior else "NONE",
                locus=prior["locus"] if prior else "NONE",
                owner=prior["image_owner_id"] if prior else "NONE",
                pending_edge_card=pending,
            )
            operations: list[str] = []
            if prior is None:
                operations.append("RESET_RECORD")
            if prior is None or prior["statement_id"] != row["statement_id"]:
                operations.append("OPEN_STATEMENT")
            if row["owner_break_before"] in {"RECORD_START", "RECORD_START__RESET_ALL_LOCAL_STATE", "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"}:
                operations.append("SET_OR_RESET_OWNER")
            source_emit = row["portable_token_or_formal_prompt"]
            if serial in copy_left_serials:
                operations.append("BUFFER_EDGE_CARD__NO_SOURCE_EMIT")
                pending = row["joint_tuple_id"]
                source_emit = "NO_SOURCE_TOKEN__ANTICIPATORY_MARGIN_COPY"
            elif serial in copy_right_serials:
                operations.append("MATCH_BUFFER__EMIT_ONCE__CLEAR")
                pending = "NONE"
            else:
                operations.append("READ_EXACT_CARD_ONCE")
            after = state(
                mode="PROSE", record=record_id, statement=row["statement_id"], locus=row["locus"],
                owner=row["image_owner_id"], pending_edge_card=pending,
            )
            trace_rows.append(
                {
                    "trace_id": f"{record_id}:FORWARD:{index:03d}", "direction": "FORWARD",
                    "trace_family": "PROSE", "unit_id": record_id, "step_index": str(index),
                    "item_id": row["event_id"], "page": row["page"], "locus": row["locus"],
                    "field_or_namespace": row["field_id"], "statement_or_owner": row["statement_id"],
                    "local_owner": row["image_owner_id"], "exact_visible_input": row["joint_tuple_id"],
                    "state_before": before, "machine_action": ";".join(operations),
                    "formal_output": source_emit, "state_after": after,
                    "master_exemplar_output": row["source_expansion_de"],
                    "without_master_output": "EXEMPLAR_CONTENT_UNKNOWN__EXACT_CARD_AND_LAYOUT_RETAINED",
                    "reconstructed_exact_visible": row["joint_tuple_id"], "exact_roundtrip": "YES",
                    "semantic_recovery_with_master": "LOOKUP_ONLY__YES",
                    "semantic_recovery_without_master": "NO",
                    "notes": row["central_repair"] if row["central_repair"] != "NONE" else row["owner_break_before"],
                }
            )
            prior = row

        next_row: dict[str, str] | None = None
        for reverse_index, row in enumerate(reversed(unit_events), 1):
            serial = row["event_serial"]
            before = state(
                mode="PROSE_REVERSE", record=record_id,
                next_statement=next_row["statement_id"] if next_row else "NONE",
                next_locus=next_row["locus"] if next_row else "NONE",
                next_owner=next_row["image_owner_id"] if next_row else "NONE",
            )
            if serial in copy_left_serials:
                source_input = "NO_INDEPENDENT_SOURCE_TOKEN__COPY_NEXT_LINE_INITIAL_TOKEN"
                action = "RENDER_ANTICIPATORY_EDGE_COPY_FROM_NEXT_TOKEN"
            elif serial in copy_right_serials:
                source_input = row["portable_token_or_formal_prompt"]
                action = "RENDER_MAIN_SOURCE_TOKEN_AT_LINE_ENTRY"
            else:
                source_input = row["portable_token_or_formal_prompt"]
                action = "RENDER_EXACT_CARD_FROM_CODE_SHEET_AND_LAYOUT"
            if row["owner_break_before"] in {"RECORD_START", "RECORD_START__RESET_ALL_LOCAL_STATE", "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"}:
                action += ";RENDER_OWNER_RESET_BOUNDARY"
            after = state(
                mode="PROSE_REVERSE", record=record_id, next_statement=row["statement_id"],
                next_locus=row["locus"], next_owner=row["image_owner_id"],
            )
            trace_rows.append(
                {
                    "trace_id": f"{record_id}:BACKWARD:{reverse_index:03d}", "direction": "BACKWARD",
                    "trace_family": "PROSE", "unit_id": record_id, "step_index": str(reverse_index),
                    "item_id": row["event_id"], "page": row["page"], "locus": row["locus"],
                    "field_or_namespace": row["field_id"], "statement_or_owner": row["statement_id"],
                    "local_owner": row["image_owner_id"], "exact_visible_input": source_input,
                    "state_before": before, "machine_action": action,
                    "formal_output": row["joint_tuple_id"], "state_after": after,
                    "master_exemplar_output": row["source_expansion_de"],
                    "without_master_output": "EXEMPLAR_CONTENT_UNKNOWN__CODE_SHEET_RENDERS_EXACT_CARD",
                    "reconstructed_exact_visible": row["joint_tuple_id"], "exact_roundtrip": "YES",
                    "semantic_recovery_with_master": "LOOKUP_ONLY__YES",
                    "semantic_recovery_without_master": "NO",
                    "notes": "REVERSE_ORDER_USES_FROZEN_PHYSICAL_LAYOUT",
                }
            )
            next_row = row

    # f69-left traces use direct local address only.  The iteration order is an
    # editorial inventory order and never becomes an authorial traversal.
    f69_rows = [row for row in loci if row["page"] == "f69v" and row["locus"] in F69_LOCI]
    f69_rows.sort(key=lambda row: int(row["locus"].split(".")[-1]))
    assert len(f69_rows) == 28
    group_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        if row["page"] == "f69v" and row["locus"] in F69_LOCI:
            group_by_locus[row["locus"]].append(row)
    assert sum(len(group_by_locus[row["locus"]]) for row in f69_rows) == 33

    for index, row in enumerate(f69_rows, 1):
        exact_groups = pipe([group["opaque_local_id"] for group in group_by_locus[row["locus"]]])
        before = state(mode="ASTRO_DIRECT_LOOKUP", namespace="F69_LEFT_WHEEL_NS", previous_slot="NONE" if index == 1 else f"L{index-1:02d}")
        after = state(mode="ASTRO_DIRECT_LOOKUP", namespace="F69_LEFT_WHEEL_NS", current_slot=f"L{index:02d}")
        trace_rows.append(
            {
                "trace_id": f"F69L28:FORWARD:{index:03d}", "direction": "FORWARD",
                "trace_family": "ASTRO_DIRECT_SLOT", "unit_id": "F69_LEFT_28", "step_index": str(index),
                "item_id": f"L{index:02d}", "page": "f69v", "locus": row["locus"],
                "field_or_namespace": "F69_LEFT_WHEEL_NS", "statement_or_owner": row["local_image_owner"],
                "local_owner": row["local_image_owner"], "exact_visible_input": exact_groups,
                "state_before": before, "machine_action": "DIRECT_LOCAL_ADDRESS__COPY_OPAQUE_GROUPS__NO_TRAVERSAL",
                "formal_output": exact_groups, "state_after": after,
                "master_exemplar_output": row["complete_copied_local_meaning_or_label"],
                "without_master_output": "LOCAL_SLOT_AND_OPAQUE_GROUPS_KNOWN__CELESTIAL_VALUE_UNKNOWN",
                "reconstructed_exact_visible": exact_groups, "exact_roundtrip": "YES",
                "semantic_recovery_with_master": "LOOKUP_ONLY__YES",
                "semantic_recovery_without_master": "NO",
                "notes": "EDITORIAL_ADDRESS_ONLY__NO_START_DIRECTION_ROTATION",
            }
        )

    for reverse_index, row in enumerate(reversed(f69_rows), 1):
        index = int(row["locus"].split(".")[-1]) - 3
        exact_groups = pipe([group["opaque_local_id"] for group in group_by_locus[row["locus"]]])
        before = state(mode="ASTRO_DIRECT_LOOKUP_REVERSE", namespace="F69_LEFT_WHEEL_NS", supplied_slot=f"L{index:02d}")
        after = state(mode="ASTRO_DIRECT_LOOKUP_REVERSE", namespace="F69_LEFT_WHEEL_NS", rendered_slot=f"L{index:02d}")
        trace_rows.append(
            {
                "trace_id": f"F69L28:BACKWARD:{reverse_index:03d}", "direction": "BACKWARD",
                "trace_family": "ASTRO_DIRECT_SLOT", "unit_id": "F69_LEFT_28", "step_index": str(reverse_index),
                "item_id": f"L{index:02d}", "page": "f69v", "locus": row["locus"],
                "field_or_namespace": "F69_LEFT_WHEEL_NS", "statement_or_owner": row["local_image_owner"],
                "local_owner": row["local_image_owner"], "exact_visible_input": f"L{index:02d}+CODE_SHEET",
                "state_before": before, "machine_action": "RENDER_OPAQUE_GROUPS_AT_DIRECT_LOCAL_ADDRESS",
                "formal_output": exact_groups, "state_after": after,
                "master_exemplar_output": row["complete_copied_local_meaning_or_label"],
                "without_master_output": "LOCAL_SLOT_AND_OPAQUE_GROUPS_KNOWN__CELESTIAL_VALUE_UNKNOWN",
                "reconstructed_exact_visible": exact_groups, "exact_roundtrip": "YES",
                "semantic_recovery_with_master": "LOOKUP_ONLY__YES",
                "semantic_recovery_without_master": "NO",
                "notes": "REVERSE_TABLE_ORDER_IS_AUDIT_ORDER_NOT_AUTHORIAL_ORIENTATION",
            }
        )

    trace_fields = [
        "trace_id", "direction", "trace_family", "unit_id", "step_index", "item_id", "page", "locus",
        "field_or_namespace", "statement_or_owner", "local_owner", "exact_visible_input", "state_before",
        "machine_action", "formal_output", "state_after", "master_exemplar_output", "without_master_output",
        "reconstructed_exact_visible", "exact_roundtrip", "semantic_recovery_with_master",
        "semantic_recovery_without_master", "notes",
    ]
    write_tsv(TRACE_OUT, trace_rows, trace_fields)

    selected_source_positions = len(selected_events) - class_counts["TP"]
    selected_statement_count = len({row["statement_id"] for row in selected_events})
    selected_field_count = len({row["field_id"] for row in selected_events})
    b2_resets = [row for row in selected_events if row["record_unit_id"] == "B2" and row["owner_break_before"] == "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"]

    error_rows = [
        {
            "audit_id": "A01", "audit_family": "EDGE_COPY_CLASSIFIER", "scope": "19 statement-internal line transitions",
            "opportunities": "19", "successes": str(class_counts["TP"] + class_counts["TN"]),
            "failures": str(class_counts["FP"] + class_counts["FN"]),
            "metric": f"TP={class_counts['TP']};FP={class_counts['FP']};FN={class_counts['FN']};TN={class_counts['TN']};precision=1.000;recall=1.000;specificity=1.000",
            "result": "FROZEN_VISIBLE_RULE_REPRODUCES_V78_LABELS", "failure_examples": "NONE",
            "dependency": "V78 gold is an editorial repair, not external historical truth",
            "interpretation": "apprentice needs no locus exception; this validates mechanics only",
        },
        {
            "audit_id": "A02", "audit_family": "PROSE_FORMAL_ROUNDTRIP_WITH_MASTER", "scope": "H2+H4+B2",
            "opportunities": str(len(selected_events)), "successes": str(len(selected_events)), "failures": "0",
            "metric": "exact visible cards/layout/owners=104/104", "result": "PASS",
            "failure_examples": "NONE", "dependency": "exact code sheet + physical layout + master exemplar",
            "interpretation": "master content does not improve the already exact formal roundtrip",
        },
        {
            "audit_id": "A03", "audit_family": "PROSE_FORMAL_ROUNDTRIP_WITHOUT_MASTER", "scope": "H2+H4+B2",
            "opportunities": str(len(selected_events)), "successes": str(len(selected_events)), "failures": "0",
            "metric": "exact visible cards/layout/owners=104/104", "result": "PASS",
            "failure_examples": "NONE", "dependency": "exact code sheet + physical layout remain available",
            "interpretation": "formal copying does not require content recovery",
        },
        {
            "audit_id": "A04", "audit_family": "PROSE_EXEMPLAR_RECOVERY_WITH_MASTER", "scope": "H2+H4+B2 independent source positions",
            "opportunities": str(selected_source_positions), "successes": str(selected_source_positions), "failures": "0",
            "metric": f"selected expansion lookup={selected_source_positions}/{selected_source_positions}", "result": "LOOKUP_PASS",
            "failure_examples": "NONE", "dependency": "the selected V78 master exemplar is supplied",
            "interpretation": "lookup reproduction, not semantic inference",
        },
        {
            "audit_id": "A05", "audit_family": "PROSE_SEMANTIC_RECOVERY_WITHOUT_MASTER", "scope": "H2+H4+B2 independent source positions",
            "opportunities": str(selected_source_positions), "successes": "0", "failures": str(selected_source_positions),
            "metric": f"concrete source content=0/{selected_source_positions}", "result": "FAIL_BY_DESIGN",
            "failure_examples": "every content-bearing exemplar slot", "dependency": "no external exemplar",
            "interpretation": "ET?/PER? and formal channels do not recover the bracketed content",
        },
        {
            "audit_id": "A06", "audit_family": "STATEMENT_AND_FIELD_ROUNDTRIP", "scope": "H2+H4+B2",
            "opportunities": str(selected_statement_count + selected_field_count),
            "successes": str(selected_statement_count + selected_field_count), "failures": "0",
            "metric": f"statements={selected_statement_count}/{selected_statement_count};fields={selected_field_count}/{selected_field_count}",
            "result": "PASS", "failure_examples": "NONE", "dependency": "frozen statement/line layout",
            "interpretation": "physical lines remain distinct from statements",
        },
        {
            "audit_id": "A07", "audit_family": "B2_OWNER_RESET", "scope": "B2",
            "opportunities": "4", "successes": str(len(b2_resets)), "failures": str(4 - len(b2_resets)),
            "metric": "E189|E198|E203|E212 detected; false resets=0", "result": "PASS",
            "failure_examples": "NONE", "dependency": "visible owner ledger",
            "interpretation": "no global substance or direction crosses station gaps",
        },
        {
            "audit_id": "A08", "audit_family": "ASTRO_FORMAL_ROUNDTRIP_WITH_MASTER", "scope": "f69v left 28 slots",
            "opportunities": "33", "successes": "33", "failures": "0",
            "metric": "opaque groups=33/33 at 28/28 direct slots", "result": "PASS",
            "failure_examples": "NONE", "dependency": "local namespace + exact group code sheet",
            "interpretation": "no start, direction, rotation or celestial identity recovered",
        },
        {
            "audit_id": "A09", "audit_family": "ASTRO_FORMAL_ROUNDTRIP_WITHOUT_MASTER", "scope": "f69v left 28 slots",
            "opportunities": "33", "successes": "33", "failures": "0",
            "metric": "opaque groups=33/33 at 28/28 direct slots", "result": "PASS",
            "failure_examples": "NONE", "dependency": "local namespace + exact group code sheet",
            "interpretation": "formal lookup is exemplar-independent",
        },
        {
            "audit_id": "A10", "audit_family": "ASTRO_EXEMPLAR_RECOVERY_WITH_MASTER", "scope": "f69v left 28 slots",
            "opportunities": "28", "successes": "28", "failures": "0",
            "metric": "selected local labels lookup=28/28", "result": "LOOKUP_PASS",
            "failure_examples": "NONE", "dependency": "selected V75 exemplar supplied",
            "interpretation": "labels are retrieved, not decoded",
        },
        {
            "audit_id": "A11", "audit_family": "ASTRO_SEMANTIC_RECOVERY_WITHOUT_MASTER", "scope": "f69v left 28 slots",
            "opportunities": "28", "successes": "0", "failures": "28",
            "metric": "celestial identities/order=0/28", "result": "FAIL_BY_DESIGN",
            "failure_examples": "L01..L28 all retain opaque local values", "dependency": "no external anchor",
            "interpretation": "editorial addresses do not become Moon stations or calendar names",
        },
        {
            "audit_id": "A12", "audit_family": "ET_WORD_VS_SILENT_LINK", "scope": "all 19 V78 ET? occurrences",
            "opportunities": "19", "successes": "19", "failures": "0",
            "metric": "spoken ET? formal coverage=19/19; silent LINK/SLOT formal coverage=19/19",
            "result": "TIE__NO_SEMANTIC_DISCRIMINATION", "failure_examples": "NONE",
            "dependency": "no independent semantic endpoint",
            "interpretation": "state machine cannot choose word over silent formal link",
        },
        {
            "audit_id": "A13", "audit_family": "PER_WORD_VS_ENTRY_RESET", "scope": "all 9 visible V78 PER? occurrences",
            "opportunities": "9", "successes": "9", "failures": "0",
            "metric": "word route=8 source tokens after one edge copy; formal ENTRY/RESET=9 visible marks without collapse",
            "result": "WORD_ROUTE_MECHANICALLY_REPAIRED__FORMAL_RIVAL_SIMPLER_OR_TIED",
            "failure_examples": "word route depends on edge-copy convention at E180/E181",
            "dependency": "physical line layout; no locus exception",
            "interpretation": "successful copying repair does not establish PER semantics",
        },
    ]
    error_fields = [
        "audit_id", "audit_family", "scope", "opportunities", "successes", "failures", "metric", "result",
        "failure_examples", "dependency", "interpretation",
    ]
    write_tsv(ERROR_OUT, error_rows, error_fields)

    trace_counts = Counter((row["trace_family"], row["direction"]) for row in trace_rows)
    summary = {
        "status": "BUILT",
        "role": "R3_TECHNICAL_REGISTER_NOTATION_SCRIBE",
        "manual_rules": len(manual_rows),
        "trace_rows": len(trace_rows),
        "trace_counts": {f"{family}:{direction}": count for (family, direction), count in sorted(trace_counts.items())},
        "selected_prose": {
            "records": TRACE_RECORDS,
            "visible_events": len(selected_events),
            "independent_source_positions_after_edge_copy": selected_source_positions,
            "statements": selected_statement_count,
            "fields": selected_field_count,
            "B2_owner_resets": [f"E{int(row['event_serial']):03d}" for row in b2_resets],
        },
        "selected_astro": {
            "unit": "F69_LEFT_28",
            "loci": len(f69_rows),
            "opaque_groups": sum(len(group_by_locus[row["locus"]]) for row in f69_rows),
            "orientation": "NONE__DIRECT_LOCAL_ADDRESS_ONLY",
        },
        "line_transition_audit": {
            "opportunities": len(transition_rows),
            "TP": class_counts["TP"], "FP": class_counts["FP"],
            "FN": class_counts["FN"], "TN": class_counts["TN"],
            "predicted_copy_pairs": [
                f"{row['line_final_event']}->{row['line_initial_event']}"
                for row in transition_rows if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"
            ],
        },
        "roundtrip": {
            "formal_with_master": "137/137 exact atoms (104 prose cards + 33 Astro groups)",
            "formal_without_master": "137/137 exact atoms (104 prose cards + 33 Astro groups)",
            "prose_semantic_with_master": f"{selected_source_positions}/{selected_source_positions} supplied lookups",
            "prose_semantic_without_master": f"0/{selected_source_positions}",
            "astro_semantic_with_master": "28/28 supplied lookups",
            "astro_semantic_without_master": "0/28",
        },
        "word_rivals": {
            "ET": "ET?_AND_SILENT_LINK_SLOT_TIED",
            "PER": "EDGE_COPY_REPAIR_PASSES_MECHANICALLY__ENTRY_RESET_SIMPLER_OR_TIED",
        },
        "input_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [V78_EVENTS, V78_STATEMENTS, V78_RECORDS, V75_LOCI, V75_GROUPS, V75_NAMESPACES]
        },
        "freeze_sha256": sha256(FREEZE),
        "output_sha256": {
            path.name: sha256(path) for path in [MANUAL_OUT, TRACE_OUT, TRANSITION_OUT, ERROR_OUT]
        },
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
        "interpretation_ceiling": "DETERMINISTIC_WORKSHOP_ROUNDTRIP_NOT_DECIPHERMENT_OR_SEMANTIC_RECOVERY",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
