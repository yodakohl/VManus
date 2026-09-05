#!/usr/bin/env python3
"""Train-only paired typed/anonymous mixed-key control; never opens held or truth."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
UPSTREAM=EXP.parent/'gdt832_joint_family_context_control/src'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def atom_id(atom,arm):
    if arm=='BLIND':
        if len(atom)!=3 or atom[0]!='X' or not 0<=int(atom[1:])<38:raise ValueError('opaque ID')
        return int(atom[1:])
    if len(atom)!=3 or atom[0] not in 'LSW':raise ValueError('typed ID')
    n=int(atom[1:]);offset,limit={'L':(0,26),'S':(26,4),'W':(30,8)}[atom[0]]
    if not 0<=n<limit:raise ValueError('typed range')
    return offset+n

def atom_name(i,arm):
    if arm=='BLIND':return f'X{i:02d}'
    return f'L{i:02d}' if i<26 else f'S{i-26:02d}' if i<30 else f'W{i-30:02d}'

def projection(source,candidates,target,arm):
    source=Path(source)
    if not source.name.endswith('_discovery.json'):raise ValueError('discovery source required')
    data=json.loads(source.read_text())
    if data.get('split')!='discovery':raise ValueError('discovery split required')
    counts=Counter(tuple(atom_id(a,arm) for a in w) for p in data['paragraphs'] for w in p['words'])
    words=sorted(counts);ids={w:i for i,w in enumerate(words)};edges=Counter()
    for p in data['paragraphs']:
        seq=[ids[tuple(atom_id(a,arm) for a in w)] for w in p['words']]
        edges.update(zip(seq,seq[1:]))
    suffix=candidates['suffix_pool'];whole=candidates['wholeword_pool']
    lines=[f'SUFFIX {len(suffix)}',' '.join(suffix),f'WHOLE {len(whole)}',' '.join(whole),f'WORDS {len(words)}']
    lines.extend(f'{counts[w]} {len(w)} '+' '.join(map(str,w)) for w in words)
    lines.append(f'TRANSITIONS {len(edges)}')
    lines.extend(f'{u} {v} {n}' for (u,v),n in sorted(edges.items()))
    lines.append('FAMILIES 0')
    Path(target).write_text('\n'.join(lines)+'\n')
    return {'cipher_sha256':sha(source),'projection_sha256':sha(target),'word_types':len(words),'word_tokens':sum(counts.values())}

def parse_result(path,arm):
    key={};objective=None;proposals=None
    for line in Path(path).read_text().splitlines():
        row=line.split('\t')
        if row[0]=='SCORE':objective={'total_nats':float(row[1]),'language_nats':float(row[2]),'family_nats':float(row[3])}
        elif row[0]=='PROPOSALS':proposals=int(row[1])
        else:key[atom_name(int(row[0]),arm)]={'role':row[1],'output':row[2]}
    if len(key)!=38 or objective is None or proposals is None:raise ValueError('incomplete fit')
    return key,objective,proposals

def job(plan):
    subprocess.run([plan['binary'],plan['model'],plan['projection'],plan['arm'],str(plan['seed']),str(plan['start']),str(plan['steps']),str(plan['sweeps']),plan['raw']],check=True,capture_output=True)
    key,objective,proposals=parse_result(plan['raw'],plan['arm'])
    out={k:plan[k] for k in ('world_id','arm','start','seed')}
    out.update(schema='GDT834_FIT_V1',key=key,discovery_objective=objective,proposals=proposals,input_hashes=plan['input_hashes'])
    save(plan['output'],out)
    return plan['output']

def verify_registration():
    reg=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for rel,digest in reg['sha256'].items():
        p=(EXP/rel).resolve()
        if not p.is_relative_to(EXP) or sha(p)!=digest:raise ValueError('registration mismatch '+rel)
    for rel,digest in reg['upstream_sha256'].items():
        p=(ROOT/rel).resolve()
        if not p.is_relative_to(ROOT) or sha(p)!=digest:raise ValueError('upstream mismatch '+rel)

def lock_fits(spec):
    paths=[];selections=[]
    for world in spec['world_ids']:
        for arm in spec['arms']:
            files=[EXP/f'artifacts/fits/world_{world}_{arm}_start{s}.json' for s in spec['starts']]
            fits=[json.loads(p.read_text()) for p in files]
            for fit,start in zip(fits,spec['starts']):
                if (fit['world_id'],fit['arm'],fit['start'])!=(world,arm,start):raise ValueError('fit identity')
            selected=min(fits,key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
            target=EXP/f'artifacts/fits/world_{world}_{arm}_selected.json';save(target,selected)
            paths.extend(p.relative_to(EXP).as_posix() for p in files);selections.append(target.relative_to(EXP).as_posix())
    lock={'schema':'GDT834_FIT_LOCK_V1','restarts':sorted(paths),'selected':sorted(selections),'spec_sha256':sha(EXP/'src/SPEC.json'),'sha256':{p:sha(EXP/p) for p in sorted(paths+selections)}}
    save(EXP/'artifacts/FIT_LOCK.json',lock)
    return lock

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fit',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--workers',type=int,default=24);args=parser.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text());verify_registration()
    if args.check:
        lock=json.loads((EXP/'artifacts/FIT_LOCK.json').read_text())
        assert len(lock['restarts'])==48 and len(lock['selected'])==6 and lock['spec_sha256']==sha(EXP/'src/SPEC.json')
        for rel,digest in lock['sha256'].items():assert sha(EXP/rel)==digest
        print('FIT_LOCK_PASS; no held or truth read');return
    if not args.fit:parser.error('choose --fit or --check')
    if (EXP/'artifacts/FIT_LOCK.json').exists():raise RuntimeError('refuse overwrite of locked fits')
    cap=json.loads((EXP/'prepared/CAPACITY.json').read_text())
    if cap['status']!='SOURCE_CAPACITY_PASS':raise RuntimeError('source capacity failed')
    ambiguity=json.loads((EXP/'artifacts/ROLE_AMBIGUITY.json').read_text())
    if ambiguity['status']!='ROLE_AMBIGUITY_PASS':raise RuntimeError('role ambiguity failed')
    runtime=EXP/'runtime';runtime.mkdir(exist_ok=True);model=runtime/'reference'
    subprocess.run([sys.executable,str(UPSTREAM/'reference_model.py'),'--reference',str(EXP/'prepared/reference.jsonl'),'--families',str(EXP/'prepared/families.json'),'--out',str(model)],check=True)
    binary=runtime/'decoder';subprocess.run(['g++','-std=c++17','-O3','-DNDEBUG',str(EXP/'src/decoder.cpp'),'-o',str(binary)],check=True)
    candidates=json.loads((EXP/'prepared/candidates.json').read_text());plans=[];metadata={}
    for world in spec['world_ids']:
        for arm in spec['arms']:
            source=EXP/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}discovery.json'
            table=runtime/f'world_{world}_{arm}.txt';meta=projection(source,candidates,table,arm);metadata[f'{world}_{arm}']=meta
            for start in spec['starts']:
                name=f'world_{world}_{arm}_start{start}'
                plans.append(dict(world_id=world,arm=arm,start=start,seed=83400000+100*world+start,steps=spec['optimizer']['annealing_steps'],sweeps=spec['optimizer']['polish_sweeps'],binary=str(binary),model=str(model),projection=str(table),raw=str(runtime/(name+'.tsv')),output=str(EXP/'artifacts/fits'/(name+'.json')),input_hashes={**meta,'model_meta_sha256':sha(model/'model_meta.json'),'decoder_sha256':sha(EXP/'src/decoder.cpp'),'spec_sha256':sha(EXP/'src/SPEC.json')}))
    save(EXP/'artifacts/FIT_INPUTS.json',metadata)
    with ProcessPoolExecutor(max_workers=min(24,max(1,args.workers))) as pool:
        futures=[pool.submit(job,plan) for plan in plans]
        for n,future in enumerate(as_completed(futures),1):future.result();print(f'completed discovery fits {n}/{len(plans)}',flush=True)
    lock=lock_fits(spec);print(json.dumps({'status':'FITS_LOCKED_UNEVALUATED','restarts':len(lock['restarts']),'selected':len(lock['selected'])}))
if __name__=='__main__':main()
