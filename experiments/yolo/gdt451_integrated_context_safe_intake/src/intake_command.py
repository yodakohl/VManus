#!/usr/bin/env python3
"""Issue an intake result with identity, advisory history, and live execution separate."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
CERTIFIER_PATH = ROOT / "experiments/yolo/gdt446_identity_execution_intake_split/src/intake_certificate_v2.py"
TARGETS_PATH = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck/artifacts/gdt449_target_context_robustness.tsv"
FALSE_SAFE_PATH = ROOT / "experiments/yolo/gdt450_target_robustness_page_holdout/artifacts/gdt450_false_safe_cases.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CERTIFIER = load_module("gdt446_certifier_for_gdt451_intake", CERTIFIER_PATH)
TARGET_HISTORY = {row["target_recipe"]: row for row in read_tsv(TARGETS_PATH)}
FALSE_SAFE_TARGETS = {row["target_recipe"] for row in read_tsv(FALSE_SAFE_PATH)}


def advisory_relation(status: str, live_decision: str) -> str:
    live_readable = live_decision in {"READ", "READ_AMBER"}
    if status == "NO_GDT449_TARGET_HISTORY":
        return "NO_HISTORY__LIVE_ONLY"
    if status == "OBSERVED_CONTEXT_MIXED_READ_STOP":
        return "HISTORY_CONTEXT_DEPENDENT__LIVE_DECIDES"
    if status == "OBSERVED_CONTEXT_ALL_STOP":
        return "HISTORY_AND_LIVE_AGREE_STOP" if not live_readable else "HISTORY_STOP_BUT_LIVE_READS__LIVE_DECIDES"
    return "HISTORY_AND_LIVE_AGREE_READABLE" if live_readable else "HISTORY_READABLE_BUT_LIVE_STOPS__LIVE_DECIDES"


def issue_integrated_certificate(
    recipe: str,
    incoming_action: str = "NONE",
    incoming_argument: str = "NONE",
    scope_incoming_action: str | None = None,
    next_recipe: str = "NONE",
) -> dict[str, object]:
    recipe = recipe.upper()
    live = CERTIFIER.issue_split_certificate(
        recipe,
        incoming_action,
        incoming_argument,
        scope_incoming_action,
        next_recipe,
    )
    history = TARGET_HISTORY.get(recipe)
    history_status = history["observed_context_robustness"] if history else "NO_GDT449_TARGET_HISTORY"
    holdout_warning = "YES" if recipe in FALSE_SAFE_TARGETS else "NO"
    final_decision = str(live["execution_decision"])
    final_route = str(live["execution_route"])
    relation = advisory_relation(history_status, final_decision)
    return {
        **live,
        "advisory_history_status": history_status,
        "advisory_history_instruction": history["deck_instruction"] if history else "NO_HISTORY__RUN_LIVE_CERTIFICATE",
        "advisory_sampled_context_count": history["unique_sampled_context_count"] if history else "0",
        "advisory_stop_factor_rules": history["stop_factor_rules"] if history else "NONE",
        "gdt450_false_safe_regression_target": holdout_warning,
        "advisory_live_relation": relation,
        "final_execution_decision": final_decision,
        "final_execution_route": final_route,
        "final_decision_source": "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY",
        "identity_can_override_live_execution": "NO",
        "advisory_can_override_live_execution": "NO",
        "live_stop_is_final": "YES" if final_decision == "STOP" else "NOT_APPLICABLE",
        "precedence": "LIVE_EXECUTION>ADVISORY_HISTORY;IDENTITY_SEPARATE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True)
    parser.add_argument("--incoming-action", default="NONE")
    parser.add_argument("--incoming-argument", default="NONE")
    parser.add_argument("--scope-incoming-action", default="AUTO")
    parser.add_argument("--next-recipe", default="NONE")
    args = parser.parse_args()
    scope = None if args.scope_incoming_action.upper() == "AUTO" else args.scope_incoming_action
    result = issue_integrated_certificate(
        args.recipe,
        args.incoming_action,
        args.incoming_argument,
        scope,
        args.next_recipe,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
