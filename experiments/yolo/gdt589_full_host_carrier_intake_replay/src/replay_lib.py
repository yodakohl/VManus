#!/usr/bin/env python3
"""Complete-host reconstruction and replay helpers for GDT589."""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
G587 = ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts"
G588 = ROOT / "experiments/yolo/gdt588_carrier_transfer_readiness_deck"

sys.path.insert(0, str(G588 / "src"))
from transfer_lib import (  # noqa: E402
    NOUNS,
    PACKET_CARD_DESCRIPTIONS,
    PORTABLE_CORE,
    ROOT_ORDER,
    future_host_reading,
    root_multiset,
)


INPUTS = {
    "complete_582": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "actions_584": G584 / "gdt584_target_occurrence_revisions.tsv",
    "assignments_587": G587 / "gdt587_1243_action_conditioned_carrier_assignments.tsv",
    "hosts_587": G587 / "gdt587_candidate_statement_host_phrases.tsv",
    "statements_588": G588 / "artifacts/gdt588_793_count_safe_statement_reader.tsv",
    "local_cards_588": G588 / "artifacts/gdt588_744_count_safe_local_card_reader.tsv",
    "rule_gate_588": G588 / "artifacts/gdt588_38_action_rule_gate.tsv",
    "repairs_588": G588 / "artifacts/gdt588_13_multiplicity_safe_packet_repairs.tsv",
}

OUTPUTS = {
    "hosts": OUT / "gdt589_953_complete_host_replay.tsv",
    "slots": OUT / "gdt589_1243_slot_replay.tsv",
    "manual": OUT / "gdt589_41_manual_override_replay.tsv",
    "source_bound": OUT / "gdt589_2_source_bound_fallthrough.tsv",
    "special_packets": OUT / "gdt589_74_special_packet_replay.tsv",
    "repeated": OUT / "gdt589_117_repeated_root_host_replay.tsv",
    "body_guard": OUT / "gdt589_361_biological_y_host_guard.tsv",
    "bath_forks": OUT / "gdt589_4_clean_bath_body_forks.tsv",
    "pages": OUT / "gdt589_30_page_replay_profile.tsv",
    "statements": OUT / "gdt589_793_count_overlay_statement_reader.tsv",
    "local_cards": OUT / "gdt589_744_count_overlay_local_card_reader.tsv",
    "deck": OUT / "GDT589_FULL_HOST_REPLAY_DECK.md",
    "book": OUT / "GDT589_COUNT_SAFE_THIRTY_PAGE_READER.md",
    "result": OUT / "gdt589_result.json",
    "validation": OUT / "gdt589_validation.json",
}

STATUS = (
    "PASS_953_COMPLETE_HOST_REPLAY__910_AUTO_EXACT__41_MANUAL_VISIBLE__"
    "2_SOURCE_FALLTHROUGH_EXACT__117_REPEAT_HOST_OVERLAY"
)

DEFAULT_PACKET = "DEFAULT_GDT584_OBJECT_COMPOSITION"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
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
    chosen = [value for value in values if value and value != "NONE"]
    return "|".join(chosen) if chosen else "NONE"


def split_pipe(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {name: read_tsv(path) for name, path in INPUTS.items()}


def unique_action_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["primary_governor_key"]].append(row)
    collisions = {key: len(members) for key, members in grouped.items() if len(members) != 1}
    if collisions:
        raise RuntimeError(f"Action-governor collisions: {collisions}")
    return {key: members[0] for key, members in grouped.items()}


def ordered_assignments(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: int(row["assignment_ordinal"]))


def ordered_complete(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: int(row["complete_slot_ordinal"]))


def noun_sequence(rows: list[dict[str, str]], field: str) -> str:
    return pipe(row[field] for row in rows)


def written_count_trace(rows: list[dict[str, str]], lemma_field: str) -> str:
    by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_root[row["carrier_root"]].append(row)
    parts: list[str] = []
    for root in ROOT_ORDER:
        members = by_root[root]
        if not members:
            continue
        lemmas = list(dict.fromkeys(row[lemma_field] for row in members))
        label = "/".join(lemmas)
        parts.append(f"{label} ×{len(members)}")
    return "; ".join(parts)


def historical_slot_readings(
    action: dict[str, str],
    assignments: list[dict[str, str]],
    host_values: set[str],
    *,
    rule_id: str | None = None,
) -> tuple[list[dict[str, str]], str]:
    roots_written = [row["carrier_root"] for row in assignments]
    root_set = frozenset(roots_written)
    values = frozenset(host_values)
    selected_rule = rule_id or action["gdt584_rule_id"]
    output: list[dict[str, str]] = []
    for ordinal, source in enumerate(assignments, 1):
        selected = NOUNS.choose_noun(
            action["register"],
            selected_rule,
            source["carrier_root"],
            root_set,
            values,
        )
        output.append(
            {
                "written_carrier_ordinal": str(ordinal),
                "carrier_root": source["carrier_root"],
                "working_context_family": selected["gdt587_context_family"],
                "working_lemma_de": selected["gdt587_lemma_de"],
                "working_object_form_de": selected["gdt587_object_form_de"],
                "working_genitive_form_de": selected["gdt587_genitive_form_de"],
            }
        )
    packet = NOUNS.packet_rule_id(action["register"], selected_rule, root_set)
    return output, packet


def _default_runtime(
    action: dict[str, str],
    gate_class: str,
    roots_written: list[str],
    host_values_written: list[str],
) -> tuple[dict[str, Any], str]:
    common = {
        "action_root": action["root"],
        "register": action["register"],
        "carrier_roots": roots_written,
        "direct_tokens": split_pipe(action["direct_governor_tokens"]),
        "host_tokens": host_values_written,
        "previous_action": action["previous_visible_action"],
        "next_action": action["next_visible_action"],
        "physical_page": action["physical_page"],
    }
    source_gate = "NOT_APPLICABLE"
    if gate_class == "SOURCE_ID_BOUND":
        try:
            future_host_reading(**common, source_id=action["source_event_or_card_id"])
        except RuntimeError as error:
            if "Source-ID-bound" not in str(error):
                raise
            source_gate = "EXPECTED_SOURCE_ID_REJECTION"
        else:
            source_gate = "ERROR_SOURCE_ID_RULE_AUTO_APPLIED"
        result = future_host_reading(**common, source_id="FUTURE_UNRELEASED_HOST")
    else:
        result = future_host_reading(**common, source_id=action["source_event_or_card_id"])
    return result, source_gate


def build_replay(
    data: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    actions = unique_action_map(data["actions_584"])
    gates = {row["rule_id"]: row for row in data["rule_gate_588"]}
    complete_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["complete_582"]:
        if row["primary_governor_key"] in actions:
            complete_by_host[row["primary_governor_key"]].append(row)
    assignments_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    register_root_alternatives: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in data["assignments_587"]:
        assignments_by_host[row["primary_governor_key"]].append(row)
        register_root_alternatives[(row["register"], row["carrier_root"])].add(
            row["gdt587_lemma_de"]
        )

    host_rows: list[dict[str, Any]] = []
    slot_rows: list[dict[str, Any]] = []
    for key, raw_assignments in sorted(
        assignments_by_host.items(), key=lambda item: int(min(row["assignment_ordinal"] for row in item[1]))
    ):
        assignments = ordered_assignments(raw_assignments)
        action = actions[key]
        gate = gates[action["gdt584_rule_id"]]
        gate_class = gate["gate_class"]
        complete = ordered_complete(complete_by_host[key])
        host_values_written = [row["slot_value"] for row in complete]
        host_values = set(host_values_written)
        roots_written = [row["carrier_root"] for row in assignments]
        historical, historical_packet = historical_slot_readings(action, assignments, host_values)
        parent_semantic, parent_semantic_packet = historical_slot_readings(
            action,
            assignments,
            host_values,
            rule_id=gate["parent_rule_id"],
        )
        runtime, source_gate = _default_runtime(
            action, gate_class, roots_written, host_values_written
        )
        defaults = runtime["slot_readings"]
        if len(defaults) != len(assignments) or len(historical) != len(assignments):
            raise RuntimeError(f"Slot-count mismatch at {key}")

        default_visible_matches = [
            default["working_lemma_de"] == expected["gdt587_lemma_de"]
            and default["working_object_form_de"] == expected["gdt587_object_form_de"]
            and default["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
            for default, expected in zip(defaults, assignments)
        ]
        default_noun_matches = [
            visible
            and default["context_family"] == expected["gdt587_context_family"]
            for visible, default, expected in zip(default_visible_matches, defaults, assignments)
        ]
        historical_matches = [
            old["working_lemma_de"] == expected["gdt587_lemma_de"]
            and old["working_object_form_de"] == expected["gdt587_object_form_de"]
            and old["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
            and old["working_context_family"] == expected["gdt587_context_family"]
            for old, expected in zip(historical, assignments)
        ]
        parent_semantic_visible_matches = [
            parent["working_lemma_de"] == expected["gdt587_lemma_de"]
            and parent["working_object_form_de"] == expected["gdt587_object_form_de"]
            and parent["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
            for parent, expected in zip(parent_semantic, assignments)
        ]
        parent_semantic_matches = [
            visible
            and parent["working_context_family"] == expected["gdt587_context_family"]
            for visible, parent, expected in zip(
                parent_semantic_visible_matches, parent_semantic, assignments
            )
        ]
        expected_packet = assignments[0]["gdt587_packet_rule_id"]
        default_packet = runtime["gdt587_packet_rule_id"]
        packet_match = default_packet == expected_packet
        old_packet_match = historical_packet == expected_packet
        default_rule = runtime["automatic_gdt583_rule_id"]
        broad_fallbacks = [row for row in defaults if "KEEP_BROAD" in row["lookup_route"]]
        broad_alternatives = [
            f"{row['carrier_root']}={'/'.join(sorted(register_root_alternatives[(action['register'], row['carrier_root'])]))}"
            for row in broad_fallbacks
        ]

        if gate_class == "AUTO_CONTEXT":
            outcome = "AUTO_EXACT_REPLAY" if all(default_noun_matches) and packet_match else "AUTO_DIVERGENCE"
            next_page_action = "AUTO_SELECT_COMPLETE_HOST"
        elif gate_class == "MANUAL_GDT584_OVERRIDE":
            noun_changed = not all(default_noun_matches)
            packet_changed = not packet_match
            if noun_changed and packet_changed:
                effect = "NOUN_AND_PACKET_CHANGE"
            elif noun_changed:
                effect = "NOUN_CHANGE"
            elif packet_changed:
                effect = "PACKET_CHANGE"
            else:
                effect = "CARRIER_OUTPUT_EQUIVALENT"
            outcome = f"MANUAL_VISIBLE__{effect}"
            next_page_action = "USE_PARENT_AUTOMATIC_RULE_UNLESS_MANUAL_CONTEXT_IS_EXPLICIT"
        else:
            equivalent = all(default_noun_matches) and packet_match
            outcome = (
                "SOURCE_ID_BLOCKED__PORTABLE_FALLTHROUGH_EQUIVALENT"
                if equivalent else "SOURCE_ID_BLOCKED__PORTABLE_FALLTHROUGH_DIFFERS"
            )
            next_page_action = "NEVER_REUSE_OLD_SOURCE_ID__USE_PORTABLE_FALLTHROUGH"

        repeated = len(roots_written) != len(set(roots_written))
        host_rows.append(
            {
                "host_ordinal": len(host_rows) + 1,
                "primary_governor_key": key,
                "action_slot_id": action["slot_id"],
                "layer": assignments[0]["layer"],
                "source_event_or_card_id": action["source_event_or_card_id"],
                "statement_or_record_id": action["statement_or_record_id"],
                "physical_page": action["physical_page"],
                "register": action["register"],
                "action_root": action["root"],
                "gdt583_rule_id": action["gdt583_rule_id"],
                "gdt584_rule_id": action["gdt584_rule_id"],
                "gate_class": gate_class,
                "parent_rule_id": gate["parent_rule_id"],
                "complete_host_slot_count": len(complete),
                "complete_host_values_written": pipe(host_values_written),
                "direct_governor_tokens": action["direct_governor_tokens"],
                "previous_visible_action": action["previous_visible_action"],
                "next_visible_action": action["next_visible_action"],
                "carrier_slot_count": len(assignments),
                "carrier_slot_ids": pipe(row["carrier_slot_id"] for row in assignments),
                "written_root_sequence": "+".join(roots_written),
                "written_root_multiset": root_multiset(assignments),
                "repeated_root": "YES" if repeated else "NO",
                "historical_rule_replay_exact": "YES" if all(historical_matches) and old_packet_match else "NO",
                "historical_action_reading_de": action["gdt584_working_default_de"],
                "source_id_gate_status": source_gate,
                "portable_runtime_rule_id": default_rule,
                "portable_action_reading_de": runtime["automatic_action_reading_de"],
                "portable_action_reading_match": (
                    "YES" if runtime["automatic_action_reading_de"] == action["gdt584_working_default_de"] else "NO"
                ),
                "portable_runtime_parent_rule_match": "YES" if default_rule == gate["parent_rule_id"] else "NO",
                "parent_semantic_exact_slot_count": sum(parent_semantic_matches),
                "parent_semantic_changed_slot_count": len(assignments) - sum(parent_semantic_matches),
                "parent_semantic_visible_exact_slot_count": sum(parent_semantic_visible_matches),
                "parent_semantic_visible_changed_slot_count": len(assignments) - sum(parent_semantic_visible_matches),
                "parent_semantic_lemma_sequence": pipe(row["working_lemma_de"] for row in parent_semantic),
                "parent_semantic_packet_rule_id": parent_semantic_packet,
                "parent_semantic_packet_match": "YES" if parent_semantic_packet == expected_packet else "NO",
                "expected_packet_rule_id": expected_packet,
                "portable_packet_rule_id": default_packet,
                "portable_packet_match": "YES" if packet_match else "NO",
                "portable_exact_slot_count": sum(default_noun_matches),
                "portable_changed_slot_count": len(assignments) - sum(default_noun_matches),
                "portable_visible_exact_slot_count": sum(default_visible_matches),
                "portable_visible_changed_slot_count": len(assignments) - sum(default_visible_matches),
                "portable_context_family_changed_slot_count": sum(
                    default["context_family"] != expected["gdt587_context_family"]
                    for default, expected in zip(defaults, assignments)
                ),
                "expected_lemma_sequence": noun_sequence(assignments, "gdt587_lemma_de"),
                "portable_lemma_sequence": pipe(row["working_lemma_de"] for row in defaults),
                "historical_count_trace_de": written_count_trace(assignments, "gdt587_lemma_de"),
                "portable_count_trace_de": pipe([runtime["carrier_count_trace_de"]]),
                "portable_broad_fallback_slot_count": len(broad_fallbacks),
                "portable_broad_fallback_alternatives_de": pipe(broad_alternatives),
                "replay_outcome": outcome,
                "next_page_action": next_page_action,
                "guard": "COMPLETE_ALREADY_SEGMENTED_HOST__EVERY_WRITTEN_CARRIER_SLOT_RETAINED",
            }
        )

        for expected, old, default in zip(assignments, historical, defaults):
            slot_match = (
                default["working_lemma_de"] == expected["gdt587_lemma_de"]
                and default["working_object_form_de"] == expected["gdt587_object_form_de"]
                and default["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
                and default["context_family"] == expected["gdt587_context_family"]
            )
            visible_match = (
                default["working_lemma_de"] == expected["gdt587_lemma_de"]
                and default["working_object_form_de"] == expected["gdt587_object_form_de"]
                and default["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
            )
            old_match = (
                old["working_lemma_de"] == expected["gdt587_lemma_de"]
                and old["working_object_form_de"] == expected["gdt587_object_form_de"]
                and old["working_genitive_form_de"] == expected["gdt587_genitive_form_de"]
                and old["working_context_family"] == expected["gdt587_context_family"]
            )
            slot_rows.append(
                {
                    "replay_slot_ordinal": len(slot_rows) + 1,
                    "carrier_slot_id": expected["carrier_slot_id"],
                    "primary_governor_key": key,
                    "physical_page": expected["physical_page"],
                    "register": expected["register"],
                    "gate_class": gate_class,
                    "gdt583_rule_id": action["gdt583_rule_id"],
                    "gdt584_rule_id": action["gdt584_rule_id"],
                    "portable_runtime_rule_id": default_rule,
                    "written_carrier_ordinal": default["written_carrier_ordinal"],
                    "carrier_root": expected["carrier_root"],
                    "portable_core": PORTABLE_CORE[expected["carrier_root"]],
                    "expected_context_family": expected["gdt587_context_family"],
                    "expected_lemma_de": expected["gdt587_lemma_de"],
                    "expected_object_form_de": expected["gdt587_object_form_de"],
                    "expected_genitive_form_de": expected["gdt587_genitive_form_de"],
                    "historical_rule_lemma_de": old["working_lemma_de"],
                    "historical_rule_exact": "YES" if old_match else "NO",
                    "portable_lookup_route": default["lookup_route"],
                    "observed_register_root_alternatives_de": "/".join(
                        sorted(register_root_alternatives[(expected["register"], expected["carrier_root"])])
                    ),
                    "portable_context_family": default["context_family"],
                    "portable_lemma_de": default["working_lemma_de"],
                    "portable_object_form_de": default["working_object_form_de"],
                    "portable_genitive_form_de": default["working_genitive_form_de"],
                    "portable_exact": "YES" if slot_match else "NO",
                    "portable_visible_exact": "YES" if visible_match else "NO",
                    "expected_packet_rule_id": expected_packet,
                    "portable_packet_rule_id": default_packet,
                    "guard": "EXACT_SLOT_ID_AND_WRITTEN_ORDINAL__NO_ROOT_OR_MULTIPLICITY_COLLAPSE",
                }
            )
    return host_rows, slot_rows


def unit_key(row: dict[str, str]) -> tuple[str, str]:
    if row["layer"] == "RUNNING_ATOM":
        return "STATEMENT", row["statement_or_record_id"]
    return "LOCAL_CARD", row["source_event_or_card_id"]


def add_count_overlay(
    base_rows: list[dict[str, str]],
    repeated_hosts: list[dict[str, Any]],
    *,
    layer: str,
) -> list[dict[str, Any]]:
    id_field = "statement_id" if layer == "STATEMENT" else "source_event_id"
    # GDT588 put ×N inside thirteen fluent sentences. GDT589 deliberately
    # restores that pass's fluent base and moves all 117 counts into a
    # separate written-slot channel: repeated spellings need not denote
    # repeated real-world objects.
    reader_field = "gdt588_base_reader_de"
    by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for host in repeated_hosts:
        kind, identifier = unit_key(host)  # type: ignore[arg-type]
        if kind == layer:
            by_unit[identifier].append(host)
    output: list[dict[str, Any]] = []
    for source in base_rows:
        identifier = source[id_field]
        hosts = sorted(by_unit.get(identifier, []), key=lambda row: int(row["host_ordinal"]))
        traces = [
            (
                f"{row['primary_governor_key']}: {row['written_root_sequence']} → "
                f"{row['expected_lemma_sequence']} (Multiset: {row['historical_count_trace_de']})"
            )
            for row in hosts
        ]
        overlay = " | ".join(traces) if traces else "NONE"
        base = source[reader_field]
        primary = (
            base
            if not traces
            else base
            + "\n\nGeschriebene Trägerspur (×N zählt Schriftträger, nicht Realobjekte): "
            + overlay
            + "."
        )
        output.append(
            {
                **source,
                "gdt589_base_reader_de": base,
                "gdt589_repeated_host_count": len(hosts),
                "gdt589_repeated_host_keys": pipe(row["primary_governor_key"] for row in hosts),
                "gdt589_written_carrier_overlay_de": overlay,
                "gdt589_primary_reader_de": primary,
                "gdt589_count_overlay": "YES" if hosts else "NO",
                "gdt589_guard": "GDT588_READER_RETAINED__ALL_REPEATED_WRITTEN_CARRIERS_EXPOSED",
            }
        )
    return output
