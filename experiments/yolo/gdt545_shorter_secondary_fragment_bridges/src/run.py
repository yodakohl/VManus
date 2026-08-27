#!/usr/bin/env python3
"""Find shorter exact old-recipe stems for GDT543's sixteen flagged cards."""

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
STATUS = "FOUR_FLAGGED_TARGETS_GAIN_SHORTER_SECONDARY_BRIDGES__TWELVE_DEFAULTS_REMAIN"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
}
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


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(recipe.split("+")) if recipe and recipe != "NONE" else tuple()


def render(parts: tuple[str, ...]) -> str:
    return "+".join(parts) if parts else "NONE"


def join(values) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def direction(start: int, width: int, total: int) -> str:
    if start and start + width < total:
        return "BOTH_SIDES"
    if start:
        return "LEFT_EXTENSION"
    if start + width < total:
        return "RIGHT_EXTENSION"
    return "NO_EXTENSION"


def mode(recipe: tuple[str, ...], state: dict[str, str]) -> str:
    inherited_action = not any(atom in ACTION_ROOTS for atom in recipe) and bool(state["action"])
    inherited_argument = not any(atom in ARGUMENT_ROOTS for atom in recipe) and bool(state["argument"])
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
    cards = read_tsv(CARD_IN)
    arms = read_tsv(ARM_IN)
    flagged_rows = read_tsv(FLAGGED_IN)
    if (len(old_events), len(cards), len(arms), len(flagged_rows)) != (4576, 81, 93, 16):
        raise RuntimeError("Input inventory drift")

    cards_by_surface = {row["surface"]: row for row in cards}
    events_by_recipe: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    surfaces_by_recipe: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        recipe = atoms(event["component_recipe"])
        events_by_recipe[recipe].append(event)
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

    context_flags = {
        row["surface"]
        for row in cards
        if row["anchor_context_relation"] == "TARGET_MODE_SET_DISJOINT"
    }
    interface_flags = {
        row["target_surface"]
        for row in arms
        if int(row["old_interface_event_count"]) == 0
    }
    flagged = {row["surface"] for row in flagged_rows}
    if flagged != context_flags | interface_flags:
        raise RuntimeError("GDT544 flag union drift")

    candidate_rows: list[dict[str, object]] = []
    candidates_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for flagged_row in flagged_rows:
        surface = flagged_row["surface"]
        card = cards_by_surface[surface]
        recipe = atoms(card["final_recipe"])
        target_modes = set(card["observed_requirement_modes"].split("|"))
        primary_length = int(card["anchor_atom_count"])
        base_visible_rank = VISIBLE_RANK[card["visible_stem_status"]]
        base_context_rank = RELATION_RANK[card["anchor_context_relation"]]
        base_supported = int(card["old_supported_interface_count"])
        base_interfaces = int(card["interface_count"])
        base_fraction = base_supported / base_interfaces
        base_all_interfaces = base_supported == base_interfaces

        for width in range(2, primary_length):
            for start in range(len(recipe) - width + 1):
                anchor = recipe[start : start + width]
                if anchor not in events_by_recipe:
                    continue
                candidate_direction = direction(start, width, len(recipe))
                surface_matches = []
                for old_surface, count in surfaces_by_recipe[anchor].items():
                    search_from = 0
                    while True:
                        char_start = surface.find(old_surface, search_from)
                        if char_start < 0:
                            break
                        surface_direction = direction(char_start, len(old_surface), len(surface))
                        surface_matches.append(
                            {
                                "surface": old_surface,
                                "event_count": count,
                                "char_start": char_start,
                                "direction": surface_direction,
                                "rank": 2 if surface_direction == candidate_direction else 1,
                            }
                        )
                        search_from = char_start + 1
                visible_rank = max((match["rank"] for match in surface_matches), default=0)
                best_matches = [match for match in surface_matches if match["rank"] == visible_rank]
                best_match = sorted(best_matches, key=lambda item: (-len(item["surface"]), -item["event_count"], item["surface"], item["char_start"]))[0] if best_matches else None
                visible_status = (
                    "ALIGNED_EXACT_OLD_SURFACE_STEM" if visible_rank == 2
                    else "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM" if visible_rank == 1
                    else "NO_EXACT_OLD_SURFACE_STEM"
                )

                boundaries = []
                if start:
                    boundaries.append((recipe[start - 1], recipe[start]))
                if start + width < len(recipe):
                    boundaries.append((recipe[start + width - 1], recipe[start + width]))
                supported = sum(bool(pair_events[pair]) for pair in boundaries)
                interface_fraction = supported / len(boundaries)
                all_interfaces = supported == len(boundaries)
                old_modes = {
                    mode(recipe, before_event[event["global_running_event_id"]])
                    for event in events_by_recipe[anchor]
                }
                relation = mode_relation(old_modes, target_modes)
                context_rank = RELATION_RANK[relation]

                visible_nonworse = visible_rank >= base_visible_rank
                context_nonworse = context_rank >= base_context_rank
                interface_nonworse = interface_fraction >= base_fraction
                context_repair = surface in context_flags and context_rank > base_context_rank
                interface_repair = surface in interface_flags and all_interfaces and not base_all_interfaces
                qualifies = visible_nonworse and context_nonworse and interface_nonworse and (context_repair or interface_repair)
                rejection_reasons = []
                if not visible_nonworse:
                    rejection_reasons.append("VISIBLE_STEM_SUPPORT_WORSE")
                if not context_nonworse:
                    rejection_reasons.append("CONTEXT_SUPPORT_WORSE")
                if not interface_nonworse:
                    rejection_reasons.append("INTERFACE_SUPPORT_WORSE")
                if not (context_repair or interface_repair):
                    rejection_reasons.append("NO_FLAG_REPAIRED")

                row = {
                    "target_ordinal": card["target_ordinal"],
                    "surface": surface,
                    "final_recipe": card["final_recipe"],
                    "flag_reasons": flagged_row["flag_reasons"],
                    "primary_anchor_recipe": card["anchor_recipe"],
                    "primary_anchor_atom_count": primary_length,
                    "primary_visible_rank": base_visible_rank,
                    "primary_context_relation": card["anchor_context_relation"],
                    "primary_context_rank": base_context_rank,
                    "primary_supported_interfaces": base_supported,
                    "primary_interface_count": base_interfaces,
                    "shorter_anchor_recipe": render(anchor),
                    "shorter_anchor_start_atom": start + 1,
                    "shorter_anchor_atom_count": width,
                    "shorter_extension_direction": candidate_direction,
                    "shorter_left_extension_recipe": render(recipe[:start]),
                    "shorter_right_extension_recipe": render(recipe[start + width :]),
                    "old_anchor_event_count": len(events_by_recipe[anchor]),
                    "old_anchor_surfaces": join(surfaces_by_recipe[anchor]),
                    "visible_stem_status": visible_status,
                    "visible_rank": visible_rank,
                    "best_visible_stem_surface": best_match["surface"] if best_match else "NONE",
                    "best_visible_stem_char_start": best_match["char_start"] + 1 if best_match else 0,
                    "shorter_anchor_context_modes": "|".join(sorted(old_modes, key=MODE_ORDER.__getitem__)),
                    "shorter_anchor_context_relation": relation,
                    "shorter_context_rank": context_rank,
                    "shorter_supported_interfaces": supported,
                    "shorter_interface_count": len(boundaries),
                    "all_shorter_interfaces_old": "YES" if all_interfaces else "NO",
                    "visible_nonworse": "YES" if visible_nonworse else "NO",
                    "context_nonworse": "YES" if context_nonworse else "NO",
                    "interface_nonworse": "YES" if interface_nonworse else "NO",
                    "repairs_context_flag": "YES" if context_repair else "NO",
                    "repairs_interface_flag": "YES" if interface_repair else "NO",
                    "qualifies_as_secondary_bridge": "YES" if qualifies else "NO",
                    "rejection_reasons": "NONE" if qualifies else "|".join(rejection_reasons),
                    "selected_secondary_bridge": "NO",
                    "guard": "SHORTER_EXACT_OLD_RECIPE_ANCHOR__PRIMARY_GDT543_ANCHOR_RETAINED",
                }
                candidate_rows.append(row)
                candidates_by_surface[surface].append(row)

    selected_by_surface = {}
    for surface, rows in candidates_by_surface.items():
        qualified = [row for row in rows if row["qualifies_as_secondary_bridge"] == "YES"]
        if not qualified:
            continue
        selected = sorted(
            qualified,
            key=lambda row: (
                -int(row["visible_rank"]),
                -int(row["shorter_context_rank"]),
                row["all_shorter_interfaces_old"] != "YES",
                -int(row["shorter_anchor_atom_count"]),
                -int(row["old_anchor_event_count"]),
                -len(row["best_visible_stem_surface"] if row["best_visible_stem_surface"] != "NONE" else ""),
                int(row["shorter_anchor_start_atom"]),
                row["shorter_anchor_recipe"],
            ),
        )[0]
        selected["selected_secondary_bridge"] = "YES"
        selected_by_surface[surface] = selected

    candidate_rows.sort(key=lambda row: (int(row["target_ordinal"]), -int(row["shorter_anchor_atom_count"]), int(row["shorter_anchor_start_atom"]), row["shorter_anchor_recipe"]))
    bridge_rows = []
    for surface in sorted(selected_by_surface, key=lambda value: int(cards_by_surface[value]["target_ordinal"])):
        selected = selected_by_surface[surface]
        card = cards_by_surface[surface]
        repair = "CONTEXT" if selected["repairs_context_flag"] == "YES" else "INTERFACE"
        bridge_rows.append(
            {
                "target_ordinal": card["target_ordinal"],
                "surface": surface,
                "final_recipe": card["final_recipe"],
                "retained_primary_anchor_recipe": card["anchor_recipe"],
                "secondary_anchor_recipe": selected["shorter_anchor_recipe"],
                "secondary_anchor_start_atom": selected["shorter_anchor_start_atom"],
                "secondary_left_extension_recipe": selected["shorter_left_extension_recipe"],
                "secondary_right_extension_recipe": selected["shorter_right_extension_recipe"],
                "secondary_visible_stem_status": selected["visible_stem_status"],
                "secondary_visible_stem_surface": selected["best_visible_stem_surface"],
                "secondary_context_modes": selected["shorter_anchor_context_modes"],
                "secondary_context_relation": selected["shorter_anchor_context_relation"],
                "secondary_supported_interfaces": selected["shorter_supported_interfaces"],
                "secondary_interface_count": selected["shorter_interface_count"],
                "repaired_dimension": repair,
                "neutral_surface_phrase_de": card["neutral_surface_phrase_de"],
                "decision": "ADD_SECONDARY_BRIDGE__RETAIN_PRIMARY_LONGEST_ANCHOR",
                "guard": "SUPPORT_BRIDGE_ONLY__NO_RECIPE_OR_MEANING_CHANGE",
            }
        )

    unrepaired_rows = []
    for flagged_row in flagged_rows:
        surface = flagged_row["surface"]
        if surface in selected_by_surface:
            continue
        rows = candidates_by_surface.get(surface, [])
        unrepaired_rows.append(
            {
                "target_ordinal": flagged_row["target_ordinal"],
                "surface": surface,
                "final_recipe": flagged_row["final_recipe"],
                "flag_reasons": flagged_row["flag_reasons"],
                "retained_primary_anchor_recipe": flagged_row["selected_anchor_recipe"],
                "shorter_exact_multiatom_candidate_count": len(rows),
                "qualified_shorter_candidate_count": sum(row["qualifies_as_secondary_bridge"] == "YES" for row in rows),
                "shorter_candidate_recipes": join(row["shorter_anchor_recipe"] for row in rows),
                "decision": "KEEP_GDT543_PRIMARY_AS_EXPLICIT_DEFAULT",
                "guard": "NO_QUALIFIED_SHORTER_SECONDARY_BRIDGE__CARD_NOT_REJECTED",
            }
        )
    unrepaired_rows.sort(key=lambda row: int(row["target_ordinal"]))

    result = {
        "status": STATUS,
        "flagged_target_count": len(flagged),
        "shorter_exact_multiatom_candidate_count": len(candidate_rows),
        "flagged_target_with_shorter_candidate_count": len(candidates_by_surface),
        "qualified_shorter_candidate_count": sum(row["qualifies_as_secondary_bridge"] == "YES" for row in candidate_rows),
        "qualified_target_count": len({row["surface"] for row in candidate_rows if row["qualifies_as_secondary_bridge"] == "YES"}),
        "selected_secondary_bridge_count": len(bridge_rows),
        "context_secondary_bridge_count": sum(row["repaired_dimension"] == "CONTEXT" for row in bridge_rows),
        "interface_secondary_bridge_count": sum(row["repaired_dimension"] == "INTERFACE" for row in bridge_rows),
        "selected_secondary_surface_count": len({row["surface"] for row in bridge_rows}),
        "selected_secondary_all_context_equal_count": sum(row["secondary_context_relation"] == "TARGET_MODE_SET_EQUAL" for row in bridge_rows),
        "selected_secondary_all_interfaces_old_count": sum(row["secondary_supported_interfaces"] == row["secondary_interface_count"] for row in bridge_rows),
        "selected_secondary_aligned_visible_count": sum(row["secondary_visible_stem_status"] == "ALIGNED_EXACT_OLD_SURFACE_STEM" for row in bridge_rows),
        "selected_secondary_direction_mismatch_visible_count": sum(row["secondary_visible_stem_status"] == "DIRECTION_MISMATCH_EXACT_OLD_SURFACE_STEM" for row in bridge_rows),
        "unrepaired_flagged_target_count": len(unrepaired_rows),
        "unrepaired_with_no_shorter_candidate_count": sum(int(row["shorter_exact_multiatom_candidate_count"]) == 0 for row in unrepaired_rows),
        "unrepaired_with_unqualified_shorter_candidates_count": sum(int(row["shorter_exact_multiatom_candidate_count"]) > 0 for row in unrepaired_rows),
        "primary_anchor_changes": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    expected = {
        "flagged_target_count": 16,
        "shorter_exact_multiatom_candidate_count": 12,
        "flagged_target_with_shorter_candidate_count": 7,
        "qualified_shorter_candidate_count": 6,
        "qualified_target_count": 4,
        "selected_secondary_bridge_count": 4,
        "context_secondary_bridge_count": 3,
        "interface_secondary_bridge_count": 1,
        "selected_secondary_all_context_equal_count": 4,
        "selected_secondary_all_interfaces_old_count": 4,
        "selected_secondary_aligned_visible_count": 3,
        "selected_secondary_direction_mismatch_visible_count": 1,
        "unrepaired_flagged_target_count": 12,
        "unrepaired_with_no_shorter_candidate_count": 9,
        "unrepaired_with_unqualified_shorter_candidates_count": 3,
    }
    drift = {key: (result[key], value) for key, value in expected.items() if result[key] != value}
    if drift:
        raise RuntimeError(f"Shorter bridge inventory drift: {drift}")

    write_tsv(CANDIDATE_OUT, candidate_rows)
    write_tsv(BRIDGE_OUT, bridge_rows)
    write_tsv(UNREPAIRED_OUT, unrepaired_rows)
    write_tsv(SUMMARY_OUT, [{"metric": key, "value": value} for key, value in result.items() if key != "status"])

    bridge_lines = []
    for row in bridge_rows:
        left = "" if row["secondary_left_extension_recipe"] == "NONE" else row["secondary_left_extension_recipe"] + " "
        right = "" if row["secondary_right_extension_recipe"] == "NONE" else " " + row["secondary_right_extension_recipe"]
        bridge_lines.append(
            f"| `{row['surface']}` | `[{row['retained_primary_anchor_recipe']}]` | "
            f"`{left}[{row['secondary_anchor_recipe']}]{right}` | "
            f"`{row['secondary_visible_stem_surface']}` | {row['repaired_dimension']} | {row['neutral_surface_phrase_de']} |"
        )
    unrepaired_names = ", ".join(f"`{row['surface']}`" for row in unrepaired_rows)
    BOOK_OUT.write_text(f"""# GDT545 — vier kürzere Sekundärbrücken

Status: `{STATUS}`

Unter den16 GDT544-Restkarten besitzen nur sieben überhaupt ein kürzeres
altes Mehrkomponenten-Ganzrezept. Das ergibt zwölf Kandidaten. Sechs Kandidaten
auf vier Zielkarten halten sichtbare Stützung, Kontext und Grenzanteil
mindestens konstant und reparieren zusätzlich eine markierte Dimension.

Der längste GDT543-Stamm bleibt immer der Hauptanker. GDT545 fügt nur eine
zweite, kürzere Beweisroute hinzu:

| Ziel | Hauptstamm | Sekundärzerlegung | sichtbarer Altträger | repariert | Arbeitsbedeutung |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(bridge_lines)}

`chckhedy` gewinnt exakte sichtbare Stammcontainment, aber nicht dieselbe
Links-/Rechtsausrichtung; diese Einschränkung bleibt ausdrücklich sichtbar.
Die anderen drei Sekundärstämme sind exakt richtungsgleich. Alle vier haben
vollständig alte Atomgrenzen und exakt dieselbe Kontextmodusmenge wie das Ziel.

Zwölf Karten bleiben unverändert als Defaults stehen: {unrepaired_names}.
Neun davon besitzen keinen kürzeren alten Mehrkomponentenstamm; drei haben nur
Kandidaten, die keine markierte Dimension ohne Verlust reparieren.

Keine Bedeutung, Rezeptkarte oder primäre Stammwahl ändert sich.
""", encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
