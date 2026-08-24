#!/usr/bin/env python3
"""Build the integrated 39-root, 173-card, 381-event workshop edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh/SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv"

LEXICON = {
    "OK": ("ANSETZEN", "PROCESS_VERB"),
    "CHD": ("UMSETZEN", "PROCESS_VERB"),
    "SH": ("HALTEN", "PROCESS_VERB"),
    "SHED": ("ABSETZEN", "PROCESS_VERB"),
    "CHK": ("WAERMEN", "PROCESS_VERB"),
    "CTH": ("BEREIT", "PROCESS_STATE"),
    "SOLK": ("AUFFANGEN", "PROCESS_VERB"),
    "P": ("EINFUELLEN", "PROCESS_VERB"),
    "LSH": ("WASCHEN", "PROCESS_VERB"),
    "CFH": ("AUSWRINGEN", "PROCESS_VERB"),
    "CH": ("ABNEHMEN", "CONTROL_ACTION"),
    "T": ("EINTRAGEN", "CONTROL_ACTION"),
    "K": ("ZUDOSIEREN", "CONTROL_ACTION"),
    "S": ("TEILEN", "CONTROL_ACTION"),
    "L": ("WEITERLEITEN", "DIRECTION_SEQUENCE"),
    "OL": ("FORTSETZEN", "DIRECTION_SEQUENCE"),
    "OT": ("DANACH", "DIRECTION_SEQUENCE"),
    "AL": ("ZIELSTELLE", "ADDRESS"),
    "AR": ("VORRAT", "ADDRESS"),
    "AIR": ("FLUESSIGKEITSLAUF", "MATERIAL_STATE"),
    "OR": ("ANSATZ", "MATERIAL_STATE"),
    "HO": ("ZUTAT", "MATERIAL_STATE"),
    "CKH": ("DURCHLASS", "WORK_OBJECT"),
    "O": ("ARBEITSGANG", "WORK_OBJECT"),
    "Y": ("ARBEITSPOSTEN", "ITEM_REFERENCE"),
    "AIN": ("PORTION", "QUANTITY"),
    "AIIN": ("SOLLMASS", "QUANTITY"),
    "IIN": ("ARBEITSSTUFE", "QUANTITY_STAGE"),
    "E": ("KURZ", "GRADE"),
    "EE": ("LANG", "GRADE"),
    "EEE": ("VOLL", "GRADE"),
    "R": ("KUEHLEN", "PROCESS_MODIFIER"),
    "AN": ("NACHPORTION", "QUANTITY"),
    "DA": ("ZWEITMARKER", "CONTROL_MARKER"),
    "LD": ("BEFESTIGEN", "CONTROL_ACTION"),
    "DY": ("SCHLUSS", "LICENSED_ENDPOINT"),
    "OS": ("ARBEITSFACH", "MEMORIZED_WHOLE_COMMAND"),
    "RESUME_CARD": ("WIEDERAUFNEHMEN", "MEMORIZED_WHOLE_COMMAND"),
    "TALAM": ("VERWAHREN", "MEMORIZED_WHOLE_COMMAND"),
}
WHOLE_RECIPES = {"OS", "RESUME_CARD", "TALAM"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(card: str) -> int:
    return int(card.removeprefix("PROC"))


def fluent(commands: list[str]) -> str:
    parts = []
    for command in commands:
        phrase = command.replace(" · ", " ").replace("; SCHLUSS", "; Schritt schliessen")
        phrase = phrase.replace("[", "").replace("]", "")
        parts.append(phrase[0].upper() + phrase[1:].lower() if phrase else phrase)
    return "; dann ".join(parts) + "."


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(SOURCE)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["card_no"]].append(event)
        by_statement[event["statement_id"]].append(event)

    token_counts = Counter(atom for event in events for atom in event["semantic_component_parse"].split("+"))
    event_counts = {atom: sum(atom in event["semantic_component_parse"].split("+") for event in events) for atom in LEXICON}
    card_counts = {atom: len({event["card_no"] for event in events if atom in event["semantic_component_parse"].split("+")}) for atom in LEXICON}
    root_rows = []
    for index, (atom, (meaning, category)) in enumerate(LEXICON.items(), start=1):
        root_rows.append({
            "root_no": f"R{index:02d}",
            "component": atom,
            "short_value_de": meaning,
            "category": category,
            "card_types": card_counts[atom],
            "events_with_component": event_counts[atom],
            "component_tokens": token_counts[atom],
            "teaching_gloss_de": {
                "DY": "nur als lizenzierte exakte Endkonstruktion",
                "Y": "dieser aktuell gemeinte Posten; kein Schluss",
                "AIIN": "vorgeschriebenes Mass oder Sollwert",
                "IIN": "Stufe des Arbeitsgangs, nicht Menge",
                "AIR": "laufende Arbeitsfluessigkeit, nicht Quelladresse",
            }.get(atom, meaning.lower()),
        })

    card_rows = []
    for card in sorted(by_card, key=number):
        rows = by_card[card]
        first = rows[0]
        atoms = first["semantic_component_parse"].split("+")
        singleton = any(event_counts[atom] == 1 for atom in atoms)
        mode = "MEMORIZED_WHOLE_COMMAND" if first["semantic_component_parse"] in WHOLE_RECIPES else "COMPOSITION_WITH_SINGLETON_ATOM" if singleton else "PRODUCTIVE_COMPOSITION"
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": first["semantic_component_parse"],
            "atomic_expansion_de": " · ".join(LEXICON[atom][0] for atom in atoms),
            "short_default_de": first["standard_command_de"],
            "composition_mode": mode,
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "records": "|".join(sorted({row["record"] for row in rows})),
            "event_ids": "|".join(row["event_id"] for row in rows),
        })

    event_rows = []
    for event in events:
        atoms = event["semantic_component_parse"].split("+")
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "component_recipe": event["semantic_component_parse"],
            "atomic_expansion_de": " · ".join(LEXICON[atom][0] for atom in atoms),
            "short_default_de": event["standard_command_de"],
        })

    statement_rows = []
    record_order = []
    for event in events:
        if event["record"] not in record_order:
            record_order.append(event["record"])
    statement_order = []
    for event in events:
        if event["statement_id"] not in statement_order:
            statement_order.append(event["statement_id"])
    for sid in statement_order:
        rows = by_statement[sid]
        statement_rows.append({
            "statement_id": sid,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "events": len(rows),
            "surface_sequence": " ".join(row["surface"] for row in rows),
            "component_sequence": " | ".join(row["semantic_component_parse"] for row in rows),
            "atomic_sequence_de": " | ".join(" · ".join(LEXICON[atom][0] for atom in row["semantic_component_parse"].split("+")) for row in rows),
            "literal_commands_de": " | ".join(row["standard_command_de"] for row in rows),
            "complete_workshop_paraphrase_de": fluent([row["standard_command_de"] for row in rows]),
            "closes": "YES" if "SCHLUSS" in rows[-1]["standard_command_de"] else "NO",
        })

    record_rows = []
    for record in record_order:
        rows = [row for row in statement_rows if row["record"] == record]
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "statements": len(rows),
            "events": sum(int(row["events"]) for row in rows),
            "continuous_surface": " || ".join(row["surface_sequence"] for row in rows),
            "continuous_workshop_reading_de": " ".join(f"[{row['statement_id']}] {row['complete_workshop_paraphrase_de']}" for row in rows),
        })

    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_SECOND_39_ROOT_TABLET.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_SECOND_381_EVENT_INTERLINEAR.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_SECOND_116_STATEMENT_EDITION.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTY_SECOND_11_RECORD_EDITION.tsv", record_rows, list(record_rows[0]))

    summary = {
        "status": "PASS",
        "root_entries": len(root_rows),
        "card_types": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "memorized_whole_cards": sum(row["composition_mode"] == "MEMORIZED_WHOLE_COMMAND" for row in card_rows),
        "cards_with_singleton_atom": sum(row["composition_mode"] == "COMPOSITION_WITH_SINGLETON_ATOM" for row in card_rows),
        "productive_cards": sum(row["composition_mode"] == "PRODUCTIVE_COMPOSITION" for row in card_rows),
        "decision": "ONE_39_ENTRY_TABLET_READS_ALL_173_CARDS_381_EVENTS_AND_116_STATEMENTS",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
