#!/usr/bin/env python3
"""Build the complete 107-label empirical address template dictionary."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt472_complete_address_template_dictionary"
OUT = BASE / "artifacts"
G463 = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges"
G464 = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G469 = ROOT / "experiments/yolo/gdt469_provenance_aware_address_reader"
G470 = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
G471 = ROOT / "experiments/yolo/gdt471_empirical_address_shell_phrasebook"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(G470 / "src"))
sys.path.insert(0, str(G471 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402
from worksheet_lib import WORKSHEET_FIELDS  # noqa: E402
from template_lib import EMPIRICAL_FIELDS, derive_template  # noqa: E402
from complete_lib import COMPLETE_FIELDS  # noqa: E402


OLD_CARRIER_TIERS = {
    "RUNNING_EXACT_RECIPE",
    "ADDRESS_FULL_FORMULA_ONLY",
    "ADDRESS_HYBRID_SHELL_ONLY",
}


def write_tsv(
    path: Path,
    rows: list[dict[str, object]],
    fieldnames: list[str] | None = None,
) -> None:
    columns = fieldnames or (list(rows[0]) if rows else None)
    if not columns:
        raise ValueError(f"No columns supplied for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def joined(values: set[str]) -> str:
    return "|".join(sorted(values)) or "NONE"


def familiarity_for_group(
    source_count: int,
    class_count: int,
    page_count: int,
    function_channel_count: int,
) -> tuple[str, int]:
    if function_channel_count == 0:
        return "WHOLE_NAME_DEFAULT", 7
    if source_count > 1 and class_count > 1:
        return "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE", 1
    if source_count > 1 and page_count > 1:
        return "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE", 2
    if source_count > 1:
        return "RECURRENT_EXACT_FUNCTION_TEMPLATE", 3
    return "SINGLETON_EXACT_FUNCTION_TEMPLATE", 4


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    families = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    old_assignments = read_tsv(G471 / "artifacts/gdt471_89_template_assignments.tsv")
    exact_support = read_tsv(G469 / "artifacts/gdt469_107_exact_supported_replay.tsv")
    ykyd_evidence = next(row for row in read_tsv(G463 / "artifacts/gdt463_4_target_reconstructions.tsv") if row["surface"] == "ykyd")
    yddy_evidence = next(row for row in read_tsv(G464 / "artifacts/gdt464_10_target_revisions.tsv") if row["surface"] == "yddy")
    label_map = {row["surface"]: row for row in labels}
    support_map = {row["surface"]: row for row in exact_support}
    old_assignment_map = {row["source_surface"]: row for row in old_assignments}
    exact_label_map = {row["surface"]: row for row in labels}

    full_labels = [row for row in labels if row["gdt466_hybrid_status"] == "FULL_FUNCTION_FORMULA"]
    full_replay_rows: list[dict[str, object]] = []
    general_full_surfaces: set[str] = set()
    exact_package_surfaces: list[str] = []
    cold_map: dict[str, dict[str, object]] = {}
    for ordinal, label in enumerate(full_labels, start=1):
        cold = intake(label["surface"], label["content_class"], rules, families, {})
        exact = intake(label["surface"], label["content_class"], rules, families, exact_label_map)
        cold_map[label["surface"]] = cold
        general = (
            cold["route"] == "CALIBRATED_FULL_FUNCTION_FORMULA"
            and cold["ordered_recipe_trace"] == label["ordered_function_recipe_trace"]
            and int(cold["known_function_character_count"]) == int(label["surface_character_count"])
            and cold["reading_de"] == label["revised_short_default_de"]
        )
        if general:
            replay_class = "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE"
            general_full_surfaces.add(label["surface"])
        else:
            replay_class = "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD"
            exact_package_surfaces.append(label["surface"])
        passed = (
            general
            or (
                label["surface"] in {"ykyd", "yddy"}
                and exact["route"] == "EXACT_KNOWN_LABEL"
                and exact["reading_de"] == label["revised_short_default_de"]
            )
        )
        full_replay_rows.append({
            "replay_id": f"G472-F{ordinal:02d}",
            "label_id": label["gdt466_label_id"],
            "surface": label["surface"],
            "content_class": label["content_class"],
            "physical_page": label["physical_page"],
            "source_recipe": label["ordered_function_recipe_trace"],
            "source_reading_de": label["revised_short_default_de"],
            "cold_route": cold["route"],
            "cold_recipe": cold["ordered_recipe_trace"],
            "cold_reading_de": cold["reading_de"],
            "cold_known_character_count": cold["known_function_character_count"],
            "surface_character_count": label["surface_character_count"],
            "cold_complete_recipe_match": "YES" if general else "NO",
            "replay_class": replay_class,
            "exact_label_reading_pass": "YES" if exact["route"] == "EXACT_KNOWN_LABEL" and exact["reading_de"] == label["revised_short_default_de"] else "NO",
            "replay_pass": "YES" if passed else "NO",
        })

    entries: list[dict[str, object]] = []
    for old in old_assignments:
        label = label_map[old["source_surface"]]
        entries.append({
            "label": label,
            "template": {
                "surface_template": old["surface_template"],
                "component_template": old["component_template"],
                "meaning_template_de": old["meaning_template_de"],
                "slot_topology": old["slot_topology"],
                "exact_channel_signature": old["exact_channel_signature"],
                "channel_shape": old["channel_shape"],
                "function_channel_count": int(old["function_channel_count"]),
                "learned_slot_count": int(old["learned_slot_count"]),
                "learned_span_trace": old["learned_span_trace"],
            },
            "assignment_mode": "LEARNED_SLOT_TEMPLATE",
            "cold": intake(label["surface"], label["content_class"], rules, families, {}),
            "support": support_map[label["surface"]],
        })
    for label in full_labels:
        if label["surface"] not in general_full_surfaces:
            continue
        entries.append({
            "label": label,
            "template": derive_template(label["surface"], rules, select_function_channels),
            "assignment_mode": "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE",
            "cold": cold_map[label["surface"]],
            "support": support_map[label["surface"]],
        })

    surface_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    component_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    topology_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        template = entry["template"]
        surface_groups[str(template["surface_template"])].append(entry)
        component_groups[str(template["component_template"])].append(entry)
        topology_groups[str(template["slot_topology"])].append(entry)

    surface_ids = {key: f"G472-T{ordinal:03d}" for ordinal, key in enumerate(sorted(surface_groups), start=1)}
    component_ids = {key: f"G472-C{ordinal:03d}" for ordinal, key in enumerate(sorted(component_groups), start=1)}
    topology_ids = {key: f"G472-P{ordinal:02d}" for ordinal, key in enumerate(sorted(topology_groups), start=1)}

    surface_rows: list[dict[str, object]] = []
    for key in sorted(surface_groups):
        group = surface_groups[key]
        templates = [entry["template"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        function_counts = {int(template["function_channel_count"]) for template in templates}
        classes = {str(label["content_class"]) for label in labels_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        state, rank = familiarity_for_group(len(group), len(classes), len(pages), min(function_counts))
        surface_rows.append({
            "surface_template_id": surface_ids[key],
            "surface_template": key,
            "template_modes": joined({str(entry["assignment_mode"]) for entry in group}),
            "component_template_ids": joined({component_ids[str(template["component_template"])] for template in templates}),
            "topology_ids": joined({topology_ids[str(template["slot_topology"])] for template in templates}),
            "exact_channel_signatures": joined({str(template["exact_channel_signature"]) for template in templates}),
            "channel_shapes": joined({str(template["channel_shape"]) for template in templates}),
            "function_channel_count": min(function_counts),
            "learned_slot_counts": joined({str(template["learned_slot_count"]) for template in templates}),
            "source_count": len(group),
            "content_class_count": len(classes),
            "content_classes": joined(classes),
            "page_count": len(pages),
            "physical_pages": joined(pages),
            "source_surfaces": joined({str(label["surface"]) for label in labels_in_group}),
            "recipe_support_tiers": joined({str(entry["support"]["recipe_support_tier"]) for entry in group}),
            "old_carrier_source_count": sum(str(entry["support"]["recipe_support_tier"]) in OLD_CARRIER_TIERS for entry in group),
            "familiarity_state": state,
            "familiarity_rank": rank,
        })

    component_rows: list[dict[str, object]] = []
    for key in sorted(component_groups):
        group = component_groups[key]
        templates = [entry["template"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        surface_templates = {str(template["surface_template"]) for template in templates}
        classes = {str(label["content_class"]) for label in labels_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        component_rows.append({
            "component_template_id": component_ids[key],
            "component_template": key,
            "template_modes": joined({str(entry["assignment_mode"]) for entry in group}),
            "meaning_template_de": joined({str(template["meaning_template_de"]) for template in templates}),
            "surface_template_count": len(surface_templates),
            "surface_template_ids": joined({surface_ids[value] for value in surface_templates}),
            "surface_templates": joined(surface_templates),
            "alternate_surface_rendering": "YES" if len(surface_templates) > 1 else "NO",
            "topology_ids": joined({topology_ids[str(template["slot_topology"])] for template in templates}),
            "source_count": len(group),
            "content_class_count": len(classes),
            "content_classes": joined(classes),
            "page_count": len(pages),
            "physical_pages": joined(pages),
            "source_surfaces": joined({str(label["surface"]) for label in labels_in_group}),
            "recipe_support_tiers": joined({str(entry["support"]["recipe_support_tier"]) for entry in group}),
        })

    topology_rows: list[dict[str, object]] = []
    for key in sorted(topology_groups):
        group = topology_groups[key]
        templates = [entry["template"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        classes = {str(label["content_class"]) for label in labels_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        topology_rows.append({
            "topology_id": topology_ids[key],
            "slot_topology": key,
            "template_modes": joined({str(entry["assignment_mode"]) for entry in group}),
            "surface_template_count": len({str(template["surface_template"]) for template in templates}),
            "component_template_count": len({str(template["component_template"]) for template in templates}),
            "source_count": len(group),
            "content_class_count": len(classes),
            "content_classes": joined(classes),
            "page_count": len(pages),
            "physical_pages": joined(pages),
            "source_surfaces": joined({str(label["surface"]) for label in labels_in_group}),
            "recurrent": "YES" if len(group) > 1 else "NO",
        })

    package_sources = {
        "ykyd": ("GDT463", ykyd_evidence["target_id"], ykyd_evidence["selected_surface_segmentation"], ykyd_evidence["selected_function_recipe"], ykyd_evidence["selected_literal_de"], "GENERAL_READER_RECOVERS_YKY_BUT_FINAL_D_BELONGS_TO_THE_EXACT_YKY_PLUS_D_PACKAGE"),
        "yddy": ("GDT464", yddy_evidence["target_id"], yddy_evidence["selected_surface_segmentation"], yddy_evidence["selected_function_recipe"], yddy_evidence["selected_literal_de"], "OVERLAPPING_Y_PLUS_D_PLUS_DY_ARMS_ARE_AN_EXACT_WHOLE_PACKAGE_NOT_FREE_DIRECTIONAL_CHANNELS"),
    }
    package_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(exact_package_surfaces, start=1):
        label = label_map[surface]
        cold = cold_map[surface]
        experiment, evidence_id, segmentation, recipe, reading, reason = package_sources[surface]
        package_rows.append({
            "exact_package_card_id": f"G472-X{ordinal:02d}",
            "surface": surface,
            "content_class": label["content_class"],
            "physical_page": label["physical_page"],
            "source_experiment": experiment,
            "source_evidence_id": evidence_id,
            "exact_segmentation": segmentation,
            "exact_recipe": recipe,
            "exact_reading_de": reading,
            "cold_route": cold["route"],
            "cold_recipe": cold["ordered_recipe_trace"],
            "cold_known_character_count": cold["known_function_character_count"],
            "dependency_reason": reason,
            "transferable": "NO",
            "reader_policy": "EXACT_SURFACE_ONLY__NEVER_GENERATE_OR_COMPONENT_MATCH",
        })

    surface_map = {row["surface_template"]: row for row in surface_rows}
    package_map = {row["surface"]: row for row in package_rows}
    entry_map = {entry["label"]["surface"]: entry for entry in entries}
    assignment_rows: list[dict[str, object]] = []
    for ordinal, label in enumerate(labels, start=1):
        if label["surface"] in package_map:
            package = package_map[label["surface"]]
            assignment_mode = "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD"
            transferable = "NO"
            complete_template_id = package["exact_package_card_id"]
            surface_id = component_id = topology_id = "NONE"
            surface_template = f"EXACT_PACKAGE[{label['surface']}]"
            component_template = label["ordered_function_recipe_trace"]
            meaning_template = label["revised_short_default_de"]
            topology = "EXACT_PACKAGE_ONLY"
            state, rank = "EXACT_PACKAGE_ONLY", 0
            cold = cold_map[label["surface"]]
            dependency = package["dependency_reason"]
        else:
            entry = entry_map[label["surface"]]
            template = entry["template"]
            surface_row = surface_map[str(template["surface_template"])]
            assignment_mode = entry["assignment_mode"]
            transferable = "YES"
            complete_template_id = surface_row["surface_template_id"]
            surface_id = surface_row["surface_template_id"]
            component_id = component_ids[str(template["component_template"])]
            topology_id = topology_ids[str(template["slot_topology"])]
            surface_template = template["surface_template"]
            component_template = template["component_template"]
            meaning_template = template["meaning_template_de"]
            topology = template["slot_topology"]
            state, rank = surface_row["familiarity_state"], int(surface_row["familiarity_rank"])
            cold = entry["cold"]
            dependency = "NONE"
        assignment_rows.append({
            "complete_assignment_id": f"G472-A{ordinal:03d}",
            "label_id": label["gdt466_label_id"],
            "source_event_id": label["source_event_id"],
            "physical_page": label["physical_page"],
            "locus": label["locus"],
            "surface": label["surface"],
            "content_class": label["content_class"],
            "gdt466_hybrid_status": label["gdt466_hybrid_status"],
            "assignment_mode": assignment_mode,
            "transferable": transferable,
            "complete_template_id": complete_template_id,
            "surface_template_id": surface_id,
            "component_template_id": component_id,
            "topology_id": topology_id,
            "surface_template": surface_template,
            "component_template": component_template,
            "meaning_template_de": meaning_template,
            "slot_topology": topology,
            "source_recipe": label["ordered_function_recipe_trace"],
            "source_reading_de": label["revised_short_default_de"],
            "cold_route": cold["route"],
            "cold_recipe": cold["ordered_recipe_trace"],
            "template_familiarity_state": state,
            "template_familiarity_rank": rank,
            "runtime_exact_label_rank": 0,
            "exact_package_dependency": dependency,
        })

    write_tsv(OUT / "gdt472_18_full_formula_cold_replay.tsv", full_replay_rows)
    write_tsv(OUT / "gdt472_107_complete_template_assignments.tsv", assignment_rows)
    write_tsv(OUT / "gdt472_87_transferable_surface_templates.tsv", surface_rows)
    write_tsv(OUT / "gdt472_85_transferable_component_templates.tsv", component_rows)
    write_tsv(OUT / "gdt472_20_transferable_topologies.tsv", topology_rows)
    write_tsv(OUT / "gdt472_2_exact_package_cards.tsv", package_rows)
    write_tsv(OUT / "gdt472_complete_ranked_address_item_template.tsv", [], WORKSHEET_FIELDS + EMPIRICAL_FIELDS + COMPLETE_FIELDS)

    contract = {
        "status": "COMPLETE_107_LABEL_TEMPLATE_DICTIONARY_READY",
        "known_label_count": 107,
        "learned_slot_label_count": 89,
        "general_zero_name_formula_count": 16,
        "exact_package_only_count": 2,
        "transferable_surface_template_count": 87,
        "transferable_component_template_count": 85,
        "transferable_topology_count": 20,
        "exact_package_cards": [row["surface"] for row in package_rows],
        "exact_package_policy": "Exact identity may replay the whole package; no unseen surface may inherit it through component or topology matching.",
        "reader_command": "python3 experiments/yolo/gdt472_complete_address_template_dictionary/src/prepare_complete_future_address.py SURFACE CONTENT_CLASS [metadata options]",
        "page_slots": 4,
        "page_slot_state": "UNRELEASED",
        "claim_boundary": "The dictionary ranks an already supplied address and gives an owner-bound default; it predicts no surface, occurrence, object identity, plaintext, language, or confirmed lexeme.",
    }
    (OUT / "gdt472_complete_dictionary_contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    surface_states = Counter(str(row["familiarity_state"]) for row in surface_rows)
    assignment_modes = Counter(str(row["assignment_mode"]) for row in assignment_rows)
    recurrent_components = [row for row in component_rows if int(row["source_count"]) > 1]
    recurrent_topologies = [row for row in topology_rows if row["recurrent"] == "YES"]
    result = {
        "status": "ALL_107_LABELS_HAVE_COMPLETE_TEMPLATE_ASSIGNMENTS__TWO_EXACT_PACKAGES_REMAIN_NONTRANSFERABLE",
        "full_formula_count": len(full_replay_rows),
        "general_zero_name_formula_count": len(general_full_surfaces),
        "exact_package_only_formula_count": len(package_rows),
        "full_formula_replay_pass_count": sum(row["replay_pass"] == "YES" for row in full_replay_rows),
        "complete_assignment_count": len(assignment_rows),
        "assignment_mode_counts": dict(sorted(assignment_modes.items())),
        "transferable_assignment_count": sum(row["transferable"] == "YES" for row in assignment_rows),
        "nontransferable_assignment_count": sum(row["transferable"] == "NO" for row in assignment_rows),
        "transferable_surface_template_count": len(surface_rows),
        "surface_template_state_counts": dict(sorted(surface_states.items())),
        "recurrent_surface_template_count": sum(int(row["source_count"]) > 1 for row in surface_rows),
        "recurrent_surface_template_source_count": sum(int(row["source_count"]) for row in surface_rows if int(row["source_count"]) > 1),
        "transferable_component_template_count": len(component_rows),
        "recurrent_component_template_count": len(recurrent_components),
        "recurrent_component_template_source_count": sum(int(row["source_count"]) for row in recurrent_components),
        "transferable_topology_count": len(topology_rows),
        "recurrent_topology_count": len(recurrent_topologies),
        "recurrent_topology_source_count": sum(int(row["source_count"]) for row in recurrent_topologies),
        "future_page_slots": 4,
        "released_page_slots": 0,
        "new_pages": 0,
        "new_channels": 0,
        "new_component_meanings": 0,
        "new_surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt472_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
