#!/usr/bin/env python3
"""Build a small apprentice codebook for the 22 learned whole cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_nomenclator_family_completion"
DICT_IN = SOURCE / "COMPACT_173_CARD_DICTIONARY.tsv"
EVENTS_IN = SOURCE / "COMPACT_381_EVENT_INTERLINEAR.tsv"
PHRASES_IN = SOURCE / "COMPACT_116_PHRASES.tsv"

CARDS_OUT = HERE / "WHOLE_CARD_22_CODEBOOK.tsv"
HEADS_OUT = HERE / "WHOLE_HEADWORD_16.tsv"
COPYBOOK_OUT = HERE / "COPYBOOK_116_STATEMENTS.tsv"
EXERCISES_OUT = HERE / "APPRENTICE_16_EXERCISES.tsv"
MANUAL_OUT = HERE / "APPRENTICE_ONE_PAGE_MANUAL.md"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


# headword id -> headword, surfaces, rule, variants, short mnemonic
HEADWORDS = {
    "W01_ZUSATZ": ("ZUSATZ", ["dl"], "offene gelernte Gegenstandskarte", "allgemeiner Zusatz", "Gib den Zusatz zum laufenden Ansatz."),
    "W02_GEFAESS": ("GEFAESS", ["os", "ly", "oykchor"], "drei gelernte Gefaesskarten", "allgemein | Empfaenger | Zubereitungsgefaess", "Das Bild und die Stelle waehlen die Gefaessform."),
    "W03_KUEHLEN": ("KUEHLEN", ["tchody", "ody"], "gelernter Schlussbefehl", "fertiger Klarauszug | abgemessene Portion", "Kuehle den bezeichneten Posten und schliesse."),
    "W04_ROH": ("ROH", ["qekey"], "offene gelernte Zustandskarte", "unbehandelter Ausgangsposten", "Nimm den Posten im rohen Zustand."),
    "W05_TUCH": ("TUCH", ["dain"], "offene gelernte Gegenstandskarte", "allgemeines Arbeitstuch", "Lege das Tuch am bezeichneten Posten ein."),
    "W06_SCHWENKEN": ("SCHWENKEN", ["sshkchdy"], "gelernter Schlussbefehl", "einmal schwenken oder bewegen", "Schwenke den Posten und schliesse."),
    "W07_PFLANZENTEIL": ("PFLANZENTEIL", ["dchey", "sh"], "zwei bildgebundene Karten", "Wurzel | Staengel", "Die Zeichnung waehlt Wurzel oder Staengel."),
    "W08_WASCHEN": ("WASCHEN", ["rshedy", "lkedy"], "gelernter Schlussbefehl", "Waschgang | nachwaschen", "Fuehre den Waschgang aus und schliesse."),
    "W09_AUFTRAGEN": ("AUFTRAGEN", ["cheeckhody"], "gelernter Schlussbefehl", "bereiteten Posten auftragen", "Trage den Posten auf und schliesse."),
    "W10_FUELLEN": ("FUELLEN", ["ytey"], "offene gelernte Handlungskarte", "aktives Gefaess oder Station fuellen", "Fuelle den bezeichneten Empfaenger."),
    "W11_KLARLAUF": ("KLARLAUF", ["cheey|shey"], "wiederkehrende gelernte Produktkarte", "klarer Ablauf oder Klarauszug", "Nimm den klaren Lauf als neuen Posten."),
    "W12_TRENNEN": ("TRENNEN", ["cfhy", "cphy"], "gepaart gelernte Handlungskarten", "auswringen | nachseihen", "Trenne zuerst grob und danach fein."),
    "W13_FRISCHWASSER": ("FRISCHWASSER", ["dshedy"], "gelernter Schlussbefehl", "Frischwasser zugeben und schliessen", "Gib Frischwasser zu und schliesse."),
    "W14_VORIGES": ("VORIGES", ["dchol|schol"], "wiederkehrende gelernte Verweiskarte", "vorigen Posten wiederaufnehmen", "Nimm den im Record zuletzt aktiven Posten."),
    "W15_TEILEN": ("TEILEN", ["ches"], "offene gelernte Handlungskarte", "aktuellen Posten teilen", "Teile den aktuellen Posten."),
    "W16_BEFESTIGEN": ("BEFESTIGEN", ["qokylddy"], "gelernter Schlussbefehl", "aktuellen Posten befestigen und schliessen", "Befestige den Posten und schliesse."),
}


EXERCISE_STATEMENTS = {
    "W01_ZUSATZ": "B1-S002",
    "W02_GEFAESS": "H1-S001",
    "W03_KUEHLEN": "H3-S001",
    "W04_ROH": "B6-S001",
    "W05_TUCH": "B4-S005",
    "W06_SCHWENKEN": "B1-S003",
    "W07_PFLANZENTEIL": "H5-S003",
    "W08_WASCHEN": "B2-S019",
    "W09_AUFTRAGEN": "H5-S002",
    "W10_FUELLEN": "B1-S015",
    "W11_KLARLAUF": "B2-S010",
    "W12_TRENNEN": "H3-S001",
    "W13_FRISCHWASSER": "B2-S007",
    "W14_VORIGES": "H3-S003",
    "W15_TEILEN": "B2-S016",
    "W16_BEFESTIGEN": "B4-S004",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENTS_IN)
    phrases = read_tsv(PHRASES_IN)
    assert (len(dictionary), len(events), len(phrases)) == (173, 381, 116)
    assert {row["page"] for row in events} <= ALLOWED_PAGES

    cards_by_surface = {row["surface_family"]: row for row in dictionary}
    whole_cards = [row for row in dictionary if row["compact_architecture"] == "MEMORIZED_WHOLE_CARD"]
    assert len(whole_cards) == 22
    whole_ids = {row["joint_tuple_id"] for row in whole_cards}

    headword_for_surface: dict[str, str] = {}
    for headword_id, (_head, surfaces, _rule, _variants, _mnemonic) in HEADWORDS.items():
        for surface in surfaces:
            if surface in headword_for_surface:
                raise AssertionError(f"duplicate surface in headwords: {surface}")
            headword_for_surface[surface] = headword_id
    assert set(headword_for_surface) == {row["surface_family"] for row in whole_cards}

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_card[event["joint_tuple_id"]].append(event)
        events_by_statement[event["statement_id"]].append(event)
    phrase_map = {row["statement_id"]: row for row in phrases}

    codebook_rows: list[dict[str, str]] = []
    for card in whole_cards:
        headword_id = headword_for_surface[card["surface_family"]]
        headword, surfaces, rule, variants, mnemonic = HEADWORDS[headword_id]
        card_events = events_by_card[card["joint_tuple_id"]]
        codebook_rows.append({
            "headword_id": headword_id,
            "headword_de": headword,
            "joint_tuple_id": card["joint_tuple_id"],
            "surface_family": card["surface_family"],
            "occurrences": str(len(card_events)),
            "event_ids": "|".join(row["event_id"] for row in card_events),
            "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in card_events)),
            "pages": "|".join(dict.fromkeys(row["page"] for row in card_events)),
            "exact_card_reading_de": card["compact_reading_de"],
            "codebook_rule": rule,
            "variant_menu_de": variants,
            "apprentice_mnemonic_de": mnemonic,
            "terminal_usage": "YES" if all(row["step_closure_role"] == "COMMIT_CELL" for row in card_events) else "NO",
        })
    codebook_rows.sort(key=lambda row: (row["headword_id"], row["surface_family"]))

    headword_rows: list[dict[str, str]] = []
    for headword_id, (headword, surfaces, rule, variants, mnemonic) in HEADWORDS.items():
        selected = [cards_by_surface[surface] for surface in surfaces]
        occurrence_count = sum(len(events_by_card[card["joint_tuple_id"]]) for card in selected)
        headword_rows.append({
            "headword_id": headword_id,
            "headword_de": headword,
            "exact_card_types": str(len(selected)),
            "occurrences": str(occurrence_count),
            "surface_families": ";".join(surfaces),
            "exact_readings_de": "|".join(card["compact_reading_de"] for card in selected),
            "codebook_rule": rule,
            "variant_menu_de": variants,
            "apprentice_mnemonic_de": mnemonic,
        })

    copybook_rows: list[dict[str, str]] = []
    for phrase in phrases:
        statement_events = events_by_statement[phrase["statement_id"]]
        surfaces = [event["surface_display"] for event in statement_events]
        architecture = [
            "P" if event["compact_architecture"] == "PRODUCTIVE_COMPOSITION"
            else "p" if event["compact_architecture"] == "PARTIAL_COMPOSITION"
            else "W"
            for event in statement_events
        ]
        whole_statement_cards = [event for event in statement_events if event["joint_tuple_id"] in whole_ids]
        whole_headwords = []
        for event in whole_statement_cards:
            surface_family = next(card["surface_family"] for card in whole_cards if card["joint_tuple_id"] == event["joint_tuple_id"])
            whole_headwords.append(headword_for_surface[surface_family])
        if whole_statement_cards:
            level = "L3_CODEBOOK"
            lesson = "Look up W cards; compose P and p cards from the component table."
        elif "p" in architecture:
            level = "L2_BOUND_CARRIERS"
            lesson = "Compose the known part and memorize only the local carrier."
        else:
            level = "L1_PRODUCTIVE"
            lesson = "Write and read from productive components only."
        copybook_rows.append({
            "statement_id": phrase["statement_id"],
            "record_unit_id": phrase["record_unit_id"],
            "page": phrase["page"],
            "loci": phrase["loci"],
            "lesson_level": level,
            "surface_sequence": " ".join(surfaces),
            "architecture_sequence": " ".join(architecture),
            "whole_headword_ids": "|".join(dict.fromkeys(whole_headwords)) if whole_headwords else "NONE",
            "whole_card_count": str(len(whole_statement_cards)),
            "card_reading_sequence_de": phrase["compact_headword_sequence_de"],
            "source_instruction_de": phrase["compact_fluent_sentence_de"],
            "copy_instruction_de": "Decke die Kartenfolge ab, schreibe sie aus der deutschen Arbeitsanweisung und vergleiche danach exakt.",
            "readback_instruction_de": "Decke die deutsche Zeile ab, lies P/p aus Bauteilen und W aus dem Codebuch zurueck.",
            "teaching_note_en": lesson,
        })

    exercise_rows: list[dict[str, str]] = []
    for ordinal, (headword_id, statement_id) in enumerate(EXERCISE_STATEMENTS.items(), start=1):
        phrase = phrase_map[statement_id]
        copy = next(row for row in copybook_rows if row["statement_id"] == statement_id)
        headword, surfaces, rule, variants, mnemonic = HEADWORDS[headword_id]
        focus_cards = [cards_by_surface[surface] for surface in surfaces]
        present_surfaces = [
            event["surface_display"] for event in events_by_statement[statement_id]
            if event["joint_tuple_id"] in {card["joint_tuple_id"] for card in focus_cards}
        ]
        exercise_rows.append({
            "exercise": f"U{ordinal:02d}",
            "headword_id": headword_id,
            "headword_de": headword,
            "statement_id": statement_id,
            "page": phrase["page"],
            "source_instruction_de": phrase["compact_fluent_sentence_de"],
            "target_surface_sequence": copy["surface_sequence"],
            "target_architecture_sequence": copy["architecture_sequence"],
            "focus_surface_present": "|".join(present_surfaces),
            "compare_variants": ";".join(surfaces),
            "variant_menu_de": variants,
            "dictation_task_de": f"Schreibe die Anweisung und markiere die Ganzkarte {headword} vor dem Vergleich.",
            "readback_answer_de": phrase["compact_fluent_sentence_de"],
        })

    manual_lines = [
        "# Einseitiges Lehrlings-Codebuch",
        "",
        "## 1. Drei Zeichenklassen",
        "",
        "- `P`: aus bekannten Bauteilen zusammensetzen.",
        "- `p`: bekannten Bauteil lesen, kleinen lokalen Traeger auswendig kennen.",
        "- `W`: exakte Ganzkarte in der folgenden Liste nachschlagen.",
        "",
        "## 2. Satzgang",
        "",
        "```text",
        "BILDBESITZER",
        "-> QUELLE / ZUTAT / ANSATZ",
        "-> PORTION / SOLLMASS",
        "-> ZIEL / FOLGE / FORTSETZUNG",
        "-> BEARBEITEN / UMSETZEN / DURCHLEITEN / SAMMELN",
        "-> KURZ / LAENGER / VOLL / BEREIT",
        "-> optionale exakte SCHLUSSKARTE",
        "```",
        "",
        "Eine physische Zeile beendet den Satz nicht automatisch. Der aktive Posten kann in die naechste Zeile weitergetragen werden.",
        "",
        "## 3. Die sechzehn gelernten Kopfwoerter",
        "",
        "| Nr. | Kopfwort | sichtbare Karten | Variantenregel |",
        "|---|---|---|---|",
    ]
    for row in headword_rows:
        manual_lines.append(f"| {row['headword_id']} | {row['headword_de']} | `{row['surface_families']}` | {row['variant_menu_de']} |")
    manual_lines.extend([
        "",
        "## 4. Kopierregel",
        "",
        "1. Lies zuerst Bildbesitzer und laufenden Posten.",
        "2. Setze alle `P`-Karten aus dem Bauteilkasten.",
        "3. Bei `p` schreibe den bekannten Kern und nimm den lokalen Traeger aus dem Muster.",
        "4. Schlage nur `W` in der 22-Karten-Liste nach.",
        "5. Kopiere eine terminale Ganzkarte als unteilbaren Schlussbefehl.",
        "6. Lies die gesamte Arbeitsfolge rueckwaerts; kein Kartenwert darf sich dabei aendern.",
        "",
        "## 5. Merksatz",
        "",
        "> Bauteile werden gelesen; Ganzkarten werden erkannt; das Bild liefert den Gegenstand.",
    ])

    write_tsv(CARDS_OUT, codebook_rows)
    write_tsv(HEADS_OUT, headword_rows)
    write_tsv(COPYBOOK_OUT, copybook_rows)
    write_tsv(EXERCISES_OUT, exercise_rows)
    MANUAL_OUT.write_text("\n".join(manual_lines).rstrip() + "\n", encoding="utf-8")

    level_counts = Counter(row["lesson_level"] for row in copybook_rows)
    summary = {
        "status": "PASS",
        "whole_card_types": len(codebook_rows),
        "whole_card_occurrences": sum(int(row["occurrences"]) for row in codebook_rows),
        "headwords": len(headword_rows),
        "copybook_statements": len(copybook_rows),
        "exercises": len(exercise_rows),
        "lesson_levels": dict(level_counts),
        "files": {},
    }
    for path in [CARDS_OUT, HEADS_OUT, COPYBOOK_OUT, EXERCISES_OUT, MANUAL_OUT]:
        summary["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
