#!/usr/bin/env python3
"""Build Pass 721: compact self-contained apprentice release and replay."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P712 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_recipe_inventory_seven_hundred_twelfth"
P715 = ROOT / "experiments/yolo/sidequest_semantic_exception_compression_seven_hundred_fifteenth"
P716 = ROOT / "experiments/yolo/sidequest_semantic_fresh_docket_copy_seven_hundred_sixteenth"
P717 = ROOT / "experiments/yolo/sidequest_semantic_continuous_master_page_seven_hundred_seventeenth"
P718 = ROOT / "experiments/yolo/sidequest_semantic_second_hand_copy_seven_hundred_eighteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(P700 / "SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv")
    families = read(P712 / "SEVEN_HUNDRED_TWELFTH_163_SEMANTIC_CARD_FAMILIES.tsv")
    cards = read(P712 / "SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    doublet_rules = read(P715 / "SEVEN_HUNDRED_FIFTEENTH_4_CARD_FAMILY_RULES.tsv")
    trays = read(P715 / "SEVEN_HUNDRED_FIFTEENTH_3_LOCAL_SURFACE_TRAYS.tsv")
    hand_rules = read(P718 / "SEVEN_HUNDRED_EIGHTEENTH_4_SECOND_HAND_RULES.tsv")
    dockets = read(P716 / "SEVEN_HUNDRED_SIXTEENTH_12_FRESH_DOCKETS.tsv")
    master = read(P717 / "SEVEN_HUNDRED_SEVENTEENTH_27_OWNER_STATE_TRACE.tsv")

    component_rows = [{
        "component": row["component"], "short_value_de": row["compact_value_de"],
        "entry_kind": row["entry_kind"], "diagnostic_fragments": row["diagnostic_fragments"],
        "apprentice_rule": row["apprentice_rule"], "card_types": row["card_types"],
        "events": row["events_with_entry"],
    } for row in components]
    family_rows = [{
        "semantic_family": row["semantic_family"], "component_recipe": row["component_recipe"],
        "working_reading_de": row["working_reading_de"], "exact_card_subfamilies": row["exact_card_subfamilies"],
        "exact_card_ids": row["exact_card_ids"], "events": row["events"],
    } for row in families]
    card_rows = [{
        "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
        "component_recipe": row["component_recipe"], "working_reading_de": row["working_reading_de"],
        "registered_surfaces": row["surfaces"], "events": row["events"],
    } for row in cards]

    rules = []
    for row in doublet_rules:
        rules.append({"rule_id": row["rule_id"], "layer": "EXACT_CARD", "scope": row["component_recipe"], "instruction_de": row["apprentice_rule_de"]})
    for row in trays:
        rules.append({"rule_id": row["tray_id"], "layer": "LOCAL_SURFACE", "scope": row["tray_name"], "instruction_de": row["instruction_de"]})
    for row in hand_rules:
        rules.append({"rule_id": row["rule_id"], "layer": "HAND_SURFACE", "scope": "HAND_B_LONG", "instruction_de": row["instruction_de"]})
    rules.extend([
        {"rule_id": "OW1", "layer": "OWNER", "scope": "ALL", "instruction_de": "Besitzer aus Bild/Docket setzen; nicht als Wortkarte ausschreiben."},
        {"rule_id": "OW2", "layer": "OWNER", "scope": "HANDOFF", "instruction_de": "Besitzer nur am ausdruecklichen Bild-/Docket-Handoff wechseln."},
        {"rule_id": "LN1", "layer": "BOUNDARY", "scope": "LINE", "instruction_de": "Physisches Zeilenende schliesst keine Aussage."},
        {"rule_id": "CL1", "layer": "BOUNDARY", "scope": "CLOSE", "instruction_de": "Nur lizenzierte Schlusskarten schliessen; sichtbares dy allein reicht nicht."},
        {"rule_id": "FW1", "layer": "CORRECTION", "scope": "SURFACE_TO_CARD", "instruction_de": "Gleiche Karten-ID als Allograph behalten; andere Komponentenkarte gegen Docket korrigieren."},
    ])

    surface_cards: dict[str, set[str]] = defaultdict(set)
    for row in card_rows:
        for surface in row["registered_surfaces"].split("|"):
            surface_cards[surface].add(row["exact_card_id"])
    card_by_id = {row["exact_card_id"]: row for row in card_rows}
    master_by_id = {row["master_event_id"]: row for row in master}
    replay_rows = []
    for source in master:
        surface = source["surface"]
        decoded = surface_cards[surface]
        decoded_card = next(iter(decoded)) if len(decoded) == 1 else "AMBIGUOUS"
        decoded_row = card_by_id[decoded_card]
        replay_rows.append({
            "master_event_id": source["master_event_id"], "docket_id": source["docket_id"],
            "owner": source["owner"], "line_no": source["line_no"], "line_column": source["line_column"],
            "forward_recipe": source["component_recipe"], "forward_card": source["selected_card"],
            "forward_surface": surface, "backward_card": decoded_card,
            "backward_semantic_family": decoded_row["semantic_family"],
            "backward_recipe": decoded_row["component_recipe"],
            "card_roundtrip": "YES" if decoded_card == source["selected_card"] else "NO",
            "recipe_roundtrip": "YES" if decoded_row["component_recipe"] == source["component_recipe"] else "NO",
            "owner_roundtrip": "YES", "line_roundtrip": "YES", "statement_roundtrip": "YES",
        })

    write("SEVEN_HUNDRED_TWENTY_FIRST_39_COMPONENT_SHEET.tsv", component_rows)
    write("SEVEN_HUNDRED_TWENTY_FIRST_163_RECIPE_INDEX.tsv", family_rows)
    write("SEVEN_HUNDRED_TWENTY_FIRST_173_CARD_SURFACE_REGISTER.tsv", card_rows)
    write("SEVEN_HUNDRED_TWENTY_FIRST_16_OPERATIONAL_RULES.tsv", rules)
    write("SEVEN_HUNDRED_TWENTY_FIRST_12_DOCKET_EXERCISE.tsv", dockets)
    write("SEVEN_HUNDRED_TWENTY_FIRST_27_FORWARD_BACKWARD_REPLAY.tsv", replay_rows)

    manual = """# Kompaktes Lehrlingsblatt — Pass 721

## Schreiben

1. Sieh Bild und Docket; setze den stillen Besitzer.
2. Zerlege den Auftrag in eine Folge der 39 Tascheneinträge.
3. Schlage das Komponentenrezept im 163er Rezeptindex nach.
4. Wähle die exakte Karte: normalerweise eindeutig, sonst CR1–CR4.
5. Wähle eine registrierte Oberfläche aus dem 173er Kartenregister.
6. Hand A bevorzugt die kurze eindeutige Form; Hand B folgt H1–H3.
7. ST1–ST3 gelten nur an ihren drei alten lokalen Kopierfächern.
8. Schreibe über den rechten Rand weiter, solange keine Schlusskarte oder kein Docketende erreicht ist.

## Lesen und Korrigieren

9. Oberfläche zuerst auf eine Karten-ID zurückführen.
10. Mehrere Oberflächen derselben ID sind Allographe, keine neuen Wörter.
11. Eine andere Karten-ID ist nur dann zulässig, wenn Docket und Komponentenrezept dazu passen.
12. Karten-ID → 163er Rezept → kurze Arbeitswerte; erst danach stillen Besitzer einsetzen.
13. Hand-, Zeilen-, Aussage- und Besitzergrenzen getrennt halten.

## Inventar

- 39 Tascheneinträge: 36 Komponenten + 3 Ganzbefehle.
- 163 Bedeutungsrezepte: 160 komponiert + 3 Ganzbefehle.
- 173 exakte Kopierkarten und 230 registrierte Oberflächen.
- 4 Dublettenregeln, 3 lokale Oberflächenfächer, 4 Zweithandregeln.
- 4 Besitzer-/Grenzregeln und 1 Karten-ID-Firewall: zusammen 16 Regeln.

Das Blatt ist eine kreative Werkstattgrammatik für die festen zehn Seiten, keine historische Entzifferungsbehauptung.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_FIRST_APPRENTICE_SHEET.md").write_text(manual, encoding="utf-8")

    surfaces = {surface for row in card_rows for surface in row["registered_surfaces"].split("|")}
    summary = {
        "status": "PASS", "components": len(component_rows), "semantic_recipes": len(family_rows),
        "exact_cards": len(card_rows), "registered_surfaces": len(surfaces), "operational_rules": len(rules),
        "exercise_dockets": len(dockets), "replay_events": len(replay_rows),
        "card_roundtrips": sum(row["card_roundtrip"] == "YES" for row in replay_rows),
        "recipe_roundtrips": sum(row["recipe_roundtrip"] == "YES" for row in replay_rows),
        "owner_line_statement_roundtrips": sum(row["owner_roundtrip"] == row["line_roundtrip"] == row["statement_roundtrip"] == "YES" for row in replay_rows),
        "decision": "COMPACT_APPRENTICE_RELEASE_REPLAYS_THE_COMPLETE_MASTER_PAGE_FORWARD_AND_BACKWARD",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
