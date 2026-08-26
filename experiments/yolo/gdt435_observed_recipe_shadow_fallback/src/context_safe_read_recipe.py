#!/usr/bin/env python3
"""Context-safe replacement for the GDT434 recipe intake command."""

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
BASE = ROOT / "experiments/yolo/gdt435_observed_recipe_shadow_fallback"
GDT434 = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader"
CATALOG = GDT434 / "artifacts/gdt434_1563_recipe_intake_catalog.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


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


def context_safe_read(
    recipe: str,
    register: str | None,
    event_id: str | None,
    owner: str | None,
    inherited_action: str | None,
    inherited_argument: str | None,
) -> dict[str, object]:
    old = load_module("gdt434_reader", GDT434 / "src/read_recipe.py")
    recipe = old.normalize_recipe(recipe)
    base_result = old.read_recipe(recipe, register)
    base_result["reader_version"] = "GDT435_CONTEXT_SAFE"
    if base_result["intake_tier"] != "T0_EXACT_OBSERVED":
        return base_result
    # GDT434 selected the first matching observed event. That is precisely the
    # behavior corrected here, so no arbitrary event provenance may leak into
    # a context-free result.
    for key in ("observed_event_id", "observed_page", "observed_surface"):
        base_result.pop(key, None)

    rows = [row for row in read_tsv(CLAUSES) if row["component_recipe"] == recipe]
    if event_id:
        matches = [row for row in rows if row["global_running_event_id"] == event_id]
        if len(matches) != 1:
            raise ValueError(f"Event {event_id!r} is not an observed occurrence of {recipe}")
        row = matches[0]
        if register and row["register"] != register:
            raise ValueError(f"Event {event_id!r} belongs to {row['register']}, not {register}")
        return {
            **base_result,
            "register": row["register"],
            "match_status": "EXACT_OBSERVED_EVENT_CONTEXT",
            "reading_de": row["imperative_clause_de"],
            "instruction_de": "Exakte bekannte Ereignis- und Zustandslesung.",
            "observed_event_id": row["global_running_event_id"],
            "observed_page": row["physical_page"],
            "observed_surface": row["surface"],
            "owner_de": row["owner_de"],
            "inherited_action_root": row["inherited_action_root"],
            "inherited_argument_root": row["inherited_argument_root"],
        }

    complete_state = inherited_action is not None and inherited_argument is not None
    if complete_state and register:
        matches = [
            row for row in rows
            if row["register"] == register
            and row["inherited_action_root"] == inherited_action
            and row["inherited_argument_root"] == inherited_argument
        ]
        clauses = sorted({row["imperative_clause_de"] for row in matches})
        if matches and len(clauses) == 1:
            chosen = sorted(matches, key=lambda row: row["global_running_event_id"])[0]
            return {
                **base_result,
                "match_status": "EXACT_OBSERVED_CONTEXT_STATE",
                "reading_de": clauses[0],
                "instruction_de": "Exakte bekannte Rezept-, Register- und Zustandslesung.",
                "observed_event_id": chosen["global_running_event_id"],
                "owner_de": owner if owner is not None else "NOT_REQUIRED_FOR_CLAUSE_SELECTION",
                "inherited_action_root": inherited_action,
                "inherited_argument_root": inherited_argument,
                "matching_event_count": len(matches),
            }

    scoped = [row for row in rows if register is None or row["register"] == register]
    if not scoped:
        return base_result
    clause_variants = sorted({row["imperative_clause_de"] for row in scoped})
    if len(clause_variants) == 1:
        chosen = sorted(scoped, key=lambda row: row["global_running_event_id"])[0]
        return {
            **base_result,
            "match_status": "EXACT_OBSERVED_SCOPE__CLAUSE_UNIQUE",
            "reading_de": clause_variants[0],
            "instruction_de": "Diese Rezept-/Registergruppe besitzt nur eine bekannte Satzlesung.",
            "observed_event_id": chosen["global_running_event_id"],
            "matching_event_count": len(scoped),
        }

    builder = load_module("gdt434_builder", GDT434 / "src/run.py")
    renderer = builder.load_renderer()
    safe_phrase = builder.safe_render(renderer, recipe.split("+"), register or "GENERIC")
    state_keys = {
        (row["inherited_action_root"], row["inherited_argument_root"])
        for row in scoped
    }
    return {
        **base_result,
        "match_status": "EXACT_OBSERVED_RECIPE__CONTEXT_REQUIRED",
        "reading_de": safe_phrase,
        "instruction_de": "Nur die sichere Kernlesung verwenden; für den ganzen Satz geerbtes Verb und Argument angeben.",
        "available_clause_variant_count": len(clause_variants),
        "available_context_state_count": len(state_keys),
        "required_context_fields": ["inherited_action", "inherited_argument"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True)
    parser.add_argument("--register", choices=sorted(REGISTERS))
    parser.add_argument("--event-id", help="Known event ID for an exact replay")
    parser.add_argument("--owner", help="Optional owner provenance; not needed to choose the sentence")
    parser.add_argument("--inherited-action", help="Inherited action root; pass NONE explicitly when empty")
    parser.add_argument("--inherited-argument", help="Inherited argument root; pass NONE explicitly when empty")
    args = parser.parse_args()
    result = context_safe_read(
        args.recipe,
        args.register,
        args.event_id,
        args.owner,
        args.inherited_action,
        args.inherited_argument,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
