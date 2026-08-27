#!/usr/bin/env python3
"""Compress repeated within-card argument mentions into reversible pronouns."""

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
BASE = ROOT / "experiments/yolo/gdt573_intra_clause_argument_pronoun_voice"
OUT = BASE / "artifacts"
G572 = ROOT / "experiments/yolo/gdt572_complete_nonstate_bracket_voice/artifacts"
INPUTS = {
    "events": G572 / "gdt572_5122_bracket_free_event_edition.tsv",
    "statements": G572 / "gdt572_793_bracket_free_statement_edition.tsv",
    "pages": G572 / "gdt572_30_page_bracket_voice_profiles.tsv",
    "argument_forms": G572 / "gdt572_20_nonstate_carried_argument_forms.tsv",
}
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ROOT_ORDER = ("Y", "AIIN", "AIN", "OR")
PRONOUN_RE = re.compile(r"\b(?:ihn|sie|beide)\b")
BRACKET_RE = re.compile(r"\[[^\]]+\]")
STATUS = (
    "PASS_22_ANAPHOR_CARDS__854_REPEAT_GROUPS__1046_LATER_ARGUMENT_MENTIONS_"
    "COVERED_BY_1043_ANAPHORS__841_CLAUSES__5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
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


def exact_matches(text: str, phrase: str) -> list[re.Match[str]]:
    return list(re.finditer(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text))


def expand_pronouns(target: str, replacements: list[dict[str, object]]) -> str:
    matches = list(PRONOUN_RE.finditer(target))
    if len(matches) != len(replacements):
        raise RuntimeError(f"Pronoun/backchannel count mismatch: {len(matches)} vs {len(replacements)}")
    parts: list[str] = []
    cursor = 0
    for match, replacement in zip(matches, replacements):
        if match.group() != replacement["pronoun_de"]:
            raise RuntimeError("Pronoun/backchannel order mismatch")
        parts.extend([target[cursor : match.start()], str(replacement["source_argument_phrase_de"])])
        cursor = match.end()
    parts.append(target[cursor:])
    return "".join(parts)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    source_forms = read_tsv(INPUTS["argument_forms"])
    if [len(source_events), len(source_statements), len(source_pages), len(source_forms)] != [5122, 793, 30, 20]:
        raise RuntimeError("GDT572 input count drift")
    if any(PRONOUN_RE.search(row["bracket_free_working_clause_de"]) for row in source_events):
        raise RuntimeError("Source edition already contains target pronouns")
    if any(BRACKET_RE.search(row["bracket_free_working_clause_de"]) for row in source_events):
        raise RuntimeError("Source edition is no longer bracket-free")

    expected_keys = {(register, root) for register in REGISTER_ORDER for root in ROOT_ORDER}
    forms_by_key = {(row["register"], row["argument_root"]): row for row in source_forms}
    if set(forms_by_key) != expected_keys:
        raise RuntimeError("Twenty-cell argument inventory drift")

    card_specs: list[dict[str, str]] = []
    variants_by_register: dict[str, list[dict[str, str]]] = defaultdict(list)
    ordered_keys = [(register, root) for register in REGISTER_ORDER for root in ROOT_ORDER]
    for ordinal, key in enumerate(ordered_keys, 1):
        register, root = key
        row = forms_by_key[key]
        article = row["explicit_argument_phrase_de"].split(" ", 1)[0]
        if article not in {"den", "die"}:
            raise RuntimeError(f"Unsupported article in {row['explicit_argument_phrase_de']}")
        card_id = f"GDT573-P{ordinal:02d}"
        pronoun = "ihn" if article == "den" else "sie"
        card_specs.append({
            "pronoun_card_id": card_id,
            "register": register,
            "argument_root": root,
            "argument_scope": "SINGLE_ARGUMENT",
            "explicit_argument_phrase_de": row["explicit_argument_phrase_de"],
            "carried_argument_phrase_de": row["carried_argument_phrase_de"],
            "pronoun_de": pronoun,
            "source_card_id": row["carry_card_id"],
        })
        for form_class, phrase in (("EXPLICIT", row["explicit_argument_phrase_de"]), ("CARRIED", row["carried_argument_phrase_de"])):
            variants_by_register[register].append({
                "pronoun_card_id": card_id,
                "argument_root": root,
                "argument_scope": "SINGLE_ARGUMENT",
                "form_class": form_class,
                "phrase": phrase,
                "pronoun": pronoun,
            })

    pair_card = {
        "pronoun_card_id": "GDT573-P21",
        "register": "CELESTIAL",
        "argument_root": "Y|Y",
        "argument_scope": "PAIRED_ARGUMENT",
        "explicit_argument_phrase_de": "die beiden Positionsposten",
        "carried_argument_phrase_de": "NOT_APPLICABLE",
        "pronoun_de": "sie",
        "source_card_id": "GDT565-R38__G407-E1058",
    }
    card_specs.append(pair_card)
    variants_by_register["CELESTIAL"].append({
        "pronoun_card_id": pair_card["pronoun_card_id"],
        "argument_root": pair_card["argument_root"],
        "argument_scope": pair_card["argument_scope"],
        "form_class": "PAIRED",
        "phrase": pair_card["explicit_argument_phrase_de"],
        "pronoun": pair_card["pronoun_de"],
    })
    coordinate_card = {
        "pronoun_card_id": "GDT573-P22",
        "register": "HERBAL",
        "argument_root": "TWO_DISTINCT_MASCULINE_ROOTS",
        "argument_scope": "COORDINATED_ARGUMENTS",
        "explicit_argument_phrase_de": "maskuline Argumentform 1 und maskuline Argumentform 2",
        "carried_argument_phrase_de": "NOT_APPLICABLE",
        "pronoun_de": "beide",
        "source_card_id": "GDT573-P05/P06/P07",
    }
    card_specs.append(coordinate_card)

    assignment_rows: list[dict[str, object]] = []
    change_rows: list[dict[str, object]] = []
    target_by_event: dict[str, str] = {}
    expansion_by_event: dict[str, str] = {}
    replacements_by_event: dict[str, list[dict[str, object]]] = {}
    group_count_by_event: Counter[str] = Counter()
    topology_group_count: Counter[tuple[str, int]] = Counter()
    topology_replacement_count: Counter[tuple[str, int]] = Counter()
    topology_events: dict[tuple[str, int], set[str]] = defaultdict(set)
    topology_pages: dict[tuple[str, int], set[str]] = defaultdict(set)
    topology_registers: dict[tuple[str, int], set[str]] = defaultdict(set)
    topology_examples: dict[tuple[str, int], list[str]] = defaultdict(list)
    card_occurrences: Counter[str] = Counter()
    card_surface_occurrences: Counter[str] = Counter()
    card_groups: Counter[str] = Counter()
    card_events: dict[str, set[str]] = defaultdict(set)
    card_pages: dict[str, set[str]] = defaultdict(set)

    group_ordinal = 0
    assignment_ordinal = 0
    anaphor_ordinal = 0
    for source in source_events:
        event_id = source["event_id"]
        clause = source["bracket_free_working_clause_de"]
        matches_by_group: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        all_spans: list[tuple[int, int, str]] = []
        for variant in variants_by_register[source["register"]]:
            group_key = (variant["argument_root"], variant["argument_scope"])
            for match in exact_matches(clause, variant["phrase"]):
                occurrence = {
                    "start": match.start(),
                    "end": match.end(),
                    "form_class": variant["form_class"],
                    "source_argument_phrase_de": variant["phrase"],
                    "pronoun_de": variant["pronoun"],
                    "pronoun_card_id": variant["pronoun_card_id"],
                    "argument_root": variant["argument_root"],
                    "argument_scope": variant["argument_scope"],
                }
                matches_by_group[group_key].append(occurrence)
                all_spans.append((match.start(), match.end(), variant["phrase"]))
        all_spans.sort()
        if any(left[1] > right[0] for left, right in zip(all_spans, all_spans[1:])):
            raise RuntimeError(f"Overlapping argument forms at {event_id}")

        local_replacements: list[dict[str, object]] = []
        ordered_groups = sorted(matches_by_group.items(), key=lambda item: min(int(hit["start"]) for hit in item[1]))
        for group_key, occurrences in ordered_groups:
            occurrences.sort(key=lambda hit: int(hit["start"]))
            if len(occurrences) < 2:
                continue
            form_classes = {str(hit["form_class"]) for hit in occurrences}
            card_ids = {str(hit["pronoun_card_id"]) for hit in occurrences}
            if len(form_classes) != 1 or len(card_ids) != 1:
                raise RuntimeError(f"Mixed repeat realization at {event_id}: {group_key}")
            group_ordinal += 1
            group_count_by_event[event_id] += 1
            form_class = str(occurrences[0]["form_class"])
            topology_key = (form_class, len(occurrences))
            topology_group_count[topology_key] += 1
            topology_replacement_count[topology_key] += len(occurrences) - 1
            topology_events[topology_key].add(event_id)
            topology_pages[topology_key].add(source["physical_page"])
            topology_registers[topology_key].add(source["register"])
            if len(topology_examples[topology_key]) < 8:
                topology_examples[topology_key].append(event_id)
            card_id = str(occurrences[0]["pronoun_card_id"])
            card_groups[card_id] += 1
            for mention_ordinal, occurrence in enumerate(occurrences[1:], 2):
                assignment_ordinal += 1
                replacement = {
                    **occurrence,
                    "assignment_ordinal": assignment_ordinal,
                    "repeat_group_ordinal": group_ordinal,
                    "mention_ordinal_for_argument": mention_ordinal,
                    "mention_count_for_argument": len(occurrences),
                }
                local_replacements.append(replacement)
                card_occurrences[card_id] += 1
                card_events[card_id].add(event_id)
                card_pages[card_id].add(source["physical_page"])

        local_replacements.sort(key=lambda replacement: int(replacement["start"]))
        if (
            len(local_replacements) == 2
            and group_count_by_event[event_id] == 2
            and all(replacement["pronoun_de"] == "ihn" for replacement in local_replacements)
        ):
            left, right = local_replacements
            if clause[int(left["end"]) : int(right["start"])] != " und ":
                raise RuntimeError(f"Ambiguous masculine repeats are not a coordinate at {event_id}")
            coordinate_id = coordinate_card["pronoun_card_id"]
            combined = {
                "start": left["start"],
                "end": right["end"],
                "form_class": "EXPLICIT_COORDINATE",
                "source_argument_phrase_de": clause[int(left["start"]) : int(right["end"])],
                "pronoun_de": "beide",
                "pronoun_card_id": coordinate_id,
                "argument_root": f"{left['argument_root']}|{right['argument_root']}",
                "argument_scope": "COORDINATED_DISTINCT_ARGUMENTS",
                "assignment_ordinal": f"{left['assignment_ordinal']}|{right['assignment_ordinal']}",
                "repeat_group_ordinal": f"{left['repeat_group_ordinal']}|{right['repeat_group_ordinal']}",
                "mention_ordinal_for_argument": "2|2",
                "mention_count_for_argument": "2|2",
                "covered_argument_mention_count": 2,
            }
            local_replacements = [combined]
            card_groups[coordinate_id] += 2
            card_occurrences[coordinate_id] += 2
            card_events[coordinate_id].add(event_id)
            card_pages[coordinate_id].add(source["physical_page"])
        else:
            for replacement in local_replacements:
                replacement["covered_argument_mention_count"] = 1

        parts: list[str] = []
        cursor = 0
        target_cursor = 0
        for replacement in local_replacements:
            start = int(replacement["start"])
            end = int(replacement["end"])
            prefix = clause[cursor:start]
            parts.append(prefix)
            target_cursor += len(prefix)
            replacement["target_start_char"] = target_cursor
            parts.append(str(replacement["pronoun_de"]))
            target_cursor += len(str(replacement["pronoun_de"]))
            replacement["target_end_char"] = target_cursor
            cursor = end
        parts.append(clause[cursor:])
        target = "".join(parts)
        expansion = expand_pronouns(target, local_replacements)
        if expansion != clause:
            raise RuntimeError(f"Argument roundtrip failed at {event_id}")
        if len(PRONOUN_RE.findall(target)) != len(local_replacements):
            raise RuntimeError(f"Pronoun count drift at {event_id}")
        target_by_event[event_id] = target
        expansion_by_event[event_id] = expansion
        replacements_by_event[event_id] = local_replacements

        for replacement in local_replacements:
            anaphor_ordinal += 1
            card_surface_occurrences[str(replacement["pronoun_card_id"])] += 1
            assignment_rows.append({
                "anaphor_ordinal": anaphor_ordinal,
                "covered_argument_mention_ordinals": replacement["assignment_ordinal"],
                "repeat_group_ordinal": replacement["repeat_group_ordinal"],
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "state_status": source["state_status"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "argument_root": replacement["argument_root"],
                "argument_scope": replacement["argument_scope"],
                "source_form_class": replacement["form_class"],
                "pronoun_card_id": replacement["pronoun_card_id"],
                "mention_ordinal_for_argument": replacement["mention_ordinal_for_argument"],
                "mention_count_for_argument": replacement["mention_count_for_argument"],
                "covered_argument_mention_count": replacement["covered_argument_mention_count"],
                "source_start_char": replacement["start"],
                "source_end_char": replacement["end"],
                "target_start_char": replacement["target_start_char"],
                "target_end_char": replacement["target_end_char"],
                "source_argument_phrase_de": replacement["source_argument_phrase_de"],
                "pronoun_de": replacement["pronoun_de"],
                "guard": "LATER_MENTION_ONLY__FULL_ARGUMENT_FRAGMENT_PRESERVED_IN_EXPANSION_CHANNEL",
            })
        if local_replacements:
            change_rows.append({
                "change_ordinal": len(change_rows) + 1,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "state_status": source["state_status"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "repeat_argument_group_count": group_count_by_event[event_id],
                "covered_later_argument_mention_count": sum(int(item["covered_argument_mention_count"]) for item in local_replacements),
                "anaphor_occurrence_count": len(local_replacements),
                "before_clause_de": clause,
                "after_clause_de": target,
                "full_argument_expansion_de": expansion,
                "guard": "WORKING_VOICE_ONLY__SOURCE_CLAUSE_EXACTLY_RESTORABLE",
            })

    inventory = (group_ordinal, assignment_ordinal, anaphor_ordinal, len(change_rows), len(topology_group_count))
    if inventory != (854, 1046, 1043, 841, 8):
        raise RuntimeError(f"Repeat inventory drift: {inventory}")
    if Counter(row["pronoun_de"] for row in assignment_rows) != Counter({"ihn": 949, "sie": 91, "beide": 3}):
        raise RuntimeError("Anaphor partition drift")
    source_classes = Counter()
    for row in assignment_rows:
        source_class = row["source_form_class"]
        count = int(row["covered_argument_mention_count"])
        source_classes["EXPLICIT" if source_class == "EXPLICIT_COORDINATE" else source_class] += count
    if source_classes != Counter({"EXPLICIT": 688, "CARRIED": 355, "PAIRED": 3}):
        raise RuntimeError(f"Source-form coverage partition drift: {source_classes}")

    card_rows: list[dict[str, object]] = []
    for ordinal, spec in enumerate(card_specs, 1):
        card_id = spec["pronoun_card_id"]
        if not card_occurrences[card_id]:
            raise RuntimeError(f"Unused pronoun card {card_id}")
        card_rows.append({
            "pronoun_card_ordinal": ordinal,
            **spec,
            "repeat_group_count": card_groups[card_id],
            "covered_later_argument_mention_count": card_occurrences[card_id],
            "surface_anaphor_occurrence_count": card_surface_occurrences[card_id],
            "event_count": len(card_events[card_id]),
            "physical_page_count": len(card_pages[card_id]),
            "guard": "GERMAN_ANAPHORIC_VOICE__NO_PORTABLE_ROOT_VALUE",
        })

    topology_rows: list[dict[str, object]] = []
    class_order = {"EXPLICIT": 0, "CARRIED": 1, "PAIRED": 2}
    for ordinal, key in enumerate(sorted(topology_group_count, key=lambda item: (class_order[item[0]], item[1])), 1):
        form_class, mention_count = key
        topology_rows.append({
            "topology_ordinal": ordinal,
            "source_form_class": form_class,
            "full_mention_count": mention_count,
            "retained_full_mention_count": 1,
            "pronoun_replacement_count_per_group": mention_count - 1,
            "repeat_group_count": topology_group_count[key],
            "replacement_occurrence_count": topology_replacement_count[key],
            "event_count": len(topology_events[key]),
            "physical_page_count": len(topology_pages[key]),
            "register_count": len(topology_registers[key]),
            "example_event_ids": "|".join(topology_examples[key]),
            "guard": "TOPOLOGY_PROFILE_ONLY__NOT_A_LONG_PHRASE_MEANING",
        })

    changed_ids = {event_id for event_id, replacements in replacements_by_event.items() if replacements}
    event_rows: list[dict[str, object]] = []
    state_changed = nonstate_changed = 0
    for ordinal, source in enumerate(source_events, 1):
        event_id = source["event_id"]
        changed = event_id in changed_ids
        if changed and source["state_status"] == "STATE_CARD":
            state_changed += 1
        if changed and source["state_status"] == "NONSTATE_CARD":
            nonstate_changed += 1
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
            "gdt572_bracket_free_clause_de": source["bracket_free_working_clause_de"],
            "pronoun_voice_working_clause_de": target_by_event[event_id],
            "full_argument_expansion_de": expansion_by_event[event_id],
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "pronoun_voice_changed": "YES" if changed else "NO",
            "repeat_argument_group_count": group_count_by_event[event_id],
            "covered_later_argument_mention_count": sum(
                int(item["covered_argument_mention_count"]) for item in replacements_by_event[event_id]
            ),
            "anaphor_occurrence_count": len(replacements_by_event[event_id]),
            "remaining_bracket_count": len(BRACKET_RE.findall(target_by_event[event_id])),
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER__FULL_ARGUMENT_ROUNDTRIP_EXACT",
        })
    if (state_changed, nonstate_changed) != (162, 679):
        raise RuntimeError(f"Changed state partition drift: {(state_changed, nonstate_changed)}")

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    changed_statement_ids: set[str] = set()
    for ordinal, source in enumerate(source_statements, 1):
        statement_id = source["statement_id"]
        local = events_by_statement[statement_id]
        before = " ".join(str(row["gdt572_bracket_free_clause_de"]) for row in local)
        after = " ".join(str(row["pronoun_voice_working_clause_de"]) for row in local)
        expansion = " ".join(str(row["full_argument_expansion_de"]) for row in local)
        if before != source["bracket_free_working_reading_de"] or expansion != before:
            raise RuntimeError(f"Statement reconstruction drift at {statement_id}")
        changed_count = sum(row["pronoun_voice_changed"] == "YES" for row in local)
        mention_count = sum(int(row["covered_later_argument_mention_count"]) for row in local)
        anaphor_count = sum(int(row["anaphor_occurrence_count"]) for row in local)
        if changed_count:
            changed_statement_ids.add(statement_id)
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
            "changed_event_count": changed_count,
            "covered_later_argument_mention_count": mention_count,
            "anaphor_occurrence_count": anaphor_count,
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt572_bracket_free_reading_de": before,
            "pronoun_voice_working_reading_de": after,
            "full_argument_expansion_de": expansion,
            "pronoun_voice_statement_changed": "YES" if changed_count else "NO",
            "end_mode": source["end_mode"],
            "remaining_bracket_count": len(BRACKET_RE.findall(after)),
            "guard": "STATEMENT_ORDER_AND_BOUNDARIES_UNCHANGED__EXPANSION_EXACT",
        })
    if len(changed_statement_ids) != 363:
        raise RuntimeError("Changed statement count drift")

    page_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    page_changed_statements: dict[str, set[str]] = defaultdict(set)
    for row in event_rows:
        page = str(row["physical_page"])
        page_events[page].append(row)
        if row["pronoun_voice_changed"] == "YES":
            page_changed_statements[page].add(str(row["statement_id"]))
    page_rows: list[dict[str, object]] = []
    changed_pages: set[str] = set()
    for ordinal, source in enumerate(source_pages, 1):
        page = source["physical_page"]
        local = page_events.get(page, [])
        changed_count = sum(row["pronoun_voice_changed"] == "YES" for row in local)
        if changed_count:
            changed_pages.add(page)
        page_rows.append({
            "page_ordinal": ordinal,
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "changed_event_count": changed_count,
            "changed_statement_count": len(page_changed_statements[page]),
            "covered_later_argument_mention_count": sum(int(row["covered_later_argument_mention_count"]) for row in local),
            "anaphor_occurrence_count": sum(int(row["anaphor_occurrence_count"]) for row in local),
            "remaining_bracket_count": 0,
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED__NO_NEW_PAGE",
        })
    if len(changed_pages) != 28:
        raise RuntimeError("Changed page count drift")

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book_lines = [
        "# GDT573 pronoun-voice thirty-page working edition",
        "",
        "Within each card the first full argument mention remains explicit; later mentions become ihn, sie or coordinated beide.",
        "The full source wording remains exactly recoverable through the expansion channel.",
        "",
        "Events: 5122 · statements: 793 · pages: 30 · changed clauses: 841 · covered later mentions: 1046 · anaphors: 1043 · exact expansions: 5122.",
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
            book_lines.extend([f"{row['edition_statement_ordinal']}. {row['pronoun_voice_working_reading_de']}", ""])
    book = OUT / "GDT573_PRONOUN_VOICE_THIRTY_PAGE_EDITION.md"
    book.write_text("\n".join(book_lines), encoding="utf-8")

    artifacts = {
        "cards": OUT / "gdt573_22_anaphor_voice_cards.tsv",
        "topologies": OUT / "gdt573_8_repeat_topology_profiles.tsv",
        "assignments": OUT / "gdt573_1043_anaphor_replacements.tsv",
        "changes": OUT / "gdt573_841_pronominalized_clauses.tsv",
        "events": OUT / "gdt573_5122_pronoun_voice_event_edition.tsv",
        "statements": OUT / "gdt573_793_pronoun_voice_statement_edition.tsv",
        "pages": OUT / "gdt573_30_page_pronoun_voice_profiles.tsv",
    }
    write_tsv(artifacts["cards"], card_rows)
    write_tsv(artifacts["topologies"], topology_rows)
    write_tsv(artifacts["assignments"], assignment_rows)
    write_tsv(artifacts["changes"], change_rows)
    write_tsv(artifacts["events"], event_rows)
    write_tsv(artifacts["statements"], statement_rows)
    write_tsv(artifacts["pages"], page_rows)

    result = {
        "experiment_id": "GDT573",
        "status": STATUS,
        "metrics": {
            "pronoun_voice_card_count": len(card_rows),
            "single_argument_card_count": 20,
            "paired_argument_card_count": 1,
            "coordinate_argument_card_count": 1,
            "repeat_topology_count": len(topology_rows),
            "repeat_argument_group_count": group_ordinal,
            "covered_later_argument_mention_count": assignment_ordinal,
            "surface_anaphor_occurrence_count": anaphor_ordinal,
            "masculine_pronoun_count": sum(row["pronoun_de"] == "ihn" for row in assignment_rows),
            "feminine_or_plural_pronoun_count": sum(row["pronoun_de"] == "sie" for row in assignment_rows),
            "coordinate_pronoun_count": sum(row["pronoun_de"] == "beide" for row in assignment_rows),
            "explicit_source_mention_count": source_classes["EXPLICIT"],
            "carried_source_mention_count": source_classes["CARRIED"],
            "paired_source_mention_count": source_classes["PAIRED"],
            "changed_event_count": len(change_rows),
            "unchanged_event_count": len(event_rows) - len(change_rows),
            "changed_state_event_count": state_changed,
            "changed_nonstate_event_count": nonstate_changed,
            "changed_statement_count": len(changed_statement_ids),
            "changed_physical_page_count": len(changed_pages),
            "exact_event_expansion_count": sum(row["full_argument_expansion_de"] == row["gdt572_bracket_free_clause_de"] for row in event_rows),
            "remaining_bracket_occurrence_count": 0,
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
        "artifact_sha256": {
            **{name: sha256(path) for name, path in artifacts.items()},
            "book": sha256(book),
        },
        "notes": [
            "Only the second and later exact mention of the same argument inside one card is pronominalized.",
            "All 1,046 later argument mentions remain in a 1,043-anaphor backchannel and all 5,122 source clauses roundtrip exactly.",
            "Three same-gender two-root coordinates use beide instead of the ambiguous ihn und ihn.",
            "Outer/inner contrasts remain explicit; the paired Y|Y card is the already licensed GDT565 phrase at G407-E1058.",
        ],
    }
    result_path = OUT / "gdt573_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
