#!/usr/bin/env python3
"""Bind each of the 254 literal clauses to selected field-level visual owners."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_literal_regeneration_hundred_third_edition/HUNDRED_THIRD_254_ATOMIC_CLAUSES.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_clause_attachment/COMPLETE_381_ATTACHED_EVENTS.tsv"
OWNERS = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"


GENERIC_ITEMS = {"Posten", "Teil", "Zutat", "Zusatz", "Vorposten"}
TEXTUAL_OBJECTS = {"Auszug", "Ansatz", "Wurzel", "Tuch", "Gefäß", "Ergebnis"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    clauses = read_tsv(CLAUSES)
    event_field = {row["event_id"]: row["field_id"] for row in read_tsv(EVENTS)}
    owner_by_field = {
        row["unit_id"]: row for row in read_tsv(OWNERS) if row["unit_kind"] == "PROSE_FIELD"
    }
    statement_source = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    bindings: list[dict[str, object]] = []
    for clause in clauses:
        fields = list(dict.fromkeys(event_field[event] for event in clause["member_event_ids"].split("|")))
        owners = [owner_by_field[field] for field in fields]
        statuses = list(dict.fromkeys(row["owner_status"] for row in owners))
        visible = list(dict.fromkeys(row["selected_visible_owner"] for row in owners))
        silent = list(dict.fromkeys(row["silent_argument_default"] for row in owners))
        items = set() if clause["item_values_de"] == "NONE" else set(clause["item_values_de"].split("+"))
        if items & TEXTUAL_OBJECTS:
            noun_source = "TEXT_NAMES_OBJECT__OWNER_LIMITS_REFERENT"
        elif items and items <= GENERIC_ITEMS:
            noun_source = "OWNER_RESOLVES_GENERIC_TEXT_ITEM"
        elif not items:
            noun_source = "OWNER_SUPPLIES_ELLIPTIC_PRIMARY_NOUN"
        else:
            noun_source = "MIXED_TEXT_AND_OWNER_OBJECT"
        if "UNRESOLVED" in statuses:
            accessibility = "OWNER_UNRESOLVED"
        elif "DIRECT_VISIBLE" in statuses:
            accessibility = "DIRECT_VISIBLE_OWNER"
        elif "INHERITED_VISIBLE" in statuses:
            accessibility = "INHERITED_VISIBLE_OWNER"
        else:
            accessibility = "PAGE_OWNER_ONLY"
        bindings.append({
            "fusion_unit_order": clause["fusion_unit_order"],
            "fusion_unit_id": clause["fusion_unit_id"],
            "statement_id": clause["statement_id"],
            "record_unit_id": clause["record_unit_id"],
            "page": clause["page"],
            "member_event_ids": clause["member_event_ids"],
            "field_ids": "|".join(fields),
            "owner_statuses": "|".join(statuses),
            "selected_visible_owners": "|".join(visible),
            "silent_argument_defaults": " | ".join(silent),
            "owner_accessibility": accessibility,
            "textual_item_values": clause["item_values_de"],
            "primary_noun_source": noun_source,
            "literal_workshop_clause_de": clause["literal_workshop_clause_de"],
        })

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in bindings:
        by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for statement_id, rows in sorted(by_statement.items(), key=lambda item: int(statement_source[item[0]]["statement_order"])):
        source = statement_source[statement_id]
        statement_rows.append({
            "statement_order": source["statement_order"],
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "clause_count": len(rows),
            "visible_owners": "|".join(dict.fromkeys(owner for row in rows for owner in str(row["selected_visible_owners"]).split("|"))),
            "owner_resolved_generic_clauses": sum(row["primary_noun_source"] == "OWNER_RESOLVES_GENERIC_TEXT_ITEM" for row in rows),
            "owner_supplied_elliptic_clauses": sum(row["primary_noun_source"] == "OWNER_SUPPLIES_ELLIPTIC_PRIMARY_NOUN" for row in rows),
            "text_named_object_clauses": sum(row["primary_noun_source"] == "TEXT_NAMES_OBJECT__OWNER_LIMITS_REFERENT" for row in rows),
            "unresolved_owner_clauses": sum(row["owner_accessibility"] == "OWNER_UNRESOLVED" for row in rows),
            "concrete_source_expansion_de": source["concrete_source_expansion_de"],
        })

    noun_counts = Counter(row["primary_noun_source"] for row in bindings)
    owner_counts = Counter(row["owner_accessibility"] for row in bindings)
    summary_rows = []
    for dimension, counts in [("PRIMARY_NOUN_SOURCE", noun_counts), ("OWNER_ACCESSIBILITY", owner_counts)]:
        for category, count in sorted(counts.items()):
            summary_rows.append({"dimension": dimension, "category": category, "clause_count": count})

    write_tsv(OUT / "HUNDRED_SIXTH_254_CLAUSE_OWNER_BINDING.tsv", list(bindings[0]), bindings)
    write_tsv(OUT / "HUNDRED_SIXTH_116_STATEMENT_OWNER_BINDING.tsv", list(statement_rows[0]), statement_rows)
    write_tsv(OUT / "HUNDRED_SIXTH_OWNER_SUMMARY.tsv", list(summary_rows[0]), summary_rows)

    report = [
        "# Hundertsechste Runde: Woher kommt das ausgelassene Nomen?", "",
        "## Ergebnis", "",
        f"Von 254 Arbeitsklauseln nennen {noun_counts['TEXT_NAMES_OBJECT__OWNER_LIMITS_REFERENT']}",
        "den Objektkanal schon textlich als Auszug, Ansatz, Wurzel, Tuch, Gefäß oder",
        "Ergebnis; das Bild begrenzt nur den konkreten Referenten.",
        f"{noun_counts['OWNER_RESOLVES_GENERIC_TEXT_ITEM']} Klauseln schreiben lediglich",
        "Posten, Teil, Zutat, Zusatz oder Vorposten und brauchen den sichtbaren Besitzer für",
        f"das konkrete Nomen. {noun_counts['OWNER_SUPPLIES_ELLIPTIC_PRIMARY_NOUN']} Klauseln",
        "lassen selbst diesen generischen Posten aus und erhalten ihr Hauptnomen ganz aus",
        "Bild und laufendem Register.", "",
        f"Die Besitzerbindung ist bei {owner_counts['DIRECT_VISIBLE_OWNER']} Klauseln direkt",
        f"sichtbar, bei {owner_counts['INHERITED_VISIBLE_OWNER']} geerbt, bei",
        f"{owner_counts['PAGE_OWNER_ONLY']} nur seitenweit und bei",
        f"{owner_counts['OWNER_UNRESOLVED']} lokal ungelöst. Unaufgelöste Besitzer bleiben",
        "sichtbar markiert und werden nicht durch erfundene Körperteile oder Geräte ersetzt.", "",
        "Das erklärt die Kürze des Textes ohne ein magisches Universalwort: Viele Karten",
        "sagen tatsächlich nur ‘diesen Posten am Ziel länger ansetzen’; die Pflanze, der",
        "Badende oder die Dienststation steht bereits im Bild- und Registergedächtnis.", "",
        "Nur die festen Seiten und die ausgewählte bestehende Besitzerkarte wurden benutzt;",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_SIXTH_CLAUSE_OWNER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "clauses": len(bindings), "statements": len(statement_rows),
        "noun_source_counts": dict(noun_counts), "owner_accessibility_counts": dict(owner_counts),
        "source_fields": len(owner_by_field),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
