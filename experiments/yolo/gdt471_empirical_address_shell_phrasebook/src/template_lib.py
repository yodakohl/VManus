#!/usr/bin/env python3
"""Derive empirical learned-slot templates and attach familiarity metadata."""

from __future__ import annotations

from typing import Any


EMPIRICAL_FIELDS = [
    "empirical_familiarity_state",
    "empirical_familiarity_rank",
    "empirical_match_level",
    "empirical_surface_template_id",
    "empirical_component_template_id",
    "empirical_topology_id",
    "empirical_surface_template",
    "empirical_component_template",
    "empirical_meaning_template_de",
    "empirical_slot_topology",
    "empirical_learned_span_trace",
    "empirical_source_count",
    "empirical_content_class_count",
    "empirical_page_count",
    "empirical_observed_content_classes",
    "empirical_observed_pages",
    "empirical_source_surfaces",
    "empirical_owner_relation",
    "family_marker_policy",
]


def derive_template(surface: str, rules: list[dict[str, str]], select_fn: Any) -> dict[str, object]:
    selected = select_fn(surface, rules)
    surface_parts: list[str] = []
    component_parts: list[str] = []
    meaning_parts: list[str] = []
    topology_parts: list[str] = []
    learned_spans: list[str] = []
    cursor = 0
    slot = 0

    def add_name(start: int, end: int) -> None:
        nonlocal slot
        slot += 1
        marker = f"{{NAME_{slot}}}"
        surface_parts.append(marker)
        component_parts.append(marker)
        meaning_parts.append(marker)
        topology_parts.append(marker)
        learned_spans.append(f"{start}:{end}:{surface[start:end]}")

    for channel in selected:
        start, end = int(channel["start"]), int(channel["end"])
        if cursor < start:
            add_name(cursor, start)
        surface_parts.append(str(channel["surface_stem"]))
        component_parts.append(str(channel["component_recipe"]))
        meaning_parts.append(str(channel["literal_working_value_de"]))
        topology_parts.append(str(channel["channel_kind"]))
        cursor = end
    if cursor < len(surface):
        add_name(cursor, len(surface))

    return {
        "surface_template": "".join(surface_parts),
        "component_template": " · ".join(component_parts),
        "meaning_template_de": " · ".join(meaning_parts),
        "slot_topology": " · ".join(topology_parts),
        "exact_channel_signature": "+".join(str(row["channel_id"]) for row in selected) or "NONE",
        "channel_shape": "+".join(str(row["channel_kind"]) for row in selected) or "NONE",
        "function_channel_count": len(selected),
        "learned_slot_count": slot,
        "learned_span_trace": "|".join(learned_spans),
        "learned_character_count": sum(int(item.split(":", 2)[1]) - int(item.split(":", 2)[0]) for item in learned_spans),
    }


def split_pipe(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def attach_familiarity(
    reading: dict[str, object],
    template: dict[str, object],
    surface_deck: dict[str, dict[str, str]],
    component_deck: dict[str, dict[str, str]],
    topology_deck: dict[str, dict[str, str]],
) -> dict[str, object]:
    surface_row = surface_deck.get(str(template["surface_template"]))
    component_row = component_deck.get(str(template["component_template"]))
    topology_row = topology_deck.get(str(template["slot_topology"]))

    if reading["known_label"] == "YES":
        state, rank, level = "EXACT_LABEL_CARD", 0, "EXACT_LABEL_CARD"
        matched = surface_row or component_row or topology_row
    elif int(template["function_channel_count"]) == 0:
        state, rank, level = "WHOLE_NAME_DEFAULT", 7, "WHOLE_NAME_DEFAULT"
        matched = surface_row or topology_row
    elif surface_row:
        state = surface_row["familiarity_state"]
        rank = int(surface_row["familiarity_rank"])
        level = "EXACT_EMPIRICAL_SURFACE_TEMPLATE"
        matched = surface_row
    elif component_row:
        state, rank, level = "KNOWN_COMPONENT_TEMPLATE_ALTERNATE_RENDERING", 5, "COMPONENT_TEMPLATE"
        matched = component_row
    elif topology_row:
        state, rank, level = "KNOWN_SLOT_TOPOLOGY_ONLY", 6, "SLOT_TOPOLOGY"
        matched = topology_row
    else:
        state, rank, level = "UNSEEN_SLOT_TOPOLOGY", 8, "NONE"
        matched = None

    classes = split_pipe(matched.get("content_classes", "NONE")) if matched else []
    pages = split_pipe(matched.get("physical_pages", "NONE")) if matched else []
    surfaces = split_pipe(matched.get("source_surfaces", "NONE")) if matched else []
    if reading["known_label"] == "YES":
        owner_relation = "EXACT_LABEL_OWNER"
    elif str(reading["content_class"]) in classes:
        owner_relation = "OWNER_CLASS_ATTESTED_FOR_MATCH"
    elif classes:
        owner_relation = "OWNER_CLASS_NEW_FOR_MATCH"
    else:
        owner_relation = "NO_EMPIRICAL_OWNER_MATCH"

    return {
        "empirical_familiarity_state": state,
        "empirical_familiarity_rank": rank,
        "empirical_match_level": level,
        "empirical_surface_template_id": surface_row["surface_template_id"] if surface_row else "NONE",
        "empirical_component_template_id": component_row["component_template_id"] if component_row else "NONE",
        "empirical_topology_id": topology_row["topology_id"] if topology_row else "NONE",
        "empirical_surface_template": template["surface_template"],
        "empirical_component_template": template["component_template"],
        "empirical_meaning_template_de": template["meaning_template_de"],
        "empirical_slot_topology": template["slot_topology"],
        "empirical_learned_span_trace": template["learned_span_trace"],
        "empirical_source_count": int(matched["source_count"]) if matched else 0,
        "empirical_content_class_count": len(classes),
        "empirical_page_count": len(pages),
        "empirical_observed_content_classes": "|".join(classes) or "NONE",
        "empirical_observed_pages": "|".join(pages) or "NONE",
        "empirical_source_surfaces": "|".join(surfaces) or "NONE",
        "empirical_owner_relation": owner_relation,
        "family_marker_policy": "REPORT_SEPARATELY__NEVER_PROMOTE_TO_FUNCTION_TEMPLATE",
    }
