#!/usr/bin/env python3
"""Same-rest r/l terminal versus next-initial graphic class."""
import csv
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ART=Path(__file__).resolve().parents[1]/"artifacts"
SOURCE=ROOT/"experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW=ROOT/"experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
READERS=("ZL3b","IT2a","RF1b")


def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))


def write(path,data,fields):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
        w.writeheader();w.writerows(data)


def main():
    pages=[r["page"] for r in read(ALLOW)]
    assert len(pages)==179 and not any(p.startswith("f84") for p in pages)
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",str(SOURCE),"--selector","page",
         "--columns","edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator,section,hand",
         "--forbid-prefix","f84"]
    for p in pages:cmd.extend(["--allow",p])
    got=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    lines=defaultdict(dict)
    for r in csv.DictReader(io.StringIO(got.stdout),delimiter="\t"):
        if r["kind"]!="P":continue
        key=(r["edition"],r["locus"]);idx=int(r["source_group_index"])
        if idx in lines[key]:raise ValueError("duplicate group")
        lines[key][idx]=r
    events=[]
    for (ed,locus),groups in sorted(lines.items()):
        for idx,left in sorted(groups.items()):
            right=groups.get(idx+1)
            if right is None:continue
            a,b=left["ivtff_group_raw"],right["ivtff_group_raw"]
            if (not re.fullmatch(r"[a-z]+",a) or not re.fullmatch(r"[a-z]+",b)
                or len(a)<3 or a[-1] not in "rl"
                or left["right_separator"]!="DEFINITE_SPACE"
                or right["left_separator"]!="DEFINITE_SPACE"):
                continue
            assert left["section"]==right["section"] and left["hand"]==right["hand"]
            events.append(dict(edition=ed,locus=locus,source_group_index=idx,
                folio=re.match(r"f\d+",left["page"]).group(),section=left["section"],
                hand=left["hand"],rest=a[:-1],ending=a[-1],left_form=a,
                next_form=b,next_initial=b[0],next_aeio=int(b[0] in "aeio")))
    cells=defaultdict(list)
    for e in events:cells[(e["edition"],e["rest"],e["section"],e["hand"])].append(e)
    strata=[]
    for (ed,rest,section,hand),es in sorted(cells.items()):
        r=[e for e in es if e["ending"]=="r"];l=[e for e in es if e["ending"]=="l"]
        rn,ln=len(r),len(l);ra=sum(e["next_aeio"] for e in r);la=sum(e["next_aeio"] for e in l)
        rf=len({e["folio"] for e in r});lf=len({e["folio"] for e in l})
        info=rn>=3 and ln>=3 and rf>=2 and lf>=2
        delta=ra/rn-la/ln if rn and ln else 0.0
        strata.append(dict(edition=ed,rest=rest,section=section,hand=hand,
            r_n=rn,r_aeio=ra,r_folios=rf,l_n=ln,l_aeio=la,l_folios=lf,
            informative=int(info),delta=f"{delta:.9f}",direction="R_GREATER" if delta>0
            else "L_GREATER" if delta<0 else "TIE_OR_NO_PAIR"))
    info={ed:[x for x in strata if x["edition"]==ed and x["informative"]] for ed in READERS}
    mean={ed:sum(float(x["delta"]) for x in info[ed])/len(info[ed]) if info[ed] else 0.0 for ed in READERS}
    positive={ed:sum(x["direction"]=="R_GREATER" for x in info[ed]) for ed in READERS}
    zl=info["ZL3b"]
    decision="NO_CAPACITY" if len(zl)<10 else (
        "R_CONTEXT_LEAD" if 3*positive["ZL3b"]>=2*len(zl) and mean["ZL3b"]>=0.05
        else "R_CONTEXT_GATE_FAIL")
    ART.mkdir(exist_ok=True)
    write(ART/"EVENTS.tsv",events,list(events[0]))
    write(ART/"STRATA.tsv",strata,list(strata[0]))
    result={"guard":got.stderr.strip(),"eligible_events":len(events),"strata":len(strata),
        "informative":{ed:len(info[ed]) for ed in READERS},"positive":positive,
        "equal_cell_mean_delta":mean,"decision":decision,
        "claim_ceiling":"Written next-initial association only; no phonetic sandhi, grammar value, significance or translation."}
    (ART/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
