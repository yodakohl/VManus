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
    bases = read("FIVE_HUNDRED_EIGHTEENTH_EIGHTEEN_BASE_PATHS.tsv")
    audit = read("FIVE_HUNDRED_EIGHTEENTH_63_UNIQUE_PROGRAM_EDIT_AUDIT.tsv")
    distance = read("FIVE_HUNDRED_EIGHTEENTH_EDIT_DISTANCE_SUMMARY.tsv")
    log = read("FIVE_HUNDRED_EIGHTEENTH_381_EMERGENT_MASTER_LOG.tsv")
    decisions = read("FIVE_HUNDRED_EIGHTEENTH_71_CONSCIOUS_DECISIONS.tsv")
    dist = Counter({int(row["edit_distance"]): int(row["unique_programs"]) for row in distance})
    types = Counter(row["decision_type"] for row in decisions)
    checks = {
        "bases18": len(bases) == 18 and len({row["base_id"] for row in bases}) == 18,
        "base_families9_9": Counter(row["base_family"] for row in bases)
        == Counter({"BIO_RECURRENT_DEFAULT": 9, "SHARED_SENTENCE_MOTIF": 9}),
        "unique_programs63": len(audit) == 63 and len({row["statement_id"] for row in audit}) == 63,
        "distance_distribution": dist
        == Counter({0: 1, 1: 15, 2: 21, 3: 11, 4: 2, 5: 2, 6: 6, 7: 2, 8: 2, 15: 1}),
        "near48_far15": sum(v for k, v in dist.items() if k <= 3) == 48
        and sum(v for k, v in dist.items() if k >= 4) == 15,
        "no_reused_exact_edit_recipe": all(row["same_edit_recipe_count"] == "1" for row in audit)
        and all(row["reusable_edit_recipe"] == "NO" for row in audit),
        "programs_not_taught": all(row["teach_as_program"] == "NO" for row in audit),
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "program_choice_removed": all(row["program_selection_decision"] == "NONE" for row in log),
        "decisions71": len(decisions) == 71,
        "decision_types21_50": types
        == Counter({"RESET_VISIBLE_OWNER": 21, "ENTER_ALLOGRAPH_BLOCK": 50}),
        "conscious67": sum(row["emergent_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in log)
        == 67,
        "automatic314": sum(row["emergent_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 314,
        "five_state_rule_everywhere": all(
            row["emergent_program_rule"] == "READ_NEXT_CARD_AND_APPLY_FIVE_STATE_AUTOMATON"
            for row in log
        ),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in audit + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTEENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
