#!/usr/bin/env python3
"""Validate V78 R1 event binding, role restrictions, scope, and counts."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVENTS = HERE / "V78_R1_381_EVENT_CONTINUOUS_INTERLINEAR.tsv"
RECORDS = HERE / "V78_R1_11_RECORD_CONTINUOUS.tsv"
FIT = HERE / "V78_R1_ET_PER_28_FIT.tsv"
CONTRADICTIONS = HERE / "V78_R1_CONTRADICTIONS.tsv"
EDITION = HERE / "V78_R1_ELEVEN_RECORDS_CONTINUOUS.md"
SUMMARY = HERE / "V78_R1_BUILD_SUMMARY.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
FORMAL_CARDS = {"2f1c5e56e8f0ff459065", "308e8ea2d5d190c498e8"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read(EVENTS)
    records = read(RECORDS)
    fits = read(FIT)
    contradictions = read(CONTRADICTIONS)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks: dict[str, object] = {}

    checks["events_381"] = len(events) == 381
    checks["event_serials_exact_once"] = [int(r["event_serial"]) for r in events] == list(range(1, 382))
    checks["pages_exactly_selected_prose"] = {r["page"] for r in events} == ALLOWED_PAGES
    checks["sealed_pages_absent"] = not ({r["page"] for r in events} & {"f84", "f84r"})
    checks["literal_token_has_exact_card"] = all(
        f"CARD[{r['joint_tuple_id']}]" in r["literal_card_order_token"] for r in events
    )

    et = [r for r in events if r["joint_tuple_id"] == ET_CARD]
    per = [r for r in events if r["joint_tuple_id"] == PER_CARD]
    formal = [r for r in events if r["joint_tuple_id"] in FORMAL_CARDS]
    exemplar = [r for r in events if r["joint_tuple_id"] not in ({ET_CARD, PER_CARD} | FORMAL_CARDS)]
    checks["et_occurrences_19"] = len(et) == 19
    checks["per_occurrences_9"] = len(per) == 9
    checks["formal_occurrences_26"] = len(formal) == 26
    checks["exemplar_occurrences_327"] = len(exemplar) == 327
    checks["et_only_und_auch"] = {r["et_per_reading"] for r in et} <= {"UND", "AUCH"}
    checks["per_only_durch_gemaess"] = {r["et_per_reading"] for r in per} <= {"DURCH", "GEMÄSS"}
    checks["et_segments_have_no_exemplar_completion"] = all(
        re.fullmatch(r"\[ET\?:(UND|AUCH)\?\]", r["source_expansion_segment"]) for r in et
    )
    checks["per_segments_have_visible_exemplar_completion"] = all(
        r["source_expansion_segment"].startswith("[PER?:")
        and " [EXEMPLAR:" in r["source_expansion_segment"]
        and "[ELLIPSE:" in r["source_expansion_segment"]
        for r in per
    )
    checks["formal_exact_nonword_label_only"] = all(
        r["source_expansion_segment"] == "[FORMAL; KEIN WORT]"
        and r["literal_card_order_token"].endswith("=[FORMAL; KEIN WORT]")
        for r in formal
    )
    checks["all_other_content_visibly_exemplar"] = all(
        r["source_expansion_segment"].startswith("[EXEMPLAR:")
        and r["literal_card_order_token"].endswith("=[EXEMPLARWERT UNBEKANNT]")
        for r in exemplar
    )

    checks["fit_rows_28"] = len(fits) == 28
    checks["fit_events_match_role_events"] = {int(r["event_serial"]) for r in fits} == {
        int(r["event_serial"]) for r in et + per
    }
    checks["all_fit_rows_no_extra_sense"] = all(r["extra_sense_introduced"] == "NO" for r in fits)
    checks["per_field_entry_count_7"] = sum(r["role_card"] == "PER?" and r["field_entry"] == "YES" for r in fits) == 7
    checks["high_repair_not_hidden"] = sum(r["fit_grade"] == "HIGH_REPAIR" for r in fits) == 3
    checks["no_role_fit_lowered_to_fail"] = all(int(r["fit_cost_0_4"]) < 4 for r in fits)

    checks["records_11"] = len(records) == 11
    checks["record_order_exact"] = [r["record_unit_id"] for r in records] == RECORD_ORDER
    checks["record_event_total_381"] = sum(int(r["event_count"]) for r in records) == 381
    literal_serials: list[int] = []
    source_serials: list[int] = []
    for record in records:
        literal_serials.extend(int(x) for x in re.findall(r"E(\d{3}):CARD", record["literal_card_order"]))
        source_serials.extend(int(x) for x in re.findall(r"E(\d{3})=>", record["source_event_alignment"]))
    checks["record_literal_binds_each_event_once"] = literal_serials == list(range(1, 382))
    checks["record_source_binds_each_event_once"] = source_serials == list(range(1, 382))
    checks["record_repair_costs_bounded"] = all(0 <= int(r["repair_cost_0_4"]) <= 4 for r in records)
    checks["line_crossings_preserved"] = any(r["line_and_field_crossing"] != "NONE" for r in records)
    checks["station_breaks_visible"] = sum(r["continuous_source_expansion"].count("[EDITORIAL:STATIONSWECHSEL") for r in records) == 10

    checks["contradictions_39"] = len(contradictions) == 39
    checks["contradictions_cover_11_records_28_roles"] = Counter(r["scope"] for r in contradictions) == {
        "RECORD": 11,
        "ET_PER_OCCURRENCE": 28,
    }
    edition = EDITION.read_text(encoding="utf-8")
    checks["edition_has_all_record_headings"] = all(f"## {record} —" in edition for record in RECORD_ORDER)
    checks["edition_marks_exemplar_formal_et_per"] = all(mark in edition for mark in ("[EXEMPLAR:", "[FORMAL; KEIN WORT]", "[ET?:", "[PER?:"))
    checks["summary_matches"] = (
        summary["events"] == 381
        and summary["records"] == 11
        and summary["statements"] == 116
        and summary["et_occurrences"] == 19
        and summary["per_occurrences"] == 9
        and summary["sealed_pages_accessed"] == []
    )

    failed = sorted(k for k, v in checks.items() if v is not True)
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "counts": {
            "events": len(events),
            "records": len(records),
            "et": len(et),
            "per": len(per),
            "formal_nonword": len(formal),
            "exemplar": len(exemplar),
            "fit_rows": len(fits),
            "contradictions": len(contradictions),
        },
        "scope": {
            "pages": sorted({r["page"] for r in events}),
            "f84": "SEALED_NOT_ACCESSED",
            "f84r": "SEALED_NOT_ACCESSED",
        },
        "ceiling": "CREATIVE_CONTINUOUS_WORKING_EDITION_NOT_CONFIRMED_TRANSLATION",
    }
    (HERE / "V78_R1_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("validation failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
