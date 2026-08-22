#!/usr/bin/env python3
"""Validate the creative quantity/preparation working edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICT = HERE / "SELECTED_173_QUANTITY_PREPARATION_DICTIONARY.tsv"
EVENTS = HERE / "SELECTED_381_QUANTITY_PREPARATION_INTERLINEAR.tsv"
STATEMENTS = HERE / "SELECTED_116_WORKSHOP_SENTENCES.tsv"
RICH_SLOTS = HERE / "WORKSHOP_SENTENCE_SLOTS.tsv"
RECORDS = HERE / "SELECTED_11_WORKSHOP_RECORDS.md"
COMPONENTS = HERE / "SELECTED_QUANTITY_PREPARATION_COMPONENTS.tsv"
COMPOSITIONS = HERE / "SELECTED_COMPOSITION_TABLE.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED_AFTER_QUANTITY.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = condition
    if not condition:
        raise AssertionError(label)


def main() -> None:
    dictionary = rows(DICT)
    events = rows(EVENTS)
    statements = rows(STATEMENTS)
    rich_slots = rows(RICH_SLOTS)
    components = rows(COMPONENTS)
    compositions = rows(COMPOSITIONS)
    unresolved = rows(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    require(len(dictionary) == 173, "dictionary_173", checks)
    require(len(events) == 381, "events_381", checks)
    require(len(statements) == 116, "statements_116", checks)
    require(len(rich_slots) == 116, "rich_slot_statements_116", checks)
    require(len({row["joint_tuple_id"] for row in dictionary}) == 173, "dictionary_ids_unique", checks)
    require([row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)], "event_order_complete", checks)
    require(set(row["page"] for row in events) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, "fixed_prose_pages_only", checks)
    require(not any(row["page"].startswith("f84") for row in events), "sealed_pages_absent", checks)

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(all(row["joint_tuple_id"] in by_id for row in events), "all_events_have_card", checks)
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
    require(all(row["concrete_word_reading_de"].strip() and row["contextual_event_reading_de"].strip() for row in events), "no_empty_event_readings", checks)
    forbidden = re.compile(r"^(UNKNOWN|UNBEKANNT|EXEMPLAR|FORMAL)(?:$|[_ ;])", re.IGNORECASE)
    require(not any(forbidden.search(row["concrete_word_reading_de"].strip()) for row in dictionary), "no_placeholder_default_gloss", checks)

    expected = {
        "9da1b6ac2c929daea697": "eine Portion",
        "1645e612504fcef59ced": "eine Portion zugeben",
        "94df4847b7b16c98394a": "eine weitere Portion zugeben",
        "d784b2abcaf1a3703de2": "eine Portion umsetzen",
        "2f1c5e56e8f0ff459065": "vorgeschriebenes Maß",
        "b5fcea1eaed06b2f2291": "auf das vorgeschriebene Maß einstellen",
        "54d0e228ca346110af05": "das nächste Maß",
        "2c82523794dcb7d2b343": "vorgeschriebener Grad",
        "7a4bb8136330ee4e6e56": "Zubereitung",
        "dec401773c1f0347793d": "mit der vorigen Zubereitung",
        "10488b911aae52b3b334": "die nächste Zubereitung",
        "b9d7b6d68209a9019e7a": "Pflanzenzubereitung",
        "6afeb5c9ab9f6cbdea0d": "eine Portion der Zubereitung",
        "497cbd9c7401810ff56b": "danach weiter",
    }
    require(all(by_id[ident]["concrete_word_reading_de"] == gloss for ident, gloss in expected.items()), "core_compositions_exact", checks)
    require(by_id["53cd0637c6820ba5e91f"]["concrete_word_reading_de"] == "durch Tuch", "dain_whole_card_not_false_ain", checks)
    require(by_id["1779decef17481ec2853"]["concrete_word_reading_de"] == "breites Gefäß", "qotedaiin_whole_card_retained", checks)
    require(by_id["f3c23f42baf625639e1e"]["concrete_word_reading_de"] == "Kraut zerstoßen", "cthaiin_whole_card_retained", checks)
    require(by_id["2d2e37ccb2dacc53ee5a"]["concrete_word_reading_de"] == "durch Tuch", "solkaiin_whole_card_retained", checks)
    require(by_id["27d97af8c96eb056c2e6"]["concrete_word_reading_de"] == "glasiertes Gefäß", "oykchor_not_false_or", checks)
    require(by_id["7249edc4df3419c26999"]["concrete_word_reading_de"] == "Pflanzenspitzen", "ycheor_not_false_or", checks)
    require(by_id["403c1592f918c8f23b88"]["concrete_word_reading_de"] == "eine Portion des laufenden Postens", "ykain_quantity_extension", checks)
    require(by_id["d929a14ec45749b2e805"]["concrete_word_reading_de"] == "diese Portion", "ykan_quantity_extension", checks)
    require(by_id["f7dc90b2c31fd341f0a4"]["concrete_word_reading_de"] == "Maß des laufenden Postens", "ykaiin_measure_extension", checks)
    require(by_id["cbb42a4fe68068325d6b"]["concrete_word_reading_de"] == "sauberes Wasser zugeben; Schluss", "dshedy_close_repaired", checks)
    require(by_id["7f68f60279efe6b28cd7"]["concrete_word_reading_de"] == "Teil als Waschung; Schluss", "rshedy_close_repaired", checks)

    comp_by_id = {row["component_id"]: row for row in components}
    require(comp_by_id["AIN"]["working_meaning_de"] == "Teil; abgeteilte Portion", "ain_distinct_exact", checks)
    require(comp_by_id["AIIN"]["working_meaning_de"] == "Maß; vorgeschriebene Menge", "aiin_distinct_exact", checks)
    require(comp_by_id["IIN_GRADE"]["working_meaning_de"] == "Grad; Arbeitsstufe oder Einstellung", "iin_distinct_exact", checks)
    require(comp_by_id["OR_PREPARATION"]["working_meaning_de"] == "Zubereitung; bereiteter Ansatz", "or_exact", checks)
    require(len(compositions) == 14, "composition_rows_14", checks)
    require({row["family"] for row in compositions} == {"AIN", "OK+AIN", "OL+AIN", "CHED+AIN", "AIIN", "OK+AIIN", "OT+AIIN", "IIN", "OR", "OL+OR", "OT+OR", "CHO+OR", "OR+AIN", "OT+OL"}, "composition_families_exact", checks)

    statement_events = [event for row in statements for event in row["event_ids"].split("|")]
    require(statement_events == [row["event_id"] for row in events], "statement_event_coverage_and_order", checks)
    require(all(int(row["event_count"]) == len(row["event_ids"].split("|")) for row in statements), "statement_counts_exact", checks)
    require(all(row["event_slot_trace"] and row["canonical_slots_present"] and row["workshop_sentence_de"] for row in statements), "statement_readings_and_slots_complete", checks)
    slot_names = {slot for row in events for slot in row["workshop_slots"].split("+")}
    require(slot_names.issubset({"OWNER_ITEM", "SOURCE", "QUANTITY", "PREPARATION", "OPERATION", "FLOW_TRANSFER", "TARGET", "STATE_GRADE", "CLOSE"}), "slot_vocabulary_closed", checks)
    require("QUANTITY" in slot_names and "PREPARATION" in slot_names and "CLOSE" in slot_names, "core_slots_present", checks)
    require([row["statement_id"] for row in rich_slots] == [row["statement_id"] for row in statements], "rich_slot_statement_order", checks)
    require([event for row in rich_slots for event in row["event_ids"].split("|")] == [row["event_id"] for row in events], "rich_slot_event_coverage_and_order", checks)
    require(sum(not row["close_slot"].startswith("OFFEN") for row in rich_slots) == 89, "closed_statements_89", checks)
    require(sum(row["close_slot"].startswith("OFFEN") for row in rich_slots) == 27, "open_statements_27", checks)
    require(sum(row["line_continuity"] == "CROSSES_PHYSICAL_LINE" for row in rich_slots) == 18, "line_crossing_statements_18", checks)

    record_text = RECORDS.read_text(encoding="utf-8")
    require(set(re.findall(r"^## ([HB]\d+) —", record_text, flags=re.MULTILINE)) == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}, "record_sections_11", checks)
    require(set(re.findall(r"\*\*([HB]\d+-S\d{3})\*\*", record_text)) == {row["statement_id"] for row in statements}, "record_statement_coverage", checks)
    require("GEGENSTAND → QUELLE → MENGE → ZUBEREITUNG → ARBEITSGANG → LAUF → ZIEL → GRAD → SCHLUSS" in record_text, "workshop_template_published", checks)

    changed_cards = [row for row in dictionary if row["quantity_revision_source"] != "UNCHANGED"]
    changed_events = [row for row in events if row["quantity_revision_source"] != "UNCHANGED"]
    require(len(changed_cards) == summary["changed_cards"] and len(changed_events) == summary["changed_events"], "changed_counts_match_summary", checks)
    require(len(unresolved) == summary["remaining_unresolved_rows"], "unresolved_count_matches_summary", checks)
    require({"IIN_LOCAL_DIMENSION", "LONG_AIIN_HULLS", "OR_INTERNAL_STRINGS"}.issubset({row["candidate_component"] for row in unresolved}), "remaining_limits_explicit", checks)
    require(summary["status"] == "PASS" and summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116 and summary["records"] == 11, "summary_counts_and_status", checks)
    paths = (DICT, EVENTS, STATEMENTS, RICH_SLOTS, RECORDS, COMPONENTS, COMPOSITIONS, UNRESOLVED)
    require(all(summary["outputs"][str(path.relative_to(ROOT))] == sha256(path) for path in paths), "summary_output_hashes_current", checks)

    result = {
        "schema": "SIDEQUEST_SELECTED_QUANTITY_PREPARATION_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "counts": {
            "cards": len(dictionary), "events": len(events), "statements": len(statements), "records": 11,
            "rich_slot_statements": len(rich_slots),
            "changed_cards": len(changed_cards), "changed_events": len(changed_events),
            "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
            "components": len(components), "composition_rows": len(compositions),
            "remaining_unresolved_rows": len(unresolved),
        },
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
