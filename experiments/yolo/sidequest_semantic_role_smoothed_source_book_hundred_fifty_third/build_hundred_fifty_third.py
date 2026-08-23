#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R151 = ROOT / "experiments/yolo/sidequest_semantic_open_carry_registers_hundred_fifty_first"
R152 = ROOT / "experiments/yolo/sidequest_semantic_spoken_role_grammar_hundred_fifty_second"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bare(value):
    return value.replace(" · ", " ").replace("; schließen", "").replace("; Schluss", "").strip()


def smooth(role, value):
    value = bare(value)
    if role in {"OPERATION", "OPERATION_CLOSE"}:
        return value
    if role == "OBJECT":
        return f"Arbeitsgegenstand: {value}"
    if role == "ORDERED_OBJECT":
        return f"als Nächstes: {value}"
    if role == "QUANTITY_OR_STAGE":
        replacements = {
            "Sollmaß": "nach Sollmaß", "Anteil": "einen Anteil", "weiterer Anteil": "einen weiteren Anteil",
            "Arbeitsstufe": "auf Arbeitsstufe", "Folgemaß": "nach Folgemaß",
        }
        return replacements.get(value, f"Menge/Stufe: {value}")
    if role == "ANAPHOR":
        replacements = {"dies": "dies", "davon": "davon", "vom vorigen": "vom Vorigen",
                        "dorthin": "dorthin", "danach dorthin": "danach dorthin",
                        "das nächste": "als Nächstes", "derselbe Ansatz": "mit demselben Ansatz"}
        return replacements.get(value, f"Bezug: {value}")
    if role == "LINK_OR_ORDER":
        return value
    if role in {"STATE", "STATE_CLOSE"}:
        if value in {"bereit", "fertig"}:
            return f"bis {value}"
        return f"Zustand/Phase: {value}"
    if role == "PROCESS_OR_STATE":
        return f"Prozess: {value}"
    if role == "PATH_OPERATION":
        return f"durch den örtlichen Weg: {value}"
    if role == "TRANSFER_OR_ADDRESS":
        replacements = {"Ziel": "zum Ziel", "Quelle": "von der Quelle", "Lauf": "am Lauf",
                        "dorthin": "dorthin", "abführen": "abführen", "überführen": "überführen"}
        return replacements.get(value, f"Weg/Adresse: {value}")
    raise ValueError(role)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    carry_clauses = read_tsv(R151 / "HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    role_events = read_tsv(R152 / "HUNDRED_FIFTY_SECOND_381_ROLE_EVENTS.tsv")
    by_statement = defaultdict(list)
    for row in role_events:
        by_statement[row["statement_id"]].append(row)

    smoothed = []
    for clause in carry_clauses:
        events = by_statement[clause["statement_id"]]
        segments = [smooth(event["spoken_role"], event["card_value_de"]) for event in events]
        close = clause["terminal_status"] == "TERMINAL"
        smooth_text = f"{clause['connective_de']} " + "; ".join(segments)
        if close:
            smooth_text += "; Schritt schließen"
        smooth_text += "."
        smoothed.append({
            "statement_id": clause["statement_id"], "record_unit_id": clause["record_unit_id"],
            "page": clause["page"], "boundary_from_previous": clause["boundary_from_previous"],
            "owner_trace": clause["owner_trace"], "terminal_status": clause["terminal_status"],
            "literal_card_chain_de": " | ".join(event["card_value_de"] for event in events),
            "spoken_role_sequence": ">".join(event["spoken_role"] for event in events),
            "role_expansion_de": " | ".join(f"{event['spoken_role']}={smooth(event['spoken_role'], event['card_value_de'])}" for event in events),
            "smoothed_workshop_clause_de": smooth_text,
            "smoothing_is_dictionary_value": "NO",
        })
    write_tsv("HUNDRED_FIFTY_THIRD_116_LITERAL_AND_SMOOTH_CLAUSES.tsv", smoothed)

    by_record = defaultdict(list)
    for row in smoothed:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    book = ["# Zweite, rollengeglättete Elf-Record-Ausgabe", "",
            "Every clause prints its exact short card chain first. The smoother German underneath adds only case,",
            "connective and role framing; it is never copied back into the dictionary.", ""]
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        continuous = " ".join(row["smoothed_workshop_clause_de"] for row in rows)
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "continuous_smoothed_workshop_de": continuous,
            "literal_chains_retained": "YES", "dictionary_values_changed": "NO",
        })
        book += [f"## {rid} · {rows[0]['page']}", ""]
        for row in rows:
            book += [f"- **{row['statement_id']}** literal: `{row['literal_card_chain_de']}`",
                     f"  - gesprochen: {row['smoothed_workshop_clause_de']}"]
        book.append("")
    write_tsv("HUNDRED_FIFTY_THIRD_ELEVEN_SMOOTH_RECORDS.tsv", record_rows)
    (OUT / "HUNDRED_FIFTY_THIRD_COMPLETE_LITERAL_AND_FLUENT_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertdreiundfünfzigste Runde: lesbareres Deutsch ohne Wörterbuchdrift", "",
        "All 116 clauses now have a literal card chain, role expansion and smoother workshop sentence side by side.",
        "The smoothing adds only German framing: objects are introduced as Arbeitsgegenstand, quantities as",
        "Menge/Stufe, anaphors as Bezug, states as Zustand/Phase, paths as örtlicher Weg, and transfer cards as",
        "Weg/Adresse. Exact terminal status contributes `Schritt schließen` once at the end.", "",
        "This is intentionally closer to a master reading an abbreviated register aloud than to elegant literary",
        "prose. It fixes the earlier problem where every noun was forced to sound like an imperative, while every",
        "short dictionary value and card order stays visible and unchanged.", "",
        "Next identify the clauses whose smoother reading still contains two or more generic role labels. Those are",
        "the best candidates for one concrete learned whole-card reinterpretation rather than more grammar.",
    ]
    (OUT / "HUNDRED_FIFTY_THIRD_SMOOTHING_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    generic_labels = ("Arbeitsgegenstand:", "Menge/Stufe:", "Bezug:", "Zustand/Phase:", "Prozess:", "durch den örtlichen Weg:", "Weg/Adresse:")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "statements": len(smoothed), "records": len(record_rows),
        "terminal_sentences": sum(row["terminal_status"] == "TERMINAL" for row in smoothed),
        "clauses_with_two_or_more_generic_role_labels": sum(sum(row["smoothed_workshop_clause_de"].count(label) for label in generic_labels) >= 2 for row in smoothed),
        "dictionary_values_changed": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
