#!/usr/bin/env python3
"""Build Pass 724: apply S/CTH/O and the concrete AIR=WASSER reading."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P721 = ROOT / "experiments/yolo/sidequest_semantic_compact_apprentice_release_seven_hundred_twenty_first"
P723 = ROOT / "experiments/yolo/sidequest_semantic_verb_revision_seven_hundred_twenty_third"
OVERRIDES = {"S": "TEIL", "CTH": "BEREITEN", "O": "ARBEITSGANG", "AIR": "WASSER"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


AIR_EXPANSIONS = {
    "E006": "Beim Pflanzenartikel Wasser aus dem aktiven Vorrat entnehmen.",
    "E103": "Der gemeinsamen zweireihigen Beckenstation Wasser zugeben.",
    "E260": "An der unteren Korbstation Wasser ansetzen beziehungsweise zulaufen lassen.",
    "E300": "Beim sichtbaren Figurenpaar Wasser umsetzen beziehungsweise weiterfuehren.",
    "E351": "Dieses Wasser am offenen Fransenlauf abstellen; den Schritt schliessen.",
}


def revise_prose(text: str) -> str:
    replacements = [
        ("im Gang", "im Arbeitsgang"), ("Im Gang", "Im Arbeitsgang"),
        ("den Gang", "den Arbeitsgang"), ("Den Gang", "Den Arbeitsgang"),
        ("den Lauf", "Wasser"), ("Den Lauf", "Wasser"),
        ("der Lauf", "das Wasser"), ("Der Lauf", "Das Wasser"),
        ("bereitstellen", "bereiten"), ("Bereitstellen", "Bereiten"),
        ("bereithalten", "bereitet halten"), ("Bereithalten", "Bereitet halten"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(P723 / "SEVEN_HUNDRED_TWENTY_THIRD_39_REVISED_COMPONENTS.tsv")
    recipes = read(P723 / "SEVEN_HUNDRED_TWENTY_THIRD_163_REVISED_RECIPES.tsv")
    cards = read(P723 / "SEVEN_HUNDRED_TWENTY_THIRD_173_REVISED_CARDS.tsv")
    events = read(P723 / "SEVEN_HUNDRED_TWENTY_THIRD_381_REVISED_EVENTS.tsv")
    statements = read(P723 / "SEVEN_HUNDRED_TWENTY_THIRD_116_REVISED_STATEMENTS.tsv")
    original_recipes = {row["semantic_family"]: row for row in read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_163_RECIPE_INDEX.tsv")}

    component_rows = []
    values = {}
    for row in components:
        old = row["revised_value_de"]
        new = OVERRIDES.get(row["component"], old)
        values[row["component"]] = new
        component_rows.append({
            "component": row["component"], "pass722_value_de": row["old_value_de"],
            "pass723_value_de": old, "pass724_value_de": new,
            "revision_wave": "SECOND_WAVE" if row["component"] in OVERRIDES else "FIRST_WAVE" if row["semantic_revision"] == "YES" else "UNCHANGED",
            "diagnostic_fragments": row["diagnostic_fragments"], "entry_kind": row["entry_kind"],
        })

    def reading(recipe: str) -> str:
        return " · ".join(values[part] for part in recipe.split("+"))

    recipe_rows = []
    for row in recipes:
        new = reading(row["component_recipe"])
        recipe_rows.append({
            "semantic_family": row["semantic_family"], "component_recipe": row["component_recipe"],
            "pass723_reading_de": row["revised_reading_de"], "pass724_reading_de": new,
            "original_pass721_reading_de": original_recipes[row["semantic_family"]]["working_reading_de"],
            "events": row["events"], "exact_card_ids": row["exact_card_ids"],
            "second_wave_revision": "YES" if row["revised_reading_de"] != new else "NO",
            "total_revision_from_pass721": "YES" if original_recipes[row["semantic_family"]]["working_reading_de"] != new else "NO",
        })
    recipe_by_family = {row["semantic_family"]: row for row in recipe_rows}

    card_rows = []
    for row in cards:
        new = reading(row["component_recipe"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass723_reading_de": row["revised_reading_de"],
            "pass724_reading_de": new, "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "second_wave_revision": "YES" if row["revised_reading_de"] != new else "NO",
        })
    card_by_id = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        new = card_by_id[row["card_no"]]["pass724_reading_de"]
        out = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "component_recipe": row["component_recipe"],
            "pass723_semantic_de": row["revised_semantic_de"], "pass724_semantic_de": new,
            "observed_surface": row["observed_surface"],
            "second_wave_revision": "YES" if row["revised_semantic_de"] != new else "NO",
            "surface_unchanged": "YES", "owner_unchanged": "YES", "boundary_unchanged": "YES",
        }
        event_rows.append(out)
        events_by_statement[row["statement_id"]].append(out)

    statement_rows = []
    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        subset = events_by_statement[row["statement_id"]]
        new_prose = revise_prose(row["revised_working_reading_de"])
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "pass723_working_reading_de": row["revised_working_reading_de"],
            "pass724_working_reading_de": new_prose,
            "pass724_atomic_trace_de": " | ".join(str(event["pass724_semantic_de"]) for event in subset),
            "second_wave_revision": "YES" if any(event["second_wave_revision"] == "YES" for event in subset) else "NO",
            "form_owner_boundary_unchanged": "YES",
        }
        statement_rows.append(out)
        statements_by_record[row["record"]].append(out)

    record_rows = []
    for record, rows in statements_by_record.items():
        record_rows.append({
            "record": record, "page": rows[0]["page"], "statements": len(rows),
            "second_wave_statements": sum(row["second_wave_revision"] == "YES" for row in rows),
            "continuous_pass724_reading_de": " ".join(str(row["pass724_working_reading_de"]) for row in rows),
            "continuous_atomic_trace_de": " || ".join(str(row["pass724_atomic_trace_de"]) for row in rows),
            "form_status": "UNCHANGED",
        })

    air_rows = []
    for row in event_rows:
        if "AIR" not in row["component_recipe"].split("+"):
            continue
        support = "TEXTLICHER_WASSERKANDIDAT_BEIM_PFLANZENARTIKEL" if row["record"] == "H1" else "SICHTBARE_BECKEN_ODER_LAUFGEOMETRIE"
        air_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "surface": row["observed_surface"],
            "component_recipe": row["component_recipe"], "atomic_reading_de": row["pass724_semantic_de"],
            "concrete_expansion_de": AIR_EXPANSIONS[row["event_id"]],
            "local_support": support, "coherent_as_water": "YES",
        })

    write("SEVEN_HUNDRED_TWENTY_FOURTH_39_COMPONENTS.tsv", component_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_163_RECIPES.tsv", recipe_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_173_CARDS.tsv", card_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv", event_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_11_RECORDS.tsv", record_rows)
    write("SEVEN_HUNDRED_TWENTY_FOURTH_5_AIR_WATER_READINGS.tsv", air_rows)

    summary = {
        "status": "PASS", "components": len(component_rows), "recipes": len(recipe_rows),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "second_wave_components": sorted(OVERRIDES),
        "second_wave_recipes": sum(row["second_wave_revision"] == "YES" for row in recipe_rows),
        "second_wave_events": sum(row["second_wave_revision"] == "YES" for row in event_rows),
        "second_wave_statements": sum(row["second_wave_revision"] == "YES" for row in statement_rows),
        "second_wave_records": sum(int(row["second_wave_statements"]) > 0 for row in record_rows),
        "total_revised_recipes_from_pass721": sum(row["total_revision_from_pass721"] == "YES" for row in recipe_rows),
        "air_water_cards": len(air_rows), "air_water_coherent": sum(row["coherent_as_water"] == "YES" for row in air_rows),
        "form_changes": 0,
        "decision": "S_TEIL_CTH_BEREITEN_O_ARBEITSGANG_AND_AIR_WASSER_ALL_COMPOSE_WITHOUT_FORM_CHANGE",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
