#!/usr/bin/env python3
"""Independently validate the GDT567 owner-voice seam adapter."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BASE = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt567_validation.json"
G566 = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "complete_events": G566 / "gdt566_5122_complete_prose_event_edition.tsv",
    "complete_statements": G566 / "gdt566_793_complete_statement_edition.tsv",
    "page_profiles": G566 / "gdt566_30_page_edition_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
}
ARTIFACTS = {
    "cards": OUT / "gdt567_39_owner_voice_adapter_cards.tsv",
    "states": OUT / "gdt567_1656_owner_voice_state_clauses.tsv",
    "events": OUT / "gdt567_5122_owner_voice_event_edition.tsv",
    "statements": OUT / "gdt567_793_owner_voice_statement_edition.tsv",
    "seams": OUT / "gdt567_4329_within_statement_seam_atlas.tsv",
    "directions": OUT / "gdt567_4_seam_direction_profiles.tsv",
    "registers": OUT / "gdt567_5_register_voice_profiles.tsv",
    "book": OUT / "GDT567_OWNER_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt567_result.json",
}
STATUS = "PASS_39_CARD_OWNER_VOICE_ADAPTER__1639_STATE_CLAUSES_HARMONIZED__1209_ARGUMENT_SEAMS_0_TO_1209_EXACT__20_RELATION_SEAMS_3_TO_20_EXACT__ZERO_ROOT_CHANGE"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ARG_GENERIC = {"Y": "den Posten", "AIIN": "den Wert", "AIN": "den Anteil", "OR": "die Einheit"}
ARG_VOICE = {
    "SOURCE_SECTION_T": {"Y": ("den laufenden Eintrag", "die beiden laufenden Einträge"), "AIIN": ("den Kennwert", ""), "AIN": ("den Teilwert", ""), "OR": ("die Eintragseinheit", "")},
    "HERBAL": {"Y": ("den Pflanzenposten", "die beiden Pflanzenposten"), "AIIN": ("den Arbeitswert", ""), "AIN": ("den Materialanteil", ""), "OR": ("die Arbeitseinheit", "")},
    "CELESTIAL": {"Y": ("den Positionsposten", "die beiden Positionsposten"), "AIIN": ("den Positionswert", ""), "OR": ("die Positionseinheit", "")},
    "BIOLOGICAL": {"Y": ("den Stationsposten", "die beiden Stationsposten"), "AIIN": ("den Stationswert", ""), "AIN": ("den Stationsanteil", ""), "OR": ("die Stationseinheit", "")},
    "PHARMA": {"Y": ("den Drogenposten", "die beiden Drogenposten"), "AIIN": ("den Mengenwert", ""), "AIN": ("den Drogenanteil", ""), "OR": ("die Ansatzeinheit", "")},
}
REL_GENERIC = {"AL": "zum Zielort", "AR": "vom Ausgang", "L": "über die Verbindung", "AIR": "entlang der Bahn"}
REL_VOICE = {
    "SOURCE_SECTION_T": {"AL": "zur Zielspalte", "AR": "von der Ausgangszeile", "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn"},
    "HERBAL": {"AL": "zur Zielstelle", "AR": "vom Ausgangsmaterial", "L": "über die Verbindung im Pflanzenartikel", "AIR": "entlang der Verarbeitungsbahn"},
    "CELESTIAL": {"AL": "zur Zielposition", "AR": "von der Ausgangsposition", "L": "über die Ringverbindung"},
    "BIOLOGICAL": {"AL": "zur Zielstation", "AR": "von der Ausgangsstation", "L": "über die sichtbare Verbindung", "AIR": "entlang der Stationsbahn"},
    "PHARMA": {"AL": "zum Zielgefäß", "AR": "vom Ausgangsgefäß", "L": "über die Gefäßverbindung"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def roots(value: str, separator: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split(separator)


def has(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE) is not None


def replace(text: str, source: str, target: str) -> str:
    return re.sub(r"(?<!\w)" + re.escape(source) + r"(?!\w)", target, text)


def head(phrase: str) -> str:
    return phrase.split()[-1]


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    src_events = read_tsv(INPUTS["complete_events"])
    src_statements = read_tsv(INPUTS["complete_statements"])
    src_pages = read_tsv(INPUTS["page_profiles"])
    src_states = read_tsv(INPUTS["state_replay"])
    cards = read_tsv(ARTIFACTS["cards"])
    states = read_tsv(ARTIFACTS["states"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    seams = read_tsv(ARTIFACTS["seams"])
    directions = read_tsv(ARTIFACTS["directions"])
    registers = read_tsv(ARTIFACTS["registers"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))
    check("input_counts", [len(src_events), len(src_statements), len(src_pages), len(src_states)] == [5122, 793, 30, 1656], [len(src_events), len(src_statements), len(src_pages), len(src_states)])
    check("artifact_counts", [len(cards), len(states), len(events), len(statements), len(seams), len(directions), len(registers)] == [39, 1656, 5122, 793, 4329, 4, 5], [len(cards), len(states), len(events), len(statements), len(seams), len(directions), len(registers)])
    pages_seen = {row["physical_page"] for row in src_pages + events + statements + states}
    check("sealed_pages_absent", not pages_seen.intersection({"f84", "f84r"}), sorted(pages_seen.intersection({"f84", "f84r"})))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("state_ordinals", [int(row["state_edition_ordinal"]) for row in states] == list(range(1, 1657)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("seam_ordinals", [int(row["seam_ordinal"]) for row in seams] == list(range(1, 4330)))

    state_by_id = {row["event_id"]: row for row in src_states}
    src_event_by_id = {row["event_id"]: row for row in src_events}
    event_by_id = {row["event_id"]: row for row in events}
    output_state_by_id = {row["event_id"]: row for row in states}
    src_statement_by_id = {row["statement_id"]: row for row in src_statements}
    check("keys_unique_exact", len(state_by_id) == len(output_state_by_id) == 1656 and len(src_event_by_id) == len(event_by_id) == 5122 and set(state_by_id) == set(output_state_by_id), [len(state_by_id), len(output_state_by_id), len(src_event_by_id), len(event_by_id)])
    check("state_partition_exact", set(state_by_id) == {row["event_id"] for row in src_events if row["state_status"] == "STATE_CARD"})

    expected_card_keys = []
    for register in REGISTERS:
        for root in ("Y", "AIIN", "AIN", "OR"):
            if root in ARG_VOICE[register]:
                expected_card_keys.append(("ARGUMENT_OWNER_VOICE", register, root))
    for register in REGISTERS:
        for root in ("AL", "AR", "L", "AIR"):
            if root in REL_VOICE[register]:
                expected_card_keys.append(("RELATION_OWNER_VOICE", register, root))
    expected_card_keys += [
        ("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "HIER_FRAGMENT"),
        ("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "DY_CLOSURE_WORDING"),
    ]
    card_keys = [(row["card_class"], row["register_scope"], row["root_or_trigger"]) for row in cards]
    check("card_ids_sequential", [row["adapter_card_id"] for row in cards] == [f"GDT567-A{i:02d}" for i in range(1, 40)])
    check("card_keys_exact", card_keys == expected_card_keys, card_keys)
    check("card_class_counts", Counter(row["card_class"] for row in cards) == Counter({"ARGUMENT_OWNER_VOICE": 19, "RELATION_OWNER_VOICE": 18, "UNIVERSAL_OWNER_VOICE": 2}), dict(Counter(row["card_class"] for row in cards)))
    card_id_by_key = {key: row["adapter_card_id"] for key, row in zip(card_keys, cards)}

    card_errors = []
    for row, key in zip(cards, expected_card_keys):
        card_class, register, root = key
        if card_class == "ARGUMENT_OWNER_VOICE":
            members = [event for event in src_events if event["state_status"] == "STATE_CARD" and event["register"] == register and root in roots(state_by_id[event["event_id"]]["effective_argument_roots"], "|")]
            generic = ARG_GENERIC[root]
            target, double_target = ARG_VOICE[register][root]
            support_phrase = head(target)
        elif card_class == "RELATION_OWNER_VOICE":
            members = [event for event in src_events if event["state_status"] == "STATE_CARD" and event["register"] == register and root in roots(state_by_id[event["event_id"]]["recipe"], "+")]
            generic = REL_GENERIC[root]
            target = REL_VOICE[register][root]
            double_target = ""
            support_phrase = target
        elif root == "HIER_FRAGMENT":
            members = [event for event in src_events if event["state_status"] == "STATE_CARD" and has(event["selected_working_clause_de"], "hier")]
            generic, target, double_target, support_phrase = "hier", "an der bezeichneten Stelle", "", "an der bezeichneten Stelle"
        else:
            members = [event for event in src_events if event["state_status"] == "STATE_CARD" and has(event["selected_working_clause_de"], "abschließen")]
            generic, target, double_target, support_phrase = "abschließen", "schließe den Schritt", "", "schließe den Schritt"
        supported = sum(has(event["owner_bound_control_clause_de"], support_phrase) for event in members)
        expected = {
            "generic_phrase_de": generic,
            "owner_voice_phrase_de": target,
            "double_y_phrase_de": double_target or "NOT_APPLICABLE",
            "source_state_event_count": str(len(members)),
            "owner_bound_target_support_count": str(supported),
            "support_rate": "1.000000000000",
        }
        bad = {field: [row[field], value] for field, value in expected.items() if row[field] != value}
        if supported != len(members):
            bad["support"] = [supported, len(members)]
        if bad:
            card_errors.append((key, bad))
    check("all_cards_reconstructed", not card_errors, card_errors[:5])
    check("register_root_use_count", sum(int(row["source_state_event_count"]) for row in cards if row["card_class"] != "UNIVERSAL_OWNER_VOICE") == 1807)
    check("universal_support_counts", [(row["source_state_event_count"], row["owner_bound_target_support_count"]) for row in cards[-2:]] == [("123", "123"), ("705", "705")], cards[-2:])

    def adapt(source: dict[str, str]) -> tuple[str, list[str]]:
        state = state_by_id.get(source["event_id"])
        if state is None:
            return source["selected_working_clause_de"], []
        text = source["selected_working_clause_de"]
        applied = []
        argument_roots = roots(state["effective_argument_roots"], "|")
        recipe_atoms = roots(state["recipe"], "+")
        if "Y" in argument_roots:
            before = text
            text = replace(text, "die beiden Posten", ARG_VOICE[source["register"]]["Y"][1])
            text = replace(text, "den Posten", ARG_VOICE[source["register"]]["Y"][0])
            if text != before:
                applied.append(card_id_by_key[("ARGUMENT_OWNER_VOICE", source["register"], "Y")])
        for root in ("AIIN", "AIN", "OR"):
            if root in argument_roots:
                before = text
                text = replace(text, ARG_GENERIC[root], ARG_VOICE[source["register"]][root][0])
                if text != before:
                    applied.append(card_id_by_key[("ARGUMENT_OWNER_VOICE", source["register"], root)])
        for root in ("AL", "AR", "L", "AIR"):
            if root in recipe_atoms:
                before = text
                text = replace(text, REL_GENERIC[root], REL_VOICE[source["register"]][root])
                if text != before:
                    applied.append(card_id_by_key[("RELATION_OWNER_VOICE", source["register"], root)])
        if has(text, "hier"):
            text = replace(text, "hier", "an der bezeichneten Stelle")
            applied.append(card_id_by_key[("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "HIER_FRAGMENT")])
        if "DY" in recipe_atoms and has(text, "abschließen"):
            text = replace(text, "abschließen", "schließe den Schritt")
            applied.append(card_id_by_key[("UNIVERSAL_OWNER_VOICE", "ALL_REGISTERS", "DY_CLOSURE_WORDING")])
        return text, applied

    event_errors = []
    for source, output in zip(src_events, events):
        adapted, applied = adapt(source)
        expected = {
            "navigation_event_id": source["navigation_event_id"], "event_id": source["event_id"],
            "statement_id": source["statement_id"], "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"], "register": source["register"], "owner_id": source["owner_id"],
            "surface": source["surface"], "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"], "gdt566_selected_clause_de": source["selected_working_clause_de"],
            "owner_voice_working_clause_de": adapted, "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "owner_voice_changed": "YES" if adapted != source["selected_working_clause_de"] else "NO",
            "owner_voice_equals_owner_bound": "YES" if adapted == source["owner_bound_control_clause_de"] else "NO",
            "adapter_card_count": str(len(applied)), "adapter_card_ids": "|".join(applied) or "NONE",
            "outer_template_id": source["outer_template_id"], "structural_template_id": source["structural_template_id"],
            "state_atom_alignment": source["state_atom_alignment"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if bad:
            event_errors.append((source["event_id"], bad))
    check("all_5122_events_reconstructed", not event_errors, event_errors[:3])
    check("nonstate_events_byte_unchanged", all(row["owner_voice_working_clause_de"] == row["gdt566_selected_clause_de"] and row["adapter_card_ids"] == "NONE" for row in events if row["state_status"] == "NONSTATE_CARD"))
    check("state_change_partition", Counter(row["owner_voice_changed"] for row in states) == Counter({"YES": 1639, "NO": 17}), dict(Counter(row["owner_voice_changed"] for row in states)))
    check("state_phrase_counts", len({row["gdt566_selected_clause_de"] for row in states}) == 607 and len({row["owner_voice_working_clause_de"] for row in states}) == 808)
    check("state_owner_exact_count", sum(row["owner_voice_equals_owner_bound"] == "YES" for row in states) == 20)
    check("state_projection_exact", all(output_state_by_id[event_id]["final_context_recipe"] == state_by_id[event_id]["recipe"] and output_state_by_id[event_id]["state_atom_alignment"] == state_by_id[event_id]["written_atom_alignment"] for event_id in state_by_id))
    check("event_guards_exact", {row["guard"] for row in events} == {"EVENT_RECIPE_AND_ROOTS_UNCHANGED__OWNER_VOICE_RENDERING_SEPARATE"})

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        grouped[event["statement_id"]].append(event)
    statement_errors = []
    for source, output in zip(src_statements, statements):
        members = sorted(grouped[source["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        old = " ".join(row["gdt566_selected_clause_de"] for row in members)
        adapted = " ".join(row["owner_voice_working_clause_de"] for row in members)
        control = " ".join(row["owner_bound_control_clause_de"] for row in members)
        expected = {
            "statement_id": source["statement_id"], "physical_page": source["physical_page"],
            "register": source["register"], "owner_id": source["owner_id"], "event_count": source["event_count"],
            "state_card_count": source["state_card_count"], "nonstate_card_count": source["nonstate_card_count"],
            "statement_mode": source["statement_mode"],
            "owner_voice_changed_event_count": str(sum(row["owner_voice_changed"] == "YES" for row in members)),
            "adapter_application_count": str(sum(int(row["adapter_card_count"]) for row in members)),
            "event_ids": source["event_ids"], "surface_sequence": source["surface_sequence"],
            "gdt566_selected_reading_de": old, "owner_voice_working_reading_de": adapted,
            "owner_bound_control_reading_de": control,
            "owner_voice_statement_changed": "YES" if adapted != old else "NO",
            "owner_voice_equals_owner_bound": "YES" if adapted == control else "NO",
            "end_mode": source["end_mode"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if old != source["selected_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
            bad["source_reconstruction"] = True
        if bad:
            statement_errors.append((source["statement_id"], bad))
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:3])
    check("statement_change_partition", Counter(row["owner_voice_statement_changed"] for row in statements) == Counter({"YES": 774, "NO": 19}), dict(Counter(row["owner_voice_statement_changed"] for row in statements)))
    check("statement_guards_exact", {row["guard"] for row in statements} == {"STATEMENT_BOUNDARY_AND_EVENT_ORDER_UNCHANGED"})

    expected_pairs = []
    for source_statement in src_statements:
        event_ids = source_statement["event_ids"].split("|")
        expected_pairs.extend(zip(event_ids, event_ids[1:]))
    check("all_adjacencies_exact", [(row["left_event_id"], row["right_event_id"]) for row in seams] == expected_pairs)
    direction_map = {("NONSTATE_CARD", "NONSTATE_CARD"): "NONSTATE_TO_NONSTATE", ("NONSTATE_CARD", "STATE_CARD"): "NONSTATE_TO_STATE", ("STATE_CARD", "NONSTATE_CARD"): "STATE_TO_NONSTATE", ("STATE_CARD", "STATE_CARD"): "STATE_TO_STATE"}
    seam_errors = []
    for output, (left_id, right_id) in zip(seams, expected_pairs):
        left, right = event_by_id[left_id], event_by_id[right_id]
        direction = direction_map[(left["state_status"], right["state_status"])]
        mixed = left["state_status"] != right["state_status"]
        args = []
        relations = []
        before_arg = after_arg = before_rel = after_rel = 0
        state_endpoint = None
        if mixed:
            state_endpoint = left if left["state_status"] == "STATE_CARD" else right
            nonstate = right if state_endpoint is left else left
            state = state_by_id[state_endpoint["event_id"]]
            for root in sorted(set(roots(state["effective_argument_roots"], "|")).intersection(ARG_GENERIC)):
                target = head(ARG_VOICE[state_endpoint["register"]][root][0])
                if has(nonstate["owner_voice_working_clause_de"], target):
                    args.append(f"{root}:{target}")
                    before_arg += int(has(state_endpoint["gdt566_selected_clause_de"], target))
                    after_arg += int(has(state_endpoint["owner_voice_working_clause_de"], target))
            for root in sorted(set(roots(state["recipe"], "+")).intersection(REL_GENERIC)):
                target = head(REL_VOICE[state_endpoint["register"]][root])
                if has(nonstate["owner_voice_working_clause_de"], target):
                    relations.append(f"{root}:{target}")
                    before_rel += int(has(state_endpoint["gdt566_selected_clause_de"], target))
                    after_rel += int(has(state_endpoint["owner_voice_working_clause_de"], target))
        expected = {
            "direction": direction, "mixed_state_nonstate": "YES" if mixed else "NO",
            "state_endpoint_event_id": state_endpoint["event_id"] if state_endpoint else "NOT_APPLICABLE",
            "state_endpoint_changed": state_endpoint["owner_voice_changed"] if state_endpoint else "NOT_APPLICABLE",
            "adapter_card_ids": state_endpoint["adapter_card_ids"] if state_endpoint else "NOT_APPLICABLE",
            "shared_argument_contacts": "|".join(args) or "NONE",
            "shared_relation_contacts": "|".join(relations) or "NONE",
            "argument_head_exact_before": str(before_arg), "argument_head_exact_after": str(after_arg),
            "relation_head_exact_before": str(before_rel), "relation_head_exact_after": str(after_rel),
            "left_gdt566_clause_de": left["gdt566_selected_clause_de"], "right_gdt566_clause_de": right["gdt566_selected_clause_de"],
            "left_owner_voice_clause_de": left["owner_voice_working_clause_de"], "right_owner_voice_clause_de": right["owner_voice_working_clause_de"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if bad:
            seam_errors.append((left_id, right_id, bad))
    check("all_4329_seams_reconstructed", not seam_errors, seam_errors[:3])
    direction_counts = Counter(row["direction"] for row in seams)
    check("direction_counts_exact", direction_counts == Counter({"NONSTATE_TO_NONSTATE": 2426, "NONSTATE_TO_STATE": 969, "STATE_TO_NONSTATE": 611, "STATE_TO_STATE": 323}), dict(direction_counts))
    mixed = [row for row in seams if row["mixed_state_nonstate"] == "YES"]
    check("mixed_seam_counts", len(mixed) == 1580 and len({row["statement_id"] for row in mixed}) == 528 and sum(row["state_endpoint_changed"] == "YES" for row in mixed) == 1563)
    check("argument_contact_gain", sum(row["shared_argument_contacts"] != "NONE" for row in mixed) == 1209 and sum(int(row["argument_head_exact_before"]) for row in mixed) == 0 and sum(int(row["argument_head_exact_after"]) for row in mixed) == 1209)
    check("relation_contact_gain", sum(row["shared_relation_contacts"] != "NONE" for row in mixed) == 20 and sum(int(row["relation_head_exact_before"]) for row in mixed) == 3 and sum(int(row["relation_head_exact_after"]) for row in mixed) == 20)
    check("seam_guards_exact", {row["guard"] for row in seams} == {"ADJACENCY_ONLY__NO_EVENT_MERGE"})

    direction_lookup = {row["direction"]: row for row in directions}
    check("direction_profiles_exact", set(direction_lookup) == set(direction_counts) and all(int(direction_lookup[key]["seam_count"]) == value for key, value in direction_counts.items()))
    register_lookup = {row["register"]: row for row in registers}
    check("register_profiles_cover_all", list(register_lookup) == list(REGISTERS) and sum(int(row["state_event_count"]) for row in registers) == 1656 and sum(int(row["changed_state_event_count"]) for row in registers) == 1639)

    expected_metrics = {
        "adapter_card_count": 39, "argument_owner_voice_card_count": 19, "relation_owner_voice_card_count": 18,
        "universal_owner_voice_card_count": 2, "register_root_cell_use_count": 1807,
        "register_root_cell_supported_use_count": 1807, "place_voice_event_count": 123,
        "place_voice_supported_event_count": 123, "close_voice_event_count": 705,
        "close_voice_supported_event_count": 705, "state_event_count": 1656,
        "changed_state_event_count": 1639, "unchanged_state_event_count": 17,
        "owner_voice_equals_owner_bound_state_count": 20, "distinct_gdt566_state_clause_count": 607,
        "distinct_owner_voice_state_clause_count": 808, "changed_statement_count": 774,
        "unchanged_statement_count": 19, "changed_physical_page_count": 28,
        "complete_event_count": 5122, "complete_statement_count": 793, "within_statement_seam_count": 4329,
        "nonstate_to_nonstate_seam_count": 2426, "nonstate_to_state_seam_count": 969,
        "state_to_nonstate_seam_count": 611, "state_to_state_seam_count": 323,
        "mixed_state_nonstate_seam_count": 1580, "mixed_seam_statement_count": 528,
        "changed_mixed_seam_endpoint_count": 1563, "shared_argument_contact_seam_count": 1209,
        "argument_head_exact_before": 0, "argument_head_exact_after": 1209,
        "shared_relation_contact_seam_count": 20, "relation_head_exact_before": 3,
        "relation_head_exact_after": 20, "new_pages": 0, "new_events": 0, "new_statements": 0,
        "new_surfaces": 0, "new_recipes": 0, "new_root_values": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_metrics.items()), {key: result.get(key) for key in expected_metrics})
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()}, result.get("input_sha256"))
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    page_headings = [line[3:] for line in book.splitlines() if line.startswith("## ")]
    check("book_metrics_present", all(needle in book for needle in ("39 Adapterkarten", "1.639/1.656", "1.209 gemeinsame", "3 → 20")))
    check("book_all_pages_once", page_headings == [row["physical_page"] for row in src_pages], page_headings)
    check("book_zero_pages_retained", book.count("Lokalregisterseite bleibt sichtbar") == 2)
    check("book_all_statements_present", all(row["statement_id"] in book for row in statements))

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
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
