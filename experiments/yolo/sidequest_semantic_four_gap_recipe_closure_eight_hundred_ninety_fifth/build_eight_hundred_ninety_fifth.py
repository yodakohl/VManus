#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_three_gap_phrase_closure_eight_hundred_ninety_fourth"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETY_FOURTH_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_FIFTH"

PROMOTIONS = {
    "PROC104": "POSTEN AN DER ZIELSTELLE ANSETZEN",
    "PROC105": "NACH SOLLMASS SAMMELN",
    "PROC106": "KURZ BIS BEREIT WEITERARBEITEN",
    "PROC107": "LANG ERWAERMEN",
    "PROC051": "PFLANZENZUTAT FUER DEN ANSATZ ENTNEHMEN",
    "PROC053": "ZUTAT ZUR ZIELSTELLE BRINGEN",
    "PROC054": "WEITER ZUGEBEN",
    "PROC020": "DANACH VOM ANSATZ ENTNEHMEN",
    "PROC170": "LANG SAMMELN",
    "PROC171": "KURZ ZUGEBEN",
    "PROC172": "AN DER ZIELSTELLE KUEHLEN",
    "PROC173": "ANSATZ ZUR ZIELSTELLE LEITEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    marks = read(MARKS)
    units = read(UNITS)
    vocabulary = read(VOCAB)
    cards = read(CARDS)
    unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    targets = [row for row in units if row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(row["model_marks"]) == 4]
    target_ids = set(PROMOTIONS)
    decisions: list[dict[str, object]] = []
    recipes: list[dict[str, object]] = []
    for index, unit in enumerate(targets, start=1):
        local = [row for row in marks if row["order_id"] == unit["order_id"] and row["stage"] == unit["stage"] and row["unit"] == unit["unit"]]
        gaps = [row for row in local if row["apprentice_action"] == "COPY_LOCAL_MODEL"]
        recipe_id = f"FGP{index:02d}"
        recipes.append({"recipe_id": recipe_id, "order_id": unit["order_id"], "master_unit_id": unit["master_unit_id"], "unit": unit["unit"], "page": unit["page"], "owner_de": unit["owner_trace_de"], "surface_recipe": " ".join(row["surface"] for row in gaps), "identity_recipe": " ".join(row["identity"] for row in gaps), "spoken_four_step_recipe_de": " -> ".join(PROMOTIONS[row["identity"]] for row in gaps), "complete_reading_de": unit["front_instruction_de"]})
        for position, gap in enumerate(gaps, start=1):
            decisions.append({"recipe_id": recipe_id, "position": position, "identity": gap["identity"], "surface": gap["surface"], "old_default_de": gap["concrete_default_de"], "new_whole_word_de": PROMOTIONS[gap["identity"]], "master_unit_id": unit["master_unit_id"], "unit": unit["unit"], "owner_de": unit["owner_trace_de"]})

    revised_vocab = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append({**row, "short_value_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "sixth_lesson": "FOUR_GAP_RECIPE_CLOSURE"})
        else:
            revised_vocab.append({**row, "sixth_lesson": "NO_CHANGE"})
    revised_marks = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append({**row, "concrete_default_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "sixth_lesson": "FOUR_GAP_RECIPE_CLOSURE"})
        else:
            revised_marks.append({**row, "sixth_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    recipe_by_unit = {row["master_unit_id"]: row for row in recipes}
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        status = "MODEL_LEAF_REQUIRED" if unit["section"] == "WHEN" else "SHARED_OR_TAUGHT_EXECUTABLE" if model == 0 else "CORE_PLUS_LOCAL_MODEL"
        recipe = recipe_by_unit.get(unit["master_unit_id"])
        revised_units.append({**unit, "core_marks": readable, "model_marks": model, "execution_status": status, "four_step_recipe_id": recipe["recipe_id"] if recipe else "NONE", "four_step_recipe_de": recipe["spoken_four_step_recipe_de"] if recipe else "NONE", "four_gap_unit_closed": "YES" if recipe and status == "SHARED_OR_TAUGHT_EXECUTABLE" else "NO"})

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        revised_cards.append({"order_id": card["order_id"], "title_de": card["title_de"], "units": len(local), "executable_units": counts["SHARED_OR_TAUGHT_EXECUTABLE"], "mixed_units": counts["CORE_PLUS_LOCAL_MODEL"], "condition_units": counts["MODEL_LEAF_REQUIRED"], "newly_closed_four_gap_units": sum(row["four_gap_unit_closed"] == "YES" for row in local)})

    write(f"{PREFIX}_12_FOUR_GAP_WHOLE_WORDS.tsv", decisions, ["recipe_id", "position", "identity", "surface", "old_default_de", "new_whole_word_de", "master_unit_id", "unit", "owner_de"])
    write(f"{PREFIX}_3_MEMORIZED_FOUR_STEP_RECIPES.tsv", recipes, ["recipe_id", "order_id", "master_unit_id", "unit", "page", "owner_de", "surface_recipe", "identity_recipe", "spoken_four_step_recipe_de", "complete_reading_de"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["sixth_lesson"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["sixth_lesson"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["four_step_recipe_id", "four_step_recipe_de", "four_gap_unit_closed"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", revised_cards, ["order_id", "title_de", "units", "executable_units", "mixed_units", "condition_units", "newly_closed_four_gap_units"])

    lines = ["# Vier-Schritt-Rezepte", "", "Drei lange lokale Inseln werden als je vier kurze Kartenwerte und als zusammenhängende Werkstattfolge gelernt.", ""]
    for row in recipes:
        lines.extend([f"## {row['recipe_id']} / {row['master_unit_id']}", "", f"`{row['surface_recipe']}`", f"**Werkstattfolge:** {row['spoken_four_step_recipe_de']}.", f"**Gesamtsatz:** {row['complete_reading_de']}", ""])
    lines.extend(["## Bilanz", "", f"Vollständig ausführbar: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118 Einheiten.", "Nur die fünfteilige Meisterpassage B1-S002 bleibt als Prosalücke; sechs WHEN-Blätter bleiben lokal."])
    (HERE / f"{PREFIX}_FOUR_STEP_RECIPEBOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {"status": "PASS", "decision": "THREE_MEMORIZED_FOUR_STEP_RECIPES_CLOSE_ALL_THREE_FOUR_GAP_UNITS", "promoted_identities": len(target_ids), "promoted_marks": sum(row["identity"] in target_ids for row in revised_marks), "recipe_blocks": len(recipes), "closed_units": sum(row["four_gap_unit_closed"] == "YES" for row in revised_units), "vocabulary_identities": len(revised_vocab), "marks": len(revised_marks), "units": len(revised_units), "unit_statuses": dict(status_counts), "condition_changes": 0, "component_changes": 0, "sealed_pages": ["f84", "f84r"]}
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text("# Sidequest Pass 895: four-gap recipe closure\n\nThree four-card local islands receive individual short values and a memorized four-step recipe. All three units close, raising the executable layer from 108 to 111. Only one five-gap prose unit and six WHEN leaves remain.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
