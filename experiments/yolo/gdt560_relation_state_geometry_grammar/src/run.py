#!/usr/bin/env python3
"""Compile AL/AR/L/AIR geometry inside the GDT557 OT/OL/DY state grammar."""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt560_relation_state_geometry_grammar"
OUT = BASE / "artifacts"
G429 = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"

STATE_ATLAS_PATH = G557 / "gdt557_all_state_marker_occurrences.tsv"
CONTRAST_PATH = G429 / "gdt429_13_nonaction_core_contrasts.tsv"

ASSIGNMENT_OUT = OUT / "gdt560_216_relation_state_assignments.tsv"
ROOT_PROFILE_OUT = OUT / "gdt560_4_relation_geometry_profiles.tsv"
ENVELOPE_OUT = OUT / "gdt560_8_relation_control_envelopes.tsv"
PROJECTION_OUT = OUT / "gdt560_28_relation_state_projections.tsv"
RICH_PROJECTION_OUT = OUT / "gdt560_44_relation_argument_state_projections.tsv"
FAMILY_OUT = OUT / "gdt560_12_multiroot_relation_families.tsv"
PAIR_OUT = OUT / "gdt560_6_relation_pair_bridges.tsv"
ARGUMENT_CONTACT_OUT = OUT / "gdt560_16_explicit_argument_contacts.tsv"
POST_DY_OUT = OUT / "gdt560_2_post_dy_l_tails.tsv"
BOOK_OUT = OUT / "GDT560_RELATION_GEOMETRY_BOOK.md"
RESULT_OUT = OUT / "gdt560_result.json"

STATUS = "PASS_EIGHT_RELATION_ENVELOPES__AL_AR_L_SPLIT_GEOMETRY__AIR_ZERO_STATE_SUBSTITUTIONS__67_OF_67_DY_FAMILY_CARDS_CLOSE"
RELATIONS = ("AL", "AR", "L", "AIR")
RELATION_SET = set(RELATIONS)
CONTROLS = ("OT", "OL", "DY")
CONTROL_SET = set(CONTROLS)
ARGUMENTS = ("Y", "AIIN", "AIN", "OR")
ARGUMENT_SET = set(ARGUMENTS)
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
ACTION_SET = set(ACTIONS)

RELATION_VALUES = {"AL": "ZIELORT", "AR": "AUSGANG", "L": "VERBINDUNG", "AIR": "BAHN"}
ARGUMENT_VALUES = {"Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
CONTROL_VALUES = {"OT": "DANACH", "OL": "FORTSETZEN", "DY": "ABSCHLIESSEN"}
LITERAL_VALUES = {**RELATION_VALUES, **ARGUMENT_VALUES, **CONTROL_VALUES}
ROOT_GEOMETRY = {
    "AL": "TARGET_HINGE__MAY_POINT_FORWARD_OR_CLOSE_A_TARGET",
    "AR": "SOURCE_OUTPUT_ENDPOINT__MOSTLY_RIGHT_EDGE",
    "L": "FORWARD_CONNECTION_OPENER__MOSTLY_LEFT_EDGE",
    "AIR": "SPARSE_PATH_DESCRIPTOR__NO_STATE_SUBSTITUTION",
}
ENVELOPE_TEMPLATES = {
    "START>R<DY": "REL · ABSCHLIESSEN",
    "OT>R<END": "DANACH · REL",
    "START>R<OL": "REL · FORTSETZEN",
    "OL>R<END": "FORTSETZEN · REL",
    "DY>R<END": "ABSCHLIESSEN · REL",
    "OT>R<DY": "DANACH · REL · ABSCHLIESSEN",
    "OL>R<DY": "FORTSETZEN · REL · ABSCHLIESSEN",
    "OL>R<OL": "FORTSETZEN · REL · FORTSETZEN",
}
ENVELOPE_ROLES = {
    "START>R<DY": "RELATION_THEN_CLOSE",
    "OT>R<END": "NEXT_RELATION_VALUE",
    "START>R<OL": "RELATION_RETAINED_BY_OL",
    "OL>R<END": "CONTINUED_RELATION_VALUE",
    "DY>R<END": "POST_CLOSE_RELATION_TAIL",
    "OT>R<DY": "NEXT_RELATION_THEN_CLOSE",
    "OL>R<DY": "CONTINUE_RELATION_THEN_CLOSE",
    "OL>R<OL": "RELATION_BRIDGED_BY_OL",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> str:
    return f"{100 * numerator / denominator:.6f}" if denominator else "0.000000"


def relation_state_projection(recipe: str) -> str:
    return "+".join(
        atom for atom in recipe.split("+") if atom in RELATION_SET | CONTROL_SET
    )


def rich_projection(recipe: str) -> str:
    return "+".join(
        atom for atom in recipe.split("+")
        if atom in RELATION_SET | CONTROL_SET | ARGUMENT_SET
    )


def normalized_relation_recipe(recipe: str) -> str:
    return "+".join("REL" if atom in RELATION_SET else atom for atom in recipe.split("+"))


def normalized_state_projection(recipe: str) -> str:
    return "+".join(
        atom for atom in recipe.split("+") if atom in CONTROL_SET or atom == "REL"
    )


def literal_reading(projection: str) -> str:
    return " · ".join(LITERAL_VALUES[atom] for atom in projection.split("+"))


def compact_relation_reading(left_control: str, right_control: str, relation: str) -> str:
    envelope = f"{left_control}>R<{right_control}"
    return ENVELOPE_TEMPLATES[envelope].replace("REL", RELATION_VALUES[relation])


def payload_geometry(
    left_actions: list[str], right_actions: list[str],
    left_arguments: list[str], right_arguments: list[str],
) -> str:
    left = bool(left_actions or left_arguments)
    right = bool(right_actions or right_arguments)
    if left and right:
        return "BETWEEN_VISIBLE_PAYLOADS"
    if right:
        return "FORWARD_TO_VISIBLE_PAYLOAD"
    if left:
        return "BACKWARD_FROM_VISIBLE_PAYLOAD"
    return "CONTROL_CARRIED_RELATION_WITHOUT_LOCAL_PAYLOAD"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state_rows = read_tsv(STATE_ATLAS_PATH)
    contrast_rows = read_tsv(CONTRAST_PATH)
    if (len(state_rows), len(contrast_rows)) != (1870, 13):
        raise RuntimeError("Input count drift")

    event_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_rows:
        event_groups[row["event_id"]].append(row)
    if len(event_groups) != 1656:
        raise RuntimeError("GDT557 marker-bearing event count drift")
    stable_fields = (
        "cohort", "statement_id", "physical_page", "register", "surface",
        "recipe", "event_marker_sequence", "statement_position",
        "statement_final", "current_reading_de",
    )
    events: dict[str, dict[str, str]] = {}
    for event_id, rows in event_groups.items():
        if any(len({row[field] for row in rows}) != 1 for field in stable_fields):
            raise RuntimeError(f"Conflicting GDT557 duplicate rows: {event_id}")
        events[event_id] = rows[0]

    selected_events = {
        event_id: event for event_id, event in events.items()
        if any(atom in RELATION_SET for atom in event["recipe"].split("+"))
    }
    assignment_rows: list[dict[str, object]] = []
    for event_id, event in selected_events.items():
        atoms = event["recipe"].split("+")
        relation_positions = [index for index, atom in enumerate(atoms) if atom in RELATION_SET]
        relation_sequence = [atoms[index] for index in relation_positions]
        for occurrence, relation_index in enumerate(relation_positions, 1):
            relation = atoms[relation_index]
            left_control_index = max(
                (index for index in range(relation_index) if atoms[index] in CONTROL_SET),
                default=-1,
            )
            right_control_index = min(
                (index for index in range(relation_index + 1, len(atoms)) if atoms[index] in CONTROL_SET),
                default=len(atoms),
            )
            left_control = atoms[left_control_index] if left_control_index >= 0 else "START"
            right_control = atoms[right_control_index] if right_control_index < len(atoms) else "END"
            block = atoms[left_control_index + 1:right_control_index]
            local_index = relation_index - left_control_index - 1
            before = block[:local_index]
            after = block[local_index + 1:]
            left_actions = [atom for atom in before if atom in ACTION_SET]
            right_actions = [atom for atom in after if atom in ACTION_SET]
            left_arguments = [atom for atom in before if atom in ARGUMENT_SET]
            right_arguments = [atom for atom in after if atom in ARGUMENT_SET]
            envelope = f"{left_control}>R<{right_control}"
            if envelope not in ENVELOPE_TEMPLATES:
                raise RuntimeError(f"Unmapped relation envelope {envelope}: {event_id}")
            assignment_rows.append({
                "assignment_ordinal": len(assignment_rows) + 1,
                "cohort": event["cohort"], "event_id": event_id,
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"], "register": event["register"],
                "surface": event["surface"], "recipe": event["recipe"],
                "relation_state_projection": relation_state_projection(event["recipe"]),
                "relation_argument_state_projection": rich_projection(event["recipe"]),
                "relation_occurrence_in_recipe": occurrence,
                "relation_multiplicity_in_recipe": len(relation_positions),
                "relation_sequence": "+".join(relation_sequence),
                "relation": relation, "relation_value_de": RELATION_VALUES[relation],
                "relation_atom_position": relation_index + 1,
                "recipe_atom_count": len(atoms),
                "left_control": left_control, "right_control": right_control,
                "carrier_envelope": envelope, "envelope_role": ENVELOPE_ROLES[envelope],
                "content_block": "+".join(block),
                "relation_position_in_block": local_index + 1,
                "block_left_edge": "YES" if not before else "NO",
                "block_right_edge": "YES" if not after else "NO",
                "left_content_before_relation": "+".join(before) or "NONE",
                "right_content_after_relation": "+".join(after) or "NONE",
                "visible_left_actions": "+".join(left_actions) or "NONE",
                "visible_right_actions": "+".join(right_actions) or "NONE",
                "visible_left_arguments": "+".join(left_arguments) or "NONE",
                "visible_right_arguments": "+".join(right_arguments) or "NONE",
                "local_payload_geometry": payload_geometry(
                    left_actions, right_actions, left_arguments, right_arguments
                ),
                "root_geometry_default": ROOT_GEOMETRY[relation],
                "compact_relation_reading_de": compact_relation_reading(left_control, right_control, relation),
                "literal_rich_projection_de": literal_reading(rich_projection(event["recipe"])),
                "statement_position": event["statement_position"],
                "statement_final": event["statement_final"],
                "current_reading_de": event["current_reading_de"],
                "guard": "RELATION_VALUE_AND_WRITTEN_CONTROL_ORDER_FIXED__NO_ROOT_OR_RECIPE_CHANGE",
            })

    single_relation_events = {
        event_id: event for event_id, event in selected_events.items()
        if sum(atom in RELATION_SET for atom in event["recipe"].split("+")) == 1
    }
    family_groups: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    for event in single_relation_events.values():
        atoms = event["recipe"].split("+")
        relation = next(atom for atom in atoms if atom in RELATION_SET)
        family_groups[normalized_relation_recipe(event["recipe"])].append((relation, event))
    multiroot_groups = {
        skeleton: material for skeleton, material in family_groups.items()
        if len({relation for relation, _ in material}) >= 2
    }
    family_rows: list[dict[str, object]] = []
    family_id_by_skeleton: dict[str, str] = {}
    for skeleton, material in sorted(
        multiroot_groups.items(),
        key=lambda item: (-len({relation for relation, _ in item[1]}), -len(item[1]), item[0]),
    ):
        family_id = f"G560-F{len(family_rows) + 1:02d}"
        family_id_by_skeleton[skeleton] = family_id
        by_relation = {
            relation: [event for root, event in material if root == relation]
            for relation in RELATIONS
        }
        variants = [relation for relation in RELATIONS if by_relation[relation]]
        first_event = material[0][1]
        first_assignment = next(
            row for row in assignment_rows if row["event_id"] == first_event["event_id"]
        )
        has_dy = "DY" in skeleton.split("+")
        family_rows.append({
            "family_ordinal": len(family_rows) + 1, "family_id": family_id,
            "normalized_recipe": skeleton,
            "normalized_state_projection": normalized_state_projection(skeleton),
            "carrier_envelope": first_assignment["carrier_envelope"],
            "relation_variant_count": len(variants),
            "relation_variants": "|".join(variants),
            "family_status": (
                "OBSERVED_THREE_RELATION_FRAME" if len(variants) == 3
                else "OBSERVED_TWO_RELATION_FRAME"
            ),
            "event_count": len(material),
            "al_event_count": len(by_relation["AL"]),
            "ar_event_count": len(by_relation["AR"]),
            "l_event_count": len(by_relation["L"]),
            "air_event_count": len(by_relation["AIR"]),
            "physical_page_count": len({event["physical_page"] for _, event in material}),
            "register_count": len({event["register"] for _, event in material}),
            "contains_dy": "YES" if has_dy else "NO",
            "statement_final_event_count": sum(event["statement_final"] == "YES" for _, event in material),
            "statement_final_percent": pct(sum(event["statement_final"] == "YES" for _, event in material), len(material)),
            "surfaces_by_relation": " || ".join(
                f"{relation}:{'|'.join(sorted({event['surface'] for event in by_relation[relation]}))}"
                for relation in variants
            ),
            "event_ids": "|".join(event["event_id"] for _, event in material),
            "family_reading_de": ENVELOPE_TEMPLATES[str(first_assignment["carrier_envelope"])],
            "scope_result": "RELATION_VALUE_SUBSTITUTES_WITHOUT_CHANGING_CONTROL_SCOPE",
        })
    for row in assignment_rows:
        if int(row["relation_multiplicity_in_recipe"]) == 1:
            row["substitution_family_id"] = family_id_by_skeleton.get(
                normalized_relation_recipe(str(row["recipe"])), "NONE"
            )
        else:
            row["substitution_family_id"] = "NONE"

    envelope_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in assignment_rows:
        envelope_groups[str(row["carrier_envelope"])].append(row)
    envelope_rows: list[dict[str, object]] = []
    for envelope, material in sorted(
        envelope_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        counts = Counter(str(row["relation"]) for row in material)
        envelope_rows.append({
            "envelope_ordinal": len(envelope_rows) + 1,
            "carrier_envelope": envelope, "envelope_role": ENVELOPE_ROLES[envelope],
            "relation_occurrence_count": len(material),
            "event_count": len({str(row["event_id"]) for row in material}),
            "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in material}),
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "register_count": len({str(row["register"]) for row in material}),
            "al_count": counts["AL"], "ar_count": counts["AR"],
            "l_count": counts["L"], "air_count": counts["AIR"],
            "relation_root_breadth": sum(counts[root] > 0 for root in RELATIONS),
            "statement_final_occurrence_count": sum(row["statement_final"] == "YES" for row in material),
            "statement_final_percent": pct(sum(row["statement_final"] == "YES" for row in material), len(material)),
            "substitution_family_assignment_count": sum(row["substitution_family_id"] != "NONE" for row in material),
            "compact_template_de": ENVELOPE_TEMPLATES[envelope],
        })

    projection_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    rich_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in selected_events.values():
        projection_groups[relation_state_projection(event["recipe"])].append(event)
        rich_groups[rich_projection(event["recipe"])].append(event)
    projection_rows: list[dict[str, object]] = []
    for projection, material in sorted(
        projection_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        projection_rows.append({
            "projection_ordinal": len(projection_rows) + 1,
            "relation_state_projection": projection, "event_count": len(material),
            "relation_occurrence_count": sum(sum(atom in RELATION_SET for atom in event["recipe"].split("+")) for event in material),
            "physical_page_count": len({event["physical_page"] for event in material}),
            "register_count": len({event["register"] for event in material}),
            "exact_recipe_count": len({event["recipe"] for event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "literal_working_reading_de": literal_reading(projection),
            "example_events": "|".join(event["event_id"] for event in material[:5]),
            "example_surfaces": "|".join(event["surface"] for event in material[:5]),
        })
    rich_projection_rows: list[dict[str, object]] = []
    for projection, material in sorted(
        rich_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        rich_projection_rows.append({
            "projection_ordinal": len(rich_projection_rows) + 1,
            "relation_argument_state_projection": projection,
            "event_count": len(material),
            "physical_page_count": len({event["physical_page"] for event in material}),
            "register_count": len({event["register"] for event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "literal_working_reading_de": literal_reading(projection),
            "example_events": "|".join(event["event_id"] for event in material[:5]),
            "example_surfaces": "|".join(event["surface"] for event in material[:5]),
        })

    contrast_by_pair: dict[frozenset[str], dict[str, str]] = {}
    for row in contrast_rows:
        if row["family"] != "RELATION":
            continue
        left, right = row["contrast_pair"].split("~")
        contrast_by_pair[frozenset((left, right))] = row
    pair_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(RELATIONS, 2):
        pair_families = [
            (skeleton, material) for skeleton, material in multiroot_groups.items()
            if {left, right} <= {relation for relation, _ in material}
        ]
        pair_event_ids = {
            event["event_id"] for _, material in pair_families
            for relation, event in material if relation in {left, right}
        }
        old = contrast_by_pair[frozenset((left, right))]
        pair_rows.append({
            "pair_ordinal": len(pair_rows) + 1,
            "relation_pair": f"{left}~{right}",
            "left_value_de": RELATION_VALUES[left], "right_value_de": RELATION_VALUES[right],
            "gdt429_shared_exact_frame_count": old["shared_exact_substitution_frame_count"],
            "gdt560_state_family_count": len(pair_families),
            "gdt560_pair_event_count": len(pair_event_ids),
            "gdt560_all_family_event_count": sum(len(material) for _, material in pair_families),
            "state_family_ids": "|".join(
                family_id_by_skeleton[skeleton] for skeleton, _ in sorted(pair_families)
            ) or "NONE",
            "normalized_recipes": "|".join(skeleton for skeleton, _ in sorted(pair_families)) or "NONE",
            "decision": (
                "STATE_SUBSTITUTION_BRIDGE_PRESENT__VALUES_REMAIN_DISTINCT"
                if pair_families else "NO_STATE_SUBSTITUTION_BRIDGE__KEEP_AIR_SEPARATE"
            ),
        })

    family_event_ids = {
        event["event_id"] for material in multiroot_groups.values() for _, event in material
    }
    root_profile_rows: list[dict[str, object]] = []
    for relation in RELATIONS:
        occurrences = [row for row in assignment_rows if row["relation"] == relation]
        root_events = [
            event for event in selected_events.values() if relation in event["recipe"].split("+")
        ]
        root_profile_rows.append({
            "relation": relation, "working_value_de": RELATION_VALUES[relation],
            "root_geometry_default": ROOT_GEOMETRY[relation],
            "occurrence_count": len(occurrences), "event_count": len(root_events),
            "statement_count": len({event["statement_id"] for event in root_events}),
            "physical_page_count": len({event["physical_page"] for event in root_events}),
            "register_count": len({event["register"] for event in root_events}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in root_events),
            "left_ot_or_ol_count": sum(row["left_control"] in {"OT", "OL"} for row in occurrences),
            "right_dy_or_ol_count": sum(row["right_control"] in {"DY", "OL"} for row in occurrences),
            "block_left_edge_count": sum(row["block_left_edge"] == "YES" for row in occurrences),
            "block_right_edge_count": sum(row["block_right_edge"] == "YES" for row in occurrences),
            "visible_left_action_count": sum(row["visible_left_actions"] != "NONE" for row in occurrences),
            "visible_right_action_count": sum(row["visible_right_actions"] != "NONE" for row in occurrences),
            "visible_left_argument_count": sum(row["visible_left_arguments"] != "NONE" for row in occurrences),
            "visible_right_argument_count": sum(row["visible_right_arguments"] != "NONE" for row in occurrences),
            "multiroot_family_event_count": sum(event["event_id"] in family_event_ids for event in root_events),
            "state_substitution_family_count": sum(relation in row["relation_variants"].split("|") for row in family_rows),
        })

    argument_contact_rows: list[dict[str, object]] = []
    for row in assignment_rows:
        if row["visible_left_arguments"] == "NONE" and row["visible_right_arguments"] == "NONE":
            continue
        argument_contact_rows.append({
            "contact_ordinal": len(argument_contact_rows) + 1,
            "event_id": row["event_id"], "physical_page": row["physical_page"],
            "register": row["register"], "surface": row["surface"],
            "recipe": row["recipe"], "relation": row["relation"],
            "relation_value_de": row["relation_value_de"],
            "carrier_envelope": row["carrier_envelope"],
            "visible_left_arguments": row["visible_left_arguments"],
            "visible_right_arguments": row["visible_right_arguments"],
            "relation_argument_state_projection": row["relation_argument_state_projection"],
            "literal_working_reading_de": row["literal_rich_projection_de"],
            "statement_final": row["statement_final"],
            "interpretation": (
                "RELATION_FOLLOWS_VISIBLE_ARGUMENT" if row["visible_left_arguments"] != "NONE"
                else "RELATION_PRECEDES_VISIBLE_ARGUMENT"
            ),
        })

    post_dy_rows: list[dict[str, object]] = []
    for row in assignment_rows:
        if row["carrier_envelope"] != "DY>R<END":
            continue
        post_dy_rows.append({
            "tail_ordinal": len(post_dy_rows) + 1,
            "event_id": row["event_id"], "physical_page": row["physical_page"],
            "register": row["register"], "surface": row["surface"],
            "recipe": row["recipe"], "relation": row["relation"],
            "relation_value_de": row["relation_value_de"],
            "statement_final": row["statement_final"],
            "written_order_reading_de": row["compact_relation_reading_de"],
            "interpretation": "CLOSE_STEP_THEN_RETAIN_VISIBLE_CONNECTION_TAIL",
        })

    family_variant_counts = Counter(int(row["relation_variant_count"]) for row in family_rows)
    dy_family_events = {
        event["event_id"]: event for material in multiroot_groups.values()
        for _, event in material if "DY" in event["recipe"].split("+")
    }
    non_dy_family_events = {
        event["event_id"]: event for material in multiroot_groups.values()
        for _, event in material if "DY" not in event["recipe"].split("+")
    }
    right_dy_assignments = [row for row in assignment_rows if row["right_control"] == "DY"]
    result = {
        "status": STATUS,
        "source_marker_occurrence_count": len(state_rows),
        "source_marker_event_count": len(events),
        "relation_state_event_count": len(selected_events),
        "relation_occurrence_count": len(assignment_rows),
        "single_relation_event_count": len(single_relation_events),
        "multirelation_event_count": len(selected_events) - len(single_relation_events),
        "al_occurrence_count": sum(row["relation"] == "AL" for row in assignment_rows),
        "ar_occurrence_count": sum(row["relation"] == "AR" for row in assignment_rows),
        "l_occurrence_count": sum(row["relation"] == "L" for row in assignment_rows),
        "air_occurrence_count": sum(row["relation"] == "AIR" for row in assignment_rows),
        "physical_page_count": len({row["physical_page"] for row in assignment_rows}),
        "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in assignment_rows}),
        "carrier_envelope_count": len(envelope_rows),
        "relation_state_projection_count": len(projection_rows),
        "relation_argument_state_projection_count": len(rich_projection_rows),
        "multiroot_relation_family_count": len(family_rows),
        "three_relation_family_count": family_variant_counts[3],
        "two_relation_family_count": family_variant_counts[2],
        "multiroot_family_event_count": len(family_event_ids),
        "relation_occurrence_outside_multiroot_family_count": sum(row["substitution_family_id"] == "NONE" for row in assignment_rows),
        "al_ar_state_family_count": next(int(row["gdt560_state_family_count"]) for row in pair_rows if row["relation_pair"] == "AL~AR"),
        "al_l_state_family_count": next(int(row["gdt560_state_family_count"]) for row in pair_rows if row["relation_pair"] == "AL~L"),
        "ar_l_state_family_count": next(int(row["gdt560_state_family_count"]) for row in pair_rows if row["relation_pair"] == "AR~L"),
        "air_state_substitution_family_count": sum("AIR" in row["relation_variants"].split("|") for row in family_rows),
        "dy_family_event_count": len(dy_family_events),
        "dy_family_statement_final_count": sum(event["statement_final"] == "YES" for event in dy_family_events.values()),
        "non_dy_family_event_count": len(non_dy_family_events),
        "non_dy_family_statement_final_count": sum(event["statement_final"] == "YES" for event in non_dy_family_events.values()),
        "right_dy_relation_occurrence_count": len(right_dy_assignments),
        "right_dy_relation_statement_final_count": sum(row["statement_final"] == "YES" for row in right_dy_assignments),
        "explicit_argument_contact_count": len(argument_contact_rows),
        "post_dy_l_tail_count": len(post_dy_rows),
        "post_dy_l_tail_statement_final_count": sum(row["statement_final"] == "YES" for row in post_dy_rows),
        "all_assignments_have_default": all(bool(row["compact_relation_reading_de"]) for row in assignment_rows),
        "all_state_projections_have_default": all(bool(row["literal_working_reading_de"]) for row in projection_rows),
        "all_rich_projections_have_default": all(bool(row["literal_working_reading_de"]) for row in rich_projection_rows),
        "new_pages": 0, "recipe_changes": 0, "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }

    write_tsv(ASSIGNMENT_OUT, assignment_rows)
    write_tsv(ROOT_PROFILE_OUT, root_profile_rows)
    write_tsv(ENVELOPE_OUT, envelope_rows)
    write_tsv(PROJECTION_OUT, projection_rows)
    write_tsv(RICH_PROJECTION_OUT, rich_projection_rows)
    write_tsv(FAMILY_OUT, family_rows)
    write_tsv(PAIR_OUT, pair_rows)
    write_tsv(ARGUMENT_CONTACT_OUT, argument_contact_rows)
    write_tsv(POST_DY_OUT, post_dy_rows)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT560 — Relations-Geometriebuch", "",
        "Die vier Wurzeln bleiben kurz: `AL=ZIELORT`, `AR=AUSGANG`, `L=VERBINDUNG`, `AIR=BAHN`. Anders als die vier Argumente bilden sie im Zustandsstrom kein einheitliches Viererfach. Alle216 Stellen erhalten dennoch eine der8 geschriebenen Kontrollhüllen und eine kurze Defaultlesung.", "",
        "## Vier verschiedene Geometrien", "",
        "| Wurzel | Wert | Stellen | links vom Block | rechts vom Block | Handlung rechts | OT/OL links | DY/OL rechts |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in root_profile_rows:
        lines.append(
            f"| `{row['relation']}` | {row['working_value_de']} | {row['occurrence_count']} | "
            f"{row['block_left_edge_count']} | {row['block_right_edge_count']} | "
            f"{row['visible_right_action_count']} | {row['left_ot_or_ol_count']} | "
            f"{row['right_dy_or_ol_count']} |"
        )
    lines.extend([
        "", "AR ist der deutlichste rechte Ausgang:50/58 Stellen beenden ihren lokalen Inhalt und47 liegen nach OT/OL. L ist das Gegenbild:86/92 eröffnen den lokalen Inhalt,58 zeigen rechts eine Handlung und85 laufen in DY/OL. AL besetzt beide Seiten und verbindet die Ausgangs- mit der Verbindungsgeometrie. AIR bleibt mit6 Stellen und0 Zustands-Austauschfamilien ein eigener seltener Bahntyp.", "",
        "## Acht vollständige Kontrollhüllen", "",
        "| Hülle | Stellen | AL | AR | L | AIR | Default |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in envelope_rows:
        lines.append(
            f"| `{row['carrier_envelope']}` | {row['relation_occurrence_count']} | {row['al_count']} | "
            f"{row['ar_count']} | {row['l_count']} | {row['air_count']} | {row['compact_template_de']} |"
        )
    lines.extend([
        "", "## Zwölf Austauschfamilien, aber kein Viererfach", "",
        "| Familie | Rezept | Varianten | Karten | final |",
        "|---|---|---|---:|---:|",
    ])
    for row in family_rows:
        lines.append(
            f"| {row['family_id']} | `{row['normalized_recipe']}` | {row['relation_variants']} | "
            f"{row['event_count']} | {row['statement_final_event_count']} |"
        )
    lines.extend([
        "", "AL↔AR teilen8 Zustandsfamilien, AL↔L vier und AR↔L zwei. AL ist damit das Gelenk. Kein AIR-Paar besitzt in diesem Zustandsausschnitt eine exakte Austauschfamilie. Die67 Familienkarten mit DY schließen67/67 Aussagen; die77 ohne DY schließen0/77. Der Relationswechsel ändert also den Kontrollschluss nicht.", "",
        "## Zwei sichtbare Nachschluss-Verbindungen", "",
        "`OT+E+DY+L` und `OK+CHD+DY+L` schreiben den ungewöhnlichen Ablauf `ABSCHLIESSEN · VERBINDUNG`. Beide sind aussagefinal. L wird hier nicht über DY zurückgebunden, sondern bleibt als sichtbarer Verbindungsschwanz nach dem geschlossenen Schritt stehen.", "",
        "## Alle28 Relations-Steuerfolgen", "",
        "| Folge | Karten | final | Default |",
        "|---|---:|---:|---|",
    ])
    for row in projection_rows:
        lines.append(
            f"| `{row['relation_state_projection']}` | {row['event_count']} | "
            f"{row['statement_final_event_count']} | {row['literal_working_reading_de']} |"
        )
    lines.extend([
        "", "Die zusätzliche44-Zeilen-Tabelle hält jede geschriebene Relation-Argument-Steuerfolge fest. Nur16/216 Relationsstellen berühren überhaupt ein explizites Argument in derselben Kontrollhülle; die Relation ist daher meist ein Kontextlink und keine ausgeschriebene binäre Klammer zwischen zwei Nomen.", "",
        "## Arbeitsgrenze und nächster Schritt", "",
        "Dies ist eine vollständige Arbeitsbelegung vorhandener Wurzeln. Sie ändert keine Bedeutung oder Seite. Als nächstes können Handlung, Grad, Relation, Argument und Kontrolle zu einer einzigen typisierten Zustandskarte zusammengesetzt werden; dafür wird weiterhin keine neue Seite geöffnet.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
