#!/usr/bin/env python3
"""Build the Pass-1022 owner/action/argument scope edition.

This is a creative sidequest compiler, not a decipherment claim.  It keeps the
Pass-1018 component values fixed and asks only which running action receives
each short argument, relation, grade, or sequence marker.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1009_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth/PASS1009_627_STATEMENT_EDITION.tsv"
P1009_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth/PASS1009_4581_EVENT_LEDGER.tsv"
P1018 = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth/PASS1018_627_REVISED_CORE_EDITION.tsv"
P1020 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_sheet_roundtrip_one_thousand_twentieth/PASS1020_31_CATEGORY_LEXICON.tsv"
P1021 = ROOT / "experiments/yolo/sidequest_semantic_repeated_core_operator_one_thousand_twenty_first/PASS1021_ADJUDICATED_DOUBLING.tsv"

ACTION = {
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
ARGUMENT = {"Y": "AKTIVER POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
RELATION = {"AR": "AUSGANG", "AL": "ZIELORT", "L": "VERBINDUNG", "AIR": "LAUF"}
GRADE = {"E": "GRAD I", "EE": "GRAD II", "EEE": "GRAD III", "IIN": "STUFE", "DA": "ZWEITE STUFE", "O": "AUSFÜHRUNG"}
SEQUENCE = {"OL": "FORTSETZEN", "OT": "DANACH"}
BOUNDARY = {"CARRIER_Q": "BEGINNMARKER", "DY": "SCHLUSS"}

PREDICATE_FALLBACK = {
    "SETZEN": "SETZEN",
    "UMSETZEN": "UMSETZEN",
    "ABSETZEN": "HALTEN",
    "HALTEN": "HALTEN",
    "AUSFÜHREN": "LOKALE HANDLUNG",
    "GEBEN": "GEBEN",
    "AUSWÄHLEN": "WÄHLEN",
    "STELLEN": "EINSTELLEN",
    "NEHMEN": "NEHMEN",
    "BEHANDELN": "UMSETZEN",
    "LEITEN": "FORTSETZEN",
    "SPÜLEN": "LOKALE HANDLUNG",
    "UMLEITEN": "UMSETZEN",
    "MERKEN": "MARKIEREN",
    "EINSETZEN": "EINSETZEN",
    "TRENNEN": "NEHMEN",
    "BEGINNEN": "EINSETZEN",
    "AUFFANGEN": "GEBEN",
    "FORTSETZEN": "FORTSETZEN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_cards(value: str) -> list[str]:
    return value.split(" ") if value else []


def split_recipes(value: str) -> list[str]:
    return value.split(" | ") if value else []


def first_right_action(atoms: list[str], position: int) -> int | None:
    return next((i for i in range(position + 1, len(atoms)) if atoms[i] in ACTION), None)


def last_left_action(atoms: list[str], position: int) -> int | None:
    return next((i for i in range(position - 1, -1, -1) if atoms[i] in ACTION), None)


def nearest_action(atoms: list[str], position: int) -> int | None:
    choices = [i for i, atom in enumerate(atoms) if atom in ACTION]
    if not choices:
        return None
    # Equal distance prefers the action already read on the left.
    return min(choices, key=lambda i: (abs(i - position), 0 if i < position else 1, i))


def action_ref(event_id: str, atom_pos: int, atom: str) -> str:
    return f"{event_id}:A{atom_pos + 1}:{ACTION[atom]}"


def target_value(ref: str) -> str:
    return ref.rsplit(":", 1)[-1] if ref else ""


def last_statement_head(statement: dict[str, str], legacy: dict[str, str]) -> str:
    atoms = [atom for recipe in split_recipes(statement["component_sequence"]) for atom in recipe.split("+")]
    actions = [ACTION[atom] for atom in atoms if atom in ACTION]
    if actions:
        return actions[-1]
    if "OL" in atoms:
        return "FORTSETZEN"
    return PREDICATE_FALLBACK.get(legacy["predicate_operation_de"], "LOKALE HANDLUNG")


def main() -> None:
    old_statements = {row["statement_id"]: row for row in read_tsv(P1009_STATEMENTS)}
    current_statements = read_tsv(P1018)
    event_meta = {row["event_id"]: row for row in read_tsv(P1009_EVENTS)}
    categories = read_tsv(P1020)
    duplicates = {row["event_id"]: row for row in read_tsv(P1021)}

    sign_category: dict[str, tuple[str, str]] = {}
    for row in categories:
        for sign in row["graphic_signs"].split("|"):
            sign_category[sign] = (row["category_id"], row["short_value_de"])

    if len(current_statements) != 627 or set(old_statements) != {row["statement_id"] for row in current_statements}:
        raise SystemExit("statement inventory mismatch")

    current_by_id = {row["statement_id"]: row for row in current_statements}
    source_head = {sid: last_statement_head(row, old_statements[sid]) for sid, row in current_by_id.items()}

    event_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    binding_origin_counts: Counter[str] = Counter()
    atom_counts: Counter[str] = Counter()
    ordinal = 0

    for statement in current_statements:
        sid = statement["statement_id"]
        legacy = old_statements[sid]
        surfaces = split_cards(statement["surface_sequence"])
        recipes = split_recipes(statement["component_sequence"])
        event_ids = legacy["event_ids"].split("|")
        if not (len(surfaces) == len(recipes) == len(event_ids) == int(statement["event_count"])):
            raise SystemExit(f"card alignment mismatch: {sid}")

        inherited_source = legacy["inheritance_source_statement_id"]
        inherited_ref = ""
        if "INHERITANCE" in legacy["predicate_realization"]:
            inherited_value = source_head.get(inherited_source, PREDICATE_FALLBACK.get(legacy["inherited_operation_de"], "LOKALE HANDLUNG"))
            inherited_ref = f"SOURCE:{inherited_source}:{inherited_value}"

        active = inherited_ref
        pending: list[dict[str, object]] = []
        statement_bindings: list[dict[str, object]] = []
        statement_actions: list[str] = []
        statement_values: Counter[str] = Counter()
        statement_origins: Counter[str] = Counter()
        statement_unbound = 0

        for card_index, (surface, recipe, event_id) in enumerate(zip(surfaces, recipes, event_ids), 1):
            meta = event_meta[event_id]
            if meta["statement_id"] != sid or meta["surface"] != surface:
                raise SystemExit(f"event alignment mismatch: {sid}/{event_id}")
            atoms = recipe.split("+")
            atom_counts.update(atoms)
            active_before = active
            # Q opens a fresh local package.  It retains the visible owner but
            # not the preceding package's action head.
            if "CARRIER_Q" in atoms:
                active_before = ""
                active = ""
            actions_here = {i: action_ref(event_id, i, atom) for i, atom in enumerate(atoms) if atom in ACTION}
            action_values_here = [ACTION[atom] for atom in atoms if atom in ACTION]
            statement_actions.extend(action_values_here)

            if actions_here and pending:
                first_ref = actions_here[min(actions_here)]
                for item in pending:
                    item["target"] = first_ref
                    item["origin"] = "FORWARD_TO_NEXT_ACTION"
                    binding_origin_counts["FORWARD_TO_NEXT_ACTION"] += 1
                    statement_origins["FORWARD_TO_NEXT_ACTION"] += 1
                pending.clear()

            card_bindings: list[dict[str, object]] = []
            card_values: dict[str, list[str]] = {"ARGUMENT": [], "RELATION": [], "GRADE": [], "SEQUENCE": [], "LOCAL": []}
            for atom_pos, atom in enumerate(atoms):
                category_id, short_value = sign_category[atom]
                target = ""
                origin = ""
                role = ""

                if atom in ACTION:
                    target = actions_here[atom_pos]
                    origin = "ACTION_HEAD"
                    role = "ACTION"
                    active = target
                elif atom in ARGUMENT:
                    role = "ARGUMENT"
                    idx = nearest_action(atoms, atom_pos)
                    if idx is not None:
                        target, origin = actions_here[idx], "SAME_CARD_NEAREST"
                    elif active_before:
                        target, origin = active_before, "RUNNING_ACTION"
                    card_values[role].append(ARGUMENT[atom])
                elif atom in RELATION:
                    role = "RELATION"
                    if atom in {"AR", "AL"}:
                        idx = last_left_action(atoms, atom_pos)
                        if idx is not None:
                            target, origin = actions_here[idx], "SAME_CARD_LEFT"
                        elif active_before:
                            target, origin = active_before, "RUNNING_ACTION"
                        else:
                            idx = first_right_action(atoms, atom_pos)
                            if idx is not None:
                                target, origin = actions_here[idx], "SAME_CARD_RIGHT_FALLBACK"
                    else:
                        idx = first_right_action(atoms, atom_pos)
                        if idx is not None:
                            target, origin = actions_here[idx], "SAME_CARD_RIGHT_FRAME"
                        else:
                            idx = last_left_action(atoms, atom_pos)
                            if idx is not None:
                                target, origin = actions_here[idx], "SAME_CARD_LEFT_FALLBACK"
                            elif active_before:
                                target, origin = active_before, "RUNNING_ACTION"
                    card_values[role].append(RELATION[atom])
                elif atom in GRADE:
                    role = "GRADE"
                    idx = nearest_action(atoms, atom_pos)
                    if idx is not None:
                        target, origin = actions_here[idx], "SAME_CARD_NEAREST"
                    elif active_before:
                        target, origin = active_before, "RUNNING_ACTION"
                    card_values[role].append(GRADE[atom])
                elif atom in SEQUENCE:
                    role = "SEQUENCE"
                    idx = first_right_action(atoms, atom_pos)
                    if idx is not None:
                        target, origin = actions_here[idx], "SAME_CARD_NEXT_STEP"
                    elif active_before:
                        target, origin = active_before, "RUNNING_ACTION"
                    card_values[role].append(SEQUENCE[atom])
                elif atom == "CARRIER_Q":
                    role, target, origin = "BOUNDARY", "GANG:NEW", "GANG_BOUNDARY"
                elif atom == "DY":
                    role, target, origin = "BOUNDARY", active or active_before or "GANG", "GANG_CLOSE"
                else:
                    role, target, origin = "LOCAL", f"OWNER:{statement['visible_owner_or_namespace_de']}", "VISIBLE_OWNER"
                    card_values[role].append(short_value)

                binding = {
                    "atom": atom,
                    "value": short_value,
                    "role": role,
                    "target": target,
                    "origin": origin,
                    "category_id": category_id,
                }
                if not target and role not in {"ACTION", "BOUNDARY", "LOCAL"}:
                    pending.append(binding)
                elif origin:
                    binding_origin_counts[origin] += 1
                    statement_origins[origin] += 1
                card_bindings.append(binding)
                statement_bindings.append(binding)
                statement_values[short_value] += 1

            if actions_here:
                # Multi-head cards are nested packages (CH[K[Y]]), not flat
                # replacement chains.  The inner head closes with the card;
                # the first/outer head remains available to the next card.
                active = actions_here[min(actions_here)]

            close = "DY" in atoms
            if close:
                if pending:
                    fallback_value = PREDICATE_FALLBACK.get(legacy["predicate_operation_de"], "LOKALE HANDLUNG")
                    fallback_ref = inherited_ref or f"MASTER:{sid}:{fallback_value}"
                    for item in pending:
                        item["target"] = fallback_ref
                        item["origin"] = "MASTER_HEAD_AT_CLOSE"
                        binding_origin_counts["MASTER_HEAD_AT_CLOSE"] += 1
                        statement_origins["MASTER_HEAD_AT_CLOSE"] += 1
                    pending.clear()
                active = ""

            duplicate = duplicates.get(event_id)
            ordinal += 1
            event_rows.append({
                "running_event_ordinal": ordinal,
                "event_id": event_id,
                "statement_id": sid,
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "owner_de": statement["visible_owner_or_namespace_de"],
                "locus": meta["locus"],
                "card_ordinal_in_statement": card_index,
                "surface": surface,
                "component_recipe": recipe,
                "action_heads_de": "+".join(action_values_here) or "NONE",
                "active_head_before_de": target_value(active_before) or "NONE",
                "arguments_de": "+".join(card_values["ARGUMENT"]) or "NONE",
                "relations_de": "+".join(card_values["RELATION"]) or "NONE",
                "grades_de": "+".join(card_values["GRADE"]) or "NONE",
                "sequence_de": "+".join(card_values["SEQUENCE"]) or "NONE",
                "local_channels_de": "+".join(card_values["LOCAL"]) or "NONE",
                "binding_trace_de": "PENDING_STATEMENT_SCOPE",
                "active_head_after_de": target_value(active) or "NONE",
                "closes_gang": "YES" if close else "NO",
                "duplicate_rule": duplicate["selected_doubling_rule"] if duplicate else "NONE",
                "scope_status": "PENDING_STATEMENT_SCOPE",
                "_bindings": card_bindings,
            })

        if pending:
            fallback_value = PREDICATE_FALLBACK.get(legacy["predicate_operation_de"], "LOKALE HANDLUNG")
            fallback_ref = inherited_ref or f"MASTER:{sid}:{fallback_value}"
            for item in pending:
                item["target"] = fallback_ref
                item["origin"] = "MASTER_HEAD_AT_STATEMENT_END"
                binding_origin_counts["MASTER_HEAD_AT_STATEMENT_END"] += 1
                statement_origins["MASTER_HEAD_AT_STATEMENT_END"] += 1
            pending.clear()

        # Pending arguments have now either found the next action or the
        # statement's memorized action head.  Render the final, not merely the
        # momentary, binding trace for every card in this statement.
        for event_row in event_rows[-len(surfaces):]:
            card_bindings = event_row["_bindings"]
            trace_parts = []
            for item in card_bindings:
                if item["role"] == "ACTION":
                    trace_parts.append(f"{item['value']}=KOPF")
                elif item["role"] == "LOCAL":
                    trace_parts.append(f"{item['value']}→BESITZER")
                elif item["role"] == "BOUNDARY":
                    trace_parts.append(f"{item['value']}→GANG")
                else:
                    trace_parts.append(f"{item['value']}→{target_value(str(item['target'])) or 'OFFEN'}")
            origins = {str(item["origin"]) for item in card_bindings if item["origin"]}
            open_binding = any(not item["target"] for item in card_bindings if item["role"] not in {"ACTION", "BOUNDARY", "LOCAL"})
            carried = any(origin in {"RUNNING_ACTION", "FORWARD_TO_NEXT_ACTION", "MASTER_HEAD_AT_CLOSE", "MASTER_HEAD_AT_STATEMENT_END"} for origin in origins)
            event_row["binding_trace_de"] = " | ".join(trace_parts)
            event_row["scope_status"] = "OPEN_SCOPE" if open_binding else ("CARRIED_SCOPE" if carried else "SELF_CONTAINED")

        statement_unbound = sum(1 for item in statement_bindings if item["role"] not in {"ACTION", "BOUNDARY", "LOCAL"} and not item["target"])
        action_chain = []
        for action in statement_actions:
            if not action_chain or action_chain[-1] != action:
                action_chain.append(action)
        if not action_chain:
            action_chain = [target_value(inherited_ref)] if inherited_ref else [PREDICATE_FALLBACK.get(legacy["predicate_operation_de"], "LOKALE HANDLUNG")]

        arg_text = "+".join(f"{name}×{count}" for name, count in statement_values.items() if name in ARGUMENT.values()) or "NONE"
        rel_text = "+".join(f"{name}×{count}" for name, count in statement_values.items() if name in RELATION.values()) or "NONE"
        grade_text = "+".join(f"{name}×{count}" for name, count in statement_values.items() if name in GRADE.values()) or "NONE"
        statement_rows.append({
            "book_statement_ordinal": statement["book_statement_ordinal"],
            "statement_id": sid,
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "owner_de": statement["visible_owner_or_namespace_de"],
            "event_count": statement["event_count"],
            "predicate_realization": legacy["predicate_realization"],
            "seed_action_de": target_value(inherited_ref) or "NONE",
            "inheritance_source_statement_id": inherited_source or "NONE",
            "action_chain_de": " > ".join(action_chain),
            "arguments_de": arg_text,
            "relations_de": rel_text,
            "grades_de": grade_text,
            "end_mode": statement["end_mode"],
            "binding_origins": "+".join(f"{name}×{count}" for name, count in sorted(statement_origins.items())),
            "scope_skeleton_de": f"BESITZER[{statement['visible_owner_or_namespace_de']}] > HANDLUNG[{ ' > '.join(action_chain)}] > ARG[{arg_text}] > REL[{rel_text}] > GRAD[{grade_text}] > {statement['end_mode']}",
            "unbound_modifier_count": statement_unbound,
            "scope_result": "COMPLETE_SCOPE_READING" if statement_unbound == 0 else "OPEN_SCOPE",
        })

    event_fields = [
        "running_event_ordinal", "event_id", "statement_id", "physical_page", "register", "owner_de", "locus",
        "card_ordinal_in_statement", "surface", "component_recipe", "action_heads_de", "active_head_before_de",
        "arguments_de", "relations_de", "grades_de", "sequence_de", "local_channels_de", "binding_trace_de",
        "active_head_after_de", "closes_gang", "duplicate_rule", "scope_status",
    ]
    statement_fields = [
        "book_statement_ordinal", "statement_id", "physical_page", "register", "owner_de", "event_count",
        "predicate_realization", "seed_action_de", "inheritance_source_statement_id", "action_chain_de",
        "arguments_de", "relations_de", "grades_de", "end_mode", "binding_origins", "scope_skeleton_de",
        "unbound_modifier_count", "scope_result",
    ]
    write_tsv(OUT / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv", event_rows, event_fields)
    write_tsv(OUT / "PASS1022_627_STATEMENT_SCOPE_EDITION.tsv", statement_rows, statement_fields)

    rules = [
        {"rule": 1, "name": "OWNER_FORWARD", "instruction_de": "Bild, Gefäß, Station oder Rad trägt den Besitzer bis zur nächsten echten Besitzer-/Proseblockgrenze; Zeilen- und bloßer Bildumbruch ändern nichts."},
        {"rule": 2, "name": "GANG_BOUNDARY", "instruction_de": "CARRIER_Q eröffnet den lokalen Gang; nur lizenziertes DY schließt den Gang, nicht den Bildbesitzer."},
        {"rule": 3, "name": "PACKAGE_FIRST", "instruction_de": "Längste Form zuerst; CHK/CKH und gleiche Doppelkerne vor jeder Nachbarschaftsbindung öffnen."},
        {"rule": 4, "name": "ACTION_HEAD", "instruction_de": "OK CH SH K S T CHD R P eröffnet oder ersetzt die laufende Handlung."},
        {"rule": 5, "name": "LOCAL_INHERITANCE", "instruction_de": "Fehlt ein Kopf, übernimmt die Kurzform die laufende Handlung desselben Besitzers und Gangs; OT wechselt zum Geschwisterschritt, OL führt fort, OS/VORBEZUG stellt den vorherigen Besitzerrahmen wieder her."},
        {"rule": 6, "name": "ARGUMENT_ATTACHMENT", "instruction_de": "Y AIIN AIN OR binden zuerst im eigenen Paket an den nächsten Handlungskopf, sonst rückwärts an die laufende Handlung."},
        {"rule": 7, "name": "RELATION_SIDE", "instruction_de": "AR/AL bevorzugen die Handlung links; L/AIR rahmen die Handlung rechts, jeweils mit örtlichem Rückfall statt erfundener Richtung."},
        {"rule": 8, "name": "GRADE_ATTACHMENT", "instruction_de": "E EE EEE IIN DA O verändern nur die nächste kompatible oder bereits laufende Handlung und reichen nie über DY/Besitzergrenze."},
    ]
    write_tsv(OUT / "PASS1022_EIGHT_SCOPE_RULES.tsv", rules, ["rule", "name", "instruction_de"])

    summary = {
        "result": "COMPLETE_OWNER_ACTION_ARGUMENT_SCOPE_STACK",
        "statements": len(statement_rows),
        "running_events": len(event_rows),
        "component_atoms": sum(atom_counts.values()),
        "distinct_graphic_signs": len(atom_counts),
        "unbound_modifiers": sum(int(row["unbound_modifier_count"]) for row in statement_rows),
        "complete_scope_statements": sum(row["scope_result"] == "COMPLETE_SCOPE_READING" for row in statement_rows),
        "binding_origin_counts": dict(sorted(binding_origin_counts.items())),
        "duplicate_events": len(duplicates),
        "input_hashes": {path.name: sha(path) for path in [P1009_STATEMENTS, P1009_EVENTS, P1018, P1020, P1021]},
    }
    (OUT / "PASS1022_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
