#!/usr/bin/env python3
"""Map the five composed case templates back onto all 116 source statements."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P631 = ROOT / "experiments/yolo/sidequest_semantic_five_branch_composition_six_hundred_thirty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def longest_contacts(statement_cards: list[str], template_cards: dict[str, list[str]]) -> list[dict[str, object]]:
    contacts: list[dict[str, object]] = []
    best = 0
    for case_id, template in template_cards.items():
        for source_start in range(len(statement_cards)):
            for template_start in range(len(template)):
                length = 0
                while source_start + length < len(statement_cards) and template_start + length < len(template) and statement_cards[source_start + length] == template[template_start + length]:
                    length += 1
                if length > best:
                    best = length
                    contacts = []
                if length and length == best:
                    contacts.append({
                        "case_id": case_id,
                        "source_start": source_start,
                        "template_start": template_start,
                        "length": length,
                        "cards": statement_cards[source_start:source_start + length],
                    })
    unique = {}
    for item in contacts:
        key = (item["case_id"], item["source_start"], item["template_start"], tuple(item["cards"]))
        unique[key] = item
    return list(unique.values())


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    masters = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv")
    template_cards = {row["intended_case_id"]: row["card_sequence"].split("|") for row in masters}
    template_surfaces = {row["intended_case_id"]: row["surface_sequence"].split() for row in masters}

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    statement_rows: list[dict[str, object]] = []
    for statement_id, rows in by_statement.items():
        cards = [row["card_no"] for row in rows]
        surfaces = [row["surface"] for row in rows]
        contacts = longest_contacts(cards, template_cards)
        max_length = int(contacts[0]["length"]) if contacts else 0
        best_cases = sorted({str(item["case_id"]) for item in contacts})
        best_runs = sorted({"|".join(str(card) for card in item["cards"]) for item in contacts})
        best_surface_runs = sorted({" ".join(surfaces[int(item["source_start"]):int(item["source_start"]) + int(item["length"])]) for item in contacts})
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "source_case": rows[0]["case_id"],
            "event_count": len(rows),
            "surface_sequence": " ".join(surfaces),
            "card_sequence": "|".join(cards),
            "longest_contiguous_template_run": max_length,
            "best_template_cases": "|".join(best_cases) if best_cases else "NONE",
            "best_card_run": " || ".join(best_runs) if best_runs else "NONE",
            "best_surface_run": " || ".join(best_surface_runs) if best_surface_runs else "NONE",
            "contact_class": (
                "NO_TEMPLATE_CARD"
                if max_length == 0
                else "SINGLE_CARD_ONLY"
                if max_length == 1
                else "ATTESTED_TEMPLATE_BIGRAM"
                if max_length == 2
                else "ATTESTED_TEMPLATE_RUN"
                if max_length < 6
                else "FULL_TEMPLATE"
            ),
            "full_six_card_template_present": "YES" if max_length == 6 else "NO",
        })
    statement_rows.sort(key=lambda row: int(str(row["statement_id"]).split("S")[-1]) if str(row["statement_id"]).split("S")[-1].isdigit() else str(row["statement_id"]))

    event_card_counts = Counter(row["card_no"] for row in events)
    position_rows: list[dict[str, object]] = []
    for case_id in sorted(template_cards):
        for position, (surface, card_id) in enumerate(zip(template_surfaces[case_id], template_cards[case_id]), 1):
            statements = sorted({row["statement_id"] for row in events if row["card_no"] == card_id})
            position_rows.append({
                "case_id": case_id,
                "template_position": position,
                "surface": surface,
                "card_no": card_id,
                "source_event_occurrences": event_card_counts[card_id],
                "source_statements": len(statements),
                "source_statement_ids": "|".join(statements) if statements else "NONE",
            })

    bigram_rows: list[dict[str, object]] = []
    for case_id in sorted(template_cards):
        template = template_cards[case_id]
        for position in range(5):
            left, right = template[position:position + 2]
            hits = []
            for statement_id, rows in by_statement.items():
                cards = [row["card_no"] for row in rows]
                for index in range(len(cards) - 1):
                    if cards[index:index + 2] == [left, right]:
                        hits.append(f"{statement_id}:{rows[index]['event_id']}")
            bigram_rows.append({
                "case_id": case_id,
                "template_left_position": position + 1,
                "template_right_position": position + 2,
                "surface_bigram": f"{template_surfaces[case_id][position]} {template_surfaces[case_id][position + 1]}",
                "card_bigram": f"{left}|{right}",
                "source_occurrences": len(hits),
                "source_hits": "|".join(hits) if hits else "NONE",
                "source_attested": "YES" if hits else "NO",
            })

    distribution = Counter(int(row["longest_contiguous_template_run"]) for row in statement_rows)
    distribution_rows = [{
        "longest_run": length,
        "statements": distribution[length],
        "fraction": f"{distribution[length]}/116",
    } for length in range(0, 7)]

    write_tsv(HERE / "SIX_HUNDRED_FORTY_NINTH_116_STATEMENT_CONTACT.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_NINTH_30_TEMPLATE_POSITION_COUNTS.tsv", position_rows, list(position_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_NINTH_25_TEMPLATE_BIGRAM_COUNTS.tsv", bigram_rows, list(bigram_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_NINTH_7_RUN_DISTRIBUTION.tsv", distribution_rows, list(distribution_rows[0]))

    attested = [row for row in bigram_rows if row["source_attested"] == "YES"]
    md = [
        "# Rückkehr zu den 116 tatsächlichen Aussagen",
        "",
        f"Der längste zusammenhängende Kontakt zwischen einer echten Aussage und einem der fünf Sechskarten-Lehrfälle beträgt {max(distribution)} Karten.",
        "",
        f"Von 25 Lehrfall-Bigrammen sind {len(attested)} tatsächlich als zusammenhängendes Kartenpaar in den 116 Aussagen vorhanden. Kein vollständiger Sechser steht im Quelltext.",
        "",
    ]
    for row in attested:
        md.extend([
            "## Tatsächlich belegtes Paar",
            "",
            f"- Fall: {row['case_id']}",
            f"- Oberfläche im Lehrfall: `{row['surface_bigram']}`",
            f"- Karten: `{row['card_bigram']}`",
            f"- Quelle: {row['source_hits']}",
            "",
        ])
    md.extend([
        "Die Einzelsemantik der Karten stammt weiterhin aus ihren tatsächlichen Vorkommen. Die fünf langen Lehrfälle sind jedoch produktive Werkstattkompositionen, keine wiedergefundenen Quellsätze. Die nächste Runde muss deshalb von den wirklich wiederkehrenden Quellpaaren und -dreiern ausgehen.",
    ])
    (HERE / "SIX_HUNDRED_FORTY_NINTH_SOURCE_CONTACT_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(statement_rows),
        "events": sum(int(row["event_count"]) for row in statement_rows),
        "template_positions": len(position_rows),
        "template_bigrams": len(bigram_rows),
        "attested_template_bigrams": len(attested),
        "novel_template_bigrams": sum(row["source_attested"] == "NO" for row in bigram_rows),
        "longest_contiguous_source_contact": max(int(row["longest_contiguous_template_run"]) for row in statement_rows),
        "statements_with_bigram_contact": sum(int(row["longest_contiguous_template_run"]) >= 2 for row in statement_rows),
        "full_template_occurrences": sum(row["full_six_card_template_present"] == "YES" for row in statement_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "SIX_CARD_CASES_ARE_PRODUCTIVE_EXERCISES_NOT_SOURCE_PHRASES",
    }
    (HERE / "SIX_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
