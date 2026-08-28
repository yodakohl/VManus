#!/usr/bin/env python3
"""Build GDT587: action-conditioned carrier nouns and complete reader."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish"
G585 = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas/artifacts"
G586 = ROOT / "experiments/yolo/gdt586_complete_name_layer_reader/artifacts"

INPUTS = {
    "complete_defaults": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "statements_582": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards_582": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "action_revisions_584": G584 / "artifacts/gdt584_target_occurrence_revisions.tsv",
    "hosts_584": G584 / "artifacts/gdt584_statement_wide_host_phrases.tsv",
    "statements_584": G584 / "artifacts/gdt584_591_polished_statement_edition.tsv",
    "local_cards_584": G584 / "artifacts/gdt584_158_polished_local_card_edition.tsv",
    "name_assignments_585": G585 / "gdt585_109_owner_content_slot_assignments.tsv",
    "name_labels_585": G585 / "gdt585_89_concrete_name_label_edition.tsv",
    "statements_586": G586 / "gdt586_793_complete_statement_reader.tsv",
    "local_cards_586": G586 / "gdt586_744_complete_local_card_reader.tsv",
}

OUTPUTS = {
    "assignments": OUT / "gdt587_1243_action_conditioned_carrier_assignments.tsv",
    "cells": OUT / "gdt587_136_observed_action_root_cells.tsv",
    "hosts": OUT / "gdt587_candidate_statement_host_phrases.tsv",
    "candidate_statements": OUT / "gdt587_379_candidate_statement_edition.tsv",
    "candidate_local": OUT / "gdt587_70_candidate_local_card_edition.tsv",
    "statements": OUT / "gdt587_793_complete_statement_reader.tsv",
    "local_cards": OUT / "gdt587_744_complete_local_card_reader.tsv",
    "pages": OUT / "gdt587_30_page_reader_profiles.tsv",
    "manual": OUT / "gdt587_25_manual_passage_audit.tsv",
    "book": OUT / "GDT587_COMPLETE_THIRTY_PAGE_READER.md",
    "manual_book": OUT / "GDT587_MANUAL_PASSAGE_AUDIT.md",
    "result": OUT / "gdt587_result.json",
}

STATUS = (
    "PASS_1243_ACTION_CONDITIONED_CARRIERS__953_EXACT_ACTION_HOSTS__"
    "136_OBSERVED_ACTION_ROOT_CELLS__793_STATEMENTS__744_LOCAL_CARDS__"
    "ZERO_GLOBAL_ROOT_CHANGE"
)

PORTABLE_CORE = {"Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
OBJECT_ROOTS = ("Y", "AIIN", "AIN", "OR")
ROOT_ORDER = {root: ordinal for ordinal, root in enumerate(OBJECT_ROOTS)}

AUDIT_IDS = (
    "G407-S003", "G515-S037", "G515-S048", "G515-S059",
    "G407-S696", "G407-S689", "G407-S688", "G407-S699",
    "G407-S047", "G407-S045", "G407-S058", "G407-S061",
    "G407-S151", "G407-S440", "G407-S621", "G407-S384",
    "G407-S663", "G407-S664", "G407-S667", "G407-S666",
    "G407-S572", "G407-S115", "G407-S526", "G407-S001", "G407-S653",
)

AUDIT_NOTES = {
    "G407-S003": "Source packet: Teilmenge belongs to working material; liquid is sorted separately.",
    "G407-S047": "Celestial packet: position, ring segment and position value are no longer equal objects.",
    "G407-S440": "Biological diversion: amount and basin content compose as one flow packet.",
    "G407-S621": "Exact CHD plus Y+AIN packet: body plus part composes to Körperteil.",
    "G407-S667": "Pharma wet sequence keeps material, extract and ingredient portion distinct.",
    "G407-S696": "Drying and grinding come from verbs; Y remains plain plant material.",
    "G407-S689": "Negative control: held OR is a plant unit, not automatically extract or vessel.",
    "G407-S572": "Negative control: mixed biological packet retains Stationsansatz instead of forcing Körper.",
    "G407-S115": "Negative control: relation-rich mixed host retains station noun rather than body.",
    "G407-S526": "Negative control: a biological list narrows only under an exact packet rule.",
    "G407-S001": "Source AIIN becomes working liquid only under rest/sort; T keeps quantity.",
    "G407-S653": "Boundary case: pharmaceutical OR under sieving remains medicinal batch.",
}

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nouns import (  # noqa: E402
    BASE_LEMMA,
    carrier_root_set,
    choose_noun,
    packet_rule_id,
    patch_polish,
)


def load_polish() -> Any:
    path = G584 / "src/polish.py"
    spec = importlib.util.spec_from_file_location("gdt584_polish_for_gdt587", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT584 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return patch_polish(module)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pipe(values: Iterable[str]) -> str:
    items = list(dict.fromkeys(value for value in values if value and value != "NONE"))
    return "|".join(items) if items else "NONE"


def exact_trace(rows: list[dict[str, str]]) -> str:
    ordered = sorted(
        rows,
        key=lambda row: (
            int(row.get("statement_event_ordinal", "1")), int(row["slot_position"]), row["slot_id"],
        ),
    )
    return " ".join(
        f"[{row['slot_id']}={row['slot_value']}:{row['gdt587_trace_default_de']}|{row['primary_governor_key']}]"
        for row in ordered
    )


def action_map(revisions: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revisions:
        grouped[row["primary_governor_key"]].append(row)
    if any(len(rows) != 1 for rows in grouped.values()):
        collisions = {key: len(rows) for key, rows in grouped.items() if len(rows) != 1}
        raise RuntimeError(f"Target action governor collision: {collisions}")
    return {key: rows[0] for key, rows in grouped.items()}


def build_assignments(
    complete: list[dict[str, str]], actions: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    candidates = [
        row for row in complete
        if row["slot_value"] in OBJECT_ROOTS and row["primary_governor_key"] in actions
    ]
    by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_host[row["primary_governor_key"]].append(row)
    all_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete:
        if row["primary_governor_key"] in actions:
            all_by_host[row["primary_governor_key"]].append(row)
    output: list[dict[str, Any]] = []
    for source in candidates:
        key = source["primary_governor_key"]
        action = actions[key]
        roots = carrier_root_set(by_host[key])
        host_values = frozenset(row["slot_value"] for row in all_by_host[key])
        selection = choose_noun(
            source["register"], action["gdt584_rule_id"], source["slot_value"], roots, host_values
        )
        output.append(
            {
                "assignment_ordinal": len(output) + 1,
                "carrier_slot_id": source["slot_id"],
                "action_slot_id": action["slot_id"],
                "layer": source["layer"],
                "source_event_or_card_id": source["source_event_or_card_id"],
                "statement_or_record_id": source["statement_or_record_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner": source["owner"],
                "surface": source["surface"],
                "slot_position": source["slot_position"],
                "carrier_root": source["slot_value"],
                "portable_carrier_core": PORTABLE_CORE[source["slot_value"]],
                "primary_governor_key": key,
                "action_root": action["root"],
                "gdt584_rule_id": action["gdt584_rule_id"],
                "carrier_root_signature": "+".join(sorted(roots, key=ROOT_ORDER.__getitem__)),
                "same_root_written_slot_count": sum(row["slot_value"] == source["slot_value"] for row in by_host[key]),
                "gdt582_default_de": source["gdt582_concrete_default_de"],
                "gdt584_base_lemma_de": BASE_LEMMA[source["register"]][source["slot_value"]],
                **selection,
                "gdt587_packet_rule_id": packet_rule_id(source["register"], action["gdt584_rule_id"], roots),
                "circularity_note": "EDITORIAL_ACTION_CONDITIONED_READING__NOT_INDEPENDENT_ROOT_CONFIRMATION",
                "guard": (
                    "EXACT_CARRIER_SLOT_AND_ACTION_GOVERNOR__PORTABLE_ROOT_UNCHANGED__"
                    "NO_NEW_PAGE_SURFACE_SEGMENT_OR_NAME"
                ),
            }
        )
    return output


def build_cells(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in assignments:
        grouped[(str(row["register"]), str(row["gdt584_rule_id"]), str(row["carrier_root"]))].append(row)
    output: list[dict[str, Any]] = []
    for key in sorted(grouped, key=lambda item: (item[0], item[1], ROOT_ORDER[item[2]])):
        register, rule, root = key
        members = grouped[key]
        output.append(
            {
                "cell_ordinal": len(output) + 1,
                "register": register,
                "gdt584_rule_id": rule,
                "carrier_root": root,
                "portable_carrier_core": PORTABLE_CORE[root],
                "written_slot_count": len(members),
                "exact_action_host_count": len({row["primary_governor_key"] for row in members}),
                "statement_or_record_count": len({row["statement_or_record_id"] for row in members}),
                "layer_profile": pipe(str(row["layer"]) for row in members),
                "carrier_root_signatures": pipe(str(row["carrier_root_signature"]) for row in members),
                "selected_context_families": pipe(str(row["gdt587_context_family"]) for row in members),
                "selected_lemmas_de": pipe(str(row["gdt587_lemma_de"]) for row in members),
                "selected_object_forms_de": pipe(str(row["gdt587_object_form_de"]) for row in members),
                "dispositions": pipe(str(row["gdt587_disposition"]) for row in members),
                "example_carrier_slot_ids": "|".join(str(row["carrier_slot_id"]) for row in members[:8]),
                "guard": "OBSERVED_REGISTER_RULE_ROOT_CELL_ONLY__NO_UNOBSERVED_MATRIX_COMPLETION",
            }
        )
    return output


def enrich_complete(
    complete: list[dict[str, str]],
    actions: dict[str, dict[str, str]],
    assignments: list[dict[str, Any]],
    name_assignments: list[dict[str, str]],
    polish: Any,
) -> list[dict[str, str]]:
    carrier = {str(row["carrier_slot_id"]): row for row in assignments}
    names = {row["slot_id"]: row for row in name_assignments}
    output: list[dict[str, str]] = []
    for source in complete:
        action = actions.get(source["primary_governor_key"])
        action_here = action if action and action["slot_id"] == source["slot_id"] else None
        default = action_here["gdt584_working_default_de"] if action_here else source["gdt582_concrete_default_de"]
        rule = action_here["gdt584_rule_id"] if action_here else "GDT582_RETAINED_NON_TARGET"
        if source["slot_id"] in names:
            default = names[source["slot_id"]]["gdt585_primary_default_de"]
        assignment = carrier.get(source["slot_id"])
        if assignment:
            lemma = str(assignment["gdt587_lemma_de"])
            obj = str(assignment["gdt587_object_form_de"])
            genitive = str(assignment["gdt587_genitive_form_de"])
            trace_default = lemma
        elif source["slot_value"] in OBJECT_ROOTS:
            register = source["register"]
            root = source["slot_value"]
            lemma = BASE_LEMMA[register][root]
            obj = polish.OBJECT_FORMS[register][root]
            genitive = polish.GENITIVE_FORMS.get(register, {}).get(root, "NOT_USED")
            trace_default = default
        else:
            lemma = obj = genitive = "NOT_APPLICABLE"
            trace_default = default
        output.append(
            {
                **source,
                "gdt584_rule_id": rule,
                "gdt584_default_de": default,
                "gdt587_lemma_de": lemma,
                "gdt587_object_form_de": obj,
                "gdt587_genitive_form_de": genitive,
                "gdt587_trace_default_de": trace_default,
            }
        )
    return output


def build_group_rows(
    statement: dict[str, str],
    event_ids: list[str],
    slots_by_event: dict[str, list[dict[str, str]]],
    carrier_by_slot: dict[str, dict[str, Any]],
    old_hosts: dict[tuple[str, str], dict[str, str]],
    polish: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    event_order = {event_id: ordinal for ordinal, event_id in enumerate(event_ids, 1)}
    members = [
        {**row, "statement_event_ordinal": str(event_order[event_id])}
        for event_id in event_ids for row in slots_by_event[event_id]
    ]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in members:
        grouped[row["primary_governor_key"]].append(row)
    ordered_groups = sorted(
        grouped.items(),
        key=lambda item: min(
            (int(row["statement_event_ordinal"]), int(row["slot_position"]), row["slot_id"])
            for row in item[1]
        ),
    )
    output: list[dict[str, Any]] = []
    for ordinal, (key, rows) in enumerate(ordered_groups, 1):
        phrase, meta = polish.render_group(rows, statement["register"])
        candidate_rows = [row for row in rows if row["slot_id"] in carrier_by_slot]
        roots = carrier_root_set(candidate_rows)
        old = old_hosts.get((statement["statement_id"], key))
        new_clause = polish.sentence_case(phrase)
        output.append(
            {
                "host_ordinal_global": 0,
                "statement_id": statement["statement_id"],
                "host_ordinal_in_statement": ordinal,
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "owner_id": statement["owner_id"],
                "primary_governor_key": key,
                "anchor_event_id": meta["anchor_event_id"],
                "packet_event_ids": meta["packet_event_ids"],
                "packet_count": meta["packet_count"],
                "action_root": meta["action_root"],
                "action_slot_id": meta["action_slot_id"],
                "gdt584_rule_id": meta["rule_id"],
                "written_slot_count": meta["slot_count"],
                "carrier_slot_count": len(candidate_rows),
                "carrier_roots": pipe(row["slot_value"] for row in candidate_rows),
                "carrier_slot_ids": pipe(row["slot_id"] for row in candidate_rows),
                "gdt587_packet_rule_id": packet_rule_id(statement["register"], str(meta["rule_id"]), roots),
                "paragraph_boundary": meta["boundary"],
                "gdt584_reader_clause_de": old["gdt584_reader_clause_de"] if old else "NOT_IN_GDT584_RUNNING_HOST_TABLE",
                "gdt587_reader_clause_de": new_clause,
                "reader_clause_changed": "YES" if old and old["gdt584_reader_clause_de"] != new_clause else "NO",
                "written_packet_slot_ids": "|".join(
                    row["slot_id"] for row in sorted(
                        rows,
                        key=lambda item: (
                            int(item["statement_event_ordinal"]), int(item["slot_position"]), item["slot_id"],
                        ),
                    )
                ),
                "gdt587_exact_host_trace_de": exact_trace(rows),
                "guard": "FIXED_GDT584_GOVERNOR_PACKET__OCCURRENCE_NOUN_AND_PACKET_READER_ONLY",
            }
        )
    warm_events = {
        str(row["anchor_event_id"]) for row in output
        if row["gdt584_rule_id"] == "T_HP_BEFORE_SH_WARM"
    }
    for row in output:
        if row["action_root"] != "SH" or str(row["anchor_event_id"]) not in warm_events:
            continue
        phrase = str(row["gdt587_reader_clause_de"])
        if phrase.endswith(" ziehen"):
            phrase = phrase[:-7] + " warm ziehen"
        elif phrase.startswith("Halte den Zustand"):
            phrase = "Halte anschließend" + phrase[len("Halte den Zustand"):] + " warm"
        elif phrase.startswith("Halte "):
            phrase += " warm"
        row["gdt587_reader_clause_de"] = phrase
        row["reader_clause_changed"] = "YES" if str(row["gdt584_reader_clause_de"]) != phrase else "NO"
    return output, members


def compose_paragraph(groups: list[dict[str, Any]], polish: Any) -> tuple[str, int]:
    compatible = [
        {
            "gdt584_reader_clause_de": str(row["gdt587_reader_clause_de"]),
            "paragraph_boundary": str(row["paragraph_boundary"]),
        }
        for row in groups
    ]
    return polish.compose_paragraph(compatible)


def build_local_clause(
    card: dict[str, str], rows: list[dict[str, str]], polish: Any
) -> tuple[str, str, int]:
    enriched = [{**row, "statement_event_ordinal": "1"} for row in rows]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    first: dict[str, tuple[int, str]] = {}
    for row in enriched:
        key = row["primary_governor_key"]
        grouped[key].append(row)
        position = (int(row["slot_position"]), row["slot_id"])
        first[key] = min(first.get(key, position), position)
    clauses: list[str] = []
    for key in sorted(grouped, key=lambda value: (first[value], value)):
        phrase, _ = polish.render_group(grouped[key], card["register"])
        clauses.append(polish.sentence_case(phrase) + ".")
    return " ".join(clauses), exact_trace(enriched), len(grouped)


def named_carrier_composition(
    event_id: str,
    label: dict[str, str],
    name_assignment: dict[str, str],
    carrier_assignment: dict[str, Any],
) -> str:
    if event_id != "P1003-E0414" or label["source_event_id"] != event_id:
        raise RuntimeError(f"Unexpected name/carrier overlap: {event_id}")
    name = f"{name_assignment['gdt585_primary_default_de']} [{name_assignment['raw_name_core']}]"
    carrier = str(carrier_assignment["gdt587_object_form_de"])
    return (
        f"Nimm den Drogeneintrag »{name}« und {carrier} und stelle den Drogeneintrag "
        f"»{name}« und {carrier} ein."
    )


def build_book(statements: list[dict[str, Any]], local: list[dict[str, Any]]) -> str:
    page_order: list[str] = []
    for row in [*statements, *local]:
        page = str(row["physical_page"])
        if page not in page_order:
            page_order.append(page)
    by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_local: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in statements:
        by_statement[str(row["physical_page"])].append(row)
    for row in local:
        by_local[str(row["physical_page"])].append(row)
    lines = [
        "# GDT587 — vollständiger 30-Seiten-Arbeitsleser", "",
        "Explorative deutsche Leserschicht; kein rekonstruierter Klartext.",
        "Trägerstämme bleiben POSTEN/WERT/ANTEIL/EINHEIT; konkrete Nomen gelten nur am exakten Handlungshost.",
    ]
    for page in page_order:
        lines.extend(["", f"## {page}", "", "### Laufende Aussagen", ""])
        if not by_statement[page]:
            lines.append("Keine laufende Aussage auf dieser Seite.")
        for row in by_statement[page]:
            lines.extend(
                [
                    f"#### {row['statement_id']} — {row['register']}", "",
                    f"Surface: `{row['surface_sequence']}`", "",
                    str(row["gdt587_primary_reader_de"]), "",
                ]
            )
        lines.extend(["### Lokale Karten", ""])
        if not by_local[page]:
            lines.append("Keine lokale Karte auf dieser Seite.")
        for row in by_local[page]:
            lines.extend(
                [
                    f"#### {row['source_event_id']} — {row['locus']}", "",
                    f"Surface: `{row['surface']}`", "",
                    str(row["gdt587_primary_reader_de"]), "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def build_manual_book(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# GDT587 — manuelle Passagenprüfung", "",
        "Zwanzig Registerpassagen plus fünf Belastungsfälle; keine neue Seite wurde geöffnet.",
    ]
    for row in rows:
        lines.extend(
            [
                "", f"## {row['statement_id']} — {row['physical_page']} / {row['register']}", "",
                f"Befund: {row['manual_note']}", "", "Vorher:", "",
                str(row["gdt586_reader_de"]), "", "Nachher:", "", str(row["gdt587_reader_de"]),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected = {
        "complete_defaults": 15889, "statements_582": 793, "local_cards_582": 744,
        "action_revisions_584": 1921, "hosts_584": 6289, "statements_584": 591,
        "local_cards_584": 158, "name_assignments_585": 109, "name_labels_585": 89,
        "statements_586": 793, "local_cards_586": 744,
    }
    observed = {name: len(rows) for name, rows in data.items()}
    if observed != expected:
        raise RuntimeError(f"Input count drift: {observed}")
    if any(
        row.get("physical_page", "").lower().startswith("f84")
        for rows in data.values() for row in rows
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT587")

    polish = load_polish()
    actions = action_map(data["action_revisions_584"])
    assignments = build_assignments(data["complete_defaults"], actions)
    if len(assignments) != 1243:
        raise RuntimeError(f"Candidate population drift: {len(assignments)}")
    cells = build_cells(assignments)
    if len(cells) != 136:
        raise RuntimeError(f"Observed action-root cell drift: {len(cells)}")
    enriched = enrich_complete(
        data["complete_defaults"], actions, assignments, data["name_assignments_585"], polish
    )
    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in enriched:
        slots_by_event[row["source_event_or_card_id"]].append(row)
    carrier_by_slot = {str(row["carrier_slot_id"]): row for row in assignments}
    old_hosts = {
        (row["statement_id"], row["primary_governor_key"]): row for row in data["hosts_584"]
    }
    old_statements = {row["statement_id"]: row for row in data["statements_584"]}
    old_local = {row["source_event_id"]: row for row in data["local_cards_584"]}

    candidate_statement_ids = {
        str(row["statement_or_record_id"]) for row in assignments if row["layer"] == "RUNNING_ATOM"
    }
    candidate_local_ids = {
        str(row["source_event_or_card_id"]) for row in assignments if row["layer"] == "LOCAL_COMPONENT"
    }
    if len(candidate_statement_ids) != 379 or len(candidate_local_ids) != 70:
        raise RuntimeError(
            f"Candidate unit drift: {len(candidate_statement_ids)} statements, {len(candidate_local_ids)} cards"
        )

    host_rows: list[dict[str, Any]] = []
    candidate_statement_rows: list[dict[str, Any]] = []
    candidate_statement_by_id: dict[str, dict[str, Any]] = {}
    assignments_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    assignments_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assignments:
        assignments_by_statement[str(row["statement_or_record_id"])].append(row)
        assignments_by_event[str(row["source_event_or_card_id"])].append(row)

    for source in data["statements_582"]:
        statement_id = source["statement_id"]
        if statement_id not in candidate_statement_ids:
            continue
        groups, members = build_group_rows(
            source, source["event_ids"].split("|"), slots_by_event, carrier_by_slot, old_hosts, polish
        )
        for group in groups:
            group["host_ordinal_global"] = len(host_rows) + 1
            host_rows.append(group)
        paragraph, paragraph_count = compose_paragraph(groups, polish)
        old = old_statements[statement_id]
        carrier_rows = assignments_by_statement[statement_id]
        changed_groups = [row for row in groups if row["reader_clause_changed"] == "YES"]
        row = {
            "candidate_statement_ordinal": len(candidate_statement_rows) + 1,
            "statement_id": statement_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "complete_slot_count": len(members),
            "carrier_assignment_count": len(carrier_rows),
            "carrier_action_host_count": len({item["primary_governor_key"] for item in carrier_rows}),
            "carrier_slot_ids": pipe(str(item["carrier_slot_id"]) for item in carrier_rows),
            "changed_host_clause_count": len(changed_groups),
            "paragraph_count": paragraph_count,
            "gdt584_polished_paragraph_de": old["gdt584_polished_paragraph_de"],
            "gdt587_action_noun_paragraph_de": paragraph,
            "reader_changed": "YES" if old["gdt584_polished_paragraph_de"] != paragraph else "NO",
            "gdt587_exact_slot_trace_de": exact_trace(members),
            "guard": "FIXED_STATEMENT_EVENT_ORDER_AND_GOVERNORS__ACTION_NOUN_READER_ONLY",
        }
        candidate_statement_rows.append(row)
        candidate_statement_by_id[statement_id] = row

    candidate_local_rows: list[dict[str, Any]] = []
    candidate_local_by_id: dict[str, dict[str, Any]] = {}
    label_by_event = {row["source_event_id"]: row for row in data["name_labels_585"]}
    name_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["name_assignments_585"]:
        name_by_event[row["source_event_or_card_id"]].append(row)
    for source in data["local_cards_582"]:
        event_id = source["source_event_id"]
        if event_id not in candidate_local_ids:
            continue
        members = slots_by_event[event_id]
        paragraph, trace, group_count = build_local_clause(source, members, polish)
        carrier_rows = assignments_by_event[event_id]
        old = old_local[event_id]
        named_primary = "NOT_APPLICABLE"
        if event_id in label_by_event:
            if len(name_by_event[event_id]) != 1 or len(carrier_rows) != 1:
                raise RuntimeError(f"Unexpected named carrier overlap shape: {event_id}")
            named_primary = named_carrier_composition(
                event_id, label_by_event[event_id], name_by_event[event_id][0], carrier_rows[0]
            )
        row = {
            "candidate_local_card_ordinal": len(candidate_local_rows) + 1,
            "source_event_id": event_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "locus": source["locus"],
            "record_id": source["record_id"],
            "owner_de": source["owner_de"],
            "surface": source["surface"],
            "complete_slot_count": len(members),
            "carrier_assignment_count": len(carrier_rows),
            "carrier_action_host_count": len({item["primary_governor_key"] for item in carrier_rows}),
            "carrier_slot_ids": pipe(str(item["carrier_slot_id"]) for item in carrier_rows),
            "host_count": group_count,
            "gdt584_polished_local_clause_de": old["gdt584_polished_local_clause_de"],
            "gdt587_action_noun_local_clause_de": paragraph,
            "gdt587_named_carrier_primary_de": named_primary,
            "reader_changed": "YES" if old["gdt584_polished_local_clause_de"] != paragraph else "NO",
            "gdt587_exact_slot_trace_de": trace,
            "guard": "FIXED_LOCAL_CARD_OWNER_RECORD_AND_HOSTS__NAME_AND_CARRIER_SLOTS_DISTINCT",
        }
        candidate_local_rows.append(row)
        candidate_local_by_id[event_id] = row

    complete_statement_rows: list[dict[str, Any]] = []
    for source in data["statements_586"]:
        statement_id = source["statement_id"]
        candidate = candidate_statement_by_id.get(statement_id)
        primary = candidate["gdt587_action_noun_paragraph_de"] if candidate else source["gdt586_primary_reader_de"]
        carrier_rows = assignments_by_statement.get(statement_id, []) if candidate else []
        complete_statement_rows.append(
            {
                **source,
                "gdt587_carrier_assignment_count": len(carrier_rows),
                "gdt587_carrier_slot_ids": pipe(str(row["carrier_slot_id"]) for row in carrier_rows),
                "gdt587_base_reader_de": source["gdt586_primary_reader_de"],
                "gdt587_primary_reader_de": primary,
                "gdt587_reader_changed": "YES" if primary != source["gdt586_primary_reader_de"] else "NO",
                "gdt587_layer_status": "ACTION_NOUN_RERENDER" if candidate else "GDT586_BYTE_RETAINED",
                "gdt587_guard": "FIXED_793_STATEMENTS__ONLY_EXACT_CANDIDATE_GOVERNORS_RERENDERED",
            }
        )

    complete_local_rows: list[dict[str, Any]] = []
    for source in data["local_cards_586"]:
        event_id = source["source_event_id"]
        candidate = candidate_local_by_id.get(event_id)
        if candidate:
            primary = (
                candidate["gdt587_named_carrier_primary_de"]
                if candidate["gdt587_named_carrier_primary_de"] != "NOT_APPLICABLE"
                else candidate["gdt587_action_noun_local_clause_de"]
            )
            carrier_rows = assignments_by_event[event_id]
        else:
            primary = source["gdt586_primary_reader_de"]
            carrier_rows = []
        complete_local_rows.append(
            {
                **source,
                "gdt587_carrier_assignment_count": len(carrier_rows),
                "gdt587_carrier_slot_ids": pipe(str(row["carrier_slot_id"]) for row in carrier_rows),
                "gdt587_base_reader_de": source["gdt586_primary_reader_de"],
                "gdt587_primary_reader_de": primary,
                "gdt587_reader_changed": "YES" if primary != source["gdt586_primary_reader_de"] else "NO",
                "gdt587_layer_status": (
                    "NAMED_CARRIER_COMPOSITION" if event_id == "P1003-E0414"
                    else "ACTION_NOUN_RERENDER" if candidate else "GDT586_BYTE_RETAINED"
                ),
                "gdt587_guard": "FIXED_744_LOCAL_CARDS__LOCAL_OWNER_BOUNDARY_RETAINED",
            }
        )

    statements_by_id = {row["statement_id"]: row for row in complete_statement_rows}
    manual_rows: list[dict[str, Any]] = []
    for statement_id in AUDIT_IDS:
        row = statements_by_id[statement_id]
        manual_rows.append(
            {
                "audit_ordinal": len(manual_rows) + 1,
                "statement_id": statement_id,
                "physical_page": row["physical_page"],
                "register": row["register"],
                "carrier_assignment_count": row["gdt587_carrier_assignment_count"],
                "reader_changed": row["gdt587_reader_changed"],
                "manual_note": AUDIT_NOTES.get(
                    statement_id,
                    "Register sample read for noun distinction, packet coherence, and retained action.",
                ),
                "gdt586_reader_de": row["gdt587_base_reader_de"],
                "gdt587_reader_de": row["gdt587_primary_reader_de"],
                "manual_disposition": "KEEP_AS_CURRENT_EXPLORATORY_READING",
                "guard": "MANUALLY_SELECTED_EXISTING_STATEMENT__NO_NEW_PAGE_OR_SLOT",
            }
        )

    page_order: list[str] = []
    for row in [*complete_statement_rows, *complete_local_rows]:
        page = str(row["physical_page"])
        if page not in page_order:
            page_order.append(page)
    page_rows: list[dict[str, Any]] = []
    for page in page_order:
        ss = [row for row in complete_statement_rows if row["physical_page"] == page]
        ll = [row for row in complete_local_rows if row["physical_page"] == page]
        aa = [row for row in assignments if row["physical_page"] == page]
        page_rows.append(
            {
                "page_ordinal": len(page_rows) + 1,
                "physical_page": page,
                "registers": pipe(str(row["register"]) for row in [*ss, *ll]),
                "statement_count": len(ss),
                "local_card_count": len(ll),
                "carrier_assignment_count": len(aa),
                "carrier_action_host_count": len({row["primary_governor_key"] for row in aa}),
                "changed_statement_count": sum(row["gdt587_reader_changed"] == "YES" for row in ss),
                "changed_local_card_count": sum(row["gdt587_reader_changed"] == "YES" for row in ll),
                "guard": "NAVIGATION_PROFILE_ONLY__RUNNING_AND_LOCAL_UNITS_REMAIN_DISTINCT",
            }
        )

    result = {
        "experiment_id": "GDT587",
        "status": STATUS,
        "candidate_carrier_slots": len(assignments),
        "candidate_action_hosts": len({row["primary_governor_key"] for row in assignments}),
        "observed_action_root_cells": len(cells),
        "root_counts": dict(sorted(Counter(str(row["carrier_root"]) for row in assignments).items())),
        "register_counts": dict(sorted(Counter(str(row["register"]) for row in assignments).items())),
        "layer_counts": dict(sorted(Counter(str(row["layer"]) for row in assignments).items())),
        "disposition_counts": dict(sorted(Counter(str(row["gdt587_disposition"]) for row in assignments).items())),
        "context_family_counts": dict(sorted(Counter(str(row["gdt587_context_family"]) for row in assignments).items())),
        "packet_rule_slot_counts": dict(sorted(Counter(str(row["gdt587_packet_rule_id"]) for row in assignments).items())),
        "candidate_statements": len(candidate_statement_rows),
        "candidate_local_cards": len(candidate_local_rows),
        "changed_candidate_statements": sum(row["reader_changed"] == "YES" for row in candidate_statement_rows),
        "changed_candidate_local_cards": sum(row["reader_changed"] == "YES" for row in candidate_local_rows),
        "complete_statements": len(complete_statement_rows),
        "complete_local_cards": len(complete_local_rows),
        "changed_complete_statements": sum(row["gdt587_reader_changed"] == "YES" for row in complete_statement_rows),
        "changed_complete_local_cards": sum(row["gdt587_reader_changed"] == "YES" for row in complete_local_rows),
        "candidate_statement_hosts_rendered": len(host_rows),
        "changed_host_clauses": sum(row["reader_clause_changed"] == "YES" for row in host_rows),
        "manual_passages": len(manual_rows),
        "physical_pages": len(page_rows),
        "exact_name_slot_overlap": len(
            {str(row["carrier_slot_id"]) for row in assignments}
            & {row["slot_id"] for row in data["name_assignments_585"]}
        ),
        "shared_named_local_card": "P1003-E0414",
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUTPUTS["assignments"], assignments)
    write_tsv(OUTPUTS["cells"], cells)
    write_tsv(OUTPUTS["hosts"], host_rows)
    write_tsv(OUTPUTS["candidate_statements"], candidate_statement_rows)
    write_tsv(OUTPUTS["candidate_local"], candidate_local_rows)
    write_tsv(OUTPUTS["statements"], complete_statement_rows)
    write_tsv(OUTPUTS["local_cards"], complete_local_rows)
    write_tsv(OUTPUTS["pages"], page_rows)
    write_tsv(OUTPUTS["manual"], manual_rows)
    OUTPUTS["book"].write_text(build_book(complete_statement_rows, complete_local_rows), encoding="utf-8")
    OUTPUTS["manual_book"].write_text(build_manual_book(manual_rows), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
