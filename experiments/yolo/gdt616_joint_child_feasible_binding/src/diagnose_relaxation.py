#!/usr/bin/env python3
"""Post-terminal exact relaxation diagnosis for GDT616 Stage A.

The registered GDT616 decision is already terminal UNSAT.  This script does
not reinterpret that decision.  It asks the smallest adjacent diagnostic
question supported by the independent finite-domain encoding: how many paid
merge nodes must be permitted to have an unoverridden child concatenation
outside the frozen TRAIN-substring set while every effective output remains a
nonempty TRAIN substring and every other registered Stage-A constraint stays
fixed?

No held, LM-confirm, target, f84, or f84r input is opened.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import z3


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import independent_bound as bound  # noqa: E402


SCHEMA = "gdt616-stage-a-relaxation-diagnostic-v1"
EXPERIMENT = HERE.parent
DEFAULT_OUTPUT = EXPERIMENT / "artifacts/stage_a/RELAXATION_DIAGNOSTIC.json"
STRICT_ARTIFACTS: Mapping[str, tuple[Path, str]] = {
    "primary_result": (
        EXPERIMENT / "artifacts/stage_a/PRIMARY_RESULT.json",
        "d87d925fff5c7e185a256dacf53619b72a8fe430e2db21ce6f6232f2e906faef",
    ),
    "independent_result": (
        EXPERIMENT / "artifacts/stage_a/INDEPENDENT_RESULT.json",
        "38b7e7741850791731946d9bc963f3ad44d5147eb267e0387d6c57b71f601361",
    ),
    "comparison": (
        EXPERIMENT / "artifacts/stage_a/COMPARISON.json",
        "e098d63da66b49134e2277e5646639a20cc3b6a8c840b22394da284a1f14aa2c",
    ),
}
EXPECTED_BOUND_SOURCE_SHA256 = (
    "014d2363fd38be7979d1286afbb639cb294b0001a3fa34b05109730439804f15"
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise bound.InputError(f"JSON root is not an object: {path}")
    return value


def verify_terminal_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for label, (path, expected) in STRICT_ARTIFACTS.items():
        if not path.is_file():
            raise bound.InputError(f"missing terminal artifact: {path}")
        digest = sha256_path(path)
        if digest != expected:
            raise bound.InputError(f"terminal artifact hash drift: {label}")
        observed[label] = digest

    source = Path(bound.__file__).resolve()
    source_digest = sha256_path(source)
    if source_digest != EXPECTED_BOUND_SOURCE_SHA256:
        raise bound.InputError("independent Stage-A source hash drift")
    observed["independent_bound_source"] = source_digest

    primary = load_json(STRICT_ARTIFACTS["primary_result"][0])
    independent = load_json(STRICT_ARTIFACTS["independent_result"][0])
    comparison = load_json(STRICT_ARTIFACTS["comparison"][0])
    for label, payload in (("primary", primary), ("independent", independent)):
        if payload.get("decision") != "NO_JOINT_CHILD_FEASIBLE_BINDING":
            raise bound.InputError(f"{label} terminal decision drift")
    if comparison.get("status") != "PASS":
        raise bound.InputError("terminal comparison is not PASS")
    if comparison.get("decision") != "NO_JOINT_CHILD_FEASIBLE_BINDING":
        raise bound.InputError("terminal comparison decision drift")
    agreement = comparison.get("agreement")
    if not isinstance(agreement, dict) or agreement.get("decision") is not True:
        raise bound.InputError("terminal solvers do not agree")
    return observed


def pb_equal(expressions: Sequence[z3.BoolRef], count: int) -> z3.BoolRef:
    return z3.PbEq([(expression, 1) for expression in expressions], count)


def status_name(status: z3.CheckSatResult) -> str:
    if status == z3.sat:
        return "SAT"
    if status == z3.unsat:
        return "UNSAT"
    raise bound.SearchIncomplete(f"unexpected solver status: {status}")


def check_rank_at_count(
    rank: int,
    count: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Independent process worker for one exact rank-participation query."""

    problem = bound.load_problem()
    merge_by_rank = {merge.rank: merge for merge in problem.merges}
    merge = merge_by_rank[rank]
    encoding = bound.build_encoding(problem)
    queries = bound.ExactQueries(encoding.solver, timeout_seconds)
    violations = [encoding.violation[item.rank] for item in problem.merges]
    minimum_constraint = pb_equal(violations, count)
    status = queries.check(minimum_constraint, encoding.violation[rank])
    row: dict[str, Any] = {
        "rank": rank,
        "merge": merge.merged,
        "can_participate_in_this_relaxation_count": status == z3.sat,
        "status": status_name(status),
    }
    row["query_count"] = queries.query_count
    row["sat_queries"] = queries.sat_count
    row["unsat_queries"] = queries.unsat_count
    return row


def sweep_ranks(
    problem: bound.Problem,
    count: int,
    timeout_seconds: int,
    workers: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(check_rank_at_count, merge.rank, count, timeout_seconds): merge.rank
            for merge in problem.merges
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
            completed += 1
            if completed % 8 == 0 or completed == len(futures):
                feasible = sum(
                    row["can_participate_in_this_relaxation_count"] for row in rows
                )
                print(
                    f"rank sweep k={count}: {completed}/{len(futures)} complete, "
                    f"{feasible} SAT",
                    file=sys.stderr,
                    flush=True,
                )
    return sorted(rows, key=lambda row: int(row["rank"]))


def diagnose(
    problem: bound.Problem,
    timeout_seconds: int,
    workers: int,
) -> dict[str, Any]:

    # Zero violations is the already completed terminal GDT616 query.  Its two
    # result files and PASS comparison are verified byte-for-byte above, so a
    # third expensive execution would add no diagnostic information.
    boundary_queries: list[dict[str, Any]] = [
        {
            "paid_child_train_gate_violations_equal": 0,
            "status": "UNSAT",
            "evidence": "hash-verified terminal primary+independent PASS comparison",
        }
    ]
    minimum: int | None = None
    rank_feasibility: list[dict[str, Any]] = []
    rank_sweeps: list[dict[str, Any]] = []
    for count in range(1, len(problem.paid_cards) + 1):
        candidate_rows = sweep_ranks(problem, count, timeout_seconds, workers)
        any_sat = any(
            row["can_participate_in_this_relaxation_count"]
            for row in candidate_rows
        )
        boundary_queries.append(
            {
                "paid_child_train_gate_violations_equal": count,
                "status": "SAT" if any_sat else "UNSAT",
                "evidence": "complete 64-rank participation sweep",
            }
        )
        rank_sweeps.append(
            {
                "paid_child_train_gate_violations_equal": count,
                "rows": candidate_rows,
            }
        )
        if any_sat:
            minimum = count
            rank_feasibility = candidate_rows
            break
    if minimum is None:
        raise bound.InputError(
            "no solution even when every one of the eight paid-child TRAIN gates is relaxed"
        )
    for row in rank_feasibility:
        row["can_participate_in_a_minimum_relaxation"] = row.pop(
            "can_participate_in_this_relaxation_count"
        )
    feasible_ranks = [
        int(row["rank"])
        for row in rank_feasibility
        if row["can_participate_in_a_minimum_relaxation"]
    ]

    if not feasible_ranks:
        raise bound.InputError("minimum count was SAT but no violation rank is feasible")

    # Fix the lowest participating rank only to obtain one reproducible,
    # fixed-seed representative witness.  It is not a registered tiebreak or
    # a recovered parameter, and other minimum witnesses may use other tuples.
    representative_anchor_rank = min(feasible_ranks)
    encoding = bound.build_encoding(problem)
    violations = [encoding.violation[merge.rank] for merge in problem.merges]
    encoding.solver.add(
        pb_equal(violations, minimum),
        encoding.violation[representative_anchor_rank],
    )
    encoding.solver.set(timeout=timeout_seconds * 1000)
    representative_status = encoding.solver.check()
    if representative_status != z3.sat:
        if representative_status == z3.unknown:
            raise bound.SearchIncomplete(
                "representative witness query returned unknown: "
                + encoding.solver.reason_unknown()
            )
        raise bound.InputError("feasible anchor rank lost its representative witness")
    model = encoding.solver.model()
    witness = bound.extract_and_replay(problem, encoding, model, minimum)
    representative_ranks = witness["paid_child_span_violation_ranks"]
    if representative_anchor_rank not in representative_ranks:
        raise bound.InputError("representative witness lost its anchor rank")

    merge_by_rank = {row["rank"]: row for row in witness["merge_replay"]}
    representative_breaks = [merge_by_rank[rank] for rank in representative_ranks]
    if any(row["child_composition_in_train"] is not False for row in representative_breaks):
        raise bound.InputError("representative break unexpectedly lies in TRAIN")
    if any(row["mode"] != "PAID" for row in representative_breaks):
        raise bound.InputError("representative break is not a paid node")

    feasible_rows = [
        row for row in rank_feasibility if row["can_participate_in_a_minimum_relaxation"]
    ]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "decision_preserved": "NO_JOINT_CHILD_FEASIBLE_BINDING",
        "diagnostic_result": "SAT_AFTER_MINIMUM_CHILD_TRAIN_GATE_RELAXATION",
        "minimum_relaxation": {
            "total_train_gate_violations": minimum,
            "child_train_gate_violations": minimum,
            "effective_train_gate_violations": 0,
            "all_other_registered_stage_a_constraints_unchanged": True,
            "exact_registered_paid_cards_used": len(problem.paid_cards),
            "paid_budget_changed": False,
        },
        "boundary_queries": boundary_queries,
        "minimum_relaxation_rank_summary": {
            "feasible_rank_count": len(feasible_ranks),
            "feasible_ranks": feasible_ranks,
            "feasible_merges": [row["merge"] for row in feasible_rows],
            "representative_anchor_rank": representative_anchor_rank,
            "representative_violation_ranks": representative_ranks,
            "representative_violation_merges": [
                row["merge"] for row in representative_breaks
            ],
        },
        "rank_sweeps": rank_sweeps,
        "rank_feasibility": rank_feasibility,
        "representative_breaks": representative_breaks,
        "representative_witness": witness,
        "paid_budget_diagnostic": {
            "status": "NOT_NEEDED_FOR_MINIMUM_REPAIR",
            "reason": (
                "The model is SAT after the minimum TRAIN-gate relaxation while "
                "retaining exactly the registered eight distinct paid locations and "
                "using every registered paid card exactly once."
            ),
        },
        "model_scope": {
            "kept": [
                "complete same-role primitive/output-card bijection",
                "all eight registered paid cards used once at eight distinct merge nodes",
                "recursive directed left-to-right child concatenation",
                "all 64 effective merge outputs nonempty and in frozen TRAIN",
                "all default child compositions in frozen TRAIN",
                "paid output differs from its unoverridden child composition",
                "qok paid-macro prohibition",
            ],
            "relaxed_only": (
                "At the counted paid nodes, the unoverridden child concatenation may "
                "miss frozen TRAIN; the paid effective output still must be in TRAIN."
            ),
            "interpretation": (
                "This locates the smallest boundary failure of the synthetic Stage-A "
                "world. It does not revise the registered UNSAT decision or establish "
                "a Voynich value or meaning."
            ),
        },
        "counts": {
            "primitives": len(problem.primitives),
            "merges": len(problem.merges),
            "paid_cards": len(problem.paid_cards),
            "train_substrings": len(problem.train_substrings),
            "effective_value_universe": len(encoding.id_to_value),
            "train_relation_tuples": sum(
                len(relation.train_pairs) for relation in encoding.relations
            ),
        },
        "solver": {
            "backend": "Z3 finite-domain integer/Boolean tables",
            "z3_version": z3.get_version_string(),
            "random_seed": 0,
            "query_count": 1
            + sum(
                int(row["query_count"])
                for sweep in rank_sweeps
                for row in sweep["rows"]
            ),
            "sat_queries": 1
            + sum(
                int(row["sat_queries"])
                for sweep in rank_sweeps
                for row in sweep["rows"]
            ),
            "unsat_queries": sum(
                int(row["unsat_queries"])
                for sweep in rank_sweeps
                for row in sweep["rows"]
            ),
            "parallel_rank_workers": workers,
            "representative_witness_selection": [
                "minimum paid-child TRAIN-gate violation count",
                "lowest feasible violation rank as a fixed anchor",
                "Z3 fixed random seed 0 completion; no mapping/card tiebreak claim",
            ],
        },
        "input_sha256": dict(sorted(problem.input_sha256.items())),
        "terminal_artifact_sha256": verify_terminal_inputs(),
        "access": {
            "held_or_lm_confirm_opened": False,
            "voynich_target_or_meaning_opened": False,
            "f84_or_f84r_opened": False,
        },
    }
    return result


def self_test() -> None:
    strict = bound.toy_problem(train=("a", "b", "ab", "ba", "x"))
    strict_encoding = bound.build_encoding(strict)
    strict_queries = bound.ExactQueries(strict_encoding.solver, 30)
    strict_terms = [strict_encoding.violation[1]]
    if strict_queries.check(pb_equal(strict_terms, 0)) != z3.sat:
        raise bound.InputError("strict toy did not remain SAT at zero violations")

    one = bound.toy_problem(train=("a", "b", "x"))
    one_encoding = bound.build_encoding(one)
    one_queries = bound.ExactQueries(one_encoding.solver, 30)
    one_terms = [one_encoding.violation[1]]
    if one_queries.check(pb_equal(one_terms, 0)) != z3.unsat:
        raise bound.InputError("one-violation toy was not UNSAT at zero")
    if one_queries.check(pb_equal(one_terms, 1)) != z3.sat:
        raise bound.InputError("one-violation toy was not SAT at one")
    print("GDT616_RELAXATION_DIAGNOSTIC_SELFTEST_PASS 3/3")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--execute-diagnostic", action="store_true")
    parser.add_argument("--time-limit-seconds", type=int, default=43_200)
    parser.add_argument(
        "--workers",
        type=int,
        default=min(32, os.cpu_count() or 1),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        self_test()
        return 0
    if not args.execute_diagnostic:
        raise SystemExit("refusing full diagnostic run without --execute-diagnostic")
    if not 1 <= args.time_limit_seconds <= 43_200:
        raise SystemExit("--time-limit-seconds must be in 1..43200")
    if not 1 <= args.workers <= 32:
        raise SystemExit("--workers must be in 1..32")
    verify_terminal_inputs()
    problem = bound.load_problem()
    result = diagnose(problem, args.time_limit_seconds, args.workers)
    result["source_sha256"] = sha256_path(Path(__file__).resolve())
    output = args.output.resolve()
    bound.atomic_write(output, bound.canonical_json(result))
    print(
        json.dumps(
            {
                "minimum": result["minimum_relaxation"],
                "output": str(output),
                "rank_summary": result["minimum_relaxation_rank_summary"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
