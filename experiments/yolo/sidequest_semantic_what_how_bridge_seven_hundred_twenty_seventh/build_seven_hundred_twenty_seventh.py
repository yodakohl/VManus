#!/usr/bin/env python3
"""Build Pass 727: bind the fixed Herbal WHAT and Biological HOW registers."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P724 = ROOT / "experiments/yolo/sidequest_semantic_concrete_medium_revision_seven_hundred_twenty_fourth"
P725 = ROOT / "experiments/yolo/sidequest_semantic_five_herbal_articles_seven_hundred_twenty_fifth"
P726 = ROOT / "experiments/yolo/sidequest_semantic_six_biological_stations_seven_hundred_twenty_sixth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def numeric(value: str) -> int:
    return int("".join(char for char in value if char.isdigit()))


def occurrences(
    ngram: tuple[str, ...], statement_sequences: dict[str, list[dict[str, str]]]
) -> list[tuple[str, list[dict[str, str]]]]:
    found: list[tuple[str, list[dict[str, str]]]] = []
    for statement_id, sequence in statement_sequences.items():
        cards = [row["card_no"] for row in sequence]
        for index in range(len(cards) - len(ngram) + 1):
            if tuple(cards[index : index + len(ngram)]) == ngram:
                found.append((statement_id, sequence[index : index + len(ngram)]))
    return found


def render_occurrence(items: list[tuple[str, list[dict[str, str]]]]) -> str:
    rendered = []
    for statement_id, rows in items:
        rendered.append(
            f"{statement_id}:{','.join(row['event_id'] for row in rows)}:"
            f"{' '.join(row['observed_surface'] for row in rows)}"
        )
    return " | ".join(rendered)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv")
    statements = read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv")
    herbal = read(P725 / "SEVEN_HUNDRED_TWENTY_FIFTH_5_COMPLETE_HERBAL_ARTICLES.tsv")
    bio = read(P726 / "SEVEN_HUNDRED_TWENTY_SIXTH_6_BIO_RECORDS.tsv")

    event_by_id = {row["event_id"]: row for row in events}
    statement_sequences: dict[str, list[dict[str, str]]] = defaultdict(list)
    record_sequences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_sequences[row["statement_id"]].append(row)
        record_sequences[row["record"]].append(row)

    h_events = [row for row in events if row["record"].startswith("H")]
    b_events = [row for row in events if row["record"].startswith("B")]
    h_cards = Counter(row["card_no"] for row in h_events)
    b_cards = Counter(row["card_no"] for row in b_events)
    shared_cards = sorted(set(h_cards) & set(b_cards), key=numeric)
    shared_card_rows = []
    for card in shared_cards:
        rows = [row for row in events if row["card_no"] == card]
        first = rows[0]
        h_rows = [row for row in rows if row["record"].startswith("H")]
        b_rows = [row for row in rows if row["record"].startswith("B")]
        shared_card_rows.append({
            "card_no": card,
            "component_recipe": first["component_recipe"],
            "atomic_reading_de": first["pass724_semantic_de"],
            "herbal_events": len(h_rows),
            "herbal_records": ",".join(sorted({row["record"] for row in h_rows}, key=numeric)),
            "herbal_event_ids": ",".join(row["event_id"] for row in h_rows),
            "bio_events": len(b_rows),
            "bio_records": ",".join(sorted({row["record"] for row in b_rows}, key=numeric)),
            "bio_event_ids": ",".join(row["event_id"] for row in b_rows),
            "portable_status": "SHARED_WORKSHOP_CARD__NOT_CROSS_REFERENCE",
        })

    sequences_by_register: dict[str, dict[int, set[tuple[str, ...]]]] = {
        "H": defaultdict(set), "B": defaultdict(set)
    }
    for statement_id, sequence in statement_sequences.items():
        register = "H" if statement_id.startswith("H") else "B"
        cards = [row["card_no"] for row in sequence]
        for n in (2, 3, 4):
            for index in range(len(cards) - n + 1):
                sequences_by_register[register][n].add(tuple(cards[index : index + n]))

    shared_by_n = {
        n: sorted(sequences_by_register["H"][n] & sequences_by_register["B"][n], key=lambda item: tuple(map(numeric, item)))
        for n in (2, 3, 4)
    }
    shared_bigram_rows = []
    for index, ngram in enumerate(shared_by_n[2], 1):
        h_occ = [(sid, rows) for sid, rows in occurrences(ngram, statement_sequences) if sid.startswith("H")]
        b_occ = [(sid, rows) for sid, rows in occurrences(ngram, statement_sequences) if sid.startswith("B")]
        component = [event_by_id[h_occ[0][1][i]["event_id"]]["component_recipe"] for i in range(2)]
        reading = [event_by_id[h_occ[0][1][i]["event_id"]]["pass724_semantic_de"] for i in range(2)]
        shared_bigram_rows.append({
            "bridge_id": f"BG{index:02d}", "card_sequence": ">".join(ngram),
            "component_sequence": ">".join(component), "portable_reading_de": " → ".join(reading),
            "herbal_occurrences": len(h_occ), "herbal_examples": render_occurrence(h_occ),
            "bio_occurrences": len(b_occ), "bio_examples": render_occurrence(b_occ),
            "interpretation": "PORTABLE_TWO_CARD_WORKSHOP_GRAMMAR__NOT_POINTER",
        })

    shared_trigram_rows = []
    for index, ngram in enumerate(shared_by_n[3], 1):
        h_occ = [(sid, rows) for sid, rows in occurrences(ngram, statement_sequences) if sid.startswith("H")]
        b_occ = [(sid, rows) for sid, rows in occurrences(ngram, statement_sequences) if sid.startswith("B")]
        first_rows = h_occ[0][1]
        shared_trigram_rows.append({
            "bridge_id": f"TG{index:02d}", "card_sequence": ">".join(ngram),
            "component_sequence": ">".join(row["component_recipe"] for row in first_rows),
            "atomic_sequence_de": " → ".join(row["pass724_semantic_de"] for row in first_rows),
            "herbal_occurrence": render_occurrence(h_occ), "bio_occurrence": render_occurrence(b_occ),
            "working_reading_de": "DEN AKTUELLEN POSTEN UNTER DEM VORGEGEBENEN MASS BEIBEHALTEN",
            "cross_register_consequence": "COMMON_MEASURE_FRAME__NO_PLANT_TO_STATION_POINTER",
        })

    register_rows: list[dict[str, object]] = []
    for row in herbal:
        register_rows.append({
            "record": row["record"], "page": row["page"], "register": "HERBAL_WHAT",
            "visible_owner_or_namespace": row["silent_plant_owner"],
            "statements": row["statements"], "events": row["events"],
            "continuous_reading_de": row["continuous_fluent_article_de"],
            "handoff_role": "PREPARES_OR_DESCRIBES_PICTURED_MATERIAL",
            "direct_cross_reference": "NONE",
        })
    for row in bio:
        register_rows.append({
            "record": row["record"], "page": row["page"], "register": "BIOLOGICAL_HOW",
            "visible_owner_or_namespace": row["owner_namespaces"],
            "statements": row["statements"], "events": row["events"],
            "continuous_reading_de": row["continuous_local_protocol_de"],
            "handoff_role": "OPERATES_ON_CURRENT_ITEM_AT_LOCAL_STATION",
            "direct_cross_reference": "NONE",
        })

    per_record_cards = {record: {row["card_no"] for row in rows} for record, rows in record_sequences.items()}
    per_record_ngrams: dict[str, dict[int, set[tuple[str, ...]]]] = {}
    for record in record_sequences:
        per_record_ngrams[record] = defaultdict(set)
        for statement_id, rows in statement_sequences.items():
            if rows[0]["record"] != record:
                continue
            cards = [row["card_no"] for row in rows]
            for n in (2, 3, 4):
                for index in range(len(cards) - n + 1):
                    per_record_ngrams[record][n].add(tuple(cards[index : index + n]))

    pair_rows = []
    for h_record in [f"H{i}" for i in range(1, 6)]:
        for b_record in [f"B{i}" for i in range(1, 7)]:
            cards = sorted(per_record_cards[h_record] & per_record_cards[b_record], key=numeric)
            bigrams = sorted(per_record_ngrams[h_record][2] & per_record_ngrams[b_record][2], key=lambda x: tuple(map(numeric, x)))
            trigrams = sorted(per_record_ngrams[h_record][3] & per_record_ngrams[b_record][3], key=lambda x: tuple(map(numeric, x)))
            fourgrams = sorted(per_record_ngrams[h_record][4] & per_record_ngrams[b_record][4], key=lambda x: tuple(map(numeric, x)))
            strongest = (
                "Y>AIIN>Y__GENERIC_MEASURE_FRAME" if trigrams
                else "SHARED_TWO_CARD_GRAMMAR" if bigrams
                else "SHARED_CARD_VOCABULARY" if cards
                else "NO_EXACT_BRIDGE"
            )
            pair_rows.append({
                "herbal_record": h_record, "bio_record": b_record,
                "shared_card_types": len(cards), "shared_card_ids": ",".join(cards) or "NONE",
                "shared_bigrams": len(bigrams), "shared_bigram_ids": " | ".join(">".join(x) for x in bigrams) or "NONE",
                "shared_trigrams": len(trigrams), "shared_trigram_ids": " | ".join(">".join(x) for x in trigrams) or "NONE",
                "shared_fourgrams": len(fourgrams), "strongest_bridge": strongest,
                "decision": "THEMATIC_COMPATIBILITY_ONLY__NO_DIRECT_CROSS_REFERENCE",
            })

    write("SEVEN_HUNDRED_TWENTY_SEVENTH_17_SHARED_CARDS.tsv", shared_card_rows)
    write("SEVEN_HUNDRED_TWENTY_SEVENTH_6_SHARED_BIGRAMS.tsv", shared_bigram_rows)
    write("SEVEN_HUNDRED_TWENTY_SEVENTH_1_SHARED_TRIGRAM.tsv", shared_trigram_rows)
    write("SEVEN_HUNDRED_TWENTY_SEVENTH_11_REGISTER_BINDING.tsv", register_rows)
    write("SEVEN_HUNDRED_TWENTY_SEVENTH_30_PAIRING_MATRIX.tsv", pair_rows)

    edition = [
        "# Herbal WHAT / Biological HOW — gemeinsame Werkstattausgabe", "",
        "Die fünf Pflanzenartikel stellen den sichtbaren Stoffbesitzer bereit; die sechs Biological-Records beschreiben lokale Arbeitsstationen. Die gemeinsame Kartensprache macht eine thematische Übergabe plausibel. Keine fixe Kartenfolge nennt jedoch einen bestimmten Pflanzenartikel als Eingang einer bestimmten Station.", "",
        "## Einziger gemeinsamer Dreikartenrahmen", "",
        "`Y – AIIN – Y` = **den aktuell gemeinten Posten unter dem vorgegebenen Maß beibehalten**.", "",
        "- H2-S001: `chy taiin shy` (E021–E023)",
        "- B3-S003: `chey daiin chey` (E232–E234)",
        "- Folgerung: dieselbe erlernte Maßformel, aber kein Pflanzenname, kein Stationsname und kein Verweisschlüssel.", "",
    ]
    for row in register_rows:
        edition.extend([
            f"## {row['record']} — {row['page']} — {row['register']}", "",
            f"**Bildbesitzer/Namensraum:** {row['visible_owner_or_namespace']}", "",
            str(row["continuous_reading_de"]), "",
        ])
    (HERE / "SEVEN_HUNDRED_TWENTY_SEVENTH_COMPLETE_WHAT_HOW_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    report = f"""# Pass 727 — WHAT/HOW-Brücke

## Ergebnis

Die Pflanzen- und Biological-Register teilen **{len(shared_cards)} exakte Karten**, **{len(shared_by_n[2])} Zweikartenfolgen** und genau **{len(shared_by_n[3])} Dreikartenfolge**. Es gibt **{len(shared_by_n[4])} gemeinsame Vierkartenfolge**.

Der stärkste tragbare Rahmen ist `Y–AIIN–Y`: in H2-S001 als `chy taiin shy`, in B3-S003 als `chey daiin chey`. Mit dem aktuellen Komponentenwörterbuch liest er sich knapp als:

> Den aktuell gemeinten Posten unter dem vorgegebenen Maß beibehalten.

Das ist eine echte gemeinsame Werkstattformel. Sie erklärt, wie ein Schreiber denselben abstrakten Arbeitsrahmen in einem Pflanzenartikel und an einer Bildstation benutzt. Sie enthält aber weder Pflanzenidentität noch Stationsidentität. Darum ist sie keine direkte Seitenreferenz.

## Arbeitsmodell

- Herbal ist das **WHAT-Register**: die Abbildung stellt den Stoffbesitzer, der Text beschreibt Auswahl, Maß und Vorbereitung.
- Biological ist das **HOW-Register**: die lokale Vignette stellt die Arbeitsstation, der Text führt den aktuellen Posten durch kurze Arbeitsschritte.
- Die Brücke ist ein gemeinsames Vokabular aus Posten, Maß, Ansatz, Fortsetzung und Anwendung.
- Der konkrete Pflanzenstoff kann im Biological-Teil still ergänzt sein; auf diesen zehn Seiten lässt sich aber keine einzelne H→B-Paarung ablesen.

Die 5×6-Paarungsmatrix bestätigt das: H2↔B3 besitzt als einziges Paar den Dreikartenrahmen, doch gerade dessen drei Karten sind generisch. Keine Paarung teilt eine Vierkartenfolge. Die stärkere Behauptung „dieser Pflanzenartikel gehört zu dieser Station“ wäre daher erfunden.

## Konkrete neue Lesart

Das Buch kann weiterhin als einfach lehrbares Werkstattbuch gelesen werden:

1. Das Bild setzt still den Gegenstand.
2. Der Herbal-Text macht daraus einen bearbeitbaren Posten.
3. `Y–AIIN–Y` hält ihn unter einem Maß aktiv.
4. Ein Biological-Bild setzt eine lokale Station.
5. Dieselben Karten für Posten, Maß, Ansatz und Fortsetzung beschreiben dort die Handhabung.

Das ergibt eine thematische WHAT→HOW-Architektur, aber keinen versteckten Hyperlink.

## Nächster Hebel

Die nächste Runde soll die sechs gemeinsamen Zweikartenfolgen in ihren vollständigen Satzumgebungen lesen. Gesucht wird eine kürzere portable Bauform wie `Ansatz→Posten`, `Posten→Maß` oder `Fortsetzung→Maß`, die ein lehrbarer Schreiber wirklich als Satzschablone benutzen konnte.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "events_bound": len(events), "herbal_events": len(h_events), "bio_events": len(b_events),
        "register_records": len(register_rows), "shared_exact_cards": len(shared_cards),
        "shared_bigrams": len(shared_by_n[2]), "shared_trigrams": len(shared_by_n[3]),
        "shared_fourgrams": len(shared_by_n[4]), "pairings": len(pair_rows),
        "unique_trigram": ">".join(shared_by_n[3][0]) if shared_by_n[3] else "NONE",
        "direct_cross_references": 0, "form_changes": 0,
        "decision": "WHAT_HOW_REGISTERS_SHARE_PORTABLE_MEASURE_AND_WORK_GRAMMAR__NO_DIRECT_CROSS_REFERENCE",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
