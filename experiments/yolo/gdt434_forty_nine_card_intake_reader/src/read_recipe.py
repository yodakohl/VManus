#!/usr/bin/env python3
"""Read one already segmented component recipe through the GDT434 intake deck."""

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
BASE = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader"
OUT = BASE / "artifacts"
CATALOG = OUT / "gdt434_1563_recipe_intake_catalog.tsv"
MAIN_READINGS = OUT / "gdt434_245_main_card_register_readings.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
BUILDER = BASE / "src/run.py"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt434_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT434 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_recipe(raw: str) -> str:
    return "+".join(part.strip().upper() for part in raw.strip().split("+") if part.strip())


def read_recipe(recipe: str, register: str | None) -> dict[str, object]:
    recipe = normalize_recipe(recipe)
    if not recipe:
        return {
            "component_recipe": recipe,
            "register": register or "GENERIC",
            "intake_tier": "T5_NO_LICENSED_RECIPE",
            "match_status": "EMPTY_RECIPE__STOP",
            "reading_de": "Keine Komponentenfolge eingegeben.",
            "instruction_de": "Stoppen; keine Karte und keine Lesung erfinden.",
            "surface_prediction": "NONE",
        }
    if register is not None and register not in REGISTERS:
        raise ValueError(f"Unknown register {register!r}; choose one of {sorted(REGISTERS)}")

    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    meanings = {row["atom"]: row["working_value_de"] for row in read_tsv(COMPONENTS)}
    atoms = recipe.split("+")
    unseen = [atom for atom in atoms if atom not in meanings]
    common = {
        "component_recipe": recipe,
        "register": register or "GENERIC",
        "surface_prediction": "NONE",
    }
    if unseen:
        return {
            **common,
            "intake_tier": "T5_NO_LICENSED_RECIPE",
            "match_status": "UNSEEN_ATOM__STOP",
            "literal_reading_de": " · ".join(meanings.get(atom, f"UNBEKANNTES_ATOM({atom})") for atom in atoms),
            "reading_de": "Keine Lesung.",
            "instruction_de": "Stoppen; zuerst den neuen Atomkern untersuchen.",
            "unseen_atoms": unseen,
        }

    hit = catalog.get(recipe)
    literal = " · ".join(meanings[atom] for atom in atoms)
    if hit is None:
        return {
            **common,
            "intake_tier": "T5_NO_LICENSED_RECIPE",
            "match_status": "KNOWN_ATOMS_BUT_UNLICENSED_RECIPE__STOP",
            "literal_reading_de": literal,
            "reading_de": f"Komponenten bekannt ({literal}), aber diese Zusammensetzung ist keine Karte.",
            "instruction_de": "Nicht als feste Karte lesen; als neue Kombination gesondert prüfen.",
        }

    tier = hit["intake_tier"]
    if tier == "T0_EXACT_OBSERVED":
        clauses = [
            row for row in read_tsv(CLAUSES)
            if row["component_recipe"] == recipe and (register is None or row["register"] == register)
        ]
        if clauses:
            chosen = sorted(clauses, key=lambda row: row["global_running_event_id"])[0]
            return {
                **common,
                "intake_tier": tier,
                "match_status": "EXACT_OBSERVED_REGISTER" if register else "EXACT_OBSERVED_RECIPE",
                "literal_reading_de": hit["literal_reading_de"],
                "reading_de": chosen["imperative_clause_de"],
                "instruction_de": "Bestehendes exaktes Rezept lesen.",
                "observed_event_id": chosen["global_running_event_id"],
                "observed_page": chosen["physical_page"],
                "observed_surface": chosen["surface"],
            }
        builder = load_builder()
        renderer = builder.load_renderer()
        phrase = builder.safe_render(renderer, atoms, register or "GENERIC")
        return {
            **common,
            "intake_tier": tier,
            "match_status": "EXACT_RECIPE__COUNTERFACTUAL_REGISTER_EXPANSION",
            "literal_reading_de": hit["literal_reading_de"],
            "reading_de": phrase,
            "instruction_de": "Rezept ist beobachtet, diese Registerlesung jedoch nicht; nur als lokale Expansion verwenden.",
        }

    if tier in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}:
        if register:
            matches = [
                row for row in read_tsv(MAIN_READINGS)
                if row["component_recipe"] == recipe and row["register"] == register
            ]
            if len(matches) != 1:
                raise RuntimeError(f"Expected one main-card register reading for {recipe}/{register}")
            reading = matches[0]["owner_local_workshop_phrase_de"]
        else:
            reading = hit["generic_workshop_phrase_de"]
        return {
            **common,
            "intake_tier": tier,
            "match_status": "EXACT_MAIN_FUTURE_CARD",
            "literal_reading_de": hit["literal_reading_de"],
            "reading_de": reading,
            "instruction_de": "Als prospektive Hauptkarte lesen; sichtbare Oberfläche bleibt offen.",
        }

    if tier == "T4_NARROW_APPENDIX":
        builder = load_builder()
        renderer = builder.load_renderer()
        reading = builder.safe_render(renderer, atoms, register or "GENERIC")
        return {
            **common,
            "intake_tier": tier,
            "match_status": "NARROW_APPENDIX__EXACT_RECIPE_REQUIRED",
            "literal_reading_de": hit["literal_reading_de"],
            "reading_de": reading,
            "instruction_de": "Nur wegen des exakten Rezeptschlüssels nachschlagen; deutsche Phrase allein ist kein Treffer.",
        }
    raise RuntimeError(f"Unhandled intake tier {tier}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", required=True, help="Exact segmented recipe, for example AL+AIN")
    parser.add_argument("--register", choices=sorted(REGISTERS), help="Optional owner register")
    args = parser.parse_args()
    print(json.dumps(read_recipe(args.recipe, args.register), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
