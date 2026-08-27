#!/usr/bin/env python3
"""Classify no-action/no-argument events by exact same-statement consumers."""

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
BASE = ROOT / "experiments/yolo/gdt555_incomplete_card_successor_roles"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G554 = ROOT / "experiments/yolo/gdt554_statement_semantic_template_audit/artifacts"

SOURCE_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
EVENT_IN = G554 / "gdt554_546_event_semantic_templates.tsv"
STATEMENT_IN = G554 / "gdt554_78_statement_template_atlas.tsv"

UNION_OUT = OUT / "gdt555_64_unique_gap_events.tsv"
ACTIONLESS_OUT = OUT / "gdt555_16_actionless_successor_roles.tsv"
ARGUMENTLESS_OUT = OUT / "gdt555_57_argumentless_successor_roles.tsv"
LINK_OUT = OUT / "gdt555_exact_initializer_links.tsv"
PROFILE_OUT = OUT / "gdt555_gap_surface_role_profiles.tsv"
SUMMARY_OUT = OUT / "gdt555_role_summary.tsv"
BOOK_OUT = OUT / "GDT555_GAP_ROLE_BOOK.md"
RESULT_OUT = OUT / "gdt555_result.json"

STATUS = "PASS_64_UNIQUE_GAPS_CLASSIFIED__EXACT_SOURCE_POINTERS_ONLY"
RELATION = {"AL", "AR", "L", "AIR"}

ROLE_DE = {
    "ARGUMENT_INITIALIZER": "setzt ein Argument für eine spätere Karte",
    "CLOSURE_BOUNDARY": "objektlose Abschluss- oder Grenzkarte",
    "PRE_ACTION_SCOPE_PROLOGUE": "setzt Relation oder Adresse vor der ersten Handlung",
    "CONTINUATION_PROLOGUE": "setzt eine Fortsetzungsangabe vor der ersten Handlung",
    "NOMINAL_CONTROL_PROLOGUE": "verbfreier nominaler oder steuernder Vorspann",
    "STANDALONE_NOMINAL_OR_CONTROL_BOUNDARY": "selbständige nominale oder steuernde Grenzkarte",
    "ACTION_INITIALIZER": "setzt eine Handlung für eine spätere Karte",
    "OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY": "objektlose Handlung mit Abschluss- oder Satzgrenze",
    "CARRIED_ACTION_OBJECTLESS_CONTROL": "führt eine geerbte Handlung objektlos durch eine Steuerkarte",
    "OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET": "objektlose Handlung vor einer neuen sichtbaren Handlung",
    "OBJECTLESS_STANDALONE_ACTION": "selbständige objektlose Handlung",
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


def atoms(row: dict[str, str]) -> list[str]:
    return row["final_recipe"].split("+")


def actionless_role(
    row: dict[str, str], argument_consumers: list[dict[str, str]],
    successor: dict[str, str] | None, is_last: bool,
) -> str:
    material = atoms(row)
    if argument_consumers:
        return "ARGUMENT_INITIALIZER"
    if "DY" in material and is_last:
        return "CLOSURE_BOUNDARY"
    if successor and any(atom in RELATION or atom.endswith("_ADDR") for atom in material):
        return "PRE_ACTION_SCOPE_PROLOGUE"
    if successor and "OL" in material:
        return "CONTINUATION_PROLOGUE"
    if successor:
        return "NOMINAL_CONTROL_PROLOGUE"
    return "STANDALONE_NOMINAL_OR_CONTROL_BOUNDARY"


def argumentless_role(
    row: dict[str, str], action_consumers: list[dict[str, str]],
    successor: dict[str, str] | None, is_last: bool,
) -> str:
    material = atoms(row)
    if row["resolved_action_roots"] == "NONE":
        return "NO_ACTION__" + actionless_role(row, [], successor, is_last)
    if action_consumers:
        return "ACTION_INITIALIZER"
    if "DY" in material or is_last:
        return "OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY"
    if row["inherited_action_root"] != "NONE":
        return "CARRIED_ACTION_OBJECTLESS_CONTROL"
    if successor:
        return "OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET"
    return "OBJECTLESS_STANDALONE_ACTION"


def immediate_consumers(
    material: list[dict[str, str]], current_ordinal: int,
) -> list[dict[str, str]]:
    return [
        row for row in material
        if int(row["card_ordinal_in_statement"]) == current_ordinal + 1
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = read_tsv(SOURCE_IN)
    events = read_tsv(EVENT_IN)
    statements = read_tsv(STATEMENT_IN)
    if (len(sources), len(events), len(statements)) != (546, 546, 78):
        raise RuntimeError("Input count drift")
    source_by_id = {row["event_id"]: row for row in sources}
    event_by_id = {row["event_id"]: row for row in events}
    if set(source_by_id) != set(event_by_id):
        raise RuntimeError("GDT539/GDT554 event identity drift")

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    for material in events_by_statement.values():
        material.sort(key=lambda row: int(row["card_ordinal_in_statement"]))

    action_consumers: dict[str, list[dict[str, str]]] = defaultdict(list)
    argument_consumers: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in sources:
        if source["inherited_action_source_event_id"] != "NONE":
            action_consumers[source["inherited_action_source_event_id"]].append(source)
        if source["inherited_argument_source_event_id"] != "NONE":
            argument_consumers[source["inherited_argument_source_event_id"]].append(source)

    actionless_ids = {
        row["event_id"] for row in events if row["resolved_action_roots"] == "NONE"
    }
    argumentless_ids = {
        row["event_id"] for row in events if row["resolved_argument_roots"] == "NONE"
    }
    gap_ids = actionless_ids | argumentless_ids
    overlap_ids = actionless_ids & argumentless_ids
    if (len(actionless_ids), len(argumentless_ids), len(overlap_ids), len(gap_ids)) != (16, 57, 9, 64):
        raise RuntimeError("Gap partition drift")

    gap_rows: list[dict[str, object]] = []
    link_rows: list[dict[str, object]] = []
    for event in events:
        event_id = event["event_id"]
        if event_id not in gap_ids:
            continue
        material = events_by_statement[event["statement_id"]]
        ordinal = int(event["card_ordinal_in_statement"])
        predecessor = material[ordinal - 2] if ordinal > 1 else None
        successor = material[ordinal] if ordinal < len(material) else None
        a_consumers = sorted(
            action_consumers.get(event_id, []),
            key=lambda row: int(row["card_ordinal_in_statement"]),
        )
        x_consumers = sorted(
            argument_consumers.get(event_id, []),
            key=lambda row: int(row["card_ordinal_in_statement"]),
        )
        for dimension, consumers, source_roots in (
            ("ACTION_STATE", a_consumers, event["explicit_action_roots"]),
            ("ARGUMENT_STATE", x_consumers, event["explicit_argument_roots"]),
        ):
            for consumer in consumers:
                consumer_event = event_by_id[consumer["event_id"]]
                distance = int(consumer["card_ordinal_in_statement"]) - ordinal
                if distance <= 0 or consumer["statement_id"] != event["statement_id"]:
                    raise RuntimeError(f"Invalid consumer link from {event_id}")
                link_rows.append({
                    "link_ordinal": len(link_rows) + 1,
                    "state_dimension": dimension,
                    "source_event_id": event_id,
                    "source_statement_id": event["statement_id"],
                    "source_card_ordinal": ordinal,
                    "source_surface": event["surface"],
                    "source_roots": source_roots,
                    "source_clause_de": event["contextual_clause_de"],
                    "consumer_event_id": consumer["event_id"],
                    "consumer_card_ordinal": consumer["card_ordinal_in_statement"],
                    "consumer_surface": consumer_event["surface"],
                    "consumer_clause_de": consumer_event["contextual_clause_de"],
                    "card_distance": distance,
                    "immediate_successor": "YES" if distance == 1 else "NO",
                    "paired_reading_de": event["contextual_clause_de"] + " → " + consumer_event["contextual_clause_de"],
                    "source_pointer_exact": "YES",
                    "same_statement": "YES",
                    "guard": "EXISTING_CLAUSES_JOINED__NO_NEW_WORD_OR_MEANING",
                })

        a_role = actionless_role(event, x_consumers, successor, ordinal == len(material)) if event_id in actionless_ids else "NOT_ACTIONLESS"
        x_role = argumentless_role(event, a_consumers, successor, ordinal == len(material)) if event_id in argumentless_ids else "NOT_ARGUMENTLESS"
        primary = a_role if event_id in actionless_ids else x_role
        immediate_a = immediate_consumers(a_consumers, ordinal)
        immediate_x = immediate_consumers(x_consumers, ordinal)
        paired = event["contextual_clause_de"]
        if immediate_a or immediate_x:
            consumer_ids = {row["event_id"] for row in immediate_a + immediate_x}
            consumer = next(row for row in material if row["event_id"] in consumer_ids)
            paired += " → " + consumer["contextual_clause_de"]
        gap_rows.append({
            "gap_ordinal": len(gap_rows) + 1,
            "event_id": event_id,
            "statement_id": event["statement_id"],
            "card_ordinal_in_statement": ordinal,
            "statement_event_count": len(material),
            "physical_page": event["physical_page"],
            "register": event["register"],
            "surface": event["surface"],
            "final_recipe": event["final_recipe"],
            "action_gap": "YES" if event_id in actionless_ids else "NO",
            "argument_gap": "YES" if event_id in argumentless_ids else "NO",
            "overlap_gap": "YES" if event_id in overlap_ids else "NO",
            "statement_initial": "YES" if ordinal == 1 else "NO",
            "statement_final": "YES" if ordinal == len(material) else "NO",
            "predecessor_event_id": predecessor["event_id"] if predecessor else "NONE",
            "successor_event_id": successor["event_id"] if successor else "NONE",
            "explicit_action_roots": event["explicit_action_roots"],
            "inherited_action_root": event["inherited_action_root"],
            "resolved_action_roots": event["resolved_action_roots"],
            "explicit_argument_roots": event["explicit_argument_roots"],
            "inherited_argument_root": event["inherited_argument_root"],
            "resolved_argument_roots": event["resolved_argument_roots"],
            "action_consumer_count": len(a_consumers),
            "immediate_action_consumer_count": len(immediate_a),
            "argument_consumer_count": len(x_consumers),
            "immediate_argument_consumer_count": len(immediate_x),
            "action_consumer_event_ids": "|".join(row["event_id"] for row in a_consumers) or "NONE",
            "argument_consumer_event_ids": "|".join(row["event_id"] for row in x_consumers) or "NONE",
            "actionless_role": a_role,
            "argumentless_role": x_role,
            "primary_gap_role": primary,
            "primary_gap_role_de": ROLE_DE.get(primary.removeprefix("NO_ACTION__"), ROLE_DE.get(primary, primary)),
            "portable_semantic_macro": event["portable_semantic_macro"],
            "current_clause_de": event["contextual_clause_de"],
            "immediate_paired_reading_de": paired,
            "retention": "EXACT_GDT554_RECIPE_MACRO_AND_CLAUSE_RETAINED",
        })

    gap_by_id = {row["event_id"]: row for row in gap_rows}
    actionless_rows = [
        {"actionless_ordinal": index, **row}
        for index, row in enumerate((gap_by_id[event_id] for event_id in [row["event_id"] for row in events] if event_id in actionless_ids), 1)
    ]
    argumentless_rows = [
        {"argumentless_ordinal": index, **row}
        for index, row in enumerate((gap_by_id[event_id] for event_id in [row["event_id"] for row in events] if event_id in argumentless_ids), 1)
    ]

    profiles: list[dict[str, object]] = []
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in gap_rows:
        by_surface[str(row["surface"])].append(row)
    for surface, rows in sorted(by_surface.items()):
        roles = sorted({str(row["primary_gap_role"]) for row in rows})
        profiles.append({
            "profile_ordinal": len(profiles) + 1,
            "surface": surface,
            "final_recipes": "|".join(sorted({str(row["final_recipe"]) for row in rows})),
            "gap_event_count": len(rows),
            "action_gap_event_count": sum(row["action_gap"] == "YES" for row in rows),
            "argument_gap_event_count": sum(row["argument_gap"] == "YES" for row in rows),
            "primary_role_count": len(roles),
            "primary_roles": "|".join(roles),
            "exact_initializer_event_count": sum(
                int(row["action_consumer_count"]) + int(row["argument_consumer_count"]) > 0
                for row in rows
            ),
            "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in rows})),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "status": "CONTEXT_ROLE_VARIATION" if len(roles) > 1 else "ONE_OBSERVED_GAP_ROLE",
            "guard": "SURFACE_ROLE_PROFILE_IS_CONTEXTUAL__NOT_NEW_LEXICAL_MEANING",
        })

    summary_rows: list[dict[str, object]] = []
    for dimension, rows, role_field in (
        ("UNIQUE_GAP", gap_rows, "primary_gap_role"),
        ("ACTIONLESS", actionless_rows, "actionless_role"),
        ("ARGUMENTLESS", argumentless_rows, "argumentless_role"),
    ):
        counts = Counter(str(row[role_field]) for row in rows)
        for role, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            summary_rows.append({
                "summary_ordinal": len(summary_rows) + 1,
                "gap_dimension": dimension,
                "role": role,
                "role_de": ROLE_DE.get(role.removeprefix("NO_ACTION__"), ROLE_DE.get(role, role)),
                "event_count": count,
                "physical_page_count": len({str(row["physical_page"]) for row in rows if row[role_field] == role}),
                "register_count": len({str(row["register"]) for row in rows if row[role_field] == role}),
                "event_ids": "|".join(str(row["event_id"]) for row in rows if row[role_field] == role),
            })

    result = {
        "status": STATUS,
        "actionless_event_count": len(actionless_rows),
        "argumentless_event_count": len(argumentless_rows),
        "overlap_gap_event_count": len(overlap_ids),
        "unique_gap_event_count": len(gap_rows),
        "gap_surface_count": len(profiles),
        "action_initializer_event_count": sum(row["argumentless_role"] == "ACTION_INITIALIZER" for row in argumentless_rows),
        "argument_initializer_event_count": sum(row["actionless_role"] == "ARGUMENT_INITIALIZER" for row in actionless_rows),
        "initializer_source_event_count": len({row["source_event_id"] for row in link_rows}),
        "initializer_link_count": len(link_rows),
        "immediate_initializer_link_count": sum(row["immediate_successor"] == "YES" for row in link_rows),
        "delayed_initializer_link_count": sum(row["immediate_successor"] == "NO" for row in link_rows),
        "maximum_initializer_distance": max(int(row["card_distance"]) for row in link_rows),
        "action_state_link_count": sum(row["state_dimension"] == "ACTION_STATE" for row in link_rows),
        "argument_state_link_count": sum(row["state_dimension"] == "ARGUMENT_STATE" for row in link_rows),
        "multi_role_gap_surface_count": sum(int(row["primary_role_count"]) > 1 for row in profiles),
        "all_gap_roles_populated": all(row["primary_gap_role"] for row in gap_rows),
        "new_pages": 0,
        "new_recipes": 0,
        "root_meaning_changes": 0,
        "german_reading_changes": 0,
    }

    write_tsv(UNION_OUT, gap_rows)
    write_tsv(ACTIONLESS_OUT, actionless_rows)
    write_tsv(ARGUMENTLESS_OUT, argumentless_rows)
    write_tsv(LINK_OUT, link_rows)
    write_tsv(PROFILE_OUT, profiles)
    write_tsv(SUMMARY_OUT, summary_rows)
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GDT555 — Arbeitsbuch der scheinbar unvollständigen Karten", "",
        "Die 16 aktionslosen und 57 argumentlosen Mengen überlappen in neun Ereignissen. Das gemeinsame Deck enthält deshalb 64, nicht 73, Kartenereignisse.", "",
        "## Exakte Initialisierungslinks", "",
    ]
    for row in link_rows:
        lines.append(
            f"- **{row['state_dimension']} · Abstand {row['card_distance']}:** "
            f"`{row['source_event_id']}` → `{row['consumer_event_id']}` — "
            f"{row['paired_reading_de']}"
        )
    lines.extend(["", "## Alle 64 eindeutigen Lückenereignisse", ""])
    for row in gap_rows:
        lines.extend([
            f"### {row['event_id']} · `{row['surface']}` · {row['primary_gap_role']}", "",
            str(row["immediate_paired_reading_de"]), "",
            f"Rezept: `{row['final_recipe']}` · Makro: `{row['portable_semantic_macro']}`", "",
        ])
    lines.extend([
        "## Grenze", "",
        "Ein Initialisierungslink ist nur dann gesetzt, wenn die spätere Karte die Quell-ID ausdrücklich als ihren geerbten Zustand nennt. Alle anderen Rollen bleiben kontextuelle Arbeitsrollen, keine neuen Wortbedeutungen.", "",
    ])
    BOOK_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
