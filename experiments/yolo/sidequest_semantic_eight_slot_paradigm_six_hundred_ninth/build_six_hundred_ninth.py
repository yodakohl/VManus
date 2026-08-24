#!/usr/bin/env python3
"""Organize the 37 semantic words into an eight-drawer workshop paradigm."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "experiments/yolo/sidequest_semantic_standalone_words_six_hundred_eighth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOTS = {
    "SEQUENCE": ["OL", "OT"],
    "OBJECT_MATERIAL": ["Y", "HO", "O", "OR"],
    "QUANTITY_STAGE": ["AIIN", "AIN", "DA", "IIN"],
    "SOURCE_PATH_TARGET": ["AR", "AIR", "CKH", "AL", "OS"],
    "ACTION": ["CFH", "CH", "CHD", "CHK", "K", "L", "LD", "LSH", "OK", "P", "R", "S", "SH", "SHED", "SOLK", "T", "TALAM"],
    "GRADE": ["E", "EE", "EEE"],
    "STATE": ["CTH"],
    "CLOSE": ["DY"],
}


SLOT_INFO = {
    "SEQUENCE": ("FOLGE", "wann oder weiter?", "ordnet Folge oder Fortsetzung"),
    "OBJECT_MATERIAL": ("GEGENSTAND", "was wird bearbeitet?", "setzt Posten, Gabe, Gang oder Ansatz"),
    "QUANTITY_STAGE": ("MENGE_STUFE", "wie viel oder welche Stufe?", "setzt Maß, Portion, Ordnung oder Stufe"),
    "SOURCE_PATH_TARGET": ("ADRESSE", "woher, wodurch oder wohin?", "setzt Quelle, Lauf, Durchlass, Ziel oder Fach"),
    "ACTION": ("HANDLUNG", "was tun?", "führt die Werkstatthandlung aus"),
    "GRADE": ("GRAD", "wie kurz, lang oder vollständig?", "modifiziert die Ausführung"),
    "STATE": ("ZUSTAND", "bis wann?", "fordert Bereitschaft"),
    "CLOSE": ("SCHLUSS", "ist der Schritt abgeschlossen?", "schließt die lizenzierte Karte"),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    words = read_tsv(SOURCE_DIR / "SIX_HUNDRED_EIGHTH_THIRTY_SEVEN_SEMANTIC_WORDS.tsv")
    cards = read_tsv(SOURCE_DIR / "SIX_HUNDRED_EIGHTH_173_CONSOLIDATED_CARD_DICTIONARY.tsv")
    events = read_tsv(SOURCE_DIR / "SIX_HUNDRED_EIGHTH_381_CONSOLIDATED_EVENT_EDITION.tsv")
    statements = read_tsv(SOURCE_DIR / "SIX_HUNDRED_EIGHTH_116_CONSOLIDATED_STATEMENTS.tsv")

    slot_by_component = {component: slot for slot, components in SLOTS.items() for component in components}
    word_by_component = {row["canonical_component"]: row for row in words}

    drawer_rows = []
    for order, (slot, components) in enumerate(SLOTS.items(), 1):
        label, question, use = SLOT_INFO[slot]
        drawer_rows.append({
            "drawer_no": order,
            "slot": slot,
            "spoken_label_de": label,
            "master_question_de": question,
            "workshop_use_de": use,
            "semantic_components": "|".join(components),
            "spoken_words_de": "|".join(word_by_component[component]["spoken_workshop_word_de"] for component in components),
            "word_count": len(components),
        })

    paradigm_words = []
    for row in words:
        component = row["canonical_component"]
        slot = slot_by_component[component]
        label, question, use = SLOT_INFO[slot]
        paradigm_words.append({
            **row,
            "paradigm_slot": slot,
            "slot_label_de": label,
            "master_question_de": question,
            "slot_use_de": use,
            "slot_mates": "|".join(SLOTS[slot]),
        })

    card_rows = []
    for row in cards:
        components = row["semantic_component_parse"].split("+")
        slots = [slot_by_component[component] for component in components]
        slot_signature = ">".join(slots)
        present = set(slots)
        supplied = []
        if "OBJECT_MATERIAL" not in present:
            supplied.append("OBJECT_FROM_IMAGE_OR_ACTIVE_ITEM")
        if "SOURCE_PATH_TARGET" not in present:
            supplied.append("ADDRESS_FROM_OWNER_OR_CURRENT_STATION")
        if "ACTION" not in present:
            supplied.append("NONACTION_ARGUMENT_OR_STATE_CARD")
        card_rows.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "graphic_component_parse": row["component_parse"],
            "semantic_component_parse": row["semantic_component_parse"],
            "consolidated_short_default_de": row["consolidated_short_default_de"],
            "component_count": row["component_count"],
            "slot_signature": slot_signature,
            "distinct_slots": len(present),
            "repeated_slot": "YES" if len(present) < len(slots) else "NO",
            "silent_fill_needed": "|".join(supplied) if supplied else "NONE",
            "occurrences": row["occurrences"],
            "records": row["records"],
            "composition_status": row["composition_status"],
        })
    card_by_id = {row["card_no"]: row for row in card_rows}

    signature_cards: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in card_rows:
        signature_cards[row["slot_signature"]].append(row)
    signature_rows = []
    for signature, rows in sorted(signature_cards.items(), key=lambda item: (-sum(int(row["occurrences"]) for row in item[1]), item[0])):
        signature_rows.append({
            "slot_signature": signature,
            "card_types": len(rows),
            "events": sum(int(row["occurrences"]) for row in rows),
            "card_ids": "|".join(row["card_no"] for row in rows),
            "example_surfaces": "|".join(str(row["surfaces"]) for row in rows[:5]),
            "example_short_defaults_de": " | ".join(str(row["consolidated_short_default_de"]) for row in rows[:5]),
            "teaching_formula_de": " → ".join(SLOT_INFO[slot][0] for slot in signature.split(">")),
        })

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        statement_events = events_by_statement[row["statement_id"]]
        signatures = [card_by_id[event["card_no"]]["slot_signature"] for event in statement_events]
        slot_counts = Counter(slot for signature in signatures for slot in signature.split(">"))
        statement_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_de": row["owner_de"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "card_slot_signatures": " | ".join(signatures),
            "sequence_slots": slot_counts["SEQUENCE"],
            "object_slots": slot_counts["OBJECT_MATERIAL"],
            "quantity_slots": slot_counts["QUANTITY_STAGE"],
            "address_slots": slot_counts["SOURCE_PATH_TARGET"],
            "action_slots": slot_counts["ACTION"],
            "grade_slots": slot_counts["GRADE"],
            "state_slots": slot_counts["STATE"],
            "close_slots": slot_counts["CLOSE"],
            "concrete_case_expansion_de": row["concrete_case_expansion_de"],
        })

    write_tsv(HERE / "SIX_HUNDRED_NINTH_EIGHT_SLOT_DRAWERS.tsv", drawer_rows, list(drawer_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_NINTH_THIRTY_SEVEN_WORD_PARADIGM.tsv", paradigm_words, list(paradigm_words[0]))
    write_tsv(HERE / "SIX_HUNDRED_NINTH_173_CARD_SLOT_PARSE.tsv", card_rows, list(card_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_NINTH_SLOT_SIGNATURE_INVENTORY.tsv", signature_rows, list(signature_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_NINTH_116_STATEMENT_SLOT_EDITION.tsv", statement_rows, list(statement_rows[0]))

    report = f"""# Sechshundertneunte Runde: das Acht-Schubladen-Paradigma

## Ergebnis

Die 37 Bedeutungswörter passen vollständig in acht Lehrschubladen:

```text
1 FOLGE          2 Wörter   – DANACH, FORTSETZEN
2 GEGENSTAND     4 Wörter   – DIES, GABE, GANG, ANSATZ
3 MENGE/STUFE    4 Wörter   – MASS, PORTION, ZWEIT, STUFE
4 ADRESSE        5 Wörter   – QUELLE, LAUF, DURCHLASS, ZIEL, FACH
5 HANDLUNG      17 Wörter   – AUSWRINGEN ... VERWAHREN
6 GRAD           3 Wörter   – KURZ, LANG, VOLL
7 ZUSTAND        1 Wort     – BEREIT
8 SCHLUSS        1 Wort     – SCHLUSS
```

## Wie der Lehrmeister fragt

Eine Karte wird nicht buchstabiert, sondern abgefragt:

```text
Wann/weiter? – Was? – Wie viel/welche Stufe?
Woher/durch was/wohin? – Was tun? – Wie lange?
Bis wann? – Fertig?
```

Nicht jede Karte füllt jede Schublade. Bildbesitzer und aktiver Fall liefern gewöhnlich Gegenstand und Ort; deshalb können kurze Karten nur `MASS`, `FORTSETZEN` oder `DIES` heißen.

## Die 173 Karten

Alle 173 Karten haben nun eine Slot-Signatur. Es gibt {len(signature_rows)} tatsächlich verwendete Signaturen. Wiederholte Slots sind erlaubt: zwei Handlungen bilden eine Kette, zwei DIES-Positionen nehmen denselben Posten wieder auf, und zwei Grade können einen gelernten Rhythmus bilden.

## Warum das Komposition vorhersagbar macht

Eine neue Karte darf nur aus Wörtern derselben acht Schubladen gebaut werden. Der Wert jedes Teils bleibt gleich; nur Reihenfolge und lokale Auslassung erzeugen die Werkstattphrase. Artikel, Pflanze, Wasser, Körperstelle oder Sternname werden nicht in die Schubladen hineinerfunden.

## Nächster Schritt

Als nächstes nehmen wir die häufigsten Slot-Signaturen und erzeugen daraus konkrete, bisher nicht benutzte Kartenkombinationen. Dann prüfen wir ausschließlich auf den zehn Seiten, ob entsprechende Oberflächen bereits vorhanden sind oder ob das Modell falsche Formen vorhersagt.
"""
    (HERE / "SIX_HUNDRED_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "semantic_words": len(paradigm_words),
        "drawers": len(drawer_rows),
        "cards": len(card_rows),
        "slot_signatures": len(signature_rows),
        "statements": len(statement_rows),
        "events": sum(int(row["event_count"]) for row in statement_rows),
        "drawer_word_counts": {row["slot"]: int(row["word_count"]) for row in drawer_rows},
        "decision": "EIGHT_DRAWER_WORKSHOP_PARADIGM_COVERS_ALL_PROSE_CARDS",
    }
    (HERE / "SIX_HUNDRED_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
