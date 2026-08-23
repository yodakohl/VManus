#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"

# A compact, teachable semantic inventory.  The match keys locate real cards;
# they do not claim that the visible spelling is an alphabetic transcription.
COMPONENTS = [
    ("OK", "EINSETZEN", "den folgenden Posten in den laufenden Arbeitsgang setzen", ("OK_SET", "OK_ADD")),
    ("OL", "WEITER", "den bestehenden Gang fortsetzen", ("OL_CONTINUE",)),
    ("OT", "FOLGE", "zum folgenden Posten oder Schritt wechseln", ("OT_FOLLOW", "OT_NEXT")),
    ("AR", "QUELLE", "etwas von der angegebenen Quelle nehmen", ("AR_FROM", "AR_SOURCE")),
    ("AL", "ZIEL", "etwas an die angegebene Stelle bringen", ("AL_TO",)),
    ("L", "AB", "aus dem aktiven Posten heraus- oder abführen", ("L_OUT", "LCH_WITHDRAW")),
    ("P", "ZU", "in einen lokalen Empfänger zuführen", ("P_IN",)),
    ("AIN", "PORTION", "eine abgegrenzte Teilmenge", ("AIN_PORTION",)),
    ("AIIN", "SOLLMASS", "das im Exemplar vorgeschriebene Maß", ("AIIN_MEASURE", "AIIN_TARGET_MEASURE")),
    ("IIN", "STUFE", "eine benannte Arbeits- oder Bearbeitungsstufe", ("IIN_TARGET_STAGE", "IIN_PORT_GRADE")),
    ("E", "KURZ", "kurz oder unmittelbar ausführen", ("GRADE_1", "E_SHORT")),
    ("EE", "LANG", "länger halten oder fortsetzen", ("GRADE_2", "EE_LONG", "EE_HOLD")),
    ("EEE", "VOLL", "bis zur vollen Stufe ausführen", ("GRADE_3", "EEE_FULL")),
    ("Y", "DIES", "den aktuell gemeinten Arbeitsposten bezeichnen", ("Y_CURRENT", "Y_ITEM", "CHY_ITEM")),
    ("DY", "SCHLUSS", "nur in einer lizenzierten Endkarte die Zelle schließen", ("DY_CLOSE", "CLOSE_EXACT", "TERMINAL_CLOSE")),
    ("OR", "ANSATZ", "den aktuell bereiteten Arbeitsansatz bezeichnen", ("OR_BATCH",)),
    ("HO", "ZUTAT", "eine weitere Zutat oder einen Materialteil einsetzen", ("HO_INGREDIENT",)),
    ("CHEO", "AUSZUG", "einen gewonnenen Auszug bezeichnen", ("CHEO_EXTRACT",)),
    ("AIR", "LAUFFLÜSSIGKEIT", "Flüssigkeit im sichtbaren oder gedachten Lauf", ("AIR_WATER",)),
    ("CHED", "ÜBERFÜHREN", "Material von einer Station in die nächste bringen", ("CHED_TRANSFER",)),
    ("CHD", "ÜBERFÜHREN", "kurze Allomorphie derselben Transferhandlung", ("CHD_TRANSFER", "CHD~CHED_TRANSFER")),
    ("CTH", "BEREIT", "einen Posten als vorbereitet oder bereit setzen", ("CTH_READY",)),
    ("SHED", "ABSETZEN", "ruhen und sich absetzen lassen", ("SHED_SETTLE",)),
    ("CHK", "WÄRMEN", "den Posten erwärmen oder warm halten", ("CHK_WARM",)),
    ("CKH", "DURCHLASS", "durch einen Gang oder eine Passage führen", ("CKH_THROUGH",)),
    ("CKHE", "SEIHEN", "durch einen trennenden Durchlass führen", ("CKHE_STRAIN",)),
    ("SOLK", "SAMMELN", "an einer lokalen Sammel- oder Auffangstelle halten", ("SOLK_COLLECT",)),
    ("LSH", "WASCHEN", "einen Wasch- oder Spülgang ausführen", ("LSH_WASH",)),
    ("TY", "TEIL", "einen Materialteil oder Rest bezeichnen", ("TY_PART",)),
]

FIELD_MODES = {
    "CH": ("GRUNDANSATZ", "einen neuen Grundposten oder eine Grundzubereitung eröffnen"),
    "D": ("MITNAHME", "einen bereits aktiven Posten in die nächste Zeile oder Zelle tragen"),
    "O": ("FORTSETZUNG", "am laufenden Ansatz weiterarbeiten"),
    "Q": ("TEILSCHRITT", "einen untergeordneten Arbeitsschritt aktivieren"),
    "S": ("ERGEBNIS", "Zustand, Ergebnis oder Nebenast eintragen"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def drawer(row: dict[str, str]) -> str:
    formula = row["component_formula"]
    value = row["current_value_de"]
    if row["component_class"] == "MEMORIZED_WHOLE_CARD":
        return "GANZKARTE"
    if "; Schluss" in value:
        return "ABSCHLUSS"
    if any(key in formula for key in ("AIN_", "AIIN_", "IIN_")):
        return "MENGE_STUFE"
    if any(key in formula for key in ("AL_TO", "AR_FROM", "AR_SOURCE", "L_OUT", "P_IN", "AIR_WATER", "CKH_THROUGH", "CKHE_STRAIN")):
        return "WEG_QUELLE_ZIEL"
    if any(key in formula for key in ("OT_FOLLOW", "OT_NEXT", "OL_CONTINUE")):
        return "REIHENFOLGE"
    if any(key in formula for key in ("GRADE_", "E_SHORT", "EE_", "EEE_", "CTH_READY", "SHED_SETTLE", "CHK_WARM", "SOLK_COLLECT")):
        return "ZUSTAND_DAUER"
    if any(key in formula for key in ("OR_BATCH", "HO_INGREDIENT", "CHEO_EXTRACT", "TY_PART")):
        return "STOFF_POSTEN"
    return "HANDLUNG_VERWEIS"


def main() -> None:
    dictionary = read(DICT)
    events = read(EVENTS)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["master_card_id"]].append(event)

    component_rows: list[dict[str, object]] = []
    covered_cards: set[str] = set()
    for rank, (symbol, word, instruction, keys) in enumerate(COMPONENTS, 1):
        cards = [row for row in dictionary if any(key in row["component_formula"] for key in keys)]
        covered_cards.update(row["master_card_id"] for row in cards)
        example_card = max(cards, key=lambda row: int(row["event_count"]))
        example_event = by_card[example_card["master_card_id"]][0]
        component_rows.append({
            "teaching_order": rank,
            "component": symbol,
            "atomic_value_de": word,
            "write_read_rule_de": instruction,
            "card_types": len(cards),
            "visible_events": sum(int(row["event_count"]) for row in cards),
            "example_card_id": example_card["master_card_id"],
            "example_surface": example_event["visible_surface"],
            "example_value_de": example_card["current_value_de"],
            "example_statement": example_event["statement_id"],
        })
    write(OUT / "TWO_HUNDRED_FOURTH_COMPONENT_LEXICON.tsv", component_rows)

    mode_rows: list[dict[str, object]] = []
    for mode, (name, rule) in FIELD_MODES.items():
        mode_events = [event for event in events if event["field_frame_mode"] == mode]
        example = mode_events[0]
        mode_rows.append({
            "field_mode": mode,
            "teaching_name_de": name,
            "write_read_rule_de": rule,
            "visible_events": len(mode_events),
            "field_count": len({event["field_id"] for event in mode_events}),
            "example_field": example["field_id"],
            "example_statement": example["statement_id"],
            "example_surface": example["visible_surface"],
        })
    write(OUT / "TWO_HUNDRED_FOURTH_FIVE_FIELD_MODES.tsv", mode_rows)

    whole_rows: list[dict[str, object]] = []
    for row in dictionary:
        if row["component_class"] != "MEMORIZED_WHOLE_CARD":
            continue
        occurrences = by_card[row["master_card_id"]]
        first = occurrences[0]
        whole_rows.append({
            "teaching_order": len(whole_rows) + 1,
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "learned_value_de": row["current_value_de"],
            "occurrences": len(occurrences),
            "records": row["records"],
            "example_event": first["event_id"],
            "example_statement": first["statement_id"],
            "copying_rule_de": "als unteilbare Ganzkarte aus dem Exemplar lernen",
        })
    write(OUT / "TWO_HUNDRED_FOURTH_22_WHOLE_CARD_DECK.tsv", whole_rows)

    index_rows: list[dict[str, object]] = []
    for row in dictionary:
        first = by_card[row["master_card_id"]][0]
        matched = [symbol for symbol, _, _, keys in COMPONENTS if any(key in row["component_formula"] for key in keys)]
        index_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "value_de": row["current_value_de"],
            "drawer": drawer(row),
            "learning_mode": "GANZKARTE_LERNEN" if row["component_class"] == "MEMORIZED_WHOLE_CARD" else "KOMPONENTEN_LESEN",
            "visible_components": "+".join(matched) if matched else "LOKALER_KARTENKERN",
            "formal_recipe": row["component_formula"],
            "example_event": first["event_id"],
            "example_statement": first["statement_id"],
            "event_count": row["event_count"],
        })
    write(OUT / "TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv", index_rows)

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "components": len(component_rows),
        "field_modes": len(mode_rows),
        "whole_cards": len(whole_rows),
        "cards": len(index_rows),
        "events": len(events),
        "cards_with_named_component": len(covered_cards),
        "cards_without_named_component": len(dictionary) - len(covered_cards),
        "drawer_counts": dict(Counter(row["drawer"] for row in index_rows)),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
