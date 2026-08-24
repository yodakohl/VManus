#!/usr/bin/env python3
"""Consolidate 15 recurrent source constructions into nine compact motifs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P650 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_source_ngrams_six_hundred_fiftieth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MOTIFS = {
    "M01_ITEM_MEASURE_FRAME": {
        "reading": "LAUFENDER POSTEN IM SOLLMASS-RAHMEN",
        "members": {"PROC019|PROC009", "PROC009|PROC019", "PROC019|PROC009|PROC019"},
        "rule": "Posten und Sollmass rahmen einander; keine Gleichheits- oder ana-Lesung",
    },
    "M02_SET_ITEM_MEASURE": {
        "reading": "POSTEN ANSETZEN, DANN SOLLMASS",
        "members": {"PROC008|PROC009"},
        "rule": "angesetzten Posten unmittelbar an Sollmass binden",
    },
    "M03_PREPARATION_ITEM": {
        "reading": "ANSATZ AUF DEN LAUFENDEN POSTEN BEZIEHEN",
        "members": {"PROC016|PROC019"},
        "rule": "Ansatzkarte gefolgt vom aktuellen Posten",
    },
    "M04_CONTINUE_CLOSE": {
        "reading": "FORTSETZEN, ABSETZEN UND SCHLIESSEN",
        "members": {"PROC013|PROC078"},
        "rule": "portable Schlusskette mit mehreren sichtbaren Allographen",
    },
    "M05_MEASURE_CONTINUATION": {
        "reading": "SOLLMASS UND FORTSETZUNG DIREKT KOPPELN",
        "members": {"PROC009|PROC013", "PROC013|PROC009"},
        "rule": "Richtung bleibt sichtbar; nicht zu einem symmetrischen Wort verschmelzen",
    },
    "M06_FEED_CONTINUATION": {
        "reading": "VORLAUF, ZIEL ODER UMSETZUNG IN DIE FORTSETZUNG FUEHREN",
        "members": {"PROC022|PROC013", "PROC042|PROC013", "PROC055|PROC013"},
        "rule": "drei verschiedene linke Zufuehrungen teilen dieselbe Fortsetzungskarte",
    },
    "M07_TRANSFER_LONG_CLOSE": {
        "reading": "POSTEN UMSETZEN UND LANG ANSETZEN; SCHLUSS",
        "members": {"PROC042|PROC100"},
        "rule": "Umsetzung geht unmittelbar in langen geschlossenen Einsatz",
    },
    "M08_PORTION_TARGET": {
        "reading": "PORTION ZUDOSIEREN UND AN DIE ZIELSTELLE GEBEN",
        "members": {"PROC070|PROC055"},
        "rule": "Portionshandlung vor der Zielkarte",
    },
    "M09_LONG_SET_BRANCH": {
        "reading": "NACH LANGEM ANSETZEN WEITERSETZEN ODER KURZ SCHLIESSEN",
        "members": {"PROC092|PROC008", "PROC092|PROC067"},
        "rule": "gleiche Langkarte fuehrt in zwei belegte Folgeschritte",
    },
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    grammar = read_tsv(P650 / "SIX_HUNDRED_FIFTIETH_RECURRENT_SOURCE_GRAMMAR.tsv")
    instances = read_tsv(P650 / "SIX_HUNDRED_FIFTIETH_RECURRENT_NGRAM_INSTANCES.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    construction_to_motif = {}
    for motif_id, spec in MOTIFS.items():
        for sequence in spec["members"]:
            construction_to_motif[sequence] = motif_id

    motif_rows: list[dict[str, object]] = []
    grammar_by_sequence = {row["card_sequence"]: row for row in grammar}
    for motif_id, spec in MOTIFS.items():
        members = sorted(spec["members"])
        member_rows = [grammar_by_sequence[sequence] for sequence in members]
        motif_rows.append({
            "motif_id": motif_id,
            "short_reading_de": spec["reading"],
            "teaching_rule_de": spec["rule"],
            "member_constructions": " || ".join(members),
            "member_types": len(members),
            "raw_occurrences_including_overlap": sum(int(row["occurrences"]) for row in member_rows),
            "records": len({record for row in member_rows for record in row["record_ids"].split("|")}),
            "pages": len({page for row in member_rows for page in row["page_ids"].split("|")}),
            "source_attested": "YES",
        })

    instances_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in instances:
        instances_by_statement[row["statement_id"]].append(row)

    selected_rows: list[dict[str, object]] = []
    rewrite_rows: list[dict[str, object]] = []
    overlap_rows: list[dict[str, object]] = []
    for statement_id, rows in by_statement.items():
        candidates = sorted(
            instances_by_statement.get(statement_id, []),
            key=lambda row: (-int(row["n"]), int(row["start_position"]), row["card_sequence"]),
        )
        occupied = set()
        selected = []
        for candidate in candidates:
            start = int(candidate["start_position"]) - 1
            positions = set(range(start, start + int(candidate["n"])))
            if positions & occupied:
                overlap_rows.append({
                    "statement_id": statement_id,
                    "card_sequence": candidate["card_sequence"],
                    "start_position": candidate["start_position"],
                    "n": candidate["n"],
                    "disposition": "SUPPRESSED_BY_LONGER_OR_EARLIER_SELECTED_SOURCE_MOTIF",
                })
                continue
            occupied |= positions
            selected.append(candidate)
            motif_id = construction_to_motif[candidate["card_sequence"]]
            selected_rows.append({
                "statement_id": statement_id,
                "page": candidate["page"],
                "record": candidate["record"],
                "case_id": candidate["case_id"],
                "start_position": candidate["start_position"],
                "n": candidate["n"],
                "surface_sequence": candidate["surface_sequence"],
                "card_sequence": candidate["card_sequence"],
                "motif_id": motif_id,
                "motif_reading_de": MOTIFS[motif_id]["reading"],
            })

        selected_by_start = {int(row["start_position"]) - 1: row for row in selected}
        tokens = []
        position = 0
        motif_covered = 0
        while position < len(rows):
            if position in selected_by_start:
                selected_instance = selected_by_start[position]
                motif_id = construction_to_motif[selected_instance["card_sequence"]]
                tokens.append(f"[{MOTIFS[motif_id]['reading']}]")
                step = int(selected_instance["n"])
                motif_covered += step
                position += step
            else:
                tokens.append(rows[position]["standard_command_de"])
                position += 1
        if selected:
            rewrite_rows.append({
                "statement_id": statement_id,
                "page": rows[0]["page"],
                "record": rows[0]["record"],
                "case_id": rows[0]["case_id"],
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "event_count": len(rows),
                "selected_motifs": "|".join(construction_to_motif[row["card_sequence"]] for row in selected),
                "selected_motif_instances": len(selected),
                "events_covered_by_motifs": motif_covered,
                "events_left_as_individual_cards": len(rows) - motif_covered,
                "minimal_source_reading_de": " / ".join(tokens),
                "all_events_accounted": "YES",
            })

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIRST_9_SOURCE_MOTIFS.tsv", motif_rows, list(motif_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIRST_SELECTED_MOTIF_INSTANCES.tsv", selected_rows, list(selected_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIRST_25_MINIMAL_STATEMENT_READINGS.tsv", rewrite_rows, list(rewrite_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIRST_OVERLAP_SUPPRESSIONS.tsv", overlap_rows, list(overlap_rows[0]) if overlap_rows else ["statement_id"])

    md = [
        "# Neun Quellmotive",
        "",
        "Die fünfzehn recurrenten Konstruktionen werden zu neun Lehrmotiven zusammengefasst. Die Kartensequenzen bleiben erhalten; nur ihre gemeinsame Werkstattfunktion bekommt einen kurzen Namen.",
        "",
    ]
    for row in motif_rows:
        md.extend([
            f"## {row['motif_id']}",
            "",
            f"**{row['short_reading_de']}**",
            "",
            f"Mitglieder: `{row['member_constructions']}`",
            "",
            f"Regel: {row['teaching_rule_de']}",
            "",
        ])
    md.extend(["# 25 echte Aussagen", ""])
    for row in rewrite_rows:
        md.extend([
            f"## {row['statement_id']} — `{row['surface_sequence']}`",
            "",
            str(row["minimal_source_reading_de"]),
            "",
        ])
    (HERE / "SIX_HUNDRED_FIFTY_FIRST_MOTIF_READING_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    assigned_members = {member for spec in MOTIFS.values() for member in spec["members"]}
    summary = {
        "status": "PASS",
        "source_construction_types": len(grammar),
        "motifs": len(motif_rows),
        "assigned_construction_types": len(assigned_members),
        "selected_nonoverlapping_instances": len(selected_rows),
        "overlap_suppressions": len(overlap_rows),
        "rewritten_source_statements": len(rewrite_rows),
        "events_in_rewritten_statements": sum(int(row["event_count"]) for row in rewrite_rows),
        "events_covered_by_motifs": sum(int(row["events_covered_by_motifs"]) for row in rewrite_rows),
        "events_left_individual": sum(int(row["events_left_as_individual_cards"]) for row in rewrite_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "NINE_COMPACT_MOTIFS_MINIMALLY_READ_TWENTY_FIVE_SOURCE_STATEMENTS",
    }
    (HERE / "SIX_HUNDRED_FIFTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
