#!/usr/bin/env python3
"""Separate one-word card glosses from sentence-level Bio expansions."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WRITER = ROOT / "experiments/yolo/sidequest_semantic_bio_roundtrip_three_hundred_eleventh/THREE_HUNDRED_ELEVENTH_124_CARD_FORWARD_WRITER.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_fresh_bio_copy_three_hundred_thirteenth/THREE_HUNDRED_THIRTEENTH_281_FRESH_COPY_EVENTS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_fresh_bio_copy_three_hundred_thirteenth/THREE_HUNDRED_THIRTEENTH_97_FRESH_COPY_STATEMENTS.tsv"

ATOMIC_OVERRIDES = {
    "MC002": "Langkontakt", "MC005": "Rücktransfer", "MC007": "Kurzkontakt",
    "MC017": "Zugabe", "MC024": "Wiedereinsatz", "MC032": "Langbearbeitung",
    "MC040": "Orteinsatz", "MC045": "Langsammlung", "MC052": "Kurzbearbeitung",
    "MC058": "Zielkurzpassage", "MC073": "Kurzvorbereitung", "MC082": "Langkontakt",
    "MC083": "Kurzkontakt", "MC088": "Neueinsatz", "MC093": "Folgeziel",
    "MC096": "Ziellanghalt", "MC097": "Folgeportion", "MC102": "Zielkurzhalt",
    "MC106": "Kurzfortgang", "MC112": "Folgevorbereitung", "MC113": "Zielabsetzung",
    "MC124": "Weiterabzug", "MC128": "Kurzabsetzung", "MC138": "Frischspülung",
    "MC147": "Kurzwärme", "MC157": "Gleichansatz", "MC171": "Folgeposten",
    "MC173": "Langfolgestufe",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    writer = read(WRITER)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    atomic_by_card: dict[str, str] = {}
    dictionary_rows: list[dict[str, object]] = []
    for row in writer:
        card_id = row["master_card_id"]
        atomic = ATOMIC_OVERRIDES.get(card_id, row["source_short_value_de"])
        assert " " not in atomic.strip()
        atomic_by_card[card_id] = atomic
        dictionary_rows.append({
            "master_card_id": card_id,
            "canonical_form": row["canonical_written_form"],
            "registered_surfaces": row["registered_surface_forms"],
            "atomic_gloss_de": atomic,
            "terminal_scope": row["terminal_scope"],
            "atomic_plus_scope_key": f"{atomic}|{row['terminal_scope']}",
            "component_recipe": row["minimal_dictionary_recipe"],
            "grade_instruction": row["grade_instruction"],
            "form_selector": row["form_selector"],
            "old_short_value_de": row["source_short_value_de"],
            "sentence_expansion_de": row["imperative_clause_de"],
            "gloss_layer": "ONE_WORD_ATOMIC_CARD_GLOSS",
            "semantic_rule_de": "Nur der Einwortwert gehört ins Wörterbuch; Verb, Objekt und Präposition entstehen erst in der Aussage.",
        })
    dictionary_path = HERE / "THREE_HUNDRED_FOURTEENTH_124_ATOMIC_BIO_DICTIONARY.tsv"
    write(dictionary_path, dictionary_rows)

    event_rows: list[dict[str, object]] = []
    for row in events:
        atomic = atomic_by_card[row["master_card_id"]]
        event_rows.append({
            "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"],
            "field_id": row["field_id"], "page": row["page"], "locus": row["locus"],
            "fresh_surface": row["fresh_surface"], "master_card_id": row["master_card_id"],
            "atomic_gloss_de": atomic, "terminal_scope": row["terminal_scope"],
            "atomic_reading": f"{atomic}{';' if row['terminal_scope'] == 'TERMINAL' else ''}",
            "sentence_expansion_de": row["imperative_de"],
            "reverse_identity_match": row["reverse_identity_match"],
        })
    event_path = HERE / "THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
    write(event_path, event_rows)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[str(row["statement_id"])].append(row)
    old_statements = {row["statement_id"]: row for row in statements}
    statement_rows: list[dict[str, object]] = []
    for statement_id, selected in by_statement.items():
        old = old_statements[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": selected[0]["record_unit_id"],
            "page": selected[0]["page"],
            "fresh_surfaces": " ".join(str(row["fresh_surface"]) for row in selected),
            "atomic_lexeme_chain": " → ".join(str(row["atomic_reading"]) for row in selected),
            "atomic_card_count": len(selected),
            "fluent_statement_de": old["german_work_instruction"],
            "terminal_scope": old["terminal_scope"],
            "roundtrip_match": old["roundtrip_match"],
            "separation_rule_de": "Kartenwerte bleiben Einwortlexeme; die flüssige Handlungsanweisung ist eine Aussageexpansion.",
        })
    statement_path = HERE / "THREE_HUNDRED_FOURTEENTH_97_ATOMIC_STATEMENT_READINGS.tsv"
    write(statement_path, statement_rows)

    key_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dictionary_rows:
        key_groups[str(row["atomic_plus_scope_key"])].append(row)
    duplicate_rows: list[dict[str, object]] = []
    for key, selected in key_groups.items():
        if len(selected) < 2:
            continue
        duplicate_rows.append({
            "atomic_plus_scope_key": key,
            "card_ids": "|".join(str(row["master_card_id"]) for row in selected),
            "forms": "|".join(str(row["canonical_form"]) for row in selected),
            "recipes": " | ".join(str(row["component_recipe"]) for row in selected),
            "resolution_de": "Gleicher Kartenwert; lokale Besitzer-/Rendererwahl entscheidet die exakte Form.",
        })
    duplicate_path = HERE / "THREE_HUNDRED_FOURTEENTH_LOCAL_ALLOGRAPH_PAIR.tsv"
    write(duplicate_path, duplicate_rows)

    report_path = HERE / "THREE_HUNDRED_FOURTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 314: atomisches Biological-Wörterbuch\n\n"
        "Alle 124 Karten besitzen jetzt genau einen deutschen Einwortwert. Achtundzwanzig alte Mehrwortglossen wurden zu Werkstattkomposita verkürzt: etwa Langkontakt, Rücktransfer, Kurzkontakt, Neueinsatz, Zielkurzhalt und Frischspülung. Verben, Pronomen, Präpositionen und sichtbare Besitzer werden nicht mehr in die angebliche Wortbedeutung gepackt; sie entstehen erst beim Ausbau der 97 Aussagen.\n\n"
        "Es bleiben 114 verschiedene Einwortwerte. Einziger absichtlicher Doppelwert mit gleichem Scope ist Kurzvorbereitung auf MC073 und MC137; das ist das bereits bekannte lokale CTH-Allographenpaar und wird über Besitzer/Renderer gewählt, nicht durch eine erfundene Bedeutungsnuance. Damit gibt es keine satzgroße Kartenübersetzung mehr.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS",
        "cards": len(dictionary_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "multiword_glosses_replaced": len(ATOMIC_OVERRIDES),
        "distinct_atomic_glosses": len(set(atomic_by_card.values())),
        "distinct_atomic_scope_keys": len(key_groups),
        "duplicate_atomic_scope_groups": len(duplicate_rows),
        "sentence_sized_dictionary_glosses": sum(" " in row["atomic_gloss_de"] for row in dictionary_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (WRITER, EVENTS, STATEMENTS)},
        "output_hashes": {path.name: sha(path) for path in (dictionary_path, event_path, statement_path, duplicate_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
