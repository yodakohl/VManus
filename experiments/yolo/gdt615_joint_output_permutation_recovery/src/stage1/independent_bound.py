#!/usr/bin/env python3
"""Independent train-only GDT615 Stage-1 child-counterpart bound.

This program imports no project module and reads exactly six public/frozen
inputs: the Stage-0 mapping commit, REGISTERED_SEARCH, its train-substring
set, GDT608's merge tree, and GDT614's registered model and contract.  It does
not read Primary or other Stage-1 files, held/lm_confirm, target, f84, or f84r.

The proof is deliberately over-relaxed.  A paid node whose two direct children
are primitives has an immutable unoverridden child composition: no paid merge
below it can change that composition.  Such a node is forbidden when that
composition is absent from the registered train substrings.  Every other merge
node is generously admitted without checking roles, licenses, paid outputs, or
grammar.  UNSAT in this superset is therefore a necessary-bound certificate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "gdt615-stage1-independent-child-counterpart-bound-v1"
EXPECTED_MAPPING_COMMIT_SHA256 = (
    "edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262"
)
MERGE_COUNT = 64

REPO_ROOT = Path(__file__).resolve().parents[5]
EXPERIMENT = Path("experiments/yolo/gdt615_joint_output_permutation_recovery")
INPUT_RELATIVE_PATHS = {
    "mapping_commit": EXPERIMENT / "artifacts/stage0/STAGE0_MAPPING_COMMIT.json",
    "registered_search": EXPERIMENT / "artifacts/REGISTERED_SEARCH.json",
    "train_substrings": EXPERIMENT / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt",
    "merge_tree": Path(
        "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
    ),
    "gdt614_contract": Path(
        "experiments/yolo/gdt614_core_run_macro_recovery/PREREGISTRATION.md"
    ),
    "gdt614_model": Path(
        "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json"
    ),
}
DEFAULT_OUTPUT_RELATIVE_PATH = EXPERIMENT / "artifacts/stage1/INDEPENDENT_RESULT.json"


class BoundError(RuntimeError):
    """Input-contract or reconstruction failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundError(f"invalid JSON in {label}: {exc}") from exc


def load_tsv(data: bytes, label: str) -> list[dict[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundError(f"invalid UTF-8 in {label}") from exc
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    require(reader.fieldnames is not None, f"missing TSV header in {label}")
    rows = list(reader)
    require(all(None not in row for row in rows), f"ragged TSV row in {label}")
    return rows


@dataclass(frozen=True)
class Node:
    rank: int
    left: str
    right: str
    merged: str
    leaves: tuple[str, ...]
    depth: int
    raw_render: str
    subtree_ranks: tuple[int, ...]
    both_children_primitive: bool
    train_supported: bool

    @property
    def subtree_mask(self) -> int:
        mask = 0
        for rank in self.subtree_ranks:
            mask |= 1 << (rank - 1)
        return mask

    def public_dict(self) -> dict[str, Any]:
        return {
            "both_children_primitive": self.both_children_primitive,
            "depth": self.depth,
            "leaves": list(self.leaves),
            "left": self.left,
            "merge": self.merged,
            "rank": self.rank,
            "raw_unoverridden_child_render": self.raw_render,
            "right": self.right,
            "subtree_ranks": list(self.subtree_ranks),
            "train_substring_member": self.train_supported,
        }


@dataclass(frozen=True)
class CoverResult:
    feasible_within_limit: bool
    minimum: int | None
    lex_ranks: tuple[int, ...] | None
    combinations_tested: int
    relevant_candidate_ranks: tuple[int, ...]
    zero_candidate_demand_indexes: tuple[int, ...]

    def public_dict(self) -> dict[str, Any]:
        return {
            "combinations_tested": self.combinations_tested,
            "feasible_within_limit": self.feasible_within_limit,
            "lex_ranks": None if self.lex_ranks is None else list(self.lex_ranks),
            "minimum": self.minimum,
            "relevant_candidate_ranks": list(self.relevant_candidate_ranks),
            "zero_candidate_demand_indexes": list(self.zero_candidate_demand_indexes),
        }


def exhaustive_minimum_cover(
    demand_masks: Sequence[int], allowed_mask: int, maximum: int
) -> CoverResult:
    """Exhaust every relevant combination by cardinality, then rank lexicography."""
    effective = tuple(mask & allowed_mask for mask in demand_masks)
    zero = tuple(index for index, mask in enumerate(effective) if mask == 0)
    relevant_mask = 0
    for mask in effective:
        relevant_mask |= mask
    candidates = tuple(
        index + 1 for index in range(MERGE_COUNT) if relevant_mask & (1 << index)
    )
    if zero:
        return CoverResult(False, None, None, 0, candidates, zero)

    tested = 0
    for size in range(min(maximum, len(candidates)) + 1):
        for ranks in itertools.combinations(candidates, size):
            tested += 1
            selected = 0
            for rank in ranks:
                selected |= 1 << (rank - 1)
            if all(mask & selected for mask in effective):
                return CoverResult(True, size, ranks, tested, candidates, ())
    return CoverResult(False, None, None, tested, candidates, ())


def brute_minimum_cover(
    demand_masks: Sequence[int], allowed_mask: int, node_count: int
) -> tuple[int, tuple[int, ...]] | None:
    """Tiny truth-table oracle used only by --self-test."""
    best: tuple[int, tuple[int, ...]] | None = None
    for selected in range(1 << node_count):
        if selected & ~allowed_mask:
            continue
        if not all(mask & selected for mask in demand_masks):
            continue
        ranks = tuple(index + 1 for index in range(node_count) if selected & (1 << index))
        candidate = (len(ranks), ranks)
        if best is None or candidate < best:
            best = candidate
    return best


def run_self_test() -> None:
    cases = 0
    for node_count in range(1, 7):
        all_nodes = (1 << node_count) - 1
        nonempty = range(1, all_nodes + 1)
        allowed_cases = {
            all_nodes,
            sum(1 << index for index in range(node_count) if index % 2 == 0),
            (1 << max(1, node_count // 2)) - 1,
        }
        for first in nonempty:
            for second in range(first, all_nodes + 1):
                for allowed in allowed_cases:
                    demands = (first, second)
                    observed = exhaustive_minimum_cover(demands, allowed, node_count)
                    expected = brute_minimum_cover(demands, allowed, node_count)
                    if expected is None:
                        require(not observed.feasible_within_limit, "self-test false SAT")
                    else:
                        require(observed.feasible_within_limit, "self-test false UNSAT")
                        require(
                            (observed.minimum, observed.lex_ranks) == expected,
                            "self-test minimum/lex mismatch",
                        )
                    cases += 1

    singleton = exhaustive_minimum_cover((1 << 3,), ((1 << 6) - 1) & ~(1 << 3), 6)
    require(singleton.zero_candidate_demand_indexes == (0,), "singleton contradiction missed")
    print(f"STAGE1_INDEPENDENT_BOUND_SELF_TEST_PASS cases={cases}")


def registered_input_hash(search: Mapping[str, Any], suffix: str) -> str:
    matches = [
        row["sha256"]
        for row in search["registered_inputs"]
        if str(row["path"]).endswith(suffix)
    ]
    require(len(matches) == 1, f"registered hash not unique for {suffix}")
    return str(matches[0])


def reconstruct_mapping(
    search: Mapping[str, Any], commit: Mapping[str, Any], model: Mapping[str, Any]
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    roles = {
        str(row["primitive_id"]): str(row["role"])
        for row in search["primitive_role_assignment"]
    }
    require(len(roles) == 34, "registered primitive role assignment is not 34-way")

    deck: dict[str, dict[str, Any]] = {}
    for role, cards in search["primitive_output_deck"].items():
        for card in cards:
            card_id = str(card["card_id"])
            require(card_id not in deck, f"duplicate deck card {card_id}")
            deck[card_id] = {**card, "role": role}
    require(len(deck) == 34, "registered primitive output deck is not 34-way")

    mapping: dict[str, str] = {}
    seen_cards: set[str] = set()
    canonical_rows: list[dict[str, Any]] = []
    for row in commit["mapping"]:
        primitive = str(row["primitive_id"])
        card_id = str(row["card_id"])
        require(primitive in roles, f"unknown primitive in commit: {primitive}")
        require(primitive not in mapping, f"duplicate primitive in commit: {primitive}")
        require(card_id in deck, f"unknown card in commit: {card_id}")
        require(card_id not in seen_cards, f"duplicate card in commit: {card_id}")
        expected = deck[card_id]
        require(row["role"] == roles[primitive] == expected["role"], "role mismatch")
        require(row["output"] == expected["output"], f"output mismatch for {card_id}")
        require(int(row["length"]) == len(str(row["output"])), "derived length mismatch")
        require(
            row.get("side_license") == expected.get("side_license"),
            f"side-license mismatch for {card_id}",
        )
        mapping[primitive] = str(row["output"])
        seen_cards.add(card_id)
        canonical = {
            "card_id": card_id,
            "length": int(row["length"]),
            "output": str(row["output"]),
            "primitive_id": primitive,
            "role": str(row["role"]),
        }
        if row.get("side_license") is not None:
            canonical["side_license"] = row["side_license"]
        canonical_rows.append(canonical)

    require(set(mapping) == set(roles), "commit does not map every primitive")
    require(seen_cards == set(deck), "commit is not a complete card bijection")

    model_roles = {row["primitive_id"]: row["role"] for row in model["primitive_cards"]}
    require(model_roles == roles, "GDT614/GDT615 primitive roles disagree")
    require(model["paid_card_deck"] == search["paid_output_deck"], "paid decks disagree")
    return mapping, canonical_rows


def reconstruct_nodes(
    tree_rows: Sequence[Mapping[str, str]],
    primitive_outputs: Mapping[str, str],
    train_substrings: set[str],
) -> list[Node]:
    require(len(tree_rows) == MERGE_COUNT, "merge tree does not contain 64 rows")
    by_name: dict[str, Node] = {}
    nodes: list[Node] = []
    primitives = set(primitive_outputs)

    def child_data(symbol: str) -> tuple[tuple[str, ...], int, str, tuple[int, ...]]:
        if symbol in primitives:
            return (symbol,), 0, primitive_outputs[symbol], ()
        require(symbol in by_name, f"merge child is neither primitive nor earlier node: {symbol}")
        child = by_name[symbol]
        return child.leaves, child.depth, child.raw_render, child.subtree_ranks

    for expected_rank, row in enumerate(tree_rows, 1):
        rank = int(row["rank"])
        require(rank == expected_rank, "merge ranks are not exactly 1..64 in file order")
        left, right, merged = row["left"], row["right"], row["merged"]
        require(merged not in primitives and merged not in by_name, f"duplicate merge {merged}")
        left_leaves, left_depth, left_render, left_subtree = child_data(left)
        right_leaves, right_depth, right_render, right_subtree = child_data(right)
        leaves = left_leaves + right_leaves
        depth = max(left_depth, right_depth) + 1
        subtree = tuple(sorted(set(left_subtree) | set(right_subtree) | {rank}))
        raw_render = left_render + right_render
        require(tuple(row["leaf_sequence"].split()) == leaves, f"leaf trace mismatch at {rank}")
        require(int(row["leaf_count"]) == len(leaves), f"leaf count mismatch at {rank}")
        require(int(row["tree_depth"]) == depth, f"tree depth mismatch at {rank}")
        node = Node(
            rank=rank,
            left=left,
            right=right,
            merged=merged,
            leaves=leaves,
            depth=depth,
            raw_render=raw_render,
            subtree_ranks=subtree,
            both_children_primitive=left in primitives and right in primitives,
            train_supported=raw_render in train_substrings,
        )
        by_name[merged] = node
        nodes.append(node)
    return nodes


def canonical_unsupported(nodes: Iterable[Node]) -> list[dict[str, Any]]:
    return [
        {"merge": node.merged, "rank": node.rank, "raw_render": node.raw_render}
        for node in nodes
        if not node.train_supported
    ]


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run_bound() -> dict[str, Any]:
    # No discovery/glob is used: this is the complete semantic read allowlist.
    blobs = {
        label: (REPO_ROOT / relative).read_bytes()
        for label, relative in INPUT_RELATIVE_PATHS.items()
    }
    hashes = {label: sha256(data) for label, data in blobs.items()}
    require(hashes["mapping_commit"] == EXPECTED_MAPPING_COMMIT_SHA256, "wrong mapping commit")

    search = load_json(blobs["registered_search"], "REGISTERED_SEARCH.json")
    commit = load_json(blobs["mapping_commit"], "STAGE0_MAPPING_COMMIT.json")
    model = load_json(blobs["gdt614_model"], "GDT614 REGISTERED_MODEL.json")
    tree_rows = load_tsv(blobs["merge_tree"], "GDT608 merge_tree.tsv")

    require(search["schema"] == "gdt615-joint-output-binding-search-v1", "wrong search schema")
    require(commit["schema"] == "gdt615-stage0-mapping-commit-v1", "wrong commit schema")
    require(commit["stage1_status"] == "NOT_RUN", "mapping commit was not pre-Stage1")
    require(
        hashes["registered_search"] == commit["registered_input_sha256"]["REGISTERED_SEARCH.json"],
        "search hash disagrees with mapping commit",
    )
    require(
        hashes["train_substrings"]
        == search["registered_train_substrings"]["sha256"]
        == commit["registered_input_sha256"]["REGISTERED_TRAIN_SUBSTRINGS.txt"],
        "train substring hash disagreement",
    )
    require(
        hashes["merge_tree"]
        == registered_input_hash(search, "/merge_tree.tsv")
        == commit["registered_input_sha256"]["merge_tree.tsv"],
        "merge tree hash disagreement",
    )
    require(
        hashes["gdt614_contract"] == registered_input_hash(search, "/PREREGISTRATION.md"),
        "GDT614 contract hash disagreement",
    )
    require(
        hashes["gdt614_model"] == registered_input_hash(search, "/REGISTERED_MODEL.json"),
        "GDT614 model hash disagreement",
    )

    primitive_outputs, mapping_rows = reconstruct_mapping(search, commit, model)

    try:
        substring_lines = blobs["train_substrings"].decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise BoundError("train substrings are not ASCII") from exc
    require(len(substring_lines) == 28101, "unexpected train substring count")
    require(len(set(substring_lines)) == len(substring_lines), "duplicate train substrings")
    require(
        substring_lines == sorted(substring_lines, key=lambda value: (len(value.encode()), value.encode())),
        "train substring ordering contract failed",
    )
    require(all(value and value.isalpha() and value.islower() for value in substring_lines), "bad substring")
    train_substrings = set(substring_lines)

    nodes = reconstruct_nodes(tree_rows, primitive_outputs, train_substrings)
    supported_ranks = [node.rank for node in nodes if node.train_supported]
    unsupported = [node for node in nodes if not node.train_supported]
    require(len(supported_ranks) == 55 and len(unsupported) == 9, "recomputed support is not 55/9")
    require(supported_ranks == commit["raw_supported_merge_ranks"], "supported ranks differ from commit")
    require(canonical_unsupported(nodes) == commit["raw_unsupported_merges"], "unsupported rows differ")

    demands = tuple(node.subtree_mask for node in unsupported)
    all_nodes_mask = (1 << MERGE_COUNT) - 1
    budget = int(search["search"]["stage1_actual_paid_location_count"])
    require(budget == model["merge_constraints"]["paid_cards"] == 8, "paid budget is not eight")

    structural = exhaustive_minimum_cover(demands, all_nodes_mask, budget)
    require(structural.minimum == 4 and structural.lex_ranks == (2, 3, 14, 23), "Stage0 cover replay failed")

    structurally_forced: list[int] = []
    for rank in structural.relevant_candidate_ranks:
        without = all_nodes_mask & ~(1 << (rank - 1))
        if not exhaustive_minimum_cover(demands, without, budget).feasible_within_limit:
            structurally_forced.append(rank)

    immutable_excluded = [
        node for node in nodes if node.both_children_primitive and not node.train_supported
    ]
    immutable_excluded_mask = sum(1 << (node.rank - 1) for node in immutable_excluded)
    conservative_allowed = all_nodes_mask & ~immutable_excluded_mask
    counterpart_bound = exhaustive_minimum_cover(demands, conservative_allowed, budget)
    contradiction_ranks = sorted(set(structurally_forced) & {node.rank for node in immutable_excluded})

    require(structurally_forced == [14], "unexpected structurally forced node set")
    require([node.rank for node in immutable_excluded] == [14], "unexpected immutable exclusion set")
    require(contradiction_ranks == [14], "forced/excluded contradiction was not Ey")
    require(not counterpart_bound.feasible_within_limit, "over-relaxed counterpart bound unexpectedly SAT")
    require(counterpart_bound.zero_candidate_demand_indexes == (0,), "wrong empty demand")

    ey = nodes[13]
    require(ey.merged == "Ey" and ey.left == "E" and ey.right == "y", "rank 14 is not Ey")
    require(ey.raw_render == "hoi" and "hoi" not in train_substrings, "Ey counterpart premise failed")
    ey_demand = unsupported[counterpart_bound.zero_candidate_demand_indexes[0]]
    require(ey_demand.rank == 14 and ey_demand.subtree_ranks == (14,), "Ey is not singleton-forced")

    unsupported_rows = []
    for node in unsupported:
        structural_candidates = list(node.subtree_ranks)
        conservative_candidates = [
            rank for rank in node.subtree_ranks if conservative_allowed & (1 << (rank - 1))
        ]
        unsupported_rows.append(
            {
                "ancestor_merge": node.merged,
                "ancestor_rank": node.rank,
                "conservative_counterpart_eligible_hit_ranks": conservative_candidates,
                "raw_render": node.raw_render,
                "structural_hit_ranks": structural_candidates,
            }
        )

    result = {
        "checks": {
            "all_64_renderings_reconstructed": True,
            "commit_mapping_is_role_bijection": True,
            "forced_excluded_intersection_nonempty": True,
            "gdt614_contract_and_model_hashes_match_registration": True,
            "merge_tree_structure_reconstructed": True,
            "registered_input_hashes_match": True,
            "stage0_55_support_and_cover_replayed": True,
            "train_substrings_unique_and_canonically_sorted": True,
        },
        "decision": {
            "exact_eight_paid_set_exists": False,
            "reason": (
                "Ey/rank14 is forced by its singleton inclusive subtree but forbidden by its "
                "immutable primitive-child counterpart ho+i=hoi, absent from registered train substrings."
            ),
            "status": "STAGE1_TRAIN_CHILD_COUNTERPART_INFEASIBLE",
            "stronger_statement": (
                "The necessary over-relaxation is UNSAT even when every non-immutable node is "
                "granted counterpart eligibility and all card-role, output, license, grammar, and tiling "
                "constraints are omitted."
            ),
        },
        "input_sha256": {
            INPUT_RELATIVE_PATHS[label].as_posix(): digest for label, digest in hashes.items()
        },
        "mapping": mapping_rows,
        "proof": {
            "budget": budget,
            "contradiction_ranks": contradiction_ranks,
            "counterpart_over_relaxation": counterpart_bound.public_dict(),
            "forced_nodes_under_budget": [nodes[rank - 1].public_dict() for rank in structurally_forced],
            "immutable_counterpart_excluded_nodes": [node.public_dict() for node in immutable_excluded],
            "raw_counterpart_absent_nodes": [node.public_dict() for node in unsupported],
            "structural_cover_without_counterpart_gate": structural.public_dict(),
            "unsupported_ancestor_demands": unsupported_rows,
        },
        "reconstruction": {
            "merge_count": len(nodes),
            "raw_supported_count": len(supported_ranks),
            "raw_supported_ranks": supported_ranks,
            "raw_unsupported_count": len(unsupported),
            "renderings": [node.public_dict() for node in nodes],
        },
        "schema": SCHEMA,
        "scope": {
            "f84_or_f84r_opened": False,
            "held_or_lm_confirm_opened": False,
            "other_stage1_file_read_or_imported": False,
            "primary_file_read_or_imported": False,
            "semantic_read_allowlist": [path.as_posix() for path in INPUT_RELATIVE_PATHS.values()],
            "target_or_voynich_data_opened": False,
            "train_only": True,
        },
    }
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run only the tiny exhaustive oracle test")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_RELATIVE_PATH,
        help="repository-relative or absolute result path",
    )
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        result = run_bound()
        output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        write_json_atomic(output, result)
        print(
            "STAGE1_INDEPENDENT_BOUND_UNSAT "
            f"forced={result['proof']['contradiction_ranks']} "
            f"output={output}"
        )
        return 0
    except BoundError as exc:
        print(f"STAGE1_INDEPENDENT_BOUND_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
