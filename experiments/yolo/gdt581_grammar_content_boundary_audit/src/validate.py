#!/usr/bin/env python3
"""Independent source-based validator for GDT581.

This file deliberately does not import ``run.py`` or ``boundary_lib.py``.  It
rebuilds identities from the upstream TSVs and checks the GDT581 artifacts
against that second derivation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit"
ART = BASE / "artifacts"


def artifact_dir(slug: str) -> Path:
    return ROOT / "experiments/yolo" / slug / "artifacts"


G407 = artifact_dir("gdt407_unified_twenty_six_page_workshop_edition")
G416 = artifact_dir("gdt416_owner_local_imperative_sentence_compiler")
G471 = artifact_dir("gdt471_empirical_address_shell_phrasebook")
G472 = artifact_dir("gdt472_complete_address_template_dictionary")
G479 = artifact_dir("gdt479_definitive_local_microrecord_edition")
G513 = artifact_dir("gdt513_remaining_local_group_semantic_census")
G515 = artifact_dir("gdt515_second_random_four_page_full_admission")
G539 = artifact_dir("gdt539_four_page_contextual_statement_edition")
G558 = artifact_dir("gdt558_grade_carrier_envelope_grammar")
G567 = artifact_dir("gdt567_owner_voice_seam_adapter")
G568 = artifact_dir("gdt568_twenty_owner_action_voice_frames")
G577 = artifact_dir("gdt577_interrupted_modifier_attachment_topology")
G579 = artifact_dir("gdt579_mixed_outer_inner_scope_voice")
G580 = artifact_dir("gdt580_adjacent_relation_resumption_voice")


INPUTS = {
    "gdt580_events": G580 / "gdt580_5122_resumption_voice_event_edition.tsv",
    "gdt580_statements": G580 / "gdt580_793_resumption_voice_statement_edition.tsv",
    "gdt580_pages": G580 / "gdt580_30_page_resumption_voice_profiles.tsv",
    "gdt580_slots": G580 / "gdt580_6_written_slot_spans.tsv",
    "gdt579_scope_slots": G579 / "gdt579_34_scope_slot_assignments.tsv",
    "gdt577_repeat_slots": G577 / "gdt577_125_slot_head_assignments.tsv",
    "gdt407_attachments": G407 / "gdt407_5051_attachment_edition.tsv",
    "gdt515_attachments": G515 / "gdt515_factorized_attachments.tsv",
    "gdt515_old_events": G515 / "gdt515_5122_running_event_edition.tsv",
    "gdt416_clauses": G416 / "gdt416_4576_imperative_clauses.tsv",
    "gdt416_inherited_actions": G416 / "gdt416_inherited_action_audit.tsv",
    "gdt416_inherited_arguments": G416 / "gdt416_inherited_argument_audit.tsv",
    "gdt539_context_events": G539 / "gdt539_546_contextual_prose_events.tsv",
    "gdt558_grade_assignments": G558 / "gdt558_333_grade_carrier_assignments.tsv",
    "gdt558_grade_hazards": G558 / "gdt558_18_false_inheritance_hazards.tsv",
    "gdt567_voice_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
    "gdt568_action_cells": G568 / "gdt568_45_register_action_cells.tsv",
    "gdt515_local_cards": G515 / "gdt515_744_local_group_edition.tsv",
    "gdt479_local_events": G479 / "gdt479_183_definitive_local_events.tsv",
    "gdt513_local_events": G513 / "gdt513_510_remaining_local_working_edition.tsv",
    "gdt515_local_51": G515 / "gdt515_51_f66r_label_sign_edition.tsv",
    "gdt471_name_templates": G471 / "gdt471_89_template_assignments.tsv",
    "gdt472_complete_templates": G472 / "gdt472_107_complete_template_assignments.tsv",
}

OUTPUTS = {
    "complete": ART / "gdt581_15889_complete_slot_ledger.tsv",
    "carriers": ART / "gdt581_13702_content_carrier_hosts.tsv",
    "controls": ART / "gdt581_2187_control_host_slots.tsv",
    "running": ART / "gdt581_13809_running_slot_hosts.tsv",
    "aliases": ART / "gdt581_4026_inherited_alias_edges.tsv",
    "focus": ART / "gdt581_5672_focus_reconciliation.tsv",
    "reconciliations": ART / "gdt581_8_final_recipe_reconciliations.tsv",
    "grades": ART / "gdt581_333_grade_envelope_hosts.tsv",
    "hazards": ART / "gdt581_18_grade_cross_boundary_hazards.tsv",
    "modifiers": ART / "gdt581_1810_non_grade_modifier_hosts.tsv",
    "cross_relations": ART / "gdt581_25_cross_card_relation_slots.tsv",
    "safe": ART / "gdt581_2_safe_focus_exceptions.tsv",
    "voice_repairs": ART / "gdt581_269_focus_voice_repairs.tsv",
    "event_repairs": ART / "gdt581_232_event_voice_repairs.tsv",
    "local_cards": ART / "gdt581_744_local_card_hosts.tsv",
    "local_components": ART / "gdt581_1973_local_component_hosts.tsv",
    "names": ART / "gdt581_107_name_core_slots.tsv",
    "events": ART / "gdt581_5122_content_ready_event_edition.tsv",
    "statements": ART / "gdt581_793_content_ready_statement_edition.tsv",
    "pages": ART / "gdt581_30_page_boundary_profiles.tsv",
}

EXPECTED_INPUT_COUNTS = {
    "gdt580_events": 5122, "gdt580_statements": 793, "gdt580_pages": 30,
    "gdt580_slots": 6, "gdt579_scope_slots": 34, "gdt577_repeat_slots": 125,
    "gdt407_attachments": 5051, "gdt515_attachments": 621,
    "gdt515_old_events": 5122, "gdt416_inherited_actions": 1598,
    "gdt416_clauses": 4576,
    "gdt416_inherited_arguments": 2096, "gdt539_context_events": 546,
    "gdt558_grade_assignments": 333, "gdt558_grade_hazards": 18,
    "gdt567_voice_cards": 39, "gdt568_action_cells": 45,
    "gdt515_local_cards": 744, "gdt479_local_events": 183,
    "gdt513_local_events": 510, "gdt515_local_51": 51,
    "gdt471_name_templates": 89, "gdt472_complete_templates": 107,
}

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
OBJECT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}
GRADE_ROOTS = {"E", "EE", "EEE"}
STATE_ROOTS = {"OT", "OL", "DY"}
RUNNING_MODIFIERS = {
    "AM_ADDR", "AN", "A_ADDR", "CARRIER_Q", "DA", "D_ADDR", "D_LABEL",
    "E", "EE", "EEE", "G_LABEL", "HO", "IIN", "LOCAL_CHAR_B",
    "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_J",
    "M_LOCAL", "O", "OS", "S_ADDR",
}
LOCAL_CONTROLS = {
    "CFH", "CHEO", "CHK", "CKH", "CPH", "CTH", "LOCAL_SIGN_C",
    "LOCAL_SIGN_X", "SECTION_MARKER",
}
SAFE_FOCUS_IDS = {"G515-A00356", "G515-A00357"}
FORCED_OCCURRENCE_ID = "G407-A04352"

IMPERATIVE_RE = re.compile(
    r"(?i)(?<![-\w])"
    r"(entnimm|nimm|halte|gib|ordne|führe|wähle|bearbeite|stelle|lege|"
    r"markiere|kennzeichne|trage|setze)(?!\w)"
)
IMPERATIVE_ROOT = {
    "entnimm": "CH", "nimm": "CH", "halte": "SH", "gib": "K",
    "ordne": "K", "führe": "K", "wähle": "S", "bearbeite": "CHD",
    "stelle": "T", "lege": "T", "markiere": "R", "kennzeichne": "R",
    "trage": "OK",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atoms(recipe: str) -> list[str]:
    return [] if recipe in {"", "NONE"} else recipe.split("+")


def nth_position(parts: list[str], root: str, rank: int) -> int | None:
    seen = 0
    for position, item in enumerate(parts, 1):
        if item == root:
            seen += 1
            if seen == rank:
                return position
    return None


def occurrence_rank(parts: list[str], root: str, position: int) -> int:
    if position < 1 or position > len(parts) or parts[position - 1] != root:
        raise RuntimeError(f"Invalid source occurrence {root}@{position} in {parts}")
    return sum(item == root for item in parts[:position])


def unique(rows: Iterable[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    source = list(rows)
    result = {row[key]: row for row in source}
    if len(result) != len(source):
        raise RuntimeError(f"Duplicate {label} identity")
    return result


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return {str(k): v for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    if isinstance(value, set):
        return sorted(str(item) for item in value)
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serial(item) for item in value]
    return value


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, check_id: str, condition: bool, observed: Any, expected: Any) -> None:
        self.checks.append({
            "check_id": check_id,
            "status": "PASS" if condition else "FAIL",
            "observed": serial(observed),
            "expected": serial(expected),
        })

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [row for row in self.checks if row["status"] == "FAIL"]


def classify_running(root: str) -> tuple[str, str]:
    if root in ACTION_ROOTS:
        return "RUNNING_ACTION_FUNCTION", "CONTENT_CARRIER"
    if root in OBJECT_ROOTS:
        return "RUNNING_OBJECT_FUNCTION", "CONTENT_CARRIER"
    if root in RELATION_ROOTS:
        return "RUNNING_RELATION_FUNCTION", "CONTENT_CARRIER"
    if root in RUNNING_MODIFIERS:
        return "RUNNING_MODIFIER_FUNCTION", "CONTENT_CARRIER"
    if root in STATE_ROOTS:
        return "RUNNING_STATE_CONTROL", "CONTROL_HOST_ONLY"
    if root == "LOCAL_X":
        return "RUNNING_LEARNED_CORE", "CONTENT_CARRIER"
    if root == "RESUME_CARD":
        return "RUNNING_RESUMPTION_CONTROL", "CONTROL_HOST_ONLY"
    raise RuntimeError(f"Unclassified running root: {root}")


def classify_local(root: str) -> tuple[str, str]:
    if root in ACTION_ROOTS:
        return "LOCAL_ACTION_FUNCTION", "CONTENT_CARRIER"
    if root in OBJECT_ROOTS:
        return "LOCAL_OBJECT_FUNCTION", "CONTENT_CARRIER"
    if root in RELATION_ROOTS:
        return "LOCAL_RELATION_FUNCTION", "CONTENT_CARRIER"
    if root in GRADE_ROOTS:
        return "LOCAL_MODIFIER_FUNCTION", "CONTENT_CARRIER"
    if root in STATE_ROOTS:
        return "LOCAL_STATE_CONTROL", "CONTROL_HOST_ONLY"
    if root in LOCAL_CONTROLS:
        return "LOCAL_MACRO_OR_SIGN_CONTROL", "CONTROL_HOST_ONLY"
    return "LOCAL_MODIFIER_FUNCTION", "CONTENT_CARRIER"


def extract_name_spans(surface: str, template: str) -> list[tuple[str, str]]:
    placeholders = re.findall(r"\{(NAME_[0-9]+)\}", template)
    if not placeholders:
        return []
    chunks = re.split(r"\{NAME_[0-9]+\}", template)
    expression = "^"
    for index, chunk in enumerate(chunks):
        expression += re.escape(chunk)
        if index < len(placeholders):
            expression += "(.+?)"
    match = re.fullmatch(expression, surface)
    if not match:
        raise RuntimeError(f"Name template does not match {surface}: {template}")
    return list(zip(placeholders, match.groups()))


def audible_action_root(clause: str) -> tuple[str, str] | None:
    for match in IMPERATIVE_RE.finditer(clause):
        verb = match.group(1).lower()
        tail = clause[match.end():]
        stop = re.search(r";|,|\.|(?i:\bund\b)", tail)
        segment = tail[:stop.start()] if stop else tail
        if verb == "führe" and not re.search(r"(?i)(?<!\w)zu(?!\w)", segment):
            continue
        if verb != "setze":
            return IMPERATIVE_ROOT[verb], verb
        return ("P" if re.search(r"(?i)(?<!\w)ein(?!\w)", segment) else "OK", verb)
    return None


def derive_local_sources(data: dict[str, list[dict[str, str]]]) -> tuple[dict[str, dict[str, str]], dict[str, tuple[str, str]]]:
    base = unique(data["gdt515_local_cards"], "source_event_id", "base local card")
    p479 = unique(data["gdt479_local_events"], "source_event_id", "GDT479 card")
    p513 = unique(data["gdt513_local_events"], "source_event_id", "GDT513 card")
    p515 = unique(data["gdt515_local_51"], "event_id", "GDT515 local card")
    if set(p479) & set(p513) or (set(p479) | set(p513)) & set(p515):
        raise RuntimeError("Local source partitions overlap")
    recipes: dict[str, tuple[str, str]] = {}
    for event_id, card in base.items():
        if event_id in p479:
            row, recipe, partition = p479[event_id], p479[event_id]["working_recipe"], "GDT479_MICRORECORD_183"
        elif event_id in p513:
            row, recipe, partition = p513[event_id], p513[event_id]["component_recipe"], "GDT513_REMAINDER_510"
        elif event_id in p515:
            row, recipe, partition = p515[event_id], p515[event_id]["visible_recipe"], "GDT515_NEW_LOCAL_51"
        else:
            raise RuntimeError(f"Unpartitioned local card: {event_id}")
        for field in ("physical_page", "register", "locus", "surface"):
            if row[field] != card[field]:
                raise RuntimeError(f"Local source coordinate drift: {event_id}:{field}")
        recipes[event_id] = (recipe, partition)
    return base, recipes


def derive_name_slots(data: dict[str, list[dict[str, str]]]) -> dict[str, tuple[str, str, str, int, int]]:
    learned = unique(data["gdt471_name_templates"], "source_event_id", "GDT471 label")
    complete = unique(data["gdt472_complete_templates"], "source_event_id", "GDT472 label")
    name_events = {event_id for event_id, row in complete.items() if "{NAME_" in row["surface_template"]}
    if name_events != set(learned):
        raise RuntimeError("GDT471/GDT472 name-event mismatch")
    result: dict[str, tuple[str, str, str, int, int]] = {}
    for event_id in name_events:
        row = complete[event_id]
        extracted = extract_name_spans(row["surface"], row["surface_template"])
        traces = []
        for item in learned[event_id]["learned_span_trace"].split("|"):
            start, end, raw = item.split(":", 2)
            traces.append((int(start), int(end), raw))
        if [raw for _, raw in extracted] != [raw for _, _, raw in traces]:
            raise RuntimeError(f"Name trace mismatch at {event_id}")
        for (placeholder, raw), (start, end, trace_raw) in zip(extracted, traces):
            if raw != trace_raw or row["surface"][start:end] != raw:
                raise RuntimeError(f"Name coordinate mismatch at {event_id}:{placeholder}")
            result[f"LOCAL_NAME:{event_id}:{placeholder}"] = (event_id, raw, row["content_class"], start, end)
    return result


def derive_focus_expectations(data: dict[str, list[dict[str, str]]], event_by_id: dict[str, dict[str, str]]) -> tuple[dict[str, dict[str, Any]], set[str], set[str]]:
    old_recipe_by_event: dict[str, str] = {}
    for row in data["gdt515_old_events"]:
        key = row["global_running_event_id"] if row["global_running_event_id"].startswith("G407-") else row["source_replay_event_id"]
        old_recipe_by_event[key] = row["component_recipe"]
    if set(old_recipe_by_event) != set(event_by_id):
        raise RuntimeError("Old/final event identity mismatch")
    sources: list[dict[str, Any]] = []
    for row in data["gdt407_attachments"]:
        event_id = row["global_running_event_id"]
        sources.append({
            "id": row["global_attachment_id"], "event": event_id,
            "source_recipe": old_recipe_by_event[event_id],
            "focus_pos": int(row["focus_atom_ordinal"]), "root": row["focus_core"],
            "head_event": row["selected_action_global_event_id"],
            "head_pos": int(row["selected_action_atom_ordinal"]), "head_root": row["action_core"],
            "head_kind": row["head_kind"], "geometry": row["attachment_geometry"],
            "selector": row["selector_rule"],
        })
    for row in data["gdt515_attachments"]:
        sources.append({
            "id": row["factorized_id"], "event": row["event_id"],
            "source_recipe": row["visible_recipe"],
            "focus_pos": int(row["focus_atom_ordinal"]), "root": row["focus_core"],
            "head_event": row["selected_action_event_id"],
            "head_pos": int(row["selected_action_atom_ordinal"]), "head_root": row["action_core"],
            "head_kind": row["head_kind"], "geometry": row["attachment_geometry"],
            "selector": row["selector_rule"],
        })
    result: dict[str, dict[str, Any]] = {}
    deleted: set[str] = set()
    changed: set[str] = set()
    for source in sources:
        event_id = source["event"]
        source_parts = atoms(source["source_recipe"])
        final_parts = atoms(event_by_id[event_id]["final_context_recipe"])
        focus_rank = occurrence_rank(source_parts, source["root"], source["focus_pos"])
        focus_pos = nth_position(final_parts, source["root"], focus_rank)
        if focus_pos is None:
            deleted.add(source["id"])
            continue
        if source["head_event"] == "OWNER" or "OWNER" in source["head_kind"]:
            head_event, head_pos, head_root, head_rank = source["head_event"], "OWNER", "OWNER", "OWNER"
        else:
            head_event = source["head_event"]
            old_head = atoms(old_recipe_by_event[head_event])
            head_rank = occurrence_rank(old_head, source["head_root"], source["head_pos"])
            head_root = source["head_root"]
            head_pos = nth_position(atoms(event_by_id[head_event]["final_context_recipe"]), head_root, head_rank)
            if source["id"] == "G515-A00403":
                head_event, head_pos, head_root, head_rank = "G515-E0423", 3, "K", 1
            elif source["id"] == "G515-A00407":
                head_event, head_pos, head_root, head_rank = "G515-E0426", 2, "K", 1
            elif head_pos is None:
                raise RuntimeError(f"Unexpected vanished focus head: {source['id']}")
        if focus_pos != source["focus_pos"] or (head_pos != "OWNER" and head_pos != source["head_pos"]) or head_root != source["head_root"]:
            changed.add(source["id"])
        result[source["id"]] = {
            "event": event_id, "root": source["root"], "focus_pos": focus_pos,
            "focus_rank": focus_rank, "head_event": head_event, "head_pos": head_pos,
            "head_root": head_root, "head_rank": head_rank,
            "geometry": source["geometry"], "selector": source["selector"],
        }
    result["GDT581-NEW-E0253-AIIN"] = {
        "event": "G515-E0253", "root": "AIIN", "focus_pos": 1, "focus_rank": 1,
        "head_event": "G515-E0253", "head_pos": 2, "head_root": "CH", "head_rank": 1,
        "geometry": "SAME_CARD_RIGHT_ACTION", "selector": "NEAREST_HEAD_LEFT_TIE",
    }
    return result, deleted, changed


def derive_aliases(data: dict[str, list[dict[str, str]]], event_by_id: dict[str, dict[str, str]]) -> Counter[tuple[str, str, str, str, str, str, str]]:
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in event_by_id.values():
        by_statement[event["statement_id"]].append(event)
    for rows in by_statement.values():
        rows.sort(key=lambda row: int(row["card_ordinal_in_statement"]))

    def prior(event_id: str, root: str) -> str | None:
        event = event_by_id[event_id]
        candidates = [row for row in by_statement[event["statement_id"]] if int(row["card_ordinal_in_statement"]) < int(event["card_ordinal_in_statement"]) and root in atoms(row["final_context_recipe"])]
        return candidates[-1]["event_id"] if candidates else None

    pending: list[tuple[str, str, str, str | None, str]] = []
    for row in data["gdt416_inherited_actions"]:
        event_id, root = row["global_running_event_id"], row["inherited_action_root"]
        pending.append(("ACTION_ALIAS", event_id, root, prior(event_id, root), "GDT416"))
    for row in data["gdt416_inherited_arguments"]:
        event_id, root = row["global_running_event_id"], row["inherited_argument_root"]
        pending.append(("OBJECT_ALIAS", event_id, root, prior(event_id, root), "GDT416"))
    for row in data["gdt539_context_events"]:
        if row["inherited_action_root"] != "NONE":
            pending.append(("ACTION_ALIAS", row["event_id"], row["inherited_action_root"], row["inherited_action_source_event_id"], "GDT539"))
        if row["inherited_argument_root"] != "NONE":
            pending.append(("OBJECT_ALIAS", row["event_id"], row["inherited_argument_root"], row["inherited_argument_source_event_id"], "GDT539"))
    result: Counter[tuple[str, str, str, str, str, str, str]] = Counter()
    for alias_class, event_id, root, source_event, layer in pending:
        event = event_by_id[event_id]
        if source_event in {None, "", "NONE"}:
            source_kind, source_id, source_position = "OWNER_DEFAULT", "OWNER", "OWNER"
            source_key = f"OWNER_DEFAULT:{event['owner_id']}:{root}"
        else:
            source = event_by_id[source_event]
            if (source["statement_id"], source["physical_page"], source["owner_id"]) != (event["statement_id"], event["physical_page"], event["owner_id"]) or int(source["card_ordinal_in_statement"]) >= int(event["card_ordinal_in_statement"]):
                raise RuntimeError(f"Alias crosses a hard boundary: {event_id}")
            positions = [i for i, item in enumerate(atoms(source["final_context_recipe"]), 1) if item == root]
            if not positions:
                raise RuntimeError(f"Alias source root absent: {source_event}:{root}")
            source_kind, source_id, source_position = "SAME_STATEMENT_EVENT", source_event, str(positions[-1])
            source_key = f"{source_event}@{source_position}:{root}"
        result[(alias_class, event_id, root, source_kind, source_id, source_position, f"{source_key}|{layer}")] += 1
    return result


def validate(output_path: Path) -> tuple[dict[str, Any], int]:
    audit = Audit()
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    out = {name: read_tsv(path) for name, path in OUTPUTS.items()}
    result = json.loads((ART / "gdt581_result.json").read_text(encoding="utf-8"))

    observed_input_counts = {name: len(rows) for name, rows in data.items()}
    audit.check("V001_INPUT_CARDINALITIES", observed_input_counts == EXPECTED_INPUT_COUNTS, observed_input_counts, EXPECTED_INPUT_COUNTS)
    forbidden = sorted({
        value for rows in data.values() for row in rows for value in row.values()
        if isinstance(value, str) and value.startswith("f84")
    })
    audit.check("V002_SEALED_F84_ABSENT", not forbidden, forbidden, [])

    source_events = data["gdt580_events"]
    source_statements = data["gdt580_statements"]
    source_pages = data["gdt580_pages"]
    event_by_id = unique(source_events, "event_id", "GDT580 event")

    expected_running: dict[str, tuple[str, str, str]] = {}
    running_balance: Counter[str] = Counter()
    for event in source_events:
        for position, root in enumerate(atoms(event["final_context_recipe"]), 1):
            boundary_class, fill = classify_running(root)
            expected_running[f"RUNNING:{event['event_id']}@{position}"] = (root, boundary_class, fill)
            running_balance[fill] += 1
    audit.check("V003_RUNNING_SLOT_SOURCE_TOTAL", len(expected_running) == 13809, len(expected_running), 13809)
    audit.check("V004_RUNNING_SLOT_SOURCE_BALANCE", running_balance == Counter({"CONTENT_CARRIER": 11938, "CONTROL_HOST_ONLY": 1871}), running_balance, Counter({"CONTENT_CARRIER": 11938, "CONTROL_HOST_ONLY": 1871}))

    base_cards, local_recipes = derive_local_sources(data)
    audit.check("V005_LOCAL_CARD_SOURCE_PARTITION", len(base_cards) == len(local_recipes) == 744, len(local_recipes), 744)
    expected_components: dict[str, tuple[str, str, str]] = {}
    local_balance: Counter[str] = Counter()
    partition_counts: Counter[str] = Counter()
    for event_id, (recipe, partition) in local_recipes.items():
        partition_counts[partition] += 1
        for position, root in enumerate(atoms(recipe), 1):
            boundary_class, fill = classify_local(root)
            expected_components[f"LOCAL_COMPONENT:{event_id}@{position}"] = (root, boundary_class, fill)
            local_balance[fill] += 1
    expected_partitions = Counter({"GDT479_MICRORECORD_183": 183, "GDT513_REMAINDER_510": 510, "GDT515_NEW_LOCAL_51": 51})
    audit.check("V006_LOCAL_PARTITION_COUNTS", partition_counts == expected_partitions, partition_counts, expected_partitions)
    audit.check("V007_LOCAL_COMPONENT_SOURCE_TOTAL", len(expected_components) == 1973, len(expected_components), 1973)
    audit.check("V008_LOCAL_COMPONENT_SOURCE_BALANCE", local_balance == Counter({"CONTENT_CARRIER": 1657, "CONTROL_HOST_ONLY": 316}), local_balance, Counter({"CONTENT_CARRIER": 1657, "CONTROL_HOST_ONLY": 316}))

    expected_names = derive_name_slots(data)
    name_class_counts = Counter(value[2] for value in expected_names.values())
    raw_name_types = {value[1] for value in expected_names.values()}
    class_name_types = {(value[2], value[1]) for value in expected_names.values()}
    expected_name_classes = Counter({"STAR_BEARING_RING_POSITION": 60, "DRUG_OR_INGREDIENT_OBJECT": 38, "BATH_OR_OUTLET_STATION": 7, "PICTURED_PLANT": 2})
    audit.check("V009_NAME_SLOT_SOURCE_TOTAL", len(expected_names) == 107, len(expected_names), 107)
    audit.check("V010_NAME_SLOT_CLASS_COUNTS", name_class_counts == expected_name_classes, name_class_counts, expected_name_classes)
    audit.check("V011_NAME_CORE_TYPE_COUNTS", (len(raw_name_types), len(class_name_types)) == (72, 80), (len(raw_name_types), len(class_name_types)), (72, 80))

    running_rows = out["running"]
    running_map = {row["slot_id"]: (row["atom_root"], row["boundary_class"], row["fill_status"]) for row in running_rows}
    audit.check("V012_RUNNING_ARTIFACT_EXACT_SOURCE_SLOTS", len(running_map) == len(running_rows) and running_map == expected_running, len(running_map), len(expected_running))
    component_rows = out["local_components"]
    component_map = {row["slot_id"]: (row["component_root"], row["boundary_class"], row["fill_status"]) for row in component_rows}
    audit.check("V013_LOCAL_COMPONENT_ARTIFACT_EXACT_SOURCE_SLOTS", len(component_map) == len(component_rows) and component_map == expected_components, len(component_map), len(expected_components))
    name_rows = out["names"]
    name_map = {
        row["slot_id"]: (row["source_event_id"], row["raw_name_core"], row["content_class"], int(row["name_span_start_zero_based"]), int(row["name_span_end_exclusive"]))
        for row in name_rows
    }
    audit.check("V014_NAME_ARTIFACT_EXACT_SOURCE_SPANS", len(name_map) == len(name_rows) and name_map == expected_names, len(name_map), len(expected_names))
    local_card_rows = out["local_cards"]
    local_card_map = {row["source_event_id"]: (row["component_recipe"], row["source_partition"]) for row in local_card_rows}
    audit.check("V015_LOCAL_CARD_ARTIFACT_EXACT_SOURCE_HOSTS", len(local_card_map) == len(local_card_rows) and local_card_map == local_recipes, len(local_card_map), 744)

    complete_rows = out["complete"]
    complete_map = {row["slot_id"]: (row["slot_value"], row["boundary_class"], row["fill_status"]) for row in complete_rows}
    expected_complete = dict(expected_running)
    expected_complete.update(expected_components)
    expected_complete.update({slot_id: (value[1], "LOCAL_LEARNED_NAME_SLOT", "CONTENT_CARRIER") for slot_id, value in expected_names.items()})
    complete_balance = Counter(row["fill_status"] for row in complete_rows)
    audit.check("V016_COMPLETE_SLOT_EXACT_SOURCE_UNIVERSE", len(complete_map) == len(complete_rows) and complete_map == expected_complete, len(complete_map), 15889)
    audit.check("V017_COMPLETE_SLOT_BALANCE", complete_balance == Counter({"CONTENT_CARRIER": 13702, "CONTROL_HOST_ONLY": 2187}), complete_balance, Counter({"CONTENT_CARRIER": 13702, "CONTROL_HOST_ONLY": 2187}))
    carriers = [row for row in complete_rows if row["fill_status"] == "CONTENT_CARRIER"]
    controls = [row for row in complete_rows if row["fill_status"] == "CONTROL_HOST_ONLY"]
    audit.check("V018_CONTENT_CARRIER_PROJECTION", out["carriers"] == carriers and len(carriers) == 13702, len(out["carriers"]), 13702)
    audit.check("V019_CONTROL_HOST_PROJECTION", out["controls"] == controls and len(controls) == 2187, len(out["controls"]), 2187)
    unowned = [row["slot_id"] for row in complete_rows if row["primary_governor_kind"] in {"", "NONE", "NOT_APPLICABLE"} or row["primary_governor_key"] in {"", "NONE", "NOT_APPLICABLE"}]
    audit.check("V020_ZERO_UNOWNED_COMPLETE_SLOTS", not unowned, unowned[:20], [])

    expected_focus, deleted_focus, coordinate_changed = derive_focus_expectations(data, event_by_id)
    audit.check("V021_FOCUS_SOURCE_DELETE", deleted_focus == {"G515-A00165"}, deleted_focus, {"G515-A00165"})
    expected_changed = {"G515-A00245", "G515-A00258", "G515-A00403", "G515-A00404", "G515-A00407", "G515-A00422"}
    audit.check("V022_FOCUS_SOURCE_COORDINATE_CHANGES", coordinate_changed == expected_changed, coordinate_changed, expected_changed)
    focus_rows = out["focus"]
    focus_by_id = unique(focus_rows, "focus_host_id", "GDT581 focus")
    observed_focus: dict[str, dict[str, Any]] = {}
    for focus_id, row in focus_by_id.items():
        observed_focus[focus_id] = {
            "event": row["event_id"], "root": row["focus_root"],
            "focus_pos": int(row["focus_final_position"]), "focus_rank": int(row["focus_occurrence_rank"]),
            "head_event": row["primary_governor_event_id"],
            "head_pos": row["primary_governor_atom_position"] if row["primary_governor_atom_position"] == "OWNER" else int(row["primary_governor_atom_position"]),
            "head_root": row["primary_governor_root"],
            "head_rank": row["primary_governor_occurrence_rank"] if row["primary_governor_occurrence_rank"] == "OWNER" else int(row["primary_governor_occurrence_rank"]),
            "geometry": row["attachment_geometry"], "selector": row["selector_rule"],
        }
    audit.check("V023_FOCUS_5672_EXACT_SOURCE_RECONCILIATION", len(observed_focus) == 5672 and observed_focus == expected_focus, len(observed_focus), 5672)
    expected_focus_positions = {
        (event["event_id"], position, root)
        for event in source_events
        for position, root in enumerate(atoms(event["final_context_recipe"]), 1)
        if root in OBJECT_ROOTS | RELATION_ROOTS | GRADE_ROOTS
    }
    observed_focus_positions = {(row["event_id"], int(row["focus_final_position"]), row["focus_root"]) for row in focus_rows}
    audit.check("V024_EVERY_FINAL_FOCUS_POSITION_HOSTED_ONCE", observed_focus_positions == expected_focus_positions and len(observed_focus_positions) == len(focus_rows), len(observed_focus_positions), len(expected_focus_positions))

    expected_reconciliations = {
        ("G515-A00165", "G515-E0182", "DELETE_STALE_FOCUS"),
        ("G515-A00245", "G515-E0244", "PURE_OCCURRENCE_POSITION_UPDATE"),
        ("G515-A00258", "G515-E0253", "PURE_OCCURRENCE_POSITION_UPDATE"),
        ("G515-A00403", "G515-E0423", "SELECTOR_FORCED_PRIMARY_HEAD_SWITCH"),
        ("G515-A00404", "G515-E0423", "PURE_OCCURRENCE_POSITION_UPDATE"),
        ("G515-A00407", "G515-E0426", "SELECTOR_FORCED_PRIMARY_HEAD_SWITCH"),
        ("G515-A00422", "G515-E0437", "PURE_OCCURRENCE_POSITION_UPDATE"),
        ("NONE", "G515-E0253", "INSERT_NEW_FINAL_FOCUS"),
    }
    observed_reconciliations = {(row["source_attachment_id"], row["event_id"], row["reconciliation_class"]) for row in out["reconciliations"]}
    audit.check("V025_EIGHT_FINAL_RECIPE_RECONCILIATIONS", observed_reconciliations == expected_reconciliations and len(out["reconciliations"]) == 8, observed_reconciliations, expected_reconciliations)

    grades = data["gdt558_grade_assignments"]
    grade_keys: set[tuple[str, int]] = set()
    grade_modes: Counter[str] = Counter()
    grade_coordinates_ok = True
    for row in grades:
        key = (row["event_id"], int(row["grade_atom_position"]))
        grade_keys.add(key)
        parts = atoms(event_by_id[row["event_id"]]["final_context_recipe"])
        grade_coordinates_ok &= row["recipe"] == event_by_id[row["event_id"]]["final_context_recipe"] and parts[int(row["grade_atom_position"]) - 1] == row["grade"]
        grade_modes[row["default_host_mode"]] += 1
    audit.check("V026_333_GRADE_SOURCE_COORDINATES", len(grade_keys) == 333 and grade_coordinates_ok, len(grade_keys), 333)
    expected_grade_modes = Counter({"VISIBLE_SAME_BLOCK_ACTION_CHAIN": 151, "CONTROL_CARRIED_GRADE_VALUE": 182})
    audit.check("V027_GRADE_HOST_MODE_BALANCE", grade_modes == expected_grade_modes, grade_modes, expected_grade_modes)
    audit.check("V028_GRADE_ARTIFACT_EXACT_SOURCE_COPY", out["grades"] == grades, len(out["grades"]), 333)
    audit.check("V029_18_HAZARDS_EXACT_SOURCE_COPY", out["hazards"] == data["gdt558_grade_hazards"] and len(out["hazards"]) == 18, len(out["hazards"]), 18)
    focus_grade_keys = {(row["event_id"], int(row["focus_final_position"])) for row in focus_rows if row["focus_root"] in GRADE_ROOTS}
    audit.check("V030_ALL_GRADE_ASSIGNMENTS_JOIN_FOCUS_HOSTS", grade_keys <= focus_grade_keys, len(grade_keys & focus_grade_keys), 333)

    expected_aliases = derive_aliases(data, event_by_id)
    observed_aliases: Counter[tuple[str, str, str, str, str, str, str]] = Counter()
    for row in out["aliases"]:
        observed_aliases[(row["alias_class"], row["event_id"], row["inherited_root"], row["lexical_source_kind"], row["lexical_source_event_id"], row["lexical_source_atom_position"], f"{row['lexical_source_key']}|{row['source_layer']}")] += 1
    alias_balance = Counter((row["alias_class"], row["lexical_source_kind"]) for row in out["aliases"])
    audit.check("V031_4026_ALIASES_EXACT_SOURCE_DERIVATION", observed_aliases == expected_aliases and sum(observed_aliases.values()) == 4026, sum(observed_aliases.values()), 4026)
    expected_alias_balance = Counter({("ACTION_ALIAS", "SAME_STATEMENT_EVENT"): 1477, ("ACTION_ALIAS", "OWNER_DEFAULT"): 264, ("OBJECT_ALIAS", "SAME_STATEMENT_EVENT"): 1801, ("OBJECT_ALIAS", "OWNER_DEFAULT"): 484})
    audit.check("V032_ALIAS_SOURCE_KIND_BALANCE", alias_balance == expected_alias_balance, alias_balance, expected_alias_balance)

    expected_modifier_positions = {
        (event["event_id"], position, root)
        for event in source_events
        for position, root in enumerate(atoms(event["final_context_recipe"]), 1)
        if root in RUNNING_MODIFIERS - GRADE_ROOTS
    }
    modifier_rows = out["modifiers"]
    observed_modifier_positions = {(row["event_id"], int(row["atom_position"]), row["atom_root"]) for row in modifier_rows}
    audit.check("V033_1810_NON_GRADE_MODIFIER_POSITIONS", observed_modifier_positions == expected_modifier_positions and len(modifier_rows) == len(observed_modifier_positions) == 1810, len(observed_modifier_positions), 1810)
    scope_expected = {
        (row["event_id"], int(row["scope_atom_position_zero_based"]) + 1): (
            f"OWNER:{event_by_id[row['event_id']]['owner_id']}"
            if row["head_event_id"] == "OWNER" or "OWNER" in row["head_kind"]
            else f"ACTION:{row['head_event_id']}@{int(row['head_atom_position_zero_based']) + 1}:{row['head_root']}"
        )
        for row in data["gdt579_scope_slots"]
        if row["scope_root"] in RUNNING_MODIFIERS - GRADE_ROOTS
    }
    modifier_by_position = {(row["event_id"], int(row["atom_position"])): row for row in modifier_rows}
    observed_scope = {key: modifier_by_position[key]["primary_governor_key"] for key in scope_expected}
    audit.check("V034_SIX_NON_GRADE_SCOPE_HEADS", len(scope_expected) == 6 and observed_scope == scope_expected, observed_scope, scope_expected)

    # Independent imperative scan, including future collision guards.
    audit.check("V035_NEGATIVE_LOOKBEHIND_BLOCKS_D_STELLE", audible_action_root("an der D-Stelle") is None, audible_action_root("an der D-Stelle"), None)
    ol_guard_observed = (audible_action_root("Führe den Gang weiter."), audible_action_root("Führe den Posten zu."))
    audit.check("V036_BARE_FUEHRE_OL_CONTROL_GUARD", ol_guard_observed == (None, ("K", "führe")), ol_guard_observed, (None, ("K", "führe")))
    expected_voice_ids: set[str] = set()
    for focus_id, host in focus_by_id.items():
        audible = audible_action_root(event_by_id[host["event_id"]]["relation_resumption_voice_working_clause_de"])
        audible_root = audible[0] if audible else "NONE"
        geometry, head_root = host["attachment_geometry"], host["primary_governor_root"]
        selected = focus_id == FORCED_OCCURRENCE_ID
        if not selected and audible:
            if geometry == "OWNER_ONLY":
                selected = True
            elif geometry == "BOUNDED_NEXT_CARD_ACTION" and audible_root != head_root:
                selected = True
            elif geometry in {"PREVIOUS_CARD_ACTION", "INHERITED_ACTION"} and audible_root != head_root and focus_id not in SAFE_FOCUS_IDS:
                selected = True
        if selected:
            expected_voice_ids.add(focus_id)
    voice_rows = out["voice_repairs"]
    observed_voice_ids = {row["focus_host_id"] for row in voice_rows}
    voice_geometries = Counter(row["attachment_geometry"] for row in voice_rows)
    audit.check("V037_269_IMPERATIVE_SELECTOR_ROWS", observed_voice_ids == expected_voice_ids and len(voice_rows) == len(observed_voice_ids) == 269, len(observed_voice_ids), 269)
    expected_repair_events = {focus_by_id[focus_id]["event_id"] for focus_id in expected_voice_ids}
    audit.check("V038_232_IMPERATIVE_SELECTOR_EVENTS", len(expected_repair_events) == 232, len(expected_repair_events), 232)
    expected_geometries = Counter({"OWNER_ONLY": 128, "BOUNDED_NEXT_CARD_ACTION": 98, "PREVIOUS_CARD_ACTION": 24, "INHERITED_ACTION": 19})
    audit.check("V039_IMPERATIVE_SELECTOR_GEOMETRY", voice_geometries == expected_geometries, voice_geometries, expected_geometries)
    repair_origins = Counter(focus_id.split("-")[0] for focus_id in observed_voice_ids)
    audit.check("V040_IMPERATIVE_SELECTOR_SOURCE_BALANCE", repair_origins == Counter({"G407": 261, "G515": 8}), repair_origins, Counter({"G407": 261, "G515": 8}))

    # Physical selector heads remain distinct from effective grade-control voice heads.
    voice_head_ok = True
    voice_class_counts: Counter[str] = Counter()
    grade_voice_ids: set[str] = set()
    for row in voice_rows:
        host = focus_by_id[row["focus_host_id"]]
        physical = (
            f"OWNER:{host['owner_id']}"
            if host["primary_governor_kind"] == "OWNER_CONTEXT"
            else f"{host['primary_governor_event_id']}@{host['primary_governor_atom_position']}:{host['primary_governor_root']}"
        )
        effective = host["effective_grammar_host_key"] if host["effective_grammar_host_kind"] == "CONTROL_ENVELOPE" else physical
        expected_voice_class = "GRADE_CONTROL_ENVELOPE_BEATS_EVENT_WIDE_ACTION" if host["effective_grammar_host_kind"] == "CONTROL_ENVELOPE" else "EXPLICIT_PRIMARY_HEAD_BLOCK"
        voice_class_counts[row["voice_repair_class"]] += 1
        if expected_voice_class.startswith("GRADE"):
            grade_voice_ids.add(row["focus_host_id"])
        voice_head_ok &= (
            row["selected_head_link"] == physical
            and row["selected_head_root"] == host["primary_governor_root"]
            and row["effective_grammar_host_kind"] == host["effective_grammar_host_kind"]
            and row["effective_grammar_host_key"] == host["effective_grammar_host_key"]
            and row["voice_head_link"] == effective
            and row["voice_repair_class"] == expected_voice_class
            and (not expected_voice_class.startswith("GRADE") or row["focus_root"] in GRADE_ROOTS)
        )
    expected_voice_classes = Counter({"EXPLICIT_PRIMARY_HEAD_BLOCK": 228, "GRADE_CONTROL_ENVELOPE_BEATS_EVENT_WIDE_ACTION": 41})
    audit.check("V041_PHYSICAL_SELECTOR_VS_EFFECTIVE_VOICE_HEADS", voice_head_ok, voice_head_ok, True)
    audit.check("V042_41_GRADE_CONTROL_VOICE_REPAIRS", voice_class_counts == expected_voice_classes and len(grade_voice_ids) == 41, voice_class_counts, expected_voice_classes)

    safe_rows = out["safe"]
    safe_ids = {row["focus_host_id"] for row in safe_rows}
    written_safe = {row["gdt515_attachment_id"] for row in data["gdt580_slots"] if row["gdt515_attachment_id"] != "NONE"}
    safe_bindings = {(row["focus_host_id"], row["event_id"], row["selected_head_link"]) for row in safe_rows}
    expected_safe_bindings = {("G515-A00356", "G515-E0379", "G515-E0378@3:T"), ("G515-A00357", "G515-E0379", "G515-E0378@3:T")}
    audit.check("V043_TWO_E0379_SAFE_EXCEPTIONS", safe_ids == written_safe == SAFE_FOCUS_IDS and safe_bindings == expected_safe_bindings, safe_bindings, expected_safe_bindings)
    audit.check("V044_E0379_SAFE_IDS_NOT_REPAIRED", not (SAFE_FOCUS_IDS & observed_voice_ids), SAFE_FOCUS_IDS & observed_voice_ids, set())

    e0385_clause = event_by_id["G515-E0385"]["relation_resumption_voice_working_clause_de"]
    audit.check("V045_E0385_AUDIBLE_ROOT_IS_R_NOT_D_STELLE_T", audible_action_root(e0385_clause) == ("R", "kennzeichne"), audible_action_root(e0385_clause), ("R", "kennzeichne"))
    e3963 = next(row for row in voice_rows if row["focus_host_id"] == FORCED_OCCURRENCE_ID)
    e3963_trigger = (e3963["selector_trigger_class"], e3963["selected_head_link"], e3963["audible_first_action_root"])
    audit.check("V046_E3963_SAME_ROOT_OCCURRENCE_FORCED", e3963_trigger == ("SAME_ROOT_DIFFERENT_ACTION_OCCURRENCE", "G407-E3962@4:CH", "CH"), e3963_trigger, ("SAME_ROOT_DIFFERENT_ACTION_OCCURRENCE", "G407-E3962@4:CH", "CH"))

    expected_cross_ids: set[str] = set()
    cross_boundaries_ok = True
    for focus_id, host in focus_by_id.items():
        event_id, head_event_id = host["event_id"], host["primary_governor_event_id"]
        if host["focus_root"] not in {"AL", "AR"} or head_event_id == event_id or host["primary_governor_kind"] == "OWNER_CONTEXT":
            continue
        current_actions = [root for root in atoms(event_by_id[event_id]["final_context_recipe"]) if root in ACTION_ROOTS]
        if not current_actions:
            continue
        expected_cross_ids.add(focus_id)
        current, head = event_by_id[event_id], event_by_id[head_event_id]
        cross_boundaries_ok &= (current["statement_id"], current["physical_page"], current["owner_id"]) == (head["statement_id"], head["physical_page"], head["owner_id"])
    cross_rows = out["cross_relations"]
    observed_cross_ids = {row["focus_host_id"] for row in cross_rows}
    cross_disposition = Counter(row["gdt581_voice_disposition"] for row in cross_rows)
    audit.check("V047_25_CROSS_CARD_RELATION_IDENTITIES", observed_cross_ids == expected_cross_ids and len(cross_rows) == len(observed_cross_ids) == 25 and cross_boundaries_ok, len(observed_cross_ids), 25)
    expected_disposition = Counter({"EXPLICIT_HEAD_BLOCK_REPAIR": 23, "SAFE_ALREADY_EXPLICIT_GDT580": 2})
    audit.check("V048_CROSS_CARD_RELATION_DISPOSITION_23_PLUS_2", cross_disposition == expected_disposition, cross_disposition, expected_disposition)
    cross_e3963 = next(row for row in cross_rows if row["focus_host_id"] == FORCED_OCCURRENCE_ID)
    e3963_cross = (cross_e3963["same_root_different_occurrence"], cross_e3963["head_event_id"], cross_e3963["head_atom_position"])
    audit.check("V049_E3963_CROSS_RELATION_OCCURRENCE_FLAG", e3963_cross == ("YES", "G407-E3962", "4"), e3963_cross, ("YES", "G407-E3962", "4"))

    event_repair_rows = out["event_repairs"]
    event_repairs_by_id = unique(event_repair_rows, "event_id", "event repair")
    focus_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in focus_rows:
        focus_by_event[row["event_id"]].append(row)
    modifiers_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in modifier_rows:
        modifiers_by_event[row["event_id"]].append(row)
    selected_by_event: dict[str, set[str]] = defaultdict(set)
    for row in voice_rows:
        selected_by_event[row["event_id"]].add(row["focus_host_id"])
    focus_link_total = sum(len(focus_by_event[event_id]) for event_id in expected_repair_events)
    modifier_link_total = sum(len(modifiers_by_event[event_id]) for event_id in expected_repair_events)
    event_counts_ok = True
    links_once_ok = True
    repair_roundtrip_ok = True
    repair_class_projection_ok = True
    voice_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in voice_rows:
        voice_by_event[row["event_id"]].append(row)
    for event_id in expected_repair_events:
        repair = event_repairs_by_id[event_id]
        clause = repair["content_ready_boundary_clause_de"]
        expected_event_focus_ids = {row["focus_host_id"] for row in focus_by_event[event_id]}
        observed_event_focus_ids = set(repair["represented_focus_ids"].split("|"))
        observed_selected_ids = set(repair["repair_focus_ids"].split("|"))
        event_counts_ok &= (
            int(repair["selected_repair_focus_count"]) == len(selected_by_event[event_id])
            and int(repair["represented_event_focus_count"]) == len(focus_by_event[event_id])
            and int(repair["represented_non_grade_modifier_count"]) == len(modifiers_by_event[event_id])
            and observed_event_focus_ids == expected_event_focus_ids
            and observed_selected_ids == selected_by_event[event_id]
        )
        expected_triggers = "|".join(sorted({row["selector_trigger_class"] for row in voice_by_event[event_id]}))
        expected_classes = "|".join(sorted({row["voice_repair_class"] for row in voice_by_event[event_id]}))
        repair_class_projection_ok &= repair["selector_trigger_classes"] == expected_triggers and repair["voice_repair_classes"] == expected_classes
        for host in focus_by_event[event_id]:
            marker = f"[{host['focus_host_id']}:{event_id}@{host['focus_final_position']}:{host['focus_root']}#{host['focus_occurrence_rank']}]"
            links_once_ok &= clause.count(marker) == 1
        for slot in modifiers_by_event[event_id]:
            links_once_ok &= clause.count(f"[{slot['slot_id']}:{slot['atom_root']}]") == 1
        source_clause = event_by_id[event_id]["relation_resumption_voice_working_clause_de"]
        repair_roundtrip_ok &= repair["source_gdt580_clause_de"] == source_clause and repair["gdt580_exact_roundtrip_de"] == source_clause
    audit.check("V050_232_EVENT_REPAIR_IDENTITIES", set(event_repairs_by_id) == expected_repair_events and len(event_repairs_by_id) == 232, len(event_repairs_by_id), 232)
    audit.check("V051_REPAIRED_EVENT_FULL_LINK_TOTALS", (focus_link_total, modifier_link_total) == (292, 62), (focus_link_total, modifier_link_total), (292, 62))
    audit.check("V052_ALL_292_FOCUS_AND_62_MODIFIER_LINKS_ONCE", event_counts_ok and links_once_ok, (focus_link_total, modifier_link_total, event_counts_ok, links_once_ok), (292, 62, True, True))
    audit.check("V053_EVENT_REPAIR_CLASS_PROJECTIONS", repair_class_projection_ok, repair_class_projection_ok, True)
    audit.check("V054_EVENT_REPAIR_GDT580_BACKCHANNELS", repair_roundtrip_ok, repair_roundtrip_ok, True)

    e0385_target = event_repairs_by_id["G515-E0385"]["content_ready_boundary_clause_de"]
    e0385_pattern = re.compile(
        r"\[G515-E0383@4:R\].*\[RUNNING:G515-E0385@1:D_ADDR\].*"
        r"\[G515-E0383@2:OK\].*\[G515-A00362:G515-E0385@2:AR#1\].*"
        r"\[G515-E0383@4:R\].*\[RUNNING:G515-E0385@3:D_ADDR\]"
    )
    audit.check("V055_E0385_EXPLICIT_R_OK_R_ORDER", bool(e0385_pattern.search(e0385_target)), "R→OK→R" if e0385_pattern.search(e0385_target) else "NOT_R→OK→R", "R→OK→R")
    e3963_target = event_repairs_by_id["G407-E3963"]["content_ready_boundary_clause_de"]
    e3963_ok = e3963_target.count("[G407-E3962@4:CH]") == 1 and e3963_target.count("[G407-E3963@2:CH]") == 2 and e3963_target.count("[G407-A04352:G407-E3963@1:AR#1]") == 1
    audit.check("V056_E3963_PREVIOUS_VS_LOCAL_CH_OCCURRENCES", e3963_ok, e3963_ok, True)
    explicit_blocks_ok = all(
        row["explicit_head_block_de"] in event_repairs_by_id[row["event_id"]]["content_ready_boundary_clause_de"]
        and row["explicit_head_block_de"].count(f"[{row['focus_machine_link']}]") == 1
        for row in voice_rows
    )
    audit.check("V057_ALL_269_SELECTED_BLOCKS_EXACTLY_EMBEDDED", explicit_blocks_ok, explicit_blocks_ok, True)

    target_events = out["events"]
    target_event_by_id = unique(target_events, "event_id", "content-ready event")
    event_identity_ok = [row["event_id"] for row in target_events] == [row["event_id"] for row in source_events]
    event_roundtrip_ok = True
    event_target_ok = True
    for source in source_events:
        target = target_event_by_id[source["event_id"]]
        source_clause = source["relation_resumption_voice_working_clause_de"]
        event_roundtrip_ok &= target["gdt580_exact_roundtrip_de"] == source_clause
        if source["event_id"] in event_repairs_by_id:
            event_target_ok &= target["grammar_boundary_status"] == "EXPLICIT_HEAD_BLOCK_REPAIR" and target["content_ready_boundary_clause_de"] == event_repairs_by_id[source["event_id"]]["content_ready_boundary_clause_de"]
        else:
            event_target_ok &= target["grammar_boundary_status"] == "UNCHANGED_NO_SELECTED_VOICE_CONFLICT" and target["content_ready_boundary_clause_de"] == source_clause
        event_target_ok &= target["statement_id"] == source["statement_id"] and target["final_context_recipe"] == source["final_context_recipe"]
    audit.check("V058_5122_EVENT_IDENTITIES", event_identity_ok and len(target_event_by_id) == 5122, len(target_event_by_id), 5122)
    exact_event_roundtrips = sum(target_event_by_id[event_id]["gdt580_exact_roundtrip_de"] == event_by_id[event_id]["relation_resumption_voice_working_clause_de"] for event_id in event_by_id)
    audit.check("V059_5122_EXACT_GDT580_EVENT_ROUNDTRIPS", event_roundtrip_ok and exact_event_roundtrips == 5122, exact_event_roundtrips, 5122)
    audit.check("V060_EVENT_TARGET_REPAIR_PARTITION", event_target_ok, event_target_ok, True)

    target_statements = out["statements"]
    target_statement_by_id = unique(target_statements, "statement_id", "content-ready statement")
    statement_identity_ok = [row["statement_id"] for row in target_statements] == [row["statement_id"] for row in source_statements]
    statement_roundtrip_ok = True
    statement_target_ok = True
    for source in source_statements:
        target = target_statement_by_id[source["statement_id"]]
        event_ids = source["event_ids"].split("|")
        source_join = " ".join(target_event_by_id[event_id]["gdt580_exact_roundtrip_de"] for event_id in event_ids)
        target_join = " ".join(target_event_by_id[event_id]["content_ready_boundary_clause_de"] for event_id in event_ids)
        statement_roundtrip_ok &= source_join == source["relation_resumption_voice_working_reading_de"] and target["gdt580_exact_roundtrip_de"] == source_join
        statement_target_ok &= target["grammar_content_boundary_reading_de"] == target_join and target["event_ids"] == source["event_ids"]
    audit.check("V061_793_STATEMENT_IDENTITIES", statement_identity_ok and len(target_statement_by_id) == 793, len(target_statement_by_id), 793)
    audit.check("V062_793_EXACT_GDT580_STATEMENT_ROUNDTRIPS", statement_roundtrip_ok, statement_roundtrip_ok, True)
    audit.check("V063_STATEMENTS_REBUILT_FROM_FIXED_EVENTS", statement_target_ok, statement_target_ok, True)

    target_pages = out["pages"]
    target_page_by_id = unique(target_pages, "physical_page", "content-ready page")
    page_identity_ok = [row["physical_page"] for row in target_pages] == [row["physical_page"] for row in source_pages]
    local_cards_by_page = Counter(row["physical_page"] for row in local_card_rows)
    local_components_by_page = Counter(row["physical_page"] for row in component_rows)
    names_by_page = Counter(row["physical_page"] for row in name_rows)
    page_counts_ok = all(
        int(target_page_by_id[page]["local_card_count"]) == local_cards_by_page[page]
        and int(target_page_by_id[page]["local_component_count"]) == local_components_by_page[page]
        and int(target_page_by_id[page]["local_name_slot_count"]) == names_by_page[page]
        for page in target_page_by_id
    )
    audit.check("V064_30_PAGE_IDENTITIES", page_identity_ok and len(target_page_by_id) == 30, len(target_page_by_id), 30)
    local_totals = (sum(local_cards_by_page.values()), sum(local_components_by_page.values()), sum(names_by_page.values()))
    audit.check("V065_PAGE_LOCAL_TOTALS", page_counts_ok and local_totals == (744, 1973, 107), local_totals, (744, 1973, 107))

    expected_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    expected_result_metrics = {
        "complete_slot_count": 15889,
        "content_carrier_count": 13702,
        "control_host_only_count": 2187,
        "inherited_alias_count": 4026,
        "focus_host_count": 5672,
        "final_recipe_reconciliation_count": 8,
        "safe_already_explicit_focus_count": 2,
        "focus_voice_repair_count": 269,
        "voice_repaired_event_count": 232,
        "fully_represented_focus_count_in_repaired_events": 292,
        "fully_represented_non_grade_modifier_count_in_repaired_events": 62,
        "event_count": 5122,
        "statement_count": 793,
        "page_count": 30,
        "local_card_count": 744,
        "local_component_count": 1973,
        "name_slot_count": 107,
        "exact_gdt580_event_roundtrip_count": 5122,
        "exact_gdt580_statement_roundtrip_count": 793,
        "zero_unowned_slot_count": 0,
    }
    observed_result_metrics = {key: result.get(key) for key in expected_result_metrics}
    audit.check("V066_RESULT_METRICS_MATCH_DERIVATION", observed_result_metrics == expected_result_metrics, observed_result_metrics, expected_result_metrics)
    audit.check("V067_RESULT_INPUT_HASHES", result.get("input_sha256") == expected_hashes, result.get("input_sha256"), expected_hashes)
    semantic_guards = (result.get("no_concrete_content_meaning_added"), result.get("structural_tags_distinct_from_english_translation"))
    audit.check("V068_RESULT_STRUCTURAL_SEMANTIC_GUARDS", semantic_guards == (True, True), semantic_guards, (True, True))

    failed = audit.failures
    validation = {
        "experiment_id": "GDT581",
        "validator": "INDEPENDENT_SOURCE_BASED_BOUNDARY_AUDIT",
        "status": (
            f"PASS_{len(audit.checks)}_SOURCE_BASED_CHECKS__15889_SLOTS__269_FOCUS_REPAIRS__232_EVENTS__5122_ROUNDTRIPS"
            if not failed else f"FAIL_{len(failed)}_OF_{len(audit.checks)}_SOURCE_BASED_CHECKS"
        ),
        "check_count": len(audit.checks),
        "passed_check_count": len(audit.checks) - len(failed),
        "failed_check_count": len(failed),
        "checks": audit.checks,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return validation, 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ART / "gdt581_validation.json")
    args = parser.parse_args()
    try:
        validation, status = validate(args.output)
    except Exception as exc:
        failure = {
            "experiment_id": "GDT581",
            "validator": "INDEPENDENT_SOURCE_BASED_BOUNDARY_AUDIT",
            "status": "FAIL_FATAL_VALIDATOR_EXCEPTION",
            "check_count": 1,
            "passed_check_count": 0,
            "failed_check_count": 1,
            "checks": [{
                "check_id": "V000_FATAL_VALIDATOR_EXCEPTION",
                "status": "FAIL",
                "observed": f"{type(exc).__name__}: {exc}",
                "expected": "all source and artifact derivations complete",
            }],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    summary = {key: validation[key] for key in ("experiment_id", "status", "check_count", "passed_check_count", "failed_check_count")}
    print(json.dumps(summary, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
