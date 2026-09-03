#!/usr/bin/env python3
"""Penalty-only candidate scoring for GDT770.

There is deliberately no prose fluency term and no access to a target surface,
old target role, old German default, or target-derived confidence field.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from model import (
    BindingClaim,
    Edge,
    TargetContext,
    bind_branch,
    resolved_orphan_ids,
    select_branch,
)


PATIENT_CLASSES = {"PATIENT"}
SOURCE_CLASSES = {"SOURCE", "PATIENT", "PROCESS", "MATERIAL", "PREPARATION", "PRODUCT"}


@dataclass(frozen=True)
class PenaltyEvent:
    penalty_id: str
    trigger_code: str
    weight: int
    edge_id: str
    note: str


@dataclass(frozen=True)
class OccurrenceEvaluation:
    candidate_id: str
    occurrence_id: str
    cohort_id: str
    locus: str
    page: str
    target_mask_id: str
    branch_id: str
    policy_class: str
    policy_kind: str
    renderer_de: str
    branch_condition_holds: bool
    requirements_hold: bool
    binding_claims: tuple[BindingClaim, ...]
    bound_edges: tuple[Edge, ...]
    duplicate_edges: tuple[Edge, ...]
    consumed_sides: frozenset[str]
    resolved_orphans: frozenset[str]
    unresolved_orphans: frozenset[str]
    penalty_events: tuple[PenaltyEvent, ...]

    @property
    def penalty(self) -> int:
        return sum(event.weight for event in self.penalty_events)


def evaluate_occurrence(
    candidate_id: str,
    branches: Sequence[Mapping[str, str]],
    context: TargetContext,
    penalty_weights: Mapping[str, int],
) -> OccurrenceEvaluation:
    """Score one fixed candidate at one masked target occurrence."""

    if not branches:
        raise AssertionError(f"candidate without branches: {candidate_id}")
    policy_kind = branches[0]["policy_kind"]
    opaque = all(branch["opaque_baseline"] == "1" for branch in branches)
    branch = select_branch(branches, context)
    illegal_branch = branch is None and not opaque
    if branch is None:
        policy_class = "OPAQUE_NULL" if opaque else "UNRESOLVED"
        branch_id = "NO_LEGAL_BRANCH"
        renderer = "OPAQUE_NULL"
        requirements_ok = False
        binding_claims: tuple[BindingClaim, ...] = ()
        bound_edges: tuple[Edge, ...] = ()
        duplicate_edges: tuple[Edge, ...] = ()
    else:
        policy_class = branch["policy_class"]
        branch_id = branch["branch_id"]
        renderer = branch["renderer_de"]
        if opaque:
            requirements_ok = True
            bound_edges, duplicate_edges, binding_claims = (), (), ()
        else:
            requirements_ok, bound_edges, duplicate_edges, binding_claims = bind_branch(
                branch, context
            )
            if not requirements_ok:
                bound_edges, duplicate_edges, binding_claims = (), (), ()

    sides = frozenset(edge.side for edge in bound_edges)
    bound_roles = frozenset(edge.role for edge in bound_edges)
    resolved = (
        frozenset()
        if opaque or branch is None
        else resolved_orphan_ids(context, bound_edges)
    )
    all_orphans = frozenset(edge_id for edge_id, _edge_type, _side in context.null_orphans)
    unresolved = all_orphans - resolved
    events: list[PenaltyEvent] = []

    def add(penalty_id: str, trigger: str, edge_id: str, note: str) -> None:
        events.append(
            PenaltyEvent(
                penalty_id=penalty_id,
                trigger_code=trigger,
                weight=penalty_weights[penalty_id],
                edge_id=edge_id,
                note=note,
            )
        )

    bad_endpoint = False
    if illegal_branch:
        add(
            "P06_ILLEGAL_BRANCH_OR_BAD_ENDPOINT",
            "ILLEGAL_BRANCH",
            "NONE",
            "no preregistered positional branch applies",
        )
    elif policy_class == "ENDPOINT":
        bad_endpoint = not any(
            edge.side == "RIGHT" and edge.role == "ENDPOINT" for edge in bound_edges
        )
        if bad_endpoint:
            add(
                "P06_ILLEGAL_BRANCH_OR_BAD_ENDPOINT",
                "BAD_ENDPOINT",
                context.right.node_id if context.right is not None else "NONE",
                "endpoint policy lacks an immediate exact right ENDPOINT",
            )

    missing_valency_trigger = ""
    if not opaque and branch is not None:
        if policy_class == "OPERATION" and not bound_roles & PATIENT_CLASSES:
            missing_valency_trigger = "PATIENTLESS_OPERATION"
        elif policy_class == "MEASURE" and "VALUE" not in bound_roles:
            missing_valency_trigger = "VALUELESS_MEASURE"
        elif policy_class in {"LINKER", "ENDPOINT"} and len(sides) < 2 and not bad_endpoint:
            missing_valency_trigger = "ONE_SIDED_LINKER"
        if missing_valency_trigger:
            add(
                "P05_MISSING_REQUIRED_VALENCY",
                missing_valency_trigger,
                "NONE",
                "candidate did not bind its required valency",
            )

    for edge_id, edge_type, _side in context.null_orphans:
        if edge_id in unresolved:
            add(
                "P04_ORPHAN_OR_SOURCELESS_RESULT",
                f"ORPHAN_{edge_type}",
                edge_id,
                "NULL-exposed structural edge remains unbound",
            )

    if not opaque and branch is not None and policy_class == "RESULT" and not bound_roles & SOURCE_CLASSES:
        add(
            "P04_ORPHAN_OR_SOURCELESS_RESULT",
            "SOURCELESS_RESULT",
            "NONE",
            "result candidate has no bound source, patient, process, or content",
        )

    for edge in duplicate_edges:
        add(
            "P03_DOUBLE_CONSUMPTION",
            "DOUBLE_CONSUMPTION",
            edge.edge_id,
            "a second logical requirement claimed the same role edge",
        )

    if (
        not opaque
        and branch is not None
        and policy_class in {"NOMINAL", "RESULT", "MEASURE"}
        and context.predicate_only_close
    ):
        add(
            "P02_NOUN_IN_PREDICATE_ONLY_CLOSE",
            "NOUN_IN_PREDICATE_ONLY_CLOSE",
            "NONE",
            "nominal output in independently frozen predicate-only close",
        )

    if opaque or illegal_branch:
        add(
            "P01_UNRESOLVED_TARGET",
            "UNRESOLVED_TARGET",
            "NONE",
            "target remains opaque",
        )

    return OccurrenceEvaluation(
        candidate_id=candidate_id,
        occurrence_id=context.occurrence_id,
        cohort_id=context.cohort_id,
        locus=context.locus,
        page=context.page,
        target_mask_id=context.target_mask_id,
        branch_id=branch_id,
        policy_class=policy_class,
        policy_kind=policy_kind,
        renderer_de=renderer,
        branch_condition_holds=branch is not None,
        requirements_hold=requirements_ok,
        binding_claims=binding_claims,
        bound_edges=bound_edges,
        duplicate_edges=duplicate_edges,
        consumed_sides=sides,
        resolved_orphans=resolved,
        unresolved_orphans=unresolved,
        penalty_events=tuple(events),
    )


def aggregate_evaluations(
    candidate_id: str,
    evaluations: Sequence[OccurrenceEvaluation],
    branches: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    """Summarise one target-wide policy without re-estimating any branch."""

    penalties = Counter(
        event.penalty_id
        for evaluation in evaluations
        for event in evaluation.penalty_events
    )
    trigger_counts = Counter(
        event.trigger_code
        for evaluation in evaluations
        for event in evaluation.penalty_events
    )
    resolved = set().union(*(evaluation.resolved_orphans for evaluation in evaluations)) if evaluations else set()
    pages = {evaluation.page for evaluation in evaluations}
    resolved_pages = {
        evaluation.page for evaluation in evaluations if evaluation.resolved_orphans
    }
    branch_pages: dict[str, set[str]] = {
        branch["branch_id"]: set() for branch in branches
    }
    for evaluation in evaluations:
        if evaluation.branch_id in branch_pages and evaluation.requirements_hold:
            branch_pages[evaluation.branch_id].add(evaluation.page)
    required_branch_coverage = {
        branch["branch_id"]: {
            "minimum": int(branch["minimum_branch_pages"]),
            "observed": len(branch_pages[branch["branch_id"]]),
            "pages": tuple(sorted(branch_pages[branch["branch_id"]])),
        }
        for branch in branches
        if int(branch["minimum_branch_pages"]) > 0
    }
    return {
        "candidate_id": candidate_id,
        "policy_kind": branches[0]["policy_kind"],
        "policy_classes": tuple(sorted({branch["policy_class"] for branch in branches})),
        "target_occurrence_count": len(evaluations),
        "target_page_count": len(pages),
        "total_penalty": sum(evaluation.penalty for evaluation in evaluations),
        "penalty_event_count": sum(penalties.values()),
        "penalty_counts": dict(sorted(penalties.items())),
        "trigger_counts": dict(sorted(trigger_counts.items())),
        "resolved_null_orphan_count": len(resolved),
        "resolved_null_orphan_ids": tuple(sorted(resolved)),
        "resolved_orphan_page_count": len(resolved_pages),
        "resolved_orphan_pages": tuple(sorted(resolved_pages)),
        "required_branch_coverage": required_branch_coverage,
    }
