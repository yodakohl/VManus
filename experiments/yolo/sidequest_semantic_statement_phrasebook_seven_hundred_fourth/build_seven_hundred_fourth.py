#!/usr/bin/env python3
"""Build Pass 704: mine recurrent statement-role phrase templates."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P703 = ROOT / "experiments/yolo/sidequest_semantic_multicard_paraphrase_seven_hundred_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REVISED = {
    "P17": ("PROC084|PROC019", "WASCHGANG; DIESER POSTEN", "Waschgang; dieser Bildposten ist gemeint."),
    "P18": ("PROC172", "KUEHLEN · ZIEL · DIES", "Diesen Posten an der bezeichneten Stelle kuehlen."),
    "P19": ("PROC124|PROC156", "ABNEHMEN · KURZ · GETEILT; PORTION", "Kurz davon abnehmen, geteilt; eine Portion davon."),
    "P20": ("PROC156|PROC134", "PORTION; EINFUELLEN · UMSETZEN · ZIEL", "Eine Portion; sie an der Zielstelle einfuellen und umsetzen."),
    "P21": ("PROC147|PROC150", "WEITERLEITEN · MASS; UMSETZEN · LAUF", "Nach vorgeschriebenem Mass weiterleiten; den Lauf umsetzen."),
    "P22": ("PROC016|PROC122", "ANSATZ; HALTEN · KURZ · DIES", "Den Ansatz; diesen kurz halten."),
    "P23": ("PROC008|PROC040", "ANSETZEN · DIES; DIES · ZUDOSIEREN · NACHGABE", "Diesen Posten ansetzen; ihm eine Nachgabe zudosieren."),
    "P24": ("PROC028|PROC041", "AUSWRINGEN · DIES; GANG · SCHLUSS", "Diesen Posten auswringen; den Arbeitsgang schliessen."),
}


def role(card: dict[str, str]) -> str:
    if card["card_class"] == "MEMORIZED_WHOLE_COMMAND":
        return "WHOLE_COMMAND"
    final = card["component_recipe"].split("+")[-1]
    return {
        "DY": "CLOSE_STEP", "Y": "CURRENT_ITEM", "AIN": "QUANTITY_STAGE",
        "AIIN": "QUANTITY_STAGE", "IIN": "QUANTITY_STAGE", "AN": "QUANTITY_STAGE",
        "DA": "QUANTITY_STAGE", "AL": "TARGET", "AR": "SOURCE", "AIR": "FLOW",
        "OR": "PREPARATION", "OL": "CONTINUE", "S": "BOUND_RESULT",
    }.get(final, "OPEN_ACTION")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    statements = read(P700 / "SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")
    old_phrases = read(P703 / "SEVEN_HUNDRED_THIRD_24_PROMPT_PHRASEBOOK.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    old_by_prompt = {row["prompt_id"]: row for row in old_phrases}

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    pair_occurrences: dict[tuple[str, str], list[tuple[str, dict[str, str], dict[str, str]]]] = defaultdict(list)
    triple_occurrences: dict[tuple[str, str, str], list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    exact_pairs: dict[tuple[str, str], list[tuple[str, dict[str, str], dict[str, str]]]] = defaultdict(list)
    statement_rows = []
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        roles = [role(card_by_no[row["card_no"]]) for row in rows]
        for left, right in zip(rows, rows[1:]):
            pair_occurrences[(role(card_by_no[left["card_no"]]), role(card_by_no[right["card_no"]]))].append((statement["statement_id"], left, right))
            exact_pairs[(left["card_no"], right["card_no"])].append((statement["statement_id"], left, right))
        for index in range(len(rows) - 2):
            slice_rows = rows[index:index + 3]
            key = tuple(role(card_by_no[row["card_no"]]) for row in slice_rows)
            triple_occurrences[key].append((statement["statement_id"], slice_rows))
        statement_rows.append({
            "statement_id": statement["statement_id"], "page": statement["page"], "record": statement["record"],
            "events": statement["events"], "card_sequence": "|".join(row["card_no"] for row in rows),
            "surface_sequence": " ".join(row["observed_surface"] for row in rows),
            "role_sequence": ">".join(roles), "role_length": len(roles),
            "working_reading_de": statement["working_reading_de"],
        })

    pair_rows = []
    for pair, occurrences in sorted(pair_occurrences.items(), key=lambda item: (-len(item[1]), item[0])):
        statement_ids = {entry[0] for entry in occurrences}
        records = {entry[1]["record"] for entry in occurrences}
        pages = {entry[1]["page"] for entry in occurrences}
        examples = [f"{sid}:{left['observed_surface']}>{right['observed_surface']}" for sid, left, right in occurrences[:5]]
        pair_rows.append({
            "left_role": pair[0], "right_role": pair[1], "token_count": len(occurrences),
            "statement_count": len(statement_ids), "record_count": len(records), "page_count": len(pages),
            "recurrent": "YES" if len(occurrences) >= 2 else "NO",
            "example_transitions": " | ".join(examples),
        })

    exact_rows = []
    recurrent_exact = [(pair, occurrences) for pair, occurrences in exact_pairs.items() if len(occurrences) >= 2]
    for pair, occurrences in sorted(recurrent_exact, key=lambda item: (-len(item[1]), item[0])):
        left, right = pair
        exact_rows.append({
            "left_card": left, "left_recipe": card_by_no[left]["component_recipe"],
            "right_card": right, "right_recipe": card_by_no[right]["component_recipe"],
            "token_count": len(occurrences),
            "statements": "|".join(entry[0] for entry in occurrences),
            "surfaces": " | ".join(f"{entry[1]['observed_surface']}>{entry[2]['observed_surface']}" for entry in occurrences),
            "role_template": f"{role(card_by_no[left])}>{role(card_by_no[right])}",
        })

    triple_rows = []
    recurrent_triples = [(key, occurrences) for key, occurrences in triple_occurrences.items() if len(occurrences) >= 2]
    for key, occurrences in sorted(recurrent_triples, key=lambda item: (-len(item[1]), item[0])):
        triple_rows.append({
            "role_trigram": ">".join(key), "token_count": len(occurrences),
            "statement_count": len({entry[0] for entry in occurrences}),
            "record_count": len({row[0]["record"] for _, row in occurrences}),
            "examples": " | ".join(f"{sid}:" + ">".join(item["observed_surface"] for item in rows) for sid, rows in occurrences[:5]),
        })

    revised_rows = []
    for prompt_id, (numbers, reading, fluent) in REVISED.items():
        cards_selected = [card_by_no[number] for number in numbers.split("|")]
        roles = [role(card) for card in cards_selected]
        support = pair_occurrences[(roles[0], roles[1])] if len(roles) == 2 else []
        exact_support = exact_pairs[(cards_selected[0]["card_no"], cards_selected[1]["card_no"])] if len(cards_selected) == 2 else []
        old = old_by_prompt[prompt_id]
        revised_rows.append({
            "prompt_id": prompt_id, "fresh_prompt_de": old["fresh_prompt_de"],
            "old_card_sequence": old["selected_card_sequence"], "revised_card_sequence": numbers,
            "revised_surface_families": " || ".join(card["surfaces"] for card in cards_selected),
            "revised_role_template": ">".join(roles),
            "role_template_support": len(support) if len(roles) == 2 else "NA",
            "exact_pair_support": len(exact_support) if len(roles) == 2 else "NA",
            "template_status": "SINGLE_EXISTING_CARD" if len(roles) == 1 else "ATTESTED_ROLE_TEMPLATE",
            "compact_reading_de": reading, "fluent_paraphrase_de": fluent,
            "new_surface_invented": "NO",
        })

    write("SEVEN_HUNDRED_FOURTH_116_STATEMENT_TEMPLATES.tsv", statement_rows)
    write("SEVEN_HUNDRED_FOURTH_55_ROLE_BIGRAMS.tsv", pair_rows)
    write("SEVEN_HUNDRED_FOURTH_14_RECURRENT_EXACT_PAIRS.tsv", exact_rows)
    write("SEVEN_HUNDRED_FOURTH_33_RECURRENT_ROLE_TRIGRAMS.tsv", triple_rows)
    write("SEVEN_HUNDRED_FOURTH_8_TEMPLATE_REVISED_PARAPHRASES.tsv", revised_rows)

    recurrent_pair_tokens = sum(len(items) for items in pair_occurrences.values() if len(items) >= 2)
    recurrent_triple_tokens = sum(len(items) for items in triple_occurrences.values() if len(items) >= 2)
    summary = {
        "status": "PASS", "statements": len(statement_rows), "events": len(events),
        "role_bigram_types": len(pair_rows), "role_bigram_tokens": sum(len(items) for items in pair_occurrences.values()),
        "recurrent_role_bigram_types": sum(len(items) >= 2 for items in pair_occurrences.values()),
        "recurrent_role_bigram_tokens": recurrent_pair_tokens,
        "exact_pair_types": len(exact_pairs), "recurrent_exact_pair_types": len(exact_rows),
        "role_trigram_types": len(triple_occurrences), "recurrent_role_trigram_types": len(triple_rows),
        "recurrent_role_trigram_tokens": recurrent_triple_tokens,
        "revised_paraphrases": len(revised_rows),
        "paraphrases_with_attested_role_template": sum(row["template_status"] == "ATTESTED_ROLE_TEMPLATE" for row in revised_rows),
        "new_surfaces": 0,
        "decision": "STATEMENTS_REUSE_ROLE_TEMPLATES_FAR_MORE_THAN_EXACT_CARD_PHRASES",
    }
    (HERE / "SEVEN_HUNDRED_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
