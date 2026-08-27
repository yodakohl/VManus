#!/usr/bin/env python3
"""Compile a horizontal semantic-template atlas for the 78 admitted statements."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt554_statement_semantic_template_audit"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G553 = ROOT / "experiments/yolo/gdt553_zero_rest_145_reader/artifacts"

EVENTS_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
STATEMENTS_IN = G539 / "gdt539_78_contextual_statements.tsv"
READER_IN = G553 / "gdt553_145_zero_rest_reader.tsv"

EVENT_OUT = OUT / "gdt554_546_event_semantic_templates.tsv"
STATEMENT_OUT = OUT / "gdt554_78_statement_template_atlas.tsv"
TARGET_SURFACE_OUT = OUT / "gdt554_145_target_surface_reinsertion.tsv"
SLOT_OUT = OUT / "gdt554_slot_transition_templates.tsv"
EVENT_TEMPLATE_OUT = OUT / "gdt554_recurrent_event_templates.tsv"
FRAME_OUT = OUT / "gdt554_recurrent_statement_frames.tsv"
WHOLE_TEMPLATE_OUT = OUT / "gdt554_recurrent_whole_statement_templates.tsv"
CONSISTENCY_OUT = OUT / "gdt554_repeated_context_consistency.tsv"
NOMINAL_OUT = OUT / "gdt554_16_nominal_fragments.tsv"
SUMMARY_OUT = OUT / "gdt554_template_summary.tsv"
BOOK_OUT = OUT / "GDT554_STATEMENT_TEMPLATE_BOOK.md"
RESULT_OUT = OUT / "gdt554_result.json"

STATUS = "PASS_78_STATEMENT_TEMPLATE_ATLAS__ZERO_EXACT_CONTEXT_CONTRADICTIONS"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
RELATION_ROOTS = {"AL", "AR", "L", "AIR"}

CONTROL_LABEL = {
    "AL": "REL:AL", "AR": "REL:AR", "L": "REL:L", "AIR": "REL:AIR",
    "E": "GRADE:I", "EE": "GRADE:II", "EEE": "GRADE:III", "O": "EXEC",
    "D_ADDR": "ADDR:D", "AM_ADDR": "ADDR:AM", "A_ADDR": "ADDR:A",
    "S_ADDR": "ADDR:S", "LOCAL_CHAR_F": "LOCAL:F",
    "LOCAL_CHAR_I": "LOCAL:I", "LOCAL_X": "LOCAL:X", "M_LOCAL": "LOCAL:M",
    "HO": "CLASS", "IIN": "STAGE", "DA": "STAGE:II", "OL": "CONTINUE",
    "OT": "THEN", "DY": "CLOSE", "CARRIER_Q": "BEGIN",
}

ABSTRACT_LABEL = {
    **{root: "A" for root in ACTION_ROOTS},
    **{root: "X" for root in ARGUMENT_ROOTS},
    **{root: "REL" for root in RELATION_ROOTS},
    "E": "G1", "EE": "G2", "EEE": "G3", "O": "EXEC",
    "D_ADDR": "ADDR", "AM_ADDR": "ADDR", "A_ADDR": "ADDR",
    "S_ADDR": "ADDR", "LOCAL_CHAR_F": "LOCAL", "LOCAL_CHAR_I": "LOCAL",
    "LOCAL_X": "LOCAL", "M_LOCAL": "LOCAL", "HO": "CLASS", "IIN": "STAGE",
    "DA": "STAGE2", "OL": "CONT", "OT": "THEN", "DY": "CLOSE",
    "CARRIER_Q": "BEGIN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def split_roots(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def state_source(explicit: list[str], inherited: str, role: str) -> str:
    if explicit:
        return f"SET_{role}{len(explicit)}"
    if inherited != "NONE":
        return f"KEEP_{role}1"
    return f"EMPTY_{role}"


def slot_template(
    explicit_actions: list[str], inherited_action: str,
    explicit_arguments: list[str], inherited_argument: str,
) -> str:
    return "__".join([
        state_source(explicit_actions, inherited_action, "A"),
        state_source(explicit_arguments, inherited_argument, "X"),
    ])


def semantic_macro(
    atoms: list[str], explicit_actions: list[str], inherited_action: str,
    explicit_arguments: list[str], inherited_argument: str,
) -> str:
    if explicit_actions:
        action = "+".join(explicit_actions)
    elif inherited_action != "NONE":
        action = "^" + inherited_action
    else:
        action = "-"
    if explicit_arguments:
        argument = "+".join(explicit_arguments)
    elif inherited_argument != "NONE":
        argument = "^" + inherited_argument
    else:
        argument = "-"
    controls = [CONTROL_LABEL[atom] for atom in atoms if atom in CONTROL_LABEL]
    return f"A:{action};X:{argument};C:{'>'.join(controls) or '-'}"


def abstract_template(
    atoms: list[str], explicit_actions: list[str], inherited_action: str,
    explicit_arguments: list[str], inherited_argument: str,
) -> str:
    state = slot_template(
        explicit_actions, inherited_action, explicit_arguments, inherited_argument
    )
    chain = ">".join(ABSTRACT_LABEL[atom] for atom in atoms)
    return f"{state}|{chain}"


def nominal_kind(atoms: list[str], resolved_arguments: list[str]) -> str:
    if resolved_arguments:
        return "ARGUMENT_OR_VALUE_FRAGMENT"
    if any(atom in RELATION_ROOTS for atom in atoms):
        return "RELATION_OR_ADDRESS_FRAGMENT"
    if "DY" in atoms:
        return "CLOSURE_FRAGMENT"
    if "OL" in atoms:
        return "CONTINUATION_FRAGMENT"
    if "OT" in atoms:
        return "ORDER_FRAGMENT"
    return "GRADE_ADDRESS_OR_LOCAL_CONTROL_FRAGMENT"


def transfer_scope(pages: set[str], registers: set[str]) -> str:
    if len(registers) > 1:
        return "CROSS_REGISTER"
    if len(pages) > 1:
        return "CROSS_PAGE"
    return "SAME_PAGE_RECURRENT"


def clipped(values: list[str], limit: int = 12) -> str:
    if len(values) <= limit:
        return " || ".join(values)
    return " || ".join(values[:limit]) + f" || ...(+{len(values) - limit})"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(EVENTS_IN)
    source_statements = read_tsv(STATEMENTS_IN)
    reader_rows = read_tsv(READER_IN)
    if (len(source_events), len(source_statements), len(reader_rows)) != (546, 78, 145):
        raise RuntimeError("Input count drift")
    reader = {row["surface"]: row for row in reader_rows}

    source_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        source_by_statement[event["statement_id"]].append(event)
    for rows in source_by_statement.values():
        rows.sort(key=lambda row: int(row["card_ordinal_in_statement"]))

    event_rows: list[dict[str, object]] = []
    event_internal: dict[str, dict[str, object]] = {}
    nominal_rows: list[dict[str, object]] = []
    target_recipe_matches = 0
    target_context_matches = 0
    repaired_target_events = 0

    for source in source_events:
        atoms = source["final_context_recipe"].split("+")
        unknown = [atom for atom in atoms if atom not in ABSTRACT_LABEL]
        if unknown:
            raise RuntimeError(f"Unmapped atoms in {source['event_id']}: {unknown}")
        explicit_actions = split_roots(source["explicit_action_roots"])
        explicit_arguments = split_roots(source["explicit_argument_roots"])
        inherited_action = source["inherited_action_root"]
        inherited_argument = source["inherited_argument_root"]
        resolved_actions = explicit_actions or (
            [inherited_action] if inherited_action != "NONE" else []
        )
        resolved_arguments = explicit_arguments or (
            [inherited_argument] if inherited_argument != "NONE" else []
        )
        macro = semantic_macro(
            atoms, explicit_actions, inherited_action,
            explicit_arguments, inherited_argument,
        )
        abstract = abstract_template(
            atoms, explicit_actions, inherited_action,
            explicit_arguments, inherited_argument,
        )
        slot = slot_template(
            explicit_actions, inherited_action,
            explicit_arguments, inherited_argument,
        )
        target = reader.get(source["surface"])
        target_member = target is not None
        recipe_match = target_member and target["final_recipe"] == source["final_context_recipe"]
        context_variants = (
            target["known_contextual_readings_de"].split(" || ") if target else []
        )
        context_match = target_member and source["contextual_clause_de"] in context_variants
        if target_member:
            if not recipe_match:
                raise RuntimeError(f"GDT553 recipe mismatch: {source['event_id']}")
            if not context_match:
                raise RuntimeError(f"GDT553 context mismatch: {source['event_id']}")
            target_recipe_matches += 1
            target_context_matches += 1
            repaired_target_events += target["resolution_generation"] != "BASE_GDT548"

        control_chain = [CONTROL_LABEL[atom] for atom in atoms if atom in CONTROL_LABEL]
        event_row: dict[str, object] = {
            "event_ordinal": source["context_event_ordinal"],
            "event_id": source["event_id"],
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "surface": source["surface"],
            "final_recipe": source["final_context_recipe"],
            "gdt553_target_member": "YES" if target_member else "NO",
            "gdt553_resolution_generation": target["resolution_generation"] if target else "OUTSIDE_GDT553",
            "gdt553_former_queue_card": target["former_queue_candidate"] if target else "OUTSIDE_GDT553",
            "gdt553_recipe_match": "YES" if recipe_match else "NOT_APPLICABLE",
            "gdt553_context_reading_match": "YES" if context_match else "NOT_APPLICABLE",
            "slot_transition_template": slot,
            "explicit_action_roots": source["explicit_action_roots"],
            "inherited_action_root": inherited_action,
            "resolved_action_roots": "|".join(resolved_actions) or "NONE",
            "explicit_argument_roots": source["explicit_argument_roots"],
            "inherited_argument_root": inherited_argument,
            "resolved_argument_roots": "|".join(resolved_arguments) or "NONE",
            "ordered_control_chain": ">".join(control_chain) or "NONE",
            "portable_semantic_macro": macro,
            "abstract_event_template": abstract,
            "contextual_clause_de": source["contextual_clause_de"],
            "portable_consistency_key": (
                f"{source['final_context_recipe']}|IA:{inherited_action}|IX:{inherited_argument}"
            ),
            "guard": "HORIZONTAL_WORKING_TEMPLATE__NO_PLAINTEXT_OR_NEW_MEANING",
        }
        event_rows.append(event_row)
        event_internal[source["event_id"]] = {
            "macro": macro, "abstract": abstract, "slot": slot,
            "resolved_actions": resolved_actions, "resolved_arguments": resolved_arguments,
            "atoms": atoms,
        }
        if not resolved_actions:
            nominal_rows.append({
                "nominal_ordinal": len(nominal_rows) + 1,
                "event_id": source["event_id"],
                "statement_id": source["statement_id"],
                "card_ordinal_in_statement": source["card_ordinal_in_statement"],
                "statement_initial": "YES" if source["card_ordinal_in_statement"] == "1" else "NO",
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_recipe": source["final_context_recipe"],
                "resolved_argument_roots": "|".join(resolved_arguments) or "NONE",
                "nominal_fragment_kind": nominal_kind(atoms, resolved_arguments),
                "ordered_control_chain": ">".join(control_chain) or "NONE",
                "current_default_reading_de": source["contextual_clause_de"],
                "decision": "KEEP_NOMINAL_OR_CONTROL_READING__DO_NOT_INVENT_VERB",
            })

    if target_recipe_matches != 149 or target_context_matches != 149:
        raise RuntimeError("Expected all 149 GDT553 events to match")
    if len(nominal_rows) != 16:
        raise RuntimeError("Expected the 16 known no-action fragments")

    statement_rows: list[dict[str, object]] = []
    statement_sequences: dict[str, dict[str, list[str]]] = {}
    for source in source_statements:
        events = source_by_statement[source["statement_id"]]
        if len(events) != int(source["event_count"]):
            raise RuntimeError(f"Statement partition mismatch: {source['statement_id']}")
        internals = [event_internal[event["event_id"]] for event in events]
        macros = [str(item["macro"]) for item in internals]
        abstracts = [str(item["abstract"]) for item in internals]
        slots = [str(item["slot"]) for item in internals]
        statement_sequences[source["statement_id"]] = {
            "macros": macros, "abstracts": abstracts, "slots": slots,
        }
        action_roots = sorted({
            root for item in internals for root in item["resolved_actions"]  # type: ignore[union-attr]
        })
        argument_roots = sorted({
            root for item in internals for root in item["resolved_arguments"]  # type: ignore[union-attr]
        })
        repaired_count = sum(
            reader[event["surface"]]["resolution_generation"] != "BASE_GDT548"
            for event in events if event["surface"] in reader
        )
        statement_rows.append({
            "statement_ordinal": source["statement_ordinal"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "locus_start": source["locus_start"],
            "locus_end": source["locus_end"],
            "event_count": source["event_count"],
            "gdt553_target_event_count": source["target_event_count"],
            "gdt553_repaired_event_count": repaired_count,
            "resolved_action_inventory": "|".join(action_roots) or "NONE",
            "resolved_argument_inventory": "|".join(argument_roots) or "NONE",
            "slot_transition_sequence": " || ".join(slots),
            "portable_semantic_macro_sequence": " || ".join(macros),
            "abstract_event_template_sequence": " || ".join(abstracts),
            "exact_abstract_statement_peer_count": 0,
            "contextual_working_reading_de": source["contextual_working_reading_de"],
            "end_mode": source["end_mode"],
            "guard": "COMPLETE_EXISTING_STATEMENT__NO_NEW_PAGE_OR_MEANING",
        })
    abstract_statement_counts = Counter(
        row["abstract_event_template_sequence"] for row in statement_rows
    )
    for row in statement_rows:
        row["exact_abstract_statement_peer_count"] = (
            abstract_statement_counts[row["abstract_event_template_sequence"]] - 1
        )

    target_surface_rows: list[dict[str, object]] = []
    target_events_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        if row["gdt553_target_member"] == "YES":
            target_events_by_surface[str(row["surface"])].append(row)
    for source in reader_rows:
        rows = target_events_by_surface[source["surface"]]
        if not rows:
            raise RuntimeError(f"Target surface absent from statements: {source['surface']}")
        incoming_states = sorted({
            f"IA:{row['inherited_action_root']}|IX:{row['inherited_argument_root']}"
            for row in rows
        })
        target_surface_rows.append({
            "target_ordinal": source["target_ordinal"],
            "surface": source["surface"],
            "final_recipe": source["final_recipe"],
            "event_count": len(rows),
            "statement_count": len({str(row["statement_id"]) for row in rows}),
            "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in rows})),
            "registers": "|".join(sorted({str(row["register"]) for row in rows})),
            "incoming_state_count": len(incoming_states),
            "incoming_states": " || ".join(incoming_states),
            "portable_macro_count": len({str(row["portable_semantic_macro"]) for row in rows}),
            "portable_macros": clipped(sorted({str(row["portable_semantic_macro"]) for row in rows})),
            "contextual_clause_count": len({str(row["contextual_clause_de"]) for row in rows}),
            "observed_contextual_clauses_de": clipped(sorted({str(row["contextual_clause_de"]) for row in rows})),
            "gdt553_observed_requirement_modes": source["observed_requirement_modes"],
            "resolution_generation": source["resolution_generation"],
            "former_queue_candidate": source["former_queue_candidate"],
            "recipe_match_all_events": "YES",
            "context_reading_match_all_events": "YES",
            "status": "REINSERTED_EXACTLY__KNOWN_CONTEXT_ONLY",
        })

    whole_template_rows: list[dict[str, object]] = []
    whole_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        whole_groups[str(row["abstract_event_template_sequence"])].append(row)
    recurring_whole_groups = [
        (signature, rows) for signature, rows in whole_groups.items() if len(rows) >= 2
    ]
    recurring_whole_groups.sort(key=lambda item: (-len(item[1]), -int(item[1][0]["event_count"]), item[0]))
    for signature, rows in recurring_whole_groups:
        pages = {str(row["physical_page"]) for row in rows}
        registers = {str(row["register"]) for row in rows}
        whole_template_rows.append({
            "whole_template_ordinal": len(whole_template_rows) + 1,
            "event_length": rows[0]["event_count"],
            "abstract_statement_template": signature,
            "statement_count": len(rows),
            "physical_page_count": len(pages),
            "register_count": len(registers),
            "portable_macro_variant_count": len({str(row["portable_semantic_macro_sequence"]) for row in rows}),
            "statement_ids": "|".join(str(row["statement_id"]) for row in rows),
            "portable_macro_variants": clipped(sorted({str(row["portable_semantic_macro_sequence"]) for row in rows})),
            "example_readings_de": clipped([str(row["contextual_working_reading_de"]) for row in rows], limit=4),
            "transfer_scope": transfer_scope(pages, registers),
            "guard": "WHOLE_ABSTRACT_STATEMENT_TEMPLATE__ROOT_SUBSTITUTION_ALLOWED",
        })

    slot_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    event_template_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        slot_groups[str(row["slot_transition_template"])].append(row)
        event_template_groups[str(row["abstract_event_template"])].append(row)

    slot_rows: list[dict[str, object]] = []
    for slot, rows in sorted(slot_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        pages = {str(row["physical_page"]) for row in rows}
        registers = {str(row["register"]) for row in rows}
        statements = {str(row["statement_id"]) for row in rows}
        slot_rows.append({
            "slot_template_ordinal": len(slot_rows) + 1,
            "slot_transition_template": slot,
            "event_count": len(rows),
            "statement_count": len(statements),
            "physical_page_count": len(pages),
            "register_count": len(registers),
            "target_event_count": sum(row["gdt553_target_member"] == "YES" for row in rows),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "example_event_id": rows[0]["event_id"],
            "example_clause_de": rows[0]["contextual_clause_de"],
            "transfer_scope": transfer_scope(pages, registers),
        })

    recurrent_event_rows: list[dict[str, object]] = []
    qualifying_event_groups = [
        (template, rows) for template, rows in event_template_groups.items()
        if len({str(row["statement_id"]) for row in rows}) >= 2
    ]
    qualifying_event_groups.sort(key=lambda item: (-len(item[1]), item[0]))
    for template, rows in qualifying_event_groups:
        pages = {str(row["physical_page"]) for row in rows}
        registers = {str(row["register"]) for row in rows}
        statements = {str(row["statement_id"]) for row in rows}
        macros = sorted({str(row["portable_semantic_macro"]) for row in rows})
        recurrent_event_rows.append({
            "template_ordinal": len(recurrent_event_rows) + 1,
            "abstract_event_template": template,
            "event_count": len(rows),
            "statement_count": len(statements),
            "physical_page_count": len(pages),
            "register_count": len(registers),
            "surface_count": len({str(row["surface"]) for row in rows}),
            "portable_macro_variant_count": len(macros),
            "target_event_count": sum(row["gdt553_target_member"] == "YES" for row in rows),
            "portable_macro_variants": clipped(macros),
            "example_event_ids": "|".join(str(row["event_id"]) for row in rows[:8]),
            "transfer_scope": transfer_scope(pages, registers),
        })

    frame_occurrences: dict[tuple[str, int, str], list[dict[str, object]]] = defaultdict(list)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    for statement_id, sequences in statement_sequences.items():
        source = source_statement_by_id[statement_id]
        events = source_by_statement[statement_id]
        for layer, sequence in (
            ("EXACT_PORTABLE", sequences["macros"]),
            ("ABSTRACT_ROLE", sequences["abstracts"]),
        ):
            for length in range(2, 5):
                for start in range(0, len(sequence) - length + 1):
                    signature = " || ".join(sequence[start:start + length])
                    frame_occurrences[(layer, length, signature)].append({
                        "statement_id": statement_id,
                        "physical_page": source["physical_page"],
                        "register": source["register"],
                        "event_ids": "|".join(
                            event["event_id"] for event in events[start:start + length]
                        ),
                    })

    selected_frames: list[tuple[tuple[str, int, str], list[dict[str, object]]]] = []
    for key, occurrences in frame_occurrences.items():
        layer, _length, _signature = key
        statement_count = len({str(item["statement_id"]) for item in occurrences})
        if layer == "EXACT_PORTABLE" and statement_count >= 2:
            selected_frames.append((key, occurrences))
        elif layer == "ABSTRACT_ROLE" and statement_count >= 3:
            selected_frames.append((key, occurrences))
    selected_frames.sort(
        key=lambda item: (
            0 if item[0][0] == "EXACT_PORTABLE" else 1,
            -item[0][1],
            -len({str(row["statement_id"]) for row in item[1]}), item[0][2],
        )
    )
    frame_rows: list[dict[str, object]] = []
    for (layer, length, signature), occurrences in selected_frames:
        pages = {str(item["physical_page"]) for item in occurrences}
        registers = {str(item["register"]) for item in occurrences}
        statements = {str(item["statement_id"]) for item in occurrences}
        frame_rows.append({
            "frame_ordinal": len(frame_rows) + 1,
            "frame_layer": layer,
            "frame_length": length,
            "frame_signature": signature,
            "occurrence_count": len(occurrences),
            "statement_count": len(statements),
            "physical_page_count": len(pages),
            "register_count": len(registers),
            "transfer_scope": transfer_scope(pages, registers),
            "statement_ids": "|".join(sorted(statements)),
            "example_event_paths": clipped(
                [str(item["event_ids"]) for item in occurrences], limit=8
            ),
            "guard": "CONTIGUOUS_WITHIN_STATEMENT_FRAME__NO_CROSS_BOUNDARY_JOIN",
        })

    consistency_rows: list[dict[str, object]] = []
    contradiction_count = 0
    family_specs = (
        (
            "SURFACE_PLUS_INCOMING_STATE",
            lambda row: (
                f"{row['surface']}|IA:{row['inherited_action_root']}|"
                f"IX:{row['inherited_argument_root']}"
            ),
        ),
        (
            "RECIPE_PLUS_INCOMING_STATE",
            lambda row: str(row["portable_consistency_key"]),
        ),
    )
    for family_type, key_function in family_specs:
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in event_rows:
            groups[key_function(row)].append(row)
        for key, rows in groups.items():
            if len(rows) < 2:
                continue
            macro_count = len({str(row["portable_semantic_macro"]) for row in rows})
            recipe_count = len({str(row["final_recipe"]) for row in rows})
            conflict = macro_count != 1 or (
                family_type == "SURFACE_PLUS_INCOMING_STATE" and recipe_count != 1
            )
            contradiction_count += conflict
            consistency_rows.append({
                "consistency_ordinal": len(consistency_rows) + 1,
                "family_type": family_type,
                "exact_context_key": key,
                "event_count": len(rows),
                "statement_count": len({str(row["statement_id"]) for row in rows}),
                "physical_page_count": len({str(row["physical_page"]) for row in rows}),
                "register_count": len({str(row["register"]) for row in rows}),
                "surface_count": len({str(row["surface"]) for row in rows}),
                "recipe_variant_count": recipe_count,
                "portable_macro_variant_count": macro_count,
                "german_clause_variant_count": len({str(row["contextual_clause_de"]) for row in rows}),
                "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
                "event_ids": "|".join(str(row["event_id"]) for row in rows),
                "portable_macro": clipped(sorted({str(row["portable_semantic_macro"]) for row in rows})),
                "status": "CONTRADICTION" if conflict else "CONSISTENT_PORTABLE_READING",
                "guard": "REGISTER_WORDING_MAY_DIFFER__PORTABLE_MACRO_MAY_NOT",
            })
    consistency_rows.sort(
        key=lambda row: (
            row["status"] != "CONTRADICTION", row["family_type"],
            -int(row["event_count"]), row["exact_context_key"],
        )
    )
    for ordinal, row in enumerate(consistency_rows, 1):
        row["consistency_ordinal"] = ordinal

    result = {
        "status": STATUS,
        "physical_page_count": len({row["physical_page"] for row in source_events}),
        "register_count": len({row["register"] for row in source_events}),
        "statement_count": len(statement_rows),
        "prose_event_count": len(event_rows),
        "gdt553_target_surface_count": len(reader),
        "gdt553_target_event_count": sum(row["gdt553_target_member"] == "YES" for row in event_rows),
        "gdt553_recipe_match_count": target_recipe_matches,
        "gdt553_context_reading_match_count": target_context_matches,
        "gdt553_repaired_target_event_count": repaired_target_events,
        "gdt553_multi_incoming_state_surface_count": sum(
            int(row["incoming_state_count"]) > 1 for row in target_surface_rows
        ),
        "slot_transition_template_count": len(slot_rows),
        "cross_register_slot_transition_template_count": sum(
            int(row["register_count"]) > 1 for row in slot_rows
        ),
        "event_template_count": len(event_template_groups),
        "recurrent_event_template_count": len(recurrent_event_rows),
        "recurrent_event_template_event_count": sum(
            len(rows) for _template, rows in qualifying_event_groups
        ),
        "cross_register_recurrent_event_template_count": sum(
            int(row["register_count"]) > 1 for row in recurrent_event_rows
        ),
        "recurrent_frame_count": len(frame_rows),
        "exact_portable_recurrent_frame_count": sum(
            row["frame_layer"] == "EXACT_PORTABLE" for row in frame_rows
        ),
        "abstract_recurrent_frame_count": sum(
            row["frame_layer"] == "ABSTRACT_ROLE" for row in frame_rows
        ),
        "cross_page_recurrent_frame_count": sum(
            row["physical_page_count"] > 1 for row in frame_rows
        ),
        "cross_register_recurrent_frame_count": sum(
            row["register_count"] > 1 for row in frame_rows
        ),
        "cross_register_exact_portable_frame_count": sum(
            row["frame_layer"] == "EXACT_PORTABLE" and row["register_count"] > 1
            for row in frame_rows
        ),
        "longest_recurrent_frame_length": max(
            int(row["frame_length"]) for row in frame_rows
        ),
        "recurrent_three_plus_frame_count": sum(
            int(row["frame_length"]) >= 3 for row in frame_rows
        ),
        "repeated_context_family_count": len(consistency_rows),
        "exact_context_contradiction_count": contradiction_count,
        "nominal_fragment_count": len(nominal_rows),
        "statement_initial_nominal_fragment_count": sum(
            row["statement_initial"] == "YES" for row in nominal_rows
        ),
        "exact_abstract_statement_peer_count": sum(
            int(row["exact_abstract_statement_peer_count"]) for row in statement_rows
        ),
        "recurrent_whole_statement_template_count": len(whole_template_rows),
        "abstract_whole_statement_template_count": len(whole_groups),
        "statements_in_recurrent_whole_template_count": sum(
            int(row["statement_count"]) for row in whole_template_rows
        ),
        "cross_page_whole_statement_template_count": sum(
            int(row["physical_page_count"]) > 1 for row in whole_template_rows
        ),
        "longest_recurrent_whole_statement_event_count": max(
            int(row["event_length"]) for row in whole_template_rows
        ),
        "new_pages": 0,
        "new_recipes": 0,
        "root_meaning_changes": 0,
        "german_reading_changes": 0,
    }
    if contradiction_count:
        result["status"] = "AUDIT_FOUND_EXACT_CONTEXT_CONTRADICTIONS"

    write_tsv(EVENT_OUT, event_rows)
    write_tsv(STATEMENT_OUT, statement_rows)
    write_tsv(TARGET_SURFACE_OUT, target_surface_rows)
    write_tsv(SLOT_OUT, slot_rows)
    write_tsv(EVENT_TEMPLATE_OUT, recurrent_event_rows)
    write_tsv(FRAME_OUT, frame_rows)
    write_tsv(WHOLE_TEMPLATE_OUT, whole_template_rows)
    write_tsv(CONSISTENCY_OUT, consistency_rows)
    write_tsv(NOMINAL_OUT, nominal_rows)
    write_tsv(SUMMARY_OUT, [
        {"metric": key, "value": value, "guard": "GDT554_REPLAYED_METRIC"}
        for key, value in result.items()
    ])
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    strongest_frames = sorted(
        frame_rows,
        key=lambda row: (
            -int(row["register_count"]), -int(row["physical_page_count"]),
            -int(row["frame_length"]), -int(row["statement_count"]),
        ),
    )[:20]
    lines = [
        "# GDT554 — horizontales Arbeitsbuch der 78 Aussagen", "",
        "Die Makros sind eine kompakte Rückseite der unveränderten deutschen Arbeitslesung: `A` nennt sichtbare Aktionen, `^A` eine gleichsatzlich geerbte Aktion, `X` Argumente und `C` die geordnete Kontrollspur. Sie sind keine behauptete historische Syntax.",
        "", "## Steckplatzbewegungen", "",
        "| Bewegung | Events | Aussagen | Seiten | Beispiel |",
        "|---|---:|---:|---:|---|",
    ]
    for row in slot_rows:
        lines.append(
            f"| `{row['slot_transition_template']}` | {row['event_count']} | "
            f"{row['statement_count']} | {row['physical_page_count']} | "
            f"{row['example_clause_de']} |"
        )
    lines.extend(["", "## Wiederkehrende vollständige Aussagenschablonen", ""])
    for row in whole_template_rows:
        lines.append(
            f"- **{row['event_length']} Karten · {row['statement_count']} Aussagen · "
            f"{row['physical_page_count']} Seiten:** `{row['abstract_statement_template']}`"
        )
    lines.extend(["", "## Stärkste seitenübergreifende Mehrkartenrahmen", ""])
    for row in strongest_frames:
        lines.append(
            f"- **{row['frame_layer']} · {row['frame_length']} Karten · "
            f"{row['statement_count']} Aussagen / {row['physical_page_count']} Seiten:** "
            f"`{row['frame_signature']}`"
        )
    lines.extend(["", "## Die 16 absichtlich verbfreien Fragmente", ""])
    for row in nominal_rows:
        lines.append(
            f"- `{row['event_id']}` / `{row['surface']}` / "
            f"{row['nominal_fragment_kind']}: {row['current_default_reading_de']}"
        )
    lines.extend(["", "## Vollständige 78-Aussagen-Ausgabe", ""])
    for row in statement_rows:
        lines.extend([
            f"### {row['statement_id']} · {row['physical_page']} · {row['register']}", "",
            f"Makro: `{row['portable_semantic_macro_sequence']}`", "",
            str(row["contextual_working_reading_de"]), "",
        ])
    lines.extend([
        "## Reichweitengrenze", "",
        "Jede Folge bleibt innerhalb ihrer ursprünglichen Aussage. Registerwörter dürfen verschieden sein, solange dieselbe portable Wurzelspur erhalten bleibt. Null exakte Kontextwidersprüche gilt nur für die wiederholten Zustände dieser vier Seiten.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
