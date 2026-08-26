#!/usr/bin/env python3
"""Compress GDT423 red cells with the older factorized attachment map."""

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
BASE = ROOT / "experiments/yolo/gdt424_page_private_slot_exception_compression"
OUT = BASE / "artifacts"
REPLAY = ROOT / "experiments/yolo/gdt423_leave_one_page_action_grammar_replay/artifacts/gdt423_4576_event_leave_page_replay.tsv"
RED_CELLS = ROOT / "experiments/yolo/gdt423_leave_one_page_action_grammar_replay/artifacts/gdt423_57_red_page_slot_cells.tsv"
ATTACHMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(REPLAY)
    red_events = [row for row in events if row["leave_page_replay_status"] == "RED_PAGE_PRIVATE_HEAD_OR_SLOT"]
    red_cells = read_tsv(RED_CELLS)
    attachments = read_tsv(ATTACHMENTS)
    attachments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    focus_edge_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in attachments:
        attachments_by_event[row["global_running_event_id"]].append(row)
        focus_edge_pages[(row["action_core"], row["focus_core"])].add(row["physical_page"])

    # Closure is assigned only to the last visible action in its own recipe.
    close_head_pages: dict[str, set[str]] = defaultdict(set)
    for row in events:
        atoms = row["component_recipe"].split("+")
        action_atoms = [atom for atom in atoms if atom in ACTIONS]
        if "DY" in atoms and action_atoms:
            close_head_pages[action_atoms[-1]].add(row["held_out_page"])

    focus_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    private_pair_rows: list[dict[str, object]] = []
    close_rows: list[dict[str, object]] = []
    exception_occurrences: list[dict[str, str]] = []

    for row in red_events:
        event_id = row["global_running_event_id"]
        page = row["held_out_page"]
        atoms = row["component_recipe"].split("+")
        action_positions = [(index, atom) for index, atom in enumerate(atoms) if atom in ACTIONS]
        actions = [atom for _, atom in action_positions]
        private_rules: list[str] = []

        local_focus_edges: list[str] = []
        for attachment in attachments_by_event[event_id]:
            edge = (attachment["action_core"], attachment["focus_core"])
            other_pages = sorted(focus_edge_pages[edge] - {page})
            status = "OLD_FOCUS_EDGE_OTHER_PAGE" if other_pages else "LOCAL_FOCUS_EDGE"
            if not other_pages:
                rule = f"FOCUS:{attachment['action_core']}<-{attachment['focus_core']}"
                private_rules.append(rule)
                local_focus_edges.append(rule)
            focus_rows.append({
                "global_running_event_id": event_id,
                "held_out_page": page,
                "surface": row["surface"],
                "focus_core": attachment["focus_core"],
                "action_core": attachment["action_core"],
                "focus_edge": f"{attachment['action_core']}<-{attachment['focus_core']}",
                "selector_rule": attachment["selector_rule"],
                "attachment_geometry": attachment["attachment_geometry"],
                "r_topology": attachment["r_topology"],
                "other_page_count": len(other_pages),
                "other_pages": "|".join(other_pages) if other_pages else "NONE",
                "factorized_replay_status": status,
            })

        pair_decision = "NOT_PAGE_PRIVATE_PAIR"
        if "HEAD_OR_ORDERED_PAIR_PAGE_PRIVATE" in row["red_causes"]:
            if len(action_positions) != 2:
                raise RuntimeError(f"unexpected private head cardinality: {event_id}")
            left_index, left_action = action_positions[0]
            right_index, right_action = action_positions[1]
            intervening = atoms[left_index + 1:right_index]
            r_topologies = sorted({a["r_topology"] for a in attachments_by_event[event_id] if a["r_topology"] != "NONE"})
            if intervening or r_topologies:
                pair_decision = "SPLIT_BY_VISIBLE_PACKAGE_OR_R_TOPOLOGY"
            else:
                pair_decision = "LOCAL_ADJACENT_ORDERED_PAIR"
                rule = f"PAIR:{left_action}>{right_action}"
                private_rules.append(rule)
            private_pair_rows.append({
                "global_running_event_id": event_id,
                "held_out_page": page,
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "ordered_pair": f"{left_action}>{right_action}",
                "intervening_atoms": "+".join(intervening) if intervening else "NONE",
                "r_topology": "|".join(r_topologies) if r_topologies else "NONE",
                "pair_decision": pair_decision,
            })

        close_status = "NO_CLOSE"
        if "DY" in atoms:
            terminal_action = actions[-1]
            other_pages = sorted(close_head_pages[terminal_action] - {page})
            close_status = "OLD_TERMINAL_HEAD_CLOSE_OTHER_PAGE" if other_pages else "LOCAL_TERMINAL_HEAD_CLOSE"
            if not other_pages:
                rule = f"CLOSE:{terminal_action}"
                private_rules.append(rule)
            close_rows.append({
                "global_running_event_id": event_id,
                "held_out_page": page,
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "terminal_action": terminal_action,
                "other_page_count": len(other_pages),
                "other_pages": "|".join(other_pages) if other_pages else "NONE",
                "close_replay_status": close_status,
            })

        appendix_rule = "NONE"
        appendix_rule_type = "NONE"
        if private_rules:
            unique_private_rules = sorted(set(private_rules))
            if len(unique_private_rules) == 1:
                appendix_rule = unique_private_rules[0]
                prefix = appendix_rule.split(":", 1)[0]
                appendix_rule_type = {
                    "PAIR": "LOCAL_ADJACENT_ORDERED_PAIR",
                    "FOCUS": "LOCAL_FOCUS_EDGE",
                    "CLOSE": "LOCAL_TERMINAL_HEAD_CLOSE",
                }[prefix]
            else:
                appendix_rule = "PACKAGE:" + "&".join(unique_private_rules)
                appendix_rule_type = "LOCAL_COMPOSITE_PACKAGE"
            exception_occurrences.append({
                "rule_id": appendix_rule,
                "rule_type": appendix_rule_type,
                "held_out_page": page,
                "global_running_event_id": event_id,
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
            })

        event_rows.append({
            "global_running_event_id": event_id,
            "held_out_page": page,
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "gdt423_slot_skeleton": row["slot_skeleton"],
            "gdt423_red_causes": row["red_causes"],
            "focus_attachment_count": len(attachments_by_event[event_id]),
            "local_focus_edges": "|".join(local_focus_edges) if local_focus_edges else "NONE",
            "private_pair_decision": pair_decision,
            "close_replay_status": close_status,
            "local_appendix_rules": appendix_rule,
            "compression_status": "LOCAL_APPENDIX_RULE_REQUIRED" if private_rules else "RESOLVED_BY_FACTORIZED_OLD_RULES",
            "imperative_clause_de": row["imperative_clause_de"],
        })

    event_by_id = {row["global_running_event_id"]: row for row in event_rows}
    cell_rows: list[dict[str, object]] = []
    for cell in red_cells:
        members = [
            row for row in red_events
            if row["held_out_page"] == cell["held_out_page"] and row["slot_skeleton"] == cell["slot_skeleton"]
        ]
        resolved = sum(event_by_id[row["global_running_event_id"]]["compression_status"] == "RESOLVED_BY_FACTORIZED_OLD_RULES" for row in members)
        local = len(members) - resolved
        rules = sorted({
            rule
            for row in members
            for rule in str(event_by_id[row["global_running_event_id"]]["local_appendix_rules"]).split("|")
            if rule != "NONE"
        })
        cell_rows.append({
            "held_out_page": cell["held_out_page"],
            "slot_skeleton": cell["slot_skeleton"],
            "gdt423_red_causes": cell["red_causes"],
            "event_count": len(members),
            "resolved_event_count": resolved,
            "local_appendix_event_count": local,
            "local_appendix_rules": "|".join(rules) if rules else "NONE",
            "compression_status": "RESOLVED_CELL" if local == 0 else "LOCAL_APPENDIX_CELL",
            "event_ids": "|".join(row["global_running_event_id"] for row in members),
            "surfaces": cell["surfaces"],
            "component_recipes": cell["component_recipes"],
        })

    grouped_exceptions: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in exception_occurrences:
        grouped_exceptions[row["rule_id"]].append(row)
    appendix_rows: list[dict[str, object]] = []
    for rule_id, members in sorted(grouped_exceptions.items()):
        appendix_rows.append({
            "rule_id": rule_id,
            "rule_type": members[0]["rule_type"],
            "portable_status": "LOCAL_ONLY_UNTIL_SECOND_PAGE",
            "pages": "|".join(sorted({row["held_out_page"] for row in members})),
            "event_count": len(members),
            "event_ids": "|".join(row["global_running_event_id"] for row in members),
            "surfaces": "|".join(sorted({row["surface"] for row in members})),
            "component_recipes": "|".join(sorted({row["component_recipe"] for row in members})),
            "future_rule": "PROMOTE_ONLY_IF_REPEATED_ON_ANOTHER_PAGE_WITH_SAME_FACTOR_ROLE",
        })

    event_rows.sort(key=lambda row: row["global_running_event_id"])
    focus_rows.sort(key=lambda row: (row["global_running_event_id"], row["focus_core"], row["action_core"]))
    private_pair_rows.sort(key=lambda row: row["global_running_event_id"])
    close_rows.sort(key=lambda row: row["global_running_event_id"])
    cell_rows.sort(key=lambda row: (row["held_out_page"], row["slot_skeleton"]))

    write_tsv(OUT / "gdt424_59_red_event_factorization.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "gdt424_92_focus_edge_replay.tsv", focus_rows, list(focus_rows[0]))
    write_tsv(OUT / "gdt424_14_private_pair_event_adjudications.tsv", private_pair_rows, list(private_pair_rows[0]))
    write_tsv(OUT / "gdt424_9_close_edge_replay.tsv", close_rows, list(close_rows[0]))
    write_tsv(OUT / "gdt424_57_red_cell_compression.tsv", cell_rows, list(cell_rows[0]))
    write_tsv(OUT / "gdt424_7_local_appendix_rules.tsv", appendix_rows, list(appendix_rows[0]))

    card = [
        "# Minimales lokales Handlungs-Zusatzdeck", "",
        "Die 57 roten GDT423-Zellen schrumpfen auf sieben lokale Regeln:", "",
    ]
    for row in appendix_rows:
        card.append(f"- `{row['rule_id']}` auf {row['pages']}: {row['surfaces']}")
    card.extend([
        "", "## Lehrregel", "",
        "- Diese Regeln sind lokal gelernte Kombinationen alter Kerne, keine neuen Wurzeln.",
        "- Sie werden erst portabel, wenn dieselbe Faktorrolle auf einer zweiten Seite erscheint.",
        "- Alle anderen ehemals roten Zellen werden mit der schon vor GDT423 vorhandenen Einzelkopf-Bindung gelesen.",
    ])
    (OUT / "MINIMAL_LOCAL_ACTION_APPENDIX.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    result = {
        "status": "GDT423_RED_QUEUE_COMPRESSED_TO_SEVEN_LOCAL_RULES",
        "gdt423_red_cell_count": len(cell_rows),
        "gdt423_red_event_count": len(event_rows),
        "resolved_red_cell_count": sum(row["compression_status"] == "RESOLVED_CELL" for row in cell_rows),
        "local_appendix_cell_count": sum(row["compression_status"] == "LOCAL_APPENDIX_CELL" for row in cell_rows),
        "resolved_red_event_count": sum(row["compression_status"] == "RESOLVED_BY_FACTORIZED_OLD_RULES" for row in event_rows),
        "local_appendix_event_count": sum(row["compression_status"] == "LOCAL_APPENDIX_RULE_REQUIRED" for row in event_rows),
        "focus_edge_count": len(focus_rows),
        "cross_page_focus_edge_count": sum(row["factorized_replay_status"] == "OLD_FOCUS_EDGE_OTHER_PAGE" for row in focus_rows),
        "local_focus_edge_count": sum(row["factorized_replay_status"] == "LOCAL_FOCUS_EDGE" for row in focus_rows),
        "private_pair_event_count": len(private_pair_rows),
        "split_private_pair_event_count": sum(row["pair_decision"] == "SPLIT_BY_VISIBLE_PACKAGE_OR_R_TOPOLOGY" for row in private_pair_rows),
        "local_adjacent_pair_event_count": sum(row["pair_decision"] == "LOCAL_ADJACENT_ORDERED_PAIR" for row in private_pair_rows),
        "close_edge_count": len(close_rows),
        "cross_page_close_edge_count": sum(row["close_replay_status"] == "OLD_TERMINAL_HEAD_CLOSE_OTHER_PAGE" for row in close_rows),
        "local_appendix_rule_count": len(appendix_rows),
        "local_appendix_page_count": len({page for row in appendix_rows for page in str(row["pages"]).split("|")}),
        "local_appendix_type_counts": dict(sorted(Counter(row["rule_type"] for row in appendix_rows).items())),
        "new_roots": 0,
        "dictionary_revisions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt424_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
