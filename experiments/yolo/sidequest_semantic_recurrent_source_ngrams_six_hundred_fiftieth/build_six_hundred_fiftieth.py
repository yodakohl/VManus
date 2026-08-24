#!/usr/bin/env python3
"""Build a source-near grammar from recurrent exact-card bigrams/trigrams."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    instance_rows: list[dict[str, object]] = []
    aggregates: dict[tuple[int, tuple[str, ...]], list[dict[str, object]]] = defaultdict(list)
    for statement_id, rows in by_statement.items():
        for n in (2, 3):
            for start in range(len(rows) - n + 1):
                window = rows[start:start + n]
                card_ids = tuple(row["card_no"] for row in window)
                item = {
                    "n": n,
                    "statement_id": statement_id,
                    "page": rows[0]["page"],
                    "record": rows[0]["record"],
                    "case_id": rows[0]["case_id"],
                    "start_position": start + 1,
                    "start_event": window[0]["event_id"],
                    "card_sequence": "|".join(card_ids),
                    "surface_sequence": " ".join(row["surface"] for row in window),
                    "command_sequence_de": " → ".join(row["standard_command_de"] for row in window),
                }
                instance_rows.append(item)
                aggregates[(n, card_ids)].append(item)

    grammar_rows: list[dict[str, object]] = []
    for (n, card_ids), instances in aggregates.items():
        if len(instances) < 2:
            continue
        statements = sorted({str(row["statement_id"]) for row in instances})
        records = sorted({str(row["record"]) for row in instances})
        pages = sorted({str(row["page"]) for row in instances})
        cases = sorted({str(row["case_id"]) for row in instances})
        surfaces = sorted({str(row["surface_sequence"]) for row in instances})
        if len(records) >= 2:
            status = "PORTABLE_SOURCE_CONSTRUCTION"
        elif len(statements) >= 2:
            status = "RECORD_LOCAL_RECURRENT_CONSTRUCTION"
        else:
            status = "WITHIN_STATEMENT_REPETITION"
        grammar_rows.append({
            "construction_id": "SRC" + str(n) + "_" + "_".join(card_ids),
            "n": n,
            "card_sequence": "|".join(card_ids),
            "command_sequence_de": str(instances[0]["command_sequence_de"]),
            "occurrences": len(instances),
            "statements": len(statements),
            "records": len(records),
            "pages": len(pages),
            "cases": len(cases),
            "statement_ids": "|".join(statements),
            "record_ids": "|".join(records),
            "page_ids": "|".join(pages),
            "case_ids": "|".join(cases),
            "surface_realizations": " || ".join(surfaces),
            "construction_status": status,
            "short_workshop_reading_de": str(instances[0]["command_sequence_de"]),
            "source_only": "YES",
        })
    grammar_rows.sort(key=lambda row: (int(row["n"]), -int(row["occurrences"]), str(row["card_sequence"])))

    recurrent_keys = {(int(row["n"]), tuple(str(row["card_sequence"]).split("|"))) for row in grammar_rows}
    recurrent_instance_rows = [
        row for row in instance_rows if (int(row["n"]), tuple(str(row["card_sequence"]).split("|"))) in recurrent_keys
    ]

    statement_rows: list[dict[str, object]] = []
    for statement_id, rows in by_statement.items():
        local = [row for row in recurrent_instance_rows if row["statement_id"] == statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "case_id": rows[0]["case_id"],
            "event_count": len(rows),
            "surface_sequence": " ".join(row["surface"] for row in rows),
            "card_sequence": "|".join(row["card_no"] for row in rows),
            "recurrent_bigram_instances": sum(int(row["n"]) == 2 for row in local),
            "recurrent_trigram_instances": sum(int(row["n"]) == 3 for row in local),
            "recurrent_source_constructions": " || ".join(sorted({str(row["card_sequence"]) for row in local})) if local else "NONE",
        })
    statement_rows.sort(key=lambda row: (str(row["record"]), str(row["statement_id"])))

    status_counts = Counter(str(row["construction_status"]) for row in grammar_rows)
    summary_rows = []
    for n in (2, 3):
        relevant_instances = [row for row in instance_rows if int(row["n"]) == n]
        relevant_grammar = [row for row in grammar_rows if int(row["n"]) == n]
        summary_rows.append({
            "n": n,
            "source_instances": len(relevant_instances),
            "distinct_types": len({row["card_sequence"] for row in relevant_instances}),
            "recurrent_types": len(relevant_grammar),
            "recurrent_instances": sum(int(row["occurrences"]) for row in relevant_grammar),
            "portable_types": sum(row["construction_status"] == "PORTABLE_SOURCE_CONSTRUCTION" for row in relevant_grammar),
            "record_local_types": sum(row["construction_status"] == "RECORD_LOCAL_RECURRENT_CONSTRUCTION" for row in relevant_grammar),
            "within_statement_types": sum(row["construction_status"] == "WITHIN_STATEMENT_REPETITION" for row in relevant_grammar),
        })

    write_tsv(HERE / "SIX_HUNDRED_FIFTIETH_RECURRENT_SOURCE_GRAMMAR.tsv", grammar_rows, list(grammar_rows[0]) if grammar_rows else ["construction_id"])
    write_tsv(HERE / "SIX_HUNDRED_FIFTIETH_RECURRENT_NGRAM_INSTANCES.tsv", recurrent_instance_rows, list(recurrent_instance_rows[0]) if recurrent_instance_rows else ["n"])
    write_tsv(HERE / "SIX_HUNDRED_FIFTIETH_116_STATEMENT_SOURCE_GRAMMAR.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTIETH_2_NGRAM_SUMMARY.tsv", summary_rows, list(summary_rows[0]))

    md = [
        "# Wirklich wiederkehrende Quellfolgen",
        "",
        "Nur exakte Kartenpaare und -dreier mit mindestens zwei Vorkommen innerhalb der 116 tatsächlichen Aussagen werden aufgenommen.",
        "",
    ]
    if grammar_rows:
        for row in grammar_rows:
            md.extend([
                f"## {row['construction_id']}",
                "",
                f"- Karten: `{row['card_sequence']}`",
                f"- Lesung: {row['short_workshop_reading_de']}",
                f"- Vorkommen: {row['occurrences']} in {row['statements']} Aussagen, {row['records']} Records",
                f"- Status: {row['construction_status']}",
                f"- Oberflächen: `{row['surface_realizations']}`",
                "",
            ])
    else:
        md.append("Es gibt keine mindestens zweimal vorkommende exakte Kartenfolge der Länge zwei oder drei.")
    (HERE / "SIX_HUNDRED_FIFTIETH_SOURCE_GRAMMAR_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(statement_rows),
        "events": sum(int(row["event_count"]) for row in statement_rows),
        "bigram_instances": next(row["source_instances"] for row in summary_rows if row["n"] == 2),
        "trigram_instances": next(row["source_instances"] for row in summary_rows if row["n"] == 3),
        "recurrent_bigram_types": next(row["recurrent_types"] for row in summary_rows if row["n"] == 2),
        "recurrent_trigram_types": next(row["recurrent_types"] for row in summary_rows if row["n"] == 3),
        "portable_types": status_counts["PORTABLE_SOURCE_CONSTRUCTION"],
        "record_local_types": status_counts["RECORD_LOCAL_RECURRENT_CONSTRUCTION"],
        "within_statement_types": status_counts["WITHIN_STATEMENT_REPETITION"],
        "statements_with_recurrent_source_construction": sum(row["recurrent_source_constructions"] != "NONE" for row in statement_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "SOURCE_NEAR_GRAMMAR_RESTRICTED_TO_RECURRENT_EXACT_NGRAMS",
    }
    (HERE / "SIX_HUNDRED_FIFTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
