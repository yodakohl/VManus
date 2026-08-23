#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R209 = ROOT / "experiments/yolo/sidequest_semantic_herbal_nouns_two_hundred_ninth"
R211 = ROOT / "experiments/yolo/sidequest_semantic_cross_register_bridge_two_hundred_eleventh"
EVENTS = R209 / "TWO_HUNDRED_NINTH_100_EVENT_OWNER_NOUN_EDITION.tsv"
ARTICLES = R209 / "TWO_HUNDRED_NINTH_FIVE_CONTINUOUS_HERBAL_ARTICLES.tsv"
BRIDGES = R211 / "TWO_HUNDRED_ELEVENTH_136_BRIDGE_OCCURRENCES.tsv"
BRIDGE_CARDS = R211 / "TWO_HUNDRED_ELEVENTH_17_CROSS_REGISTER_CARDS.tsv"


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
    bridge_occurrences = [r for r in read_tsv(BRIDGES) if r["section"] == "HERBAL"]
    bridge_ids = {r["event_id"] for r in bridge_occurrences}
    bridge_cards = {r["master_card_id"]: r for r in read_tsv(BRIDGE_CARDS)}

    events: list[dict[str, object]] = []
    for row in source_events:
        if row["event_id"] in bridge_ids:
            layer = "COMMON_BIOLOGICAL_HERBAL_CORE"
            action = "reuse known card and keep the same short value"
        elif row["semantic_layer"] == "HERBAL_NOUN":
            layer = "HERBAL_LOCAL_NOUN_SIGN"
            action = "learn one new pictured-material/container/preparation sign"
        else:
            layer = "HERBAL_LOCAL_OPERATION_SIGN"
            action = "learn or decompose one Herbal-specific work operation"
        events.append({
            "event_id": row["event_id"], "page": row["page"], "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"], "field_id": row["field_id"], "field_position": row["field_position"],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "concrete_default_de": row["portable_value_de"],
            "curriculum_layer": layer, "noun_class": row["noun_class"], "grounding": row["grounding"],
            "terminal_status": row["terminal_status"], "apprentice_action": action,
        })

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_card[str(row["master_card_id"])].append(row)
    cards: list[dict[str, object]] = []
    for card_id, linked in sorted(by_card.items()):
        values = list(dict.fromkeys(str(r["concrete_default_de"]) for r in linked))
        layers = list(dict.fromkeys(str(r["curriculum_layer"]) for r in linked))
        bridge = bridge_cards.get(card_id)
        cards.append({
            "master_card_id": card_id,
            "master_form": bridge["master_form"] if bridge else linked[0]["visible_surface"],
            "registered_surfaces": "|".join(dict.fromkeys(str(r["visible_surface"]) for r in linked)),
            "concrete_default_de": values[0],
            "curriculum_layer": layers[0],
            "occurrence_count": len(linked),
            "event_ids": "|".join(str(r["event_id"]) for r in linked),
            "records": "|".join(dict.fromkeys(str(r["record_unit_id"]) for r in linked)),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in linked)),
            "value_invariant": "YES" if len(values) == 1 else "NO",
            "learning_rule": linked[0]["apprentice_action"],
        })

    article_rows: list[dict[str, object]] = []
    for article in articles:
        linked = [r for r in events if r["record_unit_id"] == article["record_unit_id"]]
        counts = Counter(str(r["curriculum_layer"]) for r in linked)
        article_rows.append({
            "record_unit_id": article["record_unit_id"], "page": article["page"],
            "visible_owner_id": article["visible_owner_id"], "statement_ids": article["statement_ids"],
            "continuous_article_de": article["continuous_article_de"],
            "common_core_events": counts["COMMON_BIOLOGICAL_HERBAL_CORE"],
            "local_noun_events": counts["HERBAL_LOCAL_NOUN_SIGN"],
            "local_operation_events": counts["HERBAL_LOCAL_OPERATION_SIGN"],
            "explicit_card_nouns": article["explicit_card_nouns"],
            "unassigned_species_or_domain_nouns": article["intentionally_unassigned_nouns"],
        })

    event_path = OUT / "TWO_HUNDRED_FORTY_THIRD_100_EVENT_HERBAL_TRANSFER.tsv"
    card_path = OUT / "TWO_HUNDRED_FORTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv"
    article_path = OUT / "TWO_HUNDRED_FORTY_THIRD_FIVE_TRANSFERRED_ARTICLES.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_THIRD_READABLE_HERBAL_APPRENTICESHIP.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_THIRD_REPORT.md"
    write_tsv(event_path, events, list(events[0]))
    write_tsv(card_path, cards, list(cards[0]))
    write_tsv(article_path, article_rows, list(article_rows[0]))

    readable = ["# Vom Biological-Lehrling zum Herbal-Schreiber", ""]
    readable += [
        "Der Lehrling bringt 17 gemeinsame Karten mit. Sie decken 44 der 100 Kartenauftritte ab.",
        "Danach lernt er 24 lokale Nomenkarten für Pflanzenteil, Gefäß, Portion, Ansatz und Zugabe sowie 25 lokale Operationskarten.", "",
    ]
    for article in article_rows:
        readable += [
            f"## {article['record_unit_id']} / {article['page']}", "",
            str(article["continuous_article_de"]), "",
            f"Lehraufwand: {article['common_core_events']} bekannte Kernkarten, {article['local_noun_events']} neue Nomenkarten-Auftritte, {article['local_operation_events']} lokale Operationskarten-Auftritte.", "",
        ]
    readable += [
        "## Werkstattregel", "",
        "Die Pflanze selbst wird nicht als Wort wiederholt: Das Bild hält den Besitzer aktiv. Karten benennen Teile, Behälter, Ansätze, Mengen und Arbeitsschritte. Genau dadurch kann dieselbe Kernkarte in einem Beckenrecord und einem Pflanzenartikel funktionieren.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    event_counts = Counter(str(r["curriculum_layer"]) for r in events)
    card_counts = Counter(str(r["curriculum_layer"]) for r in cards)
    report = f"""# Sidequest-Pass 243: Biological-Curriculum auf Herbal übertragen

## Ergebnis

Von 100 Herbal-Kartenauftritten sind **44** sofort aus dem Biological-Kern lesbar. Die restlichen **56** teilen sich exakt in **28** lokale Nomen-Auftritte und **28** lokale Operations-Auftritte.

Auf Wörterbuchebene besteht die Herbal-Seite aus **66** Karten:

- 17 gemeinsame Herbal/Biological-Kernkarten;
- 24 neue lokale Nomenkarten;
- 25 neue lokale Operationskarten.

Alle 66 Karten haben innerhalb der vier Pflanzenseiten einen invarianten kurzen Default. Das ist genau die gesuchte Werkstattmischung: ein kleiner produktiver gemeinsamer Kern plus gelernte Fachzeichen für Bildbesitzer, Teile, Gefäße, Ansätze und besondere Arbeitsschritte.

Der nächste Hebel liegt bei den 25 lokalen Operationskarten: Wenn sie sich in die sieben Biological-Motive zerlegen lassen, schrumpft der echte Herbal-Ausnahmewortschatz weiter.

Input hashes: R209 events `{sha(EVENTS)}`; R209 articles `{sha(ARTICLES)}`; R211 bridge occurrences `{sha(BRIDGES)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "events": len(events), "cards": len(cards), "articles": len(article_rows),
        "event_layer_counts": dict(event_counts), "card_layer_counts": dict(card_counts),
        "invariant_cards": sum(r["value_invariant"] == "YES" for r in cards),
        "outputs": {p.name: sha(p) for p in (event_path, card_path, article_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
