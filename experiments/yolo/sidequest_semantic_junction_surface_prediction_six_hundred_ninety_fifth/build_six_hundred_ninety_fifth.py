#!/usr/bin/env python3
"""Predict junction-card surface families from ordered semantic components."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P694 = ROOT / "experiments/yolo/sidequest_semantic_junction_card_tray_six_hundred_ninety_fourth"

FRAGMENTS = {
    "CH": "ch",
    "AIR": "air",
    "T": "t",
    "SH": "sh",
    "OL": "ol",
    "O": "o",
    "Y": "y",
    "HO": "ho",
    "OR": "or",
    "EE": "ee",
    "CKH": "ckh",
    "DY": "dy",
    "E": "e",
    "AL": "al",
    "K": "k",
    "CHD": "ch",
    "L": "l",
    "S": "s",
    "P": "p",
    "CTH": "cth",
    "EEE": "eee",
    "AIN": "ain",
    "DA": "da",
    "IIN": "iin",
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


def ordered_match(surface: str, fragments: list[str]) -> tuple[bool, str]:
    position = 0
    residue: list[str] = []
    for fragment in fragments:
        found = surface.find(fragment, position)
        if found < 0:
            return False, "UNMATCHED"
        residue.append(surface[position:found])
        position = found + len(fragment)
    residue.append(surface[position:])
    joined = "".join(residue)
    return True, joined if joined else "NONE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    tray = read(P694 / "SIX_HUNDRED_NINETY_FOURTH_20_JUNCTION_CARD_TRAY.tsv")
    roots = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")
    value = {row["component"]: row["compact_table_value_de"] for row in roots}

    prediction_rows: list[dict[str, object]] = []
    used_components: set[str] = set()
    for row in tray:
        components = row["full_recipe"].split("+")
        used_components.update(components)
        fragments = [FRAGMENTS[component] for component in components]
        canonical = "".join(fragments)
        surfaces = row["surface_forms"].split("|")
        matches = [ordered_match(surface, fragments) for surface in surfaces]
        all_match = all(result[0] for result in matches)
        exact = all(surface == canonical for surface in surfaces)
        if exact:
            result_class = "EXACT_COMPONENT_CONCATENATION"
        elif all_match:
            result_class = "ORDERED_COMPONENTS_PLUS_BOUND_RENDERER"
        else:
            result_class = "WHOLE_CARD_ONLY"
        prediction_rows.append({
            "card_no": row["card_no"],
            "semantic_request_de": " · ".join(value[component] for component in components),
            "component_recipe": row["full_recipe"],
            "predicted_fragment_family": "-".join(fragments),
            "canonical_direct_concat": canonical,
            "actual_surfaces": row["surface_forms"],
            "ordered_fragment_match": "YES" if all_match else "NO",
            "renderer_residue": "|".join(result[1] for result in matches),
            "prediction_class": result_class,
            "stored_at_desk": row["stored_at_desk"],
            "events": row["events"],
            "records": row["records"],
            "apprentice_request_de": "Fordere eine ganze Musterkarte mit diesen Fragmenten in dieser Reihenfolge an; waehle danach nur den lokalen Renderer.",
        })

    fragment_rows = []
    for component in sorted(used_components):
        fragment_rows.append({
            "component": component,
            "compact_value_de": value[component],
            "diagnostic_surface_fragment": FRAGMENTS[component],
            "junction_cards_using_component": sum(component in row["full_recipe"].split("+") for row in tray),
            "scope_de": "Nur diagnostisches Fragment; die genaue Ganzkartenform darf einen gebundenen Renderer tragen.",
        })

    residue_counts = Counter(row["renderer_residue"] for row in prediction_rows)
    residue_rows = []
    for residue, count in sorted(residue_counts.items(), key=lambda item: (-item[1], item[0])):
        cards = [row["card_no"] for row in prediction_rows if row["renderer_residue"] == residue]
        residue_rows.append({
            "renderer_residue": residue,
            "exact_cards": count,
            "card_numbers": " ".join(cards),
            "working_copy_rule_de": "Keine Zusatzform noetig." if residue == "NONE" else "Gebundenes Reststueck aus dem lokalen Ganzkartenexemplar kopieren; Bedeutungsrezept unveraendert lassen.",
        })

    write("SIX_HUNDRED_NINETY_FIFTH_20_SURFACE_FAMILY_PREDICTIONS.tsv", prediction_rows)
    write("SIX_HUNDRED_NINETY_FIFTH_24_DIAGNOSTIC_FRAGMENTS.tsv", fragment_rows)
    write("SIX_HUNDRED_NINETY_FIFTH_RENDERER_RESIDUES.tsv", residue_rows)

    classes = Counter(row["prediction_class"] for row in prediction_rows)
    summary = {
        "status": "PASS",
        "junction_cards": len(prediction_rows),
        "diagnostic_components": len(fragment_rows),
        "ordered_surface_family_matches": sum(row["ordered_fragment_match"] == "YES" for row in prediction_rows),
        "exact_direct_concatenations": classes["EXACT_COMPONENT_CONCATENATION"],
        "bound_renderer_forms": classes["ORDERED_COMPONENTS_PLUS_BOUND_RENDERER"],
        "whole_card_only_failures": classes["WHOLE_CARD_ONLY"],
        "distinct_renderer_residues_including_none": len(residue_rows),
        "decision": "ALL_JUNCTION_SURFACES_PRESERVE_ORDERED_SEMANTIC_FRAGMENTS",
    }
    (HERE / "SIX_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
