#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_whole_card_reconciliation_two_hundred_second"
DICT = BASE / "TWO_HUNDRED_SECOND_173_CARD_RECONCILED_DICTIONARY.tsv"
EVENTS = BASE / "TWO_HUNDRED_SECOND_381_EVENT_RECONCILED_EDITION.tsv"
STATEMENTS = BASE / "TWO_HUNDRED_SECOND_116_STATEMENT_RECONCILED_EDITION.tsv"

REVISIONS = {
    "MC041": ("weiter einsetzen", "Separates OK+OL: aktives Material weiter in den Gang setzen."),
    "MC048": ("Bearbeitungsstufe", "Von der allgemeinen Arbeitsstufe als konkrete Prozessstufe getrennt."),
    "MC084": ("Vollwaschung; Schluss", "Eigenständige geschlossene Ganzkarte, nicht bloß zweites Etikett für Waschgang."),
    "MC086": ("Teil", "Neutrale Teilkarte; AIN-Karte MC105 trägt dagegen die portionierte Menge."),
    "MC090": ("weiter bearbeiten", "L+OL führt die bestehende Bearbeitung weiter, ohne neues Einsetzen."),
    "MC104": ("kurz weiterbearbeiten", "Kurzer Bearbeitungsschritt; von bloßer Fortleitung getrennt."),
    "MC105": ("Portion", "AIN-Reihe bezeichnet eine abgegrenzte Menge, nicht nur irgendeinen Teil."),
    "MC106": ("kurz weiterführen", "Kurze Fortleitung; von MC104s Bearbeitung unterschieden."),
    "MC107": ("nächster Posten", "OT-Reihe wählt den nächsten Posten."),
    "MC108": ("kleiner Rest", "Restgröße am Ende der ersten Kräuterklausel; kein Synonym für Kurzteil."),
    "MC115": ("bereiter Folgeposten", "CTH erweitert den Folgeposten um Bereitschaft."),
    "MC134": ("Weiterweg", "Lauf-/Transferweg statt unspezifischem Weitergang."),
    "MC136": ("bearbeiteter Quellauszug", "KCHOAR ist der bereits bearbeitete Auszug von der Quelle."),
    "MC141": ("Folgeklarlauf", "TSH-Rahmen markiert den anschließenden Klarlauf."),
    "MC163": ("Folgegang", "OT+CHOL bezeichnet den folgenden Arbeitsgang."),
}

FLUENT_OVERRIDES = {
    "H1-S001": "Die Wurzel der Bildpflanze nehmen, einen Teil im Aufnahmegefäß vorbereiten, Flüssigkeit zugießen, den Folgeteil einsetzen, auf Sollmaß bringen und einen kleinen Rest belassen.",
    "H1-S002": "Die erste Charge weiterbearbeiten, im Folgegang weiterführen und als bereit halten.",
    "H2-S001": "Aus dem bereiten Auszugsansatz die nächste Charge ansetzen, den bereiten Folgeposten wählen und diesen auf Sollmaß bringen.",
    "H2-S003": "Im Zubereitungsgefäß den Ansatz in der Bearbeitungsstufe bearbeiten und die vorgeschriebene Zugabemenge einsetzen.",
    "H3-S004": "Zum nächsten Posten wechseln, ihn weiter einsetzen, Bereitschaft prüfen und als aktuellen Posten halten.",
    "H5-S001": "Einen Zugabeansatz herstellen, die weitere Zutat als Zielzugabe auf Sollmaß bringen, den Folgeansatz weiter bearbeiten, einsetzen und dorthin führen.",
    "H5-S005": "Eine weitere Zutat mit dem bearbeiteten Quellauszug weiterbearbeiten und die Folgeanwendung ausführen.",
    "H5-S006": "Zum nächsten Posten wechseln, kurz weiterbearbeiten und auf Sollmaß bringen.",
    "B1-S002": "Eine Portion ansetzen, den Posten lang einwirken lassen und über den Fortsetzungsweg weitergeben.",
    "B1-S014": "Überführen, über den Weiterweg an der Zielstelle abführen und zur Folgequelle weitergehen.",
    "B1-S017": "Dorthin bringen, kurz weiterführen und übertragen; Schluss.",
    "B2-S015": "An der lokalen Randstation den Folgeklarlauf länger einwirken lassen; Schluss.",
    "B2-S019": "Eine Vollwaschung ausführen; Schluss.",
    "B3-S013": "Eine Portion bemessen, kurz vorbereiten und kurz einwirken lassen; Schluss.",
    "B3-S034": "Die Arbeitsstufe auf bereit stellen, einen Teil und das Folgemaß nehmen und am Zwischenziel kurz absetzen; Schluss.",
    "B4-S015": "Eine Portion zum Klarlauf geben, die Portion durch die Zielpassage führen, kurz auffangen und abführen; Schluss.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def duplicate_groups(rows: list[dict[str, str]], value_col: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        groups[row[value_col]].append(row["master_card_id"])
    return {value: ids for value, ids in groups.items() if len(ids) > 1}


def main() -> None:
    dictionary = read(DICT)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    before = duplicate_groups(dictionary, "current_value_de")
    old_values = {row["master_card_id"]: row["current_value_de"] for row in dictionary}

    revision_rows: list[dict[str, object]] = []
    for card_id, (new_value, reason) in REVISIONS.items():
        card = next(row for row in dictionary if row["master_card_id"] == card_id)
        revision_rows.append({
            "master_card_id": card_id,
            "master_form": card["master_form"],
            "event_count": card["event_count"],
            "old_value_de": card["current_value_de"],
            "new_value_de": new_value,
            "semantic_distinction": reason,
        })
        card["current_value_de"] = new_value
    write(OUT / "TWO_HUNDRED_THIRD_15_VALUE_REVISIONS.tsv", revision_rows)
    write(OUT / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv", dictionary)

    selected = {card_id: value for card_id, (value, _) in REVISIONS.items()}
    for event in events:
        if event["master_card_id"] in selected:
            event["portable_value_de"] = selected[event["master_card_id"]]
    write(OUT / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv", events)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    affected: list[dict[str, object]] = []
    for statement in statements:
        old_literal = statement["literal_card_reading"]
        old_fluent = statement["revised_fluent_translation_de"]
        statement["literal_card_reading"] = " | ".join(
            event["portable_value_de"] for event in by_statement[statement["statement_id"]]
        )
        if statement["statement_id"] in FLUENT_OVERRIDES:
            statement["revised_fluent_translation_de"] = FLUENT_OVERRIDES[statement["statement_id"]]
        if old_literal != statement["literal_card_reading"] or old_fluent != statement["revised_fluent_translation_de"]:
            affected.append({
                "statement_id": statement["statement_id"],
                "changed_card_ids": "|".join(dict.fromkeys(
                    event["master_card_id"] for event in by_statement[statement["statement_id"]]
                    if event["master_card_id"] in REVISIONS
                )),
                "old_literal": old_literal,
                "new_literal": statement["literal_card_reading"],
                "old_fluent": old_fluent,
                "new_fluent": statement["revised_fluent_translation_de"],
            })
    write(OUT / "TWO_HUNDRED_THIRD_116_STATEMENT_COMPACT_EDITION.tsv", statements)
    write(OUT / "TWO_HUNDRED_THIRD_AFFECTED_STATEMENTS.tsv", affected)

    after = duplicate_groups(dictionary, "current_value_de")
    values = sorted(set(before) | set(after))
    collision_rows: list[dict[str, object]] = []
    for value in values:
        collision_rows.append({
            "value_de": value,
            "before_card_ids": "|".join(before.get(value, [])),
            "before_count": len(before.get(value, [])),
            "after_card_ids": "|".join(after.get(value, [])),
            "after_count": len(after.get(value, [])),
            "resolution": "INTENTIONAL_ALLOMORPHY" if value == "einführen; Schluss" else "SPLIT_BY_FUNCTION",
        })
    write(OUT / "TWO_HUNDRED_THIRD_VALUE_COLLISION_AUDIT.tsv", collision_rows)

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "cards": len(dictionary),
        "events": len(events),
        "statements": len(statements),
        "value_revisions": len(REVISIONS),
        "affected_statements": len(affected),
        "distinct_values_before": len(set(old_values.values())),
        "duplicate_groups_before": len(before),
        "distinct_values_after": len({row["current_value_de"] for row in dictionary}),
        "duplicate_groups_after": len(after),
        "sole_duplicate_after": after,
        "max_value_words_after": max(len(row["current_value_de"].split()) for row in dictionary),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
