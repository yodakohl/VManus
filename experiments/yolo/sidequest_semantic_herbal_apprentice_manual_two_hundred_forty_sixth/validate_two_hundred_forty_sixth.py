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
    events = rows("TWO_HUNDRED_FORTY_SIXTH_FINAL_100_EVENT_HERBAL_MANUAL.tsv")
    cards = rows("TWO_HUNDRED_FORTY_SIXTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv")
    additions = rows("TWO_HUNDRED_FORTY_SIXTH_22_ADDITIONAL_CORES.tsv")
    articles = rows("TWO_HUNDRED_FORTY_SIXTH_FIVE_COMPLETE_ARTICLES.tsv")
    counts = Counter(r["composition_status"] for r in events)
    checks = {
        "100_events": len(events) == 100,
        "66_cards": len(cards) == 66,
        "five_articles": len(articles) == 5,
        "22_additional_cores": len(additions) == 22,
        "13_noun_cores": sum(r["lesson"] == "HERBAL_NOUN_CORE" for r in additions) == 13,
        "nine_operation_cores": sum(r["lesson"] == "HERBAL_OPERATION_CORE" for r in additions) == 9,
        "event_split_44_27_12_17": counts == {"KNOWN_FROM_BIOLOGICAL": 44, "FULL_COMPOSITION": 27, "PARTIAL_COMPOSITION": 12, "LEARNED_WHOLE_NOUN": 11, "LEARNED_WHOLE_OPERATION": 6},
        "all_defaults_concrete": all(r["concrete_default_de"].strip() for r in events),
        "event_ids_unique": len({r["event_id"] for r in events}) == 100,
        "fixed_pages_only": {r["page"] for r in events} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
