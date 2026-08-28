#!/usr/bin/env python3
"""Build the combined six-page GDT596+GDT597 statement edition."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt598_six_page_object_statement_integration"
ARTIFACTS = BASE / "artifacts"
PAGES = ("f75r", "f77r", "f81r", "f81v", "f82r", "f83r")
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
CARRIER_ROOTS = {"Y", "AIIN", "AIN", "OR"}
STATUS = "PASS_313_STATEMENTS__2272_HOSTS__1443_ACTIONS__650_OBJECT_COMPLETE__793_GAPS__71_COMPLETE__229_MIXED__13_GAP_ONLY__298_PARTICIPANT_PACKET__46_AIIN_ONLY__449_CARRIERLESS__36_MULTI_EVENTS__10_STRING_HAZARDS__0_SLOT_COLLISIONS"

INPUTS = {
    "gdt584_hosts": ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts/gdt584_statement_wide_host_phrases.tsv",
    "gdt582_slots": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "gdt596_baths": ROOT / "experiments/yolo/gdt596_bath_object_compound_scope_phrasebook/artifacts/gdt596_254_compound_scope_replay.tsv",
    "gdt597_nonsh": ROOT / "experiments/yolo/gdt597_nonsh_action_object_reference_phrasebook/artifacts/gdt597_396_nonsh_action_object_replay.tsv",
    "gdt586_local_cards": ROOT / "experiments/yolo/gdt586_complete_name_layer_reader/artifacts/gdt586_744_complete_local_card_reader.tsv",
    "gdt596_reviews": ROOT / "experiments/yolo/gdt596_bath_object_compound_scope_phrasebook/artifacts/gdt596_23_workshop_review_cards.tsv",
    "gdt597_reviews": ROOT / "experiments/yolo/gdt597_nonsh_action_object_reference_phrasebook/artifacts/gdt597_17_manual_workshop_decisions.tsv",
}

OUTPUTS = {
    "completed_actions": ARTIFACTS / "gdt598_650_completed_object_actions.tsv",
    "host_edition": ARTIFACTS / "gdt598_2272_integrated_host_edition.tsv",
    "statements": ARTIFACTS / "gdt598_313_integrated_statements.tsv",
    "gaps": ARTIFACTS / "gdt598_793_remaining_action_gaps.tsv",
    "gap_profiles": ARTIFACTS / "gdt598_remaining_rule_profiles.tsv",
    "multi_action_events": ARTIFACTS / "gdt598_36_multi_action_event_join_hazards.tsv",
    "string_hazards": ARTIFACTS / "gdt598_10_unsafe_string_replacement_groups.tsv",
    "local_cards": ARTIFACTS / "gdt598_40_local_card_passthrough.tsv",
    "manual_reviews": ARTIFACTS / "gdt598_40_namespaced_manual_reviews.tsv",
    "pages": ARTIFACTS / "gdt598_6_page_profiles.tsv",
    "reader": ARTIFACTS / "GDT598_SIX_PAGE_INTEGRATED_READER.md",
    "result": ARTIFACTS / "gdt598_result.json",
    "validation": ARTIFACTS / "gdt598_validation.json",
}

HOST_COLUMNS = [
    "host_ordinal_global", "statement_id", "host_ordinal_in_statement", "physical_page",
    "register", "owner_id", "primary_governor_key", "anchor_event_id", "packet_event_ids",
    "action_root", "action_slot_id", "gdt584_rule_id", "paragraph_boundary",
    "gdt584_reader_clause_de",
]
SLOT_COLUMNS = [
    "slot_id", "layer", "source_event_or_card_id", "statement_or_record_id", "physical_page",
    "register", "slot_value", "slot_position", "primary_governor_kind",
    "primary_governor_key", "realization_scope", "gdt582_concrete_default_de",
]
LOCAL_CARD_COLUMNS = [
    "reader_local_card_ordinal", "local_card_host_key", "source_event_id", "physical_page",
    "register", "locus", "record_id", "owner_de", "surface", "component_recipe",
    "name_override_count", "name_override_slot_ids", "raw_name_core_sequence",
    "gdt586_primary_reader_de", "running_statement_link_status", "name_layer_status", "guard",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guarded_query(path: Path, columns: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "physical_page",
    ]
    for page in PAGES:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns)))
    command.extend(("--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats_line = next(line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS "))
    stats = json.loads(stats_line.removeprefix("GUARD_STATS "))
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if len(rows) != stats["selected"]:
        raise RuntimeError(f"guard count mismatch for {path.name}")
    if any(row["physical_page"].startswith("f84") for row in rows):
        raise RuntimeError(f"forbidden page materialized from {path.name}")
    return rows, stats


def load_inputs() -> dict[str, Any]:
    hosts, host_guard = guarded_query(INPUTS["gdt584_hosts"], HOST_COLUMNS)
    slots, slot_guard = guarded_query(INPUTS["gdt582_slots"], SLOT_COLUMNS)
    local_cards, local_guard = guarded_query(INPUTS["gdt586_local_cards"], LOCAL_CARD_COLUMNS)
    baths = read_tsv(INPUTS["gdt596_baths"])
    nonsh = read_tsv(INPUTS["gdt597_nonsh"])
    gdt596_reviews = read_tsv(INPUTS["gdt596_reviews"])
    gdt597_reviews = read_tsv(INPUTS["gdt597_reviews"])
    for name, rows in (("GDT596", baths), ("GDT597", nonsh)):
        if {row["physical_page"] for row in rows} - set(PAGES):
            raise RuntimeError(f"{name} escaped the fixed six-page population")
    return {
        "hosts": hosts,
        "slots": slots,
        "baths": baths,
        "nonsh": nonsh,
        "local_cards": local_cards,
        "gdt596_reviews": gdt596_reviews,
        "gdt597_reviews": gdt597_reviews,
        "guard_stats": {
            "gdt584_hosts": host_guard,
            "gdt582_slots": slot_guard,
            "gdt586_local_cards": local_guard,
        },
    }


def sentence_case(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" ;.")
    return cleaned[:1].upper() + cleaned[1:] if cleaned else ""


def compose_paragraphs(rows: list[dict[str, str]], clause_field: str) -> tuple[str, int]:
    paragraphs: list[list[str]] = [[]]
    for row in rows:
        clause = sentence_case(row[clause_field])
        if clause:
            paragraphs[-1].append(clause + ".")
        if row["paragraph_boundary"] == "PARAGRAPH_AFTER" and paragraphs[-1]:
            paragraphs.append([])
    nonempty = [paragraph for paragraph in paragraphs if paragraph]
    return "\n\n".join(" ".join(paragraph) for paragraph in nonempty), len(nonempty)


def compact_profile(counter: Counter[str]) -> str:
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def build(inputs: dict[str, Any]) -> dict[str, Any]:
    hosts = sorted(inputs["hosts"], key=lambda row: int(row["host_ordinal_global"]))
    slots = list(inputs["slots"])
    baths = list(inputs["baths"])
    nonsh = list(inputs["nonsh"])
    local_card_sources = list(inputs["local_cards"])
    gdt596_review_sources = list(inputs["gdt596_reviews"])
    gdt597_review_sources = list(inputs["gdt597_reviews"])

    carrier_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        if (
            row["layer"] == "RUNNING_ATOM"
            and row["slot_value"] in CARRIER_ROOTS
            and row["primary_governor_key"].startswith("ACTION:")
        ):
            carrier_by_host[row["primary_governor_key"]].append(row)
    for rows in carrier_by_host.values():
        rows.sort(key=lambda row: (row["source_event_or_card_id"], int(row["slot_position"]), row["slot_id"]))

    completed: dict[str, dict[str, str]] = {}
    for row in baths:
        key = f"ACTION:{row['action_slot_id'].removeprefix('RUNNING:')}:SH"
        completed[key] = {
            "completion_layer": "GDT596_SH_OBJECT_PHRASEBOOK",
            "object_class": "UNIT" if row["object_class"] == "BATH_UNIT" else row["object_class"],
            "object_lemma_de": row["object_lemma_de"],
            "rendered_object_np_de": row["rendered_object_np_de"],
            "typing_card_id": row["typing_card_id"],
            "reference_scope_card_id": row["reference_scope_card_id"],
            "reference_mode": row["reference_mode"],
            "source_pointer": row["scope_source_pointer"],
            "completed_clause_de": row["gdt596_reconstructed_clause_de"],
        }
    if len(completed) != 254:
        raise RuntimeError(f"GDT596 key drift: {len(completed)}")
    for row in nonsh:
        key = row["primary_governor_key"]
        if key in completed:
            raise RuntimeError(f"completion overlap at {key}")
        completed[key] = {
            "completion_layer": "GDT597_NONSH_OBJECT_PHRASEBOOK",
            "object_class": row["object_class"],
            "object_lemma_de": row["object_lemma_de"],
            "rendered_object_np_de": row["rendered_object_np_de"],
            "typing_card_id": row["typing_card_id"],
            "reference_scope_card_id": row["reference_scope_card_id"],
            "reference_mode": row["reference_mode"],
            "source_pointer": row["source_pointer"],
            "completed_clause_de": row["gdt597_completed_clause_de"],
        }
    if len(completed) != 650:
        raise RuntimeError(f"combined completion drift: {len(completed)}")

    host_keys = {row["primary_governor_key"] for row in hosts}
    missing = set(completed) - host_keys
    if missing:
        raise RuntimeError(f"completed keys outside GDT584 stream: {sorted(missing)[:3]}")

    host_edition: list[dict[str, str]] = []
    completed_actions: list[dict[str, str]] = []
    gaps: list[dict[str, str]] = []
    for source in hosts:
        key = source["primary_governor_key"]
        is_action = source["action_root"] in ACTION_ROOTS
        completion = completed.get(key)
        carriers = carrier_by_host.get(key, [])
        if completion is not None:
            integration_status = "COMPLETED_OBJECT_ACTION"
            completion_layer = completion["completion_layer"]
            clause = completion["completed_clause_de"]
            object_class = completion["object_class"]
            object_lemma = completion["object_lemma_de"]
            rendered_np = completion["rendered_object_np_de"]
            typing_card = completion["typing_card_id"]
            reference_card = completion["reference_scope_card_id"]
            reference_mode = completion["reference_mode"]
            source_pointer = completion["source_pointer"]
        elif is_action:
            integration_status = "REMAINING_ACTION_GAP"
            completion_layer = "UPSTREAM_GDT584"
            clause = source["gdt584_reader_clause_de"]
            object_class = "UNRESOLVED"
            object_lemma = "UNRESOLVED"
            rendered_np = "UNRESOLVED"
            typing_card = "UNRESOLVED"
            reference_card = "UNRESOLVED"
            reference_mode = "UNRESOLVED"
            source_pointer = "UNRESOLVED"
        else:
            integration_status = "NON_ACTION_RETAINED"
            completion_layer = "UPSTREAM_GDT584"
            clause = source["gdt584_reader_clause_de"]
            object_class = "NOT_APPLICABLE"
            object_lemma = "NOT_APPLICABLE"
            rendered_np = "NOT_APPLICABLE"
            typing_card = "NOT_APPLICABLE"
            reference_card = "NOT_APPLICABLE"
            reference_mode = "NOT_APPLICABLE"
            source_pointer = "NOT_APPLICABLE"
        row = {
            "host_ordinal_global": source["host_ordinal_global"],
            "statement_id": source["statement_id"],
            "host_ordinal_in_statement": source["host_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "primary_governor_key": key,
            "anchor_event_id": source["anchor_event_id"],
            "action_root": source["action_root"],
            "action_slot_id": source["action_slot_id"],
            "gdt584_rule_id": source["gdt584_rule_id"],
            "paragraph_boundary": source["paragraph_boundary"],
            "integration_status": integration_status,
            "completion_layer": completion_layer,
            "written_carrier_count": str(len(carriers)),
            "written_carrier_roots": "+".join(row["slot_value"] for row in carriers) or "NONE",
            "written_carrier_lemmas_de": "|".join(row["gdt582_concrete_default_de"] for row in carriers) or "NONE",
            "object_class": object_class,
            "object_lemma_de": object_lemma,
            "rendered_object_np_de": rendered_np,
            "typing_card_id": typing_card,
            "reference_scope_card_id": reference_card,
            "reference_mode": reference_mode,
            "source_pointer": source_pointer,
            "gdt584_upstream_clause_de": source["gdt584_reader_clause_de"],
            "gdt598_integrated_clause_de": clause,
            "clause_changed": "YES" if clause != source["gdt584_reader_clause_de"] else "NO",
            "guard": "SIX_FIXED_PAGES__GDT596_PLUS_GDT597_EXACT_PATCH__UPSTREAM_OTHER_HOSTS__NO_NEW_PAGE_ROOT_PARSER_OR_SEGMENT",
        }
        host_edition.append(row)
        if completion is not None:
            completed_actions.append({
                "completed_action_ordinal": str(len(completed_actions) + 1),
                **{name: row[name] for name in (
                    "host_ordinal_global", "statement_id", "host_ordinal_in_statement", "physical_page",
                    "primary_governor_key", "anchor_event_id", "action_slot_id", "action_root", "gdt584_rule_id",
                    "completion_layer", "object_class", "object_lemma_de", "rendered_object_np_de",
                    "typing_card_id", "reference_scope_card_id", "reference_mode", "source_pointer",
                    "gdt584_upstream_clause_de", "gdt598_integrated_clause_de", "clause_changed",
                )},
            })
        elif is_action:
            participant_carriers = [
                carrier for carrier in carriers if carrier["slot_value"] in {"Y", "AIN", "OR"}
            ]
            if participant_carriers:
                gap_route = "WRITTEN_PARTICIPANT_PACKET_AVAILABLE"
                next_task = "TYPE_WRITTEN_PARTICIPANT_PACKET"
            elif carriers:
                gap_route = "AIIN_ONLY_PARAMETER__OBJECT_STILL_NEEDED"
                next_task = "KEEP_PARAMETER__SEARCH_TYPED_REFERENCE_THEN_ACTION_DEFAULT"
            else:
                gap_route = "CARRIERLESS_DEFAULT_OR_REFERENCE_NEEDED"
                next_task = "SEARCH_TYPED_REFERENCE_THEN_ACTION_DEFAULT"
            gaps.append({
                "gap_ordinal": str(len(gaps) + 1),
                **{name: row[name] for name in (
                    "host_ordinal_global", "statement_id", "host_ordinal_in_statement", "physical_page",
                    "register", "primary_governor_key", "anchor_event_id", "action_slot_id", "action_root",
                    "gdt584_rule_id", "written_carrier_count", "written_carrier_roots",
                    "written_carrier_lemmas_de", "gdt584_upstream_clause_de",
                )},
                "gap_route": gap_route,
                "next_object_task": next_task,
            })

    if len(host_edition) != 2272 or len(completed_actions) != 650 or len(gaps) != 793:
        raise RuntimeError(
            f"integration population drift: hosts={len(host_edition)} completed={len(completed_actions)} gaps={len(gaps)}"
        )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in host_edition:
        by_statement[row["statement_id"]].append(row)
    statements = []
    for statement_id, rows in sorted(by_statement.items(), key=lambda item: int(item[1][0]["host_ordinal_global"])):
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
        original, original_paragraphs = compose_paragraphs(rows, "gdt584_upstream_clause_de")
        integrated, integrated_paragraphs = compose_paragraphs(rows, "gdt598_integrated_clause_de")
        completed_count = sum(row["integration_status"] == "COMPLETED_OBJECT_ACTION" for row in rows)
        gap_count = sum(row["integration_status"] == "REMAINING_ACTION_GAP" for row in rows)
        statements.append({
            "statement_ordinal": str(len(statements) + 1),
            "statement_id": statement_id,
            "physical_page": rows[0]["physical_page"],
            "register": rows[0]["register"],
            "owner_id": rows[0]["owner_id"],
            "host_count": str(len(rows)),
            "action_count": str(sum(row["action_root"] in ACTION_ROOTS for row in rows)),
            "completed_object_action_count": str(completed_count),
            "remaining_action_gap_count": str(gap_count),
            "changed_host_count": str(sum(row["clause_changed"] == "YES" for row in rows)),
            "paragraph_count": str(integrated_paragraphs),
            "coverage_state": (
                "ALL_ACTIONS_OBJECT_COMPLETE" if gap_count == 0
                else "MIXED_COMPLETED_AND_GAP_ACTIONS" if completed_count
                else "GAP_ONLY_ACTIONS"
            ),
            "completed_root_profile": compact_profile(Counter(row["action_root"] for row in rows if row["integration_status"] == "COMPLETED_OBJECT_ACTION")) or "NONE",
            "remaining_root_profile": compact_profile(Counter(row["action_root"] for row in rows if row["integration_status"] == "REMAINING_ACTION_GAP")) or "NONE",
            "gdt584_reader_de": original,
            "gdt598_integrated_reader_de": integrated,
            "paragraph_count_preserved": "YES" if original_paragraphs == integrated_paragraphs else "NO",
        })
    if len(statements) != 313:
        raise RuntimeError(f"statement count drift: {len(statements)}")

    gap_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in gaps:
        gap_groups[(row["action_root"], row["gdt584_rule_id"])].append(row)
    gap_profiles = []
    for order, ((root, rule), rows) in enumerate(sorted(gap_groups.items()), start=1):
        gap_profiles.append({
            "profile_ordinal": str(order),
            "action_root": root,
            "gdt584_rule_id": rule,
            "gap_count": str(len(rows)),
            "written_carrier_host_count": str(sum(row["written_carrier_count"] != "0" for row in rows)),
            "written_participant_packet_host_count": str(sum(row["gap_route"] == "WRITTEN_PARTICIPANT_PACKET_AVAILABLE" for row in rows)),
            "aiin_only_parameter_host_count": str(sum(row["gap_route"] == "AIIN_ONLY_PARAMETER__OBJECT_STILL_NEEDED" for row in rows)),
            "carrierless_host_count": str(sum(row["written_carrier_count"] == "0" for row in rows)),
            "carrier_root_profile": compact_profile(Counter(root_value for row in rows for root_value in row["written_carrier_roots"].split("+") if root_value != "NONE")) or "NONE",
            "page_profile": compact_profile(Counter(row["physical_page"] for row in rows)),
            "example_governor_key": rows[0]["primary_governor_key"],
            "example_upstream_clause_de": rows[0]["gdt584_upstream_clause_de"],
        })

    completed_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in completed_actions:
        completed_by_event[row["anchor_event_id"]].append(row)
    multi_action_events = []
    for event_id, rows in sorted(
        ((event_id, rows) for event_id, rows in completed_by_event.items() if len(rows) > 1),
        key=lambda item: int(item[1][0]["host_ordinal_global"]),
    ):
        layer_profile = Counter(row["completion_layer"] for row in rows)
        multi_action_events.append({
            "hazard_ordinal": str(len(multi_action_events) + 1),
            "anchor_event_id": event_id,
            "statement_id": rows[0]["statement_id"],
            "physical_page": rows[0]["physical_page"],
            "completed_action_count": str(len(rows)),
            "join_hazard_class": "CROSS_LAYER_EVENT_COLLISION" if len(layer_profile) > 1 else "WITHIN_LAYER_MULTI_ACTION_EVENT",
            "completion_layer_profile": compact_profile(layer_profile),
            "primary_governor_keys": "|".join(row["primary_governor_key"] for row in rows),
            "action_slot_ids": "|".join(row["action_slot_id"] for row in rows),
            "action_roots": "+".join(row["action_root"] for row in rows),
            "object_lemmas_de": "|".join(row["object_lemma_de"] for row in rows),
            "integrated_clauses_de": " || ".join(row["gdt598_integrated_clause_de"] for row in rows),
            "required_join_key": "EXACT_ACTION_SLOT_ID__EVENT_ID_IS_NOT_UNIQUE",
        })

    completed_by_old_clause: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in completed_actions:
        completed_by_old_clause[row["gdt584_upstream_clause_de"]].append(row)
    string_hazards = []
    for old_clause, rows in sorted(
        (
            (old_clause, rows) for old_clause, rows in completed_by_old_clause.items()
            if len({row["gdt598_integrated_clause_de"] for row in rows}) > 1
        ),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        final_clauses = sorted({row["gdt598_integrated_clause_de"] for row in rows})
        string_hazards.append({
            "hazard_ordinal": str(len(string_hazards) + 1),
            "gdt584_upstream_clause_de": old_clause,
            "affected_action_count": str(len(rows)),
            "distinct_final_clause_count": str(len(final_clauses)),
            "completion_layer_profile": compact_profile(Counter(row["completion_layer"] for row in rows)),
            "example_governor_keys": "|".join(row["primary_governor_key"] for row in rows[:5]),
            "final_clauses_de": " || ".join(final_clauses),
            "required_join_key": "EXACT_ACTION_SLOT_ID__CLAUSE_STRING_REPLACEMENT_IS_UNSAFE",
        })

    local_cards = []
    for source in sorted(local_card_sources, key=lambda row: int(row["reader_local_card_ordinal"])):
        local_cards.append({
            "six_page_local_card_ordinal": str(len(local_cards) + 1),
            **source,
            "integration_route": "SEPARATE_LOCAL_APPENDIX__NEVER_INHERIT_INTO_RUNNING_STATEMENT",
        })

    bath_page_by_event = {row["source_event_id"]: row["physical_page"] for row in baths}
    manual_reviews = []
    for source in gdt596_review_sources:
        manual_reviews.append({
            "namespaced_review_id": f"GDT596:{source['review_id']}",
            "source_layer": "GDT596_SH_OBJECT_PHRASEBOOK",
            "native_review_id": source["review_id"],
            "target_key": source["event_id"],
            "statement_id": source["statement_id"],
            "physical_page": bath_page_by_event[source["event_id"]],
            "review_class": source["review_class"],
            "selected_clause_de": source["current_clause_de"],
            "workshop_reading_or_reason_de": source["fluent_default_de"],
            "retained_rival_de": source["object_rival_clause_de"],
            "decision_de": source["default_action"],
            "typing_card_id": source["typing_card_id"],
            "reference_scope_card_id": source["reference_scope_card_id"],
        })
    for source in gdt597_review_sources:
        completion = completed[source["primary_governor_key"]]
        manual_reviews.append({
            "namespaced_review_id": f"GDT597:{source['review_id']}",
            "source_layer": "GDT597_NONSH_OBJECT_PHRASEBOOK",
            "native_review_id": source["review_id"],
            "target_key": source["primary_governor_key"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "review_class": source["review_class"],
            "selected_clause_de": source["completed_clause_de"],
            "workshop_reading_or_reason_de": source["workshop_reason_de"],
            "retained_rival_de": source["retained_rival_de"],
            "decision_de": source["decision_de"],
            "typing_card_id": completion["typing_card_id"],
            "reference_scope_card_id": completion["reference_scope_card_id"],
        })

    pages = []
    for page in PAGES:
        page_hosts = [row for row in host_edition if row["physical_page"] == page]
        page_statements = [row for row in statements if row["physical_page"] == page]
        pages.append({
            "physical_page": page,
            "statement_count": str(len(page_statements)),
            "host_count": str(len(page_hosts)),
            "action_count": str(sum(row["action_root"] in ACTION_ROOTS for row in page_hosts)),
            "completed_object_action_count": str(sum(row["integration_status"] == "COMPLETED_OBJECT_ACTION" for row in page_hosts)),
            "remaining_action_gap_count": str(sum(row["integration_status"] == "REMAINING_ACTION_GAP" for row in page_hosts)),
            "completed_root_profile": compact_profile(Counter(row["action_root"] for row in page_hosts if row["integration_status"] == "COMPLETED_OBJECT_ACTION")),
            "remaining_root_profile": compact_profile(Counter(row["action_root"] for row in page_hosts if row["integration_status"] == "REMAINING_ACTION_GAP")),
            "changed_statement_count": str(sum(int(row["changed_host_count"]) > 0 for row in page_statements)),
        })

    result = {
        "experiment_id": "GDT598",
        "status": STATUS,
        "page_count": len(PAGES),
        "statement_count": len(statements),
        "host_count": len(host_edition),
        "action_count": sum(row["action_root"] in ACTION_ROOTS for row in host_edition),
        "non_action_host_count": sum(row["action_root"] not in ACTION_ROOTS for row in host_edition),
        "completed_object_action_count": len(completed_actions),
        "remaining_action_gap_count": len(gaps),
        "completion_layer_profile": dict(sorted(Counter(row["completion_layer"] for row in completed_actions).items())),
        "completed_root_profile": dict(sorted(Counter(row["action_root"] for row in completed_actions).items())),
        "remaining_root_profile": dict(sorted(Counter(row["action_root"] for row in gaps).items())),
        "completed_object_class_profile": dict(sorted(Counter(row["object_class"] for row in completed_actions).items())),
        "gap_route_profile": dict(sorted(Counter(row["gap_route"] for row in gaps).items())),
        "gap_rule_profile_count": len(gap_profiles),
        "statement_coverage_profile": dict(sorted(Counter(row["coverage_state"] for row in statements).items())),
        "completed_event_count": len(completed_by_event),
        "multi_action_completed_event_count": len(multi_action_events),
        "cross_layer_event_collision_count": sum(row["join_hazard_class"] == "CROSS_LAYER_EVENT_COLLISION" for row in multi_action_events),
        "action_excess_over_completed_events": len(completed_actions) - len(completed_by_event),
        "distinct_completed_upstream_clause_count": len(completed_by_old_clause),
        "unsafe_string_replacement_group_count": len(string_hazards),
        "unsafe_string_replacement_action_count": sum(int(row["affected_action_count"]) for row in string_hazards),
        "local_card_passthrough_count": len(local_cards),
        "local_card_name_override_host_count": sum(int(row["name_override_count"]) > 0 for row in local_cards),
        "local_card_name_override_slot_count": sum(int(row["name_override_count"]) for row in local_cards),
        "manual_review_count": len(manual_reviews),
        "native_manual_review_id_collision_count": sum(
            count > 1 for count in Counter(row["native_review_id"] for row in manual_reviews).values()
        ),
        "changed_host_count": sum(row["clause_changed"] == "YES" for row in host_edition),
        "changed_statement_count": sum(int(row["changed_host_count"]) > 0 for row in statements),
        "paragraph_count_preserved": sum(row["paragraph_count_preserved"] == "YES" for row in statements),
        "guard_stats": inputs["guard_stats"],
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "next_route_de": (
            "Die 650 fertigen SH/T/CHD/S-Aktionen bleiben unverändert. Als nächstes werden die 793 sichtbaren "
            "Restaktionen occurrence-genau über geschriebenes Packet, kompatible Referenz und einfachen "
            "Aktionsdefault geschlossen; keine neue Seite oder Wurzel ist nötig."
        ),
    }

    built: dict[str, Any] = {
        "completed_actions": completed_actions,
        "host_edition": host_edition,
        "statements": statements,
        "gaps": gaps,
        "gap_profiles": gap_profiles,
        "multi_action_events": multi_action_events,
        "string_hazards": string_hazards,
        "local_cards": local_cards,
        "manual_reviews": manual_reviews,
        "pages": pages,
        "result": result,
    }
    built["reader"] = render_reader(statements, local_cards, result)
    return built


def render_reader(
    statements: list[dict[str, str]],
    local_cards: list[dict[str, str]],
    result: dict[str, Any],
) -> str:
    lines = [
        "# GDT598 — integrierte Sechs-Seiten-Arbeitslesung",
        "",
        f"Status: `{result['status']}`",
        "",
        f"{result['completed_object_action_count']} von {result['action_count']} Aktionshosts besitzen die vollständige GDT596/GDT597-Objektschicht; ",
        f"{result['remaining_action_gap_count']} Restaktionen bleiben im Text sichtbar markiert. Der Join verwendet zwingend exakte Action-Slots: ",
        f"{result['multi_action_completed_event_count']} Ereignisse tragen mehrere fertige Aktionen und {result['unsafe_string_replacement_group_count']} alte Klauselstrings haben mehrere Zielklauseln.",
        "",
    ]
    current_page = ""
    for row in statements:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend((f"## {current_page}", ""))
        lines.extend((
            f"### {row['statement_id']}",
            "",
            f"Objektfertig: {row['completed_object_action_count']}/{row['action_count']}; Rest: {row['remaining_action_gap_count']}; Zustand: `{row['coverage_state']}`.",
            "",
            row["gdt598_integrated_reader_de"],
            "",
        ))
    lines.extend((
        "## Getrennte lokale Karten",
        "",
        "Diese Karten bleiben eine eigene Seitenschicht und erben niemals in die laufenden Aussagen.",
        "",
    ))
    current_page = ""
    for row in local_cards:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend((f"### {current_page}", ""))
        lines.extend((
            f"- `{row['local_card_host_key']}` ({row['locus']}): {row['gdt586_primary_reader_de']}",
            "",
        ))
    return "\n".join(lines)


def tsv_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    row_list = list(rows)
    if not row_list:
        return b""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(row_list[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(row_list)
    return stream.getvalue().encode("utf-8")


def write_built(built: dict[str, Any]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in ("completed_actions", "host_edition", "statements", "gaps", "gap_profiles", "multi_action_events", "string_hazards", "local_cards", "manual_reviews", "pages"):
        OUTPUTS[name].write_bytes(tsv_bytes(built[name]))
    OUTPUTS["reader"].write_text(built["reader"], encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
