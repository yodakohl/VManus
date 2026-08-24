#!/usr/bin/env python3
"""Validate the repaired five-article Herbal edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv")
    statements = read("THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv")
    articles = read("THREE_HUNDRED_THIRTIETH_FIVE_REPAIRED_ARTICLES.tsv")
    prose = " ".join(x["fluent_workshop_translation_de"] for x in statements).lower()
    checks = {
        "one_hundred_events": len(events) == 100 and len({x["event_id"] for x in events}) == 100,
        "nineteen_statements": len(statements) == 19 and len({x["statement_id"] for x in statements}) == 19,
        "five_articles": len(articles) == 5 and {x["record_unit_id"] for x in articles} == {"H1", "H2", "H3", "H4", "H5"},
        "article_counts_reconcile": sum(int(x["event_count"]) for x in articles) == 100 and sum(int(x["statement_count"]) for x in articles) == 19,
        "four_pages": {x["page"] for x in articles} == {"f10r", "f11r", "f55v", "f56r"},
        "all_translations_concrete": all(x["fluent_workshop_translation_de"] for x in statements),
        "all_owner_channels_explicit": all(x["visible_owner_added"] for x in statements),
        "no_superseded_story_terms": not any(term in prose for term in ["wein", "geschwür", "trank", "blütebeginn", "pflanzenspitzen", "grob zerreib", "gekühlt"]),
        "no_direct_bio_pointer": all(x["direct_bio_pointer"] == "NONE" for x in articles),
        "no_sealed_page": all("f84" not in x["page"].lower() for x in events) and all("f84" not in x["page"].lower() for x in articles),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_THIRTIETH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
