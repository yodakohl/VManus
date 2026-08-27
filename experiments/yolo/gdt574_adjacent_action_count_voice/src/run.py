#!/usr/bin/env python3
"""Render every raw-adjacent identical action pair with reversible zweimal voice."""

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
BASE = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice"
OUT = BASE / "artifacts"
G573 = ROOT / "experiments/yolo/gdt573_intra_clause_argument_pronoun_voice/artifacts"
G568 = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts"
G500 = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix/artifacts"
INPUTS = {
    "events": G573 / "gdt573_5122_pronoun_voice_event_edition.tsv",
    "statements": G573 / "gdt573_793_pronoun_voice_statement_edition.tsv",
    "pages": G573 / "gdt573_30_page_pronoun_voice_profiles.tsv",
    "owner_action_cards": G568 / "gdt568_20_owner_action_voice_cards.tsv",
    "prior_twice_cards": G500 / "gdt500_15_repeated_action_fluency_cards.tsv",
}
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ANAPHOR_RE = re.compile(r"\b(?:ihn|sie|beide)\b")
STATUS = (
    "PASS_105_REPEAT_ACTION_EVENTS__43_RAW_ADJACENT_PAIRS__5_COUNT_CARDS__"
    "36_NEW_PLUS_7_RETAINED_TWICE__62_INTERRUPTED_ORDER_EXPLICIT__"
    "5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
)


CARD_SPECS = [
    {
        "count_card_id": "GDT574-C01", "action_root": "CH", "register_scope": "SOURCE_SECTION_T|BIOLOGICAL",
        "argument_mode": "ARGUMENT", "first_frame_de": "entnimm {argument}", "count_frame_de": "entnimm {argument} zweimal",
        "source_support": "GDT568-A06|GDT500-CH_CH",
    },
    {
        "count_card_id": "GDT574-C02", "action_root": "CH", "register_scope": "HERBAL|PHARMA",
        "argument_mode": "ARGUMENT", "first_frame_de": "nimm {argument}", "count_frame_de": "nimm {argument} zweimal",
        "source_support": "GDT568-A07|GDT500-CH_CH",
    },
    {
        "count_card_id": "GDT574-C03", "action_root": "CH", "register_scope": "CELESTIAL",
        "argument_mode": "ARGUMENT", "first_frame_de": "nimm {argument} auf", "count_frame_de": "nimm {argument} zweimal auf",
        "source_support": "GDT568-A08|GDT500-CH_CH",
    },
    {
        "count_card_id": "GDT574-C04", "action_root": "CH", "register_scope": "HERBAL",
        "argument_mode": "OBJECTLESS", "first_frame_de": "nimm", "count_frame_de": "nimm zweimal",
        "source_support": "GDT500-CH_CH_ACTIVE_ARGUMENT|CURRENT_OBJECTLESS_CARD",
    },
    {
        "count_card_id": "GDT574-C05", "action_root": "OK", "register_scope": "HERBAL",
        "argument_mode": "ARGUMENT", "first_frame_de": "setze {argument} im Arbeitsgang an", "count_frame_de": "setze {argument} im Arbeitsgang zweimal an",
        "source_support": "GDT568-A02|CURRENT_ADJACENT_OK_PAIR",
    },
]


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


def inferred_pronoun(argument: str) -> str:
    lower = argument.lower()
    return "sie" if lower.startswith("die ") or lower.startswith("dieselbe ") else "ihn"


def card_for(row: dict[str, str], action_root: str, clause: str) -> str:
    if action_root == "OK":
        if row["register"] != "HERBAL":
            raise RuntimeError(f"Unexpected adjacent OK register at {row['event_id']}")
        return "GDT574-C05"
    if action_root != "CH":
        raise RuntimeError(f"Unsupported adjacent action root {action_root} at {row['event_id']}")
    if re.match(r"^(?:Weiter: |Danach: )?(?:Nimm|nimm|Entnimm|entnimm)(?:,| und) (?:nimm|entnimm)", clause):
        return "GDT574-C04"
    if row["register"] == "CELESTIAL":
        return "GDT574-C03"
    if row["register"] in {"SOURCE_SECTION_T", "BIOLOGICAL"}:
        return "GDT574-C01"
    return "GDT574-C02"


def parse_pair(clause: str, card_id: str) -> dict[str, object]:
    prefix = r"(?P<prefix>(?:Weiter|Danach): )?"
    specs = {
        "GDT574-C01": (r"(?P<verb>Entnimm|entnimm)", r"entnimm"),
        "GDT574-C02": (r"(?P<verb>Nimm|nimm)", r"nimm"),
    }
    already = "zweimal" in clause
    if card_id in specs:
        first_re, second = specs[card_id]
        if already:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>" + first_re + r" (?P<arg>.+?) zweimal)(?P<tail>.*)$")
        else:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>" + first_re + r" (?P<arg>.+?)(?P<join>,| und) " + second + r" (?P<pro>ihn|sie))(?P<tail>.*)$")
    elif card_id == "GDT574-C03":
        if already:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Nimm|nimm) (?P<arg>.+?) zweimal auf)(?P<tail>.*)$")
        else:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Nimm|nimm) (?P<arg>.+?) auf(?P<join>,| und) nimm (?P<pro>ihn|sie) auf)(?P<tail>.*)$")
    elif card_id == "GDT574-C04":
        if already:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Nimm|nimm|Entnimm|entnimm) zweimal)(?P<tail>.*)$")
        else:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Nimm|nimm|Entnimm|entnimm)(?P<join>,| und) (?P<second>nimm|entnimm))(?P<tail>.*)$")
    elif card_id == "GDT574-C05":
        if already:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Setze|setze) (?P<arg>.+?) im Arbeitsgang zweimal an)(?P<tail>.*)$")
        else:
            pattern = re.compile(r"^" + prefix + r"(?P<pair>(?P<verb>Setze|setze) (?P<arg>.+?) im Arbeitsgang an(?P<join>,| und) setze (?P<pro>ihn|sie) im Arbeitsgang an)(?P<tail>.*)$")
    else:
        raise RuntimeError(f"Unknown count card {card_id}")
    match = pattern.match(clause)
    if match is None:
        raise RuntimeError(f"Count frame mismatch for {card_id}: {clause}")
    groups = match.groupdict()
    verb = groups["verb"]
    argument = groups.get("arg")
    if card_id == "GDT574-C01" or card_id == "GDT574-C02":
        target_pair = f"{verb} {argument} zweimal"
        second = "entnimm" if card_id == "GDT574-C01" else "nimm"
        full_expansion = groups["pair"] if not already else f"{verb} {argument}, {second} {inferred_pronoun(str(argument))}"
    elif card_id == "GDT574-C03":
        target_pair = f"{verb} {argument} zweimal auf"
        full_expansion = groups["pair"] if not already else f"{verb} {argument} auf, nimm {inferred_pronoun(str(argument))} auf"
    elif card_id == "GDT574-C04":
        target_pair = f"{verb} zweimal"
        second = "entnimm" if verb.lower() == "entnimm" else "nimm"
        full_expansion = groups["pair"] if not already else f"{verb}, {second}"
    else:
        target_pair = f"{verb} {argument} im Arbeitsgang zweimal an"
        full_expansion = groups["pair"] if not already else f"{verb} {argument} im Arbeitsgang an, setze {inferred_pronoun(str(argument))} im Arbeitsgang an"
    prefix_text = groups.get("prefix") or ""
    source_pair = groups["pair"]
    tail = groups["tail"]
    target = prefix_text + target_pair + tail
    source_start = len(prefix_text)
    source_end = source_start + len(source_pair)
    target_start = len(prefix_text)
    target_end = target_start + len(target_pair)
    return {
        "target": target,
        "source_pair": source_pair,
        "target_pair": target_pair,
        "full_expansion_pair": full_expansion,
        "source_start": source_start,
        "source_end": source_end,
        "target_start": target_start,
        "target_end": target_end,
        "already": already,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    owner_cards = read_tsv(INPUTS["owner_action_cards"])
    prior_cards = read_tsv(INPUTS["prior_twice_cards"])
    if [len(source_events), len(source_statements), len(source_pages), len(owner_cards), len(prior_cards)] != [5122, 793, 30, 20, 15]:
        raise RuntimeError("Input count drift")
    owner_by_id = {row["action_voice_card_id"]: row for row in owner_cards}
    if {"GDT568-A02", "GDT568-A06", "GDT568-A07", "GDT568-A08"} - set(owner_by_id):
        raise RuntimeError("Required owner action frames missing")
    if Counter(row["compressed_count_marker_de"] for row in prior_cards) != Counter({"zweimal": 15}):
        raise RuntimeError("GDT500 zweimal precedent drift")

    topology_rows: list[dict[str, object]] = []
    assignment_rows: list[dict[str, object]] = []
    change_rows: list[dict[str, object]] = []
    target_by_event: dict[str, str] = {}
    roundtrip_by_event: dict[str, str] = {}
    slot_expansion_by_event: dict[str, str] = {}
    classification_by_event: dict[str, str] = {}
    card_by_event: dict[str, str] = {}
    sequence_profile_count: Counter[tuple[str, str]] = Counter()
    sequence_profile_events: dict[tuple[str, str], list[str]] = defaultdict(list)
    sequence_profile_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    sequence_profile_registers: dict[tuple[str, str], set[str]] = defaultdict(set)
    card_events: dict[str, set[str]] = defaultdict(set)
    card_pages: dict[str, set[str]] = defaultdict(set)
    card_registers: dict[str, set[str]] = defaultdict(set)
    card_changed: Counter[str] = Counter()
    card_retained: Counter[str] = Counter()
    repeated_event_count = adjacent_count = interrupted_count = 0

    for source in source_events:
        event_id = source["event_id"]
        clause = source["pronoun_voice_working_clause_de"]
        tokens = source["final_context_recipe"].split("+")
        action_positions = [(index, token) for index, token in enumerate(tokens) if token in ACTIONS]
        action_sequence = [token for _, token in action_positions]
        counts = Counter(action_sequence)
        repeated_roots = [root for root in action_sequence if counts[root] > 1]
        repeated_roots = list(dict.fromkeys(repeated_roots))
        if not repeated_roots:
            target_by_event[event_id] = clause
            roundtrip_by_event[event_id] = clause
            slot_expansion_by_event[event_id] = clause
            classification_by_event[event_id] = "NO_REPEATED_ACTION_ROOT"
            card_by_event[event_id] = "NOT_APPLICABLE"
            continue

        repeated_event_count += 1
        adjacent_pairs = [(index, tokens[index]) for index in range(len(tokens) - 1) if tokens[index] in ACTIONS and tokens[index + 1] == tokens[index]]
        if len(adjacent_pairs) > 1:
            raise RuntimeError(f"Multiple raw-adjacent pairs at {event_id}")
        classification = "ADJACENT_IDENTICAL_PAIR_COUNTABLE" if adjacent_pairs else "INTERRUPTED_OR_NONADJACENT_REPEAT_ORDER_EXPLICIT"
        classification_by_event[event_id] = classification
        profile_key = ("+".join(action_sequence), classification)
        sequence_profile_count[profile_key] += 1
        if len(sequence_profile_events[profile_key]) < 8:
            sequence_profile_events[profile_key].append(event_id)
        sequence_profile_pages[profile_key].add(source["physical_page"])
        sequence_profile_registers[profile_key].add(source["register"])

        if not adjacent_pairs:
            interrupted_count += 1
            target = clause
            roundtrip = clause
            slot_expansion = clause
            card_id = "NOT_APPLICABLE"
            changed = False
            pair_atom_positions = "NONE"
            source_status = "ORDER_EXPLICIT_NOT_COUNTED"
        else:
            adjacent_count += 1
            raw_index, action_root = adjacent_pairs[0]
            card_id = card_for(source, action_root, clause)
            parsed = parse_pair(clause, card_id)
            target = str(parsed["target"])
            source_pair = str(parsed["source_pair"])
            target_pair = str(parsed["target_pair"])
            roundtrip = target[: int(parsed["target_start"])] + source_pair + target[int(parsed["target_end"]) :]
            slot_expansion = target[: int(parsed["target_start"])] + str(parsed["full_expansion_pair"]) + target[int(parsed["target_end"]) :]
            if roundtrip != clause:
                raise RuntimeError(f"Source roundtrip failed at {event_id}")
            changed = target != clause
            source_status = "NEWLY_COMPRESSED" if changed else "RETAINED_EXISTING_ZWEIMAL"
            pair_atom_positions = f"{raw_index + 1}|{raw_index + 2}"
            card_events[card_id].add(event_id)
            card_pages[card_id].add(source["physical_page"])
            card_registers[card_id].add(source["register"])
            if changed:
                card_changed[card_id] += 1
            else:
                card_retained[card_id] += 1
            assignment_rows.append({
                "assignment_ordinal": len(assignment_rows) + 1,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "state_status": source["state_status"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "action_sequence": "+".join(action_sequence),
                "repeated_action_root": action_root,
                "raw_action_atom_positions": pair_atom_positions,
                "count_card_id": card_id,
                "source_status": source_status,
                "source_start_char": parsed["source_start"],
                "source_end_char": parsed["source_end"],
                "target_start_char": parsed["target_start"],
                "target_end_char": parsed["target_end"],
                "source_action_pair_fragment_de": source_pair,
                "count_fragment_de": target_pair,
                "full_two_slot_expansion_fragment_de": parsed["full_expansion_pair"],
                "action_slot_count_retained": 2,
                "guard": "RAW_ADJACENCY_ONLY__TWO_WRITTEN_ACTION_SLOTS_RETAINED",
            })
            if changed:
                change_rows.append({
                    "change_ordinal": len(change_rows) + 1,
                    "event_id": event_id,
                    "statement_id": source["statement_id"],
                    "physical_page": source["physical_page"],
                    "register": source["register"],
                    "state_status": source["state_status"],
                    "surface": source["surface"],
                    "final_context_recipe": source["final_context_recipe"],
                    "count_card_id": card_id,
                    "before_clause_de": clause,
                    "after_clause_de": target,
                    "gdt573_source_roundtrip_de": roundtrip,
                    "full_two_slot_expansion_de": slot_expansion,
                    "guard": "COUNT_VOICE_ONLY__SOURCE_CLAUSE_EXACTLY_RESTORABLE",
                })

        target_by_event[event_id] = target
        roundtrip_by_event[event_id] = roundtrip
        slot_expansion_by_event[event_id] = slot_expansion
        card_by_event[event_id] = card_id
        topology_rows.append({
            "repeated_event_ordinal": len(topology_rows) + 1,
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "state_status": source["state_status"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "action_sequence": "+".join(action_sequence),
            "repeated_action_roots": "|".join(repeated_roots),
            "repeated_action_root_counts": "|".join(f"{root}:{counts[root]}" for root in repeated_roots),
            "raw_adjacent_pair_count": len(adjacent_pairs),
            "raw_action_atom_positions": pair_atom_positions,
            "classification": classification,
            "count_card_id": card_id,
            "count_voice_changed": "YES" if changed else "NO",
            "before_clause_de": clause,
            "after_clause_de": target,
            "guard": "COMPLETE_REPEATED_ACTION_EVENT_INVENTORY__ORDER_PRESERVED",
        })

    if (repeated_event_count, adjacent_count, interrupted_count, len(topology_rows), len(sequence_profile_count)) != (105, 43, 62, 105, 28):
        raise RuntimeError("Repeated-action inventory drift")
    if (len(assignment_rows), len(change_rows), sum(card_retained.values())) != (43, 36, 7):
        raise RuntimeError("Count assignment/change partition drift")
    if Counter(row["repeated_action_root"] for row in assignment_rows) != Counter({"CH": 42, "OK": 1}):
        raise RuntimeError("Adjacent root partition drift")

    profile_rows: list[dict[str, object]] = []
    class_order = {"ADJACENT_IDENTICAL_PAIR_COUNTABLE": 0, "INTERRUPTED_OR_NONADJACENT_REPEAT_ORDER_EXPLICIT": 1}
    for ordinal, key in enumerate(sorted(sequence_profile_count, key=lambda item: (class_order[item[1]], -sequence_profile_count[item], item[0])), 1):
        action_sequence, classification = key
        profile_rows.append({
            "profile_ordinal": ordinal,
            "action_sequence": action_sequence,
            "classification": classification,
            "event_count": sequence_profile_count[key],
            "physical_page_count": len(sequence_profile_pages[key]),
            "register_count": len(sequence_profile_registers[key]),
            "example_event_ids": "|".join(sequence_profile_events[key]),
            "guard": "ACTION_SEQUENCE_PROFILE_ONLY__RAW_RECIPE_ADJACENCY_DECIDES_COUNT_VOICE",
        })

    count_card_rows: list[dict[str, object]] = []
    for ordinal, spec in enumerate(CARD_SPECS, 1):
        card_id = spec["count_card_id"]
        if not card_events[card_id]:
            raise RuntimeError(f"Unused count card {card_id}")
        count_card_rows.append({
            "count_card_ordinal": ordinal,
            **spec,
            "eligible_event_count": len(card_events[card_id]),
            "newly_compressed_event_count": card_changed[card_id],
            "retained_existing_twice_event_count": card_retained[card_id],
            "physical_page_count": len(card_pages[card_id]),
            "observed_registers": "|".join(sorted(card_registers[card_id])),
            "guard": "GERMAN_COUNT_VOICE_ONLY__ACTION_ROOT_UNCHANGED",
        })

    changed_ids = {row["event_id"] for row in change_rows}
    event_rows: list[dict[str, object]] = []
    for ordinal, source in enumerate(source_events, 1):
        event_id = source["event_id"]
        event_rows.append({
            "edition_event_ordinal": ordinal,
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "state_marker_sequence": source["state_marker_sequence"],
            "gdt573_pronoun_voice_clause_de": source["pronoun_voice_working_clause_de"],
            "action_count_working_clause_de": target_by_event[event_id],
            "gdt573_source_roundtrip_de": roundtrip_by_event[event_id],
            "full_two_action_slot_expansion_de": slot_expansion_by_event[event_id],
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "repeated_action_classification": classification_by_event[event_id],
            "count_card_id": card_by_event[event_id],
            "action_count_changed": "YES" if event_id in changed_ids else "NO",
            "zweimal_occurrence_count": target_by_event[event_id].count("zweimal"),
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER__GDT573_SOURCE_ROUNDTRIP_EXACT",
        })
    if sum(row["action_count_changed"] == "YES" for row in event_rows if row["state_status"] == "STATE_CARD") != 0:
        raise RuntimeError("Unexpected state-card rewrite")
    if sum(row["zweimal_occurrence_count"] for row in event_rows) != 43:
        raise RuntimeError("Complete zweimal count drift")

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    changed_statement_ids: set[str] = set()
    eligible_statement_ids: set[str] = set()
    for ordinal, source in enumerate(source_statements, 1):
        statement_id = source["statement_id"]
        local = events_by_statement[statement_id]
        before = " ".join(str(row["gdt573_pronoun_voice_clause_de"]) for row in local)
        after = " ".join(str(row["action_count_working_clause_de"]) for row in local)
        roundtrip = " ".join(str(row["gdt573_source_roundtrip_de"]) for row in local)
        slot_expansion = " ".join(str(row["full_two_action_slot_expansion_de"]) for row in local)
        if before != source["pronoun_voice_working_reading_de"] or roundtrip != before:
            raise RuntimeError(f"Statement roundtrip drift at {statement_id}")
        changed_count = sum(row["action_count_changed"] == "YES" for row in local)
        eligible_count = sum(row["repeated_action_classification"] == "ADJACENT_IDENTICAL_PAIR_COUNTABLE" for row in local)
        if changed_count:
            changed_statement_ids.add(statement_id)
        if eligible_count:
            eligible_statement_ids.add(statement_id)
        statement_rows.append({
            "edition_statement_ordinal": ordinal,
            "statement_id": statement_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "state_card_count": source["state_card_count"],
            "nonstate_card_count": source["nonstate_card_count"],
            "statement_mode": source["statement_mode"],
            "eligible_adjacent_pair_event_count": eligible_count,
            "changed_event_count": changed_count,
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt573_pronoun_voice_reading_de": before,
            "action_count_working_reading_de": after,
            "gdt573_source_roundtrip_de": roundtrip,
            "full_two_action_slot_expansion_de": slot_expansion,
            "action_count_statement_changed": "YES" if changed_count else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_ORDER_AND_BOUNDARIES_UNCHANGED__SOURCE_ROUNDTRIP_EXACT",
        })
    if (len(changed_statement_ids), len(eligible_statement_ids)) != (33, 40):
        raise RuntimeError("Statement coverage drift")

    page_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    page_changed_statements: dict[str, set[str]] = defaultdict(set)
    for row in event_rows:
        page = str(row["physical_page"])
        page_events[page].append(row)
        if row["action_count_changed"] == "YES":
            page_changed_statements[page].add(str(row["statement_id"]))
    changed_pages: set[str] = set()
    eligible_pages: set[str] = set()
    page_rows: list[dict[str, object]] = []
    for ordinal, source in enumerate(source_pages, 1):
        page = source["physical_page"]
        local = page_events.get(page, [])
        changed_count = sum(row["action_count_changed"] == "YES" for row in local)
        eligible_count = sum(row["repeated_action_classification"] == "ADJACENT_IDENTICAL_PAIR_COUNTABLE" for row in local)
        if changed_count:
            changed_pages.add(page)
        if eligible_count:
            eligible_pages.add(page)
        page_rows.append({
            "page_ordinal": ordinal,
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "repeated_action_event_count": sum(row["repeated_action_classification"] != "NO_REPEATED_ACTION_ROOT" for row in local),
            "eligible_adjacent_pair_event_count": eligible_count,
            "changed_event_count": changed_count,
            "changed_statement_count": len(page_changed_statements[page]),
            "zweimal_occurrence_count": sum(int(row["zweimal_occurrence_count"]) for row in local),
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED__NO_NEW_PAGE",
        })
    if (len(changed_pages), len(eligible_pages)) != (17, 18):
        raise RuntimeError("Page coverage drift")

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book_lines = [
        "# GDT574 adjacent-action count-voice thirty-page working edition",
        "",
        "Only raw-adjacent identical action atoms receive zweimal; interrupted repeats retain their written order.",
        "All GDT573 clauses remain exactly recoverable and every counted pair retains a two-slot expansion.",
        "",
        "Events: 5122 · repeated-action events: 105 · adjacent counted pairs: 43 · newly changed clauses: 36 · interrupted repeats retained: 62.",
        "",
    ]
    for page in page_rows:
        page_id = str(page["physical_page"])
        book_lines.extend([f"## {page_id}", ""])
        local = statements_by_page.get(page_id, [])
        if not local:
            book_lines.extend(["_No admitted running statements._", ""])
            continue
        for row in local:
            book_lines.extend([f"{row['edition_statement_ordinal']}. {row['action_count_working_reading_de']}", ""])
    book = OUT / "GDT574_ACTION_COUNT_VOICE_THIRTY_PAGE_EDITION.md"
    book.write_text("\n".join(book_lines), encoding="utf-8")

    artifacts = {
        "topology_events": OUT / "gdt574_105_repeated_action_events.tsv",
        "profiles": OUT / "gdt574_28_repeated_action_sequence_profiles.tsv",
        "cards": OUT / "gdt574_5_action_count_cards.tsv",
        "assignments": OUT / "gdt574_43_adjacent_action_pair_assignments.tsv",
        "changes": OUT / "gdt574_36_changed_action_clauses.tsv",
        "events": OUT / "gdt574_5122_action_count_event_edition.tsv",
        "statements": OUT / "gdt574_793_action_count_statement_edition.tsv",
        "pages": OUT / "gdt574_30_page_action_count_profiles.tsv",
    }
    write_tsv(artifacts["topology_events"], topology_rows)
    write_tsv(artifacts["profiles"], profile_rows)
    write_tsv(artifacts["cards"], count_card_rows)
    write_tsv(artifacts["assignments"], assignment_rows)
    write_tsv(artifacts["changes"], change_rows)
    write_tsv(artifacts["events"], event_rows)
    write_tsv(artifacts["statements"], statement_rows)
    write_tsv(artifacts["pages"], page_rows)

    result = {
        "experiment_id": "GDT574",
        "status": STATUS,
        "metrics": {
            "repeated_action_event_count": repeated_event_count,
            "repeated_action_sequence_profile_count": len(profile_rows),
            "raw_adjacent_identical_pair_event_count": adjacent_count,
            "interrupted_or_nonadjacent_repeat_event_count": interrupted_count,
            "action_count_card_count": len(count_card_rows),
            "adjacent_ch_pair_count": sum(row["repeated_action_root"] == "CH" for row in assignment_rows),
            "adjacent_ok_pair_count": sum(row["repeated_action_root"] == "OK" for row in assignment_rows),
            "newly_compressed_event_count": len(change_rows),
            "retained_existing_twice_event_count": sum(card_retained.values()),
            "complete_twice_occurrence_count": sum(int(row["zweimal_occurrence_count"]) for row in event_rows),
            "unchanged_event_count": len(event_rows) - len(change_rows),
            "changed_state_event_count": 0,
            "changed_nonstate_event_count": len(change_rows),
            "changed_statement_count": len(changed_statement_ids),
            "eligible_statement_count": len(eligible_statement_ids),
            "changed_physical_page_count": len(changed_pages),
            "eligible_physical_page_count": len(eligible_pages),
            "exact_gdt573_event_roundtrip_count": sum(row["gdt573_source_roundtrip_de"] == row["gdt573_pronoun_voice_clause_de"] for row in event_rows),
            "two_action_slot_expansion_count": len(assignment_rows),
            "complete_event_count": len(event_rows),
            "complete_statement_count": len(statement_rows),
            "complete_page_count": len(page_rows),
            "new_pages": 0,
            "new_events": 0,
            "new_statements": 0,
            "new_surfaces": 0,
            "new_recipes": 0,
            "new_root_values": 0,
        },
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {**{name: sha256(path) for name, path in artifacts.items()}, "book": sha256(book)},
        "notes": [
            "Only identical action atoms adjacent in the raw recipe receive zweimal; 62 interrupted or nonadjacent repeats remain explicit.",
            "Thirty-six nonstate clauses newly compress and seven existing GDT500-style twice clauses remain unchanged.",
            "Every target clause roundtrips to GDT573, and each of the 43 count cards has a two-action-slot expansion.",
        ],
    }
    result_path = OUT / "gdt574_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
