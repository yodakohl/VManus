#!/usr/bin/env python3
"""Run both frozen GDT616 Stage-A solvers and compare their exact result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
PRIMARY = EXP / "src/primary_bound.py"
INDEPENDENT = EXP / "src/independent_bound.py"
PASS_DECISION = "JOINT_CHILD_NECESSARY_BOUND_SAT"
FAIL_DECISION = "NO_JOINT_CHILD_FEASIBLE_BINDING"


class IntegrationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IntegrationError(f"result is not an object: {path}")
    return value


def mapping_signature(result: dict[str, Any], backend: str) -> list[list[object]]:
    witness = result.get("witness")
    if not isinstance(witness, dict):
        return []
    key = "mapping" if backend == "primary" else "primitive_mapping"
    rows = witness.get(key, [])
    return [[row["primitive_id"], row["card_id"], row["output"]] for row in rows]


def paid_signature(result: dict[str, Any], backend: str) -> list[list[object]]:
    witness = result.get("witness")
    if not isinstance(witness, dict):
        return []
    key = "paid_assignments" if backend == "primary" else "actual_paid_locations"
    rows = witness.get(key, [])
    return [[row["rank"], row["card_id"], row["output"]] for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-registered", action="store_true")
    parser.add_argument("--output-root", type=Path, default=Path("gdt616-stage-a-run"))
    parser.add_argument("--time-limit-seconds", type=int, default=43_200)
    args = parser.parse_args(argv)
    if not args.execute_registered:
        raise SystemExit("refusing registered execution without --execute-registered")
    if not 1 <= args.time_limit_seconds <= 43_200:
        raise SystemExit("time limit must be in 1..43200")

    output_root = args.output_root.resolve()
    if output_root.exists():
        raise SystemExit(f"refusing existing output root: {output_root}")
    output_root.mkdir(parents=True)
    primary_out = output_root / "PRIMARY_RESULT.json"
    independent_out = output_root / "INDEPENDENT_RESULT.json"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = [
        [
            sys.executable,
            str(PRIMARY),
            "--execute-registered",
            "--output",
            str(primary_out),
            "--time-limit-seconds",
            str(args.time_limit_seconds),
        ],
        [
            sys.executable,
            str(INDEPENDENT),
            "--execute-registered",
            "--output",
            str(independent_out),
            "--timeout-seconds",
            str(args.time_limit_seconds),
        ],
    ]
    processes = [subprocess.Popen(command, cwd=ROOT, env=env) for command in commands]
    return_codes = [process.wait() for process in processes]
    if return_codes != [0, 0]:
        raise IntegrationError(f"solver return codes differ from success: {return_codes}")

    primary = load_json(primary_out)
    independent = load_json(independent_out)
    decisions = [primary.get("decision"), independent.get("decision")]
    if decisions[0] != decisions[1] or decisions[0] not in {PASS_DECISION, FAIL_DECISION}:
        raise IntegrationError(f"solver decisions disagree: {decisions}")
    if decisions[0] == PASS_DECISION:
        if mapping_signature(primary, "primary") != mapping_signature(independent, "independent"):
            raise IntegrationError("canonical primitive mappings disagree")
        if paid_signature(primary, "primary") != paid_signature(independent, "independent"):
            raise IntegrationError("canonical paid assignments disagree")

    canonical_agreement: bool | None = True if decisions[0] == PASS_DECISION else None
    result = {
        "schema": "gdt616-stage-a-dual-solver-comparison-v1",
        "status": "PASS",
        "decision": decisions[0],
        "agreement": {
            "decision": True,
            "canonical_mapping": canonical_agreement,
            "canonical_paid_assignment": canonical_agreement,
        },
        "results": [
            {"backend": "primary", "path": primary_out.name, "sha256": sha256(primary_out)},
            {"backend": "independent", "path": independent_out.name, "sha256": sha256(independent_out)},
        ],
        "held_or_lm_confirm_opened": False,
        "voynich_target_opened": False,
        "f84_or_f84r_opened": False,
    }
    comparison = output_root / "COMPARISON.json"
    comparison.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT616_STAGE_A_DUAL_SOLVER_PASS decision={decisions[0]} output={comparison}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
