from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import json, hashlib, itertools
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def j(p):return json.loads(p.read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clear(seq):
    for x in seq:
        w=x['ivtff_group_raw']
        if not w or not all('a'<=c<='z' for c in w):return False
        if any(x[f] not in ('DEFINITE_SPACE','LINE_START','LINE_END') for f in ('left_separator','right_separator')):return False
    for i in range(1,len(seq)):
        l,r=seq[i-1:i+1]
        same=l['locus']==r['locus']
        if same and (int(r['source_group_index'])-int(l['source_group_index'])!=1 or l['right_separator']!='DEFINITE_SPACE' or r['left_separator']!='DEFINITE_SPACE'):return False
        if not same and (int(r['locus'].split('.')[-1])-int(l['locus'].split('.')[-1])!=1 or l['right_separator']!='LINE_END' or r['left_separator']!='LINE_START'):return False
    return True

def solve(text,ends):
    positions=[[] for _ in range(3)]
    for k in range(len(text)):
        for n,phrase in enumerate(ends):
            if tuple(text[k:k+len(phrase)])==tuple(phrase):positions[n].append(k)
    reasons=[]
    if len({w for phrase in ends for w in phrase})!=5:reasons.append('CUE_WORDS_NOT_DISTINCT')
    if [len(x) for x in positions]!=[1,1,1]:reasons.append('NO_UNIQUE_BASE_MATCH')
    else:
        a,b,c=(x[0] for x in positions)
        if a==0 or b==0 or c==0:reasons.append('NOT_STRICTLY_INTERNAL')
        if a+len(ends[0])>b or b+len(ends[1])>c:reasons.append('NOT_ORDERED_NONOVERLAPPING')
    return positions,reasons

def main():
    lock=j(E/'REGISTRATION_LOCK.json')
    for p,sha in lock['files'].items():assert h(R/p)==sha,p
    spec=j(E/'src/SPEC.json');allow=j(R/spec['allow_source'])['allowed_selectors']
    assert len(set(allow))==179 and all(not p.startswith('f84') and p!='f116v' for p in allow)
    source={}
    for name in spec['sources']:
        packet=j(R/name)
        for row in packet['lines']:
            md=row['metadata'];assert md['page'] in allow
            for values in row['groups']:
                v=dict(zip(packet['group_columns'],values));v.update(md)
                key=(md['edition'],v['source_group_id']);assert key not in source;source[key]=v
    paragraphs=j(R/spec['paragraph_source']);assert not paragraphs.get('RF1b')
    by={};flat={};original={}
    for ed in ('ZL3b','IT2a'):
        for p in paragraphs[ed]:
            assert p['page'] in allow
            rows=[]
            for line in p['lines']:
                part=[source[ed,sid] for sid in line['source_ids']]
                assert all(g['locus']==line['locus'] for g in part)
                assert [g['ivtff_group_raw'] for g in part]==line['words'];rows.extend(part)
            assert len(rows)==p['groups'];flat[ed,p['id']]=rows;original[ed,p['id']]=p
            by.setdefault((ed,p['page']),[]).append(p)
    result=j(E/'artifacts/RESULT.json');actual={(r['edition'],tuple(r['paragraph_ids'])):r for r in result['cases']}
    assert len(actual)==len(result['cases']);checked=0;counts={ed:Counter() for ed in ('ZL3b','IT2a')};expected_candidates=[]
    for (ed,page),ps in sorted(by.items()):
        ordered=sorted(ps,key=lambda p:p['lines'][0]['row'])
        for start in range(max(0,len(ordered)-3)):
            window=ordered[start:start+4];ids=[p['id'] for p in window];r=actual.pop((ed,tuple(ids)))
            want={'edition':ed,'page':page,'paragraph_ids':ids};g=[flat[ed,i] for i in ids]
            discontinuous=any(int(window[i]['lines'][0]['locus'].split('.')[-1])-int(window[i-1]['lines'][-1]['locus'].split('.')[-1])!=1 for i in range(1,4))
            if discontinuous:status='GAP_EXCLUDED'
            elif len(g[0])<2 or len(g[1])<=2 or len(g[2])<=1 or len(g[3])<=2:status='TOO_SHORT'
            else:
                tails=[g[1][-2:],g[2][-1:],g[3][-2:]]
                ends=[[x['ivtff_group_raw'] for x in t] for t in tails]
                want.update(cue_words=ends,cue_source_ids=[[x['source_group_id'] for x in t] for t in tails])
                if False in [clear(x) for x in [g[0]]+tails]:status='UNRESOLVED'
                else:
                    pos,reasons=solve([x['ivtff_group_raw'] for x in g[0]],ends);want.update(base_match_starts=pos,reasons=reasons)
                    status='CONTRADICTED' if reasons else 'FORMAL_CAPACITY_ONLY'
                    if not reasons:expected_candidates.append({'edition':ed,'page':page,'paragraphs':window,'base_match_starts':pos,'cue_words':ends})
            want['status']=status;assert r==want,(ed,ids);counts[ed][status]+=1;checked+=1
    assert not actual
    assert result['counts']=={e:dict(c) for e,c in counts.items()}
    assert result['paragraph_counts']=={e:len(paragraphs.get(e,[])) for e in ('ZL3b','IT2a','RF1b')}
    assert result['candidate_count']==len(expected_candidates)
    assert j(E/'artifacts/CANDIDATES.json')==expected_candidates
    assert result['decision']==('FORMAL_CAPACITY_ONLY' if expected_candidates else 'NO_SCORABLE_LOCAL_CUE_TEMPLATE')
    for fixture in j(E/'src/FIXTURES.json'):
        _,why=solve(fixture['base'],fixture['cues']);assert bool(why)==fixture['contradicted'],fixture['name']
    historical=j(R/spec['historical_source']);field='Full text as in Source (source spelling)'
    base=historical['records'][0]['fields'][field].casefold().split()
    cues=[r['fields'][field].split('|')[1].casefold().split() for r in historical['records'][1:]]
    pos,why=solve(base,cues);assert pos==[[14],[19],[23]] and not why
    receipt=j(E/'artifacts/RUN_RECEIPT.json');assert receipt['result_sha256']==h(E/'artifacts/RESULT.json')
    assert receipt['registration_lock_sha256']==h(E/'REGISTRATION_LOCK.json')
    assert datetime.fromisoformat(lock['locked_utc'])<datetime.fromisoformat(receipt['finished_utc'])
    validation={'status':'PASS','finished_utc':datetime.now(timezone.utc).isoformat(),'complete_windows_checked':checked,'historical_casefold_positions_zero_based':pos,'synthetic_fixtures':len(j(E/'src/FIXTURES.json')),'counts':result['counts'],'result_sha256':h(E/'artifacts/RESULT.json'),'claim_ceiling':'Independent implementation by same author; source accounting and equations only.'}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation))
if __name__=='__main__':main()
