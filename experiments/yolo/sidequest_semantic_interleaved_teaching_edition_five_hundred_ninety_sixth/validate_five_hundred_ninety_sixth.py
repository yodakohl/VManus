#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    statements = read("FIVE_HUNDRED_NINETY_SIXTH_116_FOUR_LINE_STATEMENTS.tsv")
    records = read("FIVE_HUNDRED_NINETY_SIXTH_11_RECORD_COPY_SHEETS.tsv")
    astro = read("FIVE_HUNDRED_NINETY_SIXTH_142_ASTRO_COPY_LINES.tsv")
    unified = read("FIVE_HUNDRED_NINETY_SIXTH_776_FACSIMILE_COPY_TRACE.tsv")
    checks = {
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "prose_events381": sum(int(row["event_count"]) for row in statements) == 381,
        "records11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116 and sum(int(row["events"]) for row in records) == 381,
        "statement_lines_complete": all(row["meaning_line_de"] and row["spoken_component_line_de"] and row["card_identity_line"] and row["exact_surface_line"] and row["scribe_recitation_line"] for row in statements),
        "all_bound": all(row["all_events_bound"] == "YES" for row in statements),
        "astro142": len(astro) == 142 and len({row["locus"] for row in astro}) == 142,
        "astro_no_prose": all(row["prose_value_import"] == "NONE" for row in astro),
        "unified776": len(unified) == 776 and [int(row["unified_serial"]) for row in unified] == list(range(1, 777)),
        "section_counts": Counter(row["section"] for row in unified) == Counter({"HERBAL": 100, "BIOLOGICAL": 281, "ASTRO": 395}),
        "surface_complete": all(row["surface_display_only"] and row["read_aloud_de"] and row["copy_rule_de"] and row["meaning_or_use_de"] for row in unified),
        "pages10": len({row["page"] for row in unified}) == 10,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
