#!/usr/bin/env python3
"""Paired reference intervention using the byte-frozen GDT832 OFF decoder.

Only reference/discovery data are interpreted here. Held ciphertext and control
truth have separate commitments and are never opened by this fitter.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
UPSTREAM=EXP.parent/'gdt832_joint_family_context_control'/'src'


def load_upstream():
    spec=importlib.util.spec_from_file_location('gdt833_base_run',UPSTREAM/'run.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def fit_plan(spec):
    for world in spec['world_ids']:
        for condition in spec['reference_conditions']:
            for start in spec['starts']:
                yield {'world_id':world,'reference_condition':condition,'start':start,
                       'seed':83300000+100*world+start,'engine_arm':'OFF',
                       'steps':spec['optimizer']['annealing_steps'],
                       'sweeps':spec['optimizer']['polish_sweeps']}


def fit_job(job):
    args=[job['binary'],job['model'],job['projection'],'OFF',str(job['seed']),
          str(job['start']),str(job['steps']),str(job['sweeps']),job['raw_output']]
    subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    key,objective,proposals=load_upstream().parse_cpp(Path(job['raw_output']))
    if objective['family_nats'] != 0:
        raise ValueError('Family objective must remain OFF')
    out={k:job[k] for k in ('world_id','reference_condition','start','seed','engine_arm')}
    out.update(schema='GDT833_FIT_V1',key=key,discovery_objective=objective,
               proposals=proposals,input_hashes=job['input_hashes'])
    save(job['output'],out)
    return job['output']


def select_and_lock(spec,exp=EXP):
    exp=Path(exp);selected_paths=[];restart_paths=[]
    for world in spec['world_ids']:
        for condition in spec['reference_conditions']:
            paths=[exp/'artifacts/fits'/f'world_{world}_{condition}_start{s}.json' for s in spec['starts']]
            fits=[json.loads(p.read_text()) for p in paths]
            for fit,start in zip(fits,spec['starts']):
                if (fit['world_id'],fit['reference_condition'],fit['start']) != (world,condition,start):
                    raise ValueError('Misidentified restart fit')
            winner=min(fits,key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
            target=exp/'artifacts/fits'/f'world_{world}_{condition}_selected.json'
            save(target,winner)
            selected_paths.append(target.relative_to(exp).as_posix())
            restart_paths.extend(p.relative_to(exp).as_posix() for p in paths)
    lock={'schema':'GDT833_FIT_LOCK_V1','selected':sorted(selected_paths),'restarts':sorted(restart_paths),
          'sha256':{p:digest(exp/p) for p in sorted(selected_paths+restart_paths)},
          'spec_sha256':digest(exp/'src/SPEC.json')}
    save(exp/'artifacts/FIT_LOCK.json',lock)
    return lock


def verify_registration():
    reg=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for relative,expected in reg['sha256'].items():
        path=(EXP/relative).resolve()
        if not path.is_relative_to(EXP) or digest(path)!=expected:
            raise ValueError('Registration mismatch: '+relative)
    for relative,expected in reg['upstream_sha256'].items():
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or digest(path)!=expected:
            raise ValueError('Upstream source mismatch: '+relative)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fit',action='store_true')
    p.add_argument('--check',action='store_true')
    p.add_argument('--workers',type=int,default=24)
    args=p.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    if args.check:
        verify_registration()
        lock=json.loads((EXP/'artifacts/FIT_LOCK.json').read_text())
        assert len(lock['restarts'])==48 and len(lock['selected'])==6
        assert lock['spec_sha256']==digest(EXP/'src/SPEC.json')
        for relative,expected in lock['sha256'].items():assert digest(EXP/relative)==expected
        print('FIT_LOCK_PASS; no held ciphertext or truth opened')
        return 0
    if not args.fit:p.error('choose --fit or --check')
    if (EXP/'artifacts/FIT_LOCK.json').exists():raise RuntimeError('Fits already locked; refuse overwrite')
    verify_registration()
    cap=json.loads((EXP/'prepared/CAPACITY.json').read_text())
    if cap['status']!='SOURCE_CAPACITY_PASS':raise RuntimeError('Source capacity not passed')
    runtime=EXP/'runtime';runtime.mkdir(exist_ok=True)
    models={}
    for condition in spec['reference_conditions']:
        model=runtime/('reference_'+condition.lower());models[condition]=model
        subprocess.run([sys.executable,str(UPSTREAM/'reference_model.py'),'--reference',
                        str(EXP/'prepared'/('reference_'+condition.lower()+'.jsonl')),
                        '--families',str(EXP/'prepared/families.json'),'--out',str(model)],check=True)
    binary=runtime/'decoder'
    subprocess.run(['g++','-std=c++17','-O3','-DNDEBUG',str(UPSTREAM/'decoder.cpp'),'-o',str(binary)],check=True)
    candidates=json.loads((EXP/'prepared/candidates.json').read_text())
    tables={};inputmeta={}
    base=load_upstream()
    for world in spec['world_ids']:
        table=runtime/f'world_{world}_discovery.txt';tables[world]=table
        inputmeta[world]=base.projection(EXP/'prepared'/f'world_{world}_discovery.json',candidates,table)
    save(EXP/'artifacts/FIT_INPUTS.json',inputmeta)
    jobs=[]
    for plan in fit_plan(spec):
        world=plan['world_id'];condition=plan['reference_condition'];start=plan['start']
        name=f'world_{world}_{condition}_start{start}'
        plan.update(binary=str(binary),model=str(models[condition]),projection=str(tables[world]),
                    raw_output=str(runtime/(name+'.tsv')),output=str(EXP/'artifacts/fits'/(name+'.json')),
                    input_hashes={**inputmeta[world],'model_meta_sha256':digest(models[condition]/'model_meta.json'),
                                  'decoder_source_sha256':digest(UPSTREAM/'decoder.cpp'),
                                  'spec_sha256':digest(EXP/'src/SPEC.json')})
        jobs.append(plan)
    with ProcessPoolExecutor(max_workers=min(24,max(1,args.workers))) as pool:
        futures=[pool.submit(fit_job,j) for j in jobs]
        for n,future in enumerate(as_completed(futures),1):
            future.result();print(f'completed discovery fits {n}/{len(jobs)}',flush=True)
    lock=select_and_lock(spec)
    print(json.dumps({'status':'FITS_LOCKED_UNEVALUATED','restarts':len(lock['restarts']),'selected':len(lock['selected'])}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
