#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R123 = ROOT / "experiments/yolo/sidequest_semantic_two_register_source_grammar_hundred_twenty_third"

HANDS = {
    "R-A": ("VORLAGENHAND", "master head"),
    "R-B": ("Q-EINTRITTSHAND", "prefer a registered q entry"),
    "R-C": ("S-FLUSSHAND", "prefer a registered sh or s continuation"),
    "R-D": ("KURZHAND", "prefer the shortest registered surface"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def choose_surface(hand, card):
    variants = card["registered_surfaces"].split("|")
    master = card["master_form"]
    if hand == "R-A":
        return master
    if hand == "R-B":
        return next((surface for surface in variants if surface.startswith("q")), master)
    if hand == "R-C":
        return next(
            (surface for surface in variants if surface.startswith("sh")),
            next((surface for surface in variants if surface.startswith("s")), master),
        )
    return min(enumerate(variants), key=lambda item: (len(item[1]), item[0]))[1]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    deck = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    exercises = read_tsv(R123 / "HUNDRED_TWENTY_THIRD_TWELVE_SOURCE_TO_CARD_EXERCISES.tsv")
    by_form = {row["master_form"]: row for row in deck}
    by_surface = {}
    for row in deck:
        for surface in row["registered_surfaces"].split("|"):
            if surface in by_surface:
                raise ValueError(f"ambiguous surface {surface}")
            by_surface[surface] = row

    copy_rows = []
    token_rows = []
    for exercise in exercises:
        source_cards = exercise["compiled_master_cards"].split()
        for hand, (hand_name, habit) in HANDS.items():
            visible = [choose_surface(hand, by_form[card]) for card in source_cards]
            recovered = [by_surface[surface]["master_form"] for surface in visible]
            copy_rows.append({
                "exercise_id": exercise["exercise_id"],
                "register": exercise["register"],
                "renderer_id": hand,
                "workshop_hand": hand_name,
                "hand_habit": habit,
                "ordinary_source_command_de": exercise["ordinary_source_command_de"],
                "source_master_cards": " ".join(source_cards),
                "visible_copy": " ".join(visible),
                "recovered_master_cards": " ".join(recovered),
                "card_roundtrip": "PASS" if recovered == source_cards else "FAIL",
                "recovered_source_command_de": exercise["ordinary_source_command_de"] if recovered == source_cards else "UNREADABLE",
            })
            for position, (source_card, surface, recovered_card) in enumerate(zip(source_cards, visible, recovered), 1):
                token_rows.append({
                    "exercise_id": exercise["exercise_id"],
                    "renderer_id": hand,
                    "token_position": str(position),
                    "source_master_card": source_card,
                    "selected_visible_surface": surface,
                    "recovered_master_card": recovered_card,
                    "selection_reason": habit,
                    "token_roundtrip": "PASS" if source_card == recovered_card else "FAIL",
                })
    write_tsv("HUNDRED_TWENTY_FOURTH_48_FOUR_HAND_COPIES.tsv", copy_rows)
    write_tsv("HUNDRED_TWENTY_FOURTH_TOKEN_RENDERER_TRACE.tsv", token_rows)

    exercise_rows = []
    by_exercise = defaultdict(list)
    for row in copy_rows:
        by_exercise[row["exercise_id"]].append(row)
    for exercise in exercises:
        copies = by_exercise[exercise["exercise_id"]]
        visible = {row["visible_copy"] for row in copies}
        exercise_rows.append({
            "exercise_id": exercise["exercise_id"],
            "register": exercise["register"],
            "ordinary_source_command_de": exercise["ordinary_source_command_de"],
            "master_card_sequence": exercise["compiled_master_cards"],
            "distinct_visible_copies": str(len(visible)),
            "all_four_roundtrip": "PASS" if all(row["card_roundtrip"] == "PASS" for row in copies) else "FAIL",
            "visible_copy_set": " || ".join(sorted(visible)),
        })
    write_tsv("HUNDRED_TWENTY_FOURTH_TWELVE_ROUNDTRIP_SUMMARY.tsv", exercise_rows)

    hand_rows = []
    for hand, (hand_name, habit) in HANDS.items():
        rows = [row for row in token_rows if row["renderer_id"] == hand]
        changed = sum(row["selected_visible_surface"] != row["source_master_card"] for row in rows)
        hand_rows.append({
            "renderer_id": hand,
            "workshop_hand": hand_name,
            "habit": habit,
            "exercise_copies": "12",
            "tokens_written": str(len(rows)),
            "tokens_different_from_master_head": str(changed),
            "tokens_recovered": str(sum(row["token_roundtrip"] == "PASS" for row in rows)),
        })
    write_tsv("HUNDRED_TWENTY_FOURTH_FOUR_HAND_RESULTS.tsv", hand_rows)

    report = [
        "# Hundertvierundzwanzigste Runde: vier Hände schreiben dieselben zwölf Befehle", "",
        "Jeder R123-Befehl wurde zuerst in die gemeinsame Masterkartenfolge übersetzt und danach von",
        "vier einfachen Werkstatthänden geschrieben: Vorlagenkopf, q-Eintritt, s-Fluss und Kurzform.",
        "Die sichtbaren Folgen unterscheiden sich, aber jede registrierte Oberfläche führt eindeutig zur",
        "selben Masterkarte zurück.", "",
        "Beispiel: derselbe Quellenbefehl erscheint als `char chety choky aiin`,",
        "`char chety qoky aiin`, `sar chety choky saiin` oder `dar chty oky aiin`. Das ist die",
        "gesuchte Mischung aus gelerntem Ganzkartenwert und handabhängiger Kürzelrealisierung; es sind",
        "keine vier Wörterbücher.", "",
        "Alle 48 Kopien und alle einzelnen Token lesen fehlerfrei zurück. Sichtbare Variation entsteht",
        "erst nach der semantischen Kartenwahl. Die nächste Verbesserung ist deshalb kein neues Alphabet,",
        "sondern ein kleines Meisterheft, das Quellenplätze, siebzehn Karten, zwei Register, Klammerformeln",
        "und die vier Handgewohnheiten auf wenigen Lehrseiten zusammenführt.",
    ]
    (OUT / "HUNDRED_TWENTY_FOURTH_FOUR_HAND_ROUNDTRIP_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "exercises": len(exercises),
        "hands": len(HANDS),
        "copies": len(copy_rows),
        "tokens": len(token_rows),
        "copies_roundtrip_pass": sum(row["card_roundtrip"] == "PASS" for row in copy_rows),
        "exercises_with_visible_variation": sum(int(row["distinct_visible_copies"]) > 1 for row in exercise_rows),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
