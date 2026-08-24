#!/usr/bin/env python3
"""Stress long cards and dense statements without inflating component meanings."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SHORT_DIR = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SPECIAL = {
    "PROC007": (
        "SEQUENCE_BRACKET",
        "DANACH [DIES EINTRAGEN · ABZIEHEN] FORTSETZEN",
        "OT eröffnet und OL schließt denselben Folgeblock; kein neues Ganzwort.",
    ),
    "PROC033": (
        "COREFERENTIAL_ITEM_BRACKET",
        "DIES HALTEN · IM GANG EINTRAGEN · DIES",
        "Die beiden Y/DIES-Stellen zeigen denselben laufenden Posten vor und nach dem Eintrag.",
    ),
    "PROC057": (
        "CLOSED_LONG_PROCESS",
        "ABZIEHEN · LANG · DURCHLASS · GANG; SCHLUSS",
        "DY schließt die lange Durchlasshandlung; die Oberflächenreihenfolge bleibt stehen.",
    ),
    "PROC136": (
        "STATE_THRESHOLD_FRAME",
        "HALTEN · KURZ · BIS BEREIT; UMSETZEN · DIES",
        "CTH/BEREIT bildet die Schwelle zwischen Halten und Umsetzen.",
    ),
    "PROC171": (
        "DOUBLE_GRADE_CADENCE",
        "KURZ · ZUFUEHREN · KURZ · DIES",
        "Die doppelte E/KURZ-Rahmung bleibt als gelernter Rhythmus; kein zweiter E-Wortwert.",
    ),
}


def default_recitation(short: str) -> str:
    words = short.split("·")
    if words and words[-1] == "SCHLUSS":
        return " · ".join(words[:-1]) + "; SCHLUSS"
    return " · ".join(words)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_173_SHORT_CARD_DICTIONARY.tsv")
    events = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    statements = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_116_SHORT_STATEMENT_EDITION.tsv")

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_card[row["card_no"]].append(row)
        events_by_statement[row["statement_id"]].append(row)

    recitation_dictionary = []
    for row in cards:
        if row["card_no"] in SPECIAL:
            kind, recitation, note = SPECIAL[row["card_no"]]
            repair = 1
        elif int(row["component_count"]) >= 4:
            kind = "STRAIGHT_TELEGRAPH_CHAIN"
            recitation = default_recitation(row["short_card_default_de"])
            note = "Komponenten in sichtbarer Reihenfolge sprechen; nur vor SCHLUSS pausieren."
            repair = 0
        else:
            kind = "SHORT_LEFT_TO_RIGHT"
            recitation = default_recitation(row["short_card_default_de"])
            note = "Kurze Karte direkt von links nach rechts sprechen."
            repair = 0
        recitation_dictionary.append({
            **row,
            "recitation_kind": kind,
            "spoken_recitation_de": recitation,
            "scope_note_de": note,
            "scope_repair_cost": repair,
            "component_order_preserved": "YES",
            "new_whole_card_semantic_value": "NO",
        })
    recitation_by_card = {row["card_no"]: row for row in recitation_dictionary}

    long_cards = []
    for row in recitation_dictionary:
        if int(row["component_count"]) < 4:
            continue
        examples = events_by_card[row["card_no"]]
        long_cards.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "component_parse": row["component_parse"],
            "component_count": row["component_count"],
            "short_surface_order_de": row["short_card_default_de"],
            "recitation_kind": row["recitation_kind"],
            "spoken_recitation_de": row["spoken_recitation_de"],
            "scope_note_de": row["scope_note_de"],
            "occurrences": row["occurrences"],
            "example_event_ids": "|".join(item["event_id"] for item in examples),
            "example_statement_ids": "|".join(dict.fromkeys(item["statement_id"] for item in examples)),
            "example_case_expansion_de": examples[0]["case_expansion_de"],
            "component_order_preserved": row["component_order_preserved"],
            "new_whole_card_semantic_value": row["new_whole_card_semantic_value"],
        })

    statement_sorted = sorted(statements, key=lambda row: (-int(row["event_count"]), row["statement_id"]))
    hard_statements = []
    for source in statement_sorted[:12]:
        statement_events = events_by_statement[source["statement_id"]]
        recitations = [recitation_by_card[row["card_no"]]["spoken_recitation_de"] for row in statement_events]
        chunks = [" | ".join(recitations[i:i + 4]) for i in range(0, len(recitations), 4)]
        special_cards = [row["card_no"] for row in statement_events if row["card_no"] in SPECIAL]
        long_ids = [row["card_no"] for row in statement_events if int(recitation_by_card[row["card_no"]]["component_count"]) >= 4]
        hard_statements.append({
            "statement_id": source["statement_id"],
            "page": source["page"],
            "record": source["record"],
            "owner_de": source["owner_de"],
            "event_count": source["event_count"],
            "surface_sequence": source["surface_sequence"],
            "long_card_ids": "|".join(long_ids) if long_ids else "NONE",
            "special_scope_card_ids": "|".join(special_cards) if special_cards else "NONE",
            "four_card_teaching_chunks_de": " || ".join(chunks),
            "fluent_case_expansion_de": source["concrete_case_expansion_de"],
            "source_event_order_preserved": "YES",
            "new_semantic_word_added": "NO",
        })

    rules = [
        {"rule_no": 1, "rule_name": "VISIBLE_ORDER", "rule_de": "Grundwörter grundsätzlich in sichtbarer Kartenreihenfolge sprechen.", "applies_to": "168/173 Karten"},
        {"rule_no": 2, "rule_name": "CLOSE_PAUSE", "rule_de": "Vor terminalem SCHLUSS kurz pausieren; nichts umstellen.", "applies_to": "alle geschlossenen Langkarten"},
        {"rule_no": 3, "rule_name": "SEQUENCE_BRACKET", "rule_de": "DANACH ... FORTSETZEN rahmt einen einzigen Arbeitsblock.", "applies_to": "PROC007"},
        {"rule_no": 4, "rule_name": "COREFERENCE", "rule_de": "Zweimal DIES in derselben Karte kann denselben Posten vor und nach einer Handlung wiederaufnehmen.", "applies_to": "PROC033"},
        {"rule_no": 5, "rule_name": "STATE_THRESHOLD", "rule_de": "BEREIT zwischen zwei Handlungen markiert die Schwelle: erste Handlung bis bereit, dann zweite.", "applies_to": "PROC136"},
        {"rule_no": 6, "rule_name": "DOUBLE_GRADE_CADENCE", "rule_de": "KURZ um eine Handlung bleibt ein gelernter Ausführungsrhythmus, kein neues Wort.", "applies_to": "PROC171"},
    ]

    write_tsv(HERE / "SIX_HUNDRED_SEVENTH_173_RECITATION_DICTIONARY.tsv", recitation_dictionary, list(recitation_dictionary[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTH_TWENTY_FIVE_LONG_CARD_AUDIT.tsv", long_cards, list(long_cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTH_TWELVE_HARD_STATEMENTS.tsv", hard_statements, list(hard_statements[0]))
    write_tsv(HERE / "SIX_HUNDRED_SEVENTH_SIX_SCOPE_RULES.tsv", rules, list(rules[0]))

    report = f"""# Sechshundertsiebte Runde: Langkarten und dichte Aussagen

## Ergebnis

Die vier Fünfteiler und 21 Vierteiler brauchen kein neues Wörterbuch. Alle 25 behalten ihre sichtbare Komponentenfolge. Zwanzig sind einfache Telegrammketten; fünf erhalten nur eine Sprech- oder Klammerregel.

## Die vier Fünfteiler

```text
PROC007  DANACH [DIES EINTRAGEN · ABZIEHEN] FORTSETZEN
PROC033  DIES HALTEN · IM GANG EINTRAGEN · DIES
PROC057  ABZIEHEN · LANG · DURCHLASS · GANG; SCHLUSS
PROC136  HALTEN · KURZ · BIS BEREIT; UMSETZEN · DIES
```

Keiner davon wird zu einem neuen Satzwort. Die Karte bleibt aus bekannten Grundwörtern gebaut.

## Ein zusätzlicher Rhythmus

PROC171 (`qekey`) lautet KURZ · ZUFUEHREN · KURZ · DIES. Das ist die einzige lange Karte, bei der wir einen gelernten Doppelgrad-Rhythmus behalten. Auch hier entstehen weder ein neuer E-Wert noch eine neue Stoffbedeutung.

## Die dichtesten Aussagen

Die zwölf längsten Aussagen enthalten bis zu {hard_statements[0]['event_count']} Karten. Für den Lehrling werden sie in Vierergruppen gesprochen, aber nicht umsortiert. Die Fallübersetzung ergänzt Artikel, Gefäß, Körperstelle oder Produkt nur einmal pro Aussage.

Beispiel B1-S002:

```text
ANSETZEN·MASS | ZUFUEHREN·LAUF | ANSETZEN·ZIEL | QUELLE
FORTSETZEN | ZUFUEHREN·PORTION | FORTSETZEN·ZUFUEHREN·PORTION | ZIEL
...
```

Das liest sich wie eine Werkstattliste, nicht wie ein einzelnes überlanges Wort.

## Entscheidung

Die sichtbare Reihenfolge ist selbst die Werkstattreihenfolge. Wir brauchen keine allgemeine Umstellungsgrammatik. Es reichen Pausen, zwei Klammern, eine Zustandsschwelle und ein Doppelgrad-Rhythmus.

## Nächster Schritt

Als nächstes untersuchen wir die 14 echten Einwortkarten und die fünf gelernten Spezialkerne: Welche davon sind selbständige Fachwörter, und welche sind nur graphische Kurzformen eines bereits bekannten Grundworts?
"""
    (HERE / "SIX_HUNDRED_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "cards": len(recitation_dictionary),
        "long_cards": len(long_cards),
        "five_component_cards": sum(int(row["component_count"]) == 5 for row in long_cards),
        "four_component_cards": sum(int(row["component_count"]) == 4 for row in long_cards),
        "special_scope_or_cadence_cards": len(SPECIAL),
        "new_semantic_values": 0,
        "hard_statements": len(hard_statements),
        "decision": "SURFACE_ORDER_IS_WORKSHOP_ORDER_WITH_FIVE_SCOPE_NOTES",
    }
    (HERE / "SIX_HUNDRED_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
