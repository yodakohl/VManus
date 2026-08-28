#!/usr/bin/env python3
"""Build the GDT583 object-conditioned refinement of GDT582."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G582_SRC = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/src"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(G582_SRC))
from defaults import action_noun  # noqa: E402
from passages import EDITORIAL_PARAGRAPHS  # noqa: E402
from rules import REGISTER_ORDER, RULES, TARGET_ROOTS, select_rule  # noqa: E402


INPUTS = {
    "complete": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "events": G582 / "gdt582_5122_concrete_event_edition.tsv",
    "statements": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "passages": G582 / "gdt582_20_complete_passage_sense_checks.tsv",
}

STATUS = (
    "PASS_1921_TARGET_SLOTS__1623_RUNNING_EVENTS__FOUR_ACTION_CLASSES__"
    "OBJECT_GRADE_RELATION_CHAIN_REFINEMENT__TWENTY_PASSAGES__ZERO_NEW_SLOTS"
)


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


def pipe(values: Iterable[str]) -> str:
    items = sorted(set(values))
    return "|".join(items) if items else "NONE"


def condition_text(values: tuple[str, ...]) -> str:
    return "|".join(values) if values else "NONE"


def build_rule_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ordinal, rule in enumerate(sorted(RULES, key=lambda item: item.priority), 1):
        rows.append(
            {
                "rule_ordinal": ordinal,
                "rule_id": rule.rule_id,
                "priority": rule.priority,
                "root": rule.root,
                "registers": condition_text(rule.registers),
                "source_ids": condition_text(rule.source_ids),
                "physical_pages_not": condition_text(rule.physical_pages_not),
                "direct_any": condition_text(rule.direct_any),
                "direct_none": condition_text(rule.direct_none),
                "host_any": condition_text(rule.host_any),
                "host_none": condition_text(rule.host_none),
                "host_any_groups": (
                    ";".join("|".join(group) for group in rule.host_any_groups)
                    if rule.host_any_groups else "NONE"
                ),
                "previous_actions": condition_text(rule.previous_actions),
                "next_actions": condition_text(rule.next_actions),
                "working_default_de": rule.working_default_de,
                "concrete_sense_de": rule.concrete_sense_de,
                "reading_tier": rule.reading_tier,
                "rationale": rule.rationale,
                "scope_guard": (
                    "FIXED_GDT581_ACTION_HOST__REGISTER_OWNER_AND_IMMEDIATE_SAME_CARD_"
                    "ACTION_DIRECTION_ONLY__NO_SURFACE_RESEGMENTATION"
                ),
            }
        )
    return rows


def action_inventory(rows: list[dict[str, str]]) -> set[str]:
    return {
        row["slot_value"]
        for row in rows
        if row["primary_governor_kind"] == "SELF_ACTION"
    }


def neighboring_actions(
    source: dict[str, str], host_rows: list[dict[str, str]]
) -> tuple[str, str]:
    actions = sorted(
        [row for row in host_rows if row["primary_governor_kind"] == "SELF_ACTION"],
        key=lambda row: (int(row["slot_position"]), row["slot_id"]),
    )
    positions = [index for index, row in enumerate(actions) if row["slot_id"] == source["slot_id"]]
    if len(positions) != 1:
        raise RuntimeError(f"Target action is not unique in its card: {source['slot_id']}")
    index = positions[0]
    previous = actions[index - 1]["slot_value"] if index else "NONE"
    following = actions[index + 1]["slot_value"] if index + 1 < len(actions) else "NONE"
    return previous, following


def build_assignments(
    complete: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_governor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete:
        by_host[row["source_event_or_card_id"]].append(row)
        by_governor[row["primary_governor_key"]].append(row)

    rows: list[dict[str, object]] = []
    by_slot: dict[str, dict[str, object]] = {}
    for source in complete:
        root = source["slot_value"]
        if root not in TARGET_ROOTS:
            continue
        host_rows = by_host[source["source_event_or_card_id"]]
        direct_rows = [
            row for row in host_rows
            if row["primary_governor_key"] == source["primary_governor_key"]
        ]
        if root == "T":
            event_id = source["source_event_or_card_id"]
            direct_rows.extend(
                row for row in host_rows
                if row["primary_governor_key"].startswith(f"ACTION_CHAIN:{event_id}:")
                and row["primary_governor_key"].rsplit(":", 1)[-1].split("+")[-1] == "T"
            )
        global_host_rows = by_governor[source["primary_governor_key"]]
        direct_tokens = {row["slot_value"] for row in direct_rows}
        governor_tokens = {row["slot_value"] for row in global_host_rows}
        actions = action_inventory(host_rows)
        previous_action, next_action = neighboring_actions(source, host_rows)
        rule = select_rule(
            root=root,
            register=source["register"],
            source_id=source["source_event_or_card_id"],
            physical_page=source["physical_page"],
            direct_tokens=direct_tokens,
            host_tokens=governor_tokens,
            previous_action=previous_action,
            next_action=next_action,
        )
        old = source["gdt582_concrete_default_de"]
        if governor_tokens == direct_tokens:
            object_scope = "SAME_CARD_DIRECT_HOST"
        elif governor_tokens - direct_tokens:
            object_scope = "COMPLETE_GDT581_HOST_INCLUDES_REMOTE_ARGUMENT"
        else:
            object_scope = "OWNER_OR_REGISTER_ONLY"
        assignment = {
            "assignment_ordinal": len(rows) + 1,
            "slot_id": source["slot_id"],
            "layer": source["layer"],
            "source_event_or_card_id": source["source_event_or_card_id"],
            "statement_or_record_id": source["statement_or_record_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner": source["owner"],
            "surface": source["surface"],
            "slot_position": source["slot_position"],
            "root": root,
            "primary_governor_key": source["primary_governor_key"],
            "direct_governor_tokens": pipe(direct_tokens),
            "governor_group_tokens": pipe(governor_tokens),
            "governor_object_scope": object_scope,
            "same_card_action_inventory": pipe(actions),
            "previous_visible_action": previous_action,
            "next_visible_action": next_action,
            "gdt582_broad_default_de": old,
            "gdt583_rule_id": rule.rule_id,
            "gdt583_working_default_de": rule.working_default_de,
            "gdt583_concrete_sense_de": rule.concrete_sense_de,
            "gdt583_reading_tier": rule.reading_tier,
            "gdt583_change_status": (
                "LEXICALLY_REFINED" if old != rule.working_default_de
                else "SPECIFIC_GDT582_READING_RETAINED"
            ),
            "gdt583_rationale": rule.rationale,
            "gdt583_context_signature": (
                f"{source['register']}::D[{pipe(direct_tokens)}]::"
                f"G[{pipe(governor_tokens)}]::P[{previous_action}]::N[{next_action}]"
            ),
            "gdt583_guard": (
                "EXACT_GDT582_SLOT_AND_PRIMARY_GOVERNOR_RETAINED__"
                "REPLACEABLE_WORKING_SENSE__NO_NEW_SEGMENT"
            ),
        }
        rows.append(assignment)
        by_slot[source["slot_id"]] = assignment

    if len(rows) != 1921 or len(by_slot) != 1921:
        raise RuntimeError(f"Target occurrence drift: {len(rows)} / {len(by_slot)}")
    if Counter(row["root"] for row in rows) != {
        "T": 384, "SH": 794, "CHD": 341, "S": 402,
    }:
        raise RuntimeError("Target root inventory drift")
    return rows, by_slot


def group_label(key: str, register: str) -> str:
    if key.startswith(("ACTION:", "LOCAL_ACTION:")):
        root = key.rsplit(":", 1)[-1]
        return f"beim {action_noun(root, register)} [{key}]"
    if key.startswith("ACTION_CHAIN:"):
        roots = key.rsplit(":", 1)[-1].split("+")
        nouns = [action_noun(root, register) for root in roots]
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


def working_gloss(row: dict[str, object]) -> str:
    return str(row["gdt583_working_default_de"])


def render_trace(rows: list[dict[str, object]]) -> str:
    ordered = sorted(rows, key=lambda row: (int(row["slot_position"]), str(row["slot_id"])))
    return " ".join(
        (
            f"[{row['slot_position']}:{row['slot_value']}={working_gloss(row)}|"
            f"{row['slot_id']}|{row['primary_governor_key']}|"
            f"{row['gdt583_rule_id']}]"
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
        actions = [
            row for row in members if row["primary_governor_kind"] == "SELF_ACTION"
        ]
        others = [row for row in members if row not in actions]
        if actions:
            lead = " und ".join(working_gloss(row) for row in actions)
            if others:
                lead += ": " + ", ".join(working_gloss(row) for row in others)
        else:
            lead = group_label(key, register) + ": " + ", ".join(
                working_gloss(row) for row in others
            )
        blocks.append(lead)
        represented.update(str(row["slot_id"]) for row in members)
    if represented != {str(row["slot_id"]) for row in ordered}:
        raise RuntimeError("GDT583 renderer lost a complete slot")
    return "; ".join(blocks) + "."


def enrich_complete_rows(
    complete: list[dict[str, str]], assignments: dict[str, dict[str, object]]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in complete:
        assignment = assignments.get(source["slot_id"])
        if assignment is None:
            gloss = source["gdt582_concrete_default_de"]
            rule_id = "GDT582_RETAINED_NON_TARGET"
            sense = source["gdt582_core_concept"]
            tier = "NON_TARGET_RETAINED"
        else:
            gloss = assignment["gdt583_working_default_de"]
            rule_id = assignment["gdt583_rule_id"]
            sense = assignment["gdt583_concrete_sense_de"]
            tier = assignment["gdt583_reading_tier"]
        rows.append(
            {
                **source,
                "gdt583_rule_id": rule_id,
                "gdt583_working_default_de": gloss,
                "gdt583_concrete_sense_de": sense,
                "gdt583_reading_tier": tier,
                "gdt583_guard": (
                    "GDT582_COMPLETE_SLOT_RETAINED__ONLY_T_SH_CHD_S_GLOSS_MAY_CHANGE"
                ),
            }
        )
    return rows


def strip_traces(text: str) -> str:
    text = re.sub(r"\s*\[[^\]]+\]", "", text)
    text = text.replace("im Steuerrahmen: ", "")
    text = text.replace("im Besitzerrahmen: ", "")
    text = re.sub(r"\bim Rahmen:\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def editorial_paragraph(clauses: list[str]) -> str:
    """Make a readable paragraph without changing event order or verbs."""
    clean = [strip_traces(clause) for clause in clauses]
    sentences: list[str] = []
    for clause in clean:
        clause = clause.strip()
        if not clause:
            continue
        clause = clause.replace("; Arbeitsgang abschließen.", "; schließe den Arbeitsgang.")
        clause = clause.replace("danach / neuer Arbeitsgang", "beginne danach den nächsten Arbeitsgang")
        clause = clause.replace("weiter im selben Arbeitsgang", "fahre im selben Arbeitsgang fort")
        clause = re.sub(r";\s*;", ";", clause)
        sentences.append(clause)
    return " ".join(sentences)


def build_semantic_inventory(
    assignments: list[dict[str, object]],
) -> list[dict[str, object]]:
    desired = [
        ("temperieren", ("Temperiere auf den Grad", "Stelle ein oder temperiere"), "T"),
        ("erwärmen", ("Erwärme",), "T"),
        ("kühlen", ("Kühle ab",), "T"),
        ("trocknen", ("Trockne",), "T"),
        ("ziehen/einweichen", ("Lass den Auszug ziehen", "Weiche ein"), "SH"),
        ("baden/Badgang halten", ("Halte im Bad",), "SH"),
        ("ruhen lassen", ("Lass ruhen",), "SH"),
        ("zerreiben", ("Zerreibe",), "CHD"),
        ("bearbeiten", ("Bearbeite",), "CHD"),
        ("behandeln", ("Behandle",), "CHD"),
        ("berechnen", ("Berechne",), "CHD"),
        ("abseihen", ("Seihe ab",), "S"),
        ("sieben", ("Siebe",), "S"),
        ("abtrennen", ("Trenne ab", "Sondere aus"), "S"),
        ("umleiten", ("Leite um",), "S"),
        ("auswählen", ("Wähle aus", "Wähle die Station aus", "Wähle die Position aus"), "S"),
    ]
    counts = Counter(str(row["gdt583_working_default_de"]) for row in assignments)
    rows: list[dict[str, object]] = []
    for ordinal, (sense, glosses, root) in enumerate(desired, 1):
        count = sum(counts[gloss] for gloss in glosses)
        rows.append(
            {
                "inventory_ordinal": ordinal,
                "concrete_sense_de": sense,
                "candidate_root_slot": root,
                "assigned_occurrence_count": count,
                "assigned_working_glosses": pipe(glosses),
                "current_disposition": (
                    "PLACED_IN_GDT583" if count else "OPEN_DIRECTIONAL_SUBREADING"
                ),
                "working_note": (
                    "konkreter Kontextdefault vorhanden"
                    if count
                    else "kein unterscheidendes Richtungs- oder Zustandsmerkmal im aktuellen Slotmodell"
                ),
            }
        )
    return rows


def build_passage_book(rows: list[dict[str, object]]) -> str:
    lines = [
        "# GDT583 — twenty refined working passages",
        "",
        "These are exploratory German working readings, not recovered plaintext.",
        "Every paragraph preserves the GDT582 event order; the exact machine reading",
        "and slot-level rule assignments remain in the accompanying TSV artifacts.",
    ]
    for row in rows:
        lines.extend(
            [
                "",
                f"## {row['statement_id']} — {row['physical_page']} / {row['register']}",
                "",
                f"Surface: `{row['surface_sequence']}`",
                "",
                str(row["editorial_working_paragraph_de"]),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    complete = data["complete"]
    events = data["events"]
    statements = data["statements"]
    local_cards = data["local_cards"]
    source_passages = data["passages"]
    if tuple(map(len, (complete, events, statements, local_cards, source_passages))) != (
        15889, 5122, 793, 744, 20,
    ):
        raise RuntimeError("GDT582 input count drift")
    if any(
        row.get("physical_page", "").lower().startswith("f84")
        for table in data.values() for row in table
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT583")

    rule_rows = build_rule_rows()
    assignments, by_slot = build_assignments(complete)
    enriched = enrich_complete_rows(complete, by_slot)
    slots_by_host: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in enriched:
        slots_by_host[str(row["source_event_or_card_id"])].append(row)

    target_host_ids = {str(row["source_event_or_card_id"]) for row in assignments}
    event_by_id = {row["event_id"]: row for row in events}
    card_by_id = {row["source_event_id"]: row for row in local_cards}
    running_ids = target_host_ids.intersection(event_by_id)
    local_ids = target_host_ids.intersection(card_by_id)
    if len(running_ids) != 1623:
        raise RuntimeError(f"Affected running-event count drift: {len(running_ids)}")

    refined_events: list[dict[str, object]] = []
    refined_event_by_id: dict[str, dict[str, object]] = {}
    for source in events:
        event_id = source["event_id"]
        if event_id not in running_ids:
            continue
        members = slots_by_host[event_id]
        target_members = [row for row in members if row["slot_id"] in by_slot]
        row = {
            **source,
            "gdt583_target_slot_count": len(target_members),
            "gdt583_target_roots": pipe(str(member["slot_value"]) for member in target_members),
            "gdt583_rule_ids": pipe(str(member["gdt583_rule_id"]) for member in target_members),
            "gdt583_refined_slot_trace_de": render_trace(members),
            "gdt583_refined_working_clause_de": render_card(members, source["register"]),
            "gdt583_guard": (
                "GDT582_EVENT_AND_ALL_SLOT_HOSTS_RETAINED__TARGET_GLOSSES_ONLY_REFINED"
            ),
        }
        refined_events.append(row)
        refined_event_by_id[event_id] = row

    refined_cards: list[dict[str, object]] = []
    for source in local_cards:
        host_id = source["source_event_id"]
        if host_id not in local_ids:
            continue
        members = slots_by_host[host_id]
        target_members = [row for row in members if row["slot_id"] in by_slot]
        refined_cards.append(
            {
                **source,
                "gdt583_target_slot_count": len(target_members),
                "gdt583_target_roots": pipe(str(member["slot_value"]) for member in target_members),
                "gdt583_rule_ids": pipe(str(member["gdt583_rule_id"]) for member in target_members),
                "gdt583_refined_slot_trace_de": render_trace(members),
                "gdt583_refined_working_clause_de": render_card(members, source["register"]),
                "gdt583_guard": (
                    "GDT582_LOCAL_CARD_AND_ALL_SLOT_HOSTS_RETAINED__TARGET_GLOSSES_ONLY_REFINED"
                ),
            }
        )

    affected_statements: list[dict[str, object]] = []
    affected_statement_by_id: dict[str, dict[str, object]] = {}
    for source in statements:
        event_ids = source["event_ids"].split("|")
        affected = [event_id for event_id in event_ids if event_id in refined_event_by_id]
        if not affected:
            continue
        clauses = [
            str(refined_event_by_id[event_id]["gdt583_refined_working_clause_de"])
            if event_id in refined_event_by_id
            else str(event_by_id[event_id]["concrete_working_clause_de"])
            for event_id in event_ids
        ]
        row = {
            **source,
            "gdt583_affected_event_count": len(affected),
            "gdt583_affected_event_ids": "|".join(affected),
            "gdt583_refined_working_reading_de": " ".join(clauses),
            "gdt583_editorial_paragraph_de": editorial_paragraph(clauses),
            "gdt583_guard": (
                "FIXED_GDT582_EVENT_ORDER__UNAFFECTED_EVENTS_EXACT__TRACELESS_EDITORIAL_CHANNEL_SEPARATE"
            ),
        }
        affected_statements.append(row)
        affected_statement_by_id[source["statement_id"]] = row

    passage_rows: list[dict[str, object]] = []
    source_statement_by_id = {row["statement_id"]: row for row in statements}
    for source in source_passages:
        statement_id = source["statement_id"]
        if statement_id in affected_statement_by_id:
            refined = affected_statement_by_id[statement_id]
            exact = refined["gdt583_refined_working_reading_de"]
            paragraph = EDITORIAL_PARAGRAPHS.get(
                statement_id, str(refined["gdt583_editorial_paragraph_de"])
            )
            affected_count = refined["gdt583_affected_event_count"]
        else:
            base = source_statement_by_id[statement_id]
            exact = base["concrete_working_reading_de"]
            event_ids = base["event_ids"].split("|")
            paragraph = EDITORIAL_PARAGRAPHS.get(
                statement_id,
                editorial_paragraph(
                    [event_by_id[event_id]["concrete_working_clause_de"] for event_id in event_ids]
                ),
            )
            affected_count = 0
        passage_rows.append(
            {
                "passage_ordinal": len(passage_rows) + 1,
                "statement_id": statement_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_id": source["owner_id"],
                "event_count": source["event_count"],
                "affected_event_count": affected_count,
                "surface_sequence": source["surface_sequence"],
                "gdt582_concrete_reading_de": source["gdt582_concrete_reading_de"],
                "gdt583_exact_refined_reading_de": exact,
                "editorial_working_paragraph_de": paragraph,
                "editorial_status": "EVENT_ORDER_PRESERVED__TRACELESS_READER_CHANNEL",
                "guard": "FOUR_FIXED_PASSAGES_PER_REGISTER__NO_NEW_PAGE_OR_SURFACE",
            }
        )

    inventory_rows = build_semantic_inventory(assignments)
    rule_use = Counter(str(row["gdt583_rule_id"]) for row in assignments)
    unused_rules = sorted(row["rule_id"] for row in rule_rows if not rule_use[str(row["rule_id"])])
    result = {
        "experiment_id": "GDT583",
        "status": STATUS,
        "target_roots": list(TARGET_ROOTS),
        "target_slots": len(assignments),
        "target_slot_counts": dict(sorted(Counter(str(row["root"]) for row in assignments).items())),
        "rules": len(rule_rows),
        "used_rules": len(rule_use),
        "unused_rules": unused_rules,
        "lexically_refined_slots": sum(
            row["gdt583_change_status"] == "LEXICALLY_REFINED" for row in assignments
        ),
        "affected_running_events": len(refined_events),
        "affected_local_cards": len(refined_cards),
        "affected_statements": len(affected_statements),
        "passage_checks": len(passage_rows),
        "register_counts": dict(sorted(Counter(str(row["register"]) for row in assignments).items())),
        "reading_tier_counts": dict(sorted(Counter(str(row["gdt583_reading_tier"]) for row in assignments).items())),
        "working_gloss_counts": dict(sorted(Counter(str(row["gdt583_working_default_de"]) for row in assignments).items())),
        "open_directional_subreadings": [
            row["concrete_sense_de"] for row in inventory_rows
            if row["current_disposition"] == "OPEN_DIRECTIONAL_SUBREADING"
        ],
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt583_context_rule_deck.tsv", rule_rows)
    write_tsv(OUT / "gdt583_target_occurrence_assignments.tsv", assignments)
    write_tsv(OUT / "gdt583_refined_event_edition.tsv", refined_events)
    if refined_cards:
        write_tsv(OUT / "gdt583_refined_local_card_edition.tsv", refined_cards)
    write_tsv(OUT / "gdt583_affected_statement_edition.tsv", affected_statements)
    write_tsv(OUT / "gdt583_20_refined_passage_edition.tsv", passage_rows)
    write_tsv(OUT / "gdt583_semantic_inventory.tsv", inventory_rows)
    (OUT / "GDT583_REFINED_PASSAGES.md").write_text(
        build_passage_book(passage_rows), encoding="utf-8"
    )
    (OUT / "gdt583_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
