#!/usr/bin/env python3
"""Deterministic structural helpers for GDT770.

The scorer is intentionally surface-blind at target positions.  ``surface`` is
retained by the cohort only for provenance checks; every condition below sees
the opaque ``target_mask_id`` and frozen non-target roles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Sequence


ROLE_SEPARATOR = "|"
EMPTY_MARKERS = {"", "NONE", "NA", "N/A"}
TARGET_SURFACES = {"ol", "ckhy", "ols", "otar"}
EDGE_TYPES = {"AMOUNT", "VALUE", "PATIENT", "RESULT", "FIELD_EDGE"}
TYPED_FIELD_ROLES = {
    "AMOUNT",
    "VALUE",
    "PATIENT",
    "SOURCE",
    "RESULT",
    "PROCESS",
    "ENDPOINT",
    "FIELD",
    "CLOSE",
    "PREDICATE_ONLY_CLOSE",
    "MATERIAL",
    "PREPARATION",
    "PRODUCT",
}


def split_set(value: str) -> frozenset[str]:
    """Parse the small pipe-separated role vocabulary used by the specs."""

    value = value.strip()
    if value.upper() in EMPTY_MARKERS:
        return frozenset()
    return frozenset(part.strip() for part in value.split(ROLE_SEPARATOR) if part.strip())


def has_any(roles: Iterable[str], allowed: str | Iterable[str]) -> bool:
    role_set = set(roles)
    allowed_set = split_set(allowed) if isinstance(allowed, str) else set(allowed)
    return bool(role_set & allowed_set)


def validated_role_argument(value: str, expression: str) -> frozenset[str]:
    roles = split_set(value)
    unknown = roles - TYPED_FIELD_ROLES
    if not roles or unknown:
        raise ValueError(
            f"invalid role argument in {expression!r}: "
            f"empty={not roles}, unknown={sorted(unknown)}"
        )
    return roles


@dataclass(frozen=True)
class Node:
    """One independent token or one render-once non-target span."""

    node_id: str
    cohort_id: str
    start: int
    end: int
    roles: frozenset[str]
    axes: frozenset[str]
    reader_exact: bool
    members: tuple[int, ...]
    surfaces: tuple[str, ...]


@dataclass(frozen=True)
class TargetContext:
    """Surface-free context made available to the candidate scorer."""

    occurrence_id: str
    cohort_id: str
    locus: str
    page: str
    target_mask_id: str
    ordinal: int
    line_token_count: int
    line_class: str
    left: Node | None
    right: Node | None
    predicate_only_close: bool
    null_orphans: tuple[tuple[str, str, str], ...]

    @property
    def line_final(self) -> bool:
        return self.ordinal == self.line_token_count

    @property
    def medial(self) -> bool:
        return 1 < self.ordinal < self.line_token_count

    @property
    def two_sided(self) -> bool:
        return self.left is not None and self.right is not None


@dataclass(frozen=True, order=True)
class Edge:
    """One role-labelled edge from a target to an immediate score node."""

    side_order: int
    role: str
    side: str
    neighbor_ordinal: int
    edge_id: str


@dataclass(frozen=True)
class BindingClaim:
    """One ordered required or optional attempt to consume a role edge."""

    claim_index: int
    binding_stage: str
    source_expression: str
    edge: Edge
    bound: bool
    double_consumption: bool


def _node_from_rows(cohort_id: str, rows: Sequence[Mapping[str, str]]) -> Node:
    ordered = sorted(rows, key=lambda row: int(row["ordinal"]))
    ordinals = tuple(int(row["ordinal"]) for row in ordered)
    span_ids = {row["span_id"] for row in ordered if row["span_id"] not in EMPTY_MARKERS}
    if len(span_ids) > 1:
        raise AssertionError(f"node crosses multiple spans in {cohort_id}: {span_ids}")
    # A target can own a reader-only span while remaining an independent score
    # node. Its consumed non-target partner keeps the span ID; the masked
    # target must not alias that ID in the graph.
    if len(ordered) == 1 and ordered[0]["is_target"] == "1":
        node_id = f"{cohort_id}:T{ordinals[0]:02d}"
    else:
        node_id = next(iter(span_ids), f"{cohort_id}:T{ordinals[0]:02d}")
    roles = frozenset().union(*(split_set(row["structural_roles"]) for row in ordered))
    axes = frozenset().union(*(split_set(row["structural_axes"]) for row in ordered))
    return Node(
        node_id=node_id,
        cohort_id=cohort_id,
        start=min(ordinals),
        end=max(ordinals),
        roles=roles,
        axes=axes,
        reader_exact=all(row["reader_exact"] == "1" for row in ordered),
        members=ordinals,
        surfaces=tuple(row["surface"] for row in ordered),
    )


def build_nodes(line_rows: Sequence[Mapping[str, str]]) -> tuple[Node, ...]:
    """Collapse only explicitly licensed spans; targets always remain singletons."""

    if not line_rows:
        return ()
    cohort_id = line_rows[0]["cohort_id"]
    grouped: dict[str, list[Mapping[str, str]]] = {}
    for row in sorted(line_rows, key=lambda item: int(item["ordinal"])):
        if row["is_target"] == "1":
            key = f"TARGET:{row['ordinal']}"
        elif row["span_id"] not in EMPTY_MARKERS:
            key = f"SPAN:{row['span_id']}"
        else:
            key = f"TOKEN:{row['ordinal']}"
        grouped.setdefault(key, []).append(row)
    nodes = tuple(
        sorted(
            (_node_from_rows(cohort_id, rows) for rows in grouped.values()),
            key=lambda node: (node.start, node.end, node.node_id),
        )
    )
    if len({node.node_id for node in nodes}) != len(nodes):
        raise AssertionError(f"duplicate score-node identity in {cohort_id}")
    return nodes


def _immediate_typed(nodes: Sequence[Node], ordinal: int, side: str) -> Node | None:
    """Return the physical neighbour only; never hop across an untyped cell."""

    candidates = [
        node
        for node in nodes
        if node.reader_exact
        and node.roles & TYPED_FIELD_ROLES
        and ((side == "LEFT" and node.end == ordinal - 1) or (side == "RIGHT" and node.start == ordinal + 1))
    ]
    if len(candidates) > 1:
        raise AssertionError(f"multiple immediate {side.lower()} nodes at ordinal {ordinal}")
    return candidates[0] if candidates else None


def _side_orphan_type(node: Node | None) -> str | None:
    if node is None:
        return None
    # One edge per side.  More specific bound quantities precede broader roles.
    for edge_type, role_set in (
        ("AMOUNT", {"AMOUNT"}),
        ("VALUE", {"VALUE"}),
        ("PATIENT", {"PATIENT"}),
        ("RESULT", {"RESULT", "ENDPOINT", "CLOSE"}),
    ):
        if node.roles & role_set:
            return edge_type
    return None


def make_target_contexts(
    rows: Sequence[Mapping[str, str]],
    predicate_only_close_by_slot: Mapping[tuple[str, int], bool],
) -> tuple[TargetContext, ...]:
    """Create target-local contexts without exposing target spellings or defaults."""

    by_line: dict[str, list[Mapping[str, str]]] = {}
    for row in rows:
        by_line.setdefault(row["cohort_id"], []).append(row)

    contexts: list[TargetContext] = []
    for cohort_id in sorted(by_line):
        line_rows = sorted(by_line[cohort_id], key=lambda row: int(row["ordinal"]))
        nodes = build_nodes(line_rows)
        for target in (row for row in line_rows if row["is_target"] == "1"):
            ordinal = int(target["ordinal"])
            left_raw = _immediate_typed(nodes, ordinal, "LEFT")
            right_raw = _immediate_typed(nodes, ordinal, "RIGHT")
            expected_left = split_set(target["left_neighbor_roles"])
            expected_right = split_set(target["right_neighbor_roles"])
            actual_left = left_raw.roles if left_raw is not None else frozenset()
            actual_right = right_raw.roles if right_raw is not None else frozenset()
            if expected_left and not expected_left <= actual_left:
                raise AssertionError(
                    f"left-neighbour role mismatch at {cohort_id}:{ordinal}: "
                    f"{sorted(expected_left)} not in {sorted(actual_left)}"
                )
            if expected_right and not expected_right <= actual_right:
                raise AssertionError(
                    f"right-neighbour role mismatch at {cohort_id}:{ordinal}: "
                    f"{sorted(expected_right)} not in {sorted(actual_right)}"
                )
            if not expected_left and left_raw is not None and target["left_neighbor_exact"] == "1":
                raise AssertionError(f"typed exact left neighbour omitted at {cohort_id}:{ordinal}")
            if not expected_right and right_raw is not None and target["right_neighbor_exact"] == "1":
                raise AssertionError(f"typed exact right neighbour omitted at {cohort_id}:{ordinal}")
            # For a render-once span the target-facing boundary member can have
            # fewer roles than the union of the whole span (for example s-aiin
            # exposes AMOUNT from the left but AMOUNT|VALUE from the right).
            left = replace(left_raw, roles=expected_left) if expected_left and left_raw else None
            right = replace(right_raw, roles=expected_right) if expected_right and right_raw else None
            orphans: list[tuple[str, str, str]] = []
            for side, node in (("LEFT", left), ("RIGHT", right)):
                edge_type = _side_orphan_type(node)
                if edge_type is not None and node is not None:
                    orphans.append((f"{cohort_id}:O{ordinal:02d}:{side}:{edge_type}", edge_type, side))
            if left is not None and right is not None:
                orphans.append((f"{cohort_id}:O{ordinal:02d}:BOTH:FIELD_EDGE", "FIELD_EDGE", "BOTH"))
            contexts.append(
                TargetContext(
                    occurrence_id=f"{cohort_id}:T{ordinal:02d}:{target['target_mask_id']}",
                    cohort_id=cohort_id,
                    locus=target["locus"],
                    page=target["page"],
                    target_mask_id=target["target_mask_id"],
                    ordinal=ordinal,
                    line_token_count=int(target["line_token_count"]),
                    line_class=target["line_class"],
                    left=left,
                    right=right,
                    predicate_only_close=predicate_only_close_by_slot[(cohort_id, ordinal)],
                    null_orphans=tuple(orphans),
                )
            )
    return tuple(contexts)


_CALL_RE = re.compile(r"^(NEAREST_(LEFT|RIGHT)_(NOT_)?IN)\(([^()]*)\)$")
_EDGE_CALL_RE = re.compile(r"^(LEFT_ONE|RIGHT_ONE|ANY_SIDE)\(([^()]*)\)$")


def validate_condition_expression(expression: str) -> tuple[str, ...]:
    atoms = tuple(part.strip() for part in expression.split("&") if part.strip())
    if not atoms:
        raise ValueError("empty branch condition")
    if "ELSE" in atoms and atoms != ("ELSE",):
        raise ValueError("ELSE must be the complete branch condition")
    if "ALWAYS" in atoms and atoms != ("ALWAYS",):
        raise ValueError("ALWAYS must be the complete branch condition")
    for atom in atoms:
        if atom in {"ALWAYS", "ELSE", "LINE_FINAL", "MEDIAL", "TWO_SIDED"}:
            continue
        match = _CALL_RE.fullmatch(atom)
        if match is None:
            raise ValueError(f"unsupported branch-condition atom: {atom}")
        validated_role_argument(match.group(4), atom)
    return atoms


def validate_edge_expression(expression: str) -> tuple[str, ...]:
    if expression.strip().upper() in EMPTY_MARKERS:
        return ()
    atoms = tuple(part.strip() for part in expression.split("&") if part.strip())
    if not atoms:
        raise ValueError("empty required-edge expression")
    for atom in atoms:
        negative = atom.startswith("NOT(") and atom.endswith(")")
        inner = atom[4:-1] if negative else atom
        if inner in {"LINE_FINAL", "MEDIAL"}:
            continue
        match = _EDGE_CALL_RE.fullmatch(inner)
        if match is None:
            raise ValueError(f"unsupported edge-expression atom: {atom}")
        validated_role_argument(match.group(2), atom)
    return atoms


def condition_holds(expression: str, context: TargetContext) -> bool:
    """Evaluate the deliberately tiny, non-recursive branch-condition DSL."""

    atoms = validate_condition_expression(expression)
    for atom in atoms:
        if atom == "ALWAYS":
            continue
        if atom == "LINE_FINAL" and not context.line_final:
            return False
        if atom == "MEDIAL" and not context.medial:
            return False
        if atom == "TWO_SIDED" and not context.two_sided:
            return False
        match = _CALL_RE.fullmatch(atom)
        if match:
            side = match.group(2)
            negate = bool(match.group(3))
            allowed = validated_role_argument(match.group(4), atom)
            node = context.left if side == "LEFT" else context.right
            present = node is not None and bool(node.roles & allowed)
            if present == negate:
                return False
            continue
        if atom == "ELSE":
            raise ValueError("ELSE is resolved only by the branch dispatcher")
        if atom not in {"LINE_FINAL", "MEDIAL", "TWO_SIDED"}:
            raise ValueError(f"unsupported branch-condition atom: {atom}")
    return True


def select_branch(
    branches: Sequence[Mapping[str, str]], context: TargetContext
) -> Mapping[str, str] | None:
    ordered = sorted(branches, key=lambda row: (int(row["branch_priority"]), row["branch_id"]))
    fallback: Mapping[str, str] | None = None
    for branch in ordered:
        if branch["branch_condition"] == "ELSE":
            fallback = branch
        elif condition_holds(branch["branch_condition"], context):
            return branch
    return fallback


def context_edges(context: TargetContext) -> tuple[Edge, ...]:
    edges: list[Edge] = []
    for side_order, (side, node) in enumerate((('LEFT', context.left), ('RIGHT', context.right))):
        if node is None:
            continue
        ordinal = node.end if side == "LEFT" else node.start
        for role in sorted(node.roles):
            edges.append(
                Edge(
                    side_order=side_order,
                    role=role,
                    side=side,
                    neighbor_ordinal=ordinal,
                    edge_id=f"{context.occurrence_id}:{side}:T{ordinal:02d}:{role}",
                )
            )
    return tuple(edges)


def bind_branch(
    branch: Mapping[str, str], context: TargetContext
) -> tuple[bool, tuple[Edge, ...], tuple[Edge, ...], tuple[BindingClaim, ...]]:
    """Bind positive requirements first, then one unused role-edge per side."""

    edges = context_edges(context)
    consumed: list[Edge] = []
    duplicates: list[Edge] = []
    claims: list[BindingClaim] = []
    required_left = split_set(branch["required_left_classes"])
    required_right = split_set(branch["required_right_classes"])
    if required_left and (context.left is None or not context.left.roles & required_left):
        return False, (), (), ()
    if required_right and (context.right is None or not context.right.roles & required_right):
        return False, (), (), ()

    expression = branch["required_edge_expression"].strip()
    atoms = validate_edge_expression(expression)
    for atom in atoms:
        negative = atom.startswith("NOT(") and atom.endswith(")")
        inner = atom[4:-1] if negative else atom
        if inner in {"LINE_FINAL", "MEDIAL"}:
            value = context.line_final if inner == "LINE_FINAL" else context.medial
            if value == negative:
                return False, (), (), ()
            continue
        match = _EDGE_CALL_RE.fullmatch(inner)
        if match is None:
            raise ValueError(f"unsupported edge-expression atom: {atom}")
        operation, role_text = match.groups()
        roles = validated_role_argument(role_text, atom)
        sides = (
            {"LEFT"}
            if operation == "LEFT_ONE"
            else {"RIGHT"}
            if operation == "RIGHT_ONE"
            else {"LEFT", "RIGHT"}
        )
        eligible = [edge for edge in edges if edge.side in sides and edge.role in roles]
        if negative:
            if eligible:
                return False, (), (), ()
            continue
        if not eligible:
            return False, (), (), ()
        used_ids = {edge.edge_id for edge in consumed}
        unused = [edge for edge in eligible if edge.edge_id not in used_ids]
        selected = min(unused or eligible)
        is_duplicate = not unused
        if is_duplicate:
            duplicates.append(selected)
        else:
            consumed.append(selected)
        claims.append(
            BindingClaim(
                claim_index=len(claims) + 1,
                binding_stage="REQUIRED",
                source_expression=atom,
                edge=selected,
                bound=not is_duplicate,
                double_consumption=is_duplicate,
            )
        )

    used_ids = {edge.edge_id for edge in consumed}
    for side, field in (("LEFT", "consumes_left_classes"), ("RIGHT", "consumes_right_classes")):
        roles = split_set(branch[field])
        eligible = [
            edge
            for edge in edges
            if edge.side == side and edge.role in roles and edge.edge_id not in used_ids
        ]
        if eligible:
            selected = min(eligible)
            consumed.append(selected)
            used_ids.add(selected.edge_id)
            claims.append(
                BindingClaim(
                    claim_index=len(claims) + 1,
                    binding_stage="OPTIONAL",
                    source_expression=field,
                    edge=selected,
                    bound=True,
                    double_consumption=False,
                )
            )
    return True, tuple(consumed), tuple(duplicates), tuple(claims)


def resolved_orphan_ids(
    context: TargetContext, bound_edges: Sequence[Edge]
) -> frozenset[str]:
    """Resolve only role-edges actually claimed by the deterministic binder."""

    bound_by_side: dict[str, set[str]] = {"LEFT": set(), "RIGHT": set()}
    for edge in bound_edges:
        bound_by_side[edge.side].add(edge.role)
    edge_roles = {
        "AMOUNT": {"AMOUNT"},
        "VALUE": {"VALUE"},
        "PATIENT": {"PATIENT"},
        "RESULT": {"RESULT", "ENDPOINT", "CLOSE"},
    }
    resolved: set[str] = set()
    for edge_id, edge_type, side in context.null_orphans:
        if edge_type == "FIELD_EDGE":
            if bound_by_side["LEFT"] and bound_by_side["RIGHT"]:
                resolved.add(edge_id)
        elif bound_by_side[side] & edge_roles[edge_type]:
            resolved.add(edge_id)
    return frozenset(resolved)
