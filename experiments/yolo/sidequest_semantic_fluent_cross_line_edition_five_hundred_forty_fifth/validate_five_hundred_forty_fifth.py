#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = read("FIVE_HUNDRED_FORTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_FLUENT_CARD_PHRASES.tsv")
    events = read("FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    instructions = read("FIVE_HUNDRED_FORTY_FIFTH_NINETY_SEVEN_FLUENT_INSTRUCTIONS.tsv")
    checks = {
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "events381": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "executed380": Counter(row["semantic_execution"] for row in events) == Counter({"EXECUTE_ONCE": 380, "SKIP_ANTICIPATORY_COPY": 1}),
        "instructions97": len(instructions) == 97 and [row["instruction_id"] for row in instructions] == [f"I{i:03d}" for i in range(1, 98)],
        "visible_event_partition": sum(len(row["visible_event_ids"].split("|")) for row in instructions) == 381,
        "source_positions380": len({source for row in instructions for source in row["executed_source_position_ids"].split("|")}) == 380,
        "statements116": len({statement for row in instructions for statement in row["source_statement_ids"].split("|")}) == 116,
        "ends89_8": Counter(row["end_type"] for row in instructions) == Counter({"COMMITTED_CLOSE": 89, "RECORD_FINAL_OPEN": 8}),
        "records11": Counter(row["record"] for row in instructions).keys() == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"},
        "no_line_sentence_rule": all(row["line_end_is_sentence_end"] == "NO" for row in instructions),
        "all_fluent": all(row["fluent_command_de"] for row in cards) and all(row["fluent_instruction_de"] for row in instructions),
        "components_unchanged": all(row["component_values_unchanged"] == "YES" for row in [*cards, *events, *instructions]),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
