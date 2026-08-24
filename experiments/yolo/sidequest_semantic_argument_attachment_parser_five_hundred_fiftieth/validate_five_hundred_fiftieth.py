#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    clauses = read("FIVE_HUNDRED_FIFTIETH_TWO_HUNDRED_FORTY_ONE_ACTION_BUNDLES.tsv")
    attachments = read("FIVE_HUNDRED_FIFTIETH_THREE_HUNDRED_EIGHTY_SOURCE_ATTACHMENTS.tsv")
    instructions = read("FIVE_HUNDRED_FIFTIETH_NINETY_SEVEN_REPARSED_INSTRUCTIONS.tsv")
    articles = read("FIVE_HUNDRED_FIFTIETH_ELEVEN_REPARSED_ARTICLES.tsv")
    source_ids = [row["source_position_id"] for row in attachments]
    visible_ids = [event for row in attachments for event in row["visible_event_ids"].split("|")]
    clause_sources = [source for row in clauses for source in row["source_position_ids"].split("|")]
    checks = {
        "bundles241": len(clauses) == 241 and len({row["clause_id"] for row in clauses}) == 241,
        "attachments380": len(attachments) == 380 and len(set(source_ids)) == 380,
        "visible381": len(visible_ids) == 381 and len(set(visible_ids)) == 381,
        "clause_partition380": len(clause_sources) == 380 and Counter(clause_sources) == Counter(source_ids),
        "instructions97": len(instructions) == 97 and len({row["instruction_id"] for row in instructions}) == 97,
        "articles11": len(articles) == 11 and len({row["record"] for row in articles}) == 11,
        "elliptic5": sum(row["attachment_status"] == "ELLIPTIC_INHERITED_ACTION" for row in clauses) == 5,
        "all_clauses_readable": all(row["reparsed_clause_de"] for row in clauses),
        "all_instructions_readable": all(row["reparsed_instruction_de"].endswith(".") for row in instructions),
        "record_ends8_3": Counter(row["record_final_status"] for row in articles) == Counter({"RECORD_FINAL_OPEN": 8, "COMMITTED_CLOSE": 3}),
        "components_unchanged": all(row["component_values_unchanged"] == "YES" for row in clauses + attachments),
        "fixed_pages_only": {row["page"] for row in instructions} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in instructions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FIFTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
