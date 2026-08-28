#!/usr/bin/env python3
"""Independent source and coverage audit for GDT584."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
ART = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G583 = ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement/artifacts"

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
OUTPUTS = {
    "revisions": ART / "gdt584_target_occurrence_revisions.tsv",
    "rules": ART / "gdt584_rule_dispositions.tsv",
    "issues": ART / "gdt584_pre_post_issue_census.tsv",
    "hosts": ART / "gdt584_statement_wide_host_phrases.tsv",
    "events": ART / "gdt584_1623_polished_event_edition.tsv",
    "local_cards": ART / "gdt584_158_polished_local_card_edition.tsv",
    "statements": ART / "gdt584_591_polished_statement_edition.tsv",
    "passages": ART / "gdt584_20_polished_passage_edition.tsv",
    "reviews": ART / "gdt584_40_statement_review_deck.tsv",
}
BOOK = ART / "GDT584_POLISHED_PASSAGES.md"
RESULT = ART / "gdt584_result.json"
VALIDATION = ART / "gdt584_validation.json"

EXPECTED_INPUT_SHA256 = {
    "complete": "dc96a9c10fc5cad003f56ae3547820969b0b59e59c3ac892e05447a9df184b5e",
    "events": "f6c65e31e1e0682cfdeff5ad200bc77e2e655baca3f5edfedcb2997418fc15ae",
    "statements": "e8d4ab7411a56f9e71daf56eea074981f85fd31fd8fae748746b339ad0ec4482",
    "local_cards": "ccacd0302233a20bd59019ed4945cb7b1fccb4266a62cc7b185ceb62d7d004cf",
    "passages": "85f9f6ab0c369eb5ecfeba14df88b002af007f1d70ddf3d349746f8b94ad4624",
    "g583_assignments": "6cb32d00bcfe989d1d370731d2327bea28ea690ba7c0b79e2728b844fd890705",
    "g583_events": "8bfe33c155fdbbd8c30ad653253286e33666b281bf6463a4fd6feee21b67ca60",
    "g583_statements": "94c7e411f3ba497c594411bb6fafc7647d3e6f40bae8eb5d820e75cc182a229c",
    "g583_local_cards": "061cee55e0b30364c3ecfeec5371f4da9609d2f5cacbb101da3429c7fa2abcdf",
    "g583_passages": "480956f89b22a4c3052a425faf90882a17e1b49964c73df436aa678de0804035",
}

EXPECTED_OUTPUT_SHA256 = {
    "revisions": "83639b9bd36fb4a44b0be0c1e60dfa2645c4c0d79eb2a79d5d90a7374f1ee0b4",
    "rules": "5dbe33b38f193a2a490dfddd50154c0e4f3580997cb8f54f776fb1cae7e8911c",
    "issues": "7407a077109a72c4033ead6f9e3a5f1db63c945012fb2e78da8b0036e1479195",
    "hosts": "b890858697b6dbbdd64fa4cbadff1a208ce57726c637f9e4a99f93472d4ba0e1",
    "events": "a7392f5e57b16d61fbb24d2a0bf245e5bbfef6ba94238613f450d0b372e6389c",
    "local_cards": "0cb1f00b68bd92818540abb35454a4c2d2014734334947f452c2d9781e0f3052",
    "statements": "753f4822aa83d309d9a2e93cf004e05cc1d0c6177016e74966a86a62a416eb42",
    "passages": "c8411ecf2fdd99e2fcec0df2a51aeb9e2ae70443018c85aeb12cfd75dd96cbdb",
    "reviews": "710b6b410ea8555bc48b17a0c14554aec3624636b4ddee27c16533e14fbab1aa",
    "book": "23af500f5349963c77c92e1159c6f538f2d5a035123890b62bfafaf4d40ee21b",
    "result": "aecf0efe78be83d696eab27814905ee34ed3e1e1d22cb3d6c6581a9aa537ba8c",
}

EXPECTED_RULE_COUNTS = {
    "CHD_BIO_TREAT": 261, "CHD_CELESTIAL_CALCULATE": 18,
    "CHD_HP_DRY_GRIND_CONFIRMED": 2, "CHD_HP_MATERIAL_COMMINUTE": 16,
    "CHD_HP_WET_EXTRACT_PROCESS": 5, "CHD_HP_WET_TRITURATE": 5,
    "CHD_REST_PROCESS": 34, "SH_BIO_BATHE": 254,
    "SH_CELESTIAL_FIX": 89, "SH_CH_BRIDGE_HOLD": 12,
    "SH_HP_EXTRACT_STEEP": 17, "SH_HP_SETTLE_BEFORE_STRAIN": 8,
    "SH_HP_SOAK": 35, "SH_HP_UNIT_HOLD": 5, "SH_REST_HOLD": 264,
    "SH_SOURCE_REST": 110, "S_BIO_CHD_CARRIER_SELECT": 1,
    "S_BIO_DIVERT": 44, "S_CELESTIAL_SELECT": 91, "S_HP_SEPARATE": 15,
    "S_HP_SIEVE": 12, "S_HP_SIEVE_DIRECT_PORTION": 1,
    "S_HP_STAGE_SEPARATE": 1, "S_HP_STRAIN": 33,
    "S_HP_STRAIN_AFTER_WET_STEP": 3, "S_HP_TAKE_OFF_AFTER_WET_STEP": 2,
    "S_REST_SELECT": 160, "S_SOURCE_SORT_OUT": 39,
    "T_AFTER_SH_COOL": 11, "T_BIO_RELATION_REGULATE": 1,
    "T_BIO_STATION_REGULATE": 54, "T_CELESTIAL_SET": 73,
    "T_HP_BEFORE_CHD_DRY": 2, "T_HP_BEFORE_SH_WARM": 10,
    "T_HP_FORM_SET": 13, "T_HP_LIQUID_TEMPER": 1,
    "T_HP_MEASURE_SET": 19, "T_PHYSICAL_BROAD": 101,
    "T_PHYSICAL_GRADE_TEMPER": 51, "T_SOURCE_FIX": 48,
}

SPECIAL_RULES = {
    "RUNNING:G407-E3488@3": "T_BIO_RELATION_REGULATE",
    "RUNNING:G407-E4570@1": "T_HP_LIQUID_TEMPER",
    "RUNNING:G407-E3903@1": "S_HP_STRAIN_AFTER_WET_STEP",
    "RUNNING:G407-E4069@4": "S_HP_STRAIN_AFTER_WET_STEP",
    "RUNNING:G407-E4407@2": "S_HP_STRAIN_AFTER_WET_STEP",
    "RUNNING:G407-E4226@1": "S_HP_SIEVE_DIRECT_PORTION",
    "RUNNING:G515-E0243@4": "S_HP_STAGE_SEPARATE",
    "RUNNING:G407-E4476@3": "CHD_HP_DRY_GRIND_CONFIRMED",
    "RUNNING:G407-E4490@2": "CHD_HP_DRY_GRIND_CONFIRMED",
}


class Table:
    def __init__(self, path: Path) -> None:
        self.path = path
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            self.fields = list(reader.fieldnames or [])
            self.rows = list(reader)
        if not self.fields:
            raise RuntimeError(f"Headerless TSV: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return dict(sorted(value.items()))
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    return value


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, check_id: str, condition: bool, observed: Any, expected: Any) -> None:
        self.checks.append(
            {
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "observed": serial(observed),
                "expected": serial(expected),
            }
        )

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [row for row in self.checks if row["status"] == "FAIL"]


def unique(rows: list[dict[str, str]], key: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    counts = Counter(row[key] for row in rows)
    return {row[key]: row for row in rows}, sorted(value for value, count in counts.items() if count != 1)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[\w/-]*\b", text, flags=re.UNICODE))


def lowercase_starts(text: str) -> int:
    return sum(
        bool(sentence and sentence[0].islower())
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    )


def remote_fine(row: dict[str, str]) -> bool:
    if row["governor_object_scope"] != "COMPLETE_GDT581_HOST_INCLUDES_REMOTE_ARGUMENT":
        return False
    direct = set(row["direct_governor_tokens"].split("|"))
    if row["gdt583_rule_id"] in {"SH_HP_EXTRACT_STEEP", "S_HP_STRAIN"}:
        return "AIIN" not in direct
    return row["gdt583_rule_id"] in {
        "SH_HP_SOAK", "S_HP_SIEVE", "S_HP_SEPARATE", "CHD_HP_DRY_GRIND",
    }


def main() -> int:
    audit = Audit()
    inputs = {name: Table(path) for name, path in INPUTS.items()}
    outputs = {name: Table(path) for name, path in OUTPUTS.items()}
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    input_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    audit.check("input_sha256", input_hashes == EXPECTED_INPUT_SHA256, input_hashes, EXPECTED_INPUT_SHA256)
    output_paths = {**OUTPUTS, "book": BOOK, "result": RESULT}
    output_hashes = {name: sha256(path) for name, path in output_paths.items()}
    audit.check("output_sha256", output_hashes == EXPECTED_OUTPUT_SHA256, output_hashes, EXPECTED_OUTPUT_SHA256)

    expected_counts = {
        "revisions": 1921, "rules": 43, "issues": 7, "hosts": 6289,
        "events": 1623, "local_cards": 158, "statements": 591,
        "passages": 20, "reviews": 40,
    }
    counts = {name: len(table.rows) for name, table in outputs.items()}
    audit.check("output_row_counts", counts == expected_counts, counts, expected_counts)

    revisions, duplicate_revision_ids = unique(outputs["revisions"].rows, "slot_id")
    old_assignments, duplicate_old_ids = unique(inputs["g583_assignments"].rows, "slot_id")
    audit.check(
        "target_slot_identity",
        not duplicate_revision_ids and not duplicate_old_ids and set(revisions) == set(old_assignments),
        {"new_duplicates": duplicate_revision_ids, "old_duplicates": duplicate_old_ids, "same_ids": set(revisions) == set(old_assignments)},
        {"new_duplicates": [], "old_duplicates": [], "same_ids": True},
    )
    fixed_fields = (
        "slot_id", "layer", "source_event_or_card_id", "statement_or_record_id",
        "physical_page", "register", "owner", "surface", "slot_position", "root",
        "primary_governor_key", "direct_governor_tokens", "governor_group_tokens",
        "governor_object_scope", "previous_visible_action", "next_visible_action",
        "gdt583_rule_id", "gdt583_working_default_de",
    )
    projection_failures = [
        slot_id for slot_id, row in revisions.items()
        if any(row[field] != old_assignments[slot_id][field] for field in fixed_fields)
    ]
    audit.check("gdt583_projection_fixed", not projection_failures, projection_failures[:20], [])

    root_counts = Counter(row["root"] for row in revisions.values())
    audit.check("target_root_counts", root_counts == {"T": 384, "SH": 794, "CHD": 341, "S": 402}, root_counts, {"T": 384, "SH": 794, "CHD": 341, "S": 402})
    layer_counts = Counter(row["layer"] for row in revisions.values())
    audit.check("target_layer_counts", layer_counts == {"RUNNING_ATOM": 1755, "LOCAL_COMPONENT": 166}, layer_counts, {"RUNNING_ATOM": 1755, "LOCAL_COMPONENT": 166})
    disposition_counts = Counter(row["gdt584_disposition"] for row in revisions.values())
    expected_dispositions = {"RETAINED": 1653, "REPHRASED": 218, "NARROWED": 34, "UPGRADED_FROM_BROAD": 15, "REVERTED_TO_BROAD": 1}
    audit.check("disposition_counts", disposition_counts == expected_dispositions, disposition_counts, expected_dispositions)
    rule_counts = Counter(row["gdt584_rule_id"] for row in revisions.values())
    audit.check("rule_counts", dict(rule_counts) == EXPECTED_RULE_COUNTS, rule_counts, EXPECTED_RULE_COUNTS)
    special_observed = {slot_id: revisions[slot_id]["gdt584_rule_id"] for slot_id in SPECIAL_RULES}
    audit.check("special_collocation_rules", special_observed == SPECIAL_RULES, special_observed, SPECIAL_RULES)

    remote_ids = {slot_id for slot_id, row in old_assignments.items() if remote_fine(row)}
    remote_statements = {old_assignments[slot_id]["statement_or_record_id"] for slot_id in remote_ids}
    published_remote = {slot_id for slot_id, row in revisions.items() if row["gdt584_remote_fine_argument"] == "YES"}
    audit.check(
        "remote_fine_rederivation",
        remote_ids == published_remote and len(remote_ids) == 62 and len(remote_statements) == 46,
        {"slots": len(remote_ids), "statements": len(remote_statements), "same_ids": remote_ids == published_remote},
        {"slots": 62, "statements": 46, "same_ids": True},
    )
    remote_status_failures = [
        slot_id for slot_id in remote_ids
        if revisions[slot_id]["gdt584_remote_fine_stitch_status"] != "STITCH_IN_STATEMENT_WIDE_HOST"
    ]
    audit.check("remote_fine_status", not remote_status_failures, remote_status_failures, [])

    statements, duplicate_statement_ids = unique(outputs["statements"].rows, "statement_id")
    old_statements, duplicate_old_statement_ids = unique(inputs["g583_statements"].rows, "statement_id")
    base_statements, duplicate_base_statement_ids = unique(inputs["statements"].rows, "statement_id")
    audit.check(
        "statement_identity",
        not duplicate_statement_ids and not duplicate_old_statement_ids and not duplicate_base_statement_ids and set(statements) == set(old_statements),
        {"duplicates": duplicate_statement_ids, "same_affected_ids": set(statements) == set(old_statements)},
        {"duplicates": [], "same_affected_ids": True},
    )
    statement_projection_failures = [
        statement_id for statement_id, row in statements.items()
        if any(row[field] != base_statements[statement_id][field] for field in ("physical_page", "register", "owner_id", "event_count", "event_ids", "surface_sequence"))
    ]
    audit.check("statement_projection_fixed", not statement_projection_failures, statement_projection_failures, [])

    complete_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    complete_by_slot: dict[str, dict[str, str]] = {}
    for row in inputs["complete"].rows:
        complete_by_slot[row["slot_id"]] = row
        if row["statement_or_record_id"] in statements:
            complete_by_statement[row["statement_or_record_id"]].append(row)
    trace_failures: list[str] = []
    for statement_id, row in statements.items():
        trace_ids = re.findall(r"\[([^=\]]+)=", row["gdt584_exact_slot_trace_de"])
        source_ids = [item["slot_id"] for item in complete_by_statement[statement_id]]
        if Counter(trace_ids) != Counter(source_ids) or int(row["complete_slot_count"]) != len(source_ids):
            trace_failures.append(statement_id)
    audit.check("statement_exact_slot_trace", not trace_failures, trace_failures[:20], [])

    host_keys = Counter((row["statement_id"], row["primary_governor_key"]) for row in outputs["hosts"].rows)
    duplicate_host_keys = [key for key, count in host_keys.items() if count != 1]
    audit.check("one_row_per_statement_governor", not duplicate_host_keys, duplicate_host_keys[:20], [])
    host_slot_ids: dict[str, list[str]] = defaultdict(list)
    host_projection_failures: list[str] = []
    remote_hosted_ids: set[str] = set()
    for row in outputs["hosts"].rows:
        slot_ids = row["written_packet_slot_ids"].split("|")
        host_slot_ids[row["statement_id"]].extend(slot_ids)
        if int(row["written_slot_count"]) != len(slot_ids):
            host_projection_failures.append(f"COUNT:{row['statement_id']}:{row['primary_governor_key']}")
        for slot_id in slot_ids:
            source = complete_by_slot.get(slot_id)
            if source is None or source["statement_or_record_id"] != row["statement_id"] or source["primary_governor_key"] != row["primary_governor_key"]:
                host_projection_failures.append(f"PROJECTION:{slot_id}")
            if slot_id in remote_ids and row["action_slot_id"] != "NONE":
                remote_hosted_ids.add(slot_id)
    audit.check("host_slot_projection", not host_projection_failures, host_projection_failures[:20], [])
    host_coverage_failures = [
        statement_id for statement_id in statements
        if Counter(host_slot_ids[statement_id]) != Counter(item["slot_id"] for item in complete_by_statement[statement_id])
    ]
    audit.check("host_partition_complete", not host_coverage_failures, host_coverage_failures, [])
    audit.check("all_remote_fine_slots_at_action_host", remote_hosted_ids == remote_ids, len(remote_hosted_ids), len(remote_ids))
    total_host_slots = sum(int(row["written_slot_count"]) for row in outputs["hosts"].rows)
    total_statement_slots = sum(int(row["complete_slot_count"]) for row in outputs["statements"].rows)
    audit.check("host_slot_totals", total_host_slots == total_statement_slots == 12707, {"hosts": total_host_slots, "statements": total_statement_slots}, {"hosts": 12707, "statements": 12707})

    remote_statement_total = sum(int(row["remote_fine_argument_count"]) for row in outputs["statements"].rows)
    remote_stitched_total = sum(int(row["remote_fine_stitched_count"]) for row in outputs["statements"].rows)
    audit.check("statement_remote_stitch_totals", remote_statement_total == remote_stitched_total == 62, {"remote": remote_statement_total, "stitched": remote_stitched_total}, {"remote": 62, "stitched": 62})
    target_statement_total = sum(int(row["target_slot_count"]) for row in outputs["statements"].rows)
    audit.check("running_target_slot_total", target_statement_total == 1755, target_statement_total, 1755)

    reader_texts = [row["gdt584_polished_paragraph_de"] for row in outputs["statements"].rows]
    banned_patterns = {
        "host_fragment": r"\bbeim\s",
        "embedded_grade": r"Temperiere auf den Grad",
        "ring_colon": r"(?:Stelle die Ringposition ein|Halte die Position fest):",
        "bad_genitive": r"\bvon die\b",
        "double_period": r"\.\.",
    }
    banned_counts = {
        name: sum(len(re.findall(pattern, text)) for text in reader_texts)
        for name, pattern in banned_patterns.items()
    }
    audit.check("reader_banned_patterns", not any(banned_counts.values()), banned_counts, {name: 0 for name in banned_patterns})
    lowercase_count = sum(lowercase_starts(text) for text in reader_texts)
    audit.check("reader_sentence_case", lowercase_count == 0, lowercase_count, 0)
    empty_reader_ids = [row["statement_id"] for row in outputs["statements"].rows if not row["gdt584_polished_paragraph_de"].strip()]
    audit.check("reader_nonempty", not empty_reader_ids, empty_reader_ids, [])

    old_reader_texts = [row["gdt583_editorial_paragraph_de"] for row in inputs["g583_statements"].rows]
    pre_fragments = sum(len(re.findall(r"\bbeim ", text)) for text in old_reader_texts)
    pre_fragment_statements = sum(bool(re.search(r"\bbeim ", text)) for text in old_reader_texts)
    pre_lower = sum(lowercase_starts(text) for text in old_reader_texts)
    pre_lower_statements = sum(lowercase_starts(text) > 0 for text in old_reader_texts)
    long100 = sum(word_count(text) > 100 for text in old_reader_texts)
    long200 = sum(word_count(text) > 200 for text in old_reader_texts)
    audit.check("pre_issue_rederivation", (pre_fragments, pre_fragment_statements, pre_lower, pre_lower_statements, long100, long200) == (1149, 327, 1761, 424, 106, 37), (pre_fragments, pre_fragment_statements, pre_lower, pre_lower_statements, long100, long200), (1149, 327, 1761, 424, 106, 37))
    issue_map = {row["issue_id"]: row for row in outputs["issues"].rows}
    expected_issue_pre = {
        "EVENT_LOCAL_HOST_FRAGMENTS": (1149, 327),
        "LOWERCASE_SENTENCE_STARTS": (1761, 424),
        "REMOTE_FINE_ARGUMENTS_SPLIT_FROM_ACTION": (62, 46),
        "LONG_INHERITED_STATEMENTS_OVER_100_WORDS": (106, 37),
        "DUPLICATE_GLOSSES_WITHIN_GOVERNOR": (340, 174),
        "EMBEDDED_RINGPOSITION_DUPLICATION": (43, 23),
        "EMBEDDED_GRADE_DUPLICATION": (32, 31),
    }
    observed_issue_pre = {key: (int(issue_map[key]["pre_occurrence_count"]), int(issue_map[key]["pre_statement_count"])) for key in expected_issue_pre}
    audit.check("published_issue_census", observed_issue_pre == expected_issue_pre, observed_issue_pre, expected_issue_pre)
    post_resolved = {
        key: (int(issue_map[key]["post_occurrence_count"]), int(issue_map[key]["post_statement_count"]))
        for key in ("EVENT_LOCAL_HOST_FRAGMENTS", "LOWERCASE_SENTENCE_STARTS", "REMOTE_FINE_ARGUMENTS_SPLIT_FROM_ACTION", "DUPLICATE_GLOSSES_WITHIN_GOVERNOR", "EMBEDDED_RINGPOSITION_DUPLICATION", "EMBEDDED_GRADE_DUPLICATION")
    }
    audit.check("resolved_issue_counts", all(value == (0, 0) for value in post_resolved.values()), post_resolved, {key: (0, 0) for key in post_resolved})

    events, duplicate_event_ids = unique(outputs["events"].rows, "event_id")
    base_events, duplicate_base_event_ids = unique(inputs["events"].rows, "event_id")
    event_projection_failures = [
        event_id for event_id, row in events.items()
        if any(row[field] != base_events[event_id][field] for field in ("statement_id", "physical_page", "register", "owner_id", "surface"))
    ]
    audit.check("event_identity_and_projection", not duplicate_event_ids and not duplicate_base_event_ids and not event_projection_failures, {"duplicates": duplicate_event_ids, "projection": event_projection_failures[:20]}, {"duplicates": [], "projection": []})
    event_target_total = sum(int(row["target_slot_count"]) for row in outputs["events"].rows)
    audit.check("event_target_total", event_target_total == 1755, event_target_total, 1755)

    local_cards, duplicate_local_ids = unique(outputs["local_cards"].rows, "source_event_id")
    base_local_cards, duplicate_base_local_ids = unique(inputs["local_cards"].rows, "source_event_id")
    local_projection_failures = [
        card_id for card_id, row in local_cards.items()
        if any(row[field] != base_local_cards[card_id][field] for field in ("physical_page", "register", "owner_de", "surface"))
    ]
    audit.check("local_identity_and_projection", not duplicate_local_ids and not duplicate_base_local_ids and not local_projection_failures, {"duplicates": duplicate_local_ids, "projection": local_projection_failures}, {"duplicates": [], "projection": []})
    local_target_total = sum(int(row["target_slot_count"]) for row in outputs["local_cards"].rows)
    audit.check("local_target_total", local_target_total == 166, local_target_total, 166)

    passage_ids = [row["statement_id"] for row in outputs["passages"].rows]
    old_passage_ids = [row["statement_id"] for row in inputs["g583_passages"].rows]
    passage_registers = Counter(row["register"] for row in outputs["passages"].rows)
    audit.check("passage_set_and_register_balance", passage_ids == old_passage_ids and set(passage_registers.values()) == {4} and len(passage_registers) == 5, {"same_order": passage_ids == old_passage_ids, "registers": passage_registers}, {"same_order": True, "registers": "five registers x four"})
    passage_projection_failures = [
        index for index, (new, old) in enumerate(zip(outputs["passages"].rows, inputs["g583_passages"].rows), 1)
        if any(new[field] != old[field] for field in ("statement_id", "physical_page", "register", "owner_id", "event_count", "surface_sequence"))
    ]
    audit.check("passage_projection_fixed", not passage_projection_failures, passage_projection_failures, [])
    review_ids = [row["statement_id"] for row in outputs["reviews"].rows]
    review_registers = Counter(row["register"] for row in outputs["reviews"].rows)
    audit.check("manual_review_deck", len(review_ids) == len(set(review_ids)) == 40 and len(review_registers) == 5, {"unique": len(set(review_ids)), "registers": review_registers}, {"unique": 40, "registers": "all five"})

    forbidden_hits: list[str] = []
    privacy_hits: list[str] = []
    for name, path in output_paths.items():
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?i)\bf84r?\b", text):
            forbidden_hits.append(name)
        private_home = "/" + "home" + "/" + "anon" + "/"
        if private_home in text or "PRIVATE KEY" in text:
            privacy_hits.append(name)
    audit.check("f84_f84r_forbidden", not forbidden_hits, forbidden_hits, [])
    audit.check("artifact_privacy_strings", not privacy_hits, privacy_hits, [])

    result_expected = {
        "target_slots": 1921, "semantic_revision_slots": 50,
        "affected_running_events": 1623, "affected_local_cards": 158,
        "affected_statements": 591, "statement_wide_hosts": 6289,
        "multi_packet_hosts": 845, "remote_fine_arguments_stitched": 62,
        "pre_host_fragments": 1149, "post_host_fragments": 0,
        "pre_lowercase_sentence_starts": 1761, "post_lowercase_sentence_starts": 0,
        "passage_checks": 20, "manual_statement_reviews": 40,
    }
    result_observed = {key: result[key] for key in result_expected}
    audit.check("result_summary", result_observed == result_expected, result_observed, result_expected)
    audit.check("result_input_hashes", result["input_sha256"] == EXPECTED_INPUT_SHA256, result["input_sha256"], EXPECTED_INPUT_SHA256)
    audit.check("result_rule_counts", result["gdt584_rule_counts"] == EXPECTED_RULE_COUNTS, result["gdt584_rule_counts"], EXPECTED_RULE_COUNTS)

    validation = {
        "experiment_id": "GDT584",
        "status": "PASS" if not audit.failures else "FAIL",
        "check_count": len(audit.checks),
        "pass_count": len(audit.checks) - len(audit.failures),
        "fail_count": len(audit.failures),
        "checks": audit.checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if audit.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
