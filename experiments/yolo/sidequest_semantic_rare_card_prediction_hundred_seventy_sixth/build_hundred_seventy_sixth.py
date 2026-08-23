#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CURRENT = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"
PARSE = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_173_LITERAL_PARSE.tsv"
RULES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/SURFACE_COMPILER_RULES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    current = {row["master_card_id"]: row for row in read(CURRENT)}
    parses = read(PARSE)
    rules = {row["atom"]: row for row in read(RULES)}
    cards_by_atom: dict[str, set[str]] = defaultdict(set)
    for row in parses:
        for atom in row["literal_predictive_atoms"].split("+"):
            if atom != "NONE":
                cards_by_atom[atom].add(row["master_card_id"])

    rare_rows = []
    exception_rows = []
    for row in parses:
        card = current[row["master_card_id"]]
        if int(card["event_count"]) > 2:
            continue
        literal = row["literal_predictive_atoms"]
        learned = row["learned_or_contextual_atoms"]
        atoms = [] if literal == "NONE" else literal.split("+")
        support = {atom: len(cards_by_atom[atom] - {row["master_card_id"]}) for atom in atoms}
        if literal == "NONE":
            status = "MEMORIZED_WHOLE_CARD"
        elif learned != "NONE":
            status = "COMPOSED_FRAME_PLUS_MEMORIZED_BODY"
        elif all(count >= 1 for count in support.values()):
            status = "FULLY_COMPOSED_FROM_OTHER_CARDS"
        else:
            status = "THIN_COMPONENT_SUPPORT"
        gloss = " -> ".join(rules[atom]["short_value_de"] for atom in atoms) if atoms else card["portable_card_value_de"]
        rare = {
            "master_card_id": row["master_card_id"],
            "master_form": card["master_form"],
            "registered_surfaces": card["registered_surfaces"],
            "event_count": card["event_count"],
            "records": card["records"],
            "current_value_de": card["portable_card_value_de"],
            "literal_atoms": literal,
            "predicted_component_gloss_de": gloss,
            "other_card_support_by_atom": "|".join(f"{atom}:{support[atom]}" for atom in atoms) or "NONE",
            "memorized_body": learned,
            "prediction_status": status,
            "teaching_rule_de": "aus Bausteinen lesen" if status == "FULLY_COMPOSED_FROM_OTHER_CARDS" else "Rahmen lesen Innenkoerper lernen" if status == "COMPOSED_FRAME_PLUS_MEMORIZED_BODY" else "als unteilbare Ganzkarte lernen",
        }
        rare_rows.append(rare)
        if status != "FULLY_COMPOSED_FROM_OTHER_CARDS":
            exception_rows.append(rare)
    write(OUT / "HUNDRED_SEVENTY_SIXTH_143_RARE_CARD_PREDICTIONS.tsv", rare_rows)
    write(OUT / "HUNDRED_SEVENTY_SIXTH_19_EXCEPTION_DECK.tsv", exception_rows)

    atom_rows = []
    for atom, rule in rules.items():
        atom_rows.append(
            {
                "atom": atom,
                "short_value_de": rule["short_value_de"],
                "rule_category": rule["rule_category"],
                "card_support": len(cards_by_atom[atom]),
                "supported_card_ids": "|".join(sorted(cards_by_atom[atom])),
                "rare_card_prediction_use": sum(atom in (row["literal_predictive_atoms"].split("+") if row["literal_predictive_atoms"] != "NONE" else []) and int(current[row["master_card_id"]]["event_count"]) <= 2 for row in parses),
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SIXTH_29_ATOM_SUPPORT.tsv", atom_rows)

    showcase_ids = ["MC044", "MC054", "MC036", "MC022", "MC140", "MC169", "MC085", "MC015", "MC133", "MC173"]
    by_id = {row["master_card_id"]: row for row in rare_rows}
    showcase = []
    for index, card_id in enumerate(showcase_ids, 1):
        row = by_id[card_id]
        showcase.append(
            {
                "prediction": index,
                "master_card_id": card_id,
                "visible_form": row["master_form"],
                "components": row["literal_atoms"],
                "component_prediction_de": row["predicted_component_gloss_de"],
                "current_workshop_value_de": row["current_value_de"],
                "why_useful_de": "seltene Karte wird ohne neuen Ganzwert aus dem gemeinsamen Lehrsatz lesbar",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SIXTH_10_SHOWCASE_PREDICTIONS.tsv", showcase)

    counts = defaultdict(int)
    events = defaultdict(int)
    for row in rare_rows:
        counts[row["prediction_status"]] += 1
        events[row["prediction_status"]] += int(row["event_count"])
    summary = {
        "input_sha256": {
            CURRENT.name: hashlib.sha256(CURRENT.read_bytes()).hexdigest(),
            PARSE.name: hashlib.sha256(PARSE.read_bytes()).hexdigest(),
            RULES.name: hashlib.sha256(RULES.read_bytes()).hexdigest(),
        },
        "rare_cards": len(rare_rows),
        "rare_events": sum(int(row["event_count"]) for row in rare_rows),
        "status_cards": dict(counts),
        "status_events": dict(events),
        "productive_atoms": len(atom_rows),
        "exception_deck": len(exception_rows),
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
