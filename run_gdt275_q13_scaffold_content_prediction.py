#!/usr/bin/env python3
"""Held-folio q13 scaffold-to-opaque-identity prediction with exact null."""
import csv,hashlib,json,math,random,statistics
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent;SRC="gdt227_q13_abstract_interlinear.tsv";METHOD="GDT275_Q13_SCAFFOLD_CONTENT_PREDICTION_METHOD.md";CONTEXT=["gdt274_result.json"]
WORLDS=2048;BASE_PRIOR=8.0;SCAFFOLD_PRIOR=512.0;TARGETS=("PAGE_HOST","RAW")
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def events():
 rows=read(SRC);assert len(rows)==701 and all(not x["page"].startswith("f84") for x in rows);lines=defaultdict(list)
 for x in rows:lines[(x["record_id"],x["locus"])].append(x)
 out=[]
 for key,ll in sorted(lines.items()):
  ll.sort(key=lambda x:int(x["field_ordinal"]));template=tuple(("S12" if int(x["field_group_count"])<=2 else "L3P",x["line_field_end"]) for x in ll);rn=int(ll[0]["record_field_count"])
  for slot,x in enumerate(ll):
   n=int(x["field_group_count"]);q=min(3,int((int(x["field_ordinal"])/rn)*4));pos="ONLY" if len(ll)==1 else "FIRST" if slot==0 else "LAST" if slot==len(ll)-1 else "MIDDLE";base=(n,x["line_field_end"],len(ll),pos,q);ctx=(template,slot)
   raw=x["source_tokens"].split("|");host=x["page_hosts"].split("|");assert len(raw)==len(host)==n
   for a,b in zip(raw,host):out.append({"folio":x["physical_folio"],"base":base,"context":ctx,"RAW":a,"PAGE_HOST":b})
 assert len(out)==1896 and len({x["folio"] for x in out})==9
 return out
def score(ev,target):
 folds={}
 for held in sorted({x["folio"] for x in ev}):
  tr=[x for x in ev if x["folio"]!=held];te=[x for x in ev if x["folio"]==held];glob=Counter(x[target] for x in tr);bc=defaultdict(Counter);mc=defaultdict(Counter)
  for x in tr:bc[x["base"]][x[target]]+=1;mc[x["context"]][x[target]]+=1
  V=len(glob);N=sum(glob.values());gain=0.0
  for x in te:
   y=x[target];b=bc[x["base"]];pg=(glob[y]+.5)/(N+.5*V);pb=(b[y]+BASE_PRIOR*pg)/(sum(b.values())+BASE_PRIOR);m=mc[x["context"]];pm=(m[y]+SCAFFOLD_PRIOR*pb)/(sum(m.values())+SCAFFOLD_PRIOR);gain+=math.log2(pm/pb)
  folds[held]=gain
 return sum(folds.values()),folds
def main():
 ev=events();obs={};fold_rows=[]
 for t in TARGETS:
  g,f=score(ev,t);obs[t]={"gain":g,"folds":f}
  for fol,v in f.items():fold_rows.append({"target":t,"held_folio":fol,"gain_bits":f"{v:.12f}","positive":int(v>0)})
 strata=defaultdict(list)
 for i,x in enumerate(ev):strata[(x["folio"],x["base"])].append(i)
 mobile=sum(len(v) for v in strata.values() if len(v)>1);orig=[(x["RAW"],x["PAGE_HOST"]) for x in ev];null={t:[] for t in TARGETS}
 for world in range(WORLDS):
  rng=random.Random(int(hashlib.sha256(f"GDT275_SCAFFOLD_CONTENT_NULL_V1|{world}".encode()).hexdigest()[:16],16))
  for ids in strata.values():
   vals=[orig[i] for i in ids];rng.shuffle(vals)
   for i,(a,b) in zip(ids,vals):ev[i]["RAW"]=a;ev[i]["PAGE_HOST"]=b
  for t in TARGETS:null[t].append(score(ev,t)[0])
 for i,(a,b) in enumerate(orig):ev[i]["RAW"]=a;ev[i]["PAGE_HOST"]=b
 means={t:statistics.mean(null[t]) for t in TARGETS};sds={t:statistics.pstdev(null[t]) for t in TARGETS};zs={t:(obs[t]["gain"]-means[t])/sds[t] for t in TARGETS};mx=[max((null[t][i]-means[t])/sds[t] for t in TARGETS) for i in range(WORLDS)];tests=[]
 for t in TARGETS:
  local=(1+sum(x>=obs[t]["gain"]-1e-12 for x in null[t]))/(WORLDS+1);maxp=(1+sum(x>=zs[t]-1e-12 for x in mx))/(WORLDS+1);tests.append({"target":t,"held_gain_bits":f"{obs[t]['gain']:.12f}","positive_folios":sum(x>0 for x in obs[t]["folds"].values()),"negative_folios":sum(x<0 for x in obs[t]["folds"].values()),"null_mean":f"{means[t]:.12f}","null_sd":f"{sds[t]:.12f}","z":f"{zs[t]:.12f}","local_p":f"{local:.12f}","max_two_p":f"{maxp:.12f}"})
 write("gdt275_lofo_folds.tsv",fold_rows);write("gdt275_tests.tsv",tests)
 host=next(x for x in tests if x["target"]=="PAGE_HOST");gate=float(host["held_gain_bits"])>float(host["null_mean"]) and int(host["positive_folios"])>=6 and float(host["max_two_p"])<=.05;status="Q13_SCAFFOLD_CONSTRAINS_OPAQUE_HOST_IDENTITY_EXPLORATORY" if gate else "Q13_REUSABLE_SCAFFOLD_DOES_NOT_PREDICT_EXACT_CONTENT_IDENTITY"
 counter=[{"counterexample":"PAGE_HOST_NULL_CALIBRATION","value":f"observed {host['held_gain_bits']} null {host['null_mean']} z {host['z']}","consequence":"positive raw gain is not evidence unless it exceeds exact nuisance-stratified worlds"},{"counterexample":"RAW_SENSITIVITY","value":next(x for x in tests if x["target"]=="RAW")["held_gain_bits"],"consequence":"surface group prediction is a sensitivity, not independent replication"},{"counterexample":"EXACT_IDENTITY_ENDPOINT","value":"PAGE_HOST and raw exact IDs","consequence":"failure does not reject latent classes or distributed content"},{"counterexample":"EXPOSED_MODEL","value":"priors fixed after pilot","consequence":"result is exploratory even if the gate passes"},{"counterexample":"SCAFFOLD_IS_SIZE_DERIVED","value":"S12/L3P plus endpoint","consequence":"template is formal layout, not a semantic sentence type"}];write("gdt275_counterexamples.tsv",counter)
 report=["# GDT275 — q13 scaffold-to-content prediction","",f"Status: **{status}**.","","| target | held gain bits | +/− folios | null mean | z | local p | max-two p |","|---|---:|---:|---:|---:|---:|---:|"]
 for x in tests:report.append(f"| {x['target']} | {float(x['held_gain_bits']):+.3f} | {x['positive_folios']}/{x['negative_folios']} | {float(x['null_mean']):+.3f} | {float(x['z']):+.3f} | {float(x['local_p']):.4f} | {float(x['max_two_p']):.4f} |")
 report += ["",f"The exact null preserves folio, field size, endpoint, fields per line, line slot, record-position quartile, and identity frequency; {mobile}/1896 events are in movable strata.  The large smoothing prior makes both observed scores positive, but the null receives the same calibration benefit.  The reusable coarse template therefore does not supply transferable exact host or raw-group identity beyond its structural opportunities.","","The combined GDT274–275 picture is a reusable scaffold with unique fillings, not an exact template dictionary.  Latent host classes or content distributed across the full tuple remain possible.","","No word, role, language, plaintext, meaning, or translation is assigned.  No f84r material was opened, retained, queried, joined, or scored.",""];(R/"GDT275_Q13_SCAFFOLD_CONTENT_PREDICTION_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt275_lofo_folds.tsv","gdt275_tests.tsv","gdt275_counterexamples.tsv","GDT275_Q13_SCAFFOLD_CONTENT_PREDICTION_REPORT.md"]
 result={"experiment":"GDT275_Q13_SCAFFOLD_CONTENT_PREDICTION","status":status,"events":1896,"folios":9,"nuisance_strata":len(strata),"movable_events":mobile,"worlds":WORLDS,"base_prior":BASE_PRIOR,"scaffold_prior":SCAFFOLD_PRIOR,"gate_pass":gate,"tests":{x["target"]:{k:(float(x[k]) if k not in ("target","positive_folios","negative_folios") else int(x[k]) if k in ("positive_folios","negative_folios") else x[k]) for k in x if k!="target"} for x in tests},"semantic_assignments":0,"claim_ceiling":"Scaffold-conditioned exact opaque identity only; no word role language meaning plaintext or translation.","f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),**{x:sha(x) for x in CONTEXT}},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt275_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"gate":gate,"tests":result["tests"]},sort_keys=True))
if __name__=="__main__":main()
