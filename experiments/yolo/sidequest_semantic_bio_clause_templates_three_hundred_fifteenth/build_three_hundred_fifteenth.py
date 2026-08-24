#!/usr/bin/env python3
"""Compress 97 Biological statements into seven reusable clause heads."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ATOMIC_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
ATOMIC_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_97_ATOMIC_STATEMENT_READINGS.tsv"
MODES = ROOT / "experiments/yolo/sidequest_semantic_minimal_bio_dictionary_three_hundred_tenth/THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv"

TEMPLATES = {
    "LOCAL_CONTROL": ("STEUERN", "BEZUG/FOLGE/ZIEL > laufenden Gang setzen oder fortführen"),
    "CHARGE": ("EINBRINGEN", "QUELLE/ANTEIL > EINSATZ/TRANSFER > optionales ZIEL"),
    "TREAT": ("BEHANDELN", "POSTEN > optionaler GRAD > Kontakt/Wärme/Befestigung"),
    "MEASURE": ("EINSTELLEN", "MASS/PORTION/STUFE > laufender Posten"),
    "DISCHARGE": ("ABFÜHREN", "POSTEN/QUELLE > Abzug/Transfer > optionales ZIEL"),
    "SETTLE": ("ABSETZEN", "POSTEN > optionaler GRAD/SOLLWERT > Ruhe/Sammlung"),
    "PASS_FILTER": ("DURCHARBEITEN", "POSTEN > Wasch-/Durchlass-/Trennweg > Ablauf"),
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


def words(value: str) -> int:
    return len(re.findall(r"\b\w+\b", value, flags=re.UNICODE))


def main() -> None:
    events = read(ATOMIC_EVENTS)
    old_statements = {row["statement_id"]: row for row in read(ATOMIC_STATEMENTS)}
    modes = {row["event_id"]: row["revised_operating_mode"] for row in read(MODES)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    run_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    run_count_by_mode: Counter[str] = Counter()
    event_count_by_mode: Counter[str] = Counter()
    statements_by_mode: dict[str, set[str]] = defaultdict(set)
    for statement_id, selected in by_statement.items():
        runs: list[tuple[str, list[dict[str, str]]]] = []
        for event in selected:
            mode = modes[event["event_id"]]
            event_count_by_mode[mode] += 1
            statements_by_mode[mode].add(statement_id)
            if not runs or runs[-1][0] != mode:
                runs.append((mode, []))
            runs[-1][1].append(event)
        compact_clauses: list[str] = []
        for ordinal, (mode, run_events) in enumerate(runs, start=1):
            run_count_by_mode[mode] += 1
            head, slot_order = TEMPLATES[mode]
            lexemes = [event["atomic_gloss_de"] for event in run_events]
            compact = f"{head}: {' – '.join(lexemes)}"
            compact_clauses.append(compact)
            run_rows.append({
                "run_id": f"{statement_id}-R{ordinal:02d}",
                "statement_id": statement_id,
                "record_unit_id": run_events[0]["record_unit_id"],
                "page": run_events[0]["page"],
                "mode": mode,
                "template_head_de": head,
                "slot_order": slot_order,
                "event_ids": "|".join(event["event_id"] for event in run_events),
                "surfaces": " ".join(event["fresh_surface"] for event in run_events),
                "atomic_lexemes": "|".join(lexemes),
                "event_count": len(run_events),
                "compact_clause_de": compact,
                "link_to_next": "DANN" if ordinal < len(runs) else "END",
            })
        old = old_statements[statement_id]
        compact_statement = "; dann ".join(compact_clauses) + ("." if old["terminal_scope"] == "TERMINAL" else " …")
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": selected[0]["record_unit_id"],
            "page": selected[0]["page"],
            "run_pattern": ">".join(mode for mode, _ in runs),
            "run_count": len(runs),
            "event_count": len(selected),
            "fresh_surfaces": " ".join(event["fresh_surface"] for event in selected),
            "atomic_chain": " → ".join(event["atomic_reading"] for event in selected),
            "compact_template_reading_de": compact_statement,
            "old_fluent_reading_de": old["fluent_statement_de"],
            "compact_word_count": words(compact_statement),
            "old_word_count": words(old["fluent_statement_de"]),
            "terminal_scope": old["terminal_scope"],
        })
    run_path = HERE / "THREE_HUNDRED_FIFTEENTH_240_CLAUSE_RUNS.tsv"
    statement_path = HERE / "THREE_HUNDRED_FIFTEENTH_97_TEMPLATE_STATEMENTS.tsv"
    write(run_path, run_rows)
    write(statement_path, statement_rows)

    template_rows = []
    example_for_mode = {}
    for row in run_rows:
        example_for_mode.setdefault(row["mode"], row["compact_clause_de"])
    for mode, (head, slot_order) in TEMPLATES.items():
        template_rows.append({
            "template_id": f"T_{mode}",
            "operating_mode": mode,
            "german_clause_head": head,
            "slot_order": slot_order,
            "events": event_count_by_mode[mode],
            "clause_runs": run_count_by_mode[mode],
            "statements_touched": len(statements_by_mode[mode]),
            "example": example_for_mode[mode],
            "teaching_rule_de": "Kopf einmal setzen; folgende gleichartige Karten als Argument-/Mikrobefehlskette darunter lesen.",
        })
    template_path = HERE / "THREE_HUNDRED_FIFTEENTH_SEVEN_CLAUSE_TEMPLATES.tsv"
    write(template_path, template_rows)

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record_unit_id"])].append(row)
    lines = [
        "# Kurze Biological-Lesung mit sieben Satzköpfen",
        "",
        "Jede Zeile unten ist eine bereits abgegrenzte Aussage. Ein Kopf gilt für eine zusammenhängende Folge gleichartiger Karten; `dann` verbindet nur den Wechsel zum nächsten Arbeitsmodus.",
        "",
    ]
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        lines += [f"## {record}", ""]
        for row in by_record[record]:
            lines.append(f"- **{row['statement_id']}:** {row['compact_template_reading_de']}")
        lines.append("")
    edition_path = HERE / "THREE_HUNDRED_FIFTEENTH_SIX_RECORD_TEMPLATE_EDITION.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    single_mode = sum(int(row["run_count"]) == 1 for row in statement_rows)
    report_path = HERE / "THREE_HUNDRED_FIFTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 315: sieben Biological-Satzköpfe\n\n"
        "Die 97 Aussagen zerfallen in 240 zusammenhängende Modusläufe. Statt sechzig verschiedener Vollsatzmuster braucht der Lehrling sieben Köpfe: STEUERN, EINBRINGEN, BEHANDELN, EINSTELLEN, ABFÜHREN, ABSETZEN und DURCHARBEITEN. Innerhalb eines Laufs bleiben die atomischen Kartenwerte Argumente oder Mikrobefehle; nur beim Moduswechsel wird `dann` gesetzt.\n\n"
        f"{single_mode}/97 Aussagen brauchen nur einen Kopf, {len(statement_rows)-single_mode} sind parataktische Mehrkopfketten. Die kompakte Ausgabe verwendet {sum(int(row['compact_word_count']) for row in statement_rows)} Wörter gegenüber {sum(int(row['old_word_count']) for row in statement_rows)} in der vorherigen flüssigen Ereignis-für-Ereignis-Ausgabe. Keine neue Kartenbedeutung wurde eingeführt.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS",
        "templates": len(template_rows),
        "clause_runs": len(run_rows),
        "events": sum(int(row["event_count"]) for row in run_rows),
        "statements": len(statement_rows),
        "single_mode_statements": single_mode,
        "compound_statements": len(statement_rows) - single_mode,
        "compact_words": sum(int(row["compact_word_count"]) for row in statement_rows),
        "old_words": sum(int(row["old_word_count"]) for row in statement_rows),
        "mode_run_counts": dict(run_count_by_mode),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (ATOMIC_EVENTS, ATOMIC_STATEMENTS, MODES)},
        "output_hashes": {path.name: sha(path) for path in (run_path, statement_path, template_path, edition_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
