#!/usr/bin/env python3
"""Validate GDT591's complete bath-episode continuity replay."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from typing import Any

from continuity_model import (
    ADMITTED_PAGES,
    COMPARATOR_IDS,
    INPUTS,
    OUTPUTS,
    ROOT,
    STATUS,
    TARGET_META,
    build,
    load_inputs,
    read_tsv,
    render_reader,
    sha256,
)


TABLE_NAMES = (
    "hosts",
    "statements",
    "paragraphs",
    "statement_transitions",
    "paragraph_transitions",
    "remote",
    "comparators",
    "targets",
)


def textual(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def main() -> int:
    data = load_inputs()
    rows = {name: read_tsv(OUTPUTS[name]) for name in TABLE_NAMES}
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

    hosts = rows["hosts"]
    statements = rows["statements"]
    paragraphs = rows["paragraphs"]
    statement_transitions = rows["statement_transitions"]
    paragraph_transitions = rows["paragraph_transitions"]
    remote = rows["remote"]
    comparators = rows["comparators"]
    targets = rows["targets"]

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check(
        "INPUT_HASHES",
        result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()},
        f"{len(INPUTS)} fixed inputs",
    )
    check("COMPLETE_COMPARATOR_POPULATION", len(data["hosts"]) == 953, str(len(data["hosts"])))
    check(
        "COMPLETE_GOVERNOR_KEYS_UNIQUE",
        len({row["primary_governor_key"] for row in data["hosts"]}) == 953,
        "953 exact keys; event IDs need not be unique",
    )
    all_rows = [row for name in TABLE_NAMES for row in rows[name]]
    pages = {row["physical_page"] for row in all_rows if row.get("physical_page")}
    check("NO_NEW_PAGE", pages <= ADMITTED_PAGES, f"{len(pages)} already admitted pages represented")
    check("SEALED_F84_ABSENT", not any(page.lower().startswith("f84") for page in pages), "no f84/f84r row")

    rebuilt = build(data)
    for name in TABLE_NAMES:
        check(
            f"{name.upper()}_IN_MEMORY_REBUILD",
            rows[name] == textual(rebuilt[name]),
            f"{len(rows[name])} rows",
        )
    check("RESULT_IN_MEMORY_REBUILD", result == rebuilt["result"], "compact result exact")
    check("READER_IN_MEMORY_REBUILD", reader == render_reader(rebuilt), "reader exact")

    check("BATH_HOST_COUNT", len(hosts) == 92, str(len(hosts)))
    check("BATH_HOST_UNIQUE", len({row["primary_governor_key"] for row in hosts}) == 92, "92 governors")
    bath_keys = {row["primary_governor_key"] for row in hosts}
    phrase584_counts = Counter(row["primary_governor_key"] for row in data["gdt584_phrases"])
    phrase587_counts = Counter(row["primary_governor_key"] for row in data["gdt587_phrases"])
    check(
        "GDT584_BATH_PHRASE_EXACT_ONE",
        all(phrase584_counts[key] == 1 for key in bath_keys),
        "92/92 exact governor joins",
    )
    check(
        "GDT587_BATH_PHRASE_EXACT_ONE",
        all(phrase587_counts[key] == 1 for key in bath_keys),
        "92/92 exact governor joins",
    )
    check("BATH_PAGE_COUNT", len({row["physical_page"] for row in hosts}) == 6, "six fixed bath pages")
    host_roles = Counter(row["gdt590_role"] for row in hosts)
    check("HOST_ROLE_PROFILE", host_roles == {"BODY": 52, "STATION": 40}, str(host_roles))
    check(
        "HOST_ROLE_BLOCKER_INVARIANT",
        all(
            (row["gdt590_role"] == "BODY" and row["body_blockers_present"] == "NONE")
            or (row["gdt590_role"] == "STATION" and row["body_blockers_present"] != "NONE")
            for row in hosts
        ),
        "52 clean body / 40 blocked station",
    )
    y_profile = {
        role: sum(int(row["y_slot_count"]) for row in hosts if row["gdt590_role"] == role)
        for role in ("BODY", "STATION")
    }
    check("Y_SLOT_PROFILE", y_profile == {"BODY": 55, "STATION": 57}, str(y_profile))
    check("CARRIER_SLOT_COUNT", sum(int(row["carrier_slot_count"]) for row in hosts) == 127, "127")
    carrier_root_profile = Counter(
        root
        for row in hosts
        for root in row["written_root_sequence"].split("+")
    )
    check(
        "CARRIER_ROOT_PROFILE",
        carrier_root_profile == {"Y": 112, "AIIN": 6, "AIN": 4, "OR": 5},
        str(carrier_root_profile),
    )
    check("DIRECT_CARRIER_COUNT", sum(int(row["direct_carrier_count"]) for row in hosts) == 88, "88")
    check("REMOTE_CARRIER_COUNT_FROM_HOSTS", sum(int(row["remote_carrier_count"]) for row in hosts) == 39, "39")
    check(
        "HOST_CARRIER_PARTITION",
        all(
            int(row["direct_carrier_count"]) + int(row["remote_carrier_count"])
            == int(row["carrier_slot_count"])
            for row in hosts
        ),
        "direct + remote = complete carrier count at 92/92 hosts",
    )
    fill_profile = Counter(
        (row["gdt590_role"], "AIIN" in row["written_root_sequence"].split("+"))
        for row in hosts
    )
    check(
        "BATH_FILL_ROLE_PROFILE",
        fill_profile
        == {("BODY", False): 48, ("BODY", True): 4, ("STATION", False): 38, ("STATION", True): 2},
        str(fill_profile),
    )
    check(
        "NO_READER_BOUNDARY_INSIDE_BATH_HOST",
        all(row["paragraph_boundary_inside_host"] == "NONE" for row in hosts),
        "92/92",
    )

    check("STATEMENT_COUNT", len(statements) == 64, str(len(statements)))
    statement_classes = Counter(row["episode_class"] for row in statements)
    check(
        "STATEMENT_CLASS_PROFILE",
        statement_classes == {"BODY_ONLY": 30, "STATION_ONLY": 25, "MIXED_BODY_STATION": 9},
        str(statement_classes),
    )
    host_count_profile = Counter(int(row["bath_host_count"]) for row in statements)
    check(
        "STATEMENT_HOST_COUNT_PROFILE",
        host_count_profile == {1: 50, 2: 7, 3: 5, 4: 1, 9: 1},
        str(host_count_profile),
    )
    expected_mixed = {
        "G407-S085": "STATION→BODY→BODY",
        "G407-S119": "BODY→BODY→STATION→BODY→STATION→BODY→BODY→BODY→BODY",
        "G407-S382": "BODY→STATION",
        "G407-S392": "BODY→STATION→BODY→STATION",
        "G407-S455": "BODY→STATION",
        "G407-S495": "STATION→BODY→BODY",
        "G407-S531": "STATION→BODY→BODY",
        "G407-S538": "STATION→BODY",
        "G407-S599": "BODY→STATION→STATION",
    }
    actual_mixed = {
        row["statement_id"]: row["role_sequence"]
        for row in statements
        if row["episode_class"] == "MIXED_BODY_STATION"
    }
    check("MIXED_STATEMENT_SEQUENCES", actual_mixed == expected_mixed, str(actual_mixed))
    upstream_statement_by_id = {row["statement_id"]: row for row in data["statements"]}
    check(
        "GDT590_READER_FROZEN",
        all(
            row["gdt590_primary_reader_de"]
            == upstream_statement_by_id[row["statement_id"]]["gdt590_primary_reader_de"]
            for row in statements
        ),
        "64/64 statements unchanged",
    )
    changed_hosts = [row for row in hosts if row["gdt590_changed"] == "YES"]
    check(
        "FOUR_BODY_CLAUSE_PATCHES",
        len(changed_hosts) == 4
        and all("Körper" in row["gdt590_reader_clause_de"] and "Stationsansatz" not in row["gdt590_reader_clause_de"] for row in changed_hosts),
        "four exact GDT590 host clauses retained",
    )

    statement_pairs = Counter(
        (row["from_role"], row["to_role"]) for row in statement_transitions
    )
    check("STATEMENT_TRANSITION_COUNT", len(statement_transitions) == 28, str(len(statement_transitions)))
    check(
        "STATEMENT_TRANSITION_PROFILE",
        statement_pairs
        == {("BODY", "BODY"): 10, ("STATION", "STATION"): 4, ("BODY", "STATION"): 7, ("STATION", "BODY"): 7},
        str(statement_pairs),
    )
    switches = [row for row in statement_transitions if row["role_switch"] == "YES"]
    check("STATEMENT_SWITCH_COUNT", len(switches) == 14, str(len(switches)))
    check("SWITCH_NEW_GOVERNOR", all(row["new_governor"] == "YES" for row in switches), "14/14")
    check("TRANSITIONS_SAME_PHYSICAL_PARAGRAPH", all(row["physical_same_paragraph"] == "YES" for row in statement_transitions), "28/28")
    check("SWITCH_BLOCKER_LICENSE", all(row["switch_license"] == "BLOCKER_STATE_CHANGES_WITH_ROLE" for row in switches), "14/14")
    controlled_switches = [row for row in switches if int(row["intervening_control_count"]) > 0]
    check("CONTROLLED_SWITCH_COUNT", len(controlled_switches) == 7, str(len(controlled_switches)))
    control_row_profile = Counter(
        "OT" if "OT" in row["intervening_control_roots"].split("|") else "OL"
        for row in controlled_switches
    )
    check("CONTROLLED_SWITCH_ROOT_PROFILE", control_row_profile == {"OL": 5, "OT": 2}, str(control_row_profile))
    control_token_profile = Counter(
        root
        for row in controlled_switches
        for root in row["intervening_control_roots"].split("|")
    )
    check("CONTROL_TOKEN_PROFILE", control_token_profile == {"OL": 6, "OT": 2}, str(control_token_profile))
    check(
        "SWITCH_READER_BOUNDARY_COUNT",
        sum(int(row["intervening_reader_boundary_count"]) > 0 for row in switches) == 2,
        "2/14 reader-boundary crossings, 0/14 physical-paragraph crossings",
    )

    check("PARAGRAPH_COUNT", len(paragraphs) == 17, str(len(paragraphs)))
    paragraph_classes = Counter(row["paragraph_class"] for row in paragraphs)
    check(
        "PARAGRAPH_CLASS_PROFILE",
        paragraph_classes == {"MIXED_BODY_STATION": 11, "BODY_ONLY": 4, "STATION_ONLY": 2},
        str(paragraph_classes),
    )
    paragraph_pairs = Counter(
        (row["from_role"], row["to_role"]) for row in paragraph_transitions
    )
    check("PARAGRAPH_TRANSITION_COUNT", len(paragraph_transitions) == 75, str(len(paragraph_transitions)))
    check(
        "PARAGRAPH_TRANSITION_PROFILE",
        paragraph_pairs
        == {("BODY", "BODY"): 25, ("STATION", "STATION"): 15, ("BODY", "STATION"): 17, ("STATION", "BODY"): 18},
        str(paragraph_pairs),
    )
    paragraph_switches = [row for row in paragraph_transitions if row["role_switch"] == "YES"]
    check("PARAGRAPH_SWITCH_COUNT", len(paragraph_switches) == 35, str(len(paragraph_switches)))
    switch_scope = Counter(row["same_statement"] for row in paragraph_switches)
    check("PARAGRAPH_SWITCH_SCOPE", switch_scope == {"YES": 14, "NO": 21}, str(switch_scope))

    check("REMOTE_ROW_COUNT", len(remote) == 39, str(len(remote)))
    check("REMOTE_HOST_COUNT", len({row["primary_governor_key"] for row in remote}) == 27, "27")
    remote_host_roles = Counter(
        row["gdt590_role"]
        for row in {row["primary_governor_key"]: row for row in remote}.values()
    )
    check("REMOTE_HOST_ROLE_PROFILE", remote_host_roles == {"BODY": 9, "STATION": 18}, str(remote_host_roles))
    remote_roots = Counter(row["carrier_root"] for row in remote)
    check("REMOTE_ROOT_PROFILE", remote_roots == {"Y": 25, "AIIN": 6, "AIN": 4, "OR": 4}, str(remote_roots))
    remote_geometries = Counter(row["attachment_geometry"] for row in remote)
    check(
        "REMOTE_GEOMETRY_PROFILE",
        remote_geometries == {"PREVIOUS_CARD_ACTION": 19, "INHERITED_ACTION": 12, "BOUNDED_NEXT_CARD_ACTION": 8},
        str(remote_geometries),
    )
    check("REMOTE_LOOKAHEAD_PROFILE", Counter(row["lookahead_cards"] for row in remote) == {"0": 31, "1": 8}, "31 zero / 8 one")
    check(
        "REMOTE_FIXED_GOVERNORS",
        all(row["effective_grammar_host_key"] == row["primary_governor_key"] for row in remote),
        "39/39",
    )
    check(
        "REMOTE_NO_BOUNDARY_CROSS",
        all(row["owner_boundary_crossed"] == "NO" and row["statement_boundary_crossed"] == "NO" for row in remote),
        "39/39",
    )
    check(
        "REMOTE_SCOPE_PROFILE",
        all(row["boundary_class"] == "RUNNING_OBJECT_FUNCTION" and row["realization_scope"] == "PRIMARY_GOVERNOR" for row in remote),
        "39 running object functions under primary governor",
    )
    assignment_by_slot = {row["carrier_slot_id"]: row for row in data["assignments"]}
    phrase_by_key = {
        row["primary_governor_key"]: row
        for row in data["gdt587_phrases"]
        if row["primary_governor_key"] in bath_keys
    }
    check(
        "REMOTE_ASSIGNMENT_LOCALITY",
        all(
            assignment_by_slot[row["carrier_slot_id"]]["statement_or_record_id"]
            == phrase_by_key[row["primary_governor_key"]]["statement_id"]
            and assignment_by_slot[row["carrier_slot_id"]]["owner"]
            == phrase_by_key[row["primary_governor_key"]]["owner_id"]
            for row in remote
        ),
        "39/39 remain inside exact phrase statement and owner",
    )
    e2652_remote = [row for row in remote if row["source_event_id"] == "G407-E2652"]
    check(
        "E2652_REMOTE_TRACE",
        {(row["carrier_slot_id"], row["carrier_root"], row["attachment_geometry"], row["lookahead_cards"]) for row in e2652_remote}
        == {
            ("RUNNING:G407-E2651@1", "AIIN", "BOUNDED_NEXT_CARD_ACTION", "1"),
            ("RUNNING:G407-E2653@2", "Y", "PREVIOUS_CARD_ACTION", "0"),
        },
        "daiin before / qolchey after bare SH",
    )

    check("COMPARATOR_COUNT", len(comparators) == 7, str(len(comparators)))
    check("COMPARATOR_EVENT_SET", {row["source_event_id"] for row in comparators} == set(COMPARATOR_IDS), "fixed ladder")
    check(
        "E2652_EXACT_SIGNATURE_UNIQUE",
        result["e2652_exact_signature_population_count"] == 1,
        "one AIIN|SH|Y + direct SH host among 953",
    )
    exact_comparators = [row for row in comparators if row["exact_target_signature"] == "YES"]
    check(
        "COMPARATOR_TARGET_ONLY_EXACT",
        len(exact_comparators) == 1 and exact_comparators[0]["source_event_id"] == "G407-E2652",
        "E2652 only",
    )
    continuity_key_by_event = {row["source_event_id"]: row["primary_governor_key"] for row in hosts}
    check(
        "COMPARATOR_EXACT_GOVERNOR_JOIN",
        all(row["primary_governor_key"] == continuity_key_by_event[row["source_event_id"]] for row in comparators),
        "no event-only multi-action collision",
    )
    e2652_host = next(row for row in hosts if row["source_event_id"] == "G407-E2652")
    check(
        "E2652_ALL_REMOTE_BARE_SH",
        e2652_host["complete_host_values_written"] == "AIIN|SH|Y"
        and e2652_host["direct_governor_tokens"] == "SH"
        and e2652_host["direct_carrier_count"] == "0"
        and e2652_host["remote_carrier_count"] == "2",
        "unique exact structure",
    )

    check("TARGET_COUNT", len(targets) == 4, str(len(targets)))
    check("TARGET_EVENT_SET", {row["source_event_id"] for row in targets} == set(TARGET_META), "four GDT590 targets")
    check("TARGET_BODY_FIRST", all(row["overall_preference_de"] == "Körper" for row in targets), "4/4")
    check("TARGET_STATION_VISIBLE", all(row["retained_alternative_de"] == "Stationsansatz" for row in targets), "4/4")
    target_by_event = {row["source_event_id"]: row for row in targets}
    check(
        "E2652_LAYOUT_COMPACT",
        target_by_event["G407-E2652"]["line_wrap_class"] == "RETURN_WRAP__AIIN_SH_OLY_ADJACENT_W1_W3"
        and "daiin sh qolchey" in target_by_event["G407-E2652"]["layout_aware_eva"],
        "event-remote but W1-W3 adjacent",
    )
    check(
        "F82_LAYOUT_INTERRUPTION_RETAINED",
        "LAYOUT_INTERRUPTION" in target_by_event["G407-E3182"]["layout_aware_eva"],
        "f82r.1 internal break visible",
    )

    check("READER_TARGET_COUNT", reader.count("### G407-E") == 4, "four targets")
    check("READER_MIXED_STATEMENT_COUNT", reader.count("### G407-S") == 9, "nine mixed statements")
    check("READER_REMOTE_DEFINITION", "anderes Quellereignis als der Handlungsanker" in reader and "W1–W3" in reader, "spatial ambiguity removed")
    check("READER_STATION_RIVAL", "Stationsansatz" in reader and "Gegenlesung" in reader, "alternative visible")
    check(
        "INLINE_SIZE_CAP",
        all(path.stat().st_size <= 5_000_000 for name, path in OUTPUTS.items() if name != "validation"),
        "every generated artifact at or below five MB",
    )

    tracked_outputs = [path for name, path in OUTPUTS.items() if name != "validation"]
    before = {str(path): sha256(path) for path in tracked_outputs}
    rebuild_run = subprocess.run(
        ["python3", str(ROOT / "experiments/yolo/gdt591_bath_episode_continuity/src/run.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    after = {str(path): sha256(path) for path in tracked_outputs}
    check("REBUILD_EXIT", rebuild_run.returncode == 0, rebuild_run.stderr[-500:] or "exit 0")
    check("BYTE_IDENTICAL_REBUILD", before == after, f"{len(tracked_outputs)} generated artifacts")

    status = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    payload = {
        "experiment_id": "GDT591",
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
