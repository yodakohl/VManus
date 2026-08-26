#!/usr/bin/env python3
"""Shared deterministic address-intake functions for GDT466."""

from __future__ import annotations

import csv
from pathlib import Path


NAME_CLASSES = {
    "STAR_BEARING_RING_POSITION": "STERNSTELLENNAME",
    "DRUG_OR_INGREDIENT_OBJECT": "DROGENNAME",
    "BATH_OR_OUTLET_STATION": "BADSTATIONSNAME",
    "PICTURED_PLANT": "PFLANZENNAME",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def placeholder(content_class: str, surface: str) -> str:
    return f"[{NAME_CLASSES.get(content_class, 'LOKALNAME')}:{surface}]"


def select_function_channels(surface: str, rules: list[dict[str, str]]) -> list[dict[str, object]]:
    """Apply longest directional edges, then longest nonoverlapping internals."""
    prefix_rules = [row for row in rules if row["channel_kind"] == "PREFIX" and surface.startswith(row["surface_stem"])]
    prefix = min(prefix_rules, key=lambda row: (-len(row["surface_stem"]), row["surface_stem"], row["channel_id"])) if prefix_rules else None
    prefix_end = len(prefix["surface_stem"]) if prefix else 0

    suffix_rules = [
        row for row in rules
        if row["channel_kind"] == "SUFFIX"
        and surface.endswith(row["surface_stem"])
        and prefix_end + len(row["surface_stem"]) <= len(surface)
    ]
    suffix = min(suffix_rules, key=lambda row: (-len(row["surface_stem"]), row["surface_stem"], row["channel_id"])) if suffix_rules else None
    suffix_start = len(surface) - len(suffix["surface_stem"]) if suffix else len(surface)

    selected: list[dict[str, object]] = []
    if prefix:
        selected.append({**prefix, "start": 0, "end": prefix_end})
    if suffix:
        selected.append({**suffix, "start": suffix_start, "end": len(surface)})

    candidates: list[dict[str, object]] = []
    for row in rules:
        if row["channel_kind"] != "INTERNAL":
            continue
        stem = row["surface_stem"]
        for start in range(1, len(surface) - len(stem)):
            end = start + len(stem)
            if start >= prefix_end and end <= suffix_start and surface.startswith(stem, start):
                candidates.append({**row, "start": start, "end": end})

    occupied = {position for item in selected for position in range(int(item["start"]), int(item["end"]))}
    for candidate in sorted(candidates, key=lambda item: (-len(str(item["surface_stem"])), int(item["start"]), str(item["surface_stem"]), str(item["channel_id"]))):
        interval = set(range(int(candidate["start"]), int(candidate["end"])))
        if not interval & occupied:
            selected.append(candidate)
            occupied.update(interval)

    return sorted(selected, key=lambda item: (int(item["start"]), int(item["end"]), str(item["channel_id"])))


def matching_families(surface: str, content_class: str, families: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        (row for row in families if row["content_class"] == content_class and row["surface_stem"] in surface),
        key=lambda row: (-len(row["surface_stem"]), row["surface_stem"], row["family_id"]),
    )


def render_unknown(surface: str, content_class: str, selected: list[dict[str, object]]) -> str:
    if not selected:
        return placeholder(content_class, surface)
    pieces: list[str] = []
    cursor = 0
    for item in selected:
        start, end = int(item["start"]), int(item["end"])
        if cursor < start:
            pieces.append(placeholder(content_class, surface[cursor:start]))
        pieces.append(str(item["literal_working_value_de"]))
        cursor = end
    if cursor < len(surface):
        pieces.append(placeholder(content_class, surface[cursor:]))
    return " · ".join(pieces)


def intake(
    surface: str,
    content_class: str,
    rules: list[dict[str, str]],
    families: list[dict[str, str]],
    exact_labels: dict[str, dict[str, str]],
) -> dict[str, object]:
    if surface in exact_labels:
        row = exact_labels[surface]
        hybrid_status = row.get("gdt466_hybrid_status", row["gdt465_hybrid_status"])
        return {
            "surface": surface,
            "content_class": row["content_class"],
            "route": "EXACT_KNOWN_LABEL",
            "known_label": "YES",
            "hybrid_status": hybrid_status,
            "selected_function_channels": row["ordered_function_recipe_trace"],
            "known_function_character_count": int(row["known_function_character_count"]),
            "learned_character_count": int(row["remaining_learned_character_count"]),
            "family_markers": row["owner_family_stem_trace"],
            "ordered_recipe_trace": row["ordered_function_recipe_trace"],
            "reading_de": row["revised_short_default_de"],
        }

    selected = select_function_channels(surface, rules)
    families_found = matching_families(surface, content_class, families)
    covered = sum(int(item["end"]) - int(item["start"]) for item in selected)
    if covered == len(surface) and selected:
        route = "CALIBRATED_FULL_FUNCTION_FORMULA"
        status = "FULL_FUNCTION_FORMULA"
    elif selected:
        route = "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE"
        status = "FUNCTION_SHELL_PLUS_LEARNED_CORE"
    elif families_found:
        route = "STRICT_OWNER_FAMILY_PLUS_LEARNED_NAME"
        status = "OWNER_FAMILY_STEM_ONLY"
    else:
        route = "WHOLE_LEARNED_OWNER_NAME"
        status = "WHOLE_LEARNED_LABEL"
    channel_trace = "|".join(
        f"{item['start']}:{item['end']}:{item['surface_stem']}={item['component_recipe']}"
        for item in selected
    ) or "NONE"
    family_trace = "|".join(f"{row['surface_stem']}={row['working_family_value_de']}" for row in families_found) or "NONE"
    recipe_trace = "+".join(str(item["component_recipe"]) for item in selected) or "NONE"
    return {
        "surface": surface,
        "content_class": content_class,
        "route": route,
        "known_label": "NO",
        "hybrid_status": status,
        "selected_function_channels": channel_trace,
        "known_function_character_count": covered,
        "learned_character_count": len(surface) - covered,
        "family_markers": family_trace,
        "ordered_recipe_trace": recipe_trace,
        "reading_de": render_unknown(surface, content_class, selected),
    }
