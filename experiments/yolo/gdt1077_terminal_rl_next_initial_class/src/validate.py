#!/usr/bin/env python3
"""Independent guarded adjacency and section/hand arithmetic replay."""
import csv
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ART=Path(__file__).resolve().parents[1]/"artifacts"
SOURCE=ROOT/"experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW=ROOT/"experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"


def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))


def main():
    checks={}
    pages=[r["page"] for r in read(ALLOW)]
    checks["page_scope"]=len(pages)==179 and not any(p.startswith("f84") for p in pages)
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",str(SOURCE),"--selector","page",
         "--columns","edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator,section,hand",
         "--forbid-prefix","f84"]
    for p in pages:cmd.extend(["--allow",p])
    got=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    lines=defaultdict(list)
    for r in csv.DictReader(io.StringIO(got.stdout),delimiter="\t"):
        if r["kind"]=="P":lines[(r["edition"],r["locus"])].append(r)
    expected=set()
    for (edition,locus),line in lines.items():
        seq=sorted(line,key=lambda x:int(x["source_group_index"]))
        for left,right in zip(seq,seq[1:]):
            idx=int(left["source_group_index"])
            if int(right["source_group_index"])!=idx+1:continue
            a=left["ivtff_group_raw"];b=right["ivtff_group_raw"]
            if len(a)<3 or a[-1:] not in ("r","l"):continue
            if not re.fullmatch("[a-z]+",a) or not re.fullmatch("[a-z]+",b):continue
            if left["right_separator"]!="DEFINITE_SPACE" or right["left_separator"]!="DEFINITE_SPACE":continue
            expected.add((edition,locus,idx,a,b,left["section"],left["hand"]))
    events=read(ART/"EVENTS.tsv")
    actual={(e["edition"],e["locus"],int(e["source_group_index"]),e["left_form"],e["next_form"],e["section"],e["hand"]) for e in events}
    checks["source_event_roster"]=len(events)==len(actual)==len(expected)==19571 and actual==expected
    checks["event_derived_fields"]=all(
        e["rest"]==e["left_form"][:-1] and e["ending"]==e["left_form"][-1]
        and e["next_initial"]==e["next_form"][0]
        and int(e["next_aeio"])==int(e["next_initial"] in "aeio")
        and e["folio"]==re.match(r"f\d+",e["locus"]).group()
        for e in events)
    groups=defaultdict(list)
    for e in events:groups[(e["edition"],e["rest"],e["section"],e["hand"])].append(e)
    strata=read(ART/"STRATA.tsv")
    seen={(s["edition"],s["rest"],s["section"],s["hand"]):s for s in strata}
    checks["stratum_roster"]=len(groups)==len(seen)==len(strata)==5690
    arithmetic=True
    info=defaultdict(list)
    for key,es in groups.items():
        s=seen[key]
        r=[e for e in es if e["ending"]=="r"];l=[e for e in es if e["ending"]=="l"]
        rn,ln=len(r),len(l);ra=sum(int(e["next_aeio"]) for e in r);la=sum(int(e["next_aeio"]) for e in l)
        rf=len({e["folio"] for e in r});lf=len({e["folio"] for e in l})
        informative=rn>=3 and ln>=3 and rf>=2 and lf>=2
        diff=ra/rn-la/ln if rn and ln else 0.0
        actual_numbers=tuple(int(s[k]) for k in ("r_n","r_aeio","r_folios","l_n","l_aeio","l_folios","informative"))
        arithmetic &= actual_numbers==(rn,ra,rf,ln,la,lf,int(informative)) and abs(float(s["delta"])-diff)<1e-8
        arithmetic &= s["direction"]==("R_GREATER" if diff>0 else "L_GREATER" if diff<0 else "TIE_OR_NO_PAIR")
        if informative:info[key[0]].append(diff)
    checks["stratum_arithmetic"]=arithmetic
    result=json.loads((ART/"RESULT.json").read_text())
    checks["primary_gate"]=(len(info["ZL3b"])==117 and sum(x>0 for x in info["ZL3b"])==87
                            and sum(info["ZL3b"])/117>=0.05 and result["decision"]=="R_CONTEXT_LEAD")
    checks["reader_sensitivity"]=len(info["IT2a"])==148 and len(info["RF1b"])==120 and sum(x>0 for x in info["IT2a"])==120 and sum(x>0 for x in info["RF1b"])==89
    checks["guard"]='"skipped_forbidden": 2122' in got.stderr and '"skipped_forbidden": 2122' in result["guard"]
    status="PASS" if all(checks.values()) else "FAIL"
    output={"status":status,"checks":checks,"source_events":len(expected),"cells":len(groups)}
    (ART/"VALIDATION.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
    return 0 if status=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
