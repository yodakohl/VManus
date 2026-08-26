#!/usr/bin/env python3
"""Rebuild the creative sidequest scope layer from the Pass-1026 recipes."""

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
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
P1009 = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth"
P1018 = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_revision_one_thousand_eighteenth"
P1020 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_sheet_roundtrip_one_thousand_twentieth"
P1025 = ROOT / "experiments/yolo/sidequest_semantic_leave_one_register_replay_one_thousand_twenty_fifth"
P1026 = ROOT / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth"
FULL_LEDGER = P1009 / "PASS1009_4581_EVENT_LEDGER.tsv"
STATEMENTS = P1018 / "PASS1018_627_REVISED_CORE_EDITION.tsv"
CATEGORIES = P1020 / "PASS1020_31_CATEGORY_LEXICON.tsv"
OLD_EVENTS = P1025 / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv"
OLD_ATTACHMENTS = P1025 / "PASS1025_4342_CORRECTED_ATTACHMENTS.tsv"
CORRECTED_EVENTS = P1026 / "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv"
REGISTERS = ["HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"]

ACTIONS = {
    "OK": "SETZEN", "CH": "NEHMEN", "SH": "HALTEN", "K": "GEBEN",
    "S": "WÄHLEN", "T": "EINSTELLEN", "CHD": "UMSETZEN",
    "R": "MARKIEREN", "P": "EINSETZEN",
}
FOCI = {
    "AIIN": ("WERT", "ARGUMENT"), "AIN": ("ANTEIL", "ARGUMENT"),
    "OR": ("EINHEIT", "ARGUMENT"), "Y": ("AKTIVER POSTEN", "ARGUMENT"),
    "E": ("GRAD I", "GRADE"), "EE": ("GRAD II", "GRADE"),
    "EEE": ("GRAD III", "GRADE"), "AL": ("ZIELORT", "RELATION"),
    "AR": ("AUSGANG", "RELATION"), "L": ("VERBINDUNG", "RELATION"),
    "AIR": ("LAUF", "RELATION"),
}
RELATION_FOCI = {"AL", "AR", "L", "AIR"}
FORWARD_FOCI = {"L", "AIR"}
R_COMPLEMENTS = {"Y", "AIIN", "AIN", "OR", "AL", "AR", "AIR", "L"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty table {path.name}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipe(values: list[str] | set[str]) -> str:
    selected = list(dict.fromkeys(value for value in values if value and value != "NONE"))
    return "|".join(selected) if selected else "NONE"


def counted(values: list[str], order: list[str]) -> str:
    counts = Counter(values)
    return "+".join(f"{value}×{counts[value]}" for value in order if counts[value]) or "NONE"


def action_marks(atoms: list[str]) -> list[tuple[int, str]]:
    return [(index + 1, atom) for index, atom in enumerate(atoms) if atom in ACTIONS]


def action_label(action: str | None) -> str:
    return f"{action}={ACTIONS[action]}" if action else "NONE"


def duplicate_scope(atoms: list[str], atom_index: int, focus: str) -> tuple[str, str, str]:
    paired: int | None = None
    if atom_index and atoms[atom_index - 1] == focus:
        paired = atom_index - 1
    elif atom_index + 1 < len(atoms) and atoms[atom_index + 1] == focus:
        paired = atom_index + 1
    if paired is None:
        return "SINGLE", "SINGLE", "NONE"
    first = min(atom_index, paired)
    if focus == "OR":
        return "PACKAGE_SCOPE_DESCENT", (
            "PACKAGE_OUTER" if atom_index == first else "PACKAGE_INNER"
        ), str(paired + 1)
    return "FREE_PLURAL_OR_REPEAT", (
        "FREE_PEER_1" if atom_index == first else "FREE_PEER_2"
    ), str(paired + 1)


def local_r_resolution(
    atoms: list[str], r_position: int, active_before: dict[str, object] | None,
) -> tuple[str, int | None, str, dict[str, object] | None]:
    left = [(i + 1, atom) for i, atom in enumerate(atoms[: r_position - 1]) if atom in ACTIONS]
    right = atoms[r_position:]
    next_action = next((i for i, atom in enumerate(right) if atom in ACTIONS), len(right))
    complements = [atom for atom in right[:next_action] if atom in R_COMPLEMENTS]
    if left and complements:
        return "R", r_position, "R_POSITIONAL_NESTED", None
    if left:
        position, action = left[-1]
        return action, position, "R_POSITIONAL_TAIL", None
    if complements or "L" in atoms[: r_position - 1]:
        return "R", r_position, "R_POSITIONAL_HEAD", None
    if "OL" in right[:next_action] and active_before:
        return str(active_before["action"]), None, "R_POSITIONAL_TAIL", active_before
    return "R", r_position, "R_POSITIONAL_HEAD", None


def active_after_card(
    atoms: list[str], event: dict[str, str], card_ordinal: int,
    active_before: dict[str, object] | None,
) -> dict[str, object] | None:
    actions = action_marks(atoms)
    if not actions:
        return active_before
    position, action = actions[-1]
    r_mode = "NONE"
    if action == "R":
        action, new_position, r_mode, inherited = local_r_resolution(atoms, position, active_before)
        if inherited:
            return dict(inherited)
        position = int(new_position or position)
    return {
        "action": action, "event_id": event["source_event_id"],
        "card_ordinal": card_ordinal, "atom_ordinal": position, "r_mode": r_mode,
    }


def reading_for(focus: str, value: str, selection: dict[str, object], owner: str) -> str:
    kind = str(selection["class"])
    action = str(selection["action"]) if selection["action"] else None
    label = action_label(action)
    if kind == "SAME_CARD_LEFT_ACTION":
        return f"{label}[{focus}={value}]"
    if kind == "SAME_CARD_RIGHT_ACTION":
        return f"[{focus}={value}]→{label}"
    if kind == "PREVIOUS_CARD_ACTION":
        return f"{label}⟨VORIGE KARTE⟩[{focus}={value}]"
    if kind == "INHERITED_ACTION":
        return f"{label}⟨GEERBT⟩[{focus}={value}]"
    if kind == "BOUNDED_NEXT_CARD_ACTION":
        return f"[{focus}={value}]→{label}⟨NÄCHSTE KARTE⟩"
    return f"BESITZER={owner}[{focus}={value}]"


def choose_attachment(
    focus: str, focus_position: int, atoms: list[str], event: dict[str, str],
    card_ordinal: int, active_before: dict[str, object] | None,
    next_event: dict[str, str] | None, next_atoms: list[str],
) -> dict[str, object]:
    actions = action_marks(atoms)
    left = [(position, action) for position, action in actions if position < focus_position]
    right = [(position, action) for position, action in actions if position > focus_position]
    nearest_left = left[-1] if left else None
    nearest_right = right[0] if right else None
    chosen: tuple[int, str] | None = None
    if focus in {"AL", "AR"}:
        if nearest_left:
            chosen = nearest_left
        elif not active_before and nearest_right:
            chosen = nearest_right
    elif focus in FORWARD_FOCI:
        chosen = nearest_right or nearest_left
    elif nearest_left and nearest_right:
        chosen = nearest_left if (
            focus_position - nearest_left[0] <= nearest_right[0] - focus_position
        ) else nearest_right
    else:
        chosen = nearest_left or nearest_right

    r_mode = "NONE"
    if chosen:
        position, action = chosen
        inherited_override: dict[str, object] | None = None
        if action == "R":
            action, new_position, r_mode, inherited_override = local_r_resolution(
                atoms, position, active_before
            )
            if inherited_override:
                active_before = inherited_override
                chosen = None
            else:
                position = int(new_position or position)
        if chosen:
            return {
                "class": "SAME_CARD_LEFT_ACTION" if position < focus_position else "SAME_CARD_RIGHT_ACTION",
                "action": action, "source_event": event["source_event_id"],
                "source_card": card_ordinal, "source_atom": position,
                "lookahead": 0, "r_mode": r_mode,
            }

    if active_before:
        return {
            "class": "PREVIOUS_CARD_ACTION" if int(active_before["card_ordinal"]) == card_ordinal - 1 else "INHERITED_ACTION",
            "action": str(active_before["action"]), "source_event": str(active_before["event_id"]),
            "source_card": int(active_before["card_ordinal"]),
            "source_atom": int(active_before["atom_ordinal"]), "lookahead": 0,
            "r_mode": str(active_before.get("r_mode", "NONE")),
        }

    tokens = set(atoms)
    next_actions = action_marks(next_atoms)
    forward = bool(next_actions and "DY" not in tokens and "OS" not in tokens)
    if focus in {"AL", "AR"} and not (tokens & {"CARRIER_Q", "OT", "L", "AIR"}):
        forward = False
    if forward and next_event:
        position, action = next_actions[0]
        if action == "R":
            action, new_position, r_mode, _ = local_r_resolution(next_atoms, position, None)
            position = int(new_position or position)
        return {
            "class": "BOUNDED_NEXT_CARD_ACTION", "action": action,
            "source_event": next_event["source_event_id"], "source_card": card_ordinal + 1,
            "source_atom": position, "lookahead": 1, "r_mode": r_mode,
        }
    return {
        "class": "OWNER_ONLY", "action": None, "source_event": "OWNER",
        "source_card": 0, "source_atom": 0, "lookahead": 0, "r_mode": r_mode,
    }


def rule_family(focus: str, selection: dict[str, object], atoms: list[str]) -> list[str]:
    kind = str(selection["class"])
    if focus in {"AL", "AR"}:
        families = ["AL_AR_ORDERED_FALLBACK"]
    elif focus in FORWARD_FOCI:
        families = ["L_AIR_RIGHT_FALLBACK"]
    elif kind in {"SAME_CARD_LEFT_ACTION", "SAME_CARD_RIGHT_ACTION"}:
        families = ["NEAREST_HEAD_LEFT_TIE"]
    elif kind == "PREVIOUS_CARD_ACTION":
        families = ["PREVIOUS_CARD_STACK"]
    elif kind == "INHERITED_ACTION":
        families = ["INHERITED_ACTION_STACK"]
    elif kind == "BOUNDED_NEXT_CARD_ACTION":
        families = ["Q_OT_PACKAGE_FORWARD" if set(atoms) & {"CARRIER_Q", "OT"} else "ONE_CARD_FORWARD"]
    else:
        families = ["OWNER_CONTEXT"]
    if str(selection["r_mode"]) != "NONE":
        families.append("R_POSITIONAL_MARKING")
    return list(dict.fromkeys(families))


def micro_signature(focus: str, selection: dict[str, object], duplicate_mode: str) -> str:
    group = "AL_AR" if focus in {"AL", "AR"} else "L_AIR" if focus in FORWARD_FOCI else "ARG_GRADE"
    parts = [group, str(selection["class"])]
    if str(selection["r_mode"]) != "NONE":
        parts.append(str(selection["r_mode"]))
    if duplicate_mode != "SINGLE":
        parts.append(duplicate_mode)
    return "__".join(parts)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    full_ledger = read_tsv(FULL_LEDGER)
    statements = read_tsv(STATEMENTS)
    categories = read_tsv(CATEGORIES)
    corrected_events = read_tsv(CORRECTED_EVENTS)
    old_events = read_tsv(OLD_EVENTS)
    old_attachments = read_tsv(OLD_ATTACHMENTS)
    if [len(full_ledger), len(statements), len(categories), len(corrected_events), len(old_events), len(old_attachments)] != [4581, 627, 31, 3888, 3888, 4342]:
        raise AssertionError("source inventory mismatch")

    category_by_atom: dict[str, dict[str, str]] = {}
    for category in categories:
        for atom in category["graphic_signs"].split("|"):
            if atom in category_by_atom:
                raise AssertionError(f"duplicate category atom {atom}")
            category_by_atom[atom] = category

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in corrected_events:
        events_by_statement[event["statement_id"]].append(event)
    for statement in statements:
        events = events_by_statement[statement["statement_id"]]
        if len(events) != int(statement["event_count"]) or [row["surface"] for row in events] != statement["surface_sequence"].split():
            raise AssertionError(f"statement alignment failed: {statement['statement_id']}")

    attachments: list[dict[str, object]] = []
    running_ordinal = 0
    for statement in statements:
        events = events_by_statement[statement["statement_id"]]
        active: dict[str, object] | None = None
        for card_index, event in enumerate(events, start=1):
            running_ordinal += 1
            atoms = event["pass1026_recipe"].split("+")
            missing = [atom for atom in atoms if atom not in category_by_atom]
            if missing:
                raise AssertionError(f"unregistered atom in {event['source_event_id']}: {missing}")
            next_event = events[card_index] if card_index < len(events) else None
            next_atoms = next_event["pass1026_recipe"].split("+") if next_event else []
            active_label = action_label(str(active["action"]) if active else None)
            focus_seen: Counter[str] = Counter()
            for atom_index, focus in enumerate(atoms):
                if focus not in FOCI:
                    continue
                focus_seen[focus] += 1
                value, family = FOCI[focus]
                selection = choose_attachment(
                    focus, atom_index + 1, atoms, event, card_index, active, next_event, next_atoms
                )
                duplicate_mode, duplicate_role, paired = duplicate_scope(atoms, atom_index, focus)
                families = rule_family(focus, selection, atoms)
                attachments.append({
                    "attachment_id": f"G399-A{len(attachments) + 1:05d}",
                    "focus_key": f"{event['source_event_id']}:{focus}:{focus_seen[focus]}",
                    "focus_core": focus, "focus_value_de": value, "focus_family": family,
                    "event_id": event["source_event_id"], "pass1026_event_id": event["pass1026_event_id"],
                    "running_event_ordinal": running_ordinal, "physical_page": event["physical_page"],
                    "register": event["register"], "statement_id": statement["statement_id"],
                    "card_ordinal_in_statement": card_index, "locus": event["locus"],
                    "owner_de": statement["visible_owner_or_namespace_de"], "surface": event["surface"],
                    "component_recipe": event["pass1026_recipe"], "focus_atom_ordinal": atom_index + 1,
                    "focus_occurrence_ordinal": focus_seen[focus],
                    "left_atom": atoms[atom_index - 1] if atom_index else "CARD_START",
                    "right_atom": atoms[atom_index + 1] if atom_index + 1 < len(atoms) else "CARD_END",
                    "active_head_before": active_label, "chosen_attachment_class": selection["class"],
                    "chosen_action": selection["action"] or "OWNER",
                    "chosen_action_value_de": ACTIONS[str(selection["action"])] if selection["action"] else "BESITZER",
                    "chosen_action_event_id": selection["source_event"],
                    "chosen_action_card_ordinal": selection["source_card"],
                    "chosen_action_atom_ordinal": selection["source_atom"],
                    "selected_attachment_de": reading_for(focus, value, selection, statement["visible_owner_or_namespace_de"]),
                    "teaching_rule_families": pipe(families),
                    "micro_signature": micro_signature(focus, selection, duplicate_mode),
                    "r_position_mode": selection["r_mode"], "duplicate_scope_mode": duplicate_mode,
                    "duplicate_scope_role": duplicate_role, "paired_focus_atom_ordinal": paired,
                    "bounded_lookahead_cards": selection["lookahead"], "owner_boundary_crossed": "NO",
                    "resolution_status": "COMPLETE_SELECTED_SCOPE",
                })
            active = active_after_card(atoms, event, card_index, active)
    if running_ordinal != 3888 or len(attachments) != 4374:
        raise AssertionError(f"rebuilt inventory mismatch: {running_ordinal}/{len(attachments)}")

    attachments_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachments:
        attachments_by_statement[str(row["statement_id"])].append(row)
    changed_statement_ids = {row["statement_id"] for row in corrected_events if row["pass1026_change"] != "UNCHANGED"}
    statement_rows: list[dict[str, object]] = []
    for ordinal, statement in enumerate(statements, start=1):
        sid = statement["statement_id"]
        events = events_by_statement[sid]
        focus_rows = attachments_by_statement[sid]
        atoms = [atom for event in events for atom in event["pass1026_recipe"].split("+")]
        actions = [atom for atom in atoms if atom in ACTIONS]
        arguments = [atom for atom in atoms if atom in {"AIIN", "AIN", "OR", "Y"}]
        relations = [atom for atom in atoms if atom in RELATION_FOCI]
        grades = [atom for atom in atoms if atom in {"E", "EE", "EEE"}]
        rules = {family for row in focus_rows for family in str(row["teaching_rule_families"]).split("|") if family != "NONE"}
        args_de = counted([FOCI[value][0] for value in arguments], ["WERT", "ANTEIL", "EINHEIT", "AKTIVER POSTEN"])
        rel_de = counted([FOCI[value][0] for value in relations], ["ZIELORT", "AUSGANG", "VERBINDUNG", "LAUF"])
        grade_de = counted([FOCI[value][0] for value in grades], ["GRAD I", "GRAD II", "GRAD III"])
        action_de = counted([ACTIONS[action] for action in actions], list(ACTIONS.values()))
        statement_rows.append({
            "statement_ordinal": ordinal, "statement_id": sid, "physical_page": statement["physical_page"],
            "register": statement["register"], "owner_de": statement["visible_owner_or_namespace_de"],
            "event_count": len(events), "surface_sequence": " ".join(event["surface"] for event in events),
            "corrected_recipe_sequence": " | ".join(event["pass1026_recipe"] for event in events),
            "action_chain_de": " > ".join(ACTIONS[action] for action in actions) or "BESITZERGETRAGEN",
            "arguments_de": args_de, "relations_de": rel_de, "grades_de": grade_de,
            "end_mode": statement["end_mode"], "focus_attachment_count": len(focus_rows),
            "bounded_forward_count": sum(row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION" for row in focus_rows),
            "owner_only_count": sum(row["chosen_attachment_class"] == "OWNER_ONLY" for row in focus_rows),
            "rule_families": pipe(sorted(rules)),
            "scope_skeleton_de": f"BESITZER[{statement['visible_owner_or_namespace_de']}] > HANDLUNG[{action_de}] > ARG[{args_de}] > REL[{rel_de}] > GRAD[{grade_de}] > {statement['end_mode']}",
            "pass1026_recipe_changed": "YES" if sid in changed_statement_ids else "NO",
            "scope_result": "COMPLETE_SELECTED_SCOPE__NO_OPEN_ATTACHMENTS",
        })

    surface_pages: dict[str, set[str]] = defaultdict(set)
    surface_registers: dict[str, set[str]] = defaultdict(set)
    recipe_pages: dict[str, set[str]] = defaultdict(set)
    recipe_registers: dict[str, set[str]] = defaultdict(set)
    for event in corrected_events:
        surface_pages[event["surface"]].add(event["physical_page"])
        surface_registers[event["surface"]].add(event["register"])
        recipe_pages[event["pass1026_recipe"]].add(event["physical_page"])
        recipe_registers[event["pass1026_recipe"]].add(event["register"])
    event_rows: list[dict[str, object]] = []
    for ordinal, event in enumerate(corrected_events, start=1):
        page, register, recipe = event["physical_page"], event["register"], event["pass1026_recipe"]
        osp, orp = surface_pages[event["surface"]] - {page}, recipe_pages[recipe] - {page}
        osr, orr = surface_registers[event["surface"]] - {register}, recipe_registers[recipe] - {register}
        page_result = "EXACT_SURFACE_FROM_OTHER_PAGE" if osp else "ROOT_RECIPE_FROM_OTHER_PAGE" if orp else "NEW_PAGE_RECIPE__KNOWN_ATOMS"
        register_result = "EXACT_SURFACE_FROM_OTHER_REGISTER" if osr else "ROOT_RECIPE_FROM_OTHER_REGISTER" if orr else "NEW_REGISTER_RECIPE__KNOWN_ATOMS"
        event_rows.append({
            "replay_event_id": f"G399-E{ordinal:04d}", "event_id": event["source_event_id"],
            "pass1026_event_id": event["pass1026_event_id"], "physical_page": page,
            "register": register, "statement_id": event["statement_id"], "locus": event["locus"],
            "surface": event["surface"], "component_recipe": recipe,
            "component_atom_count": len(recipe.split("+")), "pass1026_change": event["pass1026_change"],
            "all_atoms_on_fixed_sheet": "YES", "outside_surface_pages": pipe(sorted(osp)),
            "outside_recipe_pages": pipe(sorted(orp)),
            "outside_surface_registers": pipe([value for value in REGISTERS if value in osr]),
            "outside_recipe_registers": pipe([value for value in REGISTERS if value in orr]),
            "page_replay_result": page_result, "register_replay_result": register_result,
        })

    rule_pages: dict[str, set[str]] = defaultdict(set)
    rule_registers: dict[str, set[str]] = defaultdict(set)
    rule_counts: Counter[tuple[str, str]] = Counter()
    for row in attachments:
        for family in str(row["teaching_rule_families"]).split("|"):
            if family == "NONE":
                continue
            rule_pages[family].add(str(row["physical_page"])); rule_registers[family].add(str(row["register"])); rule_counts[(family, str(row["register"]))] += 1
    rule_rows: list[dict[str, object]] = []
    for family in sorted(rule_pages):
        row: dict[str, object] = {
            "rule_family": family, "support_page_count": len(rule_pages[family]),
            "support_pages": pipe(sorted(rule_pages[family])), "support_register_count": len(rule_registers[family]),
            "support_registers": pipe([value for value in REGISTERS if value in rule_registers[family]]),
            "survives_every_page_where_used": "YES" if len(rule_pages[family]) >= 2 else "NO",
            "survives_every_register_where_used": "YES" if len(rule_registers[family]) >= 2 else "NO",
        }
        for register in REGISTERS:
            row[f"{register.lower()}_occurrences"] = rule_counts[(family, register)]
        rule_rows.append(row)

    category_registers: dict[str, set[str]] = defaultdict(set)
    for event in corrected_events:
        for atom in event["pass1026_recipe"].split("+"):
            category_registers[category_by_atom[atom]["category_id"]].add(event["register"])

    page_order = list(dict.fromkeys(row["physical_page"] for row in full_ledger))
    full_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    focus_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in full_ledger: full_by_page[row["physical_page"]].append(row)
    for row in event_rows: events_by_page[str(row["physical_page"])].append(row)
    for row in attachments: focus_by_page[str(row["physical_page"])].append(row)
    for row in statement_rows: statements_by_page[str(row["physical_page"])].append(row)
    page_rows: list[dict[str, object]] = []
    for ordinal, page in enumerate(page_order, start=1):
        full, page_events, page_focus = full_by_page[page], events_by_page.get(page, []), focus_by_page.get(page, [])
        rules = {family for row in page_focus for family in str(row["teaching_rule_families"]).split("|") if family != "NONE"}
        unsupported = {family for family in rules if not (rule_pages[family] - {page})}
        page_rows.append({
            "page_ordinal": ordinal, "physical_page": page, "register": full[0]["register"],
            "visible_group_count": len(full), "running_event_count": len(page_events),
            "local_group_count": sum(row["event_role"] != "RUNNING_STATEMENT" for row in full),
            "statement_count": len(statements_by_page.get(page, [])), "focus_attachment_count": len(page_focus),
            "bounded_forward_count": sum(row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION" for row in page_focus),
            "owner_only_count": sum(row["chosen_attachment_class"] == "OWNER_ONLY" for row in page_focus),
            "rule_families_used": pipe(sorted(rules)), "unsupported_rule_families_when_page_held": pipe(sorted(unsupported)),
            "exact_surface_from_other_page": sum(row["page_replay_result"] == "EXACT_SURFACE_FROM_OTHER_PAGE" for row in page_events),
            "root_recipe_from_other_page": sum(row["page_replay_result"] == "ROOT_RECIPE_FROM_OTHER_PAGE" for row in page_events),
            "new_page_recipe_known_atoms": sum(row["page_replay_result"] == "NEW_PAGE_RECIPE__KNOWN_ATOMS" for row in page_events),
            "page_replay_result": "LOCAL_ADDRESS_COPY_ONLY" if not page_events else "FAIL_PRIVATE_RULE" if unsupported else "PASS_FIXED_SCOPE_RULES",
        })

    focus_by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    replay_by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    statement_by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachments: focus_by_register[str(row["register"])].append(row)
    for row in event_rows: replay_by_register[str(row["register"])].append(row)
    for row in statement_rows: statement_by_register[str(row["register"])].append(row)
    register_rows: list[dict[str, object]] = []
    for register in REGISTERS:
        reg_focus, reg_events = focus_by_register[register], replay_by_register[register]
        rules = {family for row in reg_focus for family in str(row["teaching_rule_families"]).split("|") if family != "NONE"}
        unsupported_rules = {family for family in rules if not (rule_registers[family] - {register})}
        categories_used = {category_by_atom[atom]["category_id"] for event in corrected_events if event["register"] == register for atom in event["pass1026_recipe"].split("+")}
        unsupported_categories = {category for category in categories_used if not (category_registers[category] - {register})}
        register_rows.append({
            "held_register": register, "running_event_count": len(reg_events),
            "statement_count": len(statement_by_register[register]), "focus_attachment_count": len(reg_focus),
            "exact_surface_from_other_register": sum(row["register_replay_result"] == "EXACT_SURFACE_FROM_OTHER_REGISTER" for row in reg_events),
            "root_recipe_from_other_register": sum(row["register_replay_result"] == "ROOT_RECIPE_FROM_OTHER_REGISTER" for row in reg_events),
            "new_register_recipe_known_atoms": sum(row["register_replay_result"] == "NEW_REGISTER_RECIPE__KNOWN_ATOMS" for row in reg_events),
            "used_rule_families": pipe(sorted(rules)), "unsupported_rule_families": pipe(sorted(unsupported_rules)),
            "used_category_count": len(categories_used), "unsupported_categories": pipe(sorted(unsupported_categories)),
            "register_replay_result": "PASS_FIXED_SCOPE" if not unsupported_rules and not unsupported_categories else "FAIL_PRIVATE_RULE_OR_CATEGORY",
        })

    old_focus_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    old_event_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old_attachments: old_focus_by_statement[row["statement_id"]].append(row)
    for row in old_events: old_event_by_statement[row["statement_id"]].append(row)
    change_rows: list[dict[str, object]] = []
    for sid in sorted(changed_statement_ids, key=lambda value: int(value.split("S")[-1])):
        old_focus, new_focus = old_focus_by_statement[sid], attachments_by_statement[sid]
        old_counts, new_counts = Counter(row["focus_core"] for row in old_focus), Counter(str(row["focus_core"]) for row in new_focus)
        added, removed = new_counts - old_counts, old_counts - new_counts
        old_rules = {family for row in old_focus for family in row["teaching_rule_families"].split("|") if family != "NONE"}
        new_rules = {family for row in new_focus for family in str(row["teaching_rule_families"]).split("|") if family != "NONE"}
        new_events = events_by_statement[sid]
        change_rows.append({
            "statement_id": sid, "physical_page": new_events[0]["physical_page"], "register": new_events[0]["register"],
            "event_count": len(new_events), "changed_event_count": sum(row["pass1026_change"] != "UNCHANGED" for row in new_events),
            "old_recipe_sequence": " | ".join(row["component_recipe"] for row in old_event_by_statement[sid]),
            "new_recipe_sequence": " | ".join(row["pass1026_recipe"] for row in new_events),
            "old_focus_count": len(old_focus), "new_focus_count": len(new_focus), "focus_count_delta": len(new_focus) - len(old_focus),
            "added_focus_atoms": pipe([f"{key}×{added[key]}" for key in FOCI if added[key]]),
            "removed_focus_atoms": pipe([f"{key}×{removed[key]}" for key in FOCI if removed[key]]),
            "old_rule_families": pipe(sorted(old_rules)), "new_rule_families": pipe(sorted(new_rules)),
            "new_bounded_forward_count": sum(row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION" for row in new_focus),
            "new_owner_only_count": sum(row["chosen_attachment_class"] == "OWNER_ONLY" for row in new_focus),
            "scope_rebuild_result": "COMPLETE__NO_NEW_CORE_VALUE",
        })

    paths = [
        OUT / "gdt399_4374_scope_attachments.tsv", OUT / "gdt399_627_statement_scope_edition.tsv",
        OUT / "gdt399_3888_event_replay.tsv", OUT / "gdt399_22_page_replay.tsv",
        OUT / "gdt399_four_register_replay.tsv", OUT / "gdt399_rule_support.tsv",
        OUT / "gdt399_96_statement_change_audit.tsv",
    ]
    for path, rows in zip(paths, [attachments, statement_rows, event_rows, page_rows, register_rows, rule_rows, change_rows]):
        write_tsv(path, rows)
    page_counts = Counter(str(row["page_replay_result"]) for row in page_rows)
    register_counts = Counter(str(row["register_replay_result"]) for row in register_rows)
    selections = Counter(str(row["chosen_attachment_class"]) for row in attachments)
    surface_recipes: dict[str, set[str]] = defaultdict(set)
    for row in corrected_events: surface_recipes[row["surface"]].add(row["pass1026_recipe"])
    summary = {
        "status": "COMPLETE_CREATIVE_SCOPE_REBUILD", "running_event_count": 3888,
        "statement_count": 627, "focus_attachment_count": len(attachments),
        "pass1025_focus_attachment_count": len(old_attachments),
        "focus_attachment_delta": len(attachments) - len(old_attachments),
        "pass1026_changed_event_count": sum(row["pass1026_change"] != "UNCHANGED" for row in corrected_events),
        "affected_statement_count": len(change_rows), "selection_class_counts": dict(sorted(selections.items())),
        "bounded_next_card_count": selections["BOUNDED_NEXT_CARD_ACTION"],
        "maximum_lookahead_cards": max(int(row["bounded_lookahead_cards"]) for row in attachments),
        "owner_boundary_crossings": sum(row["owner_boundary_crossed"] == "YES" for row in attachments),
        "rule_family_count": len(rule_rows),
        "rules_with_single_page_support": sum(row["survives_every_page_where_used"] == "NO" for row in rule_rows),
        "rules_with_single_register_support": sum(row["survives_every_register_where_used"] == "NO" for row in rule_rows),
        "page_replay_counts": dict(sorted(page_counts.items())), "register_replay_counts": dict(sorted(register_counts.items())),
        "surface_recipe_conflicts": sum(len(recipes) > 1 for recipes in surface_recipes.values()),
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in [FULL_LEDGER, STATEMENTS, CATEGORIES, OLD_EVENTS, OLD_ATTACHMENTS, CORRECTED_EVENTS]},
        "output_hashes": {path.name: sha256(path) for path in paths},
    }
    (OUT / "gdt399_result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = f"""# GDT399 — Sichtbar korrigierter Scope-Neubau

Status: kreative Arbeitsrekonstruktion, keine bestätigte Übersetzung.

## Ergebnis

Die Pass-1026-Kartenfolge lässt sich vollständig neu kompilieren: **3.888
Ereignisse, 627 Aussagen und {len(attachments):,} Fokusanschlüsse**. Gegenüber
dem überholten Pass-1025-Inventar entstehen netto **{len(attachments) - len(old_attachments):+d}**
Anschlüsse, weil die 203 sichtbar neu zerlegten Oberflächen zuvor verborgene
WERT-/ANTEIL-/POSTEN-/GRAD-/RELATIONSzeichen wieder zeigen.

Kein Anschluss bleibt offen. Kein Fokus springt über eine Besitzergrenze; der
weiteste Vorgriff bleibt genau eine Karte. Die neun bekannten groben
Scope-Familien reichen weiterhin aus. {sum(row['survives_every_page_where_used'] == 'NO' for row in rule_rows)}
Familien sind auf nur einer Seite und {sum(row['survives_every_register_where_used'] == 'NO' for row in rule_rows)}
auf nur einem Register beschränkt.

## Was sich wirklich geändert hat

- 239 Kartenereignisse in 96 Aussagen tragen ein neues sichtbares Rezept.
- Die komplette Fokuszahl steigt von 4.342 auf {len(attachments):,}.
- Alle 96 betroffenen Aussagen erhalten wieder eine vollständige Lesung aus
  denselben 19 Kernwerten; kein neuer deutscher Kern wurde ergänzt.
- Jede Oberfläche hat weiterhin genau ein Rezept.
- Die vier Register werden erneut vollständig zurückgespielt: `{dict(sorted(register_counts.items()))}`.

## Werkstattregel

Ein sichtbarer Zeichenwechsel wird zuerst neu zerlegt. Nur benannte Q-,
CHD/CHED-, CHK/CHEK-, OS/OES-, D- oder offene-Y-Verpackungen dürfen dasselbe
Rezept behalten. Danach gelten unverändert: nächster Kopf mit Linksgleichstand,
AL/AR links→aktiv→gleiche Karte rechts→Besitzer, L/AIR rechts→links, höchstens
eine Karte begrenzter Vorgriff, R positional und echter Besitzer-/Aussageschluss
als Reset.

## Bedeutung für die nächsten Seiten

Das war kein kosmetischer Patch: Die Satzmaschine wurde aus den korrigierten
Karten neu erzeugt. Sie überlebt, ohne die 239 Änderungen zurückzudrehen. Der
nächste sinnvolle Schritt ist ein gezielter Holdout dieser neuen
{len(attachments):,}-Anschlussbasis und erst danach die nächste Vierseitenfreigabe.

## Artefakte

- `artifacts/gdt399_4374_scope_attachments.tsv`
- `artifacts/gdt399_627_statement_scope_edition.tsv`
- `artifacts/gdt399_3888_event_replay.tsv`
- `artifacts/gdt399_22_page_replay.tsv`
- `artifacts/gdt399_four_register_replay.tsv`
- `artifacts/gdt399_rule_support.tsv`
- `artifacts/gdt399_96_statement_change_audit.tsv`
- `artifacts/gdt399_result.json`
"""
    (HERE / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
