#!/usr/bin/env python3
"""Build Pass 702 component compatibility grammar from the 170 composed cards."""

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


GAP_DECISIONS = {
    "LSH+Y": (
        "LIKELY_LICENSED_UNUSED_CELL", "WASCHEN · DIES",
        "LSH ist als Kopf belegt; OPERATION→DIES ist breit belegt. Nur die konkrete Paarung fehlt.",
        "Keine neue Karte; bis zu einem Exemplar zwei Karten oder Meisterumschreibung benutzen.",
    ),
    "R+Y": (
        "BLOCKED_BY_REQUIRED_COMPLEMENT", "KUEHLEN · DIES",
        "Alle fuenf R-Kopffamilien setzen zuerst OL, AL, SH oder SHED; R+AL+Y ist die belegte ausdrueckliche Form.",
        "R+AL+Y verwenden und die Zielstelle nennen.",
    ),
    "S+AIN": (
        "BLOCKED_BY_COMPONENT_REANALYSIS", "GETEILT · PORTION",
        "S kommt nur in CH+E+S und niemals als Kopf vor; freies TEILEN war zu stark.",
        "S vorlaeufig als gebundenes Ergebnis GETEILT lernen; Portion separat nennen.",
    ),
    "P+AIN+AL": (
        "BLOCKED_BY_ORDER_GRAMMAR", "EINFUELLEN · PORTION · ZIEL",
        "Im gesamten Karteninventar folgt auf kein Mengen-/Stufenzeichen eine Relations-/Zieladresse.",
        "P+CHD+AL fuer Einfuellen/Umsetzen/Ziel und AIN als eigene Mengenkarte setzen.",
    ),
    "L+AIR": (
        "LIKELY_LICENSED_UNUSED_CELL", "WEITERLEITEN · LAUF",
        "L ist produktiver Kopf; OPERATION→STATE_OBJECT ist belegt und AIR folgt CH, CHD, K und OK.",
        "Keine neue Karte; naechste L- oder AIR-Familie nur als Umschreibung waehlen.",
    ),
    "SH+E+OR": (
        "LIKELY_LICENSED_UNUSED_CELL", "HALTEN · KURZ · ANSATZ",
        "SH+E ist produktiv; E→OR und OPERATION→GRADE→STATE_OBJECT sind beide belegt.",
        "Keine neue Karte; vorhandene Halte- und Ansatzkarte nacheinander setzen.",
    ),
    "OK+AN": (
        "LIKELY_LICENSED_UNUSED_CELL", "ANSETZEN · NACHGABE",
        "OK verbindet sich mit AIN, AIIN, AL, AR, AIR, OL und Y; K+AN belegt AN als Nachgabe.",
        "Keine neue Karte; OK-Familie plus getrennte Nachgabekarte verwenden.",
    ),
    "CFH+DY": (
        "LIKELY_LICENSED_UNUSED_CELL", "AUSWRINGEN · SCHLUSS",
        "CFH+Y ist belegt; OPERATION→SCHLUSS ist breit belegt und Y/DY bilden oft eine offene/geschlossene Wahl.",
        "Keine neue Karte; CFH+Y ausfuehren und mit einer separaten lizenzierten Schlusskarte beenden.",
    ),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    tablet = read(P700 / "SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv")
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    prompts = read(P701 / "SEVEN_HUNDRED_FIRST_24_FRESH_PROMPT_ENCODINGS.tsv")
    composable_rows = [row for row in tablet if row["entry_kind"] == "COMPOSABLE_WORK_COMPONENT"]
    composed_cards = [row for row in cards if row["card_class"] != "MEMORIZED_WHOLE_COMMAND"]
    layer = {row["component"]: row["historical_layer"] for row in composable_rows}
    value = {row["component"]: row["compact_value_de"] for row in composable_rows}

    recipes_by_card = {row["card_no"]: tuple(row["component_recipe"].split("+")) for row in composed_cards}
    predecessors: dict[str, Counter[str]] = defaultdict(Counter)
    followers: dict[str, Counter[str]] = defaultdict(Counter)
    positions: dict[str, Counter[str]] = defaultdict(Counter)
    cards_with: dict[str, set[str]] = defaultdict(set)
    events_with: Counter[str] = Counter()
    adjacency_cards: dict[tuple[str, str], set[str]] = defaultdict(set)
    adjacency_events: Counter[tuple[str, str]] = Counter()
    adjacency_recipes: dict[tuple[str, str], set[str]] = defaultdict(set)
    layer_pairs: Counter[tuple[str, str]] = Counter()

    for card in composed_cards:
        recipe = recipes_by_card[card["card_no"]]
        event_count = int(card["events"])
        for index, component in enumerate(recipe):
            cards_with[component].add(card["card_no"])
            events_with[component] += event_count
            positions[component]["FIRST" if index == 0 else "LAST" if index == len(recipe) - 1 else "MIDDLE"] += 1
        for left, right in zip(recipe, recipe[1:]):
            predecessors[right][left] += 1
            followers[left][right] += 1
            adjacency_cards[(left, right)].add(card["card_no"])
            adjacency_events[(left, right)] += event_count
            adjacency_recipes[(left, right)].add(card["component_recipe"])
            layer_pairs[(layer[left], layer[right])] += 1

    profile_rows = []
    for row in composable_rows:
        component = row["component"]
        current_value = "GETEILT" if component == "S" else value[component]
        revision = "TEILEN→GETEILT; nur gebundener Ergebnisrest" if component == "S" else "UNCHANGED"
        profile_rows.append({
            "component": component, "working_value_de": current_value,
            "working_layer": "BOUND_RESULT_SIGN" if component == "S" else row["historical_layer"],
            "card_types": len(cards_with[component]), "events": events_with[component],
            "first_positions": positions[component]["FIRST"], "middle_positions": positions[component]["MIDDLE"],
            "last_positions": positions[component]["LAST"],
            "predecessors": "|".join(f"{key}:{count}" for key, count in sorted(predecessors[component].items())),
            "followers": "|".join(f"{key}:{count}" for key, count in sorted(followers[component].items())),
            "revision_from_pass700": revision,
        })

    adjacency_rows = []
    for left, right in sorted(adjacency_cards):
        adjacency_rows.append({
            "left_component": left, "left_value_de": "GETEILT" if left == "S" else value[left],
            "right_component": right, "right_value_de": "GETEILT" if right == "S" else value[right],
            "left_layer": "BOUND_RESULT_SIGN" if left == "S" else layer[left],
            "right_layer": "BOUND_RESULT_SIGN" if right == "S" else layer[right],
            "card_type_support": len(adjacency_cards[(left, right)]),
            "event_support": adjacency_events[(left, right)],
            "recipe_support": len(adjacency_recipes[(left, right)]),
            "recipes": "|".join(sorted(adjacency_recipes[(left, right)])),
            "card_numbers": "|".join(sorted(adjacency_cards[(left, right)])),
        })

    gap_rows = []
    for prompt in prompts:
        if prompt["encoding_status"] == "EXACT_EXISTING_RECIPE":
            continue
        recipe = prompt["requested_recipe"]
        decision, reading, evidence, repair = GAP_DECISIONS[recipe]
        parts = recipe.split("+")
        exact_pair_flags = ["YES" if (a, b) in adjacency_cards else "NO" for a, b in zip(parts, parts[1:])]
        layer_pair_flags = ["YES" if (layer[a], layer[b]) in layer_pairs else "NO" for a, b in zip(parts, parts[1:])]
        gap_rows.append({
            "prompt_id": prompt["prompt_id"], "prompt_de": prompt["fresh_prompt_de"],
            "requested_recipe": recipe, "working_reading_de": reading,
            "classification": decision,
            "exact_component_pairs_seen": "|".join(exact_pair_flags),
            "abstract_layer_pairs_seen": "|".join(layer_pair_flags),
            "nearest_edit_distance": prompt["nearest_edit_distance"],
            "evidence_de": evidence, "workshop_repair_de": repair,
            "new_surface_allowed": "NO",
        })

    rule_rows = [
        {"rule_id": "G01", "rule_de": "Nur eine vollstaendig belegte Komponentenfolge adressiert eine einzelne Karte.", "scope": "160 Rezepte / 170 komponierte Karten", "effect": "Lizenz vor Oberflaeche"},
        {"rule_id": "G02", "rule_de": "Die Reihenfolge der Komponenten bleibt erhalten; ein Renderer darf sie nicht vertauschen.", "scope": "alle 170 Karten", "effect": "gerichtete Syntax"},
        {"rule_id": "G03", "rule_de": "Die drei Ganzbefehle werden nie aus Komponenten neu gebaut.", "scope": "3 Karten", "effect": "Nomenklatorgrenze"},
        {"rule_id": "G04", "rule_de": "Eine lizenzierte DY-Schlusskomponente steht am Ende ihrer Kartenfolge.", "scope": "37/37 DY-Kartentypen", "effect": "harte Endposition"},
        {"rule_id": "G05", "rule_de": "E/EE/EEE sind gebundene Grade und verlangen eine Prozessbasis oder eine gelernte Ganzfamilie.", "scope": "Gradfamilien", "effect": "kein freies Zeitwort"},
        {"rule_id": "G06", "rule_de": "Nach einem Mengen-/Stufenzeichen folgt derzeit keine Ziel-/Relationsadresse.", "scope": "0 beobachtete MEASURE→RELATION-Paare", "effect": "Menge schliesst den Adressblock"},
        {"rule_id": "G07", "rule_de": "R verlangt in allen Kopfkarten zuerst Ziel, Fortsetzung, Halten oder Absetzen.", "scope": "5/5 R-Kopfkarten", "effect": "R+Y allein gesperrt"},
        {"rule_id": "G08", "rule_de": "S ist vorlaeufig GETEILT, kein frei produktives TEILEN.", "scope": "1/1 Karte; nie Kopf", "effect": "S+AIN gesperrt"},
        {"rule_id": "G09", "rule_de": "Ein abstrakt erlaubtes, aber unbelegtes Rezept darf paraphrasiert, nicht neu geschrieben werden.", "scope": "5 wahrscheinliche Leerzellen", "effect": "Mehrkarten-Umschreibung"},
        {"rule_id": "G10", "rule_de": "Der sichtbare Besitzer liefert das konkrete Substantiv; die Komponenten liefern nur die Arbeitsrelation.", "scope": "alle 11 Records", "effect": "kein neuer Stoffstamm"},
    ]

    write("SEVEN_HUNDRED_SECOND_36_COMPONENT_PROFILES.tsv", profile_rows)
    write("SEVEN_HUNDRED_SECOND_161_LICENSED_ADJACENCIES.tsv", adjacency_rows)
    write("SEVEN_HUNDRED_SECOND_8_GAP_CLASSIFICATIONS.tsv", gap_rows)
    write("SEVEN_HUNDRED_SECOND_10_COMPATIBILITY_RULES.tsv", rule_rows)

    unique_recipes = {row["component_recipe"] for row in composed_cards}
    summary = {
        "status": "PASS", "composed_cards": len(composed_cards), "unique_recipes": len(unique_recipes),
        "components": len(profile_rows), "licensed_directed_adjacencies": len(adjacency_rows),
        "licensed_layer_adjacencies": len(layer_pairs), "compatibility_rules": len(rule_rows),
        "fresh_gaps": len(gap_rows),
        "likely_licensed_unused": sum(row["classification"] == "LIKELY_LICENSED_UNUSED_CELL" for row in gap_rows),
        "blocked": sum(row["classification"].startswith("BLOCKED") for row in gap_rows),
        "component_revisions": 1, "invented_surfaces": 0,
        "decision": "FIVE_GAPS_LOOK_LIKE_UNUSED_LICENSED_CELLS__THREE_REQUIRE_GRAMMAR_OR_COMPONENT_REPAIR",
    }
    (HERE / "SEVEN_HUNDRED_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
