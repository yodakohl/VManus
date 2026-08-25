#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_allograph_renderer_nine_hundred_first"
PREFIX = "NINE_HUNDRED_SECOND"

ANALYSIS_SOURCE = SOURCE / "NINE_HUNDRED_FIRST_231_IDENTITY_RENDERER_ANALYSES.tsv"
MARK_SOURCE = SOURCE / "NINE_HUNDRED_FIRST_437_MARK_RENDERER.tsv"
UNIT_SOURCE = SOURCE / "NINE_HUNDRED_FIRST_118_UNIT_RENDERER.tsv"
CARD_SOURCE = SOURCE / "NINE_HUNDRED_FIRST_6_JOB_CARD_RENDERER.tsv"

FEATURE_SETS = [
    ("MASTER_SECTION", ("master_section",)),
    ("UNIT_POSITION", ("unit_position",)),
    ("SECTION_PLUS_POSITION", ("master_section", "unit_position")),
    ("ORDER", ("order_id",)),
    ("ORDER_PLUS_POSITION", ("order_id", "unit_position")),
    ("PAGE", ("page",)),
    ("PAGE_PLUS_POSITION", ("page", "unit_position")),
    ("STAGE", ("stage",)),
    ("STAGE_PLUS_POSITION", ("stage", "unit_position")),
    ("UNIT", ("unit",)),
    ("UNIT_PLUS_POSITION", ("unit", "unit_position")),
    ("MEMORIZED_IDENTITY", ("identity",)),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def key_for(row: dict[str, object], fields: tuple[str, ...]) -> str:
    return "|".join(str(row[field]) for field in fields)


def main() -> None:
    analyses = read(ANALYSIS_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)
    multi_recipes = {
        row["component_recipe"]
        for row in analyses
        if int(row["allograph_choices"]) > 1
    }
    assert len(multi_recipes) == 16

    grouped_units: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        grouped_units[(row["order_id"], row["stage"], row["unit"])].append(row)
    enriched: list[dict[str, object]] = []
    for key, local in grouped_units.items():
        for index, row in enumerate(local):
            if len(local) == 1:
                position = "ONLY"
            elif index == 0:
                position = "FIRST"
            elif index == len(local) - 1:
                position = "LAST"
            else:
                position = "MIDDLE"
            enriched.append({
                **row,
                "unit_position": position,
                "position_index": index + 1,
                "unit_length": len(local),
                "left_surface": local[index - 1]["surface"] if index else "UNIT_START",
                "right_surface": local[index + 1]["surface"] if index + 1 < len(local) else "UNIT_END",
            })
    enriched_by_id = {str(row["order_mark_id"]): row for row in enriched}
    enriched = [enriched_by_id[row["order_mark_id"]] for row in marks]

    occurrences_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in enriched:
        if row["component_recipe"] in multi_recipes:
            occurrences_by_recipe[str(row["component_recipe"])].append(row)

    family_rows = []
    selector_rows = []
    selection_by_occurrence: dict[str, tuple[str, str, str]] = {}
    selector_level_counts: Counter[str] = Counter()
    for recipe in sorted(multi_recipes):
        local = occurrences_by_recipe[recipe]
        chosen_name = ""
        chosen_fields: tuple[str, ...] = ()
        chosen_mapping: dict[str, str] = {}
        for feature_name, fields in FEATURE_SETS:
            buckets: dict[str, set[str]] = defaultdict(set)
            for row in local:
                buckets[key_for(row, fields)].add(str(row["surface"]))
            if all(len(values) == 1 for values in buckets.values()):
                chosen_name = feature_name
                chosen_fields = fields
                chosen_mapping = {key: next(iter(values)) for key, values in buckets.items()}
                break
        assert chosen_name
        selector_level_counts[chosen_name] += 1
        for selector_key, surface in sorted(chosen_mapping.items()):
            selector_rows.append({
                "component_recipe": recipe,
                "selector_feature_set": chosen_name,
                "selector_key": selector_key,
                "selected_surface": surface,
                "apprentice_rule": f"For {recipe}, when {chosen_name}={selector_key}, write {surface}.",
            })
        for row in local:
            selector_key = key_for(row, chosen_fields)
            predicted = chosen_mapping[selector_key]
            selection_by_occurrence[str(row["order_mark_id"])] = (chosen_name, selector_key, predicted)
        surfaces = sorted({str(row["surface"]) for row in local})
        identities = sorted({str(row["identity"]) for row in local})
        q_surfaces = [surface for surface in surfaces if surface.startswith("q")]
        if chosen_name in {"MASTER_SECTION", "UNIT_POSITION", "SECTION_PLUS_POSITION"}:
            portability = "SHARED_WORKFLOW_SELECTOR"
        elif chosen_name in {"ORDER", "ORDER_PLUS_POSITION", "PAGE", "PAGE_PLUS_POSITION"}:
            portability = "ORDER_OR_PAGE_SELECTOR"
        elif chosen_name in {"STAGE", "STAGE_PLUS_POSITION"}:
            portability = "STAGE_SELECTOR"
        elif chosen_name in {"UNIT", "UNIT_PLUS_POSITION"}:
            portability = "LOCAL_MINI_DECK_SELECTOR"
        else:
            portability = "MEMORIZED_IDENTITY_SELECTOR"
        family_rows.append({
            "component_recipe": recipe,
            "surface_family": " | ".join(surfaces),
            "identities": len(identities),
            "identity_list": " | ".join(identities),
            "occurrence_marks": len(local),
            "selector_feature_set": chosen_name,
            "selector_rules": len(chosen_mapping),
            "selector_portability": portability,
            "q_carrier_surfaces": " | ".join(q_surfaces) if q_surfaces else "NONE",
            "non_q_surfaces": " | ".join(surface for surface in surfaces if not surface.startswith("q")),
            "selection_accuracy": "EXACT_ON_CURRENT_DECK",
        })

    occurrence_rows = []
    for row in enriched:
        if row["component_recipe"] not in multi_recipes:
            continue
        feature, selector_key, predicted = selection_by_occurrence[str(row["order_mark_id"])]
        occurrence_rows.append({
            "order_mark_id": row["order_mark_id"],
            "component_recipe": row["component_recipe"],
            "identity": row["identity"],
            "surface": row["surface"],
            "order_id": row["order_id"],
            "master_section": row["master_section"],
            "page": row["page"],
            "stage": row["stage"],
            "unit": row["unit"],
            "unit_position": row["unit_position"],
            "position_index": row["position_index"],
            "unit_length": row["unit_length"],
            "left_surface": row["left_surface"],
            "right_surface": row["right_surface"],
            "q_carrier": "YES" if str(row["surface"]).startswith("q") else "NO",
            "selector_feature_set": feature,
            "selector_key": selector_key,
            "predicted_surface": predicted,
            "selector_match": "YES" if predicted == row["surface"] else "NO",
        })

    q_candidate_recipes = {
        row["component_recipe"]
        for row in family_rows
        if row["q_carrier_surfaces"] != "NONE" and row["non_q_surfaces"]
    }
    q_context: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in occurrence_rows:
        if row["component_recipe"] in q_candidate_recipes:
            q_context[(str(row["master_section"]), str(row["unit_position"]))][str(row["q_carrier"])] += 1
    q_rows = []
    for (section, position), counts in sorted(q_context.items()):
        total = counts["YES"] + counts["NO"]
        q_rows.append({
            "master_section": section,
            "unit_position": position,
            "q_marks": counts["YES"],
            "non_q_marks": counts["NO"],
            "total_marks": total,
            "working_choice": "Q" if counts["YES"] > counts["NO"] else "NO_Q" if counts["NO"] > counts["YES"] else "TIE",
        })

    revised_marks = []
    for row in enriched:
        if row["order_mark_id"] in selection_by_occurrence:
            feature, selector_key, predicted = selection_by_occurrence[str(row["order_mark_id"])]
            selector_status = "CONTEXT_SELECTED"
        else:
            feature, selector_key, predicted = "SINGLE_SURFACE_RECIPE", "GLOBAL", str(row["surface"])
            selector_status = "NO_CHOICE_NEEDED"
        revised_marks.append({
            **row,
            "allograph_selector_feature": feature,
            "allograph_selector_key": selector_key,
            "predicted_surface": predicted,
            "allograph_selector_status": selector_status,
            "thirteenth_lesson": "CONTEXTUAL_ALLOGRAPH_SELECTOR",
        })

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        revised_units.append({
            **unit,
            "predicted_surface_sequence": " ".join(str(row["predicted_surface"]) for row in local),
            "multi_allograph_marks": sum(row["component_recipe"] in multi_recipes for row in local),
            "selector_complete": "YES",
        })
    revised_cards = []
    for card in cards:
        local = [row for row in revised_marks if row["order_id"] == card["order_id"]]
        revised_cards.append({
            **card,
            "multi_allograph_marks": sum(row["component_recipe"] in multi_recipes for row in local),
            "context_selected_marks": sum(row["allograph_selector_status"] == "CONTEXT_SELECTED" for row in local),
            "selector_complete": "YES",
        })

    write(f"{PREFIX}_16_MULTI_ALLOGRAPH_FAMILIES.tsv", family_rows, list(family_rows[0]))
    write(f"{PREFIX}_SELECTOR_RULES.tsv", selector_rows, list(selector_rows[0]))
    write(f"{PREFIX}_MULTI_ALLOGRAPH_OCCURRENCES.tsv", occurrence_rows, list(occurrence_rows[0]))
    write(f"{PREFIX}_Q_CARRIER_CONTEXT.tsv", q_rows, list(q_rows[0]))
    write(f"{PREFIX}_437_CONTEXT_SELECTED_MARKS.tsv", revised_marks, list(marks[0]) + ["unit_position", "position_index", "unit_length", "left_surface", "right_surface", "allograph_selector_feature", "allograph_selector_key", "predicted_surface", "allograph_selector_status", "thirteenth_lesson"])
    write(f"{PREFIX}_118_CONTEXT_SELECTED_UNITS.tsv", revised_units, list(units[0]) + ["predicted_surface_sequence", "multi_allograph_marks", "selector_complete"])
    write(f"{PREFIX}_6_CONTEXT_SELECTED_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]))

    lines = [
        "# Kontextselektor für Allographen",
        "",
        "Nur 16 der 190 Wurzelrezepte haben mehr als eine belegte Oberfläche.",
        "Der Lehrling wählt zuerst nach Register und Kartenposition, dann nach Auftrag/Seite/Stufe; nur zuletzt nach dem lokalen Mini-Deck.",
        "",
        "## Die 16 Familien",
        "",
    ]
    for row in family_rows:
        lines.append(f"- `{row['component_recipe']}` → **{row['surface_family']}**: {row['selector_feature_set']} ({row['selector_portability']}; {row['occurrence_marks']} Marken).")
    lines.extend(["", "## q-Träger", ""])
    for row in q_rows:
        lines.append(f"- {row['master_section']} / {row['unit_position']}: q {row['q_marks']}, ohne q {row['non_q_marks']} → {row['working_choice']}.")
    (HERE / f"{PREFIX}_CONTEXT_SELECTOR_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    portability_counts = Counter(str(row["selector_portability"]) for row in family_rows)
    summary = {
        "status": "PASS",
        "decision": "SIXTEEN_MULTI_ALLOGRAPH_FAMILIES_RECEIVE_EXACT_CONTEXT_SELECTORS_ON_THE_CURRENT_WORKSHOP_DECK",
        "multi_allograph_families": len(family_rows),
        "multi_allograph_occurrences": len(occurrence_rows),
        "selector_rules": len(selector_rows),
        "selector_feature_sets": dict(selector_level_counts),
        "selector_portability": dict(portability_counts),
        "q_candidate_families": len(q_candidate_recipes),
        "q_context_cells": len(q_rows),
        "selector_matches": sum(row["selector_match"] == "YES" for row in occurrence_rows),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 902: kontextueller Allographenselektor\n\n"
        "Die 16 mehrdeutigen Wurzelrezepte werden auf allen aktuellen Vorkommen mit einer kurzen Priorität aus Register, Kartenposition, Auftrag, Seite, Stufe und lokalem Mini-Deck ausgewählt. "
        "Damit erzeugt der Schreiber für jede der 437 Marken die beobachtete Oberfläche; die verbleibende Lernlast steht explizit pro Familie im Selektorhandbuch.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
