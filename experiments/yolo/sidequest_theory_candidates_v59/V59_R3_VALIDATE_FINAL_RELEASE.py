#!/usr/bin/env python3
"""Validate counts and layer invariants of the V59 R3 final release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
FILES = {
    "cards": HERE / "V59_R3_FINAL_173_CARD_DICTIONARY.tsv",
    "events": HERE / "V59_R3_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    "fields": HERE / "V59_R3_FINAL_135_FIELD_EDITION.tsv",
    "astro": HERE / "V59_R3_FINAL_395_ASTRO_GROUPS.tsv",
    "ledger": HERE / "V59_R3_FINAL_776_EVENT_LEDGER.tsv",
    "units": HERE / "V59_R3_FINAL_14_RECORD_DIAGRAM_READINGS.tsv",
}
VALIDATION = HERE / "V59_R3_VALIDATION.json"
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
ALLOWED_PAGES = PROSE_PAGES | ASTRO_PAGES
ALLOWED_MNEMONICS = {
    "UNKNOWN_EXEMPLAR",
    "AN?",
    "BEREITUNG?",
    "TEIL?",
    "MASS?",
    "KLAR?",
    "VERWENDEN?",
    "ABLASSEN?",
    "SPÜLEN?",
    "BEREIT?",
    "WARM?",
    "ZUVOR?",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    rows = {name: read_tsv(path) for name, path in FILES.items()}
    cards = rows["cards"]
    events = rows["events"]
    fields = rows["fields"]
    astro = rows["astro"]
    ledger = rows["ledger"]
    units = rows["units"]

    checks: dict[str, bool] = {}
    checks["cards_173"] = len(cards) == 173
    checks["prose_events_381"] = len(events) == 381
    checks["fields_135"] = len(fields) == 135
    checks["astro_groups_395"] = len(astro) == 395
    checks["ledger_rows_776"] = len(ledger) == 776
    checks["units_14"] = len(units) == 14

    card_ids = [row["joint_tuple_id"] for row in cards]
    checks["card_ids_unique"] = len(set(card_ids)) == 173
    card_by_id = {row["joint_tuple_id"]: row for row in cards}
    checks["all_prose_ids_in_dictionary"] = all(row["exact_opaque_id"] in card_by_id for row in events)
    checks["components_do_not_inherit"] = all(row["component_inheritance"] == "NO_WHOLE_CARD_MEANING_INHERITANCE" for row in cards)
    checks["one_global_mnemonic_per_exact_id"] = all(
        len({event["global_default_mnemonic_German"] for event in events if event["exact_opaque_id"] == card_id}) == 1
        for card_id in set(event["exact_opaque_id"] for event in events)
    )
    checks["event_mnemonic_matches_dictionary"] = all(
        row["global_default_mnemonic_German"] == card_by_id[row["exact_opaque_id"]]["global_default_mnemonic_German"]
        for row in events
    )
    checks["mnemonics_allowlisted"] = {row["global_default_mnemonic_German"] for row in cards} <= ALLOWED_MNEMONICS
    checks["withdrawn_ckhy_unknown"] = all(
        row["global_default_mnemonic_German"] == "UNKNOWN_EXEMPLAR"
        for row in cards
        if row["page_host_coordinate"].upper() == "CKHY"
    )
    checks["withdrawn_e_unknown"] = all(
        row["global_default_mnemonic_German"] == "UNKNOWN_EXEMPLAR"
        for row in cards
        if row["page_host_coordinate"].upper() == "E"
    )

    annotated_events = [row for row in events if row["selected_atomic_status"] != "UNKNOWN_EXEMPLAR"]
    unknown_events = [row for row in events if row["selected_atomic_status"] == "UNKNOWN_EXEMPLAR"]
    checks["selected_atomic_events_145"] = len(annotated_events) == 145
    checks["unknown_exemplar_events_236"] = len(unknown_events) == 236

    context_events = [row for row in events if row["licensed_context_prompt_German"] != "NONE"]
    context_fields = {row["field_id"] for row in context_events}
    checks["v56_tier_a_events_45"] = len(context_events) == 45
    checks["v56_tier_a_fields_35"] = len(context_fields) == 35

    event_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        event_by_field[row["field_id"]].append(row)
    checks["field_event_sum_381"] = sum(int(row["event_count"]) for row in fields) == 381
    checks["field_membership_complete"] = set(event_by_field) == {row["field_id"] for row in fields} and all(
        len(event_by_field[row["field_id"]]) == int(row["event_count"]) for row in fields
    )
    checks["closed_90_open_45"] = Counter(row["closure_status"] for row in fields) == Counter({"CLOSED": 90, "OPEN": 45})
    checks["close_once_and_field_final"] = all(
        sum(event["closure_status"] != "NONCLOSE" for event in members) == (1 if next(field["closure_status"] for field in fields if field["field_id"] == field_id) == "CLOSED" else 0)
        and all(event["closure_status"] == "NONCLOSE" for event in members[:-1])
        for field_id, members in event_by_field.items()
    )
    field_named_counts = [sum(event["selected_atomic_status"] != "UNKNOWN_EXEMPLAR" for event in event_by_field[row["field_id"]]) for row in fields]
    checks["fields_without_named_anchor_52"] = sum(count == 0 for count in field_named_counts) == 52
    checks["fully_named_fields_17"] = sum(count == int(field["event_count"]) for count, field in zip(field_named_counts, fields)) == 17

    unit_kinds = Counter(row["unit_kind"] for row in units)
    checks["unit_partition_5_6_3"] = unit_kinds == Counter({"HERBAL_RECORD": 5, "BIOLOGICAL_RECORD": 6, "ASTRO_DIAGRAM": 3})
    checks["unit_ids_unique"] = len({row["unit_id"] for row in units}) == 14
    unit_by_id = {row["unit_id"]: row for row in units}
    checks["unit_texts_complete"] = all(
        row["selected_iatromedical_default_German"].strip()
        and row["selected_nonmedical_rival_German"].strip()
        and row["text_status"].startswith("COMPLETE_")
        for row in units
    )
    checks["all_unit_refs_resolve"] = all(row["unit_reading_ref"] in unit_by_id for row in events + fields + astro + ledger)

    prose_unit_counts = Counter(row["unit_id"] for row in events)
    astro_unit_counts = Counter(row["unit_id"] for row in astro)
    checks["unit_event_counts_match"] = all(
        (prose_unit_counts[row["unit_id"]] if row["unit_kind"] != "ASTRO_DIAGRAM" else astro_unit_counts[row["unit_id"]]) == int(row["event_count"])
        for row in units
    )
    prose_container_counts = Counter(row["unit_id"] for row in fields)
    astro_container_counts = Counter(row["unit_id"] for row in astro)
    astro_unique_loci = {unit_id: len({row["locus"] for row in astro if row["unit_id"] == unit_id}) for unit_id in astro_container_counts}
    checks["unit_container_counts_match"] = all(
        (prose_container_counts[row["unit_id"]] if row["unit_kind"] != "ASTRO_DIAGRAM" else astro_unique_loci[row["unit_id"]]) == int(row["container_count"])
        for row in units
    )
    checks["aggregate_extent_20_100_115_281_142_395"] = (
        sum(int(row["container_count"]) for row in units if row["unit_kind"] == "HERBAL_RECORD") == 20
        and sum(int(row["event_count"]) for row in units if row["unit_kind"] == "HERBAL_RECORD") == 100
        and sum(int(row["container_count"]) for row in units if row["unit_kind"] == "BIOLOGICAL_RECORD") == 115
        and sum(int(row["event_count"]) for row in units if row["unit_kind"] == "BIOLOGICAL_RECORD") == 281
        and sum(int(row["container_count"]) for row in units if row["unit_kind"] == "ASTRO_DIAGRAM") == 142
        and sum(int(row["event_count"]) for row in units if row["unit_kind"] == "ASTRO_DIAGRAM") == 395
    )

    checks["ledger_domain_partition"] = Counter(row["domain"] for row in ledger) == Counter({"PROSE": 381, "ASTRO": 395})
    checks["ledger_ids_unique"] = len({row["ledger_row_id"] for row in ledger}) == 776
    checks["page_allowlist_exact"] = {row["page"] for row in ledger} == ALLOWED_PAGES
    checks["line_never_sentence"] = all(row["line_is_sentence"] == "NO" for row in events + fields + astro + ledger)
    checks["astro_global_mnemonic_unknown"] = all(row["global_default_mnemonic_German"] == "UNKNOWN_EXEMPLAR" for row in astro)
    checks["astro_local_only"] = all(row["mnemonic_license"] == "ASTRO_LOCAL_ONLY_NO_PROSE_IMPORT" for row in astro)
    checks["direct_f68_f69_join_absent"] = all(row["direct_f68_f69_join"] == "NONE" for row in astro + units + ledger)
    checks["all_local_expansions_present"] = all(row["creative_local_event_expansion_German_V49"].strip() for row in events) and all(
        row["creative_local_field_expansion_German_V49"].strip() for row in fields
    ) and all(row["local_slot_default_English_V22"].strip() for row in astro)

    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema": "V59_R3_FINAL_LAYERED_TECHNICAL_EDITION_V1",
        "status": "PASS" if not failed else "FAIL",
        "counts": {
            "prose_card_types": len(cards),
            "prose_events": len(events),
            "prose_fields": len(fields),
            "astro_groups": len(astro),
            "combined_ledger_rows": len(ledger),
            "complete_record_diagram_readings": len(units),
            "selected_atomic_events": len(annotated_events),
            "unknown_exemplar_events": len(unknown_events),
            "v56_tier_a_events": len(context_events),
            "v56_tier_a_fields": len(context_fields),
        },
        "checks": checks,
        "failed_checks": failed,
        "sha256": {name: sha256(path) for name, path in FILES.items()},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL: " + ", ".join(failed))
    print("PASS validation")
    print(json.dumps(result["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
