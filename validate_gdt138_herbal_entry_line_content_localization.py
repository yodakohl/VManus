#!/usr/bin/env python3
"""Independent window refit/null validation for GDT138."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";VISUAL=ROOT/"gdt137_herbal_visual_feature_inventory.tsv";WIN=ROOT/"gdt138_line_window_inventory.tsv";FREEZE=ROOT/"gdt138_prediction.json";SCORES=ROOT/"gdt138_window_scores.tsv";FEATURES=ROOT/"gdt138_feature_scores.tsv";FOLDS=ROOT/"gdt138_folio_scores.tsv";CROSS=ROOT/"gdt138_cross_currier_scores.tsv";NULL=ROOT/"gdt138_null_results.tsv";RESULT=ROOT/"gdt138_result.json";OUT=ROOT/"gdt138_validation.json";WINDOWS=("FIRST_LINE","BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE");REPS=("PAGE_HOST_IDENTITY","PAGE_HOST_CHAR3","RAW_CHAR3");COMBOS=tuple((w,r)for w in WINDOWS for r in REPS)
def read(p):
 with Path(p).open(encoding="utf8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def order(x):return int(re.search(r"\.(\d+)$",x).group(1))
def add3(c,s):
 s="^"+s+"$"
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def dist(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x])for x in k)
 return 1-sum(min(a[x],b[x])for x in k)/d if d else 0
def loss(y,p):p=np.clip(p,1e-12,1-1e-12);return-np.log2(np.where(y>0,p,1-p))
checks=[]
def check(n,v):checks.append({"check":n,"pass":bool(v)});assert v,n
freeze=json.loads(FREEZE.read_text());result=json.loads(RESULT.read_text());visual={r["page"]:r for r in read(VISUAL)};wins=read(WIN);pages=[visual[r["page"]]for r in wins];wmap={r["page"]:r for r in wins};check("status",result["status"]=="HERBAL_ENTRY_LINE_CONTENT_LOCALIZATION_NOT_SUPPORTED");check("panel",len(pages)==126 and len({r["physical_folio"]for r in pages})==62 and not any(r["page"].startswith("f84")for r in pages))
pidx={r["page"]:i for i,r in enumerate(pages)};source=[]
with SOURCE.open(encoding="utf8",newline="")as h:
 for row in csv.DictReader(h,delimiter="\t"):
  if row["page"].startswith("f84"):continue
  if row["page"]in pidx:source.append(row)
check("source",len(source)==5227 and set(r["page"]for r in source)==set(pidx))
primary=freeze["primary_features"];crossnames=freeze["cross_currier_features"];names=list(dict.fromkeys(primary+crossnames));y=np.array([[int(r[f])for f in names]for r in pages],float);panels={"PRIMARY_8":[names.index(f)for f in primary],"CROSS_CURRIER_6":[names.index(f)for f in crossnames]};bypage=defaultdict(lambda:defaultdict(list))
for r in source:bypage[r["page"]][r["locus"]].append(r)
feat={c:[]for c in COMBOS};nuis=[];ma=max(int(r["paragraph_starts"]or 0)for r in pages);ml=max(int(r["formal_lines"])for r in pages);mg=max(int(r["formal_groups"])for r in pages);mp=max(int(r["catalogue_prose_lines"]or 0)for r in pages)
for page in pages:
 loci=sorted(bypage[page["page"]],key=order);check("line_bind_"+page["page"],loci[0]==wmap[page["page"]]["first_locus"]and loci[-1]==wmap[page["page"]]["last_locus"]);sets={"FIRST_LINE":{loci[0]},"BODY_AFTER_FIRST":set(loci[1:]),"LAST_LINE":{loci[-1]},"ALL_PAGE":set(loci)}
 for window in WINDOWS:
  b={r:Counter()for r in REPS}
  for locus in loci:
   if locus not in sets[window]:continue
   for x in sorted(bypage[page["page"]][locus],key=lambda r:int(r["group_index"])):b[REPS[0]]["H="+x["page_host"]]+=1;add3(b[REPS[1]],x["page_host"]);add3(b[REPS[2]],x["token"])
  for rep in REPS:feat[window,rep].append(b[rep])
 nuis.append(Counter({"CUR="+page["currier"]:1.,"HAND="+page["hand"]:1.,"PROFILE="+page["illustration_profile"]:1.,"LABEL="+page["catalogue_label_presence"]:1.,"PARA":int(page["paragraph_starts"]or 0)/ma,"LINES":int(page["formal_lines"])/ml,"GROUPS":int(page["formal_groups"])/mg,"PROSE":int(page["catalogue_prose_lines"]or 0)/mp}))
n=len(pages);folios=sorted({r["physical_folio"]for r in pages});fi={f:np.array([i for i,r in enumerate(pages)if r["physical_folio"]==f],int)for f in folios}
def matrix(combo=None,cross=False):
 w=np.zeros((n,n))
 for i,t in enumerate(pages):
  z=[]
  for j,r in enumerate(pages):
   if r["physical_folio"]==t["physical_folio"]or(cross and r["currier"]==t["currier"]):continue
   d=dist(nuis[i],nuis[j])+(dist(feat[combo][i],feat[combo][j])if combo else 0);z.append((d,r["page"],j))
  for d,_,j in sorted(z)[:7]:w[i,j]=1/(.1+d)
 return w
bw=matrix();cw={c:matrix(c)for c in COMBOS};bp=(bw@y+.5)/(bw.sum(1)[:,None]+1);bl=loss(y,bp);pred={c:(cw[c]@y+8*bp)/(cw[c].sum(1)[:,None]+8)for c in COMBOS};mloss={c:loss(y,pred[c])for c in COMBOS};rebuilt={};fbuild={}
for combo in COMBOS:
 for panel,cols in panels.items():
  gain=float((bl[:,cols]-mloss[combo][:,cols]).sum());fg=[float((bl[np.ix_(idx,cols)]-mloss[combo][np.ix_(idx,cols)]).sum())for idx in fi.values()];rebuilt[panel,combo]=(gain,sum(v>0 for v in fg))
 for j,name in enumerate(names):fbuild[name,combo]=float((bl[:,j]-mloss[combo][:,j]).sum())
cbw=matrix(cross=True);cb=(cbw@y+.5)/(cbw.sum(1)[:,None]+1);cbl=loss(y,cb);crossbuild={}
for combo in COMBOS:
 w=matrix(combo,cross=True);q=(w@y+8*cb)/(w.sum(1)[:,None]+8);m=loss(y,q);cols=panels["CROSS_CURRIER_6"];crossbuild[combo]=float((cbl[:,cols]-m[:,cols]).sum())
stored=result["primary_scores"]
for combo in COMBOS:
 row=stored[combo[0]][combo[1]];check("score_"+combo[0]+combo[1],abs(float(row["gain_bits"])-rebuilt["PRIMARY_8",combo][0])<1e-9 and int(row["positive_gain_folios"])==rebuilt["PRIMARY_8",combo][1]);check("cross_"+combo[0]+combo[1],abs(float(result["cross_currier"][combo[0]][combo[1]]["gain_bits"])-crossbuild[combo])<1e-9)
# Exact shared null.
obs={(panel,c):rebuilt[panel,c][0]for panel in panels for c in COMBOS};local=Counter();mx=Counter();flocal=Counter();fm=0;strata=defaultdict(list)
for i,r in enumerate(pages):strata[r["currier"],r["hand"],r["illustration_profile"]].append(i)
rng=np.random.default_rng(138001)
for _ in range(10000):
 py=y.copy()
 for idx in strata.values():idx=np.array(idx,int);py[idx]=py[rng.permutation(idx)]
 pb=(bw@py+.5)/(bw.sum(1)[:,None]+1);pbl=loss(py,pb);g={};allf=[]
 for combo in COMBOS:
  q=(cw[combo]@py+8*pb)/(cw[combo].sum(1)[:,None]+8);m=loss(py,q)
  for panel,cols in panels.items():v=float((pbl[:,cols]-m[:,cols]).sum());g[panel,combo]=v;local[panel,combo]+=v>=obs[panel,combo]-1e-12
  for j,name in enumerate(names):v=float((pbl[:,j]-m[:,j]).sum());flocal[name,combo]+=v>=fbuild[name,combo]-1e-12;allf.append(v)
 for panel in panels:mx[panel]+=max(g[panel,c]for c in COMBOS)>=max(obs[panel,c]for c in COMBOS)-1e-12
 fm+=max(allf)>=max(fbuild.values())-1e-12
first=("FIRST_LINE",result["first_line_host_representation"]);row=stored[first[0]][first[1]];check("primary_null",abs((local["PRIMARY_8",first]+1)/10001-float(row["local_permutation_p"]))<1e-12 and abs((mx["PRIMARY_8"]+1)/10001-float(row["max_12_p"]))<1e-12 and abs((fm+1)/10001-float(row["max_feature_combo_p"]))<1e-12)
score_rows=read(SCORES);feature_rows=read(FEATURES);fold_rows=read(FOLDS);null_rows=read(NULL);check("rows",len(score_rows)==24 and len(feature_rows)==108 and len(fold_rows)==1488 and len(null_rows)==24)
for r in score_rows:check("table_"+r["panel"]+r["window"]+r["representation"],abs(float(r["gain_bits"])-rebuilt[r["panel"],(r["window"],r["representation"])][0])<2e-9 and abs(float(r["baseline_bits"])-float(r["held_bits"])-float(r["gain_bits"]))<2e-9)
for r in feature_rows:check("feature_"+r["feature"]+r["window"]+r["representation"],abs(float(r["gain_bits"])-fbuild[r["feature"],(r["window"],r["representation"])])<2e-9)
fr=stored[first[0]][first[1]];gates={"selector_paid_positive":float(fr["selector_paid_gain_bits"])>0,"beats_first_line_raw":float(fr["gain_bits"])>float(stored["FIRST_LINE"]["RAW_CHAR3"]["gain_bits"]),"beats_same_host_other_windows":all(float(fr["gain_bits"])>float(stored[w][first[1]]["gain_bits"])for w in("BODY_AFTER_FIRST","LAST_LINE","ALL_PAGE")),"positive_at_least_6_of_8_features":int(fr["positive_gain_features"])>=6,"positive_at_least_35_of_62_folios":int(fr["positive_gain_folios"])>=35,"cross_currier_positive":crossbuild[first]>0,"max_12_p_le_005":float(fr["max_12_p"])<=.05};check("gates",gates==result["gates"])
check("input_hashes",all(sha(ROOT/n)==d for n,d in result["inputs"].items()));check("implementation_hashes",all(sha(ROOT/n)==d for n,d in result["implementation"].items()));check("output_hashes",all(sha(ROOT/n)==d for n,d in result["outputs"].items()));check("document_hashes",all(sha(ROOT/n)==d for n,d in result["documents"].items()));x=dict(result);d=x.pop("result_content_sha256");check("content",csha(x)==d);v={"schema":"GDT138_VALIDATION_V1","status":"PASS_INDEPENDENT_WINDOW_REFIT_AND_NULL","checks":len(checks),"passed":sum(x["pass"]for x in checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"check_rows":checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf8");print(json.dumps({"status":v["status"],"checks":v["checks"]},sort_keys=True))
