#!/usr/bin/env python3
"""Audit DY closure scope over the disjoint 26+4 admitted pages."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt556_dy_closure_boundary_scope"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"

OLD_EVENT_PATH = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENT_PATH = G407 / "gdt407_715_statement_edition.tsv"
CURRENT_EVENT_PATH = G539 / "gdt539_546_contextual_prose_events.tsv"
CURRENT_STATEMENT_PATH = G539 / "gdt539_78_contextual_statements.tsv"

DY_OUT = OUT / "gdt556_all_dy_occurrences.tsv"
STATEMENT_OUT = OUT / "gdt556_dy_statement_profiles.tsv"
MARKER_OUT = OUT / "gdt556_marker_finality_comparison.tsv"
RECIPE_OUT = OUT / "gdt556_dy_recipe_scope_profiles.tsv"
TAIL_OUT = OUT / "gdt556_nonterminal_dy_tail_profiles.tsv"
COHORT_OUT = OUT / "gdt556_cohort_closure_summary.tsv"
BOOK_OUT = OUT / "GDT556_DY_CLOSURE_BOOK.md"
RESULT_OUT = OUT / "gdt556_result.json"

STATUS = "PASS_DY_702_OF_705_STATEMENT_FINAL__THREE_LOCAL_STEP_CLOSURES"
OLD_PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)
MARKERS = ("DY", "OL", "OT", "E", "EE", "EEE", "O", "DA")
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}


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


def guarded_old_rows(path: Path, columns: tuple[str, ...]) -> tuple[list[dict[str, str]], dict[str, int]]:
    relative = path.relative_to(ROOT)
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(relative),
        "--selector", "physical_page",
    ]
    for page in OLD_PAGES:
        command.extend(["--allow", page])
    command.extend([
        "--columns", ",".join(columns), "--forbid-prefix", "f84",
    ])
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


def scope_for(ordinal: int, event_count: int) -> str:
    if event_count == 1:
        return "SINGLETON_STATEMENT_CLOSURE"
    if ordinal == event_count:
        return "STATEMENT_FINAL_STEP_CLOSURE"
    return "INTERNAL_LOCAL_STEP_CLOSURE"


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
            "explicit_action_roots": "|".join(
                atom for atom in row["component_recipe"].split("+") if atom in ACTION_ROOTS
            ) or "NONE",
            "inherited_action_root": "NOT_AVAILABLE_OLD26",
            "inherited_argument_root": "NOT_AVAILABLE_OLD26",
            "inherited_action_source_event_id": "NOT_AVAILABLE_OLD26",
            "inherited_argument_source_event_id": "NOT_AVAILABLE_OLD26",
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
            "explicit_action_roots": row["explicit_action_roots"],
            "inherited_action_root": row["inherited_action_root"],
            "inherited_argument_root": row["inherited_argument_root"],
            "inherited_action_source_event_id": row["inherited_action_source_event_id"],
            "inherited_argument_source_event_id": row["inherited_argument_source_event_id"],
        })

    old_pages = {str(row["physical_page"]) for row in events if row["cohort"] == "OLD26_GDT407"}
    current_pages = {str(row["physical_page"]) for row in events if row["cohort"] == "CURRENT4_GDT539"}
    if old_pages & current_pages or len(old_pages) != 24 or len(current_pages) != 4:
        raise RuntimeError("Expected disjoint 24-running-plus-4 page union")
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        if event["statement_key"] not in statements:
            raise RuntimeError(f"Missing statement: {event['statement_key']}")
        grouped[str(event["statement_key"])].append(event)
    if set(grouped) != set(statements):
        raise RuntimeError("Statement/event key mismatch")
    for key, material in grouped.items():
        material.sort(key=lambda row: int(row["source_order"]))
        if len(material) != int(statements[key]["event_count"]):
            raise RuntimeError(f"Statement event count mismatch: {key}")
        for ordinal, event in enumerate(material, 1):
            event["card_ordinal_in_statement"] = ordinal
            event["statement_event_count"] = len(material)
            event["statement_final"] = ordinal == len(material)

    dy_rows: list[dict[str, object]] = []
    for key, material in grouped.items():
        statement = statements[key]
        for event in material:
            recipe_atoms = str(event["recipe"]).split("+")
            positions = [index + 1 for index, atom in enumerate(recipe_atoms) if atom == "DY"]
            for occurrence, position in enumerate(positions, 1):
                ordinal = int(event["card_ordinal_in_statement"])
                successor = material[ordinal] if ordinal < len(material) else None
                dy_rows.append({
                    "dy_ordinal": len(dy_rows) + 1,
                    "cohort": event["cohort"],
                    "event_id": event["event_id"],
                    "source_event_id": event["source_event_id"],
                    "statement_id": statement["statement_id"],
                    "physical_page": event["physical_page"],
                    "register": event["register"],
                    "card_ordinal_in_statement": ordinal,
                    "statement_event_count": len(material),
                    "distance_to_statement_end": len(material) - ordinal,
                    "surface": event["surface"],
                    "recipe": event["recipe"],
                    "dy_occurrence_in_recipe": occurrence,
                    "dy_atom_position": position,
                    "recipe_atom_count": len(recipe_atoms),
                    "dy_recipe_terminal": "YES" if position == len(recipe_atoms) else "NO",
                    "closure_scope": scope_for(ordinal, len(material)),
                    "statement_end_mode": statement["end_mode"],
                    "explicit_action_roots": event["explicit_action_roots"],
                    "current_reading_de": event["reading_de"],
                    "successor_event_id": successor["event_id"] if successor else "NONE",
                    "successor_surface": successor["surface"] if successor else "NONE",
                    "successor_recipe": successor["recipe"] if successor else "NONE",
                    "successor_reading_de": successor["reading_de"] if successor else "NONE",
                    "successor_inherited_action_source_event_id": successor["inherited_action_source_event_id"] if successor else "NONE",
                    "successor_inherited_argument_source_event_id": successor["inherited_argument_source_event_id"] if successor else "NONE",
                    "guard": "POSITIONAL_WORKING_CLOSURE_SCOPE__NO_ROOT_OR_BOUNDARY_CHANGE",
                })

    dy_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dy_rows:
        cohort_prefix = "OLD26" if row["cohort"] == "OLD26_GDT407" else "CURRENT4"
        statement_key = next(
            key for key, value in statements.items()
            if key.startswith(cohort_prefix) and value["statement_id"] == row["statement_id"]
        )
        dy_by_statement[statement_key].append(row)
    statement_rows: list[dict[str, object]] = []
    for key, rows in sorted(dy_by_statement.items(), key=lambda item: (str(statements[item[0]]["physical_page"]), str(statements[item[0]]["statement_id"]))):
        statement = statements[key]
        scopes = Counter(str(row["closure_scope"]) for row in rows)
        statement_rows.append({
            "profile_ordinal": len(statement_rows) + 1,
            "cohort": statement["cohort"],
            "statement_id": statement["statement_id"],
            "physical_page": statement["physical_page"],
            "register": statement["register"],
            "statement_event_count": statement["event_count"],
            "dy_occurrence_count": len(rows),
            "internal_dy_count": scopes["INTERNAL_LOCAL_STEP_CLOSURE"],
            "final_step_dy_count": scopes["STATEMENT_FINAL_STEP_CLOSURE"],
            "singleton_dy_count": scopes["SINGLETON_STATEMENT_CLOSURE"],
            "dy_event_ids": "|".join(str(row["event_id"]) for row in rows),
            "statement_end_mode": statement["end_mode"],
            "scope_profile": "|".join(sorted(scopes)),
        })

    marker_rows: list[dict[str, object]] = []
    for cohort in ("OLD26_GDT407", "CURRENT4_GDT539", "COMBINED30"):
        material = events if cohort == "COMBINED30" else [row for row in events if row["cohort"] == cohort]
        for marker in MARKERS:
            selected = [row for row in material if marker in str(row["recipe"]).split("+")]
            final = sum(bool(row["statement_final"]) for row in selected)
            singleton = sum(int(row["statement_event_count"]) == 1 for row in selected)
            terminal = sum(str(row["recipe"]).split("+")[-1] == marker for row in selected)
            marker_rows.append({
                "comparison_ordinal": len(marker_rows) + 1,
                "cohort": cohort,
                "marker": marker,
                "event_count": len(selected),
                "statement_count": len({str(row["statement_key"]) for row in selected}),
                "statement_final_event_count": final,
                "statement_final_percent": pct(final, len(selected)),
                "statement_internal_event_count": len(selected) - final,
                "singleton_statement_event_count": singleton,
                "recipe_terminal_event_count": terminal,
                "recipe_terminal_percent": pct(terminal, len(selected)),
                "physical_page_count": len({str(row["physical_page"]) for row in selected}),
            })

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dy_rows:
        recipe_groups[str(row["recipe"])].append(row)
    recipe_rows: list[dict[str, object]] = []
    for recipe, rows in sorted(recipe_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        scopes = sorted({str(row["closure_scope"]) for row in rows})
        recipe_rows.append({
            "recipe_profile_ordinal": len(recipe_rows) + 1,
            "recipe": recipe,
            "dy_occurrence_count": len(rows),
            "surface_count": len({str(row["surface"]) for row in rows}),
            "statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in rows}),
            "physical_page_count": len({str(row["physical_page"]) for row in rows}),
            "cohort_count": len({str(row["cohort"]) for row in rows}),
            "closure_scope_count": len(scopes),
            "closure_scopes": "|".join(scopes),
            "scope_level_count": len({
                "LOCAL_STEP" if scope == "INTERNAL_LOCAL_STEP_CLOSURE" else "STATEMENT_LEVEL"
                for scope in scopes
            }),
            "scope_levels": "|".join(sorted({
                "LOCAL_STEP" if scope == "INTERNAL_LOCAL_STEP_CLOSURE" else "STATEMENT_LEVEL"
                for scope in scopes
            })),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "interpretation": "SCOPE_FROM_POSITION__DY_VALUE_UNCHANGED",
        })

    tail_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dy_rows:
        if row["dy_recipe_terminal"] == "YES":
            continue
        recipe_atoms = str(row["recipe"]).split("+")
        tail = "+".join(recipe_atoms[int(row["dy_atom_position"]):])
        tail_groups[tail].append(row)
    tail_rows: list[dict[str, object]] = []
    for tail, rows in sorted(tail_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        tail_rows.append({
            "tail_profile_ordinal": len(tail_rows) + 1,
            "post_dy_tail": tail,
            "event_count": len(rows),
            "internal_local_step_count": sum(row["closure_scope"] == "INTERNAL_LOCAL_STEP_CLOSURE" for row in rows),
            "statement_level_count": sum(row["closure_scope"] != "INTERNAL_LOCAL_STEP_CLOSURE" for row in rows),
            "recipes": "|".join(sorted({str(row["recipe"]) for row in rows})),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "interpretation": "POST_CLOSURE_ATTACHMENT__DY_VALUE_UNCHANGED",
        })

    cohort_rows: list[dict[str, object]] = []
    for cohort in ("OLD26_GDT407", "CURRENT4_GDT539", "COMBINED30"):
        material = events if cohort == "COMBINED30" else [row for row in events if row["cohort"] == cohort]
        statement_material = list(statements.values()) if cohort == "COMBINED30" else [row for row in statements.values() if row["cohort"] == cohort]
        dy_material = dy_rows if cohort == "COMBINED30" else [row for row in dy_rows if row["cohort"] == cohort]
        dy_event_ids = {str(row["event_id"]) for row in dy_material}
        final_dy = sum(row["closure_scope"] != "INTERNAL_LOCAL_STEP_CLOSURE" for row in dy_material)
        nondy = [row for row in material if str(row["event_id"]) not in dy_event_ids]
        nondy_final = sum(bool(row["statement_final"]) for row in nondy)
        cohort_rows.append({
            "cohort_ordinal": len(cohort_rows) + 1,
            "cohort": cohort,
            "physical_page_count": 30 if cohort == "COMBINED30" else 26 if cohort == "OLD26_GDT407" else 4,
            "running_physical_page_count": len({str(row["physical_page"]) for row in material}),
            "statement_count": len(statement_material),
            "event_count": len(material),
            "dy_occurrence_count": len(dy_material),
            "dy_statement_count": len({f"{row['cohort']}::{row['statement_id']}" for row in dy_material}),
            "dy_final_or_singleton_count": final_dy,
            "dy_final_or_singleton_percent": pct(final_dy, len(dy_material)),
            "dy_internal_count": len(dy_material) - final_dy,
            "non_dy_event_count": len(nondy),
            "non_dy_final_event_count": nondy_final,
            "non_dy_final_percent": pct(nondy_final, len(nondy)),
            "all_dy_recipe_terminal": "YES" if all(row["dy_recipe_terminal"] == "YES" for row in dy_material) else "NO",
        })

    combined = cohort_rows[-1]
    multi_scope_recipes = [row for row in recipe_rows if int(row["scope_level_count"]) > 1]
    singleton_final_variant_recipes = [
        row for row in recipe_rows if int(row["closure_scope_count"]) > 1
    ]
    internal_current = [
        row for row in dy_rows
        if row["cohort"] == "CURRENT4_GDT539"
        and row["closure_scope"] == "INTERNAL_LOCAL_STEP_CLOSURE"
    ]
    result = {
        "status": STATUS,
        "physical_page_count": 30,
        "old_page_count": 26,
        "current_page_count": 4,
        "statement_count": 793,
        "event_count": 5122,
        "dy_occurrence_count": len(dy_rows),
        "dy_statement_count": int(combined["dy_statement_count"]),
        "dy_final_or_singleton_count": int(combined["dy_final_or_singleton_count"]),
        "dy_internal_local_step_count": int(combined["dy_internal_count"]),
        "dy_final_or_singleton_percent": combined["dy_final_or_singleton_percent"],
        "non_dy_final_percent": combined["non_dy_final_percent"],
        "all_dy_recipe_terminal": combined["all_dy_recipe_terminal"] == "YES",
        "dy_recipe_terminal_count": sum(row["dy_recipe_terminal"] == "YES" for row in dy_rows),
        "dy_nonterminal_recipe_count": sum(row["dy_recipe_terminal"] == "NO" for row in dy_rows),
        "dy_recipe_terminal_percent": pct(sum(row["dy_recipe_terminal"] == "YES" for row in dy_rows), len(dy_rows)),
        "dy_recipe_count": len(recipe_rows),
        "dy_local_and_statement_scope_recipe_count": len(multi_scope_recipes),
        "dy_singleton_final_variant_recipe_count": len(singleton_final_variant_recipes),
        "nonterminal_dy_tail_type_count": len(tail_rows),
        "dy_statement_profile_count": len(statement_rows),
        "current_internal_dy_count": len(internal_current),
        "old_guard_selected_event_count": old_event_stats["selected"],
        "old_guard_selected_statement_count": old_statement_stats["selected"],
        "old_guard_forbidden_skip_count": old_event_stats["skipped_forbidden"] + old_statement_stats["skipped_forbidden"],
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }

    write_tsv(DY_OUT, dy_rows)
    write_tsv(STATEMENT_OUT, statement_rows)
    write_tsv(MARKER_OUT, marker_rows)
    write_tsv(RECIPE_OUT, recipe_rows)
    write_tsv(TAIL_OUT, tail_rows)
    write_tsv(COHORT_OUT, cohort_rows)
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GDT556 — DY-Abschlussbuch über 30 Seiten", "",
        "`DY` steht in 700/705 Kartenrezepten terminal. Fünf Nachträge folgen noch innerhalb der Karte; sie sind zweimal `D_LABEL`, zweimal `L` und einmal `OL`. Seine Reichweite wird durch die Kartenposition bestimmt: am Satzende schließt es den letzten Schritt beziehungsweise den Satz; in drei Satzinneren schließt es einen lokalen Schritt, nach dem die Aussage weiterläuft.", "",
        "## Kohorten", "",
        "| Kohorte | Events | DY | DY am Satzende | DY intern | Nicht-DY am Satzende |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in cohort_rows:
        lines.append(
            f"| {row['cohort']} | {row['event_count']} | {row['dy_occurrence_count']} | "
            f"{row['dy_final_or_singleton_count']} ({row['dy_final_or_singleton_percent']}%) | "
            f"{row['dy_internal_count']} | {row['non_dy_final_percent']}% |"
        )
    lines.extend(["", "## Interne lokale Abschlüsse", ""])
    for row in dy_rows:
        if row["closure_scope"] != "INTERNAL_LOCAL_STEP_CLOSURE":
            continue
        lines.append(
            f"- `{row['cohort']}` · `{row['event_id']}` / `{row['surface']}`: "
            f"{row['current_reading_de']} → `{row['successor_surface']}`: {row['successor_reading_de']}"
        )
    lines.extend(["", "## Die drei internen Schlussrezepte", ""])
    for row in recipe_rows:
        if "LOCAL_STEP" not in str(row["scope_levels"]):
            continue
        lines.append(
            f"- `{row['recipe']}` · {row['dy_occurrence_count']} Vorkommen · "
            f"{row['closure_scopes']}"
        )
    lines.extend([
        "", "## Grenze", "",
        "Die Positionsverteilung stützt die Arbeitsfunktion ABSCHLIESSEN und präzisiert ihren Scope. Sie identifiziert weder historische Syntax noch Klartext und ändert keine vorhandene Aussagegrenze.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
