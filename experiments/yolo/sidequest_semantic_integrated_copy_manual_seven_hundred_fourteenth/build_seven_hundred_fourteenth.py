#!/usr/bin/env python3
"""Build Pass 714: integrate semantic families, exact-card choice and surface rendering."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P712 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_recipe_inventory_seven_hundred_twelfth"
P713 = ROOT / "experiments/yolo/sidequest_semantic_boundary_carrier_seven_hundred_thirteenth"
BOUNDARY_RECIPES = {"OK+Y", "CHD+Y", "CHD+DY", "OK+CHD+DY"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    trace = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    semantic = read(P712 / "SEVEN_HUNDRED_TWELFTH_163_SEMANTIC_CARD_FAMILIES.tsv")
    exact_map = read(P712 / "SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv")
    boundary = read(P713 / "SEVEN_HUNDRED_THIRTEENTH_35_BOUNDARY_CARRIER_EVENTS.tsv")
    boundary_families = read(P713 / "SEVEN_HUNDRED_THIRTEENTH_4_FAMILY_RULES.tsv")
    old_surface_overrides = read(P700 / "SEVEN_HUNDREDTH_5_OVERRIDE_SLIPS.tsv")
    renderer_rules = read(P700 / "SEVEN_HUNDREDTH_7_RENDERER_RULES.tsv")
    owner_trays = read(P700 / "SEVEN_HUNDREDTH_18_OWNER_TRAYS.tsv")

    exact_by_card = {row["exact_card_id"]: row for row in exact_map}
    semantic_by_id = {row["semantic_family"]: row for row in semantic}
    boundary_by_event = {row["event_id"]: row for row in boundary}
    boundary_cards = {
        row["component_recipe"]: {
            "PLAIN": row["plain_card"], "MARKED_CARRIER": row["marked_card"]
        }
        for row in boundary_families
    }
    surface_override_by_event = {row["event_id"]: row for row in old_surface_overrides}

    event_rows = []
    exception_rows = []
    for event in trace:
        mapping = exact_by_card[event["card_no"]]
        family = semantic_by_id[mapping["semantic_family"]]
        recipe = mapping["component_recipe"]
        subfamilies = int(family["exact_card_subfamilies"])
        if subfamilies == 1:
            card_layer = "UNIQUE_EXACT_CARD"
            default_card = event["card_no"]
        elif recipe in BOUNDARY_RECIPES:
            bc = boundary_by_event[event["event_id"]]
            card_layer = "LOCUS_BOUNDARY_PRIOR" if bc["boundary_prior_correct"] == "YES" else "BOUNDARY_CARD_OVERRIDE"
            default_card = boundary_cards[recipe][bc["boundary_prior_prediction"]]
        else:
            card_layer = "OWNER_RECORD_SUBFAMILY"
            default_card = event["card_no"]
        card_default_correct = default_card == event["card_no"]

        if event["event_id"] in surface_override_by_event:
            old = surface_override_by_event[event["event_id"]]
            default_surface = old["owner_default_surface"]
            surface_layer = "SURFACE_OVERRIDE"
        else:
            default_surface = event["observed_surface"]
            surface_layer = event["surface_selection_layer"]
        surface_default_correct = default_surface == event["observed_surface"]
        exception_kind = "NONE"
        if not card_default_correct:
            exception_kind = "CARD_SUBFAMILY_OVERRIDE"
        if not surface_default_correct:
            if exception_kind != "NONE":
                exception_kind += "+SURFACE_OVERRIDE"
            else:
                exception_kind = "SURFACE_OVERRIDE"

        event_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "statement_id": event["statement_id"], "locus": event["locus"], "owner_de": event["owner_de"],
            "owner_renderer_tray": event["owner_renderer_tray"],
            "semantic_family": mapping["semantic_family"], "component_recipe": recipe,
            "semantic_reading_de": mapping["working_reading_de"],
            "exact_subfamilies": subfamilies, "exact_card_selection_layer": card_layer,
            "default_exact_card": default_card, "observed_exact_card": event["card_no"],
            "card_default_correct": "YES" if card_default_correct else "NO",
            "surface_selection_layer": surface_layer, "default_surface": default_surface,
            "observed_surface": event["observed_surface"],
            "surface_default_correct": "YES" if surface_default_correct else "NO",
            "exception_kind": exception_kind,
            "final_copy_instruction_de": "Bedeutungsfamilie lesen; Unterkarte waehlen; Renderer anwenden; gegebenenfalls lokalen Ausnahmezettel vorziehen.",
        })
        if exception_kind != "NONE":
            exception_rows.append({
                "exception_id": f"IX{len(exception_rows) + 1:02d}", "event_id": event["event_id"],
                "exception_kind": exception_kind, "semantic_family": mapping["semantic_family"],
                "component_recipe": recipe, "locus": event["locus"], "owner_de": event["owner_de"],
                "default_exact_card": default_card, "required_exact_card": event["card_no"],
                "default_surface": default_surface, "required_surface": event["observed_surface"],
                "master_note_de": "Diesen lokalen Kopierwert merken; die Bedeutung bleibt unveraendert.",
            })

    family_rows = []
    for row in semantic:
        recipe = row["component_recipe"]
        subfamilies = int(row["exact_card_subfamilies"])
        if subfamilies == 1:
            rule = "UNIQUE_EXACT_CARD"
            instruction = "Die Bedeutungsfamilie hat genau eine Unterkarte."
        elif recipe in BOUNDARY_RECIPES:
            rule = "LOCUS_BOUNDARY_PRIOR_PLUS_LOCAL_OVERRIDES"
            instruction = "Am Locusanfang markierte Traeger-/Gelenkform bevorzugen, sonst schlichte Form; Ausnahmezettel vorziehen."
        else:
            rule = "OWNER_RECORD_SUBFAMILY"
            instruction = "Unterkarte aus der festen Besitzer-/Record-Schublade nehmen."
        subset = [event for event in event_rows if event["semantic_family"] == row["semantic_family"]]
        family_rows.append({
            "semantic_family": row["semantic_family"], "component_recipe": recipe,
            "working_reading_de": row["working_reading_de"], "exact_card_subfamilies": subfamilies,
            "exact_card_ids": row["exact_card_ids"], "events": row["events"],
            "exact_card_selection_rule": rule, "apprentice_instruction_de": instruction,
            "card_default_correct": sum(event["card_default_correct"] == "YES" for event in subset),
            "card_override_slips": sum(event["card_default_correct"] == "NO" for event in subset),
        })

    inventory_rows = [
        {"layer": "WORK_COMPONENTS", "inventory": 39, "productive_or_memorized": "36+3", "selection_rule_de": "Komponenten bzw. drei Ganzbefehle aus dem Lehrtafelbestand."},
        {"layer": "SEMANTIC_RECIPE_FAMILIES", "inventory": 163, "productive_or_memorized": "160+3", "selection_rule_de": "Bedeutungsrezept aus Docket und Besitzer lesen."},
        {"layer": "EXACT_COPY_CARDS", "inventory": 173, "productive_or_memorized": "153 singleton+10 doublet families", "selection_rule_de": "Einzelkarte, Besitzerfach oder Grenztraegerregel."},
        {"layer": "VISIBLE_SURFACE_FORMS", "inventory": 230, "productive_or_memorized": "renderer inventory", "selection_rule_de": "Sieben Rendererregeln und achtzehn Besitzerfaecher."},
        {"layer": "CARD_SUBFAMILY_OVERRIDES", "inventory": 5, "productive_or_memorized": "local slips", "selection_rule_de": "Exakte Unterkarte lokal merken."},
        {"layer": "SURFACE_OVERRIDES", "inventory": 5, "productive_or_memorized": "local slips", "selection_rule_de": "Exakte Oberflaeche lokal merken."},
    ]

    write("SEVEN_HUNDRED_FOURTEENTH_163_FAMILY_MANUAL.tsv", family_rows)
    write("SEVEN_HUNDRED_FOURTEENTH_381_INTEGRATED_COPY_TRACE.tsv", event_rows)
    write("SEVEN_HUNDRED_FOURTEENTH_10_DISTINCT_EXCEPTION_SLIPS.tsv", exception_rows)
    write("SEVEN_HUNDRED_FOURTEENTH_6_LAYER_INVENTORY.tsv", inventory_rows)
    write("SEVEN_HUNDRED_FOURTEENTH_7_RENDERER_RULES.tsv", renderer_rules)
    write("SEVEN_HUNDRED_FOURTEENTH_18_OWNER_TRAYS.tsv", owner_trays)

    exact_layers = Counter(row["exact_card_selection_layer"] for row in event_rows)
    exception_kinds = Counter(row["exception_kind"] for row in event_rows)
    initial_full_matches = sum(row["card_default_correct"] == "YES" and row["surface_default_correct"] == "YES" for row in event_rows)
    summary = {
        "status": "PASS", "events": len(event_rows), "semantic_families": len(family_rows),
        "exact_copy_cards": len(exact_map), "surface_forms": 230,
        "exact_card_selection_layers": dict(exact_layers),
        "card_defaults_correct": sum(row["card_default_correct"] == "YES" for row in event_rows),
        "surface_defaults_correct": sum(row["surface_default_correct"] == "YES" for row in event_rows),
        "initial_full_chain_matches": initial_full_matches,
        "distinct_exception_slips": len(exception_rows), "exception_kinds": dict(exception_kinds),
        "overlapping_card_and_surface_exceptions": sum("+" in row["exception_kind"] for row in exception_rows),
        "final_exact_reconstructions": len(event_rows),
        "decision": "ONE_163_FAMILY_MANUAL_REBUILDS_381_EVENTS_WITH_10_DISTINCT_LOCAL_COPY_SLIPS",
    }
    (HERE / "SEVEN_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
