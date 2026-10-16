#!/usr/bin/env python3
"""Blind optimizer driver. Never reads generator seeds, truth, or associations."""
import argparse
import array
import concurrent.futures
from datetime import datetime,timezone,timedelta
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import subprocess
import sys
import time

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts';R=E/'runtime';SRC=E/'src'
DEADLINE=datetime.fromisoformat('2026-10-16T04:28:00+00:00')
LANGUAGES=['latin','middle_high_german','middle_french','old_italian_tuscan','medieval_czech','old_hungarian']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def rel(p):return str(p.relative_to(ROOT))
def indexed(x,n):return x[str(n)] if isinstance(x,dict) else x[n]

def check_lock():
    p=SRC/'REGISTRATION_LOCK.json';lock=read(p)
    for path,h in lock['hashes'].items():assert sha(ROOT/path)==h,path
    for path in [SRC/'engine.cpp',SRC/'run.py',SRC/'validate.py',A/'MODELS.json',A/'SHAPE.json.gz',E/'PREREGISTRATION.md']:
        assert rel(path) in lock['hashes']
    return p,lock

def compile_engine():
    R.mkdir(exist_ok=True)
    executable=R/'engine'
    command=['g++','-O3','-std=c++17','-o',str(executable),str(SRC/'engine.cpp')]
    subprocess.run(command,check=True,capture_output=True,text=True)
    return executable

def write_doubles(f,values):
    assert sys.byteorder=='little','Binary interface requires explicit little-endian machine'
    array.array('d',values).tofile(f)

def model_binary(shape,logtables,path):
    L=shape['L'];assert L>=27 and len(shape['signs'])==22 and len(logtables)==6
    with path.open('wb') as f:
        f.write(b'CV1390\0\0');f.write(struct.pack('<IIII',L,22,6,20440))
        write_doubles(f,[0.0]+[indexed(shape['p_len'],n) for n in range(1,L+1)])
        write_doubles(f,[0.0]*22)
        for n in range(1,L+1):write_doubles(f,indexed(shape['initial'],n))
        for n in range(1,L+1):
            rows=indexed(shape['transition'],n);assert len(rows)==n-1
            f.write(struct.pack('<I',n-1))
            write_doubles(f,(p for matrix in rows for row in matrix for p in row))
        for table in logtables:
            assert len(table)==20440 and all(len(row)==27 for row in table)
            write_doubles(f,(p for row in table for p in row))

def cases_binary(cases,path):
    with path.open('wb') as f:
        f.write(b'CASE1390');f.write(struct.pack('<I',len(cases)))
        for case in cases:
            packets=case['units'];f.write(struct.pack('<I',len(packets)))
            for packet in packets:
                assert packet and all(type(i) is int and 0<=i<22 for i in packet)
                f.write(struct.pack('<I',len(packet)));f.write(bytes(packet))

def public_models():
    meta=read(A/'MODELS.json');shape_entry=meta['shape']
    assert sha(ROOT/shape_entry['path'])==shape_entry['sha256']
    shape=read(ROOT/shape_entry['path'])
    entries={e['language']:e for e in meta['models']};assert set(entries)==set(LANGUAGES)
    tables=[]
    for lang in LANGUAGES:
        entry=entries[lang];path=ROOT/entry['path'];assert sha(path)==entry['sha256']
        model=read(path);assert model['language']==lang
        tables.append(model['logp'])
    return meta,shape,tables

def prepare_benchmark():
    R.mkdir(exist_ok=True)
    meta,shape,tables=public_models()
    model_binary(shape,tables,R/'model.bin')
    # Independent of all anonymous control cases and private generation.
    rng=random.Random(1390888)
    packets=[[rng.randrange(22) for _ in range(rng.randrange(1,shape['L']+1))] for _ in range(120)]
    benchmark_cases=[{'id':'BENCHMARK_ONLY','units':packets}]
    cases_binary(benchmark_cases,R/'benchmark_cases.bin')
    save(R/'benchmark_cases.json',{'cases':benchmark_cases,'seed':1390888,'not_control_cases':True})
    return {'model_binary':rel(R/'model.bin'),'benchmark_binary':rel(R/'benchmark_cases.bin'),'benchmark_packet_seed':1390888,'benchmark_source_length':120,'source_model_order':LANGUAGES}

def engine_json(args,timeout=None):
    result=subprocess.run([str(R/'engine')]+list(map(str,args)),check=True,capture_output=True,text=True,timeout=timeout)
    return json.loads(result.stdout)

def benchmark(workers):
    lockpath,lock=check_lock();compile_engine();prep=prepare_benchmark()
    start=time.monotonic()
    output=engine_json(['--benchmark',R/'model.bin',R/'benchmark_cases.bin',0])
    command_wall=time.monotonic()-start
    startup=max(0.0,command_wall-output['wall_seconds'])
    evaluations=18*32*257
    estimated=2*output['cpu_seconds_per_key']*evaluations/workers+2*startup*math.ceil(18*32/workers)
    now=datetime.now(timezone.utc);remaining=(DEADLINE-now).total_seconds()-1200
    receipt={'status':'RUNTIME_GATE_PASS' if estimated<=remaining else 'RUNTIME_GATE_STOP','measured_utc':now.isoformat(),
             'benchmark':output,'preparation':prep,'command_wall_seconds':command_wall,'startup_seconds':startup,
             'workers':workers,'full_block_max_evaluations':evaluations,'twofold_cpu_extrapolation_seconds':estimated,
             'remaining_seconds_after_validation_publication_reserve':remaining,'reserve_seconds':1200,
             'deadline_utc':DEADLINE.isoformat(),'model_manifest_sha256':sha(A/'MODELS.json'),'registration_lock_sha256':sha(lockpath),
             'engine_source_sha256':sha(SRC/'engine.cpp'),'truth_access':False,'anonymous_cases_access':False,
             'scope':'Runtime only on fixed independent120-packet fixture; no decoder outcome used for gate.'}
    assert not (A/'BENCHMARK.json').exists()
    save(A/'BENCHMARK.json',receipt);print(json.dumps(receipt,sort_keys=True))

def one_start(case_index,restart_index,stop_utc):
    available=(stop_utc-datetime.now(timezone.utc)).total_seconds()
    if available<=0:return {'case_index':case_index,'start_index':restart_index,'status':'TIME_BUDGET_STOP'}
    try:
        result=engine_json(['--start',R/'model.bin',R/'cases.bin',case_index,restart_index],timeout=available)
        result['status']='COMPLETE';return result
    except subprocess.TimeoutExpired:
        return {'case_index':case_index,'start_index':restart_index,'status':'TIME_BUDGET_STOP'}
    except subprocess.CalledProcessError as exc:
        return {'case_index':case_index,'start_index':restart_index,'status':'ENGINE_FAILURE','error':exc.stderr[-2000:]}

def recover(workers):
    lockpath,lock=check_lock();bench=read(A/'BENCHMARK.json')
    assert bench['status']=='RUNTIME_GATE_PASS' and workers==bench['workers']
    assert bench['registration_lock_sha256']==sha(lockpath)
    assert sha(A/'MODELS.json')==bench['model_manifest_sha256']
    assert not (A/'RECOVERY.json').exists() and not (A/'RESTARTS.json').exists()
    compile_engine();prepare_benchmark()
    # First permissible reading of anonymous controls: explicit --recover only.
    casepath=A/'CASES.json';data=read(casepath);cases=data['cases']
    assert len(cases)==18 and len({c['id'] for c in cases})==18
    assert all(len(c['units']) in (77,120) for c in cases)
    cases_binary(cases,R/'cases.bin')
    cases_hash=sha(casepath)
    save(A/'RECOVERY_INPUT_LOCK.json',{'locked_utc':datetime.now(timezone.utc).isoformat(),'cases_sha256':cases_hash,'models_sha256':sha(A/'MODELS.json'),'registration_lock_sha256':sha(lockpath)})
    started=datetime.now(timezone.utc);startmono=time.monotonic()
    stop_utc=DEADLINE-timedelta(seconds=1200)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(one_start,ci,ri,stop_utc) for ci in range(18) for ri in range(32)]
        for future in concurrent.futures.as_completed(futures):results.append(future.result())
    assert sha(casepath)==cases_hash
    results.sort(key=lambda r:(r['case_index'],r['start_index']))
    save(A/'RESTARTS.json',{'cases_sha256':sha(casepath),'registration_lock_sha256':sha(lockpath),'results':results})
    complete=all(r['status']=='COMPLETE' for r in results)
    winners=[]
    if complete:
        for ci,case in enumerate(cases):
            runs=[r for r in results if r['case_index']==ci]
            assert len(runs)==32 and all(r['proposals']==256 for r in runs)
            best=min(runs,key=lambda r:(-r['winner']['score'],r['winner']['weights'],r['winner']['b']))
            winners.append({'id':case['id'],'case_index':ci,'message_length':len(case['units']),'winning_start_index':best['start_index'],**best['winner']})
    receipt={'status':'BLIND_RECOVERY_OUTPUT_COMPLETE' if complete else 'COMPUTATIONAL_STOP_NO_RECOVERY_GATE',
             'started_utc':started.isoformat(),'finished_utc':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-startmono,
             'registration_lock_sha256':sha(lockpath),'protocol_lock_sha256':sha(SRC/'PROTOCOL_LOCK.json'),
             'models_sha256':sha(A/'MODELS.json'),'cases_sha256':sha(casepath),'restarts_sha256':sha(A/'RESTARTS.json'),
             'root_search_seed':1390000,'seed_rule':'1390000+case_index*1000+start_index','rng':'C++ std::mt19937_64 and standard uniform distributions, fixed compiler/runtime',
             'search_state':'Accepted base key; each objective evaluates its complete18-scale/27-offset orbit. Canonical scale representative used only for numerically stable orbit evaluation.',
             'compiler':subprocess.run(['g++','--version'],check=True,capture_output=True,text=True).stdout.splitlines()[0],'compiler_flags':['-O3','-std=c++17'],'workers':workers,'completed_restarts':sum(r['status']=='COMPLETE' for r in results),'required_restarts':576,
             'cases':winners,'truth_access':False,'claim':'No control truth, source-component association, plaintext or generator seed read by optimizer.'}
    save(A/'RECOVERY.json',receipt)
    save(A/'RECOVERY_LOCK.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':[{ 'path':rel(A/name),'sha256':sha(A/name)} for name in ['RECOVERY.json','RESTARTS.json']]})
    print(json.dumps({'status':receipt['status'],'completed_restarts':receipt['completed_restarts'],'output_sha256':sha(A/'RECOVERY.json')},sort_keys=True))

def controls():
    compile_engine();L=27
    shape={'signs':list(range(22)),'L':L,'p_len':[0]+[1/L]*L,'initial':[[0]*22]+[[1/22]*22 for _ in range(L)],
           'transition':[[]]+[[[[1/22]*22 for _ in range(22)] for i in range(n-1)] for n in range(1,L+1)]}
    table=[[math.log(1/27)]*27 for _ in range(20440)]
    model_binary(shape,[table]*6,R/'fixture_model.bin')
    cases_binary([{'units':[[0],[1,0],[0,0,1]]}],R/'fixture_cases.bin')
    key=[1]+[0]*21
    result=engine_json(['--normalizer',R/'fixture_model.bin',*key])
    state=[0.0]*27;state[0]=1;expected=[0.0]*27
    for n in range(1,L+1):
        nxt=[0.0]*27
        for r,v in enumerate(state):nxt[r]+=v*21/22;nxt[(r+1)%27]+=v/22
        state=nxt
        for r,v in enumerate(state):expected[r]+=v/L
    error=max(abs(a-b) for a,b in zip(result['Z'],expected));assert error<1e-12
    scored=engine_json(['--score',R/'fixture_model.bin',R/'fixture_cases.bin',0,2,*key])
    assert scored['source_characters']==[3,2,3]
    assert abs(scored['source_mixture_logp']-3*math.log(1/27))<1e-12
    assert abs(scored['score']-(scored['source_mixture_logp']+scored['sum_log_shape']-scored['sum_log_state_normalizers']))<1e-12
    print(json.dumps({'status':'PASS_SOURCE_FREE_FIXTURE','max_uniform_normalizer_error':error,'mixture_and_state_check':True,'native_or_truth_access':False},sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--prepare-benchmark',action='store_true');p.add_argument('--benchmark',action='store_true');p.add_argument('--recover',action='store_true');p.add_argument('--workers',type=int,default=32);args=p.parse_args()
    assert 1<=args.workers<=32
    assert sum([args.controls,args.prepare_benchmark,args.benchmark,args.recover])==1
    if args.controls:controls()
    elif args.prepare_benchmark:compile_engine();print(json.dumps(prepare_benchmark(),sort_keys=True))
    elif args.benchmark:benchmark(args.workers)
    else:recover(args.workers)

if __name__=='__main__':main()
