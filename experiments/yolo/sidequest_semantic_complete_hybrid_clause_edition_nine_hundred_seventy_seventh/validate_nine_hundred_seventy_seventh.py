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
    rows = read("PASS977_354_COMPLETE_HYBRID_CLAUSES.tsv")
    addresses = read("PASS977_501_LOCAL_ADDRESS_HYBRID.tsv")
    prose_ids = [event for row in rows for event in row["event_ids"].split("|")]
    address_ids = [row["event_id"] for row in addresses]
    ids = prose_ids + address_ids
    anchor = next((row for row in rows if row["clause_id"] == "P915-C003"), None)
    checks = {
        "clauses_354": len(rows) == 354,
        "clause_ids_unique": len({r["clause_id"] for r in rows}) == 354,
        "prose_events_2010": len(prose_ids) == len(set(prose_ids)) == 2010,
        "local_address_events_501": len(address_ids) == len(set(address_ids)) == 501,
        "events_2511": len(ids) == 2511,
        "events_unique": len(set(ids)) == 2511,
        "prose_and_addresses_disjoint": not set(prose_ids) & set(address_ids),
        "pages_14": len({r["physical_page"] for r in rows} | {r["physical_page"] for r in addresses}) == 14,
        "specialist_uses_95": sum(int(r["specialist_event_count"]) for r in rows) == 95,
        "all_translated": all(r["continuous_working_translation_de"] for r in rows),
        "anchor_present": anchor is not None,
        "anchor_is_complete_recipe": anchor is not None and all(word in anchor["continuous_working_translation_de"] for word in ["Sudansatz", "auswringen", "Stehzeit", "nachseihen", "Klarlauf", "kalt stellen"]),
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS977_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
