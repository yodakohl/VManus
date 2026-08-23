#!/usr/bin/env python3
"""Extract recurring picture- and exemplar-supplied phrases from the prose reader."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"

CONVENTIONS = (
    ("PFLANZE", "Pflanze", "VISIBLE_OWNER_NOUN", "die abgebildete Pflanze", "kein Kartenstamm bedeutet automatisch Pflanze"),
    ("WURZEL", "Wurzel", "OWNER_PLUS_ARTICLE_DETAIL", "der im Artikel gemeinte untere Pflanzenteil", "nur Bild und Artikel machen daraus Wurzel"),
    ("BLUETE", "Blüte", "OWNER_PLUS_ARTICLE_DETAIL", "der bild- oder exemplarbestimmte Blütenteil", "kein HO- oder Y-Stamm heißt Blüte"),
    ("KRAUT", "Kraut", "OWNER_PLUS_ARTICLE_DETAIL", "der aktuell verarbeitete Pflanzenposten", "breite Werkstattbezeichnung, kein Pflanzenname"),
    ("WASSER", "Wasser", "MASTER_EXEMPLAR_MATERIAL", "das für den Gang vorgesehene Wasser", "AIR bleibt Lauf/Bahn; Wasser ist eine Besitzerfüllung"),
    ("WEIN", "Wein", "MASTER_EXEMPLAR_MATERIAL", "das im Rezept vorgesehene Weinmedium", "nicht aus einem kurzen Stamm abgeleitet"),
    ("OEL", "Öl", "MASTER_EXEMPLAR_MATERIAL", "das im Rezept vorgesehene Öl", "nicht aus O oder OL abgeleitet"),
    ("SAFT", "Saft", "MASTER_EXEMPLAR_MATERIAL", "der aus der Pflanze gewonnene Saft", "CHEO bleibt Auszug, nicht Saft allein"),
    ("AUSZUG", "Auszug", "PROCESS_RESULT", "das Ergebnis des gerade geführten Auszugsgangs", "CHEO kann den kurzen Ergebniswert tragen; Stoffart kommt vom Besitzer"),
    ("ANSATZ", "Ansatz", "PROCESS_STATE", "der laufende Arbeitsansatz", "OR nennt Ansatz, nicht sämtliche Zutaten"),
    ("FLUESSIGKEIT", "Flüssigkeit", "OWNER_PROCESS_MEDIUM", "die aktuelle Becken- oder Arbeitsflüssigkeit", "kein generelles Wort WATER"),
    ("BECKEN", "Becken", "VISIBLE_OWNER_NOUN", "das sichtbar adressierte Becken", "nicht in AL, Y oder SOLK hineinlesen"),
    ("GEFAESS", "Gefäß", "VISIBLE_OWNER_OR_NOMENCLATOR", "das sichtbare oder gelernte Arbeitsgefäß", "OS kann lokal Gefäß sein; andere Karten erben es nur"),
    ("TUCH", "Tuch", "LEARNED_TOOL_OR_EXEMPLAR", "das für den Durchgang vorgesehene Tuch", "DAIN ist registergespalten; Tuch nicht global exportieren"),
    ("OEFFNUNG", "Öffnung", "VISIBLE_OWNER_ADDRESS", "die sichtbar bezeichnete Öffnung", "AL und AR geben Richtung, nicht die Form der Öffnung"),
    ("ABLAUF", "Ablauf", "VISIBLE_OWNER_PROCESS", "der lokale sichtbare Auslauf", "AIR/CKH nennen Lauf/Durchgang nur abstrakt"),
    ("STELLE", "Stelle", "VISIBLE_OWNER_ADDRESS", "die bezeichnete örtliche Stelle", "AL trägt nur Ziel"),
    ("TEIL", "Teil", "CARD_LEXICON", "der abgeteilte Teil", "TY liefert Teil; Besitzer liefert wovon"),
    ("PORTION", "Portion", "CARD_LEXICON", "eine abgeteilte Portion", "AIN liefert Portion; Stoff bleibt Kontext"),
    ("MASS", "Maß", "CARD_LEXICON", "das örtliche Sollmaß", "AIIN liefert Sollwert/Maß, keine konkrete Zahl"),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owner_class(value: str) -> str:
    if "Bildpflanze" in value:
        return "PLANT_BATCH"
    if "Lücke" in value:
        return "UNRESOLVED_GAP_STATION"
    if "Hauptbogenpaar" in value:
        return "CONNECTED_STRUCTURE"
    if "Becken" in value or "Gefäß" in value or "Vorrichtung" in value or "Station" in value:
        return "BASIN_STATION"
    return "GENERIC_WORKPIECE"


def owner_pronouns(kind: str) -> tuple[str, str, str, str]:
    return {
        "PLANT_BATCH": ("diese Bildpflanze", "der aktuell gezeigte Pflanzenteil", "aus dieser Pflanze", "am gezeigten Pflanzenteil"),
        "BASIN_STATION": ("diese Station", "der aktuelle Stationsposten", "aus dem sichtbaren Einlauf oder Gefäß", "zur sichtbaren Öffnung oder Schale"),
        "CONNECTED_STRUCTURE": ("dieses verbundene Bogenpaar", "der laufende Verbindungsposten", "vom sichtbaren oberen Anschluss", "zum sichtbaren unteren oder seitlichen Anschluss"),
        "UNRESOLVED_GAP_STATION": ("diese Zwischenstelle", "der dort eingetragene Posten", "von der vorigen sichtbaren Station", "zur folgenden sichtbaren Station"),
        "GENERIC_WORKPIECE": ("dieses Werkstück", "der aktuelle Arbeitsposten", "vom Ausgangsposten", "zur bezeichneten Arbeitsstelle"),
    }[kind]


def main() -> None:
    prose = [row for row in read_tsv(UNITS) if row["unit_kind"] == "PROSE_STATEMENT"]
    owner_counts = Counter(row["owner_or_namespace"] for row in prose)
    owner_rows = []
    for index, (owner, count) in enumerate(owner_counts.items(), 1):
        kind = owner_class(owner)
        subject, active, source, target = owner_pronouns(kind)
        pages = sorted({row["page"] for row in prose if row["owner_or_namespace"] == owner})
        owner_rows.append({
            "owner_id": f"OWN-{index:02d}",
            "exact_visible_owner_de": owner,
            "owner_class": kind,
            "statement_count": count,
            "pages": "|".join(pages),
            "silent_subject_de": subject,
            "silent_active_item_de": active,
            "silent_source_de": source,
            "silent_target_de": target,
            "teaching_rule_de": "Beim Besitzerwechsel diese vier Wendungen umstellen; die Kartenwerte unverändert lassen.",
        })
    write_tsv(OUT / "FIFTY_SEVENTH_17_VISIBLE_OWNER_PHRASES.tsv", owner_rows)

    convention_rows = []
    for entry_id, needle, source_class, default_phrase, boundary in CONVENTIONS:
        hits = [row for row in prose if re.search(re.escape(needle), row["fluent_working_reading_de"], re.IGNORECASE)]
        convention_rows.append({
            "phrase_id": entry_id,
            "search_form": needle,
            "content_source_class": source_class,
            "default_spoken_phrase_de": default_phrase,
            "statement_count": len(hits),
            "pages": "|".join(sorted({row["page"] for row in hits})) or "NONE",
            "statement_ids": "|".join(row["unit_id"] for row in hits) or "NONE",
            "word_boundary_de": boundary,
        })
    write_tsv(OUT / "FIFTY_SEVENTH_20_CONTENT_CONVENTIONS.tsv", convention_rows)

    annotated = []
    for row in prose:
        present = [conv for conv in convention_rows if conv["statement_ids"] != "NONE" and row["unit_id"] in conv["statement_ids"].split("|")]
        annotated.append({
            "unit_id": row["unit_id"],
            "page": row["page"],
            "visible_owner": row["owner_or_namespace"],
            "surface_sequence": row["surface_sequence"],
            "card_by_card_reading_de": row["card_by_card_reading_de"],
            "fluent_working_reading_de": row["fluent_working_reading_de"],
            "content_phrase_ids": "|".join(conv["phrase_id"] for conv in present) or "NONE",
            "content_source_classes": "|".join(sorted({conv["content_source_class"] for conv in present})) or "NONE",
            "silent_phrase_count": len(present),
            "teaching_instruction_de": "Erst Karten lesen; danach nur die hier markierten Besitzer-/Exemplarwendungen einsetzen.",
        })
    write_tsv(OUT / "FIFTY_SEVENTH_116_ANNOTATED_SENTENCES.tsv", annotated)

    book = [
        "# Bild- und Exemplarsprechbuch",
        "",
        "Der Meister lehrt neben den Karten zwanzig kurze Inhaltskonventionen. Einige",
        "kommen direkt aus dem Bild, andere aus dem lokalen Rezept- oder Stations-",
        "exemplar. Sie dürfen die flüssige Lesung konkret machen, bleiben aber außerhalb",
        "des Stammes.",
        "",
        "## Zwanzig Wendungen",
        "",
    ]
    for row in convention_rows:
        book.append(f"- **{row['default_spoken_phrase_de']}** ({row['statement_count']} Aussagen) — {row['content_source_class']}.")
    book.extend(["", "## Besitzerwechsel", ""])
    for row in owner_rows:
        book.append(
            f"- {row['exact_visible_owner_de']}: {row['silent_subject_de']}; "
            f"{row['silent_source_de']} → {row['silent_target_de']}."
        )
    (OUT / "FIFTY_SEVENTH_PICTURE_PHRASEBOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    class_counts = Counter(row["content_source_class"] for row in convention_rows)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "prose_statements": len(annotated),
            "visible_owner_phrases": len(owner_rows),
            "content_conventions": len(convention_rows),
            "statements_with_at_least_one_convention": sum(row["content_phrase_ids"] != "NONE" for row in annotated),
            **dict(class_counts),
        },
        "source": {str(UNITS.relative_to(ROOT)): sha256(UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
