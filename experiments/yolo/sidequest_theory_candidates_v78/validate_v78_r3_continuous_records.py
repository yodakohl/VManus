#!/usr/bin/env python3
"""Validate completeness and dictionary discipline of V78 R3."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

EVENTS = HERE / "V78_R3_381_EVENT_CONTINUITY.tsv"
STATEMENTS = HERE / "V78_R3_116_STATEMENT_CONTINUITY.tsv"
RECORDS = HERE / "V78_R3_11_RECORD_CONTINUITY.tsv"
CONFLICTS = HERE / "V78_R3_CONFLICTS.tsv"
SUMMARY = HERE / "V78_R3_BUILD_SUMMARY.json"
REPORT = HERE / "V78_R3_CONTINUOUS_RECORD_REPORT.md"
VALIDATION = HERE / "V78_R3_VALIDATION.json"

V77_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"
V77_OCC = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_197_OCCURRENCE_AUDIT.tsv"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"

ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
PARAMETER_ID = "2f1c5e56e8f0ff459065"
RELATION_ID = "308e8ea2d5d190c498e8"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parts(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    records = read_tsv(RECORDS)
    conflicts = read_tsv(CONFLICTS)
    dictionary = read_tsv(V77_DICT)
    v77_occ = read_tsv(V77_OCC)
    v72 = read_tsv(V72)
    source_events = read_tsv(V73) + read_tsv(V74)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check("event row count", len(events) == 381, len(events))
    check("statement row count", len(statements) == 116, len(statements))
    check("record row count", len(records) == 11, len(records))
    check("card conflict row count", len(conflicts) == 173, len(conflicts))
    check("source event count", len(source_events) == 381, len(source_events))
    check("V77 dictionary target count", len(dictionary) == 24, len(dictionary))
    check("V77 selected occurrence count", len(v77_occ) == 197, len(v77_occ))
    check("report exists and nonempty", REPORT.exists() and REPORT.stat().st_size > 1000, REPORT.stat().st_size)

    serials = [int(row["event_serial"]) for row in events]
    check("event serial order 1..381", serials == list(range(1, 382)), serials[:3] + serials[-3:])
    check("event serial uniqueness", len(set(serials)) == 381)
    check("exact eleven record order", list(dict.fromkeys(row["record_unit_id"] for row in events)) == RECORD_ORDER)
    check("allowed prose pages only", {row["page"] for row in events} == ALLOWED_PAGES, sorted({row["page"] for row in events}))
    check("no f84 selector", all(not row["page"].startswith("f84") for row in events))
    check("135 exact fields", len({row["field_id"] for row in events}) == 135)
    check("116 exact statement memberships", len({row["statement_id"] for row in events}) == 116)
    check("173 exact opaque cards", len({row["joint_tuple_id"] for row in events}) == 173)
    check("all required event cells populated", all(all(value != "" for value in row.values()) for row in events))

    source_by_serial = {int(row["event_serial"]): row for row in source_events}
    check("source serial set exact", set(source_by_serial) == set(range(1, 382)))
    for field in ["record_unit_id", "page", "locus", "field_id", "statement_id", "joint_tuple_id", "terminal_status"]:
        check(
            f"event source binding exact: {field}",
            all(row[field] == source_by_serial[int(row["event_serial"])][field] for row in events),
        )
    check(
        "literal card layer exact",
        all(
            row["literal_exact_card_order"]
            == f"E{int(row['event_serial']):03d}=[OPAQUE_EXACT_CARD:{row['joint_tuple_id']}]"
            for row in events
        ),
    )
    check(
        "every exemplar expansion bracketed",
        all(
            row["bracketed_exemplar_expansion"].startswith("[MASTER-EXEMPLAR; KEINE WORTBEDEUTUNG: ")
            and row["bracketed_exemplar_expansion"].endswith("]")
            for row in events
        ),
    )
    check(
        "every event-bound reading names event once",
        all(
            row["event_bound_working_reading"].startswith(f"E{int(row['event_serial']):03d}=")
            for row in events
        ),
    )

    decision_counts = Counter(row["decision"] for row in dictionary)
    check("20 V77 unknown targets", decision_counts["EXEMPLAR_VALUE_UNKNOWN"] == 20, decision_counts)
    check("two V77 formal nonword targets", decision_counts["FORMAL_LABEL_NOT_WORD"] == 2, decision_counts)
    check("two V77 questioned words", decision_counts["CODEBOOK_ATTESTED_CATEGORY"] == 2, decision_counts)
    portable = [row for row in dictionary if row["decision"] == "CODEBOOK_ATTESTED_CATEGORY"]
    check("portable IDs exactly ET/PER", {row["joint_tuple_id"] for row in portable} == {ET_ID, PER_ID})
    check("portable source entries exact", {row["exact_source_language_entry"] for row in portable} == {"et", "per"})
    check("portable historical rows dated 1414", all("::1414::" in row["historical_attestation"] for row in portable))
    check("portable working words question-marked", all(row["usable_as_v78_working_word"] == "YES_WITH_QUESTION_MARK" for row in portable))

    et = [row for row in events if row["joint_tuple_id"] == ET_ID]
    per = [row for row in events if row["joint_tuple_id"] == PER_ID]
    parameter = [row for row in events if row["joint_tuple_id"] == PARAMETER_ID]
    relation = [row for row in events if row["joint_tuple_id"] == RELATION_ID]
    check("dcda count 19", len(et) == 19, len(et))
    check("dcda 19/19 only ET?", all(row["event_phrase"] == "ET?" for row in et))
    check("b5fcea count 9", len(per) == 9, len(per))
    check("b5fcea 9/9 only PER?", all(row["event_phrase"] == "PER?" for row in per))
    check(
        "no other card prints ET/PER",
        all(
            row["joint_tuple_id"] in {ET_ID, PER_ID}
            for row in events
            if row["event_phrase"] in {"ET?", "PER?"}
        ),
    )
    check("ET/PER never terminal", all(row["terminal_status"] == "NONCLOSE" for row in et + per))
    check("ET field-entry pressure 4/19", sum(row["event_index_in_field"] == "1" for row in et) == 4)
    check("ET statement-entry pressure 2/19", sum(row["event_index_in_statement"] == "1" for row in et) == 2)
    check("PER field-entry support 7/9", sum(row["event_index_in_field"] == "1" for row in per) == 7)
    check("PER nonentry pressure events exact", {row["event_serial"] for row in per if row["event_index_in_field"] != "1"} == {"180", "219"})
    check("formal parameter occurrences 20", len(parameter) == 20, len(parameter))
    check("formal relation occurrences 6", len(relation) == 6, len(relation))
    check(
        "parameter always explicit nonword",
        all(row["event_phrase"] == "[FORMAL_PARAMETER_CHANNEL; KEIN_WORT]" for row in parameter),
    )
    check(
        "relation always explicit nonword",
        all(row["event_phrase"] == "[FORMAL_RELATION_SLOT_CHANNEL; KEIN_WORT]" for row in relation),
    )
    check(
        "all other event phrases unknown",
        all(
            row["event_phrase"] == "[EXEMPLARWERT_UNBEKANNT]"
            for row in events
            if row["joint_tuple_id"] not in {ET_ID, PER_ID, PARAMETER_ID, RELATION_ID}
        ),
    )
    check(
        "old mnemonic handles absent from literal phrase layer",
        all(
            not any(
                token in row["event_phrase"]
                for token in [
                    "MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?",
                    "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?",
                ]
            )
            for row in events
        ),
    )

    selected_expected = {(row["event_serial"], row["joint_tuple_id"]) for row in v77_occ}
    selected_actual = {
        (row["event_serial"], row["joint_tuple_id"])
        for row in events
        if row["v77_target"] == "YES"
    }
    check("V77 197 selected occurrences reproduced", selected_actual == selected_expected)
    check("selected occurrence cardinality exact", len(selected_actual) == 197, len(selected_actual))

    event_by_serial = {row["event_serial"]: row for row in events}
    v72_by_statement = {row["statement_id"]: row for row in v72}
    statement_coverage: list[str] = []
    statement_binding_ok = True
    statement_order_ok = True
    statement_phrase_ok = True
    statement_event_tags_ok = True
    for row in statements:
        ss = parts(row["event_serials"])
        statement_coverage.extend(ss)
        if row["statement_id"] not in v72_by_statement or row["event_serials"] != v72_by_statement[row["statement_id"]]["event_serials"]:
            statement_binding_ok = False
        expected_cards = " > ".join(f"[{event_by_serial[s]['joint_tuple_id']}]" for s in ss)
        expected_phrases = " > ".join(event_by_serial[s]["event_phrase"] for s in ss)
        if row["literal_exact_card_order"] != expected_cards:
            statement_order_ok = False
        if row["dictionary_phrase_order"] != expected_phrases:
            statement_phrase_ok = False
        found = re.findall(r"\bE(\d{3})=", row["event_aligned_bracketed_expansion"])
        if found != [f"{int(s):03d}" for s in ss]:
            statement_event_tags_ok = False
    check("statement coverage exactly once", Counter(statement_coverage) == Counter(str(i) for i in range(1, 382)))
    check("statement memberships reproduce V72", statement_binding_ok)
    check("statement exact-card order", statement_order_ok)
    check("statement dictionary phrase order", statement_phrase_ok)
    check("statement event tags exact", statement_event_tags_ok)
    check("statement texts all populated", all(row["continuous_sentence_text"] and row["v72_owner_aware_source_paraphrase"] for row in statements))
    check("18 statements cross fields", sum(int(row["cross_field_transitions"]) > 0 for row in statements) == 18)
    check("19 field transitions inside statements", sum(int(row["cross_field_transitions"]) for row in statements) == 19)
    check("18 statements cross physical lines", sum(int(row["cross_physical_line_transitions"]) > 0 for row in statements) == 18)
    check("19 physical-line transitions inside statements", sum(int(row["cross_physical_line_transitions"]) for row in statements) == 19)
    check("10 visible owner resets", sum(int(row["visible_owner_resets"]) for row in statements) == 10)
    internal_resets = {
        row["event_serial"]
        for row in events
        if "OWNER_RESET_INSIDE_SENTENCE" in row["local_grammar_pressure_flags"]
    }
    check("four internal owner-reset breaks exact", internal_resets == {"203", "264", "291", "356"}, sorted(internal_resets))

    record_coverage: list[str] = []
    record_sequence_ok = True
    record_card_order_ok = True
    record_phrase_order_ok = True
    record_tag_ok = True
    for row in records:
        ss = parts(row["event_serials"])
        record_coverage.extend(ss)
        source_ss = [event["event_serial"] for event in events if event["record_unit_id"] == row["record_unit_id"]]
        if ss != source_ss:
            record_sequence_ok = False
        expected_cards = " > ".join(f"[{event_by_serial[s]['joint_tuple_id']}]" for s in ss)
        expected_phrases = " > ".join(event_by_serial[s]["event_phrase"] for s in ss)
        if row["literal_exact_card_order"] != expected_cards:
            record_card_order_ok = False
        if row["dictionary_phrase_order"] != expected_phrases:
            record_phrase_order_ok = False
        found = re.findall(r"\bE(\d{3})=", row["complete_event_bound_record_text"])
        if found != [f"{int(s):03d}" for s in ss]:
            record_tag_ok = False
    check("record order exact", [row["record_unit_id"] for row in records] == RECORD_ORDER)
    check("record coverage exactly once", Counter(record_coverage) == Counter(str(i) for i in range(1, 382)))
    check("record event sequence exact", record_sequence_ok)
    check("record exact-card order", record_card_order_ok)
    check("record dictionary phrase order", record_phrase_order_ok)
    check("record event tags exact", record_tag_ok)
    check("record full texts populated", all(row["selected_continuous_exemplar_text"] and row["fluent_record_text"] for row in records))
    check("record process rivals populated", all(row["process_rival"] for row in records))
    check("record notation rivals populated", all(row["notation_rival"] for row in records))

    conflict_by_card = {row["joint_tuple_id"]: row for row in conflicts}
    check("one conflict row per exact card", len(conflict_by_card) == 173 and set(conflict_by_card) == {row["joint_tuple_id"] for row in events})
    check("conflict occurrence sum 381", sum(int(row["occurrences"]) for row in conflicts) == 381)
    check("every card receives formal rival", all(row["formal_link_or_entry_rival"].startswith("FORMAL_") for row in conflicts))
    check("ET formal rival intra-field", conflict_by_card[ET_ID]["formal_link_or_entry_rival"] == "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER")
    check("PER formal rival entry", conflict_by_card[PER_ID]["formal_link_or_entry_rival"] == "FORMAL_ENTRY_OR_RESET_MARK")
    check("parameter formal rival intra-field", conflict_by_card[PARAMETER_ID]["formal_link_or_entry_rival"] == "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER")
    check("relation formal rival intra-field", conflict_by_card[RELATION_ID]["formal_link_or_entry_rival"] == "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER")
    check(
        "formal-rival partition counts frozen",
        Counter(row["formal_link_or_entry_rival"] for row in conflicts)
        == {
            "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER": 89,
            "FORMAL_ENTRY_OR_RESET_MARK": 46,
            "FORMAL_CLOSE_OR_COMMIT_MARK": 27,
            "FORMAL_POLYPOSITIONAL_ENTRY_LINK_OR_CLOSE_CARD": 11,
        },
    )
    check("17 cross-Herbal/Bio cards", sum(row["cross_herbal_bio_status"] == "BOTH" for row in conflicts) == 17)

    check("summary built", summary["status"] == "BUILT")
    check("summary count block exact", summary["counts"]["events"] == 381 and summary["counts"]["statements"] == 116 and summary["counts"]["records"] == 11)
    check("summary portable checks exact", summary["portable_word_checks"] == {
        "dcda_as_et": 19,
        "dcda_non_et_phrases": 0,
        "b5fcea_as_per": 9,
        "b5fcea_non_per_phrases": 0,
        "other_events_printing_et_or_per": 0,
    })
    check("summary f84 seal", summary["seals"] == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"})
    check(
        "output hashes current",
        all(summary["output_sha256"][path.name] == sha256(path) for path in [EVENTS, STATEMENTS, RECORDS, CONFLICTS]),
    )

    report_text = REPORT.read_text(encoding="utf-8")
    check("report states nontranslation ceiling", "keine Übersetzung" in report_text and "keine Entzifferung" in report_text)
    check("report states exact ET/PER counts", "19/19-mal ausschließlich als `ET?`" in report_text and "9/9-mal ausschließlich als `PER?`" in report_text)
    check("report states two formal nonwords", "20/20-mal" in report_text and "6/6-mal" in report_text and "KEIN_WORT" in report_text)
    check("report lists all eleven records", all(f"| {record_id} |" in report_text for record_id in RECORD_ORDER))

    passed = sum(item["pass"] for item in checks)
    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "passed": passed,
        "total": len(checks),
        "failed": failed,
        "counts": {
            "events": len(events),
            "statements": len(statements),
            "records": len(records),
            "fields": len({row["field_id"] for row in events}),
            "exact_cards": len(conflicts),
            "et_occurrences": len(et),
            "per_occurrences": len(per),
            "formal_nonword_occurrences": len(parameter) + len(relation),
            "unknown_or_unaudited_occurrences": sum("EXEMPLAR_VALUE_UNKNOWN" in row["dictionary_status"] for row in events),
        },
        "continuity": {
            "statements_crossing_fields": sum(int(row["cross_field_transitions"]) > 0 for row in statements),
            "statements_crossing_lines": sum(int(row["cross_physical_line_transitions"]) > 0 for row in statements),
            "internal_owner_reset_events": sorted(internal_resets, key=int),
        },
        "checks": checks,
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']} {passed}/{len(checks)}")
    if failed:
        for item in failed:
            print(f"FAIL: {item['name']} :: {item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
