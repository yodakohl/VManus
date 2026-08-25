#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "sidequest_semantic_revised_six_order_book_eight_hundred_eighty_sixth"
PREFIX = "EIGHT_HUNDRED_EIGHTY_EIGHTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source_marks = read(BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_437_MARK_REVISED_SIX_ORDER_BOOK.tsv")
    source_units = read(BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_118_UNIT_REVISED_SIX_ORDER_BOOK.tsv")
    marks = read(HERE / f"{PREFIX}_437_MARK_MASTER_BINDING.tsv")
    units = read(HERE / f"{PREFIX}_118_READABLE_UNITS.tsv")
    stations = read(HERE / f"{PREFIX}_16_VISIBLE_STATION_BLOCKS.tsv")
    orders = read(HERE / f"{PREFIX}_6_MASTER_ORDER_CARDS.tsv")
    payloads = read(HERE / f"{PREFIX}_30_FILLED_PAYLOADS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    edition = (HERE / f"{PREFIX}_SIX_MASTER_ORDER_CARDS.md").read_text(encoding="utf-8")

    mark_projection = [{key: row[key] for key in source_marks[0]} for row in marks]
    unit_projection = [{key: row[key] for key in source_units[0]} for row in units]
    section_counts = Counter(row["master_section"] for row in marks)
    station_marks = sum(int(row["marks"]) for row in stations)
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "orders_6": len(orders) == 6,
        "marks_437": len(marks) == 437,
        "marks_exact_projection": mark_projection == source_marks,
        "units_118": len(units) == 118,
        "units_exact_projection": unit_projection == source_units,
        "sections_exact": section_counts == {"WHAT": 83, "HOW": 281, "WHEN": 73},
        "station_blocks_16": len(stations) == 16,
        "station_marks_281": station_marks == 281,
        "owner_switches_10": summary["owner_switches"] == 10,
        "station_ids_unique": len({row["station_block"] for row in stations}) == 16,
        "station_mark_ranges": all(row["first_mark"] and row["last_mark"] for row in stations),
        "each_order_has_when": all(row["when_de"] for row in orders),
        "each_order_has_title": all(row["title_de"] for row in orders),
        "each_order_in_edition": all(f"## {row['order_id']}:" in edition for row in orders),
        "every_unit_in_edition": all(f"`{row['unit']}`" in edition for row in units),
        "owner_traces_present": all(row["owner_trace_de"] for row in units),
        "payloads_30": len(payloads) == 30 and all(row["empty"] == "NO" for row in payloads),
        "dictionary_unchanged": all(row["dictionary_changed"] == "NO" for row in units) and all(row["dictionary_changes"] == "0" for row in orders),
        "no_empty_mark_default": all(row["concrete_default_de"] for row in marks),
        "ten_pages": len({row["page"] for row in marks}) == 10,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"] and not any(row["page"].startswith("f84") for row in marks),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
