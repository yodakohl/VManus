#!/usr/bin/env python3
"""Issue one bounded intake certificate for a visibly supplied component recipe."""

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
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
STOP_DECK_PATH = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck/artifacts/gdt442_47_stop_rule_deck.tsv"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


READER = load_module("gdt441_reader_for_gdt445_certificate", READER_PATH)
STOP_DECK = {row["blocked_rule"]: row for row in read_tsv(STOP_DECK_PATH)}
RED_DIRECT_PAIRS = {
    rule.removeprefix("PAIR:")
    for rule, row in STOP_DECK.items()
    if row["factor_family"] == "ADJACENT_ACTION_PAIR"
}


def split_rules(value: str) -> list[str]:
    return [] if not value or value == "NONE" else value.split("|")


def visible_separated_chains(atoms: list[str]) -> list[str]:
    """Return only action-focus-action triples literally present in the recipe."""
    found: list[str] = []
    for index in range(len(atoms) - 2):
        left, focus, right = atoms[index:index + 3]
        pair = f"{left}>{right}"
        if (
            left in READER.COMPILER.ACTION_ROOTS
            and focus in READER.FOCUS_ROOTS
            and right in READER.COMPILER.ACTION_ROOTS
            and pair in RED_DIRECT_PAIRS
        ):
            found.append(f"{index + 1}:{left}+{focus}+{right}__DIRECT_{pair}_REMAINS_RED")
    return found


def primary_stop_route(blocked: list[str]) -> str:
    if any(rule.startswith("UNSEEN:") for rule in blocked):
        return "STOP_UNSEEN_ATOM"
    if len(blocked) > 1:
        return "STOP_MULTIPLE_UNLICENSED_FACTORS"
    if blocked and blocked[0].startswith("PAIR:"):
        return "STOP_UNLICENSED_DIRECT_PAIR"
    if blocked and blocked[0].startswith("FOCUS:"):
        return "STOP_UNLICENSED_FOCUS_EDGE"
    if blocked == ["CLOSE:NO_ACTIVE_ACTION"]:
        return "STOP_CLOSE_NEEDS_ACTIVE_HEAD"
    return "STOP_UNLICENSED_FACTOR"


def route_explanation(route: str) -> str:
    explanations = {
        "EXACT_CATALOG": "Bekannten exakten Kartenschluessel lesen; Faktoren bleiben sichtbar.",
        "KNOWN_FACTOR_COMPOSITION_GREEN": "Neue sichtbare Karte nur aus seitenuebergreifend belegten Faktoren lesen.",
        "KNOWN_FACTOR_COMPOSITION_AMBER": "Neue sichtbare Karte mit genau ausgewiesener lokaler Altkante lesen.",
        "INHERITED_HEAD_CLOSE_GREEN": "Sichtbare Schlusskarte mit dem bereits aktiven Handlungskopf lesen.",
        "INHERITED_HEAD_CLOSE_AMBER": "Sichtbare Schlusskarte mit aktivem Kopf und ausgewiesener lokaler Altkante lesen.",
        "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN": "Sichtbarer Fokus trennt zwei Handlungen; das rote Direktpaar bleibt verboten.",
        "VISIBLE_SLOT_SEPARATED_CHAIN_AMBER": "Sichtbarer Fokus trennt zwei Handlungen; eine lokale Altkante bleibt gelb.",
        "STOP_UNSEEN_ATOM": "Mindestens ein sichtbarer Kern fehlt im Lehrdeck; Zustand nicht aendern.",
        "STOP_UNLICENSED_DIRECT_PAIR": "Ein sichtbar direktes Handlungspaar fehlt im Paar-Deck; Zustand nicht aendern.",
        "STOP_UNLICENSED_FOCUS_EDGE": "Eine Kopf-Fokus-Kante fehlt im Deck; Zustand nicht aendern.",
        "STOP_CLOSE_NEEDS_ACTIVE_HEAD": "Schlusskarte besitzt weder sichtbaren noch geerbten Handlungskopf.",
        "STOP_MULTIPLE_UNLICENSED_FACTORS": "Mehrere sichtbare Faktorregeln fehlen; Zustand nicht aendern.",
        "STOP_UNLICENSED_FACTOR": "Mindestens eine sichtbare Faktorregel fehlt; Zustand nicht aendern.",
    }
    return explanations[route]


def issue_certificate(
    recipe: str,
    incoming_action: str = "NONE",
    incoming_argument: str = "NONE",
    scope_incoming_action: str | None = None,
    next_recipe: str = "NONE",
    precomputed_gate: dict[str, str] | None = None,
) -> dict[str, object]:
    recipe = recipe.upper()
    incoming_action = incoming_action.upper()
    incoming_argument = incoming_argument.upper()
    next_recipe = next_recipe.upper()
    if scope_incoming_action is not None:
        scope_incoming_action = scope_incoming_action.upper()
    atoms = recipe.split("+") if recipe else []
    exact = recipe in READER.CATALOG_ROWS
    gate = precomputed_gate or READER.gate_recipe(
        recipe,
        incoming_action,
        next_recipe,
        scope_incoming_action,
    )
    blocked = split_rules(gate["blocked_factor_rules"])
    amber = split_rules(gate["amber_factor_rules"])
    explicit_actions = [atom for atom in atoms if atom in READER.COMPILER.ACTION_ROOTS]
    explicit_arguments = [atom for atom in atoms if atom in READER.COMPILER.ARGUMENT_ROOTS]
    separated = visible_separated_chains(atoms)
    inherited_close = "DY" in atoms and not explicit_actions and incoming_action != "NONE"

    flags: list[str] = []
    if exact:
        flags.append("EXACT_CATALOG_KEY")
    if separated:
        flags.append("VISIBLE_SLOT_SEPARATED_CHAIN")
    if inherited_close:
        flags.append("INHERITED_HEAD_CLOSE")
    if amber:
        flags.append("LOCAL_APPENDIX_EDGE_VISIBLE")
    if blocked:
        flags.append("NAMED_STOP_RULE")
    if not flags:
        flags.append("KNOWN_FACTOR_COMPOSITION")

    if exact:
        route = "EXACT_CATALOG"
        decision = "READ"
    elif gate["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE":
        if separated:
            route = "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN"
        elif inherited_close:
            route = "INHERITED_HEAD_CLOSE_GREEN"
        else:
            route = "KNOWN_FACTOR_COMPOSITION_GREEN"
        decision = "READ"
    elif gate["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX":
        if separated:
            route = "VISIBLE_SLOT_SEPARATED_CHAIN_AMBER"
        elif inherited_close:
            route = "INHERITED_HEAD_CLOSE_AMBER"
        else:
            route = "KNOWN_FACTOR_COMPOSITION_AMBER"
        decision = "READ_AMBER"
    else:
        route = primary_stop_route(blocked)
        decision = "STOP"

    if decision == "STOP":
        outgoing_action = incoming_action
        outgoing_argument = incoming_argument
    else:
        outgoing_action = explicit_actions[-1] if explicit_actions else incoming_action
        outgoing_argument = explicit_arguments[-1] if explicit_arguments else incoming_argument

    explanations = []
    for rule in blocked:
        row = STOP_DECK.get(rule, {})
        explanations.append(
            f"{rule}:{row.get('factor_family', 'OUTSIDE_FIXED_DECK')}:{row.get('instruction', 'STOP')}"
        )
    known_atoms = all(atom in READER.KNOWN_ATOMS for atom in atoms)
    literal = READER.ordered_literal(atoms) if known_atoms else "KEINE LIZENZIERTE KERNFOLGE"
    catalog = READER.CATALOG_ROWS.get(recipe, {})
    if scope_incoming_action is None:
        scope_mode = "AUTO_SAME_AS_OWNER_HEAD"
    elif scope_incoming_action == "NONE":
        scope_mode = "OWNER_SCOPE_RESET"
    else:
        scope_mode = "STATEMENT_SCOPE_INHERITED"

    return {
        "component_recipe": recipe,
        "visible_atom_count": len(atoms),
        "visible_atoms": "|".join(atoms) or "NONE",
        "all_atoms_known": "YES" if known_atoms else "NO",
        "exact_catalog_key": "YES" if exact else "NO",
        "catalog_intake_tier": catalog.get("intake_tier", "NONE"),
        "incoming_action": incoming_action,
        "incoming_argument": incoming_argument,
        "scope_context_mode": scope_mode,
        "scope_incoming_action": "AUTO" if scope_incoming_action is None else scope_incoming_action,
        "next_visible_recipe": next_recipe,
        "explicit_action_roots": "|".join(explicit_actions) or "NONE",
        "explicit_argument_roots": "|".join(explicit_arguments) or "NONE",
        "visible_separated_chains": "|".join(separated) or "NONE",
        "factor_gate_status": gate["factor_gate_status"],
        "scope_selector_rules": gate.get("scope_selector_rules", "NONE"),
        "portable_factor_rules": gate["portable_factor_rules"],
        "amber_factor_rules": gate["amber_factor_rules"],
        "blocked_factor_rules": gate["blocked_factor_rules"],
        "blocked_rule_explanations": "|".join(explanations) or "NONE",
        "mechanism_flags": "|".join(flags),
        "primary_intake_route": route,
        "certificate_decision": decision,
        "route_explanation_de": route_explanation(route),
        "ordered_literal_reading_de": literal,
        "outgoing_action": outgoing_action,
        "outgoing_argument": outgoing_argument,
        "state_preserved_on_stop": "YES" if decision != "STOP" or (outgoing_action == incoming_action and outgoing_argument == incoming_argument) else "NO",
        "direct_pair_promoted": "NO",
        "invisible_separator_invented": "NO",
        "meaning_revision": "NO",
        "surface_prediction": "NO",
        "occurrence_prediction": "NO",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True, help="Visible ordered component recipe")
    parser.add_argument("--incoming-action", default="NONE")
    parser.add_argument("--incoming-argument", default="NONE")
    parser.add_argument(
        "--scope-incoming-action",
        default="AUTO",
        help="AUTO, NONE for owner-scope reset, or an explicit statement-scope action",
    )
    parser.add_argument("--next-recipe", default="NONE")
    args = parser.parse_args()
    scope = None if args.scope_incoming_action.upper() == "AUTO" else args.scope_incoming_action
    certificate = issue_certificate(
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
