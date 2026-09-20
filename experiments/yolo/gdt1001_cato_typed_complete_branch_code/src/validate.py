#!/usr/bin/env python3
"""Independent source traversal, complete census, word checks and reverse enumeration."""
import collections,concurrent.futures,csv,hashlib,json,re
from pathlib import Path
from reverse import ground,replay
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def traverse(node,mode):
    # Explicit event stack, independent of the runner's recursive flattener.
    stack=[('visit',node)];out=[]
    while stack:
        action,item=stack.pop()
        if action=='emit':out.append(item);continue
        if isinstance(item,str):out.append(item);continue
        op=item[0];children=item[1:]
        if mode=='PREFIX':
            for child in reversed(children):stack.append(('visit',child))
            stack.append(('emit',op))
        else:
            stack.append(('emit',op))
            for child in reversed(children):stack.append(('visit',child))
    return out

def jobrun(job):
    return replay(job['atoms'],job['words'],job['types'],seconds=job['seconds'],max_nodes=job['max_nodes'],max_solutions=2)

def main():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    spec=read(E/'src/SPEC.json');source=read(E/'src/SOURCE.json');cases=read(A/'CASES.json');target=read(R/spec['input']);result=read(A/'RESULT.json')
    streams={w:traverse(source['tree'],w) for w in spec['writers']}
    for stream in streams.values():assert set(stream)==set(source['types']) and len(stream)==result['source_atoms'][next(k for k,v in streams.items() if v==stream)]
    expected=[]
    for ed,ps in target.items():
        for p in ps:
            for writer in spec['writers']:expected.append((ed,p,writer))
    assert len(expected)==len(cases)==result['cases'];pending=[];codes=0
    for i,(c,(ed,p,writer)) in enumerate(zip(cases,expected)):
        assert c['index']==i and c['edition']==ed and c['paragraph']==p['id'] and c['writer']==writer and c['leaf']==p['leaf'] and c['page']==p['page']
        assert not c['page'].startswith('f84') and c['page']!='f116v'
        words=[w for l in p['lines'] for w in l['words']];assert c['words']==words and c['groups']==len(words) and c['characters']==sum(map(len,words))
        assert c['source_ids']==[x for l in p['lines'] for x in l['source_ids']]
        literal=all(l['anchor_eligible'] for l in p['lines']) and all(re.fullmatch('[a-z]+',w) for w in words)
        if not literal:assert c['status']=='UNKNOWN_SOURCE';continue
        assert c['status'] in ('SAT','UNSAT_FINITE','UNKNOWN_FINITE_LIMIT','UNKNOWN_WALL_LIMIT','ERROR_WORKER')
        if c['status']=='SAT':
            assert 1<=len(c['codes'])<=2
            assert len({json.dumps(x,sort_keys=True) for x in c['codes']})==len(c['codes'])
            for code in c['codes']:ground(streams[writer],words,source['types'],code);codes+=1
            if len(c['codes'])==2:assert c['code_ambiguity']=='MULTIPLE_CODES'
            elif c['exhaustive']:assert c['code_ambiguity']=='ONE_CODE_EXHAUSTIVE_WITHIN_FIXED_MODEL'
            else:assert c['code_ambiguity']=='ALTERNATIVE_CODES_UNRESOLVED'
        if c['status']=='UNSAT_FINITE' or (c['status']=='SAT' and c['exhaustive']):
            pending.append((i,dict(atoms=streams[writer],words=words,types=source['types'],seconds=spec['replay_seconds'],max_nodes=spec['replay_max_nodes'])))
    replay_rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=spec['workers']) as pool:
        fs={pool.submit(jobrun,j):i for i,j in pending}
        for done,f in enumerate(concurrent.futures.as_completed(fs),1):
            i=fs[f];r=f.result();c=cases[i]
            if c['status']=='UNSAT_FINITE':assert r['status']!='SAT_REPLAY',(i,r)
            else:
                assert r['status']!='UNSAT_REPLAY',(i,r)
                assert all(x in c['codes'] for x in r['codes'])
            replay_rows.append(dict(index=i,**r))
            if done%32==0 or done==len(fs):print(json.dumps(dict(replayed=done,total=len(fs))),flush=True)
    replay_rows.sort(key=lambda r:r['index']);put('INDEPENDENT_REPLAYS.json',replay_rows)
    counts=dict(collections.Counter(c['status'] for c in cases));assert counts==result['case_status_counts'] and codes==result['saved_codes']
    for ed in target:
        for writer in spec['writers']:assert result['panels'][ed][writer]==dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==writer))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(cases)
    for t,c in zip(table,cases):
        for k in ('index','edition','paragraph','leaf','writer','source_atoms','source_types','groups','characters','status'):assert t[k]==str(c[k])
    out=dict(status='PASS',cases_checked=len(cases),source_atoms=result['source_atoms'],saved_codes_ground_checked=codes,primary_exhaustions_or_unique_codes_replayed=len(replay_rows),replay_status_counts=dict(collections.Counter(r['status'] for r in replay_rows)),unresolved_replays=sum(r['status']=='UNKNOWN_REPLAY_LIMIT' for r in replay_rows),scope='Independent source traversal and literal code/census checking; reverse finite search, with unknown replays retained. Not native-source truth, historical identity or semantic confirmation.',confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
