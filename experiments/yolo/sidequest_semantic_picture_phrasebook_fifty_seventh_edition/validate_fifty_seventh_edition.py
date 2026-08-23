#!/usr/bin/env python3
"""Validate the picture/exemplar phrasebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    owners = rows("FIFTY_SEVENTH_17_VISIBLE_OWNER_PHRASES.tsv")
    conventions = rows("FIFTY_SEVENTH_20_CONTENT_CONVENTIONS.tsv")
    sentences = rows("FIFTY_SEVENTH_116_ANNOTATED_SENTENCES.tsv")
    checks = {
        "seventeen_owner_phrases": len(owners) == 17 and len({row["exact_visible_owner_de"] for row in owners}) == 17,
        "twenty_content_conventions": len(conventions) == 20 and len({row["phrase_id"] for row in conventions}) == 20,
        "all_116_sentences": len(sentences) == 116 and len({row["unit_id"] for row in sentences}) == 116,
        "all_content_conventions_used": all(int(row["statement_count"]) > 0 for row in conventions),
        "counts_match_ids": all(int(row["statement_count"]) == len(row["statement_ids"].split("|")) for row in conventions),
        "sentence_tags_match_counts": all((row["content_phrase_ids"] == "NONE" and int(row["silent_phrase_count"]) == 0) or len(row["content_phrase_ids"].split("|")) == int(row["silent_phrase_count"]) for row in sentences),
        "no_owner_called_card": all("Kartenwerte unverändert" in row["teaching_rule_de"] for row in owners),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in owners + conventions + sentences),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
