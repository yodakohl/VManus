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
    units = read("FIVE_HUNDRED_FORTY_EIGHTH_IDIOMATIC_UNITS.tsv")
    sentences = read("FIVE_HUNDRED_FORTY_EIGHTH_NINETY_SEVEN_FORMULA_SENTENCES.tsv")
    articles = read("FIVE_HUNDRED_FORTY_EIGHTH_ELEVEN_FORMULA_ARTICLES.tsv")
    targets = read("FIVE_HUNDRED_FORTY_EIGHTH_AWKWARD_CARD_TARGETS.tsv")
    source_ids = [item for row in units for item in row["source_position_ids"].split("|")]
    visible_ids = [item for row in units for item in row["visible_event_ids"].split("|")]
    checks = {
        "units_nonempty": len(units) > 0 and all(row["idiomatic_unit_de"] for row in units),
        "sentences97": len(sentences) == 97 and len({row["instruction_id"] for row in sentences}) == 97,
        "articles11": len(articles) == 11 and len({row["record"] for row in articles}) == 11,
        "source_positions380": len(source_ids) == 380 and len(set(source_ids)) == 380,
        "visible_events381": len(visible_ids) == 381 and len(set(visible_ids)) == 381,
        "formula_ids15": len({row["unit_id"] for row in units if row["unit_type"] != "SINGLE_CARD"}) == 15,
        "formula_applications28": sum(row["unit_type"] != "SINGLE_CARD" for row in units) == 28,
        "instruction_partition": Counter(row["record"] for row in sentences) == Counter({row["record"]: int(row["instruction_count"]) for row in articles}),
        "article_events381": sum(int(row["visible_event_count"]) for row in articles) == 381,
        "record_ends8_3": Counter(row["record_final_status"] for row in articles) == Counter({"RECORD_FINAL_OPEN": 8, "COMMITTED_CLOSE": 3}),
        "components_unchanged": all(row["component_values_unchanged"] == "YES" for row in units + sentences),
        "targets_ranked": all(int(row["rank"]) == index for index, row in enumerate(targets, 1)),
        "fixed_pages_only": {row["page"] for row in sentences} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in sentences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
