#!/usr/bin/env python3
"""Independent arithmetic and provenance validator for GDT197."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(name):
    with (ROOT/name).open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()

def main():
    result=json.loads((ROOT/"gdt197_result.json").read_text());scores=read("gdt197_decoder_scores.tsv");folds=read("gdt197_folio_contributions.tsv");null=read("gdt197_order_null.tsv");counter=read("gdt197_counterexamples.tsv");checks=[]
    add=lambda n,v:checks.append((n,bool(v)))
    add("status",result["status"]=="TERMINAL_Y_SEQUENCE_SIGNAL_NOT_UNIQUE_OT_AXIS_NOT_SELECTED")
    add("candidates",[r["candidate"]for r in scores]==["AL_Y","AL_OT","Y_OT"])
    add("selected",[r["candidate"]for r in scores if r["selected_gdt179"]=="1"]==["Y_OT"])
    add("dimensions",result["complete_lines"]==1169 and result["groups"]==8641 and result["folios"]==91)
    add("state_totals",all(sum(int(r[f"state_{x}"])for x in("00","01","10","11"))==8641 for r in scores))
    add("fold_rows",len(folds)==273 and all(sum(int(x["held_groups"])for x in folds if x["candidate"]==r["candidate"])==8641 for r in scores))
    for row in scores:
        subset=[x for x in folds if x["candidate"]==row["candidate"]]
        u=sum(float(x["unigram_bits"])for x in subset);m=sum(float(x["markov_bits"])for x in subset)
        add("fold_unigram_"+row["candidate"],abs(u-float(row["unigram_bits"]))<1e-8)
        add("fold_markov_"+row["candidate"],abs(m-float(row["markov_bits"]))<1e-8)
        add("gain_"+row["candidate"],abs(u-m-float(row["gain_bits"]))<1e-8)
        add("positive_"+row["candidate"],sum(float(x["order_gain_bits"])>0 for x in subset)==int(row["positive_folios"]))
    ranked=sorted(scores,key=lambda r:float(r["observed_z"]),reverse=True)
    add("ranks",all(int(r["rank_by_z"])==i+1 for i,r in enumerate(ranked)))
    add("winner",result["winning_candidate"]==ranked[0]["candidate"]=="AL_Y")
    add("selected_rank",int(result["selected_rank"])==next(int(r["rank_by_z"])for r in scores if r["candidate"]=="Y_OT"))
    add("paired_gap",abs(result["al_y_minus_y_ot_observed_z_gap"]-(float(next(r for r in scores if r["candidate"]=="AL_Y")["observed_z"])-float(next(r for r in scores if r["candidate"]=="Y_OT")["observed_z"])))<1e-10)
    add("paired_p_range",0<result["paired_gap_two_sided_p"]<=1)
    add("null_rows",len(null)==3 and all(int(r["worlds"])==4096 and int(r["seed"])==197197 for r in null))
    add("counterexamples",len(counter)==5)
    add("no_f84",not any("f84" in r["held_folio"] for r in folds))
    add("f84_flags",all(v is False for v in result["f84r"].values()))
    for group in("inputs","implementation","outputs","documents"):
        for name,digest in result[group].items():add("hash:"+group+":"+name,sha(name)==digest)
    raw=dict(result);digest=raw.pop("result_content_sha256");add("content_hash",csha(raw)==digest)
    out={"schema":"GDT197_VALIDATION_V1","status":"PASS"if all(v for _,v in checks)else"FAIL","checks_passed":sum(v for _,v in checks),"checks_total":len(checks),"failed":[n for n,v in checks if not v],"result_sha256":sha("gdt197_result.json"),"scope":"Independent retained-output arithmetic, selection, provenance, and hash validation; null RNG is not independently replayed."}
    (ROOT/"gdt197_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,sort_keys=True))
    if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
