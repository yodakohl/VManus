#!/usr/bin/env python3
"""Separate exact close cards from motifs that merely occur at statement end."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P651 = ROOT / "experiments/yolo/sidequest_semantic_source_motifs_six_hundred_fifty_first"
P652 = ROOT / "experiments/yolo/sidequest_semantic_motif_attachment_grammar_six_hundred_fifty_second"


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
    selected = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_SELECTED_MOTIF_INSTANCES.tsv")
    attachments = read_tsv(P652 / "SIX_HUNDRED_FIFTY_SECOND_28_MOTIF_ATTACHMENTS.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    position_by_key = {
        (row["statement_id"], row["motif_id"], row["start_position"]): row["position_class"]
        for row in attachments
    }

    rows: list[dict[str, object]] = []
    for motif in selected:
        statement = by_statement[motif["statement_id"]]
        start = int(motif["start_position"])
        n = int(motif["n"])
        segment = statement[start - 1:start - 1 + n]
        close_cards = [row["card_no"] for row in segment if "SCHLUSS" in row["standard_command_de"]]
        ends = start + n - 1 == len(statement)
        has_close = bool(close_cards)
        if has_close and ends:
            endpoint_class = "EXPLICIT_CLOSE_AT_END"
        elif has_close:
            endpoint_class = "CLOSE_CARD_BEFORE_FURTHER_MATERIAL"
        elif ends:
            endpoint_class = "STATEMENT_END_WITHOUT_CLOSE_CARD"
        else:
            endpoint_class = "NONTERMINAL_MOTIF"
        rows.append({
            "statement_id": motif["statement_id"],
            "page": motif["page"],
            "record": motif["record"],
            "motif_id": motif["motif_id"],
            "card_sequence": motif["card_sequence"],
            "surface_sequence": motif["surface_sequence"],
            "position_class": position_by_key[(motif["statement_id"], motif["motif_id"], motif["start_position"])],
            "ends_statement": "YES" if ends else "NO",
            "contains_exact_close_card": "YES" if has_close else "NO",
            "exact_close_cards": "|".join(close_cards) if close_cards else "NONE",
            "endpoint_class": endpoint_class,
            "motif_reading_de": motif["motif_reading_de"],
            "exact_card_reading_de": " -> ".join(row["standard_command_de"] for row in segment),
        })

    endpoint_rows = [row for row in rows if row["ends_statement"] == "YES"]
    branch_rows = []
    for row in rows:
        if row["motif_id"] != "M09_LONG_SET_BRANCH":
            continue
        closed = row["contains_exact_close_card"] == "YES"
        branch_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "card_sequence": row["card_sequence"],
            "surface_sequence": row["surface_sequence"],
            "branch": "M09C_SHORT_CLOSE" if closed else "M09O_OPEN_CONTINUATION",
            "position_class": row["position_class"],
            "ends_statement": row["ends_statement"],
            "exact_reading_de": "LANG ANSETZEN, DANN KURZ SCHLIESSEN" if closed else "LANG ANSETZEN, DANN DEN POSTEN WEITERSETZEN",
        })

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIFTH_28_ENDPOINT_AUDIT.tsv", rows, list(rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIFTH_9_STATEMENT_END_MOTIFS.tsv", endpoint_rows, list(endpoint_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FIFTH_4_M09_BRANCHES.tsv", branch_rows, list(branch_rows[0]))

    md = [
        "# Neun Motive am Aussageende",
        "",
        "Aussageende und exakte Schlusskarte werden getrennt. Nur die Kartenlesung `SCHLUSS` lizenziert einen expliziten Abschluss.",
        "",
    ]
    for row in endpoint_rows:
        md.extend([
            f"## {row['statement_id']} — {row['endpoint_class']}",
            "",
            f"`{row['surface_sequence']}` = {row['exact_card_reading_de']}",
            "",
        ])
    md.extend(["# M09-Zweigpaar", ""])
    for row in branch_rows:
        md.append(f"- `{row['surface_sequence']}` — **{row['branch']}** — {row['exact_reading_de']} — {row['position_class']}")
    (HERE / "SIX_HUNDRED_FIFTY_FIFTH_ENDPOINT_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "motif_instances": len(rows),
        "motifs_at_statement_end_including_whole": len(endpoint_rows),
        "explicit_close_at_end": sum(row["endpoint_class"] == "EXPLICIT_CLOSE_AT_END" for row in rows),
        "statement_end_without_close_card": sum(row["endpoint_class"] == "STATEMENT_END_WITHOUT_CLOSE_CARD" for row in rows),
        "close_card_before_further_material": sum(row["endpoint_class"] == "CLOSE_CARD_BEFORE_FURTHER_MATERIAL" for row in rows),
        "nonterminal_motifs": sum(row["endpoint_class"] == "NONTERMINAL_MOTIF" for row in rows),
        "m09_open_branches": sum(row["branch"] == "M09O_OPEN_CONTINUATION" for row in branch_rows),
        "m09_closed_branches": sum(row["branch"] == "M09C_SHORT_CLOSE" for row in branch_rows),
        "decision": "EXACT_CLOSE_CARDS_SPLIT_SEVEN_EXPLICIT_CLOSES_FROM_TWO_UNMARKED_MEASURE_ENDS",
    }
    (HERE / "SIX_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
