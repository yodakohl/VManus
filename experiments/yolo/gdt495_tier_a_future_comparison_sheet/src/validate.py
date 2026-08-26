#!/usr/bin/env python3
"""Validate the complete 27-card GDT495 future-comparison sheet."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt495_tier_a_future_comparison_sheet"
ART = BASE / "artifacts"
G494 = ROOT / "experiments/yolo/gdt494_composed_cell_family_support_ranking/artifacts"

TIER_A_PATH = G494 / "gdt494_27_tier_a_multihead_cards.tsv"
NONTR_PATH = G494 / "gdt494_105_same_register_nontr_support_cells.tsv"
OPPOSITE_PATH = G494 / "gdt494_21_same_register_opposite_tr_cells.tsv"
CROSS_PATH = G494 / "gdt494_98_same_action_cross_register_cells.tsv"
CARD_PATH = ART / "gdt495_27_tier_a_future_cards.tsv"
NONTR_OUT = ART / "gdt495_86_local_nontr_support_cells.tsv"
OPPOSITE_OUT = ART / "gdt495_9_opposite_tr_support_cells.tsv"
CROSS_OUT = ART / "gdt495_43_cross_register_anchor_cells.tsv"
REGISTER_OUT = ART / "gdt495_5_register_card_coverage.tsv"
READABLE_OUT = ART / "GDT495_27_TIER_A_FUTURE_COMPARISON_SHEET.md"
RESULT_OUT = ART / "gdt495_result.json"
VALIDATION_OUT = ART / "gdt495_validation.json"

GUARD = "KEINE OBERFLÄCHENVORHERSAGE"
STATUS = "TWENTY_SEVEN_TIER_A_CARDS_READY__ONE_HUNDRED_THIRTY_EIGHT_SUPPORT_CELLS_VISIBLE__ZERO_SURFACE_PREDICTIONS"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def pages_from(rows: list[dict[str, str]]) -> list[str]:
    pages: set[str] = set()
    for row in rows:
        pages.update(page for page in row["pages"].split("|") if page)
    return sorted(pages, key=page_key)


def group_by_target(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["target_realization_cell_id"]].append(row)
    return grouped


def main() -> int:
    tier_fields, tier_rows = read_tsv(TIER_A_PATH)
    nontr_fields, nontr_rows = read_tsv(NONTR_PATH)
    opposite_fields, opposite_rows = read_tsv(OPPOSITE_PATH)
    cross_fields, cross_rows = read_tsv(CROSS_PATH)
    card_fields, cards = read_tsv(CARD_PATH)
    nontr_out_fields, nontr_out = read_tsv(NONTR_OUT)
    opposite_out_fields, opposite_out = read_tsv(OPPOSITE_OUT)
    cross_out_fields, cross_out = read_tsv(CROSS_OUT)
    _register_fields, register_rows = read_tsv(REGISTER_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    target_ids = {row["source_realization_cell_id"] for row in tier_rows}
    tier_by_target = {row["source_realization_cell_id"]: row for row in tier_rows}
    expected_nontr = [row for row in nontr_rows if row["target_realization_cell_id"] in target_ids]
    expected_opposite = [row for row in opposite_rows if row["target_realization_cell_id"] in target_ids]
    expected_cross = [row for row in cross_rows if row["target_realization_cell_id"] in target_ids]
    expected_nontr_by_target = group_by_target(expected_nontr)
    expected_opposite_by_target = group_by_target(expected_opposite)
    expected_cross_by_target = group_by_target(expected_cross)

    check("tier_a_source_has_27_rows", len(tier_rows) == 27, f"rows={len(tier_rows)}")
    check("tier_a_source_unique_targets", len(target_ids) == 27, f"targets={len(target_ids)}")
    check(
        "tier_a_source_all_multihead",
        all(row["priority_tier"] == "A_MULTIHEAD_SAME_REGISTER" and int(row["same_register_nontr_head_count"]) >= 2 for row in tier_rows),
        "all source rows must remain GDT494 Tier A",
    )
    check("card_output_has_27_rows", len(cards) == 27, f"rows={len(cards)}")
    check("card_output_unique_ids", len({row["future_card_id"] for row in cards}) == 27, "future-card IDs")
    check(
        "card_output_exact_id_sequence",
        [row["future_card_id"] for row in cards] == [f"G495-F{index:03d}" for index in range(1, 28)],
        "G495-F001..G495-F027",
    )
    check(
        "card_output_exact_priority_sequence",
        [int(row["priority_rank"]) for row in cards] == list(range(1, 28)),
        "ranks 1..27",
    )
    check("local_nontr_subset_has_86_rows", len(expected_nontr) == len(nontr_out) == 86, f"source={len(expected_nontr)} output={len(nontr_out)}")
    check("opposite_tr_subset_has_9_rows", len(expected_opposite) == len(opposite_out) == 9, f"source={len(expected_opposite)} output={len(opposite_out)}")
    check("cross_register_subset_has_43_rows", len(expected_cross) == len(cross_out) == 43, f"source={len(expected_cross)} output={len(cross_out)}")
    check("local_nontr_header_preserved", nontr_out_fields[2:] == nontr_fields, "two card columns plus exact GDT494 header")
    check("opposite_tr_header_preserved", opposite_out_fields[2:] == opposite_fields, "two card columns plus exact GDT494 header")
    check("cross_register_header_preserved", cross_out_fields[2:] == cross_fields, "two card columns plus exact GDT494 header")

    rank_by_target = {row["source_realization_cell_id"]: index for index, row in enumerate(tier_rows, start=1)}
    card_id_by_target = {target: f"G495-F{rank:03d}" for target, rank in rank_by_target.items()}

    def support_output_matches(
        label: str,
        source_rows: list[dict[str, str]],
        output_rows: list[dict[str, str]],
        source_fields: list[str],
    ) -> None:
        normalized: list[dict[str, str]] = []
        metadata_ok = True
        for row in output_rows:
            target = row["target_realization_cell_id"]
            metadata_ok &= row["future_card_id"] == card_id_by_target[target]
            metadata_ok &= int(row["priority_rank"]) == rank_by_target[target]
            normalized.append({field: row[field] for field in source_fields})
        check(f"{label}_card_metadata_exact", metadata_ok, "card ID and priority retained")
        check(f"{label}_rows_exact", normalized == source_rows, "all selected GDT494 fields and row order retained")

    support_output_matches("local_nontr", expected_nontr, nontr_out, nontr_fields)
    support_output_matches("opposite_tr", expected_opposite, opposite_out, opposite_fields)
    support_output_matches("cross_register", expected_cross, cross_out, cross_fields)

    card_required_fields = {
        "future_card_id",
        "priority_rank",
        "source_realization_cell_id",
        "portable_component_trace_de",
        "owner_local_slot_trace_de",
        "working_phrase_de",
        "local_nontr_support_details_de",
        "opposite_tr_support_details_de",
        "same_action_cross_register_details_de",
        "all_old_pages",
        "comparison_guard",
    }
    check("card_schema_complete", card_required_fields <= set(card_fields), f"fields={len(card_fields)}")

    for index, card in enumerate(cards, start=1):
        target = card["source_realization_cell_id"]
        source = tier_by_target[target]
        local = expected_nontr_by_target[target]
        opposite = expected_opposite_by_target[target]
        cross = expected_cross_by_target[target]
        all_support = [*local, *opposite, *cross]
        expected_local_roots = "|".join(row["alternate_action_root"] for row in local)
        expected_cross_registers = "|".join(row["observed_other_register"] for row in cross)
        expected_all_pages = "|".join(pages_from(all_support))

        preserved_fields = {
            "frozen_frame": "frozen_frame",
            "action_root": "action_root",
            "action_recipe": "action_recipe",
            "register": "register",
            "portable_component_trace_de": "portable_component_trace_de",
            "owner_local_slot_trace_de": "owner_local_slot_trace_de",
            "working_phrase_de": "composed_working_phrase_de",
            "evidence_status_retained": "evidence_status_retained",
            "state_requirement": "state_requirement",
            "state_warning": "state_warning",
            "all_slot_values_old": "all_slot_values_old",
            "composed_working_label_retained": "composed_working_label_retained",
        }
        check(
            f"card_{index:02d}_source_fields_preserved",
            all(card[output_field] == source[source_field] for output_field, source_field in preserved_fields.items()),
            target,
        )
        check(
            f"card_{index:02d}_local_support_complete",
            int(card["local_nontr_head_count"]) == len(local)
            and int(card["local_nontr_support_cell_count"]) == len(local)
            and int(card["local_nontr_event_count"]) == sum(int(row["event_count"]) for row in local)
            and card["local_nontr_roots"] == expected_local_roots
            and set(card["local_nontr_pages"].split("|")) == set(pages_from(local)),
            f"{target}: cells={len(local)} roots={expected_local_roots}",
        )
        check(
            f"card_{index:02d}_opposite_support_complete",
            int(card["opposite_tr_support_cell_count"]) == len(opposite)
            and int(card["opposite_tr_event_count"]) == sum(int(row["event_count"]) for row in opposite)
            and card["opposite_tr_observed"] == ("YES" if opposite else "NO")
            and card["opposite_tr_root"] == (opposite[0]["alternate_action_root"] if opposite else "NONE"),
            f"{target}: cells={len(opposite)}",
        )
        check(
            f"card_{index:02d}_cross_register_support_complete",
            int(card["same_action_cross_register_cell_count"]) == len(cross)
            and int(card["same_action_cross_register_event_count"]) == sum(int(row["event_count"]) for row in cross)
            and card["same_action_cross_registers"] == expected_cross_registers,
            f"{target}: cells={len(cross)} registers={expected_cross_registers}",
        )
        check(
            f"card_{index:02d}_combined_support_complete",
            int(card["all_support_cell_count"]) == len(all_support)
            and int(card["all_support_event_count"]) == sum(int(row["event_count"]) for row in all_support)
            and int(card["all_old_page_count"]) == len(pages_from(all_support))
            and card["all_old_pages"] == expected_all_pages,
            f"{target}: support={len(all_support)} pages={expected_all_pages}",
        )
        check(
            f"card_{index:02d}_guard_and_labels_retained",
            card["comparison_guard"] == GUARD
            and card["surface_prediction_made"] == "NO"
            and card["occurrence_prediction_made"] == "NO"
            and card["evidence_status_retained"] == "COMPOSED_WORKING"
            and card["composed_working_label_retained"] == "YES",
            target,
        )
        expected_support_ids = [row["support_cell_id"] for row in [*local, *opposite]] + [row["cross_register_cell_id"] for row in cross]
        check(
            f"card_{index:02d}_readable_card_complete",
            card["future_card_id"] in readable
            and card["working_phrase_de"] in readable
            and all(support_id in readable for support_id in expected_support_ids),
            f"{target}: readable card plus {len(expected_support_ids)} witness IDs",
        )

    all_support = [*expected_nontr, *expected_opposite, *expected_cross]
    all_pages = pages_from(all_support)
    check("all_local_support_roundtrip_exact", all(row["all_roundtrip_exact"] == "YES" and row["exact_same_register_frame_support"] == "YES" for row in [*expected_nontr, *expected_opposite]), "95 local cells")
    check("all_cross_anchors_exact", all(row["same_action_and_formal_frame"] == "YES" and row["exact_observed_other_register_cell"] == "YES" for row in expected_cross), "43 cross-register cells")
    check("all_27_cards_have_two_nontr_heads", all(int(row["local_nontr_head_count"]) >= 2 for row in cards), "27/27")
    check("all_27_cards_have_cross_register_anchor", all(int(row["same_action_cross_register_cell_count"]) >= 1 for row in cards), "27/27")
    check("all_27_cards_keep_old_slots", all(row["all_slot_values_old"] == "YES" for row in cards), "27/27")
    check("all_27_cards_keep_composed_label", all(row["composed_working_label_retained"] == "YES" for row in cards), "27/27")
    check("zero_surface_predictions", all(row["surface_prediction_made"] == "NO" for row in cards), "0/27")
    check("zero_occurrence_predictions", all(row["occurrence_prediction_made"] == "NO" for row in cards), "0/27")
    check("readable_guard_occurs_27_times", readable.count(f"**{GUARD}**") == 27, f"count={readable.count(f'**{GUARD}**')}")
    check("readable_has_27_ranked_sections", len(re.findall(r"^## \d{2}\. G495-F\d{3}", readable, flags=re.MULTILINE)) == 27, "ranked card sections")
    check("readable_mentions_all_support_cells", all(row["support_cell_id"] in readable for row in [*expected_nontr, *expected_opposite]) and all(row["cross_register_cell_id"] in readable for row in expected_cross), "138 support IDs")
    check("readable_contains_no_forbidden_f84", "f84" not in readable.lower(), "sealed folio absent")

    check("register_output_has_five_rows", len(register_rows) == 5, f"rows={len(register_rows)}")
    check("register_output_covers_27_cards", sum(int(row["future_card_count"]) for row in register_rows) == 27, "summed cards")
    check("register_output_covers_86_nontr_cells", sum(int(row["local_nontr_support_cell_count"]) for row in register_rows) == 86, "summed local cells")
    check("register_output_covers_43_cross_cells", sum(int(row["cross_register_anchor_cell_count"]) for row in register_rows) == 43, "summed cross cells")
    check("register_output_guard_complete", all(row["comparison_guard"] == GUARD for row in register_rows), "5/5")

    expected_result = {
        "status": STATUS,
        "tier_a_future_cards": 27,
        "local_nontr_support_cells": 86,
        "local_nontr_support_events": sum(int(row["event_count"]) for row in expected_nontr),
        "opposite_tr_support_cells": 9,
        "opposite_tr_support_events": sum(int(row["event_count"]) for row in expected_opposite),
        "cross_register_anchor_cells": 43,
        "cross_register_anchor_events": sum(int(row["event_count"]) for row in expected_cross),
        "all_visible_support_cells": 138,
        "all_visible_support_events": sum(int(row["event_count"]) for row in all_support),
        "unique_old_support_pages": len(all_pages),
        "old_support_pages": all_pages,
        "state_warning_cards": sum(row["state_warning"] != "NONE" for row in cards),
        "self_contained_cards": sum(row["state_warning"] == "NONE" for row in cards),
        "cards_with_two_or_more_local_nontr_heads": 27,
        "cards_with_cross_register_anchor": 27,
        "cards_with_all_old_slot_values": 27,
        "cards_retaining_composed_label": 27,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "comparison_guard": GUARD,
    }
    check("result_exact", result == expected_result, "result JSON reconstructed from source and card outputs")
    check("result_has_24_old_support_pages", result["unique_old_support_pages"] == 24, f"pages={result['unique_old_support_pages']}")
    check("result_has_9_state_warning_cards", result["state_warning_cards"] == 9, f"cards={result['state_warning_cards']}")
    check("result_has_329_visible_support_events", result["all_visible_support_events"] == 329, f"events={result['all_visible_support_events']}")
    check("source_header_still_complete", "priority_tier" in tier_fields and "surface_prediction_made" in tier_fields, "GDT494 source schema")

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
