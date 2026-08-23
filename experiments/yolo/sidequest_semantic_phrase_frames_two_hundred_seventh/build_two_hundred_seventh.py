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
APP = ROOT / "experiments/yolo/sidequest_semantic_apprentice_dictionary_two_hundred_fourth"
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"
INDEX = APP / "TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv"

FRAME_NAMES = {
    ("MENGE_STUFE", "WEG_QUELLE_ZIEL", "ABSCHLUSS"): ("MENGE_ZUM_ZIEL_SCHLIESSEN", "Menge festlegen, an Quelle oder Ziel führen, Zelle schließen"),
    ("MENGE_STUFE", "HANDLUNG_VERWEIS", "ABSCHLUSS"): ("MENGE_BEARBEITEN_SCHLIESSEN", "Menge festlegen, am aktuellen Posten handeln, Zelle schließen"),
    ("HANDLUNG_VERWEIS", "MENGE_STUFE", "HANDLUNG_VERWEIS"): ("HANDLUNG_MASS_HANDLUNG", "Arbeitsgang eröffnen, Maß setzen, am Posten fortarbeiten"),
    ("MENGE_STUFE", "HANDLUNG_VERWEIS", "MENGE_STUFE"): ("MASS_POSTEN_FOLGEMASS", "Maß setzen, Posten behandeln, nächste Stufe angeben"),
    ("MENGE_STUFE", "WEG_QUELLE_ZIEL", "ZUSTAND_DAUER"): ("MENGE_ZIEL_ZUSTAND", "Menge zur Station führen und ihren Zustand setzen"),
    ("MENGE_STUFE", "WEG_QUELLE_ZIEL", "WEG_QUELLE_ZIEL"): ("MENGE_DURCH_ZWEI_STATIONEN", "Menge über Quelle, Durchlass oder Ziel weiterführen"),
    ("WEG_QUELLE_ZIEL", "MENGE_STUFE", "WEG_QUELLE_ZIEL"): ("QUELLE_MENGE_ZIEL", "von der Quelle eine Menge nehmen und zum Ziel führen"),
    ("MENGE_STUFE", "WEG_QUELLE_ZIEL", "MENGE_STUFE"): ("MENGE_ZIEL_FOLGEMASS", "Menge an der Station setzen und Folgegrad angeben"),
    ("WEG_QUELLE_ZIEL", "ZUSTAND_DAUER", "ABSCHLUSS"): ("WEG_ZUSTAND_SCHLIESSEN", "durch die Station führen, Zustand setzen, schließen"),
    ("REIHENFOLGE", "ZUSTAND_DAUER", "ABSCHLUSS"): ("FOLGE_ZUSTAND_SCHLIESSEN", "Folgeschritt wählen, Zustand setzen, schließen"),
}

LEARNED_CHAINS = [
    ("LC01", "H1-S001", ["MC071", "MC158", "MC055"], "Bildwurzel eröffnen und auf den daraus genommenen Posten beziehen"),
    ("LC02", "H1-S001", ["MC086", "MC159", "MC014"], "Teil in ein Aufnahmegefäß geben und Flüssigkeit zugießen"),
    ("LC03", "H2-S003", ["MC027", "MC080", "MC080"], "Zubereitungsgefäß mit einer wiederholten Ansatzfolge eröffnen"),
    ("LC04", "H3-S001", ["MC098", "MC049", "MC129", "MC111", "MC156", "MC119", "MC037"], "Kochgut ansetzen, auswringen, stehen lassen, nachseihen, Klarlauf kalt stellen"),
    ("LC05", "H5-S002", ["MC142", "MC131", "MC026", "MC099"], "vom vorigen Ansatz einen Zugabeposten nehmen, einsetzen und auftragen"),
    ("LC06", "H5-S003", ["MC114", "MC034", "MC122"], "Stängel mit weiterer Zutat kurz bearbeiten"),
    ("LC07", "B1-S002", ["MC016", "MC012", "MC157"], "am Anschluss einen Zusatz in denselben Ansatz geben"),
    ("LC08", "B1-S006", ["MC035", "MC012", "MC056"], "durchleiten, Zusatz eintragen, Ziel markieren"),
    ("LC09", "B1-S015", ["MC109", "MC005"], "Kurzteil einführen und die Zelle schließen"),
    ("LC10", "H4-S001", ["MC047", "MC148", "MC100"], "erste und zweite Portion bilden und kalt stellen"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    index = {row["master_card_id"]: row for row in read(INDEX)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    counts: Counter[tuple[str, str, str]] = Counter()
    examples: dict[tuple[str, str, str], tuple[str, list[dict[str, str]]]] = {}
    for statement_id, rows in by_statement.items():
        drawers = [index[row["master_card_id"]]["drawer"] for row in rows]
        for i in range(len(rows) - 2):
            frame = tuple(drawers[i:i + 3])
            counts[frame] += 1
            examples.setdefault(frame, (statement_id, rows[i:i + 3]))

    frame_rows: list[dict[str, object]] = []
    for order, (frame, (name, rule)) in enumerate(FRAME_NAMES.items(), 1):
        statement_id, example = examples[frame]
        frame_rows.append({
            "teaching_order": order,
            "frame_id": f"PF{order:02d}",
            "frame_name": name,
            "slot_1": frame[0],
            "slot_2": frame[1],
            "slot_3": frame[2],
            "occurrences": counts[frame],
            "write_read_rule_de": rule,
            "example_statement": statement_id,
            "example_cards": "|".join(row["master_card_id"] for row in example),
            "example_values_de": " | ".join(row["portable_value_de"] for row in example),
        })
    write(OUT / "TWO_HUNDRED_SEVENTH_TEN_PRODUCTIVE_PHRASE_FRAMES.tsv", frame_rows)

    chain_rows: list[dict[str, object]] = []
    for chain_id, statement_id, card_ids, reading in LEARNED_CHAINS:
        statement_cards = [row["master_card_id"] for row in by_statement[statement_id]]
        start = next(i for i in range(len(statement_cards) - len(card_ids) + 1) if statement_cards[i:i + len(card_ids)] == card_ids)
        chain_rows.append({
            "chain_id": chain_id,
            "statement_id": statement_id,
            "start_position": start + 1,
            "card_ids": "|".join(card_ids),
            "master_forms": " ".join(dictionary[card_id]["master_form"] for card_id in card_ids),
            "literal_values_de": " | ".join(dictionary[card_id]["current_value_de"] for card_id in card_ids),
            "learned_phrase_de": reading,
            "token_count": len(card_ids),
        })
    write(OUT / "TWO_HUNDRED_SEVENTH_TEN_LEARNED_PHRASE_CHAINS.tsv", chain_rows)

    covered_statements = {
        statement_id
        for statement_id, rows in by_statement.items()
        if any(tuple(index[row["master_card_id"]]["drawer"] for row in rows[i:i + 3]) in FRAME_NAMES for i in range(len(rows) - 2))
    }
    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "productive_frames": len(frame_rows),
        "productive_frame_occurrences": sum(int(row["occurrences"]) for row in frame_rows),
        "statements_touched_by_productive_frames": len(covered_statements),
        "learned_chains": len(chain_rows),
        "learned_chain_tokens": sum(int(row["token_count"]) for row in chain_rows),
        "statements": len(by_statement),
        "events": len(events),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
