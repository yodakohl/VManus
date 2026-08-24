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
    log = read("FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    manual = read("FIVE_HUNDRED_TWENTY_SIXTH_SIXTEEN_RULE_MASTER_MANUAL.tsv")
    audit = read("FIVE_HUNDRED_TWENTY_SIXTH_ZERO_FREE_CHOICE_AUDIT.tsv")
    usage = read("FIVE_HUNDRED_TWENTY_SIXTH_RENDERER_USAGE.tsv")
    checks = {
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "pages7": len({row["bound_exemplar_page"] for row in log}) == 7,
        "sheets7": len({row["bound_renderer_sheet"] for row in log}) == 7,
        "manual16": len(manual) == 16 and all(row["free_choice"] == "NO" for row in manual),
        "zero_free_choices": all(row["final_free_decision_count"] == "0" for row in log),
        "all_deterministic": all(row["final_master_mode"] == "DETERMINISTIC_EXEMPLAR_EXECUTION" for row in log),
        "no_program_choice": all(row["free_program_choice"] == "NO" for row in log),
        "no_owner_choice": all(row["free_owner_choice_final"] == "NO" for row in log),
        "no_renderer_choice": all(row["free_renderer_choice"] == "NO" for row in log),
        "execution_partition314_8_59": Counter(row["execution_source"] for row in log)
        == Counter({"GLOBAL_RULE_RENDERER": 314, "AUTOMATIC_CONTEXT_RULE": 8, "BOUND_PAGE_ENTRY": 59}),
        "audit_total_zero": next(row for row in audit if row["choice_family"] == "TOTAL")["current_free_decisions"] == "0",
        "usage381": sum(int(row["events"]) for row in usage) == 381,
        "surface_roundtrip": all(row["stamp_output_surface"] == row["renderer_final_surface"] for row in log),
        "semantic_invention_absent": all(row["free_semantic_invention"] == "NO" for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in log),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
