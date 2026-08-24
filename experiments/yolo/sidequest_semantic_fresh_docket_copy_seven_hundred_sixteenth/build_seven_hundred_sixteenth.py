#!/usr/bin/env python3
"""Build Pass 716: encode fresh practice dockets with the refined doublet rules."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P712 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_recipe_inventory_seven_hundred_twelfth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


DOCKETS = [
    ("FD01", "PLANT", "Locus beginnt: aktuellen Posten ansetzen; vorgeschriebenes Mass nennen.", ["OK+Y", "AIIN"], "YES"),
    ("FD02", "PLANT", "Neue Zutat nennen; diesen Posten ansetzen; aus der Zutatquelle nehmen.", ["HO", "OK+Y", "K+HO+AR"], "NO"),
    ("FD03", "BASIN", "Mass nennen; aktuellen Posten ansetzen; Zielstelle nennen.", ["AIIN", "OK+Y", "AL"], "NO"),
    ("FD04", "BASIN", "Schritt schliessen; Posten wieder aufnehmen; an Zielstelle ansetzen.", ["CHD+DY", "CHD+Y", "OK+AL"], "YES"),
    ("FD05", "PLANT", "Mass nennen; Posten umsetzen; im Gefaess verwahren.", ["AIIN", "CHD+Y", "TALAM"], "NO"),
    ("FD06", "BASIN", "Am neuen Locus den Umsetzungsschritt schliessen.", ["CHD+DY"], "YES"),
    ("FD07", "APPARATUS", "Durchlass am Posten; danach Umsetzung schliessen.", ["CKH+Y", "CHD+DY"], "NO"),
    ("FD08", "PLANT", "Mass nennen; Umsetzung kompakt schliessen; Ansatz nennen.", ["AIIN", "CHD+DY", "OR"], "NO"),
    ("FD09", "BASIN", "Posten kurz eintragen; laufenden Ansatz-Umsetzungsschritt schliessen.", ["T+E+Y", "OK+CHD+DY"], "NO"),
    ("FD10", "BASIN", "Selbstaendige geschlossene Ansatz-Umsetzungskarte.", ["OK+CHD+DY"], "NO"),
    ("FD11", "APPARATUS", "Selbstaendige geschlossene Ansatz-Umsetzungskarte am Locusanfang.", ["OK+CHD+DY"], "YES"),
    ("FD12", "BASIN", "Schritt am Locusanfang schliessen; umsetzen; Mass nennen, aber kein Ziel folgt.", ["CHD+DY", "CHD+Y", "AIIN"], "YES"),
]


DOUBLETS = {
    "OK+Y": {"plain": "PROC008", "marked": "PROC011", "rule": "CR1"},
    "CHD+Y": {"plain": "PROC042", "marked": "PROC133", "rule": "CR2"},
    "CHD+DY": {"plain": "PROC094", "marked": "PROC076", "rule": "CR3"},
    "OK+CHD+DY": {"plain": "PROC082", "marked": "PROC091", "rule": "CR4"},
}


def choose(recipe: str, sequence: list[str], position: int, locus_start: bool, unique: dict[str, str]) -> tuple[str, str, str]:
    if recipe not in DOUBLETS:
        return unique[recipe], "UNIQUE", "UNIQUE_EXACT_CARD"
    previous = sequence[position - 1] if position else "NONE"
    following = sequence[position + 1] if position + 1 < len(sequence) else "NONE"
    if recipe == "OK+Y":
        marked = (position == 0 and locus_start) or previous == "HO"
    elif recipe == "CHD+Y":
        marked = previous == "CHD+DY" and following == "OK+AL"
    elif recipe == "CHD+DY":
        marked = (position == 0 and locus_start) or previous == "CKH+Y"
    elif recipe == "OK+CHD+DY":
        marked = position == len(sequence) - 1 and len(sequence) > 1
    else:
        raise AssertionError(recipe)
    variant = "MARKED" if marked else "PLAIN"
    return DOUBLETS[recipe]["marked" if marked else "plain"], variant, DOUBLETS[recipe]["rule"]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    mapping = read(P712 / "SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    surface_cards: dict[str, set[str]] = defaultdict(set)
    for row in mapping:
        by_recipe[row["component_recipe"]].append(row)
        for surface in row["surfaces"].split("|"):
            surface_cards[surface].add(row["exact_card_id"])
    unique = {recipe: rows[0]["exact_card_id"] for recipe, rows in by_recipe.items() if len(rows) == 1}
    by_card = {row["exact_card_id"]: row for row in mapping}

    docket_rows = []
    trace_rows = []
    for docket_id, owner, instruction, sequence, starts in DOCKETS:
        selected = []
        surfaces = []
        readings = []
        used_rules = []
        locus_start = starts == "YES"
        for position, recipe in enumerate(sequence):
            card, variant, rule = choose(recipe, sequence, position, locus_start, unique)
            card_row = by_card[card]
            candidates = [surface for surface in card_row["surfaces"].split("|") if surface_cards[surface] == {card}]
            if not candidates:
                raise AssertionError(f"No unambiguous surface for {card}")
            surface = sorted(candidates, key=lambda value: (len(value), value))[0]
            selected.append(card)
            surfaces.append(surface)
            readings.append(card_row["working_reading_de"])
            if rule != "UNIQUE_EXACT_CARD":
                used_rules.append(rule)
            trace_rows.append({
                "practice_event_id": f"{docket_id}-E{position + 1:02d}", "docket_id": docket_id,
                "owner_class": owner, "position": position + 1, "locus_start": starts,
                "previous_recipe": sequence[position - 1] if position else "NONE",
                "component_recipe": recipe,
                "next_recipe": sequence[position + 1] if position + 1 < len(sequence) else "NONE",
                "selection_rule": rule, "selected_variant": variant, "selected_card": card,
                "selected_surface": surface, "surface_unique_to_card": "YES",
                "backread_de": card_row["working_reading_de"], "local_surface_tray_lookup": "NONE",
            })
        docket_rows.append({
            "docket_id": docket_id, "owner_class": owner, "docket_de": instruction,
            "locus_start": starts, "component_sequence": " > ".join(sequence),
            "card_sequence": " > ".join(selected), "surface_sequence": " ".join(surfaces),
            "backreading_de": "; ".join(readings),
            "doublet_rules_used": "|".join(sorted(set(used_rules))) if used_rules else "NONE",
            "surface_tray_lookups": 0,
        })

    write("SEVEN_HUNDRED_SIXTEENTH_12_FRESH_DOCKETS.tsv", docket_rows)
    write("SEVEN_HUNDRED_SIXTEENTH_27_FORWARD_BACKREAD_TRACE.tsv", trace_rows)
    summary = {
        "status": "PASS", "fresh_dockets": len(docket_rows), "practice_events": len(trace_rows),
        "owners": sorted({row["owner_class"] for row in docket_rows}),
        "doublet_rules_exercised": sorted({row["selection_rule"] for row in trace_rows if row["selection_rule"].startswith("CR")}),
        "marked_doublet_events": sum(row["selected_variant"] == "MARKED" for row in trace_rows),
        "plain_doublet_events": sum(row["selected_variant"] == "PLAIN" for row in trace_rows),
        "unique_surface_backreads": sum(row["surface_unique_to_card"] == "YES" for row in trace_rows),
        "local_surface_tray_lookups": sum(int(row["surface_tray_lookups"]) for row in docket_rows),
        "new_cards": 0, "new_surfaces": 0,
        "decision": "TWELVE_FRESH_DOCKETS_ENCODE_AND_BACKREAD_WITH_FOUR_DOUBLET_RULES_AND_NO_EVENT_LOOKUP",
    }
    (HERE / "SEVEN_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
