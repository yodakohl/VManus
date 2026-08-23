#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_NINTH_FIVE_HERBAL_OWNERS.tsv", "TWO_HUNDRED_NINTH_28_HERBAL_NOUN_CARDS.tsv", "TWO_HUNDRED_NINTH_100_EVENT_OWNER_NOUN_EDITION.tsv", "TWO_HUNDRED_NINTH_FIVE_CONTINUOUS_HERBAL_ARTICLES.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    owners = read("TWO_HUNDRED_NINTH_FIVE_HERBAL_OWNERS.tsv")
    nouns = read("TWO_HUNDRED_NINTH_28_HERBAL_NOUN_CARDS.tsv")
    events = read("TWO_HUNDRED_NINTH_100_EVENT_OWNER_NOUN_EDITION.tsv")
    articles = read("TWO_HUNDRED_NINTH_FIVE_CONTINUOUS_HERBAL_ARTICLES.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "five_owner_records": len(owners) == 5 and {row["record_unit_id"] for row in owners} == {"H1", "H2", "H3", "H4", "H5"},
        "four_visible_plants": summary["unique_visible_plants"] == 4 and next(row for row in owners if row["record_unit_id"] == "H1")["visible_owner_id"] == next(row for row in owners if row["record_unit_id"] == "H2")["visible_owner_id"],
        "28_noun_cards": len(nouns) == 28 and len({row["master_card_id"] for row in nouns}) == 28,
        "two_direct_visible_nouns": summary["grounding_counts"]["DIRECT_VISIBLE"] == 2,
        "100_events": len(events) == 100 and len({row["event_id"] for row in events}) == 100,
        "19_statements": summary["statements"] == 19,
        "five_articles": len(articles) == 5,
        "owners_on_every_event": all(row["silent_owner_id"] and row["silent_owner_id"] != "NONE" for row in events),
        "no_herbal_freshwater_card": summary["herbal_freshwater_cards"] == 0,
        "unsupported_nouns_explicit": all("Pflanzenart" in row["intentionally_unassigned_nouns"] and "Wein" in row["intentionally_unassigned_nouns"] for row in articles),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_absent": not any("f84" in value.lower() for rows in (owners, nouns, events, articles) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_ninth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
