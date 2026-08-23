#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("TWO_HUNDRED_EIGHTY_SECOND_19_MANUAL_HERBAL_TRANSLATIONS.tsv")
    articles = read("TWO_HUNDRED_EIGHTY_SECOND_FIVE_HERBAL_ARTICLES.tsv")
    checks = {
        "19_statements": len(rows) == 19,
        "five_articles": len(articles) == 5,
        "record_counts": Counter(r["record_unit_id"] for r in rows) == {"H1": 2, "H2": 3, "H3": 4, "H4": 4, "H5": 6},
        "article_statement_sum": sum(int(r["statement_count"]) for r in articles) == 19,
        "statement_ids_unique": len({r["statement_id"] for r in rows}) == 19,
        "family_sequences_nonempty": all(r["family_sequence_de"].strip() for r in rows),
        "manual_translations_nonempty": all(r["manual_fluent_translation_de"].strip() for r in rows),
        "continuous_articles_nonempty": all(r["continuous_article_de"].strip() for r in articles),
        "water_localized_to_h1": sum("Wasser" in r["manual_fluent_translation_de"] for r in rows) == 1 and next(r for r in rows if "Wasser" in r["manual_fluent_translation_de"])["statement_id"] == "H1-S001",
        "only_herbal_pages": {r["page"] for r in rows} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
