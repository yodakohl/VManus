#!/usr/bin/env python3
"""Exact TRAIN-only joint child-feasible binding bound for GDT616.

This program deliberately solves only the finite Stage-A necessary model.  It
does not build W0 and it does not choose a mapping that downstream work may
freeze.  A SAT witness is a deterministic certificate that the Stage-A space
is nonempty; Stage B must search the complete Stage-A-feasible space jointly.

The scientific inputs are the registered GDT608 merge tree, the frozen GDT614
deck/grammar, and GDT615's complete TRAIN-substring table and same-role deck.
No held, lm_confirm, Voynich target, f84, or f84r path is accepted.
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
from pathlib import Path
from typing import Mapping, Sequence

import z3


SCHEMA = "gdt616-primary-joint-child-feasible-bound-v1"
MODEL_NAME = "EXACT_FINITE_TRAIN_ONLY_NECESSARY_STAGE_A"
EXPECTED_SEARCH_SCHEMA = "gdt616-joint-child-feasible-binding-registration-v1"
EXPECTED_MODEL_SCHEMA = "gdt614-registered-core-run-macro-v1"
EXPECTED_PRIMITIVES = 34
EXPECTED_MERGES = 64
EXPECTED_PAID = 8
EXPECTED_SHORT = 4
EXPECTED_MACRO = 4
MAX_SECONDS = 43_200


class BoundError(RuntimeError):
    """An input or exact-model invariant failed."""


class SearchIncomplete(RuntimeError):
    """The exact solver returned unknown or exhausted the time budget."""


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise BoundError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
INPUT_PATHS: Mapping[str, Path] = {
    "GDT616_REGISTERED_SEARCH.json": EXPERIMENT / "artifacts/REGISTERED_SEARCH.json",
    "REGISTERED_TRAIN_SUBSTRINGS.txt": ROOT
    / "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt",
    "REGISTERED_MODEL.json": ROOT
    / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json",
    "merge_tree.tsv": ROOT
    / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv",
}
EXPECTED_SHA256: Mapping[str, str] = {
    "GDT616_REGISTERED_SEARCH.json": (
        "281fe360e6e3eda19323f5e62a99fe4822546b136f7ca91b85fdf4552e565aae"
    ),
    "REGISTERED_TRAIN_SUBSTRINGS.txt": (
        "5b6859d8656f63cf8e8cf89221ae8ff1dea345e135a6cd012248b9b4c4ff14a9"
    ),
    "REGISTERED_MODEL.json": (
        "ed841dc254a961650a8bda8bdc6024b67655f6bdc96e5dab2aec02f1686ecc42"
    ),
    "merge_tree.tsv": (
        "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a"
    ),
}


@dataclass(frozen=True)
class Card:
    card_id: str
    role: str
    output: str
    side_license: str | None = None


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


@dataclass(frozen=True)
class Instance:
    primitives: tuple[Primitive, ...]
    cards_by_role: Mapping[str, tuple[Card, ...]]
    paid_cards: tuple[Card, ...]
    merges: tuple[Merge, ...]
    train_substrings: frozenset[str]
    qok_paid_macro_forbidden: bool = True

    def validate(self) -> None:
        primitive_ids = [row.primitive_id for row in self.primitives]
        if not primitive_ids or len(set(primitive_ids)) != len(primitive_ids):
            raise BoundError("primitive IDs must be nonempty and unique")
        role_counts: dict[str, int] = {}
        for primitive in self.primitives:
            role_counts[primitive.role] = role_counts.get(primitive.role, 0) + 1
        if set(role_counts) != set(self.cards_by_role):
            raise BoundError("primitive roles and primitive deck roles differ")
        primitive_card_ids: set[str] = set()
        nonempty_outputs: list[str] = []
        for role, count in role_counts.items():
            cards = self.cards_by_role[role]
            if len(cards) != count:
                raise BoundError(f"role/deck cardinality mismatch for {role}")
            if tuple(sorted(cards, key=lambda card: card.card_id)) != cards:
                raise BoundError(f"primitive cards are not sorted for {role}")
            for card in cards:
                if card.role != role:
                    raise BoundError(f"primitive card role mismatch for {card.card_id}")
                if card.card_id in primitive_card_ids:
                    raise BoundError(f"duplicate primitive card ID {card.card_id}")
                primitive_card_ids.add(card.card_id)
                _validate_output(card.output, f"primitive card {card.card_id}", True)
                if card.output:
                    nonempty_outputs.append(card.output)

        if not self.paid_cards:
            raise BoundError("paid deck is empty")
        if tuple(sorted(self.paid_cards, key=lambda card: card.card_id)) != self.paid_cards:
            raise BoundError("paid cards are not sorted")
        paid_ids = [card.card_id for card in self.paid_cards]
        if len(set(paid_ids)) != len(paid_ids):
            raise BoundError("duplicate paid card ID")
        for card in self.paid_cards:
            if card.role not in {"short_card", "macro_core"}:
                raise BoundError(f"unexpected paid-card role {card.role}")
            _validate_output(card.output, f"paid card {card.card_id}", False)
            nonempty_outputs.append(card.output)
        if len(nonempty_outputs) != len(set(nonempty_outputs)):
            raise BoundError("nonempty primitive and paid outputs are not globally distinct")

        known = set(primitive_ids)
        merge_names: set[str] = set()
        for expected_rank, merge in enumerate(self.merges, 1):
            if merge.rank != expected_rank:
                raise BoundError("merge ranks must be contiguous and ordered")
            if merge.merged in known or merge.left not in known or merge.right not in known:
                raise BoundError(f"non-topological or duplicate merge {merge.merged}")
            known.add(merge.merged)
            merge_names.add(merge.merged)
        if len(merge_names) != len(self.merges):
            raise BoundError("duplicate merge name")
        if not self.train_substrings or "" in self.train_substrings:
            raise BoundError("TRAIN substring relation must be nonempty and exclude empty")
        for value in self.train_substrings:
            _validate_output(value, "TRAIN substring", False)


@dataclass(frozen=True)
class RelationRow:
    left: str
    right: str
    child: str


@dataclass(frozen=True)
class Compiled:
    instance: Instance
    effective_domains: Mapping[str, tuple[str, ...]]
    child_domains: Mapping[str, tuple[str, ...]]
    relations: Mapping[str, tuple[RelationRow, ...]]
    permitted_paid_ids: Mapping[str, frozenset[str]]
    values: tuple[str, ...]
    value_id: Mapping[str, int]


@dataclass(frozen=True)
class Encoding:
    compiled: Compiled
    assertions: tuple[z3.BoolRef, ...]
    mapping_index: Mapping[str, z3.IntNumRef | z3.ArithRef]
    effective: Mapping[str, z3.IntNumRef | z3.ArithRef]
    child: Mapping[str, z3.IntNumRef | z3.ArithRef]
    paid_assignment: Mapping[tuple[int, str], z3.BoolRef]
    structural_certificate: Mapping[str, object]


def _validate_output(value: str, label: str, allow_empty: bool) -> None:
    if not isinstance(value, str):
        raise BoundError(f"{label} output is not a string")
    if not value and allow_empty:
        return
    if not value or not value.isascii() or not value.isalpha() or not value.islower():
        raise BoundError(f"malformed {label} output {value!r}")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    if path.exists() or temporary.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    with temporary.open("xb") as handle:
        handle.write(canonical_json(value))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _require_object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise BoundError(f"{label} must be an object")
    return value


def _require_array(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise BoundError(f"{label} must be an array")
    return value


def _card_from_row(raw: object, expected_role: str | None = None) -> Card:
    row = _require_object(raw, "card")
    try:
        card_id = str(row["card_id"])
        raw_role = row.get("role", expected_role)
        if raw_role is None:
            raise KeyError("role")
        role = str(raw_role)
        output = str(row["output"])
    except KeyError as exc:
        raise BoundError("card is missing a required field") from exc
    if expected_role is not None and role != expected_role:
        raise BoundError(f"card {card_id} role differs from its deck")
    side = row.get("side_license")
    if side is not None and not isinstance(side, str):
        raise BoundError(f"card {card_id} has malformed side license")
    return Card(card_id, role, output, side)


def load_registered_instance() -> tuple[Instance, dict[str, str]]:
    observed: dict[str, str] = {}
    for label, path in INPUT_PATHS.items():
        if not path.is_file():
            raise BoundError(f"missing registered input {label}")
        observed[label] = sha256_path(path)
    if observed != dict(EXPECTED_SHA256):
        wrong = sorted(label for label in observed if observed[label] != EXPECTED_SHA256[label])
        raise BoundError("registered input hash mismatch: " + ", ".join(wrong))

    try:
        search = json.loads(
            INPUT_PATHS["GDT616_REGISTERED_SEARCH.json"].read_text("utf-8")
        )
        model = json.loads(INPUT_PATHS["REGISTERED_MODEL.json"].read_text("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BoundError("cannot load registered JSON") from exc
    search = _require_object(search, "registered search")
    model = _require_object(model, "registered model")
    if search.get("schema") != EXPECTED_SEARCH_SCHEMA:
        raise BoundError("unexpected registered search schema")
    if model.get("schema") != EXPECTED_MODEL_SCHEMA:
        raise BoundError("unexpected registered model schema")
    if search.get("experiment_id") != "GDT616":
        raise BoundError("unexpected experiment ID in GDT616 registration")
    if search.get("model_id") != (
        "HISTORICAL_MIXED_ABBREVIATION_FST_34_CORE_RUN_MACRO_V4_JOINT_CHILD_FEASIBLE"
    ):
        raise BoundError("unexpected GDT616 model ID")

    direct_rows = [
        _require_object(row, "direct input hash")
        for row in _require_array(search.get("direct_input_hashes"), "direct input hashes")
    ]
    expected_direct_suffixes = {
        "merge_tree.tsv": observed["merge_tree.tsv"],
        "gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json": observed[
            "REGISTERED_MODEL.json"
        ],
        "gdt615_joint_output_permutation_recovery/artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt": observed[
            "REGISTERED_TRAIN_SUBSTRINGS.txt"
        ],
    }
    for suffix, digest in expected_direct_suffixes.items():
        matches = [
            str(row.get("sha256"))
            for row in direct_rows
            if str(row.get("path", "")).endswith(suffix)
        ]
        if matches != [digest]:
            raise BoundError(f"GDT616 direct-input binding mismatch for {suffix}")

    inventory = _require_object(search.get("inventory"), "registered inventory")
    primitive_rows = _require_array(
        inventory.get("primitive_role_assignment"), "primitive role assignment"
    )
    primitives: list[Primitive] = []
    for raw in primitive_rows:
        row = _require_object(raw, "primitive")
        primitives.append(Primitive(str(row["primitive_id"]), str(row["role"])))

    raw_deck = _require_object(inventory.get("primitive_output_deck"), "primitive deck")
    cards_by_role: dict[str, tuple[Card, ...]] = {}
    for role, raw_cards in raw_deck.items():
        cards = [_card_from_row(raw, str(role)) for raw in _require_array(raw_cards, str(role))]
        cards_by_role[str(role)] = tuple(sorted(cards, key=lambda card: card.card_id))

    paid_cards = tuple(
        sorted(
            (
                _card_from_row(raw)
                for raw in _require_array(inventory.get("paid_output_deck"), "paid deck")
            ),
            key=lambda card: card.card_id,
        )
    )
    model_paid = tuple(
        sorted(
            (_card_from_row(raw) for raw in _require_array(model.get("paid_card_deck"), "model paid deck")),
            key=lambda card: card.card_id,
        )
    )
    if paid_cards != model_paid:
        raise BoundError("GDT614 and GDT616 paid decks differ")

    constraints = _require_object(model.get("merge_constraints"), "merge constraints")
    expected_constraints = {
        "directed_order": "left_then_right",
        "paid_cards": EXPECTED_PAID,
        "paid_short_cards": EXPECTED_SHORT,
        "paid_macro_cards": EXPECTED_MACRO,
        "qok_paid_macro_forbidden": True,
        "default_merge_equals_recursive_children": True,
        "paid_output_must_differ_from_recursive_children": True,
    }
    for key, expected in expected_constraints.items():
        if constraints.get(key) != expected:
            raise BoundError(f"registered merge constraint drift: {key}")

    substring_payload = INPUT_PATHS["REGISTERED_TRAIN_SUBSTRINGS.txt"].read_bytes()
    try:
        substring_text = substring_payload.decode("ascii")
    except UnicodeError as exc:
        raise BoundError("TRAIN substring table is not ASCII") from exc
    if not substring_text.endswith("\n"):
        raise BoundError("TRAIN substring table lacks final newline")
    substring_order = substring_text.splitlines()
    if substring_order != sorted(set(substring_order), key=lambda value: (len(value), value)):
        raise BoundError("TRAIN substring table is not canonical")
    metadata = _require_object(search.get("train_substrings"), "TRAIN substring registration")
    if metadata.get("sha256") != observed["REGISTERED_TRAIN_SUBSTRINGS.txt"]:
        raise BoundError("TRAIN substring hash binding mismatch")
    if metadata.get("distinct_substring_count") != len(substring_order):
        raise BoundError("TRAIN substring count mismatch")

    merge_payload = INPUT_PATHS["merge_tree.tsv"].read_text(encoding="ascii")
    merge_rows = list(csv.DictReader(io.StringIO(merge_payload), delimiter="\t"))
    merges = tuple(
        Merge(int(row["rank"]), row["left"], row["right"], row["merged"])
        for row in merge_rows
    )
    if inventory.get("primitive_order") != [row.primitive_id for row in primitives]:
        raise BoundError("registered primitive order differs from inventory rows")
    if inventory.get("merge_count") != len(merges):
        raise BoundError("registered merge count differs from merge tree")
    if inventory.get("merge_rank_order") != [row.merged for row in merges]:
        raise BoundError("registered merge rank order differs from merge tree")
    limits = _require_object(search.get("limits"), "registered limits")
    if limits.get("wall_clock_seconds_maximum") != MAX_SECONDS:
        raise BoundError("registered wall-clock maximum drift")
    if limits.get("unknown_or_timeout_can_pass") is not False:
        raise BoundError("registration permits unknown or timeout to pass")
    variables = _require_object(search.get("variables"), "registered variables")
    if variables.get("actual_paid_locations") != EXPECTED_PAID:
        raise BoundError("registered paid-location count drift")
    if variables.get("relaxed_core_hit_variables") != "FORBIDDEN":
        raise BoundError("registration unexpectedly permits relaxed core-hit variables")
    selection = _require_object(search.get("stage_a_selection"), "Stage-A selection")
    if selection.get("sat_freezes_mapping_or_paid_assignment") is not False:
        raise BoundError("Stage-A registration unexpectedly freezes its witness")

    instance = Instance(
        primitives=tuple(primitives),
        cards_by_role=cards_by_role,
        paid_cards=paid_cards,
        merges=merges,
        train_substrings=frozenset(substring_order),
        qok_paid_macro_forbidden=True,
    )
    instance.validate()
    if len(instance.primitives) != EXPECTED_PRIMITIVES:
        raise BoundError("registered primitive count drift")
    if len(instance.merges) != EXPECTED_MERGES:
        raise BoundError("registered merge count drift")
    if len(instance.paid_cards) != EXPECTED_PAID:
        raise BoundError("registered paid-card count drift")
    if sum(card.role == "short_card" for card in instance.paid_cards) != EXPECTED_SHORT:
        raise BoundError("registered short-card count drift")
    if sum(card.role == "macro_core" for card in instance.paid_cards) != EXPECTED_MACRO:
        raise BoundError("registered macro-card count drift")
    return instance, observed


def _sorted_values(values: set[str] | frozenset[str]) -> tuple[str, ...]:
    return tuple(sorted(values, key=lambda value: (len(value), value)))


def _concat_relation(
    left_domain: frozenset[str],
    right_domain: frozenset[str],
    train_order: Sequence[str],
) -> tuple[RelationRow, ...]:
    """Enumerate exact allowed left/right concatenations without a Cartesian scan."""

    rows: list[RelationRow] = []
    left_lengths = {len(value) for value in left_domain}
    for child in train_order:
        for split in left_lengths:
            if split > len(child):
                continue
            left = child[:split]
            right = child[split:]
            if left in left_domain and right in right_domain:
                rows.append(RelationRow(left, right, child))
    rows.sort(key=lambda row: (len(row.child), row.child, len(row.left), row.left, row.right))
    if len(set(rows)) != len(rows):
        raise BoundError("duplicate concatenation relation row")
    return tuple(rows)


def compile_instance(instance: Instance) -> Compiled:
    instance.validate()
    train_order = _sorted_values(instance.train_substrings)
    effective_domains: dict[str, tuple[str, ...]] = {}
    for primitive in instance.primitives:
        effective_domains[primitive.primitive_id] = _sorted_values(
            {card.output for card in instance.cards_by_role[primitive.role]}
        )

    relations: dict[str, tuple[RelationRow, ...]] = {}
    child_domains: dict[str, tuple[str, ...]] = {}
    permitted_paid_ids: dict[str, frozenset[str]] = {}
    for merge in instance.merges:
        left_domain = frozenset(effective_domains[merge.left])
        right_domain = frozenset(effective_domains[merge.right])
        relation = _concat_relation(left_domain, right_domain, train_order)
        relations[merge.merged] = relation
        child_values = {row.child for row in relation}
        child_domains[merge.merged] = _sorted_values(child_values)
        permitted = {
            card.card_id
            for card in instance.paid_cards
            if not (
                instance.qok_paid_macro_forbidden
                and merge.merged == "qok"
                and card.role == "macro_core"
            )
        }
        permitted_paid_ids[merge.merged] = frozenset(permitted)
        effective_values = set(child_values)
        effective_values.update(
            card.output for card in instance.paid_cards if card.card_id in permitted
        )
        effective_domains[merge.merged] = _sorted_values(effective_values)

    all_values: set[str] = set()
    all_values.update(
        card.output
        for cards in instance.cards_by_role.values()
        for card in cards
    )
    all_values.update(card.output for card in instance.paid_cards)
    for domain in effective_domains.values():
        all_values.update(domain)
    for domain in child_domains.values():
        all_values.update(domain)
    values = _sorted_values(all_values)
    return Compiled(
        instance=instance,
        effective_domains=effective_domains,
        child_domains=child_domains,
        relations=relations,
        permitted_paid_ids=permitted_paid_ids,
        values=values,
        value_id={value: index for index, value in enumerate(values)},
    )


def build_encoding(compiled: Compiled) -> Encoding:
    instance = compiled.instance
    value_id = compiled.value_id
    assertions: list[z3.BoolRef] = []
    mapping_index: dict[str, z3.ArithRef] = {}
    effective: dict[str, z3.ArithRef] = {}
    child: dict[str, z3.ArithRef] = {}

    primitives_by_role: dict[str, list[Primitive]] = {}
    for primitive in instance.primitives:
        primitives_by_role.setdefault(primitive.role, []).append(primitive)
        variable = z3.Int(f"x__{primitive.primitive_id}")
        mapping_index[primitive.primitive_id] = variable
        eff = z3.Int(f"eff__{primitive.primitive_id}")
        effective[primitive.primitive_id] = eff
        cards = instance.cards_by_role[primitive.role]
        assertions.append(z3.And(variable >= 0, variable < len(cards)))
        assertions.append(
            z3.Or(
                *[
                    z3.And(variable == index, eff == value_id[card.output])
                    for index, card in enumerate(cards)
                ]
            )
        )
    for primitives in primitives_by_role.values():
        if len(primitives) > 1:
            assertions.append(
                z3.Distinct(*[mapping_index[row.primitive_id] for row in primitives])
            )

    paid_assignment: dict[tuple[int, str], z3.BoolRef] = {}
    for merge in instance.merges:
        for card in instance.paid_cards:
            variable = z3.Bool(f"z__{merge.rank:02d}__{card.card_id.replace(':', '_')}")
            paid_assignment[(merge.rank, card.card_id)] = variable
            if card.card_id not in compiled.permitted_paid_ids[merge.merged]:
                assertions.append(z3.Not(variable))
        assertions.append(
            z3.PbLe(
                [
                    (paid_assignment[(merge.rank, card.card_id)], 1)
                    for card in instance.paid_cards
                ],
                1,
            )
        )
    for card in instance.paid_cards:
        assertions.append(
            z3.PbEq(
                [
                    (paid_assignment[(merge.rank, card.card_id)], 1)
                    for merge in instance.merges
                ],
                1,
            )
        )

    relation_certificate: list[dict[str, object]] = []
    for merge in instance.merges:
        eff = z3.Int(f"eff__{merge.merged}")
        child_var = z3.Int(f"child__{merge.rank:02d}")
        effective[merge.merged] = eff
        child[merge.merged] = child_var
        relation = compiled.relations[merge.merged]
        if relation:
            assertions.append(
                z3.Or(
                    *[
                        z3.And(
                            effective[merge.left] == value_id[row.left],
                            effective[merge.right] == value_id[row.right],
                            child_var == value_id[row.child],
                        )
                        for row in relation
                    ]
                )
            )
        else:
            assertions.append(z3.BoolVal(False))

        train_effective_ids = [
            value_id[value]
            for value in compiled.effective_domains[merge.merged]
            if value and value in instance.train_substrings
        ]
        assertions.append(
            z3.Or(*[eff == candidate for candidate in train_effective_ids])
            if train_effective_ids
            else z3.BoolVal(False)
        )

        paid_variables = [
            paid_assignment[(merge.rank, card.card_id)] for card in instance.paid_cards
        ]
        assertions.append(z3.Implies(z3.Not(z3.Or(*paid_variables)), eff == child_var))
        for card in instance.paid_cards:
            selected = paid_assignment[(merge.rank, card.card_id)]
            assertions.append(z3.Implies(selected, eff == value_id[card.output]))
            assertions.append(z3.Implies(selected, child_var != value_id[card.output]))

        relation_rows = [[row.left, row.right, row.child] for row in relation]
        relation_certificate.append(
            {
                "rank": merge.rank,
                "merge": merge.merged,
                "allowed_child_rows": len(relation),
                "relation_sha256": sha256_json(relation_rows),
                "child_domain_size": len(compiled.child_domains[merge.merged]),
                "effective_domain_size": len(compiled.effective_domains[merge.merged]),
            }
        )

    structural_certificate: dict[str, object] = {
        "model": MODEL_NAME,
        "semantics": {
            "primitive_binding": "same-role bijection",
            "paid_assignment": "each paid card exactly once; at most one paid card per merge",
            "child": "left effective output concatenated with right effective output",
            "child_gate": "every merge child composition is an exact TRAIN substring",
            "effective_gate": "every merge effective output is a nonempty exact TRAIN substring",
            "default_effective": "child composition",
            "paid_effective": "assigned paid output, distinct from child composition",
            "static_macro_gate": "macro paid cards forbidden at exact merge qok",
            "deferred_macro_gates": [
                "LEFT_HOST",
                "RIGHT_HOST",
                "STANDALONE_OR_LEFT_HOST",
            ],
        },
        "value_count": len(compiled.values),
        "value_table_sha256": sha256_json(list(compiled.values)),
        "relation_rows_total": sum(len(rows) for rows in compiled.relations.values()),
        "relations": relation_certificate,
    }
    structural_certificate["certificate_sha256"] = sha256_json(structural_certificate)
    return Encoding(
        compiled=compiled,
        assertions=tuple(assertions),
        mapping_index=mapping_index,
        effective=effective,
        child=child,
        paid_assignment=paid_assignment,
        structural_certificate=structural_certificate,
    )


class ExactRunner:
    def __init__(self, assertions: Sequence[z3.BoolRef], time_limit_seconds: int):
        self.deadline = time.monotonic() + time_limit_seconds
        # QF_FD is excellent for the Boolean Stage-0 model, but this encoding
        # deliberately uses small bounded Int enums.  The general solver keeps
        # those equalities in a supported QF_LIA/PB fragment instead of handing
        # interpreted Int equality to the SAT-only backend.
        self.solver = z3.Solver()
        self.solver.add(*assertions)
        self.query_count = 0
        self.query_log: list[dict[str, object]] = []

    def check(
        self, phase: str, constraint: Mapping[str, object], extra: z3.BoolRef | None = None
    ) -> tuple[z3.CheckSatResult, z3.ModelRef | None]:
        remaining_ms = int((self.deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            raise SearchIncomplete("Stage-A exact-search time limit exhausted")
        self.query_count += 1
        self.solver.push()
        if extra is not None:
            self.solver.add(extra)
        self.solver.set(timeout=remaining_ms)
        status = self.solver.check()
        model = self.solver.model() if status == z3.sat else None
        reason = self.solver.reason_unknown() if status == z3.unknown else ""
        self.solver.pop()
        self.query_log.append(
            {
                "query": self.query_count,
                "phase": phase,
                "constraint": dict(constraint),
                "status": str(status),
                **({"reason_unknown": reason} if reason else {}),
            }
        )
        if status == z3.unknown:
            raise SearchIncomplete(f"Z3 returned unknown: {reason}")
        return status, model

    def commit(self, expression: z3.BoolRef) -> None:
        self.solver.add(expression)


def _model_int(model: z3.ModelRef, variable: z3.ArithRef) -> int:
    value = model.eval(variable, model_completion=True)
    if not z3.is_int_value(value):
        raise BoundError("model did not assign an integer")
    return value.as_long()


def _model_bool(model: z3.ModelRef, variable: z3.BoolRef) -> bool:
    return z3.is_true(model.eval(variable, model_completion=True))


def _extract_witness(encoding: Encoding, model: z3.ModelRef) -> dict[str, object]:
    compiled = encoding.compiled
    instance = compiled.instance
    values = compiled.values
    mapping_rows: list[dict[str, object]] = []
    mapping: dict[str, Card] = {}
    for primitive in instance.primitives:
        cards = instance.cards_by_role[primitive.role]
        index = _model_int(model, encoding.mapping_index[primitive.primitive_id])
        if not 0 <= index < len(cards):
            raise BoundError("model primitive-card index out of range")
        card = cards[index]
        mapping[primitive.primitive_id] = card
        mapping_rows.append(
            {
                "primitive_id": primitive.primitive_id,
                "role": primitive.role,
                "card_id": card.card_id,
                "output": card.output,
            }
        )

    paid_by_rank: dict[int, Card] = {}
    paid_rows: list[dict[str, object]] = []
    for merge in instance.merges:
        selected = [
            card
            for card in instance.paid_cards
            if _model_bool(model, encoding.paid_assignment[(merge.rank, card.card_id)])
        ]
        if len(selected) > 1:
            raise BoundError("model assigned multiple paid cards to one merge")
        if selected:
            paid_by_rank[merge.rank] = selected[0]
            paid_rows.append(
                {
                    "rank": merge.rank,
                    "merge": merge.merged,
                    "card_id": selected[0].card_id,
                    "role": selected[0].role,
                    "output": selected[0].output,
                    **(
                        {"side_license": selected[0].side_license}
                        if selected[0].side_license is not None
                        else {}
                    ),
                }
            )

    effective: dict[str, str] = {
        primitive.primitive_id: mapping[primitive.primitive_id].output
        for primitive in instance.primitives
    }
    merge_rows: list[dict[str, object]] = []
    for merge in instance.merges:
        child_value = effective[merge.left] + effective[merge.right]
        if child_value not in instance.train_substrings:
            raise BoundError(f"witness child composition misses TRAIN at {merge.merged}")
        paid = paid_by_rank.get(merge.rank)
        if paid is None:
            effective_value = child_value
            mode = "DEFAULT"
        else:
            if paid.output == child_value:
                raise BoundError(f"paid output equals child composition at {merge.merged}")
            if (
                instance.qok_paid_macro_forbidden
                and merge.merged == "qok"
                and paid.role == "macro_core"
            ):
                raise BoundError("qok received a forbidden paid macro")
            effective_value = paid.output
            mode = "PAID"
        effective[merge.merged] = effective_value
        solver_child = values[_model_int(model, encoding.child[merge.merged])]
        solver_eff = values[_model_int(model, encoding.effective[merge.merged])]
        if solver_child != child_value or solver_eff != effective_value:
            raise BoundError(f"Python replay differs from solver at {merge.merged}")
        merge_rows.append(
            {
                "rank": merge.rank,
                "merge": merge.merged,
                "left": merge.left,
                "right": merge.right,
                "child_composition": child_value,
                "child_is_train_substring": True,
                "mode": mode,
                "paid_card_id": paid.card_id if paid else None,
                "effective_output": effective_value,
            }
        )

    if len(paid_rows) != len(instance.paid_cards):
        raise BoundError("witness does not use exactly the complete paid deck")
    if {row["card_id"] for row in paid_rows} != {card.card_id for card in instance.paid_cards}:
        raise BoundError("witness paid assignment is not a card bijection")
    for role, cards in instance.cards_by_role.items():
        assigned = [mapping[p.primitive_id].card_id for p in instance.primitives if p.role == role]
        if set(assigned) != {card.card_id for card in cards}:
            raise BoundError(f"witness primitive mapping is not bijective in {role}")

    return {
        "mapping": mapping_rows,
        "paid_assignments": paid_rows,
        "paid_assignment_tuple": [
            [row["rank"], row["card_id"]]
            for row in paid_rows
        ],
        "merges": merge_rows,
    }


def canonicalize_paid_assignment_pairs(
    runner: ExactRunner,
    merges: Sequence[Merge],
    paid_cards: Sequence[Card],
    paid_assignment: Mapping[tuple[int, str], z3.BoolRef],
    exclusions: list[dict[str, object]],
) -> tuple[tuple[int, str], ...]:
    """Fix the lexicographically smallest sorted ``(rank, card_id)`` tuple.

    The coordinates are intentionally interleaved.  Thus
    ``((1, P01), (3, P02))`` precedes ``((1, P02), (2, P01))`` even though the
    latter has the smaller rank set.  Scanning the global pair order and
    excluding every skipped pair before committing the next selected pair is
    the exact greedy prefix construction for a fixed-cardinality sorted tuple.
    """

    ordered_pairs = [
        (merge.rank, card.card_id)
        for merge in merges
        for card in paid_cards
    ]
    following_index = 0
    chosen: list[tuple[int, str]] = []
    for position in range(len(paid_cards)):
        skipped: list[z3.BoolRef] = []
        chosen_index: int | None = None
        for index in range(following_index, len(ordered_pairs)):
            rank, card_id = ordered_pairs[index]
            selected = paid_assignment[(rank, card_id)]
            trial = z3.And(*[z3.Not(value) for value in skipped], selected)
            status, _ = runner.check(
                "canonical_paid_assignment_pair",
                {"position": position + 1, "rank": rank, "card_id": card_id},
                trial,
            )
            if status == z3.sat:
                for skipped_value in skipped:
                    runner.commit(z3.Not(skipped_value))
                runner.commit(selected)
                chosen.append((rank, card_id))
                chosen_index = index
                break
            exclusions.append(
                {
                    "coordinate": "paid_assignment_pair",
                    "position": position + 1,
                    "excluded_rank": rank,
                    "excluded_card_id": card_id,
                }
            )
            skipped.append(selected)
        if chosen_index is None:
            raise BoundError("canonical paid-pair prefix lost all feasible values")
        following_index = chosen_index + 1
    return tuple(chosen)


def solve_instance(
    instance: Instance,
    time_limit_seconds: int = 300,
    input_hashes: Mapping[str, str] | None = None,
) -> dict[str, object]:
    if not 1 <= time_limit_seconds <= MAX_SECONDS:
        raise BoundError(f"time limit must be in 1..{MAX_SECONDS}")
    compiled = compile_instance(instance)
    encoding = build_encoding(compiled)
    runner = ExactRunner(encoding.assertions, time_limit_seconds)
    existence, model = runner.check("existence", {})
    if existence == z3.unsat:
        return {
            "schema": SCHEMA,
            "decision": "NO_JOINT_CHILD_FEASIBLE_BINDING",
            "solver": {"name": "Z3", "version": z3.get_version_string()},
            "input_sha256": dict(input_hashes or {}),
            "counts": {
                "primitives": len(instance.primitives),
                "merges": len(instance.merges),
                "paid_cards": len(instance.paid_cards),
                "train_substrings": len(instance.train_substrings),
            },
            "structural_certificate": encoding.structural_certificate,
            "query_count": runner.query_count,
            "queries": runner.query_log,
            "scope": _scope_statement(),
        }
    assert model is not None

    exclusions: list[dict[str, object]] = []
    for primitive in instance.primitives:
        cards = instance.cards_by_role[primitive.role]
        variable = encoding.mapping_index[primitive.primitive_id]
        chosen: int | None = None
        for index, card in enumerate(cards):
            status, _ = runner.check(
                "canonical_primitive_mapping",
                {"primitive_id": primitive.primitive_id, "card_id": card.card_id},
                variable == index,
            )
            if status == z3.sat:
                chosen = index
                runner.commit(variable == index)
                break
            exclusions.append(
                {
                    "coordinate": "primitive_card",
                    "primitive_id": primitive.primitive_id,
                    "excluded_card_id": card.card_id,
                }
            )
        if chosen is None:
            raise BoundError("canonical primitive prefix lost all feasible values")

    canonicalize_paid_assignment_pairs(
        runner,
        instance.merges,
        instance.paid_cards,
        encoding.paid_assignment,
        exclusions,
    )

    final_status, final_model = runner.check("canonical_witness_replay", {})
    if final_status != z3.sat or final_model is None:
        raise BoundError("canonical witness replay is not SAT")
    witness = _extract_witness(encoding, final_model)
    return {
        "schema": SCHEMA,
        "decision": "JOINT_CHILD_NECESSARY_BOUND_SAT",
        "solver": {"name": "Z3", "version": z3.get_version_string()},
        "input_sha256": dict(input_hashes or {}),
        "counts": {
            "primitives": len(instance.primitives),
            "merges": len(instance.merges),
            "paid_cards": len(instance.paid_cards),
            "train_substrings": len(instance.train_substrings),
        },
        "canonical_tiebreak": [
            "lexicographically minimize primitive card-ID sequence in registered primitive order",
            "then lexicographically minimize the sorted interleaved (merge rank, paid card ID) assignment tuple",
        ],
        "canonical_prefix_exclusions": exclusions,
        "witness": witness,
        "structural_certificate": encoding.structural_certificate,
        "query_count": runner.query_count,
        "queries": runner.query_log,
        "scope": _scope_statement(),
    }


def _scope_statement() -> Mapping[str, object]:
    return {
        "kind": "permissive necessary relaxation",
        "included": [
            "complete same-role primitive/output bijection",
            "exactly eight distinct paid merge locations via a complete paid-card bijection",
            "recursive directed left-to-right effective outputs",
            "every one of 64 child compositions in TRAIN_SUBSTRINGS",
            "every one of 64 effective merge outputs nonempty and in TRAIN_SUBSTRINGS",
            "paid output differs from its child composition",
            "qok paid-macro prohibition",
        ],
        "deferred": [
            "host-side macro placement except the static qok prohibition",
            "full grammar and ordered multiplicity-preserving parses",
            "nonoverlapping 98-unit tilings and transition exposure",
            "frequency/exposure objectives and three-world construction",
        ],
        "sat_consequence": (
            "The full Stage-A-feasible space may enter a joint Stage-B search. "
            "The canonical witness does not freeze a mapping or paid assignment for W0."
        ),
        "unsat_consequence": (
            "The stricter inherited world is infeasible because every omitted condition "
            "can only remove assignments."
        ),
        "semantic_claim": "none",
    }


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-registered",
        action="store_true",
        help="required guard for the full registered scientific-input run",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=EXPERIMENT / "artifacts/work/primary_result.json",
    )
    parser.add_argument("--time-limit-seconds", type=int, default=MAX_SECONDS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    if not args.execute_registered:
        raise SystemExit(
            "refusing the full input run without --execute-registered; run toy tests instead"
        )
    instance, input_hashes = load_registered_instance()
    result = solve_instance(instance, args.time_limit_seconds, input_hashes)
    result["source_sha256"] = sha256_path(Path(__file__).resolve())
    output = args.output.resolve()
    atomic_write_json(output, result)
    print(json.dumps({"decision": result["decision"], "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
