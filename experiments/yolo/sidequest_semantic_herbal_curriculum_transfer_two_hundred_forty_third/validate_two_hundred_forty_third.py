#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = rows("TWO_HUNDRED_FORTY_THIRD_100_EVENT_HERBAL_TRANSFER.tsv")
    cards = rows("TWO_HUNDRED_FORTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv")
    articles = rows("TWO_HUNDRED_FORTY_THIRD_FIVE_TRANSFERRED_ARTICLES.tsv")
    ec = Counter(r["curriculum_layer"] for r in events)
    cc = Counter(r["curriculum_layer"] for r in cards)
    checks = {
        "100_events": len(events) == 100,
        "100_unique_event_ids": len({r["event_id"] for r in events}) == 100,
        "66_cards": len(cards) == 66,
        "five_articles": len(articles) == 5,
        "event_split_44_28_28": ec == {"COMMON_BIOLOGICAL_HERBAL_CORE": 44, "HERBAL_LOCAL_NOUN_SIGN": 28, "HERBAL_LOCAL_OPERATION_SIGN": 28},
        "card_split_17_24_25": cc == {"COMMON_BIOLOGICAL_HERBAL_CORE": 17, "HERBAL_LOCAL_NOUN_SIGN": 24, "HERBAL_LOCAL_OPERATION_SIGN": 25},
        "all_cards_invariant": all(r["value_invariant"] == "YES" for r in cards),
        "all_defaults_concrete": all(r["concrete_default_de"].strip() for r in events),
        "four_pages": {r["page"] for r in events} == {"f10r", "f11r", "f55v", "f56r"},
        "no_sealed_pages": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
