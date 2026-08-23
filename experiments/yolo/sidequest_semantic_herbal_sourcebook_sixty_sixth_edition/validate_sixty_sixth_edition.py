#!/usr/bin/env python3
"""Validate the complete five-record Herbal sourcebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read_tsv("SIXTY_SIXTH_100_HERBAL_GROUP_EDITION.tsv")
    statements = read_tsv("SIXTY_SIXTH_19_HERBAL_STATEMENTS.tsv")
    articles = read_tsv("SIXTY_SIXTH_5_COMPACT_HERBAL_ARTICLES.tsv")
    checks = {
        "four_pages": {row["page"] for row in groups} == ALLOWED,
        "100_groups": len(groups) == 100 and len({row["source_group_id"] for row in groups}) == 100,
        "nineteen_statements": len(statements) == 19 and len({row["unit_id"] for row in statements}) == 19,
        "five_records": len(articles) == 5 and {row["record_id"] for row in articles} == {"H1", "H2", "H3", "H4", "H5"},
        "group_counts_reconcile": sum(int(row["group_count"]) for row in articles) == 100,
        "statement_counts_reconcile": sum(len(row["statement_ids"].split(",")) for row in articles) == 19,
        "all_articles_concrete": all(row["compact_article_de"] and row["concrete_content_wager"] and row["strongest_practical_rival"] for row in articles),
        "no_species_claim": all(row["species_identification"] == "NONE__VISIBLE_PLANT_OWNER_ONLY" for row in articles),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in groups + statements + articles),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
