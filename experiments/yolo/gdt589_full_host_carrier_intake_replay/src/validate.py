#!/usr/bin/env python3
"""Validate GDT589 complete-host replay, gate routing, and count overlays."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from replay_lib import (
    DEFAULT_PACKET,
    INPUTS,
    OUTPUTS,
    ROOT,
    STATUS,
    build_replay,
    load_inputs,
    read_tsv,
    sha256,
    split_pipe,
    unique_action_map,
)


def main() -> int:
    data = load_inputs()
    rows = {
        name: read_tsv(path)
        for name, path in OUTPUTS.items()
        if path.suffix == ".tsv"
    }
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))
    deck = OUTPUTS["deck"].read_text(encoding="utf-8")
    book = OUTPUTS["book"].read_text(encoding="utf-8")
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
    slots = rows["slots"]
    manual = rows["manual"]
    source = rows["source_bound"]
    special = rows["special_packets"]
    repeated = rows["repeated"]
    body = rows["body_guard"]
    bath = rows["bath_forks"]
    pages = rows["pages"]
    statements = rows["statements"]
    local_cards = rows["local_cards"]

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check(
        "INPUT_HASHES",
        result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()},
        "eight fixed inputs",
    )
    check("NO_NEW_PAGE", {row["physical_page"] for row in hosts} <= {row["physical_page"] for row in data["assignments_587"]}, "fixed thirty-page population")
    check("SEALED_F84_ABSENT", not any(row["physical_page"].lower().startswith("f84") for row in [*hosts, *statements, *local_cards]), "no f84/f84r rows")

    expected_hosts, expected_slots = build_replay(data)
    expected_hosts_text = [{key: str(value) for key, value in row.items()} for row in expected_hosts]
    expected_slots_text = [{key: str(value) for key, value in row.items()} for row in expected_slots]
    check("HOST_REBUILD_EXACT", hosts == expected_hosts_text, "953 rows")
    check("SLOT_REBUILD_EXACT", slots == expected_slots_text, "1243 rows")
    check("HOST_COUNT", len(hosts) == 953, str(len(hosts)))
    check("SLOT_COUNT", len(slots) == 1243, str(len(slots)))
    check("UNIQUE_HOST_KEYS", len({row["primary_governor_key"] for row in hosts}) == 953, "953 unique governors")
    check("UNIQUE_SLOT_IDS", len({row["carrier_slot_id"] for row in slots}) == 1243, "1243 unique carrier slots")
    check(
        "SOURCE_SLOT_ORDER",
        [row["carrier_slot_id"] for row in slots]
        == [row["carrier_slot_id"] for row in data["assignments_587"]],
        "fixed GDT587 assignment order",
    )

    action_map = unique_action_map(data["actions_584"])
    check(
        "COMPLETE_HOST_TOKEN_SET",
        all(
            set(split_pipe(row["complete_host_values_written"]))
            == set(split_pipe(action_map[row["primary_governor_key"]]["governor_group_tokens"]))
            for row in hosts
        ),
        "953/953 GDT584 governor groups",
    )
    slot_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slot_by_host[row["primary_governor_key"]].append(row)
    check(
        "ROOT_SEQUENCE_RECONSTRUCTION",
        all(
            host["written_root_sequence"]
            == "+".join(row["carrier_root"] for row in slot_by_host[host["primary_governor_key"]])
            for host in hosts
        ),
        "ordered assignment slots",
    )
    check(
        "SLOT_COUNT_RECONSTRUCTION",
        all(int(host["carrier_slot_count"]) == len(slot_by_host[host["primary_governor_key"]]) for host in hosts),
        "953 host counts",
    )
    check("HISTORICAL_RULE_REPLAY", all(row["historical_rule_replay_exact"] == "YES" for row in hosts), "1243/1243 via historical rule")
    check("HISTORICAL_SLOT_REPLAY", all(row["historical_rule_exact"] == "YES" for row in slots), "1243 slot forms")

    gate_counts = Counter(row["gate_class"] for row in hosts)
    gate_slots = Counter()
    for row in hosts:
        gate_slots[row["gate_class"]] += int(row["carrier_slot_count"])
    check("GATE_HOST_PROFILE", gate_counts == {"AUTO_CONTEXT": 910, "MANUAL_GDT584_OVERRIDE": 41, "SOURCE_ID_BOUND": 2}, str(gate_counts))
    check("GATE_SLOT_PROFILE", gate_slots == {"AUTO_CONTEXT": 1186, "MANUAL_GDT584_OVERRIDE": 53, "SOURCE_ID_BOUND": 4}, str(gate_slots))

    auto_hosts = [row for row in hosts if row["gate_class"] == "AUTO_CONTEXT"]
    auto_slots = [row for row in slots if row["gate_class"] == "AUTO_CONTEXT"]
    check("AUTO_HOST_EXACT", len(auto_hosts) == 910 and all(row["replay_outcome"] == "AUTO_EXACT_REPLAY" for row in auto_hosts), "910/910")
    check("AUTO_RULE_EXACT", all(row["portable_runtime_rule_id"] == row["gdt583_rule_id"] for row in auto_hosts), "910/910 rules")
    check("AUTO_PARENT_EXACT", all(row["portable_runtime_parent_rule_match"] == "YES" for row in auto_hosts), "910/910 parent gates")
    check("AUTO_PACKET_EXACT", all(row["portable_packet_match"] == "YES" for row in auto_hosts), "910/910 packets")
    check("AUTO_SLOT_EXACT", len(auto_slots) == 1186 and all(row["portable_exact"] == "YES" for row in auto_slots), "1186/1186 full forms and context")
    check("AUTO_SLOT_VISIBLE_EXACT", all(row["portable_visible_exact"] == "YES" for row in auto_slots), "1186/1186 visible noun forms")
    check("AUTO_LOOKUP_PROFILE", Counter(row["portable_lookup_route"] for row in auto_slots) == {"OBSERVED_ACTION_ROOT_CELL": 1068, "KNOWN_PACKET_RULE": 118}, str(Counter(row["portable_lookup_route"] for row in auto_slots)))

    check("MANUAL_COUNT", len(manual) == 41 and sum(int(row["carrier_slot_count"]) for row in manual) == 53, "41 hosts / 53 slots")
    check("MANUAL_EXPLICIT_EXACT", all(row["historical_explicit_replay"] == "YES" for row in manual), "41/41")
    check("MANUAL_ACTION_DRIFT", sum(row["action_wording_change"] == "YES" for row in manual) == 39, "39/41")
    direct_noun_ids = {row["source_event_or_card_id"] for row in manual if int(row["direct_parent_changed_slot_count"]) > 0}
    runtime_noun_ids = {row["source_event_or_card_id"] for row in manual if int(row["runtime_changed_slot_count"]) > 0}
    packet_ids = {row["source_event_or_card_id"] for row in manual if row["packet_change"] == "YES"}
    check("MANUAL_PARENT_NOUN_IDS", direct_noun_ids == {"G407-E0582", "G407-E4089"}, str(sorted(direct_noun_ids)))
    check("MANUAL_RUNTIME_NOUN_IDS", runtime_noun_ids == {"G407-E0582", "G407-E4089", "G407-E4166", "G407-E4410"}, str(sorted(runtime_noun_ids)))
    check("MANUAL_PACKET_IDS", packet_ids == {"G407-E3903", "G407-E4069", "G407-E4226", "G407-E4407"}, str(sorted(packet_ids)))
    check("MANUAL_VISIBLE_AFFECTED", sum(row["carrier_effect"] == "VISIBLE_CARRIER_CHANGE" for row in manual) == 8, "four noun plus four packet hosts")
    check("MANUAL_CONTEXT_DRIFT", sum(int(row["runtime_context_family_changed_slot_count"]) for row in manual) == 36, "36 conservative context-family changes")
    manual_slots = [row for row in slots if row["gate_class"] == "MANUAL_GDT584_OVERRIDE"]
    check("MANUAL_ROUTE_PROFILE", Counter(row["portable_lookup_route"] for row in manual_slots) == {"REGISTER_INVARIANT": 32, "OBSERVED_ACTION_ROOT_CELL": 17, "KEEP_BROAD": 2, "KNOWN_PACKET_RULE": 2}, str(Counter(row["portable_lookup_route"] for row in manual_slots)))
    broad = [row for row in manual_slots if "KEEP_BROAD" in row["portable_lookup_route"]]
    check("BROAD_ALTERNATIVES_VISIBLE", len(broad) == 2 and all("/" in row["observed_register_root_alternatives_de"] for row in broad), "two broad defaults show alternatives")

    check("SOURCE_COUNT", len(source) == 2 and sum(int(row["carrier_slot_count"]) for row in source) == 4, "two hosts / four slots")
    check("SOURCE_IDS", {row["source_event_or_card_id"] for row in source} == {"G407-E0298", "G407-E0494"}, "two old bridge IDs")
    check("SOURCE_GATE_REJECTS_OLD_ID", all(row["source_id_gate_status"] == "EXPECTED_SOURCE_ID_REJECTION" for row in source), "old ID route not portable")
    check("SOURCE_VISIBLE_EXACT", all(row["visible_fallthrough_exact"] == "YES" and row["reader_route"] == "OLD_ID_RULE_DROPPED__VISIBLE_FALLTHROUGH_EXACT" for row in source), "2/2 SH_REST_HOLD fallthroughs")

    check("SPECIAL_PACKET_COUNT", len(special) == 74 and sum(int(row["carrier_slot_count"]) for row in special) == 121, "74 hosts / 121 slots")
    check("SPECIAL_GATE_PROFILE", Counter(row["gate_class"] for row in special) == {"AUTO_CONTEXT": 71, "MANUAL_GDT584_OVERRIDE": 3}, str(Counter(row["gate_class"] for row in special)))
    gap_counts = Counter(row["display_gap_class"] for row in special)
    check("PACKET_DISPLAY_GAPS", gap_counts == {"DIRECT_WRITTEN_SLOT_COMPOSITION": 64, "CLEAN_BATH_BODY_STATION_FORK": 4, "ACTION_SUPPLIES_UNWRITTEN_EXTRACT_HEAD": 3, "SLOT_Y_WORKING_LEMMA_RENAMED_IN_PACKET": 2, "PACKET_TEMPLATE_OMITS_WRITTEN_SECTOR_SHARE": 1}, str(gap_counts))
    check("PACKET_ORDER_PRIMARY", all(row["ordered_written_slot_lemmas_de"].count(" | ") + 1 == int(row["carrier_slot_count"]) for row in special), "every written special slot ordered")
    check("PACKET_HISTORICAL_EXACT", all(row["historical_explicit_replay"] == "YES" for row in special), "74/74 explicit old rule")

    check("REPEAT_COUNT", len(repeated) == 117 and sum(int(row["carrier_slot_count"]) for row in repeated) == 295, "117 hosts / 295 slots")
    check("REPEAT_EXTRA_COPIES", sum(int(row["written_extra_copy_count"]) for row in repeated) == 132, "132 written positions beyond presence")
    check("REPEAT_CLASS_PROFILE", Counter(row["repeat_class"] for row in repeated) == {"DEFAULT_COMPOSITION": 104, "SPECIAL_PACKET": 13}, str(Counter(row["repeat_class"] for row in repeated)))
    check("REPEAT_GATE_PROFILE", Counter(row["gate_class"] for row in repeated) == {"AUTO_CONTEXT": 115, "MANUAL_GDT584_OVERRIDE": 1, "SOURCE_ID_BOUND": 1}, str(Counter(row["gate_class"] for row in repeated)))
    check("REPEAT_LAYER_PROFILE", Counter(row["layer"] for row in repeated) == {"RUNNING_ATOM": 110, "LOCAL_COMPONENT": 7}, str(Counter(row["layer"] for row in repeated)))
    check("OLD_SPECIAL_REPAIRS", sum(row["gdt588_special_fluent_repair"] == "YES" for row in repeated) == 13, "thirteen GDT588 special packets")
    check("REPEAT_ORDERED_TRACE", all(row["ordered_written_slot_lemmas_de"].count(" | ") + 1 == int(row["carrier_slot_count"]) for row in repeated), "117 ordered traces")
    check("REPEAT_NOT_OBJECT_COUNTS", all(row["count_interpretation"] == "WRITTEN_CARRIER_POSITIONS__NOT_REAL_OBJECT_MULTIPLICITY" for row in repeated), "written positions only")

    check("BODY_HOST_COUNT", len(body) == 361, str(len(body)))
    bio_y_slots = [row for row in auto_slots if row["register"] == "BIOLOGICAL" and row["carrier_root"] == "Y"]
    check("BODY_SLOT_COUNT", len(bio_y_slots) == 406, str(len(bio_y_slots)))
    check("BODY_LEMMA_PROFILE", Counter(row["expected_lemma_de"] for row in bio_y_slots) == {"Stationsansatz": 338, "Körper": 61, "Strom": 7}, str(Counter(row["expected_lemma_de"] for row in bio_y_slots)))
    check("BODY_REPLAY_EXACT", all(row["portable_exact"] == "YES" for row in body), "361/361 hosts")
    bath_ids = {row["source_event_or_card_id"] for row in bath}
    check("CLEAN_BATH_FORK_IDS", bath_ids == {"G407-E2404", "G407-E2637", "G407-E2652", "G407-E3182"}, str(sorted(bath_ids)))
    check("CLEAN_BATH_NO_BLOCKERS", len(bath) == 4 and all(row["body_blockers_present"] == "NONE" for row in bath), "four blocker-free Y+AIIN hosts")
    check("CLEAN_BATH_FORK_VISIBLE", all(row["exploratory_bath_default_de"] == "Körper" and row["retained_bath_alternative_de"] == "Stationsansatz" for row in bath), "Körper first, station retained")

    check("COMPLETE_READER_COUNTS", len(statements) == 793 and len(local_cards) == 744, "793 + 744")
    check("OVERLAY_UNIT_COUNTS", sum(row["gdt589_count_overlay"] == "YES" for row in statements) == 83 and sum(row["gdt589_count_overlay"] == "YES" for row in local_cards) == 7, "90 reader units")
    overlay_keys = set()
    for row in [*statements, *local_cards]:
        overlay_keys.update(split_pipe(row["gdt589_repeated_host_keys"]))
    check("OVERLAY_HOST_COVERAGE", overlay_keys == {row["primary_governor_key"] for row in repeated}, "all 117 repeat hosts")
    check("FLUENT_BASE_RESTORED", all(row["gdt589_base_reader_de"] == row["gdt588_base_reader_de"] for row in [*statements, *local_cards]), "GDT587 fluent relation channel")
    check("NO_OVERLAY_BYTE_RETAINED", all(row["gdt589_primary_reader_de"] == row["gdt589_base_reader_de"] for row in [*statements, *local_cards] if row["gdt589_count_overlay"] == "NO"), "1447 unaffected reader units")
    check("OVERLAY_LABELS_COUNTS", all("×N zählt Schriftträger, nicht Realobjekte" in row["gdt589_primary_reader_de"] for row in [*statements, *local_cards] if row["gdt589_count_overlay"] == "YES"), "90 explicit interpretation labels")
    check("OVERLAY_ORDER_ARROW", all(" → " in row["gdt589_written_carrier_overlay_de"] for row in [*statements, *local_cards] if row["gdt589_count_overlay"] == "YES"), "ordered trace before multiset")
    check("PAGE_COUNT", len(pages) == 30 and sum(int(row["host_count"]) for row in pages) == 953, "30 pages / 953 hosts")
    check("PAGE_SLOT_TOTAL", sum(int(row["carrier_slot_count"]) for row in pages) == 1243, "1243 slots")
    check("PAGE_NO_AUTO_DIVERGENCE", all(row["auto_divergence_count"] == "0" for row in pages), "all thirty pages")

    check("DECK_COUNTS", all(token in deck for token in ("953", "1243", "117 Repeat-Hosts", "Vier saubere Bad")), "compact replay deck")
    check("DECK_THREE_LEVELS", "geordneten Slotnomen" in deck and "kompositionell eingeführter Packetkopf" in deck and "fertige Satz" in deck, "three display levels")
    check("BOOK_COMPLETE", book.count("### Laufende Aussagen") == 30 and book.count("### Lokale Karten") == 30, "thirty-page human reader")
    check("INLINE_SIZE_CAP", all(path.stat().st_size <= 5_000_000 for name, path in OUTPUTS.items() if name != "validation"), "every committed artifact at or below five MB")

    tracked_outputs = [path for name, path in OUTPUTS.items() if name != "validation"]
    before = {str(path): sha256(path) for path in tracked_outputs}
    rebuild = subprocess.run(
        ["python3", str(ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/src/run.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    after = {str(path): sha256(path) for path in tracked_outputs}
    check("REBUILD_EXIT", rebuild.returncode == 0, rebuild.stderr[-500:] or "exit 0")
    check("BYTE_IDENTICAL_REBUILD", before == after, f"{len(tracked_outputs)} artifacts")

    cli = subprocess.run(
        ["python3", str(ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/src/read_known_host.py"), "ACTION:G407-E4166@3:CHD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    cli_payload = json.loads(cli.stdout) if cli.returncode == 0 else {}
    check("KNOWN_HOST_CLI", cli.returncode == 0 and cli_payload.get("host", {}).get("gate_class") == "MANUAL_GDT584_OVERRIDE" and len(cli_payload.get("ordered_slots", [])) == 5, "five-slot manual stress host")

    status = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    payload = {
        "experiment_id": "GDT589",
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
