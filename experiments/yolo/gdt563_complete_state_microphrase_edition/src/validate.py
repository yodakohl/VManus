#!/usr/bin/env python3
"""Validate the complete GDT563 state-card microphrase edition."""

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
BASE = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt563_validation.json"

INPUTS = {
    "typed_cards": ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts/gdt561_1656_typed_state_cards.tsv",
    "state_dictionary": ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts/gdt561_36_state_atom_dictionary.tsv",
    "actionless_reader": ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader/artifacts/gdt562_706_actionless_state_reader.tsv",
}
ARTIFACTS = {
    "gdt563_1656_complete_state_microphrases.tsv": OUT / "gdt563_1656_complete_state_microphrases.tsv",
    "gdt563_950_visible_action_microphrases.tsv": OUT / "gdt563_950_visible_action_microphrases.tsv",
    "gdt563_706_actionless_source_links.tsv": OUT / "gdt563_706_actionless_source_links.tsv",
    "gdt563_402_recipe_context_profiles.tsv": OUT / "gdt563_402_recipe_context_profiles.tsv",
    "gdt563_9_state_sequence_profiles.tsv": OUT / "gdt563_9_state_sequence_profiles.tsv",
    "gdt563_8_resolution_mode_profiles.tsv": OUT / "gdt563_8_resolution_mode_profiles.tsv",
    "gdt563_16_repeated_action_cards.tsv": OUT / "gdt563_16_repeated_action_cards.tsv",
    "gdt563_context_variability_summary.tsv": OUT / "gdt563_context_variability_summary.tsv",
    "GDT563_COMPLETE_STATE_MICROPHRASE_BOOK.md": OUT / "GDT563_COMPLETE_STATE_MICROPHRASE_BOOK.md",
    "gdt563_result.json": OUT / "gdt563_result.json",
}

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
ARGUMENT_PHRASES = {
    "Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit",
}
ACTION_TEMPLATES = {
    "OK": ("setze", "setze {argument}"), "CH": ("nimm", "nimm {argument}"),
    "SH": ("halte", "halte {argument}"), "K": ("gib", "gib {argument}"),
    "S": ("wähle", "wähle {argument}"), "CHD": ("bearbeite", "bearbeite {argument}"),
    "T": ("stelle ein", "stelle {argument} ein"), "R": ("markiere", "markiere {argument}"),
    "P": ("setze ein", "setze {argument} ein"),
}
SEQUENCES = {
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
ACTIONLESS_MODE_MAP = {
    "FULL_INHERITED_OPERATION": "INHERITED_ACTION_FULL_OPERATION",
    "OBJECTLESS_INHERITED_OPERATION": "INHERITED_ACTION_OBJECTLESS_OPERATION",
    "ARGUMENT_REFERENCE_INITIALIZER": "ARGUMENT_REFERENCE_INITIALIZER",
    "FORMAL_RELATION_PROLOGUE": "FORMAL_RELATION_PROLOGUE",
    "STANDALONE_GRADED_CLOSE": "STANDALONE_GRADED_CLOSE",
    "PURE_CONTINUATION": "PURE_CONTINUATION",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def argument_phrase(roots: list[str]) -> str:
    if roots == ["Y", "Y"]:
        return "die beiden Posten"
    phrases = [ARGUMENT_PHRASES[root] for root in roots]
    if len(phrases) == 1:
        return phrases[0]
    return ", ".join(phrases[:-1]) + " und " + phrases[-1]


def action_phrase(root: str, arguments: list[str]) -> str:
    no_object, with_object = ACTION_TEMPLATES[root]
    return with_object.format(argument=argument_phrase(arguments)) if arguments else no_object


def expected_action_render(atoms: list[str], arguments: list[str]) -> tuple[str, str, list[str], bool]:
    roots = [atom for atom in atoms if atom in ACTIONS]
    expanded = " und ".join(action_phrase(root, arguments) for root in roots)
    units: list[tuple[str, int]] = []
    index = 0
    while index < len(atoms):
        atom = atoms[index]
        if atom not in ACTIONS:
            index += 1
            continue
        repeat = 1
        while index + repeat < len(atoms) and atoms[index + repeat] == atom:
            repeat += 1
        units.append((atom, repeat))
        index += repeat
    rendered_parts = []
    compressed = False
    for root, repeat in units:
        phrase = action_phrase(root, arguments)
        if repeat == 1:
            rendered_parts.append(phrase)
        elif repeat == 2:
            rendered_parts.append(phrase + " zweimal")
            compressed = True
        else:
            rendered_parts.append(phrase + f" {repeat}-mal")
            compressed = True
    return " und ".join(rendered_parts), expanded, roots, compressed


def expected_microphrase(action_chain: str, modifiers: str, sequence: str) -> str:
    _, prefix, suffix = SEQUENCES[sequence]
    parts = [part for part in (action_chain, modifiers if modifiers != "NONE" else "", suffix) if part]
    phrase = (f"{prefix}: " + "; ".join(parts) if parts else prefix) if prefix else "; ".join(parts)
    return phrase[0].upper() + phrase[1:] + "."


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    typed = read_tsv(INPUTS["typed_cards"])
    dictionary = read_tsv(INPUTS["state_dictionary"])
    actionless_source = read_tsv(INPUTS["actionless_reader"])
    cards = read_tsv(ARTIFACTS["gdt563_1656_complete_state_microphrases.tsv"])
    visible = read_tsv(ARTIFACTS["gdt563_950_visible_action_microphrases.tsv"])
    actionless_links = read_tsv(ARTIFACTS["gdt563_706_actionless_source_links.tsv"])
    recipes = read_tsv(ARTIFACTS["gdt563_402_recipe_context_profiles.tsv"])
    sequences = read_tsv(ARTIFACTS["gdt563_9_state_sequence_profiles.tsv"])
    modes = read_tsv(ARTIFACTS["gdt563_8_resolution_mode_profiles.tsv"])
    repeated = read_tsv(ARTIFACTS["gdt563_16_repeated_action_cards.tsv"])
    variability = read_tsv(ARTIFACTS["gdt563_context_variability_summary.tsv"])
    result = json.loads(ARTIFACTS["gdt563_result.json"].read_text(encoding="utf-8"))

    check("input_counts", (len(typed), len(dictionary), len(actionless_source)) == (1656, 36, 706), [len(typed), len(dictionary), len(actionless_source)])
    check("source_pages_exclude_f84", not any(row["physical_page"].startswith("f84") for row in typed), sorted({row["physical_page"] for row in typed if row["physical_page"].startswith("f84")}))
    artifact_counts = tuple(map(len, (cards, visible, actionless_links, recipes, sequences, modes, repeated, variability)))
    check("artifact_row_counts", artifact_counts == (1656, 950, 706, 402, 9, 8, 16, 4), artifact_counts)

    typed_by_id = {row["event_id"]: row for row in typed}
    card_by_id = {row["event_id"]: row for row in cards}
    check("card_ids_unique_and_complete", len(card_by_id) == 1656 and set(card_by_id) == set(typed_by_id), [len(card_by_id), len(set(card_by_id) ^ set(typed_by_id))])
    check("card_ordinals", [int(row["state_microphrase_ordinal"]) for row in cards] == list(range(1, 1657)), [cards[0]["state_microphrase_ordinal"], cards[-1]["state_microphrase_ordinal"]])
    check("recipes_and_surfaces_unchanged", all(card_by_id[event_id]["recipe"] == source["recipe"] and card_by_id[event_id]["surface"] == source["surface"] for event_id, source in typed_by_id.items()), [])
    check("typed_traces_retained", all(card_by_id[event_id]["ordered_typed_atom_trace"] == source["ordered_typed_atom_trace"] for event_id, source in typed_by_id.items()), [])
    check("owner_context_retained", all(card_by_id[event_id]["owner_bound_context_clause_de"] == source["contextual_clause_de"] for event_id, source in typed_by_id.items()), [])

    fragments = {row["atom"]: row["default_fragment_de"] for row in dictionary}
    alignment_failures = []
    for row in cards:
        expected = " | ".join(
            f"{index}:{atom}={fragments[atom]}"
            for index, atom in enumerate(row["recipe"].split("+"), 1)
        )
        if row["written_atom_alignment"] != expected:
            alignment_failures.append(row["event_id"])
    check("all_atom_alignments_exact", not alignment_failures, alignment_failures[:10])
    check("all_completion_guards_positive", all(row["all_written_atoms_retained"] == "YES" and row["all_written_action_slots_retained"] == "YES" and row["owner_free_microphrase_de"].endswith(".") for row in cards), [])

    source_actionless = {row["event_id"]: row for row in actionless_source}
    link_by_id = {row["event_id"]: row for row in actionless_links}
    expected_actionless_ids = {event_id for event_id, row in typed_by_id.items() if row["action_atom_count"] == "0"}
    check("actionless_partition_exact", set(source_actionless) == set(link_by_id) == expected_actionless_ids and len(expected_actionless_ids) == 706, [len(source_actionless), len(link_by_id), len(expected_actionless_ids)])
    check("actionless_phrases_byte_identical", all(link_by_id[event_id]["gdt562_microphrase_de"] == source["owner_free_resolved_microphrase_de"] == card_by_id[event_id]["owner_free_microphrase_de"] and link_by_id[event_id]["microphrase_byte_identical"] == "YES" for event_id, source in source_actionless.items()), [])
    check("actionless_modes_exact", all(card_by_id[event_id]["resolution_mode"] == ACTIONLESS_MODE_MAP[source["completeness_role"]] for event_id, source in source_actionless.items()), [])

    visible_by_id = {row["event_id"]: row for row in visible}
    expected_visible_ids = set(typed_by_id) - expected_actionless_ids
    check("visible_partition_exact", len(visible_by_id) == 950 and set(visible_by_id) == expected_visible_ids, [len(visible_by_id), len(set(visible_by_id) ^ expected_visible_ids)])
    visible_failures = []
    visible_action_total = 0
    for event_id, row in visible_by_id.items():
        source = typed_by_id[event_id]
        atoms = source["recipe"].split("+")
        explicit_arguments = split_roots(source["explicit_argument_roots"])
        expected_written_arguments = [atom for atom in atoms if atom in ARGUMENTS]
        if explicit_arguments != expected_written_arguments:
            visible_failures.append((event_id, "argument_source"))
            continue
        effective_arguments = explicit_arguments or split_roots(source["inherited_argument_root"])
        rendered, expanded, action_roots, compressed = expected_action_render(atoms, effective_arguments)
        modifier_atoms = [atom for atom in atoms if atom not in ACTIONS | ARGUMENTS | STATE_CONTROLS]
        modifiers = "; ".join(fragments[atom] for atom in modifier_atoms) or "NONE"
        microphrase = expected_microphrase(rendered, modifiers, source["state_marker_sequence"])
        expected_mode = "VISIBLE_ACTION_FULL_OPERATION" if effective_arguments else "VISIBLE_ACTION_OBJECTLESS_OPERATION"
        if not (
            row["written_action_roots"] == "|".join(action_roots)
            and int(row["written_action_slot_count"]) == len(action_roots)
            and row["effective_argument_roots"] == ("|".join(effective_arguments) or "NONE")
            and row["rendered_action_chain_de"] == rendered
            and row["expanded_action_chain_de"] == expanded
            and row["visible_modifier_phrase_de"] == modifiers
            and row["state_sequence_role"] == SEQUENCES[source["state_marker_sequence"]][0]
            and row["owner_free_microphrase_de"] == microphrase
            and card_by_id[event_id]["resolution_mode"] == expected_mode
            and card_by_id[event_id]["owner_free_microphrase_de"] == microphrase
        ):
            visible_failures.append((event_id, "render"))
        visible_action_total += len(action_roots)
    check("all_visible_action_renders_exact", not visible_failures, visible_failures[:10])
    check("all_1158_visible_action_slots_retained", visible_action_total == 1158 and sum(int(row["written_action_slot_count"]) for row in visible) == 1158, [visible_action_total, sum(int(row["written_action_slot_count"]) for row in visible)])

    mode_counts = Counter(row["resolution_mode"] for row in cards)
    expected_modes = Counter({
        "VISIBLE_ACTION_FULL_OPERATION": 898,
        "INHERITED_ACTION_FULL_OPERATION": 687,
        "VISIBLE_ACTION_OBJECTLESS_OPERATION": 52,
        "INHERITED_ACTION_OBJECTLESS_OPERATION": 6,
        "ARGUMENT_REFERENCE_INITIALIZER": 5,
        "FORMAL_RELATION_PROLOGUE": 4,
        "STANDALONE_GRADED_CLOSE": 3,
        "PURE_CONTINUATION": 1,
    })
    check("eight_resolution_modes_exact", mode_counts == expected_modes, mode_counts)
    mode_table = {row["resolution_mode"]: int(row["event_count"]) for row in modes}
    check("mode_profiles_exact", mode_table == expected_modes, mode_table)
    check("operation_partition", (mode_counts["VISIBLE_ACTION_FULL_OPERATION"] + mode_counts["INHERITED_ACTION_FULL_OPERATION"], mode_counts["VISIBLE_ACTION_OBJECTLESS_OPERATION"] + mode_counts["INHERITED_ACTION_OBJECTLESS_OPERATION"]) == (1585, 58), [mode_counts["VISIBLE_ACTION_FULL_OPERATION"] + mode_counts["INHERITED_ACTION_FULL_OPERATION"], mode_counts["VISIBLE_ACTION_OBJECTLESS_OPERATION"] + mode_counts["INHERITED_ACTION_OBJECTLESS_OPERATION"]])

    sequence_counts = Counter(row["state_marker_sequence"] for row in cards)
    expected_sequences = Counter({"OL": 619, "DY": 544, "OT": 279, "OT+DY": 86, "OL+DY": 74, "OT+OL": 38, "OL+OL": 14, "OL+OT": 1, "DY+OL": 1})
    check("nine_state_sequences_exact", sequence_counts == expected_sequences, sequence_counts)
    sequence_table = {row["state_marker_sequence"]: int(row["event_count"]) for row in sequences}
    check("sequence_profiles_exact", sequence_table == expected_sequences, sequence_table)
    reverse_expected = {
        "G407-E0034": "Weiter: markiere den Posten; danach nächsten Gang eröffnen.",
        "G407-E1682": "Setze den Wert; auf Grad II; abschließen; danach weiterführen.",
    }
    check("reverse_sequence_microphrases", {event_id: card_by_id[event_id]["owner_free_microphrase_de"] for event_id in reverse_expected} == reverse_expected, {event_id: card_by_id[event_id]["owner_free_microphrase_de"] for event_id in reverse_expected})

    repeated_ids = {row["event_id"] for row in repeated}
    expected_repeated_ids = {
        event_id for event_id, source in typed_by_id.items()
        if len([atom for atom in source["recipe"].split("+") if atom in ACTIONS])
        != len(set(atom for atom in source["recipe"].split("+") if atom in ACTIONS))
    }
    direct_ids = {
        "G407-E1728", "G407-E1914", "G407-E3576", "G407-E3803",
        "G407-E4486", "G515-E0496", "G515-E0516",
    }
    check("sixteen_repeated_cards_exact", repeated_ids == expected_repeated_ids and len(repeated_ids) == 16, [len(repeated_ids), sorted(repeated_ids ^ expected_repeated_ids)])
    check("seven_direct_compressions_exact", {row["event_id"] for row in repeated if row["direct_adjacent_repeat"] == "YES"} == direct_ids, sorted({row["event_id"] for row in repeated if row["direct_adjacent_repeat"] == "YES"} ^ direct_ids))
    check("repeat_roundtrips", all(row["action_slot_roundtrip"] == "YES" and int(row["written_action_slot_count"]) == len(row["written_action_roots"].split("|")) for row in repeated), [])

    cards_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        cards_by_recipe[row["recipe"]].append(row)
    profile_by_recipe = {row["recipe"]: row for row in recipes}
    check("recipe_profile_keys_exact", len(profile_by_recipe) == 402 and set(profile_by_recipe) == set(cards_by_recipe), [len(profile_by_recipe), len(set(profile_by_recipe) ^ set(cards_by_recipe))])
    profile_failures = []
    for recipe, material in cards_by_recipe.items():
        phrases = {row["owner_free_microphrase_de"] for row in material}
        profile = profile_by_recipe[recipe]
        if int(profile["event_count"]) != len(material) or int(profile["distinct_microphrase_count"]) != len(phrases) or (profile["written_recipe_determines_microphrase"] == "YES") != (len(phrases) == 1):
            profile_failures.append(recipe)
    check("all_recipe_profiles_reconstructed", not profile_failures, profile_failures[:10])
    stable = sum(row["written_recipe_determines_microphrase"] == "YES" for row in recipes)
    variable = len(recipes) - stable
    variable_events = sum(int(row["event_count"]) for row in recipes if row["written_recipe_determines_microphrase"] == "NO")
    singleton = sum(int(row["event_count"]) == 1 for row in recipes)
    recurrent = len(recipes) - singleton
    recurrent_stable = sum(int(row["event_count"]) > 1 and row["written_recipe_determines_microphrase"] == "YES" for row in recipes)
    check("recipe_variability_partition", (stable, variable, variable_events, singleton, recurrent, recurrent_stable) == (301, 101, 1277, 262, 140, 39), [stable, variable, variable_events, singleton, recurrent, recurrent_stable])
    ol_profile = profile_by_recipe["OL"]
    check("ol_maximum_variability", int(ol_profile["distinct_microphrase_count"]) == 33 and max(int(row["distinct_microphrase_count"]) for row in recipes) == 33, [ol_profile["distinct_microphrase_count"], max(int(row["distinct_microphrase_count"]) for row in recipes)])

    expected_bands = {"ONE_MICROPHRASE": (301, 379, 1), "TWO_TO_FIVE": (84, 757, 5), "SIX_TO_TEN": (12, 224, 9), "OVER_TEN": (5, 296, 33)}
    observed_bands = {row["context_variability_band"]: tuple(int(row[key]) for key in ("recipe_count", "event_count", "maximum_microphrase_count")) for row in variability}
    check("variability_bands_exact", observed_bands == expected_bands, observed_bands)

    expected_result = {
        "complete_state_card_count": 1656, "visible_action_card_count": 950,
        "actionless_source_link_count": 706, "exact_recipe_profile_count": 402,
        "state_sequence_profile_count": 9, "resolution_mode_count": 8,
        "repeated_action_card_count": 16, "direct_adjacent_repeat_compression_count": 7,
        "separated_repeat_retention_count": 9,
        "stable_single_microphrase_recipe_count": 301,
        "context_variable_recipe_count": 101,
        "context_variable_recipe_event_count": 1277,
        "singleton_recipe_count": 262, "recurrent_recipe_count": 140,
        "recurrent_stable_recipe_count": 39,
        "recurrent_context_variable_recipe_count": 101,
        "maximum_microphrase_count_for_one_recipe": 33,
        "maximum_variability_recipe": "OL",
        "full_operation_count": 1585, "objectless_operation_count": 58,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_completion_flags", all(result.get(key) is True for key in (
        "all_cards_have_microphrase", "all_written_atoms_retained",
        "all_written_action_slots_retained", "all_actionless_phrases_byte_identical",
    )), {key: result.get(key) for key in ("all_cards_have_microphrase", "all_written_atoms_retained", "all_written_action_slots_retained", "all_actionless_phrases_byte_identical")})
    check("zero_scope_mutation", all(result.get(key) == 0 for key in (
        "new_pages", "new_surfaces", "new_recipes", "new_root_values", "new_written_atoms"
    )), {key: result.get(key) for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values", "new_written_atoms")})

    book = ARTIFACTS["GDT563_COMPLETE_STATE_MICROPHRASE_BOOK.md"].read_text(encoding="utf-8")
    needles = ("Alle1.656", "950 sichtbare", "706 Zustandsellipsen", "301", "101", "1277", "262 Einzelbelege", "33 Mikrophrasen")
    check("book_core_findings_present", all(needle in book for needle in needles), [needle for needle in needles if needle not in book])

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
