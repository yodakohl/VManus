#!/usr/bin/env python3
"""Validate the third-ring exception anatomy and rebuilt prose edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_reduced_complete_edition"
BUILDER = OUT / "build_exception_anatomy.py"

CONTENT_NAMES = [
    "EIGHT_LEARNED_BRIDGE_STEMS.tsv",
    "NINETEEN_EXCEPTION_REANALYSIS.tsv",
    "COMPLETE_173_THIRD_RING_DICTIONARY.tsv",
    "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv",
    "COMPLETE_116_THIRD_RING_STATEMENTS.tsv",
    "ELEVEN_RECORD_THIRD_RING_SUMMARY.tsv",
    "ELEVEN_RECORD_THIRD_RING_READING.md",
    "EXCEPTION_ANATOMY_REPORT.md",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    source_cards = read_tsv(BASE / "IMPERATIVE_173_CARD_DICTIONARY.tsv")
    source_events = read_tsv(BASE / "IMPERATIVE_381_EVENT_TRACE.tsv")
    source_statements = read_tsv(BASE / "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv")
    bridges = read_tsv(OUT / "EIGHT_LEARNED_BRIDGE_STEMS.tsv")
    exceptions = read_tsv(OUT / "NINETEEN_EXCEPTION_REANALYSIS.tsv")
    cards = read_tsv(OUT / "COMPLETE_173_THIRD_RING_DICTIONARY.tsv")
    events = read_tsv(OUT / "COMPLETE_381_THIRD_RING_EVENT_TRACE.tsv")
    statements = read_tsv(OUT / "COMPLETE_116_THIRD_RING_STATEMENTS.tsv")
    records = read_tsv(OUT / "ELEVEN_RECORD_THIRD_RING_SUMMARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    expected_bridge_cores = {"DCH", "CFH", "CPH", "DCHE", "LDDY", "SK", "DAN", "AM"}
    check("bridge_inventory_has_eight_unique_rows", len(bridges) == 8 and len({row["bridge_id"] for row in bridges}) == 8, len(bridges))
    check("bridge_cores_are_exact", {row["visible_core"] for row in bridges} == expected_bridge_cores, sorted(row["visible_core"] for row in bridges))
    check("bridge_cells_are_concrete_and_nonempty", all(all(value for value in row.values()) for row in bridges), len(bridges))

    expected_exception_ids = {row["master_card_id"] for row in source_cards if row["composition_layer"] == "LEARNED_LOCAL_WHOLE"}
    check("exception_table_has_nineteen_unique_cards", len(exceptions) == 19 and len({row["master_card_id"] for row in exceptions}) == 19, len(exceptions))
    check("exception_ids_match_old_whole_cards", {row["master_card_id"] for row in exceptions} == expected_exception_ids, sorted({row["master_card_id"] for row in exceptions} ^ expected_exception_ids))
    exception_classes = Counter(row["new_class"] for row in exceptions)
    check("exception_split_is_ten_eight_one", exception_classes == Counter({"COMPOSED_EXISTING_ATOMS": 10, "COMPOSED_WITH_BRIDGE_STEM": 8, "LEARNED_WHOLE_CARD": 1}), dict(exception_classes))
    whole_rows = [row for row in exceptions if row["new_class"] == "LEARNED_WHOLE_CARD"]
    check("dl_is_the_only_whole_card", len(whole_rows) == 1 and whole_rows[0]["master_card_id"] == "MC012" and whole_rows[0]["new_nucleus_de"] == "ZUSATZ", whole_rows)
    check("all_exception_imperatives_are_short", all(1 <= len(row["new_imperative_de"].split()) <= 9 for row in exceptions), max(len(row["new_imperative_de"].split()) for row in exceptions))

    source_card_fields = list(source_cards[0])
    check("dictionary_has_173_unique_cards", len(cards) == 173 and len({row["master_card_id"] for row in cards}) == 173, len(cards))
    check("dictionary_preserves_base_cells", all(all(new[field] == old[field] for field in source_card_fields) for old, new in zip(source_cards, cards, strict=True)), len(cards))
    card_classes = Counter(row["third_ring_class"] for row in cards)
    expected_card_classes = Counter({"PREVIOUSLY_COMPOSED": 154, "COMPOSED_EXISTING_ATOMS": 10, "COMPOSED_WITH_BRIDGE_STEM": 8, "LEARNED_WHOLE_CARD": 1})
    check("dictionary_class_counts_exact", card_classes == expected_card_classes, dict(card_classes))
    check("all_final_card_values_nonempty", all(row["third_ring_atom_sequence"] and row["third_ring_nucleus_de"] and row["third_ring_concrete_default_de"] and row["third_ring_imperative_de"] for row in cards), len(cards))
    old_overreads = {"ANSATZGEFÄSS", "KALT STELLEN", "ROH", "SCHWENKEN", "FRISCHWASSER", "NACHWASCHEN", "SAMMELGEFÄSS", "FUELLEN", "STAENGEL"}
    changed_exception_nuclei = {row["new_nucleus_de"] for row in exceptions if row["new_class"] != "LEARNED_WHOLE_CARD"}
    check("selected_old_overreads_removed_from_new_exception_nuclei", not old_overreads & changed_exception_nuclei, sorted(old_overreads & changed_exception_nuclei))

    source_event_fields = list(source_events[0])
    check("event_trace_has_381_unique_events", len(events) == 381 and len({row["event_id"] for row in events}) == 381, len(events))
    check("event_trace_preserves_base_cells", all(all(new[field] == old[field] for field in source_event_fields) for old, new in zip(source_events, events, strict=True)), len(events))
    card_by_id = {row["master_card_id"]: row for row in cards}
    check("event_readings_match_dictionary", all(row["third_ring_atom_sequence"] == card_by_id[row["master_card_id"]]["third_ring_atom_sequence"] and row["third_ring_nucleus_de"] == card_by_id[row["master_card_id"]]["third_ring_nucleus_de"] and row["third_ring_imperative_de"] == card_by_id[row["master_card_id"]]["third_ring_imperative_de"] for row in events), len(events))
    event_classes = Counter(row["third_ring_class"] for row in events)
    expected_event_classes = Counter({"PREVIOUSLY_COMPOSED": 360, "COMPOSED_EXISTING_ATOMS": 10, "COMPOSED_WITH_BRIDGE_STEM": 9, "LEARNED_WHOLE_CARD": 2})
    check("event_class_counts_exact", event_classes == expected_event_classes, dict(event_classes))
    check("three_hundred_seventy_nine_events_have_component_anatomy", len(events) - event_classes["LEARNED_WHOLE_CARD"] == 379, len(events) - event_classes["LEARNED_WHOLE_CARD"])

    source_statement_fields = list(source_statements[0])
    check("statement_edition_has_116_unique_rows", len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116, len(statements))
    check("statement_base_cells_preserved", all(all(new[field] == old[field] for field in source_statement_fields) for old, new in zip(source_statements, statements, strict=True)), len(statements))
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    check("statement_atom_chains_reconstruct", all(row["third_ring_atom_chain"] == " | ".join(event["third_ring_atom_sequence"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    check("statement_nucleus_chains_reconstruct", all(row["third_ring_nucleus_chain_de"] == " → ".join(event["third_ring_nucleus_de"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    check("statement_imperative_chains_reconstruct", all(row["third_ring_imperative_chain_de"] == "; ".join(event["third_ring_imperative_de"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    statement_status = Counter(row["third_ring_statement_status"] for row in statements)
    expected_statement_status = Counter({"FULLY_COMPOSED_EXISTING_ATOMS": 106, "COMPOSED_WITH_BRIDGE_STEM": 8, "CONTAINS_ONE_LEARNED_WHOLE_CARD": 2})
    check("statement_status_counts_exact", statement_status == expected_statement_status, dict(statement_status))
    check("exactly_sixteen_statements_rephrased", Counter(row["third_ring_revision"] for row in statements) == Counter({"REVISED": 16, "UNCHANGED": 100}), dict(Counter(row["third_ring_revision"] for row in statements)))
    check("all_fluent_readings_are_sentences", all(row["third_ring_fluent_reading_de"] and row["third_ring_fluent_reading_de"][-1] in ".!?" for row in statements), len(statements))
    check("event_counts_partition_statements", sum(int(row["event_count"]) for row in statements) == 381 and set(events_by_statement) == {row["statement_id"] for row in statements}, sum(int(row["event_count"]) for row in statements))

    expected_records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    check("record_summary_has_eleven_ordered_records", [row["record_unit_id"] for row in records] == expected_records, [row["record_unit_id"] for row in records])
    check("record_totals_exact", sum(int(row["statement_count"]) for row in records) == 116 and sum(int(row["event_count"]) for row in records) == 381, f"{sum(int(row['statement_count']) for row in records)}/{sum(int(row['event_count']) for row in records)}")
    check("record_status_totals_exact", sum(int(row["fully_existing_atom_statements"]) for row in records) == 106 and sum(int(row["bridge_stem_statements"]) for row in records) == 8 and sum(int(row["whole_card_statements"]) for row in records) == 2, f"{sum(int(row['fully_existing_atom_statements']) for row in records)}/{sum(int(row['bridge_stem_statements']) for row in records)}/{sum(int(row['whole_card_statements']) for row in records)}")
    check("record_continuous_text_reconstructs", all(row["continuous_third_ring_reading_de"] == " ".join(statement["third_ring_fluent_reading_de"] for statement in statements if statement["record_unit_id"] == row["record_unit_id"]) for row in records), len(records))

    readable = (OUT / "ELEVEN_RECORD_THIRD_RING_READING.md").read_text(encoding="utf-8")
    check("readable_edition_contains_all_statement_ids", all(f"**{row['statement_id']} · {row['loci']}**" in readable for row in statements), len(statements))
    check("readable_edition_contains_all_surface_sequences", all(f"`{row['surface_sequence']}`" in readable for row in statements), len(statements))
    check("readable_edition_has_eleven_sections", len(re.findall(r"^## [HB][1-6] —", readable, flags=re.MULTILINE)) == 11, len(re.findall(r"^## [HB][1-6] —", readable, flags=re.MULTILINE)))

    expected_summary = {
        "status": "BUILT",
        "bridge_stems": 8,
        "reanalyzed_cards": 19,
        "master_cards": 173,
        "prose_events": 381,
        "statements": 116,
        "records": 11,
    }
    check("summary_counts_exact", all(summary.get(key) == value for key, value in expected_summary.items()), {key: summary.get(key) for key in expected_summary})
    check("summary_class_counts_exact", summary.get("card_class_counts") == dict(card_classes) and summary.get("event_class_counts") == dict(event_classes) and summary.get("statement_status_counts") == dict(statement_status), "card/event/statement")
    check("summary_output_hashes_exact", all(summary["output_sha256"].get(name) == digest(OUT / name) for name in CONTENT_NAMES), len(CONTENT_NAMES))

    sealed_pattern = re.compile(r"(?<![A-Za-z0-9])f" + "84" + r"(?:r|v)?(?![A-Za-z0-9])", re.IGNORECASE)
    sealed_hits = [name for name in CONTENT_NAMES if sealed_pattern.search((OUT / name).read_text(encoding="utf-8"))]
    check("sealed_pages_absent_from_outputs", not sealed_hits, sealed_hits)

    before = {name: digest(OUT / name) for name in CONTENT_NAMES + ["BUILD_SUMMARY.json"]}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {name: digest(OUT / name) for name in CONTENT_NAMES + ["BUILD_SUMMARY.json"]}
    check("deterministic_rebuild_is_byte_identical", before == after, "byte-identical" if before == after else sorted(name for name in before if before[name] != after[name]))
    check("builder_reports_built", '"status": "BUILT"' in rebuilt.stdout, rebuilt.stdout.splitlines()[0] if rebuilt.stdout else "NO_OUTPUT")

    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [item["name"] for item in failed],
        "counts": expected_summary,
        "checks": checks,
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "checks_passed", "checks_total", "failed_checks", "counts")}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
