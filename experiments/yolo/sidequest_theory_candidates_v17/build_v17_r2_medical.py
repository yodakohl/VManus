#!/usr/bin/env python3
"""Build the independent V17 R2 recurrent-card audit from frozen V16 files."""

from __future__ import annotations

import csv
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V16 = ROOT / "experiments/yolo/sidequest_theory_candidates_v16"
LEDGER = V16 / "V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ["f10r","f11r","f55v","f56r","f81v","f82r","f83r"]

# tuple: selected, confidence, status, conditioned second sense, three rivals.
# Each rival is text, grammar, cross-page consistency, Herbal/Bio portability,
# historical phrase plausibility, silent/special repairs.  Scores were fixed as
# the R2 reading before the generated all-occurrence table was inspected.
D = {
"2f1c5e56e8f0ff459065": ("in the stated measure or for the stated time", .66, "IMPROVED", "", [("in the stated measure or for the stated time",5,5,5,5,1),("for the same duration",4,4,4,5,4),("then in the ordinary manner",3,3,4,4,7)]),
"dcda95c81a5460feb191": ("with the foregoing preparation; likewise", .62, "IMPROVED", "", [("with the foregoing preparation; likewise",5,5,5,5,1),("add the prepared liquor",4,3,4,5,5),("then continue",3,4,5,5,6)]),
"b921a237be883a820352": ("this present portion or treated member", .57, "IMPROVED", "treated member after a local application phrase", [("this present portion or treated member",5,5,5,5,2),("this treated member",4,4,4,5,4),("the current procedural step",3,4,5,3,7)]),
"bc4f1f5c006c74a4d26d": ("give the ordinary lukewarm bath and set it ready", .44, "IMPROVED", "", [("set ready in the usual manner; close the rubric",4,5,4,4,3),("give the ordinary lukewarm bath and set it ready",5,5,5,5,2),("strain it and set it aside",4,3,4,5,6)]),
"6f7ff8287eddf4da9fdb": ("mix until the preparation is even", .58, "RETAINED", "", [("mix until the preparation is even",5,5,5,5,1),("set the preparation ready",4,4,5,5,4),("warm it gently",4,3,4,5,6)]),
"276a7c2d74d1143446f4": ("apply or use it at the affected place", .56, "REVERSED", "take the lesser portion only when followed by a measure card", [("use the lesser portion",4,4,4,4,5),("apply or use it at the affected place",5,5,5,5,2),("use the cooled preparation",3,3,4,4,8)]),
"7d25241b0e56c836372a": ("bathe with the tempered herbal liquor", .51, "IMPROVED", "", [("use the tempered warm medium; close the rubric",5,5,5,5,2),("bathe with the tempered herbal liquor",5,5,5,5,1),("keep the mixture warm",4,4,4,5,5)]),
"dd0ecaf5e27d81befffc": ("at the indicated affected place", .61, "RETAINED", "", [("at the indicated affected place",5,5,5,5,1),("at the lower body part",4,3,4,4,5),("then continue",2,3,4,4,8)]),
"b5fcea1eaed06b2f2291": ("take up the next entry or portion", .69, "RETAINED", "", [("take up the next entry or portion",5,5,5,5,1),("take the next portion",5,5,5,5,1),("draw fresh water",3,3,4,4,7)]),
"7db18b2f0fb7ed0fcfd3": ("pour over and rinse the local place", .48, "RETAINED", "", [("pour over and rinse the local place",5,5,5,5,2),("warm it gently",4,4,4,5,5),("finish the treatment",3,4,4,4,6)]),
"de7321bface5628e35d6": ("let the liquor drain at the lower outlet", .43, "REVERSED", "", [("leave at the ordinary base setting; close the rubric",4,4,3,3,5),("pour or rinse at the local place",4,4,4,5,4),("let the liquor drain at the lower outlet",5,5,4,5,2)]),
"0275fbf14e07935b0a45": ("mix the preparation thoroughly", .49, "REVERSED", "keep gently warmed when directly flanked by a heat card", [("keep gently warmed",5,4,5,5,3),("mix the preparation thoroughly",5,5,5,5,2),("add warmed water",4,3,4,5,6)]),
"1645e612504fcef59ced": ("add the measured ingredient", .55, "IMPROVED", "", [("then put it in",5,5,5,5,2),("add the measured ingredient",5,5,5,5,1),("open the upper inlet",3,3,3,4,7)]),
"7a4bb8136330ee4e6e56": ("the prepared or expressed liquor", .54, "IMPROVED", "expressed juice in a Herbal plant-part clause", [("the prepared or expressed liquor",5,5,5,5,1),("the expressed juice",5,4,4,5,3),("from the source just named",3,4,5,4,6)]),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", .59, "RETAINED", "", [("when the preparation is ready",5,5,5,5,1),("until it is warm",4,3,4,5,5),("after straining clear",3,3,4,5,7)]),
"308e8ea2d5d190c498e8": ("mix the two portions with warm water", .49, "IMPROVED", "", [("combine the two portions",5,5,5,5,2),("mix the two portions with warm water",5,5,5,5,1),("use the lower vessel",3,3,4,4,7)]),
"4d4559019a961b834aa1": ("repeat the foregoing preparation", .46, "REVERSED", "of the same when it directly governs a following noun-like card", [("of the same",4,4,5,5,4),("then continue",4,5,5,5,3),("repeat the foregoing preparation",5,5,5,5,2)]),
"259b2b3b0bf859882e2c": ("strain the application and set it aside", .40, "REVERSED", "", [("finish this application; close the rubric",4,4,4,4,4),("strain the application and set it aside",5,5,4,5,2),("give the ordinary bath",3,3,4,5,7)]),
"2cc054357a929df85f64": ("the flowering tops", .45, "REVERSED", "", [("thereafter",4,5,3,5,4),("the flowering tops",5,5,3,5,2),("the tender stem",3,3,3,5,6)]),
"2cc8bb3c2af19607888f": ("pass the liquor through the joined conduits", .53, "IMPROVED", "", [("pass the liquor through the joined conduits",5,5,5,5,1),("keep the member immersed",4,4,5,5,4),("at the second opening",3,3,5,4,7)]),
"b5df9126607030b95175": ("until the liquor runs clear", .58, "IMPROVED", "", [("until the liquor runs clear",5,5,5,5,1),("repeat the washing",3,3,4,5,7),("use clean water",4,3,4,5,6)]),
"28ffbc88b97772a75f1e": ("keep the combined mixture covered", .43, "IMPROVED", "", [("retain the combined mixture; close the rubric",5,5,5,5,2),("keep the combined mixture covered",5,5,5,5,1),("strain the mixed liquor",3,3,4,5,7)]),
"3b70942557b3a40e8030": ("let the liquor settle", .55, "RETAINED", "", [("let the liquor settle",5,5,5,5,1),("cool the bath",4,3,4,5,5),("pour into the lower vessel",3,3,4,4,7)]),
"54d0e228ca346110af05": ("keep it for the stated time", .56, "IMPROVED", "", [("for the same duration",5,5,5,5,1),("keep it for the stated time",5,5,5,5,1),("repeat after one interval",3,3,4,5,7)]),
"87411f84689b4f93a303": ("warm it gently once", .55, "IMPROVED", "", [("heat once; close the rubric",5,5,5,5,1),("warm it gently once",5,5,5,5,1),("boil it strongly",3,3,4,4,8)]),
"90bcf0a9ec0ef56399e6": ("toward the lower outlet", .47, "RETAINED", "", [("toward the lower outlet",5,5,5,5,1),("apply below the waist",4,3,4,4,5),("use a lower measure",3,3,4,3,7)]),
"9ad66e67803a12e745de": ("use the freshly pounded preparation", .52, "IMPROVED", "", [("use the fresh preparation",5,5,5,5,1),("use the freshly pounded preparation",5,5,5,5,1),("take the flowering tops",4,3,3,5,5)]),
"9da1b6ac2c929daea697": ("one measured portion", .56, "IMPROVED", "", [("one measured share",5,5,5,5,1),("one measured portion",5,5,5,5,1),("one vesselful",4,4,4,5,4)]),
"d68bc8de3bcee09db23c": ("strain it thoroughly through cloth", .57, "IMPROVED", "strain it a second time when immediately repeated", [("strain completely; close the rubric",5,5,5,5,1),("strain it thoroughly through cloth",5,5,5,5,1),("let it steep until ready",4,3,4,5,5)]),
"d904bf7b044dd3922781": ("at a gentle heat", .55, "RETAINED", "", [("at a gentle heat",5,5,5,5,1),("until lukewarm",4,4,5,5,4),("in the broad vessel",3,3,4,4,7)]),
}

def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    rows=[r for r in read_tsv(LEDGER) if r["ledger_scope"]=="GDT327_PROSE"]
    cnt=Counter(r["exact_tuple_id"] for r in rows)
    ids={k for k,v in cnt.items() if v>=3}
    assert ids==set(D), (ids-set(D),set(D)-ids)

    # Guarded field metadata extraction. The mixed full table is never parsed.
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",str(ROOT/"gdt327_joint_tuple_interlinear.tsv"),
         "--selector","page"]
    for page in PAGES: cmd += ["--allow",page]
    cmd += ["--forbid-prefix","f84",
         "--columns","page,locus,group_index,group_count,record_ordinal,field_ordinal,within_field_position,joint_tuple_id"]
    text=subprocess.run(cmd,check=True,text=True,capture_output=True).stdout
    lines=[line for line in text.splitlines() if not line.startswith("GUARD_STATS ")]
    meta=list(csv.DictReader(lines,delimiter="\t"))
    mm={(r["page"],r["locus"],int(r["group_index"])):r for r in meta}

    decision=[]
    first={}
    for r in rows: first.setdefault(r["exact_tuple_id"],r)
    for tid in sorted(ids,key=lambda k:(-cnt[k],k)):
        selected,conf,status,second,rivals=D[tid]
        out={"exact_tuple_id":tid,"surface_examples":first[tid]["surface"],"events":cnt[tid],
             "pages":"|".join(sorted({r['page'] for r in rows if r['exact_tuple_id']==tid})),
             "v16_incumbent":first[tid]["default_English"]}
        for i,(meaning,g,c,p,h,rep) in enumerate(rivals,1):
            out[f"rival_{i}"]=meaning; out[f"rival_{i}_grammar_fit_0_5"]=g
            out[f"rival_{i}_cross_page_0_5"]=c; out[f"rival_{i}_herbal_bio_0_5"]=p
            out[f"rival_{i}_historical_0_5"]=h; out[f"rival_{i}_silent_repairs"]=rep
            out[f"rival_{i}_net_score"]=g+c+p+h-rep
        out.update(selected_meaning=selected,conditioned_second_sense=second,
                   confidence=f"{conf:.2f}",revision_status=status)
        decision.append(out)
    write_tsv(HERE/"V17_R2_RECURRENT_CARD_DECISIONS.tsv",decision,list(decision[0]))

    byloc=defaultdict(list)
    for r in rows: byloc[(r["page"],r["locus"])].append(r)
    for seq in byloc.values(): seq.sort(key=lambda r:int(r["event_index"]))
    occ=[]
    for key in sorted(byloc):
        seq=byloc[key]
        translated=[]
        for r in seq:
            translated.append(D[r["exact_tuple_id"]][0] if r["exact_tuple_id"] in D else r["default_English"])
        full="; ".join(translated)
        for j,r in enumerate(seq):
            tid=r["exact_tuple_id"]
            if tid not in ids: continue
            m=mm[(r["page"],r["locus"],int(r["event_index"]))]
            prev=" | ".join(f"{x['surface']}={D[x['exact_tuple_id']][0] if x['exact_tuple_id'] in D else x['default_English']}" for x in seq[max(0,j-2):j])
            nxt=" | ".join(f"{x['surface']}={D[x['exact_tuple_id']][0] if x['exact_tuple_id'] in D else x['default_English']}" for x in seq[j+1:j+3])
            occ.append({"page":r["page"],"locus":r["locus"],"record_ordinal":m["record_ordinal"],
                "field_ordinal":m["field_ordinal"],"within_field_position":m["within_field_position"],
                "line_boundary":"LINE_START" if j==0 else ("LINE_END" if j==len(seq)-1 else "LINE_INTERIOR"),
                "event_index":r["event_index"],"surface":r["surface"],"exact_tuple_id":tid,
                "v16_reading":r["default_English"],"v17_selected_reading":D[tid][0],
                "left_two":prev,"right_two":nxt,"rewritten_complete_local_sequence":full})
    assert len(occ)==sum(cnt[k] for k in ids)==217
    write_tsv(HERE/"V17_R2_ALL_OCCURRENCE_READINGS.tsv",occ,list(occ[0]))

if __name__=="__main__": main()
