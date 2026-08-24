#!/usr/bin/env python3
"""Separate standalone workshop words from graphic aliases and specialist atoms."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SHORT_DIR = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"
SCOPE_DIR = ROOT / "experiments/yolo/sidequest_semantic_long_card_scope_six_hundred_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


STANDALONE_STATUS = {
    "PROC003": ("PORTABLE_STANDALONE_WORD", "QUELLE", "häufige Quellkarte mit mehreren Schreibformen"),
    "PROC005": ("LEARNED_SPECIALIST_WORD", "FACH", "einmalige, aber klar abgegrenzte Arbeitsfachkarte"),
    "PROC009": ("PORTABLE_STANDALONE_WORD", "MASS", "breiteste selbständige Mengenkarte über alle elf Records"),
    "PROC013": ("PORTABLE_STANDALONE_WORD", "FORTSETZEN", "gemeinsame Fortsetzungskarte mit vielen Oberflächen"),
    "PROC016": ("PORTABLE_STANDALONE_WORD", "ANSATZ", "selbständige Zubereitungskarte über Herbal und Biological"),
    "PROC019": ("PORTABLE_STANDALONE_WORD", "DIES", "selbständige laufende-Posten-Karte mit vielen Allographen"),
    "PROC034": ("GRAPHIC_ALIAS_OF_OL", "FORTSETZEN", "zweite exakte Karte, aber kein zweiter Wert; lokale OL-Fortsetzungsform"),
    "PROC043": ("LEARNED_SPECIALIST_WORD", "VERWAHREN", "einmalige fachliche Verwahrkarte"),
    "PROC052": ("PORTABLE_STANDALONE_WORD", "GABE", "selbständige Einsatz-/Materialgabe auf H5"),
    "PROC055": ("PORTABLE_STANDALONE_WORD", "ZIEL", "breite Zielkarte über Herbal und Biological"),
    "PROC058": ("PORTABLE_STANDALONE_WORD", "HALTEN", "selbständige Handlung, sonst produktiv eingebettet"),
    "PROC072": ("PORTABLE_STANDALONE_WORD", "FUEHREN", "selbständige Weg-/Transferhandlung"),
    "PROC115": ("GRAPHIC_ALIAS_OF_OL", "FORTSETZEN", "LS/WEITER ist die kurze graphische OL-Fortsetzungsalias"),
    "PROC156": ("PORTABLE_STANDALONE_WORD", "PORTION", "selbständige Portionkarte, sonst produktiv eingebettet"),
}


SPECIALISTS = {
    "CFH": ("AUSWRINGEN", "TRUE_SPECIALIST_ACTION", "nur H3; handwerklich klare Tuch-/Presshandlung"),
    "S": ("TEILEN", "TRUE_SPECIALIST_ACTION", "nur B2; abgeteilte lokale Charge"),
    "LD": ("BEFESTIGEN", "TRUE_SPECIALIST_ACTION", "nur B4; Auflage oder Einsatz festsetzen"),
    "DA": ("ZWEIT", "LEARNED_ORDINAL_MARK", "keine selbständige Karte; markiert die zweite Stufe"),
    "IIN": ("STUFE", "TRUE_SPECIALIST_STATE", "wenige Karten, aber wiederkehrende Stufenfunktion"),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_THIRTY_EIGHT_ONE_WORD_COMPONENTS.tsv")
    cards = read_tsv(SCOPE_DIR / "SIX_HUNDRED_SEVENTH_173_RECITATION_DICTIONARY.tsv")
    events = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    statements = read_tsv(SHORT_DIR / "SIX_HUNDRED_SIXTH_116_SHORT_STATEMENT_EDITION.tsv")

    standalone = []
    for row in cards:
        if int(row["component_count"]) != 1:
            continue
        status, word, reason = STANDALONE_STATUS[row["card_no"]]
        standalone.append({
            "card_no": row["card_no"],
            "surfaces": row["surfaces"],
            "graphic_component": row["component_parse"],
            "working_status": status,
            "spoken_word_de": word,
            "occurrences": row["occurrences"],
            "sections": row["sections"],
            "records": row["records"],
            "reason_de": reason,
            "adds_new_semantic_word": "NO" if status.startswith("GRAPHIC_ALIAS") else "YES",
        })

    specialists = []
    component_by_name = {row["component"]: row for row in components}
    for component, (word, status, reason) in SPECIALISTS.items():
        source = component_by_name[component]
        host_cards = [row for row in cards if component in row["component_parse"].split("+")]
        specialists.append({
            "component": component,
            "spoken_word_de": word,
            "working_status": status,
            "host_card_ids": "|".join(row["card_no"] for row in host_cards),
            "host_surfaces": "|".join(row["surfaces"] for row in host_cards),
            "card_types": source["card_types"],
            "events": source["events"],
            "reason_de": reason,
            "standalone_card_attested": "NO",
        })

    semantic_components = []
    for row in components:
        if row["component"] == "LS":
            continue
        aliases = "LS" if row["component"] == "OL" else "NONE"
        word = "FORTSETZEN" if row["component"] == "OL" else row["short_workshop_word_de"]
        semantic_components.append({
            "semantic_word_no": f"W{len(semantic_components) + 1:02d}",
            "canonical_component": row["component"],
            "graphic_component_aliases": aliases,
            "spoken_workshop_word_de": word,
            "sentence_role": row["sentence_role"],
            "teaching_rule_de": (
                "OL und LS gleich als FORTSETZEN sprechen."
                if row["component"] == "OL"
                else row["teaching_rule_de"]
            ),
        })
    semantic_word = {row["canonical_component"]: row["spoken_workshop_word_de"] for row in semantic_components}
    semantic_word["LS"] = semantic_word["OL"]

    revised_cards = []
    for row in cards:
        graphic_parts = row["component_parse"].split("+")
        semantic_parts = ["OL" if part == "LS" else part for part in graphic_parts]
        short = "·".join(semantic_word[part] for part in semantic_parts)
        revised_cards.append({
            **row,
            "semantic_component_parse": "+".join(semantic_parts),
            "consolidated_short_default_de": short,
            "graphic_alias_used": "LS_TO_OL" if "LS" in graphic_parts else "NONE",
        })
    revised_by_id = {row["card_no"]: row for row in revised_cards}

    revised_events = []
    for row in events:
        card = revised_by_id[row["card_no"]]
        revised_events.append({
            **row,
            "semantic_component_parse": card["semantic_component_parse"],
            "consolidated_short_default_de": card["consolidated_short_default_de"],
            "graphic_alias_used": card["graphic_alias_used"],
        })

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        events_by_statement[row["statement_id"]].append(row)
    revised_statements = []
    for row in statements:
        sequence = events_by_statement[row["statement_id"]]
        revised_statements.append({
            **row,
            "consolidated_card_sequence_de": " ".join(item["consolidated_short_default_de"] for item in sequence),
            "ls_alias_events": "|".join(item["event_id"] for item in sequence if item["graphic_alias_used"] == "LS_TO_OL") or "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_FOURTEEN_STANDALONE_CARD_AUDIT.tsv", standalone, list(standalone[0]))
    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_FIVE_SPECIALIST_ATOMS.tsv", specialists, list(specialists[0]))
    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_THIRTY_SEVEN_SEMANTIC_WORDS.tsv", semantic_components, list(semantic_components[0]))
    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_173_CONSOLIDATED_CARD_DICTIONARY.tsv", revised_cards, list(revised_cards[0]))
    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_381_CONSOLIDATED_EVENT_EDITION.tsv", revised_events, list(revised_events[0]))
    write_tsv(HERE / "SIX_HUNDRED_EIGHTH_116_CONSOLIDATED_STATEMENTS.tsv", revised_statements, list(revised_statements[0]))

    portable = [row for row in standalone if row["working_status"] == "PORTABLE_STANDALONE_WORD"]
    specialist_words = [row for row in standalone if row["working_status"] == "LEARNED_SPECIALIST_WORD"]
    aliases = [row for row in standalone if row["working_status"].startswith("GRAPHIC_ALIAS")]
    report = f"""# Sechshundertachte Runde: echte Einwortkarten und Spezialkerne

## Ergebnis

Von den 14 einteiligen Karten sind:

- **{len(portable)} portable selbständige Werkstattwörter**;
- **{len(specialist_words)} gelernte Fachwörter** (`FACH`, `VERWAHREN`);
- **{len(aliases)} graphische Fortsetzungsaliasse**, keine neuen Bedeutungen.

Die zwei Aliasse sind PROC034 (`dchol|schol`) und PROC115 (`ls`). Beide werden wie OL als **FORTSETZEN** gesprochen. Dadurch schrumpft die gesprochene Grundliste von 38 graphischen Komponenten auf **37 Bedeutungswörter**.

## Die zwölf selbständigen Wörter

```text
QUELLE   FACH      MASS       FORTSETZEN
ANSATZ   DIES      VERWAHREN  GABE
ZIEL     HALTEN    FUEHREN    PORTION
```

FACH und VERWAHREN sind echte gelernte Fachkarten, obwohl sie auf den zehn Seiten nur einmal vorkommen. Sie bleiben kurz und passen an klar abgegrenzte Arbeitsplätze.

## Die fünf Spezialkerne

```text
CFH  AUSWRINGEN   – H3-Tuch-/Presshandlung
S    TEILEN       – lokale Chargenteilung
LD   BEFESTIGEN   – B4-Auflage oder Einsatz
DA   ZWEIT        – gelernte Ordnungsmarke
IIN  STUFE        – gelernter Zustands-/Gradkern
```

Sie brauchen keine freien Ganzsatzbedeutungen. DA ist dabei kein selbständiges Wortzeichen, sondern eine Ordnungsmarke vor STUFE.

## Praktische Folge

Ein Lehrling lernt nun 37 Bedeutungswörter, aber 38 graphische Komponenten, weil LS nur eine Kurzform von OL/FORTSETZEN ist. Das ist genau die erwartete Mischung aus produktiven Fachkürzeln, lokalen Allographen und wenigen Fachkarten.

## Nächster Schritt

Als nächstes ordnen wir die 37 Wörter in eine kleine Paradigmentafel: Material/Objekt, Menge, Quelle/Ziel, Folge, Handlung, Grad/Zustand und Schluss. Danach prüfen wir, welche Kartenkombinationen diese Slots vollständig vorhersagen.
"""
    (HERE / "SIX_HUNDRED_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "graphic_components": 38,
        "semantic_words": len(semantic_components),
        "standalone_cards": len(standalone),
        "portable_standalone_words": len(portable),
        "learned_specialist_words": len(specialist_words),
        "graphic_alias_cards": len(aliases),
        "specialist_atoms": len(specialists),
        "cards": len(revised_cards),
        "events": len(revised_events),
        "statements": len(revised_statements),
        "decision": "THIRTY_SEVEN_SEMANTIC_WORDS_PLUS_ONE_GRAPHIC_ALIAS_COMPONENT",
    }
    (HERE / "SIX_HUNDRED_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
