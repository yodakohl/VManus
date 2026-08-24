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
    trace = read("FOUR_HUNDRED_NINETY_THIRD_NINE_EVENT_RECHARGE_TRACE.tsv")
    allo = read("FOUR_HUNDRED_NINETY_THIRD_CHO_SHO_INGREDIENT_ALLOGRAPHS.tsv")
    objects = read("FOUR_HUNDRED_NINETY_THIRD_SEVEN_RECHARGE_OBJECTS.tsv")
    candidates = read("FOUR_HUNDRED_NINETY_THIRD_THREE_H5_MACRO_READINGS.tsv")
    comparison = read("FOUR_HUNDRED_NINETY_THIRD_THREE_HERBAL_MACRO_COMPARISON.tsv")
    manual = read("FOUR_HUNDRED_NINETY_THIRD_169_ITEM_FIVE_MACRO_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_NINETY_THIRD_776_FIVE_MACRO_LEDGER.tsv")
    checks = {
        "trace_9": len(trace) == 9,
        "event_ids_exact": [r["event_id"] for r in trace] == [f"E{i:03d}" for i in range(74, 83)],
        "three_phases": len({r["macro_phase"] for r in trace}) == 3,
        "ingredient_allographs_2": len(allo) == 2,
        "cho_sho_exact": {r["surface"] for r in allo} == {"cho", "sho"},
        "same_exact_card": all(r["same_exact_card"] == "YES" for r in allo),
        "objects_7": len(objects) == 7,
        "comparison_5": len(comparison) == 5,
        "one_selected": sum(r["decision"] == "SELECT" for r in candidates) == 1,
        "manual_169": len(manual) == 169,
        "ledger_776": len(ledger) == 776,
        "five_macro_events_58": sum(r["local_macro"] != "NONE" for r in ledger) == 58,
        "h5_macro_9": sum(r["local_macro"].startswith("PFLANZENZUSATZ") for r in ledger) == 9,
        "fixed_page": {r["page"] for r in ledger if r["local_macro"].startswith("PFLANZENZUSATZ")} == {"f56r"},
        "sealed_pages_absent": not any("f84" in str(v).lower() for r in trace + ledger for v in r.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_NINETY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
