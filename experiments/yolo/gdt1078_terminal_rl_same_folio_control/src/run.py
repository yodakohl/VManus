#!/usr/bin/env python3
"""Frozen GDT1077 same-folio r/l control and line-position diagnostics."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ART=Path(__file__).resolve().parents[1]/"artifacts"
PARENT=ROOT/"experiments/yolo/gdt1077_terminal_rl_next_initial_class/artifacts/EVENTS.tsv"
HASH="b94d3bdc25a084b0ec25e24a2357363ab0bce05da409c89f2f252fde5687e1b1"
READERS=("ZL3b","IT2a","RF1b")


def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f,delimiter="\t"))


def write(path,records,fields):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
        w.writeheader();w.writerows(records)


def measure(es):
    r=[e for e in es if e["ending"]=="r"];l=[e for e in es if e["ending"]=="l"]
    rn,ln=len(r),len(l);ra=sum(int(e["next_aeio"]) for e in r);la=sum(int(e["next_aeio"]) for e in l)
    diff=ra/rn-la/ln if rn and ln else 0.0
    return r,l,rn,ln,ra,la,diff


def main():
    assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==HASH
    events=read(PARENT);assert len(events)==19571
    foliogroups=defaultdict(list)
    posgroups=defaultdict(list)
    for e in events:
        foliogroups[(e["edition"],e["rest"],e["folio"])].append(e)
        position="FIRST" if int(e["source_group_index"])==1 else "INTERNAL"
        posgroups[(e["edition"],e["rest"],e["section"],e["hand"],position)].append(e)
    folio=[]
    for (ed,rest,leaf),es in sorted(foliogroups.items()):
        r,l,rn,ln,ra,la,diff=measure(es)
        info=rn>=2 and ln>=2
        folio.append(dict(edition=ed,rest=rest,folio=leaf,sections=";".join(sorted({e["section"] for e in es})),
            hands=";".join(sorted({e["hand"] for e in es})),r_n=rn,r_aeio=ra,l_n=ln,l_aeio=la,
            informative=int(info),delta=f"{diff:.9f}",direction="R_GREATER" if diff>0 else "L_GREATER" if diff<0 else "TIE_OR_NO_PAIR"))
    position=[]
    for (ed,rest,sec,hand,pos),es in sorted(posgroups.items()):
        r,l,rn,ln,ra,la,diff=measure(es)
        rf=len({e["folio"] for e in r});lf=len({e["folio"] for e in l})
        info=rn>=3 and ln>=3 and rf>=2 and lf>=2
        position.append(dict(edition=ed,rest=rest,section=sec,hand=hand,position=pos,
            r_n=rn,r_aeio=ra,r_folios=rf,l_n=ln,l_aeio=la,l_folios=lf,
            informative=int(info),delta=f"{diff:.9f}",direction="R_GREATER" if diff>0 else "L_GREATER" if diff<0 else "TIE_OR_NO_PAIR"))
    info={ed:[x for x in folio if x["edition"]==ed and x["informative"]] for ed in READERS}
    posinfo={(ed,p):[x for x in position if x["edition"]==ed and x["position"]==p and x["informative"]]
             for ed in READERS for p in ("FIRST","INTERNAL")}
    zl=info["ZL3b"]
    leaves=len({x["folio"] for x in zl})
    positive=sum(x["direction"]=="R_GREATER" for x in zl)
    mean=sum(float(x["delta"]) for x in zl)/len(zl) if zl else 0.0
    decision="NO_CAPACITY" if len(zl)<20 or leaves<10 else (
        "SAME_FOLIO_R_CONTEXT_LEAD" if 3*positive>=2*len(zl) and mean>=0.05
        else "SAME_FOLIO_R_CONTEXT_GATE_FAIL")
    ART.mkdir(exist_ok=True)
    write(ART/"FOLIO_CELLS.tsv",folio,list(folio[0]))
    write(ART/"POSITION_CELLS.tsv",position,list(position[0]))
    pos_summary={ed:{p:{"informative":len(posinfo[(ed,p)]),
                   "positive":sum(x["direction"]=="R_GREATER" for x in posinfo[(ed,p)]),
                   "mean_delta":sum(float(x["delta"]) for x in posinfo[(ed,p)])/len(posinfo[(ed,p)]) if posinfo[(ed,p)] else 0.0}
                     for p in ("FIRST","INTERNAL")} for ed in READERS}
    summary={"input_events":len(events),"folio_cells":len(folio),
        "informative_folio_cells":{ed:len(info[ed]) for ed in READERS},
        "informative_physical_folios":{ed:len({x["folio"] for x in info[ed]}) for ed in READERS},
        "positive_folio_cells":{ed:sum(x["direction"]=="R_GREATER" for x in info[ed]) for ed in READERS},
        "equal_cell_mean_delta":{ed:sum(float(x["delta"]) for x in info[ed])/len(info[ed]) if info[ed] else 0.0 for ed in READERS},
        "mixed_section_hand_cells":sum(len({(e["section"],e["hand"]) for e in es})>1 for es in foliogroups.values()),
        "position_cells":len(position),"position_diagnostic":pos_summary,"decision":decision,
        "claim_ceiling":"Same-folio written association only; no phonetic, semantic or project-wide significance claim."}
    (ART/"RESULT.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
