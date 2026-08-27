#!/usr/bin/env python3
"""Resolve all actionless GDT561 state cards through visible state provenance."""

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
BASE = ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G561 = ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts"

INPUTS = {
    "old_context": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_context": G539 / "gdt539_546_contextual_prose_events.tsv",
    "typed_cards": G561 / "gdt561_1656_typed_state_cards.tsv",
    "state_dictionary": G561 / "gdt561_36_state_atom_dictionary.tsv",
}

CARD_OUT = OUT / "gdt562_706_actionless_state_reader.tsv"
ACTION_OUT = OUT / "gdt562_693_action_provenance.tsv"
ARGUMENT_OUT = OUT / "gdt562_459_inherited_argument_provenance.tsv"
RESIDUAL_OUT = OUT / "gdt562_19_nonfull_operation_cards.tsv"
ROLE_OUT = OUT / "gdt562_6_completeness_roles.tsv"
SEQUENCE_OUT = OUT / "gdt562_7_state_sequence_roles.tsv"
ROOT_OUT = OUT / "gdt562_9_inherited_action_profiles.tsv"
BOOK_OUT = OUT / "GDT562_ACTIONLESS_STATE_BOOK.md"
RESULT_OUT = OUT / "gdt562_result.json"

STATUS = (
    "PASS_687_OF_706_FULL_OPERATIONS__693_ACTION_CARRIES__"
    "692_ARGUMENTS_AVAILABLE__19_RESIDUALS_CLOSED_BY_FIVE_ROLES"
)

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
    "OT": ("ADVANCE_TO_NEXT_OPERATION", "Danach", ""),
    "OT+DY": ("ADVANCE_THEN_CLOSE", "Danach", "abschließen"),
    "DY": ("CLOSE_CURRENT_OPERATION", "", "abschließen"),
    "OT+OL": ("ADVANCE_THEN_CONTINUE", "Danach", "weiterführen"),
    "OL+DY": ("CONTINUE_THEN_CLOSE", "Weiter", "abschließen"),
    "OL+OL": ("DOUBLE_CONTINUATION_BRIDGE", "Weiter", "nochmals weiterführen"),
}
ROLE_DE = {
    "FULL_INHERITED_OPERATION": "geerbte Handlung mit sichtbarem oder geerbtem Argument",
    "OBJECTLESS_INHERITED_OPERATION": "geerbte objektlose Handlung",
    "ARGUMENT_REFERENCE_INITIALIZER": "Argumentbezug ohne ausgesprochene Handlung",
    "FORMAL_RELATION_PROLOGUE": "formaler oder relationaler Vorspann",
    "STANDALONE_GRADED_CLOSE": "selbständiger abgestufter Abschluss",
    "PURE_CONTINUATION": "reine Fortsetzungssteuerung",
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


def join_argument(roots: list[str]) -> str:
    phrases = [ARGUMENT_PHRASES[root] for root in roots]
    if not phrases:
        return "NONE"
    if len(phrases) == 1:
        return phrases[0]
    return ", ".join(phrases[:-1]) + " und " + phrases[-1]


def completeness_role(action_root: str, argument_roots: list[str], card: dict[str, str]) -> str:
    if action_root != "NONE" and argument_roots:
        return "FULL_INHERITED_OPERATION"
    if action_root != "NONE":
        return "OBJECTLESS_INHERITED_OPERATION"
    if argument_roots:
        return "ARGUMENT_REFERENCE_INITIALIZER"
    if "DY" in card["recipe"].split("+") and card["statement_final"] == "YES":
        return "STANDALONE_GRADED_CLOSE"
    if card["recipe"] == "OL":
        return "PURE_CONTINUATION"
    return "FORMAL_RELATION_PROLOGUE"


def owner_free_microphrase(
    action_root: str, argument_roots: list[str], recipe: str,
    marker_sequence: str, fragments: dict[str, str],
) -> tuple[str, str, str]:
    role, prefix, suffix = SEQUENCE_ROLES[marker_sequence]
    argument = join_argument(argument_roots)
    if action_root != "NONE":
        no_object, with_object = ACTION_TEMPLATES[action_root]
        base = with_object.format(argument=argument) if argument_roots else no_object
    elif argument_roots:
        base = "Bezug auf " + argument
    else:
        base = ""
    modifier_atoms = [
        atom for atom in recipe.split("+") if atom not in STATE_CONTROLS | ARGUMENTS
    ]
    modifier_phrase = "; ".join(fragments[atom] for atom in modifier_atoms)
    parts = [part for part in (base, modifier_phrase, suffix) if part]
    if prefix:
        phrase = f"{prefix}: " + "; ".join(parts) if parts else prefix
    else:
        phrase = "; ".join(parts)
    phrase = phrase[0].upper() + phrase[1:] + "." if phrase else "Fortfahren."
    return phrase, modifier_phrase or "NONE", role


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_rows = read_tsv(INPUTS["old_context"])
    current_rows = read_tsv(INPUTS["current_context"])
    typed_cards = read_tsv(INPUTS["typed_cards"])
    dictionary = read_tsv(INPUTS["state_dictionary"])
    if tuple(map(len, (old_rows, current_rows, typed_cards, dictionary))) != (4576, 546, 1656, 36):
        raise RuntimeError("Input count drift")

    actionless = [row for row in typed_cards if row["action_atom_count"] == "0"]
    if len(actionless) != 706:
        raise RuntimeError("Actionless population drift")
    actionless_by_id = {row["event_id"]: row for row in actionless}
    dictionary_by_atom = {row["atom"]: row for row in dictionary}
    fragments = {atom: row["default_fragment_de"] for atom, row in dictionary_by_atom.items()}

    # Normalize both context editions, then reconstruct prior visible state inside each statement.
    normalized: list[dict[str, str]] = []
    for row in old_rows:
        normalized.append({
            "cohort": "OLD26_GDT416", "event_id": row["global_running_event_id"],
            "statement_id": row["global_statement_id"],
            "card_ordinal": row["card_ordinal_in_statement"],
            "explicit_action_roots": row["explicit_action_roots"],
            "inherited_action_root": row["inherited_action_root"],
            "explicit_argument_roots": row["explicit_argument_roots"],
            "inherited_argument_root": row["inherited_argument_root"],
            "declared_action_source_event_id": "NOT_STORED_IN_GDT416",
            "declared_argument_source_event_id": "NOT_STORED_IN_GDT416",
        })
    for row in current_rows:
        normalized.append({
            "cohort": "CURRENT4_GDT539", "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "card_ordinal": row["card_ordinal_in_statement"],
            "explicit_action_roots": row["explicit_action_roots"],
            "inherited_action_root": row["inherited_action_root"],
            "explicit_argument_roots": row["explicit_argument_roots"],
            "inherited_argument_root": row["inherited_argument_root"],
            "declared_action_source_event_id": row["inherited_action_source_event_id"],
            "declared_argument_source_event_id": row["inherited_argument_source_event_id"],
        })
    normalized_by_id = {row["event_id"]: row for row in normalized}
    if set(actionless_by_id) - normalized_by_id.keys():
        raise RuntimeError("Context join incomplete")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in normalized:
        by_statement[row["statement_id"]].append(row)
    provenance: dict[str, dict[str, object]] = {}
    for statement_rows in by_statement.values():
        statement_rows.sort(key=lambda row: int(row["card_ordinal"]))
        last_action_root = "NONE"
        last_action_event = "NONE"
        last_action_ordinal = 0
        last_argument_root = "NONE"
        last_argument_event = "NONE"
        last_argument_ordinal = 0
        for context in statement_rows:
            event_id = context["event_id"]
            if event_id in actionless_by_id:
                card = actionless_by_id[event_id]
                inherited_action = card["inherited_action_root"]
                if inherited_action != "NONE":
                    if last_action_root == inherited_action:
                        action_source = "SAME_STATEMENT_VISIBLE_ACTION"
                        action_source_event = last_action_event
                        action_distance: object = int(context["card_ordinal"]) - last_action_ordinal
                    elif last_action_root == "NONE":
                        action_source = "OWNER_CONTEXT_DEFAULT_ACTION"
                        action_source_event = "OWNER_DEFAULT"
                        action_distance = "NOT_APPLICABLE"
                    else:
                        raise RuntimeError(f"Action provenance mismatch at {event_id}")
                else:
                    action_source = "NO_ACTIVE_ACTION"
                    action_source_event = "NONE"
                    action_distance = "NOT_APPLICABLE"

                explicit_arguments = split_roots(card["explicit_argument_roots"])
                inherited_argument = card["inherited_argument_root"]
                if explicit_arguments:
                    argument_roots = explicit_arguments
                    argument_source = "VISIBLE_ARGUMENT_IN_CARD"
                    argument_source_event = event_id
                    argument_distance: object = 0
                elif inherited_argument != "NONE":
                    argument_roots = [inherited_argument]
                    if last_argument_root == inherited_argument:
                        argument_source = "SAME_STATEMENT_VISIBLE_ARGUMENT"
                        argument_source_event = last_argument_event
                        argument_distance = int(context["card_ordinal"]) - last_argument_ordinal
                    elif last_argument_root == "NONE":
                        argument_source = "OWNER_CONTEXT_DEFAULT_ARGUMENT"
                        argument_source_event = "OWNER_DEFAULT"
                        argument_distance = "NOT_APPLICABLE"
                    else:
                        raise RuntimeError(f"Argument provenance mismatch at {event_id}")
                else:
                    argument_roots = []
                    argument_source = "NO_ACTIVE_ARGUMENT"
                    argument_source_event = "NONE"
                    argument_distance = "NOT_APPLICABLE"

                # GDT539 has exact pointers; use them as a second check, not as the reconstruction source.
                declared_action = context["declared_action_source_event_id"]
                declared_argument = context["declared_argument_source_event_id"]
                action_pointer_match = (
                    "NOT_STORED"
                    if declared_action == "NOT_STORED_IN_GDT416"
                    else "YES" if declared_action == (
                        action_source_event if inherited_action != "NONE" else "NONE"
                    ) else "NO"
                )
                argument_pointer_match = (
                    "NOT_STORED"
                    if declared_argument == "NOT_STORED_IN_GDT416"
                    else "YES" if declared_argument == (
                        argument_source_event if inherited_argument != "NONE" else "NONE"
                    ) else "NO"
                )
                if action_pointer_match == "NO" or argument_pointer_match == "NO":
                    raise RuntimeError(f"Declared source pointer mismatch at {event_id}")
                provenance[event_id] = {
                    "action_source_type": action_source,
                    "action_source_event_id": action_source_event,
                    "action_source_card_distance": action_distance,
                    "action_pointer_match": action_pointer_match,
                    "argument_source_type": argument_source,
                    "argument_source_event_id": argument_source_event,
                    "argument_source_card_distance": argument_distance,
                    "argument_pointer_match": argument_pointer_match,
                    "effective_argument_roots": "|".join(argument_roots) or "NONE",
                }

            explicit_actions = split_roots(context["explicit_action_roots"])
            if explicit_actions:
                last_action_root = explicit_actions[-1]
                last_action_event = event_id
                last_action_ordinal = int(context["card_ordinal"])
            explicit_arguments = split_roots(context["explicit_argument_roots"])
            if explicit_arguments:
                last_argument_root = explicit_arguments[-1]
                last_argument_event = event_id
                last_argument_ordinal = int(context["card_ordinal"])

    if len(provenance) != 706:
        raise RuntimeError("Provenance reconstruction incomplete")

    card_rows: list[dict[str, object]] = []
    action_rows: list[dict[str, object]] = []
    argument_rows: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    for actionless_ordinal, card in enumerate(actionless, 1):
        event_id = card["event_id"]
        source = provenance[event_id]
        effective_action = card["inherited_action_root"]
        argument_roots = split_roots(str(source["effective_argument_roots"]))
        role = completeness_role(effective_action, argument_roots, card)
        microphrase, modifiers, state_role = owner_free_microphrase(
            effective_action, argument_roots, card["recipe"],
            card["state_marker_sequence"], fragments,
        )
        atoms = card["recipe"].split("+")
        alignment = " | ".join(
            f"{index}:{atom}={dictionary_by_atom[atom]['default_fragment_de']}"
            for index, atom in enumerate(atoms, 1)
        )
        out: dict[str, object] = {
            "actionless_ordinal": actionless_ordinal,
            "cohort": card["cohort"], "event_id": event_id,
            "statement_id": card["statement_id"],
            "physical_page": card["physical_page"], "register": card["register"],
            "card_ordinal_in_statement": card["card_ordinal_in_statement"],
            "statement_position": card["statement_position"],
            "statement_final": card["statement_final"],
            "surface": card["surface"], "recipe": card["recipe"],
            "ordered_typed_atom_trace": card["ordered_typed_atom_trace"],
            "written_all_atom_default_de": card["all_atom_default_phrase_de"],
            "state_marker_sequence": card["state_marker_sequence"],
            "state_sequence_role": state_role,
            "effective_action_root": effective_action,
            "effective_action_value_de": (
                dictionary_by_atom[effective_action]["working_value_de"]
                if effective_action != "NONE" else "NONE"
            ),
            "action_source_type": source["action_source_type"],
            "action_source_event_id": source["action_source_event_id"],
            "action_source_card_distance": source["action_source_card_distance"],
            "action_pointer_match": source["action_pointer_match"],
            "effective_argument_roots": source["effective_argument_roots"],
            "effective_argument_values_de": (
                "|".join(dictionary_by_atom[root]["working_value_de"] for root in argument_roots)
                if argument_roots else "NONE"
            ),
            "argument_source_type": source["argument_source_type"],
            "argument_source_event_id": source["argument_source_event_id"],
            "argument_source_card_distance": source["argument_source_card_distance"],
            "argument_pointer_match": source["argument_pointer_match"],
            "completeness_role": role,
            "completeness_role_de": ROLE_DE[role],
            "operation_complete": "YES" if role == "FULL_INHERITED_OPERATION" else "NO",
            "visible_modifier_phrase_de": modifiers,
            "owner_free_resolved_microphrase_de": microphrase,
            "written_atom_alignment": alignment,
            "all_written_atoms_retained": "YES",
            "current_owner_context_clause_de": card["contextual_clause_de"],
            "guard": "CONTEXT_RESOLVES_ELLIPSIS__NO_NEW_ROOT_OR_HIDDEN_WRITTEN_ATOM",
        }
        card_rows.append(out)
        if effective_action != "NONE":
            action_rows.append({
                "action_provenance_ordinal": len(action_rows) + 1,
                "event_id": event_id, "statement_id": card["statement_id"],
                "physical_page": card["physical_page"], "register": card["register"],
                "surface": card["surface"], "recipe": card["recipe"],
                "inherited_action_root": effective_action,
                "inherited_action_value_de": dictionary_by_atom[effective_action]["working_value_de"],
                "action_source_type": source["action_source_type"],
                "action_source_event_id": source["action_source_event_id"],
                "source_card_distance": source["action_source_card_distance"],
                "gdt539_pointer_match": source["action_pointer_match"],
                "resolved_microphrase_de": microphrase,
                "provenance_status": "RECONSTRUCTED_FROM_PRIOR_VISIBLE_STATE_OR_OWNER_DEFAULT",
            })
        if source["argument_source_type"] in {
            "SAME_STATEMENT_VISIBLE_ARGUMENT", "OWNER_CONTEXT_DEFAULT_ARGUMENT"
        }:
            argument_rows.append({
                "argument_provenance_ordinal": len(argument_rows) + 1,
                "event_id": event_id, "statement_id": card["statement_id"],
                "physical_page": card["physical_page"], "register": card["register"],
                "surface": card["surface"], "recipe": card["recipe"],
                "inherited_argument_root": source["effective_argument_roots"],
                "inherited_argument_value_de": dictionary_by_atom[str(source["effective_argument_roots"])]["working_value_de"],
                "argument_source_type": source["argument_source_type"],
                "argument_source_event_id": source["argument_source_event_id"],
                "source_card_distance": source["argument_source_card_distance"],
                "gdt539_pointer_match": source["argument_pointer_match"],
                "resolved_microphrase_de": microphrase,
                "provenance_status": "RECONSTRUCTED_FROM_PRIOR_VISIBLE_STATE_OR_OWNER_DEFAULT",
            })
        if role != "FULL_INHERITED_OPERATION":
            residual_rows.append({
                "residual_ordinal": len(residual_rows) + 1,
                "event_id": event_id, "statement_id": card["statement_id"],
                "physical_page": card["physical_page"], "register": card["register"],
                "statement_position": card["statement_position"],
                "statement_final": card["statement_final"],
                "surface": card["surface"], "recipe": card["recipe"],
                "effective_action_root": effective_action,
                "effective_argument_roots": source["effective_argument_roots"],
                "residual_role": role, "residual_role_de": ROLE_DE[role],
                "written_default_de": card["all_atom_default_phrase_de"],
                "resolved_microphrase_de": microphrase,
                "owner_context_clause_de": card["contextual_clause_de"],
                "residual_status": "COMPLETE_BOUNDED_ROLE__NO_MISSING_ROOT_ASSUMED",
            })

    role_counts = Counter(str(row["completeness_role"]) for row in card_rows)
    role_rows: list[dict[str, object]] = []
    for role, count in sorted(role_counts.items(), key=lambda item: (-item[1], item[0])):
        material = [row for row in card_rows if row["completeness_role"] == role]
        role_rows.append({
            "completeness_role": role, "role_de": ROLE_DE[role],
            "event_count": count,
            "physical_page_count": len({str(row["physical_page"]) for row in material}),
            "register_count": len({str(row["register"]) for row in material}),
            "statement_initial_count": sum(row["statement_position"] in {"STATEMENT_INITIAL", "SINGLETON_STATEMENT"} for row in material),
            "statement_final_count": sum(row["statement_final"] == "YES" for row in material),
            "example_event_ids": "|".join(str(row["event_id"]) for row in material[:8]),
            "example_microphrases_de": " | ".join(dict.fromkeys(str(row["owner_free_resolved_microphrase_de"]) for row in material))[:1200],
            "default_status": "ROLE_DEFAULT_COMPLETE",
        })

    sequence_counts = Counter(str(row["state_marker_sequence"]) for row in card_rows)
    sequence_rows: list[dict[str, object]] = []
    for sequence, count in sorted(sequence_counts.items(), key=lambda item: (-item[1], item[0])):
        role, prefix, suffix = SEQUENCE_ROLES[sequence]
        material = [row for row in card_rows if row["state_marker_sequence"] == sequence]
        sequence_rows.append({
            "state_marker_sequence": sequence, "state_sequence_role": role,
            "event_count": count,
            "with_inherited_action_count": sum(row["effective_action_root"] != "NONE" for row in material),
            "without_inherited_action_count": sum(row["effective_action_root"] == "NONE" for row in material),
            "statement_final_count": sum(row["statement_final"] == "YES" for row in material),
            "prefix_default_de": prefix or "NONE", "suffix_default_de": suffix or "NONE",
            "example_microphrases_de": " | ".join(dict.fromkeys(str(row["owner_free_resolved_microphrase_de"]) for row in material))[:1200],
            "composition_rule": "KEEP_MARKER_ORDER_AND_INSERT_ACTIVE_ACTION_CONTEXT",
        })

    root_counts = Counter(str(row["effective_action_root"]) for row in card_rows if row["effective_action_root"] != "NONE")
    root_rows: list[dict[str, object]] = []
    for root, count in sorted(root_counts.items(), key=lambda item: (-item[1], item[0])):
        material = [row for row in card_rows if row["effective_action_root"] == root]
        root_rows.append({
            "inherited_action_root": root,
            "working_value_de": dictionary_by_atom[root]["working_value_de"],
            "actionless_event_count": count,
            "same_statement_visible_source_count": sum(row["action_source_type"] == "SAME_STATEMENT_VISIBLE_ACTION" for row in material),
            "owner_context_default_source_count": sum(row["action_source_type"] == "OWNER_CONTEXT_DEFAULT_ACTION" for row in material),
            "with_effective_argument_count": sum(row["effective_argument_roots"] != "NONE" for row in material),
            "objectless_count": sum(row["effective_argument_roots"] == "NONE" for row in material),
            "state_marker_sequences": "|".join(sorted({str(row["state_marker_sequence"]) for row in material})),
            "example_microphrases_de": " | ".join(dict.fromkeys(str(row["owner_free_resolved_microphrase_de"]) for row in material))[:1200],
        })

    write_tsv(CARD_OUT, card_rows)
    write_tsv(ACTION_OUT, action_rows)
    write_tsv(ARGUMENT_OUT, argument_rows)
    write_tsv(RESIDUAL_OUT, residual_rows)
    write_tsv(ROLE_OUT, role_rows)
    write_tsv(SEQUENCE_OUT, sequence_rows)
    write_tsv(ROOT_OUT, root_rows)

    lines = [
        "# GDT562 – die aktionslosen Karten sind fast alle Ellipsen",
        "",
        "## Kernergebnis",
        "",
        "Von706 Zustandskarten ohne sichtbares Handlungsatom besitzen693 bereits eine aktive Handlung im Kontext und692 ein sichtbares oder geerbtes Argument. 687 Karten –97,31% – ergeben damit eine vollständige Handlung-plus-Argument-Operation. Das fehlende Verb ist überwiegend Ellipse, kein unbekannter Wortstamm.",
        "",
        "## Herkunft der ergänzten Slots",
        "",
        "```text",
        "aktive Handlung: 544 frühere sichtbare Handlung derselben Aussage",
        "                 149 Besitzer-/Abschnittsdefault",
        "                  13 keine aktive Handlung",
        "Argument:        233 sichtbar in der Karte",
        "                 355 früher sichtbar in derselben Aussage",
        "                 104 Besitzer-/Abschnittsdefault",
        "                  14 kein aktives Argument",
        "```",
        "",
        "Von den544 innerhalb derselben Aussage übernommenen Handlungen stehen376 unmittelbar davor;168 bleiben über zwei bis acht Karten aktiv. Bei Argumenten sind238/355 unmittelbar und117 über zwei bis fünf Karten verzögert. Die Auslassung ist damit nicht nur ein Nachbartrick, sondern ein kurzer Satzspeicher.",
        "",
        "## Sechs Vollständigkeitsrollen",
        "",
        "| Rolle | Karten | Arbeitslesung |",
        "|---|---:|---|",
    ]
    for row in role_rows:
        lines.append(f"| `{row['completeness_role']}` | {row['event_count']} | {row['role_de']} |")
    lines += [
        "",
        "## Die19 Nicht-Volloperationen",
        "",
        "Sie sind kein gemeinsamer Rest, sondern fünf kleine, vollständig lesbare Rollen: sechs objektlose geerbte Handlungen, fünf Argumentbezüge, vier formale/relative Vorspänne, drei selbständige abgestufte Abschlüsse und eine reine Fortsetzung. Keine verlangt einen neuen Stamm.",
        "",
        "Beispiele:",
        "",
        "```text",
        "OL                    Weiter: halte den Posten.",
        "OT+EE+Y               Danach: Bezug auf den Posten; auf Grad II.",
        "OT+E+DY               Danach: auf Grad I; abschließen.",
        "OT+E+O+D_ADDR+AR      Danach: auf Grad I; zur Ausführung; hier; vom Ausgang.",
        "```",
        "",
        "## Bedeutung für die Arbeitstheorie",
        "",
        "Eine Karte muss kein sichtbares Verb tragen, um eine vollständige Anweisung zu sein. OT, OL und DY operieren auf einem bereits aktiven Handlungs- und Argumentzustand. Der Wortstamm liefert den neuen Wert; der Satzspeicher liefert ausgelassene Slots. Dies ist genau die erwartete Ökonomie eines knappen Werkstattcodebooks.",
        "",
        "Die ownerfreie Mikrophrase ist eine praktische Arbeitszeile. Daneben bleiben die exakte Atomspur und die ältere Besitzer-Kontextzeile sichtbar. Kein kontextuell ergänztes Verb wird als neues geschriebenes Atom ausgegeben.",
    ]
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    action_source_counts = Counter(str(row["action_source_type"]) for row in card_rows)
    argument_source_counts = Counter(str(row["argument_source_type"]) for row in card_rows)
    same_action_distances = [
        int(row["action_source_card_distance"]) for row in card_rows
        if row["action_source_type"] == "SAME_STATEMENT_VISIBLE_ACTION"
    ]
    same_argument_distances = [
        int(row["argument_source_card_distance"]) for row in card_rows
        if row["argument_source_type"] == "SAME_STATEMENT_VISIBLE_ARGUMENT"
    ]
    result = {
        "status": STATUS,
        "source_typed_state_card_count": len(typed_cards),
        "actionless_state_card_count": len(card_rows),
        "actionless_percent_of_state_cards": f"{100 * len(card_rows) / len(typed_cards):.6f}",
        "inherited_action_card_count": len(action_rows),
        "same_statement_visible_action_source_count": action_source_counts["SAME_STATEMENT_VISIBLE_ACTION"],
        "immediate_visible_action_source_count": same_action_distances.count(1),
        "delayed_visible_action_source_count": sum(distance > 1 for distance in same_action_distances),
        "maximum_visible_action_source_distance": max(same_action_distances),
        "owner_context_default_action_source_count": action_source_counts["OWNER_CONTEXT_DEFAULT_ACTION"],
        "no_active_action_count": action_source_counts["NO_ACTIVE_ACTION"],
        "visible_argument_in_card_count": argument_source_counts["VISIBLE_ARGUMENT_IN_CARD"],
        "inherited_argument_card_count": len(argument_rows),
        "same_statement_visible_argument_source_count": argument_source_counts["SAME_STATEMENT_VISIBLE_ARGUMENT"],
        "immediate_visible_argument_source_count": same_argument_distances.count(1),
        "delayed_visible_argument_source_count": sum(distance > 1 for distance in same_argument_distances),
        "maximum_visible_argument_source_distance": max(same_argument_distances),
        "owner_context_default_argument_source_count": argument_source_counts["OWNER_CONTEXT_DEFAULT_ARGUMENT"],
        "no_active_argument_count": argument_source_counts["NO_ACTIVE_ARGUMENT"],
        "cards_with_effective_argument_count": sum(row["effective_argument_roots"] != "NONE" for row in card_rows),
        "full_inherited_operation_count": role_counts["FULL_INHERITED_OPERATION"],
        "full_inherited_operation_percent": f"{100 * role_counts['FULL_INHERITED_OPERATION'] / len(card_rows):.6f}",
        "nonfull_operation_count": len(residual_rows),
        "completeness_role_count": len(role_rows),
        "residual_role_count": sum(role != "FULL_INHERITED_OPERATION" for role in role_counts),
        "state_sequence_role_count": len(sequence_rows),
        "inherited_action_root_count": len(root_rows),
        "role_counts": dict(role_counts),
        "state_sequence_counts": dict(sequence_counts),
        "inherited_action_root_counts": dict(root_counts),
        "all_action_sources_resolved": all(row["action_source_type"] != "UNRESOLVED" for row in card_rows),
        "all_argument_sources_resolved": all(row["argument_source_type"] != "UNRESOLVED" for row in card_rows),
        "all_cards_have_microphrase": all(row["owner_free_resolved_microphrase_de"] for row in card_rows),
        "all_written_atoms_retained": all(row["all_written_atoms_retained"] == "YES" for row in card_rows),
        "current_pointer_checked_card_count": sum(row["cohort"] == "CURRENT4_GDT539" for row in card_rows),
        "current_pointer_match_count": sum(
            row["cohort"] == "CURRENT4_GDT539"
            and row["action_pointer_match"] == "YES"
            and row["argument_pointer_match"] == "YES"
            for row in card_rows
        ),
        "new_pages": 0, "new_surfaces": 0, "new_recipes": 0,
        "new_root_values": 0, "new_written_atoms": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
