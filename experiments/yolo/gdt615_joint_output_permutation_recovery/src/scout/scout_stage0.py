#!/usr/bin/env python3
"""Seeded constructive heuristic for GDT615's relaxed Stage-0 bound.

This is explicitly not the registered primary search and cannot establish a
pass, an optimum, or infeasibility.  It emits concrete candidates for later
registered solvers to examine without consuming any held material.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import random
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from scout_core import (
    CLAIM,
    ROOT,
    WORK_ROOT,
    Evaluation,
    Problem,
    canonical_json,
    load_problem,
    require_work_path,
    write_tsv,
)


@dataclass(frozen=True, slots=True)
class SearchConfig:
    seed: int
    restarts: int
    iterations: int
    workers: int
    repair_probability: float
    repair_assignment_cap: int
    polish_rounds: int
    top_candidates: int


@dataclass(frozen=True, slots=True)
class RestartResult:
    restart_index: int
    seed: int
    trajectory_mode: str
    mapping: tuple[str, ...]
    support_count: int
    cover_minimum: int
    evaluations: int
    accepted_moves: int
    repair_moves: int


def quality(evaluation: Evaluation) -> tuple[int, int, int]:
    if evaluation.cover_minimum <= 8:
        return (1, evaluation.support_count, -evaluation.cover_minimum)
    return (0, -evaluation.cover_minimum, evaluation.support_count)


def energy(evaluation: Evaluation) -> int:
    if evaluation.cover_minimum <= 8:
        return 100_000 + 100 * evaluation.support_count - evaluation.cover_minimum
    return -128 * evaluation.cover_minimum + evaluation.support_count


def trajectory_energy(evaluation: Evaluation, mode: str) -> int:
    if mode == "gate_first":
        return energy(evaluation)
    if mode == "support_first":
        return 128 * evaluation.support_count - evaluation.cover_minimum
    if mode == "balanced":
        return (
            24 * evaluation.support_count
            - 96 * max(0, evaluation.cover_minimum - 8)
            - evaluation.cover_minimum
        )
    raise ValueError(f"unknown trajectory mode {mode}")


class ConstructiveSearch:
    def __init__(self, problem: Problem, assignment_cap: int) -> None:
        self.problem = problem
        self.assignment_cap = assignment_cap
        self.assignments: dict[int, tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]] = {}
        self.substrings_by_length: dict[int, tuple[str, ...]] = {}
        for value in problem.substrings:
            self.substrings_by_length.setdefault(len(value), []).append(value)
        self.substrings_by_length = {
            length: tuple(values)
            for length, values in self.substrings_by_length.items()
        }
        self.variable_roles = tuple(
            role
            for role, positions in problem.role_positions.items()
            if len(positions) > 1
        )
        role_leaf_mass = {
            role: sum(
                sum(
                    self.problem.primitives[
                        self.problem.primitive_index[leaf]
                    ].role
                    == role
                    for leaf in merge.leaves
                )
                for merge in self.problem.merges
            )
            for role in self.variable_roles
        }
        self.role_population = tuple(
            role
            for role in self.variable_roles
            for _ in range(max(1, role_leaf_mass[role]))
        )

    def random_mapping(self, rng: random.Random) -> tuple[str, ...]:
        mapping = list(self.problem.identity_mapping())
        for role, positions in self.problem.role_positions.items():
            cards = [card.card_id for card in self.problem.cards_by_role[role]]
            rng.shuffle(cards)
            for position, card_id in zip(positions, cards, strict=True):
                mapping[position] = card_id
        return tuple(mapping)

    def random_swap(
        self, mapping: Sequence[str], rng: random.Random
    ) -> tuple[str, ...]:
        role = rng.choice(self.role_population)
        first, second = rng.sample(self.problem.role_positions[role], 2)
        result = list(mapping)
        result[first], result[second] = result[second], result[first]
        return tuple(result)

    def _local_assignments(
        self, merge_index: int
    ) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        cached = self.assignments.get(merge_index)
        if cached is not None:
            return cached
        merge = self.problem.merges[merge_index]
        local_primitives = tuple(dict.fromkeys(merge.leaves))
        primitive_role = {
            primitive.primitive_id: primitive.role
            for primitive in self.problem.primitives
        }
        card_options = {
            role: self.problem.cards_by_role[role]
            for role in {primitive_role[leaf] for leaf in merge.leaves}
        }
        minimum_length = sum(
            min(len(card.output) for card in card_options[primitive_role[leaf]])
            for leaf in merge.leaves
        )
        maximum_length = sum(
            max(len(card.output) for card in card_options[primitive_role[leaf]])
            for leaf in merge.leaves
        )
        reservoir: list[tuple[str, ...]] = []
        seen = 0
        rng = random.Random(0x61500000 + merge.rank)

        for length in range(max(1, minimum_length), min(12, maximum_length) + 1):
            for text in self.substrings_by_length.get(length, ()):
                assigned: dict[str, str] = {}
                used: dict[str, set[str]] = {
                    role: set() for role in card_options
                }

                def visit(leaf_index: int, position: int) -> None:
                    nonlocal seen
                    if leaf_index == len(merge.leaves):
                        if position != len(text):
                            return
                        row = tuple(assigned[item] for item in local_primitives)
                        seen += 1
                        if len(reservoir) < self.assignment_cap:
                            reservoir.append(row)
                        else:
                            replacement = rng.randrange(seen)
                            if replacement < self.assignment_cap:
                                reservoir[replacement] = row
                        return
                    primitive_id = merge.leaves[leaf_index]
                    role = primitive_role[primitive_id]
                    fixed = assigned.get(primitive_id)
                    if fixed is not None:
                        card = self.problem.card_by_id[fixed]
                        if text.startswith(card.output, position):
                            visit(leaf_index + 1, position + len(card.output))
                        return
                    for card in card_options[role]:
                        if card.card_id in used[role]:
                            continue
                        if not text.startswith(card.output, position):
                            continue
                        assigned[primitive_id] = card.card_id
                        used[role].add(card.card_id)
                        visit(leaf_index + 1, position + len(card.output))
                        used[role].remove(card.card_id)
                        del assigned[primitive_id]

                visit(0, 0)

        # A tuple determines one render, so duplicate tuples can only arise via
        # duplicate input strings, which the registered table forbids.
        ordered = tuple(sorted(set(reservoir)))
        result = (local_primitives, ordered)
        self.assignments[merge_index] = result
        return result

    def repair_move(
        self,
        mapping: Sequence[str],
        evaluation: Evaluation,
        rng: random.Random,
    ) -> tuple[str, ...] | None:
        bad = [
            index
            for index in range(len(self.problem.merges))
            if not (evaluation.supported_mask & (1 << index))
        ]
        if not bad:
            return None
        weights = [
            max(1, 8 - self.problem.descendant_masks[index].bit_count()) ** 2
            for index in bad
        ]
        # Coordinated two/three-merge repairs cross local maxima that a single
        # exact repair followed by swaps cannot.  Compatibility is still a
        # partial role-wise bijection, never a relaxed mapping.
        target_count = min(len(bad), rng.choice((1, 2, 2, 3)))
        for _attempt in range(32):
            remaining_bad = list(bad)
            remaining_weights = list(weights)
            targets = []
            for _ in range(target_count):
                chosen = rng.choices(
                    range(len(remaining_bad)), weights=remaining_weights, k=1
                )[0]
                targets.append(remaining_bad.pop(chosen))
                remaining_weights.pop(chosen)

            desired: dict[str, str] = {}
            card_owner: dict[tuple[str, str], str] = {}
            compatible = True
            for merge_index in targets:
                local_primitives, rows = self._local_assignments(merge_index)
                if not rows:
                    compatible = False
                    break
                row = rng.choice(rows)
                for primitive_id, card_id in zip(
                    local_primitives, row, strict=True
                ):
                    previous = desired.get(primitive_id)
                    if previous is not None and previous != card_id:
                        compatible = False
                        break
                    role = self.problem.primitives[
                        self.problem.primitive_index[primitive_id]
                    ].role
                    owner_key = (role, card_id)
                    owner = card_owner.get(owner_key)
                    if owner is not None and owner != primitive_id:
                        compatible = False
                        break
                    desired[primitive_id] = card_id
                    card_owner[owner_key] = primitive_id
                if not compatible:
                    break
            if not compatible:
                continue

            result = list(mapping)
            for primitive_id, card_id in desired.items():
                position = self.problem.primitive_index[primitive_id]
                if result[position] == card_id:
                    continue
                role = self.problem.primitives[position].role
                holder = next(
                    candidate
                    for candidate in self.problem.role_positions[role]
                    if result[candidate] == card_id
                )
                result[position], result[holder] = result[holder], result[position]
            repaired = tuple(result)
            raw = self.problem.raw_renders(repaired)
            if all(raw[index] in self.problem.substring_set for index in targets):
                return repaired
        return None

    def polish(
        self,
        mapping: tuple[str, ...],
        rounds: int,
    ) -> tuple[tuple[str, ...], Evaluation, int]:
        current = mapping
        current_eval = self.problem.evaluate(current)
        evaluations = 1
        for _round in range(rounds):
            best_mapping = current
            best_eval = current_eval
            for role in self.variable_roles:
                positions = self.problem.role_positions[role]
                for first_offset, first in enumerate(positions):
                    for second in positions[first_offset + 1 :]:
                        proposal = list(current)
                        proposal[first], proposal[second] = (
                            proposal[second],
                            proposal[first],
                        )
                        proposal_eval = self.problem.evaluate(tuple(proposal))
                        evaluations += 1
                        if quality(proposal_eval) > quality(best_eval):
                            best_mapping = tuple(proposal)
                            best_eval = proposal_eval
                # Two orientations of every 3-cycle provide a deterministic
                # larger neighborhood without enumerating general permutations.
                for first_offset, first in enumerate(positions):
                    for second_offset in range(first_offset + 1, len(positions)):
                        second = positions[second_offset]
                        for third in positions[second_offset + 1 :]:
                            for reverse in (False, True):
                                proposal = list(current)
                                first_value = proposal[first]
                                second_value = proposal[second]
                                third_value = proposal[third]
                                if reverse:
                                    proposal[first], proposal[second], proposal[third] = (
                                        third_value,
                                        first_value,
                                        second_value,
                                    )
                                else:
                                    proposal[first], proposal[second], proposal[third] = (
                                        second_value,
                                        third_value,
                                        first_value,
                                    )
                                proposal_eval = self.problem.evaluate(tuple(proposal))
                                evaluations += 1
                                if quality(proposal_eval) > quality(best_eval):
                                    best_mapping = tuple(proposal)
                                    best_eval = proposal_eval
            if quality(best_eval) <= quality(current_eval):
                break
            current = best_mapping
            current_eval = best_eval
        return current, current_eval, evaluations

    def run_restart(
        self,
        *,
        restart_index: int,
        seed: int,
        iterations: int,
        repair_probability: float,
        polish_rounds: int,
    ) -> RestartResult:
        rng = random.Random(seed)
        trajectory_mode = ("gate_first", "support_first", "balanced")[
            restart_index % 3
        ]
        current = (
            self.problem.identity_mapping()
            if restart_index == 0
            else self.random_mapping(rng)
        )
        current_eval = self.problem.evaluate(current)
        best = current
        best_eval = current_eval
        evaluations = 1
        accepted = 0
        repairs = 0

        for step in range(iterations):
            progress = step / max(1, iterations - 1)
            temperature = 320.0 * (0.0025 ** progress)
            proposal = None
            if rng.random() < repair_probability:
                proposal = self.repair_move(current, current_eval, rng)
                if proposal is not None:
                    repairs += 1
            if proposal is None:
                proposal = self.random_swap(current, rng)
            proposal_eval = self.problem.evaluate(proposal)
            evaluations += 1
            delta = trajectory_energy(
                proposal_eval, trajectory_mode
            ) - trajectory_energy(current_eval, trajectory_mode)
            if delta >= 0 or rng.random() < math.exp(delta / max(temperature, 1e-9)):
                current = proposal
                current_eval = proposal_eval
                accepted += 1
            if quality(proposal_eval) > quality(best_eval):
                best = proposal
                best_eval = proposal_eval

        best, best_eval, polished_evaluations = self.polish(
            best, polish_rounds
        )
        evaluations += polished_evaluations
        return RestartResult(
            restart_index=restart_index,
            seed=seed,
            trajectory_mode=trajectory_mode,
            mapping=best,
            support_count=best_eval.support_count,
            cover_minimum=best_eval.cover_minimum,
            evaluations=evaluations,
            accepted_moves=accepted,
            repair_moves=repairs,
        )


def _restart_seed(base_seed: int, restart_index: int) -> int:
    digest = hashlib.sha256(f"{base_seed}:{restart_index}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big")


def _worker(arguments: tuple[int, int, int, float, int, int]) -> RestartResult:
    restart_index, seed, iterations, repair_probability, cap, polish_rounds = arguments
    problem = load_problem()
    search = ConstructiveSearch(problem, cap)
    return search.run_restart(
        restart_index=restart_index,
        seed=seed,
        iterations=iterations,
        repair_probability=repair_probability,
        polish_rounds=polish_rounds,
    )


def _result_sort_key(result: RestartResult) -> tuple[int, int, int, tuple[str, ...]]:
    if result.cover_minimum <= 8:
        return (1, result.support_count, -result.cover_minimum, tuple(result.mapping))
    return (0, -result.cover_minimum, result.support_count, tuple(result.mapping))


def _write_artifacts(
    output_dir: Path,
    problem: Problem,
    config: SearchConfig,
    results: Sequence[RestartResult],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    unique: dict[tuple[str, ...], RestartResult] = {}
    for result in results:
        previous = unique.get(result.mapping)
        if previous is None or _result_sort_key(result) > _result_sort_key(previous):
            unique[result.mapping] = result
    ranked = sorted(unique.values(), key=_result_sort_key, reverse=True)
    selected = ranked[: config.top_candidates]

    seed_rows = [
        {
            "restart_index": result.restart_index,
            "seed": result.seed,
            "trajectory_mode": result.trajectory_mode,
            "raw_train_supported_merges": result.support_count,
            "candidate_local_cover_minimum": result.cover_minimum,
            "evaluations": result.evaluations,
            "accepted_moves": result.accepted_moves,
            "constructive_repair_moves": result.repair_moves,
        }
        for result in sorted(results, key=lambda row: row.restart_index)
    ]
    write_tsv(output_dir / "restart_seeds.tsv", seed_rows)

    candidate_summaries = []
    for candidate_index, result in enumerate(selected, start=1):
        evaluation = problem.evaluate(result.mapping)
        payload = problem.candidate_payload(
            evaluation,
            provenance={
                "base_seed": config.seed,
                "restart_index": result.restart_index,
                "restart_seed": result.seed,
                "trajectory_mode": result.trajectory_mode,
                "iterations": config.iterations,
                "repair_probability": config.repair_probability,
                "repair_assignment_cap": config.repair_assignment_cap,
                "polish_rounds": config.polish_rounds,
                "candidate_rank_in_scout_output": candidate_index,
            },
        )
        stem = f"candidate_{candidate_index:03d}"
        (output_dir / f"{stem}.json").write_text(
            canonical_json(payload), encoding="utf-8"
        )
        write_tsv(output_dir / f"{stem}_mapping.tsv", payload["mapping"])
        write_tsv(output_dir / f"{stem}_raw_renders.tsv", payload["raw_merges"])
        cover_rows = [
            {
                "cover_order": order,
                "rank": rank,
                "merge": problem.merges[rank - 1].merged,
            }
            for order, rank in enumerate(
                payload["candidate_local_canonical_cover_ranks"], start=1
            )
        ]
        if cover_rows:
            write_tsv(output_dir / f"{stem}_cover.tsv", cover_rows)
        candidate_summaries.append(
            {
                "candidate_file": f"{stem}.json",
                "candidate_id": payload["candidate_id"],
                "raw_train_supported_merge_count": evaluation.support_count,
                "candidate_local_exact_cover_minimum": evaluation.cover_minimum,
                "canonical_cover_ranks": payload[
                    "candidate_local_canonical_cover_ranks"
                ],
                "restart_index": result.restart_index,
                "restart_seed": result.seed,
                "trajectory_mode": result.trajectory_mode,
            }
        )

    summary = {
        "schema": "gdt615-stage0-heuristic-scout-result-v1",
        "claim": CLAIM,
        "scientific_pass": False,
        "global_optimality_claimed": False,
        "infeasibility_claimed": False,
        "registered_input_hashes": problem.input_hashes,
        "configuration": {
            "seed": config.seed,
            "restart_seeds": [
                _restart_seed(config.seed, index) for index in range(config.restarts)
            ],
            "restarts": config.restarts,
            "iterations_per_restart": config.iterations,
            "workers": config.workers,
            "repair_probability": config.repair_probability,
            "repair_assignment_cap": config.repair_assignment_cap,
            "polish_rounds": config.polish_rounds,
            "top_candidates": config.top_candidates,
        },
        "restart_count_completed": len(results),
        "deterministic_evaluation_count": sum(row.evaluations for row in results),
        "candidates": candidate_summaries,
    }
    (output_dir / "SCOUT_RESULT.json").write_text(
        canonical_json(summary), encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=615_000)
    parser.add_argument("--restarts", type=int, default=16)
    parser.add_argument("--iterations", type=int, default=25_000)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--repair-probability", type=float, default=0.78)
    parser.add_argument("--repair-assignment-cap", type=int, default=4_096)
    parser.add_argument("--polish-rounds", type=int, default=4)
    parser.add_argument("--top-candidates", type=int, default=8)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="must be a new directory below artifacts/stage0_scout_work",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.restarts < 1 or args.iterations < 1:
        raise ValueError("restarts and iterations must be positive")
    if not 0.0 <= args.repair_probability <= 1.0:
        raise ValueError("repair probability must be within [0,1]")
    if not 1 <= args.workers <= 32:
        raise ValueError("workers must be within 1..32")
    if args.repair_assignment_cap < 1 or args.top_candidates < 1:
        raise ValueError("assignment cap and top-candidates must be positive")
    output_dir = args.output_dir or (
        WORK_ROOT
        / f"seed_{args.seed}_r{args.restarts}_i{args.iterations}"
    )
    output_dir = require_work_path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing scout output: {output_dir}")

    config = SearchConfig(
        seed=args.seed,
        restarts=args.restarts,
        iterations=args.iterations,
        workers=args.workers,
        repair_probability=args.repair_probability,
        repair_assignment_cap=args.repair_assignment_cap,
        polish_rounds=args.polish_rounds,
        top_candidates=args.top_candidates,
    )
    jobs = [
        (
            index,
            _restart_seed(config.seed, index),
            config.iterations,
            config.repair_probability,
            config.repair_assignment_cap,
            config.polish_rounds,
        )
        for index in range(config.restarts)
    ]
    if config.workers == 1:
        results = [_worker(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=config.workers) as executor:
            results = list(executor.map(_worker, jobs))
    problem = load_problem()
    _write_artifacts(output_dir, problem, config, results)
    best = max(results, key=_result_sort_key)
    print(
        "SCOUT_ONLY",
        f"support={best.support_count}/64",
        f"candidate_local_cover={best.cover_minimum}",
        f"output={output_dir.relative_to(ROOT)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
