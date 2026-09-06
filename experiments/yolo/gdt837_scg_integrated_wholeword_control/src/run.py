#!/usr/bin/env python3
"""Paired discovery-only wrapper around the unchanged GDT836 search engine."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,hashlib,json,math
from pathlib import Path
import subprocess,sys

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
MODEL_SOURCE=EXP.parent/'gdt832_joint_family_context_control/src/reference_model.py'
ENGINE_SOURCE=EXP.parent/'gdt836_integrated_wholeword_precedence/src/decoder.cpp'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_json(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.name.endswith('.gz') else raw)
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def atom_id(atom):
    if not isinstance(atom,str) or len(atom)!=3 or atom[0]!='X' or not atom[1:].isdigit() or not 0<=int(atom[1:])<38:raise ValueError('opaque atom ID')
    return int(atom[1:])

def projection(source,candidates,target):
    source=Path(source)
    if not source.name.endswith('_discovery.json.gz'):raise ValueError('discovery filename required before reading')
    raw=source.read_bytes();plain=gzip.decompress(raw);data=json.loads(plain)
    if data.get('split')!='discovery' or data.get('unit_type')!='source_sentence':raise ValueError('discovery source-sentence payload required')
    counts=Counter(tuple(atom_id(a) for a in w) for p in data['paragraphs'] for w in p['words'])
    if not counts or () in counts:raise ValueError('nonempty cipher words required')
    words=sorted(counts);ids={w:i for i,w in enumerate(words)};edges=Counter()
    for p in data['paragraphs']:
        seq=[ids[tuple(atom_id(a) for a in w)] for w in p['words']];edges.update(zip(seq,seq[1:]))
    suffix,whole=candidates['suffix_pool'],candidates['wholeword_pool']
    lines=[f'SUFFIX {len(suffix)}',' '.join(suffix),f'WHOLE {len(whole)}',' '.join(whole),f'WORDS {len(words)}']
    lines.extend(f'{counts[w]} {len(w)} '+' '.join(map(str,w)) for w in words)
    lines.append(f'TRANSITIONS {len(edges)}');lines.extend(f'{u} {v} {n}' for (u,v),n in sorted(edges.items()));lines.append('FAMILIES 0')
    Path(target).write_text('\n'.join(lines)+'\n')
    return {'cipher_sha256':hashlib.sha256(raw).hexdigest(),'cipher_uncompressed_sha256':hashlib.sha256(plain).hexdigest(),'compressed_bytes':len(raw),'uncompressed_bytes':len(plain),'projection_sha256':sha(target),'word_types':len(words),'word_tokens':sum(counts.values()),'source_sentence_units':len(data['paragraphs']),'transition_types':len(edges),'atom_incidence_entries':sum(len(set(w)) for w in words)}

def parse_result(path):
    key={};initial={};meta={};objective=None
    for line in Path(path).read_text().splitlines():
        row=line.split('\t')
        if row[0]=='SCORE':
            if objective is not None or len(row)!=4:raise ValueError('exact SCORE fields required')
            values=list(map(float,row[1:]))
            if not all(math.isfinite(v) for v in values):raise ValueError('finite SCORE values required')
            objective=dict(zip(('total_nats','language_nats','family_nats'),values))
        elif row[0]=='INITIAL':
            if len(row)!=4 or row[2] not in ('L','S','W') or not row[3]:raise ValueError('initial package schema')
            a=int(row[1]);name=f'X{a:02d}';atom_id(name)
            if name in initial:raise ValueError('duplicate initial atom')
            initial[name]={'role':row[2],'output':row[3]}
        elif row[0] in ('PROPOSALS','INITIALIZATION_ATTEMPTS','INITIALIZATION_SEED','SEARCH_SEED','PRIORITY_REJECTIONS'):
            if len(row)!=2:raise ValueError('metadata schema')
            if row[0].lower() in meta:raise ValueError('duplicate metadata')
            meta[row[0].lower()]=int(row[1])
        else:
            if len(row)!=3 or row[1] not in ('L','S','W') or not row[2]:raise ValueError('final package schema')
            a=int(row[0]);name=f'X{a:02d}';atom_id(name)
            if name in key:raise ValueError('duplicate final atom')
            key[name]={'role':row[1],'output':row[2]}
    if len(key)!=38 or len(initial)!=38 or objective is None or len(meta)!=5:raise ValueError('incomplete engine output')
    return {'key':key,'initial_key':initial,'discovery_objective':objective,**meta}

def fit_plan(spec):
    for world in spec['world_ids']:
        for arm in spec['arms']:
            for start in spec['starts']:
                yield {'world_id':world,'arm':arm,'start':start,'search_seed':837000000+100*world+start,'initialization_seed':837500000+100*world+start,'steps':spec['optimizer']['annealing_steps'],'sweeps':spec['optimizer']['polish_sweeps']}

def fit_job(plan):
    args=[plan['binary'],plan['model'],plan['projection'],plan['arm'],str(plan['search_seed']),str(plan['initialization_seed']),str(plan['start']),str(plan['steps']),str(plan['sweeps']),plan['raw']]
    completed=subprocess.run(args,capture_output=True,text=True)
    out={k:plan[k] for k in ('world_id','arm','start','search_seed','initialization_seed')}
    if completed.returncode:
        if completed.stderr.strip()!='INITIALIZATION_STOP':raise RuntimeError('engine failure: '+completed.stderr.strip())
        out.update(status='INITIALIZATION_STOP',initialization_attempts=1000)
    else:
        parsed=parse_result(plan['raw'])
        if any(parsed[k]!=plan[k] for k in ('search_seed','initialization_seed')):raise ValueError('engine seed mismatch')
        out.update(status='FIT_COMPLETE',schema='GDT837_FIT_V1',**parsed,input_hashes=plan['input_hashes'])
    save(plan['output'],out);return out['status']

def verify_registration():
    reg=read_json(EXP/'src/PREREG_LOCK.json')
    for rel,digest in reg['sha256'].items():
        path=(EXP/rel).resolve()
        if not path.is_relative_to(EXP) or sha(path)!=digest:raise ValueError('registration mismatch '+rel)
    for rel,digest in reg['upstream_sha256'].items():
        path=(ROOT/rel).resolve()
        if not path.is_relative_to(ROOT) or sha(path)!=digest:raise ValueError('upstream mismatch '+rel)

def check_pairs(fits,spec):
    expected={(w,a,s) for w in spec['world_ids'] for a in spec['arms'] for s in spec['starts']}
    if len(fits)!=len(expected) or {(f['world_id'],f['arm'],f['start']) for f in fits}!=expected:raise ValueError('complete panel required')
    by_id={(f['world_id'],f['arm'],f['start']):f for f in fits}
    for world in spec['world_ids']:
        for start in spec['starts']:
            left,right=[by_id[world,arm,start] for arm in spec['arms']]
            for f in (left,right):
                if f['status']!='FIT_COMPLETE' or f['search_seed']!=837000000+100*world+start or f['initialization_seed']!=837500000+100*world+start or type(f['initialization_attempts']) is not int or not 1<=f['initialization_attempts']<=1000:raise ValueError('complete fixed fit required')
            for f in (left,right):
                if not all(math.isfinite(f['discovery_objective'][k]) for k in ('total_nats','language_nats','family_nats')):raise ValueError('finite objectives required')
            for field in ('initial_key','initialization_attempts','initialization_seed','search_seed'):
                if left[field]!=right[field]:raise ValueError('paired initialization mismatch '+field)

def lock_fits(spec,exp=EXP):
    exp=Path(exp)
    paths=[f'artifacts/fits/world_{p["world_id"]}_{p["arm"]}_start{p["start"]}.json' for p in fit_plan(spec)]
    fits=[read_json(exp/path) for path in paths];check_pairs(fits,spec)
    selected=[]
    for world in spec['world_ids']:
        for arm in spec['arms']:
            winner=min((f for f in fits if (f['world_id'],f['arm'])==(world,arm)),key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
            path=f'artifacts/fits/world_{world}_{arm}_selected.json';save(exp/path,winner);selected.append(path)
    lock={'schema':'GDT837_FIT_LOCK_V1','restarts':sorted(paths),'selected':sorted(selected),'spec_sha256':sha(exp/'src/SPEC.json'),'paired_initializations_identical':True,'sha256':{p:sha(exp/p) for p in sorted(paths+selected)}}
    save(exp/'artifacts/FIT_LOCK.json',lock);return lock

def prepare_resources(spec):
    runtime=EXP/'runtime';runtime.mkdir(exist_ok=True);model=runtime/'reference'
    subprocess.run([sys.executable,str(MODEL_SOURCE),'--reference',str(EXP/'prepared/reference.jsonl'),'--families',str(EXP/'prepared/families.json'),'--out',str(model)],check=True)
    candidates=read_json(EXP/'prepared/candidates.json');metadata={};tables={}
    for world in spec['world_ids']:
        table=runtime/f'world_{world}_discovery.txt';tables[world]=table
        metadata[str(world)]=projection(EXP/f'prepared/world_{world}_discovery.json.gz',candidates,table)
    return model,tables,metadata

def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--fit',action='store_true');mode.add_argument('--check',action='store_true');mode.add_argument('--prepare-verification',action='store_true');p.add_argument('--workers',type=int,default=24);a=p.parse_args()
    spec=read_json(EXP/'src/SPEC.json');verify_registration()
    if a.check:
        lock=read_json(EXP/'artifacts/FIT_LOCK.json')
        restarts=sorted(f'artifacts/fits/world_{p["world_id"]}_{p["arm"]}_start{p["start"]}.json' for p in fit_plan(spec))
        selected=sorted(f'artifacts/fits/world_{w}_{a}_selected.json' for w in spec['world_ids'] for a in spec['arms'])
        if lock['restarts']!=restarts or lock['selected']!=selected or set(lock['sha256'])!=set(restarts+selected) or lock['spec_sha256']!=sha(EXP/'src/SPEC.json') or lock.get('paired_initializations_identical') is not True:raise ValueError('fit lock inventory')
        for rel,h in lock['sha256'].items():
            if sha(EXP/rel)!=h:raise ValueError('fit lock bytes')
        fits=[read_json(EXP/r) for r in restarts];check_pairs(fits,spec)
        for w in spec['world_ids']:
            for a in spec['arms']:
                winner=min((f for f in fits if (f['world_id'],f['arm'])==(w,a)),key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
                if read_json(EXP/f'artifacts/fits/world_{w}_{a}_selected.json')!=winner:raise ValueError('discovery winner mismatch')
        print('FIT_LOCK_PASS; no held or truth read');return 0
    if a.fit and ((EXP/'artifacts/FIT_LOCK.json').exists() or (EXP/'artifacts/RUN_STOP.json').exists()):raise RuntimeError('refuse overwrite of completed run')
    if read_json(EXP/'prepared/CAPACITY.json')['status']!='SOURCE_CAPACITY_PASS':raise RuntimeError('SOURCE_CAPACITY_STOP')
    model,tables,metadata=prepare_resources(spec)
    if a.prepare_verification:
        print('VERIFICATION_RESOURCES_READY; no initializer, fit, held or truth read');return 0
    runtime=EXP/'runtime';binary=runtime/'decoder'
    subprocess.run(['g++','-std=c++17','-O3','-DNDEBUG',str(ENGINE_SOURCE),'-o',str(binary)],check=True)
    save(EXP/'artifacts/FIT_INPUTS.json',metadata);plans=[]
    for plan in fit_plan(spec):
        world=plan['world_id'];name=f'world_{world}_{plan["arm"]}_start{plan["start"]}'
        plan.update(binary=str(binary),model=str(model),projection=str(tables[world]),raw=str(runtime/(name+'.tsv')),output=str(EXP/'artifacts/fits'/(name+'.json')),input_hashes={**metadata[str(world)],'model_meta_sha256':sha(model/'model_meta.json'),'decoder_source_sha256':sha(ENGINE_SOURCE),'spec_sha256':sha(EXP/'src/SPEC.json')});plans.append(plan)
    statuses=[]
    with ProcessPoolExecutor(max_workers=min(24,max(1,a.workers))) as pool:
        futures=[pool.submit(fit_job,plan) for plan in plans]
        for n,future in enumerate(as_completed(futures),1):
            statuses.append(future.result());print(f'completed planned runs {n}/{len(plans)}',flush=True)
    if 'INITIALIZATION_STOP' in statuses:
        paths=[Path(plan['output']) for plan in plans]
        save(EXP/'artifacts/RUN_STOP.json',{'status':'INITIALIZATION_STOP','failed_initializations':statuses.count('INITIALIZATION_STOP'),'scheduled_runs':len(plans),'sha256':{p.relative_to(EXP).as_posix():sha(p) for p in paths},'held_or_truth_evaluation_allowed':False});print('INITIALIZATION_STOP; no key selections or truth evaluation');return 2
    lock=lock_fits(spec);print(json.dumps({'status':'FITS_LOCKED_UNEVALUATED','restarts':len(lock['restarts']),'selected':len(lock['selected'])}));return 0
if __name__=='__main__':raise SystemExit(main())
