#!/usr/bin/env python3
"""Derive five carrier-neutral handgrips from all exact old pair carriers."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt505_carrier_neutral_pair_handgrip_atlas"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G504 = ROOT / "experiments/yolo/gdt504_semantic_delta_phrase_consistency_atlas/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
PAIR_PROFILES_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
TARGETS_IN = G504 / "gdt504_46_semantic_delta_cards.tsv"

HANDGRIPS_OUT = ART / "gdt505_5_carrier_neutral_handgrips.tsv"
CARRIERS_OUT = ART / "gdt505_55_exact_pair_carriers.tsv"
REGISTER_OUT = ART / "gdt505_15_observed_pair_register_cells.tsv"
TARGET_OUT = ART / "gdt505_11_target_pair_handgrip_cards.tsv"
BETWEEN_OUT = ART / "gdt505_15_pair_between_pattern_summary.tsv"
FRAME_OUT = ART / "gdt505_16_frame_atom_coverage.tsv"
READABLE_OUT = ART / "GDT505_CARRIER_NEUTRAL_PAIR_HANDGRIP_ATLAS.md"
RESULT_OUT = ART / "gdt505_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
PAIR_ORDER = ("P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH")
HANDGRIP_PHRASES = {
    "P+CH": "Setze das zuvor Genannte ein und nimm es.",
    "S+CHD": "Wähle das zuvor Genannte und bearbeite es.",
    "CH+P": "Nimm das zuvor Genannte und setze es ein.",
    "CH+CH": "Nimm das zuvor Genannte zweimal.",
    "CH+SH": "Nimm das zuvor Genannte und halte es.",
}
ACTION_MARKERS = {"P": "setz", "S": "wähl", "CHD": "bearbeit", "CH": "nimm", "SH": "halt"}
STATUS = "FIVE_HANDGRIPS_SURVIVE_ALL_FIFTY_FIVE_OLD_CARRIERS__ELEVEN_TARGETS_MAPPED"
GUARD = "CARRIER_NEUTRAL_ACTION_ORDER_ONLY__FOREIGN_FRAME_VALUES_NOT_TRANSFERRED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def ordered_action_indices(recipe: list[str], pair: str) -> list[int]:
    positions: list[int] = []
    start = 0
    for action in pair.split("+"):
        try:
            position = recipe.index(action, start)
        except ValueError as exc:
            raise ValueError(f"missing ordered action {action} in {'+'.join(recipe)}") from exc
        positions.append(position)
        start = position + 1
    return positions


def phrase_marker_positions(phrase: str, pair: str, *, compressed_repeat: bool = False) -> list[int]:
    lower = phrase.casefold()
    actions = pair.split("+")
    if compressed_repeat and pair == "CH+CH":
        first = lower.find(ACTION_MARKERS["CH"])
        twice = lower.find("zweimal", first + 1)
        return [first, twice]
    positions: list[int] = []
    start = 0
    for action in actions:
        position = lower.find(ACTION_MARKERS[action], start)
        positions.append(position)
        start = position + 1 if position >= 0 else start
    return positions


def argument_mode(row: dict[str, str]) -> str:
    if row["explicit_argument_roots"] != "NONE":
        return "EXPLICIT_ARGUMENTS"
    if row["inherited_argument_root"] != "NONE":
        return "INHERITED_ARGUMENT"
    return "ARGUMENT_FREE"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _profile_fields, pair_profiles = read_tsv(PAIR_PROFILES_IN)
    _target_fields, all_targets = read_tsv(TARGETS_IN)
    if (len(dictionary), len(clauses), len(pair_profiles), len(all_targets)) != (46, 4576, 81, 46):
        raise ValueError("GDT413/GDT416/GDT421/GDT504 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    profile_by_pair = {row["ordered_pair"]: row for row in pair_profiles}
    old_rows = [row for row in clauses if row["explicit_action_roots"].replace("|", "+") in PAIR_ORDER]
    target_rows = [row for row in all_targets if row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT"]
    if (len(old_rows), len(target_rows)) != (55, 11):
        raise ValueError(f"old carrier/target drift: {len(old_rows)}/{len(target_rows)}")

    carriers: list[dict[str, object]] = []
    carriers_by_pair: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in old_rows:
        pair = row["explicit_action_roots"].replace("|", "+")
        recipe = row["component_recipe"].split("+")
        action_positions = ordered_action_indices(recipe, pair)
        before = recipe[: action_positions[0]]
        between = recipe[action_positions[0] + 1 : action_positions[1]]
        after = recipe[action_positions[1] + 1 :]
        frame_atoms = before + between + after
        marker_positions = phrase_marker_positions(row["imperative_clause_de"], pair)
        marker_order_exact = len(marker_positions) == 2 and marker_positions[0] >= 0 and marker_positions[1] > marker_positions[0]
        carrier = {
            "pair_carrier_id": f"G505-C{len(carriers) + 1:02d}",
            "ordered_action_pair": pair,
            "portable_action_trace_de": " → ".join(values[action] for action in pair.split("+")),
            "carrier_neutral_handgrip_de": HANDGRIP_PHRASES[pair],
            "global_running_event_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_class": row["owner_class"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "action_component_positions": ",".join(str(position + 1) for position in action_positions),
            "clause_action_marker_positions": ",".join(str(position + 1) for position in marker_positions),
            "clause_action_order_exact": "YES" if marker_order_exact else "NO",
            "before_action_atoms": "+".join(before) if before else "NONE",
            "between_action_atoms": "+".join(between) if between else "NONE",
            "after_action_atoms": "+".join(after) if after else "NONE",
            "direct_component_adjacency": "YES" if not between else "NO",
            "frame_atom_trace": "+".join(frame_atoms) if frame_atoms else "NONE",
            "frame_value_trace_de": " · ".join(values[atom] for atom in frame_atoms) if frame_atoms else "NONE",
            "argument_mode": argument_mode(row),
            "explicit_argument_roots": row["explicit_argument_roots"],
            "inherited_argument_root": row["inherited_argument_root"],
            "imperative_clause_de": row["imperative_clause_de"],
            "portable_back_projection_de": row["portable_back_projection_de"],
            "roundtrip_exact": row["roundtrip_exact"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        }
        carriers.append(carrier)
        carriers_by_pair[pair].append(carrier)

    target_counts = Counter(
        "+".join(token for token in row["target_action_recipe"].split("+") if token in ACTION_ROOTS)
        for row in target_rows
    )
    handgrips: list[dict[str, object]] = []
    for pair in PAIR_ORDER:
        group = carriers_by_pair[pair]
        profile = profile_by_pair[pair]
        pages = sorted({str(row["physical_page"]) for row in group}, key=page_key)
        registers = [register for register in REGISTERS if any(row["register"] == register for row in group)]
        between_patterns = {str(row["between_action_atoms"]) for row in group}
        frame_atoms = sorted({atom for row in group for atom in str(row["frame_atom_trace"]).split("+") if atom != "NONE"})
        argument_modes = Counter(str(row["argument_mode"]) for row in group)
        handgrips.append({
            "handgrip_id": f"G505-H{len(handgrips) + 1:02d}",
            "ordered_action_pair": pair,
            "portable_action_trace_de": " → ".join(values[action] for action in pair.split("+")),
            "carrier_neutral_handgrip_de": HANDGRIP_PHRASES[pair],
            "old_carrier_event_count": len(group),
            "old_recipe_type_count": len({row["component_recipe"] for row in group}),
            "old_clause_form_count": len({row["imperative_clause_de"] for row in group}),
            "old_surface_count": len({row["surface"] for row in group}),
            "old_page_count": len(pages),
            "old_pages": "|".join(pages),
            "old_register_count": len(registers),
            "old_registers": "|".join(registers),
            "direct_adjacency_event_count": sum(row["direct_component_adjacency"] == "YES" for row in group),
            "separated_action_event_count": sum(row["direct_component_adjacency"] == "NO" for row in group),
            "between_pattern_count": len(between_patterns),
            "between_patterns": "|".join(sorted(between_patterns)),
            "frame_atom_family_count": len(frame_atoms),
            "frame_atom_families": "|".join(frame_atoms),
            "explicit_argument_event_count": argument_modes["EXPLICIT_ARGUMENTS"],
            "inherited_argument_event_count": argument_modes["INHERITED_ARGUMENT"],
            "argument_free_event_count": argument_modes["ARGUMENT_FREE"],
            "gdt421_event_count": profile["event_count"],
            "gdt421_recipe_type_count": profile["exact_recipe_type_count"],
            "gdt421_register_count": profile["register_count"],
            "gdt421_status": profile["status"],
            "gdt504_target_card_count": target_counts[pair],
            "all_old_clause_action_orders_exact": "YES" if all(row["clause_action_order_exact"] == "YES" for row in group) else "NO",
            "all_old_roundtrips_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in group) else "NO",
            "working_root_meaning_changed": "NO",
            "guard": GUARD,
        })

    register_rows: list[dict[str, object]] = []
    for pair in PAIR_ORDER:
        for register in REGISTERS:
            group = [row for row in carriers_by_pair[pair] if row["register"] == register]
            if not group:
                continue
            register_rows.append({
                "pair_register_cell_id": f"G505-R{len(register_rows) + 1:02d}",
                "ordered_action_pair": pair,
                "register": register,
                "carrier_neutral_handgrip_de": HANDGRIP_PHRASES[pair],
                "old_carrier_event_count": len(group),
                "old_recipe_type_count": len({row["component_recipe"] for row in group}),
                "old_clause_form_count": len({row["imperative_clause_de"] for row in group}),
                "old_page_count": len({row["physical_page"] for row in group}),
                "old_pages": "|".join(sorted({str(row["physical_page"]) for row in group}, key=page_key)),
                "direct_adjacency_event_count": sum(row["direct_component_adjacency"] == "YES" for row in group),
                "separated_action_event_count": sum(row["direct_component_adjacency"] == "NO" for row in group),
                "all_clause_action_orders_exact": "YES" if all(row["clause_action_order_exact"] == "YES" for row in group) else "NO",
                "guard": GUARD,
            })

    target_cards: list[dict[str, object]] = []
    carrier_counts_by_pair_register = Counter((str(row["ordered_action_pair"]), str(row["register"])) for row in carriers)
    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    for source in target_rows:
        pair = "+".join(token for token in source["target_action_recipe"].split("+") if token in ACTION_ROOTS)
        summary = handgrip_by_pair[pair]
        marker_positions = phrase_marker_positions(source["target_current_default_phrase_de"], pair, compressed_repeat=pair == "CH+CH")
        visible = len(marker_positions) == 2 and marker_positions[0] >= 0 and marker_positions[1] > marker_positions[0]
        target_register_events = carrier_counts_by_pair_register[(pair, source["target_register"])]
        target_cards.append({
            "target_handgrip_card_id": f"G505-T{len(target_cards) + 1:02d}",
            "source_gdt504_delta_card_id": source["semantic_delta_card_id"],
            "source_gdt502_comparison_card_id": source["source_comparison_card_id"],
            "target_matrix_cell_id": source["target_matrix_cell_id"],
            "target_action_recipe": source["target_action_recipe"],
            "target_register": source["target_register"],
            "ordered_action_pair": pair,
            "carrier_neutral_handgrip_de": HANDGRIP_PHRASES[pair],
            "target_current_default_phrase_de": source["target_current_default_phrase_de"],
            "target_phrase_handgrip_marker_positions": ",".join(str(position + 1) for position in marker_positions),
            "target_phrase_handgrip_visible": "YES" if visible else "NO",
            "old_pair_carrier_event_count": summary["old_carrier_event_count"],
            "old_pair_recipe_type_count": summary["old_recipe_type_count"],
            "old_pair_page_count": summary["old_page_count"],
            "old_pair_register_count": summary["old_register_count"],
            "target_register_old_pair_event_count": target_register_events,
            "handgrip_projection_class": "TARGET_REGISTER_OLD_HANDGRIP" if target_register_events else "CROSS_REGISTER_OLD_HANDGRIP",
            "foreign_carrier_frame_transferred": "NO",
            "target_phrase_changed": "NO",
            "target_evidence_status_retained": source["target_evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    between_rows: list[dict[str, object]] = []
    for pair in PAIR_ORDER:
        for pattern in sorted({str(row["between_action_atoms"]) for row in carriers_by_pair[pair]}):
            group = [row for row in carriers_by_pair[pair] if row["between_action_atoms"] == pattern]
            between_rows.append({
                "between_pattern_id": f"G505-B{len(between_rows) + 1:02d}",
                "ordered_action_pair": pair,
                "between_action_atoms": pattern,
                "between_value_trace_de": "NONE" if pattern == "NONE" else " · ".join(values[atom] for atom in pattern.split("+")),
                "carrier_event_count": len(group),
                "recipe_type_count": len({row["component_recipe"] for row in group}),
                "page_count": len({row["physical_page"] for row in group}),
                "register_count": len({row["register"] for row in group}),
                "direct_component_adjacency": "YES" if pattern == "NONE" else "NO",
                "all_clause_action_orders_exact": "YES" if all(row["clause_action_order_exact"] == "YES" for row in group) else "NO",
                "guard": GUARD,
            })

    frame_counts: Counter[str] = Counter()
    frame_events: dict[str, set[str]] = defaultdict(set)
    frame_pairs: dict[str, set[str]] = defaultdict(set)
    frame_registers: dict[str, set[str]] = defaultdict(set)
    for row in carriers:
        for atom in str(row["frame_atom_trace"]).split("+"):
            if atom == "NONE":
                continue
            frame_counts[atom] += 1
            frame_events[atom].add(str(row["global_running_event_id"]))
            frame_pairs[atom].add(str(row["ordered_action_pair"]))
            frame_registers[atom].add(str(row["register"]))
    frame_rows: list[dict[str, object]] = []
    for atom in sorted(frame_counts):
        frame_rows.append({
            "frame_atom": atom,
            "working_value_de": values[atom],
            "carrier_mention_count": frame_counts[atom],
            "carrier_event_count": len(frame_events[atom]),
            "pair_count": len(frame_pairs[atom]),
            "pairs": "|".join(pair for pair in PAIR_ORDER if pair in frame_pairs[atom]),
            "register_count": len(frame_registers[atom]),
            "registers": "|".join(register for register in REGISTERS if register in frame_registers[atom]),
            "transferred_into_neutral_handgrip": "NO",
            "guard": GUARD,
        })

    if (len(handgrips), len(carriers), len(register_rows), len(target_cards), len(between_rows), len(frame_rows)) != (5, 55, 15, 11, 15, 16):
        raise ValueError("GDT505 output cardinality drift")
    if any(row["clause_action_order_exact"] != "YES" for row in carriers):
        raise ValueError("old carrier phrase action-order failure")
    if any(row["target_phrase_handgrip_visible"] != "YES" for row in target_cards):
        raise ValueError("target phrase handgrip marker failure")

    write_tsv(HANDGRIPS_OUT, handgrips)
    write_tsv(CARRIERS_OUT, carriers)
    write_tsv(REGISTER_OUT, register_rows)
    write_tsv(TARGET_OUT, target_cards)
    write_tsv(BETWEEN_OUT, between_rows)
    write_tsv(FRAME_OUT, frame_rows)

    lines = [
        "# GDT505 — fünf trägerneutrale Paar-Handgriffe",
        "",
        f"Status: `{STATUS}`",
        "",
        "Alle exakten alten Klauseln mit einem der fünf GDT504-Paare werden",
        "gemeinsam gelesen. Der kurze Handgriff enthält nur die gerichteten",
        "Handlungen; Grade, Argumente, Relationen und Reihenfolgefelder bleiben",
        "als fremder Trägerrahmen daneben sichtbar.",
        "",
        "## Fünf Handgriffe",
        "",
    ]
    for row in handgrips:
        lines.extend([
            f'### {row["handgrip_id"]} · `{row["ordered_action_pair"]}`',
            "",
            f'**{row["carrier_neutral_handgrip_de"]}**',
            "",
            f'- Alt: {row["old_carrier_event_count"]} Ereignisse, {row["old_recipe_type_count"]} Rezepte, {row["old_page_count"]} Seiten, {row["old_register_count"]} Register.',
            f'- Komponentenebene: {row["direct_adjacency_event_count"]} direkt, {row["separated_action_event_count"]} getrennt; Zwischenmuster `{row["between_patterns"]}`.',
            f'- Argumente: {row["explicit_argument_event_count"]} explizit, {row["inherited_argument_event_count"]} geerbt, {row["argument_free_event_count"]} frei.',
            f'- GDT504-Ziele: {row["gdt504_target_card_count"]}; alle alten Klauseln behalten die Handlungsreihenfolge.',
            "",
        ])
    lines.extend(["## Elf Zielkarten", ""])
    for row in target_cards:
        lines.append(f'- `{row["target_action_recipe"]}` · {row["target_register"]}: **{row["target_current_default_phrase_de"]}** — `{row["handgrip_projection_class"]}`.')
    lines.extend(["", f"`{GUARD}`", ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    argument_modes = Counter(str(row["argument_mode"]) for row in carriers)
    result = {
        "status": STATUS,
        "carrier_neutral_handgrips": len(handgrips),
        "exact_old_pair_carriers": len(carriers),
        "old_recipe_types": len({row["component_recipe"] for row in carriers}),
        "old_clause_forms": len({row["imperative_clause_de"] for row in carriers}),
        "old_surfaces": len({row["surface"] for row in carriers}),
        "old_pages": len({row["physical_page"] for row in carriers}),
        "old_registers": len({row["register"] for row in carriers}),
        "old_owner_classes": len({row["owner_class"] for row in carriers}),
        "direct_component_adjacency_events": sum(row["direct_component_adjacency"] == "YES" for row in carriers),
        "separated_action_events": sum(row["direct_component_adjacency"] == "NO" for row in carriers),
        "pair_specific_between_patterns": len(between_rows),
        "frame_atom_families": len(frame_rows),
        "explicit_argument_events": argument_modes["EXPLICIT_ARGUMENTS"],
        "inherited_argument_events": argument_modes["INHERITED_ARGUMENT"],
        "argument_free_events": argument_modes["ARGUMENT_FREE"],
        "old_clause_action_orders_exact": sum(row["clause_action_order_exact"] == "YES" for row in carriers),
        "old_clause_roundtrips_exact": sum(row["roundtrip_exact"] == "YES" for row in carriers),
        "observed_pair_register_cells": len(register_rows),
        "mapped_gdt504_target_cards": len(target_cards),
        "target_register_old_handgrips": sum(row["handgrip_projection_class"] == "TARGET_REGISTER_OLD_HANDGRIP" for row in target_cards),
        "cross_register_old_handgrips": sum(row["handgrip_projection_class"] == "CROSS_REGISTER_OLD_HANDGRIP" for row in target_cards),
        "target_phrase_handgrips_visible": sum(row["target_phrase_handgrip_visible"] == "YES" for row in target_cards),
        "foreign_frame_values_transferred": 0,
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
