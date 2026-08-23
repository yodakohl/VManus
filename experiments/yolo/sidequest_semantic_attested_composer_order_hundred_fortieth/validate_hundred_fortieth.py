#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audits = rows("HUNDRED_FORTIETH_EIGHT_COMPOSER_ECOLOGY_AUDITS.tsv")
    repairs = rows("HUNDRED_FORTIETH_EIGHT_REPAIRED_TEMPLATE_INSTRUCTIONS.tsv")
    checks = {
        "audits_8": len(audits) == 8,
        "repairs_8": len(repairs) == 8,
        "exercise_ids_match": {r["exercise_id"] for r in audits} == {r["exercise_id"] for r in repairs},
        "source_templates_present": all(r["source_statement_ids"] for r in repairs),
        "two_cell_application": next(r for r in repairs if r["exercise_id"] == "C07")["source_statement_ids"] == "B4-S004|B4-S005",
        "paired_measure_kept": next(r for r in audits if r["exercise_id"] == "C05")["attested_adjacent_pairs"] == "2",
        "all_cells_nonempty": all(all(v for v in r.values()) for table in (audits, repairs) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
