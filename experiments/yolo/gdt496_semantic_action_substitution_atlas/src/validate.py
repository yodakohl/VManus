#!/usr/bin/env python3
"""Validate GDT496 source joins, semantic remainders and readable defaults."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt496_semantic_action_substitution_atlas"
ART = BASE / "artifacts"
G495 = ROOT / "experiments/yolo/gdt495_tier_a_future_comparison_sheet/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"

CARDS_IN = G495 / "gdt495_27_tier_a_future_cards.tsv"
NONTR_IN = G495 / "gdt495_86_local_nontr_support_cells.tsv"
OPPOSITE_IN = G495 / "gdt495_9_opposite_tr_support_cells.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
CARDS_OUT = ART / "gdt496_27_semantic_substitution_cards.tsv"
CELLS_OUT = ART / "gdt496_95_observed_head_cells.tsv"
EVENTS_OUT = ART / "gdt496_242_observed_family_events.tsv"
CONTEXT_OUT = ART / "gdt496_9_context_safe_defaults.tsv"
FRAMES_OUT = ART / "gdt496_9_frame_semantic_coverage.tsv"
REGISTERS_OUT = ART / "gdt496_5_register_semantic_coverage.tsv"
READABLE_OUT = ART / "GDT496_SEMANTIC_ACTION_SUBSTITUTION_ATLAS.md"
RESULT_OUT = ART / "gdt496_result.json"
VALIDATION_OUT = ART / "gdt496_validation.json"

STATUS = "EIGHTEEN_DIRECT_AND_NINE_CONTEXT_SAFE_DEFAULTS__ALL_242_OBSERVED_REMAINDERS_MATCH"
GUARD = "ARBEITSLESUNG__KEINE OBERFLÄCHENVORHERSAGE"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def split_trace(value: str) -> list[str]:
    return value.split(" · ") if value else []


def drop_index(values: list[str], index: int) -> list[str]:
    return values[:index] + values[index + 1 :]


def show_trace(values: list[str]) -> str:
    return " · ".join(values) if values else "EMPTY"


def expand_roots(values: list[str]) -> list[str]:
    output: set[str] = set()
    for value in values:
        output.update(part for part in value.split("|") if part and part != "NONE")
    return sorted(output)


def safe_phrase(phrase: str, active: bool) -> str:
    if not active:
        return phrase
    output, count = re.subn(r"\b(?:den|die|das) [^.;]+ \[wie zuvor\]", "das zuvor Genannte", phrase, count=1)
    if count != 1:
        raise ValueError(f"active phrase does not have one inherited noun: {phrase}")
    return output


def main() -> int:
    _card_in_fields, cards_in = read_tsv(CARDS_IN)
    _nontr_fields, nontr_in = read_tsv(NONTR_IN)
    _opposite_fields, opposite_in = read_tsv(OPPOSITE_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    card_out_fields, cards_out = read_tsv(CARDS_OUT)
    cell_out_fields, cells_out = read_tsv(CELLS_OUT)
    event_out_fields, events_out = read_tsv(EVENTS_OUT)
    _context_fields, context_out = read_tsv(CONTEXT_OUT)
    _frame_fields, frames_out = read_tsv(FRAMES_OUT)
    _register_fields, registers_out = read_tsv(REGISTERS_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("source_cards_27", len(cards_in) == 27, f"rows={len(cards_in)}")
    check("source_nontr_cells_86", len(nontr_in) == 86, f"rows={len(nontr_in)}")
    check("source_opposite_cells_9", len(opposite_in) == 9, f"rows={len(opposite_in)}")
    check("source_clauses_4576", len(clauses) == 4576, f"rows={len(clauses)}")
    check("output_cards_27", len(cards_out) == 27, f"rows={len(cards_out)}")
    check("output_cells_95", len(cells_out) == 95, f"rows={len(cells_out)}")
    check("output_events_242", len(events_out) == 242, f"rows={len(events_out)}")
    check("output_context_defaults_9", len(context_out) == 9, f"rows={len(context_out)}")
    check("output_frames_9", len(frames_out) == 9, f"rows={len(frames_out)}")
    check("output_registers_5", len(registers_out) == 5, f"rows={len(registers_out)}")
    check("semantic_card_ids_exact", [row["semantic_card_id"] for row in cards_out] == [f"G496-S{i:03d}" for i in range(1, 28)], "G496-S001..S027")
    check("semantic_head_ids_exact", [row["semantic_head_cell_id"] for row in cells_out] == [f"G496-H{i:03d}" for i in range(1, 96)], "G496-H001..H095")
    check("family_event_ids_exact", [row["family_event_id"] for row in events_out] == [f"G496-E{i:03d}" for i in range(1, 243)], "G496-E001..E242")

    card_in_by_id = {row["future_card_id"]: row for row in cards_in}
    card_out_by_id = {row["future_card_id"]: row for row in cards_out}
    clause_by_id = {row["global_running_event_id"]: row for row in clauses}
    support_by_id: dict[str, tuple[str, dict[str, str]]] = {}
    for row in nontr_in:
        support_by_id[row["support_cell_id"]] = ("NONTR", row)
    for row in opposite_in:
        support_by_id[row["support_cell_id"]] = ("OPPOSITE_TR", row)
    cells_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_cell: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cells_out:
        cells_by_card[row["future_card_id"]].append(row)
    for row in events_out:
        events_by_card[row["future_card_id"]].append(row)
        events_by_cell[row["support_cell_id"]].append(row)

    required_card_fields = {
        "previous_working_phrase_de",
        "context_safe_default_phrase_de",
        "substitution_class",
        "expected_portable_remainder_de",
        "expected_owner_remainder_de",
        "inherited_argument_roots_in_family",
        "guard",
    }
    required_cell_fields = {
        "support_cell_id",
        "observed_clauses_de",
        "observed_portable_remainders_de",
        "observed_owner_remainders_de",
        "inherited_argument_roots",
    }
    required_event_fields = {
        "source_event_id",
        "observed_clause_de",
        "expected_portable_remainder_de",
        "observed_portable_remainder_de",
        "expected_owner_remainder_de",
        "observed_owner_remainder_de",
    }
    check("card_schema_complete", required_card_fields <= set(card_out_fields), f"fields={len(card_out_fields)}")
    check("cell_schema_complete", required_cell_fields <= set(cell_out_fields), f"fields={len(cell_out_fields)}")
    check("event_schema_complete", required_event_fields <= set(event_out_fields), f"fields={len(event_out_fields)}")

    all_source_event_links: list[str] = []
    for cell_index, cell in enumerate(cells_out, start=1):
        support_kind, support = support_by_id[cell["support_cell_id"]]
        source = card_in_by_id[cell["future_card_id"]]
        linked_events = events_by_cell[cell["support_cell_id"]]
        all_source_event_links.extend(row["source_event_id"] for row in linked_events)
        check(
            f"cell_{cell_index:03d}_source_metadata_exact",
            cell["support_kind"] == support_kind
            and cell["future_card_id"] == support["future_card_id"]
            and cell["frozen_frame"] == source["frozen_frame"]
            and cell["target_action_recipe"] == source["action_recipe"]
            and cell["register"] == support["register"]
            and cell["alternate_action_root"] == support["alternate_action_root"]
            and cell["alternate_action_recipe"] == support["alternate_action_recipe"],
            cell["support_cell_id"],
        )
        check(
            f"cell_{cell_index:03d}_event_inventory_exact",
            int(cell["event_count"]) == int(support["event_count"]) == len(linked_events)
            and cell["source_pages"] == support["pages"]
            and cell["observed_clause_form_count"] == support["observed_clause_form_count"]
            and cell["observed_clauses_de"] == support["observed_clauses_de"],
            f"{cell['support_cell_id']}: events={len(linked_events)}",
        )
        check(
            f"cell_{cell_index:03d}_remainders_all_match",
            cell["all_portable_remainders_match"] == "YES"
            and cell["all_owner_remainders_match"] == "YES"
            and cell["observed_portable_remainder_variant_count"] == "1"
            and cell["observed_owner_remainder_variant_count"] == "1",
            f"{cell['support_cell_id']}: {cell['expected_owner_remainder_de']}",
        )
        check(
            f"cell_{cell_index:03d}_integrity_complete",
            cell["all_component_orders_match"] == "YES" and cell["all_source_roundtrips_exact"] == "YES",
            cell["support_cell_id"],
        )

    check("all_242_event_links_present", len(all_source_event_links) == 242, f"links={len(all_source_event_links)}")
    check("all_event_sources_exist", all(event_id in clause_by_id for event_id in all_source_event_links), "every card-specific source event")

    for event_index, event in enumerate(events_out, start=1):
        source_clause = clause_by_id[event["source_event_id"]]
        source_card = card_in_by_id[event["future_card_id"]]
        support_kind, support = support_by_id[event["support_cell_id"]]
        frame = source_card["frozen_frame"].split("+")
        action_index = frame.index("@ACTION")
        portable = split_trace(source_clause["portable_back_projection_de"])
        owner = split_trace(source_clause["owner_local_atom_reading_de"])
        target_portable = split_trace(source_card["portable_component_trace_de"])
        target_owner = [part.split("=", 1)[1] for part in split_trace(source_card["owner_local_slot_trace_de"])]
        expected_portable = show_trace(drop_index(target_portable, action_index))
        expected_owner = show_trace(drop_index(target_owner, action_index))
        observed_portable = show_trace(drop_index(portable, action_index))
        observed_owner = show_trace(drop_index(owner, action_index))
        check(
            f"event_{event_index:03d}_source_exact",
            event["support_kind"] == support_kind
            and event["alternate_action_recipe"] == support["alternate_action_recipe"]
            and event["source_statement_id"] == source_clause["global_statement_id"]
            and event["source_page"] == source_clause["physical_page"]
            and event["source_surface"] == source_clause["surface"]
            and event["observed_clause_de"] == source_clause["imperative_clause_de"],
            event["source_event_id"],
        )
        check(
            f"event_{event_index:03d}_remainder_exact",
            event["expected_portable_remainder_de"] == expected_portable == observed_portable == event["observed_portable_remainder_de"]
            and event["expected_owner_remainder_de"] == expected_owner == observed_owner == event["observed_owner_remainder_de"]
            and event["portable_remainder_match"] == "YES"
            and event["owner_remainder_match"] == "YES",
            f"{event['source_event_id']}: owner={expected_owner}",
        )
        check(
            f"event_{event_index:03d}_order_roundtrip_exact",
            event["component_order_match"] == "YES"
            and event["source_roundtrip_exact"] == source_clause["roundtrip_exact"] == "YES",
            event["source_event_id"],
        )

    context_by_card = {row["future_card_id"]: row for row in context_out}
    for card_index, output in enumerate(cards_out, start=1):
        source = card_in_by_id[output["future_card_id"]]
        cells = cells_by_card[output["future_card_id"]]
        events = events_by_card[output["future_card_id"]]
        active = source["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED"
        inherited_roots = expand_roots([event["inherited_argument_root"] for event in events])
        expected_class = "CONTEXT_SAFE_MULTIPLE_INHERITED_ROOTS" if active else "DIRECT_SELF_CONTAINED_REMAINDER"
        check(
            f"card_{card_index:02d}_source_meaning_preserved",
            output["priority_rank"] == source["priority_rank"]
            and output["frozen_frame"] == source["frozen_frame"]
            and output["action_root"] == source["action_root"]
            and output["action_recipe"] == source["action_recipe"]
            and output["register"] == source["register"]
            and output["portable_component_trace_de"] == source["portable_component_trace_de"]
            and output["owner_local_slot_trace_de"] == source["owner_local_slot_trace_de"]
            and output["previous_working_phrase_de"] == source["working_phrase_de"]
            and output["working_meaning_retained"] == "YES",
            output["future_card_id"],
        )
        check(
            f"card_{card_index:02d}_family_counts_exact",
            int(output["observed_head_cell_count"]) == len(cells)
            and int(output["observed_family_event_count"]) == len(events)
            and int(output["observed_nontr_head_cell_count"]) == sum(cell["support_kind"] == "NONTR" for cell in cells)
            and int(output["observed_opposite_tr_cell_count"]) == sum(cell["support_kind"] == "OPPOSITE_TR" for cell in cells),
            f"cells={len(cells)} events={len(events)}",
        )
        check(
            f"card_{card_index:02d}_semantic_class_exact",
            output["substitution_class"] == expected_class
            and output["action_substitution_reading"] == ("CONDITIONAL_ON_ACTIVE_ARGUMENT" if active else "YES")
            and output["portable_remainder_mismatch_count"] == "0"
            and output["owner_remainder_mismatch_count"] == "0",
            expected_class,
        )
        check(
            f"card_{card_index:02d}_default_phrase_exact",
            output["context_safe_default_phrase_de"] == safe_phrase(source["working_phrase_de"], active)
            and output["default_change_type"] == ("CONTEXT_NOUN_GENERALIZED" if active else "UNCHANGED_SELF_CONTAINED"),
            output["context_safe_default_phrase_de"],
        )
        check(
            f"card_{card_index:02d}_argument_profile_exact",
            output["inherited_argument_roots_in_family"] == ("|".join(inherited_roots) or "NONE")
            and (not active or len(inherited_roots) > 1)
            and (active or not inherited_roots),
            f"roots={inherited_roots}",
        )
        check(
            f"card_{card_index:02d}_guard_complete",
            output["all_component_orders_match"] == "YES"
            and output["all_source_roundtrips_exact"] == "YES"
            and output["surface_prediction_made"] == "NO"
            and output["occurrence_prediction_made"] == "NO"
            and output["guard"] == GUARD,
            output["semantic_card_id"],
        )
        check(
            f"card_{card_index:02d}_readable_complete",
            output["semantic_card_id"] in readable
            and output["context_safe_default_phrase_de"] in readable
            and all(cell["alternate_action_recipe"] in readable for cell in cells),
            output["semantic_card_id"],
        )
        if active:
            context = context_by_card[output["future_card_id"]]
            check(
                f"card_{card_index:02d}_context_row_exact",
                context["context_safe_default_de"] == output["context_safe_default_phrase_de"]
                and context["observed_inherited_argument_roots"] == output["inherited_argument_roots_in_family"]
                and context["meaning_change_made"] == "NO"
                and context["argument_noun_generalized"] == "YES"
                and context["guard"] == GUARD,
                context["context_default_id"],
            )

    check("all_active_cards_have_multiple_inherited_roots", all(len(expand_roots([event["inherited_argument_root"] for event in events_by_card[row["future_card_id"]]])) > 1 for row in cards_in if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED"), "9/9")
    check("all_self_contained_cards_have_no_inherited_root", all(not expand_roots([event["inherited_argument_root"] for event in events_by_card[row["future_card_id"]]]) for row in cards_in if row["state_requirement"] == "SELF_CONTAINED_ARGUMENT"), "18/18")
    check("readable_has_27_sections", len(re.findall(r"^## \d{2}\. G496-S\d{3}", readable, flags=re.MULTILINE)) == 27, "27 ranked sections")
    check("readable_has_27_guards", readable.count(f"**{GUARD}**") == 27, f"count={readable.count(f'**{GUARD}**')}")
    check("readable_has_every_support_cell", all(row["support_cell_id"] in readable or row["alternate_action_recipe"] in readable for row in cells_out), "95 head cells represented")
    check("readable_has_no_f84", "f84" not in readable.lower(), "sealed folio absent")

    check("frame_totals_cards", sum(int(row["card_count"]) for row in frames_out) == 27, "cards=27")
    check("frame_totals_cells", sum(int(row["observed_head_cell_count"]) for row in frames_out) == 95, "cells=95")
    check("frame_totals_events", sum(int(row["observed_family_event_count"]) for row in frames_out) == 242, "events=242")
    check("frame_zero_mismatches", all(row["portable_remainder_mismatch_count"] == row["owner_remainder_mismatch_count"] == "0" for row in frames_out), "9/9")
    check("register_totals_cards", sum(int(row["card_count"]) for row in registers_out) == 27, "cards=27")
    check("register_totals_cells", sum(int(row["observed_head_cell_count"]) for row in registers_out) == 95, "cells=95")
    check("register_totals_events", sum(int(row["observed_family_event_count"]) for row in registers_out) == 242, "events=242")
    check("register_zero_mismatches", all(row["portable_remainder_mismatch_count"] == row["owner_remainder_mismatch_count"] == "0" for row in registers_out), "5/5")

    class_counts = Counter(row["substitution_class"] for row in cards_out)
    expected_result = {
        "status": STATUS,
        "semantic_cards": 27,
        "direct_self_contained_defaults": class_counts["DIRECT_SELF_CONTAINED_REMAINDER"],
        "context_safe_defaults": sum(value for key, value in class_counts.items() if key.startswith("CONTEXT_SAFE_")),
        "context_safe_multiple_inherited_roots": class_counts["CONTEXT_SAFE_MULTIPLE_INHERITED_ROOTS"],
        "context_safe_one_inherited_root": class_counts["CONTEXT_SAFE_ONE_INHERITED_ROOT"],
        "context_safe_untagged_argument": class_counts["CONTEXT_SAFE_UNTAGGED_ARGUMENT"],
        "remainder_conflicts": class_counts["REMAINDER_CONFLICT"],
        "observed_head_cells": 95,
        "observed_nontr_head_cells": sum(row["support_kind"] == "NONTR" for row in cells_out),
        "observed_opposite_tr_cells": sum(row["support_kind"] == "OPPOSITE_TR" for row in cells_out),
        "observed_family_events": 242,
        "portable_remainder_mismatches": sum(row["portable_remainder_match"] == "NO" for row in events_out),
        "owner_remainder_mismatches": sum(row["owner_remainder_match"] == "NO" for row in events_out),
        "component_order_mismatches": sum(row["component_order_match"] == "NO" for row in events_out),
        "source_roundtrip_failures": sum(row["source_roundtrip_exact"] == "NO" for row in events_out),
        "context_noun_generalizations": len(context_out),
        "working_meaning_changes": sum(row["working_meaning_retained"] == "NO" for row in cards_out),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in cards_out),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in cards_out),
        "frame_count": len(frames_out),
        "register_count": len(registers_out),
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, "result JSON reconstructed")
    check("result_18_direct", result["direct_self_contained_defaults"] == 18, f"count={result['direct_self_contained_defaults']}")
    check("result_9_context", result["context_safe_defaults"] == result["context_safe_multiple_inherited_roots"] == 9, f"count={result['context_safe_defaults']}")
    check("result_zero_conflicts", result["remainder_conflicts"] == result["portable_remainder_mismatches"] == result["owner_remainder_mismatches"] == 0, "all remainders match")

    failed = [entry for entry in checks if not entry["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [entry["name"] for entry in failed],
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
