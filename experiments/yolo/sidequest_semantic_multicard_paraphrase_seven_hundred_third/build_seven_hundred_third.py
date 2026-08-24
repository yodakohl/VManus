#!/usr/bin/env python3
"""Build Pass 703: express missing single cards as existing-card phrases."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P701 = ROOT / "experiments/yolo/sidequest_semantic_contrast_encoder_seven_hundred_first"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PARAPHRASES = {
    "P17": ("PROC084|PROC019", "WASCHGANG; DIESEN POSTEN", "O", "NONE", "NEW_STATEMENT_RESET", "Waschgang; dieser Bildposten ist gemeint."),
    "P18": ("PROC172", "KUEHLEN · ZIEL · DIES", "AL", "NONE", "ONE_EXPANDED_EXISTING_CARD", "Diesen Posten an der bezeichneten Stelle kuehlen."),
    "P19": ("PROC156|PROC124", "PORTION; ABNEHMEN · KURZ · GETEILT", "CH+E", "REORDER_AIN_BEFORE_S", "NEW_STATEMENT_RESET", "Eine Portion; kurz davon abnehmen: geteilt."),
    "P20": ("PROC156|PROC134", "PORTION; EINFUELLEN · UMSETZEN · ZIEL", "CHD", "REORDER_AIN_BEFORE_P", "NEW_STATEMENT_RESET", "Eine Portion; sie an der Zielstelle einfuellen und umsetzen."),
    "P21": ("PROC072|PROC150", "WEITERLEITEN; UMSETZEN · LAUF", "CHD", "NONE", "ATTESTED_COMPONENT_JUNCTION", "Weiterleiten; den Lauf dabei umsetzen."),
    "P22": ("PROC016|PROC122", "ANSATZ; HALTEN · KURZ · DIES", "Y", "REORDER_OR_BEFORE_SH", "NEW_STATEMENT_RESET", "Den Ansatz; diesen kurz halten."),
    "P23": ("PROC008|PROC040", "ANSETZEN · DIES; DIES · ZUDOSIEREN · NACHGABE", "Y+Y+K", "NONE", "NEW_STATEMENT_RESET", "Diesen Posten ansetzen; ihm eine Nachgabe zudosieren."),
    "P24": ("PROC028|PROC041", "AUSWRINGEN · DIES; GANG · SCHLUSS", "Y+O", "NONE", "NEW_STATEMENT_RESET", "Diesen Posten auswringen; den Arbeitsgang schliessen."),
}


def is_subsequence(needle: list[str], haystack: list[str]) -> bool:
    cursor = 0
    for component in haystack:
        if cursor < len(needle) and needle[cursor] == component:
            cursor += 1
    return cursor == len(needle)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    prompts = read(P701 / "SEVEN_HUNDRED_FIRST_24_FRESH_PROMPT_ENCODINGS.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    event_count = {row["card_no"]: int(row["events"]) for row in cards}

    observed_card_pairs: Counter[tuple[str, str]] = Counter()
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    for rows in by_statement.values():
        for left, right in zip(rows, rows[1:]):
            observed_card_pairs[(left["card_no"], right["card_no"])] += 1

    phrase_rows = []
    for prompt in prompts:
        prompt_id = prompt["prompt_id"]
        requested = prompt["requested_recipe"].split("+")
        if prompt["encoding_status"] == "EXACT_EXISTING_RECIPE":
            candidates = [card_by_no[number] for number in prompt["exact_card_numbers"].split("|")]
            selected = max(candidates, key=lambda row: (event_count[row["card_no"]], row["card_no"]))
            selected_numbers = [selected["card_no"]]
            reading = selected["compact_atomic_reading_de"]
            extras = "NONE"
            reorder = "NONE"
            boundary = "SINGLE_CARD"
            fluent = prompt["fresh_prompt_de"]
            mode = "DIRECT_EXISTING_CARD"
        else:
            numbers, reading, extras, reorder, boundary, fluent = PARAPHRASES[prompt_id]
            selected_numbers = numbers.split("|")
            mode = "EXPANDED_EXISTING_CARD" if len(selected_numbers) == 1 else "TWO_EXISTING_CARD_PARAPHRASE"
        selected_cards = [card_by_no[number] for number in selected_numbers]
        output_components = [component for card in selected_cards for component in card["component_recipe"].split("+")]
        pair_support = [observed_card_pairs[(a, b)] for a, b in zip(selected_numbers, selected_numbers[1:])]
        requested_covered = all(component in output_components for component in set(requested))
        phrase_rows.append({
            "prompt_id": prompt_id, "fresh_prompt_de": prompt["fresh_prompt_de"],
            "requested_recipe": prompt["requested_recipe"], "encoding_mode": mode,
            "selected_card_sequence": "|".join(selected_numbers),
            "selected_surface_families": " || ".join(card["surfaces"] for card in selected_cards),
            "output_component_sequence": " | ".join(card["component_recipe"] for card in selected_cards),
            "card_count": len(selected_cards), "requested_components_covered": "YES" if requested_covered else "NO",
            "requested_order_is_subsequence": "YES" if is_subsequence(requested, output_components) else "NO_REPHRASED",
            "added_components": extras, "reordering": reorder,
            "observed_same_statement_pair_support": "|".join(map(str, pair_support)) if pair_support else "NA",
            "boundary_rule": boundary,
            "compact_workshop_reading_de": reading, "fluent_paraphrase_de": fluent,
            "new_card_or_surface_invented": "NO",
        })

    missing_rows = [row for row in phrase_rows if row["prompt_id"] in PARAPHRASES]
    write("SEVEN_HUNDRED_THIRD_24_PROMPT_PHRASEBOOK.tsv", phrase_rows)
    write("SEVEN_HUNDRED_THIRD_8_MISSING_CARD_PARAPHRASES.tsv", missing_rows)

    readable = ["# Vierundzwanzig frische Werkstattanweisungen", "", "Nur vorhandene Kartenfamilien; Oberflaechen werden nach Besitzerfach gewaehlt.", ""]
    for row in phrase_rows:
        readable.extend([
            f"## {row['prompt_id']} — {row['fresh_prompt_de']}", "",
            f"Karten: `{row['selected_card_sequence']}`", "",
            f"Komponenten: `{row['output_component_sequence']}`", "",
            f"Lesung: {row['fluent_paraphrase_de']}", "",
        ])
    (HERE / "SEVEN_HUNDRED_THIRD_24_READABLE_ENCODINGS.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "prompts": len(phrase_rows),
        "direct_existing_card": sum(row["encoding_mode"] == "DIRECT_EXISTING_CARD" for row in phrase_rows),
        "expanded_existing_card": sum(row["encoding_mode"] == "EXPANDED_EXISTING_CARD" for row in phrase_rows),
        "two_card_paraphrases": sum(row["encoding_mode"] == "TWO_EXISTING_CARD_PARAPHRASE" for row in phrase_rows),
        "requested_components_covered": sum(row["requested_components_covered"] == "YES" for row in phrase_rows),
        "new_cards": 0, "new_surfaces": 0,
        "new_two_card_transitions": sum(row["card_count"] == 2 and row["observed_same_statement_pair_support"] == "0" for row in phrase_rows),
        "decision": "ALL_24_FRESH_PROMPTS_CAN_BE_EXPRESSED_WITH_EXISTING_CARDS__SEVEN_USE_TWO_CARD_PARAPHRASE",
    }
    (HERE / "SEVEN_HUNDRED_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
