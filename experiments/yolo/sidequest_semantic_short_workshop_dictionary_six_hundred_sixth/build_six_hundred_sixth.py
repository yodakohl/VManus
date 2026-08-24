#!/usr/bin/env python3
"""Reduce the active prose lexicon to one-word components and short card compounds."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DICT_DIR = ROOT / "experiments/yolo/sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
OBJECT_DIR = ROOT / "experiments/yolo/sidequest_semantic_concrete_object_ledger_five_hundred_ninety_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SHORT = {
    "AIIN": "MASS",
    "AIN": "PORTION",
    "AIR": "LAUF",
    "AL": "ZIEL",
    "AR": "QUELLE",
    "CFH": "AUSWRINGEN",
    "CH": "ABZIEHEN",
    "CHD": "UMSETZEN",
    "CHK": "WAERMEN",
    "CKH": "DURCHLASS",
    "CTH": "BEREIT",
    "DA": "ZWEIT",
    "DY": "SCHLUSS",
    "E": "KURZ",
    "EE": "LANG",
    "EEE": "VOLL",
    "HO": "GABE",
    "IIN": "STUFE",
    "K": "ZUFUEHREN",
    "L": "FUEHREN",
    "LD": "BEFESTIGEN",
    "LS": "WEITER",
    "LSH": "WASCHEN",
    "O": "GANG",
    "OK": "ANSETZEN",
    "OL": "FORTSETZEN",
    "OR": "ANSATZ",
    "OS": "FACH",
    "OT": "DANACH",
    "P": "HINEIN",
    "R": "KUEHLEN",
    "S": "TEILEN",
    "SH": "HALTEN",
    "SHED": "ABSETZEN",
    "SOLK": "AUFFANGEN",
    "T": "EINTRAGEN",
    "TALAM": "VERWAHREN",
    "Y": "DIES",
}


def short_card(parse: str) -> str:
    return "·".join(SHORT[part] for part in parse.split("+"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    source_components = read_tsv(DICT_DIR / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    source_cards = read_tsv(DICT_DIR / "FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    source_events = read_tsv(DICT_DIR / "FIVE_HUNDRED_FIFTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_DICTIONARY.tsv")
    source_statements = read_tsv(OBJECT_DIR / "FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv")

    components = []
    for row in source_components:
        component = row["component"]
        components.append({
            "component_no": row["component_no"],
            "component": component,
            "sentence_role": row["sentence_role"],
            "short_workshop_word_de": SHORT[component],
            "old_atomic_meaning_de": row["atomic_meaning_de"],
            "grammar_contribution_de": row["grammar_contribution_de"],
            "card_types": row["card_types"],
            "events": row["events"],
            "teaching_rule_de": f"{component} immer als {SHORT[component]} sprechen; konkrete Ergänzungen kommen aus Bild und Fall.",
        })

    cards = []
    for row in source_cards:
        parts = row["component_parse"].split("+")
        short = short_card(row["component_parse"])
        old_words = len(row["portable_role_reading_de"].replace(";", " ").split())
        cards.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "component_parse": row["component_parse"],
            "component_count": len(parts),
            "short_card_default_de": short,
            "spoken_as_de": short.replace("·", " ").lower(),
            "old_portable_role_reading_de": row["portable_role_reading_de"],
            "old_role_word_count": old_words,
            "old_sentence_sized": "YES" if old_words >= 6 else "NO",
            "case_expansion_policy": "USE_OWNER_AND_CASE_LEDGER__NOT_CARD_DICTIONARY",
            "composition_status": row["composition_status"],
            "occurrences": row["occurrences"],
            "sections": row["sections"],
            "records": row["records"],
        })
    card_by_id = {row["card_no"]: row for row in cards}

    events = []
    for row in source_events:
        card = card_by_id[row["card_no"]]
        events.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "locus": row["locus"],
            "surface": row["surface"],
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "short_card_default_de": card["short_card_default_de"],
            "case_expansion_de": row["containing_clause_de"],
            "silent_owner_de": row["silent_owner_de"],
            "dictionary_layer": "SHORT_CARD_DEFAULT",
            "translation_layer": "OWNER_PLUS_CASE_EXPANSION",
        })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    statement_by_id = {row["statement_id"]: row for row in source_statements}
    statements = []
    for statement_id in statement_by_id:
        source = statement_by_id[statement_id]
        statement_events = events_by_statement[statement_id]
        statements.append({
            "statement_id": statement_id,
            "page": source["page"],
            "record": source["record"],
            "owner_de": source["owner_de"],
            "event_count": len(statement_events),
            "surface_sequence": " ".join(row["surface"] for row in statement_events),
            "short_card_sequence_de": " ".join(row["short_card_default_de"] for row in statement_events),
            "concrete_case_expansion_de": source["complete_working_instruction_de"],
            "teaching_reading_de": "Kurzkarten der Reihe nach sprechen; Bildbesitzer und Fall nur einmal ergänzen.",
        })

    write_tsv(HERE / "SIX_HUNDRED_SIXTH_THIRTY_EIGHT_ONE_WORD_COMPONENTS.tsv", components, list(components[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTH_173_SHORT_CARD_DICTIONARY.tsv", cards, list(cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv", events, list(events[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTH_116_SHORT_STATEMENT_EDITION.tsv", statements, list(statements[0]))

    distribution = Counter(int(row["component_count"]) for row in cards)
    old_sentence_sized = sum(row["old_sentence_sized"] == "YES" for row in cards)
    pocket = ["# Kurzes Werkstattwörterbuch", "", "## 38 Grundwörter", ""]
    for row in components:
        pocket.append(f"- **{row['component']}** — {row['short_workshop_word_de']}")
    pocket.extend(["", "## 173 Karten", ""])
    for row in cards:
        pocket.append(f"- **{row['card_no']}** `{row['surfaces']}` = {row['short_card_default_de']}")
    (HERE / "SIX_HUNDRED_SIXTH_POCKET_DICTIONARY.md").write_text("\n".join(pocket).rstrip() + "\n", encoding="utf-8")

    report = f"""# Sechshundertsechste Runde: das kurze Werkstattwörterbuch

## Ergebnis

Das Wörterbuch ist jetzt sauber zweigeteilt:

- **38 Grundwörter**, jedes genau ein kurzes Werkstattwort;
- **173 Karten**, jede eine Folge aus ein bis fünf dieser Grundwörter.

Keine Kartenprimärglosse ist mehr ein Satz. {old_sentence_sized} alte Rollenglossen mit sechs oder mehr Wörtern bleiben nur als Fallausbau erhalten.

## Die wichtigsten Wörter

```text
AIIN MASS      AIN PORTION    AL ZIEL       AR QUELLE
AIR LAUF       OR ANSATZ      Y DIES         DY SCHLUSS
OK ANSETZEN    CH ABZIEHEN    CHD UMSETZEN   K ZUFUEHREN
L FUEHREN      SH HALTEN      SHED ABSETZEN  SOLK AUFFANGEN
E KURZ         EE LANG        EEE VOLL       CTH BEREIT
```

Damit bedeutet etwa eine lange Karte nicht „den laufenden Posten an bezeichnete Stelle durch Durchlass kurz halten“, sondern schlicht:

```text
HALTEN · KURZ · DURCHLASS · ZIEL
```

Erst der konkrete Fall macht daraus eine flüssige Anweisung.

## Kartenlängen

- ein Grundwort: {distribution[1]} Karten;
- zwei: {distribution[2]};
- drei: {distribution[3]};
- vier: {distribution[4]};
- fünf: {distribution[5]}.

Das ist für einen Lehrling viel leichter: Er lernt 38 Wörter, wenige Ganzformen und die Reihenfolge. Er muss keine 173 Satzglossen auswendig lernen.

## Wichtige Korrekturen

- AIIN heißt nur MASS, nicht „vorgeschriebenes Maß“ als eigener Wortinhalt;
- AIR heißt LAUF, nicht automatisch Wasser;
- AL heißt ZIEL und AR QUELLE;
- Y heißt DIES, also der laufende Posten;
- O heißt GANG;
- Fallwörter wie Pflanze, Bad, Körperstelle, Wasser, Tuch oder Stern kommen aus Bild und Fall, nicht aus jedem Kürzel.

## Nächster Schritt

Als nächstes testen wir das kurze Wörterbuch an den längsten Karten und schwierigsten Sätzen. Wo die reine Links-nach-rechts-Komposition holprig wird, darf genau eine historisch plausible Werkstattreihenfolge oder eine gelernte Ganzkarte einspringen.
"""
    (HERE / "SIX_HUNDRED_SIXTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "components": len(components),
        "cards": len(cards),
        "events": len(events),
        "statements": len(statements),
        "max_component_words": max(len(row["short_workshop_word_de"].split()) for row in components),
        "max_card_components": max(int(row["component_count"]) for row in cards),
        "old_sentence_sized_glosses_moved_to_case_layer": old_sentence_sized,
        "decision": "ONE_WORD_COMPONENTS_PLUS_SHORT_CARD_COMPOUNDS",
    }
    (HERE / "SIX_HUNDRED_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
