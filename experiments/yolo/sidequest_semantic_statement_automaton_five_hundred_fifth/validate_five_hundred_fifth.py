#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    machine = read("FIVE_HUNDRED_FIFTH_FIVE_STATE_AUTOMATON.tsv")
    bigrams = read("FIVE_HUNDRED_FIFTH_56_PRIMITIVE_BIGRAMS.tsv")
    traces = read("FIVE_HUNDRED_FIFTH_116_AUTOMATON_TRACES.tsv")
    defaults = read("FIVE_HUNDRED_FIFTH_NINE_PREFERRED_BIO_PATHS.tsv")
    manual = read("FIVE_HUNDRED_FIFTH_122_ITEM_AUTOMATON_MANUAL.tsv")
    unseen = {
        f"{row['left_primitive']}>{row['right_primitive']}"
        for row in bigrams if row["observed_status"] == "UNSEEN"
    }
    checks = {
        "five_states_eight_inputs_40_rows": len(machine) == 40 and len({r["state"] for r in machine}) == 5,
        "bigrams_56": len(bigrams) == 56,
        "attested_bigrams_53": sum(r["observed_status"] == "ATTESTED" for r in bigrams) == 53,
        "exact_three_unseen": unseen == {
            "SOURCE_DRAW>MOVE_PASS", "SOURCE_DRAW>TARGET_HANDOFF", "METER_CHECK>CLOSE"
        },
        "unseen_are_rejected": all(r["machine_verdict"] == "REJECT" for r in bigrams if r["observed_status"] == "UNSEEN"),
        "attested_are_allowed": all(r["machine_verdict"] == "ALLOW" for r in bigrams if r["observed_status"] == "ATTESTED"),
        "traces_116": len(traces) == 116,
        "all_statements_accepted": all(r["machine_result"] == "ACCEPT" for r in traces),
        "closed_only_at_end": all("CLOSED>" not in r["state_path"] for r in traces),
        "nine_defaults": len(defaults) == 9,
        "preferred_support_53": sum(int(r["support_statements"]) for r in defaults) == 53,
        "manual_122": len(manual) == 122,
        "one_automaton_rule": sum(r["source_artifact"] == "PASS505_FIVE_STATE_AUTOMATON" for r in manual) == 1,
        "seal_absent": not any("f84" in str(value).lower() for row in traces for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
