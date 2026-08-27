#!/usr/bin/env python3
"""Give colliding local address/variant atoms distinct learned sigla voices."""

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
BASE = ROOT / "experiments/yolo/gdt576_learned_local_sigla_voice"
OUT = BASE / "artifacts"
G574 = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
INPUTS = {
    "events": G574 / "gdt574_5122_action_count_event_edition.tsv",
    "statements": G574 / "gdt574_793_action_count_statement_edition.tsv",
    "pages": G574 / "gdt574_30_page_action_count_profiles.tsv",
    "duplicate_groups": G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv",
}
STATUS = (
    "PASS_4_FAMILY_FRAMES__12_LEARNED_SIGLA_CARDS__773_LOCAL_SLOTS__"
    "715_CLAUSES_DIFFERENTIATED__31_COLLISIONS_RESOLVED__"
    "5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
)

FRAME_SPECS = [
    {
        "family_frame_id": "GDT576-F01",
        "frame_class": "FEMININE_LOCATION",
        "frame_de": "an der {head}",
        "function_value": "STELLENVERWEIS",
    },
    {
        "family_frame_id": "GDT576-F02",
        "frame_class": "FEMININE_MARK_LOCATION",
        "frame_de": "bei der {head}",
        "function_value": "STELLENVERWEIS",
    },
    {
        "family_frame_id": "GDT576-F03",
        "frame_class": "MASCULINE_NOTE",
        "frame_de": "beim {head}",
        "function_value": "KENNVERMERK",
    },
    {
        "family_frame_id": "GDT576-F04",
        "frame_class": "FEMININE_VARIANT",
        "frame_de": "mit der {head}",
        "function_value": "VARIANTENVERWEIS",
    },
]

CARD_SPECS = [
    {"card_id": "GDT576-C01", "atom": "D_ADDR", "source_family": "ADDRESS", "head_de": "D-Stelle", "frame_id": "GDT576-F01"},
    {"card_id": "GDT576-C02", "atom": "A_ADDR", "source_family": "ADDRESS", "head_de": "A-Stelle", "frame_id": "GDT576-F01"},
    {"card_id": "GDT576-C03", "atom": "AM_ADDR", "source_family": "ADDRESS", "head_de": "AM-Stelle", "frame_id": "GDT576-F01"},
    {"card_id": "GDT576-C04", "atom": "S_ADDR", "source_family": "ADDRESS", "head_de": "S-Stelle", "frame_id": "GDT576-F01"},
    {"card_id": "GDT576-C05", "atom": "LOCAL_CHAR_F", "source_family": "ADDRESS", "head_de": "f-Kennmarke", "frame_id": "GDT576-F02"},
    {"card_id": "GDT576-C06", "atom": "M_LOCAL", "source_family": "ADDRESS", "head_de": "m-Ortsmarke", "frame_id": "GDT576-F02"},
    {"card_id": "GDT576-C07", "atom": "D_LABEL", "source_family": "ADDRESS", "head_de": "d-Vermerk", "frame_id": "GDT576-F03"},
    {"card_id": "GDT576-C08", "atom": "LOCAL_CHAR_I", "source_family": "LOCAL_VARIANT", "head_de": "i-Variante", "frame_id": "GDT576-F04"},
    {"card_id": "GDT576-C09", "atom": "LOCAL_CHAR_G", "source_family": "LOCAL_VARIANT", "head_de": "g-Variante", "frame_id": "GDT576-F04"},
    {"card_id": "GDT576-C10", "atom": "G_LABEL", "source_family": "LOCAL_VARIANT", "head_de": "G-Vermerk", "frame_id": "GDT576-F03"},
    {"card_id": "GDT576-C11", "atom": "LOCAL_CHAR_B", "source_family": "LOCAL_VARIANT", "head_de": "b-Variante", "frame_id": "GDT576-F04"},
    {"card_id": "GDT576-C12", "atom": "LOCAL_CHAR_J", "source_family": "LOCAL_VARIANT", "head_de": "j-Variante", "frame_id": "GDT576-F04"},
]
FAMILY_ATOMS = {
    "ADDRESS": {card["atom"] for card in CARD_SPECS if card["source_family"] == "ADDRESS"},
    "LOCAL_VARIANT": {card["atom"] for card in CARD_SPECS if card["source_family"] == "LOCAL_VARIANT"},
}
SOURCE_FORMS = {
    "ADDRESS": ["an der bezeichneten Stelle"],
    "LOCAL_VARIANT": ["mit der lokalen Variante i", "mit der lokalen Variante"],
}
SCOPE_SUFFIXES = {
    "PLAIN": "",
    "OUTER": " im äußeren Zweig",
    "INNER": " im inneren Zweig",
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


def compiled_source_candidates() -> list[dict[str, str]]:
    candidates = []
    for family, forms in SOURCE_FORMS.items():
        for form in forms:
            for scope, suffix in SCOPE_SUFFIXES.items():
                candidates.append({
                    "source_family": family,
                    "base_source_fragment_de": form,
                    "scope": scope,
                    "scope_suffix_de": suffix,
                    "full_source_fragment_de": form + suffix,
                })
    return sorted(candidates, key=lambda row: (-len(row["full_source_fragment_de"]), row["full_source_fragment_de"].casefold()))


def target_base(card: dict[str, str], frames: dict[str, dict[str, str]]) -> str:
    return frames[card["frame_id"]]["frame_de"].format(head=card["head_de"])


def locate_and_align(row: dict[str, str], candidates: list[dict[str, str]]) -> list[dict[str, object]]:
    text = row["action_count_working_clause_de"]
    possible: list[dict[str, object]] = []
    for candidate in candidates:
        pattern = re.compile(
            r"(?<!\w)" + re.escape(candidate["full_source_fragment_de"]) + r"(?!\w)",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            possible.append({
                **candidate,
                "source_start": match.start(),
                "source_end": match.end(),
                "source_fragment_de": match.group(),
            })
    selected: list[dict[str, object]] = []
    occupied: list[tuple[int, int]] = []
    for match in sorted(
        possible,
        key=lambda item: (
            int(item["source_start"]),
            -(int(item["source_end"]) - int(item["source_start"])),
            str(item["full_source_fragment_de"]),
        ),
    ):
        span = (int(match["source_start"]), int(match["source_end"]))
        if any(not (span[1] <= left or span[0] >= right) for left, right in occupied):
            continue
        selected.append(match)
        occupied.append(span)

    tokens = row["final_context_recipe"].split("+")
    for family, atoms in FAMILY_ATOMS.items():
        positions = [index for index, token in enumerate(tokens) if token in atoms]
        matches = sorted(
            [match for match in selected if match["source_family"] == family],
            key=lambda item: int(item["source_start"]),
        )
        if len(matches) != len(positions):
            raise RuntimeError(
                f"Local sigla alignment drift at {row['event_id']} / {family}: "
                f"{len(matches)} phrases versus {len(positions)} atoms"
            )
        for match, position in zip(matches, positions):
            match["atom"] = tokens[position]
            match["atom_position"] = position
    return sorted(selected, key=lambda item: int(item["source_start"]))


def render_event(
    source: dict[str, str],
    candidates: list[dict[str, str]],
    cards: dict[str, dict[str, str]],
    frames: dict[str, dict[str, str]],
) -> tuple[str, list[dict[str, object]], str]:
    text = source["action_count_working_clause_de"]
    matches = locate_and_align(source, candidates)
    parts = []
    cursor = 0
    target_cursor = 0
    assignments = []
    for match in matches:
        start = int(match["source_start"])
        end = int(match["source_end"])
        prefix = text[cursor:start]
        parts.append(prefix)
        target_cursor += len(prefix)
        card = cards[str(match["atom"])]
        rendered = target_base(card, frames) + str(match["scope_suffix_de"])
        source_fragment = str(match["source_fragment_de"])
        if source_fragment[0].isupper():
            rendered = rendered[0].upper() + rendered[1:]
        target_start = target_cursor
        parts.append(rendered)
        target_cursor += len(rendered)
        assignments.append({
            **match,
            "card_id": card["card_id"],
            "frame_id": card["frame_id"],
            "head_de": card["head_de"],
            "function_value": frames[card["frame_id"]]["function_value"],
            "target_fragment_de": rendered,
            "target_start": target_start,
            "target_end": target_cursor,
        })
        cursor = end
    parts.append(text[cursor:])
    target = "".join(parts)
    roundtrip = target
    for assignment in reversed(assignments):
        left = int(assignment["target_start"])
        right = int(assignment["target_end"])
        if roundtrip[left:right] != assignment["target_fragment_de"]:
            raise RuntimeError(f"Target span drift at {source['event_id']}")
        roundtrip = roundtrip[:left] + str(assignment["source_fragment_de"]) + roundtrip[right:]
    if roundtrip != text:
        raise RuntimeError(f"Local sigla roundtrip drift at {source['event_id']}")
    return target, assignments, roundtrip


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    duplicate_groups = read_tsv(INPUTS["duplicate_groups"])
    if [len(source_events), len(source_statements), len(source_pages), len(duplicate_groups)] != [5122, 793, 30, 96]:
        raise RuntimeError("Input count drift")

    frames = {row["family_frame_id"]: row for row in FRAME_SPECS}
    cards = {row["atom"]: row for row in CARD_SPECS}
    if len(frames) != 4 or len(cards) != 12:
        raise RuntimeError("Frame/card inventory drift")
    candidates = compiled_source_candidates()

    assignment_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    changed_rows: list[dict[str, object]] = []
    assignments_by_event_position: dict[tuple[str, int], dict[str, object]] = {}
    event_by_id: dict[str, dict[str, object]] = {}
    card_occurrences: Counter[str] = Counter()
    card_events: dict[str, set[str]] = defaultdict(set)
    card_pages: dict[str, set[str]] = defaultdict(set)
    card_scopes: Counter[tuple[str, str]] = Counter()

    for source in source_events:
        target, assignments, roundtrip = render_event(source, candidates, cards, frames)
        card_ids = []
        atom_positions = []
        for assignment in assignments:
            card_id = str(assignment["card_id"])
            card_ids.append(card_id)
            atom_positions.append(str(assignment["atom_position"]))
            card_occurrences[card_id] += 1
            card_events[card_id].add(source["event_id"])
            card_pages[card_id].add(source["physical_page"])
            card_scopes[(card_id, str(assignment["scope"]))] += 1
            assignment_row = {
                "assignment_ordinal": len(assignment_rows) + 1,
                "event_id": source["event_id"],
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "atom_position_zero_based": assignment["atom_position"],
                "atom": assignment["atom"],
                "source_family": assignment["source_family"],
                "function_value": assignment["function_value"],
                "learned_head_de": assignment["head_de"],
                "family_frame_id": assignment["frame_id"],
                "sigla_card_id": card_id,
                "scope": assignment["scope"],
                "source_fragment_de": assignment["source_fragment_de"],
                "target_fragment_de": assignment["target_fragment_de"],
                "source_start": assignment["source_start"],
                "source_end": assignment["source_end"],
                "target_start": assignment["target_start"],
                "target_end": assignment["target_end"],
                "guard": "LEARNED_SIGLUM_VOICE_ONLY__SOURCE_ATOM_POSITION_RETAINED",
            }
            assignment_rows.append(assignment_row)
            assignments_by_event_position[(source["event_id"], int(assignment["atom_position"]))] = assignment_row

        changed = target != source["action_count_working_clause_de"]
        event_row = {
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
            "state_marker_sequence": source["state_marker_sequence"],
            "gdt574_action_count_clause_de": source["action_count_working_clause_de"],
            "learned_sigla_working_clause_de": target,
            "gdt574_source_roundtrip_de": roundtrip,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "sigla_voice_changed": "YES" if changed else "NO",
            "sigla_occurrence_count": len(assignments),
            "sigla_card_ids": "|".join(card_ids) or "NONE",
            "source_atom_positions_zero_based": "+".join(atom_positions) or "NONE",
            "remaining_generic_address_phrase_count": len(re.findall(r"(?<!\w)an der bezeichneten Stelle(?!\w)", target, re.IGNORECASE)),
            "remaining_generic_variant_phrase_count": len(re.findall(r"(?<!\w)mit der lokalen Variante(?: i)?(?!\w)", target, re.IGNORECASE)),
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER__GDT574_SOURCE_ROUNDTRIP_EXACT",
        }
        event_rows.append(event_row)
        event_by_id[source["event_id"]] = event_row
        if changed:
            changed_rows.append({
                "changed_event_ordinal": len(changed_rows) + 1,
                "event_id": source["event_id"],
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "sigla_card_ids": "|".join(card_ids),
                "source_clause_de": source["action_count_working_clause_de"],
                "target_clause_de": target,
                "source_roundtrip_de": roundtrip,
                "guard": "GERMAN_VOICE_CHANGE_ONLY__RECIPE_AND_ROOTS_UNCHANGED",
            })

    card_rows = []
    for card in CARD_SPECS:
        card_id = card["card_id"]
        frame = frames[card["frame_id"]]
        card_rows.append({
            "sigla_card_ordinal": len(card_rows) + 1,
            "sigla_card_id": card_id,
            "atom": card["atom"],
            "source_family": card["source_family"],
            "function_value": frame["function_value"],
            "learned_head_de": card["head_de"],
            "family_frame_id": card["frame_id"],
            "rendered_phrase_de": target_base(card, frames),
            "occurrence_count": card_occurrences[card_id],
            "event_count": len(card_events[card_id]),
            "physical_page_count": len(card_pages[card_id]),
            "plain_occurrence_count": card_scopes[(card_id, "PLAIN")],
            "outer_occurrence_count": card_scopes[(card_id, "OUTER")],
            "inner_occurrence_count": card_scopes[(card_id, "INNER")],
            "guard": "COMMON_FUNCTION_PLUS_LEARNED_HEAD__NO_PRONUNCIATION_CLAIM",
        })

    frame_rows = []
    for frame in FRAME_SPECS:
        member_cards = [row for row in card_rows if row["family_frame_id"] == frame["family_frame_id"]]
        frame_rows.append({
            "family_frame_ordinal": len(frame_rows) + 1,
            **frame,
            "member_card_count": len(member_cards),
            "occurrence_count": sum(int(row["occurrence_count"]) for row in member_cards),
            "member_atoms": "+".join(row["atom"] for row in member_cards),
            "guard": "PRODUCTIVE_GERMAN_FRAME__LEARNED_HEADS_REMAIN_DISTINCT",
        })

    collision_rows = []
    different_root_groups = [row for row in duplicate_groups if row["duplicate_topology"].startswith("DIFFERENT_ROOTS")]
    for source_group in different_root_groups:
        positions = [int(value) for value in source_group["underlying_atom_positions_zero_based"].split("+")]
        target_assignments = [assignments_by_event_position[(source_group["event_id"], position)] for position in positions]
        target_fragments = [str(row["target_fragment_de"]) for row in target_assignments]
        resolved = len(set(fragment.casefold() for fragment in target_fragments)) == len(target_fragments)
        if not resolved:
            raise RuntimeError(f"Unresolved local voice collision at {source_group['duplicate_group_id']}")
        collision_rows.append({
            "collision_ordinal": len(collision_rows) + 1,
            "gdt575_duplicate_group_id": source_group["duplicate_group_id"],
            "event_id": source_group["event_id"],
            "statement_id": source_group["statement_id"],
            "physical_page": source_group["physical_page"],
            "surface": source_group["surface"],
            "final_context_recipe": source_group["final_context_recipe"],
            "source_duplicate_phrase_de": source_group["full_phrase_de"],
            "underlying_atom_sequence": source_group["underlying_atom_sequence"],
            "target_distinct_phrases_de": "|".join(target_fragments),
            "distinct_target_phrase_count": len(set(fragment.casefold() for fragment in target_fragments)),
            "collision_resolved": "YES",
            "target_clause_de": event_by_id[source_group["event_id"]]["learned_sigla_working_clause_de"],
            "guard": "DISTINCT_ANALYTICAL_SIGLA__NO_ROOT_OR_SCOPE_MERGE",
        })

    statement_rows = []
    for source in source_statements:
        ids = source["event_ids"].split("|")
        members = [event_by_id[event_id] for event_id in ids]
        source_reading = " ".join(str(row["gdt574_action_count_clause_de"]) for row in members)
        target_reading = " ".join(str(row["learned_sigla_working_clause_de"]) for row in members)
        roundtrip = " ".join(str(row["gdt574_source_roundtrip_de"]) for row in members)
        if source_reading != source["action_count_working_reading_de"] or roundtrip != source_reading:
            raise RuntimeError(f"Statement source/roundtrip drift at {source['statement_id']}")
        changed_members = [row for row in members if row["sigla_voice_changed"] == "YES"]
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
            "sigla_bearing_event_count": sum(int(row["sigla_occurrence_count"]) > 0 for row in members),
            "sigla_occurrence_count": sum(int(row["sigla_occurrence_count"]) for row in members),
            "changed_event_count": len(changed_members),
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt574_action_count_reading_de": source_reading,
            "learned_sigla_working_reading_de": target_reading,
            "gdt574_source_roundtrip_de": roundtrip,
            "sigla_statement_changed": "YES" if changed_members else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_ORDER_AND_BOUNDARIES_UNCHANGED__SOURCE_ROUNDTRIP_EXACT",
        })

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    events_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for row in event_rows:
        events_by_page[str(row["physical_page"])].append(row)
    page_rows = []
    for source in source_pages:
        events = events_by_page[source["physical_page"]]
        statements = statements_by_page[source["physical_page"]]
        changed_events = [row for row in events if row["sigla_voice_changed"] == "YES"]
        page_rows.append({
            "page_ordinal": source["page_ordinal"],
            "physical_page": source["physical_page"],
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "sigla_bearing_event_count": sum(int(row["sigla_occurrence_count"]) > 0 for row in events),
            "sigla_occurrence_count": sum(int(row["sigla_occurrence_count"]) for row in events),
            "changed_event_count": len(changed_events),
            "changed_statement_count": sum(row["sigla_statement_changed"] == "YES" for row in statements),
            "page_status": source["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED__NO_NEW_PAGE",
        })

    if (len(assignment_rows), len(changed_rows), len({row["statement_id"] for row in changed_rows}), len({row["physical_page"] for row in changed_rows})) != (773, 715, 294, 28):
        raise RuntimeError("Sigla assignment/change count drift")
    if len(collision_rows) != 31 or not all(row["collision_resolved"] == "YES" for row in collision_rows):
        raise RuntimeError("Collision resolution drift")
    if any(int(row["remaining_generic_address_phrase_count"]) or int(row["remaining_generic_variant_phrase_count"]) for row in event_rows):
        raise RuntimeError("Generic local voice remains")
    if any(row["gdt574_source_roundtrip_de"] != row["gdt574_action_count_clause_de"] for row in event_rows):
        raise RuntimeError("Event roundtrip drift")

    write_tsv(OUT / "gdt576_4_local_function_frames.tsv", frame_rows)
    write_tsv(OUT / "gdt576_12_learned_sigla_cards.tsv", card_rows)
    write_tsv(OUT / "gdt576_773_sigla_voice_assignments.tsv", assignment_rows)
    write_tsv(OUT / "gdt576_715_changed_sigla_clauses.tsv", changed_rows)
    write_tsv(OUT / "gdt576_31_resolved_surface_collisions.tsv", collision_rows)
    write_tsv(OUT / "gdt576_5122_learned_sigla_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt576_793_learned_sigla_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt576_30_page_sigla_profiles.tsv", page_rows)

    result = {
        "experiment_id": "GDT576",
        "status": STATUS,
        "input_event_count": len(source_events),
        "input_statement_count": len(source_statements),
        "input_page_count": len(source_pages),
        "function_frame_count": len(frame_rows),
        "learned_sigla_card_count": len(card_rows),
        "address_assignment_count": sum(row["source_family"] == "ADDRESS" for row in assignment_rows),
        "variant_assignment_count": sum(row["source_family"] == "LOCAL_VARIANT" for row in assignment_rows),
        "assignment_count": len(assignment_rows),
        "changed_event_count": len(changed_rows),
        "changed_state_event_count": sum(event_by_id[row["event_id"]]["state_status"] == "STATE_CARD" for row in changed_rows),
        "changed_nonstate_event_count": sum(event_by_id[row["event_id"]]["state_status"] == "NONSTATE_CARD" for row in changed_rows),
        "changed_statement_count": sum(row["sigla_statement_changed"] == "YES" for row in statement_rows),
        "changed_page_count": sum(int(row["changed_event_count"]) > 0 for row in page_rows),
        "resolved_different_root_collision_count": len(collision_rows),
        "remaining_same_root_duplicate_group_count": sum(row["duplicate_topology"].startswith("SAME_ROOT") for row in duplicate_groups),
        "remaining_generic_address_phrase_count": 0,
        "remaining_generic_variant_phrase_count": 0,
        "exact_event_roundtrip_count": sum(row["gdt574_source_roundtrip_de"] == row["gdt574_action_count_clause_de"] for row in event_rows),
        "event_input_sha256": sha256(INPUTS["events"]),
        "claim_ceiling": (
            "A German workshop voice that composes four common local-function frames with twelve learned analytical sigla heads. "
            "The heads distinguish current structural atoms but are not Voynich pronunciations, decoded lexemes or object names."
        ),
    }
    (OUT / "gdt576_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    book = [
        "# GDT576 learned local-sigla thirty-page edition",
        "",
        f"Status: `{STATUS}`.",
        "",
        "The common local functions remain compositional; the short D/A/AM/f/m/S/d and i/g/G/b/j heads are learned analytical labels.",
        "",
    ]
    for page in source_pages:
        book.extend([f"## {page['physical_page']}", ""])
        for statement in statements_by_page[page["physical_page"]]:
            book.extend([
                f"### {statement['statement_id']}",
                "",
                str(statement["learned_sigla_working_reading_de"]),
                "",
            ])
    (OUT / "GDT576_LEARNED_SIGLA_THIRTY_PAGE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
