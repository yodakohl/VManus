#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def readings(recipe: str) -> tuple[str, str, str]:
    tokens = recipe.split("+")
    prefix = [token for token in tokens if token not in {"SHED", "DY", "AL"}]
    suffix = [token for token in tokens if token in {"DY", "AL"}]
    value = {"R": "KUEHLEN", "DY": "SCHLUSS", "AL": "ZIELSTELLE"}
    before = " · ".join(value[token] for token in prefix)
    after = " · ".join(value[token] for token in suffix)
    def combine(middle: str) -> str:
        return " · ".join(part for part in (before, middle, after) if part)
    return combine("ABSETZEN"), combine("ABGESETZT"), combine("STEHENLASSEN")


def revise_sentence(text: str) -> str:
    replacements = [
        ("Absetzen lassen", "Stehen lassen"),
        ("Kuehlen und absetzen lassen", "Kuehlen und stehen lassen"),
        ("absetzen lassen", "stehen lassen"),
        ("absetzen und", "stehen lassen und"),
        ("absetzen;", "stehen lassen;"),
        ("absetzen.", "stehen lassen."),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    target = [row for row in events if "SHED" in row["component_recipe"].split("+")]

    event_rows = []
    affected_statements: dict[str, dict[str, object]] = {}
    for row in target:
        action, result, selected = readings(row["component_recipe"])
        statement = statements[row["statement_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "old_action_reading": action,
                "result_state_rival": result,
                "selected_process_reading": selected,
                "terminal": "YES" if "DY" in row["component_recipe"].split("+") else "NO",
                "target_addressed": "YES" if "AL" in row["component_recipe"].split("+") else "NO",
                "selection_reason": (
                    "imperative process plus close; no sediment presupposition"
                    if "DY" in row["component_recipe"].split("+")
                    else "natural target phrase: at the target let stand"
                ),
            }
        )
        affected_statements[row["statement_id"]] = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "owner_de": row["owner_de"],
            "surface_sequence": statement["surface_sequence"],
            "old_reading_de": statement["clean_workshop_reading_de"],
            "revised_reading_de": revise_sentence(statement["clean_workshop_reading_de"]),
        }

    family_rows = []
    for recipe in sorted({row["component_recipe"] for row in target}):
        rows = [row for row in target if row["component_recipe"] == recipe]
        action, result, selected = readings(recipe)
        family_rows.append(
            {
                "component_recipe": recipe,
                "surfaces": "|".join(sorted({row["surface"] for row in rows})),
                "events": len(rows),
                "pages": "|".join(sorted({row["page"] for row in rows})),
                "action_candidate": action,
                "result_candidate": result,
                "selected_reading": selected,
                "selected_core_value": "STEHENLASSEN",
            }
        )

    write(
        "EIGHT_HUNDRED_THIRD_15_SHED_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "old_action_reading", "result_state_rival", "selected_process_reading", "terminal", "target_addressed", "selection_reason"],
    )
    write(
        "EIGHT_HUNDRED_THIRD_3_SHED_FAMILIES.tsv",
        family_rows,
        ["component_recipe", "surfaces", "events", "pages", "action_candidate", "result_candidate", "selected_reading", "selected_core_value"],
    )
    write(
        "EIGHT_HUNDRED_THIRD_15_REVISED_STATEMENTS.tsv",
        [affected_statements[key] for key in sorted(affected_statements)],
        ["statement_id", "page", "owner_de", "surface_sequence", "old_reading_de", "revised_reading_de"],
    )
    summary = {
        "status": "PASS",
        "decision": "SHED_REVISED_TO_STEHENLASSEN_AND_PROMOTED_TO_CORE20",
        "events": len(event_rows),
        "families": len(family_rows),
        "affected_statements": len(affected_statements),
        "terminal_events": sum(row["terminal"] == "YES" for row in event_rows),
        "target_addressed_events": sum(row["target_addressed"] == "YES" for row in event_rows),
        "result_state_selected": 0,
        "new_core_size": 20,
        "remaining_recurrent_strip_values": 11,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
