#!/usr/bin/env python3
"""Independent aggregate and provenance validator for GDT382."""
import csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(n):return list(csv.DictReader((ART/n).open(),delimiter="\t"))
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");z=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  z[o[i:j]]=(i+j+1)/2;i=j
 return z
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return float("nan")
 q=rankdata(s);return float((q[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def bits(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def independent_token_rebuild(rows,oracle,endpoint):
 """Rebuild the local opaque-token model without importing the producer."""
 y=[int(x[endpoint]) for x in oracle];domains=defaultdict(list);collections=defaultdict(set);maxord=Counter()
 for i,x in enumerate(rows):domains[x["domain"]].append(i);collections[x["domain"]].add(x["collection_id"]);maxord[x["domain"]]=max(maxord[x["domain"]],int(x["record_ordinal"])+1)
 folds=[]
 for x in rows:
  d=x["domain"];sub=x["collection_id"] if len(collections[d])>1 else "BLOCK"+str(min(4,int(x["record_ordinal"])*5//max(1,maxord[d])));folds.append(d+"::"+sub)
 pred=[0.]*len(rows);base=[0.]*len(rows)
 for d,ids in domains.items():
  tc=Counter(y[i] for i in ids);tv=Counter(rows[i]["source_token_equality"] for i in ids);tvc=[Counter(),Counter()]
  for i in ids:tvc[y[i]][rows[i]["source_token_equality"]]+=1
  fg=defaultdict(list)
  for i in ids:fg[folds[i]].append(i)
  for f,test in fg.items():
   fc=Counter(y[i] for i in test);fv=Counter(rows[i]["source_token_equality"] for i in test);fvc=[Counter(),Counter()]
   for i in test:fvc[y[i]][rows[i]["source_token_equality"]]+=1
   n1=tc[1]-fc[1];n0=tc[0]-fc[0];V=sum(tv[k]>fv[k] for k in tv)+1
   # The frozen producer's constant baseline is itself a one-feature NB model
   # with vocabulary size one plus its unseen bucket, rather than a bare prior.
   b0=math.log((n1+1)/(n0+1))+math.log((n1+1)/(n1+2))-math.log((n0+1)/(n0+2));prior=1/(1+math.exp(-max(-30,min(30,b0))))
   for i in test:
    k=rows[i]["source_token_equality"];a=tvc[1][k]-fvc[1][k]+1;b=tvc[0][k]-fvc[0][k]+1;logit=math.log((n1+1)/(n0+1))+math.log(a/(n1+V))-math.log(b/(n0+V));pred[i]=1/(1+math.exp(-max(-30,min(30,logit))));base[i]=prior
 byauc=[];gain=0
 for d,ids in domains.items():
  yy=[y[i] for i in ids]
  if 0<sum(yy)<len(yy):byauc.append(auc(yy,[pred[i] for i in ids]));gain+=bits(yy,[base[i] for i in ids])-bits(yy,[pred[i] for i in ids])
 return float(np.mean(byauc)),gain
def main():
 checks=[]
 def ck(n,v):checks.append((n,bool(v)))
 r=json.loads((ART/"gdt382_result.json").read_text());ck("result_content_hash",r["content_hash"]==content(r));ck("status",r["status"]=="METHODOLOGY_AUDIT_COMPLETE")
 for p,h in r["inputs"].items():ck("input_hash:"+p,sha(ROOT/p)==h)
 for p,h in r["outputs"].items():ck("output_hash:"+p,sha(ROOT/p)==h)
 for p,h in r["documents"].items():ck("document_hash:"+p,sha(ROOT/p)==h)
 for p,h in r["implementation"].items():ck("implementation_hash:"+p,sha(ROOT/p)==h)
 rep=read("gdt382_representation_recovery.tsv");over=read("gdt382_overcontrol_audit.tsv");ctrl=read("gdt382_bound_free_controls.tsv");dc=read("gdt382_discovery_confirmation.tsv");ont=read("gdt382_ontology_audit.tsv");counter=read("gdt382_counterexamples.tsv")
 ck("representation_rows",len(rep)==72);ck("overcontrol_rows",len(over)==144);ck("bound_free_rows",len(ctrl)==96);ck("discovery_rows",len(dc)==42);ck("ontology_rows",len(ont)==2);ck("counterexample_rows",len(counter)==5)
 endpoints=r["endpoints"];reps=r["representations"]
 for e in endpoints:
  for regime in ["LOCAL","UNIVERSAL"]:
   a=next(x for x in rep if x["endpoint"]==e and x["representation"]=="SOURCE_TOKEN_EQUALITY" and x["regime"]==regime);b=next(x for x in rep if x["endpoint"]==e and x["representation"]=="DOMAIN_LOCAL_OPAQUE_ID" and x["regime"]==regime)
   ck("opaque_isomorphism:"+e+":"+regime,all(abs(float(a[k])-float(b[k]))<1e-9 for k in ["macro_auc","macro_ap","gain_bits","gain_vs_structure_bits"]))
 best={e:max((x for x in rep if x["endpoint"]==e and x["regime"]=="LOCAL"),key=lambda x:float(x["macro_auc"])) for e in endpoints};recover=sum(float(x["macro_auc"])>=.60 and float(x["gain_bits"])>0 for x in best.values());ck("six_base_recoverable",recover==r["base_endpoints_exploration_recoverable"]==6)
 bound=[x for x in ctrl if x["regime"]=="LOCAL" and x["encoding_mode"]!="BASE_ORACLE_BLIND"];ck("bound_total",len(bound)==r["bound_control_cells_total"]==42);ck("bound_recovered",sum(float(x["macro_auc"])>=.80 for x in bound)==r["bound_control_cells_auc_0_80"]==42)
 losses=[]
 for e in endpoints:
  for v in sorted({x["variable"] for x in over}):
   g=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="GRAMMAR_FEATURE");n=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="CONDITIONED_NUISANCE");losses.append((float(g["gain_bits"])-float(n["gain_bits"]),e,v))
 m=max(losses);ck("strongest_loss_bits",abs(m[0]-r["strongest_overcontrol_loss"]["bits"])<1e-8);ck("strongest_loss_identity",[m[1],m[2]]==[r["strongest_overcontrol_loss"]["endpoint"],r["strongest_overcontrol_loss"]["variable"]])
 gaps={e:max(float(x["macro_auc"]) for x in rep if x["endpoint"]==e and x["regime"]=="LOCAL")-max(float(x["macro_auc"]) for x in rep if x["endpoint"]==e and x["regime"]=="UNIVERSAL") for e in endpoints};ck("six_local_advantages",sum(v>.10 for v in gaps.values())==6);ck("joint_not_best",sum(best[e]["representation"]!="COMPOSITE_JOINT_STATE" for e in endpoints)==6)
 dm=r["decision_matrix"];ck("pipeline_validated",dm["CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING"]);ck("joint_mapping_not_homologous",dm["JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS"]);ck("overcontrol",dm["OVERCONTROL_DESTROYS_FUNCTION_SIGNAL"]);ck("universal_too_strict",dm["UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT"]);ck("bound_recoverable",not dm["BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD"]);ck("discovery_not_suppressed",not dm["DISCOVERY_CORRECTION_UNDERPOWERED"])
 n=0;bad=0;flags=set();encoded=[]
 with gzip.open(ART/"gdt382_voynichified_observation_layer.tsv.gz","rt",encoding="utf-8",newline="") as f:
  q=csv.DictReader(f,delimiter="\t")
  for x in q:
   encoded.append(x);n+=1;flags.add(x["encoder_used_oracle"]);bad+=("f84" in (x["domain"]+x["collection_id"]+x["record_id"]+x["element_key"]).lower())
 ck("encoded_rows",n==133183);ck("oracle_blind_flags",flags=={"0"});ck("no_f84_provenance",bad==0);ck("no_voynich_scoring",r["voynich_rows_read"]==0 and not r["voynich_scored"] and not any(r["f84"].values()))
 oracle_path=ROOT/next(p for p in r["inputs"] if p.endswith("gdt378_hidden_oracle.tsv.gz"));oracle_map={}
 with gzip.open(oracle_path,"rt",encoding="utf-8",newline="") as f:
  for x in csv.DictReader(f,delimiter="\t"):oracle_map[x["element_key"]]=x
 oracle=[oracle_map[x["element_key"]] for x in encoded];ck("oracle_key_join",len(oracle_map)==len(oracle)==133183)
 for e in endpoints:
  ma,gain=independent_token_rebuild(encoded,oracle,e);x=next(q for q in rep if q["endpoint"]==e and q["representation"]=="SOURCE_TOKEN_EQUALITY" and q["regime"]=="LOCAL")
  ck("independent_token_auc:"+e,abs(ma-float(x["macro_auc"]))<2e-6);ck("independent_token_gain:"+e,abs(gain-float(x["gain_bits"]))<1e-6)
 out={"schema":"GDT382_VALIDATION_V1","status":"PASS" if all(v for _,v in checks) else "FAIL","checks":len(checks),"passed":sum(v for _,v in checks),"details":{k:v for k,v in checks},"result_hash":sha(ART/"gdt382_result.json"),"validator_hash":sha(BASE/"src/validate_gdt382.py")};out["content_hash"]=content(out);(ART/"gdt382_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"passed":out["passed"],"checks":out["checks"]}))
 if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
