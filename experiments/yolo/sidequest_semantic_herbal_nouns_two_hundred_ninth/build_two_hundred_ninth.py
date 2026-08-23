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
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"
STATEMENTS = BASE / "TWO_HUNDRED_THIRD_116_STATEMENT_COMPACT_EDITION.tsv"

OWNERS = {
    "H1": ("f10r", "PLANT_F10", "ganze Bildpflanze", "Wurzelstock|Blattreihen|offener Blütenkopf|Knospe", "MC071:Wurzel"),
    "H2": ("f10r", "PLANT_F10", "dieselbe ganze Bildpflanze", "Wurzelstock|Blattreihen|offener Blütenkopf|Knospe", "NONE"),
    "H3": ("f11r", "PLANT_F11", "ganze Bildpflanze", "Wurzelkrone|Stängelgruppe|Blätterdach|kleine Blütenköpfe", "NONE"),
    "H4": ("f55v", "PLANT_F55", "ganze Bildpflanze", "Wurzelsystem|große Blattmasse|Mittelachse|verzweigte Krone", "NONE"),
    "H5": ("f56r", "PLANT_F56", "ganze Bildpflanze", "Stängelsystem|dominanter Kopf|Nebenköpfe|Basalspross", "MC114:Stängel"),
}

NOUN_CARDS = {
    "MC071": ("PFLANZENTEIL", "DIRECT_VISIBLE", "Wurzelstock ist im f10r-Bild sichtbar"),
    "MC114": ("PFLANZENTEIL", "DIRECT_VISIBLE", "Stängelsystem ist im f56r-Bild sichtbar"),
    "MC086": ("MATERIALTEIL", "OWNER_INHERITED", "Teil der aktiven Bildpflanze oder Zubereitung"),
    "MC069": ("MATERIALTEIL", "OWNER_INHERITED", "folgender Teil des aktiven Pflanzenpostens"),
    "MC108": ("MATERIALTEIL", "OWNER_INHERITED", "kleiner verbleibender Teil"),
    "MC062": ("MATERIALTEIL", "OWNER_INHERITED", "Teil, der als Zugabe geführt wird"),
    "MC047": ("PORTION", "WORKSHOP_INFERRED", "erste abgegrenzte Portion"),
    "MC148": ("PORTION", "WORKSHOP_INFERRED", "zweite abgegrenzte Portion"),
    "MC072": ("PORTION", "WORKSHOP_INFERRED", "Anteil aus der laufenden Bereitung"),
    "MC170": ("PORTION", "WORKSHOP_INFERRED", "vorgeschriebene Portion"),
    "MC159": ("GEFÄSS_ORT", "WORKSHOP_INFERRED", "Empfänger für den ersten Pflanzenposten"),
    "MC027": ("GEFÄSS_ORT", "WORKSHOP_INFERRED", "Gefäß für die laufende Zubereitung"),
    "MC160": ("GEFÄSS_ORT", "WORKSHOP_INFERRED", "Ort zum Verwahren einer Portion"),
    "MC075": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "Auszug, der als Ansatz weitergeführt wird"),
    "MC080": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "neutraler laufender Ansatz"),
    "MC013": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "folgender Ansatz"),
    "MC157": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "derselbe fortgeführte Ansatz"),
    "MC098": ("ZUBEREITUNG_AUSZUG", "OWNER_INHERITED", "Material, das gekocht oder behandelt wird"),
    "MC049": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "flüssiger oder feuchter Arbeitsansatz"),
    "MC119": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "geklärter Ablauf oder Auszug"),
    "MC085": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "Auszug von der markierten Quelle"),
    "MC125": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "Ansatz mit einer weiteren Zutat"),
    "MC136": ("ZUBEREITUNG_AUSZUG", "WORKSHOP_INFERRED", "bereits bearbeiteter Quellauszug"),
    "MC014": ("ZUTAT_ZUGABE", "WORKSHOP_INFERRED", "Flüssigkeitszugabe ohne festgelegtes Medium"),
    "MC087": ("ZUTAT_ZUGABE", "WORKSHOP_INFERRED", "vorgeschriebene Zugabemenge"),
    "MC034": ("ZUTAT_ZUGABE", "OWNER_INHERITED", "weitere, lokal ergänzte Zutat"),
    "MC010": ("ZUTAT_ZUGABE", "WORKSHOP_INFERRED", "Zugabe an eine Zielstelle"),
    "MC131": ("ZUTAT_ZUGABE", "WORKSHOP_INFERRED", "aktuell gemeinter Zugabeposten"),
}

ARTICLES = {
    "H1": "Von der Bildpflanze die Wurzel nehmen. Einen Teil im Aufnahmegefäß vorbereiten, Flüssigkeit zugießen, den Folgeteil einsetzen, auf Sollmaß bringen und einen kleinen Rest belassen. Den ersten Posten weiterbearbeiten, im Folgegang weiterführen und bereit halten.",
    "H2": "Aus dem bereiten Auszugsansatz derselben Bildpflanze die nächste Charge ansetzen, den bereiten Folgeposten wählen und auf Sollmaß bringen. Folgeansatz und aktiven Ansatz weiterführen, davon die Sollmenge nehmen und die Folge beibehalten. Im Zubereitungsgefäß den Ansatz in der Bearbeitungsstufe bearbeiten und die vorgeschriebene Zugabemenge einsetzen.",
    "H3": "Aus dem Material der Bildpflanze ein Kochgut als Sudansatz bereiten, auswringen, eine Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen. Den weiteren Zugabeteil bereitlegen. Vom vorigen Ansatz diesen Posten weiterbearbeiten und auf Sollmaß bringen. Zum nächsten Posten wechseln, weiter einsetzen und bereit halten.",
    "H4": "Von der Bildpflanze einen Ansatz bemessen, auf Sollmaß in eine erste und zweite Portion teilen und abkühlen lassen. Die Sollmenge überführen und am Verwahrort ablegen. Eine Sollportion aus dem Quellauszug nehmen, länger bearbeiten und fertigstellen. Das Sollmaß am Ziel einsetzen und aus diesem Ansatz mit dem Bereitungsanteil die Folgezubereitung bilden.",
    "H5": "Von der Bildpflanze einen Zugabeansatz herstellen, eine weitere Zutat als Zielzugabe auf Sollmaß bringen und den Folgeansatz dorthin führen. Vom vorigen Ansatz den Zugabeposten nehmen, einsetzen und am Ziel auftragen. Den Stängel und eine weitere Zutat kurz bearbeiten und erneut einsetzen. Den Auszug einsetzen und am Ziel verteilen. Eine weitere Zutat mit dem bearbeiteten Quellauszug weiterbearbeiten und als Folgeanwendung führen. Zum nächsten Posten wechseln, kurz weiterbearbeiten und auf Sollmaß bringen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = [row for row in read(EVENTS) if row["record_unit_id"] in OWNERS]
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    statements = [row for row in read(STATEMENTS) if row["record_unit_id"] in OWNERS]
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["master_card_id"]].append(event)

    owner_rows: list[dict[str, object]] = []
    for record, (page, owner_id, owner_value, visible_parts, direct_anchor) in OWNERS.items():
        record_events = [row for row in events if row["record_unit_id"] == record]
        owner_rows.append({
            "record_unit_id": record,
            "page": page,
            "visible_owner_id": owner_id,
            "silent_owner_value_de": owner_value,
            "visible_parts": visible_parts,
            "direct_card_anchor": direct_anchor,
            "event_count": len(record_events),
            "statement_count": len({row["statement_id"] for row in record_events}),
            "owner_rule_de": "Bildbesitzer bleibt aktiv, bis Record oder expliziter Folgeposten wechselt",
        })
    write(OUT / "TWO_HUNDRED_NINTH_FIVE_HERBAL_OWNERS.tsv", owner_rows)

    noun_rows: list[dict[str, object]] = []
    for card_id, (noun_class, grounding, note) in NOUN_CARDS.items():
        card = dictionary[card_id]
        occurrences = by_card[card_id]
        noun_rows.append({
            "master_card_id": card_id,
            "master_form": card["master_form"],
            "registered_surfaces": card["registered_surfaces"],
            "herbal_value_de": card["current_value_de"],
            "noun_class": noun_class,
            "grounding": grounding,
            "herbal_occurrences": len(occurrences),
            "records": "|".join(dict.fromkeys(row["record_unit_id"] for row in occurrences)),
            "event_ids": "|".join(row["event_id"] for row in occurrences),
            "reading_note_de": note,
        })
    write(OUT / "TWO_HUNDRED_NINTH_28_HERBAL_NOUN_CARDS.tsv", noun_rows)

    event_rows: list[dict[str, object]] = []
    for event in events:
        noun = NOUN_CARDS.get(event["master_card_id"])
        owner = OWNERS[event["record_unit_id"]]
        event_rows.append({
            **event,
            "silent_owner_id": owner[2],
            "semantic_layer": "HERBAL_NOUN" if noun else "OPERATION_CONTROL_OR_STATE",
            "noun_class": noun[0] if noun else "NONE",
            "grounding": noun[1] if noun else "NOT_A_NOUN_CARD",
        })
    write(OUT / "TWO_HUNDRED_NINTH_100_EVENT_OWNER_NOUN_EDITION.tsv", event_rows)

    article_rows: list[dict[str, object]] = []
    for record, article in ARTICLES.items():
        owner = OWNERS[record]
        record_statements = [row for row in statements if row["record_unit_id"] == record]
        article_rows.append({
            "record_unit_id": record,
            "page": owner[0],
            "visible_owner_id": owner[2],
            "statement_ids": "|".join(row["statement_id"] for row in record_statements),
            "continuous_article_de": article,
            "explicit_card_nouns": "|".join(dict.fromkeys(
                event["portable_value_de"] for event in events
                if event["record_unit_id"] == record and event["master_card_id"] in NOUN_CARDS
            )),
            "intentionally_unassigned_nouns": "Pflanzenart|Blatt|Blüte|Wein|Öl|Honig|Krankheit|Körperteil",
        })
    write(OUT / "TWO_HUNDRED_NINTH_FIVE_CONTINUOUS_HERBAL_ARTICLES.tsv", article_rows)

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "owners": len(owner_rows),
        "unique_visible_plants": len({row["visible_owner_id"] for row in owner_rows}),
        "noun_cards": len(noun_rows),
        "noun_occurrences": sum(int(row["herbal_occurrences"]) for row in noun_rows),
        "grounding_counts": dict(Counter(row["grounding"] for row in noun_rows)),
        "events": len(event_rows),
        "statements": len(statements),
        "articles": len(article_rows),
        "herbal_freshwater_cards": sum(row["herbal_value_de"] == "Frischwasser zugeben; Schluss" for row in noun_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
