#!/usr/bin/env python3
"""Validate GDT559 counts, carrier rules, and deterministic artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt559_validation.json"
INPUTS = {
    "gdt557_all_state_marker_occurrences.tsv": ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts/gdt557_all_state_marker_occurrences.tsv",
    "gdt416_4576_imperative_clauses.tsv": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
    "gdt539_546_contextual_prose_events.tsv": ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts/gdt539_546_contextual_prose_events.tsv",
    "gdt429_13_nonaction_core_contrasts.tsv": ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_13_nonaction_core_contrasts.tsv",
}
ARTIFACTS = {
    "gdt559_390_argument_carrier_assignments.tsv": OUT / "gdt559_390_argument_carrier_assignments.tsv",
    "gdt559_4_argument_root_profiles.tsv": OUT / "gdt559_4_argument_root_profiles.tsv",
    "gdt559_6_argument_carrier_envelopes.tsv": OUT / "gdt559_6_argument_carrier_envelopes.tsv",
    "gdt559_24_argument_state_projections.tsv": OUT / "gdt559_24_argument_state_projections.tsv",
    "gdt559_11_multiroot_substitution_families.tsv": OUT / "gdt559_11_multiroot_substitution_families.tsv",
    "gdt559_6_argument_pair_bridges.tsv": OUT / "gdt559_6_argument_pair_bridges.tsv",
    "gdt559_341_left_controlled_successor_transitions.tsv": OUT / "gdt559_341_left_controlled_successor_transitions.tsv",
    "gdt559_8_successor_transition_profiles.tsv": OUT / "gdt559_8_successor_transition_profiles.tsv",
    "gdt559_28_y_dy_joint_cards.tsv": OUT / "gdt559_28_y_dy_joint_cards.tsv",
    "gdt559_4_y_dy_distinction_classes.tsv": OUT / "gdt559_4_y_dy_distinction_classes.tsv",
    "GDT559_ARGUMENT_CARRIER_BOOK.md": OUT / "GDT559_ARGUMENT_CARRIER_BOOK.md",
    "gdt559_result.json": OUT / "gdt559_result.json",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    state = read_tsv(INPUTS["gdt557_all_state_marker_occurrences.tsv"])
    old = read_tsv(INPUTS["gdt416_4576_imperative_clauses.tsv"])
    current = read_tsv(INPUTS["gdt539_546_contextual_prose_events.tsv"])
    contrasts = read_tsv(INPUTS["gdt429_13_nonaction_core_contrasts.tsv"])
    assignments = read_tsv(ARTIFACTS["gdt559_390_argument_carrier_assignments.tsv"])
    roots = read_tsv(ARTIFACTS["gdt559_4_argument_root_profiles.tsv"])
    envelopes = read_tsv(ARTIFACTS["gdt559_6_argument_carrier_envelopes.tsv"])
    projections = read_tsv(ARTIFACTS["gdt559_24_argument_state_projections.tsv"])
    families = read_tsv(ARTIFACTS["gdt559_11_multiroot_substitution_families.tsv"])
    pairs = read_tsv(ARTIFACTS["gdt559_6_argument_pair_bridges.tsv"])
    transitions = read_tsv(ARTIFACTS["gdt559_341_left_controlled_successor_transitions.tsv"])
    transition_profiles = read_tsv(ARTIFACTS["gdt559_8_successor_transition_profiles.tsv"])
    joint = read_tsv(ARTIFACTS["gdt559_28_y_dy_joint_cards.tsv"])
    distinction = read_tsv(ARTIFACTS["gdt559_4_y_dy_distinction_classes.tsv"])
    result = json.loads(ARTIFACTS["gdt559_result.json"].read_text(encoding="utf-8"))

    check("input_counts", (len(state), len(old), len(current), len(contrasts)) == (1870, 4576, 546, 13), [len(state), len(old), len(current), len(contrasts)])
    source_pages = {row["physical_page"] for row in state}
    check("source_pages_exclude_f84", not any(page.startswith("f84") for page in source_pages), sorted(page for page in source_pages if page.startswith("f84")))
    check("source_event_deduplication", len({row["event_id"] for row in state}) == 1656, len({row["event_id"] for row in state}))
    check("context_union", len(old) + len(current) == 5122 and not ({row["global_running_event_id"] for row in old} & {row["event_id"] for row in current}), [len(old) + len(current)])
    check("artifact_row_counts", [len(assignments), len(roots), len(envelopes), len(projections), len(families), len(pairs), len(transitions), len(transition_profiles), len(joint), len(distinction)] == [390, 4, 6, 24, 11, 6, 341, 8, 28, 4], [len(assignments), len(roots), len(envelopes), len(projections), len(families), len(pairs), len(transitions), len(transition_profiles), len(joint), len(distinction)])
    assignment_keys = {(row["event_id"], row["argument_occurrence_in_recipe"]) for row in assignments}
    check("assignment_keys_unique", len(assignment_keys) == 390, len(assignment_keys))
    check("assignment_ordinals", [int(row["assignment_ordinal"]) for row in assignments] == list(range(1, 391)), [assignments[0]["assignment_ordinal"], assignments[-1]["assignment_ordinal"]])
    root_counts = Counter(row["argument"] for row in assignments)
    check("argument_counts", root_counts == Counter({"Y": 268, "AIIN": 54, "AIN": 34, "OR": 34}), root_counts)
    multiplicity = Counter(int(row["argument_multiplicity_in_recipe"]) for row in assignments)
    check("argument_multiplicity", multiplicity == Counter({1: 374, 2: 16}), multiplicity)
    event_multiplicity = Counter()
    for row in assignments:
        event_multiplicity[row["event_id"]] = int(row["argument_multiplicity_in_recipe"])
    check("selected_event_partition", len(event_multiplicity) == 382 and Counter(event_multiplicity.values()) == Counter({1: 374, 2: 8}), [len(event_multiplicity), Counter(event_multiplicity.values())])

    expected_envelopes = {
        "OT>A<END": (185, 118, 28, 18, 21),
        "OL>A<END": (156, 105, 26, 15, 10),
        "START>A<DY": (31, 28, 0, 1, 2),
        "START>A<OL": (16, 15, 0, 0, 1),
        "OT>A<OL": (1, 1, 0, 0, 0),
        "OL>A<OL": (1, 1, 0, 0, 0),
    }
    observed_envelopes = {
        row["carrier_envelope"]: tuple(int(row[key]) for key in ("argument_occurrence_count", "y_count", "aiin_count", "ain_count", "or_count"))
        for row in envelopes
    }
    check("six_envelopes_exact", observed_envelopes == expected_envelopes, observed_envelopes)
    check("left_right_control_counts", sum(row["left_control"] == "OT" for row in assignments) == 186 and sum(row["left_control"] == "OL" for row in assignments) == 157 and sum(row["right_control"] == "OL" for row in assignments) == 18 and sum(row["right_control"] == "DY" for row in assignments) == 31, [sum(row["left_control"] == "OT" for row in assignments), sum(row["left_control"] == "OL" for row in assignments), sum(row["right_control"] == "OL" for row in assignments), sum(row["right_control"] == "DY" for row in assignments)])
    check("all_assignments_have_defaults", all(row["complete_carrier_reading_de"] and row["complete_carrier_reading_de"] != "UNRESOLVED" for row in assignments), [])
    check("all_six_envelope_templates_present", all(row["working_template_de"] for row in envelopes), [])

    projection_count = sum(int(row["event_count"]) for row in projections)
    projection_occurrences = sum(int(row["argument_occurrence_count"]) for row in projections)
    check("twenty_four_projections_cover_population", projection_count == 382 and projection_occurrences == 390, [projection_count, projection_occurrences])
    projection_map = {row["argument_state_projection"]: int(row["event_count"]) for row in projections}
    check("dominant_projection_counts", {key: projection_map[key] for key in ("OT+Y", "OL+Y", "Y+DY", "OT+AIIN", "OL+AIIN")} == {"OT+Y": 117, "OL+Y": 96, "Y+DY": 28, "OT+AIIN": 28, "OL+AIIN": 22}, {key: projection_map[key] for key in ("OT+Y", "OL+Y", "Y+DY", "OT+AIIN", "OL+AIIN")})
    check("all_projections_have_defaults", all(row["literal_working_reading_de"] for row in projections), [])

    expected_families = {
        "OT+ARG": (4, 88), "OL+ARG": (4, 59), "OT+E+ARG": (3, 24),
        "OL+K+ARG": (3, 11), "OT+AL+ARG": (3, 5), "OT+EE+ARG": (2, 24),
        "OT+CH+ARG": (2, 8), "OL+SH+E+ARG": (2, 3), "S+OT+ARG": (2, 3),
        "D_ADDR+OL+K+ARG": (2, 2), "SH+E+OL+ARG": (2, 2),
    }
    observed_families = {row["normalized_recipe"]: (int(row["argument_variant_count"]), int(row["event_count"])) for row in families}
    check("eleven_families_exact", observed_families == expected_families, observed_families)
    family_ids = {event_id for row in families for event_id in row["event_ids"].split("|")}
    check("family_event_coverage", len(family_ids) == 229 and sum(row["substitution_family_id"] == "NONE" for row in assignments) == 161, [len(family_ids), sum(row["substitution_family_id"] == "NONE" for row in assignments)])
    complete = {row["normalized_recipe"]: row["argument_variants"] for row in families if row["family_status"] == "COMPLETE_FOUR_ARGUMENT_FRAME"}
    check("two_complete_bare_frames", complete == {"OT+ARG": "Y|AIIN|AIN|OR", "OL+ARG": "Y|AIIN|AIN|OR"}, complete)
    check("family_scope_fixed", all(row["scope_result"] == "ARGUMENT_VALUE_SUBSTITUTES_INSIDE_FIXED_CONTROL_FRAME" for row in families), [])

    pair_family_counts = {row["argument_pair"]: int(row["gdt559_state_family_count"]) for row in pairs}
    check("six_pair_bridge_counts", pair_family_counts == {"Y~AIIN": 6, "Y~AIN": 5, "Y~OR": 7, "AIIN~AIN": 3, "AIIN~OR": 3, "AIN~OR": 3}, pair_family_counts)
    check("all_pairs_share_bare_frames", all(row["shared_bare_ot_argument_frame"] == "YES" and row["shared_bare_ol_argument_frame"] == "YES" for row in pairs), [])
    old_argument_pairs = {frozenset(row["contrast_pair"].split("~")) for row in contrasts if row["family"] == "ARGUMENT"}
    new_argument_pairs = {frozenset(row["argument_pair"].split("~")) for row in pairs}
    check("gdt429_pair_crosswalk_complete", old_argument_pairs == new_argument_pairs and len(new_argument_pairs) == 6, [len(old_argument_pairs), len(new_argument_pairs)])

    outcomes = Counter(row["successor_outcome"] for row in transitions)
    check("successor_partition", outcomes == Counter({"NEXT_EXPLICIT_ARGUMENT_RESETS_CARRIER": 173, "NEXT_INHERITS_CURRENT_ARGUMENT": 157, "NO_SUCCESSOR_STATEMENT_END": 11}), outcomes)
    inherited_ok = all(row["next_explicit_arguments"] == "NONE" and row["next_inherited_argument"] == row["last_argument"] for row in transitions if row["successor_outcome"] == "NEXT_INHERITS_CURRENT_ARGUMENT")
    check("all_implicit_successors_inherit_current", inherited_ok, [])
    explicit_ok = all(row["next_explicit_arguments"] != "NONE" for row in transitions if row["successor_outcome"] == "NEXT_EXPLICIT_ARGUMENT_RESETS_CARRIER")
    check("all_explicit_successors_reset_visibly", explicit_ok, [])
    terminal_ok = all(row["next_event_id"] == "NONE" and row["statement_final"] == "YES" for row in transitions if row["successor_outcome"] == "NO_SUCCESSOR_STATEMENT_END")
    check("all_no_successors_are_statement_ends", terminal_ok, [])
    check("transition_profiles_complete", len(transition_profiles) == 8 and sum(int(row["transition_count"]) for row in transition_profiles) == 341 and sum(int(row["mismatch_count"]) for row in transition_profiles) == 0, [sum(int(row["transition_count"]) for row in transition_profiles), sum(int(row["mismatch_count"]) for row in transition_profiles)])

    distinction_counts = {row["distinction_class"]: int(row["event_count"]) for row in distinction}
    check("y_dy_four_classes_exact", distinction_counts == {"Y_ONLY": 235, "DY_ONLY": 677, "Y_AND_DY": 28, "NEITHER_Y_NOR_DY": 716}, distinction_counts)
    check("joint_y_dy_written_order", len(joint) == 28 and all(int(row["y_atom_position"]) < int(row["dy_atom_position"]) and row["written_order"] == "Y_BEFORE_DY" for row in joint), [])
    check("joint_y_dy_scope", sum(row["statement_final"] == "YES" for row in joint) == 27 and [row["event_id"] for row in joint if row["statement_final"] == "NO"] == ["G407-E0133"], [sum(row["statement_final"] == "YES" for row in joint), [row["event_id"] for row in joint if row["statement_final"] == "NO"]])
    check("y_dy_defaults_present", all(row["default_reading_de"] for row in distinction) and all(row["distinction"] == "Y_ARGUMENT_POSTEN__THEN_DY_CLOSE_CONTROL" for row in joint), [])

    expected_result = {
        "argument_state_event_count": 382, "argument_occurrence_count": 390,
        "carrier_envelope_count": 6, "argument_state_projection_count": 24,
        "left_ot_or_ol_argument_count": 343,
        "multiroot_substitution_family_count": 11,
        "complete_four_argument_family_count": 2,
        "multiroot_family_event_count": 229,
        "left_controlled_transition_count": 341,
        "implicit_successor_inherits_current_count": 157,
        "explicit_successor_argument_reset_count": 173,
        "successor_argument_mismatch_count": 0,
        "argument_dy_event_count": 31,
        "argument_dy_statement_final_count": 30,
        "argument_no_dy_event_count": 351,
        "argument_no_dy_statement_final_count": 12,
        "y_dy_joint_event_count": 28,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("zero_scope_mutation", all(result.get(key) == 0 for key in ("new_pages", "recipe_changes", "root_meaning_changes", "statement_boundary_changes")), {key: result.get(key) for key in ("new_pages", "recipe_changes", "root_meaning_changes", "statement_boundary_changes")})
    book = ARTIFACTS["GDT559_ARGUMENT_CARRIER_BOOK.md"].read_text(encoding="utf-8")
    check("book_contains_core_findings", all(needle in book for needle in ("`OT+ARG` (88 Karten)", "`OL+ARG` (59 Karten)", "157/157", "Y ist nicht DY", "Alle24 geschriebenen Steuerfolgen")), len(book))

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr)
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    payload = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
