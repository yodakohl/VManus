#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"

REVISED = {
    "H1-S001": "Bei der breiten gezahnten Bluetenpflanze: Den laufenden Posten kurz entnehmen; den Ansatz im Arbeitsgang bereiten, aus der Quelle nehmen und bearbeiten; dazu Wasser entnehmen, danach den Posten bearbeiten, entnehmen und weiterfuehren, nach Sollmass ansetzen und kurz bearbeiten.",
    "H3-S001": "Bei der dicht bluehenden Kronenpflanze: Den Ansatz an der Zielstelle bearbeiten und weiter halten; auspressen, bis zum Sollmass halten, in den lokalen Empfaenger einfuellen, laenger halten, bearbeiten, entnehmen und den Schritt schliessen.",
    "H3-S002": "Bei der dicht bluehenden Kronenpflanze: Den laufenden Posten im Arbeitsgang halten und bearbeiten.",
    "H4-S004": "Bei der breitblaettrigen rispigen Pflanze: Nach Sollmass an der Zielstelle ansetzen, den laufenden Posten weiter bearbeiten, als Ansatz beibehalten und als Ansatzportion fuehren.",
    "B1-S015": "Am gemeinsamen zweireihigen Becken: Den laufenden Posten kurz bearbeiten; dann ansetzen und umsetzen; den Schritt schliessen.",
    "B3-S029": "Am durch den Bogen verbundenen Hauptpaar: Weiterarbeiten; dann den laufenden Posten vollstaendig bearbeiten; dann kurz ansetzen; den Schritt schliessen.",
    "B3-S034": "Am durch den Bogen verbundenen Hauptpaar: Den Arbeitsgang bis zur Stufe fuehren; den Posten bereitet halten und bearbeiten; danach nach Sollmass an der Zielstelle weiterfuehren, stehen lassen und schliessen.",
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
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    targets = [row for row in events if "T" in row["component_recipe"].split("+")]

    candidates = [
        {"candidate": "ANWENDEN", "herbal_fit": "HIGH", "biological_fit": "MEDIUM", "all_components_spoken": "NO", "decision": "REJECT_OLD_TOO_TARGET_SPECIFIC"},
        {"candidate": "BEARBEITEN", "herbal_fit": "HIGH", "biological_fit": "HIGH", "all_components_spoken": "YES", "decision": "SELECT_CORE_VALUE"},
        {"candidate": "BEHANDELN", "herbal_fit": "HIGH", "biological_fit": "MEDIUM", "all_components_spoken": "YES", "decision": "REJECT_TOO_MEDICAL"},
        {"candidate": "BENUTZEN", "herbal_fit": "MEDIUM", "biological_fit": "LOW", "all_components_spoken": "NO", "decision": "REJECT_OBJECT_MISMATCH"},
        {"candidate": "AUSFUEHREN", "herbal_fit": "MEDIUM", "biological_fit": "HIGH", "all_components_spoken": "YES", "decision": "REJECT_DUPLICATES_OPERATION_FRAME"},
        {"candidate": "BETAETIGEN", "herbal_fit": "LOW", "biological_fit": "HIGH", "all_components_spoken": "YES", "decision": "REJECT_MACHINE_SPECIFIC"},
    ]

    event_rows = []
    card_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in targets:
        tokens = row["component_recipe"].split("+")
        literal = " · ".join("BEARBEITEN" if token == "T" else part for token, part in zip(tokens, row["sixth_grammar_reading_de"].split(" · ")))
        item = {
            "event_id": row["event_id"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "owner_de": row["owner_de"],
            "exact_card_id": row["exact_card_id"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "old_literal_de": row["sixth_grammar_reading_de"],
            "revised_literal_de": literal,
            "selected_t_value": "BEARBEITEN",
            "local_object": row["owner_de"] if "+Y" not in row["component_recipe"] and not row["component_recipe"].endswith("Y") else "laufender Posten unter lokalem Besitzer",
        }
        event_rows.append(item)
        card_groups[row["exact_card_id"]].append(item)

    card_rows = []
    for card_id, rows in card_groups.items():
        first = rows[0]
        card_rows.append(
            {
                "exact_card_id": card_id,
                "surfaces": "|".join(sorted({row["surface"] for row in rows})),
                "component_recipe": first["component_recipe"],
                "revised_literal_de": first["revised_literal_de"],
                "events": len(rows),
                "pages": ";".join(sorted({row["page"] for row in rows})),
            }
        )

    statement_rows = []
    for statement_id, revised in REVISED.items():
        row = statements[statement_id]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "page": row["page"],
                "owner_noun_de": row["owner_noun_de"],
                "surface_sequence": row["surface_sequence"],
                "old_reading_de": row["working_reading_de"],
                "revised_reading_de": revised,
                "t_events": ",".join(item["event_id"] for item in event_rows if item["statement_id"] == statement_id),
            }
        )

    distinction_rows = [
        {"component": "OK", "short_value_de": "ANSETZEN", "question": "Which work step is activated?", "contrast": "not the manipulation itself", "decision": "KEEP"},
        {"component": "T", "short_value_de": "BEARBEITEN", "question": "What is done to the current item?", "contrast": "not merely activation or relocation", "decision": "REVISE"},
        {"component": "CHD", "short_value_de": "UMSETZEN", "question": "Where or into what state does the item move?", "contrast": "not general working", "decision": "KEEP"},
    ]

    write("EIGHT_HUNDRED_TWENTY_FIRST_6_T_CANDIDATES.tsv", candidates, ["candidate", "herbal_fit", "biological_fit", "all_components_spoken", "decision"])
    write("EIGHT_HUNDRED_TWENTY_FIRST_10_T_EVENTS.tsv", event_rows, ["event_id", "page", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "old_literal_de", "revised_literal_de", "selected_t_value", "local_object"])
    write("EIGHT_HUNDRED_TWENTY_FIRST_9_T_CARDS.tsv", card_rows, ["exact_card_id", "surfaces", "component_recipe", "revised_literal_de", "events", "pages"])
    write("EIGHT_HUNDRED_TWENTY_FIRST_7_REVISED_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "old_reading_de", "revised_reading_de", "t_events"])
    write("EIGHT_HUNDRED_TWENTY_FIRST_3_ACTION_DISTINCTIONS.tsv", distinction_rows, ["component", "short_value_de", "question", "contrast", "decision"])
    summary = {
        "status": "PASS",
        "decision": "T_REVISED_FROM_ANWENDEN_TO_BEARBEITEN_ACROSS_ALL_TEN_EVENTS",
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "pages": sorted({row["page"] for row in event_rows}),
        "old_value": "ANWENDEN",
        "new_value": "BEARBEITEN",
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
