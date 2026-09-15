#!/usr/bin/env python3
"""Finite complete-clause language; unchanged GDT900 word equations."""
import argparse, collections, concurrent.futures, csv, hashlib, importlib.util, itertools, json, re, sys, time, unicodedata
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
P900=ROOT/'experiments/yolo/gdt900_cumanicus_complete_trilingual_tables/src'
sys.path.insert(0,str(P900))
loader=importlib.util.spec_from_file_location('g900',P900/'run.py'); G=importlib.util.module_from_spec(loader);loader.loader.exec_module(G)
S=json.loads((E/'src/SPEC.json').read_text())
TARGET=ROOT/S['scope']['target']; ALPHABET=S['channel']['target_alphabet']
def save(name,data):
    (E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def table(name,rows):
    with (E/'artifacts'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['id'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def clusters(word):
    out=[]
    for c in unicodedata.normalize('NFD',word):
        if unicodedata.combining(c):out[-1]+=c
        else:out.append(c)
    return out
def generate():
    rows=[]
    for h,m,p,e in itertools.product(S['heads'],S['modifiers'],S['predicates'],S['extensions']):
        if e['id'] in ('SOUR','SWEET','UNRIPE') and m['id']!='NONE':continue
        words=h['words']+m['words']+p['words']+e['words']
        rows.append(dict(id=':'.join(x['id'] for x in (h,m,p,e)),derivation=dict(head=h['id'],modifier=m['id'],predicate=p['id'],extension=e['id']),words=words,word_count=len(words),grapheme_words=[clusters(w) for w in words],working_translation='The '+(m['working_translation']+' ' if m['working_translation'] else '')+h['working_translation']+' is '+p['working_translation']+'. '+e['working_translation'],status='ELIGIBLE' if 12<=len(words)<=24 else 'OUTSIDE_REGISTERED_WORD_COUNT'))
    assert len(rows)==81 and all(r['status']=='ELIGIBLE' for r in rows)
    return rows
def targets():
    data=json.loads(TARGET.read_text());out=[]
    for ed in ('IT2a','RF1b','ZL3b'):
        for r in sorted(data['panels'][ed],key=lambda r:r['paragraph_id']):
            assert not r['page'].startswith('f84') and r['page']!='f116v'
            if 12<=len(r['words'])<=24:out.append(dict(id=ed+':'+r['paragraph_id'],edition=ed,**r))
    assert collections.Counter(t['edition'] for t in out)=={'IT2a':41,'RF1b':5,'ZL3b':3}
    return out
def prediction(t,r):
    return dict(id=t['id']+'|'+r['id'],target_id=t['id'],edition=t['edition'],page=t['page'],physical_folio=t['physical_folio'],source_id=r['id'],required_word_count=r['word_count'],required_characters=sum(map(len,r['grapheme_words'])),required_distinct_units=len({u for g in r['grapheme_words'] for u in g}),required_complete_source='GENERATED_PARAGRAPHS.json#'+r['id'],required_relation='EXACT_WORD_EQUATIONS_GLOBAL_PREFIX_FREE_CODE_FULL32_COMPLETION',independent_confirmation_capacity=0)
def equality_pattern(xs):
    ids={};return [ids.setdefault(x,len(ids)) for x in xs]
def common(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return n
def necessary(t,r):
    a=r['grapheme_words'];b=t['words'];bad=[]
    if any(not re.fullmatch('[a-z]+',w) for w in b):return dict(status='UNKNOWN_SOURCE',contradictions=[dict(kind='NONLITERAL_TARGET')])
    if set(''.join(b))-set(ALPHABET):bad.append(dict(kind='TARGET_ALPHABET',characters=sorted(set(''.join(b))-set(ALPHABET))))
    if len(a)!=len(b):bad.append(dict(kind='WORD_COUNT',required=len(a),observed=len(b)))
    else:
        for i,(g,w) in enumerate(zip(a,b)):
            if len(g)>len(w):bad.append(dict(kind='NONEMPTY_WORD_LENGTH',position=i+1,required=len(g),observed=len(w)))
        if equality_pattern(r['words'])!=equality_pattern(b):bad.append(dict(kind='WHOLE_WORD_EQUALITY',required=equality_pattern(r['words']),observed=equality_pattern(b)))
        for i,j in itertools.combinations(range(len(a)),2):
            x,y=a[i],a[j];v,w=b[i],b[j]
            if (x==y[:len(x)])!=w.startswith(v) or (y==x[:len(y)])!=v.startswith(w):bad.append(dict(kind='WORD_PREFIX_ORDER',positions=[i+1,j+1]))
            if common(x,y)>common(v,w):bad.append(dict(kind='SHARED_PREFIX_LENGTH',positions=[i+1,j+1],required=common(x,y),observed=common(v,w)))
            if common(x[::-1],y[::-1])>common(v[::-1],w[::-1]):bad.append(dict(kind='SHARED_SUFFIX_LENGTH',positions=[i+1,j+1],required=common(x[::-1],y[::-1]),observed=common(v[::-1],w[::-1])))
    return dict(status='CONTRADICTED_NECESSARY' if bad else 'NEEDS_EXACT_SEARCH',contradictions=bad)
def complete_code(observed):
    missing=sorted(set(S['source_units'])-set(observed));code=dict(observed)
    if not missing:return code
    todo=collections.deque(['']);branch=None
    while todo and branch is None:
        prefix=todo.popleft()
        for c in ALPHABET:
            q=prefix+c
            if q in observed.values():continue
            if not any(v.startswith(q) for v in observed.values()):branch=q;break
            todo.append(q)
    if branch is None:return None
    width=0
    while len(ALPHABET)**width<len(missing):width+=1
    for i,u in enumerate(missing):
        digits=[];n=i
        for _ in range(width):digits.append(ALPHABET[n%len(ALPHABET)]);n//=len(ALPHABET)
        code[u]=branch+''.join(reversed(digits))
    return code
def check_code(code,r,t):
    if set(code)!=set(S['source_units']) or any(not v or set(v)-set(ALPHABET) for v in code.values()):return False
    values=sorted(code.values())
    return not any(b.startswith(a) for a,b in zip(values,values[1:])) and [''.join(code[u] for u in g) for g in r['grapheme_words']]==t['words']
def solve(job):
    t,r,global_deadline=job;started=time.monotonic();row=dict(status='UNSAT_EXACT',witnesses=[],complete_enumeration=True)
    if started>=global_deadline:return dict(status='UNKNOWN_GLOBAL_BUDGET',witnesses=[],complete_enumeration=False)
    deadline=min(started+2,global_deadline)
    try:
        for observed in G.solve_words(list(zip(r['grapheme_words'],t['words'])),deadline):
            code=complete_code(observed)
            if code is None:continue
            assert check_code(code,r,t)
            row['witnesses'].append(dict(observed_code=observed,completed_code=code,unobserved_units=sorted(set(code)-set(observed)),source_id=r['id'],target_id=t['id']))
            if len(row['witnesses'])>=16:
                row.update(status='SAT_INCOMPLETE_ENUMERATION',complete_enumeration=False,limit='16_OBSERVED_KEYS');break
        else:row['status']='SAT_COMPLETE_ENUMERATION' if row['witnesses'] else 'UNSAT_EXACT'
    except G.Budget:
        row.update(status='SAT_INCOMPLETE_ENUMERATION' if row['witnesses'] else 'UNKNOWN_COMPUTATION',complete_enumeration=False,limit='GLOBAL_BUDGET' if time.monotonic()>=global_deadline else 'LOCAL_2_SECONDS')
    row['elapsed_seconds']=time.monotonic()-started
    return row
def register():
    rs=generate();ts=targets();save('GENERATED_PARAGRAPHS.json',rs)
    table('PREDICTIONS.tsv',[prediction(t,r) for t in ts for r in rs])
    save('SCOPE.json',dict(targets=[{k:v for k,v in t.items() if k!='words'} for t in ts],parent_scope='GDT905 artifacts/SCOPE.json unchanged; all49 original selectedcases',source_products=len(rs),cases=len(rs)*len(ts),independent_confirmation_capacity=0))
    print(json.dumps(dict(registered_products=len(rs),registered_targets=len(ts),cases=len(rs)*len(ts))))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--register',action='store_true');a=ap.parse_args()
    if a.register:register();return
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    rs=generate();ts=targets();rows=[];jobs=[]
    for t in ts:
        for r in rs:
            row=dict(prediction(t,r),**necessary(t,r));rows.append(row)
            if row['status']=='NEEDS_EXACT_SEARCH':jobs.append((len(rows)-1,t,r))
    save('NECESSARY_CASES.json',rows)
    deadline=time.monotonic()+600
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        outputs=pool.map(solve,[(t,r,deadline) for _,t,r in jobs],chunksize=1)
        for (index,_,_),result in zip(jobs,outputs):rows[index].update(result)
    save('ALL_CASES.json',rows)
    witnesses=[];transfers=[]
    for row in rows:
        for w in row.get('witnesses',[]):
            wid='W'+str(len(witnesses)+1).zfill(6);w=dict(id=wid,case_id=row['id'],**w);witnesses.append(w)
            for t in ts:
                if t['edition']!=row['edition']:continue
                matches=[r['id'] for r in rs if check_code(w['completed_code'],r,t)]
                transfers.append(dict(witness_id=wid,target_id=t['id'],physical_folio=t['physical_folio'],same_physical_folio=t['physical_folio']==row['physical_folio'],source_ids=matches,status='EXACT_FIXED_COMPLETION_READING' if matches else 'NO_READING_UNDER_THIS_COMPLETION',independent_confirmation_capacity=0))
    save('WITNESSES.json',witnesses);save('FIXED_KEY_TRANSFER.json',transfers)
    table('CANDIDATE_TABLE.tsv',[dict(id=x['id'],target_id=x['target_id'],source_id=x['source_id'],status=x['status'],contradictions=json.dumps(x['contradictions'],ensure_ascii=False,separators=(',',':')),witness_count=len(x.get('witnesses',[])),complete_enumeration=x.get('complete_enumeration','NA'),independent_confirmation_capacity=0) for x in rows])
    groups=collections.defaultdict(list)
    for x in rows:groups[json.dumps(dict(status=x['status'],contradictions=x['contradictions']),sort_keys=True,separators=(',',':'))].append(x['id'])
    save('EQUIVALENT_OBSERVATIONS.json',[dict(observation=json.loads(k),cases=v) for k,v in sorted(groups.items())])
    transfer_witnesses=sorted({x['witness_id'] for x in transfers if not x['same_physical_folio'] and x['source_ids']})
    result=dict(status='FINITE_CONSTRUCTION_EVALUATED',cases=len(rows),source_products=len(rs),targets=len(ts),counts=dict(collections.Counter(x['status'] for x in rows)),exact_cases=len(jobs),observed_code_witnesses=len(witnesses),witnesses_transferring_to_other_physical_leaf=transfer_witnesses,observation_groups=len(groups),confirmed_words=0,independent_confirmation_capacity=0,claim_ceiling='Restricted generated source language and code only. No broader Arabic refutation, sourceidentity, significance or confirmed meaning. Unenumerated codes stay unknown.')
    save('RESULT.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
