#!/usr/bin/env python3
"""Independently validate GDT558 grade carrier envelopes."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
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

STATE_ATLAS = G557 / "gdt557_all_state_marker_occurrences.tsv"
OLD_CONTEXT = G416 / "gdt416_4576_imperative_clauses.tsv"
CURRENT_CONTEXT = G539 / "gdt539_546_contextual_prose_events.tsv"
HEAD_PROFILE = G420 / "gdt420_9_action_head_profiles.tsv"
PAIR_PROFILE = G421 / "gdt421_81_ordered_pair_profiles.tsv"

ASSIGNMENT = OUT / "gdt558_333_grade_carrier_assignments.tsv"
ENVELOPE = OUT / "gdt558_8_grade_carrier_envelopes.tsv"
PROJECTION = OUT / "gdt558_25_grade_state_projection_templates.tsv"
FAMILY = OUT / "gdt558_17_multirung_grade_families.tsv"
ORIENTATION = OUT / "gdt558_grade_operator_orientation.tsv"
HAZARD = OUT / "gdt558_18_false_inheritance_hazards.tsv"
BOOK = OUT / "GDT558_GRADE_CARRIER_BOOK.md"
RESULT = OUT / "gdt558_result.json"
VALIDATION = OUT / "gdt558_validation.json"
RUNNER = BASE / "src/run.py"

GRADES = ("E", "EE", "EEE")
GRADE_SET = set(GRADES)
CONTROL_SET = {"OT", "OL", "DY"}
ACTION_SET = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_pipe(value: str) -> set[str]:
    return set() if value == "NONE" else set(value.split("|"))


def projection(recipe: str) -> str:
    return "+".join(atom for atom in recipe.split("+") if atom in GRADE_SET | CONTROL_SET)


def main() -> int:
    state_rows = read_tsv(STATE_ATLAS)
    old_rows = read_tsv(OLD_CONTEXT)
    current_rows = read_tsv(CURRENT_CONTEXT)
    head_rows = read_tsv(HEAD_PROFILE)
    pair_rows = read_tsv(PAIR_PROFILE)
    assignments = read_tsv(ASSIGNMENT)
    envelopes = read_tsv(ENVELOPE)
    projections = read_tsv(PROJECTION)
    families = read_tsv(FAMILY)
    orientations = read_tsv(ORIENTATION)
    hazards = read_tsv(HAZARD)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("input_counts", (len(state_rows), len(old_rows), len(current_rows), len(head_rows), len(pair_rows)) == (1870, 4576, 546, 9, 81), [len(state_rows), len(old_rows), len(current_rows), len(head_rows), len(pair_rows)])
    check("source_pages_exclude_f84", all(not row["physical_page"].startswith("f84") for row in state_rows + old_rows + current_rows), [])

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_rows:
        grouped[row["event_id"]].append(row)
    stable_fields = ("cohort", "statement_id", "physical_page", "register", "surface", "recipe", "event_marker_sequence", "statement_position", "statement_final", "current_reading_de")
    conflicts = [event_id for event_id, rows in grouped.items() if any(len({row[field] for row in rows}) != 1 for field in stable_fields)]
    check("source_event_deduplication", len(grouped) == 1656 and not conflicts, [len(grouped), conflicts[:10]])
    events = {event_id: rows[0] for event_id, rows in grouped.items()}

    old_context = {row["global_running_event_id"]: row for row in old_rows}
    current_context = {row["event_id"]: row for row in current_rows}
    context = {**old_context, **current_context}
    check("context_join_complete", not (set(old_context) & set(current_context)) and not (set(events) - set(context)), [len(old_context), len(current_context), len(set(events) - set(context))])
    heads = {row["action_head"]: split_pipe(row["licensed_grades"]) for row in head_rows}
    pairs = {row["ordered_pair"]: split_pipe(row["licensed_grades"]) for row in pair_rows}

    selected = {
        event_id: event for event_id, event in events.items()
        if any(atom in {"OT", "OL"} for atom in event["recipe"].split("+"))
        and any(atom in GRADE_SET for atom in event["recipe"].split("+"))
    }
    selected_grade_count = sum(sum(atom in GRADE_SET for atom in event["recipe"].split("+")) for event in selected.values())
    grade_counts = Counter(atom for event in selected.values() for atom in event["recipe"].split("+") if atom in GRADE_SET)
    check("selected_population", len(selected) == 326 and selected_grade_count == 333 and grade_counts == Counter({"E": 214, "EE": 114, "EEE": 5}), [len(selected), selected_grade_count, grade_counts])
    check("selected_scope", len({event["physical_page"] for event in selected.values()}) == 22 and len({f"{event['cohort']}::{event['statement_id']}" for event in selected.values()}) == 222, [])
    check("selected_cohorts", Counter(event["cohort"] for event in selected.values()) == Counter({"OLD26_GDT407": 295, "CURRENT4_GDT539": 31}), Counter(event["cohort"] for event in selected.values()))
    grade_multiplicity = Counter(sum(atom in GRADE_SET for atom in event["recipe"].split("+")) for event in selected.values())
    check("grade_multiplicity", grade_multiplicity == Counter({1: 319, 2: 7}), grade_multiplicity)

    recomputed: list[tuple[object, ...]] = []
    visible_licensed = 0
    visible_count = 0
    control_carried = 0
    inherited_available = 0
    inherited_would_license = 0
    no_inherited = 0
    hazard_tuples: list[tuple[str, str, str, str]] = []
    envelope_counts: Counter[str] = Counter()
    for event_id, event in selected.items():
        atoms = event["recipe"].split("+")
        inherited = context[event_id]["inherited_action_root"]
        occurrence = 0
        for grade_index, grade in enumerate(atoms):
            if grade not in GRADE_SET:
                continue
            occurrence += 1
            left_index = max((index for index in range(grade_index) if atoms[index] in CONTROL_SET), default=-1)
            right_index = min((index for index in range(grade_index + 1, len(atoms)) if atoms[index] in CONTROL_SET), default=len(atoms))
            left_control = atoms[left_index] if left_index >= 0 else "START"
            right_control = atoms[right_index] if right_index < len(atoms) else "END"
            block = atoms[left_index + 1:right_index]
            local = grade_index - left_index - 1
            left_actions = [atom for atom in block[:local] if atom in ACTION_SET]
            right_actions = [atom for atom in block[local + 1:] if atom in ACTION_SET]
            envelope = f"{left_control}>G<{right_control}"
            envelope_counts[envelope] += 1
            if left_actions:
                visible_count += 1
                if len(left_actions) == 1:
                    licensed = grade in heads[left_actions[-1]]
                else:
                    licensed = grade in pairs["+".join(left_actions[-2:])]
                visible_licensed += licensed
                cross_status = "NOT_NEEDED_VISIBLE_HOST"
            else:
                control_carried += 1
                if inherited == "NONE":
                    cross_status = "NO_INHERITED_ACTION"
                    no_inherited += 1
                elif grade in heads[inherited]:
                    cross_status = "WOULD_BE_LICENSED_BUT_NOT_FORCED"
                    inherited_available += 1
                    inherited_would_license += 1
                else:
                    cross_status = "WOULD_VIOLATE_HEAD_LICENSE__DO_NOT_CROSS_CONTROL_BOUNDARY"
                    inherited_available += 1
                    hazard_tuples.append((event_id, grade, inherited, envelope))
            recomputed.append((
                event_id, occurrence, grade, grade_index + 1, envelope,
                "+".join(block), "+".join(left_actions) or "NONE",
                "+".join(right_actions) or "NONE", cross_status,
            ))
    output_tuples = [(
        row["event_id"], int(row["grade_occurrence_in_recipe"]), row["grade"],
        int(row["grade_atom_position"]), row["carrier_envelope"], row["content_block"],
        row["visible_left_action_chain"], row["visible_right_action_chain"],
        row["cross_boundary_inheritance_status"],
    ) for row in assignments]
    check("assignment_rows_exact", len(assignments) == 333 and recomputed == output_tuples, [len(recomputed), len(output_tuples), next((index for index, (left, right) in enumerate(zip(recomputed, output_tuples)) if left != right), "NONE")])

    expected_envelopes = Counter({
        "OT>G<END": 97, "START>G<OL": 91, "OT>G<DY": 72,
        "OL>G<DY": 29, "OL>G<END": 27, "OT>G<OL": 9,
        "OL>G<OL": 7, "START>G<DY": 1,
    })
    output_envelopes = Counter({row["carrier_envelope"]: int(row["grade_occurrence_count"]) for row in envelopes})
    check("eight_envelopes_exact", envelope_counts == expected_envelopes == output_envelopes, [envelope_counts, output_envelopes])
    check("visible_hosts_all_licensed", (visible_count, visible_licensed) == (151, 151), [visible_count, visible_licensed])
    check("control_carried_count", control_carried == 182, control_carried)
    check("inheritance_partition", (inherited_available, inherited_would_license, len(hazard_tuples), no_inherited) == (152, 134, 18, 30), [inherited_available, inherited_would_license, len(hazard_tuples), no_inherited])

    hazard_ids = [item[0] for item in hazard_tuples]
    expected_hazard_ids = [
        "G407-E1145", "G407-E1349", "G407-E1399", "G407-E2009", "G407-E2033",
        "G407-E2543", "G407-E2830", "G407-E3213", "G407-E3242", "G407-E3500",
        "G407-E3522", "G407-E3655", "G407-E3657", "G407-E3660", "G407-E3832",
        "G407-E4404", "G407-E4405", "G515-E0332",
    ]
    check("eighteen_hazard_ids", hazard_ids == expected_hazard_ids and [row["event_id"] for row in hazards] == expected_hazard_ids, [hazard_ids, [row["event_id"] for row in hazards]])
    check("hazard_head_grade_profile", Counter((item[2], item[1]) for item in hazard_tuples) == Counter({("CHD", "E"): 10, ("CHD", "EE"): 5, ("CH", "EEE"): 2, ("SH", "EEE"): 1}), Counter(f"{item[2]}+{item[1]}" for item in hazard_tuples))
    check("hazard_envelope_profile", Counter(item[3] for item in hazard_tuples) == Counter({"OT>G<DY": 10, "OT>G<END": 6, "OL>G<END": 2}), Counter(item[3] for item in hazard_tuples))

    projection_counts = Counter(projection(event["recipe"]) for event in selected.values())
    output_projection_counts = Counter({row["grade_state_projection"]: int(row["event_count"]) for row in projections})
    check("twenty_five_projections_exact", len(projection_counts) == 25 and projection_counts == output_projection_counts, [len(projection_counts), projection_counts, output_projection_counts])
    check("all_projection_defaults_present", all(row["default_operation_reading_de"] for row in projections), [])

    one_grade = [event for event in selected.values() if sum(atom in GRADE_SET for atom in event["recipe"].split("+")) == 1]
    family_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in one_grade:
        skeleton = "+".join("G" if atom in GRADE_SET else atom for atom in event["recipe"].split("+"))
        family_groups[skeleton].append(event)
    multirung = {skeleton: material for skeleton, material in family_groups.items() if len({next(atom for atom in event["recipe"].split("+") if atom in GRADE_SET) for event in material}) >= 2}
    complete = [skeleton for skeleton, material in multirung.items() if {next(atom for atom in event["recipe"].split("+") if atom in GRADE_SET) for event in material} == GRADE_SET]
    family_events = [event for material in multirung.values() for event in material]
    check("multirung_family_counts", len(multirung) == 17 and len(family_events) == 235 and complete == ["OT+G+DY"], [len(multirung), len(family_events), complete])
    check("family_artifact_exact", {row["normalized_recipe"]: int(row["event_count"]) for row in families} == {skeleton: len(material) for skeleton, material in multirung.items()}, [])
    dy_family_events = [event for event in family_events if projection(event["recipe"]).endswith("DY")]
    nondy_family_events = [event for event in family_events if "DY" not in event["recipe"].split("+")]
    check("multirung_scope_invariance", (len(dy_family_events), sum(event["statement_final"] == "YES" for event in dy_family_events), len(nondy_family_events), sum(event["statement_final"] == "YES" for event in nondy_family_events)) == (94, 94, 141, 2), [len(dy_family_events), sum(event["statement_final"] == "YES" for event in dy_family_events), len(nondy_family_events), sum(event["statement_final"] == "YES" for event in nondy_family_events)])

    orientation_map = {(row["marker"], row["grade"]): row for row in orientations}
    expected_orientation = {
        ("OT", "E"): (107, 107, 0, 0, 0),
        ("OT", "EE"): (69, 69, 0, 0, 0),
        ("OT", "EEE"): (2, 2, 0, 0, 0),
        ("OL", "E"): (115, 34, 87, 6, 0),
        ("OL", "EE"): (46, 27, 19, 1, 1),
        ("OL", "EEE"): (3, 2, 1, 0, 0),
    }
    actual_orientation = {key: (
        int(row["coevent_grade_occurrence_count"]), int(row["marker_left_boundary_count"]),
        int(row["marker_right_boundary_count"]), int(row["marker_both_boundaries_count"]),
        int(row["separated_by_other_control_count"]),
    ) for key, row in orientation_map.items()}
    check("operator_orientation_exact", actual_orientation == expected_orientation, {f"{key[0]}+{key[1]}": value for key, value in actual_orientation.items()})
    check("ot_never_right_boundary", sum(row["right_control"] == "OT" for row in assignments) == 0 and sum(row["left_control"] == "OT" for row in assignments) == 178, [])
    check("ol_direction_counts", sum(row["left_control"] == "OL" for row in assignments) == 63 and sum(row["right_control"] == "OL" for row in assignments) == 107 and sum(row["left_control"] == "OL" and row["right_control"] == "OL" for row in assignments) == 7, [])
    separated_ol = [row for row in assignments if "OL" in row["recipe"].split("+") and row["left_control"] != "OL" and row["right_control"] != "OL"]
    check("one_dy_separates_grade_from_ol", len(separated_ol) == 1 and separated_ol[0]["event_id"] == "G407-E1682" and separated_ol[0]["carrier_envelope"] == "START>G<DY", separated_ol)

    check("all_assignments_have_defaults", all(row["complete_carrier_reading_de"] and row["envelope_template_de"] for row in assignments), [])
    check("assignment_family_links", sum(row["multirung_family_id"] != "NONE" for row in assignments) == 235, sum(row["multirung_family_id"] != "NONE" for row in assignments))

    expected_result = {
        "status": "PASS_EIGHT_GRADE_ENVELOPES__151_VISIBLE_HOSTS_LICENSED__18_FALSE_CROSS_BOUNDARY_BINDS_AVOIDED",
        "source_marker_occurrence_count": 1870,
        "source_marker_event_count": 1656,
        "grade_state_event_count": 326,
        "grade_occurrence_count": 333,
        "grade_e_count": 214,
        "grade_ee_count": 114,
        "grade_eee_count": 5,
        "single_grade_event_count": 319,
        "double_grade_event_count": 7,
        "physical_page_count": 22,
        "statement_count": 222,
        "carrier_envelope_count": 8,
        "grade_state_projection_count": 25,
        "visible_same_block_host_count": 151,
        "visible_host_licensed_count": 151,
        "control_carried_grade_count": 182,
        "inherited_action_available_without_visible_host_count": 152,
        "cross_boundary_would_be_licensed_count": 134,
        "false_cross_boundary_bind_count": 18,
        "no_inherited_action_grade_count": 30,
        "ot_left_boundary_grade_count": 178,
        "grade_before_ot_boundary_count": 0,
        "ol_left_boundary_grade_count": 63,
        "ol_right_boundary_grade_count": 107,
        "ol_both_boundary_grade_count": 7,
        "grade_separated_from_only_ol_by_dy_count": 1,
        "multirung_family_count": 17,
        "complete_three_rung_family_count": 1,
        "multirung_family_event_count": 235,
        "multirung_dy_event_count": 94,
        "multirung_dy_final_count": 94,
        "multirung_non_dy_event_count": 141,
        "multirung_non_dy_final_count": 2,
        "all_assignments_have_default": True,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    check("book_contains_core_findings", all(token in book for token in ("333", "151", "18", "94/94", "2/141", "OT+G+DY")), len(book))

    deterministic = [ASSIGNMENT, ENVELOPE, PROJECTION, FAMILY, ORIENTATION, HAZARD, BOOK, RESULT]
    before = {path.name: digest(path) for path in deterministic}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {path.name: digest(path) for path in deterministic}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-1000:])
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    passed = sum(bool(item["passed"]) for item in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "check_count": len(checks), "passed_count": passed,
        "failed_count": len(checks) - passed,
        "input_sha256": {
            STATE_ATLAS.name: digest(STATE_ATLAS), OLD_CONTEXT.name: digest(OLD_CONTEXT),
            CURRENT_CONTEXT.name: digest(CURRENT_CONTEXT), HEAD_PROFILE.name: digest(HEAD_PROFILE),
            PAIR_PROFILE.name: digest(PAIR_PROFILE),
        },
        "artifact_sha256": after, "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
