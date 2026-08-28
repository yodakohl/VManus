#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import z3

from structural_model import (
    EXPECTED_HASHES,
    RELAXED_WITNESS_CARDS,
    RELAXED_WITNESS_ROLES,
    RAW_MAX60_WITNESS_ROLES,
    RID,
    ROLE_NAMES,
    build_solver,
    build_raw_leaf_solver,
    constrain_witness,
    extract_witness,
    load_inputs,
    query_fingerprint,
    valid_substrings,
)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery"
ART = EXP / "artifacts"


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def solve_query(rows, primitives, *, name, skip_child, forbid_family, fixed_witness=False):
    solver, variables, patterns = build_solver(
        rows,
        primitives,
        skip_card_child_gate=skip_child,
        forbid_all_qok_whole=forbid_family,
    )
    query_sha256 = query_fingerprint(
        rows,
        skip_card_child_gate=skip_child,
        forbid_all_qok_whole=forbid_family,
    )
    status = solver.check()
    result = {
        "query": name,
        "status": str(status),
        "skip_card_child_gate": skip_child,
        "forbid_all_qok_whole": forbid_family,
        "solver": "z3",
        "solver_version": z3.get_version_string(),
        "query_sha256": query_sha256,
    }
    if status == z3.unknown:
        result["reason_unknown"] = solver.reason_unknown()
    elif status == z3.sat and fixed_witness:
        witness_solver, witness_variables, witness_patterns = build_solver(
            rows,
            primitives,
            skip_card_child_gate=skip_child,
            forbid_all_qok_whole=forbid_family,
        )
        constrain_witness(
            witness_solver,
            witness_variables,
            RELAXED_WITNESS_ROLES,
            RELAXED_WITNESS_CARDS,
        )
        if witness_solver.check() != z3.sat:
            raise RuntimeError("frozen relaxed control witness drift")
        result["witness"] = extract_witness(
            witness_solver.model(), rows, witness_variables, witness_patterns
        )
    return result


def main() -> int:
    if z3.get_version_string() != "4.15.3":
        raise RuntimeError(
            f"install requirements.txt; expected Z3 4.15.3, got {z3.get_version_string()}"
        )
    ART.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(EXP / "src/prepare.py")], cwd=ROOT, check=True)
    subprocess.run(
        [sys.executable, str(EXP / "src/length_deck_audit.py")], cwd=ROOT, check=True
    )
    subprocess.run(
        [sys.executable, str(EXP / "src/grammar_scope_bridge.py")], cwd=ROOT, check=True
    )
    rows, primitives, input_hashes = load_inputs(ROOT)
    queries = [
        solve_query(
            rows,
            primitives,
            name="STRICT_REGISTERED_QOK_ONLY",
            skip_child=False,
            forbid_family=False,
        ),
        solve_query(
            rows,
            primitives,
            name="STRICT_SENSITIVITY_ALL_QOK_FAMILY",
            skip_child=False,
            forbid_family=True,
        ),
        solve_query(
            rows,
            primitives,
            name="CONTROL_DROP_CARD_CHILD_GATE",
            skip_child=True,
            forbid_family=False,
            fixed_witness=True,
        ),
    ]
    expected = ("unsat", "unsat", "sat")
    actual = tuple(query["status"] for query in queries)
    if actual != expected:
        raise RuntimeError(f"unexpected solver result {actual}")

    raw_solver, raw_variables, raw_accepted = build_raw_leaf_solver(rows, primitives)
    raw_solver.add(z3.Sum([z3.If(value, 1, 0) for value in raw_accepted.values()]) >= 61)
    raw_61_status = raw_solver.check()
    if raw_61_status != z3.unsat:
        raise RuntimeError(f"raw merge >=61 drift: {raw_61_status}")
    fixed_raw_solver, fixed_raw_variables, fixed_raw_accepted = build_raw_leaf_solver(
        rows, primitives
    )
    for primitive, role in RAW_MAX60_WITNESS_ROLES.items():
        fixed_raw_solver.add(fixed_raw_variables[primitive] == RID[role])
    if fixed_raw_solver.check() != z3.sat:
        raise RuntimeError("raw max60 witness drift")
    fixed_raw_model = fixed_raw_solver.model()
    raw_bad = [
        name
        for name, expression in fixed_raw_accepted.items()
        if not z3.is_true(fixed_raw_model.eval(expression))
    ]
    forced_status = {}
    for name in raw_bad:
        forced_solver, _forced_variables, forced_accepted = build_raw_leaf_solver(
            rows, primitives
        )
        forced_solver.add(
            z3.Sum([z3.If(value, 1, 0) for value in forced_accepted.values()]) >= 60,
            forced_accepted[name],
        )
        forced_status[name] = str(forced_solver.check())
    if raw_bad != ["daN", "dal", "dar", "daI"] or set(forced_status.values()) != {"unsat"}:
        raise RuntimeError(f"raw max60 explanation drift: {raw_bad} {forced_status}")

    relaxed = queries[2]["witness"]
    illegal_card_children = [
        row["unit"]
        for row in relaxed["merges"]
        if row["card"] != "none" and not row["child_embeddable"]
    ]
    if not illegal_card_children:
        raise RuntimeError("relaxed control did not isolate the removed gate")
    result = {
        "schema": "gdt613-results-v1",
        "decision": "MODEL_SCOPE_UNDERSPECIFIED_OR_INFEASIBLE",
        "status": "STOPPED_BEFORE_TRUTH_WORLD_OR_TARGET",
        "reason": (
            "Three pre-world necessary conditions fail: the strict flattened-piece EBNF has no "
            "34-role plus 4-short/4-whole-card assignment satisfying all 64 direct/default "
            "composition witnesses and every paid card child witness; the frozen deck also "
            "requires 23 unique one-character outputs where only 21 frozen-Latin values meet "
            "the registered exposure thresholds, and no WHOLE length reaches eight train word "
            "types through the published connector-only envelope."
        ),
        "solver_version": z3.get_version_string(),
        "inputs_sha256": input_hashes,
        "query_results": [
            {key: value for key, value in query.items() if key != "witness"}
            for query in queries
        ],
        "relaxed_control": {
            "status": "sat",
            "cards_with_illegal_unoverridden_children": illegal_card_children,
            "count": len(illegal_card_children),
        },
        "claim_ceiling": (
            "Rejects only this exact flattened-piece scope plus registered simultaneous "
            "coverage/card-child gates; no output, Latin recovery, target, or meaning claim."
        ),
        "next_route": (
            "Register adjacent carrier runs, type former WHOLE cards as embeddable macro cores, "
            "move at least two functional length-one cards to length two, then repeat natural-Latin "
            "oracle/recovery and open no target before it passes."
        ),
    }
    (ART / "RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ART / "relaxed_control_witness.json").write_text(
        json.dumps(relaxed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ART / "raw_leaf_merge_bound.json").write_text(
        json.dumps(
            {
                "schema": "gdt613-raw-leaf-bound-v1",
                "maximum_embeddable_merges": 60,
                "at_least_61_status": str(raw_61_status),
                "fixed_witness_roles": RAW_MAX60_WITNESS_ROLES,
                "fixed_witness_illegal_merges": raw_bad,
                "each_illegal_forced_inside_any_60_solution": forced_status,
                "scope": "supplemental raw primitive-leaf diagnostic; paid descendants are not collapsed",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_tsv(
        ART / "structural_queries.tsv",
        [
            "query",
            "status",
            "skip_card_child_gate",
            "forbid_all_qok_whole",
            "solver",
            "solver_version",
            "query_sha256",
        ],
        [{key: query[key] for key in (
            "query", "status", "skip_card_child_gate", "forbid_all_qok_whole",
            "solver", "solver_version", "query_sha256"
        )} for query in queries],
    )
    patterns = valid_substrings()
    write_tsv(
        ART / "grammar_substring_counts.tsv",
        ["role_length", "embeddable_patterns"],
        [
            {"role_length": length, "embeddable_patterns": len(patterns[length])}
            for length in sorted(patterns)
        ],
    )
    write_tsv(
        ART / "structural_input_hashes.tsv",
        ["input", "sha256"],
        [{"input": name, "sha256": input_hashes[name]} for name in sorted(EXPECTED_HASHES)],
    )
    write_tsv(
        ART / "relaxed_role_assignment.tsv",
        ["primitive", "role_code", "role"],
        [
            {
                "primitive": primitive,
                "role_code": role,
                "role": ROLE_NAMES[role],
            }
            for primitive, role in sorted(relaxed["roles"].items())
        ],
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
