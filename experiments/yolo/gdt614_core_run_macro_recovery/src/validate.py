#!/usr/bin/env python3
"""Independent replay of the GDT614 fail-fast necessary bound."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from z3 import Bool, Or, PbEq, PbLe, Solver, sat, unsat


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt614_core_run_macro_recovery"
ART = EXP / "artifacts"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    model = json.loads((ART / "REGISTERED_MODEL.json").read_text(encoding="utf-8"))
    results = json.loads((ART / "RESULTS.json").read_text(encoding="utf-8"))
    tree_path = ROOT / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
    train_path = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_train.txt"
    held_path = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_held.txt"
    tree = tsv(tree_path)
    bound_rows = tsv(ART / "necessary_merge_bound.tsv")
    witness_rows = tsv(ART / "minimum_hitting_witness.tsv")

    check("experiment_id", manifest["experiment_id"] == "GDT614")
    check("sealed_f84", manifest["sealed_data"]["f84"] == "FORBIDDEN")
    check("sealed_f84r", manifest["sealed_data"]["f84r"] == "FORBIDDEN")
    check("registered_paid_count", model["merge_constraints"]["paid_cards"] == 8)
    check("primitive_count", len(model["primitive_cards"]) == 34)
    check("tree_count", len(tree) == 64)
    check("bound_row_count", len(bound_rows) == 64)
    check("tree_rank_order", [int(row["rank"]) for row in tree] == list(range(1, 65)))

    manifest_inputs = {item["path"]: item["sha256"] for item in manifest["inputs"]}
    for path in (tree_path, train_path, held_path):
        relative = path.relative_to(ROOT).as_posix()
        check(
            f"manifest_hash_{path.name}",
            manifest_inputs.get(relative) == digest(path),
            relative,
        )
    input_manifest = {row["path"]: row for row in tsv(ART / "input_manifest.tsv")}
    for relative, row in input_manifest.items():
        path = ROOT / relative
        check(f"run_input_exists_{row['input_id']}", path.is_file(), relative)
        check(
            f"run_input_hash_{row['input_id']}", row["sha256"] == digest(path), relative
        )

    outputs = {card["primitive_id"]: card["output"] for card in model["primitive_cards"]}
    subtree: dict[str, set[str]] = {name: set() for name in outputs}
    train_types = set(train_path.read_text(encoding="ascii").splitlines())
    held_counts = Counter(held_path.read_text(encoding="ascii").splitlines())
    independent = []
    for row in tree:
        name = row["merged"]
        outputs[name] = outputs[row["left"]] + outputs[row["right"]]
        subtree[name] = {name} | subtree[row["left"]] | subtree[row["right"]]
        value = outputs[name]
        train_support = sum(value in word for word in train_types)
        held_support = sum(count for word, count in held_counts.items() if value in word)
        independent.append(
            (
                int(row["rank"]),
                name,
                value,
                train_support,
                held_support,
                train_support > 0 and held_support > 0,
            )
        )

    for expected, published in zip(independent, bound_rows, strict=True):
        rank, name, value, train_support, held_support, supported = expected
        check(f"rank_{rank}_name", published["merged"] == name)
        check(f"rank_{rank}_render", published["raw_render"] == value)
        check(
            f"rank_{rank}_train_support",
            int(published["train_types_containing"]) == train_support,
        )
        check(
            f"rank_{rank}_held_support",
            int(published["held_events_containing"]) == held_support,
        )
        check(
            f"rank_{rank}_common_support",
            int(published["common_substring_support"]) == int(supported),
        )

    failed = [name for _rank, name, _value, _train, _held, ok in independent if not ok]
    supported = len(independent) - len(failed)
    check("failed_merge_count", len(failed) == 45, str(len(failed)))
    check("supported_merge_count", supported == 19, str(supported))

    names = [row["merged"] for row in tree]
    variables = {
        name: Bool(f"independent_paid_{index + 1:02d}")
        for index, name in enumerate(names)
    }

    def cover_solver() -> Solver:
        solver = Solver()
        for name in failed:
            solver.add(Or(*(variables[node] for node in subtree[name])))
        return solver

    registered = cover_solver()
    registered.add(PbLe([(variables[name], 1) for name in names], 8))
    check("registered_eight_unsat", registered.check() == unsat)

    lower = cover_solver()
    lower.add(PbLe([(variables[name], 1) for name in names], 17))
    check("seventeen_unsat", lower.check() == unsat)

    witness = [row["merge"] for row in witness_rows]
    check("witness_size", len(witness) == 18, str(len(witness)))
    exact = cover_solver()
    exact.add(PbEq([(variables[name], 1) for name in names], 18))
    exact.add(
        *(
            variables[name] if name in witness else ~variables[name]
            for name in names
        )
    )
    check("eighteen_witness_sat", exact.check() == sat)
    for name in failed:
        check(
            f"witness_covers_{name}",
            bool(set(witness) & subtree[name]),
            " ".join(sorted(subtree[name])),
        )

    check("result_decision", results["decision"] == "TRUTH_GENERATOR_INFEASIBLE")
    check("result_failed", results["raw_missing_common_substring_merges"] == 45)
    check("result_supported", results["raw_common_substring_supported_merges"] == 19)
    check("result_minimum", results["minimum_paid_subtree_hits_required"] == 18)
    check("result_registered", results["registered_paid_cards"] == 8)
    check("result_gap", results["minimum_minus_registered"] == 10)
    check("stopped_oracle", "twelve-panel oracle" in results["stopped_gates"])
    check("stopped_recovery", "blind recovery" in results["stopped_gates"])

    payload = {
        "schema": "gdt614-independent-validation-v1",
        "status": "PASS",
        "checks_total": len(checks),
        "checks_passed": sum(item["pass"] for item in checks),
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"VALIDATION_PASS {payload['checks_passed']}/{payload['checks_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
