#!/usr/bin/env python3
"""Independently validate GDT561's complete ordered state-card reader."""

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
BASE = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt561_validation.json"

INPUTS = {
    "dictionary": ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv",
    "old_context": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
    "current_context": ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts/gdt539_546_contextual_prose_events.tsv",
    "state_atlas": ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts/gdt557_all_state_marker_occurrences.tsv",
    "grade_assignments": ROOT / "experiments/yolo/gdt558_grade_carrier_envelope_grammar/artifacts/gdt558_333_grade_carrier_assignments.tsv",
    "argument_assignments": ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar/artifacts/gdt559_390_argument_carrier_assignments.tsv",
    "relation_assignments": ROOT / "experiments/yolo/gdt560_relation_state_geometry_grammar/artifacts/gdt560_216_relation_state_assignments.tsv",
}
ARTIFACTS = {
    "gdt561_1656_typed_state_cards.tsv": OUT / "gdt561_1656_typed_state_cards.tsv",
    "gdt561_36_state_atom_dictionary.tsv": OUT / "gdt561_36_state_atom_dictionary.tsv",
    "gdt561_402_recipe_defaults.tsv": OUT / "gdt561_402_recipe_defaults.tsv",
    "gdt561_213_ordered_type_templates.tsv": OUT / "gdt561_213_ordered_type_templates.tsv",
    "gdt561_7_type_coverage.tsv": OUT / "gdt561_7_type_coverage.tsv",
    "gdt561_939_specialized_carrier_links.tsv": OUT / "gdt561_939_specialized_carrier_links.tsv",
    "gdt561_787_specialized_card_integrations.tsv": OUT / "gdt561_787_specialized_card_integrations.tsv",
    "gdt561_37_order_witness_recipes.tsv": OUT / "gdt561_37_order_witness_recipes.tsv",
    "GDT561_TYPED_STATE_CARD_BOOK.md": OUT / "GDT561_TYPED_STATE_CARD_BOOK.md",
    "gdt561_result.json": OUT / "gdt561_result.json",
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

    dictionary_source = read_tsv(INPUTS["dictionary"])
    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    state = read_tsv(INPUTS["state_atlas"])
    grades = read_tsv(INPUTS["grade_assignments"])
    arguments = read_tsv(INPUTS["argument_assignments"])
    relations = read_tsv(INPUTS["relation_assignments"])
    cards = read_tsv(ARTIFACTS["gdt561_1656_typed_state_cards.tsv"])
    dictionary = read_tsv(ARTIFACTS["gdt561_36_state_atom_dictionary.tsv"])
    recipes = read_tsv(ARTIFACTS["gdt561_402_recipe_defaults.tsv"])
    templates = read_tsv(ARTIFACTS["gdt561_213_ordered_type_templates.tsv"])
    types = read_tsv(ARTIFACTS["gdt561_7_type_coverage.tsv"])
    carriers = read_tsv(ARTIFACTS["gdt561_939_specialized_carrier_links.tsv"])
    integrations = read_tsv(ARTIFACTS["gdt561_787_specialized_card_integrations.tsv"])
    orders = read_tsv(ARTIFACTS["gdt561_37_order_witness_recipes.tsv"])
    result = json.loads(ARTIFACTS["gdt561_result.json"].read_text(encoding="utf-8"))

    input_counts = tuple(map(len, (dictionary_source, old_context, current_context, state,
                                   grades, arguments, relations)))
    check("input_counts", input_counts == (46, 4576, 546, 1870, 333, 390, 216), input_counts)
    source_pages = {row["physical_page"] for row in state}
    check("sealed_pages_absent", not any(page.startswith("f84") for page in source_pages), sorted(page for page in source_pages if page.startswith("f84")))

    source_events: dict[str, dict[str, str]] = {}
    source_duplicates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state:
        source_duplicates[row["event_id"]].append(row)
        source_events.setdefault(row["event_id"], row)
    check("source_event_count", len(source_events) == 1656, len(source_events))
    stable = ("cohort", "statement_id", "physical_page", "register", "surface", "recipe",
              "event_marker_sequence", "statement_position", "statement_final", "current_reading_de")
    conflicts = [event_id for event_id, rows in source_duplicates.items()
                 if any(len({row[field] for row in rows}) != 1 for field in stable)]
    check("state_duplicate_rows_stable", not conflicts, conflicts[:10])

    observed_counts = tuple(map(len, (cards, dictionary, recipes, templates, types,
                                      carriers, integrations, orders)))
    check("artifact_row_counts", observed_counts == (1656, 36, 402, 213, 7, 939, 787, 37), observed_counts)
    check("card_ordinals", [int(row["state_card_ordinal"]) for row in cards] == list(range(1, 1657)), [cards[0]["state_card_ordinal"], cards[-1]["state_card_ordinal"]])
    card_by_event = {row["event_id"]: row for row in cards}
    check("card_ids_unique_and_complete", len(card_by_event) == 1656 and set(card_by_event) == set(source_events), [len(card_by_event), len(set(card_by_event) ^ set(source_events))])
    recipe_mismatches = [event_id for event_id, source in source_events.items()
                         if card_by_event[event_id]["recipe"] != source["recipe"]]
    surface_mismatches = [event_id for event_id, source in source_events.items()
                          if card_by_event[event_id]["surface"] != source["surface"]]
    check("source_recipes_unchanged", not recipe_mismatches, recipe_mismatches[:10])
    check("source_surfaces_unchanged", not surface_mismatches, surface_mismatches[:10])

    atom_rows = {row["atom"]: row for row in dictionary}
    source_dict = {row["atom"]: row for row in dictionary_source}
    source_atoms = [atom for row in source_events.values() for atom in row["recipe"].split("+")]
    check("dictionary_atoms_exact", len(atom_rows) == 36 and set(atom_rows) == set(source_atoms), [len(atom_rows), sorted(set(source_atoms) - set(atom_rows))])
    check("dictionary_values_reused", all(
        row["working_value_de"] == ("ABSCHLIESSEN" if atom == "DY" else source_dict[atom]["working_value_de"])
        for atom, row in atom_rows.items()
    ), [])
    expected_categories = {
        atom: ("STATE_CONTROL" if atom in {"OT", "OL", "DY"} else source_dict[atom]["factor_family"])
        for atom in set(source_atoms)
    }
    check("dictionary_categories_exact", all(atom_rows[atom]["typed_category"] == category for atom, category in expected_categories.items()), [])
    atom_counts = Counter(source_atoms)
    dictionary_counts = {atom: int(row["atom_occurrence_count"]) for atom, row in atom_rows.items()}
    check("dictionary_occurrence_counts", dictionary_counts == atom_counts, dictionary_counts)
    check("all_4684_atom_mentions_mapped", sum(dictionary_counts.values()) == 4684, sum(dictionary_counts.values()))

    trace_failures = []
    phrase_failures = []
    mapping_failures = []
    for card in cards:
        atoms = card["recipe"].split("+")
        expected_trace = " > ".join(
            f"{atom}{{{ {'ACTION_HEAD':'HANDLUNG','GRADE':'GRAD','ARGUMENT':'ARGUMENT','RELATION':'RELATION','STATE_CONTROL':'ZUSTANDSSTEUERUNG','FORMAL_CONTROL':'FORMSTEUERUNG','LOCAL_OR_CLASS_SIGN':'LOKAL-/KLASSENZEICHEN'}[expected_categories[atom]] }={atom_rows[atom]['working_value_de']}}}"
            for atom in atoms
        )
        expected_reading = " → ".join(atom_rows[atom]["working_value_de"] for atom in atoms)
        expected_phrase = "; ".join(atom_rows[atom]["default_fragment_de"] for atom in atoms)
        if card["ordered_typed_atom_trace"] != expected_trace or card["ordered_all_atom_reading_de"] != expected_reading:
            trace_failures.append(card["event_id"])
        if card["all_atom_default_phrase_de"] != expected_phrase:
            phrase_failures.append(card["event_id"])
        if card["every_atom_mapped"] != "YES" or card["written_order_preserved"] != "YES":
            mapping_failures.append(card["event_id"])
    check("all_card_traces_reconstruct_exactly", not trace_failures, trace_failures[:10])
    check("all_card_phrases_reconstruct_exactly", not phrase_failures, phrase_failures[:10])
    check("all_card_mapping_guards_positive", not mapping_failures, mapping_failures[:10])

    atom_length_counts = Counter(len(row["recipe"].split("+")) for row in cards)
    check("card_atom_length_distribution", atom_length_counts == Counter({1: 191, 2: 383, 3: 751, 4: 217, 5: 85, 6: 24, 7: 4, 9: 1}), atom_length_counts)
    maximum_cards = [(row["event_id"], row["recipe"]) for row in cards if int(row["recipe_atom_count"]) == 9]
    check("unique_nine_atom_card", maximum_cards == [("G407-E4208", "D_ADDR+OL+CH+S+Y+CH+K+E+OL")], maximum_cards)

    old_by_id = {row["global_running_event_id"]: row for row in old_context}
    current_by_id = {row["event_id"]: row for row in current_context}
    old_cards = [row for row in cards if row["source_context_layer"] == "GDT416_OLD26_IMPERATIVE"]
    current_cards = [row for row in cards if row["source_context_layer"] == "GDT539_CURRENT4_CONTEXTUAL"]
    check("context_partition", (len(old_cards), len(current_cards)) == (1494, 162), [len(old_cards), len(current_cards)])
    check("old_context_clauses_exact", all(row["contextual_clause_de"] == old_by_id[row["event_id"]]["imperative_clause_de"] for row in old_cards), [])
    check("current_context_clauses_exact", all(row["contextual_clause_de"] == current_by_id[row["event_id"]]["contextual_clause_de"] for row in current_cards), [])

    recipe_by_key = {row["recipe"]: row for row in recipes}
    source_recipe_counts = Counter(row["recipe"] for row in cards)
    check("recipe_keys_exact", len(recipe_by_key) == 402 and set(recipe_by_key) == set(source_recipe_counts), [len(recipe_by_key), len(set(recipe_by_key) ^ set(source_recipe_counts))])
    check("recipe_event_counts_exact", all(int(recipe_by_key[key]["event_count"]) == count for key, count in source_recipe_counts.items()), [])
    check("recipe_event_total", sum(int(row["event_count"]) for row in recipes) == 1656, sum(int(row["event_count"]) for row in recipes))
    check("all_recipe_defaults_present", all(row["all_atom_default_phrase_de"] and row["every_atom_mapped"] == "YES" for row in recipes), [])
    check("zero_learned_whole_cards", all(row["default_scope"] == "EXACT_RECIPE_ONLY__OWNER_CONTEXT_REMAINS_EVENT_LOCAL" for row in recipes), [])

    signature_counts = Counter(row["ordered_type_signature"] for row in cards)
    template_by_signature = {row["ordered_type_signature"]: row for row in templates}
    check("type_template_keys_exact", len(template_by_signature) == 213 and set(template_by_signature) == set(signature_counts), [len(template_by_signature), len(set(template_by_signature) ^ set(signature_counts))])
    check("type_template_counts_exact", all(int(template_by_signature[key]["event_count"]) == count for key, count in signature_counts.items()), [])
    check("type_template_event_total", sum(int(row["event_count"]) for row in templates) == 1656, sum(int(row["event_count"]) for row in templates))
    top_signature = max(signature_counts, key=signature_counts.get)
    check("dominant_type_signature", (top_signature, signature_counts[top_signature]) == ("ACTION_HEAD+GRADE+STATE_CONTROL", 370), [top_signature, signature_counts[top_signature]])

    type_by_name = {row["typed_category"]: row for row in types}
    expected_type_metrics = {
        "ACTION_HEAD": (9, 1158, 950), "GRADE": (3, 742, 729),
        "ARGUMENT": (4, 390, 382), "RELATION": (4, 216, 212),
        "STATE_CONTROL": (3, 1870, 1656), "FORMAL_CONTROL": (4, 175, 152),
        "LOCAL_OR_CLASS_SIGN": (9, 133, 124),
    }
    observed_type_metrics = {
        key: tuple(int(row[field]) for field in ("distinct_atom_count", "atom_mention_count", "state_card_count"))
        for key, row in type_by_name.items()
    }
    check("seven_type_metrics_exact", observed_type_metrics == expected_type_metrics, observed_type_metrics)
    check("type_mentions_partition_4684", sum(value[1] for value in observed_type_metrics.values()) == 4684, sum(value[1] for value in observed_type_metrics.values()))

    layer_counts = Counter(row["layer"] for row in carriers)
    check("carrier_layer_counts", layer_counts == Counter({"GRADE": 333, "ARGUMENT": 390, "RELATION": 216}), layer_counts)
    carrier_ordinals = [int(row["carrier_link_ordinal"]) for row in carriers]
    check("carrier_ordinals", carrier_ordinals == list(range(1, 940)), [carrier_ordinals[0], carrier_ordinals[-1]])
    carrier_failures = []
    for row in carriers:
        card = card_by_event[row["event_id"]]
        atoms = card["recipe"].split("+")
        atom = row["atom"]
        if (atoms[int(row["atom_position"]) - 1] != atom
                or row["unified_atom_value_de"] != atom_rows[atom]["working_value_de"]
                or row["position_and_value_match_unified_card"] != "YES"):
            carrier_failures.append((row["layer"], row["event_id"], row["atom_position"]))
    check("carrier_positions_and_values_exact", not carrier_failures, carrier_failures[:10])

    expected_carrier_keys = set()
    for row in grades:
        expected_carrier_keys.add(("GRADE", row["event_id"], row["grade_atom_position"], row["grade"]))
    for row in arguments:
        expected_carrier_keys.add(("ARGUMENT", row["event_id"], row["argument_atom_position"], row["argument"]))
    for row in relations:
        expected_carrier_keys.add(("RELATION", row["event_id"], row["relation_atom_position"], row["relation"]))
    observed_carrier_keys = {(row["layer"], row["event_id"], row["atom_position"], row["atom"]) for row in carriers}
    check("carrier_source_links_complete", observed_carrier_keys == expected_carrier_keys and len(observed_carrier_keys) == 939, [len(observed_carrier_keys), len(expected_carrier_keys)])
    specialized_sets = {
        layer: {row["event_id"] for row in carriers if row["layer"] == layer}
        for layer in ("GRADE", "ARGUMENT", "RELATION")
    }
    union = set().union(*specialized_sets.values())
    overlaps = (
        len(specialized_sets["GRADE"] & specialized_sets["ARGUMENT"]),
        len(specialized_sets["GRADE"] & specialized_sets["RELATION"]),
        len(specialized_sets["ARGUMENT"] & specialized_sets["RELATION"]),
        len(specialized_sets["GRADE"] & specialized_sets["ARGUMENT"] & specialized_sets["RELATION"]),
    )
    check("specialized_union_and_overlaps", len(union) == 787 and overlaps == (96, 15, 22, 0), [len(union), overlaps])
    integration_ids = {row["event_id"] for row in integrations}
    check("integration_union_exact", integration_ids == union and len(integration_ids) == 787, [len(integration_ids), len(union - integration_ids)])
    check("integration_link_total", sum(int(row["total_specialized_link_count"]) for row in integrations) == 939, sum(int(row["total_specialized_link_count"]) for row in integrations))

    recipes_by_multiset: dict[str, set[str]] = defaultdict(set)
    events_by_recipe = Counter(row["recipe"] for row in cards)
    for recipe in events_by_recipe:
        recipes_by_multiset["+".join(sorted(recipe.split("+")))].add(recipe)
    variable = {key: value for key, value in recipes_by_multiset.items() if len(value) > 1}
    check("order_family_count", len(variable) == 18, len(variable))
    observed_order_recipes = {row["recipe"] for row in orders}
    expected_order_recipes = set().union(*variable.values())
    check("order_recipe_coverage", observed_order_recipes == expected_order_recipes and len(orders) == 37, [len(observed_order_recipes), len(expected_order_recipes)])
    check("order_event_coverage", sum(events_by_recipe[recipe] for recipe in expected_order_recipes) == 102 and sum(int(row["recipe_event_count"]) for row in orders) == 102, [sum(events_by_recipe[recipe] for recipe in expected_order_recipes), sum(int(row["recipe_event_count"]) for row in orders)])
    check("order_multisets_exact", all(row["atom_multiset"] == "+".join(sorted(row["recipe"].split("+"))) for row in orders), [])
    check("order_preservation_decisions", all(row["decision"] == "KEEP_WRITTEN_ORDER__DO_NOT_SORT_ATOMS" for row in orders), [])

    expected_result = {
        "state_card_count": 1656, "state_marker_occurrence_count": 1870,
        "state_atom_mention_count": 4684, "mapped_atom_mention_count": 4684,
        "distinct_state_atom_count": 36, "exact_recipe_count": 402,
        "ordered_type_template_count": 213, "typed_category_count": 7,
        "specialized_carrier_link_count": 939, "specialized_card_count": 787,
        "grade_carrier_link_count": 333, "argument_carrier_link_count": 390,
        "relation_carrier_link_count": 216,
        "order_variable_multiset_family_count": 18, "order_witness_recipe_count": 37,
        "order_witness_event_count": 102, "context_join_old_count": 1494,
        "context_join_current_count": 162, "cards_without_action": 706,
        "cards_without_argument": 1274,
        "cards_without_action_grade_argument_relation": 274,
        "pure_state_control_card_count": 222,
        "contentless_control_or_structural_card_count": 274,
        "learned_whole_card_values": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_completion_flags", all(result.get(key) is True for key in (
        "all_cards_have_default", "all_recipes_have_default", "all_atoms_mapped", "all_written_orders_preserved"
    )), {key: result.get(key) for key in ("all_cards_have_default", "all_recipes_have_default", "all_atoms_mapped", "all_written_orders_preserved")})
    check("zero_scope_mutation", all(result.get(key) == 0 for key in (
        "new_pages", "new_surfaces", "recipe_changes", "root_meaning_changes", "statement_boundary_changes"
    )), {key: result.get(key) for key in ("new_pages", "new_surfaces", "recipe_changes", "root_meaning_changes", "statement_boundary_changes")})

    book = ARTIFACTS["GDT561_TYPED_STATE_CARD_BOOK.md"].read_text(encoding="utf-8")
    book_needles = ("1.656", "4.684/4.684", "402", "939", "18 Atommengen", "kein Rezept benötigt einen neu gelernten Ganzkartenwert")
    check("book_core_findings_present", all(needle in book for needle in book_needles), [needle for needle in book_needles if needle not in book])

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
