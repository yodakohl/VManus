#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    forms = read("THREE_HUNDRED_EIGHTY_SEVENTH_15_FORM_FAULT_AND_REPAIR.tsv")
    phenomena = read("THREE_HUNDRED_EIGHTY_SEVENTH_THREE_PHENOMENA.tsv")
    source = read("THREE_HUNDRED_EIGHTY_SEVENTH_14_SOURCE_AUDIT.tsv")
    checks = {
        "fifteen_visible": len(forms) == 15,
        "fourteen_sources": len(source) == 14,
        "three_phenomena": {row["phenomenon"] for row in phenomena} == {"MARKED_CARRY", "OWNER_HANDOFF", "COMPONENT_ERROR"},
        "one_surface_repair": sum(row["surface_changed_by_corrector"] == "YES" for row in forms) == 1,
        "repair_at_position_twelve": {row["source_position"] for row in forms if row["surface_changed_by_corrector"] == "YES"} == {"12"},
        "endpoint_only": {row["fault_class"] for row in forms if row["surface_changed_by_corrector"] == "YES"} == {"ENDPOINT_DY_FOR_Y"},
        "carry_once": Counter(row["visibility_role"] for row in forms)["MARKED_ANTICIPATION"] == 1,
        "fourteen_contributions": sum(int(row["source_contribution"]) for row in forms) == 14,
        "one_source_change": sum(row["changed"] == "YES" for row in source) == 1,
        "identities_restored": all(row["corrected_identity_match"] == "YES" for row in source),
        "owner_partition": Counter(row["owner_code"] for row in source) == {"H4": 7, "B3": 7},
        "cycles_preserved": Counter(row["microcycle"] for row in source) == {"C1": 4, "C2": 3, "C3": 4, "C4": 3},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
