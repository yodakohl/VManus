#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    templates = read("FOUR_HUNDRED_SEVENTY_SEVENTH_NINE_SENTENCE_TEMPLATES.tsv")
    occurrences = read("FOUR_HUNDRED_SEVENTY_SEVENTH_MOTIF_OCCURRENCES.tsv")
    statements = read("FOUR_HUNDRED_SEVENTY_SEVENTH_116_TEMPLATE_SENTENCES.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_SEVENTH_14_TEMPLATE_UNIT_EDITIONS.tsv")
    checks = {
        "templates_9": len(templates) == 9,
        "all_templates_cross_register": all(row["cross_register"] == "YES" for row in templates),
        "occurrences_nonempty": bool(occurrences),
        "occurrence_ids_unique": len({row["occurrence_id"] for row in occurrences}) == len(occurrences),
        "statements_116": len(statements) == 116,
        "statement_event_sum_381": sum(int(row["events"]) for row in statements) == 381,
        "statement_events_preserved": len({event for row in statements for event in row["event_ids"].split("|")}) == 381,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "all_sentences_nonempty": all(row["template_workshop_sentence_de"] for row in statements),
        "fixed_pages_only": {row["page"] for row in statements + units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in occurrences + statements + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
