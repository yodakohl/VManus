#!/usr/bin/env python3
"""Independent artifact arithmetic/coverage check for GDT1080."""

import csv
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"


def main() -> None:
    result = json.loads((OUT / "RESULT.json").read_text(encoding="utf-8"))
    with (OUT / "PAGE_COUNTS.tsv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == 96
    assert {r["reader"] for r in rows} == {"ZL3b", "IT2a", "RF1b"}
    assert {r["page"] for r in rows if r["reader"] == "ZL3b"} == {
        r["page"] for r in rows if r["reader"] == "IT2a"} == {
        r["page"] for r in rows if r["reader"] == "RF1b"}
    assert all(not r["page"].startswith("f84") for r in rows)
    for r in rows:
        for k in ("groups", "chor", "shor"):
            r[k] = int(r[k])
        assert r["groups"] >= r["chor"] + r["shor"]
    for a in result["aggregates"]:
        selected = [r for r in rows if r["reader"] == a["reader"] and r["state"] == a["state"]]
        assert len(selected) == a["pages"]
        sums = Counter()
        for r in selected:
            for k in ("groups", "chor", "shor"):
                sums[k] += r[k]
        for k in ("groups", "chor", "shor"):
            assert sums[k] == a[k]
        assert math.isclose(1000*sums["chor"]/sums["groups"], a["chor_per_1000"])
        assert math.isclose(1000*sums["shor"]/sums["groups"], a["shor_per_1000"])
    for reader, d in result["readers"].items():
        f, b = d["counts_F"], d["counts_B"]
        odd = (f["chor"]+.5)*(b["shor"]+.5)/((f["shor"]+.5)*(b["chor"]+.5))
        assert math.isclose(odd, d["cross_class_or"])
        pair_logsum = sum(math.log(p["cross_class_or"]) for p in result["pairs"] if p["reader"] == reader)
        assert math.isclose(pair_logsum, d["pair_log_or_sum"])
    assert result["excluded_panel_pages"] == ["f54r", "f90v2"]
    assert result["working_preference"] == "TIED"
    checks = {"status": "PASS", "page_reader_rows": 96,
              "checks": ["coverage", "alternate_readers", "class_sums", "odds_arithmetic",
                         "paired_folios", "sealed_f84", "frozen_tie_decision"]}
    (OUT / "VALIDATION.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print("PASS: 96 page-reader rows, frozen gates, arithmetic and seal")


if __name__ == "__main__":
    main()
