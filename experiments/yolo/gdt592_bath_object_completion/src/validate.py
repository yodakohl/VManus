#!/usr/bin/env python3
"""Validate GDT592's complete bath-object working edition."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from typing import Any

from object_model import (
    ADMITTED_PAGES,
    ANAPHORIC_OBJECT_FORMS,
    BATH_PAGES,
    BODY_BLOCKERS,
    INPUTS,
    LOCAL_HANDOFF_EXPECTED_KEYS,
    LOCAL_HANDOFF_FORM_OVERRIDES,
    LOCAL_HANDOFFS,
    OBJECT_FORMS,
    OUTPUTS,
    ROOT,
    STATUS,
    build,
    event_number,
    load_inputs,
    locus_line_number,
    read_tsv,
    render_reader,
    sentence_case,
    sha256,
)


TABLE_NAMES = (
    "actions",
    "episodes",
    "objectless",
    "fill_only",
    "carries",
    "handoffs",
    "gdt569_divergences",
    "blockers",
    "pages",
    "patched_statements",
    "statements",
)

EXPECTED_OBJECTS = {
    "BODY": 53,
    "STATION": 81,
    "BATH_OBJECT": 107,
    "BATH_UNIT": 9,
    "PORTION": 4,
}
EXPECTED_ROUTES = {
    "WRITTEN_Y_GDT590": 92,
    "WRITTEN_OR_UNIT": 6,
    "WRITTEN_AIN_PORTION": 2,
    "BODY_BLOCKER_STATION": 25,
    "INTERVENING_OBJECT_HANDOFF": 13,
    "EPISODE_CARRY": 11,
    "COLD_BATH_OBJECT_DEFAULT": 105,
}
EXPECTED_CARRY_EVENTS = {
    "G407-E1579", "G407-E1713", "G407-E2471", "G407-E2481",
    "G407-E2638", "G407-E2881", "G407-E2914", "G407-E3219",
    "G407-E3379", "G407-E3489", "G407-E3590",
}
EXPECTED_GDT569_RELATIONS = {
    "NO_GDT569_STATE_ROW": 137,
    "GDT569_LOCAL_EXPLICIT_PARALLEL": 8,
    "GDT569_CARRY_FILL_PARALLEL": 20,
    "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT": 61,
    "GDT569_CURRENT_WRITTEN_OBJECT_PRECEDENCE": 2,
    "GDT569_CARRY_CLASS_ALIGNED": 24,
    "GDT569_CARRY_CLASS_DIVERGENCE_RETAINED": 2,
}
EXPECTED_GDT569_ALIGNED_SLOTS = {
    f"RUNNING:G407-E{suffix}"
    for suffix in (
        "1492@2", "1579@1", "1673@1", "1713@1", "1746@1", "1829@1",
        "2736@1", "2821@2", "2881@1", "2914@1", "3034@1", "3067@1",
        "3072@2", "3115@2", "3116@2", "3234@1", "3304@1", "3379@1",
        "3428@2", "3550@1", "3612@1", "3614@1", "3625@1", "3734@2",
    )
}


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

    actions = rows["actions"]
    episodes = rows["episodes"]
    objectless = rows["objectless"]
    fill_only = rows["fill_only"]
    carries = rows["carries"]
    handoffs = rows["handoffs"]
    gdt569_divergences = rows["gdt569_divergences"]
    blockers = rows["blockers"]
    pages = rows["pages"]
    patched_statements = rows["patched_statements"]
    statements = rows["statements"]

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check(
        "INPUT_HASHES",
        result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()},
        f"{len(INPUTS)} fixed inputs",
    )
    output_pages = {
        row["physical_page"]
        for name in TABLE_NAMES
        for row in rows[name]
        if row.get("physical_page")
    }
    check("NO_NEW_PAGE", output_pages <= ADMITTED_PAGES, f"{len(output_pages)} admitted pages")
    check("BATH_OUTPUT_PAGES", {row["physical_page"] for row in actions} == BATH_PAGES, str(sorted(BATH_PAGES)))
    check("SEALED_F84_ABSENT", not any(page.lower().startswith("f84") for page in output_pages), "no f84/f84r row")

    rebuilt = build(data)
    for name in TABLE_NAMES:
        check(
            f"{name.upper()}_IN_MEMORY_REBUILD",
            rows[name] == textual(rebuilt[name]),
            f"{len(rows[name])} rows",
        )
    check("RESULT_IN_MEMORY_REBUILD", result == rebuilt["result"], "compact result exact")
    check("READER_IN_MEMORY_REBUILD", reader == render_reader(rebuilt), "complete reader exact")

    check("BATH_ACTION_COUNT", len(actions) == 254, str(len(actions)))
    check("BATH_GOVERNORS_UNIQUE", len({row["primary_governor_key"] for row in actions}) == 254, "254 exact keys")
    bath583 = [row for row in data["gdt583_assignments"] if row["gdt583_rule_id"] == "SH_BIO_BATHE"]
    bath584 = [row for row in data["gdt584_phrases"] if row["gdt584_rule_id"] == "SH_BIO_BATHE"]
    check("GDT583_BATH_POPULATION", len(bath583) == 254, str(len(bath583)))
    check("GDT584_BATH_POPULATION", len(bath584) == 254, str(len(bath584)))
    check(
        "BATH_POPULATION_EXACT_JOIN",
        {row["primary_governor_key"] for row in actions}
        == {row["primary_governor_key"] for row in bath583}
        == {row["primary_governor_key"] for row in bath584},
        "GDT583 = GDT584 = GDT592",
    )
    check("BATH_STATEMENT_COUNT", len({row["statement_id"] for row in actions}) == 177, "177")
    check("BATH_EPISODE_COUNT", len(episodes) == 190, str(len(episodes)))
    check("BATH_PAGE_COUNT", len(pages) == 6, str(len(pages)))

    object_profile = Counter(row["gdt592_object_class"] for row in actions)
    route_profile = Counter(row["object_selection_route"] for row in actions)
    check("OBJECT_PROFILE", object_profile == EXPECTED_OBJECTS, str(object_profile))
    check("SELECTION_ROUTE_PROFILE", route_profile == EXPECTED_ROUTES, str(route_profile))
    forms_exact = True
    for row in actions:
        event_id = row["source_event_id"]
        object_class = row["gdt592_object_class"]
        if event_id in LOCAL_HANDOFF_FORM_OVERRIDES:
            expected_lemma, expected_form = LOCAL_HANDOFF_FORM_OVERRIDES[event_id]
        elif row["object_selection_route"] in {
            "INTERVENING_OBJECT_HANDOFF", "EPISODE_CARRY"
        }:
            expected_lemma = OBJECT_FORMS[object_class][0]
            expected_form = ANAPHORIC_OBJECT_FORMS[object_class]
        else:
            expected_lemma, expected_form = OBJECT_FORMS[object_class]
        forms_exact &= (
            row["gdt592_object_lemma_de"], row["gdt592_object_form_de"]
        ) == (expected_lemma, expected_form)
    check(
        "OBJECT_LEMMA_FORMS",
        forms_exact,
        "254/254 base, anaphoric, or exact Stationseinheit override forms",
    )
    check("NO_EMPTY_OBJECT", all(row["gdt592_object_lemma_de"] for row in actions), "254/254")
    bath_goods = [row for row in actions if row["gdt592_object_class"] == "BATH_OBJECT"]
    check(
        "BADEGUT_FORM_PROFILE",
        len(bath_goods) == 107
        and all(row["gdt592_object_lemma_de"] == "Badegut" for row in bath_goods)
        and Counter(row["gdt592_object_form_de"] for row in bath_goods)
        == {"das zu badende Gut": 105, "dasselbe zu badende Gut": 2},
        "105 direct Badegut forms plus two anaphoric reuses",
    )

    written_y = [row for row in actions if row["object_selection_route"] == "WRITTEN_Y_GDT590"]
    gdt591_role_by_key = {
        row["primary_governor_key"]: row["gdt590_role"] for row in data["gdt591_hosts"]
    }
    check("WRITTEN_Y_COUNT", len(written_y) == 92, str(len(written_y)))
    check(
        "WRITTEN_Y_EXACT_GDT591_ROLE",
        all(row["gdt592_object_class"] == gdt591_role_by_key[row["primary_governor_key"]] for row in written_y),
        "92/92",
    )
    check("WRITTEN_Y_PROFILE", Counter(row["gdt592_object_class"] for row in written_y) == {"BODY": 52, "STATION": 40}, "52/40")
    check(
        "WRITTEN_UNIT_PORTION",
        all(row["gdt592_object_class"] == "BATH_UNIT" for row in actions if row["object_selection_route"] == "WRITTEN_OR_UNIT")
        and all(row["gdt592_object_class"] == "PORTION" for row in actions if row["object_selection_route"] == "WRITTEN_AIN_PORTION"),
        "6 OR units / 2 AIN portions",
    )
    explicit = [row for row in actions if row["object_selection_route"].startswith("WRITTEN_")]
    check("WRITTEN_OBJECT_COUNT", len(explicit) == 100, str(len(explicit)))
    check(
        "WRITTEN_OBJECT_CLAUSES_UNCHANGED",
        all(
            row["clause_patch_required"] == "NO"
            and row["gdt592_completed_clause_de"] == row["gdt590_current_clause_de"]
            for row in explicit
        ),
        "100/100",
    )

    check("OBJECTLESS_COUNT", len(objectless) == 149, str(len(objectless)))
    check("OBJECTLESS_NO_CARRIER", all(row["carrier_slot_count"] == "0" and row["carrier_root_sequence"] == "NONE" for row in objectless), "149/149")
    check("OBJECTLESS_PATCHED", all(row["clause_patch_required"] == "YES" for row in objectless), "149/149")
    check(
        "OBJECTLESS_OBJECT_PROFILE",
        Counter(row["gdt592_object_class"] for row in objectless)
        == {"BATH_OBJECT": 103, "STATION": 40, "PORTION": 2, "BODY": 1, "BATH_UNIT": 3},
        str(Counter(row["gdt592_object_class"] for row in objectless)),
    )

    check("FILL_ONLY_COUNT", len(fill_only) == 5, str(len(fill_only)))
    check("FILL_ONLY_ROOT", all(row["carrier_root_sequence"] == "AIIN" and row["aiin_fill_present"] == "YES" for row in fill_only), "5/5")
    fill_by_event = {row["source_event_id"]: row for row in fill_only}
    check(
        "FILL_ONLY_EVENT_SET",
        set(fill_by_event) == {"G407-E2426", "G407-E2647", "G407-E3218", "G407-E3441", "G407-E3621"},
        str(sorted(fill_by_event)),
    )
    check(
        "FILL_ONLY_OBJECT_PROFILE",
        Counter(row["gdt592_object_class"] for row in fill_only) == {"BATH_OBJECT": 4, "STATION": 1},
        "four cold Badegut / E3621 local Station handoff",
    )
    check(
        "FILL_ONLY_COMPOSITION",
        all("im Bad bei der angegebenen Füllung" in row["gdt592_completed_clause_de"] for row in fill_only),
        "5/5 keep fill as parameter",
    )
    check(
        "AIIN_NEVER_SELECTS_OBJECT",
        all(not row["object_selection_route"].startswith("WRITTEN_AIIN") for row in actions),
        "AIIN only marks fill",
    )

    patch_actions = [row for row in actions if row["clause_patch_required"] == "YES"]
    check("CLAUSE_PATCH_COUNT", len(patch_actions) == 154, str(len(patch_actions)))
    check(
        "PATCH_POPULATION_PARTITION",
        Counter("FILL_ONLY" if row["carrier_root_sequence"] == "AIIN" else "OBJECTLESS" for row in patch_actions)
        == {"OBJECTLESS": 149, "FILL_ONLY": 5},
        "149 + 5",
    )
    direct_prefix_exact = True
    for row in patch_actions:
        current = row["gdt590_current_clause_de"]
        object_form = row["gdt592_object_form_de"]
        if row["carrier_root_sequence"] == "NONE":
            expected = current.replace("Halte im Bad", f"Halte {object_form} im Bad", 1)
        else:
            expected = current.replace(
                "Halte die Badfüllung",
                f"Halte {object_form} im Bad bei der angegebenen Füllung",
                1,
            )
        direct_prefix_exact &= expected == row["gdt592_completed_clause_de"]
    check("PATCH_PREFIX_TRANSFORM_EXACT", direct_prefix_exact, "154/154 suffixes retained")
    duplicate_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in patch_actions:
        duplicate_groups[(row["statement_id"], row["gdt590_current_clause_de"])].append(row)
    duplicates = [members for members in duplicate_groups.values() if len(members) > 1]
    check(
        "DUPLICATE_CLAUSE_HOST_ALIGNMENT",
        len(duplicates) == 6 and sum(map(len, duplicates)) == 14 and max(map(len, duplicates)) == 3,
        "14 targets in six statements require ordinal alignment",
    )

    check("BLOCKER_DEFAULT_COUNT", len(blockers) == 25, str(len(blockers)))
    check("BLOCKER_DEFAULT_STATION", all(row["gdt592_object_class"] == "STATION" for row in blockers), "25/25")
    check(
        "BLOCKER_VALUES_PRESENT",
        all(
            row["body_blockers_present"] != "NONE"
            and set(row["body_blockers_present"].split("|")) <= BODY_BLOCKERS
            for row in blockers
        ),
        "25 exact blocker hosts",
    )
    check(
        "BLOCKER_BEATS_CARRY",
        all(row["object_selection_route"] == "BODY_BLOCKER_STATION" for row in blockers),
        "blocker precedence fixed",
    )

    check("CARRY_COUNT", len(carries) == 11, str(len(carries)))
    check("CARRY_EVENT_SET", {row["source_event_id"] for row in carries} == EXPECTED_CARRY_EVENTS, str(sorted(EXPECTED_CARRY_EVENTS)))
    check(
        "CARRY_OBJECT_PROFILE",
        Counter(row["gdt592_object_class"] for row in carries)
        == {"STATION": 7, "BATH_OBJECT": 2, "BODY": 1, "BATH_UNIT": 1},
        str(Counter(row["gdt592_object_class"] for row in carries)),
    )
    action_by_slot = {row["action_slot_id"]: row for row in actions}
    check("ACTION_SLOT_UNIQUE", len(action_by_slot) == 254, "254 slot-grained rows over 253 events")
    check(
        "CARRY_SOURCE_OBJECT_EXACT",
        all(
            row["carry_source_action_slot_id"] in action_by_slot
            and row["carry_source_event_id"]
            == action_by_slot[row["carry_source_action_slot_id"]]["source_event_id"]
            and row["gdt592_object_class"]
            == action_by_slot[row["carry_source_action_slot_id"]]["gdt592_object_class"]
            for row in carries
        ),
        "11/11 exact prior bath-action slots",
    )
    check(
        "CARRY_SAME_SEGMENT",
        all(
            row["statement_id"]
            == action_by_slot[row["carry_source_action_slot_id"]]["statement_id"]
            and row["bath_segment_key"]
            == action_by_slot[row["carry_source_action_slot_id"]]["bath_segment_key"]
            and row["paragraph_key"]
            == action_by_slot[row["carry_source_action_slot_id"]]["paragraph_key"]
            and row["reset_before"] == "NONE"
            for row in carries
        ),
        "11/11 same statement, reader segment, and physical paragraph",
    )
    phrases_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for phrase in data["gdt584_phrases"]:
        phrases_by_statement[phrase["statement_id"]].append(phrase)
    for members in phrases_by_statement.values():
        members.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
    carry_boundary_clean = True
    for row in carries:
        source = action_by_slot[row["carry_source_action_slot_id"]]
        source_ordinal = int(source["host_ordinal_in_statement"])
        target_ordinal = int(row["host_ordinal_in_statement"])
        between_with_source = [
            phrase for phrase in phrases_by_statement[row["statement_id"]]
            if source_ordinal <= int(phrase["host_ordinal_in_statement"]) < target_ordinal
        ]
        carry_boundary_clean &= all(
            phrase["paragraph_boundary"] != "PARAGRAPH_AFTER"
            for phrase in between_with_source
        )
    check("CARRY_NO_READER_BOUNDARY", carry_boundary_clean, "11/11")
    check(
        "CARRY_VISIBLE_DISTANCE_PROFILE",
        Counter(row["carry_intervening_event_number_count"] for row in carries)
        == {"0": 7, "1": 2, "2": 2}
        and Counter(row["carry_working_strength"] for row in carries)
        == {"ADJACENT_VISIBLE_EVENT": 7, "SHORT_VISIBLE_EVENT": 4}
        and Counter(row["carry_locus_line_distance"] for row in carries)
        == {"0": 10, "1": 1},
        "seven adjacent and four short; no medium/long bath-only carry remains",
    )
    carry_distance_exact = True
    for row in carries:
        source = action_by_slot[row["carry_source_action_slot_id"]]
        host_distance = int(row["host_ordinal_in_statement"]) - int(
            source["host_ordinal_in_statement"]
        )
        event_gap = event_number(row["source_event_id"]) - event_number(
            source["source_event_id"]
        ) - 1
        expected_strength = (
            "ADJACENT_VISIBLE_EVENT"
            if event_gap == 0
            else "SHORT_VISIBLE_EVENT"
            if event_gap <= 4
            else "MEDIUM_VISIBLE_EVENT"
            if event_gap <= 8
            else "LONG_VISIBLE_EVENT_WORKING"
        )
        carry_distance_exact &= (
            int(row["carry_host_ordinal_distance"]) == host_distance
            and int(row["carry_intervening_host_count"]) == host_distance - 1
            and int(row["carry_intervening_event_number_count"]) == event_gap
            and int(row["carry_locus_line_distance"])
            == locus_line_number(row["locus"])
            - locus_line_number(source["locus"])
            and row["carry_working_strength"] == expected_strength
        )
    check("CARRY_DISTANCE_RECOMPUTE", carry_distance_exact, "11/11 source-derived host and event distances")
    check(
        "CARRY_HOST_DISTANCE_PROFILE",
        Counter(row["carry_host_ordinal_distance"] for row in carries)
        == {"1": 7, "2": 3, "3": 1},
        "host distance is retained separately from visible event distance",
    )
    carry_by_event = {row["source_event_id"]: row for row in carries}
    check(
        "CARRY_DISTANCE_DIMENSION_WITNESSES",
        (
            carry_by_event["G407-E1713"]["carry_host_ordinal_distance"],
            carry_by_event["G407-E1713"]["carry_intervening_event_number_count"],
            carry_by_event["G407-E1713"]["carry_working_strength"],
        )
        == ("1", "1", "SHORT_VISIBLE_EVENT")
        and (
            carry_by_event["G407-E3489"]["carry_host_ordinal_distance"],
            carry_by_event["G407-E3489"]["carry_intervening_event_number_count"],
            carry_by_event["G407-E3489"]["carry_working_strength"],
        )
        == ("2", "0", "ADJACENT_VISIBLE_EVENT"),
        "E1713/E3489 prove that strength is not bucketed from host distance",
    )
    check(
        "CARRY_REFERENCE_CLASS_PROFILE",
        Counter(row["carry_reference_class"] for row in carries)
        == {"TYPED_BATH_ACTION_CARRY": 9, "NEUTRAL_DEFAULT_REUSE": 2},
        "nine typed carries and two neutral Badegut reuses",
    )
    check(
        "CARRY_GENERIC_ALTERNATIVE_VISIBLE",
        all(row["retained_generic_alternative_de"] == "Badegut" for row in carries),
        "11/11 keep the cold alternative visible",
    )
    unit_carry = [row for row in carries if row["gdt592_object_class"] == "BATH_UNIT"]
    check(
        "UNIT_CARRY_E2881",
        len(unit_carry) == 1
        and unit_carry[0]["source_event_id"] == "G407-E2881"
        and unit_carry[0]["carry_source_event_id"] == "G407-E2880",
        "one adjacent unit carry",
    )

    check("HANDOFF_COUNT", len(handoffs) == 13, str(len(handoffs)))
    check("HANDOFF_EVENT_SET", {row["source_event_id"] for row in handoffs} == set(LOCAL_HANDOFFS), str(sorted(LOCAL_HANDOFFS)))
    check(
        "HANDOFF_OBJECT_PROFILE",
        Counter(row["gdt592_object_class"] for row in handoffs)
        == {"STATION": 9, "PORTION": 2, "BATH_UNIT": 2},
        str(Counter(row["gdt592_object_class"] for row in handoffs)),
    )
    handoff_identity_exact = True
    for row in handoffs:
        donor_event, donor_root, object_class = LOCAL_HANDOFFS[row["source_event_id"]]
        handoff_identity_exact &= (
            row["handoff_donor_anchor_event_id"] == donor_event
            and row["handoff_source_root"] == donor_root
            and row["gdt592_object_class"] == object_class
            and row["handoff_source_primary_governor_key"]
            == LOCAL_HANDOFF_EXPECTED_KEYS[row["source_event_id"]]
            and int(row["handoff_host_ordinal_distance"]) > 0
            and int(row["handoff_intervening_event_number_count"]) >= 0
            and row["reset_before"] == "NONE"
        )
    check("HANDOFF_EXACT_IDENTITIES", handoff_identity_exact, "13 exact target/donor/root/key cards")
    check(
        "HANDOFF_DISTANCE_PROFILES",
        Counter(row["handoff_host_ordinal_distance"] for row in handoffs)
        == {"1": 7, "2": 4, "3": 2}
        and Counter(row["handoff_intervening_event_number_count"] for row in handoffs)
        == {"0": 6, "1": 4, "2": 3}
        and Counter(
            row["handoff_anchor_intervening_event_number_count"] for row in handoffs
        )
        == {"0": 5, "1": 5, "2": 2, "4": 1}
        and Counter(row["handoff_locus_line_distance"] for row in handoffs)
        == {"0": 10, "1": 3},
        "host, written-carrier, and governor-anchor distances remain separate",
    )
    phrase_by_key = {
        phrase["primary_governor_key"]: phrase for phrase in data["gdt584_phrases"]
    }
    handoff_distance_exact = True
    handoff_boundary_clean = True
    for row in handoffs:
        donor = phrase_by_key[row["handoff_source_primary_governor_key"]]
        host_distance = int(row["host_ordinal_in_statement"]) - int(
            donor["host_ordinal_in_statement"]
        )
        carrier_gap = event_number(row["source_event_id"]) - event_number(
            row["handoff_donor_carrier_source_event_id"]
        ) - 1
        anchor_gap = event_number(row["source_event_id"]) - event_number(
            row["handoff_donor_anchor_event_id"]
        ) - 1
        handoff_distance_exact &= (
            donor["statement_id"] == row["statement_id"]
            and donor["host_ordinal_in_statement"]
            == row["handoff_donor_host_ordinal_in_statement"]
            and int(row["handoff_host_ordinal_distance"]) == host_distance
            and int(row["handoff_intervening_event_number_count"]) == carrier_gap
            and int(row["handoff_anchor_intervening_event_number_count"]) == anchor_gap
            and int(row["handoff_locus_line_distance"])
            == locus_line_number(row["locus"])
            - locus_line_number(row["handoff_source_locus"])
        )
        between = [
            phrase
            for phrase in phrases_by_statement[row["statement_id"]]
            if int(donor["host_ordinal_in_statement"])
            <= int(phrase["host_ordinal_in_statement"])
            < int(row["host_ordinal_in_statement"])
        ]
        handoff_boundary_clean &= all(
            phrase["paragraph_boundary"] != "PARAGRAPH_AFTER" for phrase in between
        )
    check("HANDOFF_DISTANCE_RECOMPUTE", handoff_distance_exact, "13/13 source-derived distances")
    check("HANDOFF_NO_READER_BOUNDARY", handoff_boundary_clean, "13/13")
    check(
        "HANDOFF_PROVENANCE_PROFILE",
        Counter(row["handoff_donor_phrase_provenance"] for row in handoffs)
        == {
            "GDT587_ASSIGNMENT": 9,
            "GDT587_COMPLETE_READER__GDT584_CLAUSE_UNCHANGED": 4,
        },
        "nine assigned nouns plus four unchanged complete-reader clauses",
    )
    check(
        "HANDOFF_REMOTE_CARRIER_SOURCES",
        {
            row["source_event_id"]: row["handoff_donor_carrier_source_event_id"]
            for row in handoffs
            if row["handoff_donor_carrier_source_event_id"]
            != row["handoff_donor_anchor_event_id"]
        }
        == {"G407-E3067": "G407-E3066", "G407-E3304": "G407-E3301"},
        "two remote written roots retain source-event identity",
    )
    check(
        "HANDOFF_STATION_UNIT_FORMS",
        {
            row["source_event_id"]: (
                row["gdt592_object_lemma_de"], row["gdt592_object_form_de"]
            )
            for row in handoffs
            if row["source_event_id"] in LOCAL_HANDOFF_FORM_OVERRIDES
        }
        == LOCAL_HANDOFF_FORM_OVERRIDES,
        "E3067/E3550 preserve Stationseinheit wording",
    )
    check(
        "HANDOFF_EPISODE_RIVALS",
        sum(row["retained_episode_alternative_de"] != "NOT_APPLICABLE" for row in handoffs)
        == 9,
        "nine class-changing handoffs retain the older bath-episode rival",
    )
    reference_events = {row["source_event_id"] for row in handoffs} | {
        row["source_event_id"] for row in carries
    }
    check(
        "ORIGINAL_24_REFERENCE_TARGETS_PARTITION",
        len(reference_events) == 24
        and not ({row["source_event_id"] for row in handoffs} & {row["source_event_id"] for row in carries})
        and {
            row["source_event_id"]
            for row in carries
            if row["carry_reference_class"] == "NEUTRAL_DEFAULT_REUSE"
        }
        == {"G407-E3219", "G407-E3489"},
        "13 local handoffs + nine typed carries + two neutral reuses",
    )

    check(
        "GDT569_RELATION_PROFILE",
        Counter(row["gdt569_parallel_relation"] for row in actions)
        == EXPECTED_GDT569_RELATIONS,
        str(Counter(row["gdt569_parallel_relation"] for row in actions)),
    )
    check(
        "GDT569_ALIGNED_SLOT_SET",
        {
            row["action_slot_id"]
            for row in actions
            if row["gdt569_parallel_relation"] == "GDT569_CARRY_CLASS_ALIGNED"
        }
        == EXPECTED_GDT569_ALIGNED_SLOTS,
        "24 exact aligned slots; relation-order swaps cannot preserve only the count",
    )
    check(
        "GDT569_JOIN_PROFILE",
        Counter(row["gdt569_state_join_status"] for row in actions)
        == {"MATCHED": 117, "NO_STATE_ROW": 137}
        and Counter(
            row["gdt569_argument_carry"]
            for row in actions
            if row["gdt569_state_join_status"] == "MATCHED"
        )
        == {"YES": 109, "NO": 8},
        "117 matched: 109 carried arguments plus eight local explicit rows",
    )
    gdt569_by_event = {row["event_id"]: row for row in data["gdt569_states"]}
    copied_state_exact = True
    missing_state_exact = True
    for row in actions:
        state = gdt569_by_event.get(row["source_event_id"])
        if state is None:
            missing_state_exact &= all(
                row[field] == "NOT_APPLICABLE"
                for field in (
                    "gdt569_state_edition_ordinal",
                    "gdt569_argument_carry",
                    "gdt569_action_carry",
                    "gdt569_argument_source_type",
                    "gdt569_inherited_argument_root",
                    "gdt569_explicit_argument_phrase_de",
                    "gdt569_carried_argument_phrase_de",
                )
            )
        else:
            copied_state_exact &= (
                row["gdt569_state_edition_ordinal"] == state["state_edition_ordinal"]
                and row["gdt569_argument_carry"] == state["argument_carry"]
                and row["gdt569_action_carry"] == state["action_carry"] == "NO"
                and row["gdt569_argument_source_type"] == state["argument_source_type"]
                and row["gdt569_inherited_argument_root"] == state["inherited_argument_root"]
                and row["gdt569_explicit_argument_phrase_de"] == state["explicit_argument_phrase_de"]
                and row["gdt569_carried_argument_phrase_de"] == state["carried_argument_phrase_de"]
            )
    check("GDT569_MATCHED_FIELDS_EXACT", copied_state_exact, "117/117 copied from event-level source")
    check("GDT569_MISSING_FIELDS_EMPTY", missing_state_exact, "137/137 explicitly NOT_APPLICABLE")
    check(
        "GDT569_SPECIFIC_DEFAULT_CANDIDATES",
        Counter(
            row["gdt569_inherited_argument_root"]
            for row in actions
            if row["gdt569_parallel_relation"]
            == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
        )
        == {"Y": 49, "AIN": 8, "OR": 4},
        "61 concrete candidates over neutral Badegut defaults",
    )
    check(
        "GDT569_WRITTEN_PRECEDENCE_SET",
        {
            row["source_event_id"]
            for row in actions
            if row["gdt569_parallel_relation"]
            == "GDT569_CURRENT_WRITTEN_OBJECT_PRECEDENCE"
        }
        == {"G407-E1648", "G407-E1789"},
        "two current written objects outrank a different old carried root",
    )
    check(
        "GDT569_DIVERGENCE_SET",
        len(gdt569_divergences) == 2
        and {row["action_slot_id"] for row in gdt569_divergences}
        == {"RUNNING:G407-E1719@1", "RUNNING:G407-E2481@1"},
        "E1719 blocker-vs-AIN and E2481 episode-vs-OR retained",
    )
    e3243 = [row for row in actions if row["source_event_id"] == "G407-E3243"]
    check(
        "DOUBLE_SH_EVENT_SLOT_GRAIN",
        len(e3243) == 2
        and {row["action_slot_id"] for row in e3243}
        == {"RUNNING:G407-E3243@2", "RUNNING:G407-E3243@5"}
        and all(row["gdt569_state_join_status"] == "NO_STATE_ROW" for row in e3243),
        "one event remains two independent bath action slots",
    )

    check("EPISODE_ACTION_TOTAL", sum(int(row["bath_action_count"]) for row in episodes) == 254, "254")
    check(
        "EPISODE_ACTION_COUNT_PROFILE",
        Counter(row["bath_action_count"] for row in episodes)
        == {"1": 150, "2": 27, "3": 7, "4": 5, "9": 1},
        str(Counter(row["bath_action_count"] for row in episodes)),
    )
    check(
        "EPISODE_SINGLE_SCOPE",
        all(
            len(set(row["action_slot_sequence"].split("|")))
            == int(row["bath_action_count"])
            for row in episodes
        ),
        "190/190 ordered slot-unique action sequences; duplicate event IDs permitted",
    )

    expected_page_profile = {
        "f75r": (61, 37, 40, 31),
        "f77r": (47, 37, 39, 29),
        "f81r": (26, 20, 22, 19),
        "f81v": (33, 26, 26, 20),
        "f82r": (40, 26, 28, 24),
        "f83r": (47, 31, 35, 31),
    }
    actual_page_profile = {
        row["physical_page"]: (
            int(row["bath_action_count"]),
            int(row["bath_statement_count"]),
            int(row["bath_episode_count"]),
            int(row["clause_patch_count"]),
        )
        for row in pages
    }
    check("PAGE_PROFILE", actual_page_profile == expected_page_profile, str(actual_page_profile))
    check("PAGE_TOTALS", sum(int(row["bath_action_count"]) for row in pages) == 254 and sum(int(row["clause_patch_count"]) for row in pages) == 154, "254 / 154")

    check("STATEMENT_COUNT", len(statements) == 793, str(len(statements)))
    check("PATCHED_STATEMENT_COUNT", len(patched_statements) == 132, str(len(patched_statements)))
    check("UNCHANGED_STATEMENT_COUNT", sum(row["gdt592_reader_changed"] == "NO" for row in statements) == 661, "661")
    upstream_fields = list(data["gdt590_statements"][0])
    check(
        "GDT590_STATEMENT_PROJECTION",
        [{field: row[field] for field in upstream_fields} for row in statements]
        == data["gdt590_statements"],
        "all upstream columns byte-retained",
    )
    check(
        "UNCHANGED_READER_BYTES",
        all(
            row["gdt592_primary_reader_de"] == row["gdt590_primary_reader_de"]
            for row in statements
            if row["gdt592_reader_changed"] == "NO"
        ),
        "661/661",
    )
    check(
        "PATCH_COUNT_PROFILE",
        Counter(row["object_patch_count"] for row in patched_statements)
        == {"1": 113, "2": 17, "3": 1, "4": 1},
        str(Counter(row["object_patch_count"] for row in patched_statements)),
    )
    check(
        "COUNT_OVERLAY_RETENTION_POPULATION",
        sum(
            row["gdt592_reader_changed"] == "YES" and row["gdt589_count_overlay"] == "YES"
            for row in statements
        ) == 11,
        "eleven patched statements retain written-count overlays",
    )
    patched_ids = {row["statement_id"] for row in patched_statements}
    internal_break_statements = 0
    for statement_id in patched_ids:
        phrases = phrases_by_statement[statement_id]
        internal_break_statements += any(
            phrase["paragraph_boundary"] == "PARAGRAPH_AFTER"
            for phrase in phrases[:-1]
        )
    check("INTERNAL_READER_BREAK_RETENTION_POPULATION", internal_break_statements == 34, "34 patched statements")
    check(
        "NO_BATH_NAME_OVERRIDE",
        all(
            row["name_override_count"] == "0"
            for row in statements
            if int(row["gdt592_bath_action_count"]) > 0
        ),
        "177/177 bath statements",
    )

    e2652 = next(row for row in actions if row["source_event_id"] == "G407-E2652")
    check(
        "E2652_FROZEN_BODY",
        e2652["gdt592_object_class"] == "BODY"
        and e2652["object_selection_route"] == "WRITTEN_Y_GDT590"
        and e2652["clause_patch_required"] == "NO",
        "GDT590/GDT591 reading unchanged",
    )
    check("E2652_STATION_VISIBLE", e2652["retained_alternative_de"] == "Stationsansatz", "station rival retained")

    check("READER_PAGE_COUNT", reader.count("## f") == 6, "six page sections")
    check("READER_STATEMENT_COUNT", reader.count("### G407-S") == 177, "177 bath statements")
    check("READER_E2652_ALTERNATIVE", "E2652 bleibt offen sichtbar" in reader and "Stationsalternative" in reader, "visible")
    check(
        "INLINE_SIZE_CAP",
        all(path.stat().st_size <= 5_000_000 for name, path in OUTPUTS.items() if name != "validation"),
        "every generated artifact at or below five MB",
    )

    tracked_outputs = [path for name, path in OUTPUTS.items() if name != "validation"]
    before = {str(path): sha256(path) for path in tracked_outputs}
    rebuild_run = subprocess.run(
        ["python3", str(ROOT / "experiments/yolo/gdt592_bath_object_completion/src/run.py")],
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
        "experiment_id": "GDT592",
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
