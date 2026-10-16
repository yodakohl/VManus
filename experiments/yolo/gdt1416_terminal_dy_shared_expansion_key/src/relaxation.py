#!/usr/bin/env python3
"""Postresult ordinary-subset diagnostic using unchanged validated solvers."""
import hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

def main():
    lock=read(E/'DIAGNOSTIC_LOCK.json')
    for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
    primary=module('ordinary_primary','experiments/yolo/gdt1414_local_homophonic_run_key/src/run.py')
    independent=module('ordinary_independent','experiments/yolo/gdt1414_local_homophonic_run_key/src/validate.py')
    s=read(E/'src/SPEC.json');W=primary.sources(s);control=read(A/'CONTROL.json')
    keep=lambda g:g[-2:]!=['d','y']
    controlled=[g for g in control['collapsed_groups'] if keep(g)]
    planted=control['planted_key'];assert controlled
    assert all(''.join(planted[u] for u in g) in set(W['deot']) for g in controlled)
    recovered=primary.solve(controlled,W['deot'],s['signs'],'BIDIR',s)
    assert recovered['status']=='SAT'
    independent.direct(recovered,controlled,W['deot'],s['signs'],'BIDIR')
    original=read(A/'RESULT.json');ids=[i for i,g in enumerate(original['groups']) if keep(g)];groups=[original['groups'][i] for i in ids]
    assert 0<len(groups)<77
    cases=[]
    for name in s['source_names']:
        for mode in s['modes']:
            r=primary.solve(groups,W[name],s['signs'],mode,s)
            if r['status']=='UNSAT':
                other=independent.solve(groups,W[name],s['signs'],mode,15)
                decision='DY_ONLY_CHANGES_INSUFFICIENT' if other['status']=='UNSAT' else 'DISAGREEMENT' if other['status']=='SAT' else 'UNCONFIRMED'
            elif r['status']=='SAT':
                independent.direct(r,groups,W[name],s['signs'],mode);other=dict(status='SAT_CERTIFICATE_VERIFIED');decision='ORDINARY_SUBSET_CAPACITY_ONLY'
            else:other=dict(status='PRIMARY_UNKNOWN_PRESERVED');decision='UNRESOLVED'
            cases.append(dict(source=name,mode=mode,primary=r,independent=other,decision=decision))
            print(json.dumps(dict(source=name,mode=mode,decision=decision)),flush=True)
    result=dict(experiment_id='GDT1416',status='POSTRESULT_ORDINARY_SUBSET_DIAGNOSTIC',selection='all and only non-dy-ending post-inverse groups',positions_zero_based=ids,retained_occurrences=len(groups),retained_distinct_forms=len(set(map(tuple,groups))),unconstrained_occurrences=77-len(groups),control=dict(positions=len(controlled),recovered=recovered,status='PASS_ANY_KEY_NOT_ORIGINAL_RECOVERY'),cases=cases,diagnostic_lock_sha256=sha(E/'DIAGNOSTIC_LOCK.json'),ceiling='Only fixed8W/non-dy ordinarykey premises. No broader ending/source/language exclusion; original1416decision preserved. Postresult selected, not original preregistration.')
    path=A/'RELAXATION.json'
    if path.exists():assert read(path)==result
    else:path.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
    assert all(c['decision']!='DISAGREEMENT' for c in cases)
if __name__=='__main__':main()
