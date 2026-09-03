#!/usr/bin/env python3
"""Build the GDT770 target-masked valency/orphan tournament."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt770_target_masked_valency_orphan_tournament")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

sys.path.insert(0, str(SRC))
from model import (  # noqa: E402
    EDGE_TYPES,
    TARGET_SURFACES,
    TYPED_FIELD_ROLES,
    TargetContext,
    build_nodes,
    make_target_contexts,
    split_set,
    validate_condition_expression,
    validate_edge_expression,
)
from scoring import (  # noqa: E402
    OccurrenceEvaluation,
    aggregate_evaluations,
    evaluate_occurrence,
)


COHORT_SPECS = SRC / "COHORT_15_LINE_SPECS.tsv"
EXCLUSION_SPECS = SRC / "COHORT_EXCLUSION_LEDGER.tsv"
CANDIDATE_SPECS = SRC / "CANDIDATE_POLICY_SPECS.tsv"
PENALTY_SPECS = SRC / "PENALTY_SPECS.tsv"
WINNER_SPECS = SRC / "WINNER_GATE_SPECS.tsv"
SLOT_CONSTRAINT_SPECS = SRC / "TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv"

OUTPUT_NAMES = (
    "MASKED_COHORT_15_LINE_ATLAS.tsv",
    "TARGET_17_OCCURRENCE_INVENTORY.tsv",
    "NULL_ORPHAN_EDGE_ATLAS.tsv",
    "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv",
    "ATTACHMENT_EDGE_ATLAS.tsv",
    "ORPHAN_DEBT_ATLAS.tsv",
    "PENALTY_EVENT_ATLAS.tsv",
    "TARGET_POLICY_SCOREBOARD.tsv",
    "LEAVE_ONE_PAGE_OUT.tsv",
    "BRANCH_COVERAGE.tsv",
    "WINNER_GATE_AUDIT.tsv",
    "TARGET_DECISIONS.tsv",
    "GDT770_4_WORKING_DICTIONARY.tsv",
    "FIFTEEN_COMPLETE_LINE_READER.tsv",
    "READER_UNIT_CONSUMPTION.tsv",
    "GDT770_CONCRETE_READER.md",
    "RESULT.json",
)

BANNED_RETIRED_LITERAL_FRAGMENTS = ("samen", "saat", "wurzel", "holz", "pulver")
PENALTY_NORMATIVE_FIELDS = (
    "penalty_id",
    "weight",
    "trigger_code",
    "applies_to_policy_classes",
    "scope",
    "per_occurrence_rule",
    "cofire_rule",
    "score_effect",
    "fluency_credit",
)
GATE_NORMATIVE_FIELDS = (
    "gate_id",
    "evaluation_order",
    "applies_to_policy_kind",
    "metric",
    "comparator",
    "threshold",
    "comparator_target",
    "tie_behavior",
    "failure_disposition",
    "pass_disposition",
)
EXPECTED_PENALTY_NORMATIVE_SHA256 = "754f0d718f00eea6491d17c23d1eb9692a62af317258bdafe22cc3a87ad53290"
EXPECTED_GATE_NORMATIVE_SHA256 = "40959bc5c3d517706378193750248e477fa17fb2762a8e6fea72adacab38f96d"


def projection_sha256(
    rows: Sequence[Mapping[str, str]], fields: Sequence[str]
) -> str:
    payload = ["\t".join(fields)]
    payload.extend("\t".join(row[field] for field in fields) for row in rows)
    return hashlib.sha256(("\n".join(payload) + "\n").encode("utf-8")).hexdigest()


def make_status(target_decisions: Sequence[Mapping[str, object]]) -> str:
    """Describe the observed outcome without constraining it in advance."""

    winner_count = sum(
        row["formal_status"] == "PROVISIONAL_POLICY_WIN" for row in target_decisions
    )
    coverage_count = sum(
        row["lead_disposition"] == "INSUFFICIENT_BRANCH_COVERAGE"
        for row in target_decisions
    )
    return (
        "PARTIAL__15_LINES_131_TOKENS_128_SCORE_NODES_127_READER_UNITS__"
        f"17_TARGET_MASKS__{winner_count}_POLICY_WINS__"
        f"{coverage_count}_RAW_LEADS_BRANCH_INSUFFICIENT__"
        "4_CONCRETE_REPLACEABLE_DEFAULTS__"
        "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def json_cell(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialise(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if isinstance(value, (set, frozenset)):
            value = sorted(value)
        return json_cell(value)
    return value


def fields_for(rows: Sequence[Mapping[str, object]]) -> list[str]:
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fields.append(field)
    return fields


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty TSV: {path.name}")
    fields = fields_for(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_source_specs(
    cohort: Sequence[Mapping[str, str]],
    exclusions: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
    penalties: Sequence[Mapping[str, str]],
    gates: Sequence[Mapping[str, str]],
    slot_constraints: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    if len(cohort) != 131:
        raise AssertionError(f"expected 131 cohort tokens, got {len(cohort)}")
    if len({row["cohort_id"] for row in cohort}) != 15:
        raise AssertionError("cohort must contain exactly 15 lines")
    if len(exclusions) != 8:
        raise AssertionError("exclusion ledger must contain exactly eight lines")
    if len(candidates) != 22 or len({row["candidate_id"] for row in candidates}) != 18:
        raise AssertionError("candidate deck must contain 22 branches / 18 candidates")
    if len(penalties) != 6 or len(gates) != 8:
        raise AssertionError("expected six penalty rows and eight winner gates")
    if len(slot_constraints) != 17:
        raise AssertionError("expected one independent slot-constraint row per target")
    slot_header = (
        "cohort_id", "ordinal", "target_mask_id", "predicate_only_close", "provenance",
    )
    if tuple(slot_constraints[0]) != slot_header or any(
        tuple(row) != slot_header for row in slot_constraints
    ):
        raise AssertionError("independent slot-constraint schema changed")
    penalty_header = (
        "penalty_id", "weight", "trigger_code", "applies_to_policy_classes", "scope",
        "per_occurrence_rule", "cofire_rule", "score_effect", "description_de", "fluency_credit",
    )
    gate_header = (
        "gate_id", "evaluation_order", "gate_name", "applies_to_policy_kind", "metric",
        "comparator", "threshold", "comparator_target", "tie_behavior",
        "failure_disposition", "pass_disposition", "description_de",
    )
    if tuple(penalties[0]) != penalty_header or any(tuple(row) != penalty_header for row in penalties):
        raise AssertionError("penalty specification schema changed")
    if tuple(gates[0]) != gate_header or any(tuple(row) != gate_header for row in gates):
        raise AssertionError("winner-gate specification schema changed")
    penalty_contract_sha = projection_sha256(penalties, PENALTY_NORMATIVE_FIELDS)
    gate_contract_sha = projection_sha256(gates, GATE_NORMATIVE_FIELDS)
    if penalty_contract_sha != EXPECTED_PENALTY_NORMATIVE_SHA256:
        raise AssertionError("penalty specification diverged from executable scoring contract")
    if gate_contract_sha != EXPECTED_GATE_NORMATIVE_SHA256:
        raise AssertionError("winner-gate specification diverged from executable gate contract")

    by_line: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
        if row["page"].startswith("f84") or row["locus"].startswith("f84"):
            raise AssertionError("sealed f84 material entered the cohort")
        if row["line_class"] != "MASKED_COHORT_LINE":
            raise AssertionError("semantic line class leaked into masked cohort")
        if Path(row["source_artifact"].split("|")[0]).is_absolute():
            raise AssertionError("absolute source path in cohort")
        if row["default_is_translation"] != "0" or row["confirmed_lexeme"] != "0":
            raise AssertionError("translation or lexeme credit in cohort")
        if row["confirmed_plaintext"] != "0" or row["component_export_credit"] != "0":
            raise AssertionError("plaintext/component credit in cohort")
        if row["is_target"] == "1":
            if row["surface"] not in TARGET_SURFACES or row["reader_exact"] != "1":
                raise AssertionError("target is not one of four exact whole forms")
            if row["target_mask_id"] in {"", "NONE"}:
                raise AssertionError("target without opaque mask")
            if row["scoring_identity"] != row["target_mask_id"]:
                raise AssertionError("target scorer identity must be opaque mask")
            if row["frozen_non_target_default_de"]:
                raise AssertionError("old target default leaked into cohort")
            if row["structural_axes"] != "NONE" or row["structural_roles"] != "NONE":
                raise AssertionError("old target role/axis leaked into cohort")
            credit_fields = (
                "old_target_default_credit",
                "old_target_role_credit",
                "old_target_evidence_credit",
                "old_target_confidence_credit",
            )
            if any(row[field] != "0" for field in credit_fields):
                raise AssertionError("old target evidence received score credit")
        else:
            if row["target_mask_id"] != "NONE" or row["scoring_identity"] != "NON_TARGET":
                raise AssertionError("non-target received target identity")
            lowered = row["frozen_non_target_default_de"].casefold()
            if any(fragment in lowered for fragment in BANNED_RETIRED_LITERAL_FRAGMENTS):
                raise AssertionError(f"retired literal leak at {row['locus']}@{row['ordinal']}")

    score_node_count = 0
    for cohort_id, rows in by_line.items():
        rows = sorted(rows, key=lambda row: int(row["ordinal"]))
        count = int(rows[0]["line_token_count"])
        if len(rows) != count or [int(row["ordinal"]) for row in rows] != list(range(1, count + 1)):
            raise AssertionError(f"non-contiguous cohort line: {cohort_id}")
        if len({row["locus"] for row in rows}) != 1 or len({row["page"] for row in rows}) != 1:
            raise AssertionError(f"mixed source line: {cohort_id}")
        for target in (row for row in rows if row["is_target"] == "1"):
            ordinal = int(target["ordinal"])
            for side, index, exact_field, roles_field in (
                ("left", ordinal - 2, "left_neighbor_exact", "left_neighbor_roles"),
                ("right", ordinal, "right_neighbor_exact", "right_neighbor_roles"),
            ):
                neighbor = rows[index] if 0 <= index < len(rows) else None
                expected_exact = neighbor is not None and neighbor["reader_exact"] == "1"
                if int(target[exact_field]) != int(expected_exact):
                    raise AssertionError(f"{side} exactness mismatch at {cohort_id}:{ordinal}")
                expected_roles = (
                    neighbor["structural_roles"]
                    if expected_exact and neighbor is not None and neighbor["is_target"] == "0"
                    else "NONE"
                )
                if target[roles_field] != expected_roles:
                    raise AssertionError(f"{side} target-facing roles mismatch at {cohort_id}:{ordinal}")
        score_node_count += len(build_nodes(rows))
    if score_node_count != 128:
        raise AssertionError(f"expected 128 score nodes, got {score_node_count}")

    targets = [row for row in cohort if row["is_target"] == "1"]
    target_counts = Counter(row["surface"] for row in targets)
    if target_counts != Counter({"ol": 5, "ckhy": 4, "ols": 3, "otar": 5}):
        raise AssertionError(f"unexpected target counts: {target_counts}")
    if len(targets) != 17:
        raise AssertionError("expected seventeen target masks")
    target_slots = {
        (row["cohort_id"], int(row["ordinal"])): row["target_mask_id"] for row in targets
    }
    constraint_slots = {
        (row["cohort_id"], int(row["ordinal"])): row for row in slot_constraints
    }
    if set(constraint_slots) != set(target_slots):
        raise AssertionError("independent slot constraints do not cover the target cohort exactly")
    for key, row in constraint_slots.items():
        if row["target_mask_id"] != target_slots[key]:
            raise AssertionError(f"slot-constraint mask mismatch at {key}")
        if row["predicate_only_close"] not in {"0", "1"}:
            raise AssertionError(f"invalid predicate-only constraint at {key}")
        if not row["provenance"]:
            raise AssertionError(f"slot constraint lacks independent provenance at {key}")

    span_groups: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        if row["span_id"] != "NONE":
            span_groups[row["span_id"]].append(row)
    if len(span_groups) != 4:
        raise AssertionError("expected four render-once spans")
    for span_id, rows in span_groups.items():
        roles = Counter(row["span_member_role"] for row in rows)
        if len(rows) != 2 or roles["CONSUMED"] != 1 or roles["OWNER"] + roles["MASKED_OWNER"] != 1:
            raise AssertionError(f"malformed render-once span: {span_id}")
        if len({(row["cohort_id"], row["locus"], row["page"]) for row in rows}) != 1:
            raise AssertionError(f"render-once span crosses a source line: {span_id}")
        ordinals = sorted(int(row["ordinal"]) for row in rows)
        if ordinals[1] != ordinals[0] + 1:
            raise AssertionError(f"render-once span is not contiguous: {span_id}")
        if any(row["reader_exact"] != "1" for row in rows):
            raise AssertionError(f"render-once span contains a nonexact member: {span_id}")
        owner = next(row for row in rows if row["span_member_role"] in {"OWNER", "MASKED_OWNER"})
        if any(row["render_once_owner_ordinal"] != owner["ordinal"] for row in rows):
            raise AssertionError(f"owner ordinal mismatch: {span_id}")
        target_members = [row for row in rows if row["is_target"] == "1"]
        if owner["span_member_role"] == "MASKED_OWNER":
            if target_members != [owner]:
                raise AssertionError(f"target-owned span has invalid target membership: {span_id}")
        elif target_members:
            raise AssertionError(f"target-free score span contains a target: {span_id}")
    target_spans = [
        span_id
        for span_id, rows in span_groups.items()
        if any(row["span_member_role"] == "MASKED_OWNER" for row in rows)
    ]
    if len(target_spans) != 1:
        raise AssertionError("expected one target-owned reader-only span")
    practical_units = sum(row["span_member_role"] != "CONSUMED" for row in cohort)
    if practical_units != 127:
        raise AssertionError(f"expected 127 reader units, got {practical_units}")

    target_to_masks: defaultdict[str, set[str]] = defaultdict(set)
    for row in targets:
        target_to_masks[row["surface"]].add(row["target_mask_id"])
    if any(len(mask_ids) != 1 for mask_ids in target_to_masks.values()):
        raise AssertionError("a target surface maps to multiple mask identities")
    if len({next(iter(mask_ids)) for mask_ids in target_to_masks.values()}) != 4:
        raise AssertionError("opaque mask IDs are not one-to-one with target decks")

    if {row["target_surface"] for row in candidates} != TARGET_SURFACES:
        raise AssertionError("candidate deck does not cover exactly four targets")
    allowed_policy_classes = {
        "OPAQUE_NULL", "LINKER", "NOMINAL", "RESULT", "OPERATION", "MEASURE", "ENDPOINT",
    }
    allowed_policy_kinds = {"NULL", "POSITIONAL", "INVARIANT"}
    role_fields = (
        "required_left_classes", "required_right_classes",
        "consumes_left_classes", "consumes_right_classes",
    )
    branches_by_id: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in candidates:
        if row["policy_class"] not in allowed_policy_classes:
            raise AssertionError(f"unknown policy class: {row['policy_class']}")
        if row["policy_kind"] not in allowed_policy_kinds:
            raise AssertionError(f"unknown policy kind: {row['policy_kind']}")
        validate_condition_expression(row["branch_condition"])
        validate_edge_expression(row["required_edge_expression"])
        for field in role_fields:
            unknown = split_set(row[field]) - TYPED_FIELD_ROLES
            if unknown:
                raise AssertionError(f"unknown roles in {field}: {sorted(unknown)}")
        branches_by_id[row["candidate_id"]].append(row)
    for candidate_id, branches in branches_by_id.items():
        priorities = sorted(int(row["branch_priority"]) for row in branches)
        if priorities != list(range(1, len(branches) + 1)):
            raise AssertionError(f"nonconsecutive branch priorities: {candidate_id}")
        ordered = sorted(branches, key=lambda row: int(row["branch_priority"]))
        else_positions = [index for index, row in enumerate(ordered) if row["branch_condition"] == "ELSE"]
        if len(else_positions) > 1 or (else_positions and else_positions != [len(ordered) - 1]):
            raise AssertionError(f"ELSE is not the unique final branch: {candidate_id}")
        if len({row["branch_id"] for row in branches}) != len(branches):
            raise AssertionError(f"duplicate branch ID: {candidate_id}")
    zero_fields = (
        "default_is_translation",
        "eva_latin_credit",
        "substring_export_credit",
        "component_claim_credit",
        "confirmed_lexeme",
        "confirmed_plaintext",
    )
    if any(row[field] != "0" for row in candidates for field in zero_fields):
        raise AssertionError("candidate deck grants prohibited semantic credit")
    if any(row["fluency_credit"] != "0" for row in penalties):
        raise AssertionError("fluency credit entered penalty deck")
    weights = {row["penalty_id"]: int(row["weight"]) for row in penalties}
    if sorted(weights.values(), reverse=True) != [6, 5, 4, 3, 2, 1]:
        raise AssertionError("penalty deck is not fixed +6..+1")
    if [int(row["evaluation_order"]) for row in gates] != list(range(1, 9)):
        raise AssertionError("winner gates are not ordered 1..8")

    return {
        "line_count": len(by_line),
        "token_count": len(cohort),
        "score_node_count": score_node_count,
        "target_count": len(targets),
        "target_counts": dict(sorted(target_counts.items())),
        "reader_exact_token_count": sum(row["reader_exact"] == "1" for row in cohort),
        "nonexact_nontarget_count": sum(row["reader_exact"] == "0" for row in cohort),
        "span_count": len(span_groups),
        "target_owned_reader_span_count": len(target_spans),
        "practical_unit_count": practical_units,
        "candidate_count": len({row["candidate_id"] for row in candidates}),
        "candidate_branch_count": len(candidates),
        "exclusion_count": len(exclusions),
        "predicate_only_close_slot_count": sum(
            row["predicate_only_close"] == "1" for row in slot_constraints
        ),
        "penalty_normative_sha256": penalty_contract_sha,
        "winner_gate_normative_sha256": gate_contract_sha,
    }


def sanitized_branches(rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    """Remove the provenance-only target spelling before scoring."""

    return [{key: value for key, value in row.items() if key != "target_surface"} for row in rows]


def make_masked_atlas(cohort: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in sorted(cohort, key=lambda item: (item["cohort_id"], int(item["ordinal"]))):
        is_target = row["is_target"] == "1"
        output.append(
            {
                "cohort_id": row["cohort_id"],
                "locus": row["locus"],
                "page": row["page"],
                "ordinal": int(row["ordinal"]),
                "masked_surface": f"[{row['target_mask_id']}]" if is_target else row["surface"],
                "is_target": int(is_target),
                "scoring_identity": row["scoring_identity"],
                "reader_exact": int(row["reader_exact"]),
                "scorer_visible_roles": "NONE" if is_target else row["structural_roles"],
                "scorer_visible_axes": "NONE",
                "display_default_de": "[ZIEL VERDECKT]" if is_target else row["frozen_non_target_default_de"],
                "span_id": row["span_id"],
                "span_member_role": row["span_member_role"],
                "render_once_owner_ordinal": row["render_once_owner_ordinal"],
                "target_surface_visible_to_scorer": 0,
                "old_target_default_role_evidence_confidence_credit": 0,
                "fluency_credit": 0,
                "component_export_credit": 0,
            }
        )
    return output


def node_text(node: object | None, field: str) -> object:
    if node is None:
        return "NONE"
    value = getattr(node, field)
    if isinstance(value, (set, frozenset, tuple)):
        return "|".join(str(item) for item in sorted(value)) or "NONE"
    return value


def make_target_inventory(
    contexts: Sequence[TargetContext],
    surface_by_occurrence: Mapping[tuple[str, int], str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for context in contexts:
        rows.append(
            {
                "occurrence_id": context.occurrence_id,
                "cohort_id": context.cohort_id,
                "locus": context.locus,
                "page": context.page,
                "ordinal": context.ordinal,
                "target_mask_id": context.target_mask_id,
                "surface_provenance_only": surface_by_occurrence[(context.cohort_id, context.ordinal)],
                "line_final": int(context.line_final),
                "medial": int(context.medial),
                "left_node_id": node_text(context.left, "node_id"),
                "left_roles": node_text(context.left, "roles"),
                "right_node_id": node_text(context.right, "node_id"),
                "right_roles": node_text(context.right, "roles"),
                "predicate_only_close_independent": int(context.predicate_only_close),
                "null_orphan_count": len(context.null_orphans),
                "null_orphan_types": "|".join(edge_type for _edge, edge_type, _side in context.null_orphans) or "NONE",
                "target_surface_visible_to_scorer": 0,
                "old_target_semantic_credit": 0,
            }
        )
    return rows


def make_null_orphans(contexts: Sequence[TargetContext]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for context in contexts:
        for edge_id, edge_type, side in context.null_orphans:
            neighbor = context.left if side == "LEFT" else context.right if side == "RIGHT" else None
            rows.append(
                {
                    "edge_id": edge_id,
                    "occurrence_id": context.occurrence_id,
                    "cohort_id": context.cohort_id,
                    "locus": context.locus,
                    "page": context.page,
                    "target_mask_id": context.target_mask_id,
                    "target_ordinal": context.ordinal,
                    "side": side,
                    "edge_type": edge_type,
                    "neighbor_node_id": node_text(neighbor, "node_id") if side != "BOTH" else "LEFT_AND_RIGHT",
                    "neighbor_roles": node_text(neighbor, "roles") if side != "BOTH" else "TWO_TYPED_EXACT_SIDES",
                    "null_penalty": 4,
                    "target_derived": 0,
                }
            )
    return rows


def occurrence_row(evaluation: OccurrenceEvaluation) -> dict[str, object]:
    return {
        "candidate_id": evaluation.candidate_id,
        "occurrence_id": evaluation.occurrence_id,
        "cohort_id": evaluation.cohort_id,
        "locus": evaluation.locus,
        "page": evaluation.page,
        "target_mask_id": evaluation.target_mask_id,
        "branch_id": evaluation.branch_id,
        "policy_class": evaluation.policy_class,
        "policy_kind": evaluation.policy_kind,
        "renderer_de_display_only": evaluation.renderer_de,
        "branch_condition_holds": int(evaluation.branch_condition_holds),
        "requirements_hold": int(evaluation.requirements_hold),
        "binding_claim_count": len(evaluation.binding_claims),
        "consumed_sides": "|".join(sorted(evaluation.consumed_sides)) or "NONE",
        "bound_edge_count": len(evaluation.bound_edges),
        "bound_edge_ids": "|".join(edge.edge_id for edge in evaluation.bound_edges) or "NONE",
        "bound_roles": "|".join(edge.role for edge in evaluation.bound_edges) or "NONE",
        "duplicate_edge_count": len(evaluation.duplicate_edges),
        "duplicate_edge_ids": "|".join(edge.edge_id for edge in evaluation.duplicate_edges) or "NONE",
        "resolved_orphan_count": len(evaluation.resolved_orphans),
        "resolved_orphan_ids": "|".join(sorted(evaluation.resolved_orphans)) or "NONE",
        "unresolved_orphan_count": len(evaluation.unresolved_orphans),
        "unresolved_orphan_ids": "|".join(sorted(evaluation.unresolved_orphans)) or "NONE",
        "penalty": evaluation.penalty,
        "penalty_ids": "|".join(event.penalty_id for event in evaluation.penalty_events) or "NONE",
        "trigger_codes": "|".join(event.trigger_code for event in evaluation.penalty_events) or "NONE",
        "fluency_credit": 0,
        "target_surface_credit": 0,
    }


def make_attachment_rows(
    evaluations: Sequence[OccurrenceEvaluation],
) -> list[dict[str, object]]:
    """Expose every ordered binding claim, including failed double claims."""

    rows: list[dict[str, object]] = []
    for evaluation in evaluations:
        if not evaluation.binding_claims:
            rows.append(
                {
                    "candidate_id": evaluation.candidate_id,
                    "occurrence_id": evaluation.occurrence_id,
                    "cohort_id": evaluation.cohort_id,
                    "locus": evaluation.locus,
                    "page": evaluation.page,
                    "target_mask_id": evaluation.target_mask_id,
                    "branch_id": evaluation.branch_id,
                    "claim_index": 0,
                    "binding_stage": "NONE",
                    "source_expression": "NONE",
                    "edge_id": "NONE",
                    "side": "NONE",
                    "neighbor_ordinal": "NONE",
                    "role": "NONE",
                    "bound": 0,
                    "double_consumption": 0,
                    "binding_status": (
                        "NO_CLAIM_REQUIREMENTS_FAILED"
                        if not evaluation.requirements_hold
                        else "NO_BINDING_CLAIM"
                    ),
                    "distance": "NONE",
                    "target_surface_credit": 0,
                }
            )
            continue
        for claim in evaluation.binding_claims:
            edge = claim.edge
            rows.append(
                {
                    "candidate_id": evaluation.candidate_id,
                    "occurrence_id": evaluation.occurrence_id,
                    "cohort_id": evaluation.cohort_id,
                    "locus": evaluation.locus,
                    "page": evaluation.page,
                    "target_mask_id": evaluation.target_mask_id,
                    "branch_id": evaluation.branch_id,
                    "claim_index": claim.claim_index,
                    "binding_stage": claim.binding_stage,
                    "source_expression": claim.source_expression,
                    "edge_id": edge.edge_id,
                    "side": edge.side,
                    "neighbor_ordinal": edge.neighbor_ordinal,
                    "role": edge.role,
                    "bound": int(claim.bound),
                    "double_consumption": int(claim.double_consumption),
                    "binding_status": "DOUBLE_CLAIM" if claim.double_consumption else "BOUND",
                    "distance": 1,
                    "target_surface_credit": 0,
                }
            )
    return rows


def make_orphan_debt_rows(
    evaluations: Sequence[OccurrenceEvaluation], contexts: Mapping[str, TargetContext]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for evaluation in evaluations:
        context = contexts[evaluation.occurrence_id]
        penalty_by_edge = {
            event.edge_id: event
            for event in evaluation.penalty_events
            if event.penalty_id == "P04_ORPHAN_OR_SOURCELESS_RESULT" and event.edge_id != "NONE"
        }
        for edge_id, edge_type, side in context.null_orphans:
            resolved = edge_id in evaluation.resolved_orphans
            rows.append(
                {
                    "candidate_id": evaluation.candidate_id,
                    "occurrence_id": evaluation.occurrence_id,
                    "cohort_id": evaluation.cohort_id,
                    "locus": evaluation.locus,
                    "page": evaluation.page,
                    "target_mask_id": evaluation.target_mask_id,
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "side": side,
                    "under_null": "OPEN",
                    "candidate_status": "RESOLVED" if resolved else "OPEN",
                    "penalty_id": "NONE" if resolved else penalty_by_edge[edge_id].penalty_id,
                    "penalty": 0 if resolved else penalty_by_edge[edge_id].weight,
                    "candidate_created_edge": 0,
                }
            )
    return rows


def make_penalty_event_rows(evaluations: Sequence[OccurrenceEvaluation]) -> list[dict[str, object]]:
    return [
        {
            "candidate_id": evaluation.candidate_id,
            "occurrence_id": evaluation.occurrence_id,
            "cohort_id": evaluation.cohort_id,
            "locus": evaluation.locus,
            "page": evaluation.page,
            "target_mask_id": evaluation.target_mask_id,
            "event_index": index,
            "penalty_id": event.penalty_id,
            "trigger_code": event.trigger_code,
            "edge_id": event.edge_id,
            "weight": event.weight,
            "note": event.note,
        }
        for evaluation in evaluations
        for index, event in enumerate(evaluation.penalty_events, start=1)
    ]


def compute_leave_one_page_out(
    target_candidates: Mapping[str, Sequence[str]],
    evaluations_by_candidate: Mapping[str, Sequence[OccurrenceEvaluation]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    min_margins: dict[str, int] = {}
    for mask_id in sorted(target_candidates):
        candidate_ids = list(target_candidates[mask_id])
        pages = sorted({evaluation.page for cid in candidate_ids for evaluation in evaluations_by_candidate[cid]})
        null_id = next(cid for cid in candidate_ids if cid.endswith("_NULL"))
        per_candidate_margins: defaultdict[str, list[int]] = defaultdict(list)
        for page in pages:
            fold_scores = {
                cid: sum(evaluation.penalty for evaluation in evaluations_by_candidate[cid] if evaluation.page != page)
                for cid in candidate_ids
            }
            minimum = min(fold_scores.values())
            minimum_ids = sorted(cid for cid, score in fold_scores.items() if score == minimum)
            for cid in candidate_ids:
                rivals = {rid: score for rid, score in fold_scores.items() if rid != cid}
                best_rival_score = min(rivals.values())
                best_rival_ids = sorted(rid for rid, score in rivals.items() if score == best_rival_score)
                margin = best_rival_score - fold_scores[cid]
                per_candidate_margins[cid].append(margin)
                rows.append(
                    {
                        "target_mask_id": mask_id,
                        "held_page": page,
                        "candidate_id": cid,
                        "fold_penalty": fold_scores[cid],
                        "null_candidate_id": null_id,
                        "null_fold_penalty": fold_scores[null_id],
                        "delta_vs_null": fold_scores[null_id] - fold_scores[cid],
                        "best_rival_ids": "|".join(best_rival_ids),
                        "best_rival_penalty": best_rival_score,
                        "strict_pairwise_margin": margin,
                        "fold_minimum_ids": "|".join(minimum_ids),
                        "unique_fold_winner": int(minimum_ids == [cid]),
                    }
                )
        min_margins.update({cid: min(margins) for cid, margins in per_candidate_margins.items()})
    return rows, min_margins


def make_branch_coverage(
    target_candidates: Mapping[str, Sequence[str]],
    contexts_by_mask: Mapping[str, Sequence[TargetContext]],
    evaluations_by_candidate: Mapping[str, Sequence[OccurrenceEvaluation]],
    branches_by_candidate: Mapping[str, Sequence[Mapping[str, str]]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mask_id in sorted(target_candidates):
        for candidate_id in target_candidates[mask_id]:
            eval_map = {evaluation.occurrence_id: evaluation for evaluation in evaluations_by_candidate[candidate_id]}
            for branch in sorted(
                branches_by_candidate[candidate_id],
                key=lambda row: (int(row["branch_priority"]), row["branch_id"]),
            ):
                selected = [
                    eval_map[context.occurrence_id]
                    for context in contexts_by_mask[mask_id]
                    if eval_map[context.occurrence_id].branch_id == branch["branch_id"]
                ]
                qualified = [evaluation for evaluation in selected if evaluation.requirements_hold]
                minimum = int(branch["minimum_branch_pages"])
                pages = sorted({evaluation.page for evaluation in qualified})
                rows.append(
                    {
                        "target_mask_id": mask_id,
                        "candidate_id": candidate_id,
                        "policy_kind": branch["policy_kind"],
                        "policy_class": branch["policy_class"],
                        "branch_id": branch["branch_id"],
                        "branch_priority": int(branch["branch_priority"]),
                        "branch_condition": branch["branch_condition"],
                        "selected_occurrence_count": len(selected),
                        "qualified_occurrence_count": len(qualified),
                        "qualified_page_count": len(pages),
                        "qualified_pages": "|".join(pages) or "NONE",
                        "minimum_branch_pages": minimum,
                        "coverage_pass": int(minimum == 0 or len(pages) >= minimum),
                    }
                )
    return rows


def evaluate_gates(
    target_candidates: Mapping[str, Sequence[str]],
    aggregates: Mapping[str, Mapping[str, object]],
    min_loo_margins: Mapping[str, int],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]], list[dict[str, object]]]:
    gate_rows: list[dict[str, object]] = []
    candidate_metrics: dict[str, dict[str, object]] = {}
    target_decisions: list[dict[str, object]] = []
    for mask_id in sorted(target_candidates):
        candidate_ids = list(target_candidates[mask_id])
        scores = {cid: int(aggregates[cid]["total_penalty"]) for cid in candidate_ids}
        null_id = next(cid for cid in candidate_ids if cid.endswith("_NULL"))
        minimum = min(scores.values())
        minimum_ids = sorted(cid for cid, score in scores.items() if score == minimum)
        nonnull = [cid for cid in candidate_ids if cid != null_id]
        invariant = [cid for cid in nonnull if aggregates[cid]["policy_kind"] == "INVARIANT"]
        for cid in candidate_ids:
            rivals = {rid: score for rid, score in scores.items() if rid != cid}
            min_rival_margin = min(score - scores[cid] for score in rivals.values())
            coverage_records = aggregates[cid]["required_branch_coverage"]
            coverage_pass = all(
                int(record["observed"]) >= int(record["minimum"])
                for record in coverage_records.values()
            )
            position_margin: int | None = None
            if aggregates[cid]["policy_kind"] == "POSITIONAL":
                position_margin = min(scores[rid] for rid in invariant) - scores[cid]
            checks = {
                "G01_BRANCH_PAGE_COVERAGE": coverage_pass,
                "G02_NULL_MARGIN": scores[null_id] - scores[cid] >= 4,
                "G03_EVERY_RIVAL_MARGIN": min_rival_margin >= 4,
                "G04_ORPHANS_REMOVED": int(aggregates[cid]["resolved_null_orphan_count"]) >= 2,
                "G05_ORPHAN_PAGES": int(aggregates[cid]["resolved_orphan_page_count"]) >= 2,
                "G06_POSITIONAL_BEATS_INVARIANT": position_margin is None or position_margin >= 4,
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": min_loo_margins[cid] > 0,
                "G08_EXACT_TIE_TO_NULL": minimum_ids == [cid],
            }
            is_nonnull = cid != null_id
            base_applicable = {
                "G01_BRANCH_PAGE_COVERAGE": is_nonnull and bool(coverage_records),
                "G02_NULL_MARGIN": is_nonnull,
                "G03_EVERY_RIVAL_MARGIN": is_nonnull,
                "G04_ORPHANS_REMOVED": is_nonnull,
                "G05_ORPHAN_PAGES": is_nonnull,
                "G06_POSITIONAL_BEATS_INVARIANT": is_nonnull and position_margin is not None,
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": is_nonnull,
            }
            survives_first_seven = is_nonnull and all(
                checks[gate_id]
                for gate_id, gate_applies in base_applicable.items()
                if gate_applies
            )
            gate_applicable = {
                **base_applicable,
                # G08 is normally reached by a gates-1--7 survivor.  A tied
                # full minimum is the one exception: expose its explicit tie
                # failure even though G03 has already rejected its margin.
                "G08_EXACT_TIE_TO_NULL": survives_first_seven
                or (is_nonnull and cid in minimum_ids and len(minimum_ids) > 1),
            }
            failed = [
                gate_id
                for gate_id, passed in checks.items()
                if gate_applicable[gate_id] and not passed
            ]
            candidate_metrics[cid] = {
                "null_candidate_id": null_id,
                "null_penalty": scores[null_id],
                "delta_vs_null": scores[null_id] - scores[cid],
                "min_rival_margin": min_rival_margin,
                "position_margin": position_margin,
                "min_loo_margin": min_loo_margins[cid],
                "raw_minimum": minimum,
                "raw_minimum_ids": tuple(minimum_ids),
                "coverage_pass": coverage_pass,
                "failed_gate_ids": tuple(failed),
                "eligible": bool(survives_first_seven and checks["G08_EXACT_TIE_TO_NULL"]),
            }
            observed = {
                "G01_BRANCH_PAGE_COVERAGE": min(
                    (int(record["observed"]) for record in coverage_records.values()),
                    default=0,
                ),
                "G02_NULL_MARGIN": scores[null_id] - scores[cid],
                "G03_EVERY_RIVAL_MARGIN": min_rival_margin,
                "G04_ORPHANS_REMOVED": int(aggregates[cid]["resolved_null_orphan_count"]),
                "G05_ORPHAN_PAGES": int(aggregates[cid]["resolved_orphan_page_count"]),
                "G06_POSITIONAL_BEATS_INVARIANT": position_margin if position_margin is not None else "NA",
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": min_loo_margins[cid],
                "G08_EXACT_TIE_TO_NULL": len(minimum_ids) if cid in minimum_ids else "NOT_AT_MINIMUM",
            }
            for order, gate_id in enumerate(checks, start=1):
                applies = gate_applicable[gate_id]
                gate_rows.append(
                    {
                        "target_mask_id": mask_id,
                        "candidate_id": cid,
                        "gate_id": gate_id,
                        "evaluation_order": order,
                        "applicable": int(applies),
                        "observed": observed[gate_id],
                        "pass": int(checks[gate_id]) if applies else "NA",
                        "candidate_disposition": (
                            "OPAQUE_BASELINE" if not is_nonnull else "NOT_APPLICABLE_OR_NOT_REACHED" if not applies
                            else "PROVISIONAL_POLICY_WIN" if gate_id == "G08_EXACT_TIE_TO_NULL" and checks[gate_id]
                            else "CONTINUE" if checks[gate_id]
                            else "INSUFFICIENT_BRANCH_COVERAGE" if gate_id == "G01_BRANCH_PAGE_COVERAGE"
                            else "OPAQUE_NULL"
                        ),
                    }
                )
        winners = [cid for cid in nonnull if candidate_metrics[cid]["eligible"]]
        if len(winners) > 1:
            raise AssertionError(f"multiple gated winners for {mask_id}: {winners}")
        raw_lead = minimum_ids[0] if len(minimum_ids) == 1 else "TIE"
        formal = winners[0] if winners else null_id
        if raw_lead != "TIE":
            failed = candidate_metrics[raw_lead]["failed_gate_ids"]
        else:
            failed = tuple(
                dict.fromkeys(
                    gate_id
                    for candidate_id in minimum_ids
                    if candidate_id != null_id
                    for gate_id in candidate_metrics[candidate_id]["failed_gate_ids"]
                )
            ) or ("G08_EXACT_TIE_TO_NULL",)
        target_decisions.append(
            {
                "target_mask_id": mask_id,
                "formal_decision": formal,
                "formal_status": "PROVISIONAL_POLICY_WIN" if winners else "OPAQUE_NULL",
                "raw_lead_candidate": raw_lead,
                "raw_minimum_candidates": "|".join(minimum_ids),
                "raw_lead_penalty": minimum,
                "null_candidate": null_id,
                "null_penalty": scores[null_id],
                "raw_lead_delta_vs_null": scores[null_id] - scores[raw_lead] if raw_lead != "TIE" else "NA",
                "raw_lead_failed_gates": "|".join(failed),
                "lead_disposition": (
                    "INSUFFICIENT_BRANCH_COVERAGE" if "G01_BRANCH_PAGE_COVERAGE" in failed else "OPAQUE_NULL"
                ),
                "policy_winner_count": len(winners),
            }
        )
    return gate_rows, candidate_metrics, target_decisions


def policy_scoreboard_rows(
    aggregates: Mapping[str, Mapping[str, object]],
    metrics: Mapping[str, Mapping[str, object]],
    target_mask_by_candidate: Mapping[str, str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cid in sorted(aggregates, key=lambda item: (target_mask_by_candidate[item], int(aggregates[item]["total_penalty"]), item)):
        aggregate = aggregates[cid]
        metric = metrics[cid]
        rows.append(
            {
                "target_mask_id": target_mask_by_candidate[cid],
                "candidate_id": cid,
                "policy_kind": aggregate["policy_kind"],
                "policy_classes": "|".join(aggregate["policy_classes"]),
                "target_occurrence_count": aggregate["target_occurrence_count"],
                "target_page_count": aggregate["target_page_count"],
                "total_penalty": aggregate["total_penalty"],
                "null_penalty": metric["null_penalty"],
                "delta_vs_null": metric["delta_vs_null"],
                "min_pairwise_rival_margin": metric["min_rival_margin"],
                "resolved_null_orphan_count": aggregate["resolved_null_orphan_count"],
                "resolved_orphan_page_count": aggregate["resolved_orphan_page_count"],
                "minimum_leave_one_page_out_margin": metric["min_loo_margin"],
                "position_margin_over_best_invariant": metric["position_margin"] if metric["position_margin"] is not None else "NA",
                "branch_coverage_pass": int(metric["coverage_pass"]),
                "failed_gate_ids": "|".join(metric["failed_gate_ids"]) or "NONE",
                "eligible_policy_winner": int(metric["eligible"]),
                "penalty_counts": aggregate["penalty_counts"],
                "trigger_counts": aggregate["trigger_counts"],
                "fluency_credit": 0,
                "confirmed_lexeme": 0,
            }
        )
    return rows


def choose_local_displays(
    target_decisions: Sequence[Mapping[str, object]],
    evaluations_by_candidate: Mapping[str, Sequence[OccurrenceEvaluation]],
    candidate_order: Mapping[str, int],
) -> dict[str, tuple[OccurrenceEvaluation, ...]]:
    """Retain every tied local minimum; source order never breaks a tie."""

    del target_decisions, candidate_order
    by_occurrence: defaultdict[str, list[OccurrenceEvaluation]] = defaultdict(list)
    for candidate_id, evaluations in evaluations_by_candidate.items():
        if candidate_id.endswith("_NULL"):
            continue
        for evaluation in evaluations:
            by_occurrence[evaluation.occurrence_id].append(evaluation)
    selected: dict[str, tuple[OccurrenceEvaluation, ...]] = {}
    for occurrence_id, evaluations in by_occurrence.items():
        legal = [e for e in evaluations if e.branch_condition_holds and e.requirements_hold]
        pool = legal or [e for e in evaluations if e.branch_condition_holds]
        if not pool:
            raise AssertionError(f"no concrete display for {occurrence_id}")
        minimum = min(e.penalty for e in pool)
        selected[occurrence_id] = tuple(
            sorted(
                (e for e in pool if e.penalty == minimum),
                key=lambda e: e.candidate_id,
            )
        )
    return selected


def editorial_target_realization(
    evaluations: Sequence[OccurrenceEvaluation], context: TargetContext
) -> tuple[str, str, str]:
    """Make a concrete German reader label without changing any score."""

    def one(evaluation: OccurrenceEvaluation) -> tuple[str, str]:
        renderer = evaluation.renderer_de
        if renderer == "Fertigprodukt/Colatura":
            return "fertige Zubereitung", "COLATURA_NOT_LOCALLY_IDENTIFIED"
        if renderer == "Übergangs-/Zubereitungsfeld":
            return "Zwischenzubereitung", "CONCRETE_NOMINAL_REALIZATION"
        if renderer == "weiter/dann":
            return "dann", "CONCRETE_SEQUENCE_REALIZATION"
        if renderer == "Ansatz/Basis":
            return "Grundansatz", "CONCRETE_NOMINAL_REALIZATION"
        if renderer == "Infusion/Dekokt":
            return "Aufguss oder Abkochung", "LEXICAL_ALTERNATIVE_RETAINED"
        if renderer == "Maß/Dosis":
            return "Dosis", "CONCRETE_MEASURE_REALIZATION"
        if renderer == "messbares Produkt/Resultat":
            return "abgemessene Zubereitung", "CONCRETE_RESULT_REALIZATION"
        if renderer == "von/aus":
            return "aus", "CONCRETE_RELATOR_REALIZATION"
        if renderer == "und/mit":
            if context.right is not None and context.right.roles & {"AMOUNT", "VALUE"}:
                return "mit", "RELATOR_BY_RIGHT_QUANTITY"
            return "und", "RELATOR_BY_NONQUANTITY_NEIGHBOURS"
        return renderer, "POLICY_RENDERER_UNCHANGED"

    realizations = [one(evaluation) for evaluation in evaluations]
    unique_texts = list(dict.fromkeys(text for text, _rule in realizations))
    unique_rules = list(dict.fromkeys(rule for _text, rule in realizations))
    side_counts = [
        len({edge.side for edge in evaluation.bound_edges}) for evaluation in evaluations
    ]
    conservative_side_count = min(side_counts)
    support_grade = (
        "A" if conservative_side_count == 2 else "B" if conservative_side_count == 1 else "C"
    )
    ambiguous = len(evaluations) > 1 or len(unique_texts) > 1
    text = " oder ".join(unique_texts)
    if ambiguous or support_grade == "C":
        text = f"[{text}?]"
    return text, support_grade, "|".join(unique_rules)


def join_reader_units(units: Sequence[str]) -> str:
    """Join field-like units without manufacturing doubled punctuation."""

    cleaned = [unit.strip().lstrip(";").strip() for unit in units]
    text = ""
    for unit in cleaned:
        if not text:
            text = unit
        elif text.endswith(":"):
            text += f" {unit}"
        else:
            text += f"; {unit}"
    return text.rstrip(". ") + "."


def target_surface_maps(
    cohort: Sequence[Mapping[str, str]], candidates: Sequence[Mapping[str, str]]
) -> tuple[dict[str, str], dict[str, str], dict[tuple[str, int], str]]:
    mask_by_surface: dict[str, str] = {}
    surface_by_mask: dict[str, str] = {}
    surface_by_occurrence: dict[tuple[str, int], str] = {}
    for row in cohort:
        if row["is_target"] != "1":
            continue
        surface, mask = row["surface"], row["target_mask_id"]
        if surface in mask_by_surface and mask_by_surface[surface] != mask:
            raise AssertionError("surface-to-mask mapping changed within cohort")
        if mask in surface_by_mask and surface_by_mask[mask] != surface:
            raise AssertionError("opaque mask maps to multiple target surfaces")
        mask_by_surface[surface] = mask
        surface_by_mask[mask] = surface
        surface_by_occurrence[(row["cohort_id"], int(row["ordinal"]))] = surface
    if set(mask_by_surface) != {row["target_surface"] for row in candidates}:
        raise AssertionError("candidate and cohort target surfaces differ")
    return mask_by_surface, surface_by_mask, surface_by_occurrence


def make_dictionary(
    target_decisions: Sequence[Mapping[str, object]],
    surface_by_mask: Mapping[str, str],
    aggregates: Mapping[str, Mapping[str, object]],
    metrics: Mapping[str, Mapping[str, object]],
    branches_by_candidate: Mapping[str, Sequence[Mapping[str, str]]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for decision in sorted(target_decisions, key=lambda row: surface_by_mask[str(row["target_mask_id"])]):
        mask = str(decision["target_mask_id"])
        surface = surface_by_mask[mask]
        lead = str(decision["raw_lead_candidate"])
        tied_ids = str(decision["raw_minimum_candidates"]).split("|")
        policy_ids = tied_ids if lead == "TIE" else [lead]
        display_policy_ids = [candidate_id for candidate_id in policy_ids if not candidate_id.endswith("_NULL")]
        if not display_policy_ids:
            display_policy_ids = policy_ids
        renderers: list[str] = []
        tags: list[str] = []
        for candidate_id in display_policy_ids:
            for branch in sorted(
                branches_by_candidate[candidate_id], key=lambda row: int(row["branch_priority"])
            ):
                if branch["renderer_de"] not in renderers:
                    renderers.append(branch["renderer_de"])
                if branch["structural_tag"] not in tags:
                    tags.append(branch["structural_tag"])
        if lead == "TIE":
            score = int(decision["raw_lead_penalty"])
            null_penalty = int(decision["null_penalty"])
            delta = null_penalty - score
            resolved_count = max(int(aggregates[cid]["resolved_null_orphan_count"]) for cid in policy_ids)
            resolved_pages = max(int(aggregates[cid]["resolved_orphan_page_count"]) for cid in policy_ids)
            failed = tuple(
                gate_id
                for gate_id in str(decision["raw_lead_failed_gates"]).split("|")
                if gate_id
            )
            min_loo = min(int(metrics[cid]["min_loo_margin"]) for cid in policy_ids)
            exploratory = False
        else:
            aggregate, metric = aggregates[lead], metrics[lead]
            score = int(aggregate["total_penalty"])
            null_penalty = int(metric["null_penalty"])
            delta = int(metric["delta_vs_null"])
            resolved_count = int(aggregate["resolved_null_orphan_count"])
            resolved_pages = int(aggregate["resolved_orphan_page_count"])
            failed = tuple(metric["failed_gate_ids"])
            min_loo = int(metric["min_loo_margin"])
            exploratory = int(metric["min_rival_margin"]) >= 4 and resolved_pages >= 2
        confidence = (
            "C1_PROVISIONAL_POLICY__C0_LEXEME"
            if decision["formal_status"] == "PROVISIONAL_POLICY_WIN"
            else "C0_FORMAL__C1_EXPLORATORY_STRUCTURAL_LEAD__C0_LEXEME"
            if exploratory
            else "C0_FORMAL__C0_CLOSE_OR_UNSTABLE_LEAD__C0_LEXEME"
        )
        concrete_reader_defaults = {
            "ckhy": "mischen",
            "ol": "unbelegter linker Mengenzweig [aus?]; vor einer Mengenangabe mit; sonst und",
            "ols": "fertige Zubereitung",
            "otar": "Zwischenzubereitung (knapper Rivale: dann)",
        }
        rows.append(
            {
                "surface": surface,
                "target_mask_id": mask,
                "formal_target_default": "OPAQUE_NULL",
                "best_replaceable_policy": "|".join(policy_ids),
                "structural_tags": "|".join(tags),
                "policy_renderer_de": "; sonst ".join(renderers),
                "concrete_default_de": concrete_reader_defaults[surface],
                "confidence": confidence,
                "formal_policy_confidence": (
                    "C1_PROVISIONAL" if decision["formal_status"] == "PROVISIONAL_POLICY_WIN" else "C0"
                ),
                "lexeme_confidence": "C0",
                "evidence": (
                    f"Strafe {score} gegen NULL {null_penalty}; Delta {delta}; "
                    f"bis zu {resolved_count} Nullwaisen auf {resolved_pages} Seiten gebunden."
                ),
                "counterevidence": (
                    f"{'Provisorischer Policy-Gewinn' if decision['formal_status'] == 'PROVISIONAL_POLICY_WIN' else 'Kein formaler Policy-Gewinn'}; "
                    f"gescheiterte Gates: {'|'.join(failed) or 'NONE'}; "
                    f"schlechteste Leave-one-page-out-Marge {min_loo}."
                ),
                "scope": "GDT770_15_LINE_COHORT__WHOLE_FORM_OCCURRENCE_ONLY",
                "replaceable": 1,
                "default_is_translation": 0,
                "confirmed_lexeme": 0,
                "confirmed_plaintext": 0,
                "substring_export_credit": 0,
                "component_export_credit": 0,
            }
        )
    return rows


def make_reader(
    cohort: Sequence[Mapping[str, str]],
    contexts: Sequence[TargetContext],
    local_displays: Mapping[str, Sequence[OccurrenceEvaluation]],
    surface_by_mask: Mapping[str, str],
    target_decisions: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    context_by_key = {(context.cohort_id, context.ordinal): context for context in contexts}
    decision_by_mask = {str(row["target_mask_id"]): row for row in target_decisions}
    by_line: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
    output: list[dict[str, object]] = []
    consumption: list[dict[str, object]] = []
    markdown = [
        "# GDT770 concrete replaceable reader",
        "",
        "This exploratory reader retains every tied lowest-penalty legal local display from the fixed candidate decks. "
        "It is a post-score working renderer, not a recovered plaintext or a target-wide policy. "
        "Support A means two bound sides, B one side, and C no positive local binding; C and ties are visibly bracketed.",
        "",
    ]
    token_total = 0
    unit_total = 0
    for cohort_id in sorted(by_line):
        rows = sorted(by_line[cohort_id], key=lambda row: int(row["ordinal"]))
        tokens = [row["surface"] for row in rows]
        masked_tokens = [f"[{row['target_mask_id']}]" if row["is_target"] == "1" else row["surface"] for row in rows]
        units: list[str] = []
        dispatches: list[str] = []
        consumed_ordinals: set[int] = set()
        covered_ordinals: list[int] = []
        for row in rows:
            ordinal = int(row["ordinal"])
            if row["span_member_role"] == "CONSUMED":
                consumed_ordinals.add(ordinal)
                continue
            if row["span_id"] != "NONE":
                member_rows = sorted(
                    (item for item in rows if item["span_id"] == row["span_id"]),
                    key=lambda item: int(item["ordinal"]),
                )
            else:
                member_rows = [row]
            member_ordinals = [int(item["ordinal"]) for item in member_rows]
            member_surfaces = [item["surface"] for item in member_rows]
            target_occurrence_id = "NONE"
            policy_ids = "NONE"
            support_grade = "NA"
            editorial_rule = "FROZEN_NON_TARGET_DEFAULT"
            if row["is_target"] == "1":
                context = context_by_key[(cohort_id, ordinal)]
                evaluations = local_displays[context.occurrence_id]
                text, support_grade, editorial_rule = editorial_target_realization(
                    evaluations, context
                )
                if row["span_member_role"] == "MASKED_OWNER":
                    member = next(
                        item for item in rows
                        if item["span_id"] == row["span_id"] and item["span_member_role"] == "CONSUMED"
                    )
                    text = f"{text}, {member['frozen_non_target_default_de']}"
                units.append(text)
                raw_lead = str(decision_by_mask[context.target_mask_id]["raw_lead_candidate"])
                candidate_ids = [evaluation.candidate_id for evaluation in evaluations]
                policy_ids = "|".join(candidate_ids)
                target_occurrence_id = context.occurrence_id
                mode = (
                    "RAW_LEAD_LOCAL_MINIMUM"
                    if candidate_ids == [raw_lead]
                    else "TIED_LOCAL_MINIMUM"
                    if len(candidate_ids) > 1
                    else "LOCAL_LEGAL_FALLBACK"
                )
                dispatches.append(
                    f"{ordinal}:{surface_by_mask[context.target_mask_id]}={text}"
                    f"<{policy_ids}:{mode}:support-{support_grade}>"
                )
            else:
                text = row["frozen_non_target_default_de"]
                if not text or text == "NONE":
                    raise AssertionError(f"non-target without concrete display: {cohort_id}@{ordinal}")
                units.append(text)
            unit_index = len(units)
            covered_ordinals.extend(member_ordinals)
            consumption.append(
                {
                    "unit_id": f"{cohort_id}:U{unit_index:02d}",
                    "cohort_id": cohort_id,
                    "locus": rows[0]["locus"],
                    "page": rows[0]["page"],
                    "unit_index": unit_index,
                    "owner_ordinal": ordinal,
                    "source_member_ordinals": "|".join(map(str, member_ordinals)),
                    "source_member_surfaces": "|".join(member_surfaces),
                    "member_count": len(member_ordinals),
                    "unit_kind": "TARGET" if row["is_target"] == "1" else "NON_TARGET",
                    "target_occurrence_id": target_occurrence_id,
                    "local_policy_ids": policy_ids,
                    "support_grade": support_grade,
                    "editorial_rule": editorial_rule,
                    "reader_text_de": text,
                    "score_credit": 0,
                }
            )
        if len(units) != len(rows) - len(consumed_ordinals):
            raise AssertionError(f"render-once coverage failure: {cohort_id}")
        if sorted(covered_ordinals) != list(range(1, len(rows) + 1)):
            raise AssertionError(f"reader unit membership is not exact at {cohort_id}")
        if len(covered_ordinals) != len(set(covered_ordinals)):
            raise AssertionError(f"reader unit membership overlaps at {cohort_id}")
        token_total += len(rows)
        unit_total += len(units)
        reader = join_reader_units(units)
        output.append(
            {
                "cohort_id": cohort_id,
                "locus": rows[0]["locus"],
                "page": rows[0]["page"],
                "token_count": len(rows),
                "practical_unit_count": len(units),
                "manuscript_line": " ".join(tokens),
                "simultaneously_masked_line": " ".join(masked_tokens),
                "target_count": sum(row["is_target"] == "1" for row in rows),
                "target_dispatches": " | ".join(dispatches),
                "practical_units_de": " | ".join(units),
                "concrete_working_reader_de": reader,
                "every_token_consumed_once": 1,
                "formal_translation_claim": 0,
            }
        )
        markdown.extend(
            [
                f"## {rows[0]['locus']}",
                "",
                f"- Manuscript line: `{' '.join(tokens)}`",
                f"- Masked line: `{' '.join(masked_tokens)}`",
                f"- Working reader: {reader}",
                f"- Target dispatch: {'; '.join(dispatches)}",
                "",
            ]
        )
    if token_total != 131 or unit_total != 127:
        raise AssertionError(f"reader totals changed: {token_total} tokens / {unit_total} units")
    if len(consumption) != 127 or sum(int(row["member_count"]) for row in consumption) != 131:
        raise AssertionError("global reader-consumption totals changed")
    return output, consumption, "\n".join(markdown).rstrip() + "\n"


def build(artifacts: Path) -> dict[str, object]:
    cohort = read_tsv(COHORT_SPECS)
    exclusions = read_tsv(EXCLUSION_SPECS)
    candidates = read_tsv(CANDIDATE_SPECS)
    penalties = read_tsv(PENALTY_SPECS)
    gates = read_tsv(WINNER_SPECS)
    slot_constraints = read_tsv(SLOT_CONSTRAINT_SPECS)
    counts = validate_source_specs(
        cohort, exclusions, candidates, penalties, gates, slot_constraints
    )

    mask_by_surface, surface_by_mask, surface_by_occurrence = target_surface_maps(cohort, candidates)
    predicate_only_close_by_slot = {
        (row["cohort_id"], int(row["ordinal"])): row["predicate_only_close"] == "1"
        for row in slot_constraints
    }
    contexts = list(make_target_contexts(cohort, predicate_only_close_by_slot))
    if len(contexts) != 17:
        raise AssertionError("context builder did not return seventeen targets")
    context_by_id = {context.occurrence_id: context for context in contexts}
    if len(context_by_id) != len(contexts):
        raise AssertionError("duplicate occurrence IDs")
    contexts_by_mask: defaultdict[str, list[TargetContext]] = defaultdict(list)
    for context in contexts:
        contexts_by_mask[context.target_mask_id].append(context)

    source_branches: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    candidate_surface: dict[str, str] = {}
    candidate_order: dict[str, int] = {}
    for index, row in enumerate(candidates):
        source_branches[row["candidate_id"]].append(row)
        candidate_surface[row["candidate_id"]] = row["target_surface"]
        candidate_order.setdefault(row["candidate_id"], index)
    branches_by_candidate = {cid: sanitized_branches(rows) for cid, rows in source_branches.items()}
    target_mask_by_candidate = {cid: mask_by_surface[surface] for cid, surface in candidate_surface.items()}
    target_candidates: defaultdict[str, list[str]] = defaultdict(list)
    for cid in sorted(branches_by_candidate, key=lambda item: candidate_order[item]):
        target_candidates[target_mask_by_candidate[cid]].append(cid)

    penalty_weights = {row["penalty_id"]: int(row["weight"]) for row in penalties}
    evaluations_by_candidate: dict[str, list[OccurrenceEvaluation]] = {}
    aggregates: dict[str, dict[str, object]] = {}
    all_evaluations: list[OccurrenceEvaluation] = []
    for candidate_id in sorted(branches_by_candidate, key=lambda item: candidate_order[item]):
        mask_id = target_mask_by_candidate[candidate_id]
        evaluations = [
            evaluate_occurrence(candidate_id, branches_by_candidate[candidate_id], context, penalty_weights)
            for context in sorted(contexts_by_mask[mask_id], key=lambda item: (item.page, item.locus, item.ordinal))
        ]
        evaluations_by_candidate[candidate_id] = evaluations
        all_evaluations.extend(evaluations)
        aggregates[candidate_id] = aggregate_evaluations(candidate_id, evaluations, branches_by_candidate[candidate_id])

    loo_rows, min_loo_margins = compute_leave_one_page_out(target_candidates, evaluations_by_candidate)
    branch_rows = make_branch_coverage(
        target_candidates, contexts_by_mask, evaluations_by_candidate, branches_by_candidate
    )
    gate_rows, metrics, target_decisions = evaluate_gates(target_candidates, aggregates, min_loo_margins)
    policy_rows = policy_scoreboard_rows(aggregates, metrics, target_mask_by_candidate)

    decision_by_surface = {surface_by_mask[str(row["target_mask_id"])]: row for row in target_decisions}
    if set(decision_by_surface) != TARGET_SURFACES:
        raise AssertionError("target decision coverage changed")

    local_displays = choose_local_displays(target_decisions, evaluations_by_candidate, candidate_order)
    dictionary_rows = make_dictionary(
        target_decisions, surface_by_mask, aggregates, metrics, branches_by_candidate
    )
    reader_rows, reader_consumption_rows, reader_markdown = make_reader(
        cohort, contexts, local_displays, surface_by_mask, target_decisions
    )

    artifacts.mkdir(parents=True, exist_ok=True)
    write_tsv(artifacts / "MASKED_COHORT_15_LINE_ATLAS.tsv", make_masked_atlas(cohort))
    write_tsv(
        artifacts / "TARGET_17_OCCURRENCE_INVENTORY.tsv",
        make_target_inventory(contexts, surface_by_occurrence),
    )
    write_tsv(artifacts / "NULL_ORPHAN_EDGE_ATLAS.tsv", make_null_orphans(contexts))
    write_tsv(
        artifacts / "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv",
        [occurrence_row(evaluation) for evaluation in all_evaluations],
    )
    write_tsv(
        artifacts / "ATTACHMENT_EDGE_ATLAS.tsv",
        make_attachment_rows(all_evaluations),
    )
    write_tsv(
        artifacts / "ORPHAN_DEBT_ATLAS.tsv", make_orphan_debt_rows(all_evaluations, context_by_id)
    )
    write_tsv(artifacts / "PENALTY_EVENT_ATLAS.tsv", make_penalty_event_rows(all_evaluations))
    write_tsv(artifacts / "TARGET_POLICY_SCOREBOARD.tsv", policy_rows)
    write_tsv(artifacts / "LEAVE_ONE_PAGE_OUT.tsv", loo_rows)
    write_tsv(artifacts / "BRANCH_COVERAGE.tsv", branch_rows)
    write_tsv(artifacts / "WINNER_GATE_AUDIT.tsv", gate_rows)
    write_tsv(
        artifacts / "TARGET_DECISIONS.tsv",
        [
            {
                "surface_provenance_only": surface_by_mask[str(row["target_mask_id"])],
                **row,
                "target_surface_visible_to_scorer": 0,
            }
            for row in target_decisions
        ],
    )
    write_tsv(artifacts / "GDT770_4_WORKING_DICTIONARY.tsv", dictionary_rows)
    write_tsv(artifacts / "FIFTEEN_COMPLETE_LINE_READER.tsv", reader_rows)
    write_tsv(artifacts / "READER_UNIT_CONSUMPTION.tsv", reader_consumption_rows)
    (artifacts / "GDT770_CONCRETE_READER.md").write_text(reader_markdown, encoding="utf-8")

    result: dict[str, object] = {
        "experiment_id": "GDT770",
        "status": make_status(target_decisions),
        "question": (
            "Which fixed whole-form policy best removes target-independent immediate-edge "
            "orphans when ol, ckhy, ols and otar are simultaneously masked in fifteen "
            "already admitted complete lines?"
        ),
        "counts": {
            **counts,
            "target_context_count": len(contexts),
            "null_orphan_edge_count": sum(len(context.null_orphans) for context in contexts),
            "candidate_occurrence_evaluation_count": len(all_evaluations),
            "leave_one_page_out_row_count": len(loo_rows),
            "branch_coverage_row_count": len(branch_rows),
            "winner_gate_row_count": len(gate_rows),
            "policy_winner_count": sum(bool(metrics[cid]["eligible"]) for cid in metrics),
            "dictionary_default_count": len(dictionary_rows),
            "reader_line_count": len(reader_rows),
            "reader_unit_consumption_count": len(reader_consumption_rows),
        },
        "target_results": {
            surface: {
                "target_mask_id": mask_by_surface[surface],
                "formal_decision": decision_by_surface[surface]["formal_decision"],
                "formal_status": decision_by_surface[surface]["formal_status"],
                "raw_lead_candidate": decision_by_surface[surface]["raw_lead_candidate"],
                "raw_lead_penalty": decision_by_surface[surface]["raw_lead_penalty"],
                "null_penalty": decision_by_surface[surface]["null_penalty"],
                "raw_lead_delta_vs_null": decision_by_surface[surface]["raw_lead_delta_vs_null"],
                "failed_gates": [
                    gate_id
                    for gate_id in str(
                        decision_by_surface[surface]["raw_lead_failed_gates"]
                    ).split("|")
                    if gate_id
                ],
                "lead_disposition": decision_by_surface[surface]["lead_disposition"],
            }
            for surface in sorted(decision_by_surface)
        },
        "score_contract": {
            "target_identity_seen_by_scorer": "opaque target_mask_id only",
            "neighbor_radius": 1,
            "skip_untyped_or_nonexact_neighbor": False,
            "fluency_credit": 0,
            "old_target_default_role_evidence_confidence_credit": 0,
            "target_surface_score_credit": 0,
            "orphan_priority": ["AMOUNT", "VALUE", "PATIENT", "RESULT"],
            "orphan_types": sorted(EDGE_TYPES),
            "penalty_weights": penalty_weights,
            "penalty_normative_sha256": counts["penalty_normative_sha256"],
            "winner_gate_normative_sha256": counts["winner_gate_normative_sha256"],
            "predicate_only_close_slot_count": counts["predicate_only_close_slot_count"],
            "resampling_unit": "page",
        },
        "scope": {
            "new_page_opened": False,
            "new_image_opened": False,
            "new_transcription_opened": False,
            "f84_accessed": False,
            "f84r_accessed": False,
            "source_scope": "fifteen already admitted complete-reader lines",
        },
        "claim_ceiling": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "confirmed_translations": 0,
            "component_export_credit": 0,
            "eva_latin_credit": 0,
            "defaults_are_replaceable": True,
        },
        "outputs": list(OUTPUT_NAMES),
    }
    write_json(artifacts / "RESULT.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    artifacts = args.artifacts_dir
    if not artifacts.is_absolute():
        artifacts = ROOT / artifacts
    result = build(artifacts)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
