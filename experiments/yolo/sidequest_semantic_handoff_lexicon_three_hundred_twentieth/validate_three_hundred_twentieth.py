#!/usr/bin/env python3
"""Validate Pass 320 shared-card handoff lexicon."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    words = read("THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv")
    events = read("THREE_HUNDRED_TWENTIETH_136_SHARED_WORD_EVENTS.tsv")
    anchors = read("THREE_HUNDRED_TWENTIETH_FIVE_HANDOFF_ANCHORS.tsv")
    counts = Counter(x["handoff_word_id"] for x in events)
    checks = {
        "seventeen_words": len(words) == 17,
        "seventeen_unique_joint_ids": len({x["joint_tuple_id"] for x in words}) == 17,
        "one_hundred_thirty_six_events": len(events) == 136,
        "event_ids_unique": len({x["event_id"] for x in events}) == 136,
        "all_words_cross_sections": all(int(x["herbal_events"]) > 0 and int(x["bio_events"]) > 0 for x in words),
        "counts_reconcile": all(counts[x["handoff_word_id"]] == int(x["total_events"]) for x in words),
        "same_meaning_per_word": all(len({e["handoff_atomic_value_de"] for e in events if e["handoff_word_id"] == x["handoff_word_id"]}) == 1 for x in words),
        "atomic_values_are_one_words": all(" " not in x["handoff_atomic_value_de"] and "/" not in x["handoff_atomic_value_de"] for x in words),
        "five_handoffs_covered": {x["herbal_record"] for x in anchors} == {"H1", "H2", "H3", "H4", "H5"},
        "seven_exact_anchors": len(anchors) == 7,
        "all_exact_identity_bridges": all(x["exact_identity_bridge"] == "YES" for x in anchors),
        "no_sealed_page": all("f84" not in "\t".join(x.values()).lower() for rows in [words, events, anchors] for x in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTIETH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
