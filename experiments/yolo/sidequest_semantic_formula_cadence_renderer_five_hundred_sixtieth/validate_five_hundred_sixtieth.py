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
    cadences = read("FIVE_HUNDRED_SIXTIETH_ELEVEN_FORMULA_CADENCES.tsv")
    executions = read("FIVE_HUNDRED_SIXTIETH_THIRTY_TWO_CADENCE_EXECUTIONS.tsv")
    ledger = read("FIVE_HUNDRED_SIXTIETH_THREE_HUNDRED_EIGHTY_ONE_RENDERER_LEDGER.tsv")
    counts = Counter(row["renderer_source"] for row in ledger)
    checks = {
        "eleven_cadences": len(cadences) == 11 and len({row["cadence_id"] for row in cadences}) == 11,
        "twelve_mixed_loci": len({row["locus"] for row in executions}) == 12,
        "thirty_two_executions": len(executions) == 32 and len({row["event_id"] for row in executions}) == 32,
        "one_shared_cadence": sum(int(row["attested_loci"]) > 1 for row in cadences) == 1,
        "no_cadence_local_memory": all(row["local_locus_memory"] == "NO" for row in cadences + executions),
        "ledger381": len(ledger) == 381 and len({row["event_id"] for row in ledger}) == 381,
        "source_counts": counts == Counter({"GLOBAL_RULE_RENDERER": 314, "FORMULA_CADENCE_RULE": 32, "UNIFORM_LOCUS_STAMP": 27, "AUTOMATIC_CONTEXT_RULE": 8}),
        "roundtrip381": all(row["surface_roundtrip"] == "YES" for row in ledger),
        "no_free_choice": all(row["free_choice"] == "NO" for row in ledger),
        "fixed_pages": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
