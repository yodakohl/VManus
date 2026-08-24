#!/usr/bin/env python3
"""Validate shared handoff syntax inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ngrams = read("THREE_HUNDRED_TWENTY_THIRD_ALL_SHARED_NGRAMS.tsv")
    profiles = read("THREE_HUNDRED_TWENTY_THIRD_17_POSITION_PROFILES.tsv")
    rules = read("THREE_HUNDRED_TWENTY_THIRD_SEVEN_WRITING_RULES.tsv")
    direct2 = [x for x in ngrams if x["mode"] == "DIRECT_BIGRAM"]
    direct3 = [x for x in ngrams if x["mode"] == "DIRECT_TRIGRAM"]
    checks = {
        "seventeen_profiles": len(profiles) == 17,
        "one_hundred_thirty_six_profile_events": sum(int(x["events"]) for x in profiles) == 136,
        "forty_nine_direct_bigrams": sum(int(x["count"]) for x in direct2) == 49,
        "thirteen_direct_trigrams": sum(int(x["count"]) for x in direct3) == 13,
        "nine_recurrent_direct_bigrams": sum(x["recurrent"] == "YES" for x in direct2) == 9,
        "one_recurrent_direct_trigram": sum(x["recurrent"] == "YES" for x in direct3) == 1,
        "seven_rules": len(rules) == 7,
        "measure_frame_present": any(x["sequence"] == "Diesposten → Sollmaß → Diesposten" and x["count"] == "2" for x in direct3),
        "all_words_have_rules": all(x["apprentice_rule"] for x in profiles),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [ngrams, profiles, rules] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
