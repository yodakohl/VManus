#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,html,io,json,math,os,re,subprocess,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt387_cross_domain_parent_link_calibration";ART=BASE/"artifacts"
ENC=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz";P385=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_result.json";FREEZE=ART/"gdt387_pre_score_freeze.json"
COMMIT="bf79d1c46e8ef983a7347b0664d0d80243f32831";BUNDLE="c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714"
LEX={"after","afore","before","ere","when","whan","whanne","whenne","until","untill","til","till","while","whil","whiles","whilst"}
REPS=["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN"]
CLASS=["L_FAR"]+[f"L{i}" for i in range(13,0,-1)]+[f"R{i}" for i in range(1,14)]+["R_FAR"];K=len(CLASS)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def bundle(paths,root):
 h=hashlib.sha256()
 for p in sorted(paths,key=lambda q:str(q.relative_to(root))):h.update(str(p.relative_to(root)).encode());h.update(b"\0");h.update(p.read_bytes());h.update(b"\0")
 return h.hexdigest()
def readgz(p):
 with gzip.open(p,"rt",encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def writegz(p,rows):
 raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);f=io.TextIOWrapper(gz,encoding="utf-8",newline="")
 with f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sigmoid(x):x=np.clip(np.asarray(x,float),-30,30);return 1/(1+np.exp(-x))
def logit(x):x=np.clip(np.asarray(x,float),1e-7,1-1e-7);return np.log(x/(1-x))
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
def bits_binary(y,p):y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-15,1-1e-15);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def binint(v,cuts):
 v=int(v)
 for i,c in enumerate(cuts):
  if v<=c:return str(i)
 return str(len(cuts))
def combine(ps):return sigmoid(np.median(np.vstack([logit(p) for p in ps]),axis=0))
def combine2(a,b):return sigmoid((logit(a)+logit(b))/2)

def sexprs(text):
 stack=[]
 for m in re.finditer(r"\(|\)|[^\s()]+",text):
  tok=m.group()
  if tok=="(":stack.append([])
  elif tok==")":
   if not stack:continue
   node=stack.pop()
   if stack:stack[-1].append(node)
   else:yield node
  elif stack:stack[-1].append(tok)
def label(node):return node[0] if isinstance(node,list) and node and isinstance(node[0],str) else ""
def base(tag):return re.split(r"[-=]",tag)[0]
def canon(token):
 token=html.unescape(token).lower().replace("[th]","þ").replace("[gh]","ȝ").replace("þ","th").replace("ð","th").replace("ȝ","y");token=unicodedata.normalize("NFKD",token);return "".join(ch for ch in token if ch.isalpha())
def terminals(node,out):
 if not isinstance(node,list) or not node:return
 if len(node)==2 and isinstance(node[1],str):out.append({"node":node,"pos":label(node),"raw":node[1],"canon":canon(node[1])});return
 for c in node[1:] if label(node) else node:
  if isinstance(c,list):terminals(c,out)
def dependencies(roots,visible):
 ids={id(x["node"]):i for i,x in enumerate(visible)};gov={}
 def walk(node):
  if id(node) in ids:return ids[id(node)]
  kids=[c for c in (node[1:] if label(node) else node) if isinstance(c,list)];vals=[(c,walk(c)) for c in kids];vals=[x for x in vals if x[1] is not None]
  if not vals:return None
  tag=base(label(node));ct=lambda x:base(label(x[0]))
  if tag in {"IP","VP","RRC"}:pref=[x for x in vals if ct(x).startswith(("VB","MD","BE","HV","DO"))] or [x for x in vals if ct(x) in {"VP","IP"}] or vals
  elif tag in {"NP","NX"}:pref=[x for x in reversed(vals) if ct(x).startswith(("N","PRO","ONE","Q"))] or list(reversed(vals))
  elif tag=="PP":pref=[x for x in vals if ct(x) in {"P","RP"}] or vals
  elif tag=="CP":pref=[x for x in vals if ct(x) in {"IP","VP"}] or list(reversed(vals))
  elif tag in {"ADJP","ADVP"}:pref=list(reversed(vals))
  else:pref=vals
  head=pref[0][1]
  for _,child in vals:
   if child!=head and child not in gov:gov[child]=head
  return head
 heads=[walk(r) for r in roots]
 for head,prior in zip(heads[1:],heads[:-1]):
  if head is not None and prior is not None and head not in gov:gov[head]=prior
 return gov
def dclass(d):
 if d<-13:return 0
 if d<0:return 14+d
 if d<=13:return 13+d
 return 27

def build_oracle(src,obskeys):
 out=[];allkeys=set()
 for path in sorted((src/"data/parsed").glob("*.psd")):
  kept=0;ordinal=0
  for form in sexprs(path.read_text(encoding="utf-8",errors="replace")):
   roots=[x for x in form if isinstance(x,list) and label(x) not in {"CODE","METADATA","ID"}]
   if not roots:continue
   ts=[]
   for root in roots:terminals(root,ts)
   visible=[x for x in ts if x["pos"] not in {"PUNC","CODE","ID"} and x["canon"] and not x["raw"].startswith("*") and x["raw"]!="0"]
   if len(visible)<3:continue
   ordinal+=1;kept+=1
   if kept>12:break
   gov=dependencies(roots,visible);keys=[]
   for j in range(len(visible)):
    rec=f"{path.stem}:{ordinal}:C{j//180+1}" if len(visible)>180 else f"{path.stem}:{ordinal}";keys.append(f"PCEEC2:{path.stem}:{rec}:{j%180+1}");allkeys.add(keys[-1])
   for j,g in gov.items():
    if j//180!=g//180 or keys[j] not in obskeys or keys[g] not in obskeys:continue
    d=g-j;out.append({"element_key":keys[j],"source_file":path.stem,"record_id":keys[j].rsplit(":",1)[0].split(":",2)[2],"element_ordinal":j%180+1,"anonymous_role_y":int(visible[j]["canon"] in LEX),"governor_key":keys[g],"governor_ordinal":g%180+1,"signed_distance":d,"distance_class":CLASS[dclass(d)]})
 return out,allkeys

def prepare(rows):
 byrec=defaultdict(list)
 for i,r in enumerate(rows):byrec[r["record_id"]].append(i)
 rep={k:[None]*len(rows) for k in REPS};channels=[None]*len(rows);strata=[None]*len(rows)
 for ids in byrec.values():
  ids.sort(key=lambda i:int(rows[i]["element_ordinal"]))
  for j,i in enumerate(ids):
   r=rows[i];span=[rows[x] for x in ids[max(0,j-2):j]]+[r];g=r["rendered_group"]
   rep["HOST_IDENTITY"][i]=("H="+r["host_id"],"HL="+str(len(r["host_id"])))
   rep["COMPLETE_RENDERED_GROUP"][i]=("G="+g,"GP="+g[:2],"GS="+g[-2:],"GL="+str(len(g)))
   rep["CONSTRUCTION_STATE"][i]=("W="+r["wrapper_state"],"P="+r["positional_state"],"B="+r["boundary_state"],"R="+r["record_state"],"V="+r["renderer_variant"],"WF="+r["within_field_index"])
   rep["COMPOSITE_JOINT_STATE"][i]=("J="+r["composite_joint_id"],)
   rep["SHORT_CONSTRUCTION_SPAN"][i]=("SS="+"|".join(x["wrapper_state"]+x["boundary_state"]+x["renderer_variant"] for x in span),"SH="+"|".join(x["host_id"] for x in span))
   rb=binint(r["within_record_frequency"],[1,2,4]);rl=binint(r["record_element_count"],[8,16,32,64]);fi=binint(r["field_index"],[0,1,2,4,8]);wi=binint(r["within_field_index"],[0,1,2,4,8])
   channels[i]=("C="+rb,"FI="+r["field_index"],"WF="+r["within_field_index"],"P="+r["positional_state"],"B="+r["boundary_state"],"PREV="+r["previous_host"],"RL="+rl)
   strata[i]=(r["positional_state"],r["boundary_state"],fi,wi,rl,rb)
 return rep,channels,strata
def nb(y,features,folds,tokens=None):
 y=np.asarray(y,int);pred=np.zeros(len(y));groups=defaultdict(list)
 for i,f in enumerate(folds):groups[f].append(i)
 for held,test in groups.items():
  train=[i for i,f in enumerate(folds) if f!=held];gf=Counter(tokens[i] for i in train) if tokens else None
  def ff(i):return (("F="+binint(gf[tokens[i]],[1,2,4,8,16,32,64]),) if tokens else ())+tuple(features[i])
  vals={i:ff(i) for i in train+test};tc=Counter(y[i] for i in train);tot=Counter();voc=defaultdict(set)
  for i in train:
   for k,v in enumerate(vals[i]):tot[(y[i],k,v)]+=1;voc[k].add(v)
  n1,n0=tc[1],tc[0];prior=math.log((n1+1)/(n0+1));vs=[len(voc[k])+1 for k in range(len(vals[train[0]]))]
  for i in test:
   z=prior
   for k,v in enumerate(vals[i]):z+=math.log((tot[(1,k,v)]+1)/(n1+vs[k]))-math.log((tot[(0,k,v)]+1)/(n0+vs[k]))
   pred[i]=float(sigmoid(z))
 return pred
def target_crossfit(y,role,strata,folds,tokens):
 n=len(y);p0=np.zeros((n,K));q0=np.zeros((n,K));q1=np.zeros((n,K));evals=[None]*n
 for held in sorted(set(folds)):
  tr=[i for i,f in enumerate(folds) if f!=held];te=[i for i,f in enumerate(folds) if f==held];gf=Counter(tokens[i] for i in tr);ss={i:tuple(strata[i])+(binint(gf[tokens[i]],[1,2,4,8,16,32,64]),) for i in tr+te};gy=np.bincount(y[tr],minlength=K);gp=(gy+1)/(len(tr)+K);sc=Counter();src=Counter();rc={0:Counter(),1:Counter()};rn={0:Counter(),1:Counter()};rgy={0:np.zeros(K,int),1:np.zeros(K,int)};rgn={0:0,1:0}
  for i in tr:
   s=ss[i];v=int(y[i]);z=int(role[i]);sc[s]+=1;src[(s,v)]+=1;rn[z][s]+=1;rc[z][(s,v)]+=1;rgy[z][v]+=1;rgn[z]+=1
  rp={z:(rgy[z]+1)/(rgn[z]+K) if rgn[z] else gp for z in [0,1]}
  for i in te:
   s=ss[i];evals[i]=s;p0[i]=(np.array([src[(s,k)] for k in range(K)])+8*gp)/(sc[s]+8)
   for z,dest in [(0,q0),(1,q1)]:dest[i]=(np.array([rc[z][(s,k)] for k in range(K)])+8*rp[z])/(rn[z][s]+8)
 return p0,q0,q1,evals
def exact_probs(p,yclass,class_counts,present):
 den=np.maximum((p*present).sum(axis=1),1e-15);return np.clip(p[np.arange(len(yclass)),yclass]/class_counts/den,1e-15,1)
def target_metrics(rows,p,records):
 top=0;rr=[];ranks=[]
 for i,r in enumerate(rows):
  cand=records[r["record_id"]];scores=[]
  for j in cand:
   if j==int(r["element_ordinal"]):continue
   c=dclass(j-int(r["element_ordinal"]));scores.append((float(p[i,c])/sum(dclass(x-int(r["element_ordinal"]))==c for x in cand if x!=int(r["element_ordinal"])),j))
  scores.sort(key=lambda x:(-x[0],x[1]));rank=1+next(k for k,x in enumerate(scores) if x[1]==int(r["governor_ordinal"]));ranks.append(rank);top+=rank==1;rr.append(1/rank)
 return top/len(rows),float(np.mean(rr)),ranks

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze["status"]=="FROZEN_BEFORE_SCORING" and not any(freeze["f84"].values())
 env=os.environ.get("GDT387_PCEEC2_DIR");assert env,"set GDT387_PCEEC2_DIR";src=Path(env);files=list((src/"data/parsed").glob("*.psd"));assert len(files)==84 and subprocess.check_output(["git","-C",str(src),"rev-parse","HEAD"],text=True).strip()==COMMIT and bundle(files,src)==BUNDLE
 allrows=[r for r in readgz(ENC) if r["domain"]=="PCEEC2"];assert len(allrows)==27518;obs={r["element_key"] for r in allrows};oracle,allkeys=build_oracle(src,obs);assert len(obs-allkeys)==0 and len(allkeys-obs)==2
 om={r["element_key"]:r for r in oracle};rows=[r for r in allrows if r["element_key"] in om];assert len({r["collection_id"] for r in rows})==84
 for r in rows:r.update(om[r["element_key"]])
 role=np.array([int(r["anonymous_role_y"]) for r in rows]);assert role.sum()==110 and len({r["collection_id"] for r,z in zip(rows,role) if z})==47
 rep,ch,strata=prepare(rows);folds=[r["collection_id"] for r in rows];const=[("CONST",)]*len(rows);pbase_role=nb(role,const,folds);local=[nb(role,rep[x],folds) for x in REPS];pchannel=nb(role,ch,folds,[r["source_token_equality"] for r in rows]);prole=combine2(combine(local),pchannel)
 y=np.array([CLASS.index(r["distance_class"]) for r in rows]);p0,q0,q1,evals=target_crossfit(y,role,strata,folds,[r["source_token_equality"] for r in rows]);pfull=(1-prole[:,None])*q0+prole[:,None]*q1
 records=defaultdict(list)
 for r in allrows:records[r["record_id"]].append(int(r["element_ordinal"]))
 counts=np.zeros(len(rows));present=np.zeros((len(rows),K),float)
 for i,r in enumerate(rows):
  cs=Counter(dclass(x-int(r["element_ordinal"])) for x in records[r["record_id"]] if x!=int(r["element_ordinal"]));counts[i]=cs[y[i]]
  for k in cs:present[i,k]=1
 true0=exact_probs(p0,y,counts,present);true1=exact_probs(pfull,y,counts,present);source_bits=float(-np.log2(true0).sum());full_bits=float(-np.log2(true1).sum());gain=source_bits-full_bits
 st1,smrr,srank=target_metrics(rows,p0,records);ft1,fmrr,frank=target_metrics(rows,pfull,records)
 folds_out=[];positive=0
 for f in sorted(set(folds)):
  ids=[i for i,x in enumerate(folds) if x==f];g=float(np.log2(true1[ids]).sum()-np.log2(true0[ids]).sum());positive+=g>0;folds_out.append({"held_file":f,"n":len(ids),"role_pivots":int(role[ids].sum()),"source_bits":float(-np.log2(true0[ids]).sum()),"role_bits":float(-np.log2(true1[ids]).sum()),"gain_bits":g,"source_top1":float(np.mean(np.array(srank)[ids]==1)),"role_top1":float(np.mean(np.array(frank)[ids]==1)),"source_mrr":float(np.mean(1/np.array(srank)[ids])),"role_mrr":float(np.mean(1/np.array(frank)[ids]))})
 groups=defaultdict(list)
 for i,(f,s) in enumerate(zip(folds,evals)):groups[(f,s)].append(i)
 mobile=np.zeros(len(rows),bool)
 for ids in groups.values():
  if len(ids)>1 and len({round(float(prole[i]),12) for i in ids})>1:mobile[ids]=True
 base_order=np.array(sorted(range(len(rows)),key=lambda i:(folds[i],evals[i])));gid=np.zeros(len(rows),int)
 for z,ids in enumerate(groups.values()):gid[ids]=z
 rng=np.random.default_rng(3872048);null=[]
 for world in range(2048):
  donor=np.lexsort((rng.random(len(rows)),gid));perm=np.empty(len(rows),int);perm[np.argsort(gid,kind="stable")]=donor;pp=prole[perm];p=(1-pp[:,None])*q0+pp[:,None]*q1;tp=exact_probs(p,y,counts,present);null.append({"world":world,"gain_bits":source_bits-float(-np.log2(tp).sum())})
 pval=(1+sum(float(x["gain_bits"])>=gain for x in null))/2049
 role_gain=bits_binary(role,pbase_role)-bits_binary(role,prole);mrr_delta=fmrr-smrr;gate=bool(role.sum()>=100 and len({folds[i] for i in range(len(rows)) if role[i]})>=40 and auc(role,prole)>=.65 and role_gain>0 and gain>0 and positive>=42 and mrr_delta>=0 and mobile.mean()>=.2 and pval<=.05)
 score=[{"route_id":"CMP_XDOMAIN_01","n":len(rows),"source_files":len(set(folds)),"role_pivots":int(role.sum()),"role_files":len({folds[i] for i in range(len(rows)) if role[i]}),"role_auc":auc(role,prole),"role_gain_bits":role_gain,"source_governor_bits":source_bits,"role_governor_bits":full_bits,"governor_gain_bits":gain,"positive_files":positive,"source_target_top1":st1,"role_target_top1":ft1,"source_target_mrr":smrr,"role_target_mrr":fmrr,"target_mrr_delta":mrr_delta,"mobile_rows":int(mobile.sum()),"mobile_fraction":float(mobile.mean()),"permutation_p":pval,"gate_pass":int(gate)}]
 pred=[]
 for i,r in enumerate(rows):pred.append({"element_key":r["element_key"],"held_file":folds[i],"anonymous_role_y":int(role[i]),"distance_class":r["distance_class"],"governor_key":r["governor_key"],"p_role_baseline":pbase_role[i],"p_role":prole[i],"source_true_target_probability":true0[i],"role_true_target_probability":true1[i],"source_target_rank":srank[i],"role_target_rank":frank[i],"null_mobile":int(mobile[i])})
 counter=sorted(({"element_key":rows[i]["element_key"],"held_file":folds[i],"distance_class":rows[i]["distance_class"],"source_target_rank":srank[i],"role_target_rank":frank[i],"role_added_log2_true_probability":math.log2(true1[i]/true0[i])} for i in range(len(rows)) if role[i]),key=lambda x:x["role_added_log2_true_probability"])[:30]
 writegz(ART/"gdt387_hidden_governor_oracle.tsv.gz",oracle);write(ART/"gdt387_route_score.tsv",score);write(ART/"gdt387_file_folds.tsv",folds_out);write(ART/"gdt387_null_worlds.tsv",null);writegz(ART/"gdt387_predictions.tsv.gz",pred);write(ART/"gdt387_counterexamples.tsv",counter)
 outs=[ART/x for x in ["gdt387_hidden_governor_oracle.tsv.gz","gdt387_route_score.tsv","gdt387_file_folds.tsv","gdt387_null_worlds.tsv","gdt387_predictions.tsv.gz","gdt387_counterexamples.tsv"]];impl=[BASE/x for x in ["src/freeze.py","src/validate_freeze.py","src/run.py","src/validate.py"]]
 result={"schema":"GDT387_RESULT_V1","status":"CROSS_DOMAIN_PARENT_LINK_SIGNATURE_SUPPORTED" if gate else "CROSS_DOMAIN_PARENT_LINK_SIGNATURE_NOT_SUPPORTED","route":score[0],"pceec2_rows":27518,"scored_governor_edges":len(rows),"root_or_unmapped_rows":27518-len(rows),"source_files":84,"voynich_rows_read":0,"semantic_state":"COMPARATOR_ONLY","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [ENC,P385,FREEZE]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outs},"implementation":{str(p.relative_to(ROOT)):sha(p) for p in impl},"source":{"url":"https://github.com/beatrice57/pceec2","commit":COMMIT,"bundle_sha256":BUNDLE},"claim_ceiling":"CROSS_DOMAIN_COMPARATOR_RELATION_CALIBRATION_ONLY"};result["content_hash"]=content(result);(ART/"gdt387_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"route":score[0]},sort_keys=True))
if __name__=="__main__":main()
