#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    sentences = read("FIVE_HUNDRED_FORTY_SIXTH_NINETY_SEVEN_ANAPHORIC_SENTENCES.tsv")
    articles = read("FIVE_HUNDRED_FORTY_SIXTH_ELEVEN_CONTINUOUS_RECORD_ARTICLES.tsv")
    checks = {
        "sentences97": len(sentences) == 97 and len({row["instruction_id"] for row in sentences}) == 97,
        "articles11": len(articles) == 11 and [row["record"] for row in articles] == ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"],
        "instruction_partition": Counter(row["record"] for row in sentences) == Counter({row["record"]: int(row["instruction_count"]) for row in articles}),
        "event_partition381": sum(int(row["visible_event_count"]) for row in articles) == 381 and len({event for row in articles for event in row["visible_event_ids"].split("|")}) == 381,
        "record_ends8_3": Counter(row["record_final_status"] for row in articles) == Counter({"RECORD_FINAL_OPEN": 8, "COMMITTED_CLOSE": 3}),
        "all_articles_complete": all(row["continuous_article_de"] and row["introduction_de"] for row in articles),
        "all_sentences_complete": all(row["anaphoric_sentence_de"].endswith(".") for row in sentences),
        "components_unchanged": all(row["component_values_unchanged"] == "YES" for row in sentences) and all(row["all_component_values_unchanged"] == "YES" for row in articles),
        "fixed_pages_only": {row["page"] for row in articles} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in articles),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
