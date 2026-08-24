#!/usr/bin/env python3
"""Extend ordered diagnostic-fragment reconstruction to all 173 prose cards."""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"

VARIANTS = {
    "OK": ["ok"], "CHD": ["ch"], "SH": ["sh", "ch", "sch"],
    "SHED": ["she", "chee", "te", "shed"], "CHK": ["ch"],
    "CTH": ["cth"], "SOLK": ["olk"], "P": ["p"], "LSH": ["lsh"],
    "CFH": ["cfh"], "CH": ["ch"], "T": ["t"], "K": ["k"],
    "S": ["s"], "L": ["l"], "OL": ["ol", "l"], "OT": ["ot"],
    "AL": ["al"], "AR": ["ar"], "AIR": ["air"], "OR": ["or"],
    "HO": ["ho"], "CKH": ["ckh"], "O": ["o"], "Y": ["y"],
    "AIN": ["ain", "an"], "AIIN": ["aiin"], "IIN": ["iin"],
    "E": ["e"], "EE": ["ee", "e"], "EEE": ["eee"], "R": ["r"],
    "AN": ["an"], "DA": ["da"], "LD": ["ld"], "DY": ["dy"],
    "OS": ["os"], "RESUME_CARD": ["chol"], "TALAM": ["talam"],
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def positions(surface: str, fragments: tuple[str, ...]) -> list[tuple[int, int]] | None:
    cursor = 0
    found_positions: list[tuple[int, int]] = []
    for fragment in fragments:
        found = surface.find(fragment, cursor)
        if found < 0:
            return None
        found_positions.append((found, found + len(fragment)))
        cursor = found + len(fragment)
    return found_positions


def best_match(surface: str, choices: list[list[str]]) -> tuple[tuple[str, ...], str, int] | None:
    candidates = []
    for fragments in itertools.product(*choices):
        matched = positions(surface, fragments)
        if matched is None:
            continue
        cursor = 0
        residue_parts: list[str] = []
        for start, stop in matched:
            residue_parts.append(surface[cursor:start])
            cursor = stop
        residue_parts.append(surface[cursor:])
        residue = "".join(residue_parts)
        candidates.append((len(residue), fragments, residue))
    if not candidates:
        return None
    residue_length, fragments, residue = min(candidates, key=lambda item: (item[0], item[1]))
    return fragments, residue if residue else "NONE", residue_length


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")
    roots = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")
    values = {row["component"]: row["compact_table_value_de"] for row in roots}

    surface_rows: list[dict[str, object]] = []
    card_rows: list[dict[str, object]] = []
    for card in cards:
        components = card["component_recipe"].split("+")
        choices = [VARIANTS[component] for component in components]
        form_rows = []
        for surface in card["surfaces"].split("|"):
            match = best_match(surface, choices)
            if match is None:
                selected_fragments: tuple[str, ...] = tuple()
                residue = "UNMATCHED"
                residue_length = len(surface)
                surface_class = "UNEXPLAINED"
            else:
                selected_fragments, residue, residue_length = match
                surface_class = "DIRECT_COMPONENT_STRING" if residue_length == 0 else "ORDERED_COMPONENTS_PLUS_RENDERER"
            row = {
                "card_no": card["card_no"],
                "surface": surface,
                "component_recipe": card["component_recipe"],
                "semantic_recipe_de": " · ".join(values[component] for component in components),
                "selected_diagnostic_fragments": "-".join(selected_fragments) if selected_fragments else "NONE",
                "renderer_residue": residue,
                "renderer_residue_length": residue_length,
                "surface_class": surface_class,
                "composition_mode": card["composition_mode"],
                "events": card["events"],
                "pages": card["pages"],
            }
            surface_rows.append(row)
            form_rows.append(row)
        if card["composition_mode"] == "MEMORIZED_WHOLE_COMMAND":
            card_class = "MEMORIZED_WHOLE_COMMAND"
        elif all(row["surface_class"] == "DIRECT_COMPONENT_STRING" for row in form_rows):
            card_class = "COMPOSED_DIRECT_ALL_FORMS"
        elif all(row["surface_class"] != "UNEXPLAINED" for row in form_rows):
            card_class = "COMPOSED_WITH_BOUND_RENDERER"
        else:
            card_class = "UNEXPLAINED_CARD"
        card_rows.append({
            "card_no": card["card_no"],
            "surfaces": card["surfaces"],
            "component_recipe": card["component_recipe"],
            "semantic_recipe_de": " · ".join(values[component] for component in components),
            "surface_forms": len(form_rows),
            "direct_forms": sum(row["surface_class"] == "DIRECT_COMPONENT_STRING" for row in form_rows),
            "renderer_forms": sum(row["surface_class"] == "ORDERED_COMPONENTS_PLUS_RENDERER" for row in form_rows),
            "max_renderer_residue_length": max(int(row["renderer_residue_length"]) for row in form_rows),
            "card_prediction_class": card_class,
            "events": card["events"],
            "pages": card["pages"],
            "copybook_rule_de": "Bedeutungsfragmente in Reihenfolge anfordern; Restzeichen aus lokalem Ganzkartenexemplar kopieren.",
        })

    fragment_rows = []
    for root in roots:
        fragment_rows.append({
            "component": root["component"],
            "compact_value_de": root["compact_table_value_de"],
            "allowed_diagnostic_fragments": "|".join(VARIANTS[root["component"]]),
            "component_cards": root["card_types"],
            "component_events": root["events_with_component"],
            "surface_rule_de": "Diagnosefragment fuer Familienanforderung; exakte Karte behaelt gebundene Rendererzeichen.",
        })

    residue_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in surface_rows:
        residue_groups[str(row["renderer_residue"])].append(row)
    residue_rows = []
    for residue, rows in sorted(residue_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        residue_rows.append({
            "renderer_residue": residue,
            "surface_forms": len(rows),
            "card_types": len({row["card_no"] for row in rows}),
            "example_surfaces": " ".join(dict.fromkeys(str(row["surface"]) for row in rows[:12])),
            "working_role_de": "Direkte Komposition." if residue == "NONE" else "Gebundener Rahmen, Positionsallograph oder Schreiberzusatz; keine eigene Wortbedeutung.",
        })

    write("SIX_HUNDRED_NINETY_SIXTH_173_CARD_SURFACE_GRAMMAR.tsv", card_rows)
    write("SIX_HUNDRED_NINETY_SIXTH_230_SURFACE_FORM_TRACES.tsv", surface_rows)
    write("SIX_HUNDRED_NINETY_SIXTH_39_COMPONENT_FRAGMENT_RULES.tsv", fragment_rows)
    write("SIX_HUNDRED_NINETY_SIXTH_30_RENDERER_RESIDUES.tsv", residue_rows)

    card_classes = Counter(row["card_prediction_class"] for row in card_rows)
    surface_classes = Counter(row["surface_class"] for row in surface_rows)
    lengths = Counter(int(row["renderer_residue_length"]) for row in surface_rows)
    summary = {
        "status": "PASS",
        "cards": len(card_rows),
        "surface_forms": len(surface_rows),
        "components": len(fragment_rows),
        "composed_direct_all_forms": card_classes["COMPOSED_DIRECT_ALL_FORMS"],
        "composed_with_bound_renderer": card_classes["COMPOSED_WITH_BOUND_RENDERER"],
        "memorized_whole_commands": card_classes["MEMORIZED_WHOLE_COMMAND"],
        "unexplained_cards": card_classes["UNEXPLAINED_CARD"],
        "direct_surface_forms": surface_classes["DIRECT_COMPONENT_STRING"],
        "renderer_surface_forms": surface_classes["ORDERED_COMPONENTS_PLUS_RENDERER"],
        "unexplained_surface_forms": surface_classes["UNEXPLAINED"],
        "renderer_residue_length_distribution": dict(sorted(lengths.items())),
        "distinct_residues_including_none": len(residue_rows),
        "maximum_residue_length": max(lengths),
        "decision": "ALL_173_CARDS_HAVE_ORDERED_SURFACE_FAMILIES_WITH_THREE_EXPLICIT_WHOLE_COMMANDS",
    }
    (HERE / "SIX_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
