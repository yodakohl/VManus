#!/usr/bin/env python3
"""Exact pX/yX line-initial paragraph-start census on allowed selectors."""
import csv
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
COLS = "edition,page,locus,kind,source_group_index,paragraph_start,ivtff_group_raw"
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def main():
    with ALLOW.open(newline="") as file:
        pages = [r["page"] for r in csv.DictReader(file, delimiter="\t")]
    assert len(pages) == 179 and not any(p.startswith("f84") for p in pages)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
           "--selector", "page", "--columns", COLS, "--forbid-prefix", "f84"]
    for p in pages:
        cmd.extend(["--allow", p])
    got = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(io.StringIO(got.stdout), delimiter="\t"))
    if any(r["page"].startswith("f84") for r in rows):
        raise ValueError("forbidden page materialized")
    initials = [r for r in rows if r["kind"] == "P" and r["source_group_index"] == "1"
                and re.fullmatch(r"[py][a-z]{3,}", r["ivtff_group_raw"])]
    by = defaultdict(list)
    for r in initials:
        by[(r["edition"], r["ivtff_group_raw"])].append(r)
    all_forms = {r["ivtff_group_raw"] for r in initials}
    bases = sorted({f[1:] for f in all_forms if f.startswith("p")
                    and "y" + f[1:] in all_forms})
    output = []
    for base in bases:
        for edition in EDITIONS:
            p = by[(edition, "p" + base)]
            y = by[(edition, "y" + base)]
            p_folios = {re.match(r"f\d+", r["page"]).group() for r in p}
            y_folios = {re.match(r"f\d+", r["page"]).group() for r in y}
            p_starts = sum(r["paragraph_start"] == "1" for r in p)
            y_starts = sum(r["paragraph_start"] == "1" for r in y)
            supported = len(p) >= 3 and len(y) >= 3 and len(p_folios) >= 2 and len(y_folios) >= 2
            direction = "P_GREATER" if p and y and p_starts * len(y) > y_starts * len(p) else (
                "EQUAL" if p and y and p_starts * len(y) == y_starts * len(p) else (
                "Y_GREATER" if p and y else "NO_PAIR_IN_READER"))
            output.append(dict(base=base, edition=edition, p_form="p"+base,
                y_form="y"+base, p_initial=len(p), p_paragraph_starts=p_starts,
                p_folios=len(p_folios), y_initial=len(y), y_paragraph_starts=y_starts,
                y_folios=len(y_folios), supported=int(supported), direction=direction))
    OUT.mkdir(exist_ok=True)
    fields = list(output[0]) if output else ["base","edition","p_form","y_form","p_initial",
        "p_paragraph_starts","p_folios","y_initial","y_paragraph_starts","y_folios","supported","direction"]
    with (OUT / "PAIRS.tsv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    zl = [r for r in output if r["edition"] == "ZL3b" and r["supported"]]
    summary = {"guard":got.stderr.strip(), "selected_rows":len(rows),
        "eligible_line_initial_events":len(initials), "pair_bases":len(bases),
        "supported_zl_bases":len(zl),
        "supported_zl_p_greater":sum(r["direction"] == "P_GREATER" for r in zl),
        "supported_zl_equal":sum(r["direction"] == "EQUAL" for r in zl),
        "supported_zl_y_greater":sum(r["direction"] == "Y_GREATER" for r in zl),
        "primary_gate":("CAPACITY_STOP" if len(zl) < 3 else
                        "GENERAL_DIRECTION" if all(r["direction"] == "P_GREATER" for r in zl)
                        and all(x["direction"] == "P_GREATER" for x in output
                        if x["base"] in {z["base"] for z in zl} and x["supported"])
                        else "DIRECTION_NOT_UNIVERSAL"),
        "claim_ceiling":"Exact whole-form paragraph scope only; no prefix meaning or translation."}
    (OUT / "RESULT.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
