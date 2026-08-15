#!/usr/bin/env python3
"""GDT096: freeze GDT095 layout channel and transfer to HEDGED records."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;ANN=ROOT/"gdt012_annotated_core_inventory.tsv";PARSED=ROOT/"gdt059_hpr2_external_inventory.tsv";METHOD=ROOT/"GDT096_LAYOUT_CHANNEL_TRANSFER_METHOD.md";REPORT=ROOT/"GDT096_LAYOUT_CHANNEL_TRANSFER_REPORT.md";PRED=ROOT/"gdt096_predictions.tsv";SCORES=ROOT/"gdt096_representation_scores.tsv";NULL=ROOT/"gdt096_exact_null.tsv";RESULT=ROOT/"gdt096_result.json"
REPS=("RAW_CHAR3","PAGE_HOST_CHAR3","COMPILER_SIGNATURE","WRAPPER_ONLY","RIGHT_ONLY","B3_ONLY","HOST_WRAPPER_JOINT","HOST_RIGHT_JOINT","HOST_B3_JOINT","HOST_WRAPPER_RIGHT_JOINT");K=5;SHRINK=4.;PAT=re.compile(r"\b(?:base|edge|ground|level)\b")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def tri(vs):
 c=Counter()
 for v in vs:
  s="^"+v+"$";c.update(s[i:i+3] for i in range(max(1,len(s)-2)))
 return c
def distance(a,b):
 k=set(a)|set(b);den=sum(max(a[x],b[x]) for x in k);return 1-sum(min(a[x],b[x]) for x in k)/den if den else 0.
def main():
 ann=read(ANN);parsed=read(PARSED);assert len(ann)==len(parsed)==671 and not any(x["locus"].startswith("f84r") for x in ann+parsed)
 by=defaultdict(list);meta={}
 for a,p in zip(ann,parsed):
  if a["kind"]=="L" and a["section"]=="P" and "PLANT" in a["object_tags"].split(";"):by[a["locus"]].append(p);meta[a["locus"]]=a
 def unit(locus,z):
  z=sorted(z,key=lambda x:int(x["group_index"]));f={"RAW_CHAR3":tri([x["token"] for x in z]),"PAGE_HOST_CHAR3":tri([x["page_host"] for x in z]),"COMPILER_SIGNATURE":Counter(x["compiler_signature"] for x in z),"WRAPPER_ONLY":Counter(x["wrapper"] for x in z),"RIGHT_ONLY":Counter(x["right_family"] for x in z),"B3_ONLY":Counter(x["b3"] for x in z),"HOST_WRAPPER_JOINT":Counter(x["page_host"]+"@W="+x["wrapper"] for x in z),"HOST_RIGHT_JOINT":Counter(x["page_host"]+"@R="+x["right_family"] for x in z),"HOST_B3_JOINT":Counter(x["page_host"]+"@B="+x["b3"] for x in z),"HOST_WRAPPER_RIGHT_JOINT":Counter(x["page_host"]+"@W="+x["wrapper"]+"@R="+x["right_family"] for x in z)}
  return{"locus":locus,"folio":z[0]["physical_folio"],"y":int(bool(PAT.search(meta[locus]["raw_source_description"].lower()))),"features":f}
 train=[unit(l,z) for l,z in by.items() if meta[l]["annotation_certainty"]=="UNHEDGED"];test=[unit(l,z) for l,z in by.items() if meta[l]["annotation_certainty"]=="HEDGED"]
 assert len(train)==83 and len(test)==35 and sum(x["y"] for x in test)==4
 probs={r:[] for r in REPS};base=[]
 for t in test:
  tr=[x for x in train if x["folio"]!=t["folio"]];bp=(sum(x["y"] for x in tr)+.5)/(len(tr)+1);base.append(bp)
  for rep in REPS:
   near=sorted((x for x in tr if distance(t["features"][rep],x["features"][rep])<1-1e-12),key=lambda x:(distance(t["features"][rep],x["features"][rep]),x["locus"]))[:K];weights=np.array([1/(.1+distance(t["features"][rep],x["features"][rep])) for x in near]);probs[rep].append((sum(w*x["y"] for w,x in zip(weights,near))+SHRINK*bp)/(weights.sum()+SHRINK))
 y=np.array([x["y"] for x in test]);base=np.array(base);bits=lambda yy,pp:float((-np.log2(np.where(yy>0,pp,1-pp))).sum());bb=bits(y,base);gains={r:bb-bits(y,np.array(probs[r])) for r in REPS}
 # Exact within-folio orbit retains every target-folio positive count.
 fis={f:[i for i,x in enumerate(test) if x["folio"]==f] for f in sorted({x["folio"] for x in test})};choices=[]
 for f,idx in fis.items():choices.append(list(itertools.combinations(idx,int(y[idx].sum()))))
 worlds=[];local={r:0 for r in REPS};maxc=0
 for combo in itertools.product(*choices):
  yy=np.zeros(len(test));
  for z in combo:yy[list(z)]=1
  b=bits(yy,base);g={r:b-bits(yy,np.array(probs[r])) for r in REPS};worlds.append(g);maxc+=max(g.values())>=max(gains.values())-1e-12
  for r in REPS:local[r]+=g[r]>=gains[r]-1e-12
 assert len(worlds)==1872
 rows=[]
 for rep in REPS:
  fg=[]
  for f,idx in fis.items():fg.append((f,bits(y[idx],base[idx])-bits(y[idx],np.array(probs[rep])[idx])))
  rows.append({"representation":rep,"train_unhedged_loci":len(train),"test_hedged_loci":len(test),"positive_test_loci":int(y.sum()),"baseline_bits":bb,"held_bits":bits(y,np.array(probs[rep])),"gain_bits":gains[rep],"positive_gain_folios":sum(v>0 for _,v in fg),"folio_gains":";".join(f"{f}:{v:.6f}" for f,v in fg),"exact_local_p":local[rep]/len(worlds),"exact_max_representation_p":maxc/len(worlds),"selector_paid_gain_bits":gains[rep]-math.log2(len(REPS))})
 rows.sort(key=lambda x:(-x["gain_bits"],x["representation"]));write(SCORES,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in rows],list(rows[0]))
 pr=[]
 for i,t in enumerate(test):
  pr.append({"locus":t["locus"],"physical_folio":t["folio"],"layout_position_observed":t["y"],"baseline_probability":base[i],**{r.lower()+"_probability":probs[r][i] for r in REPS},"annotation_certainty":"HEDGED","semantic_role":"UNASSIGNED"})
 write(PRED,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in pr],list(pr[0]));null=[{"null_id":"EXACT_WITHIN_TARGET_FOLIO_POSITIVE_COUNT","worlds":len(worlds),"target_positive_counts":";".join(f"{f}:{int(y[idx].sum())}/{len(idx)}" for f,idx in fis.items()),"representations":len(REPS),"observed_best_representation":rows[0]["representation"],"observed_best_gain_bits":rows[0]["gain_bits"],"max_representation_p":rows[0]["exact_max_representation_p"]}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in x.items()} for x in null],list(null[0]))
 frozen=next(x for x in rows if x["representation"]=="HOST_WRAPPER_JOINT");host=next(x for x in rows if x["representation"]=="PAGE_HOST_CHAR3");raw=next(x for x in rows if x["representation"]=="RAW_CHAR3");status="GDT095_HOST_WRAPPER_SPATIAL_TOKEN_LEAD_FAILS_BUT_PAGE_HOST_MARGIN_HAS_LOW_CAPACITY_TRANSFER"
 REPORT.write_text(f"""# GDT096 — layout-channel transfer

## Outcome

**{status}**

The exact GDT095 mixed spatial-token regex and representation grid were frozen, trained on
83 UNHEDGED section-P plant labels, and applied without target refitting to all
35 HEDGED labels. Every prediction excludes its physical folio. Only four
targets contain the frozen position vocabulary.

The GDT095 PAGE_HOST×WRAPPER lead loses {abs(frozen['gain_bits']):.3f} bits and
is negative on all five target folios. Its exact within-folio rank is
p={frozen['exact_local_p']:.4f}. PAGE_HOST trigrams instead gain
{host['gain_bits']:+.3f} bits on all five folios, versus raw trigrams at
{raw['gain_bits']:+.3f}; PAGE_HOST retains {host['selector_paid_gain_bits']:+.3f}
bits after the ten-way selector and has exact max p
{host['exact_max_representation_p']:.4f}. The advantage over raw is only
{host['gain_bits']-raw['gain_bits']:+.3f} bits and the HEDGED endpoint contains
four positives. In those records the words can refer to plant base, ground
level, or panel edge, so this is a low-capacity mixed-context HPR2 marginal
lead, not semantic localization. The frozen construction interaction does not
transfer.

This is archived-data stress testing, not a pristine validation. HEDGED rows
are a different annotation-quality stratum and the source corpus was already
available. The miss nevertheless prevents promotion of the GDT095 association.
No role or gloss is assigned. f84r was absent and untouched.
""",encoding="utf-8")
 result={"schema":"GDT096_LAYOUT_CHANNEL_TRANSFER_RESULT_V1","status":status,"train_unhedged_loci":len(train),"test_hedged_loci":len(test),"positive_test_loci":int(y.sum()),"exact_worlds":len(worlds),"endpoint":"MIXED_SPATIAL_CONTEXT_WORDS_BASE_EDGE_GROUND_LEVEL_NOT_PURE_LABEL_PLACEMENT","frozen_host_wrapper_result":frozen,"page_host_result":host,"raw_result":raw,"best_sensitivity":rows[0],"interpretation":"The GDT095 host-wrapper interaction does not transfer, while PAGE_HOST marginal trigrams show a low-capacity four-positive mixed spatial-context association slightly above raw strings.","claim_ceiling":"Archived annotation-stratum transfer only; no semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{ANN.name:sha(ANN),PARSED.name:sha(PARSED),"gdt095_result.json":sha(ROOT/"gdt095_result.json"),"gdt095_descriptor_token_manifest.tsv":sha(ROOT/"gdt095_descriptor_token_manifest.tsv")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{PRED.name:sha(PRED),SCORES.name:sha(SCORES),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"frozen_gain":frozen["gain_bits"],"best":rows[0]["representation"],"best_gain":rows[0]["gain_bits"],"worlds":len(worlds)},sort_keys=True))
if __name__=="__main__":main()
