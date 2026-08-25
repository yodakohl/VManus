#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_renderer_consolidated_card_deck_nine_hundred_forty_second/PASS942_2511_RENDERER_CONSOLIDATED_READINGS.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_14_PAGE_SUMMARY.tsv"
F88 = ROOT / "experiments/yolo/sidequest_semantic_f88r_local_nomenclator_nine_hundred_forty_fifth/PASS945_16_F88R_LOCAL_LABELS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read_tsv(EVENTS)
    pages = read_tsv(PAGES)
    f88 = {row["event_id"]: row for row in read_tsv(F88)}
    routed: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    for row in events:
        if row["channel"] == "OWNER_ADDRESS_OR_DIAGRAM":
            layer = "LOCAL_NOMENCLATOR_OR_ADDRESS"
            value = f88[row["event_id"]]["local_nomenclator_default_de"] if row["event_id"] in f88 else row["spoken_value_de"]
        elif row["reading_route"] == "LEARNED_CARD_FAMILY":
            layer = "LEARNED_FORMULA_CARD"
            value = row["spoken_value_de"]
        else:
            layer = "PRODUCTIVE_ABBREVIATION_COMPOSITION"
            value = row["spoken_value_de"]
        counts[layer] += 1
        routed.append({
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "channel": row["channel"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "codebook_layer": layer,
            "current_value_de": value,
        })
    write_tsv(OUT / "PASS946_2511_THREE_LAYER_EVENT_EDITION.tsv", routed, list(routed[0]))

    by_page: dict[str, Counter[str]] = defaultdict(Counter)
    for row in routed:
        by_page[str(row["physical_page"])][str(row["codebook_layer"])] += 1
    page_rows: list[dict[str, object]] = []
    for page in pages:
        c = by_page[page["physical_page"]]
        page_rows.append({
            "physical_page": page["physical_page"],
            "page_model": page["page_model"],
            "events": page["events"],
            "productive_compositions": c["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "learned_formula_cards": c["LEARNED_FORMULA_CARD"],
            "local_nomenclator_or_addresses": c["LOCAL_NOMENCLATOR_OR_ADDRESS"],
            "current_page_reading_de": page["concrete_prose_reading_de"] if page["concrete_prose_reading_de"] != "KEINE_LAUFENDE_PROSA" else page["diagram_reading_de"],
        })
    write_tsv(OUT / "PASS946_14_PAGE_LAYER_COUNTS.tsv", page_rows, list(page_rows[0]))

    manual = """# Pass 946 — das dreischichtige Werkstatt-Codebuch

## Schicht 1: produktive Fachkürzel

56 kleine Werte schreiben START, WAHL, QUELLE, ZIEL, SOLLWERT, EINHEIT,
KURZ/LANG/VOLL, DIES und ENDE. Sie bilden seltene oder neue Karten.

## Schicht 2: gelernte Formelkarten

47 häufige Komponentenfolgen werden als ganze Arbeitsformeln gesprochen. Ihre
97 sichtbaren Varianten folgen Hand, Eintritt und Position. Beispiele:
`OK+E+DY` = „kurz ansetzen; Ende“, `CHD+Y` = „diesen Posten umsetzen“.

## Schicht 3: lokaler Nomenklator

Bildbeschriftungen nennen die örtliche Pflanze, Wurzel, Figur, Station, das
Gefäß oder den Ringplatz. Sie werden nicht zwanghaft zu universellen Verben.
Auf f88r eröffnet je ein Gefäßkopf ein Zutatenregister; dreizehn weitere
Gruppen benennen die gezeichneten Wurzel-/Blattposten.

## Lesereihenfolge

1. Bildbesitzer und Kanal erkennen.
2. Oberfläche zur Komponentenfolge normalisieren.
3. Lokale Bildkarte oder gelernte Formelkartenfamilie vorziehen.
4. Sonst die produktiven Kürzel zusammensetzen.
5. Karten zu Auswahl, Vorbereitung, Arbeitsgang, Zustand und Weitergabe bündeln.
"""
    (OUT / "PASS946_THREE_LAYER_CODEBOOK_MANUAL.md").write_text(manual, encoding="utf-8")

    report = f"""# Pass 946 — konsolidiertes Bedeutungsmodell

Alle 2.511 sichtbaren Gruppen haben jetzt genau eine von drei Aufgaben:

- **{counts['PRODUCTIVE_ABBREVIATION_COMPOSITION']}** produktiv zusammengesetzte Fachkarten;
- **{counts['LEARNED_FORMULA_CARD']}** Vorkommen gelernter Formelkarten;
- **{counts['LOCAL_NOMENCLATOR_OR_ADDRESS']}** lokale Bildnamen oder Adressen.

Damit erklärt das Modell sowohl neue Wortkompositionen als auch Formen, die ein
Schreiber schlicht aus dem Exemplar lernen musste. Es ist klein genug für eine
Werkstatt und konkret genug für vollständige Rücklesung. f88r zeigt die drei
Schichten besonders sauber nebeneinander: Gefäß/Zutat aus dem Bild, häufige
Arbeitsformeln im Text, seltene Anweisungen aus produktiven Kürzeln.
"""
    (OUT / "PASS946_REPORT.md").write_text(report, encoding="utf-8")
    summary = {"events": len(routed), "pages": len(page_rows), "layer_counts": dict(counts), "outputs": {}}
    for path in sorted(OUT.glob("PASS946_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS946_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
