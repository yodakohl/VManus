#!/usr/bin/env python3
"""Build the Pass1022 attachment inventory from the current 3,888 cards."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EDITION = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth/"
    "PASS1018_627_REVISED_CORE_EDITION.tsv"
)
EVENTS = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth/"
    "PASS1009_4581_EVENT_LEDGER.tsv"
)
DOUBLING = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_repeated_core_operator_one_thousand_twenty_first/"
    "PASS1021_ADJUDICATED_DOUBLING.tsv"
)

ACTIONS = {
    "OK": "SETZEN",
    "CH": "NEHMEN",
    "SH": "HALTEN",
    "K": "GEBEN",
    "S": "WÄHLEN",
    "T": "EINSTELLEN",
    "CHD": "UMSETZEN",
    "R": "MARKIEREN",
    "P": "EINSETZEN",
}

FOCI = {
    "AIIN": ("WERT", "ARGUMENT"),
    "AIN": ("ANTEIL", "ARGUMENT"),
    "OR": ("EINHEIT", "ARGUMENT"),
    "Y": ("AKTIVER POSTEN", "ARGUMENT"),
    "E": ("GRAD I", "GRADE"),
    "EE": ("GRAD II", "GRADE"),
    "EEE": ("GRAD III", "GRADE"),
    "AL": ("ZIELORT", "RELATION"),
    "AR": ("AUSGANG", "RELATION"),
    "L": ("VERBINDUNG", "RELATION"),
    "AIR": ("LAUF", "RELATION"),
}

ATTACHMENT_FIELDS = [
    "attachment_id",
    "focus_core",
    "focus_value_de",
    "focus_family",
    "event_id",
    "book_event_ordinal",
    "physical_page",
    "register",
    "statement_id",
    "card_ordinal_in_statement",
    "locus",
    "owner_de",
    "surface_card",
    "component_recipe",
    "focus_atom_ordinal",
    "left_atom",
    "right_atom",
    "same_card_left_actions",
    "nearest_left_action",
    "same_card_right_actions",
    "nearest_right_action",
    "previous_card_event_id",
    "previous_card_recipe",
    "previous_card_actions",
    "previous_card_last_action",
    "inherited_action_before_card",
    "inherited_from_event_id",
    "inherited_from_card_ordinal",
    "owner_only_attachment",
    "chosen_attachment_class",
    "chosen_action",
    "chosen_action_value_de",
    "chosen_action_event_id",
    "chosen_action_card_ordinal",
    "chosen_action_atom_ordinal",
    "bracket_reading_de",
    "duplicate_scope_mode",
    "duplicate_scope_role",
    "paired_focus_atom_ordinal",
    "next_card_event_id",
    "next_card_recipe",
    "next_card_actions",
    "ambiguity_codes",
]

AMBIGUITY_FIELDS = [
    "ambiguity_id",
    "attachment_id",
    "ambiguity_class",
    "physical_page",
    "statement_id",
    "event_id",
    "locus",
    "surface_card",
    "component_recipe",
    "focus_core",
    "focus_value_de",
    "chosen_attachment",
    "alternative_attachment",
    "why_open_de",
    "apprentice_rule_choice_de",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def action_marks(atoms: list[str]) -> list[tuple[int, str]]:
    return [(index + 1, atom) for index, atom in enumerate(atoms) if atom in ACTIONS]


def show_actions(actions: list[tuple[int, str]]) -> str:
    return "|".join(f"{atom}@{index}" for index, atom in actions) or "NONE"


def action_label(action: str | None) -> str:
    if not action:
        return "NONE"
    return f"{action}={ACTIONS[action]}"


def bracket_reading(
    focus: str,
    focus_value: str,
    attachment_class: str,
    action: str | None,
    owner: str,
) -> str:
    if attachment_class == "SAME_CARD_LEFT_ACTION":
        return f"{action_label(action)}[{focus}={focus_value}]"
    if attachment_class == "SAME_CARD_RIGHT_ACTION":
        return f"[{focus}={focus_value}]→{action_label(action)}"
    if attachment_class == "PREVIOUS_CARD_ACTION":
        return f"{action_label(action)}⟨VORIGE KARTE⟩[{focus}={focus_value}]"
    if attachment_class == "INHERITED_ACTION":
        return f"{action_label(action)}⟨GEERBT⟩[{focus}={focus_value}]"
    return f"BESITZER={owner}[{focus}={focus_value}]"


def duplicate_roles(
    atoms: list[str],
    focus_index: int,
    focus: str,
    doubling: dict[tuple[str, str], dict[str, str]],
    event_id: str,
) -> tuple[str, str, str]:
    paired_index = None
    if focus_index > 0 and atoms[focus_index - 1] == focus:
        paired_index = focus_index - 1
    elif focus_index + 1 < len(atoms) and atoms[focus_index + 1] == focus:
        paired_index = focus_index + 1
    if paired_index is None:
        return "SINGLE", "SINGLE", "NONE"

    decision = doubling.get((event_id, focus))
    if not decision:
        raise AssertionError(f"missing Pass1021 doubling decision: {event_id} {focus}")
    mode = decision["selected_doubling_rule"]
    first = min(focus_index, paired_index)
    if mode == "PACKAGE_SCOPE_DESCENT":
        role = "PACKAGE_OUTER" if focus_index == first else "PACKAGE_INNER"
    else:
        role = "FREE_PEER_1" if focus_index == first else "FREE_PEER_2"
    return mode, role, str(paired_index + 1)


def main() -> None:
    statements = read_tsv(EDITION)
    all_events = read_tsv(EVENTS)
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in all_events:
        if event["event_role"] == "RUNNING_STATEMENT":
            running_events[event["statement_id"]].append(event)
    for group in running_events.values():
        group.sort(key=lambda row: int(row["book_event_ordinal"]))

    doubling = {
        (row["event_id"], row["core"]): row
        for row in read_tsv(DOUBLING)
        if row["core"] in FOCI
    }

    if len(statements) != 627:
        raise AssertionError(f"expected 627 statements, got {len(statements)}")
    if sum(len(group) for group in running_events.values()) != 3888:
        raise AssertionError("running-card count is not 3,888")

    attachments: list[dict[str, object]] = []
    ambiguity_specs: list[tuple[int, str, str, str, str]] = []
    event_count = 0
    target_event_count = 0

    for statement in statements:
        statement_id = statement["statement_id"]
        cards = statement["component_sequence"].split(" | ")
        surfaces = statement["surface_sequence"].split()
        events = running_events[statement_id]
        if not (len(cards) == len(surfaces) == len(events) == int(statement["event_count"])):
            raise AssertionError(f"card alignment failed for {statement_id}")
        if any(surface != event["surface"] for surface, event in zip(surfaces, events)):
            raise AssertionError(f"surface alignment failed for {statement_id}")

        active: dict[str, object] | None = None
        event_count += len(events)
        for card_index, (recipe, surface, event) in enumerate(zip(cards, surfaces, events)):
            atoms = recipe.split("+")
            current_actions = action_marks(atoms)
            previous_atoms = cards[card_index - 1].split("+") if card_index else []
            previous_actions = action_marks(previous_atoms)
            previous_event = events[card_index - 1] if card_index else None
            next_atoms = cards[card_index + 1].split("+") if card_index + 1 < len(cards) else []
            next_actions = action_marks(next_atoms)
            next_event = events[card_index + 1] if card_index + 1 < len(events) else None
            if any(atom in FOCI for atom in atoms):
                target_event_count += 1

            for atom_index, focus in enumerate(atoms):
                if focus not in FOCI:
                    continue
                focus_position = atom_index + 1
                focus_value, family = FOCI[focus]
                left_actions = [(pos, action) for pos, action in current_actions if pos < focus_position]
                right_actions = [(pos, action) for pos, action in current_actions if pos > focus_position]
                nearest_left = left_actions[-1] if left_actions else None
                nearest_right = right_actions[0] if right_actions else None

                chosen: tuple[int, str] | None = None
                attachment_class: str
                source_event_id = "NONE"
                source_card_ordinal = "NONE"
                source_atom_ordinal = "NONE"

                # L opens forward; all other requested tails/grades first close left.
                if focus == "L":
                    chosen = nearest_right or nearest_left
                else:
                    chosen = nearest_left or nearest_right
                if chosen:
                    attachment_class = (
                        "SAME_CARD_LEFT_ACTION"
                        if chosen[0] < focus_position
                        else "SAME_CARD_RIGHT_ACTION"
                    )
                    source_event_id = event["event_id"]
                    source_card_ordinal = str(card_index + 1)
                    source_atom_ordinal = str(chosen[0])
                    chosen_action = chosen[1]
                elif previous_actions:
                    attachment_class = "PREVIOUS_CARD_ACTION"
                    chosen_action = previous_actions[-1][1]
                    source_event_id = previous_event["event_id"] if previous_event else "NONE"
                    source_card_ordinal = str(card_index)
                    source_atom_ordinal = str(previous_actions[-1][0])
                elif active:
                    attachment_class = "INHERITED_ACTION"
                    chosen_action = str(active["action"])
                    source_event_id = str(active["event_id"])
                    source_card_ordinal = str(active["card_ordinal"])
                    source_atom_ordinal = str(active["atom_ordinal"])
                else:
                    attachment_class = "OWNER_ONLY"
                    chosen_action = None

                duplicate_mode, duplicate_role, paired_atom = duplicate_roles(
                    atoms, atom_index, focus, doubling, event["event_id"]
                )

                ambiguity_codes: list[str] = []
                attachment_number = len(attachments) + 1

                if nearest_left and nearest_right:
                    left_distance = focus_position - nearest_left[0]
                    right_distance = nearest_right[0] - focus_position
                    if left_distance == right_distance:
                        ambiguity_codes.append("EQUAL_DISTANCE_TWO_HEADS")
                        selected = chosen_action
                        alternative_entry = nearest_right if chosen == nearest_left else nearest_left
                        alternative = f"{action_label(alternative_entry[1])}@ATOM{alternative_entry[0]}"
                        direction = "rechts" if focus == "L" else "links"
                        ambiguity_specs.append(
                            (
                                attachment_number,
                                "EQUAL_DISTANCE_TWO_HEADS",
                                alternative,
                                "Zwei Handlungsköpfe stehen gleich nah auf beiden Seiten.",
                                f"{focus} folgt als {'Vorrahmen' if focus == 'L' else 'Nachsatz'} dem Kopf {direction}: {action_label(selected)}@ATOM{chosen[0]}.",
                            )
                        )

                if attachment_class == "OWNER_ONLY" and next_actions:
                    ambiguity_codes.append("OWNER_OR_NEXT_CARD_ACTION")
                    ambiguity_specs.append(
                        (
                            attachment_number,
                            "OWNER_OR_NEXT_CARD_ACTION",
                            f"{action_label(next_actions[0][1])}@NÄCHSTE_KARTE_ATOM{next_actions[0][0]}",
                            "Vor Ort und rückwärts ist kein Handlungskopf offen; die nächste Karte beginnt jedoch einen.",
                            "Nicht vorwärts über die Kartengrenze greifen; vorläufig an den sichtbaren Besitzer binden.",
                        )
                    )

                if chosen_action == "R":
                    local_alternatives = [entry for entry in left_actions + right_actions if entry[1] != "R"]
                    local_alternatives.sort(key=lambda entry: abs(entry[0] - focus_position))
                    alternative_location = "VORAUSGEHENDER_RAHMEN"
                    if attachment_class in {"SAME_CARD_LEFT_ACTION", "SAME_CARD_RIGHT_ACTION"}:
                        if local_alternatives:
                            alternative_action = local_alternatives[0][1]
                            alternative_location = f"ATOM{local_alternatives[0][0]}"
                        elif active and active["action"] != "R":
                            alternative_action = str(active["action"])
                        elif active:
                            alternative_action = active.get("r_alternative")
                        else:
                            alternative_action = None
                    else:
                        alternative_action = active.get("r_alternative") if active else None
                    if alternative_action:
                        ambiguity_codes.append("R_HEAD_OR_TAIL")
                        ambiguity_specs.append(
                            (
                                attachment_number,
                                "R_HEAD_OR_TAIL",
                                f"{action_label(str(alternative_action))}@{alternative_location}",
                                "R kann selbst MARKIEREN eröffnen oder den vorausgehenden Kopf abschließen.",
                                "Steht der Fokus rechts von R, R als Kopf lesen; die Schwanzlesung bleibt als echte Alternative notiert.",
                            )
                        )

                row = {
                    "attachment_id": f"SA{attachment_number:05d}",
                    "focus_core": focus,
                    "focus_value_de": focus_value,
                    "focus_family": family,
                    "event_id": event["event_id"],
                    "book_event_ordinal": event["book_event_ordinal"],
                    "physical_page": statement["physical_page"],
                    "register": statement["register"],
                    "statement_id": statement_id,
                    "card_ordinal_in_statement": card_index + 1,
                    "locus": event["locus"],
                    "owner_de": statement["visible_owner_or_namespace_de"],
                    "surface_card": surface,
                    "component_recipe": recipe,
                    "focus_atom_ordinal": focus_position,
                    "left_atom": atoms[atom_index - 1] if atom_index else "CARD_START",
                    "right_atom": atoms[atom_index + 1] if atom_index + 1 < len(atoms) else "CARD_END",
                    "same_card_left_actions": show_actions(left_actions),
                    "nearest_left_action": action_label(nearest_left[1] if nearest_left else None),
                    "same_card_right_actions": show_actions(right_actions),
                    "nearest_right_action": action_label(nearest_right[1] if nearest_right else None),
                    "previous_card_event_id": previous_event["event_id"] if previous_event else "STATEMENT_START",
                    "previous_card_recipe": cards[card_index - 1] if card_index else "STATEMENT_START",
                    "previous_card_actions": show_actions(previous_actions),
                    "previous_card_last_action": action_label(previous_actions[-1][1] if previous_actions else None),
                    "inherited_action_before_card": action_label(str(active["action"]) if active else None),
                    "inherited_from_event_id": str(active["event_id"]) if active else "NONE",
                    "inherited_from_card_ordinal": str(active["card_ordinal"]) if active else "NONE",
                    "owner_only_attachment": "YES" if attachment_class == "OWNER_ONLY" else "NO",
                    "chosen_attachment_class": attachment_class,
                    "chosen_action": chosen_action or "OWNER",
                    "chosen_action_value_de": ACTIONS[chosen_action] if chosen_action else "BESITZER",
                    "chosen_action_event_id": source_event_id,
                    "chosen_action_card_ordinal": source_card_ordinal,
                    "chosen_action_atom_ordinal": source_atom_ordinal,
                    "bracket_reading_de": bracket_reading(
                        focus, focus_value, attachment_class, chosen_action, statement["visible_owner_or_namespace_de"]
                    ),
                    "duplicate_scope_mode": duplicate_mode,
                    "duplicate_scope_role": duplicate_role,
                    "paired_focus_atom_ordinal": paired_atom,
                    "next_card_event_id": next_event["event_id"] if next_event else "STATEMENT_END",
                    "next_card_recipe": cards[card_index + 1] if card_index + 1 < len(cards) else "STATEMENT_END",
                    "next_card_actions": show_actions(next_actions),
                    "ambiguity_codes": "|".join(ambiguity_codes) or "NONE",
                }
                attachments.append(row)

            if current_actions:
                last_position, last_action = current_actions[-1]
                r_alternative: str | None = None
                if last_action == "R":
                    earlier_local = [action for position, action in current_actions if position < last_position and action != "R"]
                    if earlier_local:
                        r_alternative = earlier_local[-1]
                    elif active and active["action"] != "R":
                        r_alternative = str(active["action"])
                    elif active:
                        inherited_alternative = active.get("r_alternative")
                        r_alternative = str(inherited_alternative) if inherited_alternative else None
                active = {
                    "action": last_action,
                    "event_id": event["event_id"],
                    "card_ordinal": card_index + 1,
                    "atom_ordinal": last_position,
                    "r_alternative": r_alternative,
                }

    if event_count != 3888:
        raise AssertionError(f"aligned event count is {event_count}, expected 3,888")
    if len(attachments) != 4345:
        raise AssertionError(f"attachment count is {len(attachments)}, expected 4,345")

    ambiguities: list[dict[str, object]] = []
    for ambiguity_number, spec in enumerate(ambiguity_specs, start=1):
        attachment_number, ambiguity_class, alternative, why_open, rule_choice = spec
        attachment = attachments[attachment_number - 1]
        ambiguities.append(
            {
                "ambiguity_id": f"SAA{ambiguity_number:04d}",
                "attachment_id": attachment["attachment_id"],
                "ambiguity_class": ambiguity_class,
                "physical_page": attachment["physical_page"],
                "statement_id": attachment["statement_id"],
                "event_id": attachment["event_id"],
                "locus": attachment["locus"],
                "surface_card": attachment["surface_card"],
                "component_recipe": attachment["component_recipe"],
                "focus_core": attachment["focus_core"],
                "focus_value_de": attachment["focus_value_de"],
                "chosen_attachment": attachment["bracket_reading_de"],
                "alternative_attachment": alternative,
                "why_open_de": why_open,
                "apprentice_rule_choice_de": rule_choice,
            }
        )

    summary_rows: list[dict[str, object]] = []
    summary_fields = [
        "focus_core",
        "focus_value_de",
        "focus_family",
        "occurrences",
        "event_count",
        "statement_count",
        "same_card_left_action",
        "same_card_right_action",
        "previous_card_action",
        "inherited_action",
        "owner_only",
        "equal_distance_two_heads",
        "owner_or_next_card_action",
        "r_head_or_tail",
        "duplicate_scope_atoms",
    ]
    for focus in FOCI:
        selected = [row for row in attachments if row["focus_core"] == focus]
        classes = Counter(str(row["chosen_attachment_class"]) for row in selected)
        codes = Counter(
            code
            for row in selected
            for code in str(row["ambiguity_codes"]).split("|")
            if code != "NONE"
        )
        summary_rows.append(
            {
                "focus_core": focus,
                "focus_value_de": FOCI[focus][0],
                "focus_family": FOCI[focus][1],
                "occurrences": len(selected),
                "event_count": len({str(row["event_id"]) for row in selected}),
                "statement_count": len({str(row["statement_id"]) for row in selected}),
                "same_card_left_action": classes["SAME_CARD_LEFT_ACTION"],
                "same_card_right_action": classes["SAME_CARD_RIGHT_ACTION"],
                "previous_card_action": classes["PREVIOUS_CARD_ACTION"],
                "inherited_action": classes["INHERITED_ACTION"],
                "owner_only": classes["OWNER_ONLY"],
                "equal_distance_two_heads": codes["EQUAL_DISTANCE_TWO_HEADS"],
                "owner_or_next_card_action": codes["OWNER_OR_NEXT_CARD_ACTION"],
                "r_head_or_tail": codes["R_HEAD_OR_TAIL"],
                "duplicate_scope_atoms": sum(row["duplicate_scope_mode"] != "SINGLE" for row in selected),
            }
        )

    attachment_classes = Counter(str(row["chosen_attachment_class"]) for row in attachments)
    ambiguity_classes = Counter(str(row["ambiguity_class"]) for row in ambiguities)
    summary = {
        "statement_count": len(statements),
        "running_event_count": event_count,
        "running_events_with_requested_focus": target_event_count,
        "attachment_occurrence_count": len(attachments),
        "attachment_class_counts": dict(sorted(attachment_classes.items())),
        "ambiguity_row_count": len(ambiguities),
        "ambiguous_attachment_count": len({str(row["attachment_id"]) for row in ambiguities}),
        "ambiguity_class_counts": dict(sorted(ambiguity_classes.items())),
        "package_scope_atom_count": sum(row["duplicate_scope_mode"] == "PACKAGE_SCOPE_DESCENT" for row in attachments),
        "free_duplicate_atom_count": sum(row["duplicate_scope_mode"] == "FREE_PLURAL_OR_REPEAT" for row in attachments),
        "checks": {
            "statement_card_surface_alignment": "PASS",
            "all_requested_focus_occurrences_inventory": "PASS",
            "statement_boundary_resets_stack": "PASS",
            "future_card_excluded_from_attachment_choice": "PASS",
            "pass1021_duplicate_scope_carried_forward": "PASS",
        },
    }

    write_tsv(OUT / "SCOPE_STACK_ATTACHMENTS.tsv", attachments, ATTACHMENT_FIELDS)
    write_tsv(OUT / "SCOPE_STACK_AMBIGUITIES.tsv", ambiguities, AMBIGUITY_FIELDS)
    write_tsv(OUT / "SCOPE_STACK_SUMMARY.tsv", summary_rows, summary_fields)
    with (OUT / "SCOPE_STACK_SUMMARY.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
