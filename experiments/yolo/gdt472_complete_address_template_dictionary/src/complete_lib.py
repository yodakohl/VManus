#!/usr/bin/env python3
"""Attach complete 107-label dictionary metadata to a ranked worksheet row."""

from __future__ import annotations


COMPLETE_FIELDS = [
    "complete_dictionary_status",
    "complete_assignment_mode",
    "complete_template_id",
    "complete_transferability",
    "complete_exact_package_card_id",
    "complete_exact_package_dependency",
    "complete_reader_policy",
]


def attach_complete_metadata(
    reading: dict[str, object],
    empirical: dict[str, object],
    assignment_map: dict[str, dict[str, str]],
    package_map: dict[str, dict[str, str]],
) -> dict[str, object]:
    surface = str(reading["surface"])
    assignment = assignment_map.get(surface) if reading["known_label"] == "YES" else None
    package = package_map.get(surface) if assignment else None
    if assignment:
        mode = assignment["assignment_mode"]
        template_id = assignment["complete_template_id"]
        transferability = assignment["transferable"]
        policy = "EXACT_LABEL_CARD_FIRST__THEN_REPORT_ITS_COMPLETE_TEMPLATE_MODE"
    else:
        mode = "UNSEEN_FORM_RANKED_BY_TRANSFERABLE_TEMPLATE"
        template_id = str(
            empirical["empirical_surface_template_id"]
            if empirical["empirical_surface_template_id"] != "NONE"
            else empirical["empirical_component_template_id"]
            if empirical["empirical_component_template_id"] != "NONE"
            else empirical["empirical_topology_id"]
        )
        transferability = "POST_SURFACE_READING_ONLY"
        policy = "USE_VISIBLE_CHANNELS__KEEP_NAME_SLOTS__ANNOTATE_EMPIRICAL_FAMILIARITY"
    return {
        "complete_dictionary_status": "COMPLETE_107_LABEL_TEMPLATE_DICTIONARY_READY",
        "complete_assignment_mode": mode,
        "complete_template_id": template_id,
        "complete_transferability": transferability,
        "complete_exact_package_card_id": package["exact_package_card_id"] if package else "NONE",
        "complete_exact_package_dependency": package["dependency_reason"] if package else "NONE",
        "complete_reader_policy": policy,
    }
