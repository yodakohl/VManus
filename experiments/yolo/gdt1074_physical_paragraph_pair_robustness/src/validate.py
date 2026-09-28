#!/usr/bin/env python3
"""Independent artifact arithmetic and source-locus projection audit."""
import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def main():
    with (OUT / "EVENTS.tsv").open(newline="") as file:
        events = list(csv.DictReader(file, delimiter="\t"))
    with (OUT / "PAIRS.tsv").open(newline="") as file:
        pairs = list(csv.DictReader(file, delimiter="\t"))
    result = json.loads((OUT / "RESULT.json").read_text())
    assert len(pairs) == 47 * 3
    assert Counter(e["status"] for e in events) == result["event_statuses"]
    for r in pairs:
        es=[e for e in events if e["base"]==r["base"] and e["edition"]==r["edition"]]
        included=[e for e in es if e["status"]=="INCLUDED"]
        for lead in "py":
            xs=[e for e in included if e["lead"]==lead]
            assert len(xs)==int(r[lead+"_initial"])
            assert sum(e["physical_paragraph_start"]=="1" for e in xs)==int(r[lead+"_starts"])
            assert len({e["physical_folio"] for e in xs})==int(r[lead+"_folios"])
        assert sum(e["status"]=="UNCERTAIN_BOUNDARY" for e in es)==int(r["excluded_uncertain"])
        assert sum(e["status"]=="NO_PHYSICAL_FLAG" for e in es)==int(r["excluded_no_physical_flag"])
        p,y=int(r["p_initial"]),int(r["y_initial"])
        ps,ys=int(r["p_starts"]),int(r["y_starts"])
        assert (r["supported"]=="1")==(
            p>=3 and y>=3 and int(r["p_folios"])>=2 and int(r["y_folios"])>=2)
        direction="NO_PAIR" if not p or not y else (
            "P_GREATER" if ps*y>ys*p else "Y_GREATER" if ps*y<ys*p else "EQUAL")
        assert r["direction"]==direction
    shared=[b for b in sorted({r["base"] for r in pairs}) if all(next(x for x in pairs
        if x["base"]==b and x["edition"]==ed)["supported"]=="1"
        for ed in ("ZL3b","IT2a","RF1b"))]
    assert shared==result["supported_all_three_bases"]
    assert len(shared)==5 and all(r["direction"]=="P_GREATER" for r in pairs if r["base"] in shared)

    with (ROOT/"experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv").open(newline="") as file:
        pages=[r["page"] for r in csv.DictReader(file,delimiter="\t")]
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",
         str(ROOT/"experiments/semantic_assumptions/results/source_separator_transcription.tsv"),
         "--selector","page","--columns","edition,locus,kind,source_group_index,paragraph_start",
         "--forbid-prefix","f84"]
    for p in pages:cmd.extend(["--allow",p])
    got=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    by=defaultdict(dict)
    for r in csv.DictReader(io.StringIO(got.stdout),delimiter="\t"):
        if r["kind"]=="P" and r["source_group_index"]=="1":
            by[r["locus"]][r["edition"]]=r["paragraph_start"]
    consensus={l:v["ZL3b"] for l,v in by.items() if "ZL3b" in v and "IT2a" in v
               and v["ZL3b"]==v["IT2a"] and v["ZL3b"] in {"0","1"}}
    assert len(consensus)==result["physical_consensus_loci"]==3715
    for e in events:
        if e["status"]=="INCLUDED":
            assert consensus[e["locus"]]==e["physical_paragraph_start"]
    validation={"status":"PASS","pair_rows":len(pairs),"event_rows":len(events),
        "consensus_loci":len(consensus),"shared_supported_bases":shared,
        "claim_ceiling":"Same-manuscript structural direction only; no meaning or significance."}
    (OUT/"VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n")
    print(json.dumps(validation,indent=2))


if __name__=="__main__":main()
