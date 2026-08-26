#!/usr/bin/env python3
"""Attach GDT468 recipe provenance to the GDT466 address intake."""

from __future__ import annotations

from typing import Any


def supported_intake(
    surface: str,
    content_class: str,
    rules: list[dict[str, str]],
    families: list[dict[str, str]],
    exact_labels: dict[str, dict[str, str]],
    recipe_atlas: dict[str, dict[str, str]],
    shell_atlas: dict[str, dict[str, str]],
    intake_fn: Any,
    select_fn: Any,
) -> dict[str, object]:
    base = intake_fn(surface, content_class, rules, families, exact_labels)
    if base["known_label"] == "YES":
        channel_signature = f"EXACT_LABEL_CARD:{surface}"
        shell = None
    else:
        selected = select_fn(surface, rules)
        channel_signature = "+".join(str(item["channel_id"]) for item in selected) or "NONE"
        shell = shell_atlas.get(channel_signature)
    recipe = str(base["ordered_recipe_trace"])
    support = recipe_atlas.get(recipe)
    tier = support["support_tier"] if support else "OUTSIDE_BOUNDED_SHELL_ATLAS"
    result = {
        **base,
        "exact_channel_signature": channel_signature,
        "bounded_shell_match": "YES" if shell else "NO",
        "bounded_shell_id": shell["shell_id"] if shell else "NONE",
        "bounded_surface_template": shell["surface_template"] if shell else "NONE",
        "recipe_support_tier": tier,
        "recipe_support_rank": int(support["support_rank"]) if support else 0,
        "running_surface_type_count": int(support["running_surface_type_count"]) if support else 0,
        "running_event_count": int(support["running_event_count"]) if support else 0,
        "running_page_count": int(support["running_page_count"]) if support else 0,
        "address_full_formula_count": int(support["address_full_formula_count"]) if support else 0,
        "address_hybrid_shell_count": int(support["address_hybrid_shell_count"]) if support else 0,
        "support_explanation": (
            "EXACT_RUNNING_RECIPE_CARRIERS_EXIST" if tier == "RUNNING_EXACT_RECIPE"
            else "COMPLETE_ADDRESS_FORMULA_CARRIER_EXISTS" if tier == "ADDRESS_FULL_FORMULA_ONLY"
            else "ADDRESS_FUNCTION_TRACE_ACROSS_LEARNED_CORE_EXISTS" if tier == "ADDRESS_HYBRID_SHELL_ONLY"
            else "OLD_CHANNEL_COMPOSITION_WITHOUT_OLD_WHOLE_RECIPE" if tier == "COMPOSITION_ONLY"
            else "NO_MATCH_IN_THE_BOUNDED_PREFIX_SUFFIX_SHELL_ATLAS"
        ),
    }
    return result
