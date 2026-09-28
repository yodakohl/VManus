#!/usr/bin/env python3
"""Validate frozen pair table and independently audit paragraph metadata."""
import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def main():
    result = json.loads((OUT / "RESULT.json").read_text())
    with (OUT / "PAIRS.tsv").open(newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))
    assert len(rows) == 3 * result["pair_bases"]
    for r in rows:
        p, y = int(r["p_initial"]), int(r["y_initial"])
        ps, ys = int(r["p_paragraph_starts"]), int(r["y_paragraph_starts"])
        pf, yf = int(r["p_folios"]), int(r["y_folios"])
        assert 0 <= ps <= p and 0 <= ys <= y and pf <= p and yf <= y
        support = p >= 3 and y >= 3 and pf >= 2 and yf >= 2
        assert support == (r["supported"] == "1")
        direction = "NO_PAIR_IN_READER" if not p or not y else (
            "P_GREATER" if ps * y > ys * p else "Y_GREATER" if ps * y < ys * p else "EQUAL")
        assert direction == r["direction"]
    zl = [r for r in rows if r["edition"] == "ZL3b" and r["supported"] == "1"]
    it = [r for r in rows if r["edition"] == "IT2a" and r["supported"] == "1"]
    assert len(zl) == 7 and all(r["direction"] == "P_GREATER" for r in zl)
    assert len(it) == 8 and all(r["direction"] == "P_GREATER" for r in it)

    allow = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
    with allow.open(newline="") as file:
        pages = [r["page"] for r in csv.DictReader(file, delimiter="\t")]
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv",
           str(ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"),
           "--selector", "page", "--columns", "edition,kind,source_group_index,paragraph_start",
           "--forbid-prefix", "f84"]
    for p in pages:
        cmd.extend(["--allow", p])
    got = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    initials = [r for r in csv.DictReader(io.StringIO(got.stdout), delimiter="\t")
                if r["kind"] == "P" and r["source_group_index"] == "1"]
    counts = Counter((r["edition"], r["paragraph_start"]) for r in initials)
    assert counts[("RF1b", "1")] == 0 and counts[("RF1b", "0")] == 3768
    assert counts[("ZL3b", "1")] == 665 and counts[("IT2a", "1")] == 697
    validation = {"status":"PASS_DATA_AND_METADATA_DEFECT",
        "pair_rows":len(rows), "supported_zl":len(zl), "supported_it":len(it),
        "paragraph_initial_count_by_reader":{e:{v:counts[(e,v)] for v in ("0","1")}
                                          for e in ("ZL3b","IT2a","RF1b")},
        "decision":"Original all-reader direction gate cannot be scored: RF1b has no paragraph-start positives anywhere in admitted source metadata."}
    (OUT / "VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n")
    print(json.dumps(validation,indent=2))


if __name__ == "__main__":
    main()
