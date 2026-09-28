#!/usr/bin/env python3
"""Independent fixed-parent folio and position arithmetic replay."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ART=Path(__file__).resolve().parents[1]/"artifacts"
PARENT=ROOT/"experiments/yolo/gdt1077_terminal_rl_next_initial_class/artifacts/EVENTS.tsv"
HASH="b94d3bdc25a084b0ec25e24a2357363ab0bce05da409c89f2f252fde5687e1b1"


def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))


def summarize(es):
    r=[e for e in es if e["ending"]=="r"]
    l=[e for e in es if e["ending"]=="l"]
    rn,ln=len(r),len(l)
    ra=sum(e["next_aeio"]=="1" for e in r)
    la=sum(e["next_aeio"]=="1" for e in l)
    delta=ra/rn-la/ln if rn and ln else 0.0
    return r,l,rn,ln,ra,la,delta


def main():
    checks={"frozen_parent_hash":hashlib.sha256(PARENT.read_bytes()).hexdigest()==HASH}
    events=read(PARENT)
    checks["all_parent_events"]=len(events)==19571 and all(e["edition"] in {"ZL3b","IT2a","RF1b"} for e in events)
    folio=defaultdict(list);position=defaultdict(list)
    for e in events:
        folio[(e["edition"],e["rest"],e["folio"])].append(e)
        slot="FIRST" if e["source_group_index"]=="1" else "INTERNAL"
        position[(e["edition"],e["rest"],e["section"],e["hand"],slot)].append(e)
    frows=read(ART/"FOLIO_CELLS.tsv");prows=read(ART/"POSITION_CELLS.tsv")
    fdict={(x["edition"],x["rest"],x["folio"]):x for x in frows}
    pdict={(x["edition"],x["rest"],x["section"],x["hand"],x["position"]):x for x in prows}
    checks["cell_rosters"]=len(folio)==len(fdict)==len(frows)==11247 and len(position)==len(pdict)==len(prows)==6361
    f_ok=True;p_ok=True;f_info=defaultdict(list);p_info=defaultdict(list)
    for key,es in folio.items():
        x=fdict[key];r,l,rn,ln,ra,la,diff=summarize(es)
        info=rn>=2 and ln>=2
        f_ok &= (int(x["r_n"]),int(x["r_aeio"]),int(x["l_n"]),int(x["l_aeio"]),int(x["informative"]))==(rn,ra,ln,la,int(info))
        f_ok &= abs(float(x["delta"])-diff)<1e-8 and x["sections"]==";".join(sorted({e["section"] for e in es})) and x["hands"]==";".join(sorted({e["hand"] for e in es}))
        f_ok &= x["direction"]==("R_GREATER" if diff>0 else "L_GREATER" if diff<0 else "TIE_OR_NO_PAIR")
        if info:f_info[key[0]].append((key[2],diff))
    for key,es in position.items():
        x=pdict[key];r,l,rn,ln,ra,la,diff=summarize(es)
        rf=len({e["folio"] for e in r});lf=len({e["folio"] for e in l})
        info=rn>=3 and ln>=3 and rf>=2 and lf>=2
        p_ok &= (int(x["r_n"]),int(x["r_aeio"]),int(x["r_folios"]),int(x["l_n"]),int(x["l_aeio"]),int(x["l_folios"]),int(x["informative"]))==(rn,ra,rf,ln,la,lf,int(info))
        p_ok &= abs(float(x["delta"])-diff)<1e-8
        if info:p_info[(key[0],key[4])].append(diff)
    checks["folio_arithmetic"]=f_ok
    checks["position_arithmetic"]=p_ok
    result=json.loads((ART/"RESULT.json").read_text())
    zl=f_info["ZL3b"]
    checks["primary_gate_failure"]=len(zl)==162 and len({leaf for leaf,_ in zl})==64 and sum(diff>0 for _,diff in zl)==96 and sum(diff for _,diff in zl)/len(zl)>=0.05 and result["decision"]=="SAME_FOLIO_R_CONTEXT_GATE_FAIL"
    checks["reader_sensitivity"]=len(f_info["IT2a"])==220 and len(f_info["RF1b"])==150 and sum(x>0 for _,x in f_info["IT2a"])==132 and sum(x>0 for _,x in f_info["RF1b"])==89
    checks["position_counts"]=(len(p_info[("ZL3b","FIRST")]),len(p_info[("ZL3b","INTERNAL")]))==(15,104)
    status="PASS" if all(checks.values()) else "FAIL"
    output={"status":status,"checks":checks,"folio_cells":len(folio),"position_cells":len(position)}
    (ART/"VALIDATION.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
    return 0 if status=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
