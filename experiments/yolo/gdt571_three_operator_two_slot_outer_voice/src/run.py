#!/usr/bin/env python3
"""Factor nine OT/OL/DY sequence frames into three cards and two slots."""

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
BASE = ROOT / "experiments/yolo/gdt571_three_operator_two_slot_outer_voice"
OUT = BASE / "artifacts"
G570 = ROOT / "experiments/yolo/gdt570_five_fragment_four_join_modifier_voice/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"
INPUTS = {
    "modifier_states": G570 / "gdt570_1656_modifier_voice_state_clauses.tsv",
    "modifier_events": G570 / "gdt570_5122_modifier_voice_event_edition.tsv",
    "modifier_statements": G570 / "gdt570_793_modifier_voice_statement_edition.tsv",
    "page_profiles": G570 / "gdt570_30_page_modifier_voice_profiles.tsv",
    "template_replay": G565 / "gdt565_1656_template_replay.tsv",
    "renderer_cards": G565 / "gdt565_42_renderer_cards.tsv",
    "sequence_profiles": G557 / "gdt557_marker_sequence_profiles.tsv",
}
MARKERS = {"OT", "OL", "DY"}
MARKER_ORDER = ("OT", "OL", "DY")
VALUES = {"OT": "DANACH", "OL": "FORTSETZEN", "DY": "ABSCHLIESSEN"}
ENTRY = {"OT": "Danach", "OL": "Weiter"}
FOLLOWER = {
    "OT": "eröffne danach den nächsten Gang",
    "OL": "führe den Gang weiter",
    "DY": "schließe den Schritt",
}
CURRENT_FOLLOWER_BY_SEQUENCE = {
    "DY": "schließe den Schritt",
    "OT+DY": "schließe den Schritt",
    "OL+DY": "schließe den Schritt",
    "OT+OL": "weiterführen",
    "OL+OL": "nochmals weiterführen",
    "OL+OT": "danach nächsten Gang eröffnen",
    "DY+OL": "schließe den Schritt; danach weiterführen",
}
SEQUENCE_ORDER = ("OL", "DY", "OT", "OT+DY", "OL+DY", "OT+OL", "OL+OL", "DY+OL", "OL+OT")
STATUS = (
    "PASS_3_OPERATOR_CARDS__5_POSITION_REALIZATIONS__2_SLOT_RULES__9_SEQUENCES__"
    "1870_MARKERS__54_FINITE_FOLLOWERS__ZERO_ROOT_CHANGE"
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


def marker_sequence(recipe: str) -> list[str]:
    return [atom for atom in recipe.split("+") if atom in MARKERS]


def assign_slots(sequence: list[str]) -> tuple[str, list[str]]:
    if not sequence:
        raise RuntimeError("State card without OT/OL/DY marker")
    if sequence[0] in ENTRY:
        return sequence[0], sequence[1:]
    return "NONE", sequence


def target_follower(sequence: list[str]) -> str:
    _, followers = assign_slots(sequence)
    return "; ".join(FOLLOWER[marker] for marker in followers) if followers else "NONE"


def transform_clause(current: str, sequence: list[str]) -> str:
    sequence_key = "+".join(sequence)
    entry, followers = assign_slots(sequence)
    if entry != "NONE" and not current.startswith(ENTRY[entry]):
        raise RuntimeError(f"Entry fragment drift for {sequence_key}: {current}")
    if not followers:
        return current
    old_tail = CURRENT_FOLLOWER_BY_SEQUENCE[sequence_key]
    suffix = f"; {old_tail}."
    if not current.endswith(suffix):
        raise RuntimeError(f"Follower tail drift for {sequence_key}: {current}")
    new_tail = "; ".join(FOLLOWER[marker] for marker in followers)
    return current[: -len(suffix)] + f"; {new_tail}."


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    states = read_tsv(INPUTS["modifier_states"])
    events = read_tsv(INPUTS["modifier_events"])
    statements = read_tsv(INPUTS["modifier_statements"])
    pages = read_tsv(INPUTS["page_profiles"])
    replay = read_tsv(INPUTS["template_replay"])
    renderer_cards = read_tsv(INPUTS["renderer_cards"])
    old_profiles = read_tsv(INPUTS["sequence_profiles"])
    counts = [len(states), len(events), len(statements), len(pages), len(replay), len(renderer_cards), len(old_profiles)]
    if counts != [1656, 5122, 793, 30, 1656, 42, 9]:
        raise RuntimeError(f"Input count drift: {counts}")

    replay_by_id = {row["event_id"]: row for row in replay}
    state_by_id = {row["event_id"]: row for row in states}
    if len(replay_by_id) != 1656 or set(replay_by_id) != set(state_by_id):
        raise RuntimeError("State/template key drift")
    old_profile_by_sequence = {row["marker_sequence"]: row for row in old_profiles}
    old_frames = [row for row in renderer_cards if row["card_class"] == "STATE_FRAME"]
    if len(old_frames) != 9 or set(old_profile_by_sequence) != set(SEQUENCE_ORDER):
        raise RuntimeError("Nine-frame inventory drift")

    sequence_counter: Counter[str] = Counter()
    marker_counter: Counter[str] = Counter()
    slot_counter: Counter[tuple[str, str]] = Counter()
    marker_event_sets: dict[str, set[str]] = defaultdict(set)
    marker_page_sets: dict[str, set[str]] = defaultdict(set)
    changed_marker_counter: Counter[str] = Counter()
    assignments: list[dict[str, object]] = []
    state_rows: list[dict[str, object]] = []
    changed_rows: list[dict[str, object]] = []
    target_by_event: dict[str, str] = {}
    sequence_changed_counter: Counter[str] = Counter()

    assignment_ordinal = 0
    for state_ordinal, row in enumerate(states, 1):
        event_id = row["event_id"]
        replay_row = replay_by_id[event_id]
        sequence = marker_sequence(row["final_context_recipe"])
        sequence_key = "+".join(sequence)
        if sequence_key != replay_row["state_marker_sequence"]:
            raise RuntimeError(f"Marker-sequence drift at {event_id}")
        if sequence_key not in old_profile_by_sequence:
            raise RuntimeError(f"Unknown marker sequence {sequence_key}")
        entry, followers = assign_slots(sequence)
        current = row["modifier_voice_working_clause_de"]
        target = transform_clause(current, sequence)
        changed = target != current
        if changed:
            sequence_changed_counter[sequence_key] += 1
        target_by_event[event_id] = target
        sequence_counter[sequence_key] += 1

        marker_positions = [index for index, atom in enumerate(row["final_context_recipe"].split("+"), 1) if atom in MARKERS]
        if len(marker_positions) != len(sequence):
            raise RuntimeError(f"Marker-position drift at {event_id}")
        for marker_ordinal, (marker, atom_position) in enumerate(zip(sequence, marker_positions), 1):
            assignment_ordinal += 1
            slot = "ENTRY_PREFIX" if entry != "NONE" and marker_ordinal == 1 else "FOLLOWER_SUFFIX"
            phrase = ENTRY[marker] if slot == "ENTRY_PREFIX" else FOLLOWER[marker]
            occurrence_changed = slot == "FOLLOWER_SUFFIX" and marker in {"OT", "OL"}
            assignments.append({
                "assignment_ordinal": assignment_ordinal,
                "event_id": event_id,
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "surface": row["surface"],
                "final_context_recipe": row["final_context_recipe"],
                "state_marker_sequence": sequence_key,
                "marker_ordinal_in_sequence": marker_ordinal,
                "recipe_atom_position": atom_position,
                "operator": marker,
                "working_value": VALUES[marker],
                "outer_slot": slot,
                "position_realization_de": phrase,
                "finite_voice_changed": "YES" if occurrence_changed else "NO",
                "guard": "EVERY_MARKER_ASSIGNED_ONCE__WRITTEN_ORDER_UNCHANGED",
            })
            marker_counter[marker] += 1
            slot_counter[(marker, slot)] += 1
            marker_event_sets[marker].add(event_id)
            marker_page_sets[marker].add(row["physical_page"])
            if occurrence_changed:
                changed_marker_counter[marker] += 1

        follower_phrase = target_follower(sequence)
        state_record = {
            "state_edition_ordinal": state_ordinal,
            "event_id": event_id,
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_id": row["owner_id"],
            "cohort": row["cohort"],
            "surface": row["surface"],
            "final_context_recipe": row["final_context_recipe"],
            "context_mode": row["context_mode"],
            "state_marker_sequence": sequence_key,
            "entry_operator": entry,
            "follower_operator_sequence": "+".join(followers) if followers else "NONE",
            "two_slot_signature": f"ENTRY_{entry}__FOLLOWER_{'+'.join(followers) if followers else 'NONE'}",
            "entry_realization_de": ENTRY[entry] if entry != "NONE" else "NONE",
            "follower_realization_de": follower_phrase,
            "gdt570_modifier_voice_clause_de": current,
            "outer_voice_working_clause_de": target,
            "owner_bound_control_clause_de": row["owner_bound_control_clause_de"],
            "outer_voice_changed": "YES" if changed else "NO",
            "state_atom_alignment": row["state_atom_alignment"],
            "guard": "THREE_OPERATORS_TWO_SLOTS__ROOTS_ORDER_AND_BOUNDARY_UNCHANGED",
        }
        state_rows.append(state_record)
        if changed:
            changed_rows.append({
                "change_ordinal": len(changed_rows) + 1,
                "event_id": event_id,
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "surface": row["surface"],
                "final_context_recipe": row["final_context_recipe"],
                "state_marker_sequence": sequence_key,
                "entry_operator": entry,
                "follower_operator_sequence": "+".join(followers),
                "before_clause_de": current,
                "after_clause_de": target,
                "change_reason": "FINITE_FOLLOWER_REALIZATION_REPLACES_SEQUENCE_SPECIFIC_INFINITIVE",
                "guard": "GERMAN_VOICE_ONLY__NO_ROOT_OR_RECIPE_CHANGE",
            })

    if sequence_counter != Counter({"OL": 619, "DY": 544, "OT": 279, "OT+DY": 86, "OL+DY": 74, "OT+OL": 38, "OL+OL": 14, "DY+OL": 1, "OL+OT": 1}):
        raise RuntimeError(f"Sequence counts drift: {sequence_counter}")
    if marker_counter != Counter({"OL": 761, "DY": 705, "OT": 404}) or len(assignments) != 1870:
        raise RuntimeError("Marker assignment drift")
    if len(changed_rows) != 54 or changed_marker_counter != Counter({"OL": 53, "OT": 1}):
        raise RuntimeError("Finite follower count drift")

    cards: list[dict[str, object]] = []
    for ordinal, marker in enumerate(MARKER_ORDER, 1):
        entry_count = slot_counter[(marker, "ENTRY_PREFIX")]
        follower_count = slot_counter[(marker, "FOLLOWER_SUFFIX")]
        cards.append({
            "operator_card_ordinal": ordinal,
            "operator_card_id": f"GDT571-C{ordinal:02d}",
            "operator": marker,
            "unchanged_working_value": VALUES[marker],
            "entry_prefix_realization_de": ENTRY.get(marker, "NOT_LICENSED"),
            "follower_suffix_realization_de": FOLLOWER[marker],
            "entry_assignment_count": entry_count,
            "follower_assignment_count": follower_count,
            "total_marker_occurrence_count": marker_counter[marker],
            "distinct_event_count": len(marker_event_sets[marker]),
            "physical_page_count": len(marker_page_sets[marker]),
            "finite_voice_changed_occurrence_count": changed_marker_counter[marker],
            "guard": "ONE_ROOT_CARD_WITH_POSITION_REALIZATIONS__NO_SEQUENCE_MEANING",
        })

    slot_event_sets: dict[str, set[str]] = defaultdict(set)
    slot_assignment_counts: Counter[str] = Counter()
    for row in assignments:
        slot_assignment_counts[str(row["outer_slot"])] += 1
        slot_event_sets[str(row["outer_slot"])].add(str(row["event_id"]))
    slot_rules = [
        {
            "slot_rule_ordinal": 1,
            "slot_rule_id": "GDT571-S01",
            "outer_slot": "ENTRY_PREFIX",
            "selector": "FIRST_STATE_MARKER_IF_OT_OR_OL",
            "licensed_operators": "OT|OL",
            "assembly_rule": "REALIZE_BEFORE_BASE_AND_RETAIN_CONTEXT_INSERT_AFTER_PREFIX",
            "assignment_count": slot_assignment_counts["ENTRY_PREFIX"],
            "event_count": len(slot_event_sets["ENTRY_PREFIX"]),
            "guard": "AT_MOST_ONE_ENTRY_PREFIX_PER_STATE_CARD",
        },
        {
            "slot_rule_ordinal": 2,
            "slot_rule_id": "GDT571-S02",
            "outer_slot": "FOLLOWER_SUFFIX",
            "selector": "EVERY_DY_AND_EVERY_MARKER_AFTER_THE_ENTRY_PREFIX",
            "licensed_operators": "OT|OL|DY",
            "assembly_rule": "REALIZE_AFTER_BASE_IN_WRITTEN_MARKER_ORDER_WITH_SEMICOLON",
            "assignment_count": slot_assignment_counts["FOLLOWER_SUFFIX"],
            "event_count": len(slot_event_sets["FOLLOWER_SUFFIX"]),
            "guard": "NO_REORDERING_OR_SEQUENCE_SPECIFIC_FOLLOWER_STRING",
        },
    ]

    sequence_profiles: list[dict[str, object]] = []
    for ordinal, sequence_key in enumerate(SEQUENCE_ORDER, 1):
        sequence = sequence_key.split("+")
        entry, followers = assign_slots(sequence)
        old = old_profile_by_sequence[sequence_key]
        count = sequence_counter[sequence_key]
        if int(old["event_count"]) != count:
            raise RuntimeError(f"GDT557 profile drift for {sequence_key}")
        examples = [row["outer_voice_working_clause_de"] for row in state_rows if row["state_marker_sequence"] == sequence_key][:3]
        sequence_profiles.append({
            "sequence_profile_ordinal": ordinal,
            "state_marker_sequence": sequence_key,
            "event_count": count,
            "marker_occurrence_count": count * len(sequence),
            "entry_operator": entry,
            "follower_operator_sequence": "+".join(followers) if followers else "NONE",
            "entry_realization_de": ENTRY[entry] if entry != "NONE" else "NONE",
            "follower_realization_de": target_follower(sequence),
            "two_slot_signature": f"ENTRY_{entry}__FOLLOWER_{'+'.join(followers) if followers else 'NONE'}",
            "gdt557_working_reading_de": old["working_reading_de"],
            "finite_voice_changed_event_count": sequence_changed_counter[sequence_key],
            "statement_final_event_count": old["statement_final_event_count"],
            "example_outer_voice_clauses_de": " || ".join(examples),
            "guard": "NINE_OBSERVED_SEQUENCES_FACTORIZED_WITHOUT_SEQUENCE_CARD",
        })

    source_event_by_id = {row["event_id"]: row for row in events}
    event_rows: list[dict[str, object]] = []
    nonstate_unchanged = 0
    for ordinal, row in enumerate(events, 1):
        event_id = row["event_id"]
        state_status = row["state_status"]
        current = row["modifier_voice_working_clause_de"]
        if event_id in target_by_event:
            target = target_by_event[event_id]
            sequence_key = replay_by_id[event_id]["state_marker_sequence"]
            changed = target != current
        else:
            target = current
            sequence_key = "NOT_APPLICABLE"
            changed = False
            nonstate_unchanged += 1
        event_rows.append({
            "edition_event_ordinal": ordinal,
            "event_id": event_id,
            "statement_id": row["statement_id"],
            "card_ordinal_in_statement": row["card_ordinal_in_statement"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_id": row["owner_id"],
            "surface": row["surface"],
            "final_context_recipe": row["final_context_recipe"],
            "state_status": state_status,
            "state_marker_sequence": sequence_key,
            "gdt570_modifier_voice_clause_de": current,
            "outer_voice_working_clause_de": target,
            "owner_bound_control_clause_de": row["owner_bound_control_clause_de"],
            "outer_voice_changed": "YES" if changed else "NO",
            "state_atom_alignment": row["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER__NONSTATE_TEXT_BYTE_UNCHANGED",
        })
    if len(source_event_by_id) != 5122 or nonstate_unchanged != 3466:
        raise RuntimeError("Complete event/nonstate parity drift")

    event_rows_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        event_rows_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    changed_statement_ids: set[str] = set()
    for ordinal, source in enumerate(statements, 1):
        statement_id = source["statement_id"]
        local = event_rows_by_statement[statement_id]
        current_reading = " ".join(str(row["gdt570_modifier_voice_clause_de"]) for row in local)
        target_reading = " ".join(str(row["outer_voice_working_clause_de"]) for row in local)
        if current_reading != source["modifier_voice_working_reading_de"]:
            raise RuntimeError(f"Source statement reconstruction drift at {statement_id}")
        changed_count = sum(row["outer_voice_changed"] == "YES" for row in local)
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
            "changed_outer_state_event_count": changed_count,
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt570_modifier_voice_reading_de": current_reading,
            "outer_voice_working_reading_de": target_reading,
            "owner_bound_control_reading_de": source["owner_bound_control_reading_de"],
            "outer_voice_statement_changed": "YES" if changed_count else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED",
        })

    page_statement_ids: dict[str, set[str]] = defaultdict(set)
    changed_page_statement_ids: dict[str, set[str]] = defaultdict(set)
    page_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        page = str(row["physical_page"])
        page_events[page].append(row)
        page_statement_ids[page].add(str(row["statement_id"]))
        if row["outer_voice_changed"] == "YES":
            changed_page_statement_ids[page].add(str(row["statement_id"]))
    page_rows: list[dict[str, object]] = []
    changed_pages: set[str] = set()
    for ordinal, source in enumerate(pages, 1):
        page = source["physical_page"]
        local = page_events.get(page, [])
        local_sequences = Counter(str(row["state_marker_sequence"]) for row in local if row["state_marker_sequence"] != "NOT_APPLICABLE")
        changed_count = sum(row["outer_voice_changed"] == "YES" for row in local)
        if changed_count:
            changed_pages.add(page)
        marker_count = sum(len(key.split("+")) * count for key, count in local_sequences.items())
        page_rows.append({
            "page_ordinal": ordinal,
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "state_marker_occurrence_count": marker_count,
            "observed_state_sequences": "|".join(key for key in SEQUENCE_ORDER if local_sequences[key]) or "NONE",
            "changed_outer_state_event_count": changed_count,
            "changed_outer_statement_count": len(changed_page_statement_ids[page]),
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED",
        })

    book_lines = [
        "# GDT571 outer-voice thirty-page working edition",
        "",
        "Three OT/OL/DY cards, five observed position realizations and two outer slots generate all nine state-marker sequences.",
        "All roots and written marker orders are unchanged.",
        "",
        f"Events: {len(event_rows)} · statements: {len(statement_rows)} · pages: {len(page_rows)} · changed state clauses: {len(changed_rows)}.",
        "",
    ]
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for page in page_rows:
        page_id = str(page["physical_page"])
        book_lines.extend([f"## {page_id}", ""])
        local = statements_by_page.get(page_id, [])
        if not local:
            book_lines.extend(["_No admitted running statements._", ""])
            continue
        for row in local:
            book_lines.extend([f"{row['edition_statement_ordinal']}. {row['outer_voice_working_reading_de']}", ""])
    (OUT / "GDT571_OUTER_VOICE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book_lines), encoding="utf-8")

    artifacts = {
        "cards": OUT / "gdt571_3_operator_voice_cards.tsv",
        "slots": OUT / "gdt571_2_outer_slot_rules.tsv",
        "sequences": OUT / "gdt571_9_sequence_factorizations.tsv",
        "assignments": OUT / "gdt571_1870_marker_slot_assignments.tsv",
        "changes": OUT / "gdt571_54_changed_outer_clauses.tsv",
        "states": OUT / "gdt571_1656_outer_voice_state_clauses.tsv",
        "events": OUT / "gdt571_5122_outer_voice_event_edition.tsv",
        "statements": OUT / "gdt571_793_outer_voice_statement_edition.tsv",
        "pages": OUT / "gdt571_30_page_outer_voice_profiles.tsv",
    }
    write_tsv(artifacts["cards"], cards)
    write_tsv(artifacts["slots"], slot_rules)
    write_tsv(artifacts["sequences"], sequence_profiles)
    write_tsv(artifacts["assignments"], assignments)
    write_tsv(artifacts["changes"], changed_rows)
    write_tsv(artifacts["states"], state_rows)
    write_tsv(artifacts["events"], event_rows)
    write_tsv(artifacts["statements"], statement_rows)
    write_tsv(artifacts["pages"], page_rows)

    result = {
        "experiment_id": "GDT571",
        "status": STATUS,
        "metrics": {
            "old_sequence_frame_count": 9,
            "operator_voice_card_count": 3,
            "position_realization_count": 5,
            "outer_slot_rule_count": 2,
            "observed_state_sequence_count": 9,
            "state_marker_occurrence_count": len(assignments),
            "entry_prefix_assignment_count": slot_assignment_counts["ENTRY_PREFIX"],
            "follower_suffix_assignment_count": slot_assignment_counts["FOLLOWER_SUFFIX"],
            "entryless_state_event_count": sum(1 for row in state_rows if row["entry_operator"] == "NONE"),
            "single_marker_state_event_count": sum(1 for row in state_rows if "+" not in str(row["state_marker_sequence"])),
            "multi_marker_state_event_count": sum(1 for row in state_rows if "+" in str(row["state_marker_sequence"])),
            "finite_follower_changed_occurrence_count": sum(changed_marker_counter.values()),
            "changed_state_event_count": len(changed_rows),
            "unchanged_state_event_count": len(state_rows) - len(changed_rows),
            "changed_statement_count": len(changed_statement_ids),
            "unchanged_statement_count": len(statement_rows) - len(changed_statement_ids),
            "changed_physical_page_count": len(changed_pages),
            "state_event_count": len(state_rows),
            "nonstate_event_count": len(event_rows) - len(state_rows),
            "nonstate_byte_unchanged_count": nonstate_unchanged,
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
            "book": sha256(OUT / "GDT571_OUTER_VOICE_THIRTY_PAGE_EDITION.md"),
        },
        "notes": [
            "The first OT or OL occupies the entry-prefix slot; every DY and every later marker occupies the follower-suffix slot.",
            "The only textual changes are finite follower realizations for 53 OL occurrences and one reverse-order OT occurrence.",
            "This is a German workshop-voice factorization, not a historical plaintext claim.",
        ],
    }
    result_path = OUT / "gdt571_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
