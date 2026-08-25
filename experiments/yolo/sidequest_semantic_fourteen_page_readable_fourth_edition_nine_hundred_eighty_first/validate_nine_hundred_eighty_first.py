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
    rows = read("PASS981_FOURTEEN_PAGE_READABLE_EDITION.tsv")
    stages = {stage: sum(r["book_stage"] == stage for r in rows) for stage in {r["book_stage"] for r in rows}}
    text = (HERE / "PASS981_COMPLETE_READABLE_FOURTH_EDITION.md").read_text(encoding="utf-8")
    checks = {
        "pages_14": len(rows) == 14,
        "page_ids_unique": len({r["physical_page"] for r in rows}) == 14,
        "events_2511": sum(int(r["events"]) for r in rows) == 2511,
        "stage_shape_5_1_4_4": sorted(stages.values()) == [1, 4, 4, 5],
        "all_translated": all(len(r["complete_working_translation_de"].split()) >= 20 for r in rows),
        "all_have_layer_counts": all(r["primary_layer_counts"] for r in rows),
        "anchor_present": all(word in text for word in ["Blütenkraut", "Sudansatz", "auswringen", "Stehzeit", "nachseihen", "Klarlauf", "kalt stellen"]),
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS981_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
