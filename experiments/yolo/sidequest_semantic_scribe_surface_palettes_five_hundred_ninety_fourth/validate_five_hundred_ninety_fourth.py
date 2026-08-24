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
    cards = read("FIVE_HUNDRED_NINETY_FOURTH_173_CARD_SURFACE_STATUS.tsv")
    surfaces = read("FIVE_HUNDRED_NINETY_FOURTH_230_SURFACE_PALETTE.tsv")
    palettes = read("FIVE_HUNDRED_NINETY_FOURTH_34_MULTISURFACE_CARDS.tsv")
    hypotheses = read("FIVE_HUNDRED_NINETY_FOURTH_FIVE_SURFACE_HYPOTHESES.tsv")
    classes = Counter(row["surface_class"] for row in cards)
    checks = {
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "events381": sum(int(row["occurrences"]) for row in cards) == 381,
        "surfaces230": len(surfaces) == 230 and len({row["surface"] for row in surfaces}) == 230,
        "surface_events381": sum(int(row["events"]) for row in surfaces) == 381,
        "palettes34": len(palettes) == 34 and all(int(row["surface_count"]) > 1 for row in palettes),
        "palette_surfaces91": sum(int(row["surface_count"]) for row in palettes) == 91,
        "palette_events202": sum(int(row["occurrences"]) for row in palettes) == 202,
        "within19": classes["MULTISURFACE_WITHIN_PAGE_PALETTE"] == 19,
        "cross15": classes["MULTISURFACE_CROSS_PAGE_PALETTE"] == 15,
        "fixed17": classes["FIXED_RECURRENT_FORM"] == 17,
        "oneoff122": classes["ONE_OFF_EXEMPLAR_FORM"] == 122,
        "same_position32": sum(row["multiple_surfaces_at_same_statement_position"] == "YES" for row in palettes) == 32,
        "same_meaning": all(row["semantic_difference_between_surfaces"] == "NONE" for row in cards) and all(row["meaning_change"] == "NONE" for row in surfaces),
        "hypotheses5": len(hypotheses) == 5,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
