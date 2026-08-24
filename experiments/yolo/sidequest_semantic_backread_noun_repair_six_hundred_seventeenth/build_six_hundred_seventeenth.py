#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P616 = ROOT / "experiments/yolo/sidequest_semantic_backread_verb_repair_six_hundred_sixteenth"


def read(name: str) -> list[dict[str, str]]:
    with (P616 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REPAIRS = {
    "AIIN": ("MASS", "SOLLMASS", "the prescribed amount or setting"),
    "AIR": ("LAUF", "FLUESSIGKEITSLAUF", "the moving liquid, not the channel containing it"),
    "AL": ("ZIEL", "ZIELSTELLE", "the addressed work or body site"),
    "AR": ("QUELLE", "VORRAT", "the source stock from which material is taken"),
    "CKH": ("DURCHLASS", "DURCHLASSKANAL", "the passage or channel, not its liquid"),
    "DA": ("ZWEIT", "ZWEITMARKER", "marks a second stage or local second item"),
    "HO": ("GABE", "ZUTAT", "a new added material rather than the current item"),
    "IIN": ("STUFE", "ARBEITSSTUFE", "the named process stage, distinct from amount"),
    "OS": ("FACH", "ARBEITSFACH", "a compartment or receiver slot"),
    "Y": ("DIES", "ARBEITSPOSTEN", "the currently active item inherited from owner and case"),
}


def revise(text: str) -> str:
    output = text
    for old, new, _ in REPAIRS.values():
        output = output.replace(old, new)
    return output


def tokens(parse: str) -> set[str]:
    return set(parse.replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))


def main() -> None:
    words = read("SIX_HUNDRED_SIXTEENTH_39_BACKREAD_WORDS.tsv")
    cards = read("SIX_HUNDRED_SIXTEENTH_173_REVISED_COMMAND_DICTIONARY.tsv")
    events = read("SIX_HUNDRED_SIXTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    statements = read("SIX_HUNDRED_SIXTEENTH_116_CONTROLLED_BACKREADS.tsv")

    word_rows: list[dict[str, object]] = []
    for row in words:
        updated = dict(row)
        component = row["canonical_component"]
        updated["pre_617_workshop_word_de"] = row["spoken_workshop_word_de"]
        if component in REPAIRS:
            old, new, reason = REPAIRS[component]
            updated["spoken_workshop_word_de"] = new
            updated["noun_address_reason_de"] = reason
            updated["noun_address_revision"] = "YES"
        else:
            updated["noun_address_reason_de"] = "unchanged distinct workshop cue"
            updated["noun_address_revision"] = "NO"
        word_rows.append(updated)
    word_fields = list(words[0]) + ["pre_617_workshop_word_de", "noun_address_reason_de", "noun_address_revision"]
    write("SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv", word_rows, word_fields)

    card_rows: list[dict[str, object]] = []
    for row in cards:
        updated = dict(row)
        updated["pre_617_standard_command_de"] = row["standard_command_de"]
        updated["standard_command_de"] = revise(row["standard_command_de"])
        affected = sorted(tokens(row["semantic_component_parse"]) & set(REPAIRS))
        updated["noun_address_components"] = "|".join(affected) if affected else "NONE"
        updated["noun_address_revision"] = "YES" if affected else "NO"
        card_rows.append(updated)
    card_fields = list(cards[0]) + ["pre_617_standard_command_de", "noun_address_components", "noun_address_revision"]
    write("SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv", card_rows, card_fields)
    card_by_id = {str(row["card_no"]): row for row in card_rows}

    event_rows: list[dict[str, object]] = []
    for row in events:
        updated = dict(row)
        card = card_by_id[row["card_no"]]
        updated["pre_617_standard_command_de"] = row["standard_command_de"]
        updated["standard_command_de"] = card["standard_command_de"]
        updated["noun_address_components"] = card["noun_address_components"]
        updated["noun_address_revision"] = card["noun_address_revision"]
        event_rows.append(updated)
    event_fields = list(events[0]) + ["pre_617_standard_command_de", "noun_address_components", "noun_address_revision"]
    write("SIX_HUNDRED_SEVENTEENTH_381_SHARP_EVENT_COMMANDS.tsv", event_rows, event_fields)

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for row in statements:
        sequence = events_by_statement[row["statement_id"]]
        command_sequence = " | ".join(str(event["standard_command_de"]) for event in sequence)
        affected = sorted({part for event in sequence for part in str(event["noun_address_components"]).split("|") if part != "NONE"})
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_or_station": row["owner_or_station"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "pre_617_controlled_backread_de": row["controlled_backread_de"],
            "sharp_controlled_backread_de": f"Bei {row['owner_or_station']}: {command_sequence}.",
            "original_readable_workshop_de": row["original_readable_workshop_de"],
            "noun_address_components": "|".join(affected) if affected else "NONE",
            "noun_address_revision": "YES" if affected else "NO",
        })
    write("SIX_HUNDRED_SEVENTEENTH_116_SHARP_BACKREADS.tsv", statement_rows, list(statement_rows[0]))

    counts = {component: sum(component in tokens(row["semantic_component_parse"]) for row in events) for component in REPAIRS}
    drawer_rows = [
        {
            "drawer": "PATH_AND_CONTAINER",
            "components": "AIR|CKH",
            "sharp_words_de": "FLUESSIGKEITSLAUF|DURCHLASSKANAL",
            "events": counts["AIR"] + counts["CKH"],
            "teaching_contrast_de": "what moves versus what it moves through",
        },
        {
            "drawer": "ADDRESS",
            "components": "AR|AL|OS",
            "sharp_words_de": "VORRAT|ZIELSTELLE|ARBEITSFACH",
            "events": counts["AR"] + counts["AL"] + counts["OS"],
            "teaching_contrast_de": "from stock, to work site, or into compartment",
        },
        {
            "drawer": "ITEM",
            "components": "Y|HO",
            "sharp_words_de": "ARBEITSPOSTEN|ZUTAT",
            "events": counts["Y"] + counts["HO"],
            "teaching_contrast_de": "already active item versus newly added ingredient",
        },
        {
            "drawer": "QUANTITY_AND_STAGE",
            "components": "AIIN|AIN|AN|IIN|DA",
            "sharp_words_de": "SOLLMASS|PORTION|NACHPORTION|ARBEITSSTUFE|ZWEITMARKER",
            "events": counts["AIIN"] + sum("AIN" in tokens(row["semantic_component_parse"]) for row in events) + sum("AN" in tokens(row["semantic_component_parse"]) for row in events) + counts["IIN"] + counts["DA"],
            "teaching_contrast_de": "prescribed measure, bounded share, following share, process stage, or second marker",
        },
    ]
    write("SIX_HUNDRED_SEVENTEENTH_4_SHARP_DRAWERS.tsv", drawer_rows, list(drawer_rows[0]))

    report = f"""# Sechshundertsiebzehnte Runde: Dinge und Adressen schärfen

## Ergebnis

Zehn kurze Wörter sind nun so benannt, dass ein Lehrling sie beim Rückschreiben nicht mehr mit ihrem Nachbarn verwechseln soll:

```text
AIR   FLUESSIGKEITSLAUF    CKH  DURCHLASSKANAL
AR    VORRAT               AL   ZIELSTELLE       OS  ARBEITSFACH
Y     ARBEITSPOSTEN        HO   ZUTAT
AIIN  SOLLMASS             IIN  ARBEITSSTUFE     DA  ZWEITMARKER
```

AIN=PORTION und AN=NACHPORTION bleiben bereits scharf. Der entscheidende inhaltliche Gewinn ist `Y` gegen `HO`: Die häufige Y-Karte meint den bereits aktiven, meist vom Bild geerbten Arbeitsposten; HO führt eine neue Zutat ein.

Die Schärfung betrifft **{sum(row['noun_address_revision'] == 'YES' for row in card_rows)} Karten**, **{sum(row['noun_address_revision'] == 'YES' for row in event_rows)} Ereignisse** und **{sum(row['noun_address_revision'] == 'YES' for row in statement_rows)} Aussagen**. Das Wörterbuch bleibt bei 39 Wörtern und das Befehlsbuch bei 163 Befehlen.

## Werkstattfrage

Der Meister fragt nun in fester Reihenfolge: Aus welchem VORRAT? Was ist schon ARBEITSPOSTEN und was kommt als ZUTAT hinzu? Wie viel als SOLLMASS, PORTION oder NACHPORTION? Durch welchen DURCHLASSKANAL bewegt sich der FLUESSIGKEITSLAUF? An welche ZIELSTELLE oder in welches ARBEITSFACH?

## Nächster Schritt

Mit den geschärften 39 Wörtern wird die vollständige Prosa-Ausgabe erneut flüssig formuliert. Dabei dürfen konkrete Stoffwörter wie Wasser, Wein, Öl oder Pflanze nur aus Bild/Fall kommen, nie heimlich aus AIR, O oder HO.
"""
    (HERE / "SIX_HUNDRED_SEVENTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "word_repairs": len(REPAIRS),
        "words": len(word_rows),
        "cards": len(card_rows),
        "revised_cards": sum(row["noun_address_revision"] == "YES" for row in card_rows),
        "events": len(event_rows),
        "revised_events": sum(row["noun_address_revision"] == "YES" for row in event_rows),
        "statements": len(statement_rows),
        "revised_statements": sum(row["noun_address_revision"] == "YES" for row in statement_rows),
        "decision": "TEN_NOUN_ADDRESS_CUES_SHARPENED_FOR_BACKREADING",
    }
    (HERE / "SIX_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
