#!/usr/bin/env python3
"""Independent exact train-only necessary-world solver for GDT616.

This implementation is intentionally separate from the GDT616 primary solver.
It consumes only frozen public inputs from GDT608/GDT614/GDT615 and never
opens held, LM-confirm, target, f84, or f84r material.

The finite-domain model jointly chooses:

* a complete role-preserving primitive/output-card bijection;
* eight distinct paid merge locations, using each of the four short and four
  macro paid cards exactly once; and
* every recursive effective merge render.

Every default node must be its exact left-to-right effective-child
concatenation and that concatenation must be a registered TRAIN substring.
Every paid node must emit its assigned paid output, differ from its child
concatenation, and (in the strict query) expose that unoverridden child
concatenation as a registered TRAIN substring.  ``qok`` cannot receive a paid
macro card.

This remains a necessary relaxation, not a complete truth world: it omits the
ordered grammar, macro host-side licenses other than the qok prohibition,
word-type exposure floors, labelled traces, unit tilings, transitions, focal
rank, null mass, later worlds, held, oracle, and recovery.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import z3


SCHEMA = "gdt616-independent-joint-child-bound-v1"
EXPECTED_SEARCH_SCHEMA = "gdt615-joint-output-binding-search-v1"
EXPECTED_MODEL_SCHEMA = "gdt614-registered-core-run-macro-v1"
EXPECTED_REGISTRATION_SCHEMA = "gdt616-joint-child-feasible-binding-registration-v1"
EXPECTED_REGISTRATION_SHA256 = (
    "281fe360e6e3eda19323f5e62a99fe4822546b136f7ca91b85fdf4552e565aae"
)
EXPECTED_PRIMITIVES = 34
EXPECTED_MERGES = 64
EXPECTED_PAID = 8
DEFAULT_TIMEOUT_SECONDS = 43_200


class InputError(RuntimeError):
    """A frozen input or model invariant failed validation."""


class SearchIncomplete(RuntimeError):
    """An exact solver query returned unknown or exceeded the wall clock."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise InputError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
DEFAULT_PATHS = {
    "gdt616_registration": EXPERIMENT / "artifacts/REGISTERED_SEARCH.json",
    "registered_search": ROOT
    / "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_SEARCH.json",
    "train_substrings": ROOT
    / "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt",
    "merge_tree": ROOT
    / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv",
    "registered_model": ROOT
    / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json",
    "registered_transitions": ROOT
    / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_TRANSITIONS.tsv",
    "gdt615_terminal": ROOT
    / "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/stage1/STAGE1_RESULT.json",
}
DEFAULT_OUTPUT = EXPERIMENT / "artifacts/work/independent_result.json"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    if path.exists() or temporary.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@dataclass(frozen=True)
class Primitive:
    primitive_id: str
    role: str


@dataclass(frozen=True)
class Card:
    card_id: str
    role: str
    output: str
    side_license: str | None = None


@dataclass(frozen=True)
class Merge:
    rank: int
    left: str
    right: str
    merged: str


@dataclass(frozen=True)
class Problem:
    primitives: tuple[Primitive, ...]
    primitive_cards: tuple[Card, ...]
    paid_cards: tuple[Card, ...]
    merges: tuple[Merge, ...]
    train_substrings: frozenset[str]
    qok_macro_forbidden: bool
    input_sha256: Mapping[str, str]
    input_paths: Mapping[str, str]


@dataclass(frozen=True)
class Relation:
    rank: int
    train_pairs: tuple[tuple[str, str, str], ...]
    left_domain: tuple[str, ...]
    right_domain: tuple[str, ...]
    effective_domain: tuple[str, ...]


@dataclass
class Encoding:
    solver: z3.Solver
    primitive_assignment: Mapping[tuple[str, str], z3.BoolRef]
    paid_assignment: Mapping[tuple[int, str], z3.BoolRef]
    is_paid: Mapping[int, z3.BoolRef]
    violation: Mapping[int, z3.BoolRef]
    value: Mapping[str, z3.IntNumRef]
    train_span: Mapping[int, z3.BoolRef]
    value_to_id: Mapping[str, int]
    id_to_value: tuple[str, ...]
    relations: tuple[Relation, ...]
    assertion_count: int


def _registered_hash(search: Mapping[str, Any], suffix: str) -> str:
    matches = [
        str(row["sha256"])
        for row in search.get("registered_inputs", [])
        if str(row.get("path", "")).endswith(suffix)
    ]
    require(len(matches) == 1, f"registered hash not unique for {suffix}")
    return matches[0]


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _card_from_row(row: Mapping[str, Any], role: str) -> Card:
    return Card(
        card_id=str(row["card_id"]),
        role=role,
        output=str(row["output"]),
        side_license=(
            None if row.get("side_license") is None else str(row["side_license"])
        ),
    )


def load_problem(paths: Mapping[str, Path] = DEFAULT_PATHS) -> Problem:
    for label, path in paths.items():
        require(path.is_file(), f"missing frozen input {label}: {path}")

    require(
        sha256_path(paths["gdt616_registration"]) == EXPECTED_REGISTRATION_SHA256,
        "GDT616 registration hash drift",
    )
    registration = _load_json(paths["gdt616_registration"])
    search = _load_json(paths["registered_search"])
    model = _load_json(paths["registered_model"])
    terminal = _load_json(paths["gdt615_terminal"])
    require(
        registration.get("schema") == EXPECTED_REGISTRATION_SCHEMA,
        "GDT616 registration schema drift",
    )
    require(registration.get("experiment_id") == "GDT616", "registration ID drift")
    require(registration.get("status") == "REGISTERED_UNSCORED", "registration status drift")
    require(
        registration.get("model_id")
        == "HISTORICAL_MIXED_ABBREVIATION_FST_34_CORE_RUN_MACRO_V4_JOINT_CHILD_FEASIBLE",
        "registration model ID drift",
    )
    require(search.get("schema") == EXPECTED_SEARCH_SCHEMA, "search schema drift")
    require(model.get("schema") == EXPECTED_MODEL_SCHEMA, "model schema drift")
    require(
        terminal.get("status") == "MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE",
        "GDT615 terminal status drift",
    )

    actual_hashes = {label: sha256_path(path) for label, path in paths.items()}
    direct_hashes = {
        str(row["path"]): str(row["sha256"])
        for row in registration.get("direct_input_hashes", [])
    }
    direct_labels = (
        "merge_tree",
        "registered_model",
        "registered_transitions",
        "registered_search",
        "train_substrings",
        "gdt615_terminal",
    )
    require(len(direct_hashes) == len(direct_labels), "direct-input inventory drift")
    for label in direct_labels:
        relative = paths[label].relative_to(ROOT).as_posix()
        require(
            direct_hashes.get(relative) == actual_hashes[label],
            f"GDT616 direct-input hash drift for {label}",
        )
    require(
        actual_hashes["merge_tree"] == _registered_hash(search, "merge_tree.tsv"),
        "merge-tree hash drift against GDT615 registration",
    )
    require(
        actual_hashes["registered_model"]
        == _registered_hash(search, "REGISTERED_MODEL.json"),
        "registered-model hash drift against GDT615 registration",
    )
    substring_meta = registration.get("train_substrings")
    require(isinstance(substring_meta, dict), "missing train-substring registration")
    require(
        actual_hashes["train_substrings"] == str(substring_meta.get("sha256", "")),
        "train-substring hash drift against GDT616 registration",
    )
    old_substring_meta = search.get("registered_train_substrings")
    require(isinstance(old_substring_meta, dict), "missing inherited substring registration")
    require(
        old_substring_meta.get("sha256") == substring_meta.get("sha256"),
        "GDT616/GDT615 substring relation drift",
    )

    inventory = registration.get("inventory")
    require(isinstance(inventory, dict), "missing GDT616 registered inventory")
    primitive_rows = inventory.get("primitive_role_assignment")
    require(isinstance(primitive_rows, list), "missing primitive role assignment")
    require(
        primitive_rows == search.get("primitive_role_assignment"),
        "GDT616/GDT615 primitive-role inventory drift",
    )
    primitives = tuple(
        Primitive(str(row["primitive_id"]), str(row["role"]))
        for row in primitive_rows
    )
    require(len(primitives) == EXPECTED_PRIMITIVES, "primitive-count drift")
    require(
        len({primitive.primitive_id for primitive in primitives}) == len(primitives),
        "duplicate primitive ID",
    )

    deck = inventory.get("primitive_output_deck")
    require(isinstance(deck, dict), "missing primitive output deck")
    require(deck == search.get("primitive_output_deck"), "GDT616/GDT615 primitive deck drift")
    primitive_cards = tuple(
        _card_from_row(row, str(role))
        for role in sorted(deck)
        for row in sorted(deck[role], key=lambda item: str(item["card_id"]))
    )
    paid_rows = inventory.get("paid_output_deck")
    require(isinstance(paid_rows, list), "missing paid output deck")
    require(paid_rows == search.get("paid_output_deck"), "GDT616/GDT615 paid deck drift")
    paid_cards = tuple(
        _card_from_row(row, str(row["role"]))
        for row in sorted(paid_rows, key=lambda item: str(item["card_id"]))
    )
    require(len(paid_cards) == EXPECTED_PAID, "paid-card count drift")
    require(len({card.card_id for card in paid_cards}) == len(paid_cards), "paid IDs collide")
    nonempty_outputs = [
        card.output for card in (*primitive_cards, *paid_cards) if card.output
    ]
    require(len(nonempty_outputs) == 41, "nonempty card-output count drift")
    require(
        len(set(nonempty_outputs)) == len(nonempty_outputs),
        "global nonempty card-output collision",
    )

    role_primitive_counts: dict[str, int] = {}
    role_cards: dict[str, list[Card]] = {}
    for primitive in primitives:
        role_primitive_counts[primitive.role] = role_primitive_counts.get(primitive.role, 0) + 1
    for card in primitive_cards:
        role_cards.setdefault(card.role, []).append(card)
    require(set(role_primitive_counts) == set(role_cards), "role sets differ")
    for role, count in role_primitive_counts.items():
        require(len(role_cards[role]) == count, f"role/deck cardinality drift for {role}")

    # Cross-check the fixed GDT614 deck rather than trusting one serialization.
    model_primitive = {
        (str(row["primitive_id"]), str(row["role"]))
        for row in model.get("primitive_cards", [])
    }
    require(
        model_primitive == {(p.primitive_id, p.role) for p in primitives},
        "GDT614/GDT615 primitive-role drift",
    )
    model_paid = {
        (
            str(row["card_id"]),
            str(row["role"]),
            str(row["output"]),
            None if row.get("side_license") is None else str(row["side_license"]),
        )
        for row in model.get("paid_card_deck", [])
    }
    search_paid = {
        (card.card_id, card.role, card.output, card.side_license) for card in paid_cards
    }
    require(model_paid == search_paid, "GDT614/GDT615 paid deck drift")

    merge_text = paths["merge_tree"].read_text(encoding="ascii")
    merge_rows = list(csv.DictReader(merge_text.splitlines(), delimiter="\t"))
    merges = tuple(
        Merge(int(row["rank"]), row["left"], row["right"], row["merged"])
        for row in merge_rows
    )
    require(len(merges) == EXPECTED_MERGES, "merge-count drift")
    require([m.rank for m in merges] == list(range(1, len(merges) + 1)), "rank drift")
    require(
        [merge.merged for merge in merges] == inventory.get("merge_rank_order"),
        "registered merge-rank order drift",
    )
    known = {primitive.primitive_id for primitive in primitives}
    for merge in merges:
        require(merge.left in known and merge.right in known, f"non-topological merge {merge.merged}")
        require(merge.merged not in known, f"duplicate unit ID {merge.merged}")
        known.add(merge.merged)

    payload = paths["train_substrings"].read_bytes()
    try:
        lines = tuple(payload.decode("ascii").splitlines())
    except UnicodeDecodeError as exc:
        raise InputError("TRAIN substring table is not ASCII") from exc
    require(len(lines) == int(substring_meta["distinct_substring_count"]), "substring count drift")
    require(len(set(lines)) == len(lines), "duplicate TRAIN substring")
    require(
        lines == tuple(sorted(lines, key=lambda value: (len(value), value))),
        "TRAIN substring order drift",
    )
    minimum = int(substring_meta["minimum_length"])
    maximum = int(substring_meta["maximum_length"])
    require(
        all(minimum <= len(value) <= maximum and value.isascii() and value.isalpha() for value in lines),
        "malformed TRAIN substring",
    )
    train = frozenset(lines)

    constraints = model.get("merge_constraints")
    require(isinstance(constraints, dict), "missing GDT614 merge constraints")
    require(int(constraints.get("paid_cards", -1)) == len(paid_cards), "paid budget drift")
    require(bool(constraints.get("qok_paid_macro_forbidden")), "qok prohibition drift")
    require(bool(constraints.get("default_merge_equals_recursive_children")), "default rule drift")
    variables = registration.get("variables")
    require(isinstance(variables, dict), "missing GDT616 variable contract")
    require(int(variables.get("actual_paid_locations", -1)) == len(paid_cards), "actual paid count drift")
    require(int(variables.get("paid_short_cards", -1)) == 4, "short paid count drift")
    require(int(variables.get("paid_macro_cards", -1)) == 4, "macro paid count drift")
    require(variables.get("relaxed_core_hit_variables") == "FORBIDDEN", "core-hit contract drift")
    require(
        int(registration.get("limits", {}).get("wall_clock_seconds_maximum", -1))
        == DEFAULT_TIMEOUT_SECONDS,
        "registered wall-clock limit drift",
    )
    require(
        registration.get("stage_a_selection", {}).get("diagnostic_witness_order")
        == [
            "lexicographically minimize card IDs in registered primitive order",
            "lexicographically minimize ascending (merge rank, paid card ID) tuple",
        ],
        "diagnostic witness order drift",
    )

    return Problem(
        primitives=primitives,
        primitive_cards=primitive_cards,
        paid_cards=paid_cards,
        merges=merges,
        train_substrings=train,
        qok_macro_forbidden=True,
        input_sha256=actual_hashes,
        input_paths={label: path.relative_to(ROOT).as_posix() for label, path in paths.items()},
    )


def cards_by_role(problem: Problem) -> dict[str, tuple[Card, ...]]:
    result: dict[str, list[Card]] = {}
    for card in problem.primitive_cards:
        result.setdefault(card.role, []).append(card)
    return {
        role: tuple(sorted(cards, key=lambda card: card.card_id))
        for role, cards in result.items()
    }


def eligible_paid_cards(problem: Problem, merge: Merge) -> tuple[Card, ...]:
    return tuple(
        card
        for card in problem.paid_cards
        if not (
            problem.qok_macro_forbidden
            and merge.merged == "qok"
            and card.role == "macro_core"
        )
    )


def build_relations(problem: Problem) -> tuple[tuple[Relation, ...], dict[str, set[str]]]:
    by_role = cards_by_role(problem)
    domains: dict[str, set[str]] = {
        primitive.primitive_id: {card.output for card in by_role[primitive.role]}
        for primitive in problem.primitives
    }
    relations: list[Relation] = []
    for merge in problem.merges:
        left_domain = tuple(sorted(domains[merge.left], key=lambda value: (len(value), value)))
        right_domain = tuple(sorted(domains[merge.right], key=lambda value: (len(value), value)))
        pairs = tuple(
            sorted(
                (
                    (left, right, left + right)
                    for left in left_domain
                    for right in right_domain
                    if left + right in problem.train_substrings
                ),
                key=lambda row: (row[0], row[1], row[2]),
            )
        )
        effective = {composition for _, _, composition in pairs}
        effective.update(card.output for card in eligible_paid_cards(problem, merge))
        domains[merge.merged] = effective
        relations.append(
            Relation(
                rank=merge.rank,
                train_pairs=pairs,
                left_domain=left_domain,
                right_domain=right_domain,
                effective_domain=tuple(sorted(effective, key=lambda value: (len(value), value))),
            )
        )
    return tuple(relations), domains


def _pb_exactly(expressions: Iterable[z3.BoolRef], count: int) -> z3.BoolRef:
    terms = [(expression, 1) for expression in expressions]
    if not terms:
        return z3.BoolVal(count == 0)
    return z3.PbEq(terms, count)


def _or(expressions: Sequence[z3.BoolRef]) -> z3.BoolRef:
    if not expressions:
        return z3.BoolVal(False)
    return z3.Or(*expressions)


def build_encoding(problem: Problem) -> Encoding:
    relations, domains = build_relations(problem)
    universe = set().union(*domains.values())
    universe.update(card.output for card in problem.primitive_cards)
    universe.update(card.output for card in problem.paid_cards)
    ordered_values = tuple(sorted(universe, key=lambda value: (len(value), value)))
    value_to_id = {value: index for index, value in enumerate(ordered_values)}

    solver = z3.Solver()
    solver.set(random_seed=0)
    solver.set("smt.random_seed", 0)
    assertions = 0

    primitive_assignment: dict[tuple[str, str], z3.BoolRef] = {}
    paid_assignment: dict[tuple[int, str], z3.BoolRef] = {}
    is_paid: dict[int, z3.BoolRef] = {}
    violation: dict[int, z3.BoolRef] = {}
    train_span: dict[int, z3.BoolRef] = {}
    value: dict[str, z3.IntNumRef] = {
        item: z3.Int(f"value_{index:03d}_{item}")
        for index, item in enumerate(domains)
    }

    role_cards = cards_by_role(problem)
    primitives_by_role: dict[str, list[Primitive]] = {}
    for primitive in problem.primitives:
        primitives_by_role.setdefault(primitive.role, []).append(primitive)
        choices: list[z3.BoolRef] = []
        for card in role_cards[primitive.role]:
            variable = z3.Bool(f"primitive_{primitive.primitive_id}_card_{card.card_id}")
            primitive_assignment[(primitive.primitive_id, card.card_id)] = variable
            choices.append(variable)
            solver.add(z3.Implies(variable, value[primitive.primitive_id] == value_to_id[card.output]))
            assertions += 1
        solver.add(_pb_exactly(choices, 1))
        assertions += 1
    for role, primitives in primitives_by_role.items():
        for card in role_cards[role]:
            solver.add(
                _pb_exactly(
                    [primitive_assignment[(primitive.primitive_id, card.card_id)] for primitive in primitives],
                    1,
                )
            )
            assertions += 1

    # Every paid card is used exactly once, so its effective output must itself
    # belong to TRAIN.  Primitive-output exposure is a later Stage-B gate and
    # is deliberately not added to the registered Stage-A formula.
    missing_direct = sorted(
        {
            card.output
            for card in problem.paid_cards
            if card.output and card.output not in problem.train_substrings
        }
    )
    solver.add(z3.BoolVal(not missing_direct))
    assertions += 1

    merge_by_rank = {merge.rank: merge for merge in problem.merges}
    relation_by_rank = {relation.rank: relation for relation in relations}
    for merge in problem.merges:
        relation = relation_by_rank[merge.rank]
        node_choices: list[z3.BoolRef] = []
        for card in problem.paid_cards:
            variable = z3.Bool(f"paid_rank_{merge.rank:02d}_card_{card.card_id.replace(':', '_')}")
            paid_assignment[(merge.rank, card.card_id)] = variable
            node_choices.append(variable)
            if card not in eligible_paid_cards(problem, merge):
                solver.add(z3.Not(variable))
                assertions += 1
        solver.add(z3.PbLe([(item, 1) for item in node_choices], 1))
        assertions += 1
        is_paid[merge.rank] = z3.Bool(f"is_paid_{merge.rank:02d}")
        solver.add(is_paid[merge.rank] == _or(node_choices))
        assertions += 1

        left_value = value[merge.left]
        right_value = value[merge.right]
        node_value = value[merge.merged]
        pair_terms = [
            z3.And(
                left_value == value_to_id[left],
                right_value == value_to_id[right],
            )
            for left, right, _ in relation.train_pairs
        ]
        train_span[merge.rank] = z3.Bool(f"train_child_span_{merge.rank:02d}")
        solver.add(train_span[merge.rank] == _or(pair_terms))
        assertions += 1

        default_terms = [
            z3.And(
                left_value == value_to_id[left],
                right_value == value_to_id[right],
                node_value == value_to_id[composition],
            )
            for left, right, composition in relation.train_pairs
        ]
        solver.add(z3.Implies(z3.Not(is_paid[merge.rank]), _or(default_terms)))
        assertions += 1

        for card in problem.paid_cards:
            equal_child_pairs = [
                z3.And(
                    left_value == value_to_id[left],
                    right_value == value_to_id[right],
                )
                for left in relation.left_domain
                for right in relation.right_domain
                if left + right == card.output
            ]
            solver.add(
                z3.Implies(
                    paid_assignment[(merge.rank, card.card_id)],
                    z3.And(
                        node_value == value_to_id[card.output],
                        z3.Not(_or(equal_child_pairs)),
                    ),
                )
            )
            assertions += 1

        violation[merge.rank] = z3.Bool(f"paid_child_span_violation_{merge.rank:02d}")
        solver.add(
            violation[merge.rank]
            == z3.And(is_paid[merge.rank], z3.Not(train_span[merge.rank]))
        )
        assertions += 1

    for card in problem.paid_cards:
        solver.add(
            _pb_exactly(
                [paid_assignment[(merge.rank, card.card_id)] for merge in problem.merges],
                1,
            )
        )
        assertions += 1

    require(set(merge_by_rank) == set(relation_by_rank), "relation rank mismatch")
    return Encoding(
        solver=solver,
        primitive_assignment=primitive_assignment,
        paid_assignment=paid_assignment,
        is_paid=is_paid,
        violation=violation,
        value=value,
        train_span=train_span,
        value_to_id=value_to_id,
        id_to_value=ordered_values,
        relations=relations,
        assertion_count=assertions,
    )


class ExactQueries:
    def __init__(self, solver: z3.Solver, timeout_seconds: int):
        self.solver = solver
        self.deadline = time.monotonic() + timeout_seconds
        self.query_count = 0
        self.sat_count = 0
        self.unsat_count = 0

    def check(self, *extra: z3.BoolRef) -> z3.CheckSatResult:
        remaining_ms = int((self.deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            raise SearchIncomplete("independent exact-query wall clock exhausted")
        self.solver.set(timeout=max(1, remaining_ms))
        self.solver.push()
        self.solver.add(*extra)
        status = self.solver.check()
        self.solver.pop()
        self.query_count += 1
        if status == z3.sat:
            self.sat_count += 1
        elif status == z3.unsat:
            self.unsat_count += 1
        else:
            raise SearchIncomplete(f"exact query returned {status}: {self.solver.reason_unknown()}")
        return status


def _model_is_true(model: z3.ModelRef, expression: z3.BoolRef) -> bool:
    return z3.is_true(model.eval(expression, model_completion=True))


def choose_deterministic_witness(
    problem: Problem,
    encoding: Encoding,
    minimum_violations: int,
    queries: ExactQueries,
) -> z3.ModelRef:
    solver = encoding.solver
    violation_terms = [(encoding.violation[merge.rank], 1) for merge in problem.merges]
    solver.add(z3.PbEq(violation_terms, minimum_violations))

    by_role = cards_by_role(problem)
    for primitive in problem.primitives:
        selected = None
        for card in by_role[primitive.role]:
            candidate = encoding.primitive_assignment[(primitive.primitive_id, card.card_id)]
            if queries.check(candidate) == z3.sat:
                solver.add(candidate)
                selected = card.card_id
                break
        require(selected is not None, f"no lex primitive completion at {primitive.primitive_id}")

    # Minimize the ascending sequence of (rank, card ID) pairs directly.  It
    # is not equivalent to minimizing all ranks first and card IDs second:
    # (1,a),(3,z) precedes (1,z),(2,a) at the first pair.
    paid_pairs: list[tuple[int, str]] = []
    previous_rank = 0
    ordered_cards = tuple(sorted(problem.paid_cards, key=lambda item: item.card_id))
    merge_ranks = tuple(merge.rank for merge in problem.merges)
    for _slot in range(len(problem.paid_cards)):
        selected_pair = None
        for rank in (item for item in merge_ranks if item > previous_rank):
            gap = [
                z3.Not(encoding.is_paid[item])
                for item in merge_ranks
                if previous_rank < item < rank
            ]
            for card in ordered_cards:
                candidate = encoding.paid_assignment[(rank, card.card_id)]
                if queries.check(*gap, candidate) == z3.sat:
                    solver.add(*gap, candidate)
                    selected_pair = (rank, card.card_id)
                    paid_pairs.append(selected_pair)
                    previous_rank = rank
                    break
            if selected_pair is not None:
                break
        require(selected_pair is not None, "paid (rank,card) lex completion failed")
    solver.add(
        *[
            z3.Not(encoding.is_paid[rank])
            for rank in merge_ranks
            if rank > previous_rank
        ]
    )

    remaining_ms = int((queries.deadline - time.monotonic()) * 1000)
    if remaining_ms <= 0:
        raise SearchIncomplete("wall clock exhausted before final witness")
    solver.set(timeout=max(1, remaining_ms))
    status = solver.check()
    queries.query_count += 1
    if status != z3.sat:
        if status == z3.unsat:
            queries.unsat_count += 1
            raise InputError("deterministic witness fixing unexpectedly UNSAT")
        raise SearchIncomplete(f"final witness query returned {status}: {solver.reason_unknown()}")
    queries.sat_count += 1
    return solver.model()


def extract_and_replay(
    problem: Problem,
    encoding: Encoding,
    model: z3.ModelRef,
    expected_violations: int,
) -> dict[str, Any]:
    by_role = cards_by_role(problem)
    mapping: dict[str, Card] = {}
    mapping_rows: list[dict[str, Any]] = []
    for primitive in problem.primitives:
        chosen = [
            card
            for card in by_role[primitive.role]
            if _model_is_true(
                model,
                encoding.primitive_assignment[(primitive.primitive_id, card.card_id)],
            )
        ]
        require(len(chosen) == 1, f"model primitive assignment invalid at {primitive.primitive_id}")
        mapping[primitive.primitive_id] = chosen[0]
        mapping_rows.append(
            {
                "card_id": chosen[0].card_id,
                "length": len(chosen[0].output),
                "output": chosen[0].output,
                "primitive_id": primitive.primitive_id,
                "role": primitive.role,
                "side_license": chosen[0].side_license,
            }
        )

    for role, cards in by_role.items():
        observed = [mapping[p.primitive_id].card_id for p in problem.primitives if p.role == role]
        require(sorted(observed) == sorted(card.card_id for card in cards), f"non-bijection in {role}")

    paid_by_rank: dict[int, Card] = {}
    for merge in problem.merges:
        selected = [
            card
            for card in problem.paid_cards
            if _model_is_true(model, encoding.paid_assignment[(merge.rank, card.card_id)])
        ]
        require(len(selected) <= 1, f"multiple paid cards at rank {merge.rank}")
        if selected:
            paid_by_rank[merge.rank] = selected[0]
    require(len(paid_by_rank) == len(problem.paid_cards), "paid-location count replay failed")
    require(
        sorted(card.card_id for card in paid_by_rank.values())
        == sorted(card.card_id for card in problem.paid_cards),
        "paid-card bijection replay failed",
    )

    effective = {primitive_id: card.output for primitive_id, card in mapping.items()}
    merge_rows: list[dict[str, Any]] = []
    violation_ranks: list[int] = []
    for merge in problem.merges:
        left = effective[merge.left]
        right = effective[merge.right]
        composition = left + right
        in_train = composition in problem.train_substrings
        require(composition, f"empty child composition at rank {merge.rank}")
        paid = paid_by_rank.get(merge.rank)
        if paid is None:
            require(in_train, f"default child composition lacks TRAIN span at {merge.rank}")
            output = composition
            mode = "DEFAULT"
        else:
            require(composition != paid.output, f"paid output equals children at {merge.rank}")
            if merge.merged == "qok":
                require(paid.role != "macro_core", "qok received forbidden macro")
            output = paid.output
            mode = "PAID"
            if not in_train:
                violation_ranks.append(merge.rank)
        require(output and output in problem.train_substrings, f"effective output lacks TRAIN span at {merge.rank}")
        effective[merge.merged] = output
        solver_value = model.eval(encoding.value[merge.merged], model_completion=True).as_long()
        require(encoding.id_to_value[solver_value] == output, f"solver/replay output drift at {merge.rank}")
        solver_span = _model_is_true(model, encoding.train_span[merge.rank])
        require(solver_span == in_train, f"solver/replay span drift at {merge.rank}")
        merge_rows.append(
            {
                "child_composition": composition,
                "child_composition_in_train": in_train,
                "effective_output": output,
                "left": merge.left,
                "left_effective_output": left,
                "merge": merge.merged,
                "mode": mode,
                "paid_card_id": None if paid is None else paid.card_id,
                "paid_card_role": None if paid is None else paid.role,
                "rank": merge.rank,
                "right": merge.right,
                "right_effective_output": right,
            }
        )
    require(len(violation_ranks) == expected_violations, "minimum-violation replay drift")

    paid_rows = [
        {
            "card_id": paid_by_rank[rank].card_id,
            "child_composition": merge_rows[rank - 1]["child_composition"],
            "child_composition_in_train": merge_rows[rank - 1]["child_composition_in_train"],
            "merge": merge_rows[rank - 1]["merge"],
            "output": paid_by_rank[rank].output,
            "output_length": len(paid_by_rank[rank].output),
            "rank": rank,
            "role": paid_by_rank[rank].role,
            "side_license": paid_by_rank[rank].side_license,
        }
        for rank in sorted(paid_by_rank)
    ]
    return {
        "actual_paid_locations": paid_rows,
        "merge_replay": merge_rows,
        "paid_child_span_violation_ranks": violation_ranks,
        "primitive_mapping": mapping_rows,
        "replay_checks": {
            "all_64_recursive_effective_outputs_exact": len(merge_rows) == len(problem.merges),
            "all_41_nonempty_card_outputs_global_distinct": len(
                {
                    card.output
                    for card in (*problem.primitive_cards, *problem.paid_cards)
                    if card.output
                }
            )
            == len(
                [
                    card
                    for card in (*problem.primitive_cards, *problem.paid_cards)
                    if card.output
                ]
            ),
            "all_child_compositions_in_train": all(
                row["child_composition_in_train"] for row in merge_rows
            ),
            "all_child_compositions_nonempty": all(
                bool(row["child_composition"]) for row in merge_rows
            ),
            "all_default_child_compositions_in_train": all(
                row["child_composition_in_train"]
                for row in merge_rows
                if row["mode"] == "DEFAULT"
            ),
            "all_effective_outputs_in_train": all(
                row["effective_output"] in problem.train_substrings for row in merge_rows
            ),
            "all_effective_outputs_nonempty": all(
                bool(row["effective_output"]) for row in merge_rows
            ),
            "complete_same_role_bijection": True,
            "every_paid_card_used_once": True,
            "exactly_eight_distinct_paid_locations": len(paid_rows) == len(problem.paid_cards),
            "paid_output_differs_from_child_composition": all(
                row["output"] != row["child_composition"] for row in paid_rows
            ),
            "qok_paid_macro_forbidden": all(
                not (row["merge"] == "qok" and row["role"] == "macro_core")
                for row in paid_rows
            ),
            "strict_paid_child_gate": not violation_ranks,
        },
    }


def solve(problem: Problem, timeout_seconds: int) -> dict[str, Any]:
    encoding = build_encoding(problem)
    queries = ExactQueries(encoding.solver, timeout_seconds)
    violation_terms = [(encoding.violation[merge.rank], 1) for merge in problem.merges]
    # The registered strict query is always first and terminal when UNSAT.
    # No optional relaxation query may turn that completed proof into a later
    # timeout/unknown and thereby downgrade the registered outcome.
    strict_query = queries.check(z3.PbEq(violation_terms, 0))
    boundary_queries = [
        {
            "paid_child_span_violations_equal": 0,
            "status": "SAT" if strict_query == z3.sat else "UNSAT",
        }
    ]

    base = {
        "access": {
            "f84_or_f84r_opened": False,
            "held_or_lm_confirm_opened": False,
            "voynich_target_or_meaning_opened": False,
        },
        "claim_ceiling": (
            "Synthetic train-only necessary recursive-span world; no Voynich unit, "
            "sound, language, word, plaintext, object, operation, or meaning."
        ),
        "exact_boundary_queries": boundary_queries,
        "input_paths": dict(sorted(problem.input_paths.items())),
        "input_sha256": dict(sorted(problem.input_sha256.items())),
        "model_counts": {
            "assertions_before_query_fixes": encoding.assertion_count,
            "effective_value_universe": len(encoding.id_to_value),
            "merge_nodes": len(problem.merges),
            "paid_cards": len(problem.paid_cards),
            "primitive_cards": len(problem.primitive_cards),
            "primitives": len(problem.primitives),
            "train_relation_tuples": sum(len(relation.train_pairs) for relation in encoding.relations),
            "train_substrings": len(problem.train_substrings),
        },
        "omitted_stricter_constraints": [
            "ordered WORD/CORE_RUN grammar and complete legal parses",
            "macro LEFT_HOST/RIGHT_HOST licenses except qok paid-macro prohibition",
            "eight-train-type scored-card exposure floors",
            "multiplicity-preserving labelled traces and nonoverlapping 98-unit tilings",
            "21 transitions, focal-incidence rank, and null-mass bounds",
            "W1/W2 generation, held, LM-confirm, oracle, and blind recovery",
        ],
        "schema": SCHEMA,
        "solver": {
            "backend": "z3 finite-domain integer/Boolean tables",
            "deterministic_greedy_witness_order": [
                "registered strict paid-child span constraints fixed",
                "primitive card IDs in registered primitive order",
                "ascending (merge rank, paid card ID) pair sequence",
            ],
            "query_count": None,
            "sat_queries": None,
            "unsat_queries": None,
            "z3_version": z3.get_version_string(),
        },
    }

    if strict_query == z3.unsat:
        base.update(
            {
                "decision": "NO_JOINT_CHILD_FEASIBLE_BINDING",
                "diagnostic_relaxation_status": "NOT_RUN_AFTER_TERMINAL_STRICT_UNSAT",
                "minimum_paid_child_span_violations": None,
                "strict_joint_child_span_status": "UNSAT",
                "witness": None,
            }
        )
    else:
        model = choose_deterministic_witness(problem, encoding, 0, queries)
        witness = extract_and_replay(problem, encoding, model, 0)
        base.update(
            {
                "decision": "JOINT_CHILD_NECESSARY_BOUND_SAT",
                "diagnostic_relaxation_status": "NOT_NEEDED",
                "minimum_paid_child_span_violations": 0,
                "strict_joint_child_span_status": "SAT",
                "witness": witness,
            }
        )

    base["solver"].update(
        {
            "query_count": queries.query_count,
            "sat_queries": queries.sat_count,
            "unsat_queries": queries.unsat_count,
        }
    )
    return base


def toy_problem(
    *,
    train: Sequence[str],
    paid_role: str = "short_card",
    paid_output: str = "x",
    qok: bool = False,
) -> Problem:
    merge_name = "qok" if qok else "AB"
    return Problem(
        primitives=(Primitive("A", "literal"), Primitive("B", "literal")),
        primitive_cards=(Card("L01", "literal", "a"), Card("L02", "literal", "b")),
        paid_cards=(Card("P01", paid_role, paid_output),),
        merges=(Merge(1, "A", "B", merge_name),),
        train_substrings=frozenset(train),
        qok_macro_forbidden=True,
        input_sha256={},
        input_paths={},
    )


def run_self_test() -> None:
    cases = 0

    strict = toy_problem(train=("a", "b", "ab", "ba", "x"))
    result = solve(strict, 60)
    require(result["decision"] == "JOINT_CHILD_NECESSARY_BOUND_SAT", "toy SAT decision drift")
    require(result["strict_joint_child_span_status"] == "SAT", "toy strict SAT missed")
    require(result["minimum_paid_child_span_violations"] == 0, "toy strict minimum drift")
    cases += 1

    one_violation = toy_problem(train=("a", "b", "x"))
    result = solve(one_violation, 60)
    require(result["strict_joint_child_span_status"] == "UNSAT", "toy strict UNSAT missed")
    require(result["minimum_paid_child_span_violations"] is None, "toy terminal UNSAT drift")
    require(result["witness"] is None, "toy strict UNSAT unexpectedly emitted witness")
    require(
        result["diagnostic_relaxation_status"]
        == "NOT_RUN_AFTER_TERMINAL_STRICT_UNSAT",
        "toy strict UNSAT incorrectly ran a relaxation",
    )
    require(result["solver"]["query_count"] == 1, "toy strict UNSAT was not terminal")
    cases += 1

    qok_macro = toy_problem(
        train=("a", "b", "ab", "ba", "x"),
        paid_role="macro_core",
        qok=True,
    )
    result = solve(qok_macro, 60)
    require(result["decision"] == "NO_JOINT_CHILD_FEASIBLE_BINDING", "toy qok gate missed")
    cases += 1

    # An empty abstract effective domain is a legitimate exact contradiction,
    # not malformed input.  Here qok cannot take the only (macro) paid card and
    # neither primitive order forms a TRAIN substring.
    empty_effective = toy_problem(
        train=("a", "b", "x"),
        paid_role="macro_core",
        qok=True,
    )
    relations, _domains = build_relations(empty_effective)
    require(relations[0].effective_domain == (), "toy empty effective domain not reached")
    result = solve(empty_effective, 60)
    require(
        result["decision"] == "NO_JOINT_CHILD_FEASIBLE_BINDING",
        "toy empty effective domain did not encode UNSAT",
    )
    require(result["solver"]["query_count"] == 1, "toy empty-domain UNSAT was not terminal")
    cases += 1

    # The paid output must differ from the recursive child composition.  With
    # only one merge and output ``ab``, every legal mapping is excluded.
    equal_output = toy_problem(
        train=("a", "b", "ab", "ba"),
        paid_output="ab",
    )
    # One mapping yields ``ba`` and remains legal, so force the singleton deck
    # in a second tiny problem to test equality directly.
    equal_output = Problem(
        primitives=(Primitive("A", "fixed"), Primitive("B", "fixed_b")),
        primitive_cards=(Card("A1", "fixed", "a"), Card("B1", "fixed_b", "b")),
        paid_cards=(Card("P1", "short_card", "ab"),),
        merges=(Merge(1, "A", "B", "AB"),),
        train_substrings=frozenset(("a", "b", "ab")),
        qok_macro_forbidden=True,
        input_sha256={},
        input_paths={},
    )
    result = solve(equal_output, 60)
    require(result["decision"] == "NO_JOINT_CHILD_FEASIBLE_BINDING", "toy paid!=child missed")
    cases += 1

    with tempfile.TemporaryDirectory(prefix="gdt616-independent-selftest-") as directory:
        target = Path(directory) / "result.json"
        atomic_write(target, b"first\n")
        try:
            atomic_write(target, b"second\n")
        except FileExistsError:
            pass
        else:
            raise InputError("atomic writer overwrote an existing target")
        cases += 1

        target.unlink()
        temporary = target.with_name(target.name + f".tmp.{os.getpid()}")
        temporary.write_bytes(b"occupied\n")
        try:
            atomic_write(target, b"third\n")
        except FileExistsError:
            pass
        else:
            raise InputError("atomic writer reused an existing temporary path")
        cases += 1

    print(f"GDT616_INDEPENDENT_SELF_TEST_PASS cases={cases}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument(
        "--execute-registered",
        action="store_true",
        help="explicitly authorize the frozen GDT616 registered-input run",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        1 <= args.timeout_seconds <= DEFAULT_TIMEOUT_SECONDS,
        f"timeout must be in 1..{DEFAULT_TIMEOUT_SECONDS}",
    )
    if args.self_test:
        run_self_test()
        return 0
    require(args.execute_registered, "registered execution requires --execute-registered")
    problem = load_problem()
    try:
        result = solve(problem, args.timeout_seconds)
    except SearchIncomplete as exc:
        result = {
            "access": {
                "f84_or_f84r_opened": False,
                "held_or_lm_confirm_opened": False,
                "voynich_target_or_meaning_opened": False,
            },
            "decision": "SEARCH_INCOMPLETE",
            "error": str(exc),
            "input_paths": dict(sorted(problem.input_paths.items())),
            "input_sha256": dict(sorted(problem.input_sha256.items())),
            "schema": SCHEMA,
        }
    payload = canonical_json(result)
    atomic_write(args.output, payload)
    print(f"{result['decision']} output={args.output} sha256={sha256_bytes(payload)}")
    return 0 if result["decision"] != "SEARCH_INCOMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
