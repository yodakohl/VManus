#!/usr/bin/env python3
"""Preserve relation-before-argument order in inherited-action clauses."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
COMPILER_PATH = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/src/run.py"
SAFE_RENDERER_PATH = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/src/run.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPILER = load_module("gdt416_compiler_for_order", COMPILER_PATH)
SAFE_BUILDER = load_module("gdt434_builder_for_order", SAFE_RENDERER_PATH)
SAFE_RENDERER = SAFE_BUILDER.load_renderer()


def relation_precedes_argument(atoms: list[str]) -> bool:
    argument_positions = [index for index, atom in enumerate(atoms) if atom in COMPILER.ARGUMENT_ROOTS]
    relation_positions = [index for index, atom in enumerate(atoms) if atom in COMPILER.RELATION_ROOTS]
    return bool(argument_positions and relation_positions and min(relation_positions) < min(argument_positions))


def render_ordered_clause(
    register: str,
    atoms: list[str],
    explicit_actions: list[str],
    inherited_action: str,
    inherited_argument: str,
) -> tuple[str, str]:
    baseline = COMPILER.render_clause(register, atoms, explicit_actions, inherited_action, inherited_argument)
    if explicit_actions or not relation_precedes_argument(atoms):
        return baseline, "BASELINE_ORDER_ALREADY_SAFE"

    if not inherited_action:
        # With no active verb this is a reference card; GDT431's renderer
        # already preserves whether the route or the item was written first.
        phrase = SAFE_BUILDER.safe_render(SAFE_RENDERER, atoms, register)
        orders = [COMPILER.ORDER[atom] for atom in atoms if atom in COMPILER.ORDER]
        if orders:
            prefix = COMPILER.coordinated(orders).capitalize() + ": "
            if phrase.startswith(prefix):
                rest = phrase[len(prefix):]
                phrase = COMPILER.coordinated(orders).capitalize() + ", " + rest[0].lower() + rest[1:]
        return phrase, "REFERENCE_RELATION_BEFORE_ARGUMENT"

    relations = COMPILER.scoped_phrases(atoms, COMPILER.RELATIONS[register])
    relation_phrase = COMPILER.coordinated(relations)
    orders = [COMPILER.ORDER[atom] for atom in atoms if atom in COMPILER.ORDER]
    core = baseline
    if orders:
        order_prefix = COMPILER.coordinated(orders).capitalize() + " "
        if not core.startswith(order_prefix):
            raise RuntimeError(f"Cannot isolate order prefix in {baseline!r}")
        core = core[len(order_prefix):]
    needle = "; " + relation_phrase
    if needle not in core:
        raise RuntimeError(f"Cannot isolate relation segment {relation_phrase!r} in {baseline!r}")
    core = core.replace(needle, "", 1)
    relation_first = relation_phrase[0].upper() + relation_phrase[1:] + ": " + core[0].lower() + core[1:]
    if orders:
        relation_first = COMPILER.coordinated(orders).capitalize() + ", " + relation_first[0].lower() + relation_first[1:]
    return relation_first, "INHERITED_ACTION_RELATION_BEFORE_ARGUMENT"
