#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read_tsv("PASS962_56_PORTABLE_ROOT_CORES.tsv")
    formulas = read_tsv("PASS962_66_REGISTER_INVARIANT_FORMULAS.tsv")
    events = read_tsv("PASS962_2511_REGISTER_NORMALIZED_EVENTS.tsv")
    root_map = {row["component"]: row["portable_core_de"] for row in roots}
    checks = {
        "roots_56": len(roots) == 56,
        "unique_root_cores": len(root_map) == 56,
        "one_word_each": all(" " not in row["portable_core_de"] and "·" not in row["portable_core_de"] for row in roots),
        "exact_six_revisions": sum(row["revision"] == "BROADENED_FOR_REGISTER_INVARIANCE" for row in roots) == 6,
        "formulas_66": len(formulas) == 66,
        "events_2511": len(events) == 2511,
        "events_unique": len({row["event_id"] for row in events}) == 2511,
        "all_event_components_known": all(all(component in root_map for component in row["component_recipe"].split("+")) for row in events),
        "all_event_atomic_readings_exact": all(row["portable_atomic_reading_de"] == " · ".join(root_map[component] for component in row["component_recipe"].split("+")) for row in events),
        "all_three_registers": {row["register"] for row in events} == {"HERBAL_PREPARATION", "BATH_STATION", "CELESTIAL_LOOKUP"},
        "no_empty_expansions": all(row["register_expansion_de"] for row in events),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in roots + formulas + events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS962_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
