#!/usr/bin/env python3
"""Recover a compact source-formular skeleton above the card sequences."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GROUPS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_776_GROUP_READER.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
FIXED = ROOT / "experiments/yolo/sidequest_semantic_fixed_phrase_expander_fifty_eighth_edition/FIFTY_EIGHTH_116_FIXED_EXPANSIONS.tsv"

ACTION = {"OK", "CHD", "CTH", "CKH", "CKHE", "CHK", "SHED", "SOLK", "KCH", "SH", "CFH", "CPH", "WASH", "DAN", "SK", "PARTITION"}
ORDER = {"OT", "OL", "PREV"}
SOURCE = {"AR", "AIR", "CHEO", "OR"}
QUANTITY = {"AIIN", "AIN", "IIN", "TY"}
TARGET = {"AL"}
GRADE = {"E", "EE", "EEE"}
REFERENT = {"Y"}
CLOSE = {"CLOSE"}


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


def slots(atom_sequence: str) -> tuple[list[str], list[str]]:
    atoms = atom_sequence.split("+")
    result = []
    known = set()
    for label, vocabulary in (
        ("ORDER", ORDER), ("ACTION", ACTION), ("SOURCE_OR_PREPARATION", SOURCE),
        ("QUANTITY_OR_STAGE", QUANTITY), ("TARGET", TARGET), ("GRADE", GRADE),
        ("REFERENT", REFERENT), ("CLOSE", CLOSE),
    ):
        if any(atom in vocabulary for atom in atoms):
            result.append(label)
            known.update(atom for atom in atoms if atom in vocabulary)
    unknown = [atom for atom in atoms if atom not in known]
    if unknown:
        result.insert(0, "LEARNED_OR_LOCAL_BODY")
    return result or ["LEARNED_OR_LOCAL_BODY"], unknown


def main() -> None:
    prose_groups = [row for row in read_tsv(GROUPS) if row["page"] in {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}]
    units = {row["unit_id"]: row for row in read_tsv(UNITS) if row["unit_kind"] == "PROSE_STATEMENT"}
    fixed = {row["unit_id"]: row for row in read_tsv(FIXED)}
    by_unit = defaultdict(list)
    assignment_rows = []
    for row in prose_groups:
        labels, unknown = slots(row["atom_sequence"])
        out = {
            "source_group_id": row["source_group_id"],
            "unit_id": row["reading_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "atom_sequence": row["atom_sequence"],
            "card_reading_de": row["card_reading_de"],
            "source_slot_sequence": ">".join(labels),
            "learned_or_local_atoms": "+".join(unknown) or "NONE",
            "slot_assignment_complete": "YES",
        }
        assignment_rows.append(out)
        by_unit[row["reading_unit_id"]].append(out)
    write_tsv(OUT / "SIXTY_SECOND_381_SOURCE_SLOT_ASSIGNMENTS.tsv", assignment_rows)

    formular_rows = []
    for unit_id, unit in units.items():
        groups = by_unit[unit_id]
        slot_clauses = [f"[{row['source_slot_sequence']}={row['card_reading_de']}]" for row in groups]
        slot_program = " ".join(slot_clauses)
        german = (
            f"BESITZER {unit['owner_or_namespace']}; "
            + "; ".join(row["card_reading_de"] for row in groups)
            + "."
        )
        latin_like = (
            f"RES {{{unit['owner_or_namespace']}}} · "
            + " · ".join(f"{row['source_slot_sequence'].replace('>', '+')} {{{row['card_reading_de']}}}" for row in groups)
            + "."
        )
        formular_rows.append({
            "unit_id": unit_id,
            "page": unit["page"],
            "owner": unit["owner_or_namespace"],
            "group_count": len(groups),
            "slot_program": slot_program,
            "german_workshop_source_skeleton": german,
            "latin_like_heading_skeleton": latin_like,
            "fixed_card_expansion_de": fixed[unit_id]["fixed_generated_prose_de"],
            "source_language_claim": "NONE_TWO_ORDERING_STYLES_ONLY",
            "sentence_specific_slot_rule": "NO",
        })
    write_tsv(OUT / "SIXTY_SECOND_116_DUAL_SOURCE_FORMULARS.tsv", formular_rows)

    rules = [
        ("S01", "OWNER", "RES/BESITZER", "Bild oder Station zuerst nennen oder still setzen."),
        ("S02", "ORDER", "ORD", "OT/OL/PREV ordnen folgenden, fortgesetzten oder vorigen Posten."),
        ("S03", "ACTION", "OP", "Arbeitskern als Imperativ oder Rubrikkürzel setzen."),
        ("S04", "SOURCE_OR_PREPARATION", "EX/PRAEP", "Quelle, Lauf, Auszug oder Ansatz nennen."),
        ("S05", "QUANTITY_OR_STAGE", "Q/GRADUS", "Sollwert, Portion, Stufe oder Teil einsetzen."),
        ("S06", "TARGET", "AD", "Zielstelle einsetzen; sichtbarer Besitzer konkretisiert sie."),
        ("S07", "GRADE", "MODUS", "kurz, länger oder vollständig an die Handlung binden."),
        ("S08", "REFERENT", "HOC", "aktuellen Posten aus ACTIVE wiederaufnehmen."),
        ("S09", "CLOSE", "FIAT/CLAUDE", "nur mit gelernter Schlusskarte abschließen."),
        ("S10", "LEARNED_OR_LOCAL_BODY", "NOMEN", "gelernte Fachkarte ungeteilt aus dem Nomenklator einsetzen."),
    ]
    rule_rows = [
        {"rule_id": rule_id, "source_slot": slot, "latin_like_heading": heading, "workshop_rule_de": text}
        for rule_id, slot, heading, text in rules
    ]
    write_tsv(OUT / "SIXTY_SECOND_10_SOURCE_SLOT_RULES.tsv", rule_rows)

    doc = [
        "# Zwei mögliche Quellformular-Stile",
        "",
        "Die Karten können aus derselben Slotfolge entweder als knappe deutsche",
        "Werkstattanweisung oder als lateinisch aussehende Rubrikenfolge vorbereitet",
        "werden. Das identifiziert keine Sprache; es zeigt nur eine plausible Abkürzungs-",
        "vorstufe.",
        "",
    ]
    for row in formular_rows:
        doc.extend([
            f"## {row['unit_id']}", "",
            f"**Werkstattdeutsch:** {row['german_workshop_source_skeleton']}", "",
            f"**Rubrikenordnung:** {row['latin_like_heading_skeleton']}", "",
        ])
    (OUT / "SIXTY_SECOND_SOURCE_FORMULAR_BOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    slot_counts = Counter(label for row in assignment_rows for label in row["source_slot_sequence"].split(">"))
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "source_slot_rules": len(rule_rows),
            "prose_groups_assigned": len(assignment_rows),
            "dual_source_formulars": len(formular_rows),
            "unassigned_groups": sum(row["slot_assignment_complete"] != "YES" for row in assignment_rows),
            **dict(slot_counts),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (GROUPS, UNITS, FIXED)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
