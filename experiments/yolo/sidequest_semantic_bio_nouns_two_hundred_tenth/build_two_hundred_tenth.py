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

NOUN_CARDS = {
    "MC008": ("MATERIAL_POSTEN", "WORKSHOP_INFERRED", "Abführgut ist eine Prozessrolle, kein sichtbarer Stoff"),
    "MC012": ("MATERIAL_POSTEN", "WORKSHOP_INFERRED", "Zusatz ist in zwei Zellen eingetragen, aber nicht gezeichnet"),
    "MC022": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Zielpassage passt zur linken Unterlaufstation"),
    "MC023": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Beckenlauf bezeichnet eine lokale Laufrolle, nicht das ganze Seitenbild"),
    "MC038": ("WASCH_PROZESS", "WORKSHOP_INFERRED", "geschlossener Waschgang im gemeinsamen Beckenfeld"),
    "MC056": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Zielmarke ist eine lokale Adresse"),
    "MC058": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "kurze Zielpassage ohne behauptete Flussrichtung"),
    "MC059": ("EINSATZ_OBJEKT", "WORKSHOP_INFERRED", "Einlage ist nicht als eigener Gegenstand sicher sichtbar"),
    "MC065": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Auslass an der mittleren linken Gerätestation"),
    "MC066": ("FLÜSSIGKEITS_POSTEN", "WORKSHOP_INFERRED", "Klarabzug ist ein Prozessprodukt"),
    "MC078": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Zwischenziel am ungerichteten Hauptbogen"),
    "MC080": ("ZUBEREITUNG", "WORKSHOP_INFERRED", "Ansatz bleibt ein laufender Arbeitsposten"),
    "MC084": ("WASCH_PROZESS", "WORKSHOP_INFERRED", "Vollwaschung ist eine gelernte geschlossene Zelle"),
    "MC086": ("MENGE_TEIL", "RELATIONAL", "Teil des aktiven lokalen Postens"),
    "MC091": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Laufschluss schließt eine lokale Linie, keinen globalen Kreislauf"),
    "MC101": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Endziel gehört zum rechten Endposten"),
    "MC105": ("MENGE_TEIL", "RELATIONAL", "abgegrenzte Portion an verschiedenen Stationen"),
    "MC116": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Weiterlauf ist eine lokale Fortsetzung"),
    "MC118": ("GEFÄSS_STATION", "GEOMETRY_COMPATIBLE", "Auffanggefäß ist mit dem großen Beckenfeld vereinbar, aber nicht identifiziert"),
    "MC119": ("FLÜSSIGKEITS_POSTEN", "WORKSHOP_INFERRED", "Klarlauf erscheint an drei getrennten Stationen"),
    "MC126": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Zielzuführung an der unteren korbartigen Station"),
    "MC130": ("WASCH_PROZESS", "WORKSHOP_INFERRED", "offener Waschgang im gemeinsamen Beckenfeld"),
    "MC134": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Weiterweg ist eine lokale Routenkarte"),
    "MC138": ("FLÜSSIGKEITS_POSTEN", "WORKSHOP_INFERRED", "Frischwasser ist genau eine gelernte Zelle an der mittleren linken Station"),
    "MC168": ("WEG_STATION", "GEOMETRY_COMPATIBLE", "Abführpassage an der oberen Paarstation"),
}

RECORD_READINGS = {
    "B1": "Im gemeinsamen zweireihigen Figuren-/Beckenfeld wechseln kurze und lange Einwirkzellen mit Überführen, Weitergeben, Durchleiten, Waschen, Absetzen und Auffangen. Die sichtbare Einfassung hält den gemeinsamen Besitzer; keine Karte benennt eine Person, einen Körperteil oder eine Therapie.",
    "B2": "Die obere Paarbecken-/Zylinderstation führt Portionen durch lokale Ziel- und Abführpassagen. Die mittlere linke Gerätestation erhält genau einmal Frischwasser und führt Folgemaß, Absetzen, Einsetzen und Klarlauf. Die mittlere rechte Station bleibt ungelöst. Das untere grüne Mehrfigurenfeld und seine Randstationen bilden eigene Abführ-, Wasch-, Ziel- und Haltezellen.",
    "B3": "Die obere Fächerstation, eine runde Randstation und eine untere korbartige Randstation bilden getrennte lokale Arbeitsplätze. Danach folgt ein ungelöster Zwischenposten und schließlich das Hauptpaar am ungerichteten Bogen. Die Karten beschreiben Bemessen, Überführen, Einwirken, Absetzen, Zuführen und Abziehen; der Bogen liefert keinen Richtungspfeil.",
    "B4": "Am Hauptpaar werden Posten lang und kurz gehalten, überführt, eingesetzt, befestigt und zweimal durchgelassen. Die linke Unterlaufstation bearbeitet Sollmaß, Portion, Klarlauf, Zielpassage und Abführung. Die rechte S-Laufstation übernimmt einen weiteren Anteil. Beide Seiten bleiben lokale Äste, kein geschlossener Kreislauf.",
    "B5": "Der linke offene Endposten erhält Nachtransfer, Einführung, Zielabsetzung, Weiterführung und Sollmaß. Er ist ein eigener kurzer Record.",
    "B6": "Der rechte S-Lauf-Endposten sammelt länger, bearbeitet kurz, führt zum Endziel und nimmt eine Einlage als aktuellen Posten. Er ist vom linken Endposten getrennt.",
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
    events = [row for row in read(EVENTS) if row["record_unit_id"].startswith("B")]
    statements = [row for row in read(STATEMENTS) if row["record_unit_id"].startswith("B")]
    dictionary = {row["master_card_id"]: row for row in read(DICT)}
    by_owner: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_owner[event["visible_owner"]].append(event)
        by_card[event["master_card_id"]].append(event)

    owner_rows: list[dict[str, object]] = []
    for order, (owner, rows) in enumerate(by_owner.items(), 1):
        status = "UNRESOLVED_LOCAL_OWNER" if "ungelöst" in owner else "DIRECT_VISIBLE_LOCAL_OWNER"
        owner_rows.append({
            "owner_order": order,
            "visible_owner": owner,
            "owner_status": status,
            "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
            "records": "|".join(dict.fromkeys(row["record_unit_id"] for row in rows)),
            "event_count": len(rows),
            "statement_count": len({row["statement_id"] for row in rows}),
            "owner_rule_de": "nur lokale Station; keine unsichtbare Verbindung zum nächsten Besitzer",
        })
    write(OUT / "TWO_HUNDRED_TENTH_15_BIO_VISIBLE_OWNERS.tsv", owner_rows)

    noun_rows: list[dict[str, object]] = []
    for card_id, (noun_class, grounding, note) in NOUN_CARDS.items():
        card = dictionary[card_id]
        occurrences = by_card[card_id]
        noun_rows.append({
            "master_card_id": card_id,
            "master_form": card["master_form"],
            "registered_surfaces": card["registered_surfaces"],
            "bio_value_de": card["current_value_de"],
            "noun_class": noun_class,
            "grounding": grounding,
            "bio_occurrences": len(occurrences),
            "records": "|".join(dict.fromkeys(row["record_unit_id"] for row in occurrences)),
            "owners": "|".join(dict.fromkeys(row["visible_owner"] for row in occurrences)),
            "reading_note_de": note,
        })
    write(OUT / "TWO_HUNDRED_TENTH_25_BIO_NOUN_LOCATION_CARDS.tsv", noun_rows)

    event_rows: list[dict[str, object]] = []
    for event in events:
        noun = NOUN_CARDS.get(event["master_card_id"])
        event_rows.append({
            **event,
            "owner_status": "UNRESOLVED_LOCAL_OWNER" if "ungelöst" in event["visible_owner"] else "DIRECT_VISIBLE_LOCAL_OWNER",
            "semantic_layer": "BIO_NOUN_OR_LOCATION" if noun else "OPERATION_CONTROL_OR_STATE",
            "noun_class": noun[0] if noun else "NONE",
            "grounding": noun[1] if noun else "NOT_A_NOUN_CARD",
        })
    write(OUT / "TWO_HUNDRED_TENTH_281_EVENT_OWNER_NOUN_EDITION.tsv", event_rows)

    record_rows: list[dict[str, object]] = []
    for record, reading in RECORD_READINGS.items():
        record_events = [row for row in events if row["record_unit_id"] == record]
        record_rows.append({
            "record_unit_id": record,
            "page": record_events[0]["page"],
            "event_count": len(record_events),
            "statement_count": len({row["statement_id"] for row in record_events}),
            "visible_owner_count": len({row["visible_owner"] for row in record_events}),
            "continuous_station_reading_de": reading,
            "intentionally_unassigned_nouns": "Person|Frau|Patient|Körperteil|Krankheit|Therapie|Bad|Flussrichtung|Gesamtkreislauf",
        })
    write(OUT / "TWO_HUNDRED_TENTH_SIX_BIO_RECORD_READINGS.tsv", record_rows)

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "owners": len(owner_rows),
        "direct_owner_events": sum(int(row["event_count"]) for row in owner_rows if row["owner_status"] == "DIRECT_VISIBLE_LOCAL_OWNER"),
        "unresolved_owner_events": sum(int(row["event_count"]) for row in owner_rows if row["owner_status"] == "UNRESOLVED_LOCAL_OWNER"),
        "noun_cards": len(noun_rows),
        "noun_occurrences": sum(int(row["bio_occurrences"]) for row in noun_rows),
        "grounding_counts": dict(Counter(row["grounding"] for row in noun_rows)),
        "events": len(event_rows),
        "statements": len(statements),
        "records": len(record_rows),
        "freshwater_occurrences": sum(row["master_card_id"] == "MC138" for row in events),
        "person_word_cards": sum(row["bio_value_de"] in {"Person", "Frau", "Patient"} for row in noun_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
