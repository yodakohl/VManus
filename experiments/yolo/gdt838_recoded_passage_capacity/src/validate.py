#!/usr/bin/env python3
"""Independent direct-bijection census of saved windows; extraction is shared."""
import argparse,itertools,json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def mapping(a,b):
    forward={};reverse={}
    for x,y in zip(a,b):
        if (x in forward and forward[x]!=y) or (y in reverse and reverse[y]!=x):return None
        forward[x]=y;reverse[y]=x
    return forward

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:
        assert mapping(['a','b','a'],['x','y','x'])=={'a':'x','b':'y'}
        assert mapping(['a','b','a'],['x','y','z']) is None
        assert mapping(['a','b'],['x','x']) is None
        print(json.dumps({'status':'FIXTURE_PASS','checks':3}));return
    spec=json.loads((E/'src/SPEC.json').read_text());ws=json.loads((E/'artifacts/WINDOWS.json').read_text());expected=[];cross=0
    assert len({w['id'] for w in ws})==len(ws)
    for w in ws:
        f=Counter(w['words']);assert len(w['words'])==spec['width'] and len(f)>=spec['minimum_types'] and sum(n>1 for n in f.values())>=spec['minimum_repeated_types']
        assert w['leaf']%2==1 and not w['page'].startswith('f84')
    for u,v in itertools.combinations(ws,2):
        if u['leaf']==v['leaf']:continue
        m=mapping(u['words'],v['words'])
        if m is None:continue
        cross+=1
        if sum(x!=y for x,y in m.items())>=spec['minimum_nonidentity_types']:expected.append({'a':u['id'],'b':v['id'],'mapping':m})
    expected.sort(key=lambda p:(p['a'],p['b']))
    assert expected==json.loads((E/'artifacts/PAIRS.json').read_text())
    r=json.loads((E/'artifacts/RESULT.json').read_text())
    assert r['eligible_windows']==len(ws) and r['qualifying_pairs']==len(expected) and r['cross_folio_same_pattern_pairs']==cross
    assert r['status']==('CANDIDATES_PRESENT_UNCONFIRMED' if expected else 'CAPACITY_STOP')
    report={'status':'PAIR_CENSUS_VALIDATION_PASS','windows_checked':len(ws),'pairs_checked':len(expected),'source_extraction_independently_reimplemented':False,'held_prediction_or_semantic_validation':False}
    raw=json.dumps(report,indent=2,sort_keys=True)+'\n';target=E/'artifacts/VALIDATION.json'
    if a.check:assert target.read_text()==raw
    else:target.write_text(raw)
    print(raw)
if __name__=='__main__':main()
