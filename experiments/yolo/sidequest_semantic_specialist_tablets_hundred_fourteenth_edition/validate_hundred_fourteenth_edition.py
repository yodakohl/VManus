#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_FOURTEENTH_46_SPECIALIST_CARD_ASSIGNMENTS.tsv")
    tablets = rows("HUNDRED_FOURTEENTH_FIVE_SPECIALIST_TABLETS.tsv")
    counts = {r["tablet_id"]: int(r["card_count"]) for r in tablets}
    checks = {
        "cards_46": len(cards) == 46,
        "tablets_5": len(tablets) == 5,
        "unique_cards": len({r["master_card_id"] for r in cards}) == 46,
        "one_tablet_each": all(r["tablet_id"] in counts for r in cards),
        "counts_12_11_11_9_3": sorted(counts.values()) == [3, 9, 11, 11, 12],
        "events_bound": all(len(r["event_serials"].split("|")) == int(r["event_count"]) for r in cards),
        "no_empty_defaults": all(r["short_default_de"] for r in cards),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
