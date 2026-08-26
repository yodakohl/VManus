#!/usr/bin/env python3
"""Build the GDT471 empirical learned-slot address phrasebook."""

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
BASE = ROOT / "experiments/yolo/gdt471_empirical_address_shell_phrasebook"
OUT = BASE / "artifacts"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G470 = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(G470 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, matching_families, read_tsv, select_function_channels  # noqa: E402
from worksheet_lib import WORKSHEET_FIELDS  # noqa: E402
from template_lib import EMPIRICAL_FIELDS, attach_familiarity, derive_template  # noqa: E402


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
    probes = read_tsv(G466 / "artifacts/gdt466_89_unseen_core_insertion_probes.tsv")
    supported_replay = read_tsv(G470 / "artifacts/gdt470_89_supported_unseen_core_replay.tsv")
    label_map = {row["surface"]: row for row in labels}
    support_map = {row["source_probe_id"]: row for row in supported_replay}

    entries: list[dict[str, object]] = []
    for probe in probes:
        label = label_map[probe["source_surface"]]
        template = derive_template(probe["source_surface"], rules, select_function_channels)
        cold = intake(probe["source_surface"], probe["content_class"], rules, families, {})
        entries.append({
            "probe": probe,
            "label": label,
            "template": template,
            "cold": cold,
            "support": support_map[probe["probe_id"]],
        })

    surface_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    component_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    topology_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        template = entry["template"]
        surface_groups[str(template["surface_template"])].append(entry)
        component_groups[str(template["component_template"])].append(entry)
        topology_groups[str(template["slot_topology"])].append(entry)

    surface_ids = {key: f"G471-T{ordinal:03d}" for ordinal, key in enumerate(sorted(surface_groups), start=1)}
    component_ids = {key: f"G471-C{ordinal:03d}" for ordinal, key in enumerate(sorted(component_groups), start=1)}
    topology_ids = {key: f"G471-P{ordinal:02d}" for ordinal, key in enumerate(sorted(topology_groups), start=1)}

    surface_rows: list[dict[str, object]] = []
    for key in sorted(surface_groups):
        group = surface_groups[key]
        templates = [entry["template"] for entry in group]
        probes_in_group = [entry["probe"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        function_counts = {int(template["function_channel_count"]) for template in templates}
        classes = {str(probe["content_class"]) for probe in probes_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        state, rank = familiarity_for_group(len(group), len(classes), len(pages), min(function_counts))
        surface_rows.append({
            "surface_template_id": surface_ids[key],
            "surface_template": key,
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
            "source_surfaces": joined({str(probe["source_surface"]) for probe in probes_in_group}),
            "recipe_support_tiers": joined({str(entry["support"]["observed_recipe_support_tier"]) for entry in group}),
            "old_carrier_source_count": sum(
                str(entry["support"]["observed_recipe_support_tier"])
                in {"RUNNING_EXACT_RECIPE", "ADDRESS_FULL_FORMULA_ONLY", "ADDRESS_HYBRID_SHELL_ONLY"}
                for entry in group
            ),
            "familiarity_state": state,
            "familiarity_rank": rank,
        })

    component_rows: list[dict[str, object]] = []
    for key in sorted(component_groups):
        group = component_groups[key]
        templates = [entry["template"] for entry in group]
        probes_in_group = [entry["probe"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        surface_template_set = {str(template["surface_template"]) for template in templates}
        classes = {str(probe["content_class"]) for probe in probes_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        component_rows.append({
            "component_template_id": component_ids[key],
            "component_template": key,
            "meaning_template_de": joined({str(template["meaning_template_de"]) for template in templates}),
            "surface_template_count": len(surface_template_set),
            "surface_template_ids": joined({surface_ids[value] for value in surface_template_set}),
            "surface_templates": joined(surface_template_set),
            "alternate_surface_rendering": "YES" if len(surface_template_set) > 1 else "NO",
            "topology_ids": joined({topology_ids[str(template["slot_topology"])] for template in templates}),
            "source_count": len(group),
            "content_class_count": len(classes),
            "content_classes": joined(classes),
            "page_count": len(pages),
            "physical_pages": joined(pages),
            "source_surfaces": joined({str(probe["source_surface"]) for probe in probes_in_group}),
            "recipe_support_tiers": joined({str(entry["support"]["observed_recipe_support_tier"]) for entry in group}),
        })

    topology_rows: list[dict[str, object]] = []
    for key in sorted(topology_groups):
        group = topology_groups[key]
        templates = [entry["template"] for entry in group]
        probes_in_group = [entry["probe"] for entry in group]
        labels_in_group = [entry["label"] for entry in group]
        classes = {str(probe["content_class"]) for probe in probes_in_group}
        pages = {str(label["physical_page"]) for label in labels_in_group}
        topology_rows.append({
            "topology_id": topology_ids[key],
            "slot_topology": key,
            "surface_template_count": len({str(template["surface_template"]) for template in templates}),
            "component_template_count": len({str(template["component_template"]) for template in templates}),
            "source_count": len(group),
            "content_class_count": len(classes),
            "content_classes": joined(classes),
            "page_count": len(pages),
            "physical_pages": joined(pages),
            "source_surfaces": joined({str(probe["source_surface"]) for probe in probes_in_group}),
            "recurrent": "YES" if len(group) > 1 else "NO",
        })

    surface_map = {row["surface_template"]: row for row in surface_rows}
    component_map = {row["component_template"]: row for row in component_rows}
    topology_map = {row["slot_topology"]: row for row in topology_rows}

    assignment_rows: list[dict[str, object]] = []
    mutation_rows: list[dict[str, object]] = []
    for ordinal, entry in enumerate(entries, start=1):
        probe = entry["probe"]
        label = entry["label"]
        source_template = entry["template"]
        source_cold = entry["cold"]
        support = entry["support"]
        surface_row = surface_map[str(source_template["surface_template"])]
        assignment_rows.append({
            "assignment_id": f"G471-A{ordinal:03d}",
            "source_probe_id": probe["probe_id"],
            "source_label_id": label["gdt466_label_id"],
            "source_event_id": label["source_event_id"],
            "physical_page": label["physical_page"],
            "locus": label["locus"],
            "source_surface": probe["source_surface"],
            "content_class": probe["content_class"],
            "surface_template_id": surface_row["surface_template_id"],
            "surface_template": source_template["surface_template"],
            "component_template_id": component_ids[str(source_template["component_template"])],
            "component_template": source_template["component_template"],
            "meaning_template_de": source_template["meaning_template_de"],
            "topology_id": topology_ids[str(source_template["slot_topology"])],
            "slot_topology": source_template["slot_topology"],
            "exact_channel_signature": source_template["exact_channel_signature"],
            "channel_shape": source_template["channel_shape"],
            "function_channel_count": source_template["function_channel_count"],
            "learned_slot_count": source_template["learned_slot_count"],
            "learned_span_trace": source_template["learned_span_trace"],
            "cold_route": source_cold["route"],
            "owner_family_markers": source_cold["family_markers"],
            "recipe_support_tier": support["observed_recipe_support_tier"],
            "familiarity_state": surface_row["familiarity_state"],
            "familiarity_rank": surface_row["familiarity_rank"],
        })

        mutated_template = derive_template(probe["synthetic_unseen_surface"], rules, select_function_channels)
        mutated_cold = intake(probe["synthetic_unseen_surface"], probe["content_class"], rules, families, {})
        empirical = attach_familiarity(mutated_cold, mutated_template, surface_map, component_map, topology_map)
        template_stable = (
            source_template["surface_template"] == mutated_template["surface_template"]
            and source_template["component_template"] == mutated_template["component_template"]
            and source_template["meaning_template_de"] == mutated_template["meaning_template_de"]
            and source_template["slot_topology"] == mutated_template["slot_topology"]
            and source_template["exact_channel_signature"] == mutated_template["exact_channel_signature"]
        )
        mutation_rows.append({
            "replay_id": f"G471-M{ordinal:03d}",
            "source_probe_id": probe["probe_id"],
            "source_surface": probe["source_surface"],
            "synthetic_unseen_surface": probe["synthetic_unseen_surface"],
            "content_class": probe["content_class"],
            "source_surface_template": source_template["surface_template"],
            "mutated_surface_template": mutated_template["surface_template"],
            "source_component_template": source_template["component_template"],
            "mutated_component_template": mutated_template["component_template"],
            "source_slot_topology": source_template["slot_topology"],
            "mutated_slot_topology": mutated_template["slot_topology"],
            "matched_surface_template_id": empirical["empirical_surface_template_id"],
            "familiarity_state": empirical["empirical_familiarity_state"],
            "familiarity_rank": empirical["empirical_familiarity_rank"],
            "source_route": source_cold["route"],
            "mutated_route": mutated_cold["route"],
            "route_stable": "YES" if source_cold["route"] == mutated_cold["route"] else "NO",
            "source_family_markers": source_cold["family_markers"],
            "mutated_family_markers": mutated_cold["family_markers"],
            "family_marker_trace_stable": "YES" if source_cold["family_markers"] == mutated_cold["family_markers"] else "NO",
            "source_has_family_marker": "YES" if source_cold["family_markers"] != "NONE" else "NO",
            "mutation_retains_any_family_marker": "YES" if mutated_cold["family_markers"] != "NONE" else "NO",
            "function_template_stable": "YES" if template_stable else "NO",
            "gdt470_supported_replay_pass": support["replay_pass"],
            "replay_pass": "YES" if template_stable and support["replay_pass"] == "YES" else "NO",
        })

    family_rows: list[dict[str, object]] = []
    for family in families:
        stem = family["surface_stem"]
        content_class = family["content_class"]
        relevant = [probe for probe in probes if probe["content_class"] == content_class]
        source_match = [probe for probe in relevant if stem in probe["source_surface"]]
        mutation_match = [probe for probe in relevant if stem in probe["synthetic_unseen_surface"]]
        retained = [probe for probe in source_match if stem in probe["synthetic_unseen_surface"]]
        gained = [probe for probe in mutation_match if stem not in probe["source_surface"]]
        family_rows.append({
            "family_id": family["family_id"],
            "surface_stem": stem,
            "working_family_value_de": family["working_family_value_de"],
            "content_class": content_class,
            "source_probe_match_count": len(source_match),
            "mutation_probe_match_count": len(mutation_match),
            "paired_retained_count": len(retained),
            "paired_lost_count": len(source_match) - len(retained),
            "paired_gained_count": len(gained),
            "source_surfaces": joined({probe["source_surface"] for probe in source_match}),
            "lost_source_surfaces": joined({probe["source_surface"] for probe in source_match if stem not in probe["synthetic_unseen_surface"]}),
            "policy": "OWNER_FAMILY_MARKER_ONLY__NOT_A_FUNCTION_TEMPLATE",
        })

    write_tsv(OUT / "gdt471_89_template_assignments.tsv", assignment_rows)
    write_tsv(OUT / "gdt471_71_empirical_surface_templates.tsv", surface_rows)
    write_tsv(OUT / "gdt471_69_component_templates.tsv", component_rows)
    write_tsv(OUT / "gdt471_16_slot_topologies.tsv", topology_rows)
    write_tsv(OUT / "gdt471_89_mutation_template_replay.tsv", mutation_rows)
    write_tsv(OUT / "gdt471_18_family_marker_core_change_sensitivity.tsv", family_rows)
    write_tsv(OUT / "gdt471_ranked_address_item_template.tsv", [], WORKSHEET_FIELDS + EMPIRICAL_FIELDS)

    contract = {
        "status": "EMPIRICAL_ADDRESS_SHELL_PHRASEBOOK_READY",
        "familiarity_order": [
            {"rank": 0, "state": "EXACT_LABEL_CARD"},
            {"rank": 1, "state": "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE"},
            {"rank": 2, "state": "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE"},
            {"rank": 3, "state": "RECURRENT_EXACT_FUNCTION_TEMPLATE"},
            {"rank": 4, "state": "SINGLETON_EXACT_FUNCTION_TEMPLATE"},
            {"rank": 5, "state": "KNOWN_COMPONENT_TEMPLATE_ALTERNATE_RENDERING"},
            {"rank": 6, "state": "KNOWN_SLOT_TOPOLOGY_ONLY"},
            {"rank": 7, "state": "WHOLE_NAME_DEFAULT"},
            {"rank": 8, "state": "UNSEEN_SLOT_TOPOLOGY"},
        ],
        "template_derivation": "Replace only uncovered spans with ordered NAME slots; preserve every selected channel stem and its order.",
        "family_marker_policy": "Owner-family substrings remain a separate lexical clue and never increase function-template familiarity.",
        "reader_command": "python3 experiments/yolo/gdt471_empirical_address_shell_phrasebook/src/prepare_ranked_future_address.py SURFACE CONTENT_CLASS [metadata options]",
        "page_slots": 4,
        "page_slot_state": "UNRELEASED",
        "claim_boundary": "Familiarity ranks already supplied forms; it predicts no spelling, occurrence, individual name, plaintext, language, or confirmed lexeme.",
    }
    (OUT / "gdt471_familiarity_contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    surface_states = Counter(str(row["familiarity_state"]) for row in surface_rows)
    assignment_states = Counter(str(row["familiarity_state"]) for row in assignment_rows)
    recurrent_components = [row for row in component_rows if int(row["source_count"]) > 1]
    alternate_components = [row for row in component_rows if row["alternate_surface_rendering"] == "YES"]
    recurrent_topologies = [row for row in topology_rows if row["recurrent"] == "YES"]
    result = {
        "status": "EMPIRICAL_FUNCTION_TEMPLATES_READY__FAMILY_MARKERS_REMAIN_CORE_SENSITIVE",
        "source_pattern_count": len(entries),
        "surface_template_count": len(surface_rows),
        "surface_template_state_counts": dict(sorted(surface_states.items())),
        "source_assignment_state_counts": dict(sorted(assignment_states.items())),
        "recurrent_surface_template_count": sum(int(row["source_count"]) > 1 for row in surface_rows),
        "recurrent_surface_template_source_count": sum(int(row["source_count"]) for row in surface_rows if int(row["source_count"]) > 1),
        "cross_owner_function_template_count": surface_states["CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE"],
        "cross_owner_function_template_source_count": assignment_states["CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE"],
        "cross_page_function_template_count": sum(int(row["function_channel_count"]) > 0 and int(row["page_count"]) > 1 for row in surface_rows),
        "cross_page_function_template_source_count": sum(int(row["source_count"]) for row in surface_rows if int(row["function_channel_count"]) > 0 and int(row["page_count"]) > 1),
        "component_template_count": len(component_rows),
        "recurrent_component_template_count": len(recurrent_components),
        "recurrent_component_template_source_count": sum(int(row["source_count"]) for row in recurrent_components),
        "alternate_rendering_component_template_count": len(alternate_components),
        "alternate_rendering_component_source_count": sum(int(row["source_count"]) for row in alternate_components),
        "slot_topology_count": len(topology_rows),
        "recurrent_slot_topology_count": len(recurrent_topologies),
        "recurrent_slot_topology_source_count": sum(int(row["source_count"]) for row in recurrent_topologies),
        "mutation_replay_count": len(mutation_rows),
        "mutation_replay_pass_count": sum(row["replay_pass"] == "YES" for row in mutation_rows),
        "function_template_stable_count": sum(row["function_template_stable"] == "YES" for row in mutation_rows),
        "route_stable_count": sum(row["route_stable"] == "YES" for row in mutation_rows),
        "source_family_marker_probe_count": sum(row["source_has_family_marker"] == "YES" for row in mutation_rows),
        "mutation_any_family_marker_probe_count": sum(row["mutation_retains_any_family_marker"] == "YES" for row in mutation_rows),
        "source_family_marker_exact_trace_retained_count": sum(
            row["source_has_family_marker"] == "YES" and row["family_marker_trace_stable"] == "YES"
            for row in mutation_rows
        ),
        "family_marker_trace_stable_count": sum(row["family_marker_trace_stable"] == "YES" for row in mutation_rows),
        "family_marker_trace_changed_count": sum(row["family_marker_trace_stable"] == "NO" for row in mutation_rows),
        "future_page_slots": 4,
        "released_page_slots": 0,
        "new_pages": 0,
        "new_channels": 0,
        "new_component_meanings": 0,
        "new_surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt471_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
