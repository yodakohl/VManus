#!/usr/bin/env python3
"""Independently validate the compact V69 R4 release."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = read_tsv("V69_R4_FINAL_173_CARD_DICTIONARY.tsv")
    prose = read_tsv("V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")
    fields = read_tsv("V69_R4_FINAL_135_FIELD_EDITION.tsv")
    statements = read_tsv("V69_R4_FINAL_116_STATEMENT_EDITION.tsv")
    astro = read_tsv("V69_R4_FINAL_395_ASTRO_GROUPS.tsv")
    ledger = read_tsv("V69_R4_FINAL_776_GROUP_LEDGER.tsv")
    units = read_tsv("V69_R4_FINAL_14_UNIT_DUAL_TRANSLATION.tsv")
    manual = read_tsv("V69_R4_FINAL_9_LESSON_WORKSHOP_MANUAL.tsv")

    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    field_status = Counter(row["parse_status"] for row in fields)
    statement_status = Counter(row["parse_status"] for row in statements)
    controls = [row for row in dictionary if row["V69_FINAL_CONTROL_CLASS"] != "UNKNOWN_EXEMPLAR_WHOLE_CARD"]
    checks = {
        "row_counts": tuple(map(len, (dictionary, prose, fields, statements, astro, ledger, units, manual)))
        == (173, 381, 135, 116, 395, 776, 14, 9),
        "dictionary_unique": len(dmap) == 173,
        "dictionary_occurrences": sum(int(row["occurrences"]) for row in dictionary) == 381,
        "prose_serials": [int(row["event_serial"]) for row in prose] == list(range(1, 382)),
        "ledger_serials": [int(row["global_index"]) for row in ledger] == list(range(1, 777)),
        "prose_dictionary_join": all(row["joint_tuple_id"] in dmap for row in prose),
        "mnemonics_match_dictionary": all(
            row["selected_exact_mnemonic"] == dmap[row["joint_tuple_id"]]["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
            for row in prose
        ),
        "control_types_14": len(controls) == 14,
        "unknown_types_159": len(dictionary) - len(controls) == 159,
        "event_parse_119_262": sum(row["parse_status"] != "UNPARSED_EXEMPLAR" for row in prose) == 119,
        "field_parse_14_56_65": field_status == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}),
        "statement_parse_12_49_55": statement_status == Counter({"UNIQUE": 12, "AMBIGUOUS": 49, "UNPARSED": 55}),
        "unit_inventory": {row["unit_id"] for row in units}
        == {*(f"H{i}" for i in range(1, 6)), *(f"B{i}" for i in range(1, 7)), *(f"A{i}" for i in range(1, 4))},
        "dual_text_complete": all(
            row["iatromedical_text"].strip() and row["practical_text"].strip() for row in ledger
        ),
        "dual_units_coequal": all(row["content_status"] == "COEQUAL_CONTENT_FORK" for row in units),
        "astro_unjoined": all(row["f68_f69_mapping"] == "NONE" for row in astro),
        "no_source_recovery_claim": all(
            row["source_recovery_without_exemplar"] == "NO_FULL_SOURCE_RECOVERY" for row in ledger
        ),
        "sealed_pages_absent": all(not row["page"].startswith(("f84", "f84r")) for row in ledger),
    }
    prior = json.loads((HERE / "V69_R4_VALIDATION.json").read_text(encoding="utf-8"))
    checks["builder_validation_pass"] = prior.get("status") == "PASS" and all(prior.get("checks", {}).values())
    result = {
        "artifact": "V69_R4_INDEPENDENT_VALIDATION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "stop_rule": "V69_COMPLETE_NO_V70_AUTOMATIC",
    }
    (HERE / "V69_R4_INDEPENDENT_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
