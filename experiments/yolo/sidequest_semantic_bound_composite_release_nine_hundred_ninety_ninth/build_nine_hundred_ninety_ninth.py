#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

ARTIFACTS = [
    ("CODEBOOK", "experiments/yolo/sidequest_semantic_formula_ligature_reconciliation_nine_hundred_ninety_eighth/PASS998_159_RECONCILED_CODEBOOK.tsv"),
    ("ROOTS", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_53_PORTABLE_ROOTS.tsv"),
    ("FORMULA_LIGATURES", "experiments/yolo/sidequest_semantic_formula_ligature_reconciliation_nine_hundred_ninety_eighth/PASS998_30_FORMULA_LIGATURES.tsv"),
    ("SPECIALISTS", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_56_SPECIALIST_HEADWORDS.tsv"),
    ("EVENTS", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_2511_EVENT_INTERLINEAR.tsv"),
    ("CLAUSES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_354_NATURAL_CLAUSE_EDITION.tsv"),
    ("ADDRESSES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_501_LOCAL_ADDRESS_LEDGER.tsv"),
    ("PAGES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_14_PAGE_READABLE_EDITION.tsv"),
    ("BIO_EVENT_PHRASES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_1280_BIOLOGICAL_EVENT_PHRASES.tsv"),
    ("BIO_CLAUSES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_318_BIOLOGICAL_CLAUSES.tsv"),
    ("F88_LABELS", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_16_F88R_INGREDIENT_LABELS.tsv"),
    ("F88_BATCHES", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_THREE_F88R_BATCHES.tsv"),
    ("SECOND_DRAWER", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_70_SECOND_DRAWER_COMPOSITIONS.tsv"),
    ("CORRECTED_GRID", "experiments/yolo/sidequest_semantic_layered_composition_grid_correction_nine_hundred_ninety_seventh/PASS997_CORRECTED_LAYERED_EIGHT_BY_EIGHT_GRID.tsv"),
    ("EMPTY_GRID_CELLS", "experiments/yolo/sidequest_semantic_layered_composition_grid_correction_nine_hundred_ninety_seventh/PASS997_TWENTY_FIVE_TRUE_EMPTY_CELLS.tsv"),
    ("SURFACE_COLLISIONS", "experiments/yolo/sidequest_semantic_layered_composition_grid_correction_nine_hundred_ninety_seventh/PASS997_THREE_SURFACE_COLLISIONS.tsv"),
    ("HEADWORD_REVISIONS", "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_SIX_SHORT_HEADWORD_REVISIONS.tsv"),
]


def tsv_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    manifest = []
    for role, relative in ARTIFACTS:
        path = ROOT / relative
        manifest.append(
            {
                "artifact_role": role,
                "relative_path": relative,
                "data_rows": str(tsv_count(path)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "release_status": "CURRENT_BOUND_INPUT",
            }
        )
    with (HERE / "PASS999_RELEASE_MANIFEST.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)

    manual = """# Pass 999 — einseitiges Schreiberhandbuch

## Was gelernt wird

1. **53 Wurzeln** tragen kurze Bedeutungen wie POSTEN, MASS, PORTION, ANSATZ,
   QUELLE, ZIEL, STELLEN, HALTEN, LEITEN, MERKEN und SCHLUSS.
2. **30 Formelkarten** sind häufige Ganzschreibformen. Alle 30 bedeuten exakt
   ihre Wurzelsumme; sie sind Ligaturen, keine zusätzlichen Wörter.
3. **56 Fachköpfe** decken spezielle Handlungen und Gegenstände wie KLARLAUF,
   AUSWRINGEN, NACHSEIHEN, WEINSUD, TUCH und AUFFANGSCHALE.
4. Bildteile, Zutatenetiketten und Himmelsadressen werden als lokale Ganzkarten
   aus dem Seitenexemplar kopiert.

## Leseregel

1. Zuerst den sichtbaren Bild- oder Stationsbesitzer feststellen.
2. Lokale Adresse oder lange Fachkarte vor einer Wurzelzerlegung lesen.
3. Bekannte Formelligatur erkennen, ihre Bedeutung aber aus den Wurzeln lesen.
4. Sonst die Wurzeln von links nach rechts verbinden.
5. `E/EE/EEE` als KURZ/LÄNGER/VOLL lesen; `Y` hält den POSTEN.
6. Nur eine lizenzierte `DY`-Karte schließt den Teilgang.
7. Den natürlichen Satz aus Besitzer und Register ergänzen.

## Korrigierter Wortbaukasten

Von 64 einfachen Links-Rechts-Kombinationen sind 24 produktiv und 12 als
Formelligaturen im laufenden Inhalt belegt. Eine weitere ist nur Fachkarte,
zwei stehen nur in Bildadressen, 25 bleiben unbenutzt.

Drei naive Kurzformen sind blockiert:

- `S+Y` kollidiert mit `sy = POSTEN`;
- `CH+Y` kollidiert mit `chy = POSTEN`;
- `CH+AR` kollidiert mit `char = QUELLE`.

Für diese Bedeutungen muss der Schreiber eine längere Karte oder andere
Rendererform wählen.

## Buchlesung

> Pflanzenmaterial nehmen und nach Maß zubereiten; im Gefäß halten, trennen
> oder weiterleiten; an einer lokalen Bad-/Anwendungsstation einsetzen; danach
> eine getrennte Himmelsstelle nachschlagen.

Die vierzehn Seiten enthalten 2.511 Gruppen, davon 2.010 laufende Textgruppen
in 354 Aussagen und 501 lokale Adressen. f88r zeigt sechzehn Zutatenetiketten
in Reihen 6+6+4 unter drei stummen Gefäßen. Biological bleibt lokal und bildet
keinen einzigen Gesamtwasserkreislauf.

Dies ist die aktuelle kreative Arbeitslesung, keine historische
Entzifferungsbehauptung.
"""
    (HERE / "PASS999_ONE_PAGE_SCRIBE_MANUAL.md").write_text(manual, encoding="utf-8")

    theory = """# Pass 999 — aktuelle gebundene Arbeitstheorie

Die aktuelle Basis ist Pass 996 mit zwei verpflichtenden Korrekturen:

- Pass 997 ersetzt das fehlerhafte 24/40-Raster durch 24 produktive + 12
  Formelkarten + 1 Fachkarte + 2 Adressen + 25 leere Zellen;
- Pass 998 korrigiert vier alte Formelköpfe und zeigt, dass 30/30
  Formelkarten semantisch reguläre Wurzelkompositionen sind.

Damit lautet das Mischmodell:

> produktive Bedeutungswurzeln + gelernte graphische Ligaturen + gelernte
> Fachwörter + lokale Bildnamen.

Der vollständige Arbeitsstand ist durch `PASS999_RELEASE_MANIFEST.tsv` an 17
konkrete Tabellen gebunden. Das Taschenhandbuch ist die kürzeste menschlich
lesbare Fassung.
"""
    (HERE / "PASS999_CURRENT_WORKING_THEORY.md").write_text(theory, encoding="utf-8")

    summary = {
        "status": "PASS",
        "bound_artifacts": len(manifest),
        "book_model": "PRODUCTIVE_ROOTS_PLUS_FORMULA_LIGATURES_PLUS_SPECIALIST_AND_LOCAL_WHOLE_CARDS",
        "current_base": "PASS996",
        "mandatory_corrections": ["PASS997", "PASS998"],
    }
    (HERE / "PASS999_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
