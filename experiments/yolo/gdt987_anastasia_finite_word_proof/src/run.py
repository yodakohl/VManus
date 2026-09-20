#!/usr/bin/env python3
import collections
import concurrent.futures
import csv
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

from finite import solve

E=Path(__file__).resolve().parents[1]; R=E.parents[2]; A=E/'artifacts'
OLD=E.parent/'gdt986_anastasia_complete_condition_trees'
spec=importlib.util.spec_from_file_location('frozen986',OLD/'src/model.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


def read(p):return json.loads(p.read_text())
def put(name,value):(A/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')


def one(job):
    atoms=job['atoms'];words=job['words']
    result=solve(atoms,words)
    if result['status']=='SAT':
        ground=old.witness(atoms,words,result['code']);assert ground['valid']
        result['witness']=ground;result['projections']={}
        for atom,count in sorted(collections.Counter(atoms).items()):
            if count<2:continue
            query=solve(atoms,words,seconds=1,max_nodes=50000,forbidden=(atom,result['code'][atom]))
            if query['status']=='SAT':
                assert old.witness(atoms,words,query['code'])['valid']
                assert query['code'][atom]!=result['code'][atom]
            result['projections'][atom]=query
    return result


def isolated(job):
    try:
        r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker'],input=json.dumps(job),
                         text=True,capture_output=True,timeout=45)
        if r.returncode:return dict(status='ERROR_WORKER',exit_code=r.returncode)
        return json.loads(r.stdout)
    except subprocess.TimeoutExpired:return dict(status='UNKNOWN_WALL_LIMIT')
    except Exception as exc:return dict(status='ERROR_PROTOCOL',error_type=type(exc).__name__)


def main():
    if '--worker' in sys.argv:
        print(json.dumps(one(json.load(sys.stdin)),separators=(',',':')));return
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=read(OLD/'src/SOURCE.json');previous=read(OLD/'artifacts/CASES.json')
    started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    cases=[];jobs=[]
    for c in previous:
        keys=('edition','paragraph','page','leaf','writer','target_groups','independent_confirmation_capacity')
        row={k:c[k] for k in keys};row['gdt986_status']=c['status']
        assert not c['page'].startswith('f84')
        if c['status']=='UNKNOWN_SOURCE':
            row.update(status='UNKNOWN_SOURCE',ineligible_lines=c['ineligible_lines'])
        else:
            for k in ('words','loci','source_ids'):row[k]=c[k]
            jobs.append((len(cases),dict(atoms=source['streams'][c['writer']]['atoms'],words=c['words'])))
        cases.append(row)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        futures={pool.submit(isolated,j):i for i,j in jobs}
        for done,future in enumerate(concurrent.futures.as_completed(futures),1):
            index=futures[future];cases[index].update(future.result())
            if done%8==0 or done==len(jobs):
                print(json.dumps(dict(completed=done,of=len(jobs),latest_status=cases[index]['status'])),flush=True)
    put('CASES.json',cases)
    result=dict(status='COMPLETE_CONDITIONAL_WITNESS' if any(c['status']=='SAT' for c in cases)
                else 'FINITE_SEARCH_NO_WITNESS',case_status_counts=dict(collections.Counter(c['status'] for c in cases)),
                original_unknown_statuses=dict(collections.Counter(c['status'] for c in cases if c['gdt986_status']=='UNKNOWN_SOLVER')),
                panels={},confirmed_words=0,independent_confirmation_capacity=0,significance_claim=False)
    for ed in ('ZL3b','IT2a','RF1b'):
        result['panels'][ed]={order:dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==order))
                              for order in ('PREFIX','POSTFIX')}
    put('RESULT.json',result)
    put('EXECUTION_RECEIPT.json',dict(started_utc=utc,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         wall_seconds=time.monotonic()-started,workers=16,cases=len(cases),literal_jobs=len(jobs)))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n')
        w.writerow(['edition','paragraph','writer','source_atoms','source_types','groups','gdt986_status','status','nodes','full_code','independent_confirmation_capacity'])
        for c in cases:w.writerow([c['edition'],c['paragraph'],c['writer'],111,47,c['target_groups'],c['gdt986_status'],c['status'],c.get('nodes',''),c['status']=='SAT',0])
    lines=['# Complete conditional readings','','Every meaning is the unchanged986source hypothesis.']
    for c in cases:
        if c['status']!='SAT':continue
        lines += ['',f"## {c['edition']} {c['paragraph']} {c['writer']}",'',f"`{' '.join(c['words'])}`",'', '| Word | Source atoms |','|---|---|']
        for i,w in enumerate(c['words']):
            aa=[r['atom'] for r in c['witness']['alignment'] if r['word_index']==i]
            lines.append(f"|{w}|{' + '.join(aa)}|")
        lines += ['']+[f"- {r['id']}: {r['provisional_gloss']}" for r in source['clauses']]
    if not any(c['status']=='SAT' for c in cases):lines+=['','No complete code witness; all cases and unknowns are in CANDIDATES.tsv.']
    (A/'COMPLETE_READINGS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
