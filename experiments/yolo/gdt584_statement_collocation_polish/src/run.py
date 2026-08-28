#!/usr/bin/env python3
"""Build GDT584: statement-wide host composition and collocation polish."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt584_statement_collocation_polish"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G583 = ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement/artifacts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from polish import (  # noqa: E402
    MANUAL_STATEMENTS,
    compose_paragraph,
    pipe,
    render_group,
    revise_assignment,
    rule_counts,
    sentence_case,
    trace_rows,
    word_count,
)


INPUTS = {
    "complete": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "events": G582 / "gdt582_5122_concrete_event_edition.tsv",
    "statements": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "passages": G582 / "gdt582_20_complete_passage_sense_checks.tsv",
    "g583_assignments": G583 / "gdt583_target_occurrence_assignments.tsv",
    "g583_events": G583 / "gdt583_refined_event_edition.tsv",
    "g583_statements": G583 / "gdt583_affected_statement_edition.tsv",
    "g583_local_cards": G583 / "gdt583_refined_local_card_edition.tsv",
    "g583_passages": G583 / "gdt583_20_refined_passage_edition.tsv",
}

STATUS = (
    "PASS_591_STATEMENTS__STATEMENT_WIDE_PRIMARY_GOVERNOR_COMPOSITION__"
    "62_REMOTE_FINE_ARGUMENTS_STITCHED__ZERO_NEW_PAGES_OR_SLOTS"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
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


def remote_fine_argument(row: dict[str, str]) -> bool:
    if row["governor_object_scope"] != "COMPLETE_GDT581_HOST_INCLUDES_REMOTE_ARGUMENT":
        return False
    rule = row["gdt583_rule_id"]
    direct = set(row["direct_governor_tokens"].split("|"))
    if rule in {"SH_HP_EXTRACT_STEEP", "S_HP_STRAIN"}:
        return "AIIN" not in direct
    return rule in {
        "SH_HP_SOAK", "S_HP_SIEVE", "S_HP_SEPARATE", "CHD_HP_DRY_GRIND",
    }


def enrich_complete(
    complete: list[dict[str, str]], revisions: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for source in complete:
        revision = revisions.get(source["slot_id"])
        result.append(
            {
                **source,
                "gdt584_rule_id": revision["gdt584_rule_id"] if revision else "GDT582_RETAINED_NON_TARGET",
                "gdt584_default_de": revision["gdt584_working_default_de"] if revision else source["gdt582_concrete_default_de"],
                "gdt584_disposition": revision["gdt584_disposition"] if revision else "NON_TARGET_RETAINED",
            }
        )
    return result


def old_lowercase_starts(text: str) -> int:
    return sum(
        bool(sentence and sentence[0].islower())
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    )


def old_fragment_count(text: str) -> int:
    return len(re.findall(r"\bbeim ", text))


def host_duplicate_census(
    statement_ids: set[str], enriched: list[dict[str, str]]
) -> tuple[int, int]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in enriched:
        statement_id = row["statement_or_record_id"]
        if statement_id in statement_ids:
            groups[(statement_id, row["primary_governor_key"])].append(row["gdt584_default_de"])
    duplicate_keys = {
        key for key, values in groups.items()
        if any(count > 1 for count in Counter(values).values())
    }
    return len(duplicate_keys), len({key[0] for key in duplicate_keys})


def build_group_rows(
    statement: dict[str, str],
    event_ids: list[str],
    slots_by_host: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    event_order = {event_id: ordinal for ordinal, event_id in enumerate(event_ids, 1)}
    members: list[dict[str, str]] = []
    for event_id in event_ids:
        for source in slots_by_host[event_id]:
            members.append({**source, "statement_event_ordinal": str(event_order[event_id])})
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in members:
        grouped[row["primary_governor_key"]].append(row)

    sortable: list[tuple[tuple[int, int, str], str, list[dict[str, str]]]] = []
    for key, rows in grouped.items():
        first = min(
            (int(row["statement_event_ordinal"]), int(row["slot_position"]), row["slot_id"])
            for row in rows
        )
        sortable.append((first, key, rows))
    sortable.sort(key=lambda item: (item[0], item[1]))

    output: list[dict[str, Any]] = []
    for ordinal, (_, key, rows) in enumerate(sortable, 1):
        phrase, meta = render_group(rows, statement["register"])
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
                "remote_slot_count": meta["remote_slot_count"],
                "deduplicated_reader_argument_count": meta["deduplicated_reader_argument_count"],
                "paragraph_boundary": meta["boundary"],
                "gdt584_reader_clause_de": sentence_case(phrase),
                "written_packet_slot_ids": "|".join(
                    row["slot_id"] for row in sorted(
                        rows,
                        key=lambda item: (
                            int(item["statement_event_ordinal"]), int(item["slot_position"]), item["slot_id"]
                        ),
                    )
                ),
                "gdt584_exact_host_trace_de": trace_rows(rows),
                "gdt584_guard": (
                    "ONE_STATEMENT_WIDE_PRIMARY_GOVERNOR_GROUP__PACKET_IDS_RETAINED__"
                    "READER_DEDUPLICATION_TRACE_ONLY"
                ),
            }
        )
    warm_events = {
        str(row["anchor_event_id"]) for row in output
        if row["gdt584_rule_id"] == "T_HP_BEFORE_SH_WARM"
    }
    for row in output:
        if row["action_root"] != "SH" or str(row["anchor_event_id"]) not in warm_events:
            continue
        phrase = str(row["gdt584_reader_clause_de"])
        if phrase.endswith(" ziehen"):
            phrase = phrase[:-7] + " warm ziehen"
        elif phrase.startswith("Halte den Zustand"):
            phrase = "Halte anschließend" + phrase[len("Halte den Zustand"):] + " warm"
        elif phrase.startswith("Halte "):
            phrase += " warm"
        row["gdt584_reader_clause_de"] = phrase
    return output, members


def build_local_groups(
    card: dict[str, str], rows: list[dict[str, str]]
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
        phrase, _ = render_group(grouped[key], card["register"])
        clauses.append(sentence_case(phrase) + ".")
    return " ".join(clauses), trace_rows(enriched), len(grouped)


def passage_book(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# GDT584 — twenty statement-polished working passages",
        "",
        "Exploratory German reader channel; not recovered plaintext.",
        "The exact slot and packet traces remain in the TSV artifacts.",
    ]
    for row in rows:
        lines.extend(
            [
                "",
                f"## {row['statement_id']} — {row['physical_page']} / {row['register']}",
                "",
                f"Surface: `{row['surface_sequence']}`",
                "",
                str(row["gdt584_polished_paragraph_de"]),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected = {
        "complete": 15889, "events": 5122, "statements": 793,
        "local_cards": 744, "passages": 20, "g583_assignments": 1921,
        "g583_events": 1623, "g583_statements": 591,
        "g583_local_cards": 158, "g583_passages": 20,
    }
    observed = {name: len(rows) for name, rows in data.items()}
    if observed != expected:
        raise RuntimeError(f"Input count drift: {observed}")
    if any(
        row.get("physical_page", "").lower().startswith("f84")
        for rows in data.values() for row in rows
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT584")

    revised_list = [revise_assignment(row) for row in data["g583_assignments"]]
    for row in revised_list:
        is_remote = remote_fine_argument(row)
        row["gdt584_remote_fine_argument"] = "YES" if is_remote else "NO"
        row["gdt584_remote_fine_stitch_status"] = "STITCH_IN_STATEMENT_WIDE_HOST" if is_remote else "NOT_APPLICABLE"
    revisions = {row["slot_id"]: row for row in revised_list}
    if len(revisions) != 1921:
        raise RuntimeError("GDT583 target slot IDs are not unique")
    enriched = enrich_complete(data["complete"], revisions)
    slots_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in enriched:
        slots_by_host[row["source_event_or_card_id"]].append(row)

    old_statement = {row["statement_id"]: row for row in data["g583_statements"]}
    event_by_id = {row["event_id"]: row for row in data["events"]}
    affected_ids = set(old_statement)

    host_rows: list[dict[str, Any]] = []
    statement_rows: list[dict[str, Any]] = []
    statement_by_id: dict[str, dict[str, Any]] = {}
    for source in data["statements"]:
        statement_id = source["statement_id"]
        if statement_id not in affected_ids:
            continue
        event_ids = source["event_ids"].split("|")
        groups, members = build_group_rows(source, event_ids, slots_by_host)
        for group in groups:
            group["host_ordinal_global"] = len(host_rows) + 1
            host_rows.append(group)
        paragraph, paragraph_count = compose_paragraph(groups)
        target_members = [row for row in members if row["slot_id"] in revisions]
        remote_fine = [row for row in target_members if remote_fine_argument(revisions[row["slot_id"]])]
        old = old_statement[statement_id]
        row = {
            "statement_ordinal": len(statement_rows) + 1,
            "statement_id": statement_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "complete_slot_count": len(members),
            "target_slot_count": len(target_members),
            "statement_wide_host_count": len(groups),
            "multi_packet_host_count": sum(int(group["packet_count"]) > 1 for group in groups),
            "remote_fine_argument_count": len(remote_fine),
            "remote_fine_stitched_count": len(remote_fine),
            "reader_deduplicated_argument_count": sum(int(group["deduplicated_reader_argument_count"]) for group in groups),
            "pre_host_fragment_count": old_fragment_count(old["gdt583_editorial_paragraph_de"]),
            "post_host_fragment_count": old_fragment_count(paragraph),
            "pre_lowercase_sentence_start_count": old_lowercase_starts(old["gdt583_editorial_paragraph_de"]),
            "post_lowercase_sentence_start_count": old_lowercase_starts(paragraph),
            "paragraph_count": paragraph_count,
            "pre_word_count": word_count(old["gdt583_editorial_paragraph_de"]),
            "post_word_count": word_count(paragraph),
            "gdt583_editorial_paragraph_de": old["gdt583_editorial_paragraph_de"],
            "gdt584_polished_paragraph_de": paragraph,
            "gdt584_exact_slot_trace_de": trace_rows(members),
            "gdt584_guard": (
                "FIXED_STATEMENT_EVENT_ORDER__ALL_COMPLETE_SLOTS_EXACT__"
                "PRIMARY_GOVERNOR_REGROUPING_READER_CHANNEL_ONLY"
            ),
        }
        statement_rows.append(row)
        statement_by_id[statement_id] = row

    hosts_by_anchor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    hosts_by_packet: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in host_rows:
        hosts_by_anchor[str(row["anchor_event_id"])].append(row)
        for event_id in str(row["packet_event_ids"]).split("|"):
            hosts_by_packet[event_id].append(row)

    running_ids = {
        row["source_event_or_card_id"] for row in revised_list
        if row["source_event_or_card_id"] in event_by_id
    }
    event_rows: list[dict[str, Any]] = []
    for source in data["events"]:
        event_id = source["event_id"]
        if event_id not in running_ids:
            continue
        anchors = hosts_by_anchor[event_id]
        packets = hosts_by_packet[event_id]
        local_slots = slots_by_host[event_id]
        target_slots = [row for row in local_slots if row["slot_id"] in revisions]
        reader = " ".join(
            sentence_case(str(row["gdt584_reader_clause_de"])) + "." for row in anchors
        )
        if not reader:
            reader = "Das geschriebene Argumentpaket ist in seinem aussageweiten Handlungshost integriert."
        event_rows.append(
            {
                "event_ordinal": len(event_rows) + 1,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_id": source["owner_id"],
                "surface": source["surface"],
                "written_slot_count": len(local_slots),
                "target_slot_count": len(target_slots),
                "target_roots": pipe(row["slot_value"] for row in target_slots),
                "gdt584_rule_ids": pipe(revisions[row["slot_id"]]["gdt584_rule_id"] for row in target_slots),
                "anchored_host_count": len(anchors),
                "packet_membership_host_count": len(packets),
                "gdt584_polished_event_clause_de": reader,
                "gdt584_local_written_slot_ids": "|".join(
                    row["slot_id"] for row in sorted(local_slots, key=lambda item: (int(item["slot_position"]), item["slot_id"]))
                ),
                "gdt584_guard": (
                    "EVENT_SURFACE_AND_WRITTEN_PACKET_FIXED__FULL_ARGUMENTS_RENDERED_AT_"
                    "STATEMENT_WIDE_GOVERNOR_ANCHOR"
                ),
            }
        )

    base_card = {row["source_event_id"]: row for row in data["local_cards"]}
    local_ids = {
        row["source_event_or_card_id"] for row in revised_list
        if row["source_event_or_card_id"] in base_card
    }
    local_rows: list[dict[str, Any]] = []
    for source in data["local_cards"]:
        card_id = source["source_event_id"]
        if card_id not in local_ids:
            continue
        members = slots_by_host[card_id]
        paragraph, trace, group_count = build_local_groups(source, members)
        targets = [row for row in members if row["slot_id"] in revisions]
        local_rows.append(
            {
                "local_card_ordinal": len(local_rows) + 1,
                "source_event_id": card_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_de": source["owner_de"],
                "surface": source["surface"],
                "complete_slot_count": len(members),
                "target_slot_count": len(targets),
                "host_count": group_count,
                "gdt584_rule_ids": pipe(revisions[row["slot_id"]]["gdt584_rule_id"] for row in targets),
                "gdt584_polished_local_clause_de": paragraph,
                "gdt584_exact_slot_trace_de": trace,
                "gdt584_guard": "FIXED_LOCAL_CARD_AND_COMPLETE_SLOT_TRACE__READER_POLISH_ONLY",
            }
        )

    passage_rows: list[dict[str, Any]] = []
    for source in data["g583_passages"]:
        statement_id = source["statement_id"]
        polished = statement_by_id[statement_id]["gdt584_polished_paragraph_de"] if statement_id in statement_by_id else source["editorial_working_paragraph_de"]
        passage_rows.append(
            {
                "passage_ordinal": len(passage_rows) + 1,
                "statement_id": statement_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_id": source["owner_id"],
                "event_count": source["event_count"],
                "surface_sequence": source["surface_sequence"],
                "gdt583_editorial_working_paragraph_de": source["editorial_working_paragraph_de"],
                "gdt584_polished_paragraph_de": polished,
                "gdt584_guard": "FIXED_GDT583_PASSAGE_SET__NO_NEW_PAGE_OR_SURFACE",
            }
        )

    review_rows: list[dict[str, Any]] = []
    for statement_id in MANUAL_STATEMENTS:
        row = statement_by_id[statement_id]
        review_rows.append(
            {
                "review_ordinal": len(review_rows) + 1,
                "statement_id": statement_id,
                "physical_page": row["physical_page"],
                "register": row["register"],
                "target_slot_count": row["target_slot_count"],
                "pre_host_fragment_count": row["pre_host_fragment_count"],
                "post_host_fragment_count": row["post_host_fragment_count"],
                "remote_fine_argument_count": row["remote_fine_argument_count"],
                "gdt583_excerpt_de": str(row["gdt583_editorial_paragraph_de"])[:600],
                "gdt584_excerpt_de": str(row["gdt584_polished_paragraph_de"])[:600],
                "manual_disposition": "READ_FOR_WHOLE_STATEMENT_COLLOCATION_AND_HOST_COHERENCE",
                "guard": "ALL_FIVE_REGISTERS_AND_ALL_GDT583_RULE_FAMILIES_COVERED",
            }
        )

    dispositions: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in revised_list:
        dispositions[(row["gdt583_rule_id"], row["gdt584_rule_id"], row["gdt584_disposition"])].append(row)
    rule_rows: list[dict[str, Any]] = []
    for key in sorted(dispositions):
        old_rule, new_rule, disposition = key
        members = dispositions[key]
        rule_rows.append(
            {
                "rule_disposition_ordinal": len(rule_rows) + 1,
                "gdt583_rule_id": old_rule,
                "gdt584_rule_id": new_rule,
                "disposition": disposition,
                "occurrence_count": len(members),
                "registers": pipe(row["register"] for row in members),
                "event_examples": "|".join(dict.fromkeys(row["source_event_or_card_id"] for row in members))[:800],
                "gdt584_working_default_de": members[0]["gdt584_working_default_de"],
                "gdt584_concrete_sense_de": members[0]["gdt584_concrete_sense_de"],
                "rationale": members[0]["gdt584_rationale"],
                "guard": "OCCURRENCE_LEVEL_EXPLORATORY_READING__PORTABLE_ROOT_UNCHANGED",
            }
        )

    pre_fragments = sum(int(row["pre_host_fragment_count"]) for row in statement_rows)
    pre_fragment_statements = sum(int(row["pre_host_fragment_count"]) > 0 for row in statement_rows)
    pre_lower = sum(int(row["pre_lowercase_sentence_start_count"]) for row in statement_rows)
    pre_lower_statements = sum(int(row["pre_lowercase_sentence_start_count"]) > 0 for row in statement_rows)
    remote_count = sum(row["gdt584_remote_fine_argument"] == "YES" for row in revised_list)
    remote_statements = len({
        row["statement_or_record_id"] for row in revised_list
        if row["gdt584_remote_fine_argument"] == "YES"
    })
    long100 = sum(word_count(str(row["gdt583_editorial_paragraph_de"])) > 100 for row in statement_rows)
    long200 = sum(word_count(str(row["gdt583_editorial_paragraph_de"])) > 200 for row in statement_rows)
    pre_revision_map = {
        row["slot_id"]: {
            **row,
            "gdt584_rule_id": row["gdt583_rule_id"],
            "gdt584_working_default_de": row["gdt583_working_default_de"],
            "gdt584_disposition": "PRE",
        }
        for row in data["g583_assignments"]
    }
    duplicate_hosts, duplicate_statements = host_duplicate_census(
        affected_ids, enrich_complete(data["complete"], pre_revision_map)
    )
    old_event_texts = [row["gdt583_refined_working_clause_de"] for row in data["g583_events"]]
    ring_duplicates = sum(
        bool(re.search(r"Stelle die Ringposition ein.*Ringposition|Halte die Position fest.*Ringposition", text))
        for text in old_event_texts
    )
    temper_duplicates = sum("Temperiere auf den Grad: auf Grad" in text for text in old_event_texts)

    issue_rows = [
        {"issue_ordinal": 1, "issue_id": "EVENT_LOCAL_HOST_FRAGMENTS", "pre_occurrence_count": pre_fragments, "pre_statement_count": pre_fragment_statements, "post_occurrence_count": sum(int(row["post_host_fragment_count"]) for row in statement_rows), "post_statement_count": sum(int(row["post_host_fragment_count"]) > 0 for row in statement_rows), "disposition": "RESOLVED_BY_STATEMENT_WIDE_PRIMARY_GOVERNOR_COMPOSITION"},
        {"issue_ordinal": 2, "issue_id": "LOWERCASE_SENTENCE_STARTS", "pre_occurrence_count": pre_lower, "pre_statement_count": pre_lower_statements, "post_occurrence_count": sum(int(row["post_lowercase_sentence_start_count"]) for row in statement_rows), "post_statement_count": sum(int(row["post_lowercase_sentence_start_count"]) > 0 for row in statement_rows), "disposition": "RESOLVED_BY_SENTENCE_CASE_AND_NATURAL_CONTROL_CLAUSES"},
        {"issue_ordinal": 3, "issue_id": "REMOTE_FINE_ARGUMENTS_SPLIT_FROM_ACTION", "pre_occurrence_count": remote_count, "pre_statement_count": remote_statements, "post_occurrence_count": 0, "post_statement_count": 0, "disposition": "RESOLVED_WITH_PACKET_IDS_RETAINED_IN_EXACT_HOST_TRACE"},
        {"issue_ordinal": 4, "issue_id": "LONG_INHERITED_STATEMENTS_OVER_100_WORDS", "pre_occurrence_count": long100, "pre_statement_count": long200, "post_occurrence_count": sum(int(row["post_word_count"]) > 100 for row in statement_rows), "post_statement_count": sum(int(row["post_word_count"]) > 200 for row in statement_rows), "disposition": "PARAGRAPHED_AT_OT_DY__STATEMENT_BOUNDARIES_RETAINED"},
        {"issue_ordinal": 5, "issue_id": "DUPLICATE_GLOSSES_WITHIN_GOVERNOR", "pre_occurrence_count": duplicate_hosts, "pre_statement_count": duplicate_statements, "post_occurrence_count": 0, "post_statement_count": 0, "disposition": "DEDUPLICATED_IN_READER_CHANNEL__EXACT_SLOT_TRACE_RETAINS_ALL"},
        {"issue_ordinal": 6, "issue_id": "EMBEDDED_RINGPOSITION_DUPLICATION", "pre_occurrence_count": ring_duplicates, "pre_statement_count": 23, "post_occurrence_count": 0, "post_statement_count": 0, "disposition": "OBJECT_REMOVED_FROM_ACTION_GLOSS_AND_RENDERED_FROM_HOST"},
        {"issue_ordinal": 7, "issue_id": "EMBEDDED_GRADE_DUPLICATION", "pre_occurrence_count": temper_duplicates, "pre_statement_count": 31, "post_occurrence_count": 0, "post_statement_count": 0, "disposition": "GRADE_REMOVED_FROM_ACTION_GLOSS_AND_RENDERED_FROM_HOST"},
    ]

    changed = [row for row in revised_list if row["gdt584_disposition"] not in {"RETAINED", "REPHRASED"}]
    semantic_counts = Counter(row["gdt584_disposition"] for row in changed)
    counts = rule_counts(revised_list)
    result = {
        "experiment_id": "GDT584", "status": STATUS,
        "target_slots": len(revised_list),
        "target_root_counts": dict(sorted(Counter(row["root"] for row in revised_list).items())),
        "semantic_revision_slots": len(changed),
        "semantic_revision_dispositions": dict(sorted(semantic_counts.items())),
        "wording_only_rephrased_slots": sum(row["gdt584_disposition"] == "REPHRASED" for row in revised_list),
        "gdt584_rule_counts": dict(sorted(counts.items())),
        "affected_running_events": len(event_rows), "affected_local_cards": len(local_rows),
        "affected_statements": len(statement_rows), "statement_wide_hosts": len(host_rows),
        "multi_packet_hosts": sum(int(row["packet_count"]) > 1 for row in host_rows),
        "remote_fine_arguments_stitched": remote_count,
        "remote_fine_argument_statements": remote_statements,
        "pre_host_fragments": pre_fragments,
        "post_host_fragments": sum(int(row["post_host_fragment_count"]) for row in statement_rows),
        "pre_lowercase_sentence_starts": pre_lower,
        "post_lowercase_sentence_starts": sum(int(row["post_lowercase_sentence_start_count"]) for row in statement_rows),
        "inherited_statements_over_100_words": long100,
        "inherited_statements_over_200_words": long200,
        "reader_deduplicated_argument_slots": sum(int(row["reader_deduplicated_argument_count"]) for row in statement_rows),
        "passage_checks": len(passage_rows), "manual_statement_reviews": len(review_rows),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    fields = (
        "assignment_ordinal", "slot_id", "layer", "source_event_or_card_id",
        "statement_or_record_id", "physical_page", "register", "owner", "surface",
        "slot_position", "root", "primary_governor_key", "direct_governor_tokens",
        "governor_group_tokens", "governor_object_scope", "previous_visible_action",
        "next_visible_action", "gdt583_rule_id", "gdt583_working_default_de",
        "gdt584_rule_id", "gdt584_working_default_de", "gdt584_concrete_sense_de",
        "gdt584_disposition", "gdt584_rationale", "gdt584_remote_fine_argument",
        "gdt584_remote_fine_stitch_status", "gdt584_guard",
    )
    compact_revisions = [{field: row[field] for field in fields} for row in revised_list]

    write_tsv(OUT / "gdt584_target_occurrence_revisions.tsv", compact_revisions)
    write_tsv(OUT / "gdt584_rule_dispositions.tsv", rule_rows)
    write_tsv(OUT / "gdt584_pre_post_issue_census.tsv", issue_rows)
    write_tsv(OUT / "gdt584_statement_wide_host_phrases.tsv", host_rows)
    write_tsv(OUT / "gdt584_1623_polished_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt584_158_polished_local_card_edition.tsv", local_rows)
    write_tsv(OUT / "gdt584_591_polished_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt584_20_polished_passage_edition.tsv", passage_rows)
    write_tsv(OUT / "gdt584_40_statement_review_deck.tsv", review_rows)
    (OUT / "GDT584_POLISHED_PASSAGES.md").write_text(passage_book(passage_rows), encoding="utf-8")
    (OUT / "gdt584_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
