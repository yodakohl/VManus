#!/usr/bin/env python3
"""Validate GDT431's 47-card future reading phrasebook."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook"
OUT = BASE / "artifacts"
SOURCE = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_293_absent_multi_neighbor_predictions.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt431_47_strong_prediction_phrasebook.tsv",
        OUT / "gdt431_235_register_expansion_cards.tsv",
        OUT / "gdt431_145_neighbor_exemplars.tsv",
        OUT / "FORTY_SEVEN_FUTURE_READING_CARDS.md",
        OUT / "gdt431_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    cards = read_tsv(tracked[0])
    expansions = read_tsv(tracked[1])
    neighbors = read_tsv(tracked[2])
    source = [row for row in read_tsv(SOURCE) if row["prediction_rank"] in {"AMBER_HIGH_PRIORITY", "AMBER_STRONG"}]
    components = {row["atom"]: row["working_value_de"] for row in read_tsv(COMPONENTS)}
    observed_recipes = {row["component_recipe"] for row in read_tsv(CLAUSES)}
    source_by_recipe = {row["candidate_recipe"]: row for row in source}
    result = json.loads((OUT / "gdt431_result.json").read_text(encoding="utf-8"))
    registers = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}
    card_ids = {row["candidate_recipe"] for row in cards}
    expansion_counts = Counter(row["candidate_recipe"] for row in expansions)
    neighbor_counts = Counter(row["candidate_recipe"] for row in neighbors)
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "card_rows_47": len(cards) == 47,
        "card_ids_unique": len(card_ids) == 47,
        "source_ids_exact": card_ids == set(source_by_recipe),
        "rank_counts_exact": Counter(row["prediction_rank"] for row in cards) == Counter({"AMBER_HIGH_PRIORITY": 4, "AMBER_STRONG": 43}),
        "ordinals_1_to_47": [int(row["card_ordinal"]) for row in cards] == list(range(1, 48)),
        "literal_readings_frozen": all(row["fixed_literal_reading_de"] == source_by_recipe[row["candidate_recipe"]]["fixed_reading_de"] for row in cards),
        "all_atoms_known": all(atom in components for row in cards for atom in row["candidate_recipe"].split("+")),
        "literal_is_component_exact": all(row["fixed_literal_reading_de"] == " · ".join(components[atom] for atom in row["candidate_recipe"].split("+")) for row in cards),
        "phrases_nonempty": all(row["short_workshop_phrase_de"].strip() for row in cards),
        "generic_phrases_unique": len({row["short_workshop_phrase_de"] for row in cards}) == 47,
        "meaning_status_fixed": all(row["meaning_status"] == "COMPOSITION_OF_FIXED_COMPONENT_VALUES" for row in cards),
        "surface_rule_preserved": all(row["surface_rule"].startswith("DO_NOT_INVENT_SURFACE") for row in cards + expansions),
        "register_rows_235": len(expansions) == 235,
        "five_registers_each": all(expansion_counts[recipe] == 5 for recipe in card_ids),
        "register_set_each": all({row["register"] for row in expansions if row["candidate_recipe"] == recipe} == registers for recipe in card_ids),
        "register_phrases_nonempty": all(row["owner_local_workshop_phrase_de"].strip() and row["owner_local_atom_expansion_de"].strip() for row in expansions),
        "within_register_phrases_unique": len({(row["register"], row["owner_local_workshop_phrase_de"]) for row in expansions}) == 235,
        "neighbor_rows_145": len(neighbors) == 145,
        "neighbor_count_by_card": all(neighbor_counts[recipe] == int(source_by_recipe[recipe]["source_neighbor_count"]) for recipe in card_ids),
        "neighbor_sources_observed": all(row["source_neighbor_recipe"] in observed_recipes for row in neighbors),
        "one_root_difference": all(len(row["source_neighbor_recipe"].split("+")) == len(row["candidate_recipe"].split("+")) and sum(a != b for a, b in zip(row["source_neighbor_recipe"].split("+"), row["candidate_recipe"].split("+"))) == 1 for row in neighbors),
        "neighbor_evidence_positive": all(int(row["source_event_count"]) > 0 and int(row["source_page_count"]) > 0 for row in neighbors),
        "all_neighbor_samples_present": all(row["sample_surface"].strip() and row["sample_existing_imperative_de"].strip() for row in neighbors),
        "result_status": result["status"] == "FORTY_SEVEN_STRONG_PREDICTIONS_HAVE_FIXED_READABLE_PHRASES",
        "result_counts": result["prediction_card_count"] == 47 and result["register_expansion_count"] == 235 and result["neighbor_exemplar_count"] == 145,
        "result_phrase_collisions_zero": result["generic_phrase_collision_count"] == 0 and result["within_register_phrase_collision_count"] == 0,
        "no_surface_predictions": result["surface_predictions"] == 0,
        "no_new_component_values": result["new_component_values"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "no_placeholder_language": all(term not in output_text.upper() for term in ("UNKNOWN", "EXEMPLAR_VALUE", "UNTRANSLATED")),
        "no_forbidden_page": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt431_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
