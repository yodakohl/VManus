#!/usr/bin/env python3
"""Independently validate the GDT565 state-microphrase template generator."""

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
BASE = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt565_validation.json"
G561 = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts"
G563 = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition/artifacts"
G564 = ROOT / "experiments/yolo/gdt564_state_context_selector_atlas/artifacts"
INPUTS = {
    "state_dictionary": G561 / "gdt561_36_state_atom_dictionary.tsv",
    "state_microphrases": G563 / "gdt563_1656_complete_state_microphrases.tsv",
    "recipe_routes": G564 / "gdt564_402_recipe_selector_routes.tsv",
    "selector_cells": G564 / "gdt564_415_observed_selector_cells.tsv",
}
ARTIFACTS = {
    "gdt565_1656_template_replay.tsv": OUT / "gdt565_1656_template_replay.tsv",
    "gdt565_716_recipe_context_template_cells.tsv": OUT / "gdt565_716_recipe_context_template_cells.tsv",
    "gdt565_42_renderer_cards.tsv": OUT / "gdt565_42_renderer_cards.tsv",
    "gdt565_11_outer_template_profiles.tsv": OUT / "gdt565_11_outer_template_profiles.tsv",
    "gdt565_168_structural_template_profiles.tsv": OUT / "gdt565_168_structural_template_profiles.tsv",
    "gdt565_7_action_topology_profiles.tsv": OUT / "gdt565_7_action_topology_profiles.tsv",
    "gdt565_4_argument_topology_profiles.tsv": OUT / "gdt565_4_argument_topology_profiles.tsv",
    "gdt565_46_modifier_type_profiles.tsv": OUT / "gdt565_46_modifier_type_profiles.tsv",
    "gdt565_1_editorial_normalization.tsv": OUT / "gdt565_1_editorial_normalization.tsv",
    "GDT565_TEMPLATE_GENERATOR_BOOK.md": OUT / "GDT565_TEMPLATE_GENERATOR_BOOK.md",
    "gdt565_result.json": OUT / "gdt565_result.json",
}

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATES = {"OT", "OL", "DY"}
ARG_TEXT = {"Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit"}
ACTION_TEXT = {
    "OK": ("setze", "setze {argument}"), "CH": ("nimm", "nimm {argument}"),
    "SH": ("halte", "halte {argument}"), "K": ("gib", "gib {argument}"),
    "S": ("wähle", "wähle {argument}"), "CHD": ("bearbeite", "bearbeite {argument}"),
    "T": ("stelle ein", "stelle {argument} ein"), "R": ("markiere", "markiere {argument}"),
    "P": ("setze ein", "setze {argument} ein"),
}
FRAMES = {
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def argument_phrase(values: list[str]) -> tuple[str, str]:
    if not values:
        return "NONE", "NONE"
    if values == ["Y", "Y"]:
        return "die beiden Posten", "DOUBLE_Y"
    pieces = [ARG_TEXT[value] for value in values]
    return (pieces[0], "SINGLE") if len(pieces) == 1 else (", ".join(pieces[:-1]) + " und " + pieces[-1], "PAIR")


def units(atoms: list[str]) -> list[tuple[str, int]]:
    output = []
    index = 0
    while index < len(atoms):
        if atoms[index] not in ACTIONS:
            index += 1
            continue
        root = atoms[index]
        count = 1
        while index + count < len(atoms) and atoms[index + count] == root:
            count += 1
        output.append((root, count))
        index += count
    return output


def reconstruct(row: dict[str, str], fragments: dict[str, str], categories: dict[str, str]) -> dict[str, str]:
    atoms = row["recipe"].split("+")
    arg_roots = roots(row["effective_argument_roots"])
    argument, arg_topology = argument_phrase(arg_roots)
    if row["written_action_roots"] == "NONE":
        action_roots = roots(row["effective_action_roots"])
        action_units = [(root, 1) for root in action_roots]
    else:
        action_roots = [atom for atom in atoms if atom in ACTIONS]
        action_units = units(atoms)
    action_parts = []
    expanded = []
    compressed = False
    for root, count in action_units:
        no_object, with_object = ACTION_TEXT[root]
        phrase = with_object.format(argument=argument) if argument != "NONE" else no_object
        if count == 1:
            action_parts.append(phrase)
        elif count == 2:
            action_parts.append(phrase + " zweimal")
            compressed = True
        else:
            action_parts.append(phrase + f" {count}-mal")
            compressed = True
        expanded.extend([root] * count)
    if expanded != action_roots:
        raise RuntimeError("Action roundtrip failure")
    action_chain = " und ".join(action_parts) or "NONE"
    action_topology = "+".join("A" if count == 1 else f"Ax{count}" for _, count in action_units) or "NO_ACTION"
    modifier_atoms = [atom for atom in atoms if atom not in ACTIONS | ARGUMENTS | STATES]
    modifier = "; ".join(fragments[atom] for atom in modifier_atoms) or "NONE"
    modifier_types = "+".join(categories[atom] for atom in modifier_atoms) or "NONE"
    state_role, prefix, suffix = FRAMES[row["state_marker_sequence"]]
    if action_roots:
        base_mode, base = "ACTION_CHAIN", action_chain
    elif arg_roots:
        base_mode, base = "ARGUMENT_REFERENCE", "Bezug auf " + argument
    else:
        base_mode, base = "EMPTY_BASE", "NONE"
    parts = [part for part in (base if base != "NONE" else "", modifier if modifier != "NONE" else "", suffix) if part]
    if prefix:
        phrase = f"{prefix}: " + "; ".join(parts) if parts else prefix
    else:
        phrase = "; ".join(parts)
    generated = phrase[0].upper() + phrase[1:] + "." if phrase else "Fortfahren."
    outer = "__".join(("PREFIX" if prefix else "NO_PREFIX", base_mode, "MODIFIER" if modifier_atoms else "NO_MODIFIER", "SUFFIX" if suffix else "NO_SUFFIX"))
    structural = " || ".join((row["state_marker_sequence"], base_mode, action_topology, arg_topology, modifier_types))
    return {
        "state_frame_role": state_role,
        "base_mode": base_mode,
        "action_topology": action_topology,
        "generated_action_chain_de": action_chain,
        "argument_topology": arg_topology,
        "generated_argument_phrase_de": argument,
        "modifier_atoms": "+".join(modifier_atoms) or "NONE",
        "modifier_type_sequence": modifier_types,
        "generated_modifier_phrase_de": modifier,
        "outer_template_signature": outer,
        "structural_template_signature": structural,
        "generated_microphrase_de": generated,
        "compressed": "YES" if compressed else "NO",
    }


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    dictionary = read_tsv(INPUTS["state_dictionary"])
    source = read_tsv(INPUTS["state_microphrases"])
    routes = read_tsv(INPUTS["recipe_routes"])
    selector_source = read_tsv(INPUTS["selector_cells"])
    replay = read_tsv(ARTIFACTS["gdt565_1656_template_replay.tsv"])
    cells = read_tsv(ARTIFACTS["gdt565_716_recipe_context_template_cells.tsv"])
    renderer = read_tsv(ARTIFACTS["gdt565_42_renderer_cards.tsv"])
    outer = read_tsv(ARTIFACTS["gdt565_11_outer_template_profiles.tsv"])
    structural = read_tsv(ARTIFACTS["gdt565_168_structural_template_profiles.tsv"])
    action_profiles = read_tsv(ARTIFACTS["gdt565_7_action_topology_profiles.tsv"])
    argument_profiles = read_tsv(ARTIFACTS["gdt565_4_argument_topology_profiles.tsv"])
    modifier_profiles = read_tsv(ARTIFACTS["gdt565_46_modifier_type_profiles.tsv"])
    normalizations = read_tsv(ARTIFACTS["gdt565_1_editorial_normalization.tsv"])
    result = json.loads(ARTIFACTS["gdt565_result.json"].read_text(encoding="utf-8"))
    fragments = {row["atom"]: row["default_fragment_de"] for row in dictionary}
    categories = {row["atom"]: row["typed_category"] for row in dictionary}

    check("input_counts", [len(dictionary), len(source), len(routes), len(selector_source)] == [36, 1656, 402, 415], [len(dictionary), len(source), len(routes), len(selector_source)])
    check("artifact_counts", [len(replay), len(cells), len(renderer), len(outer), len(structural), len(action_profiles), len(argument_profiles), len(modifier_profiles), len(normalizations)] == [1656, 716, 42, 11, 168, 7, 4, 46, 1], [len(replay), len(cells), len(renderer), len(outer), len(structural), len(action_profiles), len(argument_profiles), len(modifier_profiles), len(normalizations)])
    check("sealed_pages_absent", not {row["physical_page"] for row in source}.intersection({"f84", "f84r"}), None)
    source_by_id = {row["event_id"]: row for row in source}
    replay_by_id = {row["event_id"]: row for row in replay}
    check("event_keys_unique_and_exact", len(source_by_id) == len(source) and len(replay_by_id) == len(replay) and set(source_by_id) == set(replay_by_id), [len(source_by_id), len(replay_by_id)])

    expected_rows = {}
    exact = 0
    normalized = []
    reconstruction_errors = []
    action_usage = Counter()
    argument_usage = Counter()
    modifier_usage = Counter()
    state_usage = Counter()
    combinator_usage = Counter()
    for event_id, source_row in source_by_id.items():
        expected = reconstruct(source_row, fragments, categories)
        expected_rows[event_id] = expected
        output = replay_by_id[event_id]
        fields = (
            "state_frame_role", "base_mode", "action_topology", "generated_action_chain_de",
            "argument_topology", "generated_argument_phrase_de", "modifier_atoms",
            "modifier_type_sequence", "generated_modifier_phrase_de", "outer_template_signature",
            "structural_template_signature", "generated_microphrase_de",
        )
        if any(output[field] != expected[field] for field in fields):
            reconstruction_errors.append((event_id, {field: [output[field], expected[field]] for field in fields if output[field] != expected[field]}))
        if expected["generated_microphrase_de"] == source_row["owner_free_microphrase_de"]:
            exact += 1
            expected_status = "EXACT_SOURCE_REPLAY"
        else:
            normalized.append((event_id, source_row["owner_free_microphrase_de"], expected["generated_microphrase_de"]))
            expected_status = "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" if event_id == "G407-E1000" else "UNEXPECTED_REPLAY_DRIFT"
        if output["replay_status"] != expected_status:
            reconstruction_errors.append((event_id, "replay status"))
        action_roots = roots(source_row["effective_action_roots"])
        argument_roots = roots(source_row["effective_argument_roots"])
        modifier_atoms = [] if expected["modifier_atoms"] == "NONE" else expected["modifier_atoms"].split("+")
        state_usage[source_row["state_marker_sequence"]] += 1
        action_usage.update(action_roots)
        argument_usage.update(argument_roots)
        modifier_usage.update(modifier_atoms)
        combinator_usage["ARGUMENT_COORDINATION"] += int(bool(argument_roots) and argument_roots != ["Y", "Y"])
        combinator_usage["DOUBLE_POSTEN"] += int(argument_roots == ["Y", "Y"])
        combinator_usage["ACTION_CHAIN"] += int(bool(action_roots))
        combinator_usage["ADJACENT_ACTION_REPEAT"] += int(expected["compressed"] == "YES")
        combinator_usage["MODIFIER_SEQUENCE"] += int(bool(modifier_atoms))
        combinator_usage["SENTENCE_ASSEMBLY"] += 1
    check("all_1656_template_rows_reconstructed", not reconstruction_errors, reconstruction_errors[:5])
    check("exact_replay_count", exact == 1655, exact)
    check("one_named_normalization", normalized == [("G407-E1000", "Weiter: gib den Posten und den Posten; hier.", "Weiter: gib die beiden Posten; hier.")], normalized)
    check("normalization_artifact_exact", len(normalizations) == 1 and normalizations[0]["event_id"] == "G407-E1000" and normalizations[0]["semantic_change"] == "NO__GERMAN_EDITORIAL_CONSISTENCY_ONLY", normalizations)
    check("atom_alignment_retained", all(replay_by_id[event_id]["written_atom_alignment"] == row["written_atom_alignment"] for event_id, row in source_by_id.items()), None)

    outer_signatures = sorted({expected["outer_template_signature"] for expected in expected_rows.values()})
    structural_signatures = sorted({expected["structural_template_signature"] for expected in expected_rows.values()})
    outer_ids = {signature: f"GDT565-O{i:02d}" for i, signature in enumerate(outer_signatures, 1)}
    structural_ids = {signature: f"GDT565-T{i:03d}" for i, signature in enumerate(structural_signatures, 1)}
    check("template_ids_exact", all(replay_by_id[event_id]["outer_template_id"] == outer_ids[expected["outer_template_signature"]] and replay_by_id[event_id]["structural_template_id"] == structural_ids[expected["structural_template_signature"]] for event_id, expected in expected_rows.items()), None)
    check("template_inventory_counts", len(outer_signatures) == 11 and len(structural_signatures) == 168, [len(outer_signatures), len(structural_signatures)])
    structural_counts = Counter(expected["structural_template_signature"] for expected in expected_rows.values())
    check("recurrent_structural_counts", sum(count > 1 for count in structural_counts.values()) == 82 and sum(count for count in structural_counts.values() if count > 1) == 1570, [sum(count > 1 for count in structural_counts.values()), sum(count for count in structural_counts.values() if count > 1)])
    check("topology_counts", len({expected["action_topology"] for expected in expected_rows.values()}) == 7 and len({expected["argument_topology"] for expected in expected_rows.values()}) == 4 and len({expected["modifier_type_sequence"] for expected in expected_rows.values()}) == 46, None)
    check("exact_modifier_sequence_count", len({expected["modifier_atoms"] for expected in expected_rows.values()}) == 93, len({expected["modifier_atoms"] for expected in expected_rows.values()}))

    renderer_classes = Counter(row["card_class"] for row in renderer)
    check("renderer_class_counts", renderer_classes == Counter({"MODIFIER_FRAGMENT": 14, "STATE_FRAME": 9, "ACTION_TEMPLATE": 9, "COMBINATOR": 6, "ARGUMENT_CARD": 4}), dict(renderer_classes))
    check("renderer_ids_sequential", [row["renderer_card_id"] for row in renderer] == [f"GDT565-R{i:02d}" for i in range(1, 43)], [renderer[0]["renderer_card_id"], renderer[-1]["renderer_card_id"]])
    check("all_renderer_cards_used", all(int(row["usage_count"]) > 0 for row in renderer), [row["renderer_card_id"] for row in renderer if int(row["usage_count"]) == 0])
    state_cards = {row["selector"]: row for row in renderer if row["card_class"] == "STATE_FRAME"}
    check("nine_state_cards_exact", set(state_cards) == set(FRAMES) and all(int(state_cards[key]["usage_count"]) == state_usage[key] for key in FRAMES), {key: state_cards.get(key, {}).get("usage_count") for key in FRAMES})
    action_cards = {row["selector"]: row for row in renderer if row["card_class"] == "ACTION_TEMPLATE"}
    check("nine_action_cards_exact", set(action_cards) == set(ACTION_TEXT) and all(action_cards[key]["template_no_object_de"] == ACTION_TEXT[key][0] and action_cards[key]["template_with_object_de"] == ACTION_TEXT[key][1] and int(action_cards[key]["usage_count"]) == action_usage[key] for key in ACTION_TEXT), None)
    argument_cards = {row["selector"]: row for row in renderer if row["card_class"] == "ARGUMENT_CARD"}
    check("four_argument_cards_exact", set(argument_cards) == set(ARG_TEXT) and all(argument_cards[key]["template_no_object_de"] == ARG_TEXT[key] and int(argument_cards[key]["usage_count"]) == argument_usage[key] for key in ARG_TEXT), None)
    modifier_cards = [row for row in renderer if row["card_class"] == "MODIFIER_FRAGMENT"]
    expected_fragments = {fragment: sorted(atom for atom, value in fragments.items() if value == fragment and atom not in ACTIONS | ARGUMENTS | STATES) for fragment in {fragments[atom] for atom in fragments if atom not in ACTIONS | ARGUMENTS | STATES}}
    check("fourteen_modifier_cards_exact", len(expected_fragments) == 14 and {row["selector"] for row in modifier_cards} == set(expected_fragments) and all(row["source_atoms"].split("+") == expected_fragments[row["selector"]] for row in modifier_cards), None)
    combinators = {row["selector"]: int(row["usage_count"]) for row in renderer if row["card_class"] == "COMBINATOR"}
    check("six_combinators_exact", combinators == dict(combinator_usage), [combinators, dict(combinator_usage)])

    generated_by_recipe_phrase: dict[tuple[str, str], list[str]] = defaultdict(list)
    for source_row in source:
        generated_by_recipe_phrase[(source_row["recipe"], expected_rows[source_row["event_id"]]["generated_microphrase_de"])].append(source_row["event_id"])
    check("generated_cell_count", len(generated_by_recipe_phrase) == 716, len(generated_by_recipe_phrase))
    cell_keys = {(row["recipe"], row["generated_owner_free_microphrase_de"]): row for row in cells}
    check("cell_keys_exact", len(cell_keys) == len(cells) and set(cell_keys) == set(generated_by_recipe_phrase), [len(cell_keys), len(set(generated_by_recipe_phrase) - set(cell_keys))])
    cell_errors = []
    for key, event_ids in generated_by_recipe_phrase.items():
        row = cell_keys[key]
        if int(row["event_count"]) != len(event_ids) or row["all_events_accounted"] != "YES" or int(row["normalized_event_count"]) != int("G407-E1000" in event_ids):
            cell_errors.append((key, row, event_ids))
    check("all_716_cells_reconstructed", not cell_errors, cell_errors[:3])
    check("fixed_variable_cell_partition", sum(row["gdt564_source_cell_id"] == "FIXED_RECIPE" for row in cells) == 301 and sum(row["gdt564_source_cell_id"] != "FIXED_RECIPE" for row in cells) == 415, [sum(row["gdt564_source_cell_id"] == "FIXED_RECIPE" for row in cells), sum(row["gdt564_source_cell_id"] != "FIXED_RECIPE" for row in cells)])
    selector_ids = {row["selector_cell_id"] for row in selector_source}
    check("gdt564_cell_links_exact", {row["gdt564_source_cell_id"] for row in cells if row["gdt564_source_cell_id"] != "FIXED_RECIPE"} == selector_ids, len({row["gdt564_source_cell_id"] for row in cells if row["gdt564_source_cell_id"] != "FIXED_RECIPE"}))

    def profile_exact(rows: list[dict[str, str]], signature_field: str, count_map: Counter[str]) -> bool:
        lookup = {row[signature_field]: row for row in rows}
        return set(lookup) == set(count_map) and all(int(lookup[key]["event_count"]) == value for key, value in count_map.items())

    check("outer_profiles_exact", profile_exact(outer, "signature", Counter(expected["outer_template_signature"] for expected in expected_rows.values())), None)
    check("structural_profiles_exact", profile_exact(structural, "signature", structural_counts), None)
    check("action_profiles_exact", profile_exact(action_profiles, "action_topology", Counter(expected["action_topology"] for expected in expected_rows.values())), None)
    check("argument_profiles_exact", profile_exact(argument_profiles, "argument_topology", Counter(expected["argument_topology"] for expected in expected_rows.values())), None)
    check("modifier_profiles_exact", profile_exact(modifier_profiles, "modifier_type_sequence", Counter(expected["modifier_type_sequence"] for expected in expected_rows.values())), None)

    expected_result = {
        "source_state_card_count": 1656,
        "exact_replay_count": 1655,
        "editorial_normalization_count": 1,
        "unexpected_replay_drift_count": 0,
        "distinct_owner_free_microphrase_count": 607,
        "distinct_generated_microphrase_count": 607,
        "recipe_context_cell_count": 716,
        "fixed_recipe_context_cell_count": 301,
        "variable_recipe_context_cell_count": 415,
        "renderer_card_count": 42,
        "state_frame_card_count": 9,
        "action_template_card_count": 9,
        "argument_card_count": 4,
        "modifier_fragment_card_count": 14,
        "combinator_card_count": 6,
        "modifier_source_atom_count": 20,
        "outer_template_count": 11,
        "structural_template_count": 168,
        "recurrent_structural_template_count": 82,
        "recurrent_structural_template_event_count": 1570,
        "action_topology_count": 7,
        "argument_topology_count": 4,
        "modifier_type_sequence_count": 46,
        "exact_modifier_atom_sequence_count": 93,
        "distinct_generated_action_chain_count": 133,
        "distinct_generated_modifier_phrase_count": 80,
        "visible_action_slot_count": 1158,
        "effective_action_template_use_count": 1851,
        "effective_argument_root_use_count": 1598,
        "modifier_atom_use_count": 1266,
        "editorial_microphrase_changes": 1,
        "learned_long_phrase_templates": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_status_exact", result.get("status") == "PASS_1655_EXACT_REPLAYS__ONE_EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION__716_CELLS__42_RENDERER_CARDS__168_STRUCTURAL_TEMPLATES", result.get("status"))
    check("result_guards", result.get("all_renderer_cards_used") is True and result.get("all_recipe_context_cells_accounted") is True, [result.get("all_renderer_cards_used"), result.get("all_recipe_context_cells_accounted")])
    check("zero_scope_mutation", all(result.get(key) == 0 for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values")), {key: result.get(key) for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values")})
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()}, result.get("input_sha256"))

    book = ARTIFACTS["GDT565_TEMPLATE_GENERATOR_BOOK.md"].read_text(encoding="utf-8")
    needles = ("1.655", "42 Renderer-Karten", "607 verschiedenen", "716 Rezept-Kontext", "168", "die beiden")
    check("book_core_findings_present", all(needle in book for needle in needles), [needle for needle in needles if needle not in book])

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay_process = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay_process.returncode == 0, replay_process.stderr)
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
