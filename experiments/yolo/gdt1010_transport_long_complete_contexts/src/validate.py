from common import *
from worker import bounded
import collections,concurrent.futures,csv

def task(row):
    s,g=inputs();panel=read(A/'PANEL.json');ps=[panel[i] for i in row['system']]
    other=bounded('independent',dict(paragraphs=ps))
    assert {row['status'].lower(),other['status']}!={'sat','unsat'}
    meaning_checks=[]
    for witness in row['witnesses']:
        code=witness['aliases'];assert set(code)=={w for p in ps for w in p['words']}
        assert len(witness['parses'])==2
        for pi,(p,parsed) in enumerate(zip(ps,witness['parses'])):
            cursor=0
            for clause in parsed:
                pattern=g['patterns'][clause['kind']]
                assert clause['start']==cursor and clause['end']==cursor+len(pattern);cursor=clause['end']
                assert clause['symbols']==[code[w] for w in p['words'][clause['start']:clause['end']]]
                assert all(x in g['types'][t[1:]] if t.startswith('@') else x==t for x,t in zip(clause['symbols'],pattern))
            assert cursor==len(p['words']) and parsed[0]['kind']=='INITIAL' and parsed[-1]['kind']=='CONCLUSION'
            for k in (g['patterns'] if pi==0 else ['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION']):assert sum(x['kind']==k for x in parsed)==1+int(pi==0 and k=='THEN')
        m=witness['meaning_check'];ind=bounded('meaning',dict(witness=dict(aliases=code,parses=witness['parses']),independent=True))
        if m['status']=='COMPLETE' and ind['status']=='COMPLETE':assert m['variants']==ind['variants'] and len(m['variants'])==32
        meaning_checks.append(dict(primary=m['status'],independent=ind['status'],checked_variants=32 if m['status']==ind['status']=='COMPLETE' else 0))
    return dict(id=row['id'],primary=row['status'],independent=other['status'],independent_receipt=other,witnesses=len(row['witnesses']),meaning_checks=meaning_checks)

def main():
    checklock();s,g=inputs();panel=read(A/'PANEL.json');jobs=read(A/'PREDICTIONS.json');rows=read(A/'ROWS.json');result=read(A/'RESULT.json')
    assert len(rows)==len(jobs)==282 and len(panel)==283
    required=[x['id'] for x in read(R/s['source_census']) if x['scope_status']=='ABOVE_SCOPE']
    assert required==[p['id'] for p in panel[1:]]
    assert panel[0]==read(R/s['source_previous_panel'])[0]
    for ed,paragraphs in read(R/s['source_paragraphs']).items():
        for p in paragraphs:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            pid=ed+'|'+p['id']
            if pid not in required:continue
            q=next(x for x in panel[1:] if x['id']==pid)
            assert q['words']==[w for l in p['lines'] for w in l['words']]
            assert q['source_ids']==[i for l in p['lines'] for i in l['source_ids']]
            assert q['groups']==len(q['words'])>37 and q['leaf']==p['leaf']!=83
            assert q['strict_anchor_eligible']==all(l['anchor_eligible'] for l in p['lines'])
    assert result['counts']==dict(collections.Counter(r['status'] for r in rows))
    for r,j in zip(rows,jobs):
        for k,v in j.items():assert r[k]==v
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==282
    for t,r in zip(table,rows):assert t['system']==r['id'] and t['status']==r['status'] and int(t['sampled_maps'])==len(r['witnesses'])
    checks=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        futures=[pool.submit(task,r) for r in rows]
        for f in concurrent.futures.as_completed(futures):
            checks.append(f.result())
            if len(checks)%32==0 or len(checks)==282:print(json.dumps(dict(checked=len(checks),total=282)),flush=True)
    checks.sort(key=lambda x:x['id'])
    out=dict(status='PASS',checks=checks,independent_unknowns=sum(c['independent'] not in ('sat','unsat') for c in checks),unverified_negatives=sum(c['primary']=='UNSAT' and c['independent']!='unsat' for c in checks),meaning_unknowns=sum(x['checked_variants']!=32 for c in checks for x in c['meaning_checks']),confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
