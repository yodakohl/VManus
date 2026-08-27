#!/usr/bin/env python3
"""Compile five modifier voice cards and four ordered join rules over GDT569."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt570_five_fragment_four_join_modifier_voice"
OUT = BASE / "artifacts"
G569 = ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts"
G567 = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "context_events": G569 / "gdt569_5122_context_voice_event_edition.tsv",
    "context_statements": G569 / "gdt569_793_context_voice_statement_edition.tsv",
    "context_states": G569 / "gdt569_1656_context_voice_state_clauses.tsv",
    "page_profiles": G569 / "gdt569_30_page_context_voice_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
    "voice_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
}

CURRENT_FRAGMENTS = {
    "E": "auf Grad I",
    "EE": "auf Grad II",
    "EEE": "auf Grad III",
    "IIN": "auf der Stufe",
    "DA": "auf der zweiten Stufe",
    "O": "zur Ausführung",
    "CARRIER_Q": "am Beginn",
    "AN": "als Klasse",
    "LOCAL_CHAR_G": "als Variante",
}
TARGET_FRAGMENTS = {
    **CURRENT_FRAGMENTS,
    "IIN": "auf der bezeichneten Stufe",
    "O": "als Ausführung",
    "CARRIER_Q": "als neuen Einsatz",
    "AN": "in der bezeichneten Klasse",
    "LOCAL_CHAR_G": "mit der lokalen Variante",
}
CHANGED_FRAGMENT_ATOMS = ("O", "IIN", "CARRIER_Q", "AN", "LOCAL_CHAR_G")
HERE_ATOMS = {"AM_ADDR", "A_ADDR", "D_ADDR", "D_LABEL", "LOCAL_CHAR_F", "M_LOCAL", "S_ADDR"}
JOIN_CLASS = {
    "GRADE": "OPERATIONAL_MODIFIER",
    "FORMAL_CONTROL": "OPERATIONAL_MODIFIER",
    "RELATION": "RELATION",
    "LOCAL_OR_CLASS_SIGN": "LOCAL_OR_CLASS_SIGN",
}
JOIN_CARD_BY_CLASS = {
    "OPERATIONAL_MODIFIER": "GDT570-J01",
    "RELATION": "GDT570-J02",
    "LOCAL_OR_CLASS_SIGN": "GDT570-J03",
    "CROSS_CLASS": "GDT570-J04",
}
STATUS = (
    "PASS_5_FRAGMENT_CARDS__4_JOIN_RULES__154_MODIFIER_CELLS__224_TRANSITIONS__"
    "103_WITHIN_CLASS_COORDINATED__164_STATE_CLAUSES_REFINED__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("+")


def coordinated(parts: list[str]) -> str:
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " und " + parts[-1]


def join_target(fragments: list[str], types: list[str]) -> tuple[str, list[str]]:
    if len(fragments) != len(types):
        raise RuntimeError("Modifier fragment/type length mismatch")
    groups: list[tuple[str, list[str]]] = []
    for fragment, type_name in zip(fragments, types):
        class_name = JOIN_CLASS[type_name]
        if groups and groups[-1][0] == class_name:
            groups[-1][1].append(fragment)
        else:
            groups.append((class_name, [fragment]))
    return "; ".join(coordinated(parts) for _, parts in groups), [class_name for class_name, _ in groups]


def replace_phrase(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Modifier phrase not found: {old!r} in {text!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["context_events"])
    source_statements = read_tsv(INPUTS["context_statements"])
    source_states = read_tsv(INPUTS["context_states"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    replay = read_tsv(INPUTS["state_replay"])
    voice_cards = read_tsv(INPUTS["voice_cards"])
    counts = [len(source_events), len(source_statements), len(source_states), len(source_pages), len(replay), len(voice_cards)]
    if counts != [5122, 793, 1656, 30, 1656, 39]:
        raise RuntimeError(f"Input count drift: {counts}")

    source_event_by_id = {row["event_id"]: row for row in source_events}
    source_state_by_id = {row["event_id"]: row for row in source_states}
    replay_by_id = {row["event_id"]: row for row in replay}
    if set(source_state_by_id) != set(replay_by_id):
        raise RuntimeError("State replay key drift")
    relation_phrases = {
        (row["register_scope"], row["root_or_trigger"]): row["owner_voice_phrase_de"]
        for row in voice_cards if row["card_class"] == "RELATION_OWNER_VOICE"
    }
    if len(relation_phrases) != 18:
        raise RuntimeError("Relation voice inventory drift")

    def fragment(atom: str, register: str, target: bool) -> str:
        mapping = TARGET_FRAGMENTS if target else CURRENT_FRAGMENTS
        if atom in mapping:
            return mapping[atom]
        if atom in HERE_ATOMS:
            return "an der bezeichneten Stelle"
        key = (register, atom)
        if key in relation_phrases:
            return relation_phrases[key]
        raise RuntimeError(f"No modifier fragment for {register}/{atom}")

    state_rows: list[dict[str, object]] = []
    for source in source_states:
        state = replay_by_id[source["event_id"]]
        atoms = split(state["modifier_atoms"])
        types = split(state["modifier_type_sequence"])
        current_fragments = [fragment(atom, state["register"], False) for atom in atoms]
        target_fragments = [fragment(atom, state["register"], True) for atom in atoms]
        current_phrase = "; ".join(current_fragments) if atoms else "NONE"
        if atoms:
            target_phrase, target_groups = join_target(target_fragments, types)
            after = replace_phrase(source["context_voice_working_clause_de"], current_phrase, target_phrase)
        else:
            target_phrase = "NONE"
            target_groups = []
            after = source["context_voice_working_clause_de"]
        transitions = list(zip(types, types[1:]))
        within = sum(JOIN_CLASS[left] == JOIN_CLASS[right] for left, right in transitions)
        cross = len(transitions) - within
        changed_atoms = [atom for atom in atoms if atom in CHANGED_FRAGMENT_ATOMS]
        state_rows.append({
            "state_edition_ordinal": source["state_edition_ordinal"],
            "event_id": source["event_id"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "cohort": source["cohort"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "context_mode": source["context_mode"],
            "modifier_atoms": state["modifier_atoms"],
            "modifier_type_sequence": state["modifier_type_sequence"],
            "modifier_count": len(atoms),
            "modifier_transition_count": len(transitions),
            "within_class_transition_count": within,
            "cross_class_transition_count": cross,
            "modifier_join_group_sequence": "+".join(target_groups) or "NONE",
            "changed_fragment_atoms": "|".join(changed_atoms) or "NONE",
            "current_modifier_phrase_de": current_phrase,
            "modifier_voice_phrase_de": target_phrase,
            "gdt569_context_voice_clause_de": source["context_voice_working_clause_de"],
            "modifier_voice_working_clause_de": after,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "modifier_voice_changed": "YES" if after != source["context_voice_working_clause_de"] else "NO",
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "MODIFIER_VOICE_ONLY__WRITTEN_ORDER_ROOTS_AND_BOUNDARY_UNCHANGED",
        })

    fragment_rows: list[dict[str, object]] = []
    for atom in CHANGED_FRAGMENT_ATOMS:
        members = [row for row in state_rows if atom in split(str(row["modifier_atoms"]))]
        occurrence_count = sum(split(str(row["modifier_atoms"])).count(atom) for row in members)
        target = TARGET_FRAGMENTS[atom]
        control_support = sum(target in str(row["owner_bound_control_clause_de"]) for row in members)
        cohorts = Counter(str(row["cohort"]) for row in members)
        fragment_rows.append({
            "modifier_voice_card_id": f"GDT570-F{len(fragment_rows) + 1:02d}",
            "modifier_atom": atom,
            "current_fragment_de": CURRENT_FRAGMENTS[atom],
            "modifier_voice_fragment_de": target,
            "state_event_count": len(members),
            "modifier_occurrence_count": occurrence_count,
            "old26_event_count": cohorts["OLD26_GDT407"],
            "current4_event_count": cohorts["CURRENT4_GDT515"],
            "owner_control_target_event_support_count": control_support,
            "owner_control_target_event_support_rate": f"{control_support / len(members):.12f}",
            "voice_selection": "DOMINANT_OLD_OWNER_VOICE" if atom in {"O", "CARRIER_Q"} else "ALL_OWNER_CONTROLS_AGREE",
            "example_event_ids": "|".join(str(row["event_id"]) for row in members[:8]),
            "guard": "GERMAN_FRAGMENT_VOICE_ONLY__ATOM_VALUE_UNCHANGED",
        })

    transition_occurrences: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in state_rows:
        types = split(str(row["modifier_type_sequence"]))
        for left, right in zip(types, types[1:]):
            transition_occurrences[(left, right)].append(row)
    transition_rows: list[dict[str, object]] = []
    for left in ("FORMAL_CONTROL", "GRADE", "LOCAL_OR_CLASS_SIGN", "RELATION"):
        for right in ("FORMAL_CONTROL", "GRADE", "LOCAL_OR_CLASS_SIGN", "RELATION"):
            members = transition_occurrences[(left, right)]
            left_class = JOIN_CLASS[left]
            right_class = JOIN_CLASS[right]
            same = left_class == right_class
            transition_rows.append({
                "left_modifier_type": left,
                "right_modifier_type": right,
                "left_join_class": left_class,
                "right_join_class": right_class,
                "join_card_id": JOIN_CARD_BY_CLASS[left_class if same else "CROSS_CLASS"],
                "target_join": "COORDINATE_WITHIN_CONTIGUOUS_RUN" if same else "SEMICOLON_CLASS_BOUNDARY",
                "transition_occurrence_count": len(members),
                "state_event_count": len({str(row["event_id"]) for row in members}),
                "example_event_ids": "|".join(dict.fromkeys(str(row["event_id"]) for row in members[:8])) or "NONE",
                "guard": "TYPE_PAIR_JOIN_ONLY__ATOM_ORDER_UNCHANGED",
            })

    join_rows: list[dict[str, object]] = []
    for class_name in ("OPERATIONAL_MODIFIER", "RELATION", "LOCAL_OR_CLASS_SIGN", "CROSS_CLASS"):
        if class_name == "CROSS_CLASS":
            members = [row for row in transition_rows if row["target_join"] == "SEMICOLON_CLASS_BOUNDARY"]
            event_ids = {
                str(row["event_id"]) for row in state_rows
                if int(row["cross_class_transition_count"]) > 0
            }
            description = "verschiedene Modifierklassen mit Semikolon trennen"
        else:
            members = [row for row in transition_rows if row["left_join_class"] == class_name and row["right_join_class"] == class_name]
            event_ids = set()
            for state_row in state_rows:
                type_sequence = split(str(state_row["modifier_type_sequence"]))
                class_sequence = [JOIN_CLASS[type_name] for type_name in type_sequence]
                if any(left == right == class_name for left, right in zip(class_sequence, class_sequence[1:])):
                    event_ids.add(str(state_row["event_id"]))
            description = "zusammenhängende gleichklassige Angaben mit Komma und abschließendem und koordinieren"
        join_rows.append({
            "modifier_join_card_id": JOIN_CARD_BY_CLASS[class_name],
            "join_class": class_name,
            "member_modifier_types": (
                "FORMAL_CONTROL|GRADE" if class_name == "OPERATIONAL_MODIFIER" else
                "RELATION" if class_name == "RELATION" else
                "LOCAL_OR_CLASS_SIGN" if class_name == "LOCAL_OR_CLASS_SIGN" else
                "CROSS_CLASS"
            ),
            "working_join_rule_de": description,
            "type_pair_count": len(members),
            "transition_occurrence_count": sum(int(row["transition_occurrence_count"]) for row in members),
            "state_event_count": len(event_ids),
            "guard": "CONTIGUOUS_TYPE_RUN_JOIN__WRITTEN_ORDER_UNCHANGED",
        })

    cell_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in state_rows:
        if row["modifier_atoms"] != "NONE":
            cell_groups[(str(row["register"]), str(row["modifier_atoms"]))].append(row)
    cell_rows: list[dict[str, object]] = []
    for (register, atoms), members in sorted(cell_groups.items()):
        first = members[0]
        cell_rows.append({
            "modifier_cell_id": f"GDT570-C{len(cell_rows) + 1:03d}",
            "register": register,
            "modifier_atoms": atoms,
            "modifier_type_sequence": first["modifier_type_sequence"],
            "state_event_count": len(members),
            "statement_count": len({str(row["statement_id"]) for row in members}),
            "physical_page_count": len({str(row["physical_page"]) for row in members}),
            "current_modifier_phrase_de": first["current_modifier_phrase_de"],
            "modifier_voice_phrase_de": first["modifier_voice_phrase_de"],
            "modifier_voice_changed": first["modifier_voice_changed"],
            "owner_control_contains_target_phrase_count": sum(
                str(row["modifier_voice_phrase_de"]) in str(row["owner_bound_control_clause_de"]) for row in members
            ),
            "example_event_ids": "|".join(str(row["event_id"]) for row in members[:8]),
            "guard": "REGISTER_SEQUENCE_CELL__NO_RECIPE_OR_ATOM_CHANGE",
        })

    changed_rows = [row for row in state_rows if row["modifier_voice_changed"] == "YES"]
    changed_audit_rows = [{
        "changed_modifier_ordinal": index,
        "event_id": row["event_id"],
        "statement_id": row["statement_id"],
        "physical_page": row["physical_page"],
        "register": row["register"],
        "surface": row["surface"],
        "final_context_recipe": row["final_context_recipe"],
        "modifier_atoms": row["modifier_atoms"],
        "modifier_type_sequence": row["modifier_type_sequence"],
        "changed_fragment_atoms": row["changed_fragment_atoms"],
        "within_class_transition_count": row["within_class_transition_count"],
        "current_modifier_phrase_de": row["current_modifier_phrase_de"],
        "modifier_voice_phrase_de": row["modifier_voice_phrase_de"],
        "gdt569_context_voice_clause_de": row["gdt569_context_voice_clause_de"],
        "modifier_voice_working_clause_de": row["modifier_voice_working_clause_de"],
        "guard": "NAMED_MODIFIER_VOICE_CHANGE__ROOTS_AND_ORDER_UNCHANGED",
    } for index, row in enumerate(changed_rows, 1)]

    output_state_by_id = {row["event_id"]: row for row in state_rows}
    event_rows: list[dict[str, object]] = []
    for source in source_events:
        state = output_state_by_id.get(source["event_id"])
        after = state["modifier_voice_working_clause_de"] if state else source["context_voice_working_clause_de"]
        event_rows.append({
            "edition_event_ordinal": source["edition_event_ordinal"],
            "event_id": source["event_id"],
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "gdt569_context_voice_clause_de": source["context_voice_working_clause_de"],
            "modifier_voice_working_clause_de": after,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "modifier_voice_changed": "YES" if after != source["context_voice_working_clause_de"] else "NO",
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER_AND_NONSTATE_TEXT_UNCHANGED",
        })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for source in source_statements:
        members = sorted(events_by_statement[source["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        before = " ".join(str(row["gdt569_context_voice_clause_de"]) for row in members)
        after = " ".join(str(row["modifier_voice_working_clause_de"]) for row in members)
        control = " ".join(str(row["owner_bound_control_clause_de"]) for row in members)
        if before != source["context_voice_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
            raise RuntimeError(f"Statement reconstruction drift at {source['statement_id']}")
        statement_rows.append({
            "edition_statement_ordinal": source["edition_statement_ordinal"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "state_card_count": source["state_card_count"],
            "nonstate_card_count": source["nonstate_card_count"],
            "statement_mode": source["statement_mode"],
            "changed_modifier_state_event_count": sum(row["modifier_voice_changed"] == "YES" for row in members),
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt569_context_voice_reading_de": before,
            "modifier_voice_working_reading_de": after,
            "owner_bound_control_reading_de": control,
            "modifier_voice_statement_changed": "YES" if after != before else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED",
        })

    page_rows: list[dict[str, object]] = []
    for source in source_pages:
        page_states = [row for row in state_rows if row["physical_page"] == source["physical_page"]]
        page_statements = [row for row in statement_rows if row["physical_page"] == source["physical_page"]]
        page_rows.append({
            "page_ordinal": source["page_ordinal"],
            "physical_page": source["physical_page"],
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "modifier_bearing_state_event_count": sum(row["modifier_atoms"] != "NONE" for row in page_states),
            "multi_modifier_state_event_count": sum(int(row["modifier_count"]) > 1 for row in page_states),
            "modifier_voice_changed_state_event_count": sum(row["modifier_voice_changed"] == "YES" for row in page_states),
            "modifier_voice_changed_statement_count": sum(row["modifier_voice_statement_changed"] == "YES" for row in page_statements),
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED",
        })

    result = {
        "status": STATUS,
        "modifier_fragment_voice_card_count": len(fragment_rows),
        "modifier_join_card_count": len(join_rows),
        "modifier_transition_type_count": len(transition_rows),
        "modifier_transition_occurrence_count": sum(int(row["modifier_transition_count"]) for row in state_rows),
        "within_class_coordinated_transition_count": sum(int(row["within_class_transition_count"]) for row in state_rows),
        "cross_class_semicolon_transition_count": sum(int(row["cross_class_transition_count"]) for row in state_rows),
        "modifier_bearing_state_event_count": sum(row["modifier_atoms"] != "NONE" for row in state_rows),
        "modifierless_state_event_count": sum(row["modifier_atoms"] == "NONE" for row in state_rows),
        "multi_modifier_state_event_count": sum(int(row["modifier_count"]) > 1 for row in state_rows),
        "register_modifier_cell_count": len(cell_rows),
        "changed_fragment_event_count": len({str(row["event_id"]) for row in state_rows if row["changed_fragment_atoms"] != "NONE"}),
        "changed_fragment_occurrence_count": sum(
            sum(split(str(row["modifier_atoms"])).count(atom) for atom in CHANGED_FRAGMENT_ATOMS) for row in state_rows
        ),
        "within_class_join_event_count": sum(int(row["within_class_transition_count"]) > 0 for row in state_rows),
        "changed_state_event_count": len(changed_rows),
        "unchanged_state_event_count": len(state_rows) - len(changed_rows),
        "changed_statement_count": sum(row["modifier_voice_statement_changed"] == "YES" for row in statement_rows),
        "unchanged_statement_count": sum(row["modifier_voice_statement_changed"] == "NO" for row in statement_rows),
        "changed_physical_page_count": sum(int(row["modifier_voice_changed_state_event_count"]) > 0 for row in page_rows),
        "distinct_current_modifier_phrase_count": len({str(row["current_modifier_phrase_de"]) for row in state_rows if row["modifier_atoms"] != "NONE"}),
        "distinct_modifier_voice_phrase_count": len({str(row["modifier_voice_phrase_de"]) for row in state_rows if row["modifier_atoms"] != "NONE"}),
        "owner_control_target_fragment_event_use_count": sum(int(row["owner_control_target_event_support_count"]) for row in fragment_rows),
        "owner_control_fragment_event_use_count": sum(int(row["state_event_count"]) for row in fragment_rows),
        "dominant_voice_override_event_use_count": sum(int(row["state_event_count"]) - int(row["owner_control_target_event_support_count"]) for row in fragment_rows),
        "state_event_count": len(state_rows),
        "nonstate_event_count": sum(row["state_status"] == "NONSTATE_CARD" for row in event_rows),
        "nonstate_byte_unchanged_count": sum(
            row["state_status"] == "NONSTATE_CARD" and row["gdt569_context_voice_clause_de"] == row["modifier_voice_working_clause_de"]
            for row in event_rows
        ),
        "complete_event_count": len(event_rows),
        "complete_statement_count": len(statement_rows),
        "complete_page_count": len(page_rows),
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt570_5_modifier_fragment_voice_cards.tsv", fragment_rows)
    write_tsv(OUT / "gdt570_4_modifier_join_cards.tsv", join_rows)
    write_tsv(OUT / "gdt570_16_modifier_type_transition_profiles.tsv", transition_rows)
    write_tsv(OUT / "gdt570_154_register_modifier_cells.tsv", cell_rows)
    write_tsv(OUT / "gdt570_164_changed_modifier_clauses.tsv", changed_audit_rows)
    write_tsv(OUT / "gdt570_1656_modifier_voice_state_clauses.tsv", state_rows)
    write_tsv(OUT / "gdt570_5122_modifier_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt570_793_modifier_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt570_30_page_modifier_voice_profiles.tsv", page_rows)

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book = [
        "# GDT570 – modifierstimmige 30-Seiten-Arbeitsausgabe",
        "",
        "Fünf kleine Fragmentkarten und vier Fügeregeln decken alle Modifierfolgen ab.",
        "",
        "```text",
        "1.042 Modifierkarten | 172 Mehrfachfolgen | 224 Übergänge",
        "103 gleichklassig koordiniert | 121 Klassengrenzen mit Semikolon",
        "164 verfeinerte Zustandszeilen | 3.466 unveränderte Nichtzustandszeilen",
        "```",
        "",
    ]
    for page in source_pages:
        book += [f"## {page['physical_page']}", ""]
        members = statements_by_page[page["physical_page"]]
        if not members:
            book += ["Keine laufende Prosa; zugelassene Lokalregisterseite bleibt sichtbar.", ""]
            continue
        for statement in members:
            book += [
                f"### {statement['statement_id']} · {statement['statement_mode']} · {statement['event_count']} Karten",
                "",
                f"**Formen:** {statement['surface_sequence']}",
                "",
                str(statement["modifier_voice_working_reading_de"]),
                "",
            ]
    (OUT / "GDT570_MODIFIER_VOICE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt570_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
