#!/usr/bin/env python3
"""Exhaustive word-equation enumeration and exact joint-key join."""
import argparse
from collections import Counter,defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
from source import load,tables,SCHEMES,TRAVERSALS
BASE=Path(__file__).resolve().parents[1]
class Budget(Exception):pass

def compatible(code,value):
    return all(not value.startswith(v) and not v.startswith(value) for v in code.values())
def extend_word(seq,word,key,deadline):
    def rec(i,pos,code):
        if time.monotonic()>deadline:raise Budget
        if i==len(seq):
            if pos==len(word):yield code
            return
        unit=seq[i]
        if unit in code:
            v=code[unit]
            if word.startswith(v,pos):yield from rec(i+1,pos+len(v),code)
            return
        rest_min=sum(len(code[u]) if u in code else 1 for u in seq[i+1:])
        for end in range(pos+1,len(word)-rest_min+1):
            value=word[pos:end]
            if not compatible(code,value):continue
            nxt=dict(code);nxt[unit]=value
            yield from rec(i+1,end,nxt)
    yield from rec(0,0,key)

def solve_words(equations,deadline,key=None):
    key={} if key is None else key
    if time.monotonic()>deadline:raise Budget
    if not equations:
        yield key;return
    def cost(eq):
        seq,word=eq
        unknown=sum(u not in key for u in seq)
        return (unknown, len(word), -sum(u in key for u in seq))
    chosen=min(range(len(equations)),key=lambda i:cost(equations[i]))
    seq,word=equations[chosen]
    remaining=equations[:chosen]+equations[chosen+1:]
    for expanded in extend_word(seq,word,key,deadline):
        yield from solve_words(remaining,deadline,expanded)

def common(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return n

def constraints(pattern):
    pairs=[]
    for i,j in itertools.combinations(range(18),2):
        a,b=pattern[i],pattern[j]
        pairs.append((i,j,common(a,b),common(a[::-1],b[::-1]),a==b[:len(a)],b==a[:len(b)]))
    return pairs

def reject(pattern,words,pairs):
    if len(set(words))!=18:return 'WHOLE_WORD_EQUALITY'
    for seq,w in zip(pattern,words):
        if len(w)<len(seq):return 'NONEMPTY_UNIT_LENGTH'
    for i,j,pre,suf,ap,bp in pairs:
        a,b=words[i],words[j]
        if b.startswith(a)!=ap or a.startswith(b)!=bp:return 'PREFIX_ORDER'
        if pre>common(a,b):return 'COMMON_PREFIX_LENGTH'
        if suf>common(a[::-1],b[::-1]):return 'COMMON_SUFFIX_LENGTH'
    return None

def serialize_code(key):
    return [{'unit':list(u),'value':v} for u,v in sorted(key.items())]
def deserialize_code(rows):return {tuple(x['unit']):x['value'] for x in rows}
def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--budget-seconds',type=float,default=900);a=ap.parse_args()
    started=time.monotonic();deadline=started+a.budget_seconds
    sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json'
    source=load(sp);target=json.loads(tp.read_text())
    cache={};components=[];cases=[];joint=[]
    def get(panel,pattern):
        fingerprint=digest(pattern);ck=(panel,fingerprint)
        if ck in cache:return cache[ck]
        windowlist=target['panels'][panel];pairs=constraints(pattern)
        counts=Counter();models=[];complete=True
        try:
            for window in windowlist:
                if time.monotonic()>deadline:raise Budget
                reason=reject(pattern,window['words'],pairs)
                if reason:counts[reason]+=1;continue
                counts['EXACT_ENUMERATION_WINDOWS']+=1
                found=False
                for key in solve_words(list(zip(pattern,window['words'])),deadline):
                    found=True
                    models.append({'window_id':window['id'],'code':serialize_code(key)})
                counts['EXACT_SAT_WINDOWS' if found else 'EXACT_UNSAT_WINDOWS']+=1
        except Budget:complete=False
        result={'id':len(components),'panel':panel,'pattern_sha256':fingerprint,
                'pattern':[[list(u) for u in seq] for seq in pattern],
                'eligible_windows':len(windowlist),'counts':dict(counts),
                'complete':complete,'models':models}
        components.append(result);cache[ck]=result
        return result
    byid={panel:{w['id']:w for w in ws} for panel,ws in target['panels'].items()}
    for panel in sorted(target['panels']):
        for vi,variant in enumerate(source['variants']):
            for scheme in SCHEMES:
                for ti,traversal in enumerate(TRAVERSALS):
                    case={'panel':panel,'variant':vi,'scheme':scheme,'traversal':ti}
                    if time.monotonic()>deadline:
                        case.update(status='UNKNOWN_BUDGET_NOT_RUN',joint_solutions=0);cases.append(case);continue
                    compiled=tables(source,variant,scheme,traversal)
                    ds=[get(panel,tuple(tuple(c['units']) for c in t['cells'])) for t in compiled]
                    case['components']=[x['id'] for x in ds]
                    if any(d['complete'] and not d['models'] for d in ds):
                        case.update(status='UNSAT',joint_solutions=0);cases.append(case);continue
                    before=len(joint);finished=all(d['complete'] for d in ds)
                    shared=set(u for seq in ds[0]['pattern'] for u in map(tuple,seq)) & set(u for seq in ds[1]['pattern'] for u in map(tuple,seq))
                    shared=sorted(shared)
                    index=defaultdict(list)
                    for model in ds[1]['models']:
                        key=deserialize_code(model['code']);index[tuple(key[u] for u in shared)].append((model,key))
                    try:
                        for left in ds[0]['models']:
                            ka=deserialize_code(left['code'])
                            wa=byid[panel][left['window_id']]
                            for right,kb in index.get(tuple(ka[u] for u in shared),[]):
                                if time.monotonic()>deadline:raise Budget
                                wb=byid[panel][right['window_id']]
                                if set(wa['source_group_ids']) & set(wb['source_group_ids']):continue
                                merged=dict(ka);valid=True
                                for u,v in kb.items():
                                    if u in merged:
                                        assert merged[u]==v
                                    elif compatible(merged,v):merged[u]=v
                                    else:valid=False;break
                                if not valid:continue
                                joint.append({'panel':panel,'variant':vi,'scheme':scheme,'traversal':ti,
                                              'present_window':left['window_id'],'imperfect_window':right['window_id'],
                                              'code':serialize_code(merged)})
                    except Budget:finished=False
                    case.update(status=('SAT_ENUMERATED' if len(joint)>before else 'UNSAT') if finished else 'UNKNOWN_BUDGET',joint_solutions=len(joint)-before)
                    cases.append(case)
        print(panel,Counter(c['status'] for c in cases if c['panel']==panel),flush=True)
    complete=all(c['status'] in ['UNSAT','SAT_ENUMERATED'] for c in cases)
    cell_values=defaultdict(set)
    for solution in joint:
        compiled=tables(source,source['variants'][solution['variant']],solution['scheme'],TRAVERSALS[solution['traversal']])
        for tab,field in zip(compiled,['present_window','imperfect_window']):
            window=byid[solution['panel']][solution[field]]
            for cell,word in zip(tab['cells'],window['words']):cell_values[cell['id']].add(word)
    projections={cell:{'values':sorted(values),'fixed_across_complete_model_union':complete and len(values)==1}
                 for cell,values in sorted(cell_values.items())}
    out={'schema':'GDT900_COMPLETE_MODEL_RESULT_V1','status':('SAT_COMPLETE_ENUMERATION' if joint else 'ALL_FOUR_PANELS_UNSAT') if complete else 'UNKNOWN_BUDGET',
         'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),
         'budget_seconds':a.budget_seconds,'elapsed_seconds':time.monotonic()-started,'complete':complete,
         'cases':cases,'component_count':len(components),'joint_solutions':joint,'cell_surface_projections':projections,
         'claim_ceiling':'Fixed two-edited-table/sharedcode/cell-window conjunction only; no meaning or general multilingual refutation.'}
    (BASE/'artifacts/COMPONENTS.json').write_text(json.dumps(components,indent=2)+'\n')
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'cases':len(cases),'components':len(components),'joint':len(joint),'seconds':out['elapsed_seconds']}))
if __name__=='__main__':main()
