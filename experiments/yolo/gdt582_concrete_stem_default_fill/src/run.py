#!/usr/bin/env python3
"""Build GDT582's complete exploratory concrete-default edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from defaults import (
    ACTION_NOUNS,
    BATH_STATION_DEFAULTS,
    CONTROL_DEFAULTS,
    CORE_DEFAULTS,
    DRUG_INGREDIENT_DEFAULTS,
    LOCAL_X_DEFAULTS,
    PICTURED_PLANT_DEFAULTS,
    action_noun,
    core_concept,
    core_family,
    register_gloss,
    universal_gloss,
)


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill"
OUT = BASE / "artifacts"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"

INPUTS = {
    "complete_slots": G581 / "gdt581_15889_complete_slot_ledger.tsv",
    "aliases": G581 / "gdt581_4026_inherited_alias_edges.tsv",
    "events": G581 / "gdt581_5122_content_ready_event_edition.tsv",
    "statements": G581 / "gdt581_793_content_ready_statement_edition.tsv",
    "pages": G581 / "gdt581_30_page_boundary_profiles.tsv",
    "local_cards": G581 / "gdt581_744_local_card_hosts.tsv",
    "name_slots": G581 / "gdt581_107_name_core_slots.tsv",
}

STATUS = (
    "PASS_15889_COMPLETE_DEFAULTS__13593_PRODUCTIVE_FUNCTION_SLOTS__"
    "109_LEARNED_CONTENT_SLOTS__42_CORE_STEMS__181_REGISTER_CELLS__"
    "80_CLASS_NAME_TYPES__4026_ALIAS_DEFAULTS__5122_EVENTS__793_STATEMENTS__"
    "744_LOCAL_CARDS__25_EVENT_SENSE_CHECKS__20_COMPLETE_PASSAGE_CHECKS__"
    "ZERO_EMPTY_DEFAULTS"
)

PRIORITY_SENSE_EVENTS = [
    "G407-E0230", "G407-E0063", "G407-E0336", "G407-E3154", "G407-E0930",
    "G407-E0102", "G407-E0235", "G407-E2340", "G407-E1624", "G407-E0248",
    "G407-E0226", "G407-E0607", "G515-E0385", "G515-E0379", "G407-E3963",
    "G515-E0253", "G407-E1512", "G407-E0103", "G407-E0515", "G407-E3912",
    "G515-E0211", "G407-E0015", "G407-E3923", "G407-E0953", "G407-E0486",
]

PASSAGE_STATEMENTS = [
    "G407-S002", "G407-S003", "G515-S042", "G515-S043",
    "G407-S010", "G407-S013", "G407-S020", "G407-S028",
    "G407-S041", "G407-S045", "G407-S052", "G407-S061",
    "G407-S082", "G407-S083", "G407-S086", "G407-S193",
    "G407-S649", "G407-S651", "G407-S657", "G407-S659",
]


def sense_note(register: str) -> str:
    return {
        "SOURCE_SECTION_T": "operatorisches Arbeitsgut bleibt konkret ohne Stoffzwang",
        "HERBAL": "Pflanzencharge konkret; Teil oder Art kommt aus Besitzer oder gelerntem Namen",
        "CELESTIAL": "Positions- und Tabellenrealisierung verhindert erzwungene Stoffwörter",
        "BIOLOGICAL": "Stations- und Badrealisierung hält physische Anwendung offen",
        "PHARMA": "Drogencharge konkret; einzelne Zutat kommt aus gelerntem Namensslot",
    }[register]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty table: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_join(values: list[str] | set[str]) -> str:
    return "|".join(sorted(set(values))) if values else "NONE"


def build_name_defaults(
    name_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, str]]]:
    by_type: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in name_rows:
        by_type[(row["content_class"], row["raw_name_core"])].append(row)

    star_keys = sorted(
        [key for key in by_type if key[0] == "STAR_BEARING_RING_POSITION"],
        key=lambda key: min(int(row["name_slot_ordinal"]) for row in by_type[key]),
    )
    star_default = {
        raw: f"Sternringstelle {ordinal:02d}"
        for ordinal, (_, raw) in enumerate(star_keys, 1)
    }

    expected_classes = {
        "STAR_BEARING_RING_POSITION",
        "DRUG_OR_INGREDIENT_OBJECT",
        "BATH_OR_OUTLET_STATION",
        "PICTURED_PLANT",
    }
    if {key[0] for key in by_type} != expected_classes:
        raise RuntimeError("Learned-name content-class inventory drift")
    if {
        key[1] for key in by_type if key[0] == "DRUG_OR_INGREDIENT_OBJECT"
    } != set(DRUG_INGREDIENT_DEFAULTS):
        raise RuntimeError("Drug/ingredient house-palette inventory drift")
    if {
        key[1] for key in by_type if key[0] == "BATH_OR_OUTLET_STATION"
    } != set(BATH_STATION_DEFAULTS):
        raise RuntimeError("Bath-station house-palette inventory drift")
    if {
        key[1] for key in by_type if key[0] == "PICTURED_PLANT"
    } != set(PICTURED_PLANT_DEFAULTS):
        raise RuntimeError("Pictured-plant house-palette inventory drift")

    rows: list[dict[str, object]] = []
    by_slot: dict[str, dict[str, str]] = {}
    for ordinal, key in enumerate(
        sorted(
            by_type,
            key=lambda item: min(
                int(row["name_slot_ordinal"]) for row in by_type[item]
            ),
        ),
        1,
    ):
        content_class, raw_core = key
        members = by_type[key]
        if content_class == "STAR_BEARING_RING_POSITION":
            default_de = star_default[raw_core]
            basis = "LEARNED_RING_POSITION_SEQUENCE"
        elif content_class == "DRUG_OR_INGREDIENT_OBJECT":
            default_de = DRUG_INGREDIENT_DEFAULTS[raw_core]
            basis = "CLASS_CONDITIONED_MEDIEVAL_INGREDIENT_HOUSE_PALETTE"
        elif content_class == "BATH_OR_OUTLET_STATION":
            default_de = BATH_STATION_DEFAULTS[raw_core]
            basis = "CLASS_CONDITIONED_BATH_STATION_HOUSE_PALETTE"
        else:
            default_de = PICTURED_PLANT_DEFAULTS[raw_core]
            basis = "PICTURED_PLANT_OWNER_HOUSE_DEFAULT"
        default_id = f"GDT582-N{ordinal:03d}"
        rows.append(
            {
                "name_default_ordinal": ordinal,
                "name_default_id": default_id,
                "content_class": content_class,
                "raw_name_core": raw_core,
                "occurrence_count": len(members),
                "physical_pages": stable_join([row["physical_page"] for row in members]),
                "surfaces": stable_join([row["surface"] for row in members]),
                "provisional_default_de": default_de,
                "default_basis": basis,
                "status": "REPLACEABLE_LEARNED_DEFAULT",
                "guard": "CLASS_AND_RAW_CORE_KEYED__NOT_A_PORTABLE_STEM_TRANSLATION",
            }
        )
        for member in members:
            by_slot[member["slot_id"]] = {
                "default_key": default_id,
                "core_concept": content_class,
                "default_de": default_de,
                "default_kind": "CLASS_CONDITIONED_LEARNED_NAME",
                "default_basis": basis,
            }
    if len(rows) != 80 or len(by_slot) != 107:
        raise RuntimeError("Learned-name default count drift")
    return rows, by_slot


def function_dictionary_rows(
    complete_slots: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    function_slots = [row for row in complete_slots if row["slot_value"] in CORE_DEFAULTS]
    observed_roots = {row["slot_value"] for row in function_slots}
    if observed_roots != set(CORE_DEFAULTS):
        raise RuntimeError("Productive core-stem inventory drift")

    core_rows: list[dict[str, object]] = []
    for ordinal, root in enumerate(sorted(CORE_DEFAULTS), 1):
        members = [row for row in function_slots if row["slot_value"] == root]
        core_rows.append(
            {
                "core_ordinal": ordinal,
                "root": root,
                "function_family": core_family(root),
                "invariant_core_concept": core_concept(root),
                "universal_workshop_rival_de": universal_gloss(root),
                "slot_count": len(members),
                "running_slot_count": sum(row["layer"] == "RUNNING_ATOM" for row in members),
                "local_slot_count": sum(row["layer"] == "LOCAL_COMPONENT" for row in members),
                "register_count": len({row["register"] for row in members}),
                "registers": stable_join([row["register"] for row in members]),
                "boundary_classes": stable_join([row["boundary_class"] for row in members]),
                "status": "PRODUCTIVE_CORE_WITH_REGISTER_REALIZATION",
                "guard": "ONE_SHORT_CORE_CONCEPT__NO_SENTENCE_SIZED_DICTIONARY_ENTRY",
            }
        )

    by_cell: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in function_slots:
        by_cell[(row["root"] if "root" in row else row["slot_value"], row["register"])].append(row)
    cell_rows: list[dict[str, object]] = []
    for ordinal, ((root, register), members) in enumerate(sorted(by_cell.items()), 1):
        gloss, source = register_gloss(root, register)
        cell_rows.append(
            {
                "realization_ordinal": ordinal,
                "realization_id": f"GDT582-F{ordinal:03d}",
                "root": root,
                "register": register,
                "function_family": core_family(root),
                "invariant_core_concept": core_concept(root),
                "concrete_default_de": gloss,
                "realization_source": source,
                "slot_count": len(members),
                "physical_page_count": len({row["physical_page"] for row in members}),
                "owner_count": len({row["owner"] for row in members}),
                "status": "SELECTED_REGISTER_HYBRID_DEFAULT",
                "guard": "REGISTER_REALIZES_CORE__ROOT_IDENTITY_UNCHANGED",
            }
        )
    if len(core_rows) != 42 or len(cell_rows) != 181:
        raise RuntimeError("Core or realization-cell count drift")
    return core_rows, cell_rows


def enrich_slot(
    row: dict[str, str], name_by_slot: dict[str, dict[str, str]]
) -> dict[str, object]:
    result: dict[str, object] = dict(row)
    root = row["slot_value"]
    if row["fill_status"] == "CONTROL_HOST_ONLY":
        if root not in CONTROL_DEFAULTS:
            raise RuntimeError(f"Missing control default for {root}")
        concept, default_de = CONTROL_DEFAULTS[root]
        fields = {
            "default_key": f"CONTROL:{root}",
            "core_concept": concept,
            "default_de": default_de,
            "default_kind": "STRUCTURAL_CONTROL_DEFAULT",
            "default_basis": "GDT581_CONTROL_BOUNDARY",
        }
    elif row["boundary_class"] == "LOCAL_LEARNED_NAME_SLOT":
        fields = name_by_slot[row["slot_id"]]
    elif row["boundary_class"] == "RUNNING_LEARNED_CORE":
        if row["slot_id"] not in LOCAL_X_DEFAULTS:
            raise RuntimeError(f"Missing owner-bound LOCAL_X default: {row['slot_id']}")
        concept, default_de = LOCAL_X_DEFAULTS[row["slot_id"]]
        fields = {
            "default_key": f"LOCAL_X:{row['owner']}",
            "core_concept": concept,
            "default_de": default_de,
            "default_kind": "OWNER_BOUND_LOCAL_X",
            "default_basis": "OWNER_BOUND_EXPLORATORY_MEDICAL_HOUSE_DEFAULT",
        }
    else:
        if root not in CORE_DEFAULTS:
            raise RuntimeError(f"Missing productive default for {root}")
        gloss, source = register_gloss(root, row["register"])
        fields = {
            "default_key": f"FUNCTION:{root}:{row['register']}",
            "core_concept": core_concept(root),
            "default_de": gloss,
            "default_kind": "PRODUCTIVE_REGISTER_FUNCTION",
            "default_basis": source,
        }
    result.update(
        {
            "gdt582_default_key": fields["default_key"],
            "gdt582_default_kind": fields["default_kind"],
            "gdt582_core_concept": fields["core_concept"],
            "gdt582_concrete_default_de": fields["default_de"],
            "gdt582_default_basis": fields["default_basis"],
            "gdt582_default_status": "PROVISIONAL_REPLACEABLE_DEFAULT",
            "gdt582_guard": "ONE_COMPLETE_SLOT__ONE_NONEMPTY_DEFAULT__GDT581_HOST_UNCHANGED",
        }
    )
    return result


def group_label(key: str, register: str) -> str:
    if key.startswith(("ACTION:", "LOCAL_ACTION:")):
        root = key.rsplit(":", 1)[-1]
        return f"beim {action_noun(root, register)} [{key}]"
    if key.startswith("ACTION_CHAIN:"):
        roots = key.rsplit(":", 1)[-1].split("+")
        nouns = [action_noun(root, register) for root in roots if root in CORE_DEFAULTS]
        return f"bei der Handlungskette {' + '.join(nouns)} [{key}]"
    if key.startswith("CONTROL:"):
        return f"im Steuerrahmen [{key}]"
    if key.startswith("OWNER:"):
        return f"im Besitzerrahmen [{key}]"
    if key.startswith("LOCAL_CARD:"):
        return f"auf der lokalen Karte [{key}]"
    if key.startswith(("LOCAL_RECORD:", "LOCAL_BUNDLE:")):
        return f"im lokalen Record [{key}]"
    return f"im Rahmen [{key}]"


def render_trace(rows: list[dict[str, object]]) -> str:
    ordered = sorted(rows, key=lambda row: (int(row["slot_position"]), str(row["slot_id"])))
    return " ".join(
        (
            f"[{row['slot_position']}:{row['slot_value']}="
            f"{row['gdt582_concrete_default_de']}|{row['slot_id']}|"
            f"{row['primary_governor_key']}]"
        )
        for row in ordered
    )


def render_card(rows: list[dict[str, object]], register: str) -> str:
    ordered = sorted(rows, key=lambda row: (int(row["slot_position"]), str(row["slot_id"])))
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    first_position: dict[str, int] = {}
    for row in ordered:
        key = str(row["primary_governor_key"])
        grouped[key].append(row)
        first_position[key] = min(first_position.get(key, 10**9), int(row["slot_position"]))

    blocks: list[str] = []
    represented: set[str] = set()
    for key in sorted(grouped, key=lambda item: (first_position[item], item)):
        members = grouped[key]
        action_rows = [
            row for row in members
            if row["primary_governor_kind"] == "SELF_ACTION"
        ]
        other_rows = [row for row in members if row not in action_rows]
        if action_rows:
            lead = " und ".join(
                str(row["gdt582_concrete_default_de"]) for row in action_rows
            )
            if other_rows:
                lead += ": " + ", ".join(
                    str(row["gdt582_concrete_default_de"]) for row in other_rows
                )
        else:
            lead = group_label(key, register) + ": " + ", ".join(
                str(row["gdt582_concrete_default_de"]) for row in other_rows
            )
        blocks.append(lead)
        represented.update(str(row["slot_id"]) for row in members)
    if represented != {str(row["slot_id"]) for row in ordered}:
        raise RuntimeError("Concrete renderer lost a complete slot")
    return "; ".join(blocks) + "."


def build_alias_defaults(aliases: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in aliases:
        root = row["inherited_root"]
        if root not in CORE_DEFAULTS:
            raise RuntimeError(f"Alias root lacks a productive default: {root}")
        gloss, source = register_gloss(root, row["register"])
        rows.append(
            {
                **row,
                "gdt582_default_key": f"FUNCTION:{root}:{row['register']}",
                "gdt582_core_concept": core_concept(root),
                "gdt582_inherited_default_de": gloss,
                "gdt582_default_basis": source,
                "gdt582_guard": "ALIAS_REUSES_SOURCE_DEFAULT__NO_NEW_WRITTEN_SLOT",
            }
        )
    return rows


def build_candidate_scorecard(
    complete_defaults: list[dict[str, object]], events: list[dict[str, str]]
) -> list[dict[str, object]]:
    productive = [
        row for row in complete_defaults
        if row["gdt582_default_kind"] == "PRODUCTIVE_REGISTER_FUNCTION"
    ]
    learned = [
        row for row in complete_defaults
        if row["gdt582_default_kind"] in {
            "CLASS_CONDITIONED_LEARNED_NAME", "OWNER_BOUND_LOCAL_X"
        }
    ]
    whole_keys = {
        (row["register"], row["surface"])
        for row in complete_defaults if row["fill_status"] == "CONTENT_CARRIER"
    }
    celestial_productive = sum(row["register"] == "CELESTIAL" for row in productive)
    non_table_productive = sum(
        row["register"] not in {"CELESTIAL", "SOURCE_SECTION_T"}
        for row in productive
    )
    return [
        {
            "pack_rank": 1,
            "pack_id": "REGISTER_HYBRID_CODEBOOK",
            "productive_slot_coverage": len(productive),
            "learned_slot_coverage": len(learned),
            "total_content_slot_coverage": len(productive) + len(learned),
            "dictionary_or_cell_count": 42 + 181 + 80 + 2,
            "declared_wrong_domain_slots": 0,
            "composition_rule": "ROOT_TO_CORE__REGISTER_REALIZATION__OWNER_OR_LEARNED_NAME",
            "whole_passage_result": "SELECTED__FIVE_REGISTER_READINGS_REMAIN_DISTINCT",
        },
        {
            "pack_rank": 2,
            "pack_id": "UNIVERSAL_APOTHECARY_ONLY",
            "productive_slot_coverage": len(productive),
            "learned_slot_coverage": len(learned),
            "total_content_slot_coverage": len(productive) + len(learned),
            "dictionary_or_cell_count": 42 + 80 + 2,
            "declared_wrong_domain_slots": celestial_productive,
            "composition_rule": "ONE_PHYSICAL_RECIPE_GLOSS_PER_ROOT",
            "whole_passage_result": "RETAIN_AS_RIVAL__CELESTIAL_CARDS_FORCE_SUBSTANCES",
        },
        {
            "pack_rank": 3,
            "pack_id": "UNIVERSAL_TABLE_ONLY",
            "productive_slot_coverage": len(productive),
            "learned_slot_coverage": len(learned),
            "total_content_slot_coverage": len(productive) + len(learned),
            "dictionary_or_cell_count": 42 + 80 + 2,
            "declared_wrong_domain_slots": non_table_productive,
            "composition_rule": "ONE_TABLE_GLOSS_PER_ROOT",
            "whole_passage_result": "RETAIN_AS_RIVAL__PLANT_BATH_AND_DRUG_CARDS_LOSE_OBJECTS",
        },
        {
            "pack_rank": 4,
            "pack_id": "LEARN_EVERY_REGISTER_SURFACE",
            "productive_slot_coverage": 0,
            "learned_slot_coverage": len(productive) + len(learned),
            "total_content_slot_coverage": len(productive) + len(learned),
            "dictionary_or_cell_count": len(whole_keys),
            "declared_wrong_domain_slots": 0,
            "composition_rule": "MEMORIZE_REGISTER_BY_SURFACE",
            "whole_passage_result": "REJECT_AS_BASIS__NO_COMPOUND_PREDICTION",
        },
    ]


def select_sense_events(
    events: list[dict[str, str]], slots_by_event: dict[str, list[dict[str, object]]]
) -> list[str]:
    event_by_id = {row["event_id"]: row for row in events}
    selected: list[str] = []
    for register in (
        "SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA"
    ):
        register_priority = [
            event_id for event_id in PRIORITY_SENSE_EVENTS
            if event_by_id[event_id]["register"] == register
        ]
        selected.extend(register_priority[:5])
        if len(register_priority) >= 5:
            continue
        candidates: list[tuple[int, str]] = []
        for event in events:
            if event["register"] != register or event["event_id"] not in slots_by_event:
                continue
            members = slots_by_event[event["event_id"]]
            families = {
                str(row["boundary_class"]).replace("RUNNING_", "").split("_")[0]
                for row in members if row["fill_status"] == "CONTENT_CARRIER"
            }
            score = 3 * len(families) + len(members)
            candidates.append((score, event["event_id"]))
        for _, event_id in sorted(candidates, key=lambda item: (-item[0], item[1])):
            if event_id in selected:
                continue
            selected.append(event_id)
            if sum(event_by_id[item]["register"] == register for item in selected) == 5:
                break
    if len(selected) != 25 or Counter(event_by_id[item]["register"] for item in selected) != {
        "SOURCE_SECTION_T": 5, "HERBAL": 5, "CELESTIAL": 5,
        "BIOLOGICAL": 5, "PHARMA": 5,
    }:
        raise RuntimeError("Twenty-five-event sense deck drift")
    return selected


def build_book(
    pages: list[dict[str, str]],
    events: list[dict[str, object]],
    local_cards: list[dict[str, object]],
    core_rows: list[dict[str, object]],
    name_rows: list[dict[str, object]],
) -> str:
    events_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    cards_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        events_by_page[str(row["physical_page"])].append(row)
    for row in local_cards:
        cards_by_page[str(row["physical_page"])].append(row)
    lines = [
        "# GDT582 concrete-default thirty-page edition",
        "",
        "This is an exploratory working codebook, not plaintext. Every written slot",
        "has a replaceable default; square-bracket traces preserve exact roots, slots",
        "and governors. Specific ingredient names are class-conditioned learned cards.",
        "The forty-two productive entries are GDT581 slot-value analysis classes,",
        "not forty-two confirmed manuscript words or linguistic stems.",
        "",
        "## Forty-two productive GDT581 slot-value classes",
        "",
        "| root | family | invariant concept | universal rival | slots |",
        "|---|---|---|---|---:|",
    ]
    for row in core_rows:
        lines.append(
            f"| {row['root']} | {row['function_family']} | "
            f"{row['invariant_core_concept']} | {row['universal_workshop_rival_de']} | "
            f"{row['slot_count']} |"
        )
    lines.extend(
        [
            "",
            "## Eighty learned name defaults",
            "",
            "| class | raw core | replaceable default | occurrences |",
            "|---|---|---|---:|",
        ]
    )
    for row in name_rows:
        lines.append(
            f"| {row['content_class']} | {row['raw_name_core']} | "
            f"{row['provisional_default_de']} | {row['occurrence_count']} |"
        )
    lines.extend(
        [
            "",
            "## Two owner-bound learned running defaults",
            "",
            "| slot | owner-bound concept | replaceable default |",
            "|---|---|---|",
        ]
    )
    for slot_id, (concept, default_de) in sorted(LOCAL_X_DEFAULTS.items()):
        lines.append(f"| {slot_id} | {concept} | {default_de} |")
    lines.extend(
        [
            "",
            "## Structural control defaults",
            "",
            "| control | concept | structural default |",
            "|---|---|---|",
        ]
    )
    for root, (concept, default_de) in sorted(CONTROL_DEFAULTS.items()):
        lines.append(f"| {root} | {concept} | {default_de} |")
    for page in pages:
        physical_page = page["physical_page"]
        lines.extend(["", f"## {physical_page}", ""])
        for event in events_by_page[physical_page]:
            lines.extend(
                [
                    f"### {event['event_id']} — `{event['surface']}` / `{event['final_context_recipe']}`",
                    "",
                    str(event["concrete_working_clause_de"]),
                    "",
                    str(event["concrete_slot_trace_de"]),
                    "",
                ]
            )
        if cards_by_page[physical_page]:
            lines.extend(["### Local cards", ""])
            for card in cards_by_page[physical_page]:
                lines.append(
                    f"- **{card['source_event_id']}** `{card['surface']}`: "
                    f"{card['concrete_working_clause_de']}"
                )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    complete_slots = data["complete_slots"]
    aliases = data["aliases"]
    events = data["events"]
    statements = data["statements"]
    pages = data["pages"]
    local_cards = data["local_cards"]
    name_slots = data["name_slots"]

    if (
        len(complete_slots), len(aliases), len(events), len(statements),
        len(pages), len(local_cards), len(name_slots)
    ) != (15889, 4026, 5122, 793, 30, 744, 107):
        raise RuntimeError("GDT581 input count drift")
    if any(str(row.get("physical_page", "")).lower().startswith("f84") for rows in data.values() for row in rows):
        raise RuntimeError("Forbidden f84/f84r material reached GDT582")

    name_defaults, name_by_slot = build_name_defaults(name_slots)
    core_rows, realization_rows = function_dictionary_rows(complete_slots)
    complete_defaults = [enrich_slot(row, name_by_slot) for row in complete_slots]
    if any(not str(row["gdt582_concrete_default_de"]).strip() for row in complete_defaults):
        raise RuntimeError("Empty GDT582 default")
    content_defaults = [row for row in complete_defaults if row["fill_status"] == "CONTENT_CARRIER"]
    control_defaults = [row for row in complete_defaults if row["fill_status"] == "CONTROL_HOST_ONLY"]
    productive_count = sum(
        row["gdt582_default_kind"] == "PRODUCTIVE_REGISTER_FUNCTION"
        for row in content_defaults
    )
    learned_count = len(content_defaults) - productive_count
    if (len(content_defaults), len(control_defaults), productive_count, learned_count) != (
        13702, 2187, 13593, 109
    ):
        raise RuntimeError("Complete-default partition drift")

    alias_defaults = build_alias_defaults(aliases)
    slots_by_running_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    slots_by_local_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in complete_defaults:
        if row["layer"] == "RUNNING_ATOM":
            slots_by_running_event[str(row["source_event_or_card_id"])].append(row)
        else:
            slots_by_local_card[str(row["source_event_or_card_id"])].append(row)

    event_rows: list[dict[str, object]] = []
    for event in events:
        members = slots_by_running_event[event["event_id"]]
        if not members:
            raise RuntimeError(f"Running event without complete slots: {event['event_id']}")
        event_rows.append(
            {
                **event,
                "complete_slot_count": len(members),
                "content_slot_count": sum(row["fill_status"] == "CONTENT_CARRIER" for row in members),
                "control_slot_count": sum(row["fill_status"] == "CONTROL_HOST_ONLY" for row in members),
                "concrete_slot_trace_de": render_trace(members),
                "concrete_working_clause_de": render_card(members, event["register"]),
                "gdt581_exact_roundtrip_de": event["content_ready_boundary_clause_de"],
                "gdt582_guard": "ALL_WRITTEN_RUNNING_SLOTS_RENDERED__GDT581_CLAUSE_RETAINED_EXACT",
            }
        )
    event_by_id = {row["event_id"]: row for row in event_rows}

    statement_rows: list[dict[str, object]] = []
    for statement in statements:
        event_ids = statement["event_ids"].split("|")
        concrete = " ".join(str(event_by_id[event_id]["concrete_working_clause_de"]) for event_id in event_ids)
        statement_rows.append(
            {
                **statement,
                "concrete_working_reading_de": concrete,
                "complete_slot_count": sum(int(event_by_id[event_id]["complete_slot_count"]) for event_id in event_ids),
                "content_slot_count": sum(int(event_by_id[event_id]["content_slot_count"]) for event_id in event_ids),
                "control_slot_count": sum(int(event_by_id[event_id]["control_slot_count"]) for event_id in event_ids),
                "gdt581_exact_roundtrip_de": statement["grammar_content_boundary_reading_de"],
                "gdt582_guard": "STATEMENT_REBUILT_FROM_FIXED_EVENT_IDS__GDT581_READING_RETAINED_EXACT",
            }
        )

    statement_by_id = {str(row["statement_id"]): row for row in statement_rows}
    if set(PASSAGE_STATEMENTS) - set(statement_by_id):
        missing = sorted(set(PASSAGE_STATEMENTS) - set(statement_by_id))
        raise RuntimeError(f"Missing complete passage checks: {missing}")
    passage_registers = Counter(
        str(statement_by_id[statement_id]["register"])
        for statement_id in PASSAGE_STATEMENTS
    )
    if passage_registers != {
        "SOURCE_SECTION_T": 4, "HERBAL": 4, "CELESTIAL": 4,
        "BIOLOGICAL": 4, "PHARMA": 4,
    }:
        raise RuntimeError("Twenty-statement passage deck drift")
    passage_rows: list[dict[str, object]] = []
    for ordinal, statement_id in enumerate(PASSAGE_STATEMENTS, 1):
        statement = statement_by_id[statement_id]
        register = str(statement["register"])
        passage_rows.append(
            {
                "passage_check_ordinal": ordinal,
                "statement_id": statement_id,
                "physical_page": statement["physical_page"],
                "register": register,
                "owner_id": statement["owner_id"],
                "event_count": statement["event_count"],
                "surface_sequence": statement["surface_sequence"],
                "gdt581_structural_reading_de": statement["grammar_content_boundary_reading_de"],
                "gdt582_concrete_reading_de": statement["concrete_working_reading_de"],
                "manual_house_sense_disposition": "KEEP_REGISTER_HYBRID",
                "manual_note": sense_note(register),
                "guard": "FOUR_COMPLETE_STATEMENTS_PER_REGISTER__FIXED_EVENT_IDS_AND_SLOT_HOSTS",
            }
        )

    local_rows: list[dict[str, object]] = []
    for card in local_cards:
        members = slots_by_local_card[card["source_event_id"]]
        if not members:
            raise RuntimeError(f"Local card without complete slots: {card['source_event_id']}")
        local_rows.append(
            {
                **card,
                "complete_slot_count": len(members),
                "content_slot_count": sum(row["fill_status"] == "CONTENT_CARRIER" for row in members),
                "control_slot_count": sum(row["fill_status"] == "CONTROL_HOST_ONLY" for row in members),
                "concrete_slot_trace_de": render_trace(members),
                "concrete_working_clause_de": render_card(members, card["register"]),
                "gdt582_guard": "LOCAL_CARD_OWNER_AND_LOCUS_FIXED__ALL_COMPONENT_AND_NAME_SLOTS_RENDERED",
            }
        )

    page_rows: list[dict[str, object]] = []
    aliases_by_page = Counter(row["physical_page"] for row in alias_defaults)
    for page in pages:
        physical_page = page["physical_page"]
        members = [row for row in complete_defaults if row["physical_page"] == physical_page]
        page_rows.append(
            {
                **page,
                "complete_default_slot_count": len(members),
                "content_default_slot_count": sum(row["fill_status"] == "CONTENT_CARRIER" for row in members),
                "control_default_slot_count": sum(row["fill_status"] == "CONTROL_HOST_ONLY" for row in members),
                "productive_function_slot_count": sum(row["gdt582_default_kind"] == "PRODUCTIVE_REGISTER_FUNCTION" for row in members),
                "learned_content_slot_count": sum(row["gdt582_default_kind"] in {"CLASS_CONDITIONED_LEARNED_NAME", "OWNER_BOUND_LOCAL_X"} for row in members),
                "alias_default_count": aliases_by_page[physical_page],
                "gdt582_page_status": "COMPLETE_CONCRETE_DEFAULT_PAGE",
                "gdt582_guard": "PAGE_MEMBERSHIP_UNCHANGED__NO_EMPTY_WRITTEN_DEFAULT",
            }
        )

    scorecard = build_candidate_scorecard(complete_defaults, events)
    sense_event_ids = select_sense_events(events, slots_by_running_event)
    sense_rows: list[dict[str, object]] = []
    for ordinal, event_id in enumerate(sense_event_ids, 1):
        event = event_by_id[event_id]
        register = str(event["register"])
        sense_rows.append(
            {
                "sense_check_ordinal": ordinal,
                "event_id": event_id,
                "physical_page": event["physical_page"],
                "register": register,
                "surface": event["surface"],
                "recipe": event["final_context_recipe"],
                "gdt581_structural_clause_de": event["content_ready_boundary_clause_de"],
                "gdt582_concrete_clause_de": event["concrete_working_clause_de"],
                "manual_house_sense_disposition": "KEEP_REGISTER_HYBRID",
                "manual_note": sense_note(register),
                "guard": "FIVE_EVENTS_PER_REGISTER__ALL_SLOTS_VISIBLE_IN_EXACT_TRACE",
            }
        )

    book = build_book(pages, event_rows, local_rows, core_rows, name_defaults)
    result = {
        "experiment_id": "GDT582",
        "status": STATUS,
        "complete_defaults": len(complete_defaults),
        "content_defaults": len(content_defaults),
        "control_defaults": len(control_defaults),
        "productive_function_slots": productive_count,
        "learned_content_slots": learned_count,
        "core_stems": len(core_rows),
        "register_realization_cells": len(realization_rows),
        "learned_name_types": len(name_defaults),
        "alias_defaults": len(alias_defaults),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "local_cards": len(local_rows),
        "pages": len(page_rows),
        "sense_checks": len(sense_rows),
        "complete_passage_checks": len(passage_rows),
        "candidate_packs": len(scorecard),
        "selected_pack": "REGISTER_HYBRID_CODEBOOK",
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt582_42_core_stem_defaults.tsv", core_rows)
    write_tsv(OUT / "gdt582_181_register_realization_cells.tsv", realization_rows)
    write_tsv(OUT / "gdt582_80_learned_name_defaults.tsv", name_defaults)
    write_tsv(OUT / "gdt582_13702_content_slot_defaults.tsv", content_defaults)
    write_tsv(OUT / "gdt582_2187_control_slot_defaults.tsv", control_defaults)
    write_tsv(OUT / "gdt582_15889_complete_default_ledger.tsv", complete_defaults)
    write_tsv(OUT / "gdt582_4026_alias_default_resolutions.tsv", alias_defaults)
    write_tsv(OUT / "gdt582_5122_concrete_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt582_793_concrete_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt582_744_concrete_local_card_edition.tsv", local_rows)
    write_tsv(OUT / "gdt582_30_page_concrete_profiles.tsv", page_rows)
    write_tsv(OUT / "gdt582_25_event_sense_checks.tsv", sense_rows)
    write_tsv(OUT / "gdt582_20_complete_passage_sense_checks.tsv", passage_rows)
    write_tsv(OUT / "gdt582_4_candidate_pack_scorecard.tsv", scorecard)
    (OUT / "GDT582_CONCRETE_DEFAULT_THIRTY_PAGE_EDITION.md").write_text(book, encoding="utf-8")
    (OUT / "gdt582_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
