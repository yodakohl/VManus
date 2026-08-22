#!/usr/bin/env python3
"""Independent structural validator for the V74 R1 station-atlas edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"

EVENT_SOURCE = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_SOURCE = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
OWNER_SOURCE = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENT_SOURCE = V72 / "V72_SELECTED_116_STATEMENTS.tsv"
EVENT_OUT = BASE / "V74_R1_281_EVENT_INTERLINEAR.tsv"
FIELD_OUT = BASE / "V74_R1_115_FIELD_EDITION.tsv"
STATEMENT_OUT = BASE / "V74_R1_97_STATEMENT_EDITION.tsv"
CONTINUOUS_OUT = BASE / "V74_R1_SIX_RECORD_CONTINUOUS_EDITION.md"
VALIDATION_OUT = BASE / "V74_R1_VALIDATION.json"

PAGES = {"f81v", "f82r", "f83r"}
RECORDS = {"B1", "B2", "B3", "B4", "B5", "B6"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate() -> dict[str, object]:
    source_events = [r for r in read(EVENT_SOURCE) if r["page"] in PAGES]
    source_fields = [r for r in read(FIELD_SOURCE) if r["page"] in PAGES]
    source_statements = [r for r in read(STATEMENT_SOURCE) if r["page"] in PAGES]
    owners = [r for r in read(OWNER_SOURCE) if r["unit_kind"] == "PROSE_FIELD" and r["page"] in PAGES]
    events, fields, statements = read(EVENT_OUT), read(FIELD_OUT), read(STATEMENT_OUT)
    continuous = CONTINUOUS_OUT.read_text(encoding="utf-8")
    source_event_by_serial = {r["event_serial"]: r for r in source_events}
    source_field_by_id = {r["field_id"]: r for r in source_fields}
    source_statement_by_id = {r["statement_id"]: r for r in source_statements}
    owner_by_field = {r["unit_id"]: r for r in owners}
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)
        events_by_statement[row["statement_id"]].append(row)

    # Independently derive expected field owner transitions.
    expected_transition, prior_by_record = {}, {}
    for source_field in source_fields:
        fid, rec = source_field["field_id"], source_field["record_unit_id"]
        owner_row = owner_by_field[fid]
        owner, prior = owner_row["selected_visible_owner"], prior_by_record.get(rec)
        if owner_row["owner_status"] == "UNRESOLVED":
            mode = "MASTER_EXEMPLAR_OWNER_LOOKUP" if prior == owner else "RESET_AT_V71_GAP_AND_MASTER_EXEMPLAR_OWNER_LOOKUP"
        elif prior is None: mode = "RESET_AT_RECORD_START"
        elif prior == owner: mode = "CARRY_WITHIN_LOCAL_STATION"
        else: mode = "RESET_AT_V71_SCENE_GAP"
        expected_transition[fid] = mode
        prior_by_record[rec] = owner

    internal_reset_expected = {}
    for source_statement in source_statements:
        owner_sequence = []
        for fid in source_statement["constituent_fields"].split("|"):
            owner = owner_by_field[fid]["selected_visible_owner"]
            if not owner_sequence or owner != owner_sequence[-1]: owner_sequence.append(owner)
        internal_reset_expected[source_statement["statement_id"]] = len(owner_sequence) > 1

    required_event_columns = [
        "literal_exact_card_layer", "v71_local_owner", "owner_status", "owner_transition",
        "concrete_german_default", "source_layer", "working_confidence",
        "medical_application_reading", "bathhouse_operation_rival",
        "iconographic_formal_rival", "strongest_rival", "contradiction",
    ]
    checks = {
        "exactly_281_event_rows": len(events) == 281,
        "event_serials_exact_101_to_381": [int(r["event_serial"]) for r in events] == list(range(101, 382)),
        "exactly_115_field_rows": len(fields) == 115,
        "field_ids_exact_F021_to_F135": [r["field_id"] for r in fields] == [f"F{i:03d}" for i in range(21, 136)],
        "exactly_97_statement_rows": len(statements) == 97,
        "statement_ids_unique_and_match_source": {r["statement_id"] for r in statements} == set(source_statement_by_id),
        "exactly_six_records": {r["record_unit_id"] for r in events} == RECORDS,
        "pages_exactly_fixed_bio_three": {r["page"] for r in events} == PAGES,
        "event_identity_and_membership_match_source": all(
            r["exact_card_id"] == source_event_by_serial[r["event_serial"]]["joint_tuple_id"]
            and r["field_id"] == source_event_by_serial[r["event_serial"]]["field_id"]
            and r["statement_id"] == source_event_by_serial[r["event_serial"]]["statement_id"]
            for r in events
        ),
        "every_literal_layer_contains_exact_identity": all(f"EXACT_CARD_ID={r['exact_card_id']}" in r["literal_exact_card_layer"] for r in events),
        "all_event_required_columns_nonempty": all(all(r[c] for c in required_event_columns) for r in events),
        "all_defaults_are_complete_sentences": all(len(r["concrete_german_default"]) >= 28 and r["concrete_german_default"].endswith(".") for r in events),
        "all_event_owners_match_v71": all(
            r["v71_local_owner"] == owner_by_field[r["field_id"]]["selected_visible_owner"]
            and r["owner_status"] == owner_by_field[r["field_id"]]["owner_status"] for r in events
        ),
        "field_owner_transitions_exact": all(r["owner_transition"] == expected_transition[r["field_id"]] for r in fields),
        "unresolved_fields_retained": {r["field_id"] for r in fields if r["owner_status"] == "UNRESOLVED"} == ({"F057", "F058"} | {f"F{i:03d}" for i in range(87, 99)}),
        "recognized_parser_events_remain_90": sum(r["parse_status"] != "UNPARSED_EXEMPLAR" for r in events) == 90,
        "exemplar_only_parser_events_remain_191": sum(r["parse_status"] == "UNPARSED_EXEMPLAR" for r in events) == 191,
        "field_event_counts_and_serials_match": all(
            len(events_by_field[r["field_id"]]) == int(r["event_count"])
            and "|".join(e["event_serial"] for e in events_by_field[r["field_id"]]) == source_field_by_id[r["field_id"]]["event_serials"]
            for r in fields
        ),
        "statement_event_counts_match": all(len(events_by_statement[r["statement_id"]]) == int(r["event_count"]) for r in statements),
        "exactly_four_internal_statement_owner_resets": sum(r["internal_owner_reset"] == "YES" for r in statements) == 4,
        "statement_owner_resets_match_v71": all((r["internal_owner_reset"] == "YES") == internal_reset_expected[r["statement_id"]] for r in statements),
        "reset_statements_explicitly_deny_connection": all(
            r["internal_owner_reset"] == "NO" or "OHNE BILDVERBINDUNG" in r["continuous_local_statement"] for r in statements
        ),
        "global_flow_never_claimed": all(r["global_flow_claim"] == "NONE" for r in events + fields + statements),
        "local_direction_is_explicitly_bounded": all(
            r["local_direction_status"] == "NO_DIRECTION_ASSERTED"
            or (r["local_direction_status"] == "LOCAL_EXEMPLAR_DIRECTION_ONLY" and "globaler Seitenfluss fehl" in r["contradiction"])
            for r in events
        ),
        "all_three_readings_present_per_event": all(
            r["medical_application_reading"] and r["bathhouse_operation_rival"] and r["iconographic_formal_rival"] for r in events
        ),
        "every_field_verbatim_in_continuous_edition": all(r["readable_field_text"] in continuous for r in fields),
        "all_16_station_headings_present": len({r["v71_local_owner"] for r in fields}) == 16 and all(f"### Station `{o}`" in continuous for o in {r["v71_local_owner"] for r in fields}),
        "six_record_headings_present": all(f"## {r} —" in continuous for r in sorted(RECORDS)),
        "no_new_card_labels": all(
            ("KNOWN_CARD=NONE" in r["literal_exact_card_layer"] if source_event_by_serial[r["event_serial"]]["selected_exact_mnemonic"] in {"", "NONE", "UNKNOWN"}
             else f"KNOWN_CARD={source_event_by_serial[r['event_serial']]['selected_exact_mnemonic']}" in r["literal_exact_card_layer"])
            for r in events
        ),
    }
    result = {
        "experiment": "V74_R1_COMPLETE_BIOLOGICAL_STATION_ATLAS_THIRD_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {
            "events": len(events), "fields": len(fields), "statements": len(statements),
            "records": len({r["record_unit_id"] for r in events}),
            "station_owners": len({r["v71_local_owner"] for r in fields}),
            "recognized_parser_events": sum(r["parse_status"] != "UNPARSED_EXEMPLAR" for r in events),
            "exemplar_only_parser_events": sum(r["parse_status"] == "UNPARSED_EXEMPLAR" for r in events),
            "source_layers": dict(sorted(Counter(r["source_layer"] for r in events).items())),
            "owner_statuses_events": dict(sorted(Counter(r["owner_status"] for r in events).items())),
            "local_direction_events": sum(r["local_direction_status"] == "LOCAL_EXEMPLAR_DIRECTION_ONLY" for r in events),
            "internal_statement_owner_resets": sum(r["internal_owner_reset"] == "YES" for r in statements),
        },
        "checks": checks,
        "constraints": {
            "global_flow_direction_invented": False,
            "new_card_stem_sound_language_meaning": False,
            "new_pages_read": False,
            "sealed_pages_opened": False,
            "active_v74_sibling_outputs_read": False,
            "commit_or_push": False,
        },
    }
    VALIDATION_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
