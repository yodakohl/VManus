#!/usr/bin/env python3
"""Anonymous fit orchestration; gold opens only in explicit post-lock score stage."""
import argparse,concurrent.futures,gzip,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import numpy as np
EXP=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def packed(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress((json.dumps(x,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0))

def job(task):
    from fit import fit_payload
    fold,world,path,runtime=task
    with np.load(path,allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
    output=fit_payload(arrays,models=('F','B','G') if world==0 else ('B','G'))
    output['fold']=fold;output['world']=world;output['payload_sha256']=sha(path)
    full=runtime/f'fold_{fold}'/f'fit_{world:02d}.json.gz';packed(full,output)
    dest=EXP/'artifacts/predictions'/f'fold_{fold}_world_{world:02d}.json.gz';packed(dest,output)
    return {'fold':fold,'world':world,'path':str(dest.relative_to(EXP)),'sha256':sha(dest),'payload_sha256':sha(path),'runtime_full_sha256':sha(full),
        'selected_objectives':{k:m['selected_objective'] for k,m in output['models'].items()}}

def fit_all(runtime,workers):
    assert 1<=workers<=32
    capacity=read(EXP/'artifacts/CAPACITY_VALIDATION.json');assert capacity['status']=='PASS'
    receipt=read(EXP/'artifacts/GEOMETRY.json');assert receipt['status']=='CAPACITY_PASS' and receipt['nulls_built']
    tasks=[]
    for f in receipt['folds']:
        assert [p['world'] for p in f['world_payloads']]==list(range(20))
        for p in f['world_payloads']:
            path=runtime/p['path'];assert sha(path)==p['sha256'];tasks.append((f['fold'],p['world'],path,runtime))
    assert len(tasks)==80
    # F's invariant arrays must match every world before reuse is allowed.
    for fold in range(4):
        with np.load(runtime/f'fold_{fold}/world_00.npz') as base:
            for world in range(1,20):
                with np.load(runtime/f'fold_{fold}/world_{world:02d}.npz') as z:
                    for k in ['p','q','written_rates','reference_rates']:assert np.array_equal(base[k],z[k])
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(job,t) for t in tasks]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result());print(json.dumps({'completed':len(results),'total':80,'fold':results[-1]['fold'],'world':results[-1]['world']}),flush=True)
    results.sort(key=lambda r:(r['fold'],r['world']))
    for r in results:
        if r['world']:
            base=next(b for b in results if b['fold']==r['fold'] and b['world']==0)
            r['F_reuse']={'path':base['path'],'sha256':base['sha256'],'exact_frequency_inputs_checked':True}
    lock={'experiment':'GDT1164','status':'ALL_PREDICTIONS_LOCKED_BEFORE_GOLD','locked_utc':datetime.now(timezone.utc).isoformat(),
        'site_truth_read':False,'jobs':80,'starts':492,'predictions':results,
        'bindings':{str(p.relative_to(EXP)):sha(p) for p in [EXP/'METHOD.md',EXP/'SPEC.json',EXP/'src/prepare.py',EXP/'src/fit.py',EXP/'src/run.py',EXP/'src/score.py',EXP/'artifacts/GEOMETRY.json',EXP/'artifacts/CAPACITY_VALIDATION.json',EXP/'artifacts/BUILDER_AUDIT.json.gz']}}
    (EXP/'artifacts/PREDICTION_LOCK.json').write_text(json.dumps(lock,indent=2)+'\n')
    print('ALL_PREDICTIONS_LOCKED_BEFORE_GOLD',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--workers',type=int,default=16);p.add_argument('--stage',choices=['fit','score'],required=True);p.add_argument('--release-gold',action='store_true');a=p.parse_args()
    if a.stage=='fit':assert not a.release_gold;fit_all(a.runtime,a.workers)
    else:
        assert a.release_gold,'Gold requires explicit post-lock --release-gold'
        from score import score_locked
        score_locked(a.runtime)
if __name__=='__main__':main()
