#!/usr/bin/env python3
"""Exact primary Stage-0 solver for the registered GDT615 search.

This program deliberately has only three scientific inputs:

* REGISTERED_SEARCH.json
* REGISTERED_TRAIN_SUBSTRINGS.txt
* GDT608 merge_tree.tsv

It uses a Boolean one-hot/MDD/pseudo-Boolean encoding.  It does not discover
or open any path named by the registration other than the two paths explicitly
passed on the command line and the registration file itself.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import z3


SCHEMA = "gdt615-stage0-primary-result-v1"
EXPECTED_SEARCH_SCHEMA = "gdt615-joint-output-binding-search-v1"
EXPECTED_MODEL_ID = (
    "HISTORICAL_MIXED_ABBREVIATION_FST_34_CORE_RUN_MACRO_V3_BINDING_SEARCH"
)
EXPECTED_UNIT_COUNT = 98
EXPECTED_PRIMITIVE_COUNT = 34
EXPECTED_MERGE_COUNT = 64
EXPECTED_HIT_BUDGET = 8
REGISTERED_TIME_LIMIT_SECONDS = 14_400


class InputError(RuntimeError):
    """A registered Stage-0 input failed validation."""


class SearchIncomplete(RuntimeError):
    """The exact search did not finish within the registered resource bound."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


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


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write(path, canonical_json(value))


@dataclass(frozen=True)
class Card:
    card_id: str
    role: str
    output: str
    length: int
    metadata: tuple[tuple[str, object], ...]

    def as_dict(self) -> dict[str, object]:
        result = dict(self.metadata)
        result.update(
            {
                "card_id": self.card_id,
                "role": self.role,
                "output": self.output,
                "length": self.length,
            }
        )
        return result


@dataclass(frozen=True)
class Primitive:
    primitive_id: str
    role: str


@dataclass(frozen=True)
class Merge:
    rank: int
    left: str
    right: str
    merged: str
    leaves: tuple[str, ...]
    leaf_count: int
    tree_depth: int
    merge_descendant_ranks: tuple[int, ...]


@dataclass(frozen=True)
class RegisteredInputs:
    search_path: Path
    substring_path: Path
    merge_tree_path: Path
    search_sha256: str
    substring_sha256: str
    merge_tree_sha256: str
    search: Mapping[str, object]
    primitives: tuple[Primitive, ...]
    cards_by_role: Mapping[str, tuple[Card, ...]]
    merges: tuple[Merge, ...]
    substrings: frozenset[str]
    substring_order: tuple[str, ...]


class ByteTrie:
    """Exact ASCII trie for the registered substring table."""

    def __init__(self, strings: Sequence[str]):
        self.edges: list[dict[str, int]] = [{}]
        self.terminal: list[bool] = [False]
        for value in strings:
            state = 0
            for character in value:
                following = self.edges[state].get(character)
                if following is None:
                    following = len(self.edges)
                    self.edges[state][character] = following
                    self.edges.append({})
                    self.terminal.append(False)
                state = following
            self.terminal[state] = True
        self._transition_cache: dict[tuple[int, str], int] = {}

    def transition(self, state: int, value: str) -> int:
        key = (state, value)
        cached = self._transition_cache.get(key)
        if cached is not None:
            return cached
        following = state
        for character in value:
            following = self.edges[following].get(character, -1)
            if following < 0:
                break
        self._transition_cache[key] = following
        return following


@dataclass(frozen=True)
class MDDNode:
    primitive_id: str
    arcs: tuple[tuple[str, int], ...]


class MDDRegistry:
    """Reduced ordered MDDs shared across the 64 merge predicates."""

    INVALID = -1
    ACCEPT = -2

    def __init__(
        self,
        trie: ByteTrie,
        primitive_roles: Mapping[str, str],
        cards_by_role: Mapping[str, tuple[Card, ...]],
    ):
        self.trie = trie
        self.primitive_roles = primitive_roles
        self.cards_by_role = cards_by_role
        self.nodes: list[MDDNode] = []
        self._interned: dict[tuple[str, tuple[tuple[str, int], ...]], int] = {}

    def _intern(self, primitive_id: str, arcs: tuple[tuple[str, int], ...]) -> int:
        signature = (primitive_id, arcs)
        existing = self._interned.get(signature)
        if existing is not None:
            return existing
        node_id = len(self.nodes)
        self.nodes.append(MDDNode(primitive_id, arcs))
        self._interned[signature] = node_id
        return node_id

    def build(self, leaves: tuple[str, ...]) -> int:
        @lru_cache(maxsize=None)
        def visit(position: int, trie_state: int) -> int:
            if position == len(leaves):
                return self.ACCEPT if self.trie.terminal[trie_state] else self.INVALID
            primitive_id = leaves[position]
            role = self.primitive_roles[primitive_id]
            arcs: list[tuple[str, int]] = []
            for card in self.cards_by_role[role]:
                following = self.trie.transition(trie_state, card.output)
                if following < 0:
                    continue
                child = visit(position + 1, following)
                if child != self.INVALID:
                    arcs.append((card.card_id, child))
            if not arcs:
                return self.INVALID
            return self._intern(primitive_id, tuple(arcs))

        return visit(0, 0)

    @property
    def arc_count(self) -> int:
        return sum(len(node.arcs) for node in self.nodes)


@dataclass
class BooleanModel:
    assertions: tuple[z3.BoolRef, ...]
    assignment: Mapping[tuple[str, str], z3.BoolRef]
    support: tuple[z3.BoolRef, ...]
    core_hit: tuple[z3.BoolRef, ...]
    mdd_node_count: int
    mdd_arc_count: int


def _registered_hash(search: Mapping[str, object], suffix: str) -> str:
    matches = [
        row
        for row in search.get("registered_inputs", [])
        if str(row.get("path", "")).endswith(suffix)
    ]
    if len(matches) != 1:
        raise InputError(f"registered hash not uniquely found for {suffix}")
    return str(matches[0]["sha256"])


def load_registered_inputs(
    search_path: Path, substring_path: Path, merge_tree_path: Path
) -> RegisteredInputs:
    search_payload = search_path.read_bytes()
    try:
        search = json.loads(search_payload)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid registered search JSON: {exc}") from exc
    if search.get("schema") != EXPECTED_SEARCH_SCHEMA:
        raise InputError("registered search schema drift")
    if search.get("model_id") != EXPECTED_MODEL_ID:
        raise InputError("registered model ID drift")

    expected_merge_hash = _registered_hash(search, "merge_tree.tsv")
    actual_merge_hash = sha256_path(merge_tree_path)
    if actual_merge_hash != expected_merge_hash:
        raise InputError("merge_tree.tsv hash drift")

    substring_registration = search.get("registered_train_substrings")
    if not isinstance(substring_registration, dict):
        raise InputError("missing registered train substring metadata")
    expected_substring_hash = str(substring_registration.get("sha256", ""))
    substring_payload = substring_path.read_bytes()
    actual_substring_hash = sha256_bytes(substring_payload)
    if actual_substring_hash != expected_substring_hash:
        raise InputError("registered train substring hash drift")
    try:
        substring_text = substring_payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise InputError("train substring table is not ASCII") from exc
    substring_order = tuple(substring_text.splitlines())
    expected_count = int(substring_registration.get("distinct_substring_count", -1))
    if len(substring_order) != expected_count:
        raise InputError("train substring count drift")
    if len(set(substring_order)) != len(substring_order):
        raise InputError("duplicate registered train substring")
    if any(not value or not value.isascii() or not value.islower() or not value.isalpha()
           for value in substring_order):
        raise InputError("malformed registered train substring")
    minimum = int(substring_registration.get("minimum_length", -1))
    maximum = int(substring_registration.get("maximum_length", -1))
    if any(not minimum <= len(value) <= maximum for value in substring_order):
        raise InputError("registered train substring length drift")
    expected_order = tuple(sorted(substring_order, key=lambda value: (len(value), value)))
    if substring_order != expected_order:
        raise InputError("registered train substring sort-order drift")

    primitive_rows = search.get("primitive_role_assignment")
    if not isinstance(primitive_rows, list) or len(primitive_rows) != EXPECTED_PRIMITIVE_COUNT:
        raise InputError("primitive-role count drift")
    primitives = tuple(
        Primitive(str(row["primitive_id"]), str(row["role"])) for row in primitive_rows
    )
    primitive_ids = [primitive.primitive_id for primitive in primitives]
    if len(set(primitive_ids)) != EXPECTED_PRIMITIVE_COUNT:
        raise InputError("duplicate primitive ID")

    deck = search.get("primitive_output_deck")
    if not isinstance(deck, dict):
        raise InputError("missing primitive output deck")
    cards_by_role: dict[str, tuple[Card, ...]] = {}
    all_card_ids: set[str] = set()
    all_nonempty_outputs: set[str] = set()
    for role, rows in deck.items():
        if not isinstance(rows, list):
            raise InputError(f"malformed deck role {role}")
        cards: list[Card] = []
        for row in rows:
            card_id = str(row["card_id"])
            output = str(row["output"])
            if card_id in all_card_ids:
                raise InputError(f"duplicate card ID {card_id}")
            all_card_ids.add(card_id)
            if output:
                if output in all_nonempty_outputs:
                    raise InputError(f"duplicate primitive output {output}")
                all_nonempty_outputs.add(output)
                if not output.isascii() or not output.islower() or not output.isalpha():
                    raise InputError(f"malformed output {output}")
            metadata = tuple(
                sorted(
                    (str(key), value)
                    for key, value in row.items()
                    if key not in {"card_id", "role", "output", "length"}
                )
            )
            cards.append(Card(card_id, str(role), output, len(output), metadata))
        cards.sort(key=lambda card: card.card_id)
        cards_by_role[str(role)] = tuple(cards)

    primitive_role_counts: dict[str, int] = {}
    for primitive in primitives:
        primitive_role_counts[primitive.role] = primitive_role_counts.get(primitive.role, 0) + 1
    if set(primitive_role_counts) != set(cards_by_role):
        raise InputError("primitive roles and deck roles differ")
    for role, count in primitive_role_counts.items():
        if len(cards_by_role[role]) != count:
            raise InputError(f"role/deck cardinality drift for {role}")

    merge_payload = merge_tree_path.read_text(encoding="ascii")
    merge_rows = list(csv.DictReader(io.StringIO(merge_payload), delimiter="\t"))
    if len(merge_rows) != EXPECTED_MERGE_COUNT:
        raise InputError("merge count drift")
    if [int(row["rank"]) for row in merge_rows] != list(range(1, EXPECTED_MERGE_COUNT + 1)):
        raise InputError("merge ranks are not contiguous and ordered")

    known_leaves: dict[str, tuple[str, ...]] = {
        primitive.primitive_id: (primitive.primitive_id,) for primitive in primitives
    }
    known_depth: dict[str, int] = {primitive.primitive_id: 0 for primitive in primitives}
    raw_merges: list[tuple[dict[str, str], tuple[str, ...]]] = []
    merge_names: set[str] = set()
    for row in merge_rows:
        left = row["left"]
        right = row["right"]
        merged = row["merged"]
        if merged in known_leaves or left not in known_leaves or right not in known_leaves:
            raise InputError(f"non-topological or duplicate merge {merged}")
        leaves = known_leaves[left] + known_leaves[right]
        registered_leaves = tuple(row["leaf_sequence"].split())
        if leaves != registered_leaves or len(leaves) != int(row["leaf_count"]):
            raise InputError(f"leaf expansion drift at {merged}")
        depth = 1 + max(known_depth[left], known_depth[right])
        if depth != int(row["tree_depth"]):
            raise InputError(f"tree-depth drift at {merged}")
        known_leaves[merged] = leaves
        known_depth[merged] = depth
        merge_names.add(merged)
        raw_merges.append((row, leaves))

    rank_by_name = {row["merged"]: int(row["rank"]) for row in merge_rows}

    @lru_cache(maxsize=None)
    def descendant_ranks(name: str) -> tuple[int, ...]:
        if name not in rank_by_name:
            return ()
        row = merge_rows[rank_by_name[name] - 1]
        ranks = {
            rank_by_name[name],
            *descendant_ranks(row["left"]),
            *descendant_ranks(row["right"]),
        }
        return tuple(sorted(ranks))

    primitive_role = {primitive.primitive_id: primitive.role for primitive in primitives}
    merges: list[Merge] = []
    for row, leaves in raw_merges:
        if not any(
            any(card.output for card in cards_by_role[primitive_role[leaf]])
            for leaf in leaves
        ):
            raise InputError(f"merge can render empty: {row['merged']}")
        merges.append(
            Merge(
                rank=int(row["rank"]),
                left=row["left"],
                right=row["right"],
                merged=row["merged"],
                leaves=leaves,
                leaf_count=int(row["leaf_count"]),
                tree_depth=int(row["tree_depth"]),
                merge_descendant_ranks=descendant_ranks(row["merged"]),
            )
        )
    if len({merge.merged for merge in merges}) != EXPECTED_MERGE_COUNT:
        raise InputError("duplicate named merge")

    search_budget = int(search["search"]["stage0_core_hit_budget_maximum"])
    if search_budget != EXPECTED_HIT_BUDGET:
        raise InputError("registered Stage-0 hit budget drift")
    registered_objectives = search["search"].get("selection_objectives")
    expected_objectives = [
        "maximize raw train-substring-supported merge count",
        "minimize exact paid-subtree hitting number",
        "lexicographically minimize primitive card-id sequence",
    ]
    if registered_objectives != expected_objectives:
        raise InputError("registered objective hierarchy drift")

    return RegisteredInputs(
        search_path=search_path,
        substring_path=substring_path,
        merge_tree_path=merge_tree_path,
        search_sha256=sha256_bytes(search_payload),
        substring_sha256=actual_substring_hash,
        merge_tree_sha256=actual_merge_hash,
        search=search,
        primitives=primitives,
        cards_by_role=cards_by_role,
        merges=tuple(merges),
        substrings=frozenset(substring_order),
        substring_order=substring_order,
    )


def build_boolean_model(inputs: RegisteredInputs) -> BooleanModel:
    primitive_roles = {
        primitive.primitive_id: primitive.role for primitive in inputs.primitives
    }
    assignment: dict[tuple[str, str], z3.BoolRef] = {}
    assertions: list[z3.BoolRef] = []
    for primitive in inputs.primitives:
        row = []
        for card in inputs.cards_by_role[primitive.role]:
            variable = z3.Bool(f"x__{primitive.primitive_id}__{card.card_id}")
            assignment[(primitive.primitive_id, card.card_id)] = variable
            row.append((variable, 1))
        assertions.append(z3.PbEq(row, 1))

    for role, cards in inputs.cards_by_role.items():
        role_primitives = [
            primitive for primitive in inputs.primitives if primitive.role == role
        ]
        for card in cards:
            assertions.append(
                z3.PbEq(
                    [
                        (assignment[(primitive.primitive_id, card.card_id)], 1)
                        for primitive in role_primitives
                    ],
                    1,
                )
            )

    trie = ByteTrie(inputs.substring_order)
    registry = MDDRegistry(trie, primitive_roles, inputs.cards_by_role)
    roots = [registry.build(merge.leaves) for merge in inputs.merges]
    node_variables = [z3.Bool(f"mdd__{node_id}") for node_id in range(len(registry.nodes))]
    for node_id, node in enumerate(registry.nodes):
        terms: list[z3.BoolRef] = []
        for card_id, child in node.arcs:
            selected = assignment[(node.primitive_id, card_id)]
            if child == MDDRegistry.ACCEPT:
                terms.append(selected)
            else:
                terms.append(z3.And(selected, node_variables[child]))
        assertions.append(node_variables[node_id] == z3.Or(*terms))

    support = tuple(z3.Bool(f"support__{merge.rank:02d}") for merge in inputs.merges)
    for variable, root in zip(support, roots):
        if root == MDDRegistry.INVALID:
            assertions.append(z3.Not(variable))
        elif root == MDDRegistry.ACCEPT:
            assertions.append(variable)
        else:
            assertions.append(variable == node_variables[root])

    core_hit = tuple(z3.Bool(f"core_hit__{rank:02d}") for rank in range(1, 65))
    assertions.append(z3.PbLe([(variable, 1) for variable in core_hit], EXPECTED_HIT_BUDGET))
    for merge, supported in zip(inputs.merges, support):
        assertions.append(
            z3.Or(
                supported,
                *[core_hit[rank - 1] for rank in merge.merge_descendant_ranks],
            )
        )

    return BooleanModel(
        assertions=tuple(assertions),
        assignment=assignment,
        support=support,
        core_hit=core_hit,
        mdd_node_count=len(registry.nodes),
        mdd_arc_count=registry.arc_count,
    )


def pb_at_least(variables: Sequence[z3.BoolRef], threshold: int) -> z3.BoolRef:
    if threshold <= 0:
        return z3.BoolVal(True)
    if threshold > len(variables):
        return z3.BoolVal(False)
    return z3.PbGe([(variable, 1) for variable in variables], threshold)


def pb_at_most(variables: Sequence[z3.BoolRef], threshold: int) -> z3.BoolRef:
    if threshold < 0:
        return z3.BoolVal(False)
    if threshold >= len(variables):
        return z3.BoolVal(True)
    return z3.PbLe([(variable, 1) for variable in variables], threshold)


def pb_exactly(variables: Sequence[z3.BoolRef], count: int) -> z3.BoolRef:
    if count < 0 or count > len(variables):
        return z3.BoolVal(False)
    return z3.PbEq([(variable, 1) for variable in variables], count)


def model_bool(model: z3.ModelRef, variable: z3.BoolRef) -> bool:
    return z3.is_true(model.eval(variable, model_completion=True))


def assignment_from_model(
    model: z3.ModelRef, inputs: RegisteredInputs, boolean_model: BooleanModel
) -> dict[str, Card]:
    result: dict[str, Card] = {}
    for primitive in inputs.primitives:
        selected = [
            card
            for card in inputs.cards_by_role[primitive.role]
            if model_bool(
                model, boolean_model.assignment[(primitive.primitive_id, card.card_id)]
            )
        ]
        if len(selected) != 1:
            raise RuntimeError(f"model does not bind {primitive.primitive_id} exactly once")
        result[primitive.primitive_id] = selected[0]
    return result


def render_merges(
    inputs: RegisteredInputs, mapping: Mapping[str, Card]
) -> tuple[tuple[str, bool], ...]:
    rendered = []
    for merge in inputs.merges:
        value = "".join(mapping[primitive_id].output for primitive_id in merge.leaves)
        if not value:
            raise RuntimeError(f"empty raw render for {merge.merged}")
        rendered.append((value, value in inputs.substrings))
    return tuple(rendered)


def exact_minimum_cover(
    inputs: RegisteredInputs, supported: Sequence[bool]
) -> tuple[int, ...]:
    """Return the lexicographically earliest exact minimum cover (zero based)."""

    unsupported_ranks = [index for index, value in enumerate(supported) if not value]
    universe = 0
    for rank in unsupported_ranks:
        universe |= 1 << rank
    coverage = [0] * EXPECTED_MERGE_COUNT
    candidates_by_constraint: dict[int, tuple[int, ...]] = {}
    for rank in unsupported_ranks:
        candidates = tuple(
            descendant_rank - 1
            for descendant_rank in inputs.merges[rank].merge_descendant_ranks
        )
        candidates_by_constraint[rank] = candidates
        for candidate in candidates:
            coverage[candidate] |= 1 << rank

    @lru_cache(maxsize=None)
    def solve(uncovered: int) -> tuple[int, ...] | None:
        if uncovered == 0:
            return ()
        active_constraints = [
            rank for rank in unsupported_ranks if uncovered & (1 << rank)
        ]
        pivot = min(
            active_constraints,
            key=lambda rank: (
                len(
                    {
                        coverage[candidate] & uncovered
                        for candidate in candidates_by_constraint[rank]
                    }
                ),
                rank,
            ),
        )
        best: tuple[int, ...] | None = None
        candidates = sorted(
            candidates_by_constraint[pivot],
            key=lambda candidate: (-((coverage[candidate] & uncovered).bit_count()), candidate),
        )
        for candidate in candidates:
            following = uncovered & ~coverage[candidate]
            if following == uncovered:
                continue
            suffix = solve(following)
            if suffix is None:
                continue
            proposal = tuple(sorted((candidate, *suffix)))
            if best is None or (len(proposal), proposal) < (len(best), best):
                best = proposal
        return best

    result = solve(universe)
    if result is None:
        raise RuntimeError("merge cover unexpectedly infeasible")
    if len(set(result)) != len(result):
        raise RuntimeError("minimum cover contains duplicate node")
    return result


def negative_control_mapping(inputs: RegisteredInputs) -> dict[str, Card]:
    """Reconstruct the registered GDT614 binding by role-wise listed order."""

    result: dict[str, Card] = {}
    for role, cards in inputs.cards_by_role.items():
        primitives = [primitive for primitive in inputs.primitives if primitive.role == role]
        if len(primitives) != len(cards):
            raise RuntimeError("negative-control role cardinality mismatch")
        for primitive, card in zip(primitives, cards):
            result[primitive.primitive_id] = card
    return result


class QueryRunner:
    def __init__(
        self,
        work_dir: Path,
        base_assertions: Sequence[z3.BoolRef],
        deadline: float,
        workers: int,
    ):
        self.work_dir = work_dir
        self.base_assertions = tuple(base_assertions)
        self.deadline = deadline
        self.workers = workers
        self.records: list[dict[str, object]] = []
        self.diagnostics: list[dict[str, object]] = []
        self.counter = 0
        self.query_path = work_dir / "QUERY_CERTIFICATES.jsonl"
        self.diagnostic_path = work_dir / "QUERY_DIAGNOSTICS.jsonl"

    def new_solver(self, extras: Iterable[z3.BoolRef] = ()) -> z3.Solver:
        solver = z3.SolverFor("QF_FD")
        solver.add(*self.base_assertions)
        solver.add(*tuple(extras))
        return solver

    def check(
        self,
        solver: z3.Solver,
        phase: str,
        constraint: Mapping[str, object],
        extras: Sequence[z3.BoolRef] = (),
    ) -> tuple[z3.CheckSatResult, z3.ModelRef | None, str]:
        self.counter += 1
        query_id = f"Q{self.counter:04d}"
        remaining_ms = int((self.deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            raise SearchIncomplete("registered wall-clock limit exhausted")
        solver.set(timeout=remaining_ms)
        before = time.monotonic()
        solver.push()
        if extras:
            solver.add(*extras)
        status = solver.check()
        elapsed = time.monotonic() - before
        model = solver.model() if status == z3.sat else None
        reason = solver.reason_unknown() if status == z3.unknown else ""
        solver.pop()
        record = {
            "query_id": query_id,
            "phase": phase,
            "constraint": dict(constraint),
            "result": str(status),
        }
        diagnostic = {
            "query_id": query_id,
            "elapsed_seconds": elapsed,
            "remaining_seconds_after": max(0.0, self.deadline - time.monotonic()),
            "reason_unknown": reason,
        }
        self.records.append(record)
        self.diagnostics.append(diagnostic)
        with self.query_path.open("ab") as handle:
            handle.write(canonical_json(record))
        with self.diagnostic_path.open("ab") as handle:
            handle.write(canonical_json(diagnostic))
        print(
            f"{query_id} {phase}: {status} ({elapsed:.3f}s)",
            flush=True,
        )
        if status == z3.unknown:
            raise SearchIncomplete(f"Z3 returned unknown: {reason}")
        return status, model, query_id


def lex_key_less_constraint(
    inputs: RegisteredInputs,
    boolean_model: BooleanModel,
    final_mapping: Mapping[str, Card],
) -> z3.BoolRef:
    prefixes: list[z3.BoolRef] = []
    equal_prefix: list[z3.BoolRef] = []
    for primitive in inputs.primitives:
        final_card = final_mapping[primitive.primitive_id]
        smaller = [
            boolean_model.assignment[(primitive.primitive_id, card.card_id)]
            for card in inputs.cards_by_role[primitive.role]
            if card.card_id < final_card.card_id
        ]
        if smaller:
            prefixes.append(z3.And(*equal_prefix, z3.Or(*smaller)))
        equal_prefix.append(
            boolean_model.assignment[(primitive.primitive_id, final_card.card_id)]
        )
    return z3.Or(*prefixes) if prefixes else z3.BoolVal(False)


def cover_tuple_less_constraint(
    core_hit: Sequence[z3.BoolRef], witness_zero_based: Sequence[int]
) -> z3.BoolRef:
    witness = set(witness_zero_based)
    equal_prefix: list[z3.BoolRef] = []
    earlier: list[z3.BoolRef] = []
    for rank, variable in enumerate(core_hit):
        if rank not in witness:
            earlier.append(z3.And(*equal_prefix, variable))
            equal_prefix.append(z3.Not(variable))
        else:
            equal_prefix.append(variable)
    return z3.Or(*earlier) if earlier else z3.BoolVal(False)


def mapping_constraints(
    inputs: RegisteredInputs,
    boolean_model: BooleanModel,
    mapping: Mapping[str, Card],
) -> tuple[z3.BoolRef, ...]:
    return tuple(
        boolean_model.assignment[(primitive.primitive_id, mapping[primitive.primitive_id].card_id)]
        for primitive in inputs.primitives
    )


def run_exact_search(
    inputs: RegisteredInputs,
    boolean_model: BooleanModel,
    work_dir: Path,
    time_limit_seconds: int,
    workers: int,
) -> dict[str, object]:
    started = time.monotonic()
    deadline = started + time_limit_seconds
    runner = QueryRunner(work_dir, boolean_model.assertions, deadline, workers)
    solver = runner.new_solver()

    status, existence_model, _ = runner.check(
        solver,
        "existence",
        {"core_hit_maximum": EXPECTED_HIT_BUDGET},
    )
    if status == z3.unsat:
        return {
            "schema": SCHEMA,
            "decision": "NO_EIGHT_HIT_BINDING",
            "z3_version": z3.get_version_string(),
            "query_count": runner.counter,
        }
    assert existence_model is not None
    initial_support = sum(
        model_bool(existence_model, variable) for variable in boolean_model.support
    )

    lower = initial_support
    upper = EXPECTED_MERGE_COUNT + 1
    while upper - lower > 1:
        middle = (lower + upper) // 2
        trial_status, _, _ = runner.check(
            solver,
            "maximize_support",
            {"support_at_least": middle},
            [pb_at_least(boolean_model.support, middle)],
        )
        if trial_status == z3.sat:
            lower = middle
        else:
            upper = middle
    optimum_support = lower
    boundary_sat, _, _ = runner.check(
        solver,
        "support_boundary_sat",
        {"support_at_least": optimum_support},
        [pb_at_least(boolean_model.support, optimum_support)],
    )
    boundary_unsat, _, _ = runner.check(
        solver,
        "support_boundary_unsat",
        {"support_at_least": optimum_support + 1},
        [pb_at_least(boolean_model.support, optimum_support + 1)],
    )
    if boundary_sat != z3.sat or boundary_unsat != z3.unsat:
        raise RuntimeError("support optimum boundary replay failed")
    solver.add(pb_exactly(boolean_model.support, optimum_support))

    lower_k = -1
    upper_k = EXPECTED_HIT_BUDGET
    while upper_k - lower_k > 1:
        middle = (lower_k + upper_k) // 2
        trial_status, _, _ = runner.check(
            solver,
            "minimize_cover",
            {"core_hit_at_most": middle},
            [pb_at_most(boolean_model.core_hit, middle)],
        )
        if trial_status == z3.sat:
            upper_k = middle
        else:
            lower_k = middle
    optimum_cover = upper_k
    cover_sat, cover_model, _ = runner.check(
        solver,
        "cover_boundary_sat",
        {"core_hit_at_most": optimum_cover},
        [pb_at_most(boolean_model.core_hit, optimum_cover)],
    )
    cover_unsat, _, _ = runner.check(
        solver,
        "cover_boundary_unsat",
        {"core_hit_at_most": optimum_cover - 1},
        [pb_at_most(boolean_model.core_hit, optimum_cover - 1)],
    )
    if cover_sat != z3.sat or cover_unsat != z3.unsat or cover_model is None:
        raise RuntimeError("cover optimum boundary replay failed")
    solver.add(pb_at_most(boolean_model.core_hit, optimum_cover))

    current_model = cover_model
    for primitive in inputs.primitives:
        cards = inputs.cards_by_role[primitive.role]
        current = next(
            card
            for card in cards
            if model_bool(
                current_model,
                boolean_model.assignment[(primitive.primitive_id, card.card_id)],
            )
        )
        chosen: Card | None = None
        for card in cards:
            if card.card_id >= current.card_id:
                break
            trial_status, trial_model, _ = runner.check(
                solver,
                "lexicographic_key",
                {"primitive_id": primitive.primitive_id, "try_card_id": card.card_id},
                [boolean_model.assignment[(primitive.primitive_id, card.card_id)]],
            )
            if trial_status == z3.sat:
                assert trial_model is not None
                chosen = card
                current_model = trial_model
                break
        if chosen is None:
            chosen = current
        solver.add(boolean_model.assignment[(primitive.primitive_id, chosen.card_id)])

    final_status, final_model, _ = runner.check(
        solver,
        "final_key_sat",
        {"support": optimum_support, "minimum_cover": optimum_cover},
    )
    if final_status != z3.sat or final_model is None:
        raise RuntimeError("final lexicographic key is not SAT")
    final_mapping = assignment_from_model(final_model, inputs, boolean_model)

    proof_solver = runner.new_solver(
        [
            pb_exactly(boolean_model.support, optimum_support),
            pb_at_most(boolean_model.core_hit, optimum_cover),
        ]
    )
    lex_unsat, _, _ = runner.check(
        proof_solver,
        "lexicographic_key_predecessor_unsat",
        {
            "support": optimum_support,
            "core_hit_at_most": optimum_cover,
            "key_less_than": [
                final_mapping[primitive.primitive_id].card_id
                for primitive in inputs.primitives
            ],
        },
        [lex_key_less_constraint(inputs, boolean_model, final_mapping)],
    )
    if lex_unsat != z3.unsat:
        raise RuntimeError("lexicographic key predecessor unexpectedly SAT")

    rendered = render_merges(inputs, final_mapping)
    supported = tuple(value[1] for value in rendered)
    if sum(supported) != optimum_support:
        raise RuntimeError("direct support replay disagrees with Z3 optimum")
    canonical_cover = exact_minimum_cover(inputs, supported)
    if len(canonical_cover) != optimum_cover:
        raise RuntimeError("independent fixed-map cover replay disagrees with Z3")

    fixed_extras = [
        pb_exactly(boolean_model.support, optimum_support),
        pb_exactly(boolean_model.core_hit, optimum_cover),
        *mapping_constraints(inputs, boolean_model, final_mapping),
    ]
    witness_solver = runner.new_solver(fixed_extras)
    witness_sat, _, _ = runner.check(
        witness_solver,
        "canonical_cover_sat",
        {"ascending_merge_ranks": [rank + 1 for rank in canonical_cover]},
        [
            *[boolean_model.core_hit[rank] for rank in canonical_cover],
            *[
                z3.Not(variable)
                for rank, variable in enumerate(boolean_model.core_hit)
                if rank not in set(canonical_cover)
            ],
        ],
    )
    witness_predecessor, _, _ = runner.check(
        witness_solver,
        "canonical_cover_predecessor_unsat",
        {"tuple_less_than": [rank + 1 for rank in canonical_cover]},
        [cover_tuple_less_constraint(boolean_model.core_hit, canonical_cover)],
    )
    if witness_sat != z3.sat or witness_predecessor != z3.unsat:
        raise RuntimeError("canonical cover certificate failed")

    old_mapping = negative_control_mapping(inputs)
    old_rendered = render_merges(inputs, old_mapping)
    old_cover = exact_minimum_cover(inputs, [value[1] for value in old_rendered])
    negative_registration = inputs.search["negative_control"]
    expected_old_minimum = int(
        negative_registration["gdt615_train_only_expected_exact_minimum"]
    )
    expected_old_support = int(
        negative_registration["gdt615_train_only_raw_supported_merge_count"]
    )
    old_support = sum(value[1] for value in old_rendered)
    if old_support != expected_old_support:
        raise RuntimeError(
            f"negative-control support drift: {old_support} != {expected_old_support}"
        )
    if len(old_cover) != expected_old_minimum:
        raise RuntimeError(
            f"negative-control minimum drift: {len(old_cover)} != {expected_old_minimum}"
        )

    result = {
        "schema": SCHEMA,
        "decision": "STAGE0_MAPPING_BOUND_PASS",
        "model_id": EXPECTED_MODEL_ID,
        "input_hashes": {
            "REGISTERED_SEARCH.json": inputs.search_sha256,
            "REGISTERED_TRAIN_SUBSTRINGS.txt": inputs.substring_sha256,
            "merge_tree.tsv": inputs.merge_tree_sha256,
        },
        "solver": {
            "backend": "z3/QF_FD Boolean one-hot + reduced MDD + PB",
            "z3_version": z3.get_version_string(),
            "workers_requested": workers,
            "registered_time_limit_seconds": time_limit_seconds,
            "mdd_nodes": boolean_model.mdd_node_count,
            "mdd_arcs": boolean_model.mdd_arc_count,
            "base_assertions": len(boolean_model.assertions),
            "query_count": runner.counter,
        },
        "objective": {
            "raw_train_supported_named_merges": optimum_support,
            "exact_minimum_core_hit": optimum_cover,
            "lexicographic_card_id_sequence": [
                final_mapping[primitive.primitive_id].card_id
                for primitive in inputs.primitives
            ],
        },
        "mapping": [
            {
                "primitive_id": primitive.primitive_id,
                "role": primitive.role,
                **final_mapping[primitive.primitive_id].as_dict(),
            }
            for primitive in inputs.primitives
        ],
        "raw_merges": [
            {
                "rank": merge.rank,
                "merge": merge.merged,
                "leaves": list(merge.leaves),
                "raw_render": rendered[index][0],
                "train_substring_member": rendered[index][1],
                "inclusive_recursive_merge_subtree_ranks": list(
                    merge.merge_descendant_ranks
                ),
            }
            for index, merge in enumerate(inputs.merges)
        ],
        "canonical_minimum_cover": [
            {
                "rank": rank + 1,
                "merge": inputs.merges[rank].merged,
            }
            for rank in canonical_cover
        ],
        "negative_control": {
            "relation": "GDT615_TRAIN_ONLY",
            "expected_raw_supported_merges": expected_old_support,
            "replayed_raw_supported_merges": old_support,
            "expected_exact_minimum": expected_old_minimum,
            "replayed_exact_minimum": len(old_cover),
            "canonical_cover_ranks": [rank + 1 for rank in old_cover],
            "historical_gdt614_train_intersection_held_minimum_not_replayed": int(
                negative_registration[
                    "published_gdt614_train_intersection_held_exact_minimum"
                ]
            ),
        },
        "query_certificate_file": "QUERY_CERTIFICATES.jsonl",
        "base_encoding_file": "BASE_ENCODING.smt2",
    }
    return result


def write_tabular_artifacts(work_dir: Path, result: Mapping[str, object]) -> None:
    mapping_lines = ["primitive_id\trole\tcard_id\toutput\tlength"]
    for row in result.get("mapping", []):
        mapping_lines.append(
            "\t".join(
                str(row[key])
                for key in ("primitive_id", "role", "card_id", "output", "length")
            )
        )
    atomic_write(work_dir / "mapping.tsv", ("\n".join(mapping_lines) + "\n").encode())

    merge_lines = [
        "rank\tmerge\tleaves\traw_render\ttrain_substring_member\tinclusive_subtree_ranks"
    ]
    for row in result.get("raw_merges", []):
        merge_lines.append(
            "\t".join(
                [
                    str(row["rank"]),
                    str(row["merge"]),
                    ",".join(row["leaves"]),
                    str(row["raw_render"]),
                    "1" if row["train_substring_member"] else "0",
                    ",".join(str(value) for value in row["inclusive_recursive_merge_subtree_ranks"]),
                ]
            )
        )
    atomic_write(work_dir / "raw_merges.tsv", ("\n".join(merge_lines) + "\n").encode())

    cover_lines = ["rank\tmerge"]
    for row in result.get("canonical_minimum_cover", []):
        cover_lines.append(f"{row['rank']}\t{row['merge']}")
    atomic_write(
        work_dir / "minimum_cover.tsv", ("\n".join(cover_lines) + "\n").encode()
    )


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registered-search", type=Path, required=True)
    parser.add_argument("--train-substrings", type=Path, required=True)
    parser.add_argument("--merge-tree", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--time-limit-seconds", type=int, default=14_400)
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    if not 1 <= args.time_limit_seconds <= REGISTERED_TIME_LIMIT_SECONDS:
        raise SystemExit(
            "--time-limit-seconds must be in "
            f"1..{REGISTERED_TIME_LIMIT_SECONDS}"
        )
    if not 1 <= args.workers <= 32:
        raise SystemExit("--workers must be in 1..32")
    work_dir = args.work_dir.resolve()
    if work_dir.exists() and any(work_dir.iterdir()):
        raise SystemExit(f"refusing nonempty work directory: {work_dir}")
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        inputs = load_registered_inputs(
            args.registered_search.resolve(),
            args.train_substrings.resolve(),
            args.merge_tree.resolve(),
        )
        print(
            f"validated inputs: {len(inputs.primitives)} primitives, "
            f"{len(inputs.merges)} merges, {len(inputs.substrings)} train substrings",
            flush=True,
        )
        boolean_model = build_boolean_model(inputs)
        print(
            f"built MDD: {boolean_model.mdd_node_count} nodes, "
            f"{boolean_model.mdd_arc_count} arcs, "
            f"{len(boolean_model.assertions)} assertions",
            flush=True,
        )

        encoding_solver = z3.SolverFor("QF_FD")
        encoding_solver.add(*boolean_model.assertions)
        encoding = encoding_solver.to_smt2().encode("utf-8")
        atomic_write(work_dir / "BASE_ENCODING.smt2", encoding)
        atomic_write_json(
            work_dir / "INPUT_MANIFEST.json",
            {
                "REGISTERED_SEARCH.json": inputs.search_sha256,
                "REGISTERED_TRAIN_SUBSTRINGS.txt": inputs.substring_sha256,
                "merge_tree.tsv": inputs.merge_tree_sha256,
                "BASE_ENCODING.smt2": sha256_bytes(encoding),
                "solver_source": sha256_path(Path(__file__).resolve()),
                "z3_version": z3.get_version_string(),
            },
        )
        result = run_exact_search(
            inputs,
            boolean_model,
            work_dir,
            args.time_limit_seconds,
            args.workers,
        )
        atomic_write_json(work_dir / "RESULT.json", result)
        if result.get("decision") == "STAGE0_MAPPING_BOUND_PASS":
            write_tabular_artifacts(work_dir, result)
        result_hash = sha256_path(work_dir / "RESULT.json")
        atomic_write(work_dir / "RESULT.sha256", (result_hash + "\n").encode())
        atomic_write_json(
            work_dir / "COMPLETE.json",
            {
                "schema": "gdt615-stage0-primary-run-state-v1",
                "status": "COMPLETE",
                "decision": result["decision"],
                "result_sha256": result_hash,
            },
        )
        print(json.dumps(result.get("objective", result), sort_keys=True), flush=True)
        return 0
    except SearchIncomplete as exc:
        atomic_write_json(
            work_dir / "INCOMPLETE.json",
            {
                "schema": "gdt615-stage0-primary-run-state-v1",
                "status": "SEARCH_INCOMPLETE",
                "reason": str(exc),
            },
        )
        print(f"SEARCH_INCOMPLETE: {exc}", file=sys.stderr, flush=True)
        return 2
    except Exception as exc:
        failure_path = work_dir / "FAILURE.json"
        if not failure_path.exists():
            atomic_write_json(
                failure_path,
                {
                    "schema": "gdt615-stage0-primary-run-state-v1",
                    "status": "IMPLEMENTATION_OR_VALIDATION_FAILURE",
                    "exception_type": type(exc).__name__,
                    "reason": str(exc),
                },
            )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
