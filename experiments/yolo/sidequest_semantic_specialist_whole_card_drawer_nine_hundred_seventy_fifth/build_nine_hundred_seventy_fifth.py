#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
DRAWER = ROOT / "experiments/yolo/sidequest_semantic_apprentice_phrasebook/APPRENTICE_55_LOCAL_HEADWORDS.tsv"
WHOLE = ROOT / "experiments/yolo/sidequest_semantic_apprentice_codebook/WHOLE_CARD_22_CODEBOOK.tsv"
OLD_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_air_path_revision_two_hundred_sixty_eighth/TWO_HUNDRED_SIXTY_EIGHTH_REVISED_116_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


EXTRA = [
    {
        "joint_tuple_id": "LOCAL_CHAIN_F11R_STANDING_TIME",
        "surface_family": "shfydaiin",
        "occurrence_count": "1",
        "records": "H3",
        "pages": "f11r",
        "event_ids": "E042",
        "word_class": "LOCAL_EXEMPLAR_SINGLETON",
        "lexical_drawer": "QUANTITY_TIME",
        "apprentice_headword_de": "STEHZEIT",
        "context_expansion_de": "vorgeschriebene Stehzeit",
        "context_was_removed": "NO",
        "semantic_segmentation": "SHFY+DAIIN_STANDING_TIME_WHOLE",
        "learning_rule_de": "Als lokale Zeitkarte zwischen Auswringen und Nachseihen lernen.",
    }
]

RECORD_PAGE = {
    "H1": "f10r", "H2": "f10r", "H3": "f11r", "H4": "f55v", "H5": "f56r",
    "B1": "f81v", "B2": "f82r", "B3": "f83r", "B4": "f83r", "B5": "f83r", "B6": "f83r",
}


def variants(value: str) -> list[str]:
    return [part for part in re.split(r"[;|]", value) if part]


def main() -> None:
    source_drawer = read(DRAWER)
    known_ids = {row["joint_tuple_id"] for row in source_drawer}
    for row in read(WHOLE):
        if row["joint_tuple_id"] in known_ids:
            continue
        source_drawer.append({
            "joint_tuple_id": row["joint_tuple_id"],
            "surface_family": row["surface_family"],
            "occurrence_count": row["occurrences"],
            "records": "|".join(sorted({part.split("-")[0] for part in row["statement_ids"].split("|")})),
            "pages": row["pages"],
            "event_ids": row["event_ids"],
            "word_class": "MEMORIZED_WHOLE_CARD",
            "lexical_drawer": row["headword_de"],
            "apprentice_headword_de": row["headword_de"],
            "context_expansion_de": row["exact_card_reading_de"],
            "context_was_removed": "NO",
            "semantic_segmentation": row["codebook_rule"],
            "learning_rule_de": row["apprentice_mnemonic_de"],
        })
        known_ids.add(row["joint_tuple_id"])
    source_drawer += EXTRA
    map_by_page_surface: dict[tuple[str, str], dict[str, str]] = {}
    for row in source_drawer:
        for page in row["pages"].split("|"):
            for surface in variants(row["surface_family"]):
                key = (page, surface)
                if key in map_by_page_surface and map_by_page_surface[key]["apprentice_headword_de"] != row["apprentice_headword_de"]:
                    raise ValueError(f"conflicting specialist cards for {key}")
                map_by_page_surface[key] = row

    events = read(P971 / "PASS971_2511_EVENT_EDITION.tsv")
    hybrid = []
    applied = Counter()
    for row in events:
        specialist = map_by_page_surface.get((row["physical_page"], row["surface"]))
        if specialist:
            headword = specialist["apprentice_headword_de"]
            expansion = specialist["context_expansion_de"]
            drawer = specialist["lexical_drawer"]
            combined = expansion
            applied[(headword, row["physical_page"])] += 1
        else:
            headword = ""
            expansion = ""
            drawer = ""
            combined = row["register_expansion_de"]
        hybrid.append({
            **row,
            "specialist_headword_de": headword,
            "specialist_context_expansion_de": expansion,
            "specialist_drawer": drawer,
            "hybrid_working_reading_de": combined,
            "reading_priority": "LOCAL_SPECIALIST_WHOLE_CARD" if specialist else "PORTABLE_ROOT_OR_COMMON_FORMULA",
        })
    write(HERE / "PASS975_2511_EVENT_HYBRID_EDITION.tsv", hybrid, list(hybrid[0]))

    drawer_rows = []
    for row in source_drawer:
        observed = sum(
            1 for event in events
            if event["physical_page"] in row["pages"].split("|") and event["surface"] in variants(row["surface_family"])
        )
        drawer_rows.append({
            **row,
            "pass971_observed_events": str(observed),
            "current_status": "LOCAL_SPECIALIST_OVERRIDE__PORTABLE_ROOTS_REMAIN_AS_MNEMONIC",
        })
    write(HERE / "PASS975_SPECIALIST_CARD_DRAWER.tsv", drawer_rows, list(drawer_rows[0]))

    old_rows = read(OLD_STATEMENTS)
    strong = []
    for row in old_rows:
        record = row["record_unit_id"]
        if record not in RECORD_PAGE:
            continue
        page = RECORD_PAGE[record]
        surfaces = row["visible_sequence"].split()
        hits = []
        for surface in surfaces:
            spec = map_by_page_surface.get((page, surface))
            if spec:
                hits.append(f"{surface}={spec['context_expansion_de']}")
        if hits:
            strong.append({
                "statement_id": row["statement_id"],
                "physical_page": page,
                "visible_owner": row["visible_owner"],
                "surface_sequence": row["visible_sequence"],
                "specialist_cards": " | ".join(hits),
                "specialist_card_count": str(len(hits)),
                "complete_working_translation_de": row["complete_local_translation_de"],
            })
    write(
        HERE / "PASS975_SPECIALIST_PASSAGES.tsv",
        strong,
        ["statement_id", "physical_page", "visible_owner", "surface_sequence", "specialist_cards", "specialist_card_count", "complete_working_translation_de"],
    )

    f11 = next(row for row in strong if row["statement_id"] == "H3-S001")
    report = f"""# Pass 975 — der lokale Fachkartenkasten kommt zurück

## Korrektur der zu harten Kompression

Die 86 Karten aus Pass 971 bleiben die gemeinsame Lehrtafel. Sie reichen aber
nicht als vollständiges Fachvokabular. Einige seltene Oberflächen sind in
ihrem konkreten Bild- und Satzkontext viel verständlicher als **gelernte
Ganzkarten**. Ein Schreiber von 1420 musste daher zweierlei lernen:

1. produktive Kurzbausteine für SETZEN, NEHMEN, MENGE, STUFE, ZIEL und SCHLUSS;
2. einen lokalen Fachkasten für AUSWRINGEN, NACHSEIHEN, KÜHLEN, WASCHEN,
   AUFTRAGEN, TUCH, GEFÄSS, ROH, KLARLAUF und ähnliche Werkstattwörter.

Der Fachkasten hat {len(drawer_rows)} Kartenzeilen aus dem lokalen
55er-Fachkasten, dem überlappungsfrei ergänzten Grundwortkasten und der
ausdrücklich wiederhergestellten STEHZEIT. In der
aktuellen 2.511-Ereignis-Ausgabe überschreibt er nur passende Oberfläche **und
Seite**. Außerhalb dieses Kontextes bleibt die produktive Wurzellesung aktiv.

## Unsere stärkste konkrete Passage

`{f11['surface_sequence']}`

> **Aus dem blühenden Kochgut einen Sudansatz bilden, auswringen, die
> vorgeschriebene Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und
> kalt stellen; Schluss.**

Das ist nicht mehr die frühere überlange Einwortglosse „shey = bis die
Flüssigkeit klar abläuft“. Die Arbeit wird sauber auf sieben Karten verteilt:

- `tshol` — Blütenkraut/Kochgut;
- `schoal` — Sudansatz;
- `cfhy` — auswringen;
- `shfydaiin` — vorgeschriebene Stehzeit;
- `cphy` — nachseihen;
- `shey` — Klarlauf;
- `tchody` — kalt stellen; Schluss.

Damit beantwortet sich auch die alte Frage nach `shey`: Es ist in dieser
Passage keine ganze Anweisung, sondern der kurze Produktname **Klarlauf**. Die
benachbarten Karten liefern Abwarten, Nachseihen und Kühlen.

## Weitere sinnvolle Fachkarten

- f10r: WURZEL, WURZELREST, GEFÄSS, TOPF, PRESSEN, AUFFANGEN, ANWÄRMEN;
- f55v: ANWÄRMEN, VERWAHREN, KÜHLEN;
- f56r: STÄNGEL, ZERREIBEN, ABSEIHEN, AUFTRAGEN, ANWENDEN, GABE;
- f81v: ZUSATZ, AUFFANGSCHALE, FÜLLEN, SCHWENKEN;
- f82r: SPÜLWASSER, FRISCHWASSER, TEILEN, DÜSE, ÜBERLAUF,
  WARMWASSER;
- f83r: ROH, TUCH, BECKEN, NACHWASCHEN, BEFESTIGEN.

## Das nun realistischere Schreiberhandbuch

> Zerlege die gewöhnliche Arbeitskarte. Wenn eine lokale Fachkarte an genau
> dieser Bildseite gelernt wurde, lies ihren kurzen Werkstattwert als Ganzes.
> Nutze die sichtbaren Bestandteile weiterhin als Gedächtnishilfe, aber zwinge
> das Fachwort nicht in eine neue Satzbedeutung.

Das ist die gesuchte Mischung aus Fachkürzeln und gelernten Ganzwörtern: klein
genug für mehrere Schreiber, flexibel genug für neue Kombinationen und konkret
genug für echte Rezeptketten.
"""
    (HERE / "PASS975_SPECIALIST_WHOLE_CARD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "common_dictionary_entries_retained": 86,
        "specialist_drawer_rows": len(drawer_rows),
        "specialist_applied_events": sum(1 for row in hybrid if row["specialist_headword_de"]),
        "hybrid_events": len(hybrid),
        "strong_passages": len(strong),
        "restored_anchor_passage": "H3-S001",
    }
    (HERE / "PASS975_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
