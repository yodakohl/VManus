#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    candidates = read_tsv("HUNDRED_SIXTY_NINTH_4_MATERIAL_CLASSES.tsv")
    requirements = read_tsv("HUNDRED_SIXTY_NINTH_7_PROCESS_REQUIREMENTS.tsv")
    events = read_tsv("HUNDRED_SIXTY_NINTH_17_EVENT_F11R_MATERIAL_READING.tsv")
    sources = read_tsv("HUNDRED_SIXTY_NINTH_HISTORICAL_SOURCES.tsv")
    checks = {
        "four_candidate_classes": len(candidates) == 4,
        "one_selected_class": sum(row["selection"] == "SELECTED_WORKING_CLASS" for row in candidates) == 1,
        "selected_is_best_score": max(int(row["total_0_12"]) for row in candidates) == 12,
        "seven_process_requirements": len(requirements) == 7,
        "all_h3_events_present": [int(row["event_serial"]) for row in events] == list(range(39, 56)),
        "all_on_f11r": {row["page"] for row in events} == {"f11r"},
        "one_owner_class": {row["selected_owner_class"] for row in events} == {"BLUE_FLOWERING_ASTRINGENT_WASH_HERB"},
        "no_dictionary_change": {row["dictionary_change"] for row in events} == {"NO"},
        "all_concrete_expansions": all(row["material_expansion_de"].strip() for row in events),
        "three_historical_comparators": len(sources) == 3,
        "no_exact_species_claim": all("IDENTIFICATION" in row["bounded_use"] or "ANALOGY" in row["bounded_use"] for row in sources),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
