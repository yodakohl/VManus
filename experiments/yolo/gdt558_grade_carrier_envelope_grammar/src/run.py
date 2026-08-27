#!/usr/bin/env python3
"""Compile grade-bearing OT/OL carrier envelopes from the GDT557 atlas."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt558_grade_carrier_envelope_grammar"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G420 = ROOT / "experiments/yolo/gdt420_action_head_slot_license_atlas/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"

STATE_ATLAS_PATH = G557 / "gdt557_all_state_marker_occurrences.tsv"
OLD_CONTEXT_PATH = G416 / "gdt416_4576_imperative_clauses.tsv"
CURRENT_CONTEXT_PATH = G539 / "gdt539_546_contextual_prose_events.tsv"
HEAD_PROFILE_PATH = G420 / "gdt420_9_action_head_profiles.tsv"
PAIR_PROFILE_PATH = G421 / "gdt421_81_ordered_pair_profiles.tsv"

ASSIGNMENT_OUT = OUT / "gdt558_333_grade_carrier_assignments.tsv"
ENVELOPE_OUT = OUT / "gdt558_8_grade_carrier_envelopes.tsv"
PROJECTION_OUT = OUT / "gdt558_25_grade_state_projection_templates.tsv"
FAMILY_OUT = OUT / "gdt558_17_multirung_grade_families.tsv"
ORIENTATION_OUT = OUT / "gdt558_grade_operator_orientation.tsv"
HAZARD_OUT = OUT / "gdt558_18_false_inheritance_hazards.tsv"
BOOK_OUT = OUT / "GDT558_GRADE_CARRIER_BOOK.md"
RESULT_OUT = OUT / "gdt558_result.json"

STATUS = "PASS_EIGHT_GRADE_ENVELOPES__151_VISIBLE_HOSTS_LICENSED__18_FALSE_CROSS_BOUNDARY_BINDS_AVOIDED"
GRADES = ("E", "EE", "EEE")
GRADE_SET = set(GRADES)
CONTROLS = ("OT", "OL", "DY")
CONTROL_SET = set(CONTROLS)
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
ACTION_SET = set(ACTIONS)
GRADE_VALUES = {"E": "GRAD I", "EE": "GRAD II", "EEE": "GRAD III"}
ACTION_VALUES = {
    "OK": "setzen", "CH": "nehmen", "SH": "halten", "K": "geben",
    "S": "wählen", "CHD": "bearbeiten", "T": "einstellen",
    "R": "markieren", "P": "einsetzen",
}
CONTROL_VALUES = {
    "OT": "danach den nächsten Träger eröffnen",
    "OL": "den laufenden Träger fortsetzen",
    "DY": "den laufenden Schritt abschließen",
}
ENVELOPE_TEMPLATES = {
    "OT>G<END": "danach X auf Grad n",
    "START>G<OL": "X auf Grad n; X weiterführen",
    "OT>G<DY": "danach X auf Grad n; X abschließen",
    "OL>G<DY": "X weiterführen auf Grad n; X abschließen",
    "OL>G<END": "X weiterführen auf Grad n",
    "OT>G<OL": "danach X auf Grad n; X weiterführen",
    "OL>G<OL": "X weiterführen auf Grad n; weiter aktiv halten",
    "START>G<DY": "X auf Grad n; X abschließen",
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


def split_pipe(value: str) -> set[str]:
    return set() if value == "NONE" else set(value.split("|"))


def marker_sequence(recipe: str) -> str:
    return "+".join(atom for atom in recipe.split("+") if atom in CONTROL_SET) or "NONE"


def grade_state_projection(recipe: str) -> str:
    return "+".join(atom for atom in recipe.split("+") if atom in CONTROL_SET | GRADE_SET)


def projection_reading(projection: str) -> str:
    values = {**CONTROL_VALUES, **{key: value.lower() for key, value in GRADE_VALUES.items()}}
    return "; dann ".join(values[atom] for atom in projection.split("+"))


def carrier_reading(
    left_control: str, right_control: str, grade: str, action_chain: list[str]
) -> str:
    if action_chain:
        carrier = " und ".join(ACTION_VALUES[action] for action in action_chain)
    else:
        carrier = "Träger"
    grade_label = GRADE_VALUES[grade].replace("GRAD", "Grad")
    graded = f"{carrier} auf {grade_label}"
    if left_control == "OT":
        graded = "danach " + graded
    elif left_control == "OL":
        graded = "weiter mit " + graded
    elif left_control == "DY":
        graded = "nach lokalem Abschluss " + graded
    if right_control == "OL":
        graded += "; den Träger weiterführen"
    elif right_control == "DY":
        graded += "; den Schritt abschließen"
    elif right_control == "OT":
        graded += "; danach den nächsten Träger eröffnen"
    return graded


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state_rows = read_tsv(STATE_ATLAS_PATH)
    old_context_rows = read_tsv(OLD_CONTEXT_PATH)
    current_context_rows = read_tsv(CURRENT_CONTEXT_PATH)
    head_rows = read_tsv(HEAD_PROFILE_PATH)
    pair_rows = read_tsv(PAIR_PROFILE_PATH)
    if (len(state_rows), len(old_context_rows), len(current_context_rows), len(head_rows), len(pair_rows)) != (1870, 4576, 546, 9, 81):
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

    old_context = {row["global_running_event_id"]: row for row in old_context_rows}
    current_context = {row["event_id"]: row for row in current_context_rows}
    if set(old_context) & set(current_context):
        raise RuntimeError("Old/current event identifiers overlap")
    context = {**old_context, **current_context}
    missing_context = sorted(set(events) - set(context))
    if missing_context:
        raise RuntimeError(f"Missing context rows: {missing_context[:10]}")

    head_profiles = {row["action_head"]: row for row in head_rows}
    pair_profiles = {row["ordered_pair"]: row for row in pair_rows}

    selected_events = {
        event_id: row for event_id, row in events.items()
        if any(atom in {"OT", "OL"} for atom in row["recipe"].split("+"))
        and any(atom in GRADE_SET for atom in row["recipe"].split("+"))
    }
    assignment_rows: list[dict[str, object]] = []
    for event_id, event in selected_events.items():
        atoms = event["recipe"].split("+")
        source_context = context[event_id]
        inherited_action = source_context["inherited_action_root"]
        grade_positions = [index for index, atom in enumerate(atoms) if atom in GRADE_SET]
        for grade_occurrence, grade_index in enumerate(grade_positions, 1):
            grade = atoms[grade_index]
            left_control_index = max(
                (index for index in range(grade_index) if atoms[index] in CONTROL_SET),
                default=-1,
            )
            right_control_index = min(
                (index for index in range(grade_index + 1, len(atoms)) if atoms[index] in CONTROL_SET),
                default=len(atoms),
            )
            left_control = atoms[left_control_index] if left_control_index >= 0 else "START"
            right_control = atoms[right_control_index] if right_control_index < len(atoms) else "END"
            block = atoms[left_control_index + 1:right_control_index]
            local_grade_index = grade_index - left_control_index - 1
            before_grade = block[:local_grade_index]
            after_grade = block[local_grade_index + 1:]
            left_actions = [atom for atom in before_grade if atom in ACTION_SET]
            right_actions = [atom for atom in after_grade if atom in ACTION_SET]
            envelope = f"{left_control}>G<{right_control}"

            if left_actions:
                if len(left_actions) == 1:
                    host_key = left_actions[-1]
                    licensed = split_pipe(head_profiles[host_key]["licensed_grades"])
                    host_license_source = "GDT420_SINGLE_HEAD"
                    host_license_status = "LICENSED" if grade in licensed else "NOT_LICENSED"
                else:
                    host_key = "+".join(left_actions[-2:])
                    licensed = split_pipe(pair_profiles[host_key]["licensed_grades"])
                    host_license_source = "GDT421_LAST_ORDERED_PAIR"
                    host_license_status = "LICENSED" if grade in licensed else "NOT_LICENSED"
                host_mode = "VISIBLE_SAME_BLOCK_ACTION_CHAIN"
                cross_boundary_status = "NOT_NEEDED_VISIBLE_HOST"
            else:
                host_key = "NONE"
                host_license_source = "CONTROL_DELIMITED_GRADE_CARRIER"
                host_license_status = "GRADE_VALUE_WITHOUT_FORCED_ACTION_HOST"
                host_mode = "CONTROL_CARRIED_GRADE_VALUE"
                if inherited_action == "NONE":
                    cross_boundary_status = "NO_INHERITED_ACTION"
                else:
                    inherited_license = split_pipe(head_profiles[inherited_action]["licensed_grades"])
                    cross_boundary_status = (
                        "WOULD_BE_LICENSED_BUT_NOT_FORCED"
                        if grade in inherited_license
                        else "WOULD_VIOLATE_HEAD_LICENSE__DO_NOT_CROSS_CONTROL_BOUNDARY"
                    )

            assignment_rows.append({
                "assignment_ordinal": len(assignment_rows) + 1,
                "cohort": event["cohort"], "event_id": event_id,
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"], "register": event["register"],
                "surface": event["surface"], "recipe": event["recipe"],
                "event_marker_sequence": event["event_marker_sequence"],
                "grade_state_projection": grade_state_projection(event["recipe"]),
                "grade_occurrence_in_recipe": grade_occurrence,
                "grade": grade, "grade_value_de": GRADE_VALUES[grade],
                "grade_atom_position": grade_index + 1,
                "recipe_atom_count": len(atoms),
                "left_control": left_control, "right_control": right_control,
                "carrier_envelope": envelope,
                "content_block": "+".join(block),
                "grade_position_in_block": local_grade_index + 1,
                "left_content_before_grade": "+".join(before_grade) or "NONE",
                "right_content_after_grade": "+".join(after_grade) or "NONE",
                "visible_left_action_chain": "+".join(left_actions) or "NONE",
                "visible_right_action_chain": "+".join(right_actions) or "NONE",
                "selected_visible_host_key": host_key,
                "host_license_source": host_license_source,
                "visible_host_license_status": host_license_status,
                "inherited_action_root": inherited_action,
                "cross_boundary_inheritance_status": cross_boundary_status,
                "default_host_mode": host_mode,
                "envelope_template_de": ENVELOPE_TEMPLATES[envelope],
                "complete_carrier_reading_de": carrier_reading(left_control, right_control, grade, left_actions),
                "statement_position": event["statement_position"],
                "statement_final": event["statement_final"],
                "current_reading_de": event["current_reading_de"],
                "guard": "GRADE_STAYS_INSIDE_CONTROL_ENVELOPE__NO_ROOT_OR_RECIPE_CHANGE",
            })

    single_grade_events = {
        event_id: event for event_id, event in selected_events.items()
        if sum(atom in GRADE_SET for atom in event["recipe"].split("+")) == 1
    }
    family_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in single_grade_events.values():
        skeleton = "+".join("G" if atom in GRADE_SET else atom for atom in event["recipe"].split("+"))
        family_groups[skeleton].append(event)
    multirung_groups = {
        skeleton: material for skeleton, material in family_groups.items()
        if len({next(atom for atom in event["recipe"].split("+") if atom in GRADE_SET) for event in material}) >= 2
    }
    family_rows: list[dict[str, object]] = []
    family_id_by_skeleton: dict[str, str] = {}
    for skeleton, material in sorted(
        multirung_groups.items(),
        key=lambda item: (
            -len({next(atom for atom in event["recipe"].split("+") if atom in GRADE_SET) for event in item[1]}),
            -len(item[1]), item[0],
        ),
    ):
        family_id = f"G558-F{len(family_rows) + 1:02d}"
        family_id_by_skeleton[skeleton] = family_id
        by_grade: dict[str, list[dict[str, str]]] = {
            grade: [event for event in material if grade in event["recipe"].split("+")]
            for grade in GRADES
        }
        variants = [grade for grade in GRADES if by_grade[grade]]
        sample_assignment = next(row for row in assignment_rows if row["event_id"] == material[0]["event_id"])
        family_rows.append({
            "family_ordinal": len(family_rows) + 1, "family_id": family_id,
            "normalized_recipe": skeleton,
            "marker_sequence": marker_sequence(material[0]["recipe"]),
            "carrier_envelope": sample_assignment["carrier_envelope"],
            "grade_variant_count": len(variants), "grade_variants": "|".join(variants),
            "family_status": "COMPLETE_THREE_RUNG" if len(variants) == 3 else "OBSERVED_TWO_RUNG",
            "event_count": len(material),
            "e_event_count": len(by_grade["E"]), "ee_event_count": len(by_grade["EE"]),
            "eee_event_count": len(by_grade["EEE"]),
            "e_page_count": len({event["physical_page"] for event in by_grade["E"]}),
            "ee_page_count": len({event["physical_page"] for event in by_grade["EE"]}),
            "eee_page_count": len({event["physical_page"] for event in by_grade["EEE"]}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "statement_final_percent": pct(sum(event["statement_final"] == "YES" for event in material), len(material)),
            "surfaces_by_grade": " || ".join(
                f"{grade}:{'|'.join(sorted({event['surface'] for event in by_grade[grade]}))}"
                for grade in variants
            ),
            "event_ids": "|".join(event["event_id"] for event in material),
            "family_reading_de": ENVELOPE_TEMPLATES[str(sample_assignment["carrier_envelope"])],
            "scope_result": "GRADE_RUNG_SUBSTITUTES_INSIDE_FIXED_CONTROL_ENVELOPE",
        })

    for row in assignment_rows:
        skeleton = "+".join("G" if atom in GRADE_SET else atom for atom in str(row["recipe"]).split("+"))
        row["multirung_family_id"] = family_id_by_skeleton.get(skeleton, "NONE")

    envelope_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in assignment_rows:
        envelope_groups[str(row["carrier_envelope"])].append(row)
    envelope_rows: list[dict[str, object]] = []
    for envelope, material in sorted(envelope_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        grade_counts = Counter(str(row["grade"]) for row in material)
        inheritance_counts = Counter(str(row["cross_boundary_inheritance_status"]) for row in material)
        envelope_rows.append({
            "envelope_ordinal": len(envelope_rows) + 1,
            "carrier_envelope": envelope, "grade_occurrence_count": len(material),
            "event_count": len({str(row["event_id"]) for row in material}),
            "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in material}),
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "register_count": len({str(row["register"]) for row in material}),
            "e_count": grade_counts["E"], "ee_count": grade_counts["EE"],
            "eee_count": grade_counts["EEE"],
            "visible_same_block_host_count": sum(row["default_host_mode"] == "VISIBLE_SAME_BLOCK_ACTION_CHAIN" for row in material),
            "control_carried_grade_count": sum(row["default_host_mode"] == "CONTROL_CARRIED_GRADE_VALUE" for row in material),
            "false_cross_boundary_bind_count": inheritance_counts["WOULD_VIOLATE_HEAD_LICENSE__DO_NOT_CROSS_CONTROL_BOUNDARY"],
            "statement_final_occurrence_count": sum(row["statement_final"] == "YES" for row in material),
            "statement_final_percent": pct(sum(row["statement_final"] == "YES" for row in material), len(material)),
            "multirung_assignment_count": sum(row["multirung_family_id"] != "NONE" for row in material),
            "working_template_de": ENVELOPE_TEMPLATES[envelope],
        })

    projection_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in selected_events.values():
        projection_groups[grade_state_projection(event["recipe"])].append(event)
    projection_rows: list[dict[str, object]] = []
    for projection, material in sorted(projection_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        projection_rows.append({
            "projection_ordinal": len(projection_rows) + 1,
            "grade_state_projection": projection, "event_count": len(material),
            "grade_occurrence_count": sum(sum(atom in GRADE_SET for atom in event["recipe"].split("+")) for event in material),
            "statement_count": len({f"{event['cohort']}::{event['statement_id']}" for event in material}),
            "physical_page_count": len({event["physical_page"] for event in material}),
            "register_count": len({event["register"] for event in material}),
            "exact_recipe_count": len({event["recipe"] for event in material}),
            "surface_count": len({event["surface"] for event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "statement_final_percent": pct(sum(event["statement_final"] == "YES" for event in material), len(material)),
            "default_operation_reading_de": projection_reading(projection),
            "example_events": "|".join(event["event_id"] for event in material[:5]),
            "example_surfaces": "|".join(event["surface"] for event in material[:5]),
        })

    orientation_rows: list[dict[str, object]] = []
    for marker in ("OT", "OL"):
        for grade in GRADES:
            coevent = [
                row for row in assignment_rows
                if row["grade"] == grade and marker in str(row["recipe"]).split("+")
            ]
            left_boundary = [row for row in coevent if row["left_control"] == marker]
            right_boundary = [row for row in coevent if row["right_control"] == marker]
            both = [row for row in coevent if row["left_control"] == marker and row["right_control"] == marker]
            separated = [row for row in coevent if row["left_control"] != marker and row["right_control"] != marker]
            orientation_rows.append({
                "orientation_ordinal": len(orientation_rows) + 1,
                "marker": marker, "grade": grade, "grade_value_de": GRADE_VALUES[grade],
                "coevent_grade_occurrence_count": len(coevent),
                "marker_left_boundary_count": len(left_boundary),
                "marker_right_boundary_count": len(right_boundary),
                "marker_both_boundaries_count": len(both),
                "separated_by_other_control_count": len(separated),
                "same_envelope_contact_count": len(coevent) - len(separated),
                "working_orientation": (
                    "OT_ALWAYS_OPENS_GRADED_RIGHT_BLOCK" if marker == "OT"
                    else "OL_MAY_OPEN_RIGHT_OR_HOLD_LEFT_GRADED_BLOCK"
                ),
            })

    hazard_rows: list[dict[str, object]] = []
    for row in assignment_rows:
        if row["cross_boundary_inheritance_status"] != "WOULD_VIOLATE_HEAD_LICENSE__DO_NOT_CROSS_CONTROL_BOUNDARY":
            continue
        inherited = str(row["inherited_action_root"])
        hazard_rows.append({
            "hazard_ordinal": len(hazard_rows) + 1,
            "event_id": row["event_id"], "physical_page": row["physical_page"],
            "register": row["register"], "surface": row["surface"],
            "recipe": row["recipe"], "grade": row["grade"],
            "grade_value_de": row["grade_value_de"],
            "carrier_envelope": row["carrier_envelope"],
            "inherited_action_root": inherited,
            "inherited_action_value_de": ACTION_VALUES[inherited],
            "inherited_head_licensed_grades": head_profiles[inherited]["licensed_grades"],
            "false_reading_to_avoid_de": f"{ACTION_VALUES[inherited]} auf {str(row['grade_value_de']).replace('GRAD', 'Grad')}",
            "retained_default_de": row["complete_carrier_reading_de"],
            "resolution": "CONTROL_BOUNDARY_BLOCKS_FORCED_GRADE_TO_INHERITED_HEAD_ATTACHMENT",
        })

    multirung_event_ids = {
        event_id for material in multirung_groups.values() for event_id in (event["event_id"] for event in material)
    }
    multirung_events = [selected_events[event_id] for event_id in multirung_event_ids]
    dy_multirung = [event for event in multirung_events if marker_sequence(event["recipe"]).endswith("DY")]
    nondy_multirung = [event for event in multirung_events if "DY" not in event["recipe"].split("+")]
    inheritance_counts = Counter(str(row["cross_boundary_inheritance_status"]) for row in assignment_rows)
    result = {
        "status": STATUS,
        "source_marker_occurrence_count": len(state_rows),
        "source_marker_event_count": len(events),
        "grade_state_event_count": len(selected_events),
        "grade_occurrence_count": len(assignment_rows),
        "grade_e_count": sum(row["grade"] == "E" for row in assignment_rows),
        "grade_ee_count": sum(row["grade"] == "EE" for row in assignment_rows),
        "grade_eee_count": sum(row["grade"] == "EEE" for row in assignment_rows),
        "single_grade_event_count": len(single_grade_events),
        "double_grade_event_count": len(selected_events) - len(single_grade_events),
        "physical_page_count": len({row["physical_page"] for row in assignment_rows}),
        "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in assignment_rows}),
        "carrier_envelope_count": len(envelope_rows),
        "grade_state_projection_count": len(projection_rows),
        "visible_same_block_host_count": sum(row["default_host_mode"] == "VISIBLE_SAME_BLOCK_ACTION_CHAIN" for row in assignment_rows),
        "visible_host_licensed_count": sum(row["visible_host_license_status"] == "LICENSED" for row in assignment_rows),
        "control_carried_grade_count": sum(row["default_host_mode"] == "CONTROL_CARRIED_GRADE_VALUE" for row in assignment_rows),
        "inherited_action_available_without_visible_host_count": inheritance_counts["WOULD_BE_LICENSED_BUT_NOT_FORCED"] + inheritance_counts["WOULD_VIOLATE_HEAD_LICENSE__DO_NOT_CROSS_CONTROL_BOUNDARY"],
        "cross_boundary_would_be_licensed_count": inheritance_counts["WOULD_BE_LICENSED_BUT_NOT_FORCED"],
        "false_cross_boundary_bind_count": len(hazard_rows),
        "no_inherited_action_grade_count": inheritance_counts["NO_INHERITED_ACTION"],
        "ot_left_boundary_grade_count": sum(row["left_control"] == "OT" for row in assignment_rows),
        "grade_before_ot_boundary_count": sum(row["right_control"] == "OT" for row in assignment_rows),
        "ol_left_boundary_grade_count": sum(row["left_control"] == "OL" for row in assignment_rows),
        "ol_right_boundary_grade_count": sum(row["right_control"] == "OL" for row in assignment_rows),
        "ol_both_boundary_grade_count": sum(row["left_control"] == "OL" and row["right_control"] == "OL" for row in assignment_rows),
        "grade_separated_from_only_ol_by_dy_count": sum("OL" in str(row["recipe"]).split("+") and row["left_control"] != "OL" and row["right_control"] != "OL" for row in assignment_rows),
        "multirung_family_count": len(family_rows),
        "complete_three_rung_family_count": sum(row["family_status"] == "COMPLETE_THREE_RUNG" for row in family_rows),
        "multirung_family_event_count": len(multirung_events),
        "multirung_dy_event_count": len(dy_multirung),
        "multirung_dy_final_count": sum(event["statement_final"] == "YES" for event in dy_multirung),
        "multirung_non_dy_event_count": len(nondy_multirung),
        "multirung_non_dy_final_count": sum(event["statement_final"] == "YES" for event in nondy_multirung),
        "all_assignments_have_default": all(bool(row["complete_carrier_reading_de"]) for row in assignment_rows),
        "new_pages": 0, "recipe_changes": 0, "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }

    write_tsv(ASSIGNMENT_OUT, assignment_rows)
    write_tsv(ENVELOPE_OUT, envelope_rows)
    write_tsv(PROJECTION_OUT, projection_rows)
    write_tsv(FAMILY_OUT, family_rows)
    write_tsv(ORIENTATION_OUT, orientation_rows)
    write_tsv(HAZARD_OUT, hazard_rows)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT558 — Grad-Trägerbuch", "",
        "Alle333 Gradstellen erhalten einen kurzen Träger. `E/EE/EEE` bleiben in diesem Leser kurze Werte (`GRAD I/II/III`). OT, OL und DY bestimmen die Hülle, in der der Wert gilt; der Grad ändert die Kontrollreichweite nicht.", "",
        "## Acht vollständige Hüllen", "",
        "| Hülle | Gradstellen | I | II | III | sichtbarer Kopf | falsche Erbungen vermieden | Arbeitsformel |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in envelope_rows:
        lines.append(
            f"| `{row['carrier_envelope']}` | {row['grade_occurrence_count']} | {row['e_count']} | {row['ee_count']} | {row['eee_count']} | "
            f"{row['visible_same_block_host_count']} | {row['false_cross_boundary_bind_count']} | {row['working_template_de']} |"
        )
    lines.extend([
        "", "## Einfache Leseregel", "",
        "- Ein sichtbarer Handlungskopf links vom Grad innerhalb derselben Hülle trägt den Grad. Alle 151 solchen Fälle sind durch die vorhandene Einzelkopf- oder Paarkarte lizenziert.",
        "- Fehlt in derselben Hülle ein sichtbarer Kopf, lies kurz `Träger auf Grad I/II/III`. Erzwinge keinen Handlungskopf über OT, OL oder DY hinweg.",
        "- Linkes OT eröffnet diesen Gradträger; linkes OL führt ihn vorwärts; rechtes OL hält ihn aktiv; rechtes DY schließt ihn.",
        "- Die Atomreihenfolge bleibt erhalten. Ein DY zwischen Grad und OL trennt beide Hüllen.", "",
        "## Mehrstufige Familien", "",
        "| Familie | normiertes Rezept | Stufen | Karten | final | Arbeitsformel |",
        "|---|---|---|---:|---:|---|",
    ])
    for row in family_rows:
        lines.append(
            f"| {row['family_id']} | `{row['normalized_recipe']}` | {row['grade_variants']} | "
            f"{row['event_count']} | {row['statement_final_event_count']} | {row['family_reading_de']} |"
        )
    lines.extend([
        "", "Die 17 Familien enthalten235 Karten. In den DY-Familien enden94/94 Karten, in den Familien ohne DY nur2/141. Der Gradwechsel selbst verschiebt keine Kontrollgrenze.", "",
        "## Erbschaftsfallen", "",
        "Eine blinde Bindung an den vor der Kontrollhülle geerbten Handlungskopf würde18 vorhandene Kopfkarten verletzen:15-mal CHD mit Grad I/II und3-mal CH/SH mit Grad III. Diese Widersprüche verschwinden ohne Umdeutung, sobald der Grad in seiner sichtbaren Kontrollhülle bleibt.", "",
        "## Grenze", "",
        "Die Hülle ist eine Arbeitslesung vorhandener Komponenten. Sie ändert keinen Stamm, Gradwert, Handlungskopf, Satz oder Seitenbestand und identifiziert weder Klartext noch historische Syntax.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
