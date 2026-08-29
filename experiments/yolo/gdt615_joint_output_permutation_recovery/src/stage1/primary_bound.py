#!/usr/bin/env python3
"""Primary train-only necessary child-counterpart bound for GDT615 Stage 1.

This is deliberately not a full Stage-1 world search.  It asks only whether
exactly eight paid merge locations can satisfy two necessary conditions:

* every raw-unsupported merge has a paid node in its inclusive merge subtree;
* every paid node's unoverridden child composition is a direct TRAIN span.

Scientific input paths are fixed.  No held, confirmation-LM, manuscript, or
target input can be supplied on the command line.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import z3


SCHEMA = "gdt615-stage1-primary-child-counterpart-bound-v1"
MAPPING_COMMIT_SHA256 = (
    "edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262"
)
EXPECTED_SHA256: Mapping[str, str] = {
    "STAGE0_MAPPING_COMMIT.json": MAPPING_COMMIT_SHA256,
    "REGISTERED_SEARCH.json": (
        "138cb3860a9927e8095534b293836271797a654e5e2797e12b0fadb0689e2089"
    ),
    "REGISTERED_TRAIN_SUBSTRINGS.txt": (
        "5b6859d8656f63cf8e8cf89221ae8ff1dea345e135a6cd012248b9b4c4ff14a9"
    ),
    "merge_tree.tsv": (
        "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a"
    ),
    "GDT614_PREREGISTRATION.md": (
        "552b3ee1cda663157c793ab30434aa67aef3ab534a94117bdb62e8d33b9600d1"
    ),
    "GDT614_REGISTERED_MODEL.json": (
        "ed841dc254a961650a8bda8bdc6024b67655f6bdc96e5dab2aec02f1686ecc42"
    ),
}


class BoundError(RuntimeError):
    """An input binding, formula, or certificate invariant failed."""


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise BoundError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
GDT615 = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
INPUT_PATHS: Mapping[str, Path] = {
    "STAGE0_MAPPING_COMMIT.json": (
        GDT615 / "artifacts/stage0/STAGE0_MAPPING_COMMIT.json"
    ),
    "REGISTERED_SEARCH.json": GDT615 / "artifacts/REGISTERED_SEARCH.json",
    "REGISTERED_TRAIN_SUBSTRINGS.txt": (
        GDT615 / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
    ),
    "merge_tree.tsv": (
        ROOT
        / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
    ),
    "GDT614_PREREGISTRATION.md": (
        ROOT / "experiments/yolo/gdt614_core_run_macro_recovery/PREREGISTRATION.md"
    ),
    "GDT614_REGISTERED_MODEL.json": (
        ROOT
        / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json"
    ),
}


@dataclass(frozen=True)
class MergeRow:
    rank: int
    left: str
    right: str
    merged: str
    leaves: tuple[str, ...]
    child_composition: str
    inclusive_subtree_ranks: tuple[int, ...]
    direct_train_span_possible: bool


@dataclass(frozen=True)
class LoadedInputs:
    hashes: Mapping[str, str]
    merges: tuple[MergeRow, ...]
    raw_unsupported_ranks: tuple[int, ...]
    relaxed_cover_ranks: tuple[int, ...]


@dataclass(frozen=True)
class BoundInstance:
    merge_names: tuple[str, ...]
    eligible_paid_ranks: frozenset[int]
    unsupported_subtrees: Mapping[int, tuple[int, ...]]
    paid_location_count: int

    def validate(self) -> None:
        merge_count = len(self.merge_names)
        if merge_count < 1 or len(set(self.merge_names)) != merge_count:
            raise BoundError("merge names must be nonempty and unique")
        all_ranks = set(range(1, merge_count + 1))
        if not self.eligible_paid_ranks <= all_ranks:
            raise BoundError("eligible paid rank is out of range")
        if not 0 <= self.paid_location_count <= merge_count:
            raise BoundError("paid-location cardinality is out of range")
        for unsupported_rank, subtree in self.unsupported_subtrees.items():
            if unsupported_rank not in all_ranks:
                raise BoundError("unsupported merge rank is out of range")
            if not subtree or unsupported_rank not in subtree:
                raise BoundError("inclusive subtree must contain its root")
            if tuple(sorted(set(subtree))) != tuple(subtree):
                raise BoundError("inclusive subtree ranks must be sorted and unique")
            if not set(subtree) <= all_ranks:
                raise BoundError("inclusive subtree contains an out-of-range rank")


@dataclass(frozen=True)
class NamedConstraint:
    label: str
    kind: str
    expression: z3.BoolRef
    detail: Mapping[str, object]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def read_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BoundError(f"cannot read valid {label} JSON") from exc
    if not isinstance(value, dict):
        raise BoundError(f"{label} must be a JSON object")
    return value


def require_dict(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise BoundError(f"{label} must be an object")
    return value


def require_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise BoundError(f"{label} must be an array")
    return value


def require_str(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise BoundError(f"{label} must be a string")
    return value


def require_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BoundError(f"{label} must be an integer")
    return value


def verify_hashes() -> dict[str, str]:
    observed: dict[str, str] = {}
    for label, path in INPUT_PATHS.items():
        if not path.is_file():
            raise BoundError(f"missing bound input: {label}")
        observed[label] = sha256_path(path)
    if observed != dict(EXPECTED_SHA256):
        wrong = sorted(
            label for label, digest in observed.items() if EXPECTED_SHA256[label] != digest
        )
        raise BoundError("bound input hash mismatch: " + ", ".join(wrong))
    return observed


def load_train_substrings(registered: Mapping[str, object]) -> frozenset[str]:
    metadata = require_dict(
        registered.get("registered_train_substrings"), "registered substring metadata"
    )
    if metadata.get("sha256") != EXPECTED_SHA256["REGISTERED_TRAIN_SUBSTRINGS.txt"]:
        raise BoundError("registered substring hash binding mismatch")
    try:
        payload = INPUT_PATHS["REGISTERED_TRAIN_SUBSTRINGS.txt"].read_bytes()
        text = payload.decode("ascii")
    except (OSError, UnicodeError) as exc:
        raise BoundError("cannot read the registered TRAIN substring table") from exc
    if not text.endswith("\n"):
        raise BoundError("registered TRAIN substring table lacks final newline")
    values = text.splitlines()
    if any(not value for value in values):
        raise BoundError("registered TRAIN substring table contains an empty row")
    if values != sorted(set(values), key=lambda value: (len(value), value)):
        raise BoundError("registered TRAIN substring table is not canonically sorted")
    if len(values) != metadata.get("distinct_substring_count"):
        raise BoundError("registered TRAIN substring row count mismatch")
    if min(map(len, values)) != metadata.get("minimum_length"):
        raise BoundError("registered TRAIN substring minimum-length mismatch")
    if max(map(len, values)) != metadata.get("maximum_length"):
        raise BoundError("registered TRAIN substring maximum-length mismatch")
    return frozenset(values)


def validate_registration(
    registered: Mapping[str, object], model: Mapping[str, object], preregistration: str
) -> None:
    if registered.get("schema") != "gdt615-joint-output-binding-search-v1":
        raise BoundError("unexpected GDT615 registration schema")
    search = require_dict(registered.get("search"), "registered search")
    if search.get("stage1_actual_paid_location_count") != 8:
        raise BoundError("Stage-1 paid-location count is not eight")
    if search.get("inclusive_recursive_merge_subtree") != (
        "the merge node itself plus every merge-node descendant reached through "
        "recursive left/right merge children; primitive leaves are not paid-node candidates"
    ):
        raise BoundError("inclusive merge-subtree semantics drifted")
    partition = require_dict(registered.get("partition_access"), "partition access")
    if partition.get("stage0_and_stage1_processes_have_readable_held_mount") is not False:
        raise BoundError("Stage-1 held mount is not sealed")
    if partition.get("stage0_through_stage2_processes_have_readable_lm_confirm_mount") is not False:
        raise BoundError("Stage-1 confirmation-LM mount is not sealed")

    registered_hashes = {
        require_str(row.get("path"), "registered input path"): require_str(
            row.get("sha256"), "registered input hash"
        )
        for raw_row in require_list(registered.get("registered_inputs"), "registered inputs")
        for row in [require_dict(raw_row, "registered input")]
    }
    required_suffix_hashes = {
        "merge_tree.tsv": EXPECTED_SHA256["merge_tree.tsv"],
        "gdt614_core_run_macro_recovery/PREREGISTRATION.md": EXPECTED_SHA256[
            "GDT614_PREREGISTRATION.md"
        ],
        "gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json": EXPECTED_SHA256[
            "GDT614_REGISTERED_MODEL.json"
        ],
    }
    for suffix, expected in required_suffix_hashes.items():
        matches = [digest for path, digest in registered_hashes.items() if path.endswith(suffix)]
        if matches != [expected]:
            raise BoundError(f"registered input binding mismatch for {suffix}")

    if model.get("schema") != "gdt614-registered-core-run-macro-v1":
        raise BoundError("unexpected GDT614 model schema")
    constraints = require_dict(model.get("merge_constraints"), "merge constraints")
    expected_constraints = {
        "directed_order": "left_then_right",
        "paid_cards": 8,
        "paid_short_cards": 4,
        "paid_macro_cards": 4,
        "qok_paid_macro_forbidden": True,
        "default_merge_equals_recursive_children": True,
        "paid_output_must_differ_from_recursive_children": True,
    }
    if constraints != expected_constraints:
        raise BoundError("GDT614 merge constraints drifted")
    model_paid = require_list(model.get("paid_card_deck"), "GDT614 paid deck")
    registered_paid = require_list(registered.get("paid_output_deck"), "GDT615 paid deck")
    if model_paid != registered_paid:
        raise BoundError("GDT615 paid deck differs from the bound GDT614 deck")
    roles = Counter(
        require_str(require_dict(row, "paid card").get("role"), "paid role")
        for row in model_paid
    )
    if roles != {"short_card": 4, "macro_core": 4}:
        raise BoundError("paid deck is not four short plus four macro cards")

    required_preregistration_text = (
        "Paid-child exposure must use the unoverridden child parse, not the paid atom.",
        "every paid card's unoverridden child composition present in both partitions;",
    )
    if any(fragment not in preregistration for fragment in required_preregistration_text):
        raise BoundError("GDT614 child-counterpart contract text drifted")


def validate_mapping_commit(
    commit: Mapping[str, object],
    registered: Mapping[str, object],
    hashes: Mapping[str, str],
) -> dict[str, str]:
    if commit.get("schema") != "gdt615-stage0-mapping-commit-v1":
        raise BoundError("unexpected mapping-commit schema")
    if commit.get("status") != "STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN":
        raise BoundError("mapping commit is not the frozen pre-Stage-1 certificate")
    if commit.get("stage1_status") != "NOT_RUN":
        raise BoundError("mapping commit is not blind to Stage 1")
    if commit.get("stage0_cover_is_actual_paid_location_selection") is not False:
        raise BoundError("relaxed Stage-0 cover was mislabelled as actual locations")
    for key in (
        "held_or_lm_confirm_opened",
        "voynich_target_opened",
        "f84_or_f84r_opened",
    ):
        if commit.get(key) is not False:
            raise BoundError(f"mapping commit privacy flag failed: {key}")
    expected_commit_inputs = {
        key: hashes[key]
        for key in (
            "REGISTERED_SEARCH.json",
            "REGISTERED_TRAIN_SUBSTRINGS.txt",
            "merge_tree.tsv",
        )
    }
    if commit.get("registered_input_sha256") != expected_commit_inputs:
        raise BoundError("mapping-commit Stage-0 input hashes drifted")

    primitives = require_list(
        registered.get("primitive_role_assignment"), "primitive-role assignment"
    )
    deck = require_dict(registered.get("primitive_output_deck"), "primitive deck")
    cards: dict[str, tuple[str, str]] = {}
    for role, raw_cards in deck.items():
        if not isinstance(role, str):
            raise BoundError("primitive deck role is not a string")
        for raw_card in require_list(raw_cards, f"primitive deck {role}"):
            card = require_dict(raw_card, "primitive card")
            card_id = require_str(card.get("card_id"), "primitive card ID")
            output = require_str(card.get("output"), "primitive card output")
            if card_id in cards:
                raise BoundError("duplicate primitive card ID")
            cards[card_id] = (role, output)

    mapping_rows = require_list(commit.get("mapping"), "mapping commit")
    if len(mapping_rows) != len(primitives) or len(mapping_rows) != 34:
        raise BoundError("mapping commit does not contain 34 primitives")
    mapping: dict[str, str] = {}
    seen_cards: set[str] = set()
    for position, (raw_mapping, raw_primitive) in enumerate(zip(mapping_rows, primitives)):
        row = require_dict(raw_mapping, f"mapping row {position}")
        primitive = require_dict(raw_primitive, f"primitive row {position}")
        primitive_id = require_str(row.get("primitive_id"), "mapped primitive ID")
        role = require_str(row.get("role"), "mapped primitive role")
        card_id = require_str(row.get("card_id"), "mapped card ID")
        output = require_str(row.get("output"), "mapped output")
        if primitive_id != primitive.get("primitive_id") or role != primitive.get("role"):
            raise BoundError("mapping commit order/role differs from registration")
        if cards.get(card_id) != (role, output):
            raise BoundError("mapping commit card tuple differs from registration")
        if row.get("length") != len(output):
            raise BoundError("mapping commit derived length mismatch")
        if primitive_id in mapping or card_id in seen_cards:
            raise BoundError("mapping commit is not a bijection")
        mapping[primitive_id] = output
        seen_cards.add(card_id)
    if len(seen_cards) != len(cards):
        raise BoundError("mapping commit omits registered cards")
    return mapping


def load_merges(mapping: Mapping[str, str], substrings: frozenset[str]) -> tuple[MergeRow, ...]:
    expected_header = [
        "rank",
        "left",
        "right",
        "merged",
        "train_occurrences",
        "leaf_sequence",
        "leaf_count",
        "tree_depth",
    ]
    try:
        with INPUT_PATHS["merge_tree.tsv"].open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != expected_header:
                raise BoundError("merge-tree header drifted")
            raw_rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise BoundError("cannot read the bound merge tree") from exc
    if len(raw_rows) != 64:
        raise BoundError("merge tree does not contain 64 merge nodes")

    renders = dict(mapping)
    leaves: dict[str, tuple[str, ...]] = {
        primitive_id: (primitive_id,) for primitive_id in mapping
    }
    subtrees: dict[str, tuple[int, ...]] = {primitive_id: () for primitive_id in mapping}
    rows: list[MergeRow] = []
    for expected_rank, raw in enumerate(raw_rows, 1):
        try:
            rank = int(raw["rank"])
            leaf_count = int(raw["leaf_count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise BoundError("malformed merge-tree integer") from exc
        left, right, merged = raw["left"], raw["right"], raw["merged"]
        if rank != expected_rank or left not in renders or right not in renders:
            raise BoundError("merge tree is not directed topological rank order")
        if merged in renders:
            raise BoundError("merge-tree node name is not unique")
        merged_leaves = leaves[left] + leaves[right]
        if raw["leaf_sequence"].split() != list(merged_leaves):
            raise BoundError("merge-tree leaf sequence drifted")
        if leaf_count != len(merged_leaves):
            raise BoundError("merge-tree leaf count drifted")
        child_composition = renders[left] + renders[right]
        subtree = tuple(sorted({rank, *subtrees[left], *subtrees[right]}))
        renders[merged] = child_composition
        leaves[merged] = merged_leaves
        subtrees[merged] = subtree
        rows.append(
            MergeRow(
                rank=rank,
                left=left,
                right=right,
                merged=merged,
                leaves=merged_leaves,
                child_composition=child_composition,
                inclusive_subtree_ranks=subtree,
                direct_train_span_possible=child_composition in substrings,
            )
        )
    return tuple(rows)


def load_inputs() -> LoadedInputs:
    hashes = verify_hashes()
    registered = read_json(INPUT_PATHS["REGISTERED_SEARCH.json"], "GDT615 registration")
    model = read_json(
        INPUT_PATHS["GDT614_REGISTERED_MODEL.json"], "GDT614 registered model"
    )
    try:
        preregistration = INPUT_PATHS["GDT614_PREREGISTRATION.md"].read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        raise BoundError("cannot read the bound GDT614 preregistration") from exc
    validate_registration(registered, model, preregistration)
    substrings = load_train_substrings(registered)
    commit = read_json(INPUT_PATHS["STAGE0_MAPPING_COMMIT.json"], "mapping commit")
    mapping = validate_mapping_commit(commit, registered, hashes)
    merges = load_merges(mapping, substrings)

    unsupported = tuple(row.rank for row in merges if not row.direct_train_span_possible)
    committed_unsupported = [
        {
            "merge": row.merged,
            "rank": row.rank,
            "raw_render": row.child_composition,
        }
        for row in merges
        if not row.direct_train_span_possible
    ]
    if commit.get("raw_unsupported_merges") != committed_unsupported:
        raise BoundError("recomputed raw-unsupported merges differ from mapping commit")
    objective = require_dict(commit.get("objective"), "mapping-commit objective")
    if objective.get("raw_train_supported_named_merges") != len(merges) - len(unsupported):
        raise BoundError("recomputed support count differs from mapping commit")

    relaxed_rows = require_list(
        commit.get("canonical_relaxed_minimum_cover"), "relaxed Stage-0 cover"
    )
    relaxed_ranks = tuple(
        require_int(require_dict(row, "relaxed cover row").get("rank"), "cover rank")
        for row in relaxed_rows
    )
    for unsupported_rank in unsupported:
        subtree = set(merges[unsupported_rank - 1].inclusive_subtree_ranks)
        if not subtree.intersection(relaxed_ranks):
            raise BoundError("committed relaxed cover does not cover an unsupported merge")
    if objective.get("exact_minimum_core_hit") != len(relaxed_ranks):
        raise BoundError("relaxed cover size differs from mapping-commit objective")

    return LoadedInputs(
        hashes=hashes,
        merges=merges,
        raw_unsupported_ranks=unsupported,
        relaxed_cover_ranks=relaxed_ranks,
    )


def make_instance(inputs: LoadedInputs) -> BoundInstance:
    return BoundInstance(
        merge_names=tuple(row.merged for row in inputs.merges),
        eligible_paid_ranks=frozenset(
            row.rank for row in inputs.merges if row.direct_train_span_possible
        ),
        unsupported_subtrees={
            row.rank: row.inclusive_subtree_ranks
            for row in inputs.merges
            if not row.direct_train_span_possible
        },
        paid_location_count=8,
    )


def build_formula(
    instance: BoundInstance,
) -> tuple[dict[int, z3.BoolRef], tuple[NamedConstraint, ...]]:
    instance.validate()
    variables = {
        rank: z3.Bool(f"paid_merge_{rank:02d}")
        for rank in range(1, len(instance.merge_names) + 1)
    }
    constraints: list[NamedConstraint] = [
        NamedConstraint(
            label=f"C000_exactly_{instance.paid_location_count}_paid_locations",
            kind="exact_paid_location_cardinality",
            expression=z3.PbEq(
                [(variables[rank], 1) for rank in sorted(variables)],
                instance.paid_location_count,
            ),
            detail={"exactly": instance.paid_location_count},
        )
    ]
    for rank, merge in enumerate(instance.merge_names, 1):
        eligible = rank in instance.eligible_paid_ranks
        constraints.append(
            NamedConstraint(
                label=f"E{rank:02d}_paid_requires_train_child_span",
                kind="paid_child_counterpart_direct_train_span",
                expression=z3.Implies(variables[rank], z3.BoolVal(eligible)),
                detail={"rank": rank, "merge": merge, "eligible": eligible},
            )
        )
    for unsupported_rank in sorted(instance.unsupported_subtrees):
        subtree = instance.unsupported_subtrees[unsupported_rank]
        constraints.append(
            NamedConstraint(
                label=(
                    f"U{unsupported_rank:02d}_raw_unsupported_requires_paid_subtree"
                ),
                kind="raw_unsupported_merge_coverage",
                expression=z3.Or(*(variables[rank] for rank in subtree)),
                detail={
                    "unsupported_rank": unsupported_rank,
                    "unsupported_merge": instance.merge_names[unsupported_rank - 1],
                    "inclusive_subtree_ranks": list(subtree),
                },
            )
        )
    if len({constraint.label for constraint in constraints}) != len(constraints):
        raise BoundError("duplicate formula constraint label")
    return variables, tuple(constraints)


def selected_ranks(
    model: z3.ModelRef | None, variables: Mapping[int, z3.BoolRef]
) -> list[int] | None:
    if model is None:
        return None
    return [
        rank
        for rank, variable in sorted(variables.items())
        if z3.is_true(model.eval(variable, model_completion=True))
    ]


def solve_bound(instance: BoundInstance) -> dict[str, object]:
    variables, constraints = build_formula(instance)
    by_label = {constraint.label: constraint for constraint in constraints}
    constraint_order = {constraint.label: index for index, constraint in enumerate(constraints)}
    queries: list[dict[str, object]] = []

    def check(
        phase: str,
        active_labels: Sequence[str],
        *,
        tracked: bool = False,
    ) -> tuple[z3.CheckSatResult, z3.ModelRef | None, tuple[str, ...]]:
        solver = z3.Solver()
        for label in active_labels:
            constraint = by_label[label]
            if tracked:
                solver.assert_and_track(constraint.expression, z3.Bool(label))
            else:
                solver.add(constraint.expression)
        status = solver.check()
        model = solver.model() if status == z3.sat else None
        core: tuple[str, ...] = ()
        if status == z3.unsat and tracked:
            raw_names = {str(symbol) for symbol in solver.unsat_core()}
            core = tuple(
                sorted(raw_names, key=lambda label: constraint_order[label])
            )
        record: dict[str, object] = {
            "query_id": f"Q{len(queries) + 1:04d}",
            "phase": phase,
            "result": str(status).upper(),
            "active_constraint_count": len(active_labels),
            "active_constraint_labels_sha256": sha256_json(list(active_labels)),
        }
        if len(active_labels) <= 12:
            record["active_constraint_labels"] = list(active_labels)
        witness = selected_ranks(model, variables)
        if witness is not None:
            record["paid_true_ranks"] = witness
        if core:
            record["unsat_core_labels"] = list(core)
        queries.append(record)
        return status, model, core

    all_labels = tuple(constraint.label for constraint in constraints)
    status, model, raw_core = check("full_formula", all_labels, tracked=True)
    if status == z3.unknown:
        raise BoundError("Z3 returned unknown for the finite necessary bound")
    if status == z3.sat:
        witness = selected_ranks(model, variables)
        if witness is None or len(witness) != instance.paid_location_count:
            raise BoundError("SAT witness violates paid-location cardinality")
        return {
            "status": "SAT",
            "witness_paid_ranks": witness,
            "raw_unsat_core_labels": [],
            "minimal_unsat_core_labels": [],
            "core_constraints": [],
            "core_subset_minimal": None,
            "queries": queries,
            "named_constraints": [
                {
                    "label": constraint.label,
                    "kind": constraint.kind,
                    **constraint.detail,
                }
                for constraint in constraints
            ],
        }
    if not raw_core:
        raise BoundError("UNSAT result did not expose a tracked core")

    minimal_core = list(raw_core)
    for label in tuple(raw_core):
        if label not in minimal_core:
            continue
        trial = tuple(candidate for candidate in minimal_core if candidate != label)
        trial_status, _, _ = check(f"core_minimize_drop_{label}", trial)
        if trial_status == z3.unknown:
            raise BoundError("Z3 returned unknown during core minimization")
        if trial_status == z3.unsat:
            minimal_core.remove(label)

    core_status, _, _ = check("minimal_core_replay", tuple(minimal_core))
    if core_status != z3.unsat:
        raise BoundError("minimized core does not replay as UNSAT")
    minimality_replays: list[dict[str, object]] = []
    for label in minimal_core:
        trial = tuple(candidate for candidate in minimal_core if candidate != label)
        trial_status, trial_model, _ = check(
            f"minimal_core_necessity_drop_{label}", trial
        )
        if trial_status != z3.sat:
            raise BoundError("reported core is not subset-minimal")
        minimality_replays.append(
            {
                "removed_label": label,
                "result": "SAT",
                "paid_true_ranks": selected_ranks(trial_model, variables),
            }
        )

    return {
        "status": "UNSAT",
        "witness_paid_ranks": None,
        "raw_unsat_core_labels": list(raw_core),
        "minimal_unsat_core_labels": minimal_core,
        "core_constraints": [
            {
                "label": by_label[label].label,
                "kind": by_label[label].kind,
                **by_label[label].detail,
            }
            for label in minimal_core
        ],
        "core_subset_minimal": True,
        "core_minimality_replays": minimality_replays,
        "queries": queries,
        "named_constraints": [
            {
                "label": constraint.label,
                "kind": constraint.kind,
                **constraint.detail,
            }
            for constraint in constraints
        ],
    }


def build_result(inputs: LoadedInputs, solved: Mapping[str, object]) -> dict[str, object]:
    status = require_str(solved.get("status"), "solver status")
    decision = (
        "NECESSARY_CHILD_COUNTERPART_BOUND_UNSAT"
        if status == "UNSAT"
        else "NECESSARY_CHILD_COUNTERPART_BOUND_SAT"
    )
    eligible = [
        row.rank for row in inputs.merges if row.direct_train_span_possible
    ]
    unsupported = [
        {
            "rank": row.rank,
            "merge": row.merged,
            "child_composition": row.child_composition,
            "inclusive_subtree_ranks": list(row.inclusive_subtree_ranks),
        }
        for row in inputs.merges
        if not row.direct_train_span_possible
    ]
    return {
        "schema": SCHEMA,
        "status": status,
        "decision": decision,
        "claim_scope": (
            "Train-only necessary paid-location bound under the frozen mapping; "
            "not a paid-card assignment, grammar parse, tiling, world construction, "
            "objective optimization, or held evaluation."
        ),
        "mapping_commit_sha256": MAPPING_COMMIT_SHA256,
        "input_sha256": dict(inputs.hashes),
        "partition_access": {
            "train_substring_table_opened": True,
            "held_opened": False,
            "confirmation_lm_opened": False,
            "voynich_target_opened": False,
            "sealed_folio_data_opened": False,
        },
        "bound": {
            "merge_boolean_variable_count": len(inputs.merges),
            "paid_merge_location_count_exact": 8,
            "eligible_paid_location_count": len(eligible),
            "eligible_paid_ranks": eligible,
            "raw_unsupported_merge_count": len(unsupported),
            "raw_unsupported_merges": unsupported,
            "formula": {
                "cardinality": "sum_r paid[r] = 8",
                "child_counterpart": (
                    "paid[r] -> unoverridden_child_composition[r] is a direct "
                    "REGISTERED_TRAIN_SUBSTRINGS span"
                ),
                "coverage": (
                    "for each raw-unsupported u: OR paid[r] for r in the "
                    "inclusive recursive merge-subtree of u"
                ),
            },
            "stage0_relaxed_cover_ranks": list(inputs.relaxed_cover_ranks),
            "stage0_relaxed_cover_eligible_under_child_counterpart_gate": [
                rank for rank in inputs.relaxed_cover_ranks if rank in eligible
            ],
        },
        "merge_child_counterpart_table": [
            {
                "rank": row.rank,
                "merge": row.merged,
                "left": row.left,
                "right": row.right,
                "child_composition": row.child_composition,
                "direct_train_span_possible": row.direct_train_span_possible,
                "inclusive_subtree_ranks": list(row.inclusive_subtree_ranks),
            }
            for row in inputs.merges
        ],
        "solver": {
            "backend": "z3 Boolean SAT plus pseudo-Boolean exact cardinality",
            "z3_version": z3.get_version_string(),
            "result": status,
        },
        "query_core_certificate": {
            "named_constraints": solved["named_constraints"],
            "queries": solved["queries"],
            "raw_unsat_core_labels": solved["raw_unsat_core_labels"],
            "minimal_unsat_core_labels": solved["minimal_unsat_core_labels"],
            "core_constraints": solved["core_constraints"],
            "core_subset_minimal": solved["core_subset_minimal"],
            "core_minimality_replays": solved.get("core_minimality_replays", []),
        },
        "witness_paid_ranks": solved["witness_paid_ranks"],
        "interpretation": {
            "necessary_bound_only": True,
            "full_stage1_search_performed": False,
            "full_stage1_train_world_certified": False,
            "held_or_lm_conclusion": False,
        },
    }


def write_new_result(path: Path, result: Mapping[str, object]) -> None:
    resolved = path.expanduser().resolve()
    if any("f84" in component.casefold() for component in resolved.parts):
        raise BoundError("output path contains a forbidden sealed-data token")
    if os.path.lexists(resolved):
        raise BoundError("refusing to overwrite an existing result")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(result)
    with resolved.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    try:
        inputs = load_inputs()
        instance = make_instance(inputs)
        solved = solve_bound(instance)
        result = build_result(inputs, solved)
        write_new_result(args.output, result)
    except BoundError as exc:
        print(f"STAGE1_PRIMARY_BOUND_FAILURE: {exc}", file=sys.stderr, flush=True)
        return 1
    print(
        f"{result['decision']} raw_unsupported={len(inputs.raw_unsupported_ranks)} "
        f"eligible_paid={len(instance.eligible_paid_ranks)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
