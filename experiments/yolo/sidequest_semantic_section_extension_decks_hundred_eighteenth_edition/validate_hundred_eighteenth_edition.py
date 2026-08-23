#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    membership = rows("HUNDRED_EIGHTEENTH_173_SECTION_MEMBERSHIP.tsv")
    herbal = rows("HUNDRED_EIGHTEENTH_66_CARD_HERBAL_DECK.tsv")
    bio = rows("HUNDRED_EIGHTEENTH_124_CARD_BIOLOGICAL_DECK.tsv")
    lessons = rows("HUNDRED_EIGHTEENTH_ELEVEN_INCREMENTAL_RECORD_LESSONS.tsv")
    checks = {
        "membership_173": len(membership) == 173,
        "shared_17": sum(r["section_deck_status"] == "SHARED_17" for r in membership) == 17,
        "herbal_extension_49": sum(r["section_deck_status"] == "HERBAL_EXTENSION_49" for r in membership) == 49,
        "bio_extension_107": sum(r["section_deck_status"] == "BIOLOGICAL_EXTENSION_107" for r in membership) == 107,
        "herbal_deck_66": len(herbal) == 66,
        "bio_deck_124": len(bio) == 124,
        "lessons_11": len(lessons) == 11,
        "herbal_events_100": sum(int(r["herbal_event_count"]) for r in herbal) == 100,
        "bio_events_281": sum(int(r["biological_event_count"]) for r in bio) == 281,
        "union_173": len({r["master_card_id"] for r in herbal} | {r["master_card_id"] for r in bio}) == 173,
        "intersection_17": len({r["master_card_id"] for r in herbal} & {r["master_card_id"] for r in bio}) == 17,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in membership),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
