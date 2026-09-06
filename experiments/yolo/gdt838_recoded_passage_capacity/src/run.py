#!/usr/bin/env python3
"""Frozen guarded extraction plus exact whole-group pattern capacity; no decoder."""
import argparse,hashlib,importlib.util,itertools,json,re
from collections import Counter,defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
UP=E.parent/'gdt829_repeated_passage_reflow_capacity/src/run.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x,check=False):
    raw=(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
    if check:assert p.read_bytes()==raw,p.name
    else:p.write_bytes(raw)
def registered():
    lock=read(E/'src/PREREG_LOCK.json')
    for p,h in lock.items():assert sha(ROOT/p)==h,p

def extract():
    spec=read(E/'src/SPEC.json')
    m=importlib.util.spec_from_file_location('frozen_source829',UP);h=importlib.util.module_from_spec(m);m.loader.exec_module(h)
    rows,guard=h.query(spec)
    recs=h.records(rows);base,stats=h.scaffold(recs);windows=[];counts=Counter()
    for segment in base:
        for groups,gaps in h.streams(segment):
            for start in range(len(groups)-spec['width']+1):
                counts['all_windows']+=1
                if 'UNCERTAIN_SMALL_SPACE' in gaps[start:start+spec['width']-1]:
                    counts['uncertain_boundary_windows']+=1;continue
                g=groups[start:start+spec['width']];words=[r['ivtff_group_raw'] for r in g];freq=Counter(words)
                if len(freq)<spec['minimum_types'] or sum(n>=2 for n in freq.values())<spec['minimum_repeated_types']:continue
                seen={};signature=[seen.setdefault(w,len(seen)) for w in words]
                windows.append({'id':g[0]['source_group_id']+'--'+g[-1]['source_group_id'],
                    'page':g[0]['page'],'leaf':int(re.match(r'f(\d+)',g[0]['page'])[1]),
                    'group_ids':[r['source_group_id'] for r in g],'words':words,'signature':signature})
    return windows,{'guard':guard,'source_scaffold':stats,**dict(counts)}
def pairings(windows,spec):
    buckets=defaultdict(list)
    for w in windows:buckets[tuple(w['signature'])].append(w)
    pairs=[];cross=0
    for group in buckets.values():
        for a,b in itertools.combinations(group,2):
            if a['leaf']==b['leaf']:continue
            cross+=1;mapping=dict(zip(a['words'],b['words']))
            if sum(x!=y for x,y in mapping.items())<spec['minimum_nonidentity_types']:continue
            pairs.append({'a':a['id'],'b':b['id'],'mapping':mapping})
    return sorted(pairs,key=lambda p:(p['a'],p['b'])),cross

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();registered()
    spec=read(E/'src/SPEC.json');windows,meta=extract();pairs,cross=pairings(windows,spec)
    result={'status':'CANDIDATES_PRESENT_UNCONFIRMED' if pairs else 'CAPACITY_STOP',
        'eligible_windows':len(windows),'eligible_physical_folios':len({w['leaf'] for w in windows}),
        'cross_folio_same_pattern_pairs':cross,'qualifying_pairs':len(pairs),
        'qualifying_physical_folios':len({w['leaf'] for w in windows if any(w['id'] in (p['a'],p['b']) for p in pairs)}),
        'held_payload_accessed':False,'reading':'ZL3b','independent_confirmations':0,
        'scope':'Odd admitted physical folios only; capacity thresholds uncalibrated',**meta}
    for name,obj in [('WINDOWS.json',windows),('PAIRS.json',pairs),('RESULT.json',result)]:save(E/'artifacts'/name,obj,a.check)
    print(json.dumps({k:v for k,v in result.items() if k not in ('guard','source_scaffold')},sort_keys=True))
if __name__=='__main__':main()
