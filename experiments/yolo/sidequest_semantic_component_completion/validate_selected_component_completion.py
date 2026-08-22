#!/usr/bin/env python3
"""Validate the selected creative component-completion edition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICT = HERE / "SELECTED_173_COMPONENT_COMPLETE_DICTIONARY.tsv"
EVENTS = HERE / "SELECTED_381_COMPONENT_COMPLETE_INTERLINEAR.tsv"
STATEMENTS = HERE / "SELECTED_116_COMPONENT_COMPLETE_STATEMENTS.tsv"
COMPONENTS = HERE / "SELECTED_COMPONENT_LEXICON_V2.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
Y_AUDIT = HERE / "Y_CHY_PARADIGM.tsv"
P_AUDIT = HERE / "TRANSFER_ORDER_PARADIGM.tsv"
HOLD_AUDIT = HERE / "HOLD_CORES_PARADIGM.tsv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = value
    if not value:
        raise AssertionError(label)


def main() -> None:
    dictionary = rows(DICT)
    events = rows(EVENTS)
    statements = rows(STATEMENTS)
    components = rows(COMPONENTS)
    unresolved = rows(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    require(len(dictionary) == 173, "dictionary_173", checks)
    require(len(events) == 381, "events_381", checks)
    require(len(statements) == 116, "statements_116", checks)
    require(len({row["joint_tuple_id"] for row in dictionary}) == 173, "dictionary_ids_unique", checks)
    require([row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)], "event_order_complete", checks)
    require(set(row["page"] for row in events) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, "fixed_prose_pages_only", checks)
    require(not any(row["page"].startswith("f84") for row in events), "sealed_pages_absent", checks)

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(
        all(
            row["semantic_segmentation"] == by_id[row["joint_tuple_id"]]["semantic_segmentation"]
            and row["stable_concrete_nucleus_de"] == by_id[row["joint_tuple_id"]]["stable_concrete_nucleus_de"]
            and row["concrete_word_reading_de"] == by_id[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in events
        ),
        "event_dictionary_values_identical",
        checks,
    )
    require(all(row["concrete_word_reading_de"] and row["contextual_event_reading_de"] for row in events), "no_empty_event_readings", checks)

    changed_cards = [row for row in dictionary if row["component_completion_source"] != "UNCHANGED"]
    changed_events = [row for row in events if row["component_completion_source"] != "UNCHANGED"]
    require(len(changed_cards) == 21, "changed_cards_21", checks)
    require(len(changed_events) == 83, "changed_events_83", checks)
    require(sum(int(row["revised_event_count"]) > 0 for row in statements) == 60, "changed_statements_60", checks)
    require(
        {source: sum(row["component_completion_source"] == source for row in changed_cards) for source in ("Y_CHY", "TRANSFER_ORDER", "HOLD_CORES")}
        == {"Y_CHY": 12, "TRANSFER_ORDER": 2, "HOLD_CORES": 7},
        "source_card_counts_exact",
        checks,
    )
    require(
        {source: sum(row["component_completion_source"] == source for row in changed_events) for source in ("Y_CHY", "TRANSFER_ORDER", "HOLD_CORES")}
        == {"Y_CHY": 58, "TRANSFER_ORDER": 2, "HOLD_CORES": 23},
        "source_event_counts_exact",
        checks,
    )

    y_source_events = {
        row["event_id"]
        for row in rows(Y_AUDIT)
        if row["decision"].startswith("SELECTED_Y_REFERENT") or row["decision"] == "SELECTED_CHY_AS_WRAPPED_Y"
    }
    p_source_events = {row["event_ids"] for row in rows(P_AUDIT) if row["row_role"] == "TARGET" and row["joint_tuple_id"] in {"65df3cd9e59060042d47", "ba540da978ea132f6da5"}}
    hold_source_events = {
        event_id
        for row in rows(HOLD_AUDIT)
        if row["selection_status"].startswith("SELECTED_DEFAULT")
        for event_id in row["event_ids"].split("|")
    }
    require(y_source_events == {row["event_id"] for row in changed_events if row["component_completion_source"] == "Y_CHY"}, "y_audit_event_set_exact", checks)
    require(p_source_events == {row["event_id"] for row in changed_events if row["component_completion_source"] == "TRANSFER_ORDER"}, "transfer_audit_event_set_exact", checks)
    require(hold_source_events == {row["event_id"] for row in changed_events if row["component_completion_source"] == "HOLD_CORES"}, "hold_audit_event_set_exact", checks)

    expected = {
        "b921a237be883a820352": "der laufende Posten; dies oder es",
        "4a7a6326ac95a8809302": "den laufenden Posten an der Zielstelle einsetzen",
        "1322bc176443fc2a8a86": "den laufenden Posten erneut in Arbeit nehmen",
        "65df3cd9e59060042d47": "in den Empfänger einführen; Schluss",
        "ba540da978ea132f6da5": "Einfüllstelle",
        "bc4f1f5c006c74a4d26d": "kurz oder gewöhnlich ruhen lassen; Schluss",
        "03626ca94cb17800d767": "länger ruhen oder nachwirken lassen; Schluss",
        "d904bf7b044dd3922781": "kurz oder mild erwärmen",
        "2c1a5fd92b9e3c762242": "länger warm halten",
        "3b70942557b3a40e8030": "an der Sammelstelle stehen oder absetzen lassen; Schluss",
    }
    require(all(by_id[joint]["concrete_word_reading_de"] == gloss for joint, gloss in expected.items()), "named_selected_glosses_exact", checks)
    require("Y_REFERENT" in by_id["b921a237be883a820352"]["semantic_segmentation"], "base_y_is_referent", checks)
    require("open" not in by_id["b921a237be883a820352"]["stable_concrete_nucleus_de"].lower() and "offen" not in by_id["b921a237be883a820352"]["stable_concrete_nucleus_de"].lower(), "base_y_not_openness", checks)
    require("Y_REFERENT" not in by_id["d904bf7b044dd3922781"]["semantic_segmentation"] and "Y_REFERENT" not in by_id["2c1a5fd92b9e3c762242"]["semantic_segmentation"], "ky_boundary_not_split_as_y", checks)
    require("kräftig" not in by_id["1322bc176443fc2a8a86"]["concrete_word_reading_de"].lower(), "double_ok_not_intensity", checks)
    require("erneut" in by_id["1322bc176443fc2a8a86"]["concrete_word_reading_de"].lower(), "double_ok_is_repeat", checks)

    component_ids = {row["component_id"] for row in components}
    require("Y_STATE" not in component_ids and "Y_REFERENT" in component_ids, "component_y_renamed", checks)
    require("DY_STATE" not in component_ids and "DY_TERMINAL_CONSTRUCTION" in component_ids, "dy_kept_as_terminal_construction", checks)
    require({"SH_REST_GRADED_FAMILY", "CHK_WARMTH_PAIR", "OLK_SOLK_COLLECTION_STATION", "OK_REDUPLICATION", "OK_AL_Y_ORDER"}.issubset(component_ids), "new_component_families_present", checks)
    require(len(components) == 23, "component_rows_23", checks)
    require(len(unresolved) == 14, "remaining_unresolved_14", checks)
    unresolved_ids = {row["candidate_component"] for row in unresolved}
    require({"GLOBAL_P", "GLOBAL_SH", "GLOBAL_CHK", "GLOBAL_SOLK", "GENERAL_OK_REDUPLICATION", "GENERAL_OK_AL_Y_ORDER"}.issubset(unresolved_ids), "portability_limits_explicit", checks)

    statement_event_ids = [event_id for row in statements for event_id in row["event_ids"].split("|")]
    require(statement_event_ids == [row["event_id"] for row in events], "statement_event_coverage_and_order", checks)
    require(all(int(row["event_count"]) == len(row["event_ids"].split("|")) for row in statements), "statement_counts_exact", checks)
    require(summary["status"] == "PASS" and summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116, "summary_counts_and_status", checks)
    require(
        all(summary["outputs"][str(path.relative_to(ROOT))] == sha256(path) for path in (DICT, EVENTS, STATEMENTS, COMPONENTS, UNRESOLVED)),
        "summary_output_hashes_current",
        checks,
    )

    result = {
        "schema": "SIDEQUEST_SELECTED_COMPONENT_COMPLETION_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(statements),
            "changed_cards": len(changed_cards),
            "changed_events": len(changed_events),
            "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
            "components": len(components),
            "remaining_unresolved_rows": len(unresolved),
        },
    }
    output = HERE / "VALIDATION.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
