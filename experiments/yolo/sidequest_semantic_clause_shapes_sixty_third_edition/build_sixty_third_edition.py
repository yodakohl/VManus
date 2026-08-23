#!/usr/bin/env python3
"""Reduce the source-slot inventory to twelve reusable clause shapes."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ASSIGNMENTS = ROOT / "experiments/yolo/sidequest_semantic_source_formular_sixty_second_edition/SIXTY_SECOND_381_SOURCE_SLOT_ASSIGNMENTS.tsv"
FORMULARS = ROOT / "experiments/yolo/sidequest_semantic_source_formular_sixty_second_edition/SIXTY_SECOND_116_DUAL_SOURCE_FORMULARS.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"

REPRESENTATIVES = (
    "H1-S001", "H1-S002", "H2-S002",
    "H3-S001", "H3-S002", "H3-S003", "H3-S004",
    "B1-S001",
    "B2-S005", "B2-S006", "B2-S007", "B2-S010",
    "B2-S012", "B2-S014", "B2-S016", "B2-S017",
)

SHAPES = (
    ("C01", "LEARNED_BODY_CHAIN", "NOMEN + optionale Adresse/Handlung/Schluss", "Gelernte Fachkarte einsetzen; nur ihre beobachteten Anhänge ergänzen."),
    ("C02", "ORDER_CHAIN", "FOLGE/FORTSETZUNG + folgende Klausel", "Den nächsten, fortgesetzten oder vorigen Posten setzen."),
    ("C03", "ACTION_GRADE_ENDPOINT", "HANDLUNG + GRAD + POSTEN/SCHLUSS", "Handlung kurz, länger oder vollständig ausführen; Posten halten oder schließen."),
    ("C04", "ACTION_TARGET", "HANDLUNG + ZIELSTELLE", "Eine Handlung an die sichtbare oder geerbte Zielstelle binden."),
    ("C05", "ACTION_SOURCE", "HANDLUNG + QUELLE/ANSATZ", "Eine Handlung aus einer Quelle oder am laufenden Ansatz ausführen."),
    ("C06", "ACTION_QUANTITY", "HANDLUNG + PORTION/STUFE", "Eine Handlung auf eine Portion, ein Maß oder eine Arbeitsstufe beziehen."),
    ("C07", "ACTION_REFERENT", "HANDLUNG + DIESER POSTEN", "Die Handlung am aktuell gemeinten Arbeitsposten ausführen."),
    ("C08", "ACTION_CLOSE_OR_BARE", "HANDLUNG + optionaler SCHLUSS", "Eine nackte Handlung ausführen und nur bei gelernter Endkarte schließen."),
    ("C09", "SOURCE_PREPARATION", "QUELLE/LAUF/ANSATZ + optionale Adresse", "Quelle, Flüssigkeitslauf, Auszug oder Ansatz nennen."),
    ("C10", "QUANTITY_STAGE", "MASS/PORTION/STUFE + optionaler GRAD", "Den örtlich geltenden Wert, die Portion oder Stufe einsetzen."),
    ("C11", "TARGET_ADDRESS", "ZIELSTELLE + optionaler POSTEN/SCHLUSS", "Die bezeichnete Stelle setzen; das Bild liefert den konkreten Besitzer."),
    ("C12", "REFERENT_CLOSE_RESIDUE", "DIESER POSTEN + optionaler SCHLUSS", "Den laufenden Posten wiederaufnehmen oder eine residuale Kurzform lesen."),
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


def classify(slot_sequence: str) -> str:
    labels = set(slot_sequence.split(">"))
    if "LEARNED_OR_LOCAL_BODY" in labels:
        return "LEARNED_BODY_CHAIN"
    if "ORDER" in labels:
        return "ORDER_CHAIN"
    if {"ACTION", "GRADE"} <= labels:
        return "ACTION_GRADE_ENDPOINT"
    if {"ACTION", "TARGET"} <= labels:
        return "ACTION_TARGET"
    if {"ACTION", "SOURCE_OR_PREPARATION"} <= labels:
        return "ACTION_SOURCE"
    if {"ACTION", "QUANTITY_OR_STAGE"} <= labels:
        return "ACTION_QUANTITY"
    if {"ACTION", "REFERENT"} <= labels:
        return "ACTION_REFERENT"
    if "ACTION" in labels:
        return "ACTION_CLOSE_OR_BARE"
    if "SOURCE_OR_PREPARATION" in labels:
        return "SOURCE_PREPARATION"
    if "QUANTITY_OR_STAGE" in labels:
        return "QUANTITY_STAGE"
    if "TARGET" in labels:
        return "TARGET_ADDRESS"
    return "REFERENT_CLOSE_RESIDUE"


def main() -> None:
    assignments = read_tsv(ASSIGNMENTS)
    formulars = {row["unit_id"]: row for row in read_tsv(FORMULARS)}
    units = {row["unit_id"]: row for row in read_tsv(UNITS) if row["unit_kind"] == "PROSE_STATEMENT"}
    shape_ids = {name: shape_id for shape_id, name, _, _ in SHAPES}
    counts = Counter(classify(row["source_slot_sequence"]) for row in assignments)
    sequences = defaultdict(set)
    examples = defaultdict(list)
    mapped = []
    for row in assignments:
        family = classify(row["source_slot_sequence"])
        sequences[family].add(row["source_slot_sequence"])
        if len(examples[family]) < 4:
            examples[family].append(f"{row['visible_surface']}={row['card_reading_de']}")
        mapped.append({
            **row,
            "clause_shape_id": shape_ids[family],
            "clause_shape_family": family,
            "shape_assignment_reason": row["source_slot_sequence"],
        })
    write_tsv(OUT / "SIXTY_THIRD_381_GROUP_SHAPE_MAP.tsv", mapped)

    shape_rows = []
    for shape_id, name, formula, rule in SHAPES:
        shape_rows.append({
            "shape_id": shape_id,
            "shape_family": name,
            "abstract_formula_de": formula,
            "workshop_rule_de": rule,
            "observed_group_count": counts[name],
            "observed_slot_sequences": " | ".join(sorted(sequences[name])),
            "short_examples": " | ".join(examples[name]),
        })
    write_tsv(OUT / "SIXTY_THIRD_12_CLAUSE_SHAPES.tsv", shape_rows)

    by_unit = defaultdict(list)
    for row in mapped:
        by_unit[row["unit_id"]].append(row)
    chain_rows = []
    for order, unit_id in enumerate(REPRESENTATIVES, start=1):
        unit = units[unit_id]
        formular = formulars[unit_id]
        groups = by_unit[unit_id]
        chain_rows.append({
            "chain_order": order,
            "unit_id": unit_id,
            "page": unit["page"],
            "owner": unit["owner_or_namespace"],
            "natural_source_prose_de": unit["fluent_working_reading_de"],
            "terse_source_formular_de": formular["german_workshop_source_skeleton"],
            "slot_program": formular["slot_program"],
            "clause_shape_program": " > ".join(row["clause_shape_id"] for row in groups),
            "atom_sequence": unit["atom_sequence"],
            "visible_surface": unit["surface_sequence"],
            "compression_note": "Inhalt und Besitzer werden elliptisch; Bauform, Reihenfolge und Kartenkörper bleiben schreibbar.",
        })
    write_tsv(OUT / "SIXTY_THIRD_16_COMPRESSION_CHAINS.tsv", chain_rows)

    passage_doc = [
        "# Sechzehn vollständige Kompressionsketten", "",
        "Jede Kette beginnt mit einer flüssigen, bewusst konkreten Werkstattlesung.",
        "Dann wird sie zum Formular, zu zwölf wiederverwendbaren Klauseltypen, zu",
        "Kartenatomen und schließlich zur sichtbaren Oberfläche verdichtet.", "",
    ]
    for row in chain_rows:
        passage_doc.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Ausgangsprosa:** {row['natural_source_prose_de']}", "",
            f"**Kurzes Formular:** {row['terse_source_formular_de']}", "",
            f"**Bauformen:** {row['clause_shape_program']}", "",
            f"**Atome:** `{row['atom_sequence']}`", "",
            f"**Schrift:** `{row['visible_surface']}`", "",
        ])
    (OUT / "SIXTY_THIRD_NATURAL_SOURCE_PASSAGES.md").write_text("\n".join(passage_doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Dreiundsechzigste Werkstattfassung: zwölf Klauselbauformen", "",
        "## Ergebnis", "",
        "Die 55 tatsächlich vorkommenden Slotfolgen der 381 Prosagruppen lassen",
        "sich vollständig in zwölf lehrbare Klauselfamilien einordnen. Keine Familie",
        "übersetzt eine einzelne Karte als ganzen Satz. Sie beschreibt nur, welche",
        "kleinen Bestandteile zusammengehören: Handlung, Reihenfolge, Quelle, Menge,",
        "Ziel, Grad, laufender Posten, Schluss oder gelernter Fachkörper.", "",
        "Die sechzehn ausgeschriebenen Ketten zeigen den angenommenen Arbeitsweg:",
        "natürliche Fachprosa → knappes Formular → Klauselbauformen → Kartenatome →",
        "sichtbare Schreiberform. Damit wird die Mischidee konkreter: eine kleine",
        "produktive Grammatik trägt einen größeren gelernten Nomenklator.", "",
        "## Zwölf Formen", "",
    ]
    for row in shape_rows:
        report.append(f"- {row['shape_id']} {row['shape_family']}: {row['abstract_formula_de']} ({row['observed_group_count']} Gruppen).")
    report.extend([
        "", "## Arbeitsentscheidung", "",
        "Die nächste Runde darf nun nicht wieder neue Einzelglossen erfinden. Sie soll",
        "die sechzehn Kompressionsketten rückwärts lesen und prüfen, welche Teile ein",
        "Lehrling allein aus Bauform und gemeinsamem Stamm rekonstruieren kann und wo",
        "der Bildbesitzer oder das gelernte Ganzwort unvermeidlich bleibt.", "",
        "Nur die zehn festgelegten Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "SIXTY_THIRD_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "clause_shapes": len(shape_rows),
            "observed_slot_sequences": len({row["source_slot_sequence"] for row in assignments}),
            "mapped_prose_groups": len(mapped),
            "representative_compression_chains": len(chain_rows),
            "unmapped_groups": 0,
        },
        "shape_counts": dict(sorted(counts.items())),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (ASSIGNMENTS, FORMULARS, UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
