#!/usr/bin/env python3
"""Independent validation for GDT543."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
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
BASE = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
G542 = ROOT / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"

OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS_IN = G407 / "gdt407_715_statement_edition.tsv"
CONTRACT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
TIER_IN = G542 / "gdt542_145_final_support_tiers.tsv"
CARD_OUT = OUT / "gdt543_81_fragment_extension_cards.tsv"
CANDIDATE_OUT = OUT / "gdt543_104_longest_anchor_candidates.tsv"
ARM_OUT = OUT / "gdt543_93_directional_extension_arms.tsv"
CHANNEL_OUT = OUT / "gdt543_53_visible_affix_channels.tsv"
SUPERCARD_OUT = OUT / "gdt543_19_old_supercard_reductions.tsv"
FAMILY_OUT = OUT / "gdt543_16_recurrent_anchor_families.tsv"
SUMMARY_OUT = OUT / "gdt543_fragment_extension_summary.tsv"
BOOK_OUT = OUT / "GDT543_FRAGMENT_EXTENSION_BOOK.md"
RESULT_OUT = OUT / "gdt543_result.json"
VALIDATION_OUT = OUT / "gdt543_validation.json"
RUNNER = BASE / "src/run.py"
READER = BASE / "src/fragment_extension.py"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def atoms(recipe: str) -> tuple[str, ...]:
    if not recipe or recipe == "NONE":
        return tuple()
    return tuple(recipe.split("+"))


def render(parts: tuple[str, ...]) -> str:
    return "+".join(parts) if parts else "NONE"


def positions(big: tuple[str, ...], small: tuple[str, ...]) -> list[int]:
    return [
        start
        for start in range(len(big) - len(small) + 1)
        if big[start : start + len(small)] == small
    ] if small and len(small) <= len(big) else []


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
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    contracts = read_tsv(CONTRACT_IN)
    tiers = read_tsv(TIER_IN)
    cards = read_tsv(CARD_OUT)
    candidates = read_tsv(CANDIDATE_OUT)
    arms = read_tsv(ARM_OUT)
    channels = read_tsv(CHANNEL_OUT)
    supercards = read_tsv(SUPERCARD_OUT)
    families = read_tsv(FAMILY_OUT)
    summary = read_tsv(SUMMARY_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("old_event_count", len(old_events) == 4576, len(old_events))
    check("old_statement_count", len(old_statements) == 715, len(old_statements))
    check("contract_count", len(contracts) == 145, len(contracts))
    check("tier_count", len(tiers) == 145, len(tiers))
    fragment_targets = {
        row["surface"]: row
        for row in tiers
        if row["final_support_tier"] == "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
    }
    check("fragment_target_count", len(fragment_targets) == 81, len(fragment_targets))
    check("card_count", len(cards) == 81, len(cards))
    check("candidate_count", len(candidates) == 104, len(candidates))
    check("arm_count", len(arms) == 93, len(arms))
    check("channel_count", len(channels) == 53, len(channels))
    check("supercard_row_count", len(supercards) == 19, len(supercards))
    check("family_count", len(families) == 16, len(families))
    check("card_surface_set", set(fragment_targets) == {row["surface"] for row in cards}, sorted(set(fragment_targets) ^ {row["surface"] for row in cards}))

    by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    surface_counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    event_by_id = {}
    for event in old_events:
        recipe = atoms(event["component_recipe"])
        by_recipe[recipe].append(event)
        surface_counts[recipe][event["surface"]] += 1
        event_by_id[event["global_running_event_id"]] = event
        for pair in set(zip(recipe, recipe[1:])):
            pair_events[pair].append(event)

    expected_candidates = set()
    for surface, target in fragment_targets.items():
        recipe = atoms(target["final_recipe"])
        longest = int(target["final_longest_old_fragment_atoms"])
        for start in range(len(recipe) - longest + 1):
            anchor = recipe[start : start + longest]
            if anchor in by_recipe:
                expected_candidates.add((surface, start + 1, render(anchor)))
    actual_candidates = {
        (row["surface"], int(row["anchor_start_atom"]), row["anchor_recipe"])
        for row in candidates
    }
    check("candidate_inventory_exact", expected_candidates == actual_candidates, sorted(expected_candidates ^ actual_candidates))

    candidate_replay_failures = []
    selected_by_surface = {}
    candidate_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidate_groups[row["surface"]].append(row)
        if row["selected"] == "YES":
            selected_by_surface[row["surface"]] = row
        target_recipe = atoms(row["final_recipe"])
        anchor = atoms(row["anchor_recipe"])
        start = int(row["anchor_start_atom"]) - 1
        boundaries = []
        if start:
            boundaries.append((target_recipe[start - 1], target_recipe[start]))
        if start + len(anchor) < len(target_recipe):
            boundaries.append((target_recipe[start + len(anchor) - 1], target_recipe[start + len(anchor)]))
        expected_supported = sum(bool(pair_events[pair]) for pair in boundaries)
        if (
            target_recipe[start : start + len(anchor)] != anchor
            or anchor not in by_recipe
            or int(row["old_anchor_event_count"]) != len(by_recipe[anchor])
            or int(row["old_supported_interface_count"]) != expected_supported
        ):
            candidate_replay_failures.append((row["surface"], row["anchor_recipe"], start + 1))
    check("candidate_metric_replay", not candidate_replay_failures, candidate_replay_failures)
    check("one_selected_candidate_per_target", len(selected_by_surface) == 81 and all(sum(row["selected"] == "YES" for row in group) == 1 for group in candidate_groups.values()), len(selected_by_surface))

    selection_failures = []
    for surface, group in candidate_groups.items():
        chosen = sorted(
            group,
            key=lambda row: (
                int(row["aligned_visible_match_count"]) == 0,
                row["all_interfaces_old"] != "YES",
                -int(row["old_supported_interface_count"]),
                -int(row["old_anchor_event_count"]),
                -len(row["best_visible_stem_surface"] if row["best_visible_stem_surface"] != "NONE" else ""),
                int(row["anchor_start_atom"]),
                row["anchor_recipe"],
            ),
        )[0]
        if chosen["selected"] != "YES":
            selection_failures.append(surface)
    check("canonical_selection_replay", not selection_failures, selection_failures)

    card_by_surface = {row["surface"]: row for row in cards}
    card_anchor_failures = []
    visible_failures = []
    visible_counts = Counter()
    for surface, card in card_by_surface.items():
        chosen = selected_by_surface[surface]
        if (
            card["anchor_recipe"] != chosen["anchor_recipe"]
            or card["anchor_start_atom"] != chosen["anchor_start_atom"]
            or card["old_anchor_event_count"] != chosen["old_anchor_event_count"]
        ):
            card_anchor_failures.append(surface)
        anchor = atoms(card["anchor_recipe"])
        target_recipe = atoms(card["final_recipe"])
        start = int(card["anchor_start_atom"]) - 1
        status = card["visible_stem_status"]
        visible_counts[status] += 1
        exact_matches = []
        for old_surface in surface_counts[anchor]:
            search_from = 0
            while True:
                char_start = surface.find(old_surface, search_from)
                if char_start < 0:
                    break
                exact_matches.append((old_surface, char_start, direction(char_start, len(old_surface), len(surface))))
                search_from = char_start + 1
        expected_direction = direction(start, len(anchor), len(target_recipe))
        aligned = [match for match in exact_matches if match[2] == expected_direction]
        if status == "ALIGNED_EXACT_OLD_SURFACE_STEM":
            ok = any(match[0] == card["visible_stem_surface"] for match in aligned)
        elif status == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM":
            ok = bool(exact_matches) and not aligned
        else:
            ok = not exact_matches
        if not ok:
            visible_failures.append(surface)
    check("card_selected_anchor_replay", not card_anchor_failures, card_anchor_failures)
    check("visible_stem_replay", not visible_failures, visible_failures)
    check("visible_stem_distribution", dict(visible_counts) == {
        "ALIGNED_EXACT_OLD_SURFACE_STEM": 72,
        "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM": 1,
        "NO_EXACT_OLD_SURFACE_STEM": 8,
    }, dict(visible_counts))

    arms_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    arm_failures = []
    for arm in arms:
        arms_by_surface[arm["target_surface"]].append(arm)
        card = card_by_surface[arm["target_surface"]]
        anchor = atoms(arm["anchor_recipe"])
        extension = atoms(arm["extension_recipe"])
        pair = tuple(arm["interface_pair"].split(">"))
        expected_pair = (extension[-1], anchor[0]) if arm["side"] == "LEFT" else (anchor[-1], extension[0])
        if pair != expected_pair or int(arm["old_interface_event_count"]) != len(pair_events[pair]):
            arm_failures.append((arm["target_surface"], arm["side"], arm["interface_pair"]))
        max_depth = 0
        for depth in range(1, len(extension) + 1):
            sequence = extension[-depth:] + anchor if arm["side"] == "LEFT" else anchor + extension[:depth]
            if any(positions(old_recipe, sequence) for old_recipe in by_recipe):
                max_depth = depth
        if int(arm["deepest_joint_extension_atoms"]) != max_depth:
            arm_failures.append((arm["target_surface"], arm["side"], "depth"))
    check("arm_and_interface_replay", not arm_failures, arm_failures)
    reconstruction_failures = []
    for surface, card in card_by_surface.items():
        left = atoms(card["left_extension_recipe"])
        anchor = atoms(card["anchor_recipe"])
        right = atoms(card["right_extension_recipe"])
        expected_sides = ({"LEFT"} if left else set()) | ({"RIGHT"} if right else set())
        actual_sides = {arm["side"] for arm in arms_by_surface[surface]}
        if left + anchor + right != atoms(card["final_recipe"]) or expected_sides != actual_sides:
            reconstruction_failures.append(surface)
    check("card_arm_reconstruction", not reconstruction_failures, reconstruction_failures)
    check("interface_support_count", sum(int(row["old_interface_event_count"]) > 0 for row in arms) == 87, sum(int(row["old_interface_event_count"]) > 0 for row in arms))
    check("joint_extension_counts", (sum(int(row["deepest_joint_extension_atoms"]) > 0 for row in arms), sum(row["full_arm_seen_with_anchor"] == "YES" for row in arms)) == (28, 15), [sum(int(row["deepest_joint_extension_atoms"]) > 0 for row in arms), sum(row["full_arm_seen_with_anchor"] == "YES" for row in arms)])

    observed_channels: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    observed_targets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for arm in arms:
        affix = arm["aligned_visible_affix"]
        if affix != "NONE":
            key = (arm["side"], affix)
            observed_channels[key][arm["extension_recipe"]] += 1
            observed_targets[key].add(arm["target_surface"])
    channel_by_key = {(row["side"], row["visible_affix"]): row for row in channels}
    channel_failures = []
    for key, recipes in observed_channels.items():
        row = channel_by_key.get(key)
        expected_class = "REPEATED_INVARIANT_VISIBLE_CHANNEL" if sum(recipes.values()) >= 2 and len(recipes) == 1 else "REPEATED_AMBIGUOUS_VISIBLE_CHANNEL" if sum(recipes.values()) >= 2 else "SINGLETON_VISIBLE_CHANNEL"
        if not row or int(row["observation_count"]) != sum(recipes.values()) or int(row["recipe_extension_variant_count"]) != len(recipes) or row["channel_class"] != expected_class:
            channel_failures.append(key)
    check("channel_replay", set(channel_by_key) == set(observed_channels) and not channel_failures, channel_failures)
    channel_classes = Counter(row["channel_class"] for row in channels)
    check("channel_class_counts", channel_classes["REPEATED_INVARIANT_VISIBLE_CHANNEL"] == 13 and channel_classes["REPEATED_AMBIGUOUS_VISIBLE_CHANNEL"] == 1, dict(channel_classes))
    dy = channel_by_key.get(("RIGHT", "dy"), {})
    check("right_dy_ambiguity", dy.get("recipe_extension_counts") == "DY:5|D_ADDR+Y:1" and dy.get("channel_class") == "REPEATED_AMBIGUOUS_VISIBLE_CHANNEL", dy)
    repeated_targets = {arm["target_surface"] for arm in arms if arm["visible_channel_class"] == "REPEATED_INVARIANT_VISIBLE_CHANNEL"}
    check("repeated_channel_target_count", len(repeated_targets) == 34, len(repeated_targets))

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

    context_failures = []
    context_counts = Counter()
    for surface, card in card_by_surface.items():
        recipe = atoms(card["final_recipe"])
        anchor = atoms(card["anchor_recipe"])
        old_modes = {mode(recipe, before_event[event["global_running_event_id"]]) for event in by_recipe[anchor]}
        target_modes = set(card["observed_requirement_modes"].split("|"))
        expected_relation = relation(old_modes, target_modes)
        context_counts[expected_relation] += 1
        rendered_modes = "|".join(sorted(old_modes, key=MODE_ORDER.__getitem__))
        if expected_relation != card["anchor_context_relation"] or rendered_modes != card["anchor_context_modes"]:
            context_failures.append(surface)
    check("anchor_context_replay", not context_failures, context_failures)
    check("anchor_context_distribution", dict(context_counts) == {
        "TARGET_MODE_SET_EQUAL": 53,
        "TARGET_MODE_SET_INCLUDED": 16,
        "TARGET_MODE_SET_DISJOINT": 12,
    }, dict(context_counts))

    expected_supercards = set()
    supercard_modes_by_target: dict[str, set[str]] = defaultdict(set)
    supercard_failures = []
    for surface, card in card_by_surface.items():
        target_recipe = atoms(card["final_recipe"])
        for old_recipe, events in by_recipe.items():
            if len(old_recipe) <= len(target_recipe):
                continue
            for start in positions(old_recipe, target_recipe):
                for event in events:
                    expected_supercards.add((surface, event["global_running_event_id"], start + 1))
                    supercard_modes_by_target[surface].add(mode(target_recipe, before_event[event["global_running_event_id"]]))
    actual_supercards = {(row["target_surface"], row["old_event_id"], int(row["target_start_atom"])) for row in supercards}
    for row in supercards:
        event = event_by_id.get(row["old_event_id"])
        target_recipe = atoms(row["target_recipe"])
        start = int(row["target_start_atom"]) - 1
        if not event or atoms(event["component_recipe"])[start : start + len(target_recipe)] != target_recipe or row["reduced_target_context_mode"] != mode(target_recipe, before_event[row["old_event_id"]]):
            supercard_failures.append((row["target_surface"], row["old_event_id"]))
    check("supercard_inventory_replay", actual_supercards == expected_supercards and not supercard_failures, sorted(expected_supercards ^ actual_supercards) + supercard_failures)
    supercard_targets = set(supercard_modes_by_target)
    compatible_supercards = 0
    supercard_relation_counts = Counter()
    for surface, old_modes in supercard_modes_by_target.items():
        target_modes = set(card_by_surface[surface]["observed_requirement_modes"].split("|"))
        rel = relation(old_modes, target_modes)
        supercard_relation_counts[rel] += 1
        compatible_supercards += rel != "TARGET_MODE_SET_DISJOINT"
    check("supercard_target_and_context_counts", (len(supercard_targets), compatible_supercards) == (8, 4), [len(supercard_targets), compatible_supercards, dict(supercard_relation_counts)])

    anchor_groups: dict[str, list[str]] = defaultdict(list)
    for card in cards:
        anchor_groups[card["anchor_recipe"]].append(card["surface"])
    recurring = {anchor: sorted(surfaces) for anchor, surfaces in anchor_groups.items() if len(surfaces) >= 2}
    family_inventory = {row["anchor_recipe"]: sorted(row["target_surfaces"].split("|")) for row in families}
    check("recurrent_anchor_family_replay", recurring == family_inventory, {"expected": recurring, "actual": family_inventory} if recurring != family_inventory else len(recurring))
    check("recurrent_anchor_target_count", sum(len(surfaces) for surfaces in recurring.values()) == 34, sum(len(surfaces) for surfaces in recurring.values()))

    structural_counts = Counter(row["structural_support_class"] for row in cards)
    check("structural_support_distribution", dict(structural_counts) == {
        "ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD": 31,
        "ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE": 6,
        "EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD": 8,
        "RECIPE_ANCHOR_ALL_INTERFACES_OLD": 7,
        "REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL": 29,
    }, dict(structural_counts))

    summary_map = {row["metric"]: row["value"] for row in summary}
    check("summary_required_metrics", all(key in summary_map for key in [
        "target_count", "longest_anchor_candidate_count", "directional_arm_count",
        "aligned_visible_stem_target_count", "old_supported_interface_count",
        "anchor_context_compatible_target_count", "visible_affix_channel_count",
        "repeated_invariant_visible_channel_count", "old_supercard_target_count",
    ]), summary_map)
    book = BOOK_OUT.read_text(encoding="utf-8")
    check("book_status", result["status"] in book, result["status"])
    check("book_complete_card_inventory", sum(f"`{surface}`" in book for surface in fragment_targets) == 81, sum(f"`{surface}`" in book for surface in fragment_targets))
    check("book_dy_exception", "`dy`" in book and "fünfmal `DY`" in book and "einmal `D_ADDR+Y`" in book, "dy")

    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("gdt543_reader", READER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    chady = module.lookup("chady")
    qoteeod = module.lookup("qoteeod")
    delegated = module.lookup("qokees")
    check("reader_chady", chady["anchor"]["recipe"] == "CH+A_ADDR" and chady["visible_stem"]["surface"] == "cha" and chady["arms"][0]["visible_affix"] == "dy", chady)
    check("reader_qoteeod_supercard", qoteeod["old_supercard"]["event_count"] == 1 and qoteeod["visible_stem"]["status"] == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM", qoteeod)
    check("reader_delegation", delegated["status"] == "NO_GDT543_FRAGMENT_EXTENSION_CARD", delegated)

    expected_result = {
        "status": "PASS_81_FRAGMENT_TARGETS_MAPPED__72_ALIGNED_STEMS__13_RECURRENT_CHANNELS",
        "target_count": 81,
        "longest_anchor_candidate_count": 104,
        "selected_anchor_count": 81,
        "directional_arm_count": 93,
        "visible_stem_status_counts": {
            "ALIGNED_EXACT_OLD_SURFACE_STEM": 72,
            "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM": 1,
            "NO_EXACT_OLD_SURFACE_STEM": 8,
        },
        "aligned_visible_stem_target_count": 72,
        "old_supported_interface_count": 87,
        "interface_count": 93,
        "full_arm_joint_count": 15,
        "arm_with_any_joint_extension_count": 28,
        "anchor_context_relation_counts": {
            "TARGET_MODE_SET_DISJOINT": 12,
            "TARGET_MODE_SET_EQUAL": 53,
            "TARGET_MODE_SET_INCLUDED": 16,
        },
        "anchor_context_compatible_target_count": 69,
        "visible_affix_observation_count": 83,
        "visible_affix_channel_count": 53,
        "repeated_invariant_visible_channel_count": 13,
        "repeated_ambiguous_visible_channel_count": 1,
        "targets_with_repeated_invariant_channel_count": 34,
        "recurrent_anchor_family_count": 16,
        "targets_in_recurrent_anchor_families": 34,
        "old_supercard_target_count": 8,
        "old_supercard_event_count": 19,
        "old_supercard_context_compatible_target_count": 4,
        "old_supercard_context_relation_counts": {
            "TARGET_MODE_SET_DISJOINT": 4,
            "TARGET_MODE_SET_EQUAL": 1,
            "TARGET_MODE_SET_INCLUDED": 3,
        },
        "structural_support_class_counts": {
            "ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD": 31,
            "ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE": 6,
            "EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD": 8,
            "RECIPE_ANCHOR_ALL_INTERFACES_OLD": 7,
            "REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL": 29,
        },
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated_paths = [
        CARD_OUT, CANDIDATE_OUT, ARM_OUT, CHANNEL_OUT, SUPERCARD_OUT,
        FAMILY_OUT, SUMMARY_OUT, BOOK_OUT, RESULT_OUT,
    ]
    hashes_before = {path.name: digest(path) for path in generated_paths}
    rerun = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    hashes_after = {path.name: digest(path) for path in generated_paths}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout)
    check("generator_byte_determinism", hashes_before == hashes_after, hashes_after)

    failed = [item for item in checks if not item["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION_OUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
