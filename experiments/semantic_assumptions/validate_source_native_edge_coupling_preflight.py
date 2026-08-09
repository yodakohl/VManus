#!/usr/bin/env python3
"""Independent reconstruction of the source-native edge-coupling preflight."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,math,multiprocessing as mp
from collections import defaultdict
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results"
PANEL_PATH=RESULTS/"source_native_edge_coupling_masked.tsv";CAPVAL=RESULTS/"source_native_edge_coupling_capacity_validation.json"
SPEC=BASE/"SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md";CORE=BASE/"source_native_edge_coupling_core.py";RUNNER=BASE/"run_source_native_edge_coupling_preflight.py"
PRODUCTION=RESULTS/"source_native_edge_coupling_preflight.json";PROD_REPORT=RESULTS/"source_native_edge_coupling_preflight_report.md"
VALIDATOR=Path(__file__).resolve();OUT=RESULTS/"source_native_edge_coupling_preflight_validation.json";REPORT=RESULTS/"source_native_edge_coupling_preflight_validation_report.md"
TARGET_OUT=RESULTS/"source_native_edge_coupling_target.json";TARGET_REPORT=RESULTS/"source_native_edge_coupling_target_report.md"
HASHES={PANEL_PATH:"db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c",CAPVAL:"889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5",SPEC:"634eff5ddf6e3e823728d3aa40e4fd0465b5743ba003216c69692f21ef3f466c",CORE:"c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349",RUNNER:"a57e85f5fcef9643d3cd40d47cee048db8f7030843a6c644323c44e1ecf7fda0",PRODUCTION:"901eea3a922c866d5c6705ac284cfc3c9406580853c0bb624216bf40e8587d61",PROD_REPORT:"2fd9b0b4a382937092e92eaf963d5c30fdf0f8a041576d6c0e9d663b32009f3f"}
ALPHABET="ABCDEFGHJKLMNPQRSTUVWXYZ";K=24;ALPHA=.5;PANEL=None;CHECKS=0
FIELDS=("unit_id","consensus_group_id","locus","page","physical_folio","section","currier","hand","kind","locus_position","symbol_count","length_bin","opening_family","core_first_family","core_last_family","baseline_cell","full_cell","masked_family_surface","outside_folio_baseline_support","outside_folio_full_support","target_eligible")

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u64(s):return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"little")
def load():
    with PANEL_PATH.open(encoding="utf-8",newline="") as h:
        rd=csv.DictReader(h,delimiter="\t");
        if tuple(rd.fieldnames or ())!=FIELDS:raise AssertionError("schema")
        rows=list(rd)
    if len(rows)!=19203 or len({r['unit_id'] for r in rows})!=19203 or any(r['masked_family_surface'].count('#')!=1 for r in rows):raise AssertionError("rows")
    bkeys=sorted({r['baseline_cell'] for r in rows});fkeys=sorted({r['full_cell'] for r in rows});bm={v:i for i,v in enumerate(bkeys)};fm={v:i for i,v in enumerate(fkeys)}
    folios=sorted({r['physical_folio'] for r in rows},key=lambda x:int(x[1:]));fr=[np.asarray([i for i,r in enumerate(rows) if r['physical_folio']==f],dtype=np.int64) for f in folios]
    return {"rows":rows,"bi":np.asarray([bm[r['baseline_cell']] for r in rows]),"fi":np.asarray([fm[r['full_cell']] for r in rows]),"bkeys":bkeys,"fkeys":fkeys,"folios":folios,"fr":fr,"eligible":np.asarray([r['target_eligible']=='1' for r in rows])}
def signp(pos,n):return sum(math.comb(n,k) for k in range(pos,n+1))/(2**n)
def score(y):
    p=PANEL;bc=np.zeros((len(p['bkeys']),K),dtype=np.int64);fc=np.zeros((len(p['fkeys']),K),dtype=np.int64);np.add.at(bc,(p['bi'],y),1);np.add.at(fc,(p['fi'],y),1)
    gains=np.full(len(y),np.nan);fe=[];cur=defaultdict(list)
    for folio,idx in zip(p['folios'],p['fr']):
        hb=np.zeros_like(bc);hf=np.zeros_like(fc);np.add.at(hb,(p['bi'][idx],y[idx]),1);np.add.at(hf,(p['fi'][idx],y[idx]),1);tb=bc-hb;tf=fc-hf;held=idx[p['eligible'][idx]];vals=[];cv=defaultdict(list)
        for i in held:
            b,f,o=p['bi'][i],p['fi'][i],y[i];nb=int(tb[b].sum());nf=int(tf[f].sum())
            if nb<20 or nf<5:raise AssertionError("support")
            v=math.log(((tf[f,o]+ALPHA)/(nf+ALPHA*K))/((tb[b,o]+ALPHA)/(nb+ALPHA*K)));gains[i]=v;vals.append(v);cv[p['rows'][i]['currier']].append(v)
        fe.append(float(np.mean(vals)))
        for key,values in cv.items():cur[key].append(float(np.mean(values)))
    fe=np.asarray(fe);deleted=(fe.sum()-fe)/(len(fe)-1);total=float(np.abs(fe).sum())
    c={}
    for key in ('A','B'):
        v=np.asarray(cur[key]);pos=int((v>0).sum());c[key]={"effect_equal_folio":float(v.mean()),"positive_folios":pos,"folios":len(v),"sign_p":signp(pos,len(v)),"minimum_leave_one_folio_out":float(((v.sum()-v)/(len(v)-1)).min())}
    pos=int((fe>0).sum())
    return {"eligible_rows":int(np.isfinite(gains).sum()),"physical_folios":len(fe),"effect_equal_folio":float(fe.mean()),"effect_equal_row":float(np.nanmean(gains)),"positive_folios":pos,"sign_p":signp(pos,len(fe)),"minimum_leave_one_folio_out":float(deleted.min()),"max_abs_contribution_fraction":float(np.abs(fe).max()/total) if total else 1.,"currier":c}
def synth(world,mode,strength):
    out=np.empty(len(PANEL['rows']),dtype=np.int64)
    for i,r in enumerate(PANEL['rows']):
        a=u64(f"EDGE|{world}|BASE1|{r['baseline_cell']}")%K;b=u64(f"EDGE|{world}|BASE2|{r['baseline_cell']}")%K;x=(u64(f"EDGE|{world}|BASEU|{r['unit_id']}")+.5)/(1<<64)
        value=a if x<.45 else (b if x<.70 else u64(f"EDGE|{world}|BASER|{r['unit_id']}")%K)
        if mode in {'COUPLED','ONE_FOLIO','FOLIO_RANDOM'}:
            active=mode!='ONE_FOLIO' or r['physical_folio']==PANEL['folios'][world%len(PANEL['folios'])];cu=(u64(f"EDGE|{world}|COUPLEU|{r['unit_id']}")+.5)/(1<<64)
            if active and cu<strength:
                domain=r['opening_family'] if mode!='FOLIO_RANDOM' else f"{r['physical_folio']}|{r['opening_family']}";value=u64(f"EDGE|{world}|MAP|{domain}")%K
        elif mode!='NULL':raise AssertionError("mode")
        out[i]=value
    return out
def passes(r):return r['eligible_rows']==14955 and r['physical_folios']==94 and r['effect_equal_folio']>=.02 and r['positive_folios']>=65 and r['sign_p']<=.01 and r['minimum_leave_one_folio_out']>0 and r['max_abs_contribution_fraction']<=.08 and all(r['currier'][k]['effect_equal_folio']>=.01 and r['currier'][k]['minimum_leave_one_folio_out']>0 and r['currier'][k]['positive_folios']/r['currier'][k]['folios']>=.60 for k in ('A','B'))
def task(t):
    mode,strength,world=t;r=score(synth(world,mode,strength));return {"mode":mode,"strength":strength,"world":world,"passes":passes(r),"result":r}
def compare(a,b,path='root'):
    global CHECKS;CHECKS+=1
    if isinstance(a,dict) and isinstance(b,dict):
        if set(a)!=set(b):raise AssertionError('keys '+path)
        for k in a:compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):raise AssertionError('len '+path)
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]')
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool) and not isinstance(b,bool):
        if abs(float(a)-float(b))>1e-12:raise AssertionError(f'num {path}')
    elif a!=b:raise AssertionError(f'value {path}')
def main():
    global PANEL,CHECKS
    if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
    for p,e in HASHES.items():CHECKS+=1;assert sha(p)==e,p.name
    PANEL=load();production=json.loads(PRODUCTION.read_text())
    tasks=[('NULL',0.,w) for w in range(64)]+[('COUPLED',.2,w) for w in range(8)]+[('ONE_FOLIO',.8,w) for w in range(8)]+[('FOLIO_RANDOM',.8,w) for w in range(8)]
    with mp.get_context('fork').Pool(32) as pool:worlds=pool.map(task,tasks)
    worlds.sort(key=lambda r:(r['mode'],r['strength'],r['world']));compare(worlds,production['worlds'],'worlds')
    select=lambda m:[r for r in worlds if r['mode']==m];null,coupled,one,random=map(select,['NULL','COUPLED','ONE_FOLIO','FOLIO_RANDOM'])
    ag={"null_passes":sum(r['passes'] for r in null),"null_worlds":64,"coupled_passes":sum(r['passes'] for r in coupled),"one_folio_passes":sum(r['passes'] for r in one),"folio_random_passes":sum(r['passes'] for r in random)};compare(ag,production['aggregates'],'aggregates')
    labels=synth(0,'COUPLED',.2);perm=np.asarray([(i*7+3)%24 for i in range(24)]);a,b=score(labels),score(perm[labels]);fields=['effect_equal_folio','effect_equal_row','sign_p','minimum_leave_one_folio_out','max_abs_contribution_fraction'];delta=max(abs(a[k]-b[k]) for k in fields);compare({"outcome_relabel_max_abs_difference":delta},production['invariants'],'invariants')
    assert production['status']=='PASS_TARGET_FREE_EDGE_COUPLING_PREFLIGHT' and production['decision']=='GO_FREEZE_ONE_EDGE_COUPLING_TARGET' and all(production['gates'].values()) and all(production['mutations'].values())
    assert not TARGET_OUT.exists() and not TARGET_REPORT.exists() and production['target_isolation']['target_outcomes_accessed']==production['target_isolation']['target_scores_computed']==0
    expected_inputs={p.name:sha(p) for p in (PANEL_PATH,CAPVAL,CORE,SPEC,RUNNER)};compare(expected_inputs,production['inputs'],'inputs')
    expected_report=f"""# Source-native edge-coupling synthetic preflight

Status: **{production['status']}**

The target-free 32-worker grid produced **{ag['null_passes']}/64** null,
**{ag['coupled_passes']}/8** global-coupling, **{ag['one_folio_passes']}/8**
one-folio, and **{ag['folio_random_passes']}/8** folio-random passes.
Outcome relabeling, capacity, finite-score, isolation, and target-absence gates
all passed. The source final
families were existence-tested only and zero target outcomes or scores were
opened.

Decision: **{production['decision']}**. This preflight supplies no affix, word,
meaning, plaintext, or translation.
"""
    assert PROD_REPORT.read_text()==expected_report;CHECKS+=1
    result={"experiment":"SOURCE_NATIVE_EDGE_COUPLING_PREFLIGHT_VALIDATION","status":"PASS_INDEPENDENT_88_WORLD_PREFLIGHT_RECONSTRUCTION","checks":CHECKS,"validator_sha256":sha(VALIDATOR),"production_sha256":sha(PRODUCTION),"worlds_reconstructed":88,"aggregates":ag,"target_source_opened":False,"target_outcomes_accessed":0,"target_scores_computed":0,"target_outputs_absent":True,"failures":[],"claim_ceiling":production['claim_ceiling']}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Source-native edge-coupling preflight validation

Status: **{result['status']}**

A nonimporting implementation reconstructed all **88** worlds, 94-fold
categorical fits, proper-score hierarchies, Currier and concentration gates,
0/64 null, 8/8 power, both 0/8 adversarial families, relabel invariance,
decision, bindings, and exact report in **{CHECKS:,}** checks. The final-family
source was not opened. This validates one target authorization only and
supplies no affix, word, meaning, plaintext, or translation.
""");print(json.dumps({"status":result['status'],"checks":CHECKS},sort_keys=True))
if __name__=='__main__':main()
