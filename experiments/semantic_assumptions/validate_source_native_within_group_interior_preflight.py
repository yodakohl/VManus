#!/usr/bin/env python3
"""Independent reconstruction of the endpoint-free interior preflight."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"; os.environ["MKL_NUM_THREADS"] = "1"

import csv, hashlib, json, math, multiprocessing as mp
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np


BASE = Path(__file__).resolve().parent; RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_interior_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_interior_capacity_validation.json"
CORE = BASE / "source_native_within_group_interior_core.py"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TEST_SPEC.md"
RUNNER = BASE / "run_source_native_within_group_interior_preflight.py"
PRODUCTION = RESULTS / "source_native_within_group_interior_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_native_within_group_interior_preflight_report.md"
TARGET_OUT = RESULTS / "source_native_within_group_interior_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_interior_target_report.md"
OUT = RESULTS / "source_native_within_group_interior_preflight_validation.json"
REPORT = RESULTS / "source_native_within_group_interior_preflight_validation_report.md"
FROZEN = {
    PANEL_PATH: "0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad",
    CAPACITY_VALIDATION: "1513617bafcc3c4143af7be129251cf9dd7e7aa5cfa429c414c55eaa8fe923f8",
    CORE: "f516e87c5f0c3be14a9187ffd87f935ea92331147fd3f14241a5ad754ed7bd98",
    SPEC: "3f278d5ef39432084c9f200039e20799d53b07269f48d6aef7f9b4726ad19696",
    RUNNER: "27d5f4a6ec9d7193fa50cb83b118222fab652704ac9edafcf78e9d9e40355942",
    PRODUCTION: "564fe586a118962344211a8fd7e33c8ac8130bab6b4104c893fb9e6e214107e3",
    PRODUCTION_REPORT: "a34bb814a3fec45ef0b2e7b2e1f41e042259e17358902531de10571407e9ac25",
}
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ"); ALPHA = .5
CANDIDATES = ("K1", "FIXED_2", "FIXED_3", "FIXED_4", "FIXED_5")
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "original_symbol_count", "interior_symbol_count", "split")
TASKS = ([("NULL", w) for w in range(64)] + [("POSITION",100+w) for w in range(8)] + [("CURRIER_ONE",200+w) for w in range(8)] + [("ONE_FOLIO",300+w) for w in range(8)] + [("FOLIO_RANDOM",400+w) for w in range(8)])
PANEL = None


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(text): return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")
def fixed_path(length, stages): return np.minimum(stages-1, (np.arange(length,dtype=np.int64)*stages)//length)


@dataclass
class Panel:
    rows:list[dict]; original_lengths:np.ndarray; interior_lengths:np.ndarray; splits:np.ndarray; curriers:np.ndarray; folios:np.ndarray


def load_panel():
    with PANEL_PATH.open(encoding="utf-8",newline="") as h:
        reader=csv.DictReader(h,delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS: raise ValueError("schema")
        rows=list(reader)
    if len(rows)!=19203 or len({r['unit_id'] for r in rows})!=19203: raise ValueError("identity")
    original=np.asarray([int(r['original_symbol_count']) for r in rows],dtype=np.int64); interior=np.asarray([int(r['interior_symbol_count']) for r in rows],dtype=np.int64)
    if Counter(r['split'] for r in rows)!={"TRAIN":9364,"CAL":4887,"TEST":4952} or not np.array_equal(interior,original-2): raise ValueError("geometry")
    return Panel(rows,original,interior,np.asarray([r['split'] for r in rows]),np.asarray([r['currier'] for r in rows]),np.asarray([r['physical_folio'] for r in rows]))


def fit(panel,sequences,candidate):
    stages=1 if candidate=="K1" else int(candidate.split('_')[1])
    counts={(c,l):np.full((stages,24),ALPHA,dtype=np.float64) for c in 'AB' for l in range(3,12)}
    for row,seq,olen in zip(panel.rows,sequences,panel.original_lengths):
        if row['split']!='TRAIN': continue
        path=np.zeros(len(seq),dtype=np.int64) if candidate=='K1' else fixed_path(len(seq),stages); cell=counts[(row['currier'],int(olen))]
        for state,symbol in zip(path,seq): cell[state,symbol]+=1.
    return {key:value/value.sum(axis=1,keepdims=True) for key,value in counts.items()}


def probability(seq,olen,currier,candidate,models):
    theta=models[(currier,olen)]; path=np.zeros(len(seq),dtype=np.int64) if candidate=='K1' else fixed_path(len(seq),int(candidate.split('_')[1]))
    return float(np.log(theta[path,np.asarray(seq)]).sum())


def sign_p(pos,total): return sum(math.comb(total,k) for k in range(pos,total+1))/(2**total)
def summary(values):
    effects=[]
    for folio in sorted(values,key=lambda v:int(v[1:])): effects.append(sum(x for x,_ in values[folio])/sum(n for _,n in values[folio]))
    a=np.asarray(effects,dtype=np.float64); deletion=(a.sum()-a)/(len(a)-1); total=float(np.abs(a).sum())
    return {"effect_equal_folio":float(a.mean()),"positive_folios":int((a>0).sum()),"folios":len(a),"sign_p":sign_p(int((a>0).sum()),len(a)),"minimum_leave_one_folio_out":float(deletion.min()),"max_abs_contribution_fraction":float(np.abs(a).max()/total) if total else 1.}


def evaluate(panel,sequences):
    if len(sequences)!=len(panel.rows) or any(len(s)!=n for s,n in zip(sequences,panel.interior_lengths)): raise ValueError("geometry")
    if any(not s or any(x<0 or x>=24 for x in s) for s in sequences): raise ValueError("symbol")
    models={c:fit(panel,sequences,c) for c in CANDIDATES}; diagnostics={}
    for candidate in CANDIDATES:
        ll=0.; symbols=0
        for row,seq,olen in zip(panel.rows,sequences,panel.original_lengths):
            if row['split']=='CAL': ll+=probability(seq,int(olen),row['currier'],candidate,models[candidate]); symbols+=len(seq)
        diagnostics[candidate]={"cal_log_likelihood_per_symbol":ll/symbols}
    order={c:i for i,c in enumerate(CANDIDATES)}; selected=max(CANDIDATES,key=lambda c:(diagnostics[c]['cal_log_likelihood_per_symbol'],-order[c]))
    by,unseen_by=defaultdict(list),defaultdict(list); cur={'A':defaultdict(list),'B':defaultdict(list)}
    train={(r['currier'],int(n),s) for r,n,s in zip(panel.rows,panel.original_lengths,sequences) if r['split']=='TRAIN'}
    total=unseen_total=0.; tg=ts=ug=us=0
    for row,seq,olen in zip(panel.rows,sequences,panel.original_lengths):
        if row['split']!='TEST': continue
        gain=probability(seq,int(olen),row['currier'],selected,models[selected])-probability(seq,int(olen),row['currier'],'K1',models['K1']); n=len(seq); f=row['physical_folio']
        by[f].append((gain,n));cur[row['currier']][f].append((gain,n));total+=gain;tg+=1;ts+=n
        if (row['currier'],int(olen),seq) not in train: unseen_by[f].append((gain,n));unseen_total+=gain;ug+=1;us+=n
    return {"selected_model":selected,"candidate_diagnostics":diagnostics,"test_groups":tg,"test_symbols":ts,"gain_equal_symbol":total/ts,"gain":summary(by),"unseen":{"groups":ug,"symbols":us,"gain_equal_symbol":unseen_total/us,**summary(unseen_by)},"currier":{c:{"gain":summary(cur[c])} for c in 'AB'}}


def passes(r):
    return (r['selected_model']!='K1' and r['test_groups']==4952 and r['gain']['folios']==24 and r['gain']['effect_equal_folio']>=.015 and r['gain']['positive_folios']>=18 and r['gain']['sign_p']<=.01 and r['gain']['minimum_leave_one_folio_out']>0 and r['gain']['max_abs_contribution_fraction']<=.15 and r['unseen']['groups']>=500 and r['unseen']['effect_equal_folio']>=.01 and r['unseen']['minimum_leave_one_folio_out']>0 and all(r['currier'][c]['gain']['effect_equal_folio']>=.005 and r['currier'][c]['gain']['minimum_leave_one_folio_out']>0 and r['currier'][c]['gain']['positive_folios']/r['currier'][c]['gain']['folios']>=.65 for c in 'AB'))


def synthetic(panel,world,mode):
    if mode not in {'NULL','POSITION','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'}: raise ValueError("mode")
    folios=sorted(set(panel.folios),key=lambda v:int(v[1:])); active_folio=folios[world%len(folios)]
    maps={c:tuple(sorted(range(24),key=lambda x:stable(f"SNWGI001|{world}|MAP|{c}|{x}"))[:5]) for c in 'AB'}; out=[]
    for row,olen,ilen in zip(panel.rows,panel.original_lengths,panel.interior_lengths):
        olen=int(olen);ilen=int(ilen);bucket=stable(f"SNWGI001|BUCKET|{row['unit_id']}")%128
        base=sorted(range(24),key=lambda x:stable(f"SNWGI001|{world}|BASE|{row['currier']}|{olen}|{x}")); stage_map=maps[row['currier']]
        if mode=='FOLIO_RANDOM': stage_map=tuple(sorted(range(24),key=lambda x:stable(f"SNWGI001|{world}|FMAP|{row['physical_folio']}|{row['currier']}|{x}"))[:5])
        path=fixed_path(ilen,5);seq=[]
        for pos in range(ilen):
            u=(stable(f"SNWGI001|{world}|U|{row['split']}|{row['currier']}|{olen}|{bucket}|{pos}")+.5)/(1<<64)
            symbol=base[0] if u<.36 else (base[1] if u<.57 else stable(f"SNWGI001|{world}|R|{row['split']}|{row['currier']}|{olen}|{bucket}|{pos}")%24)
            active=mode in {'POSITION','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'} and (mode!='CURRIER_ONE' or row['currier']=='B') and (mode!='ONE_FOLIO' or row['physical_folio']==active_folio)
            if active and u<.55: symbol=stage_map[int(path[pos])]
            seq.append(int(symbol))
        out.append(tuple(seq))
    return out


def compact(r): return {**r,"INTERIOR_POSITION_PASS":passes(r)}
def worker(payload):
    mode,world,reverse=payload;seq=synthetic(PANEL,world,mode)
    if reverse: seq=[tuple(reversed(x)) for x in seq]
    return mode,world,reverse,compact(evaluate(PANEL,seq))
def numeric_max(a,b):
    if isinstance(a,dict): return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
    if isinstance(a,list): return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
    if isinstance(a,(int,float)) and not isinstance(a,bool): return abs(float(a)-float(b))
    return 0. if a==b else math.inf


def finite_floats(value):
    if isinstance(value,dict): return all(finite_floats(child) for child in value.values())
    if isinstance(value,list): return all(finite_floats(child) for child in value)
    return not isinstance(value,float) or math.isfinite(value)


def expected_report(status,decision,counts,passed):
    return f"""# Endpoint-free source-group interior-position preflight

Status: **{status}**

Forward/reversed grids produce **{counts['forward']['NULL']['passes']}/64** and
**{counts['reversed']['NULL']['passes']}/64** null passes, and
**{counts['forward']['POSITION']['passes']}/8** and
**{counts['reversed']['POSITION']['passes']}/8** position-plant passes.
Currier-one, one-folio, and folio-random adversaries produce zero passes in both
orientations. All 96 decisions are reversal-stable; label relabeling, capacity,
finite-value, mutation, isolation, and target-absence gates are
**{'passing' if passed else 'not all passing'}**.

The target source was existence-tested only; zero family sequences or scores
were opened. Decision: **{decision}**. No morphology, sound, word, language,
meaning, plaintext, cipher, or translation follows.
"""


def main():
    global PANEL
    if OUT.exists() or REPORT.exists(): raise SystemExit("refusing overwrite")
    failures=[];checks=0
    def check(ok,name):
        nonlocal checks;checks+=1
        if not ok: failures.append(name)
    for path,expected in FROZEN.items(): check(sha(path)==expected,f"hash:{path.name}")
    PANEL=load_panel();payloads=[(m,w,r) for r in (False,True) for m,w in TASKS]
    with mp.get_context('fork').Pool(32) as pool: rebuilt=pool.map(worker,payloads)
    index={(m,w,r):v for m,w,r,v in rebuilt}; prod=json.loads(PRODUCTION.read_text()); stored={(x['mode'],x['world'],x['reverse']):x for x in prod['records']}
    check(set(index)==set(stored),"identities");max_delta=0.
    for key,value in index.items():
        delta=numeric_max({"mode":key[0],"world":key[1],"reverse":key[2],**value},stored[key]);max_delta=max(max_delta,delta);check(delta<=1e-12,f"record:{key}")
    counts={}
    for reverse in (False,True):
        name='reversed' if reverse else 'forward';counts[name]={m:{"worlds":sum(x==m for x,_ in TASKS),"passes":sum(index[(m,w,reverse)]['INTERIOR_POSITION_PASS'] for x,w in TASKS if x==m)} for m in ('NULL','POSITION','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM')}
    check(prod['counts']==counts,"counts")
    mismatches=[f"{m}:{w}" for m,w in TASKS if index[(m,w,False)]['INTERIOR_POSITION_PASS']!=index[(m,w,True)]['INTERIOR_POSITION_PASS']];check(prod['reversal_decision_mismatches']==mismatches,"reversal")
    refseq=synthetic(PANEL,100,'POSITION');ref=compact(evaluate(PANEL,refseq));perm=np.asarray([(7*x+3)%24 for x in range(24)],dtype=np.int64);rel=compact(evaluate(PANEL,[tuple(int(perm[x]) for x in s) for s in refseq]));label_delta=numeric_max(ref,rel);check(abs(prod['label_relabel_max_abs']-label_delta)<=1e-12,"labels")
    mutations={}
    for name,altered in (("missing_sequence",refseq[:-1]),("length_mismatch",[tuple()]+refseq[1:]),("invalid_symbol",[(-1,)+refseq[0][1:]]+refseq[1:])):
        try:evaluate(PANEL,altered)
        except ValueError:mutations[name]=True
        else:mutations[name]=False
    ids=[r['unit_id'] for r in PANEL.rows];mutations['duplicate_unit_id']=len(set(ids+[ids[0]]))!=len(ids)+1;check(prod['mutations']==mutations,"mutations")
    pattern=lambda name:counts[name]['NULL']['passes']<=1 and counts[name]['POSITION']['passes']>=7 and all(counts[name][m]['passes']==0 for m in ('CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'))
    gates={"forward_expected_pattern":pattern('forward'),"reversed_expected_pattern":pattern('reversed'),"all_96_decisions_reversal_stable":not mismatches,"label_relabel_invariance":label_delta<=1e-10,"finite_values":all(finite_floats(value) for value in index.values()),"mutation_guards":all(mutations.values()),"exact_capacity":len(PANEL.rows)==19203 and sum(PANEL.splits=='TEST')==4952 and int(PANEL.interior_lengths.sum())==45867 and len(set(PANEL.folios))==94,"target_absent":not TARGET_OUT.exists() and not TARGET_REPORT.exists()}
    check(prod['gates']==gates,"gates");check(all(gates.values()),"pass");check(prod['status']=='PASS_TARGET_FREE_WITHIN_GROUP_INTERIOR_PREFLIGHT' and prod['decision']=='GO_INDEPENDENTLY_VALIDATE_INTERIOR_PREFLIGHT',"decision");check(prod['target_source_opened'] is False and prod['target_sequences_accessed']==0 and prod['target_scores_computed']==0 and prod['target_outputs_absent'] is True,"isolation");check(PRODUCTION_REPORT.read_text()==expected_report(prod['status'],prod['decision'],counts,True),"report")
    if failures: raise SystemExit("validation failed: "+failures[0])
    result={"experiment":"SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_PREFLIGHT_VALIDATION","status":"PASS_INDEPENDENT_192_WORLD_INTERIOR_PREFLIGHT_RECONSTRUCTION","checks":checks,"failures":[],"reconstructed_worlds":192,"counts":counts,"max_record_numeric_delta":max_delta,"target_source_opened":False,"target_sequences_accessed":0,"target_scores_computed":0,"target_outputs_absent":True,"inputs":{p.name:sha(p) for p in FROZEN},"claim_ceiling":"Independent synthetic reconstruction only; no morphology, sound, word, language, meaning, plaintext, cipher, or translation follows."}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");REPORT.write_text(f"""# Endpoint-free interior preflight validation

Status: **{result['status']}**

A nonimporting implementation reconstructs all **192** original/reversed
synthetic records, counts, invariance, mutations, gates, decision, and report
in **{checks} checks**, with maximum numeric discrepancy **{max_delta:.3g}**.
The manuscript target remains unopened and absent.

This validates calibration only and supplies no morphology, sound, word,
language, meaning, plaintext, cipher, or translation.
""");print(json.dumps({"status":result['status'],"checks":checks,"max_delta":max_delta},sort_keys=True))


if __name__=='__main__':main()
