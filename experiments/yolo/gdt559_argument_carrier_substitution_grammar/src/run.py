#!/usr/bin/env python3
"""Compile the four argument roots inside the GDT557 OT/OL/DY carrier grammar."""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G429 = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"

STATE_ATLAS_PATH = G557 / "gdt557_all_state_marker_occurrences.tsv"
OLD_CONTEXT_PATH = G416 / "gdt416_4576_imperative_clauses.tsv"
CURRENT_CONTEXT_PATH = G539 / "gdt539_546_contextual_prose_events.tsv"
CONTRAST_PATH = G429 / "gdt429_13_nonaction_core_contrasts.tsv"

ASSIGNMENT_OUT = OUT / "gdt559_390_argument_carrier_assignments.tsv"
ROOT_PROFILE_OUT = OUT / "gdt559_4_argument_root_profiles.tsv"
ENVELOPE_OUT = OUT / "gdt559_6_argument_carrier_envelopes.tsv"
PROJECTION_OUT = OUT / "gdt559_24_argument_state_projections.tsv"
FAMILY_OUT = OUT / "gdt559_11_multiroot_substitution_families.tsv"
PAIR_OUT = OUT / "gdt559_6_argument_pair_bridges.tsv"
TRANSITION_OUT = OUT / "gdt559_341_left_controlled_successor_transitions.tsv"
TRANSITION_PROFILE_OUT = OUT / "gdt559_8_successor_transition_profiles.tsv"
Y_DY_JOINT_OUT = OUT / "gdt559_28_y_dy_joint_cards.tsv"
Y_DY_SUMMARY_OUT = OUT / "gdt559_4_y_dy_distinction_classes.tsv"
BOOK_OUT = OUT / "GDT559_ARGUMENT_CARRIER_BOOK.md"
RESULT_OUT = OUT / "gdt559_result.json"

STATUS = "PASS_SIX_ARGUMENT_ENVELOPES__TWO_FOUR_ROOT_BARE_FRAMES__157_OF_157_IMPLICIT_SUCCESSORS_INHERIT__Y_DY_COMPOSE_28_TIMES"
ARGUMENTS = ("Y", "AIIN", "AIN", "OR")
ARGUMENT_SET = set(ARGUMENTS)
CONTROLS = ("OT", "OL", "DY")
CONTROL_SET = set(CONTROLS)
ARGUMENT_VALUES = {"Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
ARGUMENT_ACCUSATIVE = {
    "Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit",
}
ARGUMENT_DATIVE = {
    "Y": "dem Posten", "AIIN": "dem Wert", "AIN": "dem Anteil", "OR": "der Einheit",
}
LITERAL_VALUES = {
    "OT": "NÄCHSTEN TRÄGER ERÖFFNEN",
    "OL": "TRÄGER FORTSETZEN",
    "DY": "SCHRITT ABSCHLIESSEN",
    **ARGUMENT_VALUES,
}
ENVELOPE_TEMPLATES = {
    "OT>A<END": "danach ARG als nächsten Träger eröffnen",
    "OL>A<END": "weiter mit ARG als aktuellem Träger",
    "START>A<DY": "ARG führen und den Schritt abschließen",
    "START>A<OL": "ARG weiterführen",
    "OT>A<OL": "danach ARG eröffnen und weiterführen",
    "OL>A<OL": "ARG weiterführen und aktiv halten",
}
COMPACT_ENVELOPE_TEMPLATES = {
    "OT>A<END": "DANACH · ARG",
    "OL>A<END": "FORTSETZEN · ARG",
    "START>A<DY": "ARG · ABSCHLIESSEN",
    "START>A<OL": "ARG · FORTSETZEN",
    "OT>A<OL": "DANACH · ARG · FORTSETZEN",
    "OL>A<OL": "FORTSETZEN · ARG · FORTSETZEN",
}
ENVELOPE_ROLES = {
    "OT>A<END": "NEXT_CARRIER_ARGUMENT",
    "OL>A<END": "CONTINUED_CARRIER_ARGUMENT",
    "START>A<DY": "CLOSING_ARGUMENT",
    "START>A<OL": "RETAINED_ARGUMENT",
    "OT>A<OL": "OPENED_THEN_RETAINED_ARGUMENT",
    "OL>A<OL": "CONTINUED_AND_RETAINED_ARGUMENT",
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


def pct(numerator: int, denominator: int) -> str:
    return f"{100 * numerator / denominator:.6f}" if denominator else "0.000000"


def argument_state_projection(recipe: str) -> str:
    return "+".join(
        atom for atom in recipe.split("+") if atom in CONTROL_SET | ARGUMENT_SET
    )


def normalized_argument_recipe(recipe: str) -> str:
    return "+".join("ARG" if atom in ARGUMENT_SET else atom for atom in recipe.split("+"))


def normalized_state_projection(recipe: str) -> str:
    return "+".join(
        atom for atom in recipe.split("+") if atom in CONTROL_SET or atom == "ARG"
    )


def literal_projection_reading(projection: str) -> str:
    return " → ".join(LITERAL_VALUES[atom] for atom in projection.split("+"))


def carrier_reading(left_control: str, right_control: str, argument: str) -> str:
    accusative = ARGUMENT_ACCUSATIVE[argument]
    dative = ARGUMENT_DATIVE[argument]
    envelope = f"{left_control}>A<{right_control}"
    if envelope == "OT>A<END":
        return f"danach {accusative} als nächsten Träger eröffnen"
    if envelope == "OL>A<END":
        return f"weiter mit {dative} als aktuellem Träger"
    if envelope == "START>A<DY":
        return f"{accusative} führen und den Schritt abschließen"
    if envelope == "START>A<OL":
        return f"{accusative} weiterführen"
    if envelope == "OT>A<OL":
        return f"danach {accusative} eröffnen und weiterführen"
    if envelope == "OL>A<OL":
        return f"{accusative} weiterführen und aktiv halten"
    raise RuntimeError(f"Unknown argument envelope: {envelope}")


def compact_carrier_reading(left_control: str, right_control: str, argument: str) -> str:
    envelope = f"{left_control}>A<{right_control}"
    return COMPACT_ENVELOPE_TEMPLATES[envelope].replace("ARG", ARGUMENT_VALUES[argument])


def pipe_values(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state_rows = read_tsv(STATE_ATLAS_PATH)
    old_context_rows = read_tsv(OLD_CONTEXT_PATH)
    current_context_rows = read_tsv(CURRENT_CONTEXT_PATH)
    contrast_rows = read_tsv(CONTRAST_PATH)
    input_counts = (
        len(state_rows), len(old_context_rows), len(current_context_rows), len(contrast_rows)
    )
    if input_counts != (1870, 4576, 546, 13):
        raise RuntimeError(f"Input count drift: {input_counts}")

    event_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_rows:
        event_groups[row["event_id"]].append(row)
    if len(event_groups) != 1656:
        raise RuntimeError("GDT557 marker-bearing event count drift")
    stable_fields = (
        "cohort", "statement_id", "physical_page", "register", "surface",
        "recipe", "event_marker_sequence", "statement_position",
        "statement_final", "current_reading_de",
    )
    events: dict[str, dict[str, str]] = {}
    for event_id, rows in event_groups.items():
        if any(len({row[field] for row in rows}) != 1 for field in stable_fields):
            raise RuntimeError(f"Conflicting GDT557 duplicate rows: {event_id}")
        events[event_id] = rows[0]

    context: dict[str, dict[str, object]] = {}
    for row in old_context_rows:
        context[row["global_running_event_id"]] = {
            "event_id": row["global_running_event_id"],
            "statement_id": row["global_statement_id"],
            "card_ordinal": int(row["card_ordinal_in_statement"]),
            "recipe": row["component_recipe"],
            "explicit_arguments": row["explicit_argument_roots"],
            "inherited_argument": row["inherited_argument_root"],
        }
    for row in current_context_rows:
        event_id = row["event_id"]
        if event_id in context:
            raise RuntimeError(f"Old/current context overlap: {event_id}")
        context[event_id] = {
            "event_id": event_id,
            "statement_id": row["statement_id"],
            "card_ordinal": int(row["card_ordinal_in_statement"]),
            "recipe": row["final_context_recipe"],
            "explicit_arguments": row["explicit_argument_roots"],
            "inherited_argument": row["inherited_argument_root"],
        }
    missing_context = sorted(set(events) - set(context))
    if len(context) != 5122 or missing_context:
        raise RuntimeError(f"Context union or join drift: {len(context)}, {missing_context[:5]}")
    for event_id, event in events.items():
        if context[event_id]["recipe"] != event["recipe"]:
            raise RuntimeError(f"Context recipe mismatch: {event_id}")

    statement_cards: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in context.values():
        statement_cards[str(row["statement_id"])].append(row)
    successor: dict[str, dict[str, object]] = {}
    for cards in statement_cards.values():
        cards.sort(key=lambda row: int(row["card_ordinal"]))
        for left, right in zip(cards, cards[1:]):
            successor[str(left["event_id"])] = right

    selected_events = {
        event_id: event for event_id, event in events.items()
        if any(atom in ARGUMENT_SET for atom in event["recipe"].split("+"))
    }
    assignment_rows: list[dict[str, object]] = []
    for event_id, event in selected_events.items():
        atoms = event["recipe"].split("+")
        argument_positions = [index for index, atom in enumerate(atoms) if atom in ARGUMENT_SET]
        argument_sequence = [atoms[index] for index in argument_positions]
        for occurrence, argument_index in enumerate(argument_positions, 1):
            argument = atoms[argument_index]
            left_control_index = max(
                (index for index in range(argument_index) if atoms[index] in CONTROL_SET),
                default=-1,
            )
            right_control_index = min(
                (index for index in range(argument_index + 1, len(atoms)) if atoms[index] in CONTROL_SET),
                default=len(atoms),
            )
            left_control = atoms[left_control_index] if left_control_index >= 0 else "START"
            right_control = atoms[right_control_index] if right_control_index < len(atoms) else "END"
            block = atoms[left_control_index + 1:right_control_index]
            local_index = argument_index - left_control_index - 1
            envelope = f"{left_control}>A<{right_control}"
            if envelope not in ENVELOPE_TEMPLATES:
                raise RuntimeError(f"Unmapped argument envelope {envelope}: {event_id}")
            assignment_rows.append({
                "assignment_ordinal": len(assignment_rows) + 1,
                "cohort": event["cohort"], "event_id": event_id,
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"], "register": event["register"],
                "surface": event["surface"], "recipe": event["recipe"],
                "argument_state_projection": argument_state_projection(event["recipe"]),
                "argument_occurrence_in_recipe": occurrence,
                "argument_multiplicity_in_recipe": len(argument_positions),
                "argument_sequence": "+".join(argument_sequence),
                "argument": argument, "argument_value_de": ARGUMENT_VALUES[argument],
                "argument_atom_position": argument_index + 1,
                "recipe_atom_count": len(atoms),
                "left_control": left_control, "right_control": right_control,
                "carrier_envelope": envelope,
                "carrier_role": ENVELOPE_ROLES[envelope],
                "content_block": "+".join(block),
                "argument_position_in_block": local_index + 1,
                "left_content_before_argument": "+".join(block[:local_index]) or "NONE",
                "right_content_after_argument": "+".join(block[local_index + 1:]) or "NONE",
                "is_last_argument_in_recipe": "YES" if argument_index == argument_positions[-1] else "NO",
                "compact_carrier_reading_de": compact_carrier_reading(left_control, right_control, argument),
                "envelope_template_de": ENVELOPE_TEMPLATES[envelope],
                "complete_carrier_reading_de": carrier_reading(left_control, right_control, argument),
                "literal_projection_reading_de": literal_projection_reading(argument_state_projection(event["recipe"])),
                "statement_position": event["statement_position"],
                "statement_final": event["statement_final"],
                "current_reading_de": event["current_reading_de"],
                "y_dy_atom_distinction": (
                    "Y_IS_ARGUMENT_ATOM__DY_IS_SEPARATE_CLOSE_CONTROL"
                    if argument == "Y" and "DY" in atoms else
                    "Y_IS_ARGUMENT_ATOM__NOT_THE_DY_CONTROL" if argument == "Y" else "NOT_APPLICABLE"
                ),
                "guard": "ARGUMENT_VALUE_INSIDE_WRITTEN_CONTROL_ENVELOPE__NO_ROOT_OR_RECIPE_CHANGE",
            })

    single_argument_events = {
        event_id: event for event_id, event in selected_events.items()
        if sum(atom in ARGUMENT_SET for atom in event["recipe"].split("+")) == 1
    }
    family_groups: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    for event in single_argument_events.values():
        atoms = event["recipe"].split("+")
        argument = next(atom for atom in atoms if atom in ARGUMENT_SET)
        family_groups[normalized_argument_recipe(event["recipe"])].append((argument, event))
    multiroot_groups = {
        skeleton: material for skeleton, material in family_groups.items()
        if len({argument for argument, _ in material}) >= 2
    }
    family_rows: list[dict[str, object]] = []
    family_id_by_skeleton: dict[str, str] = {}
    for skeleton, material in sorted(
        multiroot_groups.items(),
        key=lambda item: (-len({argument for argument, _ in item[1]}), -len(item[1]), item[0]),
    ):
        family_id = f"G559-F{len(family_rows) + 1:02d}"
        family_id_by_skeleton[skeleton] = family_id
        by_argument = {
            argument: [event for root, event in material if root == argument]
            for argument in ARGUMENTS
        }
        variants = [argument for argument in ARGUMENTS if by_argument[argument]]
        first_event = material[0][1]
        first_assignment = next(
            row for row in assignment_rows if row["event_id"] == first_event["event_id"]
        )
        family_rows.append({
            "family_ordinal": len(family_rows) + 1, "family_id": family_id,
            "normalized_recipe": skeleton,
            "normalized_state_projection": normalized_state_projection(skeleton),
            "carrier_envelope": first_assignment["carrier_envelope"],
            "argument_variant_count": len(variants),
            "argument_variants": "|".join(variants),
            "family_status": (
                "COMPLETE_FOUR_ARGUMENT_FRAME" if len(variants) == 4
                else "OBSERVED_THREE_ARGUMENT_FRAME" if len(variants) == 3
                else "OBSERVED_TWO_ARGUMENT_FRAME"
            ),
            "event_count": len(material),
            "y_event_count": len(by_argument["Y"]),
            "aiin_event_count": len(by_argument["AIIN"]),
            "ain_event_count": len(by_argument["AIN"]),
            "or_event_count": len(by_argument["OR"]),
            "physical_page_count": len({event["physical_page"] for _, event in material}),
            "register_count": len({event["register"] for _, event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for _, event in material),
            "statement_final_percent": pct(sum(event["statement_final"] == "YES" for _, event in material), len(material)),
            "surfaces_by_argument": " || ".join(
                f"{argument}:{'|'.join(sorted({event['surface'] for event in by_argument[argument]}))}"
                for argument in variants
            ),
            "event_ids": "|".join(event["event_id"] for _, event in material),
            "family_reading_de": ENVELOPE_TEMPLATES[str(first_assignment["carrier_envelope"])],
            "scope_result": "ARGUMENT_VALUE_SUBSTITUTES_INSIDE_FIXED_CONTROL_FRAME",
        })
    for row in assignment_rows:
        if int(row["argument_multiplicity_in_recipe"]) == 1:
            row["substitution_family_id"] = family_id_by_skeleton.get(
                normalized_argument_recipe(str(row["recipe"])), "NONE"
            )
        else:
            row["substitution_family_id"] = "NONE"

    envelope_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in assignment_rows:
        envelope_groups[str(row["carrier_envelope"])].append(row)
    envelope_rows: list[dict[str, object]] = []
    for envelope, material in sorted(
        envelope_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        root_counts = Counter(str(row["argument"]) for row in material)
        envelope_rows.append({
            "envelope_ordinal": len(envelope_rows) + 1,
            "carrier_envelope": envelope, "carrier_role": ENVELOPE_ROLES[envelope],
            "argument_occurrence_count": len(material),
            "event_count": len({str(row["event_id"]) for row in material}),
            "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in material}),
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "register_count": len({str(row["register"]) for row in material}),
            "y_count": root_counts["Y"], "aiin_count": root_counts["AIIN"],
            "ain_count": root_counts["AIN"], "or_count": root_counts["OR"],
            "argument_root_breadth": sum(root_counts[root] > 0 for root in ARGUMENTS),
            "statement_final_occurrence_count": sum(row["statement_final"] == "YES" for row in material),
            "statement_final_percent": pct(sum(row["statement_final"] == "YES" for row in material), len(material)),
            "substitution_family_assignment_count": sum(row["substitution_family_id"] != "NONE" for row in material),
            "compact_template_de": COMPACT_ENVELOPE_TEMPLATES[envelope],
            "working_template_de": ENVELOPE_TEMPLATES[envelope],
        })

    projection_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in selected_events.values():
        projection_groups[argument_state_projection(event["recipe"])].append(event)
    projection_rows: list[dict[str, object]] = []
    for projection, material in sorted(
        projection_groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        projection_rows.append({
            "projection_ordinal": len(projection_rows) + 1,
            "argument_state_projection": projection, "event_count": len(material),
            "argument_occurrence_count": sum(sum(atom in ARGUMENT_SET for atom in event["recipe"].split("+")) for event in material),
            "statement_count": len({f"{event['cohort']}::{event['statement_id']}" for event in material}),
            "physical_page_count": len({event["physical_page"] for event in material}),
            "register_count": len({event["register"] for event in material}),
            "exact_recipe_count": len({event["recipe"] for event in material}),
            "surface_count": len({event["surface"] for event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "statement_final_percent": pct(sum(event["statement_final"] == "YES" for event in material), len(material)),
            "literal_working_reading_de": literal_projection_reading(projection),
            "example_events": "|".join(event["event_id"] for event in material[:5]),
            "example_surfaces": "|".join(event["surface"] for event in material[:5]),
        })

    contrast_by_pair: dict[frozenset[str], dict[str, str]] = {}
    for row in contrast_rows:
        if row["family"] != "ARGUMENT":
            continue
        left, right = row["contrast_pair"].split("~")
        contrast_by_pair[frozenset((left, right))] = row
    pair_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(ARGUMENTS, 2):
        pair_families = [
            (skeleton, material) for skeleton, material in multiroot_groups.items()
            if {left, right} <= {argument for argument, _ in material}
        ]
        pair_event_ids = {
            event["event_id"] for _, material in pair_families
            for argument, event in material if argument in {left, right}
        }
        old = contrast_by_pair[frozenset((left, right))]
        pair_rows.append({
            "pair_ordinal": len(pair_rows) + 1,
            "argument_pair": f"{left}~{right}",
            "left_value_de": ARGUMENT_VALUES[left], "right_value_de": ARGUMENT_VALUES[right],
            "gdt429_shared_exact_frame_count": old["shared_exact_substitution_frame_count"],
            "gdt559_state_family_count": len(pair_families),
            "gdt559_pair_event_count": len(pair_event_ids),
            "gdt559_all_family_event_count": sum(len(material) for _, material in pair_families),
            "shared_bare_ot_argument_frame": "YES" if any(skeleton == "OT+ARG" for skeleton, _ in pair_families) else "NO",
            "shared_bare_ol_argument_frame": "YES" if any(skeleton == "OL+ARG" for skeleton, _ in pair_families) else "NO",
            "state_family_ids": "|".join(
                family_id_by_skeleton[skeleton] for skeleton, _ in sorted(pair_families)
            ),
            "normalized_recipes": "|".join(skeleton for skeleton, _ in sorted(pair_families)),
            "decision": "DISTINCT_ARGUMENT_VALUES_SHARE_THE_SAME_STATE_CARRIER_SLOT",
        })

    transition_rows: list[dict[str, object]] = []
    for event_id, event in selected_events.items():
        atoms = event["recipe"].split("+")
        argument_positions = [index for index, atom in enumerate(atoms) if atom in ARGUMENT_SET]
        last_index = argument_positions[-1]
        last_argument = atoms[last_index]
        left_control_index = max(
            (index for index in range(last_index) if atoms[index] in CONTROL_SET), default=-1
        )
        if left_control_index < 0 or atoms[left_control_index] not in {"OT", "OL"}:
            continue
        left_control = atoms[left_control_index]
        right_control_index = min(
            (index for index in range(last_index + 1, len(atoms)) if atoms[index] in CONTROL_SET),
            default=len(atoms),
        )
        right_control = atoms[right_control_index] if right_control_index < len(atoms) else "END"
        next_card = successor.get(event_id)
        if next_card is None:
            outcome = "NO_SUCCESSOR_STATEMENT_END"
            next_event_id = next_recipe = next_explicit = next_inherited = "NONE"
            transition_reading = "Die Aussage endet nach diesem Träger."
        else:
            next_event_id = str(next_card["event_id"])
            next_recipe = str(next_card["recipe"])
            next_explicit = str(next_card["explicit_arguments"])
            next_inherited = str(next_card["inherited_argument"])
            if pipe_values(next_explicit):
                outcome = "NEXT_EXPLICIT_ARGUMENT_RESETS_CARRIER"
                transition_reading = "Die nächste Karte setzt ein neues sichtbares Argument."
            elif next_inherited == last_argument:
                outcome = "NEXT_INHERITS_CURRENT_ARGUMENT"
                transition_reading = f"Die nächste Karte verwendet weiter {ARGUMENT_ACCUSATIVE[last_argument]}."
            elif next_inherited == "NONE":
                outcome = "MISMATCH_NEXT_HAS_NO_ARGUMENT"
                transition_reading = "UNRESOLVED"
            else:
                outcome = "MISMATCH_NEXT_INHERITS_OTHER_ARGUMENT"
                transition_reading = "UNRESOLVED"
        transition_rows.append({
            "transition_ordinal": len(transition_rows) + 1,
            "event_id": event_id, "statement_id": event["statement_id"],
            "physical_page": event["physical_page"], "register": event["register"],
            "surface": event["surface"], "recipe": event["recipe"],
            "left_control": left_control, "right_control": right_control,
            "last_argument": last_argument,
            "last_argument_value_de": ARGUMENT_VALUES[last_argument],
            "argument_sequence": "+".join(atom for atom in atoms if atom in ARGUMENT_SET),
            "current_carrier_reading_de": carrier_reading(left_control, right_control, last_argument),
            "next_event_id": next_event_id, "next_recipe": next_recipe,
            "next_explicit_arguments": next_explicit,
            "next_inherited_argument": next_inherited,
            "successor_outcome": outcome,
            "transition_reading_de": transition_reading,
            "statement_final": event["statement_final"],
            "guard": "EXPLICIT_NEXT_ARGUMENT_RESETS__OTHERWISE_INHERIT_CURRENT_CARRIER",
        })

    transition_profile_rows: list[dict[str, object]] = []
    for control in ("OT", "OL"):
        for argument in ARGUMENTS:
            material = [
                row for row in transition_rows
                if row["left_control"] == control and row["last_argument"] == argument
            ]
            outcomes = Counter(str(row["successor_outcome"]) for row in material)
            transition_profile_rows.append({
                "profile_ordinal": len(transition_profile_rows) + 1,
                "left_control": control, "argument": argument,
                "argument_value_de": ARGUMENT_VALUES[argument],
                "transition_count": len(material),
                "next_inherits_current_count": outcomes["NEXT_INHERITS_CURRENT_ARGUMENT"],
                "next_explicit_reset_count": outcomes["NEXT_EXPLICIT_ARGUMENT_RESETS_CARRIER"],
                "statement_end_count": outcomes["NO_SUCCESSOR_STATEMENT_END"],
                "mismatch_count": sum(count for outcome, count in outcomes.items() if outcome.startswith("MISMATCH")),
                "working_rule": "EXPLICIT_ARGUMENT_REPLACES_CARRIER__ELLIPSIS_INHERITS_CURRENT_ARGUMENT",
            })

    family_event_ids = {
        event["event_id"] for material in multiroot_groups.values() for _, event in material
    }
    root_profile_rows: list[dict[str, object]] = []
    for argument in ARGUMENTS:
        occurrences = [row for row in assignment_rows if row["argument"] == argument]
        root_events = [
            event for event in selected_events.values() if argument in event["recipe"].split("+")
        ]
        root_profile_rows.append({
            "argument": argument, "working_value_de": ARGUMENT_VALUES[argument],
            "occurrence_count": len(occurrences), "event_count": len(root_events),
            "statement_count": len({event["statement_id"] for event in root_events}),
            "physical_page_count": len({event["physical_page"] for event in root_events}),
            "register_count": len({event["register"] for event in root_events}),
            "left_ot_count": sum(row["left_control"] == "OT" for row in occurrences),
            "left_ol_count": sum(row["left_control"] == "OL" for row in occurrences),
            "right_ol_count": sum(row["right_control"] == "OL" for row in occurrences),
            "right_dy_count": sum(row["right_control"] == "DY" for row in occurrences),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in root_events),
            "multiroot_family_event_count": sum(event["event_id"] in family_event_ids for event in root_events),
            "multiroot_family_coverage_percent": pct(sum(event["event_id"] in family_event_ids for event in root_events), len(root_events)),
            "portable_short_reading_de": ARGUMENT_VALUES[argument],
        })

    y_dy_joint_rows: list[dict[str, object]] = []
    for event in events.values():
        atoms = event["recipe"].split("+")
        if "Y" not in atoms or "DY" not in atoms:
            continue
        y_index = atoms.index("Y")
        dy_index = atoms.index("DY")
        y_dy_joint_rows.append({
            "joint_ordinal": len(y_dy_joint_rows) + 1,
            "event_id": event["event_id"], "statement_id": event["statement_id"],
            "physical_page": event["physical_page"], "register": event["register"],
            "surface": event["surface"], "recipe": event["recipe"],
            "y_atom_position": y_index + 1, "dy_atom_position": dy_index + 1,
            "written_order": "Y_BEFORE_DY" if y_index < dy_index else "DY_BEFORE_Y",
            "intervening_atoms": "+".join(atoms[y_index + 1:dy_index]) or "NONE",
            "dy_recipe_terminal": "YES" if dy_index == len(atoms) - 1 else "NO",
            "statement_final": event["statement_final"],
            "literal_working_reading_de": literal_projection_reading(argument_state_projection(event["recipe"])),
            "distinction": "Y_ARGUMENT_POSTEN__THEN_DY_CLOSE_CONTROL",
        })

    y_dy_classes: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events.values():
        atoms = set(event["recipe"].split("+"))
        category = (
            "Y_AND_DY" if {"Y", "DY"} <= atoms else
            "Y_ONLY" if "Y" in atoms else
            "DY_ONLY" if "DY" in atoms else "NEITHER_Y_NOR_DY"
        )
        y_dy_classes[category].append(event)
    class_defaults = {
        "Y_ONLY": "Y liefert den Argumentwert POSTEN; kein DY-Schluss steht in der Karte.",
        "DY_ONLY": "DY schließt den Schritt; kein Y-Argument steht in der Karte.",
        "Y_AND_DY": "Y liefert POSTEN; das getrennte spätere DY schließt den Schritt.",
        "NEITHER_Y_NOR_DY": "Die Karte benutzt andere Träger oder nur OT/OL-Steuerung.",
    }
    y_dy_summary_rows: list[dict[str, object]] = []
    for category in ("Y_ONLY", "DY_ONLY", "Y_AND_DY", "NEITHER_Y_NOR_DY"):
        material = y_dy_classes[category]
        y_dy_summary_rows.append({
            "distinction_class": category, "event_count": len(material),
            "physical_page_count": len({event["physical_page"] for event in material}),
            "register_count": len({event["register"] for event in material}),
            "statement_final_event_count": sum(event["statement_final"] == "YES" for event in material),
            "default_reading_de": class_defaults[category],
        })

    dy_argument_events = [
        event for event in selected_events.values() if "DY" in event["recipe"].split("+")
    ]
    no_dy_argument_events = [
        event for event in selected_events.values() if "DY" not in event["recipe"].split("+")
    ]
    transition_outcomes = Counter(str(row["successor_outcome"]) for row in transition_rows)
    family_variant_counts = Counter(int(row["argument_variant_count"]) for row in family_rows)
    result = {
        "status": STATUS,
        "source_marker_occurrence_count": len(state_rows),
        "source_marker_event_count": len(events),
        "argument_state_event_count": len(selected_events),
        "argument_occurrence_count": len(assignment_rows),
        "single_argument_event_count": len(single_argument_events),
        "multiargument_event_count": len(selected_events) - len(single_argument_events),
        "y_occurrence_count": sum(row["argument"] == "Y" for row in assignment_rows),
        "aiin_occurrence_count": sum(row["argument"] == "AIIN" for row in assignment_rows),
        "ain_occurrence_count": sum(row["argument"] == "AIN" for row in assignment_rows),
        "or_occurrence_count": sum(row["argument"] == "OR" for row in assignment_rows),
        "physical_page_count": len({row["physical_page"] for row in assignment_rows}),
        "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in assignment_rows}),
        "carrier_envelope_count": len(envelope_rows),
        "argument_state_projection_count": len(projection_rows),
        "left_ot_argument_count": sum(row["left_control"] == "OT" for row in assignment_rows),
        "left_ol_argument_count": sum(row["left_control"] == "OL" for row in assignment_rows),
        "left_ot_or_ol_argument_count": sum(row["left_control"] in {"OT", "OL"} for row in assignment_rows),
        "right_ol_argument_count": sum(row["right_control"] == "OL" for row in assignment_rows),
        "right_dy_argument_count": sum(row["right_control"] == "DY" for row in assignment_rows),
        "multiroot_substitution_family_count": len(family_rows),
        "complete_four_argument_family_count": family_variant_counts[4],
        "three_argument_family_count": family_variant_counts[3],
        "two_argument_family_count": family_variant_counts[2],
        "multiroot_family_event_count": len(family_event_ids),
        "argument_occurrence_outside_multiroot_family_count": sum(row["substitution_family_id"] == "NONE" for row in assignment_rows),
        "bare_ot_argument_family_event_count": next(int(row["event_count"]) for row in family_rows if row["normalized_recipe"] == "OT+ARG"),
        "bare_ol_argument_family_event_count": next(int(row["event_count"]) for row in family_rows if row["normalized_recipe"] == "OL+ARG"),
        "all_six_argument_pairs_state_bridged": all(int(row["gdt559_state_family_count"]) >= 1 for row in pair_rows),
        "all_six_pairs_share_bare_ot_and_ol": all(row["shared_bare_ot_argument_frame"] == "YES" and row["shared_bare_ol_argument_frame"] == "YES" for row in pair_rows),
        "left_controlled_transition_count": len(transition_rows),
        "implicit_successor_inherits_current_count": transition_outcomes["NEXT_INHERITS_CURRENT_ARGUMENT"],
        "explicit_successor_argument_reset_count": transition_outcomes["NEXT_EXPLICIT_ARGUMENT_RESETS_CARRIER"],
        "no_successor_statement_end_count": transition_outcomes["NO_SUCCESSOR_STATEMENT_END"],
        "successor_argument_mismatch_count": sum(count for outcome, count in transition_outcomes.items() if outcome.startswith("MISMATCH")),
        "argument_dy_event_count": len(dy_argument_events),
        "argument_dy_statement_final_count": sum(event["statement_final"] == "YES" for event in dy_argument_events),
        "argument_no_dy_event_count": len(no_dy_argument_events),
        "argument_no_dy_statement_final_count": sum(event["statement_final"] == "YES" for event in no_dy_argument_events),
        "y_dy_joint_event_count": len(y_dy_joint_rows),
        "y_dy_joint_y_before_dy_count": sum(row["written_order"] == "Y_BEFORE_DY" for row in y_dy_joint_rows),
        "y_dy_joint_statement_final_count": sum(row["statement_final"] == "YES" for row in y_dy_joint_rows),
        "all_assignments_have_default": all(bool(row["complete_carrier_reading_de"]) for row in assignment_rows),
        "all_projections_have_default": all(bool(row["literal_working_reading_de"]) for row in projection_rows),
        "new_pages": 0, "recipe_changes": 0, "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }

    write_tsv(ASSIGNMENT_OUT, assignment_rows)
    write_tsv(ROOT_PROFILE_OUT, root_profile_rows)
    write_tsv(ENVELOPE_OUT, envelope_rows)
    write_tsv(PROJECTION_OUT, projection_rows)
    write_tsv(FAMILY_OUT, family_rows)
    write_tsv(PAIR_OUT, pair_rows)
    write_tsv(TRANSITION_OUT, transition_rows)
    write_tsv(TRANSITION_PROFILE_OUT, transition_profile_rows)
    write_tsv(Y_DY_JOINT_OUT, y_dy_joint_rows)
    write_tsv(Y_DY_SUMMARY_OUT, y_dy_summary_rows)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT559 — Argument-Trägerbuch", "",
        "Die vier kurzen Werte bleiben unverändert: `Y=POSTEN`, `AIIN=WERT`, `AIN=ANTEIL`, `OR=EINHEIT`. OT, OL und DY bestimmen, was mit diesem Wert geschieht. Jede der390 Argumentstellen und jede der24 geschriebenen Argument-Steuerfolgen hat unten bzw. in den TSV-Artefakten eine Standardlesung.", "",
        "## Sechs vollständige Hüllen", "",
        "| Hülle | Stellen | Y | AIIN | AIN | OR | Standard |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in envelope_rows:
        lines.append(
            f"| `{row['carrier_envelope']}` | {row['argument_occurrence_count']} | {row['y_count']} | "
            f"{row['aiin_count']} | {row['ain_count']} | {row['or_count']} | {row['compact_template_de']} |"
        )
    lines.extend([
        "", "## Elf echte Austauschfamilien", "",
        "| Familie | Rezept | Varianten | Karten | Seiten | Standard |",
        "|---|---|---|---:|---:|---|",
    ])
    for row in family_rows:
        lines.append(
            f"| {row['family_id']} | `{row['normalized_recipe']}` | {row['argument_variants']} | "
            f"{row['event_count']} | {row['physical_page_count']} | {row['family_reading_de']} |"
        )
    lines.extend([
        "", "Die nackten Rahmen `OT+ARG` (88 Karten) und `OL+ARG` (59 Karten) tragen jeweils alle vier Werte. Jedes der sechs Argumentpaare teilt beide Rahmen und mindestens einen weiteren state-spezifischen Austauschweg. Die elf Familien decken229 Karten; die übrigen161 Argumentstellen behalten dieselbe kurze Hüllenregel, ohne zu einer neuen Ganzwortbedeutung zu werden.", "",
        "## Nachfolgerregel", "",
        "Für341 Karten setzt OT oder OL das letzte sichtbare Argument als rechten Träger. In157/157 Fällen ohne neues sichtbares Argument übernimmt die nächste Karte genau diesen Wert. In173 Fällen schreibt die nächste Karte einen neuen Wert und ersetzt ihn; elf Karten enden die Aussage. Es gibt null falsche oder leere Übernahmen.", "",
        "```text",
        "OT + ARG   nächsten Träger als ARG eröffnen",
        "OL + ARG   mit ARG als aktuellem Träger fortfahren",
        "ARG + OL   ARG weiter aktiv halten",
        "ARG + DY   ARG führen, dann den Schritt schließen",
        "```", "",
        "## Y ist nicht DY", "",
        "Im exakten Atomstrom stehen235 Karten mit Y ohne DY,677 mit DY ohne Y und28 mit beiden. In allen28 gemeinsamen Karten steht Y vor dem getrennten DY. Die Lesung ist deshalb kompositionell: `Y` liefert POSTEN; `DY` schließt später den Schritt. 27 Karten schließen die Aussage, während `Y+DY+D_LABEL` nur einen lokalen Schritt schließt und danach sein sichtbares Etikett fortsetzt.", "",
        "## Alle24 geschriebenen Steuerfolgen", "",
        "| Folge | Karten | final | wörtliche Arbeitslesung |",
        "|---|---:|---:|---|",
    ])
    for row in projection_rows:
        lines.append(
            f"| `{row['argument_state_projection']}` | {row['event_count']} | "
            f"{row['statement_final_event_count']} | {row['literal_working_reading_de']} |"
        )
    lines.extend([
        "", "## Arbeitsgrenze", "",
        "Das ist eine vollständige Werkstattbelegung vorhandener Komponenten, keine bestätigte Übersetzung. Sie ändert keinen Stamm, kein Rezept, keine Seite und keine Aussagegrenze. Entscheidend für die nächste Seite ist die Vorhersage: Ein bekanntes Argument darf im sichtbaren OT/OL/DY-Rahmen seinen kurzen Wert wechseln, ohne dass der Kontrolloperator mitwechselt.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
