#!/usr/bin/env python3
"""Independent validator for GDT013 retained predictions and motif statistics."""

from __future__ import annotations

import csv,hashlib,json,math
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt013_result.json";VALIDATION=ROOT/"gdt013_validation.json"
ROLES=("PLANT","FIGURE","WATER_OR_APPARATUS","STAR_OR_SKY","REL_EXPLICIT_ATTACHMENT","REL_ENCLOSURE","REL_PROXIMITY","REL_ARRAY_OR_GROUP")
MODELS=("PRIOR","NUISANCE","WHOLE_TOKEN_STRING","RESIDUAL_HOST","SOURCE_FAMILY","FIELD_CONTENT_JOINT")
OBJECTS=set(ROLES[:4])
def read(name:str)->list[dict[str,str]]:
    with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def ap(y:list[int],p:list[float])->float:
    total=sum(y)
    if not total:return 0.
    g=defaultdict(lambda:[0,0])
    for a,b in zip(y,p):g[b][0]+=a;g[b][1]+=1
    tp=seen=0;value=0.
    for score in sorted(g,reverse=True):
        pos,n=g[score];tp+=pos;seen+=n
        if pos:value+=(pos/total)*(tp/seen)
    return value
def has(row:dict[str,str],role:str)->bool:
    return role in row["object_tags"if role in OBJECTS else"relation_tags"].split(";")
def hpmf(n:int,k:int,m:int)->dict[int,Fraction]:
    d=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),d)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def exact(rows:list[dict[str,str]],mask:set[int],role:str,field:str)->tuple[float,float,int]:
    allowed={i for i,r in enumerate(rows)if r["annotation_certainty"]=="UNHEDGED"};by=defaultdict(list)
    for i in allowed:by[rows[i][field]].append(i)
    st=[];obs=0;exp=Fraction();num=den=0.
    for ix in by.values():
        n=len(ix);m=sum(i in mask for i in ix);k=sum(has(rows[i],role)for i in ix)
        if not(0<m<n and 0<k<n):continue
        x=sum(i in mask and has(rows[i],role)for i in ix);w=m*(n-m)/n;num+=w*(x/m-(k-x)/(n-m));den+=w;obs+=x;exp+=Fraction(m*k,n);st.append((n,m,k))
    dist={0:Fraction(1)}
    for n,m,k in st:
        nxt=defaultdict(Fraction)
        for a,pa in dist.items():
            for b,pb in hpmf(n,k,m).items():nxt[a+b]+=pa*pb
        dist=nxt
    d=abs(Fraction(obs)-exp);p=sum(v for x,v in dist.items()if abs(Fraction(x)-exp)>=d)if st else Fraction(1)
    return num/den if den else 0.,float(p),len(st)
def feature_hit(row:dict[str,str],feature:str)->bool:
    tag,value=feature.split(":",1)
    if tag=="HOST_EXACT":return row["residual_host"]==value
    if tag=="FAMILY_EXACT":return row["family_surface"]==value
    if tag in("H2","H3"):
        n=int(tag[1]);s="^"+row["residual_host"]+"$";return value in{s[i:i+n]for i in range(len(s)-n+1)}
    if tag in("F2","F3"):
        n=int(tag[1]);s="^"+row["family_surface"]+"$";return value in{s[i:i+n]for i in range(len(s)-n+1)}
    return False


def main()->None:
    checks=[];result=json.loads(RESULT.read_text());copy=dict(result);digest=copy.pop("result_content_sha256")
    checks.extend([("schema",result["schema"]=="GDT013_LATENT_ROLE_PROPAGATION_RESULT_V1"),("content_hash",digest==csha(copy))])
    for part in("inputs","implementation","outputs"):
        for name,value in result[part].items():checks.append((part+":"+name,sha(ROOT/name)==value))
    inv=read("gdt012_annotated_core_inventory.tsv");primary=[r for r in inv if r["annotation_certainty"]=="UNHEDGED"]
    pred=read("gdt013_heldout_predictions.tsv");comp=read("gdt013_model_comparison.tsv");anchors=read("gdt013_role_anchors.tsv");prose=read("gdt013_prose_anchor_occurrences.tsv");motifs=read("gdt013_relational_motif_leads.tsv")
    checks.extend([("primary",len(primary)==result["annotated_rows"]==394 and len({r["physical_folio"]for r in primary})==result["physical_folios"]==18),("prediction_grid",len(pred)==394*8*6 and len({(r["group_id"],r["role"],r["model"])for r in pred})==len(pred)),("fold_integrity",all(next(x for x in primary if x["group_id"]==r["group_id"])["physical_folio"]==r["held_folio"]for r in pred)),("probabilities",all(0<=float(r["probability"])<=1 for r in pred)),("f84",not any(r["locus"].startswith("f84r")for r in prose)and result["f84r"]=={"opened":False,"retained":False,"joined":False,"scored":False})])
    stored={(r["role"],r["model"]):r for r in comp};mean_b={};mean_ap={}
    for role in ROLES:
      for model in MODELS:
        x=[r for r in pred if r["role"]==role and r["model"]==model];y=[int(r["actual"])for r in x];p=[float(r["probability"])for r in x];b=sum((a-z)**2 for a,z in zip(y,p))/len(y);ll=-sum(a*math.log(max(1e-15,z))+(1-a)*math.log(max(1e-15,1-z))for a,z in zip(y,p))/len(y);a=ap(y,p);row=stored[(role,model)]
        checks.append((f"metric:{role}:{model}",abs(b-float(row["held_folio_brier"]))<6e-13 and abs(ll-float(row["held_folio_logloss"]))<6e-13 and abs(a-float(row["held_folio_average_precision"]))<6e-13))
    for model in MODELS:
        mean_b[model]=sum(float(stored[(r,model)]["held_folio_brier"])for r in ROLES)/8;mean_ap[model]=sum(float(stored[(r,model)]["held_folio_average_precision"])for r in ROLES)/8
    checks.extend([("model_selection",min(MODELS,key=lambda m:(mean_b[m],m))==result["selected_calibration_model"]=="PRIOR"and max((m for m in MODELS if m!="PRIOR"),key=lambda m:(mean_ap[m],m))==result["selected_discrimination_model"]=="SOURCE_FAMILY"),("means",all(abs(mean_b[m]-result["mean_brier"][m])<6e-13 and abs(mean_ap[m]-result["mean_average_precision"][m])<6e-13 for m in MODELS))])
    specs={"ARO":("aro","REL_PROXIMITY"),"TAR":("tar","REL_ENCLOSURE"),"ED":("ed","WATER_OR_APPARATUS"),"KAL":("kal","FIGURE")}
    for row in motifs:
        motif,role=specs[row["motif"]];mask={i for i,r in enumerate(inv)if motif in r["residual_host"]};pe,pp,_=exact(inv,mask,role,"page");fe,fp,_=exact(inv,mask,role,"physical_folio")
        checks.append(("motif:"+row["motif"],abs(pe-float(row["page_conditioned_effect"]))<6e-13 and abs(pp-float(row["page_exact_p"]))<6e-13 and abs(fe-float(row["folio_conditioned_effect"]))<6e-13 and abs(fp-float(row["folio_exact_p"]))<6e-13))
    anchor_keys={(r["role"],r["selected_model"],r["rank"],r["formal_feature"])for r in anchors}
    counts=Counter((r["role_hypothesis"],r["anchor_model"],r["anchor_rank"],r["formal_feature"])for r in prose)
    checks.extend([("anchors",len(anchors)==80 and len(anchor_keys)==80),("prose_cap",all(n<=40 for n in counts.values())and len(prose)==result["prose_propagations"]==2860),("prose_features",all(feature_hit(r,r["formal_feature"])for r in prose)),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT013_CKPT001")==1)])
    report=(ROOT/"GDT013_LATENT_ROLE_PROPAGATION_REPORT.md").read_text().lower();checks.extend([("report",all(x in report for x in("aro","tar","prior remains best","no word","f84r remained"))),("claim",all(x in result["claim_ceiling"].lower()for x in("exploratory","no confirmed word","translation")))])
    failures=[n for n,ok in checks if not ok];validation={"schema":"GDT013_LATENT_ROLE_PROPAGATION_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent retained-prediction metrics and model selection, four exact page/folio motif tests, anchor/prose feature joins and caps, f84 exclusion, hashes, ledger, and claim ceiling. Does not independently refit naive Bayes."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True))
    if failures:raise SystemExit(1)
if __name__=="__main__":main()
