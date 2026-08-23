#!/usr/bin/env python3
"""Build reusable process macros above, never inside, individual card meanings."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_clause_chain_twenty_fifth_edition/TWENTY_FIFTH_254_SOURCE_CLAUSES.tsv"
WORKED = ROOT / "experiments/yolo/sidequest_semantic_worked_dossier_thirty_seventh_edition/THIRTY_SEVENTH_26_WORK_STEPS.tsv"


# macro id, clause-family pattern, spoken workshop phrase
MACROS = [
    ("M01", ("CONTINUE", "CONTINUE", "CONTINUE"), "denselben Gang über drei Teilposten fortführen"),
    ("M02", ("SET", "CONTINUE", "SETTLE"), "ansetzen, im selben Gang weiterführen und absetzen lassen"),
    ("M03", ("TRANSFER", "CONTINUE", "LEAD_OUT"), "umsetzen, weiterführen und am Ende abführen"),
    ("M04", ("READY", "DIVIDE"), "bereitstellen und einen Teil abtrennen"),
    ("M05", ("CONTINUE", "SET"), "weiterführen und den nächsten Posten ansetzen"),
    ("M06", ("SET", "CONTINUE"), "ansetzen und im selben Gang weiterführen"),
    ("M07", ("SET", "PASSAGE"), "ansetzen und durch den örtlichen Gang führen"),
    ("M08", ("PASSAGE", "SET"), "durchleiten und am folgenden Posten ansetzen"),
    ("M09", ("SET", "READY"), "ansetzen und bereitstellen"),
    ("M10", ("SET", "SETTLE"), "ansetzen und absetzen lassen"),
    ("M11", ("CONTINUE", "SETTLE"), "weiterführen und absetzen lassen"),
    ("M12", ("READY", "SET"), "den bereitgestellten Posten ansetzen"),
    ("M13", ("TRANSFER", "SET"), "umsetzen und neu ansetzen"),
    ("M14", ("SET", "TRANSFER"), "ansetzen und umsetzen"),
    ("M15", ("TRANSFER", "CONTINUE"), "umsetzen und weiterführen"),
    ("M16", ("CONTINUE", "LEAD_OUT"), "weiterführen und abführen"),
    ("M17", ("CONTINUE", "TRANSFER"), "weiterführen und umsetzen"),
    ("M18", ("WARM", "CONTINUE"), "erwärmen und im selben Gang weiterführen"),
    ("M19", ("SET", "SET"), "zwei aufeinanderfolgende Setzungen ausführen"),
    ("M20", ("CONTINUE", "CONTINUE"), "denselben Gang über zwei Teilposten fortführen"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    clauses = read_tsv(CLAUSES)
    worked_ids = {row["statement_id"] for row in read_tsv(WORKED)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for clause in clauses:
        by_statement[clause["statement_id"]].append(clause)
    for rows in by_statement.values():
        rows.sort(key=lambda row: int(row["clause_serial"]))

    macro_meta = {macro_id: {"pattern": pattern, "spoken": spoken} for macro_id, pattern, spoken in MACROS}
    priority = sorted(MACROS, key=lambda item: (-len(item[1]), int(item[0][1:])))
    macro_occurrences: dict[str, list[tuple[str, str]]] = defaultdict(list)
    programs = []
    total_covered = 0
    total_tokens = 0
    for statement_id, rows in sorted(by_statement.items(), key=lambda item: int(item[1][0]["clause_serial"])):
        families = [row["source_clause_family"] for row in rows]
        tokens = []
        reconstructed = []
        covered = 0
        index = 0
        while index < len(rows):
            match = None
            for macro_id, pattern, spoken in priority:
                if tuple(families[index:index + len(pattern)]) == pattern:
                    match = (macro_id, pattern, spoken)
                    break
            if match:
                macro_id, pattern, spoken = match
                clause_ids = [row["clause_id"] for row in rows[index:index + len(pattern)]]
                tokens.append(f"{macro_id}[{'+'.join(clause_ids)}]")
                reconstructed.extend(pattern)
                covered += len(pattern)
                macro_occurrences[macro_id].append((statement_id, "+".join(clause_ids)))
                index += len(pattern)
            else:
                row = rows[index]
                tokens.append(f"SINGLE_{row['source_clause_family']}[{row['clause_id']}]")
                reconstructed.append(row["source_clause_family"])
                index += 1
        if reconstructed != families:
            raise RuntimeError(f"macro reconstruction failed: {statement_id}")
        total_covered += covered
        total_tokens += len(tokens)
        programs.append({
            "statement_id": statement_id,
            "record_id": rows[0]["record_id"],
            "page": rows[0]["page"],
            "clause_count": len(rows),
            "clause_family_sequence": ">".join(families),
            "macro_token_count": len(tokens),
            "macro_program": " | ".join(tokens),
            "macro_covered_clauses": covered,
            "single_clauses": len(rows) - covered,
            "compression_saved_tokens": len(rows) - len(tokens),
            "reconstructed_clause_family_sequence": ">".join(reconstructed),
        })
    write_tsv(OUT / "THIRTY_EIGHTH_116_MACRO_PROGRAMS.tsv", programs, list(programs[0]))

    macro_rows = []
    for macro_id, pattern, spoken in MACROS:
        occurrences = macro_occurrences[macro_id]
        raw = []
        for statement_id, rows in by_statement.items():
            families = [row["source_clause_family"] for row in rows]
            for index in range(len(families) - len(pattern) + 1):
                if tuple(families[index:index + len(pattern)]) == pattern:
                    raw.append((statement_id, rows[index]["record_id"], rows[index]["clause_id"]))
        macro_rows.append({
            "macro_id": macro_id,
            "clause_family_pattern": ">".join(pattern),
            "clause_length": len(pattern),
            "spoken_workshop_phrase_de": spoken,
            "raw_occurrence_count": len(raw),
            "raw_record_count": len({record for _, record, _ in raw}),
            "raw_records": "|".join(sorted({record for _, record, _ in raw})),
            "greedy_occurrence_count": len(occurrences),
            "greedy_statement_ids": "|".join(statement for statement, _ in occurrences) or "NONE",
            "semantic_level": "PROCESS_MACRO_ABOVE_CARD_LEVEL",
            "word_meaning_prohibition": "NEVER_ASSIGN_MACRO_PHRASE_TO_ONE_SURFACE_OR_CARD",
        })
    write_tsv(OUT / "THIRTY_EIGHTH_20_PROCESS_MACROS.tsv", macro_rows, list(macro_rows[0]))

    worked_programs = [row for row in programs if row["statement_id"] in worked_ids]
    write_tsv(OUT / "THIRTY_EIGHTH_WORKED_JOB_MACRO_PROGRAM.tsv", worked_programs, list(worked_programs[0]))

    lines = [
        "# Zwanzig Werkstattmakros über den Karten",
        "",
        "Ein Makro ist eine häufige Abfolge mehrerer Handlungsklauseln. Es ist keine",
        "Wortbedeutung und darf niemals auf eine einzelne sichtbare Form zurückprojiziert",
        "werden. Der Lehrling benutzt es wie einen eingeübten Handgriff.",
        "",
        "## Makros",
        "",
    ]
    for row in macro_rows:
        lines.extend([
            f"### {row['macro_id']} — `{row['clause_family_pattern']}`",
            "",
            f"Sprich: **{row['spoken_workshop_phrase_de']}**. Das Muster steht roh {row['raw_occurrence_count']}× in {row['raw_record_count']} Records; die längste-gültige Zerlegung verwendet es {row['greedy_occurrence_count']}×.",
            "",
        ])
    lines.extend([
        "## Gesamtergebnis",
        "",
        f"Die 254 Klauseln der 116 Aussagen werden zu {total_tokens} Makro- oder Einzelbefehlen.",
        f"{total_covered} Klauseln liegen innerhalb eines Mehrklauselmakros; die übrigen bleiben",
        "ehrliche Einzelhandlungen. Die ursprüngliche Klauselfolge ist aus jedem Programm",
        "wortgleich rekonstruierbar.",
        "",
        "## Der vollständig gearbeitete D2-Auftrag",
        "",
    ])
    for row in worked_programs:
        lines.append(f"- `{row['statement_id']}`: {row['macro_program']}")
    (OUT / "THIRTY_EIGHTH_WORKSHOP_MACRO_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "counts": {
            "process_macros": len(macro_rows),
            "statements": len(programs),
            "source_clauses": len(clauses),
            "macro_or_single_tokens": total_tokens,
            "macro_covered_clauses": total_covered,
            "worked_job_statements": len(worked_programs),
            "worked_job_clauses": sum(int(row["clause_count"]) for row in worked_programs),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (CLAUSES, WORKED)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
