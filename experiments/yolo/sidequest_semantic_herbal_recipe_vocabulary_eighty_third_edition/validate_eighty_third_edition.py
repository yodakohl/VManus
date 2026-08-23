#!/usr/bin/env python3
"""Validate the concrete five-article recipe edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    vocab = read_tsv("EIGHTY_THIRD_21_MODEL_VOCABULARY_ROWS.tsv")
    comparisons = read_tsv("EIGHTY_THIRD_15_MODEL_ARTICLE_COMPARISONS.tsv")
    selected = read_tsv("EIGHTY_THIRD_11_SELECTED_RECIPE_WORDS.tsv")
    articles = read_tsv("EIGHTY_THIRD_5_COMPLETE_HERBAL_ARTICLES.tsv")
    bindings = read_tsv("EIGHTY_THIRD_100_HERBAL_RECIPE_BINDING.tsv")
    sources = read_tsv("EIGHTY_THIRD_6_HISTORICAL_RECIPE_ANALOGUES.tsv")
    checks = {
        "three_models_seven_core_words": len(vocab) == 21 and len({row["model_id"] for row in vocab}) == 3,
        "fifteen_comparisons": len(comparisons) == 15,
        "eleven_selected_words": len(selected) == 11 and len({row["recipe_slot"] for row in selected}) == 11,
        "five_articles": len(articles) == 5 and {row["unit_id"] for row in articles} == {"H1", "H2", "H3", "H4", "H5"},
        "article_group_sum_100": sum(int(row["group_count"]) for row in articles) == 100,
        "100_bindings": len(bindings) == 100 and len({row["source_group_identity"] for row in bindings}) == 100,
        "selected_model_consistent": all(row["selected_recipe_model"] == "M1_MEDICAL_MATERIA_RECIPE" for row in articles + bindings),
        "no_species_or_disease_invention": all(row["species_name"] == "UNNAMED" and row["disease_or_body_part"] == "UNSPECIFIED" for row in articles),
        "six_historical_analogues": len(sources) == 6,
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in articles + bindings),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
