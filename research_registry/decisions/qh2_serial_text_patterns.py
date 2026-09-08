#!/usr/bin/env python3
"""Guarded census of literal serial text patterns in the admitted 179 selectors."""
import csv, io, json, subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
COLUMNS = "source_group_id,edition,locus,page,section,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw"
EDS = ("ZL3b", "IT2a", "RF1b")

def load():
    pages = [r["page"] for r in csv.DictReader(ALLOW.open(), delimiter="\t")]
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", SOURCE, "--selector", "page"]
    for page in pages:
        cmd += ["--allow", page]
    cmd += ["--columns", COLUMNS, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    p = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    return list(csv.DictReader(io.StringIO(p.stdout), delimiter="\t")), p.stderr

def main():
    rows, guard = load()
    by = {e: defaultdict(list) for e in EDS}
    for row in rows:
        by[row["edition"]][row["locus"]].append(row)
    for e in EDS:
        for locus in by[e]:
            by[e][locus].sort(key=lambda r: int(r["source_group_index"]))
    out = {"selected_rows": len(rows), "guard_stats": guard.strip(), "patterns": []}
    def window(e, locus, start, n):
        seq = [r for r in by[e].get(locus, []) if start <= int(r["source_group_index"]) < start + n]
        if len(seq) != n or [int(r["source_group_index"]) for r in seq] != list(range(start, start + n)):
            return None
        if any(r["right_separator"] != "DEFINITE_SPACE" for r in seq[:-1]):
            return None
        return seq
    predicates = {
        "ABA": lambda s: s[0] == s[2] and s[0] != s[1],
        "ABAB": lambda s: s[0] == s[2] and s[1] == s[3] and s[0] != s[1],
        "NEAR4": lambda s: len(set(s)) == 2 and max(s.count(x) for x in set(s)) == 3,
    }
    census = {}
    for label, n in (("ABA", 3), ("ABAB", 4), ("NEAR4", 4)):
        shape = exact = 0
        for locus, source_rows in by["ZL3b"].items():
            for first in range(len(source_rows)):
                start = int(source_rows[first]["source_group_index"])
                ws = [window(e, locus, start, n) for e in EDS]
                if any(w is None for w in ws):
                    continue
                strings = [[r["ivtff_group_raw"] for r in w] for w in ws]
                if not all(predicates[label](s) for s in strings):
                    continue
                shape += 1
                exact += int(len({tuple(s) for s in strings}) == 1)
        prefix = "near_repetition_4" if label == "NEAR4" else label
        census[prefix + "_shape_windows"] = shape
        census[prefix + "_literal_identical_all_readings"] = exact
    out["census"] = census
    wanted = [("ABA", ("f19v.10", 1)), ("ABA", ("f21r.11", 1)),
              ("ABAB", ("f8r.19", 5)), ("ABAB", ("f30r.11", 2)),
              ("NEAR4", ("f86v3.3", 1))]
    for kind, (locus, start) in wanted:
        readings = {}
        for e in EDS:
            seq = window(e, locus, start, 4 if kind != "ABA" else 3)
            readings[e] = [{k: r[k] for k in ("source_group_index", "ivtff_group_raw", "left_separator", "right_separator")} for r in seq]
        out["patterns"].append({"kind": kind, "locus": locus, "start_source_group_index_1based": start,
                                 "readings": readings})
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
