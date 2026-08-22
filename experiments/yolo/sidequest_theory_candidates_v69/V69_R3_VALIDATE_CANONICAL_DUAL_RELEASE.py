#!/usr/bin/env python3
"""Validate the final V69 R3 canonical dual release."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILDER = HERE / "V69_R3_BUILD_CANONICAL_DUAL_RELEASE.py"

FILES = {
    "cards": (HERE / "V69_R3_173_CARD_DICTIONARY.tsv", 173),
    "events": (HERE / "V69_R3_381_PROSE_EVENT_LEDGER.tsv", 381),
    "fields": (HERE / "V69_R3_135_FIELD_LEDGER.tsv", 135),
    "statements": (HERE / "V69_R3_116_STATEMENT_LEDGER.tsv", 116),
    "astro": (HERE / "V69_R3_395_ASTRO_GROUP_LEDGER.tsv", 395),
    "unified": (HERE / "V69_R3_776_UNIFIED_DUAL_LEDGER.tsv", 776),
    "units": (HERE / "V69_R3_14_UNIT_DUAL_EDITION.tsv", 14),
    "compiler": (HERE / "V69_R3_22_COMPILER_TRANSITIONS.tsv", 22),
    "invariants": (HERE / "V69_R3_INVARIANT_AUDIT.tsv", 37),
    "sources": (HERE / "V69_R3_SOURCE_MANIFEST.tsv", 27),
    "release": (HERE / "V69_R3_RELEASE_MANIFEST.tsv", 10),
}

UNIT_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
UNSET_STATE = "OWNER=UNSET;ACTIVE_ITEM/PREPARATION=UNSET;TARGET/STATION=UNSET;PREVIOUS_ITEM=UNSET"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    data = {name: read_tsv(path) for name, (path, _) in FILES.items()}
    for name, (_, count) in FILES.items():
        require(len(data[name]) == count, f"{name}: expected {count}, got {len(data[name])}")

    cards = data["cards"]
    events = data["events"]
    fields = data["fields"]
    statements = data["statements"]
    astro = data["astro"]
    unified = data["unified"]
    units = data["units"]

    require(len({row["exact_joint_card_id"] for row in cards}) == 173, "card IDs not unique")
    require(sum(int(row["occurrences"]) for row in cards) == 381, "card occurrence sum")
    require(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR" for row in cards) == 11, "mnemonic card count")
    require(sum(row["strict_formal_prompt"] != "NONE" for row in cards) == 4, "formal card count")
    control_ids = {row["exact_joint_card_id"] for row in cards if row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR" or row["strict_formal_prompt"] != "NONE"}
    require(len(control_ids) == 14, "control union card count")
    require(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR" for row in cards) == 162, "unknown card tails")
    require(all(row["iatromedical_card_value"] == "NONE;LOCAL_EVENT_EXEMPLAR_ONLY" and row["practical_card_value"] == "NONE;LOCAL_EVENT_EXEMPLAR_ONLY" for row in cards), "domain value leaked into card dictionary")
    require(all(row["component_inheritance"] == "FORBIDDEN;EXACT_JOINT_CARD_ATOMIC" and row["page_host_semantics"] == "FORBIDDEN" for row in cards), "component/PAGE_HOST meaning")
    require(all(row["confirmed_lexeme"] == "NO" for row in cards), "confirmed lexeme introduced")

    require([int(row["event_serial"]) for row in events] == list(range(1, 382)), "event serials")
    require({row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, "prose page scope")
    card_by_id = {row["exact_joint_card_id"]: row for row in cards}
    for row in events:
        card = card_by_id[row["exact_joint_card_id"]]
        # A strict formal construction is not a semantic whole-card default.
        # V60 deliberately licenses VORGABEPARAMETER? only for the visible
        # surface DAIIN although DAIIN shares one opaque joint-tuple ID with
        # AIIN/CHAIIN/SAIIN/TAIIN.  Preserve that selected surface/form layer
        # instead of smuggling it into every occurrence of the exact card.
        declared_prompt = card["strict_formal_prompt"]
        if declared_prompt.startswith("SURFACE_DAIIN_ONLY:"):
            scoped_prompt = declared_prompt.split(":", 1)[1]
            expected_prompt = scoped_prompt if row["surface_display_only"] == "daiin" else "NONE"
            require(row["strict_formal_prompt"] == expected_prompt, "DAIIN-only formal scope drift")
        else:
            require(row["strict_formal_prompt"] == declared_prompt, "strict formal construction drift")
        require(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == card["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"], "mnemonic not global by exact card")
        require(row["domain_selection"] == "NONE;DUAL_UNRESOLVED", "event domain winner")
        require(row["complete_source_recovery_without_exemplar"] == "NO", "event standalone source recovery")
        require(row["formal_roundtrip"] == "PASS", "event formal roundtrip")
        require(row["iatromedical_local_exemplar"] and row["practical_local_exemplar"], "event dual text incomplete")
        require("NO_PAGE_HOST_OR_COMPONENT_MEANING" in row["semantic_contract"], "event semantic prohibition absent")
    require(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR" for row in events) == 85, "mnemonic event count")
    require(sum(row["strict_formal_prompt"] != "NONE" for row in events) == 45, "formal event count")
    require(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] != "UNKNOWN_EXEMPLAR" or row["strict_formal_prompt"] != "NONE" for row in events) == 119, "control event union")
    require(sum(row["working_exact_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR" for row in events) == 296, "unknown event tails")
    require(sum(row["compiler_channel"] == "EXEMPLAR_WHOLE_CARD" for row in events) == 262, "exemplar-only events")

    event_by_serial = {row["event_serial"]: row for row in events}
    require(len({row["field_id"] for row in fields}) == 135, "field IDs")
    decoded_field_events = []
    for field in fields:
        member_ids = field["event_serials"].split("|")
        members = [event_by_serial[value] for value in member_ids]
        decoded_field_events.extend(member_ids)
        require(int(field["event_count"]) == len(members), "field event count")
        require(field["exact_card_sequence"].split("|") == [row["exact_joint_card_id"] for row in members], "field exact sequence")
        require(field["complete_source_recovery_without_exemplar"] == "NO", "field standalone source recovery")
        require(field["domain_selection"] == "NONE;DUAL_UNRESOLVED", "field domain winner")
        require(field["iatromedical_field_exemplar"] and field["practical_field_exemplar"], "field dual text")
    require(Counter(decoded_field_events) == Counter(str(i) for i in range(1, 382)), "field event partition")
    require(Counter(row["terminal_envelope"] for row in fields) == Counter({"TERMINAL_CLOSE": 90, "OPEN_CUT": 45}), "field terminal envelope")
    require(Counter(row["parse_status"] for row in fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "field parse profile")

    require(len({row["statement_id"] for row in statements}) == 116, "statement IDs")
    decoded_statement_events = []
    first_by_unit = {}
    for statement in statements:
        first_by_unit.setdefault(statement["record_unit_id"], statement)
        ids = statement["event_serials"].split("|")
        decoded_statement_events.extend(ids)
        require(int(statement["event_count"]) == len(ids), "statement event count")
        require(statement["exact_card_sequence"].split("|") == [event_by_serial[value]["exact_joint_card_id"] for value in ids], "statement exact sequence")
        require(statement["domain_selection"] == "NONE;DUAL_UNRESOLVED" and statement["complete_source_recovery_without_exemplar"] == "NO", "statement semantic overclaim")
        require(statement["backward_from_full_transition_log"] == "YES", "statement full-log backward failure")
        require(statement["iatromedical_statement_exemplar"] and statement["practical_statement_exemplar"], "statement dual text")
    require(Counter(decoded_statement_events) == Counter(str(i) for i in range(1, 382)), "statement event partition")
    require(len(first_by_unit) == 11, "prose record count")
    require(sum(row["record_reset_status"] == "PASS_RESET_AT_RECORD_START" for row in statements) == 11, "record reset count")
    require(all(row["pre_state"] == UNSET_STATE and row["owner_active_target_previous_operations"].startswith("INTRODUCE/") for row in first_by_unit.values()), "record reset state")
    require(Counter(row["parse_status"] for row in statements) == Counter({"UNIQUE": 12, "AMBIGUOUS": 49, "UNPARSED": 55}), "statement parse profile")
    require(sum(int(row["physical_line_count"]) > 1 for row in statements) == 18, "cross-line statements")
    require(sum(row["backward_from_post_state_only"] == "YES" for row in statements) == 47, "post-state-only count")

    require([int(row["astro_group_serial"]) for row in astro] == list(range(1, 396)), "Astro serials")
    require([int(row["unified_group_ordinal"]) for row in astro] == list(range(382, 777)), "Astro unified ordinals")
    require({row["page"] for row in astro} == {"f67r2", "f68r1", "f69v"}, "Astro page scope")
    require(len({(row["page"], row["source_locus"]) for row in astro}) == 142, "Astro locus count")
    require(all(row["working_mnemonic_or_UNKNOWN_EXEMPLAR"] == "UNKNOWN_EXEMPLAR_LOCAL" for row in astro), "Astro mnemonic introduced")
    require(all(row["domain_selection"] == "NONE;DUAL_UNRESOLVED" and row["complete_source_recovery_without_exemplar"] == "NO" for row in astro), "Astro domain/recovery overclaim")
    require(all("NO_F68_F69_JOIN" in row["semantic_contract"] and "NO_F68_F69_JOIN" in row["crosspage_contract"] for row in astro), "Astro join introduced")
    require(all(row["iatromedical_local_exemplar"] and row["practical_local_exemplar"] for row in astro), "Astro dual text")

    require([int(row["unified_group_ordinal"]) for row in unified] == list(range(1, 777)), "unified ordinals")
    require([row["unified_group_id"] for row in unified] == [f"U{i:04d}" for i in range(1, 777)], "unified IDs")
    require(Counter(row["namespace"] for row in unified) == Counter({"PROSE_EXACT_JOINT_CARD": 381, "ASTRO_PAGE_LOCAL_GROUP": 395}), "unified namespaces")
    require({row["page"] for row in unified} == ALLOWED_PAGES, "unified page scope")
    require(all(row["domain_selection"] == "NONE;DUAL_UNRESOLVED" for row in unified), "unified domain winner")
    require(all(row["complete_source_recovery_without_exemplar"] == "NO" for row in unified), "unified standalone source recovery")
    require(all(row["formal_roundtrip"] == "PASS" for row in unified), "unified formal roundtrip")
    require(all(row["iatromedical_local_exemplar"] and row["practical_local_exemplar"] for row in unified), "unified dual text")

    require([row["unit_id"] for row in units] == UNIT_ORDER, "unit order")
    require(sum(int(row["group_count"]) for row in units) == 776, "unit group total")
    require(sum(int(row["locus_count"]) for row in units) == 199, "unit locus total")
    require(sum(int(row["field_count"].split(";", 1)[0]) for row in units) == 135, "unit field total")
    require(sum(int(row["statement_count"].split(";", 1)[0]) for row in units) == 116, "unit statement total")
    require(all(row["domain_selection"] == "NONE;COEQUAL_DUAL_EDITION" for row in units), "unit domain winner")
    require(all(row["iatromedical_complete_reading"] and row["practical_complete_reading"] for row in units), "unit dual reading incomplete")
    require(all(row["complete_source_recovery_without_exemplar"].startswith("0/") for row in units), "unit standalone source recovery")
    require(all(row["semantic_contract"] == "NO_WINNER;NO_CONFIRMED_LEXEME;BOTH_READINGS_LOCAL_EXEMPLARS" for row in units), "unit semantic contract")

    compiler = data["compiler"]
    require([row["transition_id"] for row in compiler] == [f"T{i:02d}" for i in range(1, 23)], "compiler transition order")
    require(all(row["decode_without_exemplar"] == "FORMAL_ONLY;COMPLETE_SOURCE_RECOVERY_NONE" for row in compiler), "compiler semantic recovery overclaim")
    require(all(row["domain_policy"] == "IATROMEDICAL_AND_PRACTICAL_COEQUAL;NO_SELECTION" for row in compiler), "compiler domain policy")
    require(all(row["semantic_prohibition"] == "NO_PAGE_HOST_COMPONENT_PHONETIC_OR_NEW_CARD_MEANING" for row in compiler), "compiler semantic prohibition")

    invariants = data["invariants"]
    require(len({row["invariant"] for row in invariants}) == 37, "invariant IDs")
    require(all(row["status"] == "PASS" and row["observed"] == row["expected"] for row in invariants), "invariant failure")
    inv = {row["invariant"]: row["observed"] for row in invariants}
    require((inv["F68_F69_SAME_INDEX_FULL_FORM_MATCH"], inv["F68_F69_ALL_PAIR_FULL_FORM_MATCH"], inv["F68_F69_DIRECT_JOIN_COUNT"]) == ("0", "0", "0"), "f68/f69 separation")
    require(inv["COMPLETE_SOURCE_RECOVERY_WITHOUT_EXEMPLAR"] == "0" and inv["DOMAIN_WINNER_SELECTED"] == "0" and inv["CONFIRMED_LEXEME_COUNT"] == "0", "final semantic ceiling")

    sources = data["sources"]
    require(len({row["source_path"] for row in sources}) == 27, "source manifest paths")
    require({row["iteration"] for row in sources} == {f"V{i}" for i in range(60, 69)}, "V60-V68 lineage coverage")
    require(all(row["selection_status"] == "FROZEN_SELECTED_OR_SELECTED_DERIVATIVE" for row in sources), "source selection status")
    for row in sources:
        path = ROOT / row["source_path"]
        require(path.is_file() and digest(path) == row["sha256"] and str(path.stat().st_size) == row["byte_count"], f"source manifest drift: {row['source_path']}")

    release = data["release"]
    require(len({row["release_path"] for row in release}) == 10, "release manifest paths")
    expected_release_counts = {173, 381, 135, 116, 395, 776, 14, 22, 37, 27}
    require({int(row["row_count"]) for row in release} == expected_release_counts, "release manifest counts")
    for row in release:
        path = ROOT / row["release_path"]
        require(path.is_file() and digest(path) == row["sha256"], f"release manifest drift: {row['release_path']}")
        require(len(read_tsv(path)) == int(row["row_count"]), f"release row count drift: {row['release_path']}")
        require(row["canonical_status"] == "V69_R3_DETERMINISTIC_DUAL_RELEASE" and row["semantic_policy"] == "NO_WINNER;LOCAL_EXEMPLARS;FORMAL_LAYERS_SEPARATE", "release policy")

    before = {name: digest(path) for name, (path, _) in FILES.items()}
    subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(path) for name, (path, _) in FILES.items()}
    require(before == after, "builder not byte-deterministic")

    print("PASS V69 R3 validator")
    print("cards=173 events=381 fields=135 statements=116 astro=395 unified=776 units=14")
    print("mnemonic=11/85 formal=4/45 control_union=14/119 unknown=162/296 exemplar_only=159/262")
    print("resets=11 crossline=18 f68_f69=0/0/NONE source_without_exemplar=0/776")
    print("domain_winner=NONE confirmed_lexemes=0 source_hashes=27 release_hashes=10")
    print("deterministic_rebuild=PASS")


if __name__ == "__main__":
    validate()
