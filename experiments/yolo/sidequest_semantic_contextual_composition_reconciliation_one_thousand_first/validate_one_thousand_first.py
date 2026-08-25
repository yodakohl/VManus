#!/usr/bin/env python3
"""Validate Pass 1001 outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    contextual = read_tsv("PASS1001_72_CONTEXTUAL_COMPOSITIONS.tsv")
    split = read_tsv("PASS1001_13_SPLIT_HEADWORD_GROUPS.tsv")
    codebook = read_tsv("PASS1001_175_REVISED_CODEBOOK.tsv")
    summary = json.loads((OUT / "PASS1001_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "seventy_two_surface_recipes": len(contextual) == 72,
        "ninety_six_specialist_events": sum(int(row["occurrences"]) for row in contextual) == 96,
        "fifty_six_old_units_covered": len({row["old_teaching_unit_id"] for row in contextual}) == 56,
        "thirteen_split_groups": len(split) == 13,
        "revised_codebook_175": len(codebook) == 175,
        "all_contextual_root_sums_nonempty": all(row["root_sum_default_de"].strip() for row in contextual),
        "all_contextual_events_bound": all(row["event_ids"].strip() for row in contextual),
        "all_old_specialist_ids_removed": not any(row["teaching_unit_id"].startswith(("W", "L")) for row in codebook),
        "all_contextual_ids_present": sum(row["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD" for row in codebook) == 72,
        "no_memorized_specialist_whole_words": not any(row["unit_type"] in {"MEMORIZED_SPECIALIST_WHOLE_WORD", "MEMORIZED_VISUAL_WHOLE_CARD"} for row in codebook),
        "formula_cards_preserved": sum(row["unit_type"] == "FORMULA_CARD" for row in codebook) == 30,
        "drug_labels_preserved": sum(row["unit_type"] == "MEMORIZED_DRUG_LABEL" for row in codebook) == 16,
        "summary_matches": summary["new_codebook_units"] == 175 and summary["new_portable_semantic_roots_required"] == 0,
        "no_blank_spoken_values": all(row["spoken_value_de"].strip() for row in codebook),
        "no_sealed_pages": not any("f84" in "\t".join(row.values()).lower() for rows in (contextual, split, codebook) for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (OUT / "PASS1001_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], result["passed"], result["total"])
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
