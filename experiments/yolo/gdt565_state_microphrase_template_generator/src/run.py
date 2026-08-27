#!/usr/bin/env python3
"""Generate every GDT563 state microphrase from a compact template kit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator"
OUT = BASE / "artifacts"
G561 = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts"
G563 = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition/artifacts"
G564 = ROOT / "experiments/yolo/gdt564_state_context_selector_atlas/artifacts"
INPUTS = {
    "state_dictionary": G561 / "gdt561_36_state_atom_dictionary.tsv",
    "state_microphrases": G563 / "gdt563_1656_complete_state_microphrases.tsv",
    "recipe_routes": G564 / "gdt564_402_recipe_selector_routes.tsv",
    "selector_cells": G564 / "gdt564_415_observed_selector_cells.tsv",
}

ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
ARGUMENTS = ("Y", "AIIN", "AIN", "OR")
STATE_CONTROLS = {"OT", "OL", "DY"}
ACTION_SET = set(ACTIONS)
ARGUMENT_SET = set(ARGUMENTS)

ARGUMENT_PHRASES = {
    "Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit",
}
ACTION_TEMPLATES = {
    "OK": ("setze", "setze {argument}"),
    "CH": ("nimm", "nimm {argument}"),
    "SH": ("halte", "halte {argument}"),
    "K": ("gib", "gib {argument}"),
    "S": ("wähle", "wähle {argument}"),
    "CHD": ("bearbeite", "bearbeite {argument}"),
    "T": ("stelle ein", "stelle {argument} ein"),
    "R": ("markiere", "markiere {argument}"),
    "P": ("setze ein", "setze {argument} ein"),
}
STATE_FRAMES = {
    "OL": ("CONTINUE_CURRENT_OPERATION", "Weiter", ""),
    "DY": ("CLOSE_CURRENT_OPERATION", "", "abschließen"),
    "OT": ("ADVANCE_TO_NEXT_OPERATION", "Danach", ""),
    "OT+DY": ("ADVANCE_THEN_CLOSE", "Danach", "abschließen"),
    "OL+DY": ("CONTINUE_THEN_CLOSE", "Weiter", "abschließen"),
    "OT+OL": ("ADVANCE_THEN_CONTINUE", "Danach", "weiterführen"),
    "OL+OL": ("DOUBLE_CONTINUATION_BRIDGE", "Weiter", "nochmals weiterführen"),
    "OL+OT": ("CONTINUE_THEN_ADVANCE", "Weiter", "danach nächsten Gang eröffnen"),
    "DY+OL": ("CLOSE_THEN_CONTINUE", "", "abschließen; danach weiterführen"),
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def packed(values: set[str] | list[str]) -> str:
    return " || ".join(sorted(set(values)))


def render_argument(roots: list[str]) -> tuple[str, str]:
    if not roots:
        return "NONE", "NONE"
    if roots == ["Y", "Y"]:
        return "die beiden Posten", "DOUBLE_Y"
    phrases = [ARGUMENT_PHRASES[root] for root in roots]
    if len(phrases) == 1:
        return phrases[0], "SINGLE"
    return ", ".join(phrases[:-1]) + " und " + phrases[-1], "PAIR"


def action_units(atoms: list[str]) -> list[tuple[str, int]]:
    units: list[tuple[str, int]] = []
    index = 0
    while index < len(atoms):
        atom = atoms[index]
        if atom not in ACTION_SET:
            index += 1
            continue
        repeat = 1
        while index + repeat < len(atoms) and atoms[index + repeat] == atom:
            repeat += 1
        units.append((atom, repeat))
        index += repeat
    return units


def render_action(root: str, argument: str) -> str:
    no_object, with_object = ACTION_TEMPLATES[root]
    return with_object.format(argument=argument) if argument != "NONE" else no_object


def render_action_chain(row: dict[str, str], argument: str) -> tuple[str, str, list[str], bool]:
    recipe_atoms = row["recipe"].split("+")
    if row["written_action_roots"] == "NONE":
        roots = split_roots(row["effective_action_roots"])
        units = [(root, 1) for root in roots]
    else:
        roots = [atom for atom in recipe_atoms if atom in ACTION_SET]
        units = action_units(recipe_atoms)
    if not roots:
        return "NONE", "NO_ACTION", [], False
    rendered: list[str] = []
    expanded: list[str] = []
    compressed = False
    for root, repeat in units:
        phrase = render_action(root, argument)
        if repeat == 1:
            rendered.append(phrase)
        elif repeat == 2:
            rendered.append(phrase + " zweimal")
            compressed = True
        else:
            rendered.append(phrase + f" {repeat}-mal")
            compressed = True
        expanded.extend([root] * repeat)
    if expanded != roots:
        raise RuntimeError(f"Action roundtrip failed at {row['event_id']}")
    topology = "+".join("A" if repeat == 1 else f"Ax{repeat}" for _, repeat in units)
    return " und ".join(rendered), topology, roots, compressed


def compose(prefix: str, base: str, modifiers: str, suffix: str) -> str:
    parts = [part for part in (base if base != "NONE" else "", modifiers if modifiers != "NONE" else "", suffix) if part]
    if prefix:
        phrase = f"{prefix}: " + "; ".join(parts) if parts else prefix
    else:
        phrase = "; ".join(parts)
    return phrase[0].upper() + phrase[1:] + "." if phrase else "Fortfahren."


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    dictionary = read_tsv(INPUTS["state_dictionary"])
    source = read_tsv(INPUTS["state_microphrases"])
    recipe_routes = read_tsv(INPUTS["recipe_routes"])
    selector_source = read_tsv(INPUTS["selector_cells"])
    if [len(dictionary), len(source), len(recipe_routes), len(selector_source)] != [36, 1656, 402, 415]:
        raise RuntimeError("Input count drift")
    dictionary_by_atom = {row["atom"]: row for row in dictionary}
    fragments = {atom: row["default_fragment_de"] for atom, row in dictionary_by_atom.items()}
    route_by_recipe = {row["recipe"]: row for row in recipe_routes}
    selector_by_recipe_phrase = {(row["recipe"], row["owner_free_microphrase_de"]): row for row in selector_source}
    if len(selector_by_recipe_phrase) != 415:
        raise RuntimeError("GDT564 selector phrase cells are not unique")

    action_usage = Counter()
    argument_usage = Counter()
    modifier_atom_usage = Counter()
    state_usage = Counter()
    combinator_usage = Counter()
    replay_rows: list[dict[str, object]] = []

    for source_row in sorted(source, key=lambda row: int(row["state_microphrase_ordinal"])):
        atoms = source_row["recipe"].split("+")
        if any(atom not in dictionary_by_atom for atom in atoms):
            raise RuntimeError(f"Unknown atom at {source_row['event_id']}")
        argument_roots = split_roots(source_row["effective_argument_roots"])
        argument, argument_topology = render_argument(argument_roots)
        action_chain, action_topology, action_roots, repeat_compressed = render_action_chain(source_row, argument)
        modifier_atoms = [atom for atom in atoms if atom not in ACTION_SET | ARGUMENT_SET | STATE_CONTROLS]
        modifier_phrase = "; ".join(fragments[atom] for atom in modifier_atoms) or "NONE"
        state_sequence = source_row["state_marker_sequence"]
        state_role, prefix, suffix = STATE_FRAMES[state_sequence]
        if action_roots:
            base_mode = "ACTION_CHAIN"
            base_phrase = action_chain
        elif argument_roots:
            base_mode = "ARGUMENT_REFERENCE"
            base_phrase = "Bezug auf " + argument
        else:
            base_mode = "EMPTY_BASE"
            base_phrase = "NONE"
        generated = compose(prefix, base_phrase, modifier_phrase, suffix)
        prefix_presence = "PREFIX" if prefix else "NO_PREFIX"
        suffix_presence = "SUFFIX" if suffix else "NO_SUFFIX"
        modifier_presence = "MODIFIER" if modifier_atoms else "NO_MODIFIER"
        outer_signature = "__".join((prefix_presence, base_mode, modifier_presence, suffix_presence))
        modifier_type_sequence = "+".join(dictionary_by_atom[atom]["typed_category"] for atom in modifier_atoms) or "NONE"
        structural_signature = " || ".join((state_sequence, base_mode, action_topology, argument_topology, modifier_type_sequence))

        state_usage[state_sequence] += 1
        action_usage.update(action_roots)
        argument_usage.update(argument_roots)
        modifier_atom_usage.update(modifier_atoms)
        combinator_usage["ARGUMENT_COORDINATION"] += int(bool(argument_roots) and argument_roots != ["Y", "Y"])
        combinator_usage["DOUBLE_POSTEN"] += int(argument_roots == ["Y", "Y"])
        combinator_usage["ACTION_CHAIN"] += int(bool(action_roots))
        combinator_usage["ADJACENT_ACTION_REPEAT"] += int(repeat_compressed)
        combinator_usage["MODIFIER_SEQUENCE"] += int(bool(modifier_atoms))
        combinator_usage["SENTENCE_ASSEMBLY"] += 1

        source_phrase = source_row["owner_free_microphrase_de"]
        if generated == source_phrase:
            replay_status = "EXACT_SOURCE_REPLAY"
        elif (
            source_row["event_id"] == "G407-E1000"
            and source_phrase == "Weiter: gib den Posten und den Posten; hier."
            and generated == "Weiter: gib die beiden Posten; hier."
        ):
            replay_status = "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION"
        else:
            replay_status = "UNEXPECTED_REPLAY_DRIFT"
        replay_rows.append({
            "template_replay_ordinal": len(replay_rows) + 1,
            "event_id": source_row["event_id"],
            "statement_id": source_row["statement_id"],
            "physical_page": source_row["physical_page"],
            "register": source_row["register"],
            "surface": source_row["surface"],
            "recipe": source_row["recipe"],
            "state_marker_sequence": state_sequence,
            "state_frame_role": state_role,
            "sentence_prefix_de": prefix or "NONE",
            "sentence_suffix_de": suffix or "NONE",
            "base_mode": base_mode,
            "effective_action_roots": source_row["effective_action_roots"],
            "action_topology": action_topology,
            "generated_action_chain_de": action_chain,
            "effective_argument_roots": source_row["effective_argument_roots"],
            "argument_topology": argument_topology,
            "generated_argument_phrase_de": argument,
            "modifier_atoms": "+".join(modifier_atoms) or "NONE",
            "modifier_type_sequence": modifier_type_sequence,
            "generated_modifier_phrase_de": modifier_phrase,
            "outer_template_signature": outer_signature,
            "structural_template_signature": structural_signature,
            "generated_microphrase_de": generated,
            "source_microphrase_de": source_phrase,
            "exact_replay": "YES" if generated == source_phrase else "NO",
            "replay_status": replay_status,
            "written_atom_alignment": source_row["written_atom_alignment"],
            "guard": "ATOMIC_TEMPLATE_REPLAY__NO_LEARNED_LONG_PHRASE",
        })

    outer_signatures = sorted({str(row["outer_template_signature"]) for row in replay_rows})
    outer_ids = {signature: f"GDT565-O{index:02d}" for index, signature in enumerate(outer_signatures, 1)}
    structural_signatures = sorted({str(row["structural_template_signature"]) for row in replay_rows})
    structural_ids = {signature: f"GDT565-T{index:03d}" for index, signature in enumerate(structural_signatures, 1)}
    for row in replay_rows:
        row["outer_template_id"] = outer_ids[str(row["outer_template_signature"])]
        row["structural_template_id"] = structural_ids[str(row["structural_template_signature"])]

    renderer_rows: list[dict[str, object]] = []

    def add_renderer(card_class: str, selector: str, source_atoms: str, no_object: str, with_object: str, prefix: str, suffix: str, rule: str, usage: int) -> None:
        renderer_rows.append({
            "renderer_card_ordinal": len(renderer_rows) + 1,
            "renderer_card_id": f"GDT565-R{len(renderer_rows) + 1:02d}",
            "card_class": card_class,
            "selector": selector,
            "source_atoms": source_atoms,
            "template_no_object_de": no_object,
            "template_with_object_de": with_object,
            "prefix_de": prefix,
            "suffix_de": suffix,
            "render_rule": rule,
            "usage_count": usage,
            "guard": "SMALL_RENDER_CARD__ROOT_VALUES_UNCHANGED",
        })

    for sequence, (role, prefix, suffix) in STATE_FRAMES.items():
        add_renderer("STATE_FRAME", sequence, sequence, "NONE", "NONE", prefix or "NONE", suffix or "NONE", role, state_usage[sequence])
    for root in ACTIONS:
        no_object, with_object = ACTION_TEMPLATES[root]
        add_renderer("ACTION_TEMPLATE", root, root, no_object, with_object, "NONE", "NONE", "SELECT_OBJECT_FORM_IF_ARGUMENT_PRESENT", action_usage[root])
    for root in ARGUMENTS:
        add_renderer("ARGUMENT_CARD", root, root, ARGUMENT_PHRASES[root], ARGUMENT_PHRASES[root], "NONE", "NONE", "INSERT_ARGUMENT_PHRASE", argument_usage[root])
    modifier_groups: dict[str, list[str]] = defaultdict(list)
    for atom, row in dictionary_by_atom.items():
        if atom not in ACTION_SET | ARGUMENT_SET | STATE_CONTROLS:
            modifier_groups[row["default_fragment_de"]].append(atom)
    for fragment in sorted(modifier_groups):
        atoms = sorted(modifier_groups[fragment])
        add_renderer("MODIFIER_FRAGMENT", fragment, "+".join(atoms), fragment, fragment, "NONE", "NONE", "RETAIN_WRITTEN_MODIFIER_ORDER", sum(modifier_atom_usage[atom] for atom in atoms))
    combinators = [
        ("ARGUMENT_COORDINATION", "join multiple argument phrases with comma and final und"),
        ("DOUBLE_POSTEN", "Y|Y becomes die beiden Posten"),
        ("ACTION_CHAIN", "join ordered action units with und"),
        ("ADJACENT_ACTION_REPEAT", "compress only adjacent identical action atoms with zweimal"),
        ("MODIFIER_SEQUENCE", "join ordered modifier fragments with semicolon"),
        ("SENTENCE_ASSEMBLY", "prefix colon plus base/modifier/suffix semicolons, initial capital and final period"),
    ]
    for selector, rule in combinators:
        add_renderer("COMBINATOR", selector, "NONE", "NONE", "NONE", "NONE", "NONE", rule, combinator_usage[selector])
    if len(renderer_rows) != 42:
        raise RuntimeError(f"Renderer card count drift: {len(renderer_rows)}")

    if any(row["replay_status"] == "UNEXPECTED_REPLAY_DRIFT" for row in replay_rows):
        raise RuntimeError("Unexpected template replay drift")
    normalization_rows = [
        {
            "normalization_ordinal": index,
            "event_id": row["event_id"],
            "recipe": row["recipe"],
            "effective_action_roots": row["effective_action_roots"],
            "effective_argument_roots": row["effective_argument_roots"],
            "old_microphrase_de": row["source_microphrase_de"],
            "normalized_microphrase_de": row["generated_microphrase_de"],
            "normalization_rule": "Y|Y_ALWAYS_RAISES_TO_DIE_BEIDEN_POSTEN",
            "semantic_change": "NO__GERMAN_EDITORIAL_CONSISTENCY_ONLY",
            "guard": "ONE_NAMED_NORMALIZATION__NO_ROOT_OR_ATOM_CHANGE",
        }
        for index, row in enumerate(
            [row for row in replay_rows if row["replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION"], 1
        )
    ]
    if len(normalization_rows) != 1:
        raise RuntimeError(f"Editorial normalization count drift: {len(normalization_rows)}")

    by_recipe_phrase: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in replay_rows:
        by_recipe_phrase[(str(row["recipe"]), str(row["generated_microphrase_de"]))].append(row)
    if len(by_recipe_phrase) != 716:
        raise RuntimeError(f"Recipe-context cell drift: {len(by_recipe_phrase)}")
    cell_rows: list[dict[str, object]] = []
    for ordinal, ((recipe, phrase), members) in enumerate(sorted(by_recipe_phrase.items()), 1):
        route = route_by_recipe[recipe]
        if route["variability_status"] == "FIXED":
            source_cell_id = "FIXED_RECIPE"
        else:
            source_cell_ids = {
                selector_by_recipe_phrase[(recipe, str(member["source_microphrase_de"]))]["selector_cell_id"]
                for member in members
            }
            if len(source_cell_ids) != 1:
                raise RuntimeError(f"GDT564 selector-cell disagreement for {recipe}: {source_cell_ids}")
            source_cell_id = next(iter(source_cell_ids))
        for field in ("state_marker_sequence", "base_mode", "action_topology", "argument_topology", "modifier_atoms", "modifier_type_sequence", "outer_template_id", "structural_template_id"):
            if len({str(row[field]) for row in members}) != 1:
                raise RuntimeError(f"Template cell disagreement for {recipe}: {field}")
        first = members[0]
        cell_rows.append({
            "recipe_context_cell_ordinal": ordinal,
            "recipe_context_cell_id": f"GDT565-C{ordinal:04d}",
            "gdt564_source_cell_id": source_cell_id,
            "recipe": recipe,
            "portable_route": route["portable_route"],
            "event_count": len(members),
            "effective_action_signatures": packed({str(row["effective_action_roots"]) for row in members}),
            "effective_argument_signatures": packed({str(row["effective_argument_roots"]) for row in members}),
            "state_marker_sequence": first["state_marker_sequence"],
            "base_mode": first["base_mode"],
            "action_topology": first["action_topology"],
            "argument_topology": first["argument_topology"],
            "modifier_atoms": first["modifier_atoms"],
            "modifier_type_sequence": first["modifier_type_sequence"],
            "outer_template_id": first["outer_template_id"],
            "structural_template_id": first["structural_template_id"],
            "generated_owner_free_microphrase_de": phrase,
            "source_microphrases_de": packed({str(row["source_microphrase_de"]) for row in members}),
            "event_ids": packed({str(row["event_id"]) for row in members}),
            "physical_page_count": len({str(row["physical_page"]) for row in members}),
            "physical_pages": packed({str(row["physical_page"]) for row in members}),
            "register_count": len({str(row["register"]) for row in members}),
            "registers": packed({str(row["register"]) for row in members}),
            "exact_replay_event_count": sum(row["exact_replay"] == "YES" for row in members),
            "normalized_event_count": sum(row["replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" for row in members),
            "all_events_accounted": "YES" if all(row["replay_status"] != "UNEXPECTED_REPLAY_DRIFT" for row in members) else "NO",
            "guard": "RECIPE_CONTEXT_CELL_GENERATED_FROM_RENDERER_CARDS",
        })

    def profile_rows(field: str, id_field: str, output_name: str) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in replay_rows:
            grouped[str(row[field])].append(row)
        output: list[dict[str, object]] = []
        for signature, members in sorted(grouped.items()):
            output.append({
                id_field: str(members[0][id_field]) if id_field in members[0] else output_name + f"-{len(output)+1:03d}",
                "signature": signature,
                "event_count": len(members),
                "recipe_count": len({str(row["recipe"]) for row in members}),
                "recipe_context_cell_count": len({(str(row["recipe"]), str(row["source_microphrase_de"])) for row in members}),
                "physical_page_count": len({str(row["physical_page"]) for row in members}),
                "register_count": len({str(row["register"]) for row in members}),
                "example_microphrases_de": packed({str(row["source_microphrase_de"]) for row in members})[:1600].rstrip(),
            })
        return output

    outer_rows = profile_rows("outer_template_signature", "outer_template_id", "OUTER")
    structural_rows = profile_rows("structural_template_signature", "structural_template_id", "STRUCTURAL")

    action_profile_rows: list[dict[str, object]] = []
    for topology, members in sorted(defaultdict(list, {key: [row for row in replay_rows if row["action_topology"] == key] for key in {str(row["action_topology"]) for row in replay_rows}}).items()):
        action_profile_rows.append({
            "action_topology": topology,
            "event_count": len(members),
            "distinct_effective_action_signature_count": len({str(row["effective_action_roots"]) for row in members}),
            "distinct_rendered_action_chain_count": len({str(row["generated_action_chain_de"]) for row in members}),
            "example_action_chains_de": packed({str(row["generated_action_chain_de"]) for row in members})[:1600].rstrip(),
        })
    argument_profile_rows: list[dict[str, object]] = []
    for topology in sorted({str(row["argument_topology"]) for row in replay_rows}):
        members = [row for row in replay_rows if row["argument_topology"] == topology]
        argument_profile_rows.append({
            "argument_topology": topology,
            "event_count": len(members),
            "distinct_effective_argument_signature_count": len({str(row["effective_argument_roots"]) for row in members}),
            "distinct_rendered_argument_phrase_count": len({str(row["generated_argument_phrase_de"]) for row in members}),
            "argument_signatures": packed({str(row["effective_argument_roots"]) for row in members}),
            "argument_phrases_de": packed({str(row["generated_argument_phrase_de"]) for row in members}),
        })
    modifier_type_profile_rows: list[dict[str, object]] = []
    for sequence in sorted({str(row["modifier_type_sequence"]) for row in replay_rows}):
        members = [row for row in replay_rows if row["modifier_type_sequence"] == sequence]
        modifier_type_profile_rows.append({
            "modifier_type_sequence": sequence,
            "event_count": len(members),
            "distinct_modifier_atom_sequence_count": len({str(row["modifier_atoms"]) for row in members}),
            "distinct_modifier_phrase_count": len({str(row["generated_modifier_phrase_de"]) for row in members}),
            "example_modifier_atom_sequences": packed({str(row["modifier_atoms"]) for row in members})[:1400].rstrip(),
            "example_modifier_phrases_de": packed({str(row["generated_modifier_phrase_de"]) for row in members})[:1400].rstrip(),
        })

    recurrent_structural = [row for row in structural_rows if int(row["event_count"]) > 1]
    result = {
        "status": "PASS_1655_EXACT_REPLAYS__ONE_EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION__716_CELLS__42_RENDERER_CARDS__168_STRUCTURAL_TEMPLATES",
        "source_state_card_count": len(source),
        "exact_replay_count": sum(row["exact_replay"] == "YES" for row in replay_rows),
        "editorial_normalization_count": len(normalization_rows),
        "unexpected_replay_drift_count": sum(row["replay_status"] == "UNEXPECTED_REPLAY_DRIFT" for row in replay_rows),
        "distinct_owner_free_microphrase_count": len({row["source_microphrase_de"] for row in replay_rows}),
        "distinct_generated_microphrase_count": len({row["generated_microphrase_de"] for row in replay_rows}),
        "recipe_context_cell_count": len(cell_rows),
        "fixed_recipe_context_cell_count": sum(row["gdt564_source_cell_id"] == "FIXED_RECIPE" for row in cell_rows),
        "variable_recipe_context_cell_count": sum(row["gdt564_source_cell_id"] != "FIXED_RECIPE" for row in cell_rows),
        "renderer_card_count": len(renderer_rows),
        "state_frame_card_count": sum(row["card_class"] == "STATE_FRAME" for row in renderer_rows),
        "action_template_card_count": sum(row["card_class"] == "ACTION_TEMPLATE" for row in renderer_rows),
        "argument_card_count": sum(row["card_class"] == "ARGUMENT_CARD" for row in renderer_rows),
        "modifier_fragment_card_count": sum(row["card_class"] == "MODIFIER_FRAGMENT" for row in renderer_rows),
        "combinator_card_count": sum(row["card_class"] == "COMBINATOR" for row in renderer_rows),
        "modifier_source_atom_count": len(modifier_atom_usage),
        "state_frame_count": len(STATE_FRAMES),
        "outer_template_count": len(outer_rows),
        "structural_template_count": len(structural_rows),
        "recurrent_structural_template_count": len(recurrent_structural),
        "recurrent_structural_template_event_count": sum(int(row["event_count"]) for row in recurrent_structural),
        "action_topology_count": len(action_profile_rows),
        "argument_topology_count": len(argument_profile_rows),
        "modifier_type_sequence_count": len(modifier_type_profile_rows),
        "exact_modifier_atom_sequence_count": len({row["modifier_atoms"] for row in replay_rows}),
        "distinct_generated_action_chain_count": len({row["generated_action_chain_de"] for row in replay_rows}),
        "distinct_generated_modifier_phrase_count": len({row["generated_modifier_phrase_de"] for row in replay_rows}),
        "visible_action_slot_count": sum(int(row["written_action_slot_count"]) for row in source),
        "effective_action_template_use_count": sum(action_usage.values()),
        "effective_argument_root_use_count": sum(argument_usage.values()),
        "modifier_atom_use_count": sum(modifier_atom_usage.values()),
        "all_renderer_cards_used": all(int(row["usage_count"]) > 0 for row in renderer_rows),
        "all_recipe_context_cells_accounted": all(row["all_events_accounted"] == "YES" for row in cell_rows),
        "new_pages": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "editorial_microphrase_changes": 1,
        "learned_long_phrase_templates": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt565_1656_template_replay.tsv", replay_rows)
    write_tsv(OUT / "gdt565_716_recipe_context_template_cells.tsv", cell_rows)
    write_tsv(OUT / "gdt565_42_renderer_cards.tsv", renderer_rows)
    write_tsv(OUT / "gdt565_11_outer_template_profiles.tsv", outer_rows)
    write_tsv(OUT / "gdt565_168_structural_template_profiles.tsv", structural_rows)
    write_tsv(OUT / "gdt565_7_action_topology_profiles.tsv", action_profile_rows)
    write_tsv(OUT / "gdt565_4_argument_topology_profiles.tsv", argument_profile_rows)
    write_tsv(OUT / "gdt565_46_modifier_type_profiles.tsv", modifier_type_profile_rows)
    write_tsv(OUT / "gdt565_1_editorial_normalization.tsv", normalization_rows)

    top_structural = sorted(structural_rows, key=lambda row: (-int(row["event_count"]), str(row["signature"])))[:12]
    book = [
        "# GDT565 – kleiner Satzgenerator für alle1.656 Zustandskarten",
        "",
        "## Ergebnis",
        "",
        "1.655 GDT563-Mikrophrasen werden bytegenau aus42 kleinen Renderer-Karten erzeugt.",
        "Eine einzige alte Doppelargument-Zeile wird von „den Posten und den Posten“ zu „die beiden",
        "Posten“ vereinheitlicht. Die607 verschiedenen Quellphrasen und716 Rezept-Kontext-Lesungen brauchen keine",
        "gelernten Langsätze.",
        "",
        "```text",
        " 9 Zustandsrahmen",
        " 9 Handlungsschablonen",
        " 4 Argumentkarten",
        "14 Modifikatorfragmente (für20 geschriebene Modifikatoratome)",
        " 6 Verknüpfungsregeln",
        "──",
        "42 Renderer-Karten",
        "```",
        "",
        "## Äußerer Satzbau",
        "",
        f"Nur{len(outer_rows)} äußere Muster kombinieren Präfix, Basismodus, Modifikatorblock und Suffix.",
        "Der Basismodus ist Handlungskette, Argumentbezug oder leere Basis. Darin arbeiten7",
        "Handlungstopologien,4 Argumenttopologien und46 Modifikatortypfolgen.",
        "",
        "## Wiederkehrende Struktur",
        "",
        f"Die genaue abstrakte Signatur besitzt{len(structural_rows)} Varianten. {len(recurrent_structural)} davon wiederholen sich",
        f"und tragen{sum(int(row['event_count']) for row in recurrent_structural)}/1656 Karten. Nur{1656 - sum(int(row['event_count']) for row in recurrent_structural)} Karten stehen auf einer einmaligen Struktur.",
        "",
        "| Struktur | Karten | Rezepte | Beispiel |",
        "|---|---:|---:|---|",
    ]
    for row in top_structural:
        example = str(row["example_microphrases_de"]).split(" || ")[0].replace("|", "\\|")
        book.append(f"| `{row['signature']}` | {row['event_count']} | {row['recipe_count']} | {example} |")
    book += [
        "",
        "## Expansion statt Langwörterbuch",
        "",
        f"Neun Handlungswurzeln plus die Kettenregeln erzeugen{result['distinct_generated_action_chain_count']} beobachtete Handlungsketten.",
        f"Vierzehn Modifikatorfragmente plus die Reihenfolgeregel erzeugen{result['distinct_generated_modifier_phrase_count']} beobachtete Modifikatorphrasen.",
        "Die Zustandsrahmen setzen Weiter/Danach/Abschluss außen herum. Genau dort entsteht die",
        "scheinbare Satzkomplexität; sie sitzt nicht in einer einzelnen Voynich-Sequenz.",
        "",
        "## Arbeitsregel",
        "",
        "1. GDT564 wählt offene Handlung und/oder Argument.",
        "2. GDT565 setzt die Handlungsschablone und das Argument ein.",
        "3. Geschriebene Modifikatoratome bleiben in ihrer Reihenfolge.",
        "4. Der Zustandsrahmen fügt Präfix und Suffix an.",
        "",
        "Jede Zeile behält Rezept, Atom-Ausrichtung, Generatorzustand und Quellphrase. Die eine",
        "Normalisierung ändert nur deutsche Glätte, keine Root- oder Argumentstruktur. Keine neue",
        "Seite, Wurzel oder gelernte Ganzsatzkarte wird verwendet.",
        "",
    ]
    (OUT / "GDT565_TEMPLATE_GENERATOR_BOOK.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt565_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
