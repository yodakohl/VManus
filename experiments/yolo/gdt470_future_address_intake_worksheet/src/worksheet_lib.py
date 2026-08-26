#!/usr/bin/env python3
"""Turn one supported address reading into a future-page worksheet row."""

from __future__ import annotations

from typing import Any


OLD_CARRIER_TIERS = {
    "RUNNING_EXACT_RECIPE",
    "ADDRESS_FULL_FORMULA_ONLY",
    "ADDRESS_HYBRID_SHELL_ONLY",
}

WORKSHEET_FIELDS = [
    "batch_id",
    "page_slot",
    "item_slot",
    "page_id",
    "locus_id",
    "owner_description",
    "content_class",
    "surface_zl3b",
    "surface_it2a",
    "surface_rf1b",
    "selected_surface",
    "transcription_agreement",
    "reader_route",
    "working_reading_de",
    "exact_channel_signature",
    "ordered_recipe_trace",
    "bounded_shell_id",
    "bounded_surface_template",
    "recipe_support_tier",
    "recipe_support_rank",
    "running_event_count",
    "running_page_count",
    "address_full_formula_count",
    "address_hybrid_shell_count",
    "known_function_character_count",
    "learned_character_count",
    "family_markers",
    "intake_action",
    "retroactive_core_change",
    "notes",
]


def transcription_agreement(*readings: str) -> str:
    supplied = [value for value in readings if value]
    if not supplied:
        return "NO_MANUAL_READING_RECORDED"
    if len(supplied) == 1:
        return "ONE_MANUAL_READING_RECORDED"
    if len(set(supplied)) == 1:
        return "SUPPLIED_READINGS_AGREE"
    return "SUPPLIED_READINGS_DIFFER"


def intake_action(reading: dict[str, object]) -> str:
    if reading["known_label"] == "YES":
        return "REUSE_EXACT_LABEL_CARD"
    route = str(reading["route"])
    tier = str(reading["recipe_support_tier"])
    if route == "CALIBRATED_FULL_FUNCTION_FORMULA":
        if tier in OLD_CARRIER_TIERS:
            return "READ_SUPPORTED_FULL_FUNCTION_FORMULA"
        return "READ_VISIBLE_FULL_FUNCTION_COMPOSITION"
    if route == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE":
        if tier in OLD_CARRIER_TIERS:
            return "READ_SUPPORTED_FUNCTION_SHELL_KEEP_NAME_CORE"
        if tier == "COMPOSITION_ONLY":
            return "READ_COMPOSED_FUNCTION_SHELL_KEEP_NAME_CORE"
        return "READ_VISIBLE_FUNCTION_SHELL_KEEP_NAME_CORE"
    if route == "STRICT_OWNER_FAMILY_PLUS_LEARNED_NAME":
        return "KEEP_OWNER_FAMILY_AND_LEARN_NAME"
    return "LEARN_WHOLE_OWNER_BOUND_NAME"


def make_worksheet_row(
    reading: dict[str, object],
    *,
    batch_id: str,
    page_slot: str,
    item_slot: str,
    page_id: str,
    locus_id: str,
    owner_description: str,
    surface_zl3b: str,
    surface_it2a: str,
    surface_rf1b: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "batch_id": batch_id,
        "page_slot": page_slot,
        "item_slot": item_slot,
        "page_id": page_id,
        "locus_id": locus_id,
        "owner_description": owner_description,
        "content_class": reading["content_class"],
        "surface_zl3b": surface_zl3b,
        "surface_it2a": surface_it2a,
        "surface_rf1b": surface_rf1b,
        "selected_surface": reading["surface"],
        "transcription_agreement": transcription_agreement(surface_zl3b, surface_it2a, surface_rf1b),
        "reader_route": reading["route"],
        "working_reading_de": reading["reading_de"],
        "exact_channel_signature": reading["exact_channel_signature"],
        "ordered_recipe_trace": reading["ordered_recipe_trace"],
        "bounded_shell_id": reading["bounded_shell_id"],
        "bounded_surface_template": reading["bounded_surface_template"],
        "recipe_support_tier": reading["recipe_support_tier"],
        "recipe_support_rank": reading["recipe_support_rank"],
        "running_event_count": reading["running_event_count"],
        "running_page_count": reading["running_page_count"],
        "address_full_formula_count": reading["address_full_formula_count"],
        "address_hybrid_shell_count": reading["address_hybrid_shell_count"],
        "known_function_character_count": reading["known_function_character_count"],
        "learned_character_count": reading["learned_character_count"],
        "family_markers": reading["family_markers"],
        "intake_action": intake_action(reading),
        "retroactive_core_change": "NO",
        "notes": notes,
    }
