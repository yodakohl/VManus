#!/usr/bin/env python3
"""Independent invariant, score, gate, and byte-replay validator for GDT770.

This file deliberately does not import ``run.py``, ``model.py``, or
``scoring.py``.  It obtains the builder's file contract by statically reading
the literal ``OUTPUT_NAMES`` assignment, then recomputes the experiment from
the preregistered TSVs.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
RUN_PATH = SRC / "run.py"
MANIFEST_PATH = EXP / "experiment.json"

COHORT_PATH = SRC / "COHORT_15_LINE_SPECS.tsv"
EXCLUSION_PATH = SRC / "COHORT_EXCLUSION_LEDGER.tsv"
CANDIDATE_PATH = SRC / "CANDIDATE_POLICY_SPECS.tsv"
PENALTY_PATH = SRC / "PENALTY_SPECS.tsv"
GATE_PATH = SRC / "WINNER_GATE_SPECS.tsv"
SLOT_CONSTRAINT_PATH = SRC / "TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv"

EXPECTED_SOURCE_SHA256 = {
    "COHORT_15_LINE_SPECS.tsv": "369e5381abe59acfb59bd4db7ff75055e42f881b0cff0846bbe849c7c9b4c735",
    "COHORT_EXCLUSION_LEDGER.tsv": "6c683d1cae66ae27f1ef89685131eb23e61c65d65a6f0f92343748d400eae705",
    "CANDIDATE_POLICY_SPECS.tsv": "be4b7079160d6bacf35b2886d5371ee99035bc842caeab8e649475e437879534",
    "PENALTY_SPECS.tsv": "cdb224e8f2fed9ebbb98eb2ed6f97f51cb691657c744858bb286f108b8319254",
    "WINNER_GATE_SPECS.tsv": "91af34b056c0ef4a364ca12f27b69770eef65f53a61e34dc39494cdf672ab33a",
    "TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv": "b2a6cf146bf2d68967a04c78435c5ef575b919668c223fafd1cf023ca97406b0",
}

TARGETS = ("ol", "ckhy", "ols", "otar")
TARGET_MASKS = {
    "ol": "TM-Q7M2",
    "ckhy": "TM-V4C9",
    "ols": "TM-H8R1",
    "otar": "TM-N5K6",
}
TARGET_COUNTS = Counter({"ol": 5, "ckhy": 4, "ols": 3, "otar": 5})
ALLOWED_ROLES = frozenset(
    {
        "AMOUNT", "VALUE", "PATIENT", "SOURCE", "RESULT", "PROCESS",
        "ENDPOINT", "FIELD", "CLOSE", "PREDICATE_ONLY_CLOSE", "MATERIAL",
        "PREPARATION", "PRODUCT",
    }
)
ORPHAN_ROLE_GROUPS = (
    ("AMOUNT", frozenset({"AMOUNT"})),
    ("VALUE", frozenset({"VALUE"})),
    ("PATIENT", frozenset({"PATIENT"})),
    ("RESULT", frozenset({"RESULT", "ENDPOINT", "CLOSE"})),
)
PATIENT_ROLES = frozenset({"PATIENT"})
SOURCE_ROLES = frozenset({"SOURCE", "PATIENT", "PROCESS", "MATERIAL", "PREPARATION", "PRODUCT"})
EMPTY = frozenset({"", "NONE", "NA", "N/A"})
SEALED_PAGE = re.compile(r"(?i)^f84r?(?:\.|$)")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
BANNED_RETIRED_LITERAL_FRAGMENTS = ("samen", "saat", "wurzel", "holz", "pulver")

ZERO_FIELDS = frozenset(
    {
        "old_target_default_credit", "old_target_role_credit",
        "old_target_evidence_credit", "old_target_confidence_credit",
        "default_is_translation", "eva_latin_credit", "substring_export_credit",
        "component_claim_credit", "component_export_credit", "confirmed_lexeme",
        "confirmed_lexemes", "confirmed_plaintext", "confirmed_plaintext_clauses",
        "fluency_credit",
    }
)


def fields(text: str) -> tuple[str, ...]:
    return tuple(text.split())


PENALTY_NORMATIVE_FIELDS = fields(
    """penalty_id weight trigger_code applies_to_policy_classes scope
    per_occurrence_rule cofire_rule score_effect fluency_credit"""
)
GATE_NORMATIVE_FIELDS = fields(
    """gate_id evaluation_order applies_to_policy_kind metric comparator threshold
    comparator_target tie_behavior failure_disposition pass_disposition"""
)
EXPECTED_PENALTY_NORMATIVE_SHA256 = (
    "754f0d718f00eea6491d17c23d1eb9692a62af317258bdafe22cc3a87ad53290"
)
EXPECTED_GATE_NORMATIVE_SHA256 = (
    "40959bc5c3d517706378193750248e477fa17fb2762a8e6fea72adacab38f96d"
)


COHORT_SCHEMA = fields(
    """cohort_id locus page line_class line_token_count ordinal surface is_target
    target_mask_id scoring_identity frozen_non_target_default_de structural_axes
    structural_roles reader_exact span_id span_member_role render_once_owner_ordinal
    left_neighbor_roles right_neighbor_roles left_neighbor_exact right_neighbor_exact
    source_artifact source_row current_provenance old_target_default_credit
    old_target_role_credit old_target_evidence_credit old_target_confidence_credit
    default_is_translation confirmed_lexeme confirmed_plaintext
    component_export_credit"""
)
EXCLUSION_SCHEMA = fields(
    """exclusion_id locus page candidate_branch target_surfaces target_mask_ids
    target_ordinals candidate_target_ordinal candidate_target_reader_exact
    raw_target_cell_count exact_target_cell_count line_token_count
    gdt734_unknown_cells_v99r7 gdt734_complete_line_v99r7 structural_signal
    exclusion_reason source_artifact source_row corroborating_artifact
    corroborating_row eligible_for_cohort default_is_translation confirmed_lexeme
    confirmed_plaintext component_export_credit"""
)
CANDIDATE_SCHEMA = fields(
    """candidate_id target_surface policy_class policy_kind branch_id
    branch_priority branch_condition structural_tag renderer_de
    required_left_classes required_right_classes required_edge_expression
    consumes_left_classes consumes_right_classes minimum_branch_pages
    candidate_scope opaque_baseline default_is_translation eva_latin_credit
    substring_export_credit component_claim_credit confirmed_lexeme
    confirmed_plaintext"""
)
PENALTY_SCHEMA = fields(
    """penalty_id weight trigger_code applies_to_policy_classes scope
    per_occurrence_rule cofire_rule score_effect description_de fluency_credit"""
)
GATE_SCHEMA = fields(
    """gate_id evaluation_order gate_name applies_to_policy_kind metric comparator
    threshold comparator_target tie_behavior failure_disposition pass_disposition
    description_de"""
)
SLOT_CONSTRAINT_SCHEMA = fields(
    """cohort_id ordinal target_mask_id predicate_only_close provenance"""
)

EXPECTED_PENALTIES = (
    ("P06_ILLEGAL_BRANCH_OR_BAD_ENDPOINT", 6),
    ("P05_MISSING_REQUIRED_VALENCY", 5),
    ("P04_ORPHAN_OR_SOURCELESS_RESULT", 4),
    ("P03_DOUBLE_CONSUMPTION", 3),
    ("P02_NOUN_IN_PREDICATE_ONLY_CLOSE", 2),
    ("P01_UNRESOLVED_TARGET", 1),
)
EXPECTED_GATES = (
    "G01_BRANCH_PAGE_COVERAGE", "G02_NULL_MARGIN", "G03_EVERY_RIVAL_MARGIN",
    "G04_ORPHANS_REMOVED", "G05_ORPHAN_PAGES",
    "G06_POSITIONAL_BEATS_INVARIANT", "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS",
    "G08_EXACT_TIE_TO_NULL",
)
EXPECTED_OUTPUTS = (
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
ARTIFACT_SCHEMAS = {
    "MASKED_COHORT_15_LINE_ATLAS.tsv": fields(
        """cohort_id locus page ordinal masked_surface is_target scoring_identity
        reader_exact scorer_visible_roles scorer_visible_axes display_default_de
        span_id span_member_role render_once_owner_ordinal
        target_surface_visible_to_scorer
        old_target_default_role_evidence_confidence_credit fluency_credit
        component_export_credit"""
    ),
    "TARGET_17_OCCURRENCE_INVENTORY.tsv": fields(
        """occurrence_id cohort_id locus page ordinal target_mask_id
        surface_provenance_only line_final medial left_node_id left_roles
        right_node_id right_roles predicate_only_close_independent
        null_orphan_count null_orphan_types
        target_surface_visible_to_scorer old_target_semantic_credit"""
    ),
    "NULL_ORPHAN_EDGE_ATLAS.tsv": fields(
        """edge_id occurrence_id cohort_id locus page target_mask_id target_ordinal
        side edge_type neighbor_node_id neighbor_roles null_penalty target_derived"""
    ),
    "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv": fields(
        """candidate_id occurrence_id cohort_id locus page target_mask_id branch_id
        policy_class policy_kind renderer_de_display_only branch_condition_holds
        requirements_hold binding_claim_count consumed_sides bound_edge_count bound_edge_ids bound_roles
        duplicate_edge_count duplicate_edge_ids resolved_orphan_count
        resolved_orphan_ids unresolved_orphan_count unresolved_orphan_ids penalty
        penalty_ids trigger_codes fluency_credit target_surface_credit"""
    ),
    "ATTACHMENT_EDGE_ATLAS.tsv": fields(
        """candidate_id occurrence_id cohort_id locus page target_mask_id branch_id
        claim_index binding_stage source_expression edge_id side neighbor_ordinal
        role bound double_consumption binding_status distance target_surface_credit"""
    ),
    "ORPHAN_DEBT_ATLAS.tsv": fields(
        """candidate_id occurrence_id cohort_id locus page target_mask_id edge_id
        edge_type side under_null candidate_status penalty_id penalty
        candidate_created_edge"""
    ),
    "PENALTY_EVENT_ATLAS.tsv": fields(
        """candidate_id occurrence_id cohort_id locus page target_mask_id event_index
        penalty_id trigger_code edge_id weight note"""
    ),
    "TARGET_POLICY_SCOREBOARD.tsv": fields(
        """target_mask_id candidate_id policy_kind policy_classes
        target_occurrence_count target_page_count total_penalty null_penalty
        delta_vs_null min_pairwise_rival_margin resolved_null_orphan_count
        resolved_orphan_page_count minimum_leave_one_page_out_margin
        position_margin_over_best_invariant branch_coverage_pass failed_gate_ids
        eligible_policy_winner penalty_counts trigger_counts fluency_credit
        confirmed_lexeme"""
    ),
    "LEAVE_ONE_PAGE_OUT.tsv": fields(
        """target_mask_id held_page candidate_id fold_penalty null_candidate_id
        null_fold_penalty delta_vs_null best_rival_ids best_rival_penalty
        strict_pairwise_margin fold_minimum_ids unique_fold_winner"""
    ),
    "BRANCH_COVERAGE.tsv": fields(
        """target_mask_id candidate_id policy_kind policy_class branch_id
        branch_priority branch_condition selected_occurrence_count
        qualified_occurrence_count qualified_page_count qualified_pages
        minimum_branch_pages coverage_pass"""
    ),
    "WINNER_GATE_AUDIT.tsv": fields(
        """target_mask_id candidate_id gate_id evaluation_order applicable observed
        pass candidate_disposition"""
    ),
    "TARGET_DECISIONS.tsv": fields(
        """surface_provenance_only target_mask_id formal_decision formal_status
        raw_lead_candidate raw_minimum_candidates raw_lead_penalty null_candidate null_penalty
        raw_lead_delta_vs_null raw_lead_failed_gates lead_disposition
        policy_winner_count target_surface_visible_to_scorer"""
    ),
    "GDT770_4_WORKING_DICTIONARY.tsv": fields(
        """surface target_mask_id formal_target_default best_replaceable_policy
        structural_tags policy_renderer_de concrete_default_de confidence
        formal_policy_confidence lexeme_confidence evidence counterevidence scope
        replaceable default_is_translation confirmed_lexeme confirmed_plaintext
        substring_export_credit component_export_credit"""
    ),
    "FIFTEEN_COMPLETE_LINE_READER.tsv": fields(
        """cohort_id locus page token_count practical_unit_count manuscript_line
        simultaneously_masked_line target_count target_dispatches practical_units_de
        concrete_working_reader_de every_token_consumed_once
        formal_translation_claim"""
    ),
    "READER_UNIT_CONSUMPTION.tsv": fields(
        """unit_id cohort_id locus page unit_index owner_ordinal
        source_member_ordinals source_member_surfaces member_count unit_kind
        target_occurrence_id local_policy_ids support_grade editorial_rule
        reader_text_de score_credit"""
    ),
}


def split_set(value: str) -> frozenset[str]:
    value = value.strip()
    if value.upper() in EMPTY:
        return frozenset()
    return frozenset(part.strip() for part in value.split("|") if part.strip())


def as_int(value: str, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"{label} is not an integer: {value!r}") from exc


def is_zero(value: object) -> bool:
    return value is False or value == 0 or str(value).strip().casefold() in {
        "", "0", "false", "none", "zero",
    }


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    raw = path.read_bytes()
    if b"\x00" in raw or b"\r" in raw:
        raise AssertionError(f"non-canonical TSV bytes: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AssertionError(f"TSV is not UTF-8: {path}") from exc
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    header = tuple(reader.fieldnames or ())
    rows = list(reader)
    if not header or len(header) != len(set(header)) or any(not name for name in header):
        raise AssertionError(f"invalid TSV header: {path}")
    if any(None in row for row in rows) or any(value is None for row in rows for value in row.values()):
        raise AssertionError(f"TSV row width differs from header: {path}")
    return header, rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projection_sha256(
    rows: Sequence[Mapping[str, str]], selected_fields: Sequence[str]
) -> str:
    payload = ["\t".join(selected_fields)]
    payload.extend("\t".join(row[field] for field in selected_fields) for row in rows)
    return hashlib.sha256(("\n".join(payload) + "\n").encode("utf-8")).hexdigest()


def safe_repo_path(value: str, label: str) -> Path:
    posix = PurePosixPath(value)
    if posix.is_absolute() or not value or ".." in posix.parts or "\\" in value:
        raise AssertionError(f"unsafe repository path in {label}: {value!r}")
    resolved = (ROOT / Path(*posix.parts)).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise AssertionError(f"path escapes repository in {label}: {value!r}") from exc
    return resolved


def recursive_zero_checks(value: object, check: Callable[[bool, str], None], location: str = "result") -> int:
    hits = 0
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{location}.{key}"
            if str(key).casefold() in ZERO_FIELDS or str(key).casefold().startswith("confirmed_"):
                check(is_zero(item), f"nonzero semantic claim at {child}: {item!r}")
                hits += 1
            hits += recursive_zero_checks(item, check, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits += recursive_zero_checks(item, check, f"{location}[{index}]")
    return hits


def literal_output_names(path: Path) -> tuple[str, ...]:
    """Read OUTPUT_NAMES without executing or importing runner code."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[ast.AST] = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == "OUTPUT_NAMES" for target in targets):
                if node.value is not None:
                    values.append(node.value)
    if len(values) != 1:
        raise AssertionError("run.py must contain exactly one literal OUTPUT_NAMES assignment")
    try:
        result = ast.literal_eval(values[0])
    except (ValueError, TypeError, SyntaxError) as exc:
        raise AssertionError("run.py OUTPUT_NAMES must be a literal tuple/list") from exc
    if not isinstance(result, (tuple, list)) or not result or any(not isinstance(item, str) for item in result):
        raise AssertionError("run.py OUTPUT_NAMES is not a nonempty string sequence")
    return tuple(result)


@dataclass(frozen=True)
class Node:
    node_id: str
    start: int
    end: int
    roles: frozenset[str]
    exact: bool
    members: tuple[int, ...]


@dataclass(frozen=True)
class Neighbor:
    side: str
    ordinal: int
    node_id: str
    roles: frozenset[str]


@dataclass(frozen=True)
class Orphan:
    orphan_id: str
    orphan_type: str
    side: str
    resolving_roles: frozenset[str]


@dataclass(frozen=True)
class Context:
    occurrence_id: str
    cohort_id: str
    locus: str
    page: str
    target_surface: str
    target_mask_id: str
    ordinal: int
    line_token_count: int
    left: Neighbor | None
    right: Neighbor | None
    target_slot_roles: frozenset[str]
    null_orphans: tuple[Orphan, ...]

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
    side_order: int
    role: str
    side: str
    neighbor_ordinal: int
    edge_id: str


@dataclass(frozen=True)
class PenaltyEvent:
    penalty_id: str
    trigger_code: str
    weight: int
    edge_id: str


@dataclass(frozen=True)
class BindingClaim:
    claim_index: int
    binding_stage: str
    source_expression: str
    edge: Edge
    bound: bool
    double_consumption: bool


@dataclass(frozen=True)
class Evaluation:
    candidate_id: str
    occurrence_id: str
    cohort_id: str
    locus: str
    page: str
    target_surface: str
    target_mask_id: str
    target_ordinal: int
    branch_id: str
    policy_class: str
    policy_kind: str
    renderer_de: str
    branch_condition_holds: bool
    requirements_hold: bool
    binding_claims: tuple[BindingClaim, ...]
    bound_edges: tuple[Edge, ...]
    duplicate_edges: tuple[Edge, ...]
    resolved_orphans: frozenset[str]
    unresolved_orphans: frozenset[str]
    penalties: tuple[PenaltyEvent, ...]

    @property
    def total_penalty(self) -> int:
        return sum(event.weight for event in self.penalties)


def build_score_nodes(line_rows: Sequence[Mapping[str, str]]) -> tuple[Node, ...]:
    """Collapse only the three non-target spans; every target stays separate."""
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in sorted(line_rows, key=lambda item: as_int(item["ordinal"], "ordinal")):
        ordinal = as_int(row["ordinal"], "ordinal")
        if row["is_target"] == "1":
            key = f"TARGET:{ordinal}"
        elif row["span_id"] != "NONE" and row["span_member_role"] != "CONSUMED" or (
            row["span_id"] != "NONE" and row["span_member_role"] == "CONSUMED"
            and not any(
                other["span_id"] == row["span_id"] and other["is_target"] == "1"
                for other in line_rows
            )
        ):
            key = f"SPAN:{row['span_id']}"
        else:
            # The VALUE member of target-bearing X4P7 stays a score node.
            key = f"TOKEN:{ordinal}"
        grouped[key].append(row)
    nodes: list[Node] = []
    cohort_id = line_rows[0]["cohort_id"] if line_rows else ""
    for key, members in grouped.items():
        ordered = sorted(members, key=lambda item: as_int(item["ordinal"], "ordinal"))
        ordinals = tuple(as_int(row["ordinal"], "ordinal") for row in ordered)
        span_ids = {row["span_id"] for row in ordered if row["span_id"] not in EMPTY}
        if len(span_ids) > 1:
            raise AssertionError(f"node crosses spans in {cohort_id}: {sorted(span_ids)}")
        target_singleton = len(ordered) == 1 and ordered[0]["is_target"] == "1"
        nodes.append(
            Node(
                node_id=(
                    f"{cohort_id}:T{ordinals[0]:02d}"
                    if target_singleton
                    else next(iter(span_ids), f"{cohort_id}:T{ordinals[0]:02d}")
                ),
                start=min(ordinals),
                end=max(ordinals),
                roles=(
                    frozenset()
                    if target_singleton
                    else frozenset().union(
                        *(split_set(row["structural_roles"]) for row in ordered)
                    )
                ),
                exact=all(row["reader_exact"] == "1" for row in ordered),
                members=ordinals,
            )
        )
    return tuple(sorted(nodes, key=lambda node: (node.start, node.end, node.node_id)))


def direct_node(nodes: Sequence[Node], ordinal: int, side: str) -> Node | None:
    matches = [
        node
        for node in nodes
        if node.exact
        and node.roles & ALLOWED_ROLES
        and ((side == "LEFT" and node.end == ordinal - 1) or (side == "RIGHT" and node.start == ordinal + 1))
    ]
    if len(matches) > 1:
        raise AssertionError(f"multiple direct {side} nodes at ordinal {ordinal}")
    return matches[0] if matches else None


def make_contexts(
    cohort: Sequence[Mapping[str, str]],
    predicate_only_close_by_slot: Mapping[tuple[str, int], bool] | None = None,
) -> tuple[Context, ...]:
    predicate_only_close_by_slot = predicate_only_close_by_slot or {}
    by_line: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
    contexts: list[Context] = []
    for cohort_id in sorted(by_line):
        line = sorted(by_line[cohort_id], key=lambda row: as_int(row["ordinal"], "ordinal"))
        nodes = build_score_nodes(line)
        for row in line:
            if row["is_target"] != "1":
                continue
            ordinal = as_int(row["ordinal"], f"{cohort_id} target ordinal")
            neighbors: dict[str, Neighbor | None] = {}
            for side, role_field, exact_field in (
                ("LEFT", "left_neighbor_roles", "left_neighbor_exact"),
                ("RIGHT", "right_neighbor_roles", "right_neighbor_exact"),
            ):
                declared_roles = split_set(row[role_field])
                node = direct_node(nodes, ordinal, side)
                declared_exact = row[exact_field] == "1"
                if declared_roles:
                    if not declared_exact or node is None:
                        raise AssertionError(f"declared {side} roles lack an exact direct node at {cohort_id}:{ordinal}")
                    if not declared_roles <= node.roles:
                        raise AssertionError(
                            f"declared {side} roles differ from direct node at {cohort_id}:{ordinal}: "
                            f"{sorted(declared_roles)} not in {sorted(node.roles)}"
                        )
                    neighbors[side] = Neighbor(
                        side,
                        node.end if side == "LEFT" else node.start,
                        node.node_id,
                        declared_roles,
                    )
                else:
                    if declared_exact:
                        raise AssertionError(f"exact {side} flag without roles at {cohort_id}:{ordinal}")
                    if node is not None:
                        raise AssertionError(f"exact typed direct {side} node omitted at {cohort_id}:{ordinal}")
                    neighbors[side] = None
            orphans: list[Orphan] = []
            for side in ("LEFT", "RIGHT"):
                neighbor = neighbors[side]
                if neighbor is None:
                    continue
                for orphan_type, role_group in ORPHAN_ROLE_GROUPS:
                    present = neighbor.roles & role_group
                    if present:
                        orphans.append(
                            Orphan(
                                f"{cohort_id}:O{ordinal:02d}:{side}:{orphan_type}",
                                orphan_type,
                                side,
                                present,
                            )
                        )
                        break
            if neighbors["LEFT"] is not None and neighbors["RIGHT"] is not None:
                orphans.append(
                    Orphan(
                        f"{cohort_id}:O{ordinal:02d}:BOTH:FIELD_EDGE",
                        "FIELD_EDGE",
                        "BOTH",
                        frozenset(),
                    )
                )
            contexts.append(
                Context(
                    occurrence_id=f"{cohort_id}:T{ordinal:02d}:{row['target_mask_id']}",
                    cohort_id=cohort_id,
                    locus=row["locus"],
                    page=row["page"],
                    target_surface=row["surface"],
                    target_mask_id=row["target_mask_id"],
                    ordinal=ordinal,
                    line_token_count=as_int(row["line_token_count"], "line_token_count"),
                    left=neighbors["LEFT"],
                    right=neighbors["RIGHT"],
                    target_slot_roles=(
                        frozenset({"PREDICATE_ONLY_CLOSE"})
                        if predicate_only_close_by_slot.get((cohort_id, ordinal), False)
                        else frozenset()
                    ),
                    null_orphans=tuple(orphans),
                )
            )
    return tuple(sorted(contexts, key=lambda item: (item.page, item.locus, item.ordinal, item.target_mask_id)))


CALL_RE = re.compile(r"^NEAREST_(LEFT|RIGHT)_(NOT_)?IN\(([^()]*)\)$")
EDGE_RE = re.compile(r"^(LEFT_ONE|RIGHT_ONE|ANY_SIDE)\(([^()]*)\)$")


def validate_role_argument(value: str, expression: str) -> frozenset[str]:
    roles = split_set(value)
    unknown = roles - ALLOWED_ROLES
    if not roles or unknown:
        raise AssertionError(
            f"invalid role argument in {expression!r}: "
            f"empty={not roles}, unknown={sorted(unknown)}"
        )
    return roles


def validate_condition_expression(expression: str) -> None:
    atoms = [part.strip() for part in expression.split("&") if part.strip()]
    if not atoms:
        raise AssertionError("empty branch condition")
    if any(atom in {"ALWAYS", "ELSE"} for atom in atoms):
        if len(atoms) != 1:
            raise AssertionError(f"ALWAYS/ELSE must be a whole condition: {expression!r}")
        return
    for atom in atoms:
        if atom in {"LINE_FINAL", "MEDIAL", "TWO_SIDED"}:
            continue
        match = CALL_RE.fullmatch(atom)
        if match is None:
            raise AssertionError(f"unsupported branch-condition atom: {atom}")
        validate_role_argument(match.group(3), atom)


def validate_edge_expression(expression: str) -> None:
    if expression.strip().upper() in EMPTY:
        return
    atoms = [part.strip() for part in expression.split("&") if part.strip()]
    if not atoms:
        raise AssertionError("empty required-edge expression")
    for atom in atoms:
        inner = atom[4:-1] if atom.startswith("NOT(") and atom.endswith(")") else atom
        if inner in {"LINE_FINAL", "MEDIAL"}:
            continue
        match = EDGE_RE.fullmatch(inner)
        if match is None:
            raise AssertionError(f"unsupported required-edge atom: {atom}")
        validate_role_argument(match.group(2), atom)


def condition_holds(expression: str, context: Context) -> bool:
    validate_condition_expression(expression)
    for atom in (part.strip() for part in expression.split("&") if part.strip()):
        if atom in {"ALWAYS", "ELSE"}:
            continue
        if atom == "LINE_FINAL":
            if not context.line_final:
                return False
            continue
        if atom == "MEDIAL":
            if not context.medial:
                return False
            continue
        if atom == "TWO_SIDED":
            if not context.two_sided:
                return False
            continue
        match = CALL_RE.fullmatch(atom)
        if match is None:
            raise AssertionError(f"unsupported branch-condition atom: {atom}")
        side, negative, roles_text = match.groups()
        neighbor = context.left if side == "LEFT" else context.right
        present = neighbor is not None and bool(
            neighbor.roles & validate_role_argument(roles_text, atom)
        )
        if present == bool(negative):
            return False
    return True


def select_branch(branches: Sequence[Mapping[str, str]], context: Context) -> Mapping[str, str] | None:
    fallback: Mapping[str, str] | None = None
    for branch in sorted(
        branches,
        key=lambda row: (as_int(row["branch_priority"], "branch_priority"), row["branch_id"]),
    ):
        if branch["branch_condition"] == "ELSE":
            fallback = branch
        elif condition_holds(branch["branch_condition"], context):
            return branch
    return fallback


def context_edges(context: Context) -> tuple[Edge, ...]:
    result: list[Edge] = []
    for side_order, neighbor in enumerate((context.left, context.right)):
        if neighbor is None:
            continue
        for role in sorted(neighbor.roles):
            result.append(
                Edge(
                    side_order,
                    role,
                    neighbor.side,
                    neighbor.ordinal,
                    f"{context.occurrence_id}:{neighbor.side}:T{neighbor.ordinal:02d}:{role}",
                )
            )
    return tuple(result)


def bind_branch(
    branch: Mapping[str, str], context: Context
) -> tuple[bool, tuple[Edge, ...], tuple[Edge, ...], tuple[BindingClaim, ...]]:
    """Bind required expressions first, then one still-open edge per side."""
    edges = context_edges(context)
    consumed: list[Edge] = []
    duplicate: list[Edge] = []
    claims: list[BindingClaim] = []
    required_left = split_set(branch["required_left_classes"])
    required_right = split_set(branch["required_right_classes"])
    if required_left and (context.left is None or not context.left.roles & required_left):
        return False, (), (), ()
    if required_right and (context.right is None or not context.right.roles & required_right):
        return False, (), (), ()
    expression = branch["required_edge_expression"].strip()
    validate_edge_expression(expression)
    atoms = [] if expression.upper() in EMPTY else [part.strip() for part in expression.split("&") if part.strip()]
    for atom in atoms:
        negative = atom.startswith("NOT(") and atom.endswith(")")
        inner = atom[4:-1] if negative else atom
        if inner in {"LINE_FINAL", "MEDIAL"}:
            value = context.line_final if inner == "LINE_FINAL" else context.medial
            if value == negative:
                return False, (), (), ()
            continue
        match = EDGE_RE.fullmatch(inner)
        if match is None:
            raise AssertionError(f"unsupported required-edge atom: {atom}")
        operation, roles_text = match.groups()
        roles = validate_role_argument(roles_text, atom)
        sides = {"LEFT"} if operation == "LEFT_ONE" else {"RIGHT"} if operation == "RIGHT_ONE" else {"LEFT", "RIGHT"}
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
            duplicate.append(selected)
        else:
            consumed.append(selected)
        claims.append(
            BindingClaim(
                len(claims) + 1,
                "REQUIRED",
                atom,
                selected,
                not is_duplicate,
                is_duplicate,
            )
        )
    used_ids = {edge.edge_id for edge in consumed}
    for side, field in (("LEFT", "consumes_left_classes"), ("RIGHT", "consumes_right_classes")):
        roles = split_set(branch[field])
        eligible = [
            edge for edge in edges
            if edge.side == side and edge.role in roles and edge.edge_id not in used_ids
        ]
        if eligible:
            selected = min(eligible)
            consumed.append(selected)
            used_ids.add(selected.edge_id)
            claims.append(
                BindingClaim(
                    len(claims) + 1,
                    "OPTIONAL",
                    field,
                    selected,
                    True,
                    False,
                )
            )
    return True, tuple(consumed), tuple(duplicate), tuple(claims)


def resolved_orphans(context: Context, bound: Sequence[Edge]) -> frozenset[str]:
    bound_by_side: dict[str, set[str]] = defaultdict(set)
    for edge in bound:
        bound_by_side[edge.side].add(edge.role)
    resolved: set[str] = set()
    for orphan in context.null_orphans:
        if orphan.orphan_type == "FIELD_EDGE":
            if bound_by_side["LEFT"] and bound_by_side["RIGHT"]:
                resolved.add(orphan.orphan_id)
        elif bound_by_side[orphan.side] & orphan.resolving_roles:
            resolved.add(orphan.orphan_id)
    return frozenset(resolved)


def evaluate_occurrence(
    candidate_id: str,
    branches: Sequence[Mapping[str, str]],
    context: Context,
    weights: Mapping[str, int],
) -> Evaluation:
    branch = select_branch(branches, context)
    opaque = all(row["opaque_baseline"] == "1" for row in branches)
    illegal = branch is None and not opaque
    if branch is None:
        branch_id = "NO_LEGAL_BRANCH"
        policy_class = "OPAQUE_NULL" if opaque else "UNRESOLVED"
        policy_kind = branches[0]["policy_kind"]
        renderer = "OPAQUE_NULL"
        requirements_hold = False
        binding_claims: tuple[BindingClaim, ...] = ()
        bound: tuple[Edge, ...] = ()
        duplicate: tuple[Edge, ...] = ()
    else:
        branch_id = branch["branch_id"]
        policy_class = branch["policy_class"]
        policy_kind = branch["policy_kind"]
        renderer = branch["renderer_de"]
        if opaque:
            requirements_hold, bound, duplicate, binding_claims = True, (), (), ()
        else:
            requirements_hold, bound, duplicate, binding_claims = bind_branch(branch, context)
            if not requirements_hold:
                bound, duplicate, binding_claims = (), (), ()
    resolved = frozenset() if opaque or branch is None else resolved_orphans(context, bound)
    all_orphans = frozenset(orphan.orphan_id for orphan in context.null_orphans)
    unresolved = all_orphans - resolved
    events: list[PenaltyEvent] = []

    def add(penalty_id: str, trigger: str, edge_id: str = "NONE") -> None:
        events.append(PenaltyEvent(penalty_id, trigger, weights[penalty_id], edge_id))

    bound_sides = {edge.side for edge in bound}
    bound_roles = {edge.role for edge in bound}
    bad_endpoint = False
    if illegal:
        add("P06_ILLEGAL_BRANCH_OR_BAD_ENDPOINT", "ILLEGAL_BRANCH")
    elif policy_class == "ENDPOINT" and not any(
        edge.side == "RIGHT" and edge.role == "ENDPOINT" for edge in bound
    ):
        bad_endpoint = True
        add(
            "P06_ILLEGAL_BRANCH_OR_BAD_ENDPOINT",
            "BAD_ENDPOINT",
            context.right.node_id if context.right is not None else "NONE",
        )
    if not opaque and branch is not None:
        trigger = ""
        if policy_class == "OPERATION" and not bound_roles & PATIENT_ROLES:
            trigger = "PATIENTLESS_OPERATION"
        elif policy_class == "MEASURE" and "VALUE" not in bound_roles:
            trigger = "VALUELESS_MEASURE"
        elif policy_class in {"LINKER", "ENDPOINT"} and len(bound_sides) < 2 and not bad_endpoint:
            trigger = "ONE_SIDED_LINKER"
        if trigger:
            add("P05_MISSING_REQUIRED_VALENCY", trigger)
    for orphan in context.null_orphans:
        if orphan.orphan_id in unresolved:
            add(
                "P04_ORPHAN_OR_SOURCELESS_RESULT",
                f"ORPHAN_{orphan.orphan_type}",
                orphan.orphan_id,
            )
    if not opaque and branch is not None and policy_class == "RESULT" and not bound_roles & SOURCE_ROLES:
        add("P04_ORPHAN_OR_SOURCELESS_RESULT", "SOURCELESS_RESULT")
    for edge in duplicate:
        add("P03_DOUBLE_CONSUMPTION", "DOUBLE_CONSUMPTION", edge.edge_id)
    if (
        not opaque
        and branch is not None
        and policy_class in {"NOMINAL", "RESULT", "MEASURE"}
        and "PREDICATE_ONLY_CLOSE" in context.target_slot_roles
    ):
        add("P02_NOUN_IN_PREDICATE_ONLY_CLOSE", "NOUN_IN_PREDICATE_ONLY_CLOSE")
    if opaque or illegal:
        add("P01_UNRESOLVED_TARGET", "UNRESOLVED_TARGET")
    return Evaluation(
        candidate_id=candidate_id,
        occurrence_id=context.occurrence_id,
        cohort_id=context.cohort_id,
        locus=context.locus,
        page=context.page,
        target_surface=context.target_surface,
        target_mask_id=context.target_mask_id,
        target_ordinal=context.ordinal,
        branch_id=branch_id,
        policy_class=policy_class,
        policy_kind=policy_kind,
        renderer_de=renderer,
        branch_condition_holds=branch is not None,
        requirements_hold=requirements_hold,
        binding_claims=binding_claims,
        bound_edges=bound,
        duplicate_edges=duplicate,
        resolved_orphans=resolved,
        unresolved_orphans=unresolved,
        penalties=tuple(events),
    )


def aggregate(
    candidate_id: str,
    evaluations: Sequence[Evaluation],
    branches: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    penalties = Counter(event.penalty_id for evaluation in evaluations for event in evaluation.penalties)
    triggers = Counter(event.trigger_code for evaluation in evaluations for event in evaluation.penalties)
    resolved = set().union(*(evaluation.resolved_orphans for evaluation in evaluations)) if evaluations else set()
    resolved_pages = {evaluation.page for evaluation in evaluations if evaluation.resolved_orphans}
    branch_pages: dict[str, set[str]] = {row["branch_id"]: set() for row in branches}
    for evaluation in evaluations:
        if evaluation.requirements_hold and evaluation.branch_id in branch_pages:
            branch_pages[evaluation.branch_id].add(evaluation.page)
    coverage = {
        row["branch_id"]: {
            "minimum": as_int(row["minimum_branch_pages"], "minimum_branch_pages"),
            "observed": len(branch_pages[row["branch_id"]]),
            "pages": tuple(sorted(branch_pages[row["branch_id"]])),
        }
        for row in branches
        if as_int(row["minimum_branch_pages"], "minimum_branch_pages") > 0
    }
    return {
        "candidate_id": candidate_id,
        "target_surface": branches[0]["target_surface"],
        "policy_kind": branches[0]["policy_kind"],
        "policy_classes": tuple(sorted({row["policy_class"] for row in branches})),
        "total_penalty": sum(evaluation.total_penalty for evaluation in evaluations),
        "penalty_event_count": sum(penalties.values()),
        "penalty_counts": dict(sorted(penalties.items())),
        "trigger_counts": dict(sorted(triggers.items())),
        "target_occurrence_count": len(evaluations),
        "target_page_count": len({evaluation.page for evaluation in evaluations}),
        "resolved_null_orphan_count": len(resolved),
        "resolved_null_orphan_ids": tuple(sorted(resolved)),
        "resolved_orphan_page_count": len(resolved_pages),
        "resolved_orphan_pages": tuple(sorted(resolved_pages)),
        "required_branch_coverage": coverage,
    }


def calculate_core(
    cohort: Sequence[Mapping[str, str]],
    candidate_rows: Sequence[Mapping[str, str]],
    weights: Mapping[str, int],
    slot_constraints: Sequence[Mapping[str, str]] = (),
) -> dict[str, object]:
    predicate_only_close_by_slot = {
        (row["cohort_id"], as_int(row["ordinal"], "slot ordinal")):
        row["predicate_only_close"] == "1"
        for row in slot_constraints
    }
    contexts = make_contexts(cohort, predicate_only_close_by_slot)
    by_candidate: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        by_candidate[row["candidate_id"]].append(row)
    evaluations: dict[str, tuple[Evaluation, ...]] = {}
    summaries: dict[str, dict[str, object]] = {}
    for candidate_id, branches in by_candidate.items():
        target = branches[0]["target_surface"]
        relevant = [context for context in contexts if context.target_mask_id == TARGET_MASKS[target]]
        items = tuple(
            evaluate_occurrence(candidate_id, branches, context, weights)
            for context in relevant
        )
        evaluations[candidate_id] = items
        summaries[candidate_id] = aggregate(candidate_id, items, branches)
    pages_by_target = {
        target: tuple(sorted({context.page for context in contexts if context.target_mask_id == TARGET_MASKS[target]}))
        for target in TARGETS
    }
    fold_penalties = {
        (candidate_id, page): sum(item.total_penalty for item in items if item.page != page)
        for candidate_id, items in evaluations.items()
        for page in pages_by_target[by_candidate[candidate_id][0]["target_surface"]]
    }
    decks: dict[str, list[str]] = defaultdict(list)
    for candidate_id, branches in by_candidate.items():
        decks[branches[0]["target_surface"]].append(candidate_id)
    null_by_target = {
        target: next(
            candidate_id for candidate_id in deck
            if all(row["opaque_baseline"] == "1" for row in by_candidate[candidate_id])
        )
        for target, deck in decks.items()
    }
    candidate_dispositions: dict[str, str] = {}
    gate_results: dict[tuple[str, str], bool] = {}
    for target in TARGETS:
        deck = decks[target]
        null_id = null_by_target[target]
        full = {candidate_id: int(summaries[candidate_id]["total_penalty"]) for candidate_id in deck}
        for candidate_id in deck:
            summary = summaries[candidate_id]
            summary["null_candidate_id"] = null_id
            summary["null_penalty"] = full[null_id]
            summary["delta_vs_null"] = full[null_id] - full[candidate_id]
            margins = {
                rival: full[rival] - full[candidate_id]
                for rival in deck if rival != candidate_id
            }
            summary["pairwise_margins"] = dict(sorted(margins.items()))
            summary["minimum_rival_margin"] = min(margins.values())
            invariant_ids = [
                rival for rival in deck
                if by_candidate[rival][0]["policy_kind"] == "INVARIANT"
            ]
            best_invariant = min((full[rival] for rival in invariant_ids), default=None)
            summary["best_invariant_penalty"] = best_invariant
            summary["margin_over_best_invariant"] = (
                best_invariant - full[candidate_id] if best_invariant is not None else None
            )
            fold_margins = {
                f"{page}|{rival}": fold_penalties[(rival, page)] - fold_penalties[(candidate_id, page)]
                for page in pages_by_target[target] for rival in deck if rival != candidate_id
            }
            summary["lopo_pairwise_margins"] = dict(sorted(fold_margins.items()))
            summary["minimum_lopo_margin"] = min(fold_margins.values())
            if candidate_id == null_id:
                candidate_dispositions[candidate_id] = "OPAQUE_NULL_BASELINE"
                continue
            coverage = summary["required_branch_coverage"]
            coverage_ok = all(
                int(item["observed"]) >= int(item["minimum"])
                for item in coverage.values()
            )
            gates = {
                "G01_BRANCH_PAGE_COVERAGE": coverage_ok,
                "G02_NULL_MARGIN": int(summary["delta_vs_null"]) >= 4,
                "G03_EVERY_RIVAL_MARGIN": int(summary["minimum_rival_margin"]) >= 4,
                "G04_ORPHANS_REMOVED": int(summary["resolved_null_orphan_count"]) >= 2,
                "G05_ORPHAN_PAGES": int(summary["resolved_orphan_page_count"]) >= 2,
                "G06_POSITIONAL_BEATS_INVARIANT": (
                    by_candidate[candidate_id][0]["policy_kind"] != "POSITIONAL"
                    or summary["margin_over_best_invariant"] is not None
                    and int(summary["margin_over_best_invariant"]) >= 4
                ),
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": int(summary["minimum_lopo_margin"]) > 0,
                "G08_EXACT_TIE_TO_NULL": list(full.values()).count(full[candidate_id]) == 1
                and full[candidate_id] == min(full.values()),
            }
            summary["gate_passes"] = gates
            gate_results.update({(candidate_id, gate_id): passed for gate_id, passed in gates.items()})
            if not gates["G01_BRANCH_PAGE_COVERAGE"]:
                candidate_dispositions[candidate_id] = "INSUFFICIENT_BRANCH_COVERAGE"
            elif all(gates.values()):
                candidate_dispositions[candidate_id] = "PROVISIONAL_POLICY_WIN"
            else:
                candidate_dispositions[candidate_id] = "OPAQUE_NULL"
    target_decisions: dict[str, dict[str, object]] = {}
    for target in TARGETS:
        winners = [
            candidate_id for candidate_id in decks[target]
            if candidate_dispositions[candidate_id] == "PROVISIONAL_POLICY_WIN"
        ]
        if len(winners) > 1:
            raise AssertionError(f"independent gates produced multiple winners for {target}: {winners}")
        selected = winners[0] if winners else null_by_target[target]
        target_decisions[target] = {
            "target_surface": target,
            "selected_candidate_id": selected,
            "target_disposition": "PROVISIONAL_POLICY_WIN" if winners else "OPAQUE_NULL",
            "undercovered_candidates": tuple(
                candidate_id for candidate_id in decks[target]
                if candidate_dispositions[candidate_id] == "INSUFFICIENT_BRANCH_COVERAGE"
            ),
        }
    return {
        "contexts": contexts,
        "candidate_branches": by_candidate,
        "evaluations": evaluations,
        "summaries": summaries,
        "pages_by_target": pages_by_target,
        "fold_penalties": fold_penalties,
        "gate_results": gate_results,
        "candidate_dispositions": candidate_dispositions,
        "target_decisions": target_decisions,
        "null_by_target": null_by_target,
    }


def validate_sources(check: Callable[[bool, str], None]) -> tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]],
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]],
    dict[str, object], int, int,
]:
    tables: dict[str, list[dict[str, str]]] = {}
    for path, schema in (
        (COHORT_PATH, COHORT_SCHEMA),
        (EXCLUSION_PATH, EXCLUSION_SCHEMA),
        (CANDIDATE_PATH, CANDIDATE_SCHEMA),
        (PENALTY_PATH, PENALTY_SCHEMA),
        (GATE_PATH, GATE_SCHEMA),
        (SLOT_CONSTRAINT_PATH, SLOT_CONSTRAINT_SCHEMA),
    ):
        check(
            sha256(path) == EXPECTED_SOURCE_SHA256[path.name],
            f"preregistered source bytes changed: {path.name}",
        )
        header, rows = read_tsv(path)
        check(header == schema, f"source schema/order changed: {path.name}")
        check(bool(rows), f"empty source table: {path.name}")
        tables[path.name] = rows
    cohort = tables[COHORT_PATH.name]
    exclusions = tables[EXCLUSION_PATH.name]
    candidates = tables[CANDIDATE_PATH.name]
    penalties = tables[PENALTY_PATH.name]
    gates = tables[GATE_PATH.name]
    slot_constraints = tables[SLOT_CONSTRAINT_PATH.name]

    check(len(cohort) == 131, "cohort must contain exactly 131 token rows")
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
    check(
        tuple(sorted(by_line)) == tuple(f"G770-L{number:03d}" for number in range(1, 16)),
        "cohort IDs must be G770-L001..L015",
    )
    check(len({row["locus"] for row in cohort}) == 15, "cohort must contain fifteen loci")
    check(len({row["page"] for row in cohort}) == 15, "cohort must contain fifteen pages")
    check(
        all(not SEALED_PAGE.match(row["page"]) and not SEALED_PAGE.match(row["locus"]) for row in cohort),
        "cohort exposes f84/f84r",
    )
    check(all(row["line_class"] == "MASKED_COHORT_LINE" for row in cohort), "unexpected line class")
    for cohort_id, line in by_line.items():
        ordered = sorted(line, key=lambda row: as_int(row["ordinal"], "ordinal"))
        count = len(ordered)
        check(
            [as_int(row["ordinal"], "ordinal") for row in ordered] == list(range(1, count + 1)),
            f"noncontiguous ordinals: {cohort_id}",
        )
        check(
            {as_int(row["line_token_count"], "line_token_count") for row in ordered} == {count},
            f"line_token_count mismatch: {cohort_id}",
        )
        check(
            len({row["locus"] for row in ordered}) == 1
            and len({row["page"] for row in ordered}) == 1,
            f"line provenance varies: {cohort_id}",
        )
        for target in (row for row in ordered if row["is_target"] == "1"):
            ordinal = as_int(target["ordinal"], "target ordinal")
            for side, index, exact_field, roles_field in (
                ("left", ordinal - 2, "left_neighbor_exact", "left_neighbor_roles"),
                ("right", ordinal, "right_neighbor_exact", "right_neighbor_roles"),
            ):
                neighbor = ordered[index] if 0 <= index < len(ordered) else None
                expected_exact = neighbor is not None and neighbor["reader_exact"] == "1"
                check(
                    target[exact_field] == str(int(expected_exact)),
                    f"{side} neighbor exactness mismatch: {cohort_id}@{ordinal}",
                )
                expected_roles = (
                    neighbor["structural_roles"]
                    if expected_exact and neighbor is not None and neighbor["is_target"] == "0"
                    else "NONE"
                )
                check(
                    target[roles_field] == expected_roles,
                    f"{side} target-facing roles mismatch: {cohort_id}@{ordinal}",
                )
    target_rows = [row for row in cohort if row["is_target"] == "1"]
    non_targets = [row for row in cohort if row["is_target"] == "0"]
    check(len(target_rows) == 17, "cohort must contain seventeen target masks")
    check(Counter(row["surface"] for row in target_rows) == TARGET_COUNTS, "target counts changed")
    check(
        Counter(row["target_mask_id"] for row in target_rows)
        == Counter({TARGET_MASKS[target]: count for target, count in TARGET_COUNTS.items()}),
        "target mask counts changed",
    )
    check(
        all(row["target_mask_id"] == TARGET_MASKS[row["surface"]] for row in target_rows),
        "surface/mask mapping changed",
    )
    check(all(row["scoring_identity"] == row["target_mask_id"] for row in target_rows), "target identity is not opaque")
    check(all(row["reader_exact"] == "1" for row in target_rows), "nonexact scored target")
    check(all(row["frozen_non_target_default_de"] == "" for row in target_rows), "target default leaked")
    check(
        all(row["structural_axes"] == "NONE" and row["structural_roles"] == "NONE" for row in target_rows),
        "target axes/roles leaked",
    )
    check(
        all(row["target_mask_id"] == "NONE" and row["scoring_identity"] == "NON_TARGET" for row in non_targets),
        "non-target mask/scoring identity changed",
    )
    check(sum(row["reader_exact"] == "0" for row in non_targets) == 11, "non-target exactness census changed")
    check(
        all(row["left_neighbor_roles"] == "NONE" and row["right_neighbor_roles"] == "NONE" for row in non_targets),
        "non-target carries target-neighbour roles",
    )
    check(
        all(row["left_neighbor_exact"] == "0" and row["right_neighbor_exact"] == "0" for row in non_targets),
        "non-target carries target-neighbour exactness",
    )
    for row_number, row in enumerate(cohort, 2):
        for field in ZERO_FIELDS & set(COHORT_SCHEMA):
            check(is_zero(row[field]), f"nonzero {field} at cohort row {row_number}")
        check(
            bool(row["surface"] and row["source_artifact"] and row["source_row"] and row["current_provenance"]),
            f"blank provenance at cohort row {row_number}",
        )
        for source in row["source_artifact"].split("|"):
            path = safe_repo_path(source, f"cohort row {row_number}")
            check(path.is_file(), f"missing cohort source: {source}")
            check("f84" not in source.casefold(), f"sealed source path in cohort: {source}")
        if row["is_target"] == "0":
            lowered = row["frozen_non_target_default_de"].casefold()
            check(
                not any(fragment in lowered for fragment in BANNED_RETIRED_LITERAL_FRAGMENTS),
                f"retired literal leaked at cohort row {row_number}",
            )

    span_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cohort:
        if row["span_id"] != "NONE":
            span_groups[row["span_id"]].append(row)
    check(len(span_groups) == 4, "cohort must declare four reader spans")
    target_owned: list[str] = []
    for span_id, rows in span_groups.items():
        ordered = sorted(rows, key=lambda row: as_int(row["ordinal"], "span ordinal"))
        ordinals = [as_int(row["ordinal"], "span ordinal") for row in ordered]
        check(len(rows) == 2 and ordinals[1] == ordinals[0] + 1, f"noncontiguous span: {span_id}")
        check(
            len({(row["cohort_id"], row["locus"], row["page"]) for row in rows}) == 1,
            f"span crosses a source line: {span_id}",
        )
        owners = [row for row in rows if row["span_member_role"] in {"OWNER", "MASKED_OWNER"}]
        consumed = [row for row in rows if row["span_member_role"] == "CONSUMED"]
        check(len(owners) == 1 and len(consumed) == 1, f"span owner contract changed: {span_id}")
        owner_ordinal = as_int(owners[0]["ordinal"], "owner ordinal")
        check(
            all(as_int(row["render_once_owner_ordinal"], "render_once_owner_ordinal") == owner_ordinal for row in rows),
            f"span owner ordinal mismatch: {span_id}",
        )
        check(all(row["reader_exact"] == "1" for row in rows), f"nonexact span: {span_id}")
        if owners[0]["span_member_role"] == "MASKED_OWNER":
            target_owned.append(span_id)
            check(owners[0]["is_target"] == "1" and consumed[0]["is_target"] == "0", f"malformed target-owned span: {span_id}")
        else:
            check(all(row["is_target"] == "0" for row in rows), f"target entered score-collapsed span: {span_id}")
    check(target_owned == ["G770-SPAN-X4P7"], "reader-only target-owned span changed")
    score_node_count = sum(len(build_score_nodes(line)) for line in by_line.values())
    reader_unit_count = sum(row["span_member_role"] != "CONSUMED" for row in cohort)
    check(score_node_count == 128, f"score-node census must be 128, got {score_node_count}")
    check(reader_unit_count == 127, f"reader-unit census must be 127, got {reader_unit_count}")

    target_slots = {
        (row["cohort_id"], as_int(row["ordinal"], "target ordinal")): row["target_mask_id"]
        for row in target_rows
    }
    constraint_slots: dict[tuple[str, int], dict[str, str]] = {}
    check(len(slot_constraints) == 17, "slot constraints must contain seventeen rows")
    for row_number, row in enumerate(slot_constraints, 2):
        key = (row["cohort_id"], as_int(row["ordinal"], "slot ordinal"))
        check(key not in constraint_slots, f"duplicate slot constraint at row {row_number}")
        constraint_slots[key] = row
        check(row["predicate_only_close"] in {"0", "1"}, f"bad predicate flag at slot row {row_number}")
        check(bool(row["provenance"].strip()), f"blank slot provenance at row {row_number}")
    check(set(constraint_slots) == set(target_slots), "slot constraints do not cover target slots exactly")
    for key, row in constraint_slots.items():
        check(row["target_mask_id"] == target_slots[key], f"slot mask mismatch at {key}")
    check(
        all(row["predicate_only_close"] == "0" for row in slot_constraints),
        "unexpected target-independent predicate-only slot",
    )
    predicate_only_close_by_slot = {
        key: row["predicate_only_close"] == "1" for key, row in constraint_slots.items()
    }
    contexts = make_contexts(cohort, predicate_only_close_by_slot)
    check(len(contexts) == 17, "context builder did not return seventeen targets")
    check(sum(len(context.null_orphans) for context in contexts) == 30, "NULL orphan census must be 30")
    check(all(not context.target_slot_roles for context in contexts), "target slot gained a frozen role")

    check(len(exclusions) == 8, "exclusion ledger must contain eight rows")
    check(
        {row["exclusion_id"] for row in exclusions} == {f"G770-X{number:03d}" for number in range(1, 9)},
        "exclusion IDs changed",
    )
    check(all(row["eligible_for_cohort"] == "0" for row in exclusions), "excluded row became eligible")
    check(
        all(not SEALED_PAGE.match(row["page"]) and not SEALED_PAGE.match(row["locus"]) for row in exclusions),
        "exclusion ledger exposes f84/f84r",
    )
    for row_number, row in enumerate(exclusions, 2):
        for field in ZERO_FIELDS & set(EXCLUSION_SCHEMA):
            check(is_zero(row[field]), f"nonzero {field} at exclusion row {row_number}")
        check(row["exclusion_reason"].startswith("REJECT_"), f"bad exclusion disposition at row {row_number}")
        for field in ("source_artifact", "corroborating_artifact"):
            for source in row[field].split("|"):
                path = safe_repo_path(source, f"exclusion row {row_number}")
                check(path.is_file(), f"missing exclusion source: {source}")
                check("f84" not in source.casefold(), f"sealed source path in exclusion ledger: {source}")

    check(len(candidates) == 22, "candidate deck must contain 22 branch rows")
    allowed_policy_classes = {
        "OPAQUE_NULL", "LINKER", "NOMINAL", "RESULT", "OPERATION", "MEASURE", "ENDPOINT",
    }
    allowed_policy_kinds = {"NULL", "POSITIONAL", "INVARIANT"}
    by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_candidate[row["candidate_id"]].append(row)
    check(len(by_candidate) == 18, "candidate deck must contain 18 IDs")
    check(
        Counter(rows[0]["target_surface"] for rows in by_candidate.values())
        == Counter({"ol": 4, "ckhy": 5, "ols": 5, "otar": 4}),
        "candidate target-deck sizes changed",
    )
    for candidate_id, rows in by_candidate.items():
        check(len({row["target_surface"] for row in rows}) == 1, f"candidate crosses targets: {candidate_id}")
        check(len({row["policy_kind"] for row in rows}) == 1, f"candidate crosses kinds: {candidate_id}")
        check(len({row["branch_id"] for row in rows}) == len(rows), f"duplicate branch: {candidate_id}")
        priorities = [as_int(row["branch_priority"], "branch_priority") for row in rows]
        check(sorted(priorities) == list(range(1, len(rows) + 1)), f"bad branch priorities: {candidate_id}")
        else_rows = [row for row in rows if row["branch_condition"] == "ELSE"]
        check(len(else_rows) <= 1, f"multiple ELSE branches: {candidate_id}")
        if else_rows:
            check(as_int(else_rows[0]["branch_priority"], "ELSE priority") == max(priorities), f"ELSE is not last: {candidate_id}")
        for row in rows:
            check(row["target_surface"] in TARGETS, f"unknown target: {candidate_id}")
            check(row["policy_class"] in allowed_policy_classes, f"unknown policy class: {candidate_id}")
            check(row["policy_kind"] in allowed_policy_kinds, f"unknown policy kind: {candidate_id}")
            check(row["candidate_scope"] == "WHOLE_FORM_OCCURRENCE_ONLY", f"scope widened: {candidate_id}")
            check(re.fullmatch(r"[A-Z0-9_]+", row["structural_tag"]) is not None, f"bad structural tag: {candidate_id}")
            check(bool(row["renderer_de"]), f"blank renderer: {candidate_id}")
            for field in (
                "required_left_classes", "required_right_classes",
                "consumes_left_classes", "consumes_right_classes",
            ):
                check(split_set(row[field]) <= ALLOWED_ROLES, f"unknown role in {candidate_id}.{field}")
            check(as_int(row["minimum_branch_pages"], "minimum_branch_pages") >= 0, f"negative branch minimum: {candidate_id}")
            for field in ZERO_FIELDS & set(CANDIDATE_SCHEMA):
                check(is_zero(row[field]), f"nonzero {field} in {candidate_id}/{row['branch_id']}")
            validate_condition_expression(row["branch_condition"])
            validate_edge_expression(row["required_edge_expression"])
    for target in TARGETS:
        deck = [candidate_id for candidate_id, rows in by_candidate.items() if rows[0]["target_surface"] == target]
        baselines = [candidate_id for candidate_id in deck if all(row["opaque_baseline"] == "1" for row in by_candidate[candidate_id])]
        check(len(baselines) == 1, f"target lacks one NULL: {target}")
        baseline = by_candidate[baselines[0]]
        check(len(baseline) == 1 and baseline[0]["policy_kind"] == "NULL" and baseline[0]["policy_class"] == "OPAQUE_NULL", f"malformed NULL: {target}")
        check(
            all(row["opaque_baseline"] == "0" for candidate_id in deck if candidate_id not in baselines for row in by_candidate[candidate_id]),
            f"non-NULL opaque flag: {target}",
        )

    check(
        tuple((row["penalty_id"], as_int(row["weight"], "penalty weight")) for row in penalties)
        == EXPECTED_PENALTIES,
        "penalty IDs/weights/order changed",
    )
    check(
        all(row["score_effect"] == "ADD_TO_PENALTY" and row["fluency_credit"] == "0" for row in penalties),
        "penalty deck gained fluency/non-penalty credit",
    )
    check(
        projection_sha256(penalties, PENALTY_NORMATIVE_FIELDS)
        == EXPECTED_PENALTY_NORMATIVE_SHA256,
        "normative penalty contract hash changed",
    )
    check(tuple(row["gate_id"] for row in gates) == EXPECTED_GATES, "winner gates changed")
    check([as_int(row["evaluation_order"], "gate order") for row in gates] == list(range(1, 9)), "gate order changed")
    gate_contract = {
        "G01_BRANCH_PAGE_COVERAGE": ("GE", "CANDIDATE_MINIMUM_BRANCH_PAGES", "INSUFFICIENT_BRANCH_COVERAGE"),
        "G02_NULL_MARGIN": ("GE", "4", "OPAQUE_NULL"),
        "G03_EVERY_RIVAL_MARGIN": ("GE", "4", "OPAQUE_NULL"),
        "G04_ORPHANS_REMOVED": ("GE", "2", "OPAQUE_NULL"),
        "G05_ORPHAN_PAGES": ("GE", "2", "OPAQUE_NULL"),
        "G06_POSITIONAL_BEATS_INVARIANT": ("GE", "4", "OPAQUE_NULL"),
        "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": ("GT", "0", "OPAQUE_NULL"),
        "G08_EXACT_TIE_TO_NULL": ("EQ", "1", "OPAQUE_NULL"),
    }
    for row in gates:
        check(
            (row["comparator"], row["threshold"], row["failure_disposition"])
            == gate_contract[row["gate_id"]],
            f"gate contract changed: {row['gate_id']}",
        )
    check(
        projection_sha256(gates, GATE_NORMATIVE_FIELDS) == EXPECTED_GATE_NORMATIVE_SHA256,
        "normative gate contract hash changed",
    )
    weights = {row["penalty_id"]: as_int(row["weight"], "penalty weight") for row in penalties}
    core = calculate_core(cohort, candidates, weights, slot_constraints)
    return (
        cohort, exclusions, candidates, penalties, gates, slot_constraints, core,
        score_node_count, reader_unit_count,
    )


def pipe(values: Sequence[object]) -> str:
    return "|".join(str(value) for value in values) or "NONE"


def json_cell(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def node_field(node: Neighbor | None, field: str) -> str:
    if node is None:
        return "NONE"
    value = getattr(node, field)
    if isinstance(value, (set, frozenset, tuple)):
        return pipe(sorted(value))
    return str(value)


def independent_metrics(
    candidates: Sequence[Mapping[str, str]], core: Mapping[str, object]
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
    evaluations: Mapping[str, tuple[Evaluation, ...]] = core["evaluations"]  # type: ignore[assignment]
    fold_penalties: Mapping[tuple[str, str], int] = core["fold_penalties"]  # type: ignore[assignment]
    pages_by_target: Mapping[str, tuple[str, ...]] = core["pages_by_target"]  # type: ignore[assignment]
    null_by_target: Mapping[str, str] = core["null_by_target"]  # type: ignore[assignment]
    by_candidate: Mapping[str, Sequence[Mapping[str, str]]] = core["candidate_branches"]  # type: ignore[assignment]
    order: dict[str, int] = {}
    decks: dict[str, list[str]] = defaultdict(list)
    for index, row in enumerate(candidates):
        order.setdefault(row["candidate_id"], index)
    for candidate_id in sorted(by_candidate, key=order.__getitem__):
        decks[by_candidate[candidate_id][0]["target_surface"]].append(candidate_id)

    metrics: dict[str, dict[str, object]] = {}
    gate_rows: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    for target in TARGETS:
        deck = decks[target]
        null_id = null_by_target[target]
        scores = {candidate_id: int(summaries[candidate_id]["total_penalty"]) for candidate_id in deck}
        minimum = min(scores.values())
        minimum_ids = sorted(candidate_id for candidate_id, score in scores.items() if score == minimum)
        invariant = [
            candidate_id for candidate_id in deck
            if candidate_id != null_id and summaries[candidate_id]["policy_kind"] == "INVARIANT"
        ]
        for candidate_id in deck:
            rivals = {rival: score for rival, score in scores.items() if rival != candidate_id}
            min_rival_margin = min(score - scores[candidate_id] for score in rivals.values())
            coverage = summaries[candidate_id]["required_branch_coverage"]
            coverage_pass = all(
                int(record["observed"]) >= int(record["minimum"])
                for record in coverage.values()  # type: ignore[union-attr]
            )
            position_margin: int | None = None
            if summaries[candidate_id]["policy_kind"] == "POSITIONAL":
                position_margin = min(scores[rival] for rival in invariant) - scores[candidate_id]
            fold_margins: list[int] = []
            for page in pages_by_target[target]:
                candidate_fold = fold_penalties[(candidate_id, page)]
                best_rival_fold = min(
                    fold_penalties[(rival, page)] for rival in deck if rival != candidate_id
                )
                fold_margins.append(best_rival_fold - candidate_fold)
            min_lopo = min(fold_margins)
            tests = {
                "G01_BRANCH_PAGE_COVERAGE": coverage_pass,
                "G02_NULL_MARGIN": scores[null_id] - scores[candidate_id] >= 4,
                "G03_EVERY_RIVAL_MARGIN": min_rival_margin >= 4,
                "G04_ORPHANS_REMOVED": int(summaries[candidate_id]["resolved_null_orphan_count"]) >= 2,
                "G05_ORPHAN_PAGES": int(summaries[candidate_id]["resolved_orphan_page_count"]) >= 2,
                "G06_POSITIONAL_BEATS_INVARIANT": position_margin is None or position_margin >= 4,
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": min_lopo > 0,
                "G08_EXACT_TIE_TO_NULL": minimum_ids == [candidate_id],
            }
            nonnull = candidate_id != null_id
            applicable = {
                "G01_BRANCH_PAGE_COVERAGE": nonnull and bool(coverage),
                "G02_NULL_MARGIN": nonnull,
                "G03_EVERY_RIVAL_MARGIN": nonnull,
                "G04_ORPHANS_REMOVED": nonnull,
                "G05_ORPHAN_PAGES": nonnull,
                "G06_POSITIONAL_BEATS_INVARIANT": nonnull and position_margin is not None,
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": nonnull,
            }
            survives = nonnull and all(
                tests[gate_id] for gate_id, applies in applicable.items() if applies
            )
            # A tied full minimum receives an explicit failing G08 record even
            # though G03 already fails.  Outside that diagnostic tie path,
            # G08 is reached only after gates 1--7 survive.
            applicable["G08_EXACT_TIE_TO_NULL"] = survives or (
                nonnull and candidate_id in minimum_ids and len(minimum_ids) > 1
            )
            failed = tuple(
                gate_id for gate_id in EXPECTED_GATES
                if applicable[gate_id] and not tests[gate_id]
            )
            eligible = survives and tests["G08_EXACT_TIE_TO_NULL"]
            metrics[candidate_id] = {
                "null_candidate_id": null_id,
                "null_penalty": scores[null_id],
                "delta_vs_null": scores[null_id] - scores[candidate_id],
                "min_rival_margin": min_rival_margin,
                "position_margin": position_margin,
                "min_lopo_margin": min_lopo,
                "coverage_pass": coverage_pass,
                "failed_gate_ids": failed,
                "eligible": eligible,
            }
            observed: dict[str, object] = {
                "G01_BRANCH_PAGE_COVERAGE": min(
                    (
                        int(record["observed"])
                        for record in coverage.values()  # type: ignore[union-attr]
                    ),
                    default=0,
                ),
                "G02_NULL_MARGIN": scores[null_id] - scores[candidate_id],
                "G03_EVERY_RIVAL_MARGIN": min_rival_margin,
                "G04_ORPHANS_REMOVED": int(summaries[candidate_id]["resolved_null_orphan_count"]),
                "G05_ORPHAN_PAGES": int(summaries[candidate_id]["resolved_orphan_page_count"]),
                "G06_POSITIONAL_BEATS_INVARIANT": position_margin if position_margin is not None else "NA",
                "G07_ALL_LEAVE_ONE_PAGE_OUT_WINS": min_lopo,
                "G08_EXACT_TIE_TO_NULL": len(minimum_ids) if candidate_id in minimum_ids else "NOT_AT_MINIMUM",
            }
            for evaluation_order, gate_id in enumerate(EXPECTED_GATES, 1):
                applies = applicable[gate_id]
                gate_rows.append(
                    {
                        "target_mask_id": TARGET_MASKS[target],
                        "candidate_id": candidate_id,
                        "gate_id": gate_id,
                        "evaluation_order": evaluation_order,
                        "applicable": int(applies),
                        "observed": observed[gate_id],
                        "pass": int(tests[gate_id]) if applies else "NA",
                        "candidate_disposition": (
                            "OPAQUE_BASELINE" if not nonnull
                            else "NOT_APPLICABLE_OR_NOT_REACHED" if not applies
                            else "CONTINUE" if tests[gate_id]
                            else "INSUFFICIENT_BRANCH_COVERAGE" if gate_id == "G01_BRANCH_PAGE_COVERAGE"
                            else "OPAQUE_NULL"
                        ),
                    }
                )
        winners = [candidate_id for candidate_id in deck if bool(metrics[candidate_id]["eligible"])]
        if len(winners) > 1:
            raise AssertionError(f"multiple independent policy winners for {target}: {winners}")
        raw_lead = minimum_ids[0] if len(minimum_ids) == 1 else "TIE"
        failed = (
            metrics[raw_lead]["failed_gate_ids"]
            if raw_lead != "TIE"
            else tuple(
                gate_id for gate_id in EXPECTED_GATES
                if any(
                    gate_id in metrics[candidate_id]["failed_gate_ids"]
                    for candidate_id in minimum_ids
                )
            )
        )
        decisions.append(
            {
                "surface_provenance_only": target,
                "target_mask_id": TARGET_MASKS[target],
                "formal_decision": winners[0] if winners else null_id,
                "formal_status": "PROVISIONAL_POLICY_WIN" if winners else "OPAQUE_NULL",
                "raw_lead_candidate": raw_lead,
                "raw_minimum_candidates": pipe(minimum_ids),
                "raw_lead_penalty": minimum,
                "null_candidate": null_id,
                "null_penalty": scores[null_id],
                "raw_lead_delta_vs_null": scores[null_id] - scores[raw_lead] if raw_lead != "TIE" else "NA",
                "raw_lead_failed_gates": pipe(failed),
                "lead_disposition": (
                    "INSUFFICIENT_BRANCH_COVERAGE"
                    if "G01_BRANCH_PAGE_COVERAGE" in failed else "OPAQUE_NULL"
                ),
                "policy_winner_count": len(winners),
                "target_surface_visible_to_scorer": 0,
            }
        )
    return metrics, gate_rows, decisions


def compare_rows(
    name: str,
    actual: Sequence[Mapping[str, str]],
    expected: Sequence[Mapping[str, object]],
    key_fields: Sequence[str],
    check: Callable[[bool, str], None],
    ignored_fields: frozenset[str] = frozenset(),
) -> None:
    check(len(actual) == len(expected), f"row count mismatch for {name}: {len(actual)} != {len(expected)}")
    actual_map = {tuple(row[field] for field in key_fields): row for row in actual}
    expected_map = {tuple(str(row[field]) for field in key_fields): row for row in expected}
    check(len(actual_map) == len(actual), f"duplicate key in {name}")
    check(set(actual_map) == set(expected_map), f"key universe mismatch in {name}")
    for key in sorted(expected_map):
        actual_row = actual_map[key]
        expected_row = expected_map[key]
        for field, expected_value in expected_row.items():
            if field in ignored_fields:
                continue
            check(field in actual_row, f"missing {field} in {name}")
            check(actual_row[field] == str(expected_value), f"{name} {key} {field}: {actual_row[field]!r} != {expected_value!r}")


def expected_core_tables(
    cohort: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
    core: Mapping[str, object],
    metrics: Mapping[str, Mapping[str, object]],
    gate_rows: Sequence[Mapping[str, object]],
    decisions: Sequence[Mapping[str, object]],
) -> dict[str, list[dict[str, object]]]:
    contexts: tuple[Context, ...] = core["contexts"]  # type: ignore[assignment]
    evaluations_by_candidate: Mapping[str, tuple[Evaluation, ...]] = core["evaluations"]  # type: ignore[assignment]
    summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
    fold_penalties: Mapping[tuple[str, str], int] = core["fold_penalties"]  # type: ignore[assignment]
    pages_by_target: Mapping[str, tuple[str, ...]] = core["pages_by_target"]  # type: ignore[assignment]
    by_candidate: Mapping[str, Sequence[Mapping[str, str]]] = core["candidate_branches"]  # type: ignore[assignment]
    null_by_target: Mapping[str, str] = core["null_by_target"]  # type: ignore[assignment]
    context_by_id = {context.occurrence_id: context for context in contexts}
    candidate_order: dict[str, int] = {}
    for index, row in enumerate(candidates):
        candidate_order.setdefault(row["candidate_id"], index)
    all_evaluations = [
        evaluation
        for candidate_id in sorted(evaluations_by_candidate, key=candidate_order.__getitem__)
        for evaluation in sorted(
            evaluations_by_candidate[candidate_id],
            key=lambda item: (item.page, item.locus, item.target_ordinal),
        )
    ]

    masked: list[dict[str, object]] = []
    for row in sorted(cohort, key=lambda item: (item["cohort_id"], as_int(item["ordinal"], "ordinal"))):
        target = row["is_target"] == "1"
        masked.append(
            {
                "cohort_id": row["cohort_id"],
                "locus": row["locus"],
                "page": row["page"],
                "ordinal": as_int(row["ordinal"], "ordinal"),
                "masked_surface": f"[{row['target_mask_id']}]" if target else row["surface"],
                "is_target": int(target),
                "scoring_identity": row["scoring_identity"],
                "reader_exact": as_int(row["reader_exact"], "reader_exact"),
                "scorer_visible_roles": "NONE" if target else row["structural_roles"],
                "scorer_visible_axes": "NONE",
                "display_default_de": "[ZIEL VERDECKT]" if target else row["frozen_non_target_default_de"],
                "span_id": row["span_id"],
                "span_member_role": row["span_member_role"],
                "render_once_owner_ordinal": row["render_once_owner_ordinal"],
                "target_surface_visible_to_scorer": 0,
                "old_target_default_role_evidence_confidence_credit": 0,
                "fluency_credit": 0,
                "component_export_credit": 0,
            }
        )

    inventory: list[dict[str, object]] = []
    null_orphans: list[dict[str, object]] = []
    for context in contexts:
        inventory.append(
            {
                "occurrence_id": context.occurrence_id,
                "cohort_id": context.cohort_id,
                "locus": context.locus,
                "page": context.page,
                "ordinal": context.ordinal,
                "target_mask_id": context.target_mask_id,
                "surface_provenance_only": context.target_surface,
                "line_final": int(context.line_final),
                "medial": int(context.medial),
                "left_node_id": node_field(context.left, "node_id"),
                "left_roles": node_field(context.left, "roles"),
                "right_node_id": node_field(context.right, "node_id"),
                "right_roles": node_field(context.right, "roles"),
                "predicate_only_close_independent": int(
                    "PREDICATE_ONLY_CLOSE" in context.target_slot_roles
                ),
                "null_orphan_count": len(context.null_orphans),
                "null_orphan_types": pipe([orphan.orphan_type for orphan in context.null_orphans]),
                "target_surface_visible_to_scorer": 0,
                "old_target_semantic_credit": 0,
            }
        )
        for orphan in context.null_orphans:
            neighbor = context.left if orphan.side == "LEFT" else context.right if orphan.side == "RIGHT" else None
            null_orphans.append(
                {
                    "edge_id": orphan.orphan_id,
                    "occurrence_id": context.occurrence_id,
                    "cohort_id": context.cohort_id,
                    "locus": context.locus,
                    "page": context.page,
                    "target_mask_id": context.target_mask_id,
                    "target_ordinal": context.ordinal,
                    "side": orphan.side,
                    "edge_type": orphan.orphan_type,
                    "neighbor_node_id": node_field(neighbor, "node_id") if orphan.side != "BOTH" else "LEFT_AND_RIGHT",
                    "neighbor_roles": node_field(neighbor, "roles") if orphan.side != "BOTH" else "TWO_TYPED_EXACT_SIDES",
                    "null_penalty": 4,
                    "target_derived": 0,
                }
            )

    occurrence_rows: list[dict[str, object]] = []
    attachment_rows: list[dict[str, object]] = []
    debt_rows: list[dict[str, object]] = []
    penalty_rows: list[dict[str, object]] = []
    for evaluation in all_evaluations:
        occurrence_rows.append(
            {
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
                "consumed_sides": pipe(sorted({edge.side for edge in evaluation.bound_edges})),
                "bound_edge_count": len(evaluation.bound_edges),
                "bound_edge_ids": pipe([edge.edge_id for edge in evaluation.bound_edges]),
                "bound_roles": pipe([edge.role for edge in evaluation.bound_edges]),
                "duplicate_edge_count": len(evaluation.duplicate_edges),
                "duplicate_edge_ids": pipe([edge.edge_id for edge in evaluation.duplicate_edges]),
                "resolved_orphan_count": len(evaluation.resolved_orphans),
                "resolved_orphan_ids": pipe(sorted(evaluation.resolved_orphans)),
                "unresolved_orphan_count": len(evaluation.unresolved_orphans),
                "unresolved_orphan_ids": pipe(sorted(evaluation.unresolved_orphans)),
                "penalty": evaluation.total_penalty,
                "penalty_ids": pipe([event.penalty_id for event in evaluation.penalties]),
                "trigger_codes": pipe([event.trigger_code for event in evaluation.penalties]),
                "fluency_credit": 0,
                "target_surface_credit": 0,
            }
        )
        context = context_by_id[evaluation.occurrence_id]
        if not evaluation.binding_claims:
            attachment_rows.append(
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
                    "edge_id": "NONE", "side": "NONE", "neighbor_ordinal": "NONE",
                    "role": "NONE", "bound": 0, "double_consumption": 0,
                    "binding_status": (
                        "NO_CLAIM_REQUIREMENTS_FAILED"
                        if not evaluation.requirements_hold else "NO_BINDING_CLAIM"
                    ),
                    "distance": "NONE",
                    "target_surface_credit": 0,
                }
            )
        for claim in evaluation.binding_claims:
            edge = claim.edge
            attachment_rows.append(
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
        for orphan in context.null_orphans:
            resolved = orphan.orphan_id in evaluation.resolved_orphans
            debt_rows.append(
                {
                    "candidate_id": evaluation.candidate_id,
                    "occurrence_id": evaluation.occurrence_id,
                    "cohort_id": evaluation.cohort_id,
                    "locus": evaluation.locus,
                    "page": evaluation.page,
                    "target_mask_id": evaluation.target_mask_id,
                    "edge_id": orphan.orphan_id,
                    "edge_type": orphan.orphan_type,
                    "side": orphan.side,
                    "under_null": "OPEN",
                    "candidate_status": "RESOLVED" if resolved else "OPEN",
                    "penalty_id": "NONE" if resolved else "P04_ORPHAN_OR_SOURCELESS_RESULT",
                    "penalty": 0 if resolved else 4,
                    "candidate_created_edge": 0,
                }
            )
        for event_index, event in enumerate(evaluation.penalties, 1):
            penalty_rows.append(
                {
                    "candidate_id": evaluation.candidate_id,
                    "occurrence_id": evaluation.occurrence_id,
                    "cohort_id": evaluation.cohort_id,
                    "locus": evaluation.locus,
                    "page": evaluation.page,
                    "target_mask_id": evaluation.target_mask_id,
                    "event_index": event_index,
                    "penalty_id": event.penalty_id,
                    "trigger_code": event.trigger_code,
                    "edge_id": event.edge_id,
                    "weight": event.weight,
                }
            )

    policy_rows: list[dict[str, object]] = []
    for candidate_id in sorted(
        summaries,
        key=lambda item: (
            TARGET_MASKS[by_candidate[item][0]["target_surface"]],
            int(summaries[item]["total_penalty"]),
            item,
        ),
    ):
        summary = summaries[candidate_id]
        metric = metrics[candidate_id]
        policy_rows.append(
            {
                "target_mask_id": TARGET_MASKS[by_candidate[candidate_id][0]["target_surface"]],
                "candidate_id": candidate_id,
                "policy_kind": summary["policy_kind"],
                "policy_classes": pipe(summary["policy_classes"]),  # type: ignore[arg-type]
                "target_occurrence_count": summary["target_occurrence_count"],
                "target_page_count": summary["target_page_count"],
                "total_penalty": summary["total_penalty"],
                "null_penalty": metric["null_penalty"],
                "delta_vs_null": metric["delta_vs_null"],
                "min_pairwise_rival_margin": metric["min_rival_margin"],
                "resolved_null_orphan_count": summary["resolved_null_orphan_count"],
                "resolved_orphan_page_count": summary["resolved_orphan_page_count"],
                "minimum_leave_one_page_out_margin": metric["min_lopo_margin"],
                "position_margin_over_best_invariant": metric["position_margin"] if metric["position_margin"] is not None else "NA",
                "branch_coverage_pass": int(metric["coverage_pass"]),
                "failed_gate_ids": pipe(metric["failed_gate_ids"]),  # type: ignore[arg-type]
                "eligible_policy_winner": int(bool(metric["eligible"])),
                "penalty_counts": json_cell(summary["penalty_counts"]),
                "trigger_counts": json_cell(summary["trigger_counts"]),
                "fluency_credit": 0,
                "confirmed_lexeme": 0,
            }
        )

    lopo_rows: list[dict[str, object]] = []
    decks: dict[str, list[str]] = defaultdict(list)
    for candidate_id in sorted(by_candidate, key=candidate_order.__getitem__):
        decks[by_candidate[candidate_id][0]["target_surface"]].append(candidate_id)
    for target in TARGETS:
        deck = decks[target]
        null_id = null_by_target[target]
        for held_page in pages_by_target[target]:
            scores = {candidate_id: fold_penalties[(candidate_id, held_page)] for candidate_id in deck}
            minimum = min(scores.values())
            minima = sorted(candidate_id for candidate_id, score in scores.items() if score == minimum)
            for candidate_id in deck:
                best_rival_penalty = min(score for rival, score in scores.items() if rival != candidate_id)
                best_rivals = sorted(
                    rival for rival, score in scores.items()
                    if rival != candidate_id and score == best_rival_penalty
                )
                lopo_rows.append(
                    {
                        "target_mask_id": TARGET_MASKS[target],
                        "held_page": held_page,
                        "candidate_id": candidate_id,
                        "fold_penalty": scores[candidate_id],
                        "null_candidate_id": null_id,
                        "null_fold_penalty": scores[null_id],
                        "delta_vs_null": scores[null_id] - scores[candidate_id],
                        "best_rival_ids": pipe(best_rivals),
                        "best_rival_penalty": best_rival_penalty,
                        "strict_pairwise_margin": best_rival_penalty - scores[candidate_id],
                        "fold_minimum_ids": pipe(minima),
                        "unique_fold_winner": int(minima == [candidate_id]),
                    }
                )

    branch_rows: list[dict[str, object]] = []
    for candidate_id in sorted(by_candidate, key=candidate_order.__getitem__):
        target = by_candidate[candidate_id][0]["target_surface"]
        eval_map = {evaluation.occurrence_id: evaluation for evaluation in evaluations_by_candidate[candidate_id]}
        relevant_contexts = [context for context in contexts if context.target_mask_id == TARGET_MASKS[target]]
        for branch in sorted(by_candidate[candidate_id], key=lambda row: (as_int(row["branch_priority"], "branch priority"), row["branch_id"])):
            selected = [
                eval_map[context.occurrence_id] for context in relevant_contexts
                if eval_map[context.occurrence_id].branch_id == branch["branch_id"]
            ]
            qualified = [evaluation for evaluation in selected if evaluation.requirements_hold]
            pages = sorted({evaluation.page for evaluation in qualified})
            minimum = as_int(branch["minimum_branch_pages"], "minimum_branch_pages")
            branch_rows.append(
                {
                    "target_mask_id": TARGET_MASKS[target],
                    "candidate_id": candidate_id,
                    "policy_kind": branch["policy_kind"],
                    "policy_class": branch["policy_class"],
                    "branch_id": branch["branch_id"],
                    "branch_priority": branch["branch_priority"],
                    "branch_condition": branch["branch_condition"],
                    "selected_occurrence_count": len(selected),
                    "qualified_occurrence_count": len(qualified),
                    "qualified_page_count": len(pages),
                    "qualified_pages": pipe(pages),
                    "minimum_branch_pages": minimum,
                    "coverage_pass": int(minimum == 0 or len(pages) >= minimum),
                }
            )
    return {
        "MASKED_COHORT_15_LINE_ATLAS.tsv": masked,
        "TARGET_17_OCCURRENCE_INVENTORY.tsv": inventory,
        "NULL_ORPHAN_EDGE_ATLAS.tsv": null_orphans,
        "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv": occurrence_rows,
        "ATTACHMENT_EDGE_ATLAS.tsv": attachment_rows,
        "ORPHAN_DEBT_ATLAS.tsv": debt_rows,
        "PENALTY_EVENT_ATLAS.tsv": penalty_rows,
        "TARGET_POLICY_SCOREBOARD.tsv": policy_rows,
        "LEAVE_ONE_PAGE_OUT.tsv": lopo_rows,
        "BRANCH_COVERAGE.tsv": branch_rows,
        "WINNER_GATE_AUDIT.tsv": [dict(row) for row in gate_rows],
        "TARGET_DECISIONS.tsv": [dict(row) for row in decisions],
    }


def expected_presentation(
    cohort: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
    core: Mapping[str, object],
    metrics: Mapping[str, Mapping[str, object]],
    decisions: Sequence[Mapping[str, object]],
) -> tuple[
    list[dict[str, object]], list[dict[str, object]],
    list[dict[str, object]], str,
]:
    contexts: tuple[Context, ...] = core["contexts"]  # type: ignore[assignment]
    evaluations: Mapping[str, tuple[Evaluation, ...]] = core["evaluations"]  # type: ignore[assignment]
    summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
    by_candidate: Mapping[str, Sequence[Mapping[str, str]]] = core["candidate_branches"]  # type: ignore[assignment]
    context_by_key = {(context.cohort_id, context.ordinal): context for context in contexts}
    decision_by_mask = {str(row["target_mask_id"]): row for row in decisions}
    candidate_order: dict[str, int] = {}
    for index, row in enumerate(candidates):
        candidate_order.setdefault(row["candidate_id"], index)

    by_occurrence: dict[str, list[Evaluation]] = defaultdict(list)
    for candidate_id, items in evaluations.items():
        if candidate_id.endswith("_NULL"):
            continue
        for evaluation in items:
            by_occurrence[evaluation.occurrence_id].append(evaluation)
    local_displays: dict[str, tuple[Evaluation, ...]] = {}
    for occurrence_id, items in by_occurrence.items():
        legal = [item for item in items if item.branch_condition_holds and item.requirements_hold]
        pool = legal or [item for item in items if item.branch_condition_holds]
        if not pool:
            raise AssertionError(f"no independent local display for {occurrence_id}")
        minimum = min(item.total_penalty for item in pool)
        local_displays[occurrence_id] = tuple(
            sorted(
                (item for item in pool if item.total_penalty == minimum),
                key=lambda item: item.candidate_id,
            )
        )

    dictionary: list[dict[str, object]] = []
    for target in sorted(TARGETS):
        mask = TARGET_MASKS[target]
        decision = decision_by_mask[mask]
        lead = str(decision["raw_lead_candidate"])
        policy_ids = (
            str(decision["raw_minimum_candidates"]).split("|")
            if lead == "TIE" else [lead]
        )
        display_policy_ids = [candidate_id for candidate_id in policy_ids if not candidate_id.endswith("_NULL")]
        if not display_policy_ids:
            display_policy_ids = policy_ids
        renderers: list[str] = []
        tags: list[str] = []
        for candidate_id in display_policy_ids:
            for branch in sorted(
                by_candidate[candidate_id],
                key=lambda row: as_int(row["branch_priority"], "branch priority"),
            ):
                if branch["renderer_de"] not in renderers:
                    renderers.append(branch["renderer_de"])
                if branch["structural_tag"] not in tags:
                    tags.append(branch["structural_tag"])
        if lead == "TIE":
            score = as_int(str(decision["raw_lead_penalty"]), "raw lead penalty")
            null_penalty = as_int(str(decision["null_penalty"]), "null penalty")
            delta = null_penalty - score
            resolved_count = max(int(summaries[item]["resolved_null_orphan_count"]) for item in policy_ids)
            resolved_pages = max(int(summaries[item]["resolved_orphan_page_count"]) for item in policy_ids)
            failed = tuple(str(decision["raw_lead_failed_gates"]).split("|"))
            min_lopo = min(int(metrics[item]["min_lopo_margin"]) for item in policy_ids)
            exploratory = False
        else:
            summary = summaries[lead]
            metric = metrics[lead]
            score = int(summary["total_penalty"])
            null_penalty = int(metric["null_penalty"])
            delta = int(metric["delta_vs_null"])
            resolved_count = int(summary["resolved_null_orphan_count"])
            resolved_pages = int(summary["resolved_orphan_page_count"])
            failed = metric["failed_gate_ids"]  # type: ignore[assignment]
            min_lopo = int(metric["min_lopo_margin"])
            exploratory = int(metric["min_rival_margin"]) >= 4 and resolved_pages >= 2
        formal_win = decision["formal_status"] == "PROVISIONAL_POLICY_WIN"
        confidence = (
            "C1_PROVISIONAL_POLICY__C0_LEXEME" if formal_win
            else "C0_FORMAL__C1_EXPLORATORY_STRUCTURAL_LEAD__C0_LEXEME" if exploratory
            else "C0_FORMAL__C0_CLOSE_OR_UNSTABLE_LEAD__C0_LEXEME"
        )
        concrete_reader_defaults = {
            "ckhy": "mischen",
            "ol": "unbelegter linker Mengenzweig [aus?]; vor einer Mengenangabe mit; sonst und",
            "ols": "fertige Zubereitung",
            "otar": "Zwischenzubereitung (knapper Rivale: dann)",
        }
        dictionary.append(
            {
                "surface": target,
                "target_mask_id": mask,
                "formal_target_default": "OPAQUE_NULL",
                "best_replaceable_policy": "|".join(policy_ids),
                "structural_tags": "|".join(tags),
                "policy_renderer_de": "; sonst ".join(renderers),
                "concrete_default_de": concrete_reader_defaults[target],
                "confidence": confidence,
                "formal_policy_confidence": "C1_PROVISIONAL" if formal_win else "C0",
                "lexeme_confidence": "C0",
                "evidence": (
                    f"Strafe {score} gegen NULL {null_penalty}; Delta {delta}; "
                    f"bis zu {resolved_count} Nullwaisen auf {resolved_pages} Seiten gebunden."
                ),
                "counterevidence": (
                    f"{'Provisorischer Policy-Gewinn' if formal_win else 'Kein formaler Policy-Gewinn'}; "
                    f"gescheiterte Gates: {'|'.join(failed) or 'NONE'}; "
                    f"schlechteste Leave-one-page-out-Marge {min_lopo}."
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

    by_line: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
    reader: list[dict[str, object]] = []
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

    def editorial_realization(
        selected: Sequence[Evaluation], context: Context
    ) -> tuple[str, str, str]:
        def one(evaluation: Evaluation) -> tuple[str, str]:
            renderer = evaluation.renderer_de
            fixed = {
                "Fertigprodukt/Colatura": ("fertige Zubereitung", "COLATURA_NOT_LOCALLY_IDENTIFIED"),
                "Übergangs-/Zubereitungsfeld": ("Zwischenzubereitung", "CONCRETE_NOMINAL_REALIZATION"),
                "weiter/dann": ("dann", "CONCRETE_SEQUENCE_REALIZATION"),
                "Ansatz/Basis": ("Grundansatz", "CONCRETE_NOMINAL_REALIZATION"),
                "Infusion/Dekokt": ("Aufguss oder Abkochung", "LEXICAL_ALTERNATIVE_RETAINED"),
                "Maß/Dosis": ("Dosis", "CONCRETE_MEASURE_REALIZATION"),
                "messbares Produkt/Resultat": ("abgemessene Zubereitung", "CONCRETE_RESULT_REALIZATION"),
                "von/aus": ("aus", "CONCRETE_RELATOR_REALIZATION"),
            }
            if renderer in fixed:
                return fixed[renderer]
            if renderer == "und/mit":
                if context.right is not None and context.right.roles & {"AMOUNT", "VALUE"}:
                    return "mit", "RELATOR_BY_RIGHT_QUANTITY"
                return "und", "RELATOR_BY_NONQUANTITY_NEIGHBOURS"
            return renderer, "POLICY_RENDERER_UNCHANGED"

        realizations = [one(item) for item in selected]
        texts = list(dict.fromkeys(text for text, _rule in realizations))
        rules = list(dict.fromkeys(rule for _text, rule in realizations))
        conservative_side_count = min(
            len({edge.side for edge in item.bound_edges}) for item in selected
        )
        support = "A" if conservative_side_count == 2 else "B" if conservative_side_count == 1 else "C"
        text = " oder ".join(texts)
        if len(selected) > 1 or len(texts) > 1 or support == "C":
            text = f"[{text}?]"
        return text, support, "|".join(rules)

    def join_units(units: Sequence[str]) -> str:
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

    for cohort_id in sorted(by_line):
        rows = sorted(by_line[cohort_id], key=lambda row: as_int(row["ordinal"], "ordinal"))
        tokens = [row["surface"] for row in rows]
        masked = [f"[{row['target_mask_id']}]" if row["is_target"] == "1" else row["surface"] for row in rows]
        units: list[str] = []
        dispatches: list[str] = []
        consumed: set[int] = set()
        covered: list[int] = []
        for row in rows:
            ordinal = as_int(row["ordinal"], "ordinal")
            if row["span_member_role"] == "CONSUMED":
                consumed.add(ordinal)
                continue
            member_rows = (
                sorted(
                    (item for item in rows if item["span_id"] == row["span_id"]),
                    key=lambda item: as_int(item["ordinal"], "span ordinal"),
                )
                if row["span_id"] != "NONE" else [row]
            )
            member_ordinals = [as_int(item["ordinal"], "member ordinal") for item in member_rows]
            member_surfaces = [item["surface"] for item in member_rows]
            target_occurrence_id = "NONE"
            policy_ids = "NONE"
            support_grade = "NA"
            editorial_rule = "FROZEN_NON_TARGET_DEFAULT"
            if row["is_target"] == "1":
                context = context_by_key[(cohort_id, ordinal)]
                selected = local_displays[context.occurrence_id]
                text, support_grade, editorial_rule = editorial_realization(selected, context)
                if row["span_member_role"] == "MASKED_OWNER":
                    member = next(
                        item for item in rows
                        if item["span_id"] == row["span_id"] and item["span_member_role"] == "CONSUMED"
                    )
                    text = f"{text}, {member['frozen_non_target_default_de']}"
                units.append(text)
                raw_lead = str(decision_by_mask[context.target_mask_id]["raw_lead_candidate"])
                selected_ids = [item.candidate_id for item in selected]
                policy_ids = "|".join(selected_ids)
                target_occurrence_id = context.occurrence_id
                mode = (
                    "RAW_LEAD_LOCAL_MINIMUM" if selected_ids == [raw_lead]
                    else "TIED_LOCAL_MINIMUM" if len(selected_ids) > 1
                    else "LOCAL_LEGAL_FALLBACK"
                )
                dispatches.append(
                    f"{ordinal}:{context.target_surface}={text}"
                    f"<{policy_ids}:{mode}:support-{support_grade}>"
                )
            else:
                text = row["frozen_non_target_default_de"]
                if not text or text == "NONE":
                    raise AssertionError(f"non-target lacks display at {cohort_id}:{ordinal}")
                units.append(text)
            unit_index = len(units)
            covered.extend(member_ordinals)
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
        working_reader = join_units(units)
        reader.append(
            {
                "cohort_id": cohort_id,
                "locus": rows[0]["locus"],
                "page": rows[0]["page"],
                "token_count": len(rows),
                "practical_unit_count": len(units),
                "manuscript_line": " ".join(tokens),
                "simultaneously_masked_line": " ".join(masked),
                "target_count": sum(row["is_target"] == "1" for row in rows),
                "target_dispatches": " | ".join(dispatches),
                "practical_units_de": " | ".join(units),
                "concrete_working_reader_de": working_reader,
                "every_token_consumed_once": 1,
                "formal_translation_claim": 0,
            }
        )
        markdown.extend(
            [
                f"## {rows[0]['locus']}",
                "",
                f"- Manuscript line: `{' '.join(tokens)}`",
                f"- Masked line: `{' '.join(masked)}`",
                f"- Working reader: {working_reader}",
                f"- Target dispatch: {'; '.join(dispatches)}",
                "",
            ]
        )
        if len(units) != len(rows) - len(consumed):
            raise AssertionError(f"independent reader coverage failure: {cohort_id}")
        if sorted(covered) != list(range(1, len(rows) + 1)) or len(covered) != len(set(covered)):
            raise AssertionError(f"independent reader membership failure: {cohort_id}")
        token_total += len(rows)
        unit_total += len(units)
    if token_total != 131 or unit_total != 127:
        raise AssertionError(f"independent reader totals changed: {token_total}/{unit_total}")
    if len(consumption) != 127 or sum(int(row["member_count"]) for row in consumption) != 131:
        raise AssertionError("independent reader consumption is not 127 units over 131 tokens")
    return dictionary, reader, consumption, "\n".join(markdown).rstrip() + "\n"


def validate_artifacts(
    artifact_dir: Path,
    cohort: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
    penalties: Sequence[Mapping[str, str]],
    gates: Sequence[Mapping[str, str]],
    slot_constraints: Sequence[Mapping[str, str]],
    core: Mapping[str, object],
    declared: Sequence[str],
    check: Callable[[bool, str], None],
) -> tuple[dict[str, Mapping[str, object]], dict[str, object]]:
    metrics, gate_rows, decisions = independent_metrics(candidates, core)
    expected = expected_core_tables(cohort, candidates, core, metrics, gate_rows, decisions)
    dictionary, reader, reader_consumption, markdown = expected_presentation(
        cohort, candidates, core, metrics, decisions
    )
    expected["GDT770_4_WORKING_DICTIONARY.tsv"] = dictionary
    expected["FIFTEEN_COMPLETE_LINE_READER.tsv"] = reader
    expected["READER_UNIT_CONSUMPTION.tsv"] = reader_consumption

    key_fields = {
        "MASKED_COHORT_15_LINE_ATLAS.tsv": ("cohort_id", "ordinal"),
        "TARGET_17_OCCURRENCE_INVENTORY.tsv": ("occurrence_id",),
        "NULL_ORPHAN_EDGE_ATLAS.tsv": ("edge_id",),
        "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv": ("candidate_id", "occurrence_id"),
        "ATTACHMENT_EDGE_ATLAS.tsv": ("candidate_id", "occurrence_id", "claim_index"),
        "ORPHAN_DEBT_ATLAS.tsv": ("candidate_id", "occurrence_id", "edge_id"),
        "PENALTY_EVENT_ATLAS.tsv": ("candidate_id", "occurrence_id", "event_index"),
        "TARGET_POLICY_SCOREBOARD.tsv": ("candidate_id",),
        "LEAVE_ONE_PAGE_OUT.tsv": ("candidate_id", "held_page"),
        "BRANCH_COVERAGE.tsv": ("candidate_id", "branch_id"),
        "WINNER_GATE_AUDIT.tsv": ("candidate_id", "gate_id"),
        "TARGET_DECISIONS.tsv": ("target_mask_id",),
        "GDT770_4_WORKING_DICTIONARY.tsv": ("surface",),
        "FIFTEEN_COMPLETE_LINE_READER.tsv": ("cohort_id",),
        "READER_UNIT_CONSUMPTION.tsv": ("unit_id",),
    }
    actual_tables: dict[str, Mapping[str, object]] = {}
    for name in declared:
        path = artifact_dir / name
        check(path.is_file(), f"declared artifact missing: {name}")
        check(path.stat().st_size > 0, f"declared artifact empty: {name}")
        if not name.endswith(".tsv"):
            continue
        header, rows = read_tsv(path)
        check(header == ARTIFACT_SCHEMAS[name], f"artifact schema/order changed: {name}")
        for row_number, row in enumerate(rows, 2):
            for field in header:
                lowered = field.casefold()
                if lowered in ZERO_FIELDS or lowered.startswith("confirmed_"):
                    check(is_zero(row[field]), f"nonzero claim {name}:{row_number}.{field}")
                if lowered in {
                    "target_surface_credit", "target_surface_visible_to_scorer",
                    "old_target_semantic_credit",
                    "old_target_default_role_evidence_confidence_credit",
                    "target_derived", "candidate_created_edge", "formal_translation_claim",
                    "score_credit",
                }:
                    check(is_zero(row[field]), f"score leak {name}:{row_number}.{field}")
        ignored = frozenset({"note"}) if name == "PENALTY_EVENT_ATLAS.tsv" else frozenset()
        compare_rows(name, rows, expected[name], key_fields[name], check, ignored)
        if name == "PENALTY_EVENT_ATLAS.tsv":
            check(all(row["note"].strip() for row in rows), "blank penalty-event note")
        actual_tables[name] = {"header": header, "rows": rows}

    markdown_actual = (artifact_dir / "GDT770_CONCRETE_READER.md").read_text(encoding="utf-8")
    check(markdown_actual == markdown, "concrete reader markdown differs from independent reconstruction")
    check(markdown_actual.count("## f") == 15, "concrete reader does not contain fifteen loci")
    check("not a recovered plaintext" in markdown_actual, "concrete reader omits plaintext caveat")

    result = json.loads((artifact_dir / "RESULT.json").read_text(encoding="utf-8"))
    check(isinstance(result, Mapping), "RESULT.json is not an object")
    check(
        set(result) == {
            "claim_ceiling", "counts", "experiment_id", "outputs", "question",
            "scope", "score_contract", "status", "target_results",
        },
        "RESULT top-level schema changed",
    )
    recursive_zero_checks(result, check, "RESULT.json")
    check(result.get("experiment_id") == "GDT770", "RESULT experiment ID changed")
    check(tuple(result.get("outputs", ())) == tuple(declared), "RESULT output contract differs from OUTPUT_NAMES")
    counts = result.get("counts")
    check(isinstance(counts, Mapping), "RESULT counts missing")
    contexts: tuple[Context, ...] = core["contexts"]  # type: ignore[assignment]
    evaluations: Mapping[str, tuple[Evaluation, ...]] = core["evaluations"]  # type: ignore[assignment]
    expected_counts = {
        "line_count": 15,
        "token_count": len(cohort),
        "score_node_count": 128,
        "target_count": len(contexts),
        "target_counts": dict(sorted(TARGET_COUNTS.items())),
        "reader_exact_token_count": sum(row["reader_exact"] == "1" for row in cohort),
        "nonexact_nontarget_count": sum(row["reader_exact"] == "0" for row in cohort),
        "span_count": len({row["span_id"] for row in cohort if row["span_id"] != "NONE"}),
        "target_owned_reader_span_count": 1,
        "practical_unit_count": 127,
        "candidate_count": len(evaluations),
        "candidate_branch_count": len(candidates),
        "exclusion_count": 8,
        "target_context_count": len(contexts),
        "null_orphan_edge_count": sum(len(context.null_orphans) for context in contexts),
        "candidate_occurrence_evaluation_count": sum(len(items) for items in evaluations.values()),
        "leave_one_page_out_row_count": len(expected["LEAVE_ONE_PAGE_OUT.tsv"]),
        "branch_coverage_row_count": len(expected["BRANCH_COVERAGE.tsv"]),
        "winner_gate_row_count": len(expected["WINNER_GATE_AUDIT.tsv"]),
        "policy_winner_count": sum(bool(metric["eligible"]) for metric in metrics.values()),
        "dictionary_default_count": len(dictionary),
        "reader_line_count": len(reader),
        "reader_unit_consumption_count": len(reader_consumption),
        "predicate_only_close_slot_count": sum(
            row["predicate_only_close"] == "1" for row in slot_constraints
        ),
        "penalty_normative_sha256": projection_sha256(
            penalties, PENALTY_NORMATIVE_FIELDS
        ),
        "winner_gate_normative_sha256": projection_sha256(
            gates, GATE_NORMATIVE_FIELDS
        ),
    }
    for field, value in expected_counts.items():
        check(counts.get(field) == value, f"RESULT count mismatch for {field}: {counts.get(field)!r} != {value!r}")
    check(set(counts) == set(expected_counts), "RESULT count schema changed")

    expected_target_results: dict[str, dict[str, object]] = {}
    for decision in decisions:
        target = str(decision["surface_provenance_only"])
        expected_target_results[target] = {
            "target_mask_id": decision["target_mask_id"],
            "formal_decision": decision["formal_decision"],
            "formal_status": decision["formal_status"],
            "raw_lead_candidate": decision["raw_lead_candidate"],
            "raw_lead_penalty": decision["raw_lead_penalty"],
            "null_penalty": decision["null_penalty"],
            "raw_lead_delta_vs_null": decision["raw_lead_delta_vs_null"],
            "failed_gates": str(decision["raw_lead_failed_gates"]).split("|"),
            "lead_disposition": decision["lead_disposition"],
        }
    check(result.get("target_results") == expected_target_results, "RESULT target_results differ from independent gates")
    check(set(expected_target_results) == set(TARGETS), "independent target result universe changed")
    score_contract = result.get("score_contract")
    check(isinstance(score_contract, Mapping), "RESULT score contract missing")
    check(
        set(score_contract) == {
            "target_identity_seen_by_scorer", "neighbor_radius",
            "skip_untyped_or_nonexact_neighbor", "fluency_credit",
            "old_target_default_role_evidence_confidence_credit",
            "target_surface_score_credit", "orphan_priority", "orphan_types",
            "penalty_weights", "resampling_unit", "penalty_normative_sha256",
            "winner_gate_normative_sha256", "predicate_only_close_slot_count",
        },
        "RESULT score-contract schema changed",
    )
    check(
        score_contract.get("target_identity_seen_by_scorer") == "opaque target_mask_id only",
        "RESULT scorer sees a nonopaque target identity",
    )
    check(score_contract.get("neighbor_radius") == 1, "RESULT widened neighbor radius")
    check(score_contract.get("skip_untyped_or_nonexact_neighbor") is False, "RESULT permits neighbor hopping")
    check(score_contract.get("fluency_credit") == 0, "RESULT gives fluency credit")
    check(score_contract.get("target_surface_score_credit") == 0, "RESULT gives target surface credit")
    check(score_contract.get("old_target_default_role_evidence_confidence_credit") == 0, "RESULT gives old target credit")
    check(
        score_contract.get("penalty_normative_sha256")
        == projection_sha256(penalties, PENALTY_NORMATIVE_FIELDS),
        "RESULT penalty normative hash changed",
    )
    check(
        score_contract.get("winner_gate_normative_sha256")
        == projection_sha256(gates, GATE_NORMATIVE_FIELDS),
        "RESULT gate normative hash changed",
    )
    check(
        score_contract.get("predicate_only_close_slot_count")
        == sum(row["predicate_only_close"] == "1" for row in slot_constraints),
        "RESULT predicate-only slot count changed",
    )
    check(
        score_contract.get("penalty_weights")
        == {row["penalty_id"]: as_int(row["weight"], "penalty weight") for row in penalties},
        "RESULT penalty weights changed",
    )
    check(score_contract.get("orphan_priority") == ["AMOUNT", "VALUE", "PATIENT", "RESULT"], "RESULT orphan priority changed")
    check(score_contract.get("orphan_types") == ["AMOUNT", "FIELD_EDGE", "PATIENT", "RESULT", "VALUE"], "RESULT orphan types changed")
    check(score_contract.get("resampling_unit") == "page", "RESULT resampling unit changed")
    scope = result.get("scope")
    check(isinstance(scope, Mapping), "RESULT scope missing")
    check(
        set(scope) == {
            "new_page_opened", "new_image_opened", "new_transcription_opened",
            "f84_accessed", "f84r_accessed", "source_scope",
        },
        "RESULT scope schema changed",
    )
    for field in ("new_page_opened", "new_image_opened", "new_transcription_opened", "f84_accessed", "f84r_accessed"):
        check(scope.get(field) is False, f"RESULT scope violation: {field}")
    check(
        scope.get("source_scope") == "fifteen already admitted complete-reader lines",
        "RESULT source scope changed",
    )
    check(
        result.get("claim_ceiling") == {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "confirmed_translations": 0,
            "component_export_credit": 0,
            "eva_latin_credit": 0,
            "defaults_are_replaceable": True,
        },
        "RESULT claim ceiling changed",
    )
    winner_count = sum(
        decision["formal_status"] == "PROVISIONAL_POLICY_WIN" for decision in decisions
    )
    undercovered_count = sum(
        decision["lead_disposition"] == "INSUFFICIENT_BRANCH_COVERAGE"
        for decision in decisions
    )
    expected_status = (
        "PARTIAL__15_LINES_131_TOKENS_128_SCORE_NODES_127_READER_UNITS__"
        f"17_TARGET_MASKS__{winner_count}_POLICY_WINS__"
        f"{undercovered_count}_RAW_LEADS_BRANCH_INSUFFICIENT__"
        "4_CONCRETE_REPLACEABLE_DEFAULTS__"
        "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
    )
    check(result.get("status") == expected_status, "RESULT status differs from independently derived census")
    return actual_tables, dict(result)


def validate_manifest(
    artifact_dir: Path,
    declared: Sequence[str],
    check: Callable[[bool, str], None],
) -> dict[str, object]:
    """Validate release metadata without opening any mixed-source manifest input."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    check(isinstance(manifest, Mapping), "experiment.json is not an object")
    check(manifest.get("schema_version") == 1, "manifest schema_version changed")
    check(manifest.get("experiment_id") == "GDT770", "manifest experiment ID changed")
    check(
        manifest.get("slug") == "target_masked_valency_orphan_tournament",
        "manifest slug changed",
    )
    check(
        manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "manifest must explicitly forbid f84 and f84r",
    )
    commands = manifest.get("commands")
    check(isinstance(commands, Mapping), "manifest commands missing")
    run_command = str(commands.get("run", ""))
    validate_command = str(commands.get("validate", ""))
    check("src/run.py" in run_command, "manifest run command does not invoke run.py")
    check("src/validate.py" in validate_command, "manifest validate command does not invoke validate.py")
    check("--output-dir" not in run_command, "manifest retains obsolete --output-dir CLI")

    def entries(field: str) -> tuple[Mapping[str, object], ...]:
        raw = manifest.get(field)
        check(isinstance(raw, list), f"manifest {field} is not a list")
        parsed: list[Mapping[str, object]] = []
        paths: list[str] = []
        for index, item in enumerate(raw):
            check(isinstance(item, Mapping), f"manifest {field}[{index}] is not an object")
            check(set(item) == {"path", "role", "sha256"}, f"manifest {field}[{index}] schema changed")
            value = str(item.get("path", ""))
            role = str(item.get("role", ""))
            digest = str(item.get("sha256", ""))
            path = safe_repo_path(value, f"manifest {field}[{index}]")
            check(bool(role.strip()), f"manifest {field}[{index}] has blank role")
            check(SHA256.fullmatch(digest) is not None, f"manifest {field}[{index}] has bad SHA-256")
            check(path.is_file(), f"manifest {field} path is missing: {value}")
            check("f84" not in value.casefold(), f"manifest {field} names forbidden f84 material")
            paths.append(value)
            parsed.append(item)
        check(len(paths) == len(set(paths)), f"manifest {field} contains duplicate paths")
        return tuple(parsed)

    inputs = entries("inputs")
    outputs = entries("outputs")
    # Inputs can be mixed-source TSVs.  Their sealed digest is checked by the
    # repository harness; this validator deliberately does not materialise them.
    for item in outputs:
        path = safe_repo_path(str(item["path"]), "manifest output")
        check(sha256(path) == item["sha256"], f"manifest output hash mismatch: {item['path']}")

    experiment_prefix = EXP.relative_to(ROOT).as_posix()
    required_artifacts = {
        f"{experiment_prefix}/artifacts/{name}" for name in declared
    }
    output_paths = {str(item["path"]) for item in outputs}
    if outputs:
        check(
            required_artifacts <= output_paths,
            "manifest outputs do not seal every literal OUTPUT_NAMES artifact",
        )
        required_sources = {
            f"{experiment_prefix}/METHOD.md",
            f"{experiment_prefix}/PREREGISTRATION.md",
            f"{experiment_prefix}/src/COHORT_15_LINE_SPECS.tsv",
            f"{experiment_prefix}/src/COHORT_EXCLUSION_LEDGER.tsv",
            f"{experiment_prefix}/src/CANDIDATE_POLICY_SPECS.tsv",
            f"{experiment_prefix}/src/PENALTY_SPECS.tsv",
            f"{experiment_prefix}/src/WINNER_GATE_SPECS.tsv",
            f"{experiment_prefix}/src/TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv",
            f"{experiment_prefix}/src/run.py",
            f"{experiment_prefix}/src/validate.py",
        }
        check(required_sources <= output_paths, "manifest omits a required GDT770 source or method file")
        check(bool(str(manifest.get("question", "")).strip()), "released manifest question is blank")
        check(bool(str(manifest.get("claim_ceiling", "")).strip()), "released manifest claim ceiling is blank")
    else:
        check(
            manifest.get("status") == "REGISTERED_UNSCORED",
            "only a REGISTERED_UNSCORED manifest may have no sealed outputs",
        )

    validation = manifest.get("validation")
    check(isinstance(validation, Mapping), "manifest validation block missing")
    if validation.get("artifact") is not None:
        check(
            validation.get("artifact")
            == f"{experiment_prefix}/artifacts/VALIDATION.json",
            "manifest validation artifact path changed",
        )
    return {
        "input_count": len(inputs),
        "output_count": len(outputs),
        "outputs_sealed": bool(outputs),
        "sealed_data": dict(manifest["sealed_data"]),
    }


def scoring_signature(
    candidates: Sequence[Mapping[str, str]], core: Mapping[str, object]
) -> str:
    """Canonical score-only digest used for a display-field mutation test."""
    evaluations: Mapping[str, tuple[Evaluation, ...]] = core["evaluations"]  # type: ignore[assignment]
    summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
    metrics, gates, decisions = independent_metrics(candidates, core)
    evaluation_rows: list[object] = []
    for candidate_id in sorted(evaluations):
        for item in sorted(evaluations[candidate_id], key=lambda value: value.occurrence_id):
            evaluation_rows.append(
                (
                    candidate_id, item.occurrence_id, item.target_mask_id, item.branch_id,
                    item.policy_class, item.policy_kind, item.branch_condition_holds,
                    item.requirements_hold,
                    tuple(
                        (
                            claim.claim_index, claim.binding_stage, claim.source_expression,
                            claim.edge.edge_id, claim.edge.side, claim.edge.neighbor_ordinal,
                            claim.edge.role, claim.bound, claim.double_consumption,
                        )
                        for claim in item.binding_claims
                    ),
                    tuple(edge.edge_id for edge in item.bound_edges),
                    tuple(edge.edge_id for edge in item.duplicate_edges),
                    tuple(sorted(item.resolved_orphans)),
                    tuple(sorted(item.unresolved_orphans)),
                    tuple(
                        (event.penalty_id, event.trigger_code, event.weight, event.edge_id)
                        for event in item.penalties
                    ),
                    item.total_penalty,
                )
            )
    summary_rows = [
        (
            candidate_id,
            summaries[candidate_id]["total_penalty"],
            summaries[candidate_id]["penalty_counts"],
            summaries[candidate_id]["trigger_counts"],
            summaries[candidate_id]["resolved_null_orphan_ids"],
            summaries[candidate_id]["resolved_orphan_pages"],
            summaries[candidate_id]["required_branch_coverage"],
        )
        for candidate_id in sorted(summaries)
    ]
    metric_rows = [
        (candidate_id, metrics[candidate_id]) for candidate_id in sorted(metrics)
    ]
    decision_rows = [
        {key: value for key, value in decision.items() if key != "surface_provenance_only"}
        for decision in sorted(decisions, key=lambda row: str(row["target_mask_id"]))
    ]
    payload = {
        "evaluations": evaluation_rows,
        "summaries": summary_rows,
        "metrics": metric_rows,
        "gates": gates,
        "decisions": decision_rows,
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=list).encode("utf-8")
    ).hexdigest()


def validate_masking_mutation(
    cohort: Sequence[Mapping[str, str]],
    candidates: Sequence[Mapping[str, str]],
    penalties: Sequence[Mapping[str, str]],
    slot_constraints: Sequence[Mapping[str, str]],
    core: Mapping[str, object],
    check: Callable[[bool, str], None],
) -> str:
    """Prove that hidden/display-only text cannot affect the score or gates."""
    changed_cohort = [dict(row) for row in cohort]
    for index, row in enumerate(changed_cohort, 1):
        row["line_class"] = f"DISPLAY_MUTATION_{index}"
        row["structural_axes"] = f"DISPLAY_AXIS_{index}"
        row["surface"] = (
            f"MASKED_TARGET_{row['target_mask_id']}"
            if row["is_target"] == "1" else f"NON_TARGET_DISPLAY_{index}"
        )
        row["frozen_non_target_default_de"] = f"DISPLAY DEFAULT {index}"
        if row["is_target"] == "1":
            # These source columns are required to be masked.  Deliberately
            # poison them here to ensure the scorer does not consult them.
            row["structural_roles"] = "PATIENT|RESULT"
    changed_candidates = [dict(row) for row in candidates]
    for index, row in enumerate(changed_candidates, 1):
        row["renderer_de"] = f"DISPLAY_RENDERER_{index}"
        row["structural_tag"] = f"DISPLAY_TAG_{index}"
    weights = {
        row["penalty_id"]: as_int(row["weight"], "penalty weight")
        for row in penalties
    }
    changed_core = calculate_core(
        changed_cohort, changed_candidates, weights, slot_constraints
    )
    original = scoring_signature(candidates, core)
    changed = scoring_signature(changed_candidates, changed_core)
    check(original == changed, "masked/display-only mutation changed scores or gates")
    return original


def validate_synthetic_full_tie(
    candidates: Sequence[Mapping[str, str]],
    core: Mapping[str, object],
    check: Callable[[bool, str], None],
) -> dict[str, object]:
    """Exercise the otherwise unobserved full-minimum tie branch of G08."""
    first = "OLS_FINISHED_PRODUCT_COLATURA"
    second = "OLS_STRAIN_OPERATION"
    synthetic = dict(core)
    original_summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
    changed_summaries = {
        candidate_id: dict(summary)
        for candidate_id, summary in original_summaries.items()
    }
    tied_penalty = int(changed_summaries[first]["total_penalty"])
    changed_summaries[second]["total_penalty"] = tied_penalty
    synthetic["summaries"] = changed_summaries
    metrics, gate_rows, decisions = independent_metrics(candidates, synthetic)
    tied_ids = tuple(sorted((first, second)))
    for candidate_id in tied_ids:
        row = next(
            item for item in gate_rows
            if item["candidate_id"] == candidate_id
            and item["gate_id"] == "G08_EXACT_TIE_TO_NULL"
        )
        check(row["applicable"] == 1, f"synthetic tied minimum did not reach G08: {candidate_id}")
        check(row["pass"] == 0, f"synthetic tied minimum passed G08: {candidate_id}")
        check(
            "G03_EVERY_RIVAL_MARGIN" in metrics[candidate_id]["failed_gate_ids"],
            f"synthetic tied minimum did not fail G03: {candidate_id}",
        )
        check(
            "G08_EXACT_TIE_TO_NULL" in metrics[candidate_id]["failed_gate_ids"],
            f"synthetic tied minimum did not fail G08: {candidate_id}",
        )
    decision = next(
        item for item in decisions if item["target_mask_id"] == TARGET_MASKS["ols"]
    )
    check(decision["raw_lead_candidate"] == "TIE", "synthetic full tie was source-order broken")
    check(
        tuple(str(decision["raw_minimum_candidates"]).split("|")) == tied_ids,
        "synthetic raw-minimum candidate set changed",
    )
    failed = set(str(decision["raw_lead_failed_gates"]).split("|"))
    check(
        {"G03_EVERY_RIVAL_MARGIN", "G08_EXACT_TIE_TO_NULL"} <= failed,
        "synthetic tie decision did not expose the G03/G08 failure union",
    )
    check(decision["formal_status"] == "OPAQUE_NULL", "synthetic tie produced a policy winner")
    return {
        "target_mask_id": TARGET_MASKS["ols"],
        "tied_minimum_candidates": list(tied_ids),
        "tied_penalty": tied_penalty,
        "decision_failed_gates": str(decision["raw_lead_failed_gates"]).split("|"),
        "g08_applicable_and_failed": True,
    }


def validate_synthetic_dormant_paths(
    penalties: Sequence[Mapping[str, str]],
    check: Callable[[bool, str], None],
) -> dict[str, object]:
    """Cover valid but data-dormant DSL and penalty branches."""
    for valid in (
        "ALWAYS", "ELSE", "LINE_FINAL&NEAREST_LEFT_IN(PATIENT|MATERIAL)",
        "NEAREST_RIGHT_NOT_IN(ENDPOINT)",
    ):
        validate_condition_expression(valid)
    for valid in (
        "NONE", "LEFT_ONE(PATIENT)",
        "ANY_SIDE(SOURCE|MATERIAL)&NOT(RIGHT_ONE(ENDPOINT))",
    ):
        validate_edge_expression(valid)
    rejected = (
        (validate_condition_expression, "ALWAYS&MEDIAL"),
        (validate_condition_expression, "ELSE&TWO_SIDED"),
        (validate_condition_expression, "NEAREST_LEFT_IN()"),
        (validate_condition_expression, "NEAREST_RIGHT_IN(UNKNOWN_ROLE)"),
        (validate_edge_expression, "LEFT_ONE()"),
        (validate_edge_expression, "ANY_SIDE(UNKNOWN_ROLE)"),
    )
    for validator, expression in rejected:
        try:
            validator(expression)
        except AssertionError:
            pass
        else:
            check(False, f"synthetic malformed DSL was accepted: {expression}")
        check(True, f"synthetic malformed DSL rejected: {expression}")

    weights = {
        row["penalty_id"]: as_int(row["weight"], "penalty weight")
        for row in penalties
    }

    def context(
        suffix: str,
        *,
        left: Neighbor | None = None,
        target_slot_roles: frozenset[str] = frozenset(),
        orphans: tuple[Orphan, ...] = (),
    ) -> Context:
        return Context(
            occurrence_id=f"SYNTHETIC:{suffix}", cohort_id="SYNTHETIC",
            locus="SYNTHETIC", page="SYNTHETIC", target_surface="synthetic",
            target_mask_id="TM-SYNTHETIC", ordinal=2, line_token_count=3,
            left=left, right=None, target_slot_roles=target_slot_roles,
            null_orphans=orphans,
        )

    def branch(
        candidate_id: str, policy_class: str, edge_expression: str = "NONE"
    ) -> dict[str, str]:
        return {
            "candidate_id": candidate_id,
            "target_surface": "synthetic",
            "policy_class": policy_class,
            "policy_kind": "INVARIANT",
            "branch_id": f"{candidate_id}-B1",
            "branch_priority": "1",
            "branch_condition": "ALWAYS",
            "structural_tag": "SYNTHETIC",
            "renderer_de": "synthetic display",
            "required_left_classes": "NONE",
            "required_right_classes": "NONE",
            "required_edge_expression": edge_expression,
            "consumes_left_classes": "NONE",
            "consumes_right_classes": "NONE",
            "minimum_branch_pages": "0",
            "candidate_scope": "WHOLE_FORM_OCCURRENCE_ONLY",
            "opaque_baseline": "0",
            "default_is_translation": "0",
            "eva_latin_credit": "0",
            "substring_export_credit": "0",
            "component_claim_credit": "0",
            "confirmed_lexeme": "0",
            "confirmed_plaintext": "0",
        }

    p02 = evaluate_occurrence(
        "SYNTHETIC_P02",
        (branch("SYNTHETIC_P02", "NOMINAL"),),
        context(
            "P02", target_slot_roles=frozenset({"PREDICATE_ONLY_CLOSE"})
        ),
        weights,
    )
    valueless = evaluate_occurrence(
        "SYNTHETIC_VALUELESS",
        (branch("SYNTHETIC_VALUELESS", "MEASURE"),),
        context("VALUELESS"),
        weights,
    )
    left = Neighbor("LEFT", 1, "SYNTHETIC:L", frozenset({"PATIENT"}))
    orphan = Orphan(
        "SYNTHETIC:ORPHAN:PATIENT", "PATIENT", "LEFT", frozenset({"PATIENT"})
    )
    double = evaluate_occurrence(
        "SYNTHETIC_DOUBLE",
        (
            branch(
                "SYNTHETIC_DOUBLE", "OPERATION",
                "LEFT_ONE(PATIENT)&LEFT_ONE(PATIENT)",
            ),
        ),
        context("DOUBLE", left=left, orphans=(orphan,)),
        weights,
    )
    check(
        [(event.penalty_id, event.trigger_code, event.weight) for event in p02.penalties]
        == [("P02_NOUN_IN_PREDICATE_ONLY_CLOSE", "NOUN_IN_PREDICATE_ONLY_CLOSE", 2)],
        "synthetic P02 penalty path changed",
    )
    check(
        [(event.penalty_id, event.trigger_code, event.weight) for event in valueless.penalties]
        == [("P05_MISSING_REQUIRED_VALENCY", "VALUELESS_MEASURE", 5)],
        "synthetic valueless-measure penalty path changed",
    )
    check(len(double.binding_claims) == 2, "synthetic double claim was not recorded twice")
    check(len(double.bound_edges) == 1, "synthetic double claim consumed more than one edge")
    check(len(double.duplicate_edges) == 1, "synthetic double claim was not marked duplicate")
    check(double.binding_claims[1].double_consumption, "synthetic second claim lacks double flag")
    check(
        [(event.penalty_id, event.trigger_code, event.weight) for event in double.penalties]
        == [("P03_DOUBLE_CONSUMPTION", "DOUBLE_CONSUMPTION", 3)],
        "synthetic P03 penalty path changed",
    )
    return {
        "malformed_dsl_cases_rejected": len(rejected),
        "p02_penalty": p02.total_penalty,
        "valueless_measure_penalty": valueless.total_penalty,
        "double_consumption_penalty": double.total_penalty,
        "double_consumption_claim_count": len(double.binding_claims),
        "unique_bound_edge_count": len(double.bound_edges),
    }


def validate_independent_imports(check: Callable[[bool, str], None]) -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=str(__file__))
    forbidden = {"run", "model", "scoring"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.rsplit(".", 1)[-1])
    check(not imported & forbidden, f"validator imports runner implementation: {sorted(imported & forbidden)}")


def replay_runner(
    artifact_dir: Path,
    declared: Sequence[str],
    check: Callable[[bool, str], None],
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="gdt770-independent-replay-") as temporary:
        replay_dir = Path(temporary) / "artifacts"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN_PATH), "--artifacts-dir", str(replay_dir)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        check(
            completed.returncode == 0,
            "temporary runner replay failed: "
            + completed.stderr.decode("utf-8", errors="replace")[-2000:],
        )
        emitted = tuple(sorted(path.name for path in replay_dir.iterdir() if path.is_file()))
        check(emitted == tuple(sorted(declared)), "temporary runner emitted an unexpected file universe")
        replay_stdout = json.loads(completed.stdout.decode("utf-8"))
        check(replay_stdout.get("experiment_id") == "GDT770", "runner stdout is not a GDT770 result")
        hashes: dict[str, str] = {}
        for name in declared:
            expected_path = artifact_dir / name
            replay_path = replay_dir / name
            check(replay_path.is_file(), f"temporary replay omitted {name}")
            check(
                replay_path.read_bytes() == expected_path.read_bytes(),
                f"byte replay mismatch for {name}",
            )
            hashes[name] = sha256(replay_path)
        return {
            "runner_exit_code": completed.returncode,
            "emitted_file_count": len(emitted),
            "byte_identical_file_count": len(hashes),
            "artifact_sha256": hashes,
        }


def write_validation(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently validate GDT770 and byte-replay its runner."
    )
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    artifact_dir = args.artifacts_dir
    if not artifact_dir.is_absolute():
        artifact_dir = ROOT / artifact_dir
    validation_path = artifact_dir / "VALIDATION.json"
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    try:
        validate_independent_imports(check)
        declared = literal_output_names(RUN_PATH)
        check(declared == EXPECTED_OUTPUTS, "literal runner OUTPUT_NAMES contract changed")
        check(len(declared) == len(set(declared)), "duplicate literal runner output name")
        check(
            all(PurePosixPath(name).name == name and "f84" not in name.casefold() for name in declared),
            "unsafe or sealed-material runner output name",
        )
        (
            cohort, _exclusions, candidates, penalties, gates, slot_constraints,
            core, score_node_count, reader_unit_count,
        ) = validate_sources(check)
        manifest_summary = validate_manifest(artifact_dir, declared, check)
        _tables, result = validate_artifacts(
            artifact_dir, cohort, candidates, penalties, gates, slot_constraints,
            core, declared, check,
        )
        score_digest = validate_masking_mutation(
            cohort, candidates, penalties, slot_constraints, core, check
        )
        tie_probe = validate_synthetic_full_tie(candidates, core, check)
        dormant_probe = validate_synthetic_dormant_paths(penalties, check)
        replay = replay_runner(artifact_dir, declared, check)
        summaries: Mapping[str, Mapping[str, object]] = core["summaries"]  # type: ignore[assignment]
        metrics, _gate_rows, decisions = independent_metrics(candidates, core)
        payload: dict[str, object] = {
            "experiment_id": "GDT770",
            "status": "PASS",
            "validator": "independent_stdlib_recomputation_no_runner_import",
            "check_count": checks,
            "source_contract": {
                "source_sha256": dict(sorted(EXPECTED_SOURCE_SHA256.items())),
                "penalty_normative_sha256": projection_sha256(
                    penalties, PENALTY_NORMATIVE_FIELDS
                ),
                "winner_gate_normative_sha256": projection_sha256(
                    gates, GATE_NORMATIVE_FIELDS
                ),
                "predicate_only_close_slot_count": sum(
                    row["predicate_only_close"] == "1" for row in slot_constraints
                ),
            },
            "core_counts": {
                "line_count": len({row["cohort_id"] for row in cohort}),
                "token_count": len(cohort),
                "score_node_count": score_node_count,
                "reader_unit_count": reader_unit_count,
                "target_context_count": len(core["contexts"]),  # type: ignore[arg-type]
                "null_orphan_edge_count": sum(
                    len(context.null_orphans) for context in core["contexts"]  # type: ignore[union-attr]
                ),
                "candidate_occurrence_evaluation_count": sum(
                    len(items) for items in core["evaluations"].values()  # type: ignore[union-attr]
                ),
                "policy_winner_count": sum(bool(item["eligible"]) for item in metrics.values()),
            },
            "candidate_total_penalties": {
                candidate_id: int(summaries[candidate_id]["total_penalty"])
                for candidate_id in sorted(summaries)
            },
            "target_decisions": {
                str(row["surface_provenance_only"]): {
                    key: value for key, value in row.items()
                    if key not in {"surface_provenance_only", "target_surface_visible_to_scorer"}
                }
                for row in decisions
            },
            "masking_mutation_score_sha256": score_digest,
            "synthetic_full_tie_probe": tie_probe,
            "synthetic_dormant_path_probe": dormant_probe,
            "manifest": manifest_summary,
            "byte_replay": replay,
            "validated_result_sha256": sha256(artifact_dir / "RESULT.json"),
            "result_status": result["status"],
        }
        # Record the final number after all assertions; writing is not itself a
        # scientific check and therefore does not increment it.
        payload["check_count"] = checks
        write_validation(validation_path, payload)
        if not args.quiet:
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        error = str(exc).replace(str(ROOT), ".")
        failure = {
            "experiment_id": "GDT770",
            "status": "FAIL",
            "check_count_before_failure": checks,
            "error": error,
        }
        try:
            write_validation(validation_path, failure)
        except OSError:
            pass
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
