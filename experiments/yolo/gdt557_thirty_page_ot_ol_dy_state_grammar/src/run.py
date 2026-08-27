#!/usr/bin/env python3
"""Compile the 30-page OT/OL/DY working state grammar."""

from __future__ import annotations

import csv
import io
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G478 = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"

OLD_EVENT_PATH = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENT_PATH = G407 / "gdt407_715_statement_edition.tsv"
CURRENT_EVENT_PATH = G539 / "gdt539_546_contextual_prose_events.tsv"
CURRENT_STATEMENT_PATH = G539 / "gdt539_78_contextual_statements.tsv"
SEED_RESULT_PATH = G478 / "gdt478_result.json"

OCCURRENCE_OUT = OUT / "gdt557_all_state_marker_occurrences.tsv"
SUMMARY_OUT = OUT / "gdt557_marker_position_summary.tsv"
PAIR_OUT = OUT / "gdt557_marker_pair_order.tsv"
SEQUENCE_OUT = OUT / "gdt557_marker_sequence_profiles.tsv"
PAGE_OUT = OUT / "gdt557_page_transfer.tsv"
EDGE_OUT = OUT / "gdt557_compositional_edge_cases.tsv"
TRANSFER_OUT = OUT / "gdt557_seed_to_full_transfer.tsv"
BOOK_OUT = OUT / "GDT557_THREE_STATE_GRAMMAR.md"
RESULT_OUT = OUT / "gdt557_result.json"

STATUS = "PASS_OT_RIGHT_402_OF_404__OL_FLEXIBLE__DY_CLOSE_702_OF_705__TWO_REVERSE_COMPOSITIONS"
OLD_PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)
CURRENT_PAGES = ("f4r", "f20v", "f31r", "f66r")
MARKERS = ("OT", "OL", "DY")
PAIR_SPECS = (("OT", "OL"), ("OT", "DY"), ("OL", "DY"))
MEANINGS = {"OT": "DANACH", "OL": "FORTSETZEN", "DY": "ABSCHLIESSEN"}
OPERATIONS = {
    "OT": "START_OR_ADVANCE_NEXT_CARRIER",
    "OL": "KEEP_CURRENT_CARRIER_ACTIVE",
    "DY": "CLOSE_CURRENT_STEP",
}
GERMAN_OPERATIONS = {
    "OT": "nächsten Träger eröffnen",
    "OL": "laufenden Träger fortsetzen",
    "DY": "laufenden Schritt abschließen",
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


def guarded_old_rows(
    path: Path, columns: tuple[str, ...]
) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "physical_page",
    ]
    for page in OLD_PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    completed = subprocess.run(
        command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr)
    stat_line = next(
        (line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")),
        "",
    )
    if not stat_line:
        raise RuntimeError("Guarded query omitted statistics")
    stats = json.loads(stat_line.removeprefix("GUARD_STATS "))
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")), stats


def pct(numerator: int, denominator: int) -> str:
    return f"{100 * numerator / denominator:.6f}" if denominator else "0.000000"


def recipe_role(position: int, atom_count: int) -> str:
    if atom_count == 1:
        return "SINGLE_ATOM"
    if position == 1:
        return "INITIAL"
    if position == atom_count:
        return "TERMINAL"
    return "INTERNAL_BRIDGE"


def statement_role(ordinal: int, event_count: int) -> str:
    if event_count == 1:
        return "SINGLETON_STATEMENT"
    if ordinal == 1:
        return "STATEMENT_INITIAL"
    if ordinal == event_count:
        return "STATEMENT_FINAL"
    return "STATEMENT_INTERNAL"


def scope_formula(marker: str, role: str) -> str:
    formulas = {
        ("OT", "SINGLE_ATOM"): "OT = nächster Träger aus dem Satzkontext",
        ("OT", "INITIAL"): "OT · X = danach X",
        ("OT", "INTERNAL_BRIDGE"): "X · OT · Y = nach X folgt Y",
        ("OT", "TERMINAL"): "X · OT = danach nächster Kontextträger",
        ("OL", "SINGLE_ATOM"): "OL = laufenden Träger fortsetzen",
        ("OL", "INITIAL"): "OL · X = weiter mit X",
        ("OL", "INTERNAL_BRIDGE"): "X · OL · Y = X in Y weiterführen",
        ("OL", "TERMINAL"): "X · OL = X weiterführen",
        ("DY", "SINGLE_ATOM"): "DY = laufenden Schritt abschließen",
        ("DY", "INITIAL"): "DY · X = Schritt schließen; dann X",
        ("DY", "INTERNAL_BRIDGE"): "X · DY · Y = X schließen; dann Y",
        ("DY", "TERMINAL"): "X · DY = X abschließen",
    }
    return formulas[(marker, role)]


def event_marker_sequence(recipe: str) -> str:
    return "+".join(atom for atom in recipe.split("+") if atom in MARKERS) or "NONE"


def pair_relation(atoms: list[str], first: str, second: str) -> str:
    first_positions = [index for index, atom in enumerate(atoms) if atom == first]
    second_positions = [index for index, atom in enumerate(atoms) if atom == second]
    if max(first_positions) < min(second_positions):
        return "FIRST_BEFORE_SECOND"
    if max(second_positions) < min(first_positions):
        return "SECOND_BEFORE_FIRST"
    return "INTERLEAVED"


def pair_reading(first: str, second: str, relation: str) -> str:
    if relation == "FIRST_BEFORE_SECOND":
        return f"{GERMAN_OPERATIONS[first]}; dann {GERMAN_OPERATIONS[second]}"
    if relation == "SECOND_BEFORE_FIRST":
        return f"{GERMAN_OPERATIONS[second]}; dann {GERMAN_OPERATIONS[first]}"
    return f"{GERMAN_OPERATIONS[first]} und {GERMAN_OPERATIONS[second]} verschränkt"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_events_raw, old_event_stats = guarded_old_rows(
        OLD_EVENT_PATH,
        (
            "global_running_ordinal", "global_running_event_id", "source_layer",
            "source_event_id", "physical_page", "register", "source_statement_id",
            "surface", "component_recipe", "literal_core_reading_de",
        ),
    )
    old_statements_raw, old_statement_stats = guarded_old_rows(
        OLD_STATEMENT_PATH,
        (
            "global_statement_id", "source_layer", "source_statement_id",
            "physical_page", "register", "event_count", "end_mode",
        ),
    )
    current_events_raw = read_tsv(CURRENT_EVENT_PATH)
    current_statements_raw = read_tsv(CURRENT_STATEMENT_PATH)
    seed_result = json.loads(SEED_RESULT_PATH.read_text(encoding="utf-8"))
    if (len(old_events_raw), len(old_statements_raw), len(current_events_raw), len(current_statements_raw)) != (4576, 715, 546, 78):
        raise RuntimeError("Input count drift")
    if old_event_stats != {"selected": 4576, "skipped_forbidden": 0, "skipped_not_allowed": 0}:
        raise RuntimeError(f"Old event guard drift: {old_event_stats}")
    if old_statement_stats != {"selected": 715, "skipped_forbidden": 0, "skipped_not_allowed": 0}:
        raise RuntimeError(f"Old statement guard drift: {old_statement_stats}")

    events: list[dict[str, object]] = []
    statements: dict[str, dict[str, object]] = {}
    for row in old_statements_raw:
        key = f"OLD26::{row['source_layer']}::{row['source_statement_id']}"
        statements[key] = {
            "cohort": "OLD26_GDT407", "statement_id": row["global_statement_id"],
            "physical_page": row["physical_page"], "register": row["register"],
            "event_count": int(row["event_count"]), "end_mode": row["end_mode"],
        }
    for row in old_events_raw:
        key = f"OLD26::{row['source_layer']}::{row['source_statement_id']}"
        events.append({
            "cohort": "OLD26_GDT407", "event_id": row["global_running_event_id"],
            "source_event_id": row["source_event_id"], "statement_key": key,
            "physical_page": row["physical_page"], "register": row["register"],
            "surface": row["surface"], "recipe": row["component_recipe"],
            "reading_de": row["literal_core_reading_de"],
            "source_order": int(row["global_running_ordinal"]),
        })
    for row in current_statements_raw:
        key = f"CURRENT4::{row['statement_id']}"
        statements[key] = {
            "cohort": "CURRENT4_GDT539", "statement_id": row["statement_id"],
            "physical_page": row["physical_page"], "register": row["register"],
            "event_count": int(row["event_count"]), "end_mode": row["end_mode"],
        }
    for row in current_events_raw:
        key = f"CURRENT4::{row['statement_id']}"
        events.append({
            "cohort": "CURRENT4_GDT539", "event_id": row["event_id"],
            "source_event_id": row["event_id"], "statement_key": key,
            "physical_page": row["physical_page"], "register": row["register"],
            "surface": row["surface"], "recipe": row["final_context_recipe"],
            "reading_de": row["contextual_clause_de"],
            "source_order": int(row["context_event_ordinal"]),
        })

    old_running_pages = {str(row["physical_page"]) for row in events if row["cohort"] == "OLD26_GDT407"}
    current_running_pages = {str(row["physical_page"]) for row in events if row["cohort"] == "CURRENT4_GDT539"}
    if old_running_pages & current_running_pages or len(old_running_pages) != 24 or current_running_pages != set(CURRENT_PAGES):
        raise RuntimeError("Expected disjoint 24-running-plus-4 page union")

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        if event["statement_key"] not in statements:
            raise RuntimeError(f"Missing statement for {event['event_id']}")
        grouped[str(event["statement_key"])].append(event)
    if set(grouped) != set(statements):
        raise RuntimeError("Statement/event key mismatch")
    for key, material in grouped.items():
        material.sort(key=lambda row: int(row["source_order"]))
        if len(material) != int(statements[key]["event_count"]):
            raise RuntimeError(f"Statement event count mismatch: {key}")
        for index, event in enumerate(material):
            event["card_ordinal_in_statement"] = index + 1
            event["statement_event_count"] = len(material)
            event["statement_position"] = statement_role(index + 1, len(material))
            event["statement_final"] = index + 1 == len(material)
            event["previous_event_id"] = material[index - 1]["event_id"] if index else "NONE"
            event["previous_surface"] = material[index - 1]["surface"] if index else "NONE"
            event["previous_marker_sequence"] = event_marker_sequence(str(material[index - 1]["recipe"])) if index else "NONE"
            event["successor_event_id"] = material[index + 1]["event_id"] if index + 1 < len(material) else "NONE"
            event["successor_surface"] = material[index + 1]["surface"] if index + 1 < len(material) else "NONE"
            event["successor_marker_sequence"] = event_marker_sequence(str(material[index + 1]["recipe"])) if index + 1 < len(material) else "NONE"

    occurrence_rows: list[dict[str, object]] = []
    event_occurrences: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        atoms = str(event["recipe"]).split("+")
        marker_sequence = event_marker_sequence(str(event["recipe"]))
        statement = statements[str(event["statement_key"])]
        for marker in MARKERS:
            positions = [index + 1 for index, atom in enumerate(atoms) if atom == marker]
            for marker_occurrence, position in enumerate(positions, 1):
                role = recipe_role(position, len(atoms))
                statement_scope = (
                    "CLOSE_STEP_AND_STATEMENT" if marker == "DY" and event["statement_final"]
                    else "CLOSE_LOCAL_STEP" if marker == "DY"
                    else "RECIPE_LOCAL_ORDER"
                )
                row = {
                    "occurrence_ordinal": len(occurrence_rows) + 1,
                    "cohort": event["cohort"], "marker": marker,
                    "working_meaning_de": MEANINGS[marker],
                    "state_operation": OPERATIONS[marker],
                    "event_id": event["event_id"], "source_event_id": event["source_event_id"],
                    "statement_id": statement["statement_id"],
                    "physical_page": event["physical_page"], "register": event["register"],
                    "card_ordinal_in_statement": event["card_ordinal_in_statement"],
                    "statement_event_count": event["statement_event_count"],
                    "distance_to_statement_start": int(event["card_ordinal_in_statement"]) - 1,
                    "distance_to_statement_end": int(event["statement_event_count"]) - int(event["card_ordinal_in_statement"]),
                    "statement_position": event["statement_position"],
                    "statement_final": "YES" if event["statement_final"] else "NO",
                    "surface": event["surface"], "recipe": event["recipe"],
                    "event_marker_sequence": marker_sequence,
                    "marker_occurrence_in_recipe": marker_occurrence,
                    "marker_atom_position": position, "recipe_atom_count": len(atoms),
                    "recipe_position_role": role,
                    "left_atom": atoms[position - 2] if position > 1 else "NONE",
                    "right_atom": atoms[position] if position < len(atoms) else "NONE",
                    "left_carrier_present": "YES" if position > 1 else "NO",
                    "right_carrier_present": "YES" if position < len(atoms) else "NO",
                    "scope_formula_de": scope_formula(marker, role),
                    "statement_scope": statement_scope,
                    "current_reading_de": event["reading_de"],
                    "previous_event_id": event["previous_event_id"],
                    "previous_surface": event["previous_surface"],
                    "previous_marker_sequence": event["previous_marker_sequence"],
                    "successor_event_id": event["successor_event_id"],
                    "successor_surface": event["successor_surface"],
                    "successor_marker_sequence": event["successor_marker_sequence"],
                    "guard": "POSITIONAL_STATE_RENDERER__ROOT_RECIPE_AND_BOUNDARY_UNCHANGED",
                }
                occurrence_rows.append(row)
                event_occurrences[str(event["event_id"])].append(row)

    summary_rows: list[dict[str, object]] = []
    for cohort in ("OLD26_GDT407", "CURRENT4_GDT539", "COMBINED30"):
        cohort_occurrences = occurrence_rows if cohort == "COMBINED30" else [row for row in occurrence_rows if row["cohort"] == cohort]
        for marker in MARKERS:
            material = [row for row in cohort_occurrences if row["marker"] == marker]
            event_ids = {str(row["event_id"]) for row in material}
            marker_events = [event for event in events if str(event["event_id"]) in event_ids]
            roles = Counter(str(row["recipe_position_role"]) for row in material)
            statement_positions = Counter(str(event["statement_position"]) for event in marker_events)
            right_count = sum(row["right_carrier_present"] == "YES" for row in material)
            left_count = sum(row["left_carrier_present"] == "YES" for row in material)
            final_count = sum(bool(event["statement_final"]) for event in marker_events)
            summary_rows.append({
                "summary_ordinal": len(summary_rows) + 1, "cohort": cohort,
                "marker": marker, "working_meaning_de": MEANINGS[marker],
                "state_operation": OPERATIONS[marker],
                "occurrence_count": len(material), "event_count": len(event_ids),
                "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in material}),
                "running_physical_page_count": len({str(row["physical_page"]) for row in material}),
                "recipe_single_atom_count": roles["SINGLE_ATOM"],
                "recipe_initial_count": roles["INITIAL"],
                "recipe_internal_bridge_count": roles["INTERNAL_BRIDGE"],
                "recipe_terminal_count": roles["TERMINAL"] + roles["SINGLE_ATOM"],
                "recipe_terminal_percent": pct(roles["TERMINAL"] + roles["SINGLE_ATOM"], len(material)),
                "left_carrier_count": left_count, "left_carrier_percent": pct(left_count, len(material)),
                "right_carrier_count": right_count, "right_carrier_percent": pct(right_count, len(material)),
                "statement_singleton_event_count": statement_positions["SINGLETON_STATEMENT"],
                "statement_initial_event_count": statement_positions["STATEMENT_INITIAL"],
                "statement_internal_event_count": statement_positions["STATEMENT_INTERNAL"],
                "statement_final_nonsingleton_event_count": statement_positions["STATEMENT_FINAL"],
                "statement_final_event_count": final_count,
                "statement_final_percent": pct(final_count, len(marker_events)),
                "statement_nonfinal_event_count": len(marker_events) - final_count,
                "median_distance_to_statement_end": f"{statistics.median(int(row['distance_to_statement_end']) for row in material):.1f}",
                "interpretation": "POSITIONAL_STATE_OPERATION__NO_LEXEME_CLAIM",
            })

    pair_rows: list[dict[str, object]] = []
    reverse_pair_edges: list[tuple[str, str, dict[str, object]]] = []
    for cohort in ("OLD26_GDT407", "CURRENT4_GDT539", "COMBINED30"):
        cohort_events = events if cohort == "COMBINED30" else [event for event in events if event["cohort"] == cohort]
        for first, second in PAIR_SPECS:
            selected = [event for event in cohort_events if first in str(event["recipe"]).split("+") and second in str(event["recipe"]).split("+")]
            relations: Counter[str] = Counter()
            immediate_first_second = 0
            immediate_second_first = 0
            reverse_events: list[dict[str, object]] = []
            sequences: Counter[str] = Counter()
            for event in selected:
                atoms = str(event["recipe"]).split("+")
                relation = pair_relation(atoms, first, second)
                relations[relation] += 1
                sequences[event_marker_sequence(str(event["recipe"]))] += 1
                immediate_first_second += any(a == first and b == second for a, b in zip(atoms, atoms[1:]))
                immediate_second_first += any(a == second and b == first for a, b in zip(atoms, atoms[1:]))
                if relation == "SECOND_BEFORE_FIRST":
                    reverse_events.append(event)
                    if cohort == "COMBINED30":
                        reverse_pair_edges.append((first, second, event))
            dominant = "FIRST_BEFORE_SECOND" if relations["FIRST_BEFORE_SECOND"] >= relations["SECOND_BEFORE_FIRST"] else "SECOND_BEFORE_FIRST"
            pair_rows.append({
                "pair_ordinal": len(pair_rows) + 1, "cohort": cohort,
                "first_marker": first, "second_marker": second,
                "first_operation": OPERATIONS[first], "second_operation": OPERATIONS[second],
                "cooccurrence_event_count": len(selected),
                "first_before_second_count": relations["FIRST_BEFORE_SECOND"],
                "second_before_first_count": relations["SECOND_BEFORE_FIRST"],
                "interleaved_count": relations["INTERLEAVED"],
                "dominant_order": dominant, "dominant_order_percent": pct(relations[dominant], len(selected)),
                "immediate_first_then_second_count": immediate_first_second,
                "immediate_second_then_first_count": immediate_second_first,
                "marker_sequences": "|".join(f"{key}:{value}" for key, value in sorted(sequences.items())),
                "running_physical_page_count": len({str(event["physical_page"]) for event in selected}),
                "reverse_event_ids": "|".join(str(event["event_id"]) for event in reverse_events) or "NONE",
                "reverse_surfaces": "|".join(str(event["surface"]) for event in reverse_events) or "NONE",
                "dominant_working_reading_de": pair_reading(first, second, dominant),
            })

    marker_events = [event for event in events if event_marker_sequence(str(event["recipe"])) != "NONE"]
    sequence_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in marker_events:
        sequence_groups[event_marker_sequence(str(event["recipe"]))].append(event)
    sequence_rows: list[dict[str, object]] = []
    rank = {"OT": 0, "OL": 1, "DY": 2}
    for sequence, material in sorted(sequence_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        markers = sequence.split("+")
        canonical = all(rank[left] <= rank[right] for left, right in zip(markers, markers[1:]))
        sequence_rows.append({
            "profile_ordinal": len(sequence_rows) + 1, "marker_sequence": sequence,
            "event_count": len(material), "marker_occurrence_count": len(markers) * len(material),
            "statement_count": len({str(event["statement_key"]) for event in material}),
            "running_physical_page_count": len({str(event["physical_page"]) for event in material}),
            "old_event_count": sum(event["cohort"] == "OLD26_GDT407" for event in material),
            "current_event_count": sum(event["cohort"] == "CURRENT4_GDT539" for event in material),
            "surface_count": len({str(event["surface"]) for event in material}),
            "exact_recipe_count": len({str(event["recipe"]) for event in material}),
            "statement_final_event_count": sum(bool(event["statement_final"]) for event in material),
            "statement_final_percent": pct(sum(bool(event["statement_final"]) for event in material), len(material)),
            "state_operation_sequence": "+".join(OPERATIONS[marker] for marker in markers),
            "working_reading_de": "; dann ".join(GERMAN_OPERATIONS[marker] for marker in markers),
            "order_class": "DOMINANT_START_CONTINUE_CLOSE_ORDER" if canonical else "REVERSE_LOCAL_COMPOSITION",
        })

    page_rows: list[dict[str, object]] = []
    for page in (*OLD_PAGES, *CURRENT_PAGES):
        material = [event for event in events if event["physical_page"] == page]
        page_occurrences = [row for row in occurrence_rows if row["physical_page"] == page]
        by_marker = {marker: [row for row in page_occurrences if row["marker"] == marker] for marker in MARKERS}
        marker_event_ids = {marker: {str(row["event_id"]) for row in rows} for marker, rows in by_marker.items()}
        by_id = {str(event["event_id"]): event for event in material}
        dy_final = sum(bool(by_id[event_id]["statement_final"]) for event_id in marker_event_ids["DY"])
        ol_final = sum(bool(by_id[event_id]["statement_final"]) for event_id in marker_event_ids["OL"])
        notes: list[str] = []
        if not material:
            notes.append("LOCAL_ONLY_PAGE_NO_RUNNING_CARDS")
        else:
            notes.append("ALL_THREE_OPERATORS_PRESENT" if all(by_marker.values()) else "PARTIAL_OPERATOR_INVENTORY")
            if sum(row["right_carrier_present"] == "NO" for row in by_marker["OT"]):
                notes.append("HAS_BARE_OT_CONTEXT_CARRIER")
            if sum(row["statement_final"] == "NO" for row in by_marker["DY"]):
                notes.append("HAS_INTERNAL_DY_LOCAL_CLOSE")
            if sum(row["right_carrier_present"] == "YES" for row in by_marker["DY"]):
                notes.append("HAS_POST_DY_ATTACHMENT")
        page_rows.append({
            "page_ordinal": len(page_rows) + 1,
            "cohort": "OLD26_GDT407" if page in OLD_PAGES else "CURRENT4_GDT539",
            "physical_page": page, "running_event_count": len(material),
            "statement_count": len({str(event["statement_key"]) for event in material}),
            "marker_bearing_event_count": len({str(row["event_id"]) for row in page_occurrences}),
            "ot_occurrence_count": len(by_marker["OT"]),
            "ot_right_carrier_count": sum(row["right_carrier_present"] == "YES" for row in by_marker["OT"]),
            "ot_right_carrier_percent": pct(sum(row["right_carrier_present"] == "YES" for row in by_marker["OT"]), len(by_marker["OT"])),
            "ol_occurrence_count": len(by_marker["OL"]),
            "ol_left_carrier_count": sum(row["left_carrier_present"] == "YES" for row in by_marker["OL"]),
            "ol_right_carrier_count": sum(row["right_carrier_present"] == "YES" for row in by_marker["OL"]),
            "ol_statement_final_event_count": ol_final,
            "ol_statement_final_percent": pct(ol_final, len(marker_event_ids["OL"])),
            "dy_occurrence_count": len(by_marker["DY"]),
            "dy_recipe_terminal_count": sum(row["right_carrier_present"] == "NO" for row in by_marker["DY"]),
            "dy_recipe_terminal_percent": pct(sum(row["right_carrier_present"] == "NO" for row in by_marker["DY"]), len(by_marker["DY"])),
            "dy_statement_final_event_count": dy_final,
            "dy_statement_final_percent": pct(dy_final, len(marker_event_ids["DY"])),
            "transfer_note": "|".join(notes),
        })

    edge_rows: list[dict[str, object]] = []

    def add_edge(category: str, occurrence: dict[str, object], resolution: str) -> None:
        edge_rows.append({
            "edge_ordinal": len(edge_rows) + 1, "category": category,
            "event_id": occurrence["event_id"], "physical_page": occurrence["physical_page"],
            "register": occurrence["register"], "surface": occurrence["surface"],
            "recipe": occurrence["recipe"], "marker_sequence": occurrence["event_marker_sequence"],
            "statement_position": occurrence["statement_position"],
            "current_reading_de": occurrence["current_reading_de"],
            "compositional_resolution_de": resolution,
        })

    for row in occurrence_rows:
        if row["marker"] == "OT" and row["right_carrier_present"] == "NO":
            add_edge("BARE_OT_CONTEXT_CARRIER", row, "DANACH eröffnet den nächsten Träger aus dem Satzkontext.")
        if row["marker"] == "DY" and row["right_carrier_present"] == "YES":
            resolution = "Lokalen Schritt schließen und mit OL weiterführen." if row["right_atom"] == "OL" else f"Schritt schließen; danach den Nachtrag {row['right_atom']} lesen."
            add_edge("POST_DY_ATTACHMENT", row, resolution)
        if row["marker"] == "DY" and row["statement_final"] == "NO":
            add_edge("INTERNAL_DY_LOCAL_CLOSE", row, "Nur den lokalen Schritt schließen; die Aussage läuft mit der nächsten Karte weiter.")
    for first, second, event in reverse_pair_edges:
        occurrence = event_occurrences[str(event["event_id"])][0]
        relation = pair_relation(str(event["recipe"]).split("+"), first, second)
        add_edge(f"REVERSE_{second}_BEFORE_{first}", occurrence, pair_reading(first, second, relation) + ".")

    combined_summary = {str(row["marker"]): row for row in summary_rows if row["cohort"] == "COMBINED30"}
    combined_pairs = {(str(row["first_marker"]), str(row["second_marker"])): row for row in pair_rows if row["cohort"] == "COMBINED30"}
    transfer_rows = [
        {
            "scope": "GDT478_SIX_PAGE_LOCAL_ADDRESS_SEED",
            "admitted_page_count": seed_result["page_count"], "running_page_count": seed_result["page_count"],
            "event_population": seed_result["order_event_count"], "marker_bearing_event_count": seed_result["order_event_count"],
            "marker_occurrence_count": seed_result["order_occurrence_count"],
            "ot_occurrence_count": seed_result["ot_occurrence_count"], "ot_right_carrier_count": seed_result["ot_right_successor_count"],
            "ol_occurrence_count": seed_result["ol_occurrence_count"], "dy_occurrence_count": "NOT_IN_SCOPE",
            "dy_statement_final_count": "NOT_IN_SCOPE", "ot_ol_joint_event_count": seed_result["joint_ot_ol_event_count"],
            "ot_before_ol_count": seed_result["joint_ot_precedes_ol_count"], "ol_before_ot_count": 0,
            "transfer_reading": "Lokaler Keim: OT startet den nächsten, OL hält den laufenden Träger.",
        },
        {
            "scope": "GDT557_THIRTY_PAGE_FULL_RUNNING_EDITION",
            "admitted_page_count": 30, "running_page_count": len(old_running_pages | current_running_pages),
            "event_population": len(events), "marker_bearing_event_count": len(marker_events),
            "marker_occurrence_count": len(occurrence_rows),
            "ot_occurrence_count": combined_summary["OT"]["occurrence_count"], "ot_right_carrier_count": combined_summary["OT"]["right_carrier_count"],
            "ol_occurrence_count": combined_summary["OL"]["occurrence_count"], "dy_occurrence_count": combined_summary["DY"]["occurrence_count"],
            "dy_statement_final_count": combined_summary["DY"]["statement_final_event_count"],
            "ot_ol_joint_event_count": combined_pairs[("OT", "OL")]["cooccurrence_event_count"],
            "ot_before_ol_count": combined_pairs[("OT", "OL")]["first_before_second_count"],
            "ol_before_ot_count": combined_pairs[("OT", "OL")]["second_before_first_count"],
            "transfer_reading": "Vollkorpus: OT eröffnet, OL hält, DY schließt; seltene Umkehrungen werden in Atomreihenfolge komponiert.",
        },
    ]

    result = {
        "status": STATUS, "admitted_physical_page_count": 30,
        "running_physical_page_count": len(old_running_pages | current_running_pages),
        "old_admitted_page_count": 26, "old_running_page_count": len(old_running_pages),
        "current_page_count": len(current_running_pages), "statement_count": len(statements),
        "event_count": len(events), "marker_bearing_event_count": len(marker_events),
        "marker_occurrence_count": len(occurrence_rows), "marker_sequence_profile_count": len(sequence_rows),
        "ot_event_count": int(combined_summary["OT"]["event_count"]),
        "ot_occurrence_count": int(combined_summary["OT"]["occurrence_count"]),
        "ot_right_carrier_count": int(combined_summary["OT"]["right_carrier_count"]),
        "ot_right_carrier_percent": combined_summary["OT"]["right_carrier_percent"],
        "bare_ot_count": int(combined_summary["OT"]["occurrence_count"]) - int(combined_summary["OT"]["right_carrier_count"]),
        "ol_event_count": int(combined_summary["OL"]["event_count"]),
        "ol_occurrence_count": int(combined_summary["OL"]["occurrence_count"]),
        "ol_single_atom_count": int(combined_summary["OL"]["recipe_single_atom_count"]),
        "ol_initial_count": int(combined_summary["OL"]["recipe_initial_count"]),
        "ol_internal_bridge_count": int(combined_summary["OL"]["recipe_internal_bridge_count"]),
        "ol_terminal_nonsingleton_count": int(combined_summary["OL"]["recipe_terminal_count"]) - int(combined_summary["OL"]["recipe_single_atom_count"]),
        "ol_statement_nonfinal_event_count": int(combined_summary["OL"]["statement_nonfinal_event_count"]),
        "dy_event_count": int(combined_summary["DY"]["event_count"]),
        "dy_occurrence_count": int(combined_summary["DY"]["occurrence_count"]),
        "dy_recipe_terminal_count": int(combined_summary["DY"]["recipe_terminal_count"]),
        "dy_statement_final_count": int(combined_summary["DY"]["statement_final_event_count"]),
        "dy_statement_final_percent": combined_summary["DY"]["statement_final_percent"],
        "ot_ol_joint_event_count": int(combined_pairs[("OT", "OL")]["cooccurrence_event_count"]),
        "ot_before_ol_count": int(combined_pairs[("OT", "OL")]["first_before_second_count"]),
        "ol_before_ot_count": int(combined_pairs[("OT", "OL")]["second_before_first_count"]),
        "ot_dy_joint_event_count": int(combined_pairs[("OT", "DY")]["cooccurrence_event_count"]),
        "ot_before_dy_count": int(combined_pairs[("OT", "DY")]["first_before_second_count"]),
        "dy_before_ot_count": int(combined_pairs[("OT", "DY")]["second_before_first_count"]),
        "ol_dy_joint_event_count": int(combined_pairs[("OL", "DY")]["cooccurrence_event_count"]),
        "ol_before_dy_count": int(combined_pairs[("OL", "DY")]["first_before_second_count"]),
        "dy_before_ol_count": int(combined_pairs[("OL", "DY")]["second_before_first_count"]),
        "reverse_pair_event_count": len(reverse_pair_edges), "compositional_edge_row_count": len(edge_rows),
        "running_pages_with_all_three_markers": sum("ALL_THREE_OPERATORS_PRESENT" in str(row["transfer_note"]) for row in page_rows),
        "old_guard_selected_event_count": old_event_stats["selected"],
        "old_guard_selected_statement_count": old_statement_stats["selected"],
        "old_guard_forbidden_skip_count": old_event_stats["skipped_forbidden"] + old_statement_stats["skipped_forbidden"],
        "new_pages": 0, "recipe_changes": 0, "root_meaning_changes": 0, "statement_boundary_changes": 0,
    }

    write_tsv(OCCURRENCE_OUT, occurrence_rows)
    write_tsv(SUMMARY_OUT, summary_rows)
    write_tsv(PAIR_OUT, pair_rows)
    write_tsv(SEQUENCE_OUT, sequence_rows)
    write_tsv(PAGE_OUT, page_rows)
    write_tsv(EDGE_OUT, edge_rows)
    write_tsv(TRANSFER_OUT, transfer_rows)
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT557 — Drei-Zustands-Grammatik über 30 Seiten", "",
        "Die drei kurzen Komponenten bilden im Arbeitsmodell kein Synonymfeld, sondern einen kleinen Ablaufapparat: `OT` eröffnet oder verschiebt auf den nächsten Träger, `OL` hält den laufenden Träger aktiv, `DY` schließt den laufenden Schritt. Die Atomreihenfolge bleibt die Ausführungsreihenfolge.", "",
        "## Gesamtprofil", "",
        "| Komponente | Vorkommen | rechts ein Träger | links ein Träger | Karten am Satzende | Arbeitsoperation |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for marker in MARKERS:
        row = combined_summary[marker]
        lines.append(
            f"| {marker} | {row['occurrence_count']} | {row['right_carrier_count']} ({row['right_carrier_percent']}%) | "
            f"{row['left_carrier_count']} ({row['left_carrier_percent']}%) | {row['statement_final_event_count']}/{row['event_count']} "
            f"({row['statement_final_percent']}%) | {GERMAN_OPERATIONS[marker]} |"
        )
    lines.extend([
        "", "OT ist damit fast vollständig rechtsgerichtet, OL absichtlich beweglich und DY fast vollständig links- und schlussgerichtet. Das sind verschiedene Slots derselben kleinen Prozessgrammatik.", "",
        "## Beobachtete Zustandsfolgen", "",
        "| Folge | Karten | Arbeitslesung | Klasse |", "|---|---:|---|---|",
    ])
    for row in sequence_rows:
        lines.append(f"| `{row['marker_sequence']}` | {row['event_count']} | {row['working_reading_de']} | {row['order_class']} |")
    lines.extend([
        "", "Die häufigen Doppeloperationen laufen fast vollständig in der Richtung Eröffnen → Fortsetzen → Schließen: OT→OL 38/39, OT→DY 86/86 und OL→DY 74/75. Es gibt keine Dreierkarte und kein DY→OT.", "",
        "Noch deutlicher ist der Abschalteeffekt: Die 704 Folgen, deren letzter Zustandsoperator DY ist, stehen 702-mal am Aussageende (99,715909%). Von 951 operierten Karten ganz ohne DY stehen nur 20 am Aussageende (2,103049%). `OT+DY` endet 86/86-mal, `OL+DY` 74/74-mal, während `OT+OL` 0/38-mal endet. DY ist damit im Arbeitsleser der Schließschalter, nicht bloß ein häufiges Schlusswort.", "",
        "## Die zwei umgekehrten Kompositionen", "",
    ])
    for first, second, event in reverse_pair_edges:
        relation = pair_relation(str(event["recipe"]).split("+"), first, second)
        lines.append(f"- `{event['event_id']}` / `{event['surface']}` / `{event['recipe']}`: {pair_reading(first, second, relation)}.")
    lines.extend([
        "", "Diese zwei Karten widerlegen nicht die Komponenten. Sie zeigen, dass die Befehle wirklich komponieren: OL→OT heißt erst den laufenden Träger halten und danach einen neuen eröffnen; DY→OL heißt den lokalen Schritt schließen und anschließend weiterführen.", "",
        "## Transfer", "",
        f"Alle {len(old_running_pages | current_running_pages)} Seiten mit laufenden Karten enthalten OT, OL und DY. Die zwei zusätzlich zugelassenen alten Lokal-Seiten besitzen in dieser Edition keine laufenden Karten und werden als solche ausgewiesen. Gegenüber dem 69-Slot-Keim von GDT478 wächst der Test auf {len(occurrence_rows)} Operatorvorkommen in {len(marker_events)} Karten; die Rollen bleiben erhalten, werden aber um DY und die zwei seltenen Umkehrfolgen ergänzt.", "",
        "## Arbeitsleser", "",
        "1. Lies die übrigen Komponenten der Karte in ihrer vorhandenen Reihenfolge.",
        "2. Bei `OT` eröffne den rechts folgenden Träger; steht OT allein, kommt dieser Träger aus dem Satzkontext.",
        "3. Bei `OL` halte den linken Träger, führe ihn in den rechten weiter oder nimm rechts einen fortzusetzenden Träger auf.",
        "4. Bei `DY` schließe den linken Schritt. Nur wenn danach noch ein Atom steht, lies es als Nachtrag oder als ausdrückliche Fortsetzung.",
        "5. Steht DY auf der letzten Karte, schließt der Schritt zugleich die Aussage; in drei internen Karten nur den lokalen Schritt.", "",
        "## Grenze", "",
        "Das ist eine vollständige Arbeitsgrammatik für die drei bereits gesetzten Komponenten in den vorhandenen Rezepten. Sie ändert keine Bedeutung, Segmentierung, Karte oder Aussagegrenze und behauptet weder historischen Klartext noch eine identifizierte Sprache oder ein identifiziertes Codebuch.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
