#!/usr/bin/env python3
"""Issue separate identity and execution certificates for a visible recipe."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
LEGACY_PATH = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate/src/intake_certificate.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEGACY = load_module("gdt445_certificate_for_gdt446_split", LEGACY_PATH)

TIER_IDENTITY = {
    "T0_EXACT_OBSERVED": ("IDENTITY_EXACT_OBSERVED", "OBSERVED"),
    "T1_FUTURE_HIGH": ("IDENTITY_EXACT_FUTURE_HIGH", "PREDICTED_HIGH"),
    "T2_FUTURE_STRONG": ("IDENTITY_EXACT_FUTURE_STRONG", "PREDICTED_STRONG"),
    "T3_SECOND_RING_AMBER": ("IDENTITY_EXACT_SECOND_RING_AMBER", "PREDICTED_AMBER"),
    "T4_NARROW_APPENDIX": ("IDENTITY_EXACT_NARROW_APPENDIX", "NARROW_LOOKUP_ONLY"),
}


def execution_route(legacy: dict[str, object]) -> tuple[str, str]:
    status = str(legacy["factor_gate_status"])
    separated = "VISIBLE_SLOT_SEPARATED_CHAIN" in str(legacy["mechanism_flags"])
    inherited = "INHERITED_HEAD_CLOSE" in str(legacy["mechanism_flags"])
    blocked = LEGACY.split_rules(str(legacy["blocked_factor_rules"]))
    if status == "FACTOR_GREEN_CROSS_PAGE":
        if separated:
            return "EXECUTE_VISIBLE_SLOT_CHAIN_GREEN", "READ"
        if inherited:
            return "EXECUTE_INHERITED_HEAD_CLOSE_GREEN", "READ"
        return "EXECUTE_KNOWN_FACTORS_GREEN", "READ"
    if status == "FACTOR_AMBER_LOCAL_APPENDIX":
        if separated:
            return "EXECUTE_VISIBLE_SLOT_CHAIN_AMBER", "READ_AMBER"
        if inherited:
            return "EXECUTE_INHERITED_HEAD_CLOSE_AMBER", "READ_AMBER"
        return "EXECUTE_KNOWN_FACTORS_AMBER", "READ_AMBER"
    return LEGACY.primary_stop_route(blocked).replace("STOP_", "EXECUTION_STOP_", 1), "STOP"


def issue_split_certificate(
    recipe: str,
    incoming_action: str = "NONE",
    incoming_argument: str = "NONE",
    scope_incoming_action: str | None = None,
    next_recipe: str = "NONE",
    precomputed_gate: dict[str, str] | None = None,
) -> dict[str, object]:
    legacy = LEGACY.issue_certificate(
        recipe,
        incoming_action,
        incoming_argument,
        scope_incoming_action,
        next_recipe,
        precomputed_gate,
    )
    tier = str(legacy["catalog_intake_tier"])
    identity_route, identity_status = TIER_IDENTITY.get(
        tier,
        ("IDENTITY_NEW_VISIBLE_RECIPE", "NOT_IN_EXACT_CATALOG"),
    )
    execute_route, decision = execution_route(legacy)
    explicit_actions = [] if legacy["explicit_action_roots"] == "NONE" else str(legacy["explicit_action_roots"]).split("|")
    explicit_arguments = [] if legacy["explicit_argument_roots"] == "NONE" else str(legacy["explicit_argument_roots"]).split("|")
    if decision == "STOP":
        outgoing_action = str(legacy["incoming_action"])
        outgoing_argument = str(legacy["incoming_argument"])
    else:
        outgoing_action = explicit_actions[-1] if explicit_actions else str(legacy["incoming_action"])
        outgoing_argument = explicit_arguments[-1] if explicit_arguments else str(legacy["incoming_argument"])
    old_decision = str(legacy["certificate_decision"])
    old_route = str(legacy["primary_intake_route"])
    correction = "NONE"
    if old_decision != decision:
        correction = f"GDT445_{old_decision}_TO_{decision}"
    elif old_route == "EXACT_CATALOG":
        correction = "SPLIT_EXACT_IDENTITY_FROM_FACTOR_EXECUTION"
    return {
        **legacy,
        "identity_route": identity_route,
        "identity_status": identity_status,
        "execution_route": execute_route,
        "execution_decision": decision,
        "identity_only_when_execution_stops": "YES" if legacy["exact_catalog_key"] == "YES" and decision == "STOP" else "NO",
        "outgoing_action_v2": outgoing_action,
        "outgoing_argument_v2": outgoing_argument,
        "execution_stop_preserves_state": "YES" if decision != "STOP" or (
            outgoing_action == legacy["incoming_action"]
            and outgoing_argument == legacy["incoming_argument"]
        ) else "NO",
        "identity_does_not_override_execution": "YES",
        "legacy_gdt445_route": old_route,
        "legacy_gdt445_decision": old_decision,
        "gdt445_correction": correction,
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
    certificate = issue_split_certificate(
        args.recipe,
        args.incoming_action,
        args.incoming_argument,
        scope,
        args.next_recipe,
    )
    print(json.dumps(certificate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
