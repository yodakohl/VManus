#!/usr/bin/env python3
"""Compile directional learned-fragment extension frames for 81 targets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from functools import lru_cache
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
STATUS = "PASS_81_FRAGMENT_TARGETS_MAPPED__72_ALIGNED_STEMS__13_RECURRENT_CHANNELS"

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


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def render(parts: tuple[str, ...] | list[str]) -> str:
    return "+".join(parts) if parts else "NONE"


def join(values) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def join_modes(values: set[str]) -> str:
    return "|".join(sorted(values, key=MODE_ORDER.__getitem__))


def occurrence_positions(big: tuple[str, ...], small: tuple[str, ...]) -> list[int]:
    if not small or len(small) > len(big):
        return []
    return [
        start
        for start in range(len(big) - len(small) + 1)
        if big[start : start + len(small)] == small
    ]


def extension_direction(start: int, width: int, total: int) -> str:
    left = start > 0
    right = start + width < total
    if left and right:
        return "BOTH_SIDES"
    if left:
        return "LEFT_EXTENSION"
    if right:
        return "RIGHT_EXTENSION"
    return "NO_EXTENSION"


def context_mode(recipe: tuple[str, ...], before: dict[str, str]) -> str:
    inherited_action = not any(atom in ACTION_ROOTS for atom in recipe) and bool(
        before["action"]
    )
    inherited_argument = not any(atom in ARGUMENT_ROOTS for atom in recipe) and bool(
        before["argument"]
    )
    if inherited_action and inherited_argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "REQUIRES_ACTIVE_ACTION"
    if inherited_argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def mode_relation(old: set[str], target: set[str]) -> str:
    if old == target:
        return "TARGET_MODE_SET_EQUAL"
    if target <= old:
        return "TARGET_MODE_SET_INCLUDED"
    if old & target:
        return "TARGET_MODE_SET_OVERLAPS"
    return "TARGET_MODE_SET_DISJOINT"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_events = read_tsv(OLD_EVENTS_IN)
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    contracts = read_tsv(CONTRACT_IN)
    tiers = read_tsv(TIER_IN)
    if (len(old_events), len(old_statements), len(contracts), len(tiers)) != (
        4576,
        715,
        145,
        145,
    ):
        raise RuntimeError("Input inventory drift")

    contract_by_surface = {row["surface"]: row for row in contracts}
    targets = [
        row
        for row in tiers
        if row["final_support_tier"]
        == "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
    ]
    if len(targets) != 81:
        raise RuntimeError(f"Expected 81 fragment targets, found {len(targets)}")

    events_by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    surface_counts_by_recipe: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        recipe = atoms(event["component_recipe"])
        events_by_recipe[recipe].append(event)
        surface_counts_by_recipe[recipe][event["surface"]] += 1
        for pair in set(zip(recipe, recipe[1:])):
            pair_events[pair].append(event)
    old_recipes = set(events_by_recipe)

    before_event: dict[str, dict[str, str]] = {}
    state_by_statement: dict[str, dict[str, str]] = {}
    for event in old_events:
        statement_id = event["source_statement_id"]
        state = state_by_statement.setdefault(
            statement_id, {"action": "", "argument": ""}
        )
        before_event[event["global_running_event_id"]] = dict(state)
        recipe = atoms(event["component_recipe"])
        visible_actions = [atom for atom in recipe if atom in ACTION_ROOTS]
        visible_arguments = [atom for atom in recipe if atom in ARGUMENT_ROOTS]
        if visible_actions:
            state["action"] = visible_actions[-1]
        if visible_arguments:
            state["argument"] = visible_arguments[-1]

    @lru_cache(maxsize=None)
    def sequence_carriers(sequence: tuple[str, ...]) -> tuple[dict[str, str], ...]:
        carriers: list[dict[str, str]] = []
        for old_recipe, events in events_by_recipe.items():
            if occurrence_positions(old_recipe, sequence):
                carriers.extend(events)
        return tuple(carriers)

    candidate_records: list[dict[str, object]] = []
    selected_material: list[dict[str, object]] = []
    supercard_rows: list[dict[str, object]] = []

    for target in targets:
        surface = target["surface"]
        recipe = atoms(target["final_recipe"])
        longest = int(target["final_longest_old_fragment_atoms"])
        target_modes = set(target["observed_requirement_modes"].split("|"))
        options: list[dict[str, object]] = []

        for start in range(len(recipe) - longest + 1):
            anchor = recipe[start : start + longest]
            if anchor not in old_recipes:
                continue
            direction = extension_direction(start, longest, len(recipe))
            boundaries: list[tuple[str, str]] = []
            if start:
                boundaries.append((recipe[start - 1], recipe[start]))
            if start + longest < len(recipe):
                boundaries.append(
                    (recipe[start + longest - 1], recipe[start + longest])
                )
            supported = sum(bool(pair_events[pair]) for pair in boundaries)

            matches: list[dict[str, object]] = []
            for old_surface, old_count in sorted(
                surface_counts_by_recipe[anchor].items()
            ):
                search_from = 0
                while True:
                    char_start = surface.find(old_surface, search_from)
                    if char_start < 0:
                        break
                    surface_direction = extension_direction(
                        char_start, len(old_surface), len(surface)
                    )
                    matches.append(
                        {
                            "old_surface": old_surface,
                            "old_surface_event_count": old_count,
                            "char_start": char_start,
                            "surface_direction": surface_direction,
                            "direction_aligned": surface_direction == direction,
                        }
                    )
                    search_from = char_start + 1

            aligned = [match for match in matches if match["direction_aligned"]]
            best_pool = aligned or matches
            best_match = (
                sorted(
                    best_pool,
                    key=lambda item: (
                        -len(str(item["old_surface"])),
                        -int(item["old_surface_event_count"]),
                        str(item["old_surface"]),
                        int(item["char_start"]),
                    ),
                )[0]
                if best_pool
                else None
            )
            option = {
                "target_ordinal": target["target_ordinal"],
                "surface": surface,
                "final_recipe": target["final_recipe"],
                "anchor_recipe": render(anchor),
                "anchor_start_atom": start + 1,
                "anchor_atom_count": longest,
                "extension_direction": direction,
                "left_extension_recipe": render(recipe[:start]),
                "right_extension_recipe": render(recipe[start + longest :]),
                "old_anchor_event_count": len(events_by_recipe[anchor]),
                "old_anchor_surface_count": len(surface_counts_by_recipe[anchor]),
                "old_anchor_surfaces": join(surface_counts_by_recipe[anchor]),
                "interface_count": len(boundaries),
                "old_supported_interface_count": supported,
                "all_interfaces_old": "YES" if supported == len(boundaries) else "NO",
                "aligned_visible_match_count": len(aligned),
                "any_visible_match_count": len(matches),
                "best_visible_stem_surface": (
                    best_match["old_surface"] if best_match else "NONE"
                ),
                "best_visible_stem_event_count": (
                    best_match["old_surface_event_count"] if best_match else 0
                ),
                "best_visible_stem_char_start": (
                    int(best_match["char_start"]) + 1 if best_match else 0
                ),
                "best_visible_stem_direction": (
                    best_match["surface_direction"] if best_match else "NONE"
                ),
                "selected": "NO",
                "guard": "EXACT_LONGEST_OLD_COMPLETE_RECIPE_ANCHOR__NO_FUZZY_MATCH",
                "_anchor": anchor,
                "_start": start,
                "_boundaries": boundaries,
                "_matches": matches,
                "_best_match": best_match,
                "_has_aligned": bool(aligned),
            }
            options.append(option)

        if not options:
            raise RuntimeError(f"No longest anchor for {surface}")

        selected = sorted(
            options,
            key=lambda item: (
                not bool(item["_has_aligned"]),
                item["all_interfaces_old"] != "YES",
                -int(item["old_supported_interface_count"]),
                -int(item["old_anchor_event_count"]),
                -len(
                    str(item["best_visible_stem_surface"])
                    if item["best_visible_stem_surface"] != "NONE"
                    else ""
                ),
                int(item["_start"]),
                str(item["anchor_recipe"]),
            ),
        )[0]
        selected["selected"] = "YES"
        candidate_records.extend(options)

        anchor = selected["_anchor"]
        start = int(selected["_start"])
        best_match = selected["_best_match"]
        has_aligned = bool(selected["_has_aligned"])
        if has_aligned:
            visible_status = "ALIGNED_EXACT_OLD_SURFACE_STEM"
        elif best_match:
            visible_status = "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM"
        else:
            visible_status = "NO_EXACT_OLD_SURFACE_STEM"

        if best_match:
            char_start = int(best_match["char_start"])
            visible_stem = str(best_match["old_surface"])
            visible_left = surface[:char_start] or "NONE"
            visible_right = surface[char_start + len(visible_stem) :] or "NONE"
        else:
            visible_stem = "NONE"
            visible_left = "NONE"
            visible_right = "NONE"

        anchor_modes = {
            context_mode(recipe, before_event[event["global_running_event_id"]])
            for event in events_by_recipe[anchor]
        }
        anchor_relation = mode_relation(anchor_modes, target_modes)

        old_supercards: list[tuple[tuple[str, ...], dict[str, str], int]] = []
        supercard_modes: set[str] = set()
        for old_recipe, events in events_by_recipe.items():
            if len(old_recipe) <= len(recipe):
                continue
            for occurrence_start in occurrence_positions(old_recipe, recipe):
                for event in events:
                    reduced_mode = context_mode(
                        recipe, before_event[event["global_running_event_id"]]
                    )
                    supercard_modes.add(reduced_mode)
                    old_supercards.append((old_recipe, event, occurrence_start))
                    supercard_rows.append(
                        {
                            "target_surface": surface,
                            "target_recipe": target["final_recipe"],
                            "target_context_modes": target["observed_requirement_modes"],
                            "old_event_id": event["global_running_event_id"],
                            "old_surface": event["surface"],
                            "old_supercard_recipe": event["component_recipe"],
                            "physical_page": event["physical_page"],
                            "register": event["register"],
                            "statement_id": event["source_statement_id"],
                            "target_start_atom": occurrence_start + 1,
                            "old_left_extra_atoms": render(old_recipe[:occurrence_start]),
                            "old_right_extra_atoms": render(
                                old_recipe[occurrence_start + len(recipe) :]
                            ),
                            "reduced_target_context_mode": reduced_mode,
                            "target_mode_present": (
                                "YES" if reduced_mode in target_modes else "NO"
                            ),
                            "guard": "EXACT_CONTIGUOUS_TARGET_RECIPE_INSIDE_LONGER_OLD_COMPLETE_CARD",
                        }
                    )
        supercard_relation = (
            mode_relation(supercard_modes, target_modes)
            if supercard_modes
            else "NO_OLD_SUPERCARD"
        )

        contract = contract_by_surface[surface]
        selected_material.append(
            {
                "target": target,
                "contract": contract,
                "recipe": recipe,
                "anchor": anchor,
                "start": start,
                "direction": selected["extension_direction"],
                "visible_status": visible_status,
                "visible_stem": visible_stem,
                "visible_left": visible_left,
                "visible_right": visible_right,
                "anchor_modes": anchor_modes,
                "anchor_relation": anchor_relation,
                "supercard_modes": supercard_modes,
                "supercard_relation": supercard_relation,
                "supercards": old_supercards,
                "selected": selected,
            }
        )

    arm_rows: list[dict[str, object]] = []
    channel_observations: dict[
        tuple[str, str], list[tuple[str, str, str]]
    ] = defaultdict(list)
    for material in selected_material:
        target = material["target"]
        recipe = material["recipe"]
        anchor = material["anchor"]
        start = int(material["start"])
        aligned = material["visible_status"] == "ALIGNED_EXACT_OLD_SURFACE_STEM"
        arms = []
        if start:
            arms.append(("LEFT", recipe[:start]))
        if start + len(anchor) < len(recipe):
            arms.append(("RIGHT", recipe[start + len(anchor) :]))

        for side, extension in arms:
            if side == "LEFT":
                interface_pair = (extension[-1], anchor[0])
                sequences = [extension[-depth:] + anchor for depth in range(1, len(extension) + 1)]
                visible_affix = material["visible_left"] if aligned else "NONE"
            else:
                interface_pair = (anchor[-1], extension[0])
                sequences = [anchor + extension[:depth] for depth in range(1, len(extension) + 1)]
                visible_affix = material["visible_right"] if aligned else "NONE"

            deepest_depth = 0
            deepest_sequence: tuple[str, ...] = tuple()
            deepest_events: tuple[dict[str, str], ...] = tuple()
            for depth, sequence in enumerate(sequences, start=1):
                carriers = sequence_carriers(sequence)
                if carriers:
                    deepest_depth = depth
                    deepest_sequence = sequence
                    deepest_events = carriers

            if visible_affix != "NONE":
                channel_observations[(side, str(visible_affix))].append(
                    (target["surface"], render(extension), render(anchor))
                )

            arm_rows.append(
                {
                    "target_surface": target["surface"],
                    "target_recipe": target["final_recipe"],
                    "side": side,
                    "anchor_recipe": render(anchor),
                    "extension_recipe": render(extension),
                    "extension_atom_count": len(extension),
                    "interface_pair": f"{interface_pair[0]}>{interface_pair[1]}",
                    "old_interface_event_count": len(pair_events[interface_pair]),
                    "old_interface_recipe_count": len(
                        {event["component_recipe"] for event in pair_events[interface_pair]}
                    ),
                    "old_interface_surfaces": join(
                        event["surface"] for event in pair_events[interface_pair]
                    ),
                    "deepest_joint_extension_atoms": deepest_depth,
                    "deepest_joint_sequence": render(deepest_sequence),
                    "deepest_joint_old_event_count": len(deepest_events),
                    "full_arm_seen_with_anchor": (
                        "YES" if deepest_depth == len(extension) else "NO"
                    ),
                    "aligned_visible_affix": visible_affix,
                    "visible_channel_class": "PENDING",
                    "visible_channel_observation_count": 0,
                    "visible_channel_recipe_variants": "NONE",
                    "guard": "DIRECTIONAL_EXTENSION_FROM_EXACT_OLD_COMPLETE_RECIPE_ANCHOR",
                }
            )

    channel_rows: list[dict[str, object]] = []
    channel_meta: dict[tuple[str, str], dict[str, object]] = {}
    for ordinal, (key, observations) in enumerate(
        sorted(channel_observations.items()), start=1
    ):
        side, affix = key
        recipe_counts = Counter(observation[1] for observation in observations)
        if len(observations) >= 2 and len(recipe_counts) == 1:
            channel_class = "REPEATED_INVARIANT_VISIBLE_CHANNEL"
        elif len(observations) >= 2:
            channel_class = "REPEATED_AMBIGUOUS_VISIBLE_CHANNEL"
        else:
            channel_class = "SINGLETON_VISIBLE_CHANNEL"
        dominant_recipe, dominant_count = sorted(
            recipe_counts.items(), key=lambda item: (-item[1], item[0])
        )[0]
        meta = {
            "class": channel_class,
            "count": len(observations),
            "variants": join(recipe_counts),
        }
        channel_meta[key] = meta
        channel_rows.append(
            {
                "channel_ordinal": ordinal,
                "side": side,
                "visible_affix": affix,
                "observation_count": len(observations),
                "target_count": len({observation[0] for observation in observations}),
                "recipe_extension_variant_count": len(recipe_counts),
                "recipe_extension_variants": join(recipe_counts),
                "recipe_extension_counts": "|".join(
                    f"{recipe}:{count}"
                    for recipe, count in sorted(recipe_counts.items())
                ),
                "dominant_recipe_extension": dominant_recipe,
                "dominant_recipe_count": dominant_count,
                "channel_class": channel_class,
                "target_surfaces": join(observation[0] for observation in observations),
                "anchor_recipes": join(observation[2] for observation in observations),
                "guard": "EXACT_VISIBLE_RESIDUE_AROUND_DIRECTION_ALIGNED_OLD_SURFACE_STEM",
            }
        )

    for arm in arm_rows:
        affix = str(arm["aligned_visible_affix"])
        if affix == "NONE":
            arm["visible_channel_class"] = "NO_ALIGNED_VISIBLE_CHANNEL"
            continue
        meta = channel_meta[(str(arm["side"]), affix)]
        arm["visible_channel_class"] = meta["class"]
        arm["visible_channel_observation_count"] = meta["count"]
        arm["visible_channel_recipe_variants"] = meta["variants"]

    arms_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for arm in arm_rows:
        arms_by_target[str(arm["target_surface"])].append(arm)

    card_rows: list[dict[str, object]] = []
    for material in selected_material:
        target = material["target"]
        surface = target["surface"]
        selected = material["selected"]
        target_arms = arms_by_target[surface]
        recurrent_channels = sum(
            arm["visible_channel_class"]
            == "REPEATED_INVARIANT_VISIBLE_CHANNEL"
            for arm in target_arms
        )
        all_interfaces_old = all(
            int(arm["old_interface_event_count"]) > 0 for arm in target_arms
        )
        if material["supercards"]:
            structural_class = "EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD"
        elif recurrent_channels:
            structural_class = "REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL"
        elif material["visible_status"] == "ALIGNED_EXACT_OLD_SURFACE_STEM":
            structural_class = (
                "ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD"
                if all_interfaces_old
                else "ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE"
            )
        else:
            structural_class = (
                "RECIPE_ANCHOR_ALL_INTERFACES_OLD"
                if all_interfaces_old
                else "EXPLICIT_RECIPE_ANCHOR_DEFAULT"
            )

        supercard_recipes = {
            render(old_recipe) for old_recipe, _, _ in material["supercards"]
        }
        contract = material["contract"]
        card_rows.append(
            {
                "target_ordinal": target["target_ordinal"],
                "surface": surface,
                "final_recipe": target["final_recipe"],
                "observed_requirement_modes": target["observed_requirement_modes"],
                "anchor_recipe": render(material["anchor"]),
                "anchor_start_atom": int(material["start"]) + 1,
                "anchor_atom_count": len(material["anchor"]),
                "old_anchor_event_count": selected["old_anchor_event_count"],
                "old_anchor_surface_count": selected["old_anchor_surface_count"],
                "old_anchor_surfaces": selected["old_anchor_surfaces"],
                "extension_direction": material["direction"],
                "left_extension_recipe": render(
                    material["recipe"][: int(material["start"])]
                ),
                "right_extension_recipe": render(
                    material["recipe"][
                        int(material["start"]) + len(material["anchor"]) :
                    ]
                ),
                "visible_stem_status": material["visible_status"],
                "visible_stem_surface": material["visible_stem"],
                "visible_left_extension": material["visible_left"],
                "visible_right_extension": material["visible_right"],
                "interface_count": len(target_arms),
                "old_supported_interface_count": sum(
                    int(arm["old_interface_event_count"]) > 0
                    for arm in target_arms
                ),
                "full_arm_joint_count": sum(
                    arm["full_arm_seen_with_anchor"] == "YES" for arm in target_arms
                ),
                "repeated_invariant_visible_channel_count": recurrent_channels,
                "anchor_context_modes": join_modes(material["anchor_modes"]),
                "anchor_context_relation": material["anchor_relation"],
                "old_supercard_event_count": len(material["supercards"]),
                "old_supercard_recipe_count": len(supercard_recipes),
                "old_supercard_recipes": join(supercard_recipes),
                "old_supercard_context_modes": (
                    join_modes(material["supercard_modes"])
                    if material["supercard_modes"]
                    else "NONE"
                ),
                "old_supercard_context_relation": material["supercard_relation"],
                "structural_support_class": structural_class,
                "neutral_surface_phrase_de": contract["neutral_surface_phrase_de"],
                "known_contextual_readings_de": contract[
                    "known_contextual_readings_de"
                ],
                "working_default": "KEEP_COMPOSITION_WITH_NAMED_OLD_FRAGMENT_AND_DIRECTIONAL_EXTENSIONS",
                "guard": "WORKING_EXTENSION_CARD__NO_WHOLE_WORD_OR_PLAINTEXT_CLAIM",
            }
        )

    selected_anchor_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for card in card_rows:
        selected_anchor_groups[str(card["anchor_recipe"])].append(card)
    family_rows: list[dict[str, object]] = []
    recurring_groups = [
        (anchor, cards)
        for anchor, cards in selected_anchor_groups.items()
        if len(cards) >= 2
    ]
    for ordinal, (anchor, cards) in enumerate(sorted(recurring_groups), start=1):
        family_rows.append(
            {
                "family_ordinal": ordinal,
                "anchor_recipe": anchor,
                "target_count": len(cards),
                "target_surfaces": join(card["surface"] for card in cards),
                "extension_directions": join(
                    card["extension_direction"] for card in cards
                ),
                "left_extension_recipes": join(
                    card["left_extension_recipe"] for card in cards
                ),
                "right_extension_recipes": join(
                    card["right_extension_recipe"] for card in cards
                ),
                "aligned_visible_stem_target_count": sum(
                    card["visible_stem_status"]
                    == "ALIGNED_EXACT_OLD_SURFACE_STEM"
                    for card in cards
                ),
                "context_compatible_target_count": sum(
                    card["anchor_context_relation"]
                    != "TARGET_MODE_SET_DISJOINT"
                    for card in cards
                ),
                "old_anchor_event_count": cards[0]["old_anchor_event_count"],
                "old_anchor_surfaces": cards[0]["old_anchor_surfaces"],
                "guard": "RECURRENT_SELECTED_ANCHOR_FAMILY__TARGET_EXTENSIONS_REMAIN_SEPARATE",
            }
        )

    clean_candidates = [
        {key: value for key, value in record.items() if not key.startswith("_")}
        for record in candidate_records
    ]
    clean_candidates.sort(
        key=lambda row: (
            int(row["target_ordinal"]),
            int(row["anchor_start_atom"]),
            str(row["anchor_recipe"]),
        )
    )
    arm_rows.sort(key=lambda row: (targets.index(next(t for t in targets if t["surface"] == row["target_surface"])), row["side"]))
    supercard_rows.sort(
        key=lambda row: (
            int(next(t["target_ordinal"] for t in targets if t["surface"] == row["target_surface"])),
            int(row["old_event_id"].split("E")[-1]),
            int(row["target_start_atom"]),
        )
    )

    write_tsv(CARD_OUT, card_rows)
    write_tsv(CANDIDATE_OUT, clean_candidates)
    write_tsv(ARM_OUT, arm_rows)
    write_tsv(CHANNEL_OUT, channel_rows)
    write_tsv(SUPERCARD_OUT, supercard_rows)
    write_tsv(FAMILY_OUT, family_rows)

    visible_status_counts = Counter(row["visible_stem_status"] for row in card_rows)
    anchor_context_counts = Counter(row["anchor_context_relation"] for row in card_rows)
    supercard_context_counts = Counter(
        row["old_supercard_context_relation"]
        for row in card_rows
        if row["old_supercard_event_count"]
    )
    structural_counts = Counter(row["structural_support_class"] for row in card_rows)
    repeated_invariant_channels = [
        row
        for row in channel_rows
        if row["channel_class"] == "REPEATED_INVARIANT_VISIBLE_CHANNEL"
    ]
    repeated_ambiguous_channels = [
        row
        for row in channel_rows
        if row["channel_class"] == "REPEATED_AMBIGUOUS_VISIBLE_CHANNEL"
    ]
    targets_with_repeated_invariant = {
        row["target_surface"]
        for row in arm_rows
        if row["visible_channel_class"]
        == "REPEATED_INVARIANT_VISIBLE_CHANNEL"
    }
    supercard_targets = {
        row["target_surface"] for row in supercard_rows
    }
    supercard_mode_compatible_targets = {
        row["surface"]
        for row in card_rows
        if int(row["old_supercard_event_count"]) > 0
        and row["old_supercard_context_relation"]
        != "TARGET_MODE_SET_DISJOINT"
    }

    result = {
        "status": STATUS,
        "target_count": len(card_rows),
        "longest_anchor_candidate_count": len(clean_candidates),
        "selected_anchor_count": len(card_rows),
        "directional_arm_count": len(arm_rows),
        "visible_stem_status_counts": dict(sorted(visible_status_counts.items())),
        "aligned_visible_stem_target_count": visible_status_counts[
            "ALIGNED_EXACT_OLD_SURFACE_STEM"
        ],
        "old_supported_interface_count": sum(
            int(row["old_interface_event_count"]) > 0 for row in arm_rows
        ),
        "interface_count": len(arm_rows),
        "full_arm_joint_count": sum(
            row["full_arm_seen_with_anchor"] == "YES" for row in arm_rows
        ),
        "arm_with_any_joint_extension_count": sum(
            int(row["deepest_joint_extension_atoms"]) > 0 for row in arm_rows
        ),
        "anchor_context_relation_counts": dict(sorted(anchor_context_counts.items())),
        "anchor_context_compatible_target_count": sum(
            row["anchor_context_relation"] != "TARGET_MODE_SET_DISJOINT"
            for row in card_rows
        ),
        "visible_affix_observation_count": sum(
            int(row["observation_count"]) for row in channel_rows
        ),
        "visible_affix_channel_count": len(channel_rows),
        "repeated_invariant_visible_channel_count": len(
            repeated_invariant_channels
        ),
        "repeated_ambiguous_visible_channel_count": len(
            repeated_ambiguous_channels
        ),
        "targets_with_repeated_invariant_channel_count": len(
            targets_with_repeated_invariant
        ),
        "recurrent_anchor_family_count": len(family_rows),
        "targets_in_recurrent_anchor_families": sum(
            int(row["target_count"]) for row in family_rows
        ),
        "old_supercard_target_count": len(supercard_targets),
        "old_supercard_event_count": len(supercard_rows),
        "old_supercard_context_compatible_target_count": len(
            supercard_mode_compatible_targets
        ),
        "old_supercard_context_relation_counts": dict(
            sorted(supercard_context_counts.items())
        ),
        "structural_support_class_counts": dict(sorted(structural_counts.items())),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    expected = {
        "target_count": 81,
        "longest_anchor_candidate_count": 104,
        "directional_arm_count": 93,
        "aligned_visible_stem_target_count": 72,
        "visible_affix_channel_count": 53,
        "repeated_invariant_visible_channel_count": 13,
        "repeated_ambiguous_visible_channel_count": 1,
        "recurrent_anchor_family_count": 16,
        "old_supercard_target_count": 8,
        "old_supercard_event_count": 19,
    }
    drift = {
        key: (result[key], value)
        for key, value in expected.items()
        if result[key] != value
    }
    if drift:
        raise RuntimeError(f"Result inventory drift: {drift}")

    summary_rows = [
        {"metric": key, "value": json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, dict) else value}
        for key, value in result.items()
        if key != "status"
    ]
    write_tsv(SUMMARY_OUT, summary_rows)

    channel_lines = []
    for row in channel_rows:
        if row["channel_class"].startswith("REPEATED"):
            channel_lines.append(
                f"| `{row['side']} {row['visible_affix']}` | {row['observation_count']} | "
                f"`{row['recipe_extension_counts']}` | `{row['channel_class']}` |"
            )
    card_lines = []
    for row in card_rows:
        left_recipe = "" if row["left_extension_recipe"] == "NONE" else row["left_extension_recipe"] + " "
        right_recipe = "" if row["right_extension_recipe"] == "NONE" else " " + row["right_extension_recipe"]
        visible_left = "" if row["visible_left_extension"] == "NONE" else row["visible_left_extension"]
        visible_right = "" if row["visible_right_extension"] == "NONE" else row["visible_right_extension"]
        visible = (
            f"`{visible_left}[{row['visible_stem_surface']}]{visible_right}`"
            if row["visible_stem_surface"] != "NONE"
            else "kein exakter sichtbarer Altstamm"
        )
        card_lines.append(
            f"| `{row['surface']}` | `{left_recipe}[{row['anchor_recipe']}]{right_recipe}` | {visible} | "
            f"`{row['anchor_context_relation']}` | `{row['structural_support_class']}` | "
            f"{row['neutral_surface_phrase_de']} |"
        )
    no_visible = ", ".join(
        f"`{row['surface']}`"
        for row in card_rows
        if row["visible_stem_status"] != "ALIGNED_EXACT_OLD_SURFACE_STEM"
    )
    unsupported = ", ".join(
        f"`{row['target_surface']}:{row['interface_pair']}`"
        for row in arm_rows
        if int(row["old_interface_event_count"]) == 0
    )
    book = f"""# GDT543 — 81 gelernte Fragmentstämme mit gerichteten Ausbauten

Status: `{STATUS}`

## Kernbefund

Alle 81 Formen behalten ein vollständiges altes Mehrkomponentenrezept als
benannten Stamm. Unter 104 gleich langen Ankeroptionen wählt die Karte einen
deterministischen Hauptanker. Bei 72/81 Zielen ist sogar eine alte sichtbare
Schreibform dieses Rezeptes exakt und richtungsgleich als Teil der neuen
Oberfläche erhalten. Die 93 linken/rechten Ausbauarme besitzen 87 alte
Grenzpaare; 69/81 Hauptanker werden in alten Satzumgebungen angetroffen, die
den Zielmodus enthalten.

Die sichtbaren Reste ergeben 83 Beobachtungen in 53 Seitenkanälen. Dreizehn
wiederkehrende Kanäle sind in ihrer Rezeptabbildung invariant und erreichen
{result['targets_with_repeated_invariant_channel_count']} Ziele. Nur der
wiederkehrende rechte Rest `dy` bleibt absichtlich zweideutig: fünfmal `DY`,
einmal `D_ADDR+Y`. Das bestätigt die schon bekannte Regel, `dy` nicht als
automatisches globales Suffix zu lesen.

Acht Zielrezepte stehen als exakte zusammenhängende Teilfolge in 19 längeren
alten Ganzkarten. Bei vier davon kommt zugleich der Ziel-Kontextmodus vor; die
vier anderen bleiben starke Struktur-, aber keine Kontextbrücken.

## Wiederkehrende sichtbare Ausbaukanäle

| Seite und Rest | Belege | Rezeptabbildung | Klasse |
| --- | ---: | --- | --- |
{chr(10).join(channel_lines)}

## Offene sichtbare und atomare Übergänge

Ohne vollständig richtungsgleichen sichtbaren Altstamm: {no_visible}.

Noch nie als direktes Paar in einer alten Ganzkarte sichtbar: {unsupported}.
Diese Karten werden nicht verworfen; sie bleiben explizite Einzeldefaults mit
ihrem alten Ganzfragment und ihrer bisherigen Bedeutung.

## Vollständiges 81-Karten-Deck

| Ziel | Rezeptausbau um Altstamm | sichtbarer Ausbau | alter Kontext | stärkste Strukturbrücke | Arbeitsbedeutung |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(card_lines)}

Keine Seite, Bedeutung, Zerlegung oder Rezeptkarte wurde verändert. Die
sichtbaren Kanäle sind Arbeitskürzel, keine bestätigten Lexeme.
"""
    BOOK_OUT.write_text(book, encoding="utf-8")
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
