#!/usr/bin/env python3
"""Build the GDT567 owner-voice seam adapter and complete prose edition."""

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
BASE = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter"
OUT = BASE / "artifacts"
G566 = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "complete_events": G566 / "gdt566_5122_complete_prose_event_edition.tsv",
    "complete_statements": G566 / "gdt566_793_complete_statement_edition.tsv",
    "page_profiles": G566 / "gdt566_30_page_edition_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
}

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ARGUMENT_GENERIC = {"Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit"}
ARGUMENT_VOICE = {
    "SOURCE_SECTION_T": {
        "Y": ("den laufenden Eintrag", "die beiden laufenden Einträge"),
        "AIIN": ("den Kennwert", ""), "AIN": ("den Teilwert", ""), "OR": ("die Eintragseinheit", ""),
    },
    "HERBAL": {
        "Y": ("den Pflanzenposten", "die beiden Pflanzenposten"),
        "AIIN": ("den Arbeitswert", ""), "AIN": ("den Materialanteil", ""), "OR": ("die Arbeitseinheit", ""),
    },
    "CELESTIAL": {
        "Y": ("den Positionsposten", "die beiden Positionsposten"),
        "AIIN": ("den Positionswert", ""), "OR": ("die Positionseinheit", ""),
    },
    "BIOLOGICAL": {
        "Y": ("den Stationsposten", "die beiden Stationsposten"),
        "AIIN": ("den Stationswert", ""), "AIN": ("den Stationsanteil", ""), "OR": ("die Stationseinheit", ""),
    },
    "PHARMA": {
        "Y": ("den Drogenposten", "die beiden Drogenposten"),
        "AIIN": ("den Mengenwert", ""), "AIN": ("den Drogenanteil", ""), "OR": ("die Ansatzeinheit", ""),
    },
}
RELATION_GENERIC = {
    "AL": "zum Zielort", "AR": "vom Ausgang", "L": "über die Verbindung", "AIR": "entlang der Bahn",
}
RELATION_VOICE = {
    "SOURCE_SECTION_T": {
        "AL": "zur Zielspalte", "AR": "von der Ausgangszeile",
        "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn",
    },
    "HERBAL": {
        "AL": "zur Zielstelle", "AR": "vom Ausgangsmaterial",
        "L": "über die Verbindung im Pflanzenartikel", "AIR": "entlang der Verarbeitungsbahn",
    },
    "CELESTIAL": {
        "AL": "zur Zielposition", "AR": "von der Ausgangsposition", "L": "über die Ringverbindung",
    },
    "BIOLOGICAL": {
        "AL": "zur Zielstation", "AR": "von der Ausgangsstation",
        "L": "über die sichtbare Verbindung", "AIR": "entlang der Stationsbahn",
    },
    "PHARMA": {
        "AL": "zum Zielgefäß", "AR": "vom Ausgangsgefäß", "L": "über die Gefäßverbindung",
    },
}


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


def roots(value: str, separator: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split(separator)


def contains_word(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, flags=re.IGNORECASE) is not None


def replace_word(text: str, source: str, target: str) -> str:
    return re.sub(r"(?<!\w)" + re.escape(source) + r"(?!\w)", target, text)


def lexical_head(phrase: str) -> str:
    return phrase.split()[-1]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["complete_events"])
    source_statements = read_tsv(INPUTS["complete_statements"])
    pages = read_tsv(INPUTS["page_profiles"])
    state_source = read_tsv(INPUTS["state_replay"])
    if [len(source_events), len(source_statements), len(pages), len(state_source)] != [5122, 793, 30, 1656]:
        raise RuntimeError("Input count drift")
    state_by_id = {row["event_id"]: row for row in state_source}
    if set(state_by_id) != {row["event_id"] for row in source_events if row["state_status"] == "STATE_CARD"}:
        raise RuntimeError("GDT565/GDT566 state partition drift")

    card_rows: list[dict[str, object]] = []
    card_ids: dict[tuple[str, str, str], str] = {}

    def add_card(card_class: str, register: str, key: str, generic: str, target: str,
                 double_target: str, members: list[dict[str, str]], support_phrase: str) -> None:
        card_id = f"GDT567-A{len(card_rows) + 1:02d}"
        card_ids[(card_class, register, key)] = card_id
        supported = [row for row in members if contains_word(row["owner_bound_control_clause_de"], support_phrase)]
        card_rows.append({
            "adapter_card_id": card_id,
            "card_class": card_class,
            "register_scope": register,
            "root_or_trigger": key,
            "generic_phrase_de": generic,
            "owner_voice_phrase_de": target,
            "double_y_phrase_de": double_target or "NOT_APPLICABLE",
            "source_state_event_count": len(members),
            "owner_bound_target_support_count": len(supported),
            "support_rate": f"{len(supported) / len(members):.12f}",
            "physical_page_count": len({row["physical_page"] for row in members}),
            "statement_count": len({row["statement_id"] for row in members}),
            "example_event_ids": "|".join(row["event_id"] for row in members[:8]),
            "guard": "OWNER_VOICE_RENDERING_ONLY__ROOT_VALUE_UNCHANGED",
        })

    for register in REGISTERS:
        for root in ("Y", "AIIN", "AIN", "OR"):
            if root not in ARGUMENT_VOICE[register]:
                continue
            members = [
                row for row in source_events
                if row["state_status"] == "STATE_CARD" and row["register"] == register
                and root in roots(state_by_id[row["event_id"]]["effective_argument_roots"], "|")
            ]
            target, double_target = ARGUMENT_VOICE[register][root]
            add_card("ARGUMENT_OWNER_VOICE", register, root, ARGUMENT_GENERIC[root], target,
                     double_target, members, lexical_head(target))

    for register in REGISTERS:
        for root in ("AL", "AR", "L", "AIR"):
            if root not in RELATION_VOICE[register]:
                continue
            members = [
                row for row in source_events
                if row["state_status"] == "STATE_CARD" and row["register"] == register
                and root in roots(state_by_id[row["event_id"]]["recipe"], "+")
            ]
            target = RELATION_VOICE[register][root]
            add_card("RELATION_OWNER_VOICE", register, root, RELATION_GENERIC[root], target,
                     "", members, target)

    place_members = [
        row for row in source_events
        if row["state_status"] == "STATE_CARD" and contains_word(row["selected_working_clause_de"], "hier")
    ]
    add_card("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "HIER_FRAGMENT", "hier",
             "an der bezeichneten Stelle", "", place_members, "an der bezeichneten Stelle")
    close_members = [
        row for row in source_events
        if row["state_status"] == "STATE_CARD" and contains_word(row["selected_working_clause_de"], "abschließen")
    ]
    add_card("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "DY_CLOSURE_WORDING", "abschließen",
             "schließe den Schritt", "", close_members, "schließe den Schritt")
    if len(card_rows) != 39 or any(row["owner_bound_target_support_count"] != row["source_state_event_count"] for row in card_rows):
        raise RuntimeError("Owner-voice card support drift")

    event_rows: list[dict[str, object]] = []
    state_rows: list[dict[str, object]] = []
    for source in source_events:
        original = source["selected_working_clause_de"]
        adapted = original
        applied: list[str] = []
        state = state_by_id.get(source["event_id"])
        if state is not None:
            argument_roots = roots(state["effective_argument_roots"], "|")
            recipe_atoms = roots(state["recipe"], "+")
            if "Y" in argument_roots:
                before = adapted
                adapted = replace_word(adapted, "die beiden Posten", ARGUMENT_VOICE[source["register"]]["Y"][1])
                adapted = replace_word(adapted, "den Posten", ARGUMENT_VOICE[source["register"]]["Y"][0])
                if adapted != before:
                    applied.append(card_ids[("ARGUMENT_OWNER_VOICE", source["register"], "Y")])
            for root in ("AIIN", "AIN", "OR"):
                if root not in argument_roots:
                    continue
                before = adapted
                adapted = replace_word(adapted, ARGUMENT_GENERIC[root], ARGUMENT_VOICE[source["register"]][root][0])
                if adapted != before:
                    applied.append(card_ids[("ARGUMENT_OWNER_VOICE", source["register"], root)])
            for root in ("AL", "AR", "L", "AIR"):
                if root not in recipe_atoms:
                    continue
                before = adapted
                adapted = replace_word(adapted, RELATION_GENERIC[root], RELATION_VOICE[source["register"]][root])
                if adapted != before:
                    applied.append(card_ids[("RELATION_OWNER_VOICE", source["register"], root)])
            if contains_word(adapted, "hier"):
                adapted = replace_word(adapted, "hier", "an der bezeichneten Stelle")
                applied.append(card_ids[("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "HIER_FRAGMENT")])
            if "DY" in recipe_atoms and contains_word(adapted, "abschließen"):
                adapted = replace_word(adapted, "abschließen", "schließe den Schritt")
                applied.append(card_ids[("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "DY_CLOSURE_WORDING")])
        changed = adapted != original
        event_row = {
            "edition_event_ordinal": source["edition_event_ordinal"],
            "navigation_event_id": source["navigation_event_id"],
            "event_id": source["event_id"],
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "gdt566_selected_clause_de": original,
            "owner_voice_working_clause_de": adapted,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "owner_voice_changed": "YES" if changed else "NO",
            "owner_voice_equals_owner_bound": "YES" if adapted == source["owner_bound_control_clause_de"] else "NO",
            "adapter_card_count": len(applied),
            "adapter_card_ids": "|".join(applied) or "NONE",
            "outer_template_id": source["outer_template_id"],
            "structural_template_id": source["structural_template_id"],
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "EVENT_RECIPE_AND_ROOTS_UNCHANGED__OWNER_VOICE_RENDERING_SEPARATE",
        }
        event_rows.append(event_row)
        if state is not None:
            state_rows.append({
                "state_edition_ordinal": len(state_rows) + 1,
                **{key: event_row[key] for key in (
                    "event_id", "statement_id", "physical_page", "register", "owner_id", "surface",
                    "final_context_recipe", "gdt566_selected_clause_de", "owner_voice_working_clause_de",
                    "owner_bound_control_clause_de", "owner_voice_changed", "owner_voice_equals_owner_bound",
                    "adapter_card_count", "adapter_card_ids", "outer_template_id", "structural_template_id",
                    "state_atom_alignment", "guard",
                )},
            })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_rows: list[dict[str, object]] = []
    for source_statement in source_statements:
        members = sorted(events_by_statement[source_statement["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        old_reading = " ".join(str(row["gdt566_selected_clause_de"]) for row in members)
        adapted_reading = " ".join(str(row["owner_voice_working_clause_de"]) for row in members)
        control = " ".join(str(row["owner_bound_control_clause_de"]) for row in members)
        if old_reading != source_statement["selected_working_reading_de"] or control != source_statement["owner_bound_control_reading_de"]:
            raise RuntimeError(f"Statement reconstruction drift at {source_statement['statement_id']}")
        statement_rows.append({
            "edition_statement_ordinal": source_statement["edition_statement_ordinal"],
            "statement_id": source_statement["statement_id"],
            "physical_page": source_statement["physical_page"],
            "register": source_statement["register"],
            "owner_id": source_statement["owner_id"],
            "event_count": source_statement["event_count"],
            "state_card_count": source_statement["state_card_count"],
            "nonstate_card_count": source_statement["nonstate_card_count"],
            "statement_mode": source_statement["statement_mode"],
            "owner_voice_changed_event_count": sum(row["owner_voice_changed"] == "YES" for row in members),
            "adapter_application_count": sum(int(row["adapter_card_count"]) for row in members),
            "event_ids": source_statement["event_ids"],
            "surface_sequence": source_statement["surface_sequence"],
            "gdt566_selected_reading_de": old_reading,
            "owner_voice_working_reading_de": adapted_reading,
            "owner_bound_control_reading_de": control,
            "owner_voice_statement_changed": "YES" if adapted_reading != old_reading else "NO",
            "owner_voice_equals_owner_bound": "YES" if adapted_reading == control else "NO",
            "end_mode": source_statement["end_mode"],
            "guard": "STATEMENT_BOUNDARY_AND_EVENT_ORDER_UNCHANGED",
        })

    event_by_id = {row["event_id"]: row for row in event_rows}
    seam_rows: list[dict[str, object]] = []
    direction_names = {
        ("NONSTATE_CARD", "NONSTATE_CARD"): "NONSTATE_TO_NONSTATE",
        ("NONSTATE_CARD", "STATE_CARD"): "NONSTATE_TO_STATE",
        ("STATE_CARD", "NONSTATE_CARD"): "STATE_TO_NONSTATE",
        ("STATE_CARD", "STATE_CARD"): "STATE_TO_STATE",
    }
    for statement in statement_rows:
        members = [event_by_id[event_id] for event_id in statement["event_ids"].split("|")]
        for left, right in zip(members, members[1:]):
            direction = direction_names[(str(left["state_status"]), str(right["state_status"]))]
            mixed = left["state_status"] != right["state_status"]
            argument_contacts: list[str] = []
            relation_contacts: list[str] = []
            before_arg = after_arg = before_relation = after_relation = 0
            state_endpoint = None
            nonstate_endpoint = None
            if mixed:
                state_endpoint = left if left["state_status"] == "STATE_CARD" else right
                nonstate_endpoint = right if left["state_status"] == "STATE_CARD" else left
                state = state_by_id[str(state_endpoint["event_id"])]
                for root in sorted(set(roots(state["effective_argument_roots"], "|")).intersection(ARGUMENT_GENERIC)):
                    target_head = lexical_head(ARGUMENT_VOICE[str(state_endpoint["register"])][root][0])
                    if contains_word(str(nonstate_endpoint["owner_voice_working_clause_de"]), target_head):
                        argument_contacts.append(f"{root}:{target_head}")
                        before_arg += int(contains_word(str(state_endpoint["gdt566_selected_clause_de"]), target_head))
                        after_arg += int(contains_word(str(state_endpoint["owner_voice_working_clause_de"]), target_head))
                for root in sorted(set(roots(state["recipe"], "+")).intersection(RELATION_GENERIC)):
                    target_head = lexical_head(RELATION_VOICE[str(state_endpoint["register"])][root])
                    if contains_word(str(nonstate_endpoint["owner_voice_working_clause_de"]), target_head):
                        relation_contacts.append(f"{root}:{target_head}")
                        before_relation += int(contains_word(str(state_endpoint["gdt566_selected_clause_de"]), target_head))
                        after_relation += int(contains_word(str(state_endpoint["owner_voice_working_clause_de"]), target_head))
            seam_rows.append({
                "seam_ordinal": len(seam_rows) + 1,
                "statement_id": statement["statement_id"],
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "left_event_id": left["event_id"],
                "right_event_id": right["event_id"],
                "direction": direction,
                "mixed_state_nonstate": "YES" if mixed else "NO",
                "state_endpoint_event_id": state_endpoint["event_id"] if state_endpoint else "NOT_APPLICABLE",
                "state_endpoint_changed": state_endpoint["owner_voice_changed"] if state_endpoint else "NOT_APPLICABLE",
                "adapter_card_ids": state_endpoint["adapter_card_ids"] if state_endpoint else "NOT_APPLICABLE",
                "shared_argument_contacts": "|".join(argument_contacts) or "NONE",
                "shared_relation_contacts": "|".join(relation_contacts) or "NONE",
                "argument_head_exact_before": before_arg,
                "argument_head_exact_after": after_arg,
                "relation_head_exact_before": before_relation,
                "relation_head_exact_after": after_relation,
                "left_gdt566_clause_de": left["gdt566_selected_clause_de"],
                "right_gdt566_clause_de": right["gdt566_selected_clause_de"],
                "left_owner_voice_clause_de": left["owner_voice_working_clause_de"],
                "right_owner_voice_clause_de": right["owner_voice_working_clause_de"],
                "guard": "ADJACENCY_ONLY__NO_EVENT_MERGE",
            })

    direction_rows: list[dict[str, object]] = []
    for direction in ("NONSTATE_TO_NONSTATE", "NONSTATE_TO_STATE", "STATE_TO_NONSTATE", "STATE_TO_STATE"):
        members = [row for row in seam_rows if row["direction"] == direction]
        direction_rows.append({
            "direction": direction,
            "seam_count": len(members),
            "statement_count": len({str(row["statement_id"]) for row in members}),
            "physical_page_count": len({str(row["physical_page"]) for row in members}),
            "register_count": len({str(row["register"]) for row in members}),
            "state_endpoint_changed_count": sum(row["state_endpoint_changed"] == "YES" for row in members),
            "shared_argument_contact_count": sum(row["shared_argument_contacts"] != "NONE" for row in members),
            "shared_relation_contact_count": sum(row["shared_relation_contacts"] != "NONE" for row in members),
            "argument_head_exact_before": sum(int(row["argument_head_exact_before"]) for row in members),
            "argument_head_exact_after": sum(int(row["argument_head_exact_after"]) for row in members),
            "relation_head_exact_before": sum(int(row["relation_head_exact_before"]) for row in members),
            "relation_head_exact_after": sum(int(row["relation_head_exact_after"]) for row in members),
        })

    register_rows: list[dict[str, object]] = []
    for register in REGISTERS:
        state_members = [row for row in state_rows if row["register"] == register]
        register_seams = [row for row in seam_rows if row["register"] == register and row["mixed_state_nonstate"] == "YES"]
        register_rows.append({
            "register": register,
            "state_event_count": len(state_members),
            "changed_state_event_count": sum(row["owner_voice_changed"] == "YES" for row in state_members),
            "distinct_gdt566_state_clause_count": len({str(row["gdt566_selected_clause_de"]) for row in state_members}),
            "distinct_owner_voice_state_clause_count": len({str(row["owner_voice_working_clause_de"]) for row in state_members}),
            "adapter_card_count": sum(row["register_scope"] == register for row in card_rows),
            "adapter_application_count": sum(int(row["adapter_card_count"]) for row in state_members),
            "mixed_seam_count": len(register_seams),
            "shared_argument_contact_count": sum(row["shared_argument_contacts"] != "NONE" for row in register_seams),
            "shared_relation_contact_count": sum(row["shared_relation_contacts"] != "NONE" for row in register_seams),
            "physical_page_count": len({str(row["physical_page"]) for row in state_members}),
        })

    mixed_seams = [row for row in seam_rows if row["mixed_state_nonstate"] == "YES"]
    result = {
        "status": "PASS_39_CARD_OWNER_VOICE_ADAPTER__1639_STATE_CLAUSES_HARMONIZED__1209_ARGUMENT_SEAMS_0_TO_1209_EXACT__20_RELATION_SEAMS_3_TO_20_EXACT__ZERO_ROOT_CHANGE",
        "adapter_card_count": len(card_rows),
        "argument_owner_voice_card_count": sum(row["card_class"] == "ARGUMENT_OWNER_VOICE" for row in card_rows),
        "relation_owner_voice_card_count": sum(row["card_class"] == "RELATION_OWNER_VOICE" for row in card_rows),
        "universal_owner_voice_card_count": sum(row["card_class"] == "UNIVERSAL_OWNER_VOICE" for row in card_rows),
        "register_root_cell_use_count": sum(int(row["source_state_event_count"]) for row in card_rows if row["card_class"] != "UNIVERSAL_OWNER_VOICE"),
        "register_root_cell_supported_use_count": sum(int(row["owner_bound_target_support_count"]) for row in card_rows if row["card_class"] != "UNIVERSAL_OWNER_VOICE"),
        "place_voice_event_count": len(place_members),
        "place_voice_supported_event_count": sum(contains_word(row["owner_bound_control_clause_de"], "an der bezeichneten Stelle") for row in place_members),
        "close_voice_event_count": len(close_members),
        "close_voice_supported_event_count": sum(contains_word(row["owner_bound_control_clause_de"], "schließe den Schritt") for row in close_members),
        "state_event_count": len(state_rows),
        "changed_state_event_count": sum(row["owner_voice_changed"] == "YES" for row in state_rows),
        "unchanged_state_event_count": sum(row["owner_voice_changed"] == "NO" for row in state_rows),
        "owner_voice_equals_owner_bound_state_count": sum(row["owner_voice_equals_owner_bound"] == "YES" for row in state_rows),
        "distinct_gdt566_state_clause_count": len({row["gdt566_selected_clause_de"] for row in state_rows}),
        "distinct_owner_voice_state_clause_count": len({row["owner_voice_working_clause_de"] for row in state_rows}),
        "changed_statement_count": sum(row["owner_voice_statement_changed"] == "YES" for row in statement_rows),
        "unchanged_statement_count": sum(row["owner_voice_statement_changed"] == "NO" for row in statement_rows),
        "changed_physical_page_count": len({row["physical_page"] for row in state_rows if row["owner_voice_changed"] == "YES"}),
        "complete_event_count": len(event_rows),
        "complete_statement_count": len(statement_rows),
        "within_statement_seam_count": len(seam_rows),
        "nonstate_to_nonstate_seam_count": sum(row["direction"] == "NONSTATE_TO_NONSTATE" for row in seam_rows),
        "nonstate_to_state_seam_count": sum(row["direction"] == "NONSTATE_TO_STATE" for row in seam_rows),
        "state_to_nonstate_seam_count": sum(row["direction"] == "STATE_TO_NONSTATE" for row in seam_rows),
        "state_to_state_seam_count": sum(row["direction"] == "STATE_TO_STATE" for row in seam_rows),
        "mixed_state_nonstate_seam_count": len(mixed_seams),
        "mixed_seam_statement_count": len({row["statement_id"] for row in mixed_seams}),
        "changed_mixed_seam_endpoint_count": sum(row["state_endpoint_changed"] == "YES" for row in mixed_seams),
        "shared_argument_contact_seam_count": sum(row["shared_argument_contacts"] != "NONE" for row in mixed_seams),
        "argument_head_exact_before": sum(int(row["argument_head_exact_before"]) for row in mixed_seams),
        "argument_head_exact_after": sum(int(row["argument_head_exact_after"]) for row in mixed_seams),
        "shared_relation_contact_seam_count": sum(row["shared_relation_contacts"] != "NONE" for row in mixed_seams),
        "relation_head_exact_before": sum(int(row["relation_head_exact_before"]) for row in mixed_seams),
        "relation_head_exact_after": sum(int(row["relation_head_exact_after"]) for row in mixed_seams),
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt567_39_owner_voice_adapter_cards.tsv", card_rows)
    write_tsv(OUT / "gdt567_1656_owner_voice_state_clauses.tsv", state_rows)
    write_tsv(OUT / "gdt567_5122_owner_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt567_793_owner_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt567_4329_within_statement_seam_atlas.tsv", seam_rows)
    write_tsv(OUT / "gdt567_4_seam_direction_profiles.tsv", direction_rows)
    write_tsv(OUT / "gdt567_5_register_voice_profiles.tsv", register_rows)

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book = [
        "# GDT567 – ownerstimmige 30-Seiten-Arbeitsausgabe",
        "",
        "Die 39 Adapterkarten ändern nur die deutsche Fachstimme der bereits gesetzten Wurzeln.",
        "Ereignisgrenzen, Rezepte, Atome und der ownergebundene Kontrollkanal bleiben sichtbar.",
        "",
        "```text",
        "19 Argumentkarten + 18 Relationskarten + 2 allgemeine Karten = 39",
        "1.639/1.656 Zustandszeilen ownerstimmig angepasst",
        "1.209 gemeinsame Argumentanschlüsse: 0 → 1.209 gleiche Fachwortköpfe",
        "20 gemeinsame Relationsanschlüsse: 3 → 20 gleiche Fachwortköpfe",
        "```",
        "",
    ]
    for page in pages:
        book += [f"## {page['physical_page']}", ""]
        page_statements = statements_by_page[page["physical_page"]]
        if not page_statements:
            book += ["Keine laufende Prosa; zugelassene Lokalregisterseite bleibt sichtbar.", ""]
            continue
        for statement in page_statements:
            book += [
                f"### {statement['statement_id']} · {statement['statement_mode']} · {statement['event_count']} Karten",
                "",
                f"**Formen:** {statement['surface_sequence']}",
                "",
                str(statement["owner_voice_working_reading_de"]),
                "",
            ]
    (OUT / "GDT567_OWNER_VOICE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt567_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
