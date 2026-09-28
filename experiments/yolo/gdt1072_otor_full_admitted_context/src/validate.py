#!/usr/bin/env python3
"""Independent aggregate check against the existing words profile."""
import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def main():
    result = json.loads((OUT / "RESULT.json").read_text())
    with (OUT / "EXACT_OCCURRENCES.tsv").open(newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))
    profile = json.loads(subprocess.check_output(
        [str(ROOT / "vmanus-work"), "words", "profile", "otor", "--json", "--limit", "1"],
        cwd=ROOT, text=True))["profiles"][0]["editions"]
    checks = []
    for edition in ("ZL3b", "IT2a", "RF1b"):
        p = profile[edition]
        corpus = [r for r in rows if r["edition"] == edition and r["cohort"] == "179_SELECTOR_CORPUS"]
        special = [r for r in rows if r["edition"] == edition and r["cohort"] == "F68R1_TWO_LOCI"]
        assert len(corpus) == p["count"] == result["exact_counts"][edition]["corpus"]
        assert len({r["page"] for r in corpus}) == p["pages_with_form"]
        assert Counter(r["section"] for r in corpus) == Counter(
            {v["value"]: v["count"] for v in p["strata"]["section"] if v["count"]})
        assert Counter(r["kind"] for r in corpus) == Counter(
            {v["value"]: v["count"] for v in p["strata"]["kind"] if v["count"]})
        assert len(special) == {"ZL3b": 2, "IT2a": 2, "RF1b": 1}[edition]
        checks.append(f"{edition}_profile_count_section_kind_pages")
    assert all(r["ivtff_group_raw"] == "otor" for r in rows)
    assert not any(r["page"].startswith("f84") for r in rows)
    assert all(r["cohort"] != "F68R1_TWO_LOCI" or r["locus"] in {"f68r1.1", "f68r1.26"} for r in rows)
    seen = defaultdict(set)
    for r in rows:
        seen[r["locus"]].add(r["edition"])
    validation = {"status": "PASS", "checks": checks,
                  "total_rows": len(rows), "distinct_loci": len(seen),
                  "all_three_reader_loci": sum(len(v) == 3 for v in seen.values()),
                  "two_reader_loci": sum(len(v) == 2 for v in seen.values()),
                  "one_reader_loci": sum(len(v) == 1 for v in seen.values()),
                  "special": {k: sorted(v) for k, v in seen.items() if k.startswith("f68r1.")}}
    (OUT / "VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
