#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P781 = ROOT / "experiments/yolo/sidequest_semantic_period_teaching_kit_seven_hundred_eighty_first"
PAGE_HAND = {"f10r": "HAND_1", "f11r": "HAND_1", "f56r": "HAND_1", "f55v": "HAND_2", "f81v": "HAND_2", "f82r": "HAND_2", "f83r": "HAND_2"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def join(values: set[str] | list[str]) -> str:
    return ",".join(sorted(values))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    old_rules = read(P781 / "SEVEN_HUNDRED_EIGHTY_FIRST_6_MARGIN_RULES.tsv")
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_recipe[row["component_recipe"]].append(row)
        by_card[row["card_no"]].append(row)

    recipe_rows = []
    recipe_id = {}
    for ordinal, recipe in enumerate(sorted(by_recipe), 1):
        rows = by_recipe[recipe]
        readings = {row["rebuilt_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"recipe has multiple readings: {recipe}")
        rid = f"RCP{ordinal:03d}"
        recipe_id[recipe] = rid
        cards = {row["card_no"] for row in rows}
        recipe_rows.append(
            {
                "recipe_id": rid,
                "component_recipe": recipe,
                "workshop_reading_de": next(iter(readings)),
                "exact_card_count": len(cards),
                "exact_card_ids": join(cards),
                "surface_forms": join({row["surface"] for row in rows}),
                "events": len(rows),
                "pages": join({row["page"] for row in rows}),
                "hands": join({PAGE_HAND[row["page"]] for row in rows}),
                "semantic_teaching_mode": "ONE_RECIPE_MULTIPLE_CARD_REALIZATIONS" if len(cards) > 1 else "ONE_RECIPE_ONE_CARD",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SECOND_163_RECIPE_DICTIONARY.tsv",
        recipe_rows,
        ["recipe_id", "component_recipe", "workshop_reading_de", "exact_card_count", "exact_card_ids", "surface_forms", "events", "pages", "hands", "semantic_teaching_mode"],
    )

    pair_rows = []
    for recipe, rows in sorted(by_recipe.items()):
        cards = sorted({row["card_no"] for row in rows})
        if len(cards) == 1:
            continue
        card1, card2 = cards
        rows1 = by_card[card1]
        rows2 = by_card[card2]
        hands1 = {PAGE_HAND[row["page"]] for row in rows1}
        hands2 = {PAGE_HAND[row["page"]] for row in rows2}
        if hands1.isdisjoint(hands2):
            ecology = "CROSS_HAND_EXCLUSIVE_PAIR"
        elif hands1 == hands2 and len(hands1) == 1:
            ecology = "WITHIN_ONE_HAND_PAIR"
        else:
            ecology = "PORTABLE_CARD_PLUS_LOCAL_VARIANT"
        pair_rows.append(
            {
                "recipe_id": recipe_id[recipe],
                "component_recipe": recipe,
                "workshop_reading_de": rows[0]["rebuilt_reading_de"],
                "card_a": card1,
                "card_a_surfaces": join({row["surface"] for row in rows1}),
                "card_a_events": len(rows1),
                "card_a_hands": join(hands1),
                "card_b": card2,
                "card_b_surfaces": join({row["surface"] for row in rows2}),
                "card_b_events": len(rows2),
                "card_b_hands": join(hands2),
                "pair_events": len(rows),
                "ecology": ecology,
                "semantic_relation": "SAME_RECIPE_AND_WORKING_READING",
                "copy_relation": "KEEP_EXACT_CARD_FROM_MODEL",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SECOND_10_TWO_CARD_RECIPE_FAMILIES.tsv",
        pair_rows,
        ["recipe_id", "component_recipe", "workshop_reading_de", "card_a", "card_a_surfaces", "card_a_events", "card_a_hands", "card_b", "card_b_surfaces", "card_b_events", "card_b_hands", "pair_events", "ecology", "semantic_relation", "copy_relation"],
    )

    paired_recipes = {row["component_recipe"] for row in pair_rows}
    trace_rows = []
    for row in events:
        trace_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "hand": PAGE_HAND[row["page"]],
                "exact_copy_identity": row["card_no"],
                "surface": row["surface"],
                "semantic_recipe_identity": recipe_id[row["component_recipe"]],
                "component_recipe": row["component_recipe"],
                "workshop_reading_de": row["rebuilt_reading_de"],
                "recipe_has_two_card_realizations": "YES" if row["component_recipe"] in paired_recipes else "NO",
                "spoken_readback_rule": "READ_RECIPE_IDENTITY",
                "copy_rule": "COPY_EXACT_CARD_IDENTITY",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SECOND_381_TWO_LEVEL_IDENTITY.tsv",
        trace_rows,
        ["event_id", "page", "record", "statement_id", "hand", "exact_copy_identity", "surface", "semantic_recipe_identity", "component_recipe", "workshop_reading_de", "recipe_has_two_card_realizations", "spoken_readback_rule", "copy_rule"],
    )

    paired_event_rows = [row for row in trace_rows if row["recipe_has_two_card_realizations"] == "YES"]
    write(
        "SEVEN_HUNDRED_EIGHTY_SECOND_71_PAIRED_RECIPE_EVENTS.tsv",
        paired_event_rows,
        ["event_id", "page", "record", "statement_id", "hand", "exact_copy_identity", "surface", "semantic_recipe_identity", "component_recipe", "workshop_reading_de", "recipe_has_two_card_realizations", "spoken_readback_rule", "copy_rule"],
    )

    new_rules = [dict(row) for row in old_rules]
    new_rules.append(
        {
            "rule_no": 7,
            "short_mark": "SPRICH/KOPIERE",
            "instruction": "speak by component recipe; copy by exact card model; equal meaning does not license a free surface swap",
        }
    )
    write("SEVEN_HUNDRED_EIGHTY_SECOND_7_MARGIN_RULES.tsv", new_rules, ["rule_no", "short_mark", "instruction"])

    report = """# Pass 782 — Sprich nach Rezept, kopiere nach Karte

Der erwartete Lehrlingsfehler zeigt eine nützliche Zweiteilung. Die173 exakten Karten fallen auf163 verschiedene Komponentenrezepte. Zehn Rezepte besitzen jeweils zwei exakte Karten; diese20 Karten tragen zusammen71 Ereignisse. In allen zehn Paaren ist die kurze Werkstattlektüre bereits identisch.

Darum brauchen wir zwei Identitäten:

- **Kopieridentität:** die exakte Karte und ihre Oberfläche; sie wird aus dem Modell bewahrt.
- **Sprech-/Bedeutungsidentität:** das Komponentenrezept; es bestimmt die gemeinsame kurze Arbeitslesung.

Das ist keine Niederlage der Wortstammidee, sondern ihre sauberste Form. `qokchy/okchy/chokchy` und `oky/choky/qoky` können dasselbe `OK+Y = ANSETZEN · DIES` sprechen, ohne dass ein Lehrling beim Abschreiben die beiden Karten willkürlich vertauschen darf. Ebenso sprechen `okchol` und `qokol` beide `OK+OL = ANSETZEN · WEITER`; hier ist die Teilung sogar handexklusiv und bleibt unser stärkster echter Handallograph-Kandidat.

Die sechs alten Randregeln erhalten deshalb nur einen siebten Merksatz: **SPRICH NACH REZEPT; KOPIERE NACH KARTE.** Das semantische Werkstattwörterbuch schrumpft von173 Karten auf163 Rezeptwerte, die diplomatische Musterbox bleibt173 Karten groß.

Als nächstes zerlegen wir die zehn Paare mechanisch. Besonders die CHD/CHED-, Y/CHY- und Eintrittshüllenwechsel sollten wenige wiederkehrende Allographieregeln ergeben. Wenn das gelingt, schrumpft auch die Kopierbox, nicht nur das gesprochene Wörterbuch.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "exact_cards": len(by_card),
        "semantic_recipes": len(recipe_rows),
        "two_card_recipes": len(pair_rows),
        "paired_cards": sum(int(row["exact_card_count"]) for row in recipe_rows if row["semantic_teaching_mode"] == "ONE_RECIPE_MULTIPLE_CARD_REALIZATIONS"),
        "paired_events": len(paired_event_rows),
        "decision": "TWO_LEVEL_IDENTITY__SPEAK_BY163_RECIPES__COPY_BY173_EXACT_CARDS",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
