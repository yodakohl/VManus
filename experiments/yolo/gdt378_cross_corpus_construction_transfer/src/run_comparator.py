#!/usr/bin/env python3
"""Run GDT378 cross-domain comparator calibration; never read Voynich."""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer";ART=BASE/"artifacts"
OBS=ART/"gdt378_comparator_observation_layer.tsv.gz";ORACLE=ART/"gdt378_hidden_oracle.tsv.gz";DESIGN=ART/"gdt378_comparator_design_freeze.json";CONTRACT=ART/"gdt378_oracle_contract.json"
ENDPOINTS=["HEAD_WITH_DEPENDENTS","HIGH_VALENCY_HEAD","REF_ANAPHORA","CORRELATIVE_MEMBER","NEXT_RESUME","UNTIL_STATE_GATE","COORDINATOR","ALTERNATIVE_OR","POLARITY_EXCLUSION","COMPARISON","FUNCTION_WORD","STATE_TRANSITION","CLOSER"]
REPS=["ABSOLUTE_PROBABILITY","WITHIN_RECORD_RANK","STRUCTURE_MINUS_NUISANCE_DELTA","DOMAIN_STANDARDIZED","SCOPE_HORIZON","NEIGHBOR_RECURRENCE","FIXED_RANK_COMBINATION"]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):
    q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(p):
    opener=gzip.open if p.suffix==".gz" else open
    with opener(p,"rt",encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows):
    if p.suffix==".gz":raw=p.open("wb");gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0);h=io.TextIOWrapper(gz,encoding="utf-8",newline="")
    else:h=p.open("w",encoding="utf-8",newline="")
    with h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sigmoid(x):
    z=np.clip(x,-40,40)
    return np.where(z>=0,1/(1+np.exp(-z)),np.exp(z)/(1+np.exp(z)))
def fit(X,y,domain,l2=4.0):
    X=np.asarray(X,float);y=np.asarray(y,float);counts=Counter(domain);w0=np.array([len(domain)/(len(counts)*counts[d]) for d in domain]);mu=np.average(X[:,1:],axis=0,weights=w0);sd=np.sqrt(np.average((X[:,1:]-mu)**2,axis=0,weights=w0));sd[sd<1e-8]=1
    Z=X.copy();Z[:,1:]=(Z[:,1:]-mu)/sd;b=np.zeros(Z.shape[1]);pen=np.ones(len(b))*l2;pen[0]=0
    for _ in range(35):
        p=sigmoid(Z@b);ww=np.maximum(p*(1-p),1e-6)*w0;H=(Z.T*ww)@Z+np.diag(pen);g=Z.T@((y-p)*w0)-pen*b
        try:step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError:step=np.linalg.lstsq(H,g,rcond=None)[0]
        b+=step
        if np.max(np.abs(step))<1e-7:break
    return b,mu,sd
def predict(model,X):
    b,mu,sd=model;Z=np.asarray(X,float).copy();Z[:,1:]=(Z[:,1:]-mu)/sd;return np.clip(sigmoid(Z@b),1e-6,1-1e-6)
def bits(y,p):
    y=np.asarray(y);p=np.clip(np.asarray(p),1e-9,1-1e-9);return float(-np.sum(y*np.log2(p)+(1-y)*np.log2(1-p)))
def rankdata(x):
    x=np.asarray(x);order=np.argsort(x,kind="stable");r=np.empty(len(x),float);i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:j+=1
        r[order[i:j]]=(i+j+1)/2;i=j
    return r
def auc(y,s):
    y=np.asarray(y,int);n1=int(y.sum());n0=len(y)-n1
    if not n1 or not n0:return float("nan")
    return float((rankdata(s)[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def ap(y,s):
    y=np.asarray(y,int);n=int(y.sum())
    if not n:return float("nan")
    order=np.argsort(-np.asarray(s),kind="stable");hit=0;total=0
    for k,i in enumerate(order,1):
        if y[i]:hit+=1;total+=hit/k
    return total/n
def within_record_rank(score,ids,records):
    out=np.zeros(len(ids),float);groups=defaultdict(list)
    for loc,i in enumerate(ids):groups[records[i]].append(loc)
    for locs in groups.values():
        v=rankdata(np.asarray([score[x] for x in locs]));n=len(locs)
        for a,b in zip(locs,v):out[a]=(b-.5)/n
    return out
def pct_rank(x):
    r=rankdata(x);return (r-.5)/max(1,len(r))

def features(obs):
    n=len(obs);byrec=defaultdict(list);bycol=defaultdict(list);bydomain=defaultdict(list)
    for i,r in enumerate(obs):
        rec=(r["domain"],r["collection_id"],r["record_id"]);byrec[rec].append(i);bycol[(r["domain"],r["collection_id"])].append(i);bydomain[r["domain"]].append(i)
    record_order={}
    for col,idxs in bycol.items():record_order[col]=sorted({(int(obs[i]["record_ordinal"]),obs[i]["record_id"]) for i in idxs})
    global_stats={}
    for domain,idxs in bydomain.items():
        stat=defaultdict(lambda:{"n":0,"records":set(),"prev":set(),"next":set(),"pos":[]})
        for rec,ri in byrec.items():
            if rec[0]!=domain:continue
            ri.sort(key=lambda i:int(obs[i]["element_ordinal"]));forms=[obs[i]["opaque_form_id"] for i in ri]
            for j,i in enumerate(ri):
                q=stat[forms[j]];q["n"]+=1;q["records"].add(rec);q["pos"].append(float(obs[i]["relative_position"]))
                if j:q["prev"].add(forms[j-1])
                if j+1<len(forms):q["next"].add(forms[j+1])
        global_stats[domain]=stat
    nuisance=[None]*n;scope=[None]*n;neighbor=[None]*n;records=[None]*n
    for rec,ids in byrec.items():
        ids.sort(key=lambda i:int(obs[i]["element_ordinal"]));forms=[obs[i]["opaque_form_id"] for i in ids];m=len(ids);cnt=Counter(forms);positions=defaultdict(list)
        for j,f in enumerate(forms):positions[f].append(j)
        order=record_order[(rec[0],rec[1])];names=[x[1] for x in order];rp=names.index(rec[2]);prev_ids=byrec.get((rec[0],rec[1],names[rp-1]),[]) if rp else [];next_ids=byrec.get((rec[0],rec[1],names[rp+1]),[]) if rp+1<len(names) else []
        prevset={obs[i]["opaque_form_id"] for i in prev_ids};nextset={obs[i]["opaque_form_id"] for i in next_ids};cur=set(forms);prevjac=len(cur&prevset)/max(1,len(cur|prevset));nextjac=len(cur&nextset)/max(1,len(cur|nextset))
        max_ord=max(x[0] for x in order)
        for j,i in enumerate(ids):
            r=obs[i];f=forms[j];ps=positions[f];before=[x for x in ps if x<j];after=[x for x in ps if x>j];q=global_stats[rec[0]][f];p=float(r["relative_position"])
            nuisance[i]=[1.,math.log1p(m),p,p*p,math.log1p(int(r["surface_length"])),math.log1p(int(r["direct_token_count"])),float(j==0),float(j==m-1),int(r["record_ordinal"])/max(1,max_ord),math.log1p(int(r["physical_line_count"]))]
            scope[i]=[(m-j-1)/max(1,m),(j)/max(1,m),(j-before[-1])/max(1,m) if before else 1.,(after[0]-j)/max(1,m) if after else 1.,len(set(forms[:j]))/max(1,m),len(set(forms[j+1:]))/max(1,m),float(bool(before)),float(bool(after))]
            pos=q["pos"]
            neighbor[i]=[float(j>0 and forms[j-1]==f),float(j+1<m and forms[j+1]==f),math.log1p(cnt[f]),len(cur)/max(1,m),float(f in prevset),float(f in nextset),prevjac,nextjac,float(j>0 and j+1<m and forms[j-1]==forms[j+1]),float(j>=2 and forms[j-2]==f),float(j+2<m and forms[j+2]==f),math.log1p(q["n"]),math.log1p(len(q["records"])),math.log1p(len(q["prev"])),math.log1p(len(q["next"])),sum(pos)/len(pos),float(np.std(pos))]
            records[i]=rec
    return np.asarray(nuisance),np.asarray(scope),np.asarray(neighbor),records

def transfer_stat(endpoint,domain_auc,available):
    vals={d:domain_auc.get(d,float("nan")) for d in available}
    finite={d:v for d,v in vals.items() if math.isfinite(v)}
    if endpoint=="HEAD_WITH_DEPENDENTS":
        proc=[finite[d] for d in ["CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"] if d in finite]
        if "COREMA" not in finite or "PCEEC2" not in finite or not proc:return float("nan")
        return min(finite["COREMA"],finite["PCEEC2"],max(proc))
    if len(finite)<3:return float("nan")
    return sorted(finite.values(),reverse=True)[2]

def main():
    design=json.loads(DESIGN.read_text());contract=json.loads(CONTRACT.read_text());assert design["status"]=="FORM_BLIND_LAYERS_FROZEN_BEFORE_SCORING" and not design["voynich_scored"]
    obs=read(OBS);oracle=read(ORACLE);assert [r["element_key"] for r in obs]==[r["element_key"] for r in oracle];N=len(obs);domains=design["domains"];Xn,Xscope,Xneighbor,record_keys=features(obs);Xfull=np.column_stack([Xn,Xscope,Xneighbor])
    Y={e:np.array([int(r[e]) for r in oracle],int) for e in ENDPOINTS};availability=contract["availability"];domain_arr=np.array([r["domain"] for r in obs]);predictions={};foldrows=[]
    for endpoint in ENDPOINTS:
        available=availability.get(endpoint,[]);P={r:np.full(N,np.nan) for r in REPS};Pn=np.full(N,np.nan);Pf=np.full(N,np.nan)
        for held in available:
            train=np.where(np.isin(domain_arr,[d for d in available if d!=held]))[0];test=np.where(domain_arr==held)[0]
            if len(train)==0 or len(np.unique(Y[endpoint][train]))<2 or len(np.unique(Y[endpoint][test]))<2:continue
            td=domain_arr[train].tolist();mn=fit(Xn[train],Y[endpoint][train],td);mf=fit(Xfull[train],Y[endpoint][train],td);ms=fit(np.column_stack([Xn[train],Xscope[train]]),Y[endpoint][train],td);mr=fit(np.column_stack([Xn[train],Xneighbor[train]]),Y[endpoint][train],td)
            pn=predict(mn,Xn[test]);pf=predict(mf,Xfull[test]);ps=predict(ms,np.column_stack([Xn[test],Xscope[test]]));pr=predict(mr,np.column_stack([Xn[test],Xneighbor[test]]));delta=np.log(pf/(1-pf))-np.log(pn/(1-pn));z=(delta-delta.mean())/max(delta.std(),1e-9);wr=within_record_rank(pf,test,record_keys);combo=(wr+pct_rank(delta)+pct_rank(ps)+pct_rank(pr))/4
            vals={"ABSOLUTE_PROBABILITY":pf,"WITHIN_RECORD_RANK":wr,"STRUCTURE_MINUS_NUISANCE_DELTA":delta,"DOMAIN_STANDARDIZED":z,"SCOPE_HORIZON":ps,"NEIGHBOR_RECURRENCE":pr,"FIXED_RANK_COMBINATION":combo}
            Pn[test]=pn;Pf[test]=pf
            for rep,v in vals.items():P[rep][test]=v
            y=Y[endpoint][test]
            for rep,v in vals.items():
                foldrows.append({"endpoint":endpoint,"held_domain":held,"representation":rep,"n":len(test),"positives":int(y.sum()),"auc":f"{auc(y,v):.9f}","average_precision":f"{ap(y,v):.9f}","prevalence":f"{y.mean():.9f}","full_gain_vs_nuisance_bits":f"{bits(y,pn)-bits(y,pf):.9f}","representation_gain_vs_nuisance_bits":f"{(bits(y,pn)-bits(y,v)) if rep in {'ABSOLUTE_PROBABILITY','SCOPE_HORIZON','NEIGHBOR_RECURRENCE'} else float('nan'):.9f}"})
        predictions[endpoint]=(P,Pn,Pf)
    summary=[]
    for endpoint in ENDPOINTS:
        available=availability.get(endpoint,[]);P,Pn,Pf=predictions[endpoint]
        for rep in REPS:
            by={r["held_domain"]:float(r["auc"]) for r in foldrows if r["endpoint"]==endpoint and r["representation"]==rep};gains={r["held_domain"]:float(r["full_gain_vs_nuisance_bits"]) for r in foldrows if r["endpoint"]==endpoint and r["representation"]==rep};stat=transfer_stat(endpoint,by,available)
            summary.append({"endpoint":endpoint,"representation":rep,"available_domains":len(available),"scored_domains":len(by),"transfer_auc_floor":f"{stat:.9f}" if math.isfinite(stat) else "","mean_domain_auc":f"{np.mean(list(by.values())):.9f}" if by else "","positive_full_gain_domains":sum(v>0 for v in gains.values()),"domain_aucs_json":json.dumps(by,sort_keys=True,separators=(",",":")),"domain_full_gains_json":json.dumps(gains,sort_keys=True,separators=(",",":"))})
    # Fixed-prediction max-family null. One shared permutation preserves endpoint correlation.
    strata=defaultdict(list)
    for i,r in enumerate(obs):
        n=int(r["record_element_count"]);lb="A" if n<=8 else "B" if n<=16 else "C" if n<=32 else "D";p=min(9,int(float(r["relative_position"])*10));sl=int(r["surface_length"]);sb="0" if sl==0 else "1-3" if sl<=3 else "4-7" if sl<=7 else "8+";strata[(r["domain"],lb,p,sb)].append(i)
    rank_cache={}
    for endpoint in ENDPOINTS:
        P,_,_=predictions[endpoint]
        for domain in availability.get(endpoint,[]):
            ids=np.where(domain_arr==domain)[0]
            for rep in REPS:
                s=P[rep][ids]
                if np.all(np.isfinite(s)):rank_cache[(endpoint,domain,rep)]=(ids,rankdata(s))
    maxima=[];null_values={(e,r):[] for e in ENDPOINTS for r in REPS};nullworldrows=[]
    Ymat=np.column_stack([Y[e] for e in ENDPOINTS])
    for world in range(256):
        rng=np.random.default_rng(378000+world);perm=np.arange(N)
        for ids in strata.values():perm[ids]=rng.permutation(ids)
        yp=Ymat[perm]
        worldstats=[]
        for ei,endpoint in enumerate(ENDPOINTS):
            available=availability.get(endpoint,[])
            for rep in REPS:
                by={}
                for domain in available:
                    key=(endpoint,domain,rep)
                    if key not in rank_cache:continue
                    ids,ranks=rank_cache[key];yy=yp[ids,ei];n1=int(yy.sum());n0=len(yy)-n1
                    if n1 and n0:by[domain]=float((ranks[yy==1].sum()-n1*(n1+1)/2)/(n1*n0))
                st=transfer_stat(endpoint,by,available);null_values[(endpoint,rep)].append(st)
                if math.isfinite(st):worldstats.append(st)
        maxima.append(max(worldstats) if worldstats else .5)
        for endpoint in ENDPOINTS:
            for rep in REPS:
                st=null_values[(endpoint,rep)][world]
                nullworldrows.append({"world":world,"endpoint":endpoint,"representation":rep,"transfer_auc_floor":f"{st:.9f}" if math.isfinite(st) else "","world_max":f"{maxima[-1]:.9f}"})
    for row in summary:
        if not row["transfer_auc_floor"]:row["local_p"]="NA";row["max_family_p"]="NA";continue
        val=float(row["transfer_auc_floor"]);nv=[x for x in null_values[(row["endpoint"],row["representation"])] if math.isfinite(x)];row["local_p"]=f"{(1+sum(x>=val for x in nv))/(1+len(nv)):.9f}";row["max_family_p"]=f"{(1+sum(x>=val for x in maxima))/257:.9f}"
    headrows=[r for r in summary if r["endpoint"]=="HEAD_WITH_DEPENDENTS" and r["transfer_auc_floor"]]
    headrows.sort(key=lambda r:(-float(r["transfer_auc_floor"]),-float(r["mean_domain_auc"]),REPS.index(r["representation"])))
    best=headrows[0];best_rep=best["representation"];best_folds=[r for r in foldrows if r["endpoint"]=="HEAD_WITH_DEPENDENTS" and r["representation"]==best_rep];aucs={r["held_domain"]:float(r["auc"]) for r in best_folds};gains={r["held_domain"]:float(r["full_gain_vs_nuisance_bits"]) for r in best_folds};proc=[d for d in ["CURIOUS_CURES","HARLEIAN_COOKERY","QUINTE_ESSENCE"] if aucs.get(d,0)>=.65 and gains.get(d,0)>0]
    gate=aucs.get("COREMA",0)>=.65 and gains.get("COREMA",0)>0 and aucs.get("PCEEC2",0)>=.65 and gains.get("PCEEC2",0)>0 and bool(proc) and float(best.get("max_family_p") or 1)<=.05
    # Fixed threshold grid, selected only on pooled held comparator labels by macro balanced accuracy.
    P=predictions["HEAD_WITH_DEPENDENTS"][0][best_rep];valid=np.isfinite(P);score=P[valid];yy=Y["HEAD_WITH_DEPENDENTS"][valid];dd=domain_arr[valid];thresholds=[]
    for q in [.50,.65,.80,.90]:
        vals=[]
        for d in availability["HEAD_WITH_DEPENDENTS"]:
            ids=np.where(dd==d)[0];cut=float(np.quantile(score[ids],q));pred=score[ids]>=cut;y=yy[ids];tpr=float(pred[y==1].mean()) if y.sum() else 0;tnr=float((~pred[y==0]).mean()) if (y==0).sum() else 0;vals.append((tpr+tnr)/2)
        thresholds.append((sum(vals)/len(vals),q))
    threshold_q=max(thresholds)[1]
    nullrows=[]
    for row in summary:
        if row["transfer_auc_floor"]:nullrows.append({"endpoint":row["endpoint"],"representation":row["representation"],"observed_transfer_auc_floor":row["transfer_auc_floor"],"local_p":row["local_p"],"max_family_p":row["max_family_p"],"worlds":256})
    write(ART/"gdt378_comparator_fold_scores.tsv",foldrows);write(ART/"gdt378_signature_summary.tsv",summary);write(ART/"gdt378_comparator_null.tsv",nullrows);write(ART/"gdt378_comparator_null_worlds.tsv.gz",nullworldrows)
    family=[]
    for endpoint in ENDPOINTS:
        rows=[r for r in summary if r["endpoint"]==endpoint and r["transfer_auc_floor"]];rows.sort(key=lambda r:-float(r["transfer_auc_floor"]))
        r=rows[0] if rows else None;family.append({"endpoint":endpoint,"best_representation":r["representation"] if r else "NONE","transfer_auc_floor":r["transfer_auc_floor"] if r else "","max_family_p":r["max_family_p"] if r else "","status":"HEAD_TRANSFER_GATE_PASS" if endpoint=="HEAD_WITH_DEPENDENTS" and gate else "COMPARATOR_TRANSFER_PROVISIONAL" if r and float(r["transfer_auc_floor"])>=.65 and float(r["max_family_p"])<=.05 else "NO_CROSS_DOMAIN_TRANSFER","voynich_eligible":int(endpoint=="HEAD_WITH_DEPENDENTS" and gate)})
    write(ART/"gdt378_functional_family_calibration.tsv",family)
    headout=[];Pall=predictions["HEAD_WITH_DEPENDENTS"][0]
    head_pn=predictions["HEAD_WITH_DEPENDENTS"][1];head_pf=predictions["HEAD_WITH_DEPENDENTS"][2]
    for i,r in enumerate(obs):headout.append({"element_key":r["element_key"],"domain":r["domain"],"oracle_label":int(Y["HEAD_WITH_DEPENDENTS"][i]),"nuisance_probability":f"{head_pn[i]:.9f}","full_probability":f"{head_pf[i]:.9f}","selected_representation":best_rep,"selected_representation_score":f"{Pall[best_rep][i]:.9f}"})
    write(ART/"gdt378_head_held_predictions.tsv.gz",headout)
    signature={"schema":"GDT378_TRANSFER_SIGNATURE_V1","status":"FROZEN_FOR_VOYNICH_MAPPING" if gate else "NO_SIGNATURE_AUTHORIZED_FOR_VOYNICH","endpoint":"HEAD_WITH_DEPENDENTS","representation":best_rep,"threshold_type":"WITHIN_DOMAIN_QUANTILE","threshold_quantile":threshold_q,"head_gate_pass":gate,"transfer_auc_floor":float(best["transfer_auc_floor"]),"max_family_p":float(best["max_family_p"]),"domain_aucs":aucs,"domain_full_gains_bits":gains,"procedural_domains_passing":proc,"semantic_state":"UNASSIGNED","voynich_scored":False,"f84_accessed":False}
    signature["content_hash"]=content(signature);(ART/"gdt378_transfer_signature_freeze.json").write_text(json.dumps(signature,indent=2,sort_keys=True)+"\n")
    outputs=[ART/x for x in ["gdt378_comparator_fold_scores.tsv","gdt378_signature_summary.tsv","gdt378_comparator_null.tsv","gdt378_comparator_null_worlds.tsv.gz","gdt378_functional_family_calibration.tsv","gdt378_head_held_predictions.tsv.gz","gdt378_transfer_signature_freeze.json"]]
    result={"schema":"GDT378_COMPARATOR_RESULT_V1","status":"CONSTRUCTION_HEAD_SIGNATURE_CALIBRATED" if gate else "NO_CONSTRUCTION_HEAD_SIGNATURE_GENERALIZED","head_gate_pass":gate,"best_head_representation":best_rep,"best_head_transfer_auc_floor":float(best["transfer_auc_floor"]),"best_head_max_family_p":float(best["max_family_p"]),"domains":domains,"rows":N,"records":design["records"],"functional_families_tested":len(ENDPOINTS),"representations_tested":len(REPS),"voynich_scored":False,"voynich_rows_read":0,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [OBS,ORACLE,DESIGN,CONTRACT]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outputs},"implementation":{str((BASE/"src/run_comparator.py").relative_to(ROOT)):sha(BASE/"src/run_comparator.py")},"claim_ceiling":"CROSS_DOMAIN_FORM_BLIND_COMPARATOR_CALIBRATION_ONLY"};result["content_hash"]=content(result);(ART/"gdt378_comparator_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"representation":best_rep,"floor":result["best_head_transfer_auc_floor"],"max_p":result["best_head_max_family_p"],"procedural":proc}))
if __name__=="__main__":main()
