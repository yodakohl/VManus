#!/usr/bin/env python3
"""Within-register capacity and direction for five frozen exact pX/yX bases."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
EVENTS = ROOT / "experiments/yolo/gdt1074_physical_paragraph_pair_robustness/artifacts/EVENTS.tsv"
EVENTS_HASH = "6357927a1a0d4275e057e0bd06043061c5ec749d506dce4174c4924e6abef75f"
BASES = ("aiin","chedy","cheol","cheor","chor")
EDITIONS = ("ZL3b","IT2a","RF1b")


def write_tsv(path, rows, fields):
    with path.open("w",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def main():
    assert hashlib.sha256(EVENTS.read_bytes()).hexdigest()==EVENTS_HASH
    with EVENTS.open(newline="") as file:
        fixed=[r for r in csv.DictReader(file,delimiter="\t")
               if r["status"]=="INCLUDED" and r["base"] in BASES]
    with ALLOW.open(newline="") as file:
        pages=[r["page"] for r in csv.DictReader(file,delimiter="\t")]
    assert len(pages)==179 and not any(p.startswith("f84") for p in pages)
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",str(SOURCE),"--selector","page",
         "--columns","edition,locus,kind,source_group_index,section,hand,currier",
         "--forbid-prefix","f84"]
    for p in pages:cmd.extend(["--allow",p])
    got=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    metadata={}
    for r in csv.DictReader(io.StringIO(got.stdout),delimiter="\t"):
        if r["kind"]=="P" and r["source_group_index"]=="1":
            key=(r["edition"],r["locus"])
            if key in metadata:raise ValueError("duplicate source first group")
            metadata[key]=r
    events=[]
    for e in fixed:
        m=metadata[(e["edition"],e["locus"])]
        events.append(dict(base=e["base"],edition=e["edition"],lead=e["lead"],
            form=e["form"],locus=e["locus"],folio=e["physical_folio"],
            start=e["physical_paragraph_start"],section=m["section"],
            hand=m["hand"],currier=m["currier"]))
    events.sort(key=lambda x:(x["edition"],x["base"],x["locus"]))
    OUT.mkdir(exist_ok=True)
    write_tsv(OUT/"EVENTS.tsv",events,list(events[0]))
    groups=defaultdict(list)
    for e in events:groups[(e["edition"],e["base"],e["section"],e["hand"])].append(e)
    strata=[]
    for (edition,base,section,hand),es in sorted(groups.items()):
        p=[e for e in es if e["lead"]=="p"]
        y=[e for e in es if e["lead"]=="y"]
        ps=sum(e["start"]=="1" for e in p)
        ys=sum(e["start"]=="1" for e in y)
        pf=len({e["folio"] for e in p})
        yf=len({e["folio"] for e in y})
        info=len(p)>=2 and len(y)>=2 and pf>=2 and yf>=2
        direction="NO_PAIR" if not p or not y else (
            "P_GREATER" if ps*len(y)>ys*len(p) else
            "Y_GREATER" if ps*len(y)<ys*len(p) else "EQUAL")
        strata.append(dict(edition=edition,base=base,section=section,hand=hand,
            p_n=len(p),p_starts=ps,p_folios=pf,y_n=len(y),y_starts=ys,
            y_folios=yf,informative=int(info),direction=direction))
    write_tsv(OUT/"STRATA.tsv",strata,list(strata[0]))
    info={ed:[s for s in strata if s["edition"]==ed and s["informative"]]
          for ed in EDITIONS}
    base_counts={ed:len({s["base"] for s in info[ed]}) for ed in EDITIONS}
    primary="NO_CAPACITY" if base_counts["ZL3b"]<3 else (
        "WITHIN_REGISTER_FORMAL_DIRECTION" if all(s["direction"]=="P_GREATER"
        for s in info["ZL3b"]) else "WITHIN_REGISTER_DIRECTION_FAIL")
    same_leaf=defaultdict(set)
    for e in events:same_leaf[(e["edition"],e["base"],e["folio"])].add(e["lead"])
    summary={"guard":got.stderr.strip(),"fixed_event_rows":len(events),
        "strata_rows":len(strata),
        "informative_section_hand_strata":{ed:len(info[ed]) for ed in EDITIONS},
        "informative_bases":base_counts,
        "informative_directions":{ed:dict(Counter(s["direction"] for s in info[ed])) for ed in EDITIONS},
        "same_leaf_both_forms":{ed:sum(k[0]==ed and len(v)==2 for k,v in same_leaf.items())
                                for ed in EDITIONS},
        "primary_decision":primary,
        "claim_ceiling":"Within-section/hand capacity or direction only; no morpheme meaning or translation."}
    (OUT/"RESULT.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
