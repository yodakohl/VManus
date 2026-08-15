#!/usr/bin/env python3
"""Independent refit, null, and artifact validation for GDT137."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";INV=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";PRED=ROOT/"gdt137_prediction.json";SCORES=ROOT/"gdt137_panel_scores.tsv";FEATURES=ROOT/"gdt137_feature_scores.tsv";FOLDS=ROOT/"gdt137_folio_scores.tsv";CROSS=ROOT/"gdt137_cross_currier_scores.tsv";NULL=ROOT/"gdt137_null_results.tsv";RESULT=ROOT/"gdt137_result.json";OUT=ROOT/"gdt137_validation.json";REPS=("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3","COMPILER_SIGNATURE")
def read(p):
 with Path(p).open(encoding="utf8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def add3(c,s):
 s="^"+s+"$"
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def dist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k)
 return 1-sum(min(a[x],b[x])for x in k)/d if d else 0
def loss(y,p):p=np.clip(p,1e-12,1-1e-12);return-np.log2(np.where(y>0,p,1-p))
checks=[]
def check(n,v):checks.append({"check":n,"pass":bool(v)});assert v,n
freeze=json.loads(PRED.read_text());result=json.loads(RESULT.read_text());pages=read(INV);check("status",result["status"]=="HERBAL_PAGE_VISUAL_CONTENT_TRANSFER_NOT_SUPPORTED");check("panel",len(pages)==127 and len({r["physical_folio"]for r in pages})==63 and not any(r["page"].startswith("f84")for r in pages))
index={r["page"]:i for i,r in enumerate(pages)};source=[]
with SOURCE.open(encoding="utf8",newline="")as h:
 for row in csv.DictReader(h,delimiter="\t"):
  if row["page"].startswith("f84"):continue
  if row["page"]in index:source.append(row)
check("source",len(source)==5234 and set(r["page"]for r in source)==set(index)and not any(r["page"].startswith("f84")for r in source))
names=freeze["features"];y=np.array([[int(r[f])for f in names]for r in pages],float);panels={"ALL_12":list(range(12)),"PRIMARY_CAPACITY_8":[names.index(f)for f in freeze["primary_capacity_features"]],"CROSS_CURRIER_6":[names.index(f)for f in freeze["cross_currier_features"]]};bypage=defaultdict(list)
for r in source:bypage[r["page"]].append(r)
feat={rep:[]for rep in REPS};nuis=[];ml=max(int(r["formal_lines"])for r in pages);mg=max(int(r["formal_groups"])for r in pages);mp=max(int(r["catalogue_prose_lines"]or 0)for r in pages);ma=max(int(r["paragraph_starts"]or 0)for r in pages)
for page in pages:
 bundles={r:Counter()for r in REPS}
 for x in sorted(bypage[page["page"]],key=lambda r:(r["locus"],int(r["group_index"]))):bundles[REPS[0]]["H="+x["page_host"]]+=1;add3(bundles[REPS[1]],x["page_host"]);add3(bundles[REPS[2]],x["token"]);bundles[REPS[3]]["|".join((x["wrapper"],x["inner_d"],x["local_frame"],x["right_family"],x["dy_closure"],x["b3"]))]+=1
 for rep in REPS:feat[rep].append(bundles[rep])
 nuis.append(Counter({"CUR="+page["currier"]:1.,"HAND="+page["hand"]:1.,"PROFILE="+page["illustration_profile"]:1.,"LABEL="+page["catalogue_label_presence"]:1.,"PARA":int(page["paragraph_starts"]or 0)/ma,"LINES":int(page["formal_lines"])/ml,"GROUPS":int(page["formal_groups"])/mg,"PROSE":int(page["catalogue_prose_lines"]or 0)/mp}))
n=len(pages);folios=sorted({r["physical_folio"]for r in pages});fi={f:np.array([i for i,r in enumerate(pages)if r["physical_folio"]==f],int)for f in folios}
def matrix(rep=None,cross=False):
 w=np.zeros((n,n))
 for i,t in enumerate(pages):
  z=[]
  for j,r in enumerate(pages):
   if r["physical_folio"]==t["physical_folio"]or(cross and r["currier"]==t["currier"]):continue
   d=dist(nuis[i],nuis[j])+(dist(feat[rep][i],feat[rep][j])if rep else 0);z.append((d,r["page"],j))
  for d,_,j in sorted(z)[:7]:w[i,j]=1/(.1+d)
 return w
bw=matrix();rw={r:matrix(r)for r in REPS};bp=(bw@y+.5)/(bw.sum(1)[:,None]+1);bl=loss(y,bp);pred={r:(rw[r]@y+8*bp)/(rw[r].sum(1)[:,None]+8)for r in REPS};mloss={r:loss(y,pred[r])for r in REPS};rebuilt={}
for panel,cols in panels.items():
 for rep in REPS:
  gain=float((bl[:,cols]-mloss[rep][:,cols]).sum());fg=[float((bl[np.ix_(idx,cols)]-mloss[rep][np.ix_(idx,cols)]).sum())for idx in fi.values()];rebuilt[panel,rep]=(gain,sum(v>0 for v in fg),fg)
  stored=result["primary"].get(rep)if panel=="PRIMARY_CAPACITY_8"else None
  if stored:check("primary_"+rep,abs(gain-float(stored["gain_bits"]))<1e-9 and sum(v>0 for v in fg)==int(stored["positive_gain_folios"]))
feature_rebuild={}
for rep in REPS:
 for j,f in enumerate(names):feature_rebuild[f,rep]=float((bl[:,j]-mloss[rep][:,j]).sum())
# Forced opposite-Currier sensitivity.
cbw=matrix(cross=True);cb=(cbw@y+.5)/(cbw.sum(1)[:,None]+1);cbl=loss(y,cb);cross_rebuild={}
for rep in REPS:
 w=matrix(rep,cross=True);q=(w@y+8*cb)/(w.sum(1)[:,None]+8);m=loss(y,q);cols=panels["CROSS_CURRIER_6"];cross_rebuild[rep]=float((cbl[:,cols]-m[:,cols]).sum());check("cross_"+rep,abs(cross_rebuild[rep]-float(result["cross_currier"][rep]["gain_bits"]))<1e-9)
# Shared exact null.
obs={(p,r):rebuilt[p,r][0]for p in panels for r in REPS};fobs=feature_rebuild;local=Counter();mx=Counter();flocal=Counter();fm=0;strata=defaultdict(list)
for i,r in enumerate(pages):strata[r["currier"],r["hand"],r["illustration_profile"]].append(i)
rng=np.random.default_rng(137001)
for _ in range(10000):
 py=y.copy()
 for idx in strata.values():idx=np.array(idx,int);py[idx]=py[rng.permutation(idx)]
 pb=(bw@py+.5)/(bw.sum(1)[:,None]+1);pbl=loss(py,pb);g={};allf=[]
 for rep in REPS:
  q=(rw[rep]@py+8*pb)/(rw[rep].sum(1)[:,None]+8);pm=loss(py,q)
  for panel,cols in panels.items():v=float((pbl[:,cols]-pm[:,cols]).sum());g[panel,rep]=v;local[panel,rep]+=v>=obs[panel,rep]-1e-12
  for j,f in enumerate(names):v=float((pbl[:,j]-pm[:,j]).sum());flocal[f,rep]+=v>=fobs[f,rep]-1e-12;allf.append(v)
 for panel in panels:mx[panel]+=max(g[panel,r]for r in REPS)>=max(obs[panel,r]for r in REPS)-1e-12
 fm+=max(allf)>=max(fobs.values())-1e-12
for rep in REPS:
 stored=result["primary"][rep];check("null_"+rep,abs((local["PRIMARY_CAPACITY_8",rep]+1)/10001-float(stored["local_permutation_p"]))<1e-12 and abs((mx["PRIMARY_CAPACITY_8"]+1)/10001-float(stored["max_four_p"]))<1e-12 and abs((fm+1)/10001-float(stored["max_feature_model_p"]))<1e-12)
score_rows=read(SCORES);feature_rows=read(FEATURES);fold_rows=read(FOLDS);null_rows=read(NULL);check("row_counts",len(score_rows)==12 and len(feature_rows)==48 and len(fold_rows)==756 and len(null_rows)==12)
for r in score_rows:
 check("score_"+r["panel"]+r["representation"],abs(float(r["baseline_bits"])-float(r["held_bits"])-float(r["gain_bits"]))<2e-9 and abs(float(r["gain_bits"])-rebuilt[r["panel"],r["representation"]][0])<2e-9)
for r in feature_rows:check("feature_"+r["feature"]+r["representation"],abs(float(r["gain_bits"])-feature_rebuild[r["feature"],r["representation"]])<2e-9)
host=result["best_page_host_representation"];primary=result["primary"];g={"selector_paid_positive":float(primary[host]["selector_paid_gain_bits"])>0,"beats_raw_and_compiler":float(primary[host]["gain_bits"])>max(float(primary["RAW_CHAR3"]["gain_bits"]),float(primary["COMPILER_SIGNATURE"]["gain_bits"])),"positive_at_least_6_of_8_features":int(primary[host]["positive_gain_features"])>=6,"positive_at_least_35_of_63_folios":int(primary[host]["positive_gain_folios"])>=35,"cross_currier_panel_positive":cross_rebuild[host]>0,"max_four_p_le_005":float(primary[host]["max_four_p"])<=.05};check("gates",g==result["gates"])
check("input_hashes",all(sha(ROOT/name)==digest for name,digest in result["inputs"].items()));check("implementation_hashes",all(sha(ROOT/name)==digest for name,digest in result["implementation"].items()));check("output_hashes",all(sha(ROOT/name)==digest for name,digest in result["outputs"].items()));check("document_hashes",all(sha(ROOT/name)==digest for name,digest in result["documents"].items()));content=dict(result);digest=content.pop("result_content_sha256");check("content",csha(content)==digest)
v={"schema":"GDT137_VALIDATION_V1","status":"PASS_INDEPENDENT_REFIT_AND_NULL","checks":len(checks),"passed":sum(x["pass"]for x in checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"check_rows":checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":v["status"],"checks":v["checks"]},sort_keys=True))
