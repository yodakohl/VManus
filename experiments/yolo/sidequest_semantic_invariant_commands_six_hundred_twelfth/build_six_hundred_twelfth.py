#!/usr/bin/env python3
"""Compile one invariant workshop command per semantic card parse and apply it to all cases."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GRADE_DIR = ROOT / "experiments/yolo/sidequest_semantic_action_grade_doctrine_six_hundred_eleventh"
CASE_DIR = ROOT / "experiments/yolo/sidequest_semantic_complete_workshop_cases_six_hundred_third"
EVENT_DIR = ROOT / "experiments/yolo/sidequest_semantic_standalone_words_six_hundred_eighth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SPECIAL_PARSE_COMMANDS = {
    "OT+Y+T+CH+OL": "DANACH [DIES EINTRAGEN · ABZIEHEN] FORTSETZEN",
    "SH+O+Y+T+Y": "DIES HALTEN · IM GANG EINTRAGEN · DIES",
    "CH+EE+CKH+O+DY": "ABZIEHEN · LANG · DURCHLASS · GANG; SCHLUSS",
    "SH+E+CTH+CHD+Y": "HALTEN · KURZ · BIS BEREIT; UMSETZEN · DIES",
    "E+K+E+Y": "KURZ · ZUFUEHREN · KURZ · DIES",
}


def command(short: str, parse: str) -> str:
    if parse in SPECIAL_PARSE_COMMANDS:
        return SPECIAL_PARSE_COMMANDS[parse]
    words = short.split("·")
    if words[-1] == "SCHLUSS":
        return " · ".join(words[:-1]) + "; SCHLUSS"
    return " · ".join(words)


def command_class(row: dict[str, str]) -> str:
    if row["action_components"] != "NONE":
        return "ACTION_COMMAND"
    slots = set(row["slot_signature"].split(">"))
    if "CLOSE" in slots:
        return "CLOSE_FORMULA"
    if "STATE" in slots or "GRADE" in slots:
        return "STATE_OR_GRADE_FORMULA"
    if "SEQUENCE" in slots:
        return "SEQUENCE_FORMULA"
    return "ARGUMENT_OR_OBJECT_FORMULA"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(GRADE_DIR / "SIX_HUNDRED_ELEVENTH_173_GRADE_AWARE_DICTIONARY.tsv")
    events = read_tsv(EVENT_DIR / "SIX_HUNDRED_EIGHTH_381_CONSOLIDATED_EVENT_EDITION.tsv")
    case_events = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_381_EVENT_CASE_BINDING.tsv")
    case_statements = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_116_STATEMENT_CASE_EDITION.tsv")

    cards_by_parse: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        cards_by_parse[row["semantic_component_parse"]].append(row)

    command_rows = []
    command_by_parse = {}
    for number, parse in enumerate(sorted(cards_by_parse), 1):
        group = cards_by_parse[parse]
        first = group[0]
        standard = command(first["consolidated_short_default_de"], parse)
        row = {
            "command_id": f"CMD{number:03d}",
            "semantic_component_parse": parse,
            "slot_signature": first["slot_signature"],
            "standard_command_de": standard,
            "command_class": command_class(first),
            "card_ids": "|".join(item["card_no"] for item in group),
            "surfaces": "|".join(item["surfaces"] for item in group),
            "card_types": len(group),
            "events": sum(int(item["occurrences"]) for item in group),
            "action_components": first["action_components"],
            "grade_scope_assignments": first["grade_scope_assignments"],
            "owner_fill_rule_de": "DIES, Ziel, Quelle oder ausgelassener Gegenstand kommen aus aktivem Bild/Fall.",
            "meaning_invariant": "YES",
        }
        command_rows.append(row)
        command_by_parse[parse] = row

    card_rows = []
    for row in cards:
        standard = command_by_parse[row["semantic_component_parse"]]
        card_rows.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "semantic_component_parse": row["semantic_component_parse"],
            "command_id": standard["command_id"],
            "standard_command_de": standard["standard_command_de"],
            "command_class": standard["command_class"],
            "occurrences": row["occurrences"],
            "records": row["records"],
            "duplicate_semantic_command": "YES" if int(standard["card_types"]) > 1 else "NO",
        })
    card_by_id = {row["card_no"]: row for row in card_rows}

    case_event_by_id = {row["event_id"]: row for row in case_events}
    event_rows = []
    for row in events:
        card = card_by_id[row["card_no"]]
        case = case_event_by_id[row["event_id"]]
        event_rows.append({
            "event_id": row["event_id"],
            "case_id": case["case_id"],
            "phase": case["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "surface": row["surface"],
            "card_no": row["card_no"],
            "semantic_component_parse": row["semantic_component_parse"],
            "command_id": card["command_id"],
            "standard_command_de": card["standard_command_de"],
            "silent_owner_de": row["silent_owner_de"],
            "case_expansion_de": row["case_expansion_de"],
            "meaning_invariant_across_occurrences": "YES",
        })

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for source in case_statements:
        statement_events = events_by_statement[source["statement_id"]]
        statement_rows.append({
            "case_id": source["case_id"],
            "phase": source["phase"],
            "statement_id": source["statement_id"],
            "page": source["page"],
            "record": source["record"],
            "owner_or_station": source["owner_or_station"],
            "input_product_id": source["input_product_id"],
            "event_count": len(statement_events),
            "surface_sequence": " ".join(row["surface"] for row in statement_events),
            "command_ids": "|".join(row["command_id"] for row in statement_events),
            "invariant_command_sequence_de": " | ".join(row["standard_command_de"] for row in statement_events),
            "concrete_case_expansion_de": source["concrete_case_step_de"],
            "owner_and_product_attach_rule_de": "Owner und Produkt einmal nennen; dann Kommandos unverändert sprechen.",
        })

    write_tsv(HERE / "SIX_HUNDRED_TWELFTH_161_STANDARD_COMMANDS.tsv", command_rows, list(command_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWELFTH_173_CARD_COMMAND_MAP.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWELFTH_381_INVARIANT_EVENT_COMMANDS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWELFTH_116_CASE_COMMAND_SEQUENCES.tsv", statement_rows, list(statement_rows[0]))

    md = ["# Sechs Fälle mit invarianten Werkstattbefehlen", ""]
    for case_id in [f"C{i}" for i in range(1, 7)]:
        md.extend([f"## {case_id}", ""])
        for row in [item for item in statement_rows if item["case_id"] == case_id]:
            md.append(
                f"- **{row['statement_id']}** / {row['owner_or_station']} / {row['input_product_id']}: "
                f"{row['invariant_command_sequence_de']}"
            )
            md.append(f"  - Fallausbau: {row['concrete_case_expansion_de']}")
        md.append("")
    (HERE / "SIX_HUNDRED_TWELFTH_SIX_CASE_COMMAND_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    duplicate_groups = [row for row in command_rows if int(row["card_types"]) > 1]
    redundant_cards = sum(int(row["card_types"]) - 1 for row in duplicate_groups)
    report = f"""# Sechshundertzwölfte Runde: invariante Werkstattbefehle

## Ergebnis

Die 173 exakten Karten reduzieren sich auf **{len(command_rows)} verschiedene Befehle**. {len(duplicate_groups)} Bedeutungsfolgen haben mehrere exakte Kartenidentitäten; zusammen sind {redundant_cards} Karten semantisch redundant, aber graphisch verschieden.

Jede der 381 Kartenverwendungen trägt nun genau denselben kurzen Befehl wie alle anderen Vorkommen derselben Bedeutungsfolge. Besitzer, Pflanze, Produkt, Gefäß oder Körperstelle werden nur außen ergänzt.

## Beispiele

```text
OK+E+DY       ANSETZEN · KURZ; SCHLUSS
OK+EE+DY      ANSETZEN · LANG; SCHLUSS
OK+EEE+DY     ANSETZEN · VOLL; SCHLUSS
SH+E+Y        HALTEN · KURZ · DIES
SH+EE+Y       HALTEN · LANG · DIES
CHK+EE+DY     WAERMEN · LANG; SCHLUSS
L+CHD+DY      FUEHREN · UMSETZEN; SCHLUSS
```

## Trennung der Ebenen

```text
Karte:       ANSETZEN · LANG; SCHLUSS
Fall C1:     milden Grundauszug im gemeinsamen Becken länger ansetzen
Fall C4:     temperierte Auflage an der Paarstation länger einwirken lassen
```

Der Kartenwert bleibt gleich. Nur Bildbesitzer und Fall machen daraus Bad, Waschung, Auflage oder technischen Einsatz.

## Warum das Mehrschreibersystem stabil bleibt

Der erste Schreiber kann `qokeedy`, der zweite dieselbe Kartenidentität in seiner gelernten Oberfläche schreiben; beide lesen denselben CMD-Befehl. Der Korrektor braucht nicht über „Wasser“, „Körper“ oder „Pflanze“ im einzelnen Zeichen zu streiten.

## Nächster Schritt

Als nächstes greifen wir die {len(duplicate_groups)} mehrfach realisierten Befehle an: Welche Doppelungen sind echte allographische Karten, welche markieren Register oder Schreiber, und welche könnten doch eine kleine Bedeutungsnuance tragen?
"""
    (HERE / "SIX_HUNDRED_TWELFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "semantic_commands": len(command_rows),
        "cards": len(card_rows),
        "duplicate_command_groups": len(duplicate_groups),
        "semantically_redundant_card_ids": redundant_cards,
        "events": len(event_rows),
        "statements": len(statement_rows),
        "cases": len({row["case_id"] for row in statement_rows}),
        "decision": "ONE_INVARIANT_COMMAND_PER_SEMANTIC_PARSE_ACROSS_ALL_CASES",
    }
    (HERE / "SIX_HUNDRED_TWELFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
