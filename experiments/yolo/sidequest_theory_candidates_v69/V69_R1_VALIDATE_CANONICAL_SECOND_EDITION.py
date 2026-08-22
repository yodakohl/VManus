#!/usr/bin/env python3
"""Validate the deterministic final R1 V69 release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
EXPECTED_UNIT_COUNTS = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27, "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9, "A1": 190, "A2": 65, "A3": 140}
EXPECTED_MNEMONICS = {"MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?", "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?"}
EXPECTED_FORMALS = {"VORGABEPARAMETER?", "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN", "STANDARDSLOT_SETZEN", "LOKALEN_RELATIONSSLOT_SETZEN"}


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_ids(text: str) -> list[int]:
    return [int(value) for value in text.split("|") if value]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(name: str, condition: bool, detail: object, checks: list[dict[str, object]]) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main() -> None:
    dictionary = read("V69_R1_173_EXACT_CARD_DICTIONARY.tsv")
    events = read("V69_R1_381_PROSE_EVENT_INTERLINEAR.tsv")
    fields = read("V69_R1_135_FIELD_DUAL_EDITION.tsv")
    statements = read("V69_R1_116_STATEMENT_DUAL_EDITION.tsv")
    astro = read("V69_R1_395_ASTRO_GROUP_DUAL_EDITION.tsv")
    unified = read("V69_R1_776_UNIFIED_DUAL_LEDGER.tsv")
    units = read("V69_R1_14_COMPLETE_UNIT_DUAL_EDITION.tsv")
    uncertainties = read("V69_R1_UNCERTAINTIES_AND_CONTRADICTIONS.tsv")
    checks: list[dict[str, object]] = []

    gate("dictionary_173", len(dictionary) == 173 and len({r["joint_tuple_id"] for r in dictionary}) == 173, len(dictionary), checks)
    mnemonic_rows = [r for r in dictionary if r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN_EXEMPLAR"]
    formal_rows = [r for r in dictionary if r["FORMAL_CONTROL"] != "NONE"]
    active_ids = {r["joint_tuple_id"] for r in mnemonic_rows + formal_rows}
    gate("exact_eleven_mnemonics", len(mnemonic_rows) == 11 and {r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for r in mnemonic_rows} == EXPECTED_MNEMONICS, len(mnemonic_rows), checks)
    gate("exact_four_formals", len(formal_rows) == 4 and {r["FORMAL_CONTROL"] for r in formal_rows} == EXPECTED_FORMALS, len(formal_rows), checks)
    gate("active_union_fourteen", len(active_ids) == 14, len(active_ids), checks)
    gate("unknown_cards_159", sum(r["dictionary_status"] == "UNKNOWN_EXEMPLAR" for r in dictionary) == 159, True, checks)
    gate("dictionary_occurrences_381", sum(int(r["occurrences"]) for r in dictionary) == 381, True, checks)
    gate("dictionary_no_local_content", all(r["local_content_binding"].startswith("EXCLUDED_FROM_DICTIONARY") for r in dictionary), True, checks)

    gate("events_381", len(events) == 381 and [int(r["event_serial"]) for r in events] == list(range(1, 382)), len(events), checks)
    gate("event_pages", {r["page"] for r in events} == ALLOWED_PAGES - {"f67r2", "f68r1", "f69v"}, True, checks)
    gate("event_ids_in_dictionary", {r["joint_tuple_id"] for r in events} <= {r["joint_tuple_id"] for r in dictionary}, True, checks)
    gate("mnemonic_event_count_85", sum(r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN_EXEMPLAR" for r in events) == 85, True, checks)
    gate("formal_event_count_45", sum(r["FORMAL_CONTROL_AT_THIS_EVENT"] != "NONE" for r in events) == 45, True, checks)
    gate("recognized_union_119", sum((r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN_EXEMPLAR") or (r["FORMAL_CONTROL_AT_THIS_EVENT"] != "NONE") for r in events) == 119, True, checks)
    gate("exemplar_only_262", sum((r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == "UNKNOWN_EXEMPLAR") and (r["FORMAL_CONTROL_AT_THIS_EVENT"] == "NONE") for r in events) == 262, True, checks)
    gate("event_dual_content", all(r["IATROMEDICAL_SIMPLE_BATH_ELECTION"] and r["PRACTICAL_MATERIAL_PROCESS_SCHEDULE"] and r["content_preference"] == "COEQUAL" for r in events), True, checks)

    gate("fields_135", len(fields) == 135 and len({r["field_id"] for r in fields}) == 135, len(fields), checks)
    field_event_ids = [value for row in fields for value in split_ids(row["event_serials"])]
    gate("field_partition_381", sorted(field_event_ids) == list(range(1, 382)), len(field_event_ids), checks)
    gate("field_dual_content", all(r["IATROMEDICAL_SIMPLE_BATH"] and r["PRACTICAL_MATERIAL_PROCESS"] and r["content_preference"] == "COEQUAL" for r in fields), True, checks)

    gate("statements_116", len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116, len(statements), checks)
    statement_event_ids = [value for row in statements for value in split_ids(row["event_serials"])]
    gate("statement_partition_381", sorted(statement_event_ids) == list(range(1, 382)), len(statement_event_ids), checks)
    gate("statement_dual_content", all(r["IATROMEDICAL_SIMPLE_BATH"] and r["PRACTICAL_MATERIAL_PROCESS"] and r["content_preference"] == "COEQUAL" for r in statements), True, checks)
    gate("line_not_sentence_contract", all("PHYSICAL_LINE_NOT_SENTENCE" in r["semantic_contract"] for r in statements), True, checks)

    gate("astro_395", len(astro) == 395 and [int(r["group_serial"]) for r in astro] == list(range(1, 396)), len(astro), checks)
    gate("astro_pages", {r["page"] for r in astro} == {"f67r2", "f68r1", "f69v"}, True, checks)
    gate("astro_no_prose_cards", all(r["mnemonic"] == "NOT_APPLICABLE_ASTRO" and "NO_PROSE_FORMAL_IMPORT" in r["formal_value"] for r in astro), True, checks)
    gate("astro_dual_content", all(r["IATROMEDICAL_ELECTION"] and r["PRACTICAL_SCHEDULE"] and r["content_preference"] == "COEQUAL" for r in astro), True, checks)
    gate("astro_no_f68_f69_mapping", all(r["direct_f68_f69_mapping"] == "NONE" for r in astro), True, checks)

    gate("unified_776", len(unified) == 776 and [int(r["global_group_serial"]) for r in unified] == list(range(1, 777)), len(unified), checks)
    gate("unified_scope", {r["page"] for r in unified} == ALLOWED_PAGES and all(not r["page"].startswith("f84") for r in unified), sorted({r["page"] for r in unified}), checks)
    gate("unified_split", Counter(r["source_kind"] for r in unified) == {"PROSE_EXACT_CARD": 381, "ASTRO_PAGE_LOCAL_GROUP": 395}, dict(Counter(r["source_kind"] for r in unified)), checks)
    gate("unified_unit_counts", dict(Counter(r["unit_id"] for r in unified)) == EXPECTED_UNIT_COUNTS, dict(Counter(r["unit_id"] for r in unified)), checks)
    gate("unified_dual_content", all(r["IATROMEDICAL_SIMPLE_BATH_ELECTION"] and r["PRACTICAL_MATERIAL_PROCESS_SCHEDULE"] and r["content_preference"] == "COEQUAL" for r in unified), True, checks)

    gate("units_14", len(units) == 14 and {r["unit_id"] for r in units} == set(EXPECTED_UNIT_COUNTS), len(units), checks)
    gate("unit_counts_sum", sum(int(r["group_count"]) for r in units) == 776, True, checks)
    gate("unit_dual_complete", all(r["complete_IATROMEDICAL_SIMPLE_BATH_ELECTION_text"] and r["complete_PRACTICAL_MATERIAL_PROCESS_SCHEDULE_text"] and r["readable_concise_iatromedical_translation"] and r["readable_concise_practical_translation"] and r["content_preference"] == "COEQUAL" for r in units), True, checks)
    gate("unit_classes", all((r["unit_id"].startswith("H") and (r["iatromedical_content_class"], r["practical_content_class"]) == ("SIMPLE", "MATERIAL")) or (r["unit_id"].startswith("B") and (r["iatromedical_content_class"], r["practical_content_class"]) == ("BATH", "PROCESS")) or (r["unit_id"].startswith("A") and (r["iatromedical_content_class"], r["practical_content_class"]) == ("ELECTION", "SCHEDULE")) for r in units), True, checks)
    gate("uncertainty_coverage", len(uncertainties) >= 24 and {r["unit_id"] for r in uncertainties if r["scope"] == "UNIT"} == set(EXPECTED_UNIT_COUNTS), len(uncertainties), checks)

    required_docs = ["V69_R1_WORKSHOP_COMPILER_MANUAL.md", "V69_R1_ONE_PAGE_FINAL_THEORY.md", "V69_R1_CANONICAL_SECOND_EDITION_REPORT.md"]
    gate("required_docs", all((OUT / name).is_file() for name in required_docs), required_docs, checks)
    gate("explicit_stop", "NO V70" in (OUT / "V69_R1_ONE_PAGE_FINAL_THEORY.md").read_text(encoding="utf-8"), True, checks)

    hash_manifest = json.loads((OUT / "V69_R1_ARTIFACT_SHA256.json").read_text(encoding="utf-8"))
    gate("artifact_hashes", all(file_hash(OUT / name) == value for name, value in hash_manifest.items()), len(hash_manifest), checks)

    result = {
        "status": "PASS", "checks_passed": len(checks),
        "counts": {"pages": 10, "dictionary": 173, "mnemonics": 11, "formal_controls": 4, "active_union": 14, "unknown_cards": 159, "events": 381, "fields": 135, "statements": 116, "astro_groups": 395, "unified_groups": 776, "units": 14},
        "content_columns": "COEQUAL_IATROMEDICAL_AND_PRACTICAL",
        "new_semantics": 0, "sealed_pages_present": False, "next_iteration": "STOP_NO_V70",
        "checks": checks,
    }
    (OUT / "V69_R1_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", **result["counts"], "checks_passed": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
