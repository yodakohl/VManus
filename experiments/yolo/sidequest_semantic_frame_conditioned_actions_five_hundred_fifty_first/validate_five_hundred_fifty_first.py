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
    lexicon = read("FIVE_HUNDRED_FIFTY_FIRST_ACTION_FRAME_LEXICON.tsv")
    actions = read("FIVE_HUNDRED_FIFTY_FIRST_ONE_HUNDRED_SEVENTY_FIVE_ACTION_OCCURRENCES.tsv")
    clauses = read("FIVE_HUNDRED_FIFTY_FIRST_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv")
    instructions = read("FIVE_HUNDRED_FIFTY_FIRST_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv")
    articles = read("FIVE_HUNDRED_FIFTY_FIRST_ELEVEN_REVISED_ARTICLES.tsv")
    checks = {
        "frame_rules23": len(lexicon) == 23 and len({(row["action_component"], row["frame_code"]) for row in lexicon}) == 23,
        "action_occurrences175": len(actions) == 175 and Counter(row["action_component"] for row in actions) == Counter({"OK": 79, "CHD": 48, "L": 27, "K": 21}),
        "clauses241": len(clauses) == 241 and len({row["clause_id"] for row in clauses}) == 241,
        "instructions97": len(instructions) == 97 and len({row["instruction_id"] for row in instructions}) == 97,
        "articles11": len(articles) == 11 and len({row["record"] for row in articles}) == 11,
        "all_action_rules_covered": Counter((row["action_component"], row["frame_code"]) for row in actions) == Counter({(row["action_component"], row["frame_code"]): int(row["occurrences"]) for row in lexicon}),
        "visible_events381": len({event for row in clauses for event in row["visible_event_ids"].split("|")}) == 381,
        "source_positions380": len({source for row in clauses for source in row["source_position_ids"].split("|")}) == 380,
        "broad_verbs_reduced": sum(row["old_reparsed_clause_de"] != row["frame_conditioned_clause_de"] for row in clauses) > 0,
        "components_not_changed": all(row["component_values_changed"] == "NO" for row in actions + clauses),
        "record_ends8_3": Counter(row["record_final_status"] for row in articles) == Counter({"RECORD_FINAL_OPEN": 8, "COMMITTED_CLOSE": 3}),
        "fixed_pages_only": {row["page"] for row in actions} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in actions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FIFTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
