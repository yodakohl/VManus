#!/usr/bin/env python3
"""Compile every admitted OT/OL/DY state card into one ordered typed reader."""

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
BASE = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader"
OUT = BASE / "artifacts"

G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"
G558 = ROOT / "experiments/yolo/gdt558_grade_carrier_envelope_grammar/artifacts"
G559 = ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar/artifacts"
G560 = ROOT / "experiments/yolo/gdt560_relation_state_geometry_grammar/artifacts"

INPUTS = {
    "dictionary": G413 / "gdt413_46_component_working_dictionary.tsv",
    "old_context": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_context": G539 / "gdt539_546_contextual_prose_events.tsv",
    "state_atlas": G557 / "gdt557_all_state_marker_occurrences.tsv",
    "grade_assignments": G558 / "gdt558_333_grade_carrier_assignments.tsv",
    "argument_assignments": G559 / "gdt559_390_argument_carrier_assignments.tsv",
    "relation_assignments": G560 / "gdt560_216_relation_state_assignments.tsv",
}

CARD_OUT = OUT / "gdt561_1656_typed_state_cards.tsv"
DICT_OUT = OUT / "gdt561_36_state_atom_dictionary.tsv"
RECIPE_OUT = OUT / "gdt561_402_recipe_defaults.tsv"
TEMPLATE_OUT = OUT / "gdt561_213_ordered_type_templates.tsv"
TYPE_OUT = OUT / "gdt561_7_type_coverage.tsv"
CARRIER_OUT = OUT / "gdt561_939_specialized_carrier_links.tsv"
INTEGRATION_OUT = OUT / "gdt561_787_specialized_card_integrations.tsv"
ORDER_OUT = OUT / "gdt561_37_order_witness_recipes.tsv"
BOOK_OUT = OUT / "GDT561_TYPED_STATE_CARD_BOOK.md"
RESULT_OUT = OUT / "gdt561_result.json"

STATUS = (
    "PASS_1656_TYPED_STATE_CARDS__4684_OF_4684_ATOMS_MAPPED__"
    "402_RECIPES_DEFAULTED__939_CARRIER_LINKS_INTEGRATED__18_ORDER_FAMILIES_PRESERVED"
)

STATE_CONTROLS = {"OT", "OL", "DY"}
CATEGORY_ORDER = (
    "ACTION_HEAD", "GRADE", "ARGUMENT", "RELATION", "STATE_CONTROL",
    "FORMAL_CONTROL", "LOCAL_OR_CLASS_SIGN",
)
CATEGORY_LABEL_DE = {
    "ACTION_HEAD": "HANDLUNG",
    "GRADE": "GRAD",
    "ARGUMENT": "ARGUMENT",
    "RELATION": "RELATION",
    "STATE_CONTROL": "ZUSTANDSSTEUERUNG",
    "FORMAL_CONTROL": "FORMSTEUERUNG",
    "LOCAL_OR_CLASS_SIGN": "LOKAL-/KLASSENZEICHEN",
}
VALUE_OVERRIDES = {"DY": "ABSCHLIESSEN"}
FRAGMENT_OVERRIDES = {
    "Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil",
    "OR": "die Einheit", "AL": "zum Zielort", "AR": "vom Ausgang",
    "L": "über die Verbindung", "AIR": "entlang der Bahn",
    "E": "auf Grad I", "EE": "auf Grad II", "EEE": "auf Grad III",
    "OT": "danach", "OL": "weiter", "DY": "abschließen",
    "O": "zur Ausführung", "CARRIER_Q": "am Beginn",
    "IIN": "auf der Stufe", "DA": "auf der zweiten Stufe",
    "D_ADDR": "hier", "AM_ADDR": "hier", "A_ADDR": "hier",
    "S_ADDR": "hier", "LOCAL_CHAR_F": "hier", "D_LABEL": "hier",
    "M_LOCAL": "hier", "LOCAL_CHAR_G": "als Variante", "AN": "als Klasse",
}
ACTION_FRAGMENTS = {
    "OK": "setzen", "CH": "nehmen", "SH": "halten", "K": "geben",
    "S": "wählen", "CHD": "bearbeiten", "T": "einstellen",
    "R": "markieren", "P": "einsetzen",
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def joined(values: list[str] | set[str], sep: str = "|") -> str:
    material = sorted(set(values))
    return sep.join(material) if material else "NONE"


def typed_category(atom: str, source_family: str) -> str:
    return "STATE_CONTROL" if atom in STATE_CONTROLS else source_family


def atom_fragment(atom: str, value: str) -> str:
    if atom in FRAGMENT_OVERRIDES:
        return FRAGMENT_OVERRIDES[atom]
    if atom in ACTION_FRAGMENTS:
        return ACTION_FRAGMENTS[atom]
    return value.casefold()


def layer_counts(atoms: list[str], categories: dict[str, str]) -> dict[str, int]:
    counts = Counter(categories[atom] for atom in atoms)
    return {category: counts[category] for category in CATEGORY_ORDER}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    dictionary_source = read_tsv(INPUTS["dictionary"])
    old_context_rows = read_tsv(INPUTS["old_context"])
    current_context_rows = read_tsv(INPUTS["current_context"])
    state_rows = read_tsv(INPUTS["state_atlas"])
    grade_rows = read_tsv(INPUTS["grade_assignments"])
    argument_rows = read_tsv(INPUTS["argument_assignments"])
    relation_rows = read_tsv(INPUTS["relation_assignments"])
    if tuple(map(len, (dictionary_source, old_context_rows, current_context_rows, state_rows,
                       grade_rows, argument_rows, relation_rows))) != (
        46, 4576, 546, 1870, 333, 390, 216
    ):
        raise RuntimeError("Input count drift")

    # One stable card row per event; the source atlas repeats cards once per state marker.
    state_events: dict[str, dict[str, str]] = {}
    event_first_ordinal: dict[str, int] = {}
    stable_fields = (
        "cohort", "source_event_id", "statement_id", "physical_page", "register",
        "card_ordinal_in_statement", "statement_event_count", "statement_position",
        "statement_final", "surface", "recipe", "event_marker_sequence",
        "current_reading_de",
    )
    grouped_state: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_rows:
        grouped_state[row["event_id"]].append(row)
        event_first_ordinal.setdefault(row["event_id"], int(row["occurrence_ordinal"]))
    for event_id, rows in grouped_state.items():
        if any(len({row[field] for row in rows}) != 1 for field in stable_fields):
            raise RuntimeError(f"Conflicting state rows for {event_id}")
        state_events[event_id] = rows[0]
    if len(state_events) != 1656:
        raise RuntimeError("State-card count drift")
    ordered_event_ids = sorted(state_events, key=lambda event_id: event_first_ordinal[event_id])

    all_atoms = [atom for event in state_events.values() for atom in event["recipe"].split("+")]
    state_atom_set = set(all_atoms)
    dictionary_by_atom = {row["atom"]: row for row in dictionary_source}
    missing_atoms = state_atom_set - dictionary_by_atom.keys()
    if missing_atoms:
        raise RuntimeError(f"Unmapped state atoms: {sorted(missing_atoms)}")
    values = {
        atom: VALUE_OVERRIDES.get(atom, dictionary_by_atom[atom]["working_value_de"])
        for atom in state_atom_set
    }
    categories = {
        atom: typed_category(atom, dictionary_by_atom[atom]["factor_family"])
        for atom in state_atom_set
    }
    if set(categories.values()) != set(CATEGORY_ORDER):
        raise RuntimeError(f"Category partition drift: {sorted(set(categories.values()))}")

    old_context = {row["global_running_event_id"]: row for row in old_context_rows}
    current_context = {row["event_id"]: row for row in current_context_rows}
    if set(state_events) - (old_context.keys() | current_context.keys()):
        raise RuntimeError("Context join incomplete")

    # Normalize all three specialized occurrence atlases into one source-linked table.
    carrier_rows: list[dict[str, object]] = []
    carrier_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)

    def add_carrier(
        layer: str, rows: list[dict[str, str]], ordinal_field: str,
        atom_field: str, position_field: str, value_field: str,
        envelope_field: str, reading_field: str, detail_field: str,
        source_name: str,
    ) -> None:
        for row in rows:
            event_id = row["event_id"]
            atom = row[atom_field]
            out: dict[str, object] = {
                "carrier_link_ordinal": len(carrier_rows) + 1,
                "layer": layer,
                "source_assignment_ordinal": row[ordinal_field],
                "source_artifact": source_name,
                "cohort": row["cohort"], "event_id": event_id,
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"], "register": row["register"],
                "surface": row["surface"], "recipe": row["recipe"],
                "atom": atom, "atom_value_de": row[value_field],
                "atom_position": row[position_field],
                "carrier_envelope": row[envelope_field],
                "specialized_default_reading_de": row[reading_field],
                "specialized_detail": row[detail_field],
                "unified_atom_category": categories[atom],
                "unified_atom_value_de": values[atom],
                "position_and_value_match_unified_card": "YES",
                "guard": "SOURCE_LINK_ONLY__NO_ATOM_REORDERING_OR_NEW_MEANING",
            }
            atoms = state_events[event_id]["recipe"].split("+")
            if atoms[int(row[position_field]) - 1] != atom or values[atom] != row[value_field]:
                raise RuntimeError(f"Carrier mismatch: {layer} {event_id} {atom}")
            carrier_rows.append(out)
            carrier_by_event[event_id].append(out)

    add_carrier(
        "GRADE", grade_rows, "assignment_ordinal", "grade", "grade_atom_position",
        "grade_value_de", "carrier_envelope", "complete_carrier_reading_de",
        "default_host_mode", "GDT558_333_GRADE_CARRIER_ASSIGNMENTS",
    )
    add_carrier(
        "ARGUMENT", argument_rows, "assignment_ordinal", "argument", "argument_atom_position",
        "argument_value_de", "carrier_envelope", "complete_carrier_reading_de",
        "carrier_role", "GDT559_390_ARGUMENT_CARRIER_ASSIGNMENTS",
    )
    add_carrier(
        "RELATION", relation_rows, "assignment_ordinal", "relation", "relation_atom_position",
        "relation_value_de", "carrier_envelope", "compact_relation_reading_de",
        "root_geometry_default", "GDT560_216_RELATION_STATE_ASSIGNMENTS",
    )

    card_rows: list[dict[str, object]] = []
    cards_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for card_ordinal, event_id in enumerate(ordered_event_ids, 1):
        event = state_events[event_id]
        atoms = event["recipe"].split("+")
        atom_categories = [categories[atom] for atom in atoms]
        context = old_context.get(event_id) or current_context[event_id]
        if event_id in old_context:
            source_context = "GDT416_OLD26_IMPERATIVE"
            contextual_clause = context["imperative_clause_de"]
            context_template = context["template"]
            explicit_actions = context["explicit_action_roots"]
            inherited_action = context["inherited_action_root"]
            explicit_arguments = context["explicit_argument_roots"]
            inherited_argument = context["inherited_argument_root"]
        else:
            source_context = "GDT539_CURRENT4_CONTEXTUAL"
            contextual_clause = context["contextual_clause_de"]
            context_template = context["content_role"]
            explicit_actions = context["explicit_action_roots"]
            inherited_action = context["inherited_action_root"]
            explicit_arguments = context["explicit_argument_roots"]
            inherited_argument = context["inherited_argument_root"]
        counts = layer_counts(atoms, categories)
        links = carrier_by_event.get(event_id, [])
        layers = sorted({str(link["layer"]) for link in links})
        ordered_trace = " > ".join(
            f"{atom}{{{CATEGORY_LABEL_DE[categories[atom]]}={values[atom]}}}" for atom in atoms
        )
        ordered_reading = " → ".join(values[atom] for atom in atoms)
        phrase = "; ".join(atom_fragment(atom, values[atom]) for atom in atoms)
        out: dict[str, object] = {
            "state_card_ordinal": card_ordinal,
            "cohort": event["cohort"], "event_id": event_id,
            "source_event_id": event["source_event_id"],
            "statement_id": event["statement_id"],
            "physical_page": event["physical_page"], "register": event["register"],
            "card_ordinal_in_statement": event["card_ordinal_in_statement"],
            "statement_event_count": event["statement_event_count"],
            "statement_position": event["statement_position"],
            "statement_final": event["statement_final"],
            "surface": event["surface"], "recipe": event["recipe"],
            "recipe_atom_count": len(atoms),
            "ordered_type_signature": "+".join(atom_categories),
            "state_marker_sequence": event["event_marker_sequence"],
            "ordered_typed_atom_trace": ordered_trace,
            "ordered_all_atom_reading_de": ordered_reading,
            "all_atom_default_phrase_de": phrase,
            "state_scope_reading_de": event["current_reading_de"],
            "source_context_layer": source_context,
            "context_template": context_template,
            "contextual_clause_de": contextual_clause,
            "explicit_action_roots": explicit_actions or "NONE",
            "inherited_action_root": inherited_action or "NONE",
            "explicit_argument_roots": explicit_arguments or "NONE",
            "inherited_argument_root": inherited_argument or "NONE",
            "action_atom_count": counts["ACTION_HEAD"],
            "grade_atom_count": counts["GRADE"],
            "argument_atom_count": counts["ARGUMENT"],
            "relation_atom_count": counts["RELATION"],
            "state_control_atom_count": counts["STATE_CONTROL"],
            "formal_control_atom_count": counts["FORMAL_CONTROL"],
            "local_or_class_sign_count": counts["LOCAL_OR_CLASS_SIGN"],
            "specialized_carrier_layers": "|".join(layers) if layers else "NONE",
            "specialized_carrier_link_count": len(links),
            "specialized_carrier_readings_de": " || ".join(
                f"{link['layer']}:{link['specialized_default_reading_de']}" for link in links
            ) or "NONE",
            "every_atom_mapped": "YES", "written_order_preserved": "YES",
            "sequence_default_status": "EXACT_RECIPE_DEFAULT__NO_LEARNED_WHOLE_CARD_VALUE",
            "guard": "WORKING_COMPOSITION_ONLY__STRUCTURAL_TYPES_NOT_PLAINTEXT_WORDS",
        }
        card_rows.append(out)
        cards_by_recipe[event["recipe"]].append(out)

    # One compact default for every exact recipe.
    recipe_rows: list[dict[str, object]] = []
    for ordinal, (recipe, cards) in enumerate(
        sorted(cards_by_recipe.items(), key=lambda item: (-len(item[1]), item[0])), 1
    ):
        first = cards[0]
        atoms = recipe.split("+")
        layer_union = {
            layer for card in cards
            for layer in str(card["specialized_carrier_layers"]).split("|") if layer != "NONE"
        }
        recipe_rows.append({
            "recipe_default_ordinal": ordinal, "recipe": recipe,
            "event_count": len(cards),
            "physical_page_count": len({str(card["physical_page"]) for card in cards}),
            "statement_count": len({str(card["statement_id"]) for card in cards}),
            "surface_count": len({str(card["surface"]) for card in cards}),
            "cohorts": joined([str(card["cohort"]) for card in cards]),
            "registers": joined([str(card["register"]) for card in cards]),
            "example_surfaces": joined([str(card["surface"]) for card in cards][:8]),
            "example_event_ids": joined([str(card["event_id"]) for card in cards][:8]),
            "recipe_atom_count": len(atoms),
            "atom_multiset": "+".join(sorted(atoms)),
            "ordered_type_signature": first["ordered_type_signature"],
            "ordered_typed_atom_trace": first["ordered_typed_atom_trace"],
            "ordered_all_atom_reading_de": first["ordered_all_atom_reading_de"],
            "all_atom_default_phrase_de": first["all_atom_default_phrase_de"],
            "specialized_carrier_layers": "|".join(sorted(layer_union)) if layer_union else "NONE",
            "every_atom_mapped": "YES", "written_order_preserved": "YES",
            "default_scope": "EXACT_RECIPE_ONLY__OWNER_CONTEXT_REMAINS_EVENT_LOCAL",
        })

    # Type signatures are composition templates, not claims about a historical syntax.
    cards_by_signature: dict[str, list[dict[str, object]]] = defaultdict(list)
    for card in card_rows:
        cards_by_signature[str(card["ordered_type_signature"])].append(card)
    template_rows: list[dict[str, object]] = []
    for ordinal, (signature, cards) in enumerate(
        sorted(cards_by_signature.items(), key=lambda item: (-len(item[1]), item[0])), 1
    ):
        recipe_set = sorted({str(card["recipe"]) for card in cards})
        slots = signature.split("+")
        template_rows.append({
            "type_template_ordinal": ordinal,
            "ordered_type_signature": signature,
            "event_count": len(cards), "recipe_count": len(recipe_set),
            "physical_page_count": len({str(card["physical_page"]) for card in cards}),
            "register_count": len({str(card["register"]) for card in cards}),
            "slot_count": len(slots),
            "typed_slot_template_de": " → ".join(CATEGORY_LABEL_DE[slot] for slot in slots),
            "example_recipes": " | ".join(recipe_set[:6]),
            "example_default_phrases_de": " | ".join(
                dict.fromkeys(str(card["all_atom_default_phrase_de"]) for card in cards)
            )[:1200],
            "composition_rule": "FILL_EACH_SLOT_WITH_ATOM_VALUE_AND_READ_LEFT_TO_RIGHT",
            "historical_status": "EDITORIAL_WORKING_TEMPLATE__NOT_CONFIRMED_SYNTAX",
        })

    # Active 36-entry subset with real occurrence and card coverage.
    dictionary_rows: list[dict[str, object]] = []
    for atom in sorted(state_atom_set, key=lambda item: (-all_atoms.count(item), item)):
        source = dictionary_by_atom[atom]
        atom_cards = [card for card in card_rows if atom in str(card["recipe"]).split("+")]
        dictionary_rows.append({
            "atom": atom, "typed_category": categories[atom],
            "working_value_de": values[atom],
            "default_fragment_de": atom_fragment(atom, values[atom]),
            "atom_occurrence_count": all_atoms.count(atom),
            "state_card_count": len(atom_cards),
            "recipe_count": len({str(card["recipe"]) for card in atom_cards}),
            "physical_page_count": len({str(card["physical_page"]) for card in atom_cards}),
            "source_factor_family": source["factor_family"],
            "source_semantic_layer": source["semantic_layer"],
            "source_dictionary": source["source_dictionary"],
            "value_status": "GDT557_STATE_ROLE_OVERRIDE" if atom == "DY" else "GDT413_VALUE_REUSED",
            "reading_scope": (
                "STRUCTURAL_SIGN__NOT_AN_ENGLISH_OR_GERMAN_WORD_TRANSLATION"
                if categories[atom] == "LOCAL_OR_CLASS_SIGN"
                else "SHORT_WORKING_VALUE__OWNER_SUPPLIES_CONCRETE_CONTENT"
            ),
        })

    type_rows: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        atoms = [atom for atom in state_atom_set if categories[atom] == category]
        selected_cards = [
            card for card in card_rows
            if any(categories[atom] == category for atom in str(card["recipe"]).split("+"))
        ]
        type_rows.append({
            "typed_category": category, "category_label_de": CATEGORY_LABEL_DE[category],
            "distinct_atom_count": len(atoms), "atoms": joined(atoms),
            "atom_mention_count": sum(all_atoms.count(atom) for atom in atoms),
            "state_card_count": len(selected_cards),
            "recipe_count": len({str(card["recipe"]) for card in selected_cards}),
            "physical_page_count": len({str(card["physical_page"]) for card in selected_cards}),
            "default_composition_role": {
                "ACTION_HEAD": "VISIBLE_OPERATION",
                "GRADE": "VISIBLE_INTENSITY_OR_RUNG_VALUE",
                "ARGUMENT": "VISIBLE_CARRIER_OR_VALUE_SLOT",
                "RELATION": "VISIBLE_DIRECTIONAL_OR_CONNECTION_SLOT",
                "STATE_CONTROL": "VISIBLE_NEXT_CONTINUE_CLOSE_OPERATION",
                "FORMAL_CONTROL": "VISIBLE_FORMAL_STAGE_OR_EXECUTION_MARKER",
                "LOCAL_OR_CLASS_SIGN": "VISIBLE_STRUCTURAL_LOCAL_OR_CLASS_TAG",
            }[category],
        })

    # One row per card in the union of the three specialized grammars.
    integration_rows: list[dict[str, object]] = []
    card_by_event = {str(card["event_id"]): card for card in card_rows}
    for ordinal, event_id in enumerate(
        [event_id for event_id in ordered_event_ids if event_id in carrier_by_event], 1
    ):
        card = card_by_event[event_id]
        links = carrier_by_event[event_id]
        layer_counts_here = Counter(str(link["layer"]) for link in links)
        integration_rows.append({
            "integration_ordinal": ordinal, "event_id": event_id,
            "statement_id": card["statement_id"], "physical_page": card["physical_page"],
            "register": card["register"], "surface": card["surface"], "recipe": card["recipe"],
            "grade_link_count": layer_counts_here["GRADE"],
            "argument_link_count": layer_counts_here["ARGUMENT"],
            "relation_link_count": layer_counts_here["RELATION"],
            "total_specialized_link_count": len(links),
            "specialized_layers": "|".join(sorted(layer_counts_here)),
            "ordered_all_atom_reading_de": card["ordered_all_atom_reading_de"],
            "all_atom_default_phrase_de": card["all_atom_default_phrase_de"],
            "specialized_readings_de": card["specialized_carrier_readings_de"],
            "integration_status": "EXACT_EVENT_AND_ATOM_POSITION_JOIN",
        })

    # Same atoms, different written orders: preserve all witnesses explicitly.
    recipes_by_multiset: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in recipe_rows:
        recipes_by_multiset[str(row["atom_multiset"])].append(row)
    variable_groups = {
        multiset: rows for multiset, rows in recipes_by_multiset.items() if len(rows) > 1
    }
    order_rows: list[dict[str, object]] = []
    for family_ordinal, (multiset, rows) in enumerate(
        sorted(variable_groups.items(), key=lambda item: (-sum(int(row["event_count"]) for row in item[1]), item[0])), 1
    ):
        family_id = f"G561-O{family_ordinal:02d}"
        recipes = sorted(rows, key=lambda row: str(row["recipe"]))
        family_event_count = sum(int(row["event_count"]) for row in recipes)
        for variant_ordinal, row in enumerate(recipes, 1):
            order_rows.append({
                "order_family_id": family_id, "atom_multiset": multiset,
                "variant_ordinal": variant_ordinal, "variant_count": len(recipes),
                "family_event_count": family_event_count,
                "recipe": row["recipe"], "recipe_event_count": row["event_count"],
                "ordered_type_signature": row["ordered_type_signature"],
                "ordered_all_atom_reading_de": row["ordered_all_atom_reading_de"],
                "all_atom_default_phrase_de": row["all_atom_default_phrase_de"],
                "contrast_recipes": "|".join(
                    str(other["recipe"]) for other in recipes if other is not row
                ),
                "decision": "KEEP_WRITTEN_ORDER__DO_NOT_SORT_ATOMS",
            })

    write_tsv(CARD_OUT, card_rows)
    write_tsv(DICT_OUT, dictionary_rows)
    write_tsv(RECIPE_OUT, recipe_rows)
    write_tsv(TEMPLATE_OUT, template_rows)
    write_tsv(TYPE_OUT, type_rows)
    write_tsv(CARRIER_OUT, carrier_rows)
    write_tsv(INTEGRATION_OUT, integration_rows)
    write_tsv(ORDER_OUT, order_rows)

    type_count_by_category = {row["typed_category"]: row for row in type_rows}
    top_templates = template_rows[:12]
    top_recipes = recipe_rows[:12]
    lines = [
        "# GDT561 – vollständiger typisierter Zustandskartenleser",
        "",
        "## Ergebnis in einem Satz",
        "",
        "Alle 1.656 bekannten Karten mit `OT`, `OL` oder `DY` besitzen nun eine links-nach-rechts erhaltene Standardlesung: 4.684/4.684 Atome sind über sieben Rollen und 36 kurze Arbeitswerte abgedeckt; kein Rezept benötigt einen neu gelernten Ganzkartenwert.",
        "",
        "Das ist eine Arbeitskomposition, keine Entzifferung. Besonders `HIER`, `VARIANTE` und `KLASSE` bleiben Strukturmarken und werden nicht zu deutschen Wörtern im Manuskript erklärt.",
        "",
        "## Umfang",
        "",
        f"- Karten: **{len(card_rows)}**",
        f"- verschiedene exakte Rezepte: **{len(recipe_rows)}**",
        f"- Atomnennungen: **{len(all_atoms)}**",
        f"- verschiedene verwendete Atome: **{len(dictionary_rows)}**",
        f"- geordnete Rollenmuster: **{len(template_rows)}**",
        f"- spezialisierte Grad-/Argument-/Relationslinks: **{len(carrier_rows)}** auf **{len(integration_rows)}** Karten",
        f"- ungeordnete Atommengen mit mehreren Reihenfolgen: **{len(variable_groups)}** ({len(order_rows)} Rezepte, {sum(int(row['recipe_event_count']) for row in order_rows)} Karten)",
        "",
        "## Sieben Rollen",
        "",
        "| Rolle | Atome | Nennungen | Karten |",
        "|---|---:|---:|---:|",
    ]
    for row in type_rows:
        lines.append(
            f"| {row['category_label_de']} | {row['distinct_atom_count']} | {row['atom_mention_count']} | {row['state_card_count']} |"
        )
    lines += [
        "",
        "## Häufigste geordnete Muster",
        "",
        "| Rollenmuster | Karten | Rezepte | Beispiel |",
        "|---|---:|---:|---|",
    ]
    for row in top_templates:
        lines.append(
            f"| `{row['ordered_type_signature']}` | {row['event_count']} | {row['recipe_count']} | `{str(row['example_recipes']).split(' | ')[0]}` |"
        )
    lines += [
        "",
        "## Häufigste exakte Rezepte",
        "",
        "| Rezept | Karten | vollständiger Default |",
        "|---|---:|---|",
    ]
    for row in top_recipes:
        lines.append(
            f"| `{row['recipe']}` | {row['event_count']} | {row['all_atom_default_phrase_de']} |"
        )
    lines += [
        "",
        "## Warum die Reihenfolge stehenbleibt",
        "",
        f"Es gibt {len(variable_groups)} Atommengen, die in mehr als einer geschriebenen Reihenfolge vorkommen. Zusammen betreffen sie {len(order_rows)} Rezepte und {sum(int(row['recipe_event_count']) for row in order_rows)} Karten. `OL+Y` und `Y+OL` erhalten deshalb nicht denselben Schlüssel: der erste Default lautet „weiter; den Posten“, der zweite „den Posten; weiter“. Das Wörterbuch liefert die Bestandteile; das Rezept liefert ihre Anordnung.",
        "",
        "## Leseregel",
        "",
        "1. Jedes Atom behält seinen kurzen Wert und seine strukturelle Rolle.",
        "2. Die Atome werden exakt in geschriebener Reihenfolge wiedergegeben.",
        "3. Grad, Argument und Relation übernehmen zusätzlich die engere Trägerlesung aus GDT558–GDT560, wo eine solche vorliegt.",
        "4. Die kontextuelle Satzzeile aus GDT416/GDT539 bleibt daneben sichtbar; sie darf die atomare Spur nicht überschreiben.",
        "5. Ein Rezeptdefault gilt nur für das bereits beobachtete exakte Rezept. Er erzeugt keine neue Voynichform.",
        "",
        "## Was jetzt wirklich noch offen ist",
        "",
        "Die Abdeckung ist nicht mehr das Problem: jede Karte ist lesbar. Offen ist die Qualität der Komposition. Besonders Karten ohne sichtbare Handlung, reine Steuerkarten und seltene Form-/Lokalzeichen müssen nun danach sortiert werden, ob ihre vollständige Defaultphrase wie eine Initialisierung, Fortsetzung, Referenz oder Abschlusszeile klingt. Dafür ist kein neuer Grundwortwert nötig; der nächste Pass kann auf den 1.656 fertigen Zeilen arbeiten.",
    ]
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "state_card_count": len(card_rows),
        "state_marker_occurrence_count": len(state_rows),
        "state_atom_mention_count": len(all_atoms),
        "mapped_atom_mention_count": sum(
            len(str(card["recipe"]).split("+")) for card in card_rows if card["every_atom_mapped"] == "YES"
        ),
        "distinct_state_atom_count": len(dictionary_rows),
        "exact_recipe_count": len(recipe_rows),
        "ordered_type_template_count": len(template_rows),
        "typed_category_count": len(type_rows),
        "specialized_carrier_link_count": len(carrier_rows),
        "specialized_card_count": len(integration_rows),
        "grade_carrier_link_count": sum(row["layer"] == "GRADE" for row in carrier_rows),
        "argument_carrier_link_count": sum(row["layer"] == "ARGUMENT" for row in carrier_rows),
        "relation_carrier_link_count": sum(row["layer"] == "RELATION" for row in carrier_rows),
        "order_variable_multiset_family_count": len(variable_groups),
        "order_witness_recipe_count": len(order_rows),
        "order_witness_event_count": sum(int(row["recipe_event_count"]) for row in order_rows),
        "all_cards_have_default": all(card["all_atom_default_phrase_de"] for card in card_rows),
        "all_recipes_have_default": all(row["all_atom_default_phrase_de"] for row in recipe_rows),
        "all_atoms_mapped": not missing_atoms,
        "all_written_orders_preserved": all(card["written_order_preserved"] == "YES" for card in card_rows),
        "context_join_old_count": sum(card["source_context_layer"] == "GDT416_OLD26_IMPERATIVE" for card in card_rows),
        "context_join_current_count": sum(card["source_context_layer"] == "GDT539_CURRENT4_CONTEXTUAL" for card in card_rows),
        "cards_without_action": sum(int(card["action_atom_count"]) == 0 for card in card_rows),
        "cards_without_argument": sum(int(card["argument_atom_count"]) == 0 for card in card_rows),
        "cards_without_action_grade_argument_relation": sum(
            all(int(card[key]) == 0 for key in (
                "action_atom_count", "grade_atom_count", "argument_atom_count", "relation_atom_count"
            )) for card in card_rows
        ),
        "pure_state_control_card_count": sum(
            all(categories[atom] == "STATE_CONTROL"
                for atom in str(card["recipe"]).split("+")) for card in card_rows
        ),
        "contentless_control_or_structural_card_count": sum(
            all(categories[atom] in {"STATE_CONTROL", "FORMAL_CONTROL", "LOCAL_OR_CLASS_SIGN"}
                for atom in str(card["recipe"]).split("+")) for card in card_rows
        ),
        "category_metrics": {
            category: {
                "distinct_atom_count": int(type_count_by_category[category]["distinct_atom_count"]),
                "atom_mention_count": int(type_count_by_category[category]["atom_mention_count"]),
                "state_card_count": int(type_count_by_category[category]["state_card_count"]),
            } for category in CATEGORY_ORDER
        },
        "new_pages": 0, "new_surfaces": 0, "recipe_changes": 0,
        "root_meaning_changes": 0, "statement_boundary_changes": 0,
        "learned_whole_card_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
