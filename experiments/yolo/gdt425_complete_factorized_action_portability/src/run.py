#!/usr/bin/env python3
"""Replay the complete running edition as factorized action obligations."""

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
BASE = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
ATTACHMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"
OLD_APPENDIX = ROOT / "experiments/yolo/gdt424_page_private_slot_exception_compression/artifacts/gdt424_7_local_appendix_rules.tsv"

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
    clauses = read_tsv(CLAUSES)
    attachments = read_tsv(ATTACHMENTS)
    old_appendix = read_tsv(OLD_APPENDIX)
    clause_by_event = {row["global_running_event_id"]: row for row in clauses}

    attachments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    focus_edge_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in attachments:
        attachments_by_event[row["global_running_event_id"]].append(row)
        focus_edge_pages[(row["action_core"], row["focus_core"])].add(row["physical_page"])

    pair_occurrences: list[tuple[dict[str, str], str, str, int]] = []
    pair_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in clauses:
        atoms = row["component_recipe"].split("+")
        for index in range(len(atoms) - 1):
            if atoms[index] in ACTIONS and atoms[index + 1] in ACTIONS:
                pair_occurrences.append((row, atoms[index], atoms[index + 1], index + 1))
                pair_pages[(atoms[index], atoms[index + 1])].add(row["physical_page"])

    close_targets: list[tuple[dict[str, str], str]] = []
    close_head_pages: dict[str, set[str]] = defaultdict(set)
    for row in clauses:
        atoms = row["component_recipe"].split("+")
        if "DY" not in atoms:
            continue
        explicit_actions = [atom for atom in atoms if atom in ACTIONS]
        target = explicit_actions[-1] if explicit_actions else row["inherited_action_root"]
        if target == "NONE":
            raise RuntimeError(f"close without explicit or inherited action: {row['global_running_event_id']}")
        close_targets.append((row, target))
        close_head_pages[target].add(row["physical_page"])

    focus_rows: list[dict[str, object]] = []
    local_action_rules_by_event: dict[str, list[str]] = defaultdict(list)
    local_owner_rules_by_event: dict[str, list[str]] = defaultdict(list)
    for row in attachments:
        edge = (row["action_core"], row["focus_core"])
        other_pages = sorted(focus_edge_pages[edge] - {row["physical_page"]})
        if other_pages:
            status = "CROSS_PAGE_EXACT_FOCUS_EDGE"
        elif row["action_core"] in {"OWNER", "VISIBLE_OWNER"}:
            status = "LOCAL_OWNER_CHANNEL_ALLOWED"
            local_owner_rules_by_event[row["global_running_event_id"]].append(f"OWNER:{row['focus_core']}")
        else:
            status = "LOCAL_ACTION_FOCUS_EDGE"
            local_action_rules_by_event[row["global_running_event_id"]].append(f"FOCUS:{row['action_core']}<-{row['focus_core']}")
        focus_rows.append({
            "global_attachment_id": row["global_attachment_id"],
            "global_running_event_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "focus_core": row["focus_core"],
            "action_core": row["action_core"],
            "focus_edge": f"{row['action_core']}<-{row['focus_core']}",
            "selector_rule": row["selector_rule"],
            "attachment_geometry": row["attachment_geometry"],
            "r_topology": row["r_topology"],
            "other_page_count": len(other_pages),
            "other_pages": "|".join(other_pages) if other_pages else "NONE",
            "portability_status": status,
        })

    pair_rows: list[dict[str, object]] = []
    local_pair_rules_by_event: dict[str, list[str]] = defaultdict(list)
    for row, left, right, ordinal in pair_occurrences:
        event_id = row["global_running_event_id"]
        other_pages = sorted(pair_pages[(left, right)] - {row["physical_page"]})
        r_topologies = sorted({a["r_topology"] for a in attachments_by_event[event_id] if a["r_topology"] != "NONE"})
        if other_pages:
            status = "CROSS_PAGE_EXACT_ADJACENT_PAIR"
        elif left == right:
            status = "OLD_REPEATED_ACTION_SCOPE"
        elif r_topologies:
            status = "OLD_R_TOPOLOGY_SPLIT"
        else:
            status = "LOCAL_ADJACENT_PAIR"
            local_pair_rules_by_event[event_id].append(f"PAIR:{left}>{right}")
        pair_rows.append({
            "global_running_event_id": event_id,
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "pair_ordinal_in_recipe": ordinal,
            "ordered_pair": f"{left}>{right}",
            "r_topology": "|".join(r_topologies) if r_topologies else "NONE",
            "other_page_count": len(other_pages),
            "other_pages": "|".join(other_pages) if other_pages else "NONE",
            "portability_status": status,
        })

    close_rows: list[dict[str, object]] = []
    for row, target in close_targets:
        other_pages = sorted(close_head_pages[target] - {row["physical_page"]})
        close_rows.append({
            "global_running_event_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "close_target_action": target,
            "target_source": "EXPLICIT_LAST_ACTION" if any(atom in ACTIONS for atom in row["component_recipe"].split("+")) else "INHERITED_ACTION",
            "other_page_count": len(other_pages),
            "other_pages": "|".join(other_pages),
            "portability_status": "CROSS_PAGE_ACTION_CLOSE",
        })

    event_rows: list[dict[str, object]] = []
    appendix_occurrences: list[dict[str, str]] = []
    for row in clauses:
        event_id = row["global_running_event_id"]
        explicit_actions = [atom for atom in row["component_recipe"].split("+") if atom in ACTIONS]
        inherited_actions = [] if row["inherited_action_root"] == "NONE" else row["inherited_action_root"].split("|")
        local_rules = sorted(set(local_action_rules_by_event[event_id] + local_pair_rules_by_event[event_id]))
        owner_rules = sorted(set(local_owner_rules_by_event[event_id]))
        if local_rules:
            status = "LOCAL_ACTION_APPENDIX_REQUIRED"
        elif explicit_actions or inherited_actions:
            status = "CROSS_PAGE_ACTION_FACTORS_COMPLETE"
        elif owner_rules:
            status = "LOCAL_OWNER_CHANNEL_ONLY"
        else:
            status = "OUTSIDE_ACTION_GRAMMAR_NO_ACTION_HEAD"
        for rule in local_rules:
            appendix_occurrences.append({
                "rule_id": rule,
                "rule_type": "LOCAL_ADJACENT_PAIR" if rule.startswith("PAIR:") else "LOCAL_ACTION_FOCUS_EDGE",
                "physical_page": row["physical_page"],
                "global_running_event_id": event_id,
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
            })
        event_rows.append({
            "global_running_event_id": event_id,
            "global_statement_id": row["global_statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "explicit_action_roots": row["explicit_action_roots"],
            "inherited_action_root": row["inherited_action_root"],
            "focus_attachment_count": len(attachments_by_event[event_id]),
            "adjacent_pair_count": sum(1 for pair in pair_rows if pair["global_running_event_id"] == event_id),
            "has_close": "YES" if "DY" in row["component_recipe"].split("+") else "NO",
            "local_action_rules": "|".join(local_rules) if local_rules else "NONE",
            "local_owner_rules": "|".join(owner_rules) if owner_rules else "NONE",
            "factorized_action_replay_status": status,
            "imperative_clause_de": row["imperative_clause_de"],
        })

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in appendix_occurrences:
        grouped[row["rule_id"]].append(row)
    appendix_rows: list[dict[str, object]] = []
    for rule_id, members in sorted(grouped.items()):
        appendix_rows.append({
            "rule_id": rule_id,
            "rule_type": members[0]["rule_type"],
            "portable_status": "LOCAL_ONLY_UNTIL_SECOND_PAGE",
            "pages": "|".join(sorted({row["physical_page"] for row in members})),
            "event_count": len(members),
            "event_ids": "|".join(row["global_running_event_id"] for row in members),
            "surfaces": "|".join(sorted({row["surface"] for row in members})),
            "component_recipes": "|".join(sorted({row["component_recipe"] for row in members})),
        })

    current_rules = {row["rule_id"] for row in appendix_rows}
    revision_rows: list[dict[str, object]] = []
    for row in old_appendix:
        old_rule = row["rule_id"]
        if old_rule.startswith("PACKAGE:CLOSE:R&FOCUS:R<-AIR"):
            new_rule = "FOCUS:R<-AIR"
            decision = "REVISED_CLOSE_IS_CROSS_PAGE_VIA_INHERITED_R"
        elif old_rule in current_rules:
            new_rule = old_rule
            decision = "RETAIN_LOCAL"
        else:
            new_rule = "NONE"
            decision = "PROMOTED_CROSS_PAGE_FROM_COMPLEX_CONTEXT"
        revision_rows.append({
            "gdt424_rule_id": old_rule,
            "gdt425_rule_id": new_rule,
            "gdt425_decision": decision,
            "gdt424_pages": row["pages"],
            "gdt424_surfaces": row["surfaces"],
        })

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in event_rows}):
        members = [row for row in event_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "registers": "|".join(sorted({str(row["register"]) for row in members})),
            "event_count": len(members),
            "cross_page_action_event_count": sum(row["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE" for row in members),
            "local_action_appendix_event_count": sum(row["factorized_action_replay_status"] == "LOCAL_ACTION_APPENDIX_REQUIRED" for row in members),
            "local_owner_channel_event_count": sum(row["factorized_action_replay_status"] == "LOCAL_OWNER_CHANNEL_ONLY" for row in members),
            "outside_action_grammar_event_count": sum(row["factorized_action_replay_status"] == "OUTSIDE_ACTION_GRAMMAR_NO_ACTION_HEAD" for row in members),
        })

    event_rows.sort(key=lambda row: row["global_running_event_id"])
    focus_rows.sort(key=lambda row: row["global_attachment_id"])
    pair_rows.sort(key=lambda row: (row["global_running_event_id"], int(row["pair_ordinal_in_recipe"])))
    close_rows.sort(key=lambda row: row["global_running_event_id"])
    write_tsv(OUT / "gdt425_4576_event_factorized_action_replay.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "gdt425_5051_focus_edge_portability.tsv", focus_rows, list(focus_rows[0]))
    write_tsv(OUT / "gdt425_649_adjacent_pair_portability.tsv", pair_rows, list(pair_rows[0]))
    write_tsv(OUT / "gdt425_639_close_edge_portability.tsv", close_rows, list(close_rows[0]))
    write_tsv(OUT / "gdt425_9_local_action_appendix.tsv", appendix_rows, list(appendix_rows[0]))
    write_tsv(OUT / "gdt425_7_gdt424_rule_revisions.tsv", revision_rows, list(revision_rows[0]))
    write_tsv(OUT / "gdt425_24_page_summary.tsv", page_rows, list(page_rows[0]))

    card = [
        "# Vollständige Handlungsgrammatik", "",
        "1. Binde Grad, Argument und Relation an den von GDT407 gewählten Einzelkopf.",
        "2. Lerne nur unmittelbar benachbarte Handlungen als geordnetes Paar.",
        "3. Wiederholung und sichtbare R-Topologie teilen eine scheinbar neue Paarung.",
        "4. Binde DY an die letzte sichtbare oder geerbte Handlung.",
        "5. Alles Übrige braucht höchstens eine der neun lokalen Zusatzkarten.", "",
        "## Neun lokale Karten", "",
    ]
    card.extend(f"- `{row['rule_id']}` auf {row['pages']}: {row['surfaces']}" for row in appendix_rows)
    (OUT / "COMPLETE_ACTION_GRAMMAR_CARD.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    status_counts = Counter(row["factorized_action_replay_status"] for row in event_rows)
    result = {
        "status": "COMPLETE_FACTORIZED_ACTION_REPLAY_WITH_NINE_LOCAL_CARDS",
        "page_key_count": len(page_rows),
        "admitted_physical_page_or_panel_count": 26,
        "event_count": len(event_rows),
        "event_status_counts": dict(sorted(status_counts.items())),
        "action_bearing_event_count": sum(bool(row["explicit_action_roots"] != "NONE" or row["inherited_action_root"] != "NONE") for row in event_rows),
        "cross_page_action_event_count": status_counts["CROSS_PAGE_ACTION_FACTORS_COMPLETE"],
        "local_action_appendix_event_count": status_counts["LOCAL_ACTION_APPENDIX_REQUIRED"],
        "focus_edge_count": len(focus_rows),
        "cross_page_focus_edge_count": sum(row["portability_status"] == "CROSS_PAGE_EXACT_FOCUS_EDGE" for row in focus_rows),
        "local_action_focus_edge_count": sum(row["portability_status"] == "LOCAL_ACTION_FOCUS_EDGE" for row in focus_rows),
        "local_owner_focus_edge_count": sum(row["portability_status"] == "LOCAL_OWNER_CHANNEL_ALLOWED" for row in focus_rows),
        "adjacent_pair_occurrence_count": len(pair_rows),
        "cross_page_adjacent_pair_count": sum(row["portability_status"] == "CROSS_PAGE_EXACT_ADJACENT_PAIR" for row in pair_rows),
        "old_topology_or_repeat_pair_count": sum(row["portability_status"] in {"OLD_REPEATED_ACTION_SCOPE", "OLD_R_TOPOLOGY_SPLIT"} for row in pair_rows),
        "local_adjacent_pair_count": sum(row["portability_status"] == "LOCAL_ADJACENT_PAIR" for row in pair_rows),
        "close_edge_count": len(close_rows),
        "cross_page_close_edge_count": sum(row["portability_status"] == "CROSS_PAGE_ACTION_CLOSE" for row in close_rows),
        "local_action_appendix_rule_count": len(appendix_rows),
        "new_roots": 0,
        "dictionary_revisions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt425_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
