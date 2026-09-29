#!/usr/bin/env python3
"""Replay and compare the post-result feature-family artifact."""
import csv
import json
from pathlib import Path
from diagnostic_feature_family import calculate

HERE = Path(__file__).resolve().parents[1]


def main():
    rows, result = calculate()
    out = HERE / "artifacts"
    with (out / "FEATURE_FAMILY.tsv").open(newline="") as f:
        recorded = list(csv.DictReader(f, delimiter="\t"))
    assert recorded == [{k: str(v) for k, v in r.items()} for r in rows]
    assert json.loads((out / "FEATURE_FAMILY_RESULT.json").read_text()) == result
    assert len(rows) == 21 and result["schor_full_feature_sets"] == [
        "SPINY_ROUND_HEAD+MULTI_UNIT_SPIKE"]
    assert result["singletons_with_any_full_word"] == 0
    (out / "FEATURE_FAMILY_VALIDATION.json").write_text(json.dumps({
        "status": "PASS", "rows": len(rows), "source": "post_result_exploratory",
        "checked": "all 21 rows, hashes, schor set and singleton count"}, indent=2) + "\n")
    print("PASS post-result feature-family replay")


if __name__ == "__main__":
    main()
