#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    codebook = read("PASS990_159_CODEBOOK_WITH_CLEAN_HEADWORDS.tsv")
    heads = read("PASS990_56_SPECIALIST_HEADWORDS.tsv")
    occurrences = read("PASS990_96_SPECIALIST_OCCURRENCES.tsv")
    checks = {
        "codebook_159": len(codebook) == 159,
        "headwords_56": len(heads) == 56 and len({row["teaching_unit_id"] for row in heads}) == 56,
        "occurrences_96": len(occurrences) == 96 and len({row["event_id"] for row in occurrences}) == 96,
        "twelve_revisions": sum(row["change_status"] == "SHORT_COMPOUND_REFINEMENT" for row in heads) == 12,
        "all_headwords_one_token": all(" " not in row["selected_headword_de"].strip() for row in heads),
        "all_occurrences_bound": sum(int(row["occurrences"]) for row in heads) == 96,
        "all_context_readings_present": all(row["observed_event_readings_de"] for row in heads),
        "klarlauf_short": next(row for row in heads if row["teaching_unit_id"] == "W022")["selected_headword_de"] == "KLARLAUF",
        "water_cards_explicit": {row["selected_headword_de"] for row in heads} >= {"FRISCHWASSER", "WARMWASSER"},
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS990_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
