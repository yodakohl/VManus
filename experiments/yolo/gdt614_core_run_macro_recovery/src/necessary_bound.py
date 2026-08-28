#!/usr/bin/env python3
"""Exact pre-world necessary bound for GDT614.

This intentionally ignores grammar, macro licensing, card type, collisions,
and paid-child exposure.  It asks only whether eight paid nodes can touch every
raw merge render that lacks even substring support in one frozen partition.
Failure under this permissive relaxation proves the registered world
infeasible.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from z3 import Bool, Or, PbEq, PbLe, Solver, is_true, sat, unsat


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_problem(root: Path) -> dict:
    exp = root / "experiments/yolo/gdt614_core_run_macro_recovery"
    paths = {
        "registered_model": exp / "artifacts/REGISTERED_MODEL.json",
        "merge_tree": root
        / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv",
        "train": root
        / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_train.txt",
        "held": root
        / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_held.txt",
    }
    model = json.loads(paths["registered_model"].read_text(encoding="utf-8"))
    merges = read_tsv(paths["merge_tree"])
    train_counts = Counter(paths["train"].read_text(encoding="ascii").splitlines())
    held_counts = Counter(paths["held"].read_text(encoding="ascii").splitlines())
    return {
        "paths": paths,
        "model": model,
        "merges": merges,
        "train_counts": train_counts,
        "held_counts": held_counts,
    }


def derive_rows(problem: dict) -> tuple[list[dict], dict[str, set[str]]]:
    primitive_output = {
        card["primitive_id"]: card["output"]
        for card in problem["model"]["primitive_cards"]
    }
    render = dict(primitive_output)
    descendants: dict[str, set[str]] = {
        primitive: set() for primitive in primitive_output
    }
    train_types = set(problem["train_counts"])
    held_counts = problem["held_counts"]
    rows = []
    for merge in problem["merges"]:
        name = merge["merged"]
        render[name] = render[merge["left"]] + render[merge["right"]]
        descendants[name] = (
            {name}
            | descendants[merge["left"]]
            | descendants[merge["right"]]
        )
        value = render[name]
        train_support = sum(value in word for word in train_types)
        held_support = sum(
            count for word, count in held_counts.items() if value in word
        )
        rows.append(
            {
                "rank": int(merge["rank"]),
                "merged": name,
                "raw_render": value,
                "raw_render_length": len(value),
                "train_types_containing": train_support,
                "held_events_containing": held_support,
                "common_substring_support": int(
                    train_support > 0 and held_support > 0
                ),
                "affecting_merge_nodes": " ".join(
                    sorted(
                        descendants[name],
                        key=lambda node: next(
                            int(row["rank"])
                            for row in problem["merges"]
                            if row["merged"] == node
                        ),
                    )
                ),
            }
        )
    return rows, descendants


def hitting_solver(
    merge_names: list[str], failed: list[str], descendants: dict[str, set[str]]
) -> tuple[int, list[str], dict[str, Bool]]:
    variables = {name: Bool(f"paid_{index + 1:02d}") for index, name in enumerate(merge_names)}

    def base() -> Solver:
        solver = Solver()
        for node in failed:
            solver.add(Or(*(variables[item] for item in descendants[node])))
        return solver

    minimum = None
    for limit in range(len(merge_names) + 1):
        solver = base()
        solver.add(PbLe([(variables[name], 1) for name in merge_names], limit))
        if solver.check() == sat:
            minimum = limit
            break
    if minimum is None:
        raise RuntimeError("hitting problem unexpectedly infeasible")

    # Deterministic lexicographically earliest minimum witness: prefer an
    # earlier ranked node whenever an exact-minimum completion remains SAT.
    fixed = []
    chosen = []
    for name in merge_names:
        trial = base()
        trial.add(PbEq([(variables[item], 1) for item in merge_names], minimum))
        trial.add(*fixed, variables[name])
        if trial.check() == sat:
            fixed.append(variables[name])
            chosen.append(name)
        else:
            fixed.append(~variables[name])
    if len(chosen) != minimum:
        raise RuntimeError((len(chosen), minimum))

    lower = base()
    lower.add(PbLe([(variables[name], 1) for name in merge_names], minimum - 1))
    if lower.check() != unsat:
        raise RuntimeError("minimum lower-bound replay did not return UNSAT")
    exact = base()
    exact.add(PbEq([(variables[name], 1) for name in merge_names], minimum))
    exact.add(*(variables[name] if name in chosen else ~variables[name] for name in merge_names))
    if exact.check() != sat:
        raise RuntimeError("minimum witness replay did not return SAT")
    return minimum, chosen, variables


def run(root: Path, out: Path) -> dict:
    problem = load_problem(root)
    rows, descendants = derive_rows(problem)
    merge_names = [row["merged"] for row in rows]
    failed = [row["merged"] for row in rows if not row["common_substring_support"]]
    minimum, chosen, _variables = hitting_solver(merge_names, failed, descendants)
    registered_paid = int(problem["model"]["merge_constraints"]["paid_cards"])

    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "necessary_merge_bound.tsv", list(rows[0]), rows)
    rank = {row["merged"]: row["rank"] for row in rows}
    witness_rows = [
        {
            "rank": rank[name],
            "merge": name,
            "selected_in_minimum_hitting_witness": 1,
        }
        for name in chosen
    ]
    write_tsv(
        out / "minimum_hitting_witness.tsv",
        list(witness_rows[0]),
        witness_rows,
    )
    input_rows = [
        {
            "input_id": key,
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for key, path in sorted(problem["paths"].items())
    ]
    write_tsv(out / "input_manifest.tsv", list(input_rows[0]), input_rows)

    decision = (
        "TRUTH_GENERATOR_INFEASIBLE"
        if minimum > registered_paid
        else "NECESSARY_BOUND_PASSES"
    )
    result = {
        "schema": "gdt614-necessary-merge-hitting-bound-v1",
        "decision": decision,
        "claim_ceiling": (
            "Necessary raw-substring/tree bound for registered W614_0 only; "
            "no target, key, word, language, plaintext, or meaning"
        ),
        "merge_nodes": len(rows),
        "raw_common_substring_supported_merges": len(rows) - len(failed),
        "raw_missing_common_substring_merges": len(failed),
        "registered_paid_cards": registered_paid,
        "minimum_paid_subtree_hits_required": minimum,
        "registered_capacity_satisfies_necessary_bound": minimum <= registered_paid,
        "minimum_minus_registered": minimum - registered_paid,
        "minimum_witness": chosen,
        "lower_bound_unsat_at": minimum - 1,
        "more_permissive_than_registered_model": [
            "ignores grammar and all 21 transition constraints",
            "ignores macro side licenses and qok macro prohibition",
            "ignores output collisions and paid card types",
            "ignores paid-child counterpart exposure",
            "requires only substring presence, not an ordered parse or unit tiling",
        ],
        "stopped_gates": [
            "joint ordered truth-world construction",
            "three-world generation",
            "twelve-panel oracle",
            "blind recovery",
        ],
    }
    (out / "RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result
