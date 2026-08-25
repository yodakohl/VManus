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
    lexicon = read("PASS983_159_TEACHING_UNIT_CODEBOOK.tsv")
    events = read("PASS983_2511_EVENT_ADDRESS_AWARE_BINDING.tsv")
    local = [r for r in events if r["primary_layer"] == "LOCAL_ADDRESS_OR_KENNING"]
    cheody = [r for r in local if r["physical_page"] == "f70v" and r["surface"] == "cheody"]
    checks = {
        "teaching_units_159": len(lexicon) == 159,
        "unit_ids_unique": len({r["teaching_unit_id"] for r in lexicon}) == 159,
        "x001_once": sum(r["teaching_unit_id"] == "X001" for r in lexicon) == 1,
        "events_2511": len(events) == 2511,
        "event_ids_unique": len({r["event_id"] for r in events}) == 2511,
        "local_addresses_485": len(local) == 485,
        "all_local_primary_x001": all(r["primary_teaching_unit_ids"] == "X001" for r in local),
        "all_local_keep_mnemonic": all(r["mnemonic_common_unit_ids"] for r in local),
        "cheody_two": len(cheody) == 2,
        "cheody_not_extract": all("AUSZUG" not in r["complete_working_reading_de"] for r in cheody),
        "all_have_reading": all(r["complete_working_reading_de"] for r in events),
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS983_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
