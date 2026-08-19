#!/usr/bin/env python3
"""Run the frozen GDT382 positive-control methodology audit; never read Voynich."""
from __future__ import annotations
import csv,gzip,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit";ART=BASE/"artifacts"
G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
ENC=ART/"gdt382_voynichified_observation_layer.tsv.gz";ORACLE=G378/"gdt378_hidden_oracle.tsv.gz";EF=ART/"gdt382_encoder_freeze.json";DF=ART/"gdt382_recovery_design_freeze.json"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
REPS=["SOURCE_TOKEN_EQUALITY","DOMAIN_LOCAL_OPAQUE_ID","HOST_IDENTITY","COMPOSITE_JOINT_STATE","COMPLETE_RENDERED_GROUP","FIELD_CONSTRUCTION_SPAN"]
MODES=["BASE_ORACLE_BLIND","FREE_TOKEN","PREFIX","SUFFIX","WRAPPER_ALTERNATION","BOUNDARY_CHOICE","POSITIONAL_ALTERNATION","ZERO_SUPPLETIVE"]
VARIABLES=["LINE_FIELD_POSITION","RECORD_RELATIVE_POSITION","BOUNDARY_CLOSURE","RECURRENCE","GLOBAL_LOCAL_FREQUENCY","RECORD_LENGTH","PREVIOUS_STATE","NEXT_STATE"]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hx(*x,n=10):return hashlib.sha256("\x1f".join(map(str,x)).encode()).hexdigest()[:n]
def content(d):
 q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with gzip.open(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with p.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sigmoid(x):return 1/(1+math.exp(-max(-30,min(30,x))))
def rankdata(x):
 a=np.asarray(x,float);o=np.argsort(a,kind="stable");r=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[o[j]]==a[o[i]]:j+=1
  r[o[i:j]]=(i+j+1)/2;i=j
 return r
def auc(y,s):
 y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return float("nan")
 rr=rankdata(s);return float((rr[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def ap(y,s):
 y=np.asarray(y,int);n=int(y.sum())
 if not n:return float("nan")
 o=np.argsort(-np.asarray(s),kind="stable");hit=0;tot=0.
 for k,i in enumerate(o,1):
  if y[i]:hit+=1;tot+=hit/k
 return tot/n
def bits(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9)
 return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def binint(v,cuts):
 v=int(v)
 for i,c in enumerate(cuts):
  if v<=c:return str(i)
 return str(len(cuts))

def prepare(rows):
 byfield=defaultdict(list);global_freq=Counter((r["domain"],r["source_token_equality"]) for r in rows)
 for i,r in enumerate(rows):byfield[r["field_id"]].append(i)
 field_exact={};field_skel={};field_len={}
 for fid,ids in byfield.items():
  ids.sort(key=lambda i:int(rows[i]["within_field_index"]));field_len[fid]=len(ids)
  field_exact[fid]="|".join(rows[i]["composite_joint_id"] for i in ids)
  field_skel[fid]="|".join(rows[i]["wrapper_state"]+":"+rows[i]["positional_state"]+":"+rows[i]["boundary_state"] for i in ids)
 feats={r:[] for r in REPS};struct=[];var={v:[] for v in VARIABLES}
 for x in rows:
  rg=x["rendered_group"];fid=x["field_id"]
  struct.append(("P="+x["positional_state"],"B="+x["boundary_state"],"R="+x["record_state"]))
  feats["SOURCE_TOKEN_EQUALITY"].append(("T="+x["source_token_equality"],))
  feats["DOMAIN_LOCAL_OPAQUE_ID"].append(("O="+x["domain_local_opaque_id"],))
  feats["HOST_IDENTITY"].append(("H="+x["host_id"],"HL="+str(len(x["host_id"]))))
  feats["COMPOSITE_JOINT_STATE"].append(("J="+x["composite_joint_id"],"W="+x["wrapper_state"],"P="+x["positional_state"],"B="+x["boundary_state"],"R="+x["record_state"],"V="+x["renderer_variant"],"HL="+str(len(x["host_id"]))))
  bigrams=sorted({rg[i:i+2] for i in range(max(0,len(rg)-1))})
  feats["COMPLETE_RENDERED_GROUP"].append(("G="+rg,"GP="+rg[:2],"GS="+rg[-2:],"GL="+str(len(rg)),"GB="+hx(*bigrams,n=8)))
  feats["FIELD_CONSTRUCTION_SPAN"].append(("FE="+field_exact[fid],"FS="+field_skel[fid],"FL="+str(field_len[fid]),"FI="+x["within_field_index"],"FB="+x["boundary_state"]))
  var["LINE_FIELD_POSITION"].append(("FI="+x["field_index"],"WF="+x["within_field_index"]))
  var["RECORD_RELATIVE_POSITION"].append(("P="+x["positional_state"],))
  var["BOUNDARY_CLOSURE"].append(("B="+x["boundary_state"],))
  var["RECURRENCE"].append(("REC="+binint(x["within_record_frequency"],[1,2,4]),))
  var["GLOBAL_LOCAL_FREQUENCY"].append(("GF="+binint(global_freq[(x["domain"],x["source_token_equality"])],[1,2,4,8,16,32,64]),))
  var["RECORD_LENGTH"].append(("RL="+binint(x["record_element_count"],[8,16,32,64]),))
  var["PREVIOUS_STATE"].append(("PREV="+x["previous_host"],))
  var["NEXT_STATE"].append(("NEXT="+x["next_host"],))
 return feats,struct,var

def fold_ids(rows):
 bydom=defaultdict(list)
 for i,r in enumerate(rows):bydom[r["domain"]].append(i)
 out=[]
 collections={d:sorted({rows[i]["collection_id"] for i in ids}) for d,ids in bydom.items()}
 maxima={d:max(int(rows[i]["record_ordinal"]) for i in ids)+1 for d,ids in bydom.items()}
 for r in rows:
  d=r["domain"]
  if len(collections[d])>1:sub=r["collection_id"]
  else:sub="BLOCK"+str(min(4,int(r["record_ordinal"])*5//max(1,maxima[d])))
  out.append(d+"::"+sub)
 return out

def nb_crossfit(y,features,rows,regime):
 n=len(y);pred=np.zeros(n,float)
 local=fold_ids(rows);folds=local if regime=="LOCAL" else [r["domain"] for r in rows]
 groups=defaultdict(list)
 for i,f in enumerate(folds):groups[f].append(i)
 # Exact algebraic replacement for repeatedly recounting every training fold:
 # build universe totals once and subtract the held group.  Vocabulary sizes
 # are likewise reduced by values occurring only in the held group.
 totals_class=Counter();held_class=Counter();totals=Counter();held=Counter();totval=Counter();heldval=Counter();vocab=defaultdict(set)
 for i,r in enumerate(rows):
  base=r["domain"] if regime=="LOCAL" else "ALL";excl=local[i] if regime=="LOCAL" else r["domain"];c=y[i]
  totals_class[(base,c)]+=1;held_class[(excl,c)]+=1
  for k,val in enumerate(features[i]):
   totals[(base,c,k,val)]+=1;held[(excl,c,k,val)]+=1;totval[(base,k,val)]+=1;heldval[(excl,k,val)]+=1;vocab[(base,k)].add(val)
 for fold,test in groups.items():
  held_domain=rows[test[0]]["domain"]
  base=held_domain if regime=="LOCAL" else "ALL";excl=fold if regime=="LOCAL" else held_domain
  n1=totals_class[(base,1)]-held_class[(excl,1)];n0=totals_class[(base,0)]-held_class[(excl,0)];prior=math.log((n1+1)/(n0+1))
  Vs=[]
  for k in range(len(features[0])):
   lost=sum(1 for val in vocab[(base,k)] if heldval[(excl,k,val)] and heldval[(excl,k,val)]==totval[(base,k,val)])
   Vs.append(len(vocab[(base,k)])-lost+1)
  for i in test:
   z=prior
   for k,val in enumerate(features[i]):
    V=Vs[k];a=totals[(base,1,k,val)]-held[(excl,1,k,val)]+1;b=totals[(base,0,k,val)]-held[(excl,0,k,val)]+1
    z+=math.log(a/(n1+V))-math.log(b/(n0+V))
   pred[i]=sigmoid(z)
 return pred

def aggregate(y,p,p0,rows,endpoint,rep,regime):
 bydom=defaultdict(list)
 for i,r in enumerate(rows):bydom[r["domain"]].append(i)
 folds=[]
 for d,ids in sorted(bydom.items()):
  yy=[y[i] for i in ids]
  if sum(yy)<1 or sum(yy)==len(yy):continue
  folds.append({"domain":d,"n":len(ids),"positives":sum(yy),"auc":auc(yy,[p[i] for i in ids]),"ap":ap(yy,[p[i] for i in ids]),"gain":bits(yy,[p0[i] for i in ids])-bits(yy,[p[i] for i in ids])})
 return {"endpoint":endpoint,"representation":rep,"regime":regime,"n":len(y),"positives":sum(y),"scored_domains":len(folds),"macro_auc":float(np.mean([x["auc"] for x in folds])) if folds else float("nan"),"macro_ap":float(np.mean([x["ap"] for x in folds])) if folds else float("nan"),"gain_bits":sum(x["gain"] for x in folds),"positive_gain_domains":sum(x["gain"]>0 for x in folds),"domains_auc_json":json.dumps({x["domain"]:round(x["auc"],9) for x in folds},sort_keys=True,separators=(",",":")),"domains_gain_json":json.dumps({x["domain"]:round(x["gain"],9) for x in folds},sort_keys=True,separators=(",",":"))}

def marker_features(base,rows,y,endpoint,mode):
 out=[]
 for i,(f,r) in enumerate(zip(base,rows)):
  z=list(f);mark="M"+hx("marker",r["domain"],endpoint,mode,n=6)
  if y[i]:
   generic={"FREE_TOKEN":"FREE_BEFORE","PREFIX":"PREFIX_MARKED","SUFFIX":"SUFFIX_MARKED","WRAPPER_ALTERNATION":"WRAPPER_MARKED","BOUNDARY_CHOICE":"BOUNDARY_MARKED","POSITIONAL_ALTERNATION":"POSITION_MARKED","ZERO_SUPPLETIVE":"SUPPLETIVE_STATE"}[mode]
   z.extend(("REALIZATION="+generic,"LOCAL_MARK="+mark))
  else:z.extend(("REALIZATION=UNMARKED","LOCAL_MARK=NONE"))
  out.append(tuple(z))
 return out

def main():
 ef=json.loads(EF.read_text());df=json.loads(DF.read_text());assert ef["status"]=="ORACLE_BLIND_ENCODER_FROZEN_BEFORE_RECOVERY" and df["status"]=="FROZEN_BEFORE_HIDDEN_ORACLE_EVALUATION" and not df["gdt381_outcome_used_to_design"]
 rows=read(ENC);oracle_raw=read(ORACLE);oracle_by_key={x["element_key"]:x for x in oracle_raw};assert len(oracle_by_key)==len(oracle_raw)==len(rows);oracle=[oracle_by_key[x["element_key"]] for x in rows];assert all("f84" not in (x["domain"]+x["collection_id"]+x["record_id"]+x["element_key"]).lower() for x in rows)
 feats,structure,var=prepare(rows);constant=[("CONST",) for _ in rows];Y={e:[int(x[e]) for x in oracle] for e in ENDPOINTS}
 rep_rows=[];preds={};baseline={}
 for endpoint in ENDPOINTS:
  y=Y[endpoint]
  for regime in ["UNIVERSAL","LOCAL"]:
   p0=nb_crossfit(y,constant,rows,regime);ps=nb_crossfit(y,structure,rows,regime);baseline[(endpoint,regime,"CONST")]=p0;baseline[(endpoint,regime,"STRUCT")]=ps
   for rep in REPS:
    p=nb_crossfit(y,feats[rep],rows,regime);preds[(endpoint,regime,rep)]=p;a=aggregate(y,p,p0,rows,endpoint,rep,regime);a["gain_vs_structure_bits"]=bits(y,ps)-bits(y,p);a["equality_isomorphism_check"]="SOURCE_EQUIVALENT" if rep in {"SOURCE_TOKEN_EQUALITY","DOMAIN_LOCAL_OPAQUE_ID","HOST_IDENTITY"} else "NOT_APPLICABLE";rep_rows.append(a)
 # Fixed-prediction held-label max-family diagnostic for local representation cells.
 strata=defaultdict(list)
 for i,r in enumerate(rows):strata[(r["domain"],r["collection_id"],r["record_state"],r["positional_state"],r["boundary_state"])].append(i)
 obs={};nullmax=[]
 for e in ENDPOINTS:
  for rep in REPS:
   a=next(x for x in rep_rows if x["endpoint"]==e and x["representation"]==rep and x["regime"]=="LOCAL");obs[(e,rep)]=a["macro_auc"]
 for world in range(256):
  rng=random.Random(382000+world);worldvals=[]
  for e in ENDPOINTS:
   yp=Y[e].copy()
   for ids in strata.values():
    vals=[yp[i] for i in ids];rng.shuffle(vals)
    for i,v in zip(ids,vals):yp[i]=v
   for rep in REPS:
    p=preds[(e,"LOCAL",rep)];by=defaultdict(list)
    for i,r in enumerate(rows):by[r["domain"]].append(i)
    av=[auc([yp[i] for i in ids],[p[i] for i in ids]) for ids in by.values() if 0<sum(yp[i] for i in ids)<len(ids)]
    if av:worldvals.append(float(np.mean(av)))
  nullmax.append(max(worldvals) if worldvals else .5)
 for a in rep_rows:
  if a["regime"]=="LOCAL":a["fixed_prediction_max_family_p"]=(1+sum(v>=a["macro_auc"] for v in nullmax))/257
  else:a["fixed_prediction_max_family_p"]="NA"
 # Overcontrol, composite representation, local folds.
 over=[]
 for endpoint in ENDPOINTS:
  y=Y[endpoint];rep=feats["COMPOSITE_JOINT_STATE"]
  for vn in VARIABLES:
   grammar=[tuple(list(rep[i])+list(var[vn][i])) for i in range(len(rows))];removed=rep;nu=var[vn]
   pconst=baseline[(endpoint,"LOCAL","CONST")];pg=nb_crossfit(y,grammar,rows,"LOCAL");pr=nb_crossfit(y,removed,rows,"LOCAL");pn=nb_crossfit(y,nu,rows,"LOCAL")
   for treatment,p,pbase in [("GRAMMAR_FEATURE",pg,pconst),("CONDITIONED_NUISANCE",pg,pn),("REMOVED",pr,pconst)]:
    a=aggregate(y,p,pbase,rows,endpoint,"COMPOSITE_JOINT_STATE","LOCAL");over.append({"endpoint":endpoint,"variable":vn,"treatment":treatment,"macro_auc":a["macro_auc"],"gain_bits":a["gain_bits"],"positive_gain_domains":a["positive_gain_domains"]})
 # Free/bound positive controls, both strict universal and domain-local.
 controls=[]
 for endpoint in ENDPOINTS:
  y=Y[endpoint]
  for mode in MODES:
   ff=feats["COMPOSITE_JOINT_STATE"] if mode=="BASE_ORACLE_BLIND" else marker_features(feats["COMPOSITE_JOINT_STATE"],rows,y,endpoint,mode)
   for regime in ["UNIVERSAL","LOCAL"]:
    p=nb_crossfit(y,ff,rows,regime);a=aggregate(y,p,baseline[(endpoint,regime,"CONST")],rows,endpoint,mode,regime);controls.append({"endpoint":endpoint,"encoding_mode":mode,"regime":regime,"macro_auc":a["macro_auc"],"gain_bits":a["gain_bits"],"positive_gain_domains":a["positive_gain_domains"],"scored_domains":a["scored_domains"]})
 # Discovery versus confirmation and predeclared development/confirmation split.
 dc=[]
 for endpoint in ENDPOINTS:
  cells=[x for x in rep_rows if x["endpoint"]==endpoint and x["regime"]=="LOCAL"]
  for x in cells:
   aucs=json.loads(x["domains_auc_json"]);gains=json.loads(x["domains_gain_json"]);passes=[d for d in aucs if aucs[d]>=.60 and gains[d]>0]
   explore=x["macro_auc"]>=.60 and x["gain_bits"]>0
   confirm=len(passes)>=3 and any(d in passes for d in ["COREMA","PCEEC2"]) and any(d in passes for d in ["CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"]) and float(x["fixed_prediction_max_family_p"])<=.05
   dc.append({"endpoint":endpoint,"representation":x["representation"],"exploration_pass":int(explore),"all_at_once_confirmation_pass":int(confirm),"passing_domains":len(passes),"max_family_p":x["fixed_prediction_max_family_p"]})
  # Representation selected only on fixed development domains, then untouched confirmation domains.
  def devscore(x):
   a=json.loads(x["domains_auc_json"]);return np.mean([a[d] for d in ["COREMA","CURIOUS_CURES","PCEEC2"] if d in a])
  selected=max(cells,key=lambda x:(devscore(x),x["gain_bits"],-REPS.index(x["representation"])))
  a=json.loads(selected["domains_auc_json"]);g=json.loads(selected["domains_gain_json"]);ok=[d for d in ["HARLEIAN_COOKERY","QUINTE_ESSENCE"] if d in a and a[d]>=.60 and g[d]>0]
  dc.append({"endpoint":endpoint,"representation":"PROSPECTIVE_SELECTED="+selected["representation"],"exploration_pass":"NA","all_at_once_confirmation_pass":int(len(ok)==2),"passing_domains":len(ok),"max_family_p":"PROSPECTIVE_TWO_DOMAIN"})
 # Ontology summaries use base composite and best representation separately.
 ont=[]
 mapping={"NATURAL_LANGUAGE_LIKE":ENDPOINTS,"TECHNICAL_NOTATION_LIKE":ENDPOINTS}
 for name,eps in mapping.items():
  vals=[]
  for e in eps:
   x=max((r for r in rep_rows if r["endpoint"]==e and r["regime"]=="LOCAL"),key=lambda r:r["macro_auc"]);vals.append(x)
  ont.append({"ontology":name,"endpoints":len(vals),"mean_best_macro_auc":float(np.mean([x["macro_auc"] for x in vals])),"endpoints_exploration_recoverable":sum(x["macro_auc"]>=.60 and x["gain_bits"]>0 for x in vals),"endpoints_confirmation_recoverable":sum(any(d["endpoint"]==x["endpoint"] and d["representation"]==x["representation"] and d["all_at_once_confirmation_pass"]==1 for d in dc) for x in vals),"interpretation":"CALIBRATION_ONLY_NOT_VOYNICH_ONTOLOGY_EVIDENCE"})
 # Counterexamples/decision matrix.
 bestbase={e:max((x for x in rep_rows if x["endpoint"]==e and x["regime"]=="LOCAL"),key=lambda x:x["macro_auc"]) for e in ENDPOINTS}
 comp_ok=sum(x["macro_auc"]>=.60 and x["gain_bits"]>0 for x in bestbase.values())
 bound_ok=sum(next(x for x in controls if x["endpoint"]==e and x["encoding_mode"]==m and x["regime"]=="LOCAL")["macro_auc"]>=.80 for e in ENDPOINTS for m in MODES[1:])
 # Loss when the most damaging nuisance treatment replaces grammar treatment.
 destructive=[]
 for e in ENDPOINTS:
  for v in VARIABLES:
   g=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="GRAMMAR_FEATURE")
   n=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="CONDITIONED_NUISANCE")
   destructive.append((g["gain_bits"]-n["gain_bits"],e,v,g,n))
 strongest=max(destructive,key=lambda x:x[0])
 decisions={
  "CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING":comp_ok>=4,
  "JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS":sum(bestbase[e]["representation"] not in {"COMPOSITE_JOINT_STATE"} for e in ENDPOINTS)>=4,
  "OVERCONTROL_DESTROYS_FUNCTION_SIGNAL":strongest[0]>50,
  "UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT":sum(max(x["macro_auc"] for x in rep_rows if x["endpoint"]==e and x["regime"]=="LOCAL")-max(x["macro_auc"] for x in rep_rows if x["endpoint"]==e and x["regime"]=="UNIVERSAL")>.10 for e in ENDPOINTS)>=3,
  "BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD":bound_ok<28,
  "DISCOVERY_CORRECTION_UNDERPOWERED":sum(x["exploration_pass"]==1 for x in dc if x["exploration_pass"]!="NA")>sum(x["all_at_once_confirmation_pass"]==1 for x in dc if x["exploration_pass"]!="NA")+6}
 write(ART/"gdt382_representation_recovery.tsv",rep_rows);write(ART/"gdt382_overcontrol_audit.tsv",over);write(ART/"gdt382_bound_free_controls.tsv",controls);write(ART/"gdt382_discovery_confirmation.tsv",dc);write(ART/"gdt382_ontology_audit.tsv",ont)
 counter=[{"item":"SOURCE_TOKEN_OPAQUE_ISOMORPHISM","finding":"SOURCE_TOKEN_EQUALITY and DOMAIN_LOCAL_OPAQUE_ID preserve exactly the same equality partition; different performance would be an implementation error."},{"item":"COMPOSITE_FRAGMENTATION","finding":"Exact composite and rendered identities can split one stable lexical identity across wrapper/position/renderer states."},{"item":"UNIVERSAL_REALIZATION_ASSUMPTION","finding":"Strict held-domain coefficients require shared realization statistics that the domain-local model intentionally relaxes."},{"item":"ORACLE_DRIVEN_BOUND_CONTROLS","finding":"Free/bound encodings are instrument ceilings deliberately generated from hidden truth; they are not natural corpus discoveries."},{"item":"FIXED_PREDICTION_MAXT","finding":"The max-family null permutes held labels against cross-fitted predictions; it does not rerun representation learning in every null world."}]
 write(ART/"gdt382_counterexamples.tsv",counter)
 outputs=[ART/x for x in ["gdt382_representation_recovery.tsv","gdt382_overcontrol_audit.tsv","gdt382_bound_free_controls.tsv","gdt382_discovery_confirmation.tsv","gdt382_ontology_audit.tsv","gdt382_counterexamples.tsv"]]
 result={"schema":"GDT382_RESULT_V1","status":"METHODOLOGY_AUDIT_COMPLETE","rows":len(rows),"records":len({(r['domain'],r['collection_id'],r['record_id']) for r in rows}),"domains":sorted({r["domain"] for r in rows}),"endpoints":ENDPOINTS,"representations":REPS,"base_endpoints_exploration_recoverable":comp_ok,"bound_control_cells_auc_0_80":bound_ok,"bound_control_cells_total":len(ENDPOINTS)*(len(MODES)-1),"strongest_overcontrol_loss":{"bits":strongest[0],"endpoint":strongest[1],"variable":strongest[2]},"decision_matrix":decisions,"methodological_consequence":"REPAIR_INSTRUMENT_BEFORE_NEXT_VOYNICH_OPERATOR" if (not decisions["CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING"] or decisions["JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS"] or decisions["OVERCONTROL_DESTROYS_FUNCTION_SIGNAL"] or decisions["UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT"] or decisions["BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD"]) else "EARLIER_NEGATIVES_MORE_INFORMATIVE","gdt381_outcome_used_to_tune":False,"voynich_rows_read":0,"voynich_scored":False,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [ENC,ORACLE,EF,DF]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outputs},"implementation":{str((BASE/'src/run_gdt382.py').relative_to(ROOT)):sha(BASE/'src/run_gdt382.py')},"claim_ceiling":"COMPARATOR_POSITIVE_CONTROL_METHODOLOGY_CALIBRATION_ONLY"}
 result["content_hash"]=content(result);(ART/"gdt382_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"recoverable":comp_ok,"bound":f"{bound_ok}/{result['bound_control_cells_total']}","decisions":decisions,"strongest_overcontrol":result["strongest_overcontrol_loss"]},sort_keys=True))
if __name__=="__main__":main()
