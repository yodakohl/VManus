#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ledger = read("TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv")
    lessons = read("TWO_HUNDRED_NINETIETH_EIGHT_LESSON_CURRICULUM.tsv")
    inventory = read("TWO_HUNDRED_NINETIETH_WORKSHOP_INVENTORY.tsv")
    counts = Counter(r["writing_layer"] for r in ledger)
    checks = {
        "ledger_776": len(ledger) == 776,
        "prose_381_astro_395": Counter(r["register"] for r in ledger) == Counter({"PROSE": 381, "ASTRO": 395}),
        "indices_1_776": [int(r["unified_index"]) for r in ledger] == list(range(1, 777)),
        "layer_counts_exact": counts == Counter({"PURE_COMPOSITION": 617, "LEARNED_WHOLE_SIGN": 79, "FRAMED_WHOLE_EXCEPTION": 1, "LOCAL_COPY_KEY": 79}),
        "all_results_exact": all(r["result_status"] == "GENERATED_OR_COPIED_EXACTLY" for r in ledger),
        "all_surfaces_present": all(r["resulting_visible_surface"].strip() for r in ledger),
        "lessons_8": len(lessons) == 8,
        "lesson_order": [int(r["lesson"]) for r in lessons] == list(range(1, 9)),
        "memorized_105": next(int(r["entry_count"]) for r in inventory if r["inventory_layer"] == "TOTAL_MEMORIZED_ENTRIES") == 105,
        "local_forms_67": next(int(r["entry_count"]) for r in inventory if r["inventory_layer"] == "LOCAL_DIAGRAM_KEYS") == 67,
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in ledger + lessons + inventory),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
