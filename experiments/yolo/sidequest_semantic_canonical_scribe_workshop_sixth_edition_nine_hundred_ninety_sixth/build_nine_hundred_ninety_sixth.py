#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P993 = YOLO / "sidequest_semantic_canonical_scribe_workshop_fifth_edition_nine_hundred_ninety_third"
P994 = YOLO / "sidequest_semantic_second_composition_drawer_nine_hundred_ninety_fourth"
P995 = YOLO / "sidequest_semantic_historical_short_headwords_nine_hundred_ninety_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REPLACEMENTS = [
    ("SOLLMASS", "MASS"),
    ("SOLLWERT", "MASS"),
    ("EINHEIT", "PORTION"),
    ("TEILMENGE", "PORTION"),
    ("ARBEITSSATZ", "ANSATZ"),
    ("EINTRAGSSATZ", "EINTRAGSGRUPPE"),
    ("EINSTELLEN", "STELLEN"),
    ("MARKIEREN", "MERKEN"),
    ("START", "BEGINN"),
    ("eine Einheit auswählen", "eine Portion auswählen"),
    ("Eine Einheit auswählen", "Eine Portion auswählen"),
]


def revise(value: str) -> str:
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def revise_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{key: revise(value) for key, value in row.items()} for row in rows]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    codebook = read_tsv(P995 / "PASS995_159_SHORT_HEADWORD_CODEBOOK.tsv")
    roots = read_tsv(P995 / "PASS995_53_SHORT_PORTABLE_ROOTS.tsv")
    events = read_tsv(P995 / "PASS995_2511_REVISED_EVENT_INTERLINEAR.tsv")
    clauses = read_tsv(P995 / "PASS995_354_REVISED_NATURAL_CLAUSES.tsv")
    bio_phrases = read_tsv(P995 / "PASS995_1280_REVISED_BIOLOGICAL_EVENT_PHRASES.tsv")
    revisions = read_tsv(P995 / "PASS995_SIX_HEADWORD_REVISIONS.tsv")

    specialists = read_tsv(P993 / "PASS993_56_SPECIALIST_HEADWORDS.tsv")
    addresses = revise_rows(read_tsv(P993 / "PASS993_501_LOCAL_ADDRESS_LEDGER.tsv"))
    pages = revise_rows(read_tsv(P993 / "PASS993_14_PAGE_READABLE_EDITION.tsv"))
    labels = read_tsv(P993 / "PASS993_16_F88R_INGREDIENT_LABELS.tsv")
    batches = read_tsv(P993 / "PASS993_THREE_F88R_BATCHES.tsv")

    drawer = revise_rows(read_tsv(P994 / "PASS994_SECOND_COMPOSITION_DRAWER.tsv"))
    grid = revise_rows(read_tsv(P994 / "PASS994_EIGHT_BY_EIGHT_COMPOSITION_GRID.tsv"))
    phrases = revise_rows(read_tsv(P994 / "PASS994_TWENTY_APPRENTICE_PHRASES.tsv"))
    bio_clauses = [row for row in clauses if row["physical_page"] in {"f75r", "f81v", "f82r", "f83r"}]

    outputs = {
        "PASS996_159_COMPLETE_CODEBOOK.tsv": codebook,
        "PASS996_53_PORTABLE_ROOTS.tsv": roots,
        "PASS996_56_SPECIALIST_HEADWORDS.tsv": specialists,
        "PASS996_2511_EVENT_INTERLINEAR.tsv": events,
        "PASS996_354_NATURAL_CLAUSE_EDITION.tsv": clauses,
        "PASS996_501_LOCAL_ADDRESS_LEDGER.tsv": addresses,
        "PASS996_14_PAGE_READABLE_EDITION.tsv": pages,
        "PASS996_1280_BIOLOGICAL_EVENT_PHRASES.tsv": bio_phrases,
        "PASS996_318_BIOLOGICAL_CLAUSES.tsv": bio_clauses,
        "PASS996_16_F88R_INGREDIENT_LABELS.tsv": labels,
        "PASS996_THREE_F88R_BATCHES.tsv": batches,
        "PASS996_70_SECOND_DRAWER_COMPOSITIONS.tsv": drawer,
        "PASS996_EIGHT_BY_EIGHT_COMPOSITION_GRID.tsv": grid,
        "PASS996_TWENTY_APPRENTICE_PHRASES.tsv": phrases,
        "PASS996_SIX_SHORT_HEADWORD_REVISIONS.tsv": revisions,
    }
    for name, rows in outputs.items():
        write_tsv(name, rows)

    theory = """# Pass 996 — aktuelle Sidequest-Arbeitstheorie

## Die Lesemaschine

Die vierzehn Seiten werden als bildadressiertes Werkstattbuch gelesen:

> Pflanzenmaterial auswählen → im Gefäß zubereiten → in lokaler Bad-,
> Leitungs- oder Anwendungsstation gebrauchen → getrennte Himmelsstelle
> nachschlagen.

Ein Schreiber lernt 159 Einheiten: 53 kurze Wurzeln, drei Diagrammzeichen,
30 häufige Formelkarten, 51 Fachkarten, fünf f13r-Bildteilkarten, sechzehn
f88r-Zutatenetiketten und eine Regel zum Kopieren lokaler Adressen. Die
längste gelernte Karte gewinnt; sonst werden Wurzeln von links nach rechts
zusammengesetzt.

## Kurzes Taschenwörterbuch

- `Y=POSTEN`, `DY=SCHLUSS`, `OK=SETZEN`, `O=AUSFÜHREN`;
- `OL=FORTSETZEN`, `OT=DANACH`, `OR=ANSATZ`;
- `CH=NEHMEN`, `S=AUSWÄHLEN`, `K=GEBEN`;
- `AR=QUELLE`, `AL=ZIEL`, `L=LEITEN`, `AIR=LAUF`;
- `AIN=PORTION`, `AIIN=MASS`, `IIN=STUFE`;
- `E=KURZ`, `EE=LÄNGER`, `EEE=VOLL`;
- `T=STELLEN`, `R=MERKEN`, `CARRIER_Q=BEGINN`;
- `CTH=BEREIT`, `SHED=ABSETZEN`, `CHK=BEHANDELN`;
- `CHEO=AUSZUG`, `CKH=DURCHLASS`, `LSH=SPÜLEN`;
- `S_ADDR=SONDERORT`, lokal als Sonderstelle oder Sternstelle erweitert.

Die Fachkarten bleiben ebenfalls kurz: KLARLAUF, AUSWRINGEN, NACHSEIHEN,
WEINSUD, FRISCHWASSER, WARMWASSER, SEITENARM, AUFFANGSCHALE, WARMGRAD,
HALTEZEIT, TUCH, ÜBERLAUF, WANNE, AUFLEGEN, AUFSTREICHEN und ZERREIBEN.

## Wortbau

Zum 30-Karten-Grunddeck kommen 70 wiederkehrende Kompositionen der zweiten
Schublade. Sie decken 287 Ereignisse; 63 stehen auf mehreren Seiten. Beispiele:

- `S+AIN` → **eine Portion auswählen**;
- `CH+OR` → **vom Ansatz nehmen**;
- `OK+CHD+DY` → **setzen und umsetzen; Schluss**;
- `LSH+E+DY` → **kurz spülen; Schluss**;
- `SOLK+EE+Y` → **den Posten länger auffangen**.

Keine dieser Bildungen benötigt eine neue Wurzel. Leere Felder im 8×8-Raster
sind erlaubte, aber auf den festen Seiten noch nicht gebrauchte Bildungen.

## Vollständige Lesung

- 2.511 sichtbare Gruppen;
- 2.010 laufende Textgruppen in 354 natürlichen Aussagen;
- 501 lokale Bild-, Stations- und Ringadressen;
- 1.280 Biological-Gruppen in 318 lokalen Stationsaussagen;
- sechzehn f88r-Zutatenetiketten in Reihen 6+6+4 unter drei stummen Gefäßen.

Biological-Verbindungen gelten nur in ihrer sichtbaren Vignette. Die
Himmelsseiten bleiben getrennte Nachschlagetafeln ohne erzwungene Richtung oder
f68↔f69-Schlüssel.

## Stärkster Auszug

`tshol schoal cfhy shfydaiin cphy shey tchody`

> Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene
> Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; den
> Teilgang schließen.

Dies ist die beste aktuelle kreative Schreiberbasis, keine behauptete
historische Entzifferung.
"""
    (HERE / "PASS996_CURRENT_WORKING_THEORY.md").write_text(theory, encoding="utf-8")

    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "portable_roots": len(roots),
        "specialist_headwords": len(specialists),
        "events": len(events),
        "clauses": len(clauses),
        "addresses": len(addresses),
        "pages": len(pages),
        "biological_events": len(bio_phrases),
        "biological_clauses": len(bio_clauses),
        "f88_labels": len(labels),
        "second_drawer_compositions": len(drawer),
        "second_drawer_events": sum(int(row["events"]) for row in drawer),
        "output_hashes": {name: sha(HERE / name) for name in sorted(outputs)},
    }
    (HERE / "PASS996_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
