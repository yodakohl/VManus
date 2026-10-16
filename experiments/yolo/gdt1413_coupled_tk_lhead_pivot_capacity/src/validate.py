#!/usr/bin/env python3
"""Independent literal six-group frame reconstruction; no semantic assignments."""
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parents[1]
A=E/'artifacts'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def units(word,alphabet):
    solutions=[]
    def visit(pos,acc):
        if len(solutions)>1:return
        if pos==len(word):solutions.append(acc);return
        for sign in alphabet:
            if word.startswith(sign,pos):visit(pos+len(sign),acc+[sign])
    visit(0,[])
    return solutions[0] if len(solutions)==1 else None

def classify(rows,signs):
    if len(rows)!=6 or any(x['kind']!='P' for x in rows):return None
    if len({(x['edition'],x['page'],x['locus']) for x in rows})!=1:return None
    ordinals=[int(x['source_group_index']) for x in rows]
    if ordinals!=list(range(ordinals[0],ordinals[0]+6)):return None
    if any(a['right_separator']!='DEFINITE_SPACE' or b['left_separator']!='DEFINITE_SPACE' for a,b in zip(rows,rows[1:])):return None
    raw=[x['ivtff_group_raw'] for x in rows]
    if raw[2]!=raw[3] or raw[4]!='l'+raw[1]:return None
    parsed=[units(w,signs) for w in raw]
    endpoint=False;changes=[]
    if parsed[0] is not None and parsed[5] is not None and len(parsed[0])==len(parsed[5]):
        changes=[i for i,(x,y) in enumerate(zip(parsed[0],parsed[5])) if x!=y]
        endpoint=len(changes)==1 and (parsed[0][changes[0]],parsed[5][changes[0]])==('t','k')
    return {'raw':raw,'units':parsed,'strict':all(x is not None for x in parsed) and endpoint,'endpoint':endpoint,'changes':changes}

def controls():
    signs=['a','t','k','r','b','l']
    def fixture(words):
        return [{'edition':'T','page':'f2r','locus':'f2r.1','kind':'P','source_group_index':str(i+1),'ivtff_group_raw':w,'left_separator':'DEFINITE_SPACE','right_separator':'DEFINITE_SPACE'} for i,w in enumerate(words)]
    base=['ta','r','b','b','lr','ka'];rows=fixture(base)
    assert classify(rows,signs)['strict']
    checks=1
    for index,word in [(0,'ka'),(5,'ta'),(5,'kk'),(3,'a'),(4,'r'),(1,'R')]:
        test=base.copy();test[index]=word
        result=classify(fixture(test),signs)
        assert result is None or not result['strict'];checks+=1
    opaque=fixture(['ta','r?','b','b','lr?','ka'])
    assert classify(opaque,signs)['strict'] is False;checks+=1
    for i in range(5):
        test=fixture(base);test[i]['right_separator']='UNCERTAIN'
        assert classify(test,signs) is None;checks+=1
        test=fixture(base);test[i+1]['left_separator']='UNCERTAIN'
        assert classify(test,signs) is None;checks+=1
    test=fixture(base);test[2]['source_group_index']='9'
    assert classify(test,signs) is None;checks+=1
    test=fixture(base);test[-1]['locus']='f2r.2'
    assert classify(test,signs) is None;checks+=1
    assert units('aa',['a','aa']) is None;checks+=1
    return {'status':'PASS','checks':checks}

def validate():
    lock=read(E/'LOCK.json')
    for path,h in lock['files'].items():
        assert not Path(path).is_absolute() and sha(ROOT/path)==h,path
    for path in [Path(__file__),E/'src/run.py',E/'src/SPEC.json']:
        assert path.relative_to(ROOT).as_posix() in lock['files']
    spec=read(E/'src/SPEC.json')
    guard=read(ROOT/spec['guard_path']);scope=read(ROOT/spec['scope_spec_path'])
    cache=ROOT/spec['cache_path'];assert sha(cache)==guard['sha256']
    assert len(scope['allowed'])==179
    lines=collections.defaultdict(list)
    with cache.open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream,delimiter='\t'):
            assert row['page'] in scope['allowed'] and not row['page'].startswith('f84')
            lines[row['edition'],row['page'],row['locus']].append(row)
    assert sum(map(len,lines.values()))==guard['stats']['selected']
    signs=read(ROOT/spec['signs_path'])['signs']
    frames=[]
    for (ed,page,locus),rows in sorted(lines.items()):
        if ed not in spec['editions']:continue
        rows.sort(key=lambda x:int(x['source_group_index']))
        assert len({int(x['source_group_index']) for x in rows})==len(rows)
        for start in range(max(0,len(rows)-5)):
            selected=rows[start:start+6]
            result=classify(selected,signs)
            if result is None:continue
            frames.append({'edition':ed,'page':page,'locus':locus,'start_group':int(selected[0]['source_group_index']),'raw':result['raw'],'parses':result['units'],'strict':result['strict']})
    frames.sort(key=lambda x:(x['edition'],x['page'],x['locus'],x['start_group']))
    assert frames==read(A/'FRAMES.json')
    counts={ed:{'descriptive':0,'strict':0,'breadth':0} for ed in spec['editions']}
    for frame in frames:
        count=counts[frame['edition']];count['descriptive']+=1
        if frame['strict']:
            count['strict']+=1
            leaf=re.match(r'f[0-9]+',frame['page'])[0]
            if leaf!=spec['known_leaf'] and frame['raw'][1]!=spec['known_head']:count['breadth']+=1
    passed=counts[spec['primary_edition']]['breadth']>0
    expected={'experiment_id':'GDT1413','counts':counts,'breadth_gate_pass':passed,'status':'FORMAL_BREADTH_PRESENT' if passed else 'FORMAL_BREADTH_MISSING'}
    assert expected==read(A/'RESULT.json')
    receipt={'experiment_id':'GDT1413','status':'PASS_INDEPENDENT_FRAME_RECONSTRUCTION','controls':controls(),'counts':counts,'lock_sha256':sha(E/'LOCK.json'),'pins':lock['files'],'outputs':{n:sha(A/n) for n in ['RESULT.json','FRAMES.json']},'scope':'Literal guarded-cache frame capacity only. Readers are alternative transcriptions; strict unit change is not same entity, lemma, converse, meaning or statistical significance.'}
    destination=A/'VALIDATION.json'
    if destination.exists():assert read(destination)==receipt
    else:destination.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'counts':counts},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--validate',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
