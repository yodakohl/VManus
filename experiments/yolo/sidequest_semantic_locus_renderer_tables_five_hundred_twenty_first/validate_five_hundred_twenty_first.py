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
    modes = read("FIVE_HUNDRED_TWENTY_FIRST_THIRTY_EIGHT_LOCUS_RENDERER_MODES.tsv")
    entries = read("FIVE_HUNDRED_TWENTY_FIRST_SIXTY_SIX_LOCAL_OVERRIDE_ENTRIES.tsv")
    log = read("FIVE_HUNDRED_TWENTY_FIRST_381_LOCUS_RENDERER_LOG.tsv")
    decisions = read("FIVE_HUNDRED_TWENTY_FIRST_THIRTY_EIGHT_CONSCIOUS_DECISIONS.tsv")
    policies = read("FIVE_HUNDRED_TWENTY_FIRST_RENDERER_POLICY_COMPARISON.tsv")
    checks = {
        "modes38": len(modes) == 38 and len({row["mode_id"] for row in modes}) == 38,
        "entries66": len(entries) == 66
        and len({(row["mode_id"], row["input_rule_surface"]) for row in entries}) == 66,
        "mode_sizes21_9_5_3": Counter(int(row["override_entries"]) for row in modes)
        == Counter({1: 21, 2: 9, 3: 5, 4: 3}),
        "override_events67": sum(int(row["support_events"]) for row in entries) == 67,
        "affected_locus_events278": sum(int(row["locus_events"]) for row in modes) == 278,
        "affected_regular_events211": sum(int(row["rule_rendered_events"]) for row in modes) == 211,
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "decisions38": len(decisions) == 38 and len({row["locus"] for row in decisions}) == 38,
        "only_locus_load_decisions": Counter(row["decision_type"] for row in decisions)
        == Counter({"LOAD_LOCUS_RENDERER_TABLE": 38}),
        "conscious38": sum(row["locus_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in log) == 38,
        "automatic343": sum(row["locus_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 343,
        "policy_selected": [row["renderer_policy"] for row in policies if row["selected"] == "YES"]
        == ["LOCUS_OVERRIDE_TABLE"],
        "surface_roundtrip": all(row["surface_roundtrip"] == "YES" for row in log),
        "owner_choice_stays_removed": all(row["free_owner_choice"] == "NO" for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in modes + entries + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
