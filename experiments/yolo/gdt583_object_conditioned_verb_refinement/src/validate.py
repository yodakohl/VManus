#!/usr/bin/env python3
"""Independent source rederivation for GDT583.

This validator imports neither the generator nor its rule module.  It parses
the published rule deck, re-derives every context from the fixed GDT582 slot
ledger, applies first-match priority, and checks the affected editions.
"""

from __future__ import annotations

import csv
import hashlib
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
BASE = ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement"
ART = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"

INPUTS = {
    "complete": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "events": G582 / "gdt582_5122_concrete_event_edition.tsv",
    "statements": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "passages": G582 / "gdt582_20_complete_passage_sense_checks.tsv",
}
OUTPUTS = {
    "rules": ART / "gdt583_context_rule_deck.tsv",
    "assignments": ART / "gdt583_target_occurrence_assignments.tsv",
    "events": ART / "gdt583_refined_event_edition.tsv",
    "local_cards": ART / "gdt583_refined_local_card_edition.tsv",
    "statements": ART / "gdt583_affected_statement_edition.tsv",
    "passages": ART / "gdt583_20_refined_passage_edition.tsv",
    "inventory": ART / "gdt583_semantic_inventory.tsv",
}
RESULT = ART / "gdt583_result.json"
BOOK = ART / "GDT583_REFINED_PASSAGES.md"

EXPECTED_INPUT_SHA256 = {
    "complete": "dc96a9c10fc5cad003f56ae3547820969b0b59e59c3ac892e05447a9df184b5e",
    "events": "f6c65e31e1e0682cfdeff5ad200bc77e2e655baca3f5edfedcb2997418fc15ae",
    "statements": "e8d4ab7411a56f9e71daf56eea074981f85fd31fd8fae748746b339ad0ec4482",
    "local_cards": "ccacd0302233a20bd59019ed4945cb7b1fccb4266a62cc7b185ceb62d7d004cf",
    "passages": "85f9f6ab0c369eb5ecfeba14df88b002af007f1d70ddf3d349746f8b94ad4624",
}
EXPECTED_ROOT_COUNTS = {"CHD": 341, "S": 402, "SH": 794, "T": 384}
EXPECTED_RULE_COUNTS = {
    "T_SOURCE_FIX": 48,
    "T_CELESTIAL_SET": 73,
    "T_AFTER_SH_COOL": 12,
    "T_HP_BEFORE_CHD_DRY": 3,
    "T_HP_BEFORE_SH_WARM": 10,
    "T_PHYSICAL_GRADE_TEMPER": 51,
    "T_HP_FORM_SET": 13,
    "T_BIO_STATION_REGULATE": 54,
    "T_HP_MEASURE_SET": 19,
    "T_PHYSICAL_BROAD": 101,
    "SH_CH_BRIDGE_HOLD": 12,
    "SH_CELESTIAL_FIX": 89,
    "SH_BIO_BATHE": 254,
    "SH_HP_EXTRACT_STEEP": 17,
    "SH_HP_SOAK": 40,
    "SH_SOURCE_REST": 110,
    "SH_REST_HOLD": 272,
    "CHD_CELESTIAL_CALCULATE": 18,
    "CHD_BIO_TREAT": 261,
    "CHD_HP_DRY_GRIND": 23,
    "CHD_REST_PROCESS": 39,
    "S_BIO_CHD_CARRIER_SELECT": 1,
    "S_CELESTIAL_SELECT": 91,
    "S_BIO_DIVERT": 44,
    "S_HP_STRAIN": 34,
    "S_HP_SIEVE": 16,
    "S_HP_SEPARATE": 15,
    "S_SOURCE_SORT_OUT": 39,
    "S_REST_SELECT": 162,
}
EXAMPLE_RULES = {
    ("G407-E4496", "T"): "T_HP_BEFORE_SH_WARM",
    ("G407-E1758", "T"): "T_AFTER_SH_COOL",
    ("G407-E4476", "T"): "T_HP_BEFORE_CHD_DRY",
    ("G407-E3036", "T"): "T_PHYSICAL_GRADE_TEMPER",
    ("G407-E0297", "T"): "T_HP_FORM_SET",
    ("G407-E0707", "CHD"): "CHD_HP_DRY_GRIND",
    ("G407-E0360", "S"): "S_HP_STRAIN",
    ("G407-E1502", "S"): "S_BIO_DIVERT",
    ("G407-E3858", "SH"): "SH_CH_BRIDGE_HOLD",
    ("G407-E0318", "SH"): "SH_HP_EXTRACT_STEEP",
    ("G407-E4196", "SH"): "SH_HP_SOAK",
}


class Table:
    def __init__(self, path: Path) -> None:
        self.path = path
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            self.fields = list(reader.fieldnames or [])
            self.rows = list(reader)
        if not self.fields:
            raise RuntimeError(f"Headerless table: {path}")


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


def split(value: str) -> tuple[str, ...]:
    return () if value in {"", "NONE"} else tuple(value.split("|"))


def pipe(values: Iterable[str]) -> str:
    items = sorted(set(values))
    return "|".join(items) if items else "NONE"


def unique(rows: list[dict[str, str]], key: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    counts = Counter(row[key] for row in rows)
    return {row[key]: row for row in rows}, sorted(value for value, count in counts.items() if count != 1)


def projection_ok(source: dict[str, str], target: dict[str, str], fields: list[str]) -> bool:
    return all(source.get(field) == target.get(field) for field in fields)


def rule_matches(rule: dict[str, str], context: dict[str, Any]) -> bool:
    if context["root"] != rule["root"] or context["register"] not in split(rule["registers"]):
        return False
    source_ids = split(rule["source_ids"])
    if source_ids and context["source_id"] not in source_ids:
        return False
    if context["physical_page"] in split(rule["physical_pages_not"]):
        return False
    direct_any = set(split(rule["direct_any"]))
    direct_none = set(split(rule["direct_none"]))
    host_any = set(split(rule["host_any"]))
    host_none = set(split(rule["host_none"]))
    if direct_any and not context["direct_tokens"].intersection(direct_any):
        return False
    if direct_none and context["direct_tokens"].intersection(direct_none):
        return False
    if host_any and not context["host_tokens"].intersection(host_any):
        return False
    if host_none and context["host_tokens"].intersection(host_none):
        return False
    if rule["host_any_groups"] != "NONE":
        for group in rule["host_any_groups"].split(";"):
            if not context["host_tokens"].intersection(group.split("|")):
                return False
    previous = split(rule["previous_actions"])
    following = split(rule["next_actions"])
    if previous and context["previous_action"] not in previous:
        return False
    if following and context["next_action"] not in following:
        return False
    return True


def derive_contexts(complete: Table) -> dict[str, dict[str, Any]]:
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_governor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in complete.rows:
        by_card[row["source_event_or_card_id"]].append(row)
        by_governor[row["primary_governor_key"]].append(row)

    result: dict[str, dict[str, Any]] = {}
    for source in complete.rows:
        root = source["slot_value"]
        if root not in {"T", "SH", "CHD", "S"}:
            continue
        card = by_card[source["source_event_or_card_id"]]
        direct_rows = [
            row for row in card
            if row["primary_governor_key"] == source["primary_governor_key"]
        ]
        if root == "T":
            event_id = source["source_event_or_card_id"]
            direct_rows.extend(
                row for row in card
                if row["primary_governor_key"].startswith(f"ACTION_CHAIN:{event_id}:")
                and row["primary_governor_key"].rsplit(":", 1)[-1].split("+")[-1] == "T"
            )
        actions = sorted(
            [row for row in card if row["primary_governor_kind"] == "SELF_ACTION"],
            key=lambda row: (int(row["slot_position"]), row["slot_id"]),
        )
        indices = [index for index, row in enumerate(actions) if row["slot_id"] == source["slot_id"]]
        if len(indices) != 1:
            raise RuntimeError(f"Action neighbor ambiguity: {source['slot_id']}")
        index = indices[0]
        result[source["slot_id"]] = {
            "source": source,
            "root": root,
            "register": source["register"],
            "source_id": source["source_event_or_card_id"],
            "physical_page": source["physical_page"],
            "direct_tokens": {row["slot_value"] for row in direct_rows},
            "host_tokens": {
                row["slot_value"] for row in by_governor[source["primary_governor_key"]]
            },
            "previous_action": actions[index - 1]["slot_value"] if index else "NONE",
            "next_action": actions[index + 1]["slot_value"] if index + 1 < len(actions) else "NONE",
            "action_inventory": {
                row["slot_value"] for row in actions
            },
        }
    return result


def main() -> int:
    audit = Audit()
    inputs = {name: Table(path) for name, path in INPUTS.items()}
    outputs = {name: Table(path) for name, path in OUTPUTS.items()}
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    observed_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    audit.check("PINNED_GDT582_INPUT_HASHES", observed_hashes == EXPECTED_INPUT_SHA256, observed_hashes, EXPECTED_INPUT_SHA256)
    audit.check(
        "PINNED_INPUT_COUNTS",
        tuple(len(inputs[name].rows) for name in ("complete", "events", "statements", "local_cards", "passages"))
        == (15889, 5122, 793, 744, 20),
        tuple(len(inputs[name].rows) for name in ("complete", "events", "statements", "local_cards", "passages")),
        (15889, 5122, 793, 744, 20),
    )
    forbidden = [
        (name, row.get("physical_page", ""))
        for name, table in {**inputs, **outputs}.items()
        for row in table.rows
        if row.get("physical_page", "").lower().startswith("f84")
    ]
    audit.check("SEALED_F84_AND_F84R_ABSENT", not forbidden, forbidden[:10], [])

    contexts = derive_contexts(inputs["complete"])
    audit.check("TARGET_CONTEXT_COUNT", len(contexts) == 1921, len(contexts), 1921)
    audit.check(
        "TARGET_ROOT_COUNTS",
        Counter(context["root"] for context in contexts.values()) == EXPECTED_ROOT_COUNTS,
        Counter(context["root"] for context in contexts.values()),
        EXPECTED_ROOT_COUNTS,
    )

    rules = sorted(outputs["rules"].rows, key=lambda row: (int(row["priority"]), row["rule_id"]))
    rule_ids = [row["rule_id"] for row in rules]
    audit.check("RULE_DECK_UNIQUE", len(rules) == len(set(rule_ids)) == 29, (len(rules), len(set(rule_ids))), (29, 29))
    assignments, duplicate_assignments = unique(outputs["assignments"].rows, "slot_id")
    audit.check("ASSIGNMENT_IDS_EXACT", not duplicate_assignments and set(assignments) == set(contexts), (len(assignments), duplicate_assignments), (1921, []))

    mismatches: list[str] = []
    selected_counts: Counter[str] = Counter()
    for slot_id, context in contexts.items():
        candidates = [rule for rule in rules if rule_matches(rule, context)]
        if not candidates:
            mismatches.append(f"{slot_id}:NO_RULE")
            continue
        selected = candidates[0]
        selected_counts[selected["rule_id"]] += 1
        target = assignments.get(slot_id, {})
        source = context["source"]
        expected_fields = {
            "root": context["root"],
            "register": context["register"],
            "source_event_or_card_id": context["source_id"],
            "direct_governor_tokens": pipe(context["direct_tokens"]),
            "governor_group_tokens": pipe(context["host_tokens"]),
            "same_card_action_inventory": pipe(context["action_inventory"]),
            "previous_visible_action": context["previous_action"],
            "next_visible_action": context["next_action"],
            "gdt583_rule_id": selected["rule_id"],
            "gdt583_working_default_de": selected["working_default_de"],
            "gdt583_concrete_sense_de": selected["concrete_sense_de"],
            "gdt583_reading_tier": selected["reading_tier"],
            "gdt582_broad_default_de": source["gdt582_concrete_default_de"],
        }
        if any(target.get(key) != value for key, value in expected_fields.items()):
            mismatches.append(slot_id)
    audit.check("FIRST_MATCH_RULE_REDERIVATION", not mismatches, mismatches[:20], [])
    audit.check("RULE_USAGE_COUNTS", selected_counts == EXPECTED_RULE_COUNTS, selected_counts, EXPECTED_RULE_COUNTS)

    examples = {
        (row["source_event_or_card_id"], row["root"]): row["gdt583_rule_id"]
        for row in outputs["assignments"].rows
        if (row["source_event_or_card_id"], row["root"]) in EXAMPLE_RULES
    }
    audit.check("DIRECTION_AND_OBJECT_EXAMPLES", examples == EXAMPLE_RULES, examples, EXAMPLE_RULES)

    source_events, _ = unique(inputs["events"].rows, "event_id")
    source_cards, _ = unique(inputs["local_cards"].rows, "source_event_id")
    running_ids = {context["source_id"] for context in contexts.values() if context["source_id"] in source_events}
    local_ids = {context["source_id"] for context in contexts.values() if context["source_id"] in source_cards}
    target_events, duplicate_events = unique(outputs["events"].rows, "event_id")
    target_cards, duplicate_cards = unique(outputs["local_cards"].rows, "source_event_id")
    audit.check("AFFECTED_EVENT_SET", not duplicate_events and set(target_events) == running_ids and len(running_ids) == 1623, (len(target_events), duplicate_events), (1623, []))
    audit.check("AFFECTED_LOCAL_CARD_SET", not duplicate_cards and set(target_cards) == local_ids and len(local_ids) == 158, (len(target_cards), duplicate_cards), (158, []))
    event_projection_errors = [
        event_id for event_id, row in target_events.items()
        if not projection_ok(source_events[event_id], row, inputs["events"].fields)
    ]
    card_projection_errors = [
        card_id for card_id, row in target_cards.items()
        if not projection_ok(source_cards[card_id], row, inputs["local_cards"].fields)
    ]
    audit.check("EVENT_SOURCE_PROJECTION", not event_projection_errors, event_projection_errors[:20], [])
    audit.check("LOCAL_CARD_SOURCE_PROJECTION", not card_projection_errors, card_projection_errors[:20], [])

    slots_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs["complete"].rows:
        slots_by_host[row["source_event_or_card_id"]].append(row)
    trace_errors: list[str] = []
    for event_id, row in target_events.items():
        trace = row["gdt583_refined_slot_trace_de"]
        for slot in slots_by_host[event_id]:
            expected_rule = assignments[slot["slot_id"]]["gdt583_rule_id"] if slot["slot_id"] in assignments else "GDT582_RETAINED_NON_TARGET"
            if slot["slot_id"] not in trace or expected_rule not in trace:
                trace_errors.append(f"{event_id}:{slot['slot_id']}")
    for card_id, row in target_cards.items():
        trace = row["gdt583_refined_slot_trace_de"]
        for slot in slots_by_host[card_id]:
            expected_rule = assignments[slot["slot_id"]]["gdt583_rule_id"] if slot["slot_id"] in assignments else "GDT582_RETAINED_NON_TARGET"
            if slot["slot_id"] not in trace or expected_rule not in trace:
                trace_errors.append(f"{card_id}:{slot['slot_id']}")
    audit.check("COMPLETE_AFFECTED_SLOT_TRACES", not trace_errors, trace_errors[:20], [])

    source_statements, _ = unique(inputs["statements"].rows, "statement_id")
    target_statements, duplicate_statements = unique(outputs["statements"].rows, "statement_id")
    expected_statement_ids = {
        row["statement_id"] for row in inputs["statements"].rows
        if set(row["event_ids"].split("|")).intersection(running_ids)
    }
    audit.check("AFFECTED_STATEMENT_SET", not duplicate_statements and set(target_statements) == expected_statement_ids and len(expected_statement_ids) == 591, (len(target_statements), duplicate_statements), (591, []))
    statement_projection_errors = [
        statement_id for statement_id, row in target_statements.items()
        if not projection_ok(source_statements[statement_id], row, inputs["statements"].fields)
    ]
    audit.check("STATEMENT_SOURCE_PROJECTION", not statement_projection_errors, statement_projection_errors[:20], [])

    recomposition_errors: list[str] = []
    for statement_id, row in target_statements.items():
        source = source_statements[statement_id]
        expected = " ".join(
            target_events[event_id]["gdt583_refined_working_clause_de"]
            if event_id in target_events else source_events[event_id]["concrete_working_clause_de"]
            for event_id in source["event_ids"].split("|")
        )
        if row["gdt583_refined_working_reading_de"] != expected:
            recomposition_errors.append(statement_id)
    audit.check("STATEMENT_EXACT_RECOMPOSITION", not recomposition_errors, recomposition_errors[:20], [])

    passage_ids = [row["statement_id"] for row in outputs["passages"].rows]
    source_passage_ids = [row["statement_id"] for row in inputs["passages"].rows]
    register_counts = Counter(row["register"] for row in outputs["passages"].rows)
    audit.check("TWENTY_FIXED_PASSAGES", passage_ids == source_passage_ids and register_counts == {"SOURCE_SECTION_T": 4, "HERBAL": 4, "CELESTIAL": 4, "BIOLOGICAL": 4, "PHARMA": 4}, (passage_ids, register_counts), (source_passage_ids, {"SOURCE_SECTION_T": 4, "HERBAL": 4, "CELESTIAL": 4, "BIOLOGICAL": 4, "PHARMA": 4}))
    paragraph_errors = [row["statement_id"] for row in outputs["passages"].rows if len(row["editorial_working_paragraph_de"].split()) < 10]
    audit.check("EDITORIAL_PARAGRAPHS_NONTRIVIAL", not paragraph_errors, paragraph_errors, [])
    book = BOOK.read_text(encoding="utf-8")
    missing_book_ids = [statement_id for statement_id in passage_ids if f"## {statement_id} " not in book]
    audit.check("PASSAGE_BOOK_COMPLETE", not missing_book_ids and "Erwärme den Ansatz" in book, missing_book_ids, [])

    inventory = outputs["inventory"].rows
    inventory_senses = {row["concrete_sense_de"] for row in inventory if int(row["assigned_occurrence_count"]) > 0}
    expected_senses = {"temperieren", "erwärmen", "kühlen", "trocknen", "ziehen/einweichen", "baden/Badgang halten", "zerreiben", "abseihen", "sieben", "abtrennen", "umleiten"}
    audit.check("CONCRETE_SENSE_INVENTORY_PLACED", expected_senses.issubset(inventory_senses), inventory_senses, expected_senses)

    audit.check("RESULT_INPUT_HASHES", result.get("input_sha256") == EXPECTED_INPUT_SHA256, result.get("input_sha256"), EXPECTED_INPUT_SHA256)
    result_counts = (
        result.get("target_slots"), result.get("rules"), result.get("affected_running_events"),
        result.get("affected_local_cards"), result.get("affected_statements"), result.get("passage_checks"),
    )
    audit.check("RESULT_COUNTS", result_counts == (1921, 29, 1623, 158, 591, 20), result_counts, (1921, 29, 1623, 158, 591, 20))
    audit.check("RESULT_RULE_COUNTS", result.get("working_gloss_counts") is not None and result.get("unused_rules") == [], result.get("unused_rules"), [])

    validation = {
        "experiment_id": "GDT583",
        "status": "PASS" if not audit.failures else "FAIL",
        "check_count": len(audit.checks),
        "failure_count": len(audit.failures),
        "checks": audit.checks,
        "source_input_sha256": observed_hashes,
    }
    (ART / "gdt583_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
