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
    rows = read_tsv("PASS966_1078_SURFACE_DICTIONARY.tsv")
    bridges = read_tsv("PASS966_107_CROSS_LAYER_SURFACES.tsv")
    all_ids = [event_id for row in rows for event_id in row["event_ids"].split("|")]
    checks = {
        "surfaces_1078": len(rows) == 1078 and len({row["surface"] for row in rows}) == 1078,
        "events_2511": len(all_ids) == 2511 and len(set(all_ids)) == 2511,
        "zero_component_conflicts": not any(row["component_recipe"].startswith("CONFLICT:") for row in rows),
        "zero_meaning_conflicts": not any(row["portable_core_de"].startswith("CONFLICT:") for row in rows),
        "cross_layer_107": len(bridges) == 107,
        "cross_layer_events_814": sum(int(row["events"]) for row in bridges) == 814,
        "bridges_exact": {row["surface"] for row in bridges} == {row["surface"] for row in rows if row["cross_layer"] == "YES"},
        "no_empty_values": all(row["component_recipe"] and row["portable_core_de"] for row in rows),
        "no_sealed_pages": not any("f84" in row["physical_pages"].lower() for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS966_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
