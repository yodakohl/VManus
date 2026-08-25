#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PAIR_DIR = ROOT / "sidequest_semantic_herbal_biological_process_pairing_eight_hundred_sixty_sixth"
BIO_DIR = ROOT / "sidequest_semantic_three_biological_process_atlas_eight_hundred_sixty_fifth"
PAIRINGS = PAIR_DIR / "EIGHT_HUNDRED_SIXTY_SIXTH_6_SELECTED_PROCESS_PAIRINGS.tsv"
PREPARATIONS = PAIR_DIR / "EIGHT_HUNDRED_SIXTY_SIXTH_4_HERBAL_PREPARATION_ARCHETYPES.tsv"
BIO_RECORDS = BIO_DIR / "EIGHT_HUNDRED_SIXTY_FIFTH_6_RECORD_PROCESS_PROFILES.tsv"
BIO_EVENTS = BIO_DIR / "EIGHT_HUNDRED_SIXTY_FIFTH_281_CARD_BIOLOGICAL_ATLAS.tsv"
PREFIX = "EIGHT_HUNDRED_SIXTY_SEVENTH"

SLOTS = {
    "f10r": ("P1", "WAESSRIGE_BASIS", "wässrige Basis mit offenem Nebenansatz"),
    "f11r": ("P2", "AUFGENOMMENER_AUSZUG", "aufgenommener Auszug"),
    "f55v": ("P3", "GEMESSENER_WARMER_ANSATZ", "gemessener warmer Ansatz"),
    "f56r": ("P4", "ZUTATEN_DURCHLASS_ANSATZ", "zutatenreicher Durchlassansatz"),
}

ENTRY_PURPOSES = {
    "B1": "gemeinsame Beckenfolge speisen und abschnittsweise weiterführen",
    "B2": "fünf Bildstationen nacheinander bemessen, durchlassen und halten",
    "B3": "Auszug an Gefäß- und Paarstationen verteilen und wieder abführen",
    "B4": "gemessene Portionen übertragen und an gekoppelten Stellen halten",
    "B5": "einen kurzen gemessenen Durchlassnachtrag ausführen",
    "B6": "einen offenen Posten an der bezeichneten Stelle einstellen",
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
    pairings = read(PAIRINGS)
    preparations = {row["page"]: row for row in read(PREPARATIONS)}
    records = {row["record"]: row for row in read(BIO_RECORDS)}
    events = read(BIO_EVENTS)

    slot_rows = []
    for page, (slot, slot_class, spoken_name) in SLOTS.items():
        row = preparations[page]
        slot_rows.append(
            {
                "product_slot": slot,
                "herbal_page": page,
                "visible_process_class": slot_class,
                "spoken_workshop_name_de": spoken_name,
                "card_visible_information_de": row["supplies_de"],
                "picture_supplied_information_de": "abgebildete Pflanze als Besitzer",
                "master_supplied_information_de": "konkreter Pflanzenname; genaue Stoffidentität; reale Maß- und Zeiteinheit",
                "exact_product_name_visible": "NO",
            }
        )

    entry_rows = []
    for index, pairing in enumerate(pairings, start=1):
        record = pairing["biological_record"]
        page = pairing["primary_preparation_page"]
        slot, slot_class, spoken_name = SLOTS[page]
        profile = records[record]
        subset = [row for row in events if row["record"] == record]
        owners = []
        for row in subset:
            if row["owner_de"] not in owners:
                owners.append(row["owner_de"])
        entry_rows.append(
            {
                "entry_id": f"WH{index:02d}",
                "what_slot": slot,
                "what_class": slot_class,
                "what_spoken_de": spoken_name,
                "how_record": record,
                "how_page": profile["page"],
                "how_purpose_de": ENTRY_PURPOSES[record],
                "visible_owner_sequence_de": " -> ".join(owners),
                "statements": profile["statements"],
                "cards": profile["cards"],
                "closed_cells": profile["closed_cells"],
                "visible_card_layer_de": "Reihenfolge; Maß-/Stufenprompts; Quelle/Ziel; Operation; Halten; Zellschluss",
                "visible_picture_layer_de": "Pflanzenbesitzer und lokale Anwendungs-/Gefäßstation",
                "required_master_layer_de": "konkretes Produkt; Körper-/Sachreferent; Maßwert; Dauerwert; gewünschtes Ergebnis",
                "readable_instruction_de": f"Nimm {slot} ({spoken_name}). Arbeitsauftrag: {ENTRY_PURPOSES[record]}.",
                "exact_product_identity": "UNNAMED",
            }
        )

    teaching_rows = [
        {"step": 1, "scribe_action_de": "Herbal-Bildbesitzer feststellen", "input_channel": "PICTURE", "output": "aktive Pflanzenquelle"},
        {"step": 2, "scribe_action_de": "sichtbare Kartenfolge als Zubereitungsart lesen", "input_channel": "CARDS", "output": "P1/P2/P3/P4"},
        {"step": 3, "scribe_action_de": "konkreten Produktnamen aus Meisterwissen ergänzen", "input_channel": "MASTER_OR_MEMORY", "output": "benannter Werkstattbestand"},
        {"step": 4, "scribe_action_de": "Biological-Bildstation feststellen", "input_channel": "PICTURE", "output": "lokaler Besitzer/Zielbereich"},
        {"step": 5, "scribe_action_de": "kurze Biological-Zellen der Reihe nach ausführen", "input_channel": "CARDS", "output": "Anwendungsschritte"},
        {"step": 6, "scribe_action_de": "reale Maß-, Dauer- und Ergebniswerte einsetzen", "input_channel": "MASTER_OR_MEMORY", "output": "vollständig ausführbarer Auftrag"},
    ]

    information_rows = [
        {"information": "Zubereitungsart", "picture": "PARTIAL", "cards": "YES", "master": "NO", "current_readability": "P1-P4 lesbar"},
        {"information": "konkrete Pflanze", "picture": "YES", "cards": "NO", "master": "YES_FOR_NAME", "current_readability": "Bildbesitzer, Name unbekannt"},
        {"information": "konkretes Produkt", "picture": "NO", "cards": "NO", "master": "YES", "current_readability": "unbenannt"},
        {"information": "Anwendungsstation", "picture": "YES", "cards": "PARTIAL", "master": "OPTIONAL", "current_readability": "lokale Station lesbar"},
        {"information": "Arbeitsreihenfolge", "picture": "PARTIAL", "cards": "YES", "master": "NO", "current_readability": "lesbar"},
        {"information": "Maß- und Dauerwert", "picture": "NO", "cards": "CATEGORY_ONLY", "master": "YES", "current_readability": "Kategorie, nicht Wert"},
        {"information": "gewünschtes Ergebnis", "picture": "PARTIAL", "cards": "STATE_ONLY", "master": "YES", "current_readability": "Zustandsstufe, nicht Sachziel"},
    ]

    write(f"{PREFIX}_4_UNNAMED_PRODUCT_SLOTS.tsv", slot_rows, ["product_slot", "herbal_page", "visible_process_class", "spoken_workshop_name_de", "card_visible_information_de", "picture_supplied_information_de", "master_supplied_information_de", "exact_product_name_visible"])
    write(f"{PREFIX}_6_WHAT_HOW_ENTRIES.tsv", entry_rows, ["entry_id", "what_slot", "what_class", "what_spoken_de", "how_record", "how_page", "how_purpose_de", "visible_owner_sequence_de", "statements", "cards", "closed_cells", "visible_card_layer_de", "visible_picture_layer_de", "required_master_layer_de", "readable_instruction_de", "exact_product_identity"])
    write(f"{PREFIX}_6_STEP_APPRENTICE_USE.tsv", teaching_rows, ["step", "scribe_action_de", "input_channel", "output"])
    write(f"{PREFIX}_INFORMATION_CHANNELS.tsv", information_rows, ["information", "picture", "cards", "master", "current_readability"])

    lines = ["# WHAT → HOW: kompaktes Werkstattblatt", ""]
    for row in entry_rows:
        lines.extend(
            [
                f"## {row['entry_id']}: {row['what_slot']} → {row['how_record']}",
                "",
                str(row["readable_instruction_de"]),
                "",
                f"Bildfolge: {row['visible_owner_sequence_de']}.",
                f"Umfang: {row['statements']} {'Zelle' if int(row['statements']) == 1 else 'Zellen'}, {row['cards']} Karten, {row['closed_cells']} Schlüsse.",
                "Der Produktname sowie reale Maß- und Dauerwerte werden vom Meister ergänzt.",
                "",
            ]
        )
    lines.extend(
        [
            "## Was der zweite Schreiber wirklich lernen muss",
            "",
            "Die Karten tragen die Prozessklasse und Reihenfolge; die Bilder tragen Besitzer",
            "und Stationen. Der nicht sichtbare Rest ist klein, aber entscheidend: Produktname,",
            "konkreter Referent sowie Maß-, Dauer- und Ergebniswerte. Damit wäre das System für",
            "eine kleine Werkstatt leicht lernbar, ohne für einen Außenstehenden selbstlesend zu sein.",
        ]
    )
    (HERE / f"{PREFIX}_WHAT_HOW_WORKSHOP_LEAF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    channel_counts = Counter(row["input_channel"] for row in teaching_rows)
    summary = {
        "status": "PASS",
        "decision": "WHAT_HOW_WORKFLOW_IS_TEACHABLE_WITH_FOUR_UNNAMED_PRODUCT_SLOTS",
        "product_slots": len(slot_rows),
        "what_how_entries": len(entry_rows),
        "biological_records": len({row["how_record"] for row in entry_rows}),
        "visible_cards": sum(int(row["cards"]) for row in entry_rows),
        "visible_statements": sum(int(row["statements"]) for row in entry_rows),
        "master_dependent_information_types": sum(row["master"] in {"YES", "YES_FOR_NAME"} for row in information_rows),
        "teaching_steps_by_channel": dict(sorted(channel_counts.items())),
        "exact_named_products": 0,
        "new_card_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 867: executable WHAT-to-HOW workshop leaf\n\n"
        "Four unnamed product slots P1-P4 now connect the four Herbal preparation types\n"
        "to all six Biological records. The leaf is executable as a workshop aid: cards\n"
        "supply process type and order, while pictures supply plant and station owners.\n\n"
        "A second scribe still needs the master or oral teaching for concrete product names,\n"
        "body/object referents, numeric measure and duration values, and the intended material\n"
        "result. This is a plausible small-workshop division of labour: compact cards are\n"
        "learnable, but the book is not autonomous prose for an outsider.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
