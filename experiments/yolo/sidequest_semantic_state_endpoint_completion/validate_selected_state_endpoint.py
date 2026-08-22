#!/usr/bin/env python3
"""Mechanical validation for the creative state/endpoint sidequest edition."""

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
DICT = HERE / "SELECTED_173_STATE_ENDPOINT_DICTIONARY.tsv"
EVENT = HERE / "SELECTED_381_STATE_ENDPOINT_INTERLINEAR.tsv"
STATEMENT = HERE / "SELECTED_116_STATE_ENDPOINT_SENTENCES.tsv"
LATTICE = HERE / "SELECTED_STATE_ENDPOINT_LATTICE.tsv"
COMPONENT = HERE / "SELECTED_STATE_ENDPOINT_COMPONENTS.tsv"
COUNTER = HERE / "STATE_ENDPOINT_COUNTEREXAMPLES.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED_AFTER_STATE_ENDPOINT.tsv"
RECORDS = HERE / "SELECTED_11_STATE_ENDPOINT_RECORDS.md"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
VALIDATION = HERE / "VALIDATION.json"
BUILDER = HERE / "build_selected_state_endpoint.py"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
CLOSED_ROLES = {"CLOSED_GRADE_1", "CLOSED_GRADE_2", "CLOSED_GRADE_3"}


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
    lattice = read_tsv(LATTICE)
    components = read_tsv(COMPONENT)
    counters = read_tsv(COUNTER)
    unresolved = read_tsv(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check("dictionary_count", len(dictionary) == 173, len(dictionary))
    check("event_count", len(events) == 381, len(events))
    check("statement_count", len(statements) == 116, len(statements))
    check("record_count", len({row["record_unit_id"] for row in statements}) == 11, len({row["record_unit_id"] for row in statements}))
    check("lattice_count", len(lattice) == 23, len(lattice))
    check("counterexample_count", len(counters) == 8, len(counters))
    check("component_count", len(components) == 28, len(components))
    check("unresolved_count", len(unresolved) == 19, len(unresolved))

    dictionary_ids = [row["joint_tuple_id"] for row in dictionary]
    check("dictionary_unique_ids", len(dictionary_ids) == len(set(dictionary_ids)), len(set(dictionary_ids)))
    check("event_ids_unique", len({row["event_id"] for row in events}) == 381, len({row["event_id"] for row in events}))
    check("event_serials_contiguous", [int(row["event_serial"]) for row in events] == list(range(1, 382)), events[-1]["event_serial"])
    check("allowed_pages_only", {row["page"] for row in events} == ALLOWED_PAGES, sorted({row["page"] for row in events}))
    check("no_blank_card_gloss", all(row["concrete_word_reading_de"].strip() for row in dictionary), "173 checked")
    check("no_blank_event_gloss", all(row["concrete_word_reading_de"].strip() for row in events), "381 checked")
    check("no_unknown_defaults", not any("UNKNOWN" in row["concrete_word_reading_de"].upper() for row in dictionary), "dictionary concrete defaults")

    by_card = {row["joint_tuple_id"]: row for row in dictionary}
    card_event_counts = Counter(row["joint_tuple_id"] for row in events)
    check("all_events_have_card", set(card_event_counts) == set(by_card), len(card_event_counts))
    check("dictionary_occurrence_counts", all(int(row["occurrences"]) == card_event_counts[row["joint_tuple_id"]] for row in dictionary), "173 checked")
    check(
        "event_dictionary_readings_match",
        all(
            row["semantic_segmentation"] == by_card[row["joint_tuple_id"]]["semantic_segmentation"]
            and row["concrete_word_reading_de"] == by_card[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in events
        ),
        "381 checked",
    )

    statement_event_ids: list[str] = []
    for row in statements:
        ids = row["event_ids"].split("|")
        statement_event_ids.extend(ids)
        check("statement_count_" + row["statement_id"], int(row["event_count"]) == len(ids), len(ids))
    check("statement_event_partition", statement_event_ids == [row["event_id"] for row in events], len(statement_event_ids))
    check("statements_unique", len({row["statement_id"] for row in statements}) == 116, len({row["statement_id"] for row in statements}))

    lattice_ids = [row["joint_tuple_id"] for row in lattice]
    check("lattice_ids_exist", set(lattice_ids) <= set(by_card), len(set(lattice_ids)))
    check("lattice_event_counts", all(int(row["events"]) == card_event_counts[row["joint_tuple_id"]] for row in lattice), "23 checked")
    check("all_lattice_glosses_concrete", all(row["selected_reading_de"].strip() for row in lattice), "23 checked")

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    closed_ids = {row["joint_tuple_id"] for row in lattice if row["cell_role"] in CLOSED_ROLES}
    closed_events = [row for row in events if row["joint_tuple_id"] in closed_ids]
    check(
        "selected_closed_lattice_events_statement_final",
        all(events_by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in closed_events),
        len(closed_events),
    )
    check("selected_closed_lattice_glosses_mark_close", all("schluss" in row["concrete_word_reading_de"].lower() for row in closed_events), len(closed_events))

    y_id = "b921a237be883a820352"
    y_card = by_card[y_id]
    check("base_y_includes_visible_dy", "dy" in y_card["surface_family"].split("|"), y_card["surface_family"])
    check("base_y_not_terminal", "CLOSE" not in y_card["semantic_segmentation"] and "Schluss" not in y_card["concrete_word_reading_de"], y_card["semantic_segmentation"])
    check("base_y_occurrences", card_event_counts[y_id] == 18, card_event_counts[y_id])

    family_counts = Counter(row["core_family"] for row in lattice)
    check("ok_grid_has_seven_rows_six_semantic_cells", family_counts["OK"] == 7, family_counts["OK"])
    check("ot_grid_has_three_cells", family_counts["OT"] == 3, family_counts["OT"])
    check("cth_grid_has_two_cells", family_counts["CTH"] == 2, family_counts["CTH"])
    check("shed_grid_has_two_cells", family_counts["SHED"] == 2, family_counts["SHED"])
    check("chk_grid_has_four_cells", family_counts["CHK"] == 4, family_counts["CHK"])
    check("solk_grid_has_three_cells", family_counts["SOLK"] == 3, family_counts["SOLK"])

    changed_cards = [row for row in dictionary if row["state_endpoint_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in events if row["state_endpoint_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["state_revised_event_count"]) > 0]
    check("changed_card_count", len(changed_cards) == 30, len(changed_cards))
    check("changed_event_count", len(changed_events) == 109, len(changed_events))
    check("changed_statement_count", len(changed_statements) == 73, len(changed_statements))
    check("summary_counts_match", summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116 and summary["lattice_rows"] == 23, summary)

    check("records_markdown_has_all_records", sum(1 for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.startswith("## ")) == 11, "11 headings")
    check("corrected_or_unresolved_row", any(row["candidate_component"] == "OR_INTERNAL_STRINGS" and "split selected CHOCHOR" in row["working_default_until_better_model"] for row in unresolved), "CHOCHOR correction")
    check("cthaiin_counterexample_present", any(row["counterexample"] == "CTHAIIN_WHOLE" for row in counters), "present")
    check("visible_dy_counterexample_present", any(row["counterexample"] == "VISIBLE_DY_NOT_GLOBAL_CLOSE" for row in counters), "present")

    generated = [DICT, EVENT, STATEMENT, RECORDS, COMPONENT, LATTICE, COUNTER, UNRESOLVED, SUMMARY]
    before = {path.name: digest(path) for path in generated}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: digest(path) for path in generated}
    check("builder_exit", rebuilt.returncode == 0, rebuilt.stderr[-500:] if rebuilt.stderr else rebuilt.returncode)
    check("deterministic_rebuild", before == after, {name: before[name] == after[name] for name in before})

    failed = [row for row in checks if not row["passed"]]
    result = {
        "schema": "SIDEQUEST_SELECTED_STATE_ENDPOINT_VALIDATION_V1",
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
