#!/usr/bin/env python3
"""Validate the selected creative application/administration edition."""

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
DICT = HERE / "SELECTED_173_APPLICATION_DICTIONARY.tsv"
EVENT = HERE / "SELECTED_381_APPLICATION_INTERLINEAR.tsv"
STATEMENT = HERE / "SELECTED_116_APPLICATION_SENTENCES.tsv"
RECORDS = HERE / "SELECTED_11_APPLICATION_RECORDS.md"
COMPONENT = HERE / "SELECTED_APPLICATION_COMPONENTS.tsv"
PARADIGM = HERE / "SELECTED_APPLICATION_PARADIGM.tsv"
BRANCHES = HERE / "SELECTED_APPLICATION_BRANCHES.tsv"
COUNTERS = HERE / "APPLICATION_COUNTEREXAMPLES.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED_AFTER_APPLICATION.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
BUILDER = HERE / "build_selected_application_completion.py"
VALIDATION = HERE / "VALIDATION.json"
REPORT = HERE / "SELECTED_APPLICATION_COMPLETION_REPORT.md"

HISTORICAL = HERE / "APPLICATION_HISTORICAL_PARADIGM.tsv"
TECHNICAL = HERE / "APPLICATION_TECHNICAL_PARADIGM.tsv"
WORKSHOP = HERE / "APPLICATION_WORKSHOP_PARADIGM.tsv"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
EXPECTED_OVERRIDE_IDS = {
    "dd0ecaf5e27d81befffc", "308e8ea2d5d190c498e8", "4a7a6326ac95a8809302",
    "90bcf0a9ec0ef56399e6", "93f69c38fdedee1598e9", "00d8ebe3c68294eeac39",
    "433713294b25b0a12f66", "7811a7daff25d476e28d", "97ddca78c9ebcc956d04",
    "abb23e5e6936b4147f76", "ba540da978ea132f6da5", "08bd5ca0c2ad137a056d",
    "0275fbf14e07935b0a45", "7d25241b0e56c836372a", "5fca8fc3dee57e1d8c1f",
    "c205570c49d4d93c23d3", "c10aec6d4dd877ec8bd8", "74c76d589d44120f647b",
    "348e81ba084c5acdb32b", "7f68f60279efe6b28cd7", "95987d6f198d6d247511",
    "eb2e4bc143f623ee03ac",
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
    branches = read_tsv(BRANCHES)
    counters = read_tsv(COUNTERS)
    unresolved = read_tsv(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check("dictionary_count", len(dictionary) == 173, len(dictionary))
    check("event_count", len(events) == 381, len(events))
    check("statement_count", len(statements) == 116, len(statements))
    check("record_count", len({row["record_unit_id"] for row in statements}) == 11, len({row["record_unit_id"] for row in statements}))
    check("component_count", len(components) == 36, len(components))
    check("paradigm_count", len(paradigm) == 35, len(paradigm))
    check("branch_count", len(branches) == 13, len(branches))
    check("counterexample_count", len(counters) == 10, len(counters))
    check("unresolved_count", len(unresolved) == 26, len(unresolved))

    dictionary_ids = [row["joint_tuple_id"] for row in dictionary]
    check("dictionary_unique_ids", len(dictionary_ids) == len(set(dictionary_ids)), len(set(dictionary_ids)))
    check("event_ids_unique", len({row["event_id"] for row in events}) == 381, len({row["event_id"] for row in events}))
    check("event_serials_contiguous", [int(row["event_serial"]) for row in events] == list(range(1, 382)), events[-1]["event_serial"])
    check("allowed_pages_only", {row["page"] for row in events} == ALLOWED_PAGES, sorted({row["page"] for row in events}))
    check("sealed_pages_absent", not any(row["page"].startswith("f84") for row in events), "381 checked")
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

    changed_cards = [row for row in dictionary if row["application_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in events if row["application_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["application_revised_event_count"]) > 0]
    check("override_identity_set", {row["joint_tuple_id"] for row in changed_cards} == EXPECTED_OVERRIDE_IDS, len(changed_cards))
    check("changed_card_count", len(changed_cards) == 22, len(changed_cards))
    check("changed_event_count", len(changed_events) == 55, len(changed_events))
    check("changed_statement_count", len(changed_statements) == 42, len(changed_statements))

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
    check("paradigm_unique_cards", len(paradigm_ids) == len(set(paradigm_ids)) == 35, len(set(paradigm_ids)))
    check("paradigm_event_sum", sum(int(row["events"]) for row in paradigm) == 147, sum(int(row["events"]) for row in paradigm))
    check("paradigm_event_counts", all(int(row["events"]) == card_event_counts[row["joint_tuple_id"]] for row in paradigm), "35 checked")
    check("paradigm_values_short", all(len(row["selected_reading_de"].split()) <= 5 for row in paradigm), max(len(row["selected_reading_de"].split()) for row in paradigm))

    close_ids = {
        "7db18b2f0fb7ed0fcfd3", "7d25241b0e56c836372a", "d25110e0d8488927278f",
        "95987d6f198d6d247511", "eb2e4bc143f623ee03ac", "7f68f60279efe6b28cd7",
    }
    close_events = [row for row in events if row["joint_tuple_id"] in close_ids]
    check("application_closes_statement_final", all(events_by_statement[row["statement_id"]][-1]["event_id"] == row["event_id"] for row in close_events), len(close_events))
    check("application_closes_marked", all("schluss" in row["concrete_word_reading_de"].lower() for row in close_events), len(close_events))

    check("al_atomic_default", by_card["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"] == "Stelle", by_card["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"])
    check("lcheey_no_anatomy", by_card["5fca8fc3dee57e1d8c1f"]["concrete_word_reading_de"] == "benetzte Stelle", by_card["5fca8fc3dee57e1d8c1f"]["concrete_word_reading_de"])
    check("lddy_fastens", by_card["eb2e4bc143f623ee03ac"]["concrete_word_reading_de"] == "Posten befestigen; Schluss", by_card["eb2e4bc143f623ee03ac"]["concrete_word_reading_de"])
    check("okeedy_broadened", by_card["7d25241b0e56c836372a"]["concrete_word_reading_de"] == "länger einwirken; Schluss", by_card["7d25241b0e56c836372a"]["concrete_word_reading_de"])
    check("choy_short", by_card["c10aec6d4dd877ec8bd8"]["concrete_word_reading_de"] == "waschen", by_card["c10aec6d4dd877ec8bd8"]["concrete_word_reading_de"])
    check("two_spread_actions_distinct", {by_card["74c76d589d44120f647b"]["concrete_word_reading_de"], by_card["348e81ba084c5acdb32b"]["concrete_word_reading_de"]} == {"einreiben", "aufstreichen"}, "DSHEOL/SHECTHEDCHY")

    branch_by_id = {row["statement_id"]: row for row in branches}
    check("clear_application_branch", branch_by_id["B2-S012"]["application_stages_de"] == "Klarauszug → länger halten → benetzte Stelle → Maß → durchtränken", branch_by_id["B2-S012"]["application_stages_de"])
    check("fasten_branch", branch_by_id["B4-S004"]["application_stages_de"] == "Posten befestigen → Schluss", branch_by_id["B4-S004"]["application_stages_de"])
    check("herbal_apply_branch", "H5-S002" in branch_by_id and "auftragen" in branch_by_id["H5-S002"]["selected_card_sequence_de"], "H5-S002")
    check("records_markdown_complete", sum(1 for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.startswith("## ")) == 11, "11 headings")
    check("selected_report_present", REPORT.exists() and "BEFESTIGEN" in REPORT.read_text(encoding="utf-8"), REPORT.name)

    historical = read_tsv(HISTORICAL)
    technical = read_tsv(TECHNICAL)
    workshop = read_tsv(WORKSHOP)
    check("historical_role_events", len(historical) == 58 and len({row["event_id"] for row in historical}) == 58, len(historical))
    check("historical_role_cards", len({row["joint_tuple_id"] for row in historical}) == 19, len({row["joint_tuple_id"] for row in historical}))
    check("technical_role_cards", len(technical) == 19, len(technical))
    check("technical_role_events", sum(int(row["occurrences"]) for row in technical) == 58, sum(int(row["occurrences"]) for row in technical))
    workshop_types = [row for row in workshop if row["row_kind"] == "TYPE"]
    workshop_records = [row for row in workshop if row["row_kind"] == "RECORD"]
    check("workshop_role_types", len(workshop_types) == 35 and sum(int(row["occurrences"]) for row in workshop_types) == 147, len(workshop_types))
    check("workshop_role_records", len(workshop_records) == 11, len(workshop_records))

    component_by_id = {row["component_id"]: row for row in components}
    check("application_action_deck", "APPLICATION_ACTION_DECK" in component_by_id, sorted(component_by_id))
    check("application_site_deck", "APPLICATION_SITE_DECK" in component_by_id, sorted(component_by_id))
    check("lddy_component_neutral", component_by_id["LDDY_APPLICATION_CLOSE"]["working_meaning_de"] == "befestigen und den Schritt schließen", component_by_id["LDDY_APPLICATION_CLOSE"]["working_meaning_de"])

    check(
        "summary_counts_match",
        summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116
        and summary["changed_cards"] == 22 and summary["changed_events"] == 55
        and summary["changed_statements"] == 42,
        summary,
    )

    generated = [DICT, EVENT, STATEMENT, RECORDS, COMPONENT, PARADIGM, BRANCHES, COUNTERS, UNRESOLVED, SUMMARY, REPORT]
    before = {path.name: digest(path) for path in generated}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: digest(path) for path in generated}
    check("builder_exit", rebuilt.returncode == 0, rebuilt.stderr[-500:] if rebuilt.stderr else rebuilt.returncode)
    check("deterministic_rebuild", before == after, {name: before[name] == after[name] for name in before})

    failed = [row for row in checks if not row["passed"]]
    result = {
        "schema": "SIDEQUEST_SELECTED_APPLICATION_COMPLETION_VALIDATION_V1",
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
