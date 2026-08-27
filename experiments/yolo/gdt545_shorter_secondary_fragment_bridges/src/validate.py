#!/usr/bin/env python3
"""Independent validation for GDT545."""

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
BASE = ROOT / "experiments/yolo/gdt545_shorter_secondary_fragment_bridges"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G543 = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"
G544 = ROOT / "experiments/yolo/gdt544_flagged_equal_length_anchor_availability/artifacts"
OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
CARD_IN = G543 / "gdt543_81_fragment_extension_cards.tsv"
ARM_IN = G543 / "gdt543_93_directional_extension_arms.tsv"
FLAGGED_IN = G544 / "gdt544_16_flagged_target_anchor_availability.tsv"
CANDIDATE_OUT = OUT / "gdt545_12_shorter_anchor_candidates.tsv"
BRIDGE_OUT = OUT / "gdt545_4_secondary_bridge_cards.tsv"
UNREPAIRED_OUT = OUT / "gdt545_12_unrepaired_flagged_cards.tsv"
SUMMARY_OUT = OUT / "gdt545_shorter_bridge_summary.tsv"
BOOK_OUT = OUT / "GDT545_SHORTER_SECONDARY_BRIDGE_BOOK.md"
RESULT_OUT = OUT / "gdt545_result.json"
VALIDATION_OUT = OUT / "gdt545_validation.json"
RUNNER = BASE / "src/run.py"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_RANK = {
    "TARGET_MODE_SET_DISJOINT": 0,
    "TARGET_MODE_SET_OVERLAPS": 1,
    "TARGET_MODE_SET_INCLUDED": 2,
    "TARGET_MODE_SET_EQUAL": 3,
}
VISIBLE_RANK = {
    "NO_EXACT_OLD_SURFACE_STEM": 0,
    "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM": 1,
    "ALIGNED_EXACT_OLD_SURFACE_STEM": 2,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(recipe.split("+")) if recipe and recipe != "NONE" else tuple()


def render(parts: tuple[str, ...]) -> str:
    return "+".join(parts) if parts else "NONE"


def direction(start: int, width: int, total: int) -> str:
    if start and start + width < total:
        return "BOTH_SIDES"
    if start:
        return "LEFT_EXTENSION"
    if start + width < total:
        return "RIGHT_EXTENSION"
    return "NO_EXTENSION"


def mode(recipe: tuple[str, ...], state: dict[str, str]) -> str:
    action = not any(atom in ACTION_ROOTS for atom in recipe) and bool(state["action"])
    argument = not any(atom in ARGUMENT_ROOTS for atom in recipe) and bool(state["argument"])
    if action and argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if action:
        return "REQUIRES_ACTIVE_ACTION"
    if argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def relation(old: set[str], target: set[str]) -> str:
    if old == target:
        return "TARGET_MODE_SET_EQUAL"
    if target <= old:
        return "TARGET_MODE_SET_INCLUDED"
    if old & target:
        return "TARGET_MODE_SET_OVERLAPS"
    return "TARGET_MODE_SET_DISJOINT"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    old_events = read_tsv(OLD_EVENTS_IN)
    cards = read_tsv(CARD_IN)
    arms = read_tsv(ARM_IN)
    flagged_rows = read_tsv(FLAGGED_IN)
    candidates = read_tsv(CANDIDATE_OUT)
    bridges = read_tsv(BRIDGE_OUT)
    unrepaired = read_tsv(UNREPAIRED_OUT)
    summary = read_tsv(SUMMARY_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("old_event_count", len(old_events) == 4576, len(old_events))
    check("gdt543_card_count", len(cards) == 81, len(cards))
    check("gdt543_arm_count", len(arms) == 93, len(arms))
    check("gdt544_flagged_count", len(flagged_rows) == 16, len(flagged_rows))
    check("shorter_candidate_count", len(candidates) == 12, len(candidates))
    check("secondary_bridge_count", len(bridges) == 4, len(bridges))
    check("unrepaired_count", len(unrepaired) == 12, len(unrepaired))

    cards_by_surface = {row["surface"]: row for row in cards}
    flagged = {row["surface"] for row in flagged_rows}
    context_flags = {row["surface"] for row in cards if row["anchor_context_relation"] == "TARGET_MODE_SET_DISJOINT"}
    interface_flags = {row["target_surface"] for row in arms if int(row["old_interface_event_count"]) == 0}
    check("flag_union_replay", flagged == context_flags | interface_flags and len(flagged) == 16, sorted(flagged ^ (context_flags | interface_flags)))

    by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    surfaces_by_recipe: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        recipe = atoms(event["component_recipe"])
        by_recipe[recipe].append(event)
        surfaces_by_recipe[recipe][event["surface"]] += 1
        for pair in set(zip(recipe, recipe[1:])):
            pair_events[pair].append(event)

    before_event = {}
    states = {}
    for event in old_events:
        state = states.setdefault(event["source_statement_id"], {"action": "", "argument": ""})
        before_event[event["global_running_event_id"]] = dict(state)
        recipe = atoms(event["component_recipe"])
        actions = [atom for atom in recipe if atom in ACTION_ROOTS]
        arguments = [atom for atom in recipe if atom in ARGUMENT_ROOTS]
        if actions:
            state["action"] = actions[-1]
        if arguments:
            state["argument"] = arguments[-1]

    expected_inventory = set()
    for surface in flagged:
        card = cards_by_surface[surface]
        recipe = atoms(card["final_recipe"])
        primary_length = int(card["anchor_atom_count"])
        for width in range(2, primary_length):
            for start in range(len(recipe) - width + 1):
                anchor = recipe[start : start + width]
                if anchor in by_recipe:
                    expected_inventory.add((surface, render(anchor), start + 1))
    actual_inventory = {(row["surface"], row["shorter_anchor_recipe"], int(row["shorter_anchor_start_atom"])) for row in candidates}
    check("shorter_candidate_inventory_exact", expected_inventory == actual_inventory, sorted(expected_inventory ^ actual_inventory))
    check("shorter_candidate_owner_count", len({row["surface"] for row in candidates}) == 7, sorted({row["surface"] for row in candidates}))

    replay_failures = []
    for row in candidates:
        surface = row["surface"]
        card = cards_by_surface[surface]
        recipe = atoms(card["final_recipe"])
        anchor = atoms(row["shorter_anchor_recipe"])
        start = int(row["shorter_anchor_start_atom"]) - 1
        candidate_direction = direction(start, len(anchor), len(recipe))
        visible_rank = 0
        for old_surface in surfaces_by_recipe[anchor]:
            search_from = 0
            while True:
                char_start = surface.find(old_surface, search_from)
                if char_start < 0:
                    break
                visible_rank = max(visible_rank, 2 if direction(char_start, len(old_surface), len(surface)) == candidate_direction else 1)
                search_from = char_start + 1
        boundaries = []
        if start:
            boundaries.append((recipe[start - 1], recipe[start]))
        if start + len(anchor) < len(recipe):
            boundaries.append((recipe[start + len(anchor) - 1], recipe[start + len(anchor)]))
        supported = sum(bool(pair_events[pair]) for pair in boundaries)
        target_modes = set(card["observed_requirement_modes"].split("|"))
        old_modes = {mode(recipe, before_event[event["global_running_event_id"]]) for event in by_recipe[anchor]}
        expected_relation = relation(old_modes, target_modes)
        if (
            recipe[start : start + len(anchor)] != anchor
            or int(row["visible_rank"]) != visible_rank
            or int(row["shorter_supported_interfaces"]) != supported
            or row["shorter_anchor_context_relation"] != expected_relation
            or int(row["old_anchor_event_count"]) != len(by_recipe[anchor])
        ):
            replay_failures.append((surface, row["shorter_anchor_recipe"]))
    check("shorter_candidate_metric_replay", not replay_failures, replay_failures)

    qualification_failures = []
    for row in candidates:
        base_fraction = int(row["primary_supported_interfaces"]) / int(row["primary_interface_count"])
        new_fraction = int(row["shorter_supported_interfaces"]) / int(row["shorter_interface_count"])
        visible_nonworse = int(row["visible_rank"]) >= int(row["primary_visible_rank"])
        context_nonworse = int(row["shorter_context_rank"]) >= int(row["primary_context_rank"])
        interface_nonworse = new_fraction >= base_fraction
        context_repair = row["surface"] in context_flags and int(row["shorter_context_rank"]) > int(row["primary_context_rank"])
        interface_repair = row["surface"] in interface_flags and row["all_shorter_interfaces_old"] == "YES" and int(row["primary_supported_interfaces"]) < int(row["primary_interface_count"])
        qualifies = visible_nonworse and context_nonworse and interface_nonworse and (context_repair or interface_repair)
        if (row["qualifies_as_secondary_bridge"] == "YES") != qualifies:
            qualification_failures.append((row["surface"], row["shorter_anchor_recipe"]))
    check("qualification_replay", not qualification_failures, qualification_failures)
    qualified = [row for row in candidates if row["qualifies_as_secondary_bridge"] == "YES"]
    check("qualified_candidate_and_target_counts", (len(qualified), len({row["surface"] for row in qualified})) == (6, 4), [len(qualified), len({row["surface"] for row in qualified})])

    candidate_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidate_groups[row["surface"]].append(row)
    selection_failures = []
    selected = {}
    for surface, rows in candidate_groups.items():
        good = [row for row in rows if row["qualifies_as_secondary_bridge"] == "YES"]
        if not good:
            continue
        expected = sorted(good, key=lambda row: (
            -int(row["visible_rank"]), -int(row["shorter_context_rank"]),
            row["all_shorter_interfaces_old"] != "YES", -int(row["shorter_anchor_atom_count"]),
            -int(row["old_anchor_event_count"]),
            -len(row["best_visible_stem_surface"] if row["best_visible_stem_surface"] != "NONE" else ""),
            int(row["shorter_anchor_start_atom"]), row["shorter_anchor_recipe"],
        ))[0]
        chosen = [row for row in rows if row["selected_secondary_bridge"] == "YES"]
        if chosen != [expected]:
            selection_failures.append(surface)
        selected[surface] = expected
    check("secondary_selection_replay", not selection_failures and len(selected) == 4, selection_failures)
    check("selected_bridge_inventory", {(row["surface"], row["secondary_anchor_recipe"]) for row in bridges} == {
        ("chckhedy", "CH+K"), ("chepakeo", "E+O"), ("chepos", "CH+E"), ("tosheo", "SH+E")
    }, [(row["surface"], row["secondary_anchor_recipe"]) for row in bridges])
    check("selected_context_equal", all(row["secondary_context_relation"] == "TARGET_MODE_SET_EQUAL" for row in bridges), [(row["surface"], row["secondary_context_relation"]) for row in bridges])
    check("selected_interfaces_all_old", all(row["secondary_supported_interfaces"] == row["secondary_interface_count"] for row in bridges), [(row["surface"], row["secondary_supported_interfaces"], row["secondary_interface_count"]) for row in bridges])
    visible_distribution = Counter(row["secondary_visible_stem_status"] for row in bridges)
    check("selected_visible_distribution", visible_distribution == Counter({"ALIGNED_EXACT_OLD_SURFACE_STEM": 3, "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM": 1}), dict(sorted(visible_distribution.items())))
    repair_distribution = Counter(row["repaired_dimension"] for row in bridges)
    check("repair_dimension_distribution", repair_distribution == Counter({"CONTEXT": 3, "INTERFACE": 1}), dict(sorted(repair_distribution.items())))

    bridge_surfaces = {row["surface"] for row in bridges}
    check("unrepaired_surface_set", {row["surface"] for row in unrepaired} == flagged - bridge_surfaces, sorted({row["surface"] for row in unrepaired} ^ (flagged - bridge_surfaces)))
    no_candidate = [row for row in unrepaired if int(row["shorter_exact_multiatom_candidate_count"]) == 0]
    unqualified_candidate = [row for row in unrepaired if int(row["shorter_exact_multiatom_candidate_count"]) > 0]
    check("unrepaired_subclasses", (len(no_candidate), len(unqualified_candidate)) == (9, 3), [len(no_candidate), len(unqualified_candidate)])
    check("primary_anchors_retained", all(row["decision"] == "ADD_SECONDARY_BRIDGE__RETAIN_PRIMARY_LONGEST_ANCHOR" and row["retained_primary_anchor_recipe"] == cards_by_surface[row["surface"]]["anchor_recipe"] for row in bridges), [(row["surface"], row["retained_primary_anchor_recipe"]) for row in bridges])

    summary_map = {row["metric"]: row["value"] for row in summary}
    check("summary_core_metrics", all(summary_map.get(key) == value for key, value in {
        "flagged_target_count": "16", "shorter_exact_multiatom_candidate_count": "12",
        "qualified_shorter_candidate_count": "6", "selected_secondary_bridge_count": "4",
        "unrepaired_flagged_target_count": "12", "primary_anchor_changes": "0",
    }.items()), summary_map)
    book = BOOK_OUT.read_text(encoding="utf-8")
    check("book_status", result["status"] in book, result["status"])
    check("book_bridge_inventory", all(f"`{surface}`" in book for surface in bridge_surfaces), sorted(bridge_surfaces))
    check("book_unrepaired_inventory", all(f"`{row['surface']}`" in book for row in unrepaired), len(unrepaired))

    expected_result = {
        "status": "FOUR_FLAGGED_TARGETS_GAIN_SHORTER_SECONDARY_BRIDGES__TWELVE_DEFAULTS_REMAIN",
        "flagged_target_count": 16,
        "shorter_exact_multiatom_candidate_count": 12,
        "flagged_target_with_shorter_candidate_count": 7,
        "qualified_shorter_candidate_count": 6,
        "qualified_target_count": 4,
        "selected_secondary_bridge_count": 4,
        "context_secondary_bridge_count": 3,
        "interface_secondary_bridge_count": 1,
        "selected_secondary_surface_count": 4,
        "selected_secondary_all_context_equal_count": 4,
        "selected_secondary_all_interfaces_old_count": 4,
        "selected_secondary_aligned_visible_count": 3,
        "selected_secondary_direction_mismatch_visible_count": 1,
        "unrepaired_flagged_target_count": 12,
        "unrepaired_with_no_shorter_candidate_count": 9,
        "unrepaired_with_unqualified_shorter_candidates_count": 3,
        "primary_anchor_changes": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated = [CANDIDATE_OUT, BRIDGE_OUT, UNREPAIRED_OUT, SUMMARY_OUT, BOOK_OUT, RESULT_OUT]
    before = {path.name: digest(path) for path in generated}
    rerun = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    after = {path.name: digest(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout)
    check("generator_byte_determinism", before == after, after)

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
