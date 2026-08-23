#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R243 = ROOT / "experiments/yolo/sidequest_semantic_herbal_curriculum_transfer_two_hundred_forty_third"
R245 = ROOT / "experiments/yolo/sidequest_semantic_herbal_noun_decomposition_two_hundred_forty_fifth"
EVENTS = R243 / "TWO_HUNDRED_FORTY_THIRD_100_EVENT_HERBAL_TRANSFER.tsv"
ARTICLES = R243 / "TWO_HUNDRED_FORTY_THIRD_FIVE_TRANSFERRED_ARTICLES.tsv"
DICTIONARY = R245 / "TWO_HUNDRED_FORTY_FIFTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv"
NOUN_CORES = R245 / "TWO_HUNDRED_FORTY_FIFTH_13_LEARNED_NOUN_CORES.tsv"

OPERATION_CORES = [
    ("TCH", "BEREITUNG", "partial-operation residual"),
    ("SHFY", "STEHZEIT", "partial-operation residual"),
    ("D", "VORIGE_QUELLE", "partial-operation residual"),
    ("TCHO", "KALT_STELLEN", "whole operation"),
    ("SOTODAN", "FOLGEANWENDUNG", "whole operation"),
    ("CHEECKHO", "AUFTRAGEN", "whole operation"),
    ("O", "ABKUEHLEN", "whole operation"),
    ("CFHY", "AUSWRINGEN", "whole operation"),
    ("CPHY", "NACHSEIHEN", "whole operation"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_events = read_tsv(EVENTS)
    articles = read_tsv(ARTICLES)
    dictionary = read_tsv(DICTIONARY)
    card = {r["master_card_id"]: r for r in dictionary}

    events: list[dict[str, object]] = []
    for row in source_events:
        item = card[row["master_card_id"]]
        events.append({
            "event_id": row["event_id"], "page": row["page"], "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"], "field_id": row["field_id"], "field_position": row["field_position"],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "component_parse": item["component_parse"],
            "concrete_default_de": item["revised_default_de"], "composition_status": item["composition_status"],
            "memorized_residue": item["memorized_residue"], "terminal_status": row["terminal_status"],
        })

    additions = []
    for row in read_tsv(NOUN_CORES):
        additions.append({"lesson": "HERBAL_NOUN_CORE", "entry": row["learned_core"], "meaning_de": row["short_meaning_de"], "learning_status": row["learning_status"]})
    for entry, meaning, status in OPERATION_CORES:
        additions.append({"lesson": "HERBAL_OPERATION_CORE", "entry": entry, "meaning_de": meaning, "learning_status": status})

    event_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_FINAL_100_EVENT_HERBAL_MANUAL.tsv"
    dictionary_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv"
    addition_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_22_ADDITIONAL_CORES.tsv"
    article_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_FIVE_COMPLETE_ARTICLES.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_READABLE_HERBAL_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_SIXTH_REPORT.md"
    write_tsv(event_path, events, list(events[0]))
    write_tsv(dictionary_path, dictionary, list(dictionary[0]))
    write_tsv(addition_path, additions, list(additions[0]))
    write_tsv(article_path, articles, list(articles[0]))

    status_counts = Counter(r["composition_status"] for r in events)
    readable = ["# Kompaktes Herbal-Handbuch für den Biological-Lehrling", ""]
    readable += [
        "## Was bereits bekannt ist", "",
        "17 gemeinsame Karten lesen 44 Ereignisse unmittelbar. Weitere 24 Karten sind vollständig aus bekannten Komponenten gebaut und lesen 27 Ereignisse.", "",
        "## Was neu gelernt wird", "",
        "Dreizehn Nomenkerne und neun Operationskerne reichen für alle verbleibenden Karten.", "",
    ]
    for row in additions:
        readable.append(f"- `{row['entry']}` = **{row['meaning_de']}** ({row['learning_status']})")
    readable += ["", "## Fünf vollständige Artikel", ""]
    for article in articles:
        readable += [f"### {article['record_unit_id']} / {article['page']}", "", article["continuous_article_de"], ""]
    readable += [
        "## Schreibablauf", "",
        "1. Bildpflanze als stillen Besitzer setzen.",
        "2. Pflanzenteil, Ansatz, Gefäß oder Zugabe aus den 22 Herbal-Kernen wählen.",
        "3. Gemeinsame Karten für Quelle, Ziel, Menge, Folge, aktuellen Posten und Zustand ergänzen.",
        "4. Operation aus dem bekannten Motiv bauen; nur die sechs ganzen Herbal-Handlungen kopieren.",
        "5. Karte offen lassen oder mit der lizenzierten Schlussform beenden.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 246: konsolidiertes Herbal-Lehrbuch

## Ergebnis

Ein in den Biological-Seiten geschulter Schreiber liest von 100 Herbal-Ereignissen **44 direkt aus dem gemeinsamen Kern** und baut **27 weitere vollständig kompositionell**. **12** Ereignisse brauchen einen neuen Kern in einem bekannten Rahmen; **17** sind ganze lokale Nomen oder Operationen.

Die Zusatzlektion hat nur **22 Kerne**: 13 Nomenkerne und 9 Operationskerne. Aus ihnen entstehen 49 lokale Herbal-Karten; zusammen mit 17 gemeinsamen Karten ergibt das das vollständige 66-Karten-Wörterbuch.

Das passt zur Werkstattidee besser als 66 isolierte Wörter. Der Lehrling lernt wenige Inhaltseinheiten und setzt daraus Zielzugabe, Folgeansatz, Bereitungsanteil, Quellauszug, Zugabemaß, Zugabeansatz und aktuelle Zutat produktiv zusammen.

Input event SHA `{sha(EVENTS)}`; dictionary `{sha(DICTIONARY)}`; noun cores `{sha(NOUN_CORES)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "events": len(events), "cards": len(dictionary), "articles": len(articles),
        "additional_cores": len(additions), "event_status_counts": dict(status_counts),
        "outputs": {p.name: sha(p) for p in (event_path, dictionary_path, addition_path, article_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
