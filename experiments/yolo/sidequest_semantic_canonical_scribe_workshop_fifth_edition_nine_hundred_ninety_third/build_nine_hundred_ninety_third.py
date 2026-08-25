#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P987 = ROOT / "experiments/yolo/sidequest_semantic_biological_natural_station_edition_nine_hundred_eighty_seventh"
P990 = ROOT / "experiments/yolo/sidequest_semantic_specialist_headword_cleanup_nine_hundred_ninetieth"
P991 = ROOT / "experiments/yolo/sidequest_semantic_canonical_natural_fourteen_page_edition_nine_hundred_ninety_first"
P992 = ROOT / "experiments/yolo/sidequest_semantic_portable_root_cleanup_nine_hundred_ninety_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    codebook = read(P992 / "PASS992_159_CODEBOOK.tsv")
    events = read(P992 / "PASS992_2511_EVENT_INTERLINEAR.tsv")
    roots = read(P992 / "PASS992_53_CLEAN_PORTABLE_ROOTS.tsv")
    clauses = read(P991 / "PASS991_354_NATURAL_CLAUSE_EDITION.tsv")
    addresses = read(P991 / "PASS991_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read(P991 / "PASS991_14_PAGE_READABLE_EDITION.tsv")
    labels = read(P991 / "PASS991_16_F88R_INGREDIENT_LABELS.tsv")
    batches = read(P991 / "PASS991_THREE_F88R_BATCHES.tsv")
    specialists = read(P990 / "PASS990_56_SPECIALIST_HEADWORDS.tsv")
    bio_events = read(P987 / "PASS987_1280_BIOLOGICAL_EVENT_PHRASES.tsv")
    bio_clauses = read(P987 / "PASS987_318_BIOLOGICAL_NATURAL_CLAUSES.tsv")

    write(HERE / "PASS993_159_COMPLETE_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS993_53_PORTABLE_ROOTS.tsv", roots, list(roots[0]))
    write(HERE / "PASS993_56_SPECIALIST_HEADWORDS.tsv", specialists, list(specialists[0]))
    write(HERE / "PASS993_2511_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS993_354_NATURAL_CLAUSE_EDITION.tsv", clauses, list(clauses[0]))
    write(HERE / "PASS993_501_LOCAL_ADDRESS_LEDGER.tsv", addresses, list(addresses[0]))
    write(HERE / "PASS993_14_PAGE_READABLE_EDITION.tsv", pages, list(pages[0]))
    write(HERE / "PASS993_16_F88R_INGREDIENT_LABELS.tsv", labels, list(labels[0]))
    write(HERE / "PASS993_THREE_F88R_BATCHES.tsv", batches, list(batches[0]))
    write(HERE / "PASS993_1280_BIOLOGICAL_EVENT_PHRASES.tsv", bio_events, list(bio_events[0]))
    write(HERE / "PASS993_318_BIOLOGICAL_CLAUSES.tsv", bio_clauses, list(bio_clauses[0]))

    theory = """# Pass 993 — aktuelle Sidequest-Arbeitstheorie

## In einem Satz

Die vierzehn Seiten werden als bildadressiertes Werkstattbuch gelesen, in dem
ein kleiner produktiver Stammcode mit gelernten Fachkarten und lokalen Bildnamen
zusammenarbeitet:

> Pflanzenmaterial auswählen → im Gefäß zubereiten → in lokaler Bad-,
> Leitungs- oder Anwendungsstation gebrauchen → getrennte Himmelsstelle
> nachschlagen.

## Was der Schreiber lernt

159 Einheiten genügen für die aktuelle Lesung:

- 53 portable Bedeutungswurzeln;
- 3 lokale Diagrammzeichen;
- 30 häufige Formelkarten;
- 51 ältere Fachkarten;
- 5 f13r-Bildteilkarten;
- 16 f88r-Zutatenetiketten;
- 1 Regel zum Kopieren kompletter Bild- und Ringadressen.

Die längste gelernte Karte gewinnt. Sonst werden die Wurzeln von links nach
rechts komponiert. `E/EE/EEE` geben einen kurzen, längeren oder vollen Grad;
`Y` hält den aktuellen POSTEN; nur lizenzierte `DY`-Karten tragen SCHLUSS.

## Wörterbuchkern

Die wichtigsten atomaren Werte sind:

- `Y=POSTEN`, `DY=SCHLUSS`, `OK=SETZEN`, `O=AUSFÜHREN`;
- `OL=FORTSETZEN`, `OT=DANACH`, `OR=ARBEITSSATZ`;
- `CH=NEHMEN`, `S=AUSWÄHLEN`, `K=GEBEN`;
- `AR=QUELLE`, `AL=ZIEL`, `L=LEITEN`, `AIR=LAUF`;
- `AIN=EINHEIT`, `AIIN=SOLLWERT`, `IIN=STUFE`;
- `E=KURZ`, `EE=LÄNGER`, `EEE=VOLL`;
- `CTH=BEREIT`, `SHED=ABSETZEN`, `CHK=BEHANDELN`;
- `CHEO=AUSZUG`, `CKH=DURCHLASS`, `LSH=SPÜLEN`;
- `S_ADDR=SONDERORT`: besondere Stelle im Stationsregister, Sternstelle im
  Himmelsregister.

## Kurze Fachkarten

Die gelernten Fachkarten bleiben Wörter, keine Mini-Sätze: KLARLAUF,
AUSWRINGEN, NACHSEIHEN, WEINSUD, FRISCHWASSER, WARMWASSER, SEITENARM,
AUFFANGSCHALE, WARMGRAD, HALTEZEIT, TUCH, ÜBERLAUF, WANNE, AUFLEGEN,
AUFSTREICHEN und ZERREIBEN. `shey/cheey` heißt nur KLARLAUF.

## Vollständige Lesung

- 2.511 sichtbare Gruppen auf 14 Seiten;
- 2.010 laufende Textgruppen in 354 natürlich formulierten Aussagen;
- 501 lokale Bild-, Stations- und Ringadressen;
- 1.280 Biological-Ereignisse in 318 lokalen Stationsaussagen;
- jede Gruppe, Aussage und Seite hat eine konkrete Arbeitslesung.

Biological-Verbindungen gelten nur in ihrer sichtbaren Vignette; es gibt keinen
erfundenen Gesamtwasserkreislauf. f88r hat drei stumme Gefäßbesitzer und
sechzehn Zutatenetiketten in Reihen 6+6+4. Die Himmelsseiten bleiben getrennte
Nachschlagetafeln ohne erzwungene Drehrichtung oder f68↔f69-Schlüssel.

## Stärkster Auszug

`tshol schoal cfhy shfydaiin cphy shey tchody`

> Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene
> Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; den
> Teilgang schließen.

## Status

Dies ist die derzeit beste kreative Schreiber- und Übersetzungsbasis des festen
Vierzehnseitenkorpus. Sie ist kein Anspruch auf historische Entzifferung. Der
nächste sinnvolle Gewinn liegt nicht in weiteren Seiten, sondern im Vergleich
der vorhergesagten Kartenkompositionen mit weiteren bereits sichtbaren
Varianten derselben vierzehn Seiten.
"""
    (HERE / "PASS993_CURRENT_WORKING_THEORY.md").write_text(theory, encoding="utf-8")

    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "portable_roots": len(roots),
        "specialist_headwords": len(specialists),
        "events": len(events),
        "clauses": len(clauses),
        "addresses": len(addresses),
        "pages": len(pages),
        "biological_events": len(bio_events),
        "biological_clauses": len(bio_clauses),
        "f88_labels": len(labels),
    }
    (HERE / "PASS993_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
