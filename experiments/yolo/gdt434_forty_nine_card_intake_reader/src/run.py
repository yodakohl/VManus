#!/usr/bin/env python3
"""Build one executable intake catalog from observed, future, and narrow recipes."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
PREDICTIONS = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_293_absent_multi_neighbor_predictions.tsv"
FIRST_CARDS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_47_strong_prediction_phrasebook.tsv"
FIRST_EXPANSIONS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_235_register_expansion_cards.tsv"
SECOND_TARGETS = ROOT / "experiments/yolo/gdt433_two_arm_second_ring_prediction_squares/artifacts/gdt433_14_second_ring_targets.tsv"
SECOND_EXPANSIONS = ROOT / "experiments/yolo/gdt433_two_arm_second_ring_prediction_squares/artifacts/gdt433_10_new_second_ring_register_cards.tsv"
RENDERER = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/src/run.py"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_renderer():
    spec = importlib.util.spec_from_file_location("gdt431_renderer", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT431 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_render(renderer, atoms: list[str], register: str = "GENERIC") -> str:
    arguments = [atom for atom in atoms if atom in renderer.ARGUMENT_ROOTS]
    actions = [atom for atom in atoms if atom in renderer.ACTION_ROOTS]
    if not actions and len(arguments) == 2 and arguments[0] == arguments[1]:
        objects = renderer.GENERIC_OBJECTS if register == "GENERIC" else renderer.REGISTER_OBJECTS[register]
        noun = renderer.strip_article(objects[arguments[0]])
        outer, inner = ("Äußere", "innere") if arguments[0] == "OR" else ("Äußerer", "innerer")
        return f"{outer} {noun}; {inner} {noun}."
    return renderer.render_recipe(atoms, register)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    predictions = read_tsv(PREDICTIONS)
    first_cards = read_tsv(FIRST_CARDS)
    first_expansions = read_tsv(FIRST_EXPANSIONS)
    second_targets = read_tsv(SECOND_TARGETS)
    second_expansions = read_tsv(SECOND_EXPANSIONS)
    components = read_tsv(COMPONENTS)
    renderer = load_renderer()
    meanings = {row["atom"]: row["working_value_de"] for row in components}

    observed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        observed[row["component_recipe"]].append(row)
    first_map = {row["candidate_recipe"]: row for row in first_cards}
    second_selected = {row["target_recipe"]: row for row in second_targets if row["decision"] == "SECOND_RING_AMBER_NEW"}
    narrow = {row["candidate_recipe"]: row for row in predictions if row["prediction_rank"] == "AMBER_NARROW"}

    catalog_rows: list[dict[str, object]] = []
    for recipe, rows in sorted(observed.items()):
        first = sorted(rows, key=lambda row: row["global_running_event_id"])[0]
        catalog_rows.append({
            "component_recipe": recipe,
            "intake_tier": "T0_EXACT_OBSERVED",
            "tier_priority": 0,
            "literal_reading_de": " · ".join(meanings[atom] for atom in recipe.split("+")),
            "generic_workshop_phrase_de": safe_render(renderer, recipe.split("+")),
            "support_count": len(rows),
            "support_kind": "OBSERVED_EVENT_COUNT",
            "registers": "|".join(sorted({row["register"] for row in rows})),
            "sample_surface": first["surface"],
            "sample_existing_clause_de": first["imperative_clause_de"],
            "intake_action": "READ_WITH_EXISTING_RECIPE",
            "surface_rule": "EXACT_VISIBLE_COMPONENT_RECIPE_REQUIRED",
        })
    for recipe, row in sorted(first_map.items()):
        tier = "T1_FUTURE_HIGH" if row["prediction_rank"] == "AMBER_HIGH_PRIORITY" else "T2_FUTURE_STRONG"
        catalog_rows.append({
            "component_recipe": recipe,
            "intake_tier": tier,
            "tier_priority": 1 if tier == "T1_FUTURE_HIGH" else 2,
            "literal_reading_de": row["fixed_literal_reading_de"],
            "generic_workshop_phrase_de": row["short_workshop_phrase_de"],
            "support_count": row["source_neighbor_count"],
            "support_kind": "DISTINCT_OBSERVED_ONE_ROOT_NEIGHBORS",
            "registers": "SOURCE_SECTION_T|HERBAL|BIOLOGICAL|CELESTIAL|PHARMA",
            "sample_surface": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "sample_existing_clause_de": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "intake_action": "READ_WITH_MAIN_FUTURE_CARD",
            "surface_rule": row["surface_rule"],
        })
    for recipe, row in sorted(second_selected.items()):
        catalog_rows.append({
            "component_recipe": recipe,
            "intake_tier": "T3_SECOND_RING_AMBER",
            "tier_priority": 3,
            "literal_reading_de": row["target_literal_de"],
            "generic_workshop_phrase_de": row["target_workshop_phrase_de"],
            "support_count": row["distinct_observed_base_count"],
            "support_kind": "OBSERVED_BASES_WITH_FOUR_STRONG_ARMS",
            "registers": "SOURCE_SECTION_T|HERBAL|BIOLOGICAL|CELESTIAL|PHARMA",
            "sample_surface": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "sample_existing_clause_de": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "intake_action": "READ_WITH_SECOND_RING_AMBER_CARD",
            "surface_rule": row["surface_rule"],
        })
    for recipe, row in sorted(narrow.items()):
        catalog_rows.append({
            "component_recipe": recipe,
            "intake_tier": "T4_NARROW_APPENDIX",
            "tier_priority": 4,
            "literal_reading_de": row["fixed_reading_de"],
            "generic_workshop_phrase_de": safe_render(renderer, recipe.split("+")),
            "support_count": row["source_neighbor_count"],
            "support_kind": "TWO_DISTINCT_OBSERVED_ONE_ROOT_NEIGHBORS",
            "registers": "SOURCE_SECTION_T|HERBAL|BIOLOGICAL|CELESTIAL|PHARMA",
            "sample_surface": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "sample_existing_clause_de": "NONE__PROSPECTIVE_COMPONENT_RECIPE",
            "intake_action": "LOOKUP_ONLY__DO_NOT_AUTO_ACCEPT",
            "surface_rule": row["surface_rule"],
        })
    catalog_rows.sort(key=lambda row: (int(row["tier_priority"]), str(row["component_recipe"])))
    write_tsv(OUT / "gdt434_1563_recipe_intake_catalog.tsv", catalog_rows, list(catalog_rows[0]))

    main_register_rows: list[dict[str, object]] = []
    for row in first_expansions:
        main_register_rows.append({
            "component_recipe": row["candidate_recipe"],
            "intake_tier": "T1_FUTURE_HIGH" if first_map[row["candidate_recipe"]]["prediction_rank"] == "AMBER_HIGH_PRIORITY" else "T2_FUTURE_STRONG",
            "register": row["register"],
            "literal_reading_de": row["portable_literal_de"],
            "owner_local_atom_expansion_de": row["owner_local_atom_expansion_de"],
            "owner_local_workshop_phrase_de": row["owner_local_workshop_phrase_de"],
            "surface_rule": row["surface_rule"],
        })
    for row in second_expansions:
        main_register_rows.append({
            "component_recipe": row["target_recipe"],
            "intake_tier": "T3_SECOND_RING_AMBER",
            "register": row["register"],
            "literal_reading_de": row["portable_literal_de"],
            "owner_local_atom_expansion_de": row["owner_local_atom_expansion_de"],
            "owner_local_workshop_phrase_de": row["owner_local_workshop_phrase_de"],
            "surface_rule": row["surface_rule"],
        })
    main_register_rows.sort(key=lambda row: (str(row["intake_tier"]), str(row["component_recipe"]), str(row["register"])))
    write_tsv(OUT / "gdt434_245_main_card_register_readings.tsv", main_register_rows, list(main_register_rows[0]))

    phrase_groups: dict[str, list[str]] = defaultdict(list)
    for recipe, row in narrow.items():
        phrase_groups[safe_render(renderer, recipe.split("+"))].append(recipe)
    narrow_rows: list[dict[str, object]] = []
    for recipe, row in sorted(narrow.items()):
        phrase = safe_render(renderer, recipe.split("+"))
        collision_recipes = sorted(phrase_groups[phrase])
        narrow_rows.append({
            "component_recipe": recipe,
            "literal_reading_de": row["fixed_reading_de"],
            "generic_workshop_phrase_de": phrase,
            "source_neighbor_count": row["source_neighbor_count"],
            "source_recipes": row["source_recipes"],
            "generic_phrase_collision_count": len(collision_recipes) - 1,
            "generic_phrase_collision_recipes": "|".join(collision_recipes) if len(collision_recipes) > 1 else "NONE",
            "appendix_rule": "EXACT_RECIPE_KEY_REQUIRED__PHRASE_ALONE_NEVER_MATCHES",
            "surface_rule": row["surface_rule"],
        })
    write_tsv(OUT / "gdt434_246_narrow_lookup_appendix.tsv", narrow_rows, list(narrow_rows[0]))

    test_rows = [
        {"test_id": "M01", "component_recipe": "CHD+Y", "register": "HERBAL", "expected_tier": "T0_EXACT_OBSERVED"},
        {"test_id": "M02", "component_recipe": "AL+AIN", "register": "BIOLOGICAL", "expected_tier": "T1_FUTURE_HIGH"},
        {"test_id": "M03", "component_recipe": "P+AL", "register": "PHARMA", "expected_tier": "T2_FUTURE_STRONG"},
        {"test_id": "M04", "component_recipe": "AIR+AIN", "register": "CELESTIAL", "expected_tier": "T3_SECOND_RING_AMBER"},
        {"test_id": "M05", "component_recipe": "P+L", "register": "HERBAL", "expected_tier": "T3_SECOND_RING_AMBER"},
        {"test_id": "M06", "component_recipe": "AIR+OR", "register": "BIOLOGICAL", "expected_tier": "T4_NARROW_APPENDIX"},
        {"test_id": "M07", "component_recipe": "AIIN+AIN+S+Y", "register": "HERBAL", "expected_tier": "T5_NO_LICENSED_RECIPE"},
        {"test_id": "M08", "component_recipe": "CH+CH+CH", "register": "PHARMA", "expected_tier": "T5_NO_LICENSED_RECIPE"},
    ]
    write_tsv(OUT / "gdt434_8_matcher_test_cases.tsv", test_rows, list(test_rows[0]))

    main_cards = [row for row in catalog_rows if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}]
    sheet = [
        "# 49-Karten-Aufnahmeblatt", "",
        "Abgleich immer über die exakt sichtbare Komponentenfolge, nie über eine ähnlich klingende deutsche Phrase.", "",
        "## Rangfolge", "",
        "1. T0: bereits beobachtetes exaktes Rezept.",
        "2. T1/T2: vier hohe und 43 starke Zukunftskarten.",
        "3. T3: zwei schwächere Amber-II-Karten.",
        "4. T4: 246 schmale Nachschlagekarten, niemals automatisch annehmen.",
        "5. T5: kein Treffer; keine Lesung erfinden.", "",
        "## Hauptdeck", "",
    ]
    for row in main_cards:
        sheet.append(f"- `{row['component_recipe']}` — **{row['generic_workshop_phrase_de']}** ({row['intake_tier']})")
    sheet += ["", "Oberflächenformen werden nicht aus diesen Rezepten erzeugt.", ""]
    (OUT / "FORTY_NINE_CARD_INTAKE_SHEET.md").write_text("\n".join(sheet), encoding="utf-8")

    tier_counts = Counter(str(row["intake_tier"]) for row in catalog_rows)
    result = {
        "status": "EXECUTABLE_49_CARD_INTAKE_READER_WITH_SEPARATE_NARROW_APPENDIX",
        "catalog_recipe_count": len(catalog_rows),
        "tier_counts": dict(sorted(tier_counts.items())),
        "main_future_card_count": len(main_cards),
        "main_register_reading_count": len(main_register_rows),
        "narrow_appendix_count": len(narrow_rows),
        "narrow_generic_phrase_collision_recipe_count": sum(row["generic_phrase_collision_count"] != 0 for row in narrow_rows),
        "matcher_test_count": len(test_rows),
        "surface_predictions": 0,
        "new_component_values": 0,
        "new_pages": 0,
    }
    (OUT / "gdt434_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
