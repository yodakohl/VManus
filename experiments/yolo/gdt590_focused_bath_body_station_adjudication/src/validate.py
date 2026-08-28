#!/usr/bin/env python3
"""Validate GDT590's four focused bath adjudications and complete replay."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from typing import Any

from bath_model import (
    ADMITTED_PAGES,
    INPUTS,
    OUTPUTS,
    ROOT,
    STATUS,
    TARGETS,
    build,
    load_inputs,
    read_tsv,
    sha256,
)


TARGET_EVENTS = set(TARGETS)
TARGET_HOSTS = {target["host_key"] for target in TARGETS.values()}
TARGET_STATEMENTS = {target["statement_id"] for target in TARGETS.values()}


def textual(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def project(row: dict[str, str], fields: list[str]) -> dict[str, str]:
    return {field: row[field] for field in fields}


def main() -> int:
    data = load_inputs()
    rows = {
        name: read_tsv(path)
        for name, path in OUTPUTS.items()
        if path.suffix == ".tsv"
    }
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))
    reader = OUTPUTS["reader"].read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_ordinal": len(checks) + 1,
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "detail": detail,
            }
        )

    adjudications = rows["adjudications"]
    analogs = rows["bath_analogs"]
    packets = rows["bath_packets"]
    guard = rows["body_guard"]
    slots = rows["slots"]
    statements = rows["statements"]
    visuals = rows["visual"]

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check(
        "INPUT_HASHES",
        result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()},
        f"{len(INPUTS)} fixed inputs",
    )
    all_tsv_rows = [*adjudications, *analogs, *packets, *guard, *slots, *statements, *visuals]
    pages = {
        row["physical_page"]
        for row in all_tsv_rows
        if row.get("physical_page")
    }
    check("NO_NEW_PAGE", pages <= ADMITTED_PAGES, f"{len(pages)} pages within fixed thirty-page set")
    check("SEALED_F84_ABSENT", not any(page.lower().startswith("f84") for page in pages), "no f84/f84r row")

    rebuilt = build(data)
    for name in ("adjudications", "bath_analogs", "bath_packets", "body_guard", "slots", "statements", "visual"):
        check(
            f"{name.upper()}_IN_MEMORY_REBUILD",
            rows[name] == textual(rebuilt[name]),
            f"{len(rows[name])} rows",
        )
    check("RESULT_IN_MEMORY_REBUILD", result == rebuilt["result"], "compact result exact")

    check("TARGET_COUNT", len(adjudications) == 4, str(len(adjudications)))
    check("TARGET_EVENT_SET", {row["source_event_id"] for row in adjudications} == TARGET_EVENTS, str(sorted(TARGET_EVENTS)))
    check("TARGET_HOST_SET", {row["primary_governor_key"] for row in adjudications} == TARGET_HOSTS, "four exact governors")
    check("TARGET_STATEMENT_SET", {row["statement_id"] for row in adjudications} == TARGET_STATEMENTS, "four exact statements")
    check("TARGET_PAGES", {row["physical_page"] for row in adjudications} == {"f77r", "f82r"}, "only already admitted f77r/f82r")
    check("TARGET_BLOCKER_FREE", all(row["body_blockers_present"] == "NONE" for row in adjudications), "four blocker-free hosts")
    check(
        "TARGET_ROOT_PACKETS",
        all(set(row["written_root_sequence"].split("+")) == {"Y", "AIIN"} for row in adjudications),
        "four Y+AIIN complete hosts",
    )
    check("TARGET_DECISION", all(row["gdt590_decision"].startswith("BODY_DEFAULT") for row in adjudications), "body first at four")
    check("TARGET_ALTERNATIVE", all("Stationsansatz" in row["retained_station_alternative_de"] for row in adjudications), "station visible at four")
    check(
        "TARGET_STRENGTH_ORDER",
        {row["source_event_id"]: row["working_strength"] for row in adjudications}
        == {
            "G407-E2404": "MEDIUM_HIGH",
            "G407-E2637": "HIGH",
            "G407-E2652": "MEDIUM_EXPLORATORY",
            "G407-E3182": "VERY_HIGH",
        },
        "E2652 weakest, E3182 strongest",
    )

    check("BATH_ANALOG_COUNT", len(analogs) == 92, str(len(analogs)))
    analog_profile = Counter(row["analogy_class"] for row in analogs)
    check(
        "BATH_ANALOG_PROFILE",
        analog_profile
        == {"CLEAN_Y_BODY_EXISTING": 48, "CLEAN_Y_PLUS_FILL_BODY_GDT590": 4, "BLOCKED_Y_STATION": 40},
        str(analog_profile),
    )
    changed_analogs = [row for row in analogs if row["gdt590_changed"] == "YES"]
    check("ANALOG_CHANGED_SET", {row["source_event_id"] for row in changed_analogs} == TARGET_EVENTS, "four exact analog changes")
    check(
        "BLOCKED_ANALOGS_STAY_STATION",
        all(
            row["body_blockers_present"] != "NONE" and set(row["gdt590_y_lemma_sequence"].split("|")) == {"Stationsansatz"}
            for row in analogs
            if row["analogy_class"] == "BLOCKED_Y_STATION"
        ),
        "40/40 blocked station hosts retained",
    )
    check(
        "SHEY_PROFILE",
        result["surface_analogy_profile"]["shey"]
        == {"clean_prior_body": 19, "clean_promoted": 1, "blocked_station": 2},
        str(result["surface_analogy_profile"]["shey"]),
    )
    check(
        "CHEEY_PROFILE",
        result["surface_analogy_profile"]["cheey"]
        == {"clean_prior_body": 11, "clean_promoted": 2, "blocked_station": 4},
        str(result["surface_analogy_profile"]["cheey"]),
    )

    packet_profile = Counter(row["gdt590_packet_class"] for row in packets)
    check("BATH_PACKET_COUNT", len(packets) == 11, str(len(packets)))
    check(
        "BATH_PACKET_PROFILE",
        packet_profile == {"FILL_ONLY": 5, "CLEAN_BODY_PLUS_FILL": 4, "BLOCKED_STATION_PLUS_FILL": 2},
        str(packet_profile),
    )
    changed_packets = [row for row in packets if row["gdt590_changed"] == "YES"]
    check("PACKET_CHANGED_SET", {row["source_event_or_card_id"] for row in changed_packets} == TARGET_EVENTS, "four target packets")
    check(
        "PACKET_BODY_AND_FILL_VISIBLE",
        all("Y=Körper" in row["gdt590_ordered_written_slot_lemmas_de"] and "AIIN=Badfüllung" in row["gdt590_ordered_written_slot_lemmas_de"] for row in changed_packets),
        "four packets preserve both written carriers",
    )

    upstream_guard_fields = list(data["body_guard"][0])
    check("BODY_GUARD_COUNT", len(guard) == 361, str(len(guard)))
    check(
        "BODY_GUARD_UPSTREAM_PROJECTION",
        [project(row, upstream_guard_fields) for row in guard] == data["body_guard"],
        "all GDT589 columns retained",
    )
    changed_guard = [row for row in guard if row["gdt590_changed"] == "YES"]
    check("BODY_GUARD_CHANGED_SET", {row["source_event_or_card_id"] for row in changed_guard} == TARGET_EVENTS, "four exact host changes")
    check("BODY_GUARD_CHANGED_LEMMA", all(row["gdt590_y_lemma_sequence"] == "Körper" for row in changed_guard), "four body defaults")

    upstream_slot_fields = list(data["slots"][0])
    check("SLOT_COUNT", len(slots) == 1243, str(len(slots)))
    check("SLOT_UPSTREAM_PROJECTION", [project(row, upstream_slot_fields) for row in slots] == data["slots"], "all GDT589 slot columns retained")
    changed_slots = [row for row in slots if row["gdt590_changed"] == "YES"]
    check("SLOT_CHANGED_COUNT", len(changed_slots) == 4, str(len(changed_slots)))
    check("SLOT_CHANGED_HOST_SET", {row["primary_governor_key"] for row in changed_slots} == TARGET_HOSTS, "one Y slot at each target")
    check("SLOT_CHANGED_ROOT", all(row["carrier_root"] == "Y" and row["gdt590_lemma_de"] == "Körper" for row in changed_slots), "Y only")
    target_aiin_slots = [row for row in slots if row["primary_governor_key"] in TARGET_HOSTS and row["carrier_root"] == "AIIN"]
    check("AIIN_FILL_RETAINED", len(target_aiin_slots) == 4 and all(row["gdt590_lemma_de"] == "Badfüllung" and row["gdt590_changed"] == "NO" for row in target_aiin_slots), "four unchanged Badfüllung slots")
    bio_y = [row for row in slots if row["register"] == "BIOLOGICAL" and row["carrier_root"] == "Y"]
    check("BIO_Y_COUNT", len(bio_y) == 406, str(len(bio_y)))
    check("BIO_Y_PROFILE", Counter(row["gdt590_lemma_de"] for row in bio_y) == {"Stationsansatz": 334, "Körper": 65, "Strom": 7}, str(Counter(row["gdt590_lemma_de"] for row in bio_y)))

    upstream_statement_fields = list(data["statements"][0])
    check("STATEMENT_COUNT", len(statements) == 793, str(len(statements)))
    check("STATEMENT_UPSTREAM_PROJECTION", [project(row, upstream_statement_fields) for row in statements] == data["statements"], "all GDT589 reader channels retained")
    changed_statements = [row for row in statements if row["gdt590_reader_changed"] == "YES"]
    unchanged_statements = [row for row in statements if row["gdt590_reader_changed"] == "NO"]
    check("STATEMENT_CHANGED_SET", {row["statement_id"] for row in changed_statements} == TARGET_STATEMENTS, "four exact readers")
    check("STATEMENT_UNCHANGED_COUNT", len(unchanged_statements) == 789, str(len(unchanged_statements)))
    check("STATEMENT_BYTE_RETAINED", all(row["gdt590_primary_reader_de"] == row["gdt589_primary_reader_de"] for row in unchanged_statements), "789/789")
    changed_statement_by_id = {row["statement_id"]: row for row in changed_statements}
    check(
        "STATEMENT_TARGET_CLAUSES",
        all(target["body_clause_de"] in changed_statement_by_id[target["statement_id"]]["gdt590_primary_reader_de"] for target in TARGETS.values()),
        "four body clauses installed",
    )
    check("STATEMENT_STATION_ALTERNATIVES", all("Stationsansatz" in row["gdt590_retained_station_clause_de"] for row in changed_statements), "four station alternatives")
    check(
        "REPEAT_OVERLAYS_RETAINED",
        all(
            row["gdt589_count_overlay"] == upstream["gdt589_count_overlay"]
            and row["gdt589_written_carrier_overlay_de"] == upstream["gdt589_written_carrier_overlay_de"]
            for row, upstream in zip(statements, data["statements"])
        ),
        "793 original written-repeat channels unchanged",
    )

    check("VISUAL_COUNT", len(visuals) == 4, str(len(visuals)))
    check("VISUAL_EVENT_SET", {row["source_event_id"] for row in visuals} == TARGET_EVENTS, "one host-specific row each")
    check("VISUAL_PROSE_NOT_LABEL", all(row["source_text_kind"] == "P" and row["exact_graphical_annotation_match"] == "NO" and row["visual_unit_class"] == "PROSE_NOT_GRAPHICAL_LABEL" for row in visuals), "four prose targets")
    check("VISUAL_NO_OWNER", all(row["visual_owner_status"] == "NO_EXACT_WORD_OR_OBJECT_OWNER" for row in visuals), "no word-level image owner")
    check("VISUAL_IMAGE_PROFILE", Counter(row["image_only_preference_de"] for row in visuals) == {"Stationsansatz": 3, "Körper": 1}, str(Counter(row["image_only_preference_de"] for row in visuals)))
    check("VISUAL_OVERALL_PROFILE", Counter(row["overall_preference_de"] for row in visuals) == {"Körper": 4}, "four overall body defaults")
    visual_by_event = {row["source_event_id"]: row for row in visuals}
    check("VISUAL_E2652_REMOTE_Y", visual_by_event["G407-E2652"]["y_carrier_event_id"] == "G407-E2653" and visual_by_event["G407-E2652"]["action_word_ordinal_in_line"] == "2" and visual_by_event["G407-E2652"]["y_word_ordinal_in_line"] == "3", "SH W2, remote Y W3")
    check("VISUAL_F82_LAYOUT", visual_by_event["G407-E3182"]["layout_segment_trace"] == "S1=W1–W4|LAYOUT_INTERRUPTION|S2=W5–W8;TARGET=S2/W2", "documented W4 break")
    image_source_by_page = {row["physical_page"]: row for row in data["image_sources"]}
    check(
        "VISUAL_IMAGE_PROVENANCE",
        all(
            row["review_image_url"] == image_source_by_page[row["physical_page"]]["image_url"]
            and row["review_image_sha256"] == image_source_by_page[row["physical_page"]]["sha256"]
            for row in visuals
        ),
        "official IIIF source records",
    )

    check("READER_FOUR_PASSAGES", reader.count("## G407-E") == 4, "four complete passages")
    check("READER_VISUAL_DISSENT", "Bildlich neigt nur E2637 leicht zu Körper" in reader and all(event in reader for event in TARGET_EVENTS), "1 body lean / 3 station leans explicit")
    check("READER_NO_PATIENT_PROMOTION", "Patient" not in reader, "no patient label")
    check("INLINE_SIZE_CAP", all(path.stat().st_size <= 5_000_000 for name, path in OUTPUTS.items() if name != "validation"), "every artifact at or below five MB")

    tracked_outputs = [path for name, path in OUTPUTS.items() if name != "validation"]
    before = {str(path): sha256(path) for path in tracked_outputs}
    rebuild_run = subprocess.run(
        ["python3", str(ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/src/run.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    after = {str(path): sha256(path) for path in tracked_outputs}
    check("REBUILD_EXIT", rebuild_run.returncode == 0, rebuild_run.stderr[-500:] or "exit 0")
    check("BYTE_IDENTICAL_REBUILD", before == after, f"{len(tracked_outputs)} artifacts")

    status = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    payload = {
        "experiment_id": "GDT590",
        "status": status,
        "checks_passed": sum(row["status"] == "PASS" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUTS["validation"].write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
