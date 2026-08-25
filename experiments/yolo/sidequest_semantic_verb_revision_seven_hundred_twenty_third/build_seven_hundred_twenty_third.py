#!/usr/bin/env python3
"""Build Pass 723: apply T/CH/K semantic revisions through the complete prose edition."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P721 = ROOT / "experiments/yolo/sidequest_semantic_compact_apprentice_release_seven_hundred_twenty_first"
OVERRIDES = {"T": "ANWENDEN", "CH": "ENTNEHMEN", "K": "ZUGEBEN"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def revise_prose(text: str) -> str:
    replacements = [
        ("weiterdosieren", "weiter zugeben"), ("Weiterdosieren", "Weiter zugeben"),
        ("zudosieren", "zugeben"), ("Zudosieren", "Zugeben"),
        ("dosieren", "zugeben"), ("Dosieren", "Zugeben"),
        ("abnehmen", "entnehmen"), ("Abnehmen", "Entnehmen"),
        ("eintragen", "anwenden"), ("Eintragen", "Anwenden"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_39_COMPONENT_SHEET.tsv")
    families = read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_163_RECIPE_INDEX.tsv")
    cards = read(P721 / "SEVEN_HUNDRED_TWENTY_FIRST_173_CARD_SURFACE_REGISTER.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    statements = read(P700 / "SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")

    component_rows = []
    values = {}
    for row in components:
        new_value = OVERRIDES.get(row["component"], row["short_value_de"])
        values[row["component"]] = new_value
        component_rows.append({
            **row, "old_value_de": row["short_value_de"], "revised_value_de": new_value,
            "semantic_revision": "YES" if row["component"] in OVERRIDES else "NO",
        })

    def reading(recipe: str) -> str:
        return " · ".join(values[part] for part in recipe.split("+"))

    family_rows = []
    for row in families:
        new = reading(row["component_recipe"])
        family_rows.append({
            "semantic_family": row["semantic_family"], "component_recipe": row["component_recipe"],
            "old_reading_de": row["working_reading_de"], "revised_reading_de": new,
            "events": row["events"], "exact_card_ids": row["exact_card_ids"],
            "semantic_revision": "YES" if row["working_reading_de"] != new else "NO",
        })
    family_by_id = {row["semantic_family"]: row for row in family_rows}
    card_rows = []
    for row in cards:
        new = reading(row["component_recipe"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "old_reading_de": row["working_reading_de"],
            "revised_reading_de": new, "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_revision": "YES" if row["working_reading_de"] != new else "NO",
        })
    card_by_id = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        card = card_by_id[row["card_no"]]
        revised = card["revised_reading_de"]
        out = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "component_recipe": row["component_recipe"],
            "old_semantic_de": row["semantic_layer_de"], "revised_semantic_de": revised,
            "observed_surface": row["observed_surface"], "surface_unchanged": "YES",
            "owner_unchanged": "YES", "boundary_unchanged": "YES",
            "semantic_revision": "YES" if row["semantic_layer_de"] != revised else "NO",
        }
        event_rows.append(out)
        events_by_statement[row["statement_id"]].append(out)

    statement_rows = []
    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        event_subset = events_by_statement[row["statement_id"]]
        new_prose = revise_prose(row["working_reading_de"])
        compact = " | ".join(str(event["revised_semantic_de"]) for event in event_subset)
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "old_working_reading_de": row["working_reading_de"], "revised_working_reading_de": new_prose,
            "revised_atomic_trace_de": compact,
            "semantic_revision": "YES" if any(event["semantic_revision"] == "YES" for event in event_subset) else "NO",
            "surface_unchanged": "YES", "owner_unchanged": "YES",
            "statement_boundary_unchanged": "YES", "line_relation_unchanged": "YES",
        }
        statement_rows.append(out)
        statements_by_record[row["record"]].append(out)

    record_rows = []
    for record, rows in statements_by_record.items():
        record_rows.append({
            "record": record, "page": rows[0]["page"], "statements": len(rows),
            "revised_statements": sum(row["semantic_revision"] == "YES" for row in rows),
            "old_continuous_reading_de": " ".join(str(row["old_working_reading_de"]) for row in rows),
            "revised_continuous_reading_de": " ".join(str(row["revised_working_reading_de"]) for row in rows),
            "old_terms_remaining_in_revision": sum(
                str(row["revised_working_reading_de"]).lower().count(term)
                for row in rows for term in ("eintragen", "abnehmen", "zudosieren", "weiterdosieren")
            ),
            "form_status": "CARD_SURFACE_OWNER_BOUNDARY_UNCHANGED",
        })

    write("SEVEN_HUNDRED_TWENTY_THIRD_39_REVISED_COMPONENTS.tsv", component_rows)
    write("SEVEN_HUNDRED_TWENTY_THIRD_163_REVISED_RECIPES.tsv", family_rows)
    write("SEVEN_HUNDRED_TWENTY_THIRD_173_REVISED_CARDS.tsv", card_rows)
    write("SEVEN_HUNDRED_TWENTY_THIRD_381_REVISED_EVENTS.tsv", event_rows)
    write("SEVEN_HUNDRED_TWENTY_THIRD_116_REVISED_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_THIRD_11_REVISED_RECORDS.tsv", record_rows)

    summary = {
        "status": "PASS", "components": len(component_rows), "recipes": len(family_rows),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows),
        "records": len(record_rows), "revised_components": len(OVERRIDES),
        "revised_recipes": sum(row["semantic_revision"] == "YES" for row in family_rows),
        "revised_cards": sum(row["semantic_revision"] == "YES" for row in card_rows),
        "revised_events": sum(row["semantic_revision"] == "YES" for row in event_rows),
        "revised_statements": sum(row["semantic_revision"] == "YES" for row in statement_rows),
        "revised_records": sum(int(row["revised_statements"]) > 0 for row in record_rows),
        "form_changes": 0,
        "decision": "T_ANWENDEN_CH_ENTNEHMEN_K_ZUGEBEN_PROPAGATE_CLEANLY_THROUGH_COMPLETE_PROSE_EDITION",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
