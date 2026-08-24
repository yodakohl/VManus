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
    formulas = read("FIVE_HUNDRED_FORTY_SEVENTH_FORMULA_LEXICON.tsv")
    occurrences = read("FIVE_HUNDRED_FORTY_SEVENTH_FORMULA_OCCURRENCES.tsv")
    compressed = read("FIVE_HUNDRED_FORTY_SEVENTH_COMPRESSED_INSTRUCTIONS.tsv")
    summary = json.loads((HERE / "FIVE_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    occurrence_counts = Counter(row["formula_id"] for row in occurrences)
    checks = {
        "formula_count15": len(formulas) == 15 and len({row["formula_id"] for row in formulas}) == 15,
        "teach5_pairings10": Counter(row["tier"] for row in formulas) == Counter({"TEACH_FORMULA": 5, "OBSERVED_PAIRING": 10}),
        "occurrence_counts_match": all(occurrence_counts[row["formula_id"]] == int(row["occurrences"]) for row in formulas),
        "all_cross_record": all(row["cross_record_portable"] == "YES" for row in occurrences),
        "instruction_count97": len(compressed) == 97 and len({row["instruction_id"] for row in compressed}) == 97,
        "executed_source380": summary["executed_source_positions"] == 380 and sum(int(row["source_card_tokens"]) for row in compressed) == 380,
        "compression366": summary["compressed_tokens"] == 366 and sum(int(row["compressed_tokens"]) for row in compressed) == 366,
        "selector_paid_positive": summary["dictionary_cost"] == 11 and summary["selector_paid_gain"] == 3,
        "components_unchanged": all(row["component_values_changed"] == "NO" for row in formulas),
        "fixed_pages_only": {row["page"] for row in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
