#!/usr/bin/env python3
"""Validate the selected creative filtration/separation edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICT = HERE / "SELECTED_173_FILTRATION_DICTIONARY.tsv"
EVENT = HERE / "SELECTED_381_FILTRATION_INTERLINEAR.tsv"
STATEMENT = HERE / "SELECTED_116_FILTRATION_SENTENCES.tsv"
RECORDS = HERE / "SELECTED_11_FILTRATION_RECORDS.md"
COMPONENT = HERE / "SELECTED_FILTRATION_COMPONENTS.tsv"
PARADIGM = HERE / "SELECTED_FILTRATION_PARADIGM.tsv"
CHAINS = HERE / "SELECTED_PROCESS_CHAINS.tsv"
COUNTERS = HERE / "FILTRATION_COUNTEREXAMPLES.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED_AFTER_FILTRATION.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
BUILDER = HERE / "build_selected_filtration_separation.py"
VALIDATION = HERE / "VALIDATION.json"

ROLE_TABLES = {
    "historical": (HERE / "HISTORICAL_FILTRATION_PARADIGM.tsv", 59, 107),
    "draughtsman": (HERE / "DRAUGHTSMAN_FILTRATION_PARADIGM.tsv", 52, 92),
    "workshop": (HERE / "WORKSHOP_FILTRATION_PARADIGM.tsv", 87, 148),
}

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
EXPECTED_OVERRIDE_IDS = {
    "2cc8bb3c2af19607888f",
    "d68bc8de3bcee09db23c",
    "c1db6b0a28d5cbb5d3d2",
    "be0974b366c981dc1eef",
    "2e7e89e0bd12b999c280",
    "d4a31dbcf1ed6d9e5aa9",
    "b5df9126607030b95175",
    "42cdc187d5b9ffc60063",
    "1bfd786e6b8b63734a59",
    "3b70942557b3a40e8030",
    "62ff059766b21c7de083",
    "e026af581c99322fbd46",
    "53cd0637c6820ba5e91f",
    "2d2e37ccb2dacc53ee5a",
    "af816c04e65874a0f2fa",
    "75a523fcf039b006f97b",
    "bdad9f9ea8b80f141496",
    "deb377381ceaf55ea310",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    dictionary = read_tsv(DICT)
    events = read_tsv(EVENT)
    statements = read_tsv(STATEMENT)
    components = read_tsv(COMPONENT)
    paradigm = read_tsv(PARADIGM)
    chains = read_tsv(CHAINS)
    counters = read_tsv(COUNTERS)
    unresolved = read_tsv(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check("dictionary_count", len(dictionary) == 173, len(dictionary))
    check("event_count", len(events) == 381, len(events))
    check("statement_count", len(statements) == 116, len(statements))
    check("record_count", len({row["record_unit_id"] for row in statements}) == 11, len({row["record_unit_id"] for row in statements}))
    check("component_count", len(components) == 34, len(components))
    check("paradigm_count", len(paradigm) == 18, len(paradigm))
    check("chain_count", len(chains) == 18, len(chains))
    check("counterexample_count", len(counters) == 9, len(counters))
    check("unresolved_count", len(unresolved) == 22, len(unresolved))

    dictionary_ids = [row["joint_tuple_id"] for row in dictionary]
    check("dictionary_unique_ids", len(dictionary_ids) == len(set(dictionary_ids)), len(set(dictionary_ids)))
    check("event_ids_unique", len({row["event_id"] for row in events}) == 381, len({row["event_id"] for row in events}))
    check("event_serials_contiguous", [int(row["event_serial"]) for row in events] == list(range(1, 382)), events[-1]["event_serial"])
    check("allowed_pages_only", {row["page"] for row in events} == ALLOWED_PAGES, sorted({row["page"] for row in events}))
    check("no_blank_dictionary_values", all(row["concrete_word_reading_de"].strip() for row in dictionary), "173 checked")
    check("no_blank_event_values", all(row["concrete_word_reading_de"].strip() for row in events), "381 checked")
    check("no_unknown_defaults", not any("UNKNOWN" in row["concrete_word_reading_de"].upper() for row in dictionary), "all defaults concrete")

    by_card = {row["joint_tuple_id"]: row for row in dictionary}
    card_event_counts = Counter(row["joint_tuple_id"] for row in events)
    check("all_events_have_dictionary_card", set(card_event_counts) == set(by_card), len(card_event_counts))
    check("dictionary_occurrence_counts", all(int(row["occurrences"]) == card_event_counts[row["joint_tuple_id"]] for row in dictionary), "173 checked")
    check(
        "event_dictionary_values_match",
        all(
            row["semantic_segmentation"] == by_card[row["joint_tuple_id"]]["semantic_segmentation"]
            and row["concrete_word_reading_de"] == by_card[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in events
        ),
        "381 checked",
    )

    changed_cards = [row for row in dictionary if row["filtration_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in events if row["filtration_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["filtration_revised_event_count"]) > 0]
    check("override_identity_set", {row["joint_tuple_id"] for row in changed_cards} == EXPECTED_OVERRIDE_IDS, len(changed_cards))
    check("changed_card_count", len(changed_cards) == 18, len(changed_cards))
    check("changed_event_count", len(changed_events) == 30, len(changed_events))
    check("changed_statement_count", len(changed_statements) == 24, len(changed_statements))

    statement_event_ids: list[str] = []
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    for row in statements:
        ids = row["event_ids"].split("|")
        statement_event_ids.extend(ids)
        check("statement_count_" + row["statement_id"], int(row["event_count"]) == len(ids), len(ids))
    check("statement_event_partition", statement_event_ids == [row["event_id"] for row in events], len(statement_event_ids))
    check("statement_ids_unique", len({row["statement_id"] for row in statements}) == 116, len({row["statement_id"] for row in statements}))

    paradigm_ids = [row["joint_tuple_id"] for row in paradigm]
    check("paradigm_exact_override_set", set(paradigm_ids) == EXPECTED_OVERRIDE_IDS, len(set(paradigm_ids)))
    check("paradigm_event_counts", all(int(row["events"]) == card_event_counts[row["joint_tuple_id"]] for row in paradigm), "18 checked")
    check("paradigm_all_values_short", all(len(row["selected_reading_de"].split()) <= 5 for row in paradigm), max(len(row["selected_reading_de"].split()) for row in paradigm))

    close_ids = {row["joint_tuple_id"] for row in paradigm if "CLOSED" in row["process_role"]}
    close_events = [row for row in events if row["joint_tuple_id"] in close_ids]
    check(
        "new_close_events_statement_final",
        all(events_by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in close_events),
        len(close_events),
    )
    check("new_close_values_mark_close", all("schluss" in row["concrete_word_reading_de"].lower() for row in close_events), len(close_events))

    clear_id = "b5df9126607030b95175"
    check("clear_extract_default", by_card[clear_id]["concrete_word_reading_de"] == "Klarauszug", by_card[clear_id]["concrete_word_reading_de"])
    check("clear_extract_four_events", card_event_counts[clear_id] == 4, card_event_counts[clear_id])
    check("dain_is_cloth_not_measure", by_card["53cd0637c6820ba5e91f"]["concrete_word_reading_de"] == "Tuch", by_card["53cd0637c6820ba5e91f"]["concrete_word_reading_de"])
    check("tshey_is_rinse_liquid", by_card["d4a31dbcf1ed6d9e5aa9"]["concrete_word_reading_de"] == "Spülflüssigkeit", by_card["d4a31dbcf1ed6d9e5aa9"]["concrete_word_reading_de"])
    check("h3_complete_chain", next(row for row in chains if row["statement_id"] == "H3-S001")["process_stages_de"] == "auswringen → stehen lassen → nachseihen → Klarauszug → abkühlen", "H3-S001")
    check("h3_surface_sequence_preserved", next(row for row in chains if row["statement_id"] == "H3-S001")["surface_sequence"] == "tshol · schoal · cfhy · shfydaiin · cphy · shey · tchody", "H3-S001")

    counter_by_name = {row["counterexample"]: row for row in counters}
    check("ckh_boundary_present", "CKH_NOT_GLOBAL" in counter_by_name, sorted(counter_by_name))
    check("chk_order_control_present", "CHK_ORDER_CONTROL" in counter_by_name, sorted(counter_by_name))
    check("cloth_deck_no_fake_root", "CLOTH_DECK_NO_SHARED_ROOT" in counter_by_name, sorted(counter_by_name))
    check("records_markdown_complete", sum(1 for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.startswith("## ")) == 11, "11 headings")

    for role, (path, expected_rows, expected_events) in ROLE_TABLES.items():
        rows = read_tsv(path)
        check(f"{role}_role_rows", len(rows) == expected_rows, len(rows))
        check(f"{role}_role_event_sum", sum(int(row["occurrences"]) for row in rows) == expected_events, sum(int(row["occurrences"]) for row in rows))
        pages = set()
        for row in rows:
            page_field = row.get("pages", "")
            pages.update(part for part in page_field.replace("|", ",").split(",") if part)
        check(f"{role}_role_allowed_pages", not pages or pages <= ALLOWED_PAGES, sorted(pages))

    check(
        "summary_counts_match",
        summary["cards"] == 173
        and summary["events"] == 381
        and summary["statements"] == 116
        and summary["changed_cards"] == 18
        and summary["changed_events"] == 30,
        summary,
    )

    generated = [DICT, EVENT, STATEMENT, RECORDS, COMPONENT, PARADIGM, CHAINS, COUNTERS, UNRESOLVED, SUMMARY]
    before = {path.name: digest(path) for path in generated}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: digest(path) for path in generated}
    check("builder_exit", rebuilt.returncode == 0, rebuilt.stderr[-500:] if rebuilt.stderr else rebuilt.returncode)
    check("deterministic_rebuild", before == after, {name: before[name] == after[name] for name in before})

    failed = [row for row in checks if not row["passed"]]
    result = {
        "schema": "SIDEQUEST_SELECTED_FILTRATION_SEPARATION_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks": len(checks),
        "failures": len(failed),
        "details": checks,
        "files": {str(path.relative_to(ROOT)): digest(path) for path in generated},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(checks), "failures": len(failed)}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
