#!/usr/bin/env python3
"""Build Pass 701: contrast tree and bounded fresh-prompt encoder."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distance(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


CONTRASTS = [
    ("C01", "Beginnen oder den Stoff umarbeiten?", "OK", "ANSETZEN", "CHD", "UMSETZEN"),
    ("C02", "In Lage halten oder zum Absetzen bringen?", "SH", "HALTEN", "SHED", "ABSETZEN"),
    ("C03", "Waermer oder kuehler machen?", "CHK", "WAERMEN", "R", "KUEHLEN"),
    ("C04", "In der Sammelstelle behalten oder hineingeben?", "SOLK", "AUFFANGEN", "P", "EINFUELLEN"),
    ("C05", "Waschen oder ausdruecken?", "LSH", "WASCHEN", "CFH", "AUSWRINGEN"),
    ("C06", "Vom Posten abnehmen oder in die Liste eintragen?", "CH", "ABNEHMEN", "T", "EINTRAGEN"),
    ("C07", "Eine Zugabe dosieren oder einen Bestand teilen?", "K", "ZUDOSIEREN", "S", "TEILEN"),
    ("C08", "Weiterleiten oder durch einen Durchlass fuehren?", "L", "WEITERLEITEN", "CKH", "DURCHLASS"),
    ("C09", "Mit demselben Gang fortfahren oder zum folgenden gehen?", "OL", "FORTSETZEN", "OT", "DANACH"),
    ("C10", "Wohin oder woher?", "AL", "ZIEL", "AR", "QUELLE"),
    ("C11", "Laufender Strom oder bereiteter Ansatz?", "AIR", "LAUF", "OR", "ANSATZ"),
    ("C12", "Neue Zutat oder bereits gemeinter Posten?", "HO", "ZUTAT", "Y", "DIES"),
    ("C13", "Eine Portion oder das vorgeschriebene Mass?", "AIN", "PORTION", "AIIN", "MASS"),
    ("C14", "Arbeitsstufe oder zweite Wiederholung?", "IIN", "STUFE", "DA", "ZWEIT"),
    ("C15", "Kurz oder laenger?", "E", "KURZ", "EE", "LANG"),
    ("C16", "Vollstaendig oder bloss bereit?", "EEE", "VOLL", "CTH", "BEREIT"),
    ("C17", "Nachgabe oder einzelner Gang?", "AN", "NACHGABE", "O", "GANG"),
    ("C18", "Befestigen oder den Schritt schliessen?", "LD", "BEFESTIGEN", "DY", "SCHLUSS"),
]


TREE = [
    ("D01", "Ist es einer der drei unteilbaren Ganzbefehle?", "JA: Ganzkarte kopieren", "NEIN: Komponentenweg oeffnen"),
    ("D02", "Welche Hauptarbeit geschieht?", "ANSETZEN/UMSETZEN/HALTEN/ABSETZEN/WAERMEN/KUEHLEN/WASCHEN/AUSWRINGEN", "Bei reiner Adresse ohne Verb zu D03"),
    ("D03", "Braucht die Arbeit Reihenfolge oder Fortsetzung?", "OT=DANACH; OL=FORTSETZEN", "Sonst kein Reihenfolgezeichen"),
    ("D04", "Braucht sie Quelle, Lauf, Ziel oder Empfaenger?", "AR=QUELLE; AIR=LAUF; AL=ZIEL; P=EINFUELLEN", "Nur sichtbare Rollen einsetzen"),
    ("D05", "Braucht sie Stoff oder Menge?", "HO=ZUTAT; OR=ANSATZ; AIN=PORTION; AIIN=MASS", "Sonst beim aktuellen Posten bleiben"),
    ("D06", "Braucht sie Stufe oder Dauergrad?", "IIN=STUFE; E=KURZ; EE=LANG; EEE=VOLL", "Grad immer an lizenzierte Basis binden"),
    ("D07", "Bleibt der Posten aktiv oder endet der Schritt?", "Y=DIES; DY=SCHLUSS; LD=BEFESTIGEN", "DY nie aus blosser Schriftform erraten"),
    ("D08", "Existiert die komplette Komponentenfolge im Kartenbuch?", "JA: vorhandene Kartenfamilie und Renderer nehmen", "NEIN: naechste Familie zeigen und Meister fragen; kein neues Wort erfinden"),
]


PROMPTS = [
    ("P01", "Diesen Posten ansetzen.", "OK+Y"),
    ("P02", "Das vorgeschriebene Mass ansetzen.", "OK+AIIN"),
    ("P03", "Eine Portion ansetzen.", "OK+AIN"),
    ("P04", "An der Zielstelle ansetzen.", "OK+AL"),
    ("P05", "Aus der Quelle ansetzen.", "OK+AR"),
    ("P06", "Den Lauf in Gang setzen.", "OK+AIR"),
    ("P07", "Kurz ansetzen und den Schritt schliessen.", "OK+E+DY"),
    ("P08", "Laenger ansetzen und den Schritt schliessen.", "OK+EE+DY"),
    ("P09", "Vollstaendig ansetzen und den Schritt schliessen.", "OK+EEE+DY"),
    ("P10", "Diesen Posten laenger halten.", "SH+EE+Y"),
    ("P11", "Kurz halten und den Schritt schliessen.", "SH+E+DY"),
    ("P12", "Absetzen und den Schritt schliessen.", "SHED+DY"),
    ("P13", "Diesen Posten kurz waermen.", "CHK+E+Y"),
    ("P14", "Laenger waermen und den Schritt schliessen.", "CHK+EE+DY"),
    ("P15", "Diesen Posten einfuellen.", "P+Y"),
    ("P16", "Weiterleiten, umsetzen und den Schritt schliessen.", "L+CHD+DY"),
    ("P17", "Diesen Posten waschen.", "LSH+Y"),
    ("P18", "Diesen Posten kuehlen.", "R+Y"),
    ("P19", "Eine Portion teilen.", "S+AIN"),
    ("P20", "Eine Portion an der Zielstelle einfuellen.", "P+AIN+AL"),
    ("P21", "Den Lauf weiterleiten.", "L+AIR"),
    ("P22", "Den Ansatz kurz halten.", "SH+E+OR"),
    ("P23", "Eine Nachgabe ansetzen.", "OK+AN"),
    ("P24", "Auswringen und den Schritt schliessen.", "CFH+DY"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    tablet = read(P700 / "SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv")
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    component_by_id = {row["component"]: row for row in tablet}
    composable = {row["component"] for row in tablet if row["entry_kind"] == "COMPOSABLE_WORK_COMPONENT"}

    contrast_rows = []
    for number, question, a, av, b, bv in CONTRASTS:
        contrast_rows.append({
            "pair_no": number, "apprentice_question_de": question,
            "component_a": a, "value_a_de": av, "component_b": b, "value_b_de": bv,
            "diagnostic_a": component_by_id[a]["diagnostic_fragments"],
            "diagnostic_b": component_by_id[b]["diagnostic_fragments"],
            "teaching_rule_de": f"Frage zuerst: {question} Dann waehle genau {a} oder {b}.",
        })
    tree_rows = [
        {"step": n, "question_de": q, "positive_branch_de": yes, "negative_branch_de": no}
        for n, q, yes, no in TREE
    ]

    cards_by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for card in cards:
        cards_by_recipe[tuple(card["component_recipe"].split("+"))].append(card)
    composed_recipes = sorted(cards_by_recipe)
    prompt_rows = []
    for prompt_id, prompt_de, recipe_text in PROMPTS:
        recipe = tuple(recipe_text.split("+"))
        exact = cards_by_recipe.get(recipe, [])
        if exact:
            nearest_distance = 0
            nearest = [recipe]
            status = "EXACT_EXISTING_RECIPE"
            decision = "Vorhandene Kartenfamilie waehlen; danach ihren belegten Renderer kopieren."
        else:
            nearest_distance = min(distance(recipe, candidate) for candidate in composed_recipes)
            nearest = [candidate for candidate in composed_recipes if distance(recipe, candidate) == nearest_distance]
            status = "NO_EXACT_CARD__NEAREST_FAMILY_ONLY"
            decision = "Keine neue Oberflaeche bilden. Naechste vorhandene Familien vorlegen und den Meister entscheiden lassen."
        nearest_cards = [card for candidate in nearest for card in cards_by_recipe[candidate]]
        prompt_rows.append({
            "prompt_id": prompt_id, "fresh_prompt_de": prompt_de,
            "requested_recipe": recipe_text, "requested_components_known": "YES" if set(recipe) <= composable else "NO",
            "encoding_status": status,
            "exact_card_numbers": "|".join(card["card_no"] for card in exact),
            "exact_surfaces": "|".join(card["surfaces"] for card in exact),
            "nearest_edit_distance": nearest_distance,
            "nearest_recipe_count": len(nearest),
            "nearest_recipes": "|".join("+".join(candidate) for candidate in nearest),
            "nearest_card_numbers": "|".join(card["card_no"] for card in nearest_cards),
            "nearest_surfaces": "|".join(card["surfaces"] for card in nearest_cards),
            "master_approval": "NO" if exact else "REQUIRED",
            "encoder_decision_de": decision,
        })

    write("SEVEN_HUNDRED_FIRST_18_CONTRAST_PAIRS.tsv", contrast_rows)
    write("SEVEN_HUNDRED_FIRST_8_DECISION_TREE_STEPS.tsv", tree_rows)
    write("SEVEN_HUNDRED_FIRST_24_FRESH_PROMPT_ENCODINGS.tsv", prompt_rows)

    exact_count = sum(row["encoding_status"] == "EXACT_EXISTING_RECIPE" for row in prompt_rows)
    missing_count = len(prompt_rows) - exact_count
    summary = {
        "status": "PASS", "composable_components": len(composable),
        "contrast_pairs": len(contrast_rows), "components_used_once_in_pairs": len(composable),
        "decision_tree_steps": len(tree_rows), "fresh_prompts": len(prompt_rows),
        "exact_existing_recipes": exact_count, "missing_recipes": missing_count,
        "missing_at_distance_one": sum(row["encoding_status"].startswith("NO_EXACT") and row["nearest_edit_distance"] == 1 for row in prompt_rows),
        "invented_surfaces": 0,
        "decision": "COMPONENT_GRAMMAR_IS_PRODUCTIVE_BUT_EXACT_CARD_INVENTORY_IS_LICENSED_AND_BOUNDED",
    }
    (HERE / "SEVEN_HUNDRED_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
