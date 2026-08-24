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
    rows = read("FIVE_HUNDRED_FORTY_SECOND_TWELVE_DUAL_PURPOSE_EXPANSIONS.tsv")
    insertions = read("FIVE_HUNDRED_FORTY_SECOND_FORTY_TWO_SILENT_INSERTIONS.tsv")
    summary = read("FIVE_HUNDRED_FORTY_SECOND_PURPOSE_COST_SUMMARY.tsv")
    total = next(row for row in summary if row["scope"] == "TOTAL")
    checks = {
        "samples12": len(rows) == 12 and [row["sample_id"] for row in rows] == [f"X{i:02d}" for i in range(1, 13)],
        "sections4_8": Counter(row["section"] for row in rows) == Counter({"HERBAL": 4, "BIOLOGICAL": 8}),
        "insertions42": len(insertions) == 42,
        "medical23_technical19": (total["medical_insertions"], total["technical_insertions"]) == ("23", "19"),
        "wins1_5_ties6": (total["medical_local_wins"], total["technical_local_wins"], total["ties"]) == ("1", "5", "6"),
        "herbal_tie": next(row for row in summary if row["scope"] == "HERBAL")["selected_purpose"] == "TIE",
        "bio_technical": next(row for row in summary if row["scope"] == "BIOLOGICAL")["selected_purpose"] == "TECHNICAL",
        "all_full_expansions": all(row["medical_expansion_de"] and row["technical_expansion_de"] for row in rows),
        "cards_unchanged": all(row["card_meanings_changed"] == "NO" for row in rows),
        "no_sealed_tokens": all("f84" not in "\t".join(row.values()).lower() for row in [*rows, *insertions, *summary]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
