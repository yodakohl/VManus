#!/usr/bin/env python3
"""Input roster, guarded extraction, and score replay for GDT1076."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ART = Path(__file__).resolve().parents[1] / "artifacts"
PARENT = ROOT / "experiments/yolo/gdt1075_py_section_hand_confound/artifacts/EVENTS.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
HASH = "6c0b9fd422054a7ece186506d06aa3fa4558a77ac75eefa40424a5b4560a594d"
PRIMARY = {("chedy", "B", "2"), ("cheol", "H", "1"), ("chor", "H", "1")}


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def jac(x, y):
    a, b = set(x.split()), set(y.split())
    return len(a & b) / len(a | b) if a | b else 0.0


def main():
    checks = {}
    checks["frozen_hash"] = hashlib.sha256(PARENT.read_bytes()).hexdigest() == HASH
    original, followers = rows(PARENT), rows(ART / "FOLLOWERS.tsv")
    checks["all_events"] = len(original) == len(followers) == 214 and all(
        tuple(a[k] for k in a) == tuple(b[k] for k in a) for a,b in zip(original,followers))
    pages = [r["page"] for r in rows(ALLOW)]
    checks["admission"] = len(pages) == 179 and not any(p.startswith("f84") for p in pages)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE), "--selector", "page",
           "--columns", "edition,page,locus,kind,source_group_index,left_separator,right_separator,ivtff_group_raw",
           "--forbid-prefix", "f84"]
    for page in pages:cmd.extend(["--allow",page])
    got = subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    by_line=defaultdict(dict)
    for r in csv.DictReader(io.StringIO(got.stdout),delimiter="\t"):
        if r["kind"]=="P" and r["source_group_index"] in {"2","3","4","5"}:
            by_line[(r["edition"],r["locus"])][int(r["source_group_index"])]=r
    exact=True
    for e in followers:
        line=by_line[(e["edition"],e["locus"])]
        found=[]
        for pos in range(2,6):
            if pos not in line:break
            r=line[pos]; w=r["ivtff_group_raw"]
            if r["left_separator"] in {"DEFINITE_SPACE","LINE_START"} and r["right_separator"] in {"DEFINITE_SPACE","LINE_END"} and re.fullmatch(r"[a-z]+",w):
                found.append(w)
        exact &= e["followers"].split()==found and int(e["usable_n"])==len(found)
    checks["extraction"] = exact
    pscores=rows(ART/"P_SCORES.tsv")
    scored={(r["edition"],r["p_locus"]):r for r in pscores}
    computed={}
    for p in (e for e in followers if e["lead"]=="p"):
        pool=[e for e in followers if e["edition"]==p["edition"] and e["section"]==p["section"] and e["hand"]==p["hand"] and e["lead"]=="y" and e["folio"]!=p["folio"]]
        same=[e for e in pool if e["base"]==p["base"]]
        other=defaultdict(list)
        for e in pool:
            if e["base"]!=p["base"]:other[e["base"]].append(e)
        if not same or len({e["folio"] for ys in other.values() for e in ys})<2:continue
        a=sum(jac(p["followers"],e["followers"]) for e in same)/len(same)
        b=sum(sum(jac(p["followers"],e["followers"]) for e in ys)/len(ys) for ys in other.values())/len(other)
        computed[(p["edition"],p["locus"])]=(len(same),sum(map(len,other.values())),len(other),a,b,a-b)
    checks["score_roster"] = len(computed)==len(scored)==43 and set(computed)==set(scored)
    checks["score_arithmetic"] = all(
        (int(s["same_y_n"]),int(s["other_y_n"]),int(s["other_y_bases"]))==v[:3]
        and all(abs(float(s[k])-x)<1e-8 for k,x in zip(("same_mean","other_mean","delta"),v[3:]))
        for locus,v in computed.items() for s in [scored[locus]])
    strata=rows(ART/"STRATA.tsv")
    primary=[r for r in strata if r["edition"]=="ZL3b" and (r["base"],r["section"],r["hand"]) in PRIMARY]
    checks["primary_capacity"] = len(primary)==3 and sorted(int(r["eligible_p_n"]) for r in primary)==[0,2,4]
    result=json.loads((ART/"RESULT.json").read_text())
    checks["registered_decision"] = result["decision"]=="NO_CAPACITY" and result["fixed_events"]==214 and result["scored_p_events"]==43 and result["strata"]==57
    checks["guard"] = "skipped_forbidden\": 2122" in got.stderr and "skipped_forbidden\": 2122" in result["guard"]
    status="PASS" if all(checks.values()) else "FAIL"
    output={"status":status,"checks":checks}
    (ART/"VALIDATION.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
    return 0 if status=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
