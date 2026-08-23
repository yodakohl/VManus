#!/usr/bin/env python3
"""Validate the minimal cross-content semantic dictionary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    core = read_tsv("SEVENTY_SECOND_43_MINIMAL_CORE_DICTIONARY.tsv")
    layers = read_tsv("SEVENTY_SECOND_89_LAYER_POCKET_DICTIONARY.tsv")
    groups = read_tsv("SEVENTY_SECOND_381_MINIMAL_CARD_READINGS.tsv")
    statements = read_tsv("SEVENTY_SECOND_116_MINIMAL_STATEMENT_READINGS.tsv")
    checks = {
        "forty_three_core_entries": len(core) == 43 and len({row["entry_id"] for row in core}) == 43,
        "twenty_eight_roots": sum(row["entry_kind"] == "PRODUCTIVE_ROOT" for row in core) == 28,
        "fifteen_learned_entries": sum(row["entry_kind"] == "LEARNED_WHOLE_OR_PATTERN" for row in core) == 15,
        "root_values_single_word": all(len(row["minimal_value_de"].split()) == 1 for row in core if row["entry_kind"] == "PRODUCTIVE_ROOT"),
        "eighty_nine_layers": len(layers) == 89,
        "nonlexical_layers_marked_nonword": all(row["dictionary_status"] == "NOT_A_WORD__WORKSHOP_CONTEXT_LAYER" for row in layers if row["hierarchy_level"] not in {"L1_ATOMIC_ROOT", "L2_LEARNED_NOMENCLATOR"}),
        "381_groups": len(groups) == 381 and len({row["source_group_id"] for row in groups}) == 381,
        "116_statements": len(statements) == 116 and len({row["unit_id"] for row in statements}) == 116,
        "all_group_readings_nonempty": all(row["minimal_component_reading_de"] and row["minimal_card_reading_de"] for row in groups),
        "allowed_pages": {row["page"] for row in groups + statements} == ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in core + layers + groups + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
