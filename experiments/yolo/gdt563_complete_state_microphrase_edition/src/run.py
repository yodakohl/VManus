#!/usr/bin/env python3
"""Compile one owner-free microphrase for every GDT561 state card."""

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
BASE = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition"
OUT = BASE / "artifacts"
G561 = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts"
G562 = ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader/artifacts"

INPUTS = {
    "typed_cards": G561 / "gdt561_1656_typed_state_cards.tsv",
    "state_dictionary": G561 / "gdt561_36_state_atom_dictionary.tsv",
    "actionless_reader": G562 / "gdt562_706_actionless_state_reader.tsv",
}

CARD_OUT = OUT / "gdt563_1656_complete_state_microphrases.tsv"
VISIBLE_OUT = OUT / "gdt563_950_visible_action_microphrases.tsv"
ACTIONLESS_LINK_OUT = OUT / "gdt563_706_actionless_source_links.tsv"
RECIPE_OUT = OUT / "gdt563_402_recipe_context_profiles.tsv"
SEQUENCE_OUT = OUT / "gdt563_9_state_sequence_profiles.tsv"
MODE_OUT = OUT / "gdt563_8_resolution_mode_profiles.tsv"
REPEAT_OUT = OUT / "gdt563_16_repeated_action_cards.tsv"
VARIABILITY_OUT = OUT / "gdt563_context_variability_summary.tsv"
BOOK_OUT = OUT / "GDT563_COMPLETE_STATE_MICROPHRASE_BOOK.md"
RESULT_OUT = OUT / "gdt563_result.json"

STATUS_BASE = (
    "PASS_1656_COMPLETE_STATE_MICROPHRASES__706_ACTIONLESS_PLUS_950_VISIBLE__"
    "ALL_ACTION_SLOTS_RETAINED__402_CONTEXT_PROFILES"
)

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
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
SEQUENCE_ROLES = {
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
MODE_DE = {
    "VISIBLE_ACTION_FULL_OPERATION": "sichtbare Handlung mit wirksamem Argument",
    "VISIBLE_ACTION_OBJECTLESS_OPERATION": "sichtbare objektlose Handlung",
    "INHERITED_ACTION_FULL_OPERATION": "geerbte Handlung mit wirksamem Argument",
    "INHERITED_ACTION_OBJECTLESS_OPERATION": "geerbte objektlose Handlung",
    "ARGUMENT_REFERENCE_INITIALIZER": "Argumentbezug ohne Handlung",
    "FORMAL_RELATION_PROLOGUE": "formaler oder relationaler Vorspann",
    "STANDALONE_GRADED_CLOSE": "selbständiger abgestufter Abschluss",
    "PURE_CONTINUATION": "reine Fortsetzung",
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


def split_roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def argument_phrase(roots: list[str]) -> str:
    if roots == ["Y", "Y"]:
        return "die beiden Posten"
    phrases = [ARGUMENT_PHRASES[root] for root in roots]
    if not phrases:
        return "NONE"
    if len(phrases) == 1:
        return phrases[0]
    return ", ".join(phrases[:-1]) + " und " + phrases[-1]


def action_phrase(root: str, argument_roots: list[str]) -> str:
    no_object, with_object = ACTION_TEMPLATES[root]
    return with_object.format(argument=argument_phrase(argument_roots)) if argument_roots else no_object


def action_units(atoms: list[str]) -> list[tuple[str, int]]:
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
    return units


def render_action_chain(
    atoms: list[str], argument_roots: list[str]
) -> tuple[str, str, list[str], bool]:
    roots = [atom for atom in atoms if atom in ACTIONS]
    expanded = " und ".join(action_phrase(root, argument_roots) for root in roots)
    rendered_units = []
    compressed = False
    expanded_from_units: list[str] = []
    for root, repeat in action_units(atoms):
        phrase = action_phrase(root, argument_roots)
        if repeat == 2:
            rendered_units.append(phrase + " zweimal")
            compressed = True
        elif repeat == 1:
            rendered_units.append(phrase)
        else:
            rendered_units.append(phrase + f" {repeat}-mal")
            compressed = True
        expanded_from_units.extend([root] * repeat)
    if expanded_from_units != roots:
        raise RuntimeError("Action unit roundtrip failed")
    return " und ".join(rendered_units), expanded, roots, compressed


def compose_microphrase(
    action_chain: str, modifiers: str, marker_sequence: str,
) -> tuple[str, str]:
    state_role, prefix, suffix = SEQUENCE_ROLES[marker_sequence]
    parts = [part for part in (action_chain, modifiers if modifiers != "NONE" else "", suffix) if part]
    if prefix:
        phrase = f"{prefix}: " + "; ".join(parts) if parts else prefix
    else:
        phrase = "; ".join(parts)
    phrase = phrase[0].upper() + phrase[1:] + "." if phrase else "Fortfahren."
    return phrase, state_role


def variability_band(count: int) -> str:
    if count == 1:
        return "ONE_MICROPHRASE"
    if count <= 5:
        return "TWO_TO_FIVE"
    if count <= 10:
        return "SIX_TO_TEN"
    return "OVER_TEN"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    typed_cards = read_tsv(INPUTS["typed_cards"])
    dictionary = read_tsv(INPUTS["state_dictionary"])
    actionless_rows = read_tsv(INPUTS["actionless_reader"])
    if tuple(map(len, (typed_cards, dictionary, actionless_rows))) != (1656, 36, 706):
        raise RuntimeError("Input count drift")

    dictionary_by_atom = {row["atom"]: row for row in dictionary}
    fragments = {atom: row["default_fragment_de"] for atom, row in dictionary_by_atom.items()}
    actionless_by_id = {row["event_id"]: row for row in actionless_rows}
    source_actionless_ids = {row["event_id"] for row in typed_cards if row["action_atom_count"] == "0"}
    if set(actionless_by_id) != source_actionless_ids:
        raise RuntimeError("GDT562 actionless partition drift")

    card_rows: list[dict[str, object]] = []
    visible_rows: list[dict[str, object]] = []
    actionless_link_rows: list[dict[str, object]] = []
    repeated_rows: list[dict[str, object]] = []
    for card in typed_cards:
        event_id = card["event_id"]
        atoms = card["recipe"].split("+")
        alignment = " | ".join(
            f"{index}:{atom}={fragments[atom]}" for index, atom in enumerate(atoms, 1)
        )
        if card["action_atom_count"] == "0":
            source = actionless_by_id[event_id]
            microphrase = source["owner_free_resolved_microphrase_de"]
            effective_actions = source["effective_action_root"]
            effective_arguments = source["effective_argument_roots"]
            resolution_mode = ACTIONLESS_MODE_MAP[source["completeness_role"]]
            state_role = source["state_sequence_role"]
            action_chain_de = (
                source["effective_action_value_de"].casefold()
                if source["effective_action_value_de"] != "NONE" else "NONE"
            )
            expanded_action_chain_de = action_chain_de
            written_action_roots = "NONE"
            written_action_slot_count = 0
            contextual_action_slot_count = 1 if effective_actions != "NONE" else 0
            modifier_phrase = source["visible_modifier_phrase_de"]
            repeat_status = "NO_VISIBLE_ACTION"
            source_layer = "GDT562_ACTIONLESS_STATE_READER"
            source_pointer = source["action_source_event_id"]
            actionless_link_rows.append({
                "actionless_link_ordinal": len(actionless_link_rows) + 1,
                "event_id": event_id, "statement_id": card["statement_id"],
                "physical_page": card["physical_page"], "register": card["register"],
                "surface": card["surface"], "recipe": card["recipe"],
                "gdt562_completeness_role": source["completeness_role"],
                "effective_action_root": effective_actions,
                "effective_argument_roots": effective_arguments,
                "gdt562_microphrase_de": source["owner_free_resolved_microphrase_de"],
                "gdt563_microphrase_de": microphrase,
                "microphrase_byte_identical": "YES",
                "source_link_status": "EXACT_EVENT_JOIN",
            })
        else:
            explicit_argument_roots = split_roots(card["explicit_argument_roots"])
            written_argument_roots = [atom for atom in atoms if atom in ARGUMENTS]
            if explicit_argument_roots != written_argument_roots:
                raise RuntimeError(f"Visible argument order mismatch at {event_id}")
            effective_argument_roots = (
                explicit_argument_roots
                if explicit_argument_roots
                else split_roots(card["inherited_argument_root"])
            )
            action_chain_de, expanded_action_chain_de, action_roots, compressed = render_action_chain(
                atoms, effective_argument_roots
            )
            if len(action_roots) != int(card["action_atom_count"]):
                raise RuntimeError(f"Visible action count mismatch at {event_id}")
            modifier_atoms = [
                atom for atom in atoms
                if atom not in ACTIONS | ARGUMENTS | STATE_CONTROLS
            ]
            modifier_phrase = "; ".join(fragments[atom] for atom in modifier_atoms) or "NONE"
            microphrase, state_role = compose_microphrase(
                action_chain_de, modifier_phrase, card["state_marker_sequence"]
            )
            effective_actions = "|".join(action_roots)
            effective_arguments = "|".join(effective_argument_roots) or "NONE"
            resolution_mode = (
                "VISIBLE_ACTION_FULL_OPERATION"
                if effective_argument_roots else "VISIBLE_ACTION_OBJECTLESS_OPERATION"
            )
            written_action_roots = effective_actions
            written_action_slot_count = len(action_roots)
            contextual_action_slot_count = 0
            repeat_status = (
                "DIRECT_ADJACENT_REPEAT_COMPRESSED"
                if compressed else "REPEATED_ROOTS_SEPARATED_AND_RETAINED"
                if len(action_roots) != len(set(action_roots)) else "NO_REPEATED_ACTION_ROOT"
            )
            source_layer = "GDT563_VISIBLE_ACTION_RENDERER"
            source_pointer = event_id
            visible_out = {
                "visible_action_ordinal": len(visible_rows) + 1,
                "event_id": event_id, "statement_id": card["statement_id"],
                "physical_page": card["physical_page"], "register": card["register"],
                "surface": card["surface"], "recipe": card["recipe"],
                "written_action_roots": written_action_roots,
                "written_action_slot_count": written_action_slot_count,
                "effective_argument_roots": effective_arguments,
                "argument_source": (
                    "VISIBLE_ARGUMENT_IN_CARD" if explicit_argument_roots
                    else "INHERITED_ARGUMENT_CONTEXT" if effective_argument_roots
                    else "NO_ACTIVE_ARGUMENT"
                ),
                "rendered_action_chain_de": action_chain_de,
                "expanded_action_chain_de": expanded_action_chain_de,
                "visible_modifier_phrase_de": modifier_phrase,
                "state_sequence_role": state_role,
                "owner_free_microphrase_de": microphrase,
                "repeat_status": repeat_status,
                "all_action_slots_retained": "YES",
                "guard": "VISIBLE_ACTION_ORDER_FIXED__CONTEXT_ARGUMENT_NOT_A_WRITTEN_ATOM",
            }
            visible_rows.append(visible_out)
            if len(action_roots) != len(set(action_roots)):
                repeated_rows.append({
                    "repeated_card_ordinal": len(repeated_rows) + 1,
                    "event_id": event_id, "statement_id": card["statement_id"],
                    "physical_page": card["physical_page"], "register": card["register"],
                    "surface": card["surface"], "recipe": card["recipe"],
                    "written_action_roots": written_action_roots,
                    "written_action_slot_count": written_action_slot_count,
                    "distinct_action_root_count": len(set(action_roots)),
                    "direct_adjacent_repeat": "YES" if compressed else "NO",
                    "repeat_status": repeat_status,
                    "rendered_action_chain_de": action_chain_de,
                    "expanded_action_chain_de": expanded_action_chain_de,
                    "owner_free_microphrase_de": microphrase,
                    "action_slot_roundtrip": "YES",
                })

        out: dict[str, object] = {
            "state_microphrase_ordinal": len(card_rows) + 1,
            "cohort": card["cohort"], "event_id": event_id,
            "statement_id": card["statement_id"],
            "physical_page": card["physical_page"], "register": card["register"],
            "card_ordinal_in_statement": card["card_ordinal_in_statement"],
            "statement_position": card["statement_position"],
            "statement_final": card["statement_final"],
            "surface": card["surface"], "recipe": card["recipe"],
            "ordered_type_signature": card["ordered_type_signature"],
            "state_marker_sequence": card["state_marker_sequence"],
            "state_sequence_role": state_role,
            "ordered_typed_atom_trace": card["ordered_typed_atom_trace"],
            "written_all_atom_default_de": card["all_atom_default_phrase_de"],
            "written_atom_alignment": alignment,
            "written_action_roots": written_action_roots,
            "written_action_slot_count": written_action_slot_count,
            "contextual_action_slot_count": contextual_action_slot_count,
            "effective_action_roots": effective_actions,
            "effective_argument_roots": effective_arguments,
            "rendered_action_chain_de": action_chain_de,
            "expanded_action_chain_de": expanded_action_chain_de,
            "visible_modifier_phrase_de": modifier_phrase,
            "resolution_mode": resolution_mode,
            "resolution_mode_de": MODE_DE[resolution_mode],
            "microphrase_source_layer": source_layer,
            "action_context_source_event_id": source_pointer,
            "owner_free_microphrase_de": microphrase,
            "owner_bound_context_clause_de": card["contextual_clause_de"],
            "specialized_carrier_readings_de": card["specialized_carrier_readings_de"],
            "repeat_status": repeat_status,
            "all_written_atoms_retained": "YES",
            "all_written_action_slots_retained": "YES",
            "microphrase_scope": "EXACT_EVENT_CONTEXT__NOT_UNIVERSAL_RECIPE_SENTENCE",
            "guard": "THREE_CHANNEL_READER__ATOM_TRACE_MICROPHRASE_AND_OWNER_CONTEXT_DISTINCT",
        }
        card_rows.append(out)

    if (len(card_rows), len(visible_rows), len(actionless_link_rows), len(repeated_rows)) != (1656, 950, 706, 16):
        raise RuntimeError("Output population drift")

    cards_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in card_rows:
        cards_by_recipe[str(row["recipe"])].append(row)
    recipe_rows: list[dict[str, object]] = []
    for ordinal, (recipe, material) in enumerate(
        sorted(cards_by_recipe.items(), key=lambda item: (-len(item[1]), item[0])), 1
    ):
        microphrases = list(dict.fromkeys(str(row["owner_free_microphrase_de"]) for row in material))
        actions = {str(row["effective_action_roots"]) for row in material}
        arguments = {str(row["effective_argument_roots"]) for row in material}
        modes = {str(row["resolution_mode"]) for row in material}
        recipe_rows.append({
            "recipe_profile_ordinal": ordinal, "recipe": recipe,
            "event_count": len(material),
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "surface_count": len({str(row["surface"]) for row in material}),
            "distinct_microphrase_count": len(microphrases),
            "distinct_effective_action_signature_count": len(actions),
            "distinct_effective_argument_signature_count": len(arguments),
            "resolution_mode_count": len(modes),
            "resolution_modes": "|".join(sorted(modes)),
            "context_variability_band": variability_band(len(microphrases)),
            "written_recipe_determines_microphrase": "YES" if len(microphrases) == 1 else "NO",
            "written_all_atom_default_de": material[0]["written_all_atom_default_de"],
            "most_common_microphrase_de": Counter(
                str(row["owner_free_microphrase_de"]) for row in material
            ).most_common(1)[0][0],
            "example_microphrases_de": " | ".join(microphrases)[:1800],
            "example_event_ids": "|".join(str(row["event_id"]) for row in material[:10]),
            "scope": "EXACT_RECIPE_PROFILE__EVENT_CONTEXT_SELECTS_MICROPHRASE",
        })

    mode_counts = Counter(str(row["resolution_mode"]) for row in card_rows)
    mode_rows: list[dict[str, object]] = []
    for mode, count in sorted(mode_counts.items(), key=lambda item: (-item[1], item[0])):
        material = [row for row in card_rows if row["resolution_mode"] == mode]
        mode_rows.append({
            "resolution_mode": mode, "resolution_mode_de": MODE_DE[mode],
            "event_count": count,
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "register_count": len({str(row["register"]) for row in material}),
            "distinct_recipe_count": len({str(row["recipe"]) for row in material}),
            "statement_final_count": sum(row["statement_final"] == "YES" for row in material),
            "example_microphrases_de": " | ".join(dict.fromkeys(str(row["owner_free_microphrase_de"]) for row in material))[:1400],
            "mode_status": "COMPLETE_MICROPHRASE_ROUTE",
        })

    sequence_counts = Counter(str(row["state_marker_sequence"]) for row in card_rows)
    sequence_rows: list[dict[str, object]] = []
    for sequence, count in sorted(sequence_counts.items(), key=lambda item: (-item[1], item[0])):
        material = [row for row in card_rows if row["state_marker_sequence"] == sequence]
        sequence_rows.append({
            "state_marker_sequence": sequence,
            "state_sequence_role": SEQUENCE_ROLES[sequence][0],
            "event_count": count,
            "visible_action_count": sum(int(row["written_action_slot_count"]) > 0 for row in material),
            "actionless_count": sum(int(row["written_action_slot_count"]) == 0 for row in material),
            "statement_final_count": sum(row["statement_final"] == "YES" for row in material),
            "distinct_recipe_count": len({str(row["recipe"]) for row in material}),
            "distinct_microphrase_count": len({str(row["owner_free_microphrase_de"]) for row in material}),
            "example_microphrases_de": " | ".join(dict.fromkeys(str(row["owner_free_microphrase_de"]) for row in material))[:1600],
            "composition_status": "COMPLETE_SEQUENCE_ROUTE",
        })

    band_counts = Counter(row["context_variability_band"] for row in recipe_rows)
    variability_rows: list[dict[str, object]] = []
    for band in ("ONE_MICROPHRASE", "TWO_TO_FIVE", "SIX_TO_TEN", "OVER_TEN"):
        material = [row for row in recipe_rows if row["context_variability_band"] == band]
        variability_rows.append({
            "context_variability_band": band,
            "recipe_count": len(material),
            "event_count": sum(int(row["event_count"]) for row in material),
            "maximum_microphrase_count": max((int(row["distinct_microphrase_count"]) for row in material), default=0),
            "example_recipes": "|".join(str(row["recipe"]) for row in sorted(material, key=lambda row: (-int(row["distinct_microphrase_count"]), str(row["recipe"])))[:12]) or "NONE",
            "interpretation": (
                "WRITTEN_RECIPE_HAS_ONE_OWNER_FREE_MICROPHRASE_IN_CURRENT_CONTEXTS"
                if band == "ONE_MICROPHRASE"
                else "EVENT_STATE_SELECTS_AMONG_MULTIPLE_OWNER_FREE_MICROPHRASES"
            ),
        })

    write_tsv(CARD_OUT, card_rows)
    write_tsv(VISIBLE_OUT, visible_rows)
    write_tsv(ACTIONLESS_LINK_OUT, actionless_link_rows)
    write_tsv(RECIPE_OUT, recipe_rows)
    write_tsv(SEQUENCE_OUT, sequence_rows)
    write_tsv(MODE_OUT, mode_rows)
    write_tsv(REPEAT_OUT, repeated_rows)
    write_tsv(VARIABILITY_OUT, variability_rows)

    stable_recipes = band_counts["ONE_MICROPHRASE"]
    variable_recipes = len(recipe_rows) - stable_recipes
    variable_events = sum(
        int(row["event_count"]) for row in recipe_rows
        if row["written_recipe_determines_microphrase"] == "NO"
    )
    singleton_recipes = sum(int(row["event_count"]) == 1 for row in recipe_rows)
    recurrent_recipes = len(recipe_rows) - singleton_recipes
    recurrent_stable_recipes = sum(
        int(row["event_count"]) > 1 and row["written_recipe_determines_microphrase"] == "YES"
        for row in recipe_rows
    )
    max_profile = max(recipe_rows, key=lambda row: int(row["distinct_microphrase_count"]))
    direct_compressions = sum(row["direct_adjacent_repeat"] == "YES" for row in repeated_rows)
    status = STATUS_BASE + f"__{stable_recipes}_STABLE_{variable_recipes}_CONTEXT_VARIABLE_RECIPES"
    lines = [
        "# GDT563 – vollständige ownerfreie Zustandskarten-Ausgabe",
        "",
        "## Ergebnis",
        "",
        "Alle1.656 Zustandskarten besitzen nun drei gleichzeitig sichtbare Lesekanäle: exakte Atomspur, ownerfreie Mikrophrase und besitzergebundene Kontextzeile. Die706 aktionslosen Mikrophrasen werden bytegleich aus GDT562 übernommen;950 Karten werden aus ihren sichtbaren Handlungen komponiert.",
        "",
        "```text",
        "950 sichtbare Handlungsrouten",
        "706 Zustandsellipsen aus GDT562",
        "402 exakte Rezeptprofile",
        "  9 Zustandsfolgen",
        "  8 Auflösungsmodi",
        "```",
        "",
        "## Auflösungsmodi",
        "",
        "| Modus | Karten |",
        "|---|---:|",
    ]
    for row in mode_rows:
        lines.append(f"| {row['resolution_mode_de']} | {row['event_count']} |")
    lines += [
        "",
        "## Rezept ist nicht immer Satz",
        "",
        f"Nur{stable_recipes}/402 Rezepte haben in allen aktuellen Ereigniskontexten genau eine ownerfreie Mikrophrase;{variable_recipes} variieren und decken{variable_events} Karten. Von den301 scheinbar stabilen Rezepten sind allerdings{singleton_recipes} Einzelbelege. Unter den{recurrent_recipes} wiederholten Rezepten bleiben nur{recurrent_stable_recipes} stabil, während{variable_recipes} kontextabhängig sind. Das variabelste Rezept `{max_profile['recipe']}` besitzt{max_profile['distinct_microphrase_count']} Mikrophrasen. Der feste Teil ist seine Atomfolge; Handlung/Argument aus dem Satzspeicher wählen die konkrete Zeile.",
        "",
        "## Wiederholte Handlungen",
        "",
        f"Sechzehn Karten wiederholen einen Handlungsroot. Nur{direct_compressions} besitzen unmittelbar benachbarte identische Schriftatome und werden mit „zweimal“ komprimiert. Die übrigen bleiben als getrennte Handlungsslots sichtbar, weil ein Grad, Argument oder Zustandsoperator dazwischensteht. Jede komprimierte Zeile bewahrt zusätzlich die expandierte Aktionskette.",
        "",
        "## Drei Kanäle",
        "",
        "```text",
        "Atomspur       was sichtbar geschrieben und wie es typisiert ist",
        "Mikrophrase    ownerfreie, zustandsaufgelöste Arbeitsanweisung",
        "Kontextzeile   konkrete Pflanze/Station/Position/Droge bzw. Textsektion",
        "```",
        "",
        "Keiner der drei Kanäle darf die anderen ersetzen. Besonders darf eine kontextuell eingesetzte Handlung nicht als neue Wortbedeutung des sichtbaren Steueratoms zurückgeschrieben werden.",
    ]
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {
        "status": status,
        "complete_state_card_count": len(card_rows),
        "visible_action_card_count": len(visible_rows),
        "actionless_source_link_count": len(actionless_link_rows),
        "exact_recipe_profile_count": len(recipe_rows),
        "state_sequence_profile_count": len(sequence_rows),
        "resolution_mode_count": len(mode_rows),
        "repeated_action_card_count": len(repeated_rows),
        "direct_adjacent_repeat_compression_count": direct_compressions,
        "separated_repeat_retention_count": len(repeated_rows) - direct_compressions,
        "stable_single_microphrase_recipe_count": stable_recipes,
        "context_variable_recipe_count": variable_recipes,
        "context_variable_recipe_event_count": variable_events,
        "singleton_recipe_count": singleton_recipes,
        "recurrent_recipe_count": recurrent_recipes,
        "recurrent_stable_recipe_count": recurrent_stable_recipes,
        "recurrent_context_variable_recipe_count": variable_recipes,
        "maximum_microphrase_count_for_one_recipe": int(max_profile["distinct_microphrase_count"]),
        "maximum_variability_recipe": max_profile["recipe"],
        "resolution_mode_counts": dict(mode_counts),
        "state_sequence_counts": dict(sequence_counts),
        "context_variability_band_counts": dict(band_counts),
        "full_operation_count": mode_counts["VISIBLE_ACTION_FULL_OPERATION"] + mode_counts["INHERITED_ACTION_FULL_OPERATION"],
        "objectless_operation_count": mode_counts["VISIBLE_ACTION_OBJECTLESS_OPERATION"] + mode_counts["INHERITED_ACTION_OBJECTLESS_OPERATION"],
        "all_cards_have_microphrase": all(row["owner_free_microphrase_de"] for row in card_rows),
        "all_written_atoms_retained": all(row["all_written_atoms_retained"] == "YES" for row in card_rows),
        "all_written_action_slots_retained": all(row["all_written_action_slots_retained"] == "YES" for row in card_rows),
        "all_actionless_phrases_byte_identical": all(row["microphrase_byte_identical"] == "YES" for row in actionless_link_rows),
        "new_pages": 0, "new_surfaces": 0, "new_recipes": 0,
        "new_root_values": 0, "new_written_atoms": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
